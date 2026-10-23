"""Testes da US-29 (Aluno envia a Versão Final do TCC 2) — spec 005, Phase 8, T026.

Os 13 cenários da US-29 (envio no prazo; parecer Aprovado sem correções; atraso, com o aviso
MF-01 antes do envio; prazo vencido sem link; substituição no prazo; reenvio após devolução;
acesso sem login; link inválido; resultado ainda não liberado; TCC 1 sem a seção; substituição
após o prazo; Versão Final homologada; parecer Reprovado). Escritos antes da extensão de
`services_entregas.enviar_entrega` à Versão Final (T027) e da seção "Versão final" da aba Meu
TCC (T028): devem falhar até a implementação.

[US-29][RBN-CAD-09.2][RBN-CAD-09.3][FR-023 a FR-025]
"""

from datetime import timedelta
from urllib.parse import parse_qs, urlparse

from django.http import Http404
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services_entregas
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    StatusConta,
    StatusEntrega,
    StatusTCC,
    TipoEntrega,
)
from sigtcc.apps.cadastro.models import EntregasMarcos, HistoricoEnviosEntregas, Notificacoes
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo
from sigtcc.apps.cadastro.tests.apoio_tcc import cadastrar_entrega, enviar_link
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    TesteTurmas,
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)

LINK_PDF = "https://drive.google.com/versao-final.pdf"
LINK_PDF_2 = "https://drive.google.com/versao-final-corrigida.pdf"
SECAO = "Versão final"


class VersaoFinalTestBase(TesteTurmas):
    """Turma de TCC 2, aluno com o resultado liberado e a entrega Versão Final cadastrada."""

    status_tcc = StatusTCC.APROVADO_COM_CORRECOES

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
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
            ent_tma=self.versao_final, ent_alu=self.aluno, ent_status=StatusEntrega.AGUARDANDO_ENVIO
        )

    def registro(self):
        return EntregasMarcos.objects.get(ent_tma=self.versao_final, ent_alu=self.aluno)

    def enviar(self, link=LINK_PDF):
        return services_entregas.enviar_entrega(self.aluno, self.versao_final.pk, link)

    def mudar_status_tcc(self, status):
        tcc = tcc_de(self.aluno, self.turma)
        tcc.tcc_status = status
        tcc.save(update_fields=["tcc_status"])

    def vencer_prazo(self):
        self.versao_final.tma_data_limite = timezone.now() - timedelta(days=1)
        self.versao_final.save(update_fields=["tma_data_limite"])

    def url_meu_tcc(self):
        return reverse("cadastro:meu_tcc", args=[self.turma.pk])

    def url_enviar(self):
        return reverse("cadastro:entrega_enviar", args=[self.turma.pk, self.versao_final.pk])

    def abrir_meu_tcc(self):
        self.client.force_login(self.aluno.alu)
        return self.client.get(self.url_meu_tcc())


