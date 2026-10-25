"""Testes de aceite da US-36: aceitar ou recusar o convite de coorientação e acompanhar o
trabalho na tela de orientandos (spec 006, User Story 7).

Cenários 1 a 11 da US-36, mais: botões do e-mail só destacam e o GET nunca grava (Q14), textos de
convite por motivo de cancelamento, aceite com a conta inativa recusado (Q-68) e a linha do
Coorientador só com "Atas" e "Registrar ata" (FR-015).

[US-36][RBN-CAD-10.4][FR-031 a FR-033][Q14][D7] (tasks T044)
"""

from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services_orientacao, services_turmas
from sigtcc.apps.cadastro.choices import (
    StatusConta,
    StatusCoorientacao,
    StatusSolicitacao,
    StatusTCC,
)
from sigtcc.apps.cadastro.models import Coorientacoes, Notificacoes
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo
from sigtcc.apps.cadastro.tests.apoio_orientacao import (
    criar_convite,
    vincular_coorientador,
    vincular_orientador,
)
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    SI,
    TesteTurmas,
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)


class ConviteTest(TesteTurmas):
    """Convite pendente ao docente, num TCC com orientador. [US-36]"""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=SI)
        self.aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        self.tcc = tcc_de(self.aluno, self.turma)
        self.orientador = criar_docente_ativo()
        vincular_orientador(self.tcc, self.orientador)
        self.docente = criar_docente_ativo()
        self.convite = criar_convite(self.tcc, self.docente)
        self.client.force_login(self.docente)

    def link(self, sufixo=""):
        return self.client.get(services_orientacao.link_da_solicitacao(self.convite) + sufixo)

    def aceitar(self):
        url = reverse("cadastro:aceitar_solicitacao", args=[self.convite.pk])
        return self.client.post(url, follow=True)

    def recusar(self):
        url = reverse("cadastro:recusar_solicitacao", args=[self.convite.pk])
        return self.client.post(url, follow=True)

    def test_cenario1_aceite(self):
        resposta = self.aceitar()
        self.assertContains(resposta, mensagens.CONVITE_ACEITO)
        coo = Coorientacoes.objects.get(coo_tcc=self.tcc)
        self.assertEqual(
            (coo.coo_doc_id, coo.coo_status), (self.docente.pk, StatusCoorientacao.ATIVA)
        )
        self.assertContains(resposta, "Coorientador")
        self.assertEqual(
            Notificacoes.objects.get(not_usu=self.aluno.alu).not_mensagem,
            mensagens.MO10_CONVITE_ACEITO_ALUNO.format(docente=self.docente.usu_nome),
        )
        self.assertEqual(
            Notificacoes.objects.get(not_usu=self.orientador).not_mensagem,
            mensagens.MO10_CONVITE_ACEITO_ORIENTADOR.format(
                docente=self.docente.usu_nome, nome=self.aluno.alu.usu_nome
            ),
        )

    def test_cenario2_e_3_link_abre_a_tela_com_o_convite(self):
        resposta = self.link()
        self.assertContains(resposta, "Convites de coorientação")
        self.assertContains(resposta, f'class="item destaque" id="solicitacao-{self.convite.pk}"')

    def test_cenario4_recusa(self):
        resposta = self.recusar()
        self.assertContains(resposta, mensagens.CONVITE_RECUSADO)
        self.convite.refresh_from_db()
        self.assertEqual(self.convite.sol_status, StatusSolicitacao.RECUSADO)
        self.assertEqual(
            Notificacoes.objects.get(not_usu=self.aluno.alu).not_mensagem,
            mensagens.MO11_CONVITE_RECUSADO.format(docente=self.docente.usu_nome),
        )
        self.assertEqual(len(services_orientacao.historico_de_orientacao(self.tcc)), 1)

    def test_cenario5_removido_perde_a_tela_e_as_atas(self):
        self.aceitar()
        coo = Coorientacoes.objects.get(coo_tcc=self.tcc)
        coo.coo_status = StatusCoorientacao.ENCERRADA
        coo.coo_data_fim = timezone.now()
        coo.save()
        self.assertEqual(services_orientacao.orientandos(self.docente), [])
        url = reverse("cadastro:atas_orientando", args=[self.tcc.pk])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_cenario7_sem_sessao_vai_ao_login(self):
        self.client.logout()
        resposta = self.link()
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("cadastro:entrar"), resposta.url)

    def test_cenario8_outro_docente(self):
        self.client.force_login(criar_docente_ativo())
        resposta = self.link()
        self.assertContains(resposta, mensagens.CONVITE_NAO_DISPONIVEL)
        self.assertNotContains(resposta, f"solicitacao-{self.convite.pk}")

    def test_cenario9_cancelado_pelo_aluno(self):
        self.convite.sol_status = StatusSolicitacao.CANCELADO
        self.convite.sol_data_resposta = timezone.now()
        self.convite.save()
        self.assertContains(self.link(), mensagens.CONVITE_CANCELADO_PELO_ALUNO)
        self.aceitar()
        self.assertFalse(Coorientacoes.objects.exists())

    def test_cenario10_recusado_mostra_data(self):
        self.recusar()
        self.assertContains(self.link(), "Recusado · ")

    def test_cenario11_pendente_nao_aparece_nos_orientandos(self):
        self.assertEqual(services_orientacao.orientandos(self.docente), [])

    def test_botoes_do_email_so_destacam(self):
        resposta = self.link("?acao=aceitar")
        self.assertContains(resposta, "autofocus")
        self.convite.refresh_from_db()
        self.assertEqual(self.convite.sol_status, StatusSolicitacao.AGUARDANDO_ACEITE)

    def test_cancelado_pelo_encerramento_texto_de_convite(self):
        services_turmas.encerrar_participacao(
            self.professor, self.turma.pk, self.aluno.pk, StatusTCC.DESISTENTE, "Desistiu"
        )
        self.assertContains(self.link(), mensagens.MO12_CONVITE_CANCELADO_ENCERRAMENTO)

    def test_aceite_com_conta_inativa_recusado(self):
        self.docente.usu_status = StatusConta.INATIVA
        self.docente.save()
        from django.http import Http404

        from sigtcc.apps.cadastro.services_orientacao import aceitar_solicitacao

        with self.assertRaises(Http404):
            aceitar_solicitacao(self.docente, self.convite.pk)
        self.assertFalse(Coorientacoes.objects.exists())

    def test_linha_do_coorientador_so_atas(self):
        self.aceitar()
        linha = services_orientacao.orientandos(self.docente)[0]
        self.assertEqual(linha["papel"], "Coorientador")
        self.assertFalse(linha["pode_historico"])
        self.assertFalse(linha["pode_publicacao"])
        self.assertIsNone(linha["apto"])
        self.assertIsNone(linha["correcoes"])


class ExternoSemConviteTest(TesteTurmas):
    """Cenário 6: externo registrado não gera convite. [US-36][RBN-CAD-10.4]"""

    def test_cenario6_externo_sem_convite(self):
        from sigtcc.apps.cadastro.models import SolicitacoesOrientacao
        from sigtcc.apps.cadastro.tests.apoio_orientacao import criar_externo

        turma = criar_turma_de(criar_docente_ativo(), curso_nome=SI)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        vincular_coorientador(tcc_de(aluno, turma), externo=criar_externo())
        self.assertFalse(SolicitacoesOrientacao.objects.exists())
