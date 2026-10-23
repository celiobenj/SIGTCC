"""Testes de aceite da US-06 (cenários 1 a 18), da expiração no login e pelo comando, e das
Clarifications Q4, Q13, Q15, Q33 e Q36 (tasks T033, T034 e T036).

O cenário 3 confere a M-16 atual do login; o texto da US-06 depende da Q-52 (Julia) e fica num
teste marcado como falha esperada.

[US-06][RBN-CAD-03.3][RBN-DEF-02.4][FR-037][FR-038][FR-039][FR-040][FR-041][SC-006]
[Q4][Q13][Q15][Q33][Q36]
"""

import io
import unittest
from datetime import date, datetime
from unittest import mock

from django.core.management import call_command
from django.db import transaction
from django.urls import reverse

from sigtcc.apps.cadastro import mensagens, services_contas
from sigtcc.apps.cadastro.choices import StatusConta
from sigtcc.apps.cadastro.models import MembrosExternos, Usuarios
from sigtcc.apps.cadastro.tests.apoio_acesso import SENHA
from sigtcc.apps.cadastro.tests.apoio_contas import (
    TesteContas,
    banca,
    docente_de,
    evento_defesa,
    membro,
)
from sigtcc.apps.cadastro.tests.fabricas import criar_defesa
from sigtcc.apps.defesa.choices import EventoDefesa, PapelBanca, StatusSessao

HOJE = date(2026, 10, 10)


def no_dia(dia):
    """Relógio parado às 10h do dia (o login e a expiração usam timezone.now)."""
    return mock.patch(
        "django.utils.timezone.now", return_value=datetime(dia.year, dia.month, dia.day, 10, 0)
    )


def sessao(conta, dia, status=StatusSessao.AGENDADA):
    """Sessão de defesa no dia, com o membro na banca."""
    defesa = criar_defesa(def_data=dia, def_status=status)
    banca(defesa, conta)
    return defesa


def validade(conta):
    return MembrosExternos.objects.get(pk=conta.pk).mem_validade_ate


def status(conta):
    return Usuarios.objects.get(pk=conta.pk).usu_status


