"""Campos próprios para tipos do dicionário de dados que o Django não gera sozinho.

[infraestrutura da feature 001, sem US específica][FR-002]
"""

from django.db import models


class CharFixoField(models.CharField):
    """Texto de tamanho fixo: gera CHAR(n) em vez de VARCHAR(n).

    Usado nas matrículas de 10 dígitos (alu_matricula, ouv_matricula), research R4.
    """

    description = "Texto de tamanho fixo (CHAR)"

    def db_type(self, connection):
        """Tipo da coluna no PostgreSQL: char com o max_length do campo."""
        return f"char({self.max_length})"


class TimestampField(models.DateTimeField):
    """Data e hora sem fuso: gera TIMESTAMP em vez de timestamp with time zone.

    O DateTimeField do Django sempre gera timestamptz no PostgreSQL, com qualquer USE_TZ.
    Usado nas 21 colunas TIMESTAMP do dicionário, com USE_TZ = False (research R1).
    """

    description = "Data e hora sem fuso (TIMESTAMP)"

    def db_type(self, connection):
        """Tipo da coluna no PostgreSQL: timestamp without time zone."""
        return "timestamp"
