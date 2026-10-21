"""Testes de aceite da US-07: gerenciar turmas de TCC (spec 004, história 1).

Um teste por cenário (1 a 13, menos o 7, que depende da matrícula e fica em test_us08_matricula),
mais os casos das Clarifications (Q9, Q12, Q15) e da revisão.

[US-07][RBN-CAD-04.1][RBN-CAD-04.2][RBN-CAD-04.3][RBN-CAD-04.4][RBN-CAD-04.5][FR-001]-[FR-010]
"""

from datetime import timedelta
from unittest import mock

from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    StatusTCC,
    StatusTurma,
    TipoEntrega,
    TipoEventoTurma,
)
from sigtcc.apps.cadastro.models import (
    Disciplinas,
    HistoricoAlunosTurmas,
    Turmas,
    TurmasMarcos,
)
from sigtcc.apps.cadastro.permissoes import papeis
from sigtcc.apps.cadastro.tests.apoio_acesso import (
    criar_coordenador,
    criar_docente_ativo,
    criar_secretaria,
)
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    SI,
    TesteTurmas,
    criar_aluno_novo,
    criar_defesa_de,
    criar_entrega,
    criar_turma_de,
    curso,
    matricular_aluno,
    tcc_de,
)


def dados_turma(**extras):
    """Dados válidos do formulário da turma (TCC 1 de Engenharia de Computação)."""
    dados = {
        "codigo_disciplina": "ESTCMP025",
        "descricao": DescricaoTurma.TCC_1,
        "identificador": "ECP06_T01",
        "ano": "2026",
        "semestre": "2",
        "dia_semana": "segunda-feira",
        "hora_inicio": "14:00",
        "hora_termino": "16:00",
        "local": "Laboratório LSI",
        "curso": str(curso(EC).pk),
    }
    dados.update(extras)
    return dados


