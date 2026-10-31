"""Mensagens exibidas ao usuário pelo módulo de Defesa (spec 007, research C8).

Textos entre aspas copiados das US-21 a 24 e 40 de docs/fonte/Historias_de_Usuario_v3_4.md. Os
MD-xx são PROVISÓRIOS (spec 007, "Mensagens a validar com a PO"; índice Q-124).

[US-21][US-22][US-23][US-24][US-40]
"""

# US-22 (E1 a E4). [US-22][RBN-DEF-03.1][FR-016]
# MD-01 (PROVISÓRIA): a US-22 só dá um exemplo; o FR-016 pede o nome de cada membro numa única
# mensagem. {membros} = "Nome (papel)", separados por vírgula.
MD01_CONFLITO_DE_HORARIO = (
    "Os seguintes membros da banca já possuem uma defesa agendada neste horário: {membros}"
)
