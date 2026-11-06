# Feature Specification: Dashboards de Produção do SIGTCC

**Feature Branch**: `feature/feat-10-dashboards`

**Created**: 2026-11-05

**Status**: Approved (Julia Cohen, 2026-11-05)

**Input**: User description: "Dashboards de Produção do SIGTCC (Épico 3): US-31, US-47, US-32 (com o Histórico de indicadores do NUCOMP, fluxo alternativo A) e US-33 (com o relatório de Artigos, fluxo alternativo D). Somente leitura, sem tabelas nem colunas novas. Esta feature é dona da base do módulo Relatórios, que a feat-11 vai consumir: tela Relatórios, registro dos relatórios, componente de filtros e exportação genérica em PDF, CSV e XLSX. Inclui como requisito de apresentação a seção Padrão visual de docs/metodologia/PASSO_A_PASSO_FEAT10.md."

**Responsável pela spec e pela implementação**: Julia Cohen. **Revisor do PR**: Célio Benjamim
(consome a base do módulo na feat-11). As US-31, 32, 33 e 47 ainda citam Maria Luiza Nobre como
responsável; a divisão vale pelo cronograma de 18/10, atividade 5.2.

**Fontes**: Histórias de Usuário v3.4 (US-31, US-47, US-32 e US-33); Matriz de Requisitos de 17/10,
aba `Requisitos_Relatorio` (RAN-REL-01 e RAN-REL-02: RBN-REL-01.1, 01.2, 02.1, 02.2, 02.3 e 02.4)
e as regras citadas por elas (RBN-CAD-05.4, 05.6, 05.7, 08.3, 08.6, 08.7, 09.5, 10.4, 10.5, 12.1, 12.3, 14.1 e RBN-DEF-01.5);
Modelo Lógico e Dicionário de 18/10; protótipo de 17/10 (telas "Relatórios"); seção "Padrão
visual" de `docs/metodologia/PASSO_A_PASSO_FEAT10.md`. As quatro US declaram "sem diagrama próprio:
consulta de relatório somente leitura".

## Dependências e reaproveitamento

- **Modelo de dados**: já existe (spec 001). Esta spec **não cria tabelas nem colunas** e nenhuma
  tela dela grava dados. Lê `Turmas`, `Alunos_Turmas`, `TCCs`, `Historico_Status_TCC`,
  `Orientacoes`, `Coorientacoes`, `Artigos`, `Areas_Interesse`, `Usuarios`, `Alunos`, `Docentes`,
  `Coordenadores`, `MembrosExternos`, `Defesas`, `Banca_Defesa` e `Cursos`.
- **Contrato da spec 007** (`specs/007-agendamento-banca/contracts/servicos-defesa.md`):
  - `FiltroPeriodoForm`, `filtro_de_periodo` e `periodo_letivo_atual` (§4), estendidos com
    Ano/Semestre **sem mudar o comportamento** da tela Defesas, da agenda e da lista de ouvintes
    (hoje "Período Letivo" só alcança o período atual; o parâmetro novo é opcional);
  - `membros_efetivos(sessao)`: Presidente, 1º e 2º Avaliador, com o Suplente acionado no lugar do
    titular ausente e sem o Suplente não acionado (US-31 e US-47).
- **Spec 002**: `services_contas.filtro_de_curso` e o curso padrão do usuário (RBN-CAD-14.1).
- **Spec 008 e 009**: `pdf.gerar_pdf` e `pdf.resposta_pdf` (geração em memória, sem acesso à rede;
  falha vira `ErroAoGerarPdf`, com log); templates de PDF com as fontes locais.
- **Bibliotecas**: `xhtml2pdf` e `openpyxl` já estão no `requirements.txt`. Nenhuma biblioteca nova,
  nem no servidor nem no navegador.
- **Telas e estilos existentes**: menu lateral (`cadastro/menu.py`), `sigtcc.css` (`.kpis`, `.kpi`,
  `.rel-layout`, `.inp`, `.tabela`, que é o nome local do `.tb` citado no guia, e os tokens `--azul`, `--verde`, `--vermelho`, `--roxo`, `--texto3`).
- **App**: `sigtcc/apps/relatorios` já está em `INSTALLED_APPS`, ainda sem rotas.

## Contratos desta feature

A feat-11 (Apoio Operacional, Célio Benjamim) consome esta base. O detalhe técnico fica em
`contracts/base-relatorios.md`, no plan; o compromisso é este:

- **C1. Registro dos relatórios**: cada relatório declara id, nome, descrição curta e perfis, no
  vocabulário de perfis que o sistema já usa, inclusive o Professor da Disciplina. O registro decide
  quem abre o relatório; o recorte das linhas (só o próprio docente, só as próprias turmas) fica na
  consulta do relatório, que recebe o usuário. Incluir um relatório novo é só registrá-lo: a lista,
  o menu, as permissões e a exportação não mudam.
- **C2. Filtros**: componente com Período (atalhos e datas), Ano/Semestre, Curso e Docente, num
  formulário próprio do módulo que herda o `FiltroPeriodoForm`. Cada relatório escolhe quais usa, e
  os filtros ficam no endereço da página. O `filtro_de_periodo` só ganha um parâmetro opcional de
  Ano/Semestre; a chamada atual continua igual. Filtro inválido não gera consulta nem arquivo: o
  recuo para o Período Letivo continua só nas telas da Defesa, sem mudança para elas.
- **C3. Estrutura do relatório**: uma estrutura única (título, filtros aplicados, colunas, linhas,
  sub-listas, KPIs, dados do gráfico e uma ou mais linhas de total com rótulo próprio) alimenta a
  tela e os três formatos de arquivo. A base mantém a ordem em que a consulta entrega as linhas, e a
  linha pode vir marcada com destaque. Isso cobre a feat-11 (lista ordenada e destacada, total de
  horas) sem mudar a base.
- **C4. Exportação**: PDF, CSV e XLSX genéricos a partir de C3, com as mesmas permissões da tela. As
  sub-listas têm uma coluna que identifica a linha-mãe. No XLSX, cada sub-lista é uma aba; no CSV,
  um arquivo só, com um bloco titulado por tabela, separado por uma linha em branco; no PDF, cada
  sub-lista vem depois da tabela principal, com título. O destaque aparece no PDF e no XLSX; no CSV,
  vale a ordem das linhas.
- **C5. Layout**: template base do Padrão visual, com parciais de gráfico.
- **Itens de configuração esperados** (em código de specs já mescladas, a aprovar no plan):
  `sigtcc/urls.py`, `cadastro/menu.py`, `defesa/forms_defesa.py`, `defesa/services_defesa.py` e o
  `popular_demo`.

## Clarifications

### Session 2026-11-05

Conferência do `analista-requisitos`; decisões de Julia Cohen.

