"""Regras de negócio da Gestão de Contas (spec 002): docentes, Coordenador de Curso, Secretaria,
membros externos, inativação, validade, expiração e prorrogação.

Direção das importações (research C3): views_contas → services_contas → services → permissoes →
models; services_contas → sigtcc.apps.defesa.models. Este módulo nunca é importado por
permissoes.py nem por defesa/models.py.

Travas (research C19): sempre dentro de transaction.atomic(), na ordem Usuarios (id crescente) →
especialização (Docentes, Secretarios, MembrosExternos) → Cursos (id crescente) → trava consultiva
do e-mail (services.travar_email). Depois de travar, tudo o que decide a regra é relido.

[US-03][US-04][US-05][US-06][US-50][RBN-CAD-01.1 a 01.4][RBN-CAD-02.1 a 02.3]
[RBN-CAD-03.1 a 03.3][RBN-CAD-14.1]
"""

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from django.urls import Resolver404, resolve
from django.utils.http import url_has_allowed_host_and_scheme

from sigtcc.apps.cadastro.choices import StatusConta
from sigtcc.apps.cadastro.models import Cursos, Docentes, MembrosExternos, Usuarios
from sigtcc.apps.cadastro.permissoes import pode_gerir

# =============================================================================================
# Recusa por curso (research C21)
# =============================================================================================


class ForaDoCurso(Exception):
    """Ação sobre registro de outro curso; a view mostra a mensagem com status 403.

    [US-03][US-04][RBN-CAD-14.1][FR-009][research C21]
    """

    def __init__(self, mensagem):
        """Guarda o texto do FR-009 que a view vai exibir. [FR-009]"""
        super().__init__(mensagem)
        self.mensagem = mensagem


def exigir_curso(usuario, registro, mensagem):
    """Levanta ForaDoCurso se o registro (Docentes ou Secretarios) não for do curso do usuário.

    Chamar depois de travar e reler o registro (o curso atual decide, Q5).
    [US-03][US-04][RBN-CAD-14.1][FR-009][Q5][Q26]
    """
    if not pode_gerir(usuario, registro):
        raise ForaDoCurso(mensagem)


# =============================================================================================
# Travas (research C19; B1)
# =============================================================================================

_ESPECIALIZACOES = ("alunos", "docentes", "membrosexternos", "secretarios")


def travar_contas(*usu_ids):
    """Trava as linhas de Usuarios em ordem crescente de id e as devolve relidas, por id.

    Só a linha de Usuarios é travada (o PostgreSQL não trava o lado opcional de um outer join).
    [research C19][B1]
    """
    ids = sorted({int(i) for i in usu_ids if i is not None})
    contas = (
        Usuarios.objects.select_related(*_ESPECIALIZACOES)
        .select_for_update(of=("self",))
        .filter(pk__in=ids)
        .order_by("pk")
    )
    return {conta.pk: conta for conta in contas}


def travar_conta(usu_id):
    """Trava e devolve a conta relida, ou None se não existir. [research C19][B1]"""
    return travar_contas(usu_id).get(int(usu_id))


def travar_cursos(*cur_ids):
    """Trava as linhas de Cursos em ordem crescente de id (C5, C19). [FR-014][FR-021]"""
    ids = sorted({int(i) for i in cur_ids if i is not None})
    return list(Cursos.objects.select_for_update().filter(pk__in=ids).order_by("pk"))


# =============================================================================================
# Listas de escolha e criação de vínculos (contrato de serviços 002, §1)
# =============================================================================================


def docentes_ativos():
    """Docentes com a conta 'Ativa': base das listas de orientador, coorientador, Professor da
    Disciplina e avaliador (as features donas aplicam os demais filtros).
    [US-04][RBN-CAD-01.3][FR-028]
    """
    return Docentes.objects.filter(doc__usu_status=StatusConta.ATIVA)


def membros_externos_disponiveis():
    """Todos os membros externos ('Aguardando Ativação', 'Ativa' e 'Expirada'): o Membro Externo
    não tem o status 'Inativa' (RBN-CAD-03.3), e a banca renova a validade (US-06 A1).
    [US-05][US-06][RBN-CAD-03.3][FR-028]
    """
    return MembrosExternos.objects.all()


def travar_e_conferir_ativo(usuario):
    """Trava a conta e confere, relida, se ela pode receber um vínculo novo.

    Docente: só 'Ativa'. Membro Externo: sempre (a banca renova a validade). Chamar na mesma
    transação do INSERT do vínculo, no POST (contrato §1; research B1).
    [US-04][RBN-CAD-01.3][FR-026][FR-028][B1]
    """
    conta = travar_conta(usuario.pk)
    if conta is None:
        return False
    if hasattr(conta, "membrosexternos"):
        return True
    return conta.usu_status == StatusConta.ATIVA


# =============================================================================================
# Atalho da banca (FR-034; research C23)
# =============================================================================================


def destino_interno(valor, request):
    """Caminho interno de "voltar" que resolve numa rota do sistema, ou None.

    Aceita só caminho relativo começando com "/" (sem "//"), do próprio host, e que resolve numa
    rota existente. [US-05][RBN-DEF-02.3][FR-034][research C23][m1]
    """
    if not valor or not valor.startswith("/") or valor.startswith("//"):
        return None
    if not url_has_allowed_host_and_scheme(
        valor, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return None
    try:
        resolve(urlsplit(valor).path)
    except Resolver404:
        return None
    return valor


def com_parametro(caminho, nome, valor):
    """Acrescenta (ou troca) um parâmetro na query do caminho, preservando os demais.

    [US-05][FR-034][research C23]
    """
    partes = urlsplit(caminho)
    parametros = [(k, v) for k, v in parse_qsl(partes.query, keep_blank_values=True) if k != nome]
    parametros.append((nome, str(valor)))
    return urlunsplit(partes._replace(query=urlencode(parametros)))
