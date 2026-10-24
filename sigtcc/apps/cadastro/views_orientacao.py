"""Views de orientação (spec 006): seção Orientação do Aluno, tela Orientações do docente, links de
pedido e convite, Apto para Defesa e Correções Conferidas. Views finas: as regras ficam em
services_orientacao.

[US-17][US-18][US-36][US-42][US-45][research R1]
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from sigtcc.apps.cadastro import mensagens, services_orientacao, services_tcc, services_turmas
from sigtcc.apps.cadastro.choices import TipoSolicitacao
from sigtcc.apps.cadastro.forms_orientacao import CoorientadorForm
from sigtcc.apps.cadastro.permissoes import perfil_requerido
from sigtcc.apps.cadastro.services_turmas import TurmaArquivada


def _volta_secao(tur_id, secao="orientacao"):
    """Volta à aba Meu TCC já na seção (research R12; contracts/rotas.md §1). [FR-042]"""
    return redirect(f"{redirect('cadastro:meu_tcc', tur_id=tur_id).url}?secao={secao}")


# =============================================================================================
# Aluno: seção Orientação da aba Meu TCC (contracts/rotas.md §1, rotas 1 e 2)
# =============================================================================================


@require_POST
@perfil_requerido("aluno")
def enviar_pedido_orientacao(request, tur_id):
    """Rota 1: "Enviar pedido" (Indicar ou Trocar de orientador). Só o próprio Aluno da turma;
    a turma arquivada volta à seção com a MT-25 (research R2, A11).
    [US-17][RBN-CAD-10.1][RBN-CAD-10.6][FR-001 a FR-005][contracts/rotas.md]
    """
    doc_id = request.POST.get("docente") or ""
    if not doc_id.isdigit():
        messages.error(request, mensagens.M14_CAMPO_OBRIGATORIO)
        return _volta_secao(tur_id)
    try:
        pedido = services_orientacao.enviar_pedido(request.user, tur_id, int(doc_id))
    except TurmaArquivada:
        messages.warning(request, mensagens.MT25_TURMA_ARQUIVADA)
    except services_orientacao.ErroOrientacao as erro:
        messages.error(request, erro.mensagem)
    else:
        messages.success(
            request, mensagens.PEDIDO_ENVIADO.format(docente=pedido.sol_doc.doc.usu_nome)
        )
    return _volta_secao(tur_id)


@require_POST
@perfil_requerido("aluno")
def cancelar_pedido_orientacao(request, tur_id):
    """Rota 2: "Cancelar Pedido" do Aluno; a lista volta a ficar disponível (FR-004).

    [US-17][RBN-CAD-10.1][FR-004][contracts/rotas.md]
    """
    try:
        services_orientacao.cancelar_pedido(request.user, tur_id)
    except TurmaArquivada:
        messages.warning(request, mensagens.MT25_TURMA_ARQUIVADA)
    return _volta_secao(tur_id)


def _secao_tcc(request, tur_id):
    """TCC do próprio Aluno na turma, para as telas de coorientação (404 sem vínculo)."""
    turma, aluno = services_tcc.turma_do_aluno(tur_id, request.user)
    tcc = services_turmas.tcc_do_aluno(turma, aluno)
    if tcc is None:
        raise Http404
    return tcc


def _janela_coorientador(request, tur_id, coo_id=None):
    """Janela "Registrar coorientador" (FR-028), também usada no "Substituir" (FR-030; US-45 D);
    "Cancelar" e "Salvar" voltam à seção Orientação (FR-042).
    [US-45][RBN-CAD-10.3][RBN-CAD-10.7][FR-028][FR-030][FR-042]
    """
    tcc = _secao_tcc(request, tur_id)
    if services_turmas.turma_arquivada(tcc.tcc_tur):
        messages.warning(request, mensagens.MT25_TURMA_ARQUIVADA)
        return _volta_secao(tur_id)
    estado = services_orientacao.estado_coorientadores(tcc)
    if not estado["pode_registrar"] or (coo_id is not None and not estado["botoes_habilitados"]):
        raise Http404
    anterior = None
    if coo_id is not None:
        anterior = next(
            (c for c in services_orientacao.coorientadores_ativos(tcc) if c.pk == coo_id), None
        )
        if anterior is None:
            raise Http404
    docentes = [
        (d.pk, services_orientacao.rotulo_docente(d))
        for d in services_orientacao.docentes_para_coorientacao(tcc)
    ]
    formulario = CoorientadorForm(
        request.POST if request.method == "POST" else None, docentes=docentes
    )
    if request.method == "POST" and formulario.is_valid():
        try:
            aviso = services_orientacao.registrar_coorientador(
                request.user, tur_id, formulario.cleaned_data, coo_id=coo_id
            )
        except TurmaArquivada:
            messages.warning(request, mensagens.MT25_TURMA_ARQUIVADA)
            return _volta_secao(tur_id)
        except services_orientacao.ErroOrientacao as erro:
            formulario.add_error("email", erro.mensagem)
        else:
            if aviso:
                messages.info(request, aviso)
            return _volta_secao(tur_id)
    contexto = {
        "tcc": tcc,
        "form": formulario,
        "anterior": anterior,
        "titulo": "Substituir coorientador" if anterior else "Registrar coorientador",
        "url_cancelar": services_orientacao.link_secao(tcc, "orientacao"),
    }
    return render(request, "cadastro/orientacao/form_coorientador.html", contexto)


@perfil_requerido("aluno")
def registrar_coorientador(request, tur_id):
    """Rota 3: "Registrar coorientador". [US-45][RBN-CAD-10.3][FR-028][contracts/rotas.md]"""
    return _janela_coorientador(request, tur_id)


@perfil_requerido("aluno")
def substituir_coorientador(request, tur_id, coo_id):
    """Rota 4: "Substituir" (a coorientação buscada pelo TCC do aluno; research R10).

    [US-45 D][RBN-CAD-10.7][FR-030][contracts/rotas.md]
    """
    return _janela_coorientador(request, tur_id, coo_id)


def _confirmar_remocao(request, tur_id, nome, servico):
    """Confirmação MO-14 (GET) e remoção (POST), voltando à seção Orientação (FR-042)."""
    tcc = _secao_tcc(request, tur_id)
    if request.method == "POST":
        try:
            servico()
        except TurmaArquivada:
            messages.warning(request, mensagens.MT25_TURMA_ARQUIVADA)
        return _volta_secao(tur_id)
    contexto = {
        "titulo": "Remover",
        "texto": mensagens.MO14_CONFIRMAR_REMOVER.format(nome=nome),
        "url_acao": request.path,
        "url_cancelar": services_orientacao.link_secao(tcc, "orientacao"),
    }
    return render(request, "cadastro/orientacao/confirmar.html", contexto)


@perfil_requerido("aluno")
def remover_coorientador(request, tur_id, coo_id):
    """Rota 5: "Remover" coorientador, com confirmação (MO-14). [US-45 E][FR-030]"""
    tcc = _secao_tcc(request, tur_id)
    coo = next((c for c in services_orientacao.coorientadores_ativos(tcc) if c.pk == coo_id), None)
    estado = services_orientacao.estado_coorientadores(tcc)
    if coo is None or not estado["mostra_botoes"] or not estado["botoes_habilitados"]:
        raise Http404
    return _confirmar_remocao(
        request,
        tur_id,
        services_orientacao.nome_do_coorientador(coo),
        lambda: services_orientacao.remover_coorientador(request.user, tur_id, coo_id),
    )


@perfil_requerido("aluno")
def remover_convite_coorientacao(request, tur_id, sol_id):
    """Rota 6: "Remover" convite pendente, com confirmação (MO-14). [US-45 C][FR-029]"""
    tcc = _secao_tcc(request, tur_id)
    convite = next((s for s in services_orientacao.convites_do_tcc(tcc) if s.pk == sol_id), None)
    if convite is None or not services_orientacao.estado_coorientadores(tcc)["mostra_botoes"]:
        raise Http404
    return _confirmar_remocao(
        request,
        tur_id,
        convite.sol_doc.doc.usu_nome,
        lambda: services_orientacao.remover_convite(request.user, tur_id, sol_id),
    )


# =============================================================================================
# Docente: tela Orientações (contracts/rotas.md §2)
# =============================================================================================


def _tela_orientacoes(request, estado=None):
    """Tela Orientações com o aviso de estado no topo e o item destacado (research R4).

    [US-18][US-36][FR-009][FR-012][FR-014][FR-031][FR-033]
    """
    contexto = services_orientacao.contexto_orientacoes(request.user)
    contexto.update(estado or {"aviso": "", "destaque": None})
    acao = request.GET.get("acao")
    contexto["acao"] = acao if acao in ("aceitar", "recusar") else ""
    return render(request, "cadastro/orientacao/orientacoes.html", contexto)


@perfil_requerido("docente")
def orientacoes(request):
    """Rota 11: item de menu "Orientações", para todo Docente (Q11); seções vazias com a MO-24.

    [US-18][US-36][RBN-CAD-10.2][RBN-CAD-10.4][RBN-CAD-11.4][FR-009][FR-014][FR-031][FR-040]
    """
    return _tela_orientacoes(request)


@perfil_requerido("docente")
def pedido_orientacao(request, sol_id):
    """Rota 12: link do pedido (e-mail e sino). A mesma tela, com o pedido destacado ou o aviso
    de estado; `?acao=` só destaca o botão; o GET nunca grava (research R4; Q14).
    [US-18][RBN-CAD-10.1][FR-012]
    """
    estado = services_orientacao.estado_da_solicitacao(
        request.user, sol_id, services_orientacao.TIPOS_PEDIDO
    )
    return _tela_orientacoes(request, estado)


@perfil_requerido("docente")
def convite_coorientacao(request, sol_id):
    """Rota 13: link do convite (e-mail com "Aceitar"/"Recusar" e sino), com as mesmas regras
    da rota 12; a resposta é dada na tela, nunca pelo e-mail (Q14).
    [US-36][RBN-CAD-10.4][FR-033][Q14]
    """
    estado = services_orientacao.estado_da_solicitacao(
        request.user, sol_id, (TipoSolicitacao.COORIENTACAO,)
    )
    return _tela_orientacoes(request, estado)


def _responder(request, sol_id, servico):
    """Chama o serviço de resposta e volta à tela Orientações com a mensagem; já respondida ou
    cancelada → página do link com o estado atual (FR-012). [FR-010][FR-011][FR-032]
    """
    try:
        texto = servico(request.user, sol_id)
    except services_orientacao.SolicitacaoRespondida as erro:
        return redirect(services_orientacao.link_da_solicitacao(erro.sol))
    except TurmaArquivada:
        messages.warning(request, mensagens.MT25_TURMA_ARQUIVADA)
    else:
        messages.success(request, texto)
    return redirect("cadastro:orientacoes")


@require_POST
@perfil_requerido("docente")
def aceitar_solicitacao(request, sol_id):
    """Rota 14: "Aceitar" pedido ou convite (só o docente indicado; senão 404).

    [US-18][US-36][RBN-CAD-10.2][RBN-CAD-10.4][FR-010][FR-032]
    """
    return _responder(request, sol_id, services_orientacao.aceitar_solicitacao)


@require_POST
@perfil_requerido("docente")
def recusar_solicitacao(request, sol_id):
    """Rota 15: "Recusar" pedido ou convite (só o docente indicado; senão 404).

    [US-18][US-36][RBN-CAD-10.2][RBN-CAD-10.4][FR-011][FR-032]
    """
    return _responder(request, sol_id, services_orientacao.recusar_solicitacao)


@perfil_requerido("docente")
def ver_proposta(request, sol_id):
    """Rota 16: janela "Ver proposta", só leitura, com o Resumo por `pode_ver_resumo` (IC-05);
    "Fechar" volta à tela Orientações. [US-18][RBN-CAD-10.2][RAN-CAD-07][FR-013]
    """
    sol = services_orientacao.solicitacao_para_proposta(request.user, sol_id)
    tcc = sol.sol_tcc
    contexto = {
        "sol": sol,
        "tcc": tcc,
        "palavras": services_tcc.palavras_chave_do(tcc),
        "mostra_resumo": services_tcc.pode_ver_resumo(request.user, tcc),
    }
    return render(request, "cadastro/orientacao/ver_proposta.html", contexto)


@perfil_requerido("docente")
def historico_orientando(request, tcc_id):
    """Rota 21: histórico do Status para o Orientador atual (template da spec 005; IC-06);
    "Fechar" volta à tela de orientandos. O Coorientador e a turma arquivada dão 404.
    [US-18 #15][US-14 A][FR-015][FR-043][research R13]
    """
    tcc = services_orientacao.tcc_do_orientador(request.user, tcc_id)
    contexto = services_tcc.contexto_historico(tcc, reverse("cadastro:orientacoes"))
    return render(request, "cadastro/tcc/historico_status.html", contexto)


@perfil_requerido("docente")
def indicar_apto(request, tcc_id):
    """Rota 23: confirmação "Confirmar que o TCC de [nome do aluno] está apto para defesa?" e
    indicação; "Cancelar" e "Confirmar" voltam à tela de orientandos. Só o Orientador atual, em
    turma não arquivada (Coorientador: 404); botão indisponível pelo endereço direto: 404.
    [US-42][RBN-CAD-11.5][FR-026][FR-027][FR-043]
    """
    tcc = services_orientacao.tcc_do_orientador(request.user, tcc_id)
    if request.method == "POST":
        try:
            services_orientacao.indicar_apto(request.user, tcc_id)
        except TurmaArquivada:
            messages.warning(request, mensagens.MT25_TURMA_ARQUIVADA)
        except services_orientacao.ErroOrientacao as erro:
            messages.error(request, erro.mensagem)
        else:
            messages.success(request, mensagens.TCC_INDICADO_APTO)
        return redirect("cadastro:orientacoes")
    if services_orientacao.estado_apto_do_tcc(tcc) != "disponivel":
        raise Http404
    contexto = {
        "titulo": "Apto para Defesa",
        "texto": mensagens.CONFIRMAR_APTO.format(nome=tcc.tcc_alu.alu.usu_nome),
        "url_acao": reverse("cadastro:indicar_apto", args=[tcc.pk]),
        "url_cancelar": reverse("cadastro:orientacoes"),
    }
    return render(request, "cadastro/orientacao/confirmar.html", contexto)


@perfil_requerido("docente")
def correcoes_conferidas(request, tcc_id):
    """Rota 24: confirmação (MO-13) e gravação de "Correções Conferidas"; "Cancelar" e
    "Confirmar" voltam à tela de orientandos. [US-18 #16][US-44 B][FR-016][Q2]
    """
    tcc = services_orientacao.tcc_do_orientador(request.user, tcc_id)
    if request.method == "POST":
        try:
            services_orientacao.conferir_correcoes(request.user, tcc_id)
        except TurmaArquivada:
            messages.warning(request, mensagens.MT25_TURMA_ARQUIVADA)
        else:
            messages.success(request, mensagens.MO13_CORRECOES_CONFERIDAS)
        return redirect("cadastro:orientacoes")
    contexto = {
        "titulo": "Correções Conferidas",
        "texto": mensagens.MO13_CONFIRMAR_CORRECOES.format(nome=tcc.tcc_alu.alu.usu_nome),
        "url_acao": reverse("cadastro:correcoes_conferidas", args=[tcc.pk]),
        "url_cancelar": reverse("cadastro:orientacoes"),
    }
    return render(request, "cadastro/orientacao/confirmar.html", contexto)
