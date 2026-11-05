"""Ouvintes da sessão de defesa (spec 009, US2; research B9; contrato
specs/009-documentacao-encerramento/contracts/servicos-documentos.md §2).

Grava só Presenca_Ouvintes e, na primeira presença de uma matrícula, o registro em Ouvintes, que
nunca é alterado nem apagado por esta feature (P4). Cumpre o contrato da spec 007: nunca grava
def_status nem Historico_Defesas e nunca cria sessão.

Spec 009 (US3): ocorrências da sessão (Defesas.def_ocorrencias; RBN-DEF-08.5).

[US-30][RBN-DEF-08.2][RBN-DEF-08.4][RBN-DEF-08.5]
"""

from django.db import transaction
from django.db.models import OuterRef, Subquery

from sigtcc.apps.defesa import mensagens, permissoes_defesa, services_defesa
from sigtcc.apps.defesa.choices import PapelBanca, StatusSessao
from sigtcc.apps.defesa.forms_ouvintes import (
    TAMANHO_DAS_OCORRENCIAS,
    normalizar_ocorrencias,
    repetidas,
    validar_matricula,
    validar_nome,
)
from sigtcc.apps.defesa.models import BancaDefesa, Defesas, Ouvintes, PresencaOuvintes


class ErroOuvintes(Exception):
    """Recusa ao salvar os ouvintes: `campo` ("permissao", "nome", "matricula") e a mensagem
    exata; nada é gravado. [US-30][RBN-DEF-08.2]
    """

    def __init__(self, campo, mensagem, linha=None):
        """Guarda o campo, a mensagem e o índice da linha (ou None). [US-30][RBN-DEF-08.2]"""
        super().__init__(mensagem)
        self.campo = campo
        self.mensagem = mensagem
        self.linha = linha


PERMISSAO = "permissao"


def ouvintes_da_sessao(sessao):
    """Ouvintes com presença na sessão, por nome. [US-30][RBN-DEF-08.2]"""
    return Ouvintes.objects.filter(presencaouvintes__pre_def=sessao).order_by(
        "ouv_nome", "ouv_matricula"
    )


def _conferir_linhas(linhas):
    """Revalida a lista (mesmas regras do formulário; o serviço é a fonte): nome, matrícula e
    duplicata só dentro da lista. Devolve [(nome, matrícula)] ou levanta ErroOuvintes.
    [US-30][RBN-DEF-08.2]
    """
    conferidas = []
    for indice, (nome, matricula) in enumerate(linhas):
        nome_valido = validar_nome(nome)
        if nome_valido is None:
            raise ErroOuvintes("nome", mensagens.NOME_INVALIDO, indice)
        matricula_valida = validar_matricula(matricula)
        if matricula_valida is None:
            raise ErroOuvintes("matricula", mensagens.MATRICULA_INVALIDA, indice)
        conferidas.append((nome_valido, matricula_valida))
    duplicadas = repetidas([matricula for _, matricula in conferidas])
    if duplicadas:
        raise ErroOuvintes("matricula", mensagens.OUVINTE_REPETIDO, duplicadas[0])
    return conferidas


def salvar_ouvintes(usuario, def_id, linhas):
    """Grava a lista inteira de ouvintes da sessão (US-30 A; FR-010 a FR-012), numa transação
    com a trava turma → aluno → TCC → sessão (travar_tcc e travar_sessao; a turma arquivada
    levanta TurmaArquivada). Com a sessão travada, confere pode_editar_ouvintes (senão
    ErroOuvintes de permissão); revalida as linhas; processa as matrículas novas em ordem
    crescente (sem deadlock no índice único entre sessões; I-02) com get_or_create, que
    reaproveita o registro existente sem mudar o nome (P4); apaga as presenças que saíram e cria
    as novas. Nunca apaga Ouvintes. [US-30][RBN-DEF-08.2]
    """
    with transaction.atomic():
        services_defesa.travar_tcc(services_defesa.tcc_da_sessao(def_id))
        sessao = services_defesa.travar_sessao(def_id)
        if not permissoes_defesa.pode_editar_ouvintes(usuario, sessao):
            raise ErroOuvintes(PERMISSAO, "")
        conferidas = _conferir_linhas(linhas)
        nomes = {matricula: nome for nome, matricula in conferidas}
        atuais = dict(
            PresencaOuvintes.objects.filter(pre_def=sessao).values_list(
                "pre_ouv__ouv_matricula", "pre_ouv_id"
            )
        )
        registros = {}
        for matricula in sorted(set(nomes) - set(atuais)):
            registros[matricula], _ = Ouvintes.objects.get_or_create(
                ouv_matricula=matricula, defaults={"ouv_nome": nomes[matricula]}
            )
        saem = [ouv_id for matricula, ouv_id in atuais.items() if matricula not in nomes]
        if saem:
            PresencaOuvintes.objects.filter(pre_def=sessao, pre_ouv_id__in=saem).delete()
        PresencaOuvintes.objects.bulk_create(
            [PresencaOuvintes(pre_def=sessao, pre_ouv=registro) for registro in registros.values()]
        )
    return sessao


