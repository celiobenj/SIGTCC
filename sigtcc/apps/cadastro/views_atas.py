"""Views das atas de orientação (spec 006): Aluno, Orientador, Coorientador e Professor da
Disciplina. Views finas sobre services_atas.

Três entradas (contracts/rotas.md): aba Meu TCC do Aluno (rotas 7 a 9), linha da tela de
orientandos (rotas 17 a 20) e painel do aluno (rota 26, só leitura). Com a turma arquivada, a
lista abre só para consulta; registro, edição e comentário voltam à lista com a MT-25.

[US-19][RBN-CAD-11.1][RBN-CAD-11.2][FR-021 a FR-025][FR-042][FR-043][FR-044][research R1]
"""

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from sigtcc.apps.cadastro import mensagens, services_atas, services_tcc, services_turmas
from sigtcc.apps.cadastro.forms_atas import AtaForm, ComentarioForm
from sigtcc.apps.cadastro.models import TCCs
from sigtcc.apps.cadastro.permissoes import perfil_requerido
from sigtcc.apps.cadastro.services_orientacao import (
    COORIENTADOR,
    ORIENTADOR,
    link_secao,
    papeis_no_tcc,
    pode_alterar_no_tcc,
)
from sigtcc.apps.cadastro.services_turmas import CONSULTAR, TurmaArquivada


def _linhas(atas, url_editar, url_comentar):
    """Atas com os endereços de "Editar" e "Comentar" de quem abre (None quando não pode).

    [US-19][RBN-CAD-11.2][FR-023]
    """
    return [
        {
            "ata": ata,
            "comentarios": list(ata.comentariosencontro_set.all()),
            "url_editar": url_editar(ata) if url_editar else "",
            "url_comentar": url_comentar(ata) if url_comentar else "",
        }
        for ata in atas
    ]


def _render_lista(request, tcc, url_voltar, url_registrar, url_editar, url_comentar):
    """Lista de atas (FR-023) com os botões que o papel permite (FR-024, FR-025).

    [US-19][RBN-CAD-11.2][FR-023][FR-024]
    """
    contexto = services_atas.contexto_lista(request.user, tcc)
    contexto.update(
        {
            "linhas": _linhas(
                contexto["atas"],
                url_editar if contexto["pode_editar"] else None,
                url_comentar if contexto["pode_comentar"] else None,
            ),
            "linhas_origem": _linhas(contexto["atas_origem"], None, None),
            "url_voltar": url_voltar,
            "url_registrar": url_registrar if contexto["pode_registrar"] else "",
        }
    )
    return render(request, "cadastro/orientacao/atas.html", contexto)


def _formulario(request, tcc, url_voltar, salvar, sucesso, ata=None, url_lista=None):
    """Janela da ata (registro ou edição): GET mostra; POST salva e volta; turma arquivada no
    meio volta com a MT-25 (research R2, A11). [FR-021][FR-022][FR-024]
    [US-19][RBN-CAD-11.1]
    """
    destino_arquivada = url_lista or url_voltar
    if services_turmas.turma_arquivada(tcc.tcc_tur):
        messages.warning(request, mensagens.MT25_TURMA_ARQUIVADA)
        return redirect(destino_arquivada)
    inicial = (
        {"data": ata.enc_data, "pauta": ata.enc_pauta, "metas": ata.enc_metas} if ata else None
    )
    formulario = AtaForm(request.POST if request.method == "POST" else None, initial=inicial)
    if request.method == "POST" and formulario.is_valid():
        try:
            salvar(formulario.cleaned_data)
        except TurmaArquivada:
            messages.warning(request, mensagens.MT25_TURMA_ARQUIVADA)
            return redirect(destino_arquivada)
        if sucesso:
            messages.success(request, sucesso)
        return redirect(url_voltar)
    contexto = {
        "tcc": tcc,
        "form": formulario,
        "ata": ata,
        "titulo": "Editar ata de orientação" if ata else "Registrar ata de orientação",
        "url_cancelar": url_voltar,
    }
    return render(request, "cadastro/orientacao/form_ata.html", contexto)


