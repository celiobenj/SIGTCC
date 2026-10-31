"""Regras da sessão de defesa (spec 007, research C1): status, histórico, criação da sessão,
banca, elegibilidade e o stub do descarte de avaliações.

Contrato com a feat-08 e a feat-09 em specs/007-agendamento-banca/contracts/servicos-defesa.md.
Nenhuma função daqui trava registros por si: quem chama trava antes, dentro do mesmo
transaction.atomic() (research C2 e C3).

[US-21][US-23][US-24][US-40][RBN-DEF-01.1][RBN-DEF-01.2][RBN-DEF-01.6][RBN-DEF-02.1]
"""

import calendar
import logging
from datetime import datetime, timedelta

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Exists, OuterRef, Q, Subquery
from django.http import Http404
from django.utils import timezone

from sigtcc.apps.cadastro import services_contas, services_entregas, services_orientacao
from sigtcc.apps.cadastro.cargas import CURSO_ENG_COMPUTACAO
from sigtcc.apps.cadastro.choices import (
    StatusCoorientacao,
    StatusOrientacao,
    StatusTCC,
    StatusTurma,
    TipoEntrega,
)
from sigtcc.apps.cadastro.models import (
    Alunos,
    Coorientacoes,
    EntregasMarcos,
    Orientacoes,
    TCCs,
    Turmas,
    Usuarios,
)
from sigtcc.apps.cadastro.permissoes import tem_perfil
from sigtcc.apps.cadastro.services import enviar_email_apos_commit, notificar
from sigtcc.apps.cadastro.services_turmas import STATUS_SESSAO_ATIVA, travar_turma_ativa
from sigtcc.apps.defesa import mensagens, permissoes_defesa
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
        # Reagendar Em Andamento, antes do resultado (RBN-DEF-03.3; US-23 E8).
        (StatusSessao.EM_ANDAMENTO, StatusSessao.REAGENDADA),
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


# =============================================================================================
# Travas da sessão, validação da banca e avisos (research C3 e C4)
# =============================================================================================

PAPEIS_ALTERAVEIS = (
    PapelBanca.PRIMEIRO_AVALIADOR,
    PapelBanca.SEGUNDO_AVALIADOR,
    PapelBanca.SUPLENTE,
)
TEMPLATE_AVISO = "defesa/emails/aviso_sessao.txt"


def _travar_tcc(tcc_id):
    """Trava turma → aluno → TCC (mesma ordem das specs 004 a 006) e relê o TCC. Chamar dentro
    de transaction.atomic(). TCC inexistente: 404. [US-21][US-23][US-24][research C3]
    """
    achado = TCCs.objects.filter(pk=tcc_id).values("tcc_tur_id", "tcc_alu_id").first()
    if achado is None:
        raise Http404
    travar_turma_ativa(achado["tcc_tur_id"])
    Alunos.objects.select_for_update().filter(pk=achado["tcc_alu_id"]).first()
    return (
        TCCs.objects.select_for_update(of=("self",))
        .select_related("tcc_tur__tur_cur", "tcc_alu__alu")
        .get(pk=tcc_id)
    )


def _tcc_da_sessao(def_id):
    """pk do TCC da sessão, sem trava; sessão inexistente: 404. [US-23][US-24][US-40]"""
    tcc_id = Defesas.objects.filter(pk=def_id).values_list("def_tcc_id", flat=True).first()
    if tcc_id is None:
        raise Http404
    return tcc_id


def _travar_sessao(def_id):
    """Trava e relê a sessão, por último na ordem de C3 (depois do TCC e dos membros).
    [US-23][US-24][research C3]
    """
    return (
        Defesas.objects.select_for_update(of=("self",))
        .select_related("def_tcc__tcc_tur__tur_cur", "def_tcc__tcc_alu__alu")
        .get(pk=def_id)
    )


def banca_por_papel(sessao):
    """{papel: Usuarios} da composição atual. [US-23][RBN-DEF-02.1]"""
    return {
        linha.ban_papel: linha.ban_usu
        for linha in BancaDefesa.objects.select_related("ban_usu").filter(ban_def=sessao)
    }


