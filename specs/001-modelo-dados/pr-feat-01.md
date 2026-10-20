# [Feat-01] Modelo de dados do SIGTCC (US-03, US-07, US-08, US-13, US-25, US-39)

**Origem**: `feature/feat-01-modelo-de-dados` → **Destino**: `develop` (merge `--no-ff`, PGCS 6.4)

**Spec**: `specs/001-modelo-dados/` (spec.md, plan.md, research.md, data-model.md, contracts/modelos-orm.md, quickstart.md, tasks.md)

**Responsável**: Julia Cohen

### 1. Resumo da Alteração

Cria o projeto Django do SIGTCC na estrutura do PGCS 2.3 e implementa no PostgreSQL 16 o modelo de dados do dicionário de 18/10 (atividade 3.2 do cronograma, TP2). Não há telas nem regras de aplicação (FR-019).

- **Projeto**: Django 5.2.18 com Python 3.12, apps `cadastro` (Épico 1), `defesa` (Épico 2) e `relatorios` (Épico 3, sem modelos), configuração por `.env` (python-dotenv), `USE_TZ = False` com `TIME_ZONE = "America/Manaus"`, `AUTH_USER_MODEL = cadastro.Usuarios` e cache em arquivo (`CACHE_DIR`) para o futuro bloqueio de login (US-11).
- **36 tabelas e 201 colunas** do dicionário, com `db_table`/`db_column` iguais ao documento: 27 no `cadastro` e 9 no `defesa`. Tipos, tamanhos, nulidade, PKs simples e compostas (`CompositePrimaryKey`) e FKs conforme o modelo lógico. `CHAR(10)` das matrículas por `CharFixoField` e `TIMESTAMP` sem fuso nas 21 colunas por `TimestampField`. Sem Salas: o local da defesa presencial é `Defesas_Presenciais.dep_local`.
- **49 restrições nomeadas**: 48 CHECKs e unicidades, inclusive parciais (`0002_restricoes_cadastro` e `0003_restricoes_defesa`), e a FK composta `Avaliacoes` → `Banca_Defesa` (`fk_avaliacoes_banca_defesa`) por `RunSQL` em migração própria (`defesa/0002_fk_composta_avaliacoes`). FKs `DEFERRABLE INITIALLY DEFERRED`, sem exclusão em cascata. Os domínios de status vêm de 26 `TextChoices` iguais ao `Glossario_Status` da matriz de 17/10.
- **Cargas iniciais** (data migrations idempotentes e reversíveis): 3 cursos (Engenharia de Computação, Sistemas de Informação, Licenciatura em Computação), 10 Áreas de Interesse e os 9 critérios oficiais de avaliação (Parte Escrita 7,0 + Parte Oral 3,0) com descritores iniciados por "PROVISÓRIO". `Equivalencia_Cursos` fica vazia até haver código confirmado.
- **53 testes automatizados** contra PostgreSQL: conformidade com o dicionário (o teste lê `docs/fonte/Modelo_Logico_e_Dicionario_18_10.md`), recusa e aceitação de cada restrição, modelo de usuário (senha nula, e-mail vazio gravado como `NULL`) e cargas iniciais.

### 2. Rastreabilidade com o Projeto

* Feature Impactada: Feature 01 - Modelo de dados do SIGTCC (base de todas as features dos três épicos)
* Histórias de Usuário Atendidas: US-03, US-07, US-08, US-13, US-25, US-39 (carga e estrutura: [US-39][RBN-CAD-14.1] Cursos, [US-08][RBN-CAD-05.7] Equivalencia_Cursos, [US-25][RBN-DEF-04.1] Criterios, [US-13][RBN-CAD-08.1] Areas_Interesse, [US-03][RBN-CAD-01.1] Docentes/Coordenadores, [US-07][RBN-CAD-04.1] Disciplinas/Turmas). Cada uma das 36 classes de modelo cita as US e os RBN da tabela que implementa.
* Requisitos da spec 001: FR-001 a FR-020; SC-001 a SC-007.
* Cartão no Trello: [preencher: atividade 3.2 – Modelo físico de dados / implementação do modelo de dados]

**Commits deste PR**

