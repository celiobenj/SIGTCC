---

description: "Task list para a feature 007 — Agendamento e Banca do SIGTCC"
---

# Tasks: Agendamento e Banca do SIGTCC

**Status**: Approved (Julia Cohen, 2026-10-30) — depois do `/speckit-analyze` (achados D1 e C1
corrigidos: tags RBN completadas no spec.md; `_verificar_conflito` movida para a Fase 2, eliminando
a dependência cruzada entre User Stories).

**Divisão da Fase 2 (decisão de Julia Cohen, 2026-10-30, no início do `/speckit-implement`)**: a
fase base pedida para 03/11 é a **Fase 2a** (elegibilidade e permissão de agendamento,
`membros_efetivos`, status da sessão, `registrar_evento`, stub de `descartar_avaliacoes` e
`popular_demo` com uma sessão em cada status, mais `agendar_sessao` e seus 2 auxiliares, de que o
`popular_demo` precisa). O restante do `services_defesa.py` vira a **Fase 2b**, na próxima rodada.
`pode_agendar` (antes T024, US1) passou para a Fase 2a, e entrou a T058 (`tccs_elegiveis`, serviço
novo, tirando a regra de elegibilidade de dentro do `AgendarForm`). Os IDs foram mantidos.

**Input**: Design documents from `/specs/007-agendamento-banca/`
**Prerequisites**: [plan.md](plan.md) (Approved, Julia Cohen, 2026-10-30), [spec.md](spec.md),
[research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/),
[quickstart.md](quickstart.md)

**Tests**: cada cenário de aceite das 5 User Stories vira pelo menos um teste Django (constituição,
princípio VI); testes incluídos nas tarefas de cada fase.

**Organization**: tarefas agrupadas por User Story. A Fase 2 (Foundational) contém o serviço base
`services_defesa.py` inteiro, incluindo a validação de conflito de horário (US-22/US3); a parte de
que a feat-08 (Célio Benjamim) depende para começar em **03/11** é a Fase 2a. Um único módulo de
serviço (não dividido por User Story) porque todas as regras giram em torno de uma única entidade
central (`Defesas`) — decisão já justificada no Complexity Tracking do plan.md.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: US1 a US5, conforme spec.md
- Caminhos de arquivo exatos em cada descrição

---

## Phase 1: Setup

**Purpose**: estrutura inicial do app `defesa` para esta feature

- [ ] T001 Criar os arquivos (com o cabeçalho `[US-XX][RBN-...]` a preencher por tarefa)
  `sigtcc/apps/defesa/services_defesa.py` e `permissoes_defesa.py` na Fase 2a;
  `forms_defesa.py`, `views_defesa.py`, `urls.py` (`app_name = "defesa"`) e `mensagens.py` quando
  a primeira User Story precisar deles — `models.py`, `choices.py` e `cargas.py` já existem (spec
  001)
- [ ] T002 [P] IC-01 (índice Q-123): `+ path("", include("sigtcc.apps.defesa.urls"))` em
  `sigtcc/urls.py`, sem remover nada existente (junto com a primeira view, Fase 3)
- [ ] T003 [P] Criar `sigtcc/apps/defesa/tests/apoio_defesa.py` com fábricas que partem de
  `tests/apoio_turmas.py`/`apoio_orientacao.py` (TCC "Apto para Defesa" com Orientador vinculado)
  e `agendar_sessao_de(tcc, **dados)`, `avancar_para(sessao, status)` (research C8)

**Checkpoint**: estrutura do app pronta para a Fase 2.

---

## Phase 2a: Foundational — fase base, **prazo crítico 03/11**

**Purpose**: o que a feat-08 (Célio Benjamim) consome para começar: elegibilidade e permissão de
agendamento, criação da sessão, status da sessão, histórico, `membros_efetivos`, stub de descarte
e `popular_demo`

**⚠️ CRITICAL**: MUST estar pronta até **03/11**.

- [ ] T004 [P] Definir, em `sigtcc/apps/defesa/services_defesa.py`, `EVENTO_DA_TRANSICAO` (dict
  `novo_status → EventoDefesa`) e `TRANSICOES_VALIDAS` (set de pares `(status_atual, novo_status)`
  permitidos para sessão já existente — sem entrada para criação) — research C2
