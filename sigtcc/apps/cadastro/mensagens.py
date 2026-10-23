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
# M-02 e M-14 passaram aos textos das US-03, 04, 05 e 50 (spec 003, Q30; spec 002, Q9; índice Q-50).
M02_ACESSO_NEGADO = "Você não tem permissão para esta ação"
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
M14_CAMPO_OBRIGATORIO = "Campo obrigatório"
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
# US-29, E3/Cenário 9: seção Versão final antes da liberação do resultado (texto exato da US).
VERSAO_FINAL_DISPONIVEL_APOS_RESULTADO = "Disponível após a liberação do resultado"

# US-44 [RBN-CAD-09.3][RBN-CAD-09.5]
VERSAO_FINAL_HOMOLOGADA = "Versão Final homologada"

# Mensagens PROVISÓRIAS da spec 005 (tabela "Mensagens a validar com a PO" do spec.md).
MF01_DATA_LIMITE_VENCIDA = "Data Limite vencida: o envio será registrado como Entregue com Atraso."
MF02_VERSAO_FINAL_DEVOLVIDA = "Versão Final devolvida para ajuste."
MF03_PALAVRA_CHAVE_REPETIDA = "Palavra-chave repetida."
# Notificação ao Orientador na mudança de tema (US-13, fluxo alternativo A): a US diz só "envia
# uma notificação ao Orientador", sem citar o texto exato — mensagem nova, registrada como
# PROVISÓRIA (Q-83) no mesmo padrão de MT21/MT22 (spec 004).
MF04_NOTIFICACAO_MUDANCA_TEMA = "{nome} alterou os dados do TCC na turma {identificador}."
# Notificação a cada aluno da turma ao cadastrar uma entrega (US-43, passo 7): a US pede "uma
# notificação no sistema e um e-mail com o Título e a Data Limite", sem citar o texto exato —
# mensagem nova, registrada como PROVISÓRIA (Q-84), no mesmo padrão da MF-04.
MF05_NOTIFICACAO_ENTREGA_CADASTRADA = (
    "Nova entrega cadastrada na turma {identificador}: {titulo}, com prazo até {data_limite}."
)
# Data Limite anterior à data do cadastro (US-43, E2, Cenário 8): a US só diz "destaca a Data
# Limite", sem citar o texto exato — mensagem nova, registrada como PROVISÓRIA (Q-84).
MF06_DATA_LIMITE_ANTERIOR_A_HOJE = "A Data Limite não pode ser anterior a hoje."
# Notificação ao Professor da Disciplina a cada envio ou substituição de link (US-15, passo 6 e
# fluxo alternativo D): a US diz só "envia... uma notificação no sistema com o envio" e "notifica
# o Professor da Disciplina no sistema", sem citar o texto exato — mensagem nova, registrada como
# PROVISÓRIA (Q-85), no mesmo padrão da MF-04/MF-05.
MF07_NOTIFICACAO_ENVIO_ENTREGA = "{nome} enviou a entrega {titulo} na turma {identificador}."
# Lembrete de prazo ao aluno que ainda não enviou, 7 dias, 48h e 24h antes da Data Limite (US-15,
# fluxo alternativo E): a US diz só "envia notificação no sistema e e-mail", sem citar o texto
# exato — mensagem nova, registrada como PROVISÓRIA (Q-86), no mesmo padrão da MF-05/MF-07.
MF08_LEMBRETE_PRAZO_ENTREGA = (
    "Lembrete: a entrega {titulo} da turma {identificador} vence em {data_limite}."
)
# Notificação à Secretaria na homologação da Versão Final (US-44, passo 6: "notifica a
# Secretaria para concluir os trâmites acadêmicos") e ao Aluno na devolução para ajuste (fluxo
# alternativo D: "notifica o Aluno") — a US não cita o texto exato de nenhuma das duas; mensagens
# novas, registradas como PROVISÓRIAS (Q-88), no mesmo padrão da MF-05/MF-07.
MF09_NOTIFICACAO_VERSAO_FINAL_HOMOLOGADA = (
    "Versão Final de {nome} homologada na turma {identificador}: TCC concluído."
)
MF10_NOTIFICACAO_VERSAO_FINAL_DEVOLVIDA = (
    "Versão Final devolvida para ajuste na turma {identificador}: {mensagem}"
)
# Assuntos dos e-mails da spec 005 (US-43, passo 7, e US-15, fluxo alternativo E: "e-mail com o
# Título e a Data Limite"; FR-015, FR-022), sem texto exato nas US — PROVISÓRIOS (Q-84, Q-86). O
# corpo repete a notificação (MF-05 e MF-08).
MF11_ASSUNTO_NOVA_ENTREGA = "SIGTCC: nova entrega"
MF12_ASSUNTO_LEMBRETE_PRAZO = "SIGTCC: lembrete de prazo"

# =============================================================================================
# Spec 002: Gestão de Contas (US-03, US-04, US-05, US-06, US-50)
# Textos das US copiados de docs/fonte/Historias_de_Usuario_v3_3.md; MC-01 a MC-13 da tabela
# "Mensagens a validar com a PO" de specs/002-gestao-contas/spec.md. [SC-002][FR-048]
# =============================================================================================

