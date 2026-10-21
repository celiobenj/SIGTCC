"""Formulários de turmas e alunos (spec 004; research B18).

Diferente do primeiro acesso (spec 003, Q12), aqui todos os erros por campo aparecem.

[US-07][US-08][US-09][FR-002][FR-011][FR-016][FR-020][FR-023][FR-024]
"""

import re
import unicodedata

from django import forms
from django.core.exceptions import ValidationError

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.mensagens import M14_CAMPO_OBRIGATORIO

LIMITE_JUSTIFICATIVA = 500
_ESPACOS = re.compile(r"\s+")


def normalizar_texto(valor):
    """NFC, sem espaços nas pontas, espaços e quebras de linha repetidos viram um espaço.

    [US-08][US-09][RBN-CAD-05.1][RBN-CAD-05.4][B18][m2][m9]
    """
    if valor is None:
        return ""
    return _ESPACOS.sub(" ", unicodedata.normalize("NFC", str(valor))).strip()


def tem_caractere_de_controle(valor):
    """Algum caractere de controle (categoria Unicode C), depois da normalização. [m9]"""
    return any(unicodedata.category(c).startswith("C") for c in valor)


def validar_justificativa(valor):
    """Justificativa obrigatória, até 500 caracteres, sem caracteres de controle.

    Vazia, só com espaços, acima de 500 ou com caractere de controle →
    "Informe uma justificativa de até 500 caracteres".
    [US-09][RBN-CAD-05.4][RBN-CAD-05.6][RBN-CAD-08.4][FR-020][FR-023][FR-024][m9]
    """
    texto = normalizar_texto(valor)
    if not texto or len(texto) > LIMITE_JUSTIFICATIVA or tem_caractere_de_controle(texto):
        raise ValidationError(mensagens.JUSTIFICATIVA_500)
    return texto


class FormularioSigtcc(forms.Form):
    """Base dos formulários da spec 004: campo obrigatório com a M-14 e todos os erros por campo.

    [FR-002][M-14][B18]
    """

    use_required_attribute = False

    def __init__(self, *args, **kwargs):
        """Usa a M-14 como mensagem de campo obrigatório. [FR-002][M-14]"""
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.error_messages["required"] = M14_CAMPO_OBRIGATORIO
