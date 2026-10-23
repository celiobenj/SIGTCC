"""Testes da US-15 (Aluno envia ou substitui o link de uma entrega) — spec 005, Phase 6, T020.

Os 8 cenários de aceite e exceção da User Story 4 do `spec.md` (envio no prazo; envio com atraso;
prazo vencido sem envio; substituição no prazo; lembrete de prazo — só a função pura
`entregas_para_lembrar`; entrega do tipo Proposta sem campo de link; link inválido; campo só
leitura quando não permitido), mais os cenários da US-15 original (acesso pela notificação,
substituição após o prazo, TCC fora de Em Andamento, aluno Desistente/Jubilado, turma arquivada)
e dois testes de corrida (research C7, achado A1 da análise `/speckit-analyze`): duas chamadas
quase simultâneas a `enviar_entrega` devem produzir um único "primeiro envio" consistente, e
`enviar_entrega` concorrendo com `encerrar_participacao` não deve permitir envio depois que a
participação for encerrada. Escritos antes de `services_entregas.enviar_entrega`,
`forms_entregas.EnviarLinkForm` e `views_entregas.minhas_entregas`/`entrega_enviar`: devem falhar
até a implementação (T021 a T023).

[US-15][RBN-CAD-09.2][RBN-CAD-09.3][RBN-CAD-09.6][FR-018 a FR-023][research C7]
"""

import threading
from datetime import timedelta
from io import StringIO
from urllib.parse import parse_qs, urlparse

from django.core.management import call_command
from django.db import close_old_connections
from django.http import Http404
from django.test import TransactionTestCase
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services_entregas, services_turmas
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    StatusConta,
    StatusEntrega,
    StatusTCC,
    StatusTurma,
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
)

LINK_VALIDO = "https://drive.google.com/documento-1"
LINK_SUBSTITUTO = "https://drive.google.com/documento-2"


class EnviarEntregaTestBase(TesteTurmas):
    """Turma de TCC 1, aluno com TCC Em Andamento e uma entrega Documento para Defesa."""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        self.aluno = matricular_aluno(
            self.turma, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        )
        self.entrega = cadastrar_entrega(
            self.turma,
            tipo=TipoEntrega.DOCUMENTO_PARA_DEFESA,
            titulo="Entrega do Documento",
            data_limite=timezone.now() + timedelta(days=10),
        )
        # `cadastrar_entrega` (apoio_tcc) só cria a Turmas_Marcos; o registro do aluno
        # ("Aguardando Envio") é quem o serviço cadastrar_entrega/criar_entregas_do_aluno criaria
        # na vida real — aqui a fábrica de teste cria direto, como o resto da suíte faz.
        EntregasMarcos.objects.create(
            ent_tma=self.entrega, ent_alu=self.aluno, ent_status=StatusEntrega.AGUARDANDO_ENVIO
        )

    def registro(self):
        return EntregasMarcos.objects.get(ent_tma=self.entrega, ent_alu=self.aluno)


