"""Telas do módulo Relatórios (spec 010; contracts/rotas.md): só orquestram e só leem. A ordem
das checagens é a do contrato: login, módulo, 404 do id, permissão, 404 do formato, filtros,
consulta e arquivo. Tela e exportação passam por montar_relatorio, para o recorte de permissão não
faltar em nenhum caminho (research R1).

[US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2]
[RBN-REL-02.3][RBN-REL-02.4][FR-001][FR-002][FR-004][FR-005][FR-018]
"""

import logging

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET

from sigtcc.apps.cadastro.permissoes import perfil_requerido

from . import exportacao, mensagens, registro, services_relatorios

logger = logging.getLogger("sigtcc.relatorios")


def _relatorio_permitido(usuario, id):
    """Relatório do id, conferido no servidor: 404 se não existe, MR-06 sem o perfil. [FR-004]"""
    registrado = registro.obter(id)
    if registrado is None:
        raise Http404
    if not registro.pode_abrir(usuario, registrado):
        raise PermissionDenied(mensagens.MR06_SEM_PERMISSAO)
    return registrado


def _endereco(id, consulta):
    """Endereço do relatório com os filtros aplicados. [FR-018][FR-076]"""
    endereco = reverse("relatorios:relatorio", args=[id])
    return f"{endereco}?{consulta}" if consulta else endereco


def _contexto_base(usuario):
    """Lista por perfil e textos da tela. [FR-002]"""
    return {
        "lista": registro.relatorios_do_usuario(usuario),
        "selecione": mensagens.MR05_SELECIONE,
        "sem_exportacao": mensagens.MR02_SEM_REGISTROS_EXPORTAR,
        "vazio_us": mensagens.NENHUM_REGISTRO_FILTROS,
        "vazio_sugestao": mensagens.MR01_SUGESTAO_VAZIO,
    }


@require_GET
@perfil_requerido()
def lista(request):
    """Tela Relatórios, com a lista do perfil. [US-31][RBN-REL-01.1][FR-002][FR-004]"""
    registro.exigir_modulo(request.user)
    return render(request, "relatorios/relatorios.html", _contexto_base(request.user))


@require_GET
@perfil_requerido()
def relatorio(request, id):
    """Um relatório, com os filtros do endereço. [US-31][RBN-REL-01.1][FR-004][FR-070]"""
    registro.exigir_modulo(request.user)
    registrado = _relatorio_permitido(request.user, id)
    form, pronto = services_relatorios.montar_relatorio(request.user, registrado, request.GET)
    consulta = form.querystring()
    contexto = _contexto_base(request.user)
    contexto.update(
        {
            "registrado": registrado,
            "form": form,
            "relatorio": pronto,
            "filtros": form.filtros() if pronto else None,
            "linhas": pronto.linhas_prontas() if pronto else [],
            "totais": pronto.totais_prontos() if pronto else [],
            "exportacoes": [
                {
                    "rotulo": formato.upper(),
                    "url": f"{reverse('relatorios:exportar', args=[id, formato])}?{consulta}",
                }
                for formato in exportacao.FORMATOS
            ],
        }
    )
    return render(request, "relatorios/relatorios.html", contexto)


@require_GET
@perfil_requerido()
def exportar(request, id, formato):
    """Arquivo do relatório, com as mesmas permissões e filtros da tela; sem registros, com filtro
    inválido ou em falha, volta ao relatório sem gerar nada. No log, só o id, o formato e a conta.
    [US-31][RBN-REL-01.1][FR-004][FR-018][FR-019][FR-020]
    """
    registro.exigir_modulo(request.user)
    registrado = _relatorio_permitido(request.user, id)
    if formato not in exportacao.FORMATOS:
        raise Http404
    form, pronto = services_relatorios.montar_relatorio(request.user, registrado, request.GET)
    destino = _endereco(id, form.querystring())
    if pronto is None or not pronto.tem_registros:
        return redirect(destino)
    try:
        return exportacao.exportar(pronto, form.filtros(), formato)
    except exportacao.ErroAoExportar as erro:
        logger.error(
            "Falha ao exportar: relatorio=%s formato=%s usuario=%s causa=%s",
            id,
            formato,
            request.user.pk,
            type(erro.__cause__).__name__,
        )
        messages.error(request, mensagens.MR07_FALHA_ARQUIVO)
        return redirect(destino)
