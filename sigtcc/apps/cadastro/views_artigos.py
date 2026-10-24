"""Views da publicação do artigo e do aproveitamento (spec 006). Views finas sobre services_artigos.

[US-46][US-20][research R1]
"""

from django.http import Http404

from sigtcc.apps.cadastro.permissoes import perfil_requerido


@perfil_requerido("docente")
def publicacao_orientando(request, tcc_id):
    """Rota 22. Provisória até a T049 (US8). [US-46][FR-035]"""
    raise Http404
