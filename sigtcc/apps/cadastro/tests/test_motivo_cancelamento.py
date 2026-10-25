"""Motivo do cancelamento de pedidos e convites, sem coluna nova (FR-050; research R3; Q7, Q17).

Relógio real (sem congelar o tempo): com o relógio congelado, todo `timezone.now()` seria igual e
os testes passariam mesmo sem o instante único do evento (IC-04). Para cada motivo, o evento real
das specs 004 e 006 e a igualdade gravada; e o teste negativo "o aluno cancela e, depois, o
evento acontece → ALUNO".

[US-17][US-18][US-36][RBN-CAD-10.6][FR-050][FR-053][Q7][Q17][research R3] (tasks T009)
"""

from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services_orientacao, services_turmas
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    OrigemOrientacao,
    StatusSolicitacao,
    StatusTCC,
    TipoSolicitacao,
)
from sigtcc.apps.cadastro.services_orientacao import MotivoCancelamento, motivo_do_cancelamento
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo
from sigtcc.apps.cadastro.tests.apoio_orientacao import (
    agendar_defesa,
    criar_convite,
    criar_pedido,
    vincular_orientador,
)
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    SI,
    TesteTurmas,
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)


def cancelar_pelo_aluno(solicitacao):
    """Simula o "Cancelar Pedido"/"Remover" do aluno: 'Cancelado' com o instante de agora.

    Depois, espera o relógio avançar: no Windows a resolução do relógio é de ~15 ms, e duas
    chamadas seguidas podem receber o mesmo instante, o que não ocorre entre requisições
    distintas do aluno e do evento (research R3, A13).
    """
    solicitacao.sol_status = StatusSolicitacao.CANCELADO
    solicitacao.sol_data_resposta = timezone.now()
    solicitacao.save()
    while timezone.now() == solicitacao.sol_data_resposta:
        pass


