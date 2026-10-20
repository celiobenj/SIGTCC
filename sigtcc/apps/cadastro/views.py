"""Views do app cadastro: só orquestram (constituição, princípio IV).

As regras ficam em services.py e permissoes.py; os textos, em mensagens.py.

[US-10][US-11][US-12][US-37][US-38][FR-025] research A20
"""

from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from sigtcc.apps.cadastro import mensagens, services
from sigtcc.apps.cadastro.forms import FormularioLogin
from sigtcc.apps.cadastro.permissoes import papeis, perfil_requerido, tipo_conta
from sigtcc.apps.cadastro.services import EstadoLogin

# Texto de cada tipo de conta no painel (spec FR-010).
_ROTULO_TIPO = {
    "aluno": "do Aluno",
    "docente": "do Docente",
    "secretaria": "da Secretaria",
    "membro_externo": "do Membro Externo",
}

# Texto de cada papel do Docente, mostrado no painel (spec Q7).
_ROTULO_PAPEL = {
    "coordenador": "Coordenador de Curso",
    "professor_disciplina": "Professor da Disciplina",
    "orientador": "Orientador",
    "coorientador": "Coorientador",
}


def acesso_negado(request, exception=None):
    """Página padrão do handler403, com a M-02 e nenhum dado da página pedida.

    [FR-025][SC-004][M-02]
    """
    return render(
        request, "acesso_negado.html", {"mensagem": mensagens.M02_ACESSO_NEGADO}, status=403
    )


def inicio(request):
    """Raiz do sistema: logado vai ao painel; visitante vai ao login. [US-11][FR-010]"""
    return redirect("cadastro:painel" if request.user.is_authenticated else "cadastro:entrar")


@perfil_requerido()
def painel(request):
    """Painel inicial mínimo do tipo de conta; papéis do Docente como itens extras (Q7).

    [US-11][RBN-CAD-06.4][FR-010][Q7]
    """
    tipo = tipo_conta(request.user)
    contexto = {
        "tipo": tipo or "",
        "rotulo_tipo": _ROTULO_TIPO.get(tipo, ""),
        "papeis": [_ROTULO_PAPEL[p] for p in sorted(papeis(request.user))],
    }
    return render(request, "cadastro/painel.html", contexto)


# Mensagem exata de cada resultado do login (US-11; M-01 com os minutos restantes).
_MENSAGEM_LOGIN = {
    EstadoLogin.VAZIO: mensagens.INFORME_CREDENCIAL,
    EstadoLogin.NAO_ENCONTRADA: mensagens.CREDENCIAL_INVALIDA,
    EstadoLogin.AGUARDANDO: mensagens.CONTA_NAO_ATIVADA,
    EstadoLogin.SENHA_INCORRETA: mensagens.CREDENCIAL_INVALIDA,
    EstadoLogin.INATIVA: mensagens.CONTA_INATIVA,
    EstadoLogin.EXPIRADA: mensagens.ACESSO_EXPIRADO,
}


def _destino_seguro(request, destino):
    """Segue o next só se for do próprio site (achado B2); senão, o painel. [US-11][FR-010]"""
    if destino and url_has_allowed_host_and_scheme(
        destino, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return destino
    return reverse("cadastro:painel")


def entrar(request):
    """Tela de login: traduz o resultado de services.autenticar na mensagem exata da US-11.

    [US-11][RBN-CAD-06.4][RBN-CAD-06.6][FR-007]-[FR-010][B2]
    """
    if request.user.is_authenticated:
        return redirect("cadastro:painel")
    if request.method == "POST":
        formulario = FormularioLogin(request.POST)
        resultado = services.autenticar(request.POST.get("credencial"), request.POST.get("senha"))
        if resultado.estado == EstadoLogin.OK:
            login(request, resultado.usuario, backend="sigtcc.apps.cadastro.backends.SigtccBackend")
            return redirect(_destino_seguro(request, request.POST.get("next")))
        if resultado.estado == EstadoLogin.BLOQUEADA:
            erro = mensagens.M01_BLOQUEIO.format(minutos=resultado.minutos_restantes)
        else:
            erro = _MENSAGEM_LOGIN[resultado.estado]
        contexto = {
            "form": formulario,
            "erro": erro,
            "mostrar_primeiro_acesso": resultado.estado == EstadoLogin.AGUARDANDO,
        }
        return render(request, "cadastro/entrar.html", contexto)
    formulario = FormularioLogin(initial={"next": request.GET.get("next", "")})
    return render(request, "cadastro/entrar.html", {"form": formulario})


@require_POST
def sair(request):
    """Encerra a sessão e volta ao login (só POST). [US-11][FR-011]"""
    logout(request)
    return redirect("cadastro:entrar")
