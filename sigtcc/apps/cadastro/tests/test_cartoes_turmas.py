"""Turmas em cartões (protótipo de 17/10, tela "Turmas"): grade nas telas Turmas e Turmas
arquivadas (Professor e Secretaria) e Turmas do Aluno, banner pelo curso, quantidade de alunos no
rodapé e o botão flutuante "Nova turma" só para quem pode criar turma.

[US-07][US-13][RBN-CAD-04.2][RBN-CAD-04.5][FR-010][FR-031]
"""

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from sigtcc.apps.cadastro.choices import StatusConta, StatusTurma
from sigtcc.apps.cadastro.templatetags.turmas_tags import CORES, banner_turma, cor_avatar
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo, criar_secretaria
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    LC,
    SI,
    TesteTurmas,
    criar_turma_de,
    curso,
    matricular_aluno,
)

FAB = 'class="fab"'
CARTAO = 'class="card-turma"'


class BannerTurmaTest(TesteTurmas):
    """Filtros banner_turma (motivoBanner) e cor_avatar (corDe) do protótipo."""

    def test_cada_curso_tem_cor_e_motivo_proprios(self):
        estilos = {nome: banner_turma(nome) for nome in (EC, SI, LC)}
        self.assertIn(f"background-color:{CORES[0]}", estilos[EC])
        self.assertIn(f"background-color:{CORES[1]}", estilos[SI])
        self.assertIn(f"background-color:{CORES[2]}", estilos[LC])
        for estilo in estilos.values():
            self.assertIn("background-image:url('data:image/svg+xml,%3Csvg", estilo)
        self.assertEqual(len(set(estilos.values())), 3)

    def test_curso_fora_da_lista_tem_cor_fixa_sem_motivo(self):
        estilo = banner_turma("Outro Curso")
        self.assertEqual(estilo, banner_turma("Outro Curso"))
        self.assertNotIn("background-image", estilo)
        self.assertIn(estilo.removeprefix("background-color:"), CORES)

    def test_texto_do_curso_nunca_entra_no_estilo(self):
        self.assertNotIn("<script>", banner_turma('<script>"'))

    def test_cor_do_avatar_igual_ao_cor_de_do_prototipo(self):
        # corDe("Ana") no protótipo: (65*31 + 110)*31 + 97 = 65972, e 65972 % 8 = 4.
        self.assertEqual(cor_avatar("Ana"), CORES[4])
        self.assertEqual(cor_avatar("Ana"), cor_avatar("Ana"))


class GradeDeTurmasTest(TesteTurmas):
    """Telas Turmas e Turmas arquivadas do Professor da Disciplina e da Secretaria."""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=SI)
        matricular_aluno(self.turma)
        matricular_aluno(self.turma)

    def test_professor_ve_cartoes_com_banner_contagem_e_link(self):
        self.client.force_login(self.professor)
        resposta = self.client.get(reverse("cadastro:turmas"))
        self.assertContains(resposta, CARTAO, count=1)
        self.assertNotContains(resposta, 'class="tabela"')
        self.assertContains(resposta, f'href="{reverse("cadastro:turma", args=[self.turma.pk])}"')
        self.assertContains(resposta, banner_turma(SI))
        self.assertContains(
            resposta, f"{self.turma.tur_descricao} · {self.turma.tur_identificador}"
        )
        self.assertContains(resposta, self.professor.usu_nome)
        self.assertContains(resposta, "2 alunos")
        self.assertContains(resposta, self.turma.tur_dis.dis_codigo)

    def test_botao_flutuante_nova_turma_so_para_o_docente(self):
        self.client.force_login(self.professor)
        resposta = self.client.get(reverse("cadastro:turmas"))
        self.assertContains(resposta, FAB, count=1)
        self.assertContains(resposta, "Nova turma")
        self.assertContains(resposta, reverse("cadastro:turma_nova"))
        self.client.force_login(criar_secretaria(curso=curso(SI)))
        resposta = self.client.get(reverse("cadastro:turmas"))
        self.assertContains(resposta, CARTAO, count=1)
        self.assertNotContains(resposta, FAB)
        self.assertNotContains(resposta, reverse("cadastro:turma_nova"))

    def test_arquivadas_em_cartoes_com_etiqueta_e_sem_botao(self):
        arquivada = criar_turma_de(self.professor, status=StatusTurma.ARQUIVADA)
        self.client.force_login(self.professor)
        resposta = self.client.get(reverse("cadastro:turmas_arquivadas"))
        self.assertContains(resposta, CARTAO, count=1)
        self.assertContains(resposta, arquivada.tur_identificador)
        self.assertContains(resposta, '<span class="chip">Arquivada</span>', html=True)
        self.assertContains(resposta, "0 aluno")
        self.assertNotContains(resposta, FAB)

    def test_sem_turmas_mostra_o_vazio(self):
        self.client.force_login(criar_docente_ativo())
        resposta = self.client.get(reverse("cadastro:turmas"))
        self.assertNotContains(resposta, CARTAO)
        self.assertContains(resposta, "Nenhuma turma.")

    def test_consultas_nao_crescem_com_as_turmas(self):
        self.client.force_login(self.professor)
        with CaptureQueriesContext(connection) as uma:
            self.client.get(reverse("cadastro:turmas"))
        for _ in range(3):
            matricular_aluno(criar_turma_de(self.professor, curso_nome=LC))
        with CaptureQueriesContext(connection) as quatro:
            self.client.get(reverse("cadastro:turmas"))
        self.assertEqual(len(uma), len(quatro))


class TurmasDoAlunoTest(TesteTurmas):
    """Item "Turmas" do Aluno: cartões que abrem "Meu TCC", nunca a tela da turma."""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=LC)
        self.aluno = matricular_aluno(self.turma, status_conta=StatusConta.ATIVA)
        matricular_aluno(self.turma)
        self.client.force_login(self.aluno.alu)

    def test_cartao_abre_meu_tcc(self):
        resposta = self.client.get(reverse("cadastro:minhas_turmas"))
        self.assertContains(resposta, CARTAO, count=1)
        self.assertNotContains(resposta, 'class="tabela"')
        self.assertContains(resposta, f'href="{reverse("cadastro:meu_tcc", args=[self.turma.pk])}"')
        self.assertNotContains(resposta, reverse("cadastro:turma", args=[self.turma.pk]) + '"')
        self.assertContains(resposta, banner_turma(LC))
        self.assertContains(resposta, "2 alunos")
        self.assertNotContains(resposta, FAB)

    def test_arquivadas_do_aluno_em_cartoes(self):
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save(update_fields=["tur_status"])
        resposta = self.client.get(reverse("cadastro:minhas_turmas_arquivadas"))
        self.assertContains(resposta, CARTAO, count=1)
        self.assertContains(resposta, '<span class="chip">Arquivada</span>', html=True)
