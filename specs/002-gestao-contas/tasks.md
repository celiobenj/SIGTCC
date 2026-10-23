# Tasks: Gestão de Contas do SIGTCC

**Input**: Design documents from `specs/002-gestao-contas/`

**Prerequisites**: [plan.md](plan.md) (aprovado em 2026-10-22, depois da revisão do
`arquiteto-django`), [spec.md](spec.md) (aprovada em 2026-10-22; Clarifications Q1 a Q35),
[research.md](research.md) (C1 a C24), [data-model.md](data-model.md),
[contracts/rotas.md](contracts/rotas.md),
[contracts/servicos-compartilhados.md](contracts/servicos-compartilhados.md),
[quickstart.md](quickstart.md)

**Aprovação**: tasks aprovado por Maria Luiza Guimarães (responsável pela implementação) em
2026-10-22.

**Tests**: obrigatórios (constituição, princípio VI): cada cenário Dado/Quando/Então das US-03 (40),
US-04 (25), US-05 (23), US-06 (18), US-50 (9) e os 4 do comando vira pelo menos um teste, mais
permissões, curso, concorrência, contrato e mensagens exatas. Os testes de cada fase vêm antes da
implementação e devem falhar primeiro.

**Organization**: histórias da spec: US1 = docentes e Secretaria (US-03), US2 = membros externos
(US-05), US3 = inativar e reativar (US-04), US4 = validade e expiração (US-06), US5 = prorrogação
(US-50), US6 = Coordenadores iniciais (comando). A troca de e-mail pelo gestor (US-03 A11, US-05 A3)
tem fase própria, com as etiquetas US1 e US2.

**Branch**: `feature/feat-04-gestao-de-contas`. Commits atômicos ao fim de cada fase, só com os testes
da fase e das anteriores passando, mostrando o `git status` antes (CLAUDE.md). Formato:
`feat(feat-04): <imperativo, até 72 caracteres, sem ponto final>`. Não fazer push, merge nem tag.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência de tarefa incompleta)
- **[Story]**: história da spec (US1 a US6)

## Regras para todas as tarefas

- Comentários e docstrings em português; cada classe, função, template e teste indica as US e RBN que
  atende (constituição, princípio II). Cada tarefa termina com `Rastreabilidade:`.
- Mensagens sempre por constantes de `sigtcc/apps/cadastro/mensagens.py` (T001); nunca texto solto.
- Nenhuma tabela nova; a única coluna e a única migração são as da T013 (Q-69, spec Q36), com o
  dicionário atualizado no mesmo commit (princípio III). Nenhum JavaScript do protótipo.
- Regras em `services_contas.py`, `permissoes.py` e `services.py`; views só orquestram; templates sem
  regra. Direção das importações (research C3): `views_contas` → `services_contas` → `services` →
  `permissoes` → `models`; `services_contas` → `sigtcc.apps.defesa.models`; `permissoes.py` nunca
  importa `defesa`.
- Travas (research C19): sempre dentro de `transaction.atomic()`, na ordem `Usuarios` (id crescente,
  `select_for_update(of=("self",))`) → especialização (`Docentes`, `Secretarios`, `MembrosExternos`)
  → `Cursos` (id crescente) → trava consultiva do e-mail (`services.travar_email`). Depois de travar,
  reler tudo o que decide a regra (status, curso atual, vínculos, validade).
- Gravação (research C20): formulários de conta são `forms.Form`, nunca `ModelForm`; o serviço grava
  com `update_fields` explícito; `usu_email` só muda na criação e em `confirmar_troca_email`;
  `usu_status` só nas ações próprias; a senha nunca é tocada.
- Ordem das conferências nas rotas com id (research C22, C11): registro pela especialização
  (`get_object_or_404`, 404 para id de outro tipo de conta) → perfil (403, M-02) → curso
  (`ForaDoCurso`, 403 com a mensagem do FR-009) → status (MC-09, MC-10). Toda ação que grava
  redireciona depois do POST (PRG).
- Datas: `django.utils.timezone.now()` chamado pelo módulo (o `avancar_relogio` troca
  `django.utils.timezone.now`), sem fuso (`USE_TZ = False`); validade vale até o fim do dia.
- Log (research C18): `services.registrar_evento` com os eventos novos; autor `services.AUTOR_SISTEMA`
  no comando, na expiração e no recálculo; detalhe sem e-mail completo, sem valores de campos (só os
  nomes) e sem traceback (erros com `type(erro).__name__`).
- Testes: base `TesteAcesso` (`tests/apoio_acesso.py`), fábricas de `tests/fabricas.py`,
  `tests/apoio_turmas.py` e `tests/apoio_contas.py` (T002); nomes `test_cenario_NN_<resumo>`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: textos, fábricas de teste e linha de base da suíte.

