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

# US-23 (E3, E4, E6, E7). [US-23][RBN-DEF-02.1][RBN-DEF-02.2][RBN-DEF-02.4]
AVALIADORES_DISTINTOS = (
    "Selecione avaliadores distintos que não façam parte da orientação do trabalho"
)
JUSTIFICATIVA = "Informe uma justificativa de até 500 caracteres"
AUSENCIA_DO_ORIENTADOR = "A ausência do Orientador exige o reagendamento da sessão"

# MD-02 a MD-04 (PROVISÓRIAS): avisos da alteração da banca (US-23 C.e, sem texto exato).
# {quando} = "DD/MM/AAAA às HH:MM".
MD02_BANCA_INCLUIDO = (
    "Você passou a integrar, como {papel}, a banca da defesa de {aluno} em {quando}. "
    "TCC: {titulo}."
)
MD03_BANCA_REMOVIDO = (
    "Você não faz mais parte da banca da defesa de {aluno} marcada para {quando}. TCC: {titulo}."
)
MD04_BANCA_ALTERADA_ALUNO = (
    "A banca da sua defesa de {quando} foi alterada: {incluido} entrou como {papel}"
    " no lugar de {removido}."
)
MD04_ASSUNTO = "SIGTCC: alteração da banca"

# US-21 E3 e US-23 E2. [US-21][US-23][RBN-DEF-01.1][RBN-DEF-02.1]
CAMPO_OBRIGATORIO = "Campo obrigatório"

# US-24. [US-24][RBN-DEF-03.2][RBN-DEF-03.3]
DEFESA_AGENDADA = "Defesa agendada com sucesso"

# MD-05 a MD-07 (PROVISÓRIAS): avisos ao Aluno e a toda a banca (US-24 passos 4 e 5, B.e, C.d;
# sem texto exato). {lugar} = Local ou Link da Videochamada; {documento} = link do Documento para
# Defesa.
MD05_DEFESA_AGENDADA = (
    "Defesa de {aluno} agendada para {quando} ({formato}: {lugar}). TCC: {titulo}. "
    "Documento para Defesa: {documento}"
)
MD05_ASSUNTO = "SIGTCC: defesa agendada"
MD06_DEFESA_REAGENDADA = (
    "Defesa de {aluno} reagendada para {quando} ({formato}: {lugar}). TCC: {titulo}. "
    "Justificativa: {justificativa}"
)
MD06_ASSUNTO = "SIGTCC: defesa reagendada"
MD07_DEFESA_CANCELADA = (
    "A defesa de {aluno} marcada para {quando} foi cancelada. TCC: {titulo}. "
    "Justificativa: {justificativa}"
)
MD07_ASSUNTO = "SIGTCC: defesa cancelada"
