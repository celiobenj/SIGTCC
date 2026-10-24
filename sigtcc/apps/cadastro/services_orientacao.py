"""Regras de orientação do app cadastro (spec 006; research R1): pedidos e troca de orientador,
convites e coorientadores, tela de orientandos, Apto para Defesa, Correções Conferidas, motivo do
cancelamento e histórico de orientação.

Este módulo importa `services_turmas` e `services_tcc`; `services_turmas` só o importa dentro das
funções que precisam dele (arquivamento e cópia para o TCC 2), para não haver import circular
(research R21, N6).

[US-17][US-18][US-36][US-42][US-45][RBN-CAD-10.1 a 10.7][RBN-CAD-11.4][RBN-CAD-11.5]
"""

import enum

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.http import Http404
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    GatilhoStatusTCC,
    ModalidadeTCC,
    OrigemOrientacao,
    StatusCoorientacao,
    StatusOrientacao,
    StatusSolicitacao,
    StatusTCC,
    TipoEntrega,
    TipoSolicitacao,
)
from sigtcc.apps.cadastro.models import (
    Alunos,
    Coorientacoes,
    Docentes,
    EntregasMarcos,
    HistoricoStatusTCC,
    Notificacoes,
    Orientacoes,
    SolicitacoesOrientacao,
    TCCs,
    TurmasMarcos,
)
from sigtcc.apps.cadastro.services import enviar_email_apos_commit, notificar
from sigtcc.apps.cadastro.services_contas import docentes_ativos, travar_e_conferir_ativo
from sigtcc.apps.cadastro.services_entregas import (
    STATUS_ENVIO_AVALIAVEL,
    exige_correcoes_conferidas,
    status_exibido,
    versao_final_do_aluno,
)
from sigtcc.apps.cadastro.services_turmas import (
    STATUS_SESSAO_ATIVA,
    STATUS_SOLICITACAO_PENDENTE,
    participacao_encerrada,
    travar_turma_ativa,
    turma_arquivada,
    turma_tem_orientador_automatico,
    vinculo_na_turma,
)
from sigtcc.apps.defesa.choices import EventoDefesa
from sigtcc.apps.defesa.models import Defesas, HistoricoDefesas

# Tipos de solicitação que são pedidos (rota 12); o convite é a Coorientação (rota 13).
TIPOS_PEDIDO = (TipoSolicitacao.ORIENTACAO, TipoSolicitacao.TROCA_DE_ORIENTACAO)

# Papéis por vínculo ativo (research R10; contrato §1).
ALUNO = "aluno"
ORIENTADOR = "orientador"
COORIENTADOR = "coorientador"
PROFESSOR = "professor"


# =============================================================================================
# Vínculo e papéis (research R10; contrato §1 e §2)
# =============================================================================================


def orientador_atual(tcc):
    """Docente do vínculo 'Ativa' em Orientacoes (no máximo um), ou None.

    [US-18][RBN-CAD-10.2][FR-047][contrato §1]
    """
    orientacao = (
        Orientacoes.objects.select_related("ori_doc__doc")
        .filter(ori_tcc=tcc, ori_status=StatusOrientacao.ATIVA)
        .first()
    )
    return orientacao.ori_doc if orientacao else None


def coorientadores_ativos(tcc):
    """Coorientações 'Ativa' do TCC (docentes do NUCOMP e externos); o convite pendente não
    entra, porque não conta como coorientação (RBN-CAD-10.4).
    [US-36][US-45][RBN-CAD-10.3][RBN-CAD-10.4][contrato §1]
    """
    return list(
        Coorientacoes.objects.select_related("coo_doc__doc", "coo_cext")
        .filter(coo_tcc=tcc, coo_status=StatusCoorientacao.ATIVA)
        .order_by("coo_data_inicio", "coo_id")
    )


def e_orientador_atual(usuario, tcc):
    """O usuário é o Orientador do vínculo ativo (pedido aceito ou automático). [FR-015][Q10]"""
    return Orientacoes.objects.filter(
        ori_tcc=tcc, ori_doc_id=usuario.pk, ori_status=StatusOrientacao.ATIVA
    ).exists()


def e_coorientador_ativo(usuario, tcc):
    """O usuário é docente do NUCOMP com coorientação aceita e ativa. [FR-015][FR-025][Q10]"""
    return Coorientacoes.objects.filter(
        coo_tcc=tcc, coo_doc_id=usuario.pk, coo_status=StatusCoorientacao.ATIVA
    ).exists()


def papeis_no_tcc(usuario, tcc):
    """Todos os papéis do usuário no TCC, só por vínculo ativo (Q10): "aluno", "orientador",
    "coorientador" e "professor"; conjunto vazio sem vínculo. O Professor da Disciplina de turma
    com orientador automático tem {"professor", "orientador"} (research R10, A4).
    [US-18][US-19][US-36][RBN-CAD-10.4][RBN-CAD-11.2][FR-023][Q10][contrato §1]
    """
    papeis = set()
    if tcc.tcc_alu_id == usuario.pk:
        papeis.add(ALUNO)
    if e_orientador_atual(usuario, tcc):
        papeis.add(ORIENTADOR)
    if e_coorientador_ativo(usuario, tcc):
        papeis.add(COORIENTADOR)
    if tcc.tcc_tur.tur_doc_id == usuario.pk:
        papeis.add(PROFESSOR)
    return papeis


def tcc_copiado(tcc):
    """TCC 1 'Aprovado para TCC 2' já copiado para um TCC 2 (Q6): existe um TCC mais novo do
    mesmo aluno criado pelo gatilho "Transferência para TCC 2" (research R6).
    [US-08][RBN-CAD-08.6][FR-007][FR-051][Q6][contrato §2]
    """
    if tcc.tcc_status != StatusTCC.APROVADO_PARA_TCC_2:
        return False
    return HistoricoStatusTCC.objects.filter(
        hst_tcc__tcc_alu_id=tcc.tcc_alu_id,
        hst_tcc_id__gt=tcc.pk,
        hst_gatilho=GatilhoStatusTCC.TRANSFERENCIA_PARA_TCC_2,
    ).exists()


def tcc_de_origem(tcc2):
    """O TCC 1 de onde o TCC 2 foi copiado, ou None (research R6; FR-023).

    [US-19][RBN-CAD-08.6][FR-023][Q6]
    """
    if not HistoricoStatusTCC.objects.filter(
        hst_tcc=tcc2, hst_gatilho=GatilhoStatusTCC.TRANSFERENCIA_PARA_TCC_2
    ).exists():
        return None
    return (
        TCCs.objects.select_related("tcc_tur")
        .filter(
            tcc_alu_id=tcc2.tcc_alu_id,
            tcc_status=StatusTCC.APROVADO_PARA_TCC_2,
            pk__lt=tcc2.pk,
        )
        .order_by("-pk")
        .first()
    )


