"""Formulários da ata de orientação e do comentário (spec 006).

Limites do dicionário 3.5.8 e 3.5.9: Pauta e Metas até 2.000 caracteres, comentário até 1.000;
acima do limite, a MO-19; campo em branco, a M-14 (campo destacado). A Data do Encontro não pode
ser futura (comparada com `timezone.now().date()`, porque `USE_TZ=False`).

[US-19][RBN-CAD-11.1][RBN-CAD-11.2][FR-021][FR-024]
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.forms_turmas import FormularioSigtcc

LIMITE_PAUTA = 2000
LIMITE_METAS = 2000
LIMITE_COMENTARIO = 1000


class AtaForm(FormularioSigtcc):
    """Janela "Registrar ata de orientação" (e edição): Data do Encontro, Pauta Discutida e
    Metas Acordadas, todas obrigatórias. [US-19][RBN-CAD-11.1][FR-021]
    """

    data = forms.DateField(
        label="Data do Encontro",
        input_formats=["%d/%m/%Y", "%Y-%m-%d"],
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    )
    pauta = forms.CharField(
        label="Pauta Discutida",
        max_length=LIMITE_PAUTA,
        error_messages={"max_length": mensagens.MO19_PAUTA},
        widget=forms.Textarea(attrs={"rows": 5, "data-contador": LIMITE_PAUTA}),
    )
    metas = forms.CharField(
        label="Metas Acordadas",
        max_length=LIMITE_METAS,
        error_messages={"max_length": mensagens.MO19_METAS},
        widget=forms.Textarea(attrs={"rows": 5, "data-contador": LIMITE_METAS}),
    )

    def clean_data(self):
        """A Data do Encontro não pode ser futura (US-19 E3). [FR-021]"""
        data = self.cleaned_data["data"]
        if data > timezone.now().date():
            raise ValidationError(mensagens.DATA_ENCONTRO_FUTURA)
        return data


class ComentarioForm(FormularioSigtcc):
    """Comentário do Orientador ou do Coorientador abaixo da ata (até 1.000 caracteres).

    [US-19][RBN-CAD-11.2][FR-024]
    """

    texto = forms.CharField(
        label="Comentário",
        max_length=LIMITE_COMENTARIO,
        error_messages={"max_length": mensagens.MO19_COMENTARIO},
        widget=forms.Textarea(attrs={"rows": 4, "data-contador": LIMITE_COMENTARIO}),
    )
