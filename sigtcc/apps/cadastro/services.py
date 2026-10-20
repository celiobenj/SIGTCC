"""Regras de negócio de acesso e conta do app cadastro (research A20).

Parte comum: log de eventos de acesso, e-mail sem diferenciar maiúsculas, envio de e-mail e o
retorno para itens indisponíveis. As regras de login, links, senha, reset, perfil e notificações
ficam nas seções seguintes deste módulo.

[US-10][US-11][US-12][US-37][US-38][FR-026][FR-029]
"""

import enum
import logging
import math
import re
from dataclasses import dataclass
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.base_user import BaseUserManager
from django.core.cache import caches
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils import timezone

from sigtcc.apps.cadastro.choices import StatusConta
from sigtcc.apps.cadastro.mensagens import ITEM_INDISPONIVEL
from sigtcc.apps.cadastro.models import Alunos, Usuarios
from sigtcc.apps.cadastro.permissoes import validade_vencida
from sigtcc.apps.cadastro.validators import tamanho_de_senha_valido

registro_acesso = logging.getLogger("sigtcc.acesso")


# =============================================================================================
# Log de eventos de acesso (FR-029; spec Q21; research A13)
# =============================================================================================


class EventoAcesso(enum.Enum):
    """Conjunto fechado de eventos do log de acesso.

    Os 6 tipos do FR-029 (SC-009) e dois eventos técnicos, fora da contagem do SC-009:
    EMAIL_DUPLICADO e FALHA_ENVIO_EMAIL. [FR-029][US-11][RBN-CAD-06.6][US-12][US-38]
    """

    LOGIN_SENHA_INCORRETA = "LOGIN_SENHA_INCORRETA"
    BLOQUEIO = "BLOQUEIO"
    SENHA_ALTERADA = "SENHA_ALTERADA"
    SENHA_REDEFINIDA = "SENHA_REDEFINIDA"
    RESET_PRIMEIRO_ACESSO = "RESET_PRIMEIRO_ACESSO"
    TROCA_EMAIL_PEDIDA = "TROCA_EMAIL_PEDIDA"
    TROCA_EMAIL_CONFIRMADA = "TROCA_EMAIL_CONFIRMADA"
    EMAIL_DUPLICADO = "EMAIL_DUPLICADO"
    FALHA_ENVIO_EMAIL = "FALHA_ENVIO_EMAIL"


def registrar_evento(evento, conta, autor=None, detalhe=""):
    """Grava uma linha no log de acesso: evento | conta=<id> | autor=<id ou própria> | detalhe.

    conta e autor são Usuarios ou None. detalhe é montado pelo sistema, nunca com algo digitado
    pelo usuário; nunca entram senha, token, link ou e-mail completo (A13). A data e a hora vêm
    do formatador do log. [FR-029][SC-008][SC-009]
    """
    id_conta = conta.pk if conta is not None else "-"
    if autor is not None:
        id_autor = autor.pk
    else:
        id_autor = "própria" if conta is not None else "-"
    registro_acesso.info(
        "%s | conta=%s | autor=%s | %s", evento.value, id_conta, id_autor, detalhe or "-"
    )


# =============================================================================================
# E-mail sem diferenciar maiúsculas (spec Q13; research A18; contrato §4)
# =============================================================================================


def normalizar_email(email):
    """Remove espaços e põe o domínio em minúsculas; None se vazio. [FR-026][Q13]"""
    if email is None:
        return None
    email = email.strip()
    if not email:
        return None
    return BaseUserManager.normalize_email(email)


def email_em_uso(email, exceto=None):
    """Diz se outra conta já usa o e-mail, sem diferenciar maiúsculas. [FR-026][Q13][I3]"""
    contas = Usuarios.objects.filter(usu_email__iexact=email)
    if exceto is not None:
        contas = contas.exclude(pk=exceto.pk)
    return contas.exists()


def dominio_do_email(email):
    """Só o domínio, para o log não guardar o e-mail completo (A13). [FR-029]"""
    return email.rsplit("@", 1)[-1] if email and "@" in email else "-"


# =============================================================================================
# Envio de e-mail (research A5)
# =============================================================================================