def pode_alterar_no_tcc(tcc):
    """Turma não arquivada, participação não encerrada e TCC não copiado (FR-007, FR-046).

    [US-17][US-19][US-45][US-46][RBN-CAD-04.5][RBN-CAD-08.5][FR-007][FR-046][contrato §2]
    """
    return not (turma_arquivada(tcc.tcc_tur) or participacao_encerrada(tcc) or tcc_copiado(tcc))


def link_da_solicitacao(sol):
    """Único lugar que monta o link de um pedido (rota 12) ou convite (rota 13): usado pelas
    notificações MO-01, MO-07, MO-16 e MO-26 e pela dedução do motivo TURMA_ARQUIVADA
    (research R3, N3; contrato §5).
    [US-17][US-18][US-36][FR-012][FR-033][FR-050][FR-052]
    """
    rota = (
        "cadastro:pedido_orientacao"
        if sol.sol_tipo in TIPOS_PEDIDO
        else "cadastro:convite_coorientacao"
    )
    return reverse(rota, args=[sol.pk])


# =============================================================================================
# Motivo do cancelamento, sem coluna nova (FR-050; research R3; contrato §5)
# =============================================================================================


class MotivoCancelamento(enum.Enum):
    """Motivo deduzido de um pedido ou convite 'Cancelado' (não é tabela nem coluna; Q7).

    [US-18][US-36][RBN-CAD-10.6][FR-050][Q7][Q17]
    """

    AGENDAMENTO = "agendamento"
    ENCERRAMENTO = "encerramento"
    DOCENTE_VIROU_ORIENTADOR = "docente_virou_orientador"
    COPIA_TCC_2 = "copia_tcc_2"
    TURMA_ARQUIVADA = "turma_arquivada"
    ALUNO = "aluno"


def motivo_do_cancelamento(sol):
    """Motivo pela igualdade exata entre `sol_data_resposta` e o instante do evento que causou o
    cancelamento, com as consultas fixas do research R3, na ordem do FR-050; sem igualdade, o
    aluno cancelou. O evento grava o mesmo objeto `datetime` nas duas linhas (contrato §5).
    [US-18][US-36][RBN-CAD-10.6][FR-050][Q7][Q17][research R3]
    """
    instante = sol.sol_data_resposta
    tcc = sol.sol_tcc
    if instante is None:
        return MotivoCancelamento.ALUNO
    if (
        sol.sol_tipo == TipoSolicitacao.TROCA_DE_ORIENTACAO
        and HistoricoDefesas.objects.filter(
            hdf_def__def_tcc=tcc, hdf_evento=EventoDefesa.AGENDAMENTO, hdf_data_hora=instante
        ).exists()
    ):
        return MotivoCancelamento.AGENDAMENTO
    if HistoricoStatusTCC.objects.filter(
        hst_tcc=tcc,
        hst_gatilho=GatilhoStatusTCC.ENCERRAMENTO_DA_PARTICIPACAO,
        hst_data_hora=instante,
    ).exists():
        return MotivoCancelamento.ENCERRAMENTO
    if (
        sol.sol_tipo == TipoSolicitacao.COORIENTACAO
        and Orientacoes.objects.filter(
            ori_tcc=tcc, ori_doc_id=sol.sol_doc_id, ori_data_inicio=instante
        ).exists()
    ):
        return MotivoCancelamento.DOCENTE_VIROU_ORIENTADOR
    if (
        HistoricoStatusTCC.objects.filter(
            hst_tcc__tcc_alu_id=tcc.tcc_alu_id,
            hst_gatilho=GatilhoStatusTCC.TRANSFERENCIA_PARA_TCC_2,
            hst_data_hora=instante,
        )
        .exclude(hst_tcc=tcc)
        .exists()
    ):
        return MotivoCancelamento.COPIA_TCC_2
    if Notificacoes.objects.filter(
        not_usu_id=sol.sol_doc_id, not_link_tela=link_da_solicitacao(sol), not_data_hora=instante
    ).exists():
        return MotivoCancelamento.TURMA_ARQUIVADA
    return MotivoCancelamento.ALUNO


# Texto do link por motivo: (pedido, convite). [FR-012][FR-033]
_TEXTOS_CANCELAMENTO = {
    MotivoCancelamento.AGENDAMENTO: (mensagens.PEDIDO_CANCELADO_AGENDAMENTO, None),
    MotivoCancelamento.ENCERRAMENTO: (
        mensagens.MO12_PEDIDO_CANCELADO_ENCERRAMENTO,
        mensagens.MO12_CONVITE_CANCELADO_ENCERRAMENTO,
    ),
    MotivoCancelamento.DOCENTE_VIROU_ORIENTADOR: (
        None,
        mensagens.MO17_CONVITE_CANCELADO_ORIENTADOR,
    ),
    MotivoCancelamento.COPIA_TCC_2: (
        mensagens.MO18_PEDIDO_CANCELADO_COPIA,
        mensagens.MO18_CONVITE_CANCELADO_COPIA,
    ),
    MotivoCancelamento.TURMA_ARQUIVADA: (
        mensagens.MO26_PEDIDO_CANCELADO_ARQUIVAMENTO,
        mensagens.MO26_CONVITE_CANCELADO_ARQUIVAMENTO,
    ),
    MotivoCancelamento.ALUNO: (
        mensagens.PEDIDO_CANCELADO_PELO_ALUNO,
        mensagens.CONVITE_CANCELADO_PELO_ALUNO,
    ),
}


def texto_do_cancelamento(sol):
    """Texto do aviso de estado do link de um pedido ou convite cancelado (FR-012, FR-033).

    [US-18][US-36][FR-012][FR-033][FR-050]
    """
    pedido, convite = _TEXTOS_CANCELAMENTO[motivo_do_cancelamento(sol)]
    texto = convite if sol.sol_tipo == TipoSolicitacao.COORIENTACAO else pedido
    return texto or mensagens.PEDIDO_CANCELADO_PELO_ALUNO


def _tipo_para_aviso(sol):
    """{tipo} da MO-18 e da MO-26: "pedido de orientação" ou "convite de coorientação"."""
    if sol.sol_tipo == TipoSolicitacao.COORIENTACAO:
        return mensagens.TIPO_CONVITE_COORIENTACAO
    return mensagens.TIPO_PEDIDO_ORIENTACAO


