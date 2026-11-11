"""US-35: Horas complementares de ouvintes (cenários 1 a 9) e a decisão C8 da spec 011.

[US-35][RBN-REL-03.4][RBN-DEF-08.2][RBN-DEF-01.5][RBN-CAD-14.1][FR-040] (tasks T040)
"""

from datetime import date
from io import BytesIO

from django.http import QueryDict
from django.urls import reverse
from openpyxl import load_workbook

from sigtcc.apps.cadastro.choices import StatusTCC
from sigtcc.apps.cadastro.tests.apoio_contas import coordenador_de, docente_de, secretaria_de
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, SI, criar_turma_de
from sigtcc.apps.defesa.choices import StatusSessao
from sigtcc.apps.defesa.models import Defesas
from sigtcc.apps.defesa.services_defesa import intervalo_do_atalho
from sigtcc.apps.defesa.tests.apoio_documentos import ouvinte, presenca
from sigtcc.apps.relatorios import registro, services_operacionais
from sigtcc.apps.relatorios.forms import FiltroRelatorioForm
from sigtcc.apps.relatorios.tests.apoio_relatorios import (
    TesteRelatorios,
    aluno_com_status,
    banca_de,
    sessao_realizada,
)

ID = "horas-ouvintes"
MATRICULA = "2415080011"


