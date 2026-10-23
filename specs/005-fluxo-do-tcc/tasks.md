# Tasks: Fluxo do TCC e Entregas do SIGTCC

**Input**: Design documents from `specs/005-fluxo-do-tcc/`

**Prerequisites**: [plan.md](plan.md) (aprovado em 2026-10-22, revisado duas vezes pelo
`arquiteto-django`), [spec.md](spec.md) (aprovada em 2026-10-22; Clarifications da sessão
2026-10-22), [research.md](research.md) (C1 a C9), [data-model.md](data-model.md),
[contracts/rotas.md](contracts/rotas.md), [contracts/servicos-compartilhados.md](contracts/servicos-compartilhados.md),
[quickstart.md](quickstart.md)

**Aprovação**: plano aprovado por Julia Cohen em 2026-10-22; tasks.md aprovado por Julia Cohen em
2026-10-22, depois de `/speckit-analyze` (achados A1 a A4, todos corrigidos: trava do TCC no
envio de entrega, T021; qualificadores de FR-007a; contagem de cenários do SC-005; mensagem
`LINK_HTTPS_500` confirmada como nova em T001).

**Tests**: obrigatórios (constituição, princípio VI): cada cenário Dado/Quando/Então das US-13
(7), US-14 (11), US-43 (5), US-15 (8), US-16 (5), US-29 (6) e US-44 (5) vira pelo menos um teste,
mais os casos das Clarifications, de permissão (Secretaria e Coorientador excluídos), de mensagens
exatas e de concorrência (travas da revisão do `arquiteto-django`). Os testes de cada fase vêm
antes da implementação e devem falhar primeiro.

**Organization**: histórias da spec: US1 = Proposta e dados do TCC (US-13), US2 = Status,
histórico e trilha (US-14), US3 = cadastro de entregas (US-43), US4 = envio e substituição de
link (US-15), US5 = acompanhamento (US-16), US6 = envio da Versão Final (US-29), US7 =
homologação ou devolução (US-44).

**Branch**: `feature/feat-05-fluxo-do-tcc`. Commits atômicos ao fim de cada fase, só com os
testes passando, mostrando o `git status` antes (CLAUDE.md). Formato:
`feat(feat-05): <imperativo, até 72 caracteres, sem ponto final>`. Não fazer push, merge nem tag.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência de tarefa incompleta)
- **[Story]**: história da spec (US1 a US7)

## Regras para todas as tarefas

- Comentários e docstrings em português; cada classe, função, template e teste indica as US e RBN
  que atende (constituição, princípio II). Cada tarefa termina com `Rastreabilidade:`.
- Mensagens sempre por constantes de `sigtcc/apps/cadastro/mensagens.py` (T001).
- Nenhuma tabela, coluna ou migração nova (data-model.md). Nenhum JavaScript do protótipo.
- Regras em `services_tcc.py`, `services_entregas.py` e nas duas funções novas de
  `services_turmas.py`; views só orquestram; templates sem regra.
- `tcc_status` **nunca** é lido/gravado fora de `services_turmas.criar_tcc_com_historico` ou
  `services_turmas.atualizar_status_tcc` (FR-012; research C2) — nenhuma tarefa de implementação
  deve fazer `tcc.tcc_status = ...` fora desses dois pontos.
- Travas (research C4, C7): `atualizar_status_tcc`/`criar_tcc_com_historico` pressupõem turma →
  aluno → TCC já travados (`select_for_update`, `transaction.atomic()`) por quem chama; o envio de
  entrega trava a própria `Entregas_Marcos`; a gravação de Palavra-Chave trava o TCC.
- Ordem das conferências em toda rota (research C1/contracts/rotas.md): turma existe (404) →
  permissão (403, M-02 da spec 003) → turma arquivada (MT-25); rotas de aluno exigem
  `vinculo_na_turma` e que o usuário autenticado seja o próprio aluno (sem IDOR).
- Confidencialidade do Resumo e do histórico: toda view que exiba `tcc_resumo` chama
  `services_tcc.pode_ver_resumo`; toda consulta de histórico passa por
  `services_tcc.historico_do_status`, nunca reimplementada (research C3, C9).
- Notificações só pelo `services.notificar()` (spec 003/004, já existente).
- Datas: `django.utils.timezone.now()` chamado pelo módulo (compatível com `avancar_relogio` dos
  testes), sem fuso (`USE_TZ = False`).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: esqueleto dos módulos novos, sem regra ainda.

