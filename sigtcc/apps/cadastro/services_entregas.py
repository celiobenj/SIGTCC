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

import enum
import operator
import threading
from datetime import timedelta
from functools import reduce

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Exists, OuterRef, Q
from django.http import Http404
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services_tcc, services_turmas
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    GatilhoStatusTCC,
    StatusConta,
    StatusEntrega,
    StatusTCC,
    StatusTurma,
    TipoEntrega,
)
from sigtcc.apps.cadastro.models import (
    Alunos,
    AlunosTurmas,
    EntregasMarcos,
    HistoricoEnviosEntregas,
    Notificacoes,
    Secretarios,
    TCCs,
    TurmasMarcos,
)
from sigtcc.apps.cadastro.services import enviar_email, notificar, registrar_evento

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


class EventoFluxoTCC(enum.Enum):
    """Eventos desta spec no log de acesso (`services.registrar_evento`, que só usa `.value`):
    autor, data e hora da homologação e da devolução da Versão Final, sem tabela própria
    (dicionário 18/10, seção 4, item 5), no mesmo padrão de TURMA_EXCLUIDA da spec 004. Ficam aqui,
    e não em `services.EventoAcesso`, para não misturar com os eventos de acesso da spec 003.
    [US-44][RBN-CAD-09.5][FR-028]
    """

    VERSAO_FINAL_HOMOLOGADA = "VERSAO_FINAL_HOMOLOGADA"
    VERSAO_FINAL_DEVOLVIDA = "VERSAO_FINAL_DEVOLVIDA"


def _registrar_avaliacao(evento, aluno, professor, turma, entrega):
    """Grava no log, depois do commit, quem homologou ou devolveu a Versão Final; o detalhe só
    tem identificadores (nunca a mensagem digitada pelo Professor, A13 da spec 003).
    [US-44][RBN-CAD-09.5][FR-028]
    """
    detalhe = f"tur_id={turma.pk} tma_id={entrega.ent_tma_id}"
    transaction.on_commit(
        lambda: registrar_evento(evento, aluno.alu, autor=professor, detalhe=detalhe)
    )


def _enviar_email_ao_aluno(usuario, assunto, texto):
    """E-mail ao aluno com o mesmo texto da notificação (FR-015, FR-022), depois do commit, só
    se a conta tiver e-mail. Mesmo padrão da spec 003 (`services.pedir_redefinicao`): a falha fica
    só no log (`services.enviar_email` registra FALHA_ENVIO_EMAIL) e não desfaz a gravação.
    [US-43][US-15][RBN-CAD-09.6][FR-015][FR-022][Q-84]
    """
    destino = usuario.usu_email
    if not destino:
        return
    contexto = {"nome": usuario.usu_nome, "texto": texto}

    def enviar():
        """Envia o aviso; falha só no log. [FR-015][FR-022]"""
        try:
            enviar_email(
                destino, assunto, "cadastro/emails/aviso_entrega.txt", contexto, conta=usuario
            )
        except Exception:
            # Já registrado no log por enviar_email; a gravação não muda.
            pass

    if settings.SIGTCC_EMAIL_SINCRONO:
        transaction.on_commit(enviar)
    else:
        transaction.on_commit(lambda: threading.Thread(target=enviar, daemon=True).start())


# =============================================================================================
# Cadastro de entregas pelo Professor da Disciplina (US-43; FR-013 a FR-017; research C6)
# =============================================================================================


