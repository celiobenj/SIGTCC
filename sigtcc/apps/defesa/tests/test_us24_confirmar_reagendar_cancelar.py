"""US-24 Notificar a banca e atualizar o status da sessão: um teste por cenário de aceite (User
Story 4 da spec 007). O cenário 8 (transição para Realizada) é da feat-08 (Edge Cases da spec);
aqui só a fronteira: o serviço único aceita Em Andamento → Realizada (test_base_defesa).

[US-24][RBN-DEF-01.2][RBN-DEF-03.2][RBN-DEF-03.3][FR-017 a FR-023] (tasks T045, T046)
"""

from datetime import datetime, time, timedelta
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import services_turmas
from sigtcc.apps.cadastro.choices import (
    StatusSolicitacao,
    StatusTCC,
    TipoEntrega,
    TipoSolicitacao,
)
from sigtcc.apps.cadastro.models import Notificacoes
from sigtcc.apps.cadastro.services_turmas import ErroTurma
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_secretaria
from sigtcc.apps.cadastro.tests.apoio_orientacao import criar_pedido
from sigtcc.apps.cadastro.tests.apoio_tcc import cadastrar_entrega, enviar_link
from sigtcc.apps.cadastro.tests.apoio_turmas import SI, TesteTurmas, curso
from sigtcc.apps.defesa.choices import EventoDefesa, FormatoSessao, StatusSessao
from sigtcc.apps.defesa.models import Defesas, HistoricoDefesas
from sigtcc.apps.defesa.tests.apoio_defesa import (
    agendar_sessao_de,
    avancar_para,
    docente,
    tcc_apto,
)

AGENDAR = reverse("defesa:agendar")
JUSTIFICATIVA = "Informe uma justificativa de até 500 caracteres"


def daqui_a(dias=10):
    """Data futura para o formulário aceitar."""
    return (timezone.now() + timedelta(days=dias)).date()


class TesteConfirmacao(TesteTurmas):
    """Cenários 1 a 4: confirmação, notificação, troca pendente. [US-24][RBN-DEF-03.2][FR-018]"""

    def setUp(self):
        super().setUp()
        self.tcc, _professor, self.orientador = tcc_apto()
        self.aluno = self.tcc.tcc_alu.alu
        entrega = cadastrar_entrega(self.tcc.tcc_tur, tipo=TipoEntrega.DOCUMENTO_PARA_DEFESA)
        enviar_link(entrega, self.tcc.tcc_alu, "https://drive.example.org/monografia")
        self.banca = [docente(), docente(), docente()]

    def agendar(self):
        self.client.force_login(self.orientador)
        av1, av2, suplente = self.banca
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(
                AGENDAR,
                {
                    "tcc": self.tcc.pk,
                    "data": daqui_a().isoformat(),
                    "h_inicio": "14:00",
                    "formato": FormatoSessao.PRESENCIAL,
                    "local": "Laboratório LSI",
                    "primeiro_avaliador": av1.pk,
                    "segundo_avaliador": av2.pk,
                    "suplente": suplente.pk,
                },
                follow=True,
            )

    def test_cenario_1_grava_agendada_avisa_e_confirma(self):
        resposta = self.agendar()
        self.assertContains(resposta, "Defesa agendada com sucesso")
        self.assertEqual(Defesas.objects.get(def_tcc=self.tcc).def_status, StatusSessao.AGENDADA)
        for pessoa in (self.aluno, self.orientador, *self.banca):
            self.assertEqual(Notificacoes.objects.filter(not_usu=pessoa).count(), 1, pessoa)

    def test_cenario_2_aviso_com_os_dados_e_o_documento(self):
        self.agendar()
        texto = Notificacoes.objects.get(not_usu=self.banca[0]).not_mensagem
        for parte in (
            f"{daqui_a():%d/%m/%Y} às 14:00",
            "Presencial: Laboratório LSI",
            self.tcc.tcc_titulo,
            self.aluno.usu_nome,
            "https://drive.example.org/monografia",
        ):
            self.assertIn(parte, texto)

    def test_cenario_3_sem_troca_pendente_e_publicada_na_lista(self):
        pedido = criar_pedido(self.tcc, docente())
        resposta = self.agendar()
        pedido.refresh_from_db()
        self.assertEqual(pedido.sol_status, StatusSolicitacao.AGUARDANDO_RESPOSTA)
        self.assertEqual(len(resposta.context["sessoes"]), 1)

    def test_cenario_4_troca_pendente_cancelada_e_avisada(self):
        indicado = docente()
        pedido = criar_pedido(self.tcc, indicado, tipo=TipoSolicitacao.TROCA_DE_ORIENTACAO)
        self.agendar()
        pedido.refresh_from_db()
        self.assertEqual(pedido.sol_status, StatusSolicitacao.CANCELADO)
        self.assertTrue(Notificacoes.objects.filter(not_usu=indicado).exists())
        self.assertEqual(Notificacoes.objects.filter(not_usu=self.aluno).count(), 2)


