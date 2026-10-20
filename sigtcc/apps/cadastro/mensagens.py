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

# ---------------------------------------------------------------------------------------------
# Rótulos de botões e links, como escritos nas US
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
