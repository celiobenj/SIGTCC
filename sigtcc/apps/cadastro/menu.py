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
