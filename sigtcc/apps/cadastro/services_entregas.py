"""Regras das entregas da turma do app cadastro (spec 005).

Domínio `Turmas_Marcos`/`Entregas_Marcos`/`Historico_Envios_Entregas`: cadastro de entregas pelo
Professor da Disciplina (US-43), envio e substituição do link pelo Aluno, com lembretes de prazo
(US-15), envio da Versão Final do TCC 2 (US-29), acompanhamento das entregas pelo Professor
(US-16) e homologação ou devolução para ajuste da Versão Final (US-44). Este módulo importa
`services_turmas` (permissão por turma, `criar_entregas_do_aluno`, `atualizar_status_tcc`) e
`services_tcc`, nunca o contrário.

[US-15][US-16][US-29][US-43][US-44][RBN-CAD-09.1 a 09.6]
[research C1][research C5][research C6][research C7]
"""

import operator
from datetime import timedelta
from functools import reduce

from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import Http404
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services_turmas
from sigtcc.apps.cadastro.choices import StatusEntrega, StatusTCC, StatusTurma, TipoEntrega
from sigtcc.apps.cadastro.models import (
    AlunosTurmas,
    EntregasMarcos,
    HistoricoEnviosEntregas,
    Notificacoes,
    TCCs,
    TurmasMarcos,
)
from sigtcc.apps.cadastro.services import notificar

# Margens dos lembretes de prazo (FR-022; research C5): 7 dias, 48h e 24h antes da Data Limite,
# com tolerância de ±1h entre execuções da rotina agendada.
_MARGEM_LEMBRETE = timedelta(hours=1)
_PRAZOS_LEMBRETE = (timedelta(days=7), timedelta(hours=48), timedelta(hours=24))


class ErroEntrega(Exception):
    """Recusa do cadastro de entrega com a mensagem exata e, se houver, o campo a destacar.

    [US-43][FR-014][research C6]
    """

    def __init__(self, mensagem, campo=None):
        """Guarda a mensagem exata e o campo. [FR-014]"""
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.campo = campo


# =============================================================================================
# Cadastro de entregas pelo Professor da Disciplina (US-43; FR-013 a FR-017; research C6)
# =============================================================================================


def cadastrar_entrega(professor, tur_id, dados):
    """Cadastra uma entrega (`Turmas_Marcos`) na turma do Professor da Disciplina (passos 3 a 6
    da US-43) e cria, para cada aluno atualmente matriculado com participação não encerrada, o
    registro de status ("Aguardando Envio", ou "Não Entregue" se a Data Limite já estiver
    vencida), notificando cada um deles com o Título e a Data Limite (passo 7, MF-05, Q-48).

    A turma é travada antes da gravação (`travar_turma_ativa`, levanta `TurmaArquivada` se
    arquivada); a criação da entrega roda num savepoint próprio (`transaction.atomic()`
    aninhado, mesmo padrão de `services_tcc.salvar_alteracoes_tcc`, research C3) para a captura
    de `IntegrityError` da `UniqueConstraint` (Proposta/Documento para Defesa/Versão Final por
    turma) não invalidar a transação externa; o formulário já restringe o Tipo pela etapa
    (FR-013), então essa captura é a rede de segurança, não o mecanismo principal de checagem
    (research C6).
    [US-43][RBN-CAD-09.1][RBN-CAD-09.6][FR-013 a FR-016][Q-41][research C6]
    """
    with transaction.atomic():
        turma = services_turmas.travar_turma_ativa(tur_id)
        try:
            with transaction.atomic():
                entrega = TurmasMarcos.objects.create(
                    tma_tur=turma,
                    tma_tipo=dados["tipo"],
                    tma_titulo=dados["titulo"],
                    tma_instrucao=dados.get("instrucao") or None,
                    tma_data_limite=dados["data_limite"],
                )
        except IntegrityError:
            raise ErroEntrega(mensagens.ENTREGA_TIPO_REPETIDO, campo="tipo")

        status_inicial = (
            StatusEntrega.NAO_ENTREGUE
            if entrega.tma_data_limite < timezone.now()
            else StatusEntrega.AGUARDANDO_ENVIO
        )
        tccs_por_aluno = {t.tcc_alu_id: t for t in TCCs.objects.filter(tcc_tur=turma)}
        vinculos = AlunosTurmas.objects.filter(mat_tur=turma).select_related("mat_alu__alu")
        for vinculo in vinculos:
            aluno = vinculo.mat_alu
            tcc = tccs_por_aluno.get(aluno.pk)
            if tcc is not None and services_turmas.participacao_encerrada(tcc):
                continue
            EntregasMarcos.objects.create(ent_tma=entrega, ent_alu=aluno, ent_status=status_inicial)
            notificar(
                aluno.alu,
                mensagens.MF05_NOTIFICACAO_ENTREGA_CADASTRADA.format(
                    identificador=turma.tur_identificador,
                    titulo=entrega.tma_titulo,
                    data_limite=entrega.tma_data_limite.strftime("%d/%m/%Y"),
                ),
                # Acesso pela notificação (fluxo alternativo A da US-15): abre a aba Atividades.
                link=reverse("cadastro:minhas_entregas", args=[turma.pk]),
            )
    return entrega


