"""Filtros de exibição dos cartões de turma: só aparência, sem regra de negócio e sem coluna nova.

Traduzem do protótipo de 17/10 (docs/fonte/prototipo/prototipo_17_10.html) as funções
motivoBanner(curso), que desenha o motivo do banner pelo curso, e corDe(nome), que dá a cor do
avatar. O protótipo guardava a cor em cada turma; aqui ela sai do curso, porque o dicionário de
dados não tem essa coluna.

[US-07][US-13][FR-010][FR-031]
"""

from urllib.parse import quote

from django import template
from django.utils.safestring import mark_safe

from sigtcc.apps.cadastro.cargas import (
    CURSO_ENG_COMPUTACAO,
    CURSO_LIC_COMPUTACAO,
    CURSO_SIST_INFORMACAO,
)

register = template.Library()

# Paleta CORES do protótipo, na mesma ordem.
CORES = ("#1967d2", "#137333", "#e37400", "#129eaf", "#9334e6", "#c5221f", "#1e8e3e", "#b06000")

# Cor do banner de cada curso do NUCOMP: as três primeiras da paleta. Curso fora da lista usa a
# cor calculada pelo nome (_cor_do_texto), sempre a mesma para o mesmo curso.
_COR_DO_CURSO = {
    CURSO_ENG_COMPUTACAO: CORES[0],
    CURSO_SIST_INFORMACAO: CORES[1],
    CURSO_LIC_COMPUTACAO: CORES[2],
}

# Desenhos do motivoBanner do protótipo, copiados sem mudança: circuito (Engenharia de
# Computação), grafo (Sistemas de Informação) e livro com lápis (Licenciatura em Computação).
_ABRE_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' width='260' height='220' viewBox='0 0 260 220' "
    "fill='none' stroke='white' stroke-opacity='.28' stroke-width='3'>"
)
_MOTIVO_DO_CURSO = {
    CURSO_ENG_COMPUTACAO: _ABRE_SVG
    + "<path d='M20 40h80l20 20h60M60 100h60l20-20h90M40 160h110l20 20h70M120 60v40M180 80v100'/>"
    "<circle cx='20' cy='40' r='6'/><circle cx='180' cy='60' r='6'/>"
    "<circle cx='60' cy='100' r='6'/><circle cx='230' cy='80' r='6'/>"
    "<circle cx='40' cy='160' r='6'/><circle cx='240' cy='180' r='6'/>"
    "<rect x='140' y='110' width='70' height='44' rx='4'/></svg>",
    CURSO_SIST_INFORMACAO: _ABRE_SVG
    + "<path d='M50 60l80 30 70-50M130 90l-30 80M130 90l90 60M100 170l120-20M50 60l50 110'/>"
    "<circle cx='50' cy='60' r='12'/><circle cx='130' cy='90' r='16'/>"
    "<circle cx='200' cy='40' r='10'/><circle cx='100' cy='170' r='12'/>"
    "<circle cx='220' cy='150' r='14'/></svg>",
    CURSO_LIC_COMPUTACAO: _ABRE_SVG
    + "<path d='M40 150V60c30-10 60-10 90 10 30-20 60-20 90-10v90c-30-10-60-10-90 10-30-20-60-20"
    "-90-10zM130 70v90'/><path d='M170 190l60-60 14 14-60 60-20 6z'/></svg>",
}


def _cor_do_texto(texto):
    """corDe(txt) do protótipo: soma de hash 31 sem sinal (32 bits) e escolha na paleta."""
    soma = 0
    for caractere in str(texto):
        soma = (soma * 31 + ord(caractere)) & 0xFFFFFFFF
    return CORES[soma % len(CORES)]


@register.filter
def banner_turma(curso):
    """Estilo do banner do cartão (motivoBanner do protótipo): cor de fundo e desenho do curso.

    Devolve o valor do atributo style. O texto do curso só escolhe a entrada dos dicionários e
    nunca entra no resultado; cor e desenho são fixos, por isso o mark_safe é seguro. O SVG vai
    codificado como no encodeURIComponent do protótipo, entre aspas simples.
    [US-07][US-13][FR-010][FR-031]
    """
    nome = str(curso)
    estilo = f"background-color:{_COR_DO_CURSO.get(nome) or _cor_do_texto(nome)}"
    motivo = _MOTIVO_DO_CURSO.get(nome)
    if motivo:
        estilo += f";background-image:url('data:image/svg+xml,{quote(motivo, safe='')}')"
    return mark_safe(estilo)


@register.filter
def cor_avatar(nome):
    """Cor do avatar pela pessoa (corDe do protótipo), sempre a mesma para o mesmo nome.

    [US-07][US-13]
    """
    return _cor_do_texto(nome)
