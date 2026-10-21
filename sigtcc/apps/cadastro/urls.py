"""Rotas do app cadastro (specs/003-acesso-login/contracts/rotas.md).

[US-10][US-11][US-12][US-37][US-38][FR-025]
"""

from django.urls import path

from sigtcc.apps.cadastro import views

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
]
