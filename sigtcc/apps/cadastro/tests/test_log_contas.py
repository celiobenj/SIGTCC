"""Testes dos acréscimos da spec 002 ao log e à troca de e-mail da spec 003 (tasks T004).

[US-03][US-05][FR-047][FR-001][research C4][C18][I4][I5]
"""

from django.db import transaction

from sigtcc.apps.cadastro import services
from sigtcc.apps.cadastro.services import AUTOR_SISTEMA, EventoAcesso
from sigtcc.apps.cadastro.tests.apoio_contas import TesteContas, docente_de, membro


class LogContasTest(TesteContas):
    """Autor "sistema", autor do gestor e eventos novos. [FR-047][C18]"""

    def test_autor_sistema_grava_sistema(self):
        conta = docente_de()
        with self.assertLogs("sigtcc.acesso", "INFO") as log:
            services.registrar_evento(EventoAcesso.CONTA_CRIADA, conta, autor=AUTOR_SISTEMA)
        self.assertIn(f"CONTA_CRIADA | conta={conta.pk} | autor=sistema |", log.output[0])

    def test_sem_autor_continua_propria(self):
        conta = docente_de()
        with self.assertLogs("sigtcc.acesso", "INFO") as log:
            services.registrar_evento(EventoAcesso.CONTA_EXPIRADA, conta)
        self.assertIn("autor=própria", log.output[0])

    def test_eventos_novos_existem(self):
        for nome in (
            "CONTA_CRIADA",
            "CONTA_ALTERADA",
            "CONTA_INATIVADA",
            "CONTA_REATIVADA",
            "ACESSO_PRORROGADO",
            "CONTA_EXPIRADA",
            "VALIDADE_RECALCULADA",
            "SENHA_GESTOR_INCORRETA",
        ):
            self.assertEqual(EventoAcesso[nome].value, nome)

    def test_troca_pedida_pelo_gestor_registra_autor_sem_email_completo(self):
        gestor = docente_de()
        conta = membro(email="ana@ufam.edu.br")
        with self.assertLogs("sigtcc.acesso", "INFO") as log, transaction.atomic():
            services.pedir_troca_email(conta, "nova@empresa.com.br", autor=gestor)
        linha = log.output[-1]
        self.assertIn(f"TROCA_EMAIL_PEDIDA | conta={conta.pk} | autor={gestor.pk} |", linha)
        self.assertNotIn("nova@empresa.com.br", linha)
        self.assertNotIn("ana@ufam.edu.br", linha)

    def test_travar_email_roda_dentro_da_transacao(self):
        with transaction.atomic():
            services.travar_email("Maria@UEA.edu.br")
            services.travar_email(None)
