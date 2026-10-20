"""Formulários do app cadastro (research A9).

[US-10][US-11][US-12][US-38][FR-003][Q12]
"""

import re

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from sigtcc.apps.cadastro import mensagens, services
from sigtcc.apps.cadastro.mensagens import M14_CAMPO_OBRIGATORIO
from sigtcc.apps.cadastro.validators import RegraSenhaSigtcc

MATRICULA = re.compile(r"\d{10}")
DOMINIO_UEA = "@uea.edu.br"


class FormularioPrimeiroErro(forms.Form):
    """Formulário que mostra só o erro do primeiro campo com problema (spec Q12).

    Os campos são validados na ordem declarada; dentro de um campo, a ordem é formato,
    existência e status (cada formulário filho segue essa ordem no seu clean_<campo>). Campo
    obrigatório vazio usa a M-14. Uso opcional nas outras features (contrato §1).
    [FR-003][Q12][M-14]
    """

    # Sem o atributo "required" no HTML: o navegador não bloqueia o envio e a mensagem exibida é
    # a da spec (M-14 ou o texto da US), não a do navegador.
    use_required_attribute = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.error_messages["required"] = M14_CAMPO_OBRIGATORIO

    def full_clean(self):
        """Valida e mantém, em errors, só o primeiro campo com erro, na ordem dos campos."""
        super().full_clean()
        if not self._errors:
            return
        for nome in self.fields:
            if nome in self._errors:
                primeiro = self._errors[nome].data[:1]
                self._errors.clear()
                self._errors[nome] = self.error_class(primeiro, renderer=self.renderer)
                return
        # Erro geral do formulário (sem campo): mantém só o primeiro.
        geral = self._errors.get(forms.forms.NON_FIELD_ERRORS)
        self._errors.clear()
        if geral:
            self._errors[forms.forms.NON_FIELD_ERRORS] = self.error_class(
                geral.data[:1], error_class="nonfield", renderer=self.renderer
            )

    def primeiro_erro(self):
        """Texto do único erro que sobrou, ou "" se o formulário é válido."""
        for lista in self.errors.values():
            return lista[0]
        return ""


class FormularioLogin(forms.Form):
    """Credencial, senha (mascarada) e o next oculto. A ordem das verificações e as mensagens
    ficam em services.autenticar (FR-008); este formulário só desenha a tela.
    [US-11][RBN-CAD-06.4][FR-007]
    """

    use_required_attribute = False

    credencial = forms.CharField(
        label="Credencial",
        max_length=100,
        required=False,
        help_text="Matrícula (Aluno) ou e-mail",
        widget=forms.TextInput(attrs={"autocomplete": "username", "autofocus": True}),
    )
    senha = forms.CharField(
        label="Senha",
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )
    next = forms.CharField(required=False, widget=forms.HiddenInput)


def _email_no_formato(email):
    """E-mail no formato nome@domínio, com até 100 caracteres (FR-001). [US-10][RBN-CAD-06.2]"""
    if not email or len(email) > 100:
        return False
    try:
        validate_email(email)
    except ValidationError:
        return False
    return True


def email_institucional(email):
    """E-mail no formato nome@uea.edu.br, com até 100 caracteres. [US-10][RBN-CAD-06.1]"""
    return _email_no_formato(email) and email.lower().endswith(DOMINIO_UEA)


class PrimeiroAcessoAlunoForm(FormularioPrimeiroErro):
    """Primeiro acesso do Aluno: Matrícula e E-mail Institucional (FR-001, FR-003; Q12).

    Matrícula: formato, existência (com turma) e status, nessa ordem. E-mail: formato e domínio
    e, no Aluno ainda sem e-mail, unicidade (Q15). Só o primeiro erro aparece.
    [US-10][RBN-CAD-06.1][FR-001][FR-003][Q2][Q12][Q15]
    """

    matricula = forms.CharField(
        label="Matrícula",
        widget=forms.TextInput(attrs={"inputmode": "numeric", "maxlength": 10}),
    )
    email = forms.CharField(
        label="E-mail Institucional",
        widget=forms.EmailInput(attrs={"maxlength": 100, "autocomplete": "email"}),
    )

    conta = None

    def clean_matricula(self):
        matricula = self.cleaned_data["matricula"].strip()
        if not MATRICULA.fullmatch(matricula):
            raise ValidationError(mensagens.MATRICULA_FORMATO)
        conta = services.conta_do_aluno_para_primeiro_acesso(matricula)
        if conta is None:
            raise ValidationError(mensagens.DADOS_NAO_ENCONTRADOS)
        recusa = services.recusa_por_status(conta)
        if recusa:
            raise ValidationError(recusa)
        self.conta = conta
        return matricula

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if not email_institucional(email):
            raise ValidationError(mensagens.EMAIL_INSTITUCIONAL)
        if (
            self.conta is not None
            and not self.conta.usu_email
            and services.email_em_uso(email, exceto=self.conta)
        ):
            raise ValidationError(mensagens.EMAIL_DE_OUTRA_CONTA_ALUNO)
        return email


