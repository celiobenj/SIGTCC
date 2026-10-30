# Implementation Plan: Agendamento e Banca do SIGTCC

**Status**: Approved (Julia Cohen, 2026-10-30) — depois de 2 rodadas de revisão do
`arquiteto-django` (bloqueantes B1-B3 e importantes I1-I4 confirmados fechados na segunda rodada,
sem resíduo).

**Branch**: `feature/feat-07-agendamento` | **Date**: 2026-10-30 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/007-agendamento-banca/spec.md` (aprovada por Julia
Cohen em 2026-10-30, depois da conferência do `analista-requisitos` e de 2 perguntas do
`/speckit-clarify`, uma delas revertida na própria sessão ao encontrar um conflito com código já
mesclado — ver Clarifications)

**Responsável pelas US de origem**: Célio Benjamim (US-21, 22, 23, 24, 40); Maria Luísa Gomes
(US-39, mecanismo geral).

**Prazo crítico**: a fase base (serviços `agendar_sessao`, `membros_efetivos`, `registrar_evento`,
`transicionar_status`, `TRANSICOES_VALIDAS` e `popular_demo`) precisa estar pronta até **03/11**,
porque a feature futura "Avaliação e Resultados" (feat-08, Célio Benjamim) depende dela. O
`tasks.md` organiza as fases para que esse bloco saia primeiro (ver "Project Structure" e a nota em
"Pendências desta feature").

## Summary

Implementar no novo app `sigtcc/apps/defesa` (Épico 2 — Gestão da Defesa) o agendamento da sessão
de defesa (US-21), a composição e a alteração da banca examinadora (US-23), a validação de
conflito de horário (US-22), a confirmação com notificações, o reagendamento, o cancelamento e as
transições automáticas de status (US-24), e a lista de sessões com filtros de período, status e
curso, mais o histórico auditável (US-40, com a aplicação do filtro de Curso da US-39). Tudo sobre
o modelo de dados já existente (spec 001, Épico 2: `Defesas`, `DefesasPresenciais`,
`DefesasRemotas`, `BancaDefesa`, `HistoricoDefesas`) — **nenhuma tabela ou coluna nova**.

Abordagem: um módulo de regras por app (`services_defesa.py`), permissões em `permissoes_defesa.py`
(mesmo padrão de `permissoes.py` do app `cadastro`), views finas em `views_defesa.py`, rotas
próprias (`sigtcc/apps/defesa/urls.py`, `app_name = "defesa"`, incluído em `sigtcc/urls.py`).
Reaproveita, sem duplicar: `services.notificar`/`enviar_email_apos_commit` (spec 004, extensão da
spec 006), `services_entregas.link_mais_recente` (spec 005), `services_turmas.atualizar_status_tcc`
— só leitura do Status "Apto para Defesa", nunca gravação — `services_orientacao.orientador_atual`,
`coorientadores_ativos`, `e_orientador_atual`, `e_coorientador_ativo` e
`cancelar_troca_no_agendamento` (spec 006), e `services_contas.membros_externos_disponiveis` e
`filtro_de_curso` (spec 002). Consome um stub de `services_avaliacoes.descartar_avaliacoes`, que a
feat-08 ainda não entregou.

Toca código já mesclado em dois pontos pequenos (registrados como pendência de aprovação, índice
Q-123): o item "Defesas" no menu lateral (`cadastro/menu.py`) e o botão "Agendar defesa" nas telas
já existentes da turma (`_abas_professor.html`, nova aba "Defesas") e de orientandos
(`orientacao/orientacoes.html`, um link por orientando elegível). Uma terceira integração
considerada (cancelar a sessão automaticamente ao encerrar a participação do aluno) foi **revertida
no `/speckit-clarify`**: `services_turmas.encerrar_participacao` (spec 004, já mesclada) já recusa
esse encerramento com sessão ativa (MT30); esta spec não toca esse arquivo.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Django 5.2, psycopg 3, python-dotenv (já no `requirements.txt`). Nenhuma
dependência nova — esta feature não lê arquivos, não gera PDF e não chama serviço externo além do
e-mail que já existe.

**Storage**: PostgreSQL 16, com as tabelas já existentes do Épico 2 (spec 001):
`Defesas`, `Defesas_Presenciais`, `Defesas_Remotas`, `Banca_Defesa`, `Historico_Defesas`. Lê, sem
alterar o esquema: `TCCs` (Status), `Entregas_Marcos`/`Historico_Envios_Entregas` (link do
Documento para Defesa), `Orientacoes`/`Coorientacoes` (banca), `Solicitacoes_Orientacao` (troca
pendente), `MembrosExternos`, `Cursos`. Nenhuma migração de esquema nem de dados
([data-model.md](data-model.md)).

**Testing**: test runner do Django contra PostgreSQL. Reaproveita `tests/apoio_acesso.py`,
`apoio_turmas.py`, `apoio_tcc.py` e `apoio_orientacao.py` (specs 003 a 006) para montar turma,
aluno, TCC "Apto para Defesa" e orientação; acrescenta `sigtcc/apps/defesa/tests/apoio_defesa.py`
(fábricas de sessão, banca e histórico). `captureOnCommitCallbacks(execute=True)` para os e-mails.
O cálculo da janela de 1 hora e o início automático são testados com o relógio controlado (mesmo
padrão de `avancar_relogio`/`timezone.now` mockado já usado nas specs 004 e 005).

**Target Platform**: servidor web Linux ou Windows (fuso America/Manaus); navegadores atuais, de
360 px para cima (spec 003, Q22). Segue o protótipo de 17/10: layout, paleta, fontes Roboto/Figtree
e ícones Material Symbols; telas "Defesas", "Agendar sessão de defesa", "Sessão de defesa",
"Alterar banca", "Acionar suplente", "Reagendar sessão de defesa", "Cancelar sessão" e "Histórico
da defesa" só como referência visual — a lógica em JavaScript do protótipo não é reaproveitada.

**Project Type**: aplicação web monolítica com renderização no servidor (Django MVT).

**Performance Goals**: SC-001 (agendar em menos de 5 minutos) é meta de roteiro manual
([quickstart.md](quickstart.md)). FR-027 (filtro de Curso) MUST atualizar a tabela em até 2
segundos (RBN-CAD-14.1) — a lista de Defesas usa `select_related`/`prefetch_related`, sem consulta
por linha (research C6).

**Constraints**:
- nenhuma tabela ou coluna nova;
- mensagens idênticas às US-21, 22, 23, 24, 39 e 40, ou provisórias em
  `docs/questoes-a-rever.md`;
- `def_status` só é gravado por `agendar_sessao` (criação, sempre "Agendada") ou por
  `transicionar_status` (transição de uma sessão já existente, validada contra
  `TRANSICOES_VALIDAS`) — nunca por atribuição direta (FR-017, FR-023; research C2);
- conflito de horário (FR-014 a FR-016) sempre antes de gravar sessão, banca ou alteração;
- trava, antes de conferir conflito, os **usuários propostos para a banca** (`_travar_membros`,
  `select_for_update()` ordenado por pk) — não as sessões, porque numa criação não há sessão
  existente para travar (research C3, achado B2/B3); ordem geral: turma(s do TCC) → aluno → TCC →
  membros propostos → sessão (se já existir) → banca, com tudo reconferido depois de travar (research
  C3, reaplicando o padrão das specs 004/005/006);
- e-mails só depois do commit (`transaction.on_commit`, via `enviar_email_apos_commit`);
  notificações no sistema na mesma transação (linhas do banco);
- **`services_turmas.encerrar_participacao` não é alterado** — o MT30 (sessão ativa bloqueia o
  encerramento) continua como está (Clarifications; decisão revertida).

**Scale/Scope**: 5 US (46 cenários de aceite), 30 FR (FR-001 a FR-030), cerca de 10 telas/janelas e
14 rotas novas, mais 2 pontos de integração pequenos em telas já mescladas (menu, aba da turma,
tela de orientandos).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Verificação | Resultado |
|---|---|---|
| I. Especificação primeiro | Spec 007 aprovada por Julia Cohen em 2026-10-30, sem marcadores `[NEEDS CLARIFICATION]` (2 perguntas resolvidas no `/speckit-clarify`, uma revertida na mesma sessão). | PASSA |
| II. Rastreabilidade | Todo FR traz `[RBN-DEF-XX]` ou `[RBN-CAD-14.1]`; services, views, forms, templates e testes levam `[US-XX][RBN-...]`. | PASSA |
| III. Modelo de dados oficial | Nenhuma tabela ou coluna nova ([data-model.md](data-model.md)); `Defesas`, `Defesas_Presenciais`, `Defesas_Remotas`, `Banca_Defesa`, `Historico_Defesas` já existem com os campos do dicionário (confirmado em `models.py`/`choices.py` do app `defesa`, spec 001). | PASSA |
| IV. Arquitetura | Tudo em `sigtcc/apps/defesa` (app novo do Épico 2); regras em `services_defesa.py`, permissões em `permissoes_defesa.py`, views só orquestram, templates sem regra; templates em `sigtcc/templates/defesa/`, static reaproveitado. Um único módulo de serviço (não dois, como nas specs 004/005/006) porque esta feature tem um domínio de dados central (a sessão) — ver Complexity Tracking. | PASSA |
| V. Qualidade | `pre-commit`/`isort`, `black -l 100`, `flake8 --max-line-length 100`; comentários em português. | PASSA |
| VI. Testes de aceitação | Um teste por cenário das 5 US (46), mais permissões (por curso e por perfil), mensagens exatas, conflito de horário sob corrida, e a transição automática Agendada/Reagendada → Em Andamento. | PASSA |
| VII. Segurança e LGPD | Acesso à sessão restrito à banca e ao Professor da Disciplina (FR-030); visibilidade da lista por perfil (FR-024); link de videochamada só `https://`; nenhum arquivo hospedado; agendamento, reagendamento, cancelamento, alteração de banca e acionamento de suplente com autor, data e hora (`Historico_Defesas`). | PASSA |
| VIII. Gerência de configuração | Branch `feature/feat-07-agendamento`; commits atômicos por fase, fase base primeiro (prazo 03/11). Dois pontos tocam código já mesclado (menu, aba da turma, tela de orientandos), registrados como Q-123, pendentes de aprovação de Célio Benjamim (config). | PASSA (pendência não bloqueante) |
| IX. Governança | Mensagens aguardam validação da PO como as demais specs; a integração do botão em telas mescladas aguarda aprovação de configuração (Q-123). | PASSA (pendências não bloqueantes) |