class EnviarEntregaServiceTest(EnviarEntregaTestBase):
    """`services_entregas.enviar_entrega`: cenários 1, 2, 4 e as recusas do FR-023.

    [US-15][FR-018 a FR-021][FR-023][research C7]
    """

    def test_cenario1_envio_no_prazo_fica_entregue_e_notifica_o_professor(self):
        """Cenário 1 do spec.md: envio antes da Data Limite -> "Entregue", professor notificado.

        [US-15][FR-018][FR-019][FR-021]
        """
        registro = services_entregas.enviar_entrega(self.aluno, self.entrega.pk, LINK_VALIDO)
        self.assertEqual(registro.ent_status, StatusEntrega.ENTREGUE)
        self.assertTrue(
            HistoricoEnviosEntregas.objects.filter(hen_ent=registro, hen_link=LINK_VALIDO).exists()
        )
        notificacao = Notificacoes.objects.get(not_usu=self.professor)
        self.assertIn("Entrega do Documento", notificacao.not_mensagem)

    def test_cenario2_envio_com_atraso(self):
        """Cenário 2 do spec.md: primeiro envio após a Data Limite -> "Entregue com Atraso".

        [US-15][FR-019]
        """
        self.entrega.tma_data_limite = timezone.now() - timedelta(days=1)
        self.entrega.save(update_fields=["tma_data_limite"])
        registro = services_entregas.enviar_entrega(self.aluno, self.entrega.pk, LINK_VALIDO)
        self.assertEqual(registro.ent_status, StatusEntrega.ENTREGUE_COM_ATRASO)

    def test_cenario4_substituicao_no_prazo_mantem_o_status_do_primeiro_envio(self):
        """Cenário 4 do spec.md: substituição antes da Data Limite mantém o status do primeiro
        envio e notifica o Professor de novo. [US-15][FR-019][FR-021]
        """
        # Primeiro envio e substituição pelo serviço (cada um notifica o Professor).
        services_entregas.enviar_entrega(self.aluno, self.entrega.pk, LINK_VALIDO)
        resultado = services_entregas.enviar_entrega(self.aluno, self.entrega.pk, LINK_SUBSTITUTO)
        self.assertEqual(resultado.ent_status, StatusEntrega.ENTREGUE)
        self.assertEqual(HistoricoEnviosEntregas.objects.filter(hen_ent=resultado).count(), 2)
        self.assertEqual(Notificacoes.objects.filter(not_usu=self.professor).count(), 2)

    def test_cenario7_link_invalido_nao_salva(self):
        """Cenário 7/E2 do spec.md: link vazio, sem https:// ou maior que 500 caracteres não
        salva — conferido no formulário (T023); aqui confere que o serviço grava o link como
        veio (a validação é do form, não do serviço). [US-15][FR-018][research C6]
        """
        # O serviço em si não valida o formato do link (quem valida é o form); a persistência de
        # um link inválido manual (teste de unidade do form, não deste serviço) fica em
        # EnviarLinkFormTest.
        registro = services_entregas.enviar_entrega(self.aluno, self.entrega.pk, LINK_VALIDO)
        self.assertEqual(
            HistoricoEnviosEntregas.objects.get(hen_ent=registro).hen_link, LINK_VALIDO
        )

    def test_cenario6_entrega_tipo_proposta_recusa_com_404(self):
        """Cenário 6/Fluxo F do spec.md: a entrega do tipo Proposta não tem campo de link.

        [US-15][FR-018]
        """
        proposta = cadastrar_entrega(self.turma, tipo=TipoEntrega.PROPOSTA, titulo="Proposta")
        with self.assertRaises(Http404):
            services_entregas.enviar_entrega(self.aluno, proposta.pk, LINK_VALIDO)
        self.assertFalse(HistoricoEnviosEntregas.objects.filter(hen_ent__ent_tma=proposta).exists())

    def test_versao_final_ainda_nao_e_liberada_nesta_fase(self):
        """A Versão Final (US-29) é tratada só na Phase 8 desta feature; nesta fase o envio ainda
        não é liberado. [US-15][research C7]
        """
        turma_tcc2 = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        aluno2 = matricular_aluno(
            turma_tcc2, status_tcc=StatusTCC.APROVADO, status_conta=StatusConta.ATIVA
        )
        versao_final = cadastrar_entrega(
            turma_tcc2, tipo=TipoEntrega.VERSAO_FINAL, titulo="Versão Final"
        )
        with self.assertRaises(Http404):
            services_entregas.enviar_entrega(aluno2, versao_final.pk, LINK_VALIDO)

    def test_substituicao_apos_a_data_limite_recusa_com_404(self):
        """E3 da US-15 original: substituição após a Data Limite não é aceita (campo só leitura).

        [US-15][FR-019]
        """
        enviar_link(
            self.entrega, self.aluno, LINK_VALIDO, quando=timezone.now() - timedelta(days=5)
        )
        self.entrega.tma_data_limite = timezone.now() - timedelta(days=1)
        self.entrega.save(update_fields=["tma_data_limite"])
        with self.assertRaises(Http404):
            services_entregas.enviar_entrega(self.aluno, self.entrega.pk, LINK_SUBSTITUTO)

    def test_tcc_fora_de_em_andamento_recusa_com_404(self):
        """E4 da US-15 original: TCC fora de "Em Andamento" (ex.: Apto para Defesa) recusa o
        envio nas entregas Documento para Defesa e Outra. [US-15][FR-023]
        """
        tcc = services_turmas.tcc_do_aluno(self.turma, self.aluno)
        tcc.tcc_status = StatusTCC.APTO_PARA_DEFESA
        tcc.save(update_fields=["tcc_status"])
        with self.assertRaises(Http404):
            services_entregas.enviar_entrega(self.aluno, self.entrega.pk, LINK_VALIDO)

    def test_aluno_desistente_recusa_com_404(self):
        """E5 da US-15 original: Aluno Desistente, Reprovado ou Jubilado não envia.

        [US-15][RBN-CAD-08.5][FR-023]
        """
        tcc = services_turmas.tcc_do_aluno(self.turma, self.aluno)
        tcc.tcc_status = StatusTCC.DESISTENTE
        tcc.save(update_fields=["tcc_status"])
        with self.assertRaises(Http404):
            services_entregas.enviar_entrega(self.aluno, self.entrega.pk, LINK_VALIDO)

    def test_turma_arquivada_recusa_com_404(self):
        """E6 da US-15 original: turma arquivada não aceita envio. [US-15][FR-023]"""
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save(update_fields=["tur_status"])
        with self.assertRaises(Http404):
            services_entregas.enviar_entrega(self.aluno, self.entrega.pk, LINK_VALIDO)


