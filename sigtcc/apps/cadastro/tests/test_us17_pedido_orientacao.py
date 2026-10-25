"""Testes de aceite da US-17: indicar, cancelar ou trocar o orientador (spec 006, User Story 1).

Cenários 1 a 12 da US-17, mais: duplo envio, docente inativado no meio (Q-68), e-mail só depois
do commit, MO-16 no pedido de troca, troca bloqueada por sessão ativa, cancelamento da troca no
agendamento (MO-06) e o histórico de orientação (FR-049). As partes que dependem da resposta do
docente (aceite e recusa pela tela Orientações) são simuladas aqui e testadas na US-18.

[US-17][RBN-CAD-10.1][RBN-CAD-10.6][FR-001 a FR-008][FR-047][FR-049] (tasks T013)
"""

from django.core import mail
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services_orientacao
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    OrigemOrientacao,
    StatusConta,
    StatusOrientacao,
    StatusSolicitacao,
    StatusTCC,
    StatusTurma,
    TipoSolicitacao,
)
from sigtcc.apps.cadastro.models import Notificacoes, Orientacoes, SolicitacoesOrientacao
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo
from sigtcc.apps.cadastro.tests.apoio_orientacao import (
    agendar_defesa,
    criar_pedido,
    vincular_orientador,
)
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    SI,
    TesteTurmas,
    criar_defesa_de,
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)
from sigtcc.apps.defesa.choices import StatusSessao


class PedidoOrientacaoTestBase(TesteTurmas):
    """Turma de TCC 1 de SI (sem orientador automático) e um aluno com TCC 'Em Andamento'."""

    status_tcc = StatusTCC.EM_ANDAMENTO

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=SI)
        self.aluno = matricular_aluno(
            self.turma, status_tcc=self.status_tcc, status_conta=StatusConta.ATIVA
        )
        self.tcc = tcc_de(self.aluno, self.turma)
        self.docente = criar_docente_ativo()
        self.docente.usu_nome = "Maria Docente Silva"
        self.docente.save()
        self.client.force_login(self.aluno.alu)

    def secao(self):
        url = reverse("cadastro:meu_tcc", args=[self.turma.pk])
        return self.client.get(f"{url}?secao=orientacao")

    def enviar(self, docente=None, follow=True):
        url = reverse("cadastro:enviar_pedido_orientacao", args=[self.turma.pk])
        return self.client.post(url, {"docente": (docente or self.docente).pk}, follow=follow)

    def cancelar(self):
        url = reverse("cadastro:cancelar_pedido_orientacao", args=[self.turma.pk])
        return self.client.post(url, follow=True)

    def pedido(self):
        return SolicitacoesOrientacao.objects.get(sol_tcc=self.tcc)


