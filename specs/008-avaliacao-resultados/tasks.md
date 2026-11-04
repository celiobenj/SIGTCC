---

description: "Task list para a feature 008 — Avaliação e Resultados do SIGTCC"
---

# Tasks: Avaliação e Resultados do SIGTCC

**Status**: Approved (Célio Benjamim, 2026-11-03) — depois do `/speckit-analyze` (I1: MA-13;
I2: US1 e US2 em sequência; I3: o que o aluno vê é testado na US5; A1: MA-14, sem reduzir a
imagem; C1: teste dos serviços únicos; D1 e U1 ajustados).

**Input**: Design documents from `/specs/008-avaliacao-resultados/`
**Prerequisites**: [plan.md](plan.md) (Approved, Célio Benjamim, 2026-11-03), [spec.md](spec.md),
[research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/),
[quickstart.md](quickstart.md)

**Tests**: cada cenário de aceite das 5 User Stories vira pelo menos um teste Django (constituição,
princípio VI); os testes estão em cada fase, escritos antes ou junto da implementação.

**Organization**: tarefas por User Story. A Fase 2 (Foundational) traz o núcleo de
`services_avaliacoes.py` (estado, cálculo, descarte, sigilo) e as mudanças na spec 007 (IC-01,
IC-03), de que todas as histórias dependem. Commits atômicos por fase, só com os testes passando;
`git status` antes de cada commit (CLAUDE.md).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: US1 a US5, conforme spec.md
- Todo código novo leva comentários em português e a rastreabilidade `[US-XX][RBN-DEF-YY.Z]`

---

## Phase 1: Setup (infraestrutura)

**Purpose**: dependência de PDF, utilitário de PDF em memória e apoio de testes

- [X] T001 IC-04, commit `chore(config)`: instalar o `xhtml2pdf` na `.venv`, acrescentar ao
  `requirements.txt` a versão exata do `pip freeze` e as dependências que ele trouxer (sem CVE
  conhecida), com o comentário de item de configuração (PGCS 3.7); conferir
  `pip install -r requirements.txt` num Linux limpo com Python 3.12 (contêiner
  `python:3.12-slim`) e anotar o resultado para o PR; se alguma dependência exigir biblioteca de
  sistema (ex.: cairo), fixar a versão que não exige (research A9; revisão I-13). Sem mudança no
  `settings.py` (sem STORAGES externo). **Nota da implementação**: conferência no Linux limpo
  pendente (Docker sem o serviço em execução na estação); a árvore instalada não tem pycairo nem
  rlPyCairo (`pip show`), ver pr-feat-08.md
- [X] T002 [P] Criar `sigtcc/apps/defesa/pdf.py` com `gerar_pdf(template, contexto) -> bytes`,
  `resposta_pdf(nome_arquivo, template, contexto) -> HttpResponse` (`attachment`, `no-store`) e
  `ErroAoGerarPdf` (com log), importando o `xhtml2pdf` só dentro de `gerar_pdf`; `link_callback`
  que aceita só caminho relativo de `static/` ou `media/`, resolvido com `realpath` dentro de
  `STATIC_ROOT` (ou dos finders) ou `MEDIA_ROOT`, e devolve `None` para `http:`, `https:`,
  `file:`, `data:` ou caminho que saia dessas pastas; fontes TTF locais em
  `sigtcc/static/fonts/` (Roboto, licença Apache 2.0, com o arquivo da licença na mesma pasta;
  `/speckit-analyze` U1) (contrato §3; research A9; revisão I-11, I-12)
- [X] T003 [P] Criar `sigtcc/apps/defesa/tests/test_pdf.py`: gera um PDF de um template de teste
  (que não estende `base.html`) e confere que começa com `%PDF`; `link_callback` recusa
  `http://`, `file://` e `../` sem acesso à rede; `resposta_pdf` com `Content-Disposition:
  attachment` e `Cache-Control: no-store`; falha de geração vira `ErroAoGerarPdf`. Commit
  `feat(feat-08)` com T002 (revisão M-01)
- [X] T004 [P] Criar `sigtcc/apps/defesa/tests/apoio_avaliacao.py` (a partir de `apoio_defesa.py`):
  `sessao_em_andamento(...)`, `lancar(sessao, membro, notas)` (9 critérios), `enviar(sessao,
  membro)`, imagens PNG/JPG geradas em memória (500 KB, 3 MB, 3000 × 3000 px) e um `.pdf` falso;
  `MEDIA_ROOT` temporário via `override_settings` (research A13)
