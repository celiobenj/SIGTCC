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
from sigtcc.apps.cadastro.choices import StatusCoorientacao, StatusOrientacao
from sigtcc.apps.cadastro.models import Coorientacoes, Orientacoes, TCCs, Usuarios
from sigtcc.apps.defesa import mensagens
from sigtcc.apps.defesa.choices import FormatoSessao, PapelBanca

OBRIGATORIO = {"required": mensagens.CAMPO_OBRIGATORIO}


class TCCChoiceField(forms.ModelChoiceField):
    """Cada opção mostra o título do trabalho e o nome do aluno (US-21, passo 4).
    [US-21][RBN-DEF-01.1]
    """

    def label_from_instance(self, tcc):
        """ "Título — Aluno". [US-21][RBN-DEF-01.1]"""
        return f"{tcc.tcc_titulo} — {tcc.tcc_alu.alu.usu_nome}"


class SelectTCC(forms.Select):
    """Lista TCC com o Orientador (Presidente) e quem não pode estar na banca (orientador e
    coorientadores) em cada opção, para static/js/banca.js atualizar a tela sem nova consulta.
    [US-23][RBN-DEF-02.1][FR-007][FR-008]
    """

    def __init__(self, *args, **kwargs):
        """`orientacao` = {tcc_id: (nome do orientador, ids da orientação)}. [US-23]"""
        self.orientacao = {}
        super().__init__(*args, **kwargs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        """Acrescenta data-orientador e data-excluir à opção. [US-23][RBN-DEF-02.1]"""
        opcao = super().create_option(name, value, label, selected, index, subindex, attrs)
        chave = getattr(value, "value", value)
        if chave in self.orientacao:
            nome, excluir = self.orientacao[chave]
            opcao["attrs"]["data-orientador"] = nome
            opcao["attrs"]["data-excluir"] = ",".join(str(pk) for pk in sorted(excluir))
        return opcao


def orientacao_dos_tccs(tccs):
    """{tcc_id: (nome do orientador atual, ids do orientador e dos coorientadores ativos)}, em
    duas consultas. [US-23][RBN-DEF-02.1][FR-008]
    """
    dados = {}
    for ori in Orientacoes.objects.select_related("ori_doc__doc").filter(
        ori_tcc__in=tccs, ori_status=StatusOrientacao.ATIVA
    ):
        dados[ori.ori_tcc_id] = (ori.ori_doc.doc.usu_nome, {ori.ori_doc_id})
    for coo in Coorientacoes.objects.filter(
        coo_tcc__in=tccs, coo_status=StatusCoorientacao.ATIVA, coo_doc__isnull=False
    ):
        dados.setdefault(coo.coo_tcc_id, ("", set()))[1].add(coo.coo_doc_id)
    return dados


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


def campo_de_membro(rotulo, obrigatorio=True):
    """Lista de um papel da banca; o Suplente é opcional ("Sem suplente", US-23 A). As opções
    (candidatos_da_banca) entram no __init__ do formulário. Quem não está na lista (o orientador
    ou um coorientador, por requisição direta) recebe a mensagem da US-23 E4.
    [US-23][RBN-DEF-02.1][FR-008][FR-009]
    """
    return MembroChoiceField(
        label=rotulo,
        queryset=Usuarios.objects.none(),
        required=obrigatorio,
        empty_label="Selecione…" if obrigatorio else "Sem suplente",
        widget=forms.Select(attrs={"class": "inp"}),
        error_messages={**OBRIGATORIO, "invalid_choice": mensagens.AVALIADORES_DISTINTOS},
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
        widget=SelectTCC(attrs={"class": "inp", "data-tcc": ""}),
        error_messages=OBRIGATORIO,
    )
    primeiro_avaliador = campo_de_membro("1º Avaliador")
    segundo_avaliador = campo_de_membro("2º Avaliador")
    suplente = campo_de_membro("Suplente", obrigatorio=False)

    field_order = ["tcc", "data", "h_inicio", "formato", "local", "link"]

    def __init__(self, *args, tccs, **kwargs):
        """`tccs`: os TCCs elegíveis que o usuário pode agendar (services_defesa.tccs_elegiveis),
        já limitados à turma ou ao orientando quando a tela de origem pede (fluxo A).
        [US-21][RBN-DEF-01.1][RBN-DEF-01.3]
        """
        super().__init__(*args, **kwargs)
        self.fields["tcc"].queryset = tccs
        self.orientacao = orientacao_dos_tccs(tccs)
        self.fields["tcc"].widget.orientacao = self.orientacao
        candidatos = candidatos_da_banca()
        if len(self.orientacao) == 1 and tccs.count() == 1:
            # Um só TCC (tela de orientandos): as listas já saem sem a orientação (US-23 E4).
            candidatos = candidatos.exclude(pk__in=next(iter(self.orientacao.values()))[1])
        for campo in CAMPOS_DA_BANCA:
            self.fields[campo].queryset = candidatos
            self.fields[campo].widget.attrs["data-banca"] = campo

    def presidente(self):
        """Nome do Orientador (Presidente) do TCC escolhido (ou do único da lista), para o campo
        somente leitura; o JavaScript atualiza ao trocar o TCC. [US-23][RBN-DEF-02.1][FR-007]
        """
        valor = self["tcc"].value()
        if not valor and len(self.orientacao) == 1:
            return next(iter(self.orientacao.values()))[0]
        try:
            return self.orientacao.get(int(valor), ("", None))[0]
        except (TypeError, ValueError):
            return ""

    def dados_banca(self):
        """Banca no formato de services_defesa.agendar. [US-23][RBN-DEF-02.1]"""
        return {campo: self.cleaned_data.get(campo) for campo in CAMPOS_DA_BANCA}


# Campos da banca no formulário, na ordem da tela, com o papel de cada um. [US-23][RBN-DEF-02.1]
CAMPOS_DA_BANCA = {
    "primeiro_avaliador": PapelBanca.PRIMEIRO_AVALIADOR,
    "segundo_avaliador": PapelBanca.SEGUNDO_AVALIADOR,
    "suplente": PapelBanca.SUPLENTE,
}


class JustificativaField(forms.CharField):
    """Justificativa obrigatória, até 500 caracteres, com a mensagem das US-23 E6 e US-24 E3.
    [US-23][US-24][RBN-DEF-02.2][RBN-DEF-02.4][RBN-DEF-03.3]
    """

    def __init__(self, **kwargs):
        """Textarea com o limite de 500. [US-23][US-24]"""
        super().__init__(
            label="Justificativa",
            widget=forms.Textarea(attrs={"class": "inp", "rows": 3, "maxlength": 500}),
            error_messages={"required": mensagens.JUSTIFICATIVA},
            **kwargs,
        )

    def clean(self, valor):
        """Mais de 500 caracteres: a mesma mensagem. [US-23][US-24]"""
        valor = super().clean(valor)
        if len(valor) > 500:
            raise forms.ValidationError(mensagens.JUSTIFICATIVA)
        return valor


class AlterarBancaForm(forms.Form):
    """ "Alterar banca" (US-23 C): Presidente bloqueado, 1º e 2º Avaliador, Suplente e
    Justificativa; as listas já saem sem o orientador e os coorientadores do TCC.
    [US-23][RBN-DEF-02.4][FR-011][FR-012]
    """

    primeiro_avaliador = campo_de_membro("1º Avaliador")
    segundo_avaliador = campo_de_membro("2º Avaliador")
    suplente = campo_de_membro("Suplente", obrigatorio=False)
    justificativa = JustificativaField()

    def __init__(self, *args, sessao, banca, **kwargs):
        """`banca` = composição atual ({papel: Usuarios}), para os valores iniciais.
        [US-23][RBN-DEF-02.4]
        """
        kwargs.setdefault(
            "initial", {campo: banca.get(papel) for campo, papel in CAMPOS_DA_BANCA.items()}
        )
        super().__init__(*args, **kwargs)
        orientacao = orientacao_dos_tccs([sessao.def_tcc]).get(sessao.def_tcc_id, ("", set()))
        self.presidente = banca.get(PapelBanca.ORIENTADOR_PRESIDENTE)
        candidatos = candidatos_da_banca().exclude(pk__in=orientacao[1])
        for campo in CAMPOS_DA_BANCA:
            self.fields[campo].queryset = candidatos
            self.fields[campo].widget.attrs["data-banca"] = campo

    def nova_banca(self):
        """{papel: Usuarios} para services_defesa.alterar_banca. [US-23][RBN-DEF-02.4]"""
        return {papel: self.cleaned_data.get(campo) for campo, papel in CAMPOS_DA_BANCA.items()}


class AcionarSuplenteForm(forms.Form):
    """ "Acionar suplente" (US-23 D): Avaliador Substituído (1º ou 2º) e Justificativa.
    [US-23][RBN-DEF-02.2][FR-013]
    """

    papel_substituido = forms.ChoiceField(
        label="Avaliador Substituído",
        widget=forms.Select(attrs={"class": "inp"}),
        error_messages=OBRIGATORIO,
    )
    justificativa = JustificativaField()

    def __init__(self, *args, banca, **kwargs):
        """Opções com o nome do titular de cada papel. [US-23][RBN-DEF-02.2]"""
        super().__init__(*args, **kwargs)
        self.fields["papel_substituido"].choices = [("", "Selecione…")] + [
            (papel, f"{papel} — {banca[papel].usu_nome}")
            for papel in (PapelBanca.PRIMEIRO_AVALIADOR, PapelBanca.SEGUNDO_AVALIADOR)
        ]
