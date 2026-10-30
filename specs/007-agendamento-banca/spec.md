# Feature Specification: Agendamento e Banca do SIGTCC

**Feature Branch**: `feature/feat-07-agendamento`

**Created**: 2026-10-30

**Status**: Approved (Julia Cohen, 2026-10-30)

**Input**: User description: "Agendamento e Banca do SIGTCC: US-21, US-22, US-23, US-24 e US-40, mais o filtro de Curso da tela Defesas (US-39)."

**Responsável pelas US de origem**: Célio Benjamim (US-21, 22, 23, 24, 40); Maria Luísa Gomes (US-39, mecanismo geral). Esta spec implementa, para o módulo de Defesa.

## Dependências e reaproveitamento

- **Modelo de dados**: já existe (spec 001, Épico 2 — Defesa). Esta spec **não cria tabelas sem
  perguntar antes**. Usa `Defesas`, `DefesasPresenciais`, `DefesasRemotas`, `BancaDefesa`,
  `HistoricoDefesas` (`sigtcc/apps/defesa/models.py`) e os choices `StatusSessao`, `FormatoSessao`,
  `PapelBanca`, `EventoDefesa` (`sigtcc/apps/defesa/choices.py`), já alinhados ao dicionário de
  dados (seções 3.6.1 a 3.6.4 e 3.6.7). O Local da defesa presencial é texto livre até 100
  caracteres (`DefesasPresenciais.dep_local`) — não há tabela de Salas (CR-2026-0001, já refletida
  no dicionário e na matriz, RBN-DEF-03.1 "sai a verificação de conflito de sala").
- **Serviços reutilizados**:
  - `services.notificar(usuario, mensagem, link=None, agora=None)` e
    `services.enviar_email_apos_commit(usuario, assunto, template, contexto)` — única forma de
    notificar e de enviar e-mail. O contrato publicado é o da spec 004-turmas-alunos
    (`contracts/servicos-compartilhados.md`, §4, "acréscimos ao contrato da spec 003"); o
    parâmetro `agora=None` de `notificar` foi acrescentado pela spec 006 (IC-12). Correção da
    conferência do analista-requisitos (2026-10-30): a atribuição original a "spec
    003-acesso-login" estava errada (a 003 só define a base, a 004 publica o contrato real).
  - `services_entregas.link_mais_recente(entrega)` (feat-05, spec 005-fluxo-do-tcc,
    `contracts/servicos-compartilhados.md`, §3) — devolve o último `HistoricoEnviosEntregas` da
    entrega do tipo Documento para Defesa, para montar a notificação do agendamento (FR-018) com o
    link do documento; o próprio contrato da spec 005 já previa esse uso pela Defesa. Acrescentado
    na conferência do analista-requisitos (2026-10-30; estava ausente, risco de reinventar a
    consulta no plano).
  - `services_turmas.atualizar_status_tcc` (feat-05, spec 005-fluxo-do-tcc) — esta spec **não**
    grava `tcc_status`; só lê o Status "Apto para Defesa" para listar TCCs elegíveis. A transição
    "Indicação de Apto para Defesa" é gravada pela US-42 (spec 006); a "Liberação do resultado",
    pela US-27 (feature futura "Avaliação e Resultados", feat-08), consumindo o serviço de status
    da sessão desta spec (ver "Contratos" abaixo).
  - `services_orientacao.orientador_atual(tcc)`, `coorientadores_ativos(tcc)`,
    `e_orientador_atual(usuario, tcc)`, `e_coorientador_ativo(usuario, tcc)` (feat-06, spec
    006-orientacao) — para identificar o Presidente da banca e excluir orientador/coorientadores
    da lista de avaliadores (RBN-DEF-02.1).
  - `services_orientacao.cancelar_troca_no_agendamento(tcc, agora)` (feat-06) — **obrigatória** na
    confirmação do agendamento (US-24, fluxo A), chamada com o TCC já travado e o mesmo `agora`
    gravado no evento 'Agendamento' de `Historico_Defesas` (contrato da spec 006, §3 e §5).
  - Validade do Membro Externo (feat-04, spec 002-gestao-contas): a lista de avaliadores usa
    `services_contas.membros_externos_disponiveis()`, que traz os Membros Externos com Status da
    Conta "Aguardando Ativação", "Ativa" ou "Expirada" (o Membro Externo não tem o status
    "Inativa" — contrato da spec 002, §1); **não filtra só por "Ativa"**. Correção da conferência
    do analista-requisitos (2026-10-30; bloqueante B1): a versão anterior desta spec dizia "pelo
    Status da Conta Ativa, igual aos Docentes", o que contradiria o próprio FR-010 e o Acceptance
    Scenario 4 da User Story 2 — um Membro Externo recém-cadastrado nasce "Aguardando Ativação" e
    precisa ficar imediatamente selecionável na banca, não some da lista por causa do status. O
    cadastro rápido (US-23, fluxo B) reaproveita o formulário de cadastro de Membro Externo da
    US-05 (spec 002).
  - `services_contas.filtro_de_curso(usuario, valor)` (feat-04, spec 002-gestao-contas,
    `services_contas.py`) — mecanismo geral do filtro de Curso (US-39); esta spec só **aplica**
    esse componente à tela Defesas (US-40, fluxo alternativo A), sem reimplementá-lo.
    `curso_id_do_usuario(usuario)` usado por `filtro_de_curso` está em `permissoes.py`, não em
    `services_contas.py` (correção da conferência do analista-requisitos, 2026-10-30; P4 —
    atribuição errada de módulo na versão anterior).
- **Serviço consumido, ainda não entregue**: `services_avaliacoes.descartar_avaliacoes(sessao,
  membro=None)` (feature futura "Avaliação e Resultados", feat-08, Célio Benjamim) — descarta as
  notas salvas por um membro (ou por todos, se `membro=None`). **Esta spec usa um stub com essa
  assinatura** até a feat-08 entregar a função real, chamado nos 3 pontos corretos (corrigido na
  conferência do analista-requisitos, 2026-10-30; bloqueante B2 — ver Clarifications): o
  **cancelamento** da sessão (FR-020, descarta todas as notas), a **alteração da banca** (FR-011,
  descarta só as do membro substituído) e o **acionamento do suplente** (FR-013, descarta só as do
  titular ausente). O **reagendamento** (FR-019) **não** chama esse serviço: a US-24 e o próprio
  FR-019 desta spec dizem explicitamente que o reagendamento mantém a banca e as avaliações já
  salvas.

