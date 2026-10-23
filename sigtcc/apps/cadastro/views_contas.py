"""Views da Gestão de Contas (spec 002): só orquestram; as regras ficam em services_contas.py.

Ordem das conferências nas rotas com id (research C22, C11): registro pela especialização (404) →
perfil (403, M-02) → curso (403 com a mensagem do FR-009) → status. Toda ação que grava redireciona
depois do POST (PRG).

[US-03][US-04][US-05][US-50][FR-009][FR-010][research C21][C22]
"""

from django.shortcuts import render

from sigtcc.apps.cadastro.services_contas import ForaDoCurso


def recusa_fora_do_curso(request, erro):
    """Página de acesso não permitido com a mensagem do FR-009 e status 403 (research C21).

    erro: ForaDoCurso, com o texto "Você só pode cadastrar e alterar dados do seu curso" ou "Você
    só pode alterar dados do seu curso". Nenhum dado do registro aparece na resposta.
    [US-03][US-04][RBN-CAD-14.1][FR-009][SC-004]
    """
    assert isinstance(erro, ForaDoCurso)
    return render(request, "acesso_negado.html", {"mensagem": erro.mensagem}, status=403)
