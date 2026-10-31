"""Regras da sessão de defesa (spec 007, research C1): status, histórico, criação da sessão,
banca, elegibilidade e o stub do descarte de avaliações.

Contrato com a feat-08 e a feat-09 em specs/007-agendamento-banca/contracts/servicos-defesa.md.
Nenhuma função daqui trava registros por si: quem chama trava antes, dentro do mesmo
transaction.atomic() (research C2 e C3).

[US-21][US-23][US-24][US-40][RBN-DEF-01.1][RBN-DEF-01.2][RBN-DEF-01.6][RBN-DEF-02.1]
"""

import logging
from datetime import datetime, timedelta

from django.db.models import Exists, OuterRef, Q
from django.utils import timezone

from sigtcc.apps.cadastro import services_orientacao
from sigtcc.apps.cadastro.cargas import CURSO_ENG_COMPUTACAO
from sigtcc.apps.cadastro.choices import StatusOrientacao, StatusTCC, StatusTurma
from sigtcc.apps.cadastro.models import Orientacoes, TCCs, Usuarios
from sigtcc.apps.cadastro.services_turmas import STATUS_SESSAO_ATIVA
from sigtcc.apps.defesa import mensagens
from sigtcc.apps.defesa.choices import EventoDefesa, FormatoSessao, PapelBanca, StatusSessao
from sigtcc.apps.defesa.models import (
    BancaDefesa,
    Defesas,
    DefesasPresenciais,
    DefesasRemotas,
    HistoricoDefesas,
)

logger = logging.getLogger("sigtcc.defesa")

# Reserva automática de cada sessão (RBN-DEF-01.1, campo 3). [US-21][US-22][RBN-DEF-03.1]
DURACAO_DA_SESSAO = timedelta(hours=1)


class ErroDefesa(Exception):
    """Ação recusada com a mensagem exata da US e, se houver, o campo a destacar (a view mostra a
    mensagem e volta ao formulário, sem gravar nada). [US-21][US-22][US-23][US-24]
    """

    def __init__(self, mensagem, campo=None):
        """Guarda a mensagem e o campo. [US-21][US-22][US-23][US-24]"""
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.campo = campo


class ConflitoDeHorario(ErroDefesa):
    """Um ou mais membros da banca têm outra sessão ativa no intervalo de 1 hora; `membros` traz
    todos eles, com o papel, para uma única mensagem (US-22, E3).
    [US-22][RBN-DEF-03.1][FR-014][FR-016]
    """

    def __init__(self, membros):
        """Monta a MD-01 com "Nome (papel)" de cada membro. [US-22][RBN-DEF-03.1][FR-016]"""
        nomes = ", ".join(f"{usuario.usu_nome} ({_rotulo(papel)})" for usuario, papel in membros)
        super().__init__(mensagens.MD01_CONFLITO_DE_HORARIO.format(membros=nomes))
        self.membros = membros


def _rotulo(papel):
    """Papel na banca para as mensagens ("Orientador" em vez de "Orientador (Presidente)").
    [US-22][US-23][RBN-DEF-02.1]
    """
    if papel == PapelBanca.ORIENTADOR_PRESIDENTE:
        return "Orientador"
    return PapelBanca(papel).label


# =============================================================================================
# Status da sessão e histórico da defesa (research C2; contrato §1 e §2)
# =============================================================================================

# Evento do histórico gravado em cada transição de status (1:1, achado I4 da revisão).
# [US-24][US-40][RBN-DEF-01.2][RBN-DEF-01.6]
EVENTO_DA_TRANSICAO = {
    StatusSessao.REAGENDADA: EventoDefesa.REAGENDAMENTO,
    StatusSessao.EM_ANDAMENTO: EventoDefesa.INICIO_AUTOMATICO,
    StatusSessao.CANCELADA: EventoDefesa.CANCELAMENTO,
    StatusSessao.REALIZADA: EventoDefesa.LIBERACAO_DO_RESULTADO,
}

# Pares (status atual, novo status) permitidos numa sessão que já existe. A criação (só
# "Agendada") não entra aqui: é feita por agendar_sessao. [US-24][RBN-DEF-01.2][RBN-DEF-03.3]
TRANSICOES_VALIDAS = frozenset(
    {
        (StatusSessao.AGENDADA, StatusSessao.REAGENDADA),
        (StatusSessao.REAGENDADA, StatusSessao.REAGENDADA),
        (StatusSessao.AGENDADA, StatusSessao.EM_ANDAMENTO),
        (StatusSessao.REAGENDADA, StatusSessao.EM_ANDAMENTO),
        (StatusSessao.AGENDADA, StatusSessao.CANCELADA),
        (StatusSessao.REAGENDADA, StatusSessao.CANCELADA),
        (StatusSessao.EM_ANDAMENTO, StatusSessao.CANCELADA),
        (StatusSessao.EM_ANDAMENTO, StatusSessao.REALIZADA),
    }
)

