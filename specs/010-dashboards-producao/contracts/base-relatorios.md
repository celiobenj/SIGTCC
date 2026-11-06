# Contrato: base do módulo Relatórios

Para a feat-11 (Célio Benjamim). Decisões da spec 010, seção "Contratos desta feature" e
Clarifications; ciência no índice Q-151, **antes** da fase base. Mudança de comportamento volta para cá.

## §1. Registrar um relatório (`registro.py`)

```python
@relatorio(
    id="defesas-realizadas",
    nome="Defesas realizadas no período",
    descricao="Sessões Realizadas, com banca e parecer",
    frase="Sessões realizadas no período, com banca e parecer.",
    perfis=("coordenador", "secretaria", "professor_disciplina"),
    filtros=("periodo", "ano_semestre", "curso"),
    ordem=70,
)
def defesas_realizadas(usuario, filtros):
    ...
```

- `perfis`: tupla não vazia, no vocabulário de `tem_perfil`. Decide quem **abre**.
- O recorte das **linhas** fica na função, que recebe o usuário (ex.: só as próprias turmas).
- `filtros`: subconjunto de `periodo`, `ano_semestre`, `curso`, `docente`, `agrupar_por`, `abrangencia`.
  O Painel e Membros Externos declaram `periodo` e `ano_semestre`.
- Erro de declaração levanta `ImproperlyConfigured` ao carregar: perfis vazios ou fora do vocabulário,
  `id` repetido ou fora do formato slug, filtro desconhecido.
- Módulo novo: importe em `RelatoriosConfig.ready()`. Lista, menu, permissões e exportação não mudam.
- Funções: `relatorios_do_usuario(usuario)`, `obter(id)`, `pode_abrir(usuario, registrado)`.

## §2. Filtros (`forms.py`)

`FiltroRelatorioForm(dados, usuario=..., registrado=...)` herda `FiltroPeriodoForm`, normaliza os dados
antes de validar e só cria os campos que o relatório declara. Curso e Docente só existem na gestão.

- `form.is_valid()` falso: `montar_relatorio` não consulta, e a view não exporta. `form.querystring()` também
  existe com filtro inválido, para o redirecionamento. `form.filtro()` herdado é proibido
  (`NotImplementedError`); use `form.filtros()`.
- `Filtros` tem `gestao`, `ano`, `semestre`, `inicio`, `fim`, `cur_id`, `doc_id`, `agrupar_por` e
  `abrangencia`, além de:
  - `periodo_q(prefixo="")`: usa `filtro_de_periodo`. Para sessão: `periodo_q("pre_def__")`;
  - `resumo()`: linha "Mostrando";
  - `querystring()`: forma canônica dos filtros.
  - `aplicados`: pares (rótulo, valor) que vão para a linha "Mostrando" e para os arquivos.
- **Invariantes**: ou `ano` e `semestre` (Período Letivo), ou `inicio` e `fim`, nunca os dois. Relatório só
  com `ano_semestre` usa `ano` e `semestre`, e `periodo_q` filtra a turma do TCC. `cur_id=None` significa
  Todos só com `gestao=True`. Fora da gestão, `doc_id = usuario.pk`, nunca `None`.
- `filtro_de_periodo(..., *, ano_semestre=None)` e `intervalo_do_atalho(atalho, hoje)`: sem o parâmetro
  novo, comportamento da feat-07.

## §3. Estrutura (`estrutura.py`)

```python
Coluna(chave, rotulo, numerica=False, definicao="")   # definicao vira title (MR-04)
Celula(texto, url=None, numerica=False)               # url só por estrutura.link_seguro(), só https
Linha(valores, destaque=False, sublistas=())          # valores: dict por chave da coluna
SubLista(titulo, colunas, linhas, vazio="Nenhum registro")
Kpi(rotulo, valor)                                    # no máximo 4
Grafico(tipo, dados, resumo)                          # "barras", "empilhado" ou "linhas"
Relatorio(colunas, linhas, totais=(), kpis=(), grafico=None, como_calculado=(),
          tem_registros=None, rotulo_linha="", id="", titulo="", frase="", gerado_em=None)
```