- [X] T001 Acrescentar em `sigtcc/apps/cadastro/mensagens.py` uma seção "spec 002 (Gestão de Contas)", copiando caractere por caractere da spec 002 (FR e tabela "Mensagens a validar com a PO"): das US — `DOCENTE_CADASTRADO = "Docente cadastrado com sucesso"`, `SECRETARIA_CADASTRADA = "Secretaria cadastrada com sucesso"`, `MEMBRO_CADASTRADO = "Membro externo cadastrado com sucesso"`, `DADOS_ATUALIZADOS = "Dados atualizados"`, `EMAIL_JA_CADASTRADO = "Este e-mail já está cadastrado"`, `EMAIL_INSTITUCIONAL_CONTAS = "Informe um e-mail institucional (@uea.edu.br)"`, `EMAIL_VALIDO = "Informe um e-mail válido"`, `NOME_INVALIDO = "O nome deve conter apenas letras e até 150 caracteres"`, `OPCAO_INVALIDA = "Selecione uma opção válida"`, `INSTITUICAO_INVALIDA = "Informe a instituição com até 150 caracteres"`, `CURSO_JA_TEM_COORDENADOR = "O curso já possui Coordenador. Desmarque o papel no coordenador atual para continuar"`, `CURSO_JA_TEM_SECRETARIA = "O curso já possui Secretaria vinculada"`, `SO_DO_SEU_CURSO_CADASTRO = "Você só pode cadastrar e alterar dados do seu curso"`, `SO_DO_SEU_CURSO_ALTERACAO = "Você só pode alterar dados do seu curso"`, `NENHUM_REGISTRO = "Nenhum registro"`, `FALHA_AO_SALVAR = "Não foi possível salvar. Tente novamente"`, `CONFIRMAR_INATIVAR_DOCENTE = "Deseja inativar o docente {nome}?"`, `DOCENTE_INATIVADO = "Docente inativado"`, `NAO_E_POSSIVEL_INATIVAR = "Não é possível inativar: o docente {motivos}"`, `MOTIVO_TCC_ATIVO = "possui {n} orientandos ou coorientandos com TCC ativo"` (sempre no plural, Q18), `MOTIVO_COORDENADOR = "é Coordenador do curso"`, `FIM_ALERTA_VINCULOS = ". Encerre ou transfira esses vínculos primeiro"`, `ACESSO_PRORROGADO_ATE = "Acesso prorrogado até {data}"`, `FALHA_AO_PRORROGAR = "Não foi possível prorrogar o acesso. Tente novamente"`; a constante PROVISÓRIA `ACESSO_EXPIRADO_US06 = "Seu acesso expirou. Procure a coordenação do curso"` com comentário "provisória até a Q-52; só o teste do cenário 3 da US-06 a usa" (research C16); rótulos `CADASTRAR_DOCENTE = "Cadastrar Docente"`, `NOVA_SECRETARIA = "Nova secretaria"`, `NOVO_MEMBRO_EXTERNO = "Novo membro externo"`, `INATIVAR = "Inativar"`, `REATIVAR = "Reativar"`, `PRORROGAR = "Prorrogar"`, `CANCELAR = "Cancelar"`, `COORDENADOR_DE_CURSO = "Coordenador de Curso"`, `SUA_SENHA = "Sua senha"` (reaproveitar `SALVAR` e `EDITAR`); MC-01 a MC-10 definidas: `MC01_CONFIRMAR_REATIVAR = "Deseja reativar o docente {nome}?"`, `MC02_DOCENTE_REATIVADO = "Docente reativado"`, `MC03_CONFIRMAR_INATIVAR_SECRETARIA = "Deseja inativar a Secretaria {nome}?"`, `MC04_SECRETARIA_INATIVADA = "Secretaria inativada"`, `MC05_CONVITES` / `MC05_CONVITE_1` ("possui {n} convites de coorientação sem resposta" / "possui 1 convite de coorientação sem resposta"), `MC06_BANCAS` / `MC06_BANCA_1` ("participa de {n} bancas Agendadas, Reagendadas ou Em Andamento" / "participa de 1 banca Agendada, Reagendada ou Em Andamento"), `MC07_TURMAS` / `MC07_TURMA_1` ("é Professor da Disciplina de {n} turmas não arquivadas" / "é Professor da Disciplina de 1 turma não arquivada"), `MC09_SEM_VALIDADE = "Este membro ainda não ativou a conta e não tem validade para prorrogar"`, `MC10_STATUS_INCOMPATIVEL = "Esta ação não está disponível para o Status da Conta atual"`; as PROVISÓRIAS (Q-58) `MC11_SENHA_INCORRETA = "Senha incorreta"`, `MC12_TROCA_EMAIL_ENVIADA = "Dados atualizados. Enviamos um link de confirmação para o novo e-mail"`, `MC13_FALHA_ENVIO_TROCA = "Dados atualizados, mas não foi possível enviar o link de confirmação. Altere o e-mail novamente em alguns minutos"` (a MC-08 é `DOCENTE_CADASTRADO`). Trocar também, na seção da spec 003, `M02_ACESSO_NEGADO = "Você não tem permissão para esta ação"` e `M14_CAMPO_OBRIGATORIO = "Campo obrigatório"` (Q9; índice Q-50). Conferir com a tabela da spec e com `Historias_de_Usuario_v3_3.md`. — Rastreabilidade: [US-03][US-04][US-05][US-06][US-50][SC-002][FR-048][Q9][Q14]
- [X] T002 [P] Criar `sigtcc/apps/cadastro/tests/apoio_contas.py` com fábricas sobre `fabricas.py`, `apoio_acesso.py` e `apoio_turmas.py`: `docente_de(curso, status=ATIVA, email=None, titulacao="Doutor")`, `coordenador_de(curso, lotado_em=None)` (linha em `Coordenadores`), `secretaria_de(curso, status=ATIVA)`, `membro(status, validade=None, email=None)`, `orientacao_ativa(docente, tcc)`, `coorientacao_ativa(docente, tcc)`, `convite_pendente(docente, tcc)` (`sol_tipo` 'Coorientação', `sol_status` 'Aguardando Aceite'), `turma_do_docente(docente, status="Ativa")`, `banca(defesa, usuario, papel, substituido=None)`, `evento_defesa(defesa, evento, data_hora, removido=None)` (`Historico_Defesas`), `marco_versao_final(turma, aluno, status)` e o caminho dos cursos EC, SI e LC. — Rastreabilidade: [US-03][US-04][US-05][US-06][US-50]
- [X] T003 Rodar `python manage.py test sigtcc.apps.cadastro` antes de qualquer mudança e anotar em "Notes" deste arquivo a linha de base: falhas já existentes (esperado: `test_mensagens.py` e `test_mensagens_turmas.py` abrem `Historias_de_Usuario_v3_2.md`, que não existe — Q-77, Julia; `test_mensagens_provisorias_da_spec` da spec 003 passa a valer depois da T001). Não corrigir código de outras specs. — Rastreabilidade: [SC-001][research C24]

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: acréscimos ao contrato da spec 003, curso do usuário, travas, base de formulários, rotas,
menu, telas comuns e testes de contrato.

**⚠️ CRITICAL**: nenhuma história começa antes desta fase.

