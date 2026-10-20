"""Cria contas de teste pelo shell, só em desenvolvimento (research A15; quickstart).

Não é tela do produto e não substitui a Gestão de Contas (spec 002). Recusa rodar com
DEBUG = False. Nenhum identificador gerado pelo banco é informado (spec 001, FR-003).

Exemplo:
    python manage.py criar_conta_teste --perfil aluno --status ativa --matricula 2026000002
        --email aluno2@uea.edu.br --senha Tcc@2026a --turma ECP_T01

[FR-027][infraestrutura de teste da feature 003]
"""

from datetime import date, time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    DiaSemana,
    StatusConta,
    StatusTurma,
    Titulacao,
)
from sigtcc.apps.cadastro.models import (
    Alunos,
    AlunosTurmas,
    Coordenadores,
    Cursos,
    Disciplinas,
    Docentes,
    MembrosExternos,
    Secretarios,
    Turmas,
    Usuarios,
)
from sigtcc.apps.cadastro.services import normalizar_email

PERFIS = ("aluno", "docente", "coordenador", "secretaria", "membro_externo")
STATUS = {"aguardando": StatusConta.AGUARDANDO_ATIVACAO, "ativa": StatusConta.ATIVA}


class Command(BaseCommand):
    """Comando criar_conta_teste. [FR-027]"""

    help = "Cria uma conta de teste de qualquer perfil (só com DEBUG = True)."

    def add_arguments(self, parser):
        """Opções do contrato §6 (servicos-compartilhados.md)."""
        parser.add_argument("--perfil", required=True, choices=PERFIS)
        parser.add_argument("--status", default="aguardando", choices=tuple(STATUS))
        parser.add_argument("--email", help="obrigatório, exceto para Aluno")
        parser.add_argument("--matricula", help="10 dígitos; obrigatório para Aluno")
        parser.add_argument("--senha", help="obrigatório com --status ativa")
        parser.add_argument("--curso", default="Engenharia de Computação", help="nome do curso")
        parser.add_argument("--turma", help="identificador; reaproveita a turma se existir")
        parser.add_argument("--professor", help="e-mail do Professor da turma criada")
        parser.add_argument("--arquivada", action="store_true", help="cria a turma 'Arquivada'")
        parser.add_argument("--validade", help="AAAA-MM-DD, validade do Membro Externo")

    def handle(self, *args, **opcoes):
        """Confere as opções e cria a conta numa transação."""
        if not settings.DEBUG:
            raise CommandError("criar_conta_teste só roda em desenvolvimento (DEBUG = True).")
        perfil = opcoes["perfil"]
        status = STATUS[opcoes["status"]]
        email = normalizar_email(opcoes["email"])
        senha = opcoes["senha"]
        if perfil != "aluno" and not email:
            raise CommandError("Informe --email para este perfil.")
        if perfil == "aluno" and not (opcoes["matricula"] or "").isdigit():
            raise CommandError("Informe --matricula com 10 dígitos para o Aluno.")
        if status == StatusConta.ATIVA and not senha:
            raise CommandError("Informe --senha para criar a conta 'Ativa'.")
        validade = None
        if opcoes["validade"]:
            try:
                validade = date.fromisoformat(opcoes["validade"])
            except ValueError as erro:
                raise CommandError("Use --validade no formato AAAA-MM-DD.") from erro
        try:
            curso = Cursos.objects.get(cur_nome=opcoes["curso"])
        except Cursos.DoesNotExist as erro:
            raise CommandError(f"Curso não encontrado: {opcoes['curso']}") from erro
        if perfil == "coordenador" and Coordenadores.objects.filter(cor_cur=curso).exists():
            raise CommandError(f"O curso {curso.cur_nome} já tem Coordenador de Curso.")

        with transaction.atomic():
            usuario = Usuarios.objects.create_user(
                email,
                self._nome(perfil, email, opcoes["matricula"]),
                password=senha if status == StatusConta.ATIVA else None,
                usu_status=status,
            )
            docente = self._criar_especializacao(usuario, perfil, curso, opcoes, validade)
            if opcoes["turma"]:
                turma = self._turma(opcoes, curso, docente)
                if perfil == "aluno":
                    AlunosTurmas.objects.get_or_create(
                        mat_alu=usuario.alunos,
                        mat_tur=turma,
                        defaults={"mat_data_inscricao": timezone.now()},
                    )
        self.stdout.write(
            self.style.SUCCESS(
                f"Conta criada: usu_id={usuario.pk}, perfil={perfil}, status={status}"
            )
        )

    def _nome(self, perfil, email, matricula):
        """Nome de teste legível."""
        sufixo = matricula if perfil == "aluno" else email.split("@")[0]
        return f"{perfil.replace('_', ' ').title()} Teste {sufixo}"

    def _criar_especializacao(self, usuario, perfil, curso, opcoes, validade):
        """Cria o registro do tipo de conta; devolve o Docentes quando houver."""
        if perfil == "aluno":
            Alunos.objects.create(
                alu=usuario, alu_matricula=opcoes["matricula"], alu_codigo_curso="TESTE"
            )
            return None
        if perfil in ("docente", "coordenador"):
            docente = Docentes.objects.create(
                doc=usuario, doc_titulacao=Titulacao.DOUTOR, doc_cur=curso
            )
            if perfil == "coordenador":
                Coordenadores.objects.create(cor_cur=curso, cor_doc=docente)
            return docente
        if perfil == "secretaria":
            Secretarios.objects.create(sec=usuario, sec_cur=curso)
            return None
        MembrosExternos.objects.create(
            mem=usuario,
            mem_titulacao=Titulacao.MESTRE,
            mem_instituicao="Instituição de teste",
            mem_validade_ate=validade,
        )
        return None

    def _turma(self, opcoes, curso, docente):
        """Reaproveita a turma pelo identificador ou cria uma turma de TCC 1 de teste."""
        identificador = opcoes["turma"]
        turma = Turmas.objects.filter(tur_identificador=identificador).first()
        if turma is not None:
            return turma
        professor = self._professor(opcoes["professor"], curso, docente)
        disciplina, _ = Disciplinas.objects.get_or_create(
            dis_codigo=f"TESTE_{identificador}"[:20], defaults={"dis_nome": "Disciplina de teste"}
        )
        hoje = timezone.now().date()
        return Turmas.objects.create(
            tur_identificador=identificador,
            tur_descricao=DescricaoTurma.TCC_1,
            tur_doc=professor,
            tur_dis=disciplina,
            tur_cur=curso,
            tur_ano=hoje.year,
            tur_semestre=1 if hoje.month <= 6 else 2,
            tur_dia_da_semana=DiaSemana.SEGUNDA,
            tur_hora_inicio=time(14, 0),
            tur_hora_termino=time(16, 0),
            tur_local="Sala de teste",
            tur_status=StatusTurma.ARQUIVADA if opcoes["arquivada"] else StatusTurma.ATIVA,
        )

    def _professor(self, email_professor, curso, docente):
        """Professor da turma: --professor, o próprio docente ou um docente de teste."""
        if email_professor:
            professor = Docentes.objects.filter(doc__usu_email__iexact=email_professor).first()
            if professor is None:
                raise CommandError(f"Docente não encontrado: {email_professor}")
            return professor
        if docente is not None:
            return docente
        numero = Usuarios.objects.count() + 1
        usuario = Usuarios.objects.create_user(
            f"professor.teste{numero}@uea.edu.br",
            f"Professor Teste {numero}",
            usu_status=StatusConta.AGUARDANDO_ATIVACAO,
        )
        return Docentes.objects.create(doc=usuario, doc_titulacao=Titulacao.DOUTOR, doc_cur=curso)