# =============================================================================================
# Envio e substituição do link pelo Aluno (US-15; FR-018 a FR-023; research C7)
# =============================================================================================


def enviar_entrega(aluno, tma_id, link):
    """Envia ou substitui o link de uma entrega do Aluno (passos 4 a 7 e fluxo D da US-15
    original): grava `Historico_Envios_Entregas` e recalcula `ent_status` a partir do
    **primeiro** envio, nunca do mais recente (FR-019) — "Entregue" se o primeiro envio ocorreu
    até 23:59 da Data Limite, "Entregue com Atraso" depois.

    Trava `Entregas_Marcos` (a linha do aluno nesta entrega) **e** `TCCs` (o TCC do aluno nessa
    turma) antes de consultar o primeiro envio e de checar `tcc.tcc_status` (research C7, achado
    A1 da análise `/speckit-analyze`): sem essas travas, um duplo clique no "Enviar" poderia gerar
    duas transações lendo `Historico_Envios_Entregas` vazio ao mesmo tempo, e uma corrida com
    `encerrar_participacao`/`atualizar_status_tcc` (que travam turma → aluno → TCC) poderia deixar
    passar um envio com o Status já mudado no meio da requisição.

    Recusa com `Http404` (sem alterar nada), no mesmo padrão de `services_tcc.salvar_proposta` e
    de `services_turmas.encerrar_participacao` para uma ação cujo botão a view já esconde, se a
    entrega não existir para este aluno, se for do tipo Proposta (cumprida ao salvar a Proposta,
    US-13, sem campo de link aqui), se for do tipo Versão Final (tratada só na US-29, Phase 8
    desta feature — ainda não liberada), se a turma estiver arquivada, se a participação do aluno
    estiver encerrada, se o TCC não estiver "Em Andamento", ou se já existir um envio anterior e a
    Data Limite já tiver passado sem devolução pendente (E3 da US-15 original). Notifica o
    Professor da Disciplina a cada envio e a cada substituição (MF-07, Q-49).
    [US-15][RBN-CAD-09.2][RBN-CAD-09.3][RBN-CAD-09.6][FR-018 a FR-021][FR-023][research C7]
    """
    with transaction.atomic():
        entrega = (
            EntregasMarcos.objects.select_for_update()
            .filter(ent_tma_id=tma_id, ent_alu=aluno)
            .first()
        )
        if entrega is None:
            raise Http404
        marco = entrega.ent_tma
        if marco.tma_tipo in (TipoEntrega.PROPOSTA, TipoEntrega.VERSAO_FINAL):
            raise Http404
        turma = marco.tma_tur
        tcc = TCCs.objects.select_for_update().filter(tcc_alu=aluno, tcc_tur=turma).first()
        if tcc is None:
            raise Http404
        if turma.tur_status == StatusTurma.ARQUIVADA:
            raise Http404
        if services_turmas.participacao_encerrada(tcc):
            raise Http404
        if tcc.tcc_status != StatusTCC.EM_ANDAMENTO:
            raise Http404

        primeiro_envio = (
            HistoricoEnviosEntregas.objects.filter(hen_ent=entrega)
            .order_by("hen_data_envio", "hen_id")
            .first()
        )
        agora = timezone.now()
        if (
            primeiro_envio is not None
            and agora > marco.tma_data_limite
            and entrega.ent_status != StatusEntrega.DEVOLVIDA_PARA_AJUSTE
        ):
            # E3 (US-15 original): substituição após a Data Limite — campo somente leitura.
            raise Http404

        HistoricoEnviosEntregas.objects.create(hen_ent=entrega, hen_link=link, hen_data_envio=agora)
        data_do_primeiro_envio = primeiro_envio.hen_data_envio if primeiro_envio else agora
        entrega.ent_status = (
            StatusEntrega.ENTREGUE
            if data_do_primeiro_envio <= marco.tma_data_limite
            else StatusEntrega.ENTREGUE_COM_ATRASO
        )
        entrega.save(update_fields=["ent_status"])
        notificar(
            turma.tur_doc.doc,
            mensagens.MF07_NOTIFICACAO_ENVIO_ENTREGA.format(
                nome=aluno.alu.usu_nome,
                titulo=marco.tma_titulo,
                identificador=turma.tur_identificador,
            ),
            # A notificação abre o acompanhamento da entrega (US-16).
            link=reverse("cadastro:entrega_acompanhar", args=[turma.pk, marco.pk]),
        )
    return entrega