class TesteReagendarECancelarPelaTela(TesteTurmas):
    """Cenários 5, 6 e 9 a 15: reagendamento e cancelamento. [US-24][RBN-DEF-03.3]
    [FR-019][FR-020][FR-022]
    """

    def setUp(self):
        super().setUp()
        self.tcc, self.professor, self.orientador = tcc_apto(SI)
        self.av1, self.av2 = docente(SI), docente(SI)
        self.sessao = agendar_sessao_de(
            self.tcc,
            self.professor,
            {"primeiro_avaliador": self.av1, "segundo_avaliador": self.av2},
            data=daqui_a(),
        )
        self.secretaria = criar_secretaria(curso=curso(SI))
        self.url_sessao = reverse("defesa:sessao", args=[self.sessao.pk])
        self.url_reagendar = reverse("defesa:reagendar", args=[self.sessao.pk])
        self.url_cancelar = reverse("defesa:cancelar", args=[self.sessao.pk])

    def reagendar(self, usuario=None, **troca):
        self.client.force_login(usuario or self.professor)
        dados = {
            "data": daqui_a(20).isoformat(),
            "h_inicio": "10:00",
            "formato": FormatoSessao.REMOTA,
            "link": "https://meet.example.org/nova",
            "justificativa": "Avaliador em viagem",
        }
        dados.update(troca)
        return self.client.post(self.url_reagendar, dados)

    def cancelar(self, usuario=None, justificativa="Aluno pediu adiamento"):
        self.client.force_login(usuario or self.secretaria)
        return self.client.post(self.url_cancelar, {"justificativa": justificativa})

    def test_cenario_5_reagendamento_com_justificativa(self):
        self.client.force_login(self.professor)
        formulario = self.client.get(self.url_reagendar)
        self.assertContains(formulario, "A banca composta e as avaliações já salvas são mantidas.")
        resposta = self.reagendar()
        self.assertRedirects(resposta, self.url_sessao, fetch_redirect_response=False)
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.def_status, StatusSessao.REAGENDADA)
        self.assertEqual(
            (self.sessao.def_data, self.sessao.def_h_inicio), (daqui_a(20), time(10, 0))
        )
        texto = Notificacoes.objects.get(not_usu=self.av1).not_mensagem
        self.assertIn(f"{daqui_a(20):%d/%m/%Y} às 10:00", texto)
        self.assertIn("Remota: https://meet.example.org/nova", texto)
        self.assertContains(self.client.get(self.url_sessao), "Sessão reagendada com sucesso")

    def test_cenario_6_cancelamento_pela_secretaria(self):
        self.client.force_login(self.secretaria)
        self.assertContains(self.client.get(self.url_sessao), self.url_cancelar)
        resposta = self.cancelar()
        self.assertRedirects(resposta, self.url_sessao, fetch_redirect_response=False)
        self.sessao.refresh_from_db()
        self.tcc.refresh_from_db()
        self.assertEqual(self.sessao.def_status, StatusSessao.CANCELADA)
        self.assertEqual(self.tcc.tcc_status, StatusTCC.APTO_PARA_DEFESA)
        for pessoa in (self.tcc.tcc_alu.alu, self.orientador, self.av1, self.av2):
            self.assertTrue(Notificacoes.objects.filter(not_usu=pessoa).exists(), pessoa)

    def test_cenario_9_sem_login(self):
        self.client.logout()
        resposta = self.client.get(self.url_reagendar)
        self.assertRedirects(
            resposta,
            f"{reverse('cadastro:entrar')}?next={self.url_reagendar}",
            fetch_redirect_response=False,
        )

    def test_cenario_10_reagendamento_com_conflito_mantem_os_dados(self):
        outro, _p, outro_ori = tcc_apto(SI)
        agendar_sessao_de(
            outro,
            outro_ori,
            {"primeiro_avaliador": self.av2, "segundo_avaliador": docente(SI)},
            data=daqui_a(20),
            h_inicio=time(10, 30),
        )
        resposta = self.reagendar()
        self.assertContains(resposta, f"{self.av2.usu_nome} (2º Avaliador)")
        form = resposta.context["form"]
        self.assertEqual(form["data"].value(), daqui_a(20).isoformat())
        self.assertEqual(form["justificativa"].value(), "Avaliador em viagem")
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.def_status, StatusSessao.AGENDADA)

    def test_cenario_11_reagendamento_sem_justificativa(self):
        resposta = self.reagendar(justificativa="")
        self.assertFormError(resposta.context["form"], "justificativa", JUSTIFICATIVA)

    def test_cenario_12_e_13_cancelamento_sem_ou_com_justificativa_longa(self):
        for justificativa in ("", "x" * 501):
            with self.subTest(tamanho=len(justificativa)):
                resposta = self.cancelar(justificativa=justificativa)
                self.assertFormError(resposta.context["form"], "justificativa", JUSTIFICATIVA)
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.def_status, StatusSessao.AGENDADA)

    def test_cenario_14_realizada_ou_cancelada_sem_botoes(self):
        for status in (StatusSessao.CANCELADA, StatusSessao.REALIZADA):
            with self.subTest(status=status):
                tcc, professor, _o = tcc_apto(SI)
                sessao = avancar_para(
                    agendar_sessao_de(
                        tcc,
                        professor,
                        {"primeiro_avaliador": docente(SI), "segundo_avaliador": docente(SI)},
                        data=daqui_a(),
                    ),
                    status,
                )
                self.client.force_login(professor)
                pagina = self.client.get(reverse("defesa:sessao", args=[sessao.pk]))
                self.assertNotContains(pagina, reverse("defesa:reagendar", args=[sessao.pk]))
                self.assertNotContains(pagina, reverse("defesa:cancelar", args=[sessao.pk]))
                self.assertEqual(
                    self.client.get(reverse("defesa:cancelar", args=[sessao.pk])).status_code, 403
                )

    def test_cenario_15_perfil_nao_autorizado(self):
        outra_secretaria = criar_secretaria()
        for usuario in (self.orientador, docente(SI), self.av1):
            with self.subTest(usuario=usuario.usu_nome):
                resposta = self.reagendar(usuario)
                self.assertContains(
                    resposta, "Você não tem permissão para esta ação", status_code=403
                )
        self.assertEqual(self.cancelar(outra_secretaria).status_code, 403)
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.def_status, StatusSessao.AGENDADA)


