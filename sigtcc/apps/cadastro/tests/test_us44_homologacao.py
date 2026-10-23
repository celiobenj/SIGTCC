"""Testes da US-44 (Professor homologa ou devolve a Versão Final) — spec 005, Phase 9, T029.

Os 10 cenários da US-44 (homologação; parecer Aprovado sem correções; correções conferidas em
Sistemas de Informação; acesso pela notificação; devolução para ajuste, com a MF-02; acesso sem
login; correções ainda não conferidas; devolução sem mensagem; Versão Final ainda não enviada;
usuário sem permissão), mais Secretaria sem acesso, turma arquivada (MT-25), turma de TCC 1 e o
registro do Professor no histórico do Status. Escritos antes de
`services_entregas.homologar_versao_final`/`devolver_versao_final` (T030) e da view
`aluno_versao_final` (T031): devem falhar até a implementação.

[US-44][RBN-CAD-09.3][RBN-CAD-09.5][FR-028 a FR-030]
"""

from datetime import timedelta
from urllib.parse import parse_qs, urlparse

from django.http import Http404
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services_entregas
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    GatilhoStatusTCC,
    StatusConta,
    StatusEntrega,
    StatusTCC,
    StatusTurma,
    TipoEntrega,
)
from sigtcc.apps.cadastro.models import (
    EntregasMarcos,
    HistoricoEnviosEntregas,
    HistoricoStatusTCC,
    Notificacoes,
)
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo, criar_secretaria
from sigtcc.apps.cadastro.tests.apoio_tcc import cadastrar_entrega, enviar_link
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    SI,
    TesteTurmas,
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)

LINK_PDF = "https://drive.google.com/versao-final.pdf"
MENSAGEM = "Falta a ficha catalográfica"


class HomologacaoTestBase(TesteTurmas):
    """Turma de TCC 2 (Engenharia de Computação, por padrão) com a Versão Final enviada."""

    curso = EC
    status_tcc = StatusTCC.APROVADO
    enviada = True

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(
            self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=self.curso
        )
        self.secretaria = criar_secretaria(curso=self.turma.tur_cur)
        self.aluno = matricular_aluno(
            self.turma, status_tcc=self.status_tcc, status_conta=StatusConta.ATIVA
        )
        self.versao_final = cadastrar_entrega(
            self.turma,
            tipo=TipoEntrega.VERSAO_FINAL,
            titulo="Versão Final",
            data_limite=timezone.now() + timedelta(days=5),
        )
        EntregasMarcos.objects.create(
            ent_tma=self.versao_final,
            ent_alu=self.aluno,
            ent_status=StatusEntrega.AGUARDANDO_ENVIO,
        )
        if self.enviada:
            enviar_link(self.versao_final, self.aluno, LINK_PDF)
            self.mudar_status_entrega(StatusEntrega.ENTREGUE)

    def registro(self):
        return EntregasMarcos.objects.get(ent_tma=self.versao_final, ent_alu=self.aluno)

    def mudar_status_entrega(self, status, **campos):
        EntregasMarcos.objects.filter(ent_tma=self.versao_final, ent_alu=self.aluno).update(
            ent_status=status, **campos
        )

    def homologar(self, professor=None):
        return services_entregas.homologar_versao_final(
            professor or self.professor, self.turma.pk, self.aluno.pk
        )

    def devolver(self, mensagem=MENSAGEM):
        return services_entregas.devolver_versao_final(
            self.professor, self.turma.pk, self.aluno.pk, mensagem
        )

    def url(self, turma=None):
        return reverse(
            "cadastro:aluno_versao_final", args=[(turma or self.turma).pk, self.aluno.pk]
        )

    def abrir(self, usuario=None):
        self.client.force_login(usuario or self.professor)
        return self.client.get(self.url())


