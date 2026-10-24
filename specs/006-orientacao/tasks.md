# Tasks: Orientação, Atas e Publicações do SIGTCC

**Input**: Design documents from `specs/006-orientacao/`

**Prerequisites**: [plan.md](plan.md) (aprovado por Leandra Matos e Célio Benjamim em 2026-10-24,
depois da revisão e de duas reconferências do `arquiteto-django`), [spec.md](spec.md) (aprovada em
2026-10-24; Clarifications Q1 a Q18), [research.md](research.md) (R1 a R21; marcas [A1] a [A34] e
[N1] a [N12]), [data-model.md](data-model.md), [contracts/rotas.md](contracts/rotas.md),
[contracts/servicos-compartilhados.md](contracts/servicos-compartilhados.md),
[quickstart.md](quickstart.md)

**Aprovação do tasks.md**: aprovado por Leandra Matos (responsável pelas US) e Célio Benjamim
(configuração) em 2026-10-24. `/speckit-analyze` de 2026-10-24: nenhum achado crítico, 100% dos FR e SC com tarefa;
os 8 achados (I1, I2, U1, C1, C2, A1, A2, F1) foram corrigidos: números das tarefas de conferência
(T059, T060), inclusão do `secao.js` em T018, criação do `.claude/launch.json` em T060, testes da
cópia para o TCC 2 em T008, testes do destino das notificações em T059, nomes reais das constantes
em T001, linhas do CSS do protótipo em T004 e dependência T007 → T009.

**Tests**: obrigatórios (constituição, princípio VI): cada cenário Dado/Quando/Então das US-17 (12),
US-18 (14), US-41 (7), US-19 (16), US-42 (8), US-45 (14), US-36 (11), US-46 (8) e US-20 (9) vira
pelo menos um teste, mais os 7 pontos de contato (US2 #15 a #17; US3 #8 e #9; US9 #10 e #11), os
casos de permissão e troca de ID (SC-006), mensagens exatas (SC-003), navegação (SC-005), motivo do
cancelamento (FR-050) e concorrência. Os testes de cada fase vêm antes da implementação e devem
falhar primeiro.

**Organization**: histórias da spec: US1 = pedido, cancelamento e troca de orientador (US-17), US2 =
resposta do docente e tela Orientações (US-18), US3 = aba Alunos e painel do aluno (US-41), US4 =
atas (US-19), US5 = Apto para Defesa (US-42), US6 = coorientadores (US-45), US7 = convite de
coorientação (US-36), US8 = publicação do artigo (US-46), US9 = aproveitamento (US-20).

**Branch**: `feature/feat-06-orientacao`. Commits atômicos ao fim de cada fase, só com os testes
passando, mostrando o `git status` antes (CLAUDE.md). Formato:
`feat(feat-06): <imperativo, até 72 caracteres, sem ponto final>`; sem coautoria nem link de
sessão. Não fazer push, merge nem tag.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência de tarefa incompleta)
- **[Story]**: história da spec (US1 a US9)

## Regras para todas as tarefas

- Comentários e docstrings em português; cada classe, função, template e teste indica as US e RBN
  que atende, no formato `[US-17][RBN-CAD-10.1]` (constituição, princípio II). Cada tarefa termina
  com `Rastreabilidade:`.
- Mensagens sempre por constantes de `sigtcc/apps/cadastro/mensagens.py` (T001): texto exato das US
  ou MO-01 a MO-26 da spec, marcadas `# PROVISÓRIA (MO-xx)`.
- Nenhuma tabela, coluna ou migração nova (data-model.md). `makemigrations --check` sem mudanças.
- Regras em `services_orientacao.py`, `services_atas.py` e `services_artigos.py`; views só
  orquestram; templates sem regra (o service entrega as decisões de botão prontas).
- `tcc_status` só muda por `services_turmas.atualizar_status_tcc` (spec 005, FR-012).
- **Travas** (research R2): `transaction.atomic()` e sempre turma (`travar_turma_ativa`; o
  Coordenador usa `select_for_update` sem exigir turma ativa) → aluno (`Alunos` com
  `select_for_update`) → TCC → conta do docente (`travar_e_conferir_ativo`) → solicitação, artigo
  ou entrega. Depois de travar, conferir `tcc.tcc_tur_id == turma.pk` (senão 404) e reler o estado.
  Gravações sujeitas a índice único rodam num savepoint; `IntegrityError` vira o tratamento do
  duplo clique.
- **Instante do evento** (research R3; contrato §5): calcular `agora = timezone.now()` **uma vez**
  por evento e passar o mesmo objeto a todas as linhas; proibido truncar, usar `Now()`,
  `auto_now`/`auto_now_add` ou chamar `timezone.now()` de novo no mesmo evento.
- **Acesso** (contracts/rotas.md): sem sessão → login com `next` (preserva `?secao=`); sem perfil →
  403 (M-02); sem vínculo → 404; todo `coo_id`, `sol_id` e `enc_id` da URL é buscado filtrando pelo
  TCC do contexto (`coo_tcc`, `sol_tcc` + `sol_tipo` da rota, `enc_tcc`); turma arquivada nas rotas
  do Aluno e do Docente → redireciona à própria tela com a MT-25 (nunca `trata_turma_arquivada`).
- **Notificações** por `services.notificar` **dentro** da transação; e-mails por
  `services.enviar_email_apos_commit` (T010). Links por `reverse`; links de pedido e convite só por
  `services_orientacao.link_da_solicitacao(sol)`.
- **Volta** (research R5): só `?volta=painel` (valor fechado); URL de destino montada no servidor.
- **Navegação** (FR-040 a FR-045; SC-005): toda tela nova tem uma tarefa que liga a chegada (menu,
  aba, bloco, linha, botão, sino ou e-mail) e a volta; a matriz "Navegação por tela" no fim deste
  arquivo aponta a tarefa de cada uma e é conferida em T059.
- **Design igual ao protótipo de 17/10** (`docs/fonte/prototipo/prototipo_17_10.html`; plan,
  Target Platform): cada template reproduz a estrutura e as classes da função do protótipo indicada
  na tarefa (só o visual; nenhum JavaScript do protótipo). Usar as classes da base da spec 003
  (`btn`, `btn pri`, `btn txt`, `btn perigo`, `cartao`, `dado`, `tabela`, `chip`, `alerta`, `item`,
  `campo`, `vazio`, `pg`, `pg-sub`) e as classes acrescentadas em T004. Ícones Material Symbols com
  os mesmos nomes do protótipo. A matriz "Design por tela" no fim deste arquivo é conferida em T060.
- Datas: `django.utils.timezone.now()` (`USE_TZ = False`); data de hoje por
  `timezone.now().date()` (nunca `timezone.localdate()`).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: textos, esqueleto dos módulos, base visual e script de seção.

