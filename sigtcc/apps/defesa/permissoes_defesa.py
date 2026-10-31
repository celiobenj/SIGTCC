"""Permissões do módulo de Defesa (spec 007, research C1 e C1a), no mesmo padrão de
cadastro/permissoes.py: predicados sem efeito colateral; quem chama decide a resposta (403 ou
mensagem).

[US-21][US-23][RBN-DEF-01.3][RBN-DEF-02.2][RBN-DEF-02.4]
"""

from sigtcc.apps.cadastro import services_orientacao
from sigtcc.apps.cadastro.cargas import CURSO_ENG_COMPUTACAO
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