**Reavaliação depois do Phase 1**: nenhuma violação nova. O design não cria tabela, coluna nem
dependência; o único ponto de atenção (cancelamento automático por encerramento de participação)
foi descartado antes do Phase 1, exatamente para não introduzir uma mudança em código já mesclado
sem necessidade.

## Project Structure

### Documentation (this feature)

```text
specs/007-agendamento-banca/
├── spec.md                          # aprovada em 2026-10-30
├── plan.md                          # este arquivo
├── research.md                      # Phase 0 (C1 a C8)
├── data-model.md                    # Phase 1 (nenhuma tabela nova)
├── quickstart.md                    # Phase 1
├── contracts/
│   ├── rotas.md                     # telas e rotas novas
│   └── servicos-defesa.md           # o que a feat-08 e a feat-09 podem chamar
├── checklists/requirements.md       # já validado (16/16)
└── tasks.md                         # Phase 2 (/speckit-tasks) — fase base primeiro (prazo 03/11)
```

### Source Code (repository root)

```text
sigtcc/urls.py                        # + include("sigtcc.apps.defesa.urls")
sigtcc/apps/cadastro/
├── menu.py                           # + item "Defesas" (IC; índice Q-123)
└── templates .. (ver abaixo)
sigtcc/apps/defesa/
├── services_defesa.py                # novo: C1 a C7 — agendar_sessao (criação), conflito
│                                      #   (_travar_membros, _verificar_conflito), _compor_banca,
│                                      #   transicionar_status, registrar_evento, histórico,
│                                      #   lista/filtros, membros_efetivos
├── permissoes_defesa.py              # novo: quem agenda/reagenda/cancela/altera banca/vê a sessão
├── forms_defesa.py                   # novo: AgendarForm, BancaForm, ReagendarForm, CancelarForm,
│                                      #   AlterarBancaForm, AcionarSuplenteForm
├── views_defesa.py                   # novo: todas as views desta spec
├── urls.py                           # novo: app_name = "defesa" (contracts/rotas.md)
├── mensagens.py                      # novo: textos das US-21, 22, 23, 24, 39 e 40
└── tests/
    ├── apoio_defesa.py               # novo: fábricas de sessão, banca e histórico
    ├── test_us21_agendar.py
    ├── test_us22_conflito.py
    ├── test_us23_banca.py
    ├── test_us24_confirmar_reagendar_cancelar.py
    ├── test_us40_lista_filtros_historico.py
    ├── test_permissoes_defesa.py
    ├── test_mensagens_defesa.py
    └── test_base_defesa.py           # fase base: agendar_sessao, transicionar_status,
                                       #   registrar_evento, _travar_membros, membros_efetivos,
                                       #   TRANSICOES_VALIDAS, popular_demo
sigtcc/templates/defesa/
├── defesas.html                      # lista (US-40) + filtros + botão "Agendar defesa"
├── turma_defesas.html                # aba "Defesas" da turma (FR-006), lista filtrada pela turma
├── form_agendar.html                 # Agendar sessão de defesa (US-21 + seção Banca, US-23)
├── sessao.html                       # janela "Sessão de defesa" (contrato §4: blocos reservados
│                                      #   para a feat-08/feat-09)
├── form_alterar_banca.html           # US-23, fluxo C
├── form_acionar_suplente.html        # US-23, fluxo D
├── form_reagendar.html               # US-24, fluxo B
├── confirmar_cancelar.html           # US-24, fluxo C
└── historico.html                    # "Histórico da defesa" (US-40)
sigtcc/apps/cadastro/
├── management/commands/popular_demo.py   # + TCCs Aptos e 1 sessão por StatusSessao (contrato)
└── templates/cadastro/
    ├── tcc/_abas_professor.html      # IC: + aba "Defesas" (índice Q-123)
    └── orientacao/orientacoes.html   # IC: + link "Agendar defesa" por orientando elegível
                                       #   (índice Q-123)
```

