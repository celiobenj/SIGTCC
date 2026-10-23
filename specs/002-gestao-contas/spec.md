# Feature Specification: Gestão de Contas do SIGTCC

**Feature Branch**: `feature/feat-04-gestao-de-contas`

**Created**: 2026-10-22

**Status**: Draft

**Input**: User description: "Use o número 002 para esta spec. Gestão de Contas do SIGTCC: US-03, 04,
05, 06 e 50. Use as seções dessas US em docs/fonte/Historias_de_Usuario_v3_2.md, com regras (RBN),
fluxos alternativos, mensagens exatas e cenários de aceite; IDs da matriz de 17/10. O modelo de dados
já existe (spec 001); não crie tabelas. Reutilize a base visual e @perfil_requerido da spec 003, e
normalizar_email e email_em_uso. A criação de contas não envia link de ativação. Inclua o comando de
gestão que cria os Coordenadores de Curso iniciais. Não crie nem troque de branch: use a
feature/feat-04-gestao-de-contas. Não faça commit."

**Responsável**: Maria Luísa Gomes (US-03 a US-06 no documento de US). A US-50 aparece no documento
com a responsável "Maria Luiza Nobre", que não é da equipe (correção pedida no índice, Q-61).

**Fontes**: `docs/fonte/Historias_de_Usuario_v3_3.md` (US-03, US-04, US-05, US-06 e US-50; o pedido
cita a v3.2, mas a cópia de referência em `docs/fonte/` é a v3.3); `docs/fonte/Matriz_Requisitos_17_10.md`
(RAN-CAD-01, RAN-CAD-02, RAN-CAD-03 e RAN-CAD-14 com os RNFs; RBN-CAD-01.1 a 01.4, 02.1 a 02.3,
03.1 a 03.3, 06.2, 11.3 e 14.1; RBN-DEF-02.3 e 02.4; Glossario_Status); `docs/fonte/Modelo_Logico_e_Dicionario_18_10.md` (tabelas
existentes); `docs/fonte/prototipo/prototipo_17_10.html` (só o visual: telas Cadastros, Docentes,
Secretarias e Membros externos); `specs/001-modelo-dados/` (modelo de dados); `specs/003-acesso-login/`
(base visual, verificação de perfil, primeiro acesso, login, e-mail sem diferenciar maiúsculas, log e
mensagens); `specs/004-turmas-alunos/` (turmas, usadas na verificação de vínculos).

**Rastreabilidade**: [US-03][RBN-CAD-01.1][RBN-CAD-01.2][RBN-CAD-01.4][RBN-CAD-02.1][RBN-CAD-02.2] ·
[US-04][RBN-CAD-01.3][RBN-CAD-01.2][RBN-CAD-02.2][RBN-CAD-02.3] ·
[US-05][RBN-CAD-03.1][RBN-CAD-03.2][RBN-DEF-02.3] · [US-06][RBN-CAD-03.3][RBN-DEF-02.4] ·
[US-50][RBN-CAD-03.3] · apoio: [RBN-CAD-11.3][RBN-CAD-14.1][RBN-CAD-06.2] · RNF de Instalabilidade
do RAN-CAD-01 (comando dos Coordenadores iniciais). Tabela completa na seção "Rastreabilidade".

## Clarifications

### Session 2026-10-22

- Q1 (definida no pedido da spec; índice Q-14): a criação de contas desta feature (Docente,
  Secretaria, Membro Externo e Coordenadores iniciais) **não** envia link de ativação. A conta fica
  'Aguardando Ativação', e a pessoa recebe o link pelo "Primeiro acesso" da spec 003
  (RBN-CAD-06.2), como já previa a Q1 daquela spec.
- Q2 (definida no pedido da spec; índice Q-15): esta feature inclui um comando de gestão, rodado na
  implantação, que cria as contas dos Coordenadores de Curso de Engenharia de Computação, Sistemas de
  Informação e Licenciatura em Computação (RNF de Instalabilidade do RAN-CAD-01). O primeiro acesso
  dessas contas segue o RBN-CAD-06.2.
- Q3 (resolvida pela matriz, sem decisão nova; índice Q-16): a US-06 muda o Status da Conta para
  'Expirada' na tentativa de login (passo 4), e o RNF de Integridade do RAN-CAD-03 diz que a conta
  "passa ao Status Expirada automaticamente ao fim da validade". Valem os dois: o status passa a
  'Expirada' automaticamente a partir do dia seguinte ao fim da validade, em todas as telas, e o
  login também faz a troca, se ela ainda não tiver ocorrido. O login da spec 003 já nega o acesso pela
  data (Q4 daquela spec). Confirmado em 2026-10-22 (índice Q-16).
- Q4 (índice Q-51): a US-06 (passo 4, E1 e cenário 3) usa a mensagem "Seu acesso expirou. Procure
  a coordenação do curso". A matriz (RBN-CAD-03.3) pede uma mensagem que oriente o contato com "o
  Orientador, o Professor da Disciplina, a Secretaria ou o Coordenador de Curso", que é o texto do
  login da spec 003 (M-16, tirado da US-11 E3). Qual vale? → A: o texto da US-06, por decisão da
  responsável em 2026-10-22, embora a matriz tenha precedência. A troca do texto no login é da spec
  003 (Julia Cohen; índice Q-52).
- Q5 (resolvida pela matriz; US-03 E8 e cenário 17, "a confirmar com a equipe"): pelo RBN-CAD-14.1,
  "as ações do Coordenador de Curso e da Secretaria (cadastros, inativações, transferências...)
  continuam restritas ao próprio curso". O curso do usuário é o Curso Coordenado do Coordenador ou o
  Curso Vinculado da Secretaria. Para Docente, vale o Curso de Lotação; para Secretaria, o Curso
  Vinculado. Na alteração, vale o curso **atual** do registro: um docente do curso do usuário pode
  ser movido para outro Curso de Lotação (US-03, cenário 36). O Curso Coordenado escolhido para um
  docente pode ser qualquer curso do NUCOMP sem Coordenador (US-03, cenário 33). Confirmado em
  2026-10-22 (índice Q-55): segue a US-03, cenário 33, mesmo com o RBN-CAD-14.1 restringindo os
  cadastros ao próprio curso.
- Q6 (divergência interna da US-03, só de texto): o fluxo principal diz "Docente salvo", e o cenário
  1 diz "Docente cadastrado com sucesso". Esta spec usa o texto do cenário, que é o critério de
  aceite e segue o padrão de "Secretaria cadastrada com sucesso" e "Membro externo cadastrado com
  sucesso". Texto definido em 2026-10-22 (MC-08; índice Q-46).
- Q7 (consequência das fontes): "curso já tem Secretaria" quer dizer que o curso tem uma Secretaria
  'Aguardando Ativação' ou 'Ativa'. Só a inativação libera o curso (US-03 A5; RBN-CAD-02.3). O
  dicionário (restrição de `Secretarias` e seção 4, regra 12) e o Glossário da matriz (Curso
  Vinculado) falam em "uma Secretaria com Status da Conta 'Ativa' por curso", mas contar só as
  'Ativa' permitiria cadastrar duas Secretarias antes da ativação, e as duas ficariam 'Ativa'.
  Confirmado em 2026-10-22; o ajuste do texto no dicionário é da Maria Luiza Guimarães (índice
  Q-60).
  Mantido em 2026-10-22 (índice Q-49): como na US-04, só a conta 'Ativa' pode ser inativada. Um
  cadastro errado em 'Aguardando Ativação' (Docente ou Secretaria) é corrigido pela alteração
  (US-03), não pela inativação.
- Q8 (resolvida pela matriz): a US-03 fala em "quantidade de orientandos". O RBN-CAD-01.4 remete ao
  RBN-CAD-11.3 (da US-18), que separa a quantidade em TCC 1 e TCC 2 e exibe um alerta visual para o
  Coordenador e para a Secretaria quando o docente passa de 5 orientandos. A listagem desta feature
  já mostra a quantidade assim.
- Q9 (texto exato das US): nesta feature, a ação recusada por falta de permissão mostra o texto das
  US, "Você não tem permissão para esta ação" (US-03 E9, US-05 E7, US-50 E2), e o campo obrigatório
  vazio mostra "Campo obrigatório" (US-03 E5, US-05 E3). Decidido em 2026-10-22 (índice Q-50): o
  sistema todo passa a usar esses textos, sem alterar as US. A M-02 e a M-14 da spec 003 passam a
  ter os textos das US (spec 003, Q30), e a troca nas constantes de mensagens entra na implementação
  desta feature.
- Q10 (regra compartilhada da spec 003, Q27; índice Q-31): o Professor da Disciplina com turmas só
  arquivadas vê a lista de Membros externos, mas não cadastra, não altera e não prorroga. Essas ações
  exigem pelo menos uma turma não arquivada. Confirmado em 2026-10-22.
- Q11 (leitura da US-50 com a matriz): a matriz (RBN-CAD-03.3) diz que "o Orientador" pode prorrogar,
  e a US-50 restringe ao Orientador do TCC cuja banca inclui o Membro Externo. Esta spec segue a
  US-50: o papel de Orientador é global (spec 003, Q27), e o vínculo com o objeto é conferido pela
  feature. O Professor da Disciplina (com turma não arquivada), a Secretaria e o Coordenador
  prorrogam qualquer Membro Externo (US-50, fluxo C). Confirmado em 2026-10-22 (índice Q-56),
  inclusive as condições "sessão não Cancelada" e "orientação ativa" do FR-042 e das Assumptions,
  que não estão nas fontes.
- Q12 (validade do Membro Externo sem banca; índice Q-44): a US-05 (A5) e a US-06 (A5) dão 30 dias
  corridos a partir do cadastro, mas o dicionário diz que `mem_validade_ate` é "nulo enquanto não
  houver vínculo com banca", e não existe coluna com a data de cadastro. Como guardar essa validade
  sem criar coluna? → A: Gravar a data do cadastro + 30 dias em `mem_validade_ate`, que fica
  preenchida desde o cadastro, e atualizar a descrição da coluna no dicionário (pendência da Maria
  Luiza Guimarães, dona do documento). Nenhuma coluna é criada. O login da spec 003 não muda: ele já
  nega o acesso com a validade vencida.
- Q13 (prazo "a confirmar" na própria US-06, A7 e cenário 17; índice Q-45): o membro é retirado da
  única banca antes da sessão (alteração da banca, RBN-DEF-02.4; a US-06 cita o ID antigo
  DEF-02.10). Qual validade vale quando não sobra nenhuma sessão válida? → A: 7 dias
  corridos após a data da retirada, como no cancelamento da sessão (A3). A data da retirada vem do
  histórico da defesa. Complemento confirmado em 2026-10-22 (índice Q-45): se o membro só tiver
  sessões Canceladas e retiradas, vale o evento mais recente dos dois, mais 7 dias corridos.
- Q14 (índice Q-46): os textos sem definição nas US (MC-01 a MC-10) foram revisados para ficar
  coerentes com os textos das US e definidos em 2026-10-22. O padrão é este: confirmação no formato
  "Deseja AÇÃO o/a PERFIL NOME?"; sucesso com particípio e sem ponto final ("Docente reativado");
  motivos de bloqueio como continuação de "Não é possível inativar: o docente ..."; e concordância de
  número (com N = 1, singular: "possui 1 convite de coorientação sem resposta"). A exceção é o
  motivo (a) da inativação, que usa sempre o texto da US-04 E1, no plural, para atender aos
  cenários 2 e 3 (Q18). A PO pode revisar qualquer texto depois, sem mudar regra.
- Q15 (índice Q-47): o recálculo pela banca (US-06) substitui uma prorrogação manual (US-50)? → A:
  Não. A prorrogação fica protegida: o recálculo nunca deixa a validade antes da data dada pela
  última prorrogação manual. Fora disso, a US-06 vale como está: cancelamento, reagendamento para
  antes e retirada reduzem a validade (cenários 7, 11 e 17), e nova banca mais distante a estende.
  Assim nenhuma US muda. Como o dicionário não tem coluna para a data da prorrogação, o plano define
  de onde ela é lida, sem tabela nova (Assumptions, "Data da última prorrogação").
- Q16 (índice Q-53): a US-04 (A4 e cenário 11) cita o Status do TCC "Pendente", que a matriz de
  17/10 retirou (aba mudanças_17_10, RBN-CAD-08.3; não está no Glossario_Status nem em
  `tcc_status`). → A: trocar por 'Sem Proposta', que também não impede a inativação. A correção
  da US-04 fica pedida no índice (Q-61).