def cancelar_pendentes_da_turma(turma, agora):
    """Arquivamento da turma (IC-12; FR-053): pedidos e convites pendentes dos TCCs da turma →
    'Cancelado' com `agora`, e a MO-26 ao docente de cada um, gravada com o mesmo `agora` e o link
    da solicitação (é o que deduz o motivo TURMA_ARQUIVADA). Chamada só por
    `services_turmas.arquivar_turma`, com turma, alunos e TCCs já travados.
    [US-07][RBN-CAD-04.5][FR-050][FR-053][Q17][IC-12][contrato §5]
    """
    pendentes = list(
        SolicitacoesOrientacao.objects.select_related("sol_doc__doc", "sol_tcc__tcc_alu__alu")
        .filter(sol_tcc__tcc_tur=turma, sol_status__in=STATUS_SOLICITACAO_PENDENTE)
        .order_by("sol_id")
    )
    SolicitacoesOrientacao.objects.filter(pk__in=[s.pk for s in pendentes]).update(
        sol_status=StatusSolicitacao.CANCELADO, sol_data_resposta=agora
    )
    for sol in pendentes:
        notificar(
            sol.sol_doc.doc,
            mensagens.MO26_NOTIFICACAO.format(
                tipo=_tipo_para_aviso(sol),
                nome=sol.sol_tcc.tcc_alu.alu.usu_nome,
                identificador=turma.tur_identificador,
            ),
            link=link_da_solicitacao(sol),
            agora=agora,
        )
    return pendentes


def cancelar_troca_no_agendamento(tcc, agora):
    """Obrigatória na confirmação do agendamento (US-24), na mesma transação, com turma → aluno →
    TCC já travados por quem chama (contrato §3). `agora` MUST ser o mesmo valor gravado em
    `Historico_Defesas.hdf_data_hora` do evento 'Agendamento' (FR-050). Cancela o pedido de Troca
    de Orientação pendente, mantém o orientador atual e avisa o Aluno e o docente (MO-06); sem
    pedido pendente, devolve None.
    [US-17][US-18][RBN-CAD-10.6][FR-008][FR-050][contrato §3]
    """
    troca = (
        SolicitacoesOrientacao.objects.select_related("sol_doc__doc", "sol_tcc__tcc_alu__alu")
        .filter(
            sol_tcc=tcc,
            sol_tipo=TipoSolicitacao.TROCA_DE_ORIENTACAO,
            sol_status=StatusSolicitacao.AGUARDANDO_RESPOSTA,
        )
        .first()
    )
    if troca is None:
        return None
    troca.sol_status = StatusSolicitacao.CANCELADO
    troca.sol_data_resposta = agora
    troca.save(update_fields=["sol_status", "sol_data_resposta"])
    aluno = tcc.tcc_alu.alu
    notificar(aluno, mensagens.MO06_TROCA_CANCELADA_ALUNO, link=link_secao(tcc, "orientacao"))
    notificar(
        troca.sol_doc.doc,
        mensagens.MO06_TROCA_CANCELADA_DOCENTE.format(nome=aluno.usu_nome),
        link=reverse("cadastro:orientacoes"),
    )
    return troca


def link_secao(tcc, secao):
    """Link da aba Meu TCC do aluno já na seção (research R12; FR-052). [FR-042][FR-052]"""
    return f"{reverse('cadastro:meu_tcc', args=[tcc.tcc_tur_id])}?secao={secao}"


# =============================================================================================
# Seção Orientação do Aluno: pedido, cancelamento e troca (US-17; FR-001 a FR-008, FR-049)
# =============================================================================================

# Status em que o Aluno indica orientador (com ou sem Proposta) e em que pede a troca.
# [US-17][RBN-CAD-10.1][RBN-CAD-10.6][FR-001][FR-005]
STATUS_INDICA_ORIENTADOR = (
    StatusTCC.SEM_PROPOSTA,
    StatusTCC.EM_ANDAMENTO,
    StatusTCC.APTO_PARA_DEFESA,
)
STATUS_TROCA_ORIENTADOR = (StatusTCC.EM_ANDAMENTO, StatusTCC.APTO_PARA_DEFESA)


class ErroOrientacao(Exception):
    """Ação recusada com uma mensagem para o usuário (a view mostra e volta à tela).

    [US-17][US-18][US-36][US-45]
    """

    def __init__(self, mensagem):
        """Guarda a mensagem exibida. [FR-048]"""
        super().__init__(mensagem)
        self.mensagem = mensagem


def pedido_pendente(tcc):
    """Pedido de Orientação ou de Troca 'Aguardando Resposta' do TCC (um por TCC), ou None.

    [US-17][RBN-CAD-10.1][FR-047]
    """
    return (
        SolicitacoesOrientacao.objects.select_related("sol_doc__doc")
        .filter(
            sol_tcc=tcc, sol_tipo__in=TIPOS_PEDIDO, sol_status=StatusSolicitacao.AGUARDANDO_RESPOSTA
        )
        .first()
    )


def sessao_de_defesa_ativa(tcc):
    """Sessão Agendada, Reagendada ou Em Andamento (bloqueia troca e Substituir/Remover).

    [US-17][US-45][RBN-CAD-10.6][RBN-CAD-10.7][FR-005][FR-030]
    """
    return Defesas.objects.filter(def_tcc=tcc, def_status__in=STATUS_SESSAO_ATIVA).exists()


def rotulo_docente(docente):
    """ "Nome — titulação · curso", como no protótipo de 17/10 (FR-002). [US-17][FR-002]"""
    return f"{docente.doc.usu_nome} — {docente.doc_titulacao} · {docente.doc_cur.cur_nome}"


def docentes_para_orientacao(excluir=None):
    """Docentes com a conta 'Ativa', de qualquer curso do NUCOMP, por nome, sem o orientador
    atual na troca (FR-002, FR-005). [US-17][RBN-CAD-10.1][FR-002][FR-005][Q-68]
    """
    docentes = docentes_ativos().select_related("doc", "doc_cur").order_by("doc__usu_nome")
    if excluir is not None:
        docentes = docentes.exclude(pk=excluir.pk)
    return list(docentes)


