"""Views da aba Atividades do app cadastro (spec 005).

Views finas (orquestram `services_entregas`, sem regra de negócio): cadastro de entregas e
acompanhamento pelo Professor da Disciplina (US-43, US-16); envio e substituição de link pelo
Aluno (US-15, US-29); homologação ou devolução para ajuste da Versão Final (US-44).

[US-15][US-16][US-29][US-43][US-44][RBN-CAD-09.1 a 09.6][research C1]
"""

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services_entregas, services_tcc, services_turmas
from sigtcc.apps.cadastro.choices import StatusTCC, TipoEntrega
from sigtcc.apps.cadastro.forms_entregas import CadastroEntregaForm, EnviarLinkForm
from sigtcc.apps.cadastro.models import EntregasMarcos, HistoricoEnviosEntregas, TurmasMarcos
from sigtcc.apps.cadastro.permissoes import perfil_requerido
from sigtcc.apps.cadastro.services_turmas import ALTERAR, CONSULTAR
from sigtcc.apps.cadastro.views_turmas import trata_turma_arquivada


def _turma_do_professor_da_disciplina(usuario, tur_id):
    """Turma pela permissão de consulta (404 → 403), restrita ao Professor da Disciplina desta
    turma — nunca a Secretaria, mesmo arquivada (contracts/rotas.md: Acesso "Professor da
    Disciplina", sem "ou Secretaria", diferente da consulta comum da turma, spec 004 Q9). Mesmo
    padrão de `views_tcc.historico_status`.
    [US-43][FR-017][contracts/rotas.md]
    """
    turma = services_turmas.turma_para(usuario, tur_id, CONSULTAR)
    if turma.tur_doc_id != usuario.pk:
        raise PermissionDenied
    return turma


@perfil_requerido("docente")
def entregas(request, tur_id):
    """Aba Atividades (lista): entregas já cadastradas e o botão "Cadastrar atividade", visível
    só com a turma ativa (E4/E5 da US-43 original; Cenário 5 do `spec.md`).

    [US-43][FR-013][FR-014][FR-017][contracts/rotas.md]
    """
    turma = _turma_do_professor_da_disciplina(request.user, tur_id)
    arquivada = services_turmas.turma_arquivada(turma)
    contexto = {
        "turma": turma,
        "entregas": TurmasMarcos.objects.filter(tma_tur=turma).order_by("tma_data_limite"),
        "arquivada": arquivada,
        "pode_cadastrar": not arquivada,
    }
    return render(request, "cadastro/tcc/entregas.html", contexto)


@perfil_requerido("docente")
@trata_turma_arquivada
def entrega_cadastrar(request, tur_id):
    """Janela "Cadastrar atividade" (passos 3 a 8 da US-43 original): GET abre o formulário,
    com Cancelar (nenhuma entrega é criada) e Cadastrar; POST chama
    `services_entregas.cadastrar_entrega`.

    [US-43][RBN-CAD-09.1][RBN-CAD-09.6][FR-013 a FR-017][contracts/rotas.md]
    """
    turma = services_turmas.turma_para(request.user, tur_id, ALTERAR)
    formulario = CadastroEntregaForm(
        request.POST if request.method == "POST" else None, turma=turma
    )
    if request.method == "POST" and formulario.is_valid():
        try:
            services_entregas.cadastrar_entrega(request.user, tur_id, formulario.cleaned_data)
        except services_entregas.ErroEntrega as erro:
            formulario.add_error(erro.campo, erro.mensagem)
        else:
            messages.success(request, mensagens.ENTREGA_CADASTRADA)
            return redirect("cadastro:entregas", tur_id=tur_id)
    contexto = {"form": formulario, "turma": turma}
    return render(request, "cadastro/tcc/form_entrega.html", contexto)


# =============================================================================================
# Envio e substituição do link pelo Aluno (US-15; FR-018 a FR-023; contracts/rotas.md)
# =============================================================================================


