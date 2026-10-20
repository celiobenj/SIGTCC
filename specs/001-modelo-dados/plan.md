# Implementation Plan: Modelo de dados do SIGTCC

**Branch**: `feature/feat-01-modelo-de-dados` (pendente de confirmação do Célio; o PGCS 4.3 lista `feat-01` como `feature/feat-01-usuarios`) | **Date**: 2026-10-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-modelo-dados/spec.md`

**Responsável**: Julia Cohen (implementação e aprovação); Maria Luiza Guimarães consultada sobre
mudanças no dicionário de dados.

## Summary

Criar o projeto Django do SIGTCC na estrutura do PGCS e implementar no PostgreSQL as 36 tabelas do
dicionário de 18/10, com nomes, tipos, tamanhos, nulidade, chaves (simples, compostas e
estrangeiras), unicidades e CHECKs iguais ao documento, mais a carga inicial de Cursos,
Areas_Interesse e Criterios (descritores provisórios). `Equivalencia_Cursos` nasce vazia.

Abordagem: modelos Django com `db_table`/`db_column` explícitos, distribuídos entre `cadastro`
(27 tabelas) e `defesa` (9); `Usuarios` como `AUTH_USER_MODEL` sem colunas extras; domínios em
`TextChoices` que geram os `CheckConstraint`; campos próprios para `CHAR(10)` e `TIMESTAMP`;
chaves compostas com `CompositePrimaryKey` e a FK composta de `Avaliacoes` por `RunSQL` numa
migração própria; uma data migration por domínio fixo; e um teste que compara o banco com o
próprio arquivo do dicionário.

**Revisão de 2026-10-19**: o agente `arquiteto-django` revisou este plano e o data-model contra o
dicionário e o PGCS. Os achados B1, I1–I4 e M1–M9 foram aplicados com aprovação de Julia Cohen;
o principal (B1) é o `TimestampField` (research R1).

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Django 5.2 LTS, psycopg 3 (`psycopg[binary]`), python-dotenv; black,
isort e flake8 (linha de 100). Versões exatas fixadas no `requirements.txt` na configuração
(research R12).

**Storage**: PostgreSQL 16. `TimestampField` (coluna `timestamp` sem fuso) com `USE_TZ = False`
e `TIME_ZONE = "America/Manaus"` (R1);
`DEFAULT_AUTO_FIELD = "django.db.models.AutoField"` (D4). Cache `FileBasedCache` em `CACHE_DIR`
do `.env` (D2).

**Testing**: test runner do Django (`manage.py test`) contra PostgreSQL 16; testes em
`sigtcc/apps/<app>/tests/`.

**Target Platform**: servidor web Linux ou Windows; desenvolvimento em Windows com `venv` (PGCS 3.1).

**Project Type**: aplicação web monolítica com renderização no servidor (Django MVT). Esta feature
só entrega a camada de modelo.

**Performance Goals**: base completa com carga inicial criada em menos de 1 minuto (SC-003).

**Constraints**: nenhuma tabela ou coluna de negócio fora do dicionário (FR-002, FR-020); nenhuma
regra de aplicação nesta feature (FR-019); segredos só no `.env`.

**Scale/Scope**: 36 tabelas, 201 colunas, 26 domínios (`TextChoices`), 50 restrições nomeadas,
1 migração de SQL (FK composta), 2 migrações de restrições e 3 data migrations; escala do NUCOMP
(centenas de alunos por semestre, 3 cursos).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Verificação | Resultado |
|---|---|---|
| I. Especificação primeiro | spec.md, plan.md e tasks.md aprovados por Julia Cohen em 2026-10-19 (o plan e o tasks depois do `/speckit-analyze`, achado C2). | PASSA |
| II. Rastreabilidade | Cada modelo terá docstring com [US-XX][RBN-...]; data migrations citam FR e RBN; testes citam o cenário da spec. | PASSA |
| III. Modelo de dados oficial | 36 tabelas e 201 colunas conferidas contra o dicionário (data-model.md, conferência automatizada); sem Salas; `Usuarios` sem colunas extras (D1); `CHAR(10)` por `CharFixoField` (R4) e `TIMESTAMP` por `TimestampField` nas 21 colunas (R1). Desvio: identidade BY DEFAULT (D4). | PASSA COM DESVIO JUSTIFICADO (ver Complexity Tracking) |
| IV. Arquitetura | Modelos em `sigtcc/apps/cadastro` e `sigtcc/apps/defesa`; `relatorios` sem modelos; nenhuma regra em views/templates. | PASSA |
| V. Qualidade | isort, black e flake8 (100) via `lint.bat`, com `pyproject.toml` e `.flake8` para as três ferramentas concordarem (R13); comentários em português. A correção do caminho do `lint.bat` (`apps/sigtcc/` → `sigtcc/`, R12) e os dois arquivos novos passam pelo Célio. | PASSA (configuração a aprovar no PR) |
| VI. Testes de aceitação | Cada cenário Dado/Quando/Então das US1–US3 da spec vira teste; conformidade lida do dicionário. | PASSA |
| VII. Segurança e LGPD | `.env` e `CACHE_DIR` no `.gitignore`; senha só como hash (`set_password`); nenhum dado pessoal na carga inicial. | PASSA |
| VIII. Gerência de configuração | Migrações no mesmo PR dos modelos; a FK composta em migração própria escrita à mão (não se perde se a `0001` for regenerada); branch `feature/feat-01-modelo-de-dados` (pendente de confirmação do Célio); PR para `develop` com template PGCS 6.3. | PASSA |
| IX. Governança | Itens de configuração para revisão do Célio Benjamim no PR: `requirements.txt`, `settings.py`, `.gitignore`, `.env.example`, `lint.bat` (caminho), `pyproject.toml`, `.flake8`, `CHANGELOG.md` e os módulos que não estão na árvore do PGCS 2.3 (`choices.py`, `fields.py`, `managers.py`, `cargas.py`, `tests/`). Desvio D4 e restrições descritas só em texto exigem consulta à Maria Luiza (autora do dicionário). | PASSA (revisões a obter no PR) |

**Re-check após a Fase 1 e após a revisão**: data-model.md e contracts/ não introduziram tabela,
coluna ou regra nova; o `TimestampField` corrige a única divergência de tipo encontrada (B1); o
único desvio continua sendo D4. As seções de transição de status do data-model são informativas e
citam a matriz. Resultado mantido.

## Aprovações (2026-10-19, Julia Cohen)

| Decisão | Situação |
|---|---|
| Spec 001 | Aprovada para tasks e implementação |
| plan.md (versão após `/speckit-analyze` de 2026-10-19) | Aprovado por Julia Cohen em 2026-10-19 |
| tasks.md (45 tarefas, versão após `/speckit-analyze` de 2026-10-19) | Aprovado por Julia Cohen em 2026-10-19 |
| R1 `USE_TZ = False`, fuso America/Manaus | Aprovada |
| R1 `TimestampField` nas 21 colunas `TIMESTAMP` (achado B1) | Aprovada |
| R13 `pyproject.toml` (black 100, isort `profile = "black"`) e `.flake8` (`extend-ignore = E203, W503`) (achado I3) | Aprovada; itens de configuração para revisão do Célio no PR |
| Achados I1, I2, I4 e M1–M9 da revisão do `arquiteto-django` | Aplicados |
| R3 `unique=True` em e-mails opcionais | Aprovada com condição: e-mail sem valor gravado como `NULL`, nunca `""`, com teste (spec US2 cenário 11; `save()` e `create_user` normalizam) |
| R4 `CharFixoField` | Aprovada |
| R5 testes de FK com verificação imediata | Aprovada |
| D1 `Usuarios` sem colunas extras | Aprovada, sem Admin e sem `createsuperuser` |
| D2 bloqueio no cache | Aprovada; nesta feature só a configuração do cache |

## Pendências para outras features e pessoas

| Pendência | Destino |
|---|---|
| Criar as contas iniciais de Coordenador de Curso de Engenharia de Computação, Sistemas de Informação e Licenciatura em Computação na implantação, por comando de gestão (`manage.py`), já que não há `createsuperuser` (RAN-CAD-01, RNF Portabilidade: Instalabilidade; primeiro acesso por RBN-CAD-06.2) | US-03 |
| Lógica de contagem de tentativas e mensagem de bloqueio (RBN-CAD-06.6) sobre o cache configurado aqui | US-11 |
| Backend de autenticação por matrícula ou e-mail | US-11 |
| Consultar Maria Luiza Guimarães e registrar no dicionário: (a) a identidade BY DEFAULT (D4); (b) as restrições que o dicionário só descreve em texto e que a spec aprovou como CHECK (FR-008, FR-010): matrícula com exatamente 10 dígitos (`alu_matricula`, `ouv_matricula`), `tur_ano` com 4 dígitos, `tur_semestre` 1 ou 2, faixas de 0,0 a 10,0 (`cri_peso`, `ava_nota`, `def_nota_final`) e domínios de `hst_status_anterior`/`hst_status_novo` e `hdf_status_anterior`/`hdf_status_novo`; (c) se o dicionário passa a exigir `CHECK (usu_email <> '')` (R3); (d) que a ordem física das colunas segue a do Django (FKs no fim) em 21 tabelas, decisão R14 de 2026-10-19 | Julia Cohen / Maria Luiza Guimarães |
| Redação do FR-007 (achado I1 do `/speckit-analyze`): a spec diz que e-mail vazio **nunca** é gravado como texto vazio, mas sem `CHECK` no banco a garantia vale só para `save()` e `create_user` (`QuerySet.update()` e `bulk_create()` não passam por eles). Depois da decisão da Maria Luiza sobre `CHECK (usu_email <> '')` (item (c) acima): com o `CHECK`, criar a restrição e manter o FR-007; sem ele, ajustar a redação do FR-007 | Julia Cohen / Maria Luiza Guimarães |
| Revisar no PR: caminho do `lint.bat` (`apps/sigtcc/` → `sigtcc/`), `pyproject.toml`, `.flake8`, `CHANGELOG.md` e os módulos fora da árvore do PGCS 2.3 | Célio Benjamim (configuração) |
| Descritores oficiais dos critérios por data migration antes do TP3 (FR-014a) | Julia Cohen |
| Códigos de curso da UEA por data migration quando confirmados (FR-016) | Julia Cohen |
| Confirmar a branch `feature/feat-01-modelo-de-dados` (o PGCS 4.3 lista `feat-01` como `feature/feat-01-usuarios`) | Célio Benjamim |

## Project Structure

### Documentation (this feature)

```text
specs/001-modelo-dados/
├── plan.md              # Este arquivo
├── research.md          # Fase 0: decisões D1–D7 e R1–R13
├── data-model.md        # Fase 1: 36 tabelas, campos, domínios e restrições
├── quickstart.md        # Fase 1: roteiro de validação
├── contracts/
│   └── modelos-orm.md   # Fase 1: interface dos modelos para as demais features
├── checklists/
│   └── requirements.md  # Checklist de qualidade da spec
├── tasks.md             # Fase 2 (/speckit-tasks)
└── pr-feat-01.md        # texto do PR (T045)
```

### Source Code (repository root)

```text
manage.py
requirements.txt              # versões exatas (==)
.env.example                  # SECRET_KEY, DEBUG, ALLOWED_HOSTS, DB_*, CACHE_DIR
.gitignore                    # + pasta de CACHE_DIR
lint.bat                      # caminho sigtcc/ (R12)
pyproject.toml                # black e isort, linha de 100 (R13)
.flake8                       # linha de 100, E203/W503, exclui migrations e venv (R13)
README.md                     # instalação e execução (PGCS 2.3)
CHANGELOG.md                  # histórico por baseline (PGCS 2.3 e 7.3)
sigtcc/
├── __init__.py
├── settings.py               # .env via python-dotenv; PostgreSQL; AUTH_USER_MODEL; USE_TZ=False; CACHES
├── urls.py                   # vazio nesta feature (sem telas)
├── wsgi.py
├── asgi.py
├── apps/
│   ├── __init__.py
│   ├── cadastro/             # Épico 1: 27 tabelas
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── choices.py        # TextChoices do Épico 1 (D7)
│   │   ├── fields.py         # CharFixoField (R4) e TimestampField (R1)
│   │   ├── managers.py       # UsuariosManager (D1)
│   │   ├── models.py
│   │   ├── cargas.py         # funções das data migrations (D6)
│   │   ├── migrations/
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_restricoes_cadastro.py
│   │   │   ├── 0003_carga_cursos.py
│   │   │   └── 0004_carga_areas_interesse.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── fabricas.py                     # dados mínimos para os testes (T024)
│   │       ├── test_conformidade_dicionario.py
│   │       ├── test_restricoes_cadastro.py
│   │       ├── test_usuarios.py
│   │       └── test_carga_inicial_cadastro.py
│   ├── defesa/               # Épico 2: 9 tabelas
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── choices.py
│   │   ├── models.py
│   │   ├── cargas.py
│   │   ├── migrations/
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_fk_composta_avaliacoes.py      # RunSQL escrito à mão (D3)
│   │   │   ├── 0003_restricoes_defesa.py
│   │   │   └── 0004_carga_criterios_provisorios.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_restricoes_defesa.py
│   │       └── test_carga_criterios.py
│   └── relatorios/           # Épico 3: sem modelos
│       ├── __init__.py
│       └── apps.py
├── templates/
│   ├── base.html             # mínimo; telas ficam para as features
│   ├── includes/.gitkeep
│   ├── cadastro/.gitkeep
│   ├── defesa/.gitkeep
│   └── relatorios/.gitkeep
└── static/
    ├── css/.gitkeep
    ├── js/.gitkeep
    └── img/.gitkeep
