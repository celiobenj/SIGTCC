"""US-34: Aluno e orientador, apoio à matrícula (cenários 1 a 7) e a decisão C6 da spec 011.

[US-34][RBN-REL-03.3][RBN-CAD-08.3][RBN-CAD-08.7][RBN-CAD-14.1][FR-030] (tasks T030)
"""

import csv
import io

from django.http import QueryDict
from django.urls import reverse

from sigtcc.apps.cadastro.choices import DescricaoTurma, StatusTCC
from sigtcc.apps.cadastro.tests.apoio_contas import coordenador_de, docente_de, secretaria_de
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, LC, SI, criar_turma_de, curso
from sigtcc.apps.relatorios import registro, services_operacionais
from sigtcc.apps.relatorios.forms import FiltroRelatorioForm
from sigtcc.apps.relatorios.tests.apoio_relatorios import TesteRelatorios, aluno_com_status

ID = "aluno-orientador"


class TesteAlunoOrientador(TesteRelatorios):
    """Turma de TCC 1 de Engenharia de Computação de 2026/2."""

    def setUp(self):
        super().setUp()
        self.secretaria = secretaria_de(EC)
        self.professor = docente_de(EC)
        self.orientador = docente_de(EC)
        self.orientador.usu_nome = "Orientadora"
        self.orientador.save()
        self.turma = criar_turma_de(self.professor)
        self.url = reverse("relatorios:relatorio", args=[ID])

    def consulta(self, texto="ano_semestre=2026-2", usuario=None):
        usuario = usuario or self.secretaria
        form = FiltroRelatorioForm(QueryDict(texto), usuario=usuario, registrado=registro.obter(ID))
        self.assertTrue(form.is_valid(), form.errors)
        return services_operacionais.aluno_orientador(usuario, form.filtros())

    def alunos(self, relatorio):
        return [linha.valores["aluno"] for linha in relatorio.linhas]

    def test_cenario_1_aprovados_primeiro_e_csv(self):
        """2 Aprovados para TCC 2 no topo, destacados, depois os 5 Em Andamento; CSV igual."""
        for nome in ("Ana", "Bruno", "Carla", "Diego", "Eva"):
            aluno_com_status(self.turma, StatusTCC.EM_ANDAMENTO, nome=nome)
        for nome in ("Zeca", "Yara"):
            aluno_com_status(
                self.turma, StatusTCC.APROVADO_PARA_TCC_2, orientador=self.orientador, nome=nome
            )
        self.client.force_login(self.secretaria)
        relatorio = self.client.get(self.url + "?ano_semestre=2026-2").context["relatorio"]
        ordem = ["Yara", "Zeca", "Ana", "Bruno", "Carla", "Diego", "Eva"]
        self.assertEqual(self.alunos(relatorio), ordem)
        self.assertEqual([linha.destaque for linha in relatorio.linhas], [True] * 2 + [False] * 5)
        self.assertEqual(
            [c.rotulo for c in relatorio.colunas],
            ["Matrícula", "Nome do Aluno", "Orientador", "Status do TCC"],
        )
        self.assertEqual(relatorio.linhas[0].valores["orientador"], "Orientadora")
        arquivo = self.client.get(
            reverse("relatorios:exportar", args=[ID, "csv"]) + "?ano_semestre=2026-2"
        )
        texto = arquivo.content.decode("utf-8-sig")
        nomes = [
            linha[1] for linha in csv.reader(io.StringIO(texto), delimiter=";") if len(linha) > 1
        ]
        self.assertEqual([nome for nome in nomes if nome in ordem], ordem)

    def test_cenario_2_coordenador(self):
        """O filtro Curso aparece preenchido com Licenciatura em Computação."""
        self.client.force_login(coordenador_de(LC))
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.context["form"]["curso"].value(), str(curso(LC).pk))

    def test_cenario_3_professor_so_periodo_letivo(self):
        """Só o Período letivo, sem Curso, e só os alunos das turmas dele (C1)."""
        aluno_com_status(self.turma, nome="Meu")
        aluno_com_status(criar_turma_de(docente_de(EC)), nome="Alheio")
        self.client.force_login(self.professor)
        resposta = self.client.get(self.url)
        campos = resposta.context["form"].fields
        self.assertNotIn("curso", campos)
        self.assertNotIn("atalho", campos)
        self.assertEqual(campos["ano_semestre"].label, "Período letivo")
        self.assertEqual(self.alunos(resposta.context["relatorio"]), ["Meu"])

    def test_cenario_4_curso_todos(self):
        """Alunos de todos os cursos do NUCOMP."""
        aluno_com_status(self.turma, nome="EC")
        aluno_com_status(criar_turma_de(docente_de(SI), curso_nome=SI), nome="SI")
        self.assertEqual(self.alunos(self.consulta()), ["EC"])
        self.assertEqual(self.alunos(self.consulta("curso=todos")), ["EC", "SI"])

    def test_cenario_5_login(self):
        """Sem sessão, a tela de login e o retorno ao relatório."""
        self.assertIn(f"next={self.url}", self.client.get(self.url)["Location"])

    def test_cenario_6_sem_dados(self):
        """Mensagem exata e botões desabilitados."""
        self.client.force_login(self.secretaria)
        resposta = self.client.get(self.url)
        self.assertContains(resposta, "Nenhum registro encontrado para os filtros selecionados")
        self.assertContains(resposta, "disabled", count=3)

    def test_cenario_7_docente_comum_nao_ve(self):
        """O item não aparece na lista."""
        self.client.force_login(docente_de(EC))
        lista = self.client.get(reverse("relatorios:lista")).context["lista"]
        self.assertNotIn(ID, [item.id for item in lista])

    def test_ja_matriculado_em_tcc_2_continua_aprovado(self):
        """Quem já foi para TCC 2 continua Aprovado para TCC 2 no período de origem (CAD-08.7)."""
        tcc = aluno_com_status(self.turma, StatusTCC.APROVADO_PARA_TCC_2, nome="Transferido")
        turma2 = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2)
        aluno_com_status(turma2, aluno=tcc.tcc_alu)  # novo TCC na turma de TCC 2
        linha = self.consulta().linhas[0]
        self.assertEqual(linha.valores["status"], "Aprovado para TCC 2")
        self.assertTrue(linha.destaque)

    def test_c6_so_turmas_de_tcc_1_e_sem_orientador(self):
        """Turmas de TCC 2 não entram; sem orientação, "Sem orientador" (C6)."""
        aluno_com_status(self.turma, nome="TCC1")
        aluno_com_status(criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2), nome="T2")
        relatorio = self.consulta()
        self.assertEqual(self.alunos(relatorio), ["TCC1"])
        self.assertEqual(relatorio.linhas[0].valores["orientador"], "Sem orientador")
