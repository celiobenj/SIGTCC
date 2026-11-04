"""Formulários da avaliação da banca e do resultado (spec 008; research A4, A5, A6): os 9
critérios (formset fixo), a assinatura, o parecer e a confirmação da liberação.

As faixas de nota vêm de services_avaliacoes.FAIXAS; o que está liberado pelo status da sessão é
decidido no serviço (que também recusa por POST direto).

[US-25][US-26][US-27][RBN-DEF-05.1][RBN-DEF-05.2][RBN-DEF-06.3][RBN-DEF-06.4]
"""

import re
from decimal import Decimal, InvalidOperation

from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet, formset_factory

from sigtcc.apps.cadastro import services
from sigtcc.apps.defesa import mensagens, services_avaliacoes
from sigtcc.apps.defesa.choices import Conceito, Parecer

# Nota com uma casa decimal, com vírgula ou ponto (FR-008). [US-25][RBN-DEF-05.2]
_NOTA = re.compile(r"^\d{1,2}(?:[.,]\d)?$")


def formatar_nota(valor):
    """Nota com vírgula e uma casa ("7,5"), ou "". [US-25][RBN-DEF-05.2]"""
    if valor is None or valor == "":
        return ""
    return f"{Decimal(valor):.1f}".replace(".", ",")


class NotaField(forms.CharField):
    """Campo Nota: aceita "7,5" ou "7.5", uma casa, de 0,0 a 10,0; fora disso, a mensagem da
    US-25 E2. [US-25][RBN-DEF-05.2][FR-009]
    """

    def prepare_value(self, value):
        """Mostra a nota gravada com vírgula. [US-25][RBN-DEF-05.2]"""
        if isinstance(value, Decimal):
            return formatar_nota(value)
        return value

    def to_python(self, value):
        """Converte para Decimal com uma casa, ou None se vazio. [US-25][RBN-DEF-05.2]"""
        if isinstance(value, Decimal):
            return value
        texto = (value or "").strip()
        if not texto:
            return None
        if not _NOTA.match(texto):
            raise ValidationError(mensagens.NOTA_FORA_DA_FAIXA)
        try:
            nota = Decimal(texto.replace(",", ".")).quantize(Decimal("0.1"))
        except InvalidOperation:
            raise ValidationError(mensagens.NOTA_FORA_DA_FAIXA)
        if not Decimal("0") <= nota <= Decimal("10"):
            raise ValidationError(mensagens.NOTA_FORA_DA_FAIXA)
        return nota


class CriterioForm(forms.Form):
    """Uma linha do formulário Avaliação: Conceito, Nota e Observações (até 500). Vazio ou
    completo (MA-01; D4); nota na faixa do conceito (FR-009). Critério bloqueado pelo status ou
    avaliação só leitura: campos desabilitados (o valor postado é ignorado).
    [US-25][RBN-DEF-05.1][RBN-DEF-05.2][FR-008 a FR-013]
    """

    conceito = forms.ChoiceField(
        label="Conceito", required=False, choices=[("", "Selecione…"), *Conceito.choices]
    )
    nota = NotaField(
        label="Nota", required=False, widget=forms.TextInput(attrs={"inputmode": "decimal"})
    )
    observacoes = forms.CharField(
        label="Observações",
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={"rows": 2}),
        error_messages={"max_length": mensagens.MA02_OBSERVACOES_LONGAS},
    )

    def __init__(self, *args, criterio=None, bloqueado=False, **kwargs):
        """Guarda o critério e desabilita os campos quando bloqueado. [US-25][RBN-DEF-05.1]"""
        super().__init__(*args, **kwargs)
        self.criterio = criterio
        self.bloqueado = bloqueado
        for campo in self.fields.values():
            campo.disabled = bloqueado

    def clean(self):
        """Critério vazio ou com conceito e nota; nota na faixa. [US-25][RBN-DEF-05.2][FR-009]"""
        dados = super().clean()
        conceito, nota = dados.get("conceito"), dados.get("nota")
        if self.bloqueado or "nota" in self.errors or "observacoes" in self.errors:
            return dados
        if not conceito and nota is None:
            if dados.get("observacoes"):
                raise ValidationError(mensagens.MA01_CONCEITO_E_NOTA)
            return dados
        if not conceito:
            self.add_error("conceito", mensagens.MA01_CONCEITO_E_NOTA)
        elif nota is None:
            self.add_error("nota", mensagens.MA01_CONCEITO_E_NOTA)
        elif not services_avaliacoes.nota_na_faixa(conceito, nota):
            self.add_error("nota", mensagens.NOTA_FORA_DA_FAIXA)
        return dados

    def dados(self):
        """{conceito, nota, observacoes} limpos. [US-25][RBN-DEF-05.2]"""
        return {
            "conceito": self.cleaned_data.get("conceito") or "",
            "nota": self.cleaned_data.get("nota"),
            "observacoes": self.cleaned_data.get("observacoes") or "",
        }


