"""PDF sob demanda, gerado em memória e entregue pela view que conferiu a permissão (spec 008,
research A9; contrato §3 de specs/008-avaliacao-resultados/contracts/servicos-avaliacoes.md).

Nenhum PDF é gravado: a Ata Final, a Folha de Aprovação e as declarações (feat-09) são geradas a
cada download, a partir dos dados congelados na liberação. O xhtml2pdf é importado só dentro de
gerar_pdf, para não pesar na memória dos workers. Recursos do PDF (imagens e fontes) só de
caminhos relativos de static/ ou media/, resolvidos dentro das pastas do projeto: nenhum acesso à
rede e nenhum arquivo fora dessas pastas (revisão I-12).

[US-27][US-28][RBN-DEF-06.4][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-08.3]
"""

import logging
import os
from io import BytesIO
from pathlib import Path
from urllib.parse import unquote, urlsplit

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.exceptions import SuspiciousFileOperation
from django.http import HttpResponse
from django.template.loader import render_to_string

logger = logging.getLogger("sigtcc.defesa")


class ErroAoGerarPdf(Exception):
    """Falha na geração do PDF (registrada no log); a feat-09 mostra a mensagem da US-28 E3.
    [US-28][RBN-DEF-07.1]
    """


def _dentro(caminho, raizes):
    """O caminho, já resolvido com realpath, fica dentro de uma das raízes (sem escapar por
    "../" nem por link simbólico). [US-28][RBN-DEF-07.1][revisão I-12]
    """
    real = os.path.realpath(caminho)
    for raiz in raizes:
        raiz_real = os.path.realpath(raiz)
        if real == raiz_real or real.startswith(raiz_real + os.sep):
            return True
    return False


def _raizes_estaticas():
    """Pastas de onde o PDF pode ler arquivos estáticos: STATIC_ROOT e as dos finders
    (STATICFILES_DIRS). [US-28][RBN-DEF-07.1][revisão I-12]
    """
    raizes = [str(settings.STATIC_ROOT)] if settings.STATIC_ROOT else []
    raizes += [str(pasta) for pasta in settings.STATICFILES_DIRS]
    return raizes


def _relativo(uri, prefixo):
    """Parte do caminho depois de "static/" ou "media/" (com ou sem "/" inicial), ou None.
    [US-28][RBN-DEF-07.1][revisão I-12]
    """
    prefixo = prefixo.strip("/") + "/"
    caminho = uri.lstrip("/")
    if not caminho.startswith(prefixo):
        return None
    return unquote(caminho[len(prefixo) :])


def link_callback(uri, rel=None):
    """Resolve um recurso do PDF para um arquivo local permitido, ou devolve None.

    Aceita só caminho relativo de static/ (STATIC_ROOT ou finders) ou de media/ (MEDIA_ROOT);
    qualquer esquema (http:, https:, file:, data: e outros) ou caminho que, resolvido com
    realpath, saia dessas pastas devolve None, e o recurso não entra (a política de recursos de
    gerar_pdf também recusa rede e arquivo fora dessas pastas). Nunca acessa a rede.
    [US-28][RBN-DEF-07.1][RBN-DEF-07.2][revisão I-12]
    """
    if not uri or not isinstance(uri, str):
        return None
    partes = urlsplit(uri)
    if partes.scheme or partes.netloc or "\\" in uri:
        return None
    estatico = _relativo(partes.path, settings.STATIC_URL)
    if estatico is not None:
        candidatos = [os.path.join(raiz, estatico) for raiz in _raizes_estaticas()]
        try:
            achado = finders.find(estatico)
        except SuspiciousFileOperation:
            # "../" que sai da pasta dos finders: recusado.
            return None
        if achado:
            candidatos.append(achado)
        for candidato in candidatos:
            if _dentro(candidato, _raizes_estaticas()) and os.path.isfile(candidato):
                return os.path.realpath(candidato)
        return None
    midia = _relativo(partes.path, settings.MEDIA_URL)
    if midia is not None:
        candidato = os.path.join(str(settings.MEDIA_ROOT), midia)
        if _dentro(candidato, [str(settings.MEDIA_ROOT)]) and os.path.isfile(candidato):
            return os.path.realpath(candidato)
    return None


def _politica():
    """Política de recursos do xhtml2pdf: sem rede e leitura local só nas pastas de static/ e
    media/ (a mesma regra do link_callback, para o que não passa por ele). [US-28][revisão I-12]
    """
    from xhtml2pdf.config.resources import ResourceAccessPolicy

    raizes = tuple(Path(raiz) for raiz in (*_raizes_estaticas(), str(settings.MEDIA_ROOT)))
    return ResourceAccessPolicy.server(base_dir=None, allow_remote=False, extra_roots=raizes)


def gerar_pdf(template, contexto):
    """Renderiza o template (que não estende base.html e usa as fontes locais de
    static/fonts/) e devolve os bytes do PDF, gerado em memória, sem gravar arquivo.
    Falha na geração: ErroAoGerarPdf, com o motivo no log.
    [US-27][US-28][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-08.3]
    """
    from xhtml2pdf import pisa

    html = render_to_string(template, contexto)
    saida = BytesIO()
    try:
        resultado = pisa.CreatePDF(
            html,
            dest=saida,
            encoding="utf-8",
            link_callback=link_callback,
            resource_policy=_politica(),
        )
    except Exception as erro:
        logger.exception("Falha ao gerar o PDF %s", template)
        raise ErroAoGerarPdf(str(erro)) from erro
    if resultado.err:
        logger.error("Falha ao gerar o PDF %s: %s erro(s)", template, resultado.err)
        raise ErroAoGerarPdf(f"{resultado.err} erro(s) ao gerar {template}")
    return saida.getvalue()


def resposta_pdf(nome_arquivo, template, contexto):
    """Resposta de download do PDF (attachment, sem cache). Quem chama confere a permissão
    antes; nenhum arquivo é persistido. [US-28][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-08.3]
    """
    resposta = HttpResponse(gerar_pdf(template, contexto), content_type="application/pdf")
    resposta["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'
    resposta["Cache-Control"] = "no-store"
    return resposta