# Dados opcionais de um evento → coluna de Historico_Defesas (dicionário 3.6.7).
_CAMPOS_DO_EVENTO = {
    "status_anterior": "hdf_status_anterior",
    "status_novo": "hdf_status_novo",
    "data_anterior": "hdf_data_anterior",
    "hora_anterior": "hdf_hora_anterior",
    "data_nova": "hdf_data_nova",
    "hora_nova": "hdf_hora_nova",
    "membro_removido": "hdf_membro_removido",
    "membro_incluido": "hdf_membro_incluido",
}


def registrar_evento(sessao, tipo, justificativa, autor, **dados):
    """Grava uma linha do histórico da defesa (contrato §2). `autor=None` é o sistema (início
    automático); `dados` aceita as chaves de _CAMPOS_DO_EVENTO e `agora` (data e hora do evento,
    padrão: o instante atual). Chave desconhecida levanta TypeError, sem gravar nada.
    [US-40][US-23][RBN-DEF-01.6][RBN-DEF-02.2][FR-023][FR-029]
    """
    agora = dados.pop("agora", None) or timezone.now()
    desconhecidos = set(dados) - set(_CAMPOS_DO_EVENTO)
    if desconhecidos:
        raise TypeError(f"Dados de evento desconhecidos: {sorted(desconhecidos)}")
    colunas = {_CAMPOS_DO_EVENTO[chave]: valor for chave, valor in dados.items()}
    return HistoricoDefesas.objects.create(
        hdf_def=sessao,
        hdf_evento=tipo,
        hdf_justificativa=justificativa,
        hdf_data_hora=agora,
        hdf_usu=autor,
        **colunas,
    )


def transicionar_status(sessao, novo_status, autor, justificativa=None, **dados_evento):
    """Único ponto que muda def_status de uma sessão que já existe (contrato §1). Confere o par
    (status atual, novo status) em TRANSICOES_VALIDAS; fora dele, levanta ValueError sem gravar
    nada. Pressupõe a sessão travada por quem chama (select_for_update, research C3).
    Devolve a linha gravada no histórico.
    [US-24][RBN-DEF-01.2][RBN-DEF-03.3][FR-017][FR-023]
    """
    anterior = sessao.def_status
    if (anterior, novo_status) not in TRANSICOES_VALIDAS:
        raise ValueError(f"Transição inválida: {anterior!r} → {novo_status!r}")
    sessao.def_status = novo_status
    sessao.save(update_fields=["def_status"])
    return registrar_evento(
        sessao,
        EVENTO_DA_TRANSICAO[novo_status],
        justificativa,
        autor,
        status_anterior=anterior,
        status_novo=novo_status,
        **dados_evento,
    )


# =============================================================================================
# Elegibilidade para o agendamento (RBN-DEF-01.1 e 01.3)
# =============================================================================================


def _tem_sessao_ativa():
    """Subconsulta: o TCC tem sessão "Agendada", "Reagendada" ou "Em Andamento".
    [US-21][RBN-DEF-01.1][FR-003]
    """
    return Exists(
        Defesas.objects.filter(def_tcc=OuterRef("pk"), def_status__in=STATUS_SESSAO_ATIVA)
    )


def tcc_elegivel(tcc):
    """O TCC pode receber uma sessão agora: Status "Apto para Defesa", turma ativa (turma
    arquivada é só consulta, RBN-CAD-04.5) e nenhuma sessão ativa. Não confere quem agenda (isso
    é permissoes_defesa.pode_agendar). [US-21][RBN-DEF-01.1][RBN-DEF-01.3][FR-001][FR-003]
    """
    return (
        tcc.tcc_status == StatusTCC.APTO_PARA_DEFESA
        and tcc.tcc_tur.tur_status == StatusTurma.ATIVA
        and not Defesas.objects.filter(def_tcc=tcc, def_status__in=STATUS_SESSAO_ATIVA).exists()
    )