class RegraDeValidadeTest(TesteContas):
    """Cenários 1, 5 a 11, 14, 15, 17 e 18 (recalcular_validade, contrato §2)."""

    def test_cenario_01_defesa_mais_sete_dias(self):
        conta = membro()
        sessao(conta, date(2026, 10, 20))
        self.assertTrue(services_contas.recalcular_validade(conta, hoje=HOJE))
        self.assertEqual(validade(conta), date(2026, 10, 27))

    def test_cenario_05_defesa_mais_distante(self):
        conta = membro()
        sessao(conta, date(2026, 10, 20))
        sessao(conta, date(2026, 11, 5))
        services_contas.recalcular_validade(conta, hoje=HOJE)
        self.assertEqual(validade(conta), date(2026, 11, 12))

    def test_cenario_06_cancelada_nao_conta(self):
        conta = membro()
        sessao(conta, date(2026, 10, 25), StatusSessao.CANCELADA)
        sessao(conta, date(2026, 10, 15))
        services_contas.recalcular_validade(conta, hoje=HOJE)
        self.assertEqual(validade(conta), date(2026, 10, 22))

    def test_cenario_07_unica_sessao_cancelada(self):
        conta = membro()
        defesa = sessao(conta, date(2026, 10, 20), StatusSessao.CANCELADA)
        evento_defesa(defesa, EventoDefesa.CANCELAMENTO, date(2026, 10, 12))
        services_contas.recalcular_validade(conta, hoje=HOJE)
        self.assertEqual(validade(conta), date(2026, 10, 19))

    def test_cenario_08_expirada_volta_a_ativa_com_nova_banca(self):
        conta = membro(status=StatusConta.EXPIRADA, validade=date(2026, 10, 1))
        sessao(conta, date(2026, 11, 10))
        services_contas.recalcular_validade(conta, hoje=date(2026, 10, 30))
        self.assertEqual(validade(conta), date(2026, 11, 17))
        self.assertEqual(status(conta), StatusConta.ATIVA)

    def test_cenario_09_nova_banca_mais_distante(self):
        conta = membro(validade=date(2026, 10, 27))
        sessao(conta, date(2026, 10, 20))
        sessao(conta, date(2026, 11, 5))
        services_contas.recalcular_validade(conta, hoje=HOJE)
        self.assertEqual(validade(conta), date(2026, 11, 12))

    def test_cenarios_10_e_11_reagendamento(self):
        for nova_data, esperado in (
            (date(2026, 11, 3), date(2026, 11, 10)),
            (date(2026, 10, 15), date(2026, 10, 22)),
        ):
            with self.subTest(nova_data=nova_data):
                conta = membro(validade=date(2026, 10, 27))
                sessao(conta, nova_data, StatusSessao.REAGENDADA)
                services_contas.recalcular_validade(conta, hoje=HOJE)
                self.assertEqual(validade(conta), esperado)

    def test_cenario_14_banca_depois_do_cadastro(self):
        conta = membro(validade=date(2026, 10, 31))
        sessao(conta, date(2026, 11, 10))
        services_contas.recalcular_validade(conta, hoje=date(2026, 10, 20))
        self.assertEqual(validade(conta), date(2026, 11, 17))

    def test_cenario_15_realizada_conta(self):
        conta = membro()
        sessao(conta, date(2026, 10, 20), StatusSessao.REALIZADA)
        services_contas.recalcular_validade(conta, hoje=date(2026, 10, 21))
        self.assertEqual(validade(conta), date(2026, 10, 27))

    def test_cenario_17_retirada_da_unica_banca(self):
        conta = membro(validade=date(2026, 10, 27))
        defesa = criar_defesa(def_data=date(2026, 10, 20))
        evento_defesa(defesa, EventoDefesa.ALTERACAO_DA_BANCA, date(2026, 10, 14), removido=conta)
        services_contas.recalcular_validade(conta, hoje=HOJE)
        self.assertEqual(validade(conta), date(2026, 10, 21))

    def test_q13_vale_o_evento_mais_recente_entre_cancelamento_e_retirada(self):
        conta = membro()
        cancelada = sessao(conta, date(2026, 10, 30), StatusSessao.CANCELADA)
        evento_defesa(cancelada, EventoDefesa.CANCELAMENTO, date(2026, 10, 12))
        outra = criar_defesa(def_data=date(2026, 11, 1))
        evento_defesa(outra, EventoDefesa.ALTERACAO_DA_BANCA, date(2026, 10, 15), removido=conta)
        services_contas.recalcular_validade(conta, hoje=HOJE)
        self.assertEqual(validade(conta), date(2026, 10, 22))

    def test_cenario_18_falha_mantem_a_validade_e_nao_quebra_quem_chamou(self):
        conta = membro(validade=date(2026, 10, 27))
        sessao(conta, date(2026, 11, 20))
        with (
            mock.patch.object(services_contas, "_validade_pelas_bancas", side_effect=RuntimeError),
            self.assertLogs("sigtcc.contas", "ERROR") as log,
            transaction.atomic(),
        ):
            self.assertFalse(services_contas.recalcular_validade(conta, hoje=HOJE))
            self.assertEqual(Usuarios.objects.filter(pk=conta.pk).count(), 1)
        self.assertIn("RuntimeError", log.output[0])
        self.assertEqual(validade(conta), date(2026, 10, 27))

    def test_q33_substituido_pelo_suplente_mantem_a_sessao(self):
        conta = membro()
        suplente = membro()
        defesa = criar_defesa(def_data=date(2026, 11, 5))
        banca(defesa, suplente, papel=PapelBanca.PRIMEIRO_AVALIADOR, substituido=conta)
        services_contas.recalcular_validade(conta, hoje=HOJE)
        self.assertEqual(validade(conta), date(2026, 11, 12))

    def test_q36_prorrogacao_protegida_no_recalculo(self):
        conta = membro(validade=date(2026, 11, 10))
        MembrosExternos.objects.filter(pk=conta.pk).update(mem_prorrogado_ate=date(2026, 11, 10))
        defesa = sessao(conta, date(2026, 10, 22), StatusSessao.REAGENDADA)
        services_contas.recalcular_validade(conta, hoje=HOJE)
        self.assertEqual(validade(conta), date(2026, 11, 10))
        defesa.def_data = date(2026, 11, 15)
        defesa.save()
        services_contas.recalcular_validade(conta, hoje=HOJE)
        self.assertEqual(validade(conta), date(2026, 11, 22))

    def test_m9_validade_no_passado_expira_na_hora(self):
        conta = membro(validade=date(2026, 12, 1))
        sessao(conta, date(2026, 10, 1), StatusSessao.REALIZADA)
        services_contas.recalcular_validade(conta, hoje=HOJE)
        self.assertEqual(status(conta), StatusConta.EXPIRADA)

    def test_aguardando_ativacao_nao_muda_de_status(self):
        conta = membro(status=StatusConta.AGUARDANDO_ATIVACAO, validade=date(2026, 9, 1))
        sessao(conta, date(2026, 11, 1))
        services_contas.recalcular_validade(conta, hoje=HOJE)
        self.assertEqual(validade(conta), date(2026, 11, 8))
        self.assertEqual(status(conta), StatusConta.AGUARDANDO_ATIVACAO)

    def test_sem_banca_mantem_a_validade_do_cadastro(self):
        conta = membro(validade=date(2026, 10, 31))
        services_contas.recalcular_validade(conta, hoje=HOJE)
        self.assertEqual(validade(conta), date(2026, 10, 31))

    def test_outro_tipo_de_conta_e_ignorado_e_chamada_repetida_nao_muda(self):
        self.assertTrue(services_contas.recalcular_validade(docente_de(), hoje=HOJE))
        conta = membro()
        sessao(conta, date(2026, 10, 20))
        services_contas.recalcular_validade(conta, hoje=HOJE)
        services_contas.recalcular_validade(conta, hoje=HOJE)
        self.assertEqual(validade(conta), date(2026, 10, 27))


