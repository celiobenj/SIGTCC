"""Formulários da Gestão de Contas (spec 002). Só forms.Form, nunca ModelForm: o serviço grava com
update_fields explícito (research C20).

[US-03][US-05][FR-002][FR-003][FR-004][FR-012][FR-032][RBN-CAD-01.1][RBN-CAD-03.1]
"""

import unicodedata

from django import forms
from django.core.exceptions import ValidationError

from sigtcc.apps.cadastro import mensagens, services
from sigtcc.apps.cadastro.choices import Titulacao
from sigtcc.apps.cadastro.forms import _email_no_formato, email_institucional
from sigtcc.apps.cadastro.forms_turmas import letra_latina, normalizar_texto
from sigtcc.apps.cadastro.models import Cursos

LIMITE_NOME = 150
LIMITE_EMAIL = 100
LIMITE_INSTITUICAO = 150


# =============================================================================================
# Validadores (FR-002, FR-012, FR-032)
# =============================================================================================


def validar_nome_completo(valor):
    """Só letras (com acentos) e espaços, até 150 caracteres (US-03 E4, US-05 E4).

    [US-03][US-05][RBN-CAD-01.1][RBN-CAD-03.1][FR-002]
    """
    texto = normalizar_texto(valor)
    if not texto or len(texto) > LIMITE_NOME or not all(c == " " or letra_latina(c) for c in texto):
        raise ValidationError(mensagens.NOME_INVALIDO)
    return texto


def validar_email_institucional(valor):
    """Formato nome@uea.edu.br, até 100 caracteres; devolve o e-mail normalizado (spec 003, Q13).

    [US-03][RBN-CAD-01.1][RBN-CAD-02.1][FR-012]
    """
    email = services.normalizar_email(valor)
    if not email or not email_institucional(email):
        raise ValidationError(mensagens.EMAIL_INSTITUCIONAL_CONTAS)
    return email


def validar_email_qualquer(valor):
    """Formato nome@domínio, de qualquer domínio, até 100 caracteres; devolve normalizado.

    [US-05][RBN-CAD-03.1][FR-032]
    """
    email = services.normalizar_email(valor)
    if not email or not _email_no_formato(email):
        raise ValidationError(mensagens.EMAIL_VALIDO)
    return email


def _caractere_de_instituicao(caractere):
    """Letra latina, número, espaço ou pontuação. [US-05][RBN-CAD-03.1]"""
    return (
        caractere == " "
        or letra_latina(caractere)
        or caractere.isdigit()
        or unicodedata.category(caractere).startswith("P")
    )


def validar_instituicao(valor):
    """Letras, números, espaços e pontuação, até 150 caracteres (US-05 E5).

    [US-05][RBN-CAD-03.1][FR-032]
    """
    texto = normalizar_texto(valor)
    if (
        not texto
        or len(texto) > LIMITE_INSTITUICAO
        or not all(map(_caractere_de_instituicao, texto))
    ):
        raise ValidationError(mensagens.INSTITUICAO_INVALIDA)
    return texto


# =============================================================================================
# Campos e base
# =============================================================================================


def campo_nome():
    """Nome Completo. [FR-002]"""
    return forms.CharField(
        label="Nome Completo",
        max_length=None,
        widget=forms.TextInput(attrs={"maxlength": LIMITE_NOME}),
    )


def campo_email_institucional():
    """E-mail Institucional (@uea.edu.br). [FR-012]"""
    return forms.CharField(
        label="E-mail Institucional",
        widget=forms.EmailInput(attrs={"maxlength": LIMITE_EMAIL}),
    )


def campo_email():
    """E-mail de qualquer domínio (Membro Externo). [FR-032]"""
    return forms.CharField(
        label="E-mail", widget=forms.EmailInput(attrs={"maxlength": LIMITE_EMAIL})
    )


def campo_titulacao():
    """Titulação em lista suspensa; valor fora: "Selecione uma opção válida". [FR-004]"""
    return forms.ChoiceField(
        label="Titulação",
        choices=[("", "Selecione")] + list(Titulacao.choices),
        error_messages={"invalid_choice": mensagens.OPCAO_INVALIDA},
    )


def campo_curso(rotulo, required=True):
    """Curso do NUCOMP em lista suspensa; valor fora: "Selecione uma opção válida". [FR-004]"""
    return forms.ModelChoiceField(
        label=rotulo,
        queryset=Cursos.objects.order_by("cur_nome"),
        empty_label="Selecione",
        required=required,
        error_messages={"invalid_choice": mensagens.OPCAO_INVALIDA},
    )


def campo_instituicao():
    """Instituição de Origem. [FR-032]"""
    return forms.CharField(
        label="Instituição de Origem",
        widget=forms.TextInput(attrs={"maxlength": LIMITE_INSTITUICAO}),
    )


def campo_sua_senha():
    """ "Sua senha": senha de quem altera, exigida só com e-mail novo (FR-008; research C7).

    Nunca devolve o valor ao HTML (sem render_value).
    """
    return forms.CharField(
        label=mensagens.SUA_SENHA,
        required=False,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )


class FormularioContas(forms.Form):
    """Base dos formulários da Gestão de Contas: obrigatório vazio mostra "Campo obrigatório"
    (US-03 E5, US-05 E3) e o navegador não bloqueia o envio (mensagem sempre a da US).
    [US-03][US-05][FR-003][Q9]
    """

    use_required_attribute = False

    def __init__(self, *args, **kwargs):
        """Usa a M-14 ("Campo obrigatório") como mensagem de campo obrigatório. [FR-003]"""
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.error_messages["required"] = mensagens.M14_CAMPO_OBRIGATORIO
