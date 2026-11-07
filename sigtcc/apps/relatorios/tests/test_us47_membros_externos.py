"""US-47: Participação de Membros Externos (cenários 5.1 a 5.9).

[US-47][RBN-REL-01.2][RBN-DEF-01.5][RBN-CAD-14.1][FR-030][FR-031][SC-001] (tasks T043 e T046)
"""

from datetime import date
from io import BytesIO

from django.db import connection
from django.http import QueryDict
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from openpyxl import load_workbook

from sigtcc.apps.cadastro.choices import DescricaoTurma
from sigtcc.apps.cadastro.tests.apoio_contas import (
    coordenador_de,
    docente_de,
    membro,
    secretaria_de,
)
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, SI, criar_turma_de, curso
from sigtcc.apps.defesa.choices import PapelBanca, StatusSessao
from sigtcc.apps.defesa.services_defesa import intervalo_do_atalho
from sigtcc.apps.relatorios import registro, services_relatorios
from sigtcc.apps.relatorios.forms import FiltroRelatorioForm
from sigtcc.apps.relatorios.tests.apoio_relatorios import (
    TesteRelatorios,
    aluno_com_status,
    banca_de,
    sessao_realizada,
)

ID = "membros-externos"
UFAM = "Universidade Federal do Amazonas"