- [X] T001 [P] Acrescentar em `sigtcc/apps/cadastro/mensagens.py` (seção "spec 005"), copiando caractere por caractere das US: `PROPOSTA_SALVA = "Proposta salva"`, `ALTERACOES_SALVAS = "Alterações salvas"`, `INFORME_PALAVRAS_CHAVE = "Informe de 1 a 5 Palavras-Chave"`, `LINK_HTTPS_500 = "O link deve começar com https:// e ter até 500 caracteres"` (confirmado na análise `/speckit-analyze`: não existe constante equivalente em `mensagens.py`; criar nova, nesta spec), `ENTREGA_CADASTRADA = "Entrega cadastrada"`, `ENTREGA_TIPO_REPETIDO = "A turma já tem uma entrega deste tipo"`, `NENHUMA_ENTREGA_CADASTRADA = "Nenhuma entrega cadastrada"`, `ENTREGA_ENVIADA = "Entrega enviada"`, `ENTREGA_CUMPRIDA_PROPOSTA = "Esta entrega é cumprida ao salvar a Proposta"`, `VERSAO_FINAL_ENVIADA = "Versão Final enviada"`, `VERSAO_FINAL_HOMOLOGADA = "Versão Final homologada"`; e as PROVISÓRIAS `MF01_DATA_LIMITE_VENCIDA = "Data Limite vencida: o envio será registrado como Entregue com Atraso."`, `MF02_VERSAO_FINAL_DEVOLVIDA = "Versão Final devolvida para ajuste."`, `MF03_PALAVRA_CHAVE_REPETIDA = "Palavra-chave repetida."`. Reaproveitar `CAMPO_OBRIGATORIO` (M-14, spec 003) e `JUSTIFICATIVA_500` (spec 004) sem duplicar. — Rastreabilidade: [US-13][US-14][US-43][US-15][US-16][US-29][US-44][SC-006]
- [X] T002 [P] Criar `sigtcc/apps/cadastro/services_tcc.py` e `sigtcc/apps/cadastro/services_entregas.py` vazios, cada um com a docstring do módulo citando as US que atende (research C1). — Rastreabilidade: [research C1]
- [X] T003 [P] Criar `sigtcc/apps/cadastro/forms_tcc.py`, `sigtcc/apps/cadastro/forms_entregas.py`, `sigtcc/apps/cadastro/views_tcc.py` e `sigtcc/apps/cadastro/views_entregas.py` vazios, cada um com a docstring do módulo. — Rastreabilidade: [research C1]
- [X] T004 [P] Criar o diretório `sigtcc/templates/cadastro/tcc/` (vazio, só para existir no controle de versão: `.gitkeep` ou o primeiro template da Phase 3). — Rastreabilidade: [plan.md, Project Structure]

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: o serviço único de gravação do Status (FR-012), a confidencialidade do Resumo
(FR-007a), a consulta de histórico sem checagem de perfil (research C9), fábricas de teste.

**⚠️ CRITICAL**: nenhuma história começa antes desta fase.

- [ ] T005 Em `sigtcc/apps/cadastro/services_turmas.py`, acrescentar `TRANSICOES_VALIDAS` (dict `GatilhoStatusTCC` → conjunto de pares `(status_atual, novo_status)` permitidos, research C2 — confirmar as 7 entradas, com "Encerramento da participação" usando só `EM_ANDAMENTO`/`APTO_PARA_DEFESA` como origem, igual a `STATUS_TCC_ENCERRAVEL`), `_validar_transicao(anterior, novo_status, gatilho)` (levanta `ValueError` fora da tabela), `criar_tcc_com_historico(aluno, turma, autor, status_inicial, gatilho, anterior=None)` e `atualizar_status_tcc(tcc, turma, autor, novo_status, gatilho)` (ambas chamam `_registrar_historico`, que continua privada). Escrever o teste `test_atualizar_status_tcc` em `sigtcc/apps/cadastro/tests/test_base_turmas.py` (transição válida grava; transição fora da tabela levanta `ValueError` sem gravar nada; gatilho inexistente idem) antes da implementação. — Rastreabilidade: [US-14][RBN-CAD-08.3][RBN-CAD-08.7][FR-008][FR-012][SC-002][research C2]
- [ ] T006 Atualizar `matricular` (gatilho "Vínculo à turma"), `_copiar_tcc_aprovado` (gatilho "Transferência para TCC 2") e `encerrar_participacao` (gatilho "Encerramento da participação"), todos em `services_turmas.py`, para chamar `criar_tcc_com_historico` ou `atualizar_status_tcc` em vez do padrão manual atual (`tcc.tcc_status = ...; tcc.save(...)` seguido de `_registrar_historico`). Rodar a suíte completa da spec 004 (`test_us07_turmas`, `test_us08_matricula`, `test_us08_importacao`, `test_us08_transferencia`, `test_us09_exclusao`) e confirmar que passa sem alteração nos testes. **Pendência Q-46**: aguarda aprovação de Leandra Matos e Célio Benjamim antes do merge (por tocar código já mesclado de outra feature); pode prosseguir com a implementação e os testes enquanto a aprovação não chega, mas o PR não fecha sem ela. — Rastreabilidade: [US-08][US-09][FR-012][Q-46]
- [ ] T007 [P] Em `services_tcc.py`, criar `pode_ver_resumo(usuario, tcc) -> bool` (Aluno dono; Orientador atual, `Orientacoes.ori_status='Ativa'`; Docente com `Solicitacoes_Orientacao` pendente para esse TCC; Coorientador do NUCOMP, `Coorientacoes.coo_status='Ativa'`; Professor da Disciplina da turma do TCC — FR-007a, research C3) e `historico_do_status(tcc) -> queryset` (todas as linhas de `Historico_Status_TCC` do TCC, ordenadas da mais antiga à mais recente, **sem checagem de perfil** — research C9). Testes em `sigtcc/apps/cadastro/tests/test_us14_status_historico.py`: cada uma das 5 categorias de `pode_ver_resumo` retorna `True`, um Docente sem vínculo retorna `False`; `historico_do_status` devolve a ordem certa e não filtra por perfil (a checagem é responsabilidade de quem chama). — Rastreabilidade: [US-13][US-14][RAN-CAD-07][FR-007a][FR-009][research C3][research C9]
- [ ] T008 [P] Criar `sigtcc/apps/cadastro/tests/apoio_tcc.py` com fábricas sobre `apoio_turmas.criar_turma_de`/`matricular_aluno` (spec 004): `salvar_proposta(tcc, titulo=..., resumo=..., modalidade=...)`, `cadastrar_entrega(turma, tipo, titulo, data_limite)`, `enviar_link(entrega, aluno, link, quando=None)` (usa `avancar_relogio` ou equivalente para controlar `hen_data_envio` nos testes de prazo). — Rastreabilidade: [infraestrutura de teste da feature 005]
- [ ] T009 Rodar `python manage.py test sigtcc.apps.cadastro.tests.test_base_turmas sigtcc.apps.cadastro.tests.test_us14_status_historico` e a suíte inteira das features 001, 003 e 004, até passar. — Rastreabilidade: [SC-002]

