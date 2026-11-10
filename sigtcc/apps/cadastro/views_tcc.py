"""Views da aba Meu TCC e do histórico do Status do app cadastro (spec 005).

Views finas (orquestram `services_tcc`, sem regra de negócio): aba Meu TCC, com a Proposta, o
Status e a Versão Final (US-13, US-14, US-29); consulta do histórico do Status pelo Aluno, pelo
Orientador e pelo Professor da Disciplina (US-14).

[US-13][US-14][US-29][RBN-CAD-07.1][RBN-CAD-08.1 a 08.8][research C1]
"""

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from sigtcc.apps.cadastro import (
    mensagens,
    services_artigos,
    services_entregas,
    services_orientacao,
    services_tcc,
    services_turmas,
)
from sigtcc.apps.cadastro.choices import StatusTCC
from sigtcc.apps.cadastro.forms_artigos import PublicacaoForm
from sigtcc.apps.cadastro.forms_entregas import EnviarLinkForm
from sigtcc.apps.cadastro.forms_tcc import DadosTCCForm, PropostaForm
from sigtcc.apps.cadastro.models import EncontroOrientacao
from sigtcc.apps.cadastro.permissoes import perfil_requerido
from sigtcc.apps.cadastro.services_turmas import CONSULTAR, TurmaArquivada


def _turmas_do_aluno(request, arquivadas):
    """Lista do item "Turmas" do Aluno (ativas ou arquivadas), com o link para a outra lista.

    [US-13][FR-031][Q-89]
    """
    contexto = {
        "turmas": services_tcc.turmas_do_aluno(request.user, arquivadas=arquivadas),
        "arquivadas": arquivadas,
    }
    return render(request, "cadastro/tcc/minhas_turmas.html", contexto)


@perfil_requerido("aluno")
def minhas_turmas(request):
    """Item de menu "Turmas" do Aluno (passo 1 das US-13, 14, 15 e 29): as turmas não arquivadas
    em que ele está matriculado; cada uma abre a aba "Meu TCC". Não dá acesso à tela da turma da
    spec 004, que continua só do Professor e da Secretaria (FR-010 da spec 004).
    [US-13][US-15][FR-031][Q-89][contracts/rotas.md]
    """
    return _turmas_do_aluno(request, arquivadas=False)


@perfil_requerido("aluno")
def minhas_turmas_arquivadas(request):
    """ "Turmas arquivadas" do Aluno (E9 da US-13): só consulta; cada turma abre "Meu TCC" sem os
    botões de salvar (a própria `meu_tcc` já trata a turma arquivada).
    [US-13][FR-006][FR-031][Q-89][contracts/rotas.md]
    """
    return _turmas_do_aluno(request, arquivadas=True)


def _proposta_inicial(tcc):
    """Valores atuais da Proposta para o formulário (GET). [US-13][FR-001]"""
    return {
        "titulo": tcc.tcc_titulo,
        "subtitulo": tcc.tcc_subtitulo,
        "resumo": tcc.tcc_resumo,
        "modalidade": tcc.tcc_modalidade,
        "link": tcc.tcc_link_proposta,
    }


def _dados_iniciais(tcc):
    """Área de Interesse e Palavras-Chave atuais para o formulário (GET). [US-13][FR-004]"""
    inicial = {"area_interesse": tcc.tcc_ari_id}
    for indice, palavra in enumerate(services_tcc.palavras_chave_do(tcc), start=1):
        if indice > services_tcc.MAXIMO_PALAVRAS_CHAVE:
            break
        inicial[f"palavra_chave_{indice}"] = palavra
    return inicial


def _form_versao_final(versao_final):
    """Formulário do Link da Versão Final, preenchido com o link mais recente já enviado, para o
    Aluno substituí-lo (US-29, fluxo D; FR-019). [US-29][FR-019]
    """
    ultimo = versao_final["ultimo_envio"] if versao_final else None
    return EnviarLinkForm(initial={"link": ultimo.hen_link if ultimo else ""})


