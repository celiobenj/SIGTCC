"""Processadores de contexto: menu lateral por perfil e contador do sino (research A8).

Para visitante anônimo, os dois devolvem vazio sem consultar o banco.

[FR-022][FR-024][FR-025][US-38][RBN-CAD-13.2]
"""

from importlib import import_module
from importlib.util import find_spec

from django.apps import apps
from django.urls import NoReverseMatch, reverse

from sigtcc.apps.cadastro.models import Notificacoes
from sigtcc.apps.cadastro.permissoes import tem_perfil


def _itens_de_todos_os_apps():
    """Junta os ITENS do menu.py de cada app instalado, sem duplicar e sem depender da ordem."""
    itens = []
    for config in apps.get_app_configs():
        nome_modulo = f"{config.name}.menu"
        if find_spec(nome_modulo) is None:
            continue
        itens.extend(getattr(import_module(nome_modulo), "ITENS", []))
    return itens


def menu(request):
    """Itens do menu lateral permitidos ao usuário, ordenados por seção e ordem. [FR-025]"""
    usuario = getattr(request, "user", None)
    if usuario is None or not usuario.is_authenticated:
        return {}
    itens = []
    for item in _itens_de_todos_os_apps():
        if not tem_perfil(usuario, *item["perfis"]):
            continue
        try:
            url = reverse(item["rota"])
        except NoReverseMatch:
            # Rota de uma feature ainda não publicada: o item não aparece.
            continue
        itens.append(
            {
                "rotulo": item["rotulo"],
                "icone": item["icone"],
                "url": url,
                "secao": item.get("secao") or "",
                "ordem": item.get("ordem", 0),
                "ativo": request.path == url,
            }
        )
    itens.sort(key=lambda i: (i["secao"] != "", i["secao"], i["ordem"], i["rotulo"]))
    return {"menu_itens": itens}


def notificacoes_nao_lidas(request):
    """Número de notificações não lidas do usuário, para o sino. [FR-022][RBN-CAD-13.2]"""
    usuario = getattr(request, "user", None)
    if usuario is None or not usuario.is_authenticated:
        return {}
    total = Notificacoes.objects.filter(not_usu_id=usuario.pk, not_lida=False).count()
    return {"notificacoes_nao_lidas": total}