- [ ] T005 Implementar `registrar_evento(sessao, tipo, justificativa, autor, **dados) ->
  HistoricoDefesas` em `services_defesa.py` — grava uma linha de `HistoricoDefesas`
  (`hdf_status_anterior`/`hdf_status_novo`, `hdf_data_anterior`/`hdf_hora_anterior`/
  `hdf_data_nova`/`hdf_hora_nova`, `hdf_membro_removido`/`hdf_membro_incluido`,
  `hdf_justificativa`, `hdf_data_hora`, `hdf_usu` aceitando `autor=None`) — contrato §2, FR-023,
  FR-029, RBN-DEF-01.6, RBN-DEF-02.2 (depende de T004)
- [ ] T006 Implementar `transicionar_status(sessao, novo_status, autor, justificativa=None,
  **dados_evento) -> Defesas` em `services_defesa.py` — valida `(status_atual, novo_status)`
  contra `TRANSICOES_VALIDAS`, levanta `ValueError` sem gravar nada se inválida, grava
  `def_status` (`update_fields=["def_status"]`) e chama `registrar_evento` — FR-017, FR-023,
  contrato §1 (depende de T004, T005)
- [ ] T009 [P] Implementar `_gravar_local_ou_link(sessao, local, link)` em `services_defesa.py` —
  grava `DefesasPresenciais` (`dep_local`, até 100 caracteres) ou `DefesasRemotas` (`der_link`,
  `https://`, até 500 caracteres) conforme `def_formato`; se a sessão já tiver a linha do outro
  formato, remove-a — FR-001, FR-004, FR-005, data-model.md
- [ ] T010 Implementar `_compor_banca(sessao, dados_banca)` em `services_defesa.py` — grava uma
  linha de `BancaDefesa` por membro (Orientador de `services_orientacao.orientador_atual(tcc)`,
  só leitura; 1º/2º Avaliador; Suplente opcional) — FR-007, RBN-DEF-02.1, research C4
- [ ] T011 Implementar `agendar_sessao(tcc, dados_basicos, dados_banca, autor) -> Defesas` em
  `services_defesa.py` — único ponto que cria `Defesas` (`def_status=AGENDADA`), chama
  `_gravar_local_ou_link`, `_compor_banca` e `registrar_evento(..., EventoDefesa.AGENDAMENTO,
  ...)` diretamente; pressupõe TCC travado e conflito já verificado pelo chamador (T007/T008) —
  FR-001 a FR-020, FR-023, research C2 (depende de T005, T009, T010)
- [ ] T012 Implementar `membros_efetivos(sessao) -> list[Usuarios]` em `services_defesa.py` — os
  3 membros que de fato atuam (Orientador, 1º e 2º Avaliador), considerando o suplente acionado
  (que passa a ocupar o papel do titular ausente); o Suplente **não** acionado não entra —
  contrato §2
- [ ] T013 [P] Implementar o stub `descartar_avaliacoes(sessao, membro=None)` em
  `services_defesa.py` — só registra em log que o descarte foi solicitado (sem tocar em
  `Avaliacoes`, tabela que esta spec não possui); assinatura exata da feat-08 — contrato §6,
  Clarifications
- [ ] T024 [P] Implementar `pode_agendar(usuario, tcc)` em `sigtcc/apps/defesa/permissoes_defesa.py`
  — `services_orientacao.e_orientador_atual` em Engenharia de Computação; Professor da Disciplina
  da turma nas demais — FR-003, RBN-DEF-01.3, research C1a (movida da US1 para a Fase 2a)
- [ ] T058 Implementar `tcc_elegivel(tcc)` e `tccs_elegiveis(usuario)` em `services_defesa.py` —
  TCCs "Apto para Defesa", sem sessão "Agendada", "Reagendada" ou "Em Andamento"
  (`services_turmas.STATUS_SESSAO_ATIVA`), em turma ativa (RBN-CAD-04.5) e sob a responsabilidade
  do usuário pela regra de `pode_agendar` (mesmo critério, em consulta única), com título e nome do
  aluno — FR-001, FR-003, RBN-DEF-01.1, RBN-DEF-01.3 (depende de T024)
- [ ] T022 IC-05: acrescentar, em `sigtcc/apps/cadastro/management/commands/popular_demo.py`, um
  TCC "Apto para Defesa" em cada curso e uma sessão em cada um dos 5 valores de `StatusSessao`,
  criadas só por `services_defesa` (`agendar_sessao` e `transicionar_status`; nunca
  `Defesas.objects.create()` direto); a sessão "Realizada" fica num TCC que depois recebe o
  resultado — contrato §5 (depende de T006, T011)