class BaseCriteriosFormSet(BaseFormSet):
    """Formset fixo dos 9 critérios, na ordem da carga; cada formulário recebe o seu critério e
    se está bloqueado (Parte Oral antes da sessão; tudo quando só leitura).
    [US-25][RBN-DEF-05.1][RBN-DEF-05.2][research A4]
    """

    def __init__(self, *args, criterios=(), liberados=frozenset(), **kwargs):
        """Guarda os critérios e os liberados. [US-25][RBN-DEF-05.1]"""
        self.criterios = list(criterios)
        self.liberados = set(liberados)
        super().__init__(*args, prefix="cri", **kwargs)

    def get_form_kwargs(self, index):
        """Critério e bloqueio do formulário de cada linha. [US-25][RBN-DEF-05.1]"""
        criterio = (
            self.criterios[index] if index is not None and index < len(self.criterios) else None
        )
        return {
            "criterio": criterio,
            "bloqueado": criterio is None or criterio.pk not in self.liberados,
        }

    def linhas(self):
        """{cri_id: dados} dos critérios liberados (os bloqueados não vão ao serviço).
        [US-25][RBN-DEF-05.1][revisão I-01]
        """
        return {
            form.criterio.pk: form.dados()
            for form in self.forms
            if form.criterio is not None and not form.bloqueado
        }

    def marcar_pendentes(self, pendentes, mensagem):
        """Destaca os critérios apontados pelo serviço. [US-25][RBN-DEF-05.2][FR-019]"""
        for form in self.forms:
            if form.criterio is not None and form.criterio.pk in pendentes:
                campo = "conceito" if not form.cleaned_data.get("conceito") else "nota"
                form.add_error(campo, mensagem)


CriteriosFormSet = formset_factory(
    CriterioForm,
    formset=BaseCriteriosFormSet,
    extra=0,
    min_num=services_avaliacoes.TOTAL_DE_CRITERIOS,
    max_num=services_avaliacoes.TOTAL_DE_CRITERIOS,
    validate_min=True,
    validate_max=True,
)


class AssinaturaForm(forms.Form):
    """Seção Assinatura do Membro da Banca (US-26): Anexar imagem (PNG ou JPG, até 2 MB), usar a
    do perfil e Salvar esta imagem no meu perfil. O tamanho é conferido antes do tipo, para
    separar as mensagens da US-26 E2 e E3 (revisão M-09); as dimensões, no serviço (MA-14).
    [US-26][RBN-DEF-05.2][FR-015][FR-016][FR-017][FR-018]
    """

    arquivo = forms.FileField(
        label="Anexar imagem",
        required=False,
        widget=forms.ClearableFileInput(attrs={"accept": "image/png,image/jpeg"}),
    )
    usar_perfil = forms.BooleanField(label="Usar a assinatura do meu perfil", required=False)
    salvar_no_perfil = forms.BooleanField(label="Salvar esta imagem no meu perfil", required=False)

    tipo = None

    def clean_arquivo(self):
        """Até 2 MB (US-26 E2) e conteúdo PNG ou JPG com a extensão certa (US-26 E3).
        [US-26][RBN-DEF-05.2][FR-016]
        """
        arquivo = self.cleaned_data.get("arquivo")
        if not arquivo:
            return None
        if arquivo.size > services.TAMANHO_MAXIMO_ASSINATURA:
            raise ValidationError(mensagens.ASSINATURA_TAMANHO)
        self.tipo = services.tipo_da_assinatura(arquivo)
        if self.tipo is None:
            raise ValidationError(mensagens.ASSINATURA_FORMATO)
        return arquivo

    def assinatura(self):
        """A escolha do avaliador para o serviço. [US-26][RBN-DEF-05.2]"""
        return services_avaliacoes.Assinatura(
            arquivo=self.cleaned_data.get("arquivo"),
            tipo=self.tipo,
            usar_perfil=self.cleaned_data.get("usar_perfil", False),
            salvar_no_perfil=self.cleaned_data.get("salvar_no_perfil", False),
        )


class ParecerForm(forms.Form):
    """Registrar parecer (US-27, passos 6 e 7): Aprovado ou Aprovado com Correções; sem escolha,
    "Selecione o parecer da banca para continuar" (US-27 E3). [US-27][RBN-DEF-06.3][FR-025]
    """

    parecer = forms.ChoiceField(
        label="Parecer",
        choices=[(p.value, p.label) for p in (Parecer.APROVADO, Parecer.APROVADO_COM_CORRECOES)],
        widget=forms.RadioSelect,
        error_messages={
            "required": mensagens.SELECIONE_O_PARECER,
            "invalid_choice": mensagens.SELECIONE_O_PARECER,
        },
    )


class ConfirmarLiberacaoForm(forms.Form):
    """Confirmação de Liberar Resultado (MA-05): a nota final e o parecer mostrados, para o
    serviço conferir se mudaram antes de gravar (D10). [US-27][RBN-DEF-06.4][FR-027]
    """

    nota = forms.DecimalField(max_digits=3, decimal_places=1, widget=forms.HiddenInput)
    parecer = forms.ChoiceField(choices=Parecer.choices, widget=forms.HiddenInput)
