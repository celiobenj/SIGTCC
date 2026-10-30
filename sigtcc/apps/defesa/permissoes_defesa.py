"""Permissões do módulo de Defesa (spec 007, research C1 e C1a), no mesmo padrão de
cadastro/permissoes.py: predicados sem efeito colateral; quem chama decide a resposta (403 ou
mensagem).

[US-21][RBN-DEF-01.3]
"""

from sigtcc.apps.cadastro import services_orientacao
from sigtcc.apps.cadastro.cargas import CURSO_ENG_COMPUTACAO


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
