"""Carga inicial dos 3 cursos do NUCOMP (data migration).

[US-39][RBN-CAD-14.1][FR-013][spec 001, US3 cenário 1]
"""

from django.db import migrations

from sigtcc.apps.cadastro import cargas


class Migration(migrations.Migration):

    dependencies = [
        ("cadastro", "0002_restricoes_cadastro"),
    ]

    operations = [
        migrations.RunPython(cargas.carregar_cursos, cargas.remover_cursos),
    ]
