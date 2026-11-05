"""US-30, declaração de participação (User Story 5 da spec 009): cenários 5.1 a 5.4, a thread
real do envio (sem SIGTCC_EMAIL_SINCRONO), o mesmo código no anexo do e-mail e na segunda via,
a falha de geração, _enviar_declaracoes sem consulta ao banco e as recusas da segunda via.

[US-30][RBN-DEF-08.3][RBN-DEF-08.4][RBN-DEF-05.4] (spec 009, tasks T046)
"""

import re
import threading
from io import BytesIO
from smtplib import SMTPException
from unittest import mock

from django.core import mail
from django.test import override_settings
from django.urls import reverse
from pypdf import PdfReader

from sigtcc.apps.cadastro.tests.apoio_acesso import criar_secretaria
from sigtcc.apps.defesa import pdf, services_documentos
from sigtcc.apps.defesa.choices import PapelBanca, StatusSessao
from sigtcc.apps.defesa.models import PresencaOuvintes
from sigtcc.apps.defesa.tests.apoio_avaliacao import TesteAvaliacao, sessao_com_banca
from sigtcc.apps.defesa.tests.apoio_documentos import (
    liberar,
    ouvinte,
    preparar_liberacao,
    presenca,
    sessao_liberada,
    texto_do_pdf,
)

ASSUNTO = "SIGTCC: declaração de participação em banca"
SEM_PERMISSAO = "Você não tem permissão para acessar os documentos desta defesa"
E3 = "Erro ao gerar os documentos da defesa. Tente realizar o download novamente em instantes"
CODIGO = re.compile(r"Código de validação: ([A-Z2-7]{4} [A-Z2-7]{4} [A-Z2-7]{4} [A-Z2-7]{4})")


def texto_do_anexo(conteudo):
    """Texto do PDF anexado (bytes), lido com o pypdf. [US-30][RBN-DEF-08.3]"""
    leitor = PdfReader(BytesIO(conteudo))
    return " ".join(" ".join(pagina.extract_text() or "" for pagina in leitor.pages).split())


def codigos(texto):
    """Códigos de validação formatados que aparecem no texto. [US-30][RBN-DEF-08.3]"""
    return set(CODIGO.findall(texto))


def declaracoes():
    """E-mails da declaração na caixa de saída, por destinatário. [US-30][RBN-DEF-08.3]"""
    return {email.to[0]: email for email in mail.outbox if email.subject == ASSUNTO}


class BaseDeclaracao(TesteAvaliacao):
    """Liberação com os callbacks on_commit e a segunda via. [US-30][RBN-DEF-08.3]"""

    def liberar_com_envio(self, cenario):
        """Libera executando os on_commit (SIGTCC_EMAIL_SINCRONO=True nos testes, TesteTurmas).
        [US-27][US-30][RBN-DEF-06.4][RBN-DEF-08.3]
        """
        with self.captureOnCommitCallbacks(execute=True):
            liberar(cenario)
        return cenario

    def segunda_via(self, usuario, sessao, follow=False):
        """GET da segunda via como o usuário. [US-30][RBN-DEF-08.3]"""
        self.client.force_login(usuario)
        return self.client.get(reverse("defesa:declaracao", args=[sessao.pk]), follow=follow)