## Contratos desta feature (o que a feat-08 e a feat-09, de Célio Benjamim, vão consumir)

- `services_defesa.membros_efetivos(sessao) -> list` — membros que de fato atuam na sessão,
  considerando o suplente acionado (substitui o titular ausente).
- `services_defesa.transicionar_status(sessao, novo_status, autor, justificativa=None,
  **dados_evento) -> Defesas` — único ponto que muda `def_status` (Agendada, Reagendada, Em
  Andamento, Realizada, Cancelada) e grava `HistoricoDefesas` via `registrar_evento`; a feat-08
  chama para a transição Em Andamento → Realizada (liberação do resultado, US-27) e a feat-09
  (ouvintes/documentos) só lê o status.
- `services_defesa.registrar_evento(sessao, tipo, justificativa, autor, **dados) -> HistoricoDefesas`
  — grava uma linha do histórico da defesa (DEF-01.6): agendamento, reagendamento, cancelamento,
  alteração da banca, acionamento de suplente, início automático ou liberação do resultado.
- Componente do filtro de período (DEF-01.5), reaproveitável por outras listas de defesa
  (agenda, ouvintes, relatórios): atalhos (Período Letivo, Esta Semana, Este Mês, Próximos 30
  Dias) e intervalo manual, com o filtro de Curso (US-39) combinado.
- Template base da janela "Sessão de defesa" (`sigtcc/templates/defesa/sessao.html`), com blocos
  reservados (`{% block avaliacao %}`, `{% block resultado %}`, `{% block documentos %}`,
  `{% block ouvintes %}`, `{% block ocorrencias %}`) para a feat-08 e a feat-09 preencherem sem
  reescrever o cabeçalho da sessão (data, horário, TCC, banca, status).
- `popular_demo` (comando de gestão) ganha TCCs "Apto para Defesa" e uma sessão em cada um dos 5
  valores de `StatusSessao`, para a feat-08 e a feat-09 testarem sem montar cenário do zero.

## Clarifications

### Session 2026-10-30

- Q: Como tratar `descartar_avaliacoes(sessao, membro=None)`, serviço da feat-08 que ainda não
  existe, mas que o **cancelamento**, a **alteração da banca** e o **acionamento do suplente**
  desta spec precisam chamar (o **reagendamento** não chama — mantém a banca e as avaliações
  salvas, FR-019)? → A: usar um stub em `services_defesa.py` com essa assinatura exata, que por
  ora só registra (log ou `HistoricoDefesas`, dado de implementação) que o descarte foi solicitado,
  sem apagar nada de `Avaliacoes` (tabela que esta spec não possui nem deve tocar) — substituído
  pela chamada real quando a feat-08 entregar a função, sem mudar a assinatura nem o ponto de
  chamada. Correção da conferência do analista-requisitos (2026-10-30; bloqueante B2): a decisão
  original desta sessão citava erradamente o reagendamento em vez do cancelamento entre os 3
  pontos de chamada.
- Q: O filtro de Membros Externos na composição da banca usa só o Status "Ativa", ou todos os
  status possíveis? → A: todos — "Aguardando Ativação", "Ativa" e "Expirada" (o Membro Externo não
  tem o status "Inativa"), via `services_contas.membros_externos_disponiveis()` (contrato da spec
  002, §1). Correção da conferência do analista-requisitos (2026-10-30; bloqueante B1): a decisão
  original desta sessão dizia "igual aos Docentes" (só "Ativa"), o que contradizia o próprio
  FR-010 e o Acceptance Scenario 4 da User Story 2 (Membro Externo recém-cadastrado precisa ficar
  disponível de imediato, com a conta "Aguardando Ativação").
- Q: A US-40 (fluxo alternativo B, "Consulta do histórico pela tela do aluno") e a matriz
  (RBN-DEF-01.6) citam o botão "Histórico da defesa" aberto também a partir do painel do aluno
  (US-41, spec futura) e da tela de orientandos (US-18, spec 006); essa spec deve cobrir esse
  ponto de entrada com um Acceptance Scenario próprio? → A: não — fica registrado como Edge Case
  (ver abaixo) e fora do escopo desta spec: as telas de origem (painel do aluno e tela de
  orientandos) não são desta feature, e o link para elas é só uma chamada ao mesmo serviço de
  histórico (`registrar_evento`/consulta), sem lógica nova aqui. A spec 006 ou a futura US-41
  inserem o link apontando para a mesma janela "Histórico da defesa". Achado da conferência do
  analista-requisitos (2026-10-30; ponto a decidir P1); SC-005 ajustado para não prometer esse
  cenário.
- Q: O cenário "Transição para Realizada" (US-24, fluxo alternativo E) precisa de Acceptance
  Scenario nesta spec? → A: não — já está nas Assumptions como responsabilidade da feat-08
  (liberação do resultado, US-27); registrado agora também como Edge Case explícito, e o texto do
  SC-005 foi ajustado para não prometer cobertura de teste desse cenário específico nesta spec.
  Achado da conferência do analista-requisitos (2026-10-30; ponto a decidir P2).