```

Acréscimos à árvore do PGCS 2.3 (para a revisão do Célio, princípio IX): `pyproject.toml`,
`.flake8`, `choices.py`, `fields.py`, `managers.py`, `cargas.py` e as pastas `tests/` dos apps.
Os `.gitkeep` só existem para as pastas vazias entrarem no Git.

Arquivos que o PGCS lista e que esta feature não cria (`views.py`, `forms.py`, `urls.py` de cada
app, `services.py`, `admin.py`) ficam para as features de tela. `sigtcc/media/` continua fora do Git.

**Structure Decision**: estrutura única do PGCS 2.3 (monólito Django), com `manage.py` na raiz
(o PGCS usa `python manage.py`, embora a árvore não o liste). Modelos de cada épico no seu app
(R9); `relatorios` só consulta.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Identidade `GENERATED BY DEFAULT` em vez de `ALWAYS` (dicionário, seção 3; princípio III) | É o que o Django gera; `ALWAYS` recusa qualquer valor informado e quebra fixtures, `loaddata` e partes do framework. Decisão da responsável, registrada na spec (FR-003, Clarifications). | Alterar as 36 colunas para `ALWAYS` por `RunSQL`: trabalho manual em cada migração e conflito permanente com o framework. **Pendente**: consulta à Maria Luiza e registro no dicionário. |
| FK composta `Avaliacoes` → `Banca_Defesa` por `RunSQL` (fora do ORM) | O Django 5.2 não permite relacionamento para modelo com chave composta. | FKs simples para `Defesas` e `Usuarios`: restrições diferentes do dicionário e não impedem avaliação de quem não é da banca. |
| `TimestampField` próprio + `USE_TZ = False` (contra a recomendação padrão do Django) | O dicionário pede `TIMESTAMP` sem fuso, e o `DateTimeField` sempre gera `timestamp with time zone` no PostgreSQL. Com `USE_TZ = False`, os valores no Python também ficam sem fuso, coerentes com a coluna; o sistema roda numa única zona sem horário de verão. | `DateTimeField` puro: gera `timestamptz` e diverge do dicionário em 21 colunas. `TimestampField` com `USE_TZ = True`: datas com fuso no Python gravadas em coluna sem fuso, com conversões implícitas. |
