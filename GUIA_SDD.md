# Guia: Spec-Driven Development no SIGTCC com Claude Code (VS Code)

## 1. O que vamos usar

A metodologia do specdriven.ai tem as fases Constitution → Specify → Clarify → Plan → Tasks →
Implement/Iterate. A ferramenta que executa exatamente essas fases dentro do Claude Code é o
**Spec Kit** (GitHub, CLI `specify`). Ele instala no projeto os comandos `/speckit-*` e cria uma
pasta por feature:

```
.specify/memory/constitution.md      regras permanentes do projeto
specs/001-nome-da-feature/
    spec.md       o quê e por quê (a partir das US)
    plan.md       como (models, views, telas) + data-model.md, research.md
    tasks.md      tarefas pequenas, ordenadas
.claude/skills/speckit-*/            comandos do Spec Kit
.claude/agents/*.md                  agentes do SIGTCC (este kit)
CLAUDE.md                            contexto lido pelo Claude Code em toda sessão (este kit)
docs/fonte/                          documentos do projeto em Markdown (este kit)
```

## 2. Instalar (uma vez, no Windows)

1. **VS Code** + extensão **Claude Code** (Marketplace, publicada pela Anthropic). Faça login com a
   sua conta Claude.
2. **Git**, **Python 3.12** e **PostgreSQL 15+**.
3. **uv** (gerenciador de ferramentas Python), no PowerShell:
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
4. **Spec Kit**:
   ```powershell
   uv tool install specify-cli
   specify version
   ```

## 3. Combinar com a equipe antes de inicializar

Inicializar o Spec Kit acrescenta ao repositório `.specify/`, `specs/`, `.claude/`, `CLAUDE.md` e
`docs/fonte/`. Isso altera a estrutura definida no PGCS, então:

- confirmem com o Célio (responsável pela configuração) e registrem no PGCS/CHANGELOG;
- **só uma pessoa** inicializa, uma vez, numa branch própria, e abre PR para a `develop`;
- confirmem a numeração das features (`feat-XX`) para os nomes de branch.

## 4. Inicializar no repositório (uma pessoa)

```powershell
cd caminho\SIGTCC
git checkout develop ; git pull
git checkout -b feature/feat-00-spec-kit
specify init --here --force --integration claude --script ps
```

Depois copie para a raiz do repositório o conteúdo deste kit (`CLAUDE.md`, `.claude/agents/`,
`docs/fonte/`). Acrescente em `docs/fonte/` a **Matriz de Requisitos de 17/10** exportada (o kit não a
inclui). Commit: `chore(config): adotar spec kit e agentes do claude code`, PR para `develop`.

> Não instale a extensão de Git do Spec Kit (`specify extension add git`): ela cria branches
> `001-nome`, que não seguem o PGCS. As branches continuam `feature/feat-XX-nome`, criadas à mão.

## 5. Constituição (uma vez, no mesmo PR)

1. Abra o VS Code na pasta do repositório e o painel do Claude Code (ícone do Claude na barra
   lateral).
2. Digite `/speckit-constitution` e cole o texto de `docs/fonte/constituicao_base.md`.
3. Revise o arquivo gerado `.specify/memory/constitution.md` com a equipe.

## 6. Ciclo de cada feature

Ordem recomendada das specs (respeita as dependências do banco):

| Spec | Conteúdo | Responsável |
|---|---|---|
| 001-modelo-de-dados | 36 tabelas do Modelo Lógico 18/10, migrations | Maria Luiza (atividade 3.2) |
| 002-gestao-de-contas | US-03, 04, 05, 06, 39 (+ US-50, Maria Luiza) | Maria Luísa |
| 003-acesso-e-login | US-10, 11, 12, 37, 38 | Julia |
| 004-turmas-e-alunos | US-07, 08, 09 | Julia |
| 005… | Fluxo do TCC, Orientação, Defesa, Relatórios | Leandra, Célio, Maria Luiza |

Para cada spec, na branch da feature (`git checkout -b feature/feat-XX-nome develop`):

| Passo | O que digitar no Claude Code | Quem confere |
|---|---|---|
| Especificar | `/speckit-specify Turmas e Alunos do SIGTCC: US-07, US-08 e US-09. Use as seções dessas US em docs/fonte/Historias_de_Usuario_v3_3.md, incluindo regras (RBN), fluxos alternativos e cenários de aceite.` | `@agent-analista-requisitos confira a spec 004 contra as US e liste os pontos a decidir` |
| Esclarecer | `/speckit-clarify` (responda às perguntas; se for decisão de escopo, consulte a equipe) | você |
| Planejar | `/speckit-plan Django 5 + PostgreSQL, app sigtcc/apps/cadastro, tabelas Turmas, Alunos_Turmas e Historico_Alunos_Turmas do dicionário de dados, conforme a constituição` | `@agent-arquiteto-django revise o plan da spec 004` |
| Tarefas | `/speckit-tasks` e depois `/speckit-analyze` | você + arquiteto |
| Implementar | `/speckit-implement` (ou `@agent-desenvolvedor-django implemente as tarefas T001 a T005`) | você revisa cada diff |
| Testar | `@agent-testador-aceite crie e rode os testes dos cenários da US-07 a US-09` | você |
| Fechar lacunas | `/speckit-converge` | você |
| Antes do PR | `@agent-revisor-pgcs confira a branch e prepare o PR` | revisor da equipe |

Commit no padrão `feat(feat-02): implementar cadastro de turmas`, PR `[Feat-02] Gestão de Turmas (US-07, US-08, US-09)`.

## 7. Agentes: o que são e como usar

Um agente (subagent) é um arquivo `.md` em `.claude/agents/` com um cabeçalho YAML (`name`,
`description`, `tools`, `model`) e, abaixo, as instruções. O Claude Code chama o agente sozinho
quando a tarefa combina com a `description`, ou você chama de forma explícita:

- digitando `@` e escolhendo o agente (ou `@agent-revisor-pgcs ...`);
- pedindo por nome: "use o agente arquiteto-django para revisar o plano".

Este kit já traz os cinco agentes. Para criar outro, peça ao próprio Claude Code ("crie um agente em
`.claude/agents/` que…") ou copie um arquivo e edite. Como ficam no repositório, a equipe toda usa os
mesmos agentes.

## 8. Cuidados

- O `lint.bat` do PGCS aponta para `apps/sigtcc/`; pela árvore do próprio PGCS o caminho é `sigtcc/`.
  Avisar o Célio.
- O PGCS diz que Matriz/EAP ficam no Drive, mas o SDD precisa delas acessíveis ao Claude. As cópias em
  `docs/fonte/` são de referência; atualizem quando o documento do Drive mudar.
- Sempre revise o diff antes de aceitar; o Claude Code pede permissão para editar e rodar comandos.