def cadastrar_entrega(professor, tur_id, dados):
    """Cadastra uma entrega (`Turmas_Marcos`) na turma do Professor da Disciplina (passos 3 a 6
    da US-43) e cria, para cada aluno atualmente matriculado com participação não encerrada, o
    registro de status ("Aguardando Envio", ou "Não Entregue" se a Data Limite já estiver
    vencida), notificando cada um deles com o Título e a Data Limite (passo 7, MF-05, Q-84).

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
            texto = mensagens.MF05_NOTIFICACAO_ENTREGA_CADASTRADA.format(
                identificador=turma.tur_identificador,
                titulo=entrega.tma_titulo,
                data_limite=entrega.tma_data_limite.strftime("%d/%m/%Y"),
            )
            notificar(
                aluno.alu,
                texto,
                # Acesso pela notificação (fluxo alternativo A da US-15): abre a aba Atividades.
                link=reverse("cadastro:minhas_entregas", args=[turma.pk]),
            )
            # E-mail com o Título e a Data Limite (passo 7 da US-43; FR-015; MF-11, Q-84).
            _enviar_email_ao_aluno(aluno.alu, mensagens.MF11_ASSUNTO_NOVA_ENTREGA, texto)
    return entrega


# =============================================================================================
# Envio e substituição do link pelo Aluno (US-15; FR-018 a FR-023; research C7)
# =============================================================================================


# Status do TCC que liberam o envio da Versão Final: resultado da banca liberado com parecer
# Aprovado ou Aprovado com Correções (FR-024; research C7 — `tcc_status` já distingue o parecer).
STATUS_TCC_LIBERA_VERSAO_FINAL = (StatusTCC.APROVADO, StatusTCC.APROVADO_COM_CORRECOES)


def envio_liberado(entrega, tcc, agora=None):
    """Regra única que decide se o Aluno pode enviar (ou substituir) o link desta entrega —
    usada por `enviar_entrega`, que confere de novo com as travas, e pelas views, só para
    mostrar ou esconder o campo Link e o botão Enviar (SC-004).

    Nunca na entrega do tipo Proposta (cumprida ao salvar a Proposta, US-13), em turma arquivada
    nem com a participação encerrada (FR-023; Reprovado incluído — E7 da US-29). Na Versão Final
    (US-29), só com o resultado liberado como Aprovado ou Aprovado com Correções (FR-024) e nunca
    depois de homologada (E6); nas demais, só com o TCC "Em Andamento" (FR-023). Com devolução
    para ajuste pendente, o reenvio é sempre aceito (FR-019, FR-025); fora dela, depois de um
    envio, a substituição só vale até a Data Limite (E3 da US-15, E5 da US-29).
    [US-15][US-29][RBN-CAD-08.5][RBN-CAD-09.2][RBN-CAD-09.3][FR-019][FR-023 a FR-025]
    """
    marco = entrega.ent_tma
    if marco.tma_tipo == TipoEntrega.PROPOSTA:
        return False
    if services_turmas.turma_arquivada(marco.tma_tur):
        return False
    if tcc is None or services_turmas.participacao_encerrada(tcc):
        return False
    if marco.tma_tipo == TipoEntrega.VERSAO_FINAL:
        if tcc.tcc_status not in STATUS_TCC_LIBERA_VERSAO_FINAL:
            return False
        if entrega.ent_status == StatusEntrega.HOMOLOGADA:
            return False
    elif tcc.tcc_status != StatusTCC.EM_ANDAMENTO:
        return False
    if entrega.ent_status == StatusEntrega.DEVOLVIDA_PARA_AJUSTE:
        return True
    agora = agora or timezone.now()
    ja_enviou = HistoricoEnviosEntregas.objects.filter(hen_ent=entrega).exists()
    return not (ja_enviou and agora > marco.tma_data_limite)


def enviar_entrega(aluno, tma_id, link):
    """Envia ou substitui o link de uma entrega do Aluno (passos 4 a 7 e fluxo D da US-15;
    passos 5 a 7 e fluxos B, D e E da US-29): grava `Historico_Envios_Entregas` e recalcula
    `ent_status` a partir do **primeiro** envio, nunca do mais recente (FR-019) — "Entregue" se o
    primeiro envio ocorreu até 23:59 da Data Limite, "Entregue com Atraso" depois. No reenvio
    após a devolução para ajuste da Versão Final (FR-025), a referência passa a ser a data do
    próprio reenvio, já que o envio anterior foi devolvido.

    Trava `Entregas_Marcos` (a linha do aluno nesta entrega) **e** `TCCs` (o TCC do aluno nessa
    turma) antes de consultar o primeiro envio e de checar `tcc.tcc_status` (research C7, achado
    A1 da análise `/speckit-analyze`): sem essas travas, um duplo clique no "Enviar" poderia gerar
    duas transações lendo `Historico_Envios_Entregas` vazio ao mesmo tempo, e uma corrida com
    `encerrar_participacao`/`atualizar_status_tcc` (que travam turma → aluno → TCC) poderia deixar
    passar um envio com o Status já mudado no meio da requisição.

    Recusa com `Http404` (sem alterar nada), no mesmo padrão de `services_tcc.salvar_proposta` e
    de `services_turmas.encerrar_participacao` para uma ação cujo botão a view já esconde, se a
    entrega não existir para este aluno ou se `envio_liberado` não permitir. Notifica o Professor
    da Disciplina a cada envio e a cada substituição (MF-07, Q-85).
    [US-15][US-29][RBN-CAD-09.2][RBN-CAD-09.3][RBN-CAD-09.6][FR-018 a FR-021][FR-023 a FR-025]
    [research C7]
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
        turma = marco.tma_tur
        tcc = TCCs.objects.select_for_update().filter(tcc_alu=aluno, tcc_tur=turma).first()
        agora = timezone.now()
        if not envio_liberado(entrega, tcc, agora):
            raise Http404

        if entrega.ent_status == StatusEntrega.DEVOLVIDA_PARA_AJUSTE:
            referencia = agora
        else:
            primeiro_envio = (
                HistoricoEnviosEntregas.objects.filter(hen_ent=entrega)
                .order_by("hen_data_envio", "hen_id")
                .first()
            )
            referencia = primeiro_envio.hen_data_envio if primeiro_envio else agora
        HistoricoEnviosEntregas.objects.create(hen_ent=entrega, hen_link=link, hen_data_envio=agora)
        entrega.ent_status = (
            StatusEntrega.ENTREGUE
            if referencia <= marco.tma_data_limite
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
            # A notificação abre o acompanhamento da entrega (US-16) ou, na Versão Final, a tela
            # do aluno na seção Versão final (fluxo alternativo C da US-44).
            link=(
                reverse("cadastro:aluno_versao_final", args=[turma.pk, aluno.pk])
                if marco.tma_tipo == TipoEntrega.VERSAO_FINAL
                else reverse("cadastro:entrega_acompanhar", args=[turma.pk, marco.pk])
            ),
        )
    return entrega


