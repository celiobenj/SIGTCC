"""Muda para 'Expirada' as contas de Membro Externo 'Ativa' com a validade vencida (FR-040).

Agendar uma vez por dia, depois da meia-noite (America/Manaus), no servidor (índice Q-67, item 4;
Q-70). Idempotente: conta a conta, com a conta travada e a validade relida
(services.expirar_se_vencida; research C15), para não expirar uma conta prorrogada no mesmo
instante. Imprime só a quantidade expirada. O diagrama ExecutarTarefasAgendadas (Vida do TCC) chama
a mesma expiração; a rotina única pode usar este comando ou services.expirar_se_vencida.

Exemplo:
    python manage.py expirar_membros_externos

[US-06][RBN-CAD-03.3][FR-040][SC-006][research C15]
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from sigtcc.apps.cadastro.choices import StatusConta
from sigtcc.apps.cadastro.models import Usuarios
from sigtcc.apps.cadastro.services import expirar_se_vencida


class Command(BaseCommand):
    """Comando expirar_membros_externos. [FR-040]"""

    help = "Muda para 'Expirada' as contas de Membro Externo com a validade vencida."

    def handle(self, *args, **opcoes):
        """Expira cada candidata numa transação curta e informa a quantidade. [FR-040][SC-006]"""
        candidatas = Usuarios.objects.filter(
            usu_status=StatusConta.ATIVA,
            membrosexternos__mem_validade_ate__lt=timezone.now().date(),
        ).order_by("pk")
        expiradas = sum(1 for conta in candidatas if expirar_se_vencida(conta))
        self.stdout.write(f"Contas expiradas: {expiradas}")
