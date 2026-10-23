"""Views da Gestão de Contas (spec 002): só orquestram; as regras ficam em services_contas.py.

Ordem das conferências nas rotas com id (research C22, C11): registro pela especialização (404) →
perfil (403, M-02) → curso (403 com a mensagem do FR-009) → status. Toda ação que grava redireciona
depois do POST (PRG).

[US-03][US-04][US-05][US-50][FR-009][FR-010][research C21][C22]
"""

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import NoReverseMatch, reverse

from sigtcc.apps.cadastro import mensagens, services_contas
from sigtcc.apps.cadastro.forms_contas import DocenteForm, SecretariaForm
from sigtcc.apps.cadastro.models import Cursos
from sigtcc.apps.cadastro.permissoes import curso_do_usuario, perfil_requerido, tem_perfil
from sigtcc.apps.cadastro.services_contas import ErroDeCampo, ForaDoCurso

GESTAO = ("secretaria", "coordenador")
MEMBROS = ("orientador", "professor_disciplina", "secretaria", "coordenador")


def recusa_fora_do_curso(request, erro):
    """Página de acesso não permitido com a mensagem do FR-009 e status 403 (research C21).

    erro: ForaDoCurso, com o texto "Você só pode cadastrar e alterar dados do seu curso" ou "Você
    só pode alterar dados do seu curso". Nenhum dado do registro aparece na resposta.
    [US-03][US-04][RBN-CAD-14.1][FR-009][SC-004]
    """
    assert isinstance(erro, ForaDoCurso)
    return render(request, "acesso_negado.html", {"mensagem": erro.mensagem}, status=403)


def _abas(usuario):
    """Abas da Gestão de Contas que o usuário pode abrir e cujas rotas já existem.

    [US-03][US-05][FR-011][FR-023][FR-031]
    """
    candidatas = (
        ("docentes", "Docentes", "cadastro:contas_docentes", GESTAO),
        ("secretarias", "Secretarias", "cadastro:contas_secretarias", GESTAO),
        ("membros", "Membros externos", "cadastro:contas_membros", MEMBROS),
    )
    abas = []
    for chave, rotulo, rota, perfis in candidatas:
        if not tem_perfil(usuario, *perfis):
            continue
        try:
            abas.append({"chave": chave, "rotulo": rotulo, "url": reverse(rota)})
        except NoReverseMatch:
            continue
    return abas


def _mostrar_resultado(request, resultado):
    """Mensagem depois de gravar: sucesso ou, na MC-13, aviso (os campos foram gravados).

    [US-03][US-05][FR-008][FR-015][FR-016]
    """
    if resultado.aviso:
        messages.warning(request, resultado.mensagem)
    else:
        messages.success(request, resultado.mensagem)


def _aplicar_erro(formulario, erro):
    """Põe a recusa do serviço no campo (ou no topo do formulário). [FR-001][FR-006]"""
    campo = erro.campo if erro.campo in formulario.fields else None
    formulario.add_error(campo, erro.mensagem)


def _esquecer_papeis(usuario):
    """Descarta os papéis guardados no objeto do usuário (o papel pode ter mudado). [m11]"""
    if hasattr(usuario, "_papeis_cache"):
        del usuario._papeis_cache


def _depois_de_gravar(request, rota):
    """PRG: volta à lista; se o usuário perdeu o acesso a ela (desmarcou o próprio papel de
    Coordenador), vai ao painel (US-03 A10; research C6, m11). [FR-016][FR-022]
    """
    _esquecer_papeis(request.user)
    if not tem_perfil(request.user, *GESTAO):
        return redirect("cadastro:painel")
    return redirect(rota)


# =============================================================================================
# Docentes (US-03; FR-012 a FR-019)
# =============================================================================================


@perfil_requerido(*GESTAO)
def docentes(request):
    """Listagem de docentes com o filtro de Curso (US-03 A7; RBN-CAD-01.4, RBN-CAD-14.1).

    [US-03][RBN-CAD-01.4][RBN-CAD-11.3][RBN-CAD-14.1][FR-017][FR-018][FR-019]
    """
    cur_id, filtro = services_contas.filtro_de_curso(request.user, request.GET.get("curso"))
    contexto = {
        "abas": _abas(request.user),
        "linhas": services_contas.listar_docentes(request.user, cur_id),
        "cursos": Cursos.objects.order_by("cur_nome"),
        "filtro": filtro,
        "limite": services_contas.LIMITE_ORIENTANDOS,
    }
    return render(request, "cadastro/contas/docentes.html", contexto)


def _dados_docente(formulario):
    """Dados limpos do formulário de Docente para o serviço. [FR-012][FR-016]"""
    return dict(formulario.cleaned_data)