class TurmasTest(TesteTurmas):
    """Cenários da US-07. [US-07][RBN-CAD-04.1 a 04.5]"""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.client.force_login(self.professor)

    def url(self, nome, turma=None):
        return reverse(f"cadastro:{nome}", args=[turma.pk] if turma else [])

    def status(self, turma):
        return Turmas.objects.get(pk=turma.pk).tur_status

    # ------------------------------------------------------------------ cenários da US-07

    def test_cenario1_cadastro_de_turma_tcc1(self):
        """Dado o Professor, quando salva TCC 1 válida, então cadastra e vira Professor dela."""
        resposta = self.client.post(self.url("turma_nova"), dados_turma(), follow=True)
        self.assertContains(resposta, mensagens.TURMA_CADASTRADA)
        turma = Turmas.objects.get(tur_identificador="ECP06_T01")
        self.assertEqual(turma.tur_doc_id, self.professor.pk)
        self.assertEqual(turma.tur_status, StatusTurma.ATIVA)
        self.assertIn(
            "professor_disciplina", papeis(type(self.professor).objects.get(pk=self.professor.pk))
        )

    def test_cenario2_arquivamento_bloqueado_com_tcc_em_andamento(self):
        """Dado TCC Em Andamento, quando clica em Arquivar, então não arquiva e informa."""
        turma = criar_turma_de(self.professor)
        matricular_aluno(turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        resposta = self.client.post(self.url("turma_arquivar", turma), follow=True)
        self.assertContains(resposta, mensagens.ARQUIVAR_TCC_ATIVO)
        self.assertEqual(self.status(turma), StatusTurma.ATIVA)

    def test_cenario3_horario_de_termino_invalido(self):
        """Dado início 10:00 e término 08:00, quando salva, então a mensagem e não salva."""
        dados = dados_turma(hora_inicio="10:00", hora_termino="08:00")
        resposta = self.client.post(self.url("turma_nova"), dados)
        self.assertContains(resposta, mensagens.HORARIO_TERMINO)
        self.assertFalse(Turmas.objects.exists())

    def test_cenario4_exclusao_bloqueada_com_alunos(self):
        """Dado turma com alunos, quando clica em Excluir, então bloqueia com a mensagem."""
        turma = criar_turma_de(self.professor)
        matricular_aluno(turma)
        for metodo in (self.client.get, self.client.post):
            resposta = metodo(self.url("turma_excluir", turma), follow=True)
            self.assertContains(resposta, mensagens.TURMA_COM_ALUNOS)
        self.assertTrue(Turmas.objects.filter(pk=turma.pk).exists())

    def test_cenario5_exclusao_de_turma_vazia(self):
        """Dado turma vazia, quando exclui e confirma, então some da lista."""
        turma = criar_turma_de(self.professor, identificador="VAZIA_T01")
        confirmacao = self.client.get(self.url("turma_excluir", turma))
        self.assertContains(
            confirmacao, mensagens.MT07_CONFIRMAR_EXCLUSAO_TURMA.format(identificador="VAZIA_T01")
        )
        resposta = self.client.post(self.url("turma_excluir", turma), follow=True)
        self.assertContains(resposta, mensagens.MT08_TURMA_EXCLUIDA)
        self.assertNotContains(resposta, "VAZIA_T01")
        self.assertFalse(Turmas.objects.filter(pk=turma.pk).exists())

    def test_cenario6_turma_arquivada_em_modo_leitura(self):
        """Dado turma arquivada, quando o Professor a abre, então só consulta, sem ações."""
        turma = criar_turma_de(self.professor, status=StatusTurma.ARQUIVADA)
        matricular_aluno(turma)
        resposta = self.client.get(self.url("turma", turma))
        self.assertEqual(resposta.status_code, 200)
        for rotulo in (
            mensagens.EDITAR,
            mensagens.MATRICULAR_ALUNOS,
            mensagens.EXCLUIR_DA_TURMA,
            mensagens.ARQUIVAR,
        ):
            self.assertNotContains(resposta, f">{rotulo}<")
        self.assertNotContains(resposta, self.url("turma_editar", turma))

    def test_cenario8_edicao_com_alunos_trava_descricao_e_curso(self):
        """Dado turma com alunos, quando edita, então Descrição e Curso bloqueados."""
        turma = criar_turma_de(self.professor, curso_nome=EC)
        matricular_aluno(turma)
        formulario = self.client.get(self.url("turma_editar", turma))
        self.assertContains(formulario, 'name="descricao"')
        self.assertRegex(formulario.content.decode(), r'name="descricao"[^>]*disabled')
        self.assertRegex(formulario.content.decode(), r'name="curso"[^>]*disabled')
        dados = dados_turma(
            identificador=turma.tur_identificador,
            local="Sala A_12",
            descricao=DescricaoTurma.TCC_2,
            curso=str(curso(SI).pk),
        )
        resposta = self.client.post(self.url("turma_editar", turma), dados, follow=True)
        self.assertContains(resposta, mensagens.MT06_TURMA_ATUALIZADA)
        turma.refresh_from_db()
        self.assertEqual(turma.tur_local, "Sala A_12")
        self.assertEqual(turma.tur_descricao, DescricaoTurma.TCC_1)
        self.assertEqual(turma.tur_cur.cur_nome, EC)

    def test_cenario9_arquivamento_com_sucesso(self):
        """Dado TCC 2 sem TCC ativo, sem sessão e Versão Final vencida, então arquiva."""
        turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2)
        matricular_aluno(turma, status_tcc=StatusTCC.APROVADO)
        criar_entrega(turma, TipoEntrega.VERSAO_FINAL, timezone.now() - timedelta(days=1))
        confirmacao = self.client.get(self.url("turma_arquivar", turma))
        self.assertContains(
            confirmacao,
            mensagens.MT09_CONFIRMAR_ARQUIVAMENTO.format(identificador=turma.tur_identificador),
        )
        resposta = self.client.post(self.url("turma_arquivar", turma), follow=True)
        self.assertContains(resposta, mensagens.MT10_TURMA_ARQUIVADA)
        self.assertEqual(self.status(turma), StatusTurma.ARQUIVADA)

    def test_cenario10_arquivamento_bloqueado_pela_data_limite(self):
        """Dado Versão Final em 30/11 e hoje 20/11, então não arquiva e informa."""
        turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2)
        criar_entrega(turma, TipoEntrega.VERSAO_FINAL, timezone.now() + timedelta(days=10))
        resposta = self.client.post(self.url("turma_arquivar", turma), follow=True)
        self.assertContains(resposta, mensagens.ARQUIVAR_VERSAO_FINAL)
        self.assertEqual(self.status(turma), StatusTurma.ATIVA)

    def test_cenario11_arquivamento_bloqueado_por_sessao_ativa(self):
        """Dado sessão de defesa Agendada, então não arquiva e informa."""
        turma = criar_turma_de(self.professor)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.APROVADO_PARA_TCC_2)
        criar_defesa_de(tcc_de(aluno, turma), "Agendada")
        resposta = self.client.post(self.url("turma_arquivar", turma), follow=True)
        self.assertContains(resposta, mensagens.ARQUIVAR_SESSAO_ATIVA)
        self.assertEqual(self.status(turma), StatusTurma.ATIVA)

    def test_cenario12_local_acima_do_limite(self):
        """Dado Local com 101 caracteres, então destaca o campo e não salva."""
        resposta = self.client.post(self.url("turma_nova"), dados_turma(local="L" * 101))
        self.assertContains(resposta, mensagens.MT05_LOCAL)
        self.assertRegex(resposta.content.decode(), r'campo com-erro">\s*<label for="id_local"')
        self.assertFalse(Turmas.objects.exists())

    def test_cenario13_identificador_repetido(self):
        """Dado ECP06_T01 existente, quando cadastra outra com ele, então destaca e não salva."""
        criar_turma_de(criar_docente_ativo(), identificador="ECP06_T01")
        resposta = self.client.post(self.url("turma_nova"), dados_turma())
        self.assertContains(resposta, mensagens.MT03_IDENTIFICADOR_REPETIDO)
        self.assertRegex(
            resposta.content.decode(), r'campo com-erro">\s*<label for="id_identificador"'
        )
        self.assertEqual(Turmas.objects.count(), 1)

    # ------------------------------------------------------------------ formatos e revisão

    def test_mt01_codigo_disciplina(self):
        for codigo in ("estcmp025", "EST CMP", "A" * 21):
            with self.subTest(codigo=codigo):
                resposta = self.client.post(
                    self.url("turma_nova"), dados_turma(codigo_disciplina=codigo)
                )
                self.assertContains(resposta, mensagens.MT01_CODIGO_DISCIPLINA)

    def test_mt02_identificador_formato(self):
        for identificador in ("ecp06_t01", "ECP 06", "A" * 31):
            with self.subTest(identificador=identificador):
                resposta = self.client.post(
                    self.url("turma_nova"), dados_turma(identificador=identificador)
                )
                self.assertContains(resposta, mensagens.MT02_IDENTIFICADOR_FORMATO)

    def test_mt04_ano_comeca_com_zero(self):
        """m1: "0123" violaria o CHECK do banco; o formulário recusa antes."""
        for ano in ("0123", "26", "20266", "abcd"):
            with self.subTest(ano=ano):
                resposta = self.client.post(self.url("turma_nova"), dados_turma(ano=ano))
                self.assertContains(resposta, mensagens.MT04_ANO)

    def test_mt05_local_com_controle_ou_so_espacos(self):
        """m9: Local só com espaços é obrigatório vazio; com caractere de controle, recusado."""
        resposta = self.client.post(self.url("turma_nova"), dados_turma(local="   "))
        self.assertContains(resposta, mensagens.M14_CAMPO_OBRIGATORIO)
        resposta = self.client.post(self.url("turma_nova"), dados_turma(local="Sala\x07A"))
        self.assertContains(resposta, mensagens.MT05_LOCAL)
        self.assertFalse(Turmas.objects.exists())

    def test_m14_obrigatorios(self):
        resposta = self.client.post(self.url("turma_nova"), {})
        self.assertContains(resposta, mensagens.M14_CAMPO_OBRIGATORIO)

    def test_identificador_concorrente_vira_mt03(self):
        """m3: IntegrityError do banco no cadastro simultâneo vira MT-03, não erro 500."""
        criar_turma_de(criar_docente_ativo(), identificador="ECP06_T01")
        # O formulário "não vê" a outra turma (cadastro simultâneo); o banco recusa.
        with mock.patch(
            "sigtcc.apps.cadastro.forms_turmas.identificador_em_uso", return_value=False
        ):
            resposta = self.client.post(self.url("turma_nova"), dados_turma())
        self.assertContains(resposta, mensagens.MT03_IDENTIFICADOR_REPETIDO)

    def test_q12_turma_que_ja_teve_aluno_nao_exclui(self):
        """Q12: turma vazia com histórico de exclusão não é excluída."""
        turma = criar_turma_de(self.professor)
        HistoricoAlunosTurmas.objects.create(
            hat_alu=criar_aluno_novo(),
            hat_tur_origem=turma,
            hat_tipo_evento=TipoEventoTurma.EXCLUSAO,
            hat_justificativa="Engano",
            hat_data_hora=timezone.now(),
            hat_usu=self.professor,
        )
        resposta = self.client.post(self.url("turma_excluir", turma), follow=True)
        self.assertContains(resposta, mensagens.TURMA_COM_ALUNOS)
        self.assertTrue(Turmas.objects.filter(pk=turma.pk).exists())

    def test_exclusao_apaga_turmas_marcos(self):
        turma = criar_turma_de(self.professor)
        criar_entrega(turma)
        self.client.post(self.url("turma_excluir", turma))
        self.assertFalse(TurmasMarcos.objects.exists())

    def test_exclusao_registra_log_depois_do_commit(self):
        """m4: TURMA_EXCLUIDA com tur_id e identificador, só depois do commit."""
        turma = criar_turma_de(self.professor, identificador="LOG_T01")
        with self.assertLogs("sigtcc.acesso") as log:
            with self.captureOnCommitCallbacks(execute=True):
                self.client.post(self.url("turma_excluir", turma))
        self.assertIn(
            f"TURMA_EXCLUIDA | conta=- | autor={self.professor.pk} | tur_id={turma.pk} "
            "identificador=LOG_T01",
            log.output[0],
        )

    def test_q15_trava_descricao_e_curso_depois_que_alunos_sairam(self):
        """Q15: turma que já teve aluno, mesmo vazia, mantém Descrição e Curso travados."""
        turma = criar_turma_de(self.professor)
        HistoricoAlunosTurmas.objects.create(
            hat_alu=criar_aluno_novo(),
            hat_tur_origem=turma,
            hat_tipo_evento=TipoEventoTurma.EXCLUSAO,
            hat_justificativa="Engano",
            hat_data_hora=timezone.now(),
            hat_usu=self.professor,
        )
        formulario = self.client.get(self.url("turma_editar", turma))
        self.assertRegex(formulario.content.decode(), r'name="descricao"[^>]*disabled')

    def test_edicao_sem_alunos_altera_tudo(self):
        turma = criar_turma_de(self.professor, curso_nome=EC)
        dados = dados_turma(
            identificador=turma.tur_identificador,
            descricao=DescricaoTurma.TCC_2,
            curso=str(curso(SI).pk),
            codigo_disciplina="ESTNOVA01",
        )
        self.client.post(self.url("turma_editar", turma), dados)
        turma.refresh_from_db()
        self.assertEqual(turma.tur_descricao, DescricaoTurma.TCC_2)
        self.assertEqual(turma.tur_cur.cur_nome, SI)
        self.assertEqual(turma.tur_dis.dis_codigo, "ESTNOVA01")

    def test_arquivamento_tcc1_sem_versao_final(self):
        """Em TCC 1 a Data Limite da Versão Final não é exigida."""
        turma = criar_turma_de(self.professor)
        self.client.post(self.url("turma_arquivar", turma))
        self.assertEqual(self.status(turma), StatusTurma.ARQUIVADA)

    def test_arquivamento_tcc2_sem_versao_final_cadastrada(self):
        turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2)
        resposta = self.client.post(self.url("turma_arquivar", turma), follow=True)
        self.assertContains(resposta, mensagens.ARQUIVAR_VERSAO_FINAL)

    def test_arquivamento_ordem_dos_motivos(self):
        """TCC em curso vem antes da sessão ativa, que vem antes da Versão Final."""
        turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.APTO_PARA_DEFESA)
        criar_defesa_de(tcc_de(aluno, turma), "Reagendada")
        resposta = self.client.post(self.url("turma_arquivar", turma), follow=True)
        self.assertContains(resposta, mensagens.ARQUIVAR_TCC_ATIVO)
        self.assertNotContains(resposta, mensagens.ARQUIVAR_SESSAO_ATIVA)

    def test_turma_arquivada_some_da_lista_e_vai_para_arquivadas(self):
        ativa = criar_turma_de(self.professor, identificador="ATIVA_T01")
        arquivada = criar_turma_de(
            self.professor, identificador="ARQ_T01", status=StatusTurma.ARQUIVADA
        )
        lista = self.client.get(self.url("turmas"))
        self.assertContains(lista, ativa.tur_identificador)
        self.assertNotContains(lista, arquivada.tur_identificador)
        self.assertContains(self.client.get(self.url("turmas_arquivadas")), "ARQ_T01")

    def test_mt25_acao_em_turma_arquivada_pelo_endereco(self):
        turma = criar_turma_de(self.professor, status=StatusTurma.ARQUIVADA)
        for nome in ("turma_editar", "turma_excluir", "turma_arquivar"):
            with self.subTest(rota=nome):
                resposta = self.client.post(self.url(nome, turma), dados_turma(), follow=True)
                self.assertContains(resposta, mensagens.MT25_TURMA_ARQUIVADA)
        self.assertEqual(self.status(turma), StatusTurma.ARQUIVADA)

    def test_secretaria_consulta_turmas_do_curso(self):
        """Q9: a Secretaria vê as turmas do curso (ativas e arquivadas), sem ações de turma."""
        ativa = criar_turma_de(self.professor, curso_nome=EC, identificador="SEC_A01")
        criar_turma_de(
            self.professor, curso_nome=EC, identificador="SEC_R01", status=StatusTurma.ARQUIVADA
        )
        criar_turma_de(self.professor, curso_nome=SI, identificador="OUTRO_C01")
        self.client.force_login(criar_secretaria(curso=curso(EC)))
        lista = self.client.get(self.url("turmas"))
        self.assertContains(lista, "SEC_A01")
        self.assertNotContains(lista, "OUTRO_C01")
        self.assertNotContains(lista, mensagens.NOVA_TURMA)
        self.assertContains(self.client.get(self.url("turmas_arquivadas")), "SEC_R01")
        pagina = self.client.get(self.url("turma", ativa))
        self.assertEqual(pagina.status_code, 200)
        self.assertNotContains(pagina, self.url("turma_editar", ativa))
        self.assertEqual(
            self.client.post(self.url("turma_editar", ativa), dados_turma()).status_code, 403
        )
        self.assertEqual(self.client.get(self.url("turma_nova")).status_code, 403)

    def test_outro_docente_e_coordenador_recebem_403(self):
        """Q9: só o Professor da turma e a Secretaria do curso abrem a turma."""
        turma = criar_turma_de(self.professor)
        for usuario in (criar_docente_ativo(), criar_coordenador()):
            with self.subTest(usuario=usuario.pk):
                self.client.force_login(usuario)
                resposta = self.client.get(self.url("turma", turma))
                self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)

    def test_disciplina_criada_e_reaproveitada(self):
        self.client.post(self.url("turma_nova"), dados_turma())
        self.client.post(self.url("turma_nova"), dados_turma(identificador="ECP06_T02"))
        self.assertEqual(Disciplinas.objects.filter(dis_codigo="ESTCMP025").count(), 1)
        self.assertEqual(Turmas.objects.count(), 2)

    def test_sem_login_vai_ao_login(self):
        self.client.logout()
        self.assertRedirects(
            self.client.get(self.url("turmas")),
            "/entrar/?next=/turmas/",
            fetch_redirect_response=False,
        )

    def test_banco_recusa_identificador_repetido(self):
        """O banco também garante a unicidade (spec 001)."""
        criar_turma_de(self.professor, identificador="DUP_T01")
        with self.assertRaises(IntegrityError):
            criar_turma_de(self.professor, identificador="DUP_T01")
