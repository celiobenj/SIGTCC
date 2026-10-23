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
import secrets
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.base_user import BaseUserManager
from django.core import signing
from django.core.cache import caches
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.db import IntegrityError, connection, transaction
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import Resolver404, resolve, reverse
from django.utils import timezone
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import url_has_allowed_host_and_scheme

from sigtcc.apps.cadastro.choices import StatusConta
from sigtcc.apps.cadastro.mensagens import (
    CONTA_JA_ATIVA,
    CURSO_NAO_RECONHECIDO,
    EMAIL_DE_OUTRA_CONTA_ALUNO,
    ITEM_INDISPONIVEL,
    LINK_ATIVACAO_ENVIADO,
    M05_EMAIL_EM_USO,
    M06_CONFIRMACAO_EMAIL_ENVIADA,
    M07_EMAIL_ATUALIZADO,
    M08_REFAZER_PRIMEIRO_ACESSO,
    M09_LINK_EMAIL_INVALIDO,
    M15_CONTA_INATIVA,
    M16_ACESSO_EXPIRADO,
    M17_FALHA_ENVIO,
    NOVO_LINK_ENVIADO,
    PERFIL_ATUALIZADO,
)
from sigtcc.apps.cadastro.models import Alunos, EquivalenciaCursos, Notificacoes, Usuarios
from sigtcc.apps.cadastro.permissoes import (
    pode_resetar_primeiro_acesso,
    tipo_conta,
    validade_vencida,
)
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
    # Spec 004 (research B4): exclusão definitiva de turma, sem tabela para o registro.
    TURMA_EXCLUIDA = "TURMA_EXCLUIDA"
    # Spec 002 (research C18): eventos da Gestão de Contas. [US-03][US-04][US-05][US-06][US-50]
    CONTA_CRIADA = "CONTA_CRIADA"
    CONTA_ALTERADA = "CONTA_ALTERADA"
    CONTA_INATIVADA = "CONTA_INATIVADA"
    CONTA_REATIVADA = "CONTA_REATIVADA"
    ACESSO_PRORROGADO = "ACESSO_PRORROGADO"
    CONTA_EXPIRADA = "CONTA_EXPIRADA"
    VALIDADE_RECALCULADA = "VALIDADE_RECALCULADA"
    SENHA_GESTOR_INCORRETA = "SENHA_GESTOR_INCORRETA"


class _AutorSistema:
    """Autor de eventos feitos pelo próprio sistema (comando, expiração, recálculo).

    [FR-047][research C18][I5]
    """

    pk = "sistema"

    def __repr__(self):
        """Representação em texto (só para depuração)."""
        return "AUTOR_SISTEMA"


# Valor de autor aceito por registrar_evento: grava autor=sistema (spec 002, contrato §5).
AUTOR_SISTEMA = _AutorSistema()


def registrar_evento(evento, conta, autor=None, detalhe=""):
    """Grava uma linha no log de acesso: evento | conta=<id> | autor=<id ou própria> | detalhe.

    conta e autor são Usuarios ou None; autor também pode ser AUTOR_SISTEMA (spec 002, C18).
    detalhe é montado pelo sistema, nunca com algo digitado pelo usuário; nunca entram senha,
    token, link ou e-mail completo (A13). A data e a hora vêm do formatador do log.
    [FR-029][SC-008][SC-009][FR-047]
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


def travar_email(email):
    """Trava consultiva por e-mail normalizado, até o fim da transação (spec 002, research C4).

    Serializa quem confere e grava o mesmo e-mail com caixa diferente; exige transação aberta.
    [US-03][US-05][FR-001][SC-003][I4]
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_xact_lock(hashtext(lower(%s)))", [email or ""])


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
    """Estado do login, com o usuário (quando encontrado) e os minutos restantes do bloqueio.

    [US-11][RBN-CAD-06.4]
    """

    estado: EstadoLogin
    usuario: object = None
    minutos_restantes: int = 0


def _cache_acesso():
    """Cache próprio do bloqueio (alias "acesso", research A2).

    [US-11][RBN-CAD-06.6]
    """
    return caches["acesso"]


def _chave_falhas(usuario):
    """Chave do contador de senhas incorretas da conta. [US-11][RBN-CAD-06.6]"""
    return f"acesso:falhas:{usuario.pk}"


