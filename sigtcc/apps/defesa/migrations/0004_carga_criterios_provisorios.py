"""Carga inicial dos 9 critérios oficiais com descritores provisórios (data migration).

Os descritores serão trocados pelos oficiais numa migração nova antes do TP3 (FR-014a).

[US-25][RBN-DEF-04.1][FR-014][spec 001, US3 cenário 2]
"""

from django.db import migrations

from sigtcc.apps.defesa import cargas


class Migration(migrations.Migration):

    dependencies = [
        ("defesa", "0003_restricoes_defesa"),
    ]

    operations = [
        migrations.RunPython(cargas.carregar_criterios_provisorios, cargas.remover_criterios),
    ]
