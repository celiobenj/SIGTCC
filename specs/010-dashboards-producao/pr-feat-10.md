# [Feat-10] Dashboards de Produção (US-31, US-32, US-33, US-47)

**Origem:** `feature/feat-10-dashboards` -> **Destino:** `develop` (merge `--no-ff`, PGCS 6.4)

**Spec:** `specs/010-dashboards-producao/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`,
`contracts/`, `quickstart.md`, `tasks.md`)

**Responsável:** Julia Cohen (spec e implementação). As US-31, 32, 33 e 47 citam Maria Luiza Nobre
como responsável; a divisão vale pelo cronograma de 18/10, atividade 5.2.

### 1. Resumo da Alteração

Módulo Relatórios no app `relatorios` (Épico 3), só de leitura, sem tabela, coluna nem migração nova
(`makemigrations --check`: "No changes detected"):

- **Tela Relatórios** (item de menu na seção Gestão, para Docente e Secretaria): lista por perfil e
  layout único do Padrão visual (lista com descrição, exportação no canto superior direito, filtros,
  linha "Mostrando", até 4 KPIs, um gráfico, tabela, "Como é calculado" e data de geração).
- **Painel de atividades por docente** (US-31; REL-01.1): o Docente vê só a própria linha, mesmo
  trocando o endereço; Coordenador e Secretaria filtram por Docente e Curso. Sub-listas Orientações e
  coorientações e Bancas; vínculo em vigor no intervalo, com o Status final do TCC como fim (Q-147).
- **Participação de Membros Externos** (US-47; REL-01.2): pessoas distintas entre os membros efetivos
  das sessões Realizadas, com as instituições.
- **Formação e evasão** e **Histórico de indicadores do NUCOMP** (US-32; REL-02.3, 02.4): contagem
  pelo último registro do histórico do TCC na turma do período, inclusive para o aluno transferido;
  artigo copiado do TCC 1 conta uma vez (Q-149).
- **Produção de TCCs** e **Artigos** (US-33; REL-02.1, 02.2): agrupamento por Curso, Área de
  Interesse ou Modalidade, abrangência, Total de Trabalhos = Ativos + Com Sucesso + Sem Sucesso.
- **Exportação** em PDF (paisagem, sem gráfico), CSV (UTF-8 com BOM, `;`) e XLSX, da mesma estrutura
  da tela, com proteção contra fórmula e resposta sem cache.
- **Base para a feat-11** (`contracts/base-relatorios.md`): registro por decorador, formulário de
  filtros herdado do `FiltroPeriodoForm`, estrutura única e exportação genérica.
- **Correção transversal (`fix(core)`)**: tabelas de todo o sistema não partem mais palavras.

**Commits**

| Commit | Título | Arquivos |
|---|---|---|
| `7bfc7ca` | docs(feat-10): registrar revisao parcial do plano | 4 |
| `0c3ba22` | docs(feat-10): planejar dashboards de producao | 9 |
| `fac2620` | test(feat-10): provar consultas de status no postgresql | 5 |
| `e236480` | feat(feat-10): criar registro e estrutura dos relatorios | 7 |
| `b3b3f48` | feat(feat-10): criar filtros dos relatorios sobre os da feat-07 | 5 |
| `5acca97` | feat(feat-10): criar exportacao e dados dos graficos | 5 |
| `6e18f8d` | feat(feat-10): criar tela relatorios com layout, rotas e menu | 16 |
| `442a07f` | feat(feat-10): emitir painel de atividades por docente (US-31) | 6 |
| `562c894` | feat(feat-10): popular cenario do painel no popular_demo | 3 |
| `3290fae` | docs(feat-10): alinhar contrato da base ao implementado | 2 |
| `3960936` | feat(feat-10): emitir producao de tccs e artigos (US-33) | 6 |
| `d869f4a` | feat(feat-10): emitir formacao e evasao (US-32) | 5 |
| `6739412` | feat(feat-10): emitir historico de indicadores do nucomp (US-32) | 7 |
| `70a7e13` | feat(feat-10): emitir participacao de membros externos (US-47) | 7 |
| `7233c90` | test(feat-10): comparar tela e arquivos com dados hostis | 3 |
| `313bd55` | test(feat-10): completar permissoes, mensagens e apresentacao | 4 |
| `a2f4480` | docs(feat-10): registrar verificacao automatica e medicao | 2 |
| `748c52b` | fix(core): impedir quebra de palavras nas tabelas | 25 |
| `ba93049` | fix(core): manter palavras inteiras nas tabelas em telas pequenas | 8 |
| `a8b2e04` | docs(feat-10): fechar o texto do pr, o changelog e a matriz | 5 |
| `fb04452` | docs(feat-10): registrar validacao manual no pr e quickstart | 2 |
| (este) | docs(feat-10): conferir o texto do pr com o pgcs | 2 |

