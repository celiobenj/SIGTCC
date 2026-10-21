# [Feat-03] Turmas e Alunos (US-07, US-08, US-09)

**Origem**: `feature/feat-03-turmas-e-alunos` → **Destino**: `develop` (merge `--no-ff`, PGCS 6.4)

**Spec**: `specs/004-turmas-alunos/` (spec.md, plan.md, research.md, data-model.md, contracts/rotas.md, contracts/servicos-compartilhados.md, quickstart.md, tasks.md)

**Responsável**: Julia Cohen

> **Base**: a feat-02 já está na `develop` (`17c0bdd`). O diff do PR traz só os commits da feat-03 (`git log origin/develop..HEAD`).

### 1. Resumo da Alteração

Implementa turmas e alunos sobre o modelo de dados da feat-01 e a base da feat-02, **sem criar tabelas nem colunas**. A única migração nova é a carga de dados `0005_carga_equivalencia_cursos`; `makemigrations --check` responde "No changes detected".

- **Turmas (US-07)**: "Nova turma" com Código da Disciplina, Descrição (TCC 1 ou TCC 2), Identificador único, ano, semestre, dia, horário, Local e Curso; quem cadastra é o Professor da Disciplina. Na edição, Descrição e Curso ficam travados na turma que tem ou já teve aluno (Q15). Só a turma que nunca teve aluno pode ser excluída (Q12; evento `TURMA_EXCLUIDA` no log). O arquivamento é recusado com TCC Em Andamento ou Apto para Defesa, com sessão de defesa ativa ou sem a Data Limite da Versão Final vencida. A turma arquivada fica só para consulta, e qualquer ação pelo endereço direto mostra a MT-25.
- **Matrícula (US-08)**: matrícula individual (Matrícula, Nome Completo e Curso), com conta nova 'Aguardando Ativação' ou vínculo da conta existente; aviso de curso divergente (MT-13) e de código não reconhecido. Nas turmas de TCC 2 de Engenharia de Computação e Licenciatura em Computação, o professor vira orientador automático (RBN-CAD-04.2). Aluno aprovado em TCC 1 tem o TCC copiado para a turma de TCC 2 (Q6); TCC em curso noutra turma, TCC concluído e aprovado para TCC 2 em turma de TCC 1 são recusados (MT-26 a MT-28). Os registros do aluno nas entregas da turma são criados na matrícula (Q17, Q18).
- **Importação (US-08, diagrama "Matrícula por CSV")**: CSV ou XLSX até 2 MB e 200 alunos, com ";" ou ",", UTF-8 (com ou sem BOM) ou Windows-1252; XLSX só da primeira planilha, lido com `defusedxml` e limite de descompressão. A prévia (Novo, Já cadastrado, Rejeitado com linha e motivo) fica na sessão por 30 minutos, presa à turma e a um código de uso único (B10, MT-32). A confirmação grava linha a linha (uma linha com erro não desfaz as outras) e mostra o resumo MT-15. Modelo de importação para download.
- **Transferência (US-08)**: Professor da turma ou Secretaria do curso transferem o aluno com TCC Em Andamento ou Apto para Defesa para turma de TCC 2 do mesmo curso e período, de outro professor. O mesmo TCC vai com o Status e o histórico; o professor de destino passa a orientar; aluno e os dois professores são notificados (MT-22). Recusada com sessão de defesa ativa (MT-18).
- **Exclusão e encerramento (US-09)**: "Excluir da turma" só para aluno sem Proposta e sem movimentação, em duas etapas (justificativa e confirmação final MT-24); apaga o TCC 'Sem Proposta', o histórico de status e as entregas sem envio (Q8, Q17) e notifica o aluno com o motivo (MT-21, cortada em 500 caracteres). "Encerrar participação" como Desistente, Reprovado ou Jubilado, com histórico (gatilho "Encerramento da participação"), orientação e coorientação encerradas (Q10), pedidos e convites pendentes cancelados com aviso ao docente (Q14, Q19, MT-31) e recusa com sessão ativa (MT-30). Lista de excluídos ou transferidos só para o Professor (RBN-CAD-05.8).
- **Acesso por turma (Q9)**: o Professor da Disciplina da turma faz tudo; a Secretaria do curso só consulta e transfere; Coordenador e outros Docentes recebem 403 (M-02). Conferência sempre na ordem 404 → 403 → MT-25, e aluno de outra turma → 404 (sem IDOR).
- **Serviços para as outras features** (`contracts/servicos-compartilhados.md`): `participacao_encerrada(tcc)`, `travar_turma_ativa(tur_id)`, `notificar(usuario, mensagem, link)` (corte em 500 caracteres e link só interno), `turma_tem_orientador_automatico`, `criar_entregas_do_aluno` e `encerrar_orientacoes_ativas`. Concorrência: travas sempre na ordem turma(s) → aluno → TCC, com tudo conferido de novo depois de travar (B17).

