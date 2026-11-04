"""Utilitário de PDF em memória (spec 008, research A9; contrato §3): gera o PDF sem gravar
arquivo, entrega como download sem cache e recusa recurso de rede ou de fora das pastas do
projeto, sem acessar a rede.

[US-27][US-28][RBN-DEF-07.1][RBN-DEF-08.3][revisão I-12][revisão M-01] (tasks T003)
"""

import os
import socket
import tempfile
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase, override_settings

from sigtcc.apps.defesa import pdf

TEMPLATE = "defesa/pdf/base_pdf.html"


def _sem_rede(*args, **kwargs):
    """Qualquer tentativa de abrir conexão de rede faz o teste falhar."""
    raise AssertionError("o PDF tentou acessar a rede")


@mock.patch.object(socket.socket, "connect", _sem_rede)
class TestePdf(SimpleTestCase):
    """gerar_pdf, resposta_pdf e link_callback. [US-28][RBN-DEF-07.1][revisão I-12]"""

    def test_gera_um_pdf_em_memoria_com_a_fonte_local(self):
        conteudo = pdf.gerar_pdf(TEMPLATE, {"titulo": "Ata Final", "texto": "Defesa realizada"})
        self.assertTrue(conteudo.startswith(b"%PDF"))
        self.assertIn(b"Roboto", conteudo)

    def test_template_de_pdf_nao_estende_a_base_das_telas(self):
        caminho = Path(settings.BASE_DIR) / "sigtcc" / "templates" / TEMPLATE
        texto = caminho.read_text(encoding="utf-8")
        self.assertNotIn("extends", texto)
        self.assertNotIn("fonts.googleapis", texto)

    def test_link_callback_aceita_static_e_media_dentro_das_pastas(self):
        fonte = pdf.link_callback("static/fonts/Roboto-Regular.ttf")
        self.assertTrue(fonte and os.path.isfile(fonte))
        self.assertEqual(pdf.link_callback("/static/fonts/Roboto-Regular.ttf"), fonte)
        with tempfile.TemporaryDirectory() as midia:
            Path(midia, "assinaturas_banca").mkdir()
            Path(midia, "assinaturas_banca", "a.png").write_bytes(b"\x89PNG\r\n\x1a\n")
            with override_settings(MEDIA_ROOT=midia):
                achado = pdf.link_callback("media/assinaturas_banca/a.png")
                self.assertEqual(
                    os.path.realpath(achado),
                    os.path.realpath(os.path.join(midia, "assinaturas_banca", "a.png")),
                )
                self.assertIsNone(pdf.link_callback("media/../segredo.png"))

    def test_link_callback_recusa_rede_arquivo_e_saida_da_pasta(self):
        for uri in (
            "http://exemplo.org/logo.png",
            "https://exemplo.org/logo.png",
            "//exemplo.org/logo.png",
            "file:///etc/passwd",
            "file://C:/Windows/win.ini",
            "data:image/png;base64,iVBORw0KGgo=",
            "static/../../manage.py",
            "static/../settings.py",
            "media/../../.env",
            "static\\..\\..\\manage.py",
            "../manage.py",
            "/etc/passwd",
            "",
            None,
        ):
            with self.subTest(uri=uri):
                self.assertIsNone(pdf.link_callback(uri))

    def test_imagem_de_rede_no_template_nao_e_buscada(self):
        with mock.patch("sigtcc.apps.defesa.pdf.render_to_string") as render:
            render.return_value = (
                '<html><body><p>Ata</p><img src="http://exemplo.org/a.png">'
                '<img src="file:///etc/passwd"></body></html>'
            )
            with self.assertLogs("xhtml2pdf", level="WARNING") as log:
                conteudo = pdf.gerar_pdf(TEMPLATE, {})
        self.assertTrue(conteudo.startswith(b"%PDF"))
        self.assertTrue(any("Blocked by the resource policy" in linha for linha in log.output))

    def test_resposta_para_download_sem_cache(self):
        resposta = pdf.resposta_pdf("ata.pdf", TEMPLATE, {"titulo": "Ata Final"})
        self.assertEqual(resposta["Content-Type"], "application/pdf")
        self.assertEqual(resposta["Content-Disposition"], 'attachment; filename="ata.pdf"')
        self.assertEqual(resposta["Cache-Control"], "no-store")
        self.assertTrue(resposta.content.startswith(b"%PDF"))

    def test_falha_na_geracao_vira_erro_ao_gerar_pdf(self):
        with mock.patch("xhtml2pdf.pisa.CreatePDF", side_effect=RuntimeError("quebrou")):
            with self.assertLogs("sigtcc.defesa", level="ERROR"):
                with self.assertRaises(pdf.ErroAoGerarPdf):
                    pdf.gerar_pdf(TEMPLATE, {"titulo": "Ata"})
        with mock.patch("xhtml2pdf.pisa.CreatePDF") as criar:
            criar.return_value.err = 1
            with self.assertLogs("sigtcc.defesa", level="ERROR"):
                with self.assertRaises(pdf.ErroAoGerarPdf):
                    pdf.gerar_pdf(TEMPLATE, {"titulo": "Ata"})

    def test_nenhum_arquivo_gravado_no_media(self):
        with tempfile.TemporaryDirectory() as midia:
            with override_settings(MEDIA_ROOT=midia):
                pdf.gerar_pdf(TEMPLATE, {"titulo": "Folha de Aprovação"})
            self.assertEqual(os.listdir(midia), [])
