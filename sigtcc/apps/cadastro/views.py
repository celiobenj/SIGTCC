"""Views do app cadastro: só orquestram (constituição, princípio IV).

As regras ficam em services.py e permissoes.py; os textos, em mensagens.py.

[US-10][US-11][US-12][US-37][US-38][FR-025] research A20
"""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from sigtcc.apps.cadastro import mensagens, services
from sigtcc.apps.cadastro.forms import (
    AtivacaoForm,
    FormularioLogin,
    PrimeiroAcessoAlunoForm,
    PrimeiroAcessoEmailForm,
)
from sigtcc.apps.cadastro.permissoes import papeis, perfil_requerido, tipo_conta
from sigtcc.apps.cadastro.services import SESSAO_TOKEN_ATIVACAO, EstadoLink, EstadoLogin

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


# ---------------------------------------------------------------------------------------------
# Primeiro acesso (US-10) e link de ativação (US-10, US-37)
# ---------------------------------------------------------------------------------------------


def primeiro_acesso(request):
    """Escolha entre "Aluno" e "Docente, Secretaria ou Membro Externo" (FR-001; Q8).

    [US-10][RBN-CAD-06.1][RBN-CAD-06.2][FR-001][Q8]
    """
    return render(request, "cadastro/primeiro_acesso.html")


def _pedir_primeiro_acesso(request, classe_formulario, titulo):
    """Valida o formulário (primeiro erro, Q12) e pede o link ao serviço (FR-002, FR-003)."""
    formulario = classe_formulario(request.POST or None)
    contexto = {"form": formulario, "titulo": titulo}
    if request.method == "POST":
        erro = ""
        if formulario.is_valid():
            resultado = services.pedir_primeiro_acesso(
                formulario.conta, formulario.cleaned_data["email"]
            )
            if resultado.enviado:
                messages.success(request, resultado.mensagem)
                return redirect("cadastro:entrar")
            contexto["erro"] = erro = resultado.mensagem
        else:
            erro = formulario.primeiro_erro()
        if erro == mensagens.CONTA_JA_ATIVA:
            # Complemento de "Esta conta já está ativa" (M-03, provisória).
            contexto["orientacao"] = mensagens.M03_ORIENTACAO_CONTA_ATIVA
    return render(request, "cadastro/primeiro_acesso_form.html", contexto)


def primeiro_acesso_aluno(request):
    """Formulário do Aluno: Matrícula e E-mail Institucional. [US-10][RBN-CAD-06.1][FR-001]"""
    return _pedir_primeiro_acesso(request, PrimeiroAcessoAlunoForm, "Primeiro acesso do Aluno")


def primeiro_acesso_email(request):
    """Formulário de Docente, Secretaria ou Membro Externo: E-mail. [US-10][RBN-CAD-06.2]"""
    return _pedir_primeiro_acesso(
        request, PrimeiroAcessoEmailForm, "Primeiro acesso de Docente, Secretaria ou Membro Externo"
    )


def ativar(request, token):
    """Guarda o token na sessão e redireciona para a URL fixa, sem o token (research A3).

    [US-10][RBN-CAD-06.1][FR-016]
    """
    request.session[SESSAO_TOKEN_ATIVACAO] = token
    return redirect("cadastro:definir_senha")


def _tela_do_link(request, resultado):
    """Tela de cada estado do link de ativação que não é VALIDO (FR-016; data-model).

    [US-10][US-37][RBN-CAD-06.9][FR-016][Q5][Q23][Q26]
    """
    estado = resultado.estado
    if estado in (EstadoLink.VENCIDO, EstadoLink.SEM_EMAIL):
        # O token fica na sessão para o "Reenviar link de ativação" (US-37).
        return render(request, "cadastro/link_vencido.html")
    request.session.pop(SESSAO_TOKEN_ATIVACAO, None)
    if estado == EstadoLink.ATIVA:
        messages.info(request, mensagens.CONTA_JA_ATIVA)
        return redirect("cadastro:entrar")
    erro = {
        EstadoLink.INATIVA: mensagens.M15_CONTA_INATIVA,
        EstadoLink.EXPIRADA: mensagens.M16_ACESSO_EXPIRADO,
    }.get(estado, mensagens.LINK_SUBSTITUIDO)
    return render(request, "cadastro/ativar.html", {"erro": erro})


def definir_senha(request):
    """Formulário de ativação: só no link VALIDO; revalida no POST com a conta travada (A17).

    [US-10][RBN-CAD-06.1][RBN-CAD-06.3][FR-004][FR-005][FR-016][I4]
    """
    token = request.session.get(SESSAO_TOKEN_ATIVACAO)
    if not token:
        return _tela_do_link(request, services.ResultadoLink(EstadoLink.ADULTERADO))
    formulario = AtivacaoForm(request.POST or None)
    if request.method == "POST" and formulario.is_valid():
        resultado = services.ativar_conta(token, formulario.cleaned_data["senha"])
        if resultado.estado != EstadoLink.VALIDO:
            return _tela_do_link(request, resultado)
        request.session.pop(SESSAO_TOKEN_ATIVACAO, None)
        messages.success(request, mensagens.CONTA_ATIVADA)
        return redirect("cadastro:entrar")
    resultado = services.validar_link_ativacao(token)
    if resultado.estado != EstadoLink.VALIDO:
        return _tela_do_link(request, resultado)
    return render(request, "cadastro/ativar.html", {"form": formulario})


@require_POST
def reenviar_link(request):
    """ "Reenviar link de ativação": só reenvia no estado VENCIDO (US-37; A3).

    Sucesso: "Enviamos um novo link para o seu e-mail". Conta resetada: M-08. Falha no envio:
    M-17, com o botão de novo. Outros estados: a tela do estado. O token sai da sessão quando o
    reenvio termina.
    [US-37][RBN-CAD-06.9][FR-017][FR-018][Q5][Q13]
    """
    token = request.session.get(SESSAO_TOKEN_ATIVACAO)
    if not token:
        return _tela_do_link(request, services.ResultadoLink(EstadoLink.ADULTERADO))
    resultado, pedido = services.reenviar_link_ativacao(token)
    if pedido is None:
        if resultado.estado == EstadoLink.VALIDO:
            return redirect("cadastro:definir_senha")
        return _tela_do_link(request, resultado)
    if pedido.mensagem == mensagens.M17_FALHA_ENVIO:
        return render(request, "cadastro/link_vencido.html", {"erro": pedido.mensagem})
    request.session.pop(SESSAO_TOKEN_ATIVACAO, None)
    contexto = {"concluido": True}
    contexto["sucesso" if pedido.enviado else "orientacao"] = pedido.mensagem
    return render(request, "cadastro/link_vencido.html", contexto)
