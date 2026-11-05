---

description: "Task list para a feature 009 — Documentação e Encerramento do SIGTCC"
---

# Tasks: Documentação e Encerramento do SIGTCC

**Status**: Approved (Célio Benjamim, 2026-11-05) — achados do `/speckit-analyze` aplicados (D1, C1 a C6, U1, I1,
R1)

**Input**: Design documents from `/specs/009-documentacao-encerramento/`
**Prerequisites**: [plan.md](plan.md) (Approved, Célio Benjamim, 2026-11-05), [spec.md](spec.md)
(Approved), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/),
[quickstart.md](quickstart.md)

**Tests**: cada cenário de aceite das 6 User Stories vira pelo menos um teste Django (constituição,
princípio VI; SC-005); os testes ficam em cada fase, escritos antes ou junto da implementação. Os
cenários são citados como `cenário <história>.<n>` (ex.: 1.10 = User Story 1, cenário 10).

**Organization**: tarefas por User Story. A Fase 2 (Foundational) traz mensagens, permissões, a
trava do PDF, o anexo de e-mail e o núcleo de `services_documentos` (E2, código, dados dos PDFs),
de que todas as histórias dependem. Commits atômicos por fase, só com os testes passando;
`git status` antes de cada commit (CLAUDE.md). Nenhuma migração.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: US1 a US6, conforme spec.md
- Cada tarefa indica as US e os RBN que atende (constituição, princípio II) e, entre parênteses,
  os FR e SC da spec; todo código novo leva comentários em português com a mesma rastreabilidade
  `[US-XX][RBN-DEF-YY.Z]`
- "Presidente" = papel Orientador (Presidente) da banca da sessão (Clarifications, B-03)

---

## Phase 1: Setup (apoio de testes)

**Purpose**: cenário de testes com sessão Realizada e liberada; nenhuma dependência nova
(`xhtml2pdf` e `pypdf==6.21.4` já no `requirements.txt`).

- [X] T001 [US-28][RBN-DEF-07.1][RBN-CAD-13.1] (FR-006) IC-16: em `sigtcc/apps/defesa/tests/apoio_avaliacao.py`, `sessao_com_banca` passa a criar
  por padrão um Coordenador (`Coordenadores`) para o curso da turma, com `doc_assinatura_path`
  apontando para uma imagem PNG gravada no `MEDIA_ROOT` temporário; parâmetro
  `com_coordenador=True` (False = curso sem Coordenador) e `assinatura_coordenador=True` (False =
  caminho nulo), para os testes da E2 (research B15)
- [X] T002 [P] [US-28][US-30][RBN-DEF-07.1][RBN-DEF-08.2] (FR-001, FR-010) Criar `sigtcc/apps/defesa/tests/apoio_documentos.py`: `sessao_liberada(etapa="TCC 2",
  parecer=Aprovado, suplente_acionado=False, **dados)` usando `apoio_avaliacao` (3 envios com
  assinatura copiada e `services_avaliacoes.liberar_resultado`); `texto_do_pdf(resposta)` com
  `pypdf.PdfReader` sobre `resposta.content`; `ouvinte(matricula, nome)`; `presenca(sessao,
  ouvinte)`
- [X] T003 [US-27][US-28][RBN-DEF-06.4][RBN-DEF-07.1] Rodar `.venv\Scripts\python.exe manage.py test sigtcc.apps.defesa` e confirmar que a
  suíte da spec 008 continua verde com o Coordenador padrão do T001 (nenhum teste depende da
  ausência dele)

**Checkpoint**: apoio pronto; commit `test(feat-09): apoio de sessao liberada e coordenador`.

---

## Phase 2: Foundational (bloqueia todas as histórias)

**Purpose**: textos, permissões, PDF seguro em paralelo, e-mail com anexo e o núcleo de
`services_documentos`.

- [X] T004 [P] [US-28][US-30][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-07.3][RBN-DEF-08.1][RBN-DEF-08.2][RBN-DEF-08.3][RBN-DEF-08.4][RBN-DEF-08.5] (FR-004 a FR-023; SC-006) IC-08: em `sigtcc/apps/defesa/mensagens.py`, acrescentar (só acréscimo), com o texto
  exato: `SEM_PERMISSAO_DOCUMENTOS` = "Você não tem permissão para acessar os documentos desta
  defesa"; `ATA_SEM_ASSINATURA_COORDENADOR` = "Não foi possível gerar a Ata Final: o Coordenador
  de Curso não possui assinatura cadastrada no perfil"; `ERRO_AO_GERAR_DOCUMENTOS` = "Erro ao gerar
  os documentos da defesa. Tente realizar o download novamente em instantes";
  `FOLHA_NAO_SE_APLICA` = "A Folha de Aprovação não se aplica ao TCC 1"; `FOLHA_REPROVADO` =
  "Documento indisponível para trabalhos reprovados"; `OUVINTES_SALVOS` = "Ouvintes salvos com
  sucesso"; `MATRICULA_INVALIDA` = "A matrícula deve conter exatamente 10 dígitos numéricos";
  `OUVINTE_REPETIDO` = "Este aluno já foi registrado como ouvinte nesta defesa"; `NOME_INVALIDO` =
  "O nome deve conter apenas letras, acentos e espaços e ter até 150 caracteres";
  `OUVINTES_FORA_DO_STATUS` = "O registro de ouvintes fica disponível apenas durante ou após a
  sessão"; `SEM_DEFESAS_AGENDADAS` = "Não existem defesas agendadas para o período selecionado";
  e as MX da spec, marcadas `# PROVISÓRIO (Q-142)` quando aplicável: `MX01_OCORRENCIAS_LONGAS`,
  `MX03_COORDENADOR_SEM_ASSINATURA`, `MX04_ASSUNTO`, `MX04_CORPO`, `MX05_DECLARACAO`,
  `MX06_OCORRENCIAS_SALVAS` (texto exato do diagrama 05), `MX07_SEM_OUVINTES`,
  `MX08_ATA_INDISPONIVEL`, `MX09_CURSO_SEM_COORDENADOR`
