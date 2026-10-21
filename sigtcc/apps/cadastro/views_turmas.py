"""Views de turmas e alunos (spec 004): só orquestram; as regras ficam em services_turmas.py e
importacao.py (constituição, princípio IV; research B1).

[US-07][US-08][US-09][FR-001]-[FR-026]
"""

from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect, render

from sigtcc.apps.cadastro import mensagens, services_turmas
from sigtcc.apps.cadastro.forms_turmas import TurmaForm
from sigtcc.apps.cadastro.permissoes import (
    perfil_requerido,
    pode_alterar_turma,
    pode_transferir,
    tipo_conta,
)
from sigtcc.apps.cadastro.services_turmas import (
    ALTERAR,
    CONSULTAR,
    ErroTurma,
    TurmaArquivada,
)


def trata_turma_arquivada(view):
    """Ação em turma arquivada (inclusive pelo endereço direto): MT-25 e volta para a turma.

    [US-07][RBN-CAD-04.5][FR-008]
    """

    @wraps(view)
    def envolta(request, tur_id, *args, **kwargs):
        """Converte TurmaArquivada na MT-25. [FR-008]"""
        try:
            return view(request, tur_id, *args, **kwargs)
        except TurmaArquivada:
            messages.warning(request, mensagens.MT25_TURMA_ARQUIVADA)
            return redirect("cadastro:turma", tur_id=tur_id)

    return envolta


@perfil_requerido("docente", "secretaria")
def turmas(request):
    """Turmas ativas do Docente (Professor da Disciplina) ou do curso da Secretaria (Q9).

    [US-07][FR-010][Q9]
    """
    contexto = {
        "turmas": services_turmas.turmas_visiveis(request.user),
        "pode_criar": tipo_conta(request.user) == "docente",
        "arquivadas": False,
    }
    return render(request, "cadastro/turmas/lista.html", contexto)


@perfil_requerido("docente", "secretaria")
def turmas_arquivadas(request):
    """Área de turmas arquivadas, só para consulta (RBN-CAD-04.5). [US-07][FR-008][FR-010]"""
    contexto = {
        "turmas": services_turmas.turmas_visiveis(request.user, arquivadas=True),
        "pode_criar": False,
        "arquivadas": True,
    }
    return render(request, "cadastro/turmas/arquivadas.html", contexto)


@perfil_requerido("docente")
def turma_nova(request):
    """Cadastro da turma: o Docente vira o Professor da Disciplina (RBN-CAD-04.2).

    [US-07][RBN-CAD-04.1][RBN-CAD-04.2][FR-001]-[FR-003]
    """
    formulario = TurmaForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and formulario.is_valid():
        try:
            turma = services_turmas.criar_turma(request.user, formulario.cleaned_data)
        except ErroTurma as erro:
            formulario.add_error(erro.campo, erro.mensagem)
        else:
            messages.success(request, mensagens.TURMA_CADASTRADA)
            return redirect("cadastro:turma", tur_id=turma.pk)
    return render(
        request, "cadastro/turmas/form_turma.html", {"form": formulario, "titulo": "Nova turma"}
    )


@perfil_requerido("docente", "secretaria")
def turma(request, tur_id):
    """Turma: dados, alunos e só as ações permitidas (E5 e cenário 6 da US-07).

    [US-07][US-08][US-09][FR-008][FR-009][FR-010]
    """
    registro = services_turmas.turma_para(request.user, tur_id, CONSULTAR)
    arquivada = services_turmas.turma_arquivada(registro)
    pode_alterar = pode_alterar_turma(request.user, registro) and not arquivada
    contexto = {
        "turma": registro,
        "alunos": services_turmas.alunos_da_turma(registro),
        "arquivada": arquivada,
        "pode_alterar": pode_alterar,
        "pode_transferir": (
            pode_transferir(request.user, registro)
            and not arquivada
            and services_turmas.turma_tem_orientador_automatico(registro)
        ),
        "e_professor": pode_alterar_turma(request.user, registro),
    }
    return render(request, "cadastro/turmas/turma.html", contexto)


