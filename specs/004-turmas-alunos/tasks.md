# Tasks: Turmas e Alunos do SIGTCC

**Input**: Design documents from `specs/004-turmas-alunos/`

**Prerequisites**: [plan.md](plan.md) (aprovado em 2026-10-20, revisado em 2026-10-21),
[spec.md](spec.md) (aprovada em 2026-10-20; Clarifications Q1 a Q19), [research.md](research.md)
(B1 a B25), [data-model.md](data-model.md), [contracts/rotas.md](contracts/rotas.md),
[contracts/servicos-compartilhados.md](contracts/servicos-compartilhados.md),
[quickstart.md](quickstart.md), diagrama `docs/diagramas/US-08_matricula_por_csv.puml`

**Aprovação**: tasks aprovado por Julia Cohen em 2026-10-21.

**Tests**: obrigatórios (constituição, princípio VI): cada cenário Dado/Quando/Então das US-07 (13),
US-08 (14) e US-09 (11) vira pelo menos um teste, mais os casos das Clarifications, de permissão, de
mensagens exatas e de segurança. Os testes de cada fase vêm antes da implementação e devem falhar
primeiro.

**Organization**: histórias da spec: US1 = turmas (US-07), US2 = matrícula, importação e
transferência (US-08; dividida em três fases), US3 = exclusão e encerramento (US-09).

**Branch**: `feature/feat-03-turmas-e-alunos` (Q-34 do índice). Commits atômicos ao fim de cada
fase, só com os testes passando, mostrando o `git status` antes (CLAUDE.md). Formato:
`feat(feat-03): <imperativo, até 72 caracteres, sem ponto final>`. Não fazer push, merge nem tag.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência de tarefa incompleta)
- **[Story]**: história da spec (US1 a US3)

## Regras para todas as tarefas

- Comentários e docstrings em português; cada classe, função, template e teste indica as US e RBN que
  atende (constituição, princípio II). Cada tarefa termina com `Rastreabilidade:`.
- Mensagens sempre por constantes de `sigtcc/apps/cadastro/mensagens.py` (T004).
- Nenhuma tabela, coluna ou migração de esquema nova (FR-028); a única migração é a carga de dados
  da T003. Nenhum JavaScript do protótipo.
- Regras em `services_turmas.py`, `importacao.py`, `permissoes.py` e `services.py`; views só
  orquestram; templates sem regra. `services_turmas` importa `services`, nunca o contrário (B6, N2).
- Travas (research B17): sempre dentro de `transaction.atomic()`, na ordem turma(s) → aluno → TCC;
  conferir tudo de novo depois de travar.
- Datas: `django.utils.timezone.now()` chamado pelo módulo (o `avancar_relogio` troca
  `django.utils.timezone.now`), sem fuso (`USE_TZ = False`).
- Ordem das conferências em toda rota de turma (B2): turma existe (404) → permissão (403, M-02 da
  spec 003) → turma arquivada (MT-25); rotas `/alunos/<alu_id>/...` exigem o aluno matriculado na
  turma (`vinculo_na_turma`, 404), também no GET.
- Notificações só pelo `services.notificar()` (B21).
- Links de rotas que ainda não existem nos templates: `{% url ... as variavel %}` (mesma solução da
  spec 003), para cada fase poder ser testada sozinha.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: dependências, constantes e carga da equivalência de cursos.

- [X] T001 Instalar no `venv` e fixar no `requirements.txt` as versões exatas (do `pip freeze`) de `openpyxl` e `defusedxml`, com comentário em português "XLSX da importação de alunos (spec 004, Q4; research B9); item de configuração (índice Q-42)". — Rastreabilidade: [US-08][RBN-CAD-05.2][Q4]
- [X] T002 [P] Acrescentar em `sigtcc/apps/cadastro/cargas.py` as constantes `CURSO_ENG_COMPUTACAO`, `CURSO_SIST_INFORMACAO`, `CURSO_LIC_COMPUTACAO` (os mesmos textos de `CURSOS`) e `CURSOS_COM_ORIENTADOR_AUTOMATICO = (CURSO_ENG_COMPUTACAO, CURSO_LIC_COMPUTACAO)`, sem mudar o comportamento das cargas existentes. — Rastreabilidade: [US-07][RBN-CAD-04.2][B8][m12]
- [X] T003 Criar a migração de dados `sigtcc/apps/cadastro/migrations/00NN_carga_equivalencia_cursos.py` (próximo número livre), que carrega em `Equivalencia_Cursos` `EST08MCPD` → "Engenharia de Computação", `EST31MSII` → "Sistemas de Informação" e `EST03MLV` → "Licenciatura em Computação" (curso pelo `cur_nome`), idempotente (`get_or_create`) e reversível por SQL (padrão de `cargas.py`), e o teste `sigtcc/apps/cadastro/tests/test_carga_equivalencia.py` (três códigos, reaplicar não duplica, reverter apaga só esses três). — Rastreabilidade: [US-08][RBN-CAD-05.7][FR-015a][Q5]

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: mensagens, permissões por turma, verificações reutilizáveis, notificações, entregas do
aluno, formulário base, menu e apoio aos testes.

**⚠️ CRITICAL**: nenhuma história começa antes desta fase.

