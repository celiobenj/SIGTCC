"""Base do módulo Relatórios: viabilidade das consultas no PostgreSQL, estrutura e registro.

[US-31][US-32][RBN-REL-01.1][RBN-CAD-08.7][FR-003][FR-018][FR-066][research R5][research R6]
(tasks T002, T004 e T005)
"""

from datetime import date
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.db.models import Count, OuterRef, Q, Subquery, Value
from django.db.models.functions import Coalesce
from django.test import SimpleTestCase

from sigtcc.apps.cadastro.choices import StatusTCC
from sigtcc.apps.cadastro.models import AlunosTurmas, HistoricoStatusTCC
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, SI, criar_turma_de, matricular_aluno
from sigtcc.apps.defesa.tests.apoio_defesa import docente
from sigtcc.apps.relatorios import registro
from sigtcc.apps.relatorios.estrutura import (
    Coluna,
    Kpi,
    Linha,
    Relatorio,
    SubLista,
    link_seguro,
)
from sigtcc.apps.relatorios.registro import relatorio
from sigtcc.apps.relatorios.tests.apoio_relatorios import (
    TesteRelatorios,
    aluno_com_status,
    registrar_status,
)


class TesteViabilidadeDaConsulta(TesteRelatorios):
    """Subconsulta do último registro em Count(filter=...) sobre values(): research R5, R6."""

    def _consulta(self):
        """Uma linha por curso, com o Status por período. [US-32][RBN-CAD-08.7]"""
        ultimo = (
            HistoricoStatusTCC.objects.filter(
                hst_tcc__tcc_alu=OuterRef("mat_alu"), hst_tcc__tcc_tur=OuterRef("mat_tur")
            )
            .order_by("-hst_data_hora", "-hst_id")
            .values("hst_status_novo")[:1]
        )
        return (
            AlunosTurmas.objects.annotate(
                status=Coalesce(Subquery(ultimo), Value(StatusTCC.SEM_PROPOSTA.value))
            )
            .values("mat_tur__tur_cur")
            .annotate(
                matriculados=Count("mat_alu"),
                sem_proposta=Count("mat_alu", filter=Q(status=StatusTCC.SEM_PROPOSTA)),
                ativos=Count("mat_alu", filter=Q(status=StatusTCC.EM_ANDAMENTO)),
                sem_sucesso=Count("mat_alu", filter=Q(status=StatusTCC.DESISTENTE)),
            )
            .order_by("mat_tur__tur_cur")
        )

    def test_uma_linha_por_curso_com_o_ultimo_registro(self):
        """R5 e R6: agrupa só pelo curso e lê o último registro de cada TCC."""
        professor = docente()
        turma_ec = criar_turma_de(professor, curso_nome=EC)
        turma_si = criar_turma_de(professor, curso_nome=SI)
        aluno_com_status(turma_ec, StatusTCC.EM_ANDAMENTO)
        tcc = aluno_com_status(turma_ec, StatusTCC.EM_ANDAMENTO)
        registrar_status(tcc, StatusTCC.DESISTENTE)
        matricular_aluno(turma_si)
        linhas = list(self._consulta())
        self.assertEqual(len(linhas), 2)
        por_curso = {linha["mat_tur__tur_cur"]: linha for linha in linhas}
        ec = por_curso[turma_ec.tur_cur_id]
        self.assertEqual(
            (ec["matriculados"], ec["ativos"], ec["sem_sucesso"], ec["sem_proposta"]),
            (2, 1, 1, 0),
        )
        self.assertEqual(por_curso[turma_si.tur_cur_id]["sem_proposta"], 1)

    def test_explain_do_postgresql(self):
        """R6: o PostgreSQL aceita a subconsulta correlacionada dentro de FILTER."""
        plano = self._consulta().explain()
        self.assertIn("Aggregate", plano)
        self.assertEqual(connection.vendor, "postgresql")