# US-03 e US-05: cadastro e alteração [RBN-CAD-01.1][RBN-CAD-01.2][RBN-CAD-02.1][RBN-CAD-02.2]
# [RBN-CAD-03.1][RBN-CAD-03.2]. MC-08 = DOCENTE_CADASTRADO (cenário 1 da US-03; spec Q6).
DOCENTE_CADASTRADO = "Docente cadastrado com sucesso"
SECRETARIA_CADASTRADA = "Secretaria cadastrada com sucesso"
MEMBRO_CADASTRADO = "Membro externo cadastrado com sucesso"
DADOS_ATUALIZADOS = "Dados atualizados"
EMAIL_JA_CADASTRADO = "Este e-mail já está cadastrado"
EMAIL_INSTITUCIONAL_CONTAS = "Informe um e-mail institucional (@uea.edu.br)"
EMAIL_VALIDO = "Informe um e-mail válido"
NOME_INVALIDO = "O nome deve conter apenas letras e até 150 caracteres"
OPCAO_INVALIDA = "Selecione uma opção válida"
INSTITUICAO_INVALIDA = "Informe a instituição com até 150 caracteres"
CURSO_JA_TEM_COORDENADOR = (
    "O curso já possui Coordenador. Desmarque o papel no coordenador atual para continuar"
)
CURSO_JA_TEM_SECRETARIA = "O curso já possui Secretaria vinculada"
SO_DO_SEU_CURSO_CADASTRO = "Você só pode cadastrar e alterar dados do seu curso"
SO_DO_SEU_CURSO_ALTERACAO = "Você só pode alterar dados do seu curso"
NENHUM_REGISTRO = "Nenhum registro"
FALHA_AO_SALVAR = "Não foi possível salvar. Tente novamente"

# US-04: inativação [RBN-CAD-01.3][RBN-CAD-02.3]. {nome}, {motivos} e {n} são NOME, MOTIVOS e N.
CONFIRMAR_INATIVAR_DOCENTE = "Deseja inativar o docente {nome}?"
DOCENTE_INATIVADO = "Docente inativado"
NAO_E_POSSIVEL_INATIVAR = "Não é possível inativar: o docente {motivos}"
# Motivo (a), sempre no plural, mesmo com N = 1 (US-04 E1; spec Q18).
MOTIVO_TCC_ATIVO = "possui {n} orientandos ou coorientandos com TCC ativo"
MOTIVO_COORDENADOR = "é Coordenador do curso"
# Fecho do alerta com mais de um motivo (US-04 E6; FR-027).
FIM_ALERTA_VINCULOS = ". Encerre ou transfira esses vínculos primeiro"

# US-50: prorrogação [RBN-CAD-03.3]. {data} no formato DD/MM/AAAA.
ACESSO_PRORROGADO_ATE = "Acesso prorrogado até {data}"
FALHA_AO_PRORROGAR = "Não foi possível prorrogar o acesso. Tente novamente"

# US-06: PROVISÓRIA até a Q-52 (troca da M-16 pela spec 003). Só o teste do cenário 3 da US-06 a
# usa; com a resposta da Julia, a M-16 recebe este texto e a constante sai (research C16).
ACESSO_EXPIRADO_US06 = "Seu acesso expirou. Procure a coordenação do curso"

# Rótulos das US-03 a 06 e 50 (critério dos cenários, spec Q21). SALVAR e EDITAR já existem.
CADASTRAR_DOCENTE = "Cadastrar Docente"
NOVA_SECRETARIA = "Nova secretaria"
NOVO_MEMBRO_EXTERNO = "Novo membro externo"
INATIVAR = "Inativar"
REATIVAR = "Reativar"
PRORROGAR = "Prorrogar"
CANCELAR = "Cancelar"
COORDENADOR_DE_CURSO = "Coordenador de Curso"
SUA_SENHA = "Sua senha"

# MC-01 a MC-10: definidas em 2026-10-22 (spec Q14; índice Q-46). [US-04][US-50]
MC01_CONFIRMAR_REATIVAR = "Deseja reativar o docente {nome}?"
MC02_DOCENTE_REATIVADO = "Docente reativado"
MC03_CONFIRMAR_INATIVAR_SECRETARIA = "Deseja inativar a Secretaria {nome}?"
MC04_SECRETARIA_INATIVADA = "Secretaria inativada"
# Motivos (b) a (d): plural com {n} e singular com N = 1 (spec Q14).
MC05_CONVITES = "possui {n} convites de coorientação sem resposta"
MC05_CONVITE_1 = "possui 1 convite de coorientação sem resposta"
MC06_BANCAS = "participa de {n} bancas Agendadas, Reagendadas ou Em Andamento"
MC06_BANCA_1 = "participa de 1 banca Agendada, Reagendada ou Em Andamento"
MC07_TURMAS = "é Professor da Disciplina de {n} turmas não arquivadas"
MC07_TURMA_1 = "é Professor da Disciplina de 1 turma não arquivada"
MC09_SEM_VALIDADE = "Este membro ainda não ativou a conta e não tem validade para prorrogar"
MC10_STATUS_INCOMPATIVEL = "Esta ação não está disponível para o Status da Conta atual"

# MC-11 a MC-13: PROVISÓRIAS (spec Q17 e Q24; índice Q-58). [US-03][US-05][FR-008]
MC11_SENHA_INCORRETA = "Senha incorreta"
MC12_TROCA_EMAIL_ENVIADA = "Dados atualizados. Enviamos um link de confirmação para o novo e-mail"
MC13_FALHA_ENVIO_TROCA = (
    "Dados atualizados, mas não foi possível enviar o link de confirmação. Altere o e-mail "
    "novamente em alguns minutos"
)