- [ ] T023 [P] `sigtcc/apps/defesa/tests/test_base_defesa.py`: `transicionar_status` (transições
  válidas e inválidas, nenhuma linha gravada quando inválida), `registrar_evento` (inclusive
  `autor=None`), `agendar_sessao`, `membros_efetivos`, `descartar_avaliacoes` (stub),
  `pode_agendar`, `tccs_elegiveis`, `popular_demo` (smoke test: uma sessão em cada status) —
  SC-003 (depende de T004 a T013, T024, T058, T022)

**Checkpoint**: fase base (2a) concluída — Célio Benjamim (feat-08) já pode depender de
`agendar_sessao`, `transicionar_status`, `registrar_evento`, `membros_efetivos`,
`TRANSICOES_VALIDAS`, `descartar_avaliacoes` (stub) e `popular_demo` (prazo 03/11).

---

## Phase 2b: Foundational — restante do `services_defesa.py` (próxima rodada)

**Purpose**: travas, conflito de horário, alteração de banca, suplente, confirmação, reagendamento,
cancelamento, início automático, lista e histórico. **Bloqueia as Fases 3 a 7.**

- [ ] T007 [P] Implementar `_travar_membros(ids_usuarios)` em `services_defesa.py` —
  `Usuarios.objects.filter(pk__in=sorted(ids_usuarios)).select_for_update().order_by("pk")` —
  research C3, achado B2/B3 da revisão do `arquiteto-django`
- [ ] T008 Implementar `_verificar_conflito(ids_usuarios, data, h_inicio, excluir_sessao=None)` em
  `services_defesa.py` — janela de 1h (ou início real, para sessões Em Andamento); desconsidera a
  própria sessão no reagendamento; levanta exceção com os nomes de todos os membros
  indisponíveis numa única mensagem, sem gravar nada — FR-014, FR-015, FR-016, research C3
  (depende de T007; chamada sempre depois de `_travar_membros`, antes de `agendar_sessao`/
  `reagendar`/`alterar_banca` — achado C1 do `/speckit-analyze`)
- [ ] T014 Implementar `alterar_banca(sessao, papel, novo_membro, justificativa, autor) -> Defesas`
  em `services_defesa.py` — depois de `_travar_membros([novo_membro.pk])` (T007) e de
  `_verificar_conflito` (T008) só do novo membro, substitui a linha do papel indicado
  (`delete()` + `create()`), chama o stub `descartar_avaliacoes(sessao, membro=antigo)` e
  `registrar_evento(..., EventoDefesa.ALTERACAO_DA_BANCA, ..., membro_removido=antigo,
  membro_incluido=novo_membro)` diretamente (não muda `def_status`) — FR-011, FR-012, research C4
  (depende de T005, T007, T008, T010, T013)
- [ ] T015 Implementar `acionar_suplente(sessao, papel_substituido, autor, justificativa) ->
  Defesas` em `services_defesa.py` — sem `_travar_membros`/`_verificar_conflito` (suplente já
  passou pela checagem quando entrou na banca original); promove o suplente ao papel do titular
  ausente, grava `ban_usu_substituido`/`ban_justificativa_substituicao`, remove a linha antiga,
  chama o stub de descarte para o ausente e `registrar_evento(...,
  EventoDefesa.ACIONAMENTO_DO_SUPLENTE, ...)` diretamente — FR-013, research C4 (depende de T005,
  T013)
- [ ] T016 Implementar `confirmar_agendamento(sessao, autor)` em `services_defesa.py` — na mesma
  transação de `agendar_sessao`: recupera o link via
  `services_entregas.link_mais_recente(entrega_documento_defesa)`, notifica
  (`services.notificar`/`enviar_email_apos_commit`) o Aluno e **todos** os membros de
  `BancaDefesa`, inclusive o Suplente não acionado (FR-018, RBN-DEF-03.2 — não
  `membros_efetivos`), e chama `services_orientacao.cancelar_troca_no_agendamento(tcc, agora)`
  com o mesmo `agora` do evento 'Agendamento' — FR-018, research C5 (depende de T011)
