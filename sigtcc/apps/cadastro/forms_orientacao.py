"""Formulários de orientação (spec 006): coorientador do NUCOMP ou externo.

O pedido de orientador usa só o campo "docente" do POST (lista pronta do service); aqui fica a
janela "Registrar coorientador", também usada no "Substituir" (US-45 D). Reaproveita os
validadores da spec 002 (nome, e-mail e instituição), sem cópia nova da regra (research R1).

[US-17][US-45][RBN-CAD-10.1][RBN-CAD-10.3]
"""

from django import forms
from django.core.exceptions import ValidationError

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.forms_contas import (
    validar_email_qualquer,
    validar_instituicao,
    validar_nome_completo,
)
from sigtcc.apps.cadastro.forms_turmas import FormularioSigtcc

DOCENTE = "docente"
EXTERNO = "externo"


class CoorientadorForm(FormularioSigtcc):
    """Tipo (Docente do NUCOMP ou Externo ao NUCOMP), Docente, Nome Completo (obrigatório, só
    letras, acentos e espaços, até 150), E-mail (opcional, nome@domínio, até 100) e Instituição de
    Origem (opcional, até 150). [US-45][RBN-CAD-10.3][FR-028]
    """

    tipo = forms.ChoiceField(
        label="Tipo",
        choices=((DOCENTE, "Docente do NUCOMP"), (EXTERNO, "Externo ao NUCOMP")),
    )
    docente = forms.TypedChoiceField(label="Docente", coerce=int, required=False, empty_value=None)
    nome = forms.CharField(label="Nome Completo", required=False, max_length=150)
    email = forms.CharField(label="E-mail", required=False, max_length=100)
    instituicao = forms.CharField(label="Instituição de Origem", required=False, max_length=150)

    def __init__(self, *args, docentes=(), **kwargs):
        """`docentes`: pares (id, rótulo) já filtrados pelo service (D8). [FR-028]

        [US-45][RBN-CAD-10.3]
        """
        super().__init__(*args, **kwargs)
        self.fields["docente"].choices = [("", "Selecione um docente…"), *docentes]
        self.fields["docente"].help_text = "O docente recebe um convite para aceitar ou recusar."

    def clean(self):
        """Campos obrigatórios por tipo e validadores da spec 002. [US-45 E2][FR-028]"""
        dados = super().clean()
        if dados.get("tipo") == DOCENTE:
            if not dados.get("docente"):
                self.add_error("docente", mensagens.M14_CAMPO_OBRIGATORIO)
            return dados
        if not (dados.get("nome") or "").strip():
            self.add_error("nome", mensagens.M14_CAMPO_OBRIGATORIO)
        else:
            try:
                dados["nome"] = validar_nome_completo(dados["nome"])
            except ValidationError as erro:
                self.add_error("nome", erro)
        if (dados.get("email") or "").strip():
            try:
                dados["email"] = validar_email_qualquer(dados["email"])
            except ValidationError as erro:
                self.add_error("email", erro)
        else:
            dados["email"] = None
        if (dados.get("instituicao") or "").strip():
            try:
                dados["instituicao"] = validar_instituicao(dados["instituicao"])
            except ValidationError as erro:
                self.add_error("instituicao", erro)
        else:
            dados["instituicao"] = None
        return dados