- [X] T004 [P] Acrescentar em `sigtcc/apps/cadastro/mensagens.py` (seção "spec 004"), copiando caractere por caractere: das US — `TURMA_CADASTRADA = "Turma cadastrada com sucesso"`, `HORARIO_TERMINO = "O horário de término deve ser posterior ao de início"`, `TURMA_COM_ALUNOS = "A turma possui alunos matriculados. Use a opção Arquivar"`, `ARQUIVAR_TCC_ATIVO = "Há TCC Em Andamento ou Apto para Defesa"`, `ARQUIVAR_SESSAO_ATIVA = "Há sessão de defesa ativa"`, `ARQUIVAR_VERSAO_FINAL = "A Data Limite da Versão Final ainda não venceu ou não foi cadastrada"`, `ALUNO_MATRICULADO = "Aluno matriculado com sucesso"`, `ALUNO_JA_NA_TURMA = "Aluno já matriculado nesta turma"`, `ARQUIVO_FORA_DO_MODELO = "Arquivo fora do modelo. Baixe o modelo de importação"`, `ALUNO_EXCLUIDO = "Aluno excluído da turma"`, `JUSTIFICATIVA_500 = "Informe uma justificativa de até 500 caracteres"`, `SELECIONE_STATUS = "Selecione o Status do aluno"`, `ALUNO_TEM_PROPOSTA = "O aluno já tem Proposta. Use Encerrar participação"`; reaproveitar `MATRICULA_FORMATO` e `CURSO_NAO_RECONHECIDO` da spec 003; rótulos `NOVA_TURMA = "Nova turma"`, `EDITAR = "Editar"`, `EXCLUIR = "Excluir"`, `ARQUIVAR = "Arquivar"`, `MATRICULAR_ALUNOS = "Matricular alunos"`, `MATRICULA_INDIVIDUAL = "Matrícula individual"`, `IMPORTAR_ARQUIVO = "Importar arquivo (CSV/XLSX)"`, `CONFIRMAR_IMPORTACAO = "Confirmar importação"`, `TRANSFERIR = "Transferir"`, `EXCLUIR_DA_TURMA = "Excluir da turma"`, `ENCERRAR_PARTICIPACAO = "Encerrar participação"`, `CONFIRMAR = "Confirmar"`; e as PROVISÓRIAS `MT01_...` a `MT31_...` (sem a MT-20) com o texto exato da tabela "Mensagens a validar com a PO" da spec, trocando IDENTIFICADOR, NOME, STATUS, TIPO, ORIGEM, DESTINO, CURSO DO ALUNO, CURSO DA TURMA, JUSTIFICATIVA, N, R e C por `{identificador}`, `{nome}`, `{status}`, `{tipo}`, `{origem}`, `{destino}`, `{curso_aluno}`, `{curso_turma}`, `{justificativa}`, `{n}`, `{r}`, `{c}`. — Rastreabilidade: [US-07][US-08][US-09][SC-002][FR-029]
- [X] T005 [P] Acrescentar em `sigtcc/apps/cadastro/services.py`: `curso_do_codigo(codigo) -> Cursos | None` (equivalência pelo código inteiro) e fazer `curso_do_aluno` delegar a ela; `EventoAcesso.TURMA_EXCLUIDA`; `notificar(usuario, mensagem, link=None)` que corta `mensagem` em 500 caracteres com "…" no fim, grava `not_link_tela` só se `destino_da_notificacao(link)` aceitar (senão nulo), `not_data_hora = timezone.now()`, `not_lida = False`; e `montar_mensagem_cortada(modelo, campo_longo, **campos)` que corta primeiro o campo longo (a justificativa) para a frase inteira caber em 500. Testes em `sigtcc/apps/cadastro/tests/test_notificar.py` (limite exato de 500, corte do campo longo, link externo descartado, link interno aceito) e um teste de que `curso_do_aluno` continua igual. — Rastreabilidade: [US-08][US-09][RBN-CAD-05.7][B6][B21][B-1][I-5]
- [X] T006 [P] Acrescentar em `sigtcc/apps/cadastro/permissoes.py`: `pode_consultar_turma(usuario, turma)` (Professor da Disciplina da turma, `tur_doc_id == usuario.pk`, ou Secretaria com `sec_cur_id == tur_cur_id`), `pode_alterar_turma(usuario, turma)` (só o Professor da turma) e `pode_transferir(usuario, turma)` (Professor da turma ou Secretaria do curso), com docstrings que citam a spec Q9 e a regra Q27 da spec 003. — Rastreabilidade: [US-07][US-08][RBN-CAD-04.5][RBN-CAD-05.6][FR-009][Q9][B2]
- [X] T007 Criar `sigtcc/apps/cadastro/tests/apoio_turmas.py` (classe base sobre `TesteAcesso` da spec 003; só usa os modelos, não depende de `services_turmas.py`) com fábricas: `criar_turma_de(professor, descricao, curso_nome, status, ano, semestre, identificador)`, `matricular_aluno(turma, status_tcc=..., com_proposta=...)` (cria aluno, vínculo, TCC e histórico), `criar_defesa(tcc, status)`, `criar_entrega(turma, tipo, data_limite)`, `criar_envio(entrega_do_aluno)`, `criar_solicitacao(tcc, docente, tipo, status)`, `arquivo_csv(linhas, separador=";", codificacao="utf-8")`, `arquivo_xlsx(linhas, planilhas=1)` (com `openpyxl`, em memória); e o acréscimo compatível `criar_secretaria(..., curso=None)` em `sigtcc/apps/cadastro/tests/apoio_acesso.py`. — Rastreabilidade: [infraestrutura de teste da feature 004][B24]
- [X] T008 Criar `sigtcc/apps/cadastro/tests/test_base_turmas.py` (testes da parte comum, escritos antes de T009 e falhando primeiro): `turma_para` na ordem 404 → 403 → MT-25 (docente de fora de turma arquivada recebe 403, não MT-25); Secretaria de outro curso recebe 403; `vinculo_na_turma` com aluno de outra turma → 404; `travar_turma_ativa` levanta `TurmaArquivada`; `turma_ja_teve_aluno` com cada uma das quatro origens; `turma_tem_orientador_automatico` (TCC 2 EC e LC sim; TCC 1 e TCC 2 SI não); `participacao_encerrada`; `criar_entregas_do_aluno` cria e reaproveita registro antigo zerando a avaliação (Q18); `remover_entregas_sem_envio` mantém os com envio (Q17). — Rastreabilidade: [FR-008][FR-009][FR-025][Q9][Q15][Q17][Q18][B2][B5][B22]
- [X] T009 Criar `sigtcc/apps/cadastro/services_turmas.py`, parte comum (research B2, B5, B8, B15, B22): constantes `CONSULTAR`, `ALTERAR`, `TRANSFERIR`, `STATUS_TCC_EM_CURSO`, `STATUS_PARTICIPACAO_ENCERRADA`; exceção `TurmaArquivada`; `turma_arquivada(turma)`; `exigir_turma_ativa(turma)`; `travar_turma_ativa(tur_id)` (`select_for_update`, relê, `TurmaArquivada`); `turma_para(usuario, tur_id, acao, travar=False)` (404 → `PermissionDenied` → `TurmaArquivada` para ALTERAR e TRANSFERIR); `vinculo_na_turma(turma, alu_id)` (404 sem `Alunos_Turmas`); `turma_ja_teve_aluno(turma)` (`Alunos_Turmas`, `TCCs`, `Historico_Status_TCC` ou `Historico_Alunos_Turmas` origem ou destino); `turma_tem_orientador_automatico(turma)` (TCC 2 e curso em `CURSOS_COM_ORIENTADOR_AUTOMATICO`); `participacao_encerrada(tcc)`; reexportar `curso_do_codigo` de `services`; `criar_entregas_do_aluno(aluno, turma)` (cria `Entregas_Marcos` 'Aguardando Envio' para cada `Turmas_Marcos`; se já existir de vínculo anterior, volta a 'Aguardando Envio' com `ent_feedback`, `ent_data_avaliacao` e `ent_correcoes_conferidas_em` vazios, Q18) e `remover_entregas_sem_envio(aluno, turma)` (apaga só os sem `Historico_Envios_Entregas`). — Rastreabilidade: [US-07][US-08][US-09][RBN-CAD-04.2][RBN-CAD-04.5][RBN-CAD-08.5][FR-008][FR-025][Q15][Q17][Q18][I-6][I-7]
- [X] T010 [P] Criar `sigtcc/apps/cadastro/forms_turmas.py` com a base `FormularioSigtcc(forms.Form)` (M-14 para obrigatório, todos os erros por campo, `use_required_attribute = False`) e as funções `normalizar_texto(valor)` (NFC, pontas, espaços repetidos, quebra de linha → espaço) e `validar_justificativa(valor)` (vazia ou só espaços, acima de 500 ou com caractere de controle → `JUSTIFICATIVA_500`). — Rastreabilidade: [US-08][US-09][RBN-CAD-05.4][RBN-CAD-05.6][RBN-CAD-08.4][B18][m9]
- [X] T011 [P] Acrescentar em `sigtcc/apps/cadastro/menu.py` o item `{"rotulo": "Turmas", "icone": "groups", "rota": "cadastro:turmas", "perfis": ("docente", "secretaria"), "ordem": 10}` (o processador de contexto da spec 003 esconde o item enquanto a rota não existir) e criar `sigtcc/apps/cadastro/views_turmas.py` vazio com a docstring do módulo. — Rastreabilidade: [US-07][FR-010][Q9]
- [X] T012 Rodar `python manage.py test sigtcc.apps.cadastro.tests.test_base_turmas sigtcc.apps.cadastro.tests.test_notificar sigtcc.apps.cadastro.tests.test_carga_equivalencia` até passar, e a suíte inteira (features 001 e 003). — Rastreabilidade: [SC-001]

