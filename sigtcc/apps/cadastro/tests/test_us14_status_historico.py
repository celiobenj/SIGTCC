"""Testes da US-14 (Status, histórico e trilha do TCC) — spec 005.

Nesta fase (T007, Foundational): só `services_tcc.pode_ver_resumo` (FR-007a, research C3) e
`services_tcc.historico_do_status` (FR-009, FR-010, research C9), sem nenhuma view ainda. Os
cenários de aceite da US-14 que dependem de view/rota (consulta pelo Aluno, pelo Professor, e os
cenários de exceção de tela) vêm na Phase 4 (T014), que complementa este arquivo.

[US-14][RBN-CAD-08.3][RBN-CAD-08.7][FR-007a][FR-009][FR-010][research C3][research C9]
"""

from django.utils import timezone

from sigtcc.apps.cadastro import services_tcc, services_turmas
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    GatilhoStatusTCC,
    ModalidadeTCC,
    OrigemOrientacao,
    StatusCoorientacao,
    StatusOrientacao,
    StatusSolicitacao,
    StatusTCC,
    TipoSolicitacao,
)
from sigtcc.apps.cadastro.models import Coorientacoes, Orientacoes, SolicitacoesOrientacao
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    TesteTurmas,
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)


class PodeVerResumoTest(TesteTurmas):
    """pode_ver_resumo: as 5 categorias autorizadas e um Docente sem vínculo (False).

    [US-13][RAN-CAD-07][FR-007a][research C3]
    """

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        self.aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        self.tcc = tcc_de(self.aluno, self.turma)

    def test_aluno_dono_ve_o_resumo(self):
        self.assertTrue(services_tcc.pode_ver_resumo(self.aluno.alu, self.tcc))

    def test_orientador_atual_ve_o_resumo(self):
        orientador = criar_docente_ativo()
        Orientacoes.objects.create(
            ori_tcc=self.tcc,
            ori_doc=orientador.docentes,
            ori_origem=OrigemOrientacao.PEDIDO_ACEITO,
            ori_status=StatusOrientacao.ATIVA,
            ori_data_inicio=timezone.now(),
        )
        self.assertTrue(services_tcc.pode_ver_resumo(orientador, self.tcc))

    def test_docente_com_pedido_de_orientacao_pendente_ve_o_resumo(self):
        docente = criar_docente_ativo()
        SolicitacoesOrientacao.objects.create(
            sol_tcc=self.tcc,
            sol_doc=docente.docentes,
            sol_tipo=TipoSolicitacao.ORIENTACAO,
            sol_status=StatusSolicitacao.AGUARDANDO_RESPOSTA,
            sol_data_solicitacao=timezone.now(),
        )
        self.assertTrue(services_tcc.pode_ver_resumo(docente, self.tcc))

    def test_coorientador_do_nucomp_com_coorientacao_ativa_ve_o_resumo(self):
        coorientador = criar_docente_ativo()
        Coorientacoes.objects.create(
            coo_tcc=self.tcc,
            coo_doc=coorientador.docentes,
            coo_status=StatusCoorientacao.ATIVA,
            coo_data_inicio=timezone.now(),
        )
        self.assertTrue(services_tcc.pode_ver_resumo(coorientador, self.tcc))

    def test_professor_da_disciplina_da_turma_ve_o_resumo(self):
        self.assertTrue(services_tcc.pode_ver_resumo(self.professor, self.tcc))

    def test_docente_sem_vinculo_nao_ve_o_resumo(self):
        outro = criar_docente_ativo()
        self.assertFalse(services_tcc.pode_ver_resumo(outro, self.tcc))

    def test_coorientador_sem_coorientacao_aceita_nao_ve_o_resumo(self):
        """Coorientação 'Encerrada' (não 'Ativa') não autoriza — só a aceita vale (FR-007a)."""
        coorientador = criar_docente_ativo()
        Coorientacoes.objects.create(
            coo_tcc=self.tcc,
            coo_doc=coorientador.docentes,
            coo_status=StatusCoorientacao.ENCERRADA,
            coo_data_inicio=timezone.now(),
            coo_data_fim=timezone.now(),
        )
        self.assertFalse(services_tcc.pode_ver_resumo(coorientador, self.tcc))

    def test_usuario_anonimo_nao_ve_o_resumo(self):
        self.assertFalse(services_tcc.pode_ver_resumo(None, self.tcc))


class HistoricoDoStatusTest(TesteTurmas):
    """historico_do_status: ordem cronológica, sem checagem de perfil (research C9).

    [US-14][RBN-CAD-08.7][FR-009][FR-010][research C9]
    """

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)

    def test_devolve_as_mudancas_da_mais_antiga_para_a_mais_recente(self):
        aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.SEM_PROPOSTA)
        tcc = tcc_de(aluno, self.turma)
        tcc.tcc_titulo = "Título"
        tcc.tcc_resumo = "Resumo"
        tcc.tcc_modalidade = ModalidadeTCC.MONOGRAFIA
        tcc.save(update_fields=["tcc_titulo", "tcc_resumo", "tcc_modalidade"])
        services_turmas.atualizar_status_tcc(
            tcc, self.turma, aluno.alu, StatusTCC.EM_ANDAMENTO, GatilhoStatusTCC.PROPOSTA_SALVA
        )
        historico = list(services_tcc.historico_do_status(tcc))
        self.assertEqual(len(historico), 2)
        self.assertIsNone(historico[0].hst_status_anterior)
        self.assertEqual(historico[0].hst_status_novo, StatusTCC.SEM_PROPOSTA)
        self.assertEqual(historico[1].hst_status_anterior, StatusTCC.SEM_PROPOSTA)
        self.assertEqual(historico[1].hst_status_novo, StatusTCC.EM_ANDAMENTO)

    def test_nao_filtra_por_perfil_quem_chama_decide(self):
        """A função devolve o histórico para qualquer chamador; a checagem de quem pode ver é
        responsabilidade da view (research C9), não desta função."""
        aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.SEM_PROPOSTA)
        tcc = tcc_de(aluno, self.turma)
        historico = services_tcc.historico_do_status(tcc)
        self.assertEqual(historico.count(), 1)
