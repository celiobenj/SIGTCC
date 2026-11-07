"""US-32 fluxo A: Histórico de indicadores do NUCOMP (cenários 4.1 e 4.2).

[US-32][RBN-REL-02.4][RBN-CAD-08.7][RBN-CAD-12.1][FR-050][FR-051][FR-052][SC-001]
(tasks T040 e T042)
"""

from datetime import date

from django.db import connection
from django.http import QueryDict
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    ModalidadeTCC,
    StatusSubmissao,
    StatusTCC,
)
from sigtcc.apps.cadastro.models import TCCs, Turmas
from sigtcc.apps.cadastro.tests.apoio_contas import coordenador_de, docente_de
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, SI, criar_turma_de
from sigtcc.apps.relatorios import registro, services_relatorios
from sigtcc.apps.relatorios.forms import FiltroRelatorioForm
from sigtcc.apps.relatorios.tests.apoio_relatorios import (
    TesteRelatorios,
    aluno_com_status,
    artigo,
    banca_de,
    registrar_status,
    sessao_realizada,
)

ID = "historico-nucomp"
LINK = "https://doi.org/10.1000/artigo"


class TesteHistorico(TesteRelatorios):
    """Períodos 2025/2, 2026/1 e 2026/2 em Engenharia de Computação."""

    def setUp(self):
        super().setUp()
        self.coordenador = coordenador_de(EC)
        self.professor = docente_de(EC)
        self.t1 = criar_turma_de(self.professor, ano=2025, semestre=2)
        self.t2 = criar_turma_de(self.professor, ano=2026, semestre=1)
        self.t3 = criar_turma_de(self.professor, ano=2026, semestre=2)
        self.url = reverse("relatorios:relatorio", args=[ID])

    def consulta(self, texto=""):
        form = FiltroRelatorioForm(
            QueryDict(texto), usuario=self.coordenador, registrado=registro.obter(ID)
        )
        self.assertTrue(form.is_valid(), form.errors)
        return services_relatorios.historico_nucomp(self.coordenador, form.filtros())

    def linha(self, relatorio, periodo):
        return next(i for i in relatorio.linhas if i.valores["periodo"] == periodo).valores

    def tcc_artigo(self, turma, **dados):
        tcc = aluno_com_status(turma, **dados)
        TCCs.objects.filter(pk=tcc.pk).update(tcc_modalidade=ModalidadeTCC.ARTIGO_CIENTIFICO)
        return TCCs.objects.get(pk=tcc.pk)

    def test_cenario_1_linhas_em_ordem_sem_filtro_de_periodo(self):
        """4.1: 3 linhas, de 2025/2 a 2026/2, só com o filtro Curso."""
        self.client.force_login(self.coordenador)
        resposta = self.client.get(self.url)
        relatorio = resposta.context["relatorio"]
        self.assertEqual(
            [item.valores["periodo"] for item in relatorio.linhas],
            ["2025/2", "2026/1", "2026/2"],
        )
        self.assertEqual(
            [coluna.rotulo for coluna in relatorio.colunas],
            [
                "Período letivo",
                "Alunos Vinculados",
                "Defesas Realizadas",
                "Artigos Publicados",
                "Desistências",
            ],
        )
        self.assertEqual(list(resposta.context["form"].fields), ["curso"])

    def test_indicadores_por_periodo(self):
        """FR-051: vínculos, sessões Realizadas pela turma e Desistências pelo histórico."""
        tcc = aluno_com_status(self.t2)
        aluno_com_status(self.t2)
        desiste = aluno_com_status(self.t3)
        registrar_status(desiste, StatusTCC.DESISTENTE)
        membros = banca_de(self.professor, docente_de(EC), docente_de(EC))
        sessao_realizada(tcc, membros, date(2026, 9, 1))
        relatorio = self.consulta()
        valores = self.linha(relatorio, "2026/1")
        self.assertEqual((valores["vinculados"], valores["defesas"]), (2, 1))
        valores = self.linha(relatorio, "2026/2")
        self.assertEqual((valores["vinculados"], valores["desistencias"]), (1, 1))

    def test_artigo_copiado_conta_uma_vez(self):
        """FR-052: no primeiro período do aluno com Publicado."""
        tcc1 = self.tcc_artigo(self.t2)
        turma2 = criar_turma_de(
            self.professor, descricao=DescricaoTurma.TCC_2, ano=2026, semestre=2
        )
        tcc2 = self.tcc_artigo(turma2, aluno=tcc1.tcc_alu)
        artigo(tcc1, status=StatusSubmissao.PUBLICADO, link=LINK)
        artigo(tcc2, status=StatusSubmissao.PUBLICADO, link=LINK)
        relatorio = self.consulta()
        self.assertEqual(self.linha(relatorio, "2026/1")["artigos"], 1)
        self.assertEqual(self.linha(relatorio, "2026/2")["artigos"], 0)

    def test_publicado_so_na_copia_conta_no_tcc2(self):
        """FR-052: TCC 1 Aceito e TCC 2 Publicado contam no período do Publicado."""
        tcc1 = self.tcc_artigo(self.t2)
        tcc2 = self.tcc_artigo(self.t3, aluno=tcc1.tcc_alu)
        artigo(tcc1, status=StatusSubmissao.ACEITO, link=LINK)
        artigo(tcc2, status=StatusSubmissao.PUBLICADO, link=LINK)
        self.assertEqual(self.linha(self.consulta(), "2026/2")["artigos"], 1)

    def test_link_editado_conta_dois(self):
        """R11: limite conhecido, explicado em "Como é calculado"."""
        tcc1 = self.tcc_artigo(self.t2)
        tcc2 = self.tcc_artigo(self.t3, aluno=tcc1.tcc_alu)
        artigo(tcc1, status=StatusSubmissao.PUBLICADO, link=LINK)
        artigo(tcc2, status=StatusSubmissao.PUBLICADO, link=LINK + "-novo")
        relatorio = self.consulta()
        self.assertEqual(self.linha(relatorio, "2026/1")["artigos"], 1)
        self.assertEqual(self.linha(relatorio, "2026/2")["artigos"], 1)

    def test_monografia_fora(self):
        """Edge Case: TCC que virou Monografia não conta."""
        artigo(aluno_com_status(self.t3), status=StatusSubmissao.PUBLICADO)
        self.assertEqual(self.linha(self.consulta(), "2026/2")["artigos"], 0)

    def test_periodo_sem_turma_do_curso_com_zeros(self):
        """Edge Case: a linha do período aparece com zeros."""
        criar_turma_de(self.professor, curso_nome=SI, ano=2024, semestre=1)
        aluno_com_status(self.t3)
        relatorio = self.consulta()
        self.assertEqual(relatorio.linhas[0].valores["periodo"], "2024/1")
        self.assertEqual(relatorio.linhas[0].valores["vinculados"], 0)

    def test_filtro_curso(self):
        """Só o curso escolhido; Todos soma."""
        aluno_com_status(self.t3)
        aluno_com_status(criar_turma_de(self.professor, curso_nome=SI))
        self.assertEqual(self.linha(self.consulta(), "2026/2")["vinculados"], 1)
        self.assertEqual(self.linha(self.consulta("curso=todos"), "2026/2")["vinculados"], 2)

    def test_kpis_do_ultimo_periodo_e_grafico(self):
        """FR-072: último período e linhas em SVG, com Artigos tracejado."""
        aluno_com_status(self.t3)
        relatorio = self.consulta()
        self.assertEqual(relatorio.kpis[0].valor, 1)
        self.assertEqual(relatorio.kpis[0].rotulo, "Vinculados")
        self.assertEqual(relatorio.grafico.tipo, "linhas")
        self.client.force_login(self.coordenador)
        resposta = self.client.get(self.url)
        self.assertContains(resposta, "<polyline", count=4)
        self.assertContains(resposta, "tracejada")
        self.assertContains(resposta, 'viewBox="0 0 640 240"')

    def test_sem_nenhum_periodo(self):
        """Edge Case: segue a E2 da US-32."""
        Turmas.objects.all().delete()
        self.client.force_login(self.coordenador)
        resposta = self.client.get(self.url)
        self.assertContains(resposta, "Nenhum registro encontrado para os filtros selecionados")
        self.assertIsNone(resposta.context["relatorio"].grafico)

    def test_sem_consulta_por_linha(self):
        """SC-001: sem depender do número de períodos."""

        def medir():
            form = FiltroRelatorioForm(
                QueryDict(""), usuario=self.coordenador, registrado=registro.obter(ID)
            )
            self.assertTrue(form.is_valid())
            filtros = form.filtros()
            with CaptureQueriesContext(connection) as contexto:
                services_relatorios.historico_nucomp(self.coordenador, filtros)
            return len(contexto)

        antes = medir()
        for ano in range(2015, 2022):
            aluno_com_status(criar_turma_de(self.professor, ano=ano, semestre=1))
        self.assertEqual(medir(), antes)
