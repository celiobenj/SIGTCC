"""Exportação genérica em PDF, CSV e XLSX a partir da estrutura do relatório (spec 010, C4;
contrato §4). Sem código por relatório; nada é gravado: tudo em memória, a cada download.

[US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2]
[RBN-REL-02.3][RBN-REL-02.4][FR-018][FR-019][FR-020][FR-026]
"""

import csv
import re
from io import BytesIO, StringIO

from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.styles import Font, PatternFill

from sigtcc.apps.defesa import pdf

FORMATOS = ("pdf", "csv", "xlsx")
TIPO_CSV = "text/csv; charset=utf-8"
TIPO_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
TEMPLATE_PDF = "relatorios/pdf/relatorio.html"
_PREFIXOS_DE_FORMULA = ("=", "+", "-", "@", "\t", "\r", "\n")
_CARACTERES_DE_ABA = re.compile(r"[\\/*?:\[\]]")
_TAMANHO_DA_ABA = 31
_FUNDO_DE_DESTAQUE = PatternFill("solid", fgColor="FEF7E0")


class ErroAoExportar(Exception):
    """Falha ao gerar o arquivo; a view mostra a MR-07. [FR-018]"""


def proteger(valor):
    """Texto que uma planilha leria como fórmula ganha `'` na frente; é a única diferença
    permitida entre o CSV e a tela (SC-005). [FR-019]
    """
    if isinstance(valor, str) and valor.startswith(_PREFIXOS_DE_FORMULA):
        return f"'{valor}"
    return valor


def texto_de_geracao(relatorio):
    """Data e hora de geração, iguais em todo o arquivo. [FR-018][FR-076]"""
    return f"Gerado em {relatorio.gerado_em:%d/%m/%Y às %H:%M}"


def sublistas_para_arquivo(relatorio):
    """Sub-listas por título, cada linha com a coluna da linha-mãe; sub-lista vazia sai com o
    mesmo texto da tela (research R10). [US-31][RBN-REL-01.1][FR-026]
    """
    indice = relatorio.indice_da_linha_mae()
    blocos = {}
    for linha in relatorio.linhas_prontas():
        mae = linha.celulas[indice].texto if linha.celulas else ""
        for sublista in linha.sublistas:
            bloco = blocos.setdefault(
                sublista.titulo,
                {
                    "titulo": sublista.titulo,
                    "colunas": [relatorio.rotulo_da_linha_mae()]
                    + [coluna.rotulo for coluna in sublista.colunas],
                    "linhas": [],
                },
            )
            if not sublista.linhas:
                vazias = [""] * (len(sublista.colunas) - 1)
                bloco["linhas"].append(([mae, sublista.vazio, *vazias], False))
            for item in sublista.linhas:
                textos = [celula.texto for celula in item.celulas]
                bloco["linhas"].append(([mae, *textos], item.destaque))
    return list(blocos.values())


def _resposta(conteudo, tipo, relatorio, extensao):
    """Resposta de download, sem cache e sem nome de pessoa no arquivo. [FR-018]"""
    resposta = HttpResponse(conteudo, content_type=tipo)
    nome = f"relatorio-{relatorio.id}-{relatorio.gerado_em:%Y%m%d-%H%M}.{extensao}"
    resposta["Content-Disposition"] = f'attachment; filename="{nome}"'
    resposta["Cache-Control"] = "no-store"
    return resposta


def _csv(relatorio, filtros):
    """UTF-8 com BOM e `;`: abre com acentos e colunas certos na planilha. [FR-019]"""
    saida = StringIO()
    escritor = csv.writer(saida, delimiter=";")

    def escrever(linha):
        escritor.writerow([proteger(valor) for valor in linha])

    escrever([relatorio.titulo])
    for rotulo, valor in filtros.aplicados:
        escrever([rotulo, valor])
    escrever([texto_de_geracao(relatorio)])
    escrever([])
    escrever([coluna.rotulo for coluna in relatorio.colunas])
    for linha in relatorio.linhas_prontas() + relatorio.totais_prontos():
        escrever([celula.texto for celula in linha.celulas])
    for bloco in sublistas_para_arquivo(relatorio):
        escrever([])
        escrever([bloco["titulo"]])
        escrever(bloco["colunas"])
        for valores, _ in bloco["linhas"]:
            escrever(valores)
    return saida.getvalue().encode("utf-8-sig")


