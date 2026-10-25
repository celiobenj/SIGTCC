"""Testes de aceite da US-37: reenviar o link de ativação vencido (spec 003, história 3).

[US-37][RBN-CAD-06.9][FR-016]-[FR-018][Q5][Q13]
"""

from smtplib import SMTPException
from unittest import mock

from django.core import mail
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services
from sigtcc.apps.cadastro.choices import StatusConta
from sigtcc.apps.cadastro.models import Usuarios
from sigtcc.apps.cadastro.services import EstadoLink
from sigtcc.apps.cadastro.tests.apoio_acesso import (
    TesteAcesso,
    avancar_relogio,
    caminho_do_link,
    criar_aluno_com_turma,
)

URL_REENVIAR = reverse("cadastro:reenviar_link")
URL_DEFINIR = reverse("cadastro:definir_senha")


def token_do(caminho):
    """Token que está no caminho do link."""
    return caminho.split("/")[-2]


class ReenvioTest(TesteAcesso):
    """Cenários de aceite da US-37. [US-37][RBN-CAD-06.9]"""

    def setUp(self):
        super().setUp()
        self.aluno = criar_aluno_com_turma(matricula="2026000001")
        self.client.post(
            reverse("cadastro:primeiro_acesso_aluno"),
            {"matricula": "2026000001", "email": "ana@uea.edu.br"},
        )
        self.antigo = caminho_do_link(mail.outbox[0])
        mail.outbox.clear()

    def conta(self):
        """Conta do aluno, relida do banco."""
        return Usuarios.objects.get(pk=self.aluno.pk)

    def abrir_vencido(self):
        """Abre o link antigo 25 horas depois (o token fica na sessão)."""
        with avancar_relogio(horas=25):
            return self.client.get(self.antigo, follow=True)

    def reenviar(self):
        """Clica em "Reenviar link de ativação" 25 horas depois."""
        with avancar_relogio(horas=25):
            return self.client.post(URL_REENVIAR, follow=True)

    def test_cenario1_link_vencido(self):
        """Dado link com mais de 24 h, quando é aberto, então aviso e botão, sem formulário."""
        resposta = self.abrir_vencido()
        self.assertContains(resposta, mensagens.LINK_ATIVACAO_VENCEU)
        self.assertContains(resposta, mensagens.REENVIAR_LINK)
        self.assertContains(resposta, f'action="{URL_REENVIAR}"')
        self.assertNotContains(resposta, 'name="senha"')

    def test_cenario2_reenvio_gera_novo_link(self):
        """Dado o aviso de vencido, quando clica em reenviar, então novo link de 24 h."""
        self.abrir_vencido()
        resposta = self.reenviar()
        self.assertContains(resposta, mensagens.NOVO_LINK_ENVIADO)
        self.assertEqual(mail.outbox[0].to, ["ana@uea.edu.br"])
        novo = token_do(caminho_do_link(mail.outbox[0]))
        with avancar_relogio(horas=25):
            self.assertEqual(services.validar_link_ativacao(novo).estado, EstadoLink.VALIDO)
        with avancar_relogio(horas=49, minutos=1):
            self.assertEqual(services.validar_link_ativacao(novo).estado, EstadoLink.VENCIDO)

    def test_cenario3_link_anterior_invalido(self):
        """Dado novo link enviado, quando abre o anterior, então "Link inválido. Use o..."."""
        self.abrir_vencido()
        self.reenviar()
        with avancar_relogio(horas=25):
            resposta = self.client.get(self.antigo, follow=True)
        self.assertContains(resposta, mensagens.LINK_SUBSTITUIDO)
        with avancar_relogio(horas=25):
            self.client.get(caminho_do_link(mail.outbox[0]))
            self.client.post(URL_DEFINIR, {"senha": "Senha1234", "confirmacao": "Senha1234"})
        self.assertEqual(self.conta().usu_status, StatusConta.ATIVA)

    def test_cenario4_conta_ja_ativa(self):
        """Dado conta já ativada, quando abre um link antigo, então "Esta conta já..." no login."""
        Usuarios.objects.filter(pk=self.aluno.pk).update(usu_status=StatusConta.ATIVA)
        resposta = self.client.get(self.antigo, follow=True)
        self.assertRedirects(resposta, reverse("cadastro:entrar"))
        self.assertContains(resposta, mensagens.CONTA_JA_ATIVA)

    def test_cenario5_conta_resetada_nao_reenvia(self):
        """Dado reset pelo Professor, quando clica em reenviar, então orienta o primeiro acesso."""
        Usuarios.objects.filter(pk=self.aluno.pk).update(
            usu_email=None, password=None, usu_link_gerado_em=timezone.now()
        )
        resposta = self.client.get(self.antigo, follow=True)
        self.assertContains(resposta, mensagens.LINK_ATIVACAO_VENCEU)
        self.assertContains(resposta, mensagens.REENVIAR_LINK)
        resposta = self.client.post(URL_REENVIAR, follow=True)
        self.assertContains(resposta, mensagens.M08_REFAZER_PRIMEIRO_ACESSO)
        self.assertContains(resposta, reverse("cadastro:primeiro_acesso"))
        self.assertEqual(len(mail.outbox), 0)

    def test_reenvio_so_em_vencido(self):
        """A3: com o link válido, substituído ou de conta inativa, o POST não reenvia."""
        self.client.get(self.antigo)
        resposta = self.client.post(URL_REENVIAR)
        self.assertRedirects(resposta, URL_DEFINIR)
        self.assertEqual(len(mail.outbox), 0)
        Usuarios.objects.filter(pk=self.aluno.pk).update(usu_status=StatusConta.INATIVA)
        resposta = self.client.post(URL_REENVIAR, follow=True)
        self.assertContains(resposta, mensagens.M15_CONTA_INATIVA)
        self.assertEqual(len(mail.outbox), 0)

    def test_reenvio_de_link_substituido(self):
        """A3: link substituído não reenvia e mostra "Link inválido. Use o..."."""
        self.client.get(self.antigo)
        with avancar_relogio(minutos=1):
            services.gerar_link_ativacao(self.conta())
        resposta = self.client.post(URL_REENVIAR, follow=True)
        self.assertContains(resposta, mensagens.LINK_SUBSTITUIDO)
        self.assertEqual(len(mail.outbox), 0)

    def test_reenvio_sem_token_na_sessao(self):
        """A3: sem token na sessão, o reenvio trata como link adulterado."""
        resposta = self.client.post(URL_REENVIAR, follow=True)
        self.assertContains(resposta, mensagens.LINK_SUBSTITUIDO)
        self.assertEqual(len(mail.outbox), 0)

    def test_reenvio_so_por_post(self):
        """O reenvio muda dados: só por POST."""
        self.assertEqual(self.client.get(URL_REENVIAR).status_code, 405)

    def test_falha_no_envio_do_reenvio(self):
        """Q13: falha no envio mostra a M-17 e mantém o link anterior e o botão."""
        self.abrir_vencido()
        gerado_em = self.conta().usu_link_gerado_em
        with mock.patch(
            "sigtcc.apps.cadastro.services.send_mail", side_effect=SMTPException("fora")
        ):
            resposta = self.reenviar()
        self.assertContains(resposta, mensagens.M17_FALHA_ENVIO)
        self.assertContains(resposta, mensagens.REENVIAR_LINK)
        self.assertEqual(self.conta().usu_link_gerado_em, gerado_em)
        resposta = self.reenviar()
        self.assertContains(resposta, mensagens.NOVO_LINK_ENVIADO)

    def test_token_sai_da_sessao_depois_do_reenvio(self):
        """A3: o token sai da sessão quando o reenvio termina."""
        self.abrir_vencido()
        self.assertIn("token_ativacao", self.client.session)
        self.reenviar()
        self.assertNotIn("token_ativacao", self.client.session)
