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

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.base_user import BaseUserManager
from django.core import signing
from django.core.cache import caches
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro.choices import StatusConta
from sigtcc.apps.cadastro.mensagens import (
    CONTA_JA_ATIVA,
    EMAIL_DE_OUTRA_CONTA_ALUNO,
    ITEM_INDISPONIVEL,
    LINK_ATIVACAO_ENVIADO,
    M15_CONTA_INATIVA,
    M16_ACESSO_EXPIRADO,
    M17_FALHA_ENVIO,
)
from sigtcc.apps.cadastro.models import Alunos, Usuarios
from sigtcc.apps.cadastro.permissoes import tipo_conta, validade_vencida
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


# =============================================================================================
# Links de ativação e primeiro acesso (US-10, US-37; FR-002, FR-006, FR-016, FR-026; A3, A5, A17)
# =============================================================================================

VALIDADE_LINK = timedelta(hours=24)
SALT_ATIVACAO = "sigtcc.ativacao"
SESSAO_TOKEN_ATIVACAO = "token_ativacao"


class FalhaEnvioEmail(Exception):
    """O e-mail não pôde ser enviado; a transação em volta é desfeita (A5). [Q13][M-17]"""


class EstadoLink(enum.Enum):
    """Estados de um link, avaliados na ordem do data-model (FR-016; Q5, Q23, Q26).

    [US-10][US-37][US-12][RBN-CAD-06.1][RBN-CAD-06.9][FR-016]
    """

    ADULTERADO = "adulterado"
    ATIVA = "ativa"
    INATIVA = "inativa"
    EXPIRADA = "expirada"
    SEM_EMAIL = "sem_email"
    SUBSTITUIDO = "substituido"
    VENCIDO = "vencido"
    VALIDO = "valido"


@dataclass
class ResultadoLink:
    """Estado do link e a conta a que ele se refere (quando a assinatura é válida)."""

    estado: EstadoLink
    usuario: object = None


@dataclass
class ResultadoPedido:
    """Resultado de um pedido que envia e-mail: enviado, ou a mensagem de recusa."""

    enviado: bool
    mensagem: str = ""


def _conta(usu_id, travar=False):
    """Conta pelo id, com as especializações; travada (select_for_update) se pedido (A17)."""
    contas = Usuarios.objects.select_related("alunos", "docentes", "membrosexternos", "secretarios")
    if travar:
        # Só a linha de Usuarios: o PostgreSQL não trava o lado opcional de um outer join.
        contas = contas.select_for_update(of=("self",))
    return contas.filter(pk=usu_id).first()


def _gravar_link_gerado_em(usuario):
    """Grava usu_link_gerado_em = agora (invalida os links anteriores) e relê do banco (A3)."""
    Usuarios.objects.filter(pk=usuario.pk).update(usu_link_gerado_em=timezone.now())
    usuario.refresh_from_db(fields=["usu_link_gerado_em"])
    return usuario.usu_link_gerado_em


def _url_absoluta(nome_rota, token):
    """Link absoluto com o SITE_URL do .env (A5)."""
    return settings.SITE_URL + reverse(nome_rota, args=[token])


def _ler_token(token, salt):
    """Abre um token assinado; devolve (usu_id, dados) ou None se adulterado (Q23)."""
    try:
        dados = signing.loads(token, salt=salt)
        return int(dados["u"]), dados
    except (signing.BadSignature, KeyError, TypeError, ValueError):
        return None


def gerar_link_ativacao(usuario):
    """Gera o link de ativação (24 h) e invalida os anteriores. Devolve a URL absoluta.

    Pode ser chamada por outras features e por testes (contrato §4; história 6, cenário 5).
    [US-10][US-37][RBN-CAD-06.1][RBN-CAD-06.2][RBN-CAD-06.9][FR-006][FR-026]
    """
    gerado_em = _gravar_link_gerado_em(usuario)
    token = signing.dumps({"u": usuario.pk, "g": gerado_em.isoformat()}, salt=SALT_ATIVACAO)
    return _url_absoluta("cadastro:ativar", token)


