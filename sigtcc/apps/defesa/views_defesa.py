"""Views do módulo de Defesa (spec 007; contracts/rotas.md). Views finas: as regras ficam em
services_defesa e permissoes_defesa.

[US-21][US-22][US-23][US-24][US-40]
"""

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import urlencode

from sigtcc.apps.cadastro import mensagens as mensagens_cadastro
from sigtcc.apps.cadastro import services_contas
from sigtcc.apps.cadastro.models import Cursos, TCCs, Turmas, Usuarios
from sigtcc.apps.cadastro.permissoes import perfil_requerido, tem_perfil
from sigtcc.apps.cadastro.services_turmas import TurmaArquivada, turma_arquivada
from sigtcc.apps.defesa import mensagens, permissoes_defesa, services_defesa
from sigtcc.apps.defesa.choices import PapelBanca
from sigtcc.apps.defesa.forms_defesa import CAMPOS_DA_BANCA as CAMPOS_DO_FORMULARIO
from sigtcc.apps.defesa.forms_defesa import (
    AcionarSuplenteForm,
    AgendarForm,
    AlterarBancaForm,
    CancelarForm,
    FiltroDefesasForm,
    ReagendarForm,
)
from sigtcc.apps.defesa.models import Defesas
from sigtcc.apps.defesa.templatetags.defesa_tags import lugar

# Perfis que veem o botão "Agendar defesa" (quem pode agendar em algum curso, RBN-DEF-01.3).
PERFIS_QUE_AGENDAM = ("orientador", "professor_disciplina")

# Campo do formulário de cada papel apontado pelo serviço (US-23 E2). [US-23][RBN-DEF-02.1]
CAMPOS_DA_BANCA = {papel: campo for campo, papel in CAMPOS_DO_FORMULARIO.items()}

# Campos do agendamento que voltam preenchidos do cadastro rápido do Membro Externo.
CAMPOS_QUE_VOLTAM = ("tcc", "data", "h_inicio", "formato", "local", "link", *CAMPOS_DO_FORMULARIO)


