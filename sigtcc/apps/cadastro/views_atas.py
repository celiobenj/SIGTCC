"""Views das atas de orientação (spec 006): Aluno, Orientador, Coorientador e Professor da
Disciplina. Views finas sobre services_atas.

[US-19][research R1]
"""

from django.http import Http404

from sigtcc.apps.cadastro.permissoes import perfil_requerido


@perfil_requerido("docente")
def atas_orientando(request, tcc_id):
    """Rota 17. Provisória até a T034 (US4). [US-19][FR-023]"""
    raise Http404


@perfil_requerido("docente")
def registrar_ata_docente(request, tcc_id):
    """Rota 18. Provisória até a T034 (US4). [US-19][FR-022]"""
    raise Http404


@perfil_requerido("docente")
def atas_painel(request, tur_id, alu_id):
    """Rota 26. Provisória até a T034 (US4). [US-19][US-41][FR-023]"""
    raise Http404
