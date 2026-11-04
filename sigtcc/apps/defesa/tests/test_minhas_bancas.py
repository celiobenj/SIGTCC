"""Minhas bancas (User Story 2 da spec 008): cenários 2.1 a 2.8, MA-12 e número fixo de
consultas.

[US-25][RBN-DEF-05.4][RBN-DEF-08.3][FR-003 a FR-006] (tasks T018)
"""

from decimal import Decimal
from unittest import mock

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from sigtcc.apps.cadastro.choices import TipoEntrega
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_membro_externo
from sigtcc.apps.cadastro.tests.apoio_tcc import cadastrar_entrega, enviar_link
from sigtcc.apps.defesa import services_avaliacoes, services_defesa
from sigtcc.apps.defesa.choices import PapelBanca, StatusSessao
from sigtcc.apps.defesa.tests.apoio_avaliacao import (
    TesteAvaliacao,
    criterios,
    lancar,
    lancar_e_enviar,
    sessao_com_banca,
)
from sigtcc.apps.defesa.tests.apoio_defesa import (
    agendar_sessao_de,
    avancar_para,
    docente,
    tcc_apto,
)

MINHAS_BANCAS = reverse("defesa:minhas_bancas")


class TesteMinhasBancas(TesteAvaliacao):
    """Cenários 2.1 a 2.8. [US-25][RBN-DEF-05.4][FR-003 a FR-006]"""

    def setUp(self):
        super().setUp()
        self.membro = docente()
        self.sessoes = {}
        for status in (
            StatusSessao.AGENDADA,
            StatusSessao.EM_ANDAMENTO,
            StatusSessao.REALIZADA,
            StatusSessao.CANCELADA,
        ):
            tcc, _professor, orientador = tcc_apto()
            sessao = agendar_sessao_de(
                tcc, orientador, {"primeiro_avaliador": self.membro, "segundo_avaliador": docente()}
            )
            self.sessoes[status] = avancar_para(sessao, status)

    def linhas(self, usuario=None):
        return services_avaliacoes.minhas_bancas(usuario or self.membro)

    def test_cenario_2_1_sem_as_canceladas_com_papel_data_e_status(self):
        self.client.force_login(self.membro)
        resposta = self.client.get(MINHAS_BANCAS)
        self.assertEqual(resposta.status_code, 200)
        vistas = [linha["sessao"] for linha in self.linhas()]
        self.assertEqual(
            {sessao.def_status for sessao in vistas},
            {StatusSessao.AGENDADA, StatusSessao.EM_ANDAMENTO, StatusSessao.REALIZADA},
        )
        self.assertNotIn(self.sessoes[StatusSessao.CANCELADA], vistas)
        self.assertContains(resposta, "1º Avaliador")
        self.assertContains(resposta, "20/11/2026")
        self.assertContains(resposta, "14:00")
        self.assertNotContains(resposta, "Cancelada")

    def test_cenario_2_2_pendencias_em_destaque_com_os_atalhos(self):
        em_andamento = self.sessoes[StatusSessao.EM_ANDAMENTO]
        tcc = em_andamento.def_tcc
        entrega = cadastrar_entrega(tcc.tcc_tur, tipo=TipoEntrega.DOCUMENTO_PARA_DEFESA)
        enviar_link(entrega, tcc.tcc_alu, "https://drive.example.org/documento")
        lancar(em_andamento, self.membro, Decimal("7.0"), criterios_lancados=criterios()[:3])
        por_sessao = {linha["sessao"]: linha for linha in self.linhas()}
        self.assertTrue(por_sessao[self.sessoes[StatusSessao.AGENDADA]]["pendente"])
        self.assertTrue(por_sessao[em_andamento]["pendente"])
        self.assertEqual(por_sessao[em_andamento]["estado"], "Rascunho salvo")
        self.assertFalse(por_sessao[self.sessoes[StatusSessao.REALIZADA]]["pendente"])
        self.assertEqual(
            por_sessao[em_andamento]["documento"], "https://drive.example.org/documento"
        )
        self.client.force_login(self.membro)
        resposta = self.client.get(MINHAS_BANCAS)
        self.assertContains(resposta, 'class="pendente"', count=2)
        self.assertContains(resposta, "https://drive.example.org/documento")
        self.assertContains(resposta, reverse("defesa:criterios"))
        self.assertContains(resposta, "Avaliar")

    def test_avaliacao_enviada_sai_do_destaque(self):
        em_andamento = self.sessoes[StatusSessao.EM_ANDAMENTO]
        lancar_e_enviar(em_andamento, self.membro, Decimal("8.0"))
        por_sessao = {linha["sessao"]: linha for linha in self.linhas()}
        self.assertFalse(por_sessao[em_andamento]["pendente"])
        self.assertEqual(por_sessao[em_andamento]["estado"], "Enviada")

    def test_cenario_2_3_membro_externo_ve_so_as_suas(self):
        externo = criar_membro_externo()
        tcc, _professor, orientador = tcc_apto()
        sua = agendar_sessao_de(
            tcc, orientador, {"primeiro_avaliador": externo, "segundo_avaliador": docente()}
        )
        self.assertEqual([linha["sessao"] for linha in self.linhas(externo)], [sua])
        self.client.force_login(externo)
        resposta = self.client.get(MINHAS_BANCAS)
        self.assertContains(resposta, tcc.tcc_alu.alu.usu_nome)
        for outra in self.sessoes.values():
            self.assertNotContains(resposta, outra.def_tcc.tcc_alu.alu.usu_nome)

    def test_cenario_2_4_suplente_acionado_com_avaliar(self):
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        services_defesa.acionar_suplente(
            cenario["orientador"],
            cenario["sessao"].pk,
            PapelBanca.SEGUNDO_AVALIADOR,
            "Não compareceu",
        )
        linha = self.linhas(cenario["suplente"])[0]
        self.assertEqual(linha["papel"], PapelBanca.SEGUNDO_AVALIADOR)
        self.assertTrue(linha["membro_efetivo"])
        self.assertTrue(linha["pendente"])
        self.client.force_login(cenario["suplente"])
        resposta = self.client.get(MINHAS_BANCAS)
        self.assertContains(resposta, "Avaliar")
        self.assertContains(resposta, reverse("defesa:avaliacao", args=[cenario["sessao"].pk]))

    def test_cenario_2_5_suplente_nao_acionado_sem_avaliar(self):
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        linha = self.linhas(cenario["suplente"])[0]
        self.assertEqual(linha["papel"], PapelBanca.SUPLENTE)
        self.assertFalse(linha["membro_efetivo"])
        self.assertFalse(linha["pendente"])
        self.client.force_login(cenario["suplente"])
        resposta = self.client.get(MINHAS_BANCAS)
        self.assertContains(resposta, "Suplente")
        self.assertNotContains(resposta, "Avaliar")

    def test_cenario_2_6_declaracao_so_quando_a_feat_09_informa(self):
        realizada = self.sessoes[StatusSessao.REALIZADA]
        self.client.force_login(self.membro)
        self.assertNotContains(self.client.get(MINHAS_BANCAS), "Declaração")
        with mock.patch(
            "sigtcc.apps.defesa.services_documentos.declaracao_disponivel",
            side_effect=lambda sessao, usuario: sessao == realizada,
        ):
            resposta = self.client.get(MINHAS_BANCAS)
        self.assertContains(resposta, "Declaração", count=1)

    def test_cenario_2_7_sem_login_vai_ao_login_e_volta(self):
        resposta = self.client.get(MINHAS_BANCAS)
        self.assertRedirects(
            resposta,
            f"{reverse('cadastro:entrar')}?next={MINHAS_BANCAS}",
            fetch_redirect_response=False,
        )

    def test_cenario_2_8_linha_abre_a_sessao_de_defesa(self):
        self.client.force_login(self.membro)
        resposta = self.client.get(MINHAS_BANCAS)
        for status in (StatusSessao.AGENDADA, StatusSessao.EM_ANDAMENTO):
            self.assertContains(resposta, reverse("defesa:sessao", args=[self.sessoes[status].pk]))
        url = reverse("defesa:sessao", args=[self.sessoes[StatusSessao.AGENDADA].pk])
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_ma12_sem_bancas(self):
        self.client.force_login(docente())
        self.assertContains(
            self.client.get(MINHAS_BANCAS), "Você não participa de nenhuma banca no momento"
        )

    def test_item_de_menu_para_docente_e_membro_externo(self):
        for usuario in (self.membro, criar_membro_externo()):
            with self.subTest(usuario=usuario.usu_email):
                self.client.force_login(usuario)
                self.assertContains(self.client.get(MINHAS_BANCAS), f'href="{MINHAS_BANCAS}"')

    def test_numero_fixo_de_consultas(self):
        def consultas():
            with CaptureQueriesContext(connection) as contexto:
                self.linhas()
            return len(contexto)

        antes = consultas()
        for _ in range(3):
            tcc, _professor, orientador = tcc_apto()
            agendar_sessao_de(
                tcc, orientador, {"primeiro_avaliador": self.membro, "segundo_avaliador": docente()}
            )
        self.assertEqual(consultas(), antes)