class TesteMembros(TesteRelatorios):
    """Turma de TCC 2 de Engenharia de Computação de 2026/2."""

    def setUp(self):
        super().setUp()
        self.coordenador = coordenador_de(EC)
        self.professor = docente_de(EC)
        self.turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2)
        self.url = reverse("relatorios:relatorio", args=[ID])

    def consulta(self, texto="ano_semestre=2026-2", usuario=None):
        usuario = usuario or self.coordenador
        form = FiltroRelatorioForm(QueryDict(texto), usuario=usuario, registrado=registro.obter(ID))
        self.assertTrue(form.is_valid(), form.errors)
        return services_relatorios.membros_externos(usuario, form.filtros())

    def tabela(self, relatorio):
        return [
            (item.valores["descricao"], item.valores["quantidade"]) for item in relatorio.linhas
        ]

    def sessao(self, *membros, data=None, turma=None):
        return sessao_realizada(aluno_com_status(turma or self.turma), banca_de(*membros), data)

    def test_cenario_1_consulta_e_xlsx(self):
        """5.1: 4 docentes, 1 externo e a instituição, e o XLSX com Descrição e Quantidade."""
        externo = membro(instituicao=UFAM)
        d1, d2, d3, d4 = (docente_de(EC) for _ in range(4))
        self.sessao(d1, d2, d3)
        self.sessao(d4, d2, externo)
        self.client.force_login(self.coordenador)
        resposta = self.client.get(self.url + "?ano_semestre=2026-2")
        self.assertEqual(
            self.tabela(resposta.context["relatorio"]),
            [
                ("Docentes do NUCOMP", 4),
                ("Membros Externos", 1),
                (f"Instituição de origem: {UFAM}", 1),
            ],
        )
        arquivo = self.client.get(
            reverse("relatorios:exportar", args=[ID, "xlsx"]) + "?ano_semestre=2026-2"
        )
        valores = [
            [celula.value for celula in linha]
            for linha in load_workbook(BytesIO(arquivo.content)).worksheets[0].iter_rows()
        ]
        self.assertIn(["Descrição", "Quantidade"], valores)
        self.assertIn(["Docentes do NUCOMP", 4], valores)

    def test_cenario_2_periodo_por_datas(self):
        """5.2: considera apenas o intervalo informado."""
        dentro, fora = membro(), membro()
        d1, d2 = docente_de(EC), docente_de(EC)
        self.sessao(d1, d2, dentro, data=date(2026, 9, 10))
        self.sessao(d1, d2, fora, data=date(2026, 10, 10))
        relatorio = self.consulta("data_inicial=2026-09-01&data_final=2026-09-30")
        self.assertEqual(self.tabela(relatorio)[1], ("Membros Externos", 1))

    def test_cenario_3_atalho_este_mes(self):
        """5.3: preenche as datas e atualiza."""
        self.client.force_login(self.coordenador)
        resposta = self.client.get(self.url + "?atalho=este_mes")
        inicio, fim = intervalo_do_atalho("este_mes")
        self.assertEqual(resposta.context["form"]["data_inicial"].value(), inicio.isoformat())
        self.assertEqual(resposta.context["form"]["data_final"].value(), fim.isoformat())

    def test_cenario_4_curso_todos(self):
        """5.4: sessões de todos os cursos; o Curso é o da turma do TCC."""
        turma_si = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=SI)
        self.sessao(docente_de(EC), docente_de(EC), membro())
        self.sessao(docente_de(EC), docente_de(EC), membro(), turma=turma_si)
        self.assertEqual(self.tabela(self.consulta())[1], ("Membros Externos", 1))
        self.assertEqual(self.tabela(self.consulta("curso=todos"))[1], ("Membros Externos", 2))

    def test_cenario_5_secretaria_com_o_curso_vinculado(self):
        """5.5: filtro preenchido, e ela pode escolher Todos (P4)."""
        secretaria = secretaria_de(EC)
        self.client.force_login(secretaria)
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.context["form"]["curso"].value(), str(curso(EC).pk))
        self.sessao(docente_de(EC), docente_de(EC), membro())
        self.assertEqual(self.client.get(self.url + "?curso=todos").context["filtros"].cur_id, None)

    def test_cenario_6_login(self):
        """5.6: sem sessão, login e retorno ao relatório."""
        self.assertIn(f"next={self.url}", self.client.get(self.url)["Location"])

    def test_cenario_7_datas_invertidas(self):
        """5.7: não atualiza e exibe a mensagem exata."""
        self.client.force_login(self.coordenador)
        resposta = self.client.get(self.url + "?data_inicial=2026-11-30&data_final=2026-11-01")
        self.assertContains(resposta, "A data inicial não pode ser superior à data final")
        self.assertIsNone(resposta.context["relatorio"])

    def test_cenario_8_sem_dados(self):
        """5.8: mensagem exata e botões desabilitados."""
        self.client.force_login(self.coordenador)
        resposta = self.client.get(self.url)
        self.assertContains(resposta, "Nenhum registro encontrado para os filtros selecionados")
        self.assertContains(resposta, "disabled", count=3)

    def test_cenario_9_docente_comum_nao_ve(self):
        """5.9: o item não aparece na lista."""
        self.client.force_login(docente_de(EC))
        lista = self.client.get(reverse("relatorios:lista")).context["lista"]
        self.assertNotIn(ID, [item.id for item in lista])

    def test_pessoas_distintas(self):
        """FR-030: quem participou de 3 bancas conta 1."""
        externo = membro()
        d1, d2 = docente_de(EC), docente_de(EC)
        for _ in range(3):
            self.sessao(d1, d2, externo)
        self.assertEqual(
            self.tabela(self.consulta())[:2],
            [("Docentes do NUCOMP", 2), ("Membros Externos", 1)],
        )

    def test_suplente(self):
        """FR-030: o acionado conta; o não acionado, não."""
        acionado, reserva, titular = membro(), membro(instituicao="UEA"), membro()
        tcc = aluno_com_status(self.turma)
        sessao_realizada(
            tcc,
            [
                (docente_de(EC), PapelBanca.ORIENTADOR_PRESIDENTE),
                (docente_de(EC), PapelBanca.PRIMEIRO_AVALIADOR),
                (acionado, PapelBanca.SEGUNDO_AVALIADOR, titular),
                (reserva, PapelBanca.SUPLENTE),
            ],
        )
        self.assertEqual(
            self.tabela(self.consulta())[1:],
            [("Membros Externos", 1), (f"Instituição de origem: {UFAM}", 1)],
        )

    def test_so_sessoes_realizadas(self):
        """FR-030: outro status não conta."""
        sessao = self.sessao(docente_de(EC), docente_de(EC), membro())
        sessao.def_status = StatusSessao.AGENDADA
        sessao.save()
        self.assertFalse(self.consulta().tem_registros)

    def test_instituicoes_e_grafias(self):
        """Edge Case: cada grafia é uma linha, da maior quantidade para a menor."""
        d1, d2 = docente_de(EC), docente_de(EC)
        for instituicao in ("UEA", "UFAM", "UFAM"):
            self.sessao(d1, d2, membro(instituicao=instituicao))
        self.sessao(d1, d2, membro(instituicao="Universidade Federal do Amazonas"))
        self.assertEqual(
            self.tabela(self.consulta())[2:],
            [
                ("Instituição de origem: UFAM", 2),
                ("Instituição de origem: UEA", 1),
                (f"Instituição de origem: {UFAM}", 1),
            ],
        )

    def test_kpis_e_grafico_em_roxo(self):
        """FR-072 e FR-073: 2 KPIs e barras em `--roxo`, com o valor escrito."""
        self.sessao(docente_de(EC), docente_de(EC), membro())
        relatorio = self.consulta()
        self.assertEqual([kpi.rotulo for kpi in relatorio.kpis][1], "Membros Externos")
        self.assertEqual(relatorio.grafico.dados[0]["cor"], "roxo")
        self.client.force_login(self.coordenador)
        self.assertContains(self.client.get(self.url), "cor-roxo")

    def test_sem_externos_sem_grafico(self):
        """FR-072: sem instituição, sem gráfico."""
        self.sessao(docente_de(EC), docente_de(EC), docente_de(EC))
        relatorio = self.consulta()
        self.assertTrue(relatorio.tem_registros)
        self.assertIsNone(relatorio.grafico)

    def test_sem_consulta_por_linha(self):
        """SC-001: sem depender do número de sessões."""

        def medir():
            form = FiltroRelatorioForm(
                QueryDict(""), usuario=self.coordenador, registrado=registro.obter(ID)
            )
            self.assertTrue(form.is_valid())
            filtros = form.filtros()
            with CaptureQueriesContext(connection) as contexto:
                services_relatorios.membros_externos(self.coordenador, filtros)
            return len(contexto)

        self.sessao(docente_de(EC), docente_de(EC), membro())
        antes = medir()
        for numero in range(6):
            self.sessao(docente_de(EC), docente_de(EC), membro(instituicao=f"Instituição {numero}"))
        self.assertEqual(medir(), antes)
