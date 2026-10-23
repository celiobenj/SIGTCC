"""Regras da Proposta, dos dados do TCC e do Status/histórico/trilha do app cadastro (spec 005).

Domínio `TCCs`/`Historico_Status_TCC`: Proposta e dados do TCC com mudança de tema (US-13);
confidencialidade do Resumo (FR-007a); consulta do histórico e da trilha do Status, sem checagem
de perfil (US-14, research C9). Este módulo importa `services_turmas` (que expõe o serviço único
de gravação do Status, `criar_tcc_com_historico`/`atualizar_status_tcc`, FR-012), nunca o
contrário.

[US-13][US-14][RBN-CAD-07.1][RBN-CAD-08.1][RBN-CAD-08.2][RBN-CAD-08.3][RBN-CAD-08.7][RBN-CAD-08.8]
[research C1][research C3][research C9]
"""

from django.db import IntegrityError, transaction
from django.http import Http404
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services_turmas
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    GatilhoStatusTCC,
    StatusCoorientacao,
    StatusEntrega,
    StatusOrientacao,
    StatusTCC,
    TipoEntrega,
    TipoSolicitacao,
)
from sigtcc.apps.cadastro.models import (
    Coorientacoes,
    EntregasMarcos,
    HistoricoStatusTCC,
    Orientacoes,
    PalavrasChaveTCC,
    SolicitacoesOrientacao,
    TCCs,
    Turmas,
    TurmasMarcos,
)
from sigtcc.apps.cadastro.services import notificar
from sigtcc.apps.cadastro.services_turmas import STATUS_SOLICITACAO_PENDENTE, vinculo_na_turma

# Campos da Proposta (mudança de tema, FR-005) — usados para decidir se o Orientador é notificado
# e para gravar a Proposta em salvar_proposta/salvar_alteracoes_tcc. [US-13][RBN-CAD-08.2]
_CAMPOS_TEMA = {
    "titulo": "tcc_titulo",
    "subtitulo": "tcc_subtitulo",
    "resumo": "tcc_resumo",
    "modalidade": "tcc_modalidade",
    "link": "tcc_link_proposta",
}

MAXIMO_PALAVRAS_CHAVE = 5


class ErroTCC(Exception):
    """Recusa de uma ação sobre o TCC com a mensagem exata e, se houver, o campo a destacar.

    [US-13][FR-007][research C3]
    """

    def __init__(self, mensagem, campo=None):
        """Guarda a mensagem exata e o campo. [FR-007]"""
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.campo = campo


def pode_ver_resumo(usuario, tcc):
    """O Resumo da Proposta (tcc_resumo) só é visível a quem a FR-007a autoriza (RAN-CAD-07 NFR
    de Confidencialidade; research C3): o próprio Aluno dono do TCC, o Orientador **atual**
    (`Orientacoes.ori_status='Ativa'`), um Docente com `Solicitacoes_Orientacao` de Orientação
    ainda pendente para esse TCC, o Coorientador do NUCOMP **com coorientação aceita**
    (`Coorientacoes.coo_status='Ativa'`, só `coo_doc`, nunca `coo_cext`) ou o Professor da
    Disciplina da turma do TCC. Qualquer outro Docente (inclusive sem vínculo) recebe False.

    Única forma permitida de decidir essa visibilidade (contrato `servicos-compartilhados.md`,
    §1): toda view desta spec, da spec 006 ou do Épico 3 que exiba `tcc_resumo` MUST chamar esta
    função antes, nunca reimplementar a regra.
    [US-13][RAN-CAD-07][FR-007a][research C3]
    """
    if usuario is None or not getattr(usuario, "is_authenticated", False):
        return False
    if tcc.tcc_alu_id == usuario.pk:
        return True
    if Orientacoes.objects.filter(
        ori_tcc=tcc, ori_status=StatusOrientacao.ATIVA, ori_doc_id=usuario.pk
    ).exists():
        return True
    # Só o pedido de Orientação (TipoSolicitacao.ORIENTACAO); a Coorientação tem regra própria,
    # abaixo, com coo_status='Ativa' (Coorientador do NUCOMP sem coorientação aceita não vê).
    if SolicitacoesOrientacao.objects.filter(
        sol_tcc=tcc,
        sol_doc_id=usuario.pk,
        sol_tipo=TipoSolicitacao.ORIENTACAO,
        sol_status__in=STATUS_SOLICITACAO_PENDENTE,
    ).exists():
        return True
    if Coorientacoes.objects.filter(
        coo_tcc=tcc, coo_status=StatusCoorientacao.ATIVA, coo_doc_id=usuario.pk
    ).exists():
        return True
    if tcc.tcc_tur.tur_doc_id == usuario.pk:
        return True
    return False