@perfil_requerido("aluno")
def meu_tcc(request, tur_id):
    """Aba Meu TCC: seção Proposta (sempre) e, depois de salva, Área de Interesse e Palavras-
    Chave. GET exibe conforme o Status do TCC (editável, com Área/Palavras-Chave liberadas, ou
    somente leitura); POST chama `salvar_proposta` (botão "Salvar Proposta") ou
    `salvar_alteracoes_tcc` (botão "Salvar alterações"). Em turma de TCC 2, também a seção
    "Versão final" (US-29), cujo botão Enviar posta em `entrega_enviar`. Restrita ao próprio
    Aluno da turma (`vinculo_na_turma`, sem IDOR).
    [US-13][US-29][RBN-CAD-07.1][RBN-CAD-08.1][RBN-CAD-08.2][FR-001][FR-006][FR-023][FR-024]
    [contracts/rotas.md]
    """
    turma, aluno = services_tcc.turma_do_aluno(tur_id, request.user)
    tcc = services_turmas.tcc_do_aluno(turma, aluno)
    if tcc is None:
        raise Http404
    arquivada = services_turmas.turma_arquivada(turma)
    proposta_existe = tcc.tcc_status != StatusTCC.SEM_PROPOSTA
    pode_salvar_proposta = tcc.tcc_status == StatusTCC.SEM_PROPOSTA and not arquivada
    pode_salvar_alteracoes = tcc.tcc_status == StatusTCC.EM_ANDAMENTO and not arquivada
    somente_leitura = not (pode_salvar_proposta or pode_salvar_alteracoes)

    proposta_form = PropostaForm(initial=_proposta_inicial(tcc), somente_leitura=somente_leitura)
    dados_form = (
        DadosTCCForm(initial=_dados_iniciais(tcc), somente_leitura=somente_leitura)
        if proposta_existe
        else None
    )

    if request.method == "POST":
        acao = request.POST.get("acao")
        # A turma pode ser arquivada entre a abertura da tela e o salvamento: os serviços travam
        # a turma e levantam TurmaArquivada; a tela volta à aba Meu TCC (só consulta) com a MT-25,
        # sem erro 500 (FR-006; a tela da turma da spec 004, destino de trata_turma_arquivada, é
        # fechada ao Aluno). [US-13][FR-006][SC-004]
        try:
            if acao == "salvar_proposta" and pode_salvar_proposta:
                proposta_form = PropostaForm(request.POST)
                if proposta_form.is_valid():
                    services_tcc.salvar_proposta(aluno, tur_id, proposta_form.cleaned_data)
                    messages.success(request, mensagens.PROPOSTA_SALVA)
                    return redirect("cadastro:meu_tcc", tur_id=tur_id)
            elif acao == "salvar_alteracoes" and pode_salvar_alteracoes:
                proposta_form = PropostaForm(request.POST)
                dados_form = DadosTCCForm(request.POST)
                if proposta_form.is_valid() and dados_form.is_valid():
                    dados = {**proposta_form.cleaned_data, **dados_form.cleaned_data}
                    try:
                        services_tcc.salvar_alteracoes_tcc(tcc, dados)
                    except services_tcc.ErroTCC as erro:
                        messages.error(request, erro.mensagem)
                    else:
                        messages.success(request, mensagens.ALTERACOES_SALVAS)
                        return redirect("cadastro:meu_tcc", tur_id=tur_id)
        except TurmaArquivada:
            messages.warning(request, mensagens.MT25_TURMA_ARQUIVADA)
            return redirect("cadastro:meu_tcc", tur_id=tur_id)

    versao_final = services_entregas.secao_versao_final(aluno, turma, tcc)
    publicacao = services_artigos.contexto_publicacao(tcc)
    contexto = {
        "turma": turma,
        "tcc": tcc,
        "proposta_form": proposta_form,
        "dados_form": dados_form,
        "proposta_existe": proposta_existe,
        "pode_salvar_proposta": pode_salvar_proposta,
        "pode_salvar_alteracoes": pode_salvar_alteracoes,
        "somente_leitura": somente_leitura,
        "arquivada": arquivada,
        # Seção "Versão final" (US-29, T028): None em TCC 1 ou sem a entrega cadastrada (E4).
        "versao_final": versao_final,
        "versao_final_pendente": mensagens.VERSAO_FINAL_DISPONIVEL_APOS_RESULTADO,
        "versao_final_atraso": mensagens.MF01_DATA_LIMITE_VENCIDA,
        # Campo Link da Versão Final com o link já enviado (US-29, fluxo D; FR-019).
        "form_versao_final": _form_versao_final(versao_final),
        # Spec 006 (IC-09): seção Orientação (US-17, US-45; FR-001 a FR-007, FR-049).
        "orientacao": services_orientacao.contexto_secao_orientacao(tcc),
        # Spec 006 (IC-09): seção Publicação do artigo (US-46; FR-034), só em Artigo Científico.
        "publicacao": publicacao,
        "form_publicacao": (PublicacaoForm(initial=publicacao["inicial"]) if publicacao else None),
        # Spec 006 (IC-09): seção Atas de orientação (US-19; FR-022).
        "atas": {
            "n": EncontroOrientacao.objects.filter(enc_tcc=tcc).count(),
            "pode_registrar": services_orientacao.pode_alterar_no_tcc(tcc),
        },
    }
    return render(request, "cadastro/tcc/meu_tcc.html", contexto)