def secao_versao_final(aluno, turma, tcc, agora=None):
    """Dados da seção "Versão final" da aba Meu TCC (passo 2 e fluxos B, C e E e exceções E3 a
    E7 da US-29), ou None quando a seção não aparece: turma de TCC 1 (E4) ou turma de TCC 2 sem a
    entrega do tipo Versão Final cadastrada para o aluno (pré-condição da US-29).

    Devolve: a entrega (`marco`) e o registro do aluno (`entrega`), o status exibido (`status`,
    com "Não Entregue" depois da Data Limite sem envio, fluxo C), o parecer liberado pela banca
    (`parecer`, lido do histórico do Status — gatilho "Liberação do resultado" — para continuar
    visível depois de "Concluído"), se o resultado ainda não foi liberado (`resultado_pendente`,
    E3, sem o campo Link), se o campo Link fica disponível (`pode_enviar`, `envio_liberado`), se
    o aviso MF-01 aparece (`aviso_atraso`: envio liberado depois da Data Limite, fluxo B), o
    envio mais recente (`ultimo_envio`, para o link somente leitura, E5/E6) e a mensagem da
    devolução para ajuste (`feedback`, fluxo E). Consulta sem gravação.
    [US-29][RBN-CAD-09.2][RBN-CAD-09.3][FR-023 a FR-025]
    """
    if turma.tur_descricao != DescricaoTurma.TCC_2 or tcc is None:
        return None
    entrega = (
        EntregasMarcos.objects.select_related("ent_tma__tma_tur")
        .filter(ent_alu=aluno, ent_tma__tma_tur=turma, ent_tma__tma_tipo=TipoEntrega.VERSAO_FINAL)
        .first()
    )
    if entrega is None:
        return None
    agora = agora or timezone.now()
    marco = entrega.ent_tma
    liberacao = (
        services_tcc.historico_do_status(tcc)
        .filter(hst_gatilho=GatilhoStatusTCC.LIBERACAO_DO_RESULTADO)
        .last()
    )
    pode_enviar = envio_liberado(entrega, tcc, agora)
    devolvida = entrega.ent_status == StatusEntrega.DEVOLVIDA_PARA_AJUSTE
    return {
        "marco": marco,
        "entrega": entrega,
        "status": status_exibido(entrega, agora),
        "parecer": liberacao.hst_status_novo if liberacao else None,
        "resultado_pendente": tcc.tcc_status in services_turmas.STATUS_TCC_EM_CURSO,
        "pode_enviar": pode_enviar,
        "aviso_atraso": pode_enviar and agora > marco.tma_data_limite,
        "ultimo_envio": link_mais_recente(entrega),
        "feedback": entrega.ent_feedback if devolvida else None,
    }


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
    não arquivada (fluxo alternativo E da US-15 original; FR-022), só de alunos ainda matriculados
    na turma (`Alunos_Turmas` atual) e com a participação não encerrada (regra das entregas do
    contrato de serviços, §3). Função pura, sem notificar: quem chama (o comando de gestão)
    decide o texto e envia (research C5).
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
    matriculado = AlunosTurmas.objects.filter(
        mat_alu=OuterRef("ent_alu"), mat_tur=OuterRef("ent_tma__tma_tur")
    )
    encerrado = TCCs.objects.filter(
        tcc_alu=OuterRef("ent_alu"),
        tcc_tur=OuterRef("ent_tma__tma_tur"),
        tcc_status__in=services_turmas.STATUS_PARTICIPACAO_ENCERRADA,
    )
    return (
        EntregasMarcos.objects.filter(
            janelas,
            ent_status=StatusEntrega.AGUARDANDO_ENVIO,
            ent_tma__tma_tur__tur_status=StatusTurma.ATIVA,
        )
        .filter(Exists(matriculado), ~Exists(encerrado))
        .select_related("ent_tma__tma_tur", "ent_alu__alu")
    )