- Q: Como buscar o Status de um aluno ou trabalho num período, se a transferência não grava histórico na turma de destino? → A: pelo último registro do histórico do TCC que está na turma do período, com desempate por data e hora e identificador; vínculo sem TCC conta como Sem Proposta (FR-041; ponto 1, D-01, D-03).
- Q: Como contar Matriculados quando o aluno tem dois vínculos no mesmo período? → A: contar vínculos, um TCC por vínculo, que é o único jeito de fechar a soma (FR-042; ponto 2, D-02).
- Q: Para onde o login leva quando a E1 aponta relatórios diferentes? → A: para o relatório do endereço pedido; `/relatorios/` sem relatório mostra a lista com a MR-05 (FR-004; ponto 3, D-05).
- Q: Os campos de data usam `min` e `max`? → A: não. A validação fica no servidor, para a mensagem exata da US aparecer junto ao campo. Isso se afasta do item 5 da heurística e do checklist de Nielsen do guia (FR-014 e FR-076; ponto 4, D-06).
- Q: Que papel o suplente acionado mostra na sub-lista Bancas? → A: "Suplente", contando pela função que exerceu (FR-025; ponto 5).
- Q: Quais links de artigo abrem fora do sistema? → A: só `https`, como na RBN-CAD-12.1; o resto aparece como texto (FR-066; ponto 6, D-13).
- Q: O filtro Curso do Painel usa qual curso, já que a RBN-CAD-05.7 e o glossário divergem? → A: o Curso de Lotação do docente, sem cortar as contagens (FR-027; ponto 7, D-04; índice Q-152).
- Q: A gestão lista só docentes com atividade (P1)? → A: não. Lista todos os docentes do filtro, com zeros, e a E3 vale só quando nenhum deles tem atividade; atende à matriz e ao cenário 10 (FR-021 e FR-027; ponto 8; índice Q-150).
- Q: Quais vínculos contam para o docente num período passado ou depois de uma troca? → A: todos os vínculos do TCC da turma, Ativa, Encerrada ou Substituída; numa troca, os dois docentes contam. Na coluna Orientador de Artigos: o vínculo ativo; sem ele, o mais recente; sem nenhum, "Sem orientador" (FR-023 e FR-065; ponto 9; índice Q-148).
- Q: Como contar orientações e coorientações num intervalo de datas? → A: conta o vínculo em vigor em algum dia do intervalo. Um intervalo que cruze a matrícula no TCC 2 conta o aluno em TCC 1 e em TCC 2, o que o bloco "Como é calculado" explica (FR-022; ponto 10; índice Q-147).
- Q: Em qual período letivo conta o artigo copiado do TCC 1 para o TCC 2? → A: uma vez, no período do primeiro TCC do aluno com Publicado, sempre com a modalidade Artigo Científico (FR-052; ponto 11, D-07; índice Q-149).
- Q: O que a coluna Aproveitamento mostra sem análise? → A: "Aguardando aceite ou publicação" (MO-22 da spec 006), provisória como MR-14 (FR-065; ponto 12, D-07; índice Q-146).
- Q: As premissas P2, P3 e P4 ficam como estão? → A: sim: docente específico prevalece sobre o filtro Curso; o arquivo da US-33 segue o agrupamento da tela; a Secretaria usa Curso Todos, pela RBN-CAD-14.1 (Assumptions; índice Q-150).
- Q: Na visão de gestão com Docente "Todos", quais docentes aparecem? → A: todo docente com conta Ativa, mesmo com zeros; Inativos e Aguardando Ativação só se tiverem atividade no período (FR-021; `/speckit-clarify`; índice Q-152).
- Q: Como declarar o Professor da Disciplina e o recorte por turma da feat-11? → A: o registro declara os perfis com o vocabulário existente, e o recorte fica na consulta, como no Docente comum (C1; ponto 13). Decisão de Julia Cohen a partir da análise; Célio Benjamim deve tomar ciência (índice Q-151).
- Q: A estrutura do relatório prevê destaque, ordenação e total de horas? → A: sim, sem regra da feat-11 na base: ordem entregue pela consulta, marca de destaque e linhas de total com rótulo próprio (C3; ponto 14; índice Q-151).
- Q: Como as sub-listas saem nos arquivos? → A: abas no XLSX, blocos titulados num único CSV e seções no PDF, com a coluna da linha-mãe (C4; ponto 15; índice Q-151).
- Q: Como estender o filtro de período sem quebrar a Defesa? → A: formulário próprio do módulo, herdando o `FiltroPeriodoForm`, e parâmetro opcional no `filtro_de_periodo`; filtro inválido não consulta nem exporta (C2; ponto 16; índice Q-151).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Painel de atividades por docente, sobre a base do módulo (Priority: P1)

O Docente consulta e exporta o próprio extrato de orientações, coorientações e bancas para
comprovar as suas atividades; o Coordenador de Curso e a Secretaria consultam qualquer docente.
Esta história entrega também a base do módulo: item Relatórios no menu, lista por perfil, filtros,
exportação e layout. [US-31][RBN-REL-01.1][RBN-CAD-14.1][RBN-DEF-01.5]

**Why this priority**: é Must Have, é o único relatório aberto a todo Docente e prova a base de que
a feat-11 depende.

**Independent Test**: como Docente, abrir Relatórios, ver a própria linha e baixar os três arquivos;
como Coordenador, ver todos os docentes e filtrar por curso; como Aluno, não ver o item no menu.

**Acceptance Scenarios**:

1. **Dado que** o Docente está autenticado e é orientador de 1 aluno em TCC 1 e de 1 aluno em TCC 2,
   **Quando** abre a tela de atividades por docente com o período letivo 2026/2, expande a linha e
   aciona o botão PDF, **Então** a tela exibe apenas a linha do Docente, com Orientandos em TCC 1
   igual a 1 e Orientandos em TCC 2 igual a 1, sem os filtros Docente e Curso, **E** o navegador
   baixa o PDF com a linha e as sub-listas exibidas.
2. **Dado que** o usuário está na tela do relatório, **Quando** informa a Data Inicial 01/09/2026 e
   a Data Final 30/09/2026 no calendário, **Então** a pré-visualização considera apenas o intervalo
   informado.
3. **Dado que** o usuário está na tela do relatório, **Quando** seleciona o atalho Este Mês no
   filtro Período, **Então** o sistema preenche Data Inicial e Data Final com o primeiro e o último
   dia do mês e atualiza a pré-visualização.
4. **Dado que** o Coordenador de Curso de Sistemas de Informação está autenticado, **Quando** abre
   a tela de atividades por docente, **Então** a tela exibe os filtros Docente, com "Todos", e
   Curso, com Sistemas de Informação, e uma linha por docente.
5. **Dado que** a Secretaria está na tela de atividades por docente, **Quando** seleciona um docente
   no filtro Docente, **Então** a pré-visualização exibe apenas a linha desse docente.
6. **Dado que** o Docente não orienta nem coorienta nenhum aluno no período, **Quando** expande a
   sua linha, **Então** a sub-lista Orientações e coorientações exibe "Nenhum registro".
7. **Dado que** o Docente não participou de nenhuma banca Realizada no período, **Quando** expande
   a sua linha, **Então** a sub-lista Bancas exibe "Nenhum registro" e o Total de Bancas é 0.
8. **Dado que** o usuário não está autenticado, **Quando** tenta abrir o endereço do relatório
   tela de atividades por docente, **Então** o sistema exibe a tela de login (US-11), **E**, após o
   login, abre esse relatório.
9. **Dado que** o usuário está na tela do relatório, **Quando** informa a Data Inicial 30/11/2026 e
   a Data Final 01/11/2026, **Então** o sistema não atualiza a pré-visualização e exibe "A data
   inicial não pode ser superior à data final".
