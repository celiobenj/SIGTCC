"""Base do módulo Relatórios: viabilidade das consultas no PostgreSQL.

[US-32][RBN-CAD-08.7][research R5][research R6] (tasks T002)
"""

from django.db import connection
from django.db.models import Count, OuterRef, Q, Subquery, Value
from django.db.models.functions import Coalesce

from sigtcc.apps.cadastro.choices import StatusTCC
from sigtcc.apps.cadastro.models import AlunosTurmas, HistoricoStatusTCC
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, SI, criar_turma_de, matricular_aluno
from sigtcc.apps.defesa.tests.apoio_defesa import docente
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
