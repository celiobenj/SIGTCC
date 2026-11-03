"""Permissões do módulo de Defesa (spec 007, research C1 e C1a), no mesmo padrão de
cadastro/permissoes.py: predicados sem efeito colateral; quem chama decide a resposta (403 ou
mensagem).

[US-21][US-23][US-24][RBN-DEF-01.3][RBN-DEF-02.2][RBN-DEF-02.4][RBN-DEF-03.3]
"""

from sigtcc.apps.cadastro import services_orientacao
from sigtcc.apps.cadastro.cargas import CURSO_ENG_COMPUTACAO
from sigtcc.apps.cadastro.permissoes import especializacao
from sigtcc.apps.cadastro.services_turmas import STATUS_SESSAO_ATIVA
from sigtcc.apps.defesa.choices import PapelBanca, StatusSessao
from sigtcc.apps.defesa.models import BancaDefesa


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


def _e_presidente(usuario, sessao):
    """O usuário tem o papel "Orientador (Presidente)" na banca da sessão (revisão M-07).
    [US-27][RBN-DEF-06.4]
    """
    return BancaDefesa.objects.filter(
        ban_def=sessao, ban_usu_id=usuario.pk, ban_papel=PapelBanca.ORIENTADOR_PRESIDENTE
    ).exists()


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