**Structure Decision**: app novo `sigtcc/apps/defesa` (Épico 2, "Gestão da Defesa"), estrutura
igual à do app `cadastro` (PGCS 2.3): `models.py`/`choices.py`/`cargas.py` já existem da spec 001;
esta spec acrescenta `services_defesa.py`, `permissoes_defesa.py`, `forms_defesa.py`,
`views_defesa.py`, `urls.py` e `mensagens.py` próprios do app, e templates em
`sigtcc/templates/defesa/`. Um módulo de serviço só (não dividido por domínio, como nas specs
004/005/006) porque todas as regras desta spec giram em torno de uma única entidade central (a
sessão de defesa) — ver Complexity Tracking.

## Itens de configuração (código de outras specs)

Cada item é um acréscimo pequeno em arquivo já mesclado na `develop`. Registrados no índice para
aprovação de Célio Benjamim (configuração).

| IC | Arquivo(s) e spec de origem | O que muda | Por quê | Testes da spec de origem | Índice |
|---|---|---|---|---|---|
| IC-01 | `sigtcc/urls.py` (003) | `+ path("", include("sigtcc.apps.defesa.urls"))`. Nada removido. | Rotas novas do app `defesa` | só acréscimo | Q-123 |
| IC-02 | `cadastro/menu.py` (003; itens de 002, 004, 005, 006) | `+` item "Defesas" (`gavel` ou ícone equivalente do protótipo, rota `defesa:defesas`, perfis `aluno`, `docente`, `secretaria`; ordem logo depois de "Orientações"). Itens existentes inalterados. | FR-024; protótipo de 17/10 | `test_base_comum.py` (menu) conferido; só acréscimo | Q-123 |
| IC-03 | `cadastro/templates/cadastro/tcc/_abas_professor.html` (005; usado por `turma.html` da 004 e `entregas.html` da 005) | `+` aba "Defesas" (`defesa:turma_defesas`, `turma.pk`), visível quando `e_professor` (mesma condição já usada para "Entregas"). Abas existentes inalteradas. | FR-006 | `test_navegacao_tcc.py` (abas) conferido; só acréscimo | Q-123 |
| IC-04 | `cadastro/templates/cadastro/orientacao/orientacoes.html` (006) | `+` link "Agendar defesa" na linha de cada orientando com TCC "Apto para Defesa" sem sessão ativa (`defesa:agendar?tcc=<id>`). Linhas sem essa condição não mudam. | FR-006 | `test_us18_resposta_orientandos.py` conferido; só acréscimo | Q-123 |
| IC-05 | `cadastro/management/commands/popular_demo.py` (005 ou 006, o que já existir) | `+` TCCs "Apto para Defesa" (um por curso) e uma sessão em cada um dos 5 valores de `StatusSessao`, usando `services_defesa` (nunca criando `Defesas` direto). | Contrato desta spec, §4 (feat-08/feat-09) | comando idempotente; sem teste de aceite próprio, só smoke test | — |