- [X] T005 [P] [US-28][RBN-DEF-07.3] (FR-005) IC-11: em `sigtcc/apps/cadastro/views.py`, acrescentar
  `mensagens_defesa.SEM_PERMISSAO_DOCUMENTOS` a `MENSAGENS_403` (comentário "Spec 009 (US-28
  E6)")
- [X] T006 [P] [US-28][US-30][RBN-DEF-07.1][RBN-DEF-08.3] (FR-007, FR-019) IC-14: em `sigtcc/apps/defesa/pdf.py`, envolver o `pisa.CreatePDF` de `gerar_pdf`
  num `threading.Lock` de módulo (`_TRAVA_PDF`), sem mudar assinatura nem tratamento de erro;
  docstring com o motivo (estado global do xhtml2pdf/reportlab; research B7); teste em
  `sigtcc/apps/defesa/tests/test_pdf.py`: duas threads gerando ao mesmo tempo produzem dois PDFs
  válidos
- [X] T007 [P] [US-30][RBN-DEF-08.3] (FR-019) IC-12: em `sigtcc/apps/cadastro/services.py`, `enviar_email(destino, assunto,
  template, contexto, conta=None, anexos=None)`: sem `anexos`, a mesma chamada literal
  `send_mail(...)` de hoje (cinco testes da spec 003 a substituem por `mock.patch`); com `anexos`
  (lista de `(nome, bytes, tipo)`), `EmailMessage(...).attach(...)` e `.send(fail_silently=False)`;
  a falha registra `FALHA_ENVIO_EMAIL` igual e relança; docstring "template de e-mail"; teste novo em
  `sigtcc/apps/cadastro/tests/test_enviar_email_anexos.py`: o anexo chega em
  `mail.outbox[0].attachments` e, sem anexo, `send_mail` continua sendo a chamada usada
- [X] T008 [US-28][US-30][RBN-DEF-07.3][RBN-DEF-08.1][RBN-DEF-08.2][RBN-DEF-08.3][RBN-DEF-08.4][RBN-DEF-08.5] (FR-005, FR-009, FR-012, FR-014 a FR-016, FR-021, FR-022) IC-08/IC-18: em `sigtcc/apps/defesa/permissoes_defesa.py`, criar a pública
  `e_presidente(usuario, sessao)` e fazer `_e_presidente` delegar para ela; acrescentar
  `pode_baixar_documentos`, `pode_baixar_declaracao`, `pode_editar_ouvintes`, `pode_ver_ouvintes`,
  `pode_editar_ocorrencias`, `pode_ver_ocorrencias`, `pode_gerar_agenda` e
  `pode_ver_ouvintes_das_defesas` exatamente como a tabela do research B2 (Suplente não acionado
  fora; turma arquivada por `services_turmas.turma_arquivada`; Secretaria só do curso da turma e,
  nos ouvintes, só Em Andamento ou Realizada; `pode_ver_ouvintes` sem chamar
  `pode_editar_ouvintes`)
- [X] T009 [US-28][US-30][RBN-DEF-07.3][RBN-DEF-08.1][RBN-DEF-08.2][RBN-DEF-08.3][RBN-DEF-08.4][RBN-DEF-08.5] (FR-005, FR-009, FR-012, FR-014 a FR-016, FR-021, FR-022) Teste `sigtcc/apps/defesa/tests/test_permissoes_documentos.py`: matriz perfil × status
  para cada função do T008 (Presidente, 1º e 2º Avaliador, suplente acionado, Suplente não
  acionado, Professor da Disciplina, Secretaria do curso e de outro curso, Coordenador fora da
  banca, Aluno, Membro Externo; Agendada, Reagendada, Em Andamento, Realizada antes e depois da
  liberação, Cancelada; turma arquivada); inclui o Presidente de TCC 1 depois de
  `_copiar_tcc_aprovado` (B-03)
- [X] T010 [US-28][US-30][RBN-DEF-07.1][RBN-DEF-07.2][RBN-CAD-13.1][RBN-DEF-08.3] (FR-004, FR-006, FR-020) Em `sigtcc/apps/defesa/services_documentos.py` (IC-01; manter os stubs por enquanto):
  `SEM_COORDENADOR`/`SEM_ASSINATURA` e `situacao_da_ata(sessao)` (Coordenador do `tur_cur` da
  turma; `services.caminho_da_assinatura` vazio = `SEM_ASSINATURA`; caminho gravado com arquivo
  ausente = `None`, Q-140); `_imagem_existente(caminho)` (`default_storage.exists`; ausente →
  `None` + `logger.warning`, research B4); `codigo_de_validacao(sessao, usuario)` (HMAC
  `salted_hmac("sigtcc.declaracao", f"{def_id}:{usu_id}", algorithm="sha256")`, Base32 sem `=`,
  16 primeiros caracteres) e `codigo_formatado(codigo)` (4 grupos com espaço); `_mes_por_extenso`
  (tabela fixa em português); `folha_aplicavel(sessao)` (`None` só em TCC 2 com parecer Aprovado
  ou Aprovado com Correções; senão `FOLHA_NAO_SE_APLICA` ou `FOLHA_REPROVADO`)
