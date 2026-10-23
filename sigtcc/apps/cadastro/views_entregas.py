"""Views da aba Atividades do app cadastro (spec 005).

Views finas (orquestram `services_entregas`, sem regra de negócio): cadastro de entregas e
acompanhamento pelo Professor da Disciplina (US-43, US-16); envio e substituição de link pelo
Aluno (US-15, US-29); homologação ou devolução para ajuste da Versão Final (US-44).

[US-15][US-16][US-29][US-43][US-44][RBN-CAD-09.1 a 09.6][research C1]
"""

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from sigtcc.apps.cadastro import mensagens, services_entregas, services_turmas
from sigtcc.apps.cadastro.forms_entregas import CadastroEntregaForm
from sigtcc.apps.cadastro.models import TurmasMarcos
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
