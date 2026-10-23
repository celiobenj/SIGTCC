"""Formulários da Proposta e dos dados do TCC do app cadastro (spec 005).

`PropostaForm` (Título, Subtítulo, Resumo, Modalidade, Link) e `DadosTCCForm` (Área de Interesse
e Palavras-Chave), com as validações do FR-007 (US-13).

[US-13][RBN-CAD-07.1][RBN-CAD-08.1][research C1][research C3]
"""

from django import forms
from django.core.exceptions import ValidationError

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import ModalidadeTCC
from sigtcc.apps.cadastro.forms_turmas import FormularioSigtcc, normalizar_texto
from sigtcc.apps.cadastro.models import AreasInteresse

LIMITE_TITULO = 250
LIMITE_SUBTITULO = 250
LIMITE_RESUMO = 1000
LIMITE_LINK = 500
LIMITE_PALAVRA_CHAVE = 100
MAXIMO_PALAVRAS_CHAVE = 5


class PropostaForm(FormularioSigtcc):
    """Título, Subtítulo, Resumo, Modalidade e Link do Documento da Proposta (FR-001, FR-007).

    Usado tanto para a primeira Proposta (passos 2 a 6 da US-13) quanto, com os mesmos campos
    preenchidos, para a mudança de tema enquanto o TCC estiver "Em Andamento" (fluxos A e B).
    [US-13][RBN-CAD-07.1][FR-001][FR-007]
    """

    titulo = forms.CharField(
        label="Título",
        max_length=LIMITE_TITULO,
        widget=forms.TextInput(attrs={"maxlength": LIMITE_TITULO}),
    )
    subtitulo = forms.CharField(
        label="Subtítulo",
        max_length=LIMITE_SUBTITULO,
        required=False,
        widget=forms.TextInput(attrs={"maxlength": LIMITE_SUBTITULO}),
    )
    resumo = forms.CharField(
        label="Resumo",
        max_length=LIMITE_RESUMO,
        help_text=f"Até {LIMITE_RESUMO} caracteres",
        widget=forms.Textarea(attrs={"rows": 6, "maxlength": LIMITE_RESUMO}),
    )
    modalidade = forms.ChoiceField(label="Modalidade", choices=ModalidadeTCC.choices)
    link = forms.CharField(
        label="Link do Documento da Proposta",
        required=False,
        help_text="Endereço público, iniciado por https:// (até 500 caracteres)",
        widget=forms.TextInput(attrs={"maxlength": LIMITE_LINK}),
    )

    def __init__(self, *args, somente_leitura=False, **kwargs):
        """Com somente_leitura, desabilita todos os campos (E7 a E9 da US-13). [FR-006]"""
        super().__init__(*args, **kwargs)
        if somente_leitura:
            for campo in self.fields.values():
                campo.disabled = True

    def clean_titulo(self):
        """Obrigatório, até 250 caracteres (E2, E3). [FR-001][FR-007]"""
        return normalizar_texto(self.cleaned_data["titulo"])

    def clean_subtitulo(self):
        """Opcional, até 250 caracteres (E3). [FR-001][FR-007]"""
        return normalizar_texto(self.cleaned_data.get("subtitulo", ""))

    def clean_resumo(self):
        """Obrigatório, até 1.000 caracteres (E2, E3). [FR-001][FR-007]"""
        return normalizar_texto(self.cleaned_data["resumo"])

    def clean_link(self):
        """Vazio (opcional) ou iniciado por https://, até 500 caracteres (E4). [FR-001][FR-007]"""
        valor = normalizar_texto(self.cleaned_data.get("link", ""))
        if not valor:
            return ""
        if not valor.startswith("https://") or len(valor) > LIMITE_LINK:
            raise ValidationError(mensagens.LINK_HTTPS_500)
        return valor


class DadosTCCForm(FormularioSigtcc):
    """Área de Interesse e de 1 a 5 Palavras-Chave, liberadas depois da Proposta salva (FR-004).

    Cada Palavra-Chave tem sua própria caixa (até 5, E6); nenhuma pode repetir (MF-03,
    Clarifications). [US-13][RBN-CAD-08.1][FR-004][FR-007]
    """

    area_interesse = forms.ModelChoiceField(
        label="Área de Interesse",
        queryset=AreasInteresse.objects.order_by("ari_nome"),
        required=False,
        empty_label="Selecione…",
    )
    palavra_chave_1 = forms.CharField(
        label="Palavra-Chave 1",
        required=False,
        max_length=LIMITE_PALAVRA_CHAVE,
        widget=forms.TextInput(attrs={"maxlength": LIMITE_PALAVRA_CHAVE}),
    )
    palavra_chave_2 = forms.CharField(
        label="Palavra-Chave 2",
        required=False,
        max_length=LIMITE_PALAVRA_CHAVE,
        widget=forms.TextInput(attrs={"maxlength": LIMITE_PALAVRA_CHAVE}),
    )
    palavra_chave_3 = forms.CharField(
        label="Palavra-Chave 3",
        required=False,
        max_length=LIMITE_PALAVRA_CHAVE,
        widget=forms.TextInput(attrs={"maxlength": LIMITE_PALAVRA_CHAVE}),
    )
    palavra_chave_4 = forms.CharField(
        label="Palavra-Chave 4",
        required=False,
        max_length=LIMITE_PALAVRA_CHAVE,
        widget=forms.TextInput(attrs={"maxlength": LIMITE_PALAVRA_CHAVE}),
    )
    palavra_chave_5 = forms.CharField(
        label="Palavra-Chave 5",
        required=False,
        max_length=LIMITE_PALAVRA_CHAVE,
        widget=forms.TextInput(attrs={"maxlength": LIMITE_PALAVRA_CHAVE}),
    )

    def __init__(self, *args, somente_leitura=False, **kwargs):
        """Com somente_leitura, desabilita todos os campos (E7 a E9 da US-13). [FR-006]"""
        super().__init__(*args, **kwargs)
        if somente_leitura:
            for campo in self.fields.values():
                campo.disabled = True

    def clean(self):
        """De 1 a 5 Palavras-Chave (E5), nenhuma repetida entre as caixas preenchidas (MF-03).

        [US-13][RBN-CAD-08.1][FR-004][FR-007][Clarifications]
        """
        dados = super().clean()
        if self.errors:
            return dados
        valores = {}
        for indice in range(1, MAXIMO_PALAVRAS_CHAVE + 1):
            campo = f"palavra_chave_{indice}"
            valor = normalizar_texto(dados.get(campo, ""))
            dados[campo] = valor
            if valor:
                valores.setdefault(valor, []).append(campo)
        preenchidas = [campo for campos in valores.values() for campo in campos]
        if not preenchidas:
            self.add_error(None, mensagens.INFORME_PALAVRAS_CHAVE)
            return dados
        repetidas = {valor: campos for valor, campos in valores.items() if len(campos) > 1}
        if repetidas:
            for campos in repetidas.values():
                for campo in campos:
                    self.add_error(campo, mensagens.MF03_PALAVRA_CHAVE_REPETIDA)
            return dados
        dados["palavras_chave"] = list(valores.keys())
        return dados