def validar_banca(tcc, banca):
    """1º e 2º Avaliador preenchidos (E2), membros distintos (E3) e nenhum orientador ou
    coorientador do trabalho como avaliador ou suplente (E4). `banca` = {papel: Usuarios ou
    None}, sem o Presidente. Levanta ErroDefesa sem gravar nada.
    [US-23][RBN-DEF-02.1][FR-009]
    """
    for papel in (PapelBanca.PRIMEIRO_AVALIADOR, PapelBanca.SEGUNDO_AVALIADOR):
        if banca.get(papel) is None:
            raise ErroDefesa(mensagens.CAMPO_OBRIGATORIO, campo=papel)
    escolhidos = [usuario.pk for usuario in banca.values() if usuario is not None]
    orientacao = {
        coo.coo_doc_id
        for coo in services_orientacao.coorientadores_ativos(tcc)
        if coo.coo_doc_id is not None
    }
    orientador = services_orientacao.orientador_atual(tcc)
    if orientador is not None:
        orientacao.add(orientador.pk)
    if len(set(escolhidos)) != len(escolhidos) or orientacao & set(escolhidos):
        raise ErroDefesa(mensagens.AVALIADORES_DISTINTOS)


def _conferir_contas(membros):
    """Contrato §1 da spec 002: cada conta que entra na banca é travada e relida no mesmo POST;
    docente que deixou de ser 'Ativa' no meio da operação é tratado como fora da lista (404,
    Q-68), sem gravar nada. Chamar depois de _travar_membros (mesma ordem de travas).
    [US-23][RBN-DEF-02.1][RBN-CAD-01.3][Q-67]
    """
    for membro in membros:
        if not services_contas.travar_e_conferir_ativo(membro):
            raise Http404


def _recalcular_validades(membros):
    """Contrato §2 da spec 002 (US-06): recalcula a validade de cada Membro Externo afetado,
    depois de gravar o evento; docentes são ignorados pelo próprio serviço, e uma falha fica só
    no log, sem desfazer a operação da Defesa. [US-06][US-23][US-24][RBN-CAD-03.3][Q-67]
    """
    for membro in membros:
        services_contas.recalcular_validade(membro)


def _quando(sessao):
    """ "DD/MM/AAAA às HH:MM" da sessão, para os avisos. [US-23][US-24]"""
    return f"{sessao.def_data:%d/%m/%Y} às {sessao.def_h_inicio:%H:%M}"


def _avisar(usuario, texto, assunto):
    """Aviso por notificação no sistema e por e-mail depois do commit (contrato da spec 004).
    [US-23][US-24][RBN-DEF-02.4][RBN-DEF-03.2][RBN-DEF-03.3]
    """
    notificar(usuario, texto)
    enviar_email_apos_commit(usuario, assunto, TEMPLATE_AVISO, {"texto": texto})


# =============================================================================================
# Alteração da banca e acionamento do suplente (US-23, fluxos C e D; research C4)
# =============================================================================================