| Commit | Mensagem |
|---|---|
| d38ee91 | chore(feat-01): configurar projeto django na estrutura do pgcs |
| c3aa8c0 | feat(feat-01): adicionar campos char e timestamp e dominios de status |
| f608690 | feat(feat-01): criar modelos das 36 tabelas do dicionario |
| 5f1b136 | feat(feat-01): adicionar restricoes do dicionario no banco |
| 8b1d5e9 | feat(feat-01): carregar dominios fixos e criterios provisorios |
| bd8cde8 | fix(feat-01): reverter cargas iniciais por sql nas migracoes |
| 67ee8e5 | docs(feat-01): adicionar rastreabilidade nas migracoes geradas |
| (último) | docs(feat-01): registrar entrega no changelog e texto do pr |

Atenção: a `develop` ainda não tem a `feature/feat-00-spec-kit`. Por isso este PR também leva `f4657a1` (spec kit, agentes e constituição), `09412c6` (matriz de 17/10), `f97bbd7` (protótipo de 17/10, mesmo conteúdo do `672480e` da feat-00) e `cd12dc6` (spec e plano da feat-01). [Remover este aviso se o PR da feat-00 entrar antes.]

### 3. Checklist Técnico da Equipe (Definition of Done)

- [x] O código foi verificado e aprovado localmente pelo script `lint.bat` (Flake8, Black e isort). Equivalente fora do Windows: `isort --check-only sigtcc/` sem erros, `black --check sigtcc/` com "39 files would be left unchanged" e `flake8 sigtcc/` sem erros. A configuração está em `pyproject.toml` e `.flake8`, com linha de 100.
- [x] Não há variáveis, imports ou trechos de código não utilizados (flake8 limpo).
- [x] As migrações do PostgreSQL foram criadas, aplicadas e testadas com sucesso. `makemigrations --check --dry-run` responde "No changes detected"; `cadastro` 0001–0004 e `defesa` 0001–0004 aplicam num banco vazio em 0,76 s (SC-003: menos de 1 minuto); `migrate defesa zero` e `migrate cadastro zero` revertem sem erro (T043).
- [x] O arquivo `.env` e arquivos da pasta `media/` NÃO foram adicionados ao Git (`git ls-files` só tem `.env.example`; `.env`, `venv/`, `/cache/` e `sigtcc/media/` estão no `.gitignore`).
- [ ] ~~A interface segue a paleta e os padrões de usabilidade estabelecidos na ISO/IEC 25010.~~ Não se aplica: a feature não tem telas (FR-019).
- [ ] ~~Não há quebras de layout ou erros acusados no console do navegador.~~ Não se aplica: a feature não tem telas.

### 4. Evidência da Validação Manual (Critérios de Aceite das USs)

Suíte completa: `python manage.py test sigtcc.apps.cadastro sigtcc.apps.defesa --noinput` → `Ran 53 tests ... OK`. Roteiro `specs/001-modelo-dados/quickstart.md` executado do zero, num banco separado (T043).

**US1 – Estrutura das 36 tabelas conforme o dicionário**
- [x] Cenário 1: existem exatamente as 36 tabelas do dicionário e nenhuma de Salas (`test_cenario1_36_tabelas_sem_salas`, `test_sem_tabelas_fora_do_dicionario`)
- [x] Cenário 2: `TCCs` com as 11 colunas, tipos, tamanhos e nulidade do dicionário; as 201 colunas são conferidas pelo arquivo do dicionário (`test_cenario2_colunas_conforme_dicionario`)
- [x] Cenário 3: PK composta de `Avaliacoes` e FK composta para `Banca_Defesa` (`test_cenario3_avaliacoes`)
- [x] Cenário 4: PK de `Alunos`, `Docentes`, `MembrosExternos` e `Secretarios` é também FK para `Usuarios.usu_id` (`test_cenario4_especializacoes`)
- [x] Cenário 5: identificador gerado pela identidade BY DEFAULT (`test_cenario5_identidade_by_default`)

