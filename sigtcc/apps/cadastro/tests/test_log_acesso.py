"""Registro de eventos de acesso em arquivo de log (FR-029; SC-008; SC-009).

[FR-029][SC-008][SC-009][Q21][US-11][RBN-CAD-06.6][US-12][US-38]
"""

import io
import logging
import re
from unittest import mock

from django.conf import settings
from django.core import mail
from django.test import Client
from django.urls import reverse

from sigtcc.apps.cadastro import services
from sigtcc.apps.cadastro.choices import StatusConta
from sigtcc.apps.cadastro.models import Usuarios
from sigtcc.apps.cadastro.tests.apoio_acesso import (
    SENHA,
    TesteAcesso,
    caminho_do_link,
    criar_aluno_com_turma,
    criar_docente_ativo,
)
from sigtcc.apps.cadastro.tests.fabricas import criar_turma, criar_usuario

NOVA = "NovaSenha99"
LINHA = re.compile(
    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \| (?P<evento>[A-Z_]+) \| conta=(?P<conta>\S+)"
    r" \| autor=(?P<autor>\S+) \| (?P<detalhe>.*)$"
)


class LogAcessoTest(TesteAcesso):
    """Uma linha por evento, com conta, data e hora, e sem dados sensíveis. [FR-029][SC-009]"""

    def setUp(self):
        super().setUp()
        self.saida = io.StringIO()
        manipulador = logging.StreamHandler(self.saida)
        formato = settings.LOGGING["formatters"]["acesso"]["format"]
        manipulador.setFormatter(logging.Formatter(formato))
        registro = logging.getLogger("sigtcc.acesso")
        self.enterContext(mock.patch.object(registro, "handlers", [manipulador]))

    def linhas(self):
        """Linhas do log já separadas em evento, conta, autor e detalhe."""
        resultado = []
        for linha in self.saida.getvalue().splitlines():
            achado = LINHA.match(linha)
            self.assertIsNotNone(achado, f"linha fora do formato: {linha}")
            resultado.append(achado.groupdict())
        return resultado

    def eventos(self, nome):
        return [linha for linha in self.linhas() if linha["evento"] == nome]

    def test_seis_tipos_de_evento(self):
        """SC-009: cada um dos 6 tipos gera exatamente uma linha, com a conta."""
        professor = criar_docente_ativo(email="prof@uea.edu.br")
        turma = criar_turma(tur_doc=professor.docentes)
        aluno = criar_aluno_com_turma(
            email="ana@uea.edu.br", status=StatusConta.ATIVA, senha=SENHA, turma=turma
        )
        conta = str(professor.pk)

        # 1. Login com senha errada.
        self.client.post(
            reverse("cadastro:entrar"), {"credencial": "prof@uea.edu.br", "senha": "Errada123"}
        )
        self.assertEqual([e["conta"] for e in self.eventos("LOGIN_SENHA_INCORRETA")], [conta])
        # 2. Bloqueio por tentativas (mais duas senhas erradas).
        for _ in range(2):
            self.client.post(
                reverse("cadastro:entrar"), {"credencial": "prof@uea.edu.br", "senha": "Errada123"}
            )
        self.assertEqual([e["conta"] for e in self.eventos("BLOQUEIO")], [conta])
        # 3. Troca de senha em "Meu perfil".
        self.client.force_login(professor)
        self.client.post(
            reverse("cadastro:alterar_senha"),
            {"senha_atual": SENHA, "nova_senha": NOVA, "confirmacao": NOVA},
        )
        self.assertEqual([e["conta"] for e in self.eventos("SENHA_ALTERADA")], [conta])
        # 4. Redefinição de senha pelo link.
        anonimo = Client()
        with self.captureOnCommitCallbacks(execute=True):
            anonimo.post(reverse("cadastro:esqueci_senha"), {"email": "ana@uea.edu.br"})
        anonimo.get(caminho_do_link(mail.outbox[-1]))
        anonimo.post(reverse("cadastro:nova_senha"), {"senha": NOVA, "confirmacao": NOVA})
        self.assertEqual([e["conta"] for e in self.eventos("SENHA_REDEFINIDA")], [str(aluno.pk)])
        # 5. Troca de e-mail: pedido e confirmação.
        aluno_cliente = Client()
        # Conta relida: a senha acabou de ser redefinida (sessão antiga cairia, Q19).
        aluno_cliente.force_login(Usuarios.objects.get(pk=aluno.pk))
        aluno_cliente.post(reverse("cadastro:perfil"), {"email": "ana2@uea.edu.br"})
        aluno_cliente.post(caminho_do_link(mail.outbox[-1]))
        self.assertEqual(len(self.eventos("TROCA_EMAIL_PEDIDA")), 1)
        self.assertEqual(len(self.eventos("TROCA_EMAIL_CONFIRMADA")), 1)
        # 6. Reset do primeiro acesso, com o autor.
        self.client.post(reverse("cadastro:resetar_primeiro_acesso", args=[aluno.pk]))
        reset = self.eventos("RESET_PRIMEIRO_ACESSO")
        self.assertEqual([(e["conta"], e["autor"]) for e in reset], [(str(aluno.pk), conta)])

        texto = self.saida.getvalue()
        for sensivel in (
            SENHA,
            NOVA,
            "Errada123",
            "ana@uea.edu.br",
            "ana2@uea.edu.br",
            "prof@uea.edu.br",
            "http",
            "/ativar/",
            "/redefinir-senha/",
        ):
            with self.subTest(sensivel=sensivel):
                self.assertNotIn(sensivel, texto)
        self.assertEqual(
            {e["autor"] for e in self.linhas() if e["evento"] != "RESET_PRIMEIRO_ACESSO"},
            {"própria"},
        )

    def test_evento_tecnico_email_duplicado(self):
        """FR-029: e-mail duplicado na busca da credencial: sem conta, só a quantidade."""
        criar_usuario(email="dup@uea.edu.br")
        criar_usuario(email="DUP@uea.edu.br")
        services.autenticar("dup@uea.edu.br", SENHA)
        [linha] = self.linhas()
        self.assertEqual(
            (linha["evento"], linha["conta"], linha["detalhe"]),
            ("EMAIL_DUPLICADO", "-", "contas=2"),
        )

    def test_evento_tecnico_falha_no_envio(self):
        """FR-029: falha no envio de e-mail registra só o tipo do erro."""
        docente = criar_docente_ativo(
            email="prof@uea.edu.br", senha=None, status=StatusConta.AGUARDANDO_ATIVACAO
        )
        erro = OSError("prof@uea.edu.br recusado")
        with mock.patch("sigtcc.apps.cadastro.services.send_mail", side_effect=erro):
            self.assertFalse(services.enviar_link_ativacao(docente))
        [linha] = self.linhas()
        self.assertEqual((linha["evento"], linha["detalhe"]), ("FALHA_ENVIO_EMAIL", "OSError"))
        self.assertNotIn("prof@uea.edu.br", self.saida.getvalue())

    def test_credencial_inexistente_nao_gera_evento(self):
        """A13: credencial inexistente não é registrada (não grava o que foi digitado)."""
        services.autenticar("ninguem@uea.edu.br", SENHA)
        self.assertEqual(self.saida.getvalue(), "")
