# Research: Dashboards de Produção

Decisões técnicas do plan 010. Nenhuma muda regra da spec.

## R1. Organização e fluxo

**Decisão**: `view → montar_relatorio(usuario, registrado, dados) → Relatorio → template ou exportacao`.
`montar_relatorio` é o único caminho: cria o formulário, consulta, preenche `id`, `titulo`, `frase` e
`gerado_em` uma vez e devolve `(form, relatorio)`, com `relatorio=None` e sem consulta se o formulário for
inválido. As views não calculam nada.

**Motivo**: uma só origem para tela e arquivos cumpre FR-018 e SC-005 por construção, e o recorte de
permissão não tem como existir num caminho e faltar no outro.

**Dados mudando**: o arquivo é recalculado no download, sem instantâneo, e `gerado_em` é o do
download. Se no download não houver registros, redireciona ao relatório.

**Alternativas**: template próprio por relatório, rejeitado porque a feat-11 teria de duplicar o
layout.

## R2. Filtro de período sem quebrar a Defesa

**Decisão**: extrair `intervalo_do_atalho(atalho, hoje)` de `filtro_de_periodo`, que passa a chamá-la,
e acrescentar `filtro_de_periodo(..., *, ano_semestre=None)`. Com `ano_semestre`, o atalho
`periodo_letivo` usa esse par; sem ele, usa `periodo_letivo_atual`, como hoje. `forms_defesa.py` não
muda: `FiltroRelatorioForm` herda `FiltroPeriodoForm`.

**Motivo**: as chamadas de produção são só as de `forms_defesa.py`, e o parâmetro só por palavra-chave
não as altera. A extração evita calcular as datas dos atalhos em dois lugares.

**Filtro inválido**: o `filtro()` herdado recua para o Período Letivo; no formulário novo ele levanta
`NotImplementedError`, e `montar_relatorio` não consulta com `is_valid()` falso (FR-014).

**Erro junto ao campo**: o `clean` do formulário novo move `DATA_INICIAL_MAIOR`, gravado sem campo pelo
pai, para `data_inicial`.

**Alternativas**: alterar `FiltroPeriodoForm`, rejeitado porque mudaria telas mescladas.

## R3. Normalização do formulário e atalho sem JavaScript

**Problema**: o formulário recebe sempre `request.GET`, então fica vinculado e `initial` é ignorado:
padrões, datas recalculadas e o oculto apareceriam com o valor recebido. Além disso, a regra herdada é
"datas preenchidas valem como intervalo", e as datas de Este Mês venceriam a troca para Esta Semana.

**Decisão**: normalizar **antes** de validar, no `__init__`, numa cópia mutável dos dados:

1. Valores fora da lista voltam ao padrão, inclusive `atalho` (R4).
2. `atalho_anterior` ausente conta como "não trocou".
3. Se `atalho` for diferente de `atalho_anterior`, as datas recebidas são apagadas: isso também tira o
   usuário de um erro de datas invertidas.
4. Curso, Docente e os demais padrões entram nos dados.

Depois da validação, os dados recebem o que foi aplicado: as datas do atalho e `atalho_anterior = atalho`.
Com Período Letivo e sem datas, elas ficam vazias.

**Casos**: "Limpar filtros" é um link sem query. Link compartilhado com datas congela o intervalo, o que
é aceitável. O form usa `autocomplete="off"`, para o Voltar do navegador não restaurar um select antigo.
Com atalho Este Mês e data editada à mão, o select continua em Este Mês, e a linha "Mostrando" é a
verdade. Ano/Semestre não tem efeito fora do Período Letivo.

**Links**: `Filtros.querystring()` é canônica e serve à exportação e ao redirecionamento.

**Alternativas**: JavaScript limpando as datas, rejeitado porque depende de script.

## R4. Valores inválidos no endereço

**Decisão**: datas inválidas seguem FR-014. `atalho`, Ano/Semestre, Agrupar por e Abrangência fora da
lista voltam ao padrão na normalização, sem virar erro de campo, porque um erro desligaria a validação
de datas do pai (`if self.errors: return`). Curso e Docente só passam se forem `todos` ou
`isdecimal()` com até 9 dígitos: `filtro_de_curso` aceita `"²".isdigit()` e quebraria em `int()`, e um
número gigante também quebraria. A linha "Mostrando"
exibe o que foi de fato aplicado.