def alterar_banca(usuario, def_id, nova_banca, justificativa):
    """Alterar banca (US-23 C): troca o 1º Avaliador, o 2º Avaliador e/ou o Suplente de uma
    sessão "Agendada" ou "Reagendada". `nova_banca` = {papel: Usuarios ou None}; se trouxer o
    Presidente diferente do atual, recusa com a E7 (o Orientador só sai por reagendamento).
    Confere o conflito de horário só dos membros que entram na banca (US-22 E). Cada troca grava
    um evento 'Alteração da Banca' (sem mudar def_status), descarta as avaliações do membro que
    saiu (stub) e avisa quem entrou, quem saiu e o Aluno. Sem troca, não grava nada.
    [US-23][RBN-DEF-02.1][RBN-DEF-02.4][FR-011][FR-012][FR-015][research C4]
    """
    tcc_id = _tcc_da_sessao(def_id)
    with transaction.atomic():
        tcc = _travar_tcc(tcc_id)
        sessao = Defesas.objects.get(pk=def_id)
        if not permissoes_defesa.pode_alterar_banca(usuario, sessao):
            raise PermissionDenied
        atual = banca_por_papel(sessao)
        presidente = nova_banca.get(PapelBanca.ORIENTADOR_PRESIDENTE)
        if presidente is not None and presidente != atual[PapelBanca.ORIENTADOR_PRESIDENTE]:
            raise ErroDefesa(mensagens.AUSENCIA_DO_ORIENTADOR)
        if not justificativa or len(justificativa) > 500:
            raise ErroDefesa(mensagens.JUSTIFICATIVA, campo="justificativa")
        proposta = {papel: nova_banca.get(papel) for papel in PAPEIS_ALTERAVEIS}
        validar_banca(tcc, proposta)
        trocas = [
            (papel, atual.get(papel), proposta[papel])
            for papel in PAPEIS_ALTERAVEIS
            if proposta[papel] != atual.get(papel)
        ]
        if not trocas:
            return sessao
        ja_na_banca = {membro.pk for membro in atual.values()}
        entram = [(novo, papel) for papel, _antigo, novo in trocas if novo is not None]
        entram = [(membro, papel) for membro, papel in entram if membro.pk not in ja_na_banca]
        _travar_membros([membro.pk for membro, _papel in entram])
        _conferir_contas([membro for membro, _papel in entram])
        sessao = _travar_sessao(def_id)
        _verificar_conflito(entram, sessao.def_data, sessao.def_h_inicio, excluir_sessao=sessao)
        # Apaga antes de criar: a PK (sessão, membro) permite trocar dois membros de papel.
        BancaDefesa.objects.filter(
            ban_def=sessao, ban_papel__in=[papel for papel, _antigo, _novo in trocas]
        ).delete()
        BancaDefesa.objects.bulk_create(
            BancaDefesa(ban_def=sessao, ban_usu=novo, ban_papel=papel)
            for papel, _antigo, novo in trocas
            if novo is not None
        )
        for papel, antigo, novo in trocas:
            if antigo is not None:
                descartar_avaliacoes(sessao, antigo)
            registrar_evento(
                sessao,
                EventoDefesa.ALTERACAO_DA_BANCA,
                justificativa,
                usuario,
                membro_removido=antigo,
                membro_incluido=novo,
            )
            _avisar_alteracao(sessao, papel, antigo, novo)
        _recalcular_validades(
            {pessoa for _papel, antigo, novo in trocas for pessoa in (antigo, novo) if pessoa}
        )
    return sessao


def _avisar_alteracao(sessao, papel, antigo, novo):
    """MD-02 a quem entrou, MD-03 a quem saiu e MD-04 ao Aluno (US-23 C.e).
    [US-23][RBN-DEF-02.4][FR-011]
    """
    tcc = sessao.def_tcc
    aluno = tcc.tcc_alu.alu
    dados = {"aluno": aluno.usu_nome, "quando": _quando(sessao), "titulo": tcc.tcc_titulo}
    assunto = mensagens.MD04_ASSUNTO
    if novo is not None:
        _avisar(novo, mensagens.MD02_BANCA_INCLUIDO.format(papel=_rotulo(papel), **dados), assunto)
    if antigo is not None:
        _avisar(antigo, mensagens.MD03_BANCA_REMOVIDO.format(**dados), assunto)
    texto = mensagens.MD04_BANCA_ALTERADA_ALUNO.format(
        quando=dados["quando"],
        incluido=novo.usu_nome if novo is not None else "ninguém",
        papel=_rotulo(papel),
        removido=antigo.usu_nome if antigo is not None else "ninguém",
    )
    _avisar(aluno, texto, assunto)


def acionar_suplente(usuario, def_id, papel_substituido, justificativa):
    """Acionar suplente (US-23 D): só o Orientador, com a sessão "Em Andamento" e Suplente na
    banca (senão PermissionDenied, M-02). O Suplente passa ao papel do titular ausente (1º ou 2º
    Avaliador), guardando quem ele substituiu e a Justificativa; o ausente sai da banca e as
    avaliações dele são descartadas (stub). Sem checar conflito: o suplente já passou por ele ao
    entrar na banca (research C3). Grava 'Acionamento do Suplente' sem mudar def_status.
    [US-23][RBN-DEF-02.2][FR-013][research C4]
    """
    if papel_substituido not in (PapelBanca.PRIMEIRO_AVALIADOR, PapelBanca.SEGUNDO_AVALIADOR):
        raise ErroDefesa(mensagens.CAMPO_OBRIGATORIO, campo="papel_substituido")
    if not justificativa or len(justificativa) > 500:
        raise ErroDefesa(mensagens.JUSTIFICATIVA, campo="justificativa")
    tcc_id = _tcc_da_sessao(def_id)
    with transaction.atomic():
        _travar_tcc(tcc_id)
        sessao = _travar_sessao(def_id)
        if not permissoes_defesa.pode_acionar_suplente(usuario, sessao):
            raise PermissionDenied
        atual = banca_por_papel(sessao)
        suplente, ausente = atual[PapelBanca.SUPLENTE], atual[papel_substituido]
        BancaDefesa.objects.filter(ban_def=sessao, ban_usu=ausente).delete()
        BancaDefesa.objects.filter(ban_def=sessao, ban_usu=suplente).update(
            ban_papel=papel_substituido,
            ban_usu_substituido=ausente,
            ban_justificativa_substituicao=justificativa,
        )
        descartar_avaliacoes(sessao, ausente)
        registrar_evento(
            sessao,
            EventoDefesa.ACIONAMENTO_DO_SUPLENTE,
            justificativa,
            usuario,
            membro_removido=ausente,
            membro_incluido=suplente,
        )
        _recalcular_validades([suplente])  # o substituído mantém a validade (spec 002, Q33)
    return sessao


