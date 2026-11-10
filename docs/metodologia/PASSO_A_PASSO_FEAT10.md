# Passo a passo — feat-10 Dashboards de Produção no VS Code com o Claude Code

**Responsável:** Julia Cohen · **Revisor do PR:** Célio Benjamim
**Spec:** 010 · **Branch:** `feature/feat-10-dashboards` · **App:** `sigtcc/apps/relatorios` (hoje só tem `apps.py`)
**Histórias:** US-31 (atividades por docente), US-47 (Membros Externos), US-32 (formação e evasão + histórico do NUCOMP) e US-33 (produção de TCCs + artigos)
**Cronograma:** atividade 5.2 (19/11 a 26/11), junto com a feat-11 do Célio
**Meta:** PR aberto até 25/11 e merge na `develop` até 26/11

Segue o ciclo do `metodologia/CICLO_SPEC_PROMPTS.md`, com os campos preenchidos para a feat-10. Os blocos com `/speckit-...` ou `@agent-...` vão no chat do Claude Code. Os blocos com `git` ou `python` vão no terminal do VS Code.

---

## Antes de começar: o que a feat-10 entrega

São **6 relatórios** em 4 US, todos somente leitura, com filtros e exportação em PDF, CSV e XLSX:

| Relatório (item da lista) | US | RBN | Quem vê |
|---|---|---|---|
| Painel de atividades por docente | US-31 | REL-01.1 | Docente (só o próprio), Coordenador, Secretaria |
| Participação de Membros Externos | US-47 | REL-01.2 | Coordenador, Secretaria |
| Formação e evasão | US-32 | REL-02.3 | Coordenador |
| Histórico de indicadores do NUCOMP | US-32 (alt. A) | REL-02.4 | Coordenador |
| Produção de TCCs | US-33 | REL-02.1 | Coordenador |
| Artigos | US-33 (alt. D) | REL-02.2 | Coordenador |

**A feat-10 é dona da base do módulo Relatórios**, que a feat-11 (Apoio Operacional, do Célio) também vai usar:
- tela "Relatórios" com a lista de relatórios por perfil (item do menu lateral, área Gestão);
- registro dos relatórios (id, nome, descrição curta, perfis);
- componente de filtros (período com atalhos, Ano/Semestre, Curso, Docente);
- exportação genérica em PDF, CSV e XLSX a partir da mesma estrutura de dados da tela;
- o layout do dashboard (seção "Padrão visual" abaixo).

---

## Padrão visual: dashboards pelas 10 heurísticas de Nielsen

Esta seção vira requisito da spec (Etapa 1). As US definem **o que** cada relatório mostra (colunas, filtros, mensagens). O padrão abaixo define **como** mostrar, sem mudar nenhuma regra.

### Layout único para os 6 relatórios

```
┌──────────────────────────────────────────────────────────────────┐
│ Relatórios                                                       │
├───────────────┬──────────────────────────────────────────────────┤
│ Lista de      │ Título do relatório            [PDF][CSV][XLSX]  │
│ relatórios    │ Uma frase: o que o relatório mostra              │
│ (com 1 linha  │──────────────────────────────────────────────────│
│ de descrição) │ Filtros: Período · Ano/Semestre · Curso  [Limpar]│
│               │ Mostrando: 2026/2 · Eng. de Computação           │
│               │──────────────────────────────────────────────────│
│               │ [KPI] [KPI] [KPI] [KPI]   (no máximo 4)          │
│               │──────────────────────────────────────────────────│
│               │ Gráfico (um só, com valores escritos)            │
│               │──────────────────────────────────────────────────│
│               │ Tabela (colunas exatas da US, linha Total)       │
│               │ ▸ Como é calculado                               │
│               │ Gerado em 05/11/2026 às 23:15                    │
└───────────────┴──────────────────────────────────────────────────┘
```

No celular (360 px), a lista de relatórios vira um seletor no topo, os KPIs ficam em 2 colunas e a tabela rola na horizontal dentro do próprio bloco.

### As 10 heurísticas aplicadas

