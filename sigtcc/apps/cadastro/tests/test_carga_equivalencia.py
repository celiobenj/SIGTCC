"""Carga da equivalência de cursos (spec 004, FR-015a; Clarifications Q5).

[US-08][RBN-CAD-05.7][FR-015a][Q5]
"""

from django.apps import apps as registro
from django.db import connection
from django.test import TestCase

from sigtcc.apps.cadastro import cargas
from sigtcc.apps.cadastro.models import EquivalenciaCursos


class CargaEquivalenciaTest(TestCase):
    """Os três códigos definitivos, carga idempotente e reversão só deles. [FR-015a]"""

    def mapa(self):
        return {e.eqc_codigo_uea: e.eqc_cur.cur_nome for e in EquivalenciaCursos.objects.all()}

    def test_tres_codigos_carregados(self):
        """EST08MCPD, EST31MSII e EST03MLV ligados aos três cursos do NUCOMP."""
        self.assertEqual(
            self.mapa(),
            {
                "EST08MCPD": "Engenharia de Computação",
                "EST31MSII": "Sistemas de Informação",
                "EST03MLV": "Licenciatura em Computação",
            },
        )

    def test_reaplicar_nao_duplica(self):
        """Rodar a carga de novo não cria nem altera registros."""
        cargas.carregar_equivalencia_cursos(registro, None)
        self.assertEqual(EquivalenciaCursos.objects.count(), 3)

    def test_reverter_apaga_so_os_tres(self):
        """A reversão apaga só os códigos carregados."""
        outro = EquivalenciaCursos.objects.first().eqc_cur
        EquivalenciaCursos.objects.create(eqc_codigo_uea="OUTRO01", eqc_cur=outro)
        with connection.schema_editor() as editor:
            cargas.remover_equivalencia_cursos(registro, editor)
        self.assertEqual(
            list(EquivalenciaCursos.objects.values_list("eqc_codigo_uea", flat=True)), ["OUTRO01"]
        )
