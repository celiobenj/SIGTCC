"""Verificação de perfil reutilizável por todas as features (research A7; contrato §2).

Perfis são tipos de conta ("aluno", "docente", "secretaria", "membro_externo") ou papéis do
Docente ("coordenador", "professor_disciplina", "orientador", "coorientador"), derivados dos dados.

Regras compartilhadas (spec Q27; RBN-CAD-04.5, "turma arquivada não recebe movimentação e fica para
consulta"):
- o papel "professor_disciplina" vale para quem tem pelo menos uma turma, ativa ou arquivada, e dá
  acesso de leitura às telas do papel;
- ações que alteram dados exigem turma não arquivada: use professor_com_turma_ativa no services.py
  da feature, antes de gravar;
- os papéis são globais; cada feature confere o vínculo com o objeto (TCC, defesa, turma).

[FR-025][Q27][RBN-CAD-04.5][RNF de Confidencialidade do RAN-CAD-01 e do RAN-CAD-02]
"""

from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Exists, OuterRef
from django.utils import timezone

from sigtcc.apps.cadastro.choices import (
    StatusConta,
    StatusCoorientacao,
    StatusOrientacao,
    StatusTurma,
)
from sigtcc.apps.cadastro.models import (
    Coordenadores,
    Coorientacoes,
    Cursos,
    Docentes,
    Orientacoes,
    Secretarios,
    Turmas,
)

TIPOS_CONTA = ("aluno", "docente", "secretaria", "membro_externo")
PAPEIS = ("coordenador", "professor_disciplina", "orientador", "coorientador")

# Relação reversa de Usuarios para cada tipo de conta.
_RELACOES = (
    ("alunos", "aluno"),
    ("docentes", "docente"),
    ("secretarios", "secretaria"),
    ("membrosexternos", "membro_externo"),
)


def _autenticado(usuario):
    """Usuário logado (AnonymousUser e None não são).

    [FR-025]
    """
    return usuario is not None and getattr(usuario, "is_authenticated", False)


def especializacao(usuario, relacao):
    """Registro da especialização (Alunos, Docentes...) ou None. [FR-025]"""
    try:
        return getattr(usuario, relacao)
    except ObjectDoesNotExist:
        return None


def tipo_conta(usuario):
    """Tipo da conta: "aluno", "docente", "secretaria", "membro_externo" ou None.

    None = visitante ou conta sem especialização, que não acessa página com perfil declarado.
    [FR-025][FR-010]
    """
    if not _autenticado(usuario):
        return None
    for relacao, tipo in _RELACOES:
        if especializacao(usuario, relacao) is not None:
            return tipo
    return None


def validade_vencida(usuario):
    """Membro Externo com a data de hoje depois de mem_validade_ate (validade nula não vence).

    [US-11][RBN-CAD-03.3][Q4]
    """
    membro = especializacao(usuario, "membrosexternos")
    if membro is None or membro.mem_validade_ate is None:
        return False
    return membro.mem_validade_ate < timezone.now().date()


def papeis(usuario):
    """Papéis do Docente, calculados numa consulta e guardados no objeto do usuário.

    "professor_disciplina" vale com qualquer turma, ativa ou arquivada (spec Q27).
    [FR-025][FR-010][Q7][Q27]
    """
    if hasattr(usuario, "_papeis_cache"):
        return usuario._papeis_cache
    resultado = frozenset()
    if tipo_conta(usuario) == "docente":
        docente = OuterRef("pk")
        linha = (
            Docentes.objects.filter(pk=usuario.pk)
            .annotate(
                coordenador=Exists(Coordenadores.objects.filter(cor_doc=docente)),
                professor_disciplina=Exists(Turmas.objects.filter(tur_doc=docente)),
                orientador=Exists(
                    Orientacoes.objects.filter(ori_doc=docente, ori_status=StatusOrientacao.ATIVA)
                ),
                coorientador=Exists(
                    Coorientacoes.objects.filter(
                        coo_doc=docente, coo_status=StatusCoorientacao.ATIVA
                    )
                ),
            )
            .values(*PAPEIS)
            .first()
        )
        if linha:
            resultado = frozenset(papel for papel in PAPEIS if linha[papel])
    usuario._papeis_cache = resultado
    return resultado


def tem_perfil(usuario, *perfis):
    """Verdadeiro se o tipo de conta ou algum papel do usuário estiver em perfis.

    Sem perfis, basta estar logado. [FR-025]
    """
    if not _autenticado(usuario):
        return False
    if not perfis:
        return True
    if tipo_conta(usuario) in perfis:
        return True
    return bool(papeis(usuario) & set(perfis))


def professor_com_turma_ativa(professor, aluno=None):
    """Regra compartilhada para ações que alteram dados (spec Q27; RBN-CAD-04.5).

    professor: Usuarios logado (com Docentes). aluno: instância de Alunos ou None.
    Verdadeiro se o professor é tur_doc de uma turma 'Ativa' e, com aluno, se o aluno está
    matriculado nela.
    [FR-015][FR-025][Q27][RBN-CAD-04.5][US-12][RBN-CAD-06.8]
    """
    if tipo_conta(professor) != "docente":
        return False
    turmas = Turmas.objects.filter(tur_doc_id=professor.pk, tur_status=StatusTurma.ATIVA)
    if aluno is not None:
        turmas = turmas.filter(alunosturmas__mat_alu=aluno)
    return turmas.exists()


