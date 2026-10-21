"""Testes de aceite da US-08: transferência do aluno para a turma de TCC 2 de outro orientador.

Cenários 6 e 12 da US-08, mais as Clarifications (Q9, Q17) e a revisão (I-1, m6, m11).

[US-08][RBN-CAD-05.6][RBN-CAD-04.2][FR-020]-[FR-022][Q9][Q17][I-1][m6][m11]
"""

from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    OrigemOrientacao,
    StatusCoorientacao,
    StatusOrientacao,
    StatusSolicitacao,
    StatusTCC,
    StatusTurma,
    TipoEventoTurma,
    TipoSolicitacao,
)
from sigtcc.apps.cadastro.models import (
    AlunosTurmas,
    Coorientacoes,
    EntregasMarcos,
    HistoricoAlunosTurmas,
    HistoricoStatusTCC,
    Notificacoes,
    Orientacoes,
    SolicitacoesOrientacao,
)
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo, criar_secretaria
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    SI,
    TesteTurmas,
    criar_defesa_de,
    criar_entrega,
    criar_envio,
    criar_solicitacao,
    criar_turma_de,
    curso,
    entrega_do_aluno,
    matricular_aluno,
    tcc_de,
)

TCC2 = DescricaoTurma.TCC_2


class TransferenciaTest(TesteTurmas):
    """Transferência (RBN-CAD-05.6). [US-08][RBN-CAD-05.6]"""

    def setUp(self):
        super().setUp()
        self.prof_origem = criar_docente_ativo()
        self.prof_destino = criar_docente_ativo()
        self.origem = criar_turma_de(
            self.prof_origem, descricao=TCC2, curso_nome=EC, identificador="ECP_ORIGEM"
        )
        self.destino = criar_turma_de(
            self.prof_destino, descricao=TCC2, curso_nome=EC, identificador="ECP_DESTINO"
        )
        self.aluno = matricular_aluno(self.origem, status_tcc=StatusTCC.EM_ANDAMENTO)
        self.tcc = tcc_de(self.aluno, self.origem)
        Orientacoes.objects.create(
            ori_tcc=self.tcc,
            ori_doc=self.prof_origem.docentes,
            ori_origem=OrigemOrientacao.AUTOMATICO,
            ori_status=StatusOrientacao.ATIVA,
            ori_data_inicio=timezone.now(),
        )
        self.client.force_login(self.prof_origem)

    def url(self, turma=None, aluno=None):
        return reverse(
            "cadastro:aluno_transferir", args=[(turma or self.origem).pk, (aluno or self.aluno).pk]
        )

    def transferir(
        self, destino=None, justificativa="Troca de orientador acordada", follow=True, **extras
    ):
        dados = {"destino": (destino or self.destino).pk, "justificativa": justificativa}
        return self.client.post(self.url(**extras), dados, follow=follow)

    # ------------------------------------------------------------------ cenários da US-08

    def test_cenario6_transferencia_para_outra_turma_tcc2(self):
        """Dado TCC Em Andamento sem sessão, então só no destino, com o novo orientador, e os
        três notificados."""
        resposta = self.transferir()
        self.assertContains(
            resposta, mensagens.MT16_TRANSFERIDO.format(identificador="ECP_DESTINO")
        )
        self.assertFalse(
            AlunosTurmas.objects.filter(mat_alu=self.aluno, mat_tur=self.origem).exists()
        )
        self.assertTrue(
            AlunosTurmas.objects.filter(mat_alu=self.aluno, mat_tur=self.destino).exists()
        )
        ativa = Orientacoes.objects.get(ori_tcc=self.tcc, ori_status=StatusOrientacao.ATIVA)
        self.assertEqual(ativa.ori_doc_id, self.prof_destino.pk)
        destinatarios = set(Notificacoes.objects.values_list("not_usu_id", flat=True))
        self.assertEqual(destinatarios, {self.aluno.pk, self.prof_origem.pk, self.prof_destino.pk})

    def test_cenario12_transferencia_bloqueada_por_sessao_ativa(self):
        """Dado sessão Agendada, quando tenta transferir, então não transfere e informa."""
        criar_defesa_de(self.tcc, "Agendada")
        resposta = self.transferir()
        self.assertContains(resposta, mensagens.MT18_TRANSFERENCIA_SESSAO)
        self.assertTrue(
            AlunosTurmas.objects.filter(mat_alu=self.aluno, mat_tur=self.origem).exists()
        )

    # ------------------------------------------------------------------ recusas e destinos

    def test_mt17_tcc_fora_de_em_andamento_ou_apto(self):
        aluno = matricular_aluno(self.origem, status_tcc=StatusTCC.SEM_PROPOSTA)
        resposta = self.transferir(aluno=aluno)
        self.assertContains(resposta, mensagens.MT17_TRANSFERENCIA_STATUS)

    def test_mt18_sessao_reagendada_e_em_andamento(self):
        for status in ("Reagendada", "Em Andamento"):
            with self.subTest(status=status):
                aluno = matricular_aluno(self.origem, status_tcc=StatusTCC.APTO_PARA_DEFESA)
                criar_defesa_de(tcc_de(aluno, self.origem), status)
                self.assertContains(
                    self.transferir(aluno=aluno), mensagens.MT18_TRANSFERENCIA_SESSAO
                )

    def test_mt19_sem_destino_possivel(self):
        self.destino.delete()
        resposta = self.client.get(self.url(), follow=True)
        self.assertContains(resposta, mensagens.MT19_SEM_DESTINO)

    def test_i1_destino_onde_o_aluno_ja_tem_vinculo_ou_tcc_some_da_lista(self):
        """I-1: turma onde o aluno já tem vínculo ou TCC não aparece (evita erro de unicidade)."""
        matricular_aluno(self.destino, aluno=self.aluno, status_tcc=StatusTCC.DESISTENTE)
        AlunosTurmas.objects.filter(mat_alu=self.aluno, mat_tur=self.destino).delete()
        resposta = self.client.get(self.url(), follow=True)
        self.assertContains(resposta, mensagens.MT19_SEM_DESTINO)
        self.assertContains(self.transferir(), mensagens.MT19_SEM_DESTINO)

    def test_destinos_so_tcc2_mesmo_curso_e_periodo_ativa_outro_professor(self):
        criar_turma_de(
            self.prof_destino, descricao=DescricaoTurma.TCC_1, curso_nome=EC, identificador="X_TCC1"
        )
        criar_turma_de(self.prof_destino, descricao=TCC2, curso_nome=SI, identificador="X_SI")
        criar_turma_de(
            self.prof_destino, descricao=TCC2, curso_nome=EC, semestre=1, identificador="X_SEM1"
        )
        criar_turma_de(
            self.prof_destino,
            descricao=TCC2,
            curso_nome=EC,
            status=StatusTurma.ARQUIVADA,
            identificador="X_ARQ",
        )
        criar_turma_de(self.prof_origem, descricao=TCC2, curso_nome=EC, identificador="X_MESMO")
        formulario = self.client.get(self.url())
        self.assertContains(formulario, "ECP_DESTINO")
        for identificador in ("X_TCC1", "X_SI", "X_SEM1", "X_ARQ", "X_MESMO"):
            with self.subTest(turma=identificador):
                self.assertNotContains(formulario, identificador)

    def test_so_em_turma_com_orientador_automatico(self):
        """TCC 2 de SI não tem orientador automático: sem "Transferir" e recusa pelo endereço."""
        turma_si = criar_turma_de(self.prof_origem, descricao=TCC2, curso_nome=SI)
        aluno = matricular_aluno(turma_si, status_tcc=StatusTCC.EM_ANDAMENTO)
        pagina = self.client.get(reverse("cadastro:turma", args=[turma_si.pk]))
        self.assertNotContains(pagina, ">Transferir<")
        self.assertEqual(self.client.get(self.url(turma=turma_si, aluno=aluno)).status_code, 403)

    def test_justificativa_vazia_e_501(self):
        for justificativa in ("", "   ", "j" * 501):
            with self.subTest(tamanho=len(justificativa)):
                self.assertContains(
                    self.transferir(justificativa=justificativa), mensagens.JUSTIFICATIVA_500
                )
        self.assertTrue(
            AlunosTurmas.objects.filter(mat_tur=self.origem, mat_alu=self.aluno).exists()
        )

    # ------------------------------------------------------------------ permissões (Q9)

    def test_secretaria_do_curso_transfere(self):
        self.client.force_login(criar_secretaria(curso=curso(EC)))
        pagina = self.client.get(reverse("cadastro:turma", args=[self.origem.pk]))
        self.assertContains(pagina, ">Transferir<")
        self.transferir()
        self.assertTrue(
            AlunosTurmas.objects.filter(mat_tur=self.destino, mat_alu=self.aluno).exists()
        )

    def test_secretaria_de_outro_curso_403(self):
        self.client.force_login(criar_secretaria(curso=curso(SI)))
        self.assertEqual(self.transferir(follow=False).status_code, 403)

    def test_aluno_de_outra_turma_404(self):
        outro = matricular_aluno(self.destino, status_tcc=StatusTCC.EM_ANDAMENTO)
        self.assertEqual(self.client.get(self.url(aluno=outro)).status_code, 404)

    def test_transferencia_em_turma_arquivada(self):
        self.origem.tur_status = StatusTurma.ARQUIVADA
        self.origem.save()
        self.assertContains(self.transferir(), mensagens.MT25_TURMA_ARQUIVADA)

    # ------------------------------------------------------------------ efeitos

    def test_orientacao_antiga_encerrada_antes_da_nova(self):
        """m6: a antiga fica 'Encerrada' com data de fim; uma só ativa por TCC."""
        self.transferir()
        antiga = Orientacoes.objects.get(ori_tcc=self.tcc, ori_doc=self.prof_origem.docentes)
        self.assertEqual(antiga.ori_status, StatusOrientacao.ENCERRADA)
        self.assertIsNotNone(antiga.ori_data_fim)
        self.assertEqual(
            Orientacoes.objects.filter(ori_tcc=self.tcc, ori_status=StatusOrientacao.ATIVA).count(),
            1,
        )

    def test_coorientacao_do_professor_destino_encerrada(self):
        Coorientacoes.objects.create(
            coo_tcc=self.tcc,
            coo_doc=self.prof_destino.docentes,
            coo_status=StatusCoorientacao.ATIVA,
            coo_data_inicio=timezone.now(),
        )
        self.transferir()
        self.assertEqual(
            Coorientacoes.objects.get(coo_tcc=self.tcc).coo_status, StatusCoorientacao.ENCERRADA
        )

    def test_m11_convite_de_coorientacao_pendente_cancelado(self):
        convite = criar_solicitacao(self.tcc, self.prof_destino, tipo=TipoSolicitacao.COORIENTACAO)
        self.transferir()
        convite.refresh_from_db()
        self.assertEqual(convite.sol_status, StatusSolicitacao.CANCELADO)
        self.assertIsNotNone(convite.sol_data_resposta)

    def test_q17_entregas_origem_sem_envio_apagadas_com_envio_mantidas(self):
        sem_envio = entrega_do_aluno(criar_entrega(self.origem), self.aluno)
        com_envio = entrega_do_aluno(criar_entrega(self.origem), self.aluno)
        criar_envio(com_envio)
        self.transferir()
        self.assertFalse(EntregasMarcos.objects.filter(pk=sem_envio.pk).exists())
        self.assertTrue(EntregasMarcos.objects.filter(pk=com_envio.pk).exists())

    def test_q17_entregas_do_destino_criadas(self):
        entrega = criar_entrega(self.destino)
        self.transferir()
        self.assertTrue(EntregasMarcos.objects.filter(ent_tma=entrega, ent_alu=self.aluno).exists())

    def test_historico_transferencia_e_lista_da_origem(self):
        self.transferir(justificativa="Troca acordada com a coordenação")
        registro = HistoricoAlunosTurmas.objects.get(hat_alu=self.aluno)
        self.assertEqual(registro.hat_tipo_evento, TipoEventoTurma.TRANSFERENCIA)
        self.assertEqual(
            (registro.hat_tur_origem_id, registro.hat_tur_destino_id),
            (self.origem.pk, self.destino.pk),
        )
        self.assertEqual(registro.hat_usu_id, self.prof_origem.pk)
        self.assertEqual(registro.hat_justificativa, "Troca acordada com a coordenação")

    def test_notificacoes_mt22_aluno_e_dois_orientadores(self):
        self.transferir()
        texto = mensagens.MT22_NOTIFICACAO_TRANSFERENCIA.format(
            nome=self.aluno.alu.usu_nome, origem="ECP_ORIGEM", destino="ECP_DESTINO"
        )
        notificacoes = {n.not_usu_id: n for n in Notificacoes.objects.all()}
        for usuario in (self.aluno.pk, self.prof_origem.pk, self.prof_destino.pk):
            self.assertEqual(notificacoes[usuario].not_mensagem, texto)
        self.assertEqual(
            notificacoes[self.prof_destino.pk].not_link_tela,
            reverse("cadastro:turma", args=[self.destino.pk]),
        )
        self.assertIsNone(notificacoes[self.aluno.pk].not_link_tela)
        self.assertIsNone(notificacoes[self.prof_origem.pk].not_link_tela)

    def test_mesmo_tcc_com_status_e_historico_na_nova_turma(self):
        historicos = HistoricoStatusTCC.objects.filter(hst_tcc=self.tcc).count()
        self.transferir()
        self.tcc.refresh_from_db()
        self.assertEqual(self.tcc.tcc_tur_id, self.destino.pk)
        self.assertEqual(self.tcc.tcc_status, StatusTCC.EM_ANDAMENTO)
        self.assertEqual(HistoricoStatusTCC.objects.filter(hst_tcc=self.tcc).count(), historicos)

    def test_solicitacao_pendente_de_outro_docente_fica(self):
        outro = criar_docente_ativo()
        convite = criar_solicitacao(self.tcc, outro, tipo=TipoSolicitacao.COORIENTACAO)
        self.transferir()
        convite.refresh_from_db()
        self.assertEqual(convite.sol_status, StatusSolicitacao.AGUARDANDO_ACEITE)
        self.assertTrue(SolicitacoesOrientacao.objects.exists())