**Recorte, sem padrão aberto**: `filtros()` define `gestao = tem_perfil(usuario, "coordenador",
"secretaria")`. Fora da gestão, os campos Curso e Docente não existem e `doc_id = usuario.pk`, nunca
`None`. `cur_id=None` só significa Todos com `gestao=True`. A consulta do Painel confere de novo:
`if not filtros.gestao: doc_id = usuario.pk`. Assim Professor, Orientador e Coorientador sem gestão
caem no recorte.

## R5. Status por período (FR-041)

**Decisão**: subconsulta sobre `HistoricoStatusTCC`, filtrada por `hst_tcc__tcc_alu` e `hst_tcc__tcc_tur`
iguais aos do vínculo em `AlunosTurmas`, com `order_by("-hst_data_hora", "-hst_id")`, envolta em
`Coalesce(..., "Sem Proposta")`.

**Motivo**: `uq_tccs_aluno_turma` garante um TCC por vínculo; a busca é pelo TCC, e o transferido
acha o registro. `Coalesce` cobre o vínculo sem TCC.

**Teste**: o último registro de cada TCC é igual a `tcc_status` (SC-003).

**Alternativas**: filtrar por `hst_tur`, rejeitado (D-01). Usar `tcc_status` direto, rejeitado
porque a matriz exige o histórico.

## R6. Contagem por grupo

**Decisão**: `GRUPOS_DE_STATUS` em `services_relatorios.py`. O `annotate` (ou `alias`) do Status vem
**antes** de `values(<agrupamento>)`, para não entrar no GROUP BY; depois,
`Count("mat_alu", filter=Q(status__in=...))`.

**Motivo**: é uma consulta só por relatório. "Sem Versão Final homologada" não entra na consulta: a
homologação já leva a Concluído (RBN-CAD-09.5).

**Custo**: cada `Count(filter=...)` reavalia a subconsulta por linha, o que não preocupa com centenas de
linhas. Se o `EXPLAIN` incomodar, a saída é `values(curso, status).annotate(n=Count("mat_alu"))`, com a
tabela montada em Python. A primeira tarefa testa R5 e R6 no PostgreSQL.

## R7. Painel de atividades (US-31)

**Decisão**: três consultas (`Orientacoes`, `Coorientacoes`, `BancaDefesa`), mais a de docentes. As
colunas e as sub-listas saem das mesmas listas, numa passagem em Python, e por isso não divergem.

- Coorientador: `coo_doc` não nulo (o externo não gera linha).
- Colunas: conjuntos de alunos por docente. Orientandos separados por `tur_descricao`; Coorientações
  só por docente, sem somar TCC 1 e TCC 2 (FR-023).
- Sub-lista: deduplicada por (TCC, papel). Bancas por data e `def_id`; orientações por nome do aluno e
  `tcc_id`. Status vem de `tcc_status`, igual ao último registro do histórico (SC-003).
- Bancas: `ban_def__def_status=Realizada`, `ban_papel__in=PAPEIS_TITULARES` e
  `filtros.periodo_q("ban_def__")`, com a sessão distinta por docente.

**Período Letivo**: `ori_tcc__tcc_tur__tur_ano` e `tur_semestre`.

**Intervalo**: ver R18.

**Linhas da gestão**: `services_contas.docentes_ativos()`, mais os docentes com atividade, filtrado por
`doc_cur`; com docente escolhido, só ele, sem o filtro Curso (P2). `tem_registros` é falso só com
Docente "Todos" e nenhuma atividade.

**`membros_efetivos`**: não dá para chamar por sessão sem gerar consulta por linha. O filtro por
`PAPEIS_TITULARES` é o mesmo que ela usa; `acionar_suplente` apaga a linha do ausente. Um teste compara.

**Papel "Suplente"**: linha com `ban_usu_substituido` preenchido.

## R8. Linha expansível

**Decisão**: botão real na primeira célula (`aria-expanded`, `aria-controls`) e a linha da sub-lista
logo abaixo. Sem JavaScript, as sub-listas ficam abertas e o botão, inerte, com `aria-expanded="true"`;
`relatorios.js` as recolhe e alterna. Enter e Espaço vêm do próprio botão. `@media print` abre as linhas
recolhidas.

**Filtros**: botão "Aplicar" sempre presente. `relatorios.js` só envia no `change` de select, nunca de
campo de data, para não enviar uma data incompleta.

**Motivo**: `<details>` não atravessa linhas de tabela, e o conteúdo continua acessível sem script.

## R9. Gráficos

