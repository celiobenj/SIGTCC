# Research: Modelo de dados do SIGTCC

**Feature**: [spec.md](spec.md) | **Plano**: [plan.md](plan.md) | **Data**: 2026-10-19

Cada item segue o formato Decisão / Justificativa / Alternativas. Os itens D1 a D7 são as decisões
informadas pela responsável no `/speckit-plan`; os itens R1 a R13 são consequências técnicas
levantadas no planejamento para cumprir o dicionário "exatamente" (FR-002); R14 foi decidido na
implementação. Revisado em 2026-10-19
após a revisão do agente `arquiteto-django` (achados B1, I1–I4 e M1–M9, aplicados com aprovação de
Julia Cohen).

---

## D1. `Usuarios` como modelo de usuário do Django, sem colunas extras

**Status**: aprovada em 2026-10-19, sem Admin e sem `createsuperuser`.

**Decisão**: `Usuarios` é o `AUTH_USER_MODEL` (`cadastro.Usuarios`), herdando só de
`AbstractBaseUser` (sem `PermissionsMixin`).

- `USERNAME_FIELD = "usu_email"`, `EMAIL_FIELD = "usu_email"`, `REQUIRED_FIELDS = ["usu_nome"]`.
- O atributo de senha continua se chamando `password` (é o nome que `set_password` e
  `check_password` usam), mas com `db_column="usu_senha"`, `max_length=255` e `null=True`.
- `last_login = None` na classe remove a coluna herdada. Sem `PermissionsMixin`, não existem
  `is_superuser`, `is_staff`, nem as tabelas de grupos e permissões do usuário.
- `is_active` é uma propriedade Python (sem coluna): verdadeira só quando `usu_status == "Ativa"`.
  Assim o `ModelBackend` recusa contas 'Aguardando Ativação', 'Inativa' e 'Expirada'.
- Gerenciador próprio (`UsuariosManager(BaseUserManager)`) com `create_user`; sem
  `create_superuser` nesta feature.
- `__str__` retorna `usu_nome`. O padrão de `AbstractBaseUser` retorna o `USERNAME_FIELD`, que é
  nulo para o Aluno antes do primeiro acesso, e `str(usuario)` levantaria `TypeError`.

**Justificativa**: atende FR-002 e FR-020 sem nenhuma coluna técnica extra em `Usuarios` (6 colunas,
iguais ao dicionário). O Django só conecta o sinal que grava `last_login` quando esse atributo é um
campo; com `None`, o sinal não é registrado. Com `usu_email` `unique=True` (ver R3), a verificação
`auth.E003` passa.

**Alternativas**: manter `AbstractUser` (cria ~10 colunas fora do dicionário); tabela de usuário
própria do Django + `Usuarios` separada (duplica identidade e senha).

**Consequências para outras features**:
- O Django Admin exige `is_staff` e `has_perm`; ele não fica disponível para `Usuarios` nesta
  feature. Se a equipe quiser o Admin, a feature que precisar define propriedades derivadas dos
  papéis (sem coluna).
- `createsuperuser` não é usado. A criação das contas iniciais de Coordenador de Curso de EC, SI
  e LC na implantação (RAN-CAD-01, Instalabilidade) fica para a US-03, por comando de gestão
  (pendência registrada no plan.md).
- O login por matrícula (Alunos) exigirá um backend de autenticação próprio na feature de login
  (US-11).

## D2. Bloqueio por tentativas (RBN-CAD-06.6) no cache, sem colunas novas

**Status**: aprovada em 2026-10-19 (só a configuração do cache nesta feature).

**Decisão**: o contador de tentativas e o bloqueio de 15 minutos ficam no cache do Django
(`FileBasedCache`), com a chave por `usu_id` (por exemplo `login_falhas:<usu_id>`), para valer
para qualquer credencial (matrícula ou e-mail). A pasta do cache vem do `.env` (`CACHE_DIR`) e
fica no `.gitignore`.

**Escopo nesta feature**: só a configuração `CACHES` em `settings.py`, a variável no
`.env.example` e a regra no `.gitignore`. A lógica de contagem e a mensagem são da feature de login
(US-11).

**Justificativa**: o dicionário (seção 4, item 1) já prevê "controle em cache com expiração
automática"; nenhuma coluna nova em `Usuarios`. O cache em arquivo persiste entre reinícios do
servidor (diferente do `LocMemCache`) e não exige serviço extra.

**Alternativas**: `django-axes` (cria tabelas próprias de tentativas, fora do dicionário); colunas
em `Usuarios` (violam FR-002); Redis/Memcached (serviço extra para um sistema pequeno).