def historico_de_orientacao(tcc):
    """Histórico de orientação (FR-049): orientadores e coorientadores anteriores (origem, datas
    e estado) e os pedidos e convites recusados ou cancelados, do mais recente ao mais antigo.
    [US-17 D][US-18 E][US-36 C][RAN-CAD-10 NFR][FR-049][D2]
    """
    linhas = []
    for ori in Orientacoes.objects.select_related("ori_doc__doc").filter(
        ori_tcc=tcc, ori_status=StatusOrientacao.ENCERRADA
    ):
        linhas.append(
            {
                "data": ori.ori_data_fim or ori.ori_data_inicio,
                "descricao": f"Orientador: {ori.ori_doc.doc.usu_nome}",
                "detalhe": f"{ori.ori_origem} · {ori.ori_status}",
                "inicio": ori.ori_data_inicio,
                "fim": ori.ori_data_fim,
            }
        )
    for coo in (
        Coorientacoes.objects.select_related("coo_doc__doc", "coo_cext")
        .filter(coo_tcc=tcc)
        .exclude(coo_status=StatusCoorientacao.ATIVA)
    ):
        linhas.append(
            {
                "data": coo.coo_data_fim or coo.coo_data_inicio,
                "descricao": f"Coorientador: {nome_do_coorientador(coo)}",
                "detalhe": coo.coo_status,
                "inicio": coo.coo_data_inicio,
                "fim": coo.coo_data_fim,
            }
        )
    for sol in SolicitacoesOrientacao.objects.select_related("sol_doc__doc").filter(
        sol_tcc=tcc, sol_status__in=(StatusSolicitacao.RECUSADO, StatusSolicitacao.CANCELADO)
    ):
        linhas.append(
            {
                "data": sol.sol_data_resposta or sol.sol_data_solicitacao,
                "descricao": f"{sol.sol_tipo}: {sol.sol_doc.doc.usu_nome}",
                "detalhe": sol.sol_status,
                "inicio": sol.sol_data_solicitacao,
                "fim": sol.sol_data_resposta,
            }
        )
    linhas.sort(key=lambda linha: linha["data"], reverse=True)
    return linhas


def nome_do_coorientador(coo):
    """Nome do coorientador do NUCOMP ou externo. [US-45][RBN-CAD-10.3]"""
    return coo.coo_doc.doc.usu_nome if coo.coo_doc_id else coo.coo_cext.cext_nome


def contexto_secao_orientacao(tcc, somente_leitura=False):
    """Estado da seção Orientação (aba Meu TCC e painel do aluno): orientador, pedido pendente,
    listas "Indicar orientador" e "Trocar de orientador" com o estado do botão, coorientadores e
    histórico. As decisões ficam aqui, nunca no template (constituição IV).
    [US-17][US-41][RBN-CAD-10.1][RBN-CAD-10.6][RBN-CAD-04.2][FR-001 a FR-007][FR-049]
    """
    turma = tcc.tcc_tur
    orientador = orientador_atual(tcc)
    pendente = pedido_pendente(tcc)
    automatico = turma_tem_orientador_automatico(turma)
    leitura = somente_leitura or not pode_alterar_no_tcc(tcc)
    sessao = sessao_de_defesa_ativa(tcc)
    mostra_lista = not leitura and not automatico and tcc.tcc_status in STATUS_INDICA_ORIENTADOR
    troca = orientador is not None
    lista_habilitada = mostra_lista and pendente is None
    if troca:
        lista_habilitada = (
            lista_habilitada and tcc.tcc_status in STATUS_TROCA_ORIENTADOR and not sessao
        )
    return {
        "tcc": tcc,
        "orientador": orientador,
        "pedido": pendente,
        "pedido_texto": (
            mensagens.PEDIDO_ENVIADO.format(docente=pendente.sol_doc.doc.usu_nome)
            if pendente
            else ""
        ),
        "automatico": automatico,
        "somente_leitura": leitura,
        "mostra_lista": mostra_lista,
        "troca": troca,
        "rotulo_lista": "Trocar de orientador" if troca else "Indicar orientador",
        "lista_habilitada": lista_habilitada,
        "pode_cancelar": not leitura and pendente is not None,
        "docentes": (
            [(d.pk, rotulo_docente(d)) for d in docentes_para_orientacao(orientador)]
            if mostra_lista
            else []
        ),
        "coorientadores": coorientadores_ativos(tcc),
        "historico": historico_de_orientacao(tcc),
        "sem_orientador": mensagens.SEM_ORIENTADOR,
    }


def _travar_tcc_do_aluno(usuario, tur_id):
    """Trava na ordem do research R2 (turma ativa → aluno → TCC) o TCC do próprio aluno na
    turma: TurmaArquivada com a turma arquivada; 404 sem vínculo ou sem TCC.
    [US-17][US-19][US-45][US-46][research R2]
    """
    turma = travar_turma_ativa(tur_id)
    vinculo_na_turma(turma, usuario.pk)
    Alunos.objects.select_for_update().filter(pk=usuario.pk).first()
    tcc = (
        TCCs.objects.select_for_update(of=("self",))
        .select_related("tcc_tur__tur_cur", "tcc_alu__alu")
        .filter(tcc_alu_id=usuario.pk, tcc_tur=turma)
        .first()
    )
    if tcc is None:
        raise Http404
    return turma, tcc


def _titulo_ou_aviso(tcc):
    """Título do TCC ou "Proposta ainda não registrada" (MO-01, MO-07, MO-16). [FR-003]"""
    return tcc.tcc_titulo or mensagens.PROPOSTA_AINDA_NAO_REGISTRADA


