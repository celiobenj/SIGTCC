"""Formulários do módulo de Defesa (spec 007). Validam formato e campos obrigatórios com as
mensagens exatas das US; as regras de negócio (quem agenda, banca, conflito) ficam em
services_defesa.

[US-21][US-23][RBN-DEF-01.1][RBN-DEF-02.1]
"""

from datetime import datetime

from django import forms
from django.core.validators import URLValidator
from django.db.models import Q
from django.utils import timezone

from sigtcc.apps.cadastro import services_contas
from sigtcc.apps.cadastro.models import TCCs, Usuarios
from sigtcc.apps.defesa import mensagens
from sigtcc.apps.defesa.choices import FormatoSessao

OBRIGATORIO = {"required": mensagens.CAMPO_OBRIGATORIO}


class TCCChoiceField(forms.ModelChoiceField):
    """Cada opção mostra o título do trabalho e o nome do aluno (US-21, passo 4).
    [US-21][RBN-DEF-01.1]
    """

    def label_from_instance(self, tcc):
        """ "Título — Aluno". [US-21][RBN-DEF-01.1]"""
        return f"{tcc.tcc_titulo} — {tcc.tcc_alu.alu.usu_nome}"


class MembroChoiceField(forms.ModelChoiceField):
    """Docente com a conta 'Ativa' ou Membro Externo (este marcado no rótulo).
    [US-23][RBN-DEF-02.1]
    """

    def label_from_instance(self, usuario):
        """Nome, com "(Membro Externo)" para quem é de fora do NUCOMP. [US-23][RBN-DEF-02.1]"""
        if hasattr(usuario, "membrosexternos"):
            return f"{usuario.usu_nome} (Membro Externo)"
        return usuario.usu_nome


def candidatos_da_banca():
    """Docentes 'Ativa' e Membros Externos (contrato §1 da spec 002), por nome. O orientador e os
    coorientadores do TCC são recusados por services_defesa.validar_banca (US-23 E4).
    [US-23][RBN-DEF-02.1][FR-008]
    """
    return (
        Usuarios.objects.filter(
            Q(docentes__in=services_contas.docentes_ativos())
            | Q(membrosexternos__in=services_contas.membros_externos_disponiveis())
        )
        .select_related("membrosexternos")
        .order_by("usu_nome", "usu_id")
    )


class DadosDaSessaoForm(forms.Form):
    """Data, Horário de Início, Formato da Sessão e Local ou Link da Videochamada (US-21 passos 6
    a 9; também no reagendamento, US-24 B). O campo do outro formato é descartado (fluxo B).
    [US-21][US-24][RBN-DEF-01.1][FR-001][FR-002][FR-004][FR-005]
    """

    data = forms.DateField(
        label="Data",
        widget=forms.DateInput(attrs={"type": "date", "class": "inp"}, format="%Y-%m-%d"),
        input_formats=["%Y-%m-%d", "%d/%m/%Y"],
        error_messages=OBRIGATORIO,
    )
    h_inicio = forms.TimeField(
        label="Horário de Início",
        widget=forms.TimeInput(attrs={"type": "time", "class": "inp"}, format="%H:%M"),
        input_formats=["%H:%M"],
        help_text="O sistema reserva 1 hora para a sessão.",
        error_messages=OBRIGATORIO,
    )
    formato = forms.ChoiceField(
        label="Formato da Sessão",
        choices=[("", "Selecione…"), *FormatoSessao.choices],
        widget=forms.Select(attrs={"class": "inp", "data-formato": ""}),
        error_messages=OBRIGATORIO,
    )
    local = forms.CharField(
        label="Local",
        required=False,
        strip=True,
        widget=forms.TextInput(
            attrs={"class": "inp", "placeholder": "A_12, Ludus, Laboratório LSI"}
        ),
    )
    link = forms.CharField(
        label="Link da Videochamada",
        required=False,
        strip=True,
        widget=forms.TextInput(attrs={"class": "inp", "placeholder": "https://meet.google.com/…"}),
    )

    def clean(self):
        """E3 a E6 da US-21: Local (Presencial) ou Link (Remota) obrigatório; data e horário
        posteriores ao momento atual; Local até 100 caracteres; Link https:// até 500.
        [US-21][RBN-DEF-01.1][FR-004][FR-005]
        """
        dados = super().clean()
        data, hora = dados.get("data"), dados.get("h_inicio")
        if data and hora and datetime.combine(data, hora) <= timezone.now():
            self.add_error("data", mensagens.DATA_NO_PASSADO)
        formato = dados.get("formato")
        if formato == FormatoSessao.PRESENCIAL:
            dados["link"] = None
            local = dados.get("local")
            if not local:
                self.add_error("local", mensagens.CAMPO_OBRIGATORIO)
            elif len(local) > 100:
                self.add_error("local", mensagens.MD08_LOCAL_LONGO)
        elif formato == FormatoSessao.REMOTA:
            dados["local"] = None
            link = dados.get("link")
            if not link:
                self.add_error("link", mensagens.CAMPO_OBRIGATORIO)
            elif not _link_valido(link):
                self.add_error("link", mensagens.LINK_INVALIDO)
        return dados

    def dados_basicos(self):
        """Dados no formato de services_defesa (agendar_sessao, reagendar). [US-21][US-24]"""
        return {
            chave: self.cleaned_data[chave]
            for chave in ("data", "h_inicio", "formato", "local", "link")
        }


