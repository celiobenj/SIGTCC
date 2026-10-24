"""Views da publicação do artigo e do aproveitamento (spec 006). Views finas sobre
services_artigos.

Publicação: seção da aba Meu TCC do Aluno (rota 10) e tela própria do Orientador (rota 22).
Aproveitamento: tela do Coordenador de Curso no menu, seção "Gestão" (rotas 27 a 29).

[US-46][US-20][RBN-CAD-12.1][RBN-CAD-12.2][RBN-CAD-12.3][FR-034 a FR-038][research R1]
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from sigtcc.apps.cadastro import mensagens, services_artigos, services_tcc, services_turmas
from sigtcc.apps.cadastro.forms_artigos import PublicacaoForm
from sigtcc.apps.cadastro.models import Cursos
from sigtcc.apps.cadastro.permissoes import curso_id_do_usuario, perfil_requerido
from sigtcc.apps.cadastro.services_orientacao import link_secao, tcc_do_orientador
from sigtcc.apps.cadastro.services_turmas import TurmaArquivada

# =============================================================================================
# Publicação do artigo (US-46; rotas 10 e 22)
# =============================================================================================


@require_POST
@perfil_requerido("aluno")
def salvar_publicacao_aluno(request, tur_id):
    """Rota 10: "Salvar publicação" da aba Meu TCC; volta à seção (`?secao=publicacao`), com
    "Publicação salva" ou os erros do formulário; turma arquivada: MT-25.
    [US-46][RBN-CAD-12.1][FR-034][FR-036][contracts/rotas.md]
    """
    turma, aluno = services_tcc.turma_do_aluno(tur_id, request.user)
    tcc = services_turmas.tcc_do_aluno(turma, aluno)
    if tcc is None:
        raise Http404
    formulario = PublicacaoForm(request.POST)
    if not formulario.is_valid():
        for campo, erros in formulario.errors.items():
            for erro in erros:
                messages.error(request, erro)
        return redirect(link_secao(tcc, "publicacao"))
    try:
        services_artigos.salvar_publicacao(request.user, tcc.pk, formulario.cleaned_data)
    except TurmaArquivada:
        messages.warning(request, mensagens.MT25_TURMA_ARQUIVADA)
    else:
        messages.success(request, mensagens.PUBLICACAO_SALVA)
    return redirect(link_secao(tcc, "publicacao"))


@perfil_requerido("docente")
def publicacao_orientando(request, tcc_id):
    """Rota 22: "Publicação do artigo" do orientando, só para o Orientador atual e só em Artigo
    Científico; "Voltar" → tela de orientandos (FR-035). Turma arquivada: 404 (R10, A10).
    [US-46 A][RBN-CAD-12.1][FR-035][FR-043]
    """
    tcc = tcc_do_orientador(request.user, tcc_id)
    publicacao = services_artigos.contexto_publicacao(tcc)
    if publicacao is None:
        raise Http404
    formulario = PublicacaoForm(
        request.POST if request.method == "POST" else None, initial=publicacao["inicial"]
    )
    if request.method == "POST" and formulario.is_valid():
        try:
            services_artigos.salvar_publicacao(request.user, tcc.pk, formulario.cleaned_data)
        except TurmaArquivada:
            messages.warning(request, mensagens.MT25_TURMA_ARQUIVADA)
            return redirect("cadastro:orientacoes")
        messages.success(request, mensagens.PUBLICACAO_SALVA)
        return redirect("cadastro:publicacao_orientando", tcc_id=tcc.pk)
    contexto = {
        "tcc": tcc,
        "pub": publicacao,
        "form_publicacao": formulario,
        "url_acao": reverse("cadastro:publicacao_orientando", args=[tcc.pk]),
    }
    return render(request, "cadastro/orientacao/publicacao.html", contexto)


# =============================================================================================
# Aproveitamento de artigos (US-20; rotas 27 a 29)
# =============================================================================================


def _curso_escolhido(request):
    """`?curso=` validado contra Cursos: "todos" = None; inválido ou ausente = curso do
    Coordenador (research R5, A5). [US-20][RBN-CAD-14.1][FR-037]
    """
    valor = request.GET.get("curso") or request.POST.get("curso") or ""
    if valor == "todos":
        return None, "todos"
    if valor.isdigit() and Cursos.objects.filter(pk=int(valor)).exists():
        return int(valor), valor
    meu = curso_id_do_usuario(request.user)
    return meu, str(meu) if meu else "todos"


@perfil_requerido("coordenador")
def aproveitamento_artigos(request):
    """Rota 27: tela "Aproveitamento de artigos" com o filtro Curso (3 cursos e Todos),
    iniciando no curso do Coordenador; botões só nos artigos do curso que coordena (FR-037).
    [US-20][RBN-CAD-12.2][RBN-CAD-14.1][FR-037][FR-041]
    """
    curso_id, valor = _curso_escolhido(request)
    contexto = {
        "linhas": services_artigos.artigos_para_analise(request.user, curso_id),
        "cursos": Cursos.objects.order_by("cur_nome"),
        "curso": valor,
    }
    return render(request, "cadastro/orientacao/aproveitamento.html", contexto)


def _decidir(request, tcc_id, servico, sucesso):
    """Chama a decisão e volta à tela com o mesmo filtro (validado). [FR-038]"""
    _, valor = _curso_escolhido(request)
    try:
        servico(request.user, tcc_id)
    except services_artigos.ErroArtigo as erro:
        messages.error(request, erro.mensagem)
    else:
        messages.success(request, sucesso)
    return redirect(f"{reverse('cadastro:aproveitamento_artigos')}?curso={valor}")


@require_POST
@perfil_requerido("coordenador")
def homologar_artigo(request, tcc_id):
    """Rota 28: "Homologar" ("Aproveitamento homologado"). [US-20][RBN-CAD-12.3][FR-038]"""
    return _decidir(
        request, tcc_id, services_artigos.homologar_artigo, mensagens.APROVEITAMENTO_HOMOLOGADO
    )


@require_POST
@perfil_requerido("coordenador")
def recusar_artigo(request, tcc_id):
    """Rota 29: "Recusar" ("Aproveitamento recusado"; MO-21 depois da liberação no Homologado).

    [US-20][RBN-CAD-12.3][FR-038]
    """
    return _decidir(
        request, tcc_id, services_artigos.recusar_artigo, mensagens.APROVEITAMENTO_RECUSADO
    )