- Q17 (índice Q-57): a US-03 (A11 e cenário 32) e a US-05 (A3 e cenário 17) dizem que o e-mail
  alterado pelo gestor vale na hora. O dicionário (seção 4, regra 3) diz que `usu_email` só é
  atualizado após a confirmação. → A: toda troca de e-mail é confirmada. Quem altera confirma a
  troca com a própria senha, e o novo endereço recebe um link de confirmação. O e-mail só muda
  depois que o link é confirmado; até lá, o e-mail antigo continua sendo o login. A regra de
  invalidar os links de ativação e de redefinição gerados antes da troca foi retirada, porque não
  está em nenhuma fonte. A correção das US fica pedida no índice (Q-61).
- Q18 (índice Q-54): com N = 1, o alerta de inativação ia para o singular ("possui 1 orientando ou
  coorientando com TCC ativo"), mas os cenários 2 e 3 da US-04 esperam o trecho no plural. → A:
  usar sempre o texto da US-04 E1, "possui N orientandos ou coorientandos com TCC ativo", sem
  singular.
- Q19 (índice Q-59): o RBN-CAD-14.1 pede o filtro de Curso em todas as listas do Coordenador e da
  Secretaria, mas o Membro Externo não tem curso (dicionário, `MembrosExternos`). → A: a lista de
  Membros externos não tem filtro de Curso.

### Session 2026-10-22 (conferências do analista de requisitos)

Correções aplicadas sem decisão nova (primeira e segunda conferências):

- Q20 (IDs e rastreabilidade): a US-06 A7 cita o ID antigo "DEF-02.10", que na aba mudanças_17_10
  virou RBN-DEF-02.4; a spec usa o ID novo (Q13, FR-037, cabeçalho). A rastreabilidade passou a
  incluir RBN-CAD-01.2 e 02.2 na US-04, RBN-DEF-02.3 na US-05 e RBN-DEF-02.4 na US-06, e ganhou a
  seção "Rastreabilidade", com o texto de cada RBN, os RNFs da matriz e os FR e SC que os atendem.
  As histórias passaram a trazer atores e pré-condições copiados das US.
- Q21 (nomes dos botões): as US-03 e US-05 usam nomes diferentes para o mesmo botão. Como na Q6,
  vale o texto dos cenários: "Salvar", "Nova secretaria", "Cadastrar Docente" e "Novo membro
  externo" (Assumptions, "Nomes dos botões"). A correção das US está no índice (Q-61).
- Q22 (prioridades): o cabeçalho da US-04 diz Must Have, e a matriz dá Should Have (RBN-CAD-01.3 e
  02.3); vale a matriz, e a correção da US está na Q-61. O cabeçalho da US-50 diz Could Have, mas a
  prorrogação faz parte do RBN-CAD-03.3, Must Have na matriz. → Pendente: a PO decide (índice Q-63).
  Recomendação: seguir a matriz e entregar a US-50 junto com a US-06.
- Q23 (documentos de referência): a cópia em `docs/fonte/` é a US v3.3. O CLAUDE.md e os agentes
  foram corrigidos; a constituição aguarda o Célio Benjamim (índice Q-62). A US-50 cita a
  responsável "Maria Luiza Nobre", que não é da equipe (Q-61).
- Q24 (detalhes da troca de e-mail pelo gestor, consequência da Q17): no formulário do gestor, o
  e-mail repetido mostra "Este e-mail já está cadastrado" (FR-001); a M-05 da spec 003 só aparece na
  confirmação. Se o envio do link falhar, os demais campos continuam gravados, o e-mail não muda e
  o sistema exibe a MC-13 (provisória). O e-mail pendente fica num token assinado (dicionário,
  seção 4, regra 3), sem coluna nova. O FR-021 da spec 003 cobre só Aluno e Membro Externo; o plano
  estende o mecanismo a Docente e Secretaria (Assumptions).
- Q25 (redação de FR e SC): o FR-037 deixa claro o caso de cancelamentos e retiradas sem sessão
  válida (Q13); o FR-026 nomeia o convite sem resposta ('Aguardando Aceite' em `sol_status`); o
  FR-040 traz a mensagem de expiração da Q4; o SC-001 registra que o cenário 3 da US-06 depende da
  Q-52; o FR-009 e o FR-014 trazem a regra da Q5; o FR-036 aponta para o FR-042; o novo SC-009 cobre
  o RNF de Comportamento Temporal do RAN-CAD-14 (filtro em menos de 2 segundos).

Pontos da segunda conferência:

- Q26 (efeito da Q5; índice Q-64): um docente lotado num curso que coordena outro (ex.: lotado em SI,
  coordena LC) pertence a qual curso, para alteração e inativação? → A: segue a US-03: ao Curso de
  Lotação (pré-condição 5, A8, A11 e cenário 36; RBN-CAD-01.2, "docente do seu curso"). Quem o
  altera, inativa ou desmarca o seu papel de Coordenador (A10) é a Secretaria ou o Coordenador do
  Curso de Lotação. Se o Curso de Lotação for diferente do Curso Coordenado, ele não edita o próprio
  cadastro. O Curso Coordenado vale só para o alcance das ações dele como usuário e para o filtro
  padrão (FR-009). Decidido em 2026-10-22.
- Q27 (índice Q-65): a mesma pessoa pode voltar a ser Secretaria depois da inativação? O
  RBN-CAD-02.3 e a US-04 só preveem a inativação, e o e-mail continua único também nas contas
  inativas. → A: segue a US: a Secretaria não é reativada. A pessoa volta por um novo cadastro, com
  outro e-mail (Edge Cases). A reativação da Secretaria vai à PO como sugestão (índice S-03).
  Decidido em 2026-10-22.
- Q28 (consequência da Q17 e da Q-21 da spec 003; índice Q-66): numa segunda troca de e-mail pelo
  gestor, o link enviado na primeira continua valendo? → A: sim. O link vale até vencer (24 horas)
  ou até outro link da mesma conta ser confirmado, como na spec 003. O risco fica registrado nos
  Edge Cases, sem coluna nova. Decidido em 2026-10-22.

Pendências de outras pessoas (registradas no índice):

- Q29: a troca da M-16 pelo texto da US-06 no login é da spec 003 (Julia Cohen; Q-52). O ajuste do
  texto da Secretaria por curso no dicionário é da Maria Luiza Guimarães, e o do Glossário, da PO
  (Q-60). A correção do documento de US está na Q-61. As features de Defesa (Célio Benjamim; Q-67)
  e de Vida do TCC (Leandra Matos; Q-68) precisam ter ciência do que esta feature espera delas:
  recálculo da validade nos eventos de banca, atalho da US-23, listas de escolha só com docentes
  'Ativa' e rotina diária de expiração. Os textos MC-11 a MC-13 aguardam a PO (Q-58).

## User Scenarios & Testing *(mandatory)*

Os cenários reproduzem os cenários de aceite das US, com as mensagens exatas entre aspas. As
prioridades indicam só a ordem de entrega. Na matriz, US-03, US-05 e US-06 são Must Have, a US-04 é
Should Have (RBN-CAD-01.3 e 02.3; o cabeçalho da US-04 diz Must Have, correção no índice, Q-61). A
US-50 é Could Have no seu cabeçalho, mas a prorrogação faz parte do RBN-CAD-03.3, Must Have na
matriz; a prioridade está em aberto (índice Q-63).

### User Story 1 - Cadastrar, alterar e listar docentes e a Secretaria [US-03] (Priority: P1)

A Secretaria ou o Coordenador de Curso cadastra e altera Docentes do seu curso, inclusive o papel de
Coordenador de Curso. O Coordenador cadastra e altera a Secretaria do seu curso. Os dois consultam a
listagem de docentes com o filtro de Curso.

**Why this priority**: sem docentes não há turmas (spec 004), orientação nem bancas. Sem Secretaria,
o curso depende só do Coordenador. É a primeira coisa que o Coordenador faz depois da implantação.

**Atores e pré-condições** (US-03):

- Ator principal: Secretaria ou Coordenador de Curso (cadastra e altera Docente); Coordenador de
  Curso (cadastra e altera Secretaria).
- Atores secundários: Docente ou Secretaria cadastrado, que ativa a conta depois pelo primeiro
  acesso (US-10); login (US-11), que passa a reconhecer a conta; US-39, que fornece o filtro de
  Curso da listagem.
- Pré-condições: (1) o usuário está autenticado (US-11), com a conta ativa, como Secretaria ou
  Coordenador de Curso; (2) o usuário tem um curso associado: Curso Coordenado (Coordenador) ou
  Curso Vinculado (Secretaria); (3) os cursos do NUCOMP estão disponíveis nas listas suspensas; (4)
  para cadastrar ou alterar Secretaria, o usuário é o Coordenador do curso; (5) para alterar, o
  docente ou a Secretaria já está cadastrado e pertence ao curso do usuário (RBN-CAD-14.1).

**Independent Test**: com um Coordenador 'Ativa', cadastrar uma Secretaria e um docente comum, marcar
o papel de Coordenador em outro docente para um curso sem Coordenador, alterar os dados e conferir a
listagem com o filtro de Curso.

**Acceptance Scenarios** (US-03, cenários 1 a 40):

1. **Dado que** a Secretaria está autenticada e não existe o e-mail mlsg@uea.edu.br, **Quando**
   preenche Nome, E-mail, Titulação Doutor e Curso de Lotação, deixa Coordenador desmarcado e clica
   em "Salvar", **Então** o sistema cria a conta como Docente comum, com o Status da Conta "Aguardando
   Ativação", e exibe "Docente cadastrado com sucesso".
2. **Dado que** o Coordenador de Sistemas de Informação está autenticado, **Quando** cadastra um
   docente lotado em Sistemas de Informação e salva, **Então** o sistema cria a conta com o Status da
   Conta "Aguardando Ativação".
3. **Dado que** o curso Sistemas de Informação não tem Coordenador, **Quando** o usuário marca
   "Coordenador de Curso", seleciona Sistemas de Informação em Curso Coordenado e salva, **Então** o
   sistema cria o docente com o papel de Coordenador vinculado a esse curso.
4. **Dado que** o usuário marcou "Coordenador de Curso" e escolheu um Curso Coordenado, **Quando**
   desmarca o checkbox e salva, **Então** o campo Curso Coordenado some e o sistema cria o docente
   como Docente comum.
5. **Dado que** já existe um docente com o e-mail maria@uea.edu.br, **Quando** o usuário tenta
   cadastrar outro Docente ou uma Secretaria com esse e-mail, **Então** o sistema não salva e exibe
   "Este e-mail já está cadastrado".
6. **Dado que** o e-mail carlos@uea.edu.br pertence a um Membro Externo ou a um Aluno, **Quando** o
   usuário tenta cadastrar um Docente com esse e-mail, **Então** o sistema não salva e exibe "Este
   e-mail já está cadastrado".
7. **Dado que** o docente ana@uea.edu.br está com o Status da Conta Inativa, **Quando** o usuário tenta
   cadastrar um novo docente com esse e-mail, **Então** o sistema não salva e exibe "Este e-mail já
   está cadastrado" **E** o usuário deve reativar o docente existente (US-04).
8. **Dado que** o usuário está no formulário de Docente, **Quando** informa maria@gmail.com e clica em
   "Salvar", **Então** o sistema exibe "Informe um e-mail institucional (@uea.edu.br)" e não salva.
9. **Dado que** o usuário está no formulário de Docente, **Quando** informa "maria.uea.edu.br", sem
   arroba, e clica em "Salvar", **Então** o sistema exibe "Informe um e-mail institucional
   (@uea.edu.br)" e não salva.
10. **Dado que** o usuário está no formulário de Docente, **Quando** informa um e-mail de @uea.edu.br
    com 101 caracteres, **Então** o sistema exibe "Informe um e-mail institucional (@uea.edu.br)" e
    não salva.
11. **Dado que** o usuário está no formulário de Docente, **Quando** informa o nome "Maria Souza 2" e
    salva, **Então** o sistema exibe "O nome deve conter apenas letras e até 150 caracteres" e não
    salva.
12. **Dado que** o usuário está no formulário de Docente, **Quando** informa o nome "João Gonçalves
    Álvares" e, em outra tentativa, um nome com 151 caracteres, **Então** o sistema aceita o primeiro
    e rejeita o segundo com "O nome deve conter apenas letras e até 150 caracteres".
13. **Dado que** o usuário está no formulário de Docente, **Quando** clica em "Salvar" sem informar a
    Titulação, **Então** o sistema destaca o campo com "Campo obrigatório" e não salva.
14. **Dado que** o usuário marcou "Coordenador de Curso", **Quando** clica em "Salvar" sem escolher o
    Curso Coordenado, **Então** o sistema destaca o campo com "Campo obrigatório" e não salva.
15. **Dado que** o curso Sistemas de Informação já tem um Coordenador, **Quando** o usuário marca
    "Coordenador de Curso" e seleciona esse curso, **Então** o sistema exibe o alerta "O curso já
    possui Coordenador. Desmarque o papel no coordenador atual para continuar" e impede o cadastro
    até que o papel seja desmarcado no coordenador atual.
16. **Dado que** o usuário está no formulário de Docente, **Quando** a requisição envia a Titulação
    "Livre-docente", **Então** o sistema rejeita com "Selecione uma opção válida" e não salva.
17. **Dado que** a Secretaria de Sistemas de Informação está autenticada, **Quando** tenta cadastrar
    um docente com Curso de Lotação Engenharia de Computação, **Então** o sistema exibe "Você só pode
    cadastrar e alterar dados do seu curso" e não salva (Clarifications, Q5).
18. **Dado que** o Coordenador de Curso está autenticado e o curso escolhido não tem Secretaria,
    **Quando** informa Nome Completo, E-mail Institucional e Curso Vinculado e clica em "Salvar",
    **Então** o sistema cria a conta da Secretaria com o Status da Conta "Aguardando Ativação" e exibe
    "Secretaria cadastrada com sucesso".
19. **Dado que** o curso escolhido já tem uma Secretaria, **Quando** o Coordenador tenta cadastrar
    outra Secretaria para esse curso, **Então** o sistema não salva e exibe "O curso já possui
    Secretaria vinculada".
20. **Dado que** a Secretaria do curso foi inativada, **Quando** o Coordenador cadastra uma nova
    Secretaria para o curso, **Então** o sistema cria a nova conta e o curso volta a ter uma
    Secretaria ativa.
21. **Dado que** a Secretaria está autenticada, **Quando** acessa o menu Cadastros, **Então** o sistema
    não exibe a opção "Nova secretaria" e bloqueia o acesso direto à tela.
22. **Dado que** um Aluno, um Docente comum ou um Membro Externo está autenticado, **Quando** tenta
    abrir a tela de cadastro de docente pela URL, **Então** o sistema nega o acesso e exibe "Você não
    tem permissão para esta ação".
23. **Dado que** o usuário preencheu parte do formulário de Docente, **Quando** clica em "Cancelar",
    **Então** o sistema volta à listagem e nenhuma conta é criada.
24. **Dado que** a Secretaria de Sistemas de Informação está autenticada, **Quando** abre "Docentes",
    **Então** o sistema exibe os docentes do curso com Nome, E-mail, Titulação, Curso de Lotação,
    Papéis, Status da Conta e quantidade de orientandos.
25. **Dado que** a listagem está filtrada pelo curso do usuário, **Quando** o usuário escolhe "Todos"
    no filtro de Curso, **Então** o sistema lista os docentes dos três cursos.
26. **Dado que** o curso escolhido no filtro não tem docentes, **Quando** o sistema aplica o filtro,
    **Então** exibe "Nenhum registro".
27. **Dado que** o docente foi cadastrado e está com o Status da Conta "Aguardando Ativação",
    **Quando** tenta fazer login, **Então** o sistema nega o acesso com "Conta ainda não ativada" e
    oferece o link "Primeiro acesso" **E** o docente aparece na listagem com 0 orientandos.
28. **Dado que** o usuário preencheu o formulário corretamente, **Quando** o sistema não consegue
    gravar a conta, **Então** exibe "Não foi possível salvar. Tente novamente", não grava e mantém os
    dados no formulário.
29. **Dado que** o Coordenador abriu a edição de um docente do seu curso, **Quando** altera a
    Titulação para Doutor e clica em "Salvar", **Então** o sistema grava e exibe "Dados atualizados".
30. **Dado que** a Secretaria abriu a edição do docente João, **Quando** informa o e-mail de outro
    usuário, **Então** o sistema exibe "Este e-mail já está cadastrado" e não grava.
31. **Dado que** a Secretaria abriu a edição de um docente, **Quando** informa o nome "João 2" ou um
    e-mail fora de @uea.edu.br, **Então** o sistema exibe a mensagem do campo e não grava.
32. **Dado que** o docente já tem o Status da Conta Ativa, **Quando** a Secretaria altera o e-mail para
    novo@uea.edu.br, confirma com a própria senha e salva, **Então** o sistema envia um link de
    confirmação para novo@uea.edu.br e o e-mail antigo continua sendo o login **E**, depois que o
    link é confirmado, o novo e-mail passa a ser o login e a senha existente continua valendo
    (Clarifications, Q17).
33. **Dado que** o curso Licenciatura em Computação não tem Coordenador, **Quando** o Coordenador de
    Curso edita um docente, marca o papel e escolhe esse curso, **Então** o sistema grava o docente
    como Coordenador desse curso.
34. **Dado que** o curso já tem um Coordenador, **Quando** o usuário marca o papel em outro docente
    desse curso e salva, **Então** o sistema exibe o alerta e não grava.
35. **Dado que** o docente é o Coordenador do curso, **Quando** o usuário desmarca o papel e salva,
    **Então** o docente vira Docente comum e o curso passa a aceitar um novo Coordenador.
36. **Dado que** a Secretaria abriu a edição de um docente do seu curso, **Quando** altera o Curso de
    Lotação e salva, **Então** o sistema grava e o docente passa a aparecer na listagem do novo curso.
37. **Dado que** o Coordenador de Curso abriu a edição da Secretaria, **Quando** corrige o Nome
    Completo e salva, **Então** o sistema grava e exibe "Dados atualizados".
38. **Dado que** o curso Engenharia de Computação já tem uma Secretaria, **Quando** o Coordenador
    altera o Curso Vinculado de outra Secretaria para esse curso, **Então** o sistema exibe "O curso já
    possui Secretaria vinculada" e não grava.
39. **Dado que** o usuário filtrou os docentes de outro curso pelo filtro, **Quando** tenta editar um
    desses docentes, **Então** o sistema não exibe o botão "Editar" e, no acesso direto, exibe "Você só
    pode cadastrar e alterar dados do seu curso".
40. **Dado que** a Secretaria está autenticada, **Quando** abre a lista de Secretarias, **Então** o
    sistema não exibe "Editar" e bloqueia o acesso direto à ação.

---

### User Story 2 - Cadastrar e alterar membros externos [US-05] (Priority: P1)

O Orientador, o Professor da Disciplina, a Secretaria ou o Coordenador de Curso cadastra e altera
avaliadores de fora do NUCOMP, com e-mail de qualquer domínio, para que possam compor bancas.

**Why this priority**: a composição da banca (US-23) precisa de Membros Externos cadastrados, e a
validade do acesso (história 4) parte do cadastro.

**Atores e pré-condições** (US-05):

- Ator principal: Orientador, Professor da Disciplina, Secretaria ou Coordenador de Curso.
- Atores secundários: Membro Externo (avaliador de fora do NUCOMP ou da UEA), que ativa a conta
  pelo primeiro acesso (US-10); composição da banca (US-23), de onde parte o cadastro pelo atalho;
  regra de validade do acesso (US-06).
- Pré-condições: (1) o usuário está autenticado (US-11) com um dos perfis acima e com a conta
  ativa; (2) para cadastrar pelo atalho, o usuário está compondo uma banca (US-23) e o avaliador
  externo desejado não aparece na lista; (3) para alterar dados, o Membro Externo já está
  cadastrado.

**Independent Test**: com uma Secretaria 'Ativa', cadastrar um membro com e-mail de outro domínio,
alterar a Titulação e o e-mail, e conferir as recusas de e-mail duplicado e de campos inválidos.

**Acceptance Scenarios** (US-05, cenários 1 a 23):

1. **Dado que** o Orientador está autenticado e o e-mail ana@ufam.edu.br não existe, **Quando**
   informa Nome, E-mail, Titulação Doutor e Instituição de Origem e clica em "Salvar", **Então** o
   sistema cria a conta com o Status da Conta "Aguardando Ativação" e exibe "Membro externo cadastrado
   com sucesso".
2. **Dado que** o Professor da Disciplina, a Secretaria ou o Coordenador de Curso está autenticado,
   **Quando** cadastra um Membro Externo com dados válidos, **Então** o sistema cria a conta com o
   Status da Conta "Aguardando Ativação".
3. **Dado que** o usuário está no formulário de Membro Externo, **Quando** informa o e-mail
   carlos@empresa.com.br e preenche os demais campos, **Então** o sistema aceita o e-mail e cadastra o
   membro.
4. **Dado que** já existe um usuário com o e-mail luisa@ufam.edu.br, **Quando** o usuário tenta
   cadastrar outro membro com esse e-mail, **Então** o sistema não salva e exibe "Este e-mail já está
   cadastrado".
5. **Dado que** o membro luisa@ufam.edu.br tem a conta expirada, **Quando** o usuário tenta cadastrá-lo
   de novo, **Então** o sistema exibe "Este e-mail já está cadastrado" e o usuário deve selecioná-lo
   na banca ou prorrogar o acesso (US-06, US-50).
6. **Dado que** o usuário está no formulário de Membro Externo, **Quando** informa "ana.ufam.edu.br" e
   clica em "Salvar", **Então** o sistema exibe "Informe um e-mail válido" e não salva.
7. **Dado que** o usuário está no formulário de Membro Externo, **Quando** informa um e-mail com 101
   caracteres, **Então** o sistema exibe "Informe um e-mail válido" e não salva.
8. **Dado que** o usuário está no formulário de Membro Externo, **Quando** clica em "Salvar" sem
   informar a Instituição de Origem, **Então** o sistema destaca o campo com "Campo obrigatório" e não
   salva.
9. **Dado que** o usuário está no formulário de Membro Externo, **Quando** deixa o Nome ou a Titulação
   em branco e clica em "Salvar", **Então** o sistema destaca o campo com "Campo obrigatório" e não
   salva.
10. **Dado que** o usuário está no formulário de Membro Externo, **Quando** informa o nome "Ana Souza
    2" e clica em "Salvar", **Então** o sistema exibe "O nome deve conter apenas letras e até 150
    caracteres" e não salva.
11. **Dado que** o usuário está no formulário de Membro Externo, **Quando** informa a instituição
    "Univ. Federal do Amazonas (UFAM) - Campus 2", **Então** o sistema aceita o texto e salva.
12. **Dado que** o usuário está no formulário de Membro Externo, **Quando** informa uma instituição com
    151 caracteres, **Então** o sistema exibe "Informe a instituição com até 150 caracteres" e não
    salva.
13. **Dado que** o usuário está no formulário de Membro Externo, **Quando** a requisição envia a
    Titulação "Livre-docente", **Então** o sistema rejeita com "Selecione uma opção válida" e não
    salva.
14. **Dado que** o usuário está compondo a banca (US-23) e o avaliador não está na lista, **Quando**
    cadastra o membro externo pelo atalho e salva, **Então** o sistema volta à banca com o novo membro
    selecionado.
15. **Dado que** o usuário abriu o cadastro pelo atalho da banca, **Quando** clica em "Cancelar",
    **Então** o sistema volta à composição da banca sem criar conta.
16. **Dado que** o Membro Externo já está cadastrado, **Quando** o Orientador corrige a Titulação e
    salva, **Então** o sistema grava e exibe "Dados atualizados".
17. **Dado que** o membro já ativou a conta, **Quando** a Secretaria altera o e-mail para
    novo@ufam.edu.br, confirma com a própria senha e salva, **Então** o sistema envia um link de
    confirmação para novo@ufam.edu.br e o e-mail antigo continua sendo o login **E**, depois que o
    link é confirmado, o novo e-mail passa a ser o login e a senha existente continua valendo
    (Clarifications, Q17).
18. **Dado que** o usuário abriu a edição de um membro, **Quando** informa um e-mail já usado por
    outro usuário ou um nome com números, **Então** o sistema não grava e mantém os dados anteriores.
19. **Dado que** a conta do membro está expirada, **Quando** o Coordenador corrige a Instituição de
    Origem e salva, **Então** o sistema grava a alteração e o acesso continua bloqueado.
20. **Dado que** o membro foi cadastrado em 01/10/2026 e não está em nenhuma banca, **Quando** o
    sistema define a validade do acesso, **Então** a conta vale até 31/10/2026 (Clarifications,
    Q12).
21. **Dado que** um Aluno está autenticado, **Quando** tenta acessar a tela de membros externos,
    **Então** o sistema nega o acesso e exibe "Você não tem permissão para esta ação".
22. **Dado que** um Docente sem papel de Orientador, Professor da Disciplina ou Coordenador está
    autenticado, **Quando** abre o menu lateral, **Então** o sistema não exibe "Membros externos" e
    bloqueia o acesso direto à tela.
23. **Dado que** o usuário preencheu o formulário corretamente, **Quando** o sistema não consegue
    gravar, **Então** exibe "Não foi possível salvar. Tente novamente" e mantém os dados no
    formulário.

---

### User Story 3 - Inativar e reativar docentes e a Secretaria [US-04] (Priority: P2)

A Secretaria ou o Coordenador inativa docentes do seu curso que deixaram de atuar, desde que não
tenham vínculos em aberto, e os reativa quando voltam. O Coordenador inativa a Secretaria do seu
curso, o que libera o curso para uma nova Secretaria.

**Why this priority**: mantém a segurança (quem saiu não entra mais) sem apagar o histórico. Depende
da história 1 (contas existentes).

**Atores e pré-condições** (US-04):

- Ator principal: Secretaria ou Coordenador de Curso (inativar ou reativar Docente); Coordenador de
  Curso (inativar Secretaria).
- Atores secundários: Docente ou Secretaria afetado; módulos de orientação e coorientação (US-17,
  US-18, US-36 e US-45), banca (US-21 e US-23) e turmas (US-07), consultados para verificar os
  vínculos; login (US-11); listagem de docentes (US-03); filtro de Curso (US-39).
- Pré-condições: (1) o usuário está autenticado (US-11) como Secretaria ou Coordenador de Curso,
  com a conta ativa; (2) o docente ou a Secretaria pertence ao curso do usuário (RBN-CAD-14.1); (3)
  para inativar, o Status da Conta está Ativa; para reativar docente, está Inativa; (4) para
  inativar a Secretaria, o usuário é o Coordenador do curso.

**Independent Test**: inativar um docente sem vínculos, ver o login negado com "Conta inativa",
reativá-lo; tentar inativar um docente com cada tipo de vínculo e ver o motivo; inativar a
Secretaria e cadastrar outra para o curso.

**Acceptance Scenarios** (US-04, cenários 1 a 25):

1. **Dado que** o docente não tem orientandos ativos, convites pendentes, bancas em aberto, turmas não
   arquivadas nem o papel de Coordenador, **Quando** a Secretaria clica em "Inativar" e confirma,
   **Então** o sistema muda o Status da Conta para "Inativa" e exibe "Docente inativado" **E** o
   docente deixa de aparecer nas listas de orientador e de avaliador.
2. **Dado que** o docente é orientador de um aluno com TCC Em Andamento, **Quando** o usuário clica em
   "Inativar", **Então** o sistema não inativa e exibe o alerta "orientandos com TCC ativo".
3. **Dado que** o docente é coorientador de um aluno com TCC Apto para Defesa, **Quando** o usuário
   clica em "Inativar", **Então** o sistema não inativa e exibe o alerta "coorientandos com TCC
   ativo".
4. **Dado que** o docente orienta um TCC Aprovado com Correções cuja Versão Final ainda não foi
   homologada, **Quando** o usuário clica em "Inativar", **Então** o sistema não inativa e informa que
   o TCC ainda é ativo.
5. **Dado que** o docente recebeu um convite de coorientação e ainda não respondeu, **Quando** o
   usuário clica em "Inativar", **Então** o sistema não inativa e informa o convite pendente.
6. **Dado que** o docente é membro de uma banca com sessão Agendada, **Quando** o usuário clica em
   "Inativar", **Então** o sistema não inativa e informa a banca em aberto.
7. **Dado que** o docente é membro de uma banca Reagendada ou Em Andamento, **Quando** o usuário clica
   em "Inativar", **Então** o sistema não inativa e informa a banca em aberto.
8. **Dado que** o docente é Professor da Disciplina de uma turma que não foi arquivada, **Quando** o
   usuário clica em "Inativar", **Então** o sistema não inativa e informa a turma.
9. **Dado que** o docente é Coordenador do curso Sistemas de Informação, **Quando** o usuário clica em
   "Inativar", **Então** o sistema não inativa e informa que o docente é Coordenador de Curso.
10. **Dado que** o docente tem orientandos ativos e uma turma não arquivada, **Quando** o usuário clica
    em "Inativar", **Então** o alerta lista os dois motivos, para que o usuário saiba tudo o que
    precisa encerrar.
11. **Dado que** o único orientando do docente está com o TCC Sem Proposta, **Quando** o usuário
    clica em "Inativar" e confirma, **Então** o sistema inativa o docente (Clarifications, Q16).
12. **Dado que** o docente só tem orientandos com TCC Concluído, Reprovado, Desistente ou Jubilado,
    bancas Realizadas ou Canceladas, convites respondidos e turmas arquivadas, **Quando** o usuário
    clica em "Inativar" e confirma, **Então** o sistema inativa o docente.
13. **Dado que** o docente é Coordenador e não tem outros vínculos, **Quando** o usuário desmarca o
    papel na US-03 e, depois, clica em "Inativar" e confirma, **Então** o sistema inativa o docente e o
    curso fica sem Coordenador até novo cadastro.
14. **Dado que** o usuário clicou em "Inativar" em um docente sem vínculos, **Quando** cancela na
    confirmação, **Então** o Status da Conta continua Ativa e nada é alterado.
15. **Dado que** o docente estava sem vínculos quando o usuário abriu a confirmação, **Quando** um aluno
    envia um convite de coorientação ao docente antes de o usuário confirmar, **Então** o sistema
    bloqueia a inativação e informa o convite pendente.
16. **Dado que** o docente foi inativado, **Quando** ele tenta fazer login e a Coordenação consulta os
    relatórios antigos, **Então** o sistema nega o acesso com "Conta inativa" **E** os TCCs, bancas e
    atas anteriores do docente continuam visíveis.
17. **Dado que** o docente está com o Status da Conta Inativa, **Quando** o usuário abre a listagem,
    **Então** o botão "Inativar" não aparece e aparece o botão "Reativar".
18. **Dado que** a Secretaria de Sistemas de Informação filtra por Engenharia de Computação, **Quando**
    tenta inativar ou reativar um docente desse curso, **Então** o sistema não exibe as ações e, no
    acesso direto, exibe "Você só pode alterar dados do seu curso".
19. **Dado que** o docente do curso do usuário está com o Status da Conta Inativa, **Quando** o usuário
    clica em "Reativar" e confirma, **Então** o Status volta a Ativa, o docente volta a fazer login e a
    aparecer nas listas de orientador e avaliador.
20. **Dado que** o docente Inativo pertence a outro curso, **Quando** o usuário tenta reativá-lo,
    **Então** o sistema não exibe o botão "Reativar" e bloqueia a ação direta.
21. **Dado que** o curso tem uma Secretaria com Status da Conta Ativa, **Quando** o Coordenador clica
    em "Inativar" e confirma, **Então** o Status passa a Inativa, a conta perde o login e mantém o
    histórico.
22. **Dado que** a Secretaria do curso está Inativa, **Quando** o Coordenador cadastra uma nova
    Secretaria para o curso (US-03), **Então** o sistema aceita o cadastro.
23. **Dado que** a Secretaria está autenticada, **Quando** abre a lista de Secretarias, **Então** o
    sistema não exibe "Inativar" e bloqueia o acesso direto à ação.
24. **Dado que** um Aluno está autenticado, **Quando** tenta abrir a tela de docentes pela URL,
    **Então** o sistema nega o acesso e exibe "Você não tem permissão para esta ação".
25. **Dado que** o usuário confirmou a inativação de um docente sem vínculos, **Quando** o sistema não
    consegue gravar, **Então** exibe "Não foi possível salvar. Tente novamente" e o docente continua
    com o Status Ativa.

---

### User Story 4 - Validade e expiração do acesso do Membro Externo [US-06] (Priority: P2)

O sistema calcula a validade do acesso de cada Membro Externo a partir das bancas em que ele está
(data da defesa mais distante + 7 dias corridos) ou, sem banca, a partir do cadastro (30 dias). Ele
renova a validade quando há nova banca ou reagendamento e muda a conta para 'Expirada' quando a
validade termina, sem apagar os dados.

**Why this priority**: é a regra de segurança das contas externas (RNF de Integridade do RAN-CAD-03).
Os gatilhos de banca vêm da feature de Defesa (US-21, US-23, US-24). Esta feature entrega a regra e a
expiração.

**Atores e pré-condições** (US-06):

- Ator principal: Sistema, que calcula a validade e muda o Status da Conta.
- Atores secundários: módulo de bancas (US-21, US-23 e US-24: vínculo, reagendamento e cancelamento
  da sessão); login (US-11); Membro Externo; cadastro do membro (US-05); prorrogação manual (US-50).
- Pré-condições: (1) o Membro Externo está cadastrado (US-05); (2) para a validade da defesa, o
  membro está vinculado a uma banca (US-23) com sessão que não esteja Cancelada.

**Independent Test**: com sessões de defesa e bancas criadas direto nos dados, calcular a validade
para cada caso (defesa mais distante, sessão cancelada, reagendamento, sem banca) e conferir o login
antes e depois da validade e a troca do status para 'Expirada'.

**Acceptance Scenarios** (US-06, cenários 1 a 18):

1. **Dado que** o membro externo está vinculado a uma defesa Agendada para 20/10/2026, **Quando** o
   sistema calcula a validade do acesso, **Então** a conta fica ativa até 27/10/2026.
2. **Dado que** a validade do membro termina em 27/10/2026, **Quando** ele faz login em 27/10/2026
   com e-mail e senha corretos, **Então** o sistema permite o acesso.
3. **Dado que** a validade do membro externo terminou em 27/10/2026, **Quando** ele tenta fazer login
   em 28/10/2026 com e-mail e senha corretos, **Então** o Status da Conta passa a Expirada, o sistema
   nega o acesso e exibe "Seu acesso expirou. Procure a coordenação do curso" (Clarifications, Q4).
4. **Dado que** a conta do membro externo expirou, **Quando** a Coordenação consulta bancas e
   relatórios do período, **Então** os dados cadastrais e a participação do membro continuam
   visíveis.
5. **Dado que** o membro tem defesas Agendadas em 20/10/2026 e 05/11/2026, **Quando** o sistema
   calcula a validade, **Então** a conta vale até 12/11/2026, contada da defesa mais distante.
6. **Dado que** o membro tem uma defesa Cancelada em 25/10/2026 e outra Agendada em 15/10/2026,
   **Quando** o sistema calcula a validade, **Então** a conta vale até 22/10/2026.
7. **Dado que** a única defesa do membro, marcada para 20/10/2026, foi cancelada em 12/10/2026,
   **Quando** o sistema recalcula a validade, **Então** a conta vale até 19/10/2026.
8. **Dado que** o Status da Conta do membro externo é Expirada, **Quando** ele é vinculado a uma nova
   banca com defesa em 10/11/2026, **Então** o Status volta a Ativa até 17/11/2026, sem novo
   cadastro.
9. **Dado que** a conta do membro vale até 27/10/2026, **Quando** ele é vinculado a uma nova banca com
   defesa em 05/11/2026, **Então** a validade passa para 12/11/2026.
10. **Dado que** a defesa do membro foi reagendada de 20/10/2026 para 03/11/2026, **Quando** o sistema
    recebe o reagendamento, **Então** a validade passa para 10/11/2026.
11. **Dado que** a defesa do membro foi reagendada de 20/10/2026 para 15/10/2026, **Quando** o sistema
    recebe o reagendamento, **Então** a validade passa para 22/10/2026.
12. **Dado que** o membro externo foi cadastrado em 01/10/2026 e não está em nenhuma banca, **Quando**
    tenta fazer login em 05/11/2026, **Então** o sistema nega o acesso, porque a validade de 30 dias
    terminou em 31/10/2026.
13. **Dado que** o membro foi cadastrado em 01/10/2026 e não está em nenhuma banca, **Quando** faz
    login em 10/10/2026, **Então** o sistema permite o acesso.
14. **Dado que** o membro foi cadastrado em 01/10/2026 e vinculado em 20/10/2026 a uma defesa de
    10/11/2026, **Quando** o sistema recalcula a validade, **Então** a conta vale até 17/11/2026.
15. **Dado que** a defesa do membro foi Realizada em 20/10/2026, **Quando** o sistema mantém a
    validade, **Então** a conta continua valendo até 27/10/2026.
16. **Dado que** o acesso do membro foi renovado por nova banca, **Quando** ele faz login com o e-mail
    e a senha de antes, **Então** o sistema permite o acesso sem novo cadastro.
17. **Dado que** o membro foi removido de uma banca Agendada antes da sessão, **Quando** o sistema
    recalcula a validade, **Então** a validade deixa de considerar essa sessão **E**, se não sobrar
    nenhuma sessão válida, a conta vale até 7 dias corridos após a data da retirada
    (Clarifications, Q13).
18. **Dado que** uma banca do membro foi reagendada, **Quando** o sistema não consegue recalcular a
    validade, **Então** mantém a validade anterior e registra o erro.

---

### User Story 5 - Prorrogar o acesso de membro externo [US-50] (Priority: P3)

O Orientador do TCC cuja banca inclui o Membro Externo, o Professor da Disciplina, a Secretaria ou o
Coordenador de Curso prorroga por mais 7 dias corridos o acesso do membro, para que ele continue
entrando depois do fim da validade.

**Why this priority**: Could Have no cabeçalho da US-50 (Must Have pelo RBN-CAD-03.3 da matriz;
em aberto, Q-63); cobre o caso em que o membro precisa de acesso depois do
prazo automático (por exemplo, para assinar a avaliação). Depende das histórias 2 e 4.

**Atores e pré-condições** (US-50):

- Ator principal: Orientador do TCC cuja banca inclui o Membro Externo.
- Atores secundários: Professor da Disciplina da turma, Secretaria e Coordenador de Curso, que
  prorrogam pelo mesmo fluxo (fluxo alternativo C), e Membro Externo, que volta a fazer login com a
  conta Ativa.
- Pré-condições: (1) o usuário está autenticado, com o Status da Conta Ativa (US-11); sem sessão
  ativa, aplica-se o E1; (2) o usuário é Orientador do TCC cuja banca inclui o Membro Externo,
  Professor da Disciplina (com turma não arquivada; Clarifications, Q10 e Q11), Secretaria ou
  Coordenador de Curso; caso contrário, aplica-se o E2; (3) o Membro Externo está cadastrado
  (US-05), com o Status da Conta Ativa ou Expirada; com a conta Aguardando Ativação, aplica-se o E3.

**Independent Test**: na tela Membros externos, prorrogar uma conta 'Ativa' e uma 'Expirada' e
conferir a nova validade, o status e o login do membro; conferir que o botão não aparece para quem
não pode e para a conta 'Aguardando Ativação'.

**Acceptance Scenarios** (US-50, cenários 1 a 9):

1. **Dado que** o Orientador está na tela Membros externos e a conta de um membro da banca do seu
   orientando vale até 27/10/2026, **Quando** aciona o botão Prorrogar na linha desse membro,
   **Então** a validade passa para 03/11/2026 e o sistema exibe "Acesso prorrogado até 03/11/2026".
2. **Dado que** o Status da Conta do membro é Expirada desde 01/10/2026 e hoje é 06/10/2026, **Quando**
   o Orientador aciona o botão Prorrogar, **Então** a validade passa para 13/10/2026 e o Status da
   Conta volta a Ativa **E** o membro faz login com o mesmo e-mail e a mesma senha.
3. **Dado que** a conta do membro vale até 27/10/2026, **Quando** o Orientador aciona o botão
   Prorrogar duas vezes, **Então** a validade passa para 10/11/2026.
4. **Dado que** a Secretaria está autenticada e abre a tela Membros externos, **Quando** aciona o botão
   Prorrogar na linha de um membro com a conta Ativa, **Então** o sistema soma 7 dias corridos à
   validade e exibe a nova validade.
5. **Dado que** o Orientador não está autenticado, **Quando** tenta abrir a tela Membros externos,
   **Então** o sistema exibe a tela de login (US-11) **E**, após o login, abre a tela Membros
   externos.
6. **Dado que** o Orientador não orienta o TCC da banca do membro, **Quando** abre a tela Membros
   externos, **Então** o botão Prorrogar não aparece na linha desse membro.
7. **Dado que** um Aluno está autenticado, **Quando** abre o endereço da ação de prorrogar, **Então** o
   sistema exibe "Você não tem permissão para esta ação" e não altera a validade.
8. **Dado que** o membro ainda não criou a senha, **Quando** o Orientador abre a tela Membros
   externos, **Então** o botão Prorrogar não aparece na linha desse membro.
9. **Dado que** o Orientador acionou o botão Prorrogar, **Quando** o sistema não consegue gravar a
   nova validade, **Então** exibe "Não foi possível prorrogar o acesso. Tente novamente" e mantém a
   validade anterior.

---

### User Story 6 - Criar os Coordenadores de Curso na implantação [RAN-CAD-01, Instalabilidade] (Priority: P1)

Na instalação, a pessoa que implanta o sistema roda um comando que cria a conta do Coordenador de
Curso de cada curso do NUCOMP. A partir dessas contas, os demais cadastros são feitos pelas telas.

**Why this priority**: sem um primeiro Coordenador não há quem cadastre Secretaria e docentes. O
sistema não tem tela de administrador.

**Independent Test**: num banco recém-instalado, rodar o comando para os três cursos, fazer o
primeiro acesso de um Coordenador (spec 003) e, com ele, cadastrar uma Secretaria e um docente.

**Acceptance Scenarios** (derivados do RNF de Instalabilidade do RAN-CAD-01; sem cenário na US):

1. **Dado que** o sistema foi instalado e nenhum curso tem Coordenador, **Quando** a pessoa que
   implanta roda o comando com Nome Completo, E-mail Institucional e Titulação do Coordenador de cada
   um dos três cursos, **Então** o sistema cria três contas de Docente com o Status da Conta
   "Aguardando Ativação", cada uma lotada no curso que coordena e com o papel de Coordenador desse
   curso, e não envia nenhum e-mail.
2. **Dado que** a conta do Coordenador foi criada pelo comando, **Quando** ele faz o "Primeiro
   acesso" com o e-mail cadastrado, **Então** recebe o link de ativação (RBN-CAD-06.2) e, depois de
   criar a senha, entra e vê o menu Cadastros.
3. **Dado que** o curso Sistemas de Informação já tem Coordenador, **Quando** o comando é rodado de
   novo para esse curso, **Então** o sistema não cria outra conta, informa que o curso já tem
   Coordenador e continua com os demais cursos.
4. **Dado que** o e-mail informado já pertence a outra conta, ou está fora de @uea.edu.br, ou o nome
   ou a Titulação estão fora das regras, **Quando** o comando é rodado, **Então** o sistema não cria
   a conta desse curso e informa o motivo, com o mesmo texto das telas de cadastro.

---

### Edge Cases

- **Cadastros simultâneos**: duas pessoas cadastram ao mesmo tempo o mesmo e-mail, o Coordenador do
  mesmo curso ou a Secretaria do mesmo curso. Só o primeiro é gravado. O segundo recebe a mensagem da
  regra ("Este e-mail já está cadastrado", "O curso já possui Coordenador..." ou "O curso já possui
  Secretaria vinculada") (US-03 E3).
- **E-mail com maiúsculas ou espaços**: "Maria@UEA.edu.br " é o mesmo e-mail que "maria@uea.edu.br"
  na verificação de unicidade (spec 003, Q13). O e-mail é gravado normalizado.
- **E-mail alterado pelo gestor** (US-03 A11, US-05 A3; Clarifications, Q17): como na troca feita
  pela própria pessoa no perfil (spec 003, US-38), o novo e-mail só passa a ser o login depois que
  o link enviado a ele é confirmado. Além disso, quem altera confirma a troca com a própria senha.
  Vale também para a conta 'Aguardando Ativação' corrigida pelo gestor.
- **Duas trocas de e-mail seguidas** (Clarifications, Q28): o link enviado na primeira troca continua
  valendo até vencer (24 horas) ou até outro link da mesma conta ser confirmado. Se o gestor digitar
  um e-mail errado e corrigir, quem receber o primeiro link pode confirmá-lo. Risco aceito: o gestor
  confere o endereço antes de salvar.
- **Coordenador que desmarca o próprio papel**: é permitido (US-03 A10) quando ele é lotado no curso
  que coordena, porque o registro dele é do seu curso (Clarifications, Q26). Ele perde o acesso de
  Coordenador na próxima página, e o curso fica sem Coordenador. A Secretaria do curso continua
  podendo cadastrar docentes e marcar um novo Coordenador.
- **Docente que coordena outro curso que não o de lotação**: o curso dele, para o alcance das ações e
  para o filtro padrão, é o Curso Coordenado (RBN-CAD-14.1). O registro dele, porém, pertence ao
  Curso de Lotação: só a Secretaria e o Coordenador desse curso o alteram, inativam ou desmarcam o
  seu papel; ele mesmo não edita o próprio cadastro (Clarifications, Q26).
- **Troca de Curso Coordenado**: marcar outro curso sem Coordenador para quem já é Coordenador
  libera o curso anterior. Um docente coordena no máximo um curso (dicionário, `Coordenadores`).
- **Conta 'Aguardando Ativação'**: docente ou Secretaria que ainda não criou a senha não tem
  "Inativar" nem "Reativar" (pré-condição da US-04). Pode ser alterado, inclusive no e-mail, para
  corrigir um cadastro errado. A Secretaria 'Aguardando Ativação' ocupa o curso (Clarifications, Q7;
  mantido na Q-49 do índice).
- **Secretaria inativada que precisa voltar** (Clarifications, Q27): não há reativação de
  Secretaria (RBN-CAD-02.3, US-04). Como o e-mail da conta inativa continua ocupado (FR-001), a
  mesma pessoa só volta por um novo cadastro (US-03 A4), com outro e-mail. A conta antiga continua
  'Inativa', com o histórico.
- **Ação pelo endereço direto com status incompatível** (US-04 E10): inativar quem já está
  'Inativa' ou reativar quem está 'Ativa' é recusado sem alterar nada (MC-10).
- **Vínculo que surge durante a confirmação** (US-04 E7): a verificação é repetida na confirmação,
  dentro da mesma gravação. Se aparecer um vínculo, nada é alterado e o motivo é exibido.
- **Docente inativo com turmas arquivadas, orientações encerradas ou bancas realizadas**: continua
  aparecendo nesses registros e relatórios. Só sai das listas de escolha de orientador, coorientador
  e avaliador.
- **Membro 'Ativa' com a validade vencida, antes da troca automática para 'Expirada'**: é tratado
  como 'Expirada' em tudo: login negado (spec 003, Q4), status exibido como Expirada e prorrogação
  contada a partir de hoje.
- **Membro sem validade gravada** (contas antigas ou de teste): na prorrogação, a contagem parte de
  hoje.
- **Membro 'Aguardando Ativação' com a validade de 30 dias vencida**: não tem o botão Prorrogar
  (US-50 E3). O primeiro acesso mostra a mensagem de expiração (spec 003, Q26). Ele volta a ter
  validade quando é vinculado a uma banca (US-06 A1).
- **Recálculo depois de uma prorrogação manual** (Q15): a validade fica com a data mais tardia entre
  o resultado da regra de banca e a data dada pela última prorrogação. Exemplo: defesa em 20/10
  (validade 27/10), prorrogada duas vezes (10/11) e depois reagendada para 22/10. A regra de banca
  daria 29/10, mas a validade continua 10/11. Se a defesa fosse reagendada para 15/11, a validade
  passaria a 22/11.
- **Membro em várias bancas, com uma Cancelada e outra Realizada**: a Cancelada não conta. A
  Realizada conta pela data da defesa (US-06 A6).
- **Alteração de membro expirado** (US-05 A6): grava os dados e não reabre o acesso.
- **Lista vazia**: as listas de Secretarias e de Membros externos sem registros exibem "Nenhum
  registro", como a de docentes (US-03 A7).

## Requirements *(mandatory)*

### Functional Requirements

**Regras comuns aos cadastros [US-03][US-05][RAN-CAD-01 a 03]**

- **FR-001**: O e-mail DEVE ser único em todo o sistema, para Docente, Secretaria, Membro Externo e
  Aluno, inclusive contas 'Inativa' e 'Expirada', sem diferenciar maiúsculas e minúsculas e mesmo em
  cadastros feitos ao mesmo tempo. Repetição: "Este e-mail já está cadastrado", sem salvar. Vale no
  cadastro e na alteração (a própria conta não conta como repetição).
- **FR-002**: Nome Completo DEVE aceitar só letras (com acentos) e espaços, com até 150 caracteres.
  Fora disso: "O nome deve conter apenas letras e até 150 caracteres", sem salvar.
- **FR-003**: Campo obrigatório vazio DEVE ser destacado com "Campo obrigatório", sem salvar.
- **FR-004**: Titulação (Especialista, Mestre ou Doutor) e os cursos (Engenharia de Computação,
  Sistemas de Informação e Licenciatura em Computação) DEVEM ser escolhidos em listas suspensas.
  Valor fora da lista, mesmo enviado direto na requisição: "Selecione uma opção válida", sem salvar.
- **FR-005**: Toda conta criada por esta feature DEVE ficar com o Status da Conta 'Aguardando
  Ativação', sem senha, e **nenhum** link de ativação é enviado (Clarifications, Q1). A pessoa ativa
  a conta pelo "Primeiro acesso" da spec 003 (RBN-CAD-06.2) e, até lá, o login responde "Conta ainda
  não ativada".
- **FR-006**: Falha ao gravar DEVE exibir "Não foi possível salvar. Tente novamente", sem gravar nada e
  com o formulário ainda preenchido.
- **FR-007**: "Cancelar" DEVE descartar o preenchimento, sem criar nem alterar conta, e voltar à
  listagem (ou à tela de origem, no atalho da banca).
- **FR-008**: Na alteração do e-mail feita pelo gestor (Docente, Secretaria ou Membro Externo), o
  formulário DEVE pedir a senha de quem altera. Senha errada: MC-11, sem salvar nada. No formulário,
  o novo e-mail passa pelas validações do cadastro, e o e-mail já usado por outra conta mostra "Este
  e-mail já está cadastrado" (FR-001). Com a senha correta, os demais campos são gravados e o novo
  e-mail recebe um link de confirmação, pelo mesmo mecanismo da troca de e-mail da spec 003 (FR-021:
  validade de 24 horas, M-07 e M-09; M-05 só na confirmação, se o e-mail tiver passado a outra conta
  nesse meio-tempo), e o sistema exibe MC-12. Se o envio do link falhar, os demais campos continuam
  gravados, o e-mail não muda e o sistema exibe a MC-13 (Clarifications, Q24). O e-mail da conta só muda depois que o link
  é confirmado; até lá, o e-mail antigo continua sendo o login. Depois da confirmação, a conta
  mantém a mesma senha e o mesmo histórico (Clarifications, Q17 e Q24; dicionário, seção 4, regra
  3).
- **FR-009**: As ações sobre Docente e Secretaria DEVEM ficar restritas ao curso do usuário
  (RBN-CAD-14.1; Clarifications, Q5). O curso do usuário é o Curso Coordenado do Coordenador ou o
  Curso Vinculado da Secretaria. O Curso Coordenado escolhido no cadastro ou na alteração de um
  docente pode ser qualquer curso do NUCOMP sem Coordenador (US-03 cenário 33; Clarifications, Q5;
  índice Q-55). O docente pertence ao seu Curso de Lotação, mesmo quando coordena outro curso
  (Clarifications, Q26). Fora do curso, os botões não aparecem, e o acesso direto é recusado,
  sem gravar, com "Você só pode cadastrar e alterar dados do seu curso" (cadastro e alteração, US-03
  E8) ou "Você só pode alterar dados do seu curso" (inativação e reativação, US-04 cenário 18).
- **FR-010**: Perfil sem permissão DEVE ficar sem o item de menu e sem os botões da ação. O acesso
  direto pelo endereço DEVE ser recusado com "Você não tem permissão para esta ação", sem gravar
  (Clarifications, Q9). Sem sessão ativa, o sistema leva ao login e, depois dele, à página pedida
  (US-50 E1).
- **FR-011**: As telas desta feature DEVEM seguir a base visual da spec 003 (protótipo de 17/10). As
  listas suspensas e a caixa de seleção de papéis atendem ao RNF de Proteção contra Erro do Usuário.

**Docentes [US-03][RBN-CAD-01.1][RBN-CAD-01.2][RBN-CAD-01.4]**

- **FR-012**: A Secretaria e o Coordenador de Curso DEVEM poder cadastrar Docente com Nome Completo,
  E-mail Institucional (formato nome@uea.edu.br, até 100 caracteres), Titulação, Curso de Lotação e
  Papéis (caixa "Coordenador de Curso"). E-mail fora do domínio, sem formato válido ou com mais de
  100 caracteres: "Informe um e-mail institucional (@uea.edu.br)", sem salvar.
- **FR-013**: O campo Curso Coordenado DEVE aparecer e ser obrigatório só quando "Coordenador de
  Curso" estiver marcado. Ao desmarcar, o campo some e o valor é descartado; sem o papel, o docente é
  Docente comum (US-03 A1 a A3). Os papéis Professor da Disciplina, Orientador e Coorientador não são
  marcados aqui: vêm das turmas e das orientações (RBN-CAD-01.1, campo 5).
- **FR-014**: Cada curso DEVE ter no máximo um Coordenador, e cada docente coordena no máximo um
  curso. Marcar o papel para um curso que já tem Coordenador: "O curso já possui Coordenador.
  Desmarque o papel no coordenador atual para continuar", sem salvar (US-03 E1). A lista de Curso
  Coordenado oferece qualquer curso do NUCOMP, não só o curso do usuário (FR-009; Clarifications,
  Q5).
- **FR-015**: O cadastro bem-sucedido DEVE exibir "Docente cadastrado com sucesso" (Clarifications,
  Q6) e incluir o docente na listagem, com 0 orientandos.
- **FR-016**: A Secretaria e o Coordenador DEVEM poder alterar Nome Completo, E-mail Institucional,
  Titulação, Curso de Lotação, Papéis e Curso Coordenado de docente do seu curso, com as validações
  do cadastro. Sucesso: "Dados atualizados". Desmarcar o papel deixa o curso sem Coordenador (US-03
  A10). Trocar o Curso de Lotação move o docente para as listas e relatórios do novo curso (US-03
  A11).
- **FR-017**: A listagem de docentes, só de leitura, DEVE mostrar Nome, E-mail Institucional,
  Titulação, Curso de Lotação, Papéis, Status da Conta ('Aguardando Ativação', 'Ativa' ou 'Inativa')
  e quantidade de orientandos, separada em TCC 1 e TCC 2, com alerta visual quando o docente passa de
  5 orientandos (RBN-CAD-11.3; Clarifications, Q8). Ela é acessada pela Secretaria e pelo
  Coordenador.
- **FR-018**: A listagem DEVE abrir filtrada pelo curso do usuário (Curso de Lotação igual ao curso
  do usuário), com as opções Engenharia de Computação, Sistemas de Informação, Licenciatura em
  Computação e Todos (RBN-CAD-14.1). O filtro muda só a exibição e vale só para a tela aberta. Sem
  docentes no filtro: "Nenhum registro".
- **FR-019**: Na listagem, "Editar", "Inativar" e "Reativar" DEVEM aparecer só nas linhas de docentes
  do curso do usuário: "Inativar" só para 'Ativa', "Reativar" só para 'Inativa' (US-04 E10).

**Secretaria [US-03][US-04][RBN-CAD-02.1 a 02.3]**

- **FR-020**: Só o Coordenador de Curso DEVE poder cadastrar Secretaria, com Nome Completo, E-mail
  Institucional (mesmas regras do FR-012) e Curso Vinculado (o curso do Coordenador). Sucesso:
  "Secretaria cadastrada com sucesso".
- **FR-021**: Cada curso DEVE ter no máximo uma Secretaria não inativa ('Aguardando Ativação' ou
  'Ativa'; Clarifications, Q7). Cadastro, ou troca de Curso Vinculado, para curso que já tem
  Secretaria: "O curso já possui Secretaria vinculada", sem salvar. A inativação libera o curso.
- **FR-022**: O Coordenador DEVE poder alterar Nome Completo, E-mail Institucional e Curso Vinculado
  da Secretaria do seu curso, com as validações do cadastro. Sucesso: "Dados atualizados".
- **FR-023**: A lista de Secretarias DEVE mostrar Nome, E-mail Institucional, Curso Vinculado e
  Status da Conta, com o filtro de Curso do FR-018. O Coordenador vê "Nova secretaria", "Editar" e
  "Inativar" (este só para 'Ativa'). A Secretaria vê a lista sem nenhuma dessas ações (US-03 E9,
  US-04 E9).
- **FR-024**: O Coordenador DEVE poder inativar a Secretaria 'Ativa' do seu curso, com confirmação
  (MC-03). Ao confirmar: Status da Conta 'Inativa', login negado com "Conta inativa" (spec 003),
  histórico mantido, curso liberado para nova Secretaria e mensagem MC-04. Cancelar na confirmação
  não altera nada.

**Inativação e reativação do Docente [US-04][RBN-CAD-01.3]**

- **FR-025**: A Secretaria e o Coordenador DEVEM poder inativar docente 'Ativa' do seu curso. Ao
  clicar em "Inativar", o sistema verifica os vínculos (FR-026). Sem vínculo, pede a confirmação
  "Deseja inativar o docente NOME?". Na confirmação, verifica de novo. Sem vínculo, grava o Status da
  Conta 'Inativa' e exibe "Docente inativado". Cancelar na confirmação não altera nada.
- **FR-026**: Impedem a inativação, nesta ordem de apresentação:
  (a) orientandos ou coorientandos com TCC ativo (Status do TCC Em Andamento, Apto para Defesa,
  Aprovado ou Aprovado com Correções enquanto a Versão Final não foi homologada);
  (b) convite de coorientação sem resposta (status 'Aguardando Aceite');
  (c) participação em banca de sessão Agendada, Reagendada ou Em Andamento;
  (d) turma sob sua responsabilidade não arquivada;
  (e) papel de Coordenador de Curso.
  Não impedem: TCC Sem Proposta (Clarifications, Q16), Concluído, Reprovado, Desistente, Jubilado ou
  Aprovado para TCC 2;
  convite já respondido; banca Realizada ou Cancelada; turma arquivada (US-04 A4).
- **FR-027**: Com vínculo, o sistema NÃO DEVE inativar e DEVE exibir um alerta com **todos** os
  motivos e as quantidades, no formato "Não é possível inativar: o docente MOTIVOS". Motivo (a):
  "possui N orientandos ou coorientandos com TCC ativo" (US-04 E1, sempre no plural, inclusive com
  N = 1; Clarifications, Q18); motivo (e): "é Coordenador do curso" (US-04 E6); motivos (b) a
  (d): MC-05 a MC-07. Com mais de um motivo, eles são unidos por
  vírgulas e "e", e o alerta termina com ". Encerre ou transfira esses vínculos primeiro" (US-04 E6).
  O alerta volta à listagem sem alterar a conta.
- **FR-028**: A conta 'Inativa' DEVE ficar sem login ("Conta inativa", spec 003) e fora das listas de
  escolha de orientador, coorientador e avaliador. TCCs, bancas, atas, turmas e relatórios
  anteriores continuam com o docente. As listas de escolha pertencem às features de Vida do TCC e de
  Defesa; esta feature define a regra ("só docentes 'Ativa' são escolhidos") para elas usarem.
- **FR-029**: A Secretaria e o Coordenador DEVEM poder reativar docente 'Inativa' do seu curso, com
  confirmação (MC-01). Ao confirmar: Status da Conta 'Ativa', login liberado com a senha que já
  tinha, volta às listas de orientador e avaliador como Docente comum e mensagem MC-02.
- **FR-030**: Falha ao gravar a inativação ou a reativação DEVE exibir "Não foi possível salvar. Tente
  novamente" e manter a conta como estava (US-04 E11).

**Membros Externos [US-05][RBN-CAD-03.1][RBN-CAD-03.2]**

- **FR-031**: O item de menu "Membros externos" e a lista DEVEM estar disponíveis para Orientador,
  Professor da Disciplina, Secretaria e Coordenador de Curso. Cadastrar, alterar e prorrogar exigem,
  para o Professor da Disciplina que não é também Orientador, Secretaria ou Coordenador, pelo menos
  uma turma não arquivada (Clarifications, Q10). Aluno, Docente sem esses papéis e Membro Externo
  ficam sem o menu e recebem a recusa do FR-010.
- **FR-032**: O cadastro DEVE ter Nome Completo (FR-002), E-mail (formato nome@domínio, de qualquer
  domínio, até 100 caracteres), Titulação (FR-004) e Instituição de Origem (letras, números, espaços
  e pontuação, até 150 caracteres), todos obrigatórios. E-mail inválido ou acima de 100 caracteres:
  "Informe um e-mail válido". Instituição fora da regra: "Informe a instituição com até 150
  caracteres". Nos dois casos, nada é salvo.
- **FR-033**: O cadastro bem-sucedido DEVE exibir "Membro externo cadastrado com sucesso", criar a
  conta 'Aguardando Ativação' com a validade inicial do FR-038 e deixar o membro disponível na lista
  de Membros externos e na escolha de avaliadores da banca (1º Avaliador, 2º Avaliador e Suplente).
- **FR-034**: O cadastro DEVE poder ser aberto a partir de outra tela do sistema (atalho da
  composição da banca, US-23, RBN-DEF-02.3). Ao salvar, volta a essa tela informando o membro criado,
  para que ele já venha selecionado. Ao cancelar, volta sem membro. Só são aceitos destinos internos
  do próprio sistema.
- **FR-035**: Os perfis do FR-031 DEVEM poder alterar Nome Completo, E-mail, Titulação e Instituição
  de Origem, com as validações do cadastro. Sucesso: "Dados atualizados". Alteração inválida não grava
  e mantém os dados anteriores. A alteração de membro 'Expirada' grava os dados e não reabre o
  acesso (US-05 A6).
- **FR-036**: A tela Membros externos DEVE listar Nome, E-mail, Instituição de Origem, Status da
  Conta e validade do acesso (DD/MM/AAAA), com "Editar" para os perfis do FR-035 e "Prorrogar"
  conforme o FR-042. O status exibido considera a validade vencida (Edge Cases). A lista não tem
  filtro de Curso, porque o Membro Externo não tem curso (Clarifications, Q19).

**Validade e expiração [US-06][RBN-CAD-03.3]**

- **FR-037**: A validade do Membro Externo vinculado a banca DEVE ser a data da defesa mais distante
  entre as suas sessões não Canceladas (Agendada, Reagendada, Em Andamento ou Realizada), mais 7 dias
  corridos (US-06 fluxo principal, A4 e A6). Se todas as sessões do membro estiverem Canceladas, a
  validade é a data do último cancelamento mais 7 dias corridos (A3). Se o membro for retirado da
  banca antes da sessão (RBN-DEF-02.4) e não sobrar nenhuma sessão não Cancelada, a validade é a
  data da retirada mais 7 dias corridos (A7; Clarifications, Q13). Se não restar sessão não
  Cancelada e houver cancelamentos e retiradas, vale a data do evento mais recente (último
  cancelamento ou última retirada), mais 7 dias corridos (Q13; índice Q-45).
- **FR-038**: O membro sem nenhuma banca DEVE ter validade de 30 dias corridos a partir do cadastro
  (US-05 A5, US-06 A5): no cadastro, a data de validade é gravada como a data do cadastro + 30 dias
  corridos, sem coluna nova (Clarifications, Q12). O primeiro vínculo a uma banca passa a aplicar o
  FR-037.
- **FR-039**: A validade DEVE ser recalculada a cada vínculo do membro a uma banca, reagendamento,
  cancelamento de sessão e retirada do membro da banca. Pode avançar ou recuar (US-06 A2), mas
  nunca para antes da data dada pela última prorrogação manual do membro (Clarifications, Q15). Se a nova
  validade alcançar hoje ou uma data futura e a conta estiver 'Expirada', ela volta a 'Ativa', com o
  mesmo login e a mesma senha (A1). A conta 'Aguardando Ativação' continua assim. Os eventos de banca
  pertencem à feature de Defesa (US-21, US-23, US-24); esta feature entrega a regra de recálculo
  para ela chamar.
- **FR-040**: A validade DEVE valer até o fim do dia indicado. A partir do dia seguinte, a conta
  'Ativa' passa a 'Expirada' automaticamente, sem depender de login (RNF de Integridade do RAN-CAD-03;
  Clarifications, Q3). O login negado pela validade também grava a troca e exibe "Seu acesso
  expirou. Procure a coordenação do curso" (US-06 passo 4 e E1; Clarifications, Q4). O login é da
  spec 003, que hoje exibe a M-16; a troca do texto depende da Q-52 do índice. Nome, E-mail,
  Titulação, Instituição e as participações em bancas não são apagados.
- **FR-041**: Se o recálculo falhar, o sistema DEVE manter a validade anterior, registrar o erro no
  log e tentar de novo no próximo evento de banca do membro (US-06 E2).

**Prorrogação [US-50][RBN-CAD-03.3]**

- **FR-042**: O botão "Prorrogar" DEVE aparecer na linha do membro com conta 'Ativa' ou 'Expirada'
  para: o Orientador de um TCC cuja banca (sessão não Cancelada) inclui o membro (Clarifications,
  Q11); o Professor da Disciplina com turma não arquivada; a Secretaria; e o Coordenador de Curso. Não
  aparece para conta 'Aguardando Ativação' (US-50 E3) nem para outros perfis ou Orientadores sem o
  vínculo (E2). Pelo endereço direto, sem permissão: "Você não tem permissão para esta ação"; conta
  'Aguardando Ativação': MC-09. Nos dois casos, nada é alterado.
- **FR-043**: Prorrogar conta 'Ativa' em dia DEVE somar 7 dias corridos à validade atual. Prorrogar
  conta 'Expirada' (ou 'Ativa' com a validade vencida, ou sem validade) DEVE gravar hoje + 7 dias
  corridos e o Status da Conta 'Ativa'. O sistema mantém o usuário na tela Membros externos, exibe
  "Acesso prorrogado até DD/MM/AAAA" e atualiza a linha. Prorrogações sucessivas somam 7 dias a cada
  vez.
- **FR-044**: Falha ao gravar a prorrogação DEVE exibir "Não foi possível prorrogar o acesso. Tente
  novamente" e manter a validade e o status anteriores.

**Coordenadores iniciais [RAN-CAD-01, Instalabilidade][RBN-CAD-06.2]**

- **FR-045**: O sistema DEVE oferecer um comando de gestão, para a implantação, que cria o
  Coordenador de Curso de um ou mais cursos do NUCOMP a partir de Nome Completo, E-mail
  Institucional, Titulação e curso. Cada conta é criada como Docente 'Aguardando Ativação', lotada no
  curso e com o papel de Coordenador desse curso, sem envio de e-mail (FR-005). O comando funciona
  com o sistema em produção, ao contrário da conta de teste da spec 003.
- **FR-046**: O comando DEVE aplicar as mesmas validações do cadastro de docente (FR-001 a FR-004,
  FR-012 e FR-014). Curso que já tem Coordenador e dados inválidos não geram conta, e o motivo é
  informado com o texto das telas. Os demais cursos seguem. Rodar o comando de novo não duplica
  contas. Ao final, o comando informa, por curso, o que foi criado e o que foi recusado.

**Registro e mensagens**

- **FR-047**: Cadastro, alteração, inativação, reativação, prorrogação, expiração e criação pelo
  comando DEVEM ser registrados no log de eventos da spec 003, com o autor (ou "sistema"), a conta
  afetada e a data e hora, sem e-mail completo nem senha.
- **FR-048**: As mensagens com texto definido nas US DEVEM ser exibidas exatamente como na US. As
  demais usam os textos da seção "Mensagens a validar com a PO": MC-01 a MC-10, definidos em
  2026-10-22 (Clarifications, Q14), e MC-11 a MC-13, PROVISÓRIOS (Clarifications, Q17 e Q24).

### Key Entities *(include if feature involves data)*

Todas já existem (spec 001). Nenhuma é criada.

- **Conta de usuário**: nome, e-mail (login, único), senha (vazia até o primeiro acesso), Status da
  Conta ('Aguardando Ativação', 'Ativa', 'Inativa', 'Expirada') e o momento do último link gerado.
- **Docente**: conta com Titulação e Curso de Lotação. Os papéis vêm de outros registros:
  Coordenador (abaixo), Professor da Disciplina (turmas), Orientador e Coorientador (orientações).
- **Coordenador de Curso**: liga um curso a um docente. Um por curso, e um curso por docente.
- **Secretaria**: conta com Curso Vinculado. Uma não inativa por curso.
- **Membro Externo**: conta com Titulação, Instituição de Origem e data de validade do acesso.
- **Curso**: os três cursos do NUCOMP, para Curso de Lotação, Curso Coordenado, Curso Vinculado e
  o filtro.
- **Só lidas, para a verificação de vínculos e a validade**: TCC e o seu Status, orientação,
  coorientação e convite de coorientação, turma (Status 'Ativa' ou 'Arquivada'), sessão de defesa
  (data e Status), banca da defesa e o histórico da defesa (data do cancelamento e da retirada do
  membro).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos cenários de aceite das US-03 (40), US-04 (25), US-05 (23), US-06 (18) e US-50
  (9), e os 4 cenários do comando dos Coordenadores iniciais, passam em testes automatizados. Os
  cenários que dependem de telas de outras features (US-05, cenários 14 e 15; gatilhos de banca da
  US-06) são testados aqui pela regra, com os dados criados direto, e nas telas pela feature dona.
  O cenário 3 da US-06 só passa depois que a spec 003 trocar a M-16 pelo texto da US-06 (índice
  Q-52).
- **SC-002**: 100% das mensagens desta feature com texto definido nas US são idênticas ao texto da
  US, caractere por caractere. As demais são idênticas à tabela "Mensagens a validar com a PO".
- **SC-003**: Nenhum e-mail fica repetido entre contas, nenhum curso fica com dois Coordenadores e
  nenhum curso fica com duas Secretarias não inativas, verificado por teste no cadastro, na
  alteração, no comando e em gravações simultâneas.
- **SC-004**: Nenhuma ação desta feature é aceita para perfil sem permissão ou fora do curso do
  usuário, verificado por teste para cada ação, inclusive pelo endereço direto.
- **SC-005**: Nenhum docente com algum dos cinco tipos de vínculo é inativado, e o alerta lista 100%
  dos motivos presentes, verificado por teste para cada vínculo sozinho e para combinações.
- **SC-006**: Nenhum Membro Externo entra no sistema depois do fim da validade, e 100% das contas
  vencidas aparecem como 'Expirada' a partir do dia seguinte ao fim da validade, mesmo sem tentativa
  de login.
- **SC-007**: Numa instalação nova, a pessoa que implanta cria os três Coordenadores, e um deles faz o
  primeiro acesso e cadastra a Secretaria e um docente do curso em até 10 minutos, seguindo só o
  roteiro do quickstart (teste manual cronometrado).
- **SC-008**: A Secretaria cadastra um docente em até 2 minutos, e o Orientador prorroga o acesso de
  um membro em até 30 segundos a partir do menu, sem ajuda (teste manual cronometrado).
- **SC-009**: A aplicação do filtro de Curso atualiza as listas de docentes e de Secretarias em menos
  de 2 segundos após a seleção (RNF de Comportamento Temporal do RAN-CAD-14).

## Rastreabilidade

Texto dos RBN conforme a matriz de 17/10 (aba Requisitos_*).

| US | RBN | Texto do RBN (matriz) | FR |
|---|---|---|---|
| US-03 | RBN-CAD-01.1 | O sistema deve mostrar um formulário de cadastro do Docente (professor do NUCOMP, incluindo Professor da Disciplina, Orientador e Coordenador de Curso) que deve conter os campos Nome Completo, E-mail Institucional, Titulação, Curso de Lotação, Papéis e Curso Coordenado. | FR-001 a FR-007, FR-012 a FR-015 |
| US-03, US-04 | RBN-CAD-01.2 | O sistema deve permitir a alteração de Nome Completo, E-mail Institucional, Titulação, Curso de Lotação, Papéis e Curso Coordenado do Docente. | FR-008, FR-016 (na US-04, desmarcar o papel de Coordenador antes de inativar) |
| US-04 | RBN-CAD-01.3 | O sistema deve permitir a manutenção do Status da Conta do Docente, com os valores Aguardando Ativação, Ativa ou Inativa, por meio da inativação e da reativação. | FR-025 a FR-030 |
| US-03 | RBN-CAD-01.4 | O sistema deve exibir a listagem de docentes, com o filtro de Curso. | FR-017 a FR-019 |
| US-03 | RBN-CAD-02.1 | O sistema deve mostrar um formulário de cadastro da Secretaria que deve conter os campos Nome Completo, E-mail Institucional e Curso Vinculado. | FR-020, FR-021, FR-023 |
| US-03, US-04 | RBN-CAD-02.2 | O sistema deve permitir a alteração de Nome Completo, E-mail Institucional e Curso Vinculado da Secretaria. | FR-008, FR-022 |
| US-04 | RBN-CAD-02.3 | O sistema deve permitir a manutenção do Status da Conta da Secretaria, com os valores Aguardando Ativação, Ativa ou Inativa, por meio da inativação. | FR-021, FR-024 |
| US-05 | RBN-CAD-03.1 | O sistema deve mostrar um formulário de cadastro do Membro Externo (avaliador de fora do NUCOMP ou da UEA) que deve conter os campos Nome Completo, E-mail, Titulação e Instituição de Origem. | FR-031 a FR-034, FR-038 |
| US-05 | RBN-CAD-03.2 | O sistema deve permitir a alteração de Nome Completo, E-mail, Titulação e Instituição de Origem do Membro Externo. | FR-008, FR-035, FR-036 |
| US-05 | RBN-DEF-02.3 | [Exceção] O sistema deve permitir o cadastro de Membro Externo ausente da lista. | FR-034 |
| US-06, US-50 | RBN-CAD-03.3 | O sistema deve permitir a manutenção do Status da Conta do Membro Externo, com os valores Aguardando Ativação, Ativa ou Expirada, expirando o acesso 7 dias após a defesa e permitindo a renovação ou a prorrogação da conta. | FR-037 a FR-044 |
| US-06 | RBN-DEF-02.4 | [Exceção] O sistema deve permitir a alteração da banca antes da sessão. | FR-037, FR-039 (retirada do membro) |
| apoio (US-03) | RBN-CAD-11.3 | O sistema deve exibir a quantidade de orientandos de cada docente. | FR-017 |
| apoio (US-03, US-04) | RBN-CAD-14.1 | O sistema deve aplicar o filtro de Curso nas visualizações do Coordenador de Curso e da Secretaria. | FR-009, FR-018, FR-019, FR-023 |
| apoio (todas) | RBN-CAD-06.2 | O sistema deve mostrar um formulário de primeiro acesso de Docente, Secretaria e Membro Externo que deve conter o campo E-mail. | FR-005, FR-045 |
| comando | RNF de Instalabilidade do RAN-CAD-01 | Criação dos Coordenadores de Curso iniciais (Clarifications, Q2). | FR-045, FR-046 |
| todas | — | Permissões, log e mensagens. | FR-010, FR-011, FR-047, FR-048 |

RNFs da matriz atendidos por esta feature:

| RAN | RNF (matriz) | FR / SC |
|---|---|---|
| RAN-CAD-01, RAN-CAD-02 | Segurança: Confidencialidade: Cada usuário acessa apenas as funções dos papéis atribuídos a ele. | FR-009, FR-010; SC-004 |
| RAN-CAD-01, RAN-CAD-02, RAN-CAD-03 | Segurança: Autenticidade: O e-mail é único no sistema e é usado como login. | FR-001, FR-008; SC-003 |
| RAN-CAD-01 | Portabilidade: Instalabilidade: criação das contas de Coordenador de Curso na instalação. | FR-045, FR-046; SC-007 |
| RAN-CAD-01, RAN-CAD-03 | Usabilidade: Proteção contra Erro do Usuário: Titulação e curso em listas suspensas; papéis em caixa de seleção. | FR-004, FR-011 |
| RAN-CAD-03 | Segurança: Integridade: A conta do Membro Externo passa ao Status Expirada automaticamente ao fim da validade (RBN-CAD-03.3). | FR-040; SC-006 |
| RAN-CAD-14 | Eficiência de Desempenho: Comportamento Temporal: o filtro de Curso atualiza as listas em menos de 2 segundos. | FR-018, FR-023; SC-009 |

## Mensagens a validar com a PO

Textos sem definição nas US nem na matriz, revisados para seguir o padrão dos textos das US. As
MC-01 a MC-10 foram **definidas em 2026-10-22** (Clarifications, Q14; índice Q-46). As MC-11 a
MC-13 são **PROVISÓRIAS** e aguardam a PO (Clarifications, Q17 e Q24; índice Q-58). A PO pode revisar qualquer uma
depois: muda só o texto, não a regra. Com N = 1, os motivos MC-05 a MC-07 vão para o singular (entre
colchetes na tabela).

| ID | Situação em que aparece | Texto | Origem | Situação |
|---|---|---|---|---|
| MC-01 | Confirmação da reativação do docente | "Deseja reativar o docente NOME?" | US-04 A1, passo 2 (sem texto; segue "Deseja inativar o docente Nome?") | Definida |
| MC-02 | Docente reativado | "Docente reativado" | US-04 A1 (segue "Docente inativado") | Definida |
| MC-03 | Confirmação da inativação da Secretaria | "Deseja inativar a Secretaria NOME?" | US-04 A2, passo 2 | Definida |
| MC-04 | Secretaria inativada | "Secretaria inativada" | US-04 A2 e cenário 21 | Definida |
| MC-05 | Motivo de bloqueio (b): convite de coorientação sem resposta | "possui N convites de coorientação sem resposta" [1 convite] | US-04 E2 e cenário 5 ("informa o motivo") | Definida |
| MC-06 | Motivo de bloqueio (c): banca em aberto | "participa de N bancas Agendadas, Reagendadas ou Em Andamento" [1 banca Agendada, Reagendada ou Em Andamento] | US-04 E3 e cenários 6 e 7 | Definida |
| MC-07 | Motivo de bloqueio (d): turma não arquivada | "é Professor da Disciplina de N turmas não arquivadas" [1 turma não arquivada] | US-04 E4 e cenário 8 | Definida |
| MC-08 | Docente cadastrado (divergência interna da US-03) | "Docente cadastrado com sucesso" (cenário 1), no lugar de "Docente salvo" (fluxo principal, passo 7) | Clarifications, Q6 | Definida |
| MC-09 | Prorrogação pelo endereço direto de conta 'Aguardando Ativação' | "Este membro ainda não ativou a conta e não tem validade para prorrogar" | US-50 E3 (só esconde o botão) | Definida |
| MC-10 | Inativar ou reativar pelo endereço direto com status incompatível | "Esta ação não está disponível para o Status da Conta atual" | US-04 E10 (só esconde o botão) | Definida |
| MC-11 | Troca de e-mail pelo gestor com a senha de quem altera errada | "Senha incorreta" | Clarifications, Q17 (sem fonte; alternativa: "Senha atual incorreta", da US-12 E2) | PROVISÓRIA (índice Q-58) |
| MC-12 | Troca de e-mail pelo gestor salva; link de confirmação enviado ao novo endereço | "Dados atualizados. Enviamos um link de confirmação para o novo e-mail" | Clarifications, Q17; segue "Dados atualizados" (US-03) e a M-06 da spec 003 | PROVISÓRIA (índice Q-58) |
| MC-13 | Troca de e-mail pelo gestor: demais campos gravados, mas o envio do link falhou | "Dados atualizados, mas não foi possível enviar o link de confirmação. Altere o e-mail novamente em alguns minutos" | Clarifications, Q24; segue "Dados atualizados" (US-03) e a M-17 da spec 003 | PROVISÓRIA (índice Q-58) |

## Assumptions

- **Branch**: `feature/feat-04-gestao-de-contas`, indicada no pedido. A branch local se chamava
  `feat-04gestao-de-contas` e foi renomeada em 2026-10-22 para o padrão do PGCS (índice, Q-48); ela
  ainda não existe no remoto. A spec é a 002, embora as specs 003 e 004 já existam.
- **Documento de US**: a cópia de referência em `docs/fonte/` é a v3.3. O pedido citava a v3.2; o
  CLAUDE.md e os agentes foram corrigidos em 2026-10-22, e a correção da constituição está no
  índice (Q-62).
- **Nomes dos botões**: as US-03 e US-05 usam nomes diferentes para o mesmo botão. Como na Q6, vale
  o texto dos cenários de aceite: "Salvar" para gravar o formulário (o fluxo principal da US-03 diz
  "Cadastrar"), "Nova secretaria" (US-03 E9 e cenário 21; o A4 diz "Cadastrar secretaria"),
  "Cadastrar Docente" e "Novo membro externo" (fluxos principais das US-03 e US-05, sem divergência
  nos cenários). A correção das US está no índice (Q-61).
- **Precedência**: matriz de 17/10 > US. As divergências tratadas estão em Clarifications (Q3 a Q8,
  Q11 a Q13, Q16 a Q19). A responsável decidiu se afastar da matriz em quatro pontos: Q4 e Q5
  (segue a US), Q11 (segue a US-50 e acrescenta condições) e Q19 (sem o filtro de Curso que o
  RBN-CAD-14.1 pede em todas as listas).
- **Dicionário de dados** (Q12): a descrição de `mem_validade_ate` passa a dizer que a coluna guarda
  também a validade de 30 dias do membro sem banca. A atualização do documento (Drive e cópia em
  `docs/fonte/`) é da Maria Luiza Guimarães; o tipo e a nulidade da coluna não mudam.
- **Reaproveitamento da spec 003** (contrato de serviços): base visual e `base.html`, verificação de
  perfil (`@perfil_requerido`, `tem_perfil`, `papeis`, `professor_com_turma_ativa`), menu lateral por
  app, `normalizar_email` e `email_em_uso`, log de eventos e o login, que já nega 'Inativa',
  'Expirada' e validade vencida. Nada disso é reescrito.
- **Escopo de curso**: Clarifications, Q5. Docente e Secretaria são de um curso. O Membro Externo não
  tem curso, e as suas ações não têm filtro nem restrição de curso (Clarifications, Q19).
- **Filtro de Curso (US-39)**: esta feature aplica o RBN-CAD-14.1 nas suas listas (docentes e
  Secretarias). A US-39 continua dona do filtro nas demais telas e relatórios.
- **Quantidade de orientandos** (RBN-CAD-11.3, da US-18): conta os TCCs com orientação ativa do
  docente, separados pela Descrição da turma (TCC 1 ou TCC 2). O alerta visual aparece quando a soma
  passa de 5. O aceite de orientação acima de 5 é da US-18.
- **Gatilhos de banca** (US-06): a feature de Defesa (US-21, US-23, US-24, Célio Benjamim) chama o
  recálculo do FR-039 nos seus eventos. Até lá, a validade dos membros vem do cadastro (FR-038) e da
  prorrogação (US-50).
- **Expiração automática** (FR-040): feita por uma rotina diária, além do login. O agendamento no
  servidor é item de operação a definir no plano, como o `clearsessions` da spec 003.
- **Atalho da banca** (US-05 A1): esta feature entrega o retorno à tela de origem. O botão
  "Cadastrar membro externo" na composição da banca é da US-23.
- **Listas de escolha de orientador, coorientador e avaliador** (FR-028): são das features de Vida
  do TCC e de Defesa, que usam a regra "só docente 'Ativa'".
- **Data da última prorrogação** (Q15): o dicionário não tem coluna para ela. A proposta é ler a
  data da última prorrogação no registro de eventos (FR-047), sem tabela nova. O plano DEVE
  confirmar que esse registro é confiável para uma regra de negócio. O log da spec 003 é um arquivo,
  que pode ser girado ou apagado. Se não for confiável, o caminho é pedir à Maria Luiza Guimarães uma
  coluna no dicionário antes de implementar (princípio III da constituição).
- **Orientador na prorrogação** (FR-042): "banca do orientando" é qualquer sessão não Cancelada de
  TCC com orientação ativa do docente.
- **Comando dos Coordenadores** (FR-045): os dados (nome, e-mail, titulação de cada Coordenador) são
  informados por quem implanta, não ficam no código nem no repositório. A pasta `management/` está
  entre os itens de configuração da spec 003 que aguardam o Célio Benjamim (índice, Q-27).
- **Mensagens**: as MC-01 a MC-10 estão definidas (Q14; índice Q-46). As MC-11 a MC-13 (PROVISÓRIAS) aguardam a
  PO (índice Q-58). A mensagem de expiração do Membro Externo é a da US-06 (Clarifications, Q4); a
  troca do texto no login da spec 003 (M-16) aguarda a Julia Cohen (índice Q-52). A M-02 e a M-14 da
  spec 003 passam aos textos das US nesta entrega (Q9; spec 003, Q30).
- **Troca de e-mail pelo gestor** (FR-008): reaproveita o link de confirmação da troca de e-mail da
  spec 003 (FR-021), sem coluna nova. O FR-021 da spec 003 cobre só Aluno e Membro Externo (para
  Docente e Secretaria, o e-mail é só leitura no perfil). O plano DEVE estender o mecanismo a
  Docente e Secretaria e confirmar que ele serve para a troca feita por outra pessoa.
- **Pendências registradas no índice** (`docs/questoes-a-rever.md`): Q-14 e Q-15 (respondidas por
  este pedido); Q-16, Q-31, Q-44 a Q-51, Q-53 a Q-57 e Q-59 (respondidas em 2026-10-22); Q-52,
  Q-58 e Q-60 a Q-62 (abertas). Da segunda conferência: Q-64 a Q-66 respondidas, S-03 registrada; aberta: Q-63 (prioridade da
  US-50, para a PO); ciência das outras features: Q-67 (Defesa) e Q-68
  (Vida do TCC).
- **Dependências**: specs 001, 003 e 004 implementadas. Turmas (spec 004), orientações,
  coorientações, convites e sessões de defesa são lidos nas tabelas da spec 001, mesmo antes de as
  features donas terem telas.
