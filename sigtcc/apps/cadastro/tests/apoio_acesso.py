"""Apoio aos testes da feature 003: classe base, contas prontas e relógio controlado.

Os testes usam force_login (o backend não autentica por senha, research A1), e-mail em memória,
caches locais e SIGTCC_EMAIL_SINCRONO = True (research A5).

[infraestrutura de teste da feature 003]
"""

import logging
import re
from contextlib import contextmanager
from datetime import timedelta
from unittest import mock

from django.core.cache import caches
from django.test import TestCase, override_settings
from django.utils import timezone

from sigtcc.apps.cadastro.choices import StatusConta, Titulacao
from sigtcc.apps.cadastro.models import (
    Alunos,
    AlunosTurmas,
    Coordenadores,
    Docentes,
    MembrosExternos,
    Notificacoes,
    Secretarios,
)
from sigtcc.apps.cadastro.tests.fabricas import (
    criar_curso,
    criar_turma,
    criar_usuario,
    proximo,
)

SENHA = "Senha1234"

_CACHE_LOCAL = {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    CACHES={
        "default": {**_CACHE_LOCAL, "LOCATION": "testes-default"},
        "acesso": {**_CACHE_LOCAL, "LOCATION": "testes-acesso"},
    },
    SIGTCC_EMAIL_SINCRONO=True,
    SITE_URL="http://testserver",
)
class TesteAcesso(TestCase):
    """Base dos testes da feature 003, com os caches limpos a cada teste.

    O log de acesso não grava no arquivo da pasta logs/ durante os testes; assertLogs continua
    capturando as linhas.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        registro = logging.getLogger("sigtcc.acesso")
        cls.enterClassContext(mock.patch.object(registro, "handlers", [logging.NullHandler()]))

    def setUp(self):
        super().setUp()
        caches["default"].clear()
        caches["acesso"].clear()


@contextmanager
def avancar_relogio(minutos=0, horas=0, dias=0):
    """Faz timezone.now() devolver o instante atual mais o intervalo (research A2, A3, A19)."""
    alvo = timezone.now() + timedelta(minutes=minutos, hours=horas, days=dias)
    with mock.patch("django.utils.timezone.now", return_value=alvo):
        yield alvo


def _com_senha(usuario, senha):
    """Grava a senha (só hash) quando informada."""
    if senha:
        usuario.set_password(senha)
        usuario.save()
    return usuario


def criar_aluno_com_turma(
    matricula=None, email=None, status=StatusConta.AGUARDANDO_ATIVACAO, senha=None, turma=None
):
    """Aluno matriculado numa turma (ativa, por padrão). Devolve o registro de Alunos.

    [US-10][RBN-CAD-06.1][US-11][RBN-CAD-06.4]
    """
    usuario = _com_senha(criar_usuario(email=email, status=status), senha)
    if email is None:
        usuario.usu_email = None
        usuario.save()
    aluno = Alunos.objects.create(
        alu=usuario,
        alu_matricula=matricula or f"{2026100000 + proximo():010d}",
        alu_codigo_curso="EST08MCPD",
    )
    AlunosTurmas.objects.create(
        mat_alu=aluno, mat_tur=turma or criar_turma(), mat_data_inscricao=timezone.now()
    )
    return aluno


def criar_docente_ativo(email=None, senha=SENHA, status=StatusConta.ATIVA, curso=None):
    """Docente com conta e senha. Devolve o Usuarios. [US-11][RBN-CAD-06.4]"""
    usuario = _com_senha(criar_usuario(email=email, status=status), senha)
    Docentes.objects.create(
        doc=usuario, doc_titulacao=Titulacao.DOUTOR, doc_cur=curso or criar_curso()
    )
    return usuario


def criar_coordenador(email=None, senha=SENHA):
    """Docente Coordenador de Curso. Devolve o Usuarios. [US-03][RBN-CAD-01.1]"""
    curso = criar_curso()
    usuario = criar_docente_ativo(email=email, senha=senha, curso=curso)
    Coordenadores.objects.create(cor_cur=curso, cor_doc=usuario.docentes)
    return usuario


def criar_secretaria(email=None, senha=SENHA, status=StatusConta.ATIVA, curso=None):
    """Conta de Secretaria (do curso informado ou de um curso novo). Devolve o Usuarios.

    [US-03][RBN-CAD-02.1][spec 004, research B24]
    """
    usuario = _com_senha(criar_usuario(email=email, status=status), senha)
    Secretarios.objects.create(sec=usuario, sec_cur=curso or criar_curso())
    return usuario


def criar_membro_externo(
    email=None, senha=SENHA, status=StatusConta.ATIVA, validade=None, titulacao=Titulacao.MESTRE
):
    """Membro Externo com validade opcional. Devolve o Usuarios. [US-05][RBN-CAD-03.1]"""
    usuario = _com_senha(criar_usuario(email=email, status=status), senha)
    MembrosExternos.objects.create(
        mem=usuario,
        mem_titulacao=titulacao,
        mem_instituicao="Universidade Federal do Amazonas",
        mem_validade_ate=validade,
    )
    return usuario


def criar_notificacao(usuario, mensagem=None, link=None, lida=False, data_hora=None):
    """Notificação do usuário (as fábricas a criam; a feature 003 não cria, FR-028).

    [US-38][RBN-CAD-13.2]
    """
    return Notificacoes.objects.create(
        not_usu=usuario,
        not_mensagem=mensagem or f"Notificação {proximo()}",
        not_link_tela=link,
        not_data_hora=data_hora or timezone.now(),
        not_lida=lida,
    )


def caminho_do_link(mensagem):
    """Caminho do link que está no corpo do e-mail (SITE_URL = http://testserver nos testes)."""
    achado = re.search(r"http://testserver(/\S+)", mensagem.body)
    assert achado, "o e-mail não tem link"
    return achado.group(1)
