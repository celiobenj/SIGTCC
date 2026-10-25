"""Configuração do app de cadastro (Épico 1).

[infraestrutura da feature 001, sem US específica]
"""

from django.apps import AppConfig


class CadastroConfig(AppConfig):
    """Configuração do app que guarda as 27 tabelas do Épico 1 (research R9)."""

    name = "sigtcc.apps.cadastro"
    label = "cadastro"
    verbose_name = "Cadastro"