def enviar_email(destino, assunto, template, contexto, conta=None):
    """Envia um e-mail de texto a partir de um template de cadastro/emails/.

    Em falha, registra FALHA_ENVIO_EMAIL só com o tipo da exceção (nunca a mensagem, que pode
    trazer o endereço) e levanta a exceção de novo para quem chamou decidir. [FR-026][Q13][A5]
    """
    corpo = render_to_string(template, contexto)
    try:
        send_mail(assunto, corpo, None, [destino], fail_silently=False)
    except Exception as erro:
        registrar_evento(EventoAcesso.FALHA_ENVIO_EMAIL, conta, detalhe=type(erro).__name__)
        raise


# =============================================================================================
# Notificação de item indisponível (FR-023; spec Q10; contrato §5)
# =============================================================================================


def item_indisponivel(request):
    """Mostra "Este item não está mais disponível" e volta à central de notificações.

    Para a tela de destino de uma notificação cujo item foi cancelado (Defesa, índice Q-12).
    [US-38][RBN-CAD-13.2][FR-023][Q10]
    """
    messages.warning(request, ITEM_INDISPONIVEL)
    return redirect("cadastro:notificacoes")


# =============================================================================================
# Login e bloqueio por tentativas (US-11; FR-007 a FR-010; research A1 e A2)
# =============================================================================================

TENTATIVAS_PARA_BLOQUEIO = 3
DURACAO_BLOQUEIO = timedelta(minutes=15)
# Tempos de vida das chaves no cache: só para limpeza; a regra compara instantes (A2).
_VIDA_CONTADOR = 24 * 60 * 60
_VIDA_BLOQUEIO = 16 * 60
_MATRICULA = re.compile(r"\d{10}")


class EstadoLogin(enum.Enum):
    """Resultados do login, na ordem de avaliação do FR-008 (spec Q12). [US-11][RBN-CAD-06.4]"""

    VAZIO = "vazio"
    NAO_ENCONTRADA = "nao_encontrada"
    AGUARDANDO = "aguardando"
    BLOQUEADA = "bloqueada"
    SENHA_INCORRETA = "senha_incorreta"
    INATIVA = "inativa"
    EXPIRADA = "expirada"
    OK = "ok"


@dataclass
class ResultadoLogin:
    """Estado do login, com o usuário (quando encontrado) e os minutos restantes do bloqueio."""

    estado: EstadoLogin
    usuario: object = None
    minutos_restantes: int = 0


def _cache_acesso():
    """Cache próprio do bloqueio (alias "acesso", research A2)."""
    return caches["acesso"]


def _chave_falhas(usuario):
    return f"acesso:falhas:{usuario.pk}"


def _chave_bloqueio(usuario):
    return f"acesso:bloqueio:{usuario.pk}"


def fim_do_bloqueio(usuario):
    """Instante do fim do bloqueio vigente da conta, ou None. [US-11][RBN-CAD-06.6]"""
    valor = _cache_acesso().get(_chave_bloqueio(usuario))
    if not valor:
        return None
    fim = datetime.fromisoformat(valor)
    return fim if fim > timezone.now() else None


def minutos_restantes(fim):
    """ "N" da M-01: minutos restantes arredondados para cima, no mínimo 1 (spec Q16)."""
    segundos = (fim - timezone.now()).total_seconds()
    return max(1, math.ceil(segundos / 60))


def _registrar_falha(usuario):
    """Conta uma senha incorreta; na terceira seguida, grava o bloqueio de 15 minutos.

    Devolve o instante do fim do bloqueio quando ele é gravado, ou None. O bloqueio é gravado com
    cache.add, para não sobrescrever um bloqueio gravado por requisição paralela (A2).
    [US-11][RBN-CAD-06.6][FR-009]
    """
    cache = _cache_acesso()
    falhas = (cache.get(_chave_falhas(usuario)) or 0) + 1
    if falhas < TENTATIVAS_PARA_BLOQUEIO:
        cache.set(_chave_falhas(usuario), falhas, _VIDA_CONTADOR)
        return None
    fim = timezone.now() + DURACAO_BLOQUEIO
    if not cache.add(_chave_bloqueio(usuario), fim.isoformat(), _VIDA_BLOQUEIO):
        # A chave pode ser de um bloqueio que já terminou (o tempo de vida passa dos 15 min).
        vigente = fim_do_bloqueio(usuario)
        if vigente is None:
            cache.set(_chave_bloqueio(usuario), fim.isoformat(), _VIDA_BLOQUEIO)
        else:
            fim = vigente
    cache.delete(_chave_falhas(usuario))
    registrar_evento(EventoAcesso.BLOQUEIO, usuario, detalhe="15 minutos")
    return fim