**US2 – Integridade garantida pelo próprio banco**
- [x] Cenário 1: `tcc_status` = 'Finalizado' recusado
- [x] Cenário 2: título, resumo e modalidade obrigatórios fora de 'Sem Proposta'
- [x] Cenário 3: uma única orientação 'Ativa' por TCC
- [x] Cenário 4: uma entrega de cada tipo por turma ('Outra' repetível)
- [x] Cenário 5: coorientação com docente ou externo, nunca os dois nem nenhum
- [x] Cenário 6: status da solicitação compatível com o tipo
- [x] Cenário 7: vários usuários sem e-mail aceitos; e-mail preenchido duplicado recusado
- [x] Cenário 8: `tur_hora_termino` posterior a `tur_hora_inicio`
- [x] Cenário 9: nota de avaliação fora de 0,0–10,0 recusada
- [x] Cenário 10: FK para registro inexistente recusada
- [x] Cenário 11: e-mail igual a texto vazio gravado como `NULL` (`Usuarios` e `CoorientadoresExternos`)
- [x] Extras: domínios e unicidades de todas as tabelas, PKs compostas, exclusão protegida e `not_lida` com padrão falso (FR-004, FR-005 e FR-012)

**US3 – Domínios fixos disponíveis desde a instalação**
- [x] Cenário 1: exatamente os 3 cursos do NUCOMP
- [x] Cenário 2: 9 critérios com pesos 7,0 + 3,0 e descritores "PROVISÓRIO"
- [x] Cenário 3: as 10 Áreas de Interesse
- [x] Cenário 4: `Equivalencia_Cursos` existe e está vazia
- [x] Cenário 5: reaplicar a carga não duplica nem altera registros

### Decisões e desvios registrados

| Decisão | Registro | Situação |
|---|---|---|
| Identidade `GENERATED BY DEFAULT AS IDENTITY` em vez de `ALWAYS` (o dicionário pede `ALWAYS`). `ALWAYS` recusa qualquer valor informado e quebra fixtures, `loaddata` e partes do framework. Nenhum código informa identificador. | research D4; spec FR-003 e Clarifications; plan, Complexity Tracking | Aceito por Julia Cohen; **falta consultar Maria Luiza e registrar no dicionário** |
| Ordem física das colunas: o Django põe as FKs no fim, e em 21 das 36 tabelas a ordem difere do dicionário. Nomes, tipos, tamanhos, nulidade e chaves conferem; o teste compara por nome. | research R14 | Decidido em 2026-10-19 (T023); informar Maria Luiza |
| Senha nula tratada em `Usuarios`: a conta 'Aguardando Ativação' tem `usu_senha` nula. `has_usable_password()` devolve falso e `check_password()` não confere nenhuma senha (o Django levantaria `TypeError`). `create_user` sem senha grava `NULL`; a senha só é guardada como hash. | research D1; `sigtcc/apps/cadastro/models.py`, `managers.py` | Implementado e testado (`test_usuarios.py`) |
| Reversão das cargas iniciais por SQL: o `delete()` do ORM com modelos históricos falhava ao reverter `0003_carga_cursos` (OneToOneField de `Coordenadores`) no `migrate cadastro zero`. As reversões passam a apagar por SQL; as FKs do banco continuam protegendo linhas referenciadas. | commit bd8cde8; encontrado na T043 | Corrigido |
| FK composta `Avaliacoes` → `Banca_Defesa` por `RunSQL`, já que o Django 5.2 não relaciona com modelo de PK composta | research D3; plan, Complexity Tracking | Em migração própria, escrita à mão |
| `TimestampField` próprio com `USE_TZ = False` (o `DateTimeField` geraria `timestamptz`) | research R1 (achado B1) | Aprovado |
| `Usuarios` sem colunas extras (sem `last_login`, `is_staff`, `is_superuser`), sem Admin e sem `createsuperuser` | research D1 | Aprovado; contas iniciais por comando de gestão na US-03 |

### Itens de configuração para revisão do Célio Benjamim (constituição, princípio IX)

