"""Fase base da spec 007 (Fase 2a do tasks.md): o contrato que a feat-08 e a feat-09 consomem.

[US-21][US-23][US-24][US-40][RBN-DEF-01.2][RBN-DEF-01.6][SC-003] (tasks T023)
"""

import shutil
import tempfile
from collections import Counter
from datetime import datetime, time, timedelta
from decimal import Decimal
from io import StringIO
from unittest import mock

from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.db import connection
from django.http import Http404
from django.test import override_settings
from django.utils import timezone

from sigtcc.apps.cadastro import services_contas, services_orientacao
from sigtcc.apps.cadastro.choices import (
    StatusConta,
    StatusOrientacao,
    StatusSolicitacao,
    StatusTCC,
    StatusTurma,
    TipoEntrega,
    TipoSolicitacao,
)
from sigtcc.apps.cadastro.models import (
    Notificacoes,
    Orientacoes,
    SolicitacoesOrientacao,
    TCCs,
    Turmas,
    Usuarios,
)
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_membro_externo, criar_secretaria
from sigtcc.apps.cadastro.tests.apoio_orientacao import criar_pedido, vincular_coorientador
from sigtcc.apps.cadastro.tests.apoio_tcc import cadastrar_entrega, enviar_link
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    LC,
    SI,
    TesteTurmas,
    criar_defesa_de,
    curso,
)
from sigtcc.apps.cadastro.tests.fabricas import criar_criterio
from sigtcc.apps.defesa import permissoes_defesa, services_avaliacoes, services_defesa
from sigtcc.apps.defesa.choices import (
    Conceito,
    EventoDefesa,
    FormatoSessao,
    PapelBanca,
    Parecer,
    StatusSessao,
)
from sigtcc.apps.defesa.models import (
    Avaliacoes,
    BancaDefesa,
    Defesas,
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
        super().setUp()
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
        super().setUp()
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
        agora = datetime(2026, 10, 30, 14, 0)
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
        super().setUp()
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
        super().setUp()
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


class TesteDescartarAvaliacoesDelegacao(TesteTurmas):
    """descartar_avaliacoes delega para services_avaliacoes (contrato §6; spec 008, IC-01 e
    IC-03): apaga as linhas de Avaliacoes e limpa o envio, com a mesma assinatura.
    [US-24][RBN-DEF-03.3][FR-020][spec 008 FR-034]
    """

    def test_apaga_linhas_e_limpa_o_envio(self):
        tcc, _professor, orientador = tcc_apto()
        sessao = agendar_sessao_de(tcc, orientador)
        avaliador = services_defesa.membros_efetivos(sessao)[1]
        criterio = criar_criterio()
        for membro in (orientador, avaliador):
            Avaliacoes.objects.create(
                ava_def=sessao,
                ava_usu=membro,
                ava_cri=criterio,
                ava_conceito=Conceito.COMPETENTE,
                ava_nota=Decimal("7.0"),
                ava_data_hora=timezone.now(),
            )
        BancaDefesa.objects.filter(ban_def=sessao, ban_usu=orientador).update(
            ban_data_envio=timezone.now()
        )
        with mock.patch(
            "sigtcc.apps.defesa.services_avaliacoes.descartar_avaliacoes",
            wraps=services_avaliacoes.descartar_avaliacoes,
        ) as real:
            with self.assertLogs("sigtcc.defesa", level="INFO") as log:
                self.assertIsNone(services_defesa.descartar_avaliacoes(sessao, orientador))
        real.assert_called_once_with(sessao, orientador)
        self.assertIn(f"membro {orientador.pk}", log.output[0])
        self.assertFalse(Avaliacoes.objects.filter(ava_def=sessao, ava_usu=orientador).exists())
        self.assertTrue(Avaliacoes.objects.filter(ava_def=sessao, ava_usu=avaliador).exists())
        linha = BancaDefesa.objects.get(ban_def=sessao, ban_usu=orientador)
        self.assertIsNone(linha.ban_data_envio)
        services_defesa.descartar_avaliacoes(sessao)
        self.assertFalse(Avaliacoes.objects.filter(ava_def=sessao).exists())


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


class TestePodeAgendar(TesteTurmas):
    """Quem agenda, pelo curso da turma do TCC. [US-21][RBN-DEF-01.3][FR-003]"""

    def test_engenharia_so_o_orientador(self):
        tcc, professor, orientador = tcc_apto()
        self.assertTrue(permissoes_defesa.pode_agendar(orientador, tcc))
        self.assertFalse(permissoes_defesa.pode_agendar(professor, tcc))
        self.assertFalse(permissoes_defesa.pode_agendar(docente(), tcc))

    def test_sistemas_e_licenciatura_so_o_professor_da_disciplina(self):
        for curso_nome in (SI, LC):
            with self.subTest(curso=curso_nome):
                tcc, professor, orientador = tcc_apto(curso_nome)
                self.assertTrue(permissoes_defesa.pode_agendar(professor, tcc))
                self.assertFalse(permissoes_defesa.pode_agendar(orientador, tcc))
                self.assertFalse(permissoes_defesa.pode_agendar(docente(curso_nome), tcc))


class TesteElegibilidade(TesteTurmas):
    """tcc_elegivel e tccs_elegiveis. [US-21][RBN-DEF-01.1][RBN-DEF-01.3][FR-001][FR-003]"""

    def test_apto_sem_sessao_e_elegivel(self):
        tcc, _professor, orientador = tcc_apto()
        self.assertTrue(services_defesa.tcc_elegivel(tcc))
        self.assertEqual(list(services_defesa.tccs_elegiveis(orientador)), [tcc])

    def test_sessao_ativa_tira_da_lista_e_encerrada_devolve(self):
        for status in StatusSessao:
            with self.subTest(status=status):
                tcc, _professor, orientador = tcc_apto()
                avancar_para(agendar_sessao_de(tcc, orientador), status)
                ativa = status in (
                    StatusSessao.AGENDADA,
                    StatusSessao.REAGENDADA,
                    StatusSessao.EM_ANDAMENTO,
                )
                self.assertEqual(services_defesa.tcc_elegivel(tcc), not ativa)
                self.assertEqual(tcc in services_defesa.tccs_elegiveis(orientador), not ativa)

    def test_status_diferente_de_apto_nao_entra(self):
        tcc, _professor, orientador = tcc_apto()
        tcc.tcc_status = StatusTCC.EM_ANDAMENTO
        tcc.save(update_fields=["tcc_status"])
        self.assertFalse(services_defesa.tcc_elegivel(tcc))
        self.assertFalse(services_defesa.tccs_elegiveis(orientador).exists())

    def test_turma_arquivada_nao_entra(self):
        tcc, _professor, orientador = tcc_apto()
        Turmas.objects.filter(pk=tcc.tcc_tur_id).update(tur_status=StatusTurma.ARQUIVADA)
        tcc.refresh_from_db()
        self.assertFalse(services_defesa.tcc_elegivel(tcc))
        self.assertFalse(services_defesa.tccs_elegiveis(orientador).exists())

    def test_lista_igual_a_permissao_mais_elegibilidade(self):
        professor_ec, orientador_ec = docente(), docente()
        professor_si, orientador_si = docente(SI), docente(SI)
        tccs = [
            tcc_apto(professor=professor_ec, orientador=orientador_ec)[0],
            tcc_apto(professor=professor_ec, orientador=docente())[0],
            tcc_apto(SI, professor=professor_si, orientador=orientador_si)[0],
            tcc_apto(SI, professor=docente(SI), orientador=orientador_si)[0],
            tcc_apto(LC, professor=professor_ec, orientador=orientador_ec)[0],
        ]
        avancar_para(agendar_sessao_de(tccs[0], orientador_ec), StatusSessao.REAGENDADA)
        for usuario in (professor_ec, orientador_ec, professor_si, orientador_si):
            with self.subTest(usuario=usuario.usu_nome):
                esperado = {
                    tcc.pk
                    for tcc in tccs
                    if permissoes_defesa.pode_agendar(usuario, tcc)
                    and services_defesa.tcc_elegivel(tcc)
                }
                lista = {tcc.pk for tcc in services_defesa.tccs_elegiveis(usuario)}
                self.assertEqual(lista, esperado)
        # Professor de EC não agenda em EC, mas agenda o TCC de Licenciatura da sua turma.
        self.assertEqual({t.pk for t in services_defesa.tccs_elegiveis(professor_ec)}, {tccs[4].pk})


class TestePopularDemo(TesteTurmas):
    """popular_demo com o cenário do roteiro da spec 007 (contrato §5; IC-05; T056): uma sessão
    em cada status, criadas pelos serviços, e os TCCs Aptos sem sessão para agendar. Spec 008
    (IC-08): avaliações de exemplo só pelos serviços, uma segunda sessão Em Andamento pronta para
    liberar e dois resultados liberados; as cópias de assinatura vão para um MEDIA_ROOT
    temporário. [US-21][US-22][US-23][US-24][US-40][RBN-DEF-01.2][US-25][US-27]
    """

    @classmethod
    def setUpClass(cls):
        cls._midia = tempfile.mkdtemp(prefix="sigtcc_demo_")
        cls.enterClassContext(override_settings(MEDIA_ROOT=cls._midia))
        cls.addClassCleanup(shutil.rmtree, cls._midia, ignore_errors=True)
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        nome_banco = connection.settings_dict["NAME"]
        cls.saida = StringIO()
        with mock.patch("builtins.input", return_value=nome_banco):
            call_command(
                "popular_demo", "--senha", "Demo2026sig", "--confirmar", "--local", stdout=cls.saida
            )

    def usuario(self, nome):
        return Usuarios.objects.get(usu_nome=nome)

    def test_uma_sessao_em_cada_status_criada_pelos_servicos(self):
        contagem = Counter(Defesas.objects.values_list("def_status", flat=True))
        # Spec 008 (IC-08): mais uma Em Andamento (pronta para liberar) e uma Realizada (TCC 1).
        esperado = Counter(StatusSessao.values)
        esperado.update([StatusSessao.EM_ANDAMENTO, StatusSessao.REALIZADA])
        self.assertEqual(contagem, esperado)
        for sessao in Defesas.objects.select_related("def_tcc__tcc_tur__tur_cur"):
            with self.subTest(status=sessao.def_status):
                primeiro = HistoricoDefesas.objects.filter(hdf_def=sessao).earliest("hdf_id")
                self.assertEqual(primeiro.hdf_evento, EventoDefesa.AGENDAMENTO)
                # A sessão do TCC 1 de 2026/1 (spec 008) é de turma já arquivada, com a
                # orientação encerrada: a regra foi conferida pelo próprio agendar() na época.
                if sessao.def_tcc.tcc_tur.tur_status == StatusTurma.ATIVA:
                    self.assertTrue(
                        permissoes_defesa.pode_agendar(primeiro.hdf_usu, sessao.def_tcc),
                        "quem agendou segue a regra do curso",
                    )
                self.assertEqual(len(services_defesa.membros_efetivos(sessao)), 3)
        realizada = Defesas.objects.get(
            def_status=StatusSessao.REALIZADA, def_parecer=Parecer.APROVADO
        )
        self.assertEqual(realizada.def_tcc.tcc_status, StatusTCC.APROVADO)
        cancelada = Defesas.objects.get(def_status=StatusSessao.CANCELADA)
        self.assertTrue(services_defesa.tcc_elegivel(cancelada.def_tcc))

    def test_agendada_daqui_a_3_dias_com_docente_extra_e_suplente(self):
        agendada = Defesas.objects.get(def_status=StatusSessao.AGENDADA)
        self.assertEqual(agendada.def_data, timezone.now().date() + timedelta(days=3))
        self.assertEqual(agendada.def_h_inicio, time(14, 0))
        banca = services_defesa.banca_por_papel(agendada)
        self.assertEqual(banca[PapelBanca.PRIMEIRO_AVALIADOR], self.usuario("Beatriz Lemos Aragão"))
        self.assertIn(PapelBanca.SUPLENTE, banca)
        em_andamento = Defesas.objects.filter(def_status=StatusSessao.EM_ANDAMENTO)
        self.assertTrue(
            [s for s in em_andamento if PapelBanca.SUPLENTE in services_defesa.banca_por_papel(s)]
        )

    def test_cenario_do_painel_de_atividades(self):
        """Spec 010 (IC-05): troca de orientador real e Suplente acionado em período passado.
        [US-31][RBN-REL-01.1][FR-023][FR-024]
        """
        trocado = Orientacoes.objects.get(
            ori_doc=self.usuario("Adriana Lopes Viana").docentes,
            ori_tcc__tcc_tur__tur_identificador="ECP-TCC1-2026.2",
            ori_status=StatusOrientacao.ENCERRADA,
        )
        self.assertIsNotNone(trocado.ori_data_fim)
        self.assertTrue(
            Orientacoes.objects.filter(
                ori_tcc=trocado.ori_tcc,
                ori_doc=self.usuario("Carlos Eduardo Pinheiro").docentes,
                ori_status=StatusOrientacao.ATIVA,
            ).exists()
        )
        acionado = BancaDefesa.objects.get(ban_usu_substituido__isnull=False)
        self.assertEqual(acionado.ban_usu, self.usuario("Henrique Matos Couto"))
        self.assertEqual(acionado.ban_def.def_status, StatusSessao.REALIZADA)
        self.assertEqual(acionado.ban_def.def_tcc.tcc_tur.tur_semestre, 1)
        self.assertIn("Roteiro da spec 010", self.saida.getvalue())

    def test_tccs_aptos_sem_sessao_para_agendar(self):
        aptos = [
            tcc
            for tcc in TCCs.objects.filter(tcc_status=StatusTCC.APTO_PARA_DEFESA)
            if services_defesa.tcc_elegivel(tcc)
        ]
        por_curso = Counter(tcc.tcc_tur.tur_cur.cur_nome for tcc in aptos)
        self.assertEqual(por_curso, Counter({EC: 3, SI: 2, LC: 1}))
        for tcc in aptos:
            with self.subTest(aluno=tcc.tcc_alu.alu.usu_nome):
                self.assertIsNotNone(services_orientacao.orientador_atual(tcc))
                self.assertTrue(tcc.tcc_ari_id)
                self.assertTrue(tcc.palavraschavetcc_set.exists())
                self.assertTrue(services_defesa.link_do_documento(tcc))
                if tcc.tcc_tur.tur_cur.cur_nome != LC:
                    self.assertTrue(services_orientacao.coorientadores_ativos(tcc))
        troca = SolicitacoesOrientacao.objects.get(
            sol_tipo=TipoSolicitacao.TROCA_DE_ORIENTACAO,
            sol_status=StatusSolicitacao.AGUARDANDO_RESPOSTA,
            sol_tcc__tcc_status=StatusTCC.APTO_PARA_DEFESA,
        )
        self.assertIn(troca.sol_tcc, aptos)

    def test_quem_agenda_cada_tcc_e_o_nao_apto(self):
        orientadora = self.usuario("Adriana Lopes Viana")
        professor_si = self.usuario("Eduardo Farias Brito")
        professor_ec = self.usuario("Fernando Costa Lima")
        da_orientadora = services_defesa.tccs_elegiveis(orientadora)
        self.assertEqual(da_orientadora.count(), 1)
        nao_apto = TCCs.objects.filter(
            tcc_status=StatusTCC.EM_ANDAMENTO,
            orientacoes__ori_doc_id=orientadora.pk,
            tcc_tur__tur_identificador="ECP-TCC1-2026.2",
        )
        self.assertTrue(nao_apto.exists())
        self.assertFalse(set(nao_apto) & set(da_orientadora))
        self.assertEqual(services_defesa.tccs_elegiveis(professor_si).count(), 2)
        self.assertFalse(services_defesa.tccs_elegiveis(professor_ec).exists())

    def test_membros_externos_e_contas(self):
        self.assertEqual(self.usuario("Marcos Vinícius Teixeira").usu_status, StatusConta.ATIVA)
        self.assertEqual(self.usuario("Helena Duarte Campos").usu_status, StatusConta.EXPIRADA)
        for nome in ("Beatriz Lemos Aragão", "Henrique Matos Couto", "Sandra Pires Lacerda"):
            self.assertEqual(self.usuario(nome).usu_status, StatusConta.ATIVA)

    def test_avaliacoes_de_demonstracao_pelos_servicos(self):
        sessoes = Defesas.objects.filter(def_status=StatusSessao.EM_ANDAMENTO)
        estados = sorted(
            sorted(item["estado"] for item in services_avaliacoes.estados_da_banca(sessao))
            for sessao in sessoes
        )
        self.assertEqual(
            estados,
            [["Enviada", "Enviada", "Enviada"], ["Enviada", "Enviada", "Rascunho salvo"]],
        )
        pronta = next(s for s in sessoes if services_avaliacoes.apuracao(s)["completos"])
        apuracao = services_avaliacoes.apuracao(pronta)
        self.assertTrue(apuracao["pode_registrar_parecer"])
        self.assertFalse(apuracao["liberar_habilitado"])
        liberadas = Defesas.objects.filter(def_data_liberacao_resultado__isnull=False)
        self.assertEqual(
            sorted(liberadas.values_list("def_parecer", flat=True)),
            [Parecer.APROVADO, Parecer.APROVADO_PARA_TCC_2],
        )
        for sessao in liberadas:
            with self.subTest(parecer=sessao.def_parecer):
                self.assertEqual(sessao.def_status, StatusSessao.REALIZADA)
                self.assertEqual(sessao.def_tcc.tcc_status, sessao.def_parecer)
                evento = HistoricoDefesas.objects.filter(hdf_def=sessao).latest("hdf_id")
                self.assertEqual(evento.hdf_evento, EventoDefesa.LIBERACAO_DO_RESULTADO)
        copias = BancaDefesa.objects.filter(ban_assinatura_path__isnull=False)
        self.assertEqual(copias.count(), 11)
        self.assertTrue(all(c.ban_assinatura_path.startswith("assinaturas_banca/") for c in copias))

    def test_imprime_o_roteiro(self):
        texto = self.saida.getvalue()
        for trecho in (
            "Roteiro da spec 007",
            "Quem pode agendar o quê",
            "Sessões de defesa:",
            "Beatriz Lemos Aragão",
            "Acionar suplente",
            "Roteiro da spec 008",
        ):
            self.assertIn(trecho, texto)


class TesteVerificarConflito(TesteTurmas):
    """_verificar_conflito: janela de 1 hora, só membros da banca, nada gravado.
    [US-22][RBN-DEF-03.1][FR-014][FR-015][FR-016]
    """

    DIA = datetime(2026, 11, 20).date()

    def setUp(self):
        super().setUp()
        self.tcc, _professor, self.orientador = tcc_apto()
        self.av1, self.av2 = docente(), docente()
        self.sessao = agendar_sessao_de(
            self.tcc,
            self.orientador,
            {"primeiro_avaliador": self.av1, "segundo_avaliador": self.av2},
            data=self.DIA,
            h_inicio=time(9, 0),
        )

    def conferir(self, membros, hora, dia=None, excluir=None):
        services_defesa._verificar_conflito(membros, dia or self.DIA, hora, excluir)

    def test_sobreposicao_rejeita_com_o_nome_e_o_papel(self):
        with self.assertRaises(services_defesa.ConflitoDeHorario) as erro:
            self.conferir([(self.av1, PapelBanca.SEGUNDO_AVALIADOR)], time(9, 30))
        self.assertEqual(erro.exception.membros, [(self.av1, PapelBanca.SEGUNDO_AVALIADOR)])
        self.assertIn(f"{self.av1.usu_nome} (2º Avaliador)", erro.exception.mensagem)

    def test_sessoes_encostadas_nao_conflitam(self):
        self.conferir([(self.av1, PapelBanca.PRIMEIRO_AVALIADOR)], time(10, 0))
        self.conferir([(self.av1, PapelBanca.PRIMEIRO_AVALIADOR)], time(8, 0))

    def test_varios_membros_numa_unica_mensagem(self):
        livre = docente()
        membros = [
            (self.orientador, PapelBanca.ORIENTADOR_PRESIDENTE),
            (livre, PapelBanca.PRIMEIRO_AVALIADOR),
            (self.av2, PapelBanca.SUPLENTE),
        ]
        with self.assertRaises(services_defesa.ConflitoDeHorario) as erro:
            self.conferir(membros, time(8, 30))
        self.assertEqual(
            erro.exception.membros,
            [(self.orientador, PapelBanca.ORIENTADOR_PRESIDENTE), (self.av2, PapelBanca.SUPLENTE)],
        )
        mensagem = erro.exception.mensagem
        self.assertIn(f"{self.orientador.usu_nome} (Orientador)", mensagem)
        self.assertIn(f"{self.av2.usu_nome} (Suplente)", mensagem)
        self.assertNotIn(livre.usu_nome, mensagem)

    def test_conta_agendada_reagendada_e_em_andamento(self):
        for status in (StatusSessao.REAGENDADA, StatusSessao.EM_ANDAMENTO):
            with self.subTest(status=status):
                tcc, _professor, orientador = tcc_apto()
                membro = docente()
                avancar_para(
                    agendar_sessao_de(
                        tcc,
                        orientador,
                        {"primeiro_avaliador": membro, "segundo_avaliador": docente()},
                        data=self.DIA,
                        h_inicio=time(14, 0),
                    ),
                    status,
                )
                with self.assertRaises(services_defesa.ConflitoDeHorario):
                    self.conferir([(membro, PapelBanca.PRIMEIRO_AVALIADOR)], time(14, 30))

    def test_ignora_sessao_cancelada_e_realizada(self):
        for status in (StatusSessao.CANCELADA, StatusSessao.REALIZADA):
            with self.subTest(status=status):
                tcc, _professor, orientador = tcc_apto()
                membro = docente()
                avancar_para(
                    agendar_sessao_de(
                        tcc,
                        orientador,
                        {"primeiro_avaliador": membro, "segundo_avaliador": docente()},
                        data=self.DIA,
                        h_inicio=time(16, 0),
                    ),
                    status,
                )
                self.conferir([(membro, PapelBanca.PRIMEIRO_AVALIADOR)], time(16, 0))

    def test_desconsidera_a_propria_sessao(self):
        self.conferir([(self.av1, PapelBanca.PRIMEIRO_AVALIADOR)], time(9, 30), excluir=self.sessao)

    def test_janela_que_passa_da_meia_noite(self):
        tcc, _professor, orientador = tcc_apto()
        membro = docente()
        agendar_sessao_de(
            tcc,
            orientador,
            {"primeiro_avaliador": membro, "segundo_avaliador": docente()},
            data=self.DIA,
            h_inicio=time(23, 30),
        )
        with self.assertRaises(services_defesa.ConflitoDeHorario):
            self.conferir(
                [(membro, PapelBanca.PRIMEIRO_AVALIADOR)],
                time(0, 0),
                dia=datetime(2026, 11, 21).date(),
            )

    def test_mesmo_local_com_banca_diferente_nao_conflita(self):
        self.conferir([(docente(), PapelBanca.PRIMEIRO_AVALIADOR)], time(9, 0))

    def test_nao_grava_nada(self):
        antes = (Defesas.objects.count(), BancaDefesa.objects.count())
        with self.assertRaises(services_defesa.ConflitoDeHorario):
            self.conferir([(self.av1, PapelBanca.PRIMEIRO_AVALIADOR)], time(9, 0))
        self.assertEqual((Defesas.objects.count(), BancaDefesa.objects.count()), antes)


class TesteTravarMembros(TesteTurmas):
    """_travar_membros trava os usuários em ordem de pk, sem repetir. [US-22][RBN-DEF-03.1]"""

    def test_ordem_por_pk_sem_repeticao(self):
        a, b = docente(), docente()
        travados = services_defesa._travar_membros([b.pk, a.pk, b.pk])
        self.assertEqual([u.pk for u in travados], sorted([a.pk, b.pk]))


class TesteAlterarBanca(TesteTurmas):
    """alterar_banca (US-23 C). [US-23][RBN-DEF-02.4][FR-011][FR-012][FR-015]"""

    def setUp(self):
        super().setUp()
        self.tcc, self.professor, self.orientador = tcc_apto()
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

    def banca(self, **trocas):
        banca = {
            PapelBanca.PRIMEIRO_AVALIADOR: self.av1,
            PapelBanca.SEGUNDO_AVALIADOR: self.av2,
            PapelBanca.SUPLENTE: self.suplente,
        }
        banca.update(trocas)
        return banca

    def alterar(self, banca, usuario=None, justificativa="Avaliador em licença"):
        return services_defesa.alterar_banca(
            usuario or self.orientador, self.sessao.pk, banca, justificativa
        )

    def test_troca_grava_evento_descarta_e_avisa(self):
        novo = docente()
        aluno = self.tcc.tcc_alu.alu
        with self.assertLogs("sigtcc.defesa", level="INFO") as log:
            self.alterar(self.banca(**{PapelBanca.SEGUNDO_AVALIADOR: novo}))
        self.assertEqual(
            services_defesa.banca_por_papel(self.sessao)[PapelBanca.SEGUNDO_AVALIADOR], novo
        )
        self.assertIn(f"membro {self.av2.pk}", log.output[0])
        evento = HistoricoDefesas.objects.filter(hdf_def=self.sessao).latest("hdf_id")
        self.assertEqual(evento.hdf_evento, EventoDefesa.ALTERACAO_DA_BANCA)
        self.assertEqual((evento.hdf_membro_removido, evento.hdf_membro_incluido), (self.av2, novo))
        self.assertEqual(evento.hdf_justificativa, "Avaliador em licença")
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.def_status, StatusSessao.AGENDADA)
        for pessoa in (novo, self.av2, aluno):
            self.assertTrue(Notificacoes.objects.filter(not_usu=pessoa).exists(), pessoa)

    def test_sem_troca_nao_grava(self):
        self.alterar(self.banca())
        self.assertEqual(HistoricoDefesas.objects.filter(hdf_def=self.sessao).count(), 1)

    def test_tirar_o_suplente(self):
        self.alterar(self.banca(**{PapelBanca.SUPLENTE: None}))
        self.assertNotIn(PapelBanca.SUPLENTE, services_defesa.banca_por_papel(self.sessao))

    def test_justificativa_vazia_ou_longa(self):
        for justificativa in ("", "x" * 501):
            with self.subTest(tamanho=len(justificativa)):
                with self.assertRaises(services_defesa.ErroDefesa) as erro:
                    self.alterar(
                        self.banca(**{PapelBanca.SEGUNDO_AVALIADOR: docente()}),
                        justificativa=justificativa,
                    )
                self.assertEqual(
                    erro.exception.mensagem, "Informe uma justificativa de até 500 caracteres"
                )

    def test_trocar_o_presidente_exige_reagendamento(self):
        banca = self.banca(**{PapelBanca.ORIENTADOR_PRESIDENTE: docente()})
        with self.assertRaises(services_defesa.ErroDefesa) as erro:
            self.alterar(banca)
        self.assertEqual(
            erro.exception.mensagem, "A ausência do Orientador exige o reagendamento da sessão"
        )

    def test_repetido_ou_da_orientacao_recusa(self):
        coorientador = docente()
        vincular_coorientador(self.tcc, coorientador)
        for banca in (
            self.banca(**{PapelBanca.SUPLENTE: self.av1}),
            self.banca(**{PapelBanca.PRIMEIRO_AVALIADOR: self.orientador}),
            self.banca(**{PapelBanca.SUPLENTE: coorientador}),
        ):
            with self.subTest(banca=banca):
                with self.assertRaises(services_defesa.ErroDefesa) as erro:
                    self.alterar(banca)
                self.assertEqual(
                    erro.exception.mensagem,
                    "Selecione avaliadores distintos que não façam parte da orientação do trabalho",
                )

    def test_conflito_so_do_membro_que_entra(self):
        ocupado = docente()
        outro_tcc, _professor, outro_orientador = tcc_apto()
        agendar_sessao_de(
            outro_tcc,
            outro_orientador,
            {"primeiro_avaliador": ocupado, "segundo_avaliador": docente()},
        )
        with self.assertRaises(services_defesa.ConflitoDeHorario):
            self.alterar(self.banca(**{PapelBanca.PRIMEIRO_AVALIADOR: ocupado}))
        self.assertEqual(
            services_defesa.banca_por_papel(self.sessao)[PapelBanca.PRIMEIRO_AVALIADOR], self.av1
        )
        # Trocar dois membros de papel não é entrada nova: sem checagem de conflito.
        self.alterar(
            self.banca(
                **{
                    PapelBanca.PRIMEIRO_AVALIADOR: self.av2,
                    PapelBanca.SEGUNDO_AVALIADOR: self.av1,
                }
            )
        )

    def test_permissao_pelo_curso_e_pelo_status(self):
        troca = self.banca(**{PapelBanca.SEGUNDO_AVALIADOR: docente()})
        with self.assertRaises(PermissionDenied):
            self.alterar(troca, usuario=self.professor)
        avancar_para(self.sessao, StatusSessao.EM_ANDAMENTO)
        with self.assertRaises(PermissionDenied):
            self.alterar(troca)


