"""Regras de turmas e alunos do app cadastro (spec 004; research B1).

Parte comum: permissão por turma, turma arquivada, vínculo do aluno, orientador automático,
participação encerrada e registros das entregas do aluno. Este módulo importa `services`, nunca o
contrário (research B6, N2).

[US-07][US-08][US-09][RBN-CAD-04.1 a 04.5][RBN-CAD-05.1 a 05.8][RBN-CAD-08.4][RBN-CAD-08.5]
"""

import enum
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from django.core.cache import caches
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.http import Http404
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import constant_time_compare

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.cargas import CURSOS_COM_ORIENTADOR_AUTOMATICO
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    GatilhoStatusTCC,
    OrigemOrientacao,
    StatusConta,
    StatusCoorientacao,
    StatusEntrega,
    StatusOrientacao,
    StatusSolicitacao,
    StatusTCC,
    StatusTurma,
    TipoEntrega,
    TipoEventoTurma,
    TipoSolicitacao,
)
from sigtcc.apps.cadastro.models import (
    Alunos,
    AlunosTurmas,
    Artigos,
    Coorientacoes,
    Disciplinas,
    EncontroOrientacao,
    EntregasMarcos,
    EquivalenciaCursos,
    HistoricoAlunosTurmas,
    HistoricoStatusTCC,
    Orientacoes,
    PalavrasChaveTCC,
    SolicitacoesOrientacao,
    TCCs,
    Turmas,
    TurmasMarcos,
    Usuarios,
)
from sigtcc.apps.cadastro.permissoes import (
    pode_alterar_turma,
    pode_consultar_turma,
    pode_transferir,
    tipo_conta,
)
from sigtcc.apps.cadastro.services import (
    EventoAcesso,
    curso_do_codigo,
    montar_mensagem_cortada,
    notificar,
    registrar_evento,
)
from sigtcc.apps.defesa.choices import StatusSessao
from sigtcc.apps.defesa.models import Defesas

# Ações sobre a turma (research B2). [FR-009]
CONSULTAR = "consultar"
ALTERAR = "alterar"
TRANSFERIR = "transferir"

# TCC em curso numa turma (spec Q7). Não confundir com o "TCC ativo" da RBN-CAD-01.3 (spec 002).
# [US-08][RBN-CAD-05.5][Q7][m17]
STATUS_TCC_EM_CURSO = (StatusTCC.SEM_PROPOSTA, StatusTCC.EM_ANDAMENTO, StatusTCC.APTO_PARA_DEFESA)

# Participação encerrada (RBN-CAD-08.5). [US-09][RBN-CAD-08.4][RBN-CAD-08.5]
STATUS_PARTICIPACAO_ENCERRADA = (StatusTCC.DESISTENTE, StatusTCC.REPROVADO, StatusTCC.JUBILADO)

# Sessão de defesa ativa (RBN-DEF-01.2). [US-07][US-08][US-09][RBN-CAD-04.5][RBN-CAD-05.6]
STATUS_SESSAO_ATIVA = (StatusSessao.AGENDADA, StatusSessao.REAGENDADA, StatusSessao.EM_ANDAMENTO)


class TurmaArquivada(Exception):
    """A turma está arquivada: só consulta (RBN-CAD-04.5); a view mostra a MT-25.

    [US-07][RBN-CAD-04.5][FR-008]
    """

    def __init__(self, turma):
        """Guarda a turma arquivada. [FR-008]"""
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


# =============================================================================================
# Turmas: cadastro, edição, exclusão e arquivamento (US-07; research B3 a B5)
# =============================================================================================


class ErroTurma(Exception):
    """Recusa de uma ação com a mensagem exata e, se houver, o campo a destacar.

    [US-07][US-08][US-09][FR-002][FR-006][FR-007]
    """

    def __init__(self, mensagem, campo=None):
        """Guarda a mensagem exata e o campo. [FR-002]"""
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.campo = campo


def turmas_visiveis(usuario, arquivadas=False):
    """Turmas que o usuário abre: as que o Docente é Professor da Disciplina ou as do curso da
    Secretaria (spec Q9), ativas ou arquivadas.
    [US-07][RBN-CAD-04.5][FR-008][FR-010][Q9]
    """
    status = StatusTurma.ARQUIVADA if arquivadas else StatusTurma.ATIVA
    turmas = Turmas.objects.select_related("tur_cur", "tur_dis", "tur_doc__doc").filter(
        tur_status=status
    )
    tipo = tipo_conta(usuario)
    if tipo == "docente":
        turmas = turmas.filter(tur_doc_id=usuario.pk)
    elif tipo == "secretaria":
        turmas = turmas.filter(tur_cur_id=usuario.secretarios.sec_cur_id)
    else:
        return Turmas.objects.none()
    return turmas.order_by("-tur_ano", "-tur_semestre", "tur_identificador")


def _aplicar_dados(turma, dados, travar_descricao_e_curso=False):
    """Copia os dados do formulário para a turma (Descrição e Curso só sem trava).

    [US-07][RBN-CAD-04.1][RBN-CAD-04.3][FR-005][Q15]
    """
    disciplina, _ = Disciplinas.objects.get_or_create(dis_codigo=dados["codigo_disciplina"])
    turma.tur_dis = disciplina
    turma.tur_identificador = dados["identificador"]
    turma.tur_ano = int(dados["ano"])
    turma.tur_semestre = int(dados["semestre"])
    turma.tur_dia_da_semana = dados["dia_semana"]
    turma.tur_hora_inicio = dados["hora_inicio"]
    turma.tur_hora_termino = dados["hora_termino"]
    turma.tur_local = dados["local"]
    if not travar_descricao_e_curso:
        turma.tur_descricao = dados["descricao"]
        turma.tur_cur = dados["curso"]


def _salvar_turma(turma):
    """Salva num savepoint; identificador repetido no banco (cadastro simultâneo) vira MT-03.

    [US-07][RBN-CAD-04.1][FR-002][MT-03]
    """
    try:
        with transaction.atomic():
            turma.save()
    except IntegrityError as erro:
        if "tur_identificador" in str(erro):
            raise ErroTurma(mensagens.MT03_IDENTIFICADOR_REPETIDO, campo="identificador")
        raise


def criar_turma(docente, dados):
    """Cadastra a turma com o Docente logado como Professor da Disciplina, 'Ativa'.

    [US-07][RBN-CAD-04.1][RBN-CAD-04.2][FR-001][FR-003][m3]
    """
    with transaction.atomic():
        turma = Turmas(tur_doc=docente.docentes, tur_status=StatusTurma.ATIVA)
        _aplicar_dados(turma, dados)
        _salvar_turma(turma)
    return turma