- [X] T001 [P] Acrescentar em `sigtcc/apps/cadastro/mensagens.py` (seção "spec 006"), copiando caractere por caractere das US: "Pedido enviado a {docente}. Aguardando resposta", "Pedido recusado", "Convite aceito", "Convite recusado", "Ata registrada", "A Data do Encontro não pode ser futura", "TCC indicado como apto para defesa", "Confirmar que o TCC de {nome} está apto para defesa?", "A entrega do tipo Documento para Defesa precisa ser cadastrada pelo Professor da Disciplina", "Este e-mail já está registrado como coorientador", "Publicação salva", "Aproveitamento homologado", "Aproveitamento recusado", "Proposta ainda não registrada", "Sem orientador", "Sem Proposta", "Este pedido não está disponível para o seu usuário", "Este convite não está disponível para o seu usuário", "Este pedido foi cancelado pelo aluno", "Este convite foi cancelado pelo aluno", "Este pedido foi cancelado porque a defesa foi agendada"; e as PROVISÓRIAS MO-01 a MO-26 com o texto exato da tabela "Mensagens a validar com a PO" da spec (MO-15 com a concordância corrigida; MO-21 "O resultado já foi liberado: a homologação deste artigo não pode mais ser recusada."; MO-26 com as formas de link e de notificação). Reaproveitar sem duplicar `LINK_HTTPS_500`, `CAMPO_OBRIGATORIO`, `MT25_TURMA_ARQUIVADA` (MT-25) e `M02_ACESSO_NEGADO` (M-02). — Rastreabilidade: [US-17][US-18][US-19][US-20][US-36][US-41][US-42][US-45][US-46][FR-048][SC-003]
- [X] T002 [P] Criar vazios, cada um com a docstring do módulo citando as US que atende (research R1): `sigtcc/apps/cadastro/services_orientacao.py`, `services_atas.py`, `services_artigos.py`, `forms_orientacao.py`, `forms_atas.py`, `forms_artigos.py`, `views_orientacao.py`, `views_atas.py`, `views_artigos.py`, `views_painel.py`. — Rastreabilidade: [research R1][plan.md, Project Structure]
- [X] T003 [P] Criar os diretórios `sigtcc/templates/cadastro/orientacao/` e os templates de e-mail em `sigtcc/templates/cadastro/emails/` (`pedido_orientacao.txt` MO-01, `pedido_troca.txt` MO-16, `convite_coorientacao.txt` MO-07 com os links "Aceitar" e "Recusar" para a rota 13 com `?acao=`, `orientacao_aceita.txt` MO-04), no padrão de `aviso_entrega.txt`, com links absolutos `{{ link }}` montados por `settings.SITE_URL + reverse(...)` (research R11). — Rastreabilidade: [US-17][US-18][US-36][US-45][FR-003][FR-010][FR-033][Q14]
- [X] T004 [P] **Base visual do protótipo** (IC-10): acrescentar em `sigtcc/static/css/sigtcc.css` as regras do protótipo de 17/10 que ainda não existem, copiadas das linhas indicadas de `docs/fonte/prototipo/prototipo_17_10.html` e adaptadas aos nomes da base da spec 003 (`.caixa` → `.cartao`, `.tb` → `.tabela`): `.blocos`, `.bloco`, `.bloco:hover`, `.bloco-cab`, `.bloco-tit`, `.bloco-rod`, `.bloco-ori` (371-380); `.painel`, `.painel-col` (381-382); `.turma-cab`, `.turma-tit`, `.turma-disc`, `.fatos`, `.fato` (314-320); `.sec-tit`, `.sec-tit.c-azul`, `.sec-tit span.cont` (122-124); `.acoes` (133); `.filtros` (268-269); `.ata` (391) e o cabeçalho do `.cartao` com ícone, título e contador (`.caixa>header`, `.caixa>header h3`, `.caixa>header .ms`, `.caixa>header .cont`, 384-387); `.chip.amarelo`, `.chip.vermelho`, `.chip.roxo` (152-154), se faltarem; e a quebra para 360 px do protótipo nessas classes. Não alterar regras existentes. — Rastreabilidade: [FR-017][FR-018][plan.md, Target Platform][IC-10][Q-112]
- [X] T005 [P] Criar `sigtcc/static/js/secao.js`: lê `?secao=` (só `orientacao`, `atas`, `publicacao`) e rola até o elemento com `id` igual; sem o parâmetro ou sem JavaScript, nada acontece (research R12). Incluir o script em `meu_tcc.html` em T018. — Rastreabilidade: [US-17 E1][US-19 E1][US-45 E1][US-46 E1][FR-042][research R12]

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: fábricas de teste, vínculo e permissões, instante do evento e motivo do cancelamento,
e as mudanças de travas e de e-mail em código de outras specs (IC-04, IC-12, IC-13, IC-14).

**⚠️ CRITICAL**: nenhuma história começa antes desta fase.