**Limitações aceitas**: o `FileBasedCache` não faz incremento atômico; com o volume esperado
(dezenas de usuários simultâneos), uma tentativa a mais contada em uma corrida rara é aceitável.
Tentativas com credencial inexistente não têm `usu_id` e não geram bloqueio (não há conta a
bloquear).

## D3. Chaves compostas com `CompositePrimaryKey`; FK composta por `RunSQL`

**Decisão**:
- `Alunos_Turmas`, `PalavrasChave_TCC`, `Banca_Defesa`, `Presenca_Ouvintes` e `Avaliacoes` usam
  `models.CompositePrimaryKey(...)` (Django 5.2).
- O campo se chama obrigatoriamente `pk` (`pk = models.CompositePrimaryKey(...)`) e recebe os
  nomes de coluna (`attname`, por exemplo `"ava_def_id"`), como no exemplo da documentação do
  Django 5.2. Confirmar o SQL gerado com `sqlmigrate` na implementação.
- A FK composta `Avaliacoes(ava_def_id, ava_usu_id)` → `Banca_Defesa(ban_def_id, ban_usu_id)` é
  criada por `migrations.RunSQL` (com `reverse_sql`) numa migração própria do app `defesa`,
  `0002_fk_composta_avaliacoes`, escrita à mão. Assim ela não some se a `0001_initial` for gerada
  de novo antes do merge. O SQL é `ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED`, igual ao
  comportamento das FKs criadas pelo Django (R5); o texto exato está no data-model.
- No ORM, `ava_def` e `ava_usu` são `ForeignKey` para `Defesas` e `Usuarios` com
  `db_constraint=False` (navegação sem criar FKs simples que o dicionário não tem); `ava_def` também
  com `db_index=False`, porque o prefixo da PK já indexa a coluna. `ava_cri` é FK normal para
  `Criterios`.
- Como o ORM não conhece a FK composta, excluir uma `BancaDefesa` com avaliações não levanta
  `ProtectedError`: o banco recusa com `IntegrityError` no fim da transação. O `PROTECT` de
  `ava_def` e `ava_usu` só age no ORM (sem FK simples no banco).

**Justificativa**: o Django 5.2 cria chaves primárias compostas, mas não permite relacionamento
apontando para um modelo com chave composta. O `RunSQL` cria exatamente a restrição do dicionário.

**Alternativas**: `id` artificial + `UniqueConstraint` (cria coluna fora do dicionário); FKs simples
para `Defesas` e `Usuarios` (restrições diferentes das do dicionário e não impedem avaliação de quem
não é da banca).

**Limitações aceitas**: o Django Admin não suporta modelos com chave composta; o `pk` é uma tupla.
Nomes de tabela em SQL bruto precisam de aspas (`"Avaliacoes"`), ver R2.

**A verificar na feature que usar**: `ModelForm`, `bulk_update` e a biblioteca de auditoria
(dicionário, seção 4, item 5, por exemplo django-simple-history, que depende de content types) em
modelos com chave composta. Não há garantia nesta feature.

## D4. Identidade "BY DEFAULT" em vez de "ALWAYS"

**Decisão**: aceitar o `AutoField` do Django, que no PostgreSQL gera
`integer GENERATED BY DEFAULT AS IDENTITY`. `DEFAULT_AUTO_FIELD = "django.db.models.AutoField"`
(inteiro de 32 bits, igual ao `INT` do dicionário; `BigAutoField` geraria `bigint`).

**Justificativa**: `ALWAYS` faz o banco recusar qualquer valor informado, o que quebra fixtures,
`loaddata` e partes do próprio framework. A spec foi ajustada (FR-003, Clarifications de
2026-10-19): a carga e o código não informam identificadores, então a sequência nunca colide.

**Alternativas**: `RunSQL` alterando cada coluna para `ALWAYS` (36 alterações manuais e
incompatibilidade com ferramentas do framework).

**Pendente**: consultar Maria Luiza Guimarães e registrar o desvio no dicionário.

## D5. `db_table` e `db_column` iguais ao dicionário

**Decisão**: todo modelo tem `Meta.db_table` com o nome exato do dicionário (`"Cursos"`,
`"Equivalencia_Cursos"`, …) e toda coluna tem o nome exato. Convenção dos atributos Python
(detalhes em [contracts/modelos-orm.md](contracts/modelos-orm.md)):
- campo comum: atributo = nome da coluna (`tcc_titulo`);
- chave estrangeira: atributo = nome da coluna sem o sufixo `_id`, com `db_column` explícito
  (`tcc_alu` → coluna `tcc_alu_id`; `art_homologado_por` → coluna `art_homologado_por`);
