"""Testes de aceite da US-42: indicar que o TCC está apto para defesa (spec 006, User Story 5).

Cenários 1 a 8 da US-42, mais: condição mudada entre o GET e o POST (MO-20), Coorientador e turma
arquivada (404) e o orientador automático (R10).

[US-42][RBN-CAD-11.5][RBN-CAD-08.3][FR-026][FR-027][SC-007] (tasks T037)
"""

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services_orientacao
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    GatilhoStatusTCC,
    OrigemOrientacao,
    StatusEntrega,
    StatusTCC,
    StatusTurma,
    TipoEntrega,
)
from sigtcc.apps.cadastro.models import (
    AreasInteresse,
    EntregasMarcos,
    HistoricoStatusTCC,
    PalavrasChaveTCC,
)
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo
from sigtcc.apps.cadastro.tests.apoio_orientacao import vincular_coorientador, vincular_orientador
from sigtcc.apps.cadastro.tests.apoio_tcc import cadastrar_entrega
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    SI,
    TesteTurmas,
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)


class AptoTest(TesteTurmas):
    """TCC "Em Andamento", Documento para Defesa Entregue, Área e duas Palavras-Chave."""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=SI)
        self.aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        self.tcc = tcc_de(self.aluno, self.turma)
        self.orientador = criar_docente_ativo()
        vincular_orientador(self.tcc, self.orientador)
        self.entrega = cadastrar_entrega(
            self.turma,
            tipo=TipoEntrega.DOCUMENTO_PARA_DEFESA,
            data_limite=timezone.now() + timedelta(days=3),
        )
        self.registro = EntregasMarcos.objects.create(
            ent_tma=self.entrega, ent_alu=self.aluno, ent_status=StatusEntrega.ENTREGUE
        )
        self.tcc.tcc_ari = AreasInteresse.objects.first()
        self.tcc.save()
        for palavra in ("Django", "Testes"):
            PalavrasChaveTCC.objects.create(pal_tcc=self.tcc, pal_palavra=palavra)
        self.client.force_login(self.orientador)

    def url(self):
        return reverse("cadastro:indicar_apto", args=[self.tcc.pk])

    def tela(self):
        return self.client.get(reverse("cadastro:orientacoes"))

    def test_cenario1_indica_apto(self):
        confirmacao = self.client.get(self.url())
        self.assertContains(
            confirmacao, mensagens.CONFIRMAR_APTO.format(nome=self.aluno.alu.usu_nome)
        )
        resposta = self.client.post(self.url(), follow=True)
        self.assertContains(resposta, mensagens.TCC_INDICADO_APTO)
        self.tcc.refresh_from_db()
        self.assertEqual(self.tcc.tcc_status, StatusTCC.APTO_PARA_DEFESA)
        historico = HistoricoStatusTCC.objects.get(
            hst_tcc=self.tcc, hst_gatilho=GatilhoStatusTCC.INDICACAO_DE_APTO
        )
        self.assertEqual(historico.hst_usu_id, self.orientador.pk)

    def test_cenario2_cancelar_volta_sem_mudar(self):
        confirmacao = self.client.get(self.url())
        self.assertContains(confirmacao, f'href="{reverse("cadastro:orientacoes")}"')
        self.tcc.refresh_from_db()
        self.assertEqual(self.tcc.tcc_status, StatusTCC.EM_ANDAMENTO)

    def test_cenario3_coorientador_sem_botao(self):
        coorientador = criar_docente_ativo()
        vincular_coorientador(self.tcc, docente=coorientador)
        self.client.force_login(coorientador)
        self.assertNotContains(self.tela(), self.url())
        self.assertEqual(self.client.post(self.url()).status_code, 404)

    def test_cenario4_sem_sessao(self):
        self.client.logout()
        resposta = self.client.get(reverse("cadastro:orientacoes"))
        self.assertEqual(resposta.status_code, 302)

    def test_cenario5_documento_nao_entregue_indisponivel(self):
        self.registro.ent_status = StatusEntrega.NAO_ENTREGUE
        self.registro.save()
        resposta = self.tela()
        self.assertNotContains(resposta, f'href="{self.url()}"')
        self.assertContains(resposta, "Apto para Defesa</button>")
        self.assertEqual(self.client.get(self.url()).status_code, 404)

    def test_cenario6_sem_palavras_indisponivel(self):
        PalavrasChaveTCC.objects.filter(pal_tcc=self.tcc).delete()
        self.assertEqual(services_orientacao.estado_apto_do_tcc(self.tcc), "indisponivel")

    def test_cenario7_ja_apto_sem_botao(self):
        self.tcc.tcc_status = StatusTCC.APTO_PARA_DEFESA
        self.tcc.save()
        resposta = self.tela()
        self.assertNotContains(resposta, "Apto para Defesa</button>")
        self.assertNotContains(resposta, f'href="{self.url()}"')
        self.assertContains(resposta, 'class="chip verde">Apto para Defesa')

    def test_cenario8_sem_entrega_cadastrada(self):
        self.registro.delete()
        self.entrega.delete()
        resposta = self.tela()
        self.assertContains(resposta, mensagens.ENTREGA_DOCUMENTO_NAO_CADASTRADA)

    def test_condicao_mudada_entre_get_e_post_mo20(self):
        self.client.get(self.url())
        self.registro.ent_status = StatusEntrega.DEVOLVIDA_PARA_AJUSTE
        self.registro.save()
        resposta = self.client.post(self.url(), follow=True)
        self.assertContains(resposta, mensagens.MO20_APTO_CONDICOES)
        self.tcc.refresh_from_db()
        self.assertEqual(self.tcc.tcc_status, StatusTCC.EM_ANDAMENTO)

    def test_turma_arquivada_404(self):
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save()
        self.assertEqual(self.client.get(self.url()).status_code, 404)

    def test_orientador_automatico_usa_o_botao(self):
        turma2 = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        aluno2 = matricular_aluno(turma2, status_tcc=StatusTCC.EM_ANDAMENTO)
        tcc2 = tcc_de(aluno2, turma2)
        vincular_orientador(tcc2, self.professor, origem=OrigemOrientacao.AUTOMATICO)
        entrega = cadastrar_entrega(turma2, tipo=TipoEntrega.DOCUMENTO_PARA_DEFESA)
        EntregasMarcos.objects.create(
            ent_tma=entrega, ent_alu=aluno2, ent_status=StatusEntrega.ENTREGUE_COM_ATRASO
        )
        tcc2.tcc_ari = AreasInteresse.objects.first()
        tcc2.save()
        PalavrasChaveTCC.objects.create(pal_tcc=tcc2, pal_palavra="IA")
        self.client.force_login(self.professor)
        self.client.post(reverse("cadastro:indicar_apto", args=[tcc2.pk]))
        tcc2.refresh_from_db()
        self.assertEqual(tcc2.tcc_status, StatusTCC.APTO_PARA_DEFESA)
