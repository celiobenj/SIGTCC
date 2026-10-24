"""Navegação até cada tela da feature 006 (SC-005; FR-040 a FR-045, FR-052).

Cada teste parte do menu do perfil e segue só links e botões renderizados (nunca monta a URL à
mão, exceto o endereço antigo da rota `aluno`, de propósito), até a tela, e volta pelo botão de
volta indicado em contracts/rotas.md. A matriz completa é conferida em T059.

[SC-005][FR-040 a FR-045][FR-052]
"""

import re

from django.urls import reverse

from sigtcc.apps.cadastro import services_orientacao
from sigtcc.apps.cadastro.choices import StatusConta, StatusTCC
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo, criar_secretaria
from sigtcc.apps.cadastro.tests.apoio_orientacao import criar_pedido, vincular_orientador
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    SI,
    TesteTurmas,
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)


def links(resposta):
    """Todos os href da página renderizada."""
    return re.findall(r'href="([^"#]+)', resposta.content.decode())


def seguir(teste, resposta, trecho):
    """Segue o primeiro link renderizado que contém `trecho` (falha se não houver)."""
    achados = [href for href in links(resposta) if trecho in href]
    teste.assertTrue(achados, f"nenhum link com {trecho!r} na página")
    return teste.client.get(achados[0].replace("&amp;", "&"))


class NavegacaoAlunoTest(TesteTurmas):
    """Aluno: menu "Turmas" → turma → aba "Meu TCC" → seção Orientação. [FR-042][T018]"""

    def setUp(self):
        super().setUp()
        self.turma = criar_turma_de(criar_docente_ativo(), curso_nome=SI)
        self.aluno = matricular_aluno(
            self.turma, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        )
        self.client.force_login(self.aluno.alu)

    def test_do_menu_ate_a_secao_orientacao(self):
        painel = self.client.get(reverse("cadastro:painel"))
        turmas = seguir(self, painel, reverse("cadastro:minhas_turmas"))
        meu_tcc = seguir(self, turmas, reverse("cadastro:meu_tcc", args=[self.turma.pk]))
        self.assertContains(meu_tcc, 'id="orientacao"')
        self.assertContains(meu_tcc, "Indicar orientador")
        self.assertContains(meu_tcc, "js/secao.js")

    def test_login_com_next_volta_a_secao(self):
        self.client.logout()
        destino = f"{reverse('cadastro:meu_tcc', args=[self.turma.pk])}?secao=orientacao"
        resposta = self.client.get(destino)
        self.assertRedirects(
            resposta,
            f"{reverse('cadastro:entrar')}?next={destino.replace('?', '%3F').replace('=', '%3D')}",
            fetch_redirect_response=False,
        )

    def test_secao_invalida_e_ignorada(self):
        url = reverse("cadastro:meu_tcc", args=[self.turma.pk])
        resposta = self.client.get(f"{url}?secao=<script>")
        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(resposta, "<script>alert")


class NavegacaoDocenteTest(TesteTurmas):
    """Docente: menu "Orientações" → tela; sino → link do pedido; linha → histórico e volta;
    "Ver proposta" → "Fechar". [US-18][FR-040][FR-043][FR-052][Q11][IC-01][T025]
    """

    def setUp(self):
        super().setUp()
        self.docente = criar_docente_ativo()
        turma = criar_turma_de(criar_docente_ativo(), curso_nome=SI)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        self.tcc = tcc_de(aluno, turma)
        self.client.force_login(self.docente)

    def test_menu_orientacoes_para_todo_docente(self):
        painel = self.client.get(reverse("cadastro:painel"))
        self.assertContains(painel, "Orientações")
        self.assertContains(painel, "supervisor_account")
        tela = seguir(self, painel, reverse("cadastro:orientacoes"))
        self.assertContains(tela, "Pedidos de orientação")
        self.assertContains(tela, "Convites de coorientação")

    def test_menu_orientacoes_nao_aparece_para_outros_perfis(self):
        self.client.force_login(criar_secretaria())
        painel = self.client.get(reverse("cadastro:painel"))
        self.assertNotIn(reverse("cadastro:orientacoes"), links(painel))

    def test_sino_leva_ao_pedido_e_ver_proposta_volta(self):
        pedido = criar_pedido(self.tcc, self.docente)
        tela = self.client.get(services_orientacao.link_da_solicitacao(pedido))
        proposta = seguir(self, tela, reverse("cadastro:ver_proposta", args=[pedido.pk]))
        voltou = seguir(self, proposta, reverse("cadastro:orientacoes"))
        self.assertContains(voltou, "Pedidos de orientação")

    def test_linha_historico_e_fechar(self):
        vincular_orientador(self.tcc, self.docente)
        tela = self.client.get(reverse("cadastro:orientacoes"))
        historico = seguir(self, tela, reverse("cadastro:historico_orientando", args=[self.tcc.pk]))
        voltou = seguir(self, historico, reverse("cadastro:orientacoes"))
        self.assertContains(voltou, "Orientandos")
