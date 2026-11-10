"""Segurança transversal da feature 003: links, sessão, cookies e acesso às páginas.

[SC-004][SC-008][FR-011][FR-025][B1][B2][I4][Q18]
"""

from django.conf import settings
from django.contrib.auth import authenticate
from django.core import mail
from django.test import Client
from django.urls import reverse

from sigtcc.apps.cadastro import mensagens, services
from sigtcc.apps.cadastro.choices import StatusConta
from sigtcc.apps.cadastro.models import Usuarios
from sigtcc.apps.cadastro.services import EstadoLink
from sigtcc.apps.cadastro.tests.apoio_acesso import (
    SENHA,
    TesteAcesso,
    avancar_relogio,
    criar_aluno_com_turma,
    criar_docente_ativo,
    criar_membro_externo,
    criar_notificacao,
    criar_secretaria,
)
from sigtcc.apps.cadastro.tests.fabricas import criar_turma

NOVA = "NovaSenha99"


def token(link):
    """Token do link absoluto."""
    return link.rstrip("/").split("/")[-1]


class LinksTest(TesteAcesso):
    """Links usados duas vezes e concorrência com o reset (I4, A17). [SC-006][I4]"""

    def test_link_de_ativacao_usado_duas_vezes(self):
        """Só o primeiro POST ativa; o segundo encontra a conta já ativa."""
        docente = criar_docente_ativo(senha=None, status=StatusConta.AGUARDANDO_ATIVACAO)
        ativacao = token(services.gerar_link_ativacao(docente))
        self.assertEqual(services.ativar_conta(ativacao, SENHA).estado, EstadoLink.VALIDO)
        self.assertEqual(services.ativar_conta(ativacao, NOVA).estado, EstadoLink.ATIVA)
        self.assertTrue(Usuarios.objects.get(pk=docente.pk).check_password(SENHA))

    def test_link_de_redefinicao_usado_duas_vezes(self):
        """Só o primeiro POST redefine; o segundo encontra a senha já trocada."""
        docente = criar_docente_ativo()
        redefinicao = token(services.gerar_link_redefinicao(docente))
        self.assertEqual(services.redefinir_senha(redefinicao, NOVA).estado, EstadoLink.VALIDO)
        estado = services.redefinir_senha(redefinicao, "Outra1234").estado
        self.assertEqual(estado, EstadoLink.SUBSTITUIDO)
        self.assertTrue(Usuarios.objects.get(pk=docente.pk).check_password(NOVA))

    def test_ativacao_depois_do_reset_nao_deixa_conta_ativa_sem_email(self):
        """A17: o reset antes da ativação faz o link valer SEM_EMAIL, e a conta não ativa."""
        professor = criar_docente_ativo()
        turma = criar_turma(tur_doc=professor.docentes)
        aluno = criar_aluno_com_turma(email="ana@uea.edu.br", turma=turma)
        ativacao = token(services.gerar_link_ativacao(Usuarios.objects.get(pk=aluno.pk)))
        services.resetar_primeiro_acesso(professor, aluno)
        self.assertEqual(services.ativar_conta(ativacao, SENHA).estado, EstadoLink.SEM_EMAIL)
        conta = Usuarios.objects.get(pk=aluno.pk)
        self.assertEqual(conta.usu_status, StatusConta.AGUARDANDO_ATIVACAO)
        self.assertIsNone(conta.usu_email)