Nenhum IC altera comportamento ou teste de outra feature — são só acréscimos independentes
(inclusão de rota, item de menu, aba e link).

## Pendências desta feature

Índice central: [docs/questoes-a-rever.md](../../docs/questoes-a-rever.md).

| Pendência | Destino | Índice |
|---|---|---|
| Aprovar os IC-01 a IC-05 (código de specs já mescladas) | Célio Benjamim (config) | Q-123 |
| Validar os textos exatos das mensagens desta spec (se algum não tiver aspas na US, vira provisório no `tasks.md`, mesmo padrão das specs 004 a 006) | Profa. Diana (PO) | a abrir no `tasks.md`, se houver |
| Entregar `services_avaliacoes.descartar_avaliacoes(sessao, membro=None)` real, substituindo o stub desta spec | Célio Benjamim (feat-08) | Clarifications |
| **Fase base pronta até 03/11** (`agendar_sessao`, `membros_efetivos`, `registrar_evento`, `transicionar_status`, `TRANSICOES_VALIDAS`, `popular_demo`) para a feat-08 depender dela | Julia Cohen → Célio Benjamim | prazo crítico (ver Summary) |
| Nome/ícone definitivo do item de menu "Defesas" (segue o protótipo de 17/10 por padrão) | Profa. Diana ou Célio Benjamim | a confirmar na implementação |

