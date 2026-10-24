"""View do painel do aluno (spec 006, US-41): só monta o contexto com os services das specs 003 a
006.

[US-41][RBN-CAD-08.9][research R1]
"""

from django.http import Http404

from sigtcc.apps.cadastro.permissoes import perfil_requerido


@perfil_requerido("docente")
def painel_aluno(request, tur_id, alu_id):
    """Painel do aluno (rota 25). Provisório até a T027 (US3). [US-41][FR-018]"""
    raise Http404