**Checkpoint**: base pronta; as histórias podem começar.

---

## Phase 3: User Story 1 - Cadastrar e manter turmas de TCC [US-07] (Priority: P1) 🎯 MVP

**Goal**: o Docente cadastra, edita, exclui (se nunca teve aluno) e arquiva turmas; a Secretaria
consulta as turmas do seu curso.

**Independent Test**: cadastrar uma turma de TCC 1, editá-la, excluí-la; cadastrar outra e arquivá-la
com as condições atendidas (alunos e TCCs criados pelas fábricas).

### Tests for User Story 1 ⚠️

- [X] T013 [US1] Criar `sigtcc/apps/cadastro/tests/test_us07_turmas.py` com `test_cenario1` a `test_cenario13` da US-07, exceto o 7, que depende da matrícula e fica em T018 (`test_us07_cenario7_orientador_automatico`); o 10 com `avancar_relogio`; mais `test_mt01_codigo_disciplina`, `test_mt02_identificador_formato`, `test_mt04_ano_comeca_com_zero` ("0123" recusado, m1), `test_mt05_local_com_controle_ou_so_espacos`, `test_m14_obrigatorios`, `test_identificador_concorrente_vira_mt03` (`IntegrityError` → MT-03, m3), `test_q12_turma_que_ja_teve_aluno_nao_exclui`, `test_exclusao_apaga_turmas_marcos`, `test_exclusao_registra_log_depois_do_commit` (`assertLogs`, `captureOnCommitCallbacks`, detalhe com `tur_id` e identificador, m4), `test_q15_trava_descricao_e_curso_depois_que_alunos_sairam`, `test_arquivamento_tcc1_sem_versao_final`, `test_arquivamento_ordem_dos_motivos`, `test_turma_arquivada_some_da_lista_e_vai_para_arquivadas`, `test_mt25_acao_em_turma_arquivada_pelo_endereco`, `test_secretaria_consulta_turmas_do_curso` (ativas e arquivadas, sem botões de ação), `test_outro_docente_e_coordenador_recebem_403` (Q9), `test_disciplina_criada_e_reaproveitada`. — Rastreabilidade: [US-07][RBN-CAD-04.1][RBN-CAD-04.2][RBN-CAD-04.3][RBN-CAD-04.4][RBN-CAD-04.5][FR-001]-[FR-010][Q9][Q12][Q15]

### Implementation for User Story 1