## Complexity Tracking

Nenhuma violação da constituição sem justificativa.

| Escolha | Por quê | Alternativa mais simples rejeitada |
|---|---|---|
| Um único módulo `services_defesa.py` (em vez de dividir por domínio, como nas specs 004/005/006) | Todas as regras desta spec (agendar, conflito, banca, status, histórico, lista) giram em torno de uma única entidade central (`Defesas`); dividir criaria acoplamento circular entre os módulos sem reduzir a revisão | Separar `services_banca.py`: a validação de conflito (US-22) depende dos dados da banca e do agendamento ao mesmo tempo, forçando imports cruzados |
| App novo `sigtcc/apps/defesa` em vez de estender `cadastro` | O Épico 2 (Gestão da Defesa) já tem app próprio desde a spec 001 (models, choices, cargas); manter a estrutura do PGCS 2.3 | Colocar tudo em `cadastro`: misturaria dois épicos no mesmo app, contra a estrutura obrigatória do PGCS |
| Reverter o cancelamento automático da sessão no encerramento da participação (Clarifications) | `services_turmas.encerrar_participacao` (spec 004) já bloqueia esse encerramento com o MT30; as duas regras não podiam coexistir, e alterar código já mesclado e testado de outra feature sem necessidade real violaria o princípio de menor mudança | Remover o MT30 e implementar o cancelamento automático: quebraria o teste já existente e mudaria comportamento aceito da spec 004 sem motivo pedido pelas US desta spec |
