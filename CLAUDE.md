# SIGTCC – instruções para o Claude Code

Sistema de Gestão de TCC do NUCOMP-UEA. Projeto da disciplina Engenharia de Software (ESTCMP025),
2026/2, Profa. Diana Maria Camara de Carvalho (Product Owner). Equipe ++C: Célio Benjamim
(configuração), Julia Cohen, Leandra Matos (Scrum Master), Maria Luísa Gomes e Maria Luiza Guimarães.

Responda e escreva sempre em **português do Brasil**.

## Metodologia: Spec-Driven Development (Spec Kit)

A especificação é a fonte da verdade. A ordem é sempre:

1. `/speckit-constitution` – regras permanentes (arquivo `.specify/memory/constitution.md`).
2. `/speckit-specify` – o quê e por quê, a partir das US (gera `specs/NNN-nome/spec.md`).
3. `/speckit-clarify` – resolve ambiguidades antes de planejar.
4. `/speckit-plan` – como (modelos, rotas, telas), gera `plan.md` e anexos.
5. `/speckit-tasks` – tarefas pequenas e ordenadas (`tasks.md`).
6. `/speckit-analyze` – confere consistência spec × plan × tasks antes de codar.
7. `/speckit-implement` e `/speckit-converge` – implementa e fecha as lacunas.

Nunca escreva código de funcionalidade sem `spec.md`, `plan.md` e `tasks.md` aprovados pela
pessoa responsável pela feature. Mudança de comportamento depois do merge começa pela spec.

## Fontes de requisitos (ler antes de especificar ou planejar)

Ficam em `docs/fonte/` (cópias de referência dos documentos do Drive):

| Arquivo | Uso |
|---|---|
| `Matriz_Requisitos_17_10.md` | Matriz de Requisitos de 17/10 (convertida de `Matriz_Requisitos_SIGTCC_17_10.xlsx`). Abas `Requisitos_*`: RAN, regras (RBN) e requisitos não funcionais (ISO/IEC 25010). `Glossario_Status`: valores de status. `mudanças_17_10`: conversão dos IDs antigos para os novos. |
| `Historias_de_Usuario_v3_2.md` | US com fluxos, regras (RBN), critérios de aceite (Dado/Quando/Então). Base do `spec.md`. |
| `Modelo_Logico_e_Dicionario_18_10.md` | 36 tabelas com nomes, tipos e restrições. Base dos `models.py`. **Não invente tabelas ou campos.** |
| `DER_SIGTCC_V2.drawio` | DER conceitual (versão 2). |
| `PGCS_Plano_de_Configuracao.md` | Estrutura de pastas, branches, commits, PR, qualidade. |
| `Cronograma_18_10.md` | Sprints, prazos e responsáveis. |
| `prototipo/prototipo_17_10.html` | Protótipo de 17/10, homologado como referência visual das telas: layout, paleta, fontes Roboto/Figtree e ícones Material Symbols. **Use só o visual**: a lógica em JavaScript é simulação e não deve ser reaproveitada como regra de negócio (as regras vêm da matriz e das US). |

Regras de precedência quando os documentos divergirem:
- Matriz de Requisitos (versão de 17/10) > Histórias de Usuário > demais documentos.
- Use sempre os IDs novos de RAN e RBN da matriz de 17/10. Se um documento citar um ID antigo,
  converta pela aba `mudanças_17_10`.
- Se a divergência mudar o comportamento, **pare e pergunte**; registre a decisão na seção
  "Clarifications" da spec. Nunca escolha sozinho.
- O módulo de **Salas foi removido do escopo** em 17/10. A defesa presencial guarda o local como
  texto (`Defesas_Presenciais.dep_local`).

## Stack e estrutura (PGCS seções 2 e 3)

- Python 3.12, Django, PostgreSQL. Ambiente Windows com `venv`.
- Monólito modular com renderização no servidor (MVT do Django = MVC):
  Model = `models.py` (+ `services.py` para regras), Controller = `views.py` + `urls.py`,
  View = `templates/`.
- Estrutura obrigatória:
  ```
  sigtcc/settings.py, urls.py
  sigtcc/apps/cadastro/   Épico 1   (models, views, forms, urls, admin, migrations)
  sigtcc/apps/defesa/     Épico 2   (+ services.py: PDFs e conflito de horário)
  sigtcc/apps/relatorios/ Épico 3   (views, services.py de exportação, urls)
  sigtcc/templates/{base.html, includes/, cadastro/, defesa/, relatorios/}
  sigtcc/static/{css, js, img}
  sigtcc/media/           (ignorado no Git)
  ```
- Qualidade: `isort`, `black --line-length 100`, `flake8 --max-line-length 100` (rodar `lint.bat`).
- Segredos só no `.env` (nunca commitar `.env` nem `media/`).

## Convenções de código

- **Todo código tem comentários em português**, e cada classe/função/template indica a US e os
  RBN que atende, no formato `[US-07][RBN-CAD-05.9]`.
- Mensagens exibidas ao usuário: copie o texto exato dos fluxos alternativos e cenários da US.
- Nomes de tabelas e colunas: siga o dicionário de dados (`db_table` e `db_column` quando o nome
  Django for diferente).
- Toda alteração em `models.py` vem com a migração no mesmo PR. Nunca apagar migrações já na develop.
- Testes: cada cenário de aceite da US vira pelo menos um teste Django (`tests/`).

## Git (PGCS seções 4 a 6)

- Branches: `main` (só via release/hotfix), `develop`, `feature/feat-XX-nome`,
  `release/vX.Y.Z`, `bugfix/epico-X-nome`, `hotfix/vX.Y.Z`. Não use branches `NNN-nome` do Spec Kit.
- Commits: Conventional Commits, imperativo, até 72 caracteres, sem ponto final.
  Ex.: `feat(feat-02): implementar importacao de alunos por CSV`.
- PR para `develop`, título `[Feat-XX] Descrição (US-XX, US-YY)`, com o template do PGCS 6.3
  preenchido e revisão de outra pessoa da equipe. Merge com `--no-ff`.
- Não faça `git push`, merge ou tag sem a pessoa pedir.

## Agentes do projeto (`.claude/agents/`)

- `analista-requisitos` – monta e confere specs a partir das US e da matriz.
- `arquiteto-django` – revisa `plan.md` contra o modelo lógico e o PGCS.
- `desenvolvedor-django` – implementa tarefas do `tasks.md`.
- `testador-aceite` – transforma cenários Dado/Quando/Então em testes e roda.
- `revisor-pgcs` – checklist antes do PR (lint, migrações, commits, rastreabilidade).