def _chave_bloqueio(usuario):
    """Chave do instante do fim do bloqueio da conta. [US-11][RBN-CAD-06.6]"""
    return f"acesso:bloqueio:{usuario.pk}"


def fim_do_bloqueio(usuario):
    """Instante do fim do bloqueio vigente da conta, ou None. [US-11][RBN-CAD-06.6]"""
    valor = _cache_acesso().get(_chave_bloqueio(usuario))
    if not valor:
        return None
    fim = datetime.fromisoformat(valor)
    return fim if fim > timezone.now() else None


def minutos_restantes(fim):
    """ "N" da M-01: minutos restantes arredondados para cima, no mínimo 1 (spec Q16).

    [US-11][RBN-CAD-06.6][Q16]
    """
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
    """Estado do link e a conta a que ele se refere (quando a assinatura é válida).

    [FR-016][FR-026]
    """

    estado: EstadoLink
    usuario: object = None


@dataclass
class ResultadoPedido:
    """Resultado de um pedido que envia e-mail: enviado, ou a mensagem de recusa.

    [US-10][US-37][FR-026]
    """

    enviado: bool
    mensagem: str = ""


def _conta(usu_id, travar=False):
    """Conta pelo id, com as especializações; travada (select_for_update) se pedido (A17).

    [FR-026][I4]
    """
    contas = Usuarios.objects.select_related("alunos", "docentes", "membrosexternos", "secretarios")
    if travar:
        # Só a linha de Usuarios: o PostgreSQL não trava o lado opcional de um outer join.
        contas = contas.select_for_update(of=("self",))
    return contas.filter(pk=usu_id).first()


def _gravar_link_gerado_em(usuario):
    """Grava usu_link_gerado_em = agora (invalida os links anteriores) e relê do banco (A3).

    [FR-006][FR-026]
    """
    Usuarios.objects.filter(pk=usuario.pk).update(usu_link_gerado_em=timezone.now())
    usuario.refresh_from_db(fields=["usu_link_gerado_em"])
    return usuario.usu_link_gerado_em


def _url_absoluta(nome_rota, token):
    """Link absoluto com o SITE_URL do .env (A5).

    [FR-026]
    """
    return settings.SITE_URL + reverse(nome_rota, args=[token])


def _ler_token(token, salt):
    """Abre um token assinado; devolve (usu_id, dados) ou None se adulterado (Q23).

    [FR-016][Q23]
    """
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
    [US-10][US-37][RBN-CAD-06.1][RBN-CAD-06.9][FR-002]
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


# =============================================================================================
# Reenvio do link de ativação vencido (US-37; FR-017, FR-018; research A3)
# =============================================================================================


def reenviar_link_ativacao(token):
    """Reenvia o link só no estado VENCIDO, com a conta travada (A3, A17).

    Devolve (ResultadoLink, ResultadoPedido ou None). Sem e-mail (conta resetada) não reenvia
    (FR-018, M-08); nos demais estados, devolve só o estado para a tela correspondente.
    Falha no envio desfaz tudo e mantém o link anterior (M-17, Q13).
    [US-37][RBN-CAD-06.9][FR-017][FR-018][Q5][Q13]
    """
    try:
        with transaction.atomic():
            resultado = validar_link_ativacao(token, travar=True)
            if resultado.estado == EstadoLink.SEM_EMAIL:
                return resultado, ResultadoPedido(False, M08_REFAZER_PRIMEIRO_ACESSO)
            if resultado.estado != EstadoLink.VENCIDO:
                return resultado, None
            _gerar_e_enviar_ativacao(resultado.usuario)
    except FalhaEnvioEmail:
        return resultado, ResultadoPedido(False, M17_FALHA_ENVIO)
    return resultado, ResultadoPedido(True, NOVO_LINK_ENVIADO)


# =============================================================================================
# Alterar e redefinir a senha; reset do primeiro acesso (US-12; FR-012 a FR-015; A3, A5, A16)
# =============================================================================================

SALT_REDEFINICAO = "sigtcc.redefinicao"
SESSAO_TOKEN_REDEFINICAO = "token_redefinicao"


def senha_atual_confere(usuario, senha):
    """Senha atual de 8 a 64 caracteres e correta (RBN-CAD-06.5). [US-12][FR-012]"""
    return tamanho_de_senha_valido(senha) and usuario.check_password(senha)


