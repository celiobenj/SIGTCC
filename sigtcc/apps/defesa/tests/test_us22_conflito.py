"""US-22 Impedir agendamentos conflitantes: um teste por cenário de aceite (User Story 3 da spec
007), pelo botão Agendar, pela alteração da banca e pelo reagendamento, e a corrida de duas
sessões novas para o mesmo docente (research C3).

[US-22][RBN-DEF-03.1][FR-014][FR-015][FR-016][SC-002] (tasks T039)
"""

import threading
from datetime import time, timedelta

from django.db import close_old_connections
from django.test import TransactionTestCase
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro.tests.apoio_turmas import TesteTurmas
from sigtcc.apps.defesa import services_defesa
from sigtcc.apps.defesa.choices import FormatoSessao, PapelBanca, StatusSessao
from sigtcc.apps.defesa.models import BancaDefesa, Defesas
from sigtcc.apps.defesa.tests.apoio_defesa import (
    agendar_sessao_de,
    avancar_para,
    docente,
    tcc_apto,
)

AGENDAR = reverse("defesa:agendar")
MENSAGEM = "Os seguintes membros da banca já possuem uma defesa agendada neste horário"


def dia():
    """Dia futuro em que as sessões dos testes acontecem."""
    return (timezone.now() + timedelta(days=12)).date()


class TesteConflitoNoAgendamento(TesteTurmas):
    """Cenários 1 a 5 e 8 a 14 pelo botão Agendar. [US-22][RBN-DEF-03.1][FR-014][FR-016]"""

    def setUp(self):
        super().setUp()
        self.tcc, _professor, self.orientador = tcc_apto()
        self.av1, self.av2, self.suplente = docente(), docente(), docente()

    def ocupar(self, membro, hora=time(14, 0), status=StatusSessao.AGENDADA, papel="primeiro"):
        """Outra sessão, de outro TCC, com o membro na banca no dia dos testes."""
        tcc, _p, orientador = tcc_apto()
        banca = {"primeiro_avaliador": docente(), "segundo_avaliador": docente()}
        banca[f"{papel}_avaliador" if papel != "suplente" else "suplente"] = membro
        return avancar_para(
            agendar_sessao_de(tcc, orientador, banca, data=dia(), h_inicio=hora), status
        )

    def agendar(self, hora="14:00", formato=FormatoSessao.PRESENCIAL, suplente=True):
        self.client.force_login(self.orientador)
        return self.client.post(
            AGENDAR,
            {
                "tcc": self.tcc.pk,
                "data": dia().isoformat(),
                "h_inicio": hora,
                "formato": formato,
                "local": "Laboratório LSI" if formato == FormatoSessao.PRESENCIAL else "",
                "link": "https://meet.example.org/x" if formato == FormatoSessao.REMOTA else "",
                "primeiro_avaliador": self.av1.pk,
                "segundo_avaliador": self.av2.pk,
                "suplente": self.suplente.pk if suplente else "",
            },
        )

    def assertAgendou(self, resposta):
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(Defesas.objects.filter(def_tcc=self.tcc).exists())

    def assertRecusou(self, resposta, *nomes):
        self.assertContains(resposta, MENSAGEM)
        for nome in nomes:
            self.assertContains(resposta, nome)
        self.assertFalse(Defesas.objects.filter(def_tcc=self.tcc).exists())
        self.assertFalse(BancaDefesa.objects.filter(ban_def__def_tcc=self.tcc).exists())

    def test_cenario_1_sem_conflito(self):
        self.assertAgendou(self.agendar())

    def test_cenario_2_sessoes_consecutivas(self):
        self.ocupar(self.av1, hora=time(9, 0))
        self.assertAgendou(self.agendar(hora="10:00"))

    def test_cenario_3_sem_suplente_checa_so_os_titulares(self):
        self.ocupar(self.suplente)
        self.assertAgendou(self.agendar(suplente=False))

    def test_cenario_4_mesmo_local_com_banca_diferente(self):
        self.ocupar(docente())
        self.assertAgendou(self.agendar())

    def test_cenario_5_remota_com_banca_livre(self):
        self.assertAgendou(self.agendar(formato=FormatoSessao.REMOTA))

    def test_cenario_5_remota_tambem_e_conferida(self):
        self.ocupar(self.av1)
        self.assertRecusou(self.agendar(formato=FormatoSessao.REMOTA), self.av1.usu_nome)

    def test_cenario_8_choque_com_o_1o_avaliador(self):
        self.ocupar(self.av1, hora=time(14, 30))
        self.assertRecusou(self.agendar(), f"{self.av1.usu_nome} (1º Avaliador)")

    def test_cenario_9_choque_com_o_orientador(self):
        self.ocupar(self.orientador, hora=time(13, 30))
        self.assertRecusou(self.agendar(), f"{self.orientador.usu_nome} (Orientador)")

    def test_cenario_10_choque_com_o_2o_avaliador_reagendado(self):
        self.ocupar(self.av2, status=StatusSessao.REAGENDADA)
        self.assertRecusou(self.agendar(), f"{self.av2.usu_nome} (2º Avaliador)")

    def test_cenario_11_choque_com_o_suplente(self):
        self.ocupar(self.suplente, papel="suplente")
        self.assertRecusou(self.agendar(), f"{self.suplente.usu_nome} (Suplente)")

    def test_cenario_12_varios_membros_numa_mensagem(self):
        self.ocupar(self.av1)
        self.ocupar(self.suplente, hora=time(14, 15))
        resposta = self.agendar()
        self.assertRecusou(resposta, self.av1.usu_nome, self.suplente.usu_nome)
        self.assertEqual(resposta.content.decode().count(MENSAGEM), 1)

    def test_cenario_13_choque_com_sessao_em_andamento(self):
        self.ocupar(self.av1, hora=time(9, 0), status=StatusSessao.EM_ANDAMENTO)
        self.assertRecusou(self.agendar(hora="09:30"), self.av1.usu_nome)

    def test_cenario_14_choque_com_sessao_reagendada(self):
        self.ocupar(self.av1, status=StatusSessao.REAGENDADA)
        self.assertRecusou(self.agendar(), self.av1.usu_nome)

    def test_sessao_cancelada_nao_conta(self):
        self.ocupar(self.av1, status=StatusSessao.CANCELADA)
        self.assertAgendou(self.agendar())


