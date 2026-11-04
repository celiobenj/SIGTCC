"""US-27, apurar e liberar o resultado (User Story 4 da spec 008): cenários 4.1 a 4.15, o ponto de
chamada da feat-09 (revisão I-10), duas liberações seguidas, SC-004 (só os serviços únicos mudam
os status) e o Histórico da defesa (IC-06; D15).

[US-27][RBN-DEF-06.2][RBN-DEF-06.3][RBN-DEF-06.4][RBN-DEF-06.6][RBN-DEF-06.7][RBN-DEF-01.6]
(tasks T029, T035)
"""

import re
from decimal import Decimal
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.core import mail
from django.urls import reverse

from sigtcc.apps.cadastro import services_turmas
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    GatilhoStatusTCC,
    Homologacao,
    StatusSubmissao,
    StatusTCC,
)
from sigtcc.apps.cadastro.models import HistoricoStatusTCC, Notificacoes
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_secretaria
from sigtcc.apps.cadastro.tests.apoio_orientacao import salvar_artigo
from sigtcc.apps.defesa import services_avaliacoes, services_defesa
from sigtcc.apps.defesa.choices import EventoDefesa, PapelBanca, Parecer, StatusSessao
from sigtcc.apps.defesa.models import Defesas, HistoricoDefesas
from sigtcc.apps.defesa.tests.apoio_avaliacao import (
    TesteAvaliacao,
    formulario,
    lancar,
    lancar_e_enviar,
    png,
    sessao_com_banca,
)

D = Decimal
SO_ORIENTADOR = "Apenas o Orientador (Presidente da banca) pode liberar o resultado da defesa"
SELECIONE = "Selecione o parecer da banca para continuar"
MA04 = "O resultado desta defesa já foi liberado e as avaliações não podem mais ser alteradas"


class BaseLiberacao(TesteAvaliacao):
    """Sessão Em Andamento com a Secretaria do curso. [US-27][RBN-DEF-06.4]"""

    descricao = DescricaoTurma.TCC_2

    def setUp(self):
        super().setUp()
        self.cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO, descricao=self.descricao)
        self.sessao = self.cenario["sessao"]
        self.tcc = self.cenario["tcc"]
        self.orientador = self.cenario["orientador"]
        self.membros = [self.cenario[chave] for chave in ("orientador", "av1", "av2")]
        self.secretaria = criar_secretaria(curso=self.tcc.tcc_tur.tur_cur)
        self.url_sessao = reverse("defesa:sessao", args=[self.sessao.pk])
        self.url_liberar = reverse("defesa:liberar_resultado", args=[self.sessao.pk])
        self.url_parecer = reverse("defesa:registrar_parecer", args=[self.sessao.pk])

    def enviar_todos(self, *notas):
        for membro, nota in zip(self.membros, notas):
            lancar_e_enviar(self.sessao, membro, nota)

    def entrar(self, usuario=None):
        self.client.force_login(usuario or self.orientador)

    def confirmar(self, nota, parecer):
        self.entrar()
        return self.client.post(self.url_liberar, {"nota": str(nota), "parecer": parecer})

    def recarregar(self):
        self.sessao.refresh_from_db()
        self.tcc.refresh_from_db()