class TesteAcionarSuplente(TesteTurmas):
    """acionar_suplente (US-23 D). [US-23][RBN-DEF-02.2][FR-013]"""

    def setUp(self):
        super().setUp()
        self.tcc, self.professor, self.orientador = tcc_apto()
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
        avancar_para(self.sessao, StatusSessao.EM_ANDAMENTO)

    def acionar(self, usuario=None, papel=PapelBanca.SEGUNDO_AVALIADOR, justificativa="Faltou"):
        return services_defesa.acionar_suplente(
            usuario or self.orientador, self.sessao.pk, papel, justificativa
        )

    def test_suplente_assume_o_papel_do_ausente(self):
        self.acionar()
        linha = BancaDefesa.objects.get(ban_def=self.sessao, ban_usu=self.suplente)
        self.assertEqual(linha.ban_papel, PapelBanca.SEGUNDO_AVALIADOR)
        self.assertEqual(linha.ban_usu_substituido, self.av2)
        self.assertEqual(linha.ban_justificativa_substituicao, "Faltou")
        self.assertFalse(BancaDefesa.objects.filter(ban_def=self.sessao, ban_usu=self.av2).exists())
        self.assertEqual(
            services_defesa.membros_efetivos(self.sessao),
            [self.orientador, self.av1, self.suplente],
        )
        evento = HistoricoDefesas.objects.filter(hdf_def=self.sessao).latest("hdf_id")
        self.assertEqual(evento.hdf_evento, EventoDefesa.ACIONAMENTO_DO_SUPLENTE)
        self.assertEqual(
            (evento.hdf_membro_removido, evento.hdf_membro_incluido), (self.av2, self.suplente)
        )
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.def_status, StatusSessao.EM_ANDAMENTO)

    def test_so_o_orientador(self):
        for usuario in (self.professor, self.av1):
            with self.subTest(usuario=usuario.usu_nome):
                with self.assertRaises(PermissionDenied):
                    self.acionar(usuario=usuario)

    def test_sem_suplente_ou_fora_de_andamento(self):
        BancaDefesa.objects.filter(ban_def=self.sessao, ban_usu=self.suplente).delete()
        with self.assertRaises(PermissionDenied):
            self.acionar()

    def test_justificativa_obrigatoria(self):
        with self.assertRaises(services_defesa.ErroDefesa) as erro:
            self.acionar(justificativa="")
        self.assertEqual(erro.exception.campo, "justificativa")
        self.assertEqual(
            BancaDefesa.objects.get(ban_def=self.sessao, ban_usu=self.suplente).ban_papel,
            PapelBanca.SUPLENTE,
        )