def _estado_da_conta(usuario):
    """'Inativa' ou 'Expirada' (status ou validade vencida, Q4), ou None. [Q6][Q26]"""
    if usuario.usu_status == StatusConta.INATIVA:
        return EstadoLink.INATIVA
    if usuario.usu_status == StatusConta.EXPIRADA or validade_vencida(usuario):
        return EstadoLink.EXPIRADA
    return None


def validar_link_ativacao(token, travar=False):
    """Estado do link de ativação, na ordem do data-model (FR-016; Q5, Q23, Q26; B1).

    ADULTERADO → ATIVA → INATIVA → EXPIRADA → SEM_EMAIL → SUBSTITUIDO → VENCIDO → VALIDO.
    Com travar=True, a conta vem travada (usar dentro de transaction.atomic, A17).
    [US-10][US-37][RBN-CAD-06.1][RBN-CAD-06.9][FR-016][FR-026]
    """
    lido = _ler_token(token, SALT_ATIVACAO)
    if lido is None:
        return ResultadoLink(EstadoLink.ADULTERADO)
    usu_id, dados = lido
    try:
        gerado_em = datetime.fromisoformat(dados["g"])
    except (KeyError, TypeError, ValueError):
        return ResultadoLink(EstadoLink.ADULTERADO)
    usuario = _conta(usu_id, travar)
    if usuario is None:
        return ResultadoLink(EstadoLink.ADULTERADO)
    if usuario.usu_status == StatusConta.ATIVA:
        return ResultadoLink(EstadoLink.ATIVA, usuario)
    estado = _estado_da_conta(usuario)
    if estado is not None:
        return ResultadoLink(estado, usuario)
    if not usuario.usu_email:
        return ResultadoLink(EstadoLink.SEM_EMAIL, usuario)
    if usuario.usu_link_gerado_em != gerado_em:
        return ResultadoLink(EstadoLink.SUBSTITUIDO, usuario)
    if timezone.now() - gerado_em > VALIDADE_LINK:
        return ResultadoLink(EstadoLink.VENCIDO, usuario)
    return ResultadoLink(EstadoLink.VALIDO, usuario)


def _gerar_e_enviar_ativacao(usuario):
    """Gera o link e envia o e-mail de ativação; em falha levanta FalhaEnvioEmail.

    Deve rodar dentro de transaction.atomic(), para a falha desfazer tudo (A5, I5).
    """
    link = gerar_link_ativacao(usuario)
    try:
        enviar_email(
            usuario.usu_email,
            "SIGTCC: ative a sua conta",
            "cadastro/emails/ativacao.txt",
            {"nome": usuario.usu_nome, "link": link},
            conta=usuario,
        )
    except Exception as erro:
        raise FalhaEnvioEmail from erro


def enviar_link_ativacao(usuario):
    """Gera, grava e envia o link de ativação numa transação; False se o envio falhar.

    Com False, nada fica gravado e quem chama mostra a M-17 (contrato §4; Q13).
    [US-10][US-37][RBN-CAD-06.1][RBN-CAD-06.9][FR-026][Q13]
    """
    try:
        with transaction.atomic():
            _gerar_e_enviar_ativacao(usuario)
    except FalhaEnvioEmail:
        return False
    return True


def recusa_por_status(usuario):
    """Mensagem de recusa do primeiro acesso pelo status da conta, ou "" se pode pedir.

    'Ativa' → "Esta conta já está ativa"; 'Inativa' → M-15; 'Expirada' ou validade vencida →
    M-16 (spec Q6). [US-10][RBN-CAD-06.1][RBN-CAD-06.2][FR-003][Q6]
    """
    if usuario.usu_status == StatusConta.ATIVA:
        return CONTA_JA_ATIVA
    estado = _estado_da_conta(usuario)
    if estado == EstadoLink.INATIVA:
        return M15_CONTA_INATIVA
    if estado == EstadoLink.EXPIRADA:
        return M16_ACESSO_EXPIRADO
    return ""