class TesteHorasOuvintes(TesteRelatorios):
    """Turma de TCC 1 de Engenharia de Computação de 2026/2."""

    def setUp(self):
        super().setUp()
        self.secretaria = secretaria_de(EC)
        self.professor = docente_de(EC)
        self.turma = criar_turma_de(self.professor)
        self.url = reverse("relatorios:relatorio", args=[ID])

    def consulta(self, texto="ano_semestre=2026-2", usuario=None):
        usuario = usuario or self.secretaria
        form = FiltroRelatorioForm(QueryDict(texto), usuario=usuario, registrado=registro.obter(ID))
        self.assertTrue(form.is_valid(), form.errors)
        return services_operacionais.horas_ouvintes(usuario, form.filtros())

    def sessao(self, data=None, turma=None):
        tcc = aluno_com_status(turma or self.turma, StatusTCC.APROVADO_PARA_TCC_2)
        return sessao_realizada(tcc, banca_de(self.professor, docente_de(EC), docente_de(EC)), data)

    def linhas(self, relatorio):
        return [
            (linha.valores["matricula"], linha.valores["data"], linha.valores["horas"])
            for linha in relatorio.linhas
        ]

    def test_cenario_1_tres_sessoes_tres_linhas_e_xlsx(self):
        """3 linhas do ouvinte, 2 horas cada, e o total; XLSX com as mesmas linhas."""
        registro_ouvinte = ouvinte(MATRICULA, "Ouvinte Assíduo")
        for dia in (18, 19, 20):
            presenca(self.sessao(date(2026, 11, dia)), registro_ouvinte)
        self.client.force_login(self.secretaria)
        relatorio = self.client.get(self.url + "?ano_semestre=2026-2").context["relatorio"]
        self.assertEqual(
            self.linhas(relatorio),
            [(MATRICULA, f"{dia}/11/2026", 2) for dia in (18, 19, 20)],
        )
        self.assertEqual(relatorio.totais[0].valores["horas"], 6)
        self.assertEqual(relatorio.totais[0].valores["ouvinte"], "Total")
        arquivo = self.client.get(
            reverse("relatorios:exportar", args=[ID, "xlsx"]) + "?ano_semestre=2026-2"
        )
        valores = [
            [c.value for c in linha]
            for linha in load_workbook(BytesIO(arquivo.content)).worksheets[0].iter_rows()
        ]
        self.assertIn(["Nome do Ouvinte", "Matrícula", "Data da Defesa", "Horas"], valores)
        self.assertEqual(sum(1 for linha in valores if MATRICULA in linha), 3)
        self.assertIn(["Total", None, None, 6], valores)

    def test_cenario_2_sessao_cancelada_nao_conta(self):
        """A presença numa sessão depois Cancelada não aparece."""
        sessao = self.sessao()
        presenca(sessao, ouvinte(MATRICULA))
        Defesas.objects.filter(pk=sessao.pk).update(def_status=StatusSessao.CANCELADA)
        self.assertEqual(self.consulta().linhas, ())

    def test_cenario_3_periodo_por_datas(self):
        """Considera apenas o intervalo informado."""
        presenca(self.sessao(date(2026, 9, 10)), ouvinte(MATRICULA))
        presenca(self.sessao(date(2026, 10, 10)), ouvinte(MATRICULA))
        relatorio = self.consulta("data_inicial=2026-09-01&data_final=2026-09-30")
        self.assertEqual(self.linhas(relatorio), [(MATRICULA, "10/09/2026", 2)])

    def test_cenario_4_atalho_este_mes(self):
        """Preenche Data Inicial e Data Final com o primeiro e o último dia do mês."""
        self.client.force_login(self.secretaria)
        resposta = self.client.get(self.url + "?atalho=este_mes")
        inicio, fim = intervalo_do_atalho("este_mes")
        self.assertEqual(resposta.context["form"]["data_inicial"].value(), inicio.isoformat())
        self.assertEqual(resposta.context["form"]["data_final"].value(), fim.isoformat())

    def test_cenario_5_professor_sem_curso_e_so_as_suas_turmas(self):
        """Filtros de período sem o Curso e só as sessões das turmas dele (C1)."""
        presenca(self.sessao(), ouvinte(MATRICULA))
        presenca(self.sessao(turma=criar_turma_de(docente_de(EC))), ouvinte("2415080012"))
        self.client.force_login(self.professor)
        resposta = self.client.get(self.url)
        self.assertNotIn("curso", resposta.context["form"].fields)
        self.assertIn("atalho", resposta.context["form"].fields)
        self.assertEqual([m for m, _, _ in self.linhas(resposta.context["relatorio"])], [MATRICULA])

    def test_cenario_6_login(self):
        """Sem sessão, a tela de login e o retorno ao relatório."""
        self.assertIn(f"next={self.url}", self.client.get(self.url)["Location"])

    def test_cenario_7_datas_invertidas(self):
        """Não atualiza e exibe a mensagem exata."""
        self.client.force_login(self.secretaria)
        resposta = self.client.get(self.url + "?data_inicial=2026-11-30&data_final=2026-11-01")
        self.assertContains(resposta, "A data inicial não pode ser superior à data final")
        self.assertIsNone(resposta.context["relatorio"])

    def test_cenario_8_sem_dados(self):
        """Mensagem exata, botões desabilitados e sem linha de total."""
        self.client.force_login(self.secretaria)
        resposta = self.client.get(self.url)
        self.assertContains(resposta, "Nenhum registro encontrado para os filtros selecionados")
        self.assertContains(resposta, "disabled", count=3)
        self.assertEqual(resposta.context["relatorio"].totais, ())

    def test_cenario_9_docente_comum_nao_ve(self):
        """O item não aparece na lista."""
        self.client.force_login(docente_de(EC))
        lista = self.client.get(reverse("relatorios:lista")).context["lista"]
        self.assertNotIn(ID, [item.id for item in lista])

    def test_curso_coordenador_e_todos(self):
        """Curso da turma do TCC da sessão; o Coordenador de SI vê só SI, e Todos os dois."""
        presenca(self.sessao(), ouvinte(MATRICULA))
        presenca(self.sessao(turma=criar_turma_de(docente_de(SI), curso_nome=SI)), ouvinte())
        coordenador = coordenador_de(SI)
        self.assertEqual(len(self.consulta(usuario=coordenador).linhas), 1)
        self.assertEqual(len(self.consulta("curso=todos", usuario=coordenador).linhas), 2)