| # | Heurística | Como aplicar no SIGTCC |
|---|---|---|
| 1 | **Visibilidade do status do sistema** | Linha "Mostrando: 2026/2 · Engenharia de Computação" sempre visível abaixo dos filtros. Data e hora de geração no rodapé e no arquivo exportado. Botões de exportação desabilitados com o motivo no `title` ("Sem registros para exportar"). |
| 2 | **Correspondência com o mundo real** | Termos das US e do NUCOMP: "Orientandos em TCC 1", "Com Sucesso", "Período letivo 2026/2". Datas em DD/MM/AAAA. Nada de nomes de campo do banco. |
| 3 | **Controle e liberdade do usuário** | Botão "Limpar filtros" volta ao padrão (período letivo atual). Filtros no endereço da página (GET), então o botão Voltar do navegador funciona e o link pode ser enviado a outra pessoa. Linhas expansíveis abrem e fecham. |
| 4 | **Consistência e padrões** | Mesmo layout nos 6 relatórios (e nos da feat-11). Exportação sempre no canto superior direito. Mesmas classes do `sigtcc.css` (`.kpi`, `.tb`, `.rel-layout`, `.inp`). A tabela da tela e o arquivo exportado têm as mesmas colunas, na mesma ordem. |
| 5 | **Prevenção de erros** | Filtros só com listas e calendário (sem texto livre). `min`/`max` nos campos de data para impedir Data Inicial depois da Final. Validação repetida no servidor (E2 da US-31 e US-47). |
| 6 | **Reconhecimento em vez de memorização** | Cada item da lista de relatórios tem uma linha de descrição. Gráficos com o valor escrito ao lado de cada barra e legenda sempre visível (nunca só em `hover`). Cabeçalho da tabela fixo ao rolar. |
| 7 | **Flexibilidade e eficiência** | Atalhos de período (Período Letivo, Esta Semana, Este Mês, Próximos 30 Dias). Endereço direto para cada relatório. Expandir a linha também pelo teclado (Enter/Espaço). |
| 8 | **Estética e design minimalista** | No máximo 4 KPIs e **um** gráfico por relatório. Sem pizza, sem 3D, sem grade pesada. Cores só com significado (tabela de cores abaixo). Barras ordenadas da maior para a menor. |
| 9 | **Ajudar a reconhecer e corrigir erros** | Mensagens exatas das US, junto ao campo com problema. Estado vazio com a mensagem da US e uma sugestão: "Tente outro período ou o curso Todos". |
| 10 | **Ajuda e documentação** | Bloco recolhível "Como é calculado" em cada relatório (ex.: "Matriculados = Sem Proposta + Ativos + Com Sucesso + Sem Sucesso"; "Aprovado sem Versão Final homologada conta como Ativo"). `title` nos cabeçalhos de coluna com a definição. |

### Cores com significado (tokens que já existem no `sigtcc.css`)

| Categoria | Token | Uso |
|---|---|---|
| Ativos / Em andamento | `--azul` | barra principal |
| Com Sucesso / Concluído | `--verde` | |
| Sem Sucesso / Desistência | `--vermelho` | |
| Sem Proposta / Não informada | `--texto3` (cinza) | |
| Membros Externos | `--roxo` | US-47 |

A cor nunca é a única pista (daltonismo): cada barra tem o rótulo e o número escritos.

### Gráfico de cada relatório

| Relatório | KPIs | Gráfico | Por quê |
|---|---|---|---|
| Atividades por docente (Docente) | Orientandos TCC 1, Orientandos TCC 2, Coorientações, Bancas | sem gráfico (uma linha só) | os 4 números já dizem tudo |
| Atividades por docente (Gestão) | Docentes, Orientações, Coorientações, Bancas | barras horizontais: total de bancas por docente | compara docentes |
| Membros Externos | Docentes do NUCOMP, Membros Externos | barras horizontais: externos por instituição | mostra de onde vêm |
| Formação e evasão | Matriculados, Ativos, Com Sucesso, Sem Sucesso | barra 100% empilhada por curso (Sem Proposta · Ativos · Com Sucesso · Sem Sucesso) | parte de um todo; a soma fecha em 100% |
| Histórico do NUCOMP | último período: Vinculados, Defesas, Artigos, Desistências | linhas por período letivo (SVG simples) | evolução no tempo |
| Produção de TCCs | Total, Ativos, Com Sucesso, Sem Sucesso | barras horizontais pelo agrupamento escolhido | compara cursos, áreas ou modalidades |
| Artigos | Artigos, Publicados, Homologados | sem gráfico (é uma lista) | a tabela é o conteúdo |

