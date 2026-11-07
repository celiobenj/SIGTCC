"""US-33 fluxo D: relatório de Artigos (cenário 2.5).

[US-33][RBN-REL-02.2][RBN-CAD-10.5][RBN-CAD-12.1][RBN-CAD-12.3][FR-065][FR-066][SC-001]
(tasks T029 e T034)
"""

from datetime import datetime

from django.db import connection
from django.http import QueryDict
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from sigtcc.apps.cadastro.choices import (
    Homologacao,
    ModalidadeTCC,
    QualisCapes,
    StatusOrientacao,
    StatusSubmissao,
)
from sigtcc.apps.cadastro.models import TCCs
from sigtcc.apps.cadastro.tests.apoio_contas import coordenador_de, docente_de
from sigtcc.apps.cadastro.tests.apoio_orientacao import vincular_orientador
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, SI, criar_turma_de
from sigtcc.apps.relatorios import mensagens, registro, services_relatorios
from sigtcc.apps.relatorios.estrutura import Celula
from sigtcc.apps.relatorios.forms import FiltroRelatorioForm
from sigtcc.apps.relatorios.tests.apoio_relatorios import (
    LINK_HOSTIL,
    TesteRelatorios,
    aluno_com_status,
    artigo,
)

ID = "artigos"


class TesteArtigos(TesteRelatorios):
    """TCCs na modalidade Artigo Científico."""

    def setUp(self):
        super().setUp()
        self.coordenador = coordenador_de(EC)
        self.professor = docente_de(EC)
        self.turma = criar_turma_de(self.professor, ano=2026, semestre=2)

    def tcc_artigo(self, **dados):
        tcc = aluno_com_status(self.turma, **dados)
        TCCs.objects.filter(pk=tcc.pk).update(tcc_modalidade=ModalidadeTCC.ARTIGO_CIENTIFICO)
        return TCCs.objects.get(pk=tcc.pk)

    def consulta(self, texto="ano_semestre=2026-2"):
        form = FiltroRelatorioForm(
            QueryDict(texto), usuario=self.coordenador, registrado=registro.obter(ID)
        )
        self.assertTrue(form.is_valid(), form.errors)
        return services_relatorios.artigos(self.coordenador, form.filtros())

    def test_cenario_5_colunas(self):
        """2.5: Título, Aluno, Orientador, Veículo, Estrato, Status, Aproveitamento e Link."""
        orientador = docente_de(EC)
        tcc = self.tcc_artigo(orientador=orientador, nome="Aluna do Artigo")
        registro_artigo = artigo(
            tcc, status=StatusSubmissao.PUBLICADO, homologacao=Homologacao.HOMOLOGADO
        )
        registro_artigo.art_veiculo_publicacao = "Revista Brasileira de Computação"
        registro_artigo.art_qualis_capes = QualisCapes.A1
        registro_artigo.save()
        self.client.force_login(self.coordenador)
        resposta = self.client.get(reverse("relatorios:relatorio", args=[ID]))
        relatorio = resposta.context["relatorio"]
        self.assertEqual(
            [coluna.rotulo for coluna in relatorio.colunas],
            [
                "Título do TCC",
                "Aluno",
                "Orientador",
                "Veículo",
                "Estrato Qualis/CAPES",
                "Status de Submissão",
                "Aproveitamento",
                "Link ou DOI",
            ],
        )
        valores = relatorio.linhas[0].valores
        self.assertEqual(valores["aluno"], "Aluna do Artigo")
        self.assertEqual(valores["orientador"], orientador.usu_nome)
        self.assertEqual(valores["veiculo"], "Revista Brasileira de Computação")
        self.assertEqual(valores["qualis"], QualisCapes.A1)
        self.assertEqual(valores["status"], "Publicado")
        self.assertEqual(valores["aproveitamento"], "Homologado")
        self.assertContains(
            resposta,
            '<a href="https://doi.org/10.1000/teste" target="_blank" '
            'rel="noopener noreferrer">https://doi.org/10.1000/teste</a>',
        )

    def test_tcc_sem_registro_de_publicacao(self):
        """Edge Case: aparece, com células vazias e a MR-14."""
        self.tcc_artigo()
        valores = self.consulta().linhas[0].valores
        self.assertEqual(valores["veiculo"], "")
        self.assertEqual(valores["link"], "")
        self.assertEqual(valores["aproveitamento"], mensagens.MR14_APROVEITAMENTO_SEM_ANALISE)

    def test_aproveitamento_sem_analise(self):
        """MR-14: com artigo ainda sem decisão."""
        artigo(self.tcc_artigo(), status=StatusSubmissao.SUBMETIDO)
        self.assertEqual(
            self.consulta().linhas[0].valores["aproveitamento"],
            "Aguardando aceite ou publicação",
        )

    def test_orientador_ativo_mais_recente_ou_nenhum(self):
        """FR-065: vínculo ativo; sem ele, o mais recente; sem nenhum, "Sem orientador"."""
        ativo, antigo, recente = docente_de(EC), docente_de(EC), docente_de(EC)
        tcc = self.tcc_artigo(nome="A")
        velha = vincular_orientador(tcc, antigo, quando=datetime(2026, 9, 1, 8))
        velha.ori_status = StatusOrientacao.ENCERRADA
        velha.save()
        vincular_orientador(tcc, ativo, quando=datetime(2026, 8, 1, 8))
        encerrado = self.tcc_artigo(nome="B")
        for docente, dia in ((antigo, 1), (recente, 20)):
            orientacao = vincular_orientador(encerrado, docente, quando=datetime(2026, 9, dia, 8))
            orientacao.ori_status = StatusOrientacao.ENCERRADA
            orientacao.save()
        self.tcc_artigo(nome="C")
        linhas = self.consulta().linhas
        self.assertEqual(
            [linha.valores["orientador"] for linha in linhas],
            [ativo.usu_nome, recente.usu_nome, "Sem orientador"],
        )

    def test_monografia_fora(self):
        """Edge Case: o TCC que virou Monografia mantém a linha em Artigos, mas não entra."""
        tcc = self.tcc_artigo()
        artigo(tcc, status=StatusSubmissao.PUBLICADO)
        TCCs.objects.filter(pk=tcc.pk).update(tcc_modalidade=ModalidadeTCC.MONOGRAFIA)
        self.assertEqual(self.consulta().linhas, ())

    def test_link_so_com_https(self):
        """FR-066: outro conteúdo é texto, sem <a>."""
        artigo(self.tcc_artigo(), link=LINK_HOSTIL)
        celula = self.consulta().linhas[0].valores["link"]
        self.assertEqual(celula, Celula(LINK_HOSTIL))
        self.client.force_login(self.coordenador)
        resposta = self.client.get(reverse("relatorios:relatorio", args=[ID]))
        self.assertNotContains(resposta, 'href="javascript:')

    def test_curso_e_periodo(self):
        """Filtros Período letivo e Curso."""
        turma_si = criar_turma_de(self.professor, curso_nome=SI)
        tcc_si = aluno_com_status(turma_si)
        TCCs.objects.filter(pk=tcc_si.pk).update(tcc_modalidade=ModalidadeTCC.ARTIGO_CIENTIFICO)
        self.tcc_artigo()
        self.assertEqual(len(self.consulta().linhas), 1)
        self.assertEqual(len(self.consulta("curso=todos").linhas), 2)
        self.assertEqual(len(self.consulta("ano_semestre=2026-2&curso=todos").linhas), 2)

    def test_kpis_sem_grafico(self):
        """FR-072: Artigos, Publicados e Homologados, sem gráfico."""
        artigo(
            self.tcc_artigo(),
            status=StatusSubmissao.PUBLICADO,
            homologacao=Homologacao.HOMOLOGADO,
        )
        artigo(self.tcc_artigo(), status=StatusSubmissao.SUBMETIDO)
        self.tcc_artigo()
        relatorio = self.consulta()
        self.assertEqual(
            [(kpi.rotulo, kpi.valor) for kpi in relatorio.kpis],
            [("Artigos", 3), ("Publicados", 1), ("Homologados", 1)],
        )
        self.assertIsNone(relatorio.grafico)

    def test_sem_registros(self):
        """E2: sem TCC de artigo no período."""
        self.client.force_login(self.coordenador)
        resposta = self.client.get(reverse("relatorios:relatorio", args=[ID]))
        self.assertContains(resposta, "Nenhum registro encontrado para os filtros selecionados")

    def test_sem_consulta_por_linha(self):
        """SC-001: Orientador por subconsulta."""

        def medir():
            form = FiltroRelatorioForm(
                QueryDict(""), usuario=self.coordenador, registrado=registro.obter(ID)
            )
            self.assertTrue(form.is_valid())
            filtros = form.filtros()
            with CaptureQueriesContext(connection) as contexto:
                services_relatorios.artigos(self.coordenador, filtros)
            return len(contexto)

        artigo(self.tcc_artigo(orientador=docente_de(EC)))
        antes = medir()
        for _ in range(5):
            artigo(self.tcc_artigo(orientador=docente_de(EC)))
        self.assertEqual(medir(), antes)