class PrazoVencidoSemEnvioTest(EnviarEntregaTestBase):
    """Cenário 3 do spec.md / fluxo C da US-15 original: status exibido "Não Entregue" sem envio
    depois da Data Limite, mas o envio continua disponível.

    [US-15][RBN-CAD-09.3][FR-020]
    """

    def test_status_exibido_vira_nao_entregue_sem_gravar_e_envio_continua_disponivel(self):
        self.entrega.tma_data_limite = timezone.now() - timedelta(hours=1)
        self.entrega.save(update_fields=["tma_data_limite"])
        registro = self.registro()
        self.assertEqual(registro.ent_status, StatusEntrega.AGUARDANDO_ENVIO)
        self.assertEqual(services_entregas.status_exibido(registro), StatusEntrega.NAO_ENTREGUE)
        # O envio continua disponível e, se ocorrer, segue o fluxo alternativo B (Entregue com
        # Atraso), sem reprovar o aluno nem mudar o Status do TCC.
        resultado = services_entregas.enviar_entrega(self.aluno, self.entrega.pk, LINK_VALIDO)
        self.assertEqual(resultado.ent_status, StatusEntrega.ENTREGUE_COM_ATRASO)
        tcc = services_turmas.tcc_do_aluno(self.turma, self.aluno)
        self.assertEqual(tcc.tcc_status, StatusTCC.EM_ANDAMENTO)


