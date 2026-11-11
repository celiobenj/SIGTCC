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

# US-21 (E2, E4, E6, E7). [US-21][RBN-DEF-01.1][RBN-DEF-01.3]
NENHUM_TCC_DISPONIVEL = "Nenhum TCC disponível para agendamento"
DATA_NO_PASSADO = "A data e o horário devem ser posteriores ao momento atual"
LINK_INVALIDO = "O link deve começar com https:// e ter até 500 caracteres"
TCC_NAO_AGENDAVEL = "Este TCC não pode ser agendado por você"
# MD-08 (PROVISÓRIA): a US-21 E5 só diz que o sistema "informa o limite de até 100 caracteres".
MD08_LOCAL_LONGO = "O Local deve ter até 100 caracteres"

# US-40 E5. [US-40][RBN-DEF-01.4][FR-030]
SEM_PERMISSAO_SESSAO = "Você não tem permissão para visualizar esta defesa"

# US-23. [US-23][RBN-DEF-02.3]
LINK_CADASTRAR_EXTERNO = "O Membro Externo não está na lista? Cadastrar"
# MD-09 e MD-10 (PROVISÓRIAS): confirmação na tela (US-23 C.e e D.e, sem texto exato).
MD09_BANCA_ALTERADA = "Banca alterada com sucesso"
MD10_SUPLENTE_ACIONADO = "Suplente acionado com sucesso"

# MD-11 e MD-12 (PROVISÓRIAS): confirmação na tela (US-24 B.e e C.d, sem texto exato).
MD11_SESSAO_REAGENDADA = "Sessão reagendada com sucesso"
MD12_SESSAO_CANCELADA = "Sessão cancelada com sucesso"
# MD-13 (PROVISÓRIA): aviso do formulário Reagendar sessão de defesa (US-24 B.b descreve o aviso
# sem aspas).
MD13_BANCA_MANTIDA = "A banca composta e as avaliações já salvas são mantidas."

# US-40 (E2 a E4). [US-40][RBN-DEF-01.4][RBN-DEF-01.5]
NENHUMA_SESSAO = "Nenhuma sessão de defesa encontrada para o período e filtros selecionados"
DATA_INICIAL_MAIOR = "A data inicial não pode ser superior à data final"
DATA_INVALIDA = "Informe uma data válida no formato DD/MM/AAAA"

# =============================================================================================
# Spec 008 (Avaliação e Resultados; IC-09): textos entre aspas das US-25, US-26 e US-27 e as
# MA-01 a MA-14 da tabela "Mensagens a validar com a PO" da spec 008, todas aprovadas (Q-129).
# =============================================================================================

# US-25 (E2, E3, E4, E8), US-26 (E2 a E4) e US-27 (E3, E4).
# [US-25][US-26][US-27][RBN-DEF-05.2][RBN-DEF-05.3][RBN-DEF-06.3][RBN-DEF-06.4]
NOTA_FORA_DA_FAIXA = (
    "A nota deve situar-se entre o valor mínimo e o máximo para o conceito selecionado "
    "(ex.: de 6,0 a 7,9 para Competente)"
)
CRITERIOS_INCOMPLETOS = "Todos os 9 critérios devem conter conceito e nota"
ASSINATURA_OBRIGATORIA = "A assinatura do membro da banca é obrigatória para finalizar a avaliação"
ACESSO_RESTRITO = "Acesso restrito aos membros avaliadores da banca"
ASSINATURA_TAMANHO = "O arquivo de assinatura deve ter tamanho máximo de 2 MB"
ASSINATURA_FORMATO = "Formato não suportado. Envie a assinatura em PNG ou JPG"
SELECIONE_O_PARECER = "Selecione o parecer da banca para continuar"
APENAS_O_ORIENTADOR = "Apenas o Orientador (Presidente da banca) pode liberar o resultado da defesa"

# MA-01 a MA-14 (aprovadas, Q-129; MA-13 e MA-14 no /speckit-analyze). {nota} com vírgula.
# [US-25][US-26][US-27][RBN-DEF-05.1][RBN-DEF-05.2][RBN-DEF-06.4][RBN-DEF-05.4]
MA01_CONCEITO_E_NOTA = "Informe o conceito e a nota do critério, ou deixe os dois em branco"
MA02_OBSERVACOES_LONGAS = "As observações devem ter até 500 caracteres"
MA03_SO_PARTE_ESCRITA = "A sessão ainda não começou: só a Parte Escrita pode ser avaliada e salva."
MA04_RESULTADO_LIBERADO = (
    "O resultado desta defesa já foi liberado e as avaliações não podem mais ser alteradas"
)
MA05_CONFIRMAR_LIBERACAO = (
    "Liberar o resultado com nota final {nota} e parecer {parecer}? Depois disso, as notas não "
    "podem mais ser alteradas."
)
# MA-06 e MA-07 (avisos ao Aluno e à banca) foram removidas em 10/11/2026 (Q-131 B): só a
# Secretaria recebe o aviso do resultado.
MA08_ASSUNTO = "SIGTCC: resultado da defesa"
MA08_RESULTADO_SECRETARIA = "Defesa de {aluno} encerrada com parecer {parecer}. TCC: {titulo}."
MA09_RASCUNHO_SALVO = "Rascunho salvo"
MA10_AVALIACAO_ENVIADA = "Avaliação enviada com sucesso"
MA11_RESULTADO_LIBERADO = "Resultado liberado com sucesso"
MA12_SEM_BANCAS = "Você não participa de nenhuma banca no momento"
MA13_AVALIACAO_JA_ENVIADA = (
    "Sua avaliação já foi enviada. Para alterá-la, use Reabrir minha avaliação"
)
MA14_ASSINATURA_GRANDE = "A imagem da assinatura deve ter no máximo 2000 × 1000 pixels"

