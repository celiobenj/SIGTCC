"""Testes de aceite da US-18: aceitar ou recusar pedido de orientação e consultar a tela de
orientandos (spec 006, User Story 2).

Cenários 1 a 14 da US-18 e os pontos de contato #15 (histórico pela linha), #16 (Correções
Conferidas) e #17 (Resumo no pedido de troca, IC-05); mais aceite duplo, aceite de pedido já
cancelado, troca com sessão ativa (A20), convite pendente ao novo orientador cancelado (MO-17),
MO-24, ordem das linhas e consultas constantes (R14).

[US-18][US-14 A][US-44 B][RBN-CAD-10.2][RBN-CAD-11.4][FR-009 a FR-016][FR-040] (tasks T019)
"""

from datetime import timedelta

from django.core import mail
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services_orientacao, services_tcc
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    ModalidadeTCC,
    StatusConta,
    StatusCoorientacao,
    StatusEntrega,
    StatusOrientacao,
    StatusSolicitacao,
    StatusTCC,
    StatusTurma,
    TipoEntrega,
    TipoSolicitacao,
)
from sigtcc.apps.cadastro.models import (
    Coorientacoes,
    EntregasMarcos,
    Notificacoes,
    Orientacoes,
)
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo
from sigtcc.apps.cadastro.tests.apoio_orientacao import (
    agendar_defesa,
    criar_convite,
    criar_pedido,
    registrar_ata,
    vincular_coorientador,
    vincular_orientador,
)
from sigtcc.apps.cadastro.tests.apoio_tcc import cadastrar_entrega, enviar_link, salvar_proposta
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    SI,
    TesteTurmas,
    criar_defesa_de,
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)
from sigtcc.apps.defesa.choices import StatusSessao


class RespostaTestBase(TesteTurmas):
    """Turma de TCC 1 de SI, aluno com TCC 'Em Andamento' e um pedido pendente ao docente."""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=SI)
        self.aluno = matricular_aluno(
            self.turma, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        )
        self.tcc = tcc_de(self.aluno, self.turma)
        self.docente = criar_docente_ativo()
        self.pedido = criar_pedido(self.tcc, self.docente)
        self.client.force_login(self.docente)

    def tela(self):
        return self.client.get(reverse("cadastro:orientacoes"))

    def aceitar(self, sol=None, follow=True):
        url = reverse("cadastro:aceitar_solicitacao", args=[(sol or self.pedido).pk])
        return self.client.post(url, follow=follow)

    def recusar(self, sol=None, follow=True):
        url = reverse("cadastro:recusar_solicitacao", args=[(sol or self.pedido).pk])
        return self.client.post(url, follow=follow)

    def link(self, sol=None):
        return self.client.get(services_orientacao.link_da_solicitacao(sol or self.pedido))


