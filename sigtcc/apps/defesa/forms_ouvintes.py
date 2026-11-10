"""Formulários dos ouvintes da sessão (spec 009, US2; research B9): uma linha por ouvinte (Nome
Completo e Matrícula), em formset com Remover (can_delete) e a linha extra vazia ignorada; e a
janela Ocorrências (US3; research B10).

A validação das linhas fica em funções (validar_nome, validar_matricula, repetidas) usadas pelo
formulário e pelo serviço (services_ouvintes.salvar_ouvintes), que é a fonte da regra. Campos
com erro recebem a classe `erro` (destaque em vermelho, .inp.erro do CSS).

[US-30][RBN-DEF-08.2][RBN-DEF-08.5] (spec 009, tasks T024 e T038)
"""

import re

from django import forms
from django.forms import BaseFormSet, formset_factory

from sigtcc.apps.defesa import mensagens

# Matrícula: exatamente 10 dígitos (Ouvintes.ouv_matricula CHAR(10); RBN-DEF-08.2).
# [US-30][RBN-DEF-08.2]
MATRICULA = re.compile(r"^[0-9]{10}$")
TAMANHO_DO_NOME = 150
MAXIMO_DE_OUVINTES = 200


def validar_nome(nome):
    """Nome aparado, ou None se inválido: não vazio, até 150 caracteres e cada caractere uma
    letra (str.isalpha, que aceita acentos e recusa "×" e "÷"; revisão M-06) ou espaço.
    [US-30][RBN-DEF-08.2]
    """
    nome = (nome or "").strip()
    if not nome or len(nome) > TAMANHO_DO_NOME:
        return None
    if not all(caractere.isalpha() or caractere == " " for caractere in nome):
        return None
    return nome


def validar_matricula(matricula):
    """Matrícula aparada, ou None se não tiver exatamente 10 dígitos. [US-30][RBN-DEF-08.2]"""
    matricula = (matricula or "").strip()
    return matricula if MATRICULA.match(matricula) else None


def repetidas(matriculas):
    """Índices das linhas cuja matrícula já apareceu numa linha anterior da mesma lista (a
    duplicata é conferida só dentro da lista enviada, que é o estado final da sessão; I-03).
    [US-30][RBN-DEF-08.2]
    """
    vistas, indices = set(), []
    for indice, matricula in enumerate(matriculas):
        if matricula in vistas:
            indices.append(indice)
        vistas.add(matricula)
    return indices


def _marcar_erros(form):
    """Acrescenta a classe `erro` aos widgets dos campos com erro (campo destacado).
    [US-30][RBN-DEF-08.2][RBN-DEF-08.5]
    """
    for nome in form.errors:
        if nome in form.fields:
            widget = form.fields[nome].widget
            classes = widget.attrs.get("class", "")
            if "erro" not in classes.split():
                widget.attrs["class"] = f"{classes} erro".strip()


class OuvinteForm(forms.Form):
    """Uma linha da janela Ouvintes: Nome Completo e Matrícula (US-30 A; FR-010 e FR-011).
    [US-30][RBN-DEF-08.2]
    """

    nome = forms.CharField(
        label="Nome Completo",
        required=False,
        strip=False,
        widget=forms.TextInput(attrs={"class": "inp", "maxlength": TAMANHO_DO_NOME}),
    )
    matricula = forms.CharField(
        label="Matrícula",
        required=False,
        widget=forms.TextInput(attrs={"class": "inp", "maxlength": 10, "inputmode": "numeric"}),
    )

    def clean_nome(self):
        """Nome só com letras, acentos e espaços, até 150 (US-30 E4). [US-30][RBN-DEF-08.2]"""
        nome = validar_nome(self.cleaned_data.get("nome"))
        if nome is None:
            raise forms.ValidationError(mensagens.NOME_INVALIDO)
        return nome

    def clean_matricula(self):
        """Matrícula com exatamente 10 dígitos (US-30 E3). [US-30][RBN-DEF-08.2]"""
        matricula = validar_matricula(self.cleaned_data.get("matricula"))
        if matricula is None:
            raise forms.ValidationError(mensagens.MATRICULA_INVALIDA)
        return matricula

    def full_clean(self):
        """Validação do Django e o destaque dos campos com erro. [US-30][RBN-DEF-08.2]"""
        super().full_clean()
        _marcar_erros(self)


