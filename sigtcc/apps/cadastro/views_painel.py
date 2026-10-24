"""View do painel do aluno (spec 006, US-41): só monta o contexto com os services das specs 003
a 006 (services_orientacao.contexto_painel), sem regra de negócio.

[US-41][RBN-CAD-08.9][research R1]
"""

from django.shortcuts import render

from sigtcc.apps.cadastro import mensagens, services_orientacao
from sigtcc.apps.cadastro.permissoes import perfil_requerido


@perfil_requerido("docente")
def painel_aluno(request, tur_id, alu_id):
    """Rota 25: painel do aluno, aberto pelo bloco da aba "Alunos" (Professor da Disciplina da
    turma; a Secretaria, outro Docente e o Aluno recebem 403, FR-020). Seções só para leitura e os
    botões de ação das specs 003 a 006, que voltam ao painel (?volta=painel); "Fechar" volta à aba
    "Alunos" (FR-044).
    [US-41][RBN-CAD-08.9][FR-017 a FR-020][FR-044][contracts/rotas.md]
    """
    contexto = services_orientacao.contexto_painel(request.user, tur_id, alu_id)
    contexto["texto_resetar"] = mensagens.RESETAR_PRIMEIRO_ACESSO
    return render(request, "cadastro/turmas/painel_aluno.html", contexto)