- [X] T011 [US-28][US-30][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-08.3] (FR-001, FR-002, FR-008, FR-019) Em `sigtcc/apps/defesa/services_documentos.py`: `_membros_do_documento(sessao)` (os 3 de
  `membros_efetivos`, na ordem Orientador, 1º, 2º Avaliador, com papel da linha da banca, nome,
  titulação lida no momento de `doc_titulacao` ou `mem_titulacao` e a assinatura de
  `ban_assinatura_path` por `_imagem_existente`); `dados_da_ata(sessao)` e `dados_da_folha(sessao)`
  com valores simples, a partir de `services_avaliacoes.resultado_da_sessao` e de `def_data`
  (FR-001, FR-002, FR-008; P12); título "Ata Final de Avaliação de Trabalho de Conclusão de Curso
  I"/"II" por `e_tcc_2`; observação do Qualis quando `elevada_pelo_qualis`; Coordenador (nome e
  assinatura); Folha com papéis Presidente, Avaliador, Avaliador e sem nenhum campo de nota;
  `dados_da_declaracao(sessao, usuario)` (nome, titulação, papel, aluno, título, curso, data da
  defesa, "Defesa nº {def_id}", código formatado; MX-05)
- [X] T012 [P] [US-30][RBN-DEF-08.3] (FR-020; SC-004) Teste `sigtcc/apps/defesa/tests/test_codigo_validacao.py`: só `A-Z2-7`, 16
  caracteres, igual em duas chamadas (SC-004), diferente entre membros e entre sessões, muda com
  outra `SECRET_KEY` (`override_settings`)
- [X] T013 [P] [US-28][RBN-DEF-07.1][RBN-DEF-07.2] (FR-001, FR-002, FR-006, FR-008; SC-001) Teste `sigtcc/apps/defesa/tests/test_us28_documentos.py` (parte de serviço):
  `situacao_da_ata` nos 3 casos e no arquivo ausente (Q-140); `dados_da_folha` sem chave de nota;
  `dados_da_ata` com suplente na linha do titular; data = `def_data`

**Checkpoint**: commit `feat(feat-09): base de permissoes e servicos de documentos` (IC-11, IC-12,
IC-14 e IC-18 relatados).

---

## Phase 3: User Story 1 — Ata Final e Folha de Aprovação (Priority: P1) 🎯 MVP

**Goal**: baixar os documentos formais depois da liberação, com a E2 na liberação e no download.

**Independent Test**: sessões Realizadas de TCC 1, TCC 2 aprovado e Reprovado; baixar cada
documento como cada perfil e conferir conteúdo, botões e recusas (cenários 1.1 a 1.19).

- [X] T014 [P] [US1] [US-28][RBN-DEF-07.1][RBN-DEF-07.2] (FR-001, FR-002) Criar `sigtcc/templates/defesa/pdf/ata_final.html` e
  `sigtcc/templates/defesa/pdf/folha_aprovacao.html` estendendo `defesa/pdf/base_pdf.html`
  (Roboto local, sem `base.html`): cabeçalho "Universidade do Estado do Amazonas – Escola Superior
  de Tecnologia" e curso; conteúdo do FR-001/FR-002; `<img>` só quando a assinatura não é `None`;
  a Folha não exibe nenhum número de nota; "Manaus, DD de mês de AAAA"
- [X] T015 [US1] [US-28][RBN-DEF-07.3] (FR-003) Em `sigtcc/apps/defesa/services_documentos.py`: `visao_dos_documentos(usuario,
  sessao)` (botões Ata, Folha e Declaração conforme permissões e `folha_aplicavel`) e
  `documentos_do_aluno(tcc)` (sessões Realizadas e liberadas do TCC, mais recente primeiro, com
  data e botões; P14)
- [X] T016 [US1] [US-28][RBN-DEF-07.1][RBN-CAD-13.1] (FR-006) Em `sigtcc/apps/defesa/services_documentos.py`: `avisar_pendencia_da_ata(sessao)`
  (relê a sessão pelo `pk`; com motivo, numa `transaction.atomic()` própria, `services.notificar`
  ao docente Coordenador com a MX-03 e link `cadastro:perfil`, ou a cada Secretaria ativa do curso
  com a MX-09 e link para `defesa:sessao`; devolve `ATA_SEM_ASSINATURA_COORDENADOR`; sem motivo,
  `None`; exceção → `logger.exception` e `None`) — research B5
- [X] T017 [US1] [US-28][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-07.3] (FR-004 a FR-007) Criar `sigtcc/apps/defesa/views_documentos.py`: `ata_final(request, def_id)` e
  `folha_aprovacao(request, def_id)` com `perfil_requerido()`, `views_defesa.sessao_ou_404`,
  `PermissionDenied(SEM_PERMISSAO_DOCUMENTOS)` sem permissão ou antes da liberação; Folha recusada
  por `folha_aplicavel`; Ata com `situacao_da_ata` → mensagem da E2 ao Presidente ou MX-08 aos
  demais, sem notificar; `ErroAoGerarPdf` → `ERRO_AO_GERAR_DOCUMENTOS`; recusas não-403 voltam à
  origem por `origem=sessao|meu_tcc` (qualquer outro valor = `sessao`) com `messages.error`;
  sucesso: `pdf.resposta_pdf("ata_final_<def_id>.pdf", ...)` / `folha_aprovacao_<def_id>.pdf`