def _pode_enviar(entrega, marco, turma, tcc):
    """Replica, só para decidir se o botão Enviar aparece, as mesmas condições que
    `services_entregas.enviar_entrega` confere de novo antes de gravar (SC-004, mesmo padrão da
    spec 004: o serviço confere de novo, inclusive pelo endereço direto).
    [US-15][RBN-CAD-09.2][RBN-CAD-08.5][FR-023][contracts/rotas.md]
    """
    if marco.tma_tipo in (TipoEntrega.PROPOSTA, TipoEntrega.VERSAO_FINAL):
        return False
    if services_turmas.turma_arquivada(turma):
        return False
    if tcc is None or services_turmas.participacao_encerrada(tcc):
        return False
    if tcc.tcc_status != StatusTCC.EM_ANDAMENTO:
        return False
    ja_enviou = HistoricoEnviosEntregas.objects.filter(hen_ent=entrega).exists()
    if ja_enviou and timezone.now() > marco.tma_data_limite:
        return False
    return True


@perfil_requerido("aluno")
def minhas_entregas(request, tur_id):
    """Aba Atividades (passos 1 a 2 da US-15 original): lista das entregas da turma do próprio
    Aluno, com Título, Data Limite e o status de envio (FR-020: "Não Entregue" calculado na
    exibição quando a Data Limite já passou sem envio, sem gravar nada). Restrita ao próprio
    Aluno da turma (`turma_do_aluno`, sem IDOR).
    [US-15][RBN-CAD-09.2][RBN-CAD-09.3][FR-018 a FR-020][contracts/rotas.md]
    """
    turma, aluno = services_tcc.turma_do_aluno(tur_id, request.user)
    arquivada = services_turmas.turma_arquivada(turma)
    entregas = (
        EntregasMarcos.objects.filter(ent_alu=aluno, ent_tma__tma_tur=turma)
        .select_related("ent_tma")
        .order_by("ent_tma__tma_data_limite")
    )
    linhas = [
        {"entrega": entrega, "status": services_entregas.status_exibido(entrega)}
        for entrega in entregas
    ]
    contexto = {"turma": turma, "linhas": linhas, "arquivada": arquivada}
    return render(request, "cadastro/tcc/minhas_entregas.html", contexto)


@perfil_requerido("aluno")
def entrega_enviar(request, tur_id, tma_id):
    """Janela da entrega (passos 3 a 7 e fluxo D da US-15 original): GET abre com o status atual
    e, quando permitido, o campo Link e o botão Enviar; POST chama
    `services_entregas.enviar_entrega`. Na entrega do tipo Proposta, sem campo de link (fluxo F:
    `ENTREGA_CUMPRIDA_PROPOSTA`). Restrita ao próprio Aluno da turma, dono da entrega (sem IDOR).
    [US-15][RBN-CAD-09.2][RBN-CAD-09.3][FR-018 a FR-023][contracts/rotas.md]
    """
    turma, aluno = services_tcc.turma_do_aluno(tur_id, request.user)
    entrega = EntregasMarcos.objects.select_related("ent_tma").filter(
        ent_tma_id=tma_id, ent_alu=aluno, ent_tma__tma_tur=turma
    ).first()
    if entrega is None:
        raise Http404
    marco = entrega.ent_tma
    tcc = services_turmas.tcc_do_aluno(turma, aluno)
    eh_proposta = marco.tma_tipo == TipoEntrega.PROPOSTA
    pode_enviar = _pode_enviar(entrega, marco, turma, tcc)

    formulario = EnviarLinkForm(
        request.POST if request.method == "POST" and pode_enviar else None
    )
    if request.method == "POST" and pode_enviar and formulario.is_valid():
        services_entregas.enviar_entrega(aluno, tma_id, formulario.cleaned_data["link"])
        messages.success(request, mensagens.ENTREGA_ENVIADA)
        return redirect("cadastro:minhas_entregas", tur_id=tur_id)

    ultimo_envio = (
        HistoricoEnviosEntregas.objects.filter(hen_ent=entrega).order_by("-hen_data_envio").first()
    )
    contexto = {
        "turma": turma,
        "entrega": entrega,
        "marco": marco,
        "status": services_entregas.status_exibido(entrega),
        "eh_proposta": eh_proposta,
        "pode_enviar": pode_enviar,
        "ultimo_link": ultimo_envio.hen_link if ultimo_envio else "",
        "form": formulario,
    }
    return render(request, "cadastro/tcc/enviar_entrega.html", contexto)