def editar_turma(professor, tur_id, dados):
    """Edita a turma, com a turma travada; Descrição e Curso ficam como estão na turma que tem
    ou já teve aluno (spec Q15). [US-07][RBN-CAD-04.3][FR-005][Q15][m3]
    """
    with transaction.atomic():
        turma = turma_para(professor, tur_id, ALTERAR, travar=True)
        _aplicar_dados(turma, dados, travar_descricao_e_curso=turma_ja_teve_aluno(turma))
        _salvar_turma(turma)
    return turma


def excluir_turma(professor, tur_id):
    """Exclui a turma que nunca teve aluno (spec Q12) e as entregas cadastradas nela; registra o
    evento no log depois do commit (research B4).
    [US-07][RBN-CAD-04.4][FR-006][Q12][m4]
    """
    with transaction.atomic():
        turma = turma_para(professor, tur_id, ALTERAR, travar=True)
        if turma_ja_teve_aluno(turma):
            raise ErroTurma(mensagens.TURMA_COM_ALUNOS)
        detalhe = f"tur_id={turma.pk} identificador={turma.tur_identificador}"
        TurmasMarcos.objects.filter(tma_tur=turma).delete()
        turma.delete()
        transaction.on_commit(
            lambda: registrar_evento(
                EventoAcesso.TURMA_EXCLUIDA, None, autor=professor, detalhe=detalhe
            )
        )


def motivo_para_nao_arquivar(turma):
    """Primeiro motivo que impede o arquivamento, na ordem da US-07, ou "" (RBN-CAD-04.5).

    [US-07][RBN-CAD-04.5][FR-007]
    """
    if TCCs.objects.filter(
        tcc_tur=turma, tcc_status__in=(StatusTCC.EM_ANDAMENTO, StatusTCC.APTO_PARA_DEFESA)
    ).exists():
        return mensagens.ARQUIVAR_TCC_ATIVO
    if Defesas.objects.filter(def_tcc__tcc_tur=turma, def_status__in=STATUS_SESSAO_ATIVA).exists():
        return mensagens.ARQUIVAR_SESSAO_ATIVA
    if turma.tur_descricao == DescricaoTurma.TCC_2:
        versao_final = TurmasMarcos.objects.filter(
            tma_tur=turma, tma_tipo=TipoEntrega.VERSAO_FINAL
        ).first()
        if versao_final is None or versao_final.tma_data_limite >= timezone.now():
            return mensagens.ARQUIVAR_VERSAO_FINAL
    return ""


def arquivar_turma(professor, tur_id):
    """Arquiva a turma com as três condições da RBN-CAD-04.5 atendidas, com a turma travada.

    [US-07][RBN-CAD-04.5][FR-007][FR-008]
    """
    with transaction.atomic():
        turma = turma_para(professor, tur_id, ALTERAR, travar=True)
        motivo = motivo_para_nao_arquivar(turma)
        if motivo:
            raise ErroTurma(motivo)
        turma.tur_status = StatusTurma.ARQUIVADA
        turma.save(update_fields=["tur_status"])
        _cancelar_pendentes_no_arquivamento(turma)
    return turma


def _cancelar_pendentes_no_arquivamento(turma):
    """Spec 006 (IC-12; FR-053; Q17): trava todos os alunos e depois todos os TCCs da turma (por
    pk, na ordem turma → aluno → TCC do research R2) e cancela os pedidos e convites pendentes, com
    a MO-26 a cada docente. O import fica aqui dentro para não haver import circular (N6).
    [US-07][RBN-CAD-04.5][FR-053][Q17][IC-12]
    """
    from sigtcc.apps.cadastro.services_orientacao import cancelar_pendentes_da_turma

    alunos = list(AlunosTurmas.objects.filter(mat_tur=turma).values_list("mat_alu_id", flat=True))
    list(Alunos.objects.select_for_update().filter(pk__in=alunos).order_by("pk"))
    list(TCCs.objects.select_for_update().filter(tcc_tur=turma).order_by("pk"))
    cancelar_pendentes_da_turma(turma, timezone.now())


def alunos_da_turma(turma):
    """Alunos matriculados, com Matrícula, Nome Completo, Curso e Status do TCC (FR-010).

    Spec 006 (IC-02; FR-017; research R14): cada linha traz também Título, Área de Interesse e
    Orientador ativo, para os blocos da aba "Alunos", sem consulta por linha (cursos, TCCs e
    orientações carregados de uma vez).
    [US-07][US-08][FR-010][RBN-CAD-05.7][RBN-CAD-08.3][spec 006 FR-017][IC-02]
    """
    vinculos = (
        AlunosTurmas.objects.filter(mat_tur=turma)
        .select_related("mat_alu__alu")
        .order_by("mat_alu__alu__usu_nome")
    )
    tccs = {t.tcc_alu_id: t for t in TCCs.objects.select_related("tcc_ari").filter(tcc_tur=turma)}
    orientadores = {
        o.ori_tcc_id: o.ori_doc.doc.usu_nome
        for o in Orientacoes.objects.select_related("ori_doc__doc").filter(
            ori_tcc__tcc_tur=turma, ori_status=StatusOrientacao.ATIVA
        )
    }
    cursos = {
        e.eqc_codigo_uea: e.eqc_cur
        for e in EquivalenciaCursos.objects.select_related("eqc_cur").filter(
            eqc_codigo_uea__in=[v.mat_alu.alu_codigo_curso for v in vinculos]
        )
    }
    linhas = []
    for vinculo in vinculos:
        aluno = vinculo.mat_alu
        curso = cursos.get(aluno.alu_codigo_curso)
        tcc = tccs.get(aluno.pk)
        linhas.append(
            {
                "aluno": aluno,
                "curso": curso.cur_nome if curso else mensagens.CURSO_NAO_RECONHECIDO,
                "tcc": tcc,
                "status_tcc": tcc.tcc_status if tcc else "",
                "encerrado": bool(tcc and participacao_encerrada(tcc)),
                "encerravel": aluno_pode_ser_encerrado(tcc),
                # Spec 006 (IC-02; FR-017): dados do bloco.
                "titulo": (tcc.tcc_titulo or "") if tcc else "",
                "area": tcc.tcc_ari.ari_nome if tcc and tcc.tcc_ari_id else "",
                "orientador": orientadores.get(tcc.pk, "") if tcc else "",
                "transferivel": bool(tcc and tcc.tcc_status in STATUS_TCC_TRANSFERIVEL),
            }
        )
    return linhas


# =============================================================================================
# Matrícula de alunos e edição do aluno (US-08; research B6 a B8, B12)
# =============================================================================================