- [X] T018 [US1] [US-28][RBN-DEF-07.3] (FR-003) IC-08: em `sigtcc/apps/defesa/urls.py`, rotas `ata_final`
  (`defesas/<int:def_id>/ata-final/`) e `folha_aprovacao` (`defesas/<int:def_id>/folha-aprovacao/`)
- [X] T019 [US1] [US-28][RBN-DEF-07.3] (FR-003) IC-03: em `sigtcc/apps/defesa/views_defesa.py`, `contexto_da_sessao` ganha a
  chave `documentos` (`visao_dos_documentos`); criar `sigtcc/templates/defesa/_bloco_documentos.html`
  e preencher `{% block documentos %}` de `sigtcc/templates/defesa/sessao.html`
- [X] T020 [US1] [US-28][RBN-DEF-07.3] (FR-003) IC-05: em `sigtcc/apps/cadastro/views_tcc.py`, contexto `documentos_defesa =
  services_documentos.documentos_do_aluno(tcc)`; criar `sigtcc/templates/defesa/_documentos_aluno.html`
  (links com `?origem=meu_tcc`) e incluí-la em `sigtcc/templates/cadastro/tcc/meu_tcc.html`;
  remover os dois botões desabilitados "Ata Final" e "Folha de Aprovação" do cartão "Defesa"
- [X] T021 [US1] [US-27][US-28][RBN-DEF-06.4][RBN-DEF-07.1][RBN-CAD-13.1] (FR-006) IC-02: em `sigtcc/apps/defesa/views_avaliacoes.py`, no ramo `resultado.liberado`
  de `liberar_resultado`, depois da MA-11, `texto = services_documentos.avisar_pendencia_da_ata(registro)`
  e `messages.warning(request, texto)` se houver; docstring cita a emenda da spec 008 (Q-144)
- [X] T022 [US1] [US-28][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-07.3] (FR-001 a FR-008; SC-001 a SC-003) Testes de view em `sigtcc/apps/defesa/tests/test_us28_documentos.py`, um por
  cenário: 1.1 (Ata com notas e 4 assinaturas, Folha sem notas, botões para banca, Professor da
  Disciplina, Secretaria e Aluno), 1.2 (Aluno baixa a Folha pelo Meu TCC), 1.3 (TCC 1: só Ata
  "I"), 1.4 (Reprovado: só Ata), 1.5 (Aprovado com Correções: Folha liberada), 1.6 (suplente na
  linha do substituído), 1.7 (observação do Qualis), 1.8 (Secretaria pela lista Defesas), 1.9
  (login e download), 1.10 (E2 na liberação: alerta, notificação ao Coordenador com link do
  perfil; download: E2 ao Presidente e MX-08 a outro perfil; Folha disponível), 1.11 (falha:
  `mock.patch` de `pdf.gerar_pdf`, mensagem, nada gravado em `MEDIA_ROOT`), 1.12, 1.13, 1.14, 1.15
  (Suplente não acionado), 1.16 (antes da liberação), 1.17 (sem Coordenador: MX-09 à Secretaria),
  1.18 (arquivo do Coordenador ausente: PDF sem a imagem, log), 1.19 (duas sessões no Meu TCC); Edge Case "Coordenador cadastra a assinatura depois da
  liberação" (o download seguinte gera a Ata, sem nova ação);
  texto do PDF por `apoio_documentos.texto_do_pdf`; `?origem=` com valor livre cai em `sessao`
- [X] T023 [US1] [US-27][US-28][RBN-DEF-06.4][RBN-DEF-07.1][RBN-DEF-07.3] (FR-003, FR-006) IC-16: em `sigtcc/apps/defesa/tests/test_us27_liberacao.py`, novo teste do alerta
  da E2 depois da MA-11 (cenário `com_coordenador=False`) e ajuste nominal de
  `test_avisos_ao_aluno_banca_e_secretaria_sem_a_nota` só se a mudança do T001 exigir; novo teste
  em `sigtcc/apps/cadastro/tests/test_navegacao_tcc.py` (aba Meu TCC, spec 005) conferindo que os botões desabilitados saíram e
  que a parcial aparece

**Checkpoint**: commit `feat(feat-09): gerar ata final e folha de aprovacao sob demanda` (IC-02,
IC-03, IC-05 relatados).

---

## Phase 4: User Story 2 — Ouvintes da sessão (Priority: P2)

**Goal**: o Presidente e o Professor da Disciplina registram os ouvintes; a Secretaria consulta.

**Independent Test**: sessões Em Andamento, Realizada, Agendada, Reagendada e Cancelada e turma
arquivada; abrir, adicionar, remover e salvar como cada perfil (cenários 2.1 a 2.12).