def alterar_senha(usuario, atual, nova):
    """Troca a senha em "Meu perfil", com a conta travada; devolve a conta ou None.

    None quando a senha atual não confere ("Senha atual incorreta"). Quem chama mantém a
    própria sessão com update_session_auth_hash; as outras caem (Q19).
    [US-12][RBN-CAD-06.5][FR-012][Q19][FR-029]
    """
    with transaction.atomic():
        conta = _conta(usuario.pk, travar=True)
        if not senha_atual_confere(conta, atual):
            return None
        conta.set_password(nova)
        conta.save(update_fields=["password"])
    registrar_evento(EventoAcesso.SENHA_ALTERADA, conta)
    return conta


def _resumo_da_senha(usuario):
    """Resumo (HMAC, 12 caracteres) do hash atual da senha: o link cai se a senha mudar (A3).

    [US-12][RBN-CAD-06.7]
    """
    return salted_hmac("sigtcc.redefinicao.senha", usuario.password or "").hexdigest()[:12]


def gerar_link_redefinicao(usuario):
    """Gera o link de redefinição (24 h) e invalida os anteriores. Devolve a URL absoluta.

    [US-12][RBN-CAD-06.7][FR-014][FR-026]
    """
    gerado_em = _gravar_link_gerado_em(usuario)
    dados = {"u": usuario.pk, "g": gerado_em.isoformat(), "s": _resumo_da_senha(usuario)}
    return _url_absoluta("cadastro:redefinir_senha", signing.dumps(dados, salt=SALT_REDEFINICAO))


def enviar_link_redefinicao(email):
    """ "Esqueci minha senha": só para conta 'Ativa' e com a validade em dia, sem revelar nada.

    Recebe o e-mail digitado (contrato §4). O link é gerado na requisição e o e-mail sai depois do
    commit, numa thread sem acesso ao banco (ou na própria requisição, com SIGTCC_EMAIL_SINCRONO).
    Falha no envio só vai para o log; quem chama mostra sempre a mensagem genérica (Q13).
    [US-12][RBN-CAD-06.7][FR-013][Q13][I1]
    """
    email = normalizar_email(email)
    contas = list(Usuarios.objects.filter(usu_email__iexact=email)[:2]) if email else []
    if len(contas) != 1:
        if len(contas) > 1:
            registrar_evento(EventoAcesso.EMAIL_DUPLICADO, None, detalhe="contas=2+")
        return
    conta = contas[0]
    if conta.usu_status != StatusConta.ATIVA or validade_vencida(conta):
        return
    with transaction.atomic():
        link = gerar_link_redefinicao(conta)
        destino, contexto = conta.usu_email, {"nome": conta.usu_nome, "link": link}

        def enviar():
            """Envia o e-mail de redefinição; falha só no log. [US-12][RBN-CAD-06.7][Q13]"""
            try:
                enviar_email(
                    destino,
                    "SIGTCC: redefinição de senha",
                    "cadastro/emails/redefinicao.txt",
                    contexto,
                    conta=conta,
                )
            except Exception:
                # Já registrado no log por enviar_email; a tela não muda (Q13).
                pass

        if settings.SIGTCC_EMAIL_SINCRONO:
            transaction.on_commit(enviar)
        else:
            transaction.on_commit(lambda: threading.Thread(target=enviar, daemon=True).start())


def validar_link_redefinicao(token, travar=False):
    """Estado do link de redefinição (data-model; Q26; B1).

    ADULTERADO → INATIVA → EXPIRADA → SUBSTITUIDO (outro link, senha já trocada ou conta
    resetada) → VENCIDO → VALIDO (conta 'Ativa' e validade em dia).
    [US-12][RBN-CAD-06.7][FR-014][Q26]
    """
    lido = _ler_token(token, SALT_REDEFINICAO)
    if lido is None:
        return ResultadoLink(EstadoLink.ADULTERADO)
    usu_id, dados = lido
    try:
        gerado_em = datetime.fromisoformat(dados["g"])
        resumo = dados["s"]
    except (KeyError, TypeError, ValueError):
        return ResultadoLink(EstadoLink.ADULTERADO)
    usuario = _conta(usu_id, travar)
    if usuario is None:
        return ResultadoLink(EstadoLink.ADULTERADO)
    estado = _estado_da_conta(usuario)
    if estado is not None:
        return ResultadoLink(estado, usuario)
    if (
        usuario.usu_status != StatusConta.ATIVA
        or usuario.usu_link_gerado_em != gerado_em
        or not constant_time_compare(resumo, _resumo_da_senha(usuario))
    ):
        return ResultadoLink(EstadoLink.SUBSTITUIDO, usuario)
    if timezone.now() - gerado_em > VALIDADE_LINK:
        return ResultadoLink(EstadoLink.VENCIDO, usuario)
    return ResultadoLink(EstadoLink.VALIDO, usuario)


