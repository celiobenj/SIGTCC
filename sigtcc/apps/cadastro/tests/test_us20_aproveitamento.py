"""Testes de aceite da US-20: homologar ou recusar o aproveitamento do artigo (spec 006, User
Story 9).

Cenários 1 a 9 da US-20 (nota mínima dos cenários 1 e 3 pela consulta do FR-039, SC-004) e os
pontos de contato #10 e #11 (Q16), mais: POST direto fora das regras (404), MO-21, turma
arquivada (D11), TCC 1 copiado fora da lista, ?curso= inválido, link com noopener e o log.

[US-20][RBN-CAD-12.2][RBN-CAD-12.3][RBN-CAD-14.1][RBN-DEF-06.4][FR-037 a FR-039][Q16][D11]
(tasks T051)
"""

from django.urls import reverse

from sigtcc.apps.cadastro import mensagens, services_artigos
from sigtcc.apps.cadastro.choices import Homologacao, ModalidadeTCC, StatusTCC, StatusTurma
from sigtcc.apps.cadastro.models import Artigos, Coordenadores
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo
from sigtcc.apps.cadastro.tests.apoio_orientacao import (
    liberar_resultado,
    salvar_artigo,
    vincular_orientador,
)
from sigtcc.apps.cadastro.tests.apoio_tcc import salvar_proposta
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    SI,
    TesteTurmas,
    criar_turma_de,
    curso,
    matricular_aluno,
    tcc_de,
)


def coordenador_de(nome_curso):
    """Docente Coordenador do curso da carga (Coordenadores: um por curso)."""
    docente = criar_docente_ativo(curso=curso(nome_curso))
    Coordenadores.objects.update_or_create(
        cor_cur=curso(nome_curso), defaults={"cor_doc": docente.docentes}
    )
    return docente


