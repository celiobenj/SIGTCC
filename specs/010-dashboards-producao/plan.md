# Implementation Plan: Dashboards de Produção do SIGTCC

**Status**: Approved (Julia Cohen, 2026-11-06) — revisão do `arquiteto-django` incorporada e
reconferida (B-01 a B-04, I-01 a I-11, M-01 a M-15, N-01 a N-09)

**Branch**: `feature/feat-10-dashboards` | **Date**: 2026-11-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/010-dashboards-producao/spec.md`, aprovada por Julia
Cohen em 2026-11-05, depois da conferência do `analista-requisitos` (D-01 a D-15, pontos 1 a 16) e
do `/speckit-clarify`.

**Responsável**: Julia Cohen. **Revisor**: Célio Benjamim (consome a base na feat-11).

## Summary

Implementar no app `sigtcc/apps/relatorios` (Épico 3) a tela Relatórios e 6 relatórios somente
leitura: Painel de atividades por docente (US-31), Participação de Membros Externos (US-47),
Formação e evasão e Histórico de indicadores do NUCOMP (US-32), Produção de TCCs e Artigos (US-33).
Nenhuma tabela, coluna ou migração nova, e nenhuma dependência nova.

Abordagem: cada relatório é uma função de consulta que recebe o usuário e os filtros e devolve uma
estrutura única (`estrutura.Relatorio`). Essa estrutura alimenta a tela e os três arquivos, o que
garante tabela igual a arquivo. A base (registro, filtros, estrutura, exportação e layout) é o
contrato da feat-11 ([contracts/base-relatorios.md](contracts/base-relatorios.md)). O Status por
período sai do último registro do histórico do TCC, numa subconsulta só (research R5).

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Django 5.2.18, psycopg 3, `xhtml2pdf` 0.2.28 (por `defesa/pdf.py`),
`openpyxl` 3.1.5. Nenhuma dependência nova; nenhuma biblioteca JavaScript nova.

**Storage**: PostgreSQL 16, só leitura das tabelas da spec 001 ([data-model.md](data-model.md)).
Nenhum arquivo gravado: PDF, CSV e XLSX são gerados em memória, a cada download.

**Testing**: test runner do Django contra PostgreSQL (`--noinput --parallel 4`, sem `--keepdb`);
reaproveita `apoio_defesa.py` e acrescenta `apoio_relatorios.py`; `CaptureQueriesContext` comparando 1
e 10 itens para provar a ausência de consulta por linha; `pypdf` para o PDF; `openpyxl` e `csv` para ler
os arquivos; teste de igualdade tela × arquivo e matriz de permissões (R15).

**Target Platform**: servidor web Linux (Render) ou Windows local, fuso America/Manaus,
`USE_TZ=False`; telas de 360, 768 e 1280 px, seguindo a tela Relatórios do protótipo de 17/10 (só
o visual; a conversão de datas em semestres do protótipo não é regra, Clarifications).

**Project Type**: aplicação web monolítica com renderização no servidor (Django MVT).

**Performance Goals**: cada consulta em menos de 2 segundos (SC-001), com número de consultas
constante, sem depender do número de linhas (R12).

**Constraints**:
- nenhuma gravação em nenhuma rota; só `GET`;
- nenhuma regra nos templates: larguras, coordenadas e rótulos vêm prontos da estrutura;
- a tela Defesas, a agenda e a lista de ouvintes não mudam: `FiltroPeriodoForm` fica intacto, e
  `filtro_de_periodo` ganha um parâmetro opcional, com a extração de `intervalo_do_atalho`, sem mudança
  de resultado (R2);
- classificação de Status num lugar só (`GRUPOS_DE_STATUS`), usada pela US-32 e pela US-33;
- permissão conferida no servidor na tela e em cada exportação, por um único `montar_relatorio`; fora
  da gestão, `doc_id` é sempre o do usuário (R4);
- estrutura só com `int` e `str` formatada, para tela e arquivo não divergirem (contrato §3);
- mensagens idênticas às US, ou as MR provisórias (Q-146).

**Scale/Scope**: 5 histórias, 47 cenários (38 das US e 9 acrescentados), 46 FR, 6 relatórios, 3 rotas,
3 formatos, 3 parciais de gráfico, 7 itens de configuração. Volume esperado: centenas de alunos por
período e dezenas de docentes.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Verificação | Resultado |
|---|---|---|
| I. Especificação primeiro | Spec 010 aprovada em 2026-11-05, com Clarifications e sem `[NEEDS CLARIFICATION]`. | PASSA |
| II. Rastreabilidade | Todo FR com `[US-XX]` ou `[RBN-...]`; seção Rastreabilidade na spec; código e testes levarão as etiquetas. | PASSA |
| III. Modelo de dados oficial | Nenhuma tabela ou coluna nova; só leitura. `makemigrations --check` sem mudanças (SC-009). | PASSA |
| IV. Arquitetura | Tudo no app `relatorios`; consultas e cálculos em `services_relatorios.py`; views só orquestram; templates sem regra, com os dados de gráfico prontos. | PASSA |
| V. Qualidade | pre-commit (isort, black -l 100, flake8 100); comentários em português com etiquetas. | PASSA |
| VI. Testes de aceitação | Um teste por cenário das 5 histórias e mensagens exatas em `test_mensagens_relatorios.py`. | PASSA |
| VII. Segurança e LGPD | Perfil conferido no servidor (tela, lista e exportação); filtros forjados ignorados; nomes de arquivo sem nome de pessoa; proteção contra fórmula; link só `https`; nenhum arquivo gravado. | PASSA |
| VIII. Gerência de configuração | Branch `feature/feat-10-dashboards`; código de outras specs listado em "Itens de configuração". | PASSA |
| IX. Governança | Regras decididas sem fonte fechada estão na Q-152 (PO); contratos na Q-151 e itens de configuração na Q-153 (Célio). `registro.py`, `estrutura.py`, `exportacao.py` e `graficos.py` diferem do `services.py` de exportação citado no `CLAUDE.md`, com precedente em `defesa/pdf.py`; registrado na Q-153. | PASSA |

**Reavaliação depois do Phase 1**: nenhuma violação nova. O design não cria tabela, coluna nem
dependência.

## Project Structure

### Documentation (this feature)

```text
specs/010-dashboards-producao/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── base-relatorios.md   # contrato da feat-11
│   └── rotas.md
├── checklists/requirements.md
└── tasks.md                 # /speckit-tasks
```

### Source Code (repository root)

```text
sigtcc/apps/relatorios/
├── apps.py                  # ready() carrega as consultas registradas (IC-07)
├── menu.py                  # item "Relatórios" na seção Gestão (novo; lido pelo contexto.py)
├── urls.py                  # lista, relatório e exportação
├── views.py                 # só orquestram
├── registro.py              # registro dos relatórios e permissões por perfil
├── estrutura.py             # Relatorio, Coluna, Celula, Linha, SubLista, Kpi, Grafico
├── forms.py                 # FiltroRelatorioForm, herda FiltroPeriodoForm
├── services_relatorios.py   # uma função por relatório, montar_relatorio e GRUPOS_DE_STATUS
├── graficos.py              # larguras, ordenação, coordenadas do SVG e resumo em texto
├── exportacao.py            # PDF, CSV e XLSX a partir da estrutura
├── mensagens.py             # textos das US e MR-01 a MR-14
└── tests/
    ├── __init__.py
    ├── apoio_relatorios.py
    ├── test_base_relatorios.py
    ├── test_filtros_relatorios.py
    ├── test_exportacao.py
    ├── test_igualdade_tela_arquivo.py
    ├── test_us31_atividades.py
    ├── test_us33_producao.py
    ├── test_us33_artigos.py
    ├── test_us32_formacao.py
    ├── test_us32_historico.py
    ├── test_us47_membros_externos.py
    ├── test_permissoes_relatorios.py
    └── test_mensagens_relatorios.py

