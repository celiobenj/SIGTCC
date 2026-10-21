"""Textos exatos das mensagens da feature 004 (SC-002): constantes de mensagens.py contra as US-07,
08 e 09 e contra a tabela "Mensagens a validar com a PO" da spec 004.

[SC-002][FR-029][US-07][US-08][US-09]
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.tests.test_mensagens import _texto_corrido

FONTE = Path(settings.BASE_DIR) / "docs" / "fonte"
SPEC = Path(settings.BASE_DIR) / "specs" / "004-turmas-alunos" / "spec.md"

# Textos e rótulos copiados das US-07, 08 e 09 (docs/fonte/Historias_de_Usuario_v3_2.md).
TEXTOS_DAS_US = (
    "TURMA_CADASTRADA",
    "HORARIO_TERMINO",
    "TURMA_COM_ALUNOS",
    "ARQUIVAR_TCC_ATIVO",
    "ARQUIVAR_SESSAO_ATIVA",
    "ARQUIVAR_VERSAO_FINAL",
    "ALUNO_MATRICULADO",
    "ALUNO_JA_NA_TURMA",
    "ARQUIVO_FORA_DO_MODELO",
    "ALUNO_EXCLUIDO",
    "JUSTIFICATIVA_500",
    "SELECIONE_STATUS",
    "ALUNO_TEM_PROPOSTA",
    "NOVA_TURMA",
    "EDITAR",
    "EXCLUIR",
    "ARQUIVAR",
    "MATRICULAR_ALUNOS",
    "MATRICULA_INDIVIDUAL",
    "IMPORTAR_ARQUIVO",
    "CONFIRMAR_IMPORTACAO",
    "TRANSFERIR",
    "EXCLUIR_DA_TURMA",
    "ENCERRAR_PARTICIPACAO",
    "CONFIRMAR",
)

# Campos das constantes ↔ campos em maiúsculas da tabela da spec.
CAMPOS = {
    "{identificador}": "IDENTIFICADOR",
    "{justificativa}": "JUSTIFICATIVA",
    "{curso_aluno}": "CURSO DO ALUNO",
    "{curso_turma}": "CURSO DA TURMA",
    "{origem}": "ORIGEM",
    "{destino}": "DESTINO",
    "{status}": "STATUS",
    "{nome}": "NOME",
    "{tipo}": "TIPO",
    "{n}": "N",
    "{r}": "R",
    "{c}": "C",
}
NUMEROS = [n for n in range(1, 33) if n != 20]


def _mensagens_da_spec():
    """{"MT-01": texto, ...}: primeiro texto entre aspas da 3ª coluna da tabela da spec 004."""
    textos = {}
    for linha in SPEC.read_text(encoding="utf-8").splitlines():
        achado = re.match(r'^\| (MT-\d{2}) \| [^|]* \| "((?:[^"\\]|\\.)*)"', linha)
        if achado:
            textos[achado.group(1)] = achado.group(2).replace('\\"', '"')
    return textos


def _com_campos_da_spec(texto):
    for campo, nome in CAMPOS.items():
        texto = texto.replace(campo, nome)
    return texto


class MensagensTurmasTest(SimpleTestCase):
    """SC-002: cada mensagem é idêntica, caractere por caractere, à fonte. [SC-002]"""

    def test_textos_das_us(self):
        """Cada texto das US-07, 08 e 09 aparece entre aspas no documento das US."""
        historias = _texto_corrido(FONTE / "Historias_de_Usuario_v3_2.md")
        for nome in TEXTOS_DAS_US:
            texto = getattr(mensagens, nome)
            with self.subTest(constante=nome):
                self.assertIn(f'"{texto}', historias)

    def test_tabela_da_spec_tem_mt01_a_mt32_sem_a_mt20(self):
        self.assertEqual(sorted(_mensagens_da_spec()), [f"MT-{n:02d}" for n in NUMEROS])

    def test_mensagens_provisorias_da_spec(self):
        """MT-01 a MT-32 (sem a MT-20) iguais à tabela da spec, com os campos trocados."""
        da_spec = _mensagens_da_spec()
        for numero in NUMEROS:
            nomes = [n for n in dir(mensagens) if n.startswith(f"MT{numero:02d}_")]
            with self.subTest(mensagem=f"MT-{numero:02d}"):
                self.assertEqual(len(nomes), 1)
                texto = _com_campos_da_spec(getattr(mensagens, nomes[0]))
                self.assertEqual(texto, da_spec[f"MT-{numero:02d}"])

    def test_mt20_reservada(self):
        self.assertFalse([n for n in dir(mensagens) if n.startswith("MT20_")])
