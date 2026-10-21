"""Regras de turmas e alunos do app cadastro (spec 004; research B1).

Parte comum: permissão por turma, turma arquivada, vínculo do aluno, orientador automático,
participação encerrada e registros das entregas do aluno. Este módulo importa `services`, nunca o
contrário (research B6, N2).

[US-07][US-08][US-09][RBN-CAD-04.1 a 04.5][RBN-CAD-05.1 a 05.8][RBN-CAD-08.4][RBN-CAD-08.5]
"""

from django.core.exceptions import PermissionDenied
from django.http import Http404

from sigtcc.apps.cadastro.cargas import CURSOS_COM_ORIENTADOR_AUTOMATICO
from sigtcc.apps.cadastro.choices import DescricaoTurma, StatusEntrega, StatusTCC, StatusTurma
from sigtcc.apps.cadastro.models import (
    Alunos,
    AlunosTurmas,
    EntregasMarcos,
    HistoricoAlunosTurmas,
    HistoricoStatusTCC,
    TCCs,
    Turmas,
)
from sigtcc.apps.cadastro.permissoes import (
    pode_alterar_turma,
    pode_consultar_turma,
    pode_transferir,
)
from sigtcc.apps.cadastro.services import curso_do_codigo  # noqa: F401 (reexportada, contrato §3)

# Ações sobre a turma (research B2). [FR-009]
CONSULTAR = "consultar"
ALTERAR = "alterar"
TRANSFERIR = "transferir"

# TCC em curso numa turma (spec Q7). Não confundir com o "TCC ativo" da RBN-CAD-01.3 (spec 002).
# [US-08][RBN-CAD-05.5][Q7][m17]
STATUS_TCC_EM_CURSO = (StatusTCC.SEM_PROPOSTA, StatusTCC.EM_ANDAMENTO, StatusTCC.APTO_PARA_DEFESA)

# Participação encerrada (RBN-CAD-08.5). [US-09][RBN-CAD-08.4][RBN-CAD-08.5]
STATUS_PARTICIPACAO_ENCERRADA = (StatusTCC.DESISTENTE, StatusTCC.REPROVADO, StatusTCC.JUBILADO)


class TurmaArquivada(Exception):
    """A turma está arquivada: só consulta (RBN-CAD-04.5); a view mostra a MT-25.

    [US-07][RBN-CAD-04.5][FR-008]
    """

    def __init__(self, turma):
        super().__init__(turma.tur_identificador)
        self.turma = turma


# =============================================================================================
# Turma arquivada e permissão por turma (contrato §1 e §3; research B2 e B5)
# =============================================================================================


def turma_arquivada(turma):
    """Consulta, sem trava; serve para decidir se um botão aparece. [US-07][RBN-CAD-04.5]"""
    return turma.tur_status == StatusTurma.ARQUIVADA


def exigir_turma_ativa(turma):
    """Levanta TurmaArquivada se a turma estiver arquivada. Só para telas: não garante a
    gravação (use travar_turma_ativa). [US-07][RBN-CAD-04.5][FR-008]
    """
    if turma_arquivada(turma):
        raise TurmaArquivada(turma)


def travar_turma_ativa(tur_id):
    """Trava a turma (select_for_update), relê e levanta TurmaArquivada se arquivada.

    Obrigatória antes de gravar em tabela ligada à turma; chamar dentro de transaction.atomic()
    (contrato §1; research B5 e B17). [US-07][RBN-CAD-04.5][FR-008][I-6]
    """
    turma = Turmas.objects.select_for_update().filter(pk=tur_id).first()
    if turma is None:
        raise Http404
    exigir_turma_ativa(turma)
    return turma


