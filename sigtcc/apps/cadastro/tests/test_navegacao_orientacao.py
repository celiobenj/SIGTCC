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


class NavegacaoProfessorTest(TesteTurmas):
    """Professor: menu "Turmas" → turma → bloco → painel → ação (?volta=painel) → painel;
    histórico → "Fechar" → painel; "Fechar" do painel → aba "Alunos". [US-41][FR-044][T030]
    """

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=SI)
        self.aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        self.client.force_login(self.professor)

    def painel(self):
        painel = self.client.get(reverse("cadastro:painel"))
        turmas = seguir(self, painel, reverse("cadastro:turmas"))
        turma = seguir(self, turmas, reverse("cadastro:turma", args=[self.turma.pk]))
        return seguir(
            self, turma, reverse("cadastro:painel_aluno", args=[self.turma.pk, self.aluno.pk])
        )

    def test_do_menu_ao_painel_e_volta(self):
        painel = self.painel()
        self.assertContains(painel, "Proposta e TCC")
        aba = seguir(self, painel, reverse("cadastro:turma", args=[self.turma.pk]))
        self.assertContains(aba, 'class="bloco"')

    def test_acao_do_painel_cancelar_volta_ao_painel(self):
        painel = self.painel()
        encerrar = seguir(
            self, painel, reverse("cadastro:aluno_encerrar", args=[self.turma.pk, self.aluno.pk])
        )
        voltou = seguir(
            self, encerrar, reverse("cadastro:painel_aluno", args=[self.turma.pk, self.aluno.pk])
        )
        self.assertContains(voltou, "Proposta e TCC")

    def test_historico_fechar_volta_ao_painel(self):
        painel = self.painel()
        historico = seguir(
            self, painel, reverse("cadastro:historico_status", args=[self.turma.pk, self.aluno.pk])
        )
        voltou = seguir(
            self, historico, reverse("cadastro:painel_aluno", args=[self.turma.pk, self.aluno.pk])
        )
        self.assertContains(voltou, "Proposta e TCC")


class NavegacaoAtasTest(TesteTurmas):
    """Atas pelas três entradas: aba Meu TCC, linha da tela de orientandos e painel; cada
    janela e lista volta à tela de origem. [US-19][FR-042][FR-043][FR-044][T036]
    """

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=SI)
        self.aluno = matricular_aluno(
            self.turma, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        )
        self.tcc = tcc_de(self.aluno, self.turma)
        self.orientador = criar_docente_ativo()
        vincular_orientador(self.tcc, self.orientador)

    def test_aluno_secao_registrar_e_ver_atas(self):
        self.client.force_login(self.aluno.alu)
        meu_tcc = self.client.get(reverse("cadastro:meu_tcc", args=[self.turma.pk]))
        self.assertContains(meu_tcc, 'id="atas"')
        janela = seguir(
            self, meu_tcc, reverse("cadastro:registrar_ata_aluno", args=[self.turma.pk])
        )
        self.assertContains(janela, "Registrar ata de orientação")
        voltou = seguir(self, janela, reverse("cadastro:meu_tcc", args=[self.turma.pk]))
        self.assertEqual(voltou.status_code, 200)
        lista = seguir(self, meu_tcc, reverse("cadastro:minhas_atas", args=[self.turma.pk]))
        seguir(self, lista, reverse("cadastro:meu_tcc", args=[self.turma.pk]))

    def test_orientador_linha_atas_e_voltar(self):
        self.client.force_login(self.orientador)
        tela = self.client.get(reverse("cadastro:orientacoes"))
        lista = seguir(self, tela, reverse("cadastro:atas_orientando", args=[self.tcc.pk]))
        voltou = seguir(self, lista, reverse("cadastro:orientacoes"))
        self.assertContains(voltou, "Orientandos")
        janela = seguir(self, tela, reverse("cadastro:registrar_ata_docente", args=[self.tcc.pk]))
        seguir(self, janela, reverse("cadastro:orientacoes"))

    def test_professor_painel_ver_atas_e_voltar(self):
        self.client.force_login(self.professor)
        painel = self.client.get(
            reverse("cadastro:painel_aluno", args=[self.turma.pk, self.aluno.pk])
        )
        lista = seguir(
            self, painel, reverse("cadastro:atas_painel", args=[self.turma.pk, self.aluno.pk])
        )
        voltou = seguir(
            self, lista, reverse("cadastro:painel_aluno", args=[self.turma.pk, self.aluno.pk])
        )
        self.assertContains(voltou, "Proposta e TCC")