**Checkpoint**: base pronta; as histórias podem começar.

---

## Phase 3: User Story 1 - Aluno registra a Proposta e os dados do TCC [US-13] (Priority: P1) 🎯 MVP

**Goal**: o Aluno salva a Proposta (muda o Status para "Em Andamento"), depois a Área de
Interesse e as Palavras-Chave, e pode alterar tudo enquanto "Em Andamento", com notificação ao
Orientador.

**Independent Test**: criar um aluno com TCC "Sem Proposta" (fábrica `matricular_aluno`), salvar a
Proposta pelo serviço, e verificar que o Status muda para "Em Andamento" e que os campos de Área
de Interesse e Palavras-Chave ficam disponíveis — sem depender de nenhuma outra história.

### Tests for User Story 1 ⚠️

- [ ] T010 [P] [US1] Criar `sigtcc/apps/cadastro/tests/test_us13_proposta.py` com os 7 cenários da US-13 (Proposta salva; Área/Palavras-Chave salvas; entrega do tipo Proposta cumprida dentro e depois do prazo — 2 cenários; mudança de tema com e sem orientador — 2 cenários; bloqueio pelo Status "Apto para Defesa"), mais os cenários de exceção (campo obrigatório, limite de caracteres, link inválido, nenhuma Palavra-Chave, sexta Palavra-Chave, Status Desistente/Reprovado/Jubilado, turma arquivada) e o cenário novo da Clarifications (Palavra-Chave repetida, MF-03). Escrever antes da implementação; deve falhar. — Rastreabilidade: [US-13][RBN-CAD-07.1][RBN-CAD-08.1][RBN-CAD-08.2][FR-001 a FR-007a]

### Implementation for User Story 1

- [ ] T011 [US1] Em `services_tcc.py`: `salvar_proposta(aluno, tur_id, dados)` (turma travada via `travar_turma_ativa`; recusa se o Status não for "Sem Proposta" ou já existir Proposta — `UNIQUE (tcc_alu, tcc_tur)`; chama `atualizar_status_tcc(..., StatusTCC.EM_ANDAMENTO, GatilhoStatusTCC.PROPOSTA_SALVA)`; cumpre a entrega do tipo Proposta, se existir, com o status calculado pela data do salvamento) e `salvar_alteracoes_tcc(tcc, dados)` (Área de Interesse, Palavras-Chave e mudança de tema; `transaction.atomic()` com `select_for_update()` no TCC; apaga e recria `PalavrasChave_TCC`; captura `IntegrityError` → MF-03; notifica o Orientador atual, se houver, a cada chamada com algum campo de tema alterado). — Rastreabilidade: [US-13][RBN-CAD-07.1][RBN-CAD-08.1][RBN-CAD-08.2][FR-001 a FR-005][research C2][research C3]
- [ ] T012 [US1] Em `forms_tcc.py`: `PropostaForm` (Título, Subtítulo, Resumo com contador, Modalidade, Link) e `DadosTCCForm` (Área de Interesse, até 5 campos de Palavra-Chave) com as validações do FR-007 e a checagem de Palavra-Chave repetida no `clean()` (Clarifications). — Rastreabilidade: [US-13][RBN-CAD-07.1][RBN-CAD-08.1][FR-007][FR-007 Clarifications]
- [ ] T013 [US1] Em `views_tcc.py`: `meu_tcc(request, tur_id)` (GET exibe os formulários conforme o Status; POST chama `salvar_proposta` ou `salvar_alteracoes_tcc`), restrita a `@perfil_requerido("aluno")` e à checagem de que o usuário é o próprio aluno da turma (`vinculo_na_turma`, sem IDOR); template `sigtcc/templates/cadastro/tcc/meu_tcc.html` com a seção Proposta, a etiqueta do Status (somente leitura) e, condicionalmente, Área de Interesse/Palavras-Chave. Rota `meu_tcc` em `urls.py` (contracts/rotas.md). — Rastreabilidade: [US-13][FR-001][FR-006][contracts/rotas.md]

