"""Dados dos gráficos (spec 010; FR-072 a FR-075; research R9): sem HTML, com os números de CSS e
SVG já como `str` com ponto, porque o `pt-br` escreveria `33,3` e quebraria `width` e `points`.
A tabela é a fonte de verdade; o gráfico só reapresenta os mesmos números.

[US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.3]
[RBN-REL-02.4]
"""

from .estrutura import Grafico

LARGURA_SVG = 640
ALTURA_SVG = 240
MARGEM_SVG = 36


def _numero(valor):
    """Número com ponto, para CSS e SVG. [research R9]"""
    return f"{valor:.2f}"


def barras(itens, cor="azul"):
    """Barras horizontais, da maior para a menor, com o valor escrito. `itens`: (rótulo, valor).
    [FR-072][FR-074]
    """
    ordenados = sorted(itens, key=lambda item: (-item[1], item[0]))
    maior = max((valor for _, valor in ordenados), default=0) or 1
    dados = [
        {"rotulo": rotulo, "valor": valor, "largura": _numero(valor * 100 / maior), "cor": cor}
        for rotulo, valor in ordenados
    ]
    resumo = "; ".join(f"{rotulo}: {valor}" for rotulo, valor in ordenados)
    return Grafico("barras", dados, resumo)


def empilhado(linhas, legenda):
    """Barra 100% empilhada. `linhas`: (rótulo, valores na ordem da `legenda`); `legenda`:
    (rótulo, cor). Sem total, a linha fica sem barra. [FR-072][FR-075]
    """
    dados = []
    resumos = []
    for rotulo, valores in linhas:
        total = sum(valores)
        partes = []
        descricao = []
        for (nome, cor), valor in zip(legenda, valores):
            percentual = valor * 100 / total if total else 0
            partes.append(
                {"rotulo": nome, "valor": valor, "largura": _numero(percentual), "cor": cor}
            )
            descricao.append(f"{percentual:.0f}% {nome}")
        dados.append({"rotulo": rotulo, "total": total, "partes": partes if total else []})
        resumos.append(f"{rotulo}: {', '.join(descricao)}" if total else f"{rotulo}: sem alunos")
    conteudo = {"linhas": dados, "legenda": [{"rotulo": n, "cor": c} for n, c in legenda]}
    return Grafico("empilhado", conteudo, "; ".join(resumos))


def linhas(rotulos, series):
    """Linhas por período em SVG, com o valor escrito em cada ponto. `series`: dicionários com
    rotulo, valores, cor e tracejada. [FR-072][FR-074]
    """
    maior = max((valor for serie in series for valor in serie["valores"]), default=0) or 1
    util_x = LARGURA_SVG - 2 * MARGEM_SVG
    util_y = ALTURA_SVG - 2 * MARGEM_SVG
    passo = util_x / (len(rotulos) - 1) if len(rotulos) > 1 else 0

    def x(indice):
        return MARGEM_SVG + indice * passo if len(rotulos) > 1 else LARGURA_SVG / 2

    def y(valor):
        return ALTURA_SVG - MARGEM_SVG - valor * util_y / maior

    prontas = []
    for serie in series:
        pontos = [
            {"x": _numero(x(indice)), "y": _numero(y(valor)), "valor": valor}
            for indice, valor in enumerate(serie["valores"])
        ]
        prontas.append(
            {
                "rotulo": serie["rotulo"],
                "cor": serie["cor"],
                "tracejada": serie.get("tracejada", False),
                "pontos": pontos,
                "caminho": " ".join(f"{ponto['x']},{ponto['y']}" for ponto in pontos),
            }
        )
    eixo = [
        {"rotulo": rotulo, "x": _numero(x(indice)), "y": _numero(ALTURA_SVG - MARGEM_SVG / 3)}
        for indice, rotulo in enumerate(rotulos)
    ]
    conteudo = {
        "series": prontas,
        "eixo": eixo,
        "caixa": f"0 0 {LARGURA_SVG} {ALTURA_SVG}",
    }
    resumo = "; ".join(
        f"{serie['rotulo']}: " + ", ".join(str(valor) for valor in serie["valores"])
        for serie in series
    )
    return Grafico("linhas", conteudo, resumo)