- [ ] T017 Implementar `reagendar(sessao, dados, justificativa, autor) -> Defesas` em
  `services_defesa.py` — depois de `_travar_membros` (T007) e `_verificar_conflito` (T008) com os
  pks de **todos** os membros de `BancaDefesa`, inclusive o Suplente (FR-014), chama
  `transicionar_status(..., StatusSessao.REAGENDADA, ...)` e notifica a banca inteira e o Aluno
  com os novos dados, sem tocar banca/avaliações — FR-019, research C5 (depende de T006, T007,
  T008)
- [ ] T018 Implementar `cancelar(sessao, justificativa, autor) -> Defesas` em `services_defesa.py`
  — chama `transicionar_status(..., StatusSessao.CANCELADA, ...)`, o stub
  `descartar_avaliacoes(sessao)` (todos os membros) e notifica a banca e o Aluno; nunca grava
  `tcc_status` — FR-020, research C5 (depende de T006, T013)
- [ ] T019 [P] Implementar `sessoes_para_iniciar(agora)` em `services_defesa.py` — função pura
  (mesmo padrão de `services_entregas.entregas_para_lembrar`), devolve sessões
  "Agendada"/"Reagendada" cujo `def_data`+`def_h_inicio` já passou — FR-021, research C6
- [ ] T020 Implementar `listar_defesas(usuario, filtros) -> queryset` em `services_defesa.py` —
  `select_related`, visibilidade por perfil somada por `Q()` com OR (nunca if/elif), filtros de
  período (FR-025), status (FR-026) e curso (FR-027, `services_contas.filtro_de_curso`) somados
  por `&`, com `.distinct()` — FR-024 a FR-028, RBN-CAD-14.1, research C6 (depende de T012)
- [ ] T021 [P] Implementar `historico_da_sessao(sessao) -> queryset` em `services_defesa.py` —
  todas as linhas de `HistoricoDefesas` da sessão, ordenadas por `hdf_data_hora`, sem checagem de
  perfil — FR-029, research C7
- [ ] T059 [P] Acrescentar em `sigtcc/apps/defesa/tests/test_base_defesa.py` os testes da Fase 2b:
  `_travar_membros` (duas transações disputando o mesmo docente), `_verificar_conflito`
  (sobreposição, exclusão da própria sessão, ignora Local), `alterar_banca`, `acionar_suplente`,
  `confirmar_agendamento`, `reagendar`, `cancelar`, `sessoes_para_iniciar`, `listar_defesas`,
  `historico_da_sessao` — SC-002 (depende de T007, T008, T014 a T021)

**Checkpoint**: `services_defesa.py` completo. As Fases 3 a 7 seguem com formulários, views,
templates e mensagens — todas podem usar `_travar_membros`/`_verificar_conflito` desde já.

---

## Phase 3: User Story 1 - Agendar a defesa com data, horário, formato e local ou link (Priority: P1) 🎯 MVP

**Goal**: formulário "Agendar sessão de defesa" com os dados básicos, a validação de conflito já
ativa (Fase 2b) e os dois pontos de entrada já mesclados (aba Defesas da turma, tela de
orientandos)

**Independent Test**: criar um TCC "Apto para Defesa" sem sessão ativa, abrir o formulário, validar
os campos básicos isoladamente (sem depender da seção Banca completa, User Story 2)

- T024 — movida para a Fase 2a (`pode_agendar`).
- [ ] T025 [P] [US1] Implementar `AgendarForm` em `sigtcc/apps/defesa/forms_defesa.py` — TCC (lista
  de `services_defesa.tccs_elegiveis(usuario)`, T058), Data (não anterior a hoje), Horário de
  Início, Formato, Local (até 100 caracteres) ou Link (`https://`, até 500 caracteres), limpando o
  campo oposto ao trocar o formato — FR-001, FR-002, FR-004, FR-005
- [ ] T026 [US1] Implementar a view `agendar` em `sigtcc/apps/defesa/views_defesa.py` — GET lista
  TCCs elegíveis (`?tcc=` pré-seleciona), POST trava turma/aluno/TCC, chama `_travar_membros` +
  `_verificar_conflito` (Fase 2b) e, sem conflito, `agendar_sessao` e `confirmar_agendamento`,
  exibindo "Defesa agendada com sucesso" — FR-001, FR-003, FR-014 a FR-016, contracts/rotas.md
  (depende de T024, T025, T008, T011, T016)
