"""Janela Ouvintes da sessão de defesa (spec 009, US2; contracts/rotas.md; research B3 e B9). As
views só orquestram: as regras ficam em permissoes_defesa e services_ouvintes.

Recusas: sem login, o login com next; sem permissão (inclusive a turma arquivada, também numa
corrida entre o GET e o POST), 403 sem texto, e o handler403 mostra a M-02 "Você não tem
permissão para esta ação" (US-30 E9; revisão I-01).

[US-30][RBN-DEF-08.2]
"""

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from sigtcc.apps.cadastro.permissoes import perfil_requerido
from sigtcc.apps.cadastro.services_turmas import TurmaArquivada
from sigtcc.apps.defesa import mensagens, permissoes_defesa, services_ouvintes, views_defesa
from sigtcc.apps.defesa.forms_ouvintes import OuvintesFormSet

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