def historico_do_status(tcc):
    """Todas as linhas do histórico do Status deste TCC, da mais antiga à mais recente (mesmo
    dado usado pela trilha do FR-010), **sem nenhuma checagem de perfil** — quem chama decide se
    autoriza (research C9; contrato `servicos-compartilhados.md`, §2). A view desta spec aplica a
    checagem (Aluno dono, Orientador atual, Professor da Disciplina — nunca Secretaria nem
    Coorientador) antes de chamar; a spec 006 (tela de orientandos) chama direto, com a própria
    checagem (Orientador do TCC) por fora.
    [US-14][RBN-CAD-08.7][FR-009][FR-010][research C9]
    """
    return HistoricoStatusTCC.objects.filter(hst_tcc=tcc).order_by("hst_data_hora", "hst_id")


# Sequências fixas da trilha do Status (FR-010), sem os gatilhos de encerramento — esses entram
# só quando o Status atual for um deles, truncando a sequência no ponto em que ocorreram.
_TRILHA_TCC_1 = (StatusTCC.EM_ANDAMENTO, StatusTCC.APTO_PARA_DEFESA, StatusTCC.APROVADO_PARA_TCC_2)


def trilha_do_status(tcc):
    """Trilha do Status do TCC, com a etapa atual destacada (FR-010): em TCC 1, Em Andamento →
    Apto para Defesa → Aprovado para TCC 2; em TCC 2, Em Andamento → Apto para Defesa → (Aprovado
    ou Aprovado com Correções, conforme o que de fato ocorreu) → Concluído. Com o Status
    "Reprovado", "Desistente" ou "Jubilado", a trilha termina na etapa em que ocorreu (lida do
    histórico, FR-009), sem as etapas seguintes do ciclo normal.

    Devolve uma lista de dicionários `{"status": StatusTCC, "atual": bool}`, na ordem de
    exibição. Usa `tcc.tcc_tur.tur_descricao` para decidir entre a trilha de TCC 1 e a de TCC 2
    (`DescricaoTurma.TCC_1`/`TCC_2`, spec 004).
    [US-14][RBN-CAD-08.8][FR-010]
    """
    if tcc.tcc_tur.tur_descricao == DescricaoTurma.TCC_2:
        passou_por_correcoes = (
            tcc.tcc_status == StatusTCC.APROVADO_COM_CORRECOES
            or historico_do_status(tcc)
            .filter(hst_status_novo=StatusTCC.APROVADO_COM_CORRECOES)
            .exists()
        )
        etapa_aprovacao = (
            StatusTCC.APROVADO_COM_CORRECOES if passou_por_correcoes else StatusTCC.APROVADO
        )
        sequencia = [
            StatusTCC.EM_ANDAMENTO,
            StatusTCC.APTO_PARA_DEFESA,
            etapa_aprovacao,
            StatusTCC.CONCLUIDO,
        ]
    else:
        sequencia = list(_TRILHA_TCC_1)

    status_atual = tcc.tcc_status
    if status_atual in services_turmas.STATUS_PARTICIPACAO_ENCERRADA:
        ultima_mudanca = historico_do_status(tcc).last()
        anterior = ultima_mudanca.hst_status_anterior if ultima_mudanca is not None else None
        if anterior in sequencia:
            sequencia = sequencia[: sequencia.index(anterior) + 1]
        else:
            sequencia = []
        sequencia.append(status_atual)

    return [{"status": status, "atual": status == status_atual} for status in sequencia]


# =============================================================================================
# Proposta e dados do TCC (US-13; FR-001 a FR-007a; research C2, C3, C4)
# =============================================================================================


def turma_do_aluno(tur_id, usuario):
    """Turma (404) e o próprio Aluno matriculado nela (404, sem IDOR pelo alu_id): as rotas do
    Aluno desta spec (`meu_tcc`, `minhas_entregas`) não passam por `services_turmas.turma_para`,
    que só libera para o Professor da Disciplina ou a Secretaria (`contracts/rotas.md`).
    [US-13][contracts/rotas.md]
    """
    turma = Turmas.objects.select_related("tur_cur", "tur_dis").filter(pk=tur_id).first()
    if turma is None:
        raise Http404
    aluno = vinculo_na_turma(turma, usuario.pk)
    return turma, aluno


def palavras_chave_do(tcc):
    """Palavras-Chave do TCC, em ordem alfabética (consulta simples, sem regra). [US-13][FR-004]"""
    return list(
        PalavrasChaveTCC.objects.filter(pal_tcc=tcc)
        .order_by("pal_palavra")
        .values_list("pal_palavra", flat=True)
    )


def _cumprir_entrega_proposta(aluno, turma, quando):
    """Cumpre a entrega do tipo Proposta da turma, se existir, com o status calculado pela data
    do salvamento: "Entregue" até a Data Limite (23:59), "Entregue com Atraso" depois (FR-003).
    [US-13][RBN-CAD-07.1][RBN-CAD-09.1][RBN-CAD-09.3][FR-003]
    """
    entrega = TurmasMarcos.objects.filter(tma_tur=turma, tma_tipo=TipoEntrega.PROPOSTA).first()
    if entrega is None:
        return
    status = (
        StatusEntrega.ENTREGUE
        if quando <= entrega.tma_data_limite
        else StatusEntrega.ENTREGUE_COM_ATRASO
    )
    registro, criado = EntregasMarcos.objects.get_or_create(
        ent_tma=entrega, ent_alu=aluno, defaults={"ent_status": status}
    )
    if not criado:
        registro.ent_status = status
        registro.save(update_fields=["ent_status"])


