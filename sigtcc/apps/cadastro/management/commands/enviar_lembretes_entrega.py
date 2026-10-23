"""Comando enviar_lembretes_entrega: rotina agendada das entregas (spec 005, T022 e T044).

Em cada execução: (1) grava "Não Entregue" nas entregas "Aguardando Envio" com a Data Limite já
vencida, em turma não arquivada (FR-020; dicionário 18/10, seção 4, item 7; Q-90); (2) envia, aos
alunos que ainda não enviaram, o lembrete 7 dias, 48 horas e 24 horas antes da Data Limite, no
sistema e por e-mail, exceto em turma arquivada e para quem tem a participação encerrada (fluxo
alternativo E da US-15; FR-022). Toda a regra fica em `services_entregas`; este comando só a chama.

Pendência de configuração (research C5; Q-86; Célio Benjamim): agendar a execução **a cada hora**
(cron, Agendador de Tarefas do Windows ou serviço de hospedagem), já que a janela de cada prazo
tem margem de ±1h. Até o agendamento existir, o comando pode ser rodado à mão:
`python manage.py enviar_lembretes_entrega`.

[US-15][RBN-CAD-09.3][RBN-CAD-09.6][FR-020][FR-022][research C5]
"""

from django.core.management.base import BaseCommand

from sigtcc.apps.cadastro import services_entregas


class Command(BaseCommand):
    """Comando enviar_lembretes_entrega. [US-15][FR-020][FR-022]"""

    help = (
        "Grava 'Não Entregue' nas entregas vencidas sem envio e envia os lembretes de prazo "
        "(7 dias, 48h e 24h antes da Data Limite)."
    )

    def handle(self, *args, **opcoes):
        """Marca as entregas vencidas, envia os lembretes e informa as quantidades.

        [FR-020][FR-022][research C5]
        """
        marcadas = services_entregas.marcar_nao_entregues()
        enviados = services_entregas.enviar_lembretes_de_prazo()
        self.stdout.write(f"{marcadas} entrega(s) marcada(s) como Não Entregue.")
        self.stdout.write(f"{enviados} lembrete(s) de prazo enviado(s).")
