"""Configuração do app de relatórios (Épico 3).

[infraestrutura da feature 001, sem US específica]
"""

from django.apps import AppConfig


class RelatoriosConfig(AppConfig):
    """Configuração do app de relatórios, que só consulta os modelos de cadastro e defesa (R9)."""

    name = "sigtcc.apps.relatorios"
    label = "relatorios"
    verbose_name = "Relatórios"

    def ready(self):
        """Carrega as consultas, que se registram pelo decorador (spec 010, IC-07; contrato §1).

        A feat-11 acrescenta aqui o seu módulo (spec 011, IC-01).
        [US-31][US-47][US-32][US-33][US-48][US-49][US-34][US-35][FR-003]
        """
        from . import services_operacionais, services_relatorios  # noqa: F401
