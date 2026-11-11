"""Visual do protótipo de 17/10 nas telas da Defesa, só com as classes do sigtcc.css: chip do
Status da sessão com a cor de corStatus e "Agendar defesa" no botão flutuante (.fab) só para quem
agenda. Só aparência: as regras continuam nos testes de cada US.

[US-21][US-24][US-25][US-40][RBN-DEF-01.2][RBN-DEF-01.4]
"""

from django.test import SimpleTestCase
from django.urls import reverse

from sigtcc.apps.cadastro.choices import StatusConta
from sigtcc.apps.cadastro.tests.apoio_turmas import TesteTurmas
from sigtcc.apps.defesa.choices import StatusSessao
from sigtcc.apps.defesa.templatetags.defesa_tags import cor_status_sessao
from sigtcc.apps.defesa.tests.apoio_defesa import (
    agendar_sessao_de,
    avancar_para,
    docente,
    tcc_apto,
)

FAB = 'class="fab"'


class CorStatusSessaoTest(SimpleTestCase):
    """Filtro cor_status_sessao (chipStatus do protótipo)."""

    def test_cada_status_tem_a_cor_do_prototipo(self):
        esperado = {
            StatusSessao.AGENDADA: "azul",
            StatusSessao.REAGENDADA: "azul",
            StatusSessao.EM_ANDAMENTO: "amarelo",
            StatusSessao.REALIZADA: "verde",
            StatusSessao.CANCELADA: "vermelho",
        }
        for status, cor in esperado.items():
            with self.subTest(status=status):
                self.assertEqual(cor_status_sessao(status), cor)
        self.assertEqual(len(esperado), len(StatusSessao.choices))
        self.assertEqual(cor_status_sessao("Outro"), "")


class TelasDaDefesaTest(TesteTurmas):
    """Tela Defesas e Minhas bancas."""

    def test_agendar_defesa_no_fab_so_para_quem_agenda(self):
        tcc, _professor, orientador = tcc_apto()
        self.client.force_login(orientador)
        resposta = self.client.get(reverse("defesa:defesas"))
        self.assertContains(resposta, FAB, count=1)
        self.assertContains(resposta, "Agendar defesa")
        aluno = tcc.tcc_alu.alu
        aluno.usu_status = StatusConta.ATIVA
        aluno.save(update_fields=["usu_status"])
        self.client.force_login(aluno)
        self.assertNotContains(self.client.get(reverse("defesa:defesas")), FAB)

    def test_minhas_bancas_com_chip_colorido(self):
        tcc, _professor, _orientador = tcc_apto()
        avaliador = docente()
        sessao = agendar_sessao_de(
            tcc, banca={"primeiro_avaliador": avaliador, "segundo_avaliador": docente()}
        )
        self.client.force_login(avaliador)
        resposta = self.client.get(reverse("defesa:minhas_bancas"))
        self.assertContains(resposta, '<span class="chip azul">Agendada</span>', html=True)
        avancar_para(sessao, StatusSessao.EM_ANDAMENTO)
        resposta = self.client.get(reverse("defesa:minhas_bancas"))
        self.assertContains(resposta, '<span class="chip amarelo">Em Andamento</span>', html=True)
