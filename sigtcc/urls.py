"""Roteamento global do SIGTCC.

As rotas de cada app entram por include. Sem MEDIA_URL publicado: as imagens de assinatura não
têm endereço público e são servidas só ao dono (research A11).

[infraestrutura da feature 003][FR-020][FR-025]
"""

from django.urls import include, path

urlpatterns = [
    path("", include("sigtcc.apps.cadastro.urls")),
]

# Logado sem permissão: página padrão com a M-02 (research A7). [FR-025]
handler403 = "sigtcc.apps.cadastro.views.acesso_negado"