def enviar_pedido(usuario, tur_id, doc_id):
    """Envia o pedido de Orientação ou, com orientador ativo, de Troca de Orientação: trava
    turma → aluno → TCC → conta do docente (research R2), reconfere tudo, grava o pedido num
    savepoint (o índice de um pedido pendente por TCC vira o tratamento do duplo clique) e avisa
    o docente no sistema (MO-01 ou MO-16) e por e-mail depois do commit.
    Ação cujo botão a tela esconde → 404; pedido já pendente → devolve o existente.
    [US-17][RBN-CAD-10.1][RBN-CAD-10.6][FR-002][FR-003][FR-005][FR-047][Q-68]
    """
    with transaction.atomic():
        turma, tcc = _travar_tcc_do_aluno(usuario, tur_id)
        if (
            not pode_alterar_no_tcc(tcc)
            or turma_tem_orientador_automatico(turma)
            or tcc.tcc_status not in STATUS_INDICA_ORIENTADOR
        ):
            raise Http404
        existente = pedido_pendente(tcc)
        if existente is not None:
            return existente
        orientador = orientador_atual(tcc)
        tipo = TipoSolicitacao.ORIENTACAO
        if orientador is not None:
            if tcc.tcc_status not in STATUS_TROCA_ORIENTADOR or sessao_de_defesa_ativa(tcc):
                raise Http404
            tipo = TipoSolicitacao.TROCA_DE_ORIENTACAO
        docente = Docentes.objects.select_related("doc", "doc_cur").filter(pk=doc_id).first()
        if docente is None or (orientador is not None and docente.pk == orientador.pk):
            raise Http404
        # Q-68: a lista só traz contas 'Ativa'; inativada no meio, como um docente fora da lista.
        if not travar_e_conferir_ativo(docente.doc):
            raise Http404
        try:
            with transaction.atomic():
                pedido = SolicitacoesOrientacao.objects.create(
                    sol_tcc=tcc,
                    sol_doc=docente,
                    sol_tipo=tipo,
                    sol_status=StatusSolicitacao.AGUARDANDO_RESPOSTA,
                    sol_data_solicitacao=timezone.now(),
                )
        except IntegrityError:
            return pedido_pendente(tcc)
        nome = usuario.usu_nome
        if tipo == TipoSolicitacao.TROCA_DE_ORIENTACAO:
            texto = mensagens.MO16_PEDIDO_TROCA.format(
                nome=nome, titulo=_titulo_ou_aviso(tcc), orientador=orientador.doc.usu_nome
            )
            assunto, template = mensagens.MO16_ASSUNTO, "cadastro/emails/pedido_troca.txt"
        else:
            texto = mensagens.MO01_PEDIDO_ORIENTACAO.format(nome=nome, titulo=_titulo_ou_aviso(tcc))
            assunto, template = mensagens.MO01_ASSUNTO, "cadastro/emails/pedido_orientacao.txt"
        link = link_da_solicitacao(pedido)
        notificar(docente.doc, texto, link=link)
        enviar_email_apos_commit(
            docente.doc, assunto, template, {"texto": texto, "link": settings.SITE_URL + link}
        )
    return pedido


def cancelar_pedido(usuario, tur_id):
    """ "Cancelar Pedido" do Aluno (FR-004): o pedido pendente vira 'Cancelado' com a data e a hora
    (motivo ALUNO, FR-050) e a lista volta a ficar disponível. Sem pedido pendente, nada muda.
    [US-17][RBN-CAD-10.1][FR-004][FR-050]
    """
    with transaction.atomic():
        _, tcc = _travar_tcc_do_aluno(usuario, tur_id)
        if not pode_alterar_no_tcc(tcc):
            raise Http404
        pedido = (
            SolicitacoesOrientacao.objects.select_for_update()
            .filter(
                sol_tcc=tcc,
                sol_tipo__in=TIPOS_PEDIDO,
                sol_status=StatusSolicitacao.AGUARDANDO_RESPOSTA,
            )
            .first()
        )
        if pedido is None:
            return None
        pedido.sol_status = StatusSolicitacao.CANCELADO
        pedido.sol_data_resposta = timezone.now()
        pedido.save(update_fields=["sol_status", "sol_data_resposta"])
    return pedido


# =============================================================================================
# Tela Orientações do docente: pedidos, convites e orientandos (US-18, US-36; FR-009 a FR-016,
# FR-026, FR-031 a FR-033; research R4, R14 a R16)
# =============================================================================================


class SolicitacaoRespondida(Exception):
    """A solicitação já não está pendente (respondida ou cancelada ao mesmo tempo): a view volta
    à página do link, que mostra o estado atual (FR-012). [US-18][US-36][FR-012][FR-033]
    """

    def __init__(self, sol):
        """Guarda a solicitação, para a view montar o link. [FR-012]"""
        super().__init__(sol.pk)
        self.sol = sol


def pedidos_pendentes(docente):
    """Pedidos de Orientação e de Troca 'Aguardando Resposta' feitos ao docente (FR-009), com
    aluno, título ou aviso, turma, data e hora e orientador atual (só na troca).
    [US-18][RBN-CAD-10.2][FR-009]
    """
    linhas = []
    for sol in (
        SolicitacoesOrientacao.objects.select_related("sol_tcc__tcc_alu__alu", "sol_tcc__tcc_tur")
        .filter(
            sol_doc_id=docente.pk,
            sol_tipo__in=TIPOS_PEDIDO,
            sol_status=StatusSolicitacao.AGUARDANDO_RESPOSTA,
        )
        .order_by("sol_data_solicitacao", "sol_id")
    ):
        tcc = sol.sol_tcc
        atual = (
            orientador_atual(tcc) if sol.sol_tipo == TipoSolicitacao.TROCA_DE_ORIENTACAO else None
        )
        linhas.append(
            {
                "sol": sol,
                "aluno": tcc.tcc_alu.alu.usu_nome,
                "titulo": _titulo_ou_aviso(tcc),
                "turma": tcc.tcc_tur,
                "orientador_atual": atual.doc.usu_nome if atual else "",
                "tem_proposta": tcc.tcc_status != StatusTCC.SEM_PROPOSTA,
            }
        )
    return linhas


def convites_pendentes(docente):
    """Convites de coorientação 'Aguardando Aceite' feitos ao docente (FR-031): aluno, título,
    turma e Orientador. [US-36][RBN-CAD-10.4][FR-031]
    """
    linhas = []
    for sol in (
        SolicitacoesOrientacao.objects.select_related("sol_tcc__tcc_alu__alu", "sol_tcc__tcc_tur")
        .filter(
            sol_doc_id=docente.pk,
            sol_tipo=TipoSolicitacao.COORIENTACAO,
            sol_status=StatusSolicitacao.AGUARDANDO_ACEITE,
        )
        .order_by("sol_data_solicitacao", "sol_id")
    ):
        tcc = sol.sol_tcc
        orientador = orientador_atual(tcc)
        linhas.append(
            {
                "sol": sol,
                "aluno": tcc.tcc_alu.alu.usu_nome,
                "titulo": _titulo_ou_aviso(tcc),
                "turma": tcc.tcc_tur,
                "orientador": orientador.doc.usu_nome if orientador else "",
            }
        )
    return linhas