### 2. Rastreabilidade com o Projeto

* Feature Impactada: Feature 03 - Turmas e Alunos (spec 004)
* Histórias de Usuário Atendidas: US-07 [RBN-CAD-04.1][RBN-CAD-04.2][RBN-CAD-04.3][RBN-CAD-04.4][RBN-CAD-04.5], US-08 [RBN-CAD-05.1][RBN-CAD-05.2][RBN-CAD-05.3][RBN-CAD-05.5][RBN-CAD-05.6][RBN-CAD-05.7], US-09 [RBN-CAD-05.4][RBN-CAD-05.8][RBN-CAD-08.4][RBN-CAD-08.5][RBN-CAD-08.7]. Cada classe, função, template e teste cita as US, RBN ou FR que atende; a conferência foi feita por script na T039.
* Requisitos da spec 004: FR-001 a FR-029; SC-001 a SC-007 (SC-003 e SC-007 também pelo roteiro manual, ver seção 4).
* Cartão no Trello: Atividade 3.3 – Implementação da camada de interface e das regras lógicas

**Commits deste PR** (só os da feat-03)

| Commit | Mensagem |
|---|---|
| adc7cdc | docs(feat-03): especificar turmas e alunos |
| 50aab55 | docs(feat-03): planejar turmas e alunos |
| c1ba6a3 | docs(feat-03): registrar aprovacao das tarefas e diagrama da us-08 |
| 8434e31 | chore(feat-03): preparar dependencias e carga de cursos da uea |
| 9b8503c | feat(feat-03): adicionar permissoes por turma e servicos compartilhados |
| a1fdf5d | feat(feat-03): cadastrar, editar, excluir e arquivar turmas |
| 5ffc32e | feat(feat-03): matricular aluno e editar dados do aluno |
| ba3b1a5 | feat(feat-03): importar alunos por csv e xlsx com previa |
| 6cad246 | feat(feat-03): transferir aluno entre turmas de tcc 2 |
| 9c67364 | feat(feat-03): excluir aluno e encerrar participacao |
| 9a93c4f | test(feat-03): conferir permissoes, mensagens e seguranca das turmas |
| d140b26 | docs(feat-03): registrar entrega no changelog e texto do pr |
| db73f0f | docs(feat-03): registrar tempo do roteiro e importacao real pendente |
| (este) | docs(feat-03): atualizar commits do texto do pr |

### 3. Checklist Técnico da Equipe (Definition of Done)

