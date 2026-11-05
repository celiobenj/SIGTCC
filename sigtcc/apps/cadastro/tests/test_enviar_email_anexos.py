"""enviar_email com anexos (spec 009, IC-12; research B7): a declaração de participação vai em
PDF anexado; sem anexos, a chamada a send_mail continua a mesma (os testes da spec 003 a
substituem por mock.patch).

[US-30][RBN-DEF-08.3] (spec 009, tasks T007)
"""

from smtplib import SMTPException
from unittest import mock

from django.core import mail
from django.test import SimpleTestCase

from sigtcc.apps.cadastro import services

TEMPLATE = "cadastro/emails/aviso_entrega.txt"
CONTEXTO = {"nome": "Ana", "texto": "Texto do aviso"}
ANEXO = ("declaracao_participacao_7.pdf", b"%PDF-1.4\n%teste\n", "application/pdf")


class TesteEnviarEmailComAnexos(SimpleTestCase):
    """Parâmetro opcional `anexos` de services.enviar_email. [US-30][RBN-DEF-08.3]"""

    def test_anexo_chega_no_email(self):
        """Com anexos: um EmailMessage com o PDF anexado. [US-30][RBN-DEF-08.3]"""
        services.enviar_email("ana@uea.edu.br", "Assunto", TEMPLATE, CONTEXTO, anexos=[ANEXO])
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ["ana@uea.edu.br"])
        self.assertEqual(email.subject, "Assunto")
        self.assertIn("Texto do aviso", email.body)
        self.assertEqual(email.attachments, [ANEXO])

    def test_sem_anexo_continua_usando_send_mail(self):
        """Sem anexos: a mesma chamada literal a send_mail de antes. [US-30][FR-026]"""
        with mock.patch("sigtcc.apps.cadastro.services.send_mail") as enviar:
            services.enviar_email("ana@uea.edu.br", "Assunto", TEMPLATE, CONTEXTO)
        enviar.assert_called_once()
        self.assertEqual(enviar.call_args.args[0], "Assunto")
        self.assertEqual(enviar.call_args.args[2:], (None, ["ana@uea.edu.br"]))
        self.assertEqual(enviar.call_args.kwargs, {"fail_silently": False})
        self.assertEqual(mail.outbox, [])

    def test_com_anexo_nao_usa_send_mail(self):
        """Com anexos, send_mail não é chamado. [US-30][RBN-DEF-08.3]"""
        with mock.patch("sigtcc.apps.cadastro.services.send_mail") as enviar:
            services.enviar_email("ana@uea.edu.br", "Assunto", TEMPLATE, CONTEXTO, anexos=[ANEXO])
        enviar.assert_not_called()
        self.assertEqual(len(mail.outbox), 1)

    def test_falha_com_anexo_registra_e_relanca(self):
        """Falha no envio com anexo: FALHA_ENVIO_EMAIL só com o tipo do erro, e a exceção sobe.
        [US-30][RBN-DEF-08.3][FR-026]
        """
        falha = SMTPException("servidor fora")
        with mock.patch.object(mail.EmailMessage, "send", side_effect=falha):
            with self.assertLogs("sigtcc.acesso") as log:
                with self.assertRaises(SMTPException):
                    services.enviar_email(
                        "ana@uea.edu.br", "Assunto", TEMPLATE, CONTEXTO, anexos=[ANEXO]
                    )
        self.assertIn("FALHA_ENVIO_EMAIL", log.output[0])
        self.assertIn("SMTPException", log.output[0])
        self.assertNotIn("servidor fora", "".join(log.output))
        self.assertNotIn("ana@uea.edu.br", "".join(log.output))
