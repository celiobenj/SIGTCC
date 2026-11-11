"""Relatórios operacionais (spec 011; RAN-REL-03): Defesas realizadas no período, Turmas e alunos,
Aluno e orientador (apoio à matrícula) e Horas complementares de ouvintes, registrados na base do
módulo da spec 010 (contrato §1 a §6). Só leitura: nenhum trecho grava dados, nem o início
automático das sessões vencidas da Defesa (Clarifications C9).

Recorte (C1, C2): Coordenador de Curso e Secretaria (`filtros.gestao`) veem o Curso escolhido ou
Todos; o Professor da Disciplina que não é Coordenador vê só as próprias turmas, na consulta, o que
vale para a tela e para os arquivos.

[US-48][US-49][US-34][US-35][RBN-REL-03.1][RBN-REL-03.2][RBN-REL-03.3][RBN-REL-03.4]
[RBN-CAD-14.1][RBN-DEF-01.5]
"""

from collections import defaultdict

from django.db.models import Case, IntegerField, OuterRef, Subquery, Value, When
from django.db.models.functions import Coalesce

from sigtcc.apps.cadastro.choices import DescricaoTurma, StatusOrientacao, StatusTCC
from sigtcc.apps.cadastro.mensagens import SEM_ORIENTADOR
from sigtcc.apps.cadastro.models import AlunosTurmas, Orientacoes, Turmas
from sigtcc.apps.defesa.choices import PapelBanca, StatusSessao
from sigtcc.apps.defesa.models import BancaDefesa, Defesas
from sigtcc.apps.defesa.services_defesa import PAPEIS_TITULARES
from sigtcc.apps.defesa.services_ouvintes import ouvintes_das_defesas

from . import mensagens
from .estrutura import Coluna, Linha, Relatorio, SubLista
from .registro import relatorio
from .services_relatorios import ultimo_status

PERFIS_OPERACIONAIS = ("coordenador", "secretaria", "professor_disciplina")
# Status destacados no relatório de turmas e alunos. [US-49][RBN-REL-03.2]
STATUS_CRITICOS = (StatusTCC.REPROVADO, StatusTCC.DESISTENTE, StatusTCC.JUBILADO)
HORAS_POR_PRESENCA = 2
AVALIADORES = (PapelBanca.PRIMEIRO_AVALIADOR, PapelBanca.SEGUNDO_AVALIADOR)


def _professor_do_recorte(usuario, filtros):
    """Id do Professor da Disciplina cujas turmas limitam a consulta, ou None na gestão.

    Sem gestão, sempre o próprio usuário, mesmo que a consulta seja chamada sem o formulário.
    [US-48 D][US-49 B][US-34 B][US-35 C][RBN-REL-03.2][C1][C2]
    """
    return None if filtros.gestao else usuario.pk


def _recortar(consulta, campo_turma, usuario, filtros):
    """Aplica o Curso (gestão) ou as turmas do Professor da Disciplina; `campo_turma` é o caminho
    até a turma ("" quando a consulta já é de Turmas). [C1][C2][RBN-CAD-14.1]
    """
    prefixo = f"{campo_turma}__" if campo_turma else ""
    professor = _professor_do_recorte(usuario, filtros)
    if professor is not None:
        return consulta.filter(**{f"{prefixo}tur_doc_id": professor})
    if filtros.cur_id is not None:
        return consulta.filter(**{f"{prefixo}tur_cur_id": filtros.cur_id})
    return consulta


def _status_na_turma():
    """Status do aluno na turma do vínculo: último registro do histórico do TCC que está na turma;
    sem TCC ou sem registro, Sem Proposta (CAD-08.7; research R5 da spec 010).
    [US-49][US-34][RBN-CAD-08.3][RBN-CAD-08.7]
    """
    return Coalesce(
        ultimo_status(hst_tcc__tcc_alu=OuterRef("mat_alu"), hst_tcc__tcc_tur=OuterRef("mat_tur")),
        Value(StatusTCC.SEM_PROPOSTA.value),
    )


# ---------------------------------------------------------------------------------------------
# Defesas realizadas no período (US-48; RBN-REL-03.1)
# ---------------------------------------------------------------------------------------------

