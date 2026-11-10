"""Filtros de exibição das tabelas dos relatórios: só formatação, sem regra de negócio.

[US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2]
[RBN-REL-02.3][RBN-REL-02.4][FR-070]
"""

import re

from django import template
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe

register = template.Library()

_COM_HIFEN = re.compile(r"\S*[-‐–]\S*")


@register.filter
def palavras_inteiras(valor):
    """Envolve em <span class="nw"> a palavra com hífen ou travessão, como "Humano-Computador"
    ou "14:00–17:40": o navegador quebraria a linha no hífen e partiria a palavra. O resto do
    texto continua quebrando entre palavras. Conteúdo escapado antes (autoescape mantido).
    fix(core): manter palavras inteiras nas tabelas em telas pequenas
    """
    texto = str(conditional_escape(valor))
    partes = []
    inicio = 0
    for achado in _COM_HIFEN.finditer(texto):
        partes.append(texto[inicio : achado.start()])
        partes.append(format_html('<span class="nw">{}</span>', mark_safe(achado.group())))
        inicio = achado.end()
    partes.append(texto[inicio:])
    return mark_safe("".join(partes))