# =============================================================================================
# Confirmação, reagendamento e cancelamento (US-24; research C5)
# =============================================================================================


def _lugar(sessao):
    """Local (Presencial) ou Link da Videochamada (Remota). [US-21][US-24][RBN-DEF-01.1]"""
    if sessao.def_formato == FormatoSessao.PRESENCIAL:
        return DefesasPresenciais.objects.get(dep_def=sessao).dep_local
    return DefesasRemotas.objects.get(der_def=sessao).der_link


def link_do_documento(tcc):
    """Link mais recente enviado pelo Aluno na entrega do tipo Documento para Defesa da turma do
    TCC (CAD-09.2), ou None (services_entregas.link_mais_recente, contrato da spec 005).
    [US-24][RBN-DEF-03.2][RBN-CAD-09.2][FR-018]
    """
    entrega = (
        EntregasMarcos.objects.filter(
            ent_tma__tma_tur=tcc.tcc_tur,
            ent_tma__tma_tipo=TipoEntrega.DOCUMENTO_PARA_DEFESA,
            ent_alu=tcc.tcc_alu,
        )
        .order_by("-ent_tma__tma_data_limite", "-ent_tma_id")
        .first()
    )
    envio = services_entregas.link_mais_recente(entrega) if entrega is not None else None
    return envio.hen_link if envio is not None else None


def _avisar_aluno_e_banca(sessao, texto, assunto):
    """O mesmo aviso ao Aluno e a todos os membros da banca, inclusive o Suplente não acionado
    (RBN-DEF-03.2; não membros_efetivos). [US-24][RBN-DEF-03.2][RBN-DEF-03.3][FR-018]
    """
    destinatarios = [sessao.def_tcc.tcc_alu.alu, *banca_por_papel(sessao).values()]
    for usuario in destinatarios:
        _avisar(usuario, texto, assunto)


def confirmar_agendamento(sessao, autor):
    """Fecha o agendamento (US-24, passos 3 a 7), na mesma transação de agendar_sessao, com o TCC
    já travado: avisa o Aluno e a banca (MD-05, com o link do Documento para Defesa) e cancela o
    pedido de troca de orientador pendente com o mesmo instante do evento 'Agendamento' (contrato
    §3 da spec 006). [US-24][RBN-DEF-03.2][RBN-CAD-10.6][FR-018][research C5]
    """
    tcc = sessao.def_tcc
    texto = mensagens.MD05_DEFESA_AGENDADA.format(
        aluno=tcc.tcc_alu.alu.usu_nome,
        quando=_quando(sessao),
        formato=sessao.def_formato,
        lugar=_lugar(sessao),
        titulo=tcc.tcc_titulo,
        documento=link_do_documento(tcc) or "-",
    )
    _avisar_aluno_e_banca(sessao, texto, mensagens.MD05_ASSUNTO)
    agendamento = HistoricoDefesas.objects.get(hdf_def=sessao, hdf_evento=EventoDefesa.AGENDAMENTO)
    services_orientacao.cancelar_troca_no_agendamento(tcc, agendamento.hdf_data_hora)


def _sessao_para_reagendar_ou_cancelar(usuario, def_id, justificativa):
    """Confere a Justificativa (E3) e trava turma → aluno → TCC, antes
    das travas de membros e da sessão. Sem permissão ou fora de status: PermissionDenied (M-02).
    [US-24][RBN-DEF-03.3][FR-019][FR-020][FR-022]
    """
    if not justificativa or len(justificativa) > 500:
        raise ErroDefesa(mensagens.JUSTIFICATIVA, campo="justificativa")
    _travar_tcc(_tcc_da_sessao(def_id))
    if not permissoes_defesa.pode_reagendar_ou_cancelar(usuario, Defesas.objects.get(pk=def_id)):
        raise PermissionDenied


