"""Testes de aceite da US-41: ver os alunos da turma e o painel de cada aluno (spec 006, User
Story 3).

Cenários 1 a 7 da US-41 e os pontos de contato #8 (Secretaria) e #9 (Encerrar participação volta
ao painel), mais: aluno sem vínculo (404), permissões (FR-020), turma arquivada sem botões nem
reset (FR-019), ?volta= com outro valor ignorado, redirecionamentos de erro com volta=painel
(IC-03) e consultas constantes (R14).

[US-41][US-08 C e D][US-09][US-12][US-44][RBN-CAD-08.9][RBN-CAD-10.5][FR-017 a FR-020][FR-044]
(tasks T026)
"""

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    StatusConta,
    StatusTCC,
    StatusTurma,
    TipoEntrega,
)
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo, criar_secretaria
from sigtcc.apps.cadastro.tests.apoio_orientacao import vincular_orientador
from sigtcc.apps.cadastro.tests.apoio_tcc import cadastrar_entrega, enviar_link
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    SI,
    TesteTurmas,
    criar_turma_de,
    curso,
    entrega_do_aluno,
    matricular_aluno,
    tcc_de,
)


class PainelTestBase(TesteTurmas):
    """Turma de TCC 1 de SI com 3 alunos: com orientador, sem orientador e sem Proposta."""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=SI)
        self.com_orientador = matricular_aluno(
            self.turma, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        )
        self.orientador = criar_docente_ativo()
        vincular_orientador(tcc_de(self.com_orientador, self.turma), self.orientador)
        self.sem_orientador = matricular_aluno(self.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        self.sem_proposta = matricular_aluno(self.turma, status_tcc=StatusTCC.SEM_PROPOSTA)
        self.client.force_login(self.professor)

    def aba(self):
        return self.client.get(reverse("cadastro:turma", args=[self.turma.pk]))

    def painel(self, aluno=None, turma=None):
        turma = turma or self.turma
        return self.client.get(
            reverse("cadastro:painel_aluno", args=[turma.pk, (aluno or self.com_orientador).pk])
        )


class PainelTest(PainelTestBase):
    """Cenários 1 a 7. [US-41][FR-017 a FR-020]"""

    def test_cenario1_blocos_e_painel_com_as_secoes(self):
        aba = self.aba()
        self.assertContains(aba, 'class="bloco"', count=3)
        resposta = self.painel()
        for secao in (
            "Proposta e TCC",
            "Orientação e coorientação",
            "Entregas",
            "Atas de orientação",
            "Defesa",
        ):
            self.assertContains(resposta, secao)
        self.assertContains(resposta, mensagens.MO23_SEM_DEFESA)
        self.assertContains(resposta, f'href="{reverse("cadastro:turma", args=[self.turma.pk])}"')

    def test_painel_tcc2_tem_versao_final(self):
        turma2 = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=SI)
        aluno = matricular_aluno(turma2, status_tcc=StatusTCC.EM_ANDAMENTO)
        entrega = cadastrar_entrega(turma2, tipo=TipoEntrega.VERSAO_FINAL)
        entrega_do_aluno(entrega, aluno)
        self.assertContains(self.painel(aluno, turma2), "Versão Final")

    def test_cenario2_sem_orientador(self):
        self.assertContains(self.aba(), mensagens.SEM_ORIENTADOR)

    def test_cenario3_sem_proposta(self):
        self.assertContains(self.aba(), mensagens.SEM_PROPOSTA)

    def test_cenario4_encerrar_participacao_pelo_painel(self):
        resposta = self.painel()
        url = reverse("cadastro:aluno_encerrar", args=[self.turma.pk, self.com_orientador.pk])
        self.assertContains(resposta, f"{url}?volta=painel")
        self.assertEqual(self.client.get(f"{url}?volta=painel").status_code, 200)

    def test_cenario5_turma_arquivada_sem_botoes(self):
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save()
        resposta = self.painel()
        self.assertEqual(resposta.status_code, 200)
        for botao in ("Editar aluno", "Encerrar participação", "Excluir aluno", "Transferir aluno"):
            self.assertNotContains(resposta, botao)
        self.assertNotContains(resposta, mensagens.RESETAR_PRIMEIRO_ACESSO)
        self.assertContains(resposta, "Histórico do Status do TCC")

    def test_cenario6_sem_sessao_vai_ao_login(self):
        self.client.logout()
        resposta = self.aba()
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("cadastro:entrar"), resposta.url)

    def test_cenario7_outro_docente_nao_ve(self):
        self.client.force_login(criar_docente_ativo())
        self.assertEqual(self.aba().status_code, 403)
        self.assertEqual(self.painel().status_code, 403)

    def test_fr020_secretaria_e_aluno_recebem_403_no_painel(self):
        self.client.force_login(criar_secretaria(curso=curso(SI)))
        self.assertEqual(self.painel().status_code, 403)
        self.client.force_login(self.com_orientador.alu)
        self.assertEqual(self.painel().status_code, 403)

    def test_aluno_sem_vinculo_404(self):
        outra = criar_turma_de(criar_docente_ativo(), curso_nome=SI)
        estranho = matricular_aluno(outra, status_tcc=StatusTCC.EM_ANDAMENTO)
        self.assertEqual(self.painel(estranho).status_code, 404)

    def test_botoes_de_acao_conforme_a_regra_de_cada_spec(self):
        resposta = self.painel(self.sem_proposta)
        self.assertContains(resposta, "Excluir aluno")
        self.assertNotContains(resposta, "Encerrar participação")
        resposta = self.painel(self.com_orientador)
        self.assertContains(resposta, "Encerrar participação")
        self.assertContains(resposta, "Editar aluno")
        self.assertContains(resposta, mensagens.RESETAR_PRIMEIRO_ACESSO)

    def test_consultas_constantes_aba_e_painel_r14(self):
        with CaptureQueriesContext(connection) as tres:
            self.aba()
        for _ in range(7):
            matricular_aluno(self.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        with CaptureQueriesContext(connection) as dez:
            self.aba()
        self.assertEqual(len(tres.captured_queries), len(dez.captured_queries))
        aluno = self.com_orientador
        entrega = cadastrar_entrega(self.turma)
        enviar_link(entrega, aluno, "https://drive.example/1")
        with CaptureQueriesContext(connection) as uma:
            self.painel(aluno)
        for _ in range(4):
            enviar_link(cadastrar_entrega(self.turma), aluno, "https://drive.example/2")
        with CaptureQueriesContext(connection) as cinco:
            self.painel(aluno)
        self.assertEqual(len(uma.captured_queries), len(cinco.captured_queries))


class VoltaAoPainelTest(PainelTestBase):
    """Ponto #9 e IC-03/IC-07: as telas de ação voltam ao painel. [FR-044][research R5]"""

    def url(self, rota, aluno=None, volta="?volta=painel"):
        aluno = aluno or self.com_orientador
        return reverse(f"cadastro:{rota}", args=[self.turma.pk, aluno.pk]) + volta

    def destino_painel(self, aluno=None):
        return reverse(
            "cadastro:painel_aluno", args=[self.turma.pk, (aluno or self.com_orientador).pk]
        )

    def test_ponto9_encerrar_confirma_e_volta_ao_painel(self):
        resposta = self.client.post(
            self.url("aluno_encerrar"),
            {"status": StatusTCC.DESISTENTE, "justificativa": "Desistiu"},
        )
        self.assertRedirects(resposta, self.destino_painel(), fetch_redirect_response=False)

    def test_ponto9_encerrar_cancelar_volta_ao_painel(self):
        resposta = self.client.get(self.url("aluno_encerrar"))
        self.assertContains(resposta, f'href="{self.destino_painel()}"')

    def test_editar_volta_ao_painel(self):
        resposta = self.client.post(
            self.url("aluno_editar"), {"nome": "Nome Novo Teste", "curso": "EST08MCPD"}
        )
        self.assertRedirects(resposta, self.destino_painel(), fetch_redirect_response=False)

    def test_sem_volta_comportamento_atual(self):
        resposta = self.client.post(
            self.url("aluno_editar", volta=""), {"nome": "Nome Novo Teste", "curso": "EST08MCPD"}
        )
        self.assertRedirects(
            resposta,
            reverse("cadastro:turma", args=[self.turma.pk]),
            fetch_redirect_response=False,
        )

    def test_volta_com_outro_valor_e_ignorada(self):
        resposta = self.client.post(
            self.url("aluno_editar", volta="?volta=https://malicioso.example"),
            {"nome": "Nome Novo Teste", "curso": "EST08MCPD"},
        )
        self.assertRedirects(
            resposta,
            reverse("cadastro:turma", args=[self.turma.pk]),
            fetch_redirect_response=False,
        )

    def test_excluir_com_proposta_erro_volta_ao_painel(self):
        resposta = self.client.get(self.url("aluno_excluir"))
        self.assertRedirects(resposta, self.destino_painel(), fetch_redirect_response=False)

    def test_excluir_confirmado_volta_a_aba_alunos(self):
        aluno = self.sem_proposta
        resposta = self.client.post(
            self.url("aluno_excluir", aluno),
            {"justificativa": "Vínculo por engano", "confirmacao_final": "1"},
        )
        self.assertRedirects(
            resposta,
            reverse("cadastro:turma", args=[self.turma.pk]),
            fetch_redirect_response=False,
        )

    def test_turma_arquivada_volta_ao_painel_com_mt25(self):
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save()
        resposta = self.client.get(self.url("aluno_editar"), follow=True)
        self.assertContains(resposta, mensagens.MT25_TURMA_ARQUIVADA)
        self.assertEqual(resposta.redirect_chain[-1][0], self.destino_painel())

    def test_endereco_antigo_leva_ao_painel(self):
        resposta = self.client.get(reverse("cadastro:aluno", args=[self.com_orientador.pk]))
        self.assertRedirects(resposta, self.destino_painel(), fetch_redirect_response=False)


class SecretariaTest(TesteTurmas):
    """Ponto #8: Secretaria vê os blocos sem painel e com "Transferir aluno". [Q4][RBN-CAD-05.6]"""

    def test_ponto8_secretaria_blocos_sem_painel_com_transferir(self):
        professor = criar_docente_ativo()
        turma = criar_turma_de(professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        criar_turma_de(criar_docente_ativo(), descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        self.client.force_login(criar_secretaria(curso=curso(EC)))
        resposta = self.client.get(reverse("cadastro:turma", args=[turma.pk]))
        self.assertContains(resposta, 'class="bloco"')
        painel = reverse("cadastro:painel_aluno", args=[turma.pk, aluno.pk])
        self.assertNotContains(resposta, f'href="{painel}"')
        self.assertContains(
            resposta, reverse("cadastro:aluno_transferir", args=[turma.pk, aluno.pk])
        )
        self.assertContains(resposta, "Transferir aluno")
