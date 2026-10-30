"""Fase base da spec 007 (Fase 2a do tasks.md): o contrato que a feat-08 e a feat-09 consomem.

[US-21][US-23][US-24][US-40][RBN-DEF-01.2][RBN-DEF-01.6][SC-003] (tasks T023)
"""

from datetime import datetime, time
from datetime import timezone as dt_timezone
from decimal import Decimal

from django.utils import timezone

from sigtcc.apps.cadastro.tests.apoio_turmas import TesteTurmas, criar_defesa_de
from sigtcc.apps.cadastro.tests.fabricas import criar_criterio
from sigtcc.apps.defesa import services_defesa
from sigtcc.apps.defesa.choices import (
    Conceito,
    EventoDefesa,
    FormatoSessao,
    PapelBanca,
    StatusSessao,
)
from sigtcc.apps.defesa.models import (
    Avaliacoes,
    BancaDefesa,
    DefesasPresenciais,
    DefesasRemotas,
    HistoricoDefesas,
)
from sigtcc.apps.defesa.tests.apoio_defesa import (
    agendar_sessao_de,
    avancar_para,
    docente,
    tcc_apto,
)

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


class TesteAgendarSessao(TesteTurmas):
    """agendar_sessao (contrato §1 e §3). [US-21][US-23][RBN-DEF-01.1][RBN-DEF-02.1][FR-007]"""

    def setUp(self):
        self.tcc, self.professor, self.orientador = tcc_apto()
        self.av1, self.av2, self.suplente = docente(), docente(), docente()

    def banca(self, suplente=None):
        return {
            "primeiro_avaliador": self.av1,
            "segundo_avaliador": self.av2,
            "suplente": suplente,
        }

    def test_presencial_grava_sessao_local_banca_e_evento(self):
        sessao = agendar_sessao_de(
            self.tcc, self.orientador, self.banca(self.suplente), local="Ludus"
        )
        self.assertEqual(sessao.def_status, StatusSessao.AGENDADA)
        self.assertEqual(sessao.def_tcc, self.tcc)
        self.assertEqual(DefesasPresenciais.objects.get(dep_def=sessao).dep_local, "Ludus")
        self.assertFalse(DefesasRemotas.objects.filter(der_def=sessao).exists())
        papeis = dict(
            BancaDefesa.objects.filter(ban_def=sessao).values_list("ban_usu_id", "ban_papel")
        )
        self.assertEqual(
            papeis,
            {
                self.orientador.pk: PapelBanca.ORIENTADOR_PRESIDENTE,
                self.av1.pk: PapelBanca.PRIMEIRO_AVALIADOR,
                self.av2.pk: PapelBanca.SEGUNDO_AVALIADOR,
                self.suplente.pk: PapelBanca.SUPLENTE,
            },
        )
        evento = HistoricoDefesas.objects.get(hdf_def=sessao)
        self.assertEqual(evento.hdf_evento, EventoDefesa.AGENDAMENTO)
        self.assertEqual(evento.hdf_status_novo, StatusSessao.AGENDADA)
        self.assertIsNone(evento.hdf_status_anterior)
        self.assertEqual(evento.hdf_usu, self.orientador)

    def test_remota_grava_o_link(self):
        sessao = agendar_sessao_de(
            self.tcc,
            self.professor,
            self.banca(),
            formato=FormatoSessao.REMOTA,
            local=None,
            link="https://meet.example.org/defesa",
        )
        remota = DefesasRemotas.objects.get(der_def=sessao)
        self.assertEqual(remota.der_link, "https://meet.example.org/defesa")
        self.assertFalse(DefesasPresenciais.objects.filter(dep_def=sessao).exists())

    def test_sem_suplente_banca_com_tres_membros(self):
        sessao = agendar_sessao_de(self.tcc, self.orientador, self.banca())
        self.assertEqual(BancaDefesa.objects.filter(ban_def=sessao).count(), 3)

    def test_presidente_e_o_orientador_atual_nunca_o_formulario(self):
        dados = self.banca()
        dados["orientador"] = self.av1  # chave ignorada: o Presidente vem do vínculo ativo
        sessao = agendar_sessao_de(self.tcc, self.orientador, dados)
        presidente = BancaDefesa.objects.get(
            ban_def=sessao, ban_papel=PapelBanca.ORIENTADOR_PRESIDENTE
        )
        self.assertEqual(presidente.ban_usu, self.orientador)

    def test_trocar_o_formato_remove_a_linha_antiga(self):
        sessao = agendar_sessao_de(self.tcc, self.orientador, self.banca())
        sessao.def_formato = FormatoSessao.REMOTA
        sessao.save(update_fields=["def_formato"])
        services_defesa._gravar_local_ou_link(sessao, link="https://meet.example.org/x")
        self.assertFalse(DefesasPresenciais.objects.filter(dep_def=sessao).exists())
        self.assertTrue(DefesasRemotas.objects.filter(der_def=sessao).exists())