- exceção única: `Usuarios.password` → coluna `usu_senha` (D1).

**Justificativa**: princípio III da constituição; o atributo Python fica legível e o `_id`
automático do Django coincide com a coluna.

## D6. Domínios fixos por data migrations separadas

**Decisão**: uma data migration por domínio, cada uma reversível e idempotente
(`get_or_create` pela chave natural, sem informar identificador):

| App | Migração | Conteúdo |
|---|---|---|
| cadastro | `0003_carga_cursos` | 3 cursos (FR-013) |
| cadastro | `0004_carga_areas_interesse` | 10 áreas (FR-015) |
| defesa | `0004_carga_criterios_provisorios` | 9 critérios, pesos e descritores "PROVISÓRIO" (FR-014) |
| cadastro | futura `00NN_carga_equivalencia_cursos` | só quando houver código confirmado (FR-016) |
| defesa | futura `00NN_descritores_oficiais` | troca dos 27 descritores antes do TP3 (FR-014a) |

As restrições (US2) ficam em migrações próprias, antes das cargas: `cadastro/0002_restricoes_cadastro`
e `defesa/0003_restricoes_defesa` (ordem completa em [tasks.md](tasks.md)).

As funções de carga ficam em módulos importáveis (por exemplo `cadastro/cargas.py` e
`defesa/cargas.py`) e recebem o registro de `apps`, para os testes chamarem duas vezes (FR-017,
SC-005).

**Justificativa**: cada domínio pode ser substituído ou complementado sem tocar nos demais; a
equivalência não tem migração agora porque não há código confirmado.

**Alternativas**: fixtures JSON (`loaddata` informa `pk`, conflita com D4); uma migração única
(substituir um domínio exigiria reescrever as outras cargas).

## D7. `choices` iguais ao Glossario_Status e `CheckConstraint` gerado a partir deles

**Decisão**: cada domínio é uma classe `models.TextChoices` (por exemplo `StatusTCC`,
`StatusEntrega`, `StatusConta`) com os valores exatos do Glossario_Status e do dicionário. Cada
modelo declara em `Meta.constraints` um `CheckConstraint` montado a partir de `Classe.values`.

**Justificativa**: `choices` sozinhos só validam formulários; o requisito FR-008 a FR-010 exige
recusa no banco. Gerar o CHECK a partir da mesma lista evita que tela e banco divirjam.

---

## R1. `TIMESTAMP` sem fuso: `TimestampField` com `USE_TZ = False`

**Status**: `USE_TZ = False` aprovado em 2026-10-19; `TimestampField` aprovado em 2026-10-19 após o
achado B1 da revisão.

**Correção da versão anterior**: esta seção dizia que `USE_TZ = False` bastava para gerar
`TIMESTAMP` sem fuso. Está errado: no backend PostgreSQL do Django, o `DateTimeField` sempre gera
`timestamp with time zone`, com qualquer valor de `USE_TZ`. O `USE_TZ` só muda o tratamento dos
valores (com ou sem fuso no Python).

**Decisão**:
- campo próprio `TimestampField` (subclasse de `DateTimeField` em `cadastro/fields.py`, cujo
  `db_type` é `timestamp`), usado nas 21 colunas `TIMESTAMP` do dicionário;
- `USE_TZ = False` e `TIME_ZONE = "America/Manaus"`, para que os valores no Python também sejam
  datas locais sem fuso, coerentes com a coluna.

**Justificativa**: o dicionário pede `TIMESTAMP` (sem fuso). O sistema atende uma única unidade em
Manaus (UTC−4, sem horário de verão), então datas locais não têm ambiguidade.

**Alternativas**: `DateTimeField` puro (gera `timestamptz`, divergente do dicionário e reprovado
pelo teste de conformidade); `TimestampField` com `USE_TZ = True` (o Python trabalharia com datas
com fuso gravadas em coluna sem fuso, com conversões implícitas confusas).

## R2. Nomes de tabela com maiúsculas

**Decisão**: manter os nomes do dicionário. O Django sempre põe aspas, então a tabela no PostgreSQL
é `"Cursos"` (sensível a maiúsculas). Todo SQL bruto (RunSQL, consultas manuais, testes de
conformidade) usa aspas duplas.

## R3. Unicidade de e-mails opcionais

**Status**: aprovada em 2026-10-19, com a condição abaixo.

**Decisão**: `usu_email` e `cext_email` com `unique=True, null=True`.

