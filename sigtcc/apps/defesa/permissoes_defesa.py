"""Permissões do módulo de Defesa (spec 007, research C1 e C1a), no mesmo padrão de
cadastro/permissoes.py: predicados sem efeito colateral; quem chama decide a resposta (403 ou
mensagem).

Spec 009 (IC-08/IC-18): e_presidente pública e as permissões dos documentos, dos ouvintes, das
ocorrências e da agenda (research B2).

[US-21][US-23][US-24][US-28][US-30][RBN-DEF-01.3][RBN-DEF-02.2][RBN-DEF-02.4][RBN-DEF-03.3]
[RBN-DEF-07.3][RBN-DEF-08.1][RBN-DEF-08.2][RBN-DEF-08.3][RBN-DEF-08.4][RBN-DEF-08.5]
"""

from sigtcc.apps.cadastro import services_orientacao, services_turmas
from sigtcc.apps.cadastro.cargas import CURSO_ENG_COMPUTACAO
from sigtcc.apps.cadastro.permissoes import especializacao, tem_perfil, tipo_conta
from sigtcc.apps.cadastro.services_turmas import STATUS_SESSAO_ATIVA
from sigtcc.apps.defesa.choices import PapelBanca, StatusSessao
from sigtcc.apps.defesa.models import BancaDefesa, PresencaOuvintes


def pode_agendar(usuario, tcc):
    """Quem agenda a defesa, pelo curso da turma do TCC (RBN-DEF-01.3): em Engenharia de
    Computação, só o Orientador atual; em Sistemas de Informação e Licenciatura em Computação, só
    o Professor da Disciplina da turma. Não confere o Status do TCC nem sessão ativa (isso é
    services_defesa.tcc_elegivel).
    [US-21][RBN-DEF-01.3][FR-003][research C1a]
    """
    if tcc.tcc_tur.tur_cur.cur_nome == CURSO_ENG_COMPUTACAO:
        return services_orientacao.e_orientador_atual(usuario, tcc)
    return tcc.tcc_tur.tur_doc_id == usuario.pk


def pode_alterar_banca(usuario, sessao):
    """Botão e ação Alterar banca: quem pode agendar o TCC (pelo curso), com a sessão
    "Agendada" ou "Reagendada" (RBN-DEF-02.4; Clarifications 2026-10-31).
    [US-23][RBN-DEF-02.4][FR-011]
    """
    return sessao.def_status in (
        StatusSessao.AGENDADA,
        StatusSessao.REAGENDADA,
    ) and pode_agendar(usuario, sessao.def_tcc)


def pode_acionar_suplente(usuario, sessao):
    """Botão e ação Acionar suplente: exclusivamente o Orientador atual, com a sessão "Em
    Andamento" e um Suplente na banca (RBN-DEF-02.2; US-23 E8 e E10).
    [US-23][RBN-DEF-02.2][FR-013]
    """
    return (
        sessao.def_status == StatusSessao.EM_ANDAMENTO
        and services_orientacao.e_orientador_atual(usuario, sessao.def_tcc)
        and BancaDefesa.objects.filter(ban_def=sessao, ban_papel=PapelBanca.SUPLENTE).exists()
    )


def pode_reagendar_ou_cancelar(usuario, sessao):
    """Botões e ações Reagendar e Cancelar sessão: quem pode agendar o TCC (pelo curso) ou a
    Secretaria do curso, com a sessão "Agendada", "Reagendada" ou "Em Andamento" (RBN-DEF-03.3;
    US-24 E4 e E5; Clarifications 2026-10-31). [US-24][RBN-DEF-03.3][FR-019][FR-020][FR-022]
    """
    if sessao.def_status not in STATUS_SESSAO_ATIVA:
        return False
    secretaria = especializacao(usuario, "secretarios")
    if secretaria is not None and secretaria.sec_cur_id == sessao.def_tcc.tcc_tur.tur_cur_id:
        return True
    return pode_agendar(usuario, sessao.def_tcc)


def pode_ver_sessao(usuario, sessao):
    """Janela "Sessão de defesa" e "Histórico da defesa": membros da banca (inclusive o
    Suplente), Professor da Disciplina da turma, Secretaria do curso e Aluno do próprio TCC; o
    Coordenador e o Coorientador fora da banca, não (US-40 E5; Clarifications 2026-10-31).
    [US-40][US-23][US-24][RBN-DEF-01.4][FR-030]
    """
    tcc = sessao.def_tcc
    if tcc.tcc_alu_id == usuario.pk or tcc.tcc_tur.tur_doc_id == usuario.pk:
        return True
    secretaria = especializacao(usuario, "secretarios")
    if secretaria is not None and secretaria.sec_cur_id == tcc.tcc_tur.tur_cur_id:
        return True
    return BancaDefesa.objects.filter(ban_def=sessao, ban_usu_id=usuario.pk).exists()


# =============================================================================================
# Spec 008 (Avaliação e Resultados; IC-09): acréscimos, nada removido
# =============================================================================================