def pode_resetar_primeiro_acesso(professor, aluno):
    """Decide se o botão "Resetar primeiro acesso" aparece e se a ação é aceita.

    Professor da Disciplina de turma não arquivada do aluno (spec Q9, Q27), e só com a conta do
    aluno 'Ativa' ou 'Aguardando Ativação' (spec Q29: reativar conta é da US-04).
    [US-12][RBN-CAD-06.8][FR-015][Q9][Q27][Q29]
    """
    if aluno.alu.usu_status not in (StatusConta.ATIVA, StatusConta.AGUARDANDO_ATIVACAO):
        return False
    return professor_com_turma_ativa(professor, aluno)


def perfil_requerido(*perfis):
    """Decorador de view: sem perfis exige só login; sem login vai ao login com next;
    sem permissão levanta PermissionDenied (handler403 mostra a M-02). [FR-025][SC-004]
    """

    def decorador(view):
        """Envolve a view com a conferência de login e perfil. [FR-025]"""

        @wraps(view)
        def envolta(request, *args, **kwargs):
            """Confere login e perfil e chama a view. [FR-025][SC-004]"""
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if not tem_perfil(request.user, *perfis):
                raise PermissionDenied
            return view(request, *args, **kwargs)

        return envolta

    return decorador


class PerfilRequeridoMixin:
    """O mesmo que perfil_requerido para views de classe (perfis_permitidos = (...)). [FR-025]"""

    perfis_permitidos = ()

    def dispatch(self, request, *args, **kwargs):
        """Confere login e perfil antes de qualquer método da view.

        [FR-025]
        """
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not tem_perfil(request.user, *self.perfis_permitidos):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


# =============================================================================================
# Permissões por turma (spec 004, research B2; spec Q9; regra Q27 da spec 003)
# =============================================================================================


def _e_professor_da_turma(usuario, turma):
    """O usuário é o Professor da Disciplina desta turma (tur_doc). [US-07][RBN-CAD-04.2]"""
    return tipo_conta(usuario) == "docente" and turma.tur_doc_id == usuario.pk


def _e_secretaria_do_curso(usuario, turma):
    """O usuário é a Secretaria do curso desta turma. [US-08][RBN-CAD-05.6][Q9]"""
    secretaria = especializacao(usuario, "secretarios")
    return secretaria is not None and secretaria.sec_cur_id == turma.tur_cur_id


def pode_consultar_turma(usuario, turma):
    """Abre a turma e a lista de alunos: o Professor da Disciplina da turma ou a Secretaria do
    curso da turma (spec 004, Q9; matriz RAN-CAD-04 e RAN-CAD-05). Coordenador de Curso e outros
    Docentes não abrem.
    [US-07][US-08][RBN-CAD-04.5][FR-009][FR-010][Q9]
    """
    return _e_professor_da_turma(usuario, turma) or _e_secretaria_do_curso(usuario, turma)


def pode_alterar_turma(usuario, turma):
    """Altera a turma e os seus alunos: só o Professor da Disciplina desta turma. A turma não
    arquivada é conferida à parte (services_turmas.turma_para), como manda a regra Q27.
    [US-07][US-08][US-09][RBN-CAD-04.3][RBN-CAD-04.5][FR-009][Q27]
    """
    return _e_professor_da_turma(usuario, turma)


def pode_transferir(usuario, turma):
    """Transfere aluno da turma: o Professor da Disciplina da turma de origem ou a Secretaria do
    curso (RBN-CAD-05.6).
    [US-08][RBN-CAD-05.6][FR-020][Q9]
    """
    return _e_professor_da_turma(usuario, turma) or _e_secretaria_do_curso(usuario, turma)


# =============================================================================================
# Curso do usuário e do registro (spec 002, research C2; RBN-CAD-14.1; spec Q5 e Q26)
# Só lê models do cadastro: nunca importar o app defesa aqui (research C3).
# =============================================================================================


def curso_id_do_usuario(usuario):
    """Id do curso que define o alcance das ações do usuário, ou None.

    Coordenador: o Curso Coordenado (Coordenadores.cor_cur), mesmo que lotado em outro curso.
    Secretaria: o Curso Vinculado (Secretarios.sec_cur). Demais perfis: None.
    [US-03][US-04][RBN-CAD-14.1][FR-009][Q5][Q26]
    """
    if not _autenticado(usuario):
        return None
    secretaria = especializacao(usuario, "secretarios")
    if secretaria is not None:
        return secretaria.sec_cur_id
    if tipo_conta(usuario) == "docente":
        return (
            Coordenadores.objects.filter(cor_doc_id=usuario.pk)
            .values_list("cor_cur_id", flat=True)
            .first()
        )
    return None


def curso_do_usuario(usuario):
    """Curso (Cursos) do usuário para o alcance das ações e o filtro padrão, ou None.

    [US-03][US-04][RBN-CAD-14.1][FR-009][FR-018][Q5]
    """
    cur_id = curso_id_do_usuario(usuario)
    return Cursos.objects.filter(pk=cur_id).first() if cur_id is not None else None


def curso_id_do_registro(registro):
    """Id do curso a que o registro pertence: Curso de Lotação do Docente (Q26) ou Curso
    Vinculado da Secretaria. registro: instância de Docentes ou Secretarios.
    [US-03][US-04][RBN-CAD-14.1][FR-009][Q26]
    """
    if isinstance(registro, Docentes):
        return registro.doc_cur_id
    if isinstance(registro, Secretarios):
        return registro.sec_cur_id
    raise TypeError("registro deve ser Docentes ou Secretarios")


def pode_gerir(usuario, registro):
    """O registro (Docentes ou Secretarios) é do curso do usuário, pelo valor atual do registro.

    [US-03][US-04][RBN-CAD-14.1][FR-009][Q5][Q26]
    """
    cur_id = curso_id_do_usuario(usuario)
    return cur_id is not None and cur_id == curso_id_do_registro(registro)