def redefinir_senha(token, nova):
    """Redefine a senha pelo link: revalida com a conta travada e grava (FR-014; A17).

    Todas as sessões da conta caem (o resumo da senha na sessão muda, Q19).
    [US-12][RBN-CAD-06.7][FR-014][Q19][Q26][FR-029]
    """
    with transaction.atomic():
        resultado = validar_link_redefinicao(token, travar=True)
        if resultado.estado != EstadoLink.VALIDO:
            return resultado
        conta = resultado.usuario
        conta.set_password(nova)
        conta.save(update_fields=["password"])
    registrar_evento(EventoAcesso.SENHA_REDEFINIDA, conta)
    return resultado


def resetar_primeiro_acesso(professor, aluno):
    """ "Resetar primeiro acesso": limpa e-mail e senha e volta a conta a 'Aguardando Ativação'.

    professor: Usuarios logado (com Docentes); aluno: instância de Alunos. Confere a permissão de
    novo com a conta travada (Q27, Q29) e levanta PermissionDenied se faltar. Grava
    usu_link_gerado_em = agora, o que invalida os links pendentes; a sessão do aluno cai pelo
    backend (A16).
    [US-12][RBN-CAD-06.8][FR-015][Q9][Q27][Q29][FR-029]
    """
    with transaction.atomic():
        conta = _conta(aluno.pk, travar=True)
        aluno.alu = conta
        if not pode_resetar_primeiro_acesso(professor, aluno):
            raise PermissionDenied
        conta.usu_email = None
        conta.password = None
        conta.usu_status = StatusConta.AGUARDANDO_ATIVACAO
        conta.usu_link_gerado_em = timezone.now()
        conta.save(update_fields=["usu_email", "password", "usu_status", "usu_link_gerado_em"])
    registrar_evento(EventoAcesso.RESET_PRIMEIRO_ACESSO, conta, autor=professor)


# =============================================================================================
# Perfil, assinatura e troca de e-mail (US-38; FR-019 a FR-021; research A4, A11)
# =============================================================================================

SALT_TROCA_EMAIL = "sigtcc.troca_email"
TAMANHO_MAXIMO_ASSINATURA = 2 * 1024 * 1024
# Tipo da imagem pelos bytes iniciais e as extensões aceitas para cada tipo (A11).
_TIPOS_ASSINATURA = {
    "png": (b"\x89PNG\r\n\x1a\n", ("png",), "image/png"),
    "jpg": (b"\xff\xd8\xff", ("jpg", "jpeg"), "image/jpeg"),
}


class EmailEmUso(Exception):
    """O novo e-mail já é de outra conta (M-05). [US-38][RBN-CAD-13.1]"""


class EstadoTroca(enum.Enum):
    """Estados do link de troca de e-mail (A4; spec Q11, Q24, Q28). [US-38][RBN-CAD-13.1]"""

    VALIDO = "valido"
    INVALIDO = "invalido"
    EM_USO = "em_uso"


@dataclass
class ResultadoTroca:
    """Estado do link de troca, a conta e o novo e-mail.

    [US-38][RBN-CAD-13.1]
    """

    estado: EstadoTroca
    usuario: object = None
    novo_email: str = ""


@dataclass
class ResultadoPerfil:
    """Resultado de salvar o perfil: sucesso e a mensagem a mostrar.

    [US-38][RBN-CAD-13.1]
    """

    sucesso: bool
    mensagem: str


def curso_do_codigo(codigo):
    """Curso do NUCOMP pelo código de curso da UEA (código inteiro), ou None.

    None = "Código não reconhecido". Fica aqui, no módulo de base, e é reexportada por
    services_turmas, sem importação circular (spec 004, research B6 e N2).
    [US-08][RBN-CAD-05.7][spec 004, FR-015][Q3][Q5]
    """
    if not codigo:
        return None
    equivalencia = (
        EquivalenciaCursos.objects.select_related("eqc_cur").filter(eqc_codigo_uea=codigo).first()
    )
    return equivalencia.eqc_cur if equivalencia else None


