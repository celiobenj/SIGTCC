"""Downloads dos documentos da defesa (spec 009; contracts/rotas.md; research B3 a B5): Ata Final e
Folha de Aprovação em PDF, gerados sob demanda, sem gravar arquivo (SC-003). As views só
orquestram: as regras ficam em permissoes_defesa e services_documentos.

Recusas (research B3): sem login, o login com next (perfil_requerido); sem permissão ou antes da
liberação, 403 com "Você não tem permissão para acessar os documentos desta defesa"; Folha de
TCC 1 ou Reprovado, E2 e falha na geração (E3) voltam à origem (janela da sessão ou aba Meu
TCC, pelo parâmetro `origem`, com valores fixos) com a mensagem exata.

Spec 009 (US6): a agenda de defesas em PDF, a partir dos filtros da tela Defesas (RBN-DEF-08.1).
Spec 009 (US5): a segunda via da declaração de participação (RBN-DEF-08.3).

[US-28][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-07.3][US-30][RBN-DEF-08.1][RBN-DEF-08.3]
"""

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse

from sigtcc.apps.cadastro import services_contas
from sigtcc.apps.cadastro.permissoes import perfil_requerido, tem_perfil
from sigtcc.apps.defesa import (
    mensagens,
    pdf,
    permissoes_defesa,
    services_defesa,
    services_documentos,
    views_defesa,
)
from sigtcc.apps.defesa.forms_defesa import FiltroDefesasForm

TEMPLATE_ATA = "defesa/pdf/ata_final.html"
TEMPLATE_FOLHA = "defesa/pdf/folha_aprovacao.html"
TEMPLATE_AGENDA = "defesa/pdf/agenda.html"
ORIGEM_MEU_TCC = "meu_tcc"


def _sessao_com_permissao(request, def_id):
    """Sessão do download, já conferida: sem permissão de baixar os documentos (inclusive o
    Suplente não acionado e antes da liberação), 403 com o texto da US-28 E6 (P5, P13).
    [US-28][RBN-DEF-07.3]
    """
    registro = views_defesa.sessao_ou_404(def_id)
    if not permissoes_defesa.pode_baixar_documentos(request.user, registro):
        raise PermissionDenied(mensagens.SEM_PERMISSAO_DOCUMENTOS)
    return registro


def _voltar(request, registro, texto):
    """Mostra a recusa e volta à origem do download: a aba Meu TCC com `origem=meu_tcc`; a
    janela da sessão com qualquer outro valor (nunca uma URL livre). [US-28][RBN-DEF-07.3]
    """
    messages.error(request, texto)
    if request.GET.get("origem") == ORIGEM_MEU_TCC:
        return redirect("cadastro:meu_tcc", tur_id=registro.def_tcc.tcc_tur_id)
    return redirect("defesa:sessao", def_id=registro.pk)


def _baixar(request, registro, nome_arquivo, template, contexto):
    """Gera e entrega o PDF; falha na geração (E3): nada é entregue nem gravado, o motivo já foi
    ao log (pdf.gerar_pdf) e a mensagem da US-28 E3 aparece na origem.
    [US-28][RBN-DEF-07.1][RBN-DEF-07.2]
    """
    try:
        return pdf.resposta_pdf(nome_arquivo, template, contexto)
    except pdf.ErroAoGerarPdf:
        return _voltar(request, registro, mensagens.ERRO_AO_GERAR_DOCUMENTOS)


@perfil_requerido()
def ata_final(request, def_id):
    """Download da Ata Final (FR-001, FR-005 a FR-008). Com a E2 (curso sem Coordenador ou
    Coordenador sem assinatura no perfil), não gera o PDF: o Presidente da banca vê a mensagem da
    US-28 E2 e os demais perfis a MX-08, sem nova notificação (P1).
    [US-28][RBN-DEF-07.1][RBN-DEF-07.3][RBN-CAD-13.1]
    """
    registro = _sessao_com_permissao(request, def_id)
    if services_documentos.situacao_da_ata(registro) is not None:
        if permissoes_defesa.e_presidente(request.user, registro):
            return _voltar(request, registro, mensagens.ATA_SEM_ASSINATURA_COORDENADOR)
        return _voltar(request, registro, mensagens.MX08_ATA_INDISPONIVEL)
    return _baixar(
        request,
        registro,
        f"ata_final_{registro.pk}.pdf",
        TEMPLATE_ATA,
        services_documentos.dados_da_ata(registro),
    )


