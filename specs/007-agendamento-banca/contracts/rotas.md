# Contrato: rotas e telas da feature 007

**Feature**: [../spec.md](../spec.md) | **Pesquisa**: [../research.md](../research.md)

Todas as rotas ficam em `sigtcc/apps/defesa/urls.py`, novo (`app_name = "defesa"`), incluído em
`sigtcc/urls.py` (IC-01). Sem login: login com `next` (spec 003). Logado sem permissão: 403 com a
M-02 (spec 003).

| Nome da rota | Caminho | Métodos | Acesso | Template | Requisitos |
|---|---|---|---|---|---|
| `defesas` | `/defesas/` | GET | Qualquer perfil autenticado, com visibilidade por perfil (FR-024) | `defesa/defesas.html` | FR-024 a FR-028 |
| `turma_defesas` | `/turmas/<tur_id>/defesas/` | GET | Professor da Disciplina da turma | `defesa/turma_defesas.html` | FR-006, FR-024 |
| `agendar` | `/defesas/agendar/` (aceita `?tcc=<id>` para pré-selecionar) | GET, POST | Orientador (EC) ou Professor da Disciplina (SI/LC) do TCC | `defesa/form_agendar.html` | FR-001 a FR-020 |
| `sessao` | `/defesas/<def_id>/` | GET | Membro da banca (inclusive o Suplente), Professor da Disciplina da turma, Secretaria do curso ou Aluno do próprio TCC (Clarifications 2026-10-31) | `defesa/sessao.html` | FR-030; contrato §4 |
| `alterar_banca` | `/defesas/<def_id>/banca/` | GET, POST | Quem pode agendar o TCC (Orientador em EC, Professor da Disciplina em SI/LC), sessão Agendada/Reagendada | `defesa/form_alterar_banca.html` | FR-011, FR-012 |
| `acionar_suplente` | `/defesas/<def_id>/suplente/` | GET, POST | Exclusivamente o Orientador, sessão Em Andamento | `defesa/form_acionar_suplente.html` | FR-013 |
| `reagendar` | `/defesas/<def_id>/reagendar/` | GET, POST | Quem pode agendar o TCC ou a Secretaria do curso | `defesa/form_reagendar.html` | FR-019 |
| `cancelar` | `/defesas/<def_id>/cancelar/` | GET, POST | Quem pode agendar o TCC ou a Secretaria do curso | `defesa/confirmar_cancelar.html` | FR-020 |
| `historico` | `/defesas/<def_id>/historico/` | GET | Mesma permissão de `sessao` | `defesa/historico.html` | FR-029 |

Regras gerais:
- Ordem das conferências: sessão existe (404) → permissão (403, M-02) → status permite a ação
  (sem MT25 própria desta spec; cada ação checa o status certo, ex. `reagendar`/`cancelar` só com
  Agendada/Reagendada/Em Andamento, `acionar_suplente` só com Em Andamento).
- `agendar` confere `permissoes_defesa.pode_agendar(usuario, tcc)` — Orientador em Engenharia de
  Computação, Professor da Disciplina em Sistemas de Informação e Licenciatura em Computação
  (FR-003); 404 se o TCC não existir ou não pertencer ao usuário nesse sentido, 403 se existir mas
  for do curso errado (ordem igual à das demais specs: existência antes de permissão).
- Botões só aparecem quando a ação é permitida (perfil, status, suplente presente); o serviço
  confere de novo, inclusive pelo endereço direto (SC-004, mesmo padrão das specs 004 a 006).
- Ações que mudam dados só por POST, com CSRF; confirmações em página própria, sem JavaScript.
- Menu: item "Defesas" novo (IC-02), rota `defesa:defesas`.
- Integrações com telas já mescladas (IC-03, IC-04): a aba "Defesas" da turma (`turma.html`,
  `_abas_professor.html`) linka para `defesa:turma_defesas`; a tela de orientandos
  (`orientacao/orientacoes.html`) linka para `defesa:agendar?tcc=<id>` em cada orientando elegível.
- A "tela de orientandos" e o "painel do aluno" (US-41, futura) não são desta spec; o link
  "Histórico da defesa" que essas telas possam abrir no futuro chama a mesma rota `historico` ou a
  função `historico_da_sessao` diretamente (research C7), sem reimplementar a consulta.
- **Quem abre `sessao`/`historico`** (Clarifications da spec, 2026-10-31; substitui a decisão I3
  do plano): membros da banca (inclusive o Suplente), Professor da Disciplina da turma, Secretaria
  do curso (que reagenda e cancela pela janela, US-24) e Aluno do próprio TCC (US-40, passo 8). O
  Coordenador de Curso e o Coorientador, docentes fora da banca, ficam só com a lista (E5 da
  US-40). Qualquer outro usuário recebe "Você não tem permissão para visualizar esta defesa"
  (FR-030), também pelo endereço direto.