def reagendar(usuario, def_id, dados_basicos, justificativa):
    """Reagendar (US-24 B): nova data, horário, formato e local ou link, mantendo a banca e as
    avaliações. Confere o conflito de todos os membros da banca, inclusive o Suplente, sem
    contar a própria sessão (US-22 D); com conflito, nada muda. Status "Reagendada", com as datas
    e horas anterior e nova no histórico; avisa o Aluno e a banca (MD-06).
    [US-24][RBN-DEF-03.3][RBN-DEF-03.1][FR-019][research C5]
    """
    with transaction.atomic():
        _sessao_para_reagendar_ou_cancelar(usuario, def_id, justificativa)
        atual = banca_por_papel(Defesas.objects.get(pk=def_id))
        membros = [(membro, papel) for papel, membro in atual.items()]
        _travar_membros([membro.pk for membro, _papel in membros])
        sessao = _travar_sessao(def_id)
        data, hora = dados_basicos["data"], dados_basicos["h_inicio"]
        _verificar_conflito(membros, data, hora, excluir_sessao=sessao)
        anterior = (sessao.def_data, sessao.def_h_inicio)
        sessao.def_data, sessao.def_h_inicio = data, hora
        sessao.def_formato = dados_basicos["formato"]
        sessao.save(update_fields=["def_data", "def_h_inicio", "def_formato"])
        _gravar_local_ou_link(sessao, dados_basicos.get("local"), dados_basicos.get("link"))
        transicionar_status(
            sessao,
            StatusSessao.REAGENDADA,
            usuario,
            justificativa,
            data_anterior=anterior[0],
            hora_anterior=anterior[1],
            data_nova=data,
            hora_nova=hora,
        )
        tcc = sessao.def_tcc
        texto = mensagens.MD06_DEFESA_REAGENDADA.format(
            aluno=tcc.tcc_alu.alu.usu_nome,
            quando=_quando(sessao),
            formato=sessao.def_formato,
            lugar=_lugar(sessao),
            titulo=tcc.tcc_titulo,
            justificativa=justificativa,
        )
        _avisar_aluno_e_banca(sessao, texto, mensagens.MD06_ASSUNTO)
        _recalcular_validades(atual.values())
    return sessao


def cancelar(usuario, def_id, justificativa):
    """Cancelar sessão (US-24 C): status "Cancelada", descarta todas as avaliações (stub) e avisa
    o Aluno e a banca (MD-07). O Status do TCC continua "Apto para Defesa" (esta spec nunca grava
    tcc_status), e o TCC volta a poder ser agendado. [US-24][RBN-DEF-03.3][FR-020][research C5]
    """
    with transaction.atomic():
        _sessao_para_reagendar_ou_cancelar(usuario, def_id, justificativa)
        sessao = _travar_sessao(def_id)
        transicionar_status(sessao, StatusSessao.CANCELADA, usuario, justificativa)
        descartar_avaliacoes(sessao)
        tcc = sessao.def_tcc
        texto = mensagens.MD07_DEFESA_CANCELADA.format(
            aluno=tcc.tcc_alu.alu.usu_nome,
            quando=_quando(sessao),
            titulo=tcc.tcc_titulo,
            justificativa=justificativa,
        )
        _avisar_aluno_e_banca(sessao, texto, mensagens.MD07_ASSUNTO)
        _recalcular_validades(banca_por_papel(sessao).values())
    return sessao


# =============================================================================================
# Início automático, lista de sessões, filtro de período e histórico (US-40; research C6, C7)
# =============================================================================================

# Atalhos do filtro de período (RBN-DEF-01.5); "periodo_letivo" é o padrão. [US-40][FR-025]
ATALHOS_DE_PERIODO = {
    "periodo_letivo": "Período Letivo",
    "esta_semana": "Esta Semana",
    "este_mes": "Este Mês",
    "proximos_30_dias": "Próximos 30 Dias",
    "intervalo": "Data Inicial e Data Final",
}


