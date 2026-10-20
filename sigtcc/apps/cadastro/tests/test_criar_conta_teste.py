"""Testes do comando criar_conta_teste (spec 003, história 6, cenário 6; FR-027).

[FR-027][infraestrutura de teste da feature 003]
"""

import io

from django.core.management import CommandError, call_command
from django.test import override_settings

from sigtcc.apps.cadastro import services
from sigtcc.apps.cadastro.choices import StatusConta, StatusTurma
from sigtcc.apps.cadastro.models import AlunosTurmas, Coordenadores, Turmas, Usuarios
from sigtcc.apps.cadastro.permissoes import papeis, tipo_conta
from sigtcc.apps.cadastro.services import EstadoLogin
from sigtcc.apps.cadastro.tests.apoio_acesso import TesteAcesso

SENHA = "Tcc@2026a"


def criar(*argumentos):
    """Roda o comando sem mostrar a saída."""
    call_command("criar_conta_teste", *argumentos, stdout=io.StringIO())


@override_settings(DEBUG=True)
class CriarContaTesteTest(TesteAcesso):
    """Comando de conta de teste. [FR-027]"""

    def test_cenario6_conta_pelo_shell(self):
        """Dado o shell, quando segue o quickstart, então cria cada perfil e a conta entra."""
        criar(
            "--perfil",
            "docente",
            "--status",
            "ativa",
            "--email",
            "docente@uea.edu.br",
            "--senha",
            SENHA,
            "--turma",
            "ECP_T01",
        )
        criar(
            "--perfil",
            "aluno",
            "--status",
            "aguardando",
            "--matricula",
            "2026000001",
            "--turma",
            "ECP_T01",
        )
        criar(
            "--perfil",
            "aluno",
            "--status",
            "ativa",
            "--matricula",
            "2026000002",
            "--email",
            "aluno2@uea.edu.br",
            "--senha",
            SENHA,
            "--turma",
            "ECP_T01",
        )
        criar(
            "--perfil",
            "coordenador",
            "--status",
            "ativa",
            "--email",
            "coord@uea.edu.br",
            "--senha",
            SENHA,
            "--curso",
            "Sistemas de Informação",
        )
        criar(
            "--perfil",
            "secretaria",
            "--status",
            "aguardando",
            "--email",
            "secretaria@uea.edu.br",
            "--curso",
            "Sistemas de Informação",
        )
        criar(
            "--perfil",
            "membro_externo",
            "--status",
            "ativa",
            "--email",
            "externo@ufam.edu.br",
            "--senha",
            SENHA,
            "--validade",
            "2026-10-01",
        )
        esperado = {
            "docente@uea.edu.br": ("docente", StatusConta.ATIVA),
            "aluno2@uea.edu.br": ("aluno", StatusConta.ATIVA),
            "coord@uea.edu.br": ("docente", StatusConta.ATIVA),
            "secretaria@uea.edu.br": ("secretaria", StatusConta.AGUARDANDO_ATIVACAO),
            "externo@ufam.edu.br": ("membro_externo", StatusConta.ATIVA),
        }
        for email, (tipo, status) in esperado.items():
            with self.subTest(email=email):
                conta = Usuarios.objects.get(usu_email=email)
                self.assertEqual(tipo_conta(conta), tipo)
                self.assertEqual(conta.usu_status, status)
        self.assertEqual(services.autenticar("2026000002", SENHA).estado, EstadoLogin.OK)
        self.assertEqual(services.autenticar("docente@uea.edu.br", SENHA).estado, EstadoLogin.OK)
        self.assertEqual(services.autenticar("2026000001", SENHA).estado, EstadoLogin.AGUARDANDO)
        self.assertIn("coordenador", papeis(Usuarios.objects.get(usu_email="coord@uea.edu.br")))

    def test_turma_reaproveitada_e_professor(self):
        """--turma reaproveita a turma; o docente do comando é o Professor dela."""
        criar(
            "--perfil",
            "docente",
            "--status",
            "ativa",
            "--email",
            "prof@uea.edu.br",
            "--senha",
            SENHA,
            "--turma",
            "ECP_T01",
        )
        criar("--perfil", "aluno", "--matricula", "2026000001", "--turma", "ECP_T01")
        turma = Turmas.objects.get(tur_identificador="ECP_T01")
        self.assertEqual(turma.tur_doc.doc.usu_email, "prof@uea.edu.br")
        self.assertEqual(Turmas.objects.count(), 1)
        self.assertTrue(AlunosTurmas.objects.filter(mat_tur=turma).exists())
        self.assertIsNone(Usuarios.objects.get(alunos__alu_matricula="2026000001").usu_email)

    def test_professor_por_email(self):
        """--professor define o tur_doc da turma criada."""
        criar(
            "--perfil",
            "docente",
            "--status",
            "ativa",
            "--email",
            "prof@uea.edu.br",
            "--senha",
            SENHA,
        )
        criar(
            "--perfil",
            "aluno",
            "--matricula",
            "2026000001",
            "--turma",
            "ECP_T02",
            "--professor",
            "PROF@uea.edu.br",
        )
        turma = Turmas.objects.get(tur_identificador="ECP_T02")
        self.assertEqual(turma.tur_doc.doc.usu_email, "prof@uea.edu.br")

    def test_turma_arquivada(self):
        """--arquivada cria a turma 'Arquivada' (Q27)."""
        criar(
            "--perfil",
            "docente",
            "--status",
            "ativa",
            "--email",
            "arq@uea.edu.br",
            "--senha",
            SENHA,
            "--turma",
            "ECP_T00",
            "--arquivada",
        )
        turma = Turmas.objects.get(tur_identificador="ECP_T00")
        self.assertEqual(turma.tur_status, StatusTurma.ARQUIVADA)
        self.assertIn("professor_disciplina", papeis(Usuarios.objects.get(pk=turma.tur_doc_id)))

    def test_coordenador_repetido_recusado(self):
        """Um curso tem um só Coordenador de Curso: o segundo é recusado com mensagem clara."""
        criar("--perfil", "coordenador", "--email", "c1@uea.edu.br")
        with self.assertRaisesMessage(CommandError, "já tem Coordenador de Curso"):
            criar("--perfil", "coordenador", "--email", "c2@uea.edu.br")
        self.assertEqual(Coordenadores.objects.count(), 1)
        self.assertFalse(Usuarios.objects.filter(usu_email="c2@uea.edu.br").exists())

    def test_opcoes_obrigatorias(self):
        """E-mail (exceto Aluno), matrícula do Aluno e senha da conta 'Ativa' são exigidos."""
        for argumentos in (
            ("--perfil", "docente"),
            ("--perfil", "aluno"),
            ("--perfil", "docente", "--email", "d@uea.edu.br", "--status", "ativa"),
        ):
            with self.subTest(argumentos=argumentos):
                with self.assertRaises(CommandError):
                    criar(*argumentos)

    @override_settings(DEBUG=False)
    def test_recusa_sem_debug(self):
        """Com DEBUG = False, o comando recusa."""
        with self.assertRaisesMessage(CommandError, "DEBUG = True"):
            criar("--perfil", "docente", "--email", "d@uea.edu.br")
        self.assertFalse(Usuarios.objects.exists())