10. **Dado que** o Coordenador de Curso filtrou um curso sem docentes com atividade no período,
    **Quando** o sistema atualiza a pré-visualização, **Então** exibe a tabela vazia com a mensagem
    "Nenhum registro encontrado para os filtros selecionados", **E** os botões PDF, CSV e XLSX
    permanecem desabilitados.
11. **Dado que** o usuário autenticado é Aluno, **Quando** abre o menu lateral, **Então** o item
    Relatórios não aparece.
12. **Dado que** o Docente comum está autenticado, **Quando** altera o endereço da página para
    pedir outro docente ou outro curso, na tela ou na exportação, **Então** o sistema ignora esses
    valores e continua mostrando só a própria linha (RAN-REL-01, Confidencialidade).
13. **Dado que** o usuário é Aluno ou Membro Externo, **Quando** abre pelo endereço direto a tela
    Relatórios, um relatório ou uma exportação, **Então** o acesso é negado.
14. **Dado que** o Docente é Professor da Disciplina sem ser Coordenador de Curso, **Quando** abre a
    tela Relatórios, **Então** vê a lista do Docente: só o Painel, com a própria linha.
15. **Dado que** o Coordenador está com um curso em que só um de 3 docentes teve atividade no período,
    **Quando** abre o painel, **Então** a tabela mostra os 3 docentes, 2 deles com zeros (RBN-REL-01.1).

---

### User Story 2 - Produção de TCCs e Artigos (Priority: P1)

O Coordenador de Curso consulta e exporta a produção de TCCs, agrupada por curso, área de interesse
ou modalidade, e a lista de artigos, para analisar as áreas de maior interesse e a produção
científica do curso. [US-33][RBN-REL-02.1][RBN-REL-02.2]

**Why this priority**: é Must Have e estabelece a classificação de Status em Ativos, Com Sucesso e
Sem Sucesso que a história seguinte reaproveita.

**Independent Test**: com trabalhos conhecidos em uma turma, conferir os totais em cada agrupamento
e abrangência; abrir Artigos e conferir as colunas; conferir que Total de Trabalhos = Ativos + Com
Sucesso + Sem Sucesso em toda linha.

**Acceptance Scenarios**:

1. **Dado que** Engenharia de Computação tem 10 trabalhos em 2026/2: 9 Ativos, 1 Com Sucesso e 0 Sem
   Sucesso, **Quando** o Coordenador de Curso abre Produção de TCCs agrupado por Curso e aciona o
   botão PDF, **Então** a pré-visualização exibe Total de Trabalhos 10, Ativos 9, Com Sucesso 1 e
   Sem Sucesso 0, **E** o navegador baixa o PDF com as colunas Total de Trabalhos, Ativos, Com
   Sucesso e Sem Sucesso.
2. **Dado que** um trabalho do período não tem Área de Interesse preenchida, **Quando** o
   Coordenador seleciona Área de Interesse no filtro Agrupar por, **Então** a pré-visualização exibe
   uma linha por área e esse trabalho na linha "Não informada".
3. **Dado que** o Coordenador está em Produção de TCCs, **Quando** seleciona Modalidade no filtro
   Agrupar por, **Então** a pré-visualização exibe as linhas Monografia e Artigo Científico.
4. **Dado que** o período tem 1 trabalho Concluído e 9 Ativos, **Quando** o Coordenador seleciona
   Apenas Concluídos no filtro Abrangência, **Então** a pré-visualização considera apenas o trabalho
   Concluído.
5. **Dado que** o período tem um TCC na modalidade Artigo Científico com aproveitamento Homologado,
   **Quando** o Coordenador seleciona Artigos, **Então** a pré-visualização exibe o Título do TCC,
   Aluno, Orientador, Veículo, Estrato Qualis/CAPES, Status de Submissão, Aproveitamento Homologado
   e o Link ou DOI.
6. **Dado que** o Coordenador está em Produção de TCCs, **Quando** seleciona Todos no filtro Curso,
   **Então** a pré-visualização considera os trabalhos de todos os cursos do NUCOMP.
7. **Dado que** o usuário não está autenticado, **Quando** tenta abrir o endereço do relatório
   Produção de TCCs, **Então** o sistema exibe a tela de login (US-11), **E**, após o login, abre
   esse relatório.
8. **Dado que** não há dados para o período selecionado no relatório Produção de TCCs, **Quando** o
   sistema atualiza a pré-visualização, **Então** exibe a tabela vazia com a mensagem "Nenhum
   registro encontrado para os filtros selecionados", **E** os botões PDF, CSV e XLSX permanecem
   desabilitados.
9. **Dado que** o usuário autenticado não é Coordenador de Curso, **Quando** abre a tela Relatórios,
   **Então** os itens Produção de TCCs e Artigos não aparecem na lista.
10. **Dado que** o usuário não é Coordenador de Curso, **Quando** abre pelo endereço direto a tela
    ou a exportação de Produção de TCCs ou de Artigos, **Então** o acesso é negado.

---

### User Story 3 - Formação e evasão (Priority: P1)

O Coordenador de Curso consulta e exporta a situação dos alunos de um período letivo, por curso.
[US-32][RBN-REL-02.3][RBN-CAD-08.7][Q-02]

**Why this priority**: é Must Have e é a conta mais sensível do módulo: toda linha precisa fechar
com o histórico do Status do TCC.

**Independent Test**: com uma turma de composição conhecida, conferir as colunas; conferir que
Matriculados = Sem Proposta + Ativos + Com Sucesso + Sem Sucesso em toda linha e no Total; gerar um
período passado e conferir a contagem pelo histórico.

**Acceptance Scenarios**:

1. **Dado que** a turma de Engenharia de Computação de 2026/2 tem 12 alunos: 2 Sem Proposta, 9
   Ativos, 1 Com Sucesso e 0 Sem Sucesso, **Quando** o Coordenador de Curso abre Formação e evasão
   com o período 2026/2 e aciona o botão CSV, **Então** a pré-visualização exibe Matriculados 12,
   Sem Proposta 2, Ativos 9, Com Sucesso 1 e Sem Sucesso 0, **E** o navegador baixa o arquivo CSV
   com as colunas Curso, Matriculados, Sem Proposta, Ativos, Com Sucesso e Sem Sucesso.
2. **Dado que** o período 2026/2 tem 8 alunos matriculados, **Quando** o Coordenador gera o
   relatório desse período, **Então** a soma de Sem Proposta, Ativos, Com Sucesso e Sem Sucesso é
   igual a 8.
3. **Dado que** um aluno de TCC 2 está com o Status Aprovado e sem Versão Final homologada,
   **Quando** o Coordenador gera o relatório do período, **Então** esse aluno é contado na coluna
   Ativos, e não em Com Sucesso.
4. **Dado que** um aluno foi Aprovado para TCC 2 na turma de 2026/1 e hoje está Em Andamento na
   turma de TCC 2 de 2026/2, **Quando** o Coordenador gera o relatório de 2026/1, **Então** esse
   aluno é contado na coluna Com Sucesso de 2026/1.
5. **Dado que** o Coordenador está em Formação e evasão, **Quando** seleciona Todos no filtro Curso,
   **Então** a pré-visualização exibe uma linha por curso do NUCOMP e a linha Total.
