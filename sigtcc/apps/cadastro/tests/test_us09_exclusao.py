"""Testes de aceite da US-09: excluir aluno ou encerrar a participação (spec 004, história 3).

Um teste por cenário (1 a 11; 7 e 8 pela regra reutilizável participacao_encerrada, porque os
botões são das features de TCC, Orientação e Entregas), mais as Clarifications (Q8, Q10, Q14, Q17,
Q19) e a revisão (B-1, I-2, I-4).

[US-09][RBN-CAD-05.4][RBN-CAD-05.8][RBN-CAD-08.4][RBN-CAD-08.5][RBN-CAD-08.7][FR-023]-[FR-026]
"""

from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services_turmas
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    GatilhoStatusTCC,
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
    Artigos,
    Coorientacoes,
    EncontroOrientacao,
    EntregasMarcos,
    HistoricoAlunosTurmas,
    HistoricoStatusTCC,
    Notificacoes,
    Orientacoes,
    PalavrasChaveTCC,
    TCCs,
)
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo, criar_secretaria
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
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

JUSTIFICATIVA = "Aluno vinculado por engano à turma"


class ExclusaoTest(TesteTurmas):
    """Exclusão do aluno sem Proposta (RBN-CAD-05.4) e lista (RBN-CAD-05.8). [US-09]"""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=EC, identificador="ECP06_T01")
        self.aluno = matricular_aluno(self.turma)
        self.client.force_login(self.professor)

    def url(self, aluno=None, turma=None):
        return reverse(
            "cadastro:aluno_excluir", args=[(turma or self.turma).pk, (aluno or self.aluno).pk]
        )

    def excluir(self, justificativa=JUSTIFICATIVA, confirmar=True, aluno=None):
        """Etapa 1 (justificativa) e, se pedido, a confirmação final."""
        resposta = self.client.post(self.url(aluno), {"justificativa": justificativa})
        if (
            not confirmar
            or resposta.status_code != 200
            or "confirmacao_final" not in resposta.content.decode()
        ):
            return resposta
        return self.client.post(
            self.url(aluno),
            {"justificativa": justificativa, "confirmacao_final": "1"},
            follow=True,
        )

    def na_turma(self, aluno=None):
        return AlunosTurmas.objects.filter(mat_tur=self.turma, mat_alu=aluno or self.aluno).exists()

    # ------------------------------------------------------------------ cenários da US-09

    def test_cenario1_exclusao_de_aluno_vinculado_por_engano(self):
        """Dado aluno sem Proposta, quando exclui e confirma, então sai da turma, vai para a
        lista e é notificado com o motivo."""
        resposta = self.excluir()
        self.assertContains(resposta, mensagens.ALUNO_EXCLUIDO)
        self.assertFalse(self.na_turma())
        lista = self.client.get(reverse("cadastro:excluidos_transferidos", args=[self.turma.pk]))
        self.assertContains(lista, self.aluno.alu_matricula)
        notificacao = Notificacoes.objects.get(not_usu_id=self.aluno.pk)
        self.assertEqual(
            notificacao.not_mensagem,
            mensagens.MT21_NOTIFICACAO_EXCLUSAO.format(
                identificador="ECP06_T01", justificativa=JUSTIFICATIVA
            ),
        )

    def test_cenario2_exclusao_bloqueada_para_aluno_com_proposta(self):
        aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        resposta = self.client.get(self.url(aluno), follow=True)
        self.assertContains(resposta, mensagens.ALUNO_TEM_PROPOSTA)
        resposta = self.client.post(
            self.url(aluno), {"justificativa": JUSTIFICATIVA, "confirmacao_final": "1"}, follow=True
        )
        self.assertContains(resposta, mensagens.ALUNO_TEM_PROPOSTA)
        self.assertTrue(self.na_turma(aluno))

    def test_cenario4_justificativa_nao_preenchida(self):
        resposta = self.excluir(justificativa="", confirmar=False)
        self.assertContains(resposta, mensagens.JUSTIFICATIVA_500)
        self.assertTrue(self.na_turma())

    def test_cenario9_consulta_dos_excluidos_ou_transferidos(self):
        """Dado um excluído e um transferido, então a lista mostra os dois com os dados."""
        self.excluir()
        transferido = matricular_aluno(self.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        destino = criar_turma_de(criar_docente_ativo(), identificador="DESTINO_T01")
        HistoricoAlunosTurmas.objects.create(
            hat_alu=transferido,
            hat_tur_origem=self.turma,
            hat_tur_destino=destino,
            hat_tipo_evento=TipoEventoTurma.TRANSFERENCIA,
            hat_justificativa="Troca acordada",
            hat_data_hora=timezone.now(),
            hat_usu=self.professor,
        )
        lista = self.client.get(reverse("cadastro:excluidos_transferidos", args=[self.turma.pk]))
        for texto in (
            self.aluno.alu.usu_nome,
            self.aluno.alu_matricula,
            JUSTIFICATIVA,
            transferido.alu.usu_nome,
            transferido.alu_matricula,
            "Troca acordada",
            self.professor.usu_nome,
        ):
            self.assertContains(lista, texto)

    def test_lista_mais_recente_primeiro_com_destino(self):
        """B16: do mais recente para o mais antigo; na transferência, a turma de destino."""
        self.excluir()
        transferido = matricular_aluno(self.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        destino = criar_turma_de(criar_docente_ativo(), identificador="DESTINO_T01")
        HistoricoAlunosTurmas.objects.create(
            hat_alu=transferido,
            hat_tur_origem=self.turma,
            hat_tur_destino=destino,
            hat_tipo_evento=TipoEventoTurma.TRANSFERENCIA,
            hat_justificativa="Troca acordada",
            hat_data_hora=timezone.now(),
            hat_usu=self.professor,
        )
        lista = self.client.get(reverse("cadastro:excluidos_transferidos", args=[self.turma.pk]))
        self.assertContains(lista, "DESTINO_T01")
        html = lista.content.decode()
        self.assertLess(html.index("Troca acordada"), html.index(JUSTIFICATIVA))

    def test_cenario10_cancelamento(self):
        """Dado formulário preenchido, quando cancela na confirmação final, então nada muda."""
        resposta = self.excluir(confirmar=False)
        self.assertContains(
            resposta, mensagens.MT24_CONFIRMAR_EXCLUSAO_ALUNO.format(nome=self.aluno.alu.usu_nome)
        )
        self.assertContains(resposta, reverse("cadastro:turma", args=[self.turma.pk]))
        self.assertTrue(self.na_turma())
        self.assertFalse(HistoricoAlunosTurmas.objects.exists())

    def test_cenario11_turma_arquivada(self):
        aluno_proposta = matricular_aluno(self.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save()
        pagina = self.client.get(reverse("cadastro:turma", args=[self.turma.pk]))
        self.assertNotContains(pagina, mensagens.EXCLUIR_DA_TURMA)
        self.assertNotContains(pagina, mensagens.ENCERRAR_PARTICIPACAO)
        resposta = self.client.post(self.url(), {"justificativa": JUSTIFICATIVA}, follow=True)
        self.assertContains(resposta, mensagens.MT25_TURMA_ARQUIVADA)
        url = reverse("cadastro:aluno_encerrar", args=[self.turma.pk, aluno_proposta.pk])
        resposta = self.client.post(
            url, {"status": "Desistente", "justificativa": "x"}, follow=True
        )
        self.assertContains(resposta, mensagens.MT25_TURMA_ARQUIVADA)

    # ------------------------------------------------------------------ Clarifications e revisão

    def test_q8_exclusao_apaga_tcc_historico_e_orientacao_automatica(self):
        turma2 = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        aluno = matricular_aluno(turma2)
        tcc = tcc_de(aluno, turma2)
        Orientacoes.objects.create(
            ori_tcc=tcc,
            ori_doc=self.professor.docentes,
            ori_origem=OrigemOrientacao.AUTOMATICO,
            ori_status=StatusOrientacao.ATIVA,
            ori_data_inicio=timezone.now(),
        )
        url = reverse("cadastro:aluno_excluir", args=[turma2.pk, aluno.pk])
        self.client.post(url, {"justificativa": JUSTIFICATIVA, "confirmacao_final": "1"})
        self.assertFalse(TCCs.objects.filter(pk=tcc.pk).exists())
        self.assertFalse(HistoricoStatusTCC.objects.filter(hst_tcc_id=tcc.pk).exists())
        self.assertFalse(Orientacoes.objects.filter(ori_tcc_id=tcc.pk).exists())
        registro = HistoricoAlunosTurmas.objects.get(hat_alu=aluno)
        self.assertEqual(registro.hat_tipo_evento, TipoEventoTurma.EXCLUSAO)
        self.assertIsNone(registro.hat_tur_destino)
        self.assertEqual(registro.hat_usu_id, self.professor.pk)

    def test_exclusao_recusada_com_encontro_coorientacao_palavra_publicacao_ou_defesa(self):
        """B14: o trabalho já foi movimentado → a mesma mensagem da Proposta. Pedido de orientação
        não está mais na lista (Q-120: o que decide é o Status "Sem Proposta")."""
        outro = criar_docente_ativo()
        casos = {
            "orientação por pedido aceito": lambda tcc: Orientacoes.objects.create(
                ori_tcc=tcc,
                ori_doc=outro.docentes,
                ori_origem=OrigemOrientacao.PEDIDO_ACEITO,
                ori_status=StatusOrientacao.ENCERRADA,
                ori_data_inicio=timezone.now(),
            ),
            "coorientação": lambda tcc: Coorientacoes.objects.create(
                coo_tcc=tcc,
                coo_doc=outro.docentes,
                coo_status=StatusCoorientacao.ATIVA,
                coo_data_inicio=timezone.now(),
            ),
            "palavra-chave": lambda tcc: PalavrasChaveTCC.objects.create(
                pal_tcc=tcc, pal_palavra="Teste"
            ),
            "encontro": lambda tcc: EncontroOrientacao.objects.create(
                enc_tcc=tcc, enc_data=timezone.now().date(), enc_pauta="Pauta", enc_metas="Metas"
            ),
            "publicação": lambda tcc: Artigos.objects.create(
                art=tcc, art_link_doi="https://doi.org/10.1/x", art_veiculo_publicacao="Revista"
            ),
            "defesa": lambda tcc: criar_defesa_de(tcc, "Cancelada"),
        }
        for nome, criar in casos.items():
            with self.subTest(caso=nome):
                aluno = matricular_aluno(self.turma)
                criar(tcc_de(aluno, self.turma))
                resposta = self.client.post(
                    self.url(aluno),
                    {"justificativa": JUSTIFICATIVA, "confirmacao_final": "1"},
                    follow=True,
                )
                self.assertContains(resposta, mensagens.ALUNO_TEM_PROPOSTA)
                self.assertTrue(self.na_turma(aluno))

    def test_q17_exclusao_mantem_entregas_com_envio_e_apaga_sem_envio(self):
        sem_envio = entrega_do_aluno(criar_entrega(self.turma), self.aluno)
        com_envio = entrega_do_aluno(criar_entrega(self.turma), self.aluno)
        criar_envio(com_envio)
        self.assertContains(self.excluir(), mensagens.ALUNO_EXCLUIDO)
        self.assertFalse(EntregasMarcos.objects.filter(pk=sem_envio.pk).exists())
        self.assertTrue(EntregasMarcos.objects.filter(pk=com_envio.pk).exists())

    def test_b1_notificacao_mt21_com_justificativa_500_e_identificador_30(self):
        turma = criar_turma_de(self.professor, identificador="I" * 30)
        aluno = matricular_aluno(turma)
        url = reverse("cadastro:aluno_excluir", args=[turma.pk, aluno.pk])
        resposta = self.client.post(
            url, {"justificativa": "j" * 500, "confirmacao_final": "1"}, follow=True
        )
        self.assertContains(resposta, mensagens.ALUNO_EXCLUIDO)
        texto = Notificacoes.objects.get(not_usu_id=aluno.pk).not_mensagem
        self.assertEqual(len(texto), 500)
        self.assertTrue(texto.startswith(f"Você foi excluído da turma {'I' * 30}. Motivo: jj"))
        self.assertTrue(texto.endswith("…"))

    def test_confirmacao_final_mt24_com_justificativa_oculta(self):
        resposta = self.excluir(confirmar=False)
        self.assertContains(resposta, 'name="confirmacao_final"')
        self.assertContains(resposta, f'value="{JUSTIFICATIVA}"')

    def test_lista_excluidos_transferidos_so_professor(self):
        """I-4: a lista é só do Professor da Disciplina (matriz, RBN-CAD-05.8)."""
        url = reverse("cadastro:excluidos_transferidos", args=[self.turma.pk])
        self.client.force_login(criar_secretaria(curso=curso(EC)))
        self.assertContains(self.client.get(url), mensagens.M02_ACESSO_NEGADO, status_code=403)
        self.client.force_login(criar_docente_ativo())
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_aluno_de_outra_turma_404(self):
        outro = matricular_aluno(criar_turma_de(criar_docente_ativo()))
        self.assertEqual(self.client.get(self.url(outro)).status_code, 404)
        url = reverse("cadastro:aluno_encerrar", args=[self.turma.pk, outro.pk])
        self.assertEqual(self.client.get(url).status_code, 404)


class EncerramentoTest(TesteTurmas):
    """Encerramento da participação (RBN-CAD-08.4, 08.5). [US-09]"""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=EC)
        self.aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        self.tcc = tcc_de(self.aluno, self.turma)
        self.client.force_login(self.professor)

    def encerrar(self, status="Desistente", justificativa="Desistiu da disciplina", aluno=None):
        url = reverse("cadastro:aluno_encerrar", args=[self.turma.pk, (aluno or self.aluno).pk])
        return self.client.post(
            url, {"status": status, "justificativa": justificativa}, follow=True
        )

    def status(self):
        return TCCs.objects.get(pk=self.tcc.pk).tcc_status

    def test_cenario3_encerramento_como_desistente(self):
        resposta = self.encerrar()
        self.assertContains(
            resposta, mensagens.MT23_PARTICIPACAO_ENCERRADA.format(status="Desistente")
        )
        self.assertEqual(self.status(), StatusTCC.DESISTENTE)
        self.assertEqual(
            TCCs.objects.get(pk=self.tcc.pk).tcc_justificativa_encerramento,
            "Desistiu da disciplina",
        )

    def test_historico_encerramento_com_professor_e_gatilho(self):
        """RBN-CAD-08.7: a transição fica no histórico com o Professor e o gatilho."""
        self.encerrar()
        ultimo = HistoricoStatusTCC.objects.filter(hst_tcc=self.tcc).order_by("-hst_id").first()
        self.assertEqual(
            (ultimo.hst_status_anterior, ultimo.hst_status_novo),
            (StatusTCC.EM_ANDAMENTO, StatusTCC.DESISTENTE),
        )
        self.assertEqual(ultimo.hst_gatilho, GatilhoStatusTCC.ENCERRAMENTO_DA_PARTICIPACAO)
        self.assertEqual(ultimo.hst_usu_id, self.professor.pk)

    def test_cenario5_justificativa_acima_do_limite(self):
        self.assertContains(self.encerrar(justificativa="j" * 501), mensagens.JUSTIFICATIVA_500)
        self.assertEqual(self.status(), StatusTCC.EM_ANDAMENTO)

    def test_cenario6_status_nao_selecionado(self):
        self.assertContains(self.encerrar(status=""), mensagens.SELECIONE_STATUS)
        self.assertEqual(self.status(), StatusTCC.EM_ANDAMENTO)

    def test_cenario7_reprovado_em_modo_leitura(self):
        """A regra reutilizável diz que o aluno Reprovado está restrito (RBN-CAD-08.5); o botão de
        envio é da feature de Entregas (US-16)."""
        self.encerrar(status="Reprovado")
        self.assertTrue(services_turmas.participacao_encerrada(TCCs.objects.get(pk=self.tcc.pk)))

    def test_cenario8_restricao_sem_excecao(self):
        self.encerrar(status="Jubilado")
        self.assertTrue(services_turmas.participacao_encerrada(TCCs.objects.get(pk=self.tcc.pk)))

    def test_q10_encerramento_encerra_orientacao_e_coorientacao(self):
        outro = criar_docente_ativo()
        Orientacoes.objects.create(
            ori_tcc=self.tcc,
            ori_doc=outro.docentes,
            ori_origem=OrigemOrientacao.PEDIDO_ACEITO,
            ori_status=StatusOrientacao.ATIVA,
            ori_data_inicio=timezone.now(),
        )
        Coorientacoes.objects.create(
            coo_tcc=self.tcc,
            coo_doc=criar_docente_ativo().docentes,
            coo_status=StatusCoorientacao.ATIVA,
            coo_data_inicio=timezone.now(),
        )
        self.encerrar()
        self.assertEqual(
            Orientacoes.objects.get(ori_tcc=self.tcc).ori_status, StatusOrientacao.ENCERRADA
        )
        self.assertEqual(
            Coorientacoes.objects.get(coo_tcc=self.tcc).coo_status, StatusCoorientacao.ENCERRADA
        )

    def test_q14_encerramento_recusado_com_sessao_ativa_mt30(self):
        for status in ("Agendada", "Reagendada", "Em Andamento"):
            with self.subTest(status=status):
                aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.APTO_PARA_DEFESA)
                criar_defesa_de(tcc_de(aluno, self.turma), status)
                self.assertContains(self.encerrar(aluno=aluno), mensagens.MT30_ENCERRAMENTO_SESSAO)
                self.assertEqual(tcc_de(aluno, self.turma).tcc_status, StatusTCC.APTO_PARA_DEFESA)

    def test_q14_q19_pedidos_e_convites_pendentes_cancelados_e_notificados(self):
        docente_pedido = criar_docente_ativo()
        docente_convite = criar_docente_ativo()
        pedido = criar_solicitacao(self.tcc, docente_pedido, tipo=TipoSolicitacao.ORIENTACAO)
        convite = criar_solicitacao(self.tcc, docente_convite, tipo=TipoSolicitacao.COORIENTACAO)
        self.encerrar()
        for solicitacao, docente in ((pedido, docente_pedido), (convite, docente_convite)):
            solicitacao.refresh_from_db()
            self.assertEqual(solicitacao.sol_status, StatusSolicitacao.CANCELADO)
            self.assertIsNotNone(solicitacao.sol_data_resposta)
            texto = Notificacoes.objects.get(not_usu_id=docente.pk).not_mensagem
            self.assertEqual(
                texto,
                mensagens.MT31_PEDIDO_CANCELADO.format(
                    tipo=solicitacao.sol_tipo.lower(), nome=self.aluno.alu.usu_nome
                ),
            )

    def test_encerramento_so_em_andamento_ou_apto(self):
        """Sem Proposta usa a exclusão; participação já encerrada não é encerrada de novo."""
        sem_proposta = matricular_aluno(self.turma)
        desistente = matricular_aluno(self.turma, status_tcc=StatusTCC.DESISTENTE)
        for aluno in (sem_proposta, desistente):
            with self.subTest(aluno=aluno.pk):
                url = reverse("cadastro:aluno_encerrar", args=[self.turma.pk, aluno.pk])
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_encerramento_concorrente_com_transferencia(self):
        """I-2: depois da transferência, o encerramento pela turma de origem é recusado."""
        turma2 = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        aluno = matricular_aluno(turma2, status_tcc=StatusTCC.EM_ANDAMENTO)
        destino = criar_turma_de(
            criar_docente_ativo(), descricao=DescricaoTurma.TCC_2, curso_nome=EC
        )
        services_turmas.transferir(self.professor, turma2.pk, aluno.pk, destino.pk, "Troca")
        url = reverse("cadastro:aluno_encerrar", args=[turma2.pk, aluno.pk])
        resposta = self.client.post(url, {"status": "Desistente", "justificativa": "x"})
        self.assertEqual(resposta.status_code, 404)
        self.assertEqual(tcc_de(aluno, destino).tcc_status, StatusTCC.EM_ANDAMENTO)


class ExclusaoComPedidoTest(TesteTurmas):
    """Q-120 (teste manual, passo 13): aluno "Sem Proposta" com pedido de orientação é excluído;
    os pendentes são cancelados com aviso ao docente (MT-33); cada solicitação vai para o log de
    acesso antes de ser apagada (Não Repúdio, RAN-CAD-10 NFR); ata, coorientação e artigo
    continuam bloqueando. [US-09][RBN-CAD-05.4][RAN-CAD-10 NFR][FR-023][Q-120]
    """

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=EC, identificador="ECP06_T02")
        self.aluno = matricular_aluno(self.turma)
        self.tcc = tcc_de(self.aluno, self.turma)
        self.docente = criar_docente_ativo()
        self.client.force_login(self.professor)

    def excluir(self):
        url = reverse("cadastro:aluno_excluir", args=[self.turma.pk, self.aluno.pk])
        return self.client.post(
            url, {"justificativa": JUSTIFICATIVA, "confirmacao_final": "1"}, follow=True
        )

    def na_turma(self):
        return AlunosTurmas.objects.filter(mat_tur=self.turma, mat_alu=self.aluno).exists()

    def test_pedido_recusado_nao_impede_e_fica_no_log(self):
        pedido = criar_solicitacao(self.tcc, self.docente, status=StatusSolicitacao.RECUSADO)
        pedido.sol_data_resposta = timezone.now()
        pedido.save()
        with self.assertLogs("sigtcc.acesso") as log:
            with self.captureOnCommitCallbacks(execute=True):
                resposta = self.excluir()
        self.assertContains(resposta, mensagens.ALUNO_EXCLUIDO)
        self.assertFalse(self.na_turma())
        self.assertFalse(TCCs.objects.filter(pk=self.tcc.pk).exists())
        from sigtcc.apps.cadastro.models import SolicitacoesOrientacao

        self.assertFalse(SolicitacoesOrientacao.objects.filter(pk=pedido.pk).exists())
        linha = next(x for x in log.output if "SOLICITACAO_REMOVIDA_NA_EXCLUSAO" in x)
        self.assertIn(f"sol_id={pedido.pk}", linha)
        self.assertIn("status=Recusado", linha)
        self.assertIn(f"docente={self.docente.pk}", linha)
        self.assertIn(f"autor={self.professor.pk}", linha)
        self.assertFalse(Notificacoes.objects.filter(not_usu=self.docente).exists())

    def test_pedido_pendente_e_cancelado_com_aviso(self):
        criar_solicitacao(self.tcc, self.docente)
        convidado = criar_docente_ativo()
        criar_solicitacao(self.tcc, convidado, tipo=TipoSolicitacao.COORIENTACAO)
        with self.assertLogs("sigtcc.acesso") as log:
            with self.captureOnCommitCallbacks(execute=True):
                self.excluir()
        self.assertFalse(self.na_turma())
        for docente, tipo in (
            (self.docente, mensagens.TIPO_PEDIDO_ORIENTACAO),
            (convidado, mensagens.TIPO_CONVITE_COORIENTACAO),
        ):
            aviso = Notificacoes.objects.get(not_usu=docente)
            self.assertEqual(
                aviso.not_mensagem,
                mensagens.MT33_SOLICITACAO_CANCELADA_EXCLUSAO.format(
                    tipo=tipo,
                    nome=self.aluno.alu.usu_nome,
                    identificador=self.turma.tur_identificador,
                ),
            )
            self.assertEqual(aviso.not_link_tela, reverse("cadastro:orientacoes"))
        removidas = [x for x in log.output if "SOLICITACAO_REMOVIDA_NA_EXCLUSAO" in x]
        self.assertEqual(len(removidas), 2)
        self.assertTrue(all("status=Cancelado" in x for x in removidas))

    def test_com_ata_coorientacao_ou_artigo_continua_bloqueado(self):
        criar_solicitacao(self.tcc, self.docente, status=StatusSolicitacao.RECUSADO)
        casos = {
            "ata": lambda tcc: EncontroOrientacao.objects.create(
                enc_tcc=tcc, enc_data=timezone.now().date(), enc_pauta="P", enc_metas="M"
            ),
            "coorientação": lambda tcc: Coorientacoes.objects.create(
                coo_tcc=tcc,
                coo_doc=self.docente.docentes,
                coo_status=StatusCoorientacao.ATIVA,
                coo_data_inicio=timezone.now(),
            ),
            "artigo": lambda tcc: Artigos.objects.create(
                art=tcc, art_link_doi="https://doi.org/10.1/x"
            ),
        }
        for nome, criar in casos.items():
            with self.subTest(caso=nome):
                aluno = matricular_aluno(self.turma)
                criar(tcc_de(aluno, self.turma))
                url = reverse("cadastro:aluno_excluir", args=[self.turma.pk, aluno.pk])
                resposta = self.client.post(
                    url, {"justificativa": JUSTIFICATIVA, "confirmacao_final": "1"}, follow=True
                )
                self.assertContains(resposta, mensagens.ALUNO_TEM_PROPOSTA)
                self.assertTrue(
                    AlunosTurmas.objects.filter(mat_tur=self.turma, mat_alu=aluno).exists()
                )

    def test_painel_mostra_excluir_com_pedido(self):
        criar_solicitacao(self.tcc, self.docente, status=StatusSolicitacao.RECUSADO)
        resposta = self.client.get(
            reverse("cadastro:painel_aluno", args=[self.turma.pk, self.aluno.pk])
        )
        self.assertContains(resposta, "Excluir aluno")
        self.assertNotContains(resposta, "Encerrar participação")