- [X] T004 Acrescentar em `sigtcc/apps/cadastro/services.py` (acréscimos ao contrato da spec 003; ciência da Julia, Q-71): em `EventoAcesso`, `CONTA_CRIADA`, `CONTA_ALTERADA`, `CONTA_INATIVADA`, `CONTA_REATIVADA`, `ACESSO_PRORROGADO`, `CONTA_EXPIRADA`, `VALIDADE_RECALCULADA` e `SENHA_GESTOR_INCORRETA`; a constante `AUTOR_SISTEMA` aceita por `registrar_evento` (grava `autor=sistema`; `autor=None` continua "própria"); `travar_email(email)` que roda `SELECT pg_advisory_xact_lock(hashtext(lower(%s)))` com o e-mail normalizado (exige transação aberta); o parâmetro opcional `autor=None` em `pedir_troca_email(conta, novo, autor=None)`, repassado ao `registrar_evento`, sem mudar o resto. Testes em `sigtcc/apps/cadastro/tests/test_log_contas.py` (autor "sistema", autor do gestor na troca, nenhum e-mail completo no detalhe). — Rastreabilidade: [US-03][US-05][FR-047][research C4][C18][I4][I5]
- [X] T005 [P] Acrescentar em `sigtcc/apps/cadastro/permissoes.py`, só com `models` do cadastro: `curso_do_usuario(usuario) -> Cursos | None` (Curso Coordenado de `Coordenadores.cor_cur` para o Coordenador; `Secretarios.sec_cur` para a Secretaria; senão `None`), `curso_do_registro(registro) -> Cursos` (`Docentes.doc_cur`, o Curso de Lotação, Q26; `Secretarios.sec_cur`) e `pode_gerir(usuario, registro) -> bool` (mesmo curso, Q5 e Q26). Testes em `sigtcc/apps/cadastro/tests/test_permissoes_contas.py` (Coordenador lotado num curso e coordenando outro: o curso dele é o coordenado; o registro dele pertence ao de lotação; Secretaria; docente comum sem curso). — Rastreabilidade: [US-03][US-04][RBN-CAD-14.1][FR-009][Q5][Q26][research C2]
- [X] T006 Criar `sigtcc/apps/cadastro/services_contas.py` com a base: exceção `ForaDoCurso(mensagem)`; `travar_conta(usu_id)` e `travar_contas(*ids)` (ordem crescente, `of=("self",)`, relendo as especializações); `travar_cursos(*cur_ids)` (ordem crescente); `docentes_ativos()`; `membros_externos_disponiveis()` (conta não 'Inativa'); `travar_e_conferir_ativo(usuario) -> bool` (trava e relê; docente: 'Ativa'; membro: não 'Inativa'); `destino_interno(valor, request) -> str | None` (começa com "/", passa por `url_has_allowed_host_and_scheme` e `resolve()`); `com_parametro(caminho, nome, valor)` com `urllib.parse`; e `exigir_curso(usuario, registro, mensagem)` que levanta `ForaDoCurso`. Testes em `sigtcc/apps/cadastro/tests/test_contrato_contas.py` (listas de escolha, `travar_e_conferir_ativo`, `destino_interno` recusando `//evil`, `https://...`, `/nao-existe/` e aceitando `/painel/`; `com_parametro` com query existente). — Rastreabilidade: [US-04][US-05][FR-028][FR-034][research C3][C19][C23][B1][m1]
- [X] T007 Ajustar `acesso_negado` em `sigtcc/apps/cadastro/views.py` e `sigtcc/templates/acesso_negado.html` para aceitar uma mensagem no contexto (padrão: `M02_ACESSO_NEGADO`), e criar em `views_contas.py` o ajudante `recusa_fora_do_curso(request, erro)` que renderiza esse template com `erro.mensagem` e `status=403`. Teste em `test_permissoes_contas.py`, depois da T005, que cria o arquivo (403 com M-02 e 403 com a mensagem do FR-009). — Rastreabilidade: [US-03][US-04][FR-009][FR-010][research C21][m2]
- [X] T008 [P] Criar `sigtcc/apps/cadastro/forms_contas.py` (só `forms.Form`, research C20) com os campos e validadores comuns: Nome Completo (só letras com acento e espaços, até 150; erro `NOME_INVALIDO`), E-mail Institucional (formato `nome@uea.edu.br`, até 100; erro `EMAIL_INSTITUCIONAL_CONTAS`), E-mail de qualquer domínio (validador do Django, até 100; erro `EMAIL_VALIDO`), Titulação ("Especialista", "Mestre", "Doutor"; valor fora: `OPCAO_INVALIDA`), Curso (os três cursos; fora: `OPCAO_INVALIDA`), Instituição de Origem (letras, números, espaços e pontuação, até 150; erro `INSTITUICAO_INVALIDA`), "Sua senha" (`PasswordInput` sem `render_value`); obrigatório vazio: `M14_CAMPO_OBRIGATORIO`; e-mail normalizado com `services.normalizar_email`. — Rastreabilidade: [US-03][US-05][FR-002][FR-003][FR-004][FR-012][FR-032][RBN-CAD-01.1][RBN-CAD-03.1]
- [X] T009 Criar `sigtcc/apps/cadastro/views_contas.py` (vazio com o ajudante da T007), as 13 rotas de [contracts/rotas.md](contracts/rotas.md) em `sigtcc/apps/cadastro/urls.py` (cada uma apontando para a view da sua fase; até lá, views que levantam `Http404`), os itens "Docentes", "Secretarias" e "Membros externos" (seção "Cadastros", ordens 20 a 22, perfis do contrato) em `sigtcc/apps/cadastro/menu.py`, e os templates comuns `sigtcc/templates/cadastro/contas/abas.html` (abas como links, a Secretaria vê "Secretarias" só para consulta) e `sigtcc/templates/cadastro/contas/confirmar.html` (pergunta, botões "Confirmar" e "Cancelar", POST com CSRF), seguindo o visual do protótipo de 17/10 (classes `cartao`, `tabela`, `btn`, `alerta` de `sigtcc.css`). — Rastreabilidade: [US-03][US-04][US-05][US-50][FR-010][FR-011][FR-031]
- [X] T010 [P] Acrescentar em `sigtcc/static/js/sigtcc.js` (só apresentação, sem regra): mostrar e esconder o campo Curso Coordenado conforme a caixa "Coordenador de Curso" e desabilitar o botão de um formulário depois do primeiro envio (prorrogar); em `sigtcc/static/css/sigtcc.css`, os estilos que faltarem para as abas e para o alerta de mais de 5 orientandos. — Rastreabilidade: [US-03][US-50][FR-013][FR-017][research C6][C12]
- [X] T011 [P] Criar `sigtcc/apps/cadastro/tests/test_mensagens_contas.py` que confere, caractere por caractere, cada constante da T001 com o texto em `docs/fonte/Historias_de_Usuario_v3_3.md` (as das US) e com a tabela "Mensagens a validar com a PO" de `specs/002-gestao-contas/spec.md` (MC-01 a MC-13). — Rastreabilidade: [SC-002][FR-048]

- [ ] T012 Pedir à Julia Cohen (Q-71) a atualização da spec 003 antes das tarefas que mudam o código dela (T004, T028, T034): FR-021 (a confirmação da troca de e-mail grava `usu_link_gerado_em`, invalidando os links de ativação e de redefinição anteriores, spec 002 Q31; trava consultiva do e-mail), regra do login (Q4, FR-008: o login com validade vencida grava 'Expirada'), FR-029 (eventos novos e autor "sistema") e o contrato `specs/003-acesso-login/contracts/servicos-compartilhados.md` (§4 e §5: `pedir_troca_email` com `autor`, `travar_email`, `AUTOR_SISTEMA`, `expirar_se_vencida`, mensagem opcional em `acesso_negado.html`). Bloqueia a T028 e a T034 até a resposta da Q-71 (ou até a Julia autorizar a edição). Registrar a resposta no índice e nas Notes. — Rastreabilidade: [constituição I][US-03][US-05][US-06][FR-008][FR-040][FR-047][Q31][Q-71]

- [X] T013 Implementar a coluna aprovada na Q-69 (spec Q36), num commit só: (1) atualizar a cópia do dicionário `docs/fonte/Modelo_Logico_e_Dicionario_18_10.md` — linha do modelo lógico da tabela 10 (`MembrosExternos (... mem_validade_ate, mem_prorrogado_ate)`) e a tabela da seção 3.2.4 com a linha `| mem_prorrogado_ate | DATE | Sim | \- | Data de validade dada pela última prorrogação manual (US-50); o recálculo pela banca nunca deixa mem_validade_ate antes dela. Nula enquanto não houver prorrogação |`, e a nova descrição de `mem_validade_ate` (gravada no cadastro como data do cadastro + 30 dias, Q-44); (2) acrescentar `mem_prorrogado_ate = models.DateField(null=True, blank=True)` em `MembrosExternos` (`sigtcc/apps/cadastro/models.py`), com comentário [US-50][US-06][RBN-CAD-03.3][Q36]; (3) gerar `sigtcc/apps/cadastro/migrations/0006_membrosexternos_mem_prorrogado_ate.py` (só essa coluna; conferir com `sqlmigrate`); (4) rodar `test_conformidade_dicionario` e a suíte do cadastro (verde). Avisar a Maria Luiza Guimarães para atualizar o documento no Drive. — Rastreabilidade: [US-06][US-50][RBN-CAD-03.3][FR-039][FR-043][Q15][Q36][Q-69][Q-44][constituição III]

**Checkpoint**: base pronta → `feat(feat-04): preparar base da gestao de contas`.

---

## Phase 3: User Story 1 - Cadastrar, alterar e listar docentes e a Secretaria (Priority: P1) 🎯 MVP