- Q: Quando um TCC "Apto para Defesa" com sessão "Agendada", "Reagendada" ou "Em Andamento" tem a
  participação do aluno encerrada (Desistente, Reprovado ou Jubilado, spec 004/005), esta spec
  deve cancelar automaticamente a sessão, ou isso fica fora do escopo? → A: inicialmente decidido
  que esta spec implementaria o cancelamento automático (Opção A), **revertido na mesma sessão**
  ao verificar `services_turmas.encerrar_participacao` (spec 004, já mesclada): essa função **já
  recusa** o encerramento quando há sessão "Agendada", "Reagendada" ou "Em Andamento" para o TCC
  (`STATUS_SESSAO_ATIVA`, mensagem MT30, "Não é possível encerrar a participação: há sessão de
  defesa ativa"), com teste já existente (`test_us09_exclusao.py`). As duas regras não podiam
  coexistir. **Decisão final (Julia Cohen, 2026-10-30): manter o MT30 como está, sem alteração em
  `services_turmas.py`.** Quem quiser encerrar a participação de um aluno com defesa agendada
  precisa primeiro cancelar ou reagendar a sessão (fora do âmbito desta sessão de encerramento).
  Ver Edge Cases.
- Q: O botão "Agendar defesa" na aba Defesas da turma (spec 004) e na tela de orientandos (spec
  006) — telas já mescladas de outras features — deve ser inserido por esta spec, ou fica para
  depois, com esta spec entregando só a rota/formulário reutilizável? → A: **esta spec insere o
  botão** nas duas telas já mescladas (decisão de Julia Cohen, 2026-10-30), no mesmo padrão de
  tocar código mesclado já usado na spec 005 (Q-46). Ver FR-006 (já previa o comportamento; agora
  explicitamente a cargo desta spec) e a pendência de aprovação correspondente em
  `docs/questoes-a-rever.md`.
- Correção do `/speckit-analyze` (2026-10-30; achado D1): FR-006, FR-015, FR-016, FR-022, FR-023,
  FR-026, FR-028 e FR-030 estavam sem a tag `[RBN-...]`, exigida pelo princípio II da constituição.
  Tags acrescentadas, conferidas em `docs/fonte/Matriz_Requisitos_17_10.md` (aba
  `Requisitos_Defesa`): FR-006 → RBN-DEF-01.1 (lista de TCCs elegíveis, mesmo campo do
  agendamento, agora acessada por mais de um ponto de entrada); FR-015/FR-016 → RBN-DEF-03.1
  (mesmo RBN do FR-014, que esses dois FRs detalham); FR-022 → RBN-DEF-03.3 (mesmo RBN do
  FR-019/FR-020, sobre quem vê os botões); FR-023 → RBN-DEF-01.2 (mesmo RBN do FR-017, sobre o
  gatilho único de cada transição); FR-026/FR-028 → RBN-DEF-01.4 (lista de sessões e seu filtro de
  Status); FR-030 → RBN-DEF-01.4 (regra de visibilidade por perfil, mesmo RBN do FR-024).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Agendar a defesa com data, horário, formato e local ou link (Priority: P1)

Como Orientador (em Engenharia de Computação) ou Professor da Disciplina (em Sistemas de
Informação ou Licenciatura em Computação), agendo a sessão de defesa de um TCC Apto para Defesa
sob minha responsabilidade, escolhendo a data, o horário de início, o formato (Presencial ou
Remota) e o Local ou o Link da Videochamada correspondente.

**Why this priority**: sem os dados básicos da sessão, não há o que compor com banca (User Story
2) nem o que validar contra conflitos (User Story 3) — é o ponto de entrada do módulo.

**Independent Test**: criar um TCC "Apto para Defesa" sem sessão ativa, abrir o formulário de
agendamento, preencher os campos básicos (sem avançar para banca/conflito, que têm suas próprias
histórias) e confirmar que o formulário valida cada campo isoladamente.

**Acceptance Scenarios**:

1. **Given** o Orientador de Engenharia de Computação tem um TCC Apto para Defesa, sem sessão
   ativa, **When** seleciona o TCC, informa data futura, Horário de Início 14:00, Formato
   Presencial e Local "Laboratório LSI", **Then** o sistema aceita os dados básicos e indica a
   reserva automática de 1 hora para a sessão.
2. **Given** o Professor da Disciplina de Sistemas de Informação tem um TCC Apto para Defesa,
   **When** escolhe Formato Remota e informa o Link da Videochamada iniciado por `https://`,
   **Then** o sistema aceita o link.
3. **Given** o usuário abriu o formulário com o Local preenchido, **When** troca o Formato da
   Sessão de Presencial para Remota, **Then** o sistema limpa o Local e exibe o campo Link da
   Videochamada (e vice-versa).
4. **Given** o Professor da Disciplina abriu a aba Defesas de uma turma (ou o Orientador abriu a
   tela de orientandos), **When** aciona "Agendar defesa", **Then** o formulário abre com a lista
   TCC limitada aos TCCs elegíveis da turma ou do orientando.
5. **Given** nenhum TCC sob a responsabilidade do usuário está Apto para Defesa sem sessão ativa,
   **When** aciona "Agendar defesa", **Then** o sistema não abre o formulário e exibe "Nenhum TCC
   disponível para agendamento".
6. **Given** o usuário deixa TCC, Data, Horário de Início, Formato ou Local/Link em branco, ou
   informa uma data/horário já passado, ou um Local com mais de 100 caracteres, ou um Link sem
   `https://` ou com mais de 500 caracteres, **When** aciona "Agendar", **Then** o sistema não
   avança e exibe a mensagem específica de cada erro, sem gravar nenhuma sessão.
7. **Given** um Professor da Disciplina tenta agendar um TCC de Engenharia de Computação, ou um
   Orientador tenta agendar um TCC de Sistemas de Informação ou Licenciatura em Computação,
   **When** acessa a função de agendamento, **Then** o sistema bloqueia o acesso e exibe "Este TCC
   não pode ser agendado por você".
8. **Given** o usuário não está autenticado, **When** tenta abrir a tela Defesas ou o formulário de
   agendamento, **Then** o sistema exibe a tela de login e, após a autenticação, a tela ou o
   formulário pedido.

---

### User Story 2 - Compor e alterar a banca examinadora (Priority: P1)

Como Orientador ou Professor da Disciplina, componho a banca examinadora (Presidente, 1º e 2º
Avaliadores e, opcionalmente, um Suplente) ao agendar a defesa, posso alterá-la antes da sessão
com justificativa, e, como Orientador, posso acionar o suplente durante a sessão em andamento se
um titular faltar.

**Why this priority**: a banca é parte obrigatória do formulário de agendamento (FR-013 a FR-017);
sem ela, a sessão não pode ser confirmada (User Story 4).

**Independent Test**: com um TCC com Orientador vinculado, abrir a seção Banca examinadora e
compor os 2 ou 3 avaliadores, sem depender da confirmação final da sessão (User Story 4).

**Acceptance Scenarios**:

1. **Given** o Orientador abriu a seção Banca examinadora, **When** observa o campo Orientador
   (Presidente), **Then** ele vem preenchido com o orientador do trabalho, somente leitura, sem
   opção de alteração nem remoção.
2. **Given** o usuário escolheu o 1º Avaliador, **When** abre as listas do 2º Avaliador e do
   Suplente, **Then** a pessoa já escolhida não aparece nelas; escolhido o 2º Avaliador, ele
   também desaparece da lista do Suplente.
3. **Given** o usuário manteve o Suplente como "Sem suplente", **When** confirma a banca, **Then**
   o sistema aceita a composição só com os 3 membros titulares.
4. **Given** o avaliador externo desejado não consta na lista, **When** o usuário aciona "O
   Membro Externo não está na lista? Cadastrar", preenche Nome Completo, E-mail, Titulação e
   Instituição de Origem e salva, **Then** o sistema grava o Membro Externo com a conta
   "Aguardando Ativação" e o deixa disponível no campo da banca que estava sendo preenchido.
5. **Given** a sessão está Agendada ou Reagendada, **When** o Orientador ou o Professor da
   Disciplina aciona "Alterar banca", troca um avaliador, informa a Justificativa (até 500
   caracteres) e salva, **Then** o sistema grava a troca, descarta as avaliações salvas pelo
   membro substituído, e notifica os membros incluídos, os removidos e o Aluno.
6. **Given** a sessão está Em Andamento e um titular faltou, com suplente indicado, **When** o
   Orientador aciona "Acionar suplente", escolhe o avaliador substituído, informa a Justificativa
   e confirma, **Then** o suplente assume como titular, as notas do substituído são descartadas, e
   o evento é registrado no histórico da defesa.
7. **Given** o usuário não escolheu o 1º ou o 2º Avaliador, ou selecionou o mesmo docente em dois
   papéis, ou indicou o orientador/um coorientador como avaliador, **When** confirma, **Then** o
   sistema não avança e exibe a mensagem específica ("Campo obrigatório" ou "Selecione avaliadores
   distintos que não façam parte da orientação do trabalho").
8. **Given** o usuário confirma a alteração da banca ou o acionamento do suplente com a
   Justificativa vazia ou acima de 500 caracteres, **When** confirma, **Then** o sistema não salva
   e exibe "Informe uma justificativa de até 500 caracteres".
9. **Given** o Orientador informa que não poderá comparecer, **When** alguém tenta substituí-lo
   pela alteração simples de banca, **Then** o sistema não altera a banca e exibe "A ausência do
   Orientador exige o reagendamento da sessão".
10. **Given** a sessão está Em Andamento sem suplente indicado e um titular falta, **When** o
    Orientador abre a sessão, **Then** o botão "Acionar suplente" não aparece, e a sessão deve ser
    reagendada.
11. **Given** quem abre a sessão Em Andamento não é o Orientador, **When** tenta acionar o
    suplente, **Then** o botão não aparece, e uma tentativa direta é bloqueada com "Você não tem
    permissão para esta ação".

---

### User Story 3 - Impedir agendamentos com conflito de horário da banca (Priority: P1)

Como sistema, ao confirmar um agendamento, um reagendamento ou uma alteração de banca, verifico se
algum membro (Orientador, 1º Avaliador, 2º Avaliador ou Suplente) tem outra sessão ativa com
sobreposição no intervalo de 1 hora, e bloqueio a gravação se houver.

**Why this priority**: é a validação "hard fail" que protege a agenda de todos os docentes;
precisa existir antes de qualquer gravação de agendamento, reagendamento ou troca de banca (User
Stories 1, 2 e 4).

**Independent Test**: com dois TCCs e uma banca parcialmente sobreposta, tentar agendar a segunda
sessão no mesmo intervalo de um membro já ocupado e verificar a rejeição, sem depender da
interface de nenhuma outra história.

**Acceptance Scenarios**:

1. **Given** nenhum membro da banca proposta tem sessão ativa no intervalo de 1 hora, **When** o
   sistema valida o agendamento, **Then** autoriza a gravação.
2. **Given** um membro tem sessão das 09:00 às 10:00, **When** o sistema agenda outra sessão para
   ele às 10:00, **Then** não há sobreposição e a gravação é autorizada.
3. **Given** a banca não tem suplente, **When** o sistema verifica a agenda, **Then** checa só o
   Orientador, o 1º Avaliador e o 2º Avaliador.
4. **Given** outra defesa no mesmo horário usa o mesmo Local em texto livre, com banca diferente,
   **When** o sistema valida, **Then** não verifica o Local (não há checagem de sala) e autoriza a
   gravação se a banca estiver livre.
5. **Given** a sessão é reagendada, ou a banca é alterada, **When** o sistema revalida conflitos,
   **Then** desconsidera a própria sessão (no reagendamento) ou verifica só os membros novos (na
   alteração de banca).
6. **Given** o Orientador, o 1º Avaliador, o 2º Avaliador ou o Suplente tem outra sessão Agendada,
   Reagendada ou Em Andamento com sobreposição no intervalo de 1 hora (contado, nesse último caso,
   a partir do início real da sessão em andamento), **When** o usuário confirma, **Then** o
   sistema rejeita a gravação, identifica nominalmente cada docente indisponível numa única
   mensagem de alerta (mesmo com vários conflitos simultâneos) e não grava nada.

---

### User Story 4 - Confirmar, notificar, reagendar e cancelar a sessão (Priority: P1)

Como Orientador, Professor da Disciplina ou Secretaria do curso, confirmo o agendamento (o que
notifica a banca e o aluno com o link do Documento para Defesa e cancela um pedido de troca de
orientador pendente), e posso reagendar ou cancelar a sessão com justificativa; o sistema também
atualiza o status automaticamente ao chegar o horário da sessão.

**Why this priority**: é o fechamento do ciclo de agendamento (grava, notifica, mantém a agenda e
o histórico corretos) e a base para a lista de sessões (User Story 5).

**Independent Test**: com o agendamento básico e a banca já validados (Users Stories 1 a 3),
confirmar a sessão e verificar a notificação, o status "Agendada" e, separadamente, reagendar e
cancelar uma sessão existente.

**Acceptance Scenarios**:

1. **Given** a banca está livre de conflitos e o aluno entregou o Documento para Defesa com URL
   cadastrada, **When** o usuário aciona "Agendar", **Then** o sistema grava a sessão como
   "Agendada", notifica o aluno e os membros da banca por e-mail e na central de notificações (com
   data, horário, formato, local ou link, título, nome do aluno e o link do documento) e exibe
   "Defesa agendada com sucesso".
2. **Given** o TCC tem um pedido de troca de orientador sem resposta, **When** o agendamento é
   confirmado, **Then** o sistema cancela automaticamente o pedido e notifica o aluno e o docente
   indicado; sem pedido pendente, nada é cancelado.
3. **Given** a sessão está Agendada, **When** o Orientador, o Professor da Disciplina ou a
   Secretaria aciona "Reagendar", informa nova data, novo horário e Justificativa e confirma,
   **Then** o sistema muda o status para "Reagendada", mantém a banca e as avaliações já salvas, e
   notifica os membros e o aluno com os novos dados.
4. **Given** a sessão está Agendada, Reagendada ou Em Andamento (antes da liberação do resultado),
   **When** o Orientador, o Professor da Disciplina ou a Secretaria aciona "Cancelar sessão",
   informa a Justificativa e confirma, **Then** o sistema muda o status para "Cancelada", descarta
   as avaliações salvas, mantém o Status do TCC "Apto para Defesa" (para permitir nova marcação) e
   notifica a banca e o aluno.
5. **Given** a sessão está Agendada ou Reagendada para um horário determinado, **When** o relógio
   do sistema atinge esse horário, **Then** o status muda automaticamente para "Em Andamento",
   somente leitura, liberando o formulário da Parte Oral aos membros da banca.
6. **Given** um reagendamento tem conflito de horário de algum membro da banca no novo intervalo,
   **When** o usuário confirma, **Then** o sistema rejeita, identifica o docente indisponível e
   mantém no formulário a data, o horário e a Justificativa já digitados.
7. **Given** o usuário confirma o reagendamento ou o cancelamento com a Justificativa vazia ou
   acima de 500 caracteres, **When** confirma, **Then** o sistema não salva e exibe "Informe uma
   justificativa de até 500 caracteres".
8. **Given** a sessão já está "Realizada" ou "Cancelada", **When** o usuário a abre, **Then** os
   botões "Reagendar" e "Cancelar sessão" não aparecem.
9. **Given** quem tenta reagendar ou cancelar não é o Orientador do TCC, o Professor da Disciplina
   da turma, nem a Secretaria do curso, **When** aciona a ação, **Then** o sistema bloqueia e
   exibe "Você não tem permissão para esta ação".
10. **Given** a sessão está "Agendada", "Reagendada" ou "Em Andamento", **When** o Professor da
    Disciplina tenta registrar o encerramento da participação do aluno (Desistente, Reprovado ou
    Jubilado, spec 004/005), **Then** o sistema recusa o encerramento com "Não é possível encerrar
    a participação: há sessão de defesa ativa" (MT30, já existente na spec 004) — quem quiser
    encerrar precisa primeiro cancelar ou reagendar a sessão.

---

### User Story 5 - Ver a lista de sessões, filtrar por período, status e curso, e consultar o histórico (Priority: P2)

Como Aluno, Docente (Orientador, Coorientador ou Avaliador), Professor da Disciplina, Coordenador
de Curso ou Secretaria, consulto a lista de sessões de defesa — restrita ao meu âmbito de
atuação —, filtro por período (com atalhos), status e, para Coordenação e Secretaria, por curso
(US-39), e abro o histórico auditável de cada sessão.

**Why this priority**: depende das sessões já existirem (Users Stories 1 a 4); é consulta, não
bloqueia nenhum fluxo de gravação, mas é essencial para o acompanhamento de todos os perfis.

**Independent Test**: com sessões em diferentes status e perfis distintos de usuário, abrir a
tela Defesas como cada perfil e verificar a visibilidade e os filtros, de forma independente das
outras histórias.

**Acceptance Scenarios**:

1. **Given** o usuário está autenticado, **When** abre o item Defesas, **Then** o sistema exibe as
   sessões do Período Letivo atual, em ordem cronológica, com Data, Horário, Aluno, Título,
   Orientador, Local ou Link e Status.
2. **Given** um Aluno está autenticado, **When** abre Defesas, **Then** vê apenas a própria
   sessão; um Docente Avaliador vê apenas as sessões em que consta nominalmente; o Professor da
   Disciplina vê todas as sessões dos alunos da sua turma; o Coordenador de Curso e a Secretaria
   veem todas as sessões do curso selecionado no filtro (US-39).
3. **Given** o usuário está na lista de defesas, **When** escolhe um atalho de período (Esta
   Semana, Este Mês ou Próximos 30 Dias) ou preenche Data Inicial e Data Final, **Then** o sistema
   mostra só as sessões desse intervalo.
4. **Given** o usuário escolhe um Status na lista (Agendada, Reagendada, Em Andamento, Realizada,
   Cancelada ou Todos), **When** o sistema aplica o filtro, **Then** mostra só as sessões
   correspondentes.
5. **Given** o Coordenador de Curso ou a Secretaria abriu Defesas, **When** troca o filtro de
   Curso (Engenharia de Computação, Sistemas de Informação, Licenciatura em Computação ou Todos),
   **Then** a tabela recarrega com as sessões do curso escolhido, combinando com os demais filtros
   já aplicados (US-39, fluxos A e C).
6. **Given** o usuário clicou na linha de uma defesa e abriu a janela "Sessão de defesa", **When**
   aciona "Histórico", **Then** o sistema abre a janela "Histórico da defesa", somente leitura, com
   a linha do tempo de todos os eventos (agendamento, reagendamento, cancelamento, alteração da
   banca, acionamento de suplente, início automático e liberação do resultado), cada um com data,
   hora, responsável e a justificativa informada.
7. **Given** não há sessões para o período, o status ou o curso filtrados, **When** o sistema
   aplica os filtros, **Then** mantém os cabeçalhos da tabela e exibe "Nenhuma sessão de defesa
   encontrada para o período e filtros selecionados".
8. **Given** a Data Inicial informada é posterior à Data Final, **When** o usuário aplica o
   filtro, **Then** o sistema exibe "A data inicial não pode ser superior à data final" e mantém a
   tabela anterior; com uma data em formato ou valor inválido (ex.: 31/02/2026), exibe "Informe uma
   data válida no formato DD/MM/AAAA".
9. **Given** um docente não faz parte da banca de uma sessão nem é o Professor da Disciplina da
   turma, **When** tenta abrir essa sessão pelo endereço direto, **Then** o sistema exibe "Você
   não tem permissão para visualizar esta defesa".

---

### Edge Cases

- O que acontece se dois usuários tentarem agendar, ao mesmo tempo, a mesma banca para horários
  diferentes mas conflitantes entre si? A validação de conflito (User Story 3) deve travar os
  registros de sessão dos membros envolvidos antes de gravar (ordem a definir no plano), para que
  a segunda requisição veja a sessão já gravada pela primeira e seja rejeitada corretamente, não
  ambas gravadas.
- Um TCC "Apto para Defesa" tem uma sessão já "Agendada", "Reagendada" ou "Em Andamento" quando
  alguém tenta encerrar a participação do aluno? **Resolvido (Clarifications, sessão 2026-10-30;
  decisão final de Julia Cohen)**: `services_turmas.encerrar_participacao` (spec 004, já mesclada)
  **já recusa** o encerramento nesse caso (`STATUS_SESSAO_ATIVA`, mensagem MT30), com teste
  existente (`test_us09_exclusao.py`); esta spec não altera esse comportamento. Quem quiser
  encerrar a participação precisa primeiro cancelar ou reagendar a sessão.
- O que acontece com a banca quando um Membro Externo recém-cadastrado (fluxo B da US-23) nunca
  ativa a conta? A sessão é agendada normalmente (a conta "Aguardando Ativação" não impede a
  indicação na banca); a notificação por e-mail é enviada ao endereço cadastrado, e o acesso real
  às fichas de avaliação depende da ativação, fora do escopo desta spec.
- Uma sessão "Em Andamento" cuja janela de 1 hora termina sem a liberação do resultado (US-27,
  futura feat-08)? Esta spec não tem gatilho de "tempo esgotado": a sessão permanece "Em
  Andamento" até alguém liberar o resultado (`transicionar_status` para "Realizada") ou cancelar.
- O filtro de Curso (US-39) para o Aluno, o Docente comum e o Membro Externo: conforme o E6 da
  US-39, esses perfis não veem o filtro nesta tela, e a visibilidade já é restrita por perfil (User
  Story 5, cenário 2), então o filtro de Curso nunca aparece para eles em Defesas.
- **Histórico pela tela do aluno ou de orientandos** (US-40, fluxo alternativo B; RBN-DEF-01.6):
  a matriz cita o botão "Histórico da defesa" aberto também a partir do painel do aluno (US-41) e
  da tela de orientandos (US-18, spec 006), fora desta spec. Esta spec expõe só o serviço de
  consulta do histórico (`registrar_evento`/consulta associada); a inserção do link nessas duas
  telas é responsabilidade de quem as constrói (Clarifications; ponto a decidir P1 da conferência
  do analista-requisitos, 2026-10-30) — **fora do escopo de teste automatizado desta spec**.
- **Transição para "Realizada"** (US-24, fluxo alternativo E; liberação do resultado, US-27): não
  tem Acceptance Scenario nesta spec porque é disparada pela feat-08 ("Avaliação e Resultados"),
  que chama `transicionar_status` desta spec (Assumptions; ponto a decidir P2 da conferência do
  analista-requisitos, 2026-10-30) — **fora do escopo de teste automatizado desta spec**.

## Requirements *(mandatory)*

### Functional Requirements — Agendar a defesa (US-21)

- **FR-001** [RBN-DEF-01.1]: O sistema MUST exibir, para o Orientador (Engenharia de Computação)
  ou o Professor da Disciplina (Sistemas de Informação e Licenciatura em Computação), o formulário
  "Agendar sessão de defesa" com os campos TCC (lista só com os TCCs "Apto para Defesa", sem sessão
  ativa e sob a responsabilidade do usuário, mostrando título e nome do aluno), Data (não anterior
  a hoje), Horário de Início, Formato da Sessão (Presencial ou Remota), Local (texto livre, até 100
  caracteres, se Presencial) ou Link da Videochamada (`https://`, até 500 caracteres, se Remota), e
  a seção Banca examinadora (US-23).
- **FR-002** [RBN-DEF-01.1]: O sistema MUST indicar a reserva automática de 1 hora de duração a
  partir do Horário de Início informado.
- **FR-003** [RBN-DEF-01.3]: O sistema MUST restringir quem pode agendar conforme o curso do TCC:
  só o Orientador em Engenharia de Computação; só o Professor da Disciplina em Sistemas de
  Informação e Licenciatura em Computação; e MUST restringir a ação a TCCs "Apto para Defesa" sem
  outra sessão "Agendada", "Reagendada" ou "Em Andamento".
- **FR-004** [RBN-DEF-01.1]: O sistema MUST limpar o campo Local ou Link da Videochamada já
  preenchido quando o Formato da Sessão for trocado, exibindo o campo correspondente ao novo
  formato.
- **FR-005** [RBN-DEF-01.1]: O sistema MUST validar, ao confirmar: campos obrigatórios preenchidos,
  Data e Horário de Início posteriores ao momento atual, limite de 100 caracteres do Local, e
  formato (`https://`, até 500 caracteres) do Link da Videochamada; nenhuma dessas validações MUST
  permitir gravar a sessão fora da regra.
- **FR-006** [RBN-DEF-01.1]: O sistema MUST oferecer o agendamento também a partir da aba Defesas de uma turma
  (spec 004) e da tela de orientandos (spec 006), com a lista TCC limitada aos TCCs elegíveis desse
  contexto. Esta spec MUST inserir o botão "Agendar defesa" diretamente nesses dois templates já
  mesclados (Clarifications, sessão 2026-10-30; decisão de Julia Cohen) — não é uma tarefa deixada
  para depois.

### Functional Requirements — Compor e alterar a banca (US-23)

- **FR-007** [RBN-DEF-02.1]: O sistema MUST vincular a banca ao TCC da sessão e exibir o campo
  Orientador (Presidente) preenchido com o orientador atual do TCC, somente leitura, sem opção de
  alteração nem remoção.
- **FR-008** [RBN-DEF-02.1]: O sistema MUST oferecer, para 1º Avaliador, 2º Avaliador e Suplente
  (opcional), listas de Docentes com Status da Conta Ativa e Membros Externos, excluindo sempre o
  orientador e os coorientadores ativos do TCC, e MUST impedir, em cada lista subsequente, a
  seleção de quem já foi escolhido em outro papel.
- **FR-009** [RBN-DEF-02.1]: O sistema MUST validar, ao confirmar a banca: 1º e 2º Avaliadores
  preenchidos, nenhum docente repetido em dois papéis, e nenhum orientador ou coorientador indicado
  como avaliador ou suplente — nesses casos, MUST bloquear a gravação e destacar a mensagem
  específica.
- **FR-010** [RBN-DEF-02.3]: O sistema MUST permitir, a partir do campo de 1º/2º Avaliador ou
  Suplente, o cadastro rápido de um Membro Externo ausente da lista (Nome Completo, E-mail,
  Titulação, Instituição de Origem), gravando a conta "Aguardando Ativação" e deixando-a disponível
  no campo que estava sendo preenchido.
- **FR-011** [RBN-DEF-02.4]: O sistema MUST permitir, com a sessão "Agendada" ou "Reagendada", que
  o Orientador ou o Professor da Disciplina altere o 1º Avaliador, o 2º Avaliador ou o Suplente,
  mediante Justificativa obrigatória (até 500 caracteres); MUST revalidar os conflitos de horário
  só dos membros novos (User Story 3) e MUST descartar as avaliações salvas pelo membro
  substituído, notificando os membros incluídos, os removidos e o Aluno.
- **FR-012** [RBN-DEF-02.1]: O sistema MUST bloquear a substituição do Orientador (Presidente) pela
  alteração simples de banca, exigindo o reagendamento da sessão nesse caso.
- **FR-013** [RBN-DEF-02.2]: O sistema MUST permitir, exclusivamente ao Orientador e só com a
  sessão "Em Andamento", acionar o Suplente no lugar de um titular ausente (campo Avaliador
  Substituído — 1º ou 2º Avaliador — e Justificativa obrigatória até 500 caracteres), promovendo o
  Suplente a titular, descartando as notas do ausente e liberando ao Suplente o formulário completo
  de avaliação; MUST ocultar essa ação quando não houver Suplente na composição ou para quem não
  for o Orientador.

### Functional Requirements — Conflito de horário (US-22)

- **FR-014** [RBN-DEF-03.1]: O sistema MUST calcular a janela de 1 hora de cada sessão a partir do
  Horário de Início (ou do início real, para sessões "Em Andamento") e MUST rejeitar o
  agendamento, o reagendamento ou a alteração de banca se qualquer membro da banca (Orientador, 1º
  Avaliador, 2º Avaliador ou Suplente) tiver outra sessão "Agendada", "Reagendada" ou "Em
  Andamento" com sobreposição nessa janela.
- **FR-015** [RBN-DEF-03.1]: Essa validação MUST desconsiderar a própria sessão no reagendamento, MUST verificar
  só os membros novos na alteração de banca, MUST ignorar o Suplente quando a banca não o tiver, e
  MUST NOT considerar o campo Local (texto livre) como fonte de conflito.
- **FR-016** [RBN-DEF-03.1]: Com um ou mais conflitos, o sistema MUST identificar nominalmente, numa única
  mensagem, todos os membros indisponíveis, e MUST NOT gravar nenhuma sessão, vínculo de banca ou
  alteração enquanto houver conflito.

### Functional Requirements — Confirmação, notificação, reagendamento e cancelamento (US-24)

- **FR-017** [RBN-DEF-01.2]: O sistema MUST manter o status da sessão (`StatusSessao`: Agendada,
  Em Andamento, Realizada, Reagendada, Cancelada) como campo automático, nunca editado diretamente
  por nenhum perfil, atualizado só pelas transições desta spec (Agendada, Reagendada, Em Andamento
  via início automático, Cancelada) ou pela feat-08 (Realizada, via `transicionar_status`).
- **FR-018** [RBN-DEF-03.2]: Ao confirmar o agendamento sem conflitos, o sistema MUST gravar a
  sessão como "Agendada", recuperar a URL da entrega do tipo Documento para Defesa do TCC, MUST
  notificar por e-mail e pela central de notificações o Aluno e todos os membros da banca (com
  data, horário, formato, local ou link, título do trabalho, nome do aluno e o link do documento),
  e MUST cancelar automaticamente um pedido de troca de orientador pendente para o TCC, se houver.
- **FR-019** [RBN-DEF-03.3]: O sistema MUST permitir, com a sessão "Agendada", "Reagendada" ou "Em
  Andamento" (antes da liberação do resultado), que o Orientador, o Professor da Disciplina ou a
  Secretaria do curso reagende a sessão (nova Data, Horário de Início, Formato, Local ou Link e
  Justificativa obrigatória até 500 caracteres), revalidando conflitos (FR-014) e mantendo a banca
  e as avaliações já salvas; o status MUST passar a "Reagendada" e a banca e o Aluno MUST ser
  notificados com os novos dados.
- **FR-020** [RBN-DEF-03.3]: O sistema MUST permitir, nas mesmas condições de status e perfis do
  FR-019, o cancelamento da sessão com Justificativa obrigatória (até 500 caracteres); o status
  MUST passar a "Cancelada", as avaliações salvas MUST ser descartadas, o Status do TCC MUST
  permanecer "Apto para Defesa" (nunca alterado por esta spec), e a banca e o Aluno MUST ser
  notificados.
- **FR-021** [RBN-DEF-01.2]: O sistema MUST mudar automaticamente o status de "Agendada" ou
  "Reagendada" para "Em Andamento" quando o horário previsto da sessão chegar, tornando a sessão
  somente leitura para os dados básicos e liberando o formulário da Parte Oral à banca (serviço
  aplicável tanto numa view quanto num comando de gestão agendado, research a detalhar).
- **FR-022** [RBN-DEF-03.3]: O sistema MUST ocultar os botões "Reagendar" e "Cancelar sessão" quando a sessão
  estiver "Realizada" ou "Cancelada", e MUST bloquear essas ações (mensagem "Você não tem permissão
  para esta ação") para quem não for o Orientador do TCC, o Professor da Disciplina da turma, nem
  a Secretaria do curso.
- **FR-023** [RBN-DEF-01.2]: O sistema MUST expor um serviço único (`transicionar_status`) para qualquer mudança
  de `def_status`, com `registrar_evento` associado (DEF-01.6), de forma que nenhum outro ponto do
  código grave `def_status` ou crie `HistoricoDefesas` diretamente — a feat-08 usa esse serviço
  para a transição "Realizada" (ver "Contratos desta feature"; referência a "FR-012" corrigida na
  conferência do analista-requisitos, 2026-10-30 — P6, erro de cópia sem relação com a transição
  "Realizada").

### Functional Requirements — Lista de sessões, filtros e histórico (US-40, US-39)

- **FR-024** [RBN-DEF-01.4]: O sistema MUST exibir a lista de sessões de defesa, somente leitura,
  em ordem cronológica, com Data, Horário, Aluno, Título do Trabalho, Orientador, Local ou Link e
  Status, restrita à visibilidade de cada perfil: Aluno, Orientador, Coorientador (com convite
  aceito) e Avaliador veem só as sessões em que constam nominalmente; o Professor da Disciplina vê
  as sessões dos alunos da própria turma; o Coordenador de Curso e a Secretaria veem as sessões do
  curso selecionado no filtro (US-39).
- **FR-025** [RBN-DEF-01.5]: O sistema MUST oferecer o filtro de período com Data Inicial e Data
  Final (calendário, DD/MM/AAAA) e os atalhos Período Letivo (padrão), Esta Semana, Este Mês e
  Próximos 30 Dias, e MUST validar que a Data Inicial não seja posterior à Data Final e que as
  datas sejam válidas no formato esperado.
- **FR-026** [RBN-DEF-01.4]: O sistema MUST oferecer o filtro de Status (Agendada, Reagendada, Em Andamento,
  Realizada, Cancelada ou Todos), combinável com o filtro de período.
- **FR-027** [RBN-CAD-14.1]: Para o Coordenador de Curso e a Secretaria, o sistema MUST aplicar o
  filtro de Curso já existente (`services_contas.filtro_de_curso`) à lista de Defesas, preenchido
  por padrão com o curso do usuário, combinável com os demais filtros da tela, e MUST atualizar a
  tabela em até 2 segundos ao trocar o curso (US-39, RBN-CAD-14.1; completude da conferência do
  analista-requisitos, 2026-10-30 — detalhe presente na matriz, sem ambiguidade, não constava
  antes nesta spec); Aluno, Docente comum e Membro Externo MUST NOT ver esse filtro.
- **FR-028** [RBN-DEF-01.4]: Sem nenhuma sessão para os filtros escolhidos, o sistema MUST manter os cabeçalhos da
  tabela e exibir "Nenhuma sessão de defesa encontrada para o período e filtros selecionados".
- **FR-029** [RBN-DEF-01.6]: O sistema MUST exibir, para cada sessão, a janela "Histórico da
  defesa" (somente leitura), com a linha do tempo de todos os eventos (agendamento, reagendamento,
  cancelamento, alteração da banca, acionamento de suplente, início automático, liberação do
  resultado), cada um com data, hora, responsável e a justificativa informada quando houver.
- **FR-030** [RBN-DEF-01.4]: O sistema MUST bloquear o acesso direto a uma sessão por quem não faz parte da banca
  nem é o Professor da Disciplina da turma, exibindo "Você não tem permissão para visualizar esta
  defesa".

### Key Entities *(reaproveitadas da spec 001/Épico 2; nenhuma nova sem confirmação)*

- **Defesas**: a sessão de defesa (TCC, data, horário de início, formato, status, parecer, nota
  final — campos usados por features futuras; esta spec usa `def_tcc`, `def_data`, `def_h_inicio`,
  `def_formato`, `def_status`).
- **DefesasPresenciais** / **DefesasRemotas**: Local em texto livre (até 100 caracteres) ou Link da
  Videochamada (até 500 caracteres, `https://`), um para um com `Defesas`.
- **BancaDefesa**: um membro por linha (PK composta sessão + usuário), com o papel (`PapelBanca`) e
  os campos de substituição (usado no acionamento do suplente e na alteração de banca).
- **HistoricoDefesas**: um evento por linha (`EventoDefesa`), com status anterior/novo, datas e
  horários anterior/novo (reagendamento), membro removido/incluído (alteração de banca e
  suplente), justificativa, data/hora e responsável.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um Orientador ou Professor da Disciplina consegue agendar uma defesa completa (dados
  básicos + banca) em menos de 5 minutos, a partir da tela Defesas.
- **SC-002**: 100% das tentativas de agendamento, reagendamento ou alteração de banca com conflito
  de horário de algum membro são rejeitadas nos testes automatizados, sem gravar nenhum dado.
- **SC-003**: 100% das mudanças de status da sessão (`def_status`) nos testes automatizados
  ocorrem só pelo serviço único de transição, nunca por atribuição direta do campo.
- **SC-004**: Cada perfil (Aluno, Docente avaliador, Professor da Disciplina, Coordenador de
  Curso, Secretaria) vê, nos testes automatizados, exatamente as sessões previstas para o seu
  âmbito de atuação — nenhuma sessão fora do escopo do perfil aparece na lista nem é acessível por
  endereço direto.
- **SC-005**: Todos os cenários de aceite desta spec (as Acceptance Scenarios das 5 User Stories,
  cobrindo os cenários das US-21, 22, 23, 24 e 40, mais a aplicação do filtro de Curso da US-39 à
  tela Defesas) têm pelo menos um teste automatizado correspondente, **exceto** os dois cenários
  explicitamente fora do escopo de teste desta spec (Edge Cases): o histórico aberto pela tela do
  aluno/orientandos (US-40, fluxo B) e a transição para "Realizada" (US-24, fluxo E) — ajuste da
  conferência do analista-requisitos (2026-10-30; pontos a decidir P1 e P2).
- **SC-006**: 100% das mensagens exibidas ao usuário por esta feature são idênticas, caractere por
  caractere, ao texto entre aspas das US-21, 22, 23, 24, 39 e 40, ou estão marcadas como
  provisórias em `docs/questoes-a-rever.md`.

## Assumptions

- O Local da defesa presencial é texto livre de até 100 caracteres, sem tabela de Salas (CR-2026-
  0001), conforme já refletido no dicionário de dados e na matriz de 17/10 (RBN-DEF-03.1, "sai a
  verificação de conflito de sala").
- O conflito de horário (User Story 3) verifica só os membros da banca, nunca o Local.
- A transição de status "Realizada" (liberação do resultado, US-27) é disparada por uma feature
  futura ("Avaliação e Resultados", feat-08, Célio Benjamim), que consome o serviço
  `transicionar_status` desta spec; esta spec não implementa a liberação do resultado nem grava
  `def_parecer` ou `def_nota_final`.
- `services_avaliacoes.descartar_avaliacoes(sessao, membro=None)` ainda não existe (feat-08); esta
  spec usa um stub com a mesma assinatura (Clarifications), substituído sem mudar o ponto de
  chamada quando a função real for entregue.
- O início automático das sessões (Agendada/Reagendada → Em Andamento) é implementado como um
  serviço aplicável tanto numa view (ao abrir a tela) quanto num comando de gestão agendado (PGCS
  9.4); o agendamento desse comando no GitHub Actions é item de configuração do Célio Benjamim
  (índice Q-79), fora do escopo de código desta spec.
- O mecanismo geral do filtro de Curso (US-39) já existe (`services_contas.filtro_de_curso`,
  feat-04); esta spec só o aplica à tela Defesas, sem reimplementá-lo nem alterar seu
  comportamento para as demais telas que já o usam.
- Esta spec toca código já mesclado de outra feature num ponto (Clarifications, sessão
  2026-10-30; decisão de Julia Cohen): insere o botão "Agendar defesa" na aba Defesas da turma
  (spec 004) e na tela de orientandos (spec 006, FR-006). Essa integração está registrada como
  pendência de aprovação em `docs/questoes-a-rever.md` (Q-123), no mesmo padrão já usado na spec
  005 (Q-46).
- `services_turmas.encerrar_participacao` (spec 004, já mesclada) continua recusando o
  encerramento da participação quando há sessão de defesa ativa (MT30); esta spec **não** altera
  esse arquivo nem essa regra (Clarifications, sessão 2026-10-30 — decisão revertida depois de
  encontrar o comportamento já existente).
