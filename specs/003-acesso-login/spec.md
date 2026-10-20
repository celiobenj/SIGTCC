# Feature Specification: Acesso e Login do SIGTCC

**Feature Branch**: `feature/feat-02-turmas` (indicada pela responsável; ver Assumptions)

**Created**: 2026-10-19

**Status**: Draft

**Input**: User description: "Use o número 003 para esta spec (002 está reservado para a Gestão de
Contas da Maria Luísa). Acesso e Login do SIGTCC: US-10, US-11, US-12, US-37 e US-38. Use as seções
dessas US em docs/fonte/Historias_de_Usuario_v3_2.md, com regras (RBN), fluxos alternativos,
mensagens exatas e cenários de aceite; IDs da matriz de 17/10. O modelo de dados já existe (spec
001); não crie tabelas. Esta spec também entrega, para as outras features reaproveitarem: a base
visual (base.html, includes, CSS) seguindo o protótipo em docs/fonte/prototipo/; a verificação de
perfil (cada perfil só acessa as funções do seu papel); a função que gera e valida o link de
primeiro acesso (a Gestão de Contas, US-03 a 06, só chama essa função ao criar a conta). A criação
das contas e das contas iniciais de Coordenador é da US-03 (spec 002); aqui só consuma contas
existentes. Para teste manual, preveja um modo de criar uma conta pelo shell, documentado no
quickstart. Não crie nem troque de branch: use a feature/feat-02-turmas."

**Responsável**: Julia Cohen (responsável pelas US-10, US-11, US-12, US-37 e US-38 no documento de
US).

**Fontes**: `docs/fonte/Historias_de_Usuario_v3_2.md` (US-10, US-11, US-12, US-37, US-38);
`docs/fonte/Matriz_Requisitos_17_10.md` (RAN-CAD-06, RAN-CAD-13; RBN-CAD-06.1 a 06.9, 13.1, 13.2 e
03.3; Glossario_Status); `docs/fonte/Modelo_Logico_e_Dicionario_18_10.md` (tabelas existentes e
seção 4, itens 1 a 3); `docs/fonte/prototipo/prototipo_17_10.html` (só o visual);
`specs/001-modelo-dados/` (modelo de dados e decisões D1 e D2).

**Rastreabilidade**: [US-10][RBN-CAD-06.1][RBN-CAD-06.2][RBN-CAD-06.3] ·
[US-11][RBN-CAD-06.4][RBN-CAD-06.6][RBN-CAD-03.3] · [US-12][RBN-CAD-06.5][RBN-CAD-06.7][RBN-CAD-06.8]
· [US-37][RBN-CAD-06.9] · [US-38][RBN-CAD-13.1][RBN-CAD-13.2]. RNF: RAN-CAD-06 (senhas criptografadas
e nunca exibidas; login só para conta Ativa; direcionamento ao painel do perfil) e RAN-CAD-13 (cada
usuário vê e edita só os campos do seu papel; troca de e-mail confirmada por link).

## Clarifications

### Session 2026-10-19

- Q1: O link de ativação é enviado automaticamente quando a conta é criada (como dizia a descrição
  da feature)? → A: Não. Seguem as US-03, US-05, US-08 e US-10 e a matriz (RBN-CAD-06.1 e 06.2): a
  conta nasce 'Aguardando Ativação' e o link só sai quando o próprio usuário pede o "Primeiro
  acesso" ou o reenvio (US-37). A Gestão de Contas (spec 002) cria a conta e não chama a geração do
  link; as funções de link ficam disponíveis para reuso, sem envio na criação.
- Q2: Aluno com e-mail já registrado num pedido anterior, ainda não ativado, pede o primeiro acesso
  com outro e-mail. O que acontece? → A: O sistema ignora o e-mail novo e reenvia o link ao e-mail
  já registrado (US-10, fluxo alternativo 2: "envia ao mesmo e-mail"). Assim, quem só conhece a
  matrícula não consegue desviar a ativação. Se o e-mail registrado estiver errado, o caminho é o
  "Resetar primeiro acesso" do Professor da Disciplina (US-12, RBN-CAD-06.8).
- Q3: Onde fica o botão "Resetar primeiro acesso" (RBN-CAD-06.8), já que a US-12 o coloca no painel
  do aluno da US-41, que ainda não existe? → A: Esta feature entrega a ação de reset e uma tela
  mínima com os dados do aluno e o botão, acessível só ao Professor da Disciplina da turma do aluno.
  **Pendência**: a US-41 (Feature 6, Leandra Matos) deve incorporar o botão ao painel do aluno quando
  for implementada, reaproveitando a ação de reset desta feature.

### Session 2026-10-19 (conferência do analista de requisitos)

- Q4: Membro Externo com `mem_validade_ate` vencida e o status ainda 'Ativa' consegue entrar? → A: Não.
  Pela matriz (RBN-CAD-03.3: "Expirada: passado esse prazo. O login fica bloqueado"), o login também
  confere a validade: com a data de hoje depois de `mem_validade_ate`, o acesso é negado com a mensagem
  de expiração da US-11, mesmo que a rotina da US-06 ainda não tenha mudado o status. Validade nula
  (sem banca) não bloqueia.
- Q5: Que tela aparece para um link de ativação de conta resetada (sem e-mail)? → A: A tela de link
  vencido, com "Este link de ativação venceu" e o botão "Reenviar link de ativação"; o clique não
  reenvia e mostra a orientação M-08 (US-37, cenário 5). Ordem de avaliação de um link de ativação:
  (1) conta já ativa; (2) conta sem e-mail; (3) link substituído por outro mais recente; (4) link
  vencido; (5) link válido.