def sessoes_para_iniciar(agora):
    """Sessões "Agendada" ou "Reagendada" cuja data e horário marcados já chegaram (US-24 D).
    Função pura: quem chama (view ou comando agendado) faz a transição.
    [US-24][RBN-DEF-01.2][FR-021][research C6]
    """
    return Defesas.objects.filter(
        Q(def_data__lt=agora.date()) | Q(def_data=agora.date(), def_h_inicio__lte=agora.time()),
        def_status__in=(StatusSessao.AGENDADA, StatusSessao.REAGENDADA),
    ).order_by("def_data", "def_h_inicio", "def_id")


def periodo_letivo_atual(hoje=None):
    """(ano, semestre) do período letivo atual: o maior entre as turmas ativas (as arquivadas
    já encerraram o período, RBN-CAD-04.5); sem turma ativa, o do calendário (janeiro a junho =
    1). [US-40][RBN-DEF-01.5][FR-025][Clarifications 2026-10-31]
    """
    maior = (
        Turmas.objects.filter(tur_status=StatusTurma.ATIVA)
        .order_by("-tur_ano", "-tur_semestre")
        .values_list("tur_ano", "tur_semestre")
        .first()
    )
    if maior is not None:
        return maior
    hoje = hoje or timezone.now().date()
    return hoje.year, 1 if hoje.month <= 6 else 2


def filtro_de_periodo(atalho, data_inicial=None, data_final=None, hoje=None, prefixo=""):
    """Q sobre Defesas para o filtro de período (contrato §4), reaproveitável pela agenda, pelos
    ouvintes e pelos relatórios: Período Letivo pelo ano e semestre da turma do TCC; Esta Semana
    (segunda a domingo), Este Mês, Próximos 30 Dias e o intervalo manual pela data da sessão.
    `prefixo` permite consultar a partir de outro modelo (ex.: "pre_def__"). As datas do
    intervalo chegam já validadas (FiltroPeriodoForm). [US-40][RBN-DEF-01.5][FR-025]
    """
    hoje = hoje or timezone.now().date()
    if atalho == "periodo_letivo":
        ano, semestre = periodo_letivo_atual(hoje)
        return Q(
            **{
                f"{prefixo}def_tcc__tcc_tur__tur_ano": ano,
                f"{prefixo}def_tcc__tcc_tur__tur_semestre": semestre,
            }
        )
    if atalho == "esta_semana":
        inicio = hoje - timedelta(days=hoje.weekday())
        fim = inicio + timedelta(days=6)
    elif atalho == "este_mes":
        inicio = hoje.replace(day=1)
        fim = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1])
    elif atalho == "proximos_30_dias":
        inicio, fim = hoje, hoje + timedelta(days=30)
    elif atalho == "intervalo":
        inicio, fim = data_inicial, data_final
    else:
        raise ValueError(f"Atalho de período desconhecido: {atalho!r}")
    return Q(**{f"{prefixo}def_data__gte": inicio, f"{prefixo}def_data__lte": fim})


def _visiveis_para(usuario, cur_id):
    """Q da visibilidade por perfil (RBN-DEF-01.4), somada por OR: Coordenador de Curso e
    Secretaria veem todas as sessões do curso do filtro (cur_id None = todos os cursos); os
    demais, as sessões em que constam (Aluno, banca, Orientador e Coorientador ativos) e as dos
    alunos das turmas de que são Professor da Disciplina. [US-40][US-39][RBN-DEF-01.4][FR-024]
    """
    if tem_perfil(usuario, "coordenador", "secretaria"):
        return Q() if cur_id is None else Q(def_tcc__tcc_tur__tur_cur_id=cur_id)
    na_banca = BancaDefesa.objects.filter(ban_def=OuterRef("pk"), ban_usu_id=usuario.pk)
    orienta = Orientacoes.objects.filter(
        ori_tcc=OuterRef("def_tcc"), ori_doc_id=usuario.pk, ori_status=StatusOrientacao.ATIVA
    )
    coorienta = Coorientacoes.objects.filter(
        coo_tcc=OuterRef("def_tcc"), coo_doc_id=usuario.pk, coo_status=StatusCoorientacao.ATIVA
    )
    return (
        Q(def_tcc__tcc_alu_id=usuario.pk)
        | Q(Exists(na_banca))
        | Q(Exists(orienta))
        | Q(Exists(coorienta))
        | Q(def_tcc__tcc_tur__tur_doc_id=usuario.pk)
    )


