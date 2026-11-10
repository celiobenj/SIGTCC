"""Cor dos chips de status, como no protótipo de 17/10: só aparência, sem regra de negócio.

Cada filtro devolve a classe de cor do .chip (verde, amarelo, vermelho, roxo, azul ou nenhuma),
com o mesmo significado em todas as telas (verde = concluído com sucesso, vermelho = sem sucesso,
amarelo = espera ou atenção).

[US-18][US-20][RBN-CAD-08.3][RBN-CAD-12.3]
"""

from django import template

from sigtcc.apps.cadastro.choices import Homologacao, StatusTCC

register = template.Library()

# chipSit do protótipo: Status do TCC → cor do chip.
_COR_STATUS_TCC = {
    StatusTCC.CONCLUIDO: "verde",
    StatusTCC.APROVADO: "verde",
    StatusTCC.APROVADO_PARA_TCC_2: "verde",
    StatusTCC.DESISTENTE: "vermelho",
    StatusTCC.REPROVADO: "vermelho",
    StatusTCC.JUBILADO: "vermelho",
    StatusTCC.APROVADO_COM_CORRECOES: "amarelo",
    StatusTCC.APTO_PARA_DEFESA: "roxo",
    StatusTCC.SEM_PROPOSTA: "",
    StatusTCC.EM_ANDAMENTO: "azul",
}

# Aproveitamento do artigo: homologado, recusado ou à espera da decisão do Coordenador.
_COR_HOMOLOGACAO = {
    Homologacao.HOMOLOGADO: "verde",
    Homologacao.RECUSADO: "vermelho",
    Homologacao.EM_ANALISE: "amarelo",
}


@register.filter
def cor_status_tcc(status):
    """Classe de cor do chip do Status do TCC (chipSit do protótipo). [US-14][RBN-CAD-08.3]"""
    return _COR_STATUS_TCC.get(status, "azul")


@register.filter
def cor_homologacao(homologacao):
    """Classe de cor do chip do aproveitamento do artigo; vazio sem valor. [US-20][RBN-CAD-12.3]"""
    return _COR_HOMOLOGACAO.get(homologacao, "")