class PrimeiroAcessoEmailForm(FormularioPrimeiroErro):
    """Primeiro acesso de Docente, Secretaria ou Membro Externo: E-mail (FR-001, FR-003; Q8).

    [US-10][RBN-CAD-06.2][FR-001][FR-003][Q8][Q12]
    """

    email = forms.CharField(
        label="E-mail",
        widget=forms.EmailInput(attrs={"maxlength": 100, "autocomplete": "email"}),
    )

    conta = None

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if not _email_no_formato(email):
            raise ValidationError(mensagens.M10_EMAIL_INVALIDO)
        conta = services.conta_por_email_para_primeiro_acesso(email)
        if conta is None:
            raise ValidationError(mensagens.DADOS_NAO_ENCONTRADOS)
        recusa = services.recusa_por_status(conta)
        if recusa:
            raise ValidationError(recusa)
        self.conta = conta
        return email


class AtivacaoForm(FormularioPrimeiroErro):
    """Senha e Confirmação de Senha, mascaradas (FR-004). [US-10][RBN-CAD-06.3][Q17]"""

    senha = forms.CharField(
        label="Senha",
        help_text=mensagens.REGRA_SENHA,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    confirmacao = forms.CharField(
        label="Confirmação de Senha",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def clean_senha(self):
        senha = self.cleaned_data["senha"]
        RegraSenhaSigtcc().validate(senha)
        return senha

    def clean(self):
        dados = super().clean()
        senha, confirmacao = dados.get("senha"), dados.get("confirmacao")
        if senha and confirmacao is not None and senha != confirmacao:
            self.add_error("confirmacao", mensagens.SENHAS_NAO_CONFEREM)
        return dados


class AlterarSenhaForm(FormularioPrimeiroErro):
    """Senha Atual, Nova Senha e Confirmação da Nova Senha, mascaradas (FR-012).

    A senha atual é conferida no campo (ordem dos campos, Q12) e de novo no serviço, com a conta
    travada. [US-12][RBN-CAD-06.5][FR-012]
    """

    senha_atual = forms.CharField(
        label="Senha Atual",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )
    nova_senha = forms.CharField(
        label="Nova Senha",
        help_text=mensagens.REGRA_SENHA,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    confirmacao = forms.CharField(
        label="Confirmação da Nova Senha",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def __init__(self, usuario, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario

    def clean_senha_atual(self):
        senha = self.cleaned_data["senha_atual"]
        if not services.senha_atual_confere(self.usuario, senha):
            raise ValidationError(mensagens.SENHA_ATUAL_INCORRETA)
        return senha

    def clean_nova_senha(self):
        senha = self.cleaned_data["nova_senha"]
        RegraSenhaSigtcc().validate(senha)
        return senha

    def clean(self):
        dados = super().clean()
        nova, confirmacao = dados.get("nova_senha"), dados.get("confirmacao")
        if nova and confirmacao is not None and nova != confirmacao:
            self.add_error("confirmacao", mensagens.SENHAS_NAO_CONFEREM)
        return dados


class EsqueciSenhaForm(FormularioPrimeiroErro):
    """E-mail cadastrado para "Esqueci minha senha" (FR-013). [US-12][RBN-CAD-06.7][M-10]"""

    email = forms.CharField(
        label="E-mail cadastrado",
        widget=forms.EmailInput(attrs={"maxlength": 100, "autocomplete": "email"}),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if not _email_no_formato(email):
            raise ValidationError(mensagens.M10_EMAIL_INVALIDO)
        return email


class NovaSenhaForm(AtivacaoForm):
    """Nova Senha e Confirmação pelo link de redefinição, com a regra de FR-004 (FR-014).

    [US-12][RBN-CAD-06.7][FR-014]
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["senha"].label = "Nova Senha"
        self.fields["confirmacao"].label = "Confirmação da Nova Senha"