**Condição da aprovação**: e-mail sem valor é gravado como `NULL`, nunca como `""`. Os modelos
`Usuarios` e `CoorientadoresExternos` normalizam no `save()` (texto vazio ou só espaços → `None`),
e o `UsuariosManager.create_user` também. Atenção: `BaseUserManager.normalize_email(None)` devolve
`""`, então `create_user` converte para `None` depois de chamar `normalize_email`. Há teste para
cada modelo (spec, US2 cenário 11) e um teste com dois Alunos criados por `create_user` sem e-mail. Um
`CHECK (usu_email <> '')` no banco seria mais forte, mas é restrição fora do dicionário; só entra
após consulta à Maria Luiza e atualização do documento.

**Justificativa**: no PostgreSQL, uma restrição `UNIQUE` aceita vários `NULL` (NULLS DISTINCT é o
padrão), que é exatamente "único quando preenchido" (FR-007). Também satisfaz a verificação
`auth.E003` do `USERNAME_FIELD`. Os formulários das features devem gravar `None`, não `""`, para
e-mail vazio.

## R4. `CHAR(10)` das matrículas

**Status**: aprovada em 2026-10-19.

**Decisão**: campo próprio `CharFixoField` (subclasse de `CharField` cujo `db_type` é
`char(<max_length>)`, em `cadastro/fields.py`, junto do `TimestampField`), usado em
`alu_matricula` e `ouv_matricula`, mais `CheckConstraint` com `__regex=r"^[0-9]{10}$"`.

**Justificativa**: `CharField` gera `varchar`; o dicionário pede `CHAR(10)`.

## R5. Exclusão sem cascata e FKs adiadas

**Status**: aprovada em 2026-10-19.

**Decisão**: todas as FKs com `on_delete=models.PROTECT` (spec: exclusão de linha referenciada é
recusada). O Django cria as FKs no PostgreSQL como `DEFERRABLE INITIALLY DEFERRED`; a FK composta
criada por `RunSQL` usa a mesma cláusula (D3), para todas se comportarem igual.

**Consequência para os testes**: dentro de `TestCase`, a violação de FK só aparece no fim da
transação. Os testes de FK (US2, cenário 10) executam `SET CONSTRAINTS ALL IMMEDIATE` (ou
`connection.check_constraints()`) dentro de `transaction.atomic()` para ver o erro na hora.

## R6. Valor padrão no banco

**Decisão**: `not_lida = BooleanField(db_default=False)` (Django 5.0+), para que o padrão exista na
coluna e não só no Python (FR-012).

## R7. Restrições condicionais

**Decisão**: `CheckConstraint(condition=...)` (o parâmetro `check=` está obsoleto desde o 5.1):
- `TCCs`: `Q(tcc_status="Sem Proposta") | Q(tcc_titulo__isnull=False, tcc_resumo__isnull=False,
  tcc_modalidade__isnull=False)`;
- `Coorientacoes`: `Q(coo_doc__isnull=False, coo_cext__isnull=True) | Q(coo_doc__isnull=True,
  coo_cext__isnull=False)`;
- `Solicitacoes_Orientacao`: `Q(sol_tipo__in=[orientação, troca], sol_status__in=[...]) |
  Q(sol_tipo="Coorientação", sol_status__in=[...])`;
- `Turmas`: `Q(tur_hora_termino__gt=F("tur_hora_inicio"))`.

Unicidades parciais com `UniqueConstraint(condition=...)`. Todas as restrições têm nome explícito
no padrão `<tipo>_<db_table em minúsculas>_<sufixo>` (lista completa no data-model), únicos no
projeto (`models.E032`) e com até 63 caracteres (limite do PostgreSQL).

## R8. Tipos numéricos e textos longos

**Decisão**: `INT` → `IntegerField`/`AutoField`; `DECIMAL(3,1)` → `DecimalField(max_digits=3,
decimal_places=1)` mais CHECK de 0,0 a 10,0; `VARCHAR(n)` → `CharField(max_length=n)` mesmo para
1000 e 2000 (nunca `TextField`, que gera `text`); campos opcionais com `null=True, blank=True`.

## R9. Distribuição das 36 tabelas entre os apps

**Decisão**: `relatorios` não tem modelos (PGCS 2.3). `cadastro` (Épico 1) tem 27 tabelas e
`defesa` (Épico 2) tem 9: `Criterios`, `Ouvintes`, `Defesas`, `Defesas_Presenciais`,
`Defesas_Remotas`, `Banca_Defesa`, `Presenca_Ouvintes`, `Avaliacoes` e `Historico_Defesas`
(o PGCS põe "Defesa, Banca, Notas e Ouvintes" no app `defesa`). `defesa` depende de `cadastro`;
nunca o contrário. Lista completa em [data-model.md](data-model.md).