- [X] T005 [P] Acrescentar a `sigtcc/apps/defesa/mensagens.py` (IC-09) os textos exatos das US-25
  a US-27 ("A nota deve situar-se entre o valor mínimo e o máximo para o conceito selecionado
  (ex.: de 6,0 a 7,9 para Competente)", "Todos os 9 critérios devem conter conceito e nota", "A
  assinatura do membro da banca é obrigatória para finalizar a avaliação", "Acesso restrito aos
  membros avaliadores da banca", "O arquivo de assinatura deve ter tamanho máximo de 2 MB",
  "Formato não suportado. Envie a assinatura em PNG ou JPG", "Selecione o parecer da banca para
  continuar", "Apenas o Orientador (Presidente da banca) pode liberar o resultado da defesa") e
  MA-01 a MA-14 da tabela "Mensagens a validar com a PO" da spec (aprovadas, Q-129)

**Checkpoint**: PDF em memória funcionando e testado; apoio de testes pronto.

---

## Phase 2: Foundational (bloqueia todas as histórias)

**Purpose**: núcleo de `services_avaliacoes.py` e as mudanças na spec 007

- [X] T006 Criar `sigtcc/apps/defesa/services_avaliacoes.py` com `estado_da_avaliacao(sessao,
  membro)` e `estados_da_banca(sessao)` derivados (Não avaliou: sem linhas em `Avaliacoes`;
  Rascunho salvo: com linhas e `ban_data_envio` nulo; Enviada: `ban_data_envio` preenchido), só
  para os `membros_efetivos`, numa consulta agregada (research A2; dicionário 3.6.4)
  [US-25][RBN-DEF-06.8]
- [X] T007 Em `services_avaliacoes.py`: `nota_individual(sessao, membro)` = Σ(`ava_nota` ×
  `cri_peso`) / 10 e `nota_final(sessao)` = média das 3 individuais já arredondadas, tudo em
  `Decimal` com `quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)`; `nota_final` devolve `None`
  sem os 3 envios; com `services_artigos.tem_artigo_homologado_qualis_ab(tcc)`, `max(6.0,
  média)`; só `membros_efetivos` (research A3; revisão I-06) [US-27][RBN-DEF-06.1][RBN-DEF-06.2]
- [X] T008 [P] Criar `sigtcc/apps/defesa/tests/test_calculo_notas.py` (SC-002): soma 6,05 → 6,1;
  6,04 → 6,0; média de 5,9, 6,0 e 6,0 → 6,0; média 5,4 com Qualis A homologado → 6,0; 7,0 com
  Qualis B → 7,0; todas 10 → 10,0; pesos de `Criterios` somam 10,0 (7,0 + 3,0); Suplente não
  acionado com linhas antigas fora do cálculo [US-27][RBN-DEF-04.1][RBN-DEF-06.1][RBN-DEF-06.2]
- [X] T009 Em `services_avaliacoes.py`: `descartar_avaliacoes(sessao, membro=None)` (apaga as
  linhas de `Avaliacoes` do membro ou de todos; limpa `ban_assinatura_path` e `ban_data_envio`
  quando a linha existe; apaga a cópia da imagem com `transaction.on_commit`; limpa
  `def_parecer`) e `voltar_envios_a_rascunho(sessao)` (mantém as notas; limpa envio, assinatura e
  `def_parecer`) (contrato §1; FR-034, FR-035; D2; D3 revista, Q-135)
  [US-23][US-24][US-27][RBN-DEF-02.2][RBN-DEF-02.4][RBN-DEF-03.3]
- [X] T010 IC-01 em `sigtcc/apps/defesa/services_defesa.py`: `descartar_avaliacoes` passa a
  delegar para `services_avaliacoes.descartar_avaliacoes` (mesma assinatura); em
  `acionar_suplente` e `alterar_banca`, a chamada vai para **antes** do `delete()` da linha de
  `BancaDefesa` (revisão I-07); `alterar_banca` descarta quem sai da banca ou passa a Suplente,
  mantém o rascunho na troca entre titulares e atualiza (`update(ban_papel=...)`) a linha de quem
  continua (D16, Q-135, revisão M-08); `reagendar` chama `voltar_envios_a_rascunho(sessao)` antes
  de `transicionar_status` (D2); novas `tcc_da_sessao`, `travar_tcc`, `travar_sessao` públicas
  (research A11) [US-23][US-24][RBN-DEF-02.4][RBN-DEF-03.3]
- [X] T011 IC-05 (parte 1) em `sigtcc/apps/defesa/views_defesa.py`: `_sessao_ou_404` vira
  `sessao_ou_404` (as chamadas existentes atualizadas), sem mudar comportamento (revisão I-04)
- [X] T012 IC-03 nos testes da spec 007: em `sigtcc/apps/defesa/tests/test_base_defesa.py`,
  `TesteDescartarAvaliacoesStub` dá lugar ao teste da delegação (apaga linhas e limpa envio); em
  `test_us23_banca.py`, troca entre titulares mantém o rascunho (com
  `connection.check_constraints()`), ida a Suplente descarta, acionamento do suplente apaga a
  cópia da assinatura do ausente e preserva `ban_usu_substituido`; em
  `test_us24_confirmar_reagendar_cancelar.py`, reagendar sessão "Em Andamento" devolve envios a
  rascunho, mantém as notas e limpa o parecer; cancelar descarta tudo (revisão I-08)
- [X] T013 Em `services_avaliacoes.py`: `visao_da_avaliacao(usuario, sessao)` com a tabela do
  research A7 (membro efetivo: própria avaliação + estados dos colegas; Orientador: também nota
  final e parecer preliminar só com os 3 envios; Professor da Disciplina, Secretaria, Aluno e
  Suplente não acionado: nada antes da liberação; depois: notas por critério e por avaliador,
  nota final e parecer; Observações só ao autor; papel na banca prevalece sobre Professor da
  Disciplina e Secretaria, revisão I-05) [US-27][RBN-DEF-06.8]
- [X] T014 [P] Em `sigtcc/apps/defesa/permissoes_defesa.py` (IC-09): `pode_avaliar(usuario,
  sessao)` (membro efetivo, sessão não Cancelada), `pode_registrar_parecer` e `pode_liberar`
  (papel "Orientador (Presidente)" na banca, revisão M-07) [US-25][US-27][RBN-DEF-05.3][RBN-DEF-06.4]
- [X] T015 [P] Criar `sigtcc/apps/defesa/services_documentos.py` com os stubs
  `ao_liberar_resultado(sessao)` (só log) e `declaracao_disponivel(sessao, usuario)` (devolve
  `False`), com a nota do contrato §2 para a feat-09 [US-27][RBN-DEF-08.3]

**Checkpoint**: estado, cálculo, descarte e sigilo testados; suíte da spec 007 passando com o IC-01.

---

## Phase 3: User Story 1 — Consultar os critérios oficiais (Priority: P1)

**Goal**: janela somente leitura com os 9 critérios (FR-001, FR-002).

**Independent Test**: abrir `defesa:criterios` como Docente e Membro Externo e conferir critérios,
pesos, somas e descrições, sem lançar notas.

- [X] T016 [P] [US1] Criar `sigtcc/apps/defesa/tests/test_us25_criterios.py`: cenário 1.1 (6 da
  Parte Escrita com pesos 0,5; 2,0; 1,0; 2,0; 0,5; 1,0 = 7,0; 3 da Parte Oral com 1,0; 1,5; 0,5 =
  3,0; total 10,0; descrições Exemplar 8,0–10,0, Competente 6,0–7,9, Necessita de Trabalho
  0,0–5,9) e cenário 1.2 (nenhuma rota grava `Criterios`; Coordenador não edita; Aluno e
  Secretaria recebem 403) [US-25][RBN-DEF-04.1][RBN-DEF-04.2]
- [X] T017 [US1] Criar `sigtcc/apps/defesa/views_avaliacoes.py` com `criterios(request)`
  (perfis `docente` e `membro_externo`), a rota `defesa:criterios` em
  `sigtcc/apps/defesa/urls.py` (IC-09) e o template `sigtcc/templates/defesa/criterios.html`
  (protótipo de 17/10) [US-25][RBN-DEF-04.2]

**Checkpoint**: US1 testada de forma independente.

---

## Phase 4: User Story 2 — Ver as minhas bancas (Priority: P1)

**Goal**: Minhas bancas para Docente e Membro Externo (FR-003 a FR-006).

**Independent Test**: com sessões em vários status, entrar como membro (Docente e Membro Externo) e
conferir lista, destaques e botões.

- [X] T018 [P] [US2] Criar `sigtcc/apps/defesa/tests/test_minhas_bancas.py`: cenários 2.1 a 2.8
  (sem Canceladas; destaque só para membros efetivos pendentes; Membro Externo só vê as suas;
  suplente acionado com Avaliar; Suplente não acionado sem Avaliar; Declaração só com
  `declaracao_disponivel` verdadeiro; login antes; clicar abre a Sessão de defesa) e MA-12 sem
  bancas; número fixo de consultas com várias linhas (revisão M-12)
  [US-25][RBN-DEF-05.4][RBN-DEF-08.3]
- [X] T019 [US2] Em `services_avaliacoes.py`: `minhas_bancas(usuario)` (linhas de `BancaDefesa`
  do usuário, sem sessões "Cancelada", por data e hora, `select_related`, estados da T006, link do
  Documento por `Subquery` sobre `HistoricoEnviosEntregas`, `declaracao_disponivel`), chamando
  `services_defesa.iniciar_sessoes_vencidas()` antes (research A8) [US-25][RBN-DEF-05.4]
- [X] T020 [US2] Em `views_avaliacoes.py`: `minhas_bancas(request)`, rota `defesa:minhas_bancas`
  e template `sigtcc/templates/defesa/minhas_bancas.html` (papel, data, horário, aluno, título,
  status, atalhos Documento, Critérios de avaliação, Avaliar e Declaração; linha abre
  `defesa:sessao`) [US-25][RBN-DEF-05.4]
- [X] T021 [US2] IC-02 em `sigtcc/apps/cadastro/menu.py`: item "Minhas bancas" (perfis `docente`
  e `membro_externo`, rota `defesa:minhas_bancas`, ícone do protótipo), sem mexer nos demais;
  conferir `test_base_comum.py` (menu) [US-25][RBN-DEF-05.4]

**Checkpoint**: US2 testada; Membro Externo entra por Minhas bancas.

---

## Phase 5: User Story 3 — Lançar, assinar e enviar a avaliação (Priority: P1)

**Goal**: formulário Avaliação com rascunho, envio assinado e reabertura (FR-007 a FR-022).

**Independent Test**: com sessão Em Andamento, lançar os 9 critérios com assinatura e conferir
envio, nota individual e "Enviada", sem liberar.

- [X] T022 [P] [US3] Criar `sigtcc/apps/defesa/tests/test_us25_avaliacao.py`: cenários 3.1 a 3.5,
  3.9, 3.10, 3.14 a 3.19 (envio com nota individual e data; Competente 7,5 aceito e 8,5 recusado
  com a mensagem exata; Observações opcionais e 501 caracteres recusados com MA-02; rascunho da
  Parte Escrita com a sessão Agendada, Parte Oral e envio bloqueados mesmo por POST; Salvar com
  a sessão Reagendada não apaga notas orais, revisão I-01; critério com só conceito, só nota ou só
  observações bloqueia com MA-01; reabrir e reenviar recalcula e limpa o parecer; avaliação
  Enviada recusa Salvar e Enviar com MA-13, revisão I-02; fora da banca, Suplente não acionado e
  sessão Cancelada com "Acesso restrito..."; Realizada só leitura; login antes; início
  automático ao abrir no horário, revisão I-04) [US-25][RBN-DEF-05.1][RBN-DEF-05.2][RBN-DEF-05.3][RBN-DEF-06.1]
- [X] T023 [P] [US3] Criar `sigtcc/apps/defesa/tests/test_us26_assinatura.py`: cenários 3.1
  (PNG de 500 KB, prévia e cópia com data e hora), 3.6 (assinatura do perfil sem novo arquivo),
  3.7 (Salvar esta imagem no meu perfil atualiza `doc_assinatura_path`/`mem_assinatura_path`),
  3.8 (Atualizar imagem), 3.11 (sem assinatura: mensagem exata), 3.12 (3 MB: mensagem de 2 MB,
  nada gravado), 3.13 (.pdf: mensagem de formato), imagem de 3000 × 3000 recusada com a MA-14
  (revisão I-11), perfil sem arquivo no disco esconde a opção, cópia apagada quando a transação desfaz
  (revisão M-11), rota `defesa:assinatura_avaliacao` só para o dono [US-26][RBN-DEF-05.2]
- [X] T024 [US3] Criar `sigtcc/apps/defesa/forms_avaliacoes.py`: formset fixo dos 9 critérios
  (Conceito em `Conceito`; Nota com vírgula e uma casa, dentro da faixa: Exemplar 8,0 a 10,0,
  Competente 6,0 a 7,9, Necessita de Trabalho 0,0 a 5,9; Observações até 500 caracteres;
  critério vazio ou completo, MA-01) e `AssinaturaForm` (arquivo PNG/JPG, `size` conferido antes
  de `services.tipo_da_assinatura` para separar as mensagens de 2 MB e de formato, revisão M-09;
  "usar a do perfil"; "Salvar esta imagem no meu perfil") [US-25][US-26][RBN-DEF-05.2]
- [X] T025 [US3] Em `services_avaliacoes.py`: `salvar_rascunho(usuario, def_id, linhas)`,
  `enviar_avaliacao(usuario, def_id, linhas, assinatura)` e `reabrir_avaliacao(usuario, def_id)`,
  cada um com `transaction.atomic()` e a trava `travar_tcc` → `travar_sessao` → linha
  `BancaDefesa`; reconferir status, liberação e vínculo depois de travar; só critérios liberados
  pelo status (bloqueados não lidos, nem atualizados, nem apagados); Enviada recusa Salvar e
  Enviar (MA-13); depois da liberação tudo recusado (MA-04); `reabrir` limpa envio, assinatura e
  `def_parecer` (research A4, A6) [US-25][US-27][RBN-DEF-05.1][RBN-DEF-05.2][RBN-DEF-06.1][RBN-DEF-06.4]
- [X] T026 [US3] Em `services_avaliacoes.py`: cópia da assinatura em
  `assinaturas_banca/<def_id>_<usu_id>_<aleatório>.<ext>` no `default_storage`, a partir do
  arquivo anexado ou do perfil (`services.caminho_da_assinatura`); validação de dimensões até
  2000 × 1000 com o Pillow (acima disso, MA-14, sem reduzir; imagem que não abre, mensagem de
  formato da US-26 E3); cópia anterior apagada depois do
  commit; cópia nova apagada se a transação desfizer; "Salvar no perfil" chama
  `services.salvar_assinatura` na mesma transação (research A5) [US-26][RBN-DEF-05.2]
- [X] T027 [US3] Em `views_avaliacoes.py`: `avaliacao(request, def_id)` (GET e POST com
  `acao=salvar`/`acao=enviar`), `reabrir(request, def_id)` e `assinatura(request, def_id)`
  (`FileResponse` só para o dono), todas via `views_defesa.sessao_ou_404`; rotas
  `defesa:avaliacao`, `defesa:reabrir_avaliacao`, `defesa:assinatura_avaliacao` (contracts/rotas.md)
  [US-25][US-26][RBN-DEF-05.3]
- [X] T028 [US3] Template `sigtcc/templates/defesa/avaliacao.html` (cabeçalho com título, aluno,
  orientador e link do Documento; 9 linhas com peso; nota MA-03; bloco Assinatura do Membro da
  Banca com Anexar imagem, Atualizar imagem, prévia, usar a do perfil, Salvar esta imagem no meu
  perfil; botões Salvar e Enviar avaliação assinada; só leitura quando Enviada ou Realizada) e
  `sigtcc/static/js/avaliacao.js` (prévia com `URL.createObjectURL`, conferência imediata de
  tamanho e extensão, habilitação dos campos; sem regra de negócio) [US-25][US-26][RBN-DEF-05.2]

**Checkpoint**: US3 testada; os 3 envios podem ser feitos.

---

## Phase 6: User Story 4 — Apurar e liberar o resultado (Priority: P1)

**Goal**: parecer, liberação, status, notificações e ponto de chamada da feat-09 (FR-023 a FR-030).

**Independent Test**: com sessão Em Andamento e 3 envios (ou não), abrir a sessão como Orientador e
conferir cálculo, parecer, bloqueios e liberação.

- [X] T029 [P] [US4] Criar `sigtcc/apps/defesa/tests/test_us27_liberacao.py`: cenários 4.1 a 4.15
  (TCC 2 Aprovado com Correções: sessão Realizada, Status do TCC, histórico e o resultado gravado
  em `Defesas` — o que o aluno vê é testado na T036, US5; `/speckit-analyze` I3; cálculo; TCC 1 7,2 → Aprovado para TCC 2; TCC 2 8,5 Aprovado; 5,4 →
  Reprovado sem Folha; Qualis A eleva a 6,0; reajuste recalcula e limpa parecer; suplente;
  login; pendente desabilita Liberar e destaca; sem parecer em TCC 2: mensagem no Registrar
  parecer e Liberar desabilitado, também por POST; não Orientador: mensagem da E4 por POST;
  depois da liberação, reabrir recusado; D10: nota mudou → reabre confirmação, e em TCC 2 subiu a
  6,0 → volta à sessão para Registrar parecer, revisão I-03; reagendamento devolve a rascunho);
  `ao_liberar_resultado` chamado depois do commit com `robust=True` e uma exceção nele não impede
  os e-mails (revisão I-10); duas liberações seguidas: a segunda não grava; SC-004: a liberação
  muda `def_status` e `tcc_status` só por `services_defesa.transicionar_status` e
  `services_turmas.atualizar_status_tcc` (conferido com `mock.patch(..., wraps=...)`, chamados
  uma vez cada) e nenhum outro ponto de `services_avaliacoes.py` grava `def_status`,
  `tcc_status`, `HistoricoDefesas` ou `HistoricoStatusTCC` (`/speckit-analyze` C1)
  [US-27][RBN-DEF-06.2][RBN-DEF-06.3][RBN-DEF-06.4][RBN-DEF-06.6][RBN-DEF-06.7]
- [X] T030 [US4] Em `services_avaliacoes.py`: `apuracao(sessao)` (nota final e parecer
  preliminar só com os 3 envios; Reprovado automático abaixo de 6,0, ignorando `def_parecer`
  gravado; Aprovado para TCC 2 em TCC 1 ≥ 6,0; em TCC 2 ≥ 6,0, o `def_parecer` gravado ou
  nenhum; flag de Liberar habilitado) e `registrar_parecer(usuario, def_id, parecer)` (só
  Orientador, Em Andamento, 3 envios, TCC 2 ≥ 6,0; Aprovado ou Aprovado com Correções; sem
  escolha: "Selecione o parecer da banca para continuar") [US-27][RBN-DEF-06.3][RBN-DEF-06.6]
- [X] T031 [US4] Em `services_avaliacoes.py`: `liberar_resultado(usuario, def_id,
  nota_confirmada, parecer_confirmado)` numa transação com `travar_tcc` → `travar_sessao`;
  confere Orientador, "Em Andamento", 3 envios e parecer; recalcula com a homologação vigente; se
  diferir, não grava e devolve os valores novos (ou "precisa registrar parecer" em TCC 2 ≥ 6,0);
  grava `def_nota_final`, `def_parecer`, `def_data_liberacao_resultado`; chama
  `services_defesa.transicionar_status(sessao, StatusSessao.REALIZADA, usuario)` e
  `services_turmas.atualizar_status_tcc(tcc, turma, usuario, parecer,
  GatilhoStatusTCC.LIBERACAO_DO_RESULTADO)`; nunca grava `def_status` nem `Historico_Defesas`
  direto (research A6) [US-27][RBN-DEF-06.4][RBN-DEF-06.7][RBN-DEF-01.2]
- [X] T032 [US4] Em `services_avaliacoes.py` (dentro de `liberar_resultado`): avisos MA-06 (Aluno),
  MA-07 (membros efetivos) e MA-08 (Secretaria do curso) por `services.notificar` e
  `services.enviar_email_apos_commit`, sem a nota no e-mail, com os templates
  `sigtcc/templates/defesa/emails/resultado_aluno.txt`, `resultado_banca.txt` e
  `resultado_secretaria.txt` (assunto "SIGTCC: resultado da defesa"); e
  `transaction.on_commit(lambda: services_documentos.ao_liberar_resultado(sessao), robust=True)`
  (FR-028, FR-030; DV-01) [US-27][RBN-DEF-06.4][RBN-DEF-08.3]
- [X] T033 [US4] Em `views_avaliacoes.py`: `registrar_parecer(request, def_id)` (POST) e
  `liberar_resultado(request, def_id)` (GET: confirmação MA-05; POST: liberação; nota mudou:
  reabre a confirmação; TCC 2 ≥ 6,0 sem parecer: volta à sessão), via `sessao_ou_404`; rotas
  `defesa:registrar_parecer` e `defesa:liberar_resultado`; template
  `sigtcc/templates/defesa/confirmar_liberacao.html` [US-27][RBN-DEF-06.3][RBN-DEF-06.4]
- [X] T034 [US4] IC-05 (parte 2) em `views_defesa.sessao` e `sigtcc/templates/defesa/sessao.html`:
  contexto de `visao_da_avaliacao` e `apuracao`; parciais `sigtcc/templates/defesa/_bloco_avaliacao.html`
  (estados, Avaliar, Reabrir minha avaliação, pendentes em destaque) e `_bloco_resultado.html`
  (nota final, parecer, Registrar parecer, Liberar Resultado desabilitado quando for o caso)
  preenchendo `{% block avaliacao %}` e `{% block resultado %}`, sem reescrever o cabeçalho
  [US-27][RBN-DEF-06.6][RBN-DEF-06.8]
- [X] T035 [US4] IC-06 em `sigtcc/templates/defesa/historico.html` (e o contexto em
  `views_defesa.historico`): nota final e parecer no evento "Liberação do Resultado", lidos de
  `Defesas` (D15; FR-037); teste em `test_us27_liberacao.py` [US-27][RBN-DEF-01.6]

**Checkpoint**: US4 testada; liberação completa sem PDFs (feat-09).

---

## Phase 7: User Story 5 — Sigilo e resultado para o aluno (Priority: P1)

**Goal**: sigilo em todas as telas e resultado na aba Meu TCC (FR-031 a FR-033).

**Independent Test**: com rascunhos e envios, abrir as telas como cada perfil, antes e depois da
liberação.

- [X] T036 [P] [US5] Criar `sigtcc/apps/defesa/tests/test_sigilo.py`: cenários 5.1 a 5.8 por
  perfil (membro, Orientador, Suplente não acionado, Professor da Disciplina, Secretaria, Aluno)
  e por tela (sessão, Minhas bancas, Avaliação, Defesas, Meu TCC, endereço direto), antes e
  depois da liberação; Observações só ao autor; Professor da Disciplina que é Orientador vê como
  Orientador (revisão I-05); Data Limite só em TCC 2 Aprovado e Aprovado com Correções (Q-127) e
  ausente sem a entrega Versão Final cadastrada; e a parte do cenário 4.1 que trata do aluno (vê
  nota final, parecer e Data Limite depois da liberação; `/speckit-analyze` I3)
  [US-27][RBN-DEF-06.5][RBN-DEF-06.8]
- [X] T037 [US5] Em `services_avaliacoes.py`: `resultado_da_sessao(sessao)` e
  `resultado_para_o_aluno(tcc)` (última sessão Realizada; nota final, parecer e, em TCC 2 Aprovado
  ou Aprovado com Correções, `tma_data_limite` da entrega do tipo Versão Final da turma)
  [US-27][RBN-DEF-06.5]
- [X] T038 [US5] IC-07: `sigtcc/templates/defesa/_resultado_aluno.html` incluído em
  `sigtcc/templates/cadastro/tcc/meu_tcc.html`, com o contexto em
  `sigtcc/apps/cadastro/views_tcc.py` (`meu_tcc`), só depois da liberação; conferir os testes da
  spec 005 da aba Meu TCC [US-27][RBN-DEF-06.5]

**Checkpoint**: todas as histórias testadas de forma independente.

---

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T039 [P] IC-08 em `sigtcc/apps/cadastro/management/commands/popular_demo.py`: avaliações de
  exemplo só por `services_avaliacoes` (sessão Em Andamento com 2 enviadas e 1 rascunho; sessão
  de TCC 2 com 3 envios, pronta para liberar; uma sessão liberada de TCC 1), com a assinatura
  estática `sigtcc/static/img/assinatura_demo.png` (research A12; revisão I-15); conferir
  `test_base_defesa.TestePopularDemo`
- [ ] T040 [P] Criar `sigtcc/apps/defesa/tests/test_mensagens_avaliacao.py`: textos das US-25 a
  US-27 conferidos, caractere por caractere, contra `docs/fonte/Historias_de_Usuario_v3_4.md`, e
  MA-01 a MA-14 contra a tabela da spec 008 (SC-007; mesmo padrão de `test_mensagens_defesa.py`)
- [ ] T041 [P] Q-134 (documentos do repositório): diagrama 28 em
  `docs/diagramas/Diagramas_Sequencia_PlantUML_v2.md` (geração da Ata e da Folha no passo
  `baixarDocumento`, sem `def_*_path` na liberação); `docs/arquitetura/Componentes_SIGTCC.drawio`,
  `Implantacao_SIGTCC.drawio` e os PNG em `docs/arquitetura/imagens/` ("PDFs gerados sob
  demanda; assinaturas no disco do serviço"); `docs/diagramas/Rastreabilidade_Diagramas_Codigo.md`
  (participantes da avaliação → `services_avaliacoes`, `views_avaliacoes`); o PGCS fica com
  Célio Benjamim no Drive
- [ ] T042 [P] `CHANGELOG.md` em "Não lançado": feature 008, a decisão de PDFs sob demanda sem
  armazenamento externo (sai do "Planejado para a v0.3.0"), o `xhtml2pdf` e as emendas D2 e D16
  da spec 007
- [ ] T043 Rodar `.venv\Scripts\python.exe manage.py test` (suíte inteira) e
  `pre-commit run --all-files`; corrigir o que falhar
- [ ] T044 Validação manual pelo roteiro de [quickstart.md](quickstart.md) (16 passos), com o
  resultado registrado em `specs/008-avaliacao-resultados/pr-feat-08.md`
- [ ] T045 Escrever `specs/008-avaliacao-resultados/pr-feat-08.md` com o modelo do PGCS 6.3:
  título `[Feat-08] Avaliação e Resultados (US-25, US-26, US-27)`, IC-01 a IC-11 com arquivo e
  motivo (Q-128), resultado da instalação no Linux limpo (T001), pendências Q-131 a Q-134

---

## Dependencies & Execution Order

- **Phase 1 (Setup)**: T001 antes de T002/T003; T004 e T005 em paralelo.
- **Phase 2 (Foundational)**: depende de T004/T005; T006 → T007 → T009 → T010 → T012; T011,
  T013, T014, T015 em paralelo depois de T006. Bloqueia todas as histórias.
- **US1 (Phase 3)** → **US2 (Phase 4)**: em sequência (as duas mexem em `views_avaliacoes.py` e
  `urls.py`; `/speckit-analyze` I2).
- **US3 (Phase 5)**: depende da US2 (mesmos arquivos de views e rotas).
- **US4 (Phase 6)**: depende da US3 (precisa dos envios).
- **US5 (Phase 7)**: depende da US4 (precisa da liberação).
- **Polish**: depois das histórias; T041 e T042 podem começar a qualquer momento.

### Commits sugeridos

1. `chore(config): adicionar xhtml2pdf as dependencias` (T001)
2. `feat(feat-08): gerar PDF em memoria sem acesso a rede` (T002, T003)
3. `feat(feat-08): calcular notas e descartar avaliacoes` (T004 a T015)
4. `feat(feat-08): exibir criterios e minhas bancas` (T016 a T021)
5. `feat(feat-08): lancar e enviar a avaliacao assinada` (T022 a T028)
6. `feat(feat-08): liberar o resultado da defesa` (T029 a T035)
7. `feat(feat-08): mostrar o resultado ao aluno com sigilo` (T036 a T038)
8. `feat(feat-08): popular avaliacoes de demonstracao` (T039, T040)
9. `docs(feat-08): ...` (T041, T042, T044, T045)

## Parallel Example: User Story 3

```text
T022 test_us25_avaliacao.py   ║  T023 test_us26_assinatura.py   (arquivos diferentes)
T024 forms_avaliacoes.py      →  T025/T026 services  →  T027 views  →  T028 template e JS
```

## Implementation Strategy

- **MVP**: Fases 1 e 2 + US1 a US4 (sem a US4 não há resultado oficial; a US5 completa o sigilo
  nas telas, mas `visao_da_avaliacao` já existe desde a Fase 2).
- Entrega incremental por fase, cada uma com os testes passando e commit próprio.