class TesteLiberacaoTcc2(BaseLiberacao):
    """Cenários de TCC 2. [US-27][RBN-DEF-06.3][RBN-DEF-06.4]"""

    def test_cenario_4_1_aprovado_com_correcoes(self):
        self.enviar_todos(D("7.0"), D("7.0"), D("7.0"))
        self.entrar()
        self.client.post(self.url_parecer, {"parecer": Parecer.APROVADO_COM_CORRECOES})
        pagina = self.client.get(self.url_liberar)
        self.assertContains(
            pagina,
            "Liberar o resultado com nota final 7,0 e parecer Aprovado com Correções? Depois "
            "disso, as notas não podem mais ser alteradas.",
        )
        with self.captureOnCommitCallbacks(execute=True):
            resposta = self.confirmar("7.0", Parecer.APROVADO_COM_CORRECOES)
        self.assertRedirects(resposta, self.url_sessao, fetch_redirect_response=False)
        self.recarregar()
        self.assertEqual(self.sessao.def_status, StatusSessao.REALIZADA)
        self.assertEqual(self.sessao.def_nota_final, D("7.0"))
        self.assertEqual(self.sessao.def_parecer, Parecer.APROVADO_COM_CORRECOES)
        self.assertIsNotNone(self.sessao.def_data_liberacao_resultado)
        self.assertEqual(self.tcc.tcc_status, StatusTCC.APROVADO_COM_CORRECOES)
        historico = HistoricoStatusTCC.objects.filter(hst_tcc=self.tcc).latest("hst_id")
        self.assertEqual(historico.hst_gatilho, GatilhoStatusTCC.LIBERACAO_DO_RESULTADO)
        evento = HistoricoDefesas.objects.filter(hdf_def=self.sessao).latest("hdf_id")
        self.assertEqual(evento.hdf_evento, EventoDefesa.LIBERACAO_DO_RESULTADO)
        self.assertContains(self.client.get(self.url_sessao), "Resultado liberado com sucesso")

    def test_cenario_4_4_nota_8_5_aprovado(self):
        self.enviar_todos(D("8.5"), D("8.5"), D("8.5"))
        services_avaliacoes.registrar_parecer(self.orientador, self.sessao.pk, Parecer.APROVADO)
        self.confirmar("8.5", Parecer.APROVADO)
        self.recarregar()
        self.assertEqual(self.tcc.tcc_status, StatusTCC.APROVADO)

    def test_cenario_4_5_nota_5_4_reprovado(self):
        self.enviar_todos(D("5.4"), D("5.4"), D("5.4"))
        self.entrar()
        self.assertNotContains(self.client.get(self.url_sessao), "Registrar parecer")
        self.confirmar("5.4", Parecer.REPROVADO)
        self.recarregar()
        self.assertEqual(self.sessao.def_parecer, Parecer.REPROVADO)
        self.assertEqual(self.tcc.tcc_status, StatusTCC.REPROVADO)

    def test_cenario_4_6_qualis_a_eleva_a_6_0(self):
        self.enviar_todos(D("5.4"), D("5.4"), D("5.4"))
        salvar_artigo(
            self.tcc,
            qualis="A1",
            status=StatusSubmissao.PUBLICADO,
            art_homologacao=Homologacao.HOMOLOGADO,
        )
        apuracao = services_avaliacoes.apuracao(self.sessao)
        self.assertEqual(apuracao["nota_final"], D("6.0"))
        self.assertIsNone(apuracao["parecer"])
        self.assertTrue(apuracao["pode_registrar_parecer"])

    def test_cenario_4_7_reajuste_recalcula_e_limpa_o_parecer(self):
        self.enviar_todos(D("7.0"), D("7.0"), D("7.0"))
        services_avaliacoes.registrar_parecer(self.orientador, self.sessao.pk, Parecer.APROVADO)
        services_avaliacoes.reabrir_avaliacao(self.membros[1], self.sessao.pk)
        self.sessao.refresh_from_db()
        self.assertIsNone(self.sessao.def_parecer)
        self.assertFalse(services_avaliacoes.apuracao(self.sessao)["completos"])
        lancar_e_enviar(self.sessao, self.membros[1], D("4.0"))
        apuracao = services_avaliacoes.apuracao(self.sessao)
        self.assertEqual(apuracao["nota_final"], D("6.0"))
        self.assertIsNone(apuracao["parecer"])

    def test_cenario_4_10_pendente_desabilita_e_destaca(self):
        self.enviar_todos(D("8.0"), D("8.0"))
        lancar(self.sessao, self.membros[2], D("8.0"))
        self.entrar()
        pagina = self.client.get(self.url_sessao)
        self.assertContains(pagina, "Pendentes: <b>" + self.membros[2].usu_nome)
        self.assertContains(pagina, 'class="pendente"', count=1)
        self.assertNotContains(pagina, self.url_liberar)
        self.assertContains(pagina, 'disabled><span class="ms">verified</span>Liberar Resultado')
        self.assertRedirects(
            self.client.get(self.url_liberar), self.url_sessao, fetch_redirect_response=False
        )
        self.confirmar("8.0", Parecer.APROVADO)
        self.recarregar()
        self.assertEqual(self.sessao.def_status, StatusSessao.EM_ANDAMENTO)

    def test_cenario_4_11_sem_parecer_em_tcc_2(self):
        self.enviar_todos(D("7.0"), D("7.0"), D("7.0"))
        self.entrar()
        pagina = self.client.get(self.url_sessao)
        self.assertContains(pagina, "Registrar parecer")
        self.assertNotContains(pagina, self.url_liberar)
        resposta = self.client.post(self.url_parecer, {})
        self.assertContains(resposta, SELECIONE)
        self.assertContains(resposta, "com-erro")
        resposta = self.confirmar("7.0", Parecer.APROVADO)
        self.recarregar()
        self.assertEqual(self.sessao.def_status, StatusSessao.EM_ANDAMENTO)
        self.assertIsNone(self.sessao.def_data_liberacao_resultado)

    def test_cenario_4_12_avaliador_titular_nao_libera(self):
        self.enviar_todos(D("8.0"), D("8.0"), D("8.0"))
        services_avaliacoes.registrar_parecer(self.orientador, self.sessao.pk, Parecer.APROVADO)
        for usuario in (self.membros[1], self.cenario["suplente"], self.cenario["professor"]):
            with self.subTest(usuario=usuario.usu_email):
                self.client.force_login(usuario)
                self.assertNotContains(self.client.get(self.url_sessao), "Liberar Resultado")
                for resposta in (
                    self.client.get(self.url_liberar),
                    self.client.post(self.url_liberar, {"nota": "8.0", "parecer": "Aprovado"}),
                    self.client.post(self.url_parecer, {"parecer": "Aprovado"}),
                ):
                    self.assertContains(resposta, SO_ORIENTADOR, status_code=403)
        self.recarregar()
        self.assertEqual(self.sessao.def_status, StatusSessao.EM_ANDAMENTO)

    def test_cenario_4_13_depois_da_liberacao_nada_muda(self):
        self.enviar_todos(D("8.0"), D("8.0"), D("8.0"))
        services_avaliacoes.registrar_parecer(self.orientador, self.sessao.pk, Parecer.APROVADO)
        self.confirmar("8.0", Parecer.APROVADO)
        membro = self.membros[1]
        self.client.force_login(membro)
        resposta = self.client.post(
            reverse("defesa:reabrir_avaliacao", args=[self.sessao.pk]), follow=True
        )
        self.assertContains(resposta, MA04)
        resposta = self.client.post(
            reverse("defesa:avaliacao", args=[self.sessao.pk]),
            formulario(D("9.0"), acao="enviar", arquivo=png()),
        )
        self.assertContains(resposta, MA04)
        for acao in (
            lambda: services_avaliacoes.salvar_rascunho(membro, self.sessao.pk, {}),
            lambda: services_avaliacoes.reabrir_avaliacao(membro, self.sessao.pk),
        ):
            with self.assertRaises(services_avaliacoes.ErroAvaliacao):
                acao()
        self.assertEqual(services_avaliacoes.nota_individual(self.sessao, membro), D("8.0"))

    def test_cenario_4_14_tcc_2_nota_sobe_a_6_volta_para_registrar_parecer(self):
        self.enviar_todos(D("5.4"), D("5.4"), D("5.4"))
        self.entrar()
        self.assertContains(self.client.get(self.url_liberar), "nota final 5,4 e parecer Reprovado")
        salvar_artigo(
            self.tcc,
            qualis="B1",
            status=StatusSubmissao.PUBLICADO,
            art_homologacao=Homologacao.HOMOLOGADO,
        )
        resposta = self.confirmar("5.4", Parecer.REPROVADO)
        self.assertRedirects(resposta, self.url_sessao, fetch_redirect_response=False)
        pagina = self.client.get(self.url_sessao)
        self.assertContains(pagina, SELECIONE)
        self.assertContains(pagina, "Registrar parecer")
        self.recarregar()
        self.assertIsNone(self.sessao.def_data_liberacao_resultado)

    def test_cenario_4_15_reagendamento_devolve_a_rascunho(self):
        self.enviar_todos(D("8.0"), D("8.0"), D("8.0"))
        services_avaliacoes.registrar_parecer(self.orientador, self.sessao.pk, Parecer.APROVADO)
        from datetime import date, time

        services_defesa.reagendar(
            self.orientador,
            self.sessao.pk,
            {
                "data": date(2026, 12, 10),
                "h_inicio": time(9, 0),
                "formato": "Presencial",
                "local": "Sala 3",
            },
            "Queda de energia",
        )
        self.recarregar()
        self.assertIsNone(self.sessao.def_parecer)
        estados = {i["estado"] for i in services_avaliacoes.estados_da_banca(self.sessao)}
        self.assertEqual(estados, {"Rascunho salvo"})