- Q6: Primeiro acesso de conta 'Inativa' ou 'Expirada'? → A: Nenhum link é enviado e aparece a mesma
  mensagem do login para o status ("Conta inativa" ou "Seu acesso expirou. Procure o Orientador, o
  Professor da Disciplina, a Secretaria ou o Coordenador de Curso"), registrada como PROVISÓRIA nesse
  novo contexto (M-15 e M-16).
- Q7: Painel do Coordenador de Curso? → A: Painel único do Docente; os itens do Coordenador de Curso
  (e dos demais papéis) aparecem como itens extras no menu do Docente, como no protótipo.
- Q8: Escolha de perfil no primeiro acesso? → A: Só duas escolhas, como na matriz (RBN-CAD-06.1 e 06.2):
  "Aluno" (Matrícula e E-mail Institucional) e "Docente, Secretaria ou Membro Externo" (E-mail). O
  e-mail deste segundo formulário é aceito se for de qualquer um dos três tipos de conta.
- Q9: Quem pode resetar o primeiro acesso, e o que os demais veem? → A: O Professor da Disciplina de
  qualquer turma não arquivada do aluno. Para os demais Professores da Disciplina, a tela do aluno
  abre sem o botão "Resetar primeiro acesso"; a ação de reset também recusa quem não tem permissão.
- Q10: Como detectar a notificação de item indisponível? → A: Nesta feature, só o item removido: se o
  endereço da notificação não leva a uma página existente, a central marca a notificação como lida e
  exibe "Este item não está mais disponível". O caso "cancelado" (US-38, cenário 9, convite de banca)
  é **pendência para a feature de Defesa**, que deve tratar o item cancelado na sua tela de destino.
- Q11: Validade, "substituído" e mensagem da troca de e-mail? → A: O link de confirmação vale 24 horas,
  a mesma validade que a matriz define para o link de primeiro acesso (RBN-CAD-06.1 e 06.9). Se um link
  de troca deixa de valer quando outro é gerado ("substituído") é decisão do plano. Ao salvar uma
  alteração que inclui troca de e-mail, aparece só a M-06 (sem "Perfil atualizado").
- Q12: Ordem das validações? → A: No primeiro acesso, aparece só o erro do primeiro campo do formulário
  com problema, na ordem dos campos (no Aluno, Matrícula antes de E-mail Institucional); dentro de um
  campo, formato antes de existência, e existência antes de status. No login: campo vazio; conta não
  encontrada; conta 'Aguardando Ativação' (sem conferir senha); bloqueio vigente; senha; e só com a
  senha correta o status 'Inativa' ou 'Expirada' (inclusive pela validade, Q4).
- Q13 (padrão sugerido): e-mails são comparados sem diferenciar maiúsculas de minúsculas na busca da
  credencial e na verificação de unicidade. Falha no envio de e-mail: em "Esqueci minha senha" a
  mensagem genérica se mantém (não revela contas); no primeiro acesso, no reenvio e na troca de e-mail
  aparece a M-17 e o link não é considerado enviado.
- Q14 (padrão sugerido): a central de notificações lista todas as notificações, da mais recente para a
  mais antiga, 20 por página. A US-38 fala em "título", mas a matriz (RBN-CAD-13.2) não exige título e
  o dicionário não tem essa coluna: a central mostra o texto da notificação, a data e a hora.
- Q15 (padrão sugerido): no Aluno que já tem e-mail registrado (Q2), o e-mail informado ainda passa pela
  validação de formato e de domínio do campo, mas não pela de unicidade, porque é ignorado; a mensagem
  de sucesso é a mesma ("Enviamos um link de ativação para o seu e-mail").
- Q16 (padrão sugerido): SC-003 é medido em teste manual cronometrado, sem contar a entrega do e-mail;
  SC-007 é verificado por um checklist de revisão visual; o "N" da M-01 é o número de minutos
  restantes arredondado para cima (no mínimo 1).
- Q17 (padrão sugerido): na regra de senha, "letra" é A–Z, maiúscula ou minúscula, como na matriz
  (RBN-CAD-06.3); letras acentuadas e outros caracteres são aceitos, mas não contam como a letra
  exigida. No login, uma senha fora de 8 a 64 caracteres é tratada como senha incorreta ("Credencial
  ou senha inválida") e conta como tentativa.

## User Scenarios & Testing *(mandatory)*

Os cenários abaixo reproduzem os cenários de aceite das US, com as mensagens exatas entre aspas. As
histórias 1 a 5 correspondem a uma US cada; a história 6 cobre o que esta feature entrega para as
demais (base visual, verificação de perfil e geração de links). As prioridades P1 a P3 indicam só a
ordem de entrega: as cinco US são Must Have na matriz e no documento de US.

### User Story 1 - Criar a senha no primeiro acesso [US-10] (Priority: P1)

Aluno, Docente, Secretaria ou Membro Externo com a conta 'Aguardando Ativação' informa os seus dados
em "Primeiro acesso", recebe por e-mail um link válido por 24 horas e cria a senha, ativando a conta.

**Why this priority**: sem a ativação, nenhuma conta criada pelas US-03, US-05 e US-08 consegue
entrar no sistema.

**Independent Test**: com uma conta 'Aguardando Ativação' criada pelo shell, pedir o primeiro
acesso, abrir o link recebido e criar a senha; a conta passa a 'Ativa'.

**Acceptance Scenarios** (US-10, cenários 1 a 11):

1. **Dado que** o aluno foi matriculado e a conta está com o Status "Aguardando Ativação", **Quando**
   informa a matrícula e o e-mail institucional, abre o link recebido e define uma senha válida,
   **Então** o sistema muda o Status da Conta para Ativa **E** direciona o aluno para a tela de
   login com a mensagem "Conta ativada".
2. **Dado que** o docente foi cadastrado com o seu e-mail, **Quando** informa esse e-mail em
   "Primeiro acesso", **Então** o sistema envia ao e-mail um link de ativação válido por 24 horas
   (e exibe "Enviamos um link de ativação para o seu e-mail" – acréscimo da spec, vindo do passo 5 da
   US-10).
3. **Dado que** o link foi gerado há mais de 24 horas e não foi usado, **Quando** o usuário abre o
   link, **Então** o sistema não exibe o formulário de senha **E** exibe o aviso "Este link de
   ativação venceu" e o botão "Reenviar link de ativação" (a US-10 diz só "um aviso"; o texto vem da
   US-37, fluxo principal, passo 2).
4. **Dado que** o usuário está no formulário de ativação, **Quando** informa a senha "abcdefgh", sem
   número, e clica em "Ativar conta", **Então** o sistema exibe "A senha deve ter de 8 a 64
   caracteres, com ao menos 1 letra e 1 número" e não ativa a conta.
5. **Dado que** o usuário está no formulário de ativação, **Quando** informa uma Confirmação de Senha
   diferente da Senha, **Então** o sistema exibe "As senhas não conferem" e não ativa a conta.
6. **Dado que** não existe aluno com a matrícula 2026000999, **Quando** o usuário informa essa
   matrícula e um e-mail institucional em "Primeiro acesso", **Então** o sistema exibe "Dados não
   encontrados. Procure o Professor da Disciplina ou a Secretaria" e não envia o link.
7. **Dado que** a conta do aluno está com o Status Ativa, **Quando** ele informa a matrícula e o
   e-mail em "Primeiro acesso", **Então** o sistema exibe "Esta conta já está ativa" **E** orienta a
   usar "Esqueci minha senha" ou procurar o Professor da Disciplina.
8. **Dado que** o aluno está no formulário de primeiro acesso, **Quando** informa o e-mail
   "aluno@gmail.com" e clica em "Enviar", **Então** o sistema exibe "Informe o seu e-mail
   institucional da UEA (@uea.edu.br)" e não envia o link.
9. **Dado que** o e-mail "ana.eng24@uea.edu.br" já está vinculado à conta de outro aluno, **Quando**
   um aluno informa a sua matrícula e esse e-mail em "Primeiro acesso", **Então** o sistema exibe
   "Este e-mail já está vinculado a outra conta. Procure o Professor da Disciplina" e não envia o
   link.
10. **Dado que** o aluno está no formulário de primeiro acesso, **Quando** informa a matrícula
    "20260001", com 8 dígitos, e clica em "Enviar", **Então** o sistema exibe "A matrícula deve ter
    10 dígitos numéricos" e não envia o link.
11. **Dado que** o aluno pediu o primeiro acesso e recebeu um link que ainda não usou, **Quando** pede
    o primeiro acesso de novo e depois abre o link anterior, **Então** o sistema exibe "Link
    inválido. Use o link mais recente enviado ao seu e-mail" **E** apenas o novo link permite ativar
    a conta.

---

### User Story 2 - Fazer login e sair [US-11] (Priority: P1)

Usuário com conta 'Ativa' entra com a credencial (matrícula ou e-mail institucional para o Aluno;
e-mail para os demais) e a senha, e é levado ao painel do seu perfil. Três senhas incorretas seguidas
bloqueiam a conta por 15 minutos.

**Why this priority**: é a porta de entrada de todas as outras features.

**Independent Test**: com uma conta ativa criada pelo shell, entrar com a credencial e a senha e ver
o painel do perfil; errar a senha três vezes e confirmar o bloqueio.

**Acceptance Scenarios** (US-11, cenários 1 a 12, mais a saída):

1. **Dado que** o aluno tem conta ativa, **Quando** informa a matrícula e a senha correta e clica em
   "Entrar", **Então** o sistema abre a sessão e exibe o painel do Aluno.
2. **Dado que** o aluno tem conta ativa com o e-mail institucional vinculado, **Quando** informa o
   e-mail institucional e a senha correta e clica em "Entrar", **Então** o sistema abre a sessão e
   exibe o painel do Aluno.
3. **Dado que** o docente tem conta ativa, **Quando** informa o e-mail e a senha correta e clica em
   "Entrar", **Então** o sistema abre a sessão e exibe o painel do Docente.
4. **Dado que** o usuário não tem tentativas incorretas registradas, **Quando** informa a credencial
   correta e uma senha errada, **Então** o sistema exibe "Credencial ou senha inválida" **E**
   registra uma tentativa incorreta.
5. **Dado que** o usuário já errou a senha 2 vezes seguidas, **Quando** erra a senha pela terceira
   vez, **Então** o sistema bloqueia o acesso por 15 minutos e mostra o tempo restante **E** recusa
   novas tentativas até o fim do prazo, mesmo com a senha correta.
6. **Dado que** o aluno errou a senha 2 vezes usando a matrícula, **Quando** erra a senha pela
   terceira vez usando o e-mail institucional, **Então** o sistema bloqueia a conta por 15 minutos
   **E** recusa o login tanto pela matrícula quanto pelo e-mail até o fim do prazo.
7. **Dado que** o usuário errou a senha 2 vezes seguidas, **Quando** informa a senha correta na
   terceira tentativa, **Então** o sistema abre a sessão e zera o contador de tentativas incorretas
   **E** um novo erro depois disso conta como a primeira tentativa.
8. **Dado que** a conta do Membro Externo está com o Status Expirada, **Quando** ele informa e-mail e
   senha corretos, **Então** o sistema nega o acesso e exibe "Seu acesso expirou. Procure o
   Orientador, o Professor da Disciplina, a Secretaria ou o Coordenador de Curso".
9. **Dado que** a conta do Membro Externo voltou para o Status Ativa depois de uma nova banca (US-06),
   **Quando** ele informa e-mail e a mesma senha de antes, **Então** o sistema abre a sessão e exibe
   o painel do Membro Externo.
10. **Dado que** o aluno foi matriculado e a conta está com o Status Aguardando Ativação, **Quando**
    informa a matrícula e uma senha e clica em "Entrar", **Então** o sistema exibe "Conta ainda não
    ativada" e o link "Primeiro acesso".
11. **Dado que** a conta do docente está com o Status Inativa (US-04), **Quando** ele informa e-mail e
    senha corretos, **Então** o sistema nega o acesso e exibe "Conta inativa".
12. **Dado que** o usuário está na tela de login, **Quando** clica em "Entrar" sem informar a
    credencial ou sem informar a senha, **Então** o sistema exibe "Informe a credencial e a senha" e
    não tenta autenticar.
13. **Dado que** o usuário está autenticado, **Quando** clica em "Sair", **Então** a sessão é
    encerrada e ele volta para a tela de login; páginas internas passam a pedir login de novo.

---

### User Story 3 - Reenviar o link de ativação vencido [US-37] (Priority: P2)

Quem ainda não ativou a conta e abre um link vencido recebe um novo link com um clique; cada novo
link invalida o anterior.

**Why this priority**: sem o reenvio, um link perdido obriga a refazer todo o primeiro acesso ou a
procurar a secretaria.

**Independent Test**: gerar um link, avançar o relógio em mais de 24 horas, abrir o link e clicar em
"Reenviar link de ativação"; o novo link ativa a conta e o anterior não.

**Acceptance Scenarios** (US-37, cenários 1 a 5):

1. **Dado que** o link de ativação foi gerado há mais de 24 horas e não foi usado, **Quando** o
   usuário abre o link, **Então** o sistema não exibe o formulário de senha **E** exibe o aviso "Este
   link de ativação venceu" e o botão "Reenviar link de ativação".
2. **Dado que** o usuário está no aviso de link vencido, **Quando** clica em "Reenviar link de
   ativação", **Então** o sistema gera um novo link válido por 24 horas e o envia ao e-mail
   cadastrado **E** exibe "Enviamos um novo link para o seu e-mail".
3. **Dado que** um novo link de ativação já foi enviado, **Quando** o usuário abre o link anterior,
   **Então** o sistema exibe "Link inválido. Use o link mais recente enviado ao seu e-mail".
4. **Dado que** a conta do usuário já foi ativada, **Quando** ele abre um link de ativação antigo,
   **Então** o sistema exibe "Esta conta já está ativa" e direciona para o login.
5. **Dado que** o Professor da Disciplina resetou o primeiro acesso do aluno (US-12), **Quando** o
   aluno abre o link antigo e clica em "Reenviar link de ativação", **Então** o sistema não reenvia e
   orienta o aluno a refazer o "Primeiro acesso".

---

### User Story 4 - Recuperar ou alterar a senha [US-12] (Priority: P2)

O usuário autenticado altera a senha em "Meu perfil"; quem esqueceu a senha recebe um link de
redefinição; o Professor da Disciplina reseta o primeiro acesso de um aluno da sua turma que
vinculou o e-mail errado.

**Why this priority**: garante a recuperação do acesso sem intervenção da equipe técnica.

**Independent Test**: alterar a senha logado; pedir "Esqueci minha senha" e redefinir pelo link;
resetar o primeiro acesso de um aluno como Professor da Disciplina da turma dele.

**Acceptance Scenarios** (US-12, cenários 1 a 8):

1. **Dado que** o usuário está autenticado, **Quando** informa a senha atual correta e uma nova senha
   válida, igual à confirmação, e clica em "Salvar", **Então** o sistema grava a nova senha e exibe
   "Senha alterada com sucesso".
2. **Dado que** o usuário está no formulário de alteração de senha, **Quando** informa uma senha
   atual errada, **Então** o sistema exibe "Senha atual incorreta" e mantém a senha anterior.
3. **Dado que** o usuário tem conta ativa e esqueceu a senha, **Quando** clica em "Esqueci minha
   senha", informa o e-mail cadastrado, abre o link em menos de 24 horas e define uma nova senha
   válida, **Então** o sistema grava a nova senha **E** o link deixa de valer.
4. **Dado que** o link de recuperação foi gerado há mais de 24 horas, **Quando** o usuário abre o
   link, **Então** o sistema exibe "Link inválido ou vencido. Solicite um novo".
5. **Dado que** o aluno vinculou um e-mail errado no primeiro acesso, **Quando** o Professor da
   Disciplina clica em "Resetar primeiro acesso" e confirma, **Então** a conta do aluno volta para
   "Aguardando Ativação", sem e-mail e sem senha **E** o aluno pode refazer o primeiro acesso com o
   e-mail correto.
6. **Dado que** o usuário está no formulário de alteração de senha, **Quando** informa a nova senha
   "12345678", sem letra, **Então** o sistema exibe "A senha deve ter de 8 a 64 caracteres, com ao
   menos 1 letra e 1 número" e mantém a senha anterior.
7. **Dado que** o aluno pertence a outra turma, **Quando** o Professor da Disciplina abre o perfil
   desse aluno, **Então** a opção "Resetar primeiro acesso" não aparece.
8. **Dado que** a conta está com o Status Aguardando Ativação, **Quando** o usuário pede "Esqueci
   minha senha", **Então** o sistema exibe a mensagem genérica ("Se a conta existir, enviaremos um
   link para o e-mail cadastrado") e não envia o link.

---

### User Story 5 - Editar o perfil e ver as notificações [US-38] (Priority: P3)

O usuário edita só os campos que o seu papel permite e acompanha as notificações geradas pelas
outras features, com contador de não lidas e acesso à tela relacionada.

**Why this priority**: depende do login e só ganha valor pleno quando as outras features passam a
gerar notificações; a edição de perfil é necessária para a assinatura usada na Defesa.

**Independent Test**: editar a imagem de assinatura como Docente e a titulação como Membro Externo;
criar notificações pelo shell e abri-las pela central.

**Acceptance Scenarios** (US-38, cenários 1 a 11):

1. **Dado que** o Docente está em "Meu perfil", **Quando** envia uma nova imagem de assinatura em PNG
   e clica em "Salvar", **Então** o sistema grava a alteração e exibe "Perfil atualizado".
2. **Dado que** o Aluno está em "Meu perfil", **Quando** tenta alterar a Matrícula ou o Curso,
   **Então** o sistema mantém esses campos bloqueados para edição.
3. **Dado que** o Docente está em "Meu perfil", **Quando** envia a imagem de assinatura em um arquivo
   PDF, **Então** o sistema exibe a mensagem de formato não aceito (PROVISÓRIA M-04) e não salva.
4. **Dado que** o usuário tem 3 notificações não lidas, **Quando** clica em uma delas na central de
   notificações, **Então** o sistema abre a tela relacionada **E** o contador de não lidas passa para
   2.
5. **Dado que** o Aluno está em "Meu perfil", **Quando** troca o e-mail institucional por outro
   @uea.edu.br que não está em uso e clica em "Salvar", **Então** o sistema envia um link de
   confirmação ao novo e-mail **E** o novo e-mail só passa a valer depois que o link é aberto.
6. **Dado que** o Aluno está em "Meu perfil", **Quando** informa o e-mail "aluno@gmail.com" e clica
   em "Salvar", **Então** o sistema destaca o campo e não salva.
7. **Dado que** o Membro Externo está em "Meu perfil", **Quando** muda a Titulação de Mestre para
   Doutor e clica em "Salvar", **Então** o sistema grava a alteração e exibe "Perfil atualizado".
8. **Dado que** a Secretaria está em "Meu perfil", **Quando** abre os dados da conta, **Então** todos
   os campos aparecem só para leitura e o botão "Salvar" não aparece.
9. **Dado que** o usuário tem uma notificação de um convite de banca que foi cancelado, **Quando**
   clica nessa notificação, **Então** o sistema exibe "Este item não está mais disponível" e marca a
   notificação como lida. *Testado na feature de Defesa (Clarifications, Q10). Nesta feature, o teste
   equivalente usa um item removido: notificação cujo endereço não leva a nenhuma página existente.*
10. **Dado que** o usuário tem 5 notificações não lidas, **Quando** clica em "Marcar como lidas",
    **Então** o contador de não lidas fica zerado.
11. **Dado que** o Docente está em "Meu perfil", **Quando** envia uma imagem de assinatura em JPG com
    3 MB, **Então** o sistema destaca o campo e não salva.

---

### User Story 6 - Base comum para as demais features (Priority: P1)

Rastreabilidade: [US-11][RBN-CAD-06.4][US-10][US-12][US-37][RBN-CAD-06.1][RBN-CAD-06.2][RBN-CAD-06.7]
[RBN-CAD-06.9]; RNF de Confidencialidade do RAN-CAD-01 e do RAN-CAD-02 ("Cada usuário acessa apenas as
funções dos papéis atribuídos a ele"); constituição, princípio VII.

As outras features (Gestão de Contas, Turmas, TCC, Defesa e Relatórios) reaproveitam o que esta
entrega: o layout visual do protótipo, a verificação de que cada perfil só acessa as funções do seu
papel, a geração e validação dos links de ativação e de redefinição e um modo de criar contas pelo
shell para testes manuais.

**Why this priority**: sem essa base, cada feature reinventaria layout e controle de acesso, e as
telas ficariam diferentes entre si.

**Independent Test**: uma página interna de exemplo, restrita a um perfil, é negada aos demais
perfis e aceita para o perfil certo; as telas desta feature usam o mesmo layout; a geração do link
de ativação funciona chamada de fora das telas desta feature.

**Acceptance Scenarios**:

1. **Dado que** o visitante não está autenticado, **Quando** abre qualquer página interna, **Então**
   o sistema leva à tela de login e, depois do login, de volta à página pedida.
2. **Dado que** uma página é restrita ao Professor da Disciplina, **Quando** um Aluno autenticado
   tenta abri-la (pelo menu ou pelo endereço direto), **Então** o sistema nega o acesso com a
   mensagem de acesso não permitido (PROVISÓRIA M-02) e não mostra nenhum dado da página.
3. **Dado que** o docente é Coordenador de Curso, **Quando** abre uma página restrita ao Coordenador
   de Curso, **Então** o acesso é permitido; para um docente que não é coordenador, é negado.
4. **Dado que** o usuário está autenticado, **Quando** abre qualquer página desta feature, **Então** a
   página mostra a barra superior com o nome do sistema, o sino com o número de notificações não
   lidas e o menu do usuário ("Meu perfil" e "Sair"), além do menu lateral com os itens do seu
   perfil, com a paleta, as fontes e os ícones do protótipo.
5. **Dado que** uma conta 'Aguardando Ativação' existe, **Quando** a geração do link de ativação é
   chamada por código fora das telas desta feature (por exemplo, num teste ou numa feature futura),
   **Então** o link é gerado com validade de 24 horas, invalida o anterior e é aceito pela tela de
   ativação desta feature.
6. **Dado que** a pessoa desenvolvedora está no shell do projeto, **Quando** segue o roteiro do
   quickstart, **Então** cria uma conta de qualquer perfil (Aluno com turma, Docente, Coordenador de
   Curso, Secretaria ou Membro Externo) para testar o login manualmente.

---

### Edge Cases

- **Matrícula sem turma** (US-10, E1): aluno cadastrado mas sem vínculo com turma recebe "Dados não
  encontrados. Procure o Professor da Disciplina ou a Secretaria".
- **Formulário único para Docente, Secretaria e Membro Externo** (Q8): o e-mail de qualquer um dos três
  tipos de conta é aceito; não há recusa por "perfil errado".
- **Primeiro acesso de conta 'Inativa' ou 'Expirada'** (Q6): nenhum link é enviado; aparece a mensagem
  do status (M-15 ou M-16).
- **Vários erros no primeiro acesso** (Q12): só o erro do primeiro campo com problema aparece.
- **Aluno pede de novo com outro e-mail** (Clarifications, Q2): o e-mail novo é ignorado e o link vai
  ao e-mail já registrado; para corrigir um e-mail errado, só o reset do Professor.
- **Conta resetada** (US-12, RBN-CAD-06.8): a conta volta a 'Aguardando Ativação', sem e-mail e sem
  senha; um link antigo mostra a tela de vencido com o botão, e o clique não reenvia e mostra a M-08
  (US-37, cenário 5; Q5). O aluno refaz o primeiro acesso.
- **Senha conferida antes do status** (Q12): a conta 'Aguardando Ativação' recebe "Conta ainda não
  ativada" sem conferir senha; nas contas 'Inativa' e 'Expirada', uma senha errada recebe "Credencial
  ou senha inválida" e conta tentativa, e só a senha correta mostra a mensagem do status. Assim, quem
  não sabe a senha não descobre o status da conta.
- **Credencial inexistente**: recebe "Credencial ou senha inválida", sem contador e sem bloqueio (não
  há conta a bloquear; research D2 da spec 001).
- **Bloqueio por conta, não por credencial**: matrícula e e-mail do mesmo aluno somam no mesmo
  contador (US-11, cenário 6). Durante o bloqueio, nem a senha correta entra.
- **"Esqueci minha senha" para conta que não está 'Ativa'** (US-12, E4) ou e-mail inexistente: mesma
  mensagem genérica, sem envio.
- **Troca de e-mail não confirmada** (US-38, E3): o e-mail antigo continua valendo para login e
  notificações até o link ser aberto; o novo e-mail precisa continuar livre no momento da
  confirmação.
- **Notificação de item removido** (US-38, E1): marcada como lida e "Este item não está mais
  disponível".
- **Sem notificações** (US-38, A2): "Você não tem notificações".
- **Link de outro tipo**: um link de redefinição de senha não serve para ativação, e vice-versa.
- **Membro Externo com a validade vencida mas ainda 'Ativa'** (Q4): o login é negado com a mensagem
  de expiração, como se a conta estivesse 'Expirada'; a mudança do status em si é da US-06.
- **Professor de turma arquivada** (Q9): vê a tela do aluno sem o botão "Resetar primeiro acesso".
- **Falha no envio de e-mail** (Q13): M-17 no primeiro acesso, no reenvio e na troca de e-mail; em
  "Esqueci minha senha", a mensagem genérica se mantém.

## Requirements *(mandatory)*

### Functional Requirements

**Primeiro acesso e ativação [US-10][RBN-CAD-06.1][RBN-CAD-06.2][RBN-CAD-06.3]**

- **FR-001**: A tela de login DEVE oferecer "Primeiro acesso", com duas escolhas (Q8): "Aluno", com
  Matrícula (exatamente 10 dígitos numéricos) e E-mail Institucional (formato nome@uea.edu.br, até 100
  caracteres); e "Docente, Secretaria ou Membro Externo", com E-mail (formato nome@domínio, até 100
  caracteres), aceito se for de uma conta de qualquer um dos três tipos. As contas iniciais de
  Coordenador de Curso criadas na implantação (spec 002) também fazem o primeiro acesso por este
  segundo formulário (RNF de Instalabilidade do RAN-CAD-01; RBN-CAD-06.2).
- **FR-002**: Ao receber dados válidos de uma conta 'Aguardando Ativação' (no
  Aluno, com matrícula vinculada a pelo menos uma turma), o sistema DEVE gerar um link de ativação
  válido por 24 horas, enviá-lo ao e-mail e exibir "Enviamos um link de ativação para o seu e-mail".
  No Aluno sem e-mail registrado, o e-mail informado é registrado na conta antes do envio. No Aluno
  que já tem e-mail registrado de um pedido anterior não concluído, o e-mail informado é ignorado e
  o novo link vai ao e-mail já registrado, com a mesma mensagem (Clarifications, Q2 e Q15). Se o
  e-mail não puder ser enviado, aparece a M-17 (Q13).
- **FR-003**: O primeiro acesso DEVE recusar, com as mensagens exatas da US-10: dados sem conta ou
  matrícula sem turma ("Dados não encontrados. Procure o Professor da Disciplina ou a Secretaria");
  conta já ativa ("Esta conta já está ativa", com orientação para "Esqueci minha senha" ou, no caso do
  Aluno com e-mail errado, para o Professor da Disciplina – complemento PROVISÓRIO M-03); e-mail do
  Aluno fora de @uea.edu.br
  ("Informe o seu e-mail institucional da UEA (@uea.edu.br)"); matrícula fora do formato ("A
  matrícula deve ter 10 dígitos numéricos", com o campo destacado); e-mail do Aluno já usado em outra
  conta ("Este e-mail já está vinculado a outra conta. Procure o Professor da Disciplina"); e-mail fora
  do formato no segundo formulário (M-10); conta 'Inativa' ("Conta inativa", M-15) ou 'Expirada' ou com
  a validade vencida ("Seu acesso expirou. Procure o Orientador, o Professor da Disciplina, a Secretaria
  ou o Coordenador de Curso", M-16). Em todos esses casos nenhum link é enviado. Havendo mais de um
  erro, aparece só o do primeiro campo com problema, na ordem dos campos; dentro de um campo, formato
  antes de existência e existência antes de status (Q12).
- **FR-004**: Ao abrir um link de ativação válido, o sistema DEVE exibir Senha e Confirmação de Senha
  e, em "Ativar conta", exigir senha de 8 a 64 caracteres com ao menos 1 letra (A–Z, maiúscula ou
  minúscula; letras acentuadas são aceitas, mas não contam como essa letra, Q17) e 1 número,
  aceitando caracteres especiais ("A senha deve ter de 8 a 64 caracteres, com
  ao menos 1 letra e 1 número"), e confirmação idêntica ("As senhas não conferem").
- **FR-005**: Ao ativar, o sistema DEVE gravar a senha só como hash, mudar o Status da Conta de
  'Aguardando Ativação' para 'Ativa', invalidar o link e levar à tela de login com "Conta ativada".
- **FR-006**: Cada novo pedido de primeiro acesso ou reenvio DEVE invalidar os links de ativação
  anteriores da conta; só o mais recente ativa a conta (US-10, A2; RBN-CAD-06.9).

**Login, bloqueio e saída [US-11][RBN-CAD-06.4][RBN-CAD-06.6][RBN-CAD-03.3]**

- **FR-007**: O login DEVE ter os campos Credencial e Senha (senha de 8 a 64 caracteres, exibida
  mascarada; RBN-CAD-06.4). Credencial do Aluno: matrícula de 10 dígitos ou o e-mail institucional
  vinculado; dos demais perfis: e-mail. E-mails são comparados sem diferenciar maiúsculas de
  minúsculas (Q13). Senha fora de 8 a 64 caracteres é tratada como senha incorreta (Q17).
- **FR-008**: O sistema DEVE avaliar o login nesta ordem (Q12), com as mensagens exatas da US-11:
  (1) campo vazio – "Informe a credencial e a senha", sem tentar autenticar; (2) credencial sem conta
  – "Credencial ou senha inválida"; (3) conta 'Aguardando Ativação' – "Conta ainda não ativada", com o
  link "Primeiro acesso", sem conferir senha; (4) bloqueio vigente – M-01; (5) senha incorreta –
  "Credencial ou senha inválida", sem dizer qual está errado, contando a tentativa; (6) com a senha
  correta: conta 'Inativa' – "Conta inativa"; conta 'Expirada', ou de Membro Externo com a data de
  hoje depois de `mem_validade_ate` (Q4; RBN-CAD-03.3) – "Seu acesso expirou. Procure o Orientador, o
  Professor da Disciplina, a Secretaria ou o Coordenador de Curso"; conta 'Ativa' – login aceito.
- **FR-009**: Na terceira senha incorreta seguida para a mesma conta, qualquer que seja a credencial
  usada, o sistema DEVE bloquear a conta por 15 minutos, exibir o bloqueio e o tempo restante
  (mensagem PROVISÓRIA M-01) e
  recusar qualquer tentativa durante o prazo, mesmo com a senha correta. A senha correta zera o
  contador. O "N" da M-01 é o número de minutos restantes arredondado para cima, no mínimo 1 (Q16). O controle não cria coluna nem tabela (spec 001, research D2).
- **FR-010**: Com o login aceito, o sistema DEVE abrir a sessão e levar o usuário ao painel do seu
  tipo de conta (Aluno, Docente, Secretaria ou Membro Externo). O Docente tem um painel único; os
  itens de Coordenador de Curso, Professor da Disciplina, Orientador e Coorientador aparecem como
  itens extras no menu, conforme os papéis que ele tiver (Q7).
- **FR-011**: O usuário autenticado DEVE poder sair ("Sair" no menu do usuário), encerrando a sessão.

**Recuperar e alterar a senha [US-12][RBN-CAD-06.5][RBN-CAD-06.7][RBN-CAD-06.8]**

- **FR-012**: Em "Meu perfil", "Alterar senha" DEVE pedir Senha Atual (de 8 a 64 caracteres, exibida
  mascarada; RBN-CAD-06.5), Nova Senha e Confirmação da Nova Senha, conferir a senha atual ("Senha atual incorreta"), aplicar a regra de FR-004 à nova senha
  e, ao salvar, exibir "Senha alterada com sucesso".
- **FR-013**: "Esqueci minha senha" DEVE pedir o e-mail cadastrado; com e-mail em formato válido
  (senão, M-10), sempre exibir "Se a conta existir, enviaremos um link para o e-mail cadastrado",
  mesmo se o envio falhar (Q13); só envia o link de redefinição (válido por 24 horas)
  se o e-mail for de uma conta 'Ativa'.
- **FR-014**: O link de redefinição DEVE abrir Nova Senha e Confirmação (regra de FR-004), gravar a
  senha e deixar de valer depois de usado; link vencido, usado ou substituído exibe "Link inválido ou
  vencido. Solicite um novo".
- **FR-015**: O Professor da Disciplina DEVE poder "Resetar primeiro acesso" de um aluno de turma sob
  sua responsabilidade, com confirmação: o sistema limpa o e-mail e a senha, invalida os links
  pendentes e volta a conta para 'Aguardando Ativação' (confirmação e conclusão com as mensagens
  PROVISÓRIAS M-12 e M-13). Esta feature entrega a ação de reset, reutilizável, e uma tela mínima
  com os dados do aluno, aberta a Professores da Disciplina. O botão "Resetar primeiro acesso" só
  aparece, e a ação só é aceita, para o Professor da Disciplina de qualquer turma não arquivada do
  aluno; para os demais, a tela abre sem o botão (Clarifications, Q3 e Q9). A US-41 incorporará o
  botão ao painel do aluno.

**Reenvio do link vencido [US-37][RBN-CAD-06.9]**

- **FR-016**: Um link de ativação DEVE ser avaliado nesta ordem (Q5): (1) conta já ativa – "Esta conta
  já está ativa" e ida para o login; (2) conta sem e-mail (resetada) – tela de vencido com o botão; (3)
  link substituído por outro mais recente – "Link inválido. Use o link mais recente enviado ao seu
  e-mail"; (4) link vencido (mais de 24 horas, não usado) – "Este link de ativação venceu" e o botão
  "Reenviar link de ativação", sem o formulário de senha; (5) link válido – formulário de ativação.
- **FR-017**: "Reenviar link de ativação" DEVE invalidar o link anterior, gerar um novo válido por 24
  horas, enviá-lo ao e-mail cadastrado e exibir "Enviamos um novo link para o seu e-mail" (falha no
  envio: M-17, Q13).
- **FR-018**: Para conta resetada (sem e-mail), o clique em "Reenviar link de ativação" NÃO DEVE
  reenviar: o usuário é orientado a refazer o "Primeiro acesso" (mensagem PROVISÓRIA M-08; US-37, E3 e
  cenário 5).

**Perfil e notificações [US-38][RBN-CAD-13.1][RBN-CAD-13.2]**

- **FR-019**: "Meu perfil" DEVE mostrar os dados da conta e liberar para edição só: Aluno – E-mail
  Institucional; Docente (inclusive Coordenador de Curso) – Imagem de Assinatura; Membro Externo –
  E-mail, Titulação (Especialista, Mestre ou Doutor) e Instituição de Origem (até 150 caracteres) e
  Imagem de Assinatura; Secretaria – nenhum campo (tudo só leitura e sem o botão "Salvar"). Nome,
  e-mail de Docente e de Secretaria, papéis, cursos e Matrícula ficam só leitura.
- **FR-020**: A Imagem de Assinatura DEVE aceitar só PNG ou JPG com até 2 MB; fora disso, o campo é
  destacado com a mensagem de formato não aceito (PROVISÓRIA M-04) e nada é salvo. Com dados
  válidos, o sistema grava e exibe "Perfil atualizado" (se a alteração incluir troca de e-mail,
  aparece só a M-06; Q11).
- **FR-021**: A troca de e-mail (Aluno e Membro Externo) DEVE validar formato (M-10), domínio
  @uea.edu.br no Aluno (M-11) e unicidade (M-05), enviar um link de confirmação ao novo endereço (M-06)
  e só trocar o e-mail depois que o link for aberto (M-07; link inválido: M-09); até lá, o e-mail
  antigo continua valendo. O link de confirmação vale 24 horas, como o de primeiro acesso (Q11); se
  ele deixa de valer quando outro é gerado é decisão do plano. Falha no envio: M-17. Todas essas
  mensagens são PROVISÓRIAS.
- **FR-022**: Todas as páginas internas DEVEM mostrar o sino com o número de notificações não lidas
  do usuário. A central DEVE listar todas as notificações, da mais recente para a mais antiga, 20 por
  página, com o texto, a data e a hora (Q14); "Marcar como lidas" marca todas e zera o contador; sem notificações, exibe "Você
  não tem notificações".
- **FR-023**: Clicar numa notificação DEVE marcá-la como lida, atualizar o contador e abrir a tela
  relacionada; se o endereço não levar a uma página existente (item removido), exibe "Este item não
  está mais disponível" (Q10). O item cancelado fica para a feature dona do item (pendência da
  Defesa).

**Base comum para as demais features (entregas compartilhadas)**

- **FR-024**: O sistema DEVE ter um layout base com o visual do protótipo de 17/10: paleta, fontes
  Roboto e Figtree, ícones Material Symbols, barra superior (nome do sistema, sino, menu do usuário),
  menu lateral por perfil e padrões de botão, campo, mensagem de erro por campo, alerta e aviso
  temporário. Todas as telas desta feature o usam, e as demais features DEVEM usá-lo. A lógica em
  JavaScript do protótipo não é reaproveitada. A conferência visual segue um checklist de revisão
  (paleta, fontes, ícones, barra superior, menu lateral, componentes; Q16). [base de todas as US;
  protótipo de 17/10][RNF de Operabilidade do RAN-CAD-06]
- **FR-025**: O sistema DEVE oferecer uma verificação de acesso reutilizável: cada página interna
  declara os perfis permitidos – tipos de conta (Aluno, Docente, Secretaria, Membro Externo) e papéis
  do Docente (Coordenador de Curso, Professor da Disciplina, Orientador, Coorientador), estes
  derivados dos dados existentes. Visitante não autenticado vai para o login; autenticado sem
  permissão recebe a mensagem de acesso não permitido (PROVISÓRIA M-02), sem ver dados da página,
  inclusive pelo endereço direto. O menu lateral mostra só os itens permitidos ao usuário.
  [US-11][RBN-CAD-06.4][RNF de Confidencialidade do RAN-CAD-01 e do RAN-CAD-02; constituição, VII]
- **FR-026**: O sistema DEVE oferecer funções reutilizáveis para gerar, enviar e validar os links de
  ativação (24 horas, só o mais recente vale) e de redefinição de senha, usadas pelas telas desta
  feature e disponíveis para outras features. A criação de conta (spec 002) NÃO envia link: a conta
  nasce 'Aguardando Ativação' e o usuário pede o link em "Primeiro acesso" (Clarifications, Q1).
  [US-10][US-12][US-37][RBN-CAD-06.1][RBN-CAD-06.2][RBN-CAD-06.7][RBN-CAD-06.9]
- **FR-027**: DEVE existir um modo, só para desenvolvimento e testes manuais, de criar pelo shell uma
  conta de qualquer perfil ('Aguardando Ativação' ou 'Ativa'), inclusive Aluno com turma e Docente
  Coordenador de Curso, documentado no quickstart. Não é tela do produto e não substitui a Gestão de
  Contas (spec 002). [infraestrutura de teste da feature 003, sem US específica]
- **FR-028**: Esta feature NÃO DEVE criar tabelas nem colunas: usa o modelo da spec 001 (Usuarios e
  especializações, Coordenadores, Turmas, Alunos_Turmas, Orientacoes, Coorientacoes, Notificacoes).
  NÃO DEVE criar contas pelas telas (US-03, US-05, US-08) nem gerar notificações de outras features.

### Key Entities *(include if feature involves data)*

Todas já existem (spec 001); nenhuma é criada.

- **Usuarios**: conta de login (nome, e-mail, senha só em hash, Status da Conta, momento do último
  link gerado, que invalida os anteriores).
- **Alunos, Docentes, Secretarios, MembrosExternos**: tipo da conta e dados do perfil (matrícula;
  titulação, instituição e assinatura).
- **Coordenadores, Turmas, Alunos_Turmas, Orientacoes, Coorientacoes**: de onde vêm os papéis do
  Docente (Coordenador de Curso, Professor da Disciplina, Orientador, Coorientador) e a regra "aluno
  com turma" e "aluno da turma do Professor".
- **Notificacoes**: mensagens do usuário, com data e hora, endereço da tela relacionada e a marcação
  de lida.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos cenários de aceite das US-10, US-11, US-12, US-37 e US-38 (47 cenários) e das
  histórias 2 (saída) e 6 passam em testes automatizados. O cenário 9 da US-38 é testado aqui na
  variante "item removido" e, na variante "convite cancelado", pela feature de Defesa (Q10).
- **SC-002**: 100% das mensagens exibidas nesta feature que têm texto definido nas US são idênticas ao
  texto da US, caractere por caractere; as 17 mensagens PROVISÓRIAS (M-01 a M-17) são idênticas ao
  texto da seção "Mensagens a validar com a PO" na versão vigente.
- **SC-003**: Um usuário com conta 'Aguardando Ativação' conclui o primeiro acesso (pedido, abertura
  do link e criação da senha) em até 3 minutos, sem ajuda, medido em teste manual cronometrado sem
  contar o tempo de entrega do e-mail (Q16).
- **SC-004**: Nenhuma página interna é acessível sem login, e nenhuma página restrita é acessível a
  perfil não permitido, verificado por teste para cada página desta feature.
- **SC-005**: Depois de 3 senhas incorretas seguidas, 100% das tentativas na mesma conta são
  recusadas por 15 minutos, por qualquer credencial; depois desse prazo, a senha correta volta a
  entrar.
- **SC-006**: Todo link de ativação ou de redefinição deixa de funcionar em 24 horas, depois de usado
  ou quando outro mais recente é gerado para a mesma conta.
- **SC-007**: Todas as telas desta feature usam o layout base, com a paleta, as fontes e os ícones do
  protótipo, conferido pelo checklist de revisão visual com o protótipo lado a lado (Q16).
- **SC-008**: Nenhuma senha aparece em tela, em log ou no banco em texto puro.

## Mensagens a validar com a PO

As mensagens abaixo **não têm texto definido nas US nem na matriz**. Os textos são **PROVISÓRIOS**:
servem para planejar e testar, mas precisam da validação da Product Owner (Profa. Diana) antes da
implementação. Depois da resposta, cada linha vira o texto definitivo (ou é corrigida) e a coluna
"Situação" passa para "Validada". Todas as demais mensagens desta spec são cópias exatas das US.

| ID | Situação em que aparece | Texto proposto (PROVISÓRIO) | Origem | Situação |
|---|---|---|---|---|
| M-01 | Login bloqueado após 3 senhas incorretas seguidas; N é o tempo restante em minutos | "Acesso bloqueado por 15 minutos após 3 tentativas incorretas. Tente novamente em N minutos." | US-11 E2 e cenário 5; RBN-CAD-06.6 ("mensagem informando o bloqueio e o tempo restante") | A validar |
| M-02 | Usuário autenticado abre uma página que o seu perfil não pode acessar | "Você não tem permissão para acessar esta página." | FR-025 (verificação de perfil); RNF de Confidencialidade do RAN-CAD-01 e do RAN-CAD-02 | A validar |
| M-03 | Complemento de "Esta conta já está ativa" no primeiro acesso | "Use \"Esqueci minha senha\" ou, se o e-mail estiver errado, procure o Professor da Disciplina." | US-10 E2 e cenário 7 ("orienta a usar…") | A validar |
| M-04 | Imagem de assinatura que não é PNG ou JPG, ou maior que 2 MB | "Envie uma imagem PNG ou JPG com até 2 MB." | US-38 E2, cenários 3 e 11; RBN-CAD-13.1 | A validar |
| M-05 | E-mail informado no perfil já usado por outra conta | "Este e-mail já está vinculado a outra conta." | US-38 E2; RBN-CAD-13.1 | A validar |
| M-06 | Troca de e-mail salva; link de confirmação enviado ao novo endereço. Aparece sozinha, no lugar de "Perfil atualizado" (Q11) | "Enviamos um link de confirmação para o novo e-mail." | US-38 passo 4 e cenário 5 | A validar |
| M-07 | Link de confirmação do novo e-mail aberto com sucesso | "E-mail atualizado." | US-38 passo 4 | A validar |
| M-08 | Reenvio pedido para conta resetada pelo Professor (sem e-mail vinculado) | "Refaça o primeiro acesso para receber um novo link." | US-37 E3 e cenário 5 | A validar |
| M-09 | Link de confirmação de e-mail vencido (24 h, Q11) ou já usado; o caso "substituído" depende do plano | "Link inválido ou vencido. Solicite um novo" (reaproveita o texto da US-12) | US-38 (não trata o caso) | A validar |
| M-10 | E-mail fora do formato nome@domínio (perfil, primeiro acesso de Docente, Secretaria e Membro Externo, "Esqueci minha senha") | "Informe um e-mail válido." | US-38 E2; RBN-CAD-06.2, 06.7 e 13.1 | A validar |
| M-11 | E-mail institucional do Aluno fora de @uea.edu.br em "Meu perfil" | "Informe o seu e-mail institucional da UEA (@uea.edu.br)" (reaproveita o texto da US-10) | US-38 E2 e cenário 6 | A validar |
| M-12 | Confirmação do "Resetar primeiro acesso" (pergunta antes de executar) | "Resetar o primeiro acesso de NOME? O e-mail e a senha vinculados serão apagados e o aluno deverá refazer o primeiro acesso." | US-12 A2 e cenário 5; RBN-CAD-06.8 | A validar |
| M-13 | Reset do primeiro acesso concluído | "Primeiro acesso resetado. O aluno já pode refazer o primeiro acesso." | US-12 A2 | A validar |
| M-14 | Campo obrigatório vazio nos formulários desta feature (exceto o login, que já tem texto) | "Preencha este campo." | US-10, US-12 e US-38 (não tratam o caso) | A validar |
| M-15 | Primeiro acesso de conta 'Inativa' (Q6) | "Conta inativa" (reaproveita o texto da US-11) | US-10 (não trata o caso); US-11 E5 | A validar |
| M-16 | Primeiro acesso de conta 'Expirada' ou de Membro Externo com a validade vencida (Q4, Q6) | "Seu acesso expirou. Procure o Orientador, o Professor da Disciplina, a Secretaria ou o Coordenador de Curso" (reaproveita o texto da US-11) | US-10 (não trata o caso); US-11 E3 | A validar |
| M-17 | Falha no envio do e-mail no primeiro acesso, no reenvio do link ou na troca de e-mail (Q13) | "Não foi possível enviar o e-mail agora. Tente novamente em alguns minutos." | Nenhuma fonte trata o caso | A validar |

## Assumptions

- **Branch**: a responsável indicou `feature/feat-02-turmas`. No PGCS 4.3, `feat-02` é Turmas; a
  confirmação do nome (ou a troca para uma branch de Acesso e Login) fica com o Célio Benjamim. O
  número da spec (003) é independente da branch.
- **Precedência**: matriz de 17/10 > US v3.2. As divergências tratadas estão em Clarifications (Q4,
  Q8 e Q14).
- **Mensagens sem texto exato nas US**: estão na seção "Mensagens a validar com a PO" (M-01 a
  M-17), marcadas como PROVISÓRIAS. A implementação usa esses textos até a validação; um texto
  validado diferente entra como correção da spec, com o teste correspondente.
- **Painéis**: esta feature entrega um painel inicial mínimo por tipo de conta (boas-vindas e menu);
  o conteúdo de cada painel vem das features dos épicos. O Docente tem um só painel, com os itens de
  cada papel no menu (Q7).
- **E-mail**: o envio usa um servidor de e-mail configurado no ambiente (segredos no .env); em
  desenvolvimento, as mensagens com os links aparecem no terminal. A falha de envio é registrada; o
  que o usuário vê está em Q13.
- **Links**: o link de confirmação de troca de e-mail vale 24 horas (Q11) e não usa tabela (o novo
  e-mail vai no próprio link; dicionário, seção 4, item 3). Ativação e redefinição seguem o item 2
  (o momento do último link gerado invalida os anteriores).
- **Sessão**: encerra ao sair; a duração máxima da sessão sem uso fica para o plano. Alterar a senha
  mantém a sessão atual.
- **Credenciais**: regras em Q13 e Q17; a matrícula é sempre de 10 dígitos.
- **Fora do escopo**: criação de contas e contas iniciais de Coordenador (spec 002, US-03); inativação
  e reativação (US-04); expiração automática e prorrogação de Membro Externo (US-06); geração de
  notificações (cada feature que notifica); painel do aluno da US-41 (ver FR-015); envio do link na
  criação da conta (não existe, Clarifications Q1).
- **Pendências para outras features**: a US-41 (Feature 6, Leandra Matos) deve incorporar o botão
  "Resetar primeiro acesso" ao painel do aluno, chamando a ação de reset desta feature; a spec 002
  (Maria Luísa Gomes) cria as contas sem chamar a geração do link (Clarifications Q1); a feature de
  Defesa deve tratar, na sua tela de destino, a notificação de convite de banca cancelado (US-38,
  cenário 9; Q10); a US-06 deve mudar para 'Expirada' as contas de Membro Externo com a validade
  vencida (o login já as bloqueia pela data, Q4).
- **Dependências**: spec 001 implementada (modelo e decisões D1 e D2). Para os cenários com turma,
  usam-se turmas criadas pelo shell até a feature de Turmas existir.
