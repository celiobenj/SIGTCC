# [Feat-11] Apoio Operacional (US-34, US-35, US-48, US-49)

**Origem:** `feature/feat-11-apoio-operacional` -> **Destino:** `develop` (merge `--no-ff`, PGCS 6.4)

**Depende de:** `fix/celio-documentos-config` e `bugfix/epico-1-correcoes-finais`, nesta ordem (a
branch foi criada a partir delas, por causa do índice `docs/questoes-a-rever.md`). Mescle esses dois
PRs antes; depois deles, este PR mostra só os commits da feat-11.

**Spec:** `specs/011-apoio-operacional/` (`spec.md`, `plan.md`, `tasks.md`, `checklists/`)

**Responsável:** Célio Benjamim (spec e implementação; cronograma de 18/10, atividade 5.2,
antecipada para 11/11/2026). As US-34, 35, 48 e 49 citam Maria Luiza Nobre como responsável pela
redação.

### 1. Resumo da Alteração

Quatro relatórios operacionais (RAN-REL-03) no módulo Relatórios da spec 010, só de leitura, sem
tabela, coluna, migração, rota ou template de tela novos (`makemigrations --check`: "No changes
detected"):

- **Defesas realizadas no período** (US-48; REL-03.1): só sessões Realizadas, com Data/Horário,
  Aluno, Orientador (Presidente da banca), Banca (1º e 2º Avaliador efetivos, com o Suplente acionado
  no papel que ocupou), Modalidade do TCC e Parecer; filtro de período das defesas e Curso.
- **Turmas e alunos** (US-49; REL-03.2): uma linha por turma, com a sub-lista dos alunos e o Status do
  TCC (último registro do histórico na turma; "Sem Proposta" sem Proposta); Reprovado, Desistente e
  Jubilado destacados.
- **Aluno e orientador (apoio à matrícula)** (US-34; REL-03.3): alunos das turmas de TCC 1 do
  período, Aprovados para TCC 2 primeiro e destacados; quem já está em TCC 2 continua como Aprovado
  para TCC 2 no período de origem.
- **Horas complementares de ouvintes** (US-35; REL-03.4): uma linha por presença em sessão
  Realizada, 2 horas cada, e a linha Total.
- **Perfis**: Coordenador de Curso, Secretaria e Professor da Disciplina. O Professor que não é
  Coordenador vê só as próprias turmas e não tem o filtro Curso; o que também é Coordenador fica com
  a visão de gestão (Clarifications C1 e C2, Q-157).

**Commits**

| Commit | Título |
|---|---|
| (1º) | docs(feat-11): especificar o apoio operacional |
| (2º) | feat(feat-11): implementar os relatorios operacionais |

**Mudanças em código de outras specs** (todas só acrescentam):

| IC | Arquivo (spec de origem) | Mudança |
|---|---|---|
| IC-01 | `relatorios/apps.py` (010) | `ready()` carrega `services_operacionais` (ponto previsto no contrato §1) |
| IC-02 | `relatorios/tests/test_permissoes_relatorios.py`, `test_igualdade_tela_arquivo.py`, `test_us31_atividades.py`, `apoio_relatorios.py` (010) | matriz de permissões e igualdade tela × arquivo com os 4 relatórios; o Professor da Disciplina passa a ver também os operacionais; ouvinte com nome hostil no `cenario_hostil` |

Documentos do repositório: `docs/diagramas/Rastreabilidade_Diagramas_Codigo.md` (participantes dos
diagramas 23 a 26 e dois itens que ainda diziam "planejado"), `CHANGELOG.md` e
`docs/questoes-a-rever.md` (Q-157). As divergências com as US, a matriz, os diagramas de sequência e
o cronograma estão na planilha da Parte C (A064 a A081).

### 2. Rastreabilidade com o Projeto

- **US:** US-48, US-49, US-34 e US-35.
- **RBN:** RBN-REL-03.1, 03.2, 03.3 e 03.4 (com RBN-CAD-08.3, 08.7, 14.1 e RBN-DEF-01.2, 01.5, 02.2,
  06.3, 08.2).
- **Diagramas de sequência:** 25 `ConsultarListasAlunos` e 26 `ConsultarDefesasRealizadas`.

### 3. Checklist Técnico da Equipe (Definition of Done)

- [x] Lint aprovado: `pre-commit run --all-files` (isort, black `--line-length 100`, flake8
  `--max-line-length 100`).
- [x] Não há variáveis, imports ou trechos de código não utilizados (flake8 limpo).
- [x] `makemigrations --check --dry-run`: "No changes detected"; nenhuma migração existente alterada.
- [x] Os arquivos `.env` e os diretórios `sigtcc/media/` e `staticfiles/` NÃO foram adicionados ao Git.
- [x] A interface usa o layout único da spec 010 (protótipo de 17/10), sem template novo.
- [x] Suíte completa passando (ver a seção 4).

### 4. Evidência da Validação Manual (Critérios de Aceite das USs)

- Testes: 4 arquivos novos com os 33 cenários das US e as decisões C1 a C8
  (`test_us48_defesas_realizadas.py`, `test_us49_turmas_alunos.py`, `test_us34_aluno_orientador.py`,
  `test_us35_horas_ouvintes.py`), mais a matriz de permissões e a igualdade tela × PDF/CSV/XLSX com
  dados hostis para os 10 relatórios.
- Demonstração (`sigtcc_validacao`, `popular_demo`): todas as contas ativas, os 4 relatórios em 4
  combinações de filtro e os 3 formatos: 0 problemas; Coordenador e Secretaria veem 6 turmas, 30
  alunos de TCC 1, 1 defesa Realizada e 3 presenças de ouvintes com Curso Todos; o Professor da
  Disciplina vê só as próprias turmas; os demais perfis recebem a MR-06.

- [x] Cenário 1: Defesas realizadas, só Realizadas, com Orientador, Banca e Parecer (US-48)
- [x] Cenário 2: Turmas e alunos, Status por aluno e destaques (US-49)
- [x] Cenário 3: Aluno e orientador, Aprovados para TCC 2 primeiro (US-34)
- [x] Cenário 4: Horas de ouvintes, uma linha por presença e o total (US-35)
- [x] Cenário 5: Professor da Disciplina vê só as próprias turmas, sem o filtro Curso (todas)

### 5. Revisão por Pares (Peer Review)

- [ ] Revisado por: ______ (outra pessoa da equipe, PGCS 6.3)