6. **Dado que** o usuário não está autenticado, **Quando** tenta abrir o endereço do relatório
   Formação e evasão, **Então** o sistema exibe a tela de login (US-11), **E**, após o login, abre
   esse relatório.
7. **Dado que** não há dados para o período selecionado no relatório Formação e evasão, **Quando** o
   sistema atualiza a pré-visualização, **Então** exibe a tabela vazia com a mensagem "Nenhum
   registro encontrado para os filtros selecionados", **E** os botões PDF, CSV e XLSX permanecem
   desabilitados.
8. **Dado que** o usuário autenticado não é Coordenador de Curso, **Quando** abre a tela Relatórios,
   **Então** os itens Formação e evasão e Histórico de indicadores do NUCOMP não aparecem na lista.
9. **Dado que** o usuário não é Coordenador de Curso, **Quando** abre pelo endereço direto a tela ou
   a exportação de Formação e evasão, **Então** o acesso é negado.
10. **Dado que** um aluno foi transferido dentro do mesmo período e o Status não mudou depois,
    **Quando** o Coordenador gera o relatório, **Então** o aluno conta uma vez, na turma de destino,
    e a soma das colunas continua igual a Matriculados (RBN-CAD-05.6).

---

### User Story 4 - Histórico de indicadores do NUCOMP (Priority: P2)

O Coordenador de Curso acompanha a evolução do NUCOMP ao longo dos semestres.
[US-32 fluxo A][RBN-REL-02.4]

**Why this priority**: é Should Have e reaproveita a base e as definições das histórias anteriores.

**Independent Test**: com três períodos cadastrados, conferir as três linhas, em ordem, e a ausência
de filtro de período.

**Acceptance Scenarios**:

1. **Dado que** o sistema tem os períodos 2025/2, 2026/1 e 2026/2, **Quando** o Coordenador
   seleciona Histórico de indicadores do NUCOMP, **Então** o sistema exibe 3 linhas, de 2025/2 a
   2026/2, com Alunos Vinculados, Defesas Realizadas, Artigos Publicados e Desistências, sem filtro
   de período.
2. **Dado que** o usuário autenticado não é Coordenador de Curso, **Quando** abre o relatório pelo
   endereço direto, **Então** o acesso é negado.

---

### User Story 5 - Participação de Membros Externos (Priority: P3)

O Coordenador de Curso e a Secretaria consultam e exportam a participação de docentes do NUCOMP e de
Membros Externos nas bancas realizadas no período, com as instituições de origem dos externos.
[US-47][RBN-REL-01.2]

**Why this priority**: é Could Have e fica por último na ordem de implementação.

**Independent Test**: com sessões Realizadas de banca conhecida, conferir que cada pessoa conta uma
vez e que o Suplente não acionado não entra.

**Acceptance Scenarios**:

1. **Dado que** no período 2026/2 houve sessões Realizadas com 4 docentes do NUCOMP e 1 Membro
   Externo da Universidade Federal do Amazonas, **Quando** o Coordenador de Curso abre o relatório
   com o período 2026/2 e aciona o botão XLSX, **Então** a pré-visualização exibe Docentes do NUCOMP
   4, Membros Externos 1 e Instituição de origem: Universidade Federal do Amazonas 1, **E** o
   navegador baixa o arquivo XLSX com as colunas Descrição e Quantidade.
2. **Dado que** o usuário está na tela do relatório, **Quando** informa a Data Inicial 01/09/2026 e
   a Data Final 30/09/2026 no calendário, **Então** a pré-visualização considera apenas o intervalo
   informado.
3. **Dado que** o usuário está na tela do relatório, **Quando** seleciona o atalho Este Mês no
   filtro Período, **Então** o sistema preenche Data Inicial e Data Final com o primeiro e o último
   dia do mês e atualiza a pré-visualização.
4. **Dado que** o Coordenador está no relatório, **Quando** seleciona Todos no filtro Curso,
   **Então** a pré-visualização considera as sessões de todos os cursos do NUCOMP.
5. **Dado que** a Secretaria de Engenharia de Computação está autenticada, **Quando** abre o
   relatório Participação de Membros Externos, **Então** o filtro Curso aparece preenchido com
   Engenharia de Computação.
6. **Dado que** o usuário não está autenticado, **Quando** tenta abrir o endereço do relatório
   Participação de Membros Externos, **Então** o sistema exibe a tela de login (US-11), **E**, após o
   login, abre esse relatório.
7. **Dado que** o usuário está na tela do relatório, **Quando** informa a Data Inicial 30/11/2026 e
   a Data Final 01/11/2026, **Então** o sistema não atualiza a pré-visualização e exibe "A data
   inicial não pode ser superior à data final".
8. **Dado que** não há dados para o período selecionado no relatório Participação de Membros
   Externos, **Quando** o sistema atualiza a pré-visualização, **Então** exibe a tabela vazia com a
   mensagem "Nenhum registro encontrado para os filtros selecionados", **E** os botões PDF, CSV e
   XLSX permanecem desabilitados.
9. **Dado que** o usuário autenticado é Docente e não é Coordenador de Curso, **Quando** abre a tela
   Relatórios, **Então** o item Participação de Membros Externos não aparece na lista.
10. **Dado que** o usuário autenticado é Docente e não é Coordenador de Curso, **Quando** abre pelo
    endereço direto a tela ou a exportação de Participação de Membros Externos, **Então** o acesso é
    negado.

---

### Edge Cases

- **Atalho no futuro**: Próximos 30 Dias não alcança sessões Realizadas; o Total de Bancas tende a 0
  e o relatório segue a E3 quando nada mais houver.
- **Aluno transferido no mesmo período**: conta uma vez, na turma de destino (`Alunos_Turmas`); o
  histórico da turma de origem não gera uma segunda contagem.
- **Aluno excluído da turma (RBN-CAD-05.4)**: sai de Matriculados e de Alunos Vinculados. O aluno
  que desiste **com** Proposta continua em Matriculados, em Sem Sucesso (regra confirmada em Q-02).
  A desistência **sem** Proposta segue a US, aberta na Q-02.
- **TCC 1 aprovado e TCC 2 no período seguinte**: cada período conta o seu próprio TCC, pelo
  histórico (US-32, cenário 4).
- **Suplente**: o acionado conta como membro da banca; o não acionado, não; o titular substituído
  não conta naquela sessão (US-31 e US-47, pelo `membros_efetivos`).
- **Mesma pessoa em várias bancas**: conta 1 em Membros Externos (pessoas distintas).
- **Coorientador externo**: não é docente do NUCOMP e não gera linha no painel de atividades.
- **Membro Externo como usuário**: não tem o item Relatórios (US-31, pré-condição 2; US-47).
- **Instituição escrita de duas formas**: o campo é texto; cada grafia é uma linha. O relatório não
  corrige nem unifica cadastros.
- **Artigo Científico sem dados de publicação**: o TCC aparece em Artigos, com as células de
  publicação vazias e a MR-14 em Aproveitamento.
- **TCC que virou Monografia**: a linha em `Artigos` continua, mas o artigo não entra no relatório
  Artigos nem em Artigos Publicados.
- **Aluno com dois vínculos no mesmo período** (Reprovado ou Aprovado para TCC 2 matriculado em outra
  turma): conta um Matriculado por vínculo, cada um com o seu TCC.