sigtcc/templates/relatorios/
├── relatorios.html          # layout único (lista + área do relatório); estende base.html
├── _filtros.html
├── _tabela.html             # linha expansível, sub-listas e total
├── _grafico_barras.html
├── _grafico_empilhado.html
├── _grafico_linhas.html     # SVG
└── pdf/
    └── relatorio.html       # estende defesa/pdf/base_pdf.html

sigtcc/static/js/relatorios.js   # opcional: expandir linha e enviar o filtro ao trocar um select
sigtcc/static/css/sigtcc.css     # estilos do protótipo que faltam (IC-04)
```

**Structure Decision**: a estrutura sugerida por Julia Cohen, mais `estrutura.py` e `graficos.py`.
`estrutura.py` evita que `registro.py`, `exportacao.py` e os relatórios da feat-11 dependam de
`services_relatorios.py`. `graficos.py` tira das consultas o cálculo de apresentação e dá aos
parciais números prontos, sem regra no template.

## Ordem de implementação e commits

1. **Base**: teste de viabilidade de R5 e R6 no PostgreSQL, com `EXPLAIN`; `estrutura`, `registro`, `GRUPOS_DE_STATUS`, `forms`, parâmetro em `filtro_de_periodo`, `exportacao`,
   layout, parciais, CSS, menu, rotas e permissões.
2. **US-31 completa**, com `popular_demo`. **Aqui a base fica pronta para o Célio.**
3. **US-33**: Produção de TCCs e Artigos, com a subconsulta do Status por período.
4. **US-32**: Formação e evasão.
5. **US-32 fluxo A**: Histórico.
6. **US-47**.
7. Polimento: checklist de Nielsen, SC-001, roteiro manual, documentos e PR.

## Itens de configuração (código de outras specs)

Aprovação de Célio Benjamim (índice Q-153). Todos só acrescentam, salvo a IC-03, que também extrai uma
função sem mudar o resultado.

| IC | Arquivo (spec de origem) | Mudança |
|---|---|---|
| IC-01 | `sigtcc/urls.py` (003) | + `include("sigtcc.apps.relatorios.urls")` |
| IC-02 | `cadastro/views.py` (003) | + MR-06 em `MENSAGENS_403` |
| IC-03 | `defesa/services_defesa.py` (007) | Extrai `intervalo_do_atalho`; `filtro_de_periodo` ganha `ano_semestre=None`, só por palavra-chave; sem o parâmetro, nada muda |
| IC-04 | `static/css/sigtcc.css` (003) | + `.kpis`, `.kpi`, `.rel-layout`, `.rel-menu a`, `.barras`, `.barra` do protótipo, `.tabela td.num` e `tfoot`, largura de 1200 px (`.wrap:has(.rel-layout)`), sub-lista, destaque, empilhado, linhas, `@media print` e bloco do relatório com `max-height`, para o cabeçalho fixo funcionar dentro de `.tabela-wrap` |
| IC-05 | `popular_demo.py` (005 a 009) | + cenário dos relatórios (período passado, transferido, artigo copiado, Membro Externo, suplente acionado, instituições) |
| IC-06 | `cadastro/contexto.py` (003) | Opcional: item do menu ativo em subcaminhos, para Relatórios ficar marcado em `/relatorios/<id>/` |
| IC-07 | `relatorios/apps.py` (001), `defesa/tests/test_us40_lista_filtros_historico.py` (007) | `ready()` carrega as consultas; + teste de `filtro_de_periodo` com `ano_semestre` |

`cadastro/menu.py` não muda: `cadastro/contexto.py` já lê o `menu.py` de cada app. `forms_defesa.py`
não muda: o formulário novo herda dele.

## Pendências desta feature

- Q-02 (PO): aluno que desiste sem Proposta. Se mudar, começa por FR-043.
- Q-146 (PO): textos MR-01 a MR-14.
- Q-151 (Célio): ciência dos contratos **antes** da fase base.
- Q-152 (PO): filtro Curso do Painel, papel "Suplente" e docentes da visão de gestão.
- Q-153 (Célio): IC-01 a IC-07.

## Complexity Tracking

Sem violações da constituição.
