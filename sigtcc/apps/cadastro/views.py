"""Views do app cadastro: só orquestram (constituição, princípio IV).

As regras ficam em services.py e permissoes.py; os textos, em mensagens.py.

[US-10][US-11][US-12][US-37][US-38][FR-025] research A20
"""

from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import Case, IntegerField, Value, When
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from sigtcc.apps.cadastro import mensagens, services
from sigtcc.apps.cadastro.choices import StatusTurma
from sigtcc.apps.cadastro.forms import (
    AlterarSenhaForm,
    AtivacaoForm,
    EsqueciSenhaForm,
    FormularioLogin,
    NovaSenhaForm,
    PerfilAlunoForm,
    PerfilDocenteForm,
    PerfilMembroExternoForm,
    PrimeiroAcessoAlunoForm,
    PrimeiroAcessoEmailForm,
)
from sigtcc.apps.cadastro.models import Alunos, Notificacoes, Turmas
from sigtcc.apps.cadastro.permissoes import (
    papeis,
    perfil_requerido,
    pode_resetar_primeiro_acesso,
    tipo_conta,
)
from sigtcc.apps.cadastro.services import (
    SESSAO_TOKEN_ATIVACAO,
    SESSAO_TOKEN_REDEFINICAO,
    EstadoLink,
    EstadoLogin,
    EstadoTroca,
)

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


# Mensagens de 403 próprias de uma US, levadas na exceção (PermissionDenied(texto)).
MENSAGENS_403 = {mensagens.SEM_PERMISSAO_PAGINA}


def acesso_negado(request, exception=None):
    """Página padrão do handler403, com a M-02 e nenhum dado da página pedida. Quando a US define
    um texto próprio (MENSAGENS_403, ex.: US-07 E8), mostra esse texto.

    [FR-025][SC-004][M-02][US-07]
    """
    texto = str(exception) if exception is not None else ""
    mensagem = texto if texto in MENSAGENS_403 else mensagens.M02_ACESSO_NEGADO
    return render(request, "acesso_negado.html", {"mensagem": mensagem}, status=403)


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
    """Valida o formulário (primeiro erro, Q12) e pede o link ao serviço (FR-002, FR-003).

    [US-10][RBN-CAD-06.1][RBN-CAD-06.2][FR-002][FR-003]
    """
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


# ---------------------------------------------------------------------------------------------
# Alterar e recuperar a senha; reset do primeiro acesso (US-12)
# ---------------------------------------------------------------------------------------------


@perfil_requerido()
def alterar_senha(request):
    """ "Alterar senha" em "Meu perfil": a sessão atual continua; as outras caem (Q19).

    [US-12][RBN-CAD-06.5][FR-012][Q19]
    """
    formulario = AlterarSenhaForm(request.user, request.POST or None)
    if request.method == "POST" and formulario.is_valid():
        dados = formulario.cleaned_data
        conta = services.alterar_senha(request.user, dados["senha_atual"], dados["nova_senha"])
        if conta is None:
            formulario.add_error("senha_atual", mensagens.SENHA_ATUAL_INCORRETA)
        else:
            update_session_auth_hash(request, conta)
            messages.success(request, mensagens.SENHA_ALTERADA)
            return redirect("cadastro:alterar_senha")
    return render(request, "cadastro/alterar_senha.html", {"form": formulario})


def esqueci_senha(request):
    """ "Esqueci minha senha": com e-mail válido, sempre a mensagem genérica (FR-013; Q13).

    [US-12][RBN-CAD-06.7][FR-013][Q13]
    """
    formulario = EsqueciSenhaForm(request.POST or None)
    if request.method == "POST" and formulario.is_valid():
        services.enviar_link_redefinicao(formulario.cleaned_data["email"])
        messages.info(request, mensagens.ESQUECI_GENERICA)
        return redirect("cadastro:entrar")
    return render(request, "cadastro/esqueci_senha.html", {"form": formulario})


def redefinir_senha(request, token):
    """Guarda o token na sessão e redireciona para a URL fixa, sem o token (research A3).

    [US-12][RBN-CAD-06.7][FR-014]
    """
    request.session[SESSAO_TOKEN_REDEFINICAO] = token
    return redirect("cadastro:nova_senha")


def _tela_do_link_de_redefinicao(request, resultado):
    """Mensagem de cada estado do link de redefinição que não é VALIDO (data-model; Q26).

    [US-12][RBN-CAD-06.7][FR-014][Q26]
    """
    request.session.pop(SESSAO_TOKEN_REDEFINICAO, None)
    erro = {
        EstadoLink.INATIVA: mensagens.M15_CONTA_INATIVA,
        EstadoLink.EXPIRADA: mensagens.M16_ACESSO_EXPIRADO,
    }.get(resultado.estado, mensagens.LINK_INVALIDO_OU_VENCIDO)
    return render(request, "cadastro/redefinir_senha.html", {"erro": erro})


