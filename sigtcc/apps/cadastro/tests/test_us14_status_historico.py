"""Testes da US-14 (Status, histórico e trilha do TCC) — spec 005.

T007 (Foundational): só `services_tcc.pode_ver_resumo` (FR-007a, research C3) e
`services_tcc.historico_do_status` (FR-009, FR-010, research C9), sem nenhuma view ainda.

T014/T016 (Phase 4): os 11 cenários de aceite da User Story 2 do spec.md, disparando cada gatilho
diretamente (research C2; "Independent Test" da US-14 — sem depender da interface das outras US),
mais a consulta pelo Aluno e pelo Professor (via view, com checagem de perfil), pelo Orientador
(via `historico_do_status` direto, simulando a futura spec 006), os cenários de exceção (sem
edição manual; Docente sem vínculo; Secretaria do curso, Clarifications) e as trilhas do
`trilha_do_status` (TCC 1, TCC 2 nas duas variações de aprovação, trilha encerrada).

[US-14][RBN-CAD-08.3][RBN-CAD-08.7][RBN-CAD-08.8][FR-007a][FR-008 a FR-012][research C2]
[research C3][research C9]
"""

from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import services_tcc, services_turmas
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    GatilhoStatusTCC,
    ModalidadeTCC,
    OrigemOrientacao,
    StatusConta,
    StatusCoorientacao,
    StatusOrientacao,
    StatusSolicitacao,
    StatusTCC,
    TipoSolicitacao,
)
from sigtcc.apps.cadastro.models import Coorientacoes, Orientacoes, SolicitacoesOrientacao
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo, criar_secretaria
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    SI,
    TesteTurmas,
    criar_aluno_novo,
    criar_turma_de,
    curso,
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


# =================================================================================================
# Cenários de aceite da User Story 2 (spec.md), disparando cada gatilho diretamente — "Independent
# Test" da US-14: sem depender da interface das outras US (matrícula, transferência, encerramento
# já têm views próprias nas specs 003/004; aqui testamos o resultado da gravação do Status e do
# histórico pelo serviço único, research C2).
# =================================================================================================