def pode_avaliar(usuario, sessao):
    """Formulário Avaliação: só os membros efetivos (Orientador, 1º e 2º Avaliador, com o
    suplente acionado no lugar do ausente), com a sessão não Cancelada; o Suplente não acionado
    e quem não integra a banca, não (RBN-DEF-05.3; spec 008 FR-007, FR-036 e D12). Não confere
    a fase da sessão nem a liberação (isso é do services_avaliacoes).
    [US-25][US-26][RBN-DEF-05.3][RBN-DEF-05.4]
    """
    if sessao.def_status == StatusSessao.CANCELADA:
        return False
    return BancaDefesa.objects.filter(
        ban_def=sessao,
        ban_usu_id=usuario.pk,
        ban_papel__in=(
            PapelBanca.ORIENTADOR_PRESIDENTE,
            PapelBanca.PRIMEIRO_AVALIADOR,
            PapelBanca.SEGUNDO_AVALIADOR,
        ),
    ).exists()


def e_presidente(usuario, sessao):
    """O usuário tem o papel "Orientador (Presidente)" na banca da sessão: é o "Orientador do
    trabalho" das US-27, US-28 e US-30 (spec 009, Clarifications B-03; research B2). Regra única,
    pública desde a spec 009 (revisão M-02). [US-27][US-28][US-30][RBN-DEF-06.4][RBN-DEF-08.2]
    """
    return BancaDefesa.objects.filter(
        ban_def=sessao, ban_usu_id=usuario.pk, ban_papel=PapelBanca.ORIENTADOR_PRESIDENTE
    ).exists()


def _e_presidente(usuario, sessao):
    """O usuário tem o papel "Orientador (Presidente)" na banca da sessão (revisão M-07).
    Delega para e_presidente (spec 009, IC-18). [US-27][RBN-DEF-06.4]
    """
    return e_presidente(usuario, sessao)


def pode_registrar_parecer(usuario, sessao):
    """Registrar parecer (US-27, passos 6 e 7): só o Orientador (Presidente da banca), pelo
    papel na banca. Fase da sessão, envios e nota ficam no services_avaliacoes.
    [US-27][RBN-DEF-06.3][RBN-DEF-06.4]
    """
    return _e_presidente(usuario, sessao)


def pode_liberar(usuario, sessao):
    """Liberar Resultado (US-27 E4): só o Orientador (Presidente da banca), pelo papel na
    banca (revisão M-07). [US-27][RBN-DEF-06.4]
    """
    return _e_presidente(usuario, sessao)


# =============================================================================================
# Spec 009 (Documentação e Encerramento; IC-08/IC-18): acréscimos, nada removido. Tabela do
# research B2: o botão aparece se e somente se o endereço aceita.
# =============================================================================================

# Papéis dos membros efetivos (o suplente acionado já ocupa o papel do titular ausente).
# [US-28][US-30][RBN-DEF-07.3][RBN-DEF-08.3]
_PAPEIS_EFETIVOS = (
    PapelBanca.ORIENTADOR_PRESIDENTE,
    PapelBanca.PRIMEIRO_AVALIADOR,
    PapelBanca.SEGUNDO_AVALIADOR,
)

# Status em que os ouvintes podem ser registrados ("durante e após", RBN-DEF-08.2; P3).
# [US-30][RBN-DEF-08.2]
STATUS_DOS_OUVINTES = (StatusSessao.EM_ANDAMENTO, StatusSessao.REALIZADA)


def _liberado(sessao):
    """O resultado da sessão foi liberado (def_data_liberacao_resultado gravado).
    [US-28][US-30][RBN-DEF-07.3][RBN-DEF-08.3]
    """
    return sessao.def_data_liberacao_resultado is not None


def _e_membro_efetivo(usuario, sessao):
    """O usuário está em membros_efetivos(sessao): Orientador, 1º ou 2º Avaliador, com o
    suplente acionado no papel do substituído; o Suplente não acionado, não (P5).
    [US-28][US-30][RBN-DEF-07.3][RBN-DEF-08.3]
    """
    return BancaDefesa.objects.filter(
        ban_def=sessao, ban_usu_id=usuario.pk, ban_papel__in=_PAPEIS_EFETIVOS
    ).exists()


def _e_professor_da_disciplina(usuario, sessao):
    """O usuário é o Professor da Disciplina da turma do TCC da sessão.
    [US-28][US-30][RBN-DEF-07.3][RBN-DEF-08.2]
    """
    return sessao.def_tcc.tcc_tur.tur_doc_id == usuario.pk


def _e_secretaria_do_curso(usuario, sessao):
    """O usuário é a Secretaria do curso da turma do TCC da sessão.
    [US-28][US-30][RBN-DEF-07.3][RBN-DEF-08.2][RBN-DEF-08.5]
    """
    secretaria = especializacao(usuario, "secretarios")
    return secretaria is not None and secretaria.sec_cur_id == sessao.def_tcc.tcc_tur.tur_cur_id


