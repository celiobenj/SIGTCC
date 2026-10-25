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
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services_entregas, services_tcc, services_turmas
from sigtcc.apps.cadastro.choices import DescricaoTurma, StatusEntrega, StatusTCC, TipoEntrega
from sigtcc.apps.cadastro.forms_entregas import (
    CadastroEntregaForm,
    DevolverParaAjusteForm,
    EnviarLinkForm,
)
from sigtcc.apps.cadastro.models import EntregasMarcos, TurmasMarcos
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
        "nenhuma_entrega": mensagens.NENHUMA_ENTREGA_CADASTRADA,
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


@perfil_requerido("docente")
def entrega_acompanhar(request, tur_id, tma_id):
    """Janela de acompanhamento da entrega (passos 4 a 7 e fluxos A a D da US-16): Título, Data
    Limite, Instruções e a tabela somente leitura, uma linha por aluno, com Status de envio e o
    link mais recente — ou, no tipo Proposta, "Ver Proposta" (a Proposta do aluno, somente
    leitura; o Resumo só aparece se `pode_ver_resumo` autorizar, FR-007a). Restrita ao Professor
    da Disciplina da turma (E2), também com a turma arquivada (fluxo D, só consulta).
    [US-16][RBN-CAD-09.4][FR-007a][FR-026][FR-027][contracts/rotas.md]
    """
    turma = _turma_do_professor_da_disciplina(request.user, tur_id)
    marco = TurmasMarcos.objects.filter(pk=tma_id, tma_tur=turma).first()
    if marco is None:
        raise Http404
    eh_proposta = marco.tma_tipo == TipoEntrega.PROPOSTA
    linhas = services_entregas.acompanhamento_entrega(marco.pk)
    for linha in linhas:
        tcc = linha["tcc"]
        linha["ver_resumo"] = tcc is not None and services_tcc.pode_ver_resumo(request.user, tcc)
        linha["proposta_salva"] = tcc is not None and tcc.tcc_status != StatusTCC.SEM_PROPOSTA
    contexto = {
        "turma": turma,
        "marco": marco,
        "eh_proposta": eh_proposta,
        "eh_versao_final": marco.tma_tipo == TipoEntrega.VERSAO_FINAL,
        "linhas": linhas,
        "arquivada": services_turmas.turma_arquivada(turma),
    }
    return render(request, "cadastro/tcc/acompanhamento_entrega.html", contexto)


# =============================================================================================
# Envio e substituição do link pelo Aluno (US-15; FR-018 a FR-023; contracts/rotas.md)
# =============================================================================================


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
    contexto = {
        "turma": turma,
        "linhas": linhas,
        "arquivada": arquivada,
        # Texto exato da US (SC-006), sem ponto final. [US-15][US-16][SC-006]
        "nenhuma_entrega": mensagens.NENHUMA_ENTREGA_CADASTRADA,
    }
    return render(request, "cadastro/tcc/minhas_entregas.html", contexto)


@perfil_requerido("aluno")
def entrega_enviar(request, tur_id, tma_id):
    """Janela da entrega (passos 3 a 7 e fluxo D da US-15; passos 5 a 7 e fluxos B, D e E da
    US-29): GET abre com o status atual e, quando permitido, o campo Link e o botão Enviar; POST
    chama `services_entregas.enviar_entrega`. Quem decide se o campo aparece é a mesma regra que
    o serviço confere de novo antes de gravar (`services_entregas.envio_liberado`, SC-004). Na
    entrega do tipo Proposta, sem campo de link (fluxo F: `ENTREGA_CUMPRIDA_PROPOSTA`). Na Versão
    Final, o envio volta à aba Meu TCC com "Versão Final enviada" (passo 7 da US-29); nas
    demais, à aba Atividades com "Entrega enviada". Restrita ao próprio Aluno da turma, dono da
    entrega (sem IDOR).
    [US-15][US-29][RBN-CAD-09.2][RBN-CAD-09.3][FR-018 a FR-025][contracts/rotas.md]
    """
    turma, aluno = services_tcc.turma_do_aluno(tur_id, request.user)
    entrega = (
        EntregasMarcos.objects.select_related("ent_tma__tma_tur")
        .filter(ent_tma_id=tma_id, ent_alu=aluno, ent_tma__tma_tur=turma)
        .first()
    )
    if entrega is None:
        raise Http404
    marco = entrega.ent_tma
    tcc = services_turmas.tcc_do_aluno(turma, aluno)
    eh_proposta = marco.tma_tipo == TipoEntrega.PROPOSTA
    eh_versao_final = marco.tma_tipo == TipoEntrega.VERSAO_FINAL
    agora = timezone.now()
    pode_enviar = services_entregas.envio_liberado(entrega, tcc, agora)

    ultimo_envio = services_entregas.link_mais_recente(entrega)
    # Campo Link preenchido com o link mais recente, pronto para ser substituído (US-15 e US-29,
    # fluxo D: "substitui o endereço no campo Link"; FR-019). [US-15][US-29][FR-019]
    formulario = EnviarLinkForm(
        request.POST if request.method == "POST" and pode_enviar else None,
        initial={"link": ultimo_envio.hen_link if ultimo_envio else ""},
    )
    if request.method == "POST" and pode_enviar and formulario.is_valid():
        services_entregas.enviar_entrega(aluno, tma_id, formulario.cleaned_data["link"])
        if eh_versao_final:
            messages.success(request, mensagens.VERSAO_FINAL_ENVIADA)
            return redirect("cadastro:meu_tcc", tur_id=tur_id)
        messages.success(request, mensagens.ENTREGA_ENVIADA)
        return redirect("cadastro:minhas_entregas", tur_id=tur_id)

    devolvida = entrega.ent_status == StatusEntrega.DEVOLVIDA_PARA_AJUSTE
    contexto = {
        "turma": turma,
        "entrega": entrega,
        "marco": marco,
        "status": services_entregas.status_exibido(entrega, agora),
        "eh_proposta": eh_proposta,
        "pode_enviar": pode_enviar,
        # Aviso MF-01 (fluxo B da US-29): Versão Final com o envio liberado depois da Data Limite.
        "aviso_atraso": eh_versao_final and pode_enviar and agora > marco.tma_data_limite,
        "aviso_atraso_texto": mensagens.MF01_DATA_LIMITE_VENCIDA,
        "feedback": entrega.ent_feedback if devolvida else None,
        "ultimo_link": ultimo_envio.hen_link if ultimo_envio else "",
        "form": formulario,
    }
    return render(request, "cadastro/tcc/enviar_entrega.html", contexto)


