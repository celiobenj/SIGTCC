"""Igualdade entre a tela e os arquivos: 6 relatórios × 3 formatos, com dados hostis. Compara o
que o HTML mostra com o que cada arquivo traz, para pegar divergência nascida no template.

[US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2]
[RBN-REL-02.3][RBN-REL-02.4][FR-018][FR-019][FR-026][SC-005][research R15] (tasks T047)
"""

import csv
import re
from html.parser import HTMLParser
from io import BytesIO, StringIO

from django.urls import reverse
from openpyxl import load_workbook
from pypdf import PdfReader

from sigtcc.apps.relatorios import registro
from sigtcc.apps.relatorios.exportacao import proteger
from sigtcc.apps.relatorios.tests.apoio_relatorios import TesteRelatorios, cenario_hostil

RELATORIOS = (
    "atividades-docente",
    "membros-externos",
    "producao-tccs",
    "artigos",
    "formacao-evasao",
    "historico-nucomp",
)
CONSULTA = "?curso=todos"
_ESPACOS = re.compile(r"[\s\x00-\x1f]+")


def normal(valor):
    """Sem espaços e sem caracteres de controle: quebra de linha e o `\\x0b` do XLSX não contam."""
    return _ESPACOS.sub("", str("" if valor is None else valor))


class Tela(HTMLParser):
    """Lê a tabela do relatório como o usuário vê: cabeçalhos, linhas, totais e sub-listas."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cabecalhos, self.linhas, self.totais, self.sublistas = [], [], [], []
        self._dentro = False
        self._divs = 0
        self._profundidade = 0
        self._secao = None
        self._linha = None
        self._celula = None
        self._icone = 0
        self._titulo = None
        self._em_h4 = False
        self._em_p = False
        self._sub = None

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        if tag == "div" and "rel-tabela" in atributos.get("class", ""):
            self._dentro = True
        if not self._dentro:
            return
        if tag == "div":
            self._divs += 1
        elif tag == "span" and "ms" in atributos.get("class", ""):
            self._icone += 1
        elif tag == "table":
            self._profundidade += 1
            if self._profundidade == 2:
                self._sub = {"titulo": self._titulo, "cabecalhos": [], "linhas": [], "vazio": ""}
                self.sublistas[-1]["blocos"].append(self._sub)
        elif tag in ("thead", "tbody", "tfoot"):
            self._secao = tag
        elif tag == "tr":
            if "linha-sub" in atributos.get("class", ""):
                self.sublistas.append({"indice": len(self.linhas) - 1, "blocos": []})
            else:
                self._linha = []
        elif tag in ("td", "th") and "sub" not in atributos.get("class", ""):
            self._celula = []
        elif tag == "h4":
            self._em_h4, self._titulo = True, ""
        elif tag == "p":
            self._em_p = True

    def handle_endtag(self, tag):
        if not self._dentro:
            return
        if tag == "div":
            self._divs -= 1
            if self._divs == 0:
                self._dentro = False
        elif tag == "span" and self._icone:
            self._icone -= 1
        elif tag == "table":
            self._profundidade -= 1
        elif tag == "h4":
            self._em_h4 = False
        elif tag == "p":
            self._em_p = False
        elif tag in ("td", "th") and self._celula is not None:
            self._linha.append("".join(self._celula).strip())
            self._celula = None
        elif tag == "tr" and self._linha is not None:
            self._guardar_linha()
            self._linha = None

    def _guardar_linha(self):
        if self._profundidade == 2:
            destino = "cabecalhos" if self._secao == "thead" else "linhas"
            if destino == "cabecalhos":
                self._sub["cabecalhos"] = self._linha
            else:
                self._sub["linhas"].append(self._linha)
        elif self._secao == "thead":
            self.cabecalhos = self._linha
        elif self._secao == "tfoot":
            self.totais.append(self._linha)
        else:
            self.linhas.append(self._linha)

    def handle_data(self, dados):
        if self._icone:
            return
        if self._em_h4:
            self._titulo += dados
        elif self._em_p:
            self.sublistas[-1]["blocos"].append(
                {"titulo": self._titulo, "cabecalhos": None, "linhas": [], "vazio": dados}
            )
        elif self._celula is not None:
            self._celula.append(dados)


def ler_tela(html):
    """Tabela da tela, com os valores normalizados."""
    tela = Tela()
    tela.feed(html)
    tela.close()
    return tela


def linhas_de_sublista(tela, colunas_por_titulo, indice_mae):
    """Sub-listas por título, como o arquivo deve trazer: com a coluna da linha-mãe."""
    esperado = {}
    for sublista in tela.sublistas:
        mae = tela.linhas[sublista["indice"]][indice_mae]
        for bloco in sublista["blocos"]:
            linhas = esperado.setdefault(bloco["titulo"], [])
            if bloco["vazio"]:
                vazias = [""] * (colunas_por_titulo[bloco["titulo"]] - 1)
                linhas.append([mae, bloco["vazio"], *vazias])
            for linha in bloco["linhas"]:
                linhas.append([mae, *linha])
    return esperado


class TesteIgualdade(TesteRelatorios):
    """Mesmas colunas, ordem e valores nos 3 formatos (a exceção é a proteção de fórmula)."""

    def setUp(self):
        super().setUp()
        self.client.force_login(cenario_hostil())

    def tela(self, id):
        resposta = self.client.get(reverse("relatorios:relatorio", args=[id]) + CONSULTA)
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.context["relatorio"].tem_registros, id)
        relatorio = resposta.context["relatorio"]
        return ler_tela(resposta.content.decode()), relatorio

    def arquivo(self, id, formato):
        resposta = self.client.get(reverse("relatorios:exportar", args=[id, formato]) + CONSULTA)
        self.assertEqual(resposta.status_code, 200)
        return resposta.content

    def colunas_das_sublistas(self, relatorio):
        return {
            sublista.titulo: len(sublista.colunas)
            for linha in relatorio.linhas
            for sublista in linha.sublistas
        }

    def conferir(self, obtido, esperado, transformar=lambda valor: valor):
        """Compara sequências de linhas, sem espaços."""
        self.assertEqual(
            [[normal(valor) for valor in linha] for linha in obtido],
            [[normal(transformar(valor)) for valor in linha] for linha in esperado],
        )

    def test_csv(self):
        """Colunas, linhas, totais e sub-listas iguais, com a proteção de fórmula."""
        for id in RELATORIOS:
            with self.subTest(relatorio=id):
                tela, relatorio = self.tela(id)
                texto = self.arquivo(id, "csv").decode("utf-8-sig")
                linhas = list(csv.reader(StringIO(texto), delimiter=";"))
                inicio = linhas.index(tela.cabecalhos)
                fim = inicio + 1
                while fim < len(linhas) and linhas[fim]:
                    fim += 1
                self.conferir(linhas[inicio + 1 : fim], [*tela.linhas, *tela.totais], proteger)
                esperado = linhas_de_sublista(
                    tela,
                    self.colunas_das_sublistas(relatorio),
                    relatorio.indice_da_linha_mae(),
                )
                self.assertEqual(bool(esperado), id == "atividades-docente")
                for titulo, linhas_esperadas in esperado.items():
                    posicao = linhas.index([titulo]) + 2
                    self.conferir(
                        linhas[posicao : posicao + len(linhas_esperadas)],
                        linhas_esperadas,
                        proteger,
                    )

    def test_xlsx(self):
        """Colunas, linhas, totais e uma aba por sub-lista, com todo texto como texto."""
        for id in RELATORIOS:
            with self.subTest(relatorio=id):
                tela, relatorio = self.tela(id)
                livro = load_workbook(BytesIO(self.arquivo(id, "xlsx")))
                linhas = [
                    [celula.value for celula in linha] for linha in livro.worksheets[0].iter_rows()
                ]
                tamanho = len(tela.cabecalhos)
                inicio = next(
                    i for i, linha in enumerate(linhas) if linha[:tamanho] == tela.cabecalhos
                )
                self.conferir(
                    [linha[:tamanho] for linha in linhas[inicio + 1 :]],
                    [*tela.linhas, *tela.totais],
                )
                esperado = linhas_de_sublista(
                    tela,
                    self.colunas_das_sublistas(relatorio),
                    relatorio.indice_da_linha_mae(),
                )
                for titulo, linhas_esperadas in esperado.items():
                    aba = [
                        [celula.value for celula in linha] for linha in livro[titulo].iter_rows()
                    ]
                    self.conferir(aba[1:], linhas_esperadas)
                for aba in livro.worksheets:
                    for linha in aba.iter_rows():
                        for celula in linha:
                            self.assertIn(celula.data_type, ("inlineStr", "s", "n"), celula.value)

    def test_pdf(self):
        """Presença de todo valor e ordem aproximada, porque a quebra de linha impede o exato."""
        for id in RELATORIOS:
            with self.subTest(relatorio=id):
                tela, relatorio = self.tela(id)
                leitor = PdfReader(BytesIO(self.arquivo(id, "pdf")))
                texto = normal(" ".join(pagina.extract_text() for pagina in leitor.pages))
                posicao = texto.index(normal("Tabela"))
                for rotulo in tela.cabecalhos:
                    posicao = texto.index(normal(rotulo), posicao)
                for linha in [*tela.linhas, *tela.totais]:
                    for valor in linha:
                        self.assertIn(normal(valor), texto)

    def test_html_escapa_o_conteudo_hostil(self):
        """O título hostil aparece como texto, nunca como marcação."""
        resposta = self.client.get(reverse("relatorios:relatorio", args=["artigos"]) + CONSULTA)
        self.assertNotContains(resposta, "<script>alert(1)")
        self.assertContains(resposta, "&lt;script&gt;alert(1)")
        self.assertNotContains(resposta, 'href="javascript:')

    def test_cobre_todo_relatorio_registrado(self):
        """Relatório novo entra neste teste."""
        self.assertEqual(set(RELATORIOS), set(registro._RELATORIOS))