class PedidoOrientacaoTest(PedidoOrientacaoTestBase):
    """Cenários 1 a 4, 8, 9, 11 e 12. [US-17][FR-001 a FR-004][FR-007]"""

    def test_cenario1_envio_bloqueia_a_lista_e_mostra_cancelar(self):
        resposta = self.enviar()
        pedido = self.pedido()
        self.assertEqual(pedido.sol_status, StatusSolicitacao.AGUARDANDO_RESPOSTA)
        self.assertEqual(pedido.sol_tipo, TipoSolicitacao.ORIENTACAO)
        self.assertContains(
            resposta, mensagens.PEDIDO_ENVIADO.format(docente="Maria Docente Silva")
        )
        self.assertContains(resposta, "Cancelar Pedido")
        self.assertContains(resposta, 'name="docente" disabled')
        self.assertRedirects(
            self.enviar(follow=False),
            f"{reverse('cadastro:meu_tcc', args=[self.turma.pk])}?secao=orientacao",
            fetch_redirect_response=False,
        )

    def test_cenario1_apos_o_aceite_mostra_o_orientador(self):
        self.enviar()
        pedido = self.pedido()
        pedido.sol_status = StatusSolicitacao.ACEITO
        pedido.sol_data_resposta = timezone.now()
        pedido.save()
        vincular_orientador(self.tcc, self.docente)
        resposta = self.secao()
        self.assertContains(resposta, "Maria Docente Silva")
        self.assertContains(resposta, "Orientador")
        self.assertContains(resposta, "Trocar de orientador")

    def test_cenario3_recusa_libera_a_lista(self):
        self.enviar()
        pedido = self.pedido()
        pedido.sol_status = StatusSolicitacao.RECUSADO
        pedido.sol_data_resposta = timezone.now()
        pedido.save()
        resposta = self.secao()
        self.assertContains(resposta, "Indicar orientador")
        self.assertNotContains(resposta, 'name="docente" disabled')

    def test_cenario4_cancelar_pedido(self):
        self.enviar()
        resposta = self.cancelar()
        self.assertEqual(self.pedido().sol_status, StatusSolicitacao.CANCELADO)
        self.assertIsNotNone(self.pedido().sol_data_resposta)
        self.assertContains(resposta, "Indicar orientador")
        self.assertNotContains(resposta, "Cancelar Pedido")

    def test_cenario8_sem_sessao_vai_ao_login_e_volta_a_secao(self):
        self.client.logout()
        resposta = self.secao()
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("cadastro:entrar"), resposta.url)
        self.assertIn("secao%3Dorientacao", resposta.url)

    def test_cenario9_pedido_pendente_so_cancelar(self):
        criar_pedido(self.tcc, self.docente)
        resposta = self.secao()
        self.assertContains(resposta, 'name="docente" disabled')
        self.assertContains(resposta, "Cancelar Pedido")
        self.assertNotContains(resposta, 'value="enviar"')

    def test_cenario11_desistente_so_consulta(self):
        self.tcc.tcc_status = StatusTCC.DESISTENTE
        self.tcc.save()
        resposta = self.secao()
        self.assertContains(resposta, mensagens.SEM_ORIENTADOR)
        self.assertNotContains(resposta, "Indicar orientador")
        self.assertNotContains(resposta, "Enviar pedido")
        self.assertEqual(self.enviar(follow=False).status_code, 404)
        self.assertFalse(SolicitacoesOrientacao.objects.exists())

    def test_cenario12_turma_arquivada_so_consulta(self):
        criar_pedido(self.tcc, self.docente)
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save()
        resposta = self.secao()
        self.assertNotContains(resposta, "Cancelar Pedido")
        self.assertNotContains(resposta, "Enviar pedido")
        resposta = self.cancelar()
        self.assertContains(resposta, mensagens.MT25_TURMA_ARQUIVADA)
        self.assertEqual(self.pedido().sol_status, StatusSolicitacao.AGUARDANDO_RESPOSTA)

    def test_lista_com_docentes_ativos_nome_titulacao_e_curso(self):
        inativo = criar_docente_ativo(status=StatusConta.INATIVA)
        resposta = self.secao()
        self.assertContains(resposta, "Maria Docente Silva")
        self.assertContains(resposta, self.docente.docentes.doc_cur.cur_nome)
        self.assertNotContains(resposta, f'value="{inativo.pk}"')

    def test_duplo_envio_cria_um_pedido_so(self):
        self.enviar()
        self.enviar(criar_docente_ativo())
        self.assertEqual(SolicitacoesOrientacao.objects.filter(sol_tcc=self.tcc).count(), 1)

    def test_docente_inativado_no_meio_e_recusado(self):
        """Q-68: o envio trava e reconfere a conta do docente."""
        self.docente.usu_status = StatusConta.INATIVA
        self.docente.save()
        self.enviar()
        self.assertFalse(SolicitacoesOrientacao.objects.exists())

    def test_outra_turma_404(self):
        outra = criar_turma_de(criar_docente_ativo(), curso_nome=SI)
        url = reverse("cadastro:enviar_pedido_orientacao", args=[outra.pk])
        resposta = self.client.post(url, {"docente": self.docente.pk})
        self.assertEqual(resposta.status_code, 404)


class NotificacaoPedidoTest(PedidoOrientacaoTestBase):
    """Cenário 2 e as notificações do envio. [US-17][FR-003][FR-052][MO-01][MO-16]"""

    status_tcc = StatusTCC.SEM_PROPOSTA

    def test_cenario2_sem_proposta_notificacao_e_email(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.enviar()
        pedido = self.pedido()
        texto = mensagens.MO01_PEDIDO_ORIENTACAO.format(
            nome=self.aluno.alu.usu_nome, titulo=mensagens.PROPOSTA_AINDA_NAO_REGISTRADA
        )
        aviso = Notificacoes.objects.get(not_usu=self.docente)
        self.assertEqual(aviso.not_mensagem, texto)
        self.assertEqual(aviso.not_link_tela, services_orientacao.link_da_solicitacao(pedido))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, mensagens.MO01_ASSUNTO)
        self.assertIn(mensagens.PROPOSTA_AINDA_NAO_REGISTRADA, mail.outbox[0].body)
        self.assertIn(services_orientacao.link_da_solicitacao(pedido), mail.outbox[0].body)

    def test_email_so_depois_do_commit(self):
        with self.captureOnCommitCallbacks(execute=False) as callbacks:
            self.enviar()
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(len(callbacks), 1)