# =============================================================================================
# Homologação ou devolução da Versão Final (US-44; FR-028 a FR-030; contracts/rotas.md)
# =============================================================================================


@perfil_requerido("docente")
@trata_turma_arquivada
def aluno_versao_final(request, tur_id, alu_id):
    """Tela do aluno, seção Versão final (passos 2 a 7, fluxos C e D e exceções da US-44): GET
    mostra o link enviado, a data e a hora, o status e, quando permitidos, os botões Homologar
    (`pode_homologar`: E2 e E4) e Devolver para Ajuste com o campo Mensagem (`pode_devolver`:
    E4); POST homologa ou devolve e mantém o Professor nesta tela, com "Versão Final
    homologada" ou a MF-02. Restrita ao Professor da Disciplina da turma de TCC 2 (E5: 403 para
    outro Docente e para a Secretaria; turma de TCC 1 ou sem Versão Final: 404). Turma
    arquivada: consulta sem botões e, numa ação pelo endereço direto, a MT-25.
    [US-44][RBN-CAD-09.3][RBN-CAD-09.5][FR-028 a FR-030][contracts/rotas.md]
    """
    turma = _turma_do_professor_da_disciplina(request.user, tur_id)
    aluno = services_turmas.vinculo_na_turma(turma, alu_id)
    tcc = services_turmas.tcc_do_aluno(turma, aluno)
    entrega = services_entregas.versao_final_do_aluno(turma, aluno)
    if turma.tur_descricao != DescricaoTurma.TCC_2 or tcc is None or entrega is None:
        raise Http404
    arquivada = services_turmas.turma_arquivada(turma)
    formulario = DevolverParaAjusteForm()

    if request.method == "POST":
        acao = request.POST.get("acao")
        if acao == "homologar":
            services_entregas.homologar_versao_final(request.user, tur_id, alu_id)
            messages.success(request, mensagens.VERSAO_FINAL_HOMOLOGADA)
            return _voltar_versao_final(request, tur_id, alu_id)
        if acao == "devolver":
            formulario = DevolverParaAjusteForm(request.POST)
            if formulario.is_valid():
                services_entregas.devolver_versao_final(
                    request.user, tur_id, alu_id, formulario.cleaned_data["mensagem"]
                )
                messages.success(request, mensagens.MF02_VERSAO_FINAL_DEVOLVIDA)
                return _voltar_versao_final(request, tur_id, alu_id)
            # Ação pelo endereço direto em turma arquivada: MT-25 antes de mostrar o erro.
            services_turmas.exigir_turma_ativa(turma)

    envio = services_entregas.link_mais_recente(entrega)
    contexto = {
        "turma": turma,
        "aluno": aluno,
        "tcc": tcc,
        "entrega": entrega,
        "marco": entrega.ent_tma,
        "status": services_entregas.status_exibido(entrega),
        "envio": envio,
        "arquivada": arquivada,
        "pode_homologar": not arquivada and services_entregas.pode_homologar(entrega, turma, tcc),
        "pode_devolver": not arquivada and services_entregas.pode_devolver(entrega),
        "aguarda_correcoes": services_entregas.pode_devolver(entrega)
        and services_entregas.exige_correcoes_conferidas(turma, tcc)
        and entrega.ent_correcoes_conferidas_em is None,
        "form": formulario,
        # Spec 006 (IC-07; FR-044): aberta pelo painel, "Voltar" ao painel.
        "url_painel": (
            reverse("cadastro:painel_aluno", args=[tur_id, alu_id])
            if request.GET.get("volta") == "painel"
            else ""
        ),
    }
    return render(request, "cadastro/tcc/homologar_versao_final.html", contexto)


def _voltar_versao_final(request, tur_id, alu_id):
    """Depois de Homologar ou Devolver: ao painel do aluno com `?volta=painel` (spec 006, IC-07;
    research R5), senão à própria tela, como antes. [US-44][FR-044][IC-07]
    """
    if request.GET.get("volta") == "painel":
        return redirect("cadastro:painel_aluno", tur_id=tur_id, alu_id=alu_id)
    return redirect("cadastro:aluno_versao_final", tur_id=tur_id, alu_id=alu_id)
