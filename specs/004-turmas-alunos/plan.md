# Implementation Plan: Turmas e Alunos do SIGTCC

**Branch**: `feature/feat-03-turmas-e-alunos` (confirmação do nome: Q-34 do índice) | **Date**: 2026-10-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/004-turmas-alunos/spec.md` (aprovada por Julia Cohen em
2026-10-20)

**Responsável**: Julia Cohen (US-07, US-08 e US-09).

**Aprovação**: plano aprovado por Julia Cohen em 2026-10-20.

**Revisão de 2026-10-21**: o `arquiteto-django` revisou o plano (3 bloqueantes, 13 importantes, 20
menores). Todos foram aplicados no research (marcados com o ID do achado), no data-model e nos
contratos; as decisões de comportamento viraram as Clarifications Q13 a Q17 da spec, decididas por
Julia Cohen.

## Summary

Implementar no app `cadastro` a manutenção das turmas de TCC (cadastro, edição, exclusão da turma
vazia e arquivamento), a matrícula de alunos (individual e por importação de CSV ou XLSX com prévia,
conforme o diagrama "Matrícula por CSV"), a edição dos dados do aluno, a transferência entre turmas
de TCC 2 com orientador automático, a exclusão do aluno sem Proposta e o encerramento da
participação, com a lista de excluídos ou transferidos. Mensagens exatas das US-07, 08 e 09 e as
provisórias MT-01 a MT-30.

Abordagem: regras em `services_turmas.py` e `importacao.py`, views finas em `views_turmas.py`,
permissão por turma (Professor da Disciplina da própria turma; Secretaria do curso só para consulta
e transferência), turma travada nas operações que alteram dados, importação com prévia na sessão e
confirmação linha a linha com savepoint. Reutiliza da spec 003 a base visual, `@perfil_requerido`, a
regra da Q27, a conta 'Aguardando Ativação' sem link, a central de notificações (as notificações
passam a ser criadas pelo serviço novo `notificar()`, research B21) e o log. Nenhuma tabela ou
coluna nova; a única migração é a carga da equivalência de cursos (dados, FR-015a).

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Django 5.2.18, psycopg 3, python-dotenv (já no `requirements.txt`).
**Novas**: `openpyxl` (leitura de XLSX, spec Q4) e `defusedxml` (XML seguro no `openpyxl`), com
versão exata no `requirements.txt` (research B9) – itens de configuração para o Célio Benjamim
(índice Q-42). O CSV usa o módulo `csv` da biblioteca padrão.

**Storage**: PostgreSQL 16 com as tabelas da spec 001 (nenhuma nova). Prévia da importação na sessão
do usuário (`django_session`), por até 30 minutos. Exclusão de turma registrada no
`LOG_DIR/acesso.log` da spec 003.

**Testing**: test runner do Django contra PostgreSQL; base `TesteAcesso` e fábricas da spec 003
(`tests/apoio_acesso.py`, `tests/fabricas.py`), `force_login`; arquivos CSV e XLSX de teste gerados
em memória (o XLSX com `openpyxl`); relógio controlado com `avancar_relogio` (Data Limite da Versão
Final); tempo medido com margem na importação de 60 linhas (SC-003), sem `assertNumQueries` exato
(research B24).

**Target Platform**: servidor web Linux ou Windows (fuso America/Manaus); navegadores atuais, de
360 px para cima (spec 003, Q22).

**Project Type**: aplicação web monolítica com renderização no servidor (Django MVT).

**Performance Goals**: importação de até 60 alunos em até 10 segundos (SC-003; RAN-CAD-05); cadastro
de turma mais importação de 30 alunos em até 5 minutos pelo Professor (SC-007, teste manual).

**Constraints**: nenhuma tabela ou coluna nova (FR-028); mensagens idênticas às US e à tabela MT
(SC-002); nenhuma ação em turma arquivada nem por quem não é o Professor da Disciplina da turma
(SC-004); arquivo de até 2 MB e 200 linhas de alunos (Q13), XLSX até 20 MB descompactado; nenhum
JavaScript do protótipo; contas novas sem e-mail e sem link (spec 003, Q1); notificações sempre pelo
`notificar()` (até 500 caracteres).

**Scale/Scope**: 3 US (38 cenários), 30 FR (FR-001 a FR-029 e FR-015a), 29 mensagens provisórias;
cerca de 14 telas e 18 rotas; turmas de até 60 alunos, dezenas de turmas por semestre.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Verificação | Resultado |
|---|---|---|
| I. Especificação primeiro | spec 004 e plan aprovados por Julia Cohen em 2026-10-20 e tasks em 2026-10-21, sem marcadores pendentes. | PASSA |
| II. Rastreabilidade | Serviços, views, formulários, templates e testes levam [US-XX][RBN-...]; testes nomeados pelo cenário da US. | PASSA |
| III. Modelo de dados oficial | Nenhuma tabela ou coluna nova ([data-model.md](data-model.md)); `Equivalencia_Cursos` guarda os códigos no formato do dicionário (spec Q5, índice Q-38); curso do aluno no `alu_codigo_curso` existente (Q3). Única migração: carga de dados da equivalência. | PASSA |
| IV. Arquitetura | Tudo em `sigtcc/apps/cadastro`; regras em `services_turmas.py`, `importacao.py` e `permissoes.py`, views só orquestram, templates sem regra; templates em `sigtcc/templates/cadastro/turmas/`, static em `sigtcc/static/`. O princípio fala em `services.py`: os módulos `services_turmas.py` e `importacao.py` são exceção justificada (Complexity Tracking; Célio, Q-42). | PASSA com exceção justificada |
| V. Qualidade | lint.bat; comentários em português. | PASSA |
| VI. Testes de aceitação | Um teste por cenário das 3 US (38), mais permissões, turma arquivada, importação (formatos, codificações, desempenho), mensagens exatas e concorrência. | PASSA |
| VII. Segurança e LGPD | Turma e alunos visíveis só ao Professor da Disciplina e à Secretaria do curso (Q9), e a lista de excluídos só ao Professor; vínculo aluno-turma exigido em toda rota de aluno (sem IDOR); ações com a turma travada e revalidadas, em ordem fixa; upload limitado a 2 MB e 200 linhas, tipo pelos bytes, XLSX contra zip bomb e XML malicioso; prévia presa à turma por token, com dados mínimos na sessão; nenhuma senha ou e-mail criado; exclusões, transferências e encerramentos com autor, data e hora. | PASSA |
| VIII. Gerência de configuração | Commits atômicos por fase; branch `feature/feat-03-turmas-e-alunos`; `requirements.txt` com versões exatas do `openpyxl` e do `defusedxml`; carga de dados com migração no mesmo PR. | PASSA (nome da branch: Q-34; `openpyxl`: aprovação do Célio) |
| IX. Governança | Escopo e textos com a PO (Q-36, mensagens provisórias); itens de configuração ao Célio. | PASSA |

**Reavaliação depois do Phase 1 e da revisão**: nenhuma violação nova. Acréscimos ao contrato da spec
003, sem mudar o que já existe: `services.notificar()` (B21), `EventoAcesso.TURMA_EXCLUIDA` (B4), as
regras por turma em `permissoes.py` (B2), `curso_do_codigo` novo em `services.py`, com
`curso_do_aluno` delegando a ela e `services_turmas` reexportando (B6, sem importação circular), o item "Turmas" no menu e o parâmetro opcional `curso` em
`apoio_acesso.criar_secretaria` (B24).

## Project Structure

### Documentation (this feature)

```text
specs/004-turmas-alunos/
├── spec.md              # aprovada em 2026-10-20
├── plan.md              # este arquivo
├── research.md          # Phase 0 (B1 a B25)
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   ├── rotas.md                     # telas e rotas
│   └── servicos-compartilhados.md   # o que as outras features usam
├── checklists/requirements.md
└── tasks.md             # Phase 2 (/speckit-tasks)
docs/diagramas/Diagramas_Sequencia_PlantUML_v2.md   # diagrama 35 MatricularAluno
```

### Source Code (repository root)

```text
requirements.txt                       # + openpyxl e defusedxml (versões exatas)
sigtcc/apps/cadastro/
├── services_turmas.py                 # novo: B3 a B8, B12 a B17, B22
├── importacao.py                      # novo: B9 a B11
├── forms_turmas.py                    # novo: B18
├── views_turmas.py                    # novo
├── permissoes.py                      # + regras por turma (B2)
├── cargas.py                          # + CURSOS_COM_ORIENTADOR_AUTOMATICO (B8)
├── urls.py                            # + rotas de turmas (contracts/rotas.md)
├── menu.py                            # + item "Turmas"
├── mensagens.py                       # + textos das US-07, 08, 09 e MT-01 a MT-30
├── services.py                        # + notificar() (B21), TURMA_EXCLUIDA (B4), curso_do_codigo (B6)
├── migrations/00NN_carga_equivalencia_cursos.py   # novo, só dados (B20)
└── tests/
    ├── apoio_turmas.py                # turmas, alunos, TCCs, defesas, entregas e arquivos de teste
    ├── apoio_acesso.py                # + criar_secretaria(..., curso=None) (B24)
    ├── test_us07_turmas.py
    ├── test_us08_matricula.py
    ├── test_us08_importacao.py        # + prévia presa à turma, limites, zip bomb, codificações
    ├── test_us08_transferencia.py
    ├── test_us09_exclusao.py          # + entregas com e sem envio, notificação de 500 caracteres
    ├── test_permissoes_turmas.py
    ├── test_mensagens_turmas.py
    └── test_carga_equivalencia.py