def _dados_iniciais(turma):
    """Valores atuais da turma para o formulário de edição."""
    return {
        "codigo_disciplina": turma.tur_dis.dis_codigo,
        "descricao": turma.tur_descricao,
        "identificador": turma.tur_identificador,
        "ano": str(turma.tur_ano),
        "semestre": str(turma.tur_semestre),
        "dia_semana": turma.tur_dia_da_semana,
        "hora_inicio": turma.tur_hora_inicio,
        "hora_termino": turma.tur_hora_termino,
        "local": turma.tur_local,
        "curso": turma.tur_cur_id,
    }


@perfil_requerido("docente", "secretaria")
@trata_turma_arquivada
def turma_editar(request, tur_id):
    """Edição da turma; Descrição e Curso travados na turma que tem ou já teve aluno (Q15).

    [US-07][RBN-CAD-04.3][FR-005][Q15]
    """
    registro = services_turmas.turma_para(request.user, tur_id, ALTERAR)
    travar = services_turmas.turma_ja_teve_aluno(registro)
    formulario = TurmaForm(
        request.POST if request.method == "POST" else None,
        initial=_dados_iniciais(registro),
        turma=registro,
        travar_descricao_e_curso=travar,
    )
    if request.method == "POST" and formulario.is_valid():
        try:
            services_turmas.editar_turma(request.user, tur_id, formulario.cleaned_data)
        except ErroTurma as erro:
            formulario.add_error(erro.campo, erro.mensagem)
        else:
            messages.success(request, mensagens.MT06_TURMA_ATUALIZADA)
            return redirect("cadastro:turma", tur_id=tur_id)
    contexto = {"form": formulario, "titulo": "Editar turma", "turma": registro}
    return render(request, "cadastro/turmas/form_turma.html", contexto)


@perfil_requerido("docente", "secretaria")
@trata_turma_arquivada
def turma_excluir(request, tur_id):
    """Exclusão da turma que nunca teve aluno: confirmação (MT-07) e execução (MT-08).

    [US-07][RBN-CAD-04.4][FR-006][Q12]
    """
    registro = services_turmas.turma_para(request.user, tur_id, ALTERAR)
    if services_turmas.turma_ja_teve_aluno(registro):
        messages.error(request, mensagens.TURMA_COM_ALUNOS)
        return redirect("cadastro:turma", tur_id=tur_id)
    if request.method == "POST":
        try:
            services_turmas.excluir_turma(request.user, tur_id)
        except ErroTurma as erro:
            messages.error(request, erro.mensagem)
            return redirect("cadastro:turma", tur_id=tur_id)
        messages.success(request, mensagens.MT08_TURMA_EXCLUIDA)
        return redirect("cadastro:turmas")
    contexto = {
        "turma": registro,
        "titulo": mensagens.EXCLUIR,
        "pergunta": mensagens.MT07_CONFIRMAR_EXCLUSAO_TURMA.format(
            identificador=registro.tur_identificador
        ),
        "rotulo": mensagens.EXCLUIR,
        "perigo": True,
    }
    return render(request, "cadastro/turmas/confirmar.html", contexto)


@perfil_requerido("docente", "secretaria")
@trata_turma_arquivada
def turma_arquivar(request, tur_id):
    """Arquivamento: confirmação (MT-09) e execução (MT-10), com os motivos da US-07.

    [US-07][RBN-CAD-04.5][FR-007]
    """
    registro = services_turmas.turma_para(request.user, tur_id, ALTERAR)
    motivo = services_turmas.motivo_para_nao_arquivar(registro)
    if motivo:
        messages.error(request, motivo)
        return redirect("cadastro:turma", tur_id=tur_id)
    if request.method == "POST":
        try:
            services_turmas.arquivar_turma(request.user, tur_id)
        except ErroTurma as erro:
            messages.error(request, erro.mensagem)
        else:
            messages.success(request, mensagens.MT10_TURMA_ARQUIVADA)
        return redirect("cadastro:turma", tur_id=tur_id)
    contexto = {
        "turma": registro,
        "titulo": mensagens.ARQUIVAR,
        "pergunta": mensagens.MT09_CONFIRMAR_ARQUIVAMENTO.format(
            identificador=registro.tur_identificador
        ),
        "rotulo": mensagens.ARQUIVAR,
        "perigo": False,
    }
    return render(request, "cadastro/turmas/confirmar.html", contexto)