class MotivoCancelamentoTest(TesteTurmas):
    """Um teste por motivo e os negativos. [FR-050]"""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.docente = criar_docente_ativo()

    def _aluno_em(self, turma, status=StatusTCC.EM_ANDAMENTO):
        aluno = matricular_aluno(turma, status_tcc=status)
        return aluno, tcc_de(aluno, turma)

    # -------------------------------------------------------------------- AGENDAMENTO (1)

    def test_agendamento(self):
        turma = criar_turma_de(self.professor, curso_nome=SI)
        _, tcc = self._aluno_em(turma)
        vincular_orientador(tcc, criar_docente_ativo())
        troca = criar_pedido(tcc, self.docente, TipoSolicitacao.TROCA_DE_ORIENTACAO)
        _, agora = agendar_defesa(tcc, self.professor)
        services_orientacao.cancelar_troca_no_agendamento(tcc, agora)
        troca.refresh_from_db()
        self.assertEqual(troca.sol_data_resposta, agora)
        self.assertEqual(motivo_do_cancelamento(troca), MotivoCancelamento.AGENDAMENTO)
        self.assertEqual(
            services_orientacao.texto_do_cancelamento(troca),
            mensagens.PEDIDO_CANCELADO_AGENDAMENTO,
        )

    def test_aluno_cancela_e_depois_a_defesa_e_agendada(self):
        turma = criar_turma_de(self.professor, curso_nome=SI)
        _, tcc = self._aluno_em(turma)
        troca = criar_pedido(tcc, self.docente, TipoSolicitacao.TROCA_DE_ORIENTACAO)
        cancelar_pelo_aluno(troca)
        agendar_defesa(tcc, self.professor)
        self.assertEqual(motivo_do_cancelamento(troca), MotivoCancelamento.ALUNO)
        self.assertEqual(
            services_orientacao.texto_do_cancelamento(troca),
            mensagens.PEDIDO_CANCELADO_PELO_ALUNO,
        )

    # ------------------------------------------------------------------- ENCERRAMENTO (2)

    def test_encerramento(self):
        turma = criar_turma_de(self.professor)
        aluno, tcc = self._aluno_em(turma)
        pedido = criar_pedido(tcc, self.docente)
        convite = criar_convite(tcc, criar_docente_ativo())
        services_turmas.encerrar_participacao(
            self.professor, turma.pk, aluno.pk, StatusTCC.DESISTENTE, "Desistiu do curso"
        )
        for solicitacao, texto in (
            (pedido, mensagens.MO12_PEDIDO_CANCELADO_ENCERRAMENTO),
            (convite, mensagens.MO12_CONVITE_CANCELADO_ENCERRAMENTO),
        ):
            solicitacao.refresh_from_db()
            self.assertEqual(motivo_do_cancelamento(solicitacao), MotivoCancelamento.ENCERRAMENTO)
            self.assertEqual(services_orientacao.texto_do_cancelamento(solicitacao), texto)

    def test_aluno_cancela_e_depois_a_participacao_e_encerrada(self):
        turma = criar_turma_de(self.professor)
        aluno, tcc = self._aluno_em(turma)
        pedido = criar_pedido(tcc, self.docente)
        cancelar_pelo_aluno(pedido)
        services_turmas.encerrar_participacao(
            self.professor, turma.pk, aluno.pk, StatusTCC.DESISTENTE, "Desistiu do curso"
        )
        pedido.refresh_from_db()
        self.assertEqual(motivo_do_cancelamento(pedido), MotivoCancelamento.ALUNO)

    # ------------------------------------------------------- DOCENTE_VIROU_ORIENTADOR (3)

    def _transferencia(self):
        origem = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        aluno, tcc = self._aluno_em(origem)
        vincular_orientador(tcc, self.professor, origem=OrigemOrientacao.AUTOMATICO)
        destino = criar_turma_de(self.docente, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        return origem, aluno, tcc, destino

    def test_docente_virou_orientador_na_transferencia(self):
        origem, aluno, tcc, destino = self._transferencia()
        convite = criar_convite(tcc, self.docente)
        services_turmas.transferir(self.professor, origem.pk, aluno.pk, destino.pk, "Ajuste")
        convite.refresh_from_db()
        self.assertEqual(convite.sol_status, StatusSolicitacao.CANCELADO)
        self.assertEqual(
            motivo_do_cancelamento(convite), MotivoCancelamento.DOCENTE_VIROU_ORIENTADOR
        )
        self.assertEqual(
            services_orientacao.texto_do_cancelamento(convite),
            mensagens.MO17_CONVITE_CANCELADO_ORIENTADOR,
        )

    def test_aluno_remove_convite_e_depois_o_docente_vira_orientador(self):
        origem, aluno, tcc, destino = self._transferencia()
        convite = criar_convite(tcc, self.docente)
        cancelar_pelo_aluno(convite)
        services_turmas.transferir(self.professor, origem.pk, aluno.pk, destino.pk, "Ajuste")
        convite.refresh_from_db()
        self.assertEqual(motivo_do_cancelamento(convite), MotivoCancelamento.ALUNO)

    # ------------------------------------------------------------------- COPIA_TCC_2 (4)

    def _copia(self, professor_tcc2):
        turma1 = criar_turma_de(criar_docente_ativo(), curso_nome=EC)
        aluno = matricular_aluno(
            turma1, matricula="2026000456", status_tcc=StatusTCC.APROVADO_PARA_TCC_2
        )
        turma2 = criar_turma_de(professor_tcc2, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        return aluno, tcc_de(aluno, turma1), turma2

    def _matricular(self, professor, turma2):
        services_turmas.matricular_individual(
            professor, turma2.pk, "2026000456", "Ana Maria Souza", "EST08MCPD"
        )

    def test_copia_para_tcc2(self):
        aluno, tcc1, turma2 = self._copia(self.professor)
        pedido = criar_pedido(tcc1, self.docente)
        self._matricular(self.professor, turma2)
        pedido.refresh_from_db()
        self.assertEqual(motivo_do_cancelamento(pedido), MotivoCancelamento.COPIA_TCC_2)
        self.assertEqual(
            services_orientacao.texto_do_cancelamento(pedido),
            mensagens.MO18_PEDIDO_CANCELADO_COPIA,
        )

    def test_contraexemplo_convite_ao_orientador_automatico_do_tcc2(self):
        """R3: convite a P no TCC 1 e orientação automática de P no TCC 2, com o mesmo instante:
        como a consulta 3 exige o mesmo TCC, o motivo é COPIA_TCC_2."""
        aluno, tcc1, turma2 = self._copia(self.professor)
        convite = criar_convite(tcc1, self.professor)
        self._matricular(self.professor, turma2)
        convite.refresh_from_db()
        self.assertEqual(motivo_do_cancelamento(convite), MotivoCancelamento.COPIA_TCC_2)

    def test_aluno_cancela_e_depois_o_tcc_e_copiado(self):
        aluno, tcc1, turma2 = self._copia(self.professor)
        pedido = criar_pedido(tcc1, self.docente)
        cancelar_pelo_aluno(pedido)
        self._matricular(self.professor, turma2)
        pedido.refresh_from_db()
        self.assertEqual(motivo_do_cancelamento(pedido), MotivoCancelamento.ALUNO)

    # --------------------------------------------------------------- TURMA_ARQUIVADA (5)

    def test_turma_arquivada(self):
        turma = criar_turma_de(self.professor)
        _, tcc = self._aluno_em(turma, StatusTCC.SEM_PROPOSTA)
        pedido = criar_pedido(tcc, self.docente)
        services_turmas.arquivar_turma(self.professor, turma.pk)
        pedido.refresh_from_db()
        self.assertEqual(motivo_do_cancelamento(pedido), MotivoCancelamento.TURMA_ARQUIVADA)
        self.assertEqual(
            services_orientacao.texto_do_cancelamento(pedido),
            mensagens.MO26_PEDIDO_CANCELADO_ARQUIVAMENTO,
        )

    def test_aluno_cancela_antes_do_arquivamento(self):
        """US-18 E3 e US-36 E3: continua "cancelado pelo aluno"."""
        turma = criar_turma_de(self.professor)
        _, tcc = self._aluno_em(turma, StatusTCC.SEM_PROPOSTA)
        pedido = criar_pedido(tcc, self.docente)
        cancelar_pelo_aluno(pedido)
        services_turmas.arquivar_turma(self.professor, turma.pk)
        pedido.refresh_from_db()
        self.assertEqual(motivo_do_cancelamento(pedido), MotivoCancelamento.ALUNO)

    # -------------------------------------------------------------------------- ALUNO (6)

    def test_sem_evento_e_o_aluno(self):
        turma = criar_turma_de(self.professor)
        _, tcc = self._aluno_em(turma)
        convite = criar_convite(tcc, self.docente)
        cancelar_pelo_aluno(convite)
        self.assertEqual(motivo_do_cancelamento(convite), MotivoCancelamento.ALUNO)
        self.assertEqual(
            services_orientacao.texto_do_cancelamento(convite),
            mensagens.CONVITE_CANCELADO_PELO_ALUNO,
        )
