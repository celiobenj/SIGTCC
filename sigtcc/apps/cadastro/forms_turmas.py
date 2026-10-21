"""Formulários de turmas e alunos (spec 004; research B18).

Diferente do primeiro acesso (spec 003, Q12), aqui todos os erros por campo aparecem.

[US-07][US-08][US-09][FR-002][FR-011][FR-016][FR-020][FR-023][FR-024]
"""

import re
import unicodedata

from django import forms
from django.core.exceptions import ValidationError

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import DescricaoTurma, DiaSemana
from sigtcc.apps.cadastro.mensagens import M14_CAMPO_OBRIGATORIO
from sigtcc.apps.cadastro.models import Cursos, Turmas

LIMITE_JUSTIFICATIVA = 500
_ESPACOS = re.compile(r"\s+")


def normalizar_texto(valor):
    """NFC, sem espaços nas pontas, espaços e quebras de linha repetidos viram um espaço.

    [US-08][US-09][RBN-CAD-05.1][RBN-CAD-05.4][B18][m2][m9]
    """
    if valor is None:
        return ""
    return _ESPACOS.sub(" ", unicodedata.normalize("NFC", str(valor))).strip()


def tem_caractere_de_controle(valor):
    """Algum caractere de controle (categoria Unicode C), depois da normalização. [m9]"""
    return any(unicodedata.category(c).startswith("C") for c in valor)


def validar_justificativa(valor):
    """Justificativa obrigatória, até 500 caracteres, sem caracteres de controle.

    Vazia, só com espaços, acima de 500 ou com caractere de controle →
    "Informe uma justificativa de até 500 caracteres".
    [US-09][RBN-CAD-05.4][RBN-CAD-05.6][RBN-CAD-08.4][FR-020][FR-023][FR-024][m9]
    """
    texto = normalizar_texto(valor)
    if not texto or len(texto) > LIMITE_JUSTIFICATIVA or tem_caractere_de_controle(texto):
        raise ValidationError(mensagens.JUSTIFICATIVA_500)
    return texto


class FormularioSigtcc(forms.Form):
    """Base dos formulários da spec 004: campo obrigatório com a M-14 e todos os erros por campo.

    [FR-002][M-14][B18]
    """

    use_required_attribute = False

    def __init__(self, *args, **kwargs):
        """Usa a M-14 como mensagem de campo obrigatório. [FR-002][M-14]"""
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.error_messages["required"] = M14_CAMPO_OBRIGATORIO


# =============================================================================================
# Turma (US-07; RBN-CAD-04.1 e 04.3; research B3)
# =============================================================================================

CODIGO_DISCIPLINA = re.compile(r"[A-Z0-9]{1,20}")
IDENTIFICADOR = re.compile(r"[A-Z0-9_]{1,30}")
ANO = re.compile(r"[1-9]\d{3}")
LIMITE_LOCAL = 100


def identificador_em_uso(identificador, exceto=None):
    """Outra turma já usa o Identificador. O banco também garante (spec 001); o serviço
    trata a corrida (m3). [US-07][RBN-CAD-04.1][FR-001]
    """
    turmas = Turmas.objects.filter(tur_identificador=identificador)
    if exceto is not None:
        turmas = turmas.exclude(pk=exceto.pk)
    return turmas.exists()


class TurmaForm(FormularioSigtcc):
    """Cadastro e edição da turma: todos os campos do RBN-CAD-04.1; Descrição e Curso travados na
    turma que tem ou já teve aluno (Q15).
    [US-07][RBN-CAD-04.1][RBN-CAD-04.3][FR-001][FR-002][FR-005][Q15]
    """

    codigo_disciplina = forms.CharField(
        label="Código da Disciplina", widget=forms.TextInput(attrs={"maxlength": 20})
    )
    descricao = forms.ChoiceField(label="Descrição", choices=DescricaoTurma.choices)
    identificador = forms.CharField(
        label="Identificador", widget=forms.TextInput(attrs={"maxlength": 30})
    )
    ano = forms.CharField(
        label="Ano", widget=forms.TextInput(attrs={"inputmode": "numeric", "maxlength": 4})
    )
    semestre = forms.ChoiceField(label="Semestre", choices=(("1", "1"), ("2", "2")))
    dia_semana = forms.ChoiceField(label="Dia da Semana", choices=DiaSemana.choices)
    hora_inicio = forms.TimeField(
        label="Horário de Início",
        input_formats=["%H:%M"],
        widget=forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
    )
    hora_termino = forms.TimeField(
        label="Horário de Término",
        input_formats=["%H:%M"],
        widget=forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
    )
    local = forms.CharField(
        label="Local",
        help_text="Sala ou laboratório da aula (até 100 caracteres)",
        widget=forms.TextInput(attrs={"maxlength": LIMITE_LOCAL}),
    )
    curso = forms.ModelChoiceField(
        label="Curso", queryset=Cursos.objects.order_by("cur_nome"), empty_label=None
    )

    def __init__(self, *args, turma=None, travar_descricao_e_curso=False, **kwargs):
        """Guarda a turma em edição; com a trava, Descrição e Curso ficam desabilitados (Q15)."""
        super().__init__(*args, **kwargs)
        self.turma = turma
        if travar_descricao_e_curso:
            self.fields["descricao"].disabled = True
            self.fields["curso"].disabled = True

    def clean_codigo_disciplina(self):
        """Só letras maiúsculas e números, até 20 (MT-01). [RBN-CAD-04.1]"""
        valor = normalizar_texto(self.cleaned_data["codigo_disciplina"])
        if not CODIGO_DISCIPLINA.fullmatch(valor):
            raise ValidationError(mensagens.MT01_CODIGO_DISCIPLINA)
        return valor

    def clean_identificador(self):
        """Letras maiúsculas, números e _, até 30 (MT-02), único (MT-03). [RBN-CAD-04.1]"""
        valor = normalizar_texto(self.cleaned_data["identificador"])
        if not IDENTIFICADOR.fullmatch(valor):
            raise ValidationError(mensagens.MT02_IDENTIFICADOR_FORMATO)
        if identificador_em_uso(valor, exceto=self.turma):
            raise ValidationError(mensagens.MT03_IDENTIFICADOR_REPETIDO)
        return valor

    def clean_ano(self):
        """Exatamente 4 dígitos, sem zero à esquerda (MT-04; m1). [RBN-CAD-04.1]"""
        valor = normalizar_texto(self.cleaned_data["ano"])
        if not ANO.fullmatch(valor):
            raise ValidationError(mensagens.MT04_ANO)
        return valor

    def clean_local(self):
        """Texto livre até 100, sem caractere de controle (MT-05; m9). [RBN-CAD-04.1]"""
        valor = normalizar_texto(self.cleaned_data["local"])
        if not valor:
            raise ValidationError(M14_CAMPO_OBRIGATORIO)
        if len(valor) > LIMITE_LOCAL or tem_caractere_de_controle(valor):
            raise ValidationError(mensagens.MT05_LOCAL)
        return valor

    def clean(self):
        """Término posterior ao início (texto da US-07). [RBN-CAD-04.1][FR-002]"""
        dados = super().clean()
        inicio, termino = dados.get("hora_inicio"), dados.get("hora_termino")
        if inicio and termino and termino <= inicio:
            self.add_error("hora_termino", mensagens.HORARIO_TERMINO)
        return dados