_COLUNAS_DEFESAS = (
    Coluna("data_horario", "Data/Horário"),
    Coluna("aluno", "Aluno"),
    Coluna("orientador", "Orientador", definicao=mensagens.DEFINICAO_ORIENTADOR_PRESIDENTE),
    Coluna("banca", "Banca", definicao=mensagens.DEFINICAO_BANCA_EFETIVA),
    Coluna("modalidade", "Modalidade do TCC"),
    Coluna("parecer", "Parecer"),
)


def _bancas_por_sessao(sessoes):
    """Membros efetivos de cada sessão numa consulta: o Suplente acionado já ocupa o papel do
    titular ausente; o não acionado fica de fora (RBN-DEF-02.2). [US-48][C3][C4]
    """
    por_sessao = defaultdict(dict)
    efetivos = BancaDefesa.objects.select_related("ban_usu").filter(
        ban_def__in=sessoes, ban_papel__in=PAPEIS_TITULARES
    )
    for membro in efetivos:
        por_sessao[membro.ban_def_id][membro.ban_papel] = membro.ban_usu.usu_nome
    return por_sessao


def _texto_da_banca(membros):
    """ "Nome (1º Avaliador); Nome (2º Avaliador)". [US-48][C4]"""
    return "; ".join(f"{membros[papel]} ({papel})" for papel in AVALIADORES if papel in membros)


@relatorio(
    id="defesas-realizadas",
    nome="Defesas realizadas no período",
    descricao=mensagens.MR15_DESCRICAO_DEFESAS,
    frase=mensagens.MR15_DESCRICAO_DEFESAS,
    perfis=PERFIS_OPERACIONAIS,
    filtros=("periodo", "ano_semestre", "curso"),
    ordem=70,
)
def defesas_realizadas(usuario, filtros):
    """Só as sessões Realizadas do período, com Data/Horário, Aluno, Orientador, Banca, Modalidade
    do TCC e Parecer, por data, hora e aluno.
    [US-48][RBN-REL-03.1][RBN-DEF-01.2][RBN-DEF-01.5][RBN-DEF-06.3][RBN-CAD-07.1][FR-010]
    """
    sessoes = _recortar(
        Defesas.objects.select_related("def_tcc__tcc_alu__alu").filter(
            filtros.periodo_q(), def_status=StatusSessao.REALIZADA
        ),
        "def_tcc__tcc_tur",
        usuario,
        filtros,
    ).order_by("def_data", "def_h_inicio", "def_tcc__tcc_alu__alu__usu_nome", "pk")
    sessoes = list(sessoes)
    bancas = _bancas_por_sessao([sessao.pk for sessao in sessoes])
    linhas = []
    for sessao in sessoes:
        membros = bancas.get(sessao.pk, {})
        linhas.append(
            Linha(
                {
                    "data_horario": f"{sessao.def_data:%d/%m/%Y} {sessao.def_h_inicio:%H:%M}",
                    "aluno": sessao.def_tcc.tcc_alu.alu.usu_nome,
                    "orientador": membros.get(PapelBanca.ORIENTADOR_PRESIDENTE, ""),
                    "banca": _texto_da_banca(membros),
                    "modalidade": sessao.def_tcc.tcc_modalidade or "",
                    "parecer": sessao.def_parecer or "",
                }
            )
        )
    return Relatorio(
        colunas=_COLUNAS_DEFESAS, linhas=tuple(linhas), como_calculado=mensagens.COMO_DEFESAS
    )


# ---------------------------------------------------------------------------------------------
# Turmas e alunos (US-49; RBN-REL-03.2)
# ---------------------------------------------------------------------------------------------

_COLUNAS_TURMAS = (
    Coluna("turma", "Turma"),
    Coluna("descricao", "TCC 1 ou TCC 2"),
    Coluna("professor", "Professor da Disciplina"),
    Coluna("total", "Total de Alunos", numerica=True, definicao=mensagens.DEFINICAO_TOTAL_ALUNOS),
)
# A US-49 pede o Status "ao lado de cada nome": só as duas colunas. [US-49][RBN-REL-03.2][C7]
_COLUNAS_ALUNOS_DA_TURMA = (
    Coluna("aluno", "Nome do Aluno"),
    Coluna("status", "Status do TCC", definicao=mensagens.DEFINICAO_STATUS_NA_TURMA),
)