class HomologacaoServiceTest(HomologacaoTestBase):
    """`homologar_versao_final` e `devolver_versao_final` (T030). [US-44][FR-028][FR-029]"""

    def test_cenario1_homologacao_conclui_o_tcc_e_notifica_a_secretaria(self):
        """Cenário 1: "Homologada", TCC "Concluído" com o gatilho e o Professor no histórico,
        data da avaliação gravada e a Secretaria do curso notificada.
        """
        self.homologar()
        registro = self.registro()
        self.assertEqual(registro.ent_status, StatusEntrega.HOMOLOGADA)
        self.assertIsNotNone(registro.ent_data_avaliacao)
        tcc = tcc_de(self.aluno, self.turma)
        self.assertEqual(tcc.tcc_status, StatusTCC.CONCLUIDO)
        historico = HistoricoStatusTCC.objects.filter(hst_tcc=tcc).latest("hst_id")
        self.assertEqual(historico.hst_gatilho, GatilhoStatusTCC.HOMOLOGACAO_DA_VERSAO_FINAL)
        self.assertEqual(historico.hst_usu, self.professor)
        self.assertTrue(Notificacoes.objects.filter(not_usu=self.secretaria).exists())

    def test_cenario2_parecer_aprovado_sem_correcoes_conclui(self):
        """Cenário 2 (fluxo alternativo A): parecer Aprovado -> TCC "Concluído"."""
        self.homologar()
        self.assertEqual(tcc_de(self.aluno, self.turma).tcc_status, StatusTCC.CONCLUIDO)

    def test_cenario5_devolucao_grava_a_mensagem_e_notifica_o_aluno(self):
        """Cenário 5 (fluxo alternativo D): "Devolvida para Ajuste", mensagem gravada, Aluno
        notificado com ela, Status do TCC sem mudança.
        """
        self.devolver()
        registro = self.registro()
        self.assertEqual(registro.ent_status, StatusEntrega.DEVOLVIDA_PARA_AJUSTE)
        self.assertEqual(registro.ent_feedback, MENSAGEM)
        self.assertIsNotNone(registro.ent_data_avaliacao)
        notificacao = Notificacoes.objects.get(not_usu=self.aluno.alu)
        self.assertIn(MENSAGEM, notificacao.not_mensagem)
        self.assertEqual(tcc_de(self.aluno, self.turma).tcc_status, StatusTCC.APROVADO)

    def test_cenario9_versao_final_nao_enviada_recusa(self):
        """Cenário 9 (E4): sem envio, nem homologa nem devolve."""
        self.mudar_status_entrega(StatusEntrega.AGUARDANDO_ENVIO)
        with self.assertRaises(Http404):
            self.homologar()
        with self.assertRaises(Http404):
            self.devolver()
        self.assertEqual(self.registro().ent_status, StatusEntrega.AGUARDANDO_ENVIO)

    def test_devolvida_aguardando_reenvio_nao_homologa(self):
        """Depois da devolução, só um novo envio (US-29, fluxo E) libera a homologação."""
        self.devolver()
        with self.assertRaises(Http404):
            self.homologar()

    def test_cenario10_outro_docente_nao_homologa(self):
        """Cenário 10 (E5): um Docente que não é o Professor da Disciplina não homologa."""
        from django.core.exceptions import PermissionDenied

        with self.assertRaises(PermissionDenied):
            self.homologar(professor=criar_docente_ativo())
        self.assertEqual(self.registro().ent_status, StatusEntrega.ENTREGUE)

    def test_turma_arquivada_nao_homologa(self):
        """Turma arquivada: nenhuma ação (MT-25 na view)."""
        from sigtcc.apps.cadastro.services_turmas import TurmaArquivada

        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save(update_fields=["tur_status"])
        with self.assertRaises(TurmaArquivada):
            self.homologar()


class CorrecoesConferidasSITest(HomologacaoTestBase):
    """Sistemas de Informação com parecer "Aprovado com Correções" (FR-029).

    [US-44][RBN-CAD-09.5][FR-029]
    """

    curso = SI
    status_tcc = StatusTCC.APROVADO_COM_CORRECOES

    def test_cenario7_correcoes_nao_conferidas_bloqueiam_a_homologacao(self):
        """Cenário 7 (E2): sem "Correções Conferidas", Homologar indisponível e nada muda."""
        with self.assertRaises(Http404):
            self.homologar()
        self.assertEqual(self.registro().ent_status, StatusEntrega.ENTREGUE)
        resposta = self.abrir()
        self.assertNotContains(resposta, 'value="homologar"')
        self.assertContains(resposta, "Devolver para Ajuste")

    def test_cenario3_correcoes_conferidas_liberam_a_homologacao(self):
        """Cenário 3 (fluxo alternativo B): com "Correções Conferidas" gravado pela spec 006,
        o botão Homologar fica disponível e a homologação conclui o TCC.
        """
        self.mudar_status_entrega(
            StatusEntrega.ENTREGUE, ent_correcoes_conferidas_em=timezone.now()
        )
        self.assertContains(self.abrir(), 'value="homologar"')
        self.homologar()
        self.assertEqual(tcc_de(self.aluno, self.turma).tcc_status, StatusTCC.CONCLUIDO)


class SIAprovadoSemCorrecoesTest(HomologacaoTestBase):
    """Sistemas de Informação com parecer "Aprovado": não exige "Correções Conferidas"."""

    curso = SI
    status_tcc = StatusTCC.APROVADO

    def test_homologa_sem_correcoes_conferidas(self):
        self.homologar()
        self.assertEqual(self.registro().ent_status, StatusEntrega.HOMOLOGADA)