- [ ] T027 [P] [US1] Criar `sigtcc/templates/defesa/form_agendar.html` (protótipo de 17/10: layout,
  paleta, Roboto/Figtree, Material Symbols; nota de 15/20 minutos de apresentação, US-21 passo 4)
- [ ] T028 [P] [US1] IC-02 (índice Q-123): item "Defesas" em `sigtcc/apps/cadastro/menu.py` (ícone
  do protótipo, rota `defesa:defesas`, perfis aluno/docente/secretaria, logo depois de
  "Orientações")
- [ ] T029 [P] [US1] IC-03 (índice Q-123): aba "Defesas" em
  `sigtcc/apps/cadastro/templates/cadastro/tcc/_abas_professor.html` (visível quando
  `e_professor`, rota `defesa:turma_defesas`); implementar a view `turma_defesas` em
  `views_defesa.py` e o template `sigtcc/templates/defesa/turma_defesas.html` — FR-006 (depende de
  T020)
- [ ] T030 [P] [US1] IC-04 (índice Q-123): link "Agendar defesa" em
  `sigtcc/apps/cadastro/templates/cadastro/orientacao/orientacoes.html`, por orientando com TCC
  elegível (`services_defesa.tcc_elegivel`, T058; `defesa:agendar?tcc=<id>`) — FR-006
- [ ] T031 [P] [US1] Acrescentar em `sigtcc/apps/defesa/mensagens.py` os textos exatos da US-21
  (ou provisórios `MD-XX`, registrados em `docs/questoes-a-rever.md`) — research C8
- [ ] T032 [US1] `sigtcc/apps/defesa/tests/test_us21_agendar.py` — os 8 cenários de aceite da User
  Story 1 (depende de T026)

**Checkpoint**: User Story 1 funcional e testável (agendamento com conflito já bloqueado; falta a
seção Banca completa — ver Fase 4).

---

## Phase 4: User Story 2 - Compor e alterar a banca examinadora (Priority: P1)

**Goal**: seção Banca examinadora no agendamento, alteração de banca e acionamento de suplente

**Independent Test**: com um TCC com Orientador vinculado, compor 2 ou 3 avaliadores na seção
Banca, sem depender da confirmação final da sessão

- [ ] T033 [P] [US2] Implementar `pode_alterar_banca(usuario, sessao)` e
  `pode_acionar_suplente(usuario, sessao)` em `permissoes_defesa.py` — Orientador/Professor da
  Disciplina com sessão Agendada/Reagendada; exclusivamente Orientador com sessão Em Andamento e
  suplente presente — FR-011, FR-013
- [ ] T034 [P] [US2] Implementar, em `forms_defesa.py`: a seção Banca do `AgendarForm` (exclui
  orientador/coorientadores, listas excludentes entre papéis, cadastro rápido de Membro Externo
  reaproveitando o formulário da US-05), `AlterarBancaForm` e `AcionarSuplenteForm` (Justificativa
  obrigatória até 500 caracteres) — FR-008, FR-009, FR-010, FR-012, FR-013
- [ ] T035 [US2] Implementar as views `alterar_banca` e `acionar_suplente` em `views_defesa.py` —
  chamam `alterar_banca`/`acionar_suplente` de `services_defesa.py` (depende de T033, T034, T014,
  T015)
- [ ] T036 [P] [US2] Criar `sigtcc/templates/defesa/form_alterar_banca.html` e
  `form_acionar_suplente.html` (protótipo de 17/10)
- [ ] T037 [P] [US2] Acrescentar em `mensagens.py` os textos exatos da US-23 (ou provisórios
  `MD-XX`)
- [ ] T038 [US2] `sigtcc/apps/defesa/tests/test_us23_banca.py` — os 11 cenários de aceite da User
  Story 2 (depende de T035)

**Checkpoint**: Users Stories 1 e 2 funcionais (agendamento completo com banca e conflito
bloqueando a gravação).

---

## Phase 5: User Story 3 - Impedir agendamentos com conflito de horário da banca (Priority: P1)

**Goal**: confirmar, com testes dedicados, que o bloqueio de conflito (já implementado e integrado
nas Fases 2b a 4) cobre todos os cenários de aceite da User Story 3 — inclusive a corrida de duas
sessões novas simultâneas

**Independent Test**: com dois TCCs e banca parcialmente sobreposta, tentar agendar a segunda
sessão no intervalo de um membro já ocupado e verificar a rejeição, sem gravar nada