def tccs_elegiveis(usuario):
    """Lista do campo TCC do agendamento: os TCCs elegíveis (tcc_elegivel) que o usuário pode
    agendar pela regra de permissoes_defesa.pode_agendar, numa consulta só, com aluno e turma já
    carregados para mostrar título e nome do aluno.
    [US-21][RBN-DEF-01.1][RBN-DEF-01.3][FR-001][FR-003]
    """
    e_orientador = Exists(
        Orientacoes.objects.filter(
            ori_tcc=OuterRef("pk"), ori_doc_id=usuario.pk, ori_status=StatusOrientacao.ATIVA
        )
    )
    engenharia = Q(tcc_tur__tur_cur__cur_nome=CURSO_ENG_COMPUTACAO)
    return (
        TCCs.objects.filter(
            tcc_status=StatusTCC.APTO_PARA_DEFESA, tcc_tur__tur_status=StatusTurma.ATIVA
        )
        .exclude(_tem_sessao_ativa())
        .filter((engenharia & e_orientador) | (~engenharia & Q(tcc_tur__tur_doc_id=usuario.pk)))
        .select_related("tcc_alu__alu", "tcc_tur__tur_cur")
        .order_by("tcc_alu__alu__usu_nome", "tcc_id")
    )


# =============================================================================================
# Criação da sessão e banca (research C2 e C4; contrato §1 e §3)
# =============================================================================================

# Papéis dos 3 membros titulares, na ordem da banca (RBN-DEF-02.1). [US-23][RBN-DEF-02.1]
PAPEIS_TITULARES = (
    PapelBanca.ORIENTADOR_PRESIDENTE,
    PapelBanca.PRIMEIRO_AVALIADOR,
    PapelBanca.SEGUNDO_AVALIADOR,
)


def _gravar_local_ou_link(sessao, local=None, link=None):
    """Grava o Local (Presencial, até 100 caracteres) ou o Link da Videochamada (Remota, até 500)
    conforme def_formato; se a sessão tinha a linha do outro formato, remove-a. Formato e tamanhos
    já validados pelo formulário. [US-21][RBN-DEF-01.1][FR-001][FR-004][FR-005]
    """
    if sessao.def_formato == FormatoSessao.PRESENCIAL:
        DefesasRemotas.objects.filter(der_def=sessao).delete()
        DefesasPresenciais.objects.update_or_create(dep_def=sessao, defaults={"dep_local": local})
    else:
        DefesasPresenciais.objects.filter(dep_def=sessao).delete()
        DefesasRemotas.objects.update_or_create(der_def=sessao, defaults={"der_link": link})


def _compor_banca(sessao, dados_banca):
    """Uma linha de Banca_Defesa por membro: o Orientador atual do TCC como Presidente (nunca vem
    do formulário), o 1º e o 2º Avaliador e o Suplente, se houver. `dados_banca` tem as chaves
    primeiro_avaliador, segundo_avaliador e suplente (Usuarios ou None), já validadas pelo
    formulário (membros distintos, sem orientador nem coorientador).
    [US-23][RBN-DEF-02.1][FR-007][research C4]
    """
    orientador = services_orientacao.orientador_atual(sessao.def_tcc)
    if orientador is None:
        raise ValueError("O TCC não tem orientador atual para presidir a banca.")
    membros = [
        (orientador.doc, PapelBanca.ORIENTADOR_PRESIDENTE),
        (dados_banca["primeiro_avaliador"], PapelBanca.PRIMEIRO_AVALIADOR),
        (dados_banca["segundo_avaliador"], PapelBanca.SEGUNDO_AVALIADOR),
    ]
    if dados_banca.get("suplente") is not None:
        membros.append((dados_banca["suplente"], PapelBanca.SUPLENTE))
    BancaDefesa.objects.bulk_create(
        BancaDefesa(ban_def=sessao, ban_usu=usuario, ban_papel=papel) for usuario, papel in membros
    )


def agendar_sessao(tcc, dados_basicos, dados_banca, autor):
    """Único ponto que cria a sessão de defesa, sempre "Agendada" (contrato §1): grava Defesas, o
    Local ou o Link, a banca e o evento 'Agendamento' no histórico. `dados_basicos` tem data,
    h_inicio, formato e local ou link. Pressupõe o TCC travado e elegível e o conflito de horário
    já conferido por quem chama (research C2 e C3); não valida nem trava nada por si.
    [US-21][US-23][US-24][RBN-DEF-01.1][RBN-DEF-01.2][RBN-DEF-03.2][FR-001][FR-017][FR-023]
    """
    sessao = Defesas.objects.create(
        def_tcc=tcc,
        def_data=dados_basicos["data"],
        def_h_inicio=dados_basicos["h_inicio"],
        def_formato=dados_basicos["formato"],
        def_status=StatusSessao.AGENDADA,
    )
    _gravar_local_ou_link(sessao, dados_basicos.get("local"), dados_basicos.get("link"))
    _compor_banca(sessao, dados_banca)
    registrar_evento(
        sessao, EventoDefesa.AGENDAMENTO, None, autor, status_novo=StatusSessao.AGENDADA
    )
    return sessao


