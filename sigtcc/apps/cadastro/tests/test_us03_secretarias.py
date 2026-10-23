"""Testes de aceite da US-03 sobre a Secretaria (cenários 18 a 21, 37, 38 e 40) e da Q7 (tasks
T015).

[US-03][RBN-CAD-02.1][RBN-CAD-02.2][RBN-CAD-14.1][FR-020][FR-021][FR-022][FR-023][Q7]
"""

from django.core import mail
from django.urls import reverse

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import StatusConta
from sigtcc.apps.cadastro.models import Secretarios, Usuarios
from sigtcc.apps.cadastro.tests.apoio_contas import (
    EC,
    SI,
    TesteContas,
    coordenador_de,
    curso,
    secretaria_de,
)

NOVA = reverse("cadastro:contas_secretaria_nova")
LISTA = reverse("cadastro:contas_secretarias")


def editar(secretaria):
    """Endereço da edição da Secretaria (Usuarios)."""
    return reverse("cadastro:contas_secretaria_editar", args=[secretaria.pk])


def dados(curso_nome=SI, **campos):
    """POST válido do formulário da Secretaria."""
    valores = {
        "nome": "Joana Secretaria",
        "email": "secretaria.si@uea.edu.br",
        "curso_vinculado": curso(curso_nome).pk,
    }
    valores.update(campos)
    return valores


class CadastroSecretariaTest(TesteContas):
    """US-03 A4, E7 e E9 (cenários 18 a 21). [FR-020][FR-021]"""

    def setUp(self):
        super().setUp()
        self.client.force_login(coordenador_de(SI))

    def test_cenario_18_coordenador_cadastra_a_secretaria(self):
        resposta = self.client.post(NOVA, dados(), follow=True)
        self.assertContains(resposta, mensagens.SECRETARIA_CADASTRADA)
        conta = Usuarios.objects.get(usu_email="secretaria.si@uea.edu.br")
        self.assertEqual(conta.usu_status, StatusConta.AGUARDANDO_ATIVACAO)
        self.assertEqual(conta.secretarios.sec_cur, curso(SI))
        self.assertEqual(mail.outbox, [])

    def test_cenario_19_curso_ja_tem_secretaria(self):
        secretaria_de(SI)
        resposta = self.client.post(NOVA, dados())
        self.assertContains(resposta, mensagens.CURSO_JA_TEM_SECRETARIA)
        self.assertFalse(Usuarios.objects.filter(usu_email="secretaria.si@uea.edu.br").exists())

    def test_q7_secretaria_aguardando_ativacao_ocupa_o_curso(self):
        secretaria_de(SI, status=StatusConta.AGUARDANDO_ATIVACAO)
        resposta = self.client.post(NOVA, dados())
        self.assertContains(resposta, mensagens.CURSO_JA_TEM_SECRETARIA)

    def test_cenario_20_secretaria_inativada_libera_o_curso(self):
        secretaria_de(SI, status=StatusConta.INATIVA)
        self.client.post(NOVA, dados())
        self.assertTrue(Usuarios.objects.filter(usu_email="secretaria.si@uea.edu.br").exists())
        ativas = Secretarios.objects.filter(
            sec_cur=curso(SI), sec__usu_status__in=["Ativa", "Aguardando Ativação"]
        )
        self.assertEqual(ativas.count(), 1)

    def test_secretaria_so_no_curso_do_coordenador(self):
        resposta = self.client.post(NOVA, dados(curso_nome=EC))
        self.assertContains(resposta, mensagens.SO_DO_SEU_CURSO_CADASTRO)

    def test_cenario_21_secretaria_nao_ve_nova_secretaria(self):
        self.client.force_login(secretaria_de(SI))
        resposta = self.client.get(LISTA)
        self.assertNotContains(resposta, mensagens.NOVA_SECRETARIA)
        resposta = self.client.get(NOVA)
        self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)


class AlteracaoSecretariaTest(TesteContas):
    """US-03 A5 e cenários 37, 38 e 40. [FR-022][FR-023]"""

    def setUp(self):
        super().setUp()
        self.client.force_login(coordenador_de(SI))
        self.secretaria = secretaria_de(SI, email="sec@uea.edu.br")

    def _dados_de(self, **campos):
        valores = {
            "nome": "Nome Corrigido",
            "email": "sec@uea.edu.br",
            "curso_vinculado": curso(SI).pk,
        }
        valores.update(campos)
        return valores

    def test_cenario_37_corrigir_o_nome(self):
        resposta = self.client.post(editar(self.secretaria), self._dados_de(), follow=True)
        self.assertContains(resposta, mensagens.DADOS_ATUALIZADOS)
        self.secretaria.refresh_from_db()
        self.assertEqual(self.secretaria.usu_nome, "Nome Corrigido")

    def test_cenario_38_curso_vinculado_ja_ocupado(self):
        secretaria_de(EC)
        resposta = self.client.post(
            editar(self.secretaria), self._dados_de(curso_vinculado=curso(EC).pk)
        )
        self.assertContains(resposta, mensagens.CURSO_JA_TEM_SECRETARIA)
        self.secretaria.secretarios.refresh_from_db()
        self.assertEqual(self.secretaria.secretarios.sec_cur, curso(SI))

    def test_cenario_40_secretaria_nao_edita(self):
        self.client.force_login(secretaria_de(EC))
        resposta = self.client.get(LISTA, {"curso": "todos"})
        self.assertNotContains(resposta, editar(self.secretaria))
        resposta = self.client.get(editar(self.secretaria))
        self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)

    def test_coordenador_de_outro_curso_nao_edita(self):
        self.client.force_login(coordenador_de(EC))
        resposta = self.client.get(editar(self.secretaria))
        self.assertContains(resposta, mensagens.SO_DO_SEU_CURSO_CADASTRO, status_code=403)

    def test_lista_mostra_colunas_e_filtro(self):
        resposta = self.client.get(LISTA)
        for coluna in ("Nome", "E-mail Institucional", "Curso Vinculado", "Status da Conta"):
            self.assertContains(resposta, coluna)
        self.assertContains(resposta, "sec@uea.edu.br")
        self.assertContains(resposta, editar(self.secretaria))