**Mudanças em código de outras specs** (aprovação do Célio Benjamim pendente na Q-153; todas só
acrescentam, salvo a IC-03, que extrai uma função sem mudar o resultado):

| IC | Arquivo (spec de origem) | Mudança |
|---|---|---|
| IC-01 | `sigtcc/urls.py` (003) | + `include("sigtcc.apps.relatorios.urls")` |
| IC-02 | `cadastro/views.py` (003) | + MR-06 em `MENSAGENS_403` |
| IC-03 | `defesa/services_defesa.py` (007) | `intervalo_do_atalho` extraída; `filtro_de_periodo(..., *, ano_semestre=None)` |
| IC-04 | `static/css/sigtcc.css` (003) | estilos do protótipo e do Padrão visual (KPIs, layout, barras, linhas, sub-lista, destaque, cabeçalho fixo, impressão) |
| IC-05 | `popular_demo.py` (005 a 009); `defesa/tests/test_base_defesa.py` (007) | troca de orientador, Suplente acionado, turma de 2025/2 com artigo copiado, Membro Externo da UEA e banca da sessão Realizada de TCC 2 com dois Membros Externos; testes desse cenário no `TestePopularDemo` |
| IC-07 | `relatorios/apps.py` (001); `defesa/tests/test_us40_lista_filtros_historico.py` (007) | `ready()` carrega as consultas; teste de `ano_semestre` |

A IC-06 (item do menu ativo em `/relatorios/<id>/`, T019) não foi feita: é opcional e depende da Q-153.

**Correção `fix(core)` em todo o sistema** (fora das tarefas da spec 010): `.tabela td` deixa de usar
`overflow-wrap: anywhere`; colunas curtas (`.nw`), endereços e palavras com hífen ficam numa linha;
colunas de texto (`.texto`) têm largura mínima; a tabela rola dentro da `.tabela-wrap`. Classes em 22
templates e o filtro `palavras_inteiras` nos relatórios. Dois testes das specs 008 e 009 passaram a
esperar `<td class="nw">`, sem mudar o que verificam.

### 2. Rastreabilidade com o Projeto

* **Feature Impactada:** Feature 10 – Dashboards de Produção
* **Histórias de Usuário Atendidas:** US-31, US-32, US-33, US-47 (RBN-REL-01.1, 01.2, 02.1, 02.2,
  02.3, 02.4; RBN-DEF-01.5 e RBN-CAD-14.1 nos filtros)
* **Cartão no Trello:** 5.2 Implementação dos relatórios

### 3. Checklist Técnico da Equipe (Definition of Done)

- [x] Lint aprovado: `pre-commit run --all-files` (isort, black `--line-length 100`, flake8
  `--max-line-length 100`) sem ocorrências.
- [x] Não há variáveis, imports ou trechos de código não utilizados (flake8 limpo).
- [x] `makemigrations --check --dry-run`: "No changes detected"; nenhuma migração existente alterada.
- [x] Os arquivos `.env` e os diretórios `sigtcc/media/` e `staticfiles/` NÃO foram adicionados ao Git.
- [x] A interface segue a paleta e os padrões do protótipo de 17/10 e o Padrão visual da spec:
  telas conferidas em 360, 768 e 1280 px, sem problema, e checklist de Nielsen OK (T052).
- [x] Não há quebras de layout nem erros acusados no console do navegador com o sistema rodando
  (T052, 07/11/2026); nenhuma palavra partida nas tabelas (verificação com o Playwright, seção 4).

