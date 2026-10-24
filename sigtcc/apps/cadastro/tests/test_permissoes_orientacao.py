"""Vínculo, papéis e permissões da feature 006 (SC-006; research R10).

Seção "vínculo" (T007): papéis por vínculo ativo, orientador automático com dois papéis,
ex-orientador e convite pendente sem papel (Q10; US-19 #16), TCC copiado para o TCC 2 (Q6) e
link único da solicitação. As seções de rotas e de concorrência vêm em T056 e T057.

[US-17][US-18][US-19][US-36][RBN-CAD-10.4][RBN-CAD-11.2][FR-007][FR-023][FR-046][Q6][Q10]
"""

from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import services_orientacao as so
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    GatilhoStatusTCC,
    OrigemOrientacao,
    StatusOrientacao,
    StatusTCC,
    StatusTurma,
    TipoSolicitacao,
)
from sigtcc.apps.cadastro.models import HistoricoStatusTCC, TCCs
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo
from sigtcc.apps.cadastro.tests.apoio_orientacao import (
    criar_convite,
    criar_externo,
    criar_pedido,
    vincular_coorientador,
    vincular_orientador,
)
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    TesteTurmas,
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)


class VinculoTest(TesteTurmas):
    """Papéis por vínculo ativo e regras de alteração no TCC. [FR-007][FR-046][Q10]"""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.orientador = criar_docente_ativo()
        self.coorientador = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor)
        self.aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        self.tcc = tcc_de(self.aluno, self.turma)

    def test_cada_papel_por_vinculo_ativo(self):
        vincular_orientador(self.tcc, self.orientador)
        vincular_coorientador(self.tcc, docente=self.coorientador)
        self.assertEqual(so.papeis_no_tcc(self.aluno.alu, self.tcc), {"aluno"})
        self.assertEqual(so.papeis_no_tcc(self.orientador, self.tcc), {"orientador"})
        self.assertEqual(so.papeis_no_tcc(self.coorientador, self.tcc), {"coorientador"})
        self.assertEqual(so.papeis_no_tcc(self.professor, self.tcc), {"professor"})
        self.assertTrue(so.e_orientador_atual(self.orientador, self.tcc))
        self.assertTrue(so.e_coorientador_ativo(self.coorientador, self.tcc))
        self.assertEqual(so.orientador_atual(self.tcc).pk, self.orientador.pk)
        self.assertEqual(len(so.coorientadores_ativos(self.tcc)), 1)

    def test_sem_vinculo_conjunto_vazio(self):
        outro = criar_docente_ativo()
        self.assertEqual(so.papeis_no_tcc(outro, self.tcc), set())
        self.assertFalse(so.e_orientador_atual(outro, self.tcc))
        self.assertIsNone(so.orientador_atual(self.tcc))

    def test_orientador_automatico_tem_dois_papeis(self):
        """TCC 2 de EC: o Professor da Disciplina é também o Orientador (R10; US-18 G)."""
        turma2 = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        aluno2 = matricular_aluno(turma2, status_tcc=StatusTCC.EM_ANDAMENTO)
        tcc2 = tcc_de(aluno2, turma2)
        vincular_orientador(tcc2, self.professor, origem=OrigemOrientacao.AUTOMATICO)
        self.assertEqual(so.papeis_no_tcc(self.professor, tcc2), {"professor", "orientador"})
        self.assertTrue(so.e_orientador_atual(self.professor, tcc2))

    def test_ex_orientador_sem_papel(self):
        """Q10: depois da troca, o ex-orientador perde o vínculo e o acesso."""
        orientacao = vincular_orientador(self.tcc, self.orientador)
        orientacao.ori_status = StatusOrientacao.ENCERRADA
        orientacao.ori_data_fim = timezone.now()
        orientacao.save()
        self.assertEqual(so.papeis_no_tcc(self.orientador, self.tcc), set())

    def test_convite_pendente_nao_da_papel(self):
        """US-19 #16: o convite 'Aguardando Aceite' não conta como coorientação."""
        criar_convite(self.tcc, self.coorientador)
        self.assertEqual(so.papeis_no_tcc(self.coorientador, self.tcc), set())

    def test_coorientador_externo_nao_e_usuario(self):
        vincular_coorientador(self.tcc, externo=criar_externo())
        self.assertEqual(len(so.coorientadores_ativos(self.tcc)), 1)

    def test_pode_alterar_no_tcc(self):
        self.assertTrue(so.pode_alterar_no_tcc(self.tcc))
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save()
        self.tcc.refresh_from_db()
        self.assertFalse(so.pode_alterar_no_tcc(self.tcc))

    def test_participacao_encerrada_nao_altera(self):
        self.tcc.tcc_status = StatusTCC.DESISTENTE
        self.tcc.save()
        self.assertFalse(so.pode_alterar_no_tcc(self.tcc))

    def test_link_da_solicitacao(self):
        pedido = criar_pedido(self.tcc, self.orientador)
        troca = criar_pedido(
            criar_tcc_extra(self), self.orientador, TipoSolicitacao.TROCA_DE_ORIENTACAO
        )
        convite = criar_convite(self.tcc, self.coorientador)
        self.assertEqual(
            so.link_da_solicitacao(pedido), reverse("cadastro:pedido_orientacao", args=[pedido.pk])
        )
        self.assertEqual(
            so.link_da_solicitacao(troca), reverse("cadastro:pedido_orientacao", args=[troca.pk])
        )
        self.assertEqual(
            so.link_da_solicitacao(convite),
            reverse("cadastro:convite_coorientacao", args=[convite.pk]),
        )


