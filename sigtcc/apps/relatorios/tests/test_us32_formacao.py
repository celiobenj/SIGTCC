"""US-32: Formação e evasão (cenários 3.1 a 3.8 e 3.10).

[US-32][RBN-REL-02.3][RBN-CAD-05.4][RBN-CAD-05.6][RBN-CAD-08.7][FR-041][FR-042][FR-043][Q-02]
[SC-001][SC-002][SC-003] (tasks T035, T036 e T039)
"""

import csv
from io import StringIO

from django.db import connection
from django.http import QueryDict
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro.choices import DescricaoTurma, StatusTCC
from sigtcc.apps.cadastro.models import AlunosTurmas, HistoricoStatusTCC, TCCs
from sigtcc.apps.cadastro.tests.apoio_contas import coordenador_de, docente_de
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, LC, SI, criar_aluno_novo, criar_turma_de
from sigtcc.apps.relatorios import registro, services_relatorios
from sigtcc.apps.relatorios.forms import FiltroRelatorioForm
from sigtcc.apps.relatorios.tests.apoio_relatorios import (
    TesteRelatorios,
    aluno_com_status,
    registrar_status,
)

ID = "formacao-evasao"
COLUNAS = ("matriculados", "sem_proposta", "ativos", "com_sucesso", "sem_sucesso")


