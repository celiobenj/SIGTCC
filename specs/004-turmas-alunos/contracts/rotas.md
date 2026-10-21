# Contrato: rotas e telas da feature 004

**Feature**: [../spec.md](../spec.md) | **Pesquisa**: [../research.md](../research.md)

Todas as rotas ficam em `sigtcc/apps/cadastro/urls.py` (`app_name = "cadastro"`). "Professor" é o
Professor da Disciplina **da turma**; "Secretaria" é a Secretaria do curso da turma (spec Q9). Sem
login: login com `next` (spec 003). Logado sem permissão: 403 com a M-02 (spec 003). Ação que altera
dados em turma arquivada: MT-25 e volta para a turma.

| Nome da rota | Caminho | Métodos | Acesso | Template | Requisitos |
|---|---|---|---|---|---|
| `turmas` | `/turmas/` | GET | Docente (turmas de que é Professor, ativas) ou Secretaria (turmas do curso) | `cadastro/turmas/lista.html` | FR-010; Q9 |
| `turmas_arquivadas` | `/turmas/arquivadas/` | GET | idem, turmas arquivadas | `cadastro/turmas/arquivadas.html` | FR-008, FR-010 |
| `turma_nova` | `/turmas/nova/` | GET, POST | Docente | `cadastro/turmas/form_turma.html` | FR-001 a FR-003 |
| `turma` | `/turmas/<tur_id>/` | GET | Professor ou Secretaria | `cadastro/turmas/turma.html` (dados, alunos, ações permitidas) | FR-008 a FR-010 |
| `turma_editar` | `/turmas/<tur_id>/editar/` | GET, POST | Professor, turma ativa | `cadastro/turmas/form_turma.html` | FR-005 |
| `turma_excluir` | `/turmas/<tur_id>/excluir/` | GET (MT-07), POST | Professor, turma ativa | `cadastro/turmas/confirmar.html` | FR-006; Q12 |
| `turma_arquivar` | `/turmas/<tur_id>/arquivar/` | GET (MT-09), POST | Professor, turma ativa | `cadastro/turmas/confirmar.html` | FR-007 |
| `matricular` | `/turmas/<tur_id>/matricular/` | GET, POST | Professor, turma ativa | `cadastro/turmas/matricular.html` ("Matrícula individual" e "Importar arquivo (CSV/XLSX)") | FR-011 a FR-015 |
| `importar` | `/turmas/<tur_id>/importar/` | GET, POST (envio do arquivo → prévia) | Professor, turma ativa | `cadastro/turmas/importar.html`, `cadastro/turmas/previa.html` | FR-016, FR-017; Q13 |
| `importar_confirmar` | `/turmas/<tur_id>/importar/confirmar/` | POST (com o `token` da prévia) | Professor, turma ativa; prévia da mesma turma e no prazo | — (redireciona para o resumo) | FR-018; B10 |
| `importar_cancelar` | `/turmas/<tur_id>/importar/cancelar/` | POST | Professor | — (apaga a prévia e volta para a turma) | B10 |
| `importar_resumo` | `/turmas/<tur_id>/importar/resumo/` | GET | Professor | `cadastro/turmas/resumo.html` | FR-018; B10 |
| `modelo_importacao` | `/turmas/modelo-importacao.csv` | GET | Docente | — (CSV UTF-8 com ";") | FR-016; Q11 |
| `aluno_editar` | `/turmas/<tur_id>/alunos/<alu_id>/editar/` | GET, POST | Professor, turma ativa | `cadastro/turmas/editar_aluno.html` | FR-019 |
| `aluno_transferir` | `/turmas/<tur_id>/alunos/<alu_id>/transferir/` | GET, POST | Professor ou Secretaria, turma ativa com orientador automático | `cadastro/turmas/transferir.html` | FR-020 a FR-022 |
| `aluno_excluir` | `/turmas/<tur_id>/alunos/<alu_id>/excluir/` | GET, POST (justificativa → confirmação final MT-24 → execução) | Professor, turma ativa, aluno sem Proposta | `cadastro/turmas/excluir_aluno.html` | FR-023; Q8 |
| `aluno_encerrar` | `/turmas/<tur_id>/alunos/<alu_id>/encerrar/` | GET, POST | Professor, turma ativa, aluno com Proposta | `cadastro/turmas/encerrar.html` | FR-024; Q10 |
| `excluidos_transferidos` | `/turmas/<tur_id>/excluidos-transferidos/` | GET | só o Professor (matriz, RBN-CAD-05.8) | `cadastro/turmas/excluidos_transferidos.html` | FR-026 |

Regras gerais:
- Ordem das conferências (B2): turma existe (404) → permissão (403, M-02) → turma arquivada (MT-25).
  Nas rotas `/alunos/<alu_id>/...`, o aluno precisa estar matriculado nesta turma (404 se não),
  também no GET (B2, `vinculo_na_turma`).
- Botões e links de ação só aparecem quando permitidos (E5 da US-07; cenários 6 e 11 da US-07 e da
  US-08; cenário 11 da US-09); o serviço confere de novo, inclusive pelo endereço direto (SC-004).
- Ações que mudam dados só por POST, com CSRF; confirmações em página própria (sem JavaScript).
- Menu: item "Turmas" (`menu.py`, perfis docente e secretaria).
- A rota `aluno` da spec 003 (`/alunos/<alu_id>/`, reset do primeiro acesso) continua igual; a lista
  de alunos da turma liga para ela só para o Professor da turma (a Secretaria não tem acesso a ela;
  observação de LGPD S-02 do índice).
