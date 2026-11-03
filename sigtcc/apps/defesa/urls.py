"""Rotas do módulo de Defesa (spec 007; contracts/rotas.md), incluídas em sigtcc/urls.py (IC-01),
e as da avaliação e do resultado (spec 008, IC-09; contracts/rotas.md da spec 008).

[US-21][US-22][US-23][US-24][US-40][US-25][US-26][US-27]
"""

from django.urls import path

from sigtcc.apps.defesa import views_avaliacoes, views_defesa

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
    path("defesas/<int:def_id>/historico/", views_defesa.historico, name="historico"),
    # Spec 008 (IC-09): Minhas bancas, critérios, avaliação e resultado.
    path("minhas-bancas/", views_avaliacoes.minhas_bancas, name="minhas_bancas"),
    path("defesas/criterios/", views_avaliacoes.criterios, name="criterios"),
    path("defesas/<int:def_id>/avaliacao/", views_avaliacoes.avaliacao, name="avaliacao"),
    path(
        "defesas/<int:def_id>/avaliacao/reabrir/",
        views_avaliacoes.reabrir,
        name="reabrir_avaliacao",
    ),
    path(
        "defesas/<int:def_id>/avaliacao/assinatura/",
        views_avaliacoes.assinatura,
        name="assinatura_avaliacao",
    ),
]
