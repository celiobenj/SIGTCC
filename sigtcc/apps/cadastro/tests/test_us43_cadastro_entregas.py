"""Testes da US-43 (Professor da Disciplina cadastra as entregas da turma) — spec 005.

T017 (Phase 5): os 5 cenários de aceite da User Story 3 do `spec.md` (cadastro; tipos por etapa
TCC 1/TCC 2; aluno vinculado depois do cadastro; tipo repetido; turma arquivada ou usuário sem
permissão), mais os cenários da US-43 original (`docs/fonte/Historias_de_Usuario_v3_4.md`): tipo
Proposta sem campo de link, tipo Versão Final define o prazo e cancelamento do cadastro — 6
cenários de aceite no total, mais os 3 de exceção (tipo repetido, turma arquivada, usuário sem
permissão). Escritos antes de `services_entregas.cadastrar_entrega`,
`forms_entregas.CadastroEntregaForm` e `views_entregas.entregas`/`entrega_cadastrar`: devem
falhar até a implementação (T018, T019).

[US-43][RBN-CAD-09.1][RBN-CAD-09.6][FR-013 a FR-017][research C6]
"""

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services_entregas
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    StatusConta,
    StatusEntrega,
    StatusTCC,
    StatusTurma,
    TipoEntrega,
)
from sigtcc.apps.cadastro.forms_entregas import CadastroEntregaForm
from sigtcc.apps.cadastro.models import EntregasMarcos, Notificacoes, TurmasMarcos
from sigtcc.apps.cadastro.services_turmas import TurmaArquivada, matricular_individual
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo, criar_secretaria
from sigtcc.apps.cadastro.tests.apoio_tcc import cadastrar_entrega
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    TesteTurmas,
    criar_turma_de,
    matricular_aluno,
)


def _dados(tipo=TipoEntrega.DOCUMENTO_PARA_DEFESA, titulo="Entrega do Documento", dias=10, **extra):
    """Dados válidos de cadastro, prontos para `services_entregas.cadastrar_entrega`. [US-43]"""
    dados = {
        "tipo": tipo,
        "titulo": titulo,
        "instrucao": "",
        "data_limite": timezone.now() + timedelta(days=dias),
    }
    dados.update(extra)
    return dados