# Status em que algum TCC impede nova matrícula (spec Q7). [US-08][RBN-CAD-05.5][Q7]
STATUS_TCC_CONCLUIDO = (StatusTCC.APROVADO, StatusTCC.APROVADO_COM_CORRECOES, StatusTCC.CONCLUIDO)


class EstadoMatricula(enum.Enum):
    """Resultado da matrícula de uma linha (individual ou do arquivo). [US-08][RBN-CAD-05.1]"""

    CRIADO = "criado"
    VINCULADO = "vinculado"
    COPIADO = "copiado"
    JA_NA_TURMA = "ja_na_turma"
    TCC_EM_CURSO = "tcc_em_curso"
    TCC_CONCLUIDO = "tcc_concluido"
    APROVADO_EM_TURMA_TCC1 = "aprovado_em_turma_tcc1"


RECUSAS = (
    EstadoMatricula.JA_NA_TURMA,
    EstadoMatricula.TCC_EM_CURSO,
    EstadoMatricula.TCC_CONCLUIDO,
    EstadoMatricula.APROVADO_EM_TURMA_TCC1,
)


@dataclass
class ResultadoMatricula:
    """Estado, aluno, mensagem principal e avisos (MT-13, MT-29) da matrícula.

    [US-08][RBN-CAD-05.1][RBN-CAD-05.5][RBN-CAD-05.7][Q16]
    """

    estado: EstadoMatricula
    aluno: object = None
    mensagem: str = ""
    avisos: list = field(default_factory=list)
    curso_reconhecido: bool = True

    @property
    def matriculado(self):
        """O aluno ficou vinculado à turma (não foi recusado). [US-08][RBN-CAD-05.1]"""
        return self.estado not in RECUSAS


def _criar_aluno_novo(matricula, nome, codigo_curso):
    """Conta 'Aguardando Ativação' sem e-mail, sem senha e sem link (spec 003, Q1) e o Aluno.

    [US-08][RBN-CAD-05.1][FR-012]
    """
    usuario = Usuarios.objects.create_user(None, nome, usu_status=StatusConta.AGUARDANDO_ATIVACAO)
    return Alunos.objects.create(
        alu=usuario, alu_matricula=matricula, alu_codigo_curso=codigo_curso
    )


def _aluno_travado(matricula):
    """Aluno pela matrícula, travado (select_for_update), ou None. [B6][m8]"""
    return (
        Alunos.objects.select_for_update(of=("self",))
        .select_related("alu")
        .filter(alu_matricula=matricula)
        .first()
    )


def _registrar_historico(tcc, turma, autor, anterior, novo, gatilho, agora=None):
    """Uma transição do Status do TCC no histórico (RBN-CAD-08.7). Com `agora`, grava esse mesmo
    instante: os cancelamentos causados pelo evento usam o mesmo valor, e é essa igualdade que
    deduz o motivo (spec 006, FR-050; research R3; IC-04).
    [RBN-CAD-08.7][FR-012][spec 006 FR-050]
    """
    HistoricoStatusTCC.objects.create(
        hst_tcc=tcc,
        hst_tur=turma,
        hst_status_anterior=anterior,
        hst_status_novo=novo,
        hst_gatilho=gatilho,
        hst_data_hora=agora or timezone.now(),
        hst_usu=autor,
    )


# =============================================================================================
# Serviço único de gravação do Status do TCC (spec 005, US-14; FR-008, FR-012; research C2)
# =============================================================================================

# Gatilho → conjunto de transições (status_atual, novo_status) permitidas (FR-008; data-model.md).
# status_atual=None só nos gatilhos de criação, quando não há TCC (nem linha de origem) anterior.
# "Encerramento da participação" usa só EM_ANDAMENTO/APTO_PARA_DEFESA como origem, igual a
# STATUS_TCC_ENCERRAVEL (aluno "Sem Proposta" é excluído da turma, US-09, não encerrado).
# [US-14][RBN-CAD-08.3][FR-008][research C2]
TRANSICOES_VALIDAS = {
    GatilhoStatusTCC.VINCULO_A_TURMA: {(None, StatusTCC.SEM_PROPOSTA)},
    GatilhoStatusTCC.PROPOSTA_SALVA: {(StatusTCC.SEM_PROPOSTA, StatusTCC.EM_ANDAMENTO)},
    GatilhoStatusTCC.TRANSFERENCIA_PARA_TCC_2: {
        (StatusTCC.APROVADO_PARA_TCC_2, StatusTCC.EM_ANDAMENTO)
    },
    GatilhoStatusTCC.INDICACAO_DE_APTO: {(StatusTCC.EM_ANDAMENTO, StatusTCC.APTO_PARA_DEFESA)},
    GatilhoStatusTCC.LIBERACAO_DO_RESULTADO: {
        (StatusTCC.APTO_PARA_DEFESA, StatusTCC.APROVADO_PARA_TCC_2),
        (StatusTCC.APTO_PARA_DEFESA, StatusTCC.APROVADO),
        (StatusTCC.APTO_PARA_DEFESA, StatusTCC.APROVADO_COM_CORRECOES),
        (StatusTCC.APTO_PARA_DEFESA, StatusTCC.REPROVADO),
    },
    GatilhoStatusTCC.HOMOLOGACAO_DA_VERSAO_FINAL: {
        (StatusTCC.APROVADO, StatusTCC.CONCLUIDO),
        (StatusTCC.APROVADO_COM_CORRECOES, StatusTCC.CONCLUIDO),
    },
    GatilhoStatusTCC.ENCERRAMENTO_DA_PARTICIPACAO: {
        (de, para)
        # Só EM_ANDAMENTO e APTO_PARA_DEFESA (igual a STATUS_TCC_ENCERRAVEL, definida mais abaixo
        # neste mesmo arquivo; repetida aqui em vez de referenciada por não poder vir antes desta
        # definição no módulo — aluno "Sem Proposta" é excluído da turma, US-09, não encerrado).
        for de in (StatusTCC.EM_ANDAMENTO, StatusTCC.APTO_PARA_DEFESA)
        for para in STATUS_PARTICIPACAO_ENCERRADA
    },
}


def _validar_transicao(anterior, novo_status, gatilho):
    """Levanta ValueError se (anterior → novo_status) não estiver prevista para o gatilho
    (FR-008) — chamada pelas duas funções públicas abaixo, nunca pulada.
    [US-14][RBN-CAD-08.3][FR-008][research C2]
    """
    if (
        gatilho not in TRANSICOES_VALIDAS
        or (anterior, novo_status) not in TRANSICOES_VALIDAS[gatilho]
    ):
        raise ValueError(
            f"Transição inválida: {anterior!r} → {novo_status!r} pelo gatilho {gatilho!r}"
        )


