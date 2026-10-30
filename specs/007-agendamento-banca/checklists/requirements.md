# Specification Quality Checklist: Agendamento e Banca do SIGTCC

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-30
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- Os nomes de tabela (`Defesas`, `BancaDefesa`, `HistoricoDefesas` etc.) e os serviços
  compartilhados reutilizados (`services.notificar`, `services_turmas.atualizar_status_tcc`,
  `services_orientacao.*`, `services_contas.filtro_de_curso`) não são detalhe de implementação
  nova: são o modelo de dados já existente (spec 001, Épico 2) e contratos já publicados pelas
  specs 002, 003, 005 e 006 que esta feature deve reutilizar, por instrução do pedido original
  ("não crie tabelas sem perguntar"; "reutilize os serviços já existentes"). Citá-los é
  rastreabilidade, não vazamento de arquitetura.
- A única decisão tomada sem o usuário presente foi registrada na seção Clarifications (stub de
  `descartar_avaliacoes`), por ser puramente de implementação temporária (assinatura já dada pelo
  usuário) e não uma regra de negócio em aberto; não há nenhum `[NEEDS CLARIFICATION]` pendente.
- Itens marcados completos foram conferidos por leitura integral das US-21, 22, 23, 24, 39 e 40 em
  `docs/fonte/Historias_de_Usuario_v3_4.md`, dos models e choices já existentes em
  `sigtcc/apps/defesa/` e dos contratos das specs 002, 003, 005 e 006.
- **Segunda rodada (2026-10-30, agente analista-requisitos)**: conferência linha a linha contra as
  5 US, a matriz de 17/10 e os contratos reais das specs 002, 004, 005 e 006. 2 achados
  bloqueantes corrigidos: filtro de Membros Externos na banca (incluía por engano só "Ativa", em
  vez de "Aguardando Ativação"/"Ativa"/"Expirada") e o ponto de chamada do stub
  `descartar_avaliacoes` (estava no reagendamento, deveria ser no cancelamento, na alteração da
  banca e no acionamento do suplente). Mais 6 pontos corrigidos: 2 cenários sem Acceptance Scenario
  movidos para Edge Cases com SC-005 ajustado (histórico pela tela do aluno/orientandos; transição
  para "Realizada"), 2 atribuições erradas de módulo corrigidas (`notificar`/
  `enviar_email_apos_commit` é contrato da spec 004, não da 003; `curso_id_do_usuario` está em
  `permissoes.py`), 1 serviço ausente acrescentado (`services_entregas.link_mais_recente`) e 1
  referência cruzada errada corrigida no FR-023. RBN, mensagens exatas, modelo de dados e os
  demais contratos reaproveitados foram confirmados sem divergência. Nenhuma mensagem nova foi
  criada nesta rodada — todas as correções foram de atribuição, escopo ou referência, não de
  texto exibido ao usuário.
- **Terceira rodada (2026-10-30, `/speckit-clarify`)**: 2 perguntas feitas e respondidas (quota
  máxima de 5 não atingida). A primeira (cancelamento automático da sessão no encerramento da
  participação) foi respondida como "esta spec implementa" (Opção A, novo FR-031) e depois
  **revertida na mesma sessão**: ao conferir `services_turmas.encerrar_participacao` (spec 004, já
  mesclada) para desenhar a integração, constatou-se que essa função **já recusa** o encerramento
  quando há sessão ativa (MT30, `STATUS_SESSAO_ATIVA`), com teste existente — o oposto do FR-031.
  Decisão final: manter o MT30, sem alteração em `services_turmas.py`; FR-031 removido, cenário 10
  da User Story 4 reescrito para refletir a recusa (não o cancelamento automático), e a pendência
  correspondente nunca chegou a ser registrada no índice (removida antes de sair do rascunho). A
  segunda pergunta (inserção do botão "Agendar defesa" nas telas já mescladas da turma e de
  orientandos) manteve a decisão "esta spec insere" (FR-006 atualizado, pendência Q-123). Também
  completado, fora do loop de perguntas porque a resposta já estava na matriz sem ambiguidade: o
  prazo de 2 segundos do filtro de Curso (RBN-CAD-14.1) ausente do FR-027. Todos os 16 itens deste
  checklist já estavam marcados antes desta rodada e continuam marcados — nenhuma regressão.