class BaseOuvintesFormSet(BaseFormSet):
    """Lista inteira de ouvintes: a linha extra vazia é ignorada (empty_permitted) e a mesma
    matrícula em duas linhas marca a repetida com "Este aluno já foi registrado como ouvinte
    nesta defesa" (US-30 cenário 13). [US-30][RBN-DEF-08.2]
    """

    def linhas_validas(self):
        """Formulários que entram na lista: preenchidos e não marcados para remover.
        [US-30][RBN-DEF-08.2]
        """
        return [
            form
            for form in self.forms
            if form.has_changed() and not (self.can_delete and self._should_delete_form(form))
        ]

    def clean(self):
        """Duplicata só dentro da lista enviada (I-03). [US-30][RBN-DEF-08.2]"""
        if any(self.errors):
            return
        linhas = self.linhas_validas()
        for indice in repetidas([form.cleaned_data["matricula"] for form in linhas]):
            linhas[indice].add_error("matricula", mensagens.OUVINTE_REPETIDO)
            _marcar_erros(linhas[indice])

    def linhas(self):
        """Lista final como (nome, matrícula), depois de is_valid. [US-30][RBN-DEF-08.2]"""
        return [
            (form.cleaned_data["nome"], form.cleaned_data["matricula"])
            for form in self.linhas_validas()
        ]


OuvintesFormSet = formset_factory(
    OuvinteForm,
    formset=BaseOuvintesFormSet,
    extra=1,
    can_delete=True,
    max_num=MAXIMO_DE_OUVINTES,
    absolute_max=MAXIMO_DE_OUVINTES,
    validate_max=True,
)


# =============================================================================================
# Ocorrências da sessão (US-30 B; RBN-DEF-08.5; research B10)
# =============================================================================================

# "VARCHAR(2000)" de Defesas.def_ocorrencias (dicionário 3.6.1). [US-30][RBN-DEF-08.5]
TAMANHO_DAS_OCORRENCIAS = 2000


def normalizar_ocorrencias(texto):
    """Texto com as quebras de linha CRLF e CR trocadas por LF (o limite bate com o contador
    da tela) e aparado; vazio vira "". [US-30][RBN-DEF-08.5]
    """
    return (texto or "").replace("\r\n", "\n").replace("\r", "\n").strip()


class OcorrenciasForm(forms.Form):
    """Janela Ocorrências (US-30 B; FR-013): texto livre opcional de até 2.000 caracteres,
    contados depois de normalizar as quebras de linha (revisão M-07); acima disso, a MX-01 e a
    caixa destacada (classe `erro`). [US-30][RBN-DEF-08.5]
    """

    ocorrencias = forms.CharField(
        label="Ocorrências",
        required=False,
        strip=False,
        widget=forms.Textarea(
            attrs={
                "class": "inp",
                "rows": 8,
                "maxlength": TAMANHO_DAS_OCORRENCIAS,
                "data-contador": TAMANHO_DAS_OCORRENCIAS,
            }
        ),
    )

    def clean_ocorrencias(self):
        """Normaliza e confere o limite (US-30 E5; MX-01). [US-30][RBN-DEF-08.5]"""
        texto = normalizar_ocorrencias(self.cleaned_data.get("ocorrencias"))
        if len(texto) > TAMANHO_DAS_OCORRENCIAS:
            raise forms.ValidationError(mensagens.MX01_OCORRENCIAS_LONGAS)
        return texto

    def full_clean(self):
        """Validação do Django e o destaque da caixa com erro. [US-30][RBN-DEF-08.5]"""
        super().full_clean()
        _marcar_erros(self)