class CadastrarEntregaServiceTest(TesteTurmas):
    """`services_entregas.cadastrar_entrega`: cenários 1, 3, 4, 6 e exceções do serviço.

    [US-43][RBN-CAD-09.1][RBN-CAD-09.6][FR-013 a FR-016][research C6]
    """

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        self.aluno1 = matricular_aluno(
            self.turma, status_tcc=StatusTCC.SEM_PROPOSTA, status_conta=StatusConta.ATIVA
        )
        self.aluno2 = matricular_aluno(
            self.turma, status_tcc=StatusTCC.SEM_PROPOSTA, status_conta=StatusConta.ATIVA
        )

    def test_cenario1_cadastro_cria_entrega_com_aguardando_envio_e_notifica_cada_aluno(self):
        """Cenário 1: a entrega aparece com "Aguardando Envio" para cada aluno, e cada um deles
        é notificado com o Título e a Data Limite (passo 7 da US original).
        [US-43][FR-013][FR-015]
        """
        entrega = services_entregas.cadastrar_entrega(
            self.professor, self.turma.pk, _dados(titulo="Entrega do Documento")
        )
        self.assertEqual(entrega.tma_titulo, "Entrega do Documento")
        self.assertEqual(entrega.tma_tipo, TipoEntrega.DOCUMENTO_PARA_DEFESA)
        for aluno in (self.aluno1, self.aluno2):
            registro = EntregasMarcos.objects.get(ent_tma=entrega, ent_alu=aluno)
            self.assertEqual(registro.ent_status, StatusEntrega.AGUARDANDO_ENVIO)
            notificacao = Notificacoes.objects.get(not_usu=aluno.alu)
            self.assertIn("Entrega do Documento", notificacao.not_mensagem)

    def test_cenario3_entrega_tipo_proposta_e_criada_sem_campo_de_link(self):
        """Cenário 3 (US original): a entrega do tipo Proposta é criada normalmente; o model
        `Turmas_Marcos` não tem nenhum campo de link — a Proposta é cumprida ao salvar a Proposta
        (US-13), nunca por um link de entrega (US-15).
        [US-43][FR-013][research C6]
        """
        entrega = services_entregas.cadastrar_entrega(
            self.professor, self.turma.pk, _dados(tipo=TipoEntrega.PROPOSTA, titulo="Proposta")
        )
        self.assertEqual(entrega.tma_tipo, TipoEntrega.PROPOSTA)
        self.assertFalse(hasattr(entrega, "tma_link"))
        registro = EntregasMarcos.objects.get(ent_tma=entrega, ent_alu=self.aluno1)
        self.assertEqual(registro.ent_status, StatusEntrega.AGUARDANDO_ENVIO)

    def test_cenario4_entrega_tipo_versao_final_define_o_prazo(self):
        """Cenário 4 (US original): a Data Limite informada passa a ser o prazo da Versão Final.

        [US-43][FR-013][research C6]
        """
        turma_tcc2 = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        matricular_aluno(turma_tcc2, status_tcc=StatusTCC.APROVADO, status_conta=StatusConta.ATIVA)
        prazo = timezone.now() + timedelta(days=30)
        entrega = services_entregas.cadastrar_entrega(
            self.professor,
            turma_tcc2.pk,
            _dados(tipo=TipoEntrega.VERSAO_FINAL, titulo="Versão Final", dias=30),
        )
        self.assertEqual(entrega.tma_tipo, TipoEntrega.VERSAO_FINAL)
        self.assertEqual(entrega.tma_data_limite.date(), prazo.date())

    def test_cenario9_tipo_repetido_nao_salva_e_retorna_a_mensagem_exata(self):
        """Cenário 9/exceção E3 (US original) e Cenário 4 do `spec.md`: tipo repetido (exceto
        "Outra") não salva e devolve "A turma já tem uma entrega deste tipo".
        [US-43][FR-014]
        """
        cadastrar_entrega(self.turma, tipo=TipoEntrega.DOCUMENTO_PARA_DEFESA)
        with self.assertRaises(services_entregas.ErroEntrega) as contexto:
            services_entregas.cadastrar_entrega(
                self.professor, self.turma.pk, _dados(titulo="Outra tentativa")
            )
        self.assertEqual(contexto.exception.mensagem, mensagens.ENTREGA_TIPO_REPETIDO)
        self.assertEqual(
            TurmasMarcos.objects.filter(
                tma_tur=self.turma, tma_tipo=TipoEntrega.DOCUMENTO_PARA_DEFESA
            ).count(),
            1,
        )

    def test_tipo_outra_permite_repetir(self):
        """O tipo "Outra" não entra na `UniqueConstraint` (research C6). [US-43][FR-014]"""
        cadastrar_entrega(self.turma, tipo=TipoEntrega.OUTRA, titulo="Seminário 1")
        entrega2 = services_entregas.cadastrar_entrega(
            self.professor, self.turma.pk, _dados(tipo=TipoEntrega.OUTRA, titulo="Seminário 2")
        )
        self.assertEqual(entrega2.tma_titulo, "Seminário 2")
        self.assertEqual(
            TurmasMarcos.objects.filter(tma_tur=self.turma, tma_tipo=TipoEntrega.OUTRA).count(), 2
        )

    def test_aluno_com_participacao_encerrada_nao_recebe_o_registro_nem_a_notificacao(self):
        """Participação encerrada (Desistente, Reprovado, Jubilado) não entra no cadastro.

        [US-43][FR-015][RBN-CAD-08.5]
        """
        desistente = matricular_aluno(self.turma, status_tcc=StatusTCC.DESISTENTE)
        entrega = services_entregas.cadastrar_entrega(
            self.professor, self.turma.pk, _dados(titulo="Entrega")
        )
        self.assertFalse(
            EntregasMarcos.objects.filter(ent_tma=entrega, ent_alu=desistente).exists()
        )
        self.assertFalse(Notificacoes.objects.filter(not_usu=desistente.alu).exists())

    def test_entrega_com_data_limite_ja_vencida_cria_registro_nao_entregue(self):
        """Data Limite já vencida no momento do cadastro: "Não Entregue" (research C6, mesma
        regra de `criar_entregas_do_aluno`, fluxo alternativo E da US original).
        [US-43][FR-015][FR-016]
        """
        entrega = services_entregas.cadastrar_entrega(
            self.professor, self.turma.pk, _dados(titulo="Entrega", dias=-1)
        )
        registro = EntregasMarcos.objects.get(ent_tma=entrega, ent_alu=self.aluno1)
        self.assertEqual(registro.ent_status, StatusEntrega.NAO_ENTREGUE)

    def test_cenario10_turma_arquivada_nao_cadastra(self):
        """Cenário 10/exceção E4 (US original) e Cenário 5 do `spec.md`: turma arquivada não
        aceita o cadastro.
        [US-43][FR-017]
        """
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save(update_fields=["tur_status"])
        with self.assertRaises(TurmaArquivada):
            services_entregas.cadastrar_entrega(
                self.professor, self.turma.pk, _dados(titulo="Entrega")
            )
        self.assertFalse(TurmasMarcos.objects.filter(tma_tur=self.turma).exists())


