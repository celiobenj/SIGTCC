# Specification Quality Checklist: Fluxo do TCC e Entregas

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-22
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

- Os nomes de tabela (`TCCs`, `Turmas_Marcos`, `Entregas_Marcos` etc.) e dos serviços
  compartilhados reutilizados (`participacao_encerrada`, `travar_turma_ativa`,
  `criar_entregas_do_aluno`) não são detalhe de implementação nova: são o modelo de dados já
  existente (spec 001) e contratos já publicados pelas specs 003 e 004 que esta feature é
  obrigada a reutilizar, por instrução do projeto ("não crie tabelas"; reaproveitar os serviços
  compartilhados). Citá-los é rastreabilidade, não vazamento de arquitetura.
- Um ponto foi registrado na seção "Clarifications" do spec.md (nome da aba "Atividades" x
  "Entregas" na US-43) em vez de usar marcador `[NEEDS CLARIFICATION]`, porque é uma divergência
  textual entre a própria US-43 e as demais US da mesma feature, não uma lacuna de requisito; a
  decisão provisória documentada não bloqueia o `/speckit-plan`, mas bloqueia a implementação da
  tela até a confirmação da Profa. Diana ou de Leandra Matos. Será registrada em
  `docs/questoes-a-rever.md` com o próximo índice.
- Itens marcados completos foram conferidos por leitura integral das US-13, 14, 15, 16, 29, 43 e
  44 em `docs/fonte/Historias_de_Usuario_v3_3.md` e das tabelas correspondentes em
  `docs/fonte/Modelo_Logico_e_Dicionario_18_10.md` (seções 3.4 e 3.5).
- **Segunda rodada (2026-10-22, agente analista-requisitos)**: conferência linha a linha contra as
  7 US, a matriz de 17/10 e o modelo lógico. Achados corrigidos nesta versão: duas mensagens
  provisórias ausentes (MF-01, MF-02, seção "Mensagens a validar com a PO"), dois cenários novos
  de cobertura na User Story 2 (gravação de Status para gatilhos disparados pela spec 006), tag
  `[RBN-CAD-XX]` em cada Functional Requirement, correção da referência ambígua a "spec 006/005"
  nas Assumptions, e nova pendência Q-45 (nome do link de histórico, US-14) em
  `docs/questoes-a-rever.md`. Nenhuma tabela, campo ou parâmetro de serviço inventado foi
  encontrado nessa rodada.
- **Terceira rodada (2026-10-22, `/speckit-clarify`)**: 3 perguntas feitas e respondidas (quota
  máxima de 5 não atingida) — Palavra-Chave repetida (FR-007, novo cenário 7 da User Story 1 e
  mensagem MF-03), acesso da Secretaria ao histórico do Status do TCC (FR-009, mantido restrito) e
  visibilidade do Coorientador (fica a cargo da spec 006). Também corrigido, fora do loop de
  perguntas porque não era ambíguo e sim um erro factual contra a RBN-DEF-06.3: o cenário 9 da
  User Story 2 citava "nota final 7,0" como limite de "Aprovado para TCC 2", corrigido para "6,0
  ou mais". E completada, pela mesma razão (resposta já definida sem ambiguidade na matriz, RAN-
  CAD-07, NFR de Confidencialidade), a visibilidade do Resumo da Proposta (novo FR-007a). Todos os
  16 itens deste checklist já estavam marcados antes desta rodada e continuam marcados — nenhuma
  regressão; a rodada elevou a qualidade sem mudar o resultado do checklist (16/16 → 16/16).
