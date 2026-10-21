"""Views de turmas e alunos (spec 004): só orquestram; as regras ficam em services_turmas.py e
importacao.py (constituição, princípio IV; research B1).

[US-07][US-08][US-09][FR-001]-[FR-026]
"""

from functools import wraps

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from sigtcc.apps.cadastro import importacao, mensagens, services_turmas
from sigtcc.apps.cadastro.forms_turmas import (
    EditarAlunoForm,
    EncerramentoForm,
    ExclusaoAlunoForm,
    ImportacaoForm,
    MatriculaForm,
    TransferenciaForm,
    TurmaForm,
)
from sigtcc.apps.cadastro.models import EquivalenciaCursos
from sigtcc.apps.cadastro.permissoes import (
    perfil_requerido,
    pode_alterar_turma,
    pode_transferir,
    tipo_conta,
)
from sigtcc.apps.cadastro.services_turmas import (
    ALTERAR,
    CONSULTAR,
    TRANSFERIR,
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


def _turma_do_professor(usuario, tur_id):
    """Turma (404) só para o Professor da Disciplina dela (403), também a arquivada: telas de
    consulta que são só dele (contracts/rotas.md). [US-08][US-09][RBN-CAD-05.8][FR-018][FR-026]
    """
    registro = services_turmas.turma_para(usuario, tur_id, CONSULTAR)
    if not pode_alterar_turma(usuario, registro):
        raise PermissionDenied
    return registro


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
    """Valores atuais da turma para o formulário de edição. [US-07][FR-005]"""
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


# ---------------------------------------------------------------------------------------------
# Matrícula individual e edição do aluno (US-08)
# ---------------------------------------------------------------------------------------------


def _codigos_de_curso():
    """Sugestões do campo Curso: códigos da equivalência com o nome do curso (sem JavaScript).

    [US-08][RBN-CAD-05.7][B18]
    """
    return EquivalenciaCursos.objects.select_related("eqc_cur").order_by("eqc_codigo_uea")


def _avisar_resultado(request, resultado):
    """Mensagem principal e avisos (MT-13, MT-29) da matrícula. [US-08][Q16][RBN-CAD-05.7]"""
    messages.success(request, resultado.mensagem)
    for aviso in resultado.avisos:
        messages.warning(request, aviso)


@perfil_requerido("docente", "secretaria")
@trata_turma_arquivada
def matricular(request, tur_id):
    """ "Matricular alunos": "Matrícula individual" e "Importar arquivo (CSV/XLSX)".

    [US-08][RBN-CAD-05.1][RBN-CAD-05.5][FR-011]-[FR-015]
    """
    registro = services_turmas.turma_para(request.user, tur_id, ALTERAR)
    formulario = MatriculaForm(request.POST if request.method == "POST" else None)
    erro = ""
    if request.method == "POST" and formulario.is_valid():
        dados = formulario.cleaned_data
        resultado = services_turmas.matricular_individual(
            request.user, tur_id, dados["matricula"], dados["nome"], dados["curso"]
        )
        if resultado.matriculado:
            _avisar_resultado(request, resultado)
            return redirect("cadastro:turma", tur_id=tur_id)
        erro = resultado.mensagem
    contexto = {
        "turma": registro,
        "form": formulario,
        "erro": erro,
        "codigos": _codigos_de_curso(),
    }
    return render(request, "cadastro/turmas/matricular.html", contexto)


@perfil_requerido("docente", "secretaria")
@trata_turma_arquivada
def aluno_editar(request, tur_id, alu_id):
    """Edição do Nome Completo e do Curso; a Matrícula é só leitura (RBN-CAD-05.3).

    [US-08][RBN-CAD-05.3][FR-019][I-7]
    """
    registro = services_turmas.turma_para(request.user, tur_id, ALTERAR)
    aluno = services_turmas.vinculo_na_turma(registro, alu_id)
    formulario = EditarAlunoForm(
        request.POST if request.method == "POST" else None,
        initial={"nome": aluno.alu.usu_nome, "curso": aluno.alu_codigo_curso},
    )
    if request.method == "POST" and formulario.is_valid():
        dados = formulario.cleaned_data
        services_turmas.editar_aluno(request.user, tur_id, alu_id, dados["nome"], dados["curso"])
        messages.success(request, mensagens.MT14_ALUNO_ATUALIZADO)
        return redirect("cadastro:turma", tur_id=tur_id)
    contexto = {
        "turma": registro,
        "aluno": aluno,
        "form": formulario,
        "codigos": _codigos_de_curso(),
    }
    return render(request, "cadastro/turmas/editar_aluno.html", contexto)


# ---------------------------------------------------------------------------------------------
# Importação por CSV ou XLSX (US-08; diagrama "Matrícula por CSV")
# ---------------------------------------------------------------------------------------------


@perfil_requerido("docente", "secretaria")
@trata_turma_arquivada
def importar(request, tur_id):
    """Envio do arquivo e prévia (nada é gravado até "Confirmar importação").

    [US-08][RBN-CAD-05.2][FR-016][FR-017][Q13]
    """
    registro = services_turmas.turma_para(request.user, tur_id, ALTERAR)
    formulario = ImportacaoForm(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
    )
    erro = ""
    if request.method == "POST" and formulario.is_valid():
        try:
            linhas = importacao.ler_arquivo(formulario.cleaned_data["arquivo"])
        except importacao.ErroModelo:
            erro = mensagens.ARQUIVO_FORA_DO_MODELO
        else:
            previa = importacao.montar_previa(registro, linhas)
            token = services_turmas.guardar_previa(request.session, registro, previa)
            contexto = {"turma": registro, "previa": previa, "token": token}
            return render(request, "cadastro/turmas/previa.html", contexto)
    contexto = {"turma": registro, "form": formulario, "erro": erro}
    return render(request, "cadastro/turmas/importar.html", contexto)


@require_POST
@perfil_requerido("docente", "secretaria")
@trata_turma_arquivada
def importar_confirmar(request, tur_id):
    """ "Confirmar importação": prévia presa à turma por código; resumo por POST/redirect/GET.

    [US-08][RBN-CAD-05.2][FR-018][B-2][N3]
    """
    services_turmas.turma_para(request.user, tur_id, ALTERAR)
    try:
        resumo = services_turmas.confirmar_importacao(
            request.user, tur_id, request.POST.get("token", ""), request.session
        )
    except services_turmas.PreviaInvalida:
        messages.warning(request, mensagens.MT32_PREVIA_INVALIDA)
        return redirect("cadastro:importar", tur_id=tur_id)
    except services_turmas.ImportacaoRepetida:
        return redirect("cadastro:turma", tur_id=tur_id)
    request.session[services_turmas.CHAVE_RESUMO] = {"tur_id": tur_id, **resumo}
    return redirect("cadastro:importar_resumo", tur_id=tur_id)


@perfil_requerido("docente", "secretaria")
def importar_resumo(request, tur_id):
    """Resumo da importação (MT-15), mostrado uma vez; recarregar volta para a turma.

    [US-08][RBN-CAD-05.2][FR-018]
    """
    registro = _turma_do_professor(request.user, tur_id)
    resumo = request.session.pop(services_turmas.CHAVE_RESUMO, None)
    if not resumo or resumo.get("tur_id") != tur_id:
        return redirect("cadastro:turma", tur_id=tur_id)
    texto = mensagens.MT15_RESUMO_IMPORTACAO.format(n=resumo["n"], r=resumo["r"], c=resumo["c"])
    contexto = {"turma": registro, "texto": texto, "rejeitadas": resumo["rejeitadas"]}
    return render(request, "cadastro/turmas/resumo.html", contexto)


@require_POST
@perfil_requerido("docente", "secretaria")
def importar_cancelar(request, tur_id):
    """ "Cancelar" na prévia: apaga a prévia e volta para a turma. [US-08][B10]"""
    _turma_do_professor(request.user, tur_id)
    services_turmas.descartar_previa(request.session)
    return redirect("cadastro:turma", tur_id=tur_id)


@perfil_requerido("docente")
def modelo_importacao(request):
    """Modelo de importação (CSV em UTF-8 com ";"; spec Q11). [US-08][RBN-CAD-05.2][FR-016]"""
    resposta = HttpResponse(importacao.gerar_modelo_csv(), content_type="text/csv; charset=utf-8")
    resposta["Content-Disposition"] = 'attachment; filename="modelo_importacao_alunos.csv"'
    return resposta


# ---------------------------------------------------------------------------------------------
# Transferência (US-08; RBN-CAD-05.6)
# ---------------------------------------------------------------------------------------------


@perfil_requerido("docente", "secretaria")
@trata_turma_arquivada
def aluno_transferir(request, tur_id, alu_id):
    """ "Transferir": Turma de Destino e Justificativa; Professor da turma ou Secretaria do curso.

    [US-08][RBN-CAD-05.6][FR-020]-[FR-022][Q9]
    """
    registro = services_turmas.turma_para(request.user, tur_id, TRANSFERIR)
    if not services_turmas.turma_tem_orientador_automatico(registro):
        raise PermissionDenied
    aluno = services_turmas.vinculo_na_turma(registro, alu_id)
    destinos = services_turmas.turmas_destino_possiveis(registro, aluno)
    if not destinos.exists():
        messages.error(request, mensagens.MT19_SEM_DESTINO)
        return redirect("cadastro:turma", tur_id=tur_id)
    formulario = TransferenciaForm(
        request.POST if request.method == "POST" else None, destinos=destinos
    )
    erro = ""
    if request.method == "POST":
        if formulario.is_valid():
            dados = formulario.cleaned_data
            try:
                destino = services_turmas.transferir(
                    request.user, tur_id, alu_id, dados["destino"].pk, dados["justificativa"]
                )
            except ErroTurma as falha:
                erro = falha.mensagem
            else:
                messages.success(
                    request,
                    mensagens.MT16_TRANSFERIDO.format(identificador=destino.tur_identificador),
                )
                return redirect("cadastro:turma", tur_id=tur_id)
        elif "destino" in formulario.errors:
            erro = mensagens.MT19_SEM_DESTINO
    contexto = {"turma": registro, "aluno": aluno, "form": formulario, "erro": erro}
    return render(request, "cadastro/turmas/transferir.html", contexto)


# ---------------------------------------------------------------------------------------------
# Exclusão do aluno, encerramento da participação e lista de excluídos ou transferidos (US-09)
# ---------------------------------------------------------------------------------------------


@perfil_requerido("docente", "secretaria")
@trata_turma_arquivada
def aluno_excluir(request, tur_id, alu_id):
    """ "Excluir da turma" em duas etapas: Justificativa e "Confirmar"; depois a confirmação final
    (MT-24) com a justificativa num campo oculto, "Confirmar" e "Cancelar" (research B14).
    [US-09][RBN-CAD-05.4][FR-023]
    """
    registro = services_turmas.turma_para(request.user, tur_id, ALTERAR)
    aluno = services_turmas.vinculo_na_turma(registro, alu_id)
    tcc = services_turmas.tcc_do_aluno(registro, aluno)
    if not services_turmas.aluno_pode_ser_excluido(tcc):
        messages.error(request, mensagens.ALUNO_TEM_PROPOSTA)
        return redirect("cadastro:turma", tur_id=tur_id)
    formulario = ExclusaoAlunoForm(request.POST if request.method == "POST" else None)
    confirmacao_final = False
    if request.method == "POST" and formulario.is_valid():
        if request.POST.get("confirmacao_final"):
            try:
                services_turmas.excluir_aluno(
                    request.user, tur_id, alu_id, formulario.cleaned_data["justificativa"]
                )
            except ErroTurma as erro:
                messages.error(request, erro.mensagem)
            else:
                messages.success(request, mensagens.ALUNO_EXCLUIDO)
            return redirect("cadastro:turma", tur_id=tur_id)
        confirmacao_final = True
    contexto = {
        "turma": registro,
        "aluno": aluno,
        "form": formulario,
        "confirmacao_final": confirmacao_final,
        "pergunta": mensagens.MT24_CONFIRMAR_EXCLUSAO_ALUNO.format(nome=aluno.alu.usu_nome),
    }
    return render(request, "cadastro/turmas/excluir_aluno.html", contexto)


@perfil_requerido("docente", "secretaria")
@trata_turma_arquivada
def aluno_encerrar(request, tur_id, alu_id):
    """ "Encerrar participação": Status e Justificativa; sucesso MT-23, sessão ativa MT-30.

    Só para TCC 'Em Andamento' ou 'Apto para Defesa'; nos outros, 404 (research B15).
    [US-09][RBN-CAD-08.4][FR-024][Q14]
    """
    registro = services_turmas.turma_para(request.user, tur_id, ALTERAR)
    aluno = services_turmas.vinculo_na_turma(registro, alu_id)
    if not services_turmas.aluno_pode_ser_encerrado(services_turmas.tcc_do_aluno(registro, aluno)):
        raise Http404
    formulario = EncerramentoForm(request.POST if request.method == "POST" else None)
    erro = ""
    if request.method == "POST" and formulario.is_valid():
        dados = formulario.cleaned_data
        try:
            services_turmas.encerrar_participacao(
                request.user, tur_id, alu_id, dados["status"], dados["justificativa"]
            )
        except ErroTurma as falha:
            erro = falha.mensagem
        else:
            messages.success(
                request, mensagens.MT23_PARTICIPACAO_ENCERRADA.format(status=dados["status"])
            )
            return redirect("cadastro:turma", tur_id=tur_id)
    contexto = {"turma": registro, "aluno": aluno, "form": formulario, "erro": erro}
    return render(request, "cadastro/turmas/encerrar.html", contexto)


@perfil_requerido("docente", "secretaria")
def excluidos_transferidos(request, tur_id):
    """Lista só de leitura dos alunos excluídos ou transferidos da turma, só para o Professor da
    Disciplina, também na turma arquivada (research B16). [US-09][RBN-CAD-05.8][FR-026][I-4]
    """
    registro = _turma_do_professor(request.user, tur_id)
    contexto = {
        "turma": registro,
        "registros": services_turmas.excluidos_e_transferidos(registro),
    }
    return render(request, "cadastro/turmas/excluidos_transferidos.html", contexto)
