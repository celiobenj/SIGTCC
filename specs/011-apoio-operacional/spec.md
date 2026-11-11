# Feature Specification: Apoio Operacional do SIGTCC

**Feature Branch**: `feature/feat-11-apoio-operacional`

**Created**: 2026-11-10

**Status**: Approved (Célio Benjamim, 2026-11-10)

**Input**: User description: "Relatórios operacionais do Épico 3 (RAN-REL-03): US-48 (Defesas
realizadas no período), US-49 (Turmas e alunos), US-34 (Aluno e orientador, apoio à matrícula) e
US-35 (Horas complementares de ouvintes), sobre a base do módulo Relatórios da spec 010
(contrato `specs/010-dashboards-producao/contracts/base-relatorios.md`, §1 a §6). Somente leitura,
sem tabelas nem colunas novas. O cronograma foi antecipado em 10/11/2026: a feature é feita de uma
vez, com as decisões em aberto tomadas pela equipe e registradas em Clarifications."

**Responsável pela spec e pela implementação**: Célio Benjamim (cronograma de 18/10, atividade
5.2, com a Julia na feat-10; antecipada para 11/11/2026). As US-34, 35, 48 e 49 citam Maria Luiza Nobre como responsável pela redação.
**Revisor do PR**: outra pessoa da equipe (PGCS 6.3).

**Fontes**: Histórias de Usuário v3.4 (US-48, US-49, US-34 e US-35); Matriz de Requisitos de 17/10,
aba `Requisitos_Relatorio` (RAN-REL-03: RBN-REL-03.1 a 03.4) e as regras citadas por elas
(RBN-CAD-07.1, 08.3, 08.7, 14.1; RBN-DEF-01.2, 01.5, 02.2, 06.3 e 08.2); Modelo Lógico e Dicionário
de 18/10; protótipo de 17/10 (telas "Relatórios"). As quatro US declaram "sem diagrama próprio:
consulta de relatório somente leitura".

## Dependências e reaproveitamento

- **Modelo de dados**: já existe (spec 001). Esta spec **não cria tabelas nem colunas** e nenhuma
  tela dela grava dados. Lê `Turmas`, `Alunos_Turmas`, `TCCs`, `Historico_Status_TCC`,
  `Orientacoes`, `Usuarios`, `Alunos`, `Docentes`, `Cursos`, `Defesas`, `Banca_Defesa`,
  `Ouvintes` e `Presenca_Ouvintes`.
- **Base do módulo Relatórios (spec 010)**: registro por decorador (§1), `FiltroRelatorioForm` e
  `Filtros` (§2), estrutura única `Relatorio`/`Linha`/`SubLista` com `destaque` e `totais` (§3),
  exportação genérica em PDF, CSV e XLSX (§4) e o layout único `relatorios/relatorios.html` (§5).
  Nenhum template de tela novo; nenhuma mudança nesses módulos.
- **Spec 010**: `ultimo_status` e o Status do vínculo (último registro do histórico do TCC na turma
  do período, CAD-08.7; "Sem Proposta" sem TCC) e o nome do orientador do TCC (vínculo ativo; sem
  ele, o mais recente).
- **Spec 009**: `services_ouvintes.ouvintes_das_defesas(periodo, cur_id)`, que a própria spec 009
  deixou para o RBN-REL-03.4 (uma linha por presença em sessão Realizada) e `HORAS_POR_SESSAO`.
- **Spec 007**: `PAPEIS_TITULARES` (o Suplente acionado ocupa o papel do titular ausente,
  RBN-DEF-02.2) e o filtro de período das defesas (RBN-DEF-01.5).
- **Spec 002**: `filtro_de_curso` e o curso padrão do usuário (RBN-CAD-14.1).

## Clarifications

### Session 2026-11-10

Decisões de Célio Benjamim (cronograma antecipado; índice Q-157), que fecham os pontos "A definir na
spec 011" do contrato §6 da spec 010:

- C1. **Recorte do Professor da Disciplina em 03.1, 03.3 e 03.4** → o mesmo do 03.2: só os dados
  das turmas em que ele é o Professor da Disciplina (sessões dos TCCs dessas turmas; alunos dessas
  turmas; ouvintes das sessões dessas turmas). Segue a regra da tela Defesas da spec 007, em que o
  Professor da Disciplina vê as sessões das próprias turmas.
