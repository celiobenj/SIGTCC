"""Exportação genérica e dados dos gráficos, com um relatório de exemplo.

[US-31][US-47][US-32][US-33][RBN-REL-01.1][FR-018][FR-019][FR-020][FR-026][FR-072][FR-074]
(tasks T010 e T012)
"""

import csv
from datetime import datetime
from io import BytesIO, StringIO
from unittest import mock

from django.test import SimpleTestCase, override_settings
from openpyxl import load_workbook
from pypdf import PdfReader

from sigtcc.apps.defesa import pdf
from sigtcc.apps.relatorios import exportacao, graficos
from sigtcc.apps.relatorios.estrutura import Celula, Coluna, Kpi, Linha, Relatorio, SubLista
from sigtcc.apps.relatorios.exportacao import ErroAoExportar, exportar, proteger, titulo_de_aba
from sigtcc.apps.relatorios.forms import Filtros


def relatorio_de_exemplo(nome="Ana Souza", titulo_trabalho="Título do trabalho"):
    """Uma linha com sub-lista cheia, outra com sub-lista vazia, e total."""
    colunas = (Coluna("nome", "Docente"), Coluna("total", "Total de Bancas", numerica=True))
    sub_colunas = (Coluna("data", "Data"), Coluna("titulo", "Título do Trabalho"))
    cheia = SubLista(
        "Bancas",
        sub_colunas,
        (Linha({"data": "05/11/2026", "titulo": titulo_trabalho}, destaque=True),),
    )
    vazia = SubLista("Bancas", sub_colunas, ())
    return Relatorio(
        colunas,
        (
            Linha({"nome": nome, "total": 3}, sublistas=(cheia,)),
            Linha({"nome": "Bruno", "total": 0}, sublistas=(vazia,)),
        ),
        totais=(Linha({"nome": "Total", "total": 3}),),
        kpis=(Kpi("Docentes", 2), Kpi("Bancas", 3)),
        rotulo_linha="nome",
        id="exemplo",
        titulo="Relatório de exemplo",
        gerado_em=datetime(2026, 11, 5, 23, 15),
    )


FILTROS = Filtros(gestao=True, aplicados=(("Período letivo", "2026/2"), ("Curso", "Todos")))


class TesteProtecao(SimpleTestCase):
    """Texto que a planilha leria como fórmula. [FR-019]"""

    def test_prefixos(self):
        """Cada prefixo ganha `'`; número e texto comum ficam iguais."""
        for valor in ("=1+1", "+x", "-x", "@a", "\tx", "\rx", "\nx"):
            with self.subTest(valor=valor):
                self.assertEqual(proteger(valor), f"'{valor}")
        self.assertEqual(proteger("Ana"), "Ana")
        self.assertEqual(proteger(-3), -3)
        self.assertEqual(proteger(""), "")


@override_settings(LANGUAGE_CODE="pt-br")
class TesteCsv(SimpleTestCase):
    """CSV que abre certo na planilha. [FR-018][FR-019][FR-026]"""

    def linhas(self, relatorio=None):
        resposta = exportar(relatorio or relatorio_de_exemplo(), FILTROS, "csv")
        texto = resposta.content.decode("utf-8-sig")
        return resposta, list(csv.reader(StringIO(texto), delimiter=";"))

    def test_resposta(self):
        """Tipo, download sem cache, sem nome de pessoa e com BOM."""
        resposta, _ = self.linhas()
        self.assertEqual(resposta["Content-Type"], exportacao.TIPO_CSV)
        self.assertEqual(
            resposta["Content-Disposition"],
            'attachment; filename="relatorio-exemplo-20261105-2315.csv"',
        )
        self.assertEqual(resposta["Cache-Control"], "no-store")
        self.assertTrue(resposta.content.startswith(b"\xef\xbb\xbf"))

    def test_conteudo(self):
        """Título, filtros, data, tabela, total e sub-lista com a linha-mãe."""
        _, linhas = self.linhas()
        self.assertEqual(linhas[0], ["Relatório de exemplo"])
        self.assertEqual(linhas[1], ["Período letivo", "2026/2"])
        self.assertEqual(linhas[3], ["Gerado em 05/11/2026 às 23:15"])
        self.assertIn(["Docente", "Total de Bancas"], linhas)
        self.assertIn(["Ana Souza", "3"], linhas)
        self.assertIn(["Total", "3"], linhas)
        self.assertIn(["Bancas"], linhas)
        self.assertIn(["Docente", "Data", "Título do Trabalho"], linhas)
        self.assertIn(["Ana Souza", "05/11/2026", "Título do trabalho"], linhas)

    def test_um_bloco_por_titulo_e_vazia_com_o_texto_da_tela(self):
        """Sub-listas de mesmo título formam um bloco; a vazia diz "Nenhum registro"."""
        _, linhas = self.linhas()
        self.assertEqual(linhas.count(["Bancas"]), 1)
        self.assertIn(["Bruno", "Nenhum registro", ""], linhas)

    def test_formula_protegida(self):
        """Conteúdo hostil sai como texto."""
        _, linhas = self.linhas(relatorio_de_exemplo(nome="=1+1"))
        self.assertIn(["'=1+1", "3"], linhas)


