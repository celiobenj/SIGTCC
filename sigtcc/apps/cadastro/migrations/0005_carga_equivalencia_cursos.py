"""Carga da equivalência entre códigos de curso da UEA e cursos do NUCOMP (data migration).

Só dados: nenhuma mudança de esquema (spec 004, FR-028).

[US-08][RBN-CAD-05.7][spec 004, FR-015a][Q5]
"""

from django.db import migrations

from sigtcc.apps.cadastro import cargas


class Migration(migrations.Migration):

    dependencies = [
        ("cadastro", "0004_carga_areas_interesse"),
    ]

    operations = [
        migrations.RunPython(
            cargas.carregar_equivalencia_cursos, cargas.remover_equivalencia_cursos
        ),
    ]