def turma_para(usuario, tur_id, acao, travar=False):
    """Turma pela permissão da ação, na ordem: existe (404) → permissão (PermissionDenied) →
    arquivada (TurmaArquivada, só para ALTERAR e TRANSFERIR). Com travar=True, chamar dentro de
    transaction.atomic(); tudo é conferido depois de travar.
    [US-07][US-08][US-09][RBN-CAD-04.5][FR-008][FR-009][Q9][B2]
    """
    turmas = Turmas.objects.select_related("tur_cur", "tur_doc__doc")
    if travar:
        turmas = turmas.select_for_update(of=("self",))
    turma = turmas.filter(pk=tur_id).first()
    if turma is None:
        raise Http404
    regra = {
        CONSULTAR: pode_consultar_turma,
        ALTERAR: pode_alterar_turma,
        TRANSFERIR: pode_transferir,
    }[acao]
    if not regra(usuario, turma):
        raise PermissionDenied
    if acao != CONSULTAR:
        exigir_turma_ativa(turma)
    return turma


def vinculo_na_turma(turma, alu_id):
    """Aluno matriculado nesta turma, senão 404 (sem IDOR pelo alu_id).

    [US-08][US-09][FR-019][FR-020][FR-023][FR-024][I-7]
    """
    if not AlunosTurmas.objects.filter(mat_tur=turma, mat_alu_id=alu_id).exists():
        raise Http404
    return Alunos.objects.select_related("alu").get(pk=alu_id)


def turma_ja_teve_aluno(turma):
    """Tem ou já teve aluno: vínculo, TCC, histórico de status ou de exclusão/transferência.

    Critério da exclusão de turma (spec Q12) e da trava de Descrição e Curso (Q15).
    [US-07][RBN-CAD-04.3][RBN-CAD-04.4][FR-005][FR-006][Q12][Q15]
    """
    return (
        AlunosTurmas.objects.filter(mat_tur=turma).exists()
        or TCCs.objects.filter(tcc_tur=turma).exists()
        or HistoricoStatusTCC.objects.filter(hst_tur=turma).exists()
        or HistoricoAlunosTurmas.objects.filter(hat_tur_origem=turma).exists()
        or HistoricoAlunosTurmas.objects.filter(hat_tur_destino=turma).exists()
    )


def turma_tem_orientador_automatico(turma):
    """TCC 2 de Engenharia de Computação ou de Licenciatura em Computação (RBN-CAD-04.2).

    [US-07][RBN-CAD-04.2][FR-004][B8]
    """
    return (
        turma.tur_descricao == DescricaoTurma.TCC_2
        and turma.tur_cur.cur_nome in CURSOS_COM_ORIENTADOR_AUTOMATICO
    )


def participacao_encerrada(tcc):
    """TCC 'Desistente', 'Reprovado' ou 'Jubilado' (contrato §2). [US-09][RBN-CAD-08.5][FR-025]"""
    return tcc.tcc_status in STATUS_PARTICIPACAO_ENCERRADA


# =============================================================================================
# Registros das entregas do aluno (spec Q17 e Q18; research B22)
# =============================================================================================


def criar_entregas_do_aluno(aluno, turma):
    """Cria o registro do aluno em cada entrega da turma ('Aguardando Envio').

    Registro de um vínculo anterior volta a 'Aguardando Envio', sem avaliação, e os envios
    anteriores ficam no histórico (Q18).
    [US-08][RBN-CAD-05.1][RBN-CAD-05.6][FR-012][FR-022][Q17][Q18]
    """
    for entrega in turma.turmasmarcos_set.all():
        registro, criado = EntregasMarcos.objects.get_or_create(
            ent_tma=entrega,
            ent_alu=aluno,
            defaults={"ent_status": StatusEntrega.AGUARDANDO_ENVIO},
        )
        if not criado:
            registro.ent_status = StatusEntrega.AGUARDANDO_ENVIO
            registro.ent_feedback = None
            registro.ent_data_avaliacao = None
            registro.ent_correcoes_conferidas_em = None
            registro.save(
                update_fields=[
                    "ent_status",
                    "ent_feedback",
                    "ent_data_avaliacao",
                    "ent_correcoes_conferidas_em",
                ]
            )


def remover_entregas_sem_envio(aluno, turma):
    """Apaga os registros do aluno nas entregas da turma sem nenhum envio; os com envio ficam
    como histórico (Q17). [US-09][RBN-CAD-05.4][RBN-CAD-05.6][FR-022][FR-023][Q17]
    """
    EntregasMarcos.objects.filter(
        ent_alu=aluno, ent_tma__tma_tur=turma, historicoenviosentregas__isnull=True
    ).delete()
