"""Apoio aos testes da feature 007: docentes, TCC "Apto para Defesa" com orientador e sessões.

Monta o cenário com as fábricas das specs 004 e 006 (apoio_turmas, apoio_orientacao), sem passar
pelos serviços dessas specs.

[infraestrutura de teste da feature 007][research C8] (tasks T003)
"""

from datetime import date, time

from sigtcc.apps.cadastro.choices import DescricaoTurma, StatusTCC
from sigtcc.apps.cadastro.tests.apoio_orientacao import vincular_orientador
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    criar_turma_de,
    curso,
    matricular_aluno,
    tcc_de,
)
from sigtcc.apps.cadastro.tests.fabricas import criar_docente
from sigtcc.apps.defesa import services_defesa
from sigtcc.apps.defesa.choices import FormatoSessao, StatusSessao

# Caminho de transições, a partir de "Agendada", até cada status (research C2).
CAMINHO = {
    StatusSessao.AGENDADA: [],
    StatusSessao.REAGENDADA: [StatusSessao.REAGENDADA],
    StatusSessao.EM_ANDAMENTO: [StatusSessao.EM_ANDAMENTO],
    StatusSessao.CANCELADA: [StatusSessao.CANCELADA],
    StatusSessao.REALIZADA: [StatusSessao.EM_ANDAMENTO, StatusSessao.REALIZADA],
}


def docente(curso_nome=EC):
    """Usuarios de um docente ativo, lotado no curso. [US-03][RBN-CAD-01.1]"""
    return criar_docente(curso(curso_nome)).doc


def tcc_apto(curso_nome=EC, descricao=DescricaoTurma.TCC_1, professor=None, orientador=None):
    """TCC "Apto para Defesa" numa turma do curso, com orientador ativo.

    Devolve (tcc, professor, orientador), os dois últimos como Usuarios.
    [US-21][RBN-DEF-01.1][RBN-CAD-11.5]
    """
    professor = professor or docente(curso_nome)
    orientador = orientador or docente(curso_nome)
    turma = criar_turma_de(professor, descricao=descricao, curso_nome=curso_nome)
    aluno = matricular_aluno(turma, status_tcc=StatusTCC.APTO_PARA_DEFESA)
    tcc = tcc_de(aluno, turma)
    vincular_orientador(tcc, orientador)
    return tcc, professor, orientador


def agendar_sessao_de(tcc, autor=None, banca=None, **dados):
    """Sessão "Agendada" pelo serviço agendar_sessao, presencial no Laboratório LSI por padrão;
    sem `banca`, cria dois docentes avaliadores, sem suplente. [US-21][US-23][RBN-DEF-01.1]
    """
    basicos = {
        "data": date(2026, 11, 20),
        "h_inicio": time(14, 0),
        "formato": FormatoSessao.PRESENCIAL,
        "local": "Laboratório LSI",
    }
    basicos.update(dados)
    banca = banca or {"primeiro_avaliador": docente(), "segundo_avaliador": docente()}
    return services_defesa.agendar_sessao(tcc, basicos, banca, autor)


def avancar_para(sessao, status, autor=None):
    """Leva uma sessão "Agendada" até o status pedido pelo serviço único de transição, sem as
    validações de tela. [US-24][RBN-DEF-01.2]
    """
    for proximo_status in CAMINHO[status]:
        services_defesa.transicionar_status(sessao, proximo_status, autor, "Cenário de teste")
    return sessao