def visao_da_sessao(usuario, sessao):
    """Blocos `ouvintes` e `ocorrencias` do contexto da janela Sessão de defesa (FR-009, FR-013
    e FR-014): a lista de ouvintes (só para quem pode ver), se pode editar (botão Ouvintes), a
    mensagem da E7 ao Presidente e ao Professor da Disciplina quando o status não é Em Andamento
    nem Realizada e, em `ocorrencias`, o texto (só a quem pode ver), se pode ver e se pode
    editar (botão Ocorrências). [US-30][RBN-DEF-08.2][RBN-DEF-08.5]
    """
    pode_ver = permissoes_defesa.pode_ver_ouvintes(usuario, sessao)
    responsavel = permissoes_defesa.e_presidente(
        usuario, sessao
    ) or permissoes_defesa.e_professor_da_disciplina(usuario, sessao)
    fora_do_status = sessao.def_status not in permissoes_defesa.STATUS_DOS_OUVINTES
    ocorrencias_visiveis = permissoes_defesa.pode_ver_ocorrencias(usuario, sessao)
    return {
        "lista": list(ouvintes_da_sessao(sessao)) if pode_ver else [],
        "pode_ver": pode_ver,
        "pode_editar": permissoes_defesa.pode_editar_ouvintes(usuario, sessao),
        "aviso": mensagens.OUVINTES_FORA_DO_STATUS if responsavel and fora_do_status else None,
        # Spec 009 (US3): bloco ocorrencias (texto só leitura e botão Ocorrências; FR-013 e
        # FR-014). [US-30][RBN-DEF-08.5]
        "ocorrencias": {
            "texto": sessao.def_ocorrencias if ocorrencias_visiveis else None,
            "pode_ver": ocorrencias_visiveis,
            "pode_editar": permissoes_defesa.pode_editar_ocorrencias(usuario, sessao),
        },
    }


# =============================================================================================
# Ouvintes das defesas (US-30 C; RBN-DEF-08.4; research B11)
# =============================================================================================

# Horas complementares por sessão assistida (RBN-DEF-08.4); valor fixo exibido, não gravado.
# [US-30][RBN-DEF-08.4]
HORAS_POR_SESSAO = "2 horas"


def ouvintes_das_defesas(periodo, cur_id):
    """Linhas da tela "Ouvintes das defesas" (FR-016 e FR-017), reaproveitáveis pelo relatório
    RBN-REL-03.4 do Épico 3: uma por presença em sessão Realizada (o ouvinte de duas sessões
    aparece duas vezes), com o ouvinte, o TCC, o aluno e o nome do Orientador (Presidente da
    banca) por Subquery, numa consulta. `periodo` é o Q sobre Defesas de
    FiltroPeriodoForm.filtro() (sem prefixo); `cur_id` é o curso ou None (todos). Ordem: data da
    defesa, título e nome do ouvinte. [US-30][RBN-DEF-08.4][RBN-DEF-01.5][RBN-CAD-14.1]
    """
    sessoes = Defesas.objects.filter(periodo, def_status=StatusSessao.REALIZADA)
    if cur_id is not None:
        sessoes = sessoes.filter(def_tcc__tcc_tur__tur_cur_id=cur_id)
    presidente = BancaDefesa.objects.filter(
        ban_def=OuterRef("pre_def"), ban_papel=PapelBanca.ORIENTADOR_PRESIDENTE
    ).values("ban_usu__usu_nome")[:1]
    return (
        PresencaOuvintes.objects.filter(pre_def__in=sessoes)
        .select_related("pre_ouv", "pre_def__def_tcc__tcc_alu__alu")
        .annotate(orientador_nome=Subquery(presidente))
        .order_by("pre_def__def_data", "pre_def__def_tcc__tcc_titulo", "pre_ouv__ouv_nome")
    )


# =============================================================================================
# Ocorrências da sessão (US-30 B; RBN-DEF-08.5; research B10)
# =============================================================================================


def registrar_ocorrencias(usuario, def_id, texto):
    """Grava Defesas.def_ocorrencias (US-30 B; FR-013 e FR-015), numa transação com a trava
    turma → aluno → TCC → sessão (travar_tcc e travar_sessao; a turma arquivada levanta
    TurmaArquivada; revisão M-14). Com a sessão travada, confere pode_editar_ocorrencias (só o
    Presidente, Em Andamento e sem liberação; senão ErroOuvintes de permissão). Normaliza as
    quebras de linha e confere os 2.000 caracteres (MX-01); vazio grava NULL. Grava só a coluna
    def_ocorrencias e nunca Historico_Defesas. [US-30][RBN-DEF-08.5]
    """
    with transaction.atomic():
        services_defesa.travar_tcc(services_defesa.tcc_da_sessao(def_id))
        sessao = services_defesa.travar_sessao(def_id)
        if not permissoes_defesa.pode_editar_ocorrencias(usuario, sessao):
            raise ErroOuvintes(PERMISSAO, "")
        texto = normalizar_ocorrencias(texto)
        if len(texto) > TAMANHO_DAS_OCORRENCIAS:
            raise ErroOuvintes("ocorrencias", mensagens.MX01_OCORRENCIAS_LONGAS)
        sessao.def_ocorrencias = texto or None
        sessao.save(update_fields=["def_ocorrencias"])
    return sessao
