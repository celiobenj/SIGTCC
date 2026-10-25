"""FK composta Avaliacoes(ava_def_id, ava_usu_id) → Banca_Defesa(ban_def_id, ban_usu_id).

Escrita à mão: o Django 5.2 não permite relacionamento para modelo com chave primária composta,
então a restrição do dicionário (3.6.6) é criada por SQL. Fica numa migração própria para não se
perder se a 0001_initial for gerada de novo antes do merge. DEFERRABLE INITIALLY DEFERRED, como as
FKs criadas pelo Django (research D3 e R5).

[US-25][RBN-DEF-05.2][US-23][RBN-DEF-02.1][spec 001, US1 cenário 3][FR-005]
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("defesa", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                'ALTER TABLE "Avaliacoes" ADD CONSTRAINT fk_avaliacoes_banca_defesa '
                'FOREIGN KEY (ava_def_id, ava_usu_id) REFERENCES "Banca_Defesa" '
                "(ban_def_id, ban_usu_id) ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;"
            ),
            reverse_sql='ALTER TABLE "Avaliacoes" DROP CONSTRAINT fk_avaliacoes_banca_defesa;',
        ),
    ]
