"""Textos exatos das mensagens da feature 008 (SC-007): constantes de defesa/mensagens.py contra
as US-25, US-26 e US-27 (v3.4) e contra a tabela "Mensagens a validar com a PO" da spec 008
(MA-01 a MA-14). Mesmo padrão de test_mensagens_defesa.py (spec 007).

[SC-007][US-25][US-26][US-27] (tasks T040)
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from sigtcc.apps.defesa import mensagens
from sigtcc.apps.defesa.tests.test_mensagens_defesa import _historias

SPEC = Path(settings.BASE_DIR) / "specs" / "008-avaliacao-resultados" / "spec.md"

# Constantes copiadas das US-25 a US-27 (texto entre aspas na US).
TEXTOS_DAS_US = (
    "NOTA_FORA_DA_FAIXA",
    "CRITERIOS_INCOMPLETOS",
    "ASSINATURA_OBRIGATORIA",
    "ACESSO_RESTRITO",
    "ASSINATURA_TAMANHO",
    "ASSINATURA_FORMATO",
    "SELECIONE_O_PARECER",
    "APENAS_O_ORIENTADOR",
)


def _linhas_ma():
    """{"MA-01": linha inteira da tabela, ...} da spec 008."""
    linhas = {}
    for linha in SPEC.read_text(encoding="utf-8").splitlines():
        achado = re.match(r"^\| (MA-\d{2}) \|", linha)
        if achado:
            linhas[achado.group(1)] = linha
    return linhas


class MensagensAvaliacaoTest(SimpleTestCase):
    """SC-007: cada mensagem é idêntica, caractere por caractere, à fonte. [SC-007]"""

    def test_textos_das_us(self):
        historias = _historias()
        for nome in TEXTOS_DAS_US:
            with self.subTest(constante=nome):
                self.assertIn(f'"{getattr(mensagens, nome)}"', historias)

    def test_tabela_da_spec_tem_ma01_a_ma14(self):
        self.assertEqual(sorted(_linhas_ma()), [f"MA-{n:02d}" for n in range(1, 15)])

    def test_cada_ma_tem_constante(self):
        for numero in range(1, 15):
            with self.subTest(mensagem=f"MA-{numero:02d}"):
                self.assertTrue([n for n in dir(mensagens) if n.startswith(f"MA{numero:02d}_")])

    def test_constantes_ma_iguais_a_tabela_da_spec(self):
        linhas = _linhas_ma()
        for nome in sorted(n for n in dir(mensagens) if re.match(r"MA\d{2}_", n)):
            with self.subTest(constante=nome):
                texto = getattr(mensagens, nome)
                if nome == "MA06_ASSUNTO":
                    # O assunto do e-mail está na coluna "Uso" da MA-06.
                    self.assertIn(f'"{texto}"', linhas["MA-06"])
                    continue
                self.assertIn(f'"{texto}"', linhas[f"MA-{nome[2:4]}"])