def criar_tcc_com_historico(
    aluno, turma, autor, status_inicial, gatilho, anterior=None, agora=None, **campos_tcc
):
    """Único ponto que cria um TCC e grava o primeiro registro do histórico (FR-008, FR-012).

    Usada pelos 2 gatilhos de criação: "Vínculo à turma" (`anterior=None`, matrícula nova, sem
    `campos_tcc` — o TCC nasce "Sem Proposta", sem título/resumo/modalidade) e "Transferência para
    TCC 2" (`anterior` = status do TCC de origem, ex. `tcc1.tcc_status`, lido por quem chama
    **antes** de passar para esta função; `campos_tcc` = `tcc_titulo`, `tcc_subtitulo`,
    `tcc_resumo`, `tcc_modalidade`, `tcc_link_proposta`, `tcc_ari`, copiados do TCC de origem —
    **obrigatórios** nesse gatilho porque `status_inicial="Em Andamento"` cai na `CHECK
    ck_tccs_campos_obrigatorios_com_proposta` do dicionário, que exige esses campos fora de "Sem
    Proposta"). Pressupõe turma, aluno e — na transferência — o TCC de origem já travados pelo
    chamador (`select_for_update`, research C4). `agora` opcional: o instante do evento (spec 006,
    FR-050; IC-04).
    [US-14][RBN-CAD-08.3][RBN-CAD-08.7][FR-008][FR-012][research C2][research C4]
    """
    _validar_transicao(anterior, status_inicial, gatilho)
    tcc = TCCs.objects.create(tcc_alu=aluno, tcc_tur=turma, tcc_status=status_inicial, **campos_tcc)
    _registrar_historico(tcc, turma, autor, anterior, status_inicial, gatilho, agora)
    return tcc


def atualizar_status_tcc(tcc, turma, autor, novo_status, gatilho, agora=None):
    """Único ponto que muda tcc_status de um TCC **já existente** e grava o histórico (FR-008,
    FR-012). Usada pelos 5 gatilhos de transição: "Proposta salva", "Indicação de Apto para
    Defesa", "Liberação do resultado", "Homologação da Versão Final" e "Encerramento da
    participação". Pressupõe que o chamador já travou turma → aluno → TCC (`select_for_update`,
    dentro do mesmo `transaction.atomic()`, research C4) **antes** de chamar esta função — ela não
    trava nada por si. Levanta ValueError se a transição não for válida; nesse caso, nenhuma linha
    é gravada. `agora` opcional: o instante do evento (spec 006, FR-050; IC-04).
    [US-14][RBN-CAD-08.3][RBN-CAD-08.7][FR-008][FR-012][research C2][research C4]
    """
    anterior = tcc.tcc_status
    _validar_transicao(anterior, novo_status, gatilho)
    tcc.tcc_status = novo_status
    tcc.save(update_fields=["tcc_status"])
    _registrar_historico(tcc, turma, autor, anterior, novo_status, gatilho, agora)


def _criar_orientacao_automatica(tcc, turma, agora=None):
    """Professor da turma como Orientador, origem 'Automático' (RBN-CAD-04.2). Com `agora`, o
    início do vínculo é o instante do evento (spec 006, FR-050; IC-04). [FR-004][B8]
    """
    Orientacoes.objects.create(
        ori_tcc=tcc,
        ori_doc=turma.tur_doc,
        ori_origem=OrigemOrientacao.AUTOMATICO,
        ori_status=StatusOrientacao.ATIVA,
        ori_data_inicio=agora or timezone.now(),
    )


def encerrar_orientacoes_ativas(tcc, agora=None):
    """Orientações e coorientações 'Ativa' do TCC → 'Encerrada', com data de fim.

    [US-08][US-09][RBN-CAD-05.6][RBN-CAD-08.4][RBN-CAD-08.6][Q10][B7]
    """
    agora = agora or timezone.now()
    Orientacoes.objects.filter(ori_tcc=tcc, ori_status=StatusOrientacao.ATIVA).update(
        ori_status=StatusOrientacao.ENCERRADA, ori_data_fim=agora
    )
    Coorientacoes.objects.filter(coo_tcc=tcc, coo_status=StatusCoorientacao.ATIVA).update(
        coo_status=StatusCoorientacao.ENCERRADA, coo_data_fim=agora
    )


def _copiar_tcc_aprovado(autor, turma, aluno, tcc1):
    """Aprovado em TCC 1 matriculado em TCC 2: novo TCC carregado com os dados do TCC 1, direto
    'Em Andamento'; o TCC 1 fica como histórico (spec Q6; research B7).

    Spec 006 (IC-04; FR-050, FR-051): trava o TCC 1 (o aluno já vem travado por `matricular`),
    grava o mesmo `agora` no histórico, nas orientações e nos cancelamentos, e cancela os pedidos
    e convites pendentes do TCC 1, avisando cada docente com a MO-18.
    [US-08][RBN-CAD-05.5][RBN-CAD-08.6][FR-013][Q6][I-13][m6][spec 006 FR-050][FR-051]
    """
    agora = timezone.now()
    tcc1 = TCCs.objects.select_for_update(of=("self",)).get(pk=tcc1.pk)
    orientacoes = list(Orientacoes.objects.filter(ori_tcc=tcc1, ori_status=StatusOrientacao.ATIVA))
    coorientacoes = list(
        Coorientacoes.objects.filter(coo_tcc=tcc1, coo_status=StatusCoorientacao.ATIVA)
    )
    encerrar_orientacoes_ativas(tcc1, agora)
    # criar_tcc_com_historico estendida com **campos_tcc (research C2, decisão de Julia Cohen
    # 2026-10-22) para satisfazer a CHECK ck_tccs_campos_obrigatorios_com_proposta, que exige
    # título/resumo/modalidade preenchidos fora de "Sem Proposta".
    novo = criar_tcc_com_historico(
        aluno,
        turma,
        autor,
        StatusTCC.EM_ANDAMENTO,
        GatilhoStatusTCC.TRANSFERENCIA_PARA_TCC_2,
        anterior=tcc1.tcc_status,
        agora=agora,
        tcc_titulo=tcc1.tcc_titulo,
        tcc_subtitulo=tcc1.tcc_subtitulo,
        tcc_resumo=tcc1.tcc_resumo,
        tcc_modalidade=tcc1.tcc_modalidade,
        tcc_link_proposta=tcc1.tcc_link_proposta,
        tcc_ari=tcc1.tcc_ari,
    )
    for palavra in PalavrasChaveTCC.objects.filter(pal_tcc=tcc1):
        PalavrasChaveTCC.objects.create(pal_tcc=novo, pal_palavra=palavra.pal_palavra)
    artigo = Artigos.objects.filter(art=tcc1).first()
    if artigo is not None:
        Artigos.objects.create(
            art=novo,
            art_veiculo_publicacao=artigo.art_veiculo_publicacao,
            art_link_doi=artigo.art_link_doi,
            art_qualis_capes=artigo.art_qualis_capes,
            art_status_submissao=artigo.art_status_submissao,
            art_homologacao=artigo.art_homologacao,
            art_homologado_por=artigo.art_homologado_por,
            art_data_homologacao=artigo.art_data_homologacao,
        )
    automatico = turma_tem_orientador_automatico(turma)
    if automatico:
        _criar_orientacao_automatica(novo, turma, agora)
    else:
        for orientacao in orientacoes:
            Orientacoes.objects.create(
                ori_tcc=novo,
                ori_doc_id=orientacao.ori_doc_id,
                ori_origem=orientacao.ori_origem,
                ori_status=StatusOrientacao.ATIVA,
                ori_data_inicio=agora,
            )
    for coorientacao in coorientacoes:
        if automatico and coorientacao.coo_doc_id == turma.tur_doc_id:
            continue
        Coorientacoes.objects.create(
            coo_tcc=novo,
            coo_doc_id=coorientacao.coo_doc_id,
            coo_cext_id=coorientacao.coo_cext_id,
            coo_status=StatusCoorientacao.ATIVA,
            coo_data_inicio=agora,
        )
    _cancelar_pendentes_do_tcc1(tcc1, aluno, agora)
    return novo