def enviar_lembretes_de_prazo(agora=None):
    """Notifica cada aluno das `entregas_para_lembrar(agora)` com o lembrete de prazo (MF-08,
    PROVISÓRIA, Q-86), com o link para a janela da entrega. Chamada pelo comando de gestão
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
        # Lembrete também por e-mail (fluxo alternativo E da US-15; FR-022; MF-12, Q-84).
        _enviar_email_ao_aluno(usuario, mensagens.MF12_ASSUNTO_LEMBRETE_PRAZO, mensagem)
        enviados += 1
    return enviados


def marcar_nao_entregues(agora=None):
    """Grava "Não Entregue" nas entregas ainda "Aguardando Envio" cuja Data Limite (23:59) já
    passou, em turma não arquivada (fluxo alternativo C da US-15; FR-020; dicionário 18/10, seção
    4, item 7; Q-90). Não mexe no Status do TCC nem bloqueia o envio, que continua disponível e
    segue o fluxo B ("Entregue com Atraso"). Chamada pelo comando agendado
    `enviar_lembretes_entrega`; enquanto ele não roda, `status_exibido` mostra o mesmo valor.

    Um único UPDATE condicionado a "Aguardando Envio": se um envio travou e gravou a linha ao
    mesmo tempo, o PostgreSQL reconfere a condição depois da trava e não sobrescreve o envio.
    Devolve o número de registros marcados.
    [US-15][US-29][RBN-CAD-09.3][FR-020][Q-90]
    """
    agora = agora or timezone.now()
    return EntregasMarcos.objects.filter(
        ent_status=StatusEntrega.AGUARDANDO_ENVIO,
        ent_tma__tma_data_limite__lt=agora,
        ent_tma__tma_tur__tur_status=StatusTurma.ATIVA,
    ).update(ent_status=StatusEntrega.NAO_ENTREGUE)


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


# =============================================================================================
# Homologação ou devolução da Versão Final pelo Professor da Disciplina (US-44; FR-028 a FR-030)
# =============================================================================================

# Status de envio que mostram os botões Homologar e Devolver para Ajuste (pré-condição e E4 da
# US-44): a Versão Final enviada e ainda não avaliada (ou reenviada depois da devolução).
STATUS_ENVIO_AVALIAVEL = (StatusEntrega.ENTREGUE, StatusEntrega.ENTREGUE_COM_ATRASO)


def versao_final_do_aluno(turma, aluno, travar=False):
    """Registro do aluno na entrega do tipo Versão Final da turma, ou None. Com travar=True,
    chamar dentro de `transaction.atomic()` (trava a linha de `Entregas_Marcos`).
    [US-29][US-44][RBN-CAD-09.5]
    """
    registros = EntregasMarcos.objects.select_related("ent_tma")
    if travar:
        registros = registros.select_for_update(of=("self",))
    return registros.filter(
        ent_alu=aluno, ent_tma__tma_tur=turma, ent_tma__tma_tipo=TipoEntrega.VERSAO_FINAL
    ).first()


def exige_correcoes_conferidas(turma, tcc):
    """Sistemas de Informação com parecer "Aprovado com Correções" (FR-029): o Professor da
    Disciplina não é o Orientador e a homologação espera o Orientador acionar "Correções
    Conferidas" (spec 006). "Sistemas de Informação" é a turma de TCC 2 sem orientador
    automático (`turma_tem_orientador_automatico`, spec 004 — Engenharia de Computação e
    Licenciatura em Computação têm).
    [US-44][RBN-CAD-09.5][FR-029]
    """
    return (
        not services_turmas.turma_tem_orientador_automatico(turma)
        and tcc.tcc_status == StatusTCC.APROVADO_COM_CORRECOES
    )


def pode_devolver(entrega):
    """Devolver para Ajuste só com a Versão Final enviada e ainda não avaliada (E4; FR-030).

    [US-44][RBN-CAD-09.5][FR-028][FR-030]
    """
    return entrega is not None and entrega.ent_status in STATUS_ENVIO_AVALIAVEL


def pode_homologar(entrega, turma, tcc):
    """Homologar exige o envio ainda não avaliado (E4) e, em Sistemas de Informação com parecer
    "Aprovado com Correções", `ent_correcoes_conferidas_em` preenchido (E2; dicionário 3.4.2).
    [US-44][RBN-CAD-09.5][FR-028][FR-029][FR-030]
    """
    if not pode_devolver(entrega) or tcc is None:
        return False
    return not (
        exige_correcoes_conferidas(turma, tcc) and entrega.ent_correcoes_conferidas_em is None
    )


def _travar_versao_final(professor, tur_id, alu_id):
    """Trava turma → aluno → TCC → registro da Versão Final, nessa ordem (research C4), e
    confere a permissão: turma (404) → Professor da Disciplina (PermissionDenied) → turma
    arquivada (TurmaArquivada) → aluno matriculado (404) → turma de TCC 2 com a Versão Final
    cadastrada para o aluno (404). Chamar dentro de `transaction.atomic()`.
    [US-44][FR-028][FR-030][research C4][contracts/rotas.md]
    """
    turma = services_turmas.turma_para(professor, tur_id, services_turmas.ALTERAR, travar=True)
    aluno = services_turmas.vinculo_na_turma(turma, alu_id)
    Alunos.objects.select_for_update().filter(pk=aluno.pk).first()
    tcc = TCCs.objects.select_for_update().filter(tcc_alu=aluno, tcc_tur=turma).first()
    entrega = versao_final_do_aluno(turma, aluno, travar=True)
    if turma.tur_descricao != DescricaoTurma.TCC_2 or tcc is None or entrega is None:
        raise Http404
    return turma, aluno, tcc, entrega


def homologar_versao_final(professor, tur_id, alu_id):
    """Homologa a Versão Final (passos 5 a 7 da US-44): muda o status de envio para "Homologada"
    com a data e a hora (`ent_data_avaliacao`), o Status do TCC para "Concluído" pelo gatilho
    "Homologação da Versão Final" (registrando o Professor no histórico, FR-012) e notifica a
    Secretaria do curso (MF-09, PROVISÓRIA, Q-88). Recusa com `Http404` (botão escondido) se a
    Versão Final não foi enviada ou já foi avaliada, ou se faltam as "Correções Conferidas" em
    Sistemas de Informação (E2, E4); `PermissionDenied` para outro Docente (E5) e
    `TurmaArquivada` com a turma arquivada.
    [US-44][US-14][RBN-CAD-09.3][RBN-CAD-09.5][FR-028][FR-029][research C2][research C4]
    """
    with transaction.atomic():
        turma, aluno, tcc, entrega = _travar_versao_final(professor, tur_id, alu_id)
        if not pode_homologar(entrega, turma, tcc):
            raise Http404
        entrega.ent_status = StatusEntrega.HOMOLOGADA
        entrega.ent_data_avaliacao = timezone.now()
        entrega.save(update_fields=["ent_status", "ent_data_avaliacao"])
        services_turmas.atualizar_status_tcc(
            tcc,
            turma,
            professor,
            StatusTCC.CONCLUIDO,
            GatilhoStatusTCC.HOMOLOGACAO_DA_VERSAO_FINAL,
        )
        _registrar_avaliacao(
            EventoFluxoTCC.VERSAO_FINAL_HOMOLOGADA, aluno, professor, turma, entrega
        )
        secretarias = Secretarios.objects.select_related("sec").filter(
            sec_cur=turma.tur_cur, sec__usu_status=StatusConta.ATIVA
        )
        for secretaria in secretarias:
            notificar(
                secretaria.sec,
                mensagens.MF09_NOTIFICACAO_VERSAO_FINAL_HOMOLOGADA.format(
                    nome=aluno.alu.usu_nome, identificador=turma.tur_identificador
                ),
            )
    return entrega


def devolver_versao_final(professor, tur_id, alu_id, mensagem):
    """Devolve a Versão Final para ajuste (fluxo alternativo D da US-44): muda o status de envio
    para "Devolvida para Ajuste", grava a Mensagem (`ent_feedback`, já validada pelo formulário:
    obrigatória, até 500 caracteres) e a data e a hora (`ent_data_avaliacao`) e notifica o Aluno
    com a mensagem, para reenviar (MF-10, PROVISÓRIA, Q-88; link para a aba Meu TCC). O Status do
    TCC não muda. Mesmas recusas de `homologar_versao_final`, exceto a das "Correções
    Conferidas", que só bloqueia a homologação (E2).
    [US-44][US-29][RBN-CAD-09.3][RBN-CAD-09.5][FR-025][FR-028][research C4]
    """
    with transaction.atomic():
        turma, aluno, _tcc, entrega = _travar_versao_final(professor, tur_id, alu_id)
        if not pode_devolver(entrega):
            raise Http404
        entrega.ent_status = StatusEntrega.DEVOLVIDA_PARA_AJUSTE
        entrega.ent_feedback = mensagem
        entrega.ent_data_avaliacao = timezone.now()
        entrega.save(update_fields=["ent_status", "ent_feedback", "ent_data_avaliacao"])
        _registrar_avaliacao(
            EventoFluxoTCC.VERSAO_FINAL_DEVOLVIDA, aluno, professor, turma, entrega
        )
        notificar(
            aluno.alu,
            mensagens.MF10_NOTIFICACAO_VERSAO_FINAL_DEVOLVIDA.format(
                identificador=turma.tur_identificador, mensagem=mensagem
            ),
            link=reverse("cadastro:meu_tcc", args=[turma.pk]),
        )
    return entrega
