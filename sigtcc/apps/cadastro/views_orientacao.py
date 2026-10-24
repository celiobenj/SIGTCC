"""Views de orientação (spec 006): seção Orientação do Aluno, tela Orientações do docente, links de
pedido e convite, Apto para Defesa e Correções Conferidas. Views finas: as regras ficam em
services_orientacao.

[US-17][US-18][US-36][US-42][US-45][research R1]
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from sigtcc.apps.cadastro import mensagens, services_orientacao
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


# =============================================================================================
# Docente: tela Orientações (contracts/rotas.md §2)
# =============================================================================================


@perfil_requerido("docente")
def orientacoes(request):
    """Tela Orientações (rota 11). Provisória até a T023 (US2). [US-18][FR-040]"""
    raise Http404


@perfil_requerido("docente")
def pedido_orientacao(request, sol_id):
    """Tela Orientações com o pedido (rota 12). Provisória até a T023 (US2). [US-18][FR-012]"""
    raise Http404


@perfil_requerido("docente")
def convite_coorientacao(request, sol_id):
    """Tela Orientações com o convite (rota 13). Provisória até a T045 (US7). [US-36][FR-033]"""
    raise Http404