def conta_do_aluno_para_primeiro_acesso(matricula):
    """Conta do Aluno pela matrícula, com pelo menos uma turma; None se não houver.

    [US-10][RBN-CAD-06.1][FR-003][US-10 E1]
    """
    aluno = (
        Alunos.objects.select_related("alu")
        .filter(alu_matricula=matricula, alunosturmas__isnull=False)
        .first()
    )
    return aluno.alu if aluno else None


def conta_por_email_para_primeiro_acesso(email):
    """Conta de Docente, Secretaria ou Membro Externo pelo e-mail; None se não houver.

    E-mail de Aluno ou de conta sem tipo não é aceito aqui (spec Q8; research A9).
    [US-10][RBN-CAD-06.2][FR-001][FR-003][Q8][Q13]
    """
    contas = list(
        Usuarios.objects.select_related(
            "alunos", "docentes", "membrosexternos", "secretarios"
        ).filter(usu_email__iexact=email)[:2]
    )
    if len(contas) != 1:
        if len(contas) > 1:
            registrar_evento(EventoAcesso.EMAIL_DUPLICADO, None, detalhe="contas=2+")
        return None
    conta = contas[0]
    return conta if tipo_conta(conta) in ("docente", "secretaria", "membro_externo") else None


def pedir_primeiro_acesso(usuario, email_informado=None):
    """Envia o link de ativação de uma conta 'Aguardando Ativação' (FR-002).

    Com a conta travada, confere o status de novo; no Aluno sem e-mail, registra o e-mail
    informado (se livre); no Aluno com e-mail, ignora o informado e usa o registrado (Q2, Q15).
    Falha no envio desfaz tudo e devolve a M-17 (I5).
    [US-10][RBN-CAD-06.1][RBN-CAD-06.2][FR-002][FR-003][Q2][Q13][Q15][I5]
    """
    try:
        with transaction.atomic():
            conta = _conta(usuario.pk, travar=True)
            recusa = recusa_por_status(conta)
            if recusa:
                return ResultadoPedido(False, recusa)
            if tipo_conta(conta) == "aluno" and not conta.usu_email:
                email = normalizar_email(email_informado)
                if email_em_uso(email, exceto=conta):
                    return ResultadoPedido(False, EMAIL_DE_OUTRA_CONTA_ALUNO)
                conta.usu_email = email
                conta.save(update_fields=["usu_email"])
            _gerar_e_enviar_ativacao(conta)
    except FalhaEnvioEmail:
        return ResultadoPedido(False, M17_FALHA_ENVIO)
    except IntegrityError:
        return ResultadoPedido(False, EMAIL_DE_OUTRA_CONTA_ALUNO)
    return ResultadoPedido(True, LINK_ATIVACAO_ENVIADO)


def ativar_conta(token, senha):
    """Ativa a conta pelo link: revalida com a conta travada e grava a senha (FR-005; A17).

    Só no estado VALIDO grava a senha (só hash) e muda o status para 'Ativa'. O link deixa de
    valer porque o estado ATIVA vem antes de VALIDO; a senha não altera usu_link_gerado_em (A3).
    Devolve o ResultadoLink (VALIDO quando ativou).
    [US-10][RBN-CAD-06.1][RBN-CAD-06.3][FR-004][FR-005][I4]
    """
    with transaction.atomic():
        resultado = validar_link_ativacao(token, travar=True)
        if resultado.estado != EstadoLink.VALIDO:
            return resultado
        conta = resultado.usuario
        conta.set_password(senha)
        conta.usu_status = StatusConta.ATIVA
        conta.save(update_fields=["password", "usu_status"])
    return resultado