- [X] T024 [P] [US2] [US-30][RBN-DEF-08.2] (FR-010, FR-011) Criar `sigtcc/apps/defesa/forms_ouvintes.py`: `OuvinteForm` (`nome` aparado,
  não vazio, até 150, cada caractere `str.isalpha()` ou espaço → senão `NOME_INVALIDO`;
  `matricula` `^[0-9]{10}$` → senão `MATRICULA_INVALIDA`) e `OuvintesFormSet = formset_factory(
  OuvinteForm, extra=1, can_delete=True, max_num=200, absolute_max=200, validate_max=True)` com
  `clean()` que marca `OUVINTE_REPETIDO` na linha repetida **só dentro da lista enviada**
  (research B9; I-03); campos com erro recebem a classe `erro`
- [X] T025 [US2] [US-30][RBN-DEF-08.2] (FR-010 a FR-012) Criar `sigtcc/apps/defesa/services_ouvintes.py`: `ErroOuvintes(campo, mensagem)`;
  `ouvintes_da_sessao(sessao)` (por nome); `salvar_ouvintes(usuario, def_id, linhas)` em
  `transaction.atomic()`: `travar_tcc(tcc_da_sessao(def_id))` e `travar_sessao(def_id)`; confere
  `pode_editar_ouvintes`; revalida as linhas (mesmas regras do T024); matrículas novas em ordem
  crescente com `Ouvintes.objects.get_or_create(ouv_matricula=..., defaults={"ouv_nome": ...})`
  ("`ouv_matricula` CHAR(10) AK"; nome existente nunca alterado, P4); apaga as `PresencaOuvintes`
  que saíram e cria as novas com `bulk_create`; nunca apaga `Ouvintes`
- [X] T026 [US2] [US-30][RBN-DEF-08.2] (FR-009) Em `sigtcc/apps/defesa/services_ouvintes.py`: `visao_da_sessao(usuario, sessao)`
  (parte de ouvintes: lista, `pode_editar`, `pode_ver`, mensagem da E7 quando o status não é Em
  Andamento nem Realizada e o usuário é Presidente ou Professor da Disciplina)
- [X] T027 [US2] [US-30][RBN-DEF-08.2] (FR-010, FR-012) Criar `sigtcc/apps/defesa/views_ouvintes.py`: `ouvintes(request, def_id)` com
  `perfil_requerido("docente")`; GET: formset com os ouvintes gravados; POST: valida, chama
  `salvar_ouvintes`, converte `TurmaArquivada` e `ErroOuvintes` de permissão em
  `PermissionDenied` (M-02; I-01), mostra erros de campo na mesma janela; sucesso:
  `OUVINTES_SALVOS` e volta à sessão
- [X] T028 [US2] [US-30][RBN-DEF-08.2] (FR-009, FR-010) Criar `sigtcc/templates/defesa/form_ouvintes.html` (linhas Nome Completo e
  Matrícula, Remover, Adicionar, Cancelar, Salvar) e `sigtcc/static/js/ouvintes.js` (clona o
  `empty_form` e atualiza o `TOTAL_FORMS`); criar `sigtcc/templates/defesa/_bloco_ouvintes.html` e
  preencher `{% block ouvintes %}` de `sessao.html`; `contexto_da_sessao` ganha a chave `ouvintes`
  (`services_ouvintes.visao_da_sessao`) — IC-03; rota `ouvintes` em `urls.py`
- [X] T029 [US2] [US-30][RBN-DEF-08.2] (FR-009 a FR-012) Testes `sigtcc/apps/defesa/tests/test_us30_ouvintes.py`, um por cenário: 2.1, 2.2,
  2.3 (remover mantém o registro em `Ouvintes`), 2.4 (12345678 e 12345abc90), 2.5 (repetido na
  lista), 2.6 ("Ana 2", vazio, e também "×"), 2.7 (Agendada, Reagendada, Cancelada), 2.8 (outro
  docente: 403 M-02), 2.9 (login), 2.10 (Secretaria só leitura, sem Adicionar/Salvar), 2.11 (nome
  gravado mantido), 2.12 (turma arquivada: sem botão, POST 403); FR-009 "os demais perfis não veem a lista" (1º e
  2º Avaliador, Suplente, Aluno e Membro Externo abrem a sessão sem o bloco de ouvintes); mais: corrida com `mock` de
  `travar_tcc` levantando `TurmaArquivada` (403, não 500); `absolute_max` com `TOTAL_FORMS`
  adulterado; a linha extra vazia é ignorada

**Checkpoint**: commit `feat(feat-09): registrar ouvintes da sessao de defesa`.

---

## Phase 5: User Story 4 — Ouvintes das defesas (Priority: P2)

**Goal**: a Secretaria consulta os ouvintes das sessões Realizadas para as horas complementares.

**Independent Test**: ouvintes em sessões Realizadas de cursos e períodos diferentes (cenários 4.1
a 4.7).

- [X] T030 [US4] [US-30][RBN-DEF-08.4][RBN-DEF-01.5] (FR-016, FR-017) Em `sigtcc/apps/defesa/services_ouvintes.py`: `ouvintes_das_defesas(periodo,
  cur_id)` com `periodo` = Q sobre `Defesas` de `FiltroPeriodoForm.filtro()` (sem prefixo):
  `PresencaOuvintes.objects.filter(pre_def__in=Defesas.objects.filter(periodo,
  def_status=Realizada[, def_tcc__tcc_tur__tur_cur_id=cur_id]))`, `select_related` do ouvinte, TCC
  e aluno, `orientador_nome` por `Subquery` do Presidente, ordem data, título, nome (research B11)