sigtcc/templates/cadastro/turmas/
├── lista.html, arquivadas.html, turma.html, form_turma.html
├── confirmar.html                     # exclusão e arquivamento da turma
├── matricular.html, importar.html, previa.html, resumo.html   # prévia com token oculto
├── editar_aluno.html, transferir.html
├── excluir_aluno.html, encerrar.html
└── excluidos_transferidos.html
```

**Structure Decision**: monólito Django do PGCS 2.3, app `cadastro` (Épico 1), com módulos novos por
assunto (research B1) e templates numa subpasta de `cadastro/`.

## Pendências desta feature

Índice central: [docs/questoes-a-rever.md](../../docs/questoes-a-rever.md).

| Pendência | Destino | Índice |
|---|---|---|
| Confirmar a branch `feature/feat-03-turmas-e-alunos` | Célio Benjamim | Q-34 |
| Validar os textos provisórios MT-01 a MT-31 | Profa. Diana (PO) | Q-36 |
| Confirmar a recusa do aluno 'Aprovado para TCC 2' em turma de TCC 1 (MT-28) | Julia Cohen | Q-39 |
| Aprovar `openpyxl` e `defusedxml`, os módulos novos, a subpasta `templates/cadastro/turmas/`, `notificar()`, o evento `TURMA_EXCLUIDA`, o limite de upload no servidor e o `clearsessions` agendado | Célio Benjamim | Q-42 |
| Ciência do encerramento recusado com sessão ativa e do cancelamento de pedidos e convites pendentes | Leandra Matos | Q-40 |
| US-43 criar os registros dos alunos já matriculados ao cadastrar uma entrega nova | Leandra Matos | Q-41 |
| Bloqueios em turma arquivada (`travar_turma_ativa`) e participação encerrada nas outras features (entregas, atas, defesa, Versão Final, lembretes, editar TCC, orientador) | Leandra, Célio, Maria Luísa e responsáveis de TCC/Entregas | contrato §1 e §2 |
| Relatórios contarem o aluno 'Aprovado para TCC 2' e a publicação uma vez; exportações neutralizarem fórmulas | Maria Luiza Guimarães (Relatórios, Épico 3) | contrato §5 |
| Tela `/alunos/<id>/` da spec 003 mostra e-mail e status de qualquer aluno a qualquer Professor da Disciplina | Julia Cohen / PO | S-02 (observação de LGPD) |
| US-41 levar "Excluir da turma", "Encerrar participação", "Editar" e "Transferir" ao painel do aluno | Leandra Matos | spec 004, Assumptions |

## Complexity Tracking

Nenhuma violação da constituição sem justificativa. Exceção justificada: princípio IV (regras também
fora de `services.py`). Escolhas que merecem registro:

| Escolha | Por quê | Alternativa mais simples rejeitada |
|---|---|---|
| Dependências novas `openpyxl` e `defusedxml` | A matriz e a US-08 pedem XLSX (spec Q4); o `defusedxml` protege o `openpyxl` de XML malicioso | Só CSV: descumpre o RBN-CAD-05.2 |
| Prévia guardada na sessão e revalidada na confirmação | O diagrama separa prévia e confirmação; dados podem mudar no meio | Reenviar o arquivo na confirmação (pior para o usuário) |
| Savepoint por linha na confirmação | Linhas válidas entram mesmo se outra falhar no meio (Q2) | Uma transação só: uma falha desfaz tudo |
| Módulos `services_turmas.py`, `importacao.py`, `forms_turmas.py` e `views_turmas.py` separados (exceção ao princípio IV) | Mantém o contrato da spec 003 intacto e os arquivos pequenos | Crescer `services.py` e `views.py`; ou pacote `services/` com `__init__` que reexporta (decisão do Célio, Q-42) |
