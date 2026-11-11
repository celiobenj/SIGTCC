"""Item do menu lateral do módulo Relatórios, lido por cadastro/contexto.py (spec 010;
contracts/rotas.md). Coordenador de Curso é Docente; Aluno e Membro Externo não veem o item.

[US-31 E4][US-47][US-32][US-33][RBN-REL-01.1][FR-001]
"""

ITENS = [
    {
        "rotulo": "Relatórios",
        "icone": "table_chart",
        "rota": "relatorios:lista",
        "perfis": ("docente", "secretaria"),
        "ordem": 31,
        "secao": "Gestão",
    },
]