class TesteRevalidacao(TesteTurmas):
    """Cenários 6 e 7: reagendamento e alteração da banca desconsideram a própria sessão.
    [US-22][RBN-DEF-03.1][FR-015]
    """

    def setUp(self):
        super().setUp()
        self.tcc, _professor, self.orientador = tcc_apto()
        self.av1, self.av2 = docente(), docente()
        self.sessao = agendar_sessao_de(
            self.tcc,
            self.orientador,
            {"primeiro_avaliador": self.av1, "segundo_avaliador": self.av2},
            data=dia(),
            h_inicio=time(14, 0),
        )

    def test_cenario_6_reagendamento_desconsidera_a_propria_sessao(self):
        services_defesa.reagendar(
            self.orientador,
            self.sessao.pk,
            {
                "data": dia(),
                "h_inicio": time(14, 30),
                "formato": FormatoSessao.PRESENCIAL,
                "local": "Ludus",
            },
            "Ajuste de horário",
        )
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.def_h_inicio, time(14, 30))

    def test_cenario_7_alteracao_verifica_so_o_novo_membro(self):
        # O 1º Avaliador continua e estaria "em conflito" com a própria sessão: não conta.
        novo = docente()
        self.client.force_login(self.orientador)
        resposta = self.client.post(
            reverse("defesa:alterar_banca", args=[self.sessao.pk]),
            {
                "primeiro_avaliador": self.av1.pk,
                "segundo_avaliador": novo.pk,
                "suplente": "",
                "justificativa": "Troca do 2º Avaliador",
            },
        )
        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(
            services_defesa.banca_por_papel(self.sessao)[PapelBanca.SEGUNDO_AVALIADOR], novo
        )


class TesteCorridaDeDuasSessoesNovas(TransactionTestCase):
    """Duas sessões novas, quase ao mesmo tempo, com o mesmo docente em horários que se
    sobrepõem: só uma é gravada (research C3, bloqueante B2 da revisão do plano).

    TransactionTestCase com serialized_rollback=True, como os testes de concorrência da spec
    006: as threads precisam enxergar os dados confirmados. [US-22][RBN-DEF-03.1][FR-016]
    """

    serialized_rollback = True

    def test_so_uma_das_duas_e_gravada(self):
        comum = docente()
        pedidos = []
        for hora in (time(14, 0), time(14, 30)):
            tcc, _p, orientador = tcc_apto()
            banca = {"primeiro_avaliador": comum, "segundo_avaliador": docente()}
            basicos = {
                "data": dia(),
                "h_inicio": hora,
                "formato": FormatoSessao.PRESENCIAL,
                "local": "Laboratório LSI",
            }
            pedidos.append((orientador, tcc.pk, basicos, banca))
        barreira = threading.Barrier(2)
        resultados, inesperadas = [], []

        def rodar(orientador, tcc_id, basicos, banca):
            try:
                barreira.wait(timeout=5)
                services_defesa.agendar(orientador, tcc_id, basicos, banca)
                resultados.append("gravou")
            except services_defesa.ConflitoDeHorario:
                resultados.append("conflito")
            except Exception as exc:  # pragma: no cover - diagnóstico de falha do teste
                inesperadas.append(exc)
            finally:
                close_old_connections()

        threads = [threading.Thread(target=rodar, args=pedido) for pedido in pedidos]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=30)
        self.assertEqual(inesperadas, [])
        self.assertEqual(sorted(resultados), ["conflito", "gravou"])
        self.assertEqual(BancaDefesa.objects.filter(ban_usu=comum).count(), 1)