def curso_do_aluno(aluno):
    """Nome do curso pela equivalência do código da UEA, ou "Código não reconhecido".

    Delega a curso_do_codigo (spec 004, research B6).
    [US-38][RBN-CAD-13.1][RBN-CAD-05.7]
    """
    curso = curso_do_codigo(aluno.alu_codigo_curso)
    return curso.cur_nome if curso else CURSO_NAO_RECONHECIDO


def tipo_por_bytes(inicio):
    """ "png", "jpg" ou None, pelos bytes iniciais do arquivo (A11).

    [US-38][RBN-CAD-13.1][FR-020]
    """
    for tipo, (assinatura_bytes, _extensoes, _mime) in _TIPOS_ASSINATURA.items():
        if inicio.startswith(assinatura_bytes):
            return tipo
    return None


def tipo_da_assinatura(arquivo):
    """Tipo da imagem enviada ("png" ou "jpg"), ou None se não for aceita (M-04).

    Até 2 MB; o tipo vem dos bytes e a extensão do nome precisa bater com ele (I7).
    [US-38][RBN-CAD-13.1][FR-020]
    """
    if arquivo.size > TAMANHO_MAXIMO_ASSINATURA:
        return None
    arquivo.seek(0)
    inicio = arquivo.read(8)
    arquivo.seek(0)
    tipo = tipo_por_bytes(inicio)
    extensao = arquivo.name.rsplit(".", 1)[-1].lower() if "." in arquivo.name else ""
    if tipo is None or extensao not in _TIPOS_ASSINATURA[tipo][1]:
        return None
    return tipo


def mime_da_assinatura(tipo):
    """Content-Type do tipo detectado. [FR-020]"""
    return _TIPOS_ASSINATURA[tipo][2]


def _registro_com_assinatura(conta):
    """Docentes ou MembrosExternos da conta (quem tem assinatura), ou None.

    [US-38][RBN-CAD-13.1][FR-020]
    """
    tipo = tipo_conta(conta)
    if tipo == "docente":
        return conta.docentes, "doc_assinatura_path"
    if tipo == "membro_externo":
        return conta.membrosexternos, "mem_assinatura_path"
    return None, None


def caminho_da_assinatura(usuario):
    """Caminho da imagem de assinatura do usuário (relativo a MEDIA_ROOT), ou None. [FR-020]"""
    registro, campo = _registro_com_assinatura(usuario)
    return getattr(registro, campo) if registro is not None else None


def salvar_assinatura(conta, arquivo, tipo):
    """Grava a imagem em assinaturas/<usu_id>_<aleatório>.<ext> e o caminho no registro.

    O arquivo anterior é apagado só depois do commit (A11). Devolve o caminho novo.
    [US-38][RBN-CAD-13.1][FR-020]
    """
    registro, campo = _registro_com_assinatura(conta)
    nome = f"assinaturas/{conta.pk}_{secrets.token_hex(8)}.{tipo}"
    caminho = default_storage.save(nome, arquivo)
    anterior = getattr(registro, campo)
    setattr(registro, campo, caminho)
    registro.save(update_fields=[campo])
    if anterior:
        transaction.on_commit(lambda: default_storage.delete(anterior))
    return caminho


def _resumo_do_email(email):
    """Resumo (HMAC) do e-mail atual: o link de troca cai se o e-mail da conta mudar (A4).

    [US-38][RBN-CAD-13.1][FR-021]
    """
    return salted_hmac("sigtcc.troca_email.atual", (email or "").lower()).hexdigest()[:12]