**Checkpoint**: a Proposta e os dados do TCC funcionam de ponta a ponta, isoladamente.

---

## Phase 4: User Story 2 - Status do TCC muda automaticamente e tem histórico e trilha [US-14] (Priority: P1)

**Goal**: o Status nunca é editado manualmente; muda só pelos 7 gatilhos fixos, com histórico e
trilha consultáveis por Aluno, Orientador e Professor da Disciplina (nunca Secretaria nem
Coorientador).

**Independent Test**: disparar cada gatilho (via `services_turmas`) e verificar o Status
resultante e o registro em `historico_do_status`, sem depender da interface das outras histórias.

### Tests for User Story 2 ⚠️

- [ ] T014 [P] [US2] Criar `sigtcc/apps/cadastro/tests/test_us14_status_historico.py` (complementa T007) com os 11 cenários da US-14 (Sem Proposta ao vincular; Em Andamento ao salvar Proposta; Apto para Defesa; as 4 variações de Liberação do resultado — Aprovado para TCC 2, Aprovado, Aprovado com Correções, Reprovado; Concluído na homologação; Desistente/Jubilado e Reprovado pelo Professor no encerramento — 2 cenários; trilha encerrada), mais consulta pelo Aluno, pelo Orientador (via `historico_do_status` direto, simulando a futura spec 006) e pelo Professor, e os cenários de exceção (sem edição manual; Docente sem vínculo não vê; Secretaria não vê, Clarifications). Escrever antes da implementação da view; deve falhar na parte de view/rota (os testes de `TRANSICOES_VALIDAS` já passam desde T005). — Rastreabilidade: [US-14][RBN-CAD-08.3][RBN-CAD-08.7][RBN-CAD-08.8][FR-008 a FR-012]

### Implementation for User Story 2

- [ ] T015 [US2] Em `views_tcc.py`: `historico_status_aluno(request, tur_id)` (Aluno, o próprio — `@perfil_requerido("aluno")`) e `historico_status(request, tur_id, alu_id)` (Professor da Disciplina da turma — `@perfil_requerido("docente")` + checagem explícita, **nunca** Secretaria nem Coorientador), ambas chamando `services_tcc.historico_do_status(tcc)` só depois de autorizar; template `sigtcc/templates/cadastro/tcc/historico_status.html` (lista cronológica somente leitura + trilha com a etapa atual destacada, FR-010). Rotas em `urls.py` (contracts/rotas.md). Acrescentar o link "Histórico do Status do TCC" (nome provisório, Q-45) em `meu_tcc.html`. — Rastreabilidade: [US-14][FR-009][FR-010][contracts/rotas.md][Q-45]
- [ ] T016 [US2] Trilha do Status (FR-010): função `trilha_do_status(tcc)` em `services_tcc.py`, que devolve a sequência fixa (TCC 1: Em Andamento → Apto para Defesa → Aprovado para TCC 2; TCC 2: Em Andamento → Apto para Defesa → Aprovado/Aprovado com Correções → Concluído) com a etapa atual destacada, e encerra a sequência em Reprovado/Desistente/Jubilado sem as etapas seguintes. Teste de cada trilha (TCC 1, TCC 2, trilha encerrada) em `test_us14_status_historico.py`. — Rastreabilidade: [US-14][RBN-CAD-08.8][FR-010]

**Checkpoint**: Status, histórico e trilha funcionam isoladamente, via serviço e via tela.

---

## Phase 5: User Story 3 - Professor cadastra as entregas da turma [US-43] (Priority: P1)

**Goal**: o Professor cadastra entregas (Proposta, Documento para Defesa, Versão Final ou Outra),
com os registros de status criados para todos os alunos da turma, inclusive os já matriculados.

**Independent Test**: cadastrar uma entrega numa turma com alunos já matriculados e verificar que
a entrega aparece na lista, que cada aluno recebe "Aguardando Envio" (ou "Não Entregue") e a
notificação, e que a turma não aceita duas entregas do mesmo tipo (exceto "Outra").

### Tests for User Story 3 ⚠️