## R10. Especializações 1:1 sem herança multi-tabela

**Decisão**: `Alunos`, `Docentes`, `MembrosExternos`, `Secretarios`, `Coordenadores`, `Artigos`,
`Defesas_Presenciais` e `Defesas_Remotas` usam `OneToOneField(primary_key=True, db_column=...)`
explícito.

**Justificativa**: a herança multi-tabela do Django criaria colunas `*_ptr` e acoplaria `Alunos` à
classe de usuário; o `OneToOneField` produz exatamente "PK que também é FK".

## R11. Testes contra PostgreSQL e conformidade com o dicionário

**Decisão**: testes Django (`manage.py test`) contra PostgreSQL 16 (o usuário do banco precisa de
`CREATEDB`). O teste de conformidade lê `docs/fonte/Modelo_Logico_e_Dicionario_18_10.md` (tabelas
das seções 3.x) e compara com `information_schema.columns` e as restrições do banco: as 36
tabelas, colunas, tipo, tamanho, precisão, nulidade e PK. Assim SC-001 e SC-006 são verificados
contra o documento-fonte, e não contra uma cópia.

Mapeamento de tipos: `INT`→`integer`, `VARCHAR(n)`→`character varying(n)`,
`CHAR(n)`→`character(n)`, `DECIMAL(p,s)`→`numeric(p,s)`, `TIMESTAMP`→`timestamp without time
zone`, `TIME`→`time without time zone`, `DATE`→`date`, `BOOLEAN`→`boolean`.

O teste compara colunas e restrições, não índices: o Django cria índices nas FKs e índices `_like`
(`varchar_pattern_ops`) em `CharField` único ou PK, que não são colunas nem contrariam o
dicionário.

## R12. Dependências e versões

**Decisão**: `requirements.txt` com versão exata (`==`) de: Django 5.2 (último patch da série LTS
na data da instalação), `psycopg[binary]` 3.x, `python-dotenv`, `black`, `isort` e `flake8`. As
versões exatas são as instaladas na tarefa de configuração (`pip freeze`), não inventadas no plano.

**Observação**: o `lint.bat` do PGCS 3.3 aponta para `apps/sigtcc/`, que não existe na árvore do
PGCS 2.3; o caminho correto é `sigtcc/`. Ajustar o script é mudança de configuração e passa pelo
responsável pela configuração (Célio Benjamim), conforme o princípio IX.

## R14. Ordem física das colunas

**Status**: decidido por Julia Cohen em 2026-10-19, durante a T023 (`/speckit-implement`).

**Contexto**: o gerador de migrações do Django cria as chaves estrangeiras no fim de cada tabela.
Em 21 das 36 tabelas a ordem física das colunas ficou diferente da ordem do dicionário; nomes,
tipos, tamanhos, precisão, nulidade e chaves conferem em todas.

**Decisão**: aceitar a ordem gerada pelo Django. O teste de conformidade compara as colunas por
nome, não por posição.

**Justificativa**: o modelo relacional não dá significado à ordem das colunas, e o SC-001 cobre
nome, tipo, tamanho e nulidade. Toda coluna acrescentada por uma feature futura também iria para
o fim da tabela, então a ordem do dicionário não se manteria de qualquer forma.

**Alternativa rejeitada**: reordenar à mão as `0001_initial` (fidelidade total, mas edição manual
de migração gerada, que se perde se a migração for regenerada antes do merge).

**Pendente**: informar a Maria Luiza Guimarães junto com as demais consultas (plan.md, Pendências).

## R13. Configuração conjunta de isort, black e flake8

**Status**: aprovada em 2026-10-19 (achado I3); itens de configuração sujeitos à revisão do Célio
no PR, junto com o caminho do `lint.bat`.

**Decisão**:
- `pyproject.toml` com `[tool.black] line-length = 100` e `[tool.isort] profile = "black"`,
  `line_length = 100`, `known_first_party = ["sigtcc"]`;
- `.flake8` com `max-line-length = 100`, `extend-ignore = E203, W503` e
  `exclude = migrations, venv`.

**Justificativa**: sem perfil, o isort usa linha de 79 e um estilo de quebra diferente do black, e
os dois reescrevem o mesmo arquivo a cada execução do `lint.bat`. O flake8 acusa E203 e W503 em
código formatado pelo black.