def _cancelar_pendentes_do_tcc1(tcc1, aluno, agora):
    """Spec 006 (FR-051; MO-18): pedidos e convites pendentes do TCC 1 → 'Cancelado' com o
    instante do gatilho "Transferência para TCC 2"; cada docente é avisado na mesma transação.
    [US-17][US-45][RBN-CAD-08.6][FR-050][FR-051][Q6][IC-04]
    """
    pendentes = list(
        SolicitacoesOrientacao.objects.select_related("sol_doc__doc").filter(
            sol_tcc=tcc1,
            sol_status__in=(
                StatusSolicitacao.AGUARDANDO_RESPOSTA,
                StatusSolicitacao.AGUARDANDO_ACEITE,
            ),
        )
    )
    SolicitacoesOrientacao.objects.filter(pk__in=[s.pk for s in pendentes]).update(
        sol_status=StatusSolicitacao.CANCELADO, sol_data_resposta=agora
    )
    for solicitacao in pendentes:
        tipo = (
            mensagens.TIPO_CONVITE_COORIENTACAO
            if solicitacao.sol_tipo == TipoSolicitacao.COORIENTACAO
            else mensagens.TIPO_PEDIDO_ORIENTACAO
        )
        notificar(
            solicitacao.sol_doc.doc,
            mensagens.MO18_NOTIFICACAO.format(tipo=tipo, nome=aluno.alu.usu_nome),
            link=reverse("cadastro:orientacoes"),
        )


def _recusa_por_tccs(aluno, turma):
    """Recusa da matrícula pelos TCCs do aluno (spec Q7; Q-39), ou None e o TCC a copiar.

    [US-08][RBN-CAD-05.5][FR-013][Q7][m5]
    """
    tccs = TCCs.objects.filter(tcc_alu=aluno).select_related("tcc_tur")
    em_curso = (
        tccs.filter(tcc_status__in=STATUS_TCC_EM_CURSO)
        .exclude(tcc_tur__tur_status=StatusTurma.ARQUIVADA)
        .first()
    )
    if em_curso is not None:
        mensagem = mensagens.MT26_TCC_EM_CURSO.format(
            identificador=em_curso.tcc_tur.tur_identificador
        )
        return ResultadoMatricula(EstadoMatricula.TCC_EM_CURSO, aluno, mensagem), None
    if tccs.filter(tcc_status__in=STATUS_TCC_CONCLUIDO).exists():
        return (
            ResultadoMatricula(EstadoMatricula.TCC_CONCLUIDO, aluno, mensagens.MT27_TCC_CONCLUIDO),
            None,
        )
    ultimo = tccs.order_by("-tcc_id").first()
    if ultimo is not None and ultimo.tcc_status == StatusTCC.APROVADO_PARA_TCC_2:
        if turma.tur_descricao != DescricaoTurma.TCC_2:
            # PROVISÓRIO até a resposta da Q-39 do índice (research B6).
            return (
                ResultadoMatricula(
                    EstadoMatricula.APROVADO_EM_TURMA_TCC1,
                    aluno,
                    mensagens.MT28_APROVADO_EM_TURMA_TCC1,
                ),
                None,
            )
        return None, ultimo
    return None, None


def matricular(professor, turma, matricula, nome, codigo_curso):
    """Matricula um aluno na turma (individual ou uma linha do arquivo), na ordem do diagrama
    "Matrícula por CSV" e do research B6. A turma deve vir travada por quem chama.
    [US-08][RBN-CAD-05.1][RBN-CAD-05.5][RBN-CAD-05.7][RBN-CAD-04.2][FR-011]-[FR-015][Q7][Q16]
    [Q17][m7][m8]
    """
    curso = curso_do_codigo(codigo_curso)
    avisos = []
    aluno = _aluno_travado(matricula)
    novo = False
    if aluno is None:
        try:
            with transaction.atomic():
                aluno = _criar_aluno_novo(matricula, nome, codigo_curso)
            novo = True
        except IntegrityError:
            # Outra requisição cadastrou a matrícula no meio (m7): segue como aluno existente.
            aluno = _aluno_travado(matricula)
            if aluno is None:
                raise
    tcc_para_copiar = None
    if not novo:
        if AlunosTurmas.objects.filter(mat_tur=turma, mat_alu=aluno).exists():
            return ResultadoMatricula(
                EstadoMatricula.JA_NA_TURMA, aluno, mensagens.ALUNO_JA_NA_TURMA
            )
        recusa, tcc_para_copiar = _recusa_por_tccs(aluno, turma)
        if recusa is not None:
            return recusa
        if aluno.alu.usu_status in (StatusConta.INATIVA, StatusConta.EXPIRADA):
            avisos.append(mensagens.MT29_CONTA_NAO_ATIVA.format(status=aluno.alu.usu_status))
        curso = curso_do_codigo(aluno.alu_codigo_curso)
    AlunosTurmas.objects.create(mat_alu=aluno, mat_tur=turma, mat_data_inscricao=timezone.now())
    if tcc_para_copiar is not None:
        _copiar_tcc_aprovado(professor, turma, aluno, tcc_para_copiar)
        estado = EstadoMatricula.COPIADO
    else:
        # Gatilho de criação "Vínculo à turma": sem campos de Proposta, SEM_PROPOSTA não tem o
        # problema de ck_tccs_campos_obrigatorios_com_proposta (spec 005, FR-012; research C2).
        tcc = criar_tcc_com_historico(
            aluno, turma, professor, StatusTCC.SEM_PROPOSTA, GatilhoStatusTCC.VINCULO_A_TURMA
        )
        if turma_tem_orientador_automatico(turma):
            _criar_orientacao_automatica(tcc, turma)
        estado = EstadoMatricula.CRIADO if novo else EstadoMatricula.VINCULADO
    criar_entregas_do_aluno(aluno, turma)
    if curso is not None and curso.pk != turma.tur_cur_id:
        avisos.append(
            mensagens.MT13_CURSO_DIVERGENTE.format(
                curso_aluno=curso.cur_nome, curso_turma=turma.tur_cur.cur_nome
            )
        )
    return ResultadoMatricula(
        estado, aluno, mensagens.ALUNO_MATRICULADO, avisos, curso_reconhecido=curso is not None
    )


