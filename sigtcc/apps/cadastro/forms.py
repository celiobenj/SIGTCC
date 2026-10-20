"""Formulários do app cadastro (research A9).

[US-10][US-11][US-12][US-38][FR-003][Q12]
"""

from django import forms

from sigtcc.apps.cadastro.mensagens import M14_CAMPO_OBRIGATORIO


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
                primeiro = self._errors[nome]
                self._errors.clear()
                self._errors[nome] = primeiro[:1]
                return
        # Erro geral do formulário (sem campo): mantém só o primeiro.
        geral = self._errors.get(forms.forms.NON_FIELD_ERRORS)
        self._errors.clear()
        if geral:
            self._errors[forms.forms.NON_FIELD_ERRORS] = geral[:1]

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