- C2. **Professor da Disciplina que também é Coordenador de Curso** → vale o perfil de gestão: vê o
  filtro Curso, com o Curso Coordenado por padrão, e todos os dados do curso escolhido (as US
  tiram o filtro Curso só do "Professor da Disciplina que não é Coordenador de Curso"; mesmo
  critério da spec 010, `PERFIS_DE_GESTAO`).
- C3. **Orientador em 03.1** → o membro no papel "Orientador (Presidente)" da banca da sessão, como
  a lista de ouvintes da spec 009.
- C4. **Banca em 03.1** → os avaliadores efetivos, "Nome (1º Avaliador); Nome (2º Avaliador)": o
  Suplente acionado aparece no papel que ocupou e o Suplente não acionado não aparece (o
  Orientador já está na coluna própria).
- C5. **Data/Horário em 03.1** → "DD/MM/AAAA HH:MM", da data e da hora de início da sessão; ordem
  por data, hora e nome do aluno.
- C6. **Universo do 03.3 (apoio à matrícula)** → os alunos das turmas de **TCC 1** do período (e do
  Curso), porque o relatório serve para identificar quem se matricula em TCC 2 e a coluna é
  "Orientador (aceito em TCC 1)". O Orientador é o do TCC da turma (vínculo ativo; sem ele, o mais
  recente; sem nenhum, "Sem orientador"). Ordem: Aprovados para TCC 2 primeiro, depois os demais,
  cada grupo pelo nome do aluno.
- C7. **Linhas do 03.2** → uma por turma do período (e do Curso), pela identificação da turma;
  coluna "TCC 1 ou TCC 2" com a Descrição da turma; sub-lista "Alunos" com Nome do Aluno e Status
  do TCC ("ao lado de cada nome", como na US), pelo nome; turma sem aluno aparece com Total de Alunos 0 e "Nenhum registro".
  Destaque nas linhas da sub-lista com Status Reprovado, Desistente ou Jubilado.
- C8. **Horas do 03.4** → coluna numérica com 2 por linha; linha "Total" com a soma; ordem por data
  da defesa e nome do ouvinte (como a tela "Ouvintes das defesas" da spec 009).
- C9. **Somente leitura** → as consultas não chamam o início automático das sessões vencidas da
  Defesa (`iniciar_sessoes_vencidas`), que grava; contam só as sessões já Realizadas.
- C10. **Textos sem texto exato nas US** → MR-15 a MR-18 (descrições) e os blocos "Como é
  calculado" (MR-03) desta spec, adotados como os da spec 010 (Q-146): um ajuste pedido pela PO
  entra como mudança de texto, sem mudar regra.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Defesas realizadas no período (Priority: P1)

A Secretaria abre Relatórios → "Defesas realizadas no período", escolhe o período e o curso e vê
só as sessões Realizadas, com Data/Horário, Aluno, Orientador, Banca, Modalidade do TCC e Parecer;
exporta em PDF, CSV ou XLSX (US-48).

**Independent Test**: com 3 sessões Realizadas e 1 Agendada em 2026/2, o relatório mostra só as 3 e
o PDF baixado tem as 3.

**Acceptance Scenarios** (US-48, cenários 1 a 9):

1. **Given** 3 sessões Realizadas e 1 Agendada em 2026/2, **When** a Secretaria abre o relatório
   com 2026/2 e aciona PDF, **Then** a pré-visualização tem só as 3, com as 6 colunas, e o PDF
   também.
2. **Given** a tela do relatório, **When** informa 01/09/2026 a 30/09/2026, **Then** só o intervalo
   conta.
3. **Given** a tela, **When** escolhe o atalho Este Mês, **Then** as datas vêm preenchidas com o
   primeiro e o último dia do mês.
4. **Given** o Coordenador de SI, **When** abre o relatório, **Then** o filtro Curso vem com SI.
5. **Given** um Professor da Disciplina que não é Coordenador, **When** abre o relatório, **Then**
   há só os filtros de período, sem o Curso, e só as sessões das turmas dele (C1).
6. **Given** usuário sem sessão, **When** abre Relatórios, **Then** a tela de login, e depois o
   relatório.
7. **Given** Data Inicial 30/11/2026 e Final 01/11/2026, **Then** "A data inicial não pode ser
   superior à data final" e nada é consultado.
8. **Given** período sem dados, **Then** "Nenhum registro encontrado para os filtros selecionados"
   e os botões PDF, CSV e XLSX desabilitados.
9. **Given** Docente que não é Coordenador nem Professor da Disciplina, **Then** o item não aparece
   na lista (e o endereço direto devolve a MR-06).

### User Story 2 - Turmas e alunos (Priority: P2)

