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
]
