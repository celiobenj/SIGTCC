"""Formulário da publicação do artigo (spec 006).

O Link ou DOI reaproveita a regra de `forms_entregas.EnviarLinkForm` (obrigatório, `https://`,
até 500 caracteres, com `LINK_HTTPS_500`), sem uma terceira cópia (research R1, A9).

[US-46][RBN-CAD-12.1][FR-034]
"""

from django import forms

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import QualisCapes, StatusSubmissao
from sigtcc.apps.cadastro.forms_entregas import EnviarLinkForm

LIMITE_VEICULO = 150


class PublicacaoForm(EnviarLinkForm):
    """Veículo de Publicação (opcional, até 150; MO-19), Link ou DOI (obrigatório, `https://`,
    até 500), Estrato Qualis/CAPES (opcional: A1 a A4, B1 a B4, C) e Status de Submissão
    (opcional: Submetido, Em Revisão, Aceito, Publicado, Rejeitado). [US-46][RBN-CAD-12.1][FR-034]
    """

    field_order = ["veiculo", "link", "qualis", "status"]

    veiculo = forms.CharField(
        label="Veículo de Publicação",
        required=False,
        max_length=LIMITE_VEICULO,
        error_messages={"max_length": mensagens.MO19_VEICULO},
    )
    qualis = forms.ChoiceField(
        label="Estrato Qualis/CAPES",
        required=False,
        choices=[("", "Selecione…"), *QualisCapes.choices],
    )
    status = forms.ChoiceField(
        label="Status de Submissão",
        required=False,
        choices=[("", "Selecione…"), *StatusSubmissao.choices],
    )

    def __init__(self, *args, somente_leitura=False, **kwargs):
        """Rótulo do Link e, só leitura, campos desabilitados. [FR-034][FR-007]"""
        super().__init__(*args, **kwargs)
        self.fields["link"].label = "Link ou DOI"
        if somente_leitura:
            for campo in self.fields.values():
                campo.disabled = True
