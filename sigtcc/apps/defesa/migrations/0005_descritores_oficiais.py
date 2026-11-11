"""Troca os descritores provisórios pelos oficiais da planilha da EST/UEA (FR-014a; Q-03 e Q-18).

Os descritores oficiais têm até 704 caracteres, mais que o VARCHAR(255) do dicionário 18/10: as
três colunas passam a VARCHAR(1000) (o dicionário foi ajustado junto). Nome, componente, peso e
identificador dos critérios não mudam. Ao reverter, os textos provisórios voltam antes de a coluna
encolher.

[US-25][RBN-DEF-04.1][FR-014a][SC-007]
"""

from django.db import migrations, models

from sigtcc.apps.defesa import cargas, descritores_oficiais


def aplicar_descritores_oficiais(apps, schema_editor):
    """Grava os 27 descritores oficiais. Antes, recarrega os 9 critérios da 0004 (carga
    idempotente): um `popular_demo` anterior à v0.3.0 esvaziava "Criterios", e o banco do Render
    ficou sem eles (hotfix v0.3.1). Com os critérios presentes, nada muda.
    [US-25][RBN-DEF-04.1][FR-014a]
    """
    cargas.carregar_criterios_provisorios(apps, schema_editor)
    criterios = apps.get_model("defesa", "Criterios")
    for nome, descritores in descritores_oficiais.DESCRITORES_OFICIAIS.items():
        if criterios.objects.filter(cri_nome=nome).update(**descritores) != 1:
            raise RuntimeError(f"Critério ausente ou duplicado: {nome}")


def voltar_descritores_provisorios(apps, schema_editor):
    """Restaura os textos provisórios da 0004 (cabem em 255 caracteres)."""
    criterios = apps.get_model("defesa", "Criterios")
    criterios.objects.filter(cri_nome__in=list(descritores_oficiais.DESCRITORES_OFICIAIS)).update(
        **cargas.DESCRITORES_PROVISORIOS
    )


class Migration(migrations.Migration):

    dependencies = [
        ("defesa", "0004_carga_criterios_provisorios"),
    ]

    operations = [
        migrations.AlterField(
            model_name="criterios",
            name="cri_desc_exemplar",
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name="criterios",
            name="cri_desc_competente",
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name="criterios",
            name="cri_desc_necessita_trabalho",
            field=models.CharField(max_length=1000),
        ),
        migrations.RunPython(aplicar_descritores_oficiais, voltar_descritores_provisorios),
    ]