- **Curso com 0 Matriculados**: a linha aparece com zeros, sem barra 100%.
- **Período atual sem turma**: aparece na lista Ano/Semestre e o relatório segue a E3.
- **Conteúdo com aparência de fórmula** (título começando com `=`, `+`, `-` ou `@`): CSV e XLSX o
  gravam como texto, sem executar nada ao abrir na planilha.
- **Falha ao gerar o PDF**: o usuário continua na tela, com aviso, e nada é baixado (MR-07).
- **Exportação pedida com filtro inválido ou sem registros** (por endereço direto): nenhum arquivo é
  gerado; a tela mostra a mensagem correspondente.
- **Período sem turma do curso filtrado no Histórico**: a linha do período aparece com zeros.
- **Sem nenhum período cadastrado**: o Histórico segue a E2 da US-32.

## Requirements *(mandatory)*

### Functional Requirements

**Base do módulo: acesso e lista**

- **FR-001**: O menu lateral MUST exibir o item "Relatórios" na área Gestão para os perfis Docente
  (inclui o Coordenador de Curso) e Secretaria. Aluno e Membro Externo MUST NOT ver o item.
  [US-31 E4][US-47][US-32][US-33]
- **FR-002**: A tela Relatórios MUST listar apenas os relatórios do perfil, cada um com nome e uma
  linha de descrição (MR-08 a MR-13), conforme a tabela abaixo. Selecionar um item abre o relatório
  no próprio layout. O Professor da Disciplina usa a coluna Docente.
  [US-31 passo 2][US-47 E4][US-32 E3][US-33 E3]

  | Relatório | Docente | Coordenador de Curso | Secretaria |
  |---|---|---|---|
  | Painel de atividades por docente | só o próprio | todos | todos |
  | Participação de Membros Externos | — | sim | sim |
  | Formação e evasão | — | sim | — |
  | Histórico de indicadores do NUCOMP | — | sim | — |
  | Produção de TCCs | — | sim | — |
  | Artigos | — | sim | — |

- **FR-003**: O registro dos relatórios MUST guardar id, nome, descrição curta e perfis, de modo que
  a feat-11 inclua relatórios sem alterar a lista, as permissões nem a exportação (C1).
- **FR-004**: A tela Relatórios, toda tela de relatório e toda exportação MUST conferir o perfil no
  servidor. O acesso por endereço direto de quem não tem o perfil MUST ser negado (MR-06). O usuário
  sem sessão vai ao login (US-11) e volta ao endereço pedido; o endereço da tela Relatórios, sem
  relatório, mostra a lista com a MR-05. [US-31 E1][US-47 E1][US-32 E1][US-33 E1]
- **FR-005**: As telas e as exportações desta feature MUST NOT alterar dados.
  [Pós-condições das US-31, 47, 32 e 33]

**Base do módulo: filtros**

- **FR-010**: O componente de filtros MUST oferecer Período (lista: Período Letivo, Esta Semana,
  Este Mês ou Próximos 30 Dias), Ano/Semestre, Data Inicial, Data Final (DD/MM/AAAA, por calendário),
  Curso (Engenharia de Computação, Sistemas de Informação, Licenciatura em Computação ou Todos) e
  Docente ("Todos" e cada docente do NUCOMP; padrão "Todos"), e cada relatório declara quais usa (C2).
  [RBN-DEF-01.5][RBN-CAD-14.1]
- **FR-011**: O componente MUST reaproveitar o `FiltroPeriodoForm` e o `filtro_de_periodo` da feat-07.
  A extensão com Ano/Semestre MUST deixar a tela Defesas, a agenda e a lista de ouvintes com o
  comportamento atual, comprovado pelos testes dessas telas. [RBN-DEF-01.5]
- **FR-012**: O filtro Período MUST vir, por padrão, com o período letivo atual; os atalhos preenchem
  Data Inicial e Data Final; as datas informadas valem como intervalo e prevalecem sobre o Ano/Semestre; o atalho Período Letivo usa o
  Ano e o Semestre da turma do TCC. [US-31 A, B][US-47 A, B][RBN-DEF-01.5]
- **FR-013**: A lista Ano/Semestre MUST trazer os períodos com turma cadastrada e o período atual, que
  é o selecionado por padrão. [US-32 passo 3][US-33 passo 3]
- **FR-014**: Data Inicial posterior à Data Final MUST impedir a atualização e exibir, junto ao campo,
  "A data inicial não pode ser superior à data final", pela validação do servidor, sem resultado de
  outro período e sem arquivo. Data inexistente ou só uma das datas preenchida MUST seguir a mensagem
  do `FiltroPeriodoForm`. [US-31 E2][US-47 E2]
- **FR-015**: O filtro Curso MUST vir preenchido com o curso do usuário (Curso Coordenado ou Curso
  Vinculado), aceita Todos e afeta só a visualização, sem exceção para a Secretaria. A troca vale só
  para a tela aberta: ao abrir outro relatório, os filtros voltam ao padrão.
  [RBN-CAD-14.1][US-31 C][US-47 D]
- **FR-016**: Para o Docente comum, os filtros Docente e Curso MUST NOT aparecer, e valores desses
  filtros recebidos pelo endereço MUST ser ignorados na tela e na exportação.
  [US-31 passo 3][RAN-REL-01]
- **FR-017**: Resultado sem registros MUST exibir a tabela vazia com "Nenhum registro encontrado para
  os filtros selecionados", seguida da sugestão MR-01, e MUST deixar PDF, CSV e XLSX desabilitados.
  [US-31 E3][US-47 E3][US-32 E2][US-33 E2]

**Exportação**

- **FR-018**: Cada relatório MUST ter os botões PDF, CSV e XLSX no canto superior direito. O arquivo
  MUST sair da mesma estrutura da tela (C3), com as mesmas colunas, na mesma ordem, os mesmos filtros e
  a data e hora de geração, e o usuário MUST permanecer na tela. [US-31 passo 9][US-47 passo 7]
  [US-32 passo 7][US-33 passo 7]
- **FR-019**: O CSV MUST abrir correto em planilha (acentos e separação de colunas) e, junto com o
  XLSX, MUST gravar como texto o conteúdo que uma planilha interpretaria como fórmula. No CSV, isso
  pode acrescentar um caractere de proteção no início da célula, e essa é a única diferença permitida
  entre o arquivo e a tela (SC-005).
- **FR-020**: O PDF MUST conter cabeçalho, filtros aplicados, KPIs em tabela simples e a tabela da US,
  sem gráfico.

**Painel de atividades por docente (US-31)**

- **FR-021**: O relatório MUST exibir as colunas Docente, Curso (Curso de Lotação), Quantidade de
  Orientandos em TCC 1, Quantidade de Orientandos em TCC 2, Quantidade de Coorientações (aceitas) e
  Total de Bancas no período (sessões Realizadas em que atuou como Presidente, 1º Avaliador, 2º
  Avaliador ou Suplente acionado). O Docente comum vê uma única linha, a própria, inclusive com zeros;
  o Coordenador e a Secretaria veem uma linha por docente do filtro, também com zeros: todo docente com
  conta Ativa e os Inativos ou Aguardando Ativação com atividade no período. Com Docente "Todos", se
  nenhum deles tiver atividade no período, vale a E3 (FR-017); o docente escolhido no filtro sempre
  tem a linha, como o Docente comum. [US-31 passo 5, C, E3][RBN-REL-01.1][RBN-CAD-10.4]
  [RAN-REL-01]