class LoginEExpiracaoTest(TesteContas):
    """Cenários 2 a 4, 12, 13 e 16 (login, US-11) e a expiração automática (FR-040; SC-006)."""

    def _entrar(self, conta, dia):
        with no_dia(dia):
            return self.client.post(
                reverse("cadastro:entrar"), {"credencial": conta.usu_email, "senha": SENHA}
            )

    def test_cenario_02_login_no_ultimo_dia(self):
        conta = membro(validade=date(2026, 10, 27))
        resposta = self._entrar(conta, date(2026, 10, 27))
        self.assertEqual(resposta.status_code, 302)

    def test_cenario_03_login_depois_da_validade_grava_expirada(self):
        conta = membro(validade=date(2026, 10, 27))
        resposta = self._entrar(conta, date(2026, 10, 28))
        self.assertContains(resposta, mensagens.ACESSO_EXPIRADO)
        self.assertEqual(status(conta), StatusConta.EXPIRADA)

    @unittest.expectedFailure
    def test_cenario_03_texto_da_us06_pendente_da_q52(self):
        # Q-52 (Julia): o login da spec 003 ainda mostra a M-16; a US-06 pede outro texto.
        conta = membro(validade=date(2026, 10, 27))
        resposta = self._entrar(conta, date(2026, 10, 28))
        self.assertContains(resposta, mensagens.ACESSO_EXPIRADO_US06)

    def test_cenario_04_dados_continuam_depois_de_expirar(self):
        conta = membro(validade=date(2026, 10, 27))
        defesa = sessao(conta, date(2026, 10, 20), StatusSessao.REALIZADA)
        self._entrar(conta, date(2026, 10, 28))
        conta.refresh_from_db()
        self.assertEqual(conta.membrosexternos.mem_instituicao, "Universidade Federal do Amazonas")
        self.assertTrue(defesa.bancadefesa_set.filter(ban_usu=conta).exists())

    def test_cenarios_12_e_13_validade_de_30_dias_sem_banca(self):
        conta = membro(validade=date(2026, 10, 31))
        self.assertEqual(self._entrar(conta, date(2026, 10, 10)).status_code, 302)
        self.client.logout()
        self.assertContains(self._entrar(conta, date(2026, 11, 5)), mensagens.ACESSO_EXPIRADO)

    def test_cenario_16_renovado_entra_com_a_mesma_senha(self):
        conta = membro(status=StatusConta.EXPIRADA, validade=date(2026, 10, 1))
        sessao(conta, date(2026, 11, 10))
        services_contas.recalcular_validade(conta, hoje=date(2026, 10, 30))
        self.assertEqual(self._entrar(conta, date(2026, 10, 30)).status_code, 302)

    def test_falha_ao_gravar_expirada_nao_muda_o_login(self):
        conta = membro(validade=date(2026, 10, 27))
        with (
            mock.patch(
                "sigtcc.apps.cadastro.services.expirar_se_vencida", side_effect=RuntimeError
            ),
            self.assertLogs("sigtcc.acesso", "ERROR"),
        ):
            resposta = self._entrar(conta, date(2026, 10, 28))
        self.assertContains(resposta, mensagens.ACESSO_EXPIRADO)

    def test_sc006_comando_expira_sem_login_e_e_idempotente(self):
        vencida = membro(validade=date(2026, 10, 1))
        em_dia = membro(validade=date(2026, 12, 1))
        saida = io.StringIO()
        with no_dia(date(2026, 10, 10)):
            call_command("expirar_membros_externos", stdout=saida)
            call_command("expirar_membros_externos", stdout=io.StringIO())
        self.assertIn("Contas expiradas: 1", saida.getvalue())
        self.assertEqual(status(vencida), StatusConta.EXPIRADA)
        self.assertEqual(status(em_dia), StatusConta.ATIVA)

    def test_comando_nao_expira_conta_prorrogada_antes_da_trava(self):
        from sigtcc.apps.cadastro import services

        conta = membro(validade=date(2026, 10, 1))
        MembrosExternos.objects.filter(pk=conta.pk).update(mem_validade_ate=date(2026, 10, 17))
        with no_dia(date(2026, 10, 10)):
            self.assertFalse(services.expirar_se_vencida(conta))
        self.assertEqual(status(conta), StatusConta.ATIVA)

    def test_log_de_expiracao_com_autor_sistema(self):
        conta = membro(validade=date(2026, 10, 1))
        with self.assertLogs("sigtcc.acesso", "INFO") as log, no_dia(date(2026, 10, 10)):
            call_command("expirar_membros_externos", stdout=io.StringIO())
        self.assertTrue(
            any(
                f"CONTA_EXPIRADA | conta={conta.pk} | autor=sistema" in linha
                for linha in log.output
            )
        )