class TesteConfirmarAgendamento(TesteTurmas):
    """confirmar_agendamento (US-24, passos 3 a 7). [US-24][RBN-DEF-03.2][FR-018]"""

    def setUp(self):
        super().setUp()
        self.tcc, self.professor, self.orientador = tcc_apto()
        self.aluno = self.tcc.tcc_alu
        entrega = cadastrar_entrega(self.tcc.tcc_tur, tipo=TipoEntrega.DOCUMENTO_PARA_DEFESA)
        enviar_link(entrega, self.aluno, "https://drive.example.org/antigo")
        enviar_link(entrega, self.aluno, "https://drive.example.org/documento")
        self.banca = {
            "primeiro_avaliador": docente(),
            "segundo_avaliador": docente(),
            "suplente": docente(),
        }

    def test_avisa_aluno_e_banca_inteira_com_o_documento(self):
        sessao = agendar_sessao_de(self.tcc, self.orientador, self.banca, local="Laboratório LSI")
        with self.captureOnCommitCallbacks(execute=True):
            services_defesa.confirmar_agendamento(sessao, self.orientador)
        destinatarios = [self.aluno.alu, self.orientador, *self.banca.values()]
        for usuario in destinatarios:
            aviso = Notificacoes.objects.get(not_usu=usuario)
            self.assertIn("20/11/2026 às 14:00", aviso.not_mensagem)
            self.assertIn("Presencial: Laboratório LSI", aviso.not_mensagem)
            self.assertIn(self.aluno.alu.usu_nome, aviso.not_mensagem)
            self.assertIn(self.tcc.tcc_titulo, aviso.not_mensagem)
            self.assertIn("https://drive.example.org/documento", aviso.not_mensagem)

    def test_cancela_a_troca_pendente_no_mesmo_instante(self):
        pedido = criar_pedido(self.tcc, docente(), tipo=TipoSolicitacao.TROCA_DE_ORIENTACAO)
        sessao = agendar_sessao_de(self.tcc, self.orientador, self.banca)
        services_defesa.confirmar_agendamento(sessao, self.orientador)
        pedido.refresh_from_db()
        agendamento = HistoricoDefesas.objects.get(hdf_def=sessao)
        self.assertEqual(pedido.sol_status, StatusSolicitacao.CANCELADO)
        self.assertEqual(pedido.sol_data_resposta, agendamento.hdf_data_hora)

    def test_sem_troca_pendente_nada_e_cancelado(self):
        pedido = criar_pedido(self.tcc, docente())
        sessao = agendar_sessao_de(self.tcc, self.orientador, self.banca)
        services_defesa.confirmar_agendamento(sessao, self.orientador)
        pedido.refresh_from_db()
        self.assertEqual(pedido.sol_status, StatusSolicitacao.AGUARDANDO_RESPOSTA)


