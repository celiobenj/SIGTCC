"""Testes de aceite da US-46: registrar a publicação do artigo (spec 006, User Story 8).

Cenários 1 a 8 da US-46, mais: alteração depois da liberação também volta a "Em Análise" (Q16),
etiqueta MO-22, domínios de Qualis e Status, Monografia sem apagar o registro (D10), rota do
Orientador só para o Orientador atual e decisão desfeita no log (D10).

[US-46][RBN-CAD-12.1][RBN-CAD-12.3][FR-034 a FR-036][Q16][D10] (tasks T047)
"""

from django.urls import reverse

from sigtcc.apps.cadastro import mensagens, services_artigos
from sigtcc.apps.cadastro.choices import (
    Homologacao,
    ModalidadeTCC,
    StatusConta,
    StatusTCC,
    StatusTurma,
)
from sigtcc.apps.cadastro.models import Artigos
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_coordenador, criar_docente_ativo
from sigtcc.apps.cadastro.tests.apoio_orientacao import (
    liberar_resultado,
    salvar_artigo,
    vincular_coorientador,
    vincular_orientador,
)
from sigtcc.apps.cadastro.tests.apoio_tcc import salvar_proposta
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    SI,
    TesteTurmas,
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)

LINK = "https://doi.org/10.1000/artigo"


class PublicacaoTest(TesteTurmas):
    """TCC Artigo Científico com orientador. [US-46]"""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=SI)
        self.aluno = matricular_aluno(
            self.turma, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        )
        self.tcc = tcc_de(self.aluno, self.turma)
        salvar_proposta(self.tcc, modalidade=ModalidadeTCC.ARTIGO_CIENTIFICO)
        self.orientador = criar_docente_ativo()
        vincular_orientador(self.tcc, self.orientador)
        self.client.force_login(self.aluno.alu)

    def salvar(self, **campos):
        dados = {"veiculo": "Revista X", "link": LINK, "qualis": "B1", "status": "Aceito"}
        dados.update(campos)
        url = reverse("cadastro:salvar_publicacao_aluno", args=[self.turma.pk])
        return self.client.post(url, dados, follow=True)

    def artigo(self):
        return Artigos.objects.get(art=self.tcc)

    def test_cenario1_aluno_salva_e_fica_em_analise(self):
        resposta = self.salvar()
        self.assertContains(resposta, mensagens.PUBLICACAO_SALVA)
        self.assertEqual(self.artigo().art_homologacao, Homologacao.EM_ANALISE)
        self.assertContains(resposta, Homologacao.EM_ANALISE)
        self.assertEqual(resposta.redirect_chain[-1][0].split("?")[1], "secao=publicacao")

    def test_cenario2_orientador_salva_pela_linha(self):
        self.client.force_login(self.orientador)
        url = reverse("cadastro:publicacao_orientando", args=[self.tcc.pk])
        self.assertContains(self.client.get(url), "Salvar publicação")
        self.client.post(url, {"link": LINK, "status": "Publicado", "qualis": "A2"})
        self.assertEqual(self.artigo().art_status_submissao, "Publicado")

    def test_cenario3_em_revisao_fora_da_tela_do_coordenador(self):
        self.salvar(status="Em Revisão")
        coordenador = criar_coordenador()
        self.assertEqual(services_artigos.artigos_para_analise(coordenador, None), [])

    def test_cenario4_mudar_qualis_desfaz_homologacao(self):
        salvar_artigo(
            self.tcc, qualis="B1", status="Aceito", art_homologacao=Homologacao.HOMOLOGADO
        )
        with self.assertLogs("sigtcc.acesso") as log:
            with self.captureOnCommitCallbacks(execute=True):
                self.salvar(qualis="A1")
        self.assertEqual(self.artigo().art_homologacao, Homologacao.EM_ANALISE)
        self.assertIn("APROVEITAMENTO_DESFEITO", log.output[0])

    def test_q16_mudar_depois_da_liberacao_tambem_desfaz(self):
        salvar_artigo(
            self.tcc, qualis="B1", status="Aceito", art_homologacao=Homologacao.HOMOLOGADO
        )
        liberar_resultado(self.tcc, self.professor, novo_status=StatusTCC.EM_ANDAMENTO)
        self.salvar(qualis="A1")
        self.assertEqual(self.artigo().art_homologacao, Homologacao.EM_ANALISE)

    def test_veiculo_sozinho_nao_desfaz(self):
        salvar_artigo(
            self.tcc, qualis="B1", status="Aceito", art_homologacao=Homologacao.HOMOLOGADO
        )
        self.salvar(
            veiculo="Outra revista",
            qualis="B1",
            status="Aceito",
            link="https://doi.org/10.1000/teste",
        )
        self.assertEqual(self.artigo().art_homologacao, Homologacao.HOMOLOGADO)

    def test_cenario5_sem_sessao(self):
        self.client.logout()
        self.assertEqual(
            self.client.get(reverse("cadastro:meu_tcc", args=[self.turma.pk])).status_code, 302
        )

    def test_cenario6_link_invalido(self):
        for link in ("http://inseguro.example", ""):
            with self.subTest(link=link):
                resposta = self.salvar(link=link)
                self.assertContains(resposta, mensagens.LINK_HTTPS_500)
        self.assertFalse(Artigos.objects.exists())

    def test_cenario7_veiculo_acima_do_limite(self):
        resposta = self.salvar(veiculo="x" * 151)
        self.assertContains(resposta, mensagens.MO19_VEICULO)
        self.assertFalse(Artigos.objects.exists())

    def test_cenario8_monografia_sem_secao_e_sem_apagar(self):
        salvar_artigo(self.tcc)
        self.tcc.tcc_modalidade = ModalidadeTCC.MONOGRAFIA
        self.tcc.save()
        resposta = self.client.get(reverse("cadastro:meu_tcc", args=[self.turma.pk]))
        self.assertNotContains(resposta, 'id="publicacao"')
        self.assertTrue(Artigos.objects.filter(art=self.tcc).exists())

    def test_etiqueta_mo22_sem_analise(self):
        self.salvar(status="Submetido")
        resposta = self.client.get(reverse("cadastro:meu_tcc", args=[self.turma.pk]))
        self.assertContains(resposta, mensagens.MO22_AGUARDANDO_PUBLICACAO)

    def test_dominios_de_qualis_e_status(self):
        self.salvar(qualis="Z9")
        self.salvar(status="Inventado")
        self.assertFalse(Artigos.objects.exists())

    def test_rota_do_orientador_restrita(self):
        coorientador = criar_docente_ativo()
        vincular_coorientador(self.tcc, docente=coorientador)
        self.client.force_login(coorientador)
        url = reverse("cadastro:publicacao_orientando", args=[self.tcc.pk])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_login(self.orientador)
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save()
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_turma_arquivada_mt25(self):
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save()
        resposta = self.salvar()
        self.assertContains(resposta, mensagens.MT25_TURMA_ARQUIVADA)
        self.assertFalse(Artigos.objects.exists())