class TesteMembrosEfetivos(TesteTurmas):
    """membros_efetivos (contrato §2). [US-23][RBN-DEF-02.1][RBN-DEF-02.2]"""

    def setUp(self):
        self.tcc, _professor, self.orientador = tcc_apto()
        self.av1, self.av2, self.suplente = docente(), docente(), docente()
        self.sessao = agendar_sessao_de(
            self.tcc,
            self.orientador,
            {
                "primeiro_avaliador": self.av1,
                "segundo_avaliador": self.av2,
                "suplente": self.suplente,
            },
        )

    def test_tres_titulares_em_ordem_sem_o_suplente_nao_acionado(self):
        self.assertEqual(
            services_defesa.membros_efetivos(self.sessao), [self.orientador, self.av1, self.av2]
        )

    def test_suplente_acionado_substitui_o_titular_ausente(self):
        # Mesmo efeito do acionamento (RBN-DEF-02.2): o suplente assume o papel do ausente.
        BancaDefesa.objects.filter(ban_def=self.sessao, ban_usu=self.av2).delete()
        BancaDefesa.objects.filter(ban_def=self.sessao, ban_usu=self.suplente).update(
            ban_papel=PapelBanca.SEGUNDO_AVALIADOR, ban_usu_substituido=self.av2
        )
        self.assertEqual(
            services_defesa.membros_efetivos(self.sessao),
            [self.orientador, self.av1, self.suplente],
        )


class TesteDescartarAvaliacoesStub(TesteTurmas):
    """Stub de descartar_avaliacoes (contrato §6). [US-24][RBN-DEF-03.3][FR-020]"""

    def test_so_registra_em_log_sem_apagar_avaliacoes(self):
        tcc, _professor, orientador = tcc_apto()
        sessao = agendar_sessao_de(tcc, orientador)
        avaliacao = Avaliacoes.objects.create(
            ava_def=sessao,
            ava_usu=orientador,
            ava_cri=criar_criterio(),
            ava_conceito=Conceito.COMPETENTE,
            ava_nota=Decimal("7.0"),
            ava_data_hora=timezone.now(),
        )
        for membro in (None, orientador):
            with self.subTest(membro=membro):
                with self.assertLogs("sigtcc.defesa", level="INFO") as log:
                    self.assertIsNone(services_defesa.descartar_avaliacoes(sessao, membro))
                self.assertIn(f"sessão {sessao.pk}", log.output[0])
        self.assertTrue(Avaliacoes.objects.filter(pk=avaliacao.pk).exists())


class TesteAvancarPara(TesteTurmas):
    """O caminho de teste chega a cada status só pelo serviço único. [SC-003]"""

    def test_cada_status_pelo_servico(self):
        for status in StatusSessao:
            with self.subTest(status=status):
                tcc, _professor, orientador = tcc_apto()
                sessao = avancar_para(agendar_sessao_de(tcc, orientador), status)
                sessao.refresh_from_db()
                self.assertEqual(sessao.def_status, status)
                ultimo = HistoricoDefesas.objects.filter(hdf_def=sessao).latest("hdf_id")
                self.assertEqual(ultimo.hdf_status_novo, status)
