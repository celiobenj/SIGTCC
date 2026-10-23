"""Views da aba Meu TCC e do histórico do Status do app cadastro (spec 005).

Views finas (orquestram `services_tcc`, sem regra de negócio): aba Meu TCC, com a Proposta, o
Status e a Versão Final (US-13, US-14, US-29); consulta do histórico do Status pelo Aluno, pelo
Orientador e pelo Professor da Disciplina (US-14).

[US-13][US-14][US-29][RBN-CAD-07.1][RBN-CAD-08.1 a 08.8][research C1]
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render

from sigtcc.apps.cadastro import mensagens, services_tcc, services_turmas
from sigtcc.apps.cadastro.choices import StatusTCC
from sigtcc.apps.cadastro.forms_tcc import DadosTCCForm, PropostaForm
from sigtcc.apps.cadastro.permissoes import perfil_requerido


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


@perfil_requerido("aluno")
def meu_tcc(request, tur_id):
    """Aba Meu TCC: seção Proposta (sempre) e, depois de salva, Área de Interesse e Palavras-
    Chave. GET exibe conforme o Status do TCC (editável, com Área/Palavras-Chave liberadas, ou
    somente leitura); POST chama `salvar_proposta` (botão "Salvar Proposta") ou
    `salvar_alteracoes_tcc` (botão "Salvar alterações"). Restrita ao próprio Aluno da turma
    (`vinculo_na_turma`, sem IDOR).
    [US-13][RBN-CAD-07.1][RBN-CAD-08.1][RBN-CAD-08.2][FR-001][FR-006][contracts/rotas.md]
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
    }
    return render(request, "cadastro/tcc/meu_tcc.html", contexto)