- [x] O código foi verificado localmente com isort, black e flake8, o equivalente do `lint.bat` fora do Windows. Rodando duas vezes, a segunda passada não altera nada, e o `flake8 sigtcc/` não aponta erros (T040).
- [x] Não há variáveis, imports ou trechos de código não utilizados (flake8 limpo).
- [x] Migrações: só a carga de dados `0005_carga_equivalencia_cursos` (reversível); nenhuma mudança de esquema; `makemigrations --check --dry-run` → "No changes detected"; nenhuma migração antiga alterada.
- [x] O arquivo `.env` e a pasta `media/` NÃO foram adicionados ao Git (`git ls-files`). Os arquivos de importação não são gravados em disco pela aplicação: a prévia guarda só matrícula, nome e curso na sessão.
- [x] A interface segue a paleta e os padrões do protótipo de 17/10 (ISO/IEC 25010), com a base visual da feat-02, conferida em 360, 768 e 1280 px (quickstart, seção 4; T042, Julia Cohen, 2026-10-21).
- [x] Não há quebras de layout ou erros no console do navegador (roteiro manual, T042).

### 4. Evidência da Validação Manual (Critérios de Aceite das USs)

Suíte completa: `python manage.py test sigtcc.apps` → `Ran 421 tests ... OK` (229 das features 001 e 003 e 192 novos).

**Validação manual (T042, Julia Cohen, 2026-10-21)**
- [x] Roteiro do `quickstart.md` executado (seções 1 a 6, itens a a o), sem divergências
- [x] SC-007: itens a e d em menos de 2 minutos (limite: 5 minutos)
- [ ] Importação de uma exportação real do sistema acadêmico da UEA (limite de compressão do XLSX, N7): a testar depois (índice Q-43); não bloqueia o merge
- [x] Revisão visual em 360, 768 e 1280 px, lado a lado com o protótipo de 17/10, sem problemas

**US-07 – Turmas** (`test_us07_turmas.py`, 33 testes)
- [x] Cenários 1 a 13 (o 7, orientador automático, em `test_us08_matricula.py`), mais Q12, Q15, MT-01 a MT-10, identificador repetido em cadastro simultâneo, exclusão no log depois do commit e turma arquivada

**US-08 – Matrícula** (`test_us08_matricula.py`, 30 testes)
- [x] Cenários 1, 2, 3, 9, 10, 11 e 13, mais o 7 da US-07, Q6 (cópia do TCC aprovado), Q7 e Q-39 (MT-26 a MT-28), Q16 (MT-29), curso divergente e matrícula concorrente

**US-08 – Importação** (`test_us08_importacao.py`, 31 testes)
- [x] Cenários 4, 5, 7, 8 e 14, mais Q2, Q11, Q13, prévia presa à turma e de uso único (B-2, N3, MT-32), zip bomb (B-3) e SC-003 (60 linhas em até 10 s)

**US-08 – Transferência** (`test_us08_transferencia.py`, 22 testes)
- [x] Cenários 6 e 12, mais Secretaria do curso (Q9), destinos possíveis (I-1), sessão ativa (MT-18), entregas (Q17) e notificações (MT-22)

**US-09 – Exclusão e encerramento** (`test_us09_exclusao.py`, 25 testes)
- [x] Cenários 1 a 11 (7 e 8 pela regra `participacao_encerrada`), mais Q8, Q10, Q14, Q17, Q19, B-1, encerramento depois de transferência (I-2) e lista só do Professor (I-4)

**Base e transversais**
- [x] `test_base_turmas.py` (15), `test_notificar.py` (8) e `test_carga_equivalencia.py` (3): serviços compartilhados, `notificar()` e carga
- [x] SC-004: `test_permissoes_turmas.py` (12) confere todas as rotas, perfil por perfil (sem login, outro docente, Coordenador, Secretaria de outro curso e do curso, turma arquivada, aluno de outra turma, só POST)
- [x] SC-002: `test_mensagens_turmas.py` (4) confere os textos das US-07 a 09 e as MT-01 a MT-32 contra a tabela da spec
- [x] SC-005 e SC-006: `test_seguranca_turmas.py` (9) cobre autor, data e hora das exclusões, transferências e encerramentos, duas importações do mesmo aluno abertas ao mesmo tempo, upload acima de 2 MB e nenhum valor de célula no log