**Goal**: US-03 (exceto a troca de e-mail, fase 6): cadastro, alteração e listagem de docentes (com o
papel de Coordenador) e da Secretaria, com filtro de Curso.

**Independent Test**: com um Coordenador 'Ativa', cadastrar uma Secretaria e um docente, marcar o
papel em outro docente para um curso sem Coordenador, alterar dados e conferir a listagem com o
filtro (quickstart, seção 3, itens 1 a 5).

### Tests for User Story 1

- [X] T014 [P] [US1] Criar `sigtcc/apps/cadastro/tests/test_us03_docentes.py` com um teste por cenário da US-03 sobre docentes (cenários 1 a 17, 22 a 31, 33 a 36 e 39; o 32 fica na fase 6): mensagens exatas pelas constantes, Status 'Aguardando Ativação' e nenhum e-mail enviado na criação (`mail.outbox` vazio, Q1), Curso Coordenado de qualquer curso sem Coordenador (cenário 33, Q5), docente lotado num curso coordenando outro (Q26: só a Secretaria e o Coordenador do Curso de Lotação editam; ele não edita o próprio cadastro), marcar o papel em docente 'Inativa' recusado com `MC10_STATUS_INCOMPATIVEL` (Q32), desmarcar o próprio papel e perder o menu na página seguinte (PRG, m11), cenário 27 com o login da spec 003 ("Conta ainda não ativada" e 0 orientandos), contagem de orientandos por TCC 1 e TCC 2 e alerta acima de 5 (Q8), filtro "Todos", curso sem docentes ("Nenhum registro"), valor de filtro inválido volta ao padrão, falha ao gravar simulada (`FALHA_AO_SALVAR`, dados mantidos) e gravação só dos campos editáveis (uma alteração não desfaz o status de uma conta inativada entre o GET e o POST, C20). — Rastreabilidade: [US-03][RBN-CAD-01.1][RBN-CAD-01.2][RBN-CAD-01.4][RBN-CAD-11.3][RBN-CAD-14.1][FR-001][FR-005][FR-006][FR-014][FR-015][FR-016][Q5][Q8][Q26][Q32]
- [X] T015 [P] [US1] Criar `sigtcc/apps/cadastro/tests/test_us03_secretarias.py` com um teste por cenário da US-03 sobre a Secretaria (18 a 21, 37, 38 e 40): só o Coordenador cadastra e altera; curso com Secretaria 'Aguardando Ativação' ou 'Ativa' recusa (Q7); após a inativação, aceita outra; a Secretaria vê a lista sem "Nova secretaria", "Editar" e "Inativar" e leva 403 no endereço direto; troca de Curso Vinculado para curso ocupado recusada. — Rastreabilidade: [US-03][RBN-CAD-02.1][RBN-CAD-02.2][FR-020][FR-021][FR-022][Q7]

### Implementation for User Story 1

- [X] T016 [US1] Implementar em `sigtcc/apps/cadastro/services_contas.py`: `_criar_docente(dados, autor)` (núcleo sem permissão, usado pela tela e pelo comando: trava os cursos e o e-mail na ordem C19, confere "curso já tem Coordenador" antes do e-mail, `email_em_uso`, cria `Usuarios` 'Aguardando Ativação' sem senha, `Docentes` e, com o papel, `Coordenadores`; `IntegrityError` vira `EMAIL_JA_CADASTRADO` ou `CURSO_JA_TEM_COORDENADOR`; log `CONTA_CRIADA`); `cadastrar_docente(usuario, dados)` (confere perfil e curso do usuário para o Curso de Lotação; `SO_DO_SEU_CURSO_CADASTRO`); `alterar_docente(usuario, doc_id, dados)` (trava conta, docente e cursos; relê; `pode_gerir` com o curso atual; recusa o papel para conta 'Inativa' com MC-10; troca, cria ou apaga a linha de `Coordenadores`; grava `usu_nome`, `doc_titulacao`, `doc_cur` com `update_fields`; log `CONTA_ALTERADA` só com os nomes dos campos); `listar_docentes(usuario, filtro)` com as contagens de TCC 1 e TCC 2 anotadas numa consulta e o indicador de mais de 5 (research C9, C10). — Rastreabilidade: [US-03][RBN-CAD-01.1][RBN-CAD-01.2][RBN-CAD-01.4][RBN-CAD-11.3][FR-012 a FR-019][research C2][C5][C6][C9][C10][C17][C19][C20]
- [X] T017 [US1] Implementar em `sigtcc/apps/cadastro/services_contas.py`: `cadastrar_secretaria(usuario, dados)` e `alterar_secretaria(usuario, sec_id, dados)` (só Coordenador do curso; trava o curso, ou os dois cursos na troca de Curso Vinculado, em ordem crescente; conta Secretarias 'Aguardando Ativação' ou 'Ativa' do curso; `CURSO_JA_TEM_SECRETARIA`; grava `usu_nome` e `sec_cur` com `update_fields`; logs) e `listar_secretarias(usuario, filtro)`. — Rastreabilidade: [US-03][RBN-CAD-02.1][RBN-CAD-02.2][FR-020 a FR-023][Q7][research C5]
- [X] T018 [US1] Implementar em `sigtcc/apps/cadastro/forms_contas.py` `DocenteForm` (Nome, E-mail Institucional, Titulação, Curso de Lotação, caixa "Coordenador de Curso", Curso Coordenado obrigatório só com a caixa marcada e ignorado sem ela; `M14_CAMPO_OBRIGATORIO`) e `SecretariaForm` (Nome, E-mail Institucional, Curso Vinculado); na edição, o e-mail aparece mas a troca é tratada na fase 6. — Rastreabilidade: [US-03][FR-012][FR-013][FR-020][RBN-CAD-01.1][RBN-CAD-02.1]
- [X] T019 [US1] Implementar em `sigtcc/apps/cadastro/views_contas.py` as views `docentes`, `docente_novo`, `docente_editar`, `secretarias`, `secretaria_nova` e `secretaria_editar` (`@perfil_requerido("secretaria", "coordenador")` ou só `"coordenador"`; busca pela especialização; `ForaDoCurso` → `recusa_fora_do_curso`; PRG com `messages.success`; "Cancelar" volta à lista sem gravar), ligando as rotas da T009. — Rastreabilidade: [US-03][FR-007][FR-009][FR-010][research C21][C22]
- [X] T020 [US1] Criar `sigtcc/templates/cadastro/contas/docentes.html`, `form_docente.html`, `secretarias.html` e `form_secretaria.html` (estendem `base.html`, incluem `abas.html`, campos com `includes/campo.html`; colunas e botões do FR-017, FR-019 e FR-023; "Editar", "Inativar" e "Reativar" só quando a view indicar; filtro de Curso com "Todos"; "Nenhum registro"), seguindo o visual do protótipo de 17/10. Usa as variáveis de contexto definidas na T019. — Rastreabilidade: [US-03][FR-011][FR-017][FR-018][FR-023]

**Checkpoint**: `test_us03_docentes` e `test_us03_secretarias` verdes (exceto o cenário 32, fase 6) →
`feat(feat-04): cadastrar alterar e listar docentes e secretaria`.

---

## Phase 4: User Story 6 - Criar os Coordenadores de Curso na implantação (Priority: P1)

**Goal**: comando que cria os Coordenadores iniciais dos três cursos.

