# Tasks: Apoio Operacional do SIGTCC

**Input**: [spec.md](spec.md), [plan.md](plan.md) | **Status**: Approved (Célio Benjamim, 2026-11-10)

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Foundational

- [X] T001 Mensagens MR-15 a MR-18, "Como é calculado" e definições de coluna em
  `sigtcc/apps/relatorios/mensagens.py` [C10]
- [X] T002 Módulo `sigtcc/apps/relatorios/services_operacionais.py` com o recorte do Professor da
  Disciplina (`_turmas_do_recorte`) [C1][C2][FR-003]
- [X] T003 IC-01: importar `services_operacionais` em `RelatoriosConfig.ready()` [FR-001]

## Phase 2: US-48 Defesas realizadas no período (P1) 🎯

- [X] T010 [US1] Testes dos cenários 1 a 9 da US-48 e das decisões C1, C3 a C5 em
  `relatorios/tests/test_us48_defesas_realizadas.py`
- [X] T011 [US1] Consulta `defesas_realizadas` (id `defesas-realizadas`, ordem 70) [FR-010]

## Phase 3: US-49 Turmas e alunos (P2)

- [X] T020 [US2] Testes dos cenários 1 a 8 da US-49, do histórico (CAD-08.7) e de C7 em
  `relatorios/tests/test_us49_turmas_alunos.py`
- [X] T021 [US2] Consulta `turmas_alunos` (id `turmas-alunos`, ordem 80) [FR-020]

## Phase 4: US-34 Aluno e orientador (P2)

- [X] T030 [US3] Testes dos cenários 1 a 7 da US-34, do aluno já em TCC 2 e de C6 em
  `relatorios/tests/test_us34_aluno_orientador.py`
- [X] T031 [US3] Consulta `aluno_orientador` (id `aluno-orientador`, ordem 90) [FR-030]

## Phase 5: US-35 Horas complementares de ouvintes (P3)

- [X] T040 [US4] Testes dos cenários 1 a 9 da US-35 e de C8 em
  `relatorios/tests/test_us35_horas_ouvintes.py`
- [X] T041 [US4] Consulta `horas_ouvintes` (id `horas-ouvintes`, ordem 100) [FR-040]

## Phase 6: Polish

- [X] T050 IC-02: lista por perfil em `test_permissoes_relatorios.py`
- [X] T051 Suíte inteira, `pre-commit run --all-files`, `makemigrations --check`
- [X] T052 Conferência na demonstração (`sigtcc_validacao`): os 4 relatórios por perfil, tela e
  arquivos
- [X] T053 `pr-feat-11.md` no modelo do PGCS 6.3

## Dependencies & Execution Order

Phase 1 antes de tudo; as fases 2 a 5 são independentes entre si; a 6 fecha.