class AceiteRecusaTest(RespostaTestBase):
    """Cenários 1 a 7 e 10 a 14. [FR-009 a FR-013]"""

    def test_cenario1_aceite(self):
        with self.captureOnCommitCallbacks(execute=True):
            resposta = self.aceitar()
        self.assertContains(resposta, mensagens.MO15_PEDIDO_ACEITO)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.sol_status, StatusSolicitacao.ACEITO)
        self.assertIsNotNone(self.pedido.sol_data_resposta)
        ativa = Orientacoes.objects.get(ori_tcc=self.tcc, ori_status=StatusOrientacao.ATIVA)
        self.assertEqual(ativa.ori_doc_id, self.docente.pk)
        self.assertNotContains(resposta, f"solicitacao-{self.pedido.pk}")
        self.assertContains(resposta, self.aluno.alu.usu_nome)
        self.assertContains(resposta, "Orientador")
        self.assertTrue(Notificacoes.objects.filter(not_usu=self.aluno.alu).exists())
        aviso = Notificacoes.objects.get(not_usu=self.professor)
        self.assertEqual(
            aviso.not_link_tela,
            reverse("cadastro:painel_aluno", args=[self.turma.pk, self.aluno.pk]),
        )
        self.assertEqual(mail.outbox[0].subject, mensagens.MO04_ASSUNTO)

    def test_cenario2_e_3_link_abre_a_tela_com_o_pedido(self):
        resposta = self.link()
        self.assertContains(resposta, "Pedidos de orientação")
        self.assertContains(resposta, f'class="item destaque" id="solicitacao-{self.pedido.pk}"')

    def test_cenario4_ver_proposta(self):
        resposta = self.client.get(reverse("cadastro:ver_proposta", args=[self.pedido.pk]))
        self.assertContains(resposta, self.tcc.tcc_titulo)
        self.assertContains(resposta, self.tcc.tcc_resumo)
        self.assertContains(resposta, "Fechar")
        self.assertContains(resposta, reverse("cadastro:orientacoes"))

    def test_cenario5_sem_proposta_sem_ver_proposta(self):
        self.tcc.tcc_status = StatusTCC.SEM_PROPOSTA
        self.tcc.tcc_titulo = self.tcc.tcc_resumo = self.tcc.tcc_modalidade = None
        self.tcc.save()
        resposta = self.tela()
        self.assertContains(resposta, mensagens.PROPOSTA_AINDA_NAO_REGISTRADA)
        self.assertNotContains(resposta, "Ver proposta")
        url = reverse("cadastro:ver_proposta", args=[self.pedido.pk])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_cenario6_recusa(self):
        resposta = self.recusar()
        self.assertContains(resposta, mensagens.PEDIDO_RECUSADO)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.sol_status, StatusSolicitacao.RECUSADO)
        self.assertEqual(
            Notificacoes.objects.get(not_usu=self.aluno.alu).not_mensagem,
            mensagens.MO03_PEDIDO_RECUSADO.format(docente=self.docente.usu_nome),
        )
        self.assertFalse(Orientacoes.objects.filter(ori_tcc=self.tcc).exists())

    def test_cenario10_sem_sessao_link_vai_ao_login(self):
        self.client.logout()
        resposta = self.link()
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("cadastro:entrar"), resposta.url)

    def test_cenario11_outro_docente_nao_disponivel(self):
        self.client.force_login(criar_docente_ativo())
        resposta = self.link()
        self.assertContains(resposta, mensagens.PEDIDO_NAO_DISPONIVEL)
        self.assertNotContains(resposta, f"solicitacao-{self.pedido.pk}")
        self.assertEqual(self.aceitar(follow=False).status_code, 404)

    def test_cenario11_inexistente_e_de_outro_tipo_mesma_resposta(self):
        url = reverse("cadastro:pedido_orientacao", args=[999999])
        self.assertContains(self.client.get(url), mensagens.PEDIDO_NAO_DISPONIVEL)
        convite = criar_convite(self.tcc, self.docente)
        url = reverse("cadastro:pedido_orientacao", args=[convite.pk])
        self.assertContains(self.client.get(url), mensagens.PEDIDO_NAO_DISPONIVEL)

    def test_cenario12_cancelado_pelo_aluno(self):
        self.pedido.sol_status = StatusSolicitacao.CANCELADO
        self.pedido.sol_data_resposta = timezone.now()
        self.pedido.save()
        resposta = self.link()
        self.assertContains(resposta, mensagens.PEDIDO_CANCELADO_PELO_ALUNO)
        self.assertNotContains(resposta, f"solicitacao-{self.pedido.pk}")

    def test_cenario14_aceito_mostra_data_e_hora(self):
        self.aceitar()
        resposta = self.link()
        self.assertContains(resposta, "Aceito · ")

    def test_aceite_de_pedido_ja_cancelado_mostra_o_estado(self):
        self.pedido.sol_status = StatusSolicitacao.CANCELADO
        self.pedido.sol_data_resposta = timezone.now()
        self.pedido.save()
        resposta = self.aceitar()
        self.assertContains(resposta, mensagens.PEDIDO_CANCELADO_PELO_ALUNO)
        self.assertFalse(Orientacoes.objects.filter(ori_tcc=self.tcc).exists())

    def test_aceite_duplo_cria_um_vinculo(self):
        self.aceitar()
        self.aceitar()
        self.assertEqual(Orientacoes.objects.filter(ori_tcc=self.tcc).count(), 1)

    def test_turma_arquivada_recusa_com_mt25(self):
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save()
        resposta = self.aceitar()
        self.assertContains(resposta, mensagens.MT25_TURMA_ARQUIVADA)

    def test_get_nunca_grava(self):
        url = services_orientacao.link_da_solicitacao(self.pedido) + "?acao=aceitar"
        self.client.get(url)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.sol_status, StatusSolicitacao.AGUARDANDO_RESPOSTA)
        url = reverse("cadastro:aceitar_solicitacao", args=[self.pedido.pk])
        self.assertEqual(self.client.get(url).status_code, 405)