- [X] T014 [US1] Acrescentar em `sigtcc/apps/cadastro/services_turmas.py` (research B3 a B5): `criar_turma(docente, dados)` (Disciplinas por `get_or_create(dis_codigo=...)`, `tur_doc` = docente, 'Ativa', `IntegrityError` de identificador → erro MT-03); `editar_turma(professor, tur_id, dados)` (turma travada; com `turma_ja_teve_aluno`, ignora Descrição e Curso); `excluir_turma(professor, tur_id)` (turma travada; `turma_ja_teve_aluno` → `TURMA_COM_ALUNOS`; apaga `Turmas_Marcos` e a turma; `registrar_evento(TURMA_EXCLUIDA, ...)` por `transaction.on_commit`); `arquivar_turma(professor, tur_id)` (turma travada; motivos na ordem TCC em curso → sessão ativa → Versão Final em TCC 2; sucesso 'Arquivada'). — Rastreabilidade: [US-07][RBN-CAD-04.1][RBN-CAD-04.2][RBN-CAD-04.3][RBN-CAD-04.4][RBN-CAD-04.5][FR-001]-[FR-008][Q12][Q15]
- [X] T015 [US1] Acrescentar em `sigtcc/apps/cadastro/forms_turmas.py` o `TurmaForm(FormularioSigtcc)`: Código da Disciplina `^[A-Z0-9]{1,20}$` (MT-01); Descrição (lista TCC 1/TCC 2); Identificador `^[A-Z0-9_]{1,30}$` (MT-02) e único (MT-03); Ano `^[1-9]\d{3}$` (MT-04); Semestre (lista 1/2); Dia da Semana (lista `DiaSemana`); Horário de Início e de Término `HH:MM` (término > início, `HORARIO_TERMINO`); Local até 100, normalizado (MT-05); Curso (lista dos 3 cursos); parâmetro `travar_descricao_e_curso` que deixa os dois `disabled`. — Rastreabilidade: [US-07][RBN-CAD-04.1][RBN-CAD-04.3][FR-001][FR-002][FR-005]
- [X] T016 [US1] Criar em `sigtcc/apps/cadastro/views_turmas.py` as views `turmas`, `turmas_arquivadas` (`@perfil_requerido("docente", "secretaria")`: Docente vê as turmas de que é Professor; Secretaria as do seu curso), `turma_nova` (`@perfil_requerido("docente")`), `turma` (`turma_para(..., CONSULTAR)`; mostra dados, alunos com Matrícula, Nome Completo, Curso e Status do TCC, e só as ações permitidas), `turma_editar`, `turma_excluir` e `turma_arquivar` (GET confirmação MT-07/MT-09, POST executa; `TurmaArquivada` → `messages` MT-25 e volta para a turma); os templates `sigtcc/templates/cadastro/turmas/lista.html`, `arquivadas.html`, `turma.html` (links das fases seguintes com `{% url ... as %}`), `form_turma.html` e `confirmar.html`, com a base visual da spec 003 e o visual das telas "Gerenciar turmas de TCC" do protótipo; e as rotas `turmas`, `turmas_arquivadas`, `turma_nova`, `turma`, `turma_editar`, `turma_excluir`, `turma_arquivar` em `sigtcc/apps/cadastro/urls.py` (contracts/rotas.md). — Rastreabilidade: [US-07][RBN-CAD-04.1]-[RBN-CAD-04.5][FR-001]-[FR-010][FR-027][Q9]
- [X] T017 [US1] Rodar `python manage.py test sigtcc.apps.cadastro.tests.test_us07_turmas` até passar, e a suíte inteira. — Rastreabilidade: [US-07][SC-001]

**Checkpoint**: turmas completas (MVP).

---

## Phase 4: User Story 2 - Matrícula individual e edição do aluno [US-08] (Priority: P1)

**Goal**: o Professor matricula um aluno por vez (aluno novo ou já cadastrado) e corrige nome e
curso.

**Independent Test**: matricular aluno novo, aluno já cadastrado (TCC 1 aprovado e reprovado), tentar
os casos recusados e editar o nome.

### Tests for User Story 2 (matrícula individual) ⚠️

- [ ] T018 [US2] Criar `sigtcc/apps/cadastro/tests/test_us08_matricula.py` com `test_cenario1`, `test_cenario2`, `test_cenario3`, `test_cenario9`, `test_cenario10`, `test_cenario11` e `test_cenario13` da US-08; o `test_us07_cenario7_orientador_automatico` (TCC 2 de LC; e TCC 2 de SI e TCC 1 sem orientador automático); mais `test_conta_nova_sem_email_sem_senha_sem_link` (nenhum e-mail enviado; spec 003, Q1), `test_tcc_sem_proposta_e_historico_vinculo` (gatilho 'Vínculo à turma', `hst_usu` = professor), `test_q7_tcc_em_curso_noutra_turma` (MT-26 com o identificador), `test_q7_tcc_em_turma_arquivada_permite`, `test_q7_qualquer_tcc_aprovado_ou_concluido` (MT-27, m5), `test_mt28_aprovado_tcc2_em_turma_tcc1`, `test_q6_copia_do_tcc1` (TCC novo direto 'Em Andamento', campos copiados, palavras-chave, `Artigos` com todas as colunas, histórico 'Transferência para TCC 2', orientação do TCC 1 encerrada, coorientadores copiados exceto o professor da turma, TCC 1 intacto), `test_q6_copia_em_tcc2_de_si_mantem_orientador`, `test_q16_conta_inativa_matriculada_com_aviso_mt29`, `test_curso_reconhecido_e_nao_reconhecido`, `test_alerta_mt13_curso_divergente`, `test_mt11_nome_com_letra_nao_latina_ou_simbolo` (grego, `×`, `ª`; NFD normalizado aceito, N6), `test_mt12_curso_formato`, `test_q17_cria_registros_das_entregas`, `test_q18_rematricula_reaproveita_registro_zerado`, `test_aluno_existente_mantem_nome_e_curso`, `test_editar_aluno_de_outra_turma_404` (I-7) e `test_matricula_concorrente_vira_aluno_existente` (`IntegrityError` em `alu_matricula`, m7). — Rastreabilidade: [US-08][RBN-CAD-05.1][RBN-CAD-05.3][RBN-CAD-05.5][RBN-CAD-05.7][RBN-CAD-04.2][RBN-CAD-08.6][FR-004][FR-011]-[FR-015][FR-019][Q6][Q7][Q16][Q17][Q18]

### Implementation for User Story 2 (matrícula individual)