def estado_apto(tcc, entregas, n_palavras, turma_tem_documento=None):
    """Estado do botão "Apto para Defesa" (FR-026): None (não aparece: Status diferente de "Em
    Andamento"), "sem_entrega_cadastrada" (indisponível, com o texto da US-42 E3),
    "indisponivel" ou "disponivel". `entregas` são os registros do aluno na turma (com o
    marco); `n_palavras` é a quantidade de Palavras-Chave; `turma_tem_documento`, quando
    informado, evita a consulta por linha (research R14).
    [US-42][RBN-CAD-11.5][FR-026][research R16]
    """
    if tcc.tcc_status != StatusTCC.EM_ANDAMENTO:
        return None
    documento = [e for e in entregas if e.ent_tma.tma_tipo == TipoEntrega.DOCUMENTO_PARA_DEFESA]
    if turma_tem_documento is None:
        turma_tem_documento = _turma_tem_documento(tcc.tcc_tur_id)
    if not documento and not turma_tem_documento:
        return "sem_entrega_cadastrada"
    entregue = any(e.ent_status in STATUS_ENVIO_AVALIAVEL for e in documento)
    if entregue and tcc.tcc_ari_id and n_palavras:
        return "disponivel"
    return "indisponivel"


def _turma_tem_documento(tur_id):
    """A turma tem a entrega do tipo Documento para Defesa cadastrada. [US-42 E3][FR-026]"""
    return TurmasMarcos.objects.filter(
        tma_tur_id=tur_id, tma_tipo=TipoEntrega.DOCUMENTO_PARA_DEFESA
    ).exists()


def estado_correcoes(tcc, entregas):
    """Estado de "Correções Conferidas" (FR-016): None (não aparece), "disponivel" (botão) ou a
    data e hora da conferência (etiqueta MO-13). Só em TCC 2 de Sistemas de Informação com
    "Aprovado com Correções", depois do envio da Versão Final. [US-44 B][RBN-CAD-09.5][FR-016][Q2]
    """
    turma = tcc.tcc_tur
    if turma.tur_descricao != DescricaoTurma.TCC_2 or not exige_correcoes_conferidas(turma, tcc):
        return None
    versao = [e for e in entregas if e.ent_tma.tma_tipo == TipoEntrega.VERSAO_FINAL]
    if not versao:
        return None
    entrega = versao[0]
    if entrega.ent_correcoes_conferidas_em is not None:
        return entrega.ent_correcoes_conferidas_em
    if entrega.ent_status in STATUS_ENVIO_AVALIAVEL:
        return "disponivel"
    return None


def orientandos(docente):
    """Tela de orientandos (FR-014, FR-015): trabalhos com vínculo ativo do docente como
    Orientador (pedido ou automático) ou Coorientador; turma arquivada no fim (US-18 G), depois
    pelo nome do aluno. Sem consulta por linha (research R14): contagens anotadas e entregas
    carregadas de uma vez. Cada linha traz as decisões dos botões prontas.
    [US-18][US-36][US-19][US-42][US-46][RBN-CAD-11.4][FR-014][FR-015][FR-016][FR-026][Q10]
    """
    como_orientador = set(
        Orientacoes.objects.filter(
            ori_doc_id=docente.pk, ori_status=StatusOrientacao.ATIVA
        ).values_list("ori_tcc_id", flat=True)
    )
    como_coorientador = set(
        Coorientacoes.objects.filter(
            coo_doc_id=docente.pk, coo_status=StatusCoorientacao.ATIVA
        ).values_list("coo_tcc_id", flat=True)
    )
    tccs = list(
        TCCs.objects.select_related("tcc_alu__alu", "tcc_tur__tur_cur")
        .filter(pk__in=como_orientador | como_coorientador)
        .annotate(
            n_atas=Count("encontroorientacao", distinct=True),
            n_palavras=Count("palavraschavetcc__pal_palavra", distinct=True),
        )
    )
    registros = {}
    for entrega in (
        EntregasMarcos.objects.select_related("ent_tma")
        .filter(
            ent_alu_id__in=[t.tcc_alu_id for t in tccs],
            ent_tma__tma_tur_id__in=[t.tcc_tur_id for t in tccs],
        )
        .order_by("ent_tma__tma_data_limite", "ent_tma_id")
    ):
        registros.setdefault((entrega.ent_alu_id, entrega.ent_tma.tma_tur_id), []).append(entrega)
    com_documento = set(
        TurmasMarcos.objects.filter(
            tma_tur_id__in=[t.tcc_tur_id for t in tccs],
            tma_tipo=TipoEntrega.DOCUMENTO_PARA_DEFESA,
        ).values_list("tma_tur_id", flat=True)
    )
    agora = timezone.now()
    linhas = []
    for tcc in tccs:
        turma = tcc.tcc_tur
        entregas = registros.get((tcc.tcc_alu_id, turma.pk), [])
        arquivada = turma_arquivada(turma)
        orientador = tcc.pk in como_orientador
        alteravel = not arquivada and pode_alterar_no_tcc(tcc)
        apto = None
        if orientador and not arquivada:
            apto = estado_apto(tcc, entregas, tcc.n_palavras, turma.pk in com_documento)
        correcoes = estado_correcoes(tcc, entregas) if orientador and not arquivada else None
        etiqueta = ""
        if correcoes not in (None, "disponivel"):
            etiqueta = mensagens.MO13_ETIQUETA.format(
                data_hora=(
                    timezone.localtime(correcoes).strftime("%d/%m/%Y %H:%M")
                    if timezone.is_aware(correcoes)
                    else correcoes.strftime("%d/%m/%Y %H:%M")
                )
            )
            correcoes = None
        linhas.append(
            {
                "tcc": tcc,
                "aluno": tcc.tcc_alu.alu.usu_nome,
                "curso": turma.tur_cur.cur_nome,
                "turma": turma,
                "titulo": tcc.tcc_titulo or "",
                "papel": "Orientador" if orientador else "Coorientador",
                "orientador": orientador,
                "arquivada": arquivada,
                "entregas": [(e.ent_tma.tma_titulo, status_exibido(e, agora)) for e in entregas],
                "n_atas": tcc.n_atas,
                "pode_registrar_ata": alteravel,
                "pode_historico": orientador and not arquivada,
                "pode_publicacao": orientador
                and not arquivada
                and tcc.tcc_modalidade == ModalidadeTCC.ARTIGO_CIENTIFICO,
                "apto": apto,
                "apto_etiqueta": orientador and tcc.tcc_status == StatusTCC.APTO_PARA_DEFESA,
                "correcoes": correcoes,
                "correcoes_etiqueta": etiqueta,
            }
        )
    linhas.sort(key=lambda linha: (linha["arquivada"], linha["aluno"]))
    return linhas