# =============================================================================================
# Aluno: aba Meu TCC (rotas 7 a 9)
# =============================================================================================


def _tcc_do_aluno(request, tur_id):
    """TCC do próprio Aluno na turma (404 sem vínculo; sem IDOR). [contracts/rotas.md §1]

    [US-19][RBN-CAD-11.1]
    """
    turma, aluno = services_tcc.turma_do_aluno(tur_id, request.user)
    tcc = services_turmas.tcc_do_aluno(turma, aluno)
    if tcc is None:
        raise Http404
    return tcc


@perfil_requerido("aluno")
def minhas_atas(request, tur_id):
    """Rota 7: "Ver atas" da seção Atas de orientação; "Voltar" → a seção (FR-042).

    [US-19][RBN-CAD-11.2][FR-023][FR-042]
    """
    tcc = _tcc_do_aluno(request, tur_id)
    return _render_lista(
        request,
        tcc,
        link_secao(tcc, "atas"),
        reverse("cadastro:registrar_ata_aluno", args=[tur_id]),
        lambda ata: reverse("cadastro:editar_ata_aluno", args=[tur_id, ata.pk]),
        None,
    )


@perfil_requerido("aluno")
def registrar_ata_aluno(request, tur_id):
    """Rota 8: janela "Registrar ata de orientação"; "Cancelar" e "Salvar" voltam à seção Atas
    (FR-042). [US-19][RBN-CAD-11.1][FR-021][FR-022]
    """
    tcc = _tcc_do_aluno(request, tur_id)
    if not services_turmas.turma_arquivada(tcc.tcc_tur) and not pode_alterar_no_tcc(tcc):
        raise Http404
    return _formulario(
        request,
        tcc,
        link_secao(tcc, "atas"),
        lambda dados: services_atas.registrar_ata(request.user, tcc.pk, dados),
        mensagens.ATA_REGISTRADA,
    )


@perfil_requerido("aluno")
def editar_ata_aluno(request, tur_id, enc_id):
    """Rota 9: edição da ata pelo Aluno; volta à lista de atas (FR-024).

    [US-19][RBN-CAD-11.2][FR-024]
    """
    tcc = _tcc_do_aluno(request, tur_id)
    ata = services_atas.ata_do_tcc(tcc, enc_id)
    if not services_turmas.turma_arquivada(tcc.tcc_tur) and not pode_alterar_no_tcc(tcc):
        raise Http404
    lista = reverse("cadastro:minhas_atas", args=[tur_id])
    return _formulario(
        request,
        tcc,
        lista,
        lambda dados: services_atas.editar_ata(request.user, tcc.pk, ata.pk, dados),
        None,
        ata=ata,
    )


# =============================================================================================
# Docente: linha da tela de orientandos (rotas 17 a 20)
# =============================================================================================


def _tcc_do_docente(request, tcc_id):
    """TCC em que o docente é Orientador atual ou Coorientador ativo, senão 404 (research R10).

    [US-19][FR-023][FR-025][Q10]
    """
    tcc = TCCs.objects.select_related("tcc_tur", "tcc_alu__alu").filter(pk=tcc_id).first()
    if tcc is None or not (papeis_no_tcc(request.user, tcc) & {ORIENTADOR, COORIENTADOR}):
        raise Http404
    return tcc


def _exige_alteracao(tcc):
    """Participação encerrada ou TCC copiado: 404 (FR-007); turma arquivada segue para a
    MT-25 em `_formulario`. [FR-046]
    [US-19][RBN-CAD-11.2]
    """
    if not services_turmas.turma_arquivada(tcc.tcc_tur) and not pode_alterar_no_tcc(tcc):
        raise Http404


@perfil_requerido("docente")
def atas_orientando(request, tcc_id):
    """Rota 17: lista de atas do orientando; "Voltar" → tela Orientações (FR-043). Com a turma
    arquivada, só leitura (FR-014). [US-19][RBN-CAD-11.2][FR-023][FR-024][FR-043]
    """
    tcc = _tcc_do_docente(request, tcc_id)
    return _render_lista(
        request,
        tcc,
        reverse("cadastro:orientacoes"),
        reverse("cadastro:registrar_ata_docente", args=[tcc.pk]),
        lambda ata: reverse("cadastro:editar_ata_docente", args=[tcc.pk, ata.pk]),
        lambda ata: reverse("cadastro:comentar_ata", args=[tcc.pk, ata.pk]),
    )