**Independent Test**: num banco recém-migrado, rodar o comando com um CSV e entrar com um Coordenador
pelo primeiro acesso (quickstart, seção 2).

- [X] T021 [P] [US6] Criar `sigtcc/apps/cadastro/tests/test_comando_coordenadores.py` com os 4 cenários da história 6: três contas 'Aguardando Ativação', lotadas e coordenando o próprio curso, sem e-mail enviado; segunda execução recusa com `CURSO_JA_TEM_COORDENADOR` e não duplica; e-mail repetido, fora de `@uea.edu.br`, nome ou titulação inválidos recusados com o texto das telas, seguindo os outros cursos; mais: CSV com BOM (`utf-8-sig`), modo `--curso --nome --email --titulacao`, saída sem nenhum e-mail, funciona com `DEBUG = False`, log `CONTA_CRIADA` com autor "sistema". — Rastreabilidade: [RAN-CAD-01][RBN-CAD-06.2][FR-045][FR-046][research C17][m4]
- [X] T022 [US6] Criar `sigtcc/apps/cadastro/management/commands/criar_coordenadores.py`: argumentos `--arquivo` (CSV `curso;nome;email;titulacao`, `encoding="utf-8-sig"`, `newline=""`, `delimiter=";"`) ou `--curso --nome --email --titulacao`; ajuda avisando que `--email` fica no histórico do shell; cada curso numa transação, chamando `services_contas._criar_docente(dados, autor=AUTOR_SISTEMA)` com o papel de Coordenador; saída por curso "criado" ou "recusado: <mensagem>", sem e-mail. — Rastreabilidade: [RAN-CAD-01][RBN-CAD-06.2][FR-045][FR-046][research C17]

**Checkpoint**: `test_comando_coordenadores` verde → `feat(feat-04): criar comando dos coordenadores iniciais`.

---

## Phase 5: User Story 2 - Cadastrar e alterar membros externos (Priority: P1)

**Goal**: US-05 (exceto a troca de e-mail, fase 6): cadastro, alteração e lista de membros externos,
com o atalho da banca.

**Independent Test**: com uma Secretaria 'Ativa', cadastrar um membro de outro domínio, alterar a
Titulação e conferir as recusas (quickstart, seção 5, itens 1 e 2).

- [X] T023 [P] [US2] Criar `sigtcc/apps/cadastro/tests/test_us05_membros.py` com um teste por cenário da US-05 (1 a 16 e 18 a 23; o 17 fica na fase 6): perfis do FR-031 (Professor da Disciplina só com turmas arquivadas vê a lista mas não cadastra nem altera, Q10), validade = data do cadastro + 30 em `mem_validade_ate` (cenário 20, Q12), e-mail de qualquer domínio, recusas com mensagens exatas, atalho da banca (`?voltar=` interno volta com `membro=<id>`; cancelar volta sem ele; `voltar` externo ou que não resolve é ignorado; valor revalidado no POST), alteração de membro 'Expirada' grava sem reabrir o acesso (US-05 A6), lista sem filtro de Curso (Q19), endereço direto com id de docente dá 404. — Rastreabilidade: [US-05][RBN-CAD-03.1][RBN-CAD-03.2][RBN-DEF-02.3][FR-031][FR-032][FR-033][FR-034][FR-035][FR-036][Q10][Q12][Q19][research C22][C23]
- [X] T024 [US2] Implementar em `sigtcc/apps/cadastro/services_contas.py`: `pode_gerir_membros(usuario) -> bool` (Orientador, Secretaria, Coordenador, ou Professor da Disciplina com `professor_com_turma_ativa`), `cadastrar_membro(usuario, dados)` (trava do e-mail, `email_em_uso`, cria `Usuarios` 'Aguardando Ativação', `MembrosExternos` com `mem_validade_ate = hoje + 30`; log), `alterar_membro(usuario, mem_id, dados)` (trava a conta, relê, grava `usu_nome`, `mem_titulacao`, `mem_instituicao` com `update_fields`; não muda status) e `listar_membros(usuario)` com status exibido considerando a validade vencida. — Rastreabilidade: [US-05][RBN-CAD-03.1][RBN-CAD-03.2][FR-031 a FR-036][FR-038][Q10][Q12][research C20]
- [X] T025 [US2] Implementar `MembroForm` em `sigtcc/apps/cadastro/forms_contas.py` (Nome, E-mail de qualquer domínio, Titulação, Instituição de Origem, campo oculto `voltar`) e as views `membros`, `membro_novo` e `membro_editar` em `sigtcc/apps/cadastro/views_contas.py` (`@perfil_requerido("orientador", "professor_disciplina", "secretaria", "coordenador")`; atalho com `destino_interno` e `com_parametro`), ligando as rotas. — Rastreabilidade: [US-05][FR-032][FR-034][FR-035][research C23]
- [X] T026 [US2] Criar `sigtcc/templates/cadastro/contas/membros.html` e `form_membro.html` (colunas do FR-036, validade DD/MM/AAAA, "Editar" e a coluna do "Prorrogar" preparada para a fase 9), seguindo o protótipo de 17/10. Usa as variáveis de contexto definidas na T025. — Rastreabilidade: [US-05][FR-036]

**Checkpoint**: `test_us05_membros` verde (exceto o cenário 17) → `feat(feat-04): cadastrar e alterar membros externos`.

---

## Phase 6: Troca de e-mail pelo gestor (US-03 A11, US-05 A3)

**Goal**: troca de e-mail com a senha de quem altera e confirmação pelo link (Q17, Q24, Q28, Q30, Q31,
Q35).

**Independent Test**: alterar o e-mail de um docente com "Sua senha" correta, conferir o link no
`mail.outbox`, confirmar e entrar com o novo e-mail (quickstart, seção 3, item 6).

