"""Textos exibidos ao usuário na feature 003 (Acesso e Login).

Dois grupos:
- textos das US, copiados caractere por caractere de docs/fonte/Historias_de_Usuario_v3_2.md;
- mensagens PROVISÓRIAS M-01 a M-17, com o ID no nome, copiadas da tabela "Mensagens a validar com
  a PO" de specs/003-acesso-login/spec.md. São provisórias até a validação da PO (índice Q-01;
  spec Q25): quando a PO validar, mude só a constante e a tabela da spec.

Nunca escreva estes textos soltos em views, forms ou templates: use estas constantes. O teste
test_mensagens.py confere os textos contra as US e a spec (SC-002).

[US-10][US-11][US-12][US-37][US-38][SC-002]
"""

# ---------------------------------------------------------------------------------------------
# US-10: primeiro acesso [RBN-CAD-06.1][RBN-CAD-06.2][RBN-CAD-06.3]
# ---------------------------------------------------------------------------------------------
LINK_ATIVACAO_ENVIADO = "Enviamos um link de ativação para o seu e-mail"
CONTA_ATIVADA = "Conta ativada"
DADOS_NAO_ENCONTRADOS = "Dados não encontrados. Procure o Professor da Disciplina ou a Secretaria"
CONTA_JA_ATIVA = "Esta conta já está ativa"
EMAIL_INSTITUCIONAL = "Informe o seu e-mail institucional da UEA (@uea.edu.br)"
MATRICULA_FORMATO = "A matrícula deve ter 10 dígitos numéricos"
EMAIL_DE_OUTRA_CONTA_ALUNO = (
    "Este e-mail já está vinculado a outra conta. Procure o Professor da Disciplina"
)
REGRA_SENHA = "A senha deve ter de 8 a 64 caracteres, com ao menos 1 letra e 1 número"
SENHAS_NAO_CONFEREM = "As senhas não conferem"
LINK_SUBSTITUIDO = "Link inválido. Use o link mais recente enviado ao seu e-mail"

# ---------------------------------------------------------------------------------------------
# US-11: login [RBN-CAD-06.4][RBN-CAD-06.6][RBN-CAD-03.3]
# ---------------------------------------------------------------------------------------------
CREDENCIAL_INVALIDA = "Credencial ou senha inválida"
ACESSO_EXPIRADO = (
    "Seu acesso expirou. Procure o Orientador, o Professor da Disciplina, a Secretaria ou o "
    "Coordenador de Curso"
)
CONTA_NAO_ATIVADA = "Conta ainda não ativada"
CONTA_INATIVA = "Conta inativa"
INFORME_CREDENCIAL = "Informe a credencial e a senha"

# ---------------------------------------------------------------------------------------------
# US-12: alterar e recuperar a senha [RBN-CAD-06.5][RBN-CAD-06.7][RBN-CAD-06.8]
# ---------------------------------------------------------------------------------------------
SENHA_ALTERADA = "Senha alterada com sucesso"
SENHA_ATUAL_INCORRETA = "Senha atual incorreta"
ESQUECI_GENERICA = "Se a conta existir, enviaremos um link para o e-mail cadastrado"
LINK_INVALIDO_OU_VENCIDO = "Link inválido ou vencido. Solicite um novo"

# ---------------------------------------------------------------------------------------------
# US-37: reenvio do link de ativação [RBN-CAD-06.9]
# ---------------------------------------------------------------------------------------------
LINK_ATIVACAO_VENCEU = "Este link de ativação venceu"
NOVO_LINK_ENVIADO = "Enviamos um novo link para o seu e-mail"

# ---------------------------------------------------------------------------------------------
# US-38: perfil e notificações [RBN-CAD-13.1][RBN-CAD-13.2]
# ---------------------------------------------------------------------------------------------
PERFIL_ATUALIZADO = "Perfil atualizado"
SEM_NOTIFICACOES = "Você não tem notificações"
ITEM_INDISPONIVEL = "Este item não está mais disponível"
# Curso do Aluno sem correspondência na equivalência (matriz, RBN-CAD-05.7).
CURSO_NAO_RECONHECIDO = "Código não reconhecido"

