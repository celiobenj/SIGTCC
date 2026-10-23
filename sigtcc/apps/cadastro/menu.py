"""Itens do menu lateral do app cadastro (research A8; contrato §3).

Cada item: rotulo, icone (Material Symbols), rota (nome da URL), perfis (tipos de conta e papéis),
ordem e secao opcional (título de grupo no menu).

[FR-022][FR-025][FR-010][Q7]
"""

ITENS = [
    {
        "rotulo": "Início",
        "icone": "home",
        "rota": "cadastro:painel",
        "perfis": ("aluno", "docente", "secretaria", "membro_externo"),
        "ordem": 0,
    },
    # Spec 005: item "Turmas" do Aluno, com as turmas em que está matriculado; não dá acesso à
    # tela da turma da spec 004 (FR-010 da spec 004). [US-13][US-15][FR-031][Q-89]
    {
        "rotulo": "Turmas",
        "icone": "groups",
        "rota": "cadastro:minhas_turmas",
        "perfis": ("aluno",),
        "ordem": 10,
    },
    # Spec 004: turmas do Professor da Disciplina ou do curso da Secretaria (Q9). Enquanto a rota
    # não existir, o processador de contexto esconde o item. [US-07][FR-010][Q9]
    {
        "rotulo": "Turmas",
        "icone": "groups",
        "rota": "cadastro:turmas",
        "perfis": ("docente", "secretaria"),
        "ordem": 10,
    },
]