class TesteReagendarECancelar(TesteTurmas):
    """reagendar e cancelar (US-24 B e C). [US-24][RBN-DEF-03.3][FR-019][FR-020][FR-022]"""

    NOVOS = {
        "data": datetime(2026, 12, 3).date(),
        "h_inicio": time(10, 0),
        "formato": FormatoSessao.REMOTA,
        "link": "https://meet.example.org/nova",
    }

    def setUp(self):
        super().setUp()
        self.tcc, self.professor, self.orientador = tcc_apto(SI)
        self.av1, self.av2, self.suplente = docente(SI), docente(SI), docente(SI)
        self.sessao = agendar_sessao_de(
            self.tcc,
            self.professor,
            {
                "primeiro_avaliador": self.av1,
                "segundo_avaliador": self.av2,
                "suplente": self.suplente,
            },
        )
        self.secretaria = criar_secretaria(curso=curso(SI))

    def test_reagendar_mantem_a_banca_e_grava_as_datas(self):
        banca = services_defesa.banca_por_papel(self.sessao)
        services_defesa.reagendar(self.professor, self.sessao.pk, self.NOVOS, "Banca em viagem")
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.def_status, StatusSessao.REAGENDADA)
        self.assertEqual(
            (self.sessao.def_data, self.sessao.def_h_inicio), (self.NOVOS["data"], time(10, 0))
        )
        self.assertEqual(
            DefesasRemotas.objects.get(der_def=self.sessao).der_link, self.NOVOS["link"]
        )
        self.assertFalse(DefesasPresenciais.objects.filter(dep_def=self.sessao).exists())
        self.assertEqual(services_defesa.banca_por_papel(self.sessao), banca)
        evento = HistoricoDefesas.objects.filter(hdf_def=self.sessao).latest("hdf_id")
        self.assertEqual(evento.hdf_evento, EventoDefesa.REAGENDAMENTO)
        self.assertEqual(evento.hdf_data_anterior, datetime(2026, 11, 20).date())
        self.assertEqual(evento.hdf_hora_anterior, time(14, 0))
        self.assertEqual(evento.hdf_data_nova, self.NOVOS["data"])
        self.assertEqual(evento.hdf_justificativa, "Banca em viagem")
        for usuario in (self.tcc.tcc_alu.alu, self.suplente):
            self.assertIn(
                "03/12/2026 às 10:00", Notificacoes.objects.get(not_usu=usuario).not_mensagem
            )

    def test_reagendar_com_conflito_do_suplente_nao_muda_nada(self):
        outro, _prof, outro_ori = tcc_apto(SI)
        agendar_sessao_de(
            outro,
            outro_ori,
            {"primeiro_avaliador": self.suplente, "segundo_avaliador": docente(SI)},
            data=self.NOVOS["data"],
            h_inicio=time(10, 30),
        )
        with self.assertRaises(services_defesa.ConflitoDeHorario):
            services_defesa.reagendar(self.professor, self.sessao.pk, self.NOVOS, "Motivo")
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.def_status, StatusSessao.AGENDADA)
        self.assertEqual(self.sessao.def_data, datetime(2026, 11, 20).date())

    def test_reagendar_a_mesma_hora_nao_conflita_com_ela_mesma(self):
        dados = dict(self.NOVOS, data=datetime(2026, 11, 20).date(), h_inicio=time(14, 30))
        services_defesa.reagendar(self.secretaria, self.sessao.pk, dados, "Ajuste")

    def test_reagendar_em_andamento(self):
        avancar_para(self.sessao, StatusSessao.EM_ANDAMENTO)
        services_defesa.reagendar(self.professor, self.sessao.pk, self.NOVOS, "Avaliador faltou")
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.def_status, StatusSessao.REAGENDADA)

    def test_cancelar_mantem_o_tcc_apto_e_descarta(self):
        with self.assertLogs("sigtcc.defesa", level="INFO") as log:
            services_defesa.cancelar(self.secretaria, self.sessao.pk, "Aluno pediu adiamento")
        self.assertIn("membro todos", log.output[0])
        self.sessao.refresh_from_db()
        self.tcc.refresh_from_db()
        self.assertEqual(self.sessao.def_status, StatusSessao.CANCELADA)
        self.assertEqual(self.tcc.tcc_status, StatusTCC.APTO_PARA_DEFESA)
        self.assertTrue(services_defesa.tcc_elegivel(self.tcc))
        evento = HistoricoDefesas.objects.filter(hdf_def=self.sessao).latest("hdf_id")
        self.assertEqual(evento.hdf_justificativa, "Aluno pediu adiamento")
        self.assertIn("foi cancelada", Notificacoes.objects.get(not_usu=self.av1).not_mensagem)

    def test_justificativa_vazia_ou_longa(self):
        for justificativa in ("", "x" * 501):
            for acao in (
                lambda j: services_defesa.cancelar(self.professor, self.sessao.pk, j),
                lambda j: services_defesa.reagendar(self.professor, self.sessao.pk, self.NOVOS, j),
            ):
                with self.subTest(tamanho=len(justificativa)):
                    with self.assertRaises(services_defesa.ErroDefesa) as erro:
                        acao(justificativa)
                    self.assertEqual(
                        erro.exception.mensagem, "Informe uma justificativa de até 500 caracteres"
                    )
        self.sessao.refresh_from_db()
        self.assertEqual(self.sessao.def_status, StatusSessao.AGENDADA)

    def test_permissao_pelo_curso_e_secretaria_de_outro_curso(self):
        outra_secretaria = criar_secretaria(curso=curso(EC))
        for usuario in (self.orientador, self.av1, outra_secretaria):
            with self.subTest(usuario=usuario.usu_nome):
                with self.assertRaises(PermissionDenied):
                    services_defesa.cancelar(usuario, self.sessao.pk, "Motivo")

    def test_sessao_realizada_ou_cancelada_bloqueia(self):
        avancar_para(self.sessao, StatusSessao.CANCELADA)
        with self.assertRaises(PermissionDenied):
            services_defesa.reagendar(self.professor, self.sessao.pk, self.NOVOS, "Motivo")