class TesteFormacao(TesteRelatorios):
    """Turma de Engenharia de Computação de 2026/2."""

    def setUp(self):
        super().setUp()
        self.coordenador = coordenador_de(EC)
        self.professor = docente_de(EC)
        self.turma = criar_turma_de(self.professor, ano=2026, semestre=2)
        self.url = reverse("relatorios:relatorio", args=[ID])

    def consulta(self, texto="ano_semestre=2026-2"):
        form = FiltroRelatorioForm(
            QueryDict(texto), usuario=self.coordenador, registrado=registro.obter(ID)
        )
        self.assertTrue(form.is_valid(), form.errors)
        return services_relatorios.formacao_evasao(self.coordenador, form.filtros())

    def valores(self, relatorio, curso=EC):
        linha = next(item for item in relatorio.linhas if item.valores["curso"] == curso)
        return tuple(linha.valores[chave] for chave in COLUNAS)

    def test_cenario_1_consulta_e_csv(self):
        """3.1: 12 alunos, e o CSV com as colunas da US."""
        for _ in range(2):
            aluno_com_status(self.turma, StatusTCC.SEM_PROPOSTA)
        for _ in range(9):
            aluno_com_status(self.turma)
        aluno_com_status(self.turma, StatusTCC.CONCLUIDO)
        self.client.force_login(self.coordenador)
        resposta = self.client.get(self.url + "?ano_semestre=2026-2")
        self.assertEqual(self.valores(resposta.context["relatorio"]), (12, 2, 9, 1, 0))
        arquivo = self.client.get(reverse("relatorios:exportar", args=[ID, "csv"]))
        linhas = list(csv.reader(StringIO(arquivo.content.decode("utf-8-sig")), delimiter=";"))
        self.assertIn(
            ["Curso", "Matriculados", "Sem Proposta", "Ativos", "Com Sucesso", "Sem Sucesso"],
            linhas,
        )
        self.assertIn([EC, "12", "2", "9", "1", "0"], linhas)

    def test_cenario_2_soma_igual_a_matriculados(self):
        """3.2 e SC-002: em toda linha e no Total, com os 10 Status."""
        for status in StatusTCC.values:
            aluno_com_status(self.turma, status)
        relatorio = self.consulta("curso=todos")
        for linha in (*relatorio.linhas, *relatorio.totais):
            matriculados, *partes = (linha.valores[chave] for chave in COLUNAS)
            self.assertEqual(matriculados, sum(partes))
        self.assertEqual(relatorio.totais[0].valores["matriculados"], 10)

    def test_cenario_3_aprovado_sem_versao_final_e_ativo(self):
        """3.3: conta em Ativos, e não em Com Sucesso."""
        turma2 = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2)
        aluno_com_status(turma2, StatusTCC.APROVADO)
        self.assertEqual(self.valores(self.consulta()), (1, 0, 1, 0, 0))

    def test_cenario_4_periodo_anterior_pelo_historico(self):
        """3.4: Aprovado para TCC 2 em 2026/1 e Em Andamento em 2026/2."""
        passada = criar_turma_de(self.professor, ano=2026, semestre=1)
        tcc1 = aluno_com_status(passada, StatusTCC.APROVADO_PARA_TCC_2)
        turma2 = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2)
        aluno_com_status(turma2, aluno=tcc1.tcc_alu)
        self.assertEqual(self.valores(self.consulta("ano_semestre=2026-1")), (1, 0, 0, 1, 0))
        self.assertEqual(self.valores(self.consulta("ano_semestre=2026-2")), (1, 0, 1, 0, 0))

    def test_cenario_5_curso_todos(self):
        """3.5: uma linha por curso do NUCOMP e a linha Total."""
        aluno_com_status(self.turma)
        aluno_com_status(criar_turma_de(self.professor, curso_nome=SI))
        relatorio = self.consulta("curso=todos")
        self.assertEqual([item.valores["curso"] for item in relatorio.linhas], sorted([EC, SI, LC]))
        self.assertEqual(self.valores(relatorio, LC), (0, 0, 0, 0, 0))
        self.assertEqual(relatorio.totais[0].valores["matriculados"], 2)

    def test_cenario_6_login(self):
        """3.6: sem sessão, login e retorno ao relatório."""
        self.assertIn(f"next={self.url}", self.client.get(self.url)["Location"])

    def test_cenario_7_sem_dados(self):
        """3.7: mensagem exata e botões desabilitados."""
        self.client.force_login(self.coordenador)
        resposta = self.client.get(self.url)
        self.assertContains(resposta, "Nenhum registro encontrado para os filtros selecionados")
        self.assertContains(resposta, "disabled", count=3)

    def test_cenario_10_transferido_sem_registro_na_destino(self):
        """3.10: conta uma vez, na turma de destino, e a soma fecha."""
        tcc = aluno_com_status(self.turma)
        destino = criar_turma_de(self.professor, ano=2026, semestre=2)
        AlunosTurmas.objects.filter(mat_alu=tcc.tcc_alu, mat_tur=self.turma).delete()
        AlunosTurmas.objects.create(
            mat_alu=tcc.tcc_alu, mat_tur=destino, mat_data_inscricao=timezone.now()
        )
        TCCs.objects.filter(pk=tcc.pk).update(tcc_tur=destino)
        self.assertFalse(HistoricoStatusTCC.objects.filter(hst_tur=destino).exists())
        self.assertEqual(self.valores(self.consulta()), (1, 0, 1, 0, 0))

    def test_vinculo_sem_tcc_e_sem_proposta(self):
        """FR-041: sem TCC, conta como Sem Proposta e a soma fecha."""
        AlunosTurmas.objects.create(
            mat_alu=criar_aluno_novo(), mat_tur=self.turma, mat_data_inscricao=timezone.now()
        )
        self.assertEqual(self.valores(self.consulta()), (1, 1, 0, 0, 0))

    def test_dois_vinculos_no_periodo(self):
        """FR-042: um Matriculado por vínculo, cada um com o seu TCC."""
        tcc = aluno_com_status(self.turma, StatusTCC.REPROVADO)
        outra = criar_turma_de(self.professor, ano=2026, semestre=2)
        aluno_com_status(outra, aluno=tcc.tcc_alu)
        self.assertEqual(self.valores(self.consulta()), (2, 0, 1, 0, 1))

    def test_excluido_nao_conta(self):
        """FR-043: o aluno excluído não tem vínculo."""
        tcc = aluno_com_status(self.turma, StatusTCC.SEM_PROPOSTA)
        aluno_com_status(self.turma)
        HistoricoStatusTCC.objects.filter(hst_tcc=tcc).delete()
        AlunosTurmas.objects.filter(mat_alu=tcc.tcc_alu).delete()
        TCCs.objects.filter(pk=tcc.pk).delete()
        self.assertEqual(self.valores(self.consulta()), (1, 0, 1, 0, 0))

    def test_desistente_com_proposta_fica_em_sem_sucesso(self):
        """FR-043 e Q-02: continua em Matriculados."""
        tcc = aluno_com_status(self.turma)
        registrar_status(tcc, StatusTCC.DESISTENTE)
        self.assertEqual(self.valores(self.consulta()), (1, 0, 0, 0, 1))

    def test_ultimo_registro_igual_ao_status(self):
        """SC-003: confere com o histórico."""
        for status in (StatusTCC.APTO_PARA_DEFESA, StatusTCC.JUBILADO, StatusTCC.CONCLUIDO):
            tcc = aluno_com_status(self.turma, status)
            ultimo = HistoricoStatusTCC.objects.filter(hst_tcc=tcc).order_by(
                "-hst_data_hora", "-hst_id"
            )[0]
            self.assertEqual(ultimo.hst_status_novo, tcc.tcc_status)
        self.assertEqual(self.valores(self.consulta()), (3, 0, 1, 1, 1))

    def test_kpis_grafico_e_ajuda(self):
        """FR-072: 4 KPIs, barra 100% e a explicação dos cartões."""
        aluno_com_status(self.turma, StatusTCC.SEM_PROPOSTA)
        aluno_com_status(self.turma)
        relatorio = self.consulta("curso=todos")
        self.assertEqual(
            [kpi.rotulo for kpi in relatorio.kpis],
            ["Matriculados", "Ativos", "Com Sucesso", "Sem Sucesso"],
        )
        self.assertEqual(relatorio.grafico.tipo, "empilhado")
        self.assertIn(f"{EC}: 50% Sem Proposta, 50% Ativos", relatorio.grafico.resumo)
        self.assertIn(f"{LC}: sem alunos", relatorio.grafico.resumo)
        self.client.force_login(self.coordenador)
        resposta = self.client.get(self.url)
        self.assertContains(resposta, "width: 50.00%")

    def test_sem_consulta_por_linha(self):
        """SC-001: sem depender do volume."""

        def medir():
            form = FiltroRelatorioForm(
                QueryDict("curso=todos"), usuario=self.coordenador, registrado=registro.obter(ID)
            )
            self.assertTrue(form.is_valid())
            filtros = form.filtros()
            with CaptureQueriesContext(connection) as contexto:
                services_relatorios.formacao_evasao(self.coordenador, filtros)
            return len(contexto)

        aluno_com_status(self.turma)
        antes = medir()
        for _ in range(10):
            aluno_com_status(self.turma)
        self.assertEqual(medir(), antes)
