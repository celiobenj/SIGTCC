"""Testes de aceite da US-45: registrar, substituir ou remover coorientadores (spec 006, User
Story 6).

Cenários 1 a 14 da US-45, mais: troca de coo_id e sol_id por outro TCC (404), externo com e-mail
já cadastrado em outro TCC com caixa diferente (MO-25; Q13, Q15), limites dos campos, lista de
Docentes sem o orientador, os coorientadores e os convidados (D8), estados 'Substituída' e
'Encerrada' (D8) e as notificações MO-07, MO-08 e MO-09.

[US-45][RBN-CAD-10.3][RBN-CAD-10.4][RBN-CAD-10.7][FR-028 a FR-030][Q13][Q15][D8] (tasks T040)
"""

from django.core import mail
from django.urls import reverse

from sigtcc.apps.cadastro import mensagens, services_orientacao
from sigtcc.apps.cadastro.choices import (
    StatusConta,
    StatusCoorientacao,
    StatusSolicitacao,
    StatusTCC,
    StatusTurma,
    TipoSolicitacao,
)
from sigtcc.apps.cadastro.models import (
    Coorientacoes,
    CoorientadoresExternos,
    Notificacoes,
    SolicitacoesOrientacao,
)
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo
from sigtcc.apps.cadastro.tests.apoio_orientacao import (
    criar_convite,
    criar_externo,
    vincular_coorientador,
    vincular_orientador,
)
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    SI,
    TesteTurmas,
    criar_defesa_de,
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)
from sigtcc.apps.defesa.choices import StatusSessao


class CoorientadoresTestBase(TesteTurmas):
    """Aluno com orientador numa turma de TCC 1 de SI."""

    def setUp(self):
        super().setUp()
        self.turma = criar_turma_de(criar_docente_ativo(), curso_nome=SI)
        self.aluno = matricular_aluno(
            self.turma, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        )
        self.tcc = tcc_de(self.aluno, self.turma)
        self.orientador = criar_docente_ativo()
        vincular_orientador(self.tcc, self.orientador)
        self.docente = criar_docente_ativo()
        self.client.force_login(self.aluno.alu)

    def url(self, rota, *args):
        return reverse(f"cadastro:{rota}", args=[self.turma.pk, *args])

    def secao(self):
        return self.client.get(reverse("cadastro:meu_tcc", args=[self.turma.pk]))

    def registrar(self, follow=True, **campos):
        dados = {"tipo": "docente", "docente": self.docente.pk}
        dados.update(campos)
        return self.client.post(self.url("registrar_coorientador"), dados, follow=follow)

    def externo(self, nome="Ana Externa Lima", email="", instituicao="", follow=True, rota=None):
        dados = {"tipo": "externo", "nome": nome, "email": email, "instituicao": instituicao}
        return self.client.post(rota or self.url("registrar_coorientador"), dados, follow=follow)


