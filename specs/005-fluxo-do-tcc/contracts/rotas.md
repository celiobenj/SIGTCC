# Contrato: rotas e telas da feature 005

**Feature**: [../spec.md](../spec.md) | **Pesquisa**: [../research.md](../research.md)

Todas as rotas ficam em `sigtcc/apps/cadastro/urls.py` (`app_name = "cadastro"`), sob o mesmo
prefixo `/turmas/<tur_id>/...` já usado pela spec 004, exceto as duas listas de turmas do Aluno
(`/minhas-turmas/...`, FR-031). "Professor" é o Professor da Disciplina
**da turma**. Sem login: login com `next` (spec 003). Logado sem permissão: 403 com a M-02 (spec
003). Ação em turma arquivada: MT-25 e volta para a turma/aba (spec 004, `trata_turma_arquivada`).

| Nome da rota | Caminho | Métodos | Acesso | Template | Requisitos |
|---|---|---|---|---|---|
| `meu_tcc` | `/turmas/<tur_id>/meu-tcc/` | GET, POST (Salvar Proposta / Salvar alterações) | Aluno matriculado na turma (`vinculo_na_turma` pelo próprio usuário) | `cadastro/tcc/meu_tcc.html` | FR-001 a FR-007a |
| `historico_status_aluno` | `/turmas/<tur_id>/meu-tcc/historico/` | GET | Aluno, o próprio | `cadastro/tcc/historico_status.html` | FR-009, FR-010 |
| `historico_status` | `/turmas/<tur_id>/alunos/<alu_id>/historico/` | GET | Professor da Disciplina da turma | `cadastro/tcc/historico_status.html` | FR-009, FR-010; Clarifications (Secretaria e Coorientador excluídos) |
| `entregas` | `/turmas/<tur_id>/entregas/` | GET | Professor da Disciplina | `cadastro/tcc/entregas.html` (lista + botão Cadastrar atividade) | FR-013, FR-014, FR-027 |
| `entrega_cadastrar` | `/turmas/<tur_id>/entregas/nova/` | GET, POST | Professor, turma ativa | `cadastro/tcc/form_entrega.html` | FR-013 a FR-017 |
| `entrega_acompanhar` | `/turmas/<tur_id>/entregas/<tma_id>/` | GET | Professor da Disciplina | `cadastro/tcc/acompanhamento_entrega.html` | FR-026, FR-027 |
| `minhas_entregas` | `/turmas/<tur_id>/minhas-entregas/` | GET | Aluno matriculado | `cadastro/tcc/minhas_entregas.html` | FR-018 a FR-025 |
| `entrega_enviar` | `/turmas/<tur_id>/minhas-entregas/<tma_id>/` | GET, POST (Enviar) | Aluno matriculado, dono da entrega | `cadastro/tcc/enviar_entrega.html` | FR-018 a FR-025 (inclui Versão Final, US-29) |
| `aluno_versao_final` | `/turmas/<tur_id>/alunos/<alu_id>/versao-final/` | GET, POST (Homologar / Devolver para Ajuste) | Professor da Disciplina, turma de TCC 2 | `cadastro/tcc/homologar_versao_final.html` | FR-028 a FR-030 |
| `minhas_turmas` | `/minhas-turmas/` | GET | Aluno (só as turmas não arquivadas em que está matriculado) | `cadastro/tcc/minhas_turmas.html` (cada turma leva a `meu_tcc`; link "Turmas arquivadas") | FR-031 |
| `minhas_turmas_arquivadas` | `/minhas-turmas/arquivadas/` | GET | Aluno (só as turmas arquivadas em que está matriculado) | `cadastro/tcc/minhas_turmas.html` (somente consulta) | FR-031; E9 da US-13 |

Regras gerais:
- Ordem das conferências (research C4, reaplicando B2 da spec 004): turma existe (404) →
  permissão (403, M-02) → turma arquivada (MT-25). Nas rotas `/alunos/<alu_id>/...`, o aluno
  precisa estar matriculado nesta turma (404 se não, `vinculo_na_turma`), também no GET.
- `meu_tcc`, `historico_status_aluno`, `minhas_entregas` e `entrega_enviar` conferem que o usuário
  autenticado **é** o Aluno dono daquele vínculo na turma (não outro aluno — sem IDOR), além do
  perfil "aluno".
- Botões só aparecem quando a ação é permitida (Status do TCC, prazo, perfil); o serviço confere
  de novo, inclusive pelo endereço direto (SC-004, mesmo padrão da spec 004).
- Ações que mudam dados só por POST, com CSRF; sem JavaScript (protótipo é só referência visual).
- Menu (FR-031; Clarifications, sessão 2026-10-23; índice Q-89): o Aluno tem um item "Turmas"
  próprio em `menu.py` (perfil "aluno", rota `minhas_turmas`, logo depois de "Início"); o item
  "Turmas" de Docente e Secretaria (rota `turmas`, spec 004) não muda. A tela da turma da spec 004
  (`turma`, `/turmas/<tur_id>/`) continua só do Professor da Disciplina e da Secretaria do curso
  (FR-010 da spec 004): o Aluno recebe 403 nela, como hoje.
- Abas (nome "Atividades" provisório, Q-80), num include por perfil, sem JavaScript:
  - Aluno (`_abas_aluno.html`, em `meu_tcc.html` e `minhas_entregas.html`): "Meu TCC" (`meu_tcc`)
    e "Atividades" (`minhas_entregas`), com a aba atual destacada.
  - Professor (`_abas_professor.html`, em `turma.html` da spec 004 e em `entregas.html`): "Alunos"
    (`turma`) e "Atividades" (`entregas`). A Secretaria do curso, que também abre `turma.html`,
    não vê a aba "Atividades" (a rota `entregas` é só do Professor, FR-027).
- A "tela de orientandos" (Orientador) e a ação "Correções Conferidas" pertencem à spec 006, ainda
  não implementada; esta spec só expõe os serviços de leitura/escrita que a 006 vai chamar
  (`contracts/servicos-compartilhados.md`).
- A "tela do aluno" completa (painel único, US-41) também não existe ainda; `historico_status` e
  `aluno_versao_final` ficam como rotas próprias desta spec, a levar ao painel depois (mesmo
  tratamento dado a US-09 na spec 004).
