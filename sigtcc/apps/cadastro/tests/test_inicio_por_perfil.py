"""Raiz do sistema leva à primeira tela de cada tipo de conta (spec 003, FR-010).

A rota /painel/ e o item "Início" do menu saíram; o logo da barra superior, o login e o
LOGIN_REDIRECT_URL apontam para a raiz.

[US-11][RBN-CAD-06.4][FR-010][Q7]
"""

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import StatusConta, Titulacao
from sigtcc.apps.cadastro.models import MembrosExternos, Secretarios
from sigtcc.apps.cadastro.tests.fabricas import (
    criar_aluno,
    criar_curso,
    criar_docente,
    criar_usuario,
)

RAIZ = reverse("cadastro:inicio")


def _aluno():
    """Aluno com a conta já ativada. [US-10]"""
    usuario = criar_aluno().alu
    usuario.usu_status = StatusConta.ATIVA
    usuario.save()
    return usuario


def _secretaria():
    """Conta de Secretaria de um curso novo. [US-03][RBN-CAD-02.1]"""
    usuario = criar_usuario()
    Secretarios.objects.create(sec=usuario, sec_cur=criar_curso())
    return usuario


def _membro_externo():
    """Membro Externo sem validade (não vence). [US-05][RBN-CAD-03.1]"""
    usuario = criar_usuario()
    MembrosExternos.objects.create(
        mem=usuario, mem_titulacao=Titulacao.MESTRE, mem_instituicao="Universidade Federal"
    )
    return usuario


class InicioPorPerfilTest(TestCase):
    """Dado cada tipo de conta logado, quando abre a raiz, então vai à sua primeira tela."""

    def assertRaizLevaA(self, usuario, rota):
        """Confere o redirecionamento da raiz e que o destino abre para o usuário."""
        self.client.force_login(usuario)
        resposta = self.client.get(RAIZ)
        self.assertRedirects(resposta, reverse(rota), fetch_redirect_response=False)
        self.assertEqual(self.client.get(reverse(rota)).status_code, 200)

    def test_aluno_vai_as_minhas_turmas(self):
        self.assertRaizLevaA(_aluno(), "cadastro:minhas_turmas")

    def test_docente_vai_as_turmas(self):
        self.assertRaizLevaA(criar_docente().doc, "cadastro:turmas")

    def test_secretaria_vai_as_defesas(self):
        self.assertRaizLevaA(_secretaria(), "defesa:defesas")

    def test_membro_externo_vai_as_minhas_bancas(self):
        self.assertRaizLevaA(_membro_externo(), "defesa:minhas_bancas")

    def test_visitante_vai_ao_login(self):
        self.assertRedirects(self.client.get(RAIZ), reverse("cadastro:entrar"))

    def test_conta_sem_tipo_recebe_403_sem_laco(self):
        """Conta sem especialização: 403 com a M-02, em vez de ir e voltar entre raiz e login."""
        self.client.force_login(criar_usuario())
        resposta = self.client.get(RAIZ)
        self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)


class PainelRemovidoTest(TestCase):
    """A rota /painel/ não existe mais; o logo e o login usam a raiz. [FR-010]"""

    def test_rota_painel_nao_existe(self):
        self.client.force_login(criar_docente().doc)
        self.assertEqual(self.client.get("/painel/").status_code, 404)

    def test_logo_e_login_apontam_para_a_raiz(self):
        self.assertEqual(settings.LOGIN_REDIRECT_URL, "cadastro:inicio")
        self.client.force_login(criar_docente().doc)
        resposta = self.client.get(reverse("cadastro:perfil"))
        self.assertContains(resposta, f'<a class="logo" href="{RAIZ}">', html=False)