- [X] T027 [P] [US1] Criar `sigtcc/apps/cadastro/tests/test_troca_email_gestor.py`: US-03 cenário 32 e US-05 cenário 17 (o e-mail só muda depois do link; até lá, o login é o antigo; depois, a senha antiga vale); senha errada → MC-11, nada gravado e `SENHA_GESTOR_INCORRETA` no log, sem limite de tentativas (Q35); sucesso → MC-12; falha no envio simulada → MC-13, demais campos gravados, e-mail sem mudança (Q24); e-mail de outra conta no formulário → `EMAIL_JA_CADASTRADO`; M-05 só na confirmação; troca só da caixa da parte local não abre troca (m12); Membro Externo 'Ativa' ou 'Expirada': Orientador e Professor da Disciplina veem o campo só para leitura e levam M-02 se postarem outro e-mail; Secretaria e Coordenador trocam (Q30); confirmação invalida os links de ativação e de redefinição anteriores ao e-mail antigo (Q31); dois links pendentes: o primeiro vale até outro ser confirmado (Q28); conta 'Aguardando Ativação' corrigida pelo link. — Rastreabilidade: [US-03][US-05][RBN-CAD-01.2][RBN-CAD-02.2][RBN-CAD-03.2][FR-008][Q17][Q24][Q28][Q30][Q31][Q35]
- [X] T028 [US1] Alterar `confirmar_troca_email` em `sigtcc/apps/cadastro/services.py` (código da spec 003; ciência da Julia, Q-71): chamar `travar_email(novo)` antes de conferir e gravar, e gravar `usu_link_gerado_em = timezone.now()` junto com `usu_email` (`update_fields=["usu_email", "usu_link_gerado_em"]`), invalidando os links anteriores (Q31). Rodar os testes da spec 003 (`test_us38_perfil_notificacoes`, `test_us10_primeiro_acesso`, `test_us12_senha`) e conferir que continuam verdes. — Rastreabilidade: [US-38][US-03][US-05][FR-008][Q31][research C4][C7]
- [X] T029 [US1] Implementar em `sigtcc/apps/cadastro/services_contas.py` `pode_trocar_email(usuario, conta)` (Membro Externo 'Ativa' ou 'Expirada': só Secretaria e Coordenador, Q30; demais contas: quem pode alterar) e o fluxo da troca dentro de `alterar_docente`, `alterar_secretaria` e `alterar_membro`: e-mail novo diferente sem diferenciar maiúsculas → exigir "Sua senha" com `services.senha_atual_confere` (MC-11 e log se errada); transação 1 grava os outros campos; transação 2 (`travar_email`, `email_em_uso`, `pedir_troca_email(conta, novo, autor=usuario)`) devolve MC-12 ou, se o envio falhar, MC-13. Ajustar `DocenteForm`, `SecretariaForm` e `MembroForm` (campo "Sua senha" exigido só com e-mail novo; e-mail só leitura quando `pode_trocar_email` for falso) e as views de edição. — Rastreabilidade: [US-03][US-05][FR-008][FR-035][Q17][Q24][Q30][Q35][research C7][C20]

**Checkpoint**: `test_troca_email_gestor` e os cenários 32 (US-03) e 17 (US-05) verdes → `feat(feat-04): trocar email pelo gestor com confirmacao`.

---

## Phase 7: User Story 3 - Inativar e reativar docentes e a Secretaria (Priority: P2)

**Goal**: US-04 completa, com a verificação de vínculos repetida sob trava.

**Independent Test**: inativar um docente sem vínculos, ver "Conta inativa" no login, reativar; ver o
motivo de cada vínculo; inativar a Secretaria e cadastrar outra (quickstart, seção 4).

- [X] T030 [P] [US3] Criar `sigtcc/apps/cadastro/tests/test_us04_inativacao.py` com um teste por cenário da US-04 (1 a 25): cada vínculo sozinho e combinado, na ordem (a) a (e) e com "e" no último; motivo (a) sempre no plural (Q18) e MC-05 a MC-07 no singular com N = 1 (Q14); TCC Sem Proposta não impede (cenário 11, Q16); Aprovado com Versão Final não homologada impede (cenário 4); vínculo que surge entre o GET e o POST (cenário 15); 'Aguardando Ativação' sem "Inativar" nem "Reativar" e MC-10 pelo endereço direto; fora do curso com `SO_DO_SEU_CURSO_ALTERACAO` (cenário 18); Secretaria inativada libera o curso e não volta (Q27); falha ao gravar; log `CONTA_INATIVADA` e `CONTA_REATIVADA`. — Rastreabilidade: [US-04][RBN-CAD-01.3][RBN-CAD-02.3][FR-024 a FR-030][Q14][Q16][Q18][Q27]
- [X] T031 [US3] Implementar em `sigtcc/apps/cadastro/services_contas.py`: `vinculos_do_docente(docente)` (cinco contagens, research C8: (a) TCCs Em Andamento, Apto para Defesa, Aprovado ou Aprovado com Correções com orientação ou coorientação 'Ativa' do docente e marco 'Versão Final' não 'Homologada', cada TCC uma vez; (b) `sol_tipo` 'Coorientação' e `sol_status` 'Aguardando Aceite'; (c) `Banca_Defesa` com `def_status` 'Agendada', 'Reagendada' ou 'Em Andamento'; (d) `Turmas` 'Ativa' do docente; (e) linha em `Coordenadores`), `alerta_de_vinculos(contagens)` (frase do FR-027 com as constantes da T001), `inativar_docente(usuario, doc_id)`, `reativar_docente(usuario, doc_id)` e `inativar_secretaria(usuario, sec_id)` (trava conta e especialização, relê status e vínculos, confere curso e perfil, grava só `usu_status`, log). — Rastreabilidade: [US-04][RBN-CAD-01.3][RBN-CAD-02.3][FR-024][FR-025][FR-026][FR-027][FR-029][research C8][C19][B1]
- [X] T032 [US3] Implementar em `sigtcc/apps/cadastro/views_contas.py` `docente_inativar`, `docente_reativar` e `secretaria_inativar` (GET: verifica e mostra o alerta na lista ou a confirmação em `contas/confirmar.html` com `CONFIRMAR_INATIVAR_DOCENTE`, MC-01 ou MC-03; POST: chama o serviço; PRG) e os botões nas listas (`docentes.html`, `secretarias.html`). — Rastreabilidade: [US-04][FR-019][FR-023][FR-025][FR-029]

**Checkpoint**: `test_us04_inativacao` verde → `feat(feat-04): inativar e reativar docentes e secretaria`.

---

## Phase 8: User Story 4 - Validade e expiração do acesso do Membro Externo (Priority: P2)

**Goal**: US-06: regra de validade para a Defesa chamar, expiração automática e no login.

**Independent Test**: com sessões e bancas criadas direto nos dados, calcular a validade em cada caso
e conferir login e status antes e depois (quickstart, seção 5, itens 3 e 5).