# ---------------------------------------------------------------------------------------------
# Rótulos de botões e links, como escritos nas US ("Sair" vem da spec 003, FR-011)
# ---------------------------------------------------------------------------------------------
PRIMEIRO_ACESSO = "Primeiro acesso"
ESQUECI_MINHA_SENHA = "Esqueci minha senha"
ENTRAR = "Entrar"
ENVIAR = "Enviar"
ATIVAR_CONTA = "Ativar conta"
REENVIAR_LINK = "Reenviar link de ativação"
SALVAR = "Salvar"
ALTERAR_SENHA = "Alterar senha"
RESETAR_PRIMEIRO_ACESSO = "Resetar primeiro acesso"
MARCAR_COMO_LIDAS = "Marcar como lidas"
MEU_PERFIL = "Meu perfil"
SAIR = "Sair"
CONFIRMAR_NOVO_EMAIL = "Confirmar novo e-mail"

# ---------------------------------------------------------------------------------------------
# Mensagens PROVISÓRIAS (spec, "Mensagens a validar com a PO"; índice Q-01)
# ---------------------------------------------------------------------------------------------
# {minutos} é o "N" da spec: minutos restantes arredondados para cima, no mínimo 1 (Q16).
M01_BLOQUEIO = (
    "Acesso bloqueado por 15 minutos após 3 tentativas incorretas. "
    "Tente novamente em {minutos} minutos."
)
M02_ACESSO_NEGADO = "Você não tem permissão para acessar esta página."
M03_ORIENTACAO_CONTA_ATIVA = (
    'Use "Esqueci minha senha" ou, se o e-mail estiver errado, procure o Professor da Disciplina.'
)
M04_ASSINATURA_FORMATO = "Envie uma imagem PNG ou JPG com até 2 MB."
M05_EMAIL_EM_USO = "Este e-mail já está vinculado a outra conta."
M06_CONFIRMACAO_EMAIL_ENVIADA = "Enviamos um link de confirmação para o novo e-mail."
M07_EMAIL_ATUALIZADO = "E-mail atualizado."
M08_REFAZER_PRIMEIRO_ACESSO = "Refaça o primeiro acesso para receber um novo link."
M09_LINK_EMAIL_INVALIDO = LINK_INVALIDO_OU_VENCIDO
M10_EMAIL_INVALIDO = "Informe um e-mail válido."
M11_EMAIL_INSTITUCIONAL = EMAIL_INSTITUCIONAL
# {nome} é o NOME do aluno na spec.
M12_CONFIRMAR_RESET = (
    "Resetar o primeiro acesso de {nome}? O e-mail e a senha vinculados serão apagados e o aluno "
    "deverá refazer o primeiro acesso."
)
M13_RESET_CONCLUIDO = "Primeiro acesso resetado. O aluno já pode refazer o primeiro acesso."
M14_CAMPO_OBRIGATORIO = "Preencha este campo."
M15_CONTA_INATIVA = CONTA_INATIVA
M16_ACESSO_EXPIRADO = ACESSO_EXPIRADO
M17_FALHA_ENVIO = "Não foi possível enviar o e-mail agora. Tente novamente em alguns minutos."

# =============================================================================================
# Spec 004: Turmas e Alunos (US-07, US-08, US-09)
# =============================================================================================

# US-07 [RBN-CAD-04.1 a 04.5]
TURMA_CADASTRADA = "Turma cadastrada com sucesso"
HORARIO_TERMINO = "O horário de término deve ser posterior ao de início"
TURMA_COM_ALUNOS = "A turma possui alunos matriculados. Use a opção Arquivar"
ARQUIVAR_TCC_ATIVO = "Há TCC Em Andamento ou Apto para Defesa"
ARQUIVAR_SESSAO_ATIVA = "Há sessão de defesa ativa"
ARQUIVAR_VERSAO_FINAL = "A Data Limite da Versão Final ainda não venceu ou não foi cadastrada"