- [ ] `requirements.txt`: versões exatas do `pip freeze` de 2026-10-19 (Django 5.2.18, psycopg 3.3.6, python-dotenv, black, isort, flake8)
- [ ] `sigtcc/settings.py`: `.env` via python-dotenv, PostgreSQL, `AUTH_USER_MODEL`, `USE_TZ = False`, `TIME_ZONE = "America/Manaus"`, `DEFAULT_AUTO_FIELD = AutoField`, `CACHES` em arquivo
- [ ] `.gitignore`: entrada `/cache/` adicionada (bloqueio de login, research D2)
- [ ] `.env.example`: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DB_*`, `CACHE_DIR`
- [ ] `lint.bat`: **caminho corrigido** de `apps/sigtcc/` para `sigtcc/` (research R12). As opções de linha passaram para os arquivos de configuração.
- [ ] `pyproject.toml` (novo): black e isort com linha de 100, `profile = "black"`, `known_first_party = ["sigtcc"]` (research R13)
- [ ] `.flake8` (novo): `max-line-length = 100`, `extend-ignore = E203, W503`, `exclude = migrations, venv, .venv` (research R13)
- [ ] `CHANGELOG.md`: entrada da entrega e pendências
- [ ] Módulos fora da árvore do PGCS 2.3: `cadastro/choices.py` e `defesa/choices.py` (TextChoices, D7), `cadastro/fields.py` (R1, R4), `cadastro/managers.py` (D1), `cadastro/cargas.py` e `defesa/cargas.py` (D6) e as pastas `tests/` dos apps. Também `manage.py` na raiz, que a árvore do PGCS não lista mas o próprio PGCS usa.
- [ ] **Confirmar o nome da branch** `feature/feat-01-modelo-de-dados`: o PGCS 4.3 lista a feat-01 como `feature/feat-01-usuarios`

### Pendências (plan.md, "Pendências para outras features e pessoas")

| Pendência | Destino |
|---|---|
| Criar as contas iniciais de Coordenador de Curso (Engenharia de Computação, Sistemas de Informação, Licenciatura em Computação) na implantação, por comando de gestão, já que não há `createsuperuser` (RAN-CAD-01; primeiro acesso por RBN-CAD-06.2) | US-03 |
| Contagem de tentativas e mensagem de bloqueio (RBN-CAD-06.6) sobre o cache configurado aqui | US-11 |
| Backend de autenticação por matrícula ou e-mail | US-11 |
| Consultar Maria Luiza Guimarães e registrar no dicionário: (a) identidade BY DEFAULT (D4); (b) restrições descritas só em texto e aprovadas como CHECK (FR-008 e FR-010): matrícula com 10 dígitos, `tur_ano` com 4 dígitos, `tur_semestre` 1 ou 2, faixas de 0,0 a 10,0 (`cri_peso`, `ava_nota`, `def_nota_final`) e domínios de `hst_status_*`/`hdf_status_*`; (c) se o dicionário passa a exigir `CHECK (usu_email <> '')` (R3); (d) ordem física das colunas (R14) | Julia Cohen / Maria Luiza Guimarães |
| Redação do FR-007: sem `CHECK` no banco, a garantia de "e-mail vazio nunca gravado" vale só para `save()` e `create_user` (`update()` e `bulk_create()` não passam por eles). Com o CHECK, mantém o FR-007; sem ele, ajusta a redação. | Julia Cohen / Maria Luiza Guimarães |
| Revisar no PR o caminho do `lint.bat`, `pyproject.toml`, `.flake8`, `CHANGELOG.md` e os módulos fora da árvore do PGCS 2.3 | Célio Benjamim |
| Descritores oficiais dos critérios por data migration antes do TP3, 18/11/2026 (FR-014a, SC-007) | Julia Cohen |
| Códigos de curso da UEA em `Equivalencia_Cursos` por data migration quando confirmados no Lyceum ou com a Secretaria (FR-016) | Julia Cohen |
| Confirmar a branch `feature/feat-01-modelo-de-dados` | Célio Benjamim |
| Confirmar com a Product Owner se o aluno que desiste antes de salvar a Proposta aparece como Desistente no relatório de evasão (RBN-REL-02.3). Não muda esta feature; se a resposta for "sim", a mudança começa pela spec. | Julia Cohen / Profa. Diana |

### 5. Revisão por Pares (Peer Review)

* Revisor Designado: [preencher: integrante da equipe] (itens de configuração: Célio Benjamim)
* Parecer do Revisor:

[ ] Aprovado integralmente para merge

[ ] Solicitação de ajustes (detalhar nos comentários)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
