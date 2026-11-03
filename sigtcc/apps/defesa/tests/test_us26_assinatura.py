"""US-26, assinatura do membro da banca (User Story 3 da spec 008): cenários 3.1, 3.6 a 3.8 e 3.11
a 3.13, MA-14 (revisão I-11), perfil sem arquivo, cópia apagada quando a transação desfaz
(revisão M-11) e a rota da cópia só para o dono.

[US-26][RBN-DEF-05.2][FR-015 a FR-019] (tasks T023)
"""

import os
from decimal import Decimal
from unittest import mock

from django.conf import settings
from django.core.files.storage import default_storage
from django.urls import reverse

from sigtcc.apps.cadastro import services
from sigtcc.apps.defesa import services_avaliacoes
from sigtcc.apps.defesa.choices import StatusSessao
from sigtcc.apps.defesa.models import BancaDefesa
from sigtcc.apps.defesa.tests.apoio_avaliacao import (
    TesteAvaliacao,
    assinatura_no_perfil,
    existe,
    formulario,
    jpg,
    pdf_falso,
    png,
    png_de_3_mb,
    png_gigante,
    sessao_com_banca,
)

OBRIGATORIA = "A assinatura do membro da banca é obrigatória para finalizar a avaliação"
TAMANHO = "O arquivo de assinatura deve ter tamanho máximo de 2 MB"
FORMATO = "Formato não suportado. Envie a assinatura em PNG ou JPG"
GRANDE = "A imagem da assinatura deve ter no máximo 2000 × 1000 pixels"