# US-08 [RBN-CAD-05.1 a 05.7] (MATRICULA_FORMATO e CURSO_NAO_RECONHECIDO já existem acima)
ALUNO_MATRICULADO = "Aluno matriculado com sucesso"
ALUNO_JA_NA_TURMA = "Aluno já matriculado nesta turma"
ARQUIVO_FORA_DO_MODELO = "Arquivo fora do modelo. Baixe o modelo de importação"

# US-09 [RBN-CAD-05.4, 08.4]
ALUNO_EXCLUIDO = "Aluno excluído da turma"
JUSTIFICATIVA_500 = "Informe uma justificativa de até 500 caracteres"
SELECIONE_STATUS = "Selecione o Status do aluno"
ALUNO_TEM_PROPOSTA = "O aluno já tem Proposta. Use Encerrar participação"

# Rótulos de botões e opções, como escritos nas US-07, 08 e 09
NOVA_TURMA = "Nova turma"
EDITAR = "Editar"
EXCLUIR = "Excluir"
ARQUIVAR = "Arquivar"
MATRICULAR_ALUNOS = "Matricular alunos"
MATRICULA_INDIVIDUAL = "Matrícula individual"
IMPORTAR_ARQUIVO = "Importar arquivo (CSV/XLSX)"
CONFIRMAR_IMPORTACAO = "Confirmar importação"
TRANSFERIR = "Transferir"
EXCLUIR_DA_TURMA = "Excluir da turma"
ENCERRAR_PARTICIPACAO = "Encerrar participação"
CONFIRMAR = "Confirmar"

# Mensagens PROVISÓRIAS da spec 004 (tabela "Mensagens a validar com a PO"; índice Q-36).
# Os campos em maiúsculas da spec viram {identificador}, {nome}, {status} etc. A MT-20 é reservada.
MT01_CODIGO_DISCIPLINA = (
    "Use só letras maiúsculas e números, sem espaços, com até 20 caracteres (ex.: ESTCMP025)."
)
MT02_IDENTIFICADOR_FORMATO = (
    "Use só letras maiúsculas, números e _, sem espaços, com até 30 caracteres (ex.: ECP06_T01)."
)
MT03_IDENTIFICADOR_REPETIDO = "Já existe uma turma com este Identificador."
MT04_ANO = "Informe o ano com 4 dígitos (ex.: 2026)."
MT05_LOCAL = "O Local deve ter até 100 caracteres."
MT06_TURMA_ATUALIZADA = "Turma atualizada com sucesso."
MT07_CONFIRMAR_EXCLUSAO_TURMA = "Excluir a turma {identificador}? Esta ação não pode ser desfeita."
MT08_TURMA_EXCLUIDA = "Turma excluída."
MT09_CONFIRMAR_ARQUIVAMENTO = (
    "Arquivar a turma {identificador}? Ela ficará disponível só para consulta."
)
MT10_TURMA_ARQUIVADA = "Turma arquivada."
MT11_NOME_COMPLETO = (
    "Informe o Nome Completo só com letras, acentos e espaços, com até 150 caracteres."
)
MT12_CURSO = (
    "Informe o código de curso da UEA, com letras maiúsculas e números, até 20 caracteres "
    "(ex.: EST08MCPD)."
)
MT13_CURSO_DIVERGENTE = (
    "O curso do aluno ({curso_aluno}) é diferente do curso da turma ({curso_turma})."
)
MT14_ALUNO_ATUALIZADO = "Dados do aluno atualizados."
MT15_RESUMO_IMPORTACAO = (
    "Importação concluída: {n} alunos matriculados, {r} linhas rejeitadas e {c} códigos de curso "
    "não reconhecidos."
)
MT16_TRANSFERIDO = "Aluno transferido para a turma {identificador}."
MT17_TRANSFERENCIA_STATUS = (
    "Só é possível transferir aluno com TCC Em Andamento ou Apto para Defesa."
)
MT18_TRANSFERENCIA_SESSAO = "Não é possível transferir: há sessão de defesa ativa."
MT19_SEM_DESTINO = "Não há turma de TCC 2 de outro orientador no mesmo curso e período."
MT21_NOTIFICACAO_EXCLUSAO = "Você foi excluído da turma {identificador}. Motivo: {justificativa}"
MT22_NOTIFICACAO_TRANSFERENCIA = "{nome} foi transferido da turma {origem} para a turma {destino}."
MT23_PARTICIPACAO_ENCERRADA = "Participação encerrada como {status}."
MT24_CONFIRMAR_EXCLUSAO_ALUNO = "Excluir {nome} da turma? O aluno perderá o acesso a ela."
MT25_TURMA_ARQUIVADA = "Esta turma está arquivada e só pode ser consultada."
MT26_TCC_EM_CURSO = "O aluno já tem TCC em andamento na turma {identificador}. Use Transferir."
MT27_TCC_CONCLUIDO = "O TCC deste aluno já foi aprovado ou concluído."
MT28_APROVADO_EM_TURMA_TCC1 = "O aluno foi aprovado em TCC 1. Matricule-o numa turma de TCC 2."
MT29_CONTA_NAO_ATIVA = (
    "A conta deste aluno está {status}: ele não consegue entrar até a conta ser reativada pela "
    "Gestão de Contas."
)
MT30_ENCERRAMENTO_SESSAO = "Não é possível encerrar a participação: há sessão de defesa ativa."
MT32_PREVIA_INVALIDA = (
    "A prévia da importação venceu ou não é desta turma. Envie o arquivo de novo."
)
MT31_PEDIDO_CANCELADO = (
    "O pedido de {tipo} para o TCC de {nome} foi cancelado porque a participação do aluno foi "
    "encerrada."
)