**Decisão**: `graficos.py` monta `Grafico(tipo, dados, resumo)`, sem HTML. Barras: largura em %, da maior
para a menor. Empilhado: partes por curso, e curso com 0 Matriculados sem barra. Linhas: pontos
calculados para um `viewBox` fixo, com o valor escrito em cada ponto.

**Localização**: com `pt-br`, `{{ 33.3 }}` sai `33,3`, o que quebra `width` e `points`. `graficos.py`
entrega `str` com ponto (`f"{x:.2f}"`), e o teste confere o HTML. Rótulos e resumo usam `{{ }}` com
autoescape e atributo entre aspas.

**Cor do Histórico**: Vinculados `--azul`, Defesas `--verde`, Desistências `--vermelho` e Artigos
`--teal`, com traço tracejado, porque `--roxo` é só de Membros Externos (FR-073).

## R10. Exportação

- **Resposta**: um helper só, com `Content-Disposition: attachment`, `Cache-Control: no-store` e o `id`
  do registro, nunca da URL. Tipos: `application/pdf`, `text/csv; charset=utf-8` e
  `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`.
- **CSV**: `utf-8-sig`, `;`. Título, filtros e data de geração, uma linha em branco, a tabela com
  `totais` e um bloco por sub-lista.
- **XLSX**: aba principal com título, filtros e data acima da tabela e com `totais`; uma aba por sub-lista.
  Título de aba saneado e limitado a 31 caracteres.
- **PDF**: `pdf.gerar_pdf` e `relatorios/pdf/relatorio.html`, com KPIs em tabela simples, sem gráfico e
  sem `<a>`. KPIs só no PDF, como em FR-020. Paisagem por `<style>` no bloco `corpo`, com `margin`
  redeclarado; um teste confere `mediabox.width > height`. `LayoutError` vira MR-07. Link de 500
  caracteres entra no teste.
- **Sub-listas**: coluna da linha-mãe (`rotulo_linha`). Vazia sai com "Nenhum registro". Sub-listas de
  mesmo título têm as mesmas colunas e formam uma aba e um bloco.
- **Fórmula**: no CSV, `str` começando com `=`, `+`, `-`, `@`, tabulação, `\r` ou `\n` ganha `'` na
  frente. No XLSX, `ILLEGAL_CHARACTERS_RE.sub("", valor)` e `cell.data_type = "s"` em toda `str`, o que
  também cobre `#REF!`; `int` continua numérico.
- **Nome do arquivo**: `relatorio-<id>-<AAAAMMDD-HHMM>.<ext>`, sem nome de pessoa.
- **Sem registros, filtro inválido ou falha**: redireciona com `Filtros.querystring()`; na falha, nos
  3 formatos, `messages.error` com a MR-07.
- **Log**: só `id`, formato e `usu_id`, sem nomes, filtros nem query string.

## R11. Artigos Publicados no Histórico (FR-052)

**Decisão**: `Artigos` com `art_status_submissao=Publicado`, `tcc_modalidade=Artigo Científico` e o
filtro de Curso; `values(aluno, art_link_doi)` com `Min(ano * 10 + semestre)`; contagem em Python por
período, numa consulta só. `art_link_doi` é obrigatório.

**Motivo**: o par aluno e link identifica o artigo e suas cópias. Só o aluno juntaria dois artigos
diferentes de quem refez a disciplina.

**Limites**: link editado no TCC 2 com Publicado conta 2, e o filtro de Curso vem antes do `Min`. O
bloco "Como é calculado" explica.

## R12. Desempenho

**Decisão**: comparar 1 e 10 itens com `CaptureQueriesContext`, chamando a função de consulta, porque um
número fixo em `assertNumQueries` quebraria com sessão, menu e sino. `select_related` nas listas.
`curso_id_do_usuario` é chamado uma vez. Nenhum índice novo (exigiria migração). Medir SC-001 com o
`popular_demo`.

## R13. Registro e permissões

**Decisão**: decorador `@relatorio(...)` sobre a função de consulta; `apps.py` importa os módulos em
`ready()`. O decorador valida na importação (`ImproperlyConfigured`): `perfis` é tupla não vazia, no
vocabulário de `tem_perfil` (`tem_perfil` sem perfis devolveria verdadeiro), `id` em slug e único,
`filtros` no vocabulário. `registro.py` e `estrutura.py` não importam `services_relatorios`, e
`mensagens.py` só tem constantes, porque `cadastro/views.py` passa a importá-lo.