- [ ] T017 [P] [US3] Criar `sigtcc/apps/cadastro/tests/test_us43_cadastro_entregas.py` com os 5 cenários de aceite (cadastro; tipos por etapa TCC1/TCC2; entrega do tipo Proposta sem campo de link; entrega do tipo Versão Final define o prazo; cancelamento; aluno vinculado depois do cadastro — 6 cenários no total, mais tipo repetido, turma arquivada e usuário sem permissão). Escrever antes da implementação; deve falhar. — Rastreabilidade: [US-43][RBN-CAD-09.1][RBN-CAD-09.6][FR-013 a FR-017]

### Implementation for User Story 3

- [ ] T018 [US3] Em `services_entregas.py`: `cadastrar_entrega(professor, tur_id, dados)` — turma travada (`travar_turma_ativa`), `transaction.atomic()`, cria `Turmas_Marcos` capturando `IntegrityError` → `ENTREGA_TIPO_REPETIDO` (research C6); para cada `AlunosTurmas` ativo com participação não encerrada, cria `Entregas_Marcos` ("Aguardando Envio" ou "Não Entregue", conforme a Data Limite) — mesma regra de `criar_entregas_do_aluno` (spec 004), chamada aqui para os alunos já matriculados (índice Q-41); notifica cada aluno via `services.notificar()`. — Rastreabilidade: [US-43][RBN-CAD-09.1][RBN-CAD-09.6][FR-013 a FR-016][Q-41][research C6]
- [ ] T019 [US3] Em `forms_entregas.py`: `CadastroEntregaForm` (Tipo — lista restrita por TCC 1/TCC 2 do FR-013 —, Título, Instruções, Data Limite não anterior a hoje). Em `views_entregas.py`: `entregas(request, tur_id)` (lista + botão "Cadastrar atividade") e `entrega_cadastrar(request, tur_id)` (GET/POST), restritas ao Professor da Disciplina da turma; templates `entregas.html` e `form_entrega.html`. Rotas em `urls.py`. — Rastreabilidade: [US-43][FR-013][FR-017][contracts/rotas.md]

**Checkpoint**: cadastro de entregas funciona isoladamente, inclusive para alunos já matriculados.

---

## Phase 6: User Story 4 - Aluno envia ou substitui o link de uma entrega [US-15] (Priority: P1)

**Goal**: o Aluno envia e substitui o link de cada entrega (exceto Proposta) até a Data Limite,
com cálculo automático do status de envio e lembretes de prazo.

**Independent Test**: com uma entrega já cadastrada, enviar um link válido antes e depois da Data
Limite e verificar o status resultante, e tentar substituir depois da Data Limite.

### Tests for User Story 4 ⚠️

- [ ] T020 [P] [US4] Criar `sigtcc/apps/cadastro/tests/test_us15_envio_entrega.py` com os 13 cenários de aceite e exceção da US-15 (envio no prazo; acesso pela notificação; atraso; prazo vencido sem envio; substituição no prazo; lembrete de prazo; entrega do tipo Proposta sem campo de link; link inválido; substituição após o prazo; TCC fora de Em Andamento; aluno Desistente/Jubilado; turma arquivada), mais dois testes de corrida: duas chamadas quase simultâneas a `enviar_entrega` para o mesmo aluno/entrega devem produzir um único "primeiro envio" consistente (research C7), e `enviar_entrega` concorrendo com `encerrar_participacao` para o mesmo TCC não deve permitir envio depois que a participação for encerrada (achado A1 da análise `/speckit-analyze`). Escrever antes da implementação; deve falhar. — Rastreabilidade: [US-15][RBN-CAD-09.2][RBN-CAD-09.3][RBN-CAD-09.6][FR-018 a FR-023]

### Implementation for User Story 4

- [ ] T021 [US4] Em `services_entregas.py`: `enviar_entrega(aluno, tma_id, link)` — `transaction.atomic()` com `EntregasMarcos.objects.select_for_update()` **e** `TCCs.objects.select_for_update()` (o TCC do aluno naquela entrega) **antes** de consultar o primeiro envio e de checar `tcc.tcc_status` (achado A1 da análise `/speckit-analyze`: sem travar o TCC, uma corrida com `encerrar_participacao`/`atualizar_status_tcc` — que travam turma→aluno→TCC — poderia deixar passar um envio com um Status já mudado no meio da requisição); cria `HistoricoEnviosEntregas`; recalcula `ent_status` a partir do primeiro envio (Entregue/Entregue com Atraso), nunca do mais recente; recusa (campo só leitura) se a entrega for do tipo Proposta, se o TCC não estiver "Em Andamento" (fora da Versão Final, tratada em US6), se a participação estiver encerrada, se a turma estiver arquivada, ou se já passou a Data Limite sem devolução pendente; notifica o Professor da Disciplina a cada envio e substituição. — Rastreabilidade: [US-15][RBN-CAD-09.2][RBN-CAD-09.3][FR-018 a FR-020][FR-023][research C7]
- [ ] T022 [US4] `entregas_para_lembrar(agora)` em `services_entregas.py` (função pura: `Entregas_Marcos` "Aguardando Envio" com `tma_data_limite` a 7 dias/48h/24h de `agora`, margem ±1h, turma não arquivada — research C5); comando de gestão `enviar_lembretes_entrega.py` que chama a função e usa `services.notificar()`, documentado como pendência de agendamento para o Célio (research C5). — Rastreabilidade: [US-15][RBN-CAD-09.6][FR-022][research C5]
- [ ] T023 [US4] Em `forms_entregas.py`: `EnviarLinkForm` (Link obrigatório, `https://`, até 500 — `LINK_HTTPS_500`). Em `views_entregas.py`: `minhas_entregas(request, tur_id)` e `entrega_enviar(request, tur_id, tma_id)`, restritas ao Aluno dono (sem IDOR); templates `minhas_entregas.html` e `enviar_entrega.html` (com o aviso "Esta entrega é cumprida ao salvar a Proposta" para o tipo Proposta). Rotas em `urls.py`. — Rastreabilidade: [US-15][FR-018][contracts/rotas.md]