def status_exibido(entrega, agora=None):
    """Status "efetivo" para exibição (FR-020, Cenário 3 do `spec.md`; fluxo alternativo C da
    US-15 original): enquanto "Aguardando Envio" e a Data Limite já tiver passado, mostra "Não
    Entregue" sem gravar nada no banco — o envio continua disponível (`enviar_entrega` não
    depende do valor gravado em `ent_status` para decidir se aceita um envio novo, só do
    primeiro registro de `Historico_Envios_Entregas`) e, se ocorrer, segue o fluxo alternativo B
    normalmente. Não altera o Status do TCC (FR-020, "sem reprovar o aluno").
    [US-15][RBN-CAD-09.3][FR-020]
    """
    agora = agora or timezone.now()
    if (
        entrega.ent_status == StatusEntrega.AGUARDANDO_ENVIO
        and agora > entrega.ent_tma.tma_data_limite
    ):
        return StatusEntrega.NAO_ENTREGUE
    return entrega.ent_status


def entregas_para_lembrar(agora):
    """`Entregas_Marcos` "Aguardando Envio" cuja Data Limite esteja a 7 dias, 48h ou 24h de
    `agora` (margem ±1h, para tolerar o intervalo entre execuções da rotina agendada), em turma
    não arquivada (fluxo alternativo E da US-15 original; FR-022). Função pura, sem notificar:
    quem chama (o comando de gestão) decide o texto e envia (research C5).
    [US-15][RBN-CAD-09.6][FR-022][research C5]
    """
    janelas = reduce(
        operator.or_,
        (
            Q(
                ent_tma__tma_data_limite__gte=agora + prazo - _MARGEM_LEMBRETE,
                ent_tma__tma_data_limite__lte=agora + prazo + _MARGEM_LEMBRETE,
            )
            for prazo in _PRAZOS_LEMBRETE
        ),
    )
    return EntregasMarcos.objects.filter(
        janelas,
        ent_status=StatusEntrega.AGUARDANDO_ENVIO,
        ent_tma__tma_tur__tur_status=StatusTurma.ATIVA,
    ).select_related("ent_tma__tma_tur", "ent_alu__alu")