@perfil_requerido(*GESTAO)
def docente_novo(request):
    """Cadastro de Docente (US-03 fluxo principal, A1 a A3). [US-03][RBN-CAD-01.1][FR-012]"""
    inicial = {"curso_lotacao": curso_do_usuario(request.user)}
    formulario = DocenteForm(request.POST if request.method == "POST" else None, initial=inicial)
    if request.method == "POST" and formulario.is_valid():
        try:
            resultado = services_contas.cadastrar_docente(request.user, _dados_docente(formulario))
        except ErroDeCampo as erro:
            _aplicar_erro(formulario, erro)
        else:
            _mostrar_resultado(request, resultado)
            return redirect("cadastro:contas_docentes")
    contexto = {"form": formulario, "titulo": mensagens.CADASTRAR_DOCENTE}
    return render(request, "cadastro/contas/form_docente.html", contexto)


@perfil_requerido(*GESTAO)
def docente_editar(request, doc_id):
    """Alteração de Docente (US-03 A8 a A11). [US-03][RBN-CAD-01.2][FR-008][FR-016]"""
    try:
        docente = services_contas.docente_para_editar(request.user, doc_id)
    except ForaDoCurso as erro:
        return recusa_fora_do_curso(request, erro)
    coordenado = services_contas.curso_coordenado_de(docente)
    inicial = {
        "nome": docente.doc.usu_nome,
        "email": docente.doc.usu_email,
        "titulacao": docente.doc_titulacao,
        "curso_lotacao": docente.doc_cur,
        "coordenador": coordenado is not None,
        "curso_coordenado": coordenado,
    }
    formulario = DocenteForm(
        request.POST if request.method == "POST" else None, initial=inicial, edicao=True
    )
    if request.method == "POST" and formulario.is_valid():
        try:
            resultado = services_contas.alterar_docente(
                request.user, doc_id, _dados_docente(formulario)
            )
        except ForaDoCurso as erro:
            return recusa_fora_do_curso(request, erro)
        except ErroDeCampo as erro:
            _aplicar_erro(formulario, erro)
        else:
            _mostrar_resultado(request, resultado)
            return _depois_de_gravar(request, "cadastro:contas_docentes")
    contexto = {"form": formulario, "titulo": "Alterar docente", "docente": docente}
    return render(request, "cadastro/contas/form_docente.html", contexto)


# =============================================================================================
# Secretaria (US-03 A4 e A5; FR-020 a FR-023)
# =============================================================================================


@perfil_requerido(*GESTAO)
def secretarias(request):
    """Lista de Secretarias com o filtro de Curso; a Secretaria vê sem ações (US-03 E9, FR-023).

    [US-03][US-04][RBN-CAD-02.1][RBN-CAD-14.1][FR-023]
    """
    cur_id, filtro = services_contas.filtro_de_curso(request.user, request.GET.get("curso"))
    contexto = {
        "abas": _abas(request.user),
        "linhas": services_contas.listar_secretarias(request.user, cur_id),
        "cursos": Cursos.objects.order_by("cur_nome"),
        "filtro": filtro,
        "pode_cadastrar": tem_perfil(request.user, "coordenador"),
    }
    return render(request, "cadastro/contas/secretarias.html", contexto)


@perfil_requerido("coordenador")
def secretaria_nova(request):
    """Cadastro da Secretaria pelo Coordenador (US-03 A4). [US-03][RBN-CAD-02.1][FR-020]"""
    inicial = {"curso_vinculado": curso_do_usuario(request.user)}
    formulario = SecretariaForm(request.POST if request.method == "POST" else None, initial=inicial)
    if request.method == "POST" and formulario.is_valid():
        try:
            resultado = services_contas.cadastrar_secretaria(
                request.user, dict(formulario.cleaned_data)
            )
        except ErroDeCampo as erro:
            _aplicar_erro(formulario, erro)
        else:
            _mostrar_resultado(request, resultado)
            return redirect("cadastro:contas_secretarias")
    contexto = {"form": formulario, "titulo": mensagens.NOVA_SECRETARIA}
    return render(request, "cadastro/contas/form_secretaria.html", contexto)


@perfil_requerido("coordenador")
def secretaria_editar(request, sec_id):
    """Alteração da Secretaria pelo Coordenador do curso (US-03 A5).

    [US-03][RBN-CAD-02.2][FR-008][FR-022]
    """
    try:
        secretaria = services_contas.secretaria_para_editar(request.user, sec_id)
    except ForaDoCurso as erro:
        return recusa_fora_do_curso(request, erro)
    inicial = {
        "nome": secretaria.sec.usu_nome,
        "email": secretaria.sec.usu_email,
        "curso_vinculado": secretaria.sec_cur,
    }
    formulario = SecretariaForm(
        request.POST if request.method == "POST" else None, initial=inicial, edicao=True
    )
    if request.method == "POST" and formulario.is_valid():
        try:
            resultado = services_contas.alterar_secretaria(
                request.user, sec_id, dict(formulario.cleaned_data)
            )
        except ForaDoCurso as erro:
            return recusa_fora_do_curso(request, erro)
        except ErroDeCampo as erro:
            _aplicar_erro(formulario, erro)
        else:
            _mostrar_resultado(request, resultado)
            return _depois_de_gravar(request, "cadastro:contas_secretarias")
    contexto = {"form": formulario, "titulo": "Alterar secretaria", "secretaria": secretaria}
    return render(request, "cadastro/contas/form_secretaria.html", contexto)
