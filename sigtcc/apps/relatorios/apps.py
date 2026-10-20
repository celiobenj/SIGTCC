"""Configuração do app de relatórios (Épico 3).

[infraestrutura da feature 001, sem US específica]
"""

from django.apps import AppConfig


class RelatoriosConfig(AppConfig):
    """Configuração do app de relatórios, que só consulta os modelos de cadastro e defesa (R9)."""

    name = "sigtcc.apps.relatorios"
    label = "relatorios"
    verbose_name = "Relatórios"