### Decisão técnica dos gráficos

- **Sem biblioteca JavaScript nova.** Barras feitas em HTML/CSS (largura em %) e o gráfico de linhas em SVG gerado no template. Motivo: o `requirements.txt` é item de configuração do Célio, não precisa de CDN, funciona com o JavaScript desligado e não pesa no Render/Vercel.
- **A tabela é a fonte de verdade.** O gráfico tem `role="img"` e um `aria-label` com o resumo ("Engenharia de Computação: 75% ativos, 8% com sucesso..."). Leitores de tela usam a tabela.
- **PDF:** o xhtml2pdf (já usado na feat-09) não lida bem com CSS moderno. O PDF leva cabeçalho, filtros, KPIs em tabela simples e a tabela da US. O gráfico fica só na tela.

---

## Etapa 0 — Preparar o ambiente (até 18/11, depois do PR da feat-07)

1. **Combine com o Célio** antes de especificar:
   - Divisão: feat-10 com você e feat-11 com ele (as US-31, 32, 33 e 47 ainda citam a Maria Luiza Nobre como responsável; o cronograma 18/10 pôs a 5.2 com vocês dois).
   - A base do módulo Relatórios (lista, filtros, exportação, layout) fica na feat-10, e ele consome na feat-11.
   - Mande para ele a seção "Padrão visual" deste guia.
