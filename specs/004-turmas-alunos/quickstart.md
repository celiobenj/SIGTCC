# Quickstart: validar Turmas e Alunos

**Feature**: [spec.md](spec.md) | **Rotas**: [contracts/rotas.md](contracts/rotas.md) |
**Serviços**: [contracts/servicos-compartilhados.md](contracts/servicos-compartilhados.md)

Roteiro para provar, num ambiente de desenvolvimento, que turmas, matrículas, importação,
transferência, exclusão e encerramento funcionam como na spec. Não contém código de implementação.

## Pré-requisitos

- Features 001 e 003 aplicadas; `python manage.py migrate` (inclui a carga da equivalência:
  EST08MCPD, EST31MSII e EST03MLV).
- `pip install -r requirements.txt` (com o `openpyxl` e o `defusedxml`).
- `.env` com `DEBUG=True`; servidor com `python manage.py runserver`.

## 1. Contas de teste (comando da spec 003)

```bash
python manage.py criar_conta_teste --perfil docente --status ativa --email prof1@uea.edu.br --senha Tcc@2026a --curso "Engenharia de Computação"
python manage.py criar_conta_teste --perfil docente --status ativa --email prof2@uea.edu.br --senha Tcc@2026a --curso "Engenharia de Computação"
python manage.py criar_conta_teste --perfil docente --status ativa --email outro@uea.edu.br --senha Tcc@2026a
python manage.py criar_conta_teste --perfil secretaria --status ativa --email sec@uea.edu.br --senha Tcc@2026a --curso "Engenharia de Computação"
```

## 2. Arquivos de importação

- `alunos_ok.csv` (UTF-8, ";"): 30 linhas com cabeçalho `Matrícula;Nome Completo;Curso`, 2 delas com
  matrícula de 9 dígitos, 1 com o curso `EST99XXXX` (não reconhecido).
- `alunos_excel.csv`: o mesmo, salvo pelo Excel em português (";" e Windows-1252, com acentos).
- `alunos.xlsx`: 5 linhas na primeira planilha.
- `documento.pdf`, um XLSX de 3 MB e um CSV com 201 linhas de alunos.

Exemplos prontos (dados fictícios) em [`exemplos/`](exemplos/): `alunos_teste.csv` e
`alunos_teste.xlsx`, com os três códigos de curso da equivalência.

## 3. Roteiro manual

Cronometrar os itens a e d juntos (SC-007: até 5 minutos).

| # | Ação | Resultado esperado |
|---|---|---|
| a | Como `prof1`, "Turmas" → "Nova turma": TCC 2, Engenharia de Computação, Identificador `ECP06_T01`, 14:00–16:00, Local "Laboratório LSI" | "Turma cadastrada com sucesso"; prof1 é Professor da Disciplina (US-07, cenário 1) |
| b | Nova turma com término 08:00 e início 10:00; outra com `ECP06_T01` de novo; outra com Local de 101 caracteres | "O horário de término deve ser posterior ao de início"; campo Identificador destacado (MT-03); campo Local destacado (cenários 3, 12, 13) |
| c | "Matricular alunos" → "Matrícula individual": `2026000123`, nome, `EST08MCPD` | "Aluno matriculado com sucesso"; conta 'Aguardando Ativação'; prof1 é o orientador (cenário 1 da US-08; cenário 7 da US-07) |
| d | "Importar arquivo" com `alunos_ok.csv` → prévia → "Confirmar importação" | prévia com novos, erros (linha e motivo) e código não reconhecido; resumo com 28 matriculados, 2 rejeitadas e 1 código não reconhecido (cenários 4 e 8 da US-08) |
| e | Importar `alunos_excel.csv` e `alunos.xlsx` | acentos preservados; alunos já matriculados ignorados com "Aluno já matriculado nesta turma" (Q11; cenário 9) |
| f | Importar `documento.pdf`, o XLSX de 3 MB e o CSV de 201 linhas | "Arquivo fora do modelo. Baixe o modelo de importação" (cenários 5 e 14; Q13); baixar o modelo pelo link da tela |
| f2 | Abrir a importação de duas turmas em abas diferentes e confirmar na primeira | a confirmação é recusada com aviso (prévia de outra turma) e nada é gravado (B10) |
| g | Editar o nome de um aluno | nome gravado; Matrícula só leitura (cenário 10 da US-08) |
| h | Pelo shell, pôr o TCC de um aluno 'Em Andamento' com título, resumo e modalidade; como prof2, criar `ECP06_T02` (mesmo curso, ano e semestre); como prof1 ou `sec`, "Transferir" o aluno para `ECP06_T02` | aluno só na turma de destino, orientador prof2, notificações para o aluno, prof1 e prof2 (cenário 6 da US-08) |
| i | Excluir da turma um aluno sem Proposta; cancelar uma vez e confirmar na outra | cancelado: nada muda; confirmado: "Aluno excluído da turma", aluno na lista de excluídos ou transferidos, notificação ao aluno (cenários 1 e 10 da US-09) |
| j | Encerrar a participação de um aluno com Proposta como Desistente; antes, tentar com uma sessão de defesa 'Agendada' para ele | com a sessão: MT-30; sem ela: Status 'Desistente' no histórico, com prof1 como responsável, orientação encerrada e pedidos pendentes cancelados (cenário 3 da US-09; Q10, Q14) |
| k | Lista de excluídos ou transferidos | os dois casos (i e h, na turma de origem), com nome, matrícula, data e hora, autor e justificativa (cenário 9 da US-09) |
| l | Tentar arquivar a turma com TCC 'Em Andamento'; depois, sem TCC ativo e sem entrega 'Versão Final'; depois com a Data Limite vencida | "Há TCC Em Andamento ou Apto para Defesa"; "A Data Limite da Versão Final ainda não venceu ou não foi cadastrada"; arquivada (cenários 2, 9 e 10) |
| m | Abrir a turma arquivada e tentar `/turmas/<id>/matricular/` pelo endereço | só consulta, sem Editar, Matricular alunos e Excluir aluno; o endereço direto mostra a MT-25 (cenário 6 da US-07, 11 da US-08 e 11 da US-09) |
| n | Como `outro@uea.edu.br`, abrir `/turmas/<id>/` | 403 com a M-02 (Q9) |
| o | Excluir uma turma vazia nova; tentar excluir `ECP06_T01` | turma vazia removida; "A turma possui alunos matriculados. Use a opção Arquivar" (cenários 4 e 5; Q12) |

## 4. Revisão visual

Comparar com as telas "Gerenciar turmas de TCC", "Matricular alunos na turma" e "Excluir aluno da
turma" de `docs/fonte/prototipo/prototipo_17_10.html`, em 360, 768 e 1280 px, com o checklist da
spec 003 (paleta, fontes, ícones, campos com erro, tabelas sem rolagem da página).

## 5. Testes automatizados

```bash
python manage.py test sigtcc.apps
```

Esperado: todos passam (feature 001, feature 003 e esta). Arquivos novos: `test_us07_turmas.py`,
`test_us08_matricula.py`, `test_us08_importacao.py` (formatos, codificações, prévia, 60 linhas em até
10 s), `test_us08_transferencia.py`, `test_us09_exclusao.py`, `test_permissoes_turmas.py` (cada ação
pelo endereço direto, SC-004), `test_mensagens_turmas.py` (SC-002) e `test_carga_equivalencia.py`.

## 6. Qualidade

`lint.bat` (ou isort, black e flake8) sem erros; `makemigrations --check` só com a carga da
equivalência já aplicada.