@relatorio(
    id="turmas-alunos",
    nome="Turmas e alunos",
    descricao=mensagens.MR16_DESCRICAO_TURMAS,
    frase=mensagens.MR16_DESCRICAO_TURMAS,
    perfis=PERFIS_OPERACIONAIS,
    filtros=("ano_semestre", "curso"),
    ordem=80,
)
def turmas_alunos(usuario, filtros):
    """Uma linha por turma do período, com a sub-lista dos alunos e o Status do TCC na turma;
    Reprovado, Desistente e Jubilado destacados. O Professor da Disciplina vê as suas turmas.
    [US-49][RBN-REL-03.2][RBN-CAD-08.3][RBN-CAD-08.7][FR-020][C7]
    """
    turmas = list(_turmas_do_periodo(usuario, filtros))
    alunos = defaultdict(list)
    vinculos = (
        AlunosTurmas.objects.filter(mat_tur__in=[turma.pk for turma in turmas])
        .select_related("mat_alu__alu")
        .annotate(status=_status_na_turma())
        .order_by("mat_alu__alu__usu_nome", "mat_alu_id")
    )
    for vinculo in vinculos:
        alunos[vinculo.mat_tur_id].append(
            Linha(
                {
                    "aluno": vinculo.mat_alu.alu.usu_nome,
                    "status": vinculo.status,
                },
                destaque=vinculo.status in STATUS_CRITICOS,
            )
        )
    linhas = tuple(
        Linha(
            {
                "turma": turma.tur_identificador,
                "descricao": turma.tur_descricao,
                "professor": turma.tur_doc.doc.usu_nome,
                "total": len(alunos[turma.pk]),
            },
            sublistas=(
                SubLista(
                    titulo=mensagens.TITULO_ALUNOS,
                    colunas=_COLUNAS_ALUNOS_DA_TURMA,
                    linhas=tuple(alunos[turma.pk]),
                ),
            ),
        )
        for turma in turmas
    )
    return Relatorio(
        colunas=_COLUNAS_TURMAS,
        linhas=linhas,
        como_calculado=mensagens.COMO_TURMAS,
        rotulo_linha="turma",
    )


def _turmas_do_periodo(usuario, filtros):
    """Turmas do período letivo, no recorte do usuário, pela identificação. [US-49][C1][C7]"""
    turmas = Turmas.objects.select_related("tur_doc__doc").filter(
        tur_ano=filtros.ano, tur_semestre=filtros.semestre
    )
    return _recortar(turmas, "", usuario, filtros).order_by("tur_identificador")


# ---------------------------------------------------------------------------------------------
# Aluno e orientador, apoio à matrícula (US-34; RBN-REL-03.3)
# ---------------------------------------------------------------------------------------------

_COLUNAS_ALUNO_ORIENTADOR = (
    Coluna("matricula", "Matrícula"),
    Coluna("aluno", "Nome do Aluno"),
    Coluna("orientador", "Orientador", definicao=mensagens.DEFINICAO_ORIENTADOR_TCC_1),
    Coluna("status", "Status do TCC", definicao=mensagens.DEFINICAO_STATUS_NA_TURMA),
)


def _orientador_na_turma():
    """Orientador do TCC do aluno na turma: o vínculo ativo; sem ele, o mais recente.
    [US-34][RBN-REL-03.3][RBN-CAD-10.4][C6]
    """
    return Subquery(
        Orientacoes.objects.filter(
            ori_tcc__tcc_alu=OuterRef("mat_alu"), ori_tcc__tcc_tur=OuterRef("mat_tur")
        )
        .annotate(
            prioridade=Case(
                When(ori_status=StatusOrientacao.ATIVA, then=0),
                default=1,
                output_field=IntegerField(),
            )
        )
        .order_by("prioridade", "-ori_data_inicio", "-ori_id")
        .values("ori_doc__doc__usu_nome")[:1]
    )