A Secretaria vê as turmas do período letivo, com a Descrição (TCC 1 ou TCC 2), o Professor da
Disciplina, o Total de Alunos e a lista de alunos com o Status do TCC, destacando Reprovado,
Desistente e Jubilado (US-49).

**Acceptance Scenarios** (US-49, cenários 1 a 8):

1. **Given** a turma de TCC 1 de 2026/2 com 7 alunos, 3 Sem Proposta, **When** abre com 2026/2 e
   aciona XLSX, **Then** a linha da turma tem TCC 1, o Professor, Total 7 e cada aluno com o
   Status, 3 com "Sem Proposta"; o XLSX tem as mesmas colunas e a lista de alunos.
2. **Given** um aluno Desistente, **Then** o Status dele aparece destacado.
3. **Given** o Coordenador de EC, **Then** o filtro Curso vem com EC.
4. **Given** o Professor da turma A e não da B, **Then** só a turma A, sem filtro Curso.
5. **Given** Curso Todos, **Then** as turmas de todos os cursos.
6. E1 (login); 7. E2 (sem registros, botões desabilitados); 8. E3 (perfil sem acesso).
9. **Given** uma turma de período anterior, **Then** o Status é o último registrado no histórico
   para aquela turma (CAD-08.7).

### User Story 3 - Aluno e orientador, apoio à matrícula (Priority: P2)

A Secretaria vê os alunos das turmas de TCC 1 do período com Matrícula, Nome do Aluno, Orientador
(aceito em TCC 1) e Status do TCC, com os Aprovados para TCC 2 primeiro e destacados (US-34).

**Acceptance Scenarios** (US-34, cenários 1 a 7):

1. **Given** 2 Aprovados para TCC 2 e 5 Em Andamento em 2026/2, **When** abre e aciona CSV,
   **Then** os 2 Aprovados no topo, destacados, depois os demais; o CSV na mesma ordem.
2. **Given** o Coordenador de LC, **Then** o filtro Curso vem com LC.
3. **Given** Professor da Disciplina não Coordenador, **Then** só o filtro Período letivo, e só os
   alunos das turmas dele (C1).
4. **Given** Curso Todos, **Then** os alunos de todos os cursos.
5. E1; 6. E2; 7. E3.
8. **Given** o aluno já matriculado em TCC 2, **When** abre o período de origem, **Then** continua
   como Aprovado para TCC 2 (CAD-08.7).

### User Story 4 - Horas complementares de ouvintes (Priority: P3)

A Secretaria vê uma linha por presença de ouvinte em sessão Realizada do período, com Nome do
Ouvinte, Matrícula, Data da Defesa e Horas (2 por linha), e o total de horas ao final (US-35).

**Acceptance Scenarios** (US-35, cenários 1 a 9):

1. **Given** o ouvinte 2415080011 em 3 sessões Realizadas de 2026/2, **When** abre e aciona XLSX,
   **Then** 3 linhas dele, cada uma com a data e 2 horas, e o total ao final; o XLSX igual.
2. **Given** um ouvinte numa sessão depois Cancelada, **Then** essa presença não aparece.
3. Datas (A); 4. Atalho (B); 5. Professor da Disciplina sem filtro Curso (C, recorte C1);
6. E1; 7. E2; 8. E3; 9. E4.

### Edge Cases

- Sessão Realizada cujo TCC está numa turma de outro curso: entra só com o Curso dela ou Todos.
- Suplente acionado: aparece na Banca no papel que ocupou; o não acionado, nunca (C4).
- Professor da Disciplina só de turma arquivada: continua com o papel (Q27 da spec 003) e vê essas
  turmas no período delas.
- Aluno transferido de turma: aparece na turma em que está matriculado (vínculo de
  `Alunos_Turmas`); o Status segue o último registro do TCC na turma (CAD-08.7).
- Conteúdo hostil em nomes e títulos: protegido na tela e nos arquivos pela exportação da spec 010
  (`proteger`, research R15).
- Id de curso forjado na URL (`?curso=²`): cai no curso padrão (Q-153).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Os quatro relatórios entram na lista da tela Relatórios para Coordenador de Curso,
  Secretaria e Professor da Disciplina, e para mais ninguém (RAN-REL-03; E3/E4 das US), na ordem
  Defesas realizadas no período, Turmas e alunos, Aluno e orientador (apoio à matrícula) e Horas
  complementares de ouvintes, depois dos relatórios da spec 010.
