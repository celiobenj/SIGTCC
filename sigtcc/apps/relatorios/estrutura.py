"""Estrutura única de um relatório: a mesma alimenta a tela e os três arquivos (spec 010, C3;
contrato §3). Toda célula guarda `int` (contagem) ou `str` já formatada: `bool`, `date` e `None`
são recusados, para a tela e o arquivo não divergirem.

[US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2]
[RBN-REL-02.3][RBN-REL-02.4][FR-018][FR-066]
"""

from dataclasses import dataclass
from urllib.parse import urlsplit

from . import mensagens

MAXIMO_DE_KPIS = 4


@dataclass(frozen=True)
class Coluna:
    """Coluna da tabela; `definicao` vira o title do cabeçalho (MR-04). [FR-076]"""

    chave: str
    rotulo: str
    numerica: bool = False
    definicao: str = ""


@dataclass(frozen=True)
class Celula:
    """Célula pronta para a tela e para os arquivos; `url` só por link_seguro. [FR-066]"""

    texto: object
    url: str | None = None
    numerica: bool = False


def link_seguro(valor):
    """Célula do Link ou DOI: abre fora do sistema só com `https` e netloc, sem espaços nem
    caracteres de controle; o resto aparece como texto. [US-33][RBN-CAD-12.1][FR-066]
    """
    try:
        partes = urlsplit(valor)
    except ValueError:
        return Celula(valor)
    limpo = not any(caractere.isspace() or ord(caractere) < 32 for caractere in valor)
    if partes.scheme == "https" and partes.netloc and limpo:
        return Celula(valor, url=valor)
    return Celula(valor)


def _conferir_valor(valor):
    """Valor canônico da estrutura (contrato §3). [FR-018]"""
    if isinstance(valor, Celula):
        return
    if isinstance(valor, bool) or not isinstance(valor, (int, str)):
        raise TypeError(f"Valor de célula inválido: {type(valor).__name__}")


@dataclass(frozen=True)
class Linha:
    """Linha de tabela; `valores` é um dicionário por chave de coluna. [FR-018]"""

    valores: dict
    destaque: bool = False
    sublistas: tuple = ()

    def __post_init__(self):
        for valor in self.valores.values():
            _conferir_valor(valor)

    def celulas(self, colunas):
        """Células na ordem das colunas, sempre como Celula. [FR-018]"""
        prontas = []
        for coluna in colunas:
            valor = self.valores.get(coluna.chave, "")
            if isinstance(valor, Celula):
                prontas.append(valor)
            else:
                prontas.append(Celula(valor, numerica=coluna.numerica))
        return prontas


@dataclass(frozen=True)
class SubLista:
    """Sub-lista de uma linha; sem linhas, mostra `vazio`. [US-31][RBN-REL-01.1][FR-025]"""

    titulo: str
    colunas: tuple
    linhas: tuple
    vazio: str = mensagens.NENHUM_REGISTRO


@dataclass(frozen=True)
class Kpi:
    """Indicador do topo do relatório. [FR-072]"""

    rotulo: str
    valor: object


@dataclass(frozen=True)
class Grafico:
    """Gráfico único do relatório: `tipo` é "barras", "empilhado" ou "linhas". [FR-072][FR-075]"""

    tipo: str
    dados: object
    resumo: str


@dataclass(frozen=True)
class LinhaPronta:
    """Linha já resolvida para o template e os exportadores, sem regra neles. [FR-018]"""

    celulas: list
    destaque: bool
    sublistas: list


@dataclass(frozen=True)
class SubListaPronta:
    """Sub-lista já resolvida. [FR-025]"""

    titulo: str
    colunas: tuple
    linhas: list
    vazio: str


@dataclass
class Relatorio:
    """Resultado de uma consulta; `id`, `titulo`, `frase` e `gerado_em` vêm do registro, em
    montar_relatorio (contrato §3). `tem_registros=None` deriva de bool(linhas); quem tem linhas
    zeradas sobrescreve. [FR-018][FR-072]
    """

    colunas: tuple
    linhas: tuple
    totais: tuple = ()
    kpis: tuple = ()
    grafico: Grafico | None = None
    como_calculado: tuple = ()
    tem_registros: bool | None = None
    rotulo_linha: str = ""
    id: str = ""
    titulo: str = ""
    frase: str = ""
    gerado_em: object = None

    def __post_init__(self):
        if len(self.kpis) > MAXIMO_DE_KPIS:
            raise ValueError("Um relatório tem no máximo 4 KPIs")
        if self.tem_registros is None:
            self.tem_registros = bool(self.linhas)
        tem_sublistas = any(linha.sublistas for linha in self.linhas)
        if tem_sublistas and not self.rotulo_linha:
            raise ValueError("Sub-listas exigem rotulo_linha, a coluna da linha-mãe")

    def _pronta(self, linha):
        """Resolve uma linha e as suas sub-listas. [FR-018]"""
        sublistas = [
            SubListaPronta(
                titulo=sublista.titulo,
                colunas=sublista.colunas,
                linhas=[
                    LinhaPronta(item.celulas(sublista.colunas), item.destaque, [])
                    for item in sublista.linhas
                ],
                vazio=sublista.vazio,
            )
            for sublista in linha.sublistas
        ]
        return LinhaPronta(linha.celulas(self.colunas), linha.destaque, sublistas)

    def linhas_prontas(self):
        """Linhas na ordem da consulta, para o template e os exportadores. [FR-018]"""
        return [self._pronta(linha) for linha in self.linhas]

    def totais_prontos(self):
        """Linhas de total, com rótulo próprio. [FR-018]"""
        return [self._pronta(linha) for linha in self.totais]

    def rotulo_da_linha_mae(self):
        """Rótulo da coluna que identifica a linha-mãe nas sub-listas. [FR-026]"""
        for coluna in self.colunas:
            if coluna.chave == self.rotulo_linha:
                return coluna.rotulo
        return ""

    def indice_da_linha_mae(self):
        """Posição da coluna da linha-mãe. [FR-026]"""
        for indice, coluna in enumerate(self.colunas):
            if coluna.chave == self.rotulo_linha:
                return indice
        return 0