class CoorientadoresTest(CoorientadoresTestBase):
    """Cenários 1 a 14. [US-45]"""

    def test_cenario1_docente_recebe_convite_e_orientador_e_avisado(self):
        with self.captureOnCommitCallbacks(execute=True):
            resposta = self.registrar()
        convite = SolicitacoesOrientacao.objects.get(sol_tipo=TipoSolicitacao.COORIENTACAO)
        self.assertEqual(convite.sol_status, StatusSolicitacao.AGUARDANDO_ACEITE)
        self.assertContains(resposta, "Aguardando Aceite")
        aviso = Notificacoes.objects.get(not_usu=self.docente)
        self.assertEqual(aviso.not_link_tela, services_orientacao.link_da_solicitacao(convite))
        self.assertEqual(mail.outbox[0].subject, mensagens.MO07_ASSUNTO)
        self.assertIn("?acao=aceitar", mail.outbox[0].body)
        self.assertIn("?acao=recusar", mail.outbox[0].body)
        self.assertTrue(Notificacoes.objects.filter(not_usu=self.orientador).exists())

    def test_cenario2_externo_registrado_sem_acesso(self):
        self.externo(email="ana@ufam.edu.br", instituicao="UFAM")
        coo = Coorientacoes.objects.get(coo_tcc=self.tcc)
        self.assertEqual(coo.coo_cext.cext_email, "ana@ufam.edu.br")
        self.assertIsNone(coo.coo_doc_id)
        self.assertFalse(SolicitacoesOrientacao.objects.exists())
        self.assertEqual(
            Notificacoes.objects.get(not_usu=self.orientador).not_mensagem,
            mensagens.MO08_COORIENTADOR_REGISTRADO.format(
                nome=self.aluno.alu.usu_nome, coorientador="Ana Externa Lima"
            ),
        )

    def test_cenario3_externo_so_com_nome(self):
        self.externo()
        externo = CoorientadoresExternos.objects.get()
        self.assertIsNone(externo.cext_email)
        self.assertIsNone(externo.cext_instituicao)

    def test_cenario4_dois_coorientadores(self):
        self.externo(nome="Primeiro Externo")
        self.externo(nome="Segundo Externo")
        resposta = self.secao()
        self.assertContains(resposta, "Primeiro Externo")
        self.assertContains(resposta, "Segundo Externo")

    def test_cenario5_remover_convite(self):
        convite = criar_convite(self.tcc, self.docente)
        confirmacao = self.client.get(self.url("remover_convite_coorientacao", convite.pk))
        self.assertContains(
            confirmacao, mensagens.MO14_CONFIRMAR_REMOVER.format(nome=self.docente.usu_nome)
        )
        self.client.post(self.url("remover_convite_coorientacao", convite.pk))
        convite.refresh_from_db()
        self.assertEqual(convite.sol_status, StatusSolicitacao.CANCELADO)
        self.client.force_login(self.docente)
        resposta = self.client.post(reverse("cadastro:aceitar_solicitacao", args=[convite.pk]))
        self.assertFalse(Coorientacoes.objects.filter(coo_tcc=self.tcc).exists())
        self.assertEqual(resposta.status_code, 302)

    def test_cenario6_substituir(self):
        x = criar_docente_ativo()
        coo = vincular_coorientador(self.tcc, docente=x)
        self.externo(nome="Zelia Nova", rota=self.url("substituir_coorientador", coo.pk))
        coo.refresh_from_db()
        self.assertEqual(coo.coo_status, StatusCoorientacao.SUBSTITUIDA)
        self.assertIsNotNone(coo.coo_data_fim)
        self.assertTrue(
            Coorientacoes.objects.filter(
                coo_tcc=self.tcc, coo_cext__cext_nome="Zelia Nova", coo_status="Ativa"
            ).exists()
        )
        self.assertEqual(
            Notificacoes.objects.get(not_usu=x).not_mensagem,
            mensagens.MO09_DEIXOU_DE_COORIENTAR.format(nome=self.aluno.alu.usu_nome),
        )
        self.assertTrue(Notificacoes.objects.filter(not_usu=self.orientador).exists())

    def test_cenario7_remover_coorientador(self):
        x = criar_docente_ativo()
        coo = vincular_coorientador(self.tcc, docente=x)
        self.client.post(self.url("remover_coorientador", coo.pk))
        coo.refresh_from_db()
        self.assertEqual(coo.coo_status, StatusCoorientacao.ENCERRADA)
        self.assertTrue(Notificacoes.objects.filter(not_usu=x).exists())
        self.assertNotIn("coorientador", services_orientacao.papeis_no_tcc(x, self.tcc))

    def test_cenario8_sem_sessao(self):
        self.client.logout()
        self.assertEqual(self.secao().status_code, 302)

    def test_cenario9_sem_orientador_sem_botao(self):
        from sigtcc.apps.cadastro.models import Orientacoes

        Orientacoes.objects.filter(ori_tcc=self.tcc).delete()
        self.assertNotContains(self.secao(), "Registrar coorientador")
        resposta = self.client.get(self.url("registrar_coorientador"))
        self.assertEqual(resposta.status_code, 404)

    def test_cenario10_coorientador_fora_da_lista(self):
        x = criar_docente_ativo()
        vincular_coorientador(self.tcc, docente=x)
        convidado = criar_docente_ativo()
        criar_convite(self.tcc, convidado)
        ids = [d.pk for d in services_orientacao.docentes_para_coorientacao(self.tcc)]
        self.assertNotIn(x.pk, ids)
        self.assertNotIn(convidado.pk, ids)
        self.assertNotIn(self.orientador.pk, ids)
        self.assertIn(self.docente.pk, ids)

    def test_cenario11_nome_em_branco(self):
        resposta = self.externo(nome="")
        self.assertContains(resposta, mensagens.M14_CAMPO_OBRIGATORIO)
        self.assertContains(resposta, "com-erro")
        self.assertFalse(Coorientacoes.objects.exists())

    def test_limites_e_formatos(self):
        resposta = self.externo(nome="Nome 123")
        self.assertContains(resposta, mensagens.NOME_INVALIDO)
        resposta = self.externo(email="sem-arroba")
        self.assertContains(resposta, mensagens.EMAIL_VALIDO)
        self.externo(instituicao="x" * 151)
        self.assertFalse(Coorientacoes.objects.exists())

    def test_cenario12_defesa_agendada_botoes_desabilitados(self):
        coo = vincular_coorientador(self.tcc, docente=criar_docente_ativo())
        criar_defesa_de(self.tcc, StatusSessao.AGENDADA)
        resposta = self.secao()
        self.assertContains(resposta, 'class="btn txt" disabled>Substituir')
        self.assertContains(resposta, 'class="btn txt" disabled>Remover')
        self.assertEqual(
            self.client.post(self.url("remover_coorientador", coo.pk)).status_code, 404
        )

    def test_cenario13_desistente_so_consulta(self):
        vincular_coorientador(self.tcc, externo=criar_externo(nome="Externo Fixo"))
        self.tcc.tcc_status = StatusTCC.DESISTENTE
        self.tcc.save()
        resposta = self.secao()
        self.assertContains(resposta, "Externo Fixo")
        self.assertNotContains(resposta, "Registrar coorientador")
        self.assertNotContains(resposta, ">Substituir<")

    def test_cenario14_turma_arquivada_so_consulta(self):
        vincular_coorientador(self.tcc, externo=criar_externo(nome="Externo Fixo"))
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save()
        resposta = self.secao()
        self.assertContains(resposta, "Externo Fixo")
        self.assertNotContains(resposta, "Registrar coorientador")
        resposta = self.client.get(self.url("registrar_coorientador"), follow=True)
        self.assertContains(resposta, mensagens.MT25_TURMA_ARQUIVADA)