class TesteLiberacaoTcc1(BaseLiberacao):
    """Cenários de TCC 1 e do cálculo. [US-27][RBN-DEF-06.2][RBN-DEF-06.3]"""

    descricao = DescricaoTurma.TCC_1

    def test_cenario_4_2_calculo_pela_regra(self):
        notas = [D("7.0"), D("8.0"), D("9.0")]
        self.enviar_todos(*notas)
        apuracao = services_avaliacoes.apuracao(self.sessao)
        self.assertEqual(apuracao["nota_final"], D("8.0"))

    def test_cenario_4_3_nota_7_2_aprovado_para_tcc_2(self):
        self.enviar_todos(D("7.2"), D("7.2"), D("7.2"))
        self.entrar()
        pagina = self.client.get(self.url_sessao)
        self.assertNotContains(pagina, "Registrar parecer")
        self.assertContains(pagina, "Aprovado para TCC 2")
        self.confirmar("7.2", Parecer.APROVADO_PARA_TCC_2)
        self.recarregar()
        self.assertEqual(self.tcc.tcc_status, StatusTCC.APROVADO_PARA_TCC_2)

    def test_cenario_4_8_suplente_no_lugar_do_2_avaliador(self):
        lancar_e_enviar(self.sessao, self.membros[2], D("2.0"))
        services_defesa.acionar_suplente(
            self.orientador, self.sessao.pk, PapelBanca.SEGUNDO_AVALIADOR, "Faltou"
        )
        lancar_e_enviar(self.sessao, self.membros[0], D("8.0"))
        lancar_e_enviar(self.sessao, self.membros[1], D("8.0"))
        lancar_e_enviar(self.sessao, self.cenario["suplente"], D("8.0"))
        self.assertEqual(services_avaliacoes.apuracao(self.sessao)["nota_final"], D("8.0"))

    def test_cenario_4_9_sem_login(self):
        resposta = self.client.get(self.url_sessao)
        self.assertRedirects(
            resposta,
            f"{reverse('cadastro:entrar')}?next={self.url_sessao}",
            fetch_redirect_response=False,
        )

    def test_d10_nota_mudou_reabre_a_confirmacao(self):
        self.enviar_todos(D("5.4"), D("5.4"), D("5.4"))
        salvar_artigo(
            self.tcc,
            qualis="A1",
            status=StatusSubmissao.PUBLICADO,
            art_homologacao=Homologacao.HOMOLOGADO,
        )
        resposta = self.confirmar("5.4", Parecer.REPROVADO)
        self.assertContains(resposta, "nota final 6,0 e parecer Aprovado para TCC 2")
        self.recarregar()
        self.assertIsNone(self.sessao.def_data_liberacao_resultado)
        self.confirmar("6.0", Parecer.APROVADO_PARA_TCC_2)
        self.recarregar()
        self.assertEqual(self.sessao.def_nota_final, D("6.0"))

    def test_avisos_ao_aluno_banca_e_secretaria_sem_a_nota(self):
        self.enviar_todos(D("7.3"), D("7.3"), D("7.3"))
        with self.captureOnCommitCallbacks(execute=True):
            self.confirmar("7.3", Parecer.APROVADO_PARA_TCC_2)
        aluno = self.cenario["aluno"]
        self.assertEqual(
            Notificacoes.objects.get(not_usu=aluno).not_mensagem,
            "O resultado da sua defesa foi liberado. Consulte a nota final e o parecer na aba "
            "Meu TCC.",
        )
        for membro in self.membros:
            self.assertTrue(
                Notificacoes.objects.filter(
                    not_usu=membro, not_mensagem__startswith="O resultado da defesa de"
                ).exists()
            )
        aviso = Notificacoes.objects.get(not_usu=self.secretaria)
        self.assertIn("encerrada com parecer Aprovado para TCC 2", aviso.not_mensagem)
        assuntos = {email.subject for email in mail.outbox}
        self.assertEqual(assuntos, {"SIGTCC: resultado da defesa"})
        self.assertFalse([email for email in mail.outbox if "7,3" in email.body])

    def test_ponto_da_feat_09_depois_do_commit_e_robusto(self):
        self.enviar_todos(D("8.0"), D("8.0"), D("8.0"))
        with mock.patch(
            "sigtcc.apps.defesa.services_documentos.ao_liberar_resultado",
            side_effect=RuntimeError("feat-09 falhou"),
        ) as ponto:
            with self.captureOnCommitCallbacks(execute=True) as callbacks:
                self.confirmar("8.0", Parecer.APROVADO_PARA_TCC_2)
                ponto.assert_not_called()
        ponto.assert_called_once()
        self.assertTrue(callbacks)
        self.recarregar()
        self.assertEqual(self.sessao.def_status, StatusSessao.REALIZADA)
        self.assertTrue(mail.outbox)

    def test_duas_liberacoes_seguidas_a_segunda_nao_grava(self):
        self.enviar_todos(D("8.0"), D("8.0"), D("8.0"))
        services_avaliacoes.liberar_resultado(
            self.orientador, self.sessao.pk, D("8.0"), Parecer.APROVADO_PARA_TCC_2
        )
        antes = HistoricoDefesas.objects.filter(hdf_def=self.sessao).count()
        with self.assertRaises(services_avaliacoes.ErroAvaliacao) as erro:
            services_avaliacoes.liberar_resultado(
                self.orientador, self.sessao.pk, D("8.0"), Parecer.APROVADO_PARA_TCC_2
            )
        self.assertEqual(erro.exception.mensagem, MA04)
        self.assertEqual(HistoricoDefesas.objects.filter(hdf_def=self.sessao).count(), antes)

    def test_sc004_status_so_pelos_servicos_unicos(self):
        self.enviar_todos(D("8.0"), D("8.0"), D("8.0"))
        with mock.patch.object(
            services_defesa, "transicionar_status", wraps=services_defesa.transicionar_status
        ) as sessao, mock.patch.object(
            services_turmas, "atualizar_status_tcc", wraps=services_turmas.atualizar_status_tcc
        ) as tcc:
            services_avaliacoes.liberar_resultado(
                self.orientador, self.sessao.pk, D("8.0"), Parecer.APROVADO_PARA_TCC_2
            )
        sessao.assert_called_once()
        self.assertEqual(sessao.call_args.args[1], StatusSessao.REALIZADA)
        tcc.assert_called_once()
        self.assertEqual(tcc.call_args.args[4], GatilhoStatusTCC.LIBERACAO_DO_RESULTADO)

    def test_sc004_nenhuma_gravacao_direta_no_codigo(self):
        fonte = (
            Path(settings.BASE_DIR) / "sigtcc" / "apps" / "defesa" / "services_avaliacoes.py"
        ).read_text(encoding="utf-8")
        for proibido in (
            # Atribuição no objeto ou update(); filtros de consulta não contam.
            r"\.def_status\s*=(?!=)",
            r"\.tcc_status\s*=(?!=)",
            r"update\([^)]*def_status",
            r"update\([^)]*tcc_status",
            r"HistoricoDefesas\.objects",
            r"HistoricoStatusTCC",
            r"Defesas\.objects\.create",
        ):
            with self.subTest(trecho=proibido):
                self.assertIsNone(re.search(proibido, fonte))

    def test_historico_mostra_nota_e_parecer_na_liberacao(self):
        self.enviar_todos(D("7.6"), D("7.6"), D("7.6"))
        self.confirmar("7.6", Parecer.APROVADO_PARA_TCC_2)
        self.client.force_login(self.cenario["aluno"])
        pagina = self.client.get(reverse("defesa:historico", args=[self.sessao.pk]))
        self.assertContains(pagina, "Liberação do Resultado")
        self.assertContains(pagina, "Nota final: 7,6; parecer: Aprovado para TCC 2")
        self.assertEqual(Defesas.objects.get(pk=self.sessao.pk).def_nota_final, D("7.6"))