class Cenario6AlunoVinculadoDepoisDoCadastroTest(TesteTurmas):
    """Cenário 6 (US original) e Cenário 3 do `spec.md`: aluno vinculado à turma depois do
    cadastro da entrega recebe "Aguardando Envio" (índice Q-41, `criar_entregas_do_aluno`).

    [US-43][FR-016][Q-41]
    """

    def test_aluno_matriculado_depois_do_cadastro_recebe_aguardando_envio(self):
        professor = criar_docente_ativo()
        turma = criar_turma_de(professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        entrega = services_entregas.cadastrar_entrega(
            professor, turma.pk, _dados(titulo="Entrega do Documento")
        )
        resultado = matricular_individual(
            professor, turma.pk, "2026200099", "Aluno Novo", "EST08MCPD"
        )
        registro = EntregasMarcos.objects.get(ent_tma=entrega, ent_alu=resultado.aluno)
        self.assertEqual(registro.ent_status, StatusEntrega.AGUARDANDO_ENVIO)


class CadastroEntregaFormTest(TesteTurmas):
    """Cenário 2 do `spec.md`: a lista Tipo é restrita pela etapa da turma (FR-013).

    [US-43][FR-013]
    """

    def test_turma_tcc1_lista_proposta_documento_e_outra_sem_versao_final(self):
        professor = criar_docente_ativo()
        turma = criar_turma_de(professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        formulario = CadastroEntregaForm(turma=turma)
        valores = [valor for valor, _ in formulario.fields["tipo"].choices]
        self.assertEqual(
            valores, [TipoEntrega.PROPOSTA, TipoEntrega.DOCUMENTO_PARA_DEFESA, TipoEntrega.OUTRA]
        )

    def test_turma_tcc2_lista_documento_versao_final_e_outra_sem_proposta(self):
        professor = criar_docente_ativo()
        turma = criar_turma_de(professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        formulario = CadastroEntregaForm(turma=turma)
        valores = [valor for valor, _ in formulario.fields["tipo"].choices]
        self.assertEqual(
            valores,
            [TipoEntrega.DOCUMENTO_PARA_DEFESA, TipoEntrega.VERSAO_FINAL, TipoEntrega.OUTRA],
        )

    def test_data_limite_anterior_a_hoje_e_recusada(self):
        """E2/Cenário 8 (US original): Data Limite anterior à data do cadastro não salva e
        destaca o campo. [US-43][FR-013]
        """
        professor = criar_docente_ativo()
        turma = criar_turma_de(professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        ontem = (timezone.now() - timedelta(days=1)).date()
        formulario = CadastroEntregaForm(
            data={
                "tipo": TipoEntrega.DOCUMENTO_PARA_DEFESA,
                "titulo": "Entrega",
                "instrucao": "",
                "data_limite": ontem.isoformat(),
            },
            turma=turma,
        )
        self.assertFalse(formulario.is_valid())
        self.assertIn("data_limite", formulario.errors)


class EntregasViewTest(TesteTurmas):
    """Views `entregas` (lista) e `entrega_cadastrar` (GET/POST): cenários 1, 5 e cancelamento,
    mais os cenários de exceção de permissão e turma arquivada.

    [US-43][FR-013][FR-017][contracts/rotas.md]
    """

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        self.aluno = matricular_aluno(
            self.turma, status_tcc=StatusTCC.SEM_PROPOSTA, status_conta=StatusConta.ATIVA
        )

    def url_lista(self):
        return reverse("cadastro:entregas", args=[self.turma.pk])

    def url_cadastrar(self):
        return reverse("cadastro:entrega_cadastrar", args=[self.turma.pk])

    def test_lista_vazia_mostra_a_mensagem_e_o_botao_cadastrar_atividade(self):
        self.client.force_login(self.professor)
        resposta = self.client.get(self.url_lista())
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, mensagens.NENHUMA_ENTREGA_CADASTRADA)
        self.assertContains(resposta, "Cadastrar atividade")
        self.assertContains(resposta, self.url_cadastrar())

    def test_cenario1_professor_cadastra_entrega_por_post(self):
        self.client.force_login(self.professor)
        resposta = self.client.post(
            self.url_cadastrar(),
            {
                "tipo": TipoEntrega.DOCUMENTO_PARA_DEFESA,
                "titulo": "Entrega do Documento",
                "instrucao": "",
                "data_limite": (timezone.now() + timedelta(days=10)).date().isoformat(),
            },
            follow=True,
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, mensagens.ENTREGA_CADASTRADA)
        self.assertContains(resposta, "Entrega do Documento")
        self.assertTrue(
            EntregasMarcos.objects.filter(ent_tma__tma_tur=self.turma, ent_alu=self.aluno).exists()
        )

    def test_cancelamento_get_nao_cria_entrega_e_tem_o_link_cancelar(self):
        """Cenário 5 (US original): a janela Cadastrar atividade tem Cancelar; sem acionar
        Cadastrar, nenhuma entrega é criada. [US-43]
        """
        self.client.force_login(self.professor)
        resposta = self.client.get(self.url_cadastrar())
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Cancelar")
        self.assertContains(resposta, self.url_lista())
        self.assertEqual(TurmasMarcos.objects.filter(tma_tur=self.turma).count(), 0)

    def test_tipo_repetido_por_post_mostra_a_mensagem_no_formulario(self):
        cadastrar_entrega(self.turma, tipo=TipoEntrega.DOCUMENTO_PARA_DEFESA)
        self.client.force_login(self.professor)
        resposta = self.client.post(
            self.url_cadastrar(),
            {
                "tipo": TipoEntrega.DOCUMENTO_PARA_DEFESA,
                "titulo": "Outra tentativa",
                "instrucao": "",
                "data_limite": (timezone.now() + timedelta(days=10)).date().isoformat(),
            },
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, mensagens.ENTREGA_TIPO_REPETIDO)
        self.assertEqual(
            TurmasMarcos.objects.filter(
                tma_tur=self.turma, tma_tipo=TipoEntrega.DOCUMENTO_PARA_DEFESA
            ).count(),
            1,
        )

    def test_cenario5_turma_arquivada_lista_so_para_consulta_sem_o_botao(self):
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save(update_fields=["tur_status"])
        self.client.force_login(self.professor)
        resposta = self.client.get(self.url_lista())
        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(resposta, "Cadastrar atividade")

    def test_turma_arquivada_redireciona_o_cadastro_direto_com_a_mt25(self):
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save(update_fields=["tur_status"])
        self.client.force_login(self.professor)
        resposta = self.client.get(self.url_cadastrar(), follow=True)
        self.assertRedirects(resposta, reverse("cadastro:turma", args=[self.turma.pk]))
        self.assertContains(resposta, mensagens.MT25_TURMA_ARQUIVADA)

    def test_cenario11_docente_sem_permissao_recebe_403_na_lista_e_no_cadastro(self):
        """Cenário 11/exceção E5 (US original): Docente que não é o Professor da Disciplina não
        cadastra entregas (FR-017).
        [US-43][FR-017]
        """
        outro_docente = criar_docente_ativo()
        self.client.force_login(outro_docente)
        self.assertEqual(self.client.get(self.url_lista()).status_code, 403)
        self.assertEqual(self.client.get(self.url_cadastrar()).status_code, 403)

    def test_secretaria_do_curso_recebe_403(self):
        """A lista de entregas é restrita ao Professor da Disciplina (contracts/rotas.md), nunca
        à Secretaria, mesmo que ela consulte a turma (spec 004, Q9). [US-43][FR-017]
        """
        secretaria = criar_secretaria()
        self.client.force_login(secretaria)
        self.assertEqual(self.client.get(self.url_lista()).status_code, 403)

    def test_aluno_recebe_403(self):
        self.client.force_login(self.aluno.alu)
        self.assertEqual(self.client.get(self.url_lista()).status_code, 403)
        self.assertEqual(self.client.get(self.url_cadastrar()).status_code, 403)

    def test_turma_inexistente_recebe_404(self):
        self.client.force_login(self.professor)
        self.assertEqual(self.client.get(reverse("cadastro:entregas", args=[0])).status_code, 404)
        self.assertEqual(
            self.client.get(reverse("cadastro:entrega_cadastrar", args=[0])).status_code, 404
        )


class EmailNovaEntregaTest(TesteTurmas):
    """FR-015 (US-43, passo 7): além da notificação, um e-mail com o Título e a Data Limite a
    cada aluno com e-mail cadastrado, depois do commit (Phase 12, T045; MF-11, Q-84).

    [US-43][RBN-CAD-09.6][FR-015][Q-84]
    """

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        self.com_email = matricular_aluno(
            self.turma, status_tcc=StatusTCC.SEM_PROPOSTA, status_conta=StatusConta.ATIVA
        )
        self.com_email.alu.usu_email = "aluno.email@uea.edu.br"
        self.com_email.alu.save(update_fields=["usu_email"])
        self.sem_email = matricular_aluno(
            self.turma, status_tcc=StatusTCC.SEM_PROPOSTA, status_conta=StatusConta.ATIVA
        )

    def test_email_com_titulo_e_data_limite_so_para_quem_tem_email(self):
        from django.core import mail

        with self.captureOnCommitCallbacks(execute=True):
            entrega = services_entregas.cadastrar_entrega(
                self.professor, self.turma.pk, _dados(titulo="Entrega do Documento")
            )
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ["aluno.email@uea.edu.br"])
        self.assertEqual(email.subject, mensagens.MF11_ASSUNTO_NOVA_ENTREGA)
        self.assertIn("Entrega do Documento", email.body)
        self.assertIn(entrega.tma_data_limite.strftime("%d/%m/%Y"), email.body)
        # A notificação no sistema continua para os dois.
        self.assertEqual(Notificacoes.objects.count(), 2)

    def test_falha_no_envio_nao_desfaz_o_cadastro(self):
        from unittest import mock

        from sigtcc.apps.cadastro import services

        with mock.patch.object(services, "send_mail", side_effect=OSError("smtp fora")):
            with self.assertLogs("sigtcc.acesso"):
                with self.captureOnCommitCallbacks(execute=True):
                    entrega = services_entregas.cadastrar_entrega(
                        self.professor, self.turma.pk, _dados()
                    )
        self.assertTrue(TurmasMarcos.objects.filter(pk=entrega.pk).exists())