- [X] T031 [US4] [US-30][RBN-DEF-08.4][RBN-DEF-01.5][RBN-CAD-14.1] (FR-016, FR-017) Em `sigtcc/apps/defesa/views_ouvintes.py`: `ouvintes_das_defesas(request)` com
  `perfil_requerido("secretaria")`, `iniciar_sessoes_vencidas()`, `FiltroPeriodoForm` e
  `services_contas.filtro_de_curso`; criar `sigtcc/templates/defesa/ouvintes_das_defesas.html`
  (inclui `_filtro_periodo.html` e o filtro de Curso; colunas Nome Completo, Matrícula, Título,
  Aluno, Orientador, Data da defesa, "2 horas"; vazia → MX-07); rota `ouvintes_das_defesas`
  (`ouvintes-das-defesas/`) em `urls.py`
- [X] T032 [US4] [US-30][RBN-DEF-08.4] (FR-016) IC-07: em `sigtcc/apps/cadastro/menu.py`, item "Ouvintes das defesas" (perfis
  `("secretaria",)`, rota `defesa:ouvintes_das_defesas`, ícone `how_to_reg`, `ordem` 15, depois de
  "Minhas bancas", na mesma seção do item "Defesas")
- [X] T033 [US4] [US-30][RBN-DEF-08.4][RBN-DEF-01.5][RBN-CAD-14.1] (FR-016 a FR-018) Testes `sigtcc/apps/defesa/tests/test_us30_ouvintes_das_defesas.py`: 4.1 a 4.7
  (colunas; ouvinte em duas sessões aparece duas vezes com 2 horas; Em Andamento/Cancelada fora;
  regra do filtro de Curso; MX-07; docente, Professor da Disciplina e Coordenador recusados; login);
  `assertNumQueries` constante com 1 e com 10 linhas; o menu mostra o item só à Secretaria

**Checkpoint**: commit `feat(feat-09): listar ouvintes das defesas para a secretaria` (IC-07).

---

## Phase 6: User Story 6 — Agenda de defesas em PDF (Priority: P2)

**Goal**: gerar a agenda pública das sessões Agendadas e Reagendadas do período.

**Independent Test**: sessões em vários status, cursos e datas; gerar com filtros diferentes
(cenários 6.1 a 6.7).

- [X] T034 [US6] [US-30][RBN-DEF-08.1][RBN-CAD-14.1] (FR-022, FR-024) Em `sigtcc/apps/defesa/services_documentos.py`: `agenda_de_defesas(usuario,
  periodo, cur_id)` (status Agendada e Reagendada, Q do período, sem a visibilidade do perfil, P2;
  `cur_id` só para `coordenador`/`secretaria`; ordem `def_data`, `def_h_inicio`; agrupada por dia;
  linha com HH:MM, título, aluno, Presidente e `dep_local` ou link) — research B12
- [X] T035 [US6] [US-30][RBN-DEF-08.1][RBN-DEF-01.5] (FR-022, FR-023) Em `sigtcc/apps/defesa/views_documentos.py`: `agenda(request)` com
  `perfil_requerido("docente", "coordenador", "secretaria")`, `iniciar_sessoes_vencidas()`,
  `FiltroDefesasForm` sobre `request.GET`; form inválido → redireciona a `defesa:defesas` com a
  query string original; vazia → `SEM_DEFESAS_AGENDADAS` e redireciona; `ErroAoGerarPdf` →
  `ERRO_AO_GERAR_DOCUMENTOS`; sucesso `agenda_defesas.pdf`; criar
  `sigtcc/templates/defesa/pdf/agenda.html`; rota `agenda` (`defesas/agenda/`) antes de
  `defesas/<int:def_id>/` em `urls.py`
- [X] T036 [US6] [US-30][RBN-DEF-08.1] (FR-022) IC-06: em `sigtcc/apps/defesa/views_defesa.py` (`defesas`) e
  `sigtcc/templates/defesa/defesas.html`, botão "Agenda de defesas (PDF)" para `pode_gerar_agenda`,
  com a query string atual
- [X] T037 [US6] [US-30][RBN-DEF-08.1][RBN-CAD-14.1] (FR-022 a FR-024) Testes `sigtcc/apps/defesa/tests/test_us30_agenda.py`: 6.1 a 6.7 (agrupado por dia
  com data DD/MM/AAAA e HH:MM; filtro de Curso do Coordenador; vazia sem arquivo; Em Andamento,
  Realizada e Cancelada fora; Orientador recebe todas as sessões de todos os cursos; login; Aluno e
  Membro Externo recusados); filtro inválido redireciona sem PDF; sessão vencida já iniciada não
  aparece; falha de geração (`mock.patch` de `pdf.gerar_pdf` levantando `ErroAoGerarPdf`) →
  `ERRO_AO_GERAR_DOCUMENTOS` e nenhum arquivo; o botão "Agenda de defesas (PDF)" não aparece ao
  Aluno nem ao Membro Externo na tela Defesas

**Checkpoint**: commit `feat(feat-09): gerar agenda de defesas em pdf` (IC-06).

---

## Phase 7: User Story 3 — Ocorrências (Priority: P3)

**Goal**: o Presidente relata as ocorrências até a liberação; Secretaria e Professor da Disciplina
leem.

**Independent Test**: sessão Em Andamento; salvar como Presidente e conferir a leitura por perfil;
depois da liberação, só consulta (cenários 3.1 a 3.8).

