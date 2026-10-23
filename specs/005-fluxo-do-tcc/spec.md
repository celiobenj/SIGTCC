# Feature Specification: Fluxo do TCC e Entregas

**Feature Branch**: `feature/feat-05-fluxo-do-tcc`

**Created**: 2026-10-22

**Status**: Approved (Julia Cohen, 2026-10-22)

**Input**: User description: "Fluxo do TCC e Entregas do SIGTCC: US-13, US-14, US-15, US-16, US-29, US-43 e US-44, com o modelo de dados da spec 001 e reutilizando os serviços das specs 003 e 004."

## Dependências e reaproveitamento

- **Modelo de dados**: já existe (spec 001). Esta spec não cria tabelas nem colunas. Usa
  `TCCs`, `PalavrasChave_TCC`, `Historico_Status_TCC`, `Turmas_Marcos`, `Entregas_Marcos` e
  `Historico_Envios_Entregas` (`docs/fonte/Modelo_Logico_e_Dicionario_18_10.md`, seções 3.4 e 3.5).
- **Serviços reutilizados** (`specs/003-acesso-login/contracts/servicos-compartilhados.md` e
  `specs/004-turmas-alunos/contracts/servicos-compartilhados.md`):
  - `participacao_encerrada(tcc)`: aluno Desistente, Reprovado ou Jubilado não edita o TCC nem
    envia entregas (RBN-CAD-08.5).
  - `travar_turma_ativa(tur_id)` / `TurmaArquivada`: turma arquivada vira só consulta, com a MT-25.
  - `turma_para(usuario, tur_id, acao, travar=False)`, `vinculo_na_turma`: permissão e existência
    (404 → 403 → MT-25), regra do Professor da Disciplina (spec Q27).
  - `turma_tem_orientador_automatico(turma)`: define quem confirma Apto para Defesa e quem precisa
    de "Correções Conferidas" antes da homologação (Sistemas de Informação).
  - `criar_entregas_do_aluno(aluno, turma)`: a spec 004 já cria os registros de entrega do aluno na
    matrícula e na transferência. **Esta spec (US-43) usa o mesmo serviço do outro lado**: ao
    cadastrar uma entrega nova, cria o registro `Entregas_Marcos` 'Aguardando Envio' (ou 'Não
    Entregue', se a Data Limite já venceu) para cada aluno atualmente matriculado na turma, com
    participação não encerrada (índice Q-41).
  - `services.notificar(usuario, mensagem, link=None)`: única forma de notificar (corte em 500
    caracteres, só link interno).
- **O que a spec 006** (orientação, atas, publicações — US-41, US-42, responsável Célio Benjamim)
  **pode consumir desta spec**, sem duplicar regra:
  - Dados da Proposta e do TCC: título, subtítulo, resumo, modalidade, link da proposta, área de
    interesse, palavras-chave (somente leitura fora desta spec).
  - Status do TCC e seu histórico (`Historico_Status_TCC`): a 006 **lê e confia** no Status já
    calculado por esta spec; não deve recalcular nem duplicar a tabela de gatilhos (RBN-CAD-08.3).
    Os gatilhos "Indicação de Apto para Defesa" e "Liberação do resultado" são **disparados pela
    spec 006** (US-42, US-27), mas a gravação do Status e do histórico é sempre feita pelo serviço
    desta spec (ver `atualizar_status_tcc` no plano).
  - Estado das entregas (`Entregas_Marcos`, `Turmas_Marcos`): a entrega do tipo "Documento para
    Defesa" com status Entregue ou Entregue com Atraso é pré-condição do botão Apto para Defesa
    (US-42) e é o link enviado à banca no agendamento (US-anterior de Defesa). A 006 só consulta;
    não grava em `Entregas_Marcos`.
  - Vocabulário consistente: "tela de orientandos" (Orientador) e "tela do aluno" (Professor da
    Disciplina, RAN-CAD-08.9) são as telas em que a 006 insere suas próprias ações (Apto para
    Defesa, Correções Conferidas) ao lado dos dados que esta spec exibe.
  - Visibilidade do Coorientador do NUCOMP (RBN-CAD-11.4): esta spec não concede ao Coorientador
    acesso ao Status, ao histórico (FR-009) nem ao acompanhamento de entregas (FR-026); a 006
    decide, no seu próprio painel de orientandos, como e se reaproveita os serviços de consulta
    desta spec para o Coorientador (Clarifications, sessão 2026-10-22).
- **Tela da turma e menu da spec 004** (FR-010 da spec 004, já mesclada): o item de menu "Turmas" e
  a tela da turma (`/turmas/<tur_id>/`) continuam só do Professor da Disciplina e da Secretaria do
  curso. Esta spec não abre essa tela ao Aluno: dá ao Aluno uma entrada própria (item "Turmas" do
  Aluno, com as turmas em que está matriculado) e só **acrescenta** à tela da turma da spec 004 a
  barra de abas "Alunos" e "Atividades" do Professor (FR-031; Clarifications, sessão 2026-10-23;
  índice Q-89).

## Clarifications

### Session 2026-10-22

- Q: Quando o Aluno informa a mesma Palavra-Chave em duas caixas diferentes, o sistema deve
  rejeitar com uma mensagem, ou aceitar e gravar só uma ocorrência? → A: Rejeitar: destacar a
  caixa repetida e exibir mensagem antes de salvar (Opção A).
- Q: A Secretaria do curso deve ver o Status do TCC e o histórico (FR-009) de um aluno, ou isso
  fica restrito a Aluno, Orientador e Professor da Disciplina, como hoje? → A: Restrito — mantém
  só Aluno, Orientador e Professor da Disciplina; a US-14 não lista a Secretaria como ator, e o
  painel do aluno (RAN-CAD-08.9) já é restrito ao Professor da Disciplina responsável pela turma.
- Q: O Coorientador do NUCOMP (com coorientação aceita) deve ter a mesma visibilidade de Status,
  histórico e entregas que o Orientador nesta spec (FR-009, FR-026), ou isso fica só a cargo da
  spec 006? → A: Fica com a spec 006; esta spec não altera permissões para o Coorientador — a 006
  decide como expor isso no seu próprio painel de orientandos, reaproveitando os serviços de
  consulta desta spec.

### Session 2026-10-23

- Q: Como o Aluno e o Professor chegam às abas "Meu TCC" e "Atividades"? As US-13, 14, 15 e 29
  dizem que o Aluno acessa o item "Turmas" e seleciona a turma, que abre na aba "Meu TCC"; as
  US-16 e 43 dizem que o Professor abre a turma e seleciona a aba "Atividades". Mas o FR-010 da
  spec 004 (já mesclada) diz que só o Professor da Disciplina e a Secretaria do curso abrem a turma
  e veem o item "Turmas". → A: Alternativa B (Célio Benjamim, 2026-10-23; índice Q-89): o Aluno
  ganha um item de menu "Turmas" próprio, com a lista das turmas em que está matriculado e o
  acesso às turmas arquivadas; a turma do Aluno abre na aba "Meu TCC", com as abas "Meu TCC" e
  "Atividades" (rotas desta spec). A tela da turma da spec 004 continua fechada ao Aluno (FR-010 da
  spec 004 sem mudança) e só ganha a barra de abas "Alunos" e "Atividades", com "Atividades"
  visível apenas ao Professor da Disciplina da turma. Alternativas rejeitadas: abrir a tela da
  turma da spec 004 ao Aluno (mudaria uma spec mesclada e exporia a lista de colegas) e só pôr links
  no Painel (contraria o passo 1 das US e não atende "Turmas arquivadas", E9 da US-13).

### Divergência encontrada na US-43 (v3.3) — ponto a decidir

A US-43 ("Cadastrar as entregas da turma") tem uma inconsistência de nomenclatura entre o passo 1
do fluxo principal e o restante da própria US:

- Passo 1: "o Professor da Disciplina acessa o item Turmas, seleciona a turma e abre a **aba
  Entregas**."
- Passos 2, 8 e todos os fluxos alternativos e de exceção (E1, E4): "aba **Atividades**" (ex.:
  passo 8, "O sistema mantém o Professor na aba Atividades"; E1, "o sistema apresenta... e o fluxo
  prossegue... na aba Atividades").
- As US-15 e US-16 (mesma feature) usam "aba Atividades" em todos os passos, sem nenhuma ocorrência
  de "aba Entregas".
- A US-43 (v3.3) também **removeu** o fluxo alternativo F que existia implicitamente na US-15
  ("Entrega do tipo Proposta", presente lá) — a US-43 atual vai de A a E, sem F; isso não é uma
  perda de conteúdo (o fluxo da US-15 já cobre o caso), mas confirma que a numeração dos fluxos não
  foi revisada de ponta a ponta na v3.3.

**Decisão desta spec (provisória, não escolhida por mim)**: por maioria de ocorrências (US-15,
US-16 e quase toda a US-43), esta spec usa **"aba Atividades"** como nome da aba nos requisitos e
nas mensagens, e trata "aba Entregas" do passo 1 da US-43 como lapso de digitação a confirmar com a
Profa. Diana ou com Leandra Matos (responsável pelas US-13 a 16, 29, 43 e 44). **Este item está
registrado em `docs/questoes-a-rever.md` (Q-80) e não bloqueia o planejamento, mas bloqueia a tela
antes de implementá-la.**

### Pontos decididos na conferência do analista-requisitos (2026-10-22)

1. **Mensagem ausente — US-29, fluxo alternativo B**: a US diz "a seção Versão final exibe o aviso
   'Data Limite vencida: o envio será registrado como Entregue com Atraso'", texto que não estava
   citado no FR-025 nem no Acceptance Scenario correspondente da User Story 6. **Decisão: incluir.**
   Adicionada como mensagem provisória **MF-01** na seção "Mensagens a validar com a PO" (é texto
   exato da US, mas segue a convenção do projeto de marcar como provisória toda mensagem de
   interface ainda não validada pela PO em uma nova spec, como nas specs 003 e 004) e referenciada
   no Acceptance Scenario 2 da User Story 6.
2. **Mensagem ausente — US-44, fluxo alternativo D**: a US diz "o Professor permanece na tela do
   aluno, com a mensagem 'Versão Final devolvida para ajuste'", ausente do FR-028 e do Acceptance
   Scenario 3 da User Story 7. **Decisão: incluir.** Adicionada como mensagem provisória **MF-02**
   e referenciada no Acceptance Scenario 3 da User Story 7.
3. **Nome do link de histórico — US-14**: o fluxo principal (passo 6 e pré-condições) chama o link
   de "Histórico do Status do TCC", mas o fluxo alternativo A (consulta pelo Orientador) chama o
   mesmo link apenas de "Histórico". **Decisão provisória: usar "Histórico do Status do TCC" como
   nome completo do link** (mais descritivo e usado no fluxo principal); "Histórico", no fluxo
   alternativo A, é tratado como referência abreviada ao mesmo link, não como um link diferente.
   Esta decisão depende de confirmação de Leandra Matos ou da Profa. Diana e foi registrada como
   **Q-81** em `docs/questoes-a-rever.md`.
4. **Cobertura de teste na fronteira com a spec 006**: a US-14 tem gatilhos ("Indicação de Apto
   para Defesa", "Liberação do resultado") disparados por ações de outra spec (006, Célio
   Benjamim), mas a gravação do Status e do histórico para esses gatilhos é responsabilidade do
   FR-012 **desta** spec. **Decisão: esta spec ganha Acceptance Scenarios próprios testando essa
   gravação** (ver User Story 2, cenários 8 a 11), para que o mapeamento gatilho → Status não fique
   sem teste em nenhuma das duas specs; a spec 006 testa apenas o disparo (a chamada ao serviço),
   não o resultado da gravação.
5. **Mensagens ausentes — US-43**: o passo 7 do fluxo principal pede "uma notificação no sistema e
   um e-mail com o Título e a Data Limite" a cada aluno da turma, e o E2/Cenário 8 pede que o
   sistema "destaque a Data Limite" quando ela for anterior à data do cadastro — nenhum dos dois
   cita o texto exato. **Decisão: incluir.** A implementação (T018/T019) criou as mensagens
   PROVISÓRIAS **MF-05** (notificação da entrega) e **MF-06** (Data Limite anterior a hoje), no
   mesmo padrão da MF-04, registradas como **Q-84** em `docs/questoes-a-rever.md`. O envio por
   e-mail do passo 7 não foi implementado nesta fase (só a notificação no sistema, única forma
   coberta pelo contrato de `services.notificar` reaproveitado desta spec); ver Q-84.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Aluno registra a Proposta e os dados do TCC (Priority: P1)

Como Aluno, registro a Proposta do meu TCC (Título, Resumo, Modalidade e, opcionalmente, Subtítulo
e Link do Documento da Proposta) na turma em que estou matriculado. Ao salvar, o TCC passa de "Sem
Proposta" para "Em Andamento", e, com a Proposta salva, também informo a Área de Interesse e as
Palavras-Chave do trabalho. Enquanto o TCC estiver "Em Andamento", posso alterar qualquer um desses
dados (mudança de tema), e meu orientador, quando houver, é avisado de cada alteração.

**Why this priority**: sem a Proposta, o TCC nunca muda de "Sem Proposta" e nenhuma outra US desta
spec (entregas, status, versão final) tem o que mostrar. É o ponto de entrada do fluxo todo.

**Independent Test**: pode ser testada isoladamente — criar um aluno com TCC "Sem Proposta", salvar
a Proposta pelo formulário, e verificar que o Status muda para "Em Andamento" e que os campos de
Área de Interesse e Palavras-Chave ficam disponíveis.

**Acceptance Scenarios**:

1. **Given** o Aluno está autenticado, vinculado à turma TCC 1 e o TCC está com o Status "Sem
   Proposta", **When** ele preenche Título, Resumo e a Modalidade "Monografia" e aciona "Salvar
   Proposta", **Then** o sistema cria a Proposta na turma, exibe "Proposta salva" e muda a etiqueta
   para "Em Andamento", escondendo o botão "Salvar Proposta" e liberando Área de Interesse e
   Palavras-Chave.
2. **Given** o Aluno já salvou a Proposta, **When** ele seleciona a Área de Interesse e informa de
   1 a 5 Palavras-Chave e aciona "Salvar alterações", **Then** o sistema grava a área e as palavras
   e exibe "Alterações salvas".
3. **Given** a turma tem uma entrega do tipo "Proposta" com Data Limite 10/09, **When** o Aluno
   salva a Proposta em 08/09, **Then** essa entrega passa ao status "Entregue"; se salva em 12/09,
   passa a "Entregue com Atraso" (o Status do TCC muda para "Em Andamento" nos dois casos).
4. **Given** o TCC está "Em Andamento" e tem orientador, **When** o Aluno altera o Título e salva,
   **Then** o novo Título é gravado e o Orientador recebe uma notificação; sem orientador, o
   sistema grava sem notificar.
5. **Given** o TCC está com o Status "Apto para Defesa" (ou o Aluno está Desistente, Reprovado,
   Jubilado, ou a turma está arquivada), **When** o Aluno abre a aba "Meu TCC", **Then** os campos
   aparecem apenas para leitura, sem os botões de salvar.
6. **Given** o Aluno deixa o Resumo em branco, ou informa um Título com 251 caracteres, ou um link
   que não comece com `https://`, ou nenhuma Palavra-Chave, **When** aciona o botão de salvar,
   **Then** o sistema não salva e exibe a mensagem específica de cada erro (campo obrigatório,
   limite de caracteres, formato do link ou "Informe de 1 a 5 Palavras-Chave").
7. **Given** o Aluno informa a mesma Palavra-Chave em duas caixas diferentes (ex.: "IoT" duas
   vezes), **When** aciona "Salvar alterações", **Then** o sistema não salva, destaca as caixas
   repetidas e exibe "Palavra-chave repetida." (MF-03; Clarifications, sessão 2026-10-22).
8. **Given** o Aluno está autenticado e matriculado numa turma não arquivada, **When** aciona o
   item de menu "Turmas" e seleciona a turma, **Then** o sistema abre a turma na aba "Meu TCC",
   com as abas "Meu TCC" e "Atividades"; a lista mostra só as turmas em que o Aluno está
   matriculado, e a tela da turma do Professor (lista de alunos, spec 004) continua inacessível a
   ele (US-13, passos 1 e 2; FR-031; Clarifications, sessão 2026-10-23).
9. **Given** a turma do Aluno foi arquivada, **When** ele abre "Turmas arquivadas", **Then** a turma
   aparece nessa lista (e não mais em "Turmas") e abre a aba "Meu TCC" apenas para consulta (US-13,
   E9; FR-031).

---

### User Story 2 - Status do TCC muda automaticamente e tem histórico e trilha (Priority: P1)

Como Aluno, Orientador ou Professor da Disciplina, acompanho o Status do TCC (Sem Proposta, Em
Andamento, Apto para Defesa, Aprovado para TCC 2, Aprovado, Aprovado com Correções, Concluído,
Reprovado, Desistente ou Jubilado) sem que ninguém o edite manualmente: ele muda só quando um
gatilho específico ocorre em outra tela, e cada mudança fica registrada no histórico (status
anterior, novo status, data, hora, responsável e gatilho) e na trilha visual da etapa atual.

**Why this priority**: é o eixo transversal da feature — toda ação das outras seis US (e de US de
outras specs, como Apto para Defesa e liberação do resultado) passa por aqui para definir o Status.
Sem isso, não há como saber em que etapa o TCC está.

**Independent Test**: pode ser testada isoladamente — disparar cada gatilho (vínculo à turma,
Proposta salva, encerramento da participação) e verificar o Status resultante e o registro no
histórico, sem depender da interface das outras US.

**Acceptance Scenarios**:

1. **Given** o Professor da Disciplina vincula o aluno a uma turma, **When** o vínculo é gravado,
   **Then** o TCC nasce com o Status "Sem Proposta" e o histórico registra o status anterior vazio,
   o gatilho "Vínculo à turma" e o Professor como responsável.
2. **Given** o TCC está "Sem Proposta", **When** o Aluno salva a Proposta, **Then** o Status passa
   a "Em Andamento" e o histórico registra o gatilho "Proposta salva" com o Aluno como responsável.
3. **Given** o aluno está com o Status "Aprovado para TCC 2" e é vinculado à turma de TCC 2,
   **When** o vínculo é gravado, **Then** o Status retorna a "Em Andamento" com o gatilho
   "Transferência para TCC 2", preservando o histórico anterior.
4. **Given** o Professor da Disciplina registra a desistência, a reprovação ou o jubilamento do
   aluno com justificativa, **When** o encerramento é confirmado, **Then** o Status passa ao valor
   escolhido, com o Professor como responsável e o gatilho "Encerramento da participação".
5. **Given** o Aluno (ou o Orientador, na tela de orientandos, ou o Professor da Disciplina, na
   tela do aluno) está autenticado, **When** aciona o link "Histórico do Status do TCC", **Then**
   o sistema exibe a lista cronológica (do mais antigo ao mais recente) e a trilha com a etapa
   atual destacada; um Docente sem vínculo com o TCC não vê nada.
6. **Given** o TCC passou a "Reprovado", "Desistente" ou "Jubilado", **When** alguém abre a trilha,
   **Then** ela termina na etapa em que ocorreu, sem as etapas seguintes do ciclo normal.
7. **Given** qualquer usuário autenticado, **When** procura um campo ou botão para editar o Status
   diretamente, **Then** não encontra: o Status aparece apenas como etiqueta somente leitura.
8. **Given** o TCC está "Em Andamento", a entrega "Documento para Defesa" está Entregue ou
   Entregue com Atraso e o Orientador aciona "Apto para Defesa" (gatilho disparado pela spec 006,
   US-42), **When** essa ação chama o serviço de gravação desta spec (FR-012), **Then** o Status
   passa a "Apto para Defesa" e o histórico registra o Orientador como responsável e o gatilho
   "Indicação de Apto para Defesa".
9. **Given** o TCC 1 está "Apto para Defesa" e a defesa foi realizada, **When** a banca libera o
   resultado com nota final 6,0 ou mais (gatilho disparado pela spec 006, US-27; limite conforme
   RBN-DEF-06.3), **Then** o Status passa a "Aprovado para TCC 2" e o histórico registra o gatilho
   "Liberação do resultado".
10. **Given** o TCC 2 está "Apto para Defesa" e a defesa foi realizada, **When** a banca libera o
    resultado com parecer "Aprovado", "Aprovado com Correções" ou nota final menor que 6,0, **Then**
    o Status passa, respectivamente, a "Aprovado", "Aprovado com Correções" ou "Reprovado", com o
    gatilho "Liberação do resultado" registrado no histórico.
11. **Given** um gatilho de outra spec (006) chama o serviço de gravação desta spec com um valor de
    Status fora da tabela fixa de gatilhos (FR-008), **When** a chamada ocorre, **Then** o serviço
    rejeita a chamada, sem gravar nenhuma linha no histórico — a spec 006 só pode disparar os
    gatilhos previstos no FR-008, nunca escrever o Status diretamente.

---

### User Story 3 - Professor cadastra as entregas da turma (Priority: P1)

Como Professor da Disciplina, cadastro as entregas da minha turma (Proposta, Documento para Defesa,
Versão Final ou Outra), com Título, Instruções opcionais e Data Limite, para que os alunos saibam o
que enviar e até quando — inclusive os alunos que já estavam matriculados antes do cadastro.

**Why this priority**: sem entregas cadastradas, não há nada para o aluno enviar (US-15), nada para
o professor acompanhar (US-16) e nenhuma pré-condição para Apto para Defesa ou para a Versão Final.

**Independent Test**: pode ser testada isoladamente — cadastrar uma entrega numa turma com alunos
já matriculados e verificar que a entrega aparece na lista, que cada aluno da turma recebe o
registro de status "Aguardando Envio" (ou "Não Entregue", se a Data Limite já passou) e a
notificação, e que a turma não aceita duas entregas do mesmo tipo (exceto "Outra").

**Acceptance Scenarios**:

1. **Given** o Professor da Disciplina está autenticado na aba Atividades da turma, **When**
   aciona "Cadastrar atividade", informa Título, o Tipo "Documento para Defesa" e a Data Limite e
   confirma, **Then** a entrega aparece na lista com o status "Aguardando Envio" para cada aluno,
   o sistema exibe "Entrega cadastrada" e cada aluno recebe notificação no sistema e por e-mail.
2. **Given** a turma é de TCC 1, **When** o Professor abre a lista Tipo, **Then** ela mostra
   Proposta, Documento para Defesa e Outra, sem Versão Final; em TCC 2, mostra Documento para
   Defesa, Versão Final e Outra, sem Proposta.
3. **Given** a turma tem a entrega "Entrega do Documento" com Data Limite 25/09/2026, **When** um
   aluno é vinculado à turma em 20/09/2026, **Then** a entrega aparece para esse aluno com o status
   "Aguardando Envio" (índice Q-41, serviço `criar_entregas_do_aluno`).
4. **Given** a turma já tem uma entrega do tipo "Documento para Defesa", **When** o Professor tenta
   cadastrar outra do mesmo tipo, **Then** o sistema não salva e exibe "A turma já tem uma entrega
   deste tipo".
5. **Given** a turma está arquivada, ou o Docente não é o Professor da Disciplina da turma,
   **When** abre a aba de entregas, **Then** vê a lista apenas para consulta, sem o botão
   "Cadastrar atividade".

---

### User Story 4 - Aluno envia ou substitui o link de uma entrega (Priority: P1)

Como Aluno, envio o link de cada entrega da minha turma (exceto a do tipo Proposta, cumprida ao
salvar a Proposta) e posso substituí-lo até a Data Limite, sendo lembrado do prazo antes de vencer.

**Why this priority**: é a ação mais frequente do Aluno nesta feature e alimenta diretamente o
acompanhamento do professor (US-16) e as pré-condições de Apto para Defesa.

**Independent Test**: pode ser testada isoladamente — com uma entrega já cadastrada, enviar um link
válido antes e depois da Data Limite e verificar o status resultante (Entregue / Entregue com
Atraso), e tentar substituir o link depois da Data Limite para confirmar que o campo vira somente
leitura.

**Acceptance Scenarios**:

1. **Given** existe a entrega "Documento para Defesa" com Data Limite 20/11 e o TCC está "Em
   Andamento", **When** o Aluno informa um link `https://` e envia em 18/11, **Then** o envio é
   registrado, o status passa a "Entregue", o sistema exibe "Entrega enviada" e o Professor da
   Disciplina é notificado.
2. **Given** a Data Limite é 20/11, **When** o Aluno envia o link em 21/11, **Then** o envio é
   aceito e o status passa a "Entregue com Atraso".
3. **Given** o Aluno não enviou o link, **When** passam as 23:59 da Data Limite, **Then** o status
   muda para "Não Entregue", mas o envio continua disponível (sem reprovação automática).
4. **Given** o Aluno enviou o link em 18/11 e a Data Limite é 20/11, **When** ele substitui o link
   em 19/11 e envia, **Then** o sistema grava a substituição, mantém o status do primeiro envio e
   notifica o Professor da Disciplina novamente.
5. **Given** faltam 7 dias, 48 horas ou 24 horas para a Data Limite e o Aluno não enviou, **When**
   o sistema verifica os prazos, **Then** o Aluno recebe lembrete no sistema e por e-mail (exceto
   em turma arquivada).
6. **Given** a entrega é do tipo Proposta, **When** o Aluno a abre na aba de entregas, **Then** a
   janela não tem campo de link e exibe "Esta entrega é cumprida ao salvar a Proposta".
7. **Given** o link informado está vazio, não começa com `https://` ou tem mais de 500 caracteres,
   **When** o Aluno aciona Enviar, **Then** o sistema não salva e exibe "O link deve começar com
   https:// e ter até 500 caracteres".
8. **Given** o Aluno já enviou o link e a Data Limite já passou (sem devolução pendente), ou o TCC
   não está "Em Andamento", ou o Aluno está Desistente/Reprovado/Jubilado, ou a turma está
   arquivada, **When** ele abre a entrega, **Then** o campo Link aparece apenas para leitura, sem o
   botão Enviar.
9. **Given** o Aluno está numa das abas da sua turma, **When** seleciona a aba "Atividades",
   **Then** o sistema lista as entregas da turma com Título, Data Limite e o status de envio do
   Aluno (US-15, passos 1 e 2; FR-031).

---

### User Story 5 - Professor acompanha as entregas dos alunos da turma (Priority: P2)

Como Professor da Disciplina, consulto, por aluno, o status de envio e o link de cada entrega da
minha turma, para saber quem já enviou e acessar o material.

**Why this priority**: depende das entregas cadastradas (US-43) e dos envios dos alunos (US-15)
para ter conteúdo; é consulta, não bloqueia o fluxo de ninguém, mas é essencial para o
acompanhamento do professor antes de liberar Apto para Defesa ou homologar a Versão Final.

**Independent Test**: pode ser testada isoladamente — com uma entrega e três alunos (um sem envio,
um no prazo, um com atraso), abrir o acompanhamento e verificar as três linhas com o status correto
e o link de quem enviou.

**Acceptance Scenarios**:

1. **Given** a turma tem 3 alunos e 2 enviaram o link da entrega "Documento para Defesa", **When**
   o Professor abre a entrega, **Then** o sistema exibe 3 linhas: duas com "Entregue" e o link, uma
   com "Aguardando Envio".
2. **Given** a Data Limite venceu e um aluno não enviou, **When** o Professor abre a entrega,
   **Then** a linha do aluno exibe "Não Entregue", sem link e sem mudança no Status do TCC.
3. **Given** a entrega é do tipo Proposta e o aluno já salvou a sua, **When** o Professor aciona
   "Ver Proposta" na linha do aluno, **Then** o sistema exibe a Proposta somente para leitura.
4. **Given** a turma ainda não tem entregas cadastradas, **When** o Professor abre a aba de
   entregas, **Then** o sistema exibe "Nenhuma entrega cadastrada" e o botão "Cadastrar atividade".
5. **Given** um Docente não é o Professor da Disciplina da turma, **When** tenta abrir o
   acompanhamento, **Then** o sistema não exibe a lista.
6. **Given** o Professor da Disciplina abriu a turma pelo item "Turmas" (tela da turma, aba
   "Alunos", spec 004), **When** seleciona a aba "Atividades", **Then** o sistema abre a lista de
   entregas da turma; a Secretaria do curso, que também abre essa tela, não vê a aba "Atividades"
   (US-16, passos 1 e 2; US-43, passo 1; FR-027; FR-031).

---

### User Story 6 - Aluno envia a Versão Final do TCC 2 (Priority: P2)

Como Aluno de TCC 2 com a banca já realizada e o parecer Aprovado ou Aprovado com Correções, envio
o link de um único PDF com o texto final corrigido, a Folha de Aprovação assinada e a ficha
catalográfica, para que seja homologado e o TCC seja concluído.

**Why this priority**: só existe depois da defesa (fora do escopo direto desta spec, mas consumida
dela); é o penúltimo passo do ciclo de vida do TCC 2, antes da homologação (US-44).

**Independent Test**: pode ser testada isoladamente — com um TCC 2 já "Aprovado" (sem depender da
banca real) e a entrega "Versão Final" cadastrada, enviar o link e verificar o status "Entregue" ou
"Entregue com Atraso" e a notificação ao Professor.

**Acceptance Scenarios**:

1. **Given** o TCC 2 foi aprovado com correções e a Data Limite da Versão Final é 30/11, **When**
   o Aluno informa o link do PDF final na seção "Versão final" e envia em 25/11, **Then** o envio
   é registrado, o status passa a "Entregue", o sistema exibe "Versão Final enviada" e o Professor
   da Disciplina é notificado.
2. **Given** a Data Limite da Versão Final já passou, **When** o Aluno abre a seção Versão final
   antes de enviar, **Then** o sistema exibe o aviso "Data Limite vencida: o envio será registrado
   como Entregue com Atraso" (MF-01); ao enviar o link, o envio é aceito com esse status.
3. **Given** o TCC 2 está Aprovado e sem link da Versão Final, **When** vence a Data Limite dessa
   entrega, **Then** o status de envio passa a "Não Entregue" e o Status do TCC permanece
   "Aprovado" (sem mudança pelo atraso).
4. **Given** o Professor devolveu a Versão Final com uma mensagem de ajuste, **When** o Aluno envia
   o novo link dentro da Data Limite, **Then** o status retorna a "Entregue" (ou "Entregue com
   Atraso", conforme a data).
5. **Given** a defesa do TCC 2 ainda não teve o resultado liberado, ou o Aluno está em turma de
   TCC 1, ou o parecer foi Reprovado, **When** o Aluno abre a aba Meu TCC, **Then** a seção "Versão
   final" não exibe o campo de link (mensagens específicas para cada caso).
6. **Given** a Versão Final já foi homologada, **When** o Aluno abre a seção, **Then** o link
   aparece apenas para leitura, com o status "Homologada" e sem botão Enviar.

---

### User Story 7 - Professor homologa ou devolve a Versão Final (Priority: P2)

Como Professor da Disciplina, homologo a Versão Final enviada pelo aluno — o que conclui o TCC — ou
a devolvo para ajuste com uma mensagem, garantindo que o TCC só se encerra com a versão corrigida e
conferida (em Sistemas de Informação, só depois do Orientador confirmar "Correções Conferidas").

**Why this priority**: é o gatilho final do ciclo de vida do TCC ("Homologação da Versão Final" →
Status "Concluído"); depende da US-29 (envio) e da US-14 (gravação do Status).

**Independent Test**: pode ser testada isoladamente — com a Versão Final já enviada, acionar
Homologar e verificar que o status de envio passa a "Homologada", o Status do TCC passa a
"Concluído" e a Secretaria é notificada; separadamente, acionar Devolver para Ajuste com mensagem e
verificar o status "Devolvida para Ajuste" e a notificação ao aluno.

**Acceptance Scenarios**:

1. **Given** o Aluno enviou o link da Versão Final, **When** o Professor da Disciplina confere o
   PDF e aciona "Homologar", **Then** o status de envio passa a "Homologada", o Status do TCC passa
   a "Concluído" (gatilho "Homologação da Versão Final"), a Secretaria é notificada e o sistema
   exibe "Versão Final homologada".
2. **Given** o TCC 2 é de Sistemas de Informação com parecer "Aprovado com Correções" e o Aluno
   enviou o link, **When** o Orientador ainda não acionou "Correções Conferidas" na tela de
   orientandos, **Then** o botão Homologar permanece indisponível ao Professor da Disciplina; após
   o Orientador confirmar, o botão passa a ficar disponível.
3. **Given** o Professor aciona "Devolver para Ajuste", **When** informa a Mensagem (obrigatória,
   até 500 caracteres) e confirma, **Then** o status passa a "Devolvida para Ajuste", o Aluno é
   notificado com essa mensagem para reenviar, e o sistema mantém o Professor na tela do aluno com
   a mensagem "Versão Final devolvida para ajuste" (MF-02).
4. **Given** o Professor confirma a devolução com o campo Mensagem vazio, **When** aciona
   confirmar, **Then** o sistema não devolve e destaca o campo.
5. **Given** o Aluno ainda não enviou o link da Versão Final, ou o Docente não é o Professor da
   Disciplina da turma, **When** abre a tela do aluno, **Then** os botões Homologar e Devolver para
   Ajuste não aparecem.

---

### Edge Cases

- O que acontece quando a Data Limite de uma entrega "Outra" (sem efeito no Status do TCC) vence
  sem envio? A entrega passa a "Não Entregue" como qualquer outra, sem nenhum efeito adicional —
  "Outra" só se distingue por não ser pré-condição de nenhum gatilho de Status.
- Como o sistema trata um aluno que salva a Proposta exatamente nos 23:59:59 da Data Limite da
  entrega do tipo Proposta? Conta como dentro do prazo (o limite documentado é "até 23:59").
- O que acontece se o Professor tentar cadastrar uma segunda entrega do tipo "Outra" na mesma
  turma? É permitido — a restrição de unicidade (`UNIQUE (tma_tur_id, tma_tipo)`) só vale para
  Proposta, Documento para Defesa e Versão Final.
- Como o histórico do Status do TCC se comporta quando o mesmo aluno tem dois TCCs (um de TCC 1
  "Aprovado para TCC 2" e um de TCC 2 "Em Andamento", após a transferência — RBN-CAD-08.6)? Cada
  linha de `TCCs` tem seu próprio `Historico_Status_TCC`; o histórico do TCC 1 permanece intacto e
  encerrado em "Aprovado para TCC 2", e o TCC 2 começa um novo histórico a partir de "Em Andamento".
- O que acontece com entregas de um aluno excluído da turma (US-09, spec 004)? Ficam apagadas se
  sem envio (regra já coberta pela spec 004, `remover_entregas_sem_envio`); com envio, a spec 004
  as preserva como histórico e esta spec não as exibe mais nas listas ativas (regra do contrato da
  spec 004, seção "Regra das entregas para as outras features").

## Requirements *(mandatory)*

### Functional Requirements — Proposta e dados do TCC (US-13)

- **FR-001** [RBN-CAD-07.1]: O sistema MUST exibir, para o Aluno autenticado e vinculado a uma turma não
  arquivada, a seção Proposta na aba Meu TCC, com os campos Título (obrigatório, até 250
  caracteres), Subtítulo (opcional, até 250), Resumo (obrigatório, até 1.000, com contador de
  caracteres restantes), Modalidade (obrigatório: Monografia ou Artigo Científico) e Link do
  Documento da Proposta (opcional, até 500 caracteres, iniciado por `https://`).
- **FR-002** [RBN-CAD-07.1, RBN-CAD-08.3]: O sistema MUST permitir salvar a Proposta somente quando o TCC do aluno estiver com
  o Status "Sem Proposta" e ainda não existir Proposta dele nessa turma; ao salvar, MUST criar a
  Proposta na turma ativa do aluno e mudar o Status do TCC para "Em Andamento" (gatilho "Proposta
  salva").
- **FR-003** [RBN-CAD-07.1, RBN-CAD-09.1, RBN-CAD-09.3]: O sistema MUST, ao salvar a Proposta, cumprir a entrega do tipo Proposta da turma
  (quando existir), com o status "Entregue" (salvamento até 23:59 da Data Limite) ou "Entregue com
  Atraso" (depois).
- **FR-004** [RBN-CAD-08.1]: O sistema MUST liberar, somente depois de a Proposta ser salva, os campos Área de
  Interesse (lista fixa de 10 valores) e Palavras-Chave (de 1 a 5, até 100 caracteres cada).
- **FR-005** [RBN-CAD-08.2]: O sistema MUST permitir, enquanto o Status do TCC for "Em Andamento", alterar
  qualquer um dos campos da Proposta, a Área de Interesse e as Palavras-Chave (mudança de tema) e
  MUST notificar o Orientador atual a cada alteração, quando houver orientador.
- **FR-006** [RBN-CAD-08.5]: O sistema MUST tornar os campos da Proposta e do TCC somente leitura, sem os botões
  de salvar, quando o Status do TCC não for "Sem Proposta" nem "Em Andamento", quando o aluno
  estiver Desistente, Reprovado ou Jubilado (`participacao_encerrada`), ou quando a turma estiver
  arquivada.
- **FR-007** [RBN-CAD-07.1, RBN-CAD-08.1]: O sistema MUST validar, ao salvar: campos obrigatórios preenchidos (mensagem "Campo
  obrigatório"), limites de caracteres de cada campo, formato do Link (`https://`, até 500
  caracteres), de 1 a 5 Palavras-Chave informadas e nenhuma Palavra-Chave repetida entre as caixas
  preenchidas (mensagem provisória MF-03; Clarifications, sessão 2026-10-22); nenhuma dessas
  validações MUST permitir salvar dados fora da regra.

- **FR-007a** [RBN-CAD-07.1]: O sistema MUST restringir a visibilidade do Resumo da Proposta ao
  próprio Aluno, ao Orientador **atual** (vínculo `Orientacoes` com `ori_status='Ativa'`, ou ao
  Docente indicado num pedido de orientação ainda pendente), ao Coorientador do NUCOMP **com
  coorientação aceita** (`Coorientacoes.coo_status='Ativa'`) e ao Professor da Disciplina da
  turma; Título e Modalidade MUST também ficar visíveis à banca, na agenda de defesas e nos
  relatórios de gestão (RAN-CAD-07, requisito não funcional de Confidencialidade). Completude
  adicionada na conferência do analista-requisitos (2026-10-22): a matriz já define a regra sem
  ambiguidade, sem necessidade de decisão. Qualificadores "atual"/"com coorientação aceita"
  explicitados na análise `/speckit-analyze` (achado A2), para o texto do FR bater exatamente com
  `services_tcc.pode_ver_resumo` (research C3).

### Functional Requirements — Status, histórico e trilha do TCC (US-14)

- **FR-008** [RBN-CAD-08.3]: O sistema MUST manter o Status do TCC como campo somente leitura, sem formulário nem
  botão de edição manual para nenhum perfil, atualizado exclusivamente pelos gatilhos fixos:
  Vínculo à turma, Proposta salva, Transferência para TCC 2, Indicação de Apto para Defesa,
  Liberação do resultado, Homologação da Versão Final e Encerramento da participação.
- **FR-009** [RBN-CAD-08.7]: O sistema MUST registrar, a cada mudança de Status, uma linha no histórico com o
  Status anterior, o novo Status, a data e a hora, o usuário responsável e o gatilho, e MUST
  disponibilizar essa consulta — pelo link "Histórico do Status do TCC" (nome provisório; ver
  Clarifications, item 3, e índice Q-81) — ao Aluno, ao Orientador (na tela de orientandos) e ao
  Professor da Disciplina (na tela do aluno); um Docente sem vínculo com o TCC MUST NOT visualizar
  esse histórico. A Secretaria do curso (que consulta turmas na spec 004, Q9) também MUST NOT
  visualizar esse histórico (Clarifications, sessão 2026-10-22).
- **FR-010** [RBN-CAD-08.8]: O sistema MUST exibir a trilha do Status do TCC com a etapa atual destacada: em TCC
  1, Em Andamento → Apto para Defesa → Aprovado para TCC 2; em TCC 2, Em Andamento → Apto para
  Defesa → (Aprovado ou Aprovado com Correções) → Concluído; com Reprovado, Desistente ou Jubilado,
  a trilha MUST terminar na etapa em que ocorreu.
- **FR-011** [RBN-CAD-08.3, RBN-CAD-08.6]: O sistema MUST manter, na transferência de um aluno "Aprovado para TCC 2" para a
  turma de TCC 2, o histórico do TCC 1 intacto e MUST iniciar o registro do novo Status ("Em
  Andamento", gatilho "Transferência para TCC 2") preservando a referência ao histórico anterior.
- **FR-012** [RBN-CAD-08.3, RBN-CAD-08.7]: O sistema MUST expor um serviço único e reutilizável por outras features (ex.: spec
  006) para registrar a mudança de Status e o histórico a partir de um gatilho, de forma que o
  Status nunca seja alterado diretamente em código fora desse serviço.

### Functional Requirements — Cadastro de entregas (US-43)

- **FR-013** [RBN-CAD-09.1]: O sistema MUST permitir que o Professor da Disciplina da turma (não arquivada)
  cadastre uma entrega com Tipo (Proposta, Documento para Defesa, Versão Final ou Outra — lista
  restrita a Proposta/Documento para Defesa/Outra em turma de TCC 1, e a Documento para
  Defesa/Versão Final/Outra em turma de TCC 2), Título (obrigatório, até 100 caracteres),
  Instruções (opcional, até 1.000 caracteres) e Data Limite (obrigatória, não anterior à data do
  cadastro, válida até 23:59).
- **FR-014** [RBN-CAD-09.1]: O sistema MUST impedir mais de uma entrega dos tipos Proposta, Documento para Defesa
  ou Versão Final por turma (mensagem "A turma já tem uma entrega deste tipo"); o tipo Outra MUST
  permitir repetição.
- **FR-015** [RBN-CAD-09.1, RBN-CAD-09.6]: O sistema MUST, ao cadastrar a entrega, criar o registro de status "Aguardando Envio"
  para cada aluno atualmente matriculado na turma com participação não encerrada, e MUST notificar
  cada um deles no sistema e por e-mail, com o Título e a Data Limite.
- **FR-016** [RBN-CAD-09.1]: O sistema MUST criar o registro de entrega ("Aguardando Envio" ou, se a Data Limite
  já tiver vencido, "Não Entregue") também para um aluno vinculado à turma **depois** do cadastro
  da entrega, usando o mesmo serviço compartilhado que cria os registros na matrícula e na
  transferência (`criar_entregas_do_aluno`, spec 004; índice Q-41).
- **FR-017** [RBN-CAD-09.1]: O sistema MUST restringir o cadastro de entregas ao Professor da Disciplina
  responsável pela turma e MUST impedir o cadastro (sem exibir o botão correspondente) em turma
  arquivada ou para outro Docente.

### Functional Requirements — Envio e substituição do link (US-15, US-29)

- **FR-018** [RBN-CAD-09.2]: O sistema MUST permitir ao Aluno enviar, em cada entrega cadastrada que não seja do
  tipo Proposta, um link obrigatório iniciado por `https://`, com até 500 caracteres, e MUST
  registrar o envio com o aluno, a data e a hora.
- **FR-019** [RBN-CAD-09.3]: O sistema MUST calcular o status de envio a partir do primeiro envio: "Entregue" até
  23:59 da Data Limite, "Entregue com Atraso" depois; MUST permitir substituir o link até a Data
  Limite (mantendo o status calculado pelo primeiro envio) e MUST tornar o campo somente leitura,
  sem o botão Enviar, depois da Data Limite, salvo nos casos de devolução para ajuste (US-44).
- **FR-020** [RBN-CAD-09.3]: O sistema MUST marcar a entrega como "Não Entregue" quando a Data Limite vencer sem
  nenhum envio, sem reprovar o aluno nem alterar o Status do TCC, e MUST manter o envio disponível
  mesmo após essa marcação.
- **FR-021** [RBN-CAD-09.6]: O sistema MUST notificar o Professor da Disciplina a cada envio e a cada substituição
  de link.
- **FR-022** [RBN-CAD-09.6]: O sistema MUST enviar lembretes de prazo (notificação no sistema e e-mail) 7 dias, 48
  horas e 24 horas antes da Data Limite, apenas aos alunos que ainda não enviaram e apenas em turma
  não arquivada.
- **FR-023** [RBN-CAD-09.2, RBN-CAD-08.5]: O sistema MUST desabilitar o envio (campo somente leitura, sem botão) quando o TCC
  não estiver "Em Andamento" (entregas Documento para Defesa e Outra), quando o aluno estiver
  Desistente/Reprovado/Jubilado, ou quando a turma estiver arquivada.
- **FR-024** [RBN-CAD-09.2, RBN-CAD-09.3]: Na entrega do tipo Versão Final (exclusiva de TCC 2), o sistema MUST liberar o envio
  somente depois da liberação do resultado da banca com parecer Aprovado ou Aprovado com Correções,
  e MUST ocultar o campo de link com o parecer Reprovado ou antes da liberação.
- **FR-025** [RBN-CAD-09.2, RBN-CAD-09.3]: O sistema MUST permitir o reenvio do link da Versão Final, dentro da Data Limite,
  quando o status de envio estiver "Devolvida para Ajuste" (US-44), recalculando o status como
  "Entregue" ou "Entregue com Atraso".

### Functional Requirements — Acompanhamento das entregas (US-16)

- **FR-026** [RBN-CAD-09.4]: O sistema MUST exibir ao Professor da Disciplina da turma uma lista somente leitura,
  por entrega, com uma linha por aluno da turma contendo nome, matrícula, status de envio e o link
  mais recente (com data e hora); na entrega do tipo Proposta, a coluna de link MUST ser substituída
  por um acesso à Proposta registrada, somente leitura.
- **FR-027** [RBN-CAD-09.4]: O sistema MUST restringir essa consulta ao Professor da Disciplina da turma e MUST
  exibir "Nenhuma entrega cadastrada" quando a turma ainda não tiver nenhuma entrega.

### Functional Requirements — Homologação da Versão Final (US-44)

- **FR-028** [RBN-CAD-09.5]: O sistema MUST permitir ao Professor da Disciplina da turma de TCC 2, após o envio do
  link da Versão Final pelo aluno, homologar (muda o status de envio para "Homologada", o Status do
  TCC para "Concluído" com o gatilho "Homologação da Versão Final", e notifica a Secretaria) ou
  devolver para ajuste (exige Mensagem obrigatória de até 500 caracteres, muda o status para
  "Devolvida para Ajuste" e notifica o Aluno).
- **FR-029** [RBN-CAD-09.5]: Em turma de Sistemas de Informação com parecer "Aprovado com Correções", o sistema
  MUST exigir que o Orientador confirme "Correções Conferidas" (sem campos, na tela de orientandos)
  antes de liberar o botão Homologar ao Professor da Disciplina.
- **FR-030** [RBN-CAD-09.5]: O sistema MUST ocultar os botões Homologar e Devolver para Ajuste quando o Aluno ainda
  não tiver enviado o link da Versão Final, ou para um Docente que não seja o Professor da
  Disciplina da turma.

### Functional Requirements — Navegação até as telas desta spec (US-13, US-15, US-16, US-43)

- **FR-031** [US-13, US-15, US-16, US-43; RAN-CAD-08, RAN-CAD-09]: O sistema MUST oferecer ao Aluno um item de menu "Turmas"
  com as turmas não arquivadas em que ele está matriculado e o acesso a "Turmas arquivadas"
  (somente consulta); a turma escolhida MUST abrir na aba "Meu TCC", com as abas "Meu TCC" e
  "Atividades" (nome provisório, Q-80). Na tela da turma da spec 004, o sistema MUST exibir as
  abas "Alunos" e "Atividades", esta só para o Professor da Disciplina da turma (FR-017, FR-027).
  O item "Turmas" do Aluno MUST NOT dar acesso à tela da turma da spec 004 nem à lista de alunos,
  que continuam restritas pelo FR-010 da spec 004 (Clarifications, sessão 2026-10-23; índice Q-89).

### Key Entities *(reaproveitadas da spec 001; nenhuma nova)*

- **TCCs**: o trabalho de um aluno numa turma. Campos usados nesta spec: título, subtítulo, resumo,
  modalidade, link da proposta, área de interesse (`tcc_ari_id`), status, justificativa de
  encerramento. Uma Proposta por aluno por turma (`UNIQUE (tcc_alu_id, tcc_tur_id)`).
- **PalavrasChave_TCC**: de 1 a 5 palavras-chave por TCC, cada uma até 100 caracteres.
- **Historico_Status_TCC**: uma linha por mudança de Status, com status anterior, novo status,
  gatilho, data/hora, usuário responsável e a turma no momento da mudança.
- **Turmas_Marcos**: a entrega cadastrada pelo Professor (tipo, título, instruções, data limite),
  no máximo uma de cada tipo por turma, exceto "Outra".
- **Entregas_Marcos**: o status de envio de um aluno numa entrega (Aguardando Envio, Entregue,
  Entregue com Atraso, Não Entregue, Devolvida para Ajuste ou Homologada), com feedback da
  devolução e data da avaliação.
- **Historico_Envios_Entregas**: cada envio ou substituição de link, com o link e a data/hora
  exatos — base para "o status calculado pelo primeiro envio" e para o link "mais recente" exibido
  ao professor.

## Mensagens a validar com a PO

Textos já citados entre aspas nas US v3.3, mas que não constavam dos Acceptance Scenarios antes da
conferência do analista-requisitos (2026-10-22). São **PROVISÓRIOS** pela mesma convenção das
specs 003 e 004: servem para planejar, testar e implementar e precisam da validação da Product
Owner (Profa. Diana), mesmo sendo texto exato da fonte.

| ID | Situação em que aparece | Texto proposto (PROVISÓRIO) | Origem | Situação |
|---|---|---|---|---|
| MF-01 | Versão final: Data Limite da entrega já vencida, antes do envio | "Data Limite vencida: o envio será registrado como Entregue com Atraso." | US-29, fluxo alternativo B | A validar |
| MF-02 | Confirmação da devolução da Versão Final para ajuste | "Versão Final devolvida para ajuste." | US-44, fluxo alternativo D | A validar |
| MF-03 | Palavra-Chave repetida entre as caixas preenchidas | "Palavra-chave repetida." | Clarifications, sessão 2026-10-22; FR-007 | A validar |
| MF-04 | Notificação ao Orientador a cada mudança de tema (Título, Subtítulo, Resumo, Modalidade ou Link) | "{nome} alterou os dados do TCC na turma {identificador}." | US-13, fluxo alternativo A ("envia uma notificação ao Orientador", sem texto exato citado); índice Q-83 | A validar |
| MF-05 | Notificação a cada aluno da turma ao cadastrar uma entrega | "Nova entrega cadastrada na turma {identificador}: {titulo}, com prazo até {data_limite}." | US-43, passo 7 ("uma notificação no sistema e um e-mail com o Título e a Data Limite", sem texto exato citado); índice Q-84 | A validar |
| MF-06 | Data Limite anterior à data do cadastro, no formulário de cadastro de entrega | "A Data Limite não pode ser anterior a hoje." | US-43, E2 e Cenário 8 ("destaca a Data Limite", sem texto exato citado); índice Q-84 | A validar |
| MF-07 | Notificação ao Professor da Disciplina a cada envio ou substituição de link de uma entrega | "{nome} enviou a entrega {titulo} na turma {identificador}." | US-15, passo 6 e fluxo alternativo D (sem texto exato citado); índice Q-85 | A validar |
| MF-08 | Lembrete de prazo ao aluno que ainda não enviou, 7 dias, 48 horas e 24 horas antes da Data Limite | "Lembrete: a entrega {titulo} da turma {identificador} vence em {data_limite}." | US-15, fluxo alternativo E ("envia notificação no sistema e e-mail", sem texto exato citado); índice Q-86 | A validar |
| MF-09 | Notificação à Secretaria do curso na homologação da Versão Final | "Versão Final de {nome} homologada na turma {identificador}: TCC concluído." | US-44, passo 6 ("notifica a Secretaria", sem texto exato citado); índice Q-88 | A validar |
| MF-10 | Notificação ao Aluno na devolução da Versão Final para ajuste, com a mensagem do Professor | "Versão Final devolvida para ajuste na turma {identificador}: {mensagem}" | US-44, fluxo alternativo D ("notifica o Aluno", sem texto exato citado); índice Q-88 | A validar |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um Aluno consegue registrar a Proposta completa (Título, Resumo, Modalidade) e salvar
  em menos de 2 minutos, a partir da tela da turma.
- **SC-002**: 100% das mudanças de Status do TCC nos testes automatizados ocorrem apenas pelos sete
  gatilhos fixos, nunca por edição direta de um campo editável na interface.
- **SC-003**: Um Professor da Disciplina consegue cadastrar uma entrega nova e ver a confirmação de
  que todos os alunos da turma foram notificados em menos de 1 minuto.
- **SC-004**: O status de envio de uma entrega (Entregue, Entregue com Atraso ou Não Entregue) é
  calculado automaticamente, sem decisão manual de nenhum usuário, em 100% dos casos testados.
- **SC-005**: Todos os 97 cenários de aceite desta spec (89 cenários originais das US-13, 14, 15,
  16, 29, 43 e 44 — fluxos principais, alternativos e de exceção — mais os cenários novos
  acrescentados na conferência do analista-requisitos e no `/speckit-clarify`, e os 4 de navegação
  da sessão 2026-10-23, contados em `plan.md`, Scale/Scope) têm pelo menos um teste automatizado
  correspondente.
- **SC-006**: 100% das mensagens exibidas ao usuário por esta feature são idênticas, caractere por
  caractere, ao texto entre aspas das US-13, 14, 15, 16, 29, 43 e 44, ou estão marcadas como
  provisórias em `docs/questoes-a-rever.md`.

## Assumptions

- O nome exato da aba de entregas ("Atividades" ou "Entregas") segue provisoriamente "Atividades"
  por maioria de ocorrências na v3.3 (ver seção Clarifications); a confirmação final depende da
  Profa. Diana ou de Leandra Matos e será registrada em `docs/questoes-a-rever.md`.
- O serviço que grava o Status do TCC e o histórico (FR-012) é definido nesta spec e exposto como
  contrato para a spec 006, que dispara os gatilhos "Indicação de Apto para Defesa" e "Liberação do
  resultado" sem duplicar a lógica de gravação.
- Esta spec não implementa a geração da Folha de Aprovação em PDF nem o cálculo de notas e parecer
  da banca (US-27, US-28, spec 006 — orientação, defesa, atas e publicações, responsável Célio
  Benjamim) — apenas consome o resultado (parecer liberado) como pré-condição do envio da Versão
  Final. Confirmado: só existe a spec 006 depois desta; não há spec de Defesa separada.
- A tabela de equivalência de cursos e a regra "Professor da Disciplina também é Orientador"
  (Engenharia de Computação e Licenciatura em Computação) já existem na spec 004
  (`turma_tem_orientador_automatico`, `cargas.py`) e são apenas consultadas aqui.
- Os lembretes de prazo (7 dias, 48h, 24h) dependem de uma rotina agendada (research/plano, a
  detalhar no `/speckit-plan`), fora do escopo de uma view síncrona.
