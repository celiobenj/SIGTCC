"""Fábricas de registros mínimos e válidos para os testes de restrições.

Nenhuma fábrica informa identificador gerado pelo banco (spec FR-003). Cada chamada usa valores
únicos (contador) para não esbarrar nas unicidades.

[infraestrutura da feature 001, sem US específica][apoio aos testes da US2]
"""

import itertools
from datetime import date, datetime, time
from decimal import Decimal

from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    DiaSemana,
    ModalidadeTCC,
    StatusConta,
    StatusTCC,
    StatusTurma,
    TipoEntrega,
    Titulacao,
)
from sigtcc.apps.cadastro.models import (
    Alunos,
    CoorientadoresExternos,
    Cursos,
    Disciplinas,
    Docentes,
    TCCs,
    Turmas,
    TurmasMarcos,
    Usuarios,
)

_contador = itertools.count(1)
AGORA = datetime(2026, 10, 19, 10, 0)


def proximo():
    """Número sequencial para gerar valores únicos."""
    return next(_contador)


def criar_curso(nome=None):
    return Cursos.objects.create(cur_nome=nome or f"Curso {proximo()}")


def criar_usuario(email=None, status=StatusConta.ATIVA, **campos):
    n = proximo()
    return Usuarios.objects.create_user(
        email if email is not None else f"usuario{n}@uea.edu.br",
        f"Usuário {n}",
        usu_status=status,
        **campos,
    )


def criar_docente(curso=None):
    return Docentes.objects.create(
        doc=criar_usuario(),
        doc_titulacao=Titulacao.DOUTOR,
        doc_cur=curso or criar_curso(),
    )


def criar_aluno(matricula=None):
    return Alunos.objects.create(
        alu=criar_usuario(email=None, status=StatusConta.AGUARDANDO_ATIVACAO),
        alu_matricula=matricula or f"{2026000000 + proximo():010d}",
        alu_codigo_curso="EST08MCPD",
    )


def criar_disciplina():
    return Disciplinas.objects.create(dis_codigo=f"DIS{proximo()}")


def criar_turma(**campos):
    docente = campos.pop("tur_doc", None) or criar_docente()
    valores = {
        "tur_identificador": f"TUR_{proximo()}",
        "tur_descricao": DescricaoTurma.TCC_1,
        "tur_doc": docente,
        "tur_dis": criar_disciplina(),
        "tur_cur": docente.doc_cur,
        "tur_ano": 2026,
        "tur_semestre": 2,
        "tur_dia_da_semana": DiaSemana.SEGUNDA,
        "tur_hora_inicio": time(14, 0),
        "tur_hora_termino": time(16, 0),
        "tur_local": "Laboratório LSI",
        "tur_status": StatusTurma.ATIVA,
    }
    valores.update(campos)
    return Turmas.objects.create(**valores)


def criar_tcc(**campos):
    valores = {
        "tcc_alu": campos.pop("tcc_alu", None) or criar_aluno(),
        "tcc_tur": campos.pop("tcc_tur", None) or criar_turma(),
        "tcc_status": StatusTCC.SEM_PROPOSTA,
    }
    valores.update(campos)
    return TCCs.objects.create(**valores)


def criar_tcc_com_proposta(**campos):
    valores = {
        "tcc_status": StatusTCC.EM_ANDAMENTO,
        "tcc_titulo": "Título do trabalho",
        "tcc_resumo": "Resumo do trabalho",
        "tcc_modalidade": ModalidadeTCC.MONOGRAFIA,
    }
    valores.update(campos)
    return criar_tcc(**valores)


def criar_marco(turma=None, tipo=TipoEntrega.OUTRA):
    return TurmasMarcos.objects.create(
        tma_tur=turma or criar_turma(),
        tma_tipo=tipo,
        tma_titulo=f"Entrega {proximo()}",
        tma_data_limite=AGORA,
    )


def criar_coorientador_externo(email=None):
    return CoorientadoresExternos.objects.create(cext_nome=f"Externo {proximo()}", cext_email=email)


# ---------------------------------------------------------------------------------------------
# App defesa
# ---------------------------------------------------------------------------------------------


def criar_defesa(tcc=None, **campos):
    from sigtcc.apps.defesa.choices import FormatoSessao, StatusSessao
    from sigtcc.apps.defesa.models import Defesas

    valores = {
        "def_tcc": tcc or criar_tcc_com_proposta(),
        "def_data": date(2026, 11, 20),
        "def_h_inicio": time(9, 0),
        "def_formato": FormatoSessao.PRESENCIAL,
        "def_status": StatusSessao.AGENDADA,
    }
    valores.update(campos)
    return Defesas.objects.create(**valores)


def criar_criterio(**campos):
    from sigtcc.apps.defesa.choices import ComponenteCriterio
    from sigtcc.apps.defesa.models import Criterios

    valores = {
        "cri_nome": f"Critério {proximo()}",
        "cri_componente": ComponenteCriterio.PARTE_ESCRITA,
        "cri_desc_exemplar": "Descritor exemplar",
        "cri_desc_competente": "Descritor competente",
        "cri_desc_necessita_trabalho": "Descritor necessita de trabalho",
        "cri_peso": Decimal("1.0"),
    }
    valores.update(campos)
    return Criterios.objects.create(**valores)


def criar_membro_banca(defesa=None, usuario=None, **campos):
    from sigtcc.apps.defesa.choices import PapelBanca
    from sigtcc.apps.defesa.models import BancaDefesa

    valores = {
        "ban_def": defesa or criar_defesa(),
        "ban_usu": usuario or criar_usuario(),
        "ban_papel": PapelBanca.PRIMEIRO_AVALIADOR,
    }
    valores.update(campos)
    return BancaDefesa.objects.create(**valores)
