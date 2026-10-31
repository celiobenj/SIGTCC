"""Rotas do módulo de Defesa (spec 007; contracts/rotas.md), incluídas em sigtcc/urls.py (IC-01).

[US-21][US-22][US-23][US-24][US-40]
"""

from django.urls import path

from sigtcc.apps.defesa import views_defesa

app_name = "defesa"

urlpatterns = [
    path("defesas/", views_defesa.defesas, name="defesas"),
    path("defesas/agendar/", views_defesa.agendar, name="agendar"),
    path("turmas/<int:tur_id>/defesas/", views_defesa.turma_defesas, name="turma_defesas"),
]