def pedir_troca_email(conta, novo, autor=None):
    """Envia ao novo e-mail o link de confirmação (24 h); o e-mail atual continua valendo.

    Levanta EmailEmUso (M-05) ou FalhaEnvioEmail (M-17); deve rodar dentro de
    transaction.atomic(), para a falha desfazer o salvamento inteiro (A5, m13). autor: quem
    pediu a troca, quando não é a própria conta (troca pelo gestor, spec 002, FR-008).
    [US-38][RBN-CAD-13.1][FR-021][Q11][Q24][FR-029]
    """
    if email_em_uso(novo, exceto=conta):
        raise EmailEmUso
    dados = {
        "u": conta.pk,
        "r": _resumo_do_email(conta.usu_email),
        "n": novo,
        "e": timezone.now().isoformat(),
    }
    link = _url_absoluta("cadastro:confirmar_email", signing.dumps(dados, salt=SALT_TROCA_EMAIL))
    try:
        enviar_email(
            novo,
            "SIGTCC: confirme o seu novo e-mail",
            "cadastro/emails/confirmar_email.txt",
            {"nome": conta.usu_nome, "link": link},
            conta=conta,
        )
    except Exception as erro:
        raise FalhaEnvioEmail from erro
    registrar_evento(
        EventoAcesso.TROCA_EMAIL_PEDIDA, conta, autor=autor, detalhe=dominio_do_email(novo)
    )


def atualizar_perfil(usuario, dados, arquivo=None, tipo_arquivo=None):
    """Salva só os campos que o papel pode editar (FR-019); troca de e-mail pede confirmação.

    Aluno: e-mail. Docente: assinatura. Membro Externo: e-mail, titulação, instituição e
    assinatura. Secretaria: nada. Com troca de e-mail, a mensagem é só a M-06 (Q11); falha no
    envio desfaz tudo (M-17).
    [US-38][RBN-CAD-13.1][FR-019][FR-020][FR-021][Q11]
    """
    tipo = tipo_conta(usuario)
    novo = normalizar_email(dados.get("email")) if tipo in ("aluno", "membro_externo") else None
    troca = novo is not None and novo.lower() != (usuario.usu_email or "").lower()
    caminho_novo = None
    try:
        with transaction.atomic():
            conta = _conta(usuario.pk, travar=True)
            if tipo == "membro_externo":
                membro = conta.membrosexternos
                membro.mem_titulacao = dados["titulacao"]
                membro.mem_instituicao = dados["instituicao"]
                membro.save(update_fields=["mem_titulacao", "mem_instituicao"])
            if arquivo is not None and tipo in ("docente", "membro_externo"):
                caminho_novo = salvar_assinatura(conta, arquivo, tipo_arquivo)
            if troca:
                pedir_troca_email(conta, novo)
    except (FalhaEnvioEmail, EmailEmUso) as erro:
        if caminho_novo:
            default_storage.delete(caminho_novo)
        mensagem = M05_EMAIL_EM_USO if isinstance(erro, EmailEmUso) else M17_FALHA_ENVIO
        return ResultadoPerfil(False, mensagem)
    return ResultadoPerfil(True, M06_CONFIRMACAO_EMAIL_ENVIADA if troca else PERFIL_ATUALIZADO)


def validar_link_troca_email(token, travar=False):
    """Estado do link de troca de e-mail (A4; spec Q11, Q24, Q28).

    INVALIDO: adulterado, com mais de 24 h ou com o e-mail da conta já mudado (inclusive por esta
    troca). EM_USO: o novo e-mail passou a ser de outra conta.
    [US-38][RBN-CAD-13.1][FR-021]
    """
    lido = _ler_token(token, SALT_TROCA_EMAIL)
    if lido is None:
        return ResultadoTroca(EstadoTroca.INVALIDO)
    usu_id, dados = lido
    try:
        emitido_em = datetime.fromisoformat(dados["e"])
        resumo, novo = dados["r"], dados["n"]
    except (KeyError, TypeError, ValueError):
        return ResultadoTroca(EstadoTroca.INVALIDO)
    conta = _conta(usu_id, travar)
    if (
        conta is None
        or timezone.now() - emitido_em > VALIDADE_LINK
        or not constant_time_compare(resumo, _resumo_do_email(conta.usu_email))
    ):
        return ResultadoTroca(EstadoTroca.INVALIDO)
    if email_em_uso(novo, exceto=conta):
        return ResultadoTroca(EstadoTroca.EM_USO, conta, novo)
    return ResultadoTroca(EstadoTroca.VALIDO, conta, novo)