class TesteAssinatura(TesteAvaliacao):
    """Cenários da US-26. [US-26][RBN-DEF-05.2]"""

    def setUp(self):
        super().setUp()
        self.cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        self.sessao = self.cenario["sessao"]
        self.membro = self.cenario["av1"]
        self.url = reverse("defesa:avaliacao", args=[self.sessao.pk])
        self.client.force_login(self.membro)

    def enviar(self, **assinatura):
        return self.client.post(self.url, formulario(Decimal("8.0"), acao="enviar", **assinatura))

    def linha(self):
        return BancaDefesa.objects.get(ban_def=self.sessao, ban_usu=self.membro)

    def copias(self):
        pasta = os.path.join(settings.MEDIA_ROOT, "assinaturas_banca")
        prefixo = f"{self.sessao.pk}_{self.membro.pk}_"
        nomes = os.listdir(pasta) if os.path.isdir(pasta) else []
        return [nome for nome in nomes if nome.startswith(prefixo)]

    def test_cenario_3_1_png_de_500_kb_com_copia_e_data(self):
        pagina = self.client.get(self.url)
        self.assertContains(pagina, "Anexar imagem")
        self.assertContains(pagina, "data-previa-assinatura")
        self.assertContains(pagina, "js/avaliacao.js")
        self.enviar(arquivo=png())
        linha = self.linha()
        self.assertIsNotNone(linha.ban_data_envio)
        self.assertTrue(
            linha.ban_assinatura_path.startswith(
                f"assinaturas_banca/{self.sessao.pk}_{self.membro.pk}_"
            )
        )
        self.assertTrue(existe(linha.ban_assinatura_path))
        resposta = self.client.get(reverse("defesa:assinatura_avaliacao", args=[self.sessao.pk]))
        self.assertEqual(resposta["Content-Type"], "image/png")

    def test_jpg_aceito(self):
        self.enviar(arquivo=jpg())
        self.assertTrue(self.linha().ban_assinatura_path.endswith(".jpg"))

    def test_cenario_3_6_assinatura_do_perfil_sem_novo_arquivo(self):
        perfil = assinatura_no_perfil(self.membro)
        pagina = self.client.get(self.url)
        self.assertContains(pagina, "Usar a assinatura do meu perfil")
        self.assertContains(pagina, reverse("cadastro:assinatura"))
        self.enviar(usar_perfil="on")
        linha = self.linha()
        self.assertIsNotNone(linha.ban_data_envio)
        self.assertNotEqual(linha.ban_assinatura_path, perfil)
        with default_storage.open(linha.ban_assinatura_path, "rb") as copia:
            with default_storage.open(perfil, "rb") as original:
                self.assertEqual(copia.read(), original.read())

    def test_cenario_3_7_salvar_no_perfil(self):
        self.assertIsNone(services.caminho_da_assinatura(self.membro))
        self.enviar(arquivo=png(), salvar_no_perfil="on")
        self.membro.docentes.refresh_from_db()
        caminho = self.membro.docentes.doc_assinatura_path
        self.assertTrue(caminho and existe(caminho))
        self.assertNotEqual(caminho, self.linha().ban_assinatura_path)

    def test_salvar_no_perfil_do_membro_externo(self):
        from sigtcc.apps.cadastro.tests.apoio_acesso import criar_membro_externo
        from sigtcc.apps.defesa import services_defesa
        from sigtcc.apps.defesa.choices import PapelBanca

        externo = criar_membro_externo()
        BancaDefesa.objects.filter(ban_def=self.sessao, ban_usu=self.cenario["suplente"]).update(
            ban_usu=externo
        )
        services_defesa.acionar_suplente(
            self.cenario["orientador"], self.sessao.pk, PapelBanca.SEGUNDO_AVALIADOR, "Faltou"
        )
        self.client.force_login(externo)
        self.enviar(arquivo=png(), salvar_no_perfil="on")
        externo.membrosexternos.refresh_from_db()
        self.assertTrue(existe(externo.membrosexternos.mem_assinatura_path))

    def test_cenario_3_8_atualizar_imagem(self):
        pagina = self.client.get(self.url)
        self.assertContains(pagina, 'data-atualizar="Atualizar imagem"')
        self.enviar(arquivo=png(nome="nova.png", tamanho=None))
        self.assertTrue(self.linha().ban_assinatura_path.endswith(".png"))

    def test_cenario_3_11_sem_assinatura(self):
        resposta = self.enviar()
        self.assertContains(resposta, OBRIGATORIA)
        self.assertIsNone(self.linha().ban_data_envio)

    def test_cenario_3_12_arquivo_de_3_mb(self):
        resposta = self.enviar(arquivo=png_de_3_mb())
        self.assertContains(resposta, TAMANHO)
        self.assertIsNone(self.linha().ban_data_envio)
        self.assertEqual(self.copias(), [])

    def test_cenario_3_13_arquivo_pdf(self):
        resposta = self.enviar(arquivo=pdf_falso())
        self.assertContains(resposta, FORMATO)
        self.assertNotContains(resposta, '<img class="assin"')
        self.assertIsNone(self.linha().ban_data_envio)

    def test_png_com_extensao_falsa_recusado(self):
        resposta = self.enviar(arquivo=png(nome="assinatura.gif"))
        self.assertContains(resposta, FORMATO)

    def test_ma14_imagem_de_3000_por_3000(self):
        resposta = self.enviar(arquivo=png_gigante())
        self.assertContains(resposta, GRANDE)
        self.assertIsNone(self.linha().ban_data_envio)
        self.assertEqual(self.copias(), [])

    def test_perfil_sem_arquivo_no_disco_esconde_a_opcao(self):
        perfil = assinatura_no_perfil(self.membro)
        default_storage.delete(perfil)
        pagina = self.client.get(self.url)
        self.assertNotContains(pagina, "Usar a assinatura do meu perfil")
        resposta = self.enviar(usar_perfil="on")
        self.assertContains(resposta, OBRIGATORIA)

    def test_copia_apagada_quando_a_transacao_desfaz(self):
        with mock.patch.object(
            services_avaliacoes, "_apagar_depois_do_commit", side_effect=RuntimeError("falhou")
        ):
            with self.assertRaises(RuntimeError):
                services_avaliacoes.enviar_avaliacao(
                    self.membro,
                    self.sessao.pk,
                    {
                        c.pk: {"conceito": "Exemplar", "nota": Decimal("8.0")}
                        for c in services_avaliacoes._criterios()
                    },
                    services_avaliacoes.Assinatura(arquivo=png(), tipo="png"),
                )
        self.assertEqual(self.copias(), [])
        self.assertIsNone(self.linha().ban_data_envio)

    def test_copia_anterior_apagada_no_reenvio(self):
        self.enviar(arquivo=png())
        primeira = self.linha().ban_assinatura_path
        with self.captureOnCommitCallbacks(execute=True):
            self.client.post(reverse("defesa:reabrir_avaliacao", args=[self.sessao.pk]))
        self.assertFalse(existe(primeira))
        self.enviar(arquivo=png())
        self.assertTrue(existe(self.linha().ban_assinatura_path))

    def test_rota_da_copia_so_para_o_dono(self):
        self.enviar(arquivo=png())
        url = reverse("defesa:assinatura_avaliacao", args=[self.sessao.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        for usuario in (self.cenario["orientador"], self.cenario["av2"], self.cenario["professor"]):
            with self.subTest(usuario=usuario.usu_email):
                self.client.force_login(usuario)
                self.assertEqual(self.client.get(url).status_code, 404)
        self.client.logout()
        self.assertEqual(self.client.get(url).status_code, 302)
