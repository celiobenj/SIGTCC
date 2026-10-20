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
    path("painel/", views.painel, name="painel"),
]