**Rotas**: `perfil_requerido()`, só com login, e a view confere o resto, para todos receberem a MR-06.
`exigir_modulo(usuario)` é `tem_perfil(usuario, "docente", "secretaria")`. Ordem na exportação: login,
`exigir_modulo`, 404 do id, `pode_abrir`, 404 do formato, formulário, consulta,
arquivo. Um teste confere que os 6 ids estão registrados.

## R14. Texto do filtro aplicado

**Decisão**: a linha "Mostrando" sai de `filtros.resumo()`, com o período ou as datas em DD/MM/AAAA e o
curso, docente, agrupamento e abrangência quando houver. Com docente específico, não cita o Curso, que
não foi aplicado (P2). `gerado_em` usa `timezone.now()` (`USE_TZ=False`).

## R15. Testes de filtro, igualdade e permissão

**Filtros**: `test_filtros_relatorios.py` cobre R2 a R4. A suíte da Defesa roda sem alteração (SC-006),
mais um teste de `filtro_de_periodo` com `ano_semestre`.

**Igualdade (SC-005)**: teste parametrizado, 6 relatórios × 3 formatos, que extrai cabeçalhos, linhas,
totais e sub-listas do HTML e de cada arquivo e compara com as mesmas sequências. O CSV compara contra
`proteger(valor)`. O PDF, por `pypdf`, confere presença e ordem aproximada.

**Dados hostis**: `=1+1`, `-x`, `@a`, `<script>`, aspas, `#REF!`, `\x0b`, link `javascript:` e link de
500 caracteres.

**Permissões (SC-004)**: 6 relatórios × (tela, 3 formatos, lista) × anônimo, Aluno, Membro Externo, conta
sem especialização, Docente, Professor, Orientador, Coorientador, Coordenador e Secretaria, mais
`?docente=<outro>&curso=<outro>&curso=todos` para quem não é gestão.

## R16. Produção de TCCs e Artigos

**Produção**: a base é `TCCs` das turmas do período, sem `Sem Proposta`, porque o agrupamento usa
`tcc_ari` e `tcc_modalidade`. A subconsulta de R5 usa `OuterRef("pk")`, sem `Coalesce`. `annotate` antes
de `values()`, como em R6.

**Artigos**: base `TCCs` com a modalidade Artigo Científico, e `select_related("artigos")` com tratamento
da ausência, porque o TCC sem linha em `Artigos` aparece. Orientador por `Subquery` com `Case` (ativa
primeiro), `-ori_data_inicio` e `-ori_id`. Link por um helper que aceita só `https` com `urlsplit` e
netloc.

## R17. Membros Externos

**Decisão**: `BancaDefesa` com os filtros de R7 e o Curso da turma do TCC; `Count("ban_usu", distinct=True,
filter=...)` por docente e por Membro Externo, numa consulta; instituições por `mem_instituicao`.

## R18. Vínculo em vigor no intervalo (FR-022)

**Problema**: `encerrar_orientacoes_ativas` só roda na matrícula em TCC 2 e no encerramento de
participação. TCC Concluído ou Reprovado mantém a orientação Ativa, com data de fim nula.

**Decisão** (Julia Cohen, 2026-11-06): fim efetivo =
`Coalesce(ori_data_fim, Case(When(tcc_status__in=STATUS_FINAIS, then=<data do último registro do histórico do TCC>)))`.
`STATUS_FINAIS` deriva de `GRUPOS_DE_STATUS`: Com Sucesso e Sem Sucesso (Concluído, Aprovado para TCC 2,
Reprovado, Desistente e Jubilado). Aprovado e Aprovado com Correções ficam em Ativos: o trabalho ainda
aguarda a Versão Final. `Case` e `Coalesce` declaram `output_field=TimestampField()`. Em vigor:
`ori_data_inicio__date__lte=fim` e (fim efetivo nulo ou `__date__gte=inicio`). O mesmo vale para
`Coorientacoes`, porque a liberação do resultado e a homologação não encerram coorientação. Encerrada e
Substituída sempre têm data de fim; o `Coalesce` só atua no vínculo Ativa.

**Efeito a explicar em "Como é calculado"**: o aluno Aprovado para TCC 2 deixa de contar depois da
aprovação, mas, depois de matriculado, a data de fim da orientação prevalece, e um intervalo entre a
aprovação e a matrícula volta a contá-lo.

**Teste**: em `test_us31_atividades.py`, para orientação e coorientação.

**Alternativas**: limitar a turma Ativa, rejeitado porque zeraria intervalos passados; aceitar e
explicar, rejeitado porque inflaria o número.
