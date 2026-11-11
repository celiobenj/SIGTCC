"""Início automático das sessões de defesa (US-24 D): muda para "Em Andamento" as sessões
"Agendada" ou "Reagendada" cujo horário marcado já chegou. As telas da Defesa fazem o mesmo ao
abrir; o comando garante a transição sem ninguém abrir o sistema. Agendar a cada minuto no
servidor (PGCS 9.4; o agendamento no GitHub Actions é item de configuração do Célio, Q-79).
Idempotente.

Exemplo: python manage.py iniciar_sessoes

[US-24][RBN-DEF-01.2][FR-021]
"""

from django.core.management.base import BaseCommand

from sigtcc.apps.defesa import services_defesa


class Command(BaseCommand):
    """Comando iniciar_sessoes. [US-24][RBN-DEF-01.2][FR-021]"""

    help = "Muda para 'Em Andamento' as sessões de defesa cujo horário marcado já chegou."

    def handle(self, *args, **opcoes):
        """Aplica o início automático e informa quantas sessões começaram. [US-24][FR-021]"""
        iniciadas = services_defesa.iniciar_sessoes_vencidas()
        self.stdout.write(f"Sessões iniciadas: {iniciadas}")