class TesteSessoesParaIniciar(TesteTurmas):
    """sessoes_para_iniciar (US-24 D). [US-24][RBN-DEF-01.2][FR-021]"""

    def test_so_agendada_ou_reagendada_com_horario_alcancado(self):
        tcc, _professor, orientador = tcc_apto()
        sessao = agendar_sessao_de(tcc, orientador, h_inicio=time(14, 0))
        antes = datetime(2026, 11, 20, 13, 59)
        na_hora = datetime(2026, 11, 20, 14, 0)
        self.assertNotIn(sessao, services_defesa.sessoes_para_iniciar(antes))
        self.assertIn(sessao, services_defesa.sessoes_para_iniciar(na_hora))
        self.assertIn(sessao, services_defesa.sessoes_para_iniciar(datetime(2026, 11, 21, 8, 0)))
        avancar_para(sessao, StatusSessao.CANCELADA)
        self.assertNotIn(sessao, services_defesa.sessoes_para_iniciar(na_hora))


class TestePeriodo(TesteTurmas):
    """periodo_letivo_atual e filtro_de_periodo (contrato §4). [US-40][RBN-DEF-01.5][FR-025]"""

    HOJE = datetime(2026, 11, 18).date()  # quarta-feira

    def datas(self, atalho, **kwargs):
        tcc, _professor, orientador = tcc_apto()
        sessoes = {
            dia: agendar_sessao_de(tcc, orientador, data=datetime(2026, *dia).date())
            for dia in ((11, 16), (11, 22), (11, 23), (11, 30), (12, 1), (12, 18), (12, 19))
        }
        filtro = services_defesa.filtro_de_periodo(atalho, hoje=self.HOJE, **kwargs)
        achadas = set(Defesas.objects.filter(filtro, def_tcc=tcc))
        return {dia for dia, sessao in sessoes.items() if sessao in achadas}

    def test_esta_semana_de_segunda_a_domingo(self):
        self.assertEqual(self.datas("esta_semana"), {(11, 16), (11, 22)})

    def test_este_mes(self):
        self.assertEqual(self.datas("este_mes"), {(11, 16), (11, 22), (11, 23), (11, 30)})

    def test_proximos_30_dias(self):
        self.assertEqual(
            self.datas("proximos_30_dias"), {(11, 22), (11, 23), (11, 30), (12, 1), (12, 18)}
        )

    def test_intervalo_manual(self):
        dias = self.datas(
            "intervalo",
            data_inicial=datetime(2026, 11, 22).date(),
            data_final=datetime(2026, 11, 30).date(),
        )
        self.assertEqual(dias, {(11, 22), (11, 23), (11, 30)})

    def test_periodo_letivo_pela_turma_das_turmas_ativas(self):
        atual, _p, ori = tcc_apto()
        Turmas.objects.filter(pk=atual.tcc_tur_id).update(tur_ano=2027, tur_semestre=1)
        antigo, _p2, ori2 = tcc_apto()
        Turmas.objects.filter(pk=antigo.tcc_tur_id).update(tur_ano=2026, tur_semestre=2)
        arquivado, _p3, ori3 = tcc_apto()
        Turmas.objects.filter(pk=arquivado.tcc_tur_id).update(
            tur_ano=2028, tur_semestre=1, tur_status=StatusTurma.ARQUIVADA
        )
        self.assertEqual(services_defesa.periodo_letivo_atual(), (2027, 1))
        na_lista = agendar_sessao_de(atual, ori, data=datetime(2026, 12, 1).date())
        fora = agendar_sessao_de(antigo, ori2)
        filtro = services_defesa.filtro_de_periodo("periodo_letivo")
        self.assertEqual(list(Defesas.objects.filter(filtro)), [na_lista])
        self.assertNotIn(fora, Defesas.objects.filter(filtro))

    def test_sem_turma_ativa_usa_o_calendario(self):
        Turmas.objects.update(tur_status=StatusTurma.ARQUIVADA)
        self.assertEqual(services_defesa.periodo_letivo_atual(self.HOJE), (2026, 2))
        self.assertEqual(
            services_defesa.periodo_letivo_atual(datetime(2026, 3, 1).date()), (2026, 1)
        )

    def test_prefixo_para_outro_modelo(self):
        filtro = services_defesa.filtro_de_periodo("este_mes", hoje=self.HOJE, prefixo="ban_def__")
        tcc, _professor, orientador = tcc_apto()
        sessao = agendar_sessao_de(tcc, orientador)
        self.assertTrue(BancaDefesa.objects.filter(filtro, ban_def=sessao).exists())