**Testes automatizados:** suíte completa em 07/11/2026, no commit `ba93049`
(`manage.py test --noinput --parallel 4`): 1779 testes, todos passando, mais 1 falha esperada já
marcada como `expectedFailure` (anterior a esta spec). Repetida em 07/11/2026 no commit `fb04452`,
com o mesmo resultado; os commits depois de `ba93049` só mudam documentos. Testes novos em `sigtcc/apps/relatorios/tests/`:
um arquivo por US (`test_us31_atividades`, `test_us47_membros_externos`, `test_us32_formacao`,
`test_us32_historico`, `test_us33_producao`, `test_us33_artigos`), `test_filtros_relatorios`,
`test_exportacao`, `test_igualdade_tela_arquivo` (6 relatórios × 3 formatos com dados hostis),
`test_permissoes_relatorios` (6 relatórios × lista, tela e 3 formatos × 10 perfis, `POST` recusado,
nenhuma gravação), `test_mensagens_relatorios` e `test_base_relatorios`.

**SC-001** (meta de 2 s), medido com o `popular_demo`: tela em até 0,04 s e arquivo em até 0,22 s. O
volume de demonstração é pequeno e não prova a escala de produção (achado U1, aceito sem mudança).

### 4. Evidência da Validação Manual (Critérios de Aceite das USs)

Roteiro manual do `quickstart.md` executado por Julia Cohen em 07/11/2026, sobre o cenário do
`popular_demo`: **sem defeito**. Exportações em PDF, CSV e XLSX conferidas com a tela, checklist
das 10 heurísticas de Nielsen OK, revisão visual em 360, 768 e 1280 px sem problemas e console do
navegador sem erros. Registro na seção 5 do `quickstart.md` (T052).

Verificação automática das tabelas com o Playwright em 07/11/2026, em banco separado populado pelo
`popular_demo` e apagado depois: perfis Coordenador, Secretaria e Docente; 98 telas com tabela em 360,
768 e 1280 px, com sub-listas e `<details>` abertos; 390 medições, **zero palavras partidas** e
nenhuma página com rolagem horizontal.

Os cenários de aceite também estão cobertos por testes automatizados (um ou mais por cenário):

- [x] Cenário 1: Painel de atividades por docente, com recorte do Docente e visão de gestão (US-31)
- [x] Cenário 2: Participação de Membros Externos, com pessoas distintas e instituições (US-47)
- [x] Cenário 3: Formação e evasão, com a soma igual a Matriculados e o período anterior pelo histórico (US-32)
- [x] Cenário 4: Histórico de indicadores do NUCOMP, do mais antigo ao mais recente (US-32 fluxo A)
- [x] Cenário 5: Produção de TCCs por Curso, Área e Modalidade e relatório de Artigos (US-33)
- [x] Cenário 6: Exportação em PDF, CSV e XLSX igual à tela, e botões desabilitados sem registros (todas)

**Pendências registradas em `docs/questoes-a-rever.md` (não bloqueiam o merge):**
- Q-02 (PO): aluno que desiste sem Proposta; a spec segue a US-32 (FR-043).
- Q-146 (PO): textos provisórios MR-01 a MR-14.
- Q-151 (Célio): ciência dos contratos da base do módulo para a feat-11.
- Q-152 (PO): filtro Curso do Painel pelo Curso de Lotação, papel "Suplente" e docentes da visão de
  gestão; ciência de que a Secretaria com Curso Todos vê alunos de outros cursos.
- Q-153 (Célio): itens de configuração IC-01 a IC-05 e IC-07.

**Avisos ao revisor:**
- O roteiro manual da spec 009 muda: a sessão Realizada de TCC 2 do `popular_demo` agora tem como 1º
  Avaliador a Membro Externo Débora Nunes Aquino (UEA) e como 2º Marcos Vinícius Teixeira (UFAM);
  a sessão de TCC 1 de 2026/1 tem o Suplente Henrique Matos Couto acionado no lugar de Renata Silveira
  Cruz.
- O commit `7bfc7ca` registrou só o template do `plan.md`; o plano completo está em `0c3ba22`.

### 5. Revisão por Pares (Peer Review)

* **Revisor Designado:** Célio Benjamim (consome a base do módulo Relatórios na feat-11)
* **Parecer do Revisor:**

[ ] Aprovado integralmente para merge

[ ] Solicitação de ajustes (detalhar nos comentários)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
