"""Testes de aceite da US-08 (matrícula individual e edição do aluno) e do cenário 7 da US-07.

Cenários 1, 2, 3, 9, 10, 11 e 13 da US-08; os de importação e de transferência ficam nos seus
arquivos. Mais os casos das Clarifications (Q6, Q7, Q16 a Q18) e da revisão.

[US-08][RBN-CAD-05.1][RBN-CAD-05.3][RBN-CAD-05.5][RBN-CAD-05.7][US-07][RBN-CAD-04.2]
[RBN-CAD-08.6][FR-004][FR-011]-[FR-015][FR-019][Q6][Q7][Q16][Q17][Q18]
"""

from unittest import mock

from django.core import mail
from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services_turmas
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    GatilhoStatusTCC,
    OrigemOrientacao,
    StatusConta,
    StatusCoorientacao,
    StatusEntrega,
    StatusOrientacao,
    StatusTCC,
    StatusTurma,
)
from sigtcc.apps.cadastro.models import (
    Alunos,
    AlunosTurmas,
    Artigos,
    Coorientacoes,
    EntregasMarcos,
    HistoricoStatusTCC,
    Orientacoes,
    PalavrasChaveTCC,
    TCCs,
    Usuarios,
)
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    LC,
    SI,
    TesteTurmas,
    criar_aluno_novo,
    criar_entrega,
    criar_envio,
    criar_turma_de,
    entrega_do_aluno,
    matricular_aluno,
    tcc_de,
)