- [X] T006 [P] Criar `sigtcc/apps/cadastro/tests/apoio_orientacao.py` sobre `apoio_turmas` e `apoio_tcc`: `criar_pedido(tcc, docente, tipo=ORIENTACAO)`, `criar_convite(tcc, docente)`, `vincular_orientador(tcc, docente, origem=PEDIDO_ACEITO)`, `vincular_coorientador(tcc, docente=None, externo=None)`, `criar_externo(nome, email=None, instituicao=None)`, `registrar_ata(tcc, data, pauta, metas)`, `comentar(ata, usuario, texto)`, `salvar_artigo(tcc, link, qualis=None, status=None, homologacao=None)`, `liberar_resultado(tcc, autor)` (gatilho `LIBERACAO_DO_RESULTADO` por `atualizar_status_tcc`), `agendar_defesa(tcc)` (`Defesas` 'Agendada' + `Historico_Defesas` 'Agendamento' com um `agora` devolvido). — Rastreabilidade: [infraestrutura de teste da feature 006]
- [X] T007 Em `services_orientacao.py` (research R6, R10; contrato §1 e §2): `orientador_atual(tcc)`, `coorientadores_ativos(tcc)`, `papeis_no_tcc(usuario, tcc) -> set[str]` (`aluno`, `orientador`, `coorientador`, `professor`, só por vínculo ativo; o Professor da Disciplina de turma com orientador automático tem `{"professor","orientador"}`), `e_orientador_atual`, `e_coorientador_ativo`, `tcc_copiado(tcc)`, `tcc_de_origem(tcc2)`, `pode_alterar_no_tcc(tcc)` (turma não arquivada, participação não encerrada, TCC não copiado) e `link_da_solicitacao(sol)` (rota 12 para Orientação e Troca de Orientação, rota 13 para Coorientação). Testes antes, em `sigtcc/apps/cadastro/tests/test_permissoes_orientacao.py` (seção "vínculo"): cada papel, conjunto vazio sem vínculo, orientador automático com dois papéis, ex-orientador sem papel (Q10), convite pendente sem papel (US-19 #16), TCC copiado. — Rastreabilidade: [US-18][US-19][US-36][RBN-CAD-10.4][RBN-CAD-11.2][FR-007][FR-023][FR-046][Q6][Q10]
- [X] T008 **IC-04 + IC-12 (parte `notificar`)**, em `sigtcc/apps/cadastro/services_turmas.py` e `services.py`: (a) `_registrar_historico`, `atualizar_status_tcc`, `criar_tcc_com_historico` e `_criar_orientacao_automatica` ganham `agora=None`; (b) `encerrar_participacao`, `transferir` e `_copiar_tcc_aprovado` calculam `agora` uma vez e passam o mesmo objeto ao histórico, aos cancelamentos (`sol_data_resposta`) e à orientação; (c) `_copiar_tcc_aprovado` passa a travar o TCC 1 (`select_for_update`, depois do aluno) e a cancelar os pedidos e convites pendentes do TCC 1, notificando cada docente com a MO-18 (link `orientacoes`) dentro da transação (import de `services_orientacao` dentro da função); (d) `services.notificar(usuario, mensagem, link=None, agora=None)`. As notificações MT-31 e MT-22 não mudam (Q18). Rodar `test_us08_*`, `test_us09_*`, `test_us14_*`, `test_notificar` sem alteração. Testes novos, antes, em `sigtcc/apps/cadastro/tests/test_us08_transferencia.py` (seção "spec 006"): a cópia para o TCC 2 cancela os pedidos e convites pendentes do TCC 1 com `sol_data_resposta` igual ao `hst_data_hora` do gatilho "Transferência para TCC 2"; cada docente recebe a MO-18 com link `orientacoes`; o TCC 1 é travado (a cópia espera um `select_for_update` concorrente no TCC 1, `TransactionTestCase`); `notificar(..., agora=X)` grava `not_data_hora == X` (em `test_notificar.py`). — Rastreabilidade: [US-08][US-09][FR-050][FR-051][Q6][Q7][Q18][IC-04][IC-12][Q-106][Q-114]
- [X] T009 Motivo do cancelamento e arquivamento (**IC-12**): em `services_orientacao.py`, `MotivoCancelamento` (`AGENDAMENTO`, `ENCERRAMENTO`, `DOCENTE_VIROU_ORIENTADOR`, `COPIA_TCC_2`, `TURMA_ARQUIVADA`, `ALUNO`), `motivo_do_cancelamento(sol)` com as 6 consultas fixas do research R3 na ordem do FR-050 (5: `Notificacoes(not_usu=sol.sol_doc, not_link_tela=link_da_solicitacao(sol), not_data_hora=X)`), `texto_do_cancelamento(sol)` (texto de pedido ou de convite) e `cancelar_pendentes_da_turma(turma, agora)` (marca 'Cancelado' com `sol_data_resposta=agora` e grava a MO-26 com `notificar(..., link_da_solicitacao(sol), agora=agora)`); em `services_turmas.arquivar_turma`, depois de `motivo_para_nao_arquivar` e na mesma transação, travar todos os alunos e depois todos os TCCs da turma (por `pk`) e chamar a função (import dentro da função). Testes antes: `sigtcc/apps/cadastro/tests/test_motivo_cancelamento.py` com **relógio real** (um teste por motivo conferindo a igualdade gravada; teste negativo "aluno cancela, depois o evento acontece → ALUNO" para cada evento; contraexemplo do research R3: convite a P no TCC 1 e orientação automática de P no TCC 2 → `COPIA_TCC_2`; aluno cancela antes do arquivamento → `ALUNO`) e `sigtcc/apps/cadastro/tests/test_arquivamento_pendentes.py` (pendentes cancelados com o mesmo instante; MO-26 com `not_link_tela == link_da_solicitacao(sol)`; `test_us07_turmas` continua). — Rastreabilidade: [US-07][US-18 E3][US-36 E3][RBN-CAD-04.5][FR-050][FR-053][Q7][Q17][IC-12][Q-114]
- [X] T010 [P] **IC-13**: em `sigtcc/apps/cadastro/services.py`, `enviar_email_apos_commit(usuario, assunto, template, contexto)` extraído de `services_entregas._enviar_email_ao_aluno` (mesma regra de `SIGTCC_EMAIL_SINCRONO` e thread; só envia se houver `usu_email`; falha só no log), e `_enviar_email_ao_aluno` passa a chamá-lo. `test_us15_envio_entrega`, `test_us43_*` e `test_us44_*` continuam. — Rastreabilidade: [research R11][IC-13][Q-115]
- [X] T011 [P] **IC-14**: em `sigtcc/apps/cadastro/services_entregas.py`, `enviar_entrega` acha a entrega sem trava para saber a turma e trava turma (`Turmas.objects.select_for_update()`, sem exigir turma ativa) → aluno → TCC → entrega (relida travada); regras de envio inalteradas (turma arquivada continua 404 por `envio_liberado`). Testes em `test_us15_envio_entrega.py`: os existentes passam; novo "turma arquivada entre o GET e o POST → 404". — Rastreabilidade: [US-15][US-29][research R2][N1][IC-14][Q-116]
- [X] T012 Rodar `python manage.py test sigtcc.apps` (suíte completa das specs 001 a 005 mais os testes da Phase 2) e `makemigrations --check`. — Rastreabilidade: [constituição VIII][SC-006]

**Checkpoint**: base pronta; as histórias podem começar.

---

## Phase 3: User Story 1 - Aluno indica, cancela ou troca o orientador [US-17] (Priority: P1) 🎯 MVP

**Goal**: na aba Meu TCC, o Aluno envia o pedido de orientação, cancela o pedido pendente e pede a
troca de orientador, com o histórico de orientação na seção.

**Independent Test**: aluno matriculado numa turma sem orientador automático; enviar, cancelar,
enviar de novo e, com o aceite simulado por fábrica, conferir a seção Orientação.

### Tests for User Story 1 ⚠️

- [X] T013 [P] [US1] Criar `sigtcc/apps/cadastro/tests/test_us17_pedido_orientacao.py` com os 12 cenários da US-17 (spec, US1 #1 a #12) e os casos: duplo envio (índice `uq_solicitacoes_orientacao_pedido_pendente` → mesmo tratamento), docente inativado entre o GET e o POST (Q-68), e-mail MO-01 só depois do commit (`captureOnCommitCallbacks`), MO-16 no pedido de troca, troca bloqueada por sessão em `STATUS_SESSAO_ATIVA`, `cancelar_troca_no_agendamento(tcc, agora)` (MO-06 ao Aluno e ao docente; `None` sem pedido) e histórico de orientação (FR-049). Deve falhar. — Rastreabilidade: [US-17][RBN-CAD-10.1][RBN-CAD-10.6][FR-001 a FR-008][FR-049]

### Implementation for User Story 1

- [X] T014 [US1] Em `services_orientacao.py`: `contexto_secao_orientacao(aluno, turma, tcc)` (estado da seção: orientador, pedido pendente, listas "Indicar"/"Trocar" habilitadas ou não, orientador automático FR-006, somente leitura FR-007), `enviar_pedido(aluno, tur_id, doc_id)` (travas do R2; tipo Orientação ou Troca de Orientação; MO-01/MO-16 por `notificar` com `link_da_solicitacao` e e-mail após commit), `cancelar_pedido(aluno, tur_id)`, `cancelar_troca_no_agendamento(tcc, agora)` (contrato §3) e `historico_de_orientacao(tcc)` (FR-049). Lista de docentes por `docentes_ativos()` com nome, titulação e curso. — Rastreabilidade: [US-17][RBN-CAD-10.1][RBN-CAD-10.6][FR-001 a FR-008][FR-047][FR-049]
- [X] T015 [US1] Em `forms_orientacao.py`: `PedidoOrientacaoForm` (lista de docentes do contexto, excluindo o orientador atual na troca). — Rastreabilidade: [US-17][FR-002][FR-005]
- [X] T016 [US1] Em `views_orientacao.py`: rotas 1 (`enviar_pedido_orientacao`, POST) e 2 (`cancelar_pedido_orientacao`, POST) de `contracts/rotas.md`, só para o próprio Aluno (`turma_do_aluno`, `tcc_do_aluno`); redirecionam para `meu_tcc?secao=orientacao` com a mensagem; `TurmaArquivada` → mesma tela com a MT-25. Rotas em `sigtcc/apps/cadastro/urls.py`. — Rastreabilidade: [US-17][FR-001][FR-004][contracts/rotas.md §1]
- [X] T017 [US1] **Design**: criar `sigtcc/templates/cadastro/tcc/_secao_orientacao.html` reproduzindo `secaoOrientacaoAluno` do protótipo: título `sec-tit c-azul` "Orientação", `item` com avatar e "Orientador", `alerta info` com ícone `hourglass_top` no pedido pendente e botão "Cancelar Pedido", `campo` select "Indicar orientador"/"Trocar de orientador" com `btn pri` "Enviar pedido", subtítulo "Coorientadores" (preenchido em US6) e `<details>` "Histórico de orientação (n)" do `secOrientacao`; parâmetro `somente_leitura` para o painel. Sem regra no template. — Rastreabilidade: [US-17][FR-001][FR-005][FR-006][FR-049][plan.md, Target Platform]
- [X] T018 [US1] **Navegação** (IC-09): em `sigtcc/templates/cadastro/tcc/meu_tcc.html` e `views_tcc.meu_tcc`, incluir `_secao_orientacao.html` com `id="orientacao"`, aceitar `?secao=` (só os 3 valores; outro valor é ignorado), carregar `secao.js` e corrigir o comentário das linhas 8 a 10 (Q-87). Chegada: item "Turmas" do Aluno → turma → aba "Meu TCC" → seção; volta: as ações redirecionam à própria seção. Teste em `sigtcc/apps/cadastro/tests/test_navegacao_orientacao.py`: o aluno chega à seção pela navegação a partir do menu; sem sessão, o login com `next` volta a `meu_tcc?secao=orientacao`. — Rastreabilidade: [US-17 E1][FR-042][IC-09][Q-111][SC-005]

**Checkpoint**: pedido, cancelamento e troca funcionam de ponta a ponta para o Aluno.

---

## Phase 4: User Story 2 - Docente aceita ou recusa pedidos e consulta a tela de orientandos [US-18] (Priority: P1)

**Goal**: o docente abre "Orientações" pelo menu, pelo sino ou pelo e-mail, responde os pedidos, vê
a proposta e acompanha os orientandos, com histórico do Status e "Correções Conferidas".

**Independent Test**: pedido pendente criado por fábrica; aceitar pela tela Orientações e conferir o
vínculo, as notificações e a linha do aluno.

### Tests for User Story 2 ⚠️

- [ ] T019 [P] [US2] Criar `sigtcc/apps/cadastro/tests/test_us18_resposta_orientandos.py` com os 14 cenários da US-18 e os pontos de contato #15 (histórico pela linha; Coorientador sem o link), #16 (Correções Conferidas: só TCC 2 de SI, "Aprovado com Correções", depois do envio; etiqueta MO-13; devolução apaga e o botão volta após o reenvio) e #17 (Resumo no pedido de troca, IC-05). Mais: aceite duplo e aceite de pedido já cancelado (estado atual), aceite de troca com sessão ativa recusado (N20/A20), aceite que encerra a coorientação do novo orientador, convite pendente ao novo orientador cancelado (MO-17), MO-24 nas seções vazias, ordem das linhas (turma arquivada no fim, US-18 G), página do link com cada motivo (MO-12, MO-18, MO-26, agendamento, aluno) e a mesma resposta para `sol_id` inexistente, de outro tipo ou de outro docente (R4), `assertNumQueries` constante com 1 e 10 orientandos (R14). Deve falhar. — Rastreabilidade: [US-18][US-14 A][US-44 B][RBN-CAD-10.2][RBN-CAD-11.4][FR-009 a FR-016][FR-040]

### Implementation for User Story 2

- [ ] T020 [US2] **IC-05**: em `sigtcc/apps/cadastro/services_tcc.py`, `pode_ver_resumo` aceita também `TipoSolicitacao.TROCA_DE_ORIENTACAO` pendente; + 1 teste em `test_permissoes_tcc.py`. — Rastreabilidade: [US-18][FR-013][IC-05][Q-107]
- [ ] T021 [US2] Em `services_orientacao.py`: `pedidos_pendentes(docente)`, `orientandos(docente)` (só vínculos ativos, turma arquivada no fim, sem N+1 conforme R14, com as decisões de botão por linha), `estado_da_solicitacao(docente, sol_id, tipos)` (ordem do R4: mesma resposta para inexistente, outro tipo ou outro docente; estado pendente, decidido ou cancelado com `texto_do_cancelamento`), `aceitar_solicitacao(docente, sol_id)` e `recusar_solicitacao(docente, sol_id)` para pedidos (travas do R2; reconferência; no aceite de troca: encerra a orientação anterior com o mesmo `agora`, encerra a coorientação do novo orientador, cancela o convite pendente a ele com o mesmo `agora`, reconfere a sessão; MO-02, MO-04 com e-mail, MO-05, MO-03). — Rastreabilidade: [US-18][US-17 D][RBN-CAD-10.2][RBN-CAD-10.6][RBN-CAD-11.4][FR-009 a FR-012][FR-014][FR-015][FR-050]
- [ ] T022 [US2] **R15 + IC-07**: em `services_orientacao.py`, `conferir_correcoes(orientador, tcc_id)` (trava turma → aluno → TCC → `versao_final_do_aluno(..., travar=True)`; confere `exige_correcoes_conferidas`, "Aprovado com Correções", envio em `STATUS_ENVIO_AVALIAVEL`, ainda não conferida); em `services_entregas.devolver_versao_final`, gravar `ent_correcoes_conferidas_em=None` (+ 1 teste em `test_us44_homologacao.py`). — Rastreabilidade: [US-18 #16][US-44 B e D][RBN-CAD-09.5][FR-016][Q2][IC-07][Q-109]
- [ ] T023 [US2] Em `views_orientacao.py`: rotas 11 (`orientacoes`), 12 (`pedido_orientacao`, `?acao=` só destaca), 14 (`aceitar_solicitacao`), 15 (`recusar_solicitacao`), 16 (`ver_proposta`, Resumo por `pode_ver_resumo`, palavras por `palavras_chave_do`), 21 (`historico_orientando`, só `e_orientador_atual`; turma arquivada → 404) e 24 (`correcoes_conferidas`, GET de confirmação MO-13 e POST), com `perfil_requerido("docente")`. **IC-06**: mover `views_tcc._contexto_historico` para `services_tcc.contexto_historico(tcc, url_voltar)` (monta `turma = tcc.tcc_tur`), usada por `historico_status` (volta ao painel), `historico_status_aluno` (volta a Meu TCC) e pela rota 21 (volta a `orientacoes`); botão "Fechar" em `historico_status.html`. Rotas em `urls.py`. — Rastreabilidade: [US-18][US-14 A e B][FR-009 a FR-016][FR-043][IC-06][Q-108][contracts/rotas.md §2]
- [ ] T024 [US2] **Design**: criar `sigtcc/templates/cadastro/orientacao/orientacoes.html` reproduzindo `viewOrientacoes`: `h2.pg` "Orientações"; aviso de estado no topo em `alerta` (FR-012); `sec-tit c-azul` "Pedidos de orientação" com `item` (avatar, "aluno — título", turma, data e hora, orientador atual na troca) e `acoes` com `btn txt` "Ver proposta", `btn perigo` "Recusar" e `btn pri` "Aceitar"; `sec-tit c-azul` "Convites de coorientação" (preenchido em US7); a tela de orientandos em `tabela-wrap` + `tabela` com as colunas Nome do Aluno, Curso, Turma, Título, Modalidade, Papel, Status do TCC, Status das entregas e Atas e ações (`btn txt` "Atas (n)", "Registrar ata", "Histórico", "Publicação"; `btn` "Apto para Defesa"; `btn pri` "Correções Conferidas"; etiquetas `chip`); seções vazias com MO-24 em `vazio`. Criar `orientacao/ver_proposta.html` (janela com os campos em `dado`, botão "Fechar") e `orientacao/confirmar.html` (confirmação genérica: título, texto, `url_acao`, `url_cancelar`, botões "Cancelar" e "Confirmar", no padrão do modal do protótipo). — Rastreabilidade: [US-18][FR-009][FR-014][FR-015][FR-040][plan.md, Target Platform]
- [ ] T025 [US2] **Navegação** (IC-01): em `sigtcc/apps/cadastro/menu.py`, item "Orientações" (`supervisor_account`, perfis `("docente",)`, ordem 12, sem seção). Chegadas: menu → rota 11; sino e e-mail (MO-01, MO-16) → rota 12 por `link_da_solicitacao`; "Ver proposta" e "Fechar" ↔ rota 11; "Histórico" da linha → rota 21 → "Fechar" → rota 11; "Correções Conferidas" → confirmação → rota 11. Testes em `test_navegacao_orientacao.py` e `test_base_comum.py` (IC-11): item no menu para todo Docente (Q11) e para ninguém mais; cada link e cada volta acima; login com `next` no link do pedido (US-18 #10). — Rastreabilidade: [US-18][FR-040][FR-043][FR-052][Q11][IC-01][Q-103][SC-005]

**Checkpoint**: o docente responde pedidos e acompanha os orientandos; US1 e US2 juntas entregam o
vínculo de orientação.

---

## Phase 5: User Story 3 - Professor da Disciplina vê os alunos da turma e o painel de cada aluno [US-41] (Priority: P1)

**Goal**: a aba "Alunos" vira blocos de consulta e o painel do aluno reúne as seções e as ações das
specs 003 a 006, com volta ao painel.

**Independent Test**: turma com 3 alunos (um sem orientador, um sem Proposta); abrir a aba e o
painel, conferir seções, botões e voltas.

### Tests for User Story 3 ⚠️

- [ ] T026 [P] [US3] Criar `sigtcc/apps/cadastro/tests/test_us41_painel_aluno.py` com os 7 cenários da US-41 e os pontos de contato #8 (Secretaria: blocos sem painel, "Transferir aluno") e #9 (Encerrar participação → volta ao painel ao confirmar e ao cancelar). Mais: `alu_id` sem vínculo com a turma → 404 (`vinculo_na_turma`); Secretaria, outro Docente e Aluno → 403 (FR-020); turma arquivada sem botões, inclusive sem "Resetar primeiro acesso" (FR-019); `?volta=` com outro valor ignorado (sem redirecionamento aberto); redirecionamentos de erro com `volta=painel` (MT-19, aluno com proposta, turma arquivada; IC-03); `assertNumQueries` na aba com 1 e 10 alunos e no painel com 1 e 5 entregas (R14). Deve falhar. — Rastreabilidade: [US-41][US-08 C e D][US-09][US-12][US-44][RBN-CAD-08.9][RBN-CAD-10.5][FR-017 a FR-020][FR-044]

### Implementation for User Story 3

- [ ] T027 [US3] **IC-02 (service)**: em `services_turmas.alunos_da_turma`, resolver o curso por um dicionário de `Cursos` carregado uma vez e acrescentar título, área e orientador ativo sem consulta por linha (R14). Em `views_painel.py`, `painel_aluno` (rota 25: `turma_para(CONSULTAR)`, `tur_doc_id == usuario`, `vinculo_na_turma`, `tcc_do_aluno`) montando o contexto das 7 seções com os services das specs 003 a 006 (Resumo por `pode_ver_resumo`; Entregas por `status_exibido` e `link_mais_recente` pré-carregados; Defesa com MO-23) e os botões da US-41 conforme a regra de cada spec (`pode_resetar_primeiro_acesso` **e** turma não arquivada). Rota em `urls.py`. — Rastreabilidade: [US-41][RBN-CAD-08.9][FR-017 a FR-020][IC-02][Q-104]
- [ ] T028 [US3] **IC-03, IC-07 e IC-08 (volta ao painel)**: em `sigtcc/apps/cadastro/views_turmas.py` (`aluno_editar`, `aluno_encerrar`, `aluno_excluir`, `aluno_transferir`) e nos templates `turmas/editar_aluno.html`, `encerrar.html`, `excluir_aluno.html`, `transferir.html`, aceitar `?volta=painel` (campo oculto no POST): "Cancelar", fim e erros voltam ao painel; Excluir e Transferir confirmados voltam à aba "Alunos". Em `views_entregas.aluno_versao_final` e `homologar_versao_final.html`, o mesmo. Em `views.py` (spec 003): `aluno` redireciona ao painel da turma mais recente (não arquivada primeiro, depois `tur_ano`, `tur_semestre`, `tur_id` decrescentes; sem turma, 403); `resetar_primeiro_acesso` e o "Cancelar" de `confirmar_reset.html` redirecionam para `cadastro:aluno`; remover `templates/cadastro/aluno.html`. Ajustar `test_us09_exclusao.py:174`, `test_us12_senha.py` e `test_seguranca.py:152` (IC-11). — Rastreabilidade: [US-41 C][US-08][US-09][US-12][US-44][FR-044][Q12][IC-03][IC-07][IC-08][IC-11][Q-105][Q-109][Q-110][Q-113]
- [ ] T029 [US3] **Design**: (a) em `sigtcc/templates/cadastro/turmas/turma.html` (IC-02), trocar a tabela da aba "Alunos" por `div.blocos` com um `.bloco` por aluno, como `blocoAluno` do protótipo (avatar, nome, "matrícula · curso", título ou "Sem Proposta", "Área de Interesse", `bloco-ori` com ícone `supervisor_account` e orientador ou "Sem orientador", `chip` do Status); para o Professor o bloco é link para o painel; para a Secretaria, bloco sem link e `btn` "Transferir aluno" quando permitido; ações da turma inalteradas; (b) criar `sigtcc/templates/cadastro/turmas/painel_aluno.html` como `viewAlunoTurma`: `btn txt` com `arrow_back` "turma · identificador" (volta à aba), cabeçalho `turma-cab` com avatar, nome, `chip` do Status, `fatos` (Matrícula, Curso, E-mail Institucional) e os botões de ação (`edit` "Editar aluno", `lock_reset` "Resetar primeiro acesso", `swap_horiz` "Transferir aluno", `block` "Encerrar participação" em `btn perigo`, `person_remove` "Excluir aluno"); `div.painel` com duas `painel-col` e as seções em `cartao` com ícone (Proposta e TCC `description` com o link `history` "Histórico do Status do TCC"; Entregas `assignment`; Atas `history_edu`; Publicação `article`; Orientação `supervisor_account` pelo include de T017 com `somente_leitura`; Defesa `gavel`; Versão Final com "Homologar" e "Devolver para Ajuste"); botão "Fechar". — Rastreabilidade: [US-41][FR-017][FR-018][FR-019][plan.md, Target Platform][IC-02][Q-104]
- [ ] T030 [US3] **Navegação**: chegada pelo item "Turmas" (ou botão "Turmas arquivadas") → turma → aba "Alunos" → bloco → painel; cada botão do painel → tela de ação com `?volta=painel` → volta ao painel; link de histórico → `historico_status` → "Fechar" → painel; "Fechar" do painel → aba "Alunos"; endereço antigo `alunos/<id>/` → painel. Testes em `test_navegacao_orientacao.py` para cada chegada e volta; ajustar `test_navegacao_tcc.py:177` e `test_us08_transferencia.py:190` ("Transferir aluno" no bloco) (IC-11). — Rastreabilidade: [US-41 C][FR-044][FR-045][IC-11][Q-113][SC-005]

**Checkpoint**: o Professor da Disciplina acompanha a turma pelo painel; nenhuma ação das specs 003
a 005 perdeu o caminho.

---

## Phase 6: User Story 4 - Aluno, Orientador e Coorientador registram, consultam, editam e comentam atas [US-19] (Priority: P1)

**Goal**: atas pela aba Meu TCC (Aluno), pela linha da tela de orientandos (Orientador e
Coorientador) e pelo painel (Professor, só leitura), com comentários.

**Independent Test**: registrar uma ata como Aluno e outra como Orientador, comentar, editar e
conferir ordem e visibilidade.

### Tests for User Story 4 ⚠️

- [ ] T031 [P] [US4] Criar `sigtcc/apps/cadastro/tests/test_us19_atas.py` com os 16 cenários da US-19. Mais: troca de `enc_id` por ata de outro TCC → 404 em cada rota com `enc_id` (Aluno e Docente); atas do TCC 1 na lista do TCC 2 só para consulta e nunca editáveis pela rota do TCC 2 (Q6); ex-orientador sem acesso (Q10); limites `enc_pauta` e `enc_metas` "obrigatórias, até 2.000 caracteres" e comentário "até 1.000 caracteres" (MO-19); data de hoje aceita, amanhã recusada; mesma Data do Encontro → a última registrada primeiro (D14); turma arquivada: rota 17 só leitura, GET das 18 a 20 volta à 17 com a MT-25, POST recusado. Deve falhar. — Rastreabilidade: [US-19][RBN-CAD-11.1][RBN-CAD-11.2][FR-021 a FR-025][Q6][Q10][D14]

### Implementation for User Story 4

- [ ] T032 [US4] Em `services_atas.py`: `atas_do_tcc(tcc)` (ordem `enc_data` desc, `enc_id` desc; comentários com autor, data e hora; atas do TCC de origem à parte), `pode_ver_atas(usuario, tcc)`, `registrar_ata(usuario, tcc, dados)`, `editar_ata(usuario, tcc, enc_id, dados)` (busca `enc_tcc=tcc`), `comentar_ata(docente, tcc, enc_id, texto)` (só Orientador ou Coorientador ativo), todas com travas do R2 e `pode_alterar_no_tcc`. — Rastreabilidade: [US-19][RBN-CAD-11.1][RBN-CAD-11.2][FR-021 a FR-025]
- [ ] T033 [US4] Em `forms_atas.py`: `AtaForm` (`enc_data` obrigatória, DD/MM/AAAA, "não futura" comparada com `timezone.now().date()`; `enc_pauta` e `enc_metas` obrigatórias, "até 2.000 caracteres", MO-19) e `ComentarioForm` (`com_texto` obrigatório, "até 1.000 caracteres", MO-19). — Rastreabilidade: [US-19][FR-021][FR-024][data-model.md §1]
- [ ] T034 [US4] Em `views_atas.py`: rotas 7, 8, 9 (Aluno, prefixo `turmas/<tur_id>/meu-tcc/`), 17, 18, 19, 20 (Docente, `orientacoes/tcc/<tcc_id>/`, por `e_orientador_atual` ou `e_coorientador_ativo`) e 26 (`atas_painel`, Professor, mesmas checagens do painel). Rotas em `urls.py`. — Rastreabilidade: [US-19][FR-022 a FR-025][contracts/rotas.md §1 a §3]
- [ ] T035 [US4] **Design**: criar `sigtcc/templates/cadastro/tcc/_secao_atas.html` (como a seção de atas de `viewMeuTcc`: `sec-tit c-azul` "Atas de orientação" com `span.cont` "n encontro(s)", `btn` com `add` "Registrar ata" e `btn txt` "Ver atas"), `orientacao/atas.html` (como `secAtas`: cada `.ata` com a data em negrito, `dado` "Pauta Discutida" e "Metas Acordadas", comentários em `alerta info` com ícone `comment` e "autor · data e hora", `btn txt` "Editar" e "Comentar" conforme o papel; bloco "Atas do TCC 1" abaixo, identificado pela turma; "Voltar") e `orientacao/form_ata.html` (janela "Registrar ata de orientação": Data do Encontro, Pauta Discutida, Metas Acordadas com contador, "Cancelar" e "Salvar"; mesma janela para editar; campo de comentário abaixo da ata na rota 20). — Rastreabilidade: [US-19][FR-021 a FR-024][plan.md, Target Platform]
- [ ] T036 [US4] **Navegação**: Aluno: Meu TCC → seção Atas (`id="atas"`, `?secao=atas`) → "Registrar ata" → janela → "Cancelar"/"Salvar" → seção; "Ver atas" → lista → "Editar" → formulário → lista; "Voltar" → seção. Docente: Orientações → linha → "Atas (n)" → lista → "Editar"/"Comentar" → lista → "Voltar" → Orientações; linha → "Registrar ata" → janela → Orientações. Professor: painel → seção Atas → "Ver atas" → lista só leitura → "Voltar" → painel. Incluir `_secao_atas.html` em `meu_tcc.html` e no painel (T029). Testes em `test_navegacao_orientacao.py` para cada caminho. — Rastreabilidade: [US-19][FR-042][FR-043][FR-044][SC-005]

**Checkpoint**: atas completas para os quatro papéis.

---

## Phase 7: User Story 5 - Orientador indica que o TCC está apto para defesa [US-42] (Priority: P1)

**Goal**: botão "Apto para Defesa" na linha do Orientador, com confirmação e mudança de Status pelo
serviço único.

**Independent Test**: TCC "Em Andamento" com "Documento para Defesa" entregue e Área e
Palavra-Chave; indicar Apto e conferir Status e histórico.

### Tests for User Story 5 ⚠️

- [ ] T037 [P] [US5] Criar `sigtcc/apps/cadastro/tests/test_us42_apto_defesa.py` com os 8 cenários da US-42. Mais: condição mudada entre o GET e o POST → MO-20 sem mudar o Status; Coorientador recebe 404 na rota 23; turma arquivada → 404; orientador automático (Professor da Disciplina) vê e usa o botão (R10). Deve falhar. — Rastreabilidade: [US-42][RBN-CAD-11.5][RBN-CAD-08.3][FR-026][FR-027][SC-007]

### Implementation for User Story 5

- [ ] T038 [US5] Em `services_orientacao.py`: `estado_apto(tcc)` (ausente, `sem_entrega_cadastrada`, `indisponivel`, `disponivel`; entrega por `Turmas_Marcos.tma_tipo = DOCUMENTO_PARA_DEFESA`; envio em `STATUS_ENVIO_AVALIAVEL`) e `indicar_apto(orientador, tcc_id)` (travas do R2; reconfere; `atualizar_status_tcc(tcc, turma, orientador, APTO_PARA_DEFESA, INDICACAO_DE_APTO)`). — Rastreabilidade: [US-42][RBN-CAD-11.5][FR-026][FR-027]
- [ ] T039 [US5] Em `views_orientacao.py`: rota 23 (`indicar_apto`, GET com `orientacao/confirmar.html` e o texto "Confirmar que o TCC de {nome} está apto para defesa?"; POST). Na linha (T024): `btn` "Apto para Defesa" desabilitado com `title` da US-42 E3 quando indisponível e etiqueta `chip` "Apto para Defesa" depois. **Navegação**: Orientações → linha → "Apto para Defesa" → confirmação → "Cancelar"/"Confirmar" → Orientações; teste em `test_navegacao_orientacao.py`. — Rastreabilidade: [US-42][FR-026][FR-027][FR-043][SC-005]

**Checkpoint**: todas as histórias P1 prontas (MVP completo da orientação).

---

## Phase 8: User Story 6 - Aluno registra, substitui ou remove coorientadores [US-45] (Priority: P2)

**Goal**: coorientadores do NUCOMP (por convite) e externos (por registro), com substituir e remover
até o agendamento.

**Independent Test**: com orientador vinculado, registrar um docente e um externo, substituir e
remover, conferindo estados e notificações.

### Tests for User Story 6 ⚠️

- [ ] T040 [P] [US6] Criar `sigtcc/apps/cadastro/tests/test_us45_coorientadores.py` com os 14 cenários da US-45. Mais: troca de `coo_id` e de `sol_id` por outro TCC → 404 (rotas 4, 5, 6); externo com e-mail já cadastrado em outro TCC (maiúsculas diferentes) → reaproveitado, Nome e Instituição mantidos, MO-25 (Q13, Q15); dois cadastros simultâneos do mesmo e-mail → um só externo (R17); "Nome Completo (obrigatório, só letras, acentos e espaços, até 150)", "E-mail (opcional, nome@domínio, até 100)", "Instituição de Origem (opcional, até 150)"; lista de Docentes sem o orientador, os coorientadores e quem já tem convite pendente (D8); 'Substituída' no Substituir e 'Encerrada' no Remover (D8); MO-07 com e-mail, MO-08, MO-09. Deve falhar. — Rastreabilidade: [US-45][RBN-CAD-10.3][RBN-CAD-10.4][RBN-CAD-10.7][FR-028 a FR-030][Q13][Q15][D8]

### Implementation for User Story 6

- [ ] T041 [US6] Em `services_orientacao.py`: `docentes_para_coorientacao(tcc)`, `registrar_coorientador(aluno, tur_id, dados)` (docente: convite 'Aguardando Aceite' com `travar_e_conferir_ativo`, conferência de convite repetido sob a trava do TCC, MO-07 por `link_da_solicitacao` e e-mail após commit; externo: R17 com `normalizar_email`, `travar_email`, `iexact` + `order_by("cext_id").first()`, criação em savepoint; MO-08), `substituir_coorientador(aluno, tur_id, coo_id, dados)`, `remover_coorientador(aluno, tur_id, coo_id)` e `remover_convite(aluno, tur_id, sol_id)` (bloqueio com sessão em `STATUS_SESSAO_ATIVA`; MO-09). — Rastreabilidade: [US-45][RBN-CAD-10.3][RBN-CAD-10.7][FR-028 a FR-030][research R17]
- [ ] T042 [US6] Em `forms_orientacao.py`: `CoorientadorForm` (Tipo, Docente do NUCOMP ou Nome Completo por `forms_contas.validar_nome_completo`, E-mail, Instituição de Origem, com os limites de T040). Em `views_orientacao.py`: rotas 3, 4, 5 e 6 (`contracts/rotas.md §1`), com confirmação MO-14 por `orientacao/confirmar.html`. Rotas em `urls.py`. — Rastreabilidade: [US-45][FR-028 a FR-030][contracts/rotas.md §1]
- [ ] T043 [US6] **Design + Navegação**: em `_secao_orientacao.html`, a lista "Coorientadores" como no protótipo (`item` com ícone `person` em círculo azul para docente e cinza para externo, "Docente do NUCOMP" ou "Externo ao NUCOMP · instituição", `chip amarelo` "Aguardando aceite", `btn txt` "Substituir"/"Remover"/"Remover convite" ou desabilitados com sessão, `btn` com `person_add` "Registrar coorientador"); criar `orientacao/form_coorientador.html` como a janela de `formCoorientador` (Tipo, caixa do Docente com a dica do convite, caixa do Externo; "Cancelar" e "Salvar"), usada para registrar e substituir. Chegada: Meu TCC → seção Orientação → botão → janela/confirmação → "Cancelar"/"Salvar"/"Confirmar" → seção Orientação. Testes em `test_navegacao_orientacao.py`. — Rastreabilidade: [US-45][FR-028 a FR-030][FR-042][plan.md, Target Platform][SC-005]

**Checkpoint**: o Aluno gerencia coorientadores; os convites aguardam a US7.

---

## Phase 9: User Story 7 - Docente aceita ou recusa o convite de coorientação e acompanha o trabalho [US-36] (Priority: P2)

**Goal**: convites na tela Orientações, resposta na tela (nunca pelo e-mail) e o trabalho na tela de
orientandos com o Papel Coorientador.

**Independent Test**: convite pendente por fábrica; aceitar e recusar, conferindo vínculo,
notificações e linha.

### Tests for User Story 7 ⚠️

- [ ] T044 [P] [US7] Criar `sigtcc/apps/cadastro/tests/test_us36_convite_coorientacao.py` com os 11 cenários da US-36. Mais: botões "Aceitar"/"Recusar" do e-mail (`?acao=`) só destacam, GET nunca grava (Q14); convite cancelado por cada motivo mostra o texto de convite (MO-12, MO-17, MO-18, MO-26); aceite com a conta do docente 'Inativa' recusado (Q-68); linha do Coorientador só com "Atas" e "Registrar ata" (FR-015). Deve falhar. — Rastreabilidade: [US-36][RBN-CAD-10.4][FR-031 a FR-033][Q14][D7]

### Implementation for User Story 7

- [ ] T045 [US7] Em `services_orientacao.py`: `convites_pendentes(docente)` e, em `aceitar_solicitacao`/`recusar_solicitacao`, o ramo Coorientação (cria `Coorientacoes` 'Ativa' com `coo_doc` em savepoint, MO-10 ao Aluno e ao Orientador; recusa com MO-11). Em `views_orientacao.py`: rota 13 (`convite_coorientacao`, mesma view base da rota 12, com `sol_tipo` Coorientação). Rota em `urls.py`. — Rastreabilidade: [US-36][RBN-CAD-10.4][FR-031 a FR-033]
- [ ] T046 [US7] **Design + Navegação**: em `orientacoes.html`, a seção "Convites de coorientação" como no protótipo (`item` com avatar, "aluno — título", "turma · Orientador", `acoes` com `btn perigo` "Recusar" e `btn pri` "Aceitar") e o destaque do convite aberto pelo link. Chegadas: menu "Orientações"; sino e e-mail (MO-07, botões "Aceitar"/"Recusar") → rota 13 → mesma tela. Testes em `test_navegacao_orientacao.py`, inclusive login com `next` (US-36 #7). — Rastreabilidade: [US-36][FR-031][FR-033][FR-040][plan.md, Target Platform][SC-005]

**Checkpoint**: o ciclo de coorientação está completo (US6 + US7).

---

## Phase 10: User Story 8 - Aluno ou Orientador registra a publicação do artigo [US-46] (Priority: P2)

**Goal**: seção "Publicação do artigo" para o Aluno e tela própria para o Orientador, com o ciclo do
aproveitamento.

**Independent Test**: TCC Artigo Científico; salvar como Aluno e como Orientador, conferindo "Em
Análise" com Aceito ou Publicado.

### Tests for User Story 8 ⚠️

- [ ] T047 [P] [US8] Criar `sigtcc/apps/cadastro/tests/test_us46_publicacao.py` com os 8 cenários da US-46. Mais: alteração de Qualis, Status ou Link de artigo Homologado ou Recusado volta a "Em Análise" também **depois** da liberação (Q16); etiqueta MO-22 sem análise; "Link ou DOI obrigatório, `https://`, até 500" com `LINK_HTTPS_500`; "Veículo de Publicação opcional, até 150" (MO-19); Qualis só A1 a A4, B1 a B4, C; Status só Submetido, Em Revisão, Aceito, Publicado, Rejeitado; Monografia esconde a seção sem apagar o registro (D10); rota 22 só para `e_orientador_atual` e 404 com turma arquivada; decisão anterior no log (D10). Deve falhar. — Rastreabilidade: [US-46][RBN-CAD-12.1][RBN-CAD-12.3][FR-034 a FR-036][Q16][D10]

### Implementation for User Story 8

- [ ] T048 [US8] Em `services_artigos.py`: `EventoArtigo` (enum local, como `EventoFluxoTCC`), `salvar_publicacao(usuario, tcc, dados)` (trava turma → aluno → TCC → `Artigos`; ciclo do research R8 sem limite de tempo; `pode_alterar_no_tcc`) e `etiqueta_aproveitamento(artigo)`. Em `forms_artigos.py`: `PublicacaoForm` (validação do Link igual à de `forms_tcc.py`, sem cópia nova da regra). — Rastreabilidade: [US-46][RBN-CAD-12.1][RBN-CAD-12.3][FR-034][FR-036][research R8]
- [ ] T049 [US8] Em `views_artigos.py`: rotas 10 (`salvar_publicacao_aluno`, POST → `meu_tcc?secao=publicacao`) e 22 (`publicacao_orientando`, GET e POST, "Voltar" → `orientacoes`). Rotas em `urls.py`. — Rastreabilidade: [US-46][FR-034][FR-035][contracts/rotas.md §1 e §2]
- [ ] T050 [US8] **Design + Navegação**: criar `sigtcc/templates/cadastro/tcc/_secao_publicacao.html` (como `formPublicacao` e `secPublicacaoPainel`: `sec-tit c-azul` "Publicação do artigo", etiqueta de aproveitamento em `chip`, campos Veículo, Link ou DOI, Estrato Qualis/CAPES e Status de Submissão, `btn pri` "Salvar publicação"; versão só leitura com `dado` e o link "abrir" com `target="_blank" rel="noopener noreferrer"`) e `orientacao/publicacao.html` (tela do Orientador com o mesmo include e "Voltar"). Incluir a seção em `meu_tcc.html` (`id="publicacao"`) e no painel (T029), só em Artigo Científico. Chegadas: Meu TCC → seção (`?secao=publicacao`); Orientações → linha → "Publicação" → tela → "Voltar". Testes em `test_navegacao_orientacao.py`. — Rastreabilidade: [US-46][FR-034][FR-035][FR-042][FR-043][plan.md, Target Platform][SC-005]

**Checkpoint**: publicação registrada; o artigo Aceito ou Publicado aguarda a US9.

---

## Phase 11: User Story 9 - Coordenador de Curso homologa ou recusa o aproveitamento do artigo [US-20] (Priority: P2)

**Goal**: tela "Aproveitamento de artigos" na seção "Gestão" do menu, com filtro Curso e as decisões
do Coordenador do curso.

**Independent Test**: artigos Aceitos de dois cursos; abrir como Coordenador de um deles, homologar
e recusar, conferindo filtro e botões.

### Tests for User Story 9 ⚠️

- [ ] T051 [P] [US9] Criar `sigtcc/apps/cadastro/tests/test_us20_aproveitamento.py` com os 9 cenários da US-20 (nota mínima dos cenários 1 e 3 pela consulta `tem_artigo_homologado_qualis_ab`, SC-004) e os pontos de contato #10 e #11 (Q16). Mais: POST direto em artigo de outro curso, Monografia, Status fora de Aceito/Publicado, TCC copiado ou inexistente → 404 (R9); recusa de Homologado depois da liberação → MO-21; Homologar e Recusar em turma arquivada funcionam (D11; N2); TCC 1 copiado não aparece (só o TCC atual); `?curso=` inválido vira o curso do Coordenador; link "abrir" com `rel="noopener noreferrer"`; eventos `EventoArtigo` no log com autor e `tcc_id`. Deve falhar. — Rastreabilidade: [US-20][RBN-CAD-12.2][RBN-CAD-12.3][RBN-CAD-14.1][RBN-DEF-06.4][FR-037 a FR-039][Q16][D11]

### Implementation for User Story 9

- [ ] T052 [US9] Em `services_artigos.py`: `artigos_para_analise(coordenador, curso)` (Aceito ou Publicado, Artigo Científico, `tcc_copiado` falso; filtro pelo `tcc_tur.tur_cur`; curso inicial por `permissoes.curso_id_do_usuario`), `homologar_artigo` e `recusar_artigo` (turma por `select_for_update` sem exigir ativa → aluno → TCC → `Artigos`; validações do R9 depois da trava; `registrar_evento(EventoArtigo...)` após o commit), `resultado_liberado(tcc)` e `tem_artigo_homologado_qualis_ab(tcc)` (contrato §4). — Rastreabilidade: [US-20][RBN-CAD-12.2][RBN-CAD-12.3][FR-037 a FR-039][research R7][research R9]
- [ ] T053 [US9] Em `views_artigos.py`: rotas 27 (`aproveitamento_artigos`, `?curso=` validado contra `Cursos`), 28 (`homologar_artigo`) e 29 (`recusar_artigo`), com `perfil_requerido("coordenador")`, voltando a `artigos/?curso=` com a mensagem. Rotas em `urls.py`. — Rastreabilidade: [US-20][FR-037][FR-038][contracts/rotas.md §4]
- [ ] T054 [US9] **Design + Navegação**: criar `sigtcc/templates/cadastro/orientacao/aproveitamento.html` como `viewArtigos`: `h2.pg` "Aproveitamento de artigos", `p.pg-sub` com o texto do protótipo sobre a nota mínima, `filtros` com o select Curso (3 cursos e Todos), `tabela` com Aluno, Orientador, Título do TCC, Veículo de Publicação, Estrato Qualis/CAPES, Link ou DOI ("abrir"), Aproveitamento (`chip`) e `acoes` com `btn pri` "Homologar" e `btn perigo` "Recusar" (sem botões nos outros cursos; "Recusar" indisponível no Homologado depois da liberação); tabela vazia em `vazio`. Em `menu.py` (IC-01): "Aproveitamento de artigos" (`article`, perfis `("coordenador",)`, ordem 30, `secao: "Gestão"`). Testes em `test_navegacao_orientacao.py` e `test_base_comum.py`: item só para o Coordenador (US-20 E4), seção "Gestão" depois de "Cadastros" (R19), login com `next` (US-20 #6). — Rastreabilidade: [US-20][FR-037][FR-038][FR-041][IC-01][Q-103][plan.md, Target Platform][SC-005]

**Checkpoint**: todas as histórias entregues.

---

## Phase 12: Polish & Cross-Cutting Concerns

- [ ] T055 [P] Criar `sigtcc/apps/cadastro/tests/test_mensagens_orientacao.py` no padrão de `test_mensagens_tcc.py`: cada constante da spec 006 em `mensagens.py` é igual ao texto da US (lido de `docs/fonte/Historias_de_Usuario_v3_3.md`) ou à tabela MO-01 a MO-26 da spec. — Rastreabilidade: [FR-048][SC-003]
- [ ] T056 [P] Completar `sigtcc/apps/cadastro/tests/test_permissoes_orientacao.py`: uma linha por rota 1 a 29 com sem sessão (login), perfil errado (403), sem vínculo (404), troca de cada ID (404), turma arquivada (MT-25 ou 404 conforme `contracts/rotas.md`) e CSRF obrigatório nos POST; nenhum GET grava. — Rastreabilidade: [FR-046][SC-006][contracts/rotas.md]
- [ ] T057 [P] Concorrência em `sigtcc/apps/cadastro/tests/test_permissoes_orientacao.py` (seção "concorrência", `TransactionTestCase`): dois aceites do mesmo pedido; aceite × cancelamento pelo aluno; dois convites ao mesmo docente; dois externos com o mesmo e-mail; Correções Conferidas × reenvio da Versão Final (IC-14); arquivamento × aceite. Nenhum deadlock nem 500. — Rastreabilidade: [FR-047][research R2][N1]
- [ ] T058 Rodar `lint.bat` (isort, black 100, flake8 100), `python manage.py makemigrations --check` e `python manage.py test sigtcc.apps` (suíte completa). Registrar as contagens. — Rastreabilidade: [constituição V][constituição VIII]
- [ ] T059 **Navegação (SC-005)**: em `test_navegacao_orientacao.py`, um teste que percorre a matriz "Navegação por tela" abaixo, partindo do menu de cada perfil e seguindo só links e botões renderizados (sem montar URL à mão, exceto o endereço antigo da rota `aluno`), até cada tela, e volta pelo botão de volta indicado. No mesmo arquivo, um teste por linha da tabela do FR-052 (e de `contracts/rotas.md` §5): dispara a ação que gera a notificação (MO-01 a MO-11, MO-16, MO-18, MO-26) e confere o destinatário e o `not_link_tela` (rota 12 ou 13 por `link_da_solicitacao`, `meu_tcc?secao=orientacao`, `orientacoes` ou `painel_aluno`); confere também que o encerramento e a transferência continuam com a MT-31 e a MT-22 (Q18). — Rastreabilidade: [FR-040 a FR-045][FR-052][SC-005]
- [ ] T060 **Design (protótipo)**: criar `.claude/launch.json` (configuração `sigtcc`: `runtimeExecutable` `.venv\Scripts\python.exe`, `runtimeArgs` `["manage.py", "runserver", "8000"]`, `port` 8000), subir o servidor por ele, abrir cada tela da matriz "Design por tela" no navegador em 1280 px e em 360 px, lado a lado com a função do protótipo (`docs/fonte/prototipo/prototipo_17_10.html`), e conferir: estrutura e ordem das seções, classes, ícones Material Symbols, rótulos dos botões, cores dos `chip` e dos botões (`pri`, `perigo`, `txt`), fontes Roboto/Figtree. Corrigir divergências nos templates ou em `sigtcc.css` (T004). Registrar o resultado, com capturas, na seção "Conferência visual" no fim deste arquivo. — Rastreabilidade: [plan.md, Target Platform][constituição VII]
- [ ] T061 Executar o roteiro de [quickstart.md](quickstart.md) (23 passos) pela navegação e registrar o resultado neste arquivo. — Rastreabilidade: [SC-001][SC-002][SC-005]
- [ ] T062 Atualizar `docs/questoes-a-rever.md` com o que a implementação tiver confirmado ou mudado (Q-95 a Q-117), seguindo "Como usar"; rodar o agente `revisor-pgcs` e preparar o texto do PR `[Feat-06] Orientação, Atas e Publicações (US-17, US-18, US-19, US-20, US-36, US-41, US-42, US-45, US-46)` com o template do PGCS 6.3. — Rastreabilidade: [constituição VIII][PGCS 6.3]

---

## Navegação por tela (conferida em T059)

| Tela | Perfil | Chega por | Volta por | Tarefa |
|---|---|---|---|---|
| Seção Orientação (Meu TCC) | Aluno | Menu "Turmas" → turma → aba "Meu TCC" (`?secao=orientacao`); sino MO-02, MO-03, MO-06, MO-10, MO-11 | é seção da aba | T018 |
| Janela "Registrar coorientador" / Substituir | Aluno | Seção Orientação → "Registrar coorientador" ou "Substituir" | "Cancelar"/"Salvar" → seção | T043 |
| Confirmação Remover coorientador ou convite | Aluno | Seção Orientação → "Remover" | "Cancelar"/"Confirmar" → seção | T043 |
| Seção Atas (Meu TCC) | Aluno | Aba "Meu TCC" (`?secao=atas`) | é seção da aba | T036 |
| Janela "Registrar ata de orientação" (Aluno) | Aluno | Seção Atas → "Registrar ata" | "Cancelar"/"Salvar" → seção | T036 |
| Lista de atas (Aluno) e edição | Aluno | Seção Atas → "Ver atas" → "Editar" | "Voltar" → seção; edição → lista | T036 |
| Seção Publicação do artigo | Aluno | Aba "Meu TCC" (`?secao=publicacao`) | é seção da aba | T050 |
| Histórico do Status (Aluno) | Aluno | Aba "Meu TCC" → link de histórico | "Fechar" → Meu TCC | T023 |
| Orientações (pedidos, convites, orientandos) | Docente | Menu "Orientações" | tela de topo | T025 |
| Orientações com pedido ou convite destacado / aviso de estado | Docente | Sino e e-mail (MO-01, MO-07, MO-16, MO-26) → rota 12 ou 13 | é a própria tela Orientações | T025, T046 |
| Janela "Ver proposta" | Docente | Orientações → pedido → "Ver proposta" | "Fechar" → Orientações | T025 |
| Lista de atas do orientando, edição e comentário | Orientador, Coorientador | Orientações → linha → "Atas (n)" → "Editar"/"Comentar" | "Voltar" → Orientações; edição e comentário → lista | T036 |
| Janela "Registrar ata" (Docente) | Orientador, Coorientador | Orientações → linha → "Registrar ata" | "Cancelar"/"Salvar" → Orientações | T036 |
| Histórico do Status (Orientador) | Orientador | Orientações → linha → "Histórico" | "Fechar" → Orientações | T025 |
| Publicação do orientando | Orientador | Orientações → linha → "Publicação" | "Voltar" → Orientações | T050 |
| Confirmação Apto para Defesa | Orientador | Orientações → linha → "Apto para Defesa" | "Cancelar"/"Confirmar" → Orientações | T039 |
| Confirmação Correções Conferidas | Orientador | Orientações → linha → "Correções Conferidas" | "Cancelar"/"Confirmar" → Orientações | T025 |
| Aba "Alunos" em blocos | Professor, Secretaria | Menu "Turmas" (ou "Turmas arquivadas") → turma | tela da turma | T030 |
| Painel do aluno | Professor | Aba "Alunos" → bloco; sino MO-04; endereço antigo `alunos/<id>/` | "Fechar" → aba "Alunos" | T030 |
| Telas de ação (Editar, Encerrar, Excluir, Transferir, Resetar, Homologar, Devolver) | Professor | Painel → botão (`?volta=painel`) | "Cancelar"/fim → painel; Excluir e Transferir confirmados → aba | T028, T030 |
| Histórico do Status (Professor) | Professor | Painel → link de histórico | "Fechar" → painel | T030 |
| Atas do painel (só leitura) | Professor | Painel → seção Atas → "Ver atas" | "Voltar" → painel | T036 |
| Transferir aluno (Secretaria) | Secretaria | Aba "Alunos" → bloco → "Transferir aluno" | fluxo da spec 004 | T030 |
| Aproveitamento de artigos | Coordenador | Menu, seção "Gestão" → "Aproveitamento de artigos" | tela de topo; decisões voltam a ela com `?curso=` | T054 |

## Design por tela (conferido em T060)

| Tela | Função do protótipo de 17/10 | Template | Tarefa |
|---|---|---|---|
| Seção Orientação e coorientadores | `secaoOrientacaoAluno`, `secOrientacao` | `tcc/_secao_orientacao.html` | T017, T043 |
| Janela de coorientador | `formCoorientador` | `orientacao/form_coorientador.html` | T043 |
| Seção e lista de atas, janela de ata | seção de atas de `viewMeuTcc`, `secAtas`, `formAta` | `tcc/_secao_atas.html`, `orientacao/atas.html`, `orientacao/form_ata.html` | T035 |
| Publicação | `formPublicacao`, `secPublicacaoPainel`, `abrirPublicacao` | `tcc/_secao_publicacao.html`, `orientacao/publicacao.html` | T050 |
| Orientações | `viewOrientacoes` | `orientacao/orientacoes.html` | T024, T046 |
| Ver proposta, confirmações | `fichaTcc` no modal, `confirmar` | `orientacao/ver_proposta.html`, `orientacao/confirmar.html` | T024 |
| Aba "Alunos" | `blocoAluno` | `turmas/turma.html` | T029 |
| Painel do aluno | `viewAlunoTurma` e as `sec*` | `turmas/painel_aluno.html` | T029 |
| Aproveitamento de artigos | `viewArtigos` | `orientacao/aproveitamento.html` | T054 |
| Menu | itens `orientacoes` (`supervisor_account`) e `artigos` (`article`) na seção "Gestão" | `menu.py` | T025, T054 |

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências; T001 a T005 em paralelo.
- **Foundational (Phase 2)**: depende da Phase 1; bloqueia todas as histórias. T007 e T008 antes de T009
  (o motivo usa `link_da_solicitacao` de T007 e o instante do evento de T008); T006, T010 e T011 em paralelo com T007.
- **US1 (Phase 3)** e **US2 (Phase 4)**: dependem só da Phase 2; podem andar em paralelo, mas o
  teste ponta a ponta do pedido precisa das duas.
- **US3 (Phase 5)**: depende da Phase 2 e do include de T017 (seção Orientação no painel).
- **US4 (Phase 6)**: depende de US2 (linha da tela de orientandos) e de US3 (painel) para a
  navegação; o service e os testes de service podem começar logo após a Phase 2.
- **US5 (Phase 7)**: depende de US2 (linha e `confirmar.html`).
- **US6 (Phase 8)**: depende de US1 (seção Orientação).
- **US7 (Phase 9)**: depende de US6 (convites) e de US2 (tela Orientações).
- **US8 (Phase 10)**: depende da Phase 2; a navegação do Orientador depende de US2 e a do painel,
  de US3.
- **US9 (Phase 11)**: depende de US8 (artigos Aceitos ou Publicados).
- **Polish (Phase 12)**: depois de todas as histórias.

### Within Each User Story

- Testes primeiro (devem falhar) → service → form → view e rota → template (design) → navegação.
- Commit ao fim de cada fase, com os testes passando.

### Parallel Opportunities

- Phase 1: T001 a T005.
- Phase 2: T006, T010 e T011 em paralelo com T007; T007 e T008 → T009.
- Os arquivos de teste de cada história ([P]) podem ser escritos em paralelo logo após a Phase 2.
- Depois da Phase 5: US4 e US5 em paralelo (arquivos diferentes, exceto a linha de
  `orientacoes.html`, que deve ser editada uma de cada vez); US6 e US8 em paralelo.
- Phase 12: T055, T056 e T057.

## Parallel Example: User Story 2

```text
Task: "T019 Criar test_us18_resposta_orientandos.py"     (teste, antes)
Task: "T020 IC-05 pode_ver_resumo aceita troca"          (services_tcc.py, independente)
Task: "T022 R15 + IC-07 Correções Conferidas"            (depois de T021 no mesmo arquivo)
```

## Implementation Strategy

### MVP First (User Stories 1 e 2)

1. Phase 1 e Phase 2.
2. US1 (pedido) + US2 (resposta e tela Orientações): o vínculo de orientação funciona de ponta a
   ponta, com navegação pelo menu, pelo sino e pelo e-mail.
3. **Validar**: passos 1 a 6 do quickstart.

### Incremental Delivery

1. + US3 (painel): o Professor volta a ter todas as ações das specs 003 a 005.
2. + US4 (atas) e US5 (Apto): orientação completa; liberado para o módulo de Defesa.
3. + US6 e US7 (coorientação).
4. + US8 e US9 (publicação e aproveitamento).
5. Polish: permissões, concorrência, navegação, conferência visual, quickstart, PR.

## Conferência visual

*(preenchida em T060)*