def matricular_individual(professor, tur_id, matricula, nome, codigo_curso):
    """Matrícula individual com a turma travada (research B17). [US-08][RBN-CAD-05.1][FR-011]"""
    with transaction.atomic():
        turma = turma_para(professor, tur_id, ALTERAR, travar=True)
        return matricular(professor, turma, matricula, nome, codigo_curso)


def editar_aluno(professor, tur_id, alu_id, nome, codigo_curso):
    """Corrige Nome Completo e Curso do aluno da turma; a Matrícula não muda (RBN-CAD-05.3).

    [US-08][RBN-CAD-05.3][FR-019][I-7]
    """
    with transaction.atomic():
        turma = turma_para(professor, tur_id, ALTERAR, travar=True)
        aluno = vinculo_na_turma(turma, alu_id)
        aluno = _aluno_travado(aluno.alu_matricula)
        aluno.alu.usu_nome = nome
        aluno.alu.save(update_fields=["usu_nome"])
        aluno.alu_codigo_curso = codigo_curso
        aluno.save(update_fields=["alu_codigo_curso"])
    return aluno


# =============================================================================================
# Importação: prévia na sessão e confirmação (US-08; research B10)
# =============================================================================================

CHAVE_PREVIA = "importacao"
CHAVE_RESUMO = "importacao_resumo"
VALIDADE_PREVIA = timedelta(minutes=30)


class PreviaInvalida(Exception):
    """Prévia ausente, vencida, de outra turma ou com código errado. [US-08][MT-32][B10][B-2]"""


class ImportacaoRepetida(Exception):
    """O mesmo código de prévia já foi confirmado (dois POST simultâneos). [US-08][B10][N3]"""


def guardar_previa(sessao, turma, previa):
    """Guarda na sessão só o mínimo: código, turma, instante, linhas válidas normalizadas e, das
    linhas com erro, só o número e o motivo (achado I-10). Substitui a prévia anterior.
    [US-08][RBN-CAD-05.2][FR-017][B-2][I-10]
    """
    token = secrets.token_urlsafe(16)
    sessao[CHAVE_PREVIA] = {
        "token": token,
        "tur_id": turma.pk,
        "instante": timezone.now().isoformat(),
        "linhas": [[i.numero, i.matricula, i.nome, i.curso] for i in previa.validos],
        "erros": [[i.numero, i.motivo] for i in previa.rejeitados],
    }
    return token


def descartar_previa(sessao):
    """ "Cancelar" na prévia: apaga a prévia da sessão. [US-08][B10]"""
    sessao.pop(CHAVE_PREVIA, None)


def _previa_vencida(previa):
    """Prévia com mais de 30 minutos. [US-08][RBN-CAD-05.2][B10]"""
    return timezone.now() - datetime.fromisoformat(previa["instante"]) > VALIDADE_PREVIA


def confirmar_importacao(professor, tur_id, token, sessao):
    """ "Confirmar importação": confere a prévia (código, turma e prazo), tira a prévia da sessão,
    marca o código como usado e matricula linha a linha, cada uma num savepoint (spec Q2).
    Devolve o resumo da MT-15: n (matriculados), r (rejeitadas), c (códigos não reconhecidos) e a
    lista de rejeitadas (linha e motivo).
    [US-08][RBN-CAD-05.2][FR-018][Q2][B-2][N3][m8]
    """
    previa = sessao.get(CHAVE_PREVIA)
    if previa is None or not token or not constant_time_compare(previa["token"], token):
        raise PreviaInvalida
    if previa["tur_id"] != tur_id or _previa_vencida(previa):
        if _previa_vencida(previa):
            descartar_previa(sessao)
        raise PreviaInvalida
    descartar_previa(sessao)
    # O cache padrão pode descartar entradas, mas a marca só precisa durar os segundos entre dois
    # POST simultâneos (análise D5).
    if not caches["default"].add(f"importacao:{token}", 1, 3600):
        raise ImportacaoRepetida
    rejeitadas = [tuple(erro) for erro in previa["erros"]]
    matriculados = nao_reconhecidos = 0
    with transaction.atomic():
        turma = turma_para(professor, tur_id, ALTERAR, travar=True)
        matriculas = sorted(linha[1] for linha in previa["linhas"])
        list(
            Alunos.objects.select_for_update()
            .filter(alu_matricula__in=matriculas)
            .order_by("alu_matricula")
        )
        for numero, matricula, nome, codigo_curso in previa["linhas"]:
            with transaction.atomic():
                resultado = matricular(professor, turma, matricula, nome, codigo_curso)
            if resultado.matriculado:
                matriculados += 1
                nao_reconhecidos += 0 if resultado.curso_reconhecido else 1
            else:
                rejeitadas.append((numero, resultado.mensagem))
    rejeitadas.sort()
    return {
        "n": matriculados,
        "r": len(rejeitadas),
        "c": nao_reconhecidos,
        "rejeitadas": [list(r) for r in rejeitadas],
    }


# =============================================================================================
# Transferência para a turma de TCC 2 de outro orientador (US-08; RBN-CAD-05.6; research B13)
# =============================================================================================

STATUS_TCC_TRANSFERIVEL = (StatusTCC.EM_ANDAMENTO, StatusTCC.APTO_PARA_DEFESA)


