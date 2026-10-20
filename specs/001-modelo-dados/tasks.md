# Tasks: Modelo de dados do SIGTCC

**Input**: Design documents from `specs/001-modelo-dados/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md) (aprovada em 2026-10-19),
[research.md](research.md), [data-model.md](data-model.md),
[contracts/modelos-orm.md](contracts/modelos-orm.md), [quickstart.md](quickstart.md)

**Tests**: obrigatórios. A constituição (princípio VI) exige um teste por cenário Dado/Quando/Então,
e a spec pede testes de recusa e de aceitação para cada restrição (SC-002) e a conferência
automatizada com o dicionário (SC-001).

**Organization**: tarefas agrupadas por história da spec: US1 (estrutura das 36 tabelas), US2
(integridade no banco) e US3 (domínios fixos).

**Branch**: `feature/feat-01-modelo-de-dados`. Commits no formato
`feat(feat-01): <imperativo, até 72 caracteres, sem ponto final>`. Não fazer `git push`, merge
nem tag sem pedido da responsável (Julia Cohen).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência de tarefa incompleta)
- **[Story]**: história da spec a que a tarefa pertence (US1, US2, US3)

## Regras para todas as tarefas

- Cada tarefa termina com `Rastreabilidade:` e as US e RBN que atende (constituição, princípio II).
  Tarefas de infraestrutura e de estrutura geral, que servem a todas as US, dizem isso
  explicitamente em vez de citar uma US.
- Comentários e docstrings em português do Brasil (constituição, princípio V).
- Cada classe tem docstring com as tags da tabela **Rastreabilidade** abaixo; cada função de carga e
  cada teste citam o FR ou o cenário da spec (por exemplo `# [US2 cenário 3][FR-007]`).
- Nomes de tabela e coluna exatamente como no data-model: `Meta.db_table` sempre explícito e
  `db_column` em toda FK e em `Usuarios.password` (`"usu_senha"`).
- Campos com "nulo" no data-model: `null=True, blank=True`. FKs: `on_delete=models.PROTECT`.
- Nunca informar identificador (`*_id` de identidade) em código, carga ou teste (spec FR-003).
- SQL bruto sempre com o nome da tabela entre aspas duplas (`"Cursos"`), research R2.

## Rastreabilidade (docstring de cada modelo)

| Modelo | Tags |
|---|---|
| Cursos | [US-39][RBN-CAD-14.1][US-03][RBN-CAD-01.1] |
| EquivalenciaCursos | [US-08][RBN-CAD-05.7] |
| Disciplinas | [US-07][RBN-CAD-04.1] |
| AreasInteresse | [US-13][RBN-CAD-08.1] |
| Usuarios | [US-10][RBN-CAD-06.3][US-11][RBN-CAD-06.4][US-04][RBN-CAD-01.3][RBN-CAD-02.3][US-06][RBN-CAD-03.3] |
| Alunos | [US-08][RBN-CAD-05.1][RBN-CAD-05.7] |
| Docentes | [US-03][RBN-CAD-01.1] |
| MembrosExternos | [US-05][RBN-CAD-03.1][US-06][RBN-CAD-03.3] |
| Secretarios | [US-03][RBN-CAD-02.1] |
| CoorientadoresExternos | [US-45][RBN-CAD-10.3] |
| Coordenadores | [US-03][RBN-CAD-01.1] |
| Turmas | [US-07][RBN-CAD-04.1][RBN-CAD-04.5] |
| AlunosTurmas | [US-08][RBN-CAD-05.1][RBN-CAD-05.5] |
| HistoricoAlunosTurmas | [US-09][RBN-CAD-05.4][RBN-CAD-05.8][US-08][RBN-CAD-05.6] |
| TurmasMarcos | [US-43][RBN-CAD-09.1] |
| EntregasMarcos | [US-15][RBN-CAD-09.3][US-44][RBN-CAD-09.5] |
| HistoricoEnviosEntregas | [US-15][RBN-CAD-09.2] |
| TCCs | [US-13][RBN-CAD-07.1][US-14][RBN-CAD-08.3][US-09][RBN-CAD-08.4] |
| Orientacoes | [US-17][RBN-CAD-10.1][RBN-CAD-10.6][US-18][RBN-CAD-10.2] |
| Coorientacoes | [US-45][RBN-CAD-10.3][RBN-CAD-10.7][US-36][RBN-CAD-10.4] |
| PalavrasChaveTCC | [US-13][RBN-CAD-08.1] |
| SolicitacoesOrientacao | [US-17][RBN-CAD-10.1][RBN-CAD-10.6][US-36][RBN-CAD-10.4] |
| HistoricoStatusTCC | [US-14][RBN-CAD-08.7][RBN-CAD-08.8] |
| Artigos | [US-46][RBN-CAD-12.1][US-20][RBN-CAD-12.3] |
| EncontroOrientacao | [US-19][RBN-CAD-11.1] |
| ComentariosEncontro | [US-19][RBN-CAD-11.2] |
| Notificacoes | [US-38][RBN-CAD-13.2] |
| Criterios | [US-25][RBN-DEF-04.1][RBN-DEF-04.2] |
| Ouvintes | [US-30][RBN-DEF-08.2] |
| Defesas | [US-21][RBN-DEF-01.1][US-24][RBN-DEF-01.2][US-27][RBN-DEF-06.3][RBN-DEF-06.4][US-28][RBN-DEF-07.1] |
| DefesasPresenciais | [US-21][RBN-DEF-01.1] |
| DefesasRemotas | [US-21][RBN-DEF-01.1] |
| BancaDefesa | [US-23][RBN-DEF-02.1][RBN-DEF-02.2][US-26][RBN-DEF-05.2] |
| PresencaOuvintes | [US-30][RBN-DEF-08.2][RBN-DEF-08.4] |
| Avaliacoes | [US-25][RBN-DEF-05.2] |
| HistoricoDefesas | [US-40][RBN-DEF-01.6][US-24][RBN-DEF-03.3] |

Fonte: US × RBN do `Historias_de_Usuario_v3_2.md` (IDs novos da matriz de 17/10).

## Migrações desta feature (ordem de execução)

| App | Migração | Tarefa | História |
|---|---|---|---|
| cadastro | `0001_initial` (gerada) | T021 | US1 |
| defesa | `0001_initial` (gerada) | T021 | US1 |
| defesa | `0002_fk_composta_avaliacoes` (escrita à mão) | T022 | US1 |
| cadastro | `0002_restricoes_cadastro` (gerada) | T031 | US2 |
| defesa | `0003_restricoes_defesa` (gerada) | T031 | US2 |
| cadastro | `0003_carga_cursos`, `0004_carga_areas_interesse` (vazias + `RunPython`) | T037 | US3 |
| defesa | `0004_carga_criterios_provisorios` (vazia + `RunPython`) | T038 | US3 |

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: criar o projeto Django na estrutura do PGCS 2.3 com a configuração aprovada.

