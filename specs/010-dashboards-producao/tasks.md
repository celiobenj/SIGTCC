---

description: "Task list para a feature 010 — Dashboards de Produção do SIGTCC"
---

# Tasks: Dashboards de Produção do SIGTCC

**Status**: Approved (Julia Cohen, 2026-11-06) — achados do `/speckit-analyze` aplicados (C1, F1, G1 a G3,
I1 a I3, A1); U1 ficou fora das correções

**Input**: Design documents from `/specs/010-dashboards-producao/`
**Prerequisites**: [plan.md](plan.md) (Approved, Julia Cohen, 2026-11-06), [spec.md](spec.md)
(Approved, Julia Cohen, 2026-11-05), [research.md](research.md), [data-model.md](data-model.md),
[contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: cada cenário de aceite das 5 User Stories vira pelo menos um teste Django (constituição,
princípio VI); os testes ficam em cada fase, escritos antes ou junto da implementação. Os cenários
são citados como `cenário <história>.<n>` (ex.: 1.10 = User Story 1, cenário 10).

**Organization**: tarefas por User Story, na ordem combinada: base e US-31, US-33, US-32, Histórico
e US-47. **A base fica pronta ao fim da Fase 3**, e o Célio pode começar a feat-11 a partir daí.
Commits atômicos por fase ou grupo de tarefas, só com os testes passando; `git status` antes de cada
commit (CLAUDE.md). Nenhuma migração.

**Aprovação**: tasks.md aprovado por Julia Cohen em 2026-11-06.

**Bloqueio**: a ciência do Célio nos contratos (Q-151) vem **antes** da Fase 2.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: US1 a US5, conforme spec.md (US1 = US-31; US2 = US-33; US3 = US-32; US4 = US-32 fluxo A;
  US5 = US-47)
- Cada tarefa indica as US e os RBN que atende e, entre parênteses, os FR e SC; todo código novo leva
  comentários em português com a mesma rastreabilidade
- Caminhos relativos a `sigtcc/apps/relatorios/`, quando não dito o contrário

---

## Phase 1: Setup (viabilidade e apoio de testes)

**Purpose**: provar as consultas no PostgreSQL antes de construir em cima delas; nenhuma dependência
nova.

- [X] T001 [US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2][RBN-REL-02.3][RBN-REL-02.4] Criar `sigtcc/apps/relatorios/tests/__init__.py` e `tests/apoio_relatorios.py`, sobre `apoio_defesa.py`: `aluno_na_turma(status)`, `sessao_realizada(banca, suplente_acionado=False)`, `artigo(tcc, status, homologacao)`, `transferido()`, `aprovado_e_matriculado_em_tcc2()`, `dados_hostis()` com `=1+1`, `-x`, `@a`, `<script>`, aspas, `#REF!`, `\x0b`, link `javascript:` e link de 500 caracteres (research R15)
- [X] T002 [US-32][RBN-CAD-08.7] (FR-041; research R5, R6) Teste de viabilidade em `tests/test_base_relatorios.py`: a subconsulta do último registro do histórico com `Coalesce`, dentro de `Count(filter=...)` depois de `values()`, sobre `AlunosTurmas`; rodar `EXPLAIN` e anotar em research R6 se a saída alternativa (`values(curso, status)`) será usada. Se a consulta não funcionar, parar e avisar

**Checkpoint**: consultas viáveis no PostgreSQL 16.

---

## Phase 2: Foundational (base do módulo)

**Purpose**: registro, filtros, estrutura, exportação e layout, de que todos os relatórios dependem
(contrato C1 a C5).

**⚠️ CRITICAL**: nenhum relatório começa antes do fim desta fase.

### Mensagens e estrutura

- [X] T003 [P] [US-31][US-47][US-32][US-33] (FR-014, FR-017; MR-01 a MR-14) Criar `mensagens.py`, só com constantes: textos exatos das US ("Nenhum registro encontrado para os filtros selecionados", "Nenhum registro") e MR-01 a MR-14; reaproveitar `DATA_INICIAL_MAIOR` e `DATA_INVALIDA` de `defesa/mensagens.py` e `SEM_ORIENTADOR` de `cadastro/mensagens.py`
- [X] T004 [P] [US-31][RBN-REL-01.1] (FR-018, FR-066, C3) Teste e implementação de `estrutura.py`: `Coluna`, `Celula(texto, url=None, numerica=False)`, `Linha` com `celulas(colunas)` sempre em `Celula`, `SubLista`, `Kpi`, `Grafico`, `Relatorio(colunas, linhas, totais=(), kpis=(), grafico=None, como_calculado=(), tem_registros=None, rotulo_linha="", id="", titulo="", frase="", gerado_em=None)`; `__post_init__` recusa `bool`, `date` e `None`, mais de 4 KPIs e sub-listas sem `rotulo_linha`; `tem_registros=None` deriva de `bool(linhas)`; `link_seguro(valor)` só com `https` e netloc (contrato §3)

### Registro e permissões

- [X] T005 [US-31][US-47][US-32][US-33][RBN-REL-01.2] (FR-002, FR-003, FR-004, C1) Teste e implementação de `registro.py`: decorador `@relatorio(id, nome, descricao, frase, perfis, filtros, ordem)` com `ImproperlyConfigured` para perfis vazios ou fora de `TIPOS_CONTA + PAPEIS`, `id` repetido ou fora de slug e filtro desconhecido; `relatorios_do_usuario`, `obter`, `pode_abrir` e `exigir_modulo` (research R13)
- [X] T006 [US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2][RBN-REL-02.3][RBN-REL-02.4] IC-07: `apps.py`, `ready()` importa os módulos de consulta, sem consulta ao banco nem ciclo (research R13)

### Filtros

- [X] T007 [P] [US-31][RBN-DEF-01.5] (FR-011, FR-012, SC-006) IC-03: em `sigtcc/apps/defesa/services_defesa.py`, extrair `intervalo_do_atalho(atalho, hoje)` e acrescentar `ano_semestre=None`, só por palavra-chave, a `filtro_de_periodo`; teste em `sigtcc/apps/defesa/tests/test_us40_lista_filtros_historico.py` (research R2)
- [X] T008 [US-31][US-47][RBN-DEF-01.5][RBN-CAD-14.1] (FR-010, FR-012 a FR-016, C2) Criar `tests/test_filtros_relatorios.py`: padrões renderizados no formulário; atalho que preenche as datas e troca de atalho; `atalho_anterior` ausente; datas invertidas com erro em `data_inicial`, sem resultado; datas invertidas seguidas de troca de atalho; data inexistente; só uma data; `atalho`, Ano/Semestre, Agrupar por e Abrangência forjados voltam ao padrão sem desligar a validação de datas; `?curso=²`, `?docente=²` e número com mais de 9 dígitos; datas prevalecem sobre Ano/Semestre; período atual sem turma na lista; `filtro()` proibido (research R3, R4)
- [X] T009 [US-31][US-47][RBN-DEF-01.5][RBN-CAD-14.1] (FR-010 a FR-016, C2) Implementar `forms.py`: `FiltroRelatorioForm(dados, usuario=..., registrado=...)` herda `FiltroPeriodoForm`, com normalização no `__init__`, `choices` montados no `__init__`, campos só os declarados, Curso e Docente só na gestão, oculto `atalho_anterior`, `clean` que move o erro para `data_inicial`; `Filtros` com `gestao`, `ano`, `semestre`, `inicio`, `fim`, `cur_id`, `doc_id`, `agrupar_por`, `abrangencia`, `periodo_q(prefixo)`, `resumo()` e `querystring()`; fora da gestão, `doc_id = usuario.pk` (research R3, R4, R14; contrato §2)

### Exportação e gráficos

- [ ] T010 [P] [US-31][RBN-REL-01.1] (FR-018 a FR-020, C4) Criar `tests/test_exportacao.py` com um `Relatorio` de exemplo: tipos, `attachment`, `no-store`, nome do arquivo; CSV com BOM, `;`, título, filtros, `gerado_em`, `totais`, bloco por sub-lista e coluna da linha-mãe; XLSX com abas, `totais`, tipo texto em toda `str`, `\x0b` removido, aba saneada e `int` numérico; PDF em paisagem, sem gráfico, sem `<a>`, com KPIs; sub-lista vazia com "Nenhum registro"; falha vira exceção tratada; `proteger()` com todos os prefixos (research R10)
- [ ] T011 [US-31][RBN-REL-01.1] (FR-018 a FR-020, C4) Implementar `exportacao.py` e `sigtcc/templates/relatorios/pdf/relatorio.html`, que estende `defesa/pdf/base_pdf.html`: `exportar(relatorio, filtros, formato)`, helper único de resposta, `proteger()`, log só com `id`, formato e `usu_id`; se a paisagem no bloco `corpo` não funcionar, parar e registrar como novo IC (research R10)
- [ ] T012 [P] [US-31][US-47][US-32][US-33] (FR-072 a FR-075) Teste e implementação de `graficos.py`: `barras`, `empilhado` e `linhas`, sem HTML, com números como `str` com ponto, barras da maior para a menor, curso com 0 Matriculados sem barra, resumo em texto (research R9)

### Layout e rotas

- [ ] T013 [P] [US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2][RBN-REL-02.3][RBN-REL-02.4] (FR-070, FR-071, FR-073, FR-076) IC-04: em `sigtcc/static/css/sigtcc.css`, trazer do protótipo `.kpis`, `.kpi`, `.rel-layout`, `.rel-menu a`, `.barras`, `.barra`; acrescentar `.tabela td.num` e `tfoot`, `.wrap:has(.rel-layout)` com 1200 px, sub-lista, destaque com negrito, empilhado, linhas, `@media print` e bloco do relatório com `max-height`, para o cabeçalho fixo; 360 px sem rolagem horizontal da página
- [ ] T014 [P] [US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2][RBN-REL-02.3][RBN-REL-02.4] (FR-070, FR-076) Criar `sigtcc/templates/relatorios/_filtros.html` (form GET com `autocomplete="off"`, "Aplicar" e "Limpar filtros"), `_tabela.html` (linha com botão `aria-expanded`, sub-listas, `tfoot`, `title` nos cabeçalhos, link com `target="_blank"` e `rel="noopener noreferrer"`), `_grafico_barras.html`, `_grafico_empilhado.html` e `_grafico_linhas.html`, sem regra, usando `Linha.celulas`
- [ ] T015 [US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2][RBN-REL-02.3][RBN-REL-02.4] (FR-002, FR-070, FR-071, FR-076) Criar `sigtcc/templates/relatorios/relatorios.html`, que estende `base.html`: lista por perfil com descrição, em forma de links; título e PDF, CSV e XLSX no canto superior direito, com `title` MR-02 quando desabilitados; frase; filtros; linha "Mostrando"; KPIs; gráfico; tabela; "Como é calculado"; "Gerado em DD/MM/AAAA às HH:MM"; estado vazio com a mensagem da US e a MR-01; MR-05 sem relatório escolhido; formulário inválido só com os erros
- [ ] T016 [P] [US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2][RBN-REL-02.3][RBN-REL-02.4] (FR-025, FR-076) Criar `sigtcc/static/js/relatorios.js`: recolher as sub-listas e alternar, e enviar o formulário só no `change` de select; carregar pelo bloco `scripts`; sem o script, tudo funciona
- [ ] T017 [US-31][US-47][US-32][US-33][RBN-REL-02.1] (FR-001, FR-004, FR-005, FR-018, FR-040) Implementar em `services_relatorios.py` `GRUPOS_DE_STATUS`, `STATUS_FINAIS` derivado dele (research R18) e `montar_relatorio(usuario, registrado, dados)`, devolvendo `(form, relatorio)`, e criar `views.py`, `urls.py` e `menu.py`: só `GET`; `perfil_requerido()` e `exigir_modulo`; ordem da exportação de `contracts/rotas.md`; sem registros, filtro inválido ou falha redireciona com `Filtros.querystring()`, com a MR-07 na falha; item "Relatórios" na seção "Gestão"
- [ ] T018 [US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2][RBN-REL-02.3][RBN-REL-02.4] IC-01 e IC-02: `sigtcc/urls.py` com `include("sigtcc.apps.relatorios.urls")`; MR-06 em `MENSAGENS_403` de `sigtcc/apps/cadastro/views.py`
- [ ] T019 [P] [US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2][RBN-REL-02.3][RBN-REL-02.4] IC-06 (opcional, depende da Q-153): em `sigtcc/apps/cadastro/contexto.py`, item do menu ativo em subcaminhos, sem mudar os demais
- [ ] T020 [US-31] (FR-001, FR-002, FR-004, FR-018, SC-004, SC-007) Teste em `tests/test_base_relatorios.py`: relatório de exemplo registrado no teste aparece na lista, abre, exporta e bloqueia perfil, sem alterar a base; exportação com filtro inválido ou sem registros não gera arquivo e redireciona ao relatório com os mesmos filtros; falha simulada nos 3 formatos redireciona com a MR-07

**Checkpoint**: um relatório de exemplo percorre tela e arquivos; a tela Defesas continua passando.

---

## Phase 3: User Story 1 - Painel de atividades por docente (Priority: P1) 🎯 MVP

**Goal**: extrato do Docente e visão de gestão, com filtros e exportação (US-31; RBN-REL-01.1).

**Independent Test**: como Docente, ver a própria linha e baixar os três arquivos; como Coordenador,
ver todos e filtrar; como Aluno, não ver o item.

### Tests for User Story 1

- [ ] T021 [P] [US1] [US-31][RBN-REL-01.1] Criar `tests/test_us31_atividades.py` com os cenários 1.1 a 1.11 e 1.14 e 1.15: uma linha para o Docente, gestão com todos, zeros, E3 com ninguém ativo, docente escolhido com zeros e de outro curso, sub-listas com "Nenhum registro", login e retorno, data invertida, Professor da Disciplina como Docente
- [ ] T022 [US1] [US-31][RBN-REL-01.1][RBN-CAD-14.1] (FR-022, FR-023, FR-024, FR-027) Em `tests/test_us31_atividades.py`: vínculo em vigor no intervalo; orientação e coorientação Ativas de TCC em Status final terminam na data do Status (R18); Aprovado e Aprovado com Correções continuam em vigor; intervalo que cruza a matrícula conta em TCC 1 e TCC 2, com Coorientações sem dobrar; troca de orientador conta os dois; aluno conta uma vez por coluna; período passado; coorientador externo fora; suplente acionado conta, com papel "Suplente"; não acionado e titular substituído fora; Inativos só com atividade; filtro Curso por Lotação sem cortar contagens; `ban_papel__in=PAPEIS_TITULARES` igual a `membros_efetivos`
- [ ] T023 [P] [US1] [US-31][RAN-REL-01] (FR-016, SC-004) Cenário 1.12 e matriz em `tests/test_permissoes_relatorios.py`: `?docente=<outro>&curso=<outro>&curso=todos` em tela e nos 3 formatos, com Docente puro, Professor, Orientador e Coorientador; cenário 1.13 com Aluno, Membro Externo e conta sem especialização na lista, tela e exportação, com a MR-06

### Implementation for User Story 1

- [ ] T024 [US1] [US-31][RBN-REL-01.1] (FR-021 a FR-027) Implementar `atividades_docente(usuario, filtros)` em `services_relatorios.py`, registrada com `periodo`, `ano_semestre`, `curso` e `docente`: três consultas, fim efetivo de R18 com `output_field`, colunas e sub-listas derivadas numa passagem, deduplicação por (TCC, papel), ordens de R7, nova conferência de `filtros.gestao`, sub-listas sem link, `rotulo_linha`, `tem_registros` próprio (research R7, R18)
- [ ] T025 [US1] [US-31] (FR-072, FR-076) KPIs do Docente e da Gestão, gráfico só com docentes com banca (sem gráfico se nenhum tiver), "Como é calculado" com a sobreposição de TCC 1 e TCC 2 e o efeito do Aprovado para TCC 2 (research R18), `definicao` das colunas
- [ ] T026 [US1] [US-31] (SC-001) Teste de N+1 em `tests/test_us31_atividades.py`, com `CaptureQueriesContext`, comparando 1 e 10 docentes (research R12)
- [ ] T027 [US1] [US-31][RBN-REL-01.1] IC-05: em `sigtcc/apps/cadastro/management/commands/popular_demo.py`, cenário dos relatórios para a US-31 (período passado, troca de orientador, TCC Concluído antigo, suplente acionado) e tabela do roteiro

**Checkpoint**: **base pronta para o Célio**. Avisar que a feat-11 pode partir da branch.

---

## Phase 4: User Story 2 - Produção de TCCs e Artigos (Priority: P1)

**Goal**: produção agrupada e lista de artigos (US-33; RBN-REL-02.1, 02.2).

**Independent Test**: conferir totais por agrupamento e abrangência e as colunas de Artigos.

### Tests for User Story 2

- [ ] T028 [P] [US2] [US-33][RBN-REL-02.1] Criar `tests/test_us33_producao.py` com os cenários 2.1 a 2.4 e 2.6 a 2.8: Total = Ativos + Com Sucesso + Sem Sucesso em toda linha; `GRUPOS_DE_STATUS` cobre os 10 valores uma vez; Sem Proposta fora; 10 áreas e "Não informada"; arquivo no agrupamento da tela (P3); teste cruzado com Formação
- [ ] T029 [P] [US2] [US-33][RBN-REL-02.2] Criar `tests/test_us33_artigos.py` com o cenário 2.5: colunas exatas; TCC sem linha em `Artigos`; MR-14; Orientador ativo, mais recente e "Sem orientador"; TCC que virou Monografia fora; link só `https`
- [ ] T030 [P] [US2] [US-33] (SC-004) Cenários 2.9 e 2.10 na matriz de `tests/test_permissoes_relatorios.py`

### Implementation for User Story 2

- [ ] T031 [US2] [US-33][RBN-REL-02.1][RBN-CAD-08.3][RBN-CAD-08.7] (FR-041) Subconsulta do Status por período em `services_relatorios.py`, para vínculo e para TCC (research R5, R16)
- [ ] T032 [US2] [US-33][RBN-REL-02.1] (FR-060 a FR-064) Implementar `producao_tccs(usuario, filtros)`, com base `TCCs`, agrupamentos, abrangência, linha Total, `tem_registros` próprio, KPIs, barras e "Como é calculado" (research R16)
- [ ] T033 [US2] [US-33][RBN-REL-02.2][RBN-CAD-12.1][RBN-CAD-12.3] (FR-065, FR-066) Implementar `artigos(usuario, filtros)`, com `select_related("artigos")`, Orientador por `Subquery`, `link_seguro`, 3 KPIs e sem gráfico (research R16)
- [ ] T034 [US2] [US-33] (SC-001) Teste de N+1 de Produção e Artigos e IC-05: trabalhos sem Área e artigos no `popular_demo`

**Checkpoint**: US-33 completa.

---

## Phase 5: User Story 3 - Formação e evasão (Priority: P1)

**Goal**: situação dos alunos por curso (US-32; RBN-REL-02.3).

**Independent Test**: conferir colunas e soma; período passado pelo histórico.

### Tests for User Story 3

- [ ] T035 [P] [US3] [US-32][RBN-REL-02.3] Criar `tests/test_us32_formacao.py` com os cenários 3.1 a 3.8: soma igual a Matriculados em toda linha e no Total; aprovado sem Versão Final em Ativos; período passado pelo histórico; Curso Todos com zeros
- [ ] T036 [US3] [US-32][RBN-CAD-05.4][RBN-CAD-05.6][RBN-CAD-08.7] (FR-041, FR-042, FR-043; SC-002, SC-003) Em `tests/test_us32_formacao.py`: cenário 3.10 (transferido), vínculo sem TCC como Sem Proposta, dois vínculos no período, excluído fora, Desistente com Proposta em Sem Sucesso (Q-02), último registro igual a `tcc_status`
- [ ] T037 [P] [US3] [US-32] (SC-004) Cenário 3.9 na matriz de `tests/test_permissoes_relatorios.py`, inclusive Secretaria

### Implementation for User Story 3

- [ ] T038 [US3] [US-32][RBN-REL-02.3] (FR-042, FR-043) Implementar `formacao_evasao(usuario, filtros)`, com base `AlunosTurmas`, linha Total, `tem_registros` próprio, KPIs, barra 100% e "Como é calculado", explicando por que os cartões não somam Matriculados
- [ ] T039 [US3] [US-32] (SC-001) Teste de N+1 e IC-05: aluno transferido, excluído e Aprovado para TCC 2 no `popular_demo`

**Checkpoint**: US-32 completa, sem o Histórico.

---

## Phase 6: User Story 4 - Histórico de indicadores do NUCOMP (Priority: P2)

**Goal**: série por período letivo (US-32 fluxo A; RBN-REL-02.4).

**Independent Test**: três períodos, em ordem, sem filtro de período.

### Tests for User Story 4

- [ ] T040 [P] [US4] [US-32][RBN-REL-02.4] Criar `tests/test_us32_historico.py` com os cenários 4.1 e 4.2: ordem; só filtro Curso; período sem turma do curso com zeros; sem período, E2; Alunos Vinculados igual a Matriculados; Defesas pela turma; Desistências pelo histórico; artigo copiado conta uma vez, no primeiro período com Publicado; link editado conta 2; Monografia fora

### Implementation for User Story 4

- [ ] T041 [US4] [US-32][RBN-REL-02.4] (FR-050 a FR-052) Implementar `historico_nucomp(usuario, filtros)`, com consultas por período, Artigos Publicados de R11, KPIs do último período, gráfico de linhas e "Como é calculado" (research R11, R9)
- [ ] T042 [US4] [US-32] (SC-001) Teste de N+1 e IC-05: artigo copiado e três períodos no `popular_demo`

**Checkpoint**: US-32 completa.

---

## Phase 7: User Story 5 - Participação de Membros Externos (Priority: P3)

**Goal**: pessoas distintas e instituições (US-47; RBN-REL-01.2).

**Independent Test**: cada pessoa conta uma vez; suplente não acionado fora.

### Tests for User Story 5

- [ ] T043 [P] [US5] [US-47][RBN-REL-01.2] Criar `tests/test_us47_membros_externos.py` com os cenários 5.1 a 5.9: pessoas distintas; suplente; cada grafia de instituição uma linha; ordem das instituições; Curso pela turma do TCC; Secretaria com Curso Vinculado e com Todos
- [ ] T044 [P] [US5] [US-47] (SC-004) Cenário 5.10 na matriz de `tests/test_permissoes_relatorios.py`

### Implementation for User Story 5

- [ ] T045 [US5] [US-47][RBN-REL-01.2][RBN-CAD-14.1] (FR-030, FR-031) Implementar `membros_externos(usuario, filtros)`, registrada com `periodo`, `ano_semestre` e `curso`, com KPIs, barras em `--roxo` e "Como é calculado" (research R17)
- [ ] T046 [US5] [US-47] (SC-001) Teste de N+1 e IC-05: Membros Externos de instituições diferentes no `popular_demo`

**Checkpoint**: 6 relatórios entregues.

---

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T047 [P] [US-31][US-47][US-32][US-33] (FR-018, SC-005) Criar `tests/test_igualdade_tela_arquivo.py`: 6 relatórios × 3 formatos, com dados hostis, comparando cabeçalhos, linhas, totais e sub-listas do HTML e de cada arquivo; CSV contra `proteger(valor)`; PDF por presença e ordem aproximada; link de 500 caracteres no PDF (research R15)
- [ ] T048 [P] [US-31][US-47][US-32][US-33] (FR-005, SC-004) Completar `tests/test_permissoes_relatorios.py`: 6 relatórios × (tela, 3 formatos, lista) × 10 perfis, com os 6 ids registrados; formato desconhecido e id desconhecido com 404; `POST` nas 3 rotas devolve 405; nenhuma consulta de escrita ao abrir e exportar (`CaptureQueriesContext`)
- [ ] T049 [P] [US-31][US-47][US-32][US-33] (constituição VI) Criar `tests/test_mensagens_relatorios.py`: textos exatos das US e MR, e nenhum texto novo fora de `mensagens.py`
- [ ] T050 [P] [US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2][RBN-REL-02.3][RBN-REL-02.4][RBN-CAD-14.1] (FR-015, FR-070 a FR-076) Teste em `tests/test_base_relatorios.py`: máximo de 4 KPIs e 1 gráfico por relatório; HTML com ponto em `width` e `points`; `<script>` escapado em `aria-label` e `title`; layout sem JavaScript; "Limpar filtros" é link sem query e volta ao padrão; os links da lista levam sem filtros, e os filtros voltam ao padrão ao abrir outro relatório; a página mantém os filtros no endereço
- [ ] T051 [US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2][RBN-REL-02.3][RBN-REL-02.4] (SC-001, SC-006, SC-009) Rodar a suíte completa (`manage.py test --noinput --parallel 4`), `makemigrations --check --dry-run` e `pre-commit run --all-files`; medir SC-001 com o `popular_demo`
- [ ] T052 [US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2][RBN-REL-02.3][RBN-REL-02.4] Roteiro manual do `quickstart.md`, com 4 perfis, arquivos conferidos, CSV em planilha real, 360, 768 e 1280 px, JavaScript desligado, checklist de Nielsen e teste de 5 segundos (SC-008). **Executado por pessoa**; registrar na seção 4 do quickstart
- [ ] T053 [US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2][RBN-REL-02.3][RBN-REL-02.4] Criar `pr-feat-10.md`, atualizar `CHANGELOG.md` e a "Situação no desenvolvimento" das US-31, 32, 33 e 47, e conferir `docs/questoes-a-rever.md`

---

## Dependencies & Execution Order

- **Setup (Fase 1)** → **Foundational (Fase 2)**, depois da ciência do Célio (Q-151) → **US1 (Fase 3)**.
- **T017** cria `GRUPOS_DE_STATUS` e `STATUS_FINAIS` (usados em T024); **T031** acrescenta a subconsulta do Status por período, de que **US3 e US4** dependem.
- **US5 (Fase 7)** depende só da Fase 2, mas fica por último (Could Have).
- **Polish (Fase 8)** depende dos 6 relatórios. T052 é manual.

## Parallel Example

```text
Fase 2: T003, T004, T007, T010, T012, T013, T014, T016
Fase 3: T021 e T023 (T022 depois de T021, no mesmo arquivo)
```

## Implementation Strategy

**MVP**: Fases 1 a 3, com o Painel e a base. Ao fim da Fase 3, avisar o Célio. Depois, na ordem US-33,
US-32, Histórico e US-47, cada fase com commit próprio.
