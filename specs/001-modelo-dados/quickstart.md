# Quickstart: validar o modelo de dados

**Feature**: [spec.md](spec.md) | **Modelo**: [data-model.md](data-model.md)

Guia para provar, em um ambiente limpo, que a base do SIGTCC confere com o dicionário e que a carga
inicial está correta. Não contém código de implementação.

## Pré-requisitos

- Python 3.12 e PostgreSQL 16 instalados.
- Um usuário do PostgreSQL com permissão `CREATEDB` (o `manage.py test` cria o banco de teste).
- Repositório na branch da feature (`feature/feat-01-modelo-de-dados`).

## 1. Preparar o ambiente

Windows (padrão do PGCS 3.1):

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

macOS/Linux: `python3.12 -m venv venv`, `source venv/bin/activate`, `cp .env.example .env`.

Preencher no `.env`: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`,
`DB_HOST`, `DB_PORT` e `CACHE_DIR`.

```bash
createdb sigtcc        # ou pelo pgAdmin, com o nome usado em DB_NAME
```

## 2. Criar a base e aplicar a carga (US1, US3; SC-003)

```bash
python manage.py check
python manage.py migrate
```

Esperado: `check` sem erros; `migrate` aplica `cadastro` 0001 a 0004 (`0002_restricoes_cadastro`,
`0003_carga_cursos`, `0004_carga_areas_interesse`) e `defesa` 0001 a 0004
(`0002_fk_composta_avaliacoes`, `0003_restricoes_defesa`, `0004_carga_criterios_provisorios`) sem
intervenção, em menos de 1 minuto.

## 3. Conferir no banco

```bash
python manage.py dbshell
```

| Consulta | Esperado |
|---|---|
| `SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_name NOT LIKE 'django\_%' AND table_name NOT LIKE 'auth\_%';` | 36 |
| `SELECT column_name FROM information_schema.columns WHERE table_name='Usuarios' ORDER BY ordinal_position;` | as 6 colunas do dicionário, sem `last_login`, `is_staff`, `is_superuser` |
| `SELECT count(*) FROM information_schema.columns WHERE table_schema='public' AND data_type='timestamp without time zone';` | 21 |
| `SELECT count(*) FROM information_schema.columns WHERE table_schema='public' AND data_type='timestamp with time zone' AND table_name NOT LIKE 'django\_%';` | 0 |
| `SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname='fk_avaliacoes_banca_defesa';` | `FOREIGN KEY (ava_def_id, ava_usu_id) REFERENCES "Banca_Defesa"(ban_def_id, ban_usu_id) DEFERRABLE INITIALLY DEFERRED` |
| `SELECT cur_nome FROM "Cursos" ORDER BY cur_nome;` | 3 cursos |
| `SELECT count(*) FROM "Areas_Interesse";` | 10 |
| `SELECT cri_componente, sum(cri_peso) FROM "Criterios" GROUP BY 1;` | Parte Escrita 7.0; Parte Oral 3.0 |
| `SELECT count(*) FROM "Criterios" WHERE cri_desc_exemplar LIKE 'PROVISÓRIO%';` | 9 (até a troca de FR-014a) |
| `SELECT count(*) FROM "Equivalencia_Cursos";` | 0 |

Os nomes de tabela levam aspas duplas porque têm maiúsculas (research R2).

## 4. Rodar os testes (US1, US2, US3; SC-001, SC-002, SC-004, SC-005, SC-006)

```bash
python manage.py test sigtcc.apps.cadastro sigtcc.apps.defesa
```

Esperado: todos passam. Os grupos de teste são:

| Grupo | Prova |
|---|---|
| Conformidade com o dicionário | lê `docs/fonte/Modelo_Logico_e_Dicionario_18_10.md` e compara as 36 tabelas e as 201 colunas (tipo, tamanho, nulidade, PK) com o banco, ignorando índices (SC-001, SC-006) |
| Restrições | um teste de recusa e um de aceitação para cada domínio, unicidade e restrição condicional (US2; SC-002) |
| Carga inicial | conteúdo das 4 tabelas e reaplicação sem duplicar (US3; SC-004, SC-005) |
| Usuário | `create_user`, senha nula, `is_active` derivado do status, `str()` com o nome (contrato, seção 3) |
| E-mail vazio | `usu_email` e `cext_email` gravados com `""` ficam `NULL` no banco; dois Alunos criados por `create_user` sem e-mail coexistem (US2, cenários 7 e 11) |
| Padrões, chaves compostas e exclusão | `not_lida` grava `false` quando omitido (FR-012); duplicata recusada nas 5 PKs compostas (FR-004); `DELETE` por SQL de linha referenciada recusado pelo banco (FR-005) |

## 5. Qualidade (constituição, princípio V)

```bat
lint.bat
```

Esperado: isort, black e flake8 sem erros (linha de 100, migrações excluídas do flake8). Rodar
duas vezes seguidas não deve alterar nenhum arquivo na segunda execução (`pyproject.toml` e
`.flake8`, research R13).

## 6. Reverter (opcional)

```bash
python manage.py migrate defesa zero
python manage.py migrate cadastro zero
```

Esperado: as cargas e a FK composta são desfeitas sem erro (migrações reversíveis).
