"""Textos exatos das mensagens da feature 005 (SC-006): constantes de mensagens.py contra as
US-13, 14, 15, 16, 29, 43 e 44 e contra a tabela "Mensagens a validar com a PO" da spec 005.

Mesmo padrão de test_mensagens_turmas.py (spec 004), lendo a versão das US em uso nesta feature
(`Historias_de_Usuario_v3_3.md`, citada no `spec.md`).

[SC-006][US-13][US-14][US-15][US-16][US-29][US-43][US-44]
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.tests.test_mensagens import _texto_corrido

FONTE = Path(settings.BASE_DIR) / "docs" / "fonte" / "Historias_de_Usuario_v3_3.md"
SPEC = Path(settings.BASE_DIR) / "specs" / "005-fluxo-do-tcc" / "spec.md"

# Textos copiados, caractere por caractere, das US desta feature (T001 e T028).
TEXTOS_DAS_US = (
    "PROPOSTA_SALVA",
    "ALTERACOES_SALVAS",
    "INFORME_PALAVRAS_CHAVE",
    "LINK_HTTPS_500",
    "ENTREGA_CADASTRADA",
    "ENTREGA_TIPO_REPETIDO",
    "NENHUMA_ENTREGA_CADASTRADA",
    "ENTREGA_ENVIADA",
    "ENTREGA_CUMPRIDA_PROPOSTA",
    "VERSAO_FINAL_ENVIADA",
    "VERSAO_FINAL_DISPONIVEL_APOS_RESULTADO",
    "VERSAO_FINAL_HOMOLOGADA",
)

# MF-01 a MF-10 (PROVISÓRIAS): o número da tabela da spec ↔ prefixo da constante.
NUMEROS_MF = range(1, 11)


def _historias():
    """Texto corrido das US, sem o escape do Markdown (ex.: "https\\://" vira "https://")."""
    return _texto_corrido(FONTE).replace("\\", "")


def _mensagens_da_spec():
    """{"MF-01": texto, ...}: primeiro texto entre aspas da 3ª coluna da tabela da spec 005."""
    textos = {}
    for linha in SPEC.read_text(encoding="utf-8").splitlines():
        achado = re.match(r'^\| (MF-\d{2}) \| [^|]* \| "((?:[^"\\]|\\.)*)"', linha)
        if achado:
            textos[achado.group(1)] = achado.group(2).replace('\\"', '"')
    return textos


class MensagensTCCTest(SimpleTestCase):
    """SC-006: cada mensagem é idêntica, caractere por caractere, à fonte. [SC-006]"""

    def test_textos_das_us(self):
        """Cada texto das US desta feature aparece entre aspas no documento das US."""
        historias = _historias()
        for nome in TEXTOS_DAS_US:
            texto = getattr(mensagens, nome)
            with self.subTest(constante=nome):
                self.assertIn(f'"{texto}', historias)

    def test_tabela_da_spec_tem_mf01_a_mf10(self):
        self.assertEqual(sorted(_mensagens_da_spec()), [f"MF-{n:02d}" for n in NUMEROS_MF])

    def test_mensagens_provisorias_iguais_a_tabela_da_spec(self):
        """MF-01 a MF-10 iguais à tabela da spec (os campos {nome} etc. são os mesmos)."""
        da_spec = _mensagens_da_spec()
        for numero in NUMEROS_MF:
            nomes = [n for n in dir(mensagens) if n.startswith(f"MF{numero:02d}_")]
            with self.subTest(mensagem=f"MF-{numero:02d}"):
                self.assertEqual(len(nomes), 1)
                self.assertEqual(getattr(mensagens, nomes[0]), da_spec[f"MF-{numero:02d}"])

    def test_mf01_e_mf02_sao_texto_das_us(self):
        """MF-01 e MF-02 são texto exato das US-29 e US-44 (sem o ponto final, que a tabela da
        spec acrescentou), apesar de marcadas como provisórias (Clarifications, itens 1 e 2).
        """
        historias = _historias()
        for nome in ("MF01_DATA_LIMITE_VENCIDA", "MF02_VERSAO_FINAL_DEVOLVIDA"):
            with self.subTest(constante=nome):
                self.assertIn(f'"{getattr(mensagens, nome).rstrip(".")}"', historias)
