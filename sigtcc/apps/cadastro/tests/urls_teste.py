"""Rotas de teste da base comum: páginas de exemplo restritas por perfil (spec 003, história 6).

Usadas só por test_base_comum.py, com override_settings(ROOT_URLCONF=...).

[FR-025][SC-004][infraestrutura de teste da feature 003]
"""

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.urls import include, path
from django.views import View

from sigtcc.apps.cadastro.permissoes import PerfilRequeridoMixin, perfil_requerido

DADO_DA_PAGINA = "dado restrito da página de exemplo"


@perfil_requerido("professor_disciplina")
def so_professor(request):
    """Página de exemplo restrita ao Professor da Disciplina."""
    return HttpResponse(DADO_DA_PAGINA)


@perfil_requerido("coordenador")
def so_coordenador(request):
    """Página de exemplo restrita ao Coordenador de Curso."""
    return HttpResponse(DADO_DA_PAGINA)


@perfil_requerido()
def servico_nega(request):
    """Página cujo serviço levanta PermissionDenied (contrato §2)."""
    raise PermissionDenied


class SoSecretaria(PerfilRequeridoMixin, View):
    """View de classe de exemplo restrita à Secretaria."""

    perfis_permitidos = ("secretaria",)

    def get(self, request):
        return HttpResponse(DADO_DA_PAGINA)


urlpatterns = [
    path("", include("sigtcc.apps.cadastro.urls")),
    path("exemplo/professor/", so_professor),
    path("exemplo/coordenador/", so_coordenador),
    path("exemplo/servico/", servico_nega),
    path("exemplo/secretaria/", SoSecretaria.as_view()),
]

handler403 = "sigtcc.apps.cadastro.views.acesso_negado"
