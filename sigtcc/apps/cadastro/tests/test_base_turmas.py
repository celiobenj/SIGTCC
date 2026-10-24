"""Parte comum da feature 004: permissão por turma, turma arquivada, vínculo do aluno, turma que já
teve aluno, orientador automático, participação encerrada e entregas do aluno.

[US-07][US-08][US-09][FR-008][FR-009][FR-025][Q9][Q15][Q17][Q18][research B2][B5][B22]
"""

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404
from django.utils import timezone

from sigtcc.apps.cadastro import services, services_turmas
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    GatilhoStatusTCC,
    ModalidadeTCC,
    StatusEntrega,
    StatusTCC,
    StatusTurma,
    TipoEventoTurma,
)
from sigtcc.apps.cadastro.models import (
    AreasInteresse,
    EntregasMarcos,
    HistoricoAlunosTurmas,
    HistoricoStatusTCC,
    TCCs,
    Turmas,
)
from sigtcc.apps.cadastro.permissoes import (
    pode_alterar_turma,
    pode_consultar_turma,
    pode_transferir,
)
from sigtcc.apps.cadastro.services_turmas import ALTERAR, CONSULTAR, TRANSFERIR, TurmaArquivada
from sigtcc.apps.cadastro.tests.apoio_acesso import (
    criar_coordenador,
    criar_docente_ativo,
    criar_secretaria,
)
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    LC,
    SI,
    TesteTurmas,
    criar_aluno_novo,
    criar_entrega,
    criar_envio,
    criar_turma_de,
    curso,
    entrega_do_aluno,
    matricular_aluno,
    tcc_de,
)


class PermissaoPorTurmaTest(TesteTurmas):
    """turma_para: 404 → 403 → MT-25; Secretaria só do curso (Q9). [FR-009][B2]"""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=EC)

    def test_professor_consulta_e_altera(self):
        self.assertEqual(
            services_turmas.turma_para(self.professor, self.turma.pk, ALTERAR), self.turma
        )
        self.assertTrue(pode_alterar_turma(self.professor, self.turma))

    def test_secretaria_do_curso_consulta_e_transfere_mas_nao_altera(self):
        secretaria = criar_secretaria(curso=curso(EC))
        self.assertTrue(pode_consultar_turma(secretaria, self.turma))
        self.assertTrue(pode_transferir(secretaria, self.turma))
        self.assertFalse(pode_alterar_turma(secretaria, self.turma))
        with self.assertRaises(PermissionDenied):
            services_turmas.turma_para(secretaria, self.turma.pk, ALTERAR)

    def test_secretaria_de_outro_curso_e_outros_docentes_recebem_403(self):
        for usuario in (
            criar_secretaria(curso=curso(SI)),
            criar_docente_ativo(),
            criar_coordenador(),
        ):
            with self.subTest(usuario=usuario.pk):
                with self.assertRaises(PermissionDenied):
                    services_turmas.turma_para(usuario, self.turma.pk, CONSULTAR)

    def test_turma_inexistente_404(self):
        with self.assertRaises(Http404):
            services_turmas.turma_para(self.professor, 999999, CONSULTAR)

    def test_ordem_403_antes_de_turma_arquivada(self):
        """Quem não tem permissão não descobre que a turma está arquivada."""
        Turmas.objects.filter(pk=self.turma.pk).update(tur_status=StatusTurma.ARQUIVADA)
        with self.assertRaises(PermissionDenied):
            services_turmas.turma_para(criar_docente_ativo(), self.turma.pk, ALTERAR)
        with self.assertRaises(TurmaArquivada):
            services_turmas.turma_para(self.professor, self.turma.pk, ALTERAR)
        with self.assertRaises(TurmaArquivada):
            services_turmas.turma_para(self.professor, self.turma.pk, TRANSFERIR)
        self.assertEqual(
            services_turmas.turma_para(self.professor, self.turma.pk, CONSULTAR), self.turma
        )

    def test_travar_turma_ativa(self):
        with transaction.atomic():
            self.assertEqual(services_turmas.travar_turma_ativa(self.turma.pk), self.turma)
        Turmas.objects.filter(pk=self.turma.pk).update(tur_status=StatusTurma.ARQUIVADA)
        with self.assertRaises(TurmaArquivada), transaction.atomic():
            services_turmas.travar_turma_ativa(self.turma.pk)
        self.assertTrue(services_turmas.turma_arquivada(Turmas.objects.get(pk=self.turma.pk)))

    def test_vinculo_na_turma(self):
        aluno = matricular_aluno(self.turma)
        outro = matricular_aluno(criar_turma_de(criar_docente_ativo()))
        self.assertEqual(services_turmas.vinculo_na_turma(self.turma, aluno.pk), aluno)
        with self.assertRaises(Http404):
            services_turmas.vinculo_na_turma(self.turma, outro.pk)