def confirmar_troca_email(token):
    """Confirma a troca (POST do botão "Confirmar novo e-mail"), com a conta travada (Q28).

    Devolve a mensagem: M-07 (trocado), M-09 (link inválido) ou M-05 (e-mail ocupado).
    [US-38][RBN-CAD-13.1][FR-021][Q28][FR-029]
    """
    with transaction.atomic():
        resultado = validar_link_troca_email(token, travar=True)
        if resultado.estado == EstadoTroca.INVALIDO:
            return M09_LINK_EMAIL_INVALIDO
        if resultado.estado == EstadoTroca.EM_USO:
            return M05_EMAIL_EM_USO
        conta = resultado.usuario
        conta.usu_email = resultado.novo_email
        try:
            with transaction.atomic():
                conta.save(update_fields=["usu_email"])
        except IntegrityError:
            return M05_EMAIL_EM_USO
    registrar_evento(
        EventoAcesso.TROCA_EMAIL_CONFIRMADA, conta, detalhe=dominio_do_email(conta.usu_email)
    )
    return M07_EMAIL_ATUALIZADO


# =============================================================================================
# Central de notificações (US-38; FR-022, FR-023; research A12)
# =============================================================================================


def destino_da_notificacao(link):
    """Caminho interno de not_link_tela, ou None se não leva a uma página existente.

    Aceita só caminho relativo começando com "/", sem host, com query opcional; o caminho
    precisa resolver numa rota (Q10) e passar por url_has_allowed_host_and_scheme (A12).
    [US-38][RBN-CAD-13.2][FR-023][Q10]
    """
    if not link or not link.startswith("/") or link.startswith("//") or "\\" in link:
        return None
    partes = urlsplit(link)
    if partes.scheme or partes.netloc:
        return None
    try:
        resolve(partes.path)
    except Resolver404:
        return None
    if not url_has_allowed_host_and_scheme(link, allowed_hosts=None):
        return None
    return link


def abrir_notificacao(usuario, not_id):
    """Marca a notificação do usuário como lida e devolve (notificação, destino) ou None.

    None quando a notificação não existe ou é de outra conta (a view responde 404).
    [US-38][RBN-CAD-13.2][FR-023]
    """
    notificacao = Notificacoes.objects.filter(pk=not_id, not_usu_id=usuario.pk).first()
    if notificacao is None:
        return None
    if not notificacao.not_lida:
        Notificacoes.objects.filter(pk=notificacao.pk).update(not_lida=True)
    return notificacao, destino_da_notificacao(notificacao.not_link_tela)


def marcar_todas_lidas(usuario):
    """ "Marcar como lidas": todas as notificações do usuário. [US-38][RBN-CAD-13.2][FR-022]"""
    Notificacoes.objects.filter(not_usu_id=usuario.pk, not_lida=False).update(not_lida=True)


# =============================================================================================
# Criação de notificações (spec 004, research B21; contrato §4 da spec 004)
# =============================================================================================

LIMITE_NOTIFICACAO = 500
RETICENCIAS = "…"


def _cortar(texto, limite):
    """Corta o texto no limite, terminando com reticências. [US-38][RBN-CAD-13.2][B-1]"""
    if len(texto) <= limite:
        return texto
    return texto[: limite - len(RETICENCIAS)].rstrip() + RETICENCIAS


def montar_mensagem_cortada(modelo, campo_longo, **campos):
    """Monta a mensagem a partir do modelo (str.format) cortando primeiro o campo longo.

    Assim a frase fica inteira e só a parte variável longa (a justificativa) perde o fim, para o
    texto caber nos 500 caracteres da notificação (achado B-1).
    [US-09][RBN-CAD-05.4][spec 004, B21][B-1]
    """
    sem_campo = modelo.format(**{**campos, campo_longo: ""})
    espaco = LIMITE_NOTIFICACAO - len(sem_campo)
    campos[campo_longo] = _cortar(campos[campo_longo], max(espaco, len(RETICENCIAS)))
    return _cortar(modelo.format(**campos), LIMITE_NOTIFICACAO)


def notificar(usuario, mensagem, link=None):
    """Única forma de criar uma notificação (contrato §4 da spec 004).

    Corta a mensagem em 500 caracteres com reticências; grava o link só se for interno e válido
    (destino_da_notificacao), senão sem link; preenche data e hora e "não lida".
    [US-38][RBN-CAD-13.2][US-08][US-09][spec 004, B21][I-5]
    """
    destino = destino_da_notificacao(link) if link else None
    return Notificacoes.objects.create(
        not_usu=usuario,
        not_mensagem=_cortar(mensagem, LIMITE_NOTIFICACAO),
        not_link_tela=destino,
        not_data_hora=timezone.now(),
        not_lida=False,
    )