class SessaoECookiesTest(TesteAcesso):
    """Sessão de 60 minutos sem uso, fim ao fechar o navegador e cookies (Q18; A6). [FR-011]"""

    def entrar(self, cliente=None):
        cliente = cliente or self.client
        criar_docente_ativo(email="prof@uea.edu.br")
        return cliente.post(
            reverse("cadastro:entrar"), {"credencial": "prof@uea.edu.br", "senha": SENHA}
        )

    def test_configuracao_da_sessao(self):
        """C1: 60 minutos, janela deslizante e fim ao fechar o navegador."""
        self.assertEqual(settings.SESSION_COOKIE_AGE, 3600)
        self.assertTrue(settings.SESSION_SAVE_EVERY_REQUEST)
        self.assertTrue(settings.SESSION_EXPIRE_AT_BROWSER_CLOSE)
        self.assertEqual(settings.SECURE_REFERRER_POLICY, "same-origin")
        self.assertTrue(settings.SECURE_CONTENT_TYPE_NOSNIFF)

    def test_cookie_de_sessao(self):
        """A6: HttpOnly, SameSite=Lax e sem Max-Age/Expires (some ao fechar o navegador)."""
        resposta = self.entrar()
        cookie = resposta.cookies[settings.SESSION_COOKIE_NAME]
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["samesite"], "Lax")
        self.assertEqual(cookie["max-age"], "")
        self.assertEqual(cookie["expires"], "")

    def test_cabecalhos_de_seguranca(self):
        """A3 e A11: Referrer-Policy same-origin e nosniff."""
        resposta = self.client.get(reverse("cadastro:entrar"))
        self.assertEqual(resposta["Referrer-Policy"], "same-origin")
        self.assertEqual(resposta["X-Content-Type-Options"], "nosniff")

    def test_sessao_cai_depois_de_60_minutos_sem_uso(self):
        """Q18: com 61 minutos sem uso, a próxima página leva ao login; com 59, continua."""
        self.entrar()
        outro = Client()
        outro.post(reverse("cadastro:entrar"), {"credencial": "prof@uea.edu.br", "senha": SENHA})
        with avancar_relogio(minutos=59):
            self.assertEqual(self.client.get(reverse("cadastro:painel")).status_code, 200)
        with avancar_relogio(minutos=61):
            resposta = outro.get(reverse("cadastro:painel"))
        self.assertRedirects(resposta, "/entrar/?next=/painel/", fetch_redirect_response=False)

    def test_senha_nunca_aparece(self):
        """SC-008: a senha não volta no HTML e fica só como hash."""
        resposta = self.client.post(
            reverse("cadastro:entrar"), {"credencial": "x@uea.edu.br", "senha": "SegredoX123"}
        )
        self.assertNotContains(resposta, "SegredoX123")
        docente = criar_docente_ativo(senha="SegredoX123")
        self.assertNotIn("SegredoX123", Usuarios.objects.get(pk=docente.pk).password)
        self.assertTrue(Usuarios.objects.get(pk=docente.pk).password.startswith("pbkdf2_"))

    def test_authenticate_do_django_nao_entra(self):
        """A1: authenticate() e Client.login() não pulam a ordem do login nem o bloqueio."""
        criar_docente_ativo(email="prof@uea.edu.br")
        self.assertIsNone(authenticate(usu_email="prof@uea.edu.br", password=SENHA))
        self.assertFalse(self.client.login(usu_email="prof@uea.edu.br", password=SENHA))


class TodasAsPaginasTest(TesteAcesso):
    """SC-004 (C2): nenhuma página interna sem login; restritas só para o perfil certo."""

    def setUp(self):
        super().setUp()
        professor = criar_docente_ativo()
        turma = criar_turma(tur_doc=professor.docentes)
        self.aluno = criar_aluno_com_turma(
            matricula="2026000077", status=StatusConta.ATIVA, senha=SENHA, turma=turma
        )
        self.notificacao = criar_notificacao(professor)

    def internas(self):
        """(método, caminho) de cada rota interna de contracts/rotas.md."""
        return (
            ("get", reverse("cadastro:painel")),
            ("get", reverse("cadastro:perfil")),
            ("get", reverse("cadastro:assinatura")),
            ("get", reverse("cadastro:alterar_senha")),
            ("get", reverse("cadastro:notificacoes")),
            ("get", reverse("cadastro:abrir_notificacao", args=[self.notificacao.pk])),
            ("post", reverse("cadastro:marcar_lidas")),
            ("get", reverse("cadastro:aluno", args=[self.aluno.pk])),
            ("get", reverse("cadastro:resetar_primeiro_acesso", args=[self.aluno.pk])),
            ("post", reverse("cadastro:resetar_primeiro_acesso", args=[self.aluno.pk])),
        )

    def test_sem_login_vai_ao_login(self):
        """Visitante em qualquer página interna vai ao login com next."""
        for metodo, caminho in self.internas():
            with self.subTest(caminho=caminho, metodo=metodo):
                resposta = getattr(self.client, metodo)(caminho)
                self.assertRedirects(
                    resposta, f"/entrar/?next={caminho}", fetch_redirect_response=False
                )
        resposta = self.client.post(reverse("cadastro:sair"))
        self.assertRedirects(resposta, reverse("cadastro:entrar"))

    def test_restritas_negadas_aos_outros_perfis(self):
        """Aluno, Secretaria e Membro Externo recebem 403 com a M-02 e sem dados do aluno."""
        restritas = [(m, c) for m, c in self.internas() if "/alunos/" in c]
        for usuario in (self.aluno.alu, criar_secretaria(), criar_membro_externo()):
            self.client.force_login(usuario)
            for metodo, caminho in restritas:
                with self.subTest(usuario=usuario.pk, caminho=caminho, metodo=metodo):
                    resposta = getattr(self.client, metodo)(caminho)
                    self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)
                    self.assertNotContains(resposta, "2026000077", status_code=403)
        self.assertEqual(Usuarios.objects.get(pk=self.aluno.pk).usu_status, StatusConta.ATIVA)
        self.assertEqual(len(mail.outbox), 0)