class TrocaOrientadorTest(PedidoOrientacaoTestBase):
    """Cenários 5, 6, 7 e 10; FR-005, FR-006, FR-008. [US-17][RBN-CAD-10.6]"""

    def setUp(self):
        super().setUp()
        self.atual = criar_docente_ativo()
        self.atual.usu_nome = "Carlos Orientador Atual"
        self.atual.save()
        vincular_orientador(self.tcc, self.atual)

    def test_cenario5_troca_mantem_o_atual_ate_o_aceite(self):
        with self.captureOnCommitCallbacks(execute=True):
            resposta = self.enviar()
        pedido = self.pedido()
        self.assertEqual(pedido.sol_tipo, TipoSolicitacao.TROCA_DE_ORIENTACAO)
        self.assertEqual(services_orientacao.orientador_atual(self.tcc).pk, self.atual.pk)
        self.assertContains(resposta, "Carlos Orientador Atual")
        aviso = Notificacoes.objects.get(not_usu=self.docente)
        self.assertEqual(
            aviso.not_mensagem,
            mensagens.MO16_PEDIDO_TROCA.format(
                nome=self.aluno.alu.usu_nome,
                titulo=self.tcc.tcc_titulo,
                orientador="Carlos Orientador Atual",
            ),
        )
        self.assertEqual(mail.outbox[0].subject, mensagens.MO16_ASSUNTO)

    def test_lista_de_troca_sem_o_orientador_atual(self):
        resposta = self.secao()
        self.assertContains(resposta, "Trocar de orientador")
        self.assertNotContains(resposta, f'<option value="{self.atual.pk}"')
        self.enviar(self.atual)
        self.assertFalse(SolicitacoesOrientacao.objects.exists())

    def test_cenario6_agendamento_cancela_a_troca(self):
        self.enviar()
        _, agora = agendar_defesa(self.tcc, self.professor)
        services_orientacao.cancelar_troca_no_agendamento(self.tcc, agora)
        pedido = self.pedido()
        self.assertEqual(pedido.sol_status, StatusSolicitacao.CANCELADO)
        self.assertEqual(services_orientacao.orientador_atual(self.tcc).pk, self.atual.pk)
        self.assertEqual(
            Notificacoes.objects.get(not_usu=self.aluno.alu).not_mensagem,
            mensagens.MO06_TROCA_CANCELADA_ALUNO,
        )
        self.assertTrue(
            Notificacoes.objects.filter(
                not_usu=self.docente,
                not_mensagem=mensagens.MO06_TROCA_CANCELADA_DOCENTE.format(
                    nome=self.aluno.alu.usu_nome
                ),
            ).exists()
        )

    def test_cancelar_troca_sem_pedido_devolve_none(self):
        self.assertIsNone(
            services_orientacao.cancelar_troca_no_agendamento(self.tcc, timezone.now())
        )

    def test_cenario10_defesa_agendada_lista_desabilitada(self):
        criar_defesa_de(self.tcc, StatusSessao.AGENDADA)
        resposta = self.secao()
        self.assertContains(resposta, "Trocar de orientador")
        self.assertContains(resposta, 'name="docente" disabled')
        self.enviar()
        self.assertFalse(SolicitacoesOrientacao.objects.exists())

    def test_historico_de_orientacao_fr049(self):
        """FR-049: orientador anterior e pedidos recusados ou cancelados, com datas."""
        anterior = services_orientacao.orientador_atual(self.tcc)
        orientacao = Orientacoes.objects.get(ori_tcc=self.tcc)
        orientacao.ori_status = StatusOrientacao.ENCERRADA
        orientacao.ori_data_fim = timezone.now()
        orientacao.save()
        vincular_orientador(self.tcc, self.docente)
        recusado = criar_pedido(self.tcc, criar_docente_ativo())
        recusado.sol_status = StatusSolicitacao.RECUSADO
        recusado.sol_data_resposta = timezone.now()
        recusado.save()
        historico = services_orientacao.historico_de_orientacao(self.tcc)
        self.assertEqual(len(historico), 2)
        resposta = self.secao()
        self.assertContains(resposta, "Histórico de orientação (2)")
        self.assertContains(resposta, anterior.doc.usu_nome)


class OrientadorAutomaticoTest(TesteTurmas):
    """Cenário 7: TCC 2 de EC, o professor já é o Orientador, sem listas. [FR-006]"""

    def test_cenario7_sem_lista_em_tcc2_de_ec(self):
        professor = criar_docente_ativo()
        professor.usu_nome = "Paulo Professor"
        professor.save()
        turma = criar_turma_de(professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        aluno = matricular_aluno(
            turma, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        )
        vincular_orientador(tcc_de(aluno, turma), professor, origem=OrigemOrientacao.AUTOMATICO)
        self.client.force_login(aluno.alu)
        resposta = self.client.get(reverse("cadastro:meu_tcc", args=[turma.pk]))
        self.assertContains(resposta, "Paulo Professor")
        self.assertNotContains(resposta, "Indicar orientador")
        self.assertNotContains(resposta, "Trocar de orientador")
        url = reverse("cadastro:enviar_pedido_orientacao", args=[turma.pk])
        self.client.post(url, {"docente": criar_docente_ativo().pk})
        self.assertFalse(SolicitacoesOrientacao.objects.exists())