def membros_efetivos(sessao):
    """Os 3 membros que de fato atuam na sessão (Orientador, 1º e 2º Avaliador), na ordem da
    banca. O suplente acionado já ocupa o papel do titular ausente (RBN-DEF-02.2) e por isso
    entra; o Suplente não acionado não entra (contrato §2: avaliação, quórum, ata e declaração).
    [US-23][RBN-DEF-02.1][RBN-DEF-02.2][RBN-DEF-07.1][RBN-DEF-08.3]
    """
    linhas = BancaDefesa.objects.select_related("ban_usu").filter(
        ban_def=sessao, ban_papel__in=PAPEIS_TITULARES
    )
    ordenadas = sorted(linhas, key=lambda linha: PAPEIS_TITULARES.index(linha.ban_papel))
    return [linha.ban_usu for linha in ordenadas]


# =============================================================================================
# Serviço consumido da feat-08, ainda não entregue (contrato §6)
# =============================================================================================


def descartar_avaliacoes(sessao, membro=None):
    """STUB até a feat-08 entregar a função real (Clarifications da spec 007): só registra em log
    que o descarte foi pedido, sem tocar em Avaliacoes. `membro=None` = todos os membros. A
    feat-08 troca o corpo sem mudar a assinatura nem os pontos de chamada (cancelamento,
    alteração da banca e acionamento do suplente).
    [US-23][US-24][RBN-DEF-02.2][RBN-DEF-02.4][RBN-DEF-03.3][FR-011][FR-013][FR-020]
    """
    logger.info(
        "Descarte de avaliações pedido (stub): sessão %s, membro %s",
        sessao.pk,
        membro.pk if membro is not None else "todos",
    )


# =============================================================================================
# Travas e conflito de horário (research C3; US-22)
# =============================================================================================


def _travar_membros(ids_usuarios):
    """Trava, em ordem fixa de pk (evita deadlock), os usuários propostos para a banca. Serializa
    duas transações que disputam o mesmo docente, mesmo quando nenhuma das sessões em jogo existe
    ainda (research C3; bloqueante B2 da revisão do plano). Chamar dentro de transaction.atomic(),
    antes de _verificar_conflito. [US-22][RBN-DEF-03.1][FR-014][FR-016]
    """
    return list(
        Usuarios.objects.filter(pk__in=sorted(set(ids_usuarios))).select_for_update().order_by("pk")
    )


def _janela(data, h_inicio):
    """Início e fim da reserva de 1 hora. [US-22][RBN-DEF-01.1][RBN-DEF-03.1]"""
    inicio = datetime.combine(data, h_inicio)
    return inicio, inicio + DURACAO_DA_SESSAO


def _verificar_conflito(membros, data, h_inicio, excluir_sessao=None):
    """Levanta ConflitoDeHorario se algum membro tem outra sessão "Agendada", "Reagendada" ou "Em
    Andamento" que se sobrepõe à janela de 1 hora (a da sessão Em Andamento conta do início, que é
    o horário marcado, US-22 E4). Sessões encostadas (09:00-10:00 e 10:00) não conflitam. O Local
    não entra (US-22, fluxo B). `membros` = pares (Usuarios, papel); `excluir_sessao` é a própria
    sessão no reagendamento e na alteração da banca. Não grava nada; chamar depois de
    _travar_membros. [US-22][RBN-DEF-03.1][FR-014][FR-015][FR-016]
    """
    membros = list(membros)
    inicio, fim = _janela(data, h_inicio)
    linhas = BancaDefesa.objects.select_related("ban_def").filter(
        ban_usu_id__in=[usuario.pk for usuario, _papel in membros],
        ban_def__def_status__in=STATUS_SESSAO_ATIVA,
        # A janela pode passar da meia-noite: confere o dia anterior e o seguinte.
        ban_def__def_data__range=(data - timedelta(days=1), data + timedelta(days=1)),
    )
    if excluir_sessao is not None:
        linhas = linhas.exclude(ban_def=excluir_sessao)
    ocupados = set()
    for linha in linhas:
        outro_inicio, outro_fim = _janela(linha.ban_def.def_data, linha.ban_def.def_h_inicio)
        if outro_inicio < fim and inicio < outro_fim:
            ocupados.add(linha.ban_usu_id)
    em_conflito = [(usuario, papel) for usuario, papel in membros if usuario.pk in ocupados]
    if em_conflito:
        raise ConflitoDeHorario(em_conflito)
