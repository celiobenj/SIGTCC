"""Regras da sessão de defesa (spec 007, research C1): status, histórico, criação da sessão,
banca, elegibilidade e o stub do descarte de avaliações.

Contrato com a feat-08 e a feat-09 em specs/007-agendamento-banca/contracts/servicos-defesa.md.
Nenhuma função daqui trava registros por si: quem chama trava antes, dentro do mesmo
transaction.atomic() (research C2 e C3).

[US-21][US-23][US-24][US-40][RBN-DEF-01.1][RBN-DEF-01.2][RBN-DEF-01.6][RBN-DEF-02.1]
"""

from django.utils import timezone

from sigtcc.apps.defesa.choices import EventoDefesa, StatusSessao
from sigtcc.apps.defesa.models import HistoricoDefesas

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