@perfil_requerido()
def defesas(request):
    """Tela Defesas (US-21 passos 1 e 2; US-40): sessões que o perfil pode ver, em ordem
    cronológica, com os filtros de período (Período Letivo por padrão), Status e, para o
    Coordenador de Curso e a Secretaria, Curso (US-39, com o curso do usuário por padrão); o
    botão "Agendar defesa" para quem agenda. Filtro inválido (E3, E4): mostra a mensagem e a
    lista do Período Letivo, sem aplicar o filtro.
    [US-21][US-40][US-39][RBN-DEF-01.4][RBN-DEF-01.5][RBN-CAD-14.1][FR-024 a FR-028]
    """
    services_defesa.iniciar_sessoes_vencidas()
    form = FiltroDefesasForm(request.GET or None)
    valido = form.is_valid()
    gestao = tem_perfil(request.user, "coordenador", "secretaria")
    cur_id, curso = None, ""
    if gestao:
        cur_id, curso = services_contas.filtro_de_curso(request.user, request.GET.get("curso"))
    contexto = {
        "form": form,
        "sessoes": services_defesa.listar_defesas(
            request.user,
            periodo=form.filtro(),
            status=form.cleaned_data.get("status") if valido else None,
            cur_id=cur_id,
        ),
        "mostra_curso": gestao,
        "cursos": Cursos.objects.order_by("cur_nome") if gestao else [],
        "curso": curso,
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
    services_defesa.iniciar_sessoes_vencidas()
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
    form = AgendarForm(request.POST or None, tccs=tccs, initial=_iniciais(request))
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
            _erro_no_formulario(form, erro)
        else:
            messages.success(request, mensagens.DEFESA_AGENDADA)
            return redirect(voltar)
    contexto = {
        "form": form,
        "url_cancelar": voltar,
        "titulo": "Agendar sessão de defesa",
        "url_cadastrar_externo": _atalho_do_externo(request),
        "texto_cadastrar_externo": mensagens.LINK_CADASTRAR_EXTERNO,
    }
    return render(request, "defesa/form_agendar.html", contexto)


def _atalho_do_externo(request):
    """Link "O Membro Externo não está na lista? Cadastrar" (US-23 B), pelo atalho do contrato
    §3 da spec 002: volta a esta tela com `membro=<id>` (o JavaScript acrescenta os campos já
    preenchidos e o `campo` em foco). [US-23][RBN-DEF-02.3][FR-010]
    """
    return (
        f"{reverse('cadastro:contas_membro_novo')}?{urlencode({'voltar': request.get_full_path()})}"
    )


def _iniciais(request):
    """Valores iniciais na volta do cadastro rápido: os campos que vieram na query e o Membro
    Externo recém-cadastrado no `campo` que estava sendo preenchido. O `membro` é conferido (está
    em membros_externos_disponiveis), nunca aceito às cegas (contrato §3 da spec 002).
    [US-23][RBN-DEF-02.3][FR-010]
    """
    if request.method != "GET":
        return {}
    iniciais = {campo: request.GET[campo] for campo in CAMPOS_QUE_VOLTAM if request.GET.get(campo)}
    membro, campo = request.GET.get("membro", ""), request.GET.get("campo", "")
    if (
        membro.isdigit()
        and campo in CAMPOS_DO_FORMULARIO
        and services_contas.membros_externos_disponiveis().filter(pk=int(membro)).exists()
    ):
        iniciais[campo] = int(membro)
    return iniciais


def _sessao_ou_404(def_id):
    """Sessão com o TCC, a turma e o aluno já carregados, depois do início automático das
    sessões cujo horário chegou (US-24 D), para o status e os botões valerem já.
    [US-23][US-24][US-40][FR-021]
    """
    services_defesa.iniciar_sessoes_vencidas()
    return get_object_or_404(
        Defesas.objects.select_related(
            "def_tcc__tcc_tur__tur_cur",
            "def_tcc__tcc_alu__alu",
            "defesaspresenciais",
            "defesasremotas",
        ),
        pk=def_id,
    )


@perfil_requerido()
def sessao(request, def_id):
    """Janela "Sessão de defesa" (US-40 passo 8): aluno, título, data, horário, formato, local ou
    link, status e banca, com os botões que o perfil e o status permitem; os blocos de avaliação,
    resultado, documentos, ouvintes e ocorrências ficam para a feat-08 e a feat-09 (contrato §3).
    Sem permissão, também pelo endereço direto: US-40 E5.
    [US-40][US-23][US-24][RBN-DEF-01.4][FR-030]
    """
    registro = _sessao_ou_404(def_id)
    if not permissoes_defesa.pode_ver_sessao(request.user, registro):
        raise PermissionDenied(mensagens.SEM_PERMISSAO_SESSAO)
    banca = services_defesa.banca_por_papel(registro)
    ordem = (*services_defesa.PAPEIS_TITULARES, PapelBanca.SUPLENTE)
    contexto = {
        "sessao": registro,
        "banca": [(papel, banca[papel]) for papel in ordem if papel in banca],
        "substituicoes": services_defesa.substituicoes(registro),
        "pode_alterar_banca": permissoes_defesa.pode_alterar_banca(request.user, registro),
        "pode_acionar_suplente": permissoes_defesa.pode_acionar_suplente(request.user, registro),
        "pode_reagendar_ou_cancelar": permissoes_defesa.pode_reagendar_ou_cancelar(
            request.user, registro
        ),
    }
    return render(request, "defesa/sessao.html", contexto)


def _erro_no_formulario(form, erro):
    """Mostra a recusa do serviço no campo apontado (ou no topo do formulário).
    [US-23][US-24]
    """
    campo = CAMPOS_DA_BANCA.get(erro.campo, erro.campo)
    form.add_error(campo if campo in form.fields else None, erro.mensagem)


@perfil_requerido("docente")
def alterar_banca(request, def_id):
    """ "Alterar banca" (US-23 C): só quem pode agendar o TCC, com a sessão Agendada ou
    Reagendada (senão M-02). Recusas (E3 a E7 e conflito, US-22 E) voltam ao formulário sem
    gravar; sucesso volta à sessão com a MD-09.
    [US-23][US-22][RBN-DEF-02.4][RBN-DEF-03.1][FR-011][FR-012][FR-015]
    """
    registro = _sessao_ou_404(def_id)
    if not permissoes_defesa.pode_alterar_banca(request.user, registro):
        raise PermissionDenied
    banca = services_defesa.banca_por_papel(registro)
    form = AlterarBancaForm(request.POST or None, sessao=registro, banca=banca)
    if request.method == "POST" and form.is_valid():
        nova = form.nova_banca()
        presidente = request.POST.get("presidente", "")
        if presidente.isdigit():
            nova[PapelBanca.ORIENTADOR_PRESIDENTE] = Usuarios.objects.filter(
                pk=int(presidente)
            ).first()
        try:
            services_defesa.alterar_banca(
                request.user, registro.pk, nova, form.cleaned_data["justificativa"]
            )
        except services_defesa.ErroDefesa as erro:
            _erro_no_formulario(form, erro)
        else:
            messages.success(request, mensagens.MD09_BANCA_ALTERADA)
            return redirect("defesa:sessao", def_id=registro.pk)
    contexto = {"form": form, "sessao": registro, "presidente": form.presidente}
    return render(request, "defesa/form_alterar_banca.html", contexto)


@perfil_requerido("docente")
def acionar_suplente(request, def_id):
    """ "Acionar suplente" (US-23 D): exclusivamente o Orientador, com a sessão Em Andamento e
    Suplente na banca (senão M-02, "Você não tem permissão para esta ação", E10). Justificativa
    vazia ou longa: não efetiva (E9). [US-23][RBN-DEF-02.2][FR-013]
    """
    registro = _sessao_ou_404(def_id)
    if not permissoes_defesa.pode_acionar_suplente(request.user, registro):
        raise PermissionDenied
    banca = services_defesa.banca_por_papel(registro)
    form = AcionarSuplenteForm(request.POST or None, banca=banca)
    if request.method == "POST" and form.is_valid():
        try:
            services_defesa.acionar_suplente(
                request.user,
                registro.pk,
                form.cleaned_data["papel_substituido"],
                form.cleaned_data["justificativa"],
            )
        except services_defesa.ErroDefesa as erro:
            _erro_no_formulario(form, erro)
        else:
            messages.success(request, mensagens.MD10_SUPLENTE_ACIONADO)
            return redirect("defesa:sessao", def_id=registro.pk)
    contexto = {"form": form, "sessao": registro, "suplente": banca[PapelBanca.SUPLENTE]}
    return render(request, "defesa/form_acionar_suplente.html", contexto)


@perfil_requerido("docente", "secretaria")
def reagendar(request, def_id):
    """ "Reagendar sessão de defesa" (US-24 B): quem pode agendar o TCC ou a Secretaria do curso,
    com a sessão Agendada, Reagendada ou Em Andamento (senão M-02, E4 e E5). Conflito (E2):
    volta ao formulário com os dados digitados; sucesso volta à sessão com a MD-11.
    [US-24][US-22][RBN-DEF-03.3][RBN-DEF-03.1][FR-019][FR-022]
    """
    registro = _sessao_ou_404(def_id)
    if not permissoes_defesa.pode_reagendar_ou_cancelar(request.user, registro):
        raise PermissionDenied
    form = ReagendarForm.da_sessao(registro, lugar(registro), request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            services_defesa.reagendar(
                request.user,
                registro.pk,
                form.dados_basicos(),
                form.cleaned_data["justificativa"],
            )
        except services_defesa.ErroDefesa as erro:
            _erro_no_formulario(form, erro)
        else:
            messages.success(request, mensagens.MD11_SESSAO_REAGENDADA)
            return redirect("defesa:sessao", def_id=registro.pk)
    contexto = {
        "form": form,
        "sessao": registro,
        "banca": services_defesa.banca_por_papel(registro).items(),
        "aviso_banca": mensagens.MD13_BANCA_MANTIDA,
    }
    return render(request, "defesa/form_reagendar.html", contexto)


@perfil_requerido("docente", "secretaria")
def cancelar(request, def_id):
    """ "Cancelar sessão" (US-24 C): as mesmas permissões do reagendamento; pede a Justificativa
    e a confirmação. O TCC continua "Apto para Defesa". Sucesso volta à sessão com a MD-12.
    [US-24][RBN-DEF-03.3][FR-020][FR-022]
    """
    registro = _sessao_ou_404(def_id)
    if not permissoes_defesa.pode_reagendar_ou_cancelar(request.user, registro):
        raise PermissionDenied
    form = CancelarForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            services_defesa.cancelar(request.user, registro.pk, form.cleaned_data["justificativa"])
        except services_defesa.ErroDefesa as erro:
            _erro_no_formulario(form, erro)
        else:
            messages.success(request, mensagens.MD12_SESSAO_CANCELADA)
            return redirect("defesa:sessao", def_id=registro.pk)
    return render(request, "defesa/confirmar_cancelar.html", {"form": form, "sessao": registro})


@perfil_requerido()
def historico(request, def_id):
    """Janela "Histórico da defesa" (US-40 passos 9 a 11): linha do tempo, somente leitura, dos
    eventos de todas as sessões do TCC, com data, hora, responsável e justificativa; as mesmas
    permissões da sessão (US-40 E5). [US-40][RBN-DEF-01.6][FR-029][FR-030]
    """
    registro = _sessao_ou_404(def_id)
    if not permissoes_defesa.pode_ver_sessao(request.user, registro):
        raise PermissionDenied(mensagens.SEM_PERMISSAO_SESSAO)
    contexto = {"sessao": registro, "eventos": services_defesa.historico_da_sessao(registro)}
    return render(request, "defesa/historico.html", contexto)