class MatriculaTest(TesteTurmas):
    """Matrícula individual. [US-08][RBN-CAD-05.1][RBN-CAD-05.5]"""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=EC)
        self.client.force_login(self.professor)

    def matricular(
        self,
        matricula="2026000123",
        nome="Ana Maria Souza",
        curso="EST08MCPD",
        turma=None,
        follow=True,
    ):
        url = reverse("cadastro:matricular", args=[(turma or self.turma).pk])
        dados = {"matricula": matricula, "nome": nome, "curso": curso}
        return self.client.post(url, dados, follow=follow)

    def aluno(self, matricula="2026000123"):
        return Alunos.objects.select_related("alu").get(alu_matricula=matricula)

    # ------------------------------------------------------------------ cenários da US-08

    def test_cenario1_aluno_novo(self):
        """Dado matrícula inexistente, quando salva, então conta 'Aguardando Ativação' e vínculo."""
        resposta = self.matricular()
        self.assertContains(resposta, mensagens.ALUNO_MATRICULADO)
        aluno = self.aluno()
        self.assertEqual(aluno.alu.usu_status, StatusConta.AGUARDANDO_ATIVACAO)
        self.assertTrue(AlunosTurmas.objects.filter(mat_alu=aluno, mat_tur=self.turma).exists())

    def test_cenario2_matricula_com_8_digitos(self):
        """Dado 8 dígitos, então "A matrícula deve ter 10 dígitos numéricos" e não salva."""
        resposta = self.matricular(matricula="20260001")
        self.assertContains(resposta, mensagens.MATRICULA_FORMATO)
        self.assertFalse(Alunos.objects.filter(alu_matricula="20260001").exists())

    def test_cenario3_aluno_ja_cadastrado_em_outra_turma(self):
        """Dado aluno que cursou TCC 1, quando matriculado em TCC 2, então sem conta nova."""
        turma1 = criar_turma_de(criar_docente_ativo(), status=StatusTurma.ARQUIVADA)
        aluno = matricular_aluno(turma1, matricula="2026000123", status_tcc=StatusTCC.REPROVADO)
        turma2 = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=SI)
        contas = Usuarios.objects.count()
        resposta = self.matricular(turma=turma2)
        self.assertContains(resposta, mensagens.ALUNO_MATRICULADO)
        self.assertEqual(Usuarios.objects.count(), contas)
        self.assertTrue(AlunosTurmas.objects.filter(mat_alu=aluno, mat_tur=turma1).exists())
        self.assertTrue(AlunosTurmas.objects.filter(mat_alu=aluno, mat_tur=turma2).exists())

    def test_cenario9_aluno_ja_matriculado_nesta_turma(self):
        """Dado aluno já na turma, então ignora e informa "Aluno já matriculado nesta turma"."""
        self.matricular()
        resposta = self.matricular()
        self.assertContains(resposta, mensagens.ALUNO_JA_NA_TURMA)
        self.assertEqual(TCCs.objects.filter(tcc_tur=self.turma).count(), 1)

    def test_cenario10_edicao_do_nome(self):
        """Dado aluno na turma, quando corrige o nome, então grava e a Matrícula fica só leitura."""
        aluno = matricular_aluno(self.turma, matricula="2026000123")
        url = reverse("cadastro:aluno_editar", args=[self.turma.pk, aluno.pk])
        formulario = self.client.get(url)
        self.assertContains(formulario, "2026000123")
        self.assertNotContains(formulario, 'name="matricula"')
        resposta = self.client.post(
            url,
            {"nome": "Nome Corrigido", "curso": "EST08MCPD", "matricula": "2099999999"},
            follow=True,
        )
        self.assertContains(resposta, mensagens.MT14_ALUNO_ATUALIZADO)
        aluno.refresh_from_db()
        self.assertEqual(aluno.alu.usu_nome, "Nome Corrigido")
        self.assertEqual(aluno.alu_matricula, "2026000123")

    def test_cenario11_matricula_em_turma_arquivada(self):
        """Dado turma arquivada, então "Matricular alunos" fica indisponível."""
        arquivada = criar_turma_de(self.professor, status=StatusTurma.ARQUIVADA)
        pagina = self.client.get(reverse("cadastro:turma", args=[arquivada.pk]))
        self.assertNotContains(pagina, reverse("cadastro:matricular", args=[arquivada.pk]))
        resposta = self.matricular(turma=arquivada)
        self.assertContains(resposta, mensagens.MT25_TURMA_ARQUIVADA)
        self.assertFalse(AlunosTurmas.objects.filter(mat_tur=arquivada).exists())

    def test_cenario13_aprovado_em_tcc1_matriculado_em_tcc2(self):
        """Dado 'Aprovado para TCC 2', quando matriculado em TCC 2, então TCC carregado, Em
        Andamento."""
        turma1 = criar_turma_de(criar_docente_ativo(), status=StatusTurma.ARQUIVADA)
        aluno = matricular_aluno(
            turma1, matricula="2026000123", status_tcc=StatusTCC.APROVADO_PARA_TCC_2
        )
        turma2 = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=SI)
        self.matricular(turma=turma2)
        novo = tcc_de(aluno, turma2)
        self.assertEqual(novo.tcc_status, StatusTCC.EM_ANDAMENTO)
        self.assertEqual(novo.tcc_titulo, "Título do trabalho")

    # ------------------------------------------------------------------ US-07, cenário 7

    def test_us07_cenario7_orientador_automatico(self):
        """Dado TCC 2 de LC, quando o aluno é matriculado, então o Docente é o Orientador."""
        turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=LC)
        self.matricular(turma=turma)
        orientacao = Orientacoes.objects.get(ori_tcc__tcc_tur=turma)
        self.assertEqual(orientacao.ori_doc_id, self.professor.pk)
        self.assertEqual(orientacao.ori_origem, OrigemOrientacao.AUTOMATICO)
        self.assertEqual(orientacao.ori_status, StatusOrientacao.ATIVA)
        for descricao, nome in ((DescricaoTurma.TCC_2, SI), (DescricaoTurma.TCC_1, EC)):
            with self.subTest(descricao=descricao, curso=nome):
                sem = criar_turma_de(self.professor, descricao=descricao, curso_nome=nome)
                self.matricular(matricula=f"20260009{len(nome):02d}", turma=sem)
                self.assertFalse(Orientacoes.objects.filter(ori_tcc__tcc_tur=sem).exists())

    # ------------------------------------------------------------------ Clarifications

    def test_conta_nova_sem_email_sem_senha_sem_link(self):
        """Spec 003, Q1: a conta nasce sem e-mail e sem senha, e nenhum link é enviado."""
        self.matricular()
        usuario = self.aluno().alu
        self.assertIsNone(usuario.usu_email)
        self.assertIsNone(usuario.password)
        self.assertEqual(len(mail.outbox), 0)

    def test_tcc_sem_proposta_e_historico_vinculo(self):
        self.matricular()
        tcc = tcc_de(self.aluno(), self.turma)
        self.assertEqual(tcc.tcc_status, StatusTCC.SEM_PROPOSTA)
        historico = HistoricoStatusTCC.objects.get(hst_tcc=tcc)
        self.assertEqual(historico.hst_gatilho, GatilhoStatusTCC.VINCULO_A_TURMA)
        self.assertIsNone(historico.hst_status_anterior)
        self.assertEqual(historico.hst_usu_id, self.professor.pk)
        self.assertEqual(historico.hst_tur_id, self.turma.pk)

    def test_q7_tcc_em_curso_noutra_turma(self):
        outra = criar_turma_de(criar_docente_ativo(), identificador="OUTRA_T01")
        matricular_aluno(outra, matricula="2026000123", status_tcc=StatusTCC.EM_ANDAMENTO)
        resposta = self.matricular()
        self.assertContains(resposta, mensagens.MT26_TCC_EM_CURSO.format(identificador="OUTRA_T01"))
        self.assertFalse(AlunosTurmas.objects.filter(mat_tur=self.turma).exists())

    def test_q7_tcc_em_turma_arquivada_permite(self):
        arquivada = criar_turma_de(criar_docente_ativo(), status=StatusTurma.ARQUIVADA)
        matricular_aluno(arquivada, matricula="2026000123", status_tcc=StatusTCC.SEM_PROPOSTA)
        self.assertContains(self.matricular(), mensagens.ALUNO_MATRICULADO)

    def test_q7_qualquer_tcc_aprovado_ou_concluido(self):
        """m5: qualquer TCC aprovado ou concluído recusa, mesmo que não seja o último."""
        arquivada = criar_turma_de(criar_docente_ativo(), status=StatusTurma.ARQUIVADA)
        aluno = matricular_aluno(arquivada, matricula="2026000123", status_tcc=StatusTCC.CONCLUIDO)
        outra = criar_turma_de(criar_docente_ativo(), status=StatusTurma.ARQUIVADA)
        matricular_aluno(outra, aluno=aluno, status_tcc=StatusTCC.REPROVADO)
        self.assertContains(self.matricular(), mensagens.MT27_TCC_CONCLUIDO)

    def test_mt28_aprovado_tcc2_em_turma_tcc1(self):
        """Q-39 (provisório): aprovado em TCC 1 matriculado em turma de TCC 1 é recusado."""
        arquivada = criar_turma_de(criar_docente_ativo(), status=StatusTurma.ARQUIVADA)
        matricular_aluno(
            arquivada, matricula="2026000123", status_tcc=StatusTCC.APROVADO_PARA_TCC_2
        )
        self.assertContains(self.matricular(), mensagens.MT28_APROVADO_EM_TURMA_TCC1)

    def test_q6_copia_do_tcc1(self):
        """Q6 e B7: TCC novo direto 'Em Andamento', dados, palavras, publicação, histórico e
        orientação (turma de TCC 2 de EC, com orientador automático)."""
        orientador1 = criar_docente_ativo()
        coorientador = criar_docente_ativo()
        turma1 = criar_turma_de(orientador1, status=StatusTurma.ARQUIVADA)
        aluno = matricular_aluno(
            turma1, matricula="2026000123", status_tcc=StatusTCC.APROVADO_PARA_TCC_2
        )
        tcc1 = tcc_de(aluno, turma1)
        agora = timezone.now()
        Orientacoes.objects.create(
            ori_tcc=tcc1,
            ori_doc=orientador1.docentes,
            ori_origem=OrigemOrientacao.PEDIDO_ACEITO,
            ori_status=StatusOrientacao.ATIVA,
            ori_data_inicio=agora,
        )
        for docente in (coorientador, self.professor):
            Coorientacoes.objects.create(
                coo_tcc=tcc1,
                coo_doc=docente.docentes,
                coo_status=StatusCoorientacao.ATIVA,
                coo_data_inicio=agora,
            )
        PalavrasChaveTCC.objects.create(pal_tcc=tcc1, pal_palavra="Django")
        Artigos.objects.create(
            art=tcc1, art_link_doi="https://doi.org/10.1/x", art_veiculo_publicacao="Revista"
        )
        turma2 = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        self.matricular(turma=turma2)
        novo = tcc_de(aluno, turma2)
        self.assertEqual(novo.tcc_status, StatusTCC.EM_ANDAMENTO)
        historicos = list(HistoricoStatusTCC.objects.filter(hst_tcc=novo))
        self.assertEqual(len(historicos), 1)
        self.assertEqual(historicos[0].hst_status_anterior, StatusTCC.APROVADO_PARA_TCC_2)
        self.assertEqual(historicos[0].hst_gatilho, GatilhoStatusTCC.TRANSFERENCIA_PARA_TCC_2)
        self.assertEqual(
            list(
                PalavrasChaveTCC.objects.filter(pal_tcc=novo).values_list("pal_palavra", flat=True)
            ),
            ["Django"],
        )
        self.assertEqual(Artigos.objects.get(art=novo).art_veiculo_publicacao, "Revista")
        self.assertEqual(
            Orientacoes.objects.get(ori_tcc=tcc1).ori_status, StatusOrientacao.ENCERRADA
        )
        ativa = Orientacoes.objects.get(ori_tcc=novo, ori_status=StatusOrientacao.ATIVA)
        self.assertEqual(
            (ativa.ori_doc_id, ativa.ori_origem), (self.professor.pk, OrigemOrientacao.AUTOMATICO)
        )
        self.assertEqual(
            list(Coorientacoes.objects.filter(coo_tcc=novo).values_list("coo_doc_id", flat=True)),
            [coorientador.pk],
        )
        self.assertFalse(
            Coorientacoes.objects.filter(coo_tcc=tcc1, coo_status=StatusCoorientacao.ATIVA).exists()
        )
        tcc1.refresh_from_db()
        self.assertEqual(tcc1.tcc_status, StatusTCC.APROVADO_PARA_TCC_2)

    def test_q6_copia_em_tcc2_de_si_mantem_orientador(self):
        orientador1 = criar_docente_ativo()
        turma1 = criar_turma_de(orientador1, curso_nome=SI, status=StatusTurma.ARQUIVADA)
        aluno = matricular_aluno(
            turma1, matricula="2026000123", status_tcc=StatusTCC.APROVADO_PARA_TCC_2
        )
        Orientacoes.objects.create(
            ori_tcc=tcc_de(aluno, turma1),
            ori_doc=orientador1.docentes,
            ori_origem=OrigemOrientacao.PEDIDO_ACEITO,
            ori_status=StatusOrientacao.ATIVA,
            ori_data_inicio=timezone.now(),
        )
        turma2 = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=SI)
        self.matricular(turma=turma2)
        ativa = Orientacoes.objects.get(
            ori_tcc=tcc_de(aluno, turma2), ori_status=StatusOrientacao.ATIVA
        )
        self.assertEqual(
            (ativa.ori_doc_id, ativa.ori_origem), (orientador1.pk, OrigemOrientacao.PEDIDO_ACEITO)
        )

    def test_q16_conta_inativa_matriculada_com_aviso_mt29(self):
        arquivada = criar_turma_de(criar_docente_ativo(), status=StatusTurma.ARQUIVADA)
        aluno = matricular_aluno(arquivada, matricula="2026000123", status_tcc=StatusTCC.REPROVADO)
        Usuarios.objects.filter(pk=aluno.pk).update(usu_status=StatusConta.INATIVA)
        resposta = self.matricular()
        self.assertContains(resposta, mensagens.ALUNO_MATRICULADO)
        self.assertContains(resposta, mensagens.MT29_CONTA_NAO_ATIVA.format(status="Inativa"))
        self.assertEqual(Usuarios.objects.get(pk=aluno.pk).usu_status, StatusConta.INATIVA)

    def test_curso_reconhecido_e_nao_reconhecido(self):
        self.matricular(matricula="2026000123", curso="EST08MCPD")
        self.matricular(matricula="2026000124", curso="EST99XXXX")
        pagina = self.client.get(reverse("cadastro:turma", args=[self.turma.pk]))
        self.assertContains(pagina, "Engenharia de Computação")
        self.assertContains(pagina, mensagens.CURSO_NAO_RECONHECIDO)

    def test_alerta_mt13_curso_divergente(self):
        resposta = self.matricular(curso="EST31MSII")
        self.assertContains(resposta, mensagens.ALUNO_MATRICULADO)
        self.assertContains(
            resposta,
            mensagens.MT13_CURSO_DIVERGENTE.format(
                curso_aluno="Sistemas de Informação", curso_turma="Engenharia de Computação"
            ),
        )

    def test_mt11_nome_com_letra_nao_latina_ou_simbolo(self):
        """N6: grego, sinal de multiplicação e ordinal recusados; acento decomposto aceito."""
        for nome in ("Ανδρέας Silva", "Ana × Souza", "Maria 2ª", "Ana123"):
            with self.subTest(nome=nome):
                self.assertContains(self.matricular(nome=nome), mensagens.MT11_NOME_COMPLETO)
        self.assertContains(self.matricular(nome="José Conceição"), mensagens.ALUNO_MATRICULADO)
        self.assertEqual(self.aluno().alu.usu_nome, "José Conceição")

    def test_mt11_nome_acima_de_150(self):
        self.assertContains(self.matricular(nome="A" * 151), mensagens.MT11_NOME_COMPLETO)

    def test_mt12_curso_formato(self):
        for curso in ("est08mcpd", "Engenharia de Computação", "A" * 21):
            with self.subTest(curso=curso):
                self.assertContains(self.matricular(curso=curso), mensagens.MT12_CURSO)

    def test_m14_campos_vazios(self):
        self.assertContains(
            self.matricular(matricula="", nome="", curso=""), mensagens.M14_CAMPO_OBRIGATORIO
        )

    def test_q17_cria_registros_das_entregas(self):
        criar_entrega(self.turma)
        criar_entrega(self.turma)
        self.matricular()
        self.assertEqual(EntregasMarcos.objects.filter(ent_alu=self.aluno()).count(), 2)

    def test_q18_rematricula_reaproveita_registro_zerado(self):
        entrega = criar_entrega(self.turma)
        aluno = criar_aluno_novo(matricula="2026000123")
        antigo = entrega_do_aluno(entrega, aluno, status=StatusEntrega.ENTREGUE)
        criar_envio(antigo)
        self.matricular()
        antigo.refresh_from_db()
        self.assertEqual(antigo.ent_status, StatusEntrega.AGUARDANDO_ENVIO)
        self.assertEqual(antigo.historicoenviosentregas_set.count(), 1)

    def test_aluno_existente_mantem_nome_e_curso(self):
        criar_aluno_novo(matricula="2026000123", nome="Nome Original", codigo_curso="EST31MSII")
        self.matricular(nome="Outro Nome", curso="EST08MCPD")
        aluno = self.aluno()
        self.assertEqual(aluno.alu.usu_nome, "Nome Original")
        self.assertEqual(aluno.alu_codigo_curso, "EST31MSII")

    def test_editar_aluno_de_outra_turma_404(self):
        """I-7: o alu_id precisa ser de aluno matriculado nesta turma."""
        outro = matricular_aluno(criar_turma_de(criar_docente_ativo()))
        url = reverse("cadastro:aluno_editar", args=[self.turma.pk, outro.pk])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(
            self.client.post(url, {"nome": "X", "curso": "EST08MCPD"}).status_code, 404
        )

    def test_editar_aluno_valida_nome(self):
        aluno = matricular_aluno(self.turma)
        url = reverse("cadastro:aluno_editar", args=[self.turma.pk, aluno.pk])
        resposta = self.client.post(url, {"nome": "Nome 2", "curso": "EST08MCPD"})
        self.assertContains(resposta, mensagens.MT11_NOME_COMPLETO)

    def test_matricula_concorrente_vira_aluno_existente(self):
        """m7: outra requisição cria a mesma matrícula no meio; vira aluno já cadastrado."""
        criar_aluno_novo(matricula="2026000123")
        original = services_turmas._aluno_travado
        chamadas = []

        def nao_ve_na_primeira(matricula):
            chamadas.append(matricula)
            return None if len(chamadas) == 1 else original(matricula)

        # A primeira busca "não vê" o aluno criado pela outra requisição; a criação esbarra na
        # unicidade e o serviço segue como aluno já cadastrado.
        with mock.patch.object(services_turmas, "_aluno_travado", side_effect=nao_ve_na_primeira):
            resposta = self.matricular()
        self.assertEqual(len(chamadas), 2)
        self.assertContains(resposta, mensagens.ALUNO_MATRICULADO)
        self.assertEqual(Alunos.objects.filter(alu_matricula="2026000123").count(), 1)

    def test_banco_recusa_matricula_repetida(self):
        criar_aluno_novo(matricula="2026000777")
        with self.assertRaises(IntegrityError):
            criar_aluno_novo(matricula="2026000777")