**Checkpoint**: envio e substituição de link funcionam isoladamente, com cálculo de status correto
mesmo sob corrida.

---

## Phase 7: User Story 5 - Professor acompanha as entregas dos alunos da turma [US-16] (Priority: P2)

**Goal**: o Professor consulta, por aluno, o status de envio e o link de cada entrega.

**Independent Test**: com uma entrega e três alunos (sem envio, no prazo, com atraso), abrir o
acompanhamento e verificar as três linhas.

### Tests for User Story 5 ⚠️

- [ ] T024 [P] [US5] Criar `sigtcc/apps/cadastro/tests/test_us16_acompanhamento.py` com os 5 cenários de aceite e exceção (acompanhamento; aluno sem envio após o prazo; envio com atraso; entrega do tipo Proposta mostra "Ver Proposta"; turma arquivada), mais acesso restrito (Docente sem permissão) e "Nenhuma entrega cadastrada". Escrever antes da implementação; deve falhar. — Rastreabilidade: [US-16][RBN-CAD-09.4][FR-026][FR-027]

### Implementation for User Story 5

- [ ] T025 [US5] Em `services_entregas.py`: `acompanhamento_entrega(tma_id) -> lista` (uma linha por aluno da turma com participação não encerrada: nome, matrícula, status de envio, link mais recente — `HistoricoEnviosEntregas` ordenado por `hen_data_envio` — ou, no tipo Proposta, referência à Proposta do aluno em vez do link). Em `views_entregas.py`: `entrega_acompanhar(request, tur_id, tma_id)`, restrita ao Professor da Disciplina da turma; template `acompanhamento_entrega.html` (chama `pode_ver_resumo` antes de linkar a Proposta, já que o Professor da turma está nas categorias permitidas, mas a função centraliza a checagem mesmo assim). Rota em `urls.py`. — Rastreabilidade: [US-16][RBN-CAD-09.4][FR-026][FR-027][contracts/rotas.md]

**Checkpoint**: acompanhamento funciona isoladamente, com as entregas e os envios das histórias anteriores.

---

## Phase 8: User Story 6 - Aluno envia a Versão Final do TCC 2 [US-29] (Priority: P2)

**Goal**: o Aluno de TCC 2, com o resultado liberado como Aprovado ou Aprovado com Correções,
envia o PDF final (texto corrigido, Folha de Aprovação, ficha catalográfica).

**Independent Test**: com um TCC 2 "Aprovado" (sem depender da banca real) e a entrega "Versão
Final" cadastrada, enviar o link e verificar o status.

### Tests for User Story 6 ⚠️

- [ ] T026 [P] [US6] Criar `sigtcc/apps/cadastro/tests/test_us29_versao_final.py` com os 13 cenários de aceite e exceção da US-29 (envio no prazo; parecer Aprovado sem correções; atraso — com a mensagem MF-01 antes do envio; prazo vencido sem link; substituição no prazo; reenvio após devolução; link inválido; resultado ainda não liberado; TCC 1 sem seção; substituição após o prazo; Versão Final homologada; parecer Reprovado). Escrever antes da implementação; deve falhar. — Rastreabilidade: [US-29][RBN-CAD-09.2][RBN-CAD-09.3][FR-023 a FR-025]

### Implementation for User Story 6

- [ ] T027 [US6] Estender `enviar_entrega` (T021) para a entrega do tipo "Versão Final": libera o envio só com `tcc.tcc_status` em `(StatusTCC.APROVADO, StatusTCC.APROVADO_COM_CORRECOES)` (FR-024; sem campo de "parecer" novo, `tcc_status` já distingue os casos — research C7); exibe a mensagem provisória MF-01 quando a Data Limite já passou e ainda não há envio; permite reenvio quando `ent_status = 'Devolvida para Ajuste'` (FR-025), recalculando o status pelo mesmo cálculo do primeiro envio. — Rastreabilidade: [US-29][RBN-CAD-09.2][RBN-CAD-09.3][FR-023 a FR-025][research C7]
- [ ] T028 [US6] Em `meu_tcc.html` (ou um template incluído), acrescentar a seção "Versão final" (só em turma de TCC 2 com a entrega cadastrada): nota, parecer, Data Limite, botões Ata Final/Folha de Aprovação (consumidos de outra spec — US-28, fora do escopo; exibir "Disponível após a liberação do resultado" enquanto não houver `tcc_status` em Aprovado/Aprovado com Correções/Reprovado liberado) e o campo Link reaproveitando `entrega_enviar`. — Rastreabilidade: [US-29][FR-023][FR-024]

