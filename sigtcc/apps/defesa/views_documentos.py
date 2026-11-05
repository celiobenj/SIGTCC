"""Downloads dos documentos da defesa (spec 009; contracts/rotas.md; research B3 a B5): Ata Final e
Folha de Aprovação em PDF, gerados sob demanda, sem gravar arquivo (SC-003). As views só
orquestram: as regras ficam em permissoes_defesa e services_documentos.

Recusas (research B3): sem login, o login com next (perfil_requerido); sem permissão ou antes da
liberação, 403 com "Você não tem permissão para acessar os documentos desta defesa"; Folha de
TCC 1 ou Reprovado, E2 e falha na geração (E3) voltam à origem (janela da sessão ou aba Meu
TCC, pelo parâmetro `origem`, com valores fixos) com a mensagem exata.

[US-28][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-07.3]
"""

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from sigtcc.apps.cadastro.permissoes import perfil_requerido
from sigtcc.apps.defesa import mensagens, pdf, permissoes_defesa, services_documentos, views_defesa

TEMPLATE_ATA = "defesa/pdf/ata_final.html"
TEMPLATE_FOLHA = "defesa/pdf/folha_aprovacao.html"
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