class TesteEnvioNaLiberacao(BaseDeclaracao):
    """Cenários 5.1, 5.3 e 5.4 e a thread real. [US-30][RBN-DEF-08.3][RBN-DEF-08.4]"""

    def test_cenario_5_1_tres_emails_com_o_pdf_e_o_codigo(self):
        cenario = preparar_liberacao()
        sessao = cenario["sessao"]
        presenca(sessao, ouvinte("2022010001", "Ana Souza"))
        self.liberar_com_envio(cenario)
        enviados = declaracoes()
        membros = [cenario[chave] for chave in ("orientador", "av1", "av2")]
        self.assertEqual(set(enviados), {membro.usu_email for membro in membros})
        for membro in membros:
            with self.subTest(membro=membro.pk):
                email = enviados[membro.usu_email]
                [(nome, conteudo, tipo)] = email.attachments
                self.assertEqual(nome, f"declaracao_participacao_{sessao.pk}.pdf")
                self.assertEqual(tipo, "application/pdf")
                self.assertTrue(conteudo.startswith(b"%PDF"))
                esperado = services_documentos.codigo_formatado(
                    services_documentos.codigo_de_validacao(sessao, membro)
                )
                self.assertIn(f"Código de validação: {esperado}.", email.body)
                anexo = texto_do_anexo(conteudo)
                self.assertEqual(codigos(anexo), {esperado})
                self.assertIn(membro.usu_nome, anexo)
                self.assertIn(f"Defesa nº {sessao.pk}", anexo)
                self.assertIn("Este código não constitui assinatura digital.", anexo)
        # "Consolida os ouvintes": a consulta da US4; as presenças continuam como estavam.
        self.assertEqual(PresencaOuvintes.objects.filter(pre_def=sessao).count(), 1)

    def test_cenario_5_3_suplente_acionado_recebe_e_os_demais_nao(self):
        cenario = preparar_liberacao(suplente_acionado=True)
        presenca(cenario["sessao"], ouvinte("2022010001", "Ana Souza"))
        self.liberar_com_envio(cenario)
        enviados = declaracoes()
        self.assertIn(cenario["suplente"].usu_email, enviados)
        self.assertNotIn(cenario["ausente"].usu_email, enviados)
        self.assertEqual(len(enviados), 3)
        anexo = texto_do_anexo(enviados[cenario["suplente"].usu_email].attachments[0][1])
        self.assertIn("participou como 2º Avaliador", anexo)
        # Suplente não acionado: nenhuma declaração (outra sessão).
        outra = preparar_liberacao()
        mail.outbox.clear()
        self.liberar_com_envio(outra)
        self.assertNotIn(outra["suplente"].usu_email, declaracoes())
        # Nenhum e-mail vai a ouvinte (FR-018): só os 3 membros efetivos recebem a declaração.
        self.assertEqual(len(declaracoes()), 3)

    def test_cenario_5_4_falha_de_envio_nao_desfaz_a_liberacao(self):
        cenario = preparar_liberacao()
        sessao = cenario["sessao"]
        with mock.patch.object(
            mail.EmailMessage, "send", side_effect=SMTPException("servidor fora")
        ):
            with self.assertLogs("sigtcc.acesso") as log:
                self.liberar_com_envio(cenario)
        self.assertIn("FALHA_ENVIO_EMAIL", "".join(log.output))
        sessao.refresh_from_db()
        self.assertEqual(sessao.def_status, StatusSessao.REALIZADA)
        self.assertIsNotNone(sessao.def_data_liberacao_resultado)
        resposta = self.segunda_via(cenario["av1"], sessao)
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta["Content-Type"], "application/pdf")

    def test_falha_de_geracao_no_envio_so_no_log(self):
        cenario = preparar_liberacao()
        with mock.patch(
            "sigtcc.apps.defesa.pdf.gerar_pdf", side_effect=pdf.ErroAoGerarPdf("conversor fora")
        ):
            self.liberar_com_envio(cenario)
        self.assertEqual(declaracoes(), {})
        cenario["sessao"].refresh_from_db()
        self.assertEqual(cenario["sessao"].def_status, StatusSessao.REALIZADA)

    @override_settings(SIGTCC_EMAIL_SINCRONO=False)
    def test_thread_real_sem_envio_sincrono(self):
        """Sem SIGTCC_EMAIL_SINCRONO, o envio roda numa threading.Thread daemon; o teste aguarda
        o término dela (join) e confere os 3 e-mails. [US-30][RBN-DEF-08.3]
        """
        cenario = sessao_liberada()
        mail.outbox.clear()
        criadas = []
        original = threading.Thread

        class ThreadRegistrada(original):
            """Thread real que fica guardada para o teste aguardar o término. [US-30]"""

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                criadas.append(self)

        with mock.patch.object(services_documentos.threading, "Thread", ThreadRegistrada):
            services_documentos.ao_liberar_resultado(cenario["sessao"])
        self.assertEqual(len(criadas), 1)
        thread = criadas[0]
        self.assertTrue(thread.daemon)
        self.assertEqual(
            thread.name, f"{services_documentos.NOME_DA_THREAD}-{cenario['sessao'].pk}"
        )
        thread.join(timeout=60)
        self.assertFalse(thread.is_alive())
        self.assertEqual(len(declaracoes()), 3)

    def test_ao_liberar_resultado_nunca_levanta(self):
        cenario = sessao_liberada()
        with mock.patch(
            "sigtcc.apps.defesa.services_documentos._itens_das_declaracoes",
            side_effect=RuntimeError("falhou"),
        ):
            with self.assertLogs("sigtcc.defesa", level="ERROR"):
                services_documentos.ao_liberar_resultado(cenario["sessao"])

    def test_enviar_declaracoes_sem_consulta_ao_banco(self):
        cenario = sessao_liberada()
        itens = services_documentos._itens_das_declaracoes(cenario["sessao"])
        self.assertEqual(len(itens), 3)
        mail.outbox.clear()
        with self.assertNumQueries(0):
            services_documentos._enviar_declaracoes(itens)
        self.assertEqual(len(declaracoes()), 3)