**Checkpoint**: envio da Versão Final funciona isoladamente, pré-condicionado só pelo Status do TCC.

---

## Phase 9: User Story 7 - Professor homologa ou devolve a Versão Final [US-44] (Priority: P2)

**Goal**: o Professor homologa a Versão Final (conclui o TCC) ou devolve para ajuste; em Sistemas
de Informação com parecer "Aprovado com Correções", exige "Correções Conferidas" do Orientador
antes.

**Independent Test**: com a Versão Final já enviada, homologar e verificar "Concluído" e a
notificação à Secretaria; separadamente, devolver com mensagem e verificar "Devolvida para
Ajuste" e a notificação ao aluno.

### Tests for User Story 7 ⚠️

- [ ] T029 [P] [US7] Criar `sigtcc/apps/cadastro/tests/test_us44_homologacao.py` com os 10 cenários de aceite e exceção da US-44 (homologação; parecer Aprovado sem correções; correções conferidas em Sistemas de Informação; acesso pela notificação; devolução para ajuste — com a mensagem MF-02; correções ainda não conferidas; devolução sem mensagem; Versão Final ainda não enviada; usuário sem permissão). Escrever antes da implementação; deve falhar. — Rastreabilidade: [US-44][RBN-CAD-09.3][RBN-CAD-09.5][FR-028 a FR-030]

### Implementation for User Story 7

- [ ] T030 [US7] Em `services_entregas.py`: `homologar_versao_final(professor, tur_id, alu_id)` — `transaction.atomic()` com turma → aluno → TCC travados; recusa (Http404 ou erro, conforme o caso) se o envio não existir, se o Docente não for o Professor da Disciplina, ou se o TCC for de Sistemas de Informação com parecer "Aprovado com Correções" e `ent_correcoes_conferidas_em` vazio (FR-029; o campo é gravado pela futura spec 006, esta spec só lê e valida); muda `ent_status` para "Homologada", chama `atualizar_status_tcc(..., StatusTCC.CONCLUIDO, GatilhoStatusTCC.HOMOLOGACAO_DA_VERSAO_FINAL)` e notifica a Secretaria. `devolver_versao_final(professor, tur_id, alu_id, mensagem)` — mensagem obrigatória até 500 caracteres (`JUSTIFICATIVA_500`); muda `ent_status` para "Devolvida para Ajuste", grava `ent_feedback` e `ent_data_avaliacao`, notifica o Aluno. — Rastreabilidade: [US-44][RBN-CAD-09.3][RBN-CAD-09.5][FR-028][FR-029][research C2]
- [ ] T031 [US7] Em `forms_entregas.py`: `DevolverParaAjusteForm` (Mensagem obrigatória, até 500). Em `views_entregas.py`: `aluno_versao_final(request, tur_id, alu_id)` (GET exibe link/status/botões conforme o caso; POST homologa ou devolve), restrita ao Professor da Disciplina da turma de TCC 2; template `homologar_versao_final.html` com as mensagens "Versão Final homologada" e, provisória, "Versão Final devolvida para ajuste" (MF-02). Rota em `urls.py`. — Rastreabilidade: [US-44][FR-028][FR-030][contracts/rotas.md]

**Checkpoint**: homologação e devolução funcionam isoladamente; o ciclo de vida completo do TCC 2
(Proposta → entregas → Versão Final → homologação → Concluído) está testável de ponta a ponta.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: mensagens exatas, permissões por perfil, roteiro manual.