def titulo_de_aba(titulo, usados):
    """Título aceito pelo XLSX: sem caracteres proibidos, até 31 caracteres e sem repetir.

    [FR-018][research R10]
    """
    base = _CARACTERES_DE_ABA.sub(" ", ILLEGAL_CHARACTERS_RE.sub("", titulo)).strip() or "Relatorio"
    base = base[:_TAMANHO_DA_ABA]
    candidato, numero = base, 1
    while candidato in usados:
        numero += 1
        sufixo = f" {numero}"
        candidato = base[: _TAMANHO_DA_ABA - len(sufixo)] + sufixo
    usados.add(candidato)
    return candidato


def _gravar_linha(aba, linha, valores, negrito=False, destaque=False):
    """Toda `str` vai como texto, o que cobre fórmula e `#REF!`; `int` continua numérico.

    [FR-019][research R10]
    """
    for coluna, valor in enumerate(valores, start=1):
        celula = aba.cell(row=linha, column=coluna)
        if isinstance(valor, str):
            celula.value = ILLEGAL_CHARACTERS_RE.sub("", valor)
            celula.data_type = "s"
        else:
            celula.value = valor
        if negrito or destaque:
            celula.font = Font(bold=True)
        if destaque:
            celula.fill = _FUNDO_DE_DESTAQUE


def _xlsx(relatorio, filtros):
    """Aba principal com filtros, data, tabela e totais; uma aba por sub-lista. [FR-018][FR-026]"""
    livro = Workbook()
    aba = livro.active
    usados = set()
    aba.title = titulo_de_aba(relatorio.titulo, usados)
    linha = 1
    _gravar_linha(aba, linha, [relatorio.titulo], negrito=True)
    for rotulo, valor in filtros.aplicados:
        linha += 1
        _gravar_linha(aba, linha, [rotulo, valor])
    linha += 1
    _gravar_linha(aba, linha, [texto_de_geracao(relatorio)])
    linha += 2
    _gravar_linha(aba, linha, [coluna.rotulo for coluna in relatorio.colunas], negrito=True)
    for pronta in relatorio.linhas_prontas():
        linha += 1
        textos = [celula.texto for celula in pronta.celulas]
        _gravar_linha(aba, linha, textos, destaque=pronta.destaque)
    for pronta in relatorio.totais_prontos():
        linha += 1
        _gravar_linha(aba, linha, [celula.texto for celula in pronta.celulas], negrito=True)
    for bloco in sublistas_para_arquivo(relatorio):
        aba_lista = livro.create_sheet(titulo_de_aba(bloco["titulo"], usados))
        _gravar_linha(aba_lista, 1, bloco["colunas"], negrito=True)
        for posicao, (valores, destaque) in enumerate(bloco["linhas"], start=2):
            _gravar_linha(aba_lista, posicao, valores, destaque=destaque)
    saida = BytesIO()
    livro.save(saida)
    return saida.getvalue()


def _pdf(relatorio, filtros):
    """Cabeçalho, filtros, KPIs em tabela simples, tabela e sub-listas, sem gráfico e sem link.

    [FR-020][research R10]
    """
    return pdf.gerar_pdf(
        TEMPLATE_PDF,
        {
            "titulo": relatorio.titulo,
            "relatorio": relatorio,
            "filtros": filtros,
            "linhas": relatorio.linhas_prontas(),
            "totais": relatorio.totais_prontos(),
            "sublistas": sublistas_para_arquivo(relatorio),
            "geracao": texto_de_geracao(relatorio),
        },
    )


def exportar(relatorio, filtros, formato):
    """Arquivo do relatório no formato pedido; quem chama conferiu a permissão antes. Falha em
    qualquer formato vira ErroAoExportar. [FR-018][FR-019][FR-020]
    """
    geradores = {
        "pdf": (_pdf, "application/pdf"),
        "csv": (_csv, TIPO_CSV),
        "xlsx": (_xlsx, TIPO_XLSX),
    }
    gerador, tipo = geradores[formato]
    try:
        conteudo = gerador(relatorio, filtros)
    except Exception as erro:
        raise ErroAoExportar(formato) from erro
    return _resposta(conteudo, tipo, relatorio, formato)