- [ ] T019 [US2] Acrescentar em `sigtcc/apps/cadastro/services_turmas.py` (research B6 a B8, B12): `ResultadoMatricula` (estado em `CRIADO`, `VINCULADO`, `COPIADO`, `JA_NA_TURMA`, `TCC_EM_CURSO`, `TCC_CONCLUIDO`, `APROVADO_EM_TURMA_TCC1`, mais `avisos`: MT-13, MT-29, "Código não reconhecido"); `matricular(professor, turma, matricula, nome, codigo_curso)` na ordem do B6 (turma já travada por quem chama; aluno existente travado; aluno novo num savepoint com nova tentativa em `IntegrityError`; conta nova por `Usuarios.objects.create_user(None, nome, usu_status='Aguardando Ativação')`; vínculo, TCC 'Sem Proposta', histórico, orientação automática, `criar_entregas_do_aluno`); `_copiar_tcc_aprovado(professor, turma, aluno, tcc1)` na ordem do B7; `editar_aluno(professor, tur_id, alu_id, nome, codigo_curso)` (turma travada, `vinculo_na_turma`). A recusa `APROVADO_EM_TURMA_TCC1` (MT-28) é comportamento PROVISÓRIO até a resposta da Q-39 do índice; se a resposta for outra, a mudança começa pela spec e por este teste. — Rastreabilidade: [US-08][RBN-CAD-05.1][RBN-CAD-05.3][RBN-CAD-05.5][RBN-CAD-05.7][RBN-CAD-04.2][RBN-CAD-08.6][FR-011]-[FR-015][FR-019][Q6][Q7][Q16]
- [ ] T020 [US2] Acrescentar em `sigtcc/apps/cadastro/forms_turmas.py` o `MatriculaForm` (Matrícula `^\d{10}$` com `MATRICULA_FORMATO`; Nome Completo normalizado em NFC, só letras latinas — `str.isalpha()` e `unicodedata.name(c).startswith("LATIN")` — e espaços, até 150, MT-11; Curso `^[A-Z0-9]{1,20}$`, MT-12, com `<datalist>` dos códigos da equivalência e o nome do curso) e o `EditarAlunoForm` (Nome Completo e Curso; Matrícula só leitura). Exportar a validação de linha (`validar_dados_do_aluno(matricula, nome, curso) -> list[str]`) para a importação reaproveitar. — Rastreabilidade: [US-08][RBN-CAD-05.1][RBN-CAD-05.3][FR-011][FR-019][N6]
- [ ] T021 [US2] Criar em `sigtcc/apps/cadastro/views_turmas.py` as views `matricular` (GET com as duas opções e o formulário individual; POST chama `matricular` com a turma travada por `turma_para(..., ALTERAR, travar=True)` e mostra `ALUNO_MATRICULADO` e os avisos) e `aluno_editar` (MT-14); os templates `sigtcc/templates/cadastro/turmas/matricular.html` e `editar_aluno.html` (tela "Matricular alunos na turma" do protótipo); e as rotas `matricular` e `aluno_editar`. — Rastreabilidade: [US-08][RBN-CAD-05.1][RBN-CAD-05.3][FR-011][FR-019]
- [ ] T022 [US2] Rodar `python manage.py test sigtcc.apps.cadastro.tests.test_us08_matricula sigtcc.apps.cadastro.tests.test_us07_turmas` até passar. — Rastreabilidade: [US-08][SC-001][SC-005]

---

## Phase 5: User Story 2 - Importação por CSV ou XLSX [US-08] (Priority: P1)

**Goal**: o Professor importa até 200 alunos por arquivo, com prévia presa à turma e confirmação,
conforme o diagrama "Matrícula por CSV".

**Independent Test**: importar um CSV com linhas válidas e inválidas, um CSV do Excel em português e
um XLSX; recusar PDF, arquivo grande, arquivo com 201 linhas e XLSX malicioso.

### Tests for User Story 2 (importação) ⚠️

- [ ] T023 [US2] Criar `sigtcc/apps/cadastro/tests/test_us08_importacao.py` com `test_cenario4`, `test_cenario5`, `test_cenario7`, `test_cenario8` e `test_cenario14` da US-08; mais `test_q11_csv_ponto_e_virgula_e_virgula`, `test_q11_utf8_bom_e_windows1252_com_acentos`, `test_q11_xlsx_so_primeira_planilha`, `test_xlsx_matricula_numerica_sem_ponto_zero`, `test_cabecalhos_em_outra_ordem_e_maiusculas`, `test_cabecalho_faltando_fora_do_modelo`, `test_q13_201_linhas_fora_do_modelo` (e 200 linhas aceitas), `test_zip_bomb_fora_do_modelo` (soma descompactada acima de 20 MB e razão acima de 100), `test_defusedxml_em_uso` (`openpyxl.xml.DEFUSEDXML is True`, N7), `test_arquivo_corrompido_fora_do_modelo` (CSV binário, XLSX com bytes de ZIP inválido), `test_previa_sem_gravar_nada`, `test_previa_classifica_como_o_diagrama` (inválida, já matriculada, já cadastrada, nova, MT-26/27/28, MT-29, alerta), `test_matricula_repetida_no_arquivo`, `test_b2_confirmar_com_token_de_outra_turma_recusa` (duas turmas, duas abas), `test_b2_confirmar_sem_previa_ou_vencida` (31 minutos), `test_n3_segundo_post_nao_grava_nem_troca_resumo`, `test_f5_no_resumo_nao_repete` (PRG), `test_n4_abrir_outra_turma_nao_apaga_previa`, `test_cancelar_apaga_previa`, `test_previa_guarda_so_o_minimo` (linhas com erro só com número e motivo, I-10), `test_q2_linha_que_falha_na_confirmacao_nao_desfaz_outras`, `test_resumo_mt15_com_contagens`, `test_modelo_importacao_csv_utf8_bom_ponto_e_virgula` e `test_sc003_60_linhas_em_ate_10_segundos` (com margem). — Rastreabilidade: [US-08][RBN-CAD-05.2][RBN-CAD-05.5][RBN-CAD-05.7][FR-016]-[FR-018][SC-003][Q2][Q4][Q11][Q13][B-2][B-3][N3][N4][N7]

### Implementation for User Story 2 (importação)