- [X] T038 [P] [US3] [US-30][RBN-DEF-08.5] (FR-013) Em `sigtcc/apps/defesa/forms_ouvintes.py`: `OcorrenciasForm` (`Textarea`,
  opcional; `clean` normaliza `\r\n` → `\n` antes de conferir "VARCHAR(2000)" → MX-01; caixa com
  a classe `erro`)
- [X] T039 [US3] [US-30][RBN-DEF-08.5] (FR-013 a FR-015) Em `sigtcc/apps/defesa/services_ouvintes.py`: `registrar_ocorrencias(usuario,
  def_id, texto)` (trava `travar_tcc` + `travar_sessao`; `pode_editar_ocorrencias`; vazio → `None`;
  `save(update_fields=["def_ocorrencias"])`; nunca grava `Historico_Defesas`) e a parte de
  ocorrências de `visao_da_sessao` (texto, `pode_editar`, `pode_ver`)
- [X] T040 [US3] [US-30][RBN-DEF-08.5] (FR-013, FR-015) Em `sigtcc/apps/defesa/views_ouvintes.py`: `ocorrencias(request, def_id)` com
  `perfil_requerido("docente")`, mesma conversão de `TurmaArquivada` em 403; sucesso MX-06 e volta à
  sessão; criar `sigtcc/templates/defesa/form_ocorrencias.html` (contador com
  `static/js/contador.js`) e `sigtcc/templates/defesa/_bloco_ocorrencias.html`; preencher
  `{% block ocorrencias %}` de `sessao.html`; rota `ocorrencias` em `urls.py`
- [X] T041 [US3] [US-30][RBN-DEF-08.5] (FR-013 a FR-015) Testes `sigtcc/apps/defesa/tests/test_us30_ocorrencias.py`: 3.1 a 3.8 (gravar e ler
  por Secretaria e Professor da Disciplina; vazio permitido; 2.001 → MX-01 e nada gravado, e 2.000
  com quebras `\r\n` aceito; Realizada só leitura; Professor da Disciplina recusado; Avaliador,
  Suplente e Aluno não veem; login; Presidente de TCC 1 depois da matrícula no TCC 2 ainda lê, B-03;
  Edge Case "Ocorrências e reagendamento": a ocorrência gravada continua depois de reagendar a
  sessão Em Andamento e volta a ser editável quando a nova sessão fica Em Andamento)

**Checkpoint**: commit `feat(feat-09): registrar ocorrencias da sessao`.

---

## Phase 8: User Story 5 — Declaração de participação (Priority: P3)

**Goal**: declaração por e-mail na liberação e segunda via em Minhas bancas.

**Independent Test**: liberar o resultado e conferir e-mails e segunda via, inclusive com suplente
(cenários 5.1 a 5.4).