def nova_senha(request):
    """Nova senha pelo link: só no estado VALIDO, revalidado no POST (FR-014; A17; Q26).

    [US-12][RBN-CAD-06.7][FR-014][Q19][Q26]
    """
    token = request.session.get(SESSAO_TOKEN_REDEFINICAO)
    if not token:
        return _tela_do_link_de_redefinicao(request, services.ResultadoLink(EstadoLink.ADULTERADO))
    formulario = NovaSenhaForm(request.POST or None)
    if request.method == "POST" and formulario.is_valid():
        resultado = services.redefinir_senha(token, formulario.cleaned_data["senha"])
        if resultado.estado != EstadoLink.VALIDO:
            return _tela_do_link_de_redefinicao(request, resultado)
        request.session.pop(SESSAO_TOKEN_REDEFINICAO, None)
        messages.success(request, mensagens.SENHA_ALTERADA)
        return redirect("cadastro:entrar")
    resultado = services.validar_link_redefinicao(token)
    if resultado.estado != EstadoLink.VALIDO:
        return _tela_do_link_de_redefinicao(request, resultado)
    return render(request, "cadastro/redefinir_senha.html", {"form": formulario})


@perfil_requerido("professor_disciplina")
def aluno(request, alu_id):
    """Endereço antigo da tela mínima do aluno (spec 003): a tela foi retirada pela spec 006
    (Q12; IC-08) e o endereço leva ao painel do aluno na turma mais recente em que quem abre é o
    Professor da Disciplina (não arquivada primeiro, depois ano, semestre e tur_id decrescentes;
    research R5, N12); sem essa turma, acesso negado (M-02). O reset fica no painel.
    [US-12][US-41][RBN-CAD-06.8][RBN-CAD-08.9][FR-015][spec 006 FR-044][Q12][IC-08]
    """
    registro = get_object_or_404(Alunos.objects.select_related("alu"), pk=alu_id)
    turma = (
        Turmas.objects.filter(tur_doc_id=request.user.pk, alunosturmas__mat_alu=registro)
        .annotate(
            arquivada=Case(
                When(tur_status=StatusTurma.ARQUIVADA, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        )
        .order_by("arquivada", "-tur_ano", "-tur_semestre", "-tur_id")
        .first()
    )
    if turma is None:
        raise PermissionDenied
    return redirect("cadastro:painel_aluno", tur_id=turma.pk, alu_id=registro.pk)


@perfil_requerido("professor_disciplina")
def resetar_primeiro_acesso(request, alu_id):
    """Confirmação (GET, M-12) e execução (POST, M-13) do reset do primeiro acesso.

    [US-12][RBN-CAD-06.8][FR-015][Q27][Q29]
    """
    registro = get_object_or_404(Alunos.objects.select_related("alu"), pk=alu_id)
    if request.method == "POST":
        services.resetar_primeiro_acesso(request.user, registro)
        messages.success(request, mensagens.M13_RESET_CONCLUIDO)
        return redirect("cadastro:aluno", alu_id=registro.pk)
    if not pode_resetar_primeiro_acesso(request.user, registro):
        raise PermissionDenied
    pergunta = mensagens.M12_CONFIRMAR_RESET.format(nome=registro.alu.usu_nome)
    return render(
        request, "cadastro/confirmar_reset.html", {"aluno": registro, "pergunta": pergunta}
    )


# ---------------------------------------------------------------------------------------------
# Perfil e notificações (US-38)
# ---------------------------------------------------------------------------------------------

_FORMULARIO_DO_PERFIL = {
    "aluno": PerfilAlunoForm,
    "docente": PerfilDocenteForm,
    "membro_externo": PerfilMembroExternoForm,
}


def _dados_do_perfil(usuario, tipo):
    """Dados só de leitura de "Meu perfil", por tipo de conta (FR-019). [US-38][RBN-CAD-13.1]"""
    dados = [("Nome", usuario.usu_nome)]
    if tipo == "aluno":
        dados += [
            ("Matrícula", usuario.alunos.alu_matricula),
            ("Curso", services.curso_do_aluno(usuario.alunos)),
        ]
    elif tipo == "docente":
        docente = usuario.docentes
        rotulos = [_ROTULO_PAPEL[p] for p in sorted(papeis(usuario))]
        dados += [
            ("E-mail", usuario.usu_email),
            ("Titulação", docente.doc_titulacao),
            ("Curso de lotação", docente.doc_cur.cur_nome),
            ("Papéis", ", ".join(rotulos) or "—"),
        ]
    elif tipo == "secretaria":
        dados += [("E-mail", usuario.usu_email), ("Curso", usuario.secretarios.sec_cur.cur_nome)]
    elif tipo == "membro_externo":
        validade = usuario.membrosexternos.mem_validade_ate
        dados += [("Validade do acesso", validade.strftime("%d/%m/%Y") if validade else "—")]
    return dados


def _valores_iniciais(usuario, tipo):
    """Valores atuais dos campos editáveis.

    [US-38][RBN-CAD-13.1]
    """
    if tipo == "membro_externo":
        membro = usuario.membrosexternos
        return {
            "email": usuario.usu_email,
            "titulacao": membro.mem_titulacao,
            "instituicao": membro.mem_instituicao,
        }
    return {"email": usuario.usu_email}


@perfil_requerido()
def perfil(request):
    """ "Meu perfil": mostra os dados e libera só os campos do papel (FR-019 a FR-021).

    Secretaria: tudo só leitura e sem "Salvar". Com troca de e-mail, só a M-06 (Q11).
    [US-38][RBN-CAD-13.1][FR-019][FR-020][FR-021][Q11]
    """
    usuario = request.user
    tipo = tipo_conta(usuario)
    classe = _FORMULARIO_DO_PERFIL.get(tipo)
    contexto = {"dados": _dados_do_perfil(usuario, tipo)}
    if classe is None:
        if request.method == "POST":
            return redirect("cadastro:perfil")
        return render(request, "cadastro/perfil.html", contexto)
    if request.method == "POST":
        formulario = classe(usuario, request.POST, request.FILES)
        if formulario.is_valid():
            dados = formulario.cleaned_data
            resultado = services.atualizar_perfil(
                usuario, dados, dados.get("assinatura"), formulario.tipo_assinatura
            )
            if resultado.sucesso:
                messages.success(request, resultado.mensagem)
                return redirect("cadastro:perfil")
            if resultado.mensagem == mensagens.M05_EMAIL_EM_USO:
                formulario.add_error("email", resultado.mensagem)
            else:
                contexto["erro"] = resultado.mensagem
    else:
        formulario = classe(usuario, initial=_valores_iniciais(usuario, tipo))
    contexto["form"] = formulario
    contexto["tem_assinatura"] = bool(services.caminho_da_assinatura(usuario))
    return render(request, "cadastro/perfil.html", contexto)


@perfil_requerido()
def assinatura(request):
    """Imagem de assinatura do próprio usuário, sem URL pública (research A11).

    [US-38][RBN-CAD-13.1][FR-020]
    """
    caminho = services.caminho_da_assinatura(request.user)
    if not caminho or not default_storage.exists(caminho):
        raise Http404
    arquivo = default_storage.open(caminho, "rb")
    tipo = services.tipo_por_bytes(arquivo.read(8))
    arquivo.seek(0)
    if tipo is None:
        arquivo.close()
        raise Http404
    return FileResponse(arquivo, content_type=services.mime_da_assinatura(tipo))


def confirmar_email(request, token):
    """Link de troca de e-mail: GET mostra o novo e-mail e o botão; POST confirma (Q28).

    [US-38][RBN-CAD-13.1][FR-021][Q11][Q24][Q28]
    """
    if request.method == "POST":
        mensagem = services.confirmar_troca_email(token)
        chave = "sucesso" if mensagem == mensagens.M07_EMAIL_ATUALIZADO else "erro"
        return render(request, "cadastro/confirmar_email.html", {chave: mensagem})
    resultado = services.validar_link_troca_email(token)
    if resultado.estado == EstadoTroca.VALIDO:
        contexto = {"novo_email": resultado.novo_email}
    elif resultado.estado == EstadoTroca.EM_USO:
        contexto = {"erro": mensagens.M05_EMAIL_EM_USO}
    else:
        contexto = {"erro": mensagens.M09_LINK_EMAIL_INVALIDO}
    return render(request, "cadastro/confirmar_email.html", contexto)


@perfil_requerido()
def notificacoes(request):
    """Central de notificações: da mais recente para a mais antiga, 20 por página (Q14).

    [US-38][RBN-CAD-13.2][FR-022][Q14]
    """
    lista = Notificacoes.objects.filter(not_usu_id=request.user.pk).order_by(
        "-not_data_hora", "-not_id"
    )
    pagina = Paginator(lista, 20).get_page(request.GET.get("pagina"))
    return render(request, "cadastro/notificacoes.html", {"pagina": pagina})


@perfil_requerido()
def abrir_notificacao(request, not_id):
    """Marca como lida e abre a tela relacionada; item removido: "Este item não está mais
    disponível" (Q10). Mudança de estado por GET aceita (research A12).
    [US-38][RBN-CAD-13.2][FR-023][Q10]
    """
    aberta = services.abrir_notificacao(request.user, not_id)
    if aberta is None:
        raise Http404
    notificacao, destino = aberta
    if destino:
        return redirect(destino)
    if notificacao.not_link_tela:
        return services.item_indisponivel(request)
    return redirect("cadastro:notificacoes")


@require_POST
@perfil_requerido()
def marcar_lidas(request):
    """ "Marcar como lidas": zera o contador. [US-38][RBN-CAD-13.2][FR-022]"""
    services.marcar_todas_lidas(request.user)
    return redirect("cadastro:notificacoes")
