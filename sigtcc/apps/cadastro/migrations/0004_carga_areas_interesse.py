"""Carga inicial das 10 Áreas de Interesse (data migration).

[US-13][RBN-CAD-08.1][FR-015][spec 001, US3 cenário 3]
"""

from django.db import migrations

from sigtcc.apps.cadastro import cargas


class Migration(migrations.Migration):

    dependencies = [
        ("cadastro", "0003_carga_cursos"),
    ]

    operations = [
        migrations.RunPython(cargas.carregar_areas_interesse, cargas.remover_areas_interesse),
    ]