2. Abra a pasta `SIGTCC` no VS Code e ative o ambiente virtual:
   - macOS: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`
3. Atualize a `develop` e o banco local:

```
git status
git checkout develop
git pull
pip install -r requirements.txt -r requirements-dev.txt
python manage.py migrate
python manage.py test
```

4. Confira em `docs/questoes-a-rever.md` a **Q-02** (aluno que desiste antes da Proposta entra como Desistente na evasão?). Ela muda a conta da US-32. Se ainda estiver Aberta, a spec segue a US como está e cita a Q-02.
5. Crie a branch:

```
git checkout -b feature/feat-10-dashboards
```

---

## Etapa 1 — Especificar

```
/speckit-specify Use o número 010 para esta spec. Dashboards de Produção do
SIGTCC (Épico 3): US-31, US-47, US-32 (com o Histórico de indicadores do
NUCOMP, fluxo alternativo A) e US-33 (com o relatório de Artigos, fluxo
alternativo D). Use as seções dessas US em
docs/fonte/Historias_de_Usuario_v3_4.md, com regras (RBN-REL-01.1, 01.2,
02.1, 02.2, 02.3, 02.4), fluxos alternativos, mensagens exatas e cenários de
aceite; IDs da matriz de 17/10. Todos os relatórios são somente leitura: não
crie tabelas nem colunas, e me pergunte se algum número não puder ser
calculado com o Modelo Lógico 18/10.
Esta feature é dona da base do módulo Relatórios, que a feat-11 (Célio) vai
consumir: tela "Relatórios" no menu lateral (área Gestão) com a lista de
relatórios por perfil, registro dos relatórios (id, nome, descrição curta,
perfis), componente de filtros (Período com atalhos, Ano/Semestre, Curso,
Docente) reaproveitando o FiltroPeriodoForm e o filtro_de_periodo da feat-07
sem quebrar a tela Defesas, e exportação genérica em PDF (xhtml2pdf, como na
feat-09), CSV e XLSX (openpyxl) a partir da mesma estrutura da tela.
Inclua como requisito de apresentação a seção "Padrão visual" de
metodologia/PASSO_A_PASSO_FEAT10.md (layout único, as 10 heurísticas de
Nielsen, cores com significado, KPIs e gráfico de cada relatório, gráficos em
HTML/CSS e SVG sem biblioteca nova, tabela como fonte de verdade, PDF sem
gráfico). Esse padrão não muda nenhuma regra das US. Textos de ajuda e de
estado vazio que não estão nas US entram como provisórios na seção
"Mensagens a validar com a PO". A Q-02 do docs/questoes-a-rever.md afeta a
US-32: siga a US e cite a questão. Não crie nem troque de branch: use a
feature/feat-10-dashboards. Não faça commit.
```

> Antes de rodar, copie este guia para `docs/metodologia/PASSO_A_PASSO_FEAT10.md` no repositório (ou cole a seção "Padrão visual" no prompt).

---

## Etapa 2 — Conferir a spec

```
@agent-analista-requisitos confira a spec 010 contra as US-31, US-47, US-32 e
US-33 e a matriz de 17/10. Confira em especial: as fórmulas (Matriculados =
Sem Proposta + Ativos + Com Sucesso + Sem Sucesso; Total de Trabalhos = Ativos
+ Com Sucesso + Sem Sucesso), quais Status do TCC caem em cada coluna, o
período anterior contado pelo histórico (US-32 cenário 4) e a visibilidade
de cada relatório por perfil. Liste os pontos a decidir.
```

Para responder, use a regra do ciclo:
- **Configuração técnica** (formato, onde guardar, como calcular): pode aceitar a recomendação.
- **Regra ou mensagem que as US não têm:** vira sugestão para a PO no índice, fora da spec.
- **Contrato com o Célio ou conflito com outra feature:** pare e fale com ele antes.

```
Aplique as correções simples. Decisões: 1: _, 2: _, ... Registre tudo em
Clarifications. Mensagens novas entram como provisórias na seção "Mensagens a
validar com a PO" (prefixo MR-). Pendências de outras pessoas vão para
docs/questoes-a-rever.md com o próximo ID.
```

## Etapa 3 — Esclarecer

```
/speckit-clarify
```

Terminal:

```
git add specs/010-*/ docs/questoes-a-rever.md
git commit -m "docs(feat-10): especificar dashboards de producao"
git push -u origin feature/feat-10-dashboards
```

**Mande ao Célio a seção de contratos da spec 010** (registro de relatórios, filtros, exportação, template base), para ele usar na spec 011.

---

## Etapa 4 — Planejar

```
Aprovo a spec 010 (Julia Cohen, {data}). Registre a aprovação e rode
/speckit-plan com Django 5.2 + PostgreSQL 16, app sigtcc/apps/relatorios,
templates em sigtcc/templates/relatorios/ e estilos no
sigtcc/static/css/sigtcc.css, seguindo a tela Relatórios do protótipo de
17/10 e a constituição. Estrutura sugerida:
- services_relatorios.py: uma função pura por relatório, que recebe o
  usuário e os filtros e devolve a mesma estrutura (título, filtros
  aplicados, colunas, linhas, sub-listas, total, KPIs, dados do gráfico);
  contagens com annotate/aggregate no banco, sem consulta por linha;
- registro.py: registro dos relatórios e permissões por perfil;
- exportacao.py: PDF, CSV (UTF-8 com BOM, separador ;) e XLSX genéricos
  a partir dessa estrutura;
- forms.py: filtros, reaproveitando o FiltroPeriodoForm da feat-07;
- um template base com o layout do Padrão visual e um parcial por gráfico
  (barras, barra 100% empilhada, linhas em SVG).