class HomologacaoViewTest(HomologacaoTestBase):
    """View `aluno_versao_final` (T031). [US-44][FR-028][FR-030][contracts/rotas.md]"""

    def test_cenario1_homologar_pela_tela(self):
        """Cenário 1: o Professor fica na tela do aluno com "Versão Final homologada", o status
        "Homologada" e sem os botões.
        """
        resposta = self.abrir()
        self.assertContains(resposta, LINK_PDF)
        self.assertContains(resposta, 'value="homologar"')
        self.assertContains(resposta, "Devolver para Ajuste")
        resposta = self.client.post(self.url(), {"acao": "homologar"}, follow=True)
        self.assertEqual(resposta.redirect_chain[-1][0], self.url())
        self.assertContains(resposta, mensagens.VERSAO_FINAL_HOMOLOGADA)
        self.assertContains(resposta, StatusEntrega.HOMOLOGADA.label)
        self.assertNotContains(resposta, 'value="homologar"')
        self.assertNotContains(resposta, "Devolver para Ajuste")

    def test_cenario4_acesso_pela_notificacao_do_envio(self):
        """Cenário 4 (fluxo alternativo C): a notificação do envio da Versão Final abre a tela
        do aluno na seção Versão final.
        """
        self.mudar_status_entrega(StatusEntrega.AGUARDANDO_ENVIO)
        HistoricoEnviosEntregas.objects.filter(hen_ent__ent_tma=self.versao_final).delete()
        services_entregas.enviar_entrega(self.aluno, self.versao_final.pk, LINK_PDF)
        notificacao = Notificacoes.objects.get(not_usu=self.professor)
        self.client.force_login(self.professor)
        resposta = self.client.get(
            reverse("cadastro:abrir_notificacao", args=[notificacao.pk]), follow=True
        )
        self.assertEqual(resposta.redirect_chain[-1][0], self.url())
        self.assertContains(resposta, "Versão final")

    def test_cenario5_devolver_pela_tela_mostra_a_mf02(self):
        """Cenário 5 (fluxo alternativo D): o Professor permanece na tela do aluno com a MF-02."""
        self.client.force_login(self.professor)
        resposta = self.client.post(
            self.url(), {"acao": "devolver", "mensagem": MENSAGEM}, follow=True
        )
        self.assertEqual(resposta.redirect_chain[-1][0], self.url())
        self.assertContains(resposta, mensagens.MF02_VERSAO_FINAL_DEVOLVIDA)
        self.assertEqual(self.registro().ent_status, StatusEntrega.DEVOLVIDA_PARA_AJUSTE)

    def test_cenario6_sem_login_vai_para_o_login_com_next(self):
        """Cenário 6 (E1): sem sessão, a tela de login, com retorno à tela do aluno."""
        resposta = self.client.get(self.url())
        self.assertEqual(resposta.status_code, 302)
        destino = urlparse(resposta["Location"])
        self.assertEqual(destino.path, reverse("cadastro:entrar"))
        self.assertEqual(parse_qs(destino.query)["next"], [self.url()])

    def test_cenario8_devolucao_sem_mensagem_destaca_o_campo(self):
        """Cenário 8 (E3): Mensagem vazia (ou acima de 500) não devolve e destaca o campo."""
        self.client.force_login(self.professor)
        for mensagem in ("", "x" * 501):
            with self.subTest(tamanho=len(mensagem)):
                resposta = self.client.post(self.url(), {"acao": "devolver", "mensagem": mensagem})
                self.assertEqual(resposta.status_code, 200)
                self.assertContains(resposta, mensagens.JUSTIFICATIVA_500)
                self.assertEqual(self.registro().ent_status, StatusEntrega.ENTREGUE)

    def test_cenario10_outro_docente_nao_ve_a_tela_nem_os_botoes(self):
        """Cenário 10 (E5): outro Docente recebe 403, sem os botões."""
        resposta = self.abrir(criar_docente_ativo())
        self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)
        self.assertNotContains(resposta, 'value="homologar"', status_code=403)

    def test_secretaria_nao_abre_a_tela(self):
        self.assertEqual(self.abrir(self.secretaria).status_code, 403)

    def test_turma_arquivada_mostra_sem_botoes_e_post_responde_mt25(self):
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save(update_fields=["tur_status"])
        resposta = self.abrir()
        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(resposta, 'value="homologar"')
        resposta = self.client.post(self.url(), {"acao": "homologar"}, follow=True)
        self.assertContains(resposta, mensagens.MT25_TURMA_ARQUIVADA)
        self.assertEqual(self.registro().ent_status, StatusEntrega.ENTREGUE)

    def test_turma_de_tcc_1_recebe_404(self):
        turma_tcc1 = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        aluno_tcc1 = matricular_aluno(turma_tcc1, status_tcc=StatusTCC.EM_ANDAMENTO)
        self.client.force_login(self.professor)
        self.assertEqual(
            self.client.get(
                reverse("cadastro:aluno_versao_final", args=[turma_tcc1.pk, aluno_tcc1.pk])
            ).status_code,
            404,
        )


class VersaoFinalNaoEnviadaViewTest(HomologacaoTestBase):
    """Cenário 9 (E4): sem envio, a seção mostra "Aguardando Envio", sem os botões."""

    enviada = False

    def test_cenario9_sem_envio_sem_botoes(self):
        resposta = self.abrir()
        self.assertContains(resposta, StatusEntrega.AGUARDANDO_ENVIO.label)
        self.assertNotContains(resposta, 'value="homologar"')
        self.assertNotContains(resposta, "Devolver para Ajuste")