def _turma_arquivada(sessao):
    """A turma do TCC da sessão está arquivada (services_turmas.turma_arquivada; consulta sem
    trava, para decidir o botão). [US-30][RBN-CAD-04.5][RBN-DEF-08.2][RBN-DEF-08.5]
    """
    return services_turmas.turma_arquivada(sessao.def_tcc.tcc_tur)


def pode_baixar_documentos(usuario, sessao):
    """Ata Final e Folha de Aprovação (US-28; FR-003 e FR-005): só depois da liberação e só aos
    membros efetivos da banca, ao Professor da Disciplina da turma, à Secretaria do curso e ao
    Aluno do TCC. O Suplente não acionado, não (P5); antes da liberação, ninguém (P13).
    [US-28][RBN-DEF-07.3]
    """
    if not _liberado(sessao):
        return False
    return (
        sessao.def_tcc.tcc_alu_id == usuario.pk
        or _e_professor_da_disciplina(usuario, sessao)
        or _e_secretaria_do_curso(usuario, sessao)
        or _e_membro_efetivo(usuario, sessao)
    )


def pode_baixar_declaracao(usuario, sessao):
    """Declaração de participação (US-30 D; FR-021): resultado liberado e usuário em
    membros_efetivos(sessao) (inclusive o suplente acionado e o Membro Externo).
    [US-30][RBN-DEF-08.3][RBN-DEF-05.4]
    """
    return _liberado(sessao) and _e_membro_efetivo(usuario, sessao)


def pode_editar_ouvintes(usuario, sessao):
    """Botão e ação Ouvintes (US-30 A; FR-009 e FR-012): sessão Em Andamento ou Realizada,
    turma não arquivada, e o Presidente da banca ou o Professor da Disciplina da turma.
    [US-30][RBN-DEF-08.2]
    """
    if sessao.def_status not in STATUS_DOS_OUVINTES or _turma_arquivada(sessao):
        return False
    return e_presidente(usuario, sessao) or _e_professor_da_disciplina(usuario, sessao)


def pode_ver_ouvintes(usuario, sessao):
    """Lista de ouvintes na janela da sessão, só para leitura (FR-009; P3 e P6), com regra
    própria, sem chamar pode_editar_ouvintes (revisão B-02): o Presidente e o Professor da
    Disciplina da turma, em qualquer status, quando há presenças gravadas ou quando ele pode
    editar (Em Andamento ou Realizada, com a turma não arquivada); a Secretaria do curso, só com
    a sessão Em Andamento ou Realizada. Os demais perfis não veem a lista.
    [US-30][RBN-DEF-08.2]
    """
    if e_presidente(usuario, sessao) or _e_professor_da_disciplina(usuario, sessao):
        editavel = sessao.def_status in STATUS_DOS_OUVINTES and not _turma_arquivada(sessao)
        return editavel or PresencaOuvintes.objects.filter(pre_def=sessao).exists()
    return sessao.def_status in STATUS_DOS_OUVINTES and _e_secretaria_do_curso(usuario, sessao)


def pode_editar_ocorrencias(usuario, sessao):
    """Botão e ação Ocorrências (US-30 B; FR-013 e FR-015): só o Presidente da banca (P9), com
    a sessão Em Andamento, sem liberação e a turma não arquivada (revisão I-01).
    [US-30][RBN-DEF-08.5]
    """
    return (
        sessao.def_status == StatusSessao.EM_ANDAMENTO
        and not _liberado(sessao)
        and not _turma_arquivada(sessao)
        and e_presidente(usuario, sessao)
    )


def pode_ver_ocorrencias(usuario, sessao):
    """Texto das ocorrências, só para leitura (FR-014; P10): com texto gravado, o Presidente da
    banca, o Professor da Disciplina da turma e a Secretaria do curso. Avaliadores, Suplente e
    Aluno, não. [US-30][RBN-DEF-08.5]
    """
    if not sessao.def_ocorrencias:
        return False
    return (
        e_presidente(usuario, sessao)
        or _e_professor_da_disciplina(usuario, sessao)
        or _e_secretaria_do_curso(usuario, sessao)
    )


def pode_gerar_agenda(usuario):
    """Botão e rota "Agenda de defesas (PDF)" (US-30 F; FR-022): perfil Docente (qualquer um,
    inclusive o Coordenador e o Professor da Disciplina; a agenda é pública, P2) ou Secretaria.
    O Aluno e o Membro Externo, não. [US-30][RBN-DEF-08.1]
    """
    return tem_perfil(usuario, "docente", "coordenador", "secretaria")


def pode_ver_ouvintes_das_defesas(usuario):
    """Menu "Ouvintes das defesas" (US-30 C; FR-016): só a Secretaria (P8).
    [US-30][RBN-DEF-08.4]
    """
    return tipo_conta(usuario) == "secretaria"
