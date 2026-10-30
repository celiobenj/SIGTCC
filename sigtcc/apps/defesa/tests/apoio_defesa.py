"""Apoio aos testes da feature 007: docentes, TCC "Apto para Defesa" com orientador e sessões.

Monta o cenário com as fábricas das specs 004 e 006 (apoio_turmas, apoio_orientacao), sem passar
pelos serviços dessas specs.

[infraestrutura de teste da feature 007][research C8] (tasks T003)
"""

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