- [X] T001 Criar `requirements.txt` na raiz: num `venv` com Python 3.12, instalar `"Django>=5.2,<5.3"`, `"psycopg[binary]>=3.2,<4"`, `python-dotenv`, `black`, `isort` e `flake8`; gravar no arquivo apenas esses pacotes e suas dependências com versão exata (`==`) tirada do `pip freeze` (research R12). Não inventar versões. — Rastreabilidade: [infraestrutura da feature 001, sem US específica]
- [X] T002 [P] Criar `pyproject.toml` na raiz com exatamente `[tool.black]` `line-length = 100` e `[tool.isort]` `profile = "black"`, `line_length = 100`, `known_first_party = ["sigtcc"]`; comentário no topo indicando item de configuração para revisão do Célio Benjamim (research R13). — Rastreabilidade: [infraestrutura da feature 001, sem US específica]
- [X] T003 [P] Criar `.flake8` na raiz com `[flake8]`, `max-line-length = 100`, `extend-ignore = E203, W503`, `exclude = migrations, venv, .venv` (research R13). — Rastreabilidade: [infraestrutura da feature 001, sem US específica]
- [X] T004 [P] Criar `lint.bat` na raiz com o texto do PGCS 3.3, trocando o caminho `apps/sigtcc/` por `sigtcc/` nos três comandos (`isort sigtcc/`, `black sigtcc/`, `flake8 sigtcc/`; as opções de linha vêm de `pyproject.toml` e `.flake8`) e mantendo as mensagens de sucesso e falha (research R12; revisão do Célio). — Rastreabilidade: [infraestrutura da feature 001, sem US específica]
- [X] T005 [P] Criar `.env.example` com `SECRET_KEY=troque-esta-chave`, `DEBUG=True`, `ALLOWED_HOSTS=localhost,127.0.0.1`, `DB_NAME=sigtcc`, `DB_USER=sigtcc`, `DB_PASSWORD=`, `DB_HOST=localhost`, `DB_PORT=5432` e `CACHE_DIR=cache` (cada uma com comentário em português), e acrescentar `/cache/` ao `.gitignore` com o comentário `# Cache do bloqueio de login (research D2)`. — Rastreabilidade: [infraestrutura da feature 001, sem US específica]
- [X] T006 Criar `manage.py` (padrão do Django com `DJANGO_SETTINGS_MODULE="sigtcc.settings"`), `sigtcc/__init__.py`, `sigtcc/wsgi.py`, `sigtcc/asgi.py` e `sigtcc/urls.py` com `urlpatterns = []` e comentário "sem rotas nesta feature (spec FR-019)". — Rastreabilidade: [infraestrutura da feature 001, sem US específica]
- [X] T007 Criar os pacotes dos apps: `sigtcc/apps/__init__.py`; `sigtcc/apps/cadastro/{__init__.py, apps.py, migrations/__init__.py, tests/__init__.py}` com `CadastroConfig(name="sigtcc.apps.cadastro", label="cadastro", verbose_name="Cadastro")`; `sigtcc/apps/defesa/{__init__.py, apps.py, migrations/__init__.py, tests/__init__.py}` com `DefesaConfig(name="sigtcc.apps.defesa", label="defesa", verbose_name="Defesa")`; `sigtcc/apps/relatorios/{__init__.py, apps.py}` com `RelatoriosConfig(name="sigtcc.apps.relatorios", label="relatorios", verbose_name="Relatórios")` e sem `models.py` (research R9). — Rastreabilidade: [infraestrutura da feature 001, sem US específica]
- [X] T008 Criar `sigtcc/settings.py`: `BASE_DIR = Path(__file__).resolve().parent.parent`; `load_dotenv(BASE_DIR / ".env")`; `SECRET_KEY`, `DEBUG` (`== "True"`), `ALLOWED_HOSTS` (separado por vírgula) do ambiente; `INSTALLED_APPS` = `django.contrib.contenttypes`, `django.contrib.auth`, `django.contrib.sessions`, `django.contrib.messages`, `django.contrib.staticfiles`, `sigtcc.apps.cadastro`, `sigtcc.apps.defesa`, `sigtcc.apps.relatorios` (**sem** `django.contrib.admin`, research D1); middleware padrão do Django sem o de admin; `ROOT_URLCONF = "sigtcc.urls"`; `TEMPLATES` com `DIRS=[BASE_DIR / "sigtcc" / "templates"]` e `APP_DIRS=True`; `DATABASES["default"]` PostgreSQL (`django.db.backends.postgresql`) com `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`; `AUTH_USER_MODEL = "cadastro.Usuarios"`; `AUTH_PASSWORD_VALIDATORS = []` com comentário "definidos pela US-10 (RBN-CAD-06.3)"; `LANGUAGE_CODE = "pt-br"`; `TIME_ZONE = "America/Manaus"`; `USE_I18N = True`; `USE_TZ = False` (research R1); `STATIC_URL = "static/"`, `STATICFILES_DIRS = [BASE_DIR / "sigtcc" / "static"]`; `MEDIA_URL = "media/"`, `MEDIA_ROOT = BASE_DIR / "sigtcc" / "media"`; `DEFAULT_AUTO_FIELD = "django.db.models.AutoField"` (research D4); `CACHES["default"]` com `django.core.cache.backends.filebased.FileBasedCache` e `LOCATION` = `CACHE_DIR` do `.env` (relativo a `BASE_DIR` quando não for absoluto; padrão `cache`), comentário "bloqueio de login da US-11 (RBN-CAD-06.6), research D2". — Rastreabilidade: [infraestrutura da feature 001, sem US específica]
- [X] T009 [P] Criar `sigtcc/templates/base.html` mínimo (`<!DOCTYPE html>`, `lang="pt-BR"`, `{% block titulo %}`, `{% block conteudo %}`, comentário "telas ficam para as features") e os arquivos `.gitkeep` em `sigtcc/templates/{includes,cadastro,defesa,relatorios}/` e `sigtcc/static/{css,js,img}/`. — Rastreabilidade: [infraestrutura da feature 001, sem US específica]
- [X] T010 [P] Criar `README.md` (pré-requisitos, `venv`, `.env`, `createdb`, `migrate`, `test`, `lint.bat`, conforme [quickstart.md](quickstart.md)) e `CHANGELOG.md` com a seção `## [Não lançado]` e o item "Modelo de dados: 36 tabelas do dicionário de 18/10 e carga inicial dos domínios fixos (feat-01)". — Rastreabilidade: [infraestrutura da feature 001, sem US específica]

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: campos próprios e domínios usados pelos modelos das três histórias.

**⚠️ CRITICAL**: nenhuma história começa antes desta fase.