class RegrasDaTurmaTest(TesteTurmas):
    """turma_ja_teve_aluno (Q12, Q15), orientador automático (B8), participação encerrada."""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()

    def test_turma_ja_teve_aluno(self):
        turma = criar_turma_de(self.professor)
        self.assertFalse(services_turmas.turma_ja_teve_aluno(turma))
        matricular_aluno(turma)
        self.assertTrue(services_turmas.turma_ja_teve_aluno(turma))

    def test_turma_ja_teve_aluno_so_pelo_historico(self):
        turma = criar_turma_de(self.professor)
        HistoricoAlunosTurmas.objects.create(
            hat_alu=criar_aluno_novo(),
            hat_tur_origem=turma,
            hat_tipo_evento=TipoEventoTurma.EXCLUSAO,
            hat_justificativa="Vínculo por engano",
            hat_data_hora=timezone.now(),
            hat_usu=self.professor,
        )
        self.assertTrue(services_turmas.turma_ja_teve_aluno(turma))

    def test_orientador_automatico(self):
        casos = (
            (DescricaoTurma.TCC_2, EC, True),
            (DescricaoTurma.TCC_2, LC, True),
            (DescricaoTurma.TCC_2, SI, False),
            (DescricaoTurma.TCC_1, EC, False),
        )
        for descricao, nome, esperado in casos:
            with self.subTest(descricao=descricao, curso=nome):
                turma = criar_turma_de(self.professor, descricao=descricao, curso_nome=nome)
                self.assertEqual(services_turmas.turma_tem_orientador_automatico(turma), esperado)

    def test_participacao_encerrada(self):
        turma = criar_turma_de(self.professor)
        for status in StatusTCC.values:
            with self.subTest(status=status):
                aluno = matricular_aluno(turma, status_tcc=status)
                esperado = status in ("Desistente", "Reprovado", "Jubilado")
                self.assertEqual(
                    services_turmas.participacao_encerrada(tcc_de(aluno, turma)), esperado
                )


class EntregasDoAlunoTest(TesteTurmas):
    """Registros do aluno nas entregas da turma (Q17, Q18). [B22]"""

    def setUp(self):
        super().setUp()
        self.turma = criar_turma_de(criar_docente_ativo())
        self.entrega1 = criar_entrega(self.turma)
        self.entrega2 = criar_entrega(self.turma)
        self.aluno = criar_aluno_novo()

    def test_cria_registros_das_entregas_existentes(self):
        services_turmas.criar_entregas_do_aluno(self.aluno, self.turma)
        registros = EntregasMarcos.objects.filter(ent_alu=self.aluno)
        self.assertEqual(registros.count(), 2)
        self.assertEqual(
            set(registros.values_list("ent_status", flat=True)), {StatusEntrega.AGUARDANDO_ENVIO}
        )

    def test_q18_reaproveita_registro_antigo_zerando_a_avaliacao(self):
        antigo = entrega_do_aluno(self.entrega1, self.aluno, status=StatusEntrega.HOMOLOGADA)
        EntregasMarcos.objects.filter(pk=antigo.pk).update(
            ent_feedback="Bom", ent_data_avaliacao=timezone.now()
        )
        criar_envio(antigo)
        services_turmas.criar_entregas_do_aluno(self.aluno, self.turma)
        antigo.refresh_from_db()
        self.assertEqual(antigo.ent_status, StatusEntrega.AGUARDANDO_ENVIO)
        self.assertIsNone(antigo.ent_feedback)
        self.assertIsNone(antigo.ent_data_avaliacao)
        self.assertEqual(antigo.historicoenviosentregas_set.count(), 1)
        self.assertEqual(EntregasMarcos.objects.filter(ent_alu=self.aluno).count(), 2)

    def test_q17_remove_so_registros_sem_envio(self):
        sem_envio = entrega_do_aluno(self.entrega1, self.aluno)
        com_envio = entrega_do_aluno(self.entrega2, self.aluno)
        criar_envio(com_envio)
        services_turmas.remover_entregas_sem_envio(self.aluno, self.turma)
        self.assertFalse(EntregasMarcos.objects.filter(pk=sem_envio.pk).exists())
        self.assertTrue(EntregasMarcos.objects.filter(pk=com_envio.pk).exists())

    def test_curso_do_codigo_reexportado(self):
        self.assertIs(services_turmas.curso_do_codigo, services.curso_do_codigo)