### Decisões e desvios registrados

| Decisão | Registro | Situação |
|---|---|---|
| Códigos de curso completos (EST08MCPD, EST31MSII, EST03MLV) e curso identificado pelo campo Curso | spec Q5, FR-015a; índice Q-17, Q-37, Q-38 | Decidido por Julia Cohen (2026-10-20) |
| MT-32 (prévia vencida, já usada ou de outra turma), lacuna de texto achada na implementação | spec, tabela de mensagens; índice Q-36 | A validar com a PO |
| Recusa do aluno 'Aprovado para TCC 2' em turma de TCC 1 (MT-28) | research B6; índice Q-39 | Provisória até a resposta |
| Resumo e "Cancelar" da importação só para o Professor (a Secretaria do curso abria as duas telas), como em `contracts/rotas.md` | commit `dc95011` | Correção sem mudança na spec |
| Regras fora de `services.py` (`services_turmas.py`, `importacao.py`), exceção ao princípio IV | plan, Complexity Tracking; índice Q-42 (6) | A aprovar pelo Célio |
| Mensagem do primeiro commit (antes `docs(feat-03)`, sem descrição) reescrita para `docs(feat-03): especificar turmas e alunos`, com push forçado (`--force-with-lease`) | PGCS 5 | Feito a pedido de Julia Cohen (2026-10-21) |

### Itens de configuração para revisão do Célio Benjamim (constituição, princípio IX; índice Q-34 e Q-42)

- [ ] `requirements.txt`: `openpyxl==3.1.5`, `et_xmlfile==2.0.0` e `defusedxml==0.7.1` (XLSX seguro)
- [ ] Módulos novos: `services_turmas.py`, `importacao.py`, `forms_turmas.py`, `views_turmas.py`, `cargas.py` (equivalência) e a subpasta `templates/cadastro/turmas/`
- [ ] Evento `TURMA_EXCLUIDA` no log de acesso da feat-02 e o serviço `notificar()` em `services.py`
- [ ] Migração de dados `0005_carga_equivalencia_cursos`
- [ ] Servidor de produção: limite de upload no servidor web em cerca de 2,5 MB (research B23; o Django recebe o arquivo inteiro antes da view, e a aplicação recusa acima de 2 MB) e `clearsessions` agendado (a prévia da importação fica na sessão)
- [ ] Exceção ao princípio IV (regras em `services_turmas.py` e `importacao.py`) ou conversão de `services.py` em pacote
- [ ] **Confirmar o nome da branch** `feature/feat-03-turmas-e-alunos` (índice Q-34; conferir com a numeração do PGCS 4.3)

### Pendências

| Pendência | Destino | Índice |
|---|---|---|
| Validar os 31 textos provisórios MT-01 a MT-32 (sem a MT-20) | Profa. Diana (PO) | Q-36 |
| Confirmar a recusa do aluno 'Aprovado para TCC 2' em turma de TCC 1 (MT-28) | Julia Cohen / PO | Q-39 |
| Ciência da regra do encerramento (sessão ativa, pedidos e convites cancelados, MT-31) | Leandra Matos | Q-40 |
| Criar os registros de entrega dos alunos já matriculados ao cadastrar entrega nova (US-43) | Leandra Matos | Q-41 |
| Itens de configuração e nome da branch | Célio Benjamim | Q-34, Q-42 |
| Importar uma exportação real do sistema acadêmico da UEA (N7) | Julia Cohen | Q-43 |

### 5. Revisão por Pares (Peer Review)

* Revisores Designados: Célio Benjamim (itens de configuração: Q-34 e Q-42) e Leandra Matos (código; as features de Orientação, Entregas e o painel do aluno usam `participacao_encerrada`, `travar_turma_ativa` e `notificar()`)
* Parecer do Revisor:

[ ] Aprovado integralmente para merge

[ ] Solicitação de ajustes (detalhar nos comentários)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