class LembretesDePrazoTest(EnviarEntregaTestBase):
    """Fluxo alternativo E da US-15 original (Could Have): função pura `entregas_para_lembrar`.

    [US-15][RBN-CAD-09.6][FR-022][research C5]
    """

    def test_entrega_a_7_dias_entra_na_lista(self):
        agora = timezone.now()
        self.entrega.tma_data_limite = agora + timedelta(days=7)
        self.entrega.save(update_fields=["tma_data_limite"])
        resultado = services_entregas.entregas_para_lembrar(agora)
        self.assertIn(self.registro(), list(resultado))

    def test_entrega_a_48h_entra_na_lista(self):
        agora = timezone.now()
        self.entrega.tma_data_limite = agora + timedelta(hours=48)
        self.entrega.save(update_fields=["tma_data_limite"])
        self.assertIn(self.registro(), list(services_entregas.entregas_para_lembrar(agora)))

    def test_entrega_a_24h_entra_na_lista(self):
        agora = timezone.now()
        self.entrega.tma_data_limite = agora + timedelta(hours=24)
        self.entrega.save(update_fields=["tma_data_limite"])
        self.assertIn(self.registro(), list(services_entregas.entregas_para_lembrar(agora)))

    def test_entrega_fora_das_janelas_nao_entra_na_lista(self):
        agora = timezone.now()
        self.entrega.tma_data_limite = agora + timedelta(days=3)
        self.entrega.save(update_fields=["tma_data_limite"])
        self.assertNotIn(self.registro(), list(services_entregas.entregas_para_lembrar(agora)))

    def test_aluno_que_ja_enviou_nao_entra_na_lista(self):
        agora = timezone.now()
        self.entrega.tma_data_limite = agora + timedelta(hours=24)
        self.entrega.save(update_fields=["tma_data_limite"])
        enviar_link(self.entrega, self.aluno, LINK_VALIDO, quando=agora)
        registro = self.registro()
        registro.ent_status = StatusEntrega.ENTREGUE
        registro.save(update_fields=["ent_status"])
        self.assertNotIn(registro, list(services_entregas.entregas_para_lembrar(agora)))

    def test_turma_arquivada_nao_entra_na_lista(self):
        agora = timezone.now()
        self.entrega.tma_data_limite = agora + timedelta(hours=24)
        self.entrega.save(update_fields=["tma_data_limite"])
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save(update_fields=["tur_status"])
        self.assertNotIn(self.registro(), list(services_entregas.entregas_para_lembrar(agora)))


class EnviarLinkFormTest(TesteTurmas):
    """Cenário 7/E2 do spec.md: validação do Link no formulário. [US-15][FR-018]"""

    def test_link_vazio_mostra_a_mensagem_exata(self):
        from sigtcc.apps.cadastro.forms_entregas import EnviarLinkForm

        formulario = EnviarLinkForm(data={"link": ""})
        self.assertFalse(formulario.is_valid())
        self.assertIn(mensagens.LINK_HTTPS_500, formulario.errors["link"])

    def test_link_sem_https_mostra_a_mensagem_exata(self):
        from sigtcc.apps.cadastro.forms_entregas import EnviarLinkForm

        formulario = EnviarLinkForm(data={"link": "http://drive.google.com/x"})
        self.assertFalse(formulario.is_valid())
        self.assertIn(mensagens.LINK_HTTPS_500, formulario.errors["link"])

    def test_link_maior_que_500_mostra_a_mensagem_exata(self):
        from sigtcc.apps.cadastro.forms_entregas import EnviarLinkForm

        formulario = EnviarLinkForm(data={"link": "https://" + "a" * 500})
        self.assertFalse(formulario.is_valid())
        self.assertIn(mensagens.LINK_HTTPS_500, formulario.errors["link"])

    def test_link_valido_passa(self):
        from sigtcc.apps.cadastro.forms_entregas import EnviarLinkForm

        formulario = EnviarLinkForm(data={"link": LINK_VALIDO})
        self.assertTrue(formulario.is_valid())


