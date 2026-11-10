"""Filtros de exibição das sessões de defesa: janela de 1 hora e Local ou Link, sem consulta
nova (os dados vêm de services_defesa.listar_defesas). Só formatação, sem regra de negócio.

[US-21][US-40][RBN-DEF-01.1][RBN-DEF-01.4]
"""

from datetime import datetime

from django import template

from sigtcc.apps.defesa.choices import FormatoSessao
from sigtcc.apps.defesa.services_defesa import DURACAO_DA_SESSAO

register = template.Library()


@register.filter
def horario(sessao):
    """ "HH:MM–HH:MM" com a reserva de 1 hora (RBN-DEF-01.1). [US-21][US-40][RBN-DEF-01.4]"""
    inicio = datetime.combine(sessao.def_data, sessao.def_h_inicio)
    return f"{inicio:%H:%M}–{inicio + DURACAO_DA_SESSAO:%H:%M}"


@register.filter
def lugar(sessao):
    """Local (Presencial) ou Link da Videochamada (Remota). [US-21][US-40][RBN-DEF-01.4]"""
    if sessao.def_formato == FormatoSessao.PRESENCIAL:
        return sessao.defesaspresenciais.dep_local
    return sessao.defesasremotas.der_link