def salvar_proposta(aluno, tur_id, dados):
    """Primeira Proposta do Aluno na turma (FR-002): só quando o TCC estiver "Sem Proposta" (e,
    pela `UNIQUE (tcc_alu, tcc_tur)`, ainda sem Proposta nela); grava Título, Subtítulo, Resumo,
    Modalidade e Link, muda o Status para "Em Andamento" (gatilho "Proposta salva") e cumpre a
    entrega do tipo Proposta, se existir (FR-003). A turma e o TCC são travados antes de ler o
    Status, na ordem turma → aluno → TCC (research C2, C4).
    [US-13][RBN-CAD-07.1][RBN-CAD-08.1][RBN-CAD-08.2][FR-001]-[FR-003][research C2][research C3]
    """
    with transaction.atomic():
        turma = services_turmas.travar_turma_ativa(tur_id)
        tcc = TCCs.objects.select_for_update().filter(tcc_alu=aluno, tcc_tur=turma).first()
        if tcc is None or tcc.tcc_status != StatusTCC.SEM_PROPOSTA:
            # Botão "Salvar Proposta" só aparece nesse Status (view); acesso direto fora dele
            # (corrida ou endereço direto) não encontra o que fazer (mesmo padrão de B15/B17).
            raise Http404
        tcc.tcc_titulo = dados["titulo"]
        tcc.tcc_subtitulo = dados.get("subtitulo") or None
        tcc.tcc_resumo = dados["resumo"]
        tcc.tcc_modalidade = dados["modalidade"]
        tcc.tcc_link_proposta = dados.get("link") or None
        tcc.save(
            update_fields=[
                "tcc_titulo",
                "tcc_subtitulo",
                "tcc_resumo",
                "tcc_modalidade",
                "tcc_link_proposta",
            ]
        )
        services_turmas.atualizar_status_tcc(
            tcc, turma, aluno.alu, StatusTCC.EM_ANDAMENTO, GatilhoStatusTCC.PROPOSTA_SALVA
        )
        _cumprir_entrega_proposta(aluno, turma, timezone.now())
    return tcc


def salvar_alteracoes_tcc(tcc, dados):
    """Mudança de tema, Área de Interesse e Palavras-Chave, enquanto o TCC estiver "Em Andamento"
    (FR-004, FR-005): grava os campos da Proposta, apaga e recria as `PalavrasChave_TCC` (de 1 a
    5, sem repetir — já conferido pelo formulário; `IntegrityError` numa corrida de duplo clique
    vira MF-03, rede de segurança do research C3) e notifica o Orientador atual, se houver,
    quando algum campo de tema (Título, Subtítulo, Resumo, Modalidade ou Link) mudou. O TCC é
    travado antes da leitura (research C4); a gravação das Palavras-Chave usa um savepoint
    próprio (`transaction.atomic()` aninhado) para a captura de `IntegrityError` não invalidar a
    transação externa.
    [US-13][RBN-CAD-08.1][RBN-CAD-08.2][FR-004][FR-005][research C2][research C3][research C4]
    """
    with transaction.atomic():
        tcc = TCCs.objects.select_for_update().get(pk=tcc.pk)
        tema_mudou = any(
            getattr(tcc, campo_model) != (dados.get(campo_form) or None)
            for campo_form, campo_model in _CAMPOS_TEMA.items()
        )
        tcc.tcc_titulo = dados.get("titulo") or None
        tcc.tcc_subtitulo = dados.get("subtitulo") or None
        tcc.tcc_resumo = dados.get("resumo") or None
        tcc.tcc_modalidade = dados.get("modalidade") or None
        tcc.tcc_link_proposta = dados.get("link") or None
        tcc.tcc_ari = dados.get("area_interesse")
        tcc.save(
            update_fields=[
                "tcc_titulo",
                "tcc_subtitulo",
                "tcc_resumo",
                "tcc_modalidade",
                "tcc_link_proposta",
                "tcc_ari",
            ]
        )
        try:
            with transaction.atomic():
                PalavrasChaveTCC.objects.filter(pal_tcc=tcc).delete()
                for palavra in dados.get("palavras_chave", []):
                    PalavrasChaveTCC.objects.create(pal_tcc=tcc, pal_palavra=palavra)
        except IntegrityError:
            raise ErroTCC(mensagens.MF03_PALAVRA_CHAVE_REPETIDA)
        if tema_mudou:
            orientador = Orientacoes.objects.filter(
                ori_tcc=tcc, ori_status=StatusOrientacao.ATIVA
            ).first()
            if orientador is not None:
                notificar(
                    orientador.ori_doc.doc,
                    mensagens.MF04_NOTIFICACAO_MUDANCA_TEMA.format(
                        nome=tcc.tcc_alu.alu.usu_nome, identificador=tcc.tcc_tur.tur_identificador
                    ),
                )
    return tcc