- [X] T011 Criar `sigtcc/apps/cadastro/fields.py` com `CharFixoField(models.CharField)`, cujo `db_type(self, connection)` retorna `f"char({self.max_length})"` (research R4), e `TimestampField(models.DateTimeField)`, cujo `db_type(self, connection)` retorna `"timestamp"` (coluna sem fuso; research R1). Ambos no nível do módulo, para a migração conseguir importá-los. — Rastreabilidade: [infraestrutura da feature 001, sem US específica]
- [X] T012 [P] Criar `sigtcc/apps/cadastro/choices.py` com 19 classes `models.TextChoices`, valor igual ao rótulo, exatamente: `StatusConta` ("Aguardando Ativação", "Ativa", "Inativa", "Expirada"); `Titulacao` ("Especialista", "Mestre", "Doutor"); `DescricaoTurma` ("TCC 1", "TCC 2"); `StatusTurma` ("Ativa", "Arquivada"); `DiaSemana` ("segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado"); `TipoEventoTurma` ("Exclusão", "Transferência"); `TipoEntrega` ("Proposta", "Documento para Defesa", "Versão Final", "Outra"); `StatusEntrega` ("Aguardando Envio", "Entregue", "Entregue com Atraso", "Não Entregue", "Devolvida para Ajuste", "Homologada"); `ModalidadeTCC` ("Monografia", "Artigo Científico"); `StatusTCC` ("Sem Proposta", "Em Andamento", "Apto para Defesa", "Aprovado para TCC 2", "Aprovado", "Aprovado com Correções", "Concluído", "Reprovado", "Desistente", "Jubilado"); `OrigemOrientacao` ("Pedido Aceito", "Automático"); `StatusOrientacao` ("Ativa", "Encerrada"); `StatusCoorientacao` ("Ativa", "Substituída", "Encerrada"); `TipoSolicitacao` ("Orientação", "Troca de Orientação", "Coorientação"); `StatusSolicitacao` ("Aguardando Resposta", "Aguardando Aceite", "Aceito", "Recusado", "Cancelado"); `GatilhoStatusTCC` ("Vínculo à turma", "Proposta salva", "Transferência para TCC 2", "Indicação de Apto para Defesa", "Liberação do resultado", "Homologação da Versão Final", "Encerramento da participação"); `QualisCapes` ("A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "C"); `StatusSubmissao` ("Submetido", "Em Revisão", "Aceito", "Publicado", "Rejeitado"); `Homologacao` ("Em Análise", "Homologado", "Recusado"). Docstring do módulo: "valores do Glossario_Status da matriz de 17/10 e do dicionário de 18/10 (research D7)". — Rastreabilidade: [infraestrutura da feature 001, sem US específica]
- [X] T013 [P] Criar `sigtcc/apps/defesa/choices.py` com 7 classes `models.TextChoices`, valor igual ao rótulo: `ComponenteCriterio` ("Parte Escrita", "Parte Oral"); `FormatoSessao` ("Presencial", "Remota"); `StatusSessao` ("Agendada", "Em Andamento", "Realizada", "Reagendada", "Cancelada"); `Parecer` ("Reprovado", "Aprovado para TCC 2", "Aprovado", "Aprovado com Correções"); `PapelBanca` ("Orientador (Presidente)", "1º Avaliador", "2º Avaliador", "Suplente", com "º" = U+00BA); `Conceito` ("Exemplar", "Competente", "Necessita de Trabalho"); `EventoDefesa` ("Agendamento", "Reagendamento", "Cancelamento", "Início Automático", "Acionamento do Suplente", "Alteração da Banca", "Liberação do Resultado"). — Rastreabilidade: [infraestrutura da feature 001, sem US específica]

**Checkpoint**: campos e domínios prontos; os modelos podem ser escritos.

---

## Phase 3: User Story 1 - Estrutura das 36 tabelas conforme o dicionário (Priority: P1) 🎯 MVP

**Goal**: a base criada do zero tem exatamente as 36 tabelas e as 201 colunas do dicionário, com
tipos, tamanhos, nulidade e chaves (PK simples, compostas, AK por `unique` e FKs).

**Independent Test**: em banco vazio, `python manage.py migrate` e
`python manage.py test sigtcc.apps.cadastro.tests.test_conformidade_dicionario` passam (spec US1,
cenários 1 a 5; SC-001, SC-006).

### Tests for User Story 1 ⚠️

> Escrever primeiro e confirmar que falham antes dos modelos existirem.

- [ ] T014 [US1] Criar `sigtcc/apps/cadastro/tests/test_conformidade_dicionario.py`, parte 1 (leitura do dicionário e colunas): função que lê `BASE_DIR / "docs/fonte/Modelo_Logico_e_Dicionario_18_10.md"`, separa as seções `### 3.x.y Tabela <Nome>` e extrai de cada linha da tabela `Campo`, `Tipo`, `Nulo?`, `Chave` e `Descrição`; testes (`django.test.TestCase`, consultas em `information_schema` com `connection.cursor()`): `test_cenario1_36_tabelas_sem_salas` (as 36 tabelas existem no schema `public` e nenhuma tem "Sala" no nome); `test_cenario2_colunas_conforme_dicionario` (para as 201 colunas: mesma ordem, `data_type` pelo mapeamento `INT`→`integer`, `VARCHAR(n)`→`character varying` com `character_maximum_length = n`, `CHAR(n)`→`character` com tamanho `n`, `DECIMAL(p,s)`→`numeric` com `numeric_precision = p` e `numeric_scale = s`, `TIMESTAMP`→`timestamp without time zone`, `TIME`→`time without time zone`, `DATE`→`date`, `BOOLEAN`→`boolean`, e `is_nullable` igual a `Nulo?`); `test_sem_tabelas_fora_do_dicionario` (todas as tabelas de `public` estão nas 36 ou em `django_migrations`, `django_content_type`, `django_session`, `auth_permission`, `auth_group`, `auth_group_permissions`; spec FR-020, SC-006); `test_usuarios_tem_6_colunas` (sem `last_login`, `is_staff`, `is_superuser`; research D1). Não comparar índices (research R11). Mensagens de falha citando tabela e coluna. — Rastreabilidade: [base de todas as US; sem RBN específica][spec US1 cenários 1, 2][FR-001][FR-002][FR-020][SC-001][SC-006]
- [ ] T015 [US1] Completar `sigtcc/apps/cadastro/tests/test_conformidade_dicionario.py`, parte 2 (chaves e identidade): `test_pk_conforme_dicionario` (colunas de cada PK em `information_schema.table_constraints`/`key_column_usage` iguais às colunas com `PK` na coluna `Chave` do dicionário, inclusive as 5 compostas, na ordem do dicionário); `test_cenario3_avaliacoes` (PK de `"Avaliacoes"` = (`ava_def_id`, `ava_usu_id`, `ava_cri_id`) e `pg_get_constraintdef` da restrição `fk_avaliacoes_banca_defesa` igual a `FOREIGN KEY (ava_def_id, ava_usu_id) REFERENCES "Banca_Defesa"(ban_def_id, ban_usu_id) DEFERRABLE INITIALLY DEFERRED`); `test_cenario4_especializacoes` (a PK de `"Alunos"`, `"Docentes"`, `"MembrosExternos"` e `"Secretarios"` também é FK para `"Usuarios"(usu_id)`, via `pg_constraint`); `test_fks_conforme_modelo_logico` (cada `[FK Tabela.coluna]` da seção 2 do dicionário existe como FK no banco para a tabela certa; `ava_def_id` e `ava_usu_id` só pela FK composta); `test_cenario5_identidade_by_default` (toda coluna descrita como "GENERATED ALWAYS AS IDENTITY" tem `is_identity = 'YES'` e `identity_generation = 'BY DEFAULT'`, desvio aprovado em FR-003, e um `Cursos` criado sem `cur_id` recebe identificador gerado). — Rastreabilidade: [base de todas as US; sem RBN específica][spec US1 cenários 3, 4, 5][FR-003][FR-004][FR-005]

### Implementation for User Story 1

- [ ] T016 [US1] Criar `sigtcc/apps/cadastro/managers.py` com `UsuariosManager(BaseUserManager)`: `create_user(self, usu_email, usu_nome, password=None, **campos)` que faz `email = self.normalize_email(usu_email) if usu_email else ""`, converte para `None` se `email.strip() == ""` (o `normalize_email(None)` do Django devolve `""`), aplica `campos.setdefault("usu_status", StatusConta.AGUARDANDO_ATIVACAO)`, chama `user.set_password(password)` quando houver senha e deixa `user.password = None` quando não houver, e salva com `using=self._db`. Sem `create_superuser` (research D1; contrato §3). — Rastreabilidade: [US-10][RBN-CAD-06.3][US-11][RBN-CAD-06.4]
- [ ] T017 [US1] Em `sigtcc/apps/cadastro/models.py` (sem `Meta.constraints`, que ficam para a US2; `choices=` nos campos de domínio), criar: `Cursos` (`"Cursos"`): `cur_id` AutoField PK; `cur_nome` CharField(100); `cur_descricao` CharField(255), nulo. `EquivalenciaCursos` (`"Equivalencia_Cursos"`): `eqc_codigo_uea` CharField(20) PK; `eqc_cur` FK → Cursos, `db_column="eqc_cur_id"`. `Disciplinas` (`"Disciplinas"`): `dis_id` AutoField PK; `dis_codigo` CharField(20), `unique`; `dis_nome` CharField(100), nulo; `dis_descricao` CharField(255), nulo. `AreasInteresse` (`"Areas_Interesse"`): `ari_id` AutoField PK; `ari_nome` CharField(100), `unique`. `Usuarios` (`"Usuarios"`, herda só de `AbstractBaseUser`): `usu_id` AutoField PK; `usu_nome` CharField(150); `usu_email` CharField(100), nulo, `unique`; `password` CharField(255), nulo, `db_column="usu_senha"`; `usu_status` CharField(30), `StatusConta`; `usu_link_gerado_em` TimestampField, nulo; `last_login = None`; `objects = UsuariosManager()`; `USERNAME_FIELD = "usu_email"`, `EMAIL_FIELD = "usu_email"`, `REQUIRED_FIELDS = ["usu_nome"]`; propriedade `is_active` que retorna `self.usu_status == StatusConta.ATIVA`; `__str__` que retorna `self.usu_nome`. `Alunos` (`"Alunos"`): `alu` OneToOneField → Usuarios, `primary_key=True`, `db_column="alu_id"`; `alu_matricula` CharFixoField(10), `unique`; `alu_codigo_curso` CharField(20) (não é FK). `Docentes` (`"Docentes"`): `doc` OneToOneField → Usuarios, PK, `db_column="doc_id"`; `doc_titulacao` CharField(20), `Titulacao`; `doc_cur` FK → Cursos, `db_column="doc_cur_id"`; `doc_assinatura_path` CharField(255), nulo. `MembrosExternos` (`"MembrosExternos"`): `mem` OneToOneField → Usuarios, PK, `db_column="mem_id"`; `mem_titulacao` CharField(20), `Titulacao`; `mem_instituicao` CharField(150); `mem_assinatura_path` CharField(255), nulo; `mem_validade_ate` DateField, nulo. `Secretarios` (`"Secretarios"`): `sec` OneToOneField → Usuarios, PK, `db_column="sec_id"`; `sec_cur` FK → Cursos, `db_column="sec_cur_id"`. `CoorientadoresExternos` (`"CoorientadoresExternos"`): `cext_id` AutoField PK; `cext_nome` CharField(150); `cext_email` CharField(100), nulo, `unique`; `cext_instituicao` CharField(150), nulo. `Coordenadores` (`"Coordenadores"`): `cor_cur` OneToOneField → Cursos, PK, `db_column="cor_cur_id"`; `cor_doc` OneToOneField → Docentes, `db_column="cor_doc_id"`. — Rastreabilidade: [US-39][RBN-CAD-14.1][US-03][RBN-CAD-01.1][US-08][RBN-CAD-05.7][US-07][RBN-CAD-04.1][US-13][RBN-CAD-08.1][US-10][RBN-CAD-06.3][US-11][RBN-CAD-06.4][US-04][RBN-CAD-01.3][RBN-CAD-02.3][US-06][RBN-CAD-03.3][RBN-CAD-05.1][US-05][RBN-CAD-03.1][RBN-CAD-02.1][US-45][RBN-CAD-10.3]
- [ ] T018 [US1] Continuar `sigtcc/apps/cadastro/models.py`: `Turmas` (`"Turmas"`): `tur_id` AutoField PK; `tur_identificador` CharField(30), `unique`; `tur_descricao` CharField(10), `DescricaoTurma`; `tur_doc` FK → Docentes (`tur_doc_id`); `tur_dis` FK → Disciplinas (`tur_dis_id`); `tur_cur` FK → Cursos (`tur_cur_id`); `tur_ano` IntegerField; `tur_semestre` IntegerField; `tur_dia_da_semana` CharField(20), `DiaSemana`; `tur_hora_inicio` TimeField; `tur_hora_termino` TimeField; `tur_local` CharField(100); `tur_status` CharField(20), `StatusTurma`. `AlunosTurmas` (`"Alunos_Turmas"`): `pk = models.CompositePrimaryKey("mat_alu_id", "mat_tur_id")`; `mat_alu` FK → Alunos (`mat_alu_id`); `mat_tur` FK → Turmas (`mat_tur_id`); `mat_data_inscricao` TimestampField. `HistoricoAlunosTurmas` (`"Historico_Alunos_Turmas"`): `hat_id` AutoField PK; `hat_alu` FK → Alunos (`hat_alu_id`); `hat_tur_origem` FK → Turmas (`hat_tur_origem_id`, `related_name="historicos_origem"`); `hat_tur_destino` FK → Turmas, nulo (`hat_tur_destino_id`, `related_name="historicos_destino"`); `hat_tipo_evento` CharField(20), `TipoEventoTurma`; `hat_justificativa` CharField(500); `hat_data_hora` TimestampField; `hat_usu` FK → Usuarios (`hat_usu_id`). `TurmasMarcos` (`"Turmas_Marcos"`): `tma_id` AutoField PK; `tma_tur` FK → Turmas (`tma_tur_id`); `tma_tipo` CharField(30), `TipoEntrega`; `tma_titulo` CharField(100); `tma_instrucao` CharField(1000), nulo; `tma_data_limite` TimestampField. `EntregasMarcos` (`"Entregas_Marcos"`): `ent_id` AutoField PK; `ent_tma` FK → TurmasMarcos (`ent_tma_id`); `ent_alu` FK → Alunos (`ent_alu_id`); `ent_status` CharField(30), `StatusEntrega`; `ent_feedback` CharField(500), nulo; `ent_data_avaliacao` TimestampField, nulo; `ent_correcoes_conferidas_em` TimestampField, nulo. `HistoricoEnviosEntregas` (`"Historico_Envios_Entregas"`): `hen_id` AutoField PK; `hen_ent` FK → EntregasMarcos (`hen_ent_id`); `hen_link` CharField(500); `hen_data_envio` TimestampField. — Rastreabilidade: [US-07][RBN-CAD-04.1][RBN-CAD-04.5][US-08][RBN-CAD-05.1][RBN-CAD-05.5][US-09][RBN-CAD-05.4][RBN-CAD-05.8][RBN-CAD-05.6][US-43][RBN-CAD-09.1][US-15][RBN-CAD-09.3][US-44][RBN-CAD-09.5][RBN-CAD-09.2]
- [ ] T019 [US1] Concluir `sigtcc/apps/cadastro/models.py`: `TCCs` (`"TCCs"`): `tcc_id` AutoField PK; `tcc_alu` FK → Alunos (`tcc_alu_id`); `tcc_tur` FK → Turmas (`tcc_tur_id`); `tcc_ari` FK → AreasInteresse, nulo (`tcc_ari_id`); `tcc_modalidade` CharField(30), nulo, `ModalidadeTCC`; `tcc_titulo` CharField(250), nulo; `tcc_subtitulo` CharField(250), nulo; `tcc_resumo` CharField(1000), nulo; `tcc_link_proposta` CharField(500), nulo; `tcc_status` CharField(50), `StatusTCC`; `tcc_justificativa_encerramento` CharField(500), nulo. `Orientacoes` (`"Orientacoes"`): `ori_id` AutoField PK; `ori_tcc` FK → TCCs (`ori_tcc_id`); `ori_doc` FK → Docentes (`ori_doc_id`); `ori_origem` CharField(20), `OrigemOrientacao`; `ori_status` CharField(20), `StatusOrientacao`; `ori_data_inicio` TimestampField; `ori_data_fim` TimestampField, nulo. `Coorientacoes` (`"Coorientacoes"`): `coo_id` AutoField PK; `coo_tcc` FK → TCCs (`coo_tcc_id`); `coo_doc` FK → Docentes, nulo (`coo_doc_id`); `coo_cext` FK → CoorientadoresExternos, nulo (`coo_cext_id`); `coo_status` CharField(20), `StatusCoorientacao`; `coo_data_inicio` TimestampField; `coo_data_fim` TimestampField, nulo. `PalavrasChaveTCC` (`"PalavrasChave_TCC"`): `pk = models.CompositePrimaryKey("pal_tcc_id", "pal_palavra")`; `pal_tcc` FK → TCCs (`pal_tcc_id`); `pal_palavra` CharField(100). `SolicitacoesOrientacao` (`"Solicitacoes_Orientacao"`): `sol_id` AutoField PK; `sol_tcc` FK → TCCs (`sol_tcc_id`); `sol_doc` FK → Docentes (`sol_doc_id`); `sol_tipo` CharField(20), `TipoSolicitacao`; `sol_status` CharField(20), `StatusSolicitacao`; `sol_data_solicitacao` TimestampField; `sol_data_resposta` TimestampField, nulo. `HistoricoStatusTCC` (`"Historico_Status_TCC"`): `hst_id` AutoField PK; `hst_tcc` FK → TCCs (`hst_tcc_id`); `hst_tur` FK → Turmas (`hst_tur_id`); `hst_status_anterior` CharField(50), nulo, `StatusTCC`; `hst_status_novo` CharField(50), `StatusTCC`; `hst_gatilho` CharField(100), `GatilhoStatusTCC`; `hst_data_hora` TimestampField; `hst_usu` FK → Usuarios (`hst_usu_id`). `Artigos` (`"Artigos"`): `art` OneToOneField → TCCs, PK, `db_column="art_id"`; `art_veiculo_publicacao` CharField(150), nulo; `art_link_doi` CharField(500); `art_qualis_capes` CharField(5), nulo, `QualisCapes`; `art_status_submissao` CharField(30), nulo, `StatusSubmissao`; `art_homologacao` CharField(20), nulo, `Homologacao`; `art_homologado_por` FK → Usuarios, nulo, `db_column="art_homologado_por"`; `art_data_homologacao` TimestampField, nulo. `EncontroOrientacao` (`"Encontro_Orientacao"`): `enc_id` AutoField PK; `enc_tcc` FK → TCCs (`enc_tcc_id`); `enc_data` DateField; `enc_pauta` CharField(2000); `enc_metas` CharField(2000). `ComentariosEncontro` (`"Comentarios_Encontro"`): `com_id` AutoField PK; `com_enc` FK → EncontroOrientacao (`com_enc_id`); `com_usu` FK → Usuarios (`com_usu_id`); `com_texto` CharField(1000); `com_data_hora` TimestampField. `Notificacoes` (`"Notificacoes"`): `not_id` AutoField PK; `not_usu` FK → Usuarios (`not_usu_id`); `not_mensagem` CharField(500); `not_link_tela` CharField(255), nulo; `not_data_hora` TimestampField; `not_lida` BooleanField(`db_default=False`) (research R6). — Rastreabilidade: [US-13][RBN-CAD-07.1][US-14][RBN-CAD-08.3][US-09][RBN-CAD-08.4][US-17][RBN-CAD-10.1][RBN-CAD-10.6][US-18][RBN-CAD-10.2][US-45][RBN-CAD-10.3][RBN-CAD-10.7][US-36][RBN-CAD-10.4][RBN-CAD-08.1][RBN-CAD-08.7][RBN-CAD-08.8][US-46][RBN-CAD-12.1][US-20][RBN-CAD-12.3][US-19][RBN-CAD-11.1][RBN-CAD-11.2][US-38][RBN-CAD-13.2]
- [ ] T020 [P] [US1] Criar `sigtcc/apps/defesa/models.py` (sem `Meta.constraints`; FKs para o cadastro por string `"cadastro.<Modelo>"` ou `settings.AUTH_USER_MODEL`; `TimestampField` e `CharFixoField` importados de `sigtcc.apps.cadastro.fields`): `Criterios` (`"Criterios"`): `cri_id` AutoField PK; `cri_nome` CharField(100); `cri_componente` CharField(20), `ComponenteCriterio`; `cri_descricao` CharField(255), nulo; `cri_desc_exemplar` CharField(255); `cri_desc_competente` CharField(255); `cri_desc_necessita_trabalho` CharField(255); `cri_peso` DecimalField(3, 1). `Ouvintes` (`"Ouvintes"`): `ouv_id` AutoField PK; `ouv_matricula` CharFixoField(10), `unique`; `ouv_nome` CharField(150). `Defesas` (`"Defesas"`): `def_id` AutoField PK; `def_tcc` FK → cadastro.TCCs (`def_tcc_id`); `def_data` DateField; `def_h_inicio` TimeField; `def_formato` CharField(20), `FormatoSessao`; `def_status` CharField(30), `StatusSessao`; `def_parecer` CharField(30), nulo, `Parecer`; `def_nota_final` DecimalField(3, 1), nulo; `def_ocorrencias` CharField(2000), nulo; `def_data_liberacao_resultado` TimestampField, nulo; `def_ata_final_path` CharField(255), nulo; `def_folha_aprovacao_path` CharField(255), nulo. `DefesasPresenciais` (`"Defesas_Presenciais"`): `dep_def` OneToOneField → Defesas, PK, `db_column="dep_def_id"`; `dep_local` CharField(100). `DefesasRemotas` (`"Defesas_Remotas"`): `der_def` OneToOneField → Defesas, PK, `db_column="der_def_id"`; `der_link` CharField(500). `BancaDefesa` (`"Banca_Defesa"`): `pk = models.CompositePrimaryKey("ban_def_id", "ban_usu_id")`; `ban_def` FK → Defesas (`ban_def_id`); `ban_usu` FK → Usuarios (`ban_usu_id`, `related_name="bancas"`); `ban_papel` CharField(30), `PapelBanca`; `ban_usu_substituido` FK → Usuarios, nulo (`ban_usu_substituido_id`, `related_name="substituicoes_banca"`); `ban_justificativa_substituicao` CharField(500), nulo; `ban_assinatura_path` CharField(255), nulo; `ban_data_envio` TimestampField, nulo. `PresencaOuvintes` (`"Presenca_Ouvintes"`): `pk = models.CompositePrimaryKey("pre_def_id", "pre_ouv_id")`; `pre_def` FK → Defesas (`pre_def_id`); `pre_ouv` FK → Ouvintes (`pre_ouv_id`). `Avaliacoes` (`"Avaliacoes"`): `pk = models.CompositePrimaryKey("ava_def_id", "ava_usu_id", "ava_cri_id")`; `ava_def` FK → Defesas, `db_constraint=False`, `db_index=False` (`ava_def_id`); `ava_usu` FK → Usuarios, `db_constraint=False` (`ava_usu_id`); `ava_cri` FK → Criterios (`ava_cri_id`); `ava_conceito` CharField(30), `Conceito`; `ava_nota` DecimalField(3, 1); `ava_observacoes` CharField(500), nulo; `ava_data_hora` TimestampField. `HistoricoDefesas` (`"Historico_Defesas"`): `hdf_id` AutoField PK; `hdf_def` FK → Defesas (`hdf_def_id`); `hdf_evento` CharField(30), `EventoDefesa`; `hdf_status_anterior` CharField(30), nulo, `StatusSessao`; `hdf_status_novo` CharField(30), nulo, `StatusSessao`; `hdf_data_anterior` DateField, nulo; `hdf_hora_anterior` TimeField, nulo; `hdf_data_nova` DateField, nulo; `hdf_hora_nova` TimeField, nulo; `hdf_membro_removido` FK → Usuarios, nulo (`hdf_membro_removido_id`, `related_name="+"`); `hdf_membro_incluido` FK → Usuarios, nulo (`hdf_membro_incluido_id`, `related_name="+"`); `hdf_justificativa` CharField(500), nulo; `hdf_data_hora` TimestampField; `hdf_usu` FK → Usuarios, nulo (`hdf_usu_id`, `related_name="eventos_defesa"`). — Rastreabilidade: [US-25][RBN-DEF-04.1][RBN-DEF-04.2][US-30][RBN-DEF-08.2][US-21][RBN-DEF-01.1][US-24][RBN-DEF-01.2][US-27][RBN-DEF-06.3][RBN-DEF-06.4][US-28][RBN-DEF-07.1][US-23][RBN-DEF-02.1][RBN-DEF-02.2][US-26][RBN-DEF-05.2][RBN-DEF-08.4][US-40][RBN-DEF-01.6][RBN-DEF-03.3]
- [ ] T021 [US1] Gerar as migrações iniciais com `python manage.py makemigrations cadastro defesa` → `sigtcc/apps/cadastro/migrations/0001_initial.py` e `sigtcc/apps/defesa/migrations/0001_initial.py`; rodar `python manage.py check` (sem erros, inclusive `auth.E003`) e conferir no `python manage.py sqlmigrate` de cada app: nomes de tabela entre aspas, `char(10)` nas matrículas, `timestamp` (sem `with time zone`) nas 21 colunas, `integer GENERATED BY DEFAULT AS IDENTITY` nas PKs identity, PKs compostas na ordem do dicionário, `DEFAULT false` em `not_lida`, nenhuma FK simples saindo de `ava_def_id` ou `ava_usu_id`. Se o `CompositePrimaryKey` não aceitar o nome de coluna (`"mat_alu_id"`), usar o nome do campo (`"mat_alu"`) e registrar a decisão em `specs/001-modelo-dados/research.md` (D3). — Rastreabilidade: [base de todas as US; sem RBN específica][modelos de T017–T020]
- [ ] T022 [US1] Criar à mão `sigtcc/apps/defesa/migrations/0002_fk_composta_avaliacoes.py` com `dependencies = [("defesa", "0001_initial")]` e `migrations.RunSQL` com `sql` = `ALTER TABLE "Avaliacoes" ADD CONSTRAINT fk_avaliacoes_banca_defesa FOREIGN KEY (ava_def_id, ava_usu_id) REFERENCES "Banca_Defesa" (ban_def_id, ban_usu_id) ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;` e `reverse_sql` = `ALTER TABLE "Avaliacoes" DROP CONSTRAINT fk_avaliacoes_banca_defesa;` (data-model, Avaliacoes; research D3), com comentário explicando por que está fora do ORM. — Rastreabilidade: [US-25][RBN-DEF-05.2][US-23][RBN-DEF-02.1][RBN-DEF-02.2][US-26]
- [ ] T023 [US1] Criar o banco local (`createdb`) e o `.env` a partir do `.env.example`, rodar `python manage.py migrate` e `python manage.py test sigtcc.apps.cadastro.tests.test_conformidade_dicionario`; corrigir `sigtcc/apps/cadastro/models.py` ou `sigtcc/apps/defesa/models.py` até todos os testes de T014 e T015 passarem (regerar as `0001_initial` se for preciso, pois ainda não estão na `develop`). — Rastreabilidade: [base de todas as US; sem RBN específica][spec US1][SC-001]

**Checkpoint**: US1 completa. As 36 tabelas conferem com o dicionário; MVP entregável.

---

## Phase 4: User Story 2 - Integridade garantida pelo próprio banco (Priority: P1)

**Goal**: o banco recusa valores fora do domínio, duplicidades proibidas, referências inexistentes e
combinações inconsistentes (FR-004 a FR-012); e-mail vazio vira `NULL` (FR-007).

**Independent Test**: `python manage.py test sigtcc.apps.cadastro.tests.test_restricoes_cadastro
sigtcc.apps.defesa.tests.test_restricoes_defesa sigtcc.apps.cadastro.tests.test_usuarios` passa
(spec US2, cenários 1 a 11; SC-002).

### Tests for User Story 2 ⚠️

> Cada restrição tem um teste de recusa e um de aceitação. Toda asserção de `IntegrityError` fica
> dentro de `transaction.atomic()`. Para FKs (adiadas, research R5), executar
> `SET CONSTRAINTS ALL IMMEDIATE` antes da gravação.

- [ ] T024 [US2] Criar `sigtcc/apps/cadastro/tests/fabricas.py` com funções que criam registros mínimos válidos, sem informar identificadores: `criar_curso`, `criar_usuario` (via `Usuarios.objects.create_user`), `criar_docente`, `criar_aluno` (matrícula com 10 dígitos, sequencial por chamada), `criar_disciplina`, `criar_turma` (horário 14:00–16:00, `tur_ano` 2026, `tur_semestre` 2, valores válidos dos domínios), `criar_tcc` (status 'Sem Proposta'), `criar_tcc_com_proposta` (status 'Em Andamento' com título, resumo e modalidade), `criar_marco`, `criar_coorientador_externo`; e `criar_defesa`, `criar_criterio`, `criar_membro_banca` para os testes do app defesa. — Rastreabilidade: [infraestrutura da feature 001, sem US específica][apoio aos testes da US2]
- [ ] T025 [P] [US2] Criar `sigtcc/apps/cadastro/tests/test_restricoes_cadastro.py` com os cenários da spec: `test_cenario1_tcc_status_fora_do_glossario` ('Finalizado' recusado); `test_cenario2_campos_obrigatorios_com_proposta` ('Em Andamento' sem título/resumo/modalidade recusado; com os três aceito; 'Desistente' sem os três recusado; 'Sem Proposta' sem os três aceito); `test_cenario3_uma_orientacao_ativa` (segunda 'Ativa' no mesmo TCC recusada; 'Encerrada' extra aceita); `test_cenario4_uma_entrega_por_tipo` (segunda 'Proposta' na mesma turma recusada; duas 'Outra' aceitas); `test_cenario5_coorientacao_docente_ou_externo` (ambos ou nenhum recusado; só docente e só externo aceitos; mesmo docente 'Ativa' duas vezes no TCC recusado; um 'Substituída' e um 'Ativa' aceitos); `test_cenario6_status_por_tipo` ('Coorientação' + 'Aguardando Resposta' recusado; + 'Aguardando Aceite' aceito; 'Orientação' + 'Aguardando Aceite' recusado; dois pedidos 'Orientação'/'Troca de Orientação' em 'Aguardando Resposta' no mesmo TCC recusados); `test_cenario7_emails` (dois `Usuarios` e dois `CoorientadoresExternos` com e-mail nulo aceitos; e-mail repetido recusado); `test_cenario8_horario_turma` (`tur_hora_termino` igual ou anterior a `tur_hora_inicio` recusado); `test_cenario10_fk_inexistente` (`Docentes` com `doc_cur_id` inexistente recusado após `SET CONSTRAINTS ALL IMMEDIATE`); `test_exclusao_protegida` (excluir `Cursos` referenciado levanta `ProtectedError` no ORM); `test_exclusao_recusada_pelo_banco` (`DELETE FROM "Cursos"` por SQL de um curso referenciado, após `SET CONSTRAINTS ALL IMMEDIATE`, levanta `IntegrityError`; FR-005); `test_fr012_not_lida_padrao_falso` (`INSERT` por SQL em `"Notificacoes"` sem a coluna `not_lida` grava `false`; FR-012); `test_pk_composta_recusa_duplicata` (o mesmo (`mat_alu_id`, `mat_tur_id`) duas vezes em `"Alunos_Turmas"` e a mesma (`pal_tcc_id`, `pal_palavra`) duas vezes em `"PalavrasChave_TCC"` recusados; pares diferentes aceitos; FR-004); um teste parametrizado (`subTest`) com valor inválido e válido para cada CHECK de domínio do cadastro listado no data-model (`ck_usuarios_usu_status`, `ck_docentes_doc_titulacao`, `ck_membrosexternos_mem_titulacao`, `ck_turmas_tur_descricao`, `ck_turmas_tur_status`, `ck_turmas_tur_dia_da_semana`, `ck_historico_alunos_turmas_hat_tipo_evento`, `ck_turmas_marcos_tma_tipo`, `ck_entregas_marcos_ent_status`, `ck_tccs_tcc_modalidade`, `ck_orientacoes_ori_origem`, `ck_orientacoes_ori_status`, `ck_coorientacoes_coo_status`, `ck_solicitacoes_orientacao_sol_tipo`, `ck_historico_status_tcc_hst_status_anterior` (nulo aceito), `ck_historico_status_tcc_hst_status_novo`, `ck_historico_status_tcc_hst_gatilho`, `ck_artigos_art_qualis_capes`, `ck_artigos_art_status_submissao`, `ck_artigos_art_homologacao` (nulos aceitos)); `ck_alunos_alu_matricula` ('12345' e 'ABCDEFGHIJ' recusados; '2026000001' aceito); `ck_turmas_tur_ano` (999 e 10000 recusados; 2026 aceito); `ck_turmas_tur_semestre` (3 recusado; 1 e 2 aceitos); unicidades simples e compostas de FR-006 (`dis_codigo`, `ari_nome`, `alu_matricula`, `tur_identificador`, `cor_doc_id`, (`ent_tma_id`, `ent_alu_id`), (`tcc_alu_id`, `tcc_tur_id`)) recusando a duplicata. — Rastreabilidade: [US-39][RBN-CAD-14.1][US-03][RBN-CAD-01.1][US-08][RBN-CAD-05.7][US-07][RBN-CAD-04.1][US-13][RBN-CAD-08.1][US-10][RBN-CAD-06.3][US-11][RBN-CAD-06.4][US-04][RBN-CAD-01.3][RBN-CAD-02.3][US-06][RBN-CAD-03.3][RBN-CAD-05.1][US-05][RBN-CAD-03.1][RBN-CAD-02.1][US-45][RBN-CAD-10.3][RBN-CAD-04.5][RBN-CAD-05.5][US-09][RBN-CAD-05.4][RBN-CAD-05.8][RBN-CAD-05.6][US-43][RBN-CAD-09.1][US-15][RBN-CAD-09.3][US-44][RBN-CAD-09.5][RBN-CAD-09.2][RBN-CAD-07.1][US-14][RBN-CAD-08.3][RBN-CAD-08.4][US-17][RBN-CAD-10.1][RBN-CAD-10.6][US-18][RBN-CAD-10.2][RBN-CAD-10.7][US-36][RBN-CAD-10.4][RBN-CAD-08.7][RBN-CAD-08.8][US-46][RBN-CAD-12.1][US-20][RBN-CAD-12.3][US-19][RBN-CAD-11.1][RBN-CAD-11.2][US-38][RBN-CAD-13.2][spec US2 cenários 1–8, 10][FR-004]–[FR-012]
- [ ] T026 [P] [US2] Criar `sigtcc/apps/defesa/tests/test_restricoes_defesa.py`: `test_cenario9_nota_fora_da_faixa` (`ava_nota` 10.5 e -0.1 recusadas; 0.0 e 10.0 aceitas); faixas de `ck_criterios_cri_peso` e `ck_defesas_def_nota_final` (10.5 e -0.1 recusados; nulo aceito em `def_nota_final`); CHECKs de domínio com valor inválido e válido: `ck_criterios_cri_componente`, `ck_defesas_def_formato`, `ck_defesas_def_status`, `ck_defesas_def_parecer` (nulo aceito), `ck_banca_defesa_ban_papel`, `ck_avaliacoes_ava_conceito`, `ck_historico_defesas_hdf_evento`, `ck_historico_defesas_hdf_status_anterior` e `ck_historico_defesas_hdf_status_novo` (nulos aceitos); `ck_ouvintes_ouv_matricula` ('12345' recusado; '2026000001' aceito) e unicidade de `ouv_matricula`; `test_fk_composta_recusa_avaliador_fora_da_banca` (avaliação com (`ava_def_id`, `ava_usu_id`) inexistente em `"Banca_Defesa"` recusada após `SET CONSTRAINTS ALL IMMEDIATE`); `test_exclusao_banca_com_avaliacao` (excluir `BancaDefesa` que tem `Avaliacoes` levanta `IntegrityError`, não `ProtectedError`; contrato §4); `test_pk_composta_recusa_duplicata` (o mesmo (`ban_def_id`, `ban_usu_id`) duas vezes em `"Banca_Defesa"`, o mesmo (`pre_def_id`, `pre_ouv_id`) em `"Presenca_Ouvintes"` e o mesmo (`ava_def_id`, `ava_usu_id`, `ava_cri_id`) em `"Avaliacoes"` recusados; combinações diferentes aceitas; FR-004). — Rastreabilidade: [US-25][RBN-DEF-04.1][RBN-DEF-04.2][US-30][RBN-DEF-08.2][US-21][RBN-DEF-01.1][US-24][RBN-DEF-01.2][US-27][RBN-DEF-06.3][RBN-DEF-06.4][US-28][RBN-DEF-07.1][US-23][RBN-DEF-02.1][RBN-DEF-02.2][US-26][RBN-DEF-05.2][RBN-DEF-08.4][US-40][RBN-DEF-01.6][RBN-DEF-03.3][spec US2 cenário 9][FR-004][FR-005][FR-010]
- [ ] T027 [P] [US2] Criar `sigtcc/apps/cadastro/tests/test_usuarios.py`: `test_cenario11_email_vazio_vira_nulo` (`Usuarios` e `CoorientadoresExternos` salvos com `""` e com `"   "` ficam com e-mail `NULL`, conferido por SQL `IS NULL`); `test_cenario7_dois_alunos_sem_email` (dois `create_user(None, ...)` e dois `create_user("", ...)` coexistem); `test_create_user_sem_senha` (`password` nulo, `has_usable_password()` falso, status 'Aguardando Ativação'); `test_create_user_com_senha` (hash diferente do texto e `check_password` verdadeiro); `test_is_active_por_status` (verdadeiro só para 'Ativa' entre os 4 status); `test_str_usa_nome` (`str()` de usuário sem e-mail retorna `usu_nome`); `test_sem_colunas_extras` (`Usuarios._meta` sem `last_login`, `is_staff`, `is_superuser`, `groups`, `user_permissions`). — Rastreabilidade: [US-10][RBN-CAD-06.3][US-11][RBN-CAD-06.4][US-04][RBN-CAD-01.3][RBN-CAD-02.3][US-06][RBN-CAD-03.3][US-45][RBN-CAD-10.3][spec US2 cenários 7, 11][FR-007]

### Implementation for User Story 2

- [ ] T028 [US2] Acrescentar `Meta.constraints` em `sigtcc/apps/cadastro/models.py`, com `models.CheckConstraint(condition=..., name=...)` gerado de `<Choices>.values` (domínios anuláveis com `| Q(<campo>__isnull=True)`) e `models.UniqueConstraint(fields=..., condition=..., name=...)`, exatamente: `ck_usuarios_usu_status`; `ck_alunos_alu_matricula` (`alu_matricula__regex=r"^[0-9]{10}$"`); `ck_docentes_doc_titulacao`; `ck_membrosexternos_mem_titulacao`; `ck_turmas_tur_descricao`, `ck_turmas_tur_status`, `ck_turmas_tur_dia_da_semana`, `ck_turmas_tur_semestre` (`tur_semestre__in=[1, 2]`), `ck_turmas_tur_ano` (`tur_ano__gte=1000, tur_ano__lte=9999`), `ck_turmas_horario` (`tur_hora_termino__gt=F("tur_hora_inicio")`); `ck_historico_alunos_turmas_hat_tipo_evento`; `ck_turmas_marcos_tma_tipo` e `uq_turmas_marcos_tipo_por_turma` (`fields=["tma_tur", "tma_tipo"]`, `condition=~Q(tma_tipo="Outra")`); `ck_entregas_marcos_ent_status` e `uq_entregas_marcos_aluno_atividade` (`ent_tma`, `ent_alu`); `ck_tccs_tcc_status`, `ck_tccs_tcc_modalidade` (aceita nulo), `ck_tccs_campos_obrigatorios_com_proposta` (`Q(tcc_status="Sem Proposta") | Q(tcc_titulo__isnull=False, tcc_resumo__isnull=False, tcc_modalidade__isnull=False)`), `uq_tccs_aluno_turma` (`tcc_alu`, `tcc_tur`); `ck_orientacoes_ori_origem`, `ck_orientacoes_ori_status`, `uq_orientacoes_uma_ativa_por_tcc` (`ori_tcc`, `condition=Q(ori_status="Ativa")`); `ck_coorientacoes_coo_status`, `ck_coorientacoes_docente_ou_externo` (`Q(coo_doc__isnull=False, coo_cext__isnull=True) | Q(coo_doc__isnull=True, coo_cext__isnull=False)`), `uq_coorientacoes_docente_ativo` (`coo_tcc`, `coo_doc`, `condition=Q(coo_status="Ativa")`), `uq_coorientacoes_externo_ativo` (`coo_tcc`, `coo_cext`, `condition=Q(coo_status="Ativa")`); `ck_solicitacoes_orientacao_sol_tipo`, `ck_solicitacoes_orientacao_status_por_tipo` (`Q(sol_tipo__in=["Orientação", "Troca de Orientação"], sol_status__in=["Aguardando Resposta", "Aceito", "Recusado", "Cancelado"]) | Q(sol_tipo="Coorientação", sol_status__in=["Aguardando Aceite", "Aceito", "Recusado", "Cancelado"])`), `uq_solicitacoes_orientacao_pedido_pendente` (`sol_tcc`, `condition=Q(sol_tipo__in=["Orientação", "Troca de Orientação"], sol_status="Aguardando Resposta")`); `ck_historico_status_tcc_hst_status_anterior` (aceita nulo), `ck_historico_status_tcc_hst_status_novo`, `ck_historico_status_tcc_hst_gatilho`; `ck_artigos_art_qualis_capes`, `ck_artigos_art_status_submissao`, `ck_artigos_art_homologacao` (todas aceitam nulo). — Rastreabilidade: [US-39][RBN-CAD-14.1][US-03][RBN-CAD-01.1][US-08][RBN-CAD-05.7][US-07][RBN-CAD-04.1][US-13][RBN-CAD-08.1][US-10][RBN-CAD-06.3][US-11][RBN-CAD-06.4][US-04][RBN-CAD-01.3][RBN-CAD-02.3][US-06][RBN-CAD-03.3][RBN-CAD-05.1][US-05][RBN-CAD-03.1][RBN-CAD-02.1][US-45][RBN-CAD-10.3][RBN-CAD-04.5][RBN-CAD-05.5][US-09][RBN-CAD-05.4][RBN-CAD-05.8][RBN-CAD-05.6][US-43][RBN-CAD-09.1][US-15][RBN-CAD-09.3][US-44][RBN-CAD-09.5][RBN-CAD-09.2][RBN-CAD-07.1][US-14][RBN-CAD-08.3][RBN-CAD-08.4][US-17][RBN-CAD-10.1][RBN-CAD-10.6][US-18][RBN-CAD-10.2][RBN-CAD-10.7][US-36][RBN-CAD-10.4][RBN-CAD-08.7][RBN-CAD-08.8][US-46][RBN-CAD-12.1][US-20][RBN-CAD-12.3][US-19][RBN-CAD-11.1][RBN-CAD-11.2][US-38][RBN-CAD-13.2][FR-006]–[FR-011]
- [ ] T029 [US2] Em `sigtcc/apps/cadastro/models.py`, sobrescrever `save()` de `Usuarios` e de `CoorientadoresExternos` para gravar `None` quando `usu_email`/`cext_email` for `""` ou só espaços (spec FR-007, cenário 11; research R3), com comentário avisando que `QuerySet.update()` e `bulk_create()` não passam pelo `save()` (contrato §3). — Rastreabilidade: [US-10][RBN-CAD-06.3][US-11][RBN-CAD-06.4][US-04][RBN-CAD-01.3][RBN-CAD-02.3][US-06][RBN-CAD-03.3][US-45][RBN-CAD-10.3][FR-007]
- [ ] T030 [P] [US2] Acrescentar `Meta.constraints` em `sigtcc/apps/defesa/models.py`, exatamente: `ck_criterios_cri_componente`, `ck_criterios_cri_peso` (`cri_peso__gte=0, cri_peso__lte=10`); `ck_ouvintes_ouv_matricula` (`ouv_matricula__regex=r"^[0-9]{10}$"`); `ck_defesas_def_formato`, `ck_defesas_def_status`, `ck_defesas_def_parecer` (aceita nulo), `ck_defesas_def_nota_final` (0 a 10 ou nulo); `ck_banca_defesa_ban_papel`; `ck_avaliacoes_ava_conceito`, `ck_avaliacoes_ava_nota` (`ava_nota__gte=0, ava_nota__lte=10`); `ck_historico_defesas_hdf_evento`, `ck_historico_defesas_hdf_status_anterior` e `ck_historico_defesas_hdf_status_novo` (ambas aceitam nulo). — Rastreabilidade: [US-25][RBN-DEF-04.1][RBN-DEF-04.2][US-30][RBN-DEF-08.2][US-21][RBN-DEF-01.1][US-24][RBN-DEF-01.2][US-27][RBN-DEF-06.3][RBN-DEF-06.4][US-28][RBN-DEF-07.1][US-23][RBN-DEF-02.1][RBN-DEF-02.2][US-26][RBN-DEF-05.2][RBN-DEF-08.4][US-40][RBN-DEF-01.6][RBN-DEF-03.3][FR-008][FR-010]
- [ ] T031 [US2] Gerar `sigtcc/apps/cadastro/migrations/0002_restricoes_cadastro.py` (`makemigrations cadastro --name restricoes_cadastro`) e `sigtcc/apps/defesa/migrations/0003_restricoes_defesa.py` (`makemigrations defesa --name restricoes_defesa`, que deve depender de `0002_fk_composta_avaliacoes`); a migração só pode conter `AddConstraint` (nenhuma alteração de campo); conferir com `sqlmigrate` os 50 nomes de restrição do data-model. — Rastreabilidade: [base de todas as US; sem RBN específica][modelos de T028 e T030]
- [ ] T032 [US2] Rodar `python manage.py migrate` e os testes de T025, T026 e T027 até passarem; rodar de novo `test_conformidade_dicionario` para confirmar que as restrições não mudaram colunas. — Rastreabilidade: [base de todas as US; sem RBN específica][spec US2][SC-002]

**Checkpoint**: US1 e US2 completas; toda restrição de FR-004 a FR-012 tem teste de recusa e de aceitação.

---

## Phase 5: User Story 3 - Domínios fixos disponíveis desde a instalação (Priority: P2)

**Goal**: após o `migrate`, `Cursos` (3), `Areas_Interesse` (10) e `Criterios` (9, descritores
"PROVISÓRIO") estão preenchidos; `Equivalencia_Cursos` está vazia; a carga é idempotente.

**Independent Test**: `python manage.py test sigtcc.apps.cadastro.tests.test_carga_inicial_cadastro
sigtcc.apps.defesa.tests.test_carga_criterios` passa (spec US3, cenários 1 a 5; SC-004, SC-005;
FR-013 a FR-017).

### Tests for User Story 3 ⚠️

- [ ] T033 [P] [US3] Criar `sigtcc/apps/cadastro/tests/test_carga_inicial_cadastro.py`: `test_cenario1_cursos` (exatamente "Engenharia de Computação", "Sistemas de Informação", "Licenciatura em Computação", com `cur_descricao` nulo); `test_cenario3_areas` (exatamente "Engenharia de Software", "Inteligência Artificial", "Redes de Computadores", "Banco de Dados", "Sistemas Embarcados", "Segurança da Informação", "Interação Humano-Computador", "Ciência de Dados", "Computação Gráfica", "Educação em Computação"); `test_cenario4_equivalencia_vazia` (0 linhas); `test_cenario5_reaplicacao` (chamar `cargas.carregar_cursos` e `cargas.carregar_areas_interesse` de novo com `django.apps.apps` não muda contagem nem identificadores); `test_fr017_nenhuma_outra_tabela_do_cadastro_com_dados` (todas as tabelas do app, exceto `Cursos` e `Areas_Interesse`, com 0 linhas). — Rastreabilidade: [US-39][RBN-CAD-14.1][US-13][RBN-CAD-08.1][US-08][RBN-CAD-05.7][spec US3 cenários 1, 3, 4, 5][FR-013][FR-015][FR-016][FR-017]
- [ ] T034 [P] [US3] Criar `sigtcc/apps/defesa/tests/test_carga_criterios.py`: `test_cenario2_nove_criterios` (exatamente, como (componente, nome, peso): ("Parte Escrita", "Relevância do Tema", 0.5), ("Parte Escrita", "Metodologia", 2.0), ("Parte Escrita", "Revisão da Literatura", 1.0), ("Parte Escrita", "Resultados e Discussões", 2.0), ("Parte Escrita", "Conclusões", 0.5), ("Parte Escrita", "Redação", 1.0), ("Parte Oral", "Organização", 1.0), ("Parte Oral", "Domínio do Assunto", 1.5), ("Parte Oral", "Postura perante a Banca", 0.5), comparando `Decimal`); `test_soma_dos_pesos` (7.0 na Parte Escrita, 3.0 na Parte Oral, 10.0 no total; SC-004); `test_descritores_provisorios` (os 27 descritores começam por "PROVISÓRIO", têm até 255 caracteres e são exatamente os três textos de T036; `cri_descricao` nulo; FR-014); `test_reaplicacao` (chamar `cargas.carregar_criterios_provisorios` de novo não duplica); `test_fr017_nenhuma_outra_tabela_do_defesa_com_dados` (todas as tabelas do app, exceto `Criterios`, com 0 linhas). — Rastreabilidade: [US-25][RBN-DEF-04.1][spec US3 cenários 2, 5][FR-014][FR-017]

### Implementation for User Story 3

- [ ] T035 [P] [US3] Criar `sigtcc/apps/cadastro/cargas.py` com as tuplas `CURSOS` e `AREAS_INTERESSE` (valores exatos de T033) e as funções `carregar_cursos(apps, schema_editor)` e `carregar_areas_interesse(apps, schema_editor)` (usam `apps.get_model("cadastro", ...)` e `get_or_create` pelo nome, sem informar identificador; [US-39][RBN-CAD-14.1][FR-013] e [US-13][RBN-CAD-08.1][FR-015]) e as reversas `remover_cursos` e `remover_areas_interesse` (apagam só esses nomes). Comentário no topo: mudanças futuras viram funções novas e migrações novas, nunca alteram as existentes (research D6). — Rastreabilidade: [US-39][RBN-CAD-14.1][US-13][RBN-CAD-08.1][FR-013][FR-015]
- [ ] T036 [P] [US3] Criar `sigtcc/apps/defesa/cargas.py` com a lista `CRITERIOS` (os 9 de T034, peso como `Decimal`) e os descritores provisórios exatos: Exemplar = `"PROVISÓRIO – Exemplar (nota de 8,0 a 10,0). Texto oficial pendente da planilha de avaliação da EST/UEA."`; Competente = `"PROVISÓRIO – Competente (nota de 6,0 a 7,9). Texto oficial pendente da planilha de avaliação da EST/UEA."`; Necessita de Trabalho = `"PROVISÓRIO – Necessita de Trabalho (nota de 0,0 a 5,9). Texto oficial pendente da planilha de avaliação da EST/UEA."` (travessão U+2013); função `carregar_criterios_provisorios(apps, schema_editor)` com `get_or_create(cri_nome=..., defaults={componente, peso, os 3 descritores, cri_descricao=None})` e reversa `remover_criterios` ([US-25][RBN-DEF-04.1][FR-014]; FR-014a: a troca pelos textos oficiais será uma migração nova antes do TP3). — Rastreabilidade: [US-25][RBN-DEF-04.1][FR-014]
- [ ] T037 [US3] Criar as data migrations do cadastro: `sigtcc/apps/cadastro/migrations/0003_carga_cursos.py` (`makemigrations cadastro --empty --name carga_cursos`; `RunPython(cargas.carregar_cursos, cargas.remover_cursos)`) e `sigtcc/apps/cadastro/migrations/0004_carga_areas_interesse.py` (`RunPython(cargas.carregar_areas_interesse, cargas.remover_areas_interesse)`). Nenhuma migração para `Equivalencia_Cursos` (FR-016). — Rastreabilidade: [US-39][RBN-CAD-14.1][US-13][RBN-CAD-08.1][FR-013][FR-015][FR-016]
- [ ] T038 [P] [US3] Criar `sigtcc/apps/defesa/migrations/0004_carga_criterios_provisorios.py` (`makemigrations defesa --empty --name carga_criterios_provisorios`; `RunPython(cargas.carregar_criterios_provisorios, cargas.remover_criterios)`). — Rastreabilidade: [US-25][RBN-DEF-04.1][FR-014]
- [ ] T039 [US3] Rodar `python manage.py migrate` e os testes de T033 e T034 até passarem; conferir `python manage.py migrate defesa 0003` e `python manage.py migrate cadastro 0002` (reversão das cargas) e voltar com `migrate`. — Rastreabilidade: [US-39][RBN-CAD-14.1][US-13][RBN-CAD-08.1][US-08][RBN-CAD-05.7][US-25][RBN-DEF-04.1][spec US3][SC-004][SC-005]

**Checkpoint**: as três histórias completas e testáveis de forma independente.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: qualidade, rastreabilidade e preparação do PR.

- [ ] T040 Conferir a rastreabilidade em `sigtcc/apps/cadastro/models.py` e `sigtcc/apps/defesa/models.py`: as 36 classes têm docstring com as tags da tabela **Rastreabilidade**; `fields.py`, `choices.py`, `managers.py`, `cargas.py` e cada arquivo de teste citam research, FR ou cenário (constituição, princípio II). — Rastreabilidade: [infraestrutura da feature 001, sem US específica]
- [ ] T041 Rodar `lint.bat` (ou os três comandos equivalentes fora do Windows) duas vezes seguidas: a segunda execução não altera nenhum arquivo e o flake8 termina sem erros em `sigtcc/` (constituição, princípio V; research R13). — Rastreabilidade: [infraestrutura da feature 001, sem US específica]
- [ ] T042 Rodar a suíte completa `python manage.py test sigtcc.apps.cadastro sigtcc.apps.defesa` em banco de teste novo; todos os testes passam. — Rastreabilidade: [infraestrutura da feature 001, sem US específica]
- [ ] T043 Executar o roteiro de `specs/001-modelo-dados/quickstart.md` do zero (banco vazio): medir o tempo de `migrate` (menos de 1 minuto, SC-003), rodar as consultas da seção 3 e a reversão da seção 6 (`migrate defesa zero` e `migrate cadastro zero`); corrigir o quickstart se algum resultado esperado estiver diferente. — Rastreabilidade: [infraestrutura da feature 001, sem US específica][FR-018][SC-003]
- [ ] T044 Atualizar `CHANGELOG.md` com o que foi entregue (36 tabelas, 50 restrições, cargas de Cursos, Areas_Interesse e Criterios provisórios) e com as pendências do plano (descritores oficiais antes do TP3, códigos de curso, consulta à Maria Luiza). — Rastreabilidade: [infraestrutura da feature 001, sem US específica]
- [ ] T045 Preparar o texto do PR em `specs/001-modelo-dados/pr-feat-01.md` com o template do PGCS 6.3, título `[Feat-01] Modelo de dados do SIGTCC (US-03, US-07, US-08, US-13, US-25, US-39)`, usando o agente `revisor-pgcs` para o checklist (lint, migrações no mesmo PR, `.env` e `media/` fora do Git, rastreabilidade) e listando os itens de configuração para revisão do Célio (plan.md, seção Pendências). Não fazer `git push` nem abrir o PR sem pedido da responsável. — Rastreabilidade: [infraestrutura da feature 001, sem US específica]

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências. T006–T008 em sequência (o settings referencia os apps);
  T002–T005, T009 e T010 em paralelo.
- **Foundational (Phase 2)**: depende do Setup; bloqueia as três histórias.
- **US1 (Phase 3)**: depende da Foundational.
- **US2 (Phase 4)**: depende da US1 (as restrições são acrescentadas aos modelos e a migração
  `0002_restricoes_cadastro`/`0003_restricoes_defesa` segue as da US1).
- **US3 (Phase 5)**: depende da US1 (modelos `Cursos`, `AreasInteresse`, `Criterios`) e da US2
  (as data migrations `cadastro/0003`, `cadastro/0004` e `defesa/0004` vêm depois das migrações de
  restrição na cadeia de cada app). **A ordem US1 → US2 → US3 é obrigatória**; a numeração da
  tabela "Migrações desta feature" vale só para essa ordem.
- **Polish (Phase 6)**: depende das histórias concluídas.

### User Story Dependencies

- **US1 (P1)**: independente; é o MVP.
- **US2 (P1)**: precisa dos modelos da US1; seus testes não dependem da US3.
- **US3 (P2)**: implementada depois da US2 (cadeia de migrações); seus testes não verificam
  nenhuma restrição da US2.

### Within Each User Story

- Testes escritos antes e falhando; depois modelos, migrações e execução.
- `sigtcc/apps/cadastro/models.py` é um arquivo só: T017 → T018 → T019 (US1) e T028 → T029 (US2)
  são sequenciais.

### Parallel Opportunities

- Setup: T002, T003, T004, T005, T009, T010.
- Foundational: T012 e T013 (depois de T011 ou junto, arquivos diferentes).
- US1: T020 (defesa) em paralelo com T017–T019 (cadastro).
- US2: T025, T026 e T027 em paralelo (depois de T024); T030 em paralelo com T028–T029.
- US3: T033, T034, T035, T036 em paralelo; T038 em paralelo com T037.

---

## Parallel Example: User Story 2

```bash
# Depois de T024 (fábricas), os três arquivos de teste em paralelo:
Task: "T025 test_restricoes_cadastro.py"
Task: "T026 test_restricoes_defesa.py"
Task: "T027 test_usuarios.py"

# Restrições dos dois apps em paralelo:
Task: "T028 Meta.constraints em sigtcc/apps/cadastro/models.py"
Task: "T030 Meta.constraints em sigtcc/apps/defesa/models.py"
```

## Parallel Example: User Story 3

```bash
Task: "T033 test_carga_inicial_cadastro.py"
Task: "T034 test_carga_criterios.py"
Task: "T035 sigtcc/apps/cadastro/cargas.py"
Task: "T036 sigtcc/apps/defesa/cargas.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Fases 1 e 2 (projeto, campos e domínios).
2. Fase 3 (US1): as 36 tabelas conferidas contra o dicionário.
3. **Parar e validar**: `test_conformidade_dicionario` verde. Commit sugerido:
   `feat(feat-01): criar modelos das 36 tabelas do dicionario`.

### Incremental Delivery

1. US1 → commit da estrutura (MVP).
2. US2 → commit `feat(feat-01): adicionar restricoes do dicionario no banco`.
3. US3 → commit `feat(feat-01): carregar dominios fixos e criterios provisorios`.
4. Polish → `docs(feat-01): atualizar changelog e readme do modelo de dados`.

### Parallel Team Strategy

Com mais de uma pessoa (sob a responsabilidade da Julia Cohen): uma pessoa nos modelos e testes do
`cadastro`, outra nos do `defesa`, sincronizando nas tarefas de migração (T021, T031, T037, T038).

---

## Notes

- [P] = arquivos diferentes, sem dependência de tarefa incompleta.
- Nenhuma tarefa cria tela, formulário, view ou regra de aplicação (spec FR-019).
- Migrações desta feature podem ser regeneradas enquanto não estiverem na `develop`; depois do merge,
  nunca apagar nem reescrever (PGCS 6.2).
- Pendências fora desta feature (US-03, US-11, Maria Luiza, Célio, TP3) estão na seção
  "Pendências" do [plan.md](plan.md).
- **FR-014a e SC-007 não são entregues por estas tarefas.** Responsável: Julia Cohen. Prazo: antes
  do TP3 (18/11/2026). Entrega: uma data migration (carga) nova,
  `sigtcc/apps/defesa/migrations/00NN_descritores_oficiais.py`, que troca os 27 descritores pelos
  textos da planilha oficial de avaliação da EST/UEA sem mudar nome, componente, peso nem
  identificador; mais um teste que confirme 0 descritores com "PROVISÓRIO". Depende de a planilha
  ser colocada em `docs/fonte/`.
- O mesmo vale para os códigos de curso da UEA (FR-016): data migration (carga) nova
  `sigtcc/apps/cadastro/migrations/00NN_carga_equivalencia_cursos.py` quando houver código
  confirmado.