- [ ] T039 [US3] `sigtcc/apps/defesa/tests/test_us22_conflito.py` — os 6 cenários de aceite da
  User Story 3 contra `_verificar_conflito`/`_travar_membros` (T007/T008, Fase 2b) já integrados
  nas views `agendar` (T026), `alterar_banca` (T035) e `reagendar` (T042) — incluindo a corrida de
  duas sessões novas simultâneas para o mesmo docente (research C3) — FR-014 a FR-016 (depende de
  T026, T035, T042)

**Checkpoint**: User Story 3 coberta por teste próprio, sem nenhuma implementação pendente (toda a
lógica já está na Fase 2b).

---

## Phase 6: User Story 4 - Confirmar, notificar, reagendar e cancelar a sessão (Priority: P1)

**Goal**: reagendamento, cancelamento e início automático da sessão, com notificações

**Independent Test**: com o agendamento básico e a banca já validados, confirmar a sessão e
verificar a notificação e o status "Agendada"; separadamente, reagendar e cancelar uma sessão
existente

- [ ] T040 [P] [US4] Implementar `pode_reagendar_ou_cancelar(usuario, sessao)` em
  `permissoes_defesa.py` — Orientador, Professor da Disciplina ou Secretaria do curso, com sessão
  Agendada/Reagendada/Em Andamento — FR-022
- [ ] T041 [P] [US4] Implementar `ReagendarForm` e `CancelarForm` em `forms_defesa.py`
  (Justificativa obrigatória até 500 caracteres) — FR-019, FR-020
- [ ] T042 [US4] Implementar as views `reagendar` e `cancelar` em `views_defesa.py` — chamam
  `reagendar`/`cancelar` de `services_defesa.py` (que já usa `_travar_membros`/
  `_verificar_conflito`, Fase 2b), ocultam os botões quando Realizada/Cancelada — FR-019, FR-020,
  FR-022 (depende de T040, T041, T017, T018)
- [ ] T043 [P] [US4] Criar `sigtcc/templates/defesa/form_reagendar.html` e
  `confirmar_cancelar.html` (protótipo de 17/10)
- [ ] T044 [P] [US4] Acrescentar em `mensagens.py` os textos exatos da US-24 (ou provisórios
  `MD-XX`)
- [ ] T045 [US4] `sigtcc/apps/defesa/tests/test_us24_confirmar_reagendar_cancelar.py` — os 10
  cenários de aceite da User Story 4, incluindo o cenário 10 (MT30, `services_turmas.py` **não**
  alterado) com relógio controlado para o início automático (depende de T042)
- [ ] T046 [US4] Aplicar `sessoes_para_iniciar(agora)` na view `defesas`/`sessao` (chama
  `transicionar_status` para as sessões encontradas antes de renderizar) e no comando de gestão
  agendado (PGCS 9.4, Assumptions; agendamento no GitHub Actions é item do Célio, Q-79) — FR-021
  (depende de T019, T006)

**Checkpoint**: ciclo completo de agendamento, confirmação, reagendamento, cancelamento e início
automático funcional; User Story 3 (T039) pode ser concluída depois de T042.

---

## Phase 7: User Story 5 - Ver a lista de sessões, filtrar por período, status e curso, e consultar o histórico (Priority: P2)

**Goal**: tela "Defesas" com filtros e janela "Histórico da defesa", restrita por perfil

**Independent Test**: com sessões em status e perfis distintos, abrir a tela Defesas como cada
perfil e verificar visibilidade e filtros

- [ ] T047 [P] [US5] Implementar `pode_ver_sessao(usuario, sessao)` em `permissoes_defesa.py` —
  membro da banca ou Professor da Disciplina da turma; Aluno, Coordenador e Secretaria **não**
  acessam `sessao`/`historico` direto (decisão explícita, contracts/rotas.md) — FR-030
- [ ] T048 [US5] Implementar a view `defesas` em `views_defesa.py` — lista + filtros de período
  (atalhos e intervalo manual), status e, para Coordenador/Secretaria, curso (`?curso=`,
  `services_contas.filtro_de_curso`), atualizando em até 2 segundos — FR-024 a FR-028, RBN-CAD-14.1
  (depende de T020, T047)
- [ ] T049 [US5] Implementar as views `sessao` e `historico` em `views_defesa.py` — 404 → 403
  (M-02) → conteúdo, nessa ordem — FR-029, FR-030 (depende de T047, T021)
