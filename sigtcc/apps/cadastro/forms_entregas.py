"""Formulários das entregas da turma do app cadastro (spec 005).

Cadastro de entrega (US-43), envio do link (US-15, US-29) e devolução para ajuste da Versão
Final (US-44).

[US-15][US-29][US-43][US-44][RBN-CAD-09.1 a 09.6][research C1]
"""

from datetime import datetime, time

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import DescricaoTurma, TipoEntrega
from sigtcc.apps.cadastro.forms_turmas import FormularioSigtcc, normalizar_texto

LIMITE_TITULO_ENTREGA = 100
LIMITE_INSTRUCAO = 1000
LIMITE_LINK_ENTREGA = 500

# Tipos permitidos por etapa da turma (fluxo alternativo A da US-43; FR-013): TCC 1 não tem
# Versão Final, TCC 2 não tem Proposta — "Outra" entra nas duas.
_TIPOS_TCC_1 = (TipoEntrega.PROPOSTA, TipoEntrega.DOCUMENTO_PARA_DEFESA, TipoEntrega.OUTRA)
_TIPOS_TCC_2 = (TipoEntrega.DOCUMENTO_PARA_DEFESA, TipoEntrega.VERSAO_FINAL, TipoEntrega.OUTRA)


class CadastroEntregaForm(FormularioSigtcc):
    """Cadastro de uma entrega (`Turmas_Marcos`) na aba Atividades da turma: Tipo restrito pela
    etapa (FR-013), Título (até 100 caracteres), Instruções opcionais (até 1.000 caracteres) e
    Data Limite não anterior à data do cadastro (E2, Cenário 8 da US-43 original).

    [US-43][RBN-CAD-09.1][FR-013][research C6]
    """

    tipo = forms.ChoiceField(label="Tipo", choices=TipoEntrega.choices)
    titulo = forms.CharField(
        label="Título",
        max_length=LIMITE_TITULO_ENTREGA,
        widget=forms.TextInput(attrs={"maxlength": LIMITE_TITULO_ENTREGA}),
    )
    instrucao = forms.CharField(
        label="Instruções",
        max_length=LIMITE_INSTRUCAO,
        required=False,
        help_text=f"Opcional, até {LIMITE_INSTRUCAO} caracteres",
        widget=forms.Textarea(attrs={"rows": 4, "maxlength": LIMITE_INSTRUCAO}),
    )
    data_limite = forms.DateField(
        label="Data Limite",
        help_text="O prazo vale até 23:59 do dia informado",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def __init__(self, *args, turma=None, **kwargs):
        """Restringe a lista Tipo pela etapa da turma (TCC 1 ou TCC 2; fluxo alternativo A).

        [US-43][FR-013]
        """
        super().__init__(*args, **kwargs)
        self.turma = turma
        tipos = (
            _TIPOS_TCC_1
            if turma is None or turma.tur_descricao == DescricaoTurma.TCC_1
            else _TIPOS_TCC_2
        )
        self.fields["tipo"].choices = [(tipo.value, tipo.label) for tipo in tipos]

    def clean_titulo(self):
        """Obrigatório, até 100 caracteres (E2). [FR-013]"""
        return normalizar_texto(self.cleaned_data["titulo"])

    def clean_instrucao(self):
        """Opcional, até 1.000 caracteres (E2). [FR-013]"""
        return normalizar_texto(self.cleaned_data.get("instrucao", ""))

    def clean_data_limite(self):
        """Não anterior à data do cadastro (E2, Cenário 8); vale até 23:59 desse dia (devolve a
        data e a hora completas, já no fim do dia, para `services_entregas.cadastrar_entrega`).
        [US-43][FR-013][MF-06][research C6]
        """
        valor = self.cleaned_data["data_limite"]
        if valor < timezone.now().date():
            raise ValidationError(mensagens.MF06_DATA_LIMITE_ANTERIOR_A_HOJE)
        return datetime.combine(valor, time(23, 59, 59))


class EnviarLinkForm(FormularioSigtcc):
    """Link de envio ou substituição de uma entrega (US-15, passo 4): obrigatório, iniciado por
    `https://`, até 500 caracteres — vazio, formato errado ou tamanho excedido mostram a mesma
    mensagem exata (E2/Cenário 7 do `spec.md`), por isso o campo é `required=False` no Django (que
    mostraria "Campo obrigatório") e a obrigatoriedade é conferida em `clean_link` junto com o
    resto, com `LINK_HTTPS_500`.
    [US-15][RBN-CAD-09.2][FR-018][FR-019]
    """

    link = forms.CharField(
        label="Link",
        required=False,
        widget=forms.TextInput(attrs={"maxlength": LIMITE_LINK_ENTREGA}),
    )

    def clean_link(self):
        """Obrigatório, iniciado por https://, até 500 caracteres (E2/Cenário 7). [FR-018]"""
        valor = normalizar_texto(self.cleaned_data.get("link", ""))
        if not valor or not valor.startswith("https://") or len(valor) > LIMITE_LINK_ENTREGA:
            raise ValidationError(mensagens.LINK_HTTPS_500)
        return valor
