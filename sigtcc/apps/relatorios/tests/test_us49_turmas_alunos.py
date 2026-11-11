"""US-49: Turmas e alunos (cenários 1 a 8), o Status pelo histórico (CAD-08.7) e a decisão C7.

[US-49][RBN-REL-03.2][RBN-CAD-08.3][RBN-CAD-08.7][RBN-CAD-14.1][FR-020] (tasks T020)
"""

from datetime import timedelta
from io import BytesIO

from django.http import QueryDict
from django.urls import reverse
from django.utils import timezone
from openpyxl import load_workbook

from sigtcc.apps.cadastro.choices import DescricaoTurma, StatusTCC
from sigtcc.apps.cadastro.tests.apoio_contas import coordenador_de, docente_de, secretaria_de
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, SI, criar_turma_de, curso
from sigtcc.apps.relatorios import registro, services_operacionais
from sigtcc.apps.relatorios.forms import FiltroRelatorioForm
from sigtcc.apps.relatorios.tests.apoio_relatorios import (
    TesteRelatorios,
    aluno_com_status,
    registrar_status,
)

ID = "turmas-alunos"


class TesteTurmasAlunos(TesteRelatorios):
    """Turma ECP07_T01 (TCC 1) de Engenharia de Computação de 2026/2."""

    def setUp(self):
        super().setUp()
        self.secretaria = secretaria_de(EC)
        self.professor = docente_de(EC)
        self.professor.usu_nome = "Prof. Turma"
        self.professor.save()
        self.turma = criar_turma_de(self.professor, identificador="ECP07_T01")
        self.url = reverse("relatorios:relatorio", args=[ID])

    def consulta(self, texto="ano_semestre=2026-2", usuario=None):
        usuario = usuario or self.secretaria
        form = FiltroRelatorioForm(QueryDict(texto), usuario=usuario, registrado=registro.obter(ID))
        self.assertTrue(form.is_valid(), form.errors)
        return services_operacionais.turmas_alunos(usuario, form.filtros())

    def turmas(self, relatorio):
        return [linha.valores["turma"] for linha in relatorio.linhas]

    def test_cenario_1_turma_com_7_alunos_e_xlsx(self):
        """7 alunos, 3 Sem Proposta: TCC 1, Professor, Total 7 e o Status de cada um; XLSX."""
        for numero in range(3):
            aluno_com_status(self.turma, StatusTCC.SEM_PROPOSTA, nome=f"Sem {numero}")
        for numero in range(4):
            aluno_com_status(self.turma, StatusTCC.EM_ANDAMENTO, nome=f"Com {numero}")
        self.client.force_login(self.secretaria)
        relatorio = self.client.get(self.url + "?ano_semestre=2026-2").context["relatorio"]
        linha = relatorio.linhas[0]
        self.assertEqual(
            linha.valores,
            {"turma": "ECP07_T01", "descricao": "TCC 1", "professor": "Prof. Turma", "total": 7},
        )
        status = [item.valores["status"] for item in linha.sublistas[0].linhas]
        self.assertEqual(status.count("Sem Proposta"), 3)
        self.assertEqual(status.count("Em Andamento"), 4)
        arquivo = self.client.get(
            reverse("relatorios:exportar", args=[ID, "xlsx"]) + "?ano_semestre=2026-2"
        )
        livro = load_workbook(BytesIO(arquivo.content))
        valores = [[c.value for c in linha] for linha in livro.worksheets[0].iter_rows()]
        self.assertIn(
            ["Turma", "TCC 1 ou TCC 2", "Professor da Disciplina", "Total de Alunos"], valores
        )
        self.assertIn(["ECP07_T01", "TCC 1", "Prof. Turma", 7], valores)
        alunos = [[c.value for c in linha] for linha in livro.worksheets[1].iter_rows()]
        self.assertEqual(sum(1 for linha in alunos if "Sem Proposta" in linha), 3)

    def test_cenario_2_desistente_destacado(self):
        """O Status Desistente aparece destacado; Em Andamento não."""
        aluno_com_status(self.turma, StatusTCC.DESISTENTE, nome="Desistente")
        aluno_com_status(self.turma, StatusTCC.EM_ANDAMENTO, nome="Normal")
        itens = self.consulta().linhas[0].sublistas[0].linhas
        destaques = {item.valores["aluno"]: item.destaque for item in itens}
        self.assertEqual(destaques, {"Desistente": True, "Normal": False})
        self.client.force_login(self.secretaria)
        self.assertContains(self.client.get(self.url), 'class="destaque"', count=1)

    def test_reprovado_e_jubilado_tambem(self):
        """Reprovado e Jubilado também são destacados (RBN-REL-03.2)."""
        for status in (StatusTCC.REPROVADO, StatusTCC.JUBILADO):
            aluno_com_status(self.turma, status)
        itens = self.consulta().linhas[0].sublistas[0].linhas
        self.assertTrue(all(item.destaque for item in itens))

    def test_cenario_3_coordenador(self):
        """O filtro Curso aparece preenchido com Engenharia de Computação."""
        self.client.force_login(coordenador_de(EC))
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.context["form"]["curso"].value(), str(curso(EC).pk))

    def test_cenario_4_professor_so_as_proprias_turmas(self):
        """Só ECP07_T01, sem o filtro Curso."""
        criar_turma_de(docente_de(SI), curso_nome=SI, identificador="SIN07_T01")
        self.client.force_login(self.professor)
        resposta = self.client.get(self.url)
        self.assertNotIn("curso", resposta.context["form"].fields)
        self.assertEqual(self.turmas(resposta.context["relatorio"]), ["ECP07_T01"])

    def test_cenario_5_curso_todos(self):
        """Turmas de todos os cursos do NUCOMP."""
        criar_turma_de(docente_de(SI), curso_nome=SI, identificador="SIN07_T01")
        self.assertEqual(self.turmas(self.consulta()), ["ECP07_T01"])
        self.assertEqual(self.turmas(self.consulta("curso=todos")), ["ECP07_T01", "SIN07_T01"])

    def test_cenario_6_login(self):
        """Sem sessão, a tela de login e o retorno ao relatório."""
        self.assertIn(f"next={self.url}", self.client.get(self.url)["Location"])

    def test_cenario_7_sem_dados(self):
        """Curso sem turma no período: mensagem exata e botões desabilitados."""
        self.client.force_login(secretaria_de(SI))
        resposta = self.client.get(self.url)
        self.assertContains(resposta, "Nenhum registro encontrado para os filtros selecionados")
        self.assertContains(resposta, "disabled", count=3)

    def test_cenario_8_docente_comum_nao_ve(self):
        """O item não aparece na lista."""
        self.client.force_login(docente_de(EC))
        lista = self.client.get(reverse("relatorios:lista")).context["lista"]
        self.assertNotIn(ID, [item.id for item in lista])

    def test_status_de_periodo_anterior_pelo_historico(self):
        """Turma de período anterior: o último Status registrado para aquela turma (CAD-08.7)."""
        antiga = criar_turma_de(self.professor, ano=2026, semestre=1, identificador="ECP07_A")
        ontem = timezone.now() - timedelta(days=1)
        tcc = aluno_com_status(antiga, StatusTCC.EM_ANDAMENTO, ontem, nome="Antigo")
        registrar_status(tcc, StatusTCC.APROVADO_PARA_TCC_2)
        nova = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, identificador="N")
        aluno_com_status(nova, StatusTCC.APROVADO, aluno=tcc.tcc_alu)  # novo TCC no TCC 2
        item = self.consulta("ano_semestre=2026-1").linhas[0].sublistas[0].linhas[0]
        self.assertEqual(item.valores["status"], "Aprovado para TCC 2")
        atual = {linha.valores["turma"]: linha for linha in self.consulta().linhas}["N"]
        self.assertEqual(atual.sublistas[0].linhas[0].valores["status"], "Aprovado")

    def test_turma_sem_aluno(self):
        """Turma sem aluno: Total 0 e "Nenhum registro" na sub-lista (C7)."""
        linha = self.consulta().linhas[0]
        self.assertEqual(linha.valores["total"], 0)
        self.assertEqual(linha.sublistas[0].linhas, ())