def contexto_orientacoes(docente):
    """Contexto da tela Orientações: as três seções e os avisos de seção vazia (MO-24).

    [US-18][US-36][FR-009][FR-014][FR-031][FR-040][Q11]
    """
    return {
        "pedidos": pedidos_pendentes(docente),
        "convites": convites_pendentes(docente),
        "orientandos": orientandos(docente),
        "sem_pedidos": mensagens.MO24_SEM_PEDIDOS,
        "sem_convites": mensagens.MO24_SEM_CONVITES,
        "sem_orientandos": mensagens.MO24_SEM_ORIENTANDOS,
        "texto_sem_entrega": mensagens.ENTREGA_DOCUMENTO_NAO_CADASTRADA,
    }


def estado_da_solicitacao(docente, sol_id, tipos):
    """Aviso de estado da página do link de pedido (rota 12) ou convite (rota 13), na ordem do
    research R4: inexistente, de outro tipo ou de outro docente dão a mesma resposta ("não está
    disponível para o seu usuário"), sem revelar existência nem estado; ao docente indicado,
    o destaque do pendente, a decisão com data e hora ou o motivo do cancelamento.
    [US-18][US-36][RBN-CAD-10.1][RBN-CAD-10.4][FR-012][FR-033][research R4]
    """
    convite = TipoSolicitacao.COORIENTACAO in tipos
    sol = (
        SolicitacoesOrientacao.objects.select_related("sol_tcc__tcc_tur", "sol_tcc__tcc_alu__alu")
        .filter(pk=sol_id, sol_tipo__in=tipos)
        .first()
    )
    if sol is None or sol.sol_doc_id != docente.pk:
        texto = mensagens.CONVITE_NAO_DISPONIVEL if convite else mensagens.PEDIDO_NAO_DISPONIVEL
        return {"aviso": texto, "destaque": None}
    if sol.sol_status in STATUS_SOLICITACAO_PENDENTE:
        return {"aviso": "", "destaque": sol.pk}
    if sol.sol_status == StatusSolicitacao.CANCELADO:
        return {"aviso": texto_do_cancelamento(sol), "destaque": None}
    return {"aviso": sol.sol_status, "aviso_data": sol.sol_data_resposta, "destaque": None}


def _travar_para_resposta(docente, sol_id):
    """Trava na ordem do research R2 (turma ativa → aluno → TCC → conta do docente →
    solicitação) para responder: 404 se a solicitação não é do docente ou se o TCC mudou de
    turma no meio; TurmaArquivada com a turma arquivada; SolicitacaoRespondida se já não está
    pendente. [US-18][US-36][FR-010][FR-011][FR-032][research R2][N14]
    """
    achada = (
        SolicitacoesOrientacao.objects.select_related("sol_tcc")
        .filter(pk=sol_id, sol_doc_id=docente.pk)
        .first()
    )
    if achada is None:
        raise Http404
    turma = travar_turma_ativa(achada.sol_tcc.tcc_tur_id)
    Alunos.objects.select_for_update().filter(pk=achada.sol_tcc.tcc_alu_id).first()
    tcc = (
        TCCs.objects.select_for_update(of=("self",))
        .select_related("tcc_tur__tur_cur", "tcc_tur__tur_doc__doc", "tcc_alu__alu")
        .get(pk=achada.sol_tcc_id)
    )
    if tcc.tcc_tur_id != turma.pk:
        raise Http404
    if not travar_e_conferir_ativo(docente):
        raise Http404
    sol = SolicitacoesOrientacao.objects.select_for_update().get(pk=achada.pk)
    if sol.sol_status not in STATUS_SOLICITACAO_PENDENTE:
        raise SolicitacaoRespondida(sol)
    if not pode_alterar_no_tcc(tcc):
        raise Http404
    return tcc, sol


def aceitar_solicitacao(docente, sol_id):
    """ "Aceitar" um pedido (FR-010) ou convite (FR-032), com autor, data e hora. Devolve a
    mensagem da tela (MO-15 ou "Convite aceito").
    - Pedido de Orientação: vínculo 'Ativa' "Pedido Aceito"; MO-02 ao Aluno e MO-04 (sistema e
      e-mail) ao Professor da Disciplina.
    - Troca: encerra o vínculo anterior (MO-05 ao orientador anterior), encerra a coorientação de
      quem aceita e cancela o convite pendente a ele com o mesmo instante (MO-17 pelo link; D13);
      recusada com sessão de defesa ativa (A20).
    - Convite: coorientação 'Ativa'; MO-10 ao Aluno e ao Orientador.
    [US-18][US-36][US-17 D][RBN-CAD-10.2][RBN-CAD-10.4][RBN-CAD-10.6][FR-010][FR-032][FR-050]
    """
    with transaction.atomic():
        tcc, sol = _travar_para_resposta(docente, sol_id)
        agora = timezone.now()
        aluno = tcc.tcc_alu.alu
        if sol.sol_tipo == TipoSolicitacao.COORIENTACAO:
            return _aceitar_convite(docente, tcc, sol, aluno, agora)
        anterior = orientador_atual(tcc)
        if sol.sol_tipo == TipoSolicitacao.TROCA_DE_ORIENTACAO:
            if anterior is None or anterior.pk == docente.pk or sessao_de_defesa_ativa(tcc):
                raise Http404
            Orientacoes.objects.filter(ori_tcc=tcc, ori_status=StatusOrientacao.ATIVA).update(
                ori_status=StatusOrientacao.ENCERRADA, ori_data_fim=agora
            )
            Coorientacoes.objects.filter(
                coo_tcc=tcc, coo_doc_id=docente.pk, coo_status=StatusCoorientacao.ATIVA
            ).update(coo_status=StatusCoorientacao.ENCERRADA, coo_data_fim=agora)
            SolicitacoesOrientacao.objects.filter(
                sol_tcc=tcc,
                sol_doc_id=docente.pk,
                sol_tipo=TipoSolicitacao.COORIENTACAO,
                sol_status=StatusSolicitacao.AGUARDANDO_ACEITE,
            ).update(sol_status=StatusSolicitacao.CANCELADO, sol_data_resposta=agora)
        elif anterior is not None:
            raise Http404
        try:
            with transaction.atomic():
                Orientacoes.objects.create(
                    ori_tcc=tcc,
                    ori_doc_id=docente.pk,
                    ori_origem=OrigemOrientacao.PEDIDO_ACEITO,
                    ori_status=StatusOrientacao.ATIVA,
                    ori_data_inicio=agora,
                )
        except IntegrityError:
            raise SolicitacaoRespondida(sol)
        sol.sol_status = StatusSolicitacao.ACEITO
        sol.sol_data_resposta = agora
        sol.save(update_fields=["sol_status", "sol_data_resposta"])
        nome_docente = docente.usu_nome
        notificar(
            aluno,
            mensagens.MO02_PEDIDO_ACEITO.format(docente=nome_docente),
            link=link_secao(tcc, "orientacao"),
        )
        if anterior is not None:
            notificar(
                anterior.doc,
                mensagens.MO05_TROCA_ORIENTADOR.format(nome=aluno.usu_nome, docente=nome_docente),
                link=reverse("cadastro:orientacoes"),
            )
        turma = tcc.tcc_tur
        professor = turma.tur_doc.doc
        texto = mensagens.MO04_ORIENTACAO_ACEITA.format(
            docente=nome_docente, nome=aluno.usu_nome, identificador=turma.tur_identificador
        )
        link_painel = reverse("cadastro:painel_aluno", args=[turma.pk, aluno.pk])
        notificar(professor, texto, link=link_painel)
        enviar_email_apos_commit(
            professor,
            mensagens.MO04_ASSUNTO,
            "cadastro/emails/orientacao_aceita.txt",
            {"texto": texto, "link": settings.SITE_URL + link_painel},
        )
    return mensagens.MO15_PEDIDO_ACEITO