@perfil_requerido()
def folha_aprovacao(request, def_id):
    """Download da Folha de Aprovação (FR-002, FR-004, FR-005, FR-007): TCC 1 e Reprovado são
    recusados com a mensagem da US-28 (cenários 12 e 13), também pelo endereço direto.
    [US-28][RBN-DEF-07.2][RBN-DEF-07.3]
    """
    registro = _sessao_com_permissao(request, def_id)
    recusa = services_documentos.folha_aplicavel(registro)
    if recusa is not None:
        return _voltar(request, registro, recusa)
    return _baixar(
        request,
        registro,
        f"folha_aprovacao_{registro.pk}.pdf",
        TEMPLATE_FOLHA,
        services_documentos.dados_da_folha(registro),
    )


@perfil_requerido()
def declaracao(request, def_id):
    """Segunda via da declaração de participação (US-30 D; FR-020 e FR-021): só ao membro
    efetivo e depois da liberação (senão 403 com o texto da US-28 E6, inclusive ao Suplente não
    acionado, ao Aluno e à Secretaria; P13), com o mesmo conteúdo e o mesmo código do e-mail
    (dados_da_declaracao). Falha na geração: a mensagem da US-28 E3, de volta à sessão.
    [US-30][RBN-DEF-08.3][RBN-DEF-05.4]
    """
    registro = views_defesa.sessao_ou_404(def_id)
    if not permissoes_defesa.pode_baixar_declaracao(request.user, registro):
        raise PermissionDenied(mensagens.SEM_PERMISSAO_DOCUMENTOS)
    return _baixar(
        request,
        registro,
        services_documentos.nome_da_declaracao(registro.pk),
        services_documentos.TEMPLATE_DECLARACAO,
        services_documentos.dados_da_declaracao(registro, request.user),
    )


def _voltar_para_defesas(request, texto=None):
    """Volta à tela Defesas com a query string original (que mostra os erros do filtro) e, se
    houver, a mensagem. [US-30][RBN-DEF-08.1]
    """
    if texto:
        messages.error(request, texto)
    destino = reverse("defesa:defesas")
    consulta = request.GET.urlencode()
    return redirect(f"{destino}?{consulta}" if consulta else destino)


@perfil_requerido("docente", "coordenador", "secretaria")
def agenda(request):
    """ "Agenda de defesas (PDF)" (US-30 F; FR-022 a FR-024): com os mesmos parâmetros da tela
    Defesas, as sessões Agendadas e Reagendadas do período, de todos os cursos (P2) ou, para o
    Coordenador e a Secretaria, do curso do filtro. Antes, o início automático das sessões
    vencidas. Filtro inválido: volta à tela Defesas com a query string original, sem PDF; sem
    sessões: "Não existem defesas agendadas para o período selecionado", sem arquivo; falha na
    geração: a mensagem da US-28 E3. O Aluno e o Membro Externo recebem a M-02.
    [US-30][RBN-DEF-08.1][RBN-DEF-01.5][RBN-CAD-14.1]
    """
    if not permissoes_defesa.pode_gerar_agenda(request.user):
        raise PermissionDenied
    services_defesa.iniciar_sessoes_vencidas()
    form = FiltroDefesasForm(request.GET or None)
    if form.is_bound and not form.is_valid():
        return _voltar_para_defesas(request)
    cur_id = None
    if tem_perfil(request.user, "coordenador", "secretaria"):
        cur_id, _ = services_contas.filtro_de_curso(request.user, request.GET.get("curso"))
    dias = services_documentos.agenda_de_defesas(request.user, form.filtro(), cur_id)
    if not dias:
        return _voltar_para_defesas(request, mensagens.SEM_DEFESAS_AGENDADAS)
    try:
        return pdf.resposta_pdf("agenda_defesas.pdf", TEMPLATE_AGENDA, {"dias": dias})
    except pdf.ErroAoGerarPdf:
        return _voltar_para_defesas(request, mensagens.ERRO_AO_GERAR_DOCUMENTOS)