- [X] T042 [P] [US5] [US-30][RBN-DEF-08.3] (FR-019, FR-020) Criar `sigtcc/templates/defesa/pdf/declaracao.html` (MX-05, "Defesa nº
  {def_id}", código formatado, "Este código não constitui assinatura digital") e
  `sigtcc/templates/defesa/emails/declaracao.txt` (MX-04)
- [X] T043 [US5] [US-30][RBN-DEF-08.3] (FR-019) Em `sigtcc/apps/defesa/services_documentos.py`: `_enviar_declaracoes(itens)` (sem
  acesso ao banco: para cada item, `pdf.gerar_pdf` e `services.enviar_email(..., anexos=[(
  "declaracao_participacao_<def_id>.pdf", bytes, "application/pdf")])`; falha de um membro não
  interrompe os demais; falha de geração só no log; `connection.close()` no `finally`) e o corpo
  real de `ao_liberar_resultado(sessao)` (relê a sessão; itens com valores simples e o `pk` da
  conta; síncrono com `SIGTCC_EMAIL_SINCRONO`, senão `threading.Thread(daemon=True)`; nunca
  levanta) — research B7
- [X] T044 [US5] [US-25][US-30][RBN-DEF-05.4][RBN-DEF-08.3] (FR-021) Em `sigtcc/apps/defesa/services_documentos.py`: corpo real de
  `declaracao_disponivel(sessao, usuario)` (= `pode_baixar_declaracao`); IC-15: corrigir o
  docstring de `services_avaliacoes.minhas_bancas` (uma consulta a mais por sessão Realizada)
- [X] T045 [US5] [US-30][RBN-DEF-05.4][RBN-DEF-08.3] (FR-021) Em `sigtcc/apps/defesa/views_documentos.py`: `declaracao(request, def_id)` com
  `perfil_requerido()` e `PermissionDenied(SEM_PERMISSAO_DOCUMENTOS)`; rota `declaracao`
  (`defesas/<int:def_id>/declaracao/`); botão Declaração em `_bloco_documentos.html`; IC-04: link
  "Declaração" de `sigtcc/templates/defesa/minhas_bancas.html` para `defesa:declaracao`
- [X] T046 [US5] [US-30][RBN-DEF-08.3][RBN-DEF-08.4] (FR-018 a FR-021; SC-004) Testes `sigtcc/apps/defesa/tests/test_us30_declaracao.py`: 5.1 (3 e-mails com o
  anexo PDF e o código; `captureOnCommitCallbacks(execute=True)` e `SIGTCC_EMAIL_SINCRONO=True`),
  5.2 (segunda via com o mesmo código do e-mail), 5.3 (suplente recebe, titular ausente e
  Suplente não acionado não; nenhum e-mail vai a ouvinte da sessão, FR-018), 5.4 (backend que
  falha: liberação mantida, log, segunda via disponível); falha de geração da segunda via
  (`ErroAoGerarPdf`) → `ERRO_AO_GERAR_DOCUMENTOS`; o "consolida os ouvintes" do 5.1 não grava
  nada (a consolidação é a consulta da US4, T030), então o teste só confere que as presenças da
  sessão continuam; `_enviar_declaracoes` com `assertNumQueries(0)`; Aluno e Secretaria recebem
  `SEM_PERMISSAO_DOCUMENTOS`; IC-16: ajustar `sigtcc/apps/defesa/tests/test_minhas_bancas.py`
  (destino do link e `declaracao_disponivel` real) e o conjunto de assuntos de
  `test_us27_liberacao.test_avisos_ao_aluno_banca_e_secretaria_sem_a_nota` (inclui o da MX-04)

**Checkpoint**: commit `feat(feat-09): enviar declaracao de participacao na liberacao` (IC-04,
IC-15, IC-16).

---

## Phase 9: Polish & Cross-Cutting Concerns

- [X] T047 [P] [US-28][US-30][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-07.3][RBN-DEF-08.1][RBN-DEF-08.2][RBN-DEF-08.3][RBN-DEF-08.4][RBN-DEF-08.5] (SC-003, SC-006) Teste `sigtcc/apps/defesa/tests/test_mensagens_documentos.py`: cada texto do T004
  igual ao da US-28/US-30, do diagrama 05 (MX-06) ou da tabela "Mensagens a validar com a PO"
  (SC-006); nenhum PDF gravado em disco em todo o módulo de testes (SC-003)
- [X] T048 [US-28][US-30][RBN-DEF-07.1][RBN-CAD-13.1][RBN-DEF-08.1][RBN-DEF-08.2][RBN-DEF-08.5] IC-09: em `sigtcc/apps/cadastro/management/commands/popular_demo.py`, só por serviços:
  ouvintes e ocorrências na sessão Realizada de demonstração; `static/img/assinatura_demo.png`
  copiada para o perfil do Coordenador de um curso; outro curso com Coordenador sem assinatura
  (E2); sessões Agendada e Reagendada no período para a agenda (research B14)
- [X] T049 [P] [US-28][US-30][RBN-DEF-07.1][RBN-DEF-08.1][RBN-DEF-08.2][RBN-DEF-08.5] IC-17: atualizar `docs/diagramas/Rastreabilidade_Diagramas_Codigo.md`
  (`:GeradorDocumentosPDF` deixa de citar stubs; `services_ouvintes`, `views_documentos`,
  `views_ouvintes` e o participante do diagrama 05), o diagrama 28 em
  `docs/diagramas/Diagramas_Sequencia_PlantUML_v2.md` (passo da E2 na liberação, Q-144),
  `docs/arquitetura/Componentes_SIGTCC.drawio` (rótulo do componente da Defesa; PNG fica na Q-137)
  e `CHANGELOG.md` (entrada da feat-09)
- [X] T050 [US-28][US-30][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-07.3][RBN-DEF-08.1][RBN-DEF-08.2][RBN-DEF-08.3][RBN-DEF-08.4][RBN-DEF-08.5] (SC-005) Rodar `.venv\Scripts\python.exe manage.py test` (suíte inteira) e `pre-commit run
  --all-files`; corrigir o que aparecer
- [X] T051 [US-28][US-30][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-07.3][RBN-DEF-08.1][RBN-DEF-08.2][RBN-DEF-08.3][RBN-DEF-08.4][RBN-DEF-08.5] (FR-001 a FR-024) Validação manual pelo roteiro de 18 passos (1 a 17 e 13a) de [quickstart.md](quickstart.md) no banco
  `sigtcc_validacao`, no navegador; registrar o resultado no `pr-feat-09.md` (com o risco aceito do
  código de validação e da `SECRET_KEY`, research B6)

**Checkpoint**: commit `chore(feat-09): popular demonstracao e atualizar documentos`.

---

## Dependencies & Execution Order

- **Phase 1 → Phase 2 → histórias**. Phase 2 bloqueia todas.
- **US1 (P1, MVP)** depende só da Phase 2.
- **US2** depende da Phase 2; **US3** depende da US2 (mesmos `forms_ouvintes.py`,
  `services_ouvintes.py`, `views_ouvintes.py` e a chave `ouvintes` de `contexto_da_sessao`).
- **US4** depende da US2 (`services_ouvintes.py`, `views_ouvintes.py`).
- **US6** depende da Phase 2 e de `views_documentos.py` criado na US1.
- **US5** depende da US1 (`_bloco_documentos.html`, `views_documentos.py`).
- `urls.py`, `sessao.html` e `contexto_da_sessao` são tocados por várias histórias: nunca em
  paralelo.

### Commits sugeridos

Um por fase, nos checkpoints acima (Conventional Commits, até 72 caracteres, sem ponto final).

## Parallel Example: Phase 2

```text
T004 mensagens.py  |  T005 cadastro/views.py  |  T006 pdf.py  |  T007 cadastro/services.py
depois: T008 → T009; T010 → T011 → T012 [P] T013
```

## Implementation Strategy

1. MVP: Phases 1, 2 e 3 (Ata e Folha com a E2) — o encerramento formal já funciona.
2. Depois, em ordem de prioridade: US2 → US4 → US6 (P2), US3 → US5 (P3).
3. Polish: demonstração, documentos, suíte inteira, pre-commit e roteiro manual.