- [ ] T033 [P] [US4] Criar `sigtcc/apps/cadastro/tests/test_us06_validade.py` com um teste por cenário da US-06 (1 a 18) chamando `recalcular_validade` com dados criados direto: defesa mais distante + 7; sessão Cancelada não conta; último cancelamento + 7; retirada + 7 (Q13) e o mais recente entre cancelamentos e retiradas (Q-45); Realizada conta; reagendamento para depois e para antes; 'Expirada' volta a 'Ativa'; 'Aguardando Ativação' não muda de status; validade no passado com conta 'Ativa' grava 'Expirada' (m9); membro substituído pelo suplente mantém a sessão no cálculo (Q33); falha simulada mantém a validade, devolve `False` e não quebra a transação de quem chamou (US-06 E2); outro tipo de conta devolve `True` sem mudar nada. O cenário 3 confere `ACESSO_EXPIRADO_US06` e fica `@expectedFailure` com o motivo "Q-52: troca da M-16 pela spec 003". A proteção da prorrogação (Edge Case, Q15, Q36): depois de uma prorrogação (`mem_prorrogado_ate` preenchida), um reagendamento para antes não reduz a validade abaixo dela, e um para depois a estende (exemplo do Edge Case: 10/11 continua; 15/11 → 22/11). — Rastreabilidade: [US-06][RBN-CAD-03.3][RBN-DEF-02.4][FR-037 a FR-041][Q4][Q13][Q15][Q33][Q34][research C13][C14]
- [ ] T034 [US4] Implementar `expirar_se_vencida(usuario) -> bool` em `sigtcc/apps/cadastro/services.py` (transação curta; trava a conta; relê status e `mem_validade_ate`; grava 'Expirada' com `update_fields=["usu_status"]` só se ainda for 'Ativa' vencida; log `CONTA_EXPIRADA` com `AUTOR_SISTEMA`) e chamá-la em `autenticar` no ramo de validade vencida, dentro de `try/except` (uma falha não muda o resultado `EXPIRADA`). Testes em `test_us06_validade.py` (login grava a troca; falha simulada na gravação mantém a recusa do login) e conferir que `test_us11_login` (spec 003) continua verde. — Rastreabilidade: [US-06][US-11][RBN-CAD-03.3][FR-040][Q3][research C15][I2]
- [ ] T035 [US4] Implementar `recalcular_validade(usuario, hoje=None) -> bool` em `sigtcc/apps/cadastro/services_contas.py` conforme research C14 e data-model §4: só Membro Externo; savepoint interno com a exceção capturada fora dele; trava `select_for_update(no_key=True, of=("self",))`; relê `MembrosExternos`; passo 1 com `ban_usu` ou `ban_usu_substituido` igual ao membro e `def_status` diferente de 'Cancelada'; passo 2 com `Historico_Defesas` ('Cancelamento' de sessão com o membro na banca; 'Alteração da Banca' com `hdf_membro_removido`); passo 3 mantém; `_data_protegida(membro)` lê `mem_prorrogado_ate` e a validade nunca fica antes dela (Q15, Q36); ajuste de status; grava com `update_fields`; log `VALIDADE_RECALCULADA` (sistema) ou, na falha, só `type(erro).__name__`. — Rastreabilidade: [US-06][RBN-CAD-03.3][RBN-DEF-02.4][FR-037][FR-039][FR-041][Q13][Q15][Q33][research C13][C14][I1][I8]
- [ ] T036 [US4] Criar `sigtcc/apps/cadastro/management/commands/expirar_membros_externos.py`: lista as contas de Membro Externo 'Ativa' com `mem_validade_ate` antes de hoje e chama `services.expirar_se_vencida` para cada uma; imprime só a quantidade expirada; idempotente. Testes em `test_us06_validade.py` (SC-006: expira sem login; rodar de novo não muda nada; conta prorrogada no meio não é expirada). — Rastreabilidade: [US-06][RBN-CAD-03.3][FR-040][SC-006][research C15]

**Checkpoint**: `test_us06_validade` verde (com o `expectedFailure` da Q-52) →
`feat(feat-04): calcular validade e expirar membros externos`.

---

## Phase 9: User Story 5 - Prorrogar o acesso de membro externo (Priority: P3)

**Goal**: US-50: botão "Prorrogar" para quem pode, somando 7 dias.

**Independent Test**: prorrogar uma conta 'Ativa' e uma 'Expirada' e conferir validade, status e
login; conferir que o botão não aparece para quem não pode nem para 'Aguardando Ativação'
(quickstart, seção 5, item 4).

- [ ] T037 [P] [US5] Criar `sigtcc/apps/cadastro/tests/test_us50_prorrogacao.py` com um teste por cenário da US-50 (1 a 9): Orientador com orientação 'Ativa' de TCC com sessão não Cancelada e o membro na banca (Q11); Orientador sem o vínculo não vê o botão; Professor da Disciplina só com turma não arquivada; 'Ativa' em dia soma 7; 'Expirada', vencida ou sem validade gravada (Edge Case) → hoje + 7 e 'Ativa'; em todos os casos, `mem_prorrogado_ate` recebe a nova validade (Q36); duas vezes soma 14; 'Aguardando Ativação' sem botão e MC-09 no endereço direto (com permissão); sem permissão → M-02 antes de olhar o status (m7); falha ao gravar; PRG; log `ACESSO_PRORROGADO`. — Rastreabilidade: [US-50][RBN-CAD-03.3][FR-042 a FR-044][Q10][Q11][research C11][C12]
- [ ] T038 [US5] Implementar em `sigtcc/apps/cadastro/services_contas.py` `pode_prorrogar(usuario, membro)`, a anotação do vínculo do Orientador em `listar_membros` (uma consulta) e `prorrogar(usuario, mem_id)` (trava a conta, relê, confere permissão e depois status, calcula, grava `mem_validade_ate`, `mem_prorrogado_ate` (a mesma data, Q36) e `usu_status` com `update_fields`, log). — Rastreabilidade: [US-50][RBN-CAD-03.3][FR-042][FR-043][FR-044][research C11][C12][C15]
- [ ] T039 [US5] Implementar a view `membro_prorrogar` (só POST, PRG com `ACESSO_PRORROGADO_ATE` ou `FALHA_AO_PRORROGAR`) em `sigtcc/apps/cadastro/views_contas.py` e o botão "Prorrogar" em `sigtcc/templates/cadastro/contas/membros.html` (formulário POST com o atributo que o `sigtcc.js` usa para desabilitar após o clique). — Rastreabilidade: [US-50][FR-042][FR-043]

**Checkpoint**: `test_us50_prorrogacao` verde → `feat(feat-04): prorrogar acesso de membro externo`.

---

## Phase 10: Polish & Cross-Cutting Concerns

- [ ] T040 [P] Completar `sigtcc/apps/cadastro/tests/test_permissoes_contas.py` (SC-004): para cada uma das 13 rotas e cada perfil (Aluno, Docente comum, Orientador, Professor só com turmas arquivadas, Secretaria, Coordenador, Membro Externo, visitante), o resultado esperado (200, 302 para o login com `next`, 403 com M-02, 403 com a mensagem do FR-009, 404 para id de outro tipo de conta), inclusive pelo endereço direto, e nenhum dado do registro na resposta 403. — Rastreabilidade: [US-03][US-04][US-05][US-50][SC-004][FR-009][FR-010][research C21][C22]
- [ ] T041 [P] Criar `sigtcc/apps/cadastro/tests/test_concorrencia_contas.py` com `TransactionTestCase` e duas conexões (SC-003; research C24): mesmo e-mail com caixa diferente gravado ao mesmo tempo (só um passa, C4); dois Coordenadores para o mesmo curso; duas Secretarias para o mesmo curso; inativação simultânea a um vínculo novo criado com `travar_e_conferir_ativo` (o vínculo é recusado ou a inativação é recusada, nunca os dois gravados, B1); expiração simultânea a uma prorrogação (a conta prorrogada fica 'Ativa', I2); edição simultânea a uma inativação (o status não volta, C20). — Rastreabilidade: [US-03][US-04][US-06][US-50][SC-003][SC-005][research C4][C5][C15][C19][C20][B1][I2][I3]
- [ ] T042 [P] Completar `sigtcc/apps/cadastro/tests/test_contrato_contas.py` (contrato de serviços 002): `recalcular_validade` dentro de uma transação externa (savepoint: falha não quebra a transação; chamada repetida não muda o resultado), `docentes_ativos`, `membros_externos_disponiveis`, `travar_e_conferir_ativo`, `expirar_se_vencida`, atalho da banca; e o teste de tempo do filtro de Curso com 60 docentes por curso, abaixo de 2 s com margem (SC-009). — Rastreabilidade: [US-04][US-05][US-06][FR-028][FR-034][FR-039][SC-009][research C3][C14]
- [ ] T043 Rodar `lint.bat` (isort, black --line-length 100, flake8 --max-line-length 100) e corrigir só os arquivos desta feature; rodar `python manage.py test sigtcc.apps.cadastro sigtcc.apps.defesa` e comparar com a linha de base da T003 (nenhuma falha nova). — Rastreabilidade: [constituição V][SC-001]
- [ ] T044 Executar o [quickstart.md](quickstart.md) inteiro, cronometrando o SC-007 (até 10 min) e o SC-008 (docente em até 2 min; prorrogação em até 30 s), e registrar o resultado em "Notes". — Rastreabilidade: [SC-007][SC-008]
- [ ] T045 Conferir a rastreabilidade de todos os arquivos novos e alterados (cada classe, função, template e teste com [US-XX][RBN-...]) e, antes do PR, rodar o agente `revisor-pgcs` e preparar o texto do PR `[Feat-04] Gestão de Contas (US-03, US-04, US-05, US-06, US-50)` com o template do PGCS 6.3, incluindo as pendências abertas (Q-52, Q-58, Q-63, Q-67, Q-68, Q-70, Q-71, Q-76, Q-77) e os testes marcados com Q-52 e Q-69. — Rastreabilidade: [constituição II][constituição VIII]

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (fase 1)**: sem dependências.
- **Foundational (fase 2)**: depende da fase 1; bloqueia todas as histórias.
- **US1 (fase 3)**: depende da fase 2.
- **US6 (fase 4)**: depende da T016 (`_criar_docente`).
- **US2 (fase 5)**: depende da fase 2; pode correr junto com a fase 3 (arquivos de teste e templates
  diferentes; `services_contas.py`, `forms_contas.py` e `views_contas.py` são compartilhados, então as
  tarefas de implementação são sequenciais entre si).