- [ ] T024 [US2] Criar `sigtcc/apps/cadastro/importacao.py` (research B9 a B11): `ErroModelo`; `ler_arquivo(arquivo)` (2 MB; extensão `.csv`/`.xlsx`; XLSX pelos bytes `PK\x03\x04`, `zipfile` com soma de `file_size` até 20 MB e razão até 100, `openpyxl.load_workbook(read_only=True, data_only=True)`, primeira planilha, `wb.close()` em `finally`; CSV em `utf-8-sig` ou `cp1252`, separador por `csv.Sniffer(delimiters=";,")` no cabeçalho; até 200 linhas não vazias; cabeçalhos normalizados; exceções listadas no B9 → `ErroModelo`); `montar_previa(turma, linhas)` (classificação do diagrama usando `validar_dados_do_aluno` e a mesma lógica de recusa do `matricular`, sem gravar); `gerar_modelo_csv()` (UTF-8 com BOM, ";", cabeçalho e uma linha de exemplo). — Rastreabilidade: [US-08][RBN-CAD-05.2][RBN-CAD-05.7][FR-016][FR-017][Q2][Q4][Q11][Q13][B-3]
- [ ] T025 [US2] Acrescentar em `sigtcc/apps/cadastro/services_turmas.py` `confirmar_importacao(professor, tur_id, token, sessao)`: confere prévia, `token`, `tur_id` e prazo de 30 minutos; tira a prévia da sessão; marca o token com `caches["default"].add(f"importacao:{token}", 1, 3600)` (já marcado → recusa; o cache padrão em arquivo pode descartar entradas acima de 300, mas a marca só precisa durar os segundos de dois POST simultâneos, research B10); trava a turma e os alunos já cadastrados em ordem de matrícula; chama `matricular` linha a linha, cada uma num savepoint; devolve o resumo (matriculados, rejeitadas com número e motivo, códigos não reconhecidos). — Rastreabilidade: [US-08][RBN-CAD-05.2][FR-018][Q2][B-2][N3][m8]
- [ ] T026 [US2] Acrescentar em `sigtcc/apps/cadastro/forms_turmas.py` o `ImportacaoForm` (um `FileField`) e criar em `sigtcc/apps/cadastro/views_turmas.py` as views `importar` (GET formulário; POST lê, monta a prévia, grava na sessão `token`, `tur_id`, instante ISO e o mínimo; mostra `previa.html` com o `token` oculto), `importar_confirmar` (POST; chama o serviço; guarda o resumo pequeno na sessão e redireciona), `importar_resumo` (GET; MT-15), `importar_cancelar` (POST) e `modelo_importacao` (GET, `text/csv`, `Content-Disposition` com `modelo_importacao_alunos.csv`); os templates `sigtcc/templates/cadastro/turmas/importar.html`, `previa.html` e `resumo.html`; e as rotas `importar`, `importar_confirmar`, `importar_resumo`, `importar_cancelar` e `modelo_importacao`. — Rastreabilidade: [US-08][RBN-CAD-05.2][FR-016]-[FR-018][B10][B11]
- [ ] T027 [US2] Rodar `python manage.py test sigtcc.apps.cadastro.tests.test_us08_importacao sigtcc.apps.cadastro.tests.test_us08_matricula` até passar. — Rastreabilidade: [US-08][SC-001][SC-003]

---

## Phase 6: User Story 2 - Transferência entre turmas de TCC 2 [US-08] (Priority: P1)

**Goal**: o Professor da turma de origem ou a Secretaria do curso transfere o aluno para a turma de
TCC 2 de outro orientador.

**Independent Test**: transferir um aluno com TCC 'Em Andamento' entre duas turmas de TCC 2 de
Engenharia de Computação do mesmo período e conferir orientação, entregas, histórico e notificações.

### Tests for User Story 2 (transferência) ⚠️

- [ ] T028 [US2] Criar `sigtcc/apps/cadastro/tests/test_us08_transferencia.py` com `test_cenario6` e `test_cenario12` da US-08; mais `test_mt17_tcc_fora_de_em_andamento_ou_apto`, `test_mt18_sessao_reagendada_e_em_andamento`, `test_mt19_sem_destino_possivel`, `test_i1_destino_onde_o_aluno_ja_tem_vinculo_ou_tcc_some_da_lista`, `test_destinos_so_tcc2_mesmo_curso_e_periodo_ativa_outro_professor`, `test_so_em_turma_com_orientador_automatico` (TCC 2 de SI não oferece "Transferir"), `test_justificativa_vazia_e_501`, `test_secretaria_do_curso_transfere`, `test_secretaria_de_outro_curso_403`, `test_orientacao_antiga_encerrada_antes_da_nova`, `test_coorientacao_do_professor_destino_encerrada`, `test_m11_convite_de_coorientacao_pendente_cancelado`, `test_q17_entregas_origem_sem_envio_apagadas_com_envio_mantidas`, `test_q17_entregas_do_destino_criadas`, `test_historico_transferencia_e_lista_da_origem`, `test_notificacoes_mt22_aluno_e_dois_orientadores` (link só para o novo orientador), `test_mesmo_tcc_com_status_e_historico_na_nova_turma` e `test_aluno_de_outra_turma_404`. — Rastreabilidade: [US-08][RBN-CAD-05.6][RBN-CAD-04.2][FR-020]-[FR-022][Q9][Q17][I-1][m6][m11]

### Implementation for User Story 2 (transferência)

- [ ] T029 [US2] Acrescentar em `sigtcc/apps/cadastro/services_turmas.py` `turmas_destino_possiveis(turma_origem, aluno)` e `transferir(autor, tur_origem_id, alu_id, tur_destino_id, justificativa)` como no research B13 (travas das duas turmas em ordem de `tur_id`, depois o TCC; motivos MT-17, MT-18, MT-19; efeitos na ordem do B13; notificações MT-22 por `notificar()`). — Rastreabilidade: [US-08][RBN-CAD-05.6][FR-020]-[FR-022][Q17][I-1][m6][m11]
- [ ] T030 [US2] Acrescentar em `sigtcc/apps/cadastro/forms_turmas.py` o `TransferenciaForm` (Turma de Destino, lista de `turmas_destino_possiveis`; Justificativa com `validar_justificativa`) e criar em `sigtcc/apps/cadastro/views_turmas.py` a view `aluno_transferir` (`turma_para(..., TRANSFERIR)`, `vinculo_na_turma`; MT-16), o template `sigtcc/templates/cadastro/turmas/transferir.html` e a rota `aluno_transferir`. — Rastreabilidade: [US-08][RBN-CAD-05.6][FR-020]-[FR-022]
- [ ] T031 [US2] Rodar `python manage.py test sigtcc.apps.cadastro.tests.test_us08_transferencia` até passar, e de novo as fases 3 a 5. — Rastreabilidade: [US-08][SC-001]

