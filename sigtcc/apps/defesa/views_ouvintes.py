"""Janela Ouvintes da sessão de defesa (spec 009, US2; contracts/rotas.md; research B3 e B9). As
views só orquestram: as regras ficam em permissoes_defesa e services_ouvintes.

Recusas: sem login, o login com next; sem permissão (inclusive a turma arquivada, também numa
corrida entre o GET e o POST), 403 sem texto, e o handler403 mostra a M-02 "Você não tem
permissão para esta ação" (US-30 E9; revisão I-01).

Spec 009 (US4): tela "Ouvintes das defesas" da Secretaria (RBN-DEF-08.4), somente leitura.
Spec 009 (US3): janela Ocorrências do Presidente da banca (RBN-DEF-08.5).

[US-30][RBN-DEF-08.2][RBN-DEF-08.4][RBN-DEF-08.5]
"""

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from sigtcc.apps.cadastro import services_contas
from sigtcc.apps.cadastro.models import Cursos
from sigtcc.apps.cadastro.permissoes import perfil_requerido
from sigtcc.apps.cadastro.services_turmas import TurmaArquivada
from sigtcc.apps.defesa import (
    mensagens,
    permissoes_defesa,
    services_defesa,
    services_ouvintes,
    views_defesa,
)
from sigtcc.apps.defesa.forms_defesa import FiltroPeriodoForm
from sigtcc.apps.defesa.forms_ouvintes import OcorrenciasForm, OuvintesFormSet

PREFIXO_OUVINTES = "ouv"


def _erro_na_linha(formset, erro):
    """Mostra a recusa do serviço no campo da linha apontada (ou no topo da lista).
    [US-30][RBN-DEF-08.2]
    """
    linhas = formset.linhas_validas()
    if erro.linha is not None and erro.linha < len(linhas):
        linhas[erro.linha].add_error(erro.campo, erro.mensagem)
    else:
        formset._non_form_errors = formset.error_class([erro.mensagem])


@perfil_requerido("docente")
def ouvintes(request, def_id):
    """Janela Ouvintes (US-30 A; FR-010 a FR-012): só o Presidente da banca ou o Professor da
    Disciplina da turma, com a sessão Em Andamento ou Realizada e a turma não arquivada (senão
    M-02). GET: os ouvintes gravados e uma linha vazia. POST: grava a lista inteira e volta à
    sessão com "Ouvintes salvos com sucesso"; erros de campo na mesma janela, sem gravar.
    [US-30][RBN-DEF-08.2]
    """
    registro = views_defesa.sessao_ou_404(def_id)
    if not permissoes_defesa.pode_editar_ouvintes(request.user, registro):
        raise PermissionDenied
    if request.method == "POST":
        formset = OuvintesFormSet(request.POST, prefix=PREFIXO_OUVINTES)
        if formset.is_valid():
            try:
                services_ouvintes.salvar_ouvintes(request.user, registro.pk, formset.linhas())
            except TurmaArquivada:
                raise PermissionDenied
            except services_ouvintes.ErroOuvintes as erro:
                if erro.campo == services_ouvintes.PERMISSAO:
                    raise PermissionDenied
                _erro_na_linha(formset, erro)
            else:
                messages.success(request, mensagens.OUVINTES_SALVOS)
                return redirect("defesa:sessao", def_id=registro.pk)
    else:
        inicial = [
            {"nome": ouvinte.ouv_nome, "matricula": ouvinte.ouv_matricula}
            for ouvinte in services_ouvintes.ouvintes_da_sessao(registro)
        ]
        formset = OuvintesFormSet(initial=inicial, prefix=PREFIXO_OUVINTES)
    return render(request, "defesa/form_ouvintes.html", {"formset": formset, "sessao": registro})


@perfil_requerido("secretaria")
def ouvintes_das_defesas(request):
    """Tela "Ouvintes das defesas" (US-30 C; FR-016 a FR-018), só da Secretaria (P8; os demais
    perfis recebem a M-02): os ouvintes das sessões Realizadas, com o filtro de período das
    defesas (spec 007; Período Letivo por padrão; filtro inválido mostra a mensagem e usa o
    padrão) e o filtro de Curso (spec 002, US-39). Sem linhas: MX-07. Antes, o início automático
    das sessões vencidas, como as demais telas da Defesa.
    [US-30][RBN-DEF-08.4][RBN-DEF-01.5][RBN-CAD-14.1]
    """
    services_defesa.iniciar_sessoes_vencidas()
    form = FiltroPeriodoForm(request.GET or None)
    form.is_valid()
    cur_id, curso = services_contas.filtro_de_curso(request.user, request.GET.get("curso"))
    contexto = {
        "form": form,
        "linhas": services_ouvintes.ouvintes_das_defesas(form.filtro(), cur_id),
        "cursos": Cursos.objects.order_by("cur_nome"),
        "curso": curso,
        "horas": services_ouvintes.HORAS_POR_SESSAO,
        "vazia": mensagens.MX07_SEM_OUVINTES,
    }
    return render(request, "defesa/ouvintes_das_defesas.html", contexto)


@perfil_requerido("docente")
def ocorrencias(request, def_id):
    """Janela Ocorrências (US-30 B; FR-013 e FR-015): só o Presidente da banca, com a sessão Em
    Andamento, sem liberação e a turma não arquivada (senão M-02, inclusive ao Professor da
    Disciplina, P9; a TurmaArquivada da trava também vira 403). GET: o texto gravado. POST:
    grava e volta à sessão com "Ocorrências salvas com sucesso" (MX-06); acima de 2.000
    caracteres, a MX-01 na mesma janela, com a caixa destacada e nada gravado.
    [US-30][RBN-DEF-08.5]
    """
    registro = views_defesa.sessao_ou_404(def_id)
    if not permissoes_defesa.pode_editar_ocorrencias(request.user, registro):
        raise PermissionDenied
    if request.method == "POST":
        form = OcorrenciasForm(request.POST)
        if form.is_valid():
            try:
                services_ouvintes.registrar_ocorrencias(
                    request.user, registro.pk, form.cleaned_data["ocorrencias"]
                )
            except TurmaArquivada:
                raise PermissionDenied
            except services_ouvintes.ErroOuvintes as erro:
                if erro.campo == services_ouvintes.PERMISSAO:
                    raise PermissionDenied
                form.add_error("ocorrencias", erro.mensagem)
            else:
                messages.success(request, mensagens.MX06_OCORRENCIAS_SALVAS)
                return redirect("defesa:sessao", def_id=registro.pk)
    else:
        form = OcorrenciasForm(initial={"ocorrencias": registro.def_ocorrencias or ""})
    return render(request, "defesa/form_ocorrencias.html", {"form": form, "sessao": registro})