class ServicoUnicoDeStatusTest(TesteTurmas):
    """criar_tcc_com_historico e atualizar_status_tcc: serviço único de gravação do Status do TCC
    (FR-008, FR-012, research C2). A transição é validada contra TRANSICOES_VALIDAS; fora da
    tabela (gatilho inexistente ou transição não prevista), levanta ValueError sem gravar nada.
    [US-14][RBN-CAD-08.3][RBN-CAD-08.7][FR-008][FR-012][SC-002][research C2]
    """

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1)
        self.aluno = criar_aluno_novo()

    def test_criar_tcc_com_historico_grava_tcc_e_primeiro_registro(self):
        """Gatilho de criação (Vínculo à turma): cria o TCC já com o Status inicial e o primeiro
        registro do histórico, com status anterior vazio. [US-14][RBN-CAD-08.3][RBN-CAD-08.7]
        """
        tcc = services_turmas.criar_tcc_com_historico(
            self.aluno,
            self.turma,
            self.professor,
            StatusTCC.SEM_PROPOSTA,
            GatilhoStatusTCC.VINCULO_A_TURMA,
        )
        self.assertEqual(tcc.tcc_status, StatusTCC.SEM_PROPOSTA)
        historico = HistoricoStatusTCC.objects.get(hst_tcc=tcc)
        self.assertIsNone(historico.hst_status_anterior)
        self.assertEqual(historico.hst_status_novo, StatusTCC.SEM_PROPOSTA)
        self.assertEqual(historico.hst_gatilho, GatilhoStatusTCC.VINCULO_A_TURMA)
        self.assertEqual(historico.hst_usu_id, self.professor.pk)
        self.assertEqual(historico.hst_tur_id, self.turma.pk)

    def test_criar_tcc_com_historico_aceita_anterior_e_campos_extras(self):
        """Gatilho de criação com linha de origem (Transferência para TCC 2): `anterior` vem de
        fora do objeto (status do TCC de origem) e `**campos_tcc` grava título/resumo/modalidade
        já na criação, exigidos pela CHECK ck_tccs_campos_obrigatorios_com_proposta fora de "Sem
        Proposta" (research C2, decisão de Julia Cohen 2026-10-22).
        [US-14][RBN-CAD-08.3][RBN-CAD-08.7][FR-008][FR-012][research C2]
        """
        area = AreasInteresse.objects.create(ari_nome="Área de interesse copiada")
        tcc = services_turmas.criar_tcc_com_historico(
            self.aluno,
            self.turma,
            self.professor,
            StatusTCC.EM_ANDAMENTO,
            GatilhoStatusTCC.TRANSFERENCIA_PARA_TCC_2,
            anterior=StatusTCC.APROVADO_PARA_TCC_2,
            tcc_titulo="Título copiado",
            tcc_subtitulo="Subtítulo copiado",
            tcc_resumo="Resumo copiado",
            tcc_modalidade=ModalidadeTCC.MONOGRAFIA,
            tcc_link_proposta="https://exemplo.org/proposta",
            tcc_ari=area,
        )
        self.assertEqual(tcc.tcc_status, StatusTCC.EM_ANDAMENTO)
        self.assertEqual(tcc.tcc_titulo, "Título copiado")
        self.assertEqual(tcc.tcc_resumo, "Resumo copiado")
        self.assertEqual(tcc.tcc_modalidade, ModalidadeTCC.MONOGRAFIA)
        historico = HistoricoStatusTCC.objects.get(hst_tcc=tcc)
        self.assertEqual(historico.hst_status_anterior, StatusTCC.APROVADO_PARA_TCC_2)
        self.assertEqual(historico.hst_status_novo, StatusTCC.EM_ANDAMENTO)
        self.assertEqual(historico.hst_gatilho, GatilhoStatusTCC.TRANSFERENCIA_PARA_TCC_2)

    def test_criar_tcc_com_historico_transicao_invalida_nao_grava_nada(self):
        """Transição fora da tabela (ex.: gatilho de criação com Status final errado) levanta
        ValueError sem criar TCC nem histórico. [US-14][FR-008][research C2]
        """
        with self.assertRaises(ValueError):
            services_turmas.criar_tcc_com_historico(
                self.aluno,
                self.turma,
                self.professor,
                StatusTCC.EM_ANDAMENTO,
                GatilhoStatusTCC.VINCULO_A_TURMA,
            )
        self.assertFalse(TCCs.objects.filter(tcc_alu=self.aluno, tcc_tur=self.turma).exists())
        self.assertFalse(HistoricoStatusTCC.objects.filter(hst_tcc__tcc_alu=self.aluno).exists())

    def test_atualizar_status_tcc_transicao_valida_grava_historico(self):
        """Transição válida (Proposta salva: Sem Proposta → Em Andamento) muda tcc_status e grava
        o histórico certo. [US-14][RBN-CAD-08.3][RBN-CAD-08.7][FR-008][FR-012]
        """
        aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.SEM_PROPOSTA)
        tcc = tcc_de(aluno, self.turma)
        # Fora de "Sem Proposta", o CHECK do banco exige título/resumo/modalidade (spec 001); o
        # preenchimento real é feito por services_tcc.salvar_proposta (US-13, fase 3, ainda não
        # implementada); aqui só o suficiente para a transição de Status ser gravável.
        tcc.tcc_titulo = "Título do trabalho"
        tcc.tcc_resumo = "Resumo do trabalho"
        tcc.tcc_modalidade = ModalidadeTCC.MONOGRAFIA
        tcc.save(update_fields=["tcc_titulo", "tcc_resumo", "tcc_modalidade"])
        services_turmas.atualizar_status_tcc(
            tcc, self.turma, aluno.alu, StatusTCC.EM_ANDAMENTO, GatilhoStatusTCC.PROPOSTA_SALVA
        )
        tcc.refresh_from_db()
        self.assertEqual(tcc.tcc_status, StatusTCC.EM_ANDAMENTO)
        historico = HistoricoStatusTCC.objects.get(
            hst_tcc=tcc, hst_gatilho=GatilhoStatusTCC.PROPOSTA_SALVA
        )
        self.assertEqual(historico.hst_status_anterior, StatusTCC.SEM_PROPOSTA)
        self.assertEqual(historico.hst_status_novo, StatusTCC.EM_ANDAMENTO)
        self.assertEqual(historico.hst_usu_id, aluno.alu_id)

    def test_atualizar_status_tcc_transicao_fora_da_tabela_nao_grava_nada(self):
        """Transição fora da tabela (Status atual incompatível com o gatilho) levanta ValueError
        sem gravar nenhuma linha no histórico. [US-14][FR-008][SC-002][research C2]
        """
        aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.SEM_PROPOSTA)
        tcc = tcc_de(aluno, self.turma)
        qtd_historico_antes = HistoricoStatusTCC.objects.filter(hst_tcc=tcc).count()
        with self.assertRaises(ValueError):
            services_turmas.atualizar_status_tcc(
                tcc,
                self.turma,
                aluno.alu,
                StatusTCC.APTO_PARA_DEFESA,
                GatilhoStatusTCC.PROPOSTA_SALVA,
            )
        tcc.refresh_from_db()
        self.assertEqual(tcc.tcc_status, StatusTCC.SEM_PROPOSTA)
        self.assertEqual(
            HistoricoStatusTCC.objects.filter(hst_tcc=tcc).count(), qtd_historico_antes
        )

    def test_atualizar_status_tcc_gatilho_inexistente_levanta_value_error(self):
        """Gatilho fora de TRANSICOES_VALIDAS (string arbitrária) também levanta ValueError, sem
        gravar nada. [US-14][FR-008][research C2]
        """
        aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.SEM_PROPOSTA)
        tcc = tcc_de(aluno, self.turma)
        with self.assertRaises(ValueError):
            services_turmas.atualizar_status_tcc(
                tcc, self.turma, aluno.alu, StatusTCC.EM_ANDAMENTO, "Gatilho Inexistente"
            )
        tcc.refresh_from_db()
        self.assertEqual(tcc.tcc_status, StatusTCC.SEM_PROPOSTA)
        self.assertFalse(
            HistoricoStatusTCC.objects.filter(
                hst_tcc=tcc, hst_gatilho="Gatilho Inexistente"
            ).exists()
        )
