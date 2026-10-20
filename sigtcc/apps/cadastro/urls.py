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
    path("painel/", views.painel, name="painel"),
]
