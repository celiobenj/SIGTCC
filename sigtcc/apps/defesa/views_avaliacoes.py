"""Views da avaliação da banca e do resultado da defesa (spec 008; contracts/rotas.md). Views
finas: as regras ficam em services_avaliacoes e permissoes_defesa; o sigilo, em
services_avaliacoes.visao_da_avaliacao.

[US-25][US-26][US-27][RBN-DEF-04.2][RBN-DEF-05.1 a RBN-DEF-05.4][RBN-DEF-06.3][RBN-DEF-06.4]
"""

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from sigtcc.apps.cadastro import services
from sigtcc.apps.cadastro.permissoes import perfil_requerido
from sigtcc.apps.defesa import mensagens, permissoes_defesa, services_avaliacoes, views_defesa
from sigtcc.apps.defesa.forms_avaliacoes import AssinaturaForm, CriteriosFormSet
from sigtcc.apps.defesa.models import BancaDefesa


@perfil_requerido("docente", "membro_externo")
def criterios(request):
    """Janela "Critérios de avaliação" (FR-001, FR-002): os 9 critérios por componente, com
    peso, somas 7,0 e 3,0, total 10,0 e as descrições dos conceitos; somente leitura, sem ação
    de criar, editar ou remover para nenhum perfil. Outros perfis: 403.
    [US-25][RBN-DEF-04.1][RBN-DEF-04.2]
    """
    partes, total = services_avaliacoes.criterios_por_componente()
    return render(request, "defesa/criterios.html", {"partes": partes, "total": total})


@perfil_requerido("docente", "membro_externo")
def minhas_bancas(request):
    """Tela "Minhas bancas" (FR-003 a FR-006): as sessões de que o usuário é membro, sem as
    Canceladas, com papel, data, horário, aluno, título e status, as pendências em destaque e
    os atalhos Documento, Critérios de avaliação, Avaliar e Declaração; a linha abre a janela
    Sessão de defesa. Sem nenhuma, MA-12. [US-25][RBN-DEF-05.4][RBN-DEF-08.3]
    """
    contexto = {
        "bancas": services_avaliacoes.minhas_bancas(request.user),
        "sem_bancas": mensagens.MA12_SEM_BANCAS,
    }
    return render(request, "defesa/minhas_bancas.html", contexto)


def _mostrar_erro(request, erro, formset=None, form_assinatura=None):
    """Recusa do serviço na tela: os critérios pendentes destacados, o erro da assinatura no
    bloco de assinatura e a mensagem no topo. [US-25][US-26][RBN-DEF-05.2]
    """
    if erro.pendentes and formset is not None:
        formset.marcar_pendentes(erro.pendentes, erro.mensagem)
    if erro.campo == "assinatura" and form_assinatura is not None:
        form_assinatura.add_error(None, erro.mensagem)
    messages.error(request, erro.mensagem)


@perfil_requerido()
def avaliacao(request, def_id):
    """Formulário "Avaliação" (US-25, US-26): só os membros efetivos, com a sessão não Cancelada
    (senão "Acesso restrito aos membros avaliadores da banca", também pelo endereço direto).
    GET mostra os 9 critérios conforme o status (Parte Escrita antes da sessão, MA-03; as duas
    partes e a assinatura com a sessão Em Andamento; só leitura quando Enviada ou Realizada);
    POST com acao=salvar (rascunho, MA-09) ou acao=enviar (envio assinado, MA-10). Recusas do
    serviço voltam ao formulário sem gravar. Roda o início automático antes (sessao_ou_404).
    [US-25][US-26][RBN-DEF-05.1][RBN-DEF-05.2][RBN-DEF-05.3][FR-007 a FR-022][FR-036]
    """
    registro = views_defesa.sessao_ou_404(def_id)
    if not permissoes_defesa.pode_avaliar(request.user, registro):
        raise PermissionDenied(mensagens.ACESSO_RESTRITO)
    dados = services_avaliacoes.formulario_da_avaliacao(request.user, registro)
    post = request.POST if request.method == "POST" else None
    formset = CriteriosFormSet(
        post, initial=dados["iniciais"], criterios=dados["criterios"], liberados=dados["liberados"]
    )
    form_assinatura = AssinaturaForm(post, request.FILES if post is not None else None)
    if post is not None:
        acao = request.POST.get("acao")
        enviar = acao == "enviar"
        assinatura_ok = form_assinatura.is_valid() if enviar else True
        if formset.is_valid() and assinatura_ok:
            try:
                if enviar:
                    services_avaliacoes.enviar_avaliacao(
                        request.user, registro.pk, formset.linhas(), form_assinatura.assinatura()
                    )
                    messages.success(request, mensagens.MA10_AVALIACAO_ENVIADA)
                else:
                    services_avaliacoes.salvar_rascunho(request.user, registro.pk, formset.linhas())
                    messages.success(request, mensagens.MA09_RASCUNHO_SALVO)
            except services_avaliacoes.AcessoRestrito:
                raise PermissionDenied(mensagens.ACESSO_RESTRITO)
            except services_avaliacoes.ErroAvaliacao as erro:
                _mostrar_erro(request, erro, formset, form_assinatura)
            else:
                return redirect("defesa:avaliacao", def_id=registro.pk)
    contexto = {
        "sessao": registro,
        "dados": dados,
        "formset": formset,
        "linhas": list(zip(dados["criterios"], formset.forms)),
        "form_assinatura": form_assinatura,
        "aviso_antes_da_sessao": mensagens.MA03_SO_PARTE_ESCRITA,
        "erro_tamanho": mensagens.ASSINATURA_TAMANHO,
        "erro_formato": mensagens.ASSINATURA_FORMATO,
    }
    return render(request, "defesa/avaliacao.html", contexto)


@perfil_requerido()
@require_POST
def reabrir(request, def_id):
    """ "Reabrir minha avaliação" (US-25 C; US-27 E): a avaliação Enviada volta a "Rascunho
    salvo", sem assinatura, com as notas; só com a sessão Em Andamento e antes da liberação
    (senão MA-04). Volta à janela Sessão de defesa. [US-25][US-27][RBN-DEF-06.1][FR-021][FR-022]
    """
    registro = views_defesa.sessao_ou_404(def_id)
    if not permissoes_defesa.pode_avaliar(request.user, registro):
        raise PermissionDenied(mensagens.ACESSO_RESTRITO)
    try:
        services_avaliacoes.reabrir_avaliacao(request.user, registro.pk)
    except services_avaliacoes.AcessoRestrito:
        raise PermissionDenied(mensagens.ACESSO_RESTRITO)
    except services_avaliacoes.ErroAvaliacao as erro:
        messages.error(request, erro.mensagem)
    return redirect("defesa:sessao", def_id=registro.pk)


@perfil_requerido()
def assinatura(request, def_id):
    """Cópia da imagem de assinatura enviada na avaliação (ban_assinatura_path), só para o
    próprio membro, sem URL pública (research A5); qualquer outro ou arquivo ausente: 404.
    [US-26][RBN-DEF-05.2][FR-018]
    """
    linha = BancaDefesa.objects.filter(ban_def_id=def_id, ban_usu_id=request.user.pk).first()
    caminho = linha.ban_assinatura_path if linha is not None else None
    if not caminho or not default_storage.exists(caminho):
        raise Http404
    arquivo = default_storage.open(caminho, "rb")
    tipo = services.tipo_por_bytes(arquivo.read(8))
    arquivo.seek(0)
    if tipo is None:
        arquivo.close()
        raise Http404
    return FileResponse(arquivo, content_type=services.mime_da_assinatura(tipo))
