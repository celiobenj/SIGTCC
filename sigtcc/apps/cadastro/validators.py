"""Regra de senha do SIGTCC (research A10; spec Q17).

8 a 64 caracteres, com ao menos uma letra de A a Z (maiúscula ou minúscula) e um número de 0 a 9.
Outros caracteres, inclusive letras acentuadas, são aceitos, mas não contam como a letra exigida.

[US-10][RBN-CAD-06.3][US-12][RBN-CAD-06.5][Q17]
"""

import re

from django.core.exceptions import ValidationError

from sigtcc.apps.cadastro.mensagens import REGRA_SENHA

TAMANHO_MINIMO = 8
TAMANHO_MAXIMO = 64
_LETRA = re.compile(r"[A-Za-z]")
_NUMERO = re.compile(r"[0-9]")


def senha_atende_regra(senha):
    """Diz se a senha segue a regra da US-10. [US-10][RBN-CAD-06.3][Q17]"""
    if senha is None or not TAMANHO_MINIMO <= len(senha) <= TAMANHO_MAXIMO:
        return False
    return bool(_LETRA.search(senha)) and bool(_NUMERO.search(senha))


def tamanho_de_senha_valido(senha):
    """Diz se a senha tem de 8 a 64 caracteres (login e senha atual). [US-11][RBN-CAD-06.4]"""
    return senha is not None and TAMANHO_MINIMO <= len(senha) <= TAMANHO_MAXIMO


class RegraSenhaSigtcc:
    """Validador do Django com a regra de senha, único em AUTH_PASSWORD_VALIDATORS.

    Vale também para outras features que chamarem validate_password (research A10).
    [US-10][RBN-CAD-06.3][US-12][RBN-CAD-06.5]
    """

    def validate(self, password, user=None):
        """Levanta ValidationError com o texto exato da US-10 se a senha não seguir a regra.

        [US-10][RBN-CAD-06.3]
        """
        if not senha_atende_regra(password):
            raise ValidationError(REGRA_SENHA, code="regra_senha_sigtcc")

    def get_help_text(self):
        """Texto de ajuda mostrado com o campo de senha.

        [US-10][RBN-CAD-06.3]
        """
        return REGRA_SENHA
