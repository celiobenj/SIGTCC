# Contrato: modelos ORM do SIGTCC

**Feature**: [../spec.md](../spec.md) | **Modelo**: [../data-model.md](../data-model.md)

Esta feature não tem telas nem API. A interface que ela expõe é o conjunto de modelos Django que as
demais features importam. Este contrato fixa nomes e comportamentos dos quais as outras features
podem depender; mudar qualquer item abaixo é mudança de comportamento e começa pela spec.

## 1. Localização e importação

| App (`app_label`) | Módulo | Modelos |
|---|---|---|
| `cadastro` | `sigtcc.apps.cadastro.models` | Cursos, EquivalenciaCursos, Disciplinas, AreasInteresse, Usuarios, Alunos, Docentes, MembrosExternos, Secretarios, CoorientadoresExternos, Coordenadores, Turmas, AlunosTurmas, HistoricoAlunosTurmas, TurmasMarcos, EntregasMarcos, HistoricoEnviosEntregas, TCCs, Orientacoes, Coorientacoes, PalavrasChaveTCC, SolicitacoesOrientacao, HistoricoStatusTCC, Artigos, EncontroOrientacao, ComentariosEncontro, Notificacoes |
| `defesa` | `sigtcc.apps.defesa.models` | Criterios, Ouvintes, Defesas, DefesasPresenciais, DefesasRemotas, BancaDefesa, PresencaOuvintes, Avaliacoes, HistoricoDefesas |
| `relatorios` | — | nenhum modelo; só consulta os de `cadastro` e `defesa` |

- Domínios (`TextChoices`): `sigtcc.apps.cadastro.choices` e `sigtcc.apps.defesa.choices`.
- Campos próprios: `sigtcc.apps.cadastro.fields.CharFixoField` (`CHAR(n)`, matrículas) e
  `sigtcc.apps.cadastro.fields.TimestampField` (`TIMESTAMP` sem fuso, as 21 colunas de data e hora).
  Valores de data e hora são `datetime` sem fuso, no horário de Manaus (`USE_TZ = False`).
- `defesa` pode importar de `cadastro`; `cadastro` nunca importa de `defesa`.
- O usuário é obtido por `django.contrib.auth.get_user_model()` ou pela string
  `settings.AUTH_USER_MODEL` (`"cadastro.Usuarios"`) em FKs.

## 2. Nomes de atributos

| Caso | Regra | Exemplo |
|---|---|---|
| Coluna comum | atributo = coluna | `tcc_titulo` |
| FK | atributo = coluna sem `_id`; o `<atributo>_id` do Django é a coluna | `tcc_alu` / `tcc_alu_id` |
| FK cuja coluna não termina em `_id` | atributo = coluna, `db_column` explícito | `art_homologado_por` (o Django expõe `art_homologado_por_id`, a coluna é `art_homologado_por`) |
| PK que é FK (1:1) | atributo = coluna sem `_id`; `pk` = id do pai | `Alunos.alu` / `Alunos.pk == Usuarios.usu_id` |
| PK composta | campo `pk = CompositePrimaryKey(...)`; `pk` é tupla na ordem do dicionário | `BancaDefesa.pk == (ban_def_id, ban_usu_id)` |
| Senha | `Usuarios.password` (coluna `usu_senha`) | `user.set_password(...)` |

## 3. Comportamento garantido do `Usuarios`

- `USERNAME_FIELD = "usu_email"`; `EMAIL_FIELD = "usu_email"`; `REQUIRED_FIELDS = ["usu_nome"]`.
- `Usuarios.objects.create_user(usu_email, usu_nome, password=None, **campos)`: grava o hash com
  `set_password` quando a senha é informada; sem senha, `password` fica `None` (conta
  'Aguardando Ativação'). O e-mail passa por `normalize_email` e, se ficar vazio, é gravado como
  `None` (o `normalize_email` do Django devolve `""` para `None`).
- `str(usuario)` retorna `usu_nome` (o e-mail pode ser nulo).
- `is_active` é `True` somente se `usu_status == "Ativa"`; não é coluna e não é gravável.
- Não existem `last_login`, `is_staff`, `is_superuser`, `groups` nem `user_permissions`.
- E-mail vazio (`""` ou só espaços) é normalizado para `None` no `save()` de `Usuarios` e de
  `CoorientadoresExternos` e no `create_user`; o banco nunca recebe `""` por esses caminhos.
  Atenção: `QuerySet.update()` e `bulk_create()` não chamam `save()`; quem usar esses métodos deve
  normalizar antes.

## 4. Garantias do banco que as features podem assumir

- Toda gravação fora dos domínios, das unicidades e das restrições de
  [data-model.md](../data-model.md) levanta `django.db.IntegrityError`. As features devem validar
  antes no formulário (mensagens da US) e tratar o `IntegrityError` como erro inesperado.
- Exclusão de linha referenciada levanta `django.db.models.ProtectedError` no ORM, com uma
  exceção: excluir uma `BancaDefesa` que tem avaliações. A FK composta
  `Avaliacoes` → `Banca_Defesa` existe só no banco (o ORM não a conhece), então a recusa vem como
  `django.db.IntegrityError`.
- Todas as FKs, inclusive a composta, são `DEFERRABLE INITIALLY DEFERRED`: a violação de FK não
  aparece no `save()`, e sim no fim da transação (no commit ou ao sair do `transaction.atomic()`
  mais externo). Quem precisar do erro na hora executa `SET CONSTRAINTS ALL IMMEDIATE`.
- Identificadores nunca são informados na criação (spec FR-003).
- `Notificacoes.not_lida` nasce `False` mesmo em inserção sem o campo.
- `Avaliacoes` só aceita (`ava_def_id`, `ava_usu_id`) que exista em `Banca_Defesa`.

## 5. O que NÃO faz parte do contrato

- Regras da seção 4 do dicionário e as marcadas como "validação na aplicação" (ficam nas features).
- Admin do Django (não instalado nesta feature).
- Conteúdo de `Equivalencia_Cursos` (vazia até haver código confirmado) e o texto dos descritores
  dos critérios (provisório até o TP3).
