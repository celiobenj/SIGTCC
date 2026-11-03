"""Textos exatos das mensagens da feature 007 (SC-006): constantes de defesa/mensagens.py contra
as US-21, 22, 23, 24 e 40 (v3.4) e contra a tabela "Mensagens a validar com a PO" da spec 007
(MD-01 a MD-13). Mesmo padrão de test_mensagens_orientacao.py (spec 006).

[SC-006][US-21][US-22][US-23][US-24][US-40] (tasks T055)
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from sigtcc.apps.cadastro import mensagens as mensagens_cadastro
from sigtcc.apps.cadastro.tests.test_mensagens import _texto_corrido
from sigtcc.apps.defesa import mensagens

FONTE = Path(settings.BASE_DIR) / "docs" / "fonte" / "Historias_de_Usuario_v3_4.md"
SPEC = Path(settings.BASE_DIR) / "specs" / "007-agendamento-banca" / "spec.md"
TABELA = Path(settings.BASE_DIR) / "sigtcc" / "templates" / "defesa" / "_tabela_defesas.html"

# Constantes copiadas das US desta feature (texto entre aspas na US).
TEXTOS_DAS_US = (
    "CAMPO_OBRIGATORIO",
    "NENHUM_TCC_DISPONIVEL",
    "DATA_NO_PASSADO",
    "LINK_INVALIDO",
    "TCC_NAO_AGENDAVEL",
    "AVALIADORES_DISTINTOS",
    "JUSTIFICATIVA",
    "AUSENCIA_DO_ORIENTADOR",
    "LINK_CADASTRAR_EXTERNO",
    "DEFESA_AGENDADA",
    "NENHUMA_SESSAO",
    "DATA_INICIAL_MAIOR",
    "DATA_INVALIDA",
    "SEM_PERMISSAO_SESSAO",
)


def _historias():
    """Texto corrido das US, sem o escape do Markdown (ex.: "https\\://" vira "https://")."""
    return _texto_corrido(FONTE).replace("\\", "")


def _linhas_md():
    """{"MD-01": linha inteira da tabela, ...} da spec 007."""
    linhas = {}
    for linha in SPEC.read_text(encoding="utf-8").splitlines():
        achado = re.match(r"^\| (MD-\d{2}) \|", linha)
        if achado:
            linhas[achado.group(1)] = linha
    return linhas


class MensagensDefesaTest(SimpleTestCase):
    """SC-006: cada mensagem é idêntica, caractere por caractere, à fonte. [SC-006]"""

    def test_textos_das_us(self):
        historias = _historias()
        for nome in TEXTOS_DAS_US:
            with self.subTest(constante=nome):
                self.assertIn(f'"{getattr(mensagens, nome)}"', historias)

    def test_m02_e_o_texto_das_us_23_e_24(self):
        # "Você não tem permissão para esta ação" (US-23 E10, US-24 E5) é a M-02 do handler403.
        self.assertIn(f'"{mensagens_cadastro.M02_ACESSO_NEGADO}"', _historias())

    def test_tabela_da_spec_tem_md01_a_md13(self):
        self.assertEqual(sorted(_linhas_md()), [f"MD-{n:02d}" for n in range(1, 14)])

    def test_cada_md_tem_constante(self):
        for numero in range(1, 14):
            with self.subTest(mensagem=f"MD-{numero:02d}"):
                self.assertTrue([n for n in dir(mensagens) if n.startswith(f"MD{numero:02d}_")])

    def test_constantes_md_iguais_a_tabela_da_spec(self):
        linhas = _linhas_md()
        for nome in sorted(n for n in dir(mensagens) if re.match(r"MD\d{2}_", n)):
            with self.subTest(constante=nome):
                self.assertIn(f'"{getattr(mensagens, nome)}"', linhas[f"MD-{nome[2:4]}"])

    def test_lista_vazia_usa_o_texto_da_us_40(self):
        self.assertIn(mensagens.NENHUMA_SESSAO, TABELA.read_text(encoding="utf-8"))