class VersaoFinalServiceTest(VersaoFinalTestBase):
    """`services_entregas.enviar_entrega` na entrega do tipo Versão Final (T027).

    [US-29][RBN-CAD-09.2][RBN-CAD-09.3][FR-024][FR-025]
    """

    def test_cenario1_aprovado_com_correcoes_envio_no_prazo(self):
        """Cenário 1: envio no prazo -> "Entregue", Professor notificado, Status do TCC igual."""
        registro = self.enviar()
        self.assertEqual(registro.ent_status, StatusEntrega.ENTREGUE)
        self.assertTrue(Notificacoes.objects.filter(not_usu=self.professor).exists())
        self.assertEqual(
            tcc_de(self.aluno, self.turma).tcc_status, StatusTCC.APROVADO_COM_CORRECOES
        )

    def test_cenario2_aprovado_sem_correcoes(self):
        """Cenário 2 (fluxo alternativo A): parecer Aprovado -> envio registrado "Entregue"."""
        self.mudar_status_tcc(StatusTCC.APROVADO)
        self.assertEqual(self.enviar().ent_status, StatusEntrega.ENTREGUE)

    def test_cenario3_envio_com_atraso(self):
        """Cenário 3 (fluxo alternativo B): Data Limite vencida -> "Entregue com Atraso"."""
        self.vencer_prazo()
        self.assertEqual(self.enviar().ent_status, StatusEntrega.ENTREGUE_COM_ATRASO)

    def test_cenario4_prazo_vencido_sem_link(self):
        """Cenário 4 (fluxo alternativo C): "Não Entregue" e o Status do TCC permanece."""
        self.mudar_status_tcc(StatusTCC.APROVADO)
        self.vencer_prazo()
        self.assertEqual(
            services_entregas.status_exibido(self.registro()), StatusEntrega.NAO_ENTREGUE
        )
        self.assertEqual(tcc_de(self.aluno, self.turma).tcc_status, StatusTCC.APROVADO)

    def test_cenario5_substituicao_antes_da_data_limite_mantem_entregue(self):
        """Cenário 5 (fluxo alternativo D): o novo link é gravado e o status fica "Entregue"."""
        self.enviar()
        registro = self.enviar(LINK_PDF_2)
        self.assertEqual(registro.ent_status, StatusEntrega.ENTREGUE)
        self.assertEqual(services_entregas.link_mais_recente(registro).hen_link, LINK_PDF_2)

    def test_cenario6_reenvio_apos_devolucao_volta_a_entregue(self):
        """Cenário 6 (fluxo alternativo E): devolvida, o reenvio no prazo volta a "Entregue"."""
        self.enviar()
        EntregasMarcos.objects.filter(pk=self.registro().pk).update(
            ent_status=StatusEntrega.DEVOLVIDA_PARA_AJUSTE,
            ent_feedback="Falta a ficha catalográfica",
        )
        self.assertEqual(self.enviar(LINK_PDF_2).ent_status, StatusEntrega.ENTREGUE)

    def test_reenvio_apos_devolucao_depois_da_data_limite_fica_com_atraso(self):
        """FR-019/FR-025: com devolução pendente, o reenvio é aceito mesmo depois da Data Limite
        e o status é recalculado pela data do reenvio ("Entregue com Atraso").
        """
        enviar_link(self.versao_final, self.aluno, LINK_PDF, quando=timezone.now() - timedelta(3))
        self.vencer_prazo()
        EntregasMarcos.objects.filter(pk=self.registro().pk).update(
            ent_status=StatusEntrega.DEVOLVIDA_PARA_AJUSTE
        )
        self.assertEqual(self.enviar(LINK_PDF_2).ent_status, StatusEntrega.ENTREGUE_COM_ATRASO)

    def test_cenario9_resultado_ainda_nao_liberado_recusa(self):
        """Cenário 9 (E3): com o TCC ainda "Apto para Defesa", o envio é recusado."""
        self.mudar_status_tcc(StatusTCC.APTO_PARA_DEFESA)
        with self.assertRaises(Http404):
            self.enviar()
        self.assertFalse(HistoricoEnviosEntregas.objects.exists())

    def test_cenario11_substituicao_apos_a_data_limite_recusa(self):
        """Cenário 11 (E5): já enviado e fora da devolução, depois da Data Limite não substitui."""
        enviar_link(self.versao_final, self.aluno, LINK_PDF, quando=timezone.now() - timedelta(3))
        self.vencer_prazo()
        with self.assertRaises(Http404):
            self.enviar(LINK_PDF_2)

    def test_cenario12_versao_final_homologada_recusa(self):
        """Cenário 12 (E6): Versão Final homologada não aceita novo link."""
        self.enviar()
        EntregasMarcos.objects.filter(pk=self.registro().pk).update(
            ent_status=StatusEntrega.HOMOLOGADA
        )
        with self.assertRaises(Http404):
            self.enviar(LINK_PDF_2)

    def test_cenario13_parecer_reprovado_recusa(self):
        """Cenário 13 (E7): com o Status Reprovado, a entrega não fica disponível."""
        self.mudar_status_tcc(StatusTCC.REPROVADO)
        with self.assertRaises(Http404):
            self.enviar()