- **Troca de e-mail (fase 6)**: depende das fases 3 e 5.
- **US3 (fase 7)**: depende da fase 3 (listas e alteração do papel).
- **US4 (fase 8)**: depende da fase 5 (membros).
- **US5 (fase 9)**: depende das fases 5 e 8 (`expirar_se_vencida`, status vencido).
- **Polish (fase 10)**: depende de todas.

### Bloqueios externos

- Spec 003 (Julia, Q-71): T012 bloqueia a T028 (confirmação da troca de e-mail) e a T034 (login grava 'Expirada'). A T004 (acréscimos ao `services.py`) pode seguir, porque não muda comportamento existente.

- A Defesa só liga o recálculo em produção depois que a T035 (proteção) estiver no `develop` (Q34,
  Q36).
- Texto de expiração no login: Q-52 (Julia). Até lá, o teste do cenário 3 da US-06 fica
  `expectedFailure` (T033).
- Textos MC-11 a MC-13: provisórios (Q-58); não bloqueiam.

### Parallel Opportunities

- Setup: T002 ao lado de T001.
- Foundational: T005, T008, T010 e T011 (arquivos diferentes), depois de T004 e T006; a T007 vem
  depois da T005 (mesmo arquivo de teste); a T012 corre ao lado de todas (pedido à Julia); a T013
  (coluna da Q-69) corre ao lado das outras e precisa estar pronta antes da T035 e da T038.
- Testes de cada história ([P]) antes da implementação: T014 e T015; T021; T023; T027; T030; T033;
  T037.
- Templates (T020, T026): depois das views da mesma fase (contexto definido nelas).
- Polish: T040, T041 e T042.

---

## Parallel Example: User Story 1

```bash
Task: "T014 test_us03_docentes.py"
Task: "T015 test_us03_secretarias.py"
```

## Parallel Example: Polish

```bash
Task: "T040 test_permissoes_contas.py"
Task: "T041 test_concorrencia_contas.py"
Task: "T042 test_contrato_contas.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Fases 1 e 2.
2. Fase 3 (US1): docentes e Secretaria.
3. Fase 4 (US6): Coordenadores iniciais — sem eles não há quem use a US1 numa instalação nova.
4. **Parar e validar**: `test_us03_*` e `test_comando_coordenadores` verdes; quickstart, seções 2 e 3.

### Incremental Delivery

1. Setup + Foundational → `feat(feat-04): preparar base da gestao de contas`.
2. US1 → `feat(feat-04): cadastrar alterar e listar docentes e secretaria`.
3. US6 → `feat(feat-04): criar comando dos coordenadores iniciais`.
4. US2 → `feat(feat-04): cadastrar e alterar membros externos`.
5. Troca de e-mail → `feat(feat-04): trocar email pelo gestor com confirmacao`.
6. US3 → `feat(feat-04): inativar e reativar docentes e secretaria`.
7. US4 → `feat(feat-04): calcular validade e expirar membros externos`.
8. US5 → `feat(feat-04): prorrogar acesso de membro externo`.
9. Polish → `test(feat-04): ...` e `docs(feat-04): ...`.

---

## Notes

- [P] = arquivos diferentes, sem dependência de tarefa incompleta.
- T028 e T034 mudam código da spec 003 (acréscimos combinados no contrato; ciência da Julia, Q-71):
  rodar a suíte da spec 003 depois de cada uma.
- Código de outras pessoas não é corrigido aqui: `criar_turma` e os testes que abrem a US v3.2 ficam
  com a Julia (Q-77).
- Linha de base da suíte (T003, 2026-10-22, `cadastro` + `defesa`, `--parallel 1`): 421 testes,
  3 falhas e 2 erros antes de qualquer mudança: (1) e (2) `test_textos_das_us` em `test_mensagens.py`
  e `test_mensagens_turmas.py` abrem a US v3.2, que não existe (Q-77, Julia); (3) e (4)
  `test_mensagens_provisorias_da_spec` (M-02 e M-14), corrigidos pela T001; (5)
  `test_base_comum.test_cenario5_link_gerado_fora_das_telas` falha na suíte inteira e passa sozinho
  (depende da ordem dos testes; spec 003, não é desta feature). Causa provável: os dois links do teste
  são gerados no mesmo instante gravado em `usu_link_gerado_em`, e o primeiro não fica "substituído";
  é intermitente e independe do código da spec 002 (avisar a Julia junto da Q-77). O `venv` precisou de
  `pip install -r requirements.txt` (faltava o `openpyxl` da spec 004).
- Resultado do quickstart (T044): _a preencher_.
- T009 (2026-10-22): as rotas entram na fase de cada view, e não como esqueletos que devolvem 404;
  o processador de contexto do menu já esconde o item enquanto a rota não existe. Nenhuma regra muda.
- T013: o `test_conformidade_dicionario` (spec 001) passou a esperar 202 colunas (201 + a da Q-69).
- T012: o pedido à Julia está na Q-71 do índice. A T028 e a T034 foram feitas antes da resposta, por
  decisão da responsável em 2026-10-23 (acréscimos já combinados no contrato §5); a Julia precisa dar
  ciência e atualizar a spec 003.
- Fase 3: o fluxo da troca de e-mail pelo gestor (senha, MC-11 a MC-13, `pedir_troca_email` com
  autor) já entrou em `alterar_docente` e `alterar_secretaria`, porque é o mesmo formulário; os testes
  dele, a restrição da Q30 (Membro Externo) e a mudança em `confirmar_troca_email` (T028) ficam na
  fase 6. A unicidade do e-mail novo é conferida antes de "Sua senha" (US-03 cenário 30; FR-008).
- Pendências fora desta feature: [plan.md](plan.md) ("Pendências") e o índice
  [docs/questoes-a-rever.md](../../docs/questoes-a-rever.md).