**Checkpoint**: US-08 completa.

---

## Phase 7: User Story 3 - Excluir aluno ou encerrar a participação [US-09] (Priority: P2)

**Goal**: o Professor exclui o aluno sem Proposta, encerra a participação do aluno com Proposta e
consulta a lista de excluídos ou transferidos.

**Independent Test**: excluir um aluno sem Proposta (com e sem entrega enviada), tentar excluir um
com Proposta, encerrar um com TCC 'Em Andamento' e abrir a lista.

### Tests for User Story 3 ⚠️

- [ ] T032 [US3] Criar `sigtcc/apps/cadastro/tests/test_us09_exclusao.py` com `test_cenario1` a `test_cenario11` da US-09 (7 e 8 pela `participacao_encerrada`, porque os botões são das features de TCC, Orientação e Entregas); mais `test_q8_exclusao_apaga_tcc_historico_e_orientacao_automatica`, `test_exclusao_recusada_com_solicitacao_encontro_coorientacao_palavra_publicacao_ou_defesa`, `test_q17_exclusao_mantem_entregas_com_envio_e_apaga_sem_envio` (não recusa), `test_b1_notificacao_mt21_com_justificativa_500_e_identificador_30` (cabe em 500, termina com "…"), `test_confirmacao_final_mt24_com_justificativa_oculta`, `test_q10_encerramento_encerra_orientacao_e_coorientacao`, `test_q14_encerramento_recusado_com_sessao_ativa_mt30` (Agendada, Reagendada, Em Andamento), `test_q14_q19_pedidos_e_convites_pendentes_cancelados_e_notificados` (`sol_data_resposta` = data do cancelamento; MT-31 para cada docente), `test_encerramento_so_em_andamento_ou_apto`, `test_encerramento_concorrente_com_transferencia` (o segundo encontra o estado novo e recusa), `test_historico_encerramento_com_professor_e_gatilho`, `test_lista_excluidos_transferidos_so_professor` (Secretaria 403, I-4), `test_lista_mais_recente_primeiro_com_destino` e `test_aluno_de_outra_turma_404`. — Rastreabilidade: [US-09][RBN-CAD-05.4][RBN-CAD-05.8][RBN-CAD-08.4][RBN-CAD-08.5][RBN-CAD-08.7][FR-023]-[FR-026][Q8][Q10][Q14][Q17][Q19][B-1][I-2][I-4]

### Implementation for User Story 3

- [ ] T033 [US3] Acrescentar em `sigtcc/apps/cadastro/services_turmas.py` `excluir_aluno(professor, tur_id, alu_id, justificativa)` (research B14), `encerrar_participacao(professor, tur_id, alu_id, status, justificativa)` (research B15, com MT-31 por `notificar()`) e `excluidos_e_transferidos(turma)` (research B16). — Rastreabilidade: [US-09][RBN-CAD-05.4][RBN-CAD-05.8][RBN-CAD-08.4][FR-023][FR-024][FR-026][Q8][Q10][Q14][Q17][Q19]
- [ ] T034 [US3] Acrescentar em `sigtcc/apps/cadastro/forms_turmas.py` o `ExclusaoAlunoForm` (Justificativa) e o `EncerramentoForm` (Status: lista Desistente, Reprovado, Jubilado, com `SELECIONE_STATUS`; Justificativa) e criar em `sigtcc/apps/cadastro/views_turmas.py` as views `aluno_excluir` (etapa 1 justificativa e "Confirmar"; etapa 2 MT-24 com a justificativa oculta, "Confirmar" e "Cancelar"; sucesso `ALUNO_EXCLUIDO`), `aluno_encerrar` (MT-23 ou MT-30) e `excluidos_transferidos` (só o Professor); os templates `sigtcc/templates/cadastro/turmas/excluir_aluno.html`, `encerrar.html` e `excluidos_transferidos.html` (tela "Excluir aluno da turma" do protótipo); e as rotas `aluno_excluir`, `aluno_encerrar` e `excluidos_transferidos`. — Rastreabilidade: [US-09][RBN-CAD-05.4][RBN-CAD-05.8][RBN-CAD-08.4][FR-023][FR-024][FR-026]
- [ ] T035 [US3] Rodar `python manage.py test sigtcc.apps.cadastro.tests.test_us09_exclusao` até passar, e a suíte do app inteira. — Rastreabilidade: [US-09][SC-001][SC-006]

**Checkpoint**: as três histórias completas.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: permissões de todas as rotas, mensagens exatas, qualidade, roteiro manual e PR.