- **Valor canônico**: `int` para contagem (`numerica=True`) e `str` já formatada para o resto, ou `Celula`
  para link. Data como `DD/MM/AAAA`. Vazio é `""`, nunca `"-"`. `bool`, `date` e `None` são recusados em
  `__post_init__`.
- `Linha.celulas(colunas)` devolve sempre uma lista ordenada de `Celula`. O template e os exportadores
  usam `Relatorio.linhas_prontas()` e `totais_prontos()`, que já trazem as células e as sub-listas
  resolvidas, porque o template não chama método com argumento.
- `link_seguro(valor)`, em `estrutura.py`, devolve `Celula` com `url` só para `https` com netloc. No
  template: `<a href="{{ c.url }}" target="_blank" rel="noopener noreferrer">`, com autoescape e sem
  `mark_safe`. Nas sub-listas do Painel, nenhuma célula tem `url`.
- A base mantém a ordem de `linhas`. Ordenação é da consulta.
- `destaque`: vale em linha e em linha de sub-lista, na tela, no PDF e no XLSX, com negrito além do fundo;
  no CSV, vale a ordem.
- `totais`: uma ou mais `Linha` com rótulo próprio (Total, total de horas), nos 3 formatos.
- `tem_registros=None` deriva de `bool(linhas)`; `False` aciona a mensagem da US e desabilita a exportação.
  Todo relatório com linhas zeradas sobrescreve: Painel, Produção por Área ou Modalidade, Formação e
  Produção com Curso Todos.
- Sub-listas exigem `rotulo_linha`, a chave da coluna da linha-mãe: sem ela, o construtor falha.
- Sub-listas de mesmo título têm as mesmas colunas.
- `id`, `titulo`, `frase` e `gerado_em` vêm do registro e são preenchidos por `montar_relatorio`; a
  consulta não os informa.
- `montar_relatorio(usuario, registrado, dados)` devolve `(form, relatorio)`, com `relatorio=None` e sem
  consulta quando o formulário é inválido; a tela usa título e frase do registro.

## §4. Exportação (`exportacao.py`)

`exportar(relatorio, filtros, formato) -> HttpResponse`. Sem código por relatório.

| Formato | Saída |
|---|---|
| PDF | Cabeçalho, filtros, KPIs em tabela, tabela, `totais` e sub-listas com título, data de geração; paisagem; sem gráfico e sem link |
| CSV | UTF-8 com BOM, `;`; título, filtros e data; tabela e `totais`; um bloco titulado por sub-lista, com a coluna da linha-mãe; sem KPIs |
| XLSX | Aba principal com filtros, data, tabela e `totais`; uma aba por sub-lista, com a coluna da linha-mãe; sem KPIs |

Toda `str` é protegida contra fórmula. Títulos de aba são saneados. Resposta com `attachment` e `no-store`.
Nome: `relatorio-<id>-<AAAAMMDD-HHMM>.<ext>`. Falha em qualquer formato vira MR-07.

## §5. Layout

`relatorios/relatorios.html` é o layout único; a feat-11 não cria template de tela. Parciais:
`_grafico_barras.html`, `_grafico_empilhado.html`, `_grafico_linhas.html`, com dados de `graficos.py`,
que entrega números como `str` com ponto. Cores só pelos tokens de FR-073.

## §6. Atendimento à feat-11

| RBN | Necessidade | Coberta por |
|---|---|---|
| RBN-REL-03.1 | Filtro de período das defesas e de Curso | §2 |
| RBN-REL-03.2 | Professor só com as próprias turmas; alunos por turma; destaque de aluno na sub-lista | §1, §3 |
| RBN-REL-03.3 | Aprovados para TCC 2 primeiro e destacados | §3 |
| RBN-REL-03.4 | Uma linha por ouvinte e total de horas | §3 (`totais`) |

**A definir na spec 011**: recorte do Professor em 03.1, 03.3 e 03.4 (a matriz só o fixa em 03.2) e quem é
Professor e Coordenador ao mesmo tempo.
