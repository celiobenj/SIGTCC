"""US-33: Produção de TCCs (cenários 2.1 a 2.4 e 2.6 a 2.8).

[US-33][RBN-REL-02.1][RBN-CAD-08.3][RBN-CAD-08.7][FR-040][FR-041][FR-060][FR-061][FR-062][FR-063]
[FR-064][SC-001][SC-002] (tasks T028 e T034)
"""

import csv
from io import BytesIO, StringIO

from django.db import connection
from django.http import QueryDict
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from pypdf import PdfReader

from sigtcc.apps.cadastro.choices import ModalidadeTCC, StatusTCC
from sigtcc.apps.cadastro.models import AreasInteresse, TCCs
from sigtcc.apps.cadastro.tests.apoio_contas import coordenador_de, docente_de
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, LC, SI, criar_turma_de
from sigtcc.apps.relatorios import registro, services_relatorios
from sigtcc.apps.relatorios.forms import FiltroRelatorioForm
from sigtcc.apps.relatorios.services_relatorios import GRUPOS_DE_STATUS
from sigtcc.apps.relatorios.tests.apoio_relatorios import (
    TesteRelatorios,
    aluno_com_status,
    registrar_status,
)

ID = "producao-tccs"


class TesteProducao(TesteRelatorios):
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
        return services_relatorios.producao_tccs(self.coordenador, form.filtros())

    def linha(self, relatorio, grupo):
        return next(item for item in relatorio.linhas if item.valores["grupo"] == grupo)

    def valores(self, linha):
        return tuple(
            linha.valores[chave] for chave in ("total", "ativos", "com_sucesso", "sem_sucesso")
        )

    def povoar(self, ativos=9, concluidos=1):
        for _ in range(ativos):
            aluno_com_status(self.turma)
        for _ in range(concluidos):
            aluno_com_status(self.turma, StatusTCC.CONCLUIDO)

    def test_cenario_1_por_curso_e_pdf(self):
        """2.1: Total 10, Ativos 9, Com Sucesso 1 e Sem Sucesso 0, e o PDF com as colunas."""
        self.povoar()
        self.client.force_login(self.coordenador)
        resposta = self.client.get(self.url + "?agrupar_por=curso&ano_semestre=2026-2")
        relatorio = resposta.context["relatorio"]
        self.assertEqual(self.valores(self.linha(relatorio, EC)), (10, 9, 1, 0))
        arquivo = self.client.get(reverse("relatorios:exportar", args=[ID, "pdf"]))
        texto = " ".join(p.extract_text() for p in PdfReader(BytesIO(arquivo.content)).pages)
        for coluna in ("Total de Trabalhos", "Ativos", "Com Sucesso", "Sem Sucesso"):
            self.assertIn(coluna, texto)

    def test_cenario_2_area_de_interesse(self):
        """2.2: uma linha por área e o trabalho sem área em "Não informada"."""
        sem_area = aluno_com_status(self.turma)
        com_area = aluno_com_status(self.turma)
        area = AreasInteresse.objects.order_by("ari_nome").first()
        TCCs.objects.filter(pk=com_area.pk).update(tcc_ari=area)
        self.assertIsNone(sem_area.tcc_ari)
        relatorio = self.consulta("agrupar_por=area")
        self.assertEqual(len(relatorio.linhas), AreasInteresse.objects.count() + 1)
        self.assertEqual(self.linha(relatorio, "Não informada").valores["total"], 1)
        self.assertEqual(self.linha(relatorio, area.ari_nome).valores["total"], 1)

    def test_sem_trabalho_sem_area_nao_ha_nao_informada(self):
        """FR-062: a linha só aparece se houver."""
        tcc = aluno_com_status(self.turma)
        area = AreasInteresse.objects.first()
        TCCs.objects.filter(pk=tcc.pk).update(tcc_ari=area)
        relatorio = self.consulta("agrupar_por=area")
        self.assertEqual(len(relatorio.linhas), AreasInteresse.objects.count())

    def test_cenario_3_modalidade(self):
        """2.3: as linhas Monografia e Artigo Científico."""
        tcc = aluno_com_status(self.turma)
        TCCs.objects.filter(pk=tcc.pk).update(tcc_modalidade=ModalidadeTCC.ARTIGO_CIENTIFICO)
        relatorio = self.consulta("agrupar_por=modalidade")
        self.assertEqual(
            [item.valores["grupo"] for item in relatorio.linhas],
            ["Monografia", "Artigo Científico"],
        )
        self.assertEqual(self.linha(relatorio, "Monografia").valores["total"], 0)
        self.assertEqual(self.linha(relatorio, "Artigo Científico").valores["total"], 1)

    def test_cenario_4_apenas_concluidos(self):
        """2.4: só o trabalho Concluído."""
        self.povoar()
        relatorio = self.consulta("abrangencia=concluidos")
        self.assertEqual(self.valores(self.linha(relatorio, EC)), (1, 0, 1, 0))

    def test_todos_os_aprovados(self):
        """FR-063: Aprovado e Aprovado com Correções ficam em Ativos, sem quebrar a soma."""
        for status in (
            StatusTCC.APROVADO_PARA_TCC_2,
            StatusTCC.APROVADO,
            StatusTCC.APROVADO_COM_CORRECOES,
            StatusTCC.CONCLUIDO,
            StatusTCC.EM_ANDAMENTO,
            StatusTCC.REPROVADO,
        ):
            aluno_com_status(self.turma, status)
        relatorio = self.consulta("abrangencia=aprovados")
        self.assertEqual(self.valores(self.linha(relatorio, EC)), (4, 2, 2, 0))

    def test_cenario_6_curso_todos(self):
        """2.6: todos os cursos do NUCOMP, com zeros, e a linha Total."""
        aluno_com_status(self.turma)
        aluno_com_status(criar_turma_de(self.professor, curso_nome=SI))
        relatorio = self.consulta("curso=todos")
        self.assertEqual({item.valores["grupo"] for item in relatorio.linhas}, {EC, SI, LC})
        self.assertEqual(self.linha(relatorio, LC).valores["total"], 0)
        self.assertEqual(relatorio.totais[0].valores["total"], 2)

    def test_cenario_7_login(self):
        """2.7: sem sessão, login e retorno ao relatório."""
        resposta = self.client.get(self.url)
        self.assertIn(f"next={self.url}", resposta["Location"])

    def test_cenario_8_sem_dados(self):
        """2.8: mensagem exata e botões desabilitados, mesmo com linhas zeradas."""
        self.client.force_login(self.coordenador)
        resposta = self.client.get(self.url)
        self.assertContains(resposta, "Nenhum registro encontrado para os filtros selecionados")
        self.assertContains(resposta, "disabled", count=3)

    def test_sem_proposta_fora(self):
        """US-33 passo 5: Sem Proposta não entra."""
        aluno_com_status(self.turma, StatusTCC.SEM_PROPOSTA)
        aluno_com_status(self.turma)
        self.assertEqual(self.linha(self.consulta(), EC).valores["total"], 1)

    def test_grupos_cobrem_os_status(self):
        """FR-040: Sem Proposta à parte; os outros 9 valores, em exatamente um grupo."""
        todos = [status for grupo in GRUPOS_DE_STATUS.values() for status in grupo]
        self.assertEqual(len(todos), len(set(todos)))
        self.assertEqual(set(todos) | {StatusTCC.SEM_PROPOSTA}, set(StatusTCC))

    def test_soma_fecha_em_toda_linha(self):
        """SC-002: em toda linha e no Total."""
        for status in GRUPOS_DE_STATUS["ativos"] + GRUPOS_DE_STATUS["sem_sucesso"]:
            aluno_com_status(self.turma, status)
        relatorio = self.consulta()
        for linha in (*relatorio.linhas, *relatorio.totais):
            total, ativos, sucesso, sem = self.valores(linha)
            self.assertEqual(total, ativos + sucesso + sem)

    def test_pelo_ultimo_registro_do_tcc(self):
        """FR-041: o histórico, e não um registro antigo."""
        tcc = aluno_com_status(self.turma)
        registrar_status(tcc, StatusTCC.DESISTENTE)
        self.assertEqual(self.valores(self.linha(self.consulta(), EC)), (1, 0, 0, 1))

    def test_periodo_e_curso_filtrados(self):
        """Outro período e outro curso não entram."""
        aluno_com_status(criar_turma_de(self.professor, ano=2026, semestre=1))
        aluno_com_status(criar_turma_de(self.professor, curso_nome=SI))
        aluno_com_status(self.turma)
        relatorio = self.consulta()
        self.assertEqual(len(relatorio.linhas), 1)
        self.assertEqual(relatorio.totais[0].valores["total"], 1)

    def test_arquivo_no_agrupamento_da_tela(self):
        """P3 e FR-064: colunas da tela no arquivo, com a linha Total."""
        aluno_com_status(self.turma)
        self.client.force_login(self.coordenador)
        arquivo = self.client.get(
            reverse("relatorios:exportar", args=[ID, "csv"]) + "?agrupar_por=modalidade"
        )
        linhas = list(csv.reader(StringIO(arquivo.content.decode("utf-8-sig")), delimiter=";"))
        self.assertIn(
            ["Modalidade", "Total de Trabalhos", "Ativos", "Com Sucesso", "Sem Sucesso"], linhas
        )
        self.assertIn(["Total", "1", "1", "0", "0"], linhas)

    def test_kpis_e_grafico(self):
        """FR-072: 4 KPIs e barras só com o que tem trabalho."""
        self.povoar(ativos=2, concluidos=1)
        relatorio = self.consulta("curso=todos")
        self.assertEqual(
            [(kpi.rotulo, kpi.valor) for kpi in relatorio.kpis],
            [("Total de Trabalhos", 3), ("Ativos", 2), ("Com Sucesso", 1), ("Sem Sucesso", 0)],
        )
        self.assertEqual([item["rotulo"] for item in relatorio.grafico.dados], [EC])

    def test_sem_consulta_por_linha(self):
        """SC-001: uma consulta, sem depender do volume."""
        self.povoar(ativos=1, concluidos=0)

        def medir():
            form = FiltroRelatorioForm(
                QueryDict("curso=todos"), usuario=self.coordenador, registrado=registro.obter(ID)
            )
            self.assertTrue(form.is_valid())
            filtros = form.filtros()
            with CaptureQueriesContext(connection) as contexto:
                services_relatorios.producao_tccs(self.coordenador, filtros)
            return len(contexto)

        antes = medir()
        self.povoar(ativos=10, concluidos=3)
        self.assertEqual(medir(), antes)
