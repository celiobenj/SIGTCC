"""Comando enviar_lembretes_entrega: lembretes de prazo das entregas (spec 005, T022).

Envia, aos alunos que ainda não enviaram, o lembrete 7 dias, 48 horas e 24 horas antes da Data
Limite, exceto em turma arquivada (fluxo alternativo E da US-15). Toda a regra fica em
`services_entregas.enviar_lembretes_de_prazo`; este comando só a chama.

Pendência de configuração (research C5; Célio Benjamim): agendar a execução **a cada hora**
(cron, Agendador de Tarefas do Windows ou serviço de hospedagem), já que a janela de cada prazo
tem margem de ±1h. Até o agendamento existir, o comando pode ser rodado à mão:
`python manage.py enviar_lembretes_entrega`.

[US-15][RBN-CAD-09.6][FR-022][research C5]
"""

from django.core.management.base import BaseCommand

from sigtcc.apps.cadastro import services_entregas


class Command(BaseCommand):
    """Comando enviar_lembretes_entrega. [US-15][FR-022]"""

    help = "Envia os lembretes de prazo das entregas (7 dias, 48h e 24h antes da Data Limite)."

    def handle(self, *args, **opcoes):
        """Chama o serviço e informa quantos lembretes foram enviados. [FR-022][research C5]"""
        enviados = services_entregas.enviar_lembretes_de_prazo()
        self.stdout.write(f"{enviados} lembrete(s) de prazo enviado(s).")