class ExternoReaproveitadoTest(CoorientadoresTestBase):
    """Q13 e Q15: e-mail já cadastrado em outro TCC; R17: caixa diferente. [FR-028]"""

    def test_reaproveita_sem_alterar_nome_e_instituicao(self):
        existente = criar_externo(
            nome="Nome Original", email="pesq@ufam.edu.br", instituicao="UFAM"
        )
        resposta = self.externo(nome="Outro Nome", email="Pesq@UFAM.edu.br", instituicao="X")
        self.assertContains(resposta, mensagens.MO25_EXTERNO_REAPROVEITADO)
        existente.refresh_from_db()
        self.assertEqual(
            (existente.cext_nome, existente.cext_instituicao), ("Nome Original", "UFAM")
        )
        self.assertEqual(CoorientadoresExternos.objects.count(), 1)
        self.assertEqual(Coorientacoes.objects.get(coo_tcc=self.tcc).coo_cext_id, existente.pk)

    def test_mesmo_email_no_mesmo_trabalho_recusado(self):
        self.externo(email="pesq@ufam.edu.br")
        resposta = self.externo(email="pesq@ufam.edu.br")
        self.assertContains(resposta, mensagens.EMAIL_JA_COORIENTADOR)
        self.assertEqual(Coorientacoes.objects.filter(coo_tcc=self.tcc).count(), 1)


class SegurancaCoorientadoresTest(CoorientadoresTestBase):
    """coo_id e sol_id de outro TCC: 404 (research R10, A1). [SC-006]"""

    def test_ids_de_outro_tcc_404(self):
        outro = matricular_aluno(self.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        tcc_outro = tcc_de(outro, self.turma)
        vincular_orientador(tcc_outro, criar_docente_ativo())
        coo = vincular_coorientador(tcc_outro, externo=criar_externo())
        convite = criar_convite(tcc_outro, criar_docente_ativo())
        for rota, arg in (
            ("substituir_coorientador", coo.pk),
            ("remover_coorientador", coo.pk),
            ("remover_convite_coorientacao", convite.pk),
        ):
            with self.subTest(rota=rota):
                self.assertEqual(self.client.post(self.url(rota, arg)).status_code, 404)
        coo.refresh_from_db()
        self.assertEqual(coo.coo_status, StatusCoorientacao.ATIVA)


class AlternanciaDoTipoTest(CoorientadoresTestBase):
    """Teste manual, passo 7: só a caixa do Tipo escolhido fica visível (alternar_tipo.js), sem
    JavaScript o formulário funciona e o servidor decide o que vale. [US-45][FR-028]
    """

    def test_janela_liga_a_alternancia(self):
        resposta = self.client.get(self.url("registrar_coorientador"))
        self.assertContains(resposta, 'data-alterna="tipo"')
        self.assertContains(resposta, 'data-tipo="docente"')
        self.assertContains(resposta, 'data-tipo="externo"')
        self.assertContains(resposta, "js/alternar_tipo.js")
        # O servidor não esconde nenhuma caixa: sem JavaScript, as duas aparecem.
        self.assertNotRegex(resposta.content.decode(), r"<fieldset[^>]*hidden")

    def test_reexibicao_com_erro_mantem_o_tipo_enviado(self):
        resposta = self.externo(nome="")
        self.assertContains(resposta, '<option value="externo" selected>')
        self.assertContains(resposta, 'data-tipo="externo"')

    def test_servidor_ignora_a_caixa_do_outro_tipo(self):
        """Sem JS, o aluno pode preencher as duas caixas: vale só a do Tipo."""
        dados = {
            "tipo": "externo",
            "docente": self.docente.pk,
            "nome": "Ana Externa Lima",
            "email": "",
            "instituicao": "",
        }
        self.client.post(self.url("registrar_coorientador"), dados)
        self.assertFalse(SolicitacoesOrientacao.objects.exists())
        self.assertEqual(
            Coorientacoes.objects.get(coo_tcc=self.tcc).coo_cext.cext_nome, "Ana Externa Lima"
        )

    def test_substituir_tambem_alterna(self):
        coo = vincular_coorientador(self.tcc, externo=criar_externo())
        resposta = self.client.get(self.url("substituir_coorientador", coo.pk))
        self.assertContains(resposta, 'data-alterna="tipo"')
        self.assertContains(resposta, "js/alternar_tipo.js")