class MinhasEntregasViewTest(EnviarEntregaTestBase):
    """Views `minhas_entregas` e `entrega_enviar`: cenários 1, 5, 6, 8 e o acesso restrito.

    [US-15][FR-018 a FR-023][contracts/rotas.md]
    """

    def url_lista(self):
        return reverse("cadastro:minhas_entregas", args=[self.turma.pk])

    def url_entrega(self, entrega=None):
        return reverse(
            "cadastro:entrega_enviar", args=[self.turma.pk, (entrega or self.entrega).pk]
        )

    def test_lista_mostra_a_entrega_e_o_status(self):
        self.client.force_login(self.aluno.alu)
        resposta = self.client.get(self.url_lista())
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Entrega do Documento")
        self.assertContains(resposta, "Aguardando Envio")

    def test_cenario1_envio_por_post_mostra_a_mensagem_e_o_status(self):
        self.client.force_login(self.aluno.alu)
        resposta = self.client.post(self.url_entrega(), {"link": LINK_VALIDO}, follow=True)
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, mensagens.ENTREGA_ENVIADA)
        self.assertEqual(self.registro().ent_status, StatusEntrega.ENTREGUE)

    def test_cenario6_entrega_tipo_proposta_mostra_o_aviso_sem_campo_de_link(self):
        """Cenário 6 do spec.md: fluxo F — sem campo de link, com o aviso exato.

        [US-15][FR-018]
        """
        proposta = cadastrar_entrega(self.turma, tipo=TipoEntrega.PROPOSTA, titulo="Proposta")
        # Registro do aluno nessa entrega, como o serviço de cadastro (US-43) criaria.
        EntregasMarcos.objects.create(
            ent_tma=proposta, ent_alu=self.aluno, ent_status=StatusEntrega.AGUARDANDO_ENVIO
        )
        self.client.force_login(self.aluno.alu)
        resposta = self.client.get(self.url_entrega(proposta))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, mensagens.ENTREGA_CUMPRIDA_PROPOSTA)
        self.assertNotContains(resposta, 'name="link"')

    def test_cenario7_link_invalido_por_post_nao_salva(self):
        self.client.force_login(self.aluno.alu)
        resposta = self.client.post(self.url_entrega(), {"link": "ftp://arquivo"})
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, mensagens.LINK_HTTPS_500)
        self.assertFalse(HistoricoEnviosEntregas.objects.filter(hen_ent=self.registro()).exists())

    def test_cenario8_tcc_fora_de_em_andamento_esconde_o_botao_enviar(self):
        """Cenário 8 do spec.md: campo só leitura, sem o botão Enviar. [US-15][FR-023]"""
        tcc = services_turmas.tcc_do_aluno(self.turma, self.aluno)
        tcc.tcc_status = StatusTCC.APTO_PARA_DEFESA
        tcc.save(update_fields=["tcc_status"])
        self.client.force_login(self.aluno.alu)
        resposta = self.client.get(self.url_entrega())
        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(resposta, ">Enviar<")

    def test_turma_arquivada_esconde_o_botao_enviar(self):
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save(update_fields=["tur_status"])
        self.client.force_login(self.aluno.alu)
        resposta = self.client.get(self.url_entrega())
        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(resposta, ">Enviar<")

    def test_outro_aluno_recebe_404_sem_idor(self):
        """Sem IDOR: outro aluno (mesmo que da mesma turma) não acessa a entrega alheia.

        [US-15][contracts/rotas.md]
        """
        outro_aluno = matricular_aluno(
            self.turma, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        )
        self.client.force_login(outro_aluno.alu)
        self.assertEqual(self.client.get(self.url_entrega()).status_code, 404)

    def test_docente_recebe_403(self):
        self.client.force_login(self.professor)
        self.assertEqual(self.client.get(self.url_lista()).status_code, 403)
        self.assertEqual(self.client.get(self.url_entrega()).status_code, 403)

    def test_turma_inexistente_recebe_404(self):
        self.client.force_login(self.aluno.alu)
        self.assertEqual(
            self.client.get(reverse("cadastro:minhas_entregas", args=[0])).status_code, 404
        )

    def test_cenario2_acesso_pela_notificacao_abre_a_aba_atividades(self):
        """Cenário 2 da US-15 (fluxo alternativo A): a notificação da nova entrega abre a aba
        Atividades da turma, com a entrega. [US-15][RBN-CAD-09.6]
        """
        services_entregas.cadastrar_entrega(
            self.professor,
            self.turma.pk,
            {
                "tipo": TipoEntrega.OUTRA,
                "titulo": "Entrega do Cronograma",
                "data_limite": timezone.now() + timedelta(days=3),
            },
        )
        notificacao = Notificacoes.objects.get(not_usu=self.aluno.alu)
        self.client.force_login(self.aluno.alu)
        resposta = self.client.get(
            reverse("cadastro:abrir_notificacao", args=[notificacao.pk]), follow=True
        )
        self.assertEqual(resposta.redirect_chain[-1][0], self.url_lista())
        self.assertContains(resposta, "Entrega do Cronograma")

    def test_cenario8_sem_login_vai_para_o_login_e_volta_para_a_aba(self):
        """Cenário 8 da US-15 (E1): sem sessão, a tela de login, com retorno à aba Atividades.

        [US-15][contracts/rotas.md]
        """
        resposta = self.client.get(self.url_lista())
        self.assertEqual(resposta.status_code, 302)
        destino = urlparse(resposta["Location"])
        self.assertEqual(destino.path, reverse("cadastro:entrar"))
        self.assertEqual(parse_qs(destino.query)["next"], [self.url_lista()])

    def test_cenario10_substituicao_apos_o_prazo_fica_somente_leitura(self):
        """Cenário 10 da US-15 (E3): enviado no prazo e aberto depois da Data Limite, o Link
        aparece só para leitura, sem o botão Enviar, e o status permanece Entregue.
        [US-15][FR-019]
        """
        enviar_link(
            self.entrega, self.aluno, LINK_VALIDO, quando=timezone.now() - timedelta(days=4)
        )
        registro = self.registro()
        registro.ent_status = StatusEntrega.ENTREGUE
        registro.save(update_fields=["ent_status"])
        self.entrega.tma_data_limite = timezone.now() - timedelta(days=2)
        self.entrega.save(update_fields=["tma_data_limite"])
        self.client.force_login(self.aluno.alu)
        resposta = self.client.get(self.url_entrega())
        self.assertContains(resposta, LINK_VALIDO)
        self.assertContains(resposta, StatusEntrega.ENTREGUE.label)
        self.assertNotContains(resposta, ">Enviar<")
        # Pelo endereço direto, o POST também não grava nada (SC-004).
        self.client.post(self.url_entrega(), {"link": LINK_SUBSTITUTO})
        self.assertFalse(HistoricoEnviosEntregas.objects.filter(hen_link=LINK_SUBSTITUTO).exists())

    def test_cenario12_aluno_jubilado_sem_o_botao_enviar(self):
        """Cenário 12 da US-15 (E5): aluno Jubilado abre a entrega, sem o botão Enviar.

        [US-15][RBN-CAD-08.5][FR-023]
        """
        tcc = services_turmas.tcc_do_aluno(self.turma, self.aluno)
        tcc.tcc_status = StatusTCC.JUBILADO
        tcc.save(update_fields=["tcc_status"])
        self.client.force_login(self.aluno.alu)
        resposta = self.client.get(self.url_entrega())
        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(resposta, ">Enviar<")


