"""Backend de autenticação do SIGTCC (research A1).

A senha não é conferida aqui: a ordem das verificações do login (US-11) fica em
services.autenticar. Este backend só carrega o usuário da sessão a cada requisição e derruba a
sessão de conta que deixou de estar 'Ativa' ou ficou com a validade vencida.

[US-11][RBN-CAD-06.4][RBN-CAD-03.3][Q4][Q18]
"""

from django.contrib.auth.backends import ModelBackend

from sigtcc.apps.cadastro.choices import StatusConta
from sigtcc.apps.cadastro.models import Usuarios
from sigtcc.apps.cadastro.permissoes import validade_vencida


class SigtccBackend(ModelBackend):
    """Único backend em AUTHENTICATION_BACKENDS. [US-11][RBN-CAD-06.4]"""

    def authenticate(self, request, **credenciais):
        """Sempre None: nem authenticate() nem Client.login() pulam a ordem e o bloqueio (A1)."""
        return None

    def get_user(self, user_id):
        """Carrega o usuário com as quatro especializações numa consulta só (A1, I9)."""
        try:
            usuario = Usuarios.objects.select_related(
                "alunos", "docentes", "membrosexternos", "secretarios"
            ).get(pk=user_id)
        except Usuarios.DoesNotExist:
            return None
        return usuario if self.user_can_authenticate(usuario) else None

    def user_can_authenticate(self, user):
        """Só conta 'Ativa' e com a validade em dia mantém a sessão. [US-11][Q4][RBN-CAD-03.3]"""
        return user.usu_status == StatusConta.ATIVA and not validade_vencida(user)