class TesteXlsx(SimpleTestCase):
    """XLSX com abas e tipos certos. [FR-018][FR-019][FR-026]"""

    def livro(self, relatorio=None):
        resposta = exportar(relatorio or relatorio_de_exemplo(), FILTROS, "xlsx")
        return resposta, load_workbook(BytesIO(resposta.content))

    def valores(self, aba):
        return [[celula.value for celula in linha] for linha in aba.iter_rows()]

    def test_resposta_e_abas(self):
        """Uma aba principal e uma por sub-lista."""
        resposta, livro = self.livro()
        self.assertEqual(resposta["Content-Type"], exportacao.TIPO_XLSX)
        self.assertEqual(resposta["Cache-Control"], "no-store")
        self.assertEqual(livro.sheetnames, ["Relatório de exemplo", "Bancas"])

    def test_tabela_com_numero_e_total(self):
        """`int` continua numérico; o total entra."""
        _, livro = self.livro()
        valores = self.valores(livro.worksheets[0])
        self.assertIn(["Ana Souza", 3], valores)
        self.assertIn(["Total", 3], valores)

    def test_sublista_com_a_linha_mae(self):
        """Sub-lista cheia e vazia, com a coluna da linha-mãe."""
        _, livro = self.livro()
        valores = self.valores(livro["Bancas"])
        self.assertEqual(valores[0], ["Docente", "Data", "Título do Trabalho"])
        self.assertIn(["Ana Souza", "05/11/2026", "Título do trabalho"], valores)
        self.assertEqual(valores[-1][:2], ["Bruno", "Nenhum registro"])

    def test_conteudo_hostil_vira_texto(self):
        """Fórmula e `#REF!` não executam; caractere de controle não derruba o arquivo."""
        for valor, esperado in (("=1+1", "=1+1"), ("#REF!", "#REF!"), ("a\x0bb", "ab")):
            with self.subTest(valor=valor):
                _, livro = self.livro(relatorio_de_exemplo(nome=valor))
                aba = livro.worksheets[0]
                celulas = [c for linha in aba.iter_rows() for c in linha if c.value == esperado]
                self.assertTrue(celulas)
                self.assertEqual(celulas[0].data_type, "s")

    def test_destaque_em_negrito(self):
        """O destaque não depende só da cor."""
        _, livro = self.livro()
        celula = livro["Bancas"]["B2"]
        self.assertTrue(celula.font.bold)

    def test_titulo_de_aba_saneado(self):
        """Caracteres proibidos, limite de 31 e nome repetido."""
        usados = set()
        self.assertEqual(titulo_de_aba("a/b:c*d?e[f]g\\h", usados), "a b c d e f g h")
        longo = titulo_de_aba("x" * 40, usados)
        self.assertEqual(len(longo), 31)
        repetido = titulo_de_aba("x" * 40, usados)
        self.assertEqual(len(repetido), 31)
        self.assertNotEqual(longo, repetido)


