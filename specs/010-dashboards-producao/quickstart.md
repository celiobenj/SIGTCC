# Quickstart: validar os Dashboards de Produção

**Feature**: [spec.md](spec.md) | **Rotas**: [contracts/rotas.md](contracts/rotas.md) |
**Base**: [contracts/base-relatorios.md](contracts/base-relatorios.md)

Roteiro manual para provar os 6 relatórios. Não contém código de implementação.

## Pré-requisitos

- `python manage.py migrate` (nenhuma migração nova).
- **Atenção: o `popular_demo` apaga todos os dados do banco.** Use um banco local de teste.

```bash
python manage.py popular_demo --senha Demo2026sig --confirmar --local
python manage.py runserver
```

As contas e o roteiro saem na tabela impressa no fim do comando.

## 1. Roteiro manual

| # | Quem | Ação | Resultado esperado |
|---|---|---|---|
| a | Aluno e Membro Externo | Abrir o menu; abrir `/relatorios/` | Sem item Relatórios; acesso negado |
| b | Docente comum | Relatórios → Painel | Só a própria linha, sem filtros Docente e Curso; expandir por teclado |
| c | Docente comum | Pôr `?docente=` e `?curso=` no endereço, na tela e na exportação | Valores ignorados |
| d | Coordenador | Abrir o Painel; trocar curso e docente | Docentes com zeros; docente de outro curso aparece |
| e | Qualquer um | Este Mês, depois Esta Semana; depois datas invertidas seguidas de troca de atalho | Datas trocam junto com o atalho; o erro some |
| e2 | Docente | Atalho por data, com orientando de TCC Concluído há tempos | Esse orientando não conta (FR-022) |
| f | Qualquer um | Datas invertidas | Mensagem exata junto ao campo, sem atualizar |
| g | Coordenador | Produção: cada agrupamento e abrangência | Totais fecham; Não informada aparece |
| h | Coordenador | Artigos | Colunas exatas; Link `https` abre fora; MR-14 sem análise |
| i | Coordenador | Formação no período passado | Aprovado para TCC 2 em Com Sucesso; soma fecha |
| j | Coordenador | Histórico | Linhas do mais antigo ao mais recente, sem filtro de período |
| k | Secretaria | Abrir por endereço Formação, Histórico, Produção e Artigos, na tela e na exportação | Acesso negado |
| l | Secretaria | Membros Externos | Curso Vinculado por padrão; pessoas distintas; suplente não acionado fora |
| m | Coordenador | Baixar PDF, CSV e XLSX de cada relatório | Iguais à tela; PDF sem gráfico |
| m2 | Coordenador | Abrir o CSV do Histórico numa planilha real | Acentos e colunas certos. Conferir também título começando com espaço e `=`. Se "2026/2" virar data, anotar: é aceito, e o XLSX é o formato fiel |
| n | Coordenador | Filtro sem resultado | Mensagem da US e sugestão; botões desabilitados com o motivo no `title` |
| o | Coordenador | "Limpar filtros" e Voltar do navegador | Volta ao padrão; refaz o filtro anterior |
| p | Todos | Defesas, agenda e ouvintes | Comportamento igual ao de antes |

## 2. Revisão de apresentação

Conferir em 360, 768 e 1280 px, com o console sem erros e com o JavaScript desligado. Passar o
checklist de Nielsen do guia, com uma exceção combinada: o item 5 confere a mensagem do servidor,
porque a spec retirou `min` e `max` das datas. Fazer o teste de 5 segundos (SC-008).

## 3. Verificação automática

```bash
python manage.py test sigtcc.apps.relatorios --noinput
python manage.py test --noinput --parallel 4
python manage.py makemigrations --check --dry-run
pre-commit run --all-files
```

## 4. Verificação automática executada (T051)

Em 07/11/2026, no commit `313bd55` (`manage.py test --noinput --parallel 4`): 1777 testes, todos
passando, mais 1 falha esperada marcada como `expectedFailure` (anterior a esta spec).
`pre-commit run --all-files` sem ocorrências; `makemigrations --check --dry-run`: "No changes detected".

**SC-001**, medido no banco de teste com o `popular_demo` (58 vínculos, 58 TCCs, 20 docentes e 7 sessões),
com Curso Todos: tela em no máximo 0,04 s nos 6 relatórios (maior tempo de 5 repetições) e arquivos em
no máximo 0,22 s (PDF do Painel). A meta é 2 segundos. O volume é menor que o esperado em produção
(achado U1 do `/speckit-analyze`, fora das correções), então a medição não prova a escala real.

## 5. Resultado da validação manual

A preencher depois do roteiro (T052).
