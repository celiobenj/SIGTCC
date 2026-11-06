"""Rotas do módulo Relatórios (spec 010; contracts/rotas.md), incluídas em sigtcc/urls.py.

[US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2]
[RBN-REL-02.3][RBN-REL-02.4][FR-001][FR-004][FR-018]
"""

from django.urls import path

from . import views

app_name = "relatorios"

urlpatterns = [
    path("relatorios/", views.lista, name="lista"),
    path("relatorios/<slug:id>/", views.relatorio, name="relatorio"),
    path("relatorios/<slug:id>/exportar/<slug:formato>/", views.exportar, name="exportar"),
]