def listar_defesas(usuario, periodo=None, status=None, cur_id=None):
    """Lista Defesas (US-40), em ordem cronológica, com a visibilidade do perfil e os filtros de
    período (Q de filtro_de_periodo), de Status (None = Todos) e de curso (Coordenador e
    Secretaria; None = Todos), numa consulta, com aluno, turma, Local ou Link e o nome do
    Orientador (Presidente) já carregados. [US-40][US-39][RBN-DEF-01.4][RBN-DEF-01.5][FR-024]
    [FR-025][FR-026][FR-027]
    """
    presidente = BancaDefesa.objects.filter(
        ban_def=OuterRef("pk"), ban_papel=PapelBanca.ORIENTADOR_PRESIDENTE
    ).values("ban_usu__usu_nome")[:1]
    sessoes = Defesas.objects.filter(_visiveis_para(usuario, cur_id))
    if periodo is not None:
        sessoes = sessoes.filter(periodo)
    if status:
        sessoes = sessoes.filter(def_status=status)
    return (
        sessoes.select_related(
            "def_tcc__tcc_alu__alu",
            "def_tcc__tcc_tur__tur_cur",
            "defesaspresenciais",
            "defesasremotas",
        )
        .annotate(orientador_nome=Subquery(presidente))
        .order_by("def_data", "def_h_inicio", "def_id")
    )


def historico_da_sessao(sessao):
    """Histórico da defesa do TCC (RBN-DEF-01.6): os eventos de todas as sessões do TCC desta
    sessão, inclusive as canceladas, em ordem cronológica, sem checagem de perfil (quem chama
    autoriza com permissoes_defesa.pode_ver_sessao). [US-40][RBN-DEF-01.6][FR-029][research C7]
    """
    return (
        HistoricoDefesas.objects.filter(hdf_def__def_tcc_id=sessao.def_tcc_id)
        .select_related("hdf_def", "hdf_usu", "hdf_membro_removido", "hdf_membro_incluido")
        .order_by("hdf_data_hora", "hdf_id")
    )


# =============================================================================================
# Agendamento completo (US-21, US-22, US-23 e US-24, fluxo principal; research C2 a C5)
# =============================================================================================


def agendar(usuario, tcc_id, dados_basicos, dados_banca):
    """Botão Agendar: trava turma → aluno → TCC, confere de novo quem agenda e a elegibilidade
    (E7 e E2 da US-21, com a mensagem E7), valida a banca (US-23 E2 a E4), trava e confere as
    contas da banca (contrato §1 da spec 002), checa o conflito de horário de toda a banca
    (US-22), cria a sessão "Agendada" e confirma (avisos e cancelamento da troca, US-24) e
    recalcula a validade dos Membros Externos (contrato §2 da spec 002). Qualquer recusa: nada
    gravado. `dados_banca` = {primeiro_avaliador, segundo_avaliador, suplente}.
    [US-21][US-22][US-23][US-24][RBN-DEF-01.1][RBN-DEF-01.3][RBN-DEF-02.1][RBN-DEF-03.1]
    [RBN-DEF-03.2][FR-001][FR-003][FR-009][FR-014][FR-018]
    """
    with transaction.atomic():
        tcc = _travar_tcc(tcc_id)
        if not (permissoes_defesa.pode_agendar(usuario, tcc) and tcc_elegivel(tcc)):
            raise ErroDefesa(mensagens.TCC_NAO_AGENDAVEL)
        banca = {
            PapelBanca.PRIMEIRO_AVALIADOR: dados_banca.get("primeiro_avaliador"),
            PapelBanca.SEGUNDO_AVALIADOR: dados_banca.get("segundo_avaliador"),
            PapelBanca.SUPLENTE: dados_banca.get("suplente"),
        }
        validar_banca(tcc, banca)
        presidente = services_orientacao.orientador_atual(tcc).doc
        membros = [(presidente, PapelBanca.ORIENTADOR_PRESIDENTE)]
        membros += [(membro, papel) for papel, membro in banca.items() if membro is not None]
        _travar_membros([membro.pk for membro, _papel in membros])
        _conferir_contas([membro for membro, _papel in membros])
        _verificar_conflito(membros, dados_basicos["data"], dados_basicos["h_inicio"])
        sessao = agendar_sessao(tcc, dados_basicos, dados_banca, usuario)
        confirmar_agendamento(sessao, usuario)
        _recalcular_validades([membro for membro, _papel in membros])
    return sessao