class TrocaTest(TesteTurmas):
    """Cenários 7 e 13, o ponto #17 e os casos da troca. [FR-010][FR-013][D13][A20]"""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=SI)
        self.aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        self.tcc = tcc_de(self.aluno, self.turma)
        self.x = criar_docente_ativo()
        self.y = criar_docente_ativo()
        vincular_orientador(self.tcc, self.x)
        self.troca = criar_pedido(self.tcc, self.y, TipoSolicitacao.TROCA_DE_ORIENTACAO)
        self.client.force_login(self.y)

    def aceitar(self):
        url = reverse("cadastro:aceitar_solicitacao", args=[self.troca.pk])
        return self.client.post(url, follow=True)

    def test_cenario7_troca_aceita(self):
        self.aceitar()
        ativa = Orientacoes.objects.get(ori_tcc=self.tcc, ori_status=StatusOrientacao.ATIVA)
        self.assertEqual(ativa.ori_doc_id, self.y.pk)
        anterior = Orientacoes.objects.get(ori_tcc=self.tcc, ori_doc_id=self.x.pk)
        self.assertEqual(anterior.ori_status, StatusOrientacao.ENCERRADA)
        self.assertEqual(anterior.ori_data_fim, ativa.ori_data_inicio)
        self.assertEqual(
            Notificacoes.objects.get(not_usu=self.x).not_mensagem,
            mensagens.MO05_TROCA_ORIENTADOR.format(
                nome=self.aluno.alu.usu_nome, docente=self.y.usu_nome
            ),
        )
        self.client.force_login(self.x)
        self.assertNotContains(
            self.client.get(reverse("cadastro:orientacoes")), self.tcc.tcc_titulo
        )

    def test_troca_encerra_a_coorientacao_e_cancela_o_convite_do_novo(self):
        vincular_coorientador(self.tcc, docente=self.y)
        convite = criar_convite(self.tcc, criar_docente_ativo())
        convite.sol_doc = self.y.docentes
        convite.save()
        self.aceitar()
        self.assertEqual(
            Coorientacoes.objects.get(coo_tcc=self.tcc, coo_doc_id=self.y.pk).coo_status,
            StatusCoorientacao.ENCERRADA,
        )
        convite.refresh_from_db()
        self.assertEqual(
            services_orientacao.motivo_do_cancelamento(convite),
            services_orientacao.MotivoCancelamento.DOCENTE_VIROU_ORIENTADOR,
        )

    def test_cenario13_link_da_troca_cancelada_pelo_agendamento(self):
        _, agora = agendar_defesa(self.tcc, self.professor)
        services_orientacao.cancelar_troca_no_agendamento(self.tcc, agora)
        resposta = self.client.get(services_orientacao.link_da_solicitacao(self.troca))
        self.assertContains(resposta, mensagens.PEDIDO_CANCELADO_AGENDAMENTO)

    def test_troca_com_sessao_ativa_recusada(self):
        criar_defesa_de(self.tcc, StatusSessao.AGENDADA)
        resposta = self.client.post(reverse("cadastro:aceitar_solicitacao", args=[self.troca.pk]))
        self.assertEqual(resposta.status_code, 404)
        self.assertEqual(
            Orientacoes.objects.get(ori_tcc=self.tcc, ori_status=StatusOrientacao.ATIVA).ori_doc_id,
            self.x.pk,
        )

    def test_ponto17_resumo_no_pedido_de_troca(self):
        self.assertTrue(services_tcc.pode_ver_resumo(self.y, self.tcc))
        resposta = self.client.get(reverse("cadastro:ver_proposta", args=[self.troca.pk]))
        self.assertContains(resposta, self.tcc.tcc_resumo)

    def test_pedido_de_troca_mostra_orientador_atual(self):
        resposta = self.client.get(reverse("cadastro:orientacoes"))
        self.assertContains(resposta, f"Orientador atual: {self.x.usu_nome}")