class EnviarLembretesTest(EnviarEntregaTestBase):
    """Cenário 6 da US-15 (fluxo alternativo E): o lembrete chega ao aluno que não enviou, uma
    vez por janela, pelo comando `enviar_lembretes_entrega` (T022).

    [US-15][RBN-CAD-09.6][FR-022][research C5]
    """

    def test_cenario6_lembrete_de_48h_notifica_o_aluno_com_o_link_da_entrega(self):
        agora = timezone.now()
        self.entrega.tma_data_limite = agora + timedelta(hours=48)
        self.entrega.save(update_fields=["tma_data_limite"])
        self.assertEqual(services_entregas.enviar_lembretes_de_prazo(agora), 1)
        notificacao = Notificacoes.objects.get(not_usu=self.aluno.alu)
        self.assertIn("Entrega do Documento", notificacao.not_mensagem)
        self.assertEqual(notificacao.not_link_tela, self.url_entrega_do_aluno())

    def test_lembrete_nao_se_repete_na_execucao_seguinte_da_mesma_janela(self):
        agora = timezone.now()
        self.entrega.tma_data_limite = agora + timedelta(hours=24)
        self.entrega.save(update_fields=["tma_data_limite"])
        services_entregas.enviar_lembretes_de_prazo(agora)
        self.assertEqual(
            services_entregas.enviar_lembretes_de_prazo(agora + timedelta(minutes=50)), 0
        )
        self.assertEqual(Notificacoes.objects.filter(not_usu=self.aluno.alu).count(), 1)

    def test_comando_enviar_lembretes_entrega(self):
        self.entrega.tma_data_limite = timezone.now() + timedelta(days=7)
        self.entrega.save(update_fields=["tma_data_limite"])
        saida = StringIO()
        call_command("enviar_lembretes_entrega", stdout=saida)
        self.assertIn("1 lembrete(s)", saida.getvalue())
        self.assertTrue(Notificacoes.objects.filter(not_usu=self.aluno.alu).exists())

    def url_entrega_do_aluno(self):
        return reverse("cadastro:entrega_enviar", args=[self.turma.pk, self.entrega.pk])


