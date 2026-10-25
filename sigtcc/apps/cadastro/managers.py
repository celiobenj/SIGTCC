"""Gerenciador do modelo Usuarios (research D1; contrato modelos-orm.md, seção 3).

[US-10][RBN-CAD-06.3][US-11][RBN-CAD-06.4]
"""

from django.contrib.auth.base_user import BaseUserManager

from sigtcc.apps.cadastro.choices import StatusConta


class UsuariosManager(BaseUserManager):
    """Cria usuários com e-mail opcional e senha só como hash. Sem create_superuser (D1)."""

    def create_user(self, usu_email, usu_nome, password=None, **campos):
        """Cria um usuário.

        O e-mail passa por normalize_email e, se ficar vazio, é gravado como None: o Django
        devolve "" para None, e e-mail sem valor nunca é gravado como texto vazio (FR-007, R3).
        Sem senha, a conta fica 'Aguardando Ativação' com a senha nula (dicionário, 3.2.1).
        """
        email = self.normalize_email(usu_email) if usu_email else ""
        if email.strip() == "":
            email = None
        campos.setdefault("usu_status", StatusConta.AGUARDANDO_ATIVACAO)
        usuario = self.model(usu_email=email, usu_nome=usu_nome, **campos)
        if password:
            usuario.set_password(password)
        else:
            usuario.password = None
        usuario.save(using=self._db)
        return usuario