class TesteEstrutura(SimpleTestCase):
    """Estrutura única: valor canônico, células ordenadas e link (contrato §3). [FR-018][FR-066]"""

    COLUNAS = (Coluna("nome", "Nome"), Coluna("total", "Total", numerica=True))

    def test_recusa_valor_fora_do_canonico(self):
        """bool, date e None não entram: a tela e o arquivo divergiriam."""
        for valor in (True, None, date(2026, 11, 5), 1.5):
            with self.subTest(valor=valor), self.assertRaises(TypeError):
                Linha({"nome": valor})

    def test_celulas_na_ordem_das_colunas(self):
        """A ordem vem das colunas, não do dicionário, e toda célula é Celula."""
        celulas = Linha({"total": 3, "nome": "Ana"}).celulas(self.COLUNAS)
        self.assertEqual([(c.texto, c.numerica) for c in celulas], [("Ana", False), (3, True)])

    def test_valor_ausente_sai_vazio(self):
        """Vazio é "", nunca "-", que ganharia a proteção de fórmula no CSV."""
        self.assertEqual(Linha({}).celulas(self.COLUNAS)[0].texto, "")

    def test_link_seguro_so_com_https(self):
        """FR-066: só https com netloc vira link; o resto é texto."""
        self.assertEqual(link_seguro("https://doi.org/10.1/x").url, "https://doi.org/10.1/x")
        for valor in (
            "http://doi.org/x",
            "javascript:alert(1)",
            "https://",
            "10.1000/xyz",
            "https://a.b/c d",
            "https://[",
        ):
            with self.subTest(valor=valor):
                celula = link_seguro(valor)
                self.assertIsNone(celula.url)
                self.assertEqual(celula.texto, valor)

    def test_tem_registros_deriva_das_linhas(self):
        """Sem sobrescrever, sem linhas é sem registros."""
        self.assertFalse(Relatorio(self.COLUNAS, ()).tem_registros)
        self.assertTrue(Relatorio(self.COLUNAS, (Linha({"nome": "A"}),)).tem_registros)
        zerado = Relatorio(self.COLUNAS, (Linha({"total": 0}),), tem_registros=False)
        self.assertFalse(zerado.tem_registros)

    def test_no_maximo_quatro_kpis(self):
        """FR-072: no máximo 4 KPIs."""
        with self.assertRaises(ValueError):
            Relatorio(self.COLUNAS, (), kpis=tuple(Kpi(str(n), n) for n in range(5)))

    def test_sublistas_exigem_a_coluna_da_linha_mae(self):
        """Contrato §3: sem rotulo_linha, o arquivo não saberia a linha-mãe."""
        sublista = SubLista("Bancas", (Coluna("data", "Data"),), ())
        with self.assertRaises(ValueError):
            Relatorio(self.COLUNAS, (Linha({"nome": "A"}, sublistas=(sublista,)),))

    def test_linhas_prontas_resolvem_as_sublistas(self):
        """A sub-lista chega pronta, com destaque, para o template e os exportadores."""
        colunas = (Coluna("data", "Data"),)
        item = Linha({"data": "05/11/2026"}, destaque=True)
        sublista = SubLista("Bancas", colunas, (item,))
        relatorio = Relatorio(
            self.COLUNAS, (Linha({"nome": "A"}, sublistas=(sublista,)),), rotulo_linha="nome"
        )
        pronta = relatorio.linhas_prontas()[0].sublistas[0]
        self.assertEqual(pronta.linhas[0].celulas[0].texto, "05/11/2026")
        self.assertTrue(pronta.linhas[0].destaque)
        self.assertEqual(relatorio.rotulo_da_linha_mae(), "Nome")


class TesteRegistro(SimpleTestCase):
    """Registro por decorador; erro de declaração falha ao carregar (R13). [FR-003][FR-004]"""

    def _registrar(self, id="exemplo", perfis=("coordenador",), filtros=("curso",)):
        return relatorio(id, "Exemplo", "Descrição", "Frase", perfis, filtros, 90)(
            lambda u, f: None
        )

    def test_registra_e_obtem(self):
        """O decorador devolve a função e guarda a declaração."""
        with mock.patch.dict(registro._RELATORIOS, clear=False):
            self._registrar()
            self.assertEqual(registro.obter("exemplo").nome, "Exemplo")
        self.assertIsNone(registro.obter("exemplo"))

    def test_declaracao_invalida_nao_carrega(self):
        """Perfis vazios abririam a todos: tem_perfil sem perfis é verdadeiro."""
        casos = (
            {"perfis": ()},
            {"perfis": ["coordenador"]},
            {"perfis": ("reitor",)},
            {"filtros": ("turma",)},
            {"id": "Com Espaco"},
        )
        for caso in casos:
            with self.subTest(caso=caso), mock.patch.dict(registro._RELATORIOS):
                with self.assertRaises(ImproperlyConfigured):
                    self._registrar(**caso)

    def test_id_repetido_nao_carrega(self):
        """Um id só por relatório."""
        with mock.patch.dict(registro._RELATORIOS):
            self._registrar()
            with self.assertRaises(ImproperlyConfigured):
                self._registrar()