def _aceitar_convite(docente, tcc, sol, aluno, agora):
    """Ramo do convite de coorientação no aceite (FR-032). [US-36][RBN-CAD-10.4][FR-032]"""
    orientador = orientador_atual(tcc)
    if orientador is not None and orientador.pk == docente.pk:
        raise Http404
    try:
        with transaction.atomic():
            Coorientacoes.objects.create(
                coo_tcc=tcc,
                coo_doc_id=docente.pk,
                coo_status=StatusCoorientacao.ATIVA,
                coo_data_inicio=agora,
            )
    except IntegrityError:
        raise SolicitacaoRespondida(sol)
    sol.sol_status = StatusSolicitacao.ACEITO
    sol.sol_data_resposta = agora
    sol.save(update_fields=["sol_status", "sol_data_resposta"])
    nome = docente.usu_nome
    notificar(
        aluno,
        mensagens.MO10_CONVITE_ACEITO_ALUNO.format(docente=nome),
        link=link_secao(tcc, "orientacao"),
    )
    if orientador is not None:
        notificar(
            orientador.doc,
            mensagens.MO10_CONVITE_ACEITO_ORIENTADOR.format(docente=nome, nome=aluno.usu_nome),
            link=reverse("cadastro:orientacoes"),
        )
    return mensagens.CONVITE_ACEITO


def recusar_solicitacao(docente, sol_id):
    """ "Recusar" um pedido (FR-011: MO-03 ao Aluno; o orientador atual é mantido na troca) ou
    convite (FR-032: MO-11 ao Aluno), com autor, data e hora. Devolve a mensagem da tela.
    [US-18][US-36][RBN-CAD-10.2][RBN-CAD-10.4][FR-011][FR-032]
    """
    with transaction.atomic():
        tcc, sol = _travar_para_resposta(docente, sol_id)
        sol.sol_status = StatusSolicitacao.RECUSADO
        sol.sol_data_resposta = timezone.now()
        sol.save(update_fields=["sol_status", "sol_data_resposta"])
        convite = sol.sol_tipo == TipoSolicitacao.COORIENTACAO
        modelo = mensagens.MO11_CONVITE_RECUSADO if convite else mensagens.MO03_PEDIDO_RECUSADO
        notificar(
            tcc.tcc_alu.alu,
            modelo.format(docente=docente.usu_nome),
            link=link_secao(tcc, "orientacao"),
        )
    return mensagens.CONVITE_RECUSADO if convite else mensagens.PEDIDO_RECUSADO


def solicitacao_para_proposta(docente, sol_id):
    """Pedido pendente do docente para a janela "Ver proposta" (FR-013), ou 404.

    [US-18][RBN-CAD-10.2][FR-013]
    """
    sol = (
        SolicitacoesOrientacao.objects.select_related(
            "sol_tcc__tcc_alu__alu", "sol_tcc__tcc_tur", "sol_tcc__tcc_ari"
        )
        .filter(
            pk=sol_id,
            sol_doc_id=docente.pk,
            sol_tipo__in=TIPOS_PEDIDO,
            sol_status=StatusSolicitacao.AGUARDANDO_RESPOSTA,
        )
        .first()
    )
    if sol is None or sol.sol_tcc.tcc_status == StatusTCC.SEM_PROPOSTA:
        raise Http404
    return sol


def tcc_do_orientador(docente, tcc_id):
    """TCC em que o docente é o Orientador atual, em turma não arquivada (rotas 21 a 24), ou
    404 (sem revelar o TCC; research R10, A10). [US-18][US-42][US-46][FR-015][FR-043]
    """
    tcc = TCCs.objects.select_related("tcc_tur__tur_cur", "tcc_alu__alu").filter(pk=tcc_id).first()
    if tcc is None or turma_arquivada(tcc.tcc_tur) or not e_orientador_atual(docente, tcc):
        raise Http404
    return tcc


def conferir_correcoes(orientador, tcc_id):
    """ "Correções Conferidas" (FR-016; research R15): trava turma → aluno → TCC → Versão Final e
    só então confere: Orientador atual, TCC 2 de Sistemas de Informação com "Aprovado com
    Correções", Versão Final Entregue ou Entregue com Atraso e ainda não conferida; grava
    `ent_correcoes_conferidas_em`, o único campo de Entregas_Marcos que a 006 escreve.
    [US-18 #16][US-44 B][RBN-CAD-09.5][FR-016][Q2][research R15]
    """
    achado = TCCs.objects.filter(pk=tcc_id).values("tcc_tur_id", "tcc_alu_id").first()
    if achado is None:
        raise Http404
    with transaction.atomic():
        turma = travar_turma_ativa(achado["tcc_tur_id"])
        aluno = Alunos.objects.select_for_update().filter(pk=achado["tcc_alu_id"]).first()
        tcc = (
            TCCs.objects.select_for_update(of=("self",))
            .select_related("tcc_tur__tur_cur", "tcc_alu__alu")
            .get(pk=tcc_id)
        )
        if tcc.tcc_tur_id != turma.pk or not e_orientador_atual(orientador, tcc):
            raise Http404
        entrega = versao_final_do_aluno(turma, aluno, travar=True)
        if estado_correcoes(tcc, [entrega] if entrega else []) != "disponivel":
            raise Http404
        entrega.ent_correcoes_conferidas_em = timezone.now()
        entrega.save(update_fields=["ent_correcoes_conferidas_em"])
    return tcc