def _buscar_conta(credencial):
    """Conta pela credencial: 10 dígitos → matrícula; senão, e-mail sem diferenciar maiúsculas.

    Mais de uma conta com o mesmo e-mail registra EMAIL_DUPLICADO e não devolve nenhuma (I3).
    [US-11][RBN-CAD-06.4][Q13]
    """
    if _MATRICULA.fullmatch(credencial):
        aluno = Alunos.objects.select_related("alu").filter(alu_matricula=credencial).first()
        return aluno.alu if aluno else None
    contas = list(Usuarios.objects.filter(usu_email__iexact=credencial)[:2])
    if len(contas) > 1:
        total = Usuarios.objects.filter(usu_email__iexact=credencial).count()
        registrar_evento(EventoAcesso.EMAIL_DUPLICADO, None, detalhe=f"contas={total}")
        return None
    return contas[0] if contas else None


def autenticar(credencial, senha):
    """Avalia o login na ordem do FR-008 (spec Q12) e devolve um ResultadoLogin.

    1 vazio; 2 conta não encontrada (com hash fictício, I1); 3 'Aguardando Ativação' sem conferir
    senha; 4 bloqueio vigente; 5 senha fora de 8 a 64 ou incorreta (conta tentativa; na terceira,
    bloqueio); 6 com a senha correta: confere o bloqueio de novo (I2), zera o contador e devolve
    'Inativa', 'Expirada' (status ou validade vencida, Q4) ou OK.
    [US-11][RBN-CAD-06.4][RBN-CAD-06.6][RBN-CAD-03.3][FR-007][FR-008][FR-009][Q4][Q12][Q17]
    """
    credencial = (credencial or "").strip()
    senha = senha or ""
    if not credencial or not senha:
        return ResultadoLogin(EstadoLogin.VAZIO)
    usuario = _buscar_conta(credencial)
    if usuario is None:
        # Mesmo custo de uma senha conferida: o tempo não revela se a conta existe (I1).
        Usuarios().set_password(senha)
        return ResultadoLogin(EstadoLogin.NAO_ENCONTRADA)
    if usuario.usu_status == StatusConta.AGUARDANDO_ATIVACAO:
        return ResultadoLogin(EstadoLogin.AGUARDANDO, usuario)
    fim = fim_do_bloqueio(usuario)
    if fim is not None:
        return ResultadoLogin(EstadoLogin.BLOQUEADA, usuario, minutos_restantes(fim))
    if not (tamanho_de_senha_valido(senha) and usuario.check_password(senha)):
        registrar_evento(EventoAcesso.LOGIN_SENHA_INCORRETA, usuario)
        fim = _registrar_falha(usuario)
        if fim is not None:
            return ResultadoLogin(EstadoLogin.BLOQUEADA, usuario, minutos_restantes(fim))
        return ResultadoLogin(EstadoLogin.SENHA_INCORRETA, usuario)
    fim = fim_do_bloqueio(usuario)
    if fim is not None:
        return ResultadoLogin(EstadoLogin.BLOQUEADA, usuario, minutos_restantes(fim))
    _cache_acesso().delete(_chave_falhas(usuario))
    if usuario.usu_status == StatusConta.INATIVA:
        return ResultadoLogin(EstadoLogin.INATIVA, usuario)
    if usuario.usu_status == StatusConta.EXPIRADA or validade_vencida(usuario):
        return ResultadoLogin(EstadoLogin.EXPIRADA, usuario)
    return ResultadoLogin(EstadoLogin.OK, usuario)
