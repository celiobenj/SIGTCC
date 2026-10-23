"""Confere, caractere por caractere, os textos da Gestão de Contas (SC-002; FR-048).

Textos das US: contra docs/fonte/Historias_de_Usuario_v3_3.md. MC-01 a MC-13: contra a tabela
"Mensagens a validar com a PO" de specs/002-gestao-contas/spec.md.

[US-03][US-04][US-05][US-06][US-50][SC-002][FR-048]
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from sigtcc.apps.cadastro import mensagens as m

US = Path(settings.BASE_DIR) / "docs" / "fonte" / "Historias_de_Usuario_v3_3.md"
SPEC = Path(settings.BASE_DIR) / "specs" / "002-gestao-contas" / "spec.md"

# Textos fixos das US (os com campo variável são conferidos pelas partes fixas, abaixo).
TEXTOS_DAS_US = [
    m.DOCENTE_CADASTRADO,
    m.SECRETARIA_CADASTRADA,
    m.MEMBRO_CADASTRADO,
    m.DADOS_ATUALIZADOS,
    m.EMAIL_JA_CADASTRADO,
    m.EMAIL_INSTITUCIONAL_CONTAS,
    m.EMAIL_VALIDO,
    m.NOME_INVALIDO,
    m.OPCAO_INVALIDA,
    m.INSTITUICAO_INVALIDA,
    m.CURSO_JA_TEM_COORDENADOR,
    m.CURSO_JA_TEM_SECRETARIA,
    m.SO_DO_SEU_CURSO_CADASTRO,
    m.SO_DO_SEU_CURSO_ALTERACAO,
    m.NENHUM_REGISTRO,
    m.FALHA_AO_SALVAR,
    m.DOCENTE_INATIVADO,
    m.MOTIVO_COORDENADOR,
    m.FALHA_AO_PRORROGAR,
    m.ACESSO_EXPIRADO_US06,
    m.M02_ACESSO_NEGADO,
    m.M14_CAMPO_OBRIGATORIO,
    m.CADASTRAR_DOCENTE,
    m.NOVA_SECRETARIA,
    m.NOVO_MEMBRO_EXTERNO,
]

# Constantes com campo variável: (constante, como a US escreve o exemplo).
COM_CAMPO = [
    (m.CONFIRMAR_INATIVAR_DOCENTE.format(nome="Nome"), "Deseja inativar o docente Nome?"),
    (
        m.NAO_E_POSSIVEL_INATIVAR.format(motivos=m.MOTIVO_TCC_ATIVO.format(n="N")),
        "Não é possível inativar: o docente possui N orientandos ou coorientandos com TCC ativo",
    ),
    (
        m.MOTIVO_COORDENADOR + m.FIM_ALERTA_VINCULOS,
        "é Coordenador do curso. Encerre ou transfira esses vínculos primeiro",
    ),
    (m.ACESSO_PRORROGADO_ATE.format(data="DD/MM/AAAA"), "Acesso prorrogado até DD/MM/AAAA"),
]

MC = {
    "MC-01": m.MC01_CONFIRMAR_REATIVAR.format(nome="NOME"),
    "MC-02": m.MC02_DOCENTE_REATIVADO,
    "MC-03": m.MC03_CONFIRMAR_INATIVAR_SECRETARIA.format(nome="NOME"),
    "MC-04": m.MC04_SECRETARIA_INATIVADA,
    "MC-05": m.MC05_CONVITES.format(n="N"),
    "MC-06": m.MC06_BANCAS.format(n="N"),
    "MC-07": m.MC07_TURMAS.format(n="N"),
    "MC-08": m.DOCENTE_CADASTRADO,
    "MC-09": m.MC09_SEM_VALIDADE,
    "MC-10": m.MC10_STATUS_INCOMPATIVEL,
    "MC-11": m.MC11_SENHA_INCORRETA,
    "MC-12": m.MC12_TROCA_EMAIL_ENVIADA,
    "MC-13": m.MC13_FALHA_ENVIO_TROCA,
}

# Forma no singular (entre colchetes na tabela): o trecho entre colchetes precisa aparecer nela.
SINGULAR = {
    "MC-05": m.MC05_CONVITE_1,
    "MC-06": m.MC06_BANCA_1,
    "MC-07": m.MC07_TURMA_1,
}


def _linhas_mc():
    """Linhas "| MC-NN | situação | "texto" ... | origem | situação |" da spec."""
    linhas = {}
    for linha in SPEC.read_text(encoding="utf-8").splitlines():
        achado = re.match(r"\| (MC-\d\d) \| [^|]* \| (.*?) \|", linha)
        if achado:
            linhas[achado.group(1)] = achado.group(2)
    return linhas


class MensagensContasTest(SimpleTestCase):
    """SC-002: textos idênticos às US (v3.3) e à tabela MC da spec 002."""

    def test_textos_das_us(self):
        texto = US.read_text(encoding="utf-8")
        for constante in TEXTOS_DAS_US:
            with self.subTest(constante=constante):
                self.assertIn(constante, texto)
        for montado, exemplo in COM_CAMPO:
            with self.subTest(montado=montado):
                self.assertEqual(montado, exemplo)
                self.assertIn(exemplo, texto)

    def test_mensagens_mc_da_spec(self):
        linhas = _linhas_mc()
        self.assertEqual(sorted(linhas), sorted(MC))
        for chave, constante in MC.items():
            with self.subTest(mensagem=chave):
                primeiro = re.search(r'"([^"]+)"', linhas[chave]).group(1)
                self.assertEqual(constante, primeiro)

    def test_singular_dos_motivos(self):
        linhas = _linhas_mc()
        for chave, constante in SINGULAR.items():
            with self.subTest(mensagem=chave):
                trecho = re.search(r"\[([^\]]+)\]", linhas[chave]).group(1)
                self.assertIn(trecho, constante)