# =============================================================================================
# Spec 005: Fluxo do TCC e Entregas (US-13, US-14, US-15, US-16, US-29, US-43, US-44)
# =============================================================================================

# US-13 [RBN-CAD-07.1][RBN-CAD-08.1][RBN-CAD-08.2]
PROPOSTA_SALVA = "Proposta salva"
ALTERACOES_SALVAS = "Alterações salvas"
INFORME_PALAVRAS_CHAVE = "Informe de 1 a 5 Palavras-Chave"
# Confirmado na análise /speckit-analyze: não existe constante equivalente em mensagens.py antes
# desta spec (research/tasks T001); reaproveitar M14_CAMPO_OBRIGATORIO (campo obrigatório, E2) e
# JUSTIFICATIVA_500 (mensagem de limite de caracteres análoga) sem duplicar.
LINK_HTTPS_500 = "O link deve começar com https:// e ter até 500 caracteres"

# US-43 [RBN-CAD-09.1][RBN-CAD-09.6]
ENTREGA_CADASTRADA = "Entrega cadastrada"
ENTREGA_TIPO_REPETIDO = "A turma já tem uma entrega deste tipo"
NENHUMA_ENTREGA_CADASTRADA = "Nenhuma entrega cadastrada"

# US-15 [RBN-CAD-09.2][RBN-CAD-09.3][RBN-CAD-09.6]
ENTREGA_ENVIADA = "Entrega enviada"
ENTREGA_CUMPRIDA_PROPOSTA = "Esta entrega é cumprida ao salvar a Proposta"

# US-29 [RBN-CAD-09.2][RBN-CAD-09.3]
VERSAO_FINAL_ENVIADA = "Versão Final enviada"

# US-44 [RBN-CAD-09.3][RBN-CAD-09.5]
VERSAO_FINAL_HOMOLOGADA = "Versão Final homologada"

# Mensagens PROVISÓRIAS da spec 005 (tabela "Mensagens a validar com a PO" do spec.md).
MF01_DATA_LIMITE_VENCIDA = "Data Limite vencida: o envio será registrado como Entregue com Atraso."
MF02_VERSAO_FINAL_DEVOLVIDA = "Versão Final devolvida para ajuste."
MF03_PALAVRA_CHAVE_REPETIDA = "Palavra-chave repetida."