class TesteListarDefesas(TesteTurmas):
    """listar_defesas: visibilidade por perfil somada por OR e filtros. [US-40][US-39]
    [RBN-DEF-01.4][FR-024][FR-026][FR-027]
    """

    def setUp(self):
        super().setUp()
        self.tcc_ec, self.prof_ec, self.ori_ec = tcc_apto()
        self.av = docente()
        self.coorientador = docente()
        vincular_coorientador(self.tcc_ec, self.coorientador)
        self.sessao_ec = agendar_sessao_de(
            self.tcc_ec,
            self.ori_ec,
            {"primeiro_avaliador": self.av, "segundo_avaliador": docente()},
        )
        self.tcc_si, self.prof_si, self.ori_si = tcc_apto(SI)
        self.sessao_si = agendar_sessao_de(
            self.tcc_si,
            self.prof_si,
            {"primeiro_avaliador": docente(SI), "segundo_avaliador": docente(SI)},
            data=datetime(2026, 11, 10).date(),
        )

    def lista(self, usuario, **filtros):
        return list(services_defesa.listar_defesas(usuario, **filtros))

    def test_cada_perfil_ve_so_o_seu_ambito(self):
        casos = {
            "aluno": (self.tcc_ec.tcc_alu.alu, [self.sessao_ec]),
            "avaliador": (self.av, [self.sessao_ec]),
            "orientador": (self.ori_si, [self.sessao_si]),
            "coorientador": (self.coorientador, [self.sessao_ec]),
            "professor": (self.prof_ec, [self.sessao_ec]),
            "outro docente": (docente(), []),
        }
        for nome, (usuario, esperado) in casos.items():
            with self.subTest(perfil=nome):
                self.assertEqual(self.lista(usuario), esperado)

    def test_dois_papeis_somam_sem_repetir(self):
        # Professor da Disciplina da turma de SI e avaliador da banca de EC.
        tcc, _p, ori = tcc_apto(professor=docente())
        sessao = agendar_sessao_de(
            tcc, ori, {"primeiro_avaliador": self.prof_si, "segundo_avaliador": docente()}
        )
        self.assertEqual(self.lista(self.prof_si), [self.sessao_si, sessao])

    def test_coordenacao_e_secretaria_pelo_curso_do_filtro(self):
        secretaria = criar_secretaria(curso=curso(SI))
        self.assertEqual(self.lista(secretaria, cur_id=curso(SI).pk), [self.sessao_si])
        self.assertEqual(self.lista(secretaria, cur_id=None), [self.sessao_si, self.sessao_ec])

    def test_filtro_de_status_e_de_periodo(self):
        avancar_para(self.sessao_si, StatusSessao.CANCELADA)
        secretaria = criar_secretaria(curso=curso(SI))
        self.assertEqual(self.lista(secretaria, status=StatusSessao.CANCELADA), [self.sessao_si])
        periodo = services_defesa.filtro_de_periodo(
            "intervalo",
            data_inicial=datetime(2026, 11, 15).date(),
            data_final=datetime(2026, 11, 30).date(),
        )
        self.assertEqual(self.lista(secretaria, periodo=periodo), [self.sessao_ec])

    def test_ordem_cronologica_e_dados_carregados(self):
        secretaria = criar_secretaria(curso=curso(SI))
        aluno_ec = self.tcc_ec.tcc_alu.alu
        linhas = self.lista(secretaria)
        with self.assertNumQueries(0):  # tudo já veio na consulta da lista
            self.assertEqual(
                [s.orientador_nome for s in linhas], [self.ori_si.usu_nome, self.ori_ec.usu_nome]
            )
            self.assertEqual(linhas[0].defesaspresenciais.dep_local, "Laboratório LSI")
            self.assertEqual(linhas[1].def_tcc.tcc_alu.alu, aluno_ec)
            self.assertEqual(linhas[1].def_tcc.tcc_tur.tur_cur.cur_nome, EC)