- [ ] T032 [P] Criar `sigtcc/apps/cadastro/tests/test_mensagens_tcc.py` (padrão de `test_mensagens_turmas.py`, spec 004): cada constante exata de `mensagens.py` contra o texto entre aspas das US-13, 14, 15, 16, 29, 43 e 44; as MF-01 a MF-03 contra a tabela "Mensagens a validar com a PO" do `spec.md`. — Rastreabilidade: [SC-006]
- [ ] T033 [P] Criar `sigtcc/apps/cadastro/tests/test_permissoes_tcc.py` cobrindo todas as 8 rotas de `contracts/rotas.md`, perfil por perfil: sem login (redireciona com `next`); outro Docente (403); Secretaria do curso tentando ver histórico/entregas/Proposta de outro aluno (403 — Clarifications); Coorientador do NUCOMP tentando ver histórico (403 — Clarifications); aluno de outra turma tentando acessar `meu_tcc`/`minhas_entregas`/`entrega_enviar` de outro aluno (404, sem IDOR); turma arquivada (MT-25 nas ações, consulta liberada); só POST nas ações que mudam dado. — Rastreabilidade: [SC-004][Clarifications][contracts/rotas.md]
- [ ] T034 Rodar `isort`, `black --line-length 100` e `flake8 --max-line-length 100` (ou `lint.bat`) sem erros; rodar `python manage.py makemigrations --check --dry-run` (deve responder "No changes detected" — nenhuma migração nesta feature); rodar a suíte completa (`python manage.py test sigtcc.apps`) até passar, incluindo a regressão da spec 004 (T006). — Rastreabilidade: [constituição, princípios V e VI]
- [ ] T035 Executar o roteiro manual do `quickstart.md` (passos a a o, mais a verificação de fronteira com a spec 006 via shell) e registrar o resultado (data, responsável, divergências) no `spec.md`, seção de validação manual, no mesmo formato já usado pela spec 004. — Rastreabilidade: [SC-001][SC-003][quickstart.md]

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências — pode começar imediatamente.
- **Foundational (Phase 2)**: depende do Setup; BLOQUEIA todas as histórias (T005/T006 são a base
  de FR-012, usada por US1, US2, US6 e US7; T007 é a base de US2 e US5).
- **User Stories (Phase 3 a 9)**: todas dependem da Foundational. Ordem sugerida pela própria
  cadeia de dados (Proposta → Status → entregas → envio → acompanhamento → Versão Final →
  homologação), mas US3, US5 e US7 têm dependência direta de dados de US1/US2/US4/US6 só para o
  roteiro manual, não para os testes unitários (cada história usa fábricas, não a tela anterior).
- **Polish (Phase 10)**: depende de todas as histórias desejadas estarem completas.

### User Story Dependencies

- **US1 (P1)**: depende só da Foundational.
- **US2 (P1)**: depende só da Foundational (T005/T007); historicamente alimentada por US1, mas
  testável sozinha via `services_turmas` direto.
- **US3 (P1)**: depende só da Foundational.
- **US4 (P1)**: depende de US3 existir (precisa de uma entrega cadastrada) só para o teste de
  integração ponta a ponta; o serviço `enviar_entrega` é testável com a fábrica `cadastrar_entrega`
  (T008) sem depender da view de US3.
- **US5 (P2)**: usa dados de US3 e US4 (fábricas), sem depender das views delas.
- **US6 (P2)**: estende o serviço de US4 (T021); depende de US4 completa.
- **US7 (P2)**: depende de US6 completa (precisa de um envio de Versão Final) e de T005/T006 (usa
  `atualizar_status_tcc`).

### Parallel Opportunities

- T001 a T004 (Setup) em paralelo.
- T007 e T008 (Foundational) em paralelo entre si, depois de T005/T006.
- Testes de cada história (`[P]`, ex. T010, T014, T017, T020, T024, T026, T029) podem ser escritos
  em paralelo por pessoas diferentes, já que são arquivos distintos.
- US1, US2 e US3 podem ser implementadas em paralelo por pessoas diferentes depois da Foundational
  (sem dependência direta entre si); US4 depende só da Foundational para o serviço, mas da US3
  para o roteiro manual; US5 depois de US3/US4; US6 depois de US4; US7 depois de US6.

---

## Implementation Strategy

### MVP First (US1 + US2 + US3 + US4)

1. Completar Phase 1 (Setup) e Phase 2 (Foundational) — bloqueante.
2. Completar US1 (Proposta) — sem ela, nada mais tem Status "Em Andamento" para testar de verdade.
3. Completar US2 (Status/histórico) — valida que US1 gravou certo.
4. Completar US3 (cadastro de entregas) e US4 (envio) — ciclo básico de entrega.
5. **PARAR e VALIDAR**: rodar o roteiro manual (passos a a i do `quickstart.md`) com só essas 4
   histórias.

### Incremental Delivery

1. Setup + Foundational → base pronta.
2. US1 → testar isoladamente → MVP da Proposta.
3. US2 → testar isoladamente → Status/histórico visíveis.
4. US3 → US4 → ciclo de entregas completo (exceto Versão Final).
5. US5 → acompanhamento do Professor.
6. US6 → US7 → ciclo do TCC 2 completo, até "Concluído".
7. Phase 10 → mensagens, permissões, roteiro completo.

## Notes

- `[P]` = arquivos diferentes, sem dependência de tarefa incompleta.
- `[Story]` mapeia a tarefa à história (US1 a US7) para rastreabilidade.
- Cada teste do início de fase deve falhar antes da implementação da mesma fase.
- Comitar depois de cada fase ou grupo de tarefas relacionadas, só com os testes passando,
  mostrando o `git status` antes (CLAUDE.md) — não fazer commit sem pedido explícito da pessoa.
- Parar em qualquer checkpoint para validar a história isoladamente.
