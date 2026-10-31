"""Views do módulo de Defesa (spec 007; contracts/rotas.md). Views finas: as regras ficam em
services_defesa e permissoes_defesa.

[US-21][US-22][US-23][US-24][US-40]
"""

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from sigtcc.apps.cadastro import mensagens as mensagens_cadastro
from sigtcc.apps.cadastro.models import TCCs, Turmas
from sigtcc.apps.cadastro.permissoes import perfil_requerido, tem_perfil
from sigtcc.apps.cadastro.services_turmas import TurmaArquivada, turma_arquivada
from sigtcc.apps.defesa import mensagens, permissoes_defesa, services_defesa
from sigtcc.apps.defesa.choices import PapelBanca
from sigtcc.apps.defesa.forms_defesa import AgendarForm

# Perfis que veem o botão "Agendar defesa" (quem pode agendar em algum curso, RBN-DEF-01.3).
PERFIS_QUE_AGENDAM = ("orientador", "professor_disciplina")

# Campo do formulário de cada papel apontado pelo serviço (US-23 E2). [US-23][RBN-DEF-02.1]
CAMPOS_DA_BANCA = {
    PapelBanca.PRIMEIRO_AVALIADOR: "primeiro_avaliador",
    PapelBanca.SEGUNDO_AVALIADOR: "segundo_avaliador",
}


@perfil_requerido()
def defesas(request):
    """Tela Defesas (US-21 passos 1 e 2; US-40): sessões do Período Letivo atual que o perfil
    pode ver, em ordem cronológica, e o botão "Agendar defesa" para quem agenda.
    [US-21][US-40][RBN-DEF-01.4][RBN-DEF-01.5][FR-024][FR-028]
    """
    contexto = {
        "sessoes": services_defesa.listar_defesas(
            request.user, periodo=services_defesa.filtro_de_periodo("periodo_letivo")
        ),
        "pode_agendar": tem_perfil(request.user, *PERFIS_QUE_AGENDAM),
        "url_agendar": reverse("defesa:agendar"),
    }
    return render(request, "defesa/defesas.html", contexto)


@perfil_requerido("docente")
def turma_defesas(request, tur_id):
    """Aba Defesas da turma (US-21, fluxo A): as sessões dos alunos da turma, só para o
    Professor da Disciplina; "Agendar defesa" abre o formulário limitado à turma.
    [US-21][US-40][RBN-DEF-01.4][FR-006][FR-024]
    """
    turma = get_object_or_404(Turmas.objects.select_related("tur_cur"), pk=tur_id)
    if turma.tur_doc_id != request.user.pk:
        raise PermissionDenied
    contexto = {
        "turma": turma,
        "sessoes": services_defesa.listar_defesas(request.user).filter(def_tcc__tcc_tur=turma),
        "arquivada": turma_arquivada(turma),
        "url_agendar": f"{reverse('defesa:agendar')}?turma={turma.pk}",
    }
    return render(request, "defesa/turma_defesas.html", contexto)


def _origem(request):
    """Tela de onde veio o agendamento, para onde ele volta (US-24 passo 8: "mantém o usuário na
    tela"): a aba Defesas da turma, a tela de orientandos ou a tela Defesas.
    [US-21][US-24][FR-006]
    """
    turma = request.GET.get("turma", "")
    if turma.isdigit():
        return reverse("defesa:turma_defesas", args=[int(turma)])
    if request.GET.get("de") == "orientacoes":
        return reverse("cadastro:orientacoes")
    return reverse("defesa:defesas")


def _tccs_para_o_formulario(request):
    """TCCs elegíveis do usuário, limitados ao `?tcc=` (tela de orientandos) ou à `?turma=` (aba
    Defesas da turma). Com `?tcc=` de um TCC que o usuário não pode agendar pelo curso: E7.
    [US-21][RBN-DEF-01.1][RBN-DEF-01.3][FR-003][FR-006]
    """
    tccs = services_defesa.tccs_elegiveis(request.user)
    tcc_id, tur_id = request.GET.get("tcc", ""), request.GET.get("turma", "")
    if tcc_id.isdigit():
        tcc = get_object_or_404(TCCs.objects.select_related("tcc_tur__tur_cur"), pk=tcc_id)
        if not permissoes_defesa.pode_agendar(request.user, tcc):
            raise PermissionDenied(mensagens.TCC_NAO_AGENDAVEL)
        tccs = tccs.filter(pk=tcc.pk)
    elif tur_id.isdigit():
        tccs = tccs.filter(tcc_tur_id=int(tur_id))
    return tccs


@perfil_requerido("docente")
def agendar(request):
    """ "Agendar sessão de defesa" (US-21 e US-23; botão Agendar: US-22 e US-24). Sem TCC
    elegível, não abre o formulário e volta com a E2. Recusas do serviço voltam ao formulário com
    a mensagem, sem gravar nada; sucesso volta à tela de origem com "Defesa agendada com
    sucesso". [US-21][US-22][US-23][US-24][RBN-DEF-01.1][RBN-DEF-01.3][RBN-DEF-03.1]
    [RBN-DEF-03.2][FR-001 a FR-006][FR-014 a FR-016][FR-018]
    """
    voltar = _origem(request)
    tccs = _tccs_para_o_formulario(request)
    if not tccs.exists():
        messages.error(request, mensagens.NENHUM_TCC_DISPONIVEL)
        return redirect(voltar)
    form = AgendarForm(request.POST or None, tccs=tccs)
    if request.method == "POST" and form.is_valid():
        try:
            services_defesa.agendar(
                request.user,
                form.cleaned_data["tcc"].pk,
                form.dados_basicos(),
                form.dados_banca(),
            )
        except TurmaArquivada:
            messages.warning(request, mensagens_cadastro.MT25_TURMA_ARQUIVADA)
            return redirect(voltar)
        except services_defesa.ErroDefesa as erro:
            form.add_error(CAMPOS_DA_BANCA.get(erro.campo), erro.mensagem)
        else:
            messages.success(request, mensagens.DEFESA_AGENDADA)
            return redirect(voltar)
    contexto = {"form": form, "url_cancelar": voltar, "titulo": "Agendar sessão de defesa"}
    return render(request, "defesa/form_agendar.html", contexto)