def enviar_lembretes_de_prazo(agora=None):
    """Notifica cada aluno das `entregas_para_lembrar(agora)` com o lembrete de prazo (MF-08,
    PROVISÓRIA, Q-50), com o link para a janela da entrega. Chamada pelo comando de gestão
    `enviar_lembretes_entrega` (rotina agendada a configurar — research C5).

    Como a janela de cada prazo tem margem de ±1h, uma rotina horária encontraria a mesma
    entrega em duas execuções seguidas; para não repetir o lembrete, não notifica de novo quem já
    recebeu o mesmo texto nas últimas 2 horas (sem tabela nova: consulta `Notificacoes`).
    Devolve o número de lembretes enviados.
    [US-15][RBN-CAD-09.6][FR-022][research C5]
    """
    agora = agora or timezone.now()
    enviados = 0
    for entrega in entregas_para_lembrar(agora):
        marco = entrega.ent_tma
        turma = marco.tma_tur
        mensagem = mensagens.MF08_LEMBRETE_PRAZO_ENTREGA.format(
            titulo=marco.tma_titulo,
            identificador=turma.tur_identificador,
            data_limite=marco.tma_data_limite.strftime("%d/%m/%Y %H:%M"),
        )
        usuario = entrega.ent_alu.alu
        if Notificacoes.objects.filter(
            not_usu=usuario, not_mensagem=mensagem, not_data_hora__gte=agora - 2 * _MARGEM_LEMBRETE
        ).exists():
            continue
        notificar(
            usuario,
            mensagem,
            link=reverse("cadastro:entrega_enviar", args=[turma.pk, marco.pk]),
        )
        enviados += 1
    return enviados


# =============================================================================================
# Acompanhamento das entregas pelo Professor da Disciplina (US-16; FR-026, FR-027)
# =============================================================================================


def link_mais_recente(entrega):
    """Último envio (`Historico_Envios_Entregas`) do aluno nesta entrega, ou None — o link "mais
    recente" exibido ao Professor (FR-026) e, para a spec 006, o documento enviado à banca no
    agendamento (contrato `servicos-compartilhados.md`, §3).
    [US-16][RBN-CAD-09.4][FR-026]
    """
    return (
        HistoricoEnviosEntregas.objects.filter(hen_ent=entrega)
        .order_by("-hen_data_envio", "-hen_id")
        .first()
    )


def acompanhamento_entrega(tma_id):
    """Uma linha por aluno da turma da entrega, só com os alunos atualmente matriculados e com a
    participação não encerrada (regra das entregas do contrato, §3): o aluno (`aluno`, com nome
    e matrícula), o status de envio exibido (`status`, com "Não Entregue" calculado depois da
    Data Limite, FR-020), o envio mais recente (`envio`, link e data/hora, ou None) e o TCC do
    aluno na turma (`tcc`, usado no tipo Proposta para o "Ver Proposta", em vez do link).
    Consulta somente leitura, sem checagem de perfil: a view restringe ao Professor da
    Disciplina da turma (FR-027).
    [US-16][RBN-CAD-09.4][FR-026][FR-027]
    """
    marco = TurmasMarcos.objects.select_related("tma_tur").get(pk=tma_id)
    turma = marco.tma_tur
    matriculados = AlunosTurmas.objects.filter(mat_tur=turma).values("mat_alu")
    tccs_por_aluno = {t.tcc_alu_id: t for t in TCCs.objects.filter(tcc_tur=turma)}
    registros = (
        EntregasMarcos.objects.filter(ent_tma=marco, ent_alu__in=matriculados)
        .select_related("ent_tma", "ent_alu__alu")
        .order_by("ent_alu__alu__usu_nome", "ent_alu__alu_matricula")
    )
    agora = timezone.now()
    linhas = []
    for registro in registros:
        tcc = tccs_por_aluno.get(registro.ent_alu_id)
        if tcc is not None and services_turmas.participacao_encerrada(tcc):
            continue
        linhas.append(
            {
                "aluno": registro.ent_alu,
                "status": status_exibido(registro, agora),
                "envio": link_mais_recente(registro),
                "tcc": tcc,
            }
        )
    return linhas
