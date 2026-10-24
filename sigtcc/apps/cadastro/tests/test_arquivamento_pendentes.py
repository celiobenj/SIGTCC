"""Arquivamento da turma cancela os pedidos e convites pendentes (FR-053; Q17; IC-12).

[US-07][RBN-CAD-04.5][FR-050][FR-053][Q17][IC-12] (tasks T009)
"""

from django.urls import reverse

from sigtcc.apps.cadastro import mensagens, services_orientacao, services_turmas
from sigtcc.apps.cadastro.choices import StatusSolicitacao, StatusTCC, StatusTurma
from sigtcc.apps.cadastro.models import Notificacoes
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo
from sigtcc.apps.cadastro.tests.apoio_orientacao import criar_convite, criar_pedido
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    TesteTurmas,
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)


class ArquivamentoPendentesTest(TesteTurmas):
    """Q17: os pendentes saem com o mesmo instante e a MO-26 leva ao pedido ou convite."""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor)
        self.aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.SEM_PROPOSTA)
        self.tcc = tcc_de(self.aluno, self.turma)
        self.docente_pedido = criar_docente_ativo()
        self.docente_convite = criar_docente_ativo()
        self.pedido = criar_pedido(self.tcc, self.docente_pedido)
        outro = matricular_aluno(self.turma, status_tcc=StatusTCC.SEM_PROPOSTA)
        self.convite = criar_convite(tcc_de(outro, self.turma), self.docente_convite)

    def test_pendentes_cancelados_com_o_mesmo_instante(self):
        services_turmas.arquivar_turma(self.professor, self.turma.pk)
        self.turma.refresh_from_db()
        self.assertEqual(self.turma.tur_status, StatusTurma.ARQUIVADA)
        self.pedido.refresh_from_db()
        self.convite.refresh_from_db()
        self.assertEqual(self.pedido.sol_status, StatusSolicitacao.CANCELADO)
        self.assertEqual(self.convite.sol_status, StatusSolicitacao.CANCELADO)
        self.assertEqual(self.pedido.sol_data_resposta, self.convite.sol_data_resposta)

    def test_mo26_com_o_link_da_solicitacao_e_o_mesmo_instante(self):
        services_turmas.arquivar_turma(self.professor, self.turma.pk)
        for solicitacao, docente, tipo in (
            (self.pedido, self.docente_pedido, mensagens.TIPO_PEDIDO_ORIENTACAO),
            (self.convite, self.docente_convite, mensagens.TIPO_CONVITE_COORIENTACAO),
        ):
            solicitacao.refresh_from_db()
            aviso = Notificacoes.objects.get(not_usu=docente)
            self.assertEqual(
                aviso.not_link_tela, services_orientacao.link_da_solicitacao(solicitacao)
            )
            self.assertEqual(aviso.not_data_hora, solicitacao.sol_data_resposta)
            self.assertEqual(
                aviso.not_mensagem,
                mensagens.MO26_NOTIFICACAO.format(
                    tipo=tipo,
                    nome=solicitacao.sol_tcc.tcc_alu.alu.usu_nome,
                    identificador=self.turma.tur_identificador,
                ),
            )

    def test_link_e_a_rota_do_pedido_ou_do_convite(self):
        services_turmas.arquivar_turma(self.professor, self.turma.pk)
        aviso = Notificacoes.objects.get(not_usu=self.docente_pedido)
        self.assertEqual(
            aviso.not_link_tela, reverse("cadastro:pedido_orientacao", args=[self.pedido.pk])
        )

    def test_arquivamento_recusado_nao_cancela(self):
        """Com TCC 'Em Andamento', o arquivamento é recusado e nada muda (RBN-CAD-04.5)."""
        matricular_aluno(self.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        with self.assertRaises(services_turmas.ErroTurma):
            services_turmas.arquivar_turma(self.professor, self.turma.pk)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.sol_status, StatusSolicitacao.AGUARDANDO_RESPOSTA)
        self.assertFalse(Notificacoes.objects.filter(not_usu=self.docente_pedido).exists())

    def test_solicitacao_ja_respondida_nao_muda(self):
        self.pedido.sol_status = StatusSolicitacao.RECUSADO
        self.pedido.save()
        services_turmas.arquivar_turma(self.professor, self.turma.pk)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.sol_status, StatusSolicitacao.RECUSADO)