def turmas_destino_possiveis(turma_origem, aluno):
    """Turmas de TCC 2, do mesmo curso e período, 'Ativa', de outro Professor da Disciplina e sem
    vínculo nem TCC do aluno (evita as unicidades; achado I-1).
    [US-08][RBN-CAD-05.6][FR-020][I-1]
    """
    return (
        Turmas.objects.filter(
            tur_descricao=DescricaoTurma.TCC_2,
            tur_cur_id=turma_origem.tur_cur_id,
            tur_ano=turma_origem.tur_ano,
            tur_semestre=turma_origem.tur_semestre,
            tur_status=StatusTurma.ATIVA,
        )
        .exclude(tur_doc_id=turma_origem.tur_doc_id)
        .exclude(alunosturmas__mat_alu=aluno)
        .exclude(tccs__tcc_alu=aluno)
        .select_related("tur_doc__doc")
        .order_by("tur_identificador")
    )


def _travar_turmas_em_ordem(*tur_ids):
    """Trava as turmas em ordem de tur_id, para duas transferências não se travarem.

    [US-08][RBN-CAD-05.6][B17][I-2]
    """
    list(Turmas.objects.select_for_update().filter(pk__in=tur_ids).order_by("pk"))


def transferir(autor, tur_origem_id, alu_id, tur_destino_id, justificativa):
    """Transfere o aluno: o mesmo TCC, com o Status e o histórico, vai para a turma de destino e o
    professor dela passa a orientar (RBN-CAD-05.6; research B13).
    [US-08][RBN-CAD-05.6][RBN-CAD-04.2][FR-020][FR-021][FR-022][Q17][I-1][m6][m11]
    """
    with transaction.atomic():
        _travar_turmas_em_ordem(tur_origem_id, tur_destino_id)
        origem = turma_para(autor, tur_origem_id, TRANSFERIR)
        if not turma_tem_orientador_automatico(origem):
            raise PermissionDenied
        aluno = vinculo_na_turma(origem, alu_id)
        tcc = TCCs.objects.select_for_update().get(tcc_alu=aluno, tcc_tur=origem)
        if tcc.tcc_status not in STATUS_TCC_TRANSFERIVEL:
            raise ErroTurma(mensagens.MT17_TRANSFERENCIA_STATUS)
        if Defesas.objects.filter(def_tcc=tcc, def_status__in=STATUS_SESSAO_ATIVA).exists():
            raise ErroTurma(mensagens.MT18_TRANSFERENCIA_SESSAO)
        destino = turmas_destino_possiveis(origem, aluno).filter(pk=tur_destino_id).first()
        if destino is None:
            raise ErroTurma(mensagens.MT19_SEM_DESTINO)
        agora = timezone.now()
        Orientacoes.objects.filter(ori_tcc=tcc, ori_status=StatusOrientacao.ATIVA).update(
            ori_status=StatusOrientacao.ENCERRADA, ori_data_fim=agora
        )
        tcc.tcc_tur = destino
        tcc.save(update_fields=["tcc_tur"])
        AlunosTurmas.objects.filter(mat_alu=aluno, mat_tur=origem).delete()
        AlunosTurmas.objects.create(mat_alu=aluno, mat_tur=destino, mat_data_inscricao=agora)
        # Spec 006 (IC-04; FR-050): o mesmo instante do convite cancelado abaixo, para o link do
        # convite mostrar a MO-17 ("o docente passou a ser o orientador").
        _criar_orientacao_automatica(tcc, destino, agora)
        Coorientacoes.objects.filter(
            coo_tcc=tcc, coo_doc_id=destino.tur_doc_id, coo_status=StatusCoorientacao.ATIVA
        ).update(coo_status=StatusCoorientacao.ENCERRADA, coo_data_fim=agora)
        SolicitacoesOrientacao.objects.filter(
            sol_tcc=tcc,
            sol_doc_id=destino.tur_doc_id,
            sol_tipo=TipoSolicitacao.COORIENTACAO,
            sol_status=StatusSolicitacao.AGUARDANDO_ACEITE,
        ).update(sol_status=StatusSolicitacao.CANCELADO, sol_data_resposta=agora)
        remover_entregas_sem_envio(aluno, origem)
        criar_entregas_do_aluno(aluno, destino)
        HistoricoAlunosTurmas.objects.create(
            hat_alu=aluno,
            hat_tur_origem=origem,
            hat_tur_destino=destino,
            hat_tipo_evento=TipoEventoTurma.TRANSFERENCIA,
            hat_justificativa=justificativa,
            hat_data_hora=agora,
            hat_usu=autor,
        )
        texto = mensagens.MT22_NOTIFICACAO_TRANSFERENCIA.format(
            nome=aluno.alu.usu_nome,
            origem=origem.tur_identificador,
            destino=destino.tur_identificador,
        )
        notificar(aluno.alu, texto)
        notificar(origem.tur_doc.doc, texto)
        notificar(destino.tur_doc.doc, texto, link=reverse("cadastro:turma", args=[destino.pk]))
    return destino


# =============================================================================================
# Exclusão do aluno e encerramento da participação (US-09; research B14 a B16)
# =============================================================================================

# Status em que o Professor encerra a participação (research B15). [RBN-CAD-08.4][FR-024]
STATUS_TCC_ENCERRAVEL = (StatusTCC.EM_ANDAMENTO, StatusTCC.APTO_PARA_DEFESA)

# Confere que TRANSICOES_VALIDAS (spec 005, research C2) usa exatamente estas origens para o
# gatilho "Encerramento da participação" — as duas tabelas não podem divergir (FR-008).
assert {de for de, _ in TRANSICOES_VALIDAS[GatilhoStatusTCC.ENCERRAMENTO_DA_PARTICIPACAO]} == set(
    STATUS_TCC_ENCERRAVEL
)

# Pedidos e convites ainda sem resposta, cancelados pelo encerramento (spec Q14). [Q14]
STATUS_SOLICITACAO_PENDENTE = (
    StatusSolicitacao.AGUARDANDO_RESPOSTA,
    StatusSolicitacao.AGUARDANDO_ACEITE,
)


def tcc_do_aluno(turma, aluno):
    """TCC do aluno nesta turma, ou None. [US-09][RBN-CAD-08.3]"""
    return TCCs.objects.filter(tcc_alu=aluno, tcc_tur=turma).first()


