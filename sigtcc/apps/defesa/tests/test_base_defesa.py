"""Fase base da spec 007 (Fase 2a do tasks.md): o contrato que a feat-08 e a feat-09 consomem.

[US-21][US-23][US-24][US-40][RBN-DEF-01.2][RBN-DEF-01.6][SC-003] (tasks T023)
"""

from datetime import datetime, time
from datetime import timezone as dt_timezone

from sigtcc.apps.cadastro.tests.apoio_turmas import TesteTurmas, criar_defesa_de
from sigtcc.apps.defesa import services_defesa
from sigtcc.apps.defesa.choices import EventoDefesa, StatusSessao
from sigtcc.apps.defesa.models import HistoricoDefesas
from sigtcc.apps.defesa.tests.apoio_defesa import docente, tcc_apto

TODOS_OS_STATUS = list(StatusSessao)


class TesteTransicaoDeStatus(TesteTurmas):
    """transicionar_status e TRANSICOES_VALIDAS (contrato §1). [US-24][RBN-DEF-01.2][FR-017]"""

    def setUp(self):
        self.tcc, self.professor, self.orientador = tcc_apto()

    def sessao(self, status):
        return criar_defesa_de(self.tcc, status)

    def test_todas_as_transicoes_validas_gravam_status_e_evento(self):
        for anterior, novo in services_defesa.TRANSICOES_VALIDAS:
            with self.subTest(anterior=anterior, novo=novo):
                sessao = self.sessao(anterior)
                evento = services_defesa.transicionar_status(
                    sessao, novo, self.orientador, "Justificativa"
                )
                sessao.refresh_from_db()
                self.assertEqual(sessao.def_status, novo)
                self.assertEqual(evento.hdf_evento, services_defesa.EVENTO_DA_TRANSICAO[novo])
                self.assertEqual(evento.hdf_status_anterior, anterior)
                self.assertEqual(evento.hdf_status_novo, novo)
                self.assertEqual(evento.hdf_justificativa, "Justificativa")
                self.assertEqual(evento.hdf_usu, self.orientador)

    def test_transicao_fora_da_tabela_nao_grava_nada(self):
        invalidas = [
            (a, n)
            for a in TODOS_OS_STATUS
            for n in TODOS_OS_STATUS
            if (a, n) not in services_defesa.TRANSICOES_VALIDAS
        ]
        # Inclui as saídas de Realizada e Cancelada e a volta para Agendada.
        self.assertIn((StatusSessao.REALIZADA, StatusSessao.CANCELADA), invalidas)
        self.assertIn((StatusSessao.CANCELADA, StatusSessao.AGENDADA), invalidas)
        self.assertIn((StatusSessao.AGENDADA, StatusSessao.REALIZADA), invalidas)
        for anterior, novo in invalidas:
            with self.subTest(anterior=anterior, novo=novo):
                sessao = self.sessao(anterior)
                with self.assertRaises(ValueError):
                    services_defesa.transicionar_status(sessao, novo, self.orientador)
                sessao.refresh_from_db()
                self.assertEqual(sessao.def_status, anterior)
                self.assertFalse(HistoricoDefesas.objects.filter(hdf_def=sessao).exists())

    def test_cada_status_novo_tem_um_unico_evento(self):
        destinos = {novo for _anterior, novo in services_defesa.TRANSICOES_VALIDAS}
        self.assertEqual(destinos, set(services_defesa.EVENTO_DA_TRANSICAO))
        self.assertNotIn(StatusSessao.AGENDADA, destinos)

    def test_inicio_automatico_sem_autor(self):
        sessao = self.sessao(StatusSessao.AGENDADA)
        evento = services_defesa.transicionar_status(sessao, StatusSessao.EM_ANDAMENTO, None)
        self.assertIsNone(evento.hdf_usu)
        self.assertEqual(evento.hdf_evento, EventoDefesa.INICIO_AUTOMATICO)

    def test_reagendamento_guarda_datas_e_horas(self):
        sessao = self.sessao(StatusSessao.AGENDADA)
        evento = services_defesa.transicionar_status(
            sessao,
            StatusSessao.REAGENDADA,
            self.professor,
            "Banca indisponível",
            data_anterior=sessao.def_data,
            hora_anterior=sessao.def_h_inicio,
            data_nova=datetime(2026, 12, 1).date(),
            hora_nova=time(10, 0),
        )
        self.assertEqual(evento.hdf_data_anterior, sessao.def_data)
        self.assertEqual(evento.hdf_hora_nova, time(10, 0))


class TesteRegistrarEvento(TesteTurmas):
    """registrar_evento (contrato §2). [US-40][RBN-DEF-01.6][FR-023][FR-029]"""

    def setUp(self):
        self.tcc, self.professor, self.orientador = tcc_apto()
        self.sessao = criar_defesa_de(self.tcc, StatusSessao.AGENDADA)

    def test_evento_sem_mudanca_de_status(self):
        removido, incluido = docente(), docente()
        evento = services_defesa.registrar_evento(
            self.sessao,
            EventoDefesa.ALTERACAO_DA_BANCA,
            "Avaliador em licença",
            self.orientador,
            membro_removido=removido,
            membro_incluido=incluido,
        )
        self.assertEqual(evento.hdf_membro_removido, removido)
        self.assertEqual(evento.hdf_membro_incluido, incluido)
        self.assertIsNone(evento.hdf_status_anterior)
        self.assertIsNone(evento.hdf_status_novo)
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.def_status, StatusSessao.AGENDADA)

    def test_usa_o_instante_informado(self):
        agora = datetime(2026, 10, 30, 14, 0, tzinfo=dt_timezone.utc)
        evento = services_defesa.registrar_evento(
            self.sessao, EventoDefesa.AGENDAMENTO, None, self.orientador, agora=agora
        )
        self.assertEqual(evento.hdf_data_hora, agora)

    def test_dado_desconhecido_nao_grava(self):
        with self.assertRaises(TypeError):
            services_defesa.registrar_evento(
                self.sessao, EventoDefesa.AGENDAMENTO, None, None, local="Sala 1"
            )
        self.assertFalse(HistoricoDefesas.objects.exists())