class Cenario1VinculoATurmaTest(TesteTurmas):
    """Cenário 1: vincular o aluno nasce o TCC "Sem Proposta", com o histórico registrando o
    status anterior vazio, o gatilho "Vínculo à turma" e o Professor como responsável.

    [US-14][RBN-CAD-08.3][RBN-CAD-08.7][FR-008][FR-009]
    """

    def test_tcc_nasce_sem_proposta_com_professor_responsavel(self):
        professor = criar_docente_ativo()
        turma = criar_turma_de(professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        aluno = criar_aluno_novo()
        tcc = services_turmas.criar_tcc_com_historico(
            aluno, turma, professor, StatusTCC.SEM_PROPOSTA, GatilhoStatusTCC.VINCULO_A_TURMA
        )
        self.assertEqual(tcc.tcc_status, StatusTCC.SEM_PROPOSTA)
        linha = services_tcc.historico_do_status(tcc).get()
        self.assertIsNone(linha.hst_status_anterior)
        self.assertEqual(linha.hst_status_novo, StatusTCC.SEM_PROPOSTA)
        self.assertEqual(linha.hst_gatilho, GatilhoStatusTCC.VINCULO_A_TURMA)
        self.assertEqual(linha.hst_usu_id, professor.pk)


class Cenario2PropostaSalvaTest(TesteTurmas):
    """Cenário 2: TCC "Sem Proposta" + Proposta salva → "Em Andamento", histórico com o gatilho
    "Proposta salva" e o Aluno como responsável.

    [US-14][RBN-CAD-08.3][RBN-CAD-08.7][FR-008][FR-009]
    """

    def test_status_passa_a_em_andamento_com_aluno_responsavel(self):
        professor = criar_docente_ativo()
        turma = criar_turma_de(professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.SEM_PROPOSTA)
        tcc = tcc_de(aluno, turma)
        # A Proposta (Título, Resumo, Modalidade) é gravada antes da mudança de Status, como faz
        # services_tcc.salvar_proposta — a CHECK ck_tccs_campos_obrigatorios_com_proposta exige
        # esses campos fora de "Sem Proposta".
        tcc.tcc_titulo = "Sistema de Gestão de TCC"
        tcc.tcc_resumo = "Resumo do trabalho."
        tcc.tcc_modalidade = ModalidadeTCC.MONOGRAFIA
        tcc.save(update_fields=["tcc_titulo", "tcc_resumo", "tcc_modalidade"])
        services_turmas.atualizar_status_tcc(
            tcc, turma, aluno.alu, StatusTCC.EM_ANDAMENTO, GatilhoStatusTCC.PROPOSTA_SALVA
        )
        tcc.refresh_from_db()
        self.assertEqual(tcc.tcc_status, StatusTCC.EM_ANDAMENTO)
        linha = services_tcc.historico_do_status(tcc).last()
        self.assertEqual(linha.hst_gatilho, GatilhoStatusTCC.PROPOSTA_SALVA)
        self.assertEqual(linha.hst_usu_id, aluno.alu_id)


class Cenario3TransferenciaParaTCC2Test(TesteTurmas):
    """Cenário 3: aluno "Aprovado para TCC 2" vinculado à turma de TCC 2 → volta a "Em Andamento"
    com o gatilho "Transferência para TCC 2", preservando o histórico anterior do TCC 1.

    [US-14][RBN-CAD-08.3][RBN-CAD-08.7][RBN-CAD-08.6][FR-008][FR-009][FR-011]
    """

    def test_retorna_a_em_andamento_preservando_historico_do_tcc1(self):
        professor = criar_docente_ativo()
        turma1 = criar_turma_de(professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        turma2 = criar_turma_de(professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        aluno = matricular_aluno(turma1, status_tcc=StatusTCC.APROVADO_PARA_TCC_2)
        tcc1 = tcc_de(aluno, turma1)
        historico_tcc1_antes = list(services_tcc.historico_do_status(tcc1))

        tcc2 = services_turmas.criar_tcc_com_historico(
            aluno,
            turma2,
            professor,
            StatusTCC.EM_ANDAMENTO,
            GatilhoStatusTCC.TRANSFERENCIA_PARA_TCC_2,
            anterior=tcc1.tcc_status,
            tcc_titulo=tcc1.tcc_titulo,
            tcc_resumo=tcc1.tcc_resumo,
            tcc_modalidade=tcc1.tcc_modalidade,
        )

        self.assertEqual(tcc2.tcc_status, StatusTCC.EM_ANDAMENTO)
        linha = services_tcc.historico_do_status(tcc2).get()
        self.assertEqual(linha.hst_status_anterior, StatusTCC.APROVADO_PARA_TCC_2)
        self.assertEqual(linha.hst_gatilho, GatilhoStatusTCC.TRANSFERENCIA_PARA_TCC_2)
        # O histórico do TCC 1 continua intacto, sem nenhuma linha nova (FR-011).
        self.assertEqual(list(services_tcc.historico_do_status(tcc1)), historico_tcc1_antes)


class Cenario4EncerramentoDaParticipacaoTest(TesteTurmas):
    """Cenário 4: o Professor da Disciplina registra desistência, reprovação ou jubilamento com
    justificativa → o Status passa ao valor escolhido, com o Professor como responsável e o
    gatilho "Encerramento da participação" (2 variações: Desistente e Jubilado/Reprovado).

    [US-14][RBN-CAD-08.3][RBN-CAD-08.4][RBN-CAD-08.7][FR-008][FR-009]
    """

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)

    def test_desistente_com_professor_responsavel(self):
        aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        tcc = services_turmas.encerrar_participacao(
            self.professor, self.turma.pk, aluno.pk, StatusTCC.DESISTENTE, "Motivos pessoais."
        )
        self.assertEqual(tcc.tcc_status, StatusTCC.DESISTENTE)
        linha = services_tcc.historico_do_status(tcc).last()
        self.assertEqual(linha.hst_gatilho, GatilhoStatusTCC.ENCERRAMENTO_DA_PARTICIPACAO)
        self.assertEqual(linha.hst_usu_id, self.professor.pk)

    def test_jubilado_e_reprovado_com_professor_responsavel(self):
        for status in (StatusTCC.JUBILADO, StatusTCC.REPROVADO):
            with self.subTest(status=status):
                aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.APTO_PARA_DEFESA)
                tcc = services_turmas.encerrar_participacao(
                    self.professor, self.turma.pk, aluno.pk, status, "Justificativa do professor."
                )
                self.assertEqual(tcc.tcc_status, status)
                linha = services_tcc.historico_do_status(tcc).last()
                self.assertEqual(linha.hst_gatilho, GatilhoStatusTCC.ENCERRAMENTO_DA_PARTICIPACAO)
                self.assertEqual(linha.hst_usu_id, self.professor.pk)


class Cenario7SemEdicaoManualTest(TesteTurmas):
    """Cenário 7: o Status aparece só como etiqueta somente leitura — não há campo nem botão de
    edição direta em nenhuma tela desta spec.

    [US-14][RBN-CAD-08.3][FR-008]
    """

    def test_tela_meu_tcc_nao_tem_campo_de_status(self):
        professor = criar_docente_ativo()
        turma = criar_turma_de(professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        aluno = matricular_aluno(
            turma, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        )
        self.client.force_login(aluno.alu)
        resposta = self.client.get(reverse("cadastro:meu_tcc", args=[turma.pk]))
        self.assertNotContains(resposta, 'name="tcc_status"')
        self.assertNotContains(resposta, 'name="status"')

    def test_tela_de_historico_nao_tem_formulario_de_edicao_do_status(self):
        """A tela não tem nenhum campo ou botão para editar o Status (FR-008); o único `<form>`
        da página é o "Sair" do cabeçalho comum (base.html), sem relação com o TCC."""
        professor = criar_docente_ativo()
        turma = criar_turma_de(professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        aluno = matricular_aluno(
            turma, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        )
        self.client.force_login(aluno.alu)
        resposta = self.client.get(reverse("cadastro:historico_status_aluno", args=[turma.pk]))
        self.assertNotContains(resposta, 'name="tcc_status"')
        self.assertNotContains(resposta, 'name="status"')
        self.assertNotContains(resposta, "Salvar Status")


class Cenario8IndicacaoDeAptoTest(TesteTurmas):
    """Cenário 8: o Orientador aciona "Apto para Defesa" (gatilho disparado pela spec 006,
    US-42); essa ação chama `atualizar_status_tcc` (FR-012), o Status passa a "Apto para Defesa"
    e o histórico registra o Orientador como responsável e o gatilho "Indicação de Apto para
    Defesa".

    [US-14][RBN-CAD-08.3][RBN-CAD-08.7][FR-008][FR-009][FR-012]
    """

    def test_apto_para_defesa_com_orientador_responsavel(self):
        professor = criar_docente_ativo()
        orientador = criar_docente_ativo()
        turma = criar_turma_de(professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        tcc = tcc_de(aluno, turma)
        services_turmas.atualizar_status_tcc(
            tcc, turma, orientador, StatusTCC.APTO_PARA_DEFESA, GatilhoStatusTCC.INDICACAO_DE_APTO
        )
        tcc.refresh_from_db()
        self.assertEqual(tcc.tcc_status, StatusTCC.APTO_PARA_DEFESA)
        linha = services_tcc.historico_do_status(tcc).last()
        self.assertEqual(linha.hst_gatilho, GatilhoStatusTCC.INDICACAO_DE_APTO)
        self.assertEqual(linha.hst_usu_id, orientador.pk)


class Cenario9LiberacaoDoResultadoTCC1Test(TesteTurmas):
    """Cenário 9: TCC 1 "Apto para Defesa" + a banca libera o resultado com nota final 6,0 ou
    mais (gatilho disparado pela spec 006, US-27) → "Aprovado para TCC 2", com o gatilho
    "Liberação do resultado" registrado no histórico.

    [US-14][RBN-CAD-08.3][RBN-CAD-08.7][FR-008][FR-009][FR-012]
    """

    def test_aprovado_para_tcc2(self):
        professor = criar_docente_ativo()
        turma = criar_turma_de(professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.APTO_PARA_DEFESA)
        tcc = tcc_de(aluno, turma)
        services_turmas.atualizar_status_tcc(
            tcc,
            turma,
            professor,
            StatusTCC.APROVADO_PARA_TCC_2,
            GatilhoStatusTCC.LIBERACAO_DO_RESULTADO,
        )
        tcc.refresh_from_db()
        self.assertEqual(tcc.tcc_status, StatusTCC.APROVADO_PARA_TCC_2)
        linha = services_tcc.historico_do_status(tcc).last()
        self.assertEqual(linha.hst_gatilho, GatilhoStatusTCC.LIBERACAO_DO_RESULTADO)


class Cenario10LiberacaoDoResultadoTCC2Test(TesteTurmas):
    """Cenário 10: TCC 2 "Apto para Defesa" + a banca libera o resultado com parecer "Aprovado",
    "Aprovado com Correções" ou nota final menor que 6,0 → "Aprovado", "Aprovado com Correções"
    ou "Reprovado", respectivamente, com o gatilho "Liberação do resultado" (3 variações).

    [US-14][RBN-CAD-08.3][RBN-CAD-08.7][FR-008][FR-009][FR-012]
    """

    def test_aprovado_aprovado_com_correcoes_ou_reprovado(self):
        professor = criar_docente_ativo()
        turma = criar_turma_de(professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        for status in (
            StatusTCC.APROVADO,
            StatusTCC.APROVADO_COM_CORRECOES,
            StatusTCC.REPROVADO,
        ):
            with self.subTest(status=status):
                aluno = matricular_aluno(turma, status_tcc=StatusTCC.APTO_PARA_DEFESA)
                tcc = tcc_de(aluno, turma)
                services_turmas.atualizar_status_tcc(
                    tcc, turma, professor, status, GatilhoStatusTCC.LIBERACAO_DO_RESULTADO
                )
                tcc.refresh_from_db()
                self.assertEqual(tcc.tcc_status, status)
                linha = services_tcc.historico_do_status(tcc).last()
                self.assertEqual(linha.hst_gatilho, GatilhoStatusTCC.LIBERACAO_DO_RESULTADO)


class ConcluidoNaHomologacaoTest(TesteTurmas):
    """Complemento (FR-008): o gatilho "Homologação da Versão Final" (US-44, fase futura desta
    mesma spec) leva o TCC 2 "Aprovado" ou "Aprovado com Correções" a "Concluído", pelo mesmo
    serviço único (FR-012).

    [US-14][RBN-CAD-08.3][RBN-CAD-08.7][FR-008][FR-009][FR-012]
    """

    def test_concluido_a_partir_de_aprovado_ou_aprovado_com_correcoes(self):
        professor = criar_docente_ativo()
        turma = criar_turma_de(professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        for origem in (StatusTCC.APROVADO, StatusTCC.APROVADO_COM_CORRECOES):
            with self.subTest(origem=origem):
                aluno = matricular_aluno(turma, status_tcc=origem)
                tcc = tcc_de(aluno, turma)
                services_turmas.atualizar_status_tcc(
                    tcc,
                    turma,
                    professor,
                    StatusTCC.CONCLUIDO,
                    GatilhoStatusTCC.HOMOLOGACAO_DA_VERSAO_FINAL,
                )
                tcc.refresh_from_db()
                self.assertEqual(tcc.tcc_status, StatusTCC.CONCLUIDO)
                linha = services_tcc.historico_do_status(tcc).last()
                self.assertEqual(linha.hst_gatilho, GatilhoStatusTCC.HOMOLOGACAO_DA_VERSAO_FINAL)


class Cenario11GatilhoForaDaTabelaTest(TesteTurmas):
    """Cenário 11: um gatilho de outra spec (006) chama o serviço de gravação desta spec com um
    valor de Status fora da tabela fixa de gatilhos (FR-008) → a chamada é rejeitada, sem gravar
    nenhuma linha no histórico.

    [US-14][RBN-CAD-08.3][FR-008][FR-011]
    """

    def test_transicao_fora_da_tabela_nao_grava_nada(self):
        professor = criar_docente_ativo()
        turma = criar_turma_de(professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.SEM_PROPOSTA)
        tcc = tcc_de(aluno, turma)
        with self.assertRaises(ValueError):
            services_turmas.atualizar_status_tcc(
                tcc,
                turma,
                professor,
                StatusTCC.CONCLUIDO,
                GatilhoStatusTCC.PROPOSTA_SALVA,
            )
        tcc.refresh_from_db()
        self.assertEqual(tcc.tcc_status, StatusTCC.SEM_PROPOSTA)
        self.assertEqual(services_tcc.historico_do_status(tcc).count(), 1)


# =================================================================================================
# Cenário 5: consulta pelo link "Histórico do Status do TCC" — Aluno, Orientador (direto,
# simulando a spec 006) e Professor da Disciplina; Docente sem vínculo e Secretaria não veem
# (Clarifications, sessão 2026-10-22).
# =================================================================================================


class HistoricoStatusAlunoViewTest(TesteTurmas):
    """O próprio Aluno consulta o histórico e a trilha pela view `historico_status_aluno`.

    [US-14][FR-009][FR-010][contracts/rotas.md]
    """

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        self.aluno = matricular_aluno(
            self.turma, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        )
        self.tcc = tcc_de(self.aluno, self.turma)

    def url(self):
        return reverse("cadastro:historico_status_aluno", args=[self.turma.pk])

    def test_aluno_dono_ve_o_historico_e_a_trilha(self):
        self.client.force_login(self.aluno.alu)
        resposta = self.client.get(self.url())
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            list(resposta.context["historico"]), list(services_tcc.historico_do_status(self.tcc))
        )
        self.assertEqual(resposta.context["trilha"], services_tcc.trilha_do_status(self.tcc))

    def test_link_aparece_na_tela_meu_tcc(self):
        self.client.force_login(self.aluno.alu)
        resposta = self.client.get(reverse("cadastro:meu_tcc", args=[self.turma.pk]))
        self.assertContains(resposta, self.url())
        self.assertContains(resposta, "Histórico do Status do TCC")

    def test_outro_aluno_sem_vinculo_na_turma_recebe_404(self):
        outro = matricular_aluno(
            criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC),
            status_conta=StatusConta.ATIVA,
        )
        self.client.force_login(outro.alu)
        resposta = self.client.get(self.url())
        self.assertEqual(resposta.status_code, 404)


class HistoricoStatusProfessorViewTest(TesteTurmas):
    """O Professor da Disciplina consulta o histórico de um aluno da turma pela view
    `historico_status`; um Docente sem vínculo e a Secretaria do curso não veem (Clarifications).

    [US-14][FR-009][FR-010][contracts/rotas.md]
    """

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        self.aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        self.tcc = tcc_de(self.aluno, self.turma)

    def url(self):
        return reverse("cadastro:historico_status", args=[self.turma.pk, self.aluno.pk])

    def test_professor_da_disciplina_ve_o_historico_e_a_trilha(self):
        self.client.force_login(self.professor)
        resposta = self.client.get(self.url())
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            list(resposta.context["historico"]), list(services_tcc.historico_do_status(self.tcc))
        )
        self.assertEqual(resposta.context["trilha"], services_tcc.trilha_do_status(self.tcc))

    def test_docente_sem_vinculo_recebe_403(self):
        outro_docente = criar_docente_ativo()
        self.client.force_login(outro_docente)
        resposta = self.client.get(self.url())
        self.assertEqual(resposta.status_code, 403)

    def test_secretaria_do_curso_recebe_403(self):
        """A Secretaria consulta turmas (spec 004, Q9), mas não este histórico (Clarifications,
        sessão 2026-10-22, FR-009)."""
        secretaria = criar_secretaria(curso=curso(EC))
        self.client.force_login(secretaria)
        resposta = self.client.get(self.url())
        self.assertEqual(resposta.status_code, 403)

    def test_secretaria_de_outro_curso_recebe_403(self):
        secretaria = criar_secretaria(curso=curso(SI))
        self.client.force_login(secretaria)
        resposta = self.client.get(self.url())
        self.assertEqual(resposta.status_code, 403)

    def test_aluno_fora_da_turma_recebe_404(self):
        self.client.force_login(self.professor)
        resposta = self.client.get(reverse("cadastro:historico_status", args=[self.turma.pk, 0]))
        self.assertEqual(resposta.status_code, 404)

    def test_turma_inexistente_recebe_404(self):
        self.client.force_login(self.professor)
        resposta = self.client.get(reverse("cadastro:historico_status", args=[0, self.aluno.pk]))
        self.assertEqual(resposta.status_code, 404)


class ConsultaPeloOrientadorTest(TesteTurmas):
    """O Orientador consulta o histórico chamando `historico_do_status` direto, sem passar pela
    view desta spec — é assim que a futura spec 006 (tela de orientandos) vai reaproveitar a
    consulta, aplicando a própria checagem de Orientador por fora (research C9).

    [US-14][FR-009][research C9]
    """

    def test_orientador_ativo_obtem_o_historico_completo(self):
        professor = criar_docente_ativo()
        orientador = criar_docente_ativo()
        turma = criar_turma_de(professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.SEM_PROPOSTA)
        tcc = tcc_de(aluno, turma)
        Orientacoes.objects.create(
            ori_tcc=tcc,
            ori_doc=orientador.docentes,
            ori_origem=OrigemOrientacao.PEDIDO_ACEITO,
            ori_status=StatusOrientacao.ATIVA,
            ori_data_inicio=timezone.now(),
        )
        tcc.tcc_titulo = "Sistema de Gestão de TCC"
        tcc.tcc_resumo = "Resumo do trabalho."
        tcc.tcc_modalidade = ModalidadeTCC.MONOGRAFIA
        tcc.save(update_fields=["tcc_titulo", "tcc_resumo", "tcc_modalidade"])
        services_turmas.atualizar_status_tcc(
            tcc, turma, aluno.alu, StatusTCC.EM_ANDAMENTO, GatilhoStatusTCC.PROPOSTA_SALVA
        )
        # O Orientador (confirmado por pode_ver_resumo, FR-007a) chama a função direto.
        self.assertTrue(services_tcc.pode_ver_resumo(orientador, tcc))
        historico = services_tcc.historico_do_status(tcc)
        self.assertEqual(historico.count(), 2)
        self.assertEqual(historico.last().hst_gatilho, GatilhoStatusTCC.PROPOSTA_SALVA)


# =================================================================================================
# Trilha do Status (T016, FR-010): TCC 1, as duas variações de TCC 2 e a trilha encerrada
# (cenário 6 da User Story 2).
# =================================================================================================


class TrilhaDoStatusTest(TesteTurmas):
    """`trilha_do_status`: sequência fixa com a etapa atual destacada, por tipo de turma, e o
    corte da trilha em Reprovado/Desistente/Jubilado (cenário 6).

    [US-14][RBN-CAD-08.8][FR-010]
    """

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()

    def test_trilha_tcc1_destaca_a_etapa_atual(self):
        turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.APTO_PARA_DEFESA)
        tcc = tcc_de(aluno, turma)
        self.assertEqual(
            services_tcc.trilha_do_status(tcc),
            [
                {"status": StatusTCC.EM_ANDAMENTO, "atual": False},
                {"status": StatusTCC.APTO_PARA_DEFESA, "atual": True},
                {"status": StatusTCC.APROVADO_PARA_TCC_2, "atual": False},
            ],
        )

    def test_trilha_tcc2_com_aprovado(self):
        turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.APROVADO)
        tcc = tcc_de(aluno, turma)
        self.assertEqual(
            services_tcc.trilha_do_status(tcc),
            [
                {"status": StatusTCC.EM_ANDAMENTO, "atual": False},
                {"status": StatusTCC.APTO_PARA_DEFESA, "atual": False},
                {"status": StatusTCC.APROVADO, "atual": True},
                {"status": StatusTCC.CONCLUIDO, "atual": False},
            ],
        )

    def test_trilha_tcc2_com_aprovado_com_correcoes(self):
        turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.APTO_PARA_DEFESA)
        tcc = tcc_de(aluno, turma)
        services_turmas.atualizar_status_tcc(
            tcc,
            turma,
            self.professor,
            StatusTCC.APROVADO_COM_CORRECOES,
            GatilhoStatusTCC.LIBERACAO_DO_RESULTADO,
        )
        tcc.refresh_from_db()
        self.assertEqual(
            services_tcc.trilha_do_status(tcc),
            [
                {"status": StatusTCC.EM_ANDAMENTO, "atual": False},
                {"status": StatusTCC.APTO_PARA_DEFESA, "atual": False},
                {"status": StatusTCC.APROVADO_COM_CORRECOES, "atual": True},
                {"status": StatusTCC.CONCLUIDO, "atual": False},
            ],
        )

    def test_trilha_tcc2_concluido_mantem_a_etapa_de_aprovado_com_correcoes(self):
        """Depois de Concluído, a trilha mostra a etapa de aprovação que de fato ocorreu (olhando
        o histórico), não sempre "Aprovado" por padrão."""
        turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.APTO_PARA_DEFESA)
        tcc = tcc_de(aluno, turma)
        services_turmas.atualizar_status_tcc(
            tcc,
            turma,
            self.professor,
            StatusTCC.APROVADO_COM_CORRECOES,
            GatilhoStatusTCC.LIBERACAO_DO_RESULTADO,
        )
        tcc.refresh_from_db()
        services_turmas.atualizar_status_tcc(
            tcc,
            turma,
            self.professor,
            StatusTCC.CONCLUIDO,
            GatilhoStatusTCC.HOMOLOGACAO_DA_VERSAO_FINAL,
        )
        tcc.refresh_from_db()
        self.assertEqual(
            services_tcc.trilha_do_status(tcc),
            [
                {"status": StatusTCC.EM_ANDAMENTO, "atual": False},
                {"status": StatusTCC.APTO_PARA_DEFESA, "atual": False},
                {"status": StatusTCC.APROVADO_COM_CORRECOES, "atual": False},
                {"status": StatusTCC.CONCLUIDO, "atual": True},
            ],
        )

    def test_trilha_encerrada_em_desistente_termina_na_etapa_em_que_ocorreu(self):
        turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        tcc = services_turmas.encerrar_participacao(
            self.professor, turma.pk, aluno.pk, StatusTCC.DESISTENTE, "Motivos pessoais."
        )
        self.assertEqual(
            services_tcc.trilha_do_status(tcc),
            [
                {"status": StatusTCC.EM_ANDAMENTO, "atual": False},
                {"status": StatusTCC.DESISTENTE, "atual": True},
            ],
        )

    def test_trilha_encerrada_em_jubilado_depois_de_apto_para_defesa(self):
        turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.APTO_PARA_DEFESA)
        tcc = services_turmas.encerrar_participacao(
            self.professor, turma.pk, aluno.pk, StatusTCC.JUBILADO, "Jubilamento."
        )
        self.assertEqual(
            services_tcc.trilha_do_status(tcc),
            [
                {"status": StatusTCC.EM_ANDAMENTO, "atual": False},
                {"status": StatusTCC.APTO_PARA_DEFESA, "atual": False},
                {"status": StatusTCC.JUBILADO, "atual": True},
            ],
        )

    def test_trilha_encerrada_em_reprovado_no_tcc2(self):
        turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.APTO_PARA_DEFESA)
        tcc = tcc_de(aluno, turma)
        services_turmas.atualizar_status_tcc(
            tcc, turma, self.professor, StatusTCC.REPROVADO, GatilhoStatusTCC.LIBERACAO_DO_RESULTADO
        )
        tcc.refresh_from_db()
        self.assertEqual(
            services_tcc.trilha_do_status(tcc),
            [
                {"status": StatusTCC.EM_ANDAMENTO, "atual": False},
                {"status": StatusTCC.APTO_PARA_DEFESA, "atual": False},
                {"status": StatusTCC.REPROVADO, "atual": True},
            ],
        )