class TesteHistorico(TesteTurmas):
    """historico_da_sessao: todas as sessões do TCC, em ordem. [US-40][RBN-DEF-01.6][FR-029]"""

    def test_reune_as_sessoes_do_tcc_inclusive_canceladas(self):
        tcc, professor, orientador = tcc_apto()
        primeira = agendar_sessao_de(tcc, orientador)
        avancar_para(primeira, StatusSessao.CANCELADA, orientador)
        segunda = agendar_sessao_de(tcc, orientador, data=datetime(2026, 12, 2).date())
        outro, _p, outro_ori = tcc_apto()
        agendar_sessao_de(outro, outro_ori)
        eventos = list(services_defesa.historico_da_sessao(segunda))
        self.assertEqual(
            [(e.hdf_def, e.hdf_evento) for e in eventos],
            [
                (primeira, EventoDefesa.AGENDAMENTO),
                (primeira, EventoDefesa.CANCELAMENTO),
                (segunda, EventoDefesa.AGENDAMENTO),
            ],
        )
        self.assertEqual(eventos[1].hdf_usu, orientador)


class TesteAgendar(TesteTurmas):
    """agendar: o botão Agendar de ponta a ponta no serviço. [US-21][US-22][US-23][US-24]
    [RBN-DEF-01.3][RBN-DEF-03.1][RBN-DEF-03.2][Q-67]
    """

    BASICOS = {
        "data": datetime(2026, 11, 20).date(),
        "h_inicio": time(14, 0),
        "formato": FormatoSessao.PRESENCIAL,
        "local": "Laboratório LSI",
    }

    def setUp(self):
        super().setUp()
        self.tcc, self.professor, self.orientador = tcc_apto()
        self.banca = {"primeiro_avaliador": docente(), "segundo_avaliador": docente()}

    def agendar(self, usuario=None, banca=None):
        return services_defesa.agendar(
            usuario or self.orientador, self.tcc.pk, self.BASICOS, banca or self.banca
        )

    def test_grava_confirma_e_avisa(self):
        sessao = self.agendar()
        self.assertEqual(sessao.def_status, StatusSessao.AGENDADA)
        self.assertEqual(Notificacoes.objects.filter(not_usu=self.tcc.tcc_alu.alu).count(), 1)

    def test_quem_nao_agenda_ou_tcc_nao_elegivel(self):
        with self.assertRaises(services_defesa.ErroDefesa) as erro:
            self.agendar(usuario=self.professor)
        self.assertEqual(erro.exception.mensagem, "Este TCC não pode ser agendado por você")
        self.agendar()
        with self.assertRaises(services_defesa.ErroDefesa):
            self.agendar(banca={"primeiro_avaliador": docente(), "segundo_avaliador": docente()})
        self.assertEqual(Defesas.objects.filter(def_tcc=self.tcc).count(), 1)

    def test_conflito_ou_banca_invalida_nao_grava_nada(self):
        outro, _p, outro_ori = tcc_apto()
        agendar_sessao_de(
            outro,
            outro_ori,
            {"primeiro_avaliador": self.banca["segundo_avaliador"], "segundo_avaliador": docente()},
        )
        with self.assertRaises(services_defesa.ConflitoDeHorario):
            self.agendar()
        with self.assertRaises(services_defesa.ErroDefesa):
            self.agendar(
                banca={"primeiro_avaliador": self.orientador, "segundo_avaliador": docente()}
            )
        self.assertFalse(Defesas.objects.filter(def_tcc=self.tcc).exists())
        self.assertFalse(Notificacoes.objects.filter(not_usu=self.tcc.tcc_alu.alu).exists())

    def test_docente_inativado_no_meio_e_recusado(self):
        Usuarios.objects.filter(pk=self.banca["primeiro_avaliador"].pk).update(
            usu_status=StatusConta.INATIVA
        )
        with self.assertRaises(Http404):
            self.agendar()
        self.assertFalse(Defesas.objects.filter(def_tcc=self.tcc).exists())

    def test_renova_a_validade_do_membro_externo_expirado(self):
        externo = criar_membro_externo(
            status=StatusConta.EXPIRADA, validade=datetime(2026, 1, 31).date()
        )
        with mock.patch.object(
            services_contas, "data_de_hoje", return_value=datetime(2026, 11, 1).date()
        ):
            self.agendar(banca={"primeiro_avaliador": externo, "segundo_avaliador": docente()})
        externo.refresh_from_db()
        self.assertEqual(externo.usu_status, StatusConta.ATIVA)
        self.assertEqual(externo.membrosexternos.mem_validade_ate, datetime(2026, 11, 27).date())