@perfil_requerido("aluno")
def historico_status_aluno(request, tur_id):
    """Histórico do Status do TCC do próprio Aluno (sem edição manual, FR-008): lista
    cronológica e trilha com a etapa atual destacada. Restrita ao próprio Aluno da turma
    (`vinculo_na_turma`, sem IDOR), como `meu_tcc`.
    [US-14][RBN-CAD-08.3][RBN-CAD-08.7][RBN-CAD-08.8][FR-009][FR-010][contracts/rotas.md]
    """
    turma, aluno = services_tcc.turma_do_aluno(tur_id, request.user)
    tcc = services_turmas.tcc_do_aluno(turma, aluno)
    if tcc is None:
        raise Http404
    # "Fechar" volta à aba Meu TCC (spec 006, IC-06). [FR-043]
    contexto = services_tcc.contexto_historico(tcc, reverse("cadastro:meu_tcc", args=[turma.pk]))
    return render(request, "cadastro/tcc/historico_status.html", contexto)


@perfil_requerido("docente")
def historico_status(request, tur_id, alu_id):
    """Histórico do Status do TCC de um aluno da turma, para o Professor da Disciplina — nunca
    para a Secretaria do curso nem para o Coorientador (Clarifications; FR-009). `turma_para`
    com a ação CONSULTAR libera Professor e Secretaria; a checagem explícita abaixo exclui a
    Secretaria, porque este histórico é mais restrito que a consulta comum da turma.
    [US-14][RBN-CAD-08.3][RBN-CAD-08.7][RBN-CAD-08.8][FR-009][FR-010][contracts/rotas.md]
    """
    turma = services_turmas.turma_para(request.user, tur_id, CONSULTAR)
    if turma.tur_doc_id != request.user.pk:
        raise PermissionDenied
    aluno = services_turmas.vinculo_na_turma(turma, alu_id)
    tcc = services_turmas.tcc_do_aluno(turma, aluno)
    if tcc is None:
        raise Http404
    # "Fechar" volta ao painel do aluno (spec 006, IC-06; FR-044). [FR-043][FR-044]
    contexto = services_tcc.contexto_historico(
        tcc, reverse("cadastro:painel_aluno", args=[turma.pk, aluno.pk])
    )
    return render(request, "cadastro/tcc/historico_status.html", contexto)