def _trabalho_movimentado(tcc):
    """O TCC já tem solicitação, encontro, orientação por pedido, coorientação, palavra-chave,
    publicação ou defesa: o trabalho já foi movimentado e a exclusão é recusada (research B14).
    [US-09][RBN-CAD-05.4][FR-023]
    """
    return (
        SolicitacoesOrientacao.objects.filter(sol_tcc=tcc).exists()
        or EncontroOrientacao.objects.filter(enc_tcc=tcc).exists()
        or Orientacoes.objects.filter(ori_tcc=tcc)
        .exclude(ori_origem=OrigemOrientacao.AUTOMATICO)
        .exists()
        or Coorientacoes.objects.filter(coo_tcc=tcc).exists()
        or PalavrasChaveTCC.objects.filter(pal_tcc=tcc).exists()
        or Artigos.objects.filter(art=tcc).exists()
        or Defesas.objects.filter(def_tcc=tcc).exists()
    )


def aluno_pode_ser_excluido(tcc):
    """Sem TCC ou com TCC 'Sem Proposta' ainda não movimentado (RBN-CAD-05.4; research B14).

    [US-09][RBN-CAD-05.4][FR-023]
    """
    return tcc is None or (
        tcc.tcc_status == StatusTCC.SEM_PROPOSTA and not _trabalho_movimentado(tcc)
    )


def aluno_pode_ser_encerrado(tcc):
    """TCC 'Em Andamento' ou 'Apto para Defesa' (research B15). [US-09][RBN-CAD-08.4][FR-024]"""
    return tcc is not None and tcc.tcc_status in STATUS_TCC_ENCERRAVEL


def excluir_aluno(professor, tur_id, alu_id, justificativa):
    """Exclui da turma o aluno sem Proposta: apaga o histórico de status, a orientação automática
    e o TCC 'Sem Proposta' (Q8), os registros de entrega sem envio (Q17) e o vínculo; grava a
    exclusão no histórico da turma e avisa o aluno com a MT-21 (research B14; travas B17).
    [US-09][RBN-CAD-05.4][RBN-CAD-05.8][FR-023][Q8][Q17][B-1]
    """
    with transaction.atomic():
        turma = turma_para(professor, tur_id, ALTERAR, travar=True)
        aluno = vinculo_na_turma(turma, alu_id)
        tcc = TCCs.objects.select_for_update().filter(tcc_alu=aluno, tcc_tur=turma).first()
        if not aluno_pode_ser_excluido(tcc):
            raise ErroTurma(mensagens.ALUNO_TEM_PROPOSTA)
        if tcc is not None:
            HistoricoStatusTCC.objects.filter(hst_tcc=tcc).delete()
            Orientacoes.objects.filter(ori_tcc=tcc, ori_origem=OrigemOrientacao.AUTOMATICO).delete()
            tcc.delete()
        remover_entregas_sem_envio(aluno, turma)
        AlunosTurmas.objects.filter(mat_alu=aluno, mat_tur=turma).delete()
        HistoricoAlunosTurmas.objects.create(
            hat_alu=aluno,
            hat_tur_origem=turma,
            hat_tur_destino=None,
            hat_tipo_evento=TipoEventoTurma.EXCLUSAO,
            hat_justificativa=justificativa,
            hat_data_hora=timezone.now(),
            hat_usu=professor,
        )
        texto = montar_mensagem_cortada(
            mensagens.MT21_NOTIFICACAO_EXCLUSAO,
            "justificativa",
            identificador=turma.tur_identificador,
            justificativa=justificativa,
        )
        notificar(aluno.alu, texto)
    return aluno


def encerrar_participacao(professor, tur_id, alu_id, status, justificativa):
    """Encerra a participação como Desistente, Reprovado ou Jubilado (RBN-CAD-08.4): muda o Status
    com histórico, encerra orientação e coorientação ativas (Q10), cancela os pedidos e convites
    pendentes e avisa cada docente com a MT-31 (Q14, Q19). Com sessão de defesa ativa, recusa com
    a MT-30. Tudo conferido de novo depois de travar a turma e o TCC (research B15 e B17; I-2).
    [US-09][RBN-CAD-08.4][RBN-CAD-08.5][RBN-CAD-08.7][FR-024][Q10][Q14][Q19][I-2]
    """
    if status not in STATUS_PARTICIPACAO_ENCERRADA:
        raise ErroTurma(mensagens.SELECIONE_STATUS, campo="status")
    with transaction.atomic():
        turma = turma_para(professor, tur_id, ALTERAR, travar=True)
        aluno = vinculo_na_turma(turma, alu_id)
        tcc = TCCs.objects.select_for_update().filter(tcc_alu=aluno, tcc_tur=turma).first()
        if not aluno_pode_ser_encerrado(tcc):
            raise Http404
        if Defesas.objects.filter(def_tcc=tcc, def_status__in=STATUS_SESSAO_ATIVA).exists():
            raise ErroTurma(mensagens.MT30_ENCERRAMENTO_SESSAO)
        agora = timezone.now()
        # Gatilho de transição "Encerramento da participação" (spec 005, FR-012; research C2):
        # turma → aluno → TCC já travados acima (select_for_update); tcc_justificativa_encerramento
        # não faz parte do Status nem do histórico, gravado à parte, no mesmo UPDATE.
        tcc.tcc_justificativa_encerramento = justificativa
        tcc.save(update_fields=["tcc_justificativa_encerramento"])
        # Spec 006 (IC-04; FR-050): o mesmo `agora` dos cancelamentos abaixo deduz a MO-12.
        atualizar_status_tcc(
            tcc, turma, professor, status, GatilhoStatusTCC.ENCERRAMENTO_DA_PARTICIPACAO, agora
        )
        encerrar_orientacoes_ativas(tcc, agora)
        pendentes = list(
            SolicitacoesOrientacao.objects.select_related("sol_doc__doc").filter(
                sol_tcc=tcc, sol_status__in=STATUS_SOLICITACAO_PENDENTE
            )
        )
        SolicitacoesOrientacao.objects.filter(pk__in=[s.pk for s in pendentes]).update(
            sol_status=StatusSolicitacao.CANCELADO, sol_data_resposta=agora
        )
        for solicitacao in pendentes:
            notificar(
                solicitacao.sol_doc.doc,
                mensagens.MT31_PEDIDO_CANCELADO.format(
                    tipo=solicitacao.sol_tipo.lower(), nome=aluno.alu.usu_nome
                ),
            )
    return tcc


def excluidos_e_transferidos(turma):
    """Exclusões e transferências que saíram desta turma, da mais recente para a mais antiga
    (research B16). Só leitura. [US-09][RBN-CAD-05.8][FR-026][I-4]
    """
    return (
        HistoricoAlunosTurmas.objects.filter(hat_tur_origem=turma)
        .select_related("hat_alu__alu", "hat_usu", "hat_tur_destino")
        .order_by("-hat_data_hora", "-hat_id")
    )