- [ ] T050 [P] [US5] Criar `sigtcc/templates/defesa/defesas.html`, `sessao.html` (com os blocos
  reservados `{% block avaliacao %}`, `resultado`, `documentos`, `ouvintes`, `ocorrencias` do
  contrato §4 da feat-08/feat-09) e `historico.html` (protótipo de 17/10)
- [ ] T051 [P] [US5] Criar o componente do filtro de período (`sigtcc/templates/defesa/` + função
  auxiliar em `services_defesa.py`, `componente_filtro_periodo`) reaproveitável pela feat-08/feat-09
  — contrato §4, RBN-DEF-01.5
- [ ] T052 [P] [US5] Acrescentar em `mensagens.py` os textos exatos da US-40 e da aplicação do
  filtro de Curso (US-39) à tela Defesas
- [ ] T053 [US5] `sigtcc/apps/defesa/tests/test_us40_lista_filtros_historico.py` — os 9 cenários de
  aceite da User Story 5 (depende de T048, T049)

**Checkpoint**: todas as 5 User Stories funcionais de forma independente.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: cobertura cruzada e validação final

- [ ] T054 [P] `sigtcc/apps/defesa/tests/test_permissoes_defesa.py` — cobertura cruzada de todos os
  `pode_*` (por curso e por perfil), incluindo acesso por endereço direto (SC-004)
- [ ] T055 [P] `sigtcc/apps/defesa/tests/test_mensagens_defesa.py` — confere, caractere por
  caractere, os textos entre aspas das US-21, 22, 23, 24, 39 e 40 (SC-006)
- [ ] T056 Rodar o roteiro de [quickstart.md](quickstart.md) manualmente e registrar o resultado
- [ ] T057 `pre-commit run --all-files` (`isort`, `black -l 100`, `flake8 --max-line-length 100`)
  em todos os arquivos novos/alterados desta feature

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Fase 1)**: sem dependências
- **Fase 2a**: depende da Fase 1 — prazo crítico **03/11** (feat-08 depende dela)
- **Fase 2b**: depende da Fase 2a — **BLOQUEIA todas as User Stories**; inclui
  `_verificar_conflito` (US-22), para que nenhuma User Story dependa de outra para ter o bloqueio
  de conflito ativo (achado C1 do `/speckit-analyze`, corrigido)
- **User Stories (Fases 3 a 7)**: todas dependem só da Fase 2 (2a e 2b). Entre si, seguem a ordem
  de prioridade da spec (US1, US2, US3, US4 — todas P1 — depois US5, P2); a única dependência
  entre fases de User Story que permanece é a do teste da US3 (T039) sobre as views de US1/US2/US4
  (T026, T035, T042), porque o teste de aceite da User Story 3 exercita essas views — a
  **implementação** da US3 não depende de nenhuma outra fase
- **Polish (Fase 8)**: depende de todas as User Stories desejadas estarem completas

### Parallel Opportunities

- Fase 2a: T004, T009, T013, T024 em paralelo; depois T005→T006, T009/T010→T011, T024→T058;
  T022 e T023 por último
- Fase 2b: T007, T019, T021 em paralelo; depois T007→T008→T014/T017, T013→T015/T018
- Dentro de cada User Story: tarefas `[P]` (permissões, forms, templates, mensagens) em paralelo;
  a view e o teste de cada fase vêm depois

## Implementation Strategy

### MVP First

1. Fase 1 (Setup) + Fase 2a (prazo 03/11) + Fase 2b (já com o bloqueio de conflito)
2. Fase 3 (US1) + Fase 4 (US2) — formam o agendamento completo e seguro (sem isso, não há MVP
   utilizável)
3. **VALIDAR**: agendar uma defesa de ponta a ponta, com banca e bloqueio de conflito
4. Fase 6 (US4) — ciclo de confirmação/reagendamento/cancelamento; Fase 5 (US3) pode entrar a
   qualquer momento depois da Fase 2b, já que é só teste
5. Fase 7 (US5) — lista e histórico (P2, pode entrar depois do MVP)

### Entrega incremental

Fase 2a (fase base, 03/11) → Fase 2b → US1+US2 (MVP de agendamento seguro) → US3 (teste de
confirmação) → US4 (ciclo completo) → US5 (consulta) → Polish.
