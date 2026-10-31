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
    path("defesas/<int:def_id>/", views_defesa.sessao, name="sessao"),
    path("defesas/<int:def_id>/banca/", views_defesa.alterar_banca, name="alterar_banca"),
    path("defesas/<int:def_id>/suplente/", views_defesa.acionar_suplente, name="acionar_suplente"),
    path("defesas/<int:def_id>/reagendar/", views_defesa.reagendar, name="reagendar"),
    path("defesas/<int:def_id>/cancelar/", views_defesa.cancelar, name="cancelar"),
]