class TestePdf(SimpleTestCase):
    """PDF em paisagem, sem gráfico e sem link. [FR-020]"""

    def leitor(self, relatorio=None):
        resposta = exportar(relatorio or relatorio_de_exemplo(), FILTROS, "pdf")
        return resposta, PdfReader(BytesIO(resposta.content))

    def test_paisagem(self):
        """Artigos tem 8 colunas: a página é mais larga que alta."""
        resposta, leitor = self.leitor()
        self.assertEqual(resposta["Content-Type"], "application/pdf")
        self.assertEqual(resposta["Cache-Control"], "no-store")
        caixa = leitor.pages[0].mediabox
        self.assertGreater(caixa.width, caixa.height)

    def test_conteudo(self):
        """Filtros, KPIs, tabela, total, sub-lista e data de geração."""
        _, leitor = self.leitor()
        texto = " ".join(pagina.extract_text() for pagina in leitor.pages)
        for esperado in (
            "Relatório de exemplo",
            "Período letivo: 2026/2",
            "Docentes",
            "Ana Souza",
            "Total",
            "Bancas",
            "Nenhum registro",
            "Gerado em 05/11/2026 às 23:15",
        ):
            with self.subTest(esperado=esperado):
                self.assertIn(esperado, texto)

    def test_sem_link(self):
        """Célula com url sai só como texto."""
        colunas = (Coluna("link", "Link"),)
        relatorio = Relatorio(
            colunas,
            (Linha({"link": Celula("https://doi.org/1", url="https://doi.org/1")}),),
            id="exemplo",
            titulo="Exemplo",
            gerado_em=datetime(2026, 11, 5, 23, 15),
        )
        _, leitor = self.leitor(relatorio)
        self.assertNotIn("/Annots", leitor.pages[0])

    def test_conteudo_hostil(self):
        """Marcação escapada e link longo sem espaço não derrubam o PDF."""
        for nome in ("<script>alert(1)</script>", "https://doi.org/" + "a" * 484, "a\x0bb"):
            with self.subTest(nome=nome[:10]):
                resposta, _ = self.leitor(relatorio_de_exemplo(nome=nome))
                self.assertTrue(resposta.content.startswith(b"%PDF"))


class TesteFalha(SimpleTestCase):
    """Falha em qualquer formato vira ErroAoExportar. [FR-018]"""

    def test_pdf(self):
        """ErroAoGerarPdf não escapa."""
        with mock.patch.object(pdf, "gerar_pdf", side_effect=pdf.ErroAoGerarPdf("x")):
            with self.assertRaises(ErroAoExportar):
                exportar(relatorio_de_exemplo(), FILTROS, "pdf")

    def test_csv_e_xlsx(self):
        """Erro inesperado também."""
        for formato in ("csv", "xlsx"):
            with self.subTest(formato=formato), mock.patch.object(
                exportacao, "sublistas_para_arquivo", side_effect=ValueError
            ):
                with self.assertRaises(ErroAoExportar):
                    exportar(relatorio_de_exemplo(), FILTROS, formato)


class TesteGraficos(SimpleTestCase):
    """Dados dos gráficos, sem HTML e com ponto. [FR-072][FR-074][FR-075]"""

    def test_barras_da_maior_para_a_menor(self):
        """Ordem, largura com ponto e resumo."""
        grafico = graficos.barras([("A", 1), ("B", 3), ("C", 2)])
        self.assertEqual([item["rotulo"] for item in grafico.dados], ["B", "C", "A"])
        self.assertEqual(grafico.dados[1]["largura"], "66.67")
        self.assertEqual(grafico.resumo, "B: 3; C: 2; A: 1")

    def test_barras_zeradas_nao_dividem_por_zero(self):
        """Tudo zero: largura 0."""
        self.assertEqual(graficos.barras([("A", 0)]).dados[0]["largura"], "0.00")

    def test_empilhado(self):
        """Partes somam 100%; curso sem alunos fica sem barra."""
        legenda = (("Ativos", "azul"), ("Com Sucesso", "verde"))
        grafico = graficos.empilhado([("EC", (3, 1)), ("SI", (0, 0))], legenda)
        partes = grafico.dados["linhas"][0]["partes"]
        self.assertEqual([p["largura"] for p in partes], ["75.00", "25.00"])
        self.assertEqual(grafico.dados["linhas"][1]["partes"], [])
        self.assertIn("EC: 75% Ativos, 25% Com Sucesso", grafico.resumo)

    def test_linhas(self):
        """Pontos com ponto decimal; um período só não divide por zero."""
        series = [{"rotulo": "Vinculados", "valores": [1, 3], "cor": "azul"}]
        grafico = graficos.linhas(["2025/2", "2026/1"], series)
        self.assertNotIn(",", grafico.dados["series"][0]["pontos"][0]["x"])
        self.assertIn(",", grafico.dados["series"][0]["caminho"])
        unico = graficos.linhas(["2026/1"], [{"rotulo": "V", "valores": [0], "cor": "azul"}])
        self.assertEqual(unico.dados["series"][0]["pontos"][0]["x"], "320.00")