class VersaoFinalMeuTCCTest(VersaoFinalTestBase):
    """Seção "Versão final" da aba Meu TCC e envio pela tela (T028). [US-29][FR-023][FR-024]"""

    def test_cenario1_envio_pela_tela_mostra_a_mensagem_e_volta_ao_meu_tcc(self):
        """Cenário 1: "Versão Final enviada", com o Aluno mantido na aba Meu TCC."""
        resposta = self.abrir_meu_tcc()
        self.assertContains(resposta, SECAO)
        self.assertContains(resposta, StatusEntrega.AGUARDANDO_ENVIO.label)
        self.assertContains(resposta, f'action="{self.url_enviar()}"')
        resposta = self.client.post(self.url_enviar(), {"link": LINK_PDF}, follow=True)
        self.assertEqual(resposta.redirect_chain[-1][0], self.url_meu_tcc())
        self.assertContains(resposta, mensagens.VERSAO_FINAL_ENVIADA)
        self.assertEqual(self.registro().ent_status, StatusEntrega.ENTREGUE)

    def test_cenario3_aviso_mf01_antes_do_envio_com_a_data_limite_vencida(self):
        """Cenário 3 (fluxo alternativo B): aviso MF-01 antes de enviar, campo disponível."""
        self.vencer_prazo()
        resposta = self.abrir_meu_tcc()
        self.assertContains(resposta, mensagens.MF01_DATA_LIMITE_VENCIDA)
        self.assertContains(resposta, f'action="{self.url_enviar()}"')

    def test_cenario6_devolvida_mostra_o_status_e_a_mensagem_do_professor(self):
        """Fluxo alternativo E: a seção exibe "Devolvida para Ajuste" e a mensagem do Professor,
        com o campo Link para reenviar.
        """
        self.enviar()
        EntregasMarcos.objects.filter(pk=self.registro().pk).update(
            ent_status=StatusEntrega.DEVOLVIDA_PARA_AJUSTE,
            ent_feedback="Falta a ficha catalográfica",
        )
        resposta = self.abrir_meu_tcc()
        self.assertContains(resposta, StatusEntrega.DEVOLVIDA_PARA_AJUSTE.label)
        self.assertContains(resposta, "Falta a ficha catalográfica")
        self.assertContains(resposta, f'action="{self.url_enviar()}"')

    def test_cenario7_sem_login_vai_para_o_login_e_volta_ao_meu_tcc(self):
        """Cenário 7 (E1): sem sessão, a tela de login, com retorno à aba Meu TCC."""
        resposta = self.client.get(self.url_meu_tcc())
        self.assertEqual(resposta.status_code, 302)
        destino = urlparse(resposta["Location"])
        self.assertEqual(destino.path, reverse("cadastro:entrar"))
        self.assertEqual(parse_qs(destino.query)["next"], [self.url_meu_tcc()])

    def test_cenario8_link_vazio_nao_salva(self):
        """Cenário 8 (E2): link vazio -> mensagem exata, nada gravado."""
        self.client.force_login(self.aluno.alu)
        resposta = self.client.post(self.url_enviar(), {"link": ""})
        self.assertContains(resposta, mensagens.LINK_HTTPS_500)
        self.assertFalse(HistoricoEnviosEntregas.objects.exists())

    def test_cenario9_resultado_nao_liberado_mostra_o_aviso_sem_campo(self):
        """Cenário 9 (E3): "Disponível após a liberação do resultado", sem o campo de link."""
        self.mudar_status_tcc(StatusTCC.APTO_PARA_DEFESA)
        resposta = self.abrir_meu_tcc()
        self.assertContains(resposta, SECAO)
        self.assertContains(resposta, mensagens.VERSAO_FINAL_DISPONIVEL_APOS_RESULTADO)
        self.assertNotContains(resposta, f'action="{self.url_enviar()}"')

    def test_cenario10_tcc_1_nao_mostra_a_secao(self):
        """Cenário 10 (E4): turma de TCC 1, sem a seção Versão final."""
        turma_tcc1 = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        aluno = matricular_aluno(
            turma_tcc1, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        )
        self.client.force_login(aluno.alu)
        resposta = self.client.get(reverse("cadastro:meu_tcc", args=[turma_tcc1.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(resposta, SECAO)

    def test_cenario11_substituicao_apos_o_prazo_somente_leitura(self):
        """Cenário 11 (E5): link só leitura, sem o botão Enviar, status "Entregue"."""
        enviar_link(self.versao_final, self.aluno, LINK_PDF, quando=timezone.now() - timedelta(3))
        EntregasMarcos.objects.filter(pk=self.registro().pk).update(
            ent_status=StatusEntrega.ENTREGUE
        )
        self.vencer_prazo()
        resposta = self.abrir_meu_tcc()
        self.assertContains(resposta, LINK_PDF)
        self.assertContains(resposta, StatusEntrega.ENTREGUE.label)
        self.assertNotContains(resposta, f'action="{self.url_enviar()}"')
        self.assertNotContains(resposta, ">Enviar<")

    def test_cenario12_homologada_link_somente_leitura(self):
        """Cenário 12 (E6): status "Homologada", link só leitura, sem o botão Enviar."""
        self.enviar()
        EntregasMarcos.objects.filter(pk=self.registro().pk).update(
            ent_status=StatusEntrega.HOMOLOGADA
        )
        resposta = self.abrir_meu_tcc()
        self.assertContains(resposta, StatusEntrega.HOMOLOGADA.label)
        self.assertContains(resposta, LINK_PDF)
        self.assertNotContains(resposta, ">Enviar<")

    def test_cenario13_parecer_reprovado_sem_campo_de_link(self):
        """Cenário 13 (E7): com o parecer Reprovado, o campo Link não aparece."""
        self.mudar_status_tcc(StatusTCC.REPROVADO)
        resposta = self.abrir_meu_tcc()
        self.assertNotContains(resposta, f'action="{self.url_enviar()}"')
        self.assertNotContains(resposta, ">Enviar<")

    def test_post_direto_com_resultado_nao_liberado_nao_grava(self):
        """SC-004: pelo endereço direto, o envio fora da regra não grava nada."""
        self.mudar_status_tcc(StatusTCC.APTO_PARA_DEFESA)
        self.client.force_login(self.aluno.alu)
        self.client.post(self.url_enviar(), {"link": LINK_PDF})
        self.assertFalse(HistoricoEnviosEntregas.objects.exists())