class ConcorrenciaEnviarEntregaTest(TransactionTestCase):
    """Dois testes de corrida (research C7, achado A1 da análise `/speckit-analyze`).

    Usa `TransactionTestCase` (não `TestCase`): os dois testes abrem conexões de banco reais em
    threads separadas, e `TestCase` embrulha o teste numa transação não confirmada, invisível às
    outras conexões. `serialized_rollback=True` restaura, depois do `flush`, os dados carregados
    pelas migrações de dados (Cursos etc., usados por `criar_turma_de`).
    [US-15][research C7]
    """

    serialized_rollback = True

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        self.aluno = matricular_aluno(
            self.turma, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        )
        self.entrega = cadastrar_entrega(
            self.turma,
            tipo=TipoEntrega.DOCUMENTO_PARA_DEFESA,
            titulo="Entrega do Documento",
            data_limite=timezone.now() + timedelta(days=10),
        )
        # `cadastrar_entrega` (apoio_tcc) só cria a Turmas_Marcos; o registro do aluno
        # ("Aguardando Envio") é quem o serviço cadastrar_entrega/criar_entregas_do_aluno criaria
        # na vida real — aqui a fábrica de teste cria direto, como o resto da suíte faz.
        EntregasMarcos.objects.create(
            ent_tma=self.entrega, ent_alu=self.aluno, ent_status=StatusEntrega.AGUARDANDO_ENVIO
        )

    def registro(self):
        return EntregasMarcos.objects.get(ent_tma=self.entrega, ent_alu=self.aluno)

    def test_duas_chamadas_quase_simultaneas_produzem_um_unico_primeiro_envio(self):
        """Duas threads enviando o link quase ao mesmo tempo: a trava em `Entregas_Marcos`
        serializa as duas transações, e o primeiro envio salvo no banco (não necessariamente o
        que "chegou primeiro" na CPU, mas sempre um só) decide o status — nunca os dois ao mesmo
        tempo, nunca nenhum. [research C7]
        """
        erros = []
        barreira = threading.Barrier(2)

        def enviar(link):
            try:
                barreira.wait(timeout=5)
                services_entregas.enviar_entrega(self.aluno, self.entrega.pk, link)
            except Exception as exc:  # pragma: no cover - diagnóstico de falha do teste
                erros.append(exc)
            finally:
                close_old_connections()

        threads = [
            threading.Thread(target=enviar, args=(LINK_VALIDO,)),
            threading.Thread(target=enviar, args=(LINK_SUBSTITUTO,)),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(erros, [])
        self.assertEqual(HistoricoEnviosEntregas.objects.filter(hen_ent=self.registro()).count(), 2)
        # Só um status final, calculado por um único "primeiro envio" (o mais antigo gravado).
        primeiro = (
            HistoricoEnviosEntregas.objects.filter(hen_ent=self.registro())
            .order_by("hen_data_envio", "hen_id")
            .first()
        )
        esperado = (
            StatusEntrega.ENTREGUE
            if primeiro.hen_data_envio <= self.entrega.tma_data_limite
            else StatusEntrega.ENTREGUE_COM_ATRASO
        )
        self.assertEqual(self.registro().ent_status, esperado)

    def test_enviar_entrega_concorrendo_com_encerrar_participacao_nao_libera_envio_depois(self):
        """`enviar_entrega` não pode enviar depois que `encerrar_participacao` já travou e
        encerrou a participação do aluno — a trava em `TCCs` garante que uma das duas operações
        vê o Status já atualizado (research C7, achado A1). [research C7]
        """
        services_turmas.encerrar_participacao(
            self.professor, self.turma.pk, self.aluno.pk, StatusTCC.DESISTENTE, "Desistência"
        )
        with self.assertRaises(Http404):
            services_entregas.enviar_entrega(self.aluno, self.entrega.pk, LINK_VALIDO)
        self.assertFalse(HistoricoEnviosEntregas.objects.filter(hen_ent=self.registro()).exists())