- **FR-002**: Filtros: 03.1 e 03.4 com o filtro de período das defesas (atalho, Ano/Semestre, Data
  Inicial e Data Final; padrão Período Letivo atual; RBN-DEF-01.5); 03.2 e 03.3 com "Período letivo"
  (Ano/Semestre). Coordenador de Curso e Secretaria também com o filtro Curso, padrão no curso do
  usuário (RBN-CAD-14.1). Professor da Disciplina não Coordenador: sem filtro Curso (C2).
- **FR-003**: Recorte do Professor da Disciplina não Coordenador: só as próprias turmas (C1), feito
  na consulta, valendo para tela e arquivo.
- **FR-010** (03.1): só as sessões com status Realizada do período; colunas Data/Horário, Aluno,
  Orientador, Banca, Modalidade do TCC e Parecer (C3 a C5).
- **FR-020** (03.2): uma linha por turma do período com Turma, TCC 1 ou TCC 2, Professor da
  Disciplina e Total de Alunos, e a sub-lista dos alunos com o Status do TCC (último registro do
  histórico do TCC na turma; "Sem Proposta" sem Proposta), destacando Reprovado, Desistente e
  Jubilado (C7).
- **FR-030** (03.3): alunos das turmas de TCC 1 do período com Matrícula, Nome do Aluno, Orientador
  e Status do TCC (CAD-08.7), Aprovados para TCC 2 primeiro e destacados (C6).
- **FR-040** (03.4): uma linha por presença de ouvinte em sessão Realizada do período, com Nome do
  Ouvinte, Matrícula, Data da Defesa e Horas = 2, e a linha Total com a soma das horas (C8).
- **FR-050**: Mensagens exatas das US: "A data inicial não pode ser superior à data final" e
  "Nenhum registro encontrado para os filtros selecionados"; sem registros, botões desabilitados
  (spec 010).
- **FR-051**: Exportação em PDF, CSV e XLSX pela base da spec 010, com as colunas, os destaques, a
  sub-lista, o total e os filtros da tela.
- **FR-052**: Somente leitura: nenhuma consulta grava (C9).

### Key Entities

Sem entidade nova. Leitura de Turmas, Alunos_Turmas, TCCs, Historico_Status_TCC, Orientacoes,
Defesas, Banca_Defesa, Ouvintes e Presenca_Ouvintes.

## Success Criteria *(mandatory)*

- **SC-001**: Os 33 cenários de aceite das US-48, 49, 34 e 35 viram testes e passam.
- **SC-002**: Tela e arquivo mostram as mesmas linhas, na mesma ordem, para os 4 relatórios
  (teste de igualdade tela × arquivo da spec 010).
- **SC-003**: Nenhum perfil fora de Coordenador, Secretaria e Professor da Disciplina abre os
  relatórios, nem pelo endereço direto.

## Assumptions

- O Período letivo de 03.2 e 03.3 lista os períodos com turma cadastrada mais o atual (spec 010).
- O total de 03.4 conta horas (2 por presença), não pessoas.

## Rastreabilidade

| US | RBN | Relatório (id) | Testes |
|---|---|---|---|
| US-48 | RBN-REL-03.1 | `defesas-realizadas` | `test_us48_defesas_realizadas.py` |
| US-49 | RBN-REL-03.2 | `turmas-alunos` | `test_us49_turmas_alunos.py` |
| US-34 | RBN-REL-03.3 | `aluno-orientador` | `test_us34_aluno_orientador.py` |
| US-35 | RBN-REL-03.4 | `horas-ouvintes` | `test_us35_horas_ouvintes.py` |

## Fora do escopo

- Integração com o Lyceum (REQ-WNT-04): o arquivo do 03.3 apoia o lançamento manual.
- Gráficos e KPIs: as US-48, 49, 34 e 35 não pedem.

## Mensagens a validar com a PO

| ID | Uso | Texto adotado | Situação |
|---|---|---|---|
| MR-15 | Descrição: Defesas realizadas no período | "Sessões Realizadas no período, com banca e parecer" | Adotada (C10) |
| MR-16 | Descrição: Turmas e alunos | "Turmas do período com o Status do TCC de cada aluno" | Adotada (C10) |
| MR-17 | Descrição: Aluno e orientador (apoio à matrícula) | "Alunos de TCC 1 com o orientador; Aprovados para TCC 2 primeiro" | Adotada (C10) |
| MR-18 | Descrição: Horas complementares de ouvintes | "Presenças de ouvintes nas sessões Realizadas, 2 horas cada" | Adotada (C10) |