@relatorio(
    id="aluno-orientador",
    nome="Aluno e orientador (apoio à matrícula)",
    descricao=mensagens.MR17_DESCRICAO_ALUNO_ORIENTADOR,
    frase=mensagens.MR17_DESCRICAO_ALUNO_ORIENTADOR,
    perfis=PERFIS_OPERACIONAIS,
    filtros=("ano_semestre", "curso"),
    ordem=90,
)
def aluno_orientador(usuario, filtros):
    """Alunos das turmas de TCC 1 do período com Matrícula, Nome, Orientador e Status do TCC; os
    Aprovados para TCC 2 primeiro e destacados, e depois os demais, pelo nome.
    [US-34][RBN-REL-03.3][RBN-CAD-08.3][RBN-CAD-08.7][REQ-WNT-04][FR-030][C6]
    """
    vinculos = _recortar(
        AlunosTurmas.objects.select_related("mat_alu__alu").filter(
            mat_tur__tur_ano=filtros.ano,
            mat_tur__tur_semestre=filtros.semestre,
            mat_tur__tur_descricao=DescricaoTurma.TCC_1,
        ),
        "mat_tur",
        usuario,
        filtros,
    )
    vinculos = (
        vinculos.annotate(status=_status_na_turma(), orientador=_orientador_na_turma())
        .annotate(
            primeiro=Case(
                When(status=StatusTCC.APROVADO_PARA_TCC_2, then=0),
                default=1,
                output_field=IntegerField(),
            )
        )
        .order_by("primeiro", "mat_alu__alu__usu_nome", "mat_alu_id")
    )
    linhas = tuple(
        Linha(
            {
                "matricula": vinculo.mat_alu.alu_matricula,
                "aluno": vinculo.mat_alu.alu.usu_nome,
                "orientador": vinculo.orientador or SEM_ORIENTADOR,
                "status": vinculo.status,
            },
            destaque=vinculo.status == StatusTCC.APROVADO_PARA_TCC_2,
        )
        for vinculo in vinculos
    )
    return Relatorio(
        colunas=_COLUNAS_ALUNO_ORIENTADOR,
        linhas=linhas,
        como_calculado=mensagens.COMO_ALUNO_ORIENTADOR,
    )


# ---------------------------------------------------------------------------------------------
# Horas complementares de ouvintes (US-35; RBN-REL-03.4)
# ---------------------------------------------------------------------------------------------

_COLUNAS_HORAS = (
    Coluna("ouvinte", "Nome do Ouvinte"),
    Coluna("matricula", "Matrícula"),
    Coluna("data", "Data da Defesa"),
    Coluna("horas", "Horas", numerica=True, definicao=mensagens.DEFINICAO_HORAS),
)


@relatorio(
    id="horas-ouvintes",
    nome="Horas complementares de ouvintes",
    descricao=mensagens.MR18_DESCRICAO_HORAS,
    frase=mensagens.MR18_DESCRICAO_HORAS,
    perfis=PERFIS_OPERACIONAIS,
    filtros=("periodo", "ano_semestre", "curso"),
    ordem=100,
)
def horas_ouvintes(usuario, filtros):
    """Uma linha por presença de ouvinte em sessão Realizada do período, com 2 horas cada, e o
    total de horas ao final; reaproveita a consulta da tela "Ouvintes das defesas" (spec 009).
    [US-35][RBN-REL-03.4][RBN-DEF-08.2][RBN-DEF-08.4][RBN-DEF-01.5][FR-040][C8]
    """
    cur_id = filtros.cur_id if filtros.gestao else None
    presencas = ouvintes_das_defesas(filtros.periodo_q(), cur_id)
    professor = _professor_do_recorte(usuario, filtros)
    if professor is not None:
        presencas = presencas.filter(pre_def__def_tcc__tcc_tur__tur_doc_id=professor)
    presencas = presencas.order_by("pre_def__def_data", "pre_ouv__ouv_nome", "pre_ouv_id")
    linhas = tuple(
        Linha(
            {
                "ouvinte": presenca.pre_ouv.ouv_nome,
                "matricula": presenca.pre_ouv.ouv_matricula,
                "data": f"{presenca.pre_def.def_data:%d/%m/%Y}",
                "horas": HORAS_POR_PRESENCA,
            }
        )
        for presenca in presencas
    )
    total = Linha(
        {
            "ouvinte": mensagens.ROTULO_TOTAL,
            "matricula": "",
            "data": "",
            "horas": HORAS_POR_PRESENCA * len(linhas),
        }
    )
    return Relatorio(
        colunas=_COLUNAS_HORAS,
        linhas=linhas,
        totais=(total,) if linhas else (),
        como_calculado=mensagens.COMO_HORAS,
    )