class TesteInicioAutomatico(TesteTurmas):
    """Cenário 7: ao chegar o horário, a sessão passa a Em Andamento, pela tela ou pelo comando.
    [US-24][RBN-DEF-01.2][FR-021]
    """

    def setUp(self):
        super().setUp()
        self.tcc, _professor, self.orientador = tcc_apto()
        self.sessao = agendar_sessao_de(
            self.tcc,
            self.orientador,
            {"primeiro_avaliador": docente(), "segundo_avaliador": docente()},
            data=datetime(2026, 11, 20).date(),
            h_inicio=time(14, 0),
        )

    def no_relogio(self, quando):
        return mock.patch("django.utils.timezone.now", return_value=quando)

    def test_cenario_7_ao_abrir_a_tela_depois_do_horario(self):
        # O login acontece no mesmo relógio, para a sessão de acesso não vencer (US-11).
        with self.no_relogio(datetime(2026, 11, 20, 13, 59)):
            self.client.force_login(self.orientador)
            self.assertEqual(self.client.get(reverse("defesa:defesas")).status_code, 200)
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.def_status, StatusSessao.AGENDADA)
        with self.no_relogio(datetime(2026, 11, 20, 14, 0)):
            self.client.force_login(self.orientador)
            self.client.get(reverse("defesa:sessao", args=[self.sessao.pk]))
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.def_status, StatusSessao.EM_ANDAMENTO)
        evento = HistoricoDefesas.objects.filter(hdf_def=self.sessao).latest("hdf_id")
        self.assertEqual(evento.hdf_evento, EventoDefesa.INICIO_AUTOMATICO)
        self.assertIsNone(evento.hdf_usu)
        self.assertEqual(evento.hdf_data_hora, datetime(2026, 11, 20, 14, 0))

    def test_cenario_7_pelo_comando_agendado_e_idempotente(self):
        saida = StringIO()
        with self.no_relogio(datetime(2026, 11, 20, 14, 5)):
            call_command("iniciar_sessoes", stdout=saida)
            call_command("iniciar_sessoes", stdout=saida)
        self.assertIn("Sessões iniciadas: 1", saida.getvalue())
        self.assertIn("Sessões iniciadas: 0", saida.getvalue())
        self.assertEqual(
            HistoricoDefesas.objects.filter(
                hdf_def=self.sessao, hdf_evento=EventoDefesa.INICIO_AUTOMATICO
            ).count(),
            1,
        )

    def test_em_andamento_bloqueia_a_alteracao_simples_da_banca(self):
        with self.no_relogio(datetime(2026, 11, 20, 14, 10)):
            self.client.force_login(self.orientador)
            resposta = self.client.get(reverse("defesa:alterar_banca", args=[self.sessao.pk]))
        self.assertEqual(resposta.status_code, 403)


class TesteEncerramentoComSessaoAtiva(TesteTurmas):
    """Spec 007, User Story 4, cenário 10: o encerramento da participação continua recusado com
    sessão ativa (MT30, spec 004, sem alteração). [US-24][US-09][RBN-CAD-08.4]
    """

    def test_mt30_continua_valendo(self):
        tcc, professor, orientador = tcc_apto()
        agendar_sessao_de(
            tcc, orientador, {"primeiro_avaliador": docente(), "segundo_avaliador": docente()}
        )
        with self.assertRaises(ErroTurma) as erro:
            services_turmas.encerrar_participacao(
                professor, tcc.tcc_tur_id, tcc.tcc_alu_id, StatusTCC.DESISTENTE, "Trancou o curso"
            )
        self.assertEqual(
            erro.exception.mensagem,
            "Não é possível encerrar a participação: há sessão de defesa ativa.",
        )