def _link_valido(link):
    """Endereço https:// válido, com até 500 caracteres (US-21 E6). [US-21][RBN-DEF-01.1]"""
    if len(link) > 500 or not link.startswith("https://"):
        return False
    try:
        URLValidator(schemes=["https"])(link)
    except forms.ValidationError:
        return False
    return True


class AgendarForm(DadosDaSessaoForm):
    """ "Agendar sessão de defesa" (US-21) com a seção Banca examinadora (US-23): TCC só entre os
    elegíveis recebidos da view, avaliadores e Suplente opcional ("Sem suplente").
    [US-21][US-23][RBN-DEF-01.1][RBN-DEF-02.1][FR-001][FR-007][FR-008]
    """

    tcc = TCCChoiceField(
        label="TCC",
        queryset=TCCs.objects.none(),
        empty_label="Selecione…",
        widget=forms.Select(attrs={"class": "inp"}),
        error_messages=OBRIGATORIO,
    )
    primeiro_avaliador = MembroChoiceField(
        label="1º Avaliador",
        queryset=Usuarios.objects.none(),
        empty_label="Selecione…",
        widget=forms.Select(attrs={"class": "inp"}),
        error_messages=OBRIGATORIO,
    )
    segundo_avaliador = MembroChoiceField(
        label="2º Avaliador",
        queryset=Usuarios.objects.none(),
        empty_label="Selecione…",
        widget=forms.Select(attrs={"class": "inp"}),
        error_messages=OBRIGATORIO,
    )
    suplente = MembroChoiceField(
        label="Suplente",
        queryset=Usuarios.objects.none(),
        required=False,
        empty_label="Sem suplente",
        widget=forms.Select(attrs={"class": "inp"}),
    )

    field_order = ["tcc", "data", "h_inicio", "formato", "local", "link"]

    def __init__(self, *args, tccs, **kwargs):
        """`tccs`: os TCCs elegíveis que o usuário pode agendar (services_defesa.tccs_elegiveis),
        já limitados à turma ou ao orientando quando a tela de origem pede (fluxo A).
        [US-21][RBN-DEF-01.1][RBN-DEF-01.3]
        """
        super().__init__(*args, **kwargs)
        self.fields["tcc"].queryset = tccs
        candidatos = candidatos_da_banca()
        for campo in ("primeiro_avaliador", "segundo_avaliador", "suplente"):
            self.fields[campo].queryset = candidatos

    def dados_banca(self):
        """Banca no formato de services_defesa.agendar. [US-23][RBN-DEF-02.1]"""
        return {
            campo: self.cleaned_data.get(campo)
            for campo in ("primeiro_avaliador", "segundo_avaliador", "suplente")
        }
