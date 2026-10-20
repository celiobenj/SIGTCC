"""Comportamento do modelo Usuarios e do e-mail opcional (contrato modelos-orm.md, seção 3).

[US-10][RBN-CAD-06.3][US-11][RBN-CAD-06.4][US-45][RBN-CAD-10.3][spec 001, US2 cenários 7 e 11]
[FR-007]
"""

from django.db import connection
from django.test import TestCase

from sigtcc.apps.cadastro.choices import StatusConta
from sigtcc.apps.cadastro.models import CoorientadoresExternos, Usuarios


def email_e_nulo(tabela, coluna_id, coluna_email, valor_id):
    """Confere no próprio banco se o e-mail ficou NULL (e não texto vazio)."""
    with connection.cursor() as cursor:
        cursor.execute(
            f'SELECT {coluna_email} IS NULL FROM "{tabela}" WHERE {coluna_id} = %s', [valor_id]
        )
        return cursor.fetchone()[0]


class EmailVazioTest(TestCase):
    """E-mail sem valor é gravado como NULL, nunca como texto vazio (FR-007; aprovação de R3)."""

    def test_cenario11_email_vazio_vira_nulo(self):
        """Dado um e-mail "" ou só com espaços, quando o registro é salvo, então fica NULL."""
        for valor in ("", "   "):
            with self.subTest(modelo="Usuarios", valor=repr(valor)):
                usuario = Usuarios.objects.create(
                    usu_nome="Aluno sem e-mail",
                    usu_email=valor,
                    usu_status=StatusConta.AGUARDANDO_ATIVACAO,
                )
                self.assertIsNone(usuario.usu_email)
                self.assertTrue(email_e_nulo("Usuarios", "usu_id", "usu_email", usuario.usu_id))
            with self.subTest(modelo="CoorientadoresExternos", valor=repr(valor)):
                externo = CoorientadoresExternos.objects.create(
                    cext_nome="Coorientador", cext_email=valor
                )
                self.assertIsNone(externo.cext_email)
                self.assertTrue(
                    email_e_nulo("CoorientadoresExternos", "cext_id", "cext_email", externo.cext_id)
                )

    def test_cenario7_dois_alunos_sem_email(self):
        """Vários Alunos sem e-mail antes do primeiro acesso coexistem (create_user)."""
        criados = [
            Usuarios.objects.create_user(None, "Aluno A"),
            Usuarios.objects.create_user(None, "Aluno B"),
            Usuarios.objects.create_user("", "Aluno C"),
            Usuarios.objects.create_user("", "Aluno D"),
        ]
        for usuario in criados:
            self.assertTrue(email_e_nulo("Usuarios", "usu_id", "usu_email", usuario.usu_id))


class UsuariosTest(TestCase):
    """create_user, senha, is_active e representação em texto (research D1)."""

    def test_create_user_sem_senha(self):
        """Sem senha: senha nula, não utilizável, conta 'Aguardando Ativação'."""
        usuario = Usuarios.objects.create_user("docente@uea.edu.br", "Docente")
        self.assertIsNone(usuario.password)
        self.assertFalse(usuario.has_usable_password())
        self.assertEqual(usuario.usu_status, StatusConta.AGUARDANDO_ATIVACAO)
        # Sem senha, nenhuma senha confere (o Django puro levantaria TypeError; research D1).
        self.assertFalse(usuario.check_password("qualquer"))

    def test_create_user_com_senha(self):
        """Com senha: guardada só como hash (constituição, princípio VII)."""
        usuario = Usuarios.objects.create_user(
            "secretaria@uea.edu.br",
            "Secretaria",
            password="senha-forte-123",
            usu_status=StatusConta.ATIVA,
        )
        usuario.refresh_from_db()
        self.assertNotEqual(usuario.password, "senha-forte-123")
        self.assertTrue(usuario.check_password("senha-forte-123"))

    def test_create_user_normaliza_dominio(self):
        """O domínio do e-mail é normalizado para minúsculas pelo normalize_email do Django."""
        usuario = Usuarios.objects.create_user("Pessoa@UEA.EDU.BR", "Pessoa")
        self.assertEqual(usuario.usu_email, "Pessoa@uea.edu.br")

    def test_is_active_por_status(self):
        """Só a conta 'Ativa' está ativa para login."""
        for status in StatusConta.values:
            with self.subTest(status=status):
                usuario = Usuarios(usu_nome="Teste", usu_status=status)
                self.assertEqual(usuario.is_active, status == StatusConta.ATIVA)

    def test_str_usa_nome(self):
        """str() funciona para usuário sem e-mail e mostra o nome."""
        usuario = Usuarios.objects.create_user(None, "Aluno Sem E-mail")
        self.assertEqual(str(usuario), "Aluno Sem E-mail")

    def test_sem_colunas_extras(self):
        """Usuarios não tem last_login, is_staff, is_superuser, groups nem user_permissions."""
        nomes = {campo.name for campo in Usuarios._meta.get_fields()}
        for tecnico in ("last_login", "is_staff", "is_superuser", "groups", "user_permissions"):
            self.assertNotIn(tecnico, nomes)
