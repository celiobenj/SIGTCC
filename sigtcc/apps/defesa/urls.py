"""Rotas do módulo de Defesa (spec 007; contracts/rotas.md), incluídas em sigtcc/urls.py (IC-01),
e as da avaliação e do resultado (spec 008, IC-09; contracts/rotas.md da spec 008).

Spec 009 (IC-08): downloads da Ata Final e da Folha de Aprovação, as telas Ouvintes,
Ocorrências e Ouvintes das defesas e a agenda de defesas em PDF (contracts/rotas.md da spec 009).

[US-21][US-22][US-23][US-24][US-40][US-25][US-26][US-27][US-28][US-30][RBN-DEF-07.3][RBN-DEF-08.2]
[RBN-DEF-08.4][RBN-DEF-08.1][RBN-DEF-08.5]
"""

from django.urls import path

from sigtcc.apps.defesa import views_avaliacoes, views_defesa, views_documentos, views_ouvintes

app_name = "defesa"

urlpatterns = [
    path("defesas/", views_defesa.defesas, name="defesas"),
    path("defesas/agendar/", views_defesa.agendar, name="agendar"),
    path("turmas/<int:tur_id>/defesas/", views_defesa.turma_defesas, name="turma_defesas"),
    # Spec 009 (US6): agenda de defesas em PDF, antes de defesas/<int:def_id>/ para a leitura.
    # [US-30][RBN-DEF-08.1]
    path("defesas/agenda/", views_documentos.agenda, name="agenda"),
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
    path(
        "defesas/<int:def_id>/parecer/",
        views_avaliacoes.registrar_parecer,
        name="registrar_parecer",
    ),
    path(
        "defesas/<int:def_id>/liberar/",
        views_avaliacoes.liberar_resultado,
        name="liberar_resultado",
    ),
    # Spec 009 (IC-08): documentos da defesa em PDF, sob demanda. [US-28][RBN-DEF-07.3]
    path("defesas/<int:def_id>/ata-final/", views_documentos.ata_final, name="ata_final"),
    path(
        "defesas/<int:def_id>/folha-aprovacao/",
        views_documentos.folha_aprovacao,
        name="folha_aprovacao",
    ),
    # Spec 009 (IC-08): janela Ouvintes da sessão. [US-30][RBN-DEF-08.2]
    path("defesas/<int:def_id>/ouvintes/", views_ouvintes.ouvintes, name="ouvintes"),
    # Spec 009 (US3): janela Ocorrências da sessão. [US-30][RBN-DEF-08.5]
    path("defesas/<int:def_id>/ocorrencias/", views_ouvintes.ocorrencias, name="ocorrencias"),
    # Spec 009 (US4): Ouvintes das defesas, da Secretaria. [US-30][RBN-DEF-08.4]
    path(
        "ouvintes-das-defesas/",
        views_ouvintes.ouvintes_das_defesas,
        name="ouvintes_das_defesas",
    ),
]
