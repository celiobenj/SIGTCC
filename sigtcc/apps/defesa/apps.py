"""Configuração do app de defesa (Épico 2).

[infraestrutura da feature 001, sem US específica]
"""

from django.apps import AppConfig


class DefesaConfig(AppConfig):
    """Configuração do app que guarda as 9 tabelas do Épico 2 (research R9)."""

    name = "sigtcc.apps.defesa"
    label = "defesa"
    verbose_name = "Defesa"