Os contratos para a feat-11 ficam em contracts/base-relatorios.md. Organize
as tarefas para que a fase base (registro, filtros, exportação, template
base e um relatório completo, o de atividades por docente) fique pronta
primeiro, porque o Célio depende dela. Não faça commit.
```

## Etapa 5 — Revisar o plano

```
@agent-arquiteto-django revise o plan da spec 010, com atenção a segurança
(Docente só vê a própria linha, mesmo trocando o filtro pelo endereço;
relatórios do Coordenador bloqueados por endereço direto; Secretaria
limitada ao Curso Vinculado), desempenho das contagens (sem N+1), igualdade
entre a tela e os arquivos exportados e reaproveitamento pela feat-11
```

Depois:

```
Aplique as correções técnicas. Decisões: Q-__: _, Q-__: _. Itens de
configuração vão para o Célio no índice. Rode o arquiteto de novo só para
confirmar que os bloqueantes e importantes fecharam. Não faça commit.
```

## Etapa 6 — Tarefas e análise

```
Aprovo o plan da spec 010 (Julia Cohen, {data}). Registre a aprovação e
rode /speckit-tasks e em seguida /speckit-analyze. Não faça commit.
```

Se o analyze achar problemas:

```
Aplique as correções de [IDs]. Depois registre minha aprovação do tasks.md
(Julia Cohen, {data}). Não faça commit.
```

Meta: 0 CRITICAL e 0 HIGH. Terminal:

```
git add specs/010-*/ docs/questoes-a-rever.md
git commit -m "docs(feat-10): planejar dashboards de producao"
git push
```

---

## Etapa 7 — Implementar (19/11 a 24/11)

### 7.1 Fase base primeiro (até 20/11)

```
/speckit-implement Implemente só a fase base do tasks.md da spec 010:
item Relatórios no menu lateral, tela Relatórios com a lista por perfil,
registro dos relatórios, filtros, exportação PDF/CSV/XLSX, template base
com o layout do Padrão visual e o relatório de atividades por docente
(US-31) completo, incluindo dados de demonstração no popular_demo. Faça um
commit atômico ao concluir cada grupo de tarefas relacionadas, só depois de
os testes da etapa passarem. Use Conventional Commits com escopo feat-10,
imperativo, até 72 caracteres. Não faça push. Antes de cada commit, mostre o
git status. Pare e me pergunte se algo divergir da spec, das US ou do Modelo
Lógico 18/10.
```

Terminal:

```
python manage.py test
git push
```

**Avise o Célio:** a base está na `feature/feat-10-dashboards`. Ele pode criar a `feature/feat-11-apoio-operacional` a partir dela.

### 7.2 Restante, na ordem

Ordem: US-31 (já pronta) → US-33 → US-32 → US-47.
A US-33 vem antes da US-32 porque as duas usam a mesma classificação de Status em Ativos, Com Sucesso e Sem Sucesso; a US-47 é Could Have e fica por último.

```
/speckit-implement Continue a partir da próxima tarefa pendente, na ordem
US-33, US-32 e US-47. Mesmas regras de commit: atômico por grupo de
tarefas, testes passando, Conventional Commits feat-10, sem push, git
status antes de cada commit. Pare e me pergunte se algo divergir da spec.
```

Se parar no meio:

```
Continue o /speckit-implement a partir da próxima tarefa pendente.
```

Faça `git push` no fim de cada história.

**Pontos para conferir em cada história:**
- **US-31:**
  - Docente vê só a própria linha, sem os filtros Docente e Curso, mesmo alterando o endereço.
  - Coordenador e Secretaria veem "Todos" por padrão e podem escolher um docente.
  - Sub-listas com "Nenhum registro" quando vazias; Total de Bancas 0.
  - Só bancas Realizadas no período.
- **US-33:**
  - Agrupar por Curso, Área de Interesse (10 áreas + "Não informada") e Modalidade.
  - Abrangência Todos, Todos os Aprovados e Apenas Concluídos.
  - Total de Trabalhos = Ativos + Com Sucesso + Sem Sucesso em toda linha (teste automático).
  - Relatório de Artigos com Veículo, Qualis, Status de Submissão, Aproveitamento e Link/DOI.
- **US-32:**
  - Matriculados = soma das quatro colunas em toda linha e no Total (teste automático).
  - Aprovado sem Versão Final homologada conta como Ativo.
  - Período anterior contado pelo histórico (cenário 4).
  - Histórico do NUCOMP sem filtro de período, do mais antigo ao mais recente.
- **US-47:**
  - Pessoas distintas (quem participou de 3 bancas conta 1).
  - Só membros efetivos de sessões Realizadas (com o suplente acionado, via `membros_efetivos` da feat-07).
  - Secretaria com o filtro Curso preenchido com o Curso Vinculado.
- **Em todos:**
  - E2: "A data inicial não pode ser superior à data final".
  - E3: "Nenhum registro encontrado para os filtros selecionados", com PDF, CSV e XLSX desabilitados.
  - Arquivo exportado com as mesmas colunas da tela e os filtros aplicados.
  - CSV abre certo no Excel (acentos e separador).
  - Aluno não vê o item Relatórios.

---

## Etapa 8 — Teste manual e revisão de usabilidade (24/11)

1. Rode `python manage.py popular_demo --local --senha "Senha123teste"` (acrescente `--confirmar` se o comando pedir; ele apaga os dados do banco local) e depois `python manage.py runserver`.
2. Siga o `quickstart.md` da spec 010, com um cenário por critério de aceite.
3. Teste nos quatro perfis: Docente, Coordenador de Curso, Secretaria e Aluno (não pode ver Relatórios).
4. Abra os três arquivos exportados de cada relatório e compare com a tela.
5. Revise o visual em 360, 768 e 1280 px (Cmd+Option+I → Cmd+Shift+M) e confira que o console não tem erros.
6. **Checklist de Nielsen** (marque cada item em cada relatório):

| # | Conferir | OK |
|---|---|---|
| 1 | A linha "Mostrando:" muda junto com os filtros; data de geração aparece | ☐ |
| 2 | Nenhum termo técnico ou nome de campo do banco na tela | ☐ |
| 3 | "Limpar filtros" volta ao padrão; Voltar do navegador refaz o filtro anterior | ☐ |
| 4 | Layout, posição dos botões e nomes iguais nos 6 relatórios | ☐ |
| 5 | Não é possível escolher Data Inicial depois da Final | ☐ |
| 6 | Todo gráfico tem valores escritos e legenda visível | ☐ |
| 7 | Atalhos de período funcionam; linha expande pelo teclado | ☐ |
| 8 | No máximo 4 KPIs e 1 gráfico; cores só com significado | ☐ |
| 9 | Mensagens de erro e de estado vazio são as das US, perto do campo | ☐ |
| 10 | "Como é calculado" explica as fórmulas do relatório | ☐ |

7. **Teste de 5 segundos:** mostre cada dashboard a alguém de fora da equipe por 5 segundos e pergunte "o que esse relatório diz?". Se a pessoa não souber, simplifique o gráfico ou os KPIs.

```
T___ feito: roteiro manual OK [ou: passo X falhou: ...], exportações
conferidas com a tela, checklist de Nielsen OK [ou: itens X e Y ajustados],
revisão visual em 360/768/1280 sem problemas, console sem erros. Marque a
tarefa e registre no quickstart e no pr.
```

---

## Etapa 9 — Preparar o PR (25/11)

Se a `develop` mudou:

```
git checkout develop && git pull
git checkout feature/feat-10-dashboards
git rebase develop
python manage.py test
git push --force-with-lease
```

Verificação completa:

```
pre-commit run --all-files
python manage.py makemigrations --check
```

No Claude Code:

```
@agent-revisor-pgcs confira a branch e prepare o PR
```

```
Atualize o pr-feat-10.md: título "[Feat-10] Dashboards de Produção (US-31,
US-32, US-33, US-47)", cartão do Trello "5.2 Implementação dos relatórios",
revisor Célio Benjamim (consome a base do módulo Relatórios), evidência
manual [resultado do teste e do checklist de Nielsen]. Atualize também a
seção [Não lançado] do CHANGELOG.md e a "Situação no desenvolvimento" das
US-31, 32, 33 e 47 em docs/fonte. Faça um commit docs(feat-10). Não faça
push.
```

Terminal:

```
git status
git ls-files | grep -E "\.env$"     # não pode mostrar nada
git push
```

No GitHub:
- Base: `develop`. Compare: `feature/feat-10-dashboards`.
- Título: a 1ª linha do `pr-feat-10.md`, sem "# ".
- Descrição: o resto do arquivo.
- Reviewer: Célio.
- Confira a aba Commits.

---

## Etapa 10 — Depois do PR (26/11)

- Revise o PR do Célio, `[Feat-11]`:
  - Confira se ele usou a base (registro, filtros, exportação, template) sem duplicar código.
  - Confira se os relatórios dele seguem o mesmo Padrão visual.
- Merge na `develop` com "Create a merge commit" até 26/11. Depois, apague a branch.
- A partir de 27/11, a Leandra começa a implantação em produção (5.3), que depende da 5.2.