@perfil_requerido("docente")
def registrar_ata_docente(request, tcc_id):
    """Rota 18: "Registrar ata" pela linha; "Cancelar" e "Salvar" voltam à tela Orientações.

    [US-19][RBN-CAD-11.1][FR-022][FR-043]
    """
    tcc = _tcc_do_docente(request, tcc_id)
    _exige_alteracao(tcc)
    return _formulario(
        request,
        tcc,
        reverse("cadastro:orientacoes"),
        lambda dados: services_atas.registrar_ata(request.user, tcc.pk, dados),
        mensagens.ATA_REGISTRADA,
        url_lista=reverse("cadastro:atas_orientando", args=[tcc.pk]),
    )


@perfil_requerido("docente")
def editar_ata_docente(request, tcc_id, enc_id):
    """Rota 19: edição da ata pelo Orientador ou pelo Coorientador; volta à lista (FR-024).

    [US-19][RBN-CAD-11.2][FR-024]
    """
    tcc = _tcc_do_docente(request, tcc_id)
    ata = services_atas.ata_do_tcc(tcc, enc_id)
    _exige_alteracao(tcc)
    lista = reverse("cadastro:atas_orientando", args=[tcc.pk])
    return _formulario(
        request,
        tcc,
        lista,
        lambda dados: services_atas.editar_ata(request.user, tcc.pk, ata.pk, dados),
        None,
        ata=ata,
    )


@perfil_requerido("docente")
def comentar_ata(request, tcc_id, enc_id):
    """Rota 20: campo de comentário abaixo da ata; volta à lista (FR-024).

    [US-19][RBN-CAD-11.2][FR-024]
    """
    tcc = _tcc_do_docente(request, tcc_id)
    ata = services_atas.ata_do_tcc(tcc, enc_id)
    _exige_alteracao(tcc)
    lista = reverse("cadastro:atas_orientando", args=[tcc.pk])
    if services_turmas.turma_arquivada(tcc.tcc_tur):
        messages.warning(request, mensagens.MT25_TURMA_ARQUIVADA)
        return redirect(lista)
    formulario = ComentarioForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and formulario.is_valid():
        try:
            services_atas.comentar_ata(
                request.user, tcc.pk, ata.pk, formulario.cleaned_data["texto"]
            )
        except TurmaArquivada:
            messages.warning(request, mensagens.MT25_TURMA_ARQUIVADA)
        return redirect(lista)
    contexto = {
        "tcc": tcc,
        "ata": ata,
        "form": formulario,
        "comentar": True,
        "titulo": "Comentar ata",
        "url_cancelar": lista,
    }
    return render(request, "cadastro/orientacao/form_ata.html", contexto)


# =============================================================================================
# Professor da Disciplina: painel do aluno (rota 26, só leitura)
# =============================================================================================


@perfil_requerido("docente")
def atas_painel(request, tur_id, alu_id):
    """Rota 26: atas só para leitura, para o Professor da Disciplina da turma (mesmas checagens
    do painel: research R10, A2); "Voltar" → painel. [US-19 F][US-41][FR-023][FR-044]
    """
    turma = services_turmas.turma_para(request.user, tur_id, CONSULTAR)
    if turma.tur_doc_id != request.user.pk:
        raise PermissionDenied
    aluno = services_turmas.vinculo_na_turma(turma, alu_id)
    tcc = services_turmas.tcc_do_aluno(turma, aluno)
    if tcc is None:
        raise Http404
    contexto = services_atas.contexto_lista(request.user, tcc)
    contexto.update(
        {
            "linhas": _linhas(contexto["atas"], None, None),
            "linhas_origem": _linhas(contexto["atas_origem"], None, None),
            "url_voltar": reverse("cadastro:painel_aluno", args=[turma.pk, aluno.pk]),
            "url_registrar": "",
        }
    )
    return render(request, "cadastro/orientacao/atas.html", contexto)