class TesteSegundaVia(BaseDeclaracao):
    """Cenário 5.2 e as recusas da segunda via (FR-021). [US-30][RBN-DEF-08.3][RBN-DEF-05.4]"""

    def test_cenario_5_2_segunda_via_com_o_mesmo_codigo_do_email(self):
        cenario = self.liberar_com_envio(preparar_liberacao())
        sessao = cenario["sessao"]
        for chave in ("orientador", "av1", "av2"):
            membro = cenario[chave]
            with self.subTest(perfil=chave):
                self.client.force_login(membro)
                bancas = self.client.get(reverse("defesa:minhas_bancas"))
                self.assertContains(bancas, reverse("defesa:declaracao", args=[sessao.pk]))
                resposta = self.segunda_via(membro, sessao)
                self.assertEqual(resposta.status_code, 200)
                self.assertEqual(
                    resposta["Content-Disposition"],
                    f'attachment; filename="declaracao_participacao_{sessao.pk}.pdf"',
                )
                da_segunda_via = codigos(" ".join(texto_do_pdf(resposta).split()))
                email = declaracoes()[membro.usu_email]
                do_anexo = codigos(texto_do_anexo(email.attachments[0][1]))
                self.assertEqual(len(da_segunda_via), 1)
                self.assertEqual(da_segunda_via, do_anexo)
                self.assertEqual(da_segunda_via, codigos(email.body))

    def test_botao_declaracao_na_janela_da_sessao(self):
        cenario = sessao_liberada()
        sessao = cenario["sessao"]
        url = reverse("defesa:declaracao", args=[sessao.pk])
        self.client.force_login(cenario["av2"])
        self.assertContains(self.client.get(reverse("defesa:sessao", args=[sessao.pk])), url)
        for chave in ("aluno", "professor", "suplente"):
            with self.subTest(perfil=chave):
                self.client.force_login(cenario[chave])
                pagina = self.client.get(reverse("defesa:sessao", args=[sessao.pk]))
                self.assertNotContains(pagina, url)

    def test_recusas_da_segunda_via(self):
        cenario = sessao_liberada()
        sessao = cenario["sessao"]
        secretaria = criar_secretaria(curso=cenario["tcc"].tcc_tur.tur_cur)
        for usuario in (cenario["aluno"], secretaria, cenario["suplente"], cenario["professor"]):
            with self.subTest(usuario=usuario.pk):
                self.assertContains(
                    self.segunda_via(usuario, sessao), SEM_PERMISSAO, status_code=403
                )
        antes = sessao_com_banca(StatusSessao.REALIZADA)
        self.assertContains(
            self.segunda_via(antes["orientador"], antes["sessao"]), SEM_PERMISSAO, status_code=403
        )

    def test_suplente_acionado_baixa_a_segunda_via(self):
        cenario = sessao_liberada(
            suplente_acionado=True, papel_substituido=PapelBanca.PRIMEIRO_AVALIADOR
        )
        resposta = self.segunda_via(cenario["suplente"], cenario["sessao"])
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("participou como 1º Avaliador", " ".join(texto_do_pdf(resposta).split()))
        self.assertContains(
            self.segunda_via(cenario["ausente"], cenario["sessao"]),
            SEM_PERMISSAO,
            status_code=403,
        )

    def test_falha_de_geracao_da_segunda_via(self):
        cenario = sessao_liberada()
        with mock.patch(
            "sigtcc.apps.defesa.pdf.gerar_pdf", side_effect=pdf.ErroAoGerarPdf("conversor fora")
        ):
            resposta = self.segunda_via(cenario["av1"], cenario["sessao"], follow=True)
        self.assertContains(resposta, E3)
        self.assertNotEqual(resposta["Content-Type"], "application/pdf")

    def test_login_e_depois_a_segunda_via(self):
        cenario = sessao_liberada()
        url = reverse("defesa:declaracao", args=[cenario["sessao"].pk])
        resposta = self.client.get(url)
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("cadastro:entrar"), resposta["Location"])
        self.client.force_login(cenario["av1"])
        self.assertEqual(self.client.get(url).status_code, 200)