- **FR-022**: Com o atalho Período Letivo, as orientações e coorientações MUST contar pelas turmas do
  Ano/Semestre selecionado, separadas em TCC 1 e TCC 2 pela turma. Com Esta Semana, Este Mês, Próximos
  30 Dias ou datas informadas, MUST contar o vínculo em vigor em algum dia do intervalo, pelas datas de
  início e fim, classificado pela turma do TCC. Um intervalo que cruze a matrícula no TCC 2 conta o
  aluno em TCC 1 e em TCC 2, e o bloco "Como é calculado" MUST dizer isso.
  [US-31 passo 5, A, B, cenário 2][RBN-REL-01.1][Q-147]
- **FR-023**: MUST contar todos os vínculos do TCC da turma, Ativa, Encerrada ou Substituída: contar só
  os ativos zeraria os períodos passados, porque a matrícula no TCC 2 encerra os vínculos do TCC 1.
  Numa troca de orientador, os dois docentes contam, e a soma das linhas pode passar do número de
  alunos. Dentro da linha, cada aluno conta uma vez por coluna, mesmo com dois vínculos com o docente. [RBN-REL-01.1][RBN-CAD-08.6][Q-148]
- **FR-024**: Total de Bancas MUST contar as sessões Realizadas: pela turma do TCC no atalho Período
  Letivo e pela data da sessão nos demais. [US-31 passo 5][RBN-DEF-01.5]
- **FR-025**: Cada linha MUST expandir, por clique ou teclado (Enter ou Espaço), nas sub-listas
  "Orientações e coorientações" (Nome do Aluno, Título do Trabalho, Papel (Orientador ou Coorientador) e
  Status do TCC) e "Bancas" (Data, Papel na banca, Nome do Aluno e Título do Trabalho). O suplente
  acionado aparece com o papel "Suplente". Sub-lista vazia MUST exibir "Nenhum registro".
  [US-31 passos 6 e 7, D, E][RBN-CAD-08.3]
- **FR-026**: A exportação MUST incluir as sub-listas. [US-31 passo 9][RBN-REL-01.1]
- **FR-027**: O filtro Curso MUST usar o Curso de Lotação do docente e MUST NOT cortar as contagens: a
  linha traz toda a atividade do docente, de qualquer curso. Um docente específico no filtro Docente
  prevalece sobre o Curso (premissa P2). [US-31 C, cenários 4 e 5][Q-152]

**Participação de Membros Externos (US-47)**

- **FR-030**: O relatório MUST exibir as colunas Descrição e Quantidade: uma linha "Docentes do NUCOMP"
  e uma "Membros Externos", com pessoas distintas que atuaram como membros efetivos nas sessões
  Realizadas do período, e uma linha "Instituição de origem: <nome>" por instituição, com a quantidade
  de Membros Externos distintos. [US-47 passo 5][RBN-REL-01.2]
- **FR-031**: Os filtros MUST ser Período (como em FR-012) e Curso; o Curso considera o curso da turma
  do TCC da sessão, e Todos considera as sessões de todos os cursos. [US-47 C, D][RBN-CAD-05.7][RBN-CAD-14.1]

**Classificação pelo Status do TCC (US-32 e US-33)**

- **FR-040**: A classificação MUST ser única para os relatórios: **Ativos** = Em Andamento, Apto para
  Defesa, Aprovado e Aprovado com Correções sem Versão Final homologada; **Com Sucesso** = Concluído e
  Aprovado para TCC 2; **Sem Sucesso** = Reprovado, Desistente e Jubilado; **Sem Proposta** só existe
  em Formação e evasão. A homologação da Versão Final já muda o Status para Concluído, então a
  classificação olha só o Status, sem consultar as entregas. [RBN-REL-02.1][RBN-REL-02.3]
  [RBN-CAD-08.3][RBN-CAD-09.5]
- **FR-041**: Cada aluno ou trabalho MUST ser contado pelo último registro do histórico do TCC que está
  na turma do período, com desempate por data e hora e identificador, sem divergência em relação ao
  histórico. A busca é pelo TCC, e não pela turma do registro, porque a transferência não grava
  histórico na turma de destino. Vínculo sem TCC conta como Sem Proposta.
  [RBN-CAD-08.7][RAN-REL-02][RBN-CAD-05.6]

**Formação e evasão (US-32)**

- **FR-042**: O relatório MUST exibir uma linha por curso da turma e a linha Total, nas colunas Curso,
  Matriculados (alunos vinculados às turmas do período, exceto os excluídos da turma, um por vínculo), Sem
  Proposta, Ativos, Com Sucesso e Sem Sucesso, com Sem Proposta + Ativos + Com Sucesso + Sem Sucesso = Matriculados
  em toda linha e no Total. Com Curso Todos, MUST exibir uma linha por curso do NUCOMP.
  [US-32 passo 5, B][RBN-REL-02.3]
- **FR-043**: A saída de Matriculados por exclusão MUST seguir a US: o aluno excluído da turma não conta.
  A Q-02 segue aberta para o aluno sem Proposta; o aluno que desiste com Proposta continua em
  Matriculados, em Sem Sucesso. [US-32 passo 5][RBN-CAD-05.4][Q-02]

**Histórico de indicadores do NUCOMP (US-32 fluxo A)**

- **FR-050**: O relatório MUST exibir só o filtro Curso e uma linha por período letivo cadastrado, do
  mais antigo ao mais recente, com as colunas Período letivo, Alunos Vinculados, Defesas Realizadas,
  Artigos Publicados e Desistências. [US-32 A][RBN-REL-02.4]
- **FR-051**: Alunos Vinculados MUST usar a definição de Matriculados; Defesas Realizadas MUST contar as
  sessões Realizadas pela turma do TCC; Desistências MUST contar as transições para Desistente no
  histórico da turma do período. Nenhum indicador tem data própria de semestre: o período é o da turma.
  [RBN-REL-02.4][RBN-CAD-08.7]
- **FR-052**: Artigos Publicados MUST contar os artigos com Status de Submissão Publicado de TCCs na
  modalidade Artigo Científico. `Artigos` não tem data de publicação, e o artigo do TCC 1 é copiado
  para o TCC 2; por isso, cada artigo conta uma vez, no período do primeiro TCC do aluno com Publicado.
  [RBN-REL-02.4][RBN-CAD-12.1][Q-149]

**Produção de TCCs (US-33)**

- **FR-060**: O relatório MUST oferecer os filtros Período letivo, Agrupar por (Curso, Área de Interesse
  ou Modalidade; padrão Curso), Abrangência (Todos, Todos os Aprovados ou Apenas Concluídos; padrão
  Todos) e Curso. [US-33 passo 3][RBN-REL-02.1]
- **FR-061**: O relatório MUST exibir uma linha por valor do agrupamento e a linha Total, nas colunas
  Total de Trabalhos, Ativos, Com Sucesso e Sem Sucesso, precedidas da coluna do agrupamento, com Total
  de Trabalhos = Ativos + Com Sucesso + Sem Sucesso em toda linha. TCCs Sem Proposta não entram.
  [US-33 passo 5][RBN-REL-02.1]