def criar_tcc_extra(teste):
    """Outro aluno e TCC na mesma turma (um pedido pendente por TCC)."""
    aluno = matricular_aluno(teste.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
    return tcc_de(aluno, teste.turma)


class TccCopiadoTest(TesteTurmas):
    """Q6: TCC 1 aprovado e copiado para o TCC 2 fica só para consulta. [FR-007][FR-051]"""

    def setUp(self):
        super().setUp()
        professor = criar_docente_ativo()
        self.turma1 = criar_turma_de(professor)
        self.aluno = matricular_aluno(self.turma1, status_tcc=StatusTCC.APROVADO_PARA_TCC_2)
        self.tcc1 = tcc_de(self.aluno, self.turma1)
        self.turma2 = criar_turma_de(criar_docente_ativo(), descricao=DescricaoTurma.TCC_2)
        self.tcc2 = TCCs.objects.create(
            tcc_alu=self.aluno,
            tcc_tur=self.turma2,
            tcc_status=StatusTCC.EM_ANDAMENTO,
            tcc_titulo="Título",
            tcc_resumo="Resumo",
            tcc_modalidade="Monografia",
        )
        HistoricoStatusTCC.objects.create(
            hst_tcc=self.tcc2,
            hst_tur=self.turma2,
            hst_status_anterior=StatusTCC.APROVADO_PARA_TCC_2,
            hst_status_novo=StatusTCC.EM_ANDAMENTO,
            hst_gatilho=GatilhoStatusTCC.TRANSFERENCIA_PARA_TCC_2,
            hst_data_hora=timezone.now(),
            hst_usu=professor,
        )

    def test_tcc1_copiado_e_tcc2_nao(self):
        self.assertTrue(so.tcc_copiado(self.tcc1))
        self.assertFalse(so.tcc_copiado(self.tcc2))
        self.assertFalse(so.pode_alterar_no_tcc(self.tcc1))
        self.assertTrue(so.pode_alterar_no_tcc(self.tcc2))

    def test_tcc_de_origem(self):
        self.assertEqual(so.tcc_de_origem(self.tcc2), self.tcc1)
        self.assertIsNone(so.tcc_de_origem(self.tcc1))

    def test_aprovado_sem_copia_nao_esta_copiado(self):
        HistoricoStatusTCC.objects.filter(hst_tcc=self.tcc2).delete()
        self.tcc2.delete()
        self.assertFalse(so.tcc_copiado(self.tcc1))