class OrientandosTest(TesteTurmas):
    """Cenários 8 e 9, pontos #15 e #16, MO-24 e R14. [FR-014][FR-015][FR-016]"""

    def setUp(self):
        super().setUp()
        self.docente = criar_docente_ativo()
        self.client.force_login(self.docente)

    def _orientando(self, turma=None, status=StatusTCC.EM_ANDAMENTO, **dados):
        turma = turma or criar_turma_de(criar_docente_ativo(), curso_nome=SI)
        aluno = matricular_aluno(turma, status_tcc=status, **dados)
        tcc = tcc_de(aluno, turma)
        vincular_orientador(tcc, self.docente)
        return aluno, tcc

    def test_secoes_vazias_mo24(self):
        resposta = self.client.get(reverse("cadastro:orientacoes"))
        self.assertContains(resposta, mensagens.MO24_SEM_PEDIDOS)
        self.assertContains(resposta, mensagens.MO24_SEM_CONVITES)
        self.assertContains(resposta, mensagens.MO24_SEM_ORIENTANDOS)

    def test_cenario8_listagem_de_docentes_mostra_6(self):
        """A contagem da listagem da spec 002 conta vínculos 'Ativa' em Orientacoes."""
        for _ in range(6):
            self._orientando()
        self.assertEqual(
            Orientacoes.objects.filter(
                ori_doc_id=self.docente.pk, ori_status=StatusOrientacao.ATIVA
            ).count(),
            6,
        )

    def test_cenario9_turma_arquivada_no_fim_so_atas(self):
        _, tcc_ativo = self._orientando()
        arquivada = criar_turma_de(criar_docente_ativo(), status=StatusTurma.ARQUIVADA)
        _, tcc_arq = self._orientando(turma=arquivada)
        registrar_ata(tcc_arq)
        linhas = services_orientacao.orientandos(self.docente)
        self.assertEqual([linha["tcc"].pk for linha in linhas], [tcc_ativo.pk, tcc_arq.pk])
        self.assertFalse(linhas[1]["pode_registrar_ata"])
        self.assertFalse(linhas[1]["pode_historico"])
        self.assertIsNone(linhas[1]["apto"])
        self.assertEqual(linhas[1]["n_atas"], 1)
        resposta = self.client.get(reverse("cadastro:orientacoes"))
        for coluna in ("Nome do Aluno", "Curso", "Turma", "Título", "Modalidade", "Papel"):
            self.assertContains(resposta, coluna)

    def test_coorientador_so_atas(self):
        turma = criar_turma_de(criar_docente_ativo(), curso_nome=SI)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        vincular_coorientador(tcc_de(aluno, turma), docente=self.docente)
        linha = services_orientacao.orientandos(self.docente)[0]
        self.assertEqual(linha["papel"], "Coorientador")
        self.assertFalse(linha["pode_historico"])
        self.assertIsNone(linha["apto"])
        self.assertTrue(linha["pode_registrar_ata"])

    def test_ponto15_historico_pela_linha(self):
        _, tcc = self._orientando()
        resposta = self.client.get(reverse("cadastro:orientacoes"))
        url = reverse("cadastro:historico_orientando", args=[tcc.pk])
        self.assertContains(resposta, url)
        historico = self.client.get(url)
        self.assertContains(historico, "Histórico do Status do TCC")
        self.assertContains(historico, f'href="{reverse("cadastro:orientacoes")}"')

    def test_ponto15_coorientador_sem_historico(self):
        turma = criar_turma_de(criar_docente_ativo(), curso_nome=SI)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        tcc = tcc_de(aluno, turma)
        vincular_coorientador(tcc, docente=self.docente)
        url = reverse("cadastro:historico_orientando", args=[tcc.pk])
        self.assertEqual(self.client.get(url).status_code, 404)

    def _correcoes(self, enviar=True):
        turma = criar_turma_de(criar_docente_ativo(), descricao=DescricaoTurma.TCC_2, curso_nome=SI)
        aluno, tcc = self._orientando(turma=turma, status=StatusTCC.APROVADO_COM_CORRECOES)
        entrega = cadastrar_entrega(
            turma, tipo=TipoEntrega.VERSAO_FINAL, data_limite=timezone.now() + timedelta(days=5)
        )
        registro = EntregasMarcos.objects.create(
            ent_tma=entrega,
            ent_alu=aluno,
            ent_status=StatusEntrega.ENTREGUE if enviar else StatusEntrega.AGUARDANDO_ENVIO,
        )
        if enviar:
            enviar_link(entrega, aluno, "https://drive.example/vf")
        return tcc, registro

    def test_ponto16_correcoes_conferidas(self):
        tcc, registro = self._correcoes()
        url = reverse("cadastro:correcoes_conferidas", args=[tcc.pk])
        self.assertContains(self.client.get(reverse("cadastro:orientacoes")), url)
        confirmacao = self.client.get(url)
        self.assertContains(
            confirmacao, mensagens.MO13_CONFIRMAR_CORRECOES.format(nome=tcc.tcc_alu.alu.usu_nome)
        )
        resposta = self.client.post(url, follow=True)
        self.assertContains(resposta, mensagens.MO13_CORRECOES_CONFERIDAS)
        registro.refresh_from_db()
        self.assertIsNotNone(registro.ent_correcoes_conferidas_em)
        self.assertContains(resposta, "Correções conferidas em ")

    def test_ponto16_sem_envio_nao_aparece(self):
        tcc, _ = self._correcoes(enviar=False)
        url = reverse("cadastro:correcoes_conferidas", args=[tcc.pk])
        self.assertNotContains(self.client.get(reverse("cadastro:orientacoes")), url)
        self.assertEqual(self.client.post(url).status_code, 404)

    def test_ponto16_devolucao_apaga_a_conferencia(self):
        tcc, registro = self._correcoes()
        self.client.post(reverse("cadastro:correcoes_conferidas", args=[tcc.pk]))
        from sigtcc.apps.cadastro import services_entregas

        professor = tcc.tcc_tur.tur_doc.doc
        services_entregas.devolver_versao_final(
            professor, tcc.tcc_tur_id, tcc.tcc_alu_id, "Ajustar a formatação"
        )
        registro.refresh_from_db()
        self.assertIsNone(registro.ent_correcoes_conferidas_em)

    def test_consultas_constantes_r14(self):
        self._orientando()
        with CaptureQueriesContext(connection) as uma:
            services_orientacao.orientandos(self.docente)
        for _ in range(9):
            self._orientando()
        with CaptureQueriesContext(connection) as dez:
            services_orientacao.orientandos(self.docente)
        self.assertEqual(len(uma.captured_queries), len(dez.captured_queries))

    def test_artigo_cientifico_tem_publicacao(self):
        aluno, tcc = self._orientando()
        salvar_proposta(tcc, modalidade=ModalidadeTCC.ARTIGO_CIENTIFICO)
        linha = services_orientacao.orientandos(self.docente)[0]
        self.assertTrue(linha["pode_publicacao"])