- [ ] T036 [P] Criar `sigtcc/apps/cadastro/tests/test_permissoes_turmas.py` (SC-004): para cada rota de `contracts/rotas.md`, (a) sem login → login com `next`; (b) docente de outra turma e Coordenador de Curso sem a turma → 403 com M-02; (c) Secretaria de outro curso → 403; (d) Secretaria do curso → só `turmas`, `turmas_arquivadas`, `turma` e `aluno_transferir`; (e) turma arquivada → MT-25 nas ações (e 403 antes da MT-25 para quem não tem permissão); (f) `alu_id` de aluno de outra turma → 404; (g) ações só por POST. — Rastreabilidade: [SC-004][FR-008][FR-009][Q9][I-7]
- [ ] T037 [P] Criar `sigtcc/apps/cadastro/tests/test_mensagens_turmas.py` (SC-002): constantes das US-07, 08 e 09 conferidas entre aspas em `docs/fonte/Historias_de_Usuario_v3_2.md` (normalizando as quebras de citação, como em `test_mensagens.py` da spec 003); MT-01 a MT-31 (sem a MT-20) conferidas contra a tabela da spec 004, trocando os campos (`{identificador}` ↔ IDENTIFICADOR etc.). — Rastreabilidade: [SC-002][FR-029]
- [ ] T038 [P] Criar `sigtcc/apps/cadastro/tests/test_seguranca_turmas.py`: SC-006 (exclusão de turma no log; exclusão, transferência e encerramento com autor, data e hora); SC-005 (nenhuma matrícula duplicada na mesma turma nem segunda conta, na matrícula e na importação, inclusive em duas importações simultâneas do mesmo aluno); upload acima de 2 MB recusado; nenhum valor de célula do arquivo entra em log. — Rastreabilidade: [SC-005][SC-006][B-3]
- [ ] T039 Rodar o script de rastreabilidade (o mesmo da spec 003, em `sigtcc/apps/cadastro/{services_turmas,importacao,forms_turmas,views_turmas,permissoes,services}.py`, nos testes novos e em `sigtcc/templates/cadastro/turmas/`) e acrescentar as marcações que faltarem. — Rastreabilidade: [constituição, princípio II]
- [ ] T040 Rodar `lint.bat` (ou isort, black e flake8) duas vezes: a segunda não altera nada e o flake8 termina sem erros em `sigtcc/`. — Rastreabilidade: [infraestrutura da feature 004]
- [ ] T041 Rodar `python manage.py test sigtcc.apps` em banco de teste novo e `python manage.py makemigrations --check --dry-run` (só a carga da T003, nenhuma mudança de esquema). — Rastreabilidade: [SC-001][FR-028]
- [ ] T042 Executar o roteiro de `specs/004-turmas-alunos/quickstart.md` (seções 1 a 4), cronometrar o SC-007, importar uma exportação real do sistema acadêmico da UEA (confere o limite de compressão do XLSX, N7) e fazer a revisão visual em 360, 768 e 1280 px; corrigir o quickstart se algo diferir. Tarefa da responsável (Julia Cohen). — Rastreabilidade: [SC-003][SC-007][FR-027][N7]
- [ ] T043 Atualizar `CHANGELOG.md` com a entrega da feature 004 e as pendências abertas (Q-34, Q-36, Q-39 a Q-42) e preparar `specs/004-turmas-alunos/pr-feat-03.md` com o template do PGCS 6.3, título `[Feat-03] Turmas e Alunos (US-07, US-08, US-09)`, usando o agente `revisor-pgcs`; listar os itens de configuração da Q-42 para o Célio, inclusive o limite de upload no servidor web (cerca de 2,5 MB, research B23), que não tem tarefa de código. Não fazer push nem abrir o PR sem pedido da responsável. — Rastreabilidade: [infraestrutura da feature 004]

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 e T002 [P] em paralelo; T003 depois de T001.
- **Foundational (Phase 2)**: depende do Setup; bloqueia as histórias. T004, T005, T006, T010 e T011
  em paralelo; T007 (fábricas) depois do Setup; T008 (testes) depende de T007; T009 (serviços
  comuns) depende de T005, T006 e T008; T012 por
  último.
- **US1 (Phase 3)**: depende da Foundational. MVP.
- **US2 matrícula (Phase 4)**: depende da US1 (turma criada e rota `turma`).
- **US2 importação (Phase 5)**: depende da Phase 4 (`matricular` e a validação de linha).
- **US2 transferência (Phase 6)**: depende da Phase 4 (vínculo, TCC e orientação automática) e vem
  antes da US3.
- **US3 (Phase 7)**: depende da Phase 6 (o `test_encerramento_concorrente_com_transferencia` usa o
  serviço de transferência, e a lista de excluídos ou transferidos mostra transferências reais).
- **Polish (Phase 8)**: depende de todas.

### Within Each Phase

- Testes escritos antes e falhando; depois serviço, formulário, view, template e rota; por fim rodar.
- `services_turmas.py`, `forms_turmas.py`, `views_turmas.py` e `urls.py` são compartilhados: as
  tarefas de implementação das fases são sequenciais entre si.
- Commit ao fim de cada fase, só com os testes da fase e das anteriores passando.

### Parallel Opportunities

- Setup: T002 ao lado de T001.
- Foundational: T004, T005, T006, T010 e T011.
- Polish: T036, T037 e T038.

---

## Parallel Example: Foundational

```bash
Task: "T004 mensagens.py (spec 004)"
Task: "T005 services.py: curso_do_codigo, notificar, TURMA_EXCLUIDA"
Task: "T006 permissoes.py: regras por turma"
Task: "T010 forms_turmas.py: base e normalização"
Task: "T011 menu.py e views_turmas.py"
```

## Parallel Example: Polish

```bash
Task: "T036 test_permissoes_turmas.py"
Task: "T037 test_mensagens_turmas.py"
Task: "T038 test_seguranca_turmas.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Fases 1 e 2 (dependências, carga, base).
2. Fase 3 (US1): turmas completas.
3. **Parar e validar**: `test_us07_turmas` verde; itens a, b, l, m, n e o do quickstart.

### Incremental Delivery

1. Setup + Foundational → `chore(feat-03): preparar base de turmas e carga de cursos` e
   `feat(feat-03): adicionar permissoes por turma e servicos compartilhados`.
2. US1 → `feat(feat-03): cadastrar, editar, excluir e arquivar turmas`.
3. US2 matrícula → `feat(feat-03): matricular aluno e editar dados do aluno`.
4. US2 importação → `feat(feat-03): importar alunos por csv e xlsx com previa`.
5. US2 transferência → `feat(feat-03): transferir aluno entre turmas de tcc 2`.
6. US3 → `feat(feat-03): excluir aluno e encerrar participacao`.
7. Polish → `test(feat-03): ...` e `docs(feat-03): ...`.

---

## Notes

- [P] = arquivos diferentes, sem dependência de tarefa incompleta.
- As 30 mensagens provisórias (MT) não bloqueiam as tarefas (como na spec 003, Q25); quando a PO
  validar (Q-36), trocar só as constantes e a tabela da spec.
- A MT-28 depende da Q-39 (Julia); se a resposta mudar o comportamento, começa pela spec.
- Pendências fora desta feature: [plan.md](plan.md) ("Pendências") e o índice
  [docs/questoes-a-rever.md](../../docs/questoes-a-rever.md).