- **FR-062**: O agrupamento por Área de Interesse MUST exibir uma linha por uma das 10 áreas e, se
  houver, a linha "Não informada"; o agrupamento por Modalidade MUST exibir Monografia e Artigo
  Científico. [US-33 A, B]
- **FR-063**: A abrangência Todos os Aprovados MUST considerar Aprovado para TCC 2, Aprovado, Aprovado
  com Correções e Concluído; Apenas Concluídos, somente Concluído. [US-33 C][RBN-REL-02.1]
- **FR-064**: O arquivo exportado MUST seguir o agrupamento escolhido na tela (premissa P3).
  [US-33 passo 7][Padrão visual, heurística 4]

**Artigos (US-33 fluxo D)**

- **FR-065**: O relatório MUST listar os TCCs na modalidade Artigo Científico das turmas do período,
  com os filtros Período letivo e Curso e as colunas Título do TCC, Aluno, Orientador, Veículo, Estrato
  Qualis/CAPES, Status de Submissão, Aproveitamento (Em Análise, Homologado ou Recusado) e Link ou DOI.
  Orientador é o do vínculo ativo; sem ele, o do vínculo mais recente; sem nenhum, "Sem orientador".
  Sem análise, Aproveitamento mostra a MR-14. [US-33 D][RBN-REL-02.2][RBN-CAD-10.5][RBN-CAD-12.1]
  [RBN-CAD-12.3]
- **FR-066**: O link MUST abrir o artigo fora do sistema, somente para endereços `https`; outro
  conteúdo aparece como texto. [US-33 D][RBN-CAD-12.1]

**Padrão visual** (requisito de apresentação; não muda nenhuma regra das US)

- **FR-070**: Os relatórios MUST usar um layout único: à esquerda, a lista de relatórios com a descrição
  de cada um; à direita, título e [PDF][CSV][XLSX]; uma frase sobre o relatório; filtros e "Limpar
  filtros"; a linha "Mostrando"; até 4 KPIs; um gráfico; a tabela com as colunas exatas da US e a linha
  Total; o bloco recolhível "Como é calculado"; e "Gerado em DD/MM/AAAA às HH:MM". A feat-11 usa o
  mesmo layout. [Padrão visual; heurística 4]
- **FR-071**: Em 360 px, a lista MUST virar um seletor no topo, os KPIs ficam em 2 colunas e a tabela
  rola na horizontal dentro do próprio bloco, sem rolagem horizontal da página.
- **FR-072**: Cada relatório MUST seguir a tabela de KPIs e gráfico:

  | Relatório | KPIs (no máximo 4) | Gráfico |
  |---|---|---|
  | Atividades por docente (Docente) | Orientandos TCC 1, Orientandos TCC 2, Coorientações, Bancas | sem gráfico |
  | Atividades por docente (Gestão) | Docentes, Orientações, Coorientações, Bancas | barras horizontais: total de bancas por docente |
  | Membros Externos | Docentes do NUCOMP, Membros Externos | barras horizontais: externos por instituição |
  | Formação e evasão | Matriculados, Ativos, Com Sucesso, Sem Sucesso (sem Sem Proposta: o bloco "Como é calculado" explica por que os cartões não somam Matriculados) | barra 100% empilhada por curso |
  | Histórico do NUCOMP | do último período: Vinculados, Defesas, Artigos, Desistências | linhas por período letivo |
  | Produção de TCCs | Total, Ativos, Com Sucesso, Sem Sucesso | barras horizontais pelo agrupamento |
  | Artigos | Artigos, Publicados, Homologados | sem gráfico |

  Na visão de gestão, Docentes é o número de linhas da tabela e Orientações soma as colunas de
  Orientandos em TCC 1 e TCC 2. O gráfico mostra só os docentes com banca e não aparece se nenhum tiver.

- **FR-073**: As cores MUST ter significado único: Ativos em `--azul`; Com Sucesso em `--verde`; Sem
  Sucesso em `--vermelho`; Sem Proposta e Não informada em `--texto3`; Membros Externos em `--roxo`. A
  cor nunca é a única pista: toda barra tem rótulo e número escritos, e a legenda fica sempre visível.
- **FR-074**: Os gráficos MUST ser desenhados sem biblioteca nova (barras em HTML/CSS e linhas em SVG),
  funcionar com o JavaScript desligado e ter barras ordenadas da maior para a menor. Sem pizza e sem 3D.
- **FR-075**: A tabela é a fonte de verdade: todo número do gráfico e dos KPIs MUST sair da mesma
  estrutura da tabela, e o gráfico MUST ter um resumo em texto para leitores de tela.
- **FR-076**: Heurísticas de Nielsen, aplicadas em todos os relatórios:
  1. **Visibilidade do status**: a linha "Mostrando" muda com os filtros; a data e a hora de geração
     aparecem no rodapé e no arquivo; o botão desabilitado explica o motivo no `title` (MR-02).
  2. **Mundo real**: termos das US e do NUCOMP e datas em DD/MM/AAAA, sem nome de campo do banco.
  3. **Controle e liberdade**: "Limpar filtros" volta ao padrão; os filtros ficam no endereço (GET), e
     o Voltar do navegador funciona; as linhas abrem e fecham.
  4. **Consistência**: mesmo layout, mesmas classes de estilo e exportação no mesmo lugar; tabela e
     arquivo com as mesmas colunas.
  5. **Prevenção de erros**: filtros só com listas e calendário e validação no servidor. Sem `min` e
     `max` nas datas, que trocariam a mensagem da US pelo aviso do navegador.
  6. **Reconhecimento**: descrição na lista, valores escritos, legenda visível e cabeçalho da tabela
     fixo ao rolar.
  7. **Eficiência**: atalhos de período, endereço direto para cada relatório e expansão por teclado.
  8. **Minimalismo**: no máximo 4 KPIs e um gráfico por relatório, sem grade pesada.
  9. **Recuperação de erros**: mensagens exatas das US junto ao campo e sugestão no estado vazio (MR-01).
  10. **Ajuda**: bloco "Como é calculado" (MR-03) e `title` nos cabeçalhos com a definição da coluna
      (MR-04).

### Key Entities

Nenhuma entidade nova. Os relatórios são consultas sobre o modelo existente.

- **Relatório registrado**: declaração em código (id, nome, descrição curta, perfis); não é tabela.
- **Filtros aplicados**: período, curso, docente, agrupamento e abrangência da consulta, no endereço.
- **Vínculo de orientação**: `Orientacoes` e `Coorientacoes`, com status e datas de início e fim.
- **Status por período**: último registro de `Historico_Status_TCC` do TCC que está na turma do período.
- **Membro efetivo**: integrante de `Banca_Defesa` que de fato atuou na sessão Realizada.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Cada consulta e cada troca de filtro exibe o resultado em menos de 2 segundos, com o
  volume de dados do `popular_demo`. [RAN-REL-01][RAN-CAD-14]
- **SC-002**: Em 100% das linhas e dos Totais, Matriculados = Sem Proposta + Ativos + Com Sucesso + Sem
  Sucesso e Total de Trabalhos = Ativos + Com Sucesso + Sem Sucesso.
- **SC-003**: 100% dos totais conferem com o histórico do Status do TCC, inclusive em período passado
  e com aluno transferido; o último registro de cada TCC é igual ao Status atual dele. [RAN-REL-02]
