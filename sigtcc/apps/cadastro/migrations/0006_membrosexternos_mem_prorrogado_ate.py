"""Coluna MembrosExternos.mem_prorrogado_ate: data dada pela última prorrogação manual.

Aprovada pela autora do dicionário (índice Q-69; spec 002, Clarifications Q36); a cópia do
dicionário em docs/fonte/ foi atualizada no mesmo commit (princípio III).

[US-50][US-06][RBN-CAD-03.3][FR-039][FR-043]
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cadastro", "0005_carga_equivalencia_cursos"),
    ]

    operations = [
        migrations.AddField(
            model_name="membrosexternos",
            name="mem_prorrogado_ate",
            field=models.DateField(blank=True, null=True),
        ),
    ]