class AproveitamentoTest(TesteTurmas):
    """Artigos Aceitos em EC e SI; Coordenador de EC. [US-20]"""

    def setUp(self):
        super().setUp()
        self.coordenador = coordenador_de(EC)
        self.professor = criar_docente_ativo()
        self.tcc_ec = self._artigo(EC, qualis="A2", status="Publicado")
        self.tcc_si = self._artigo(SI, qualis="B1", status="Aceito")
        self.client.force_login(self.coordenador)

    def _artigo(self, nome_curso, qualis, status, homologacao=Homologacao.EM_ANALISE):
        turma = criar_turma_de(self.professor, curso_nome=nome_curso)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        tcc = tcc_de(aluno, turma)
        salvar_proposta(tcc, modalidade=ModalidadeTCC.ARTIGO_CIENTIFICO)
        vincular_orientador(tcc, criar_docente_ativo())
        salvar_artigo(tcc, qualis=qualis, status=status, art_homologacao=homologacao)
        return tcc

    def tela(self, curso_param=None):
        url = reverse("cadastro:aproveitamento_artigos")
        return self.client.get(url + (f"?curso={curso_param}" if curso_param else ""))

    def decidir(self, rota, tcc, follow=True):
        return self.client.post(reverse(f"cadastro:{rota}", args=[tcc.pk]), follow=follow)

    def artigo(self, tcc):
        return Artigos.objects.get(art=tcc)

    def test_cenario1_homologa_e_nota_minima(self):
        with self.assertLogs("sigtcc.acesso") as log:
            with self.captureOnCommitCallbacks(execute=True):
                resposta = self.decidir("homologar_artigo", self.tcc_ec)
        self.assertContains(resposta, mensagens.APROVEITAMENTO_HOMOLOGADO)
        artigo = self.artigo(self.tcc_ec)
        self.assertEqual(artigo.art_homologacao, Homologacao.HOMOLOGADO)
        self.assertEqual(artigo.art_homologado_por_id, self.coordenador.pk)
        self.assertTrue(services_artigos.tem_artigo_homologado_qualis_ab(self.tcc_ec))
        self.assertIn("APROVEITAMENTO_HOMOLOGADO", log.output[0])
        self.assertIn(f"tcc_id={self.tcc_ec.pk}", log.output[0])

    def test_cenario2_recusa(self):
        resposta = self.decidir("recusar_artigo", self.tcc_ec)
        self.assertContains(resposta, mensagens.APROVEITAMENTO_RECUSADO)
        self.assertEqual(self.artigo(self.tcc_ec).art_homologacao, Homologacao.RECUSADO)
        self.assertFalse(services_artigos.tem_artigo_homologado_qualis_ab(self.tcc_ec))

    def test_cenario3_qualis_c_sem_nota_minima(self):
        Artigos.objects.filter(art=self.tcc_ec).update(art_qualis_capes="C")
        self.decidir("homologar_artigo", self.tcc_ec)
        self.assertFalse(services_artigos.tem_artigo_homologado_qualis_ab(self.tcc_ec))

    def test_cenario4_recusa_antes_da_liberacao(self):
        self.decidir("homologar_artigo", self.tcc_ec)
        self.decidir("recusar_artigo", self.tcc_ec)
        self.assertEqual(self.artigo(self.tcc_ec).art_homologacao, Homologacao.RECUSADO)

    def test_cenario5_alterado_aparece_em_analise(self):
        Artigos.objects.filter(art=self.tcc_ec).update(art_homologacao=Homologacao.EM_ANALISE)
        self.assertContains(self.tela(), Homologacao.EM_ANALISE)

    def test_cenario6_sem_sessao(self):
        self.client.logout()
        resposta = self.tela()
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("cadastro:entrar"), resposta.url)

    def test_cenario7_outro_curso_sem_botoes(self):
        resposta = self.tela(curso(SI).pk)
        self.assertContains(resposta, self.tcc_si.tcc_titulo)
        self.assertNotContains(resposta, ">Homologar<")
        self.assertNotContains(resposta, ">Recusar<")
        self.assertEqual(
            self.decidir("homologar_artigo", self.tcc_si, follow=False).status_code, 404
        )

    def test_filtro_inicia_no_curso_do_coordenador(self):
        resposta = self.tela()
        self.assertContains(resposta, ">Homologar<")
        linhas = resposta.context["linhas"]
        self.assertEqual([linha["tcc"].pk for linha in linhas], [self.tcc_ec.pk])

    def test_curso_invalido_vira_o_do_coordenador(self):
        resposta = self.tela("abc")
        self.assertEqual(resposta.context["curso"], str(curso(EC).pk))

    def test_cenario8_recusar_indisponivel_depois_da_liberacao(self):
        self.decidir("homologar_artigo", self.tcc_ec)
        liberar_resultado(self.tcc_ec, self.professor, novo_status=StatusTCC.EM_ANDAMENTO)
        resposta = self.tela()
        self.assertContains(resposta, 'class="btn perigo" disabled>Recusar')
        resposta = self.decidir("recusar_artigo", self.tcc_ec)
        self.assertContains(resposta, mensagens.MO21_RESULTADO_LIBERADO)
        self.assertEqual(self.artigo(self.tcc_ec).art_homologacao, Homologacao.HOMOLOGADO)

    def test_cenario9_docente_sem_item_no_menu(self):
        self.client.force_login(criar_docente_ativo())
        painel = self.client.get(reverse("cadastro:painel"))
        self.assertNotContains(painel, "Aproveitamento de artigos")
        self.assertEqual(self.tela().status_code, 403)

    def test_ponto10_em_analise_depois_da_liberacao_tem_botoes(self):
        liberar_resultado(self.tcc_ec, self.professor, novo_status=StatusTCC.EM_ANDAMENTO)
        resposta = self.tela()
        self.assertContains(resposta, ">Homologar<")
        self.assertContains(resposta, ">Recusar<")

    def test_ponto11_alteracao_depois_da_liberacao_volta_a_em_analise(self):
        self.decidir("homologar_artigo", self.tcc_ec)
        liberar_resultado(self.tcc_ec, self.professor, novo_status=StatusTCC.EM_ANDAMENTO)
        aluno = self.tcc_ec.tcc_alu
        self.client.force_login(aluno.alu)
        services_artigos.salvar_publicacao(
            aluno.alu,
            self.tcc_ec.pk,
            {"link": "https://doi.org/x", "qualis": "A1", "status": "Publicado"},
        )
        self.assertEqual(self.artigo(self.tcc_ec).art_homologacao, Homologacao.EM_ANALISE)

    def test_turma_arquivada_ainda_decide_d11(self):
        turma = self.tcc_ec.tcc_tur
        turma.tur_status = StatusTurma.ARQUIVADA
        turma.save()
        self.decidir("homologar_artigo", self.tcc_ec)
        self.assertEqual(self.artigo(self.tcc_ec).art_homologacao, Homologacao.HOMOLOGADO)

    def test_post_direto_fora_das_regras_404(self):
        Artigos.objects.filter(art=self.tcc_ec).update(art_status_submissao="Em Revisão")
        self.assertEqual(
            self.decidir("homologar_artigo", self.tcc_ec, follow=False).status_code, 404
        )
        self.tcc_ec.tcc_modalidade = ModalidadeTCC.MONOGRAFIA
        self.tcc_ec.save()
        self.assertEqual(self.decidir("recusar_artigo", self.tcc_ec, follow=False).status_code, 404)
        url = reverse("cadastro:homologar_artigo", args=[999999])
        self.assertEqual(self.client.post(url).status_code, 404)

    def test_link_abrir_com_noopener(self):
        self.assertContains(self.tela(), 'target="_blank" rel="noopener noreferrer">abrir')

    def test_get_nao_decide(self):
        url = reverse("cadastro:homologar_artigo", args=[self.tcc_ec.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