- **SC-004**: Nenhum perfil consegue ver, por tela, endereço direto ou exportação, um relatório ou um
  extrato fora da sua permissão.
- **SC-005**: Os 3 arquivos de cada relatório têm as mesmas colunas, a mesma ordem e os mesmos valores
  da tela, com a exceção de FR-019, e o CSV abre com acentos e colunas corretos.
- **SC-006**: A tela Defesas, a agenda e a lista de ouvintes continuam passando em todos os testes.
- **SC-007**: A feat-11 inclui um relatório só com o registro, a consulta e a declaração dos filtros,
  sem alterar a base.
- **SC-008**: Os 6 relatórios passam no checklist das 10 heurísticas em 360, 768 e 1280 px, e uma pessoa
  de fora da equipe diz o que cada dashboard mostra depois de vê-lo por 5 segundos.
- **SC-009**: Nenhuma migração nova: `makemigrations --check` não acusa mudanças.

## Assumptions

- **P2 (confirmada)**: um docente específico prevalece sobre o filtro Curso, porque a lista traz "cada
  docente do NUCOMP" e o cenário 5 da US-31 exige a linha dele (índice Q-150).
- **P3 (confirmada)**: a US-33 diz que o arquivo sai "por curso da turma"; a spec segue o agrupamento
  da tela, pelo Padrão visual (tabela = arquivo), porque nenhuma regra da matriz exige o contrário
  (índice Q-150).
- **P4 (confirmada)**: a Secretaria usa o filtro Curso com Todos, como dizem a US-31 C e a RBN-CAD-14.1. O guia
  da feat-10 cita "Secretaria limitada ao Curso Vinculado"; vale a matriz (índice Q-150).
- **Q-02**: a spec segue a US-32; a questão continua aberta só para o aluno sem Proposta. Se a PO
  responder de outro modo, a mudança começa por FR-043.
- Com Curso Todos ou agrupamento por Área ou Modalidade, os valores sem trabalho aparecem com zero;
  a E3 vale quando não há nenhum registro no resultado.
- Com um TCC por vínculo, Total de Trabalhos (abrangência Todos) = Matriculados − Sem Proposta; a
  igualdade serve de teste cruzado entre os relatórios.
- A meta de 2 segundos vem de RAN-REL-01 e RAN-CAD-14; a spec a estende aos 6 relatórios por
  consistência.
- O período letivo atual segue `periodo_letivo_atual` (turmas ativas; sem elas, o calendário).
- O Coordenador de Curso é um Docente: enquanto Coordenador, usa a visão de gestão também no painel.
- O detalhe do CSV (UTF-8 com BOM e separador `;`) fica no plan e em `contracts/base-relatorios.md`;
  a organização das sub-listas nos arquivos está em C4.
- Sem ordem definida na US, a tabela do Painel vem por nome do docente, e as instituições de Membros
  Externos, da maior quantidade para a menor e, no empate, por nome.
- A US-31 usa os dois nomes, "tela de atividades" e "Painel de atividades por docente"; a lista usa o
  nome do protótipo, "Painel de atividades por docente".

## Rastreabilidade

| US | RBN | Requisitos |
|---|---|---|
| US-31 | RBN-REL-01.1, RBN-DEF-01.5, RBN-CAD-14.1, RBN-CAD-10.4 | FR-001 a FR-020, FR-021 a FR-027 |
| US-47 | RBN-REL-01.2, RBN-DEF-01.5, RBN-CAD-14.1 | FR-001 a FR-020, FR-030 e FR-031 |
| US-32 | RBN-REL-02.3, RBN-CAD-05.4, RBN-CAD-08.3, RBN-CAD-08.7 | FR-001 a FR-020, FR-040 a FR-043 |
| US-32 fluxo A | RBN-REL-02.4, RBN-CAD-08.7, RBN-CAD-12.1 | FR-001 a FR-020, FR-050 a FR-052 |
| US-33 | RBN-REL-02.1, RBN-CAD-08.3, RBN-CAD-08.7 | FR-001 a FR-020, FR-040, FR-041, FR-060 a FR-064 |
| US-33 fluxo D | RBN-REL-02.2, RBN-CAD-12.1, RBN-CAD-12.3 | FR-001 a FR-020, FR-065 e FR-066 |
| Padrão visual | sem RBN (requisito de apresentação) | FR-070 a FR-076 |

## Fora do escopo

- Relatórios operacionais da feat-11 (RAN-REL-03: US-48 em diante).
- Painel de análise e homologação de artigos (RBN-CAD-12.2 e 12.3): a coluna Aproveitamento só lê.
- Corrigir ou unificar cadastros, como nomes de instituição.
- Gráfico no PDF, CSV ou XLSX.

## Mensagens a validar com a PO

Textos sem texto exato nas US — **PROVISÓRIOS** (índice Q-146). Os textos entre aspas nos FR são
cópia exata das US-31, 47, 32 e 33.

| ID | Uso | Texto proposto (PROVISÓRIO) | Origem | Situação |
|---|---|---|---|---|
| MR-01 | Sugestão no estado vazio, depois da mensagem da US | "Tente outro período ou o curso Todos" | Padrão visual, heurística 9 | Provisória |
| MR-02 | `title` dos botões desabilitados | "Sem registros para exportar" | Padrão visual, heurística 1 | Provisória |
| MR-03 | Bloco "Como é calculado", um texto por relatório | Fórmulas e definições das US, por exemplo "Matriculados = Sem Proposta + Ativos + Com Sucesso + Sem Sucesso" e "Aprovado sem Versão Final homologada conta como Ativo" | Padrão visual, heurística 10 | Provisória |
| MR-04 | `title` dos cabeçalhos de coluna | Definição da coluna, tirada da US | Padrão visual, heurística 10 | Provisória |
| MR-05 | Área de relatório antes de selecionar um item | "Selecione um relatório na lista" | sem texto na US | Provisória |
| MR-06 | Acesso negado por endereço direto | "Você não tem permissão para visualizar este relatório" | sem texto na US | Provisória |
| MR-07 | Falha ao gerar o arquivo | "Não foi possível gerar o arquivo. Tente novamente" | sem texto na US | Provisória |
| MR-08 | Descrição: Painel de atividades por docente | "Orientações, coorientações e bancas de cada docente no período" | Padrão visual, heurística 6 | Provisória |
| MR-09 | Descrição: Participação de Membros Externos | "Docentes e Membros Externos nas bancas realizadas, com as instituições de origem" | Padrão visual, heurística 6 | Provisória |
| MR-10 | Descrição: Formação e evasão | "Situação dos alunos do período letivo, por curso" | Padrão visual, heurística 6 | Provisória |
| MR-11 | Descrição: Histórico de indicadores do NUCOMP | "Vinculados, defesas, artigos e desistências em cada período letivo" | Padrão visual, heurística 6 | Provisória |
| MR-12 | Descrição: Produção de TCCs | "Trabalhos do período por curso, área de interesse ou modalidade" | Padrão visual, heurística 6 | Provisória |
| MR-13 | Descrição: Artigos | "TCCs na modalidade Artigo Científico, com publicação e aproveitamento" | Padrão visual, heurística 6 | Provisória |
| MR-14 | Aproveitamento sem análise | "Aguardando aceite ou publicação" | MO-22 da spec 006, a validar na Q-95 | Provisória |
