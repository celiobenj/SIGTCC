"""Textos exatos das mensagens da feature 009 (SC-006) e nenhum PDF gravado em disco (SC-003).

Cada constante do T004 em defesa/mensagens.py é comparada, caractere por caractere, com a fonte:
o texto entre aspas das US-28 e US-30 (v3.4), o diagrama 05 (MX-06) ou a tabela "Mensagens a
validar com a PO" da spec 009 (MX-01 a MX-09, sem a MX-02, removida). Mesmo padrão de
test_mensagens_avaliacao.py (spec 008).

[SC-003][SC-006][US-28][US-30][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-07.3][RBN-DEF-08.1]
[RBN-DEF-08.2][RBN-DEF-08.3][RBN-DEF-08.4][RBN-DEF-08.5] (spec 009, tasks T047)
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase
from django.urls import reverse

from sigtcc.apps.defesa import mensagens
from sigtcc.apps.defesa.choices import StatusSessao
from sigtcc.apps.defesa.tests.apoio_avaliacao import TesteAvaliacao, sessao_com_banca
from sigtcc.apps.defesa.tests.apoio_documentos import sessao_liberada
from sigtcc.apps.defesa.tests.test_mensagens_defesa import _historias

SPEC = Path(settings.BASE_DIR) / "specs" / "009-documentacao-encerramento" / "spec.md"
DIAGRAMAS = Path(settings.BASE_DIR) / "docs" / "diagramas" / "Diagramas_Sequencia_PlantUML_v2.md"

# Constantes copiadas das US-28 e US-30 (texto entre aspas na US). [US-28][US-30]
TEXTOS_DAS_US = (
    "SEM_PERMISSAO_DOCUMENTOS",
    "ATA_SEM_ASSINATURA_COORDENADOR",
    "ERRO_AO_GERAR_DOCUMENTOS",
    "FOLHA_NAO_SE_APLICA",
    "FOLHA_REPROVADO",
    "OUVINTES_SALVOS",
    "MATRICULA_INVALIDA",
    "OUVINTE_REPETIDO",
    "NOME_INVALIDO",
    "OUVINTES_FORA_DO_STATUS",
    "SEM_DEFESAS_AGENDADAS",
)

# MX da spec 009 (a MX-02 foi removida, P4). [US-28][US-30]
NUMEROS_MX = (1, 3, 4, 5, 6, 7, 8, 9)


def _linhas_mx():
    """{"MX-01": linha da tabela, ...} da spec 009, com as aspas escapadas (\\") desfeitas.
    [SC-006]
    """
    linhas = {}
    for linha in SPEC.read_text(encoding="utf-8").splitlines():
        achado = re.match(r"^\| (MX-\d{2}) \|", linha)
        if achado:
            linhas[achado.group(1)] = linha.replace('\\"', '"')
    return linhas


class MensagensDocumentosTest(SimpleTestCase):
    """SC-006: cada mensagem é idêntica à fonte. [SC-006][US-28][US-30]"""

    def test_textos_das_us(self):
        historias = _historias()
        for nome in TEXTOS_DAS_US:
            with self.subTest(constante=nome):
                self.assertIn(f'"{getattr(mensagens, nome)}"', historias)

    def test_tabela_da_spec_tem_as_mx(self):
        self.assertEqual(sorted(_linhas_mx()), [f"MX-{n:02d}" for n in (1, 2, 3, 4, 5, 6, 7, 8, 9)])

    def test_cada_mx_tem_constante(self):
        for numero in NUMEROS_MX:
            with self.subTest(mensagem=f"MX-{numero:02d}"):
                self.assertTrue([n for n in dir(mensagens) if n.startswith(f"MX{numero:02d}_")])
        self.assertFalse([n for n in dir(mensagens) if n.startswith("MX02_")])

    def test_constantes_mx_iguais_a_tabela_da_spec(self):
        linhas = _linhas_mx()
        for nome in sorted(n for n in dir(mensagens) if re.match(r"MX\d{2}_", n)):
            with self.subTest(constante=nome):
                texto = getattr(mensagens, nome)
                linha = linhas[f"MX-{nome[2:4]}"]
                if nome == "MX04_ASSUNTO":
                    self.assertIn(f'Assunto "{texto}"', linha)
                elif nome == "MX04_CORPO":
                    self.assertIn(f'corpo "{texto}"', linha)
                else:
                    self.assertIn(f'"{texto}"', linha)

    def test_mx06_e_o_texto_do_diagrama_05(self):
        self.assertEqual(mensagens.MX06_OCORRENCIAS_SALVAS, "Ocorrências salvas com sucesso")
        self.assertIn(mensagens.MX06_OCORRENCIAS_SALVAS, DIAGRAMAS.read_text(encoding="utf-8"))

    def test_provisorias_marcadas_com_q142(self):
        fonte = (Path(settings.BASE_DIR) / "sigtcc" / "apps" / "defesa" / "mensagens.py").read_text(
            encoding="utf-8"
        )
        trecho = fonte[fonte.index("MX01_OCORRENCIAS_LONGAS") - 200 :]
        self.assertGreaterEqual(trecho.count("# PROVISÓRIO (Q-142)"), 7)


class NenhumPdfEmDiscoTest(TesteAvaliacao):
    """SC-003: gerar a Ata, a Folha, a declaração e a agenda não grava nenhum PDF no MEDIA_ROOT
    nem na pasta do projeto. [SC-003][US-28][US-30][RBN-DEF-07.1][RBN-DEF-08.1][RBN-DEF-08.3]
    """

    def pdfs(self):
        """PDFs no MEDIA_ROOT e na pasta sigtcc/ do projeto. [SC-003]"""
        raizes = (Path(settings.MEDIA_ROOT), Path(settings.BASE_DIR) / "sigtcc")
        return {str(caminho) for raiz in raizes for caminho in raiz.rglob("*.pdf")}

    def test_downloads_nao_gravam_pdf(self):
        antes = self.pdfs()
        cenario = sessao_liberada()
        sessao = cenario["sessao"]
        sessao_com_banca(StatusSessao.AGENDADA)
        self.client.force_login(cenario["av1"])
        for nome in ("ata_final", "folha_aprovacao", "declaracao"):
            with self.subTest(documento=nome):
                resposta = self.client.get(reverse(f"defesa:{nome}", args=[sessao.pk]))
                self.assertEqual(resposta["Content-Type"], "application/pdf")
        resposta = self.client.get(
            reverse("defesa:agenda"), {"data_inicial": "01/11/2026", "data_final": "30/11/2026"}
        )
        self.assertEqual(resposta["Content-Type"], "application/pdf")
        self.assertEqual(self.pdfs(), antes)
        self.assertIsNone(sessao.def_ata_final_path)
        self.assertIsNone(sessao.def_folha_aprovacao_path)