# =============================================================================================
# Spec 009 (Documentação e Encerramento; IC-08): só acréscimo. Textos entre aspas das US-28 e
# US-30 e as MX da tabela "Mensagens a validar com a PO" da spec 009.
# =============================================================================================

# US-28 (E1 a E3, E6) e US-30 (E1 a E4, E7, F).
# [US-28][US-30][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-07.3][RBN-DEF-08.1][RBN-DEF-08.2]
SEM_PERMISSAO_DOCUMENTOS = "Você não tem permissão para acessar os documentos desta defesa"
ATA_SEM_ASSINATURA_COORDENADOR = (
    "Não foi possível gerar a Ata Final: o Coordenador de Curso não possui assinatura cadastrada "
    "no perfil"
)
ERRO_AO_GERAR_DOCUMENTOS = (
    "Erro ao gerar os documentos da defesa. Tente realizar o download novamente em instantes"
)
FOLHA_NAO_SE_APLICA = "A Folha de Aprovação não se aplica ao TCC 1"
FOLHA_REPROVADO = "Documento indisponível para trabalhos reprovados"
OUVINTES_SALVOS = "Ouvintes salvos com sucesso"
MATRICULA_INVALIDA = "A matrícula deve conter exatamente 10 dígitos numéricos"
OUVINTE_REPETIDO = "Este aluno já foi registrado como ouvinte nesta defesa"
NOME_INVALIDO = "O nome deve conter apenas letras, acentos e espaços e ter até 150 caracteres"
OUVINTES_FORA_DO_STATUS = "O registro de ouvintes fica disponível apenas durante ou após a sessão"
SEM_DEFESAS_AGENDADAS = "Não existem defesas agendadas para o período selecionado"

# MX-01 a MX-09 (MX-02 removida, P4). MX-06 tem texto exato no diagrama 05
# (RegistrarOuvintesAgenda, passo 3.4); as demais são provisórias até a PO validar (Q-142).
# [US-28][US-30][RBN-DEF-07.1][RBN-DEF-08.3][RBN-DEF-08.4][RBN-DEF-08.5][RBN-CAD-13.1]
MX01_OCORRENCIAS_LONGAS = "As ocorrências devem ter até 2.000 caracteres"  # PROVISÓRIO (Q-142)
# PROVISÓRIO (Q-142)
MX03_COORDENADOR_SEM_ASSINATURA = (
    "Cadastre a imagem de assinatura no seu perfil: a Ata Final da defesa de {aluno} não pode ser "
    "gerada sem ela."
)
MX04_ASSUNTO = "SIGTCC: declaração de participação em banca"  # PROVISÓRIO (Q-142)
# PROVISÓRIO (Q-142)
MX04_CORPO = (
    "Segue em anexo a declaração da sua participação na banca da defesa de {aluno} em {data}. "
    "Código de validação: {codigo}."
)
# PROVISÓRIO (Q-142)
MX05_DECLARACAO = (
    "Declaramos que {nome}, {titulacao}, participou como {papel} da banca examinadora da defesa "
    'do Trabalho de Conclusão de Curso "{titulo}", de {aluno}, do curso de {curso}, realizada em '
    "{data}. Código de validação: {codigo}. Este código não constitui assinatura digital."
)
MX06_OCORRENCIAS_SALVAS = "Ocorrências salvas com sucesso"
# PROVISÓRIO (Q-142)
MX07_SEM_OUVINTES = "Nenhum ouvinte encontrado para o período e filtros selecionados"
# PROVISÓRIO (Q-142)
MX08_ATA_INDISPONIVEL = (
    "A Ata Final está indisponível: o Coordenador de Curso ainda não cadastrou a assinatura no "
    "perfil"
)
# PROVISÓRIO (Q-142)
MX09_CURSO_SEM_COORDENADOR = (
    "O curso {curso} não tem Coordenador de Curso cadastrado: a Ata Final da defesa de {aluno} "
    "não pode ser gerada."
)
