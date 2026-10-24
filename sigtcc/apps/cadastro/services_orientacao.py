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
from django.http import Http404
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import (
    GatilhoStatusTCC,
    StatusCoorientacao,
    StatusOrientacao,
    StatusSolicitacao,
    StatusTCC,
    TipoSolicitacao,
)
from sigtcc.apps.cadastro.models import (
    Alunos,
    Coorientacoes,
    Docentes,
    HistoricoStatusTCC,
    Notificacoes,
    Orientacoes,
    SolicitacoesOrientacao,
    TCCs,
)
from sigtcc.apps.cadastro.services import enviar_email_apos_commit, notificar
from sigtcc.apps.cadastro.services_contas import docentes_ativos, travar_e_conferir_ativo
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
