# Implementation Plan: Apoio Operacional do SIGTCC

**Branch**: `feature/feat-11-apoio-operacional` | **Date**: 2026-11-10 |
**Spec**: [spec.md](spec.md) | **Status**: Approved (Célio Benjamim, 2026-11-10)

## Summary

Quatro relatórios somente leitura (RBN-REL-03.1 a 03.4) registrados no módulo Relatórios da spec
010 por decorador, num módulo novo `relatorios/services_operacionais.py`, carregado em
`RelatoriosConfig.ready()` (contrato §1, ponto de extensão já previsto). Nenhum modelo, migração,
rota, template de tela ou biblioteca nova.

## Technical Context

- Python 3.12, Django 5.2, PostgreSQL 16; xhtml2pdf e openpyxl (já presentes).
- Testes: `django.test`, sobre `relatorios/tests/apoio_relatorios.py` (spec 010).
- Desempenho: cada relatório em consultas fixas (sem consulta por linha): 03.1 com
  `prefetch_related` da banca; 03.2 com uma consulta de turmas e uma de vínculos anotados; 03.3 numa
  consulta com subconsultas; 03.4 na consulta da spec 009.

## Constitution Check

- Somente leitura, sem tabela nova: ✔ (FR-052, C9).
- Regras em `services`, views só orquestram: ✔ (usa as views da spec 010 sem mudança).
- Comentários em português com `[US-xx][RBN-xx]`: ✔.
- Cada cenário de aceite vira teste: ✔ (tasks T010 a T040).

## Project Structure

```
specs/011-apoio-operacional/{spec.md, plan.md, tasks.md, checklists/requirements.md, pr-feat-11.md}
sigtcc/apps/relatorios/
  services_operacionais.py   novo: 4 consultas com @relatorio (ordens 70, 80, 90 e 100)
  mensagens.py               + MR-15 a MR-18, "Como é calculado" e definições de coluna
  apps.py                    ready(): importa services_operacionais (IC-01)
  tests/test_us48_defesas_realizadas.py, test_us49_turmas_alunos.py,
        test_us34_aluno_orientador.py, test_us35_horas_ouvintes.py
  tests/test_permissoes_relatorios.py   lista por perfil passa a ter os 4 novos (IC-02)
sigtcc/apps/cadastro/management/commands/popular_demo.py  sem mudança (os dados de demonstração
  já têm turmas, sessões Realizadas e ouvintes)
```

## Decisões de implementação

- **Recorte (C1, C2)**: `filtros.gestao` (Coordenador ou Secretaria) decide; fora da gestão, o
  filtro é `tur_doc_id = usuario.pk` (a PK de Docentes é a de Usuarios), aplicado na consulta.
- **Período (03.1, 03.4)**: `filtros.periodo_q(prefixo)` da spec 010.
- **Status do vínculo (03.2, 03.3)**: `Coalesce(ultimo_status(hst_tcc__tcc_alu=..., hst_tcc__tcc_tur=...),
  "Sem Proposta")`, o mesmo de `formacao_evasao` (research R5 da spec 010).
- **Orientador (03.3)**: subconsulta de `Orientacoes` do TCC do aluno na turma, ativa primeiro.
- **Banca (03.1)**: `BancaDefesa` com `PAPEIS_TITULARES`, por `prefetch_related`, ordenada pelo
  papel; o Presidente vai para a coluna Orientador.
- **Ouvintes (03.4)**: `services_ouvintes.ouvintes_das_defesas(filtros.periodo_q(), cur_id)`, com o
  recorte do Professor por `pre_def__def_tcc__tcc_tur__tur_doc_id`.

## Itens de configuração (código de outras specs)

- IC-01: `relatorios/apps.py` (spec 010) — uma linha no `ready()`, prevista no contrato §1.
- IC-02: `relatorios/tests/test_permissoes_relatorios.py` (spec 010) — a lista esperada por perfil
  passa a incluir os 4 relatórios novos.

## Ordem de implementação e commits

1. `docs(feat-11): especificar o apoio operacional` — spec, plan, tasks, índice de questões.
2. `feat(feat-11): implementar os relatorios operacionais` — mensagens, consultas, IC-01, testes.

## Pendências desta feature

Nenhuma aberta: as decisões estão em Clarifications (C1 a C10, índice Q-157).
