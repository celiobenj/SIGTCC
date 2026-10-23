"""Rotas do app cadastro (specs/003-acesso-login/contracts/rotas.md, specs/004 e specs/002).

[US-10][US-11][US-12][US-37][US-38][FR-025][US-03][US-04][US-05][US-50]
"""

from django.urls import path

from sigtcc.apps.cadastro import views, views_contas, views_turmas

app_name = "cadastro"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("entrar/", views.entrar, name="entrar"),
    path("sair/", views.sair, name="sair"),
    path("primeiro-acesso/", views.primeiro_acesso, name="primeiro_acesso"),
    path("primeiro-acesso/aluno/", views.primeiro_acesso_aluno, name="primeiro_acesso_aluno"),
    path("primeiro-acesso/email/", views.primeiro_acesso_email, name="primeiro_acesso_email"),
    path("primeiro-acesso/ativar/<str:token>/", views.ativar, name="ativar"),
    path("primeiro-acesso/definir-senha/", views.definir_senha, name="definir_senha"),
    path("primeiro-acesso/reenviar/", views.reenviar_link, name="reenviar_link"),
    path("esqueci-minha-senha/", views.esqueci_senha, name="esqueci_senha"),
    path("redefinir-senha/nova/", views.nova_senha, name="nova_senha"),
    path("redefinir-senha/<str:token>/", views.redefinir_senha, name="redefinir_senha"),
    path("painel/", views.painel, name="painel"),
    path("perfil/", views.perfil, name="perfil"),
    path("perfil/assinatura/", views.assinatura, name="assinatura"),
    path("perfil/senha/", views.alterar_senha, name="alterar_senha"),
    path("perfil/email/confirmar/<str:token>/", views.confirmar_email, name="confirmar_email"),
    path("notificacoes/", views.notificacoes, name="notificacoes"),
    path("notificacoes/marcar-lidas/", views.marcar_lidas, name="marcar_lidas"),
    path("notificacoes/<int:not_id>/", views.abrir_notificacao, name="abrir_notificacao"),
    path("alunos/<int:alu_id>/", views.aluno, name="aluno"),
    path(
        "alunos/<int:alu_id>/resetar-primeiro-acesso/",
        views.resetar_primeiro_acesso,
        name="resetar_primeiro_acesso",
    ),
    # Spec 004: turmas (contracts/rotas.md). [US-07][US-08][US-09]
    path("turmas/", views_turmas.turmas, name="turmas"),
    path("turmas/arquivadas/", views_turmas.turmas_arquivadas, name="turmas_arquivadas"),
    path("turmas/nova/", views_turmas.turma_nova, name="turma_nova"),
    path("turmas/<int:tur_id>/", views_turmas.turma, name="turma"),
    path("turmas/<int:tur_id>/editar/", views_turmas.turma_editar, name="turma_editar"),
    path("turmas/<int:tur_id>/excluir/", views_turmas.turma_excluir, name="turma_excluir"),
    path("turmas/<int:tur_id>/arquivar/", views_turmas.turma_arquivar, name="turma_arquivar"),
    path("turmas/<int:tur_id>/matricular/", views_turmas.matricular, name="matricular"),
    path("turmas/<int:tur_id>/importar/", views_turmas.importar, name="importar"),
    path(
        "turmas/<int:tur_id>/importar/confirmar/",
        views_turmas.importar_confirmar,
        name="importar_confirmar",
    ),
    path(
        "turmas/<int:tur_id>/importar/resumo/",
        views_turmas.importar_resumo,
        name="importar_resumo",
    ),
    path(
        "turmas/<int:tur_id>/importar/cancelar/",
        views_turmas.importar_cancelar,
        name="importar_cancelar",
    ),
    path(
        "turmas/modelo-importacao.csv",
        views_turmas.modelo_importacao,
        name="modelo_importacao",
    ),
    path(
        "turmas/<int:tur_id>/alunos/<int:alu_id>/editar/",
        views_turmas.aluno_editar,
        name="aluno_editar",
    ),
    path(
        "turmas/<int:tur_id>/alunos/<int:alu_id>/transferir/",
        views_turmas.aluno_transferir,
        name="aluno_transferir",
    ),
    path(
        "turmas/<int:tur_id>/alunos/<int:alu_id>/excluir/",
        views_turmas.aluno_excluir,
        name="aluno_excluir",
    ),
    path(
        "turmas/<int:tur_id>/alunos/<int:alu_id>/encerrar/",
        views_turmas.aluno_encerrar,
        name="aluno_encerrar",
    ),
    path(
        "turmas/<int:tur_id>/excluidos-transferidos/",
        views_turmas.excluidos_transferidos,
        name="excluidos_transferidos",
    ),
    # Spec 002: Gestão de Contas (specs/002-gestao-contas/contracts/rotas.md). [US-03]
    path("cadastros/docentes/", views_contas.docentes, name="contas_docentes"),
    path("cadastros/docentes/novo/", views_contas.docente_novo, name="contas_docente_novo"),
    path(
        "cadastros/docentes/<int:doc_id>/editar/",
        views_contas.docente_editar,
        name="contas_docente_editar",
    ),
    # [US-04]
    path(
        "cadastros/docentes/<int:doc_id>/inativar/",
        views_contas.docente_inativar,
        name="contas_docente_inativar",
    ),
    path(
        "cadastros/docentes/<int:doc_id>/reativar/",
        views_contas.docente_reativar,
        name="contas_docente_reativar",
    ),
    path("cadastros/secretarias/", views_contas.secretarias, name="contas_secretarias"),
    path(
        "cadastros/secretarias/nova/",
        views_contas.secretaria_nova,
        name="contas_secretaria_nova",
    ),
    path(
        "cadastros/secretarias/<int:sec_id>/editar/",
        views_contas.secretaria_editar,
        name="contas_secretaria_editar",
    ),
    path(
        "cadastros/secretarias/<int:sec_id>/inativar/",
        views_contas.secretaria_inativar,
        name="contas_secretaria_inativar",
    ),
    # [US-05]
    path("cadastros/membros-externos/", views_contas.membros, name="contas_membros"),
    path(
        "cadastros/membros-externos/novo/",
        views_contas.membro_novo,
        name="contas_membro_novo",
    ),
    path(
        "cadastros/membros-externos/<int:mem_id>/editar/",
        views_contas.membro_editar,
        name="contas_membro_editar",
    ),
    # [US-50]
    path(
        "cadastros/membros-externos/<int:mem_id>/prorrogar/",
        views_contas.membro_prorrogar,
        name="contas_membro_prorrogar",
    ),
]
