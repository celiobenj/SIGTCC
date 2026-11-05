# Feature Specification: Avaliação e Resultados do SIGTCC

**Feature Branch**: `feature/feat-08-avaliacao`

**Created**: 2026-11-03

**Status**: Draft

**Input**: User description: "Avaliação e Resultados do SIGTCC: US-25 (lançar as notas), US-26 (assinatura) e US-27 (liberar o resultado), mais os critérios fixos de avaliação (DEF-04.1 e DEF-04.2) e a tela Minhas bancas (DEF-05.4). Use as seções dessas US em docs/fonte/Historias_de_Usuario_v3_4.md, com regras (RBN), fluxos alternativos, exceções e cenários de aceite. Siga specs/007-agendamento-banca/contracts/servicos-defesa.md: usar transicionar_status (para Realizada, só a partir de Em Andamento), registrar_evento, membros_efetivos e os blocos do template sessao.html; nunca escrever def_status nem Historico_Defesas diretamente e nunca criar sessão. Incluir services_avaliacoes.descartar_avaliacoes(sessao, membro=None), que substitui o stub de services_defesa sem mudar a assinatura (contrato §6, Q-125). Regras de cálculo: nota individual = soma de nota × peso ÷ 10 com uma casa decimal e arredondamento comercial (Decimal, ROUND_HALF_UP), nota final = média das 3 notas arredondadas, Qualis A ou B homologado garante 6,0. Sigilo das notas conforme DEF-06.8. A geração dos documentos é da feat-09; aqui só o ponto de chamada na liberação."

**Responsável pelas US de origem**: Célio Benjamim (US-25, US-26 e US-27).

**Fontes**: Histórias de Usuário v3.4 (US-25, US-26 e US-27); Matriz de Requisitos de 17/10, aba
`Requisitos_Defesa` (RAN-DEF-04 a RAN-DEF-06: RBN-DEF-04.1, 04.2, 05.1 a 05.4 e 06.1 a 06.8);
dicionário de dados de 18/10 (seções 3.1.4, 3.6.1, 3.6.4 e 3.6.6); diagramas de sequência
`AvaliarCriterios` e `LiberarResultadoDefesa` (PlantUML v2).

## Dependências e reaproveitamento

- **Modelo de dados**: já existe (spec 001). Esta spec **não cria tabelas nem colunas**. Usa:
  - `Criterios` (dicionário 3.1.4): os 9 critérios oficiais, já carregados pela migração inicial
    com os pesos da matriz e os descritores provisórios dos conceitos (índice Q-03 e Q-18);
  - `Avaliacoes` (3.6.6): uma linha por membro e critério, com conceito, nota, observações e data
    e hora; a FK composta para `Banca_Defesa` é verificada só no fim da transação (migração
    `0002_fk_composta_avaliacoes`, `DEFERRABLE INITIALLY DEFERRED`);
  - `BancaDefesa` (3.6.4): grava `ban_assinatura_path` e `ban_data_envio`. O estado da avaliação
    de cada membro é derivado pela regra do dicionário (3.6.4) e exibido com os rótulos da matriz
    (RBN-DEF-06.8) e da US-27: **Não avaliou** (sem linhas em `Avaliacoes`), **Rascunho salvo**
    (com linhas e `ban_data_envio` nulo) e **Enviada** (`ban_data_envio` preenchido);
  - `Defesas` (3.6.1): grava `def_parecer`, `def_nota_final` e `def_data_liberacao_resultado`.
    **Não grava** `def_status` (só por `transicionar_status`), `def_ocorrencias`,
    `def_ata_final_path` nem `def_folha_aprovacao_path` (ficam sem uso: os PDFs são gerados sob
    demanda e não são gravados; Clarifications 2026-11-03, Q-133);
  - choices `ComponenteCriterio`, `Conceito`, `Parecer`, `PapelBanca` e `StatusSessao`
    (`sigtcc/apps/defesa/choices.py`).
- **Contrato da spec 007** (`specs/007-agendamento-banca/contracts/servicos-defesa.md`):
  - `services_defesa.transicionar_status(sessao, StatusSessao.REALIZADA, autor)` na liberação do
    resultado, **só a partir de "Em Andamento"**, com a sessão já travada (`select_for_update`)
    na mesma transação. É a única forma de mudar `def_status` e de gravar `Historico_Defesas`
    com mudança de status; esta spec **nunca** escreve `def_status` nem cria `HistoricoDefesas`
    diretamente e **nunca cria sessão** (§1);
  - `services_defesa.registrar_evento(...)` só se for preciso gravar um evento sem mudança de
    status (§2). A liberação usa o evento "Liberação do Resultado", gravado pelo próprio
    `transicionar_status`;
  - `services_defesa.membros_efetivos(sessao)`: os 3 membros que avaliam (Orientador, 1º e 2º
    Avaliador, com o suplente acionado no lugar do ausente). É a base do acesso ao formulário
    (RBN-DEF-05.3), do quórum (RBN-DEF-06.6) e do cálculo (RBN-DEF-06.2) (§2);
  - template `sigtcc/templates/defesa/sessao.html`: esta spec preenche os blocos
    `{% block avaliacao %}` (status de envio de cada membro e acesso ao formulário) e
    `{% block resultado %}` (nota final, parecer e Liberar Resultado), sem reescrever o cabeçalho
    da sessão (§3). Os blocos `documentos`, `ouvintes` e `ocorrencias` ficam para a feat-09;
  - permissões de abertura da janela "Sessão de defesa" da spec 007 (FR-030: membros da banca,
    Professor da Disciplina da turma, Secretaria do curso e Aluno do próprio TCC), sem alteração.
- **Serviço desta spec que substitui o stub da spec 007** (contrato §6; índice Q-125):
  `services_avaliacoes.descartar_avaliacoes(sessao, membro=None)` apaga as linhas de
  `Avaliacoes` do membro (ou de todos, com `membro=None`) e limpa a assinatura e a data de envio
  da linha de `BancaDefesa`, quando ela ainda existe. `services_defesa.descartar_avaliacoes`
  passa a delegar para essa função, **com a mesma assinatura e nos mesmos 3 pontos de chamada**
  (cancelamento: todos; alteração da banca: o substituído; acionamento do suplente: o ausente),
  dentro da transação de quem chama. A FK composta verificada no fim da transação garante que
  nenhuma avaliação fique órfã.
- **Mudanças em código da spec 007** (Q-128; relatadas no plano e no PR):
  - `services_defesa.alterar_banca`: hoje descarta as avaliações de todo membro que sai de um
    papel, inclusive quem só troca de papel e continua na banca. Passa a descartar **só quem saiu
    da banca** (RBN-DEF-02.4: "membro removido"); quem troca de papel mantém o rascunho
    (Clarifications 2026-11-03, D16);
  - `services_defesa.reagendar`: no reagendamento de uma sessão "Em Andamento", chama o serviço
    desta spec que devolve as avaliações enviadas a "Rascunho salvo" (FR-035; D2).
- **Serviços de outras specs reutilizados**:
  - `services_turmas.atualizar_status_tcc(tcc, turma, autor, novo_status, gatilho)` (spec 005,
    contrato §2) com o gatilho "Liberação do resultado". A tabela de transições já aceita
    "Apto para Defesa" → "Aprovado para TCC 2", "Aprovado", "Aprovado com Correções" ou
    "Reprovado". Quem chama trava turma → aluno → TCC antes;
  - `services_artigos.tem_artigo_homologado_qualis_ab(tcc)` (spec 006, contrato §4), chamada no
    momento da liberação, com o TCC já travado (RBN-DEF-06.2: vale a homologação existente
    nesse momento);
  - `services.tipo_da_assinatura(arquivo)` e o armazenamento privado da imagem de assinatura do
    perfil (spec 003, US-38: `doc_assinatura_path` do Docente e `mem_assinatura_path` do Membro
    Externo), para validar e reaproveitar a assinatura;
  - `services.notificar(...)` e `services.enviar_email_apos_commit(...)` (contrato da spec 004,
    §4), únicas formas de notificar e enviar e-mail;
  - `services_entregas.link_mais_recente(entrega)` (spec 005, §3): link do Documento para Defesa
    nas telas Minhas bancas e Avaliação;
  - a entrega do tipo Versão Final da turma de TCC 2 (spec 005, US-43) para mostrar a Data
    Limite ao aluno (RBN-DEF-06.5).
- **Ponto de chamada para a feat-09** (US-30): depois de gravada a liberação, esta spec chama
  um único serviço da feat-09 que envia as declarações de participação por e-mail
  (RBN-DEF-08.3). Até a feat-09 entregar a função, fica um stub com a assinatura combinada, que
  só registra em log (mesmo padrão do `descartar_avaliacoes` da spec 007). A Ata Final e a Folha
  de Aprovação **não são geradas na liberação**: a feat-09 as gera a cada download, a partir dos
  dados congelados (Clarifications 2026-11-03). O botão **Declaração** de Minhas bancas (US-25,
  fluxo F) só aparece quando a feat-09 informar que a declaração existe.
- **Infraestrutura de PDF entregue por esta feature** (para a feat-09): o `xhtml2pdf` e um
  utilitário que gera o PDF em memória e o entrega pela view que conferiu a permissão, sem
  endereço público e sem gravar arquivo.

## Contratos desta feature (o que a feat-09 e outras telas vão consumir)

- `services_avaliacoes.descartar_avaliacoes(sessao, membro=None)` (ver acima).
- `services_avaliacoes.estado_da_avaliacao(sessao, membro)`: "Não avaliou", "Rascunho salvo" ou
  "Enviada" (dicionário 3.6.4; rótulos da RBN-DEF-06.8).
- `services_avaliacoes.voltar_envios_a_rascunho(sessao)` (nome final no plano): chamado pela spec
  007 no reagendamento de sessão "Em Andamento" (FR-035).
- `services_avaliacoes.nota_individual(sessao, membro)` e
  `services_avaliacoes.nota_final(sessao)`: cálculo do RBN-DEF-06.1 e do RBN-DEF-06.2, em
  `Decimal` com `ROUND_HALF_UP` e uma casa decimal. A feat-09 usa para a Ata Final, depois da
  liberação.
- `services_avaliacoes.resultado_da_sessao(sessao)`: nota final, parecer e data da liberação de
  uma sessão "Realizada", para a Ata Final, a Folha de Aprovação e a tela do aluno.
- Stubs `services_documentos.ao_liberar_resultado(sessao)` e
  `services_documentos.declaracao_disponivel(sessao, usuario)`, substituídos pela feat-09 sem
  mudar a assinatura nem o ponto de chamada; utilitário `pdf.gerar_pdf`/`pdf.resposta_pdf` (plan,
  research A9 e A10).

## Clarifications

### Session 2026-11-03

- Q: `descartar_avaliacoes` substitui o stub da spec 007 sem mudar a assinatura nem os 3 pontos
  de chamada? → A (Célio Benjamim, na descrição desta feature): **sim**. A função real fica em
  `services_avaliacoes.py`, e `services_defesa.descartar_avaliacoes` passa a delegar para ela.
  Índice Q-125 respondido.
- Q: A Data Limite da Versão Final aparece ao aluno em qual parecer? A matriz (RBN-DEF-06.5) diz
  "Em TCC 2, mostra também a Data Limite da entrega do tipo Versão Final"; a US-27 (passo 13 e
  pós-condições) só cita o parecer "Aprovado com Correções", e o glossário da matriz diz que, no
  parecer "Aprovado", também "Falta a Versão Final". → A (Célio Benjamim, 2026-11-03): **em todo
  TCC 2 aprovado** (Aprovado e Aprovado com Correções), como diz a matriz, que prevalece. Os dois
  pareceres entregam a Versão Final, como já dizem a US-29 (fluxo alternativo A) e a spec 005; o
  glossário da matriz não muda. Reprovado e Aprovado para TCC 2 não mostram a Data Limite. Índice
  Q-127.
- Q: Esta spec pode mexer em código já mesclado de outras specs (stub de
  `descartar_avaliacoes` da spec 007, menu Minhas bancas, seção do resultado na aba Meu TCC da
  spec 005, `popular_demo`)? → A (Célio Benjamim, 2026-11-03): **sim, no que for necessário**,
  sempre relatando cada mudança (arquivo e motivo) no plano e no PR. Índice Q-128.
- Q: Os textos sem texto exato nas US (MA-01 a MA-12) podem ser usados? → A (Célio Benjamim,
  2026-11-03): **sim, todos aprovados** como estão na tabela "Mensagens a validar com a PO".
  Índice Q-129. **Complemento** (`/speckit-analyze`, 2026-11-03, Célio Benjamim): MA-13 (a MA-04
  diz que o resultado já foi liberado e não serve para a avaliação apenas enviada; I1) e MA-14
  (imagem grande demais em pixels recusada com mensagem própria, sem reduzir a imagem
  automaticamente; A1), ambas aprovadas.

Conferência do analista-requisitos (2026-11-03): pontos a decidir D1 a D16, decididos por Célio
Benjamim na mesma data (índice Q-130; a divergência do D8 fica aberta para a PO na Q-131):

- Q (D1): Quando o botão Liberar Resultado fica disponível? → A: **depois dos 3 envios e do
  parecer definido** (RBN-DEF-06.4). Em TCC 2, o botão fica desabilitado até o Orientador
  registrar o parecer; a mensagem "Selecione o parecer da banca para continuar" aparece na
  confirmação do Registrar parecer (US-27 E3, passo 7). O servidor também recusa a liberação sem
  parecer. FR-023, FR-025 e cenário 4.11.
- Q (D2): No reagendamento de uma sessão "Em Andamento", as avaliações enviadas continuam
  "Enviada"? → A: **não**. As notas são mantidas (RBN-DEF-03.3), mas todas as avaliações enviadas
  voltam a "Rascunho salvo" (sem data de envio e sem assinatura), e cada membro reenvia assinando
  quando a nova sessão estiver "Em Andamento" (RBN-DEF-05.1, RBN-DEF-06.6). FR-035 e cenário 4.15.
- Q (D3): O que acontece com o parecer escolhido em TCC 2 quando um reenvio muda a nota final?
  → A: **é limpo**, e o Orientador escolhe de novo (RBN-DEF-06.1: "o parecer automático é
  recalculado"). **Revista no `/speckit-plan`** (revisão do `arquiteto-django`, B-01; Célio
  Benjamim, 2026-11-03; Q-135): como não há coluna para guardar a nota do momento do registro, o
  parecer escolhido é limpo **sempre que os 3 envios deixam de estar completos** (Reabrir minha
  avaliação, acionamento do suplente, alteração da banca, reagendamento ou cancelamento), mesmo
  que a nota final volte igual. FR-021 e Edge Cases.
- Q (D4): Observações num critério sem conceito e nota, ao Salvar? → A: bloquear com a MA-01,
  como o critério só com conceito ou só com nota. FR-013.
- Q (D5): Salvar fica disponível com a sessão "Em Andamento"? → A: sim. FR-012.
- Q (D6): Reabrir minha avaliação limpa a assinatura? → A: sim: a avaliação volta a "Rascunho
  salvo" sem data de envio e sem assinatura, e o reenvio exige assinar de novo (US-27 E: "reenvia
  com a assinatura"). FR-021.
- Q (D7): O que Professor da Disciplina, Secretaria e Aluno veem antes da liberação? → A: **o que
  dizem as US, ao pé da letra** (US-27 passo 2 e cenário 3): cada avaliador vê só a própria
  avaliação e o status dos colegas; o Orientador vê a nota final só depois dos 3 envios; o aluno
  não vê nenhuma nota. Quem as US não citam (Professor da Disciplina e Secretaria) não vê nada do
  bloco de avaliação, nem o status de envio; o Aluno também não vê o status. As Observações,
  que nenhuma fonte manda exibir a outros, ficam visíveis só ao próprio avaliador. FR-031,
  FR-032 e cenários 5.3 e 5.7.
- Q (D8): Quem é notificado na liberação? → A: **Aluno, membros efetivos da banca e Secretaria do
  curso**. **Diverge da US-27**, que só cita a Secretaria (atores secundários); fica registrado na
  seção "Divergências em relação às US" e na Q-131 para revisar depois. FR-030.
- Q (D9): Uma falha na geração dos PDFs desfaz a liberação? → A: não; o ponto de chamada é
  acionado depois de gravada a liberação, e o contrato com a feat-09 (nome do serviço e como ela
  informa que a declaração existe) é definido no plano. FR-028.
- Q (D10): E se a nota final ou o parecer mudarem entre a confirmação e a gravação (por exemplo,
  um artigo homologado nesse meio-tempo)? → A: **o sistema não grava e reabre a confirmação** com
  a nova nota e o novo parecer (RBN-DEF-06.2). FR-027 e cenário 4.14.
- Q (D11): O destaque de pendência em Minhas bancas vale para o Suplente não acionado? → A: não,
  só para os membros efetivos. FR-004.
- Q (D12): O formulário de uma sessão Cancelada aberto pelo endereço direto? → A: recusar com
  "Acesso restrito aos membros avaliadores da banca". FR-036.
- Q (D13): Liberação com a turma arquivada? → A: não acontece: o arquivamento da turma já é
  recusado com sessão ativa (spec 004, `services_turmas.arquivar_turma`). Edge Cases.
- Q (D14): Cada envio fica registrado (Não Repúdio, RAN-DEF-05)? → A: só o último envio fica
  gravado (o dicionário tem uma coluna de assinatura e uma de data de envio por membro); limitação
  aceita e anotada. Edge Cases.
- Q (D15): De onde o Histórico da defesa tira a nota final e o parecer do evento de liberação
  (RBN-DEF-01.6)? → A: da própria sessão (`def_nota_final` e `def_parecer`), exibidos no evento
  "Liberação do Resultado". FR-037.
- Q (D16): Quem só troca de papel na alteração da banca perde o rascunho? → A: **não**; descarta
  só quem saiu da banca (RBN-DEF-02.4). Aprovado depois de conferir que a mudança em
  `alterar_banca` é pequena (uma condição e o teste). FR-034. **Complemento** (revisão do
  `arquiteto-django`, I-06; Célio Benjamim, 2026-11-03; Q-135): a troca que mantém o rascunho é
  só **entre titulares** (1º ↔ 2º Avaliador); quem passa de titular a **Suplente** tem as
  avaliações descartadas e, se acionado depois, começa "Não avaliou".
- Q: Os PDFs (Ata Final, Folha de Aprovação e declarações) são gravados num armazenamento
  externo privado, como previa o PGCS 1.2? → A (Célio Benjamim, 2026-11-03, no `/speckit-plan`):
  **não; são gerados sempre sob demanda**, a cada download, a partir dos dados congelados na
  liberação, e nunca gravados. As imagens de assinatura continuam como hoje (disco do serviço,
  apagadas a cada deploy no Render gratuito); sem a imagem, o PDF sai sem ela (assinatura
  eletrônica fora do escopo). Na Ata, vale o Coordenador de Curso atual no momento do download
  (não há histórico de coordenadores; risco aceito). Textos da matriz, das US-27/US-28, do
  dicionário e do PGCS que pressupõem PDFs gravados: Q-132 a Q-134. Ideias futuras: S-04 a
  S-06. FR-028.
- Também aprovados: Minhas bancas abre a janela Sessão de defesa, onde ficam Reabrir minha
  avaliação e Liberar Resultado (US-27 passo 1; US-25 C.a), cenário 2.8 e FR-004; cenário da
  US-26 C9 (abrir o formulário com a sessão Agendada), cenário 3.18; rótulos do estado da
  avaliação pela matriz (RBN-DEF-06.8).

### Session 2026-11-04

- Q (emenda pedida pela spec 009, P1): a liberação aplica a E2 da US-28 (Coordenador de Curso sem
  assinatura no perfil)? → A (Célio Benjamim, 2026-11-04): **sim**. Depois do commit da
  liberação, `views_avaliacoes.liberar_resultado` chama a verificação da spec 009: com a E2, o
  Orientador vê na tela "Não foi possível gerar a Ata Final: o Coordenador de Curso não possui
  assinatura cadastrada no perfil" e o Coordenador (ou, sem Coordenador, a Secretaria do curso) é
  notificado. A liberação, o status, o parecer e os avisos desta spec **não mudam**. Contrato §2
  atualizado. Índice Q-144.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar os critérios oficiais de avaliação (Priority: P1)

Como Avaliador (Docente ou Membro Externo da banca), consulto, numa janela somente leitura, os 9
critérios oficiais da EST/UEA, com componente, nome, peso e a descrição de cada conceito, para
avaliar o trabalho com as regras vigentes.

**Why this priority**: os critérios fixos são a base do formulário de avaliação (User Story 3) e
do cálculo das notas (User Story 4); sem eles não há avaliação.

**Independent Test**: abrir a janela Critérios de avaliação a partir de Minhas bancas e conferir
os 9 critérios, os pesos e as somas, sem lançar nenhuma nota.

**Acceptance Scenarios**:

1. **Given** o Avaliador está em Minhas bancas, **When** aciona Critérios de avaliação, **Then**
   o sistema exibe os 6 critérios da Parte Escrita (Relevância do Tema 0,5; Metodologia 2,0;
   Revisão da Literatura 1,0; Resultados e Discussões 2,0; Conclusões 0,5; Redação 1,0; total
   7,0), os 3 da Parte Oral (Organização 1,0; Domínio do Assunto 1,5; Postura perante a Banca
   0,5; total 3,0), a soma 10,0 e as descrições dos conceitos Exemplar (8,0 a 10,0), Competente
   (6,0 a 7,9) e Necessita de Trabalho (0,0 a 5,9) de cada critério (US-25 cenário 4).
2. **Given** qualquer perfil, inclusive o Coordenador de Curso, **When** procura criar, editar
   ou remover um critério, **Then** não existe tela nem ação para isso, e a janela de consulta é
   somente leitura (RBN-DEF-04.1).

---

### User Story 2 - Ver as minhas bancas (Priority: P1)

Como Docente ou Membro Externo, abro o item Minhas bancas e vejo as sessões de defesa de que
participo, com o meu papel, a data, o horário e o status, as avaliações pendentes em destaque e
os atalhos para o documento, os critérios e o formulário de avaliação.

**Why this priority**: é o ponto de entrada da avaliação (US-25, passos 1 a 3) e o único acesso
do Membro Externo ao sistema (US-25, fluxo E).

**Independent Test**: com sessões em vários status, entrar como membro da banca (Docente e
Membro Externo) e conferir a lista, os destaques e os botões, sem lançar notas.

**Acceptance Scenarios**:

1. **Given** o Docente integra bancas de sessões Agendada, Em Andamento, Realizada e Cancelada,
   **When** abre Minhas bancas, **Then** vê as três primeiras, com papel na banca, data, horário
   e status, e não vê a Cancelada.
2. **Given** o usuário é membro efetivo e a sua avaliação numa sessão Agendada, Reagendada ou Em
   Andamento está "Não avaliou" ou "Rascunho salvo", **When** abre Minhas bancas, **Then** a linha aparece em
   destaque como pendente, com os atalhos Documento, Critérios de avaliação e Avaliar.
3. **Given** um Membro Externo foi designado para uma banca, **When** faz login, **Then** acessa
   Minhas bancas e vê só as defesas para as quais foi designado (US-25 cenário 8).
4. **Given** o Orientador acionou o suplente durante a sessão, **When** o suplente abre Minhas
   bancas, **Then** vê o botão Avaliar habilitado, com a Parte Escrita e a Parte Oral liberadas
   (US-25 cenário 7).
5. **Given** o usuário é Suplente ainda não acionado, **When** abre Minhas bancas, **Then** vê a
   sessão com o papel Suplente, sem o botão Avaliar.
6. **Given** a sessão está Realizada e a feat-09 informa que a declaração de participação do
   usuário existe, **When** o usuário abre Minhas bancas, **Then** vê o botão Declaração na linha
   (US-25, fluxo F; o download e o código de validação são da feat-09).
7. **Given** o Avaliador não está autenticado, **When** tenta abrir Minhas bancas, **Then** o
   sistema exibe a tela de login e, após a autenticação, a tela Minhas bancas (US-25 cenário 10).
8. **Given** o usuário está em Minhas bancas, **When** clica numa sessão, **Then** o sistema abre
   a janela Sessão de defesa, com o status de envio e, conforme o perfil, Reabrir minha avaliação
   e Liberar Resultado (US-27 passo 1; US-25 C.a).

---

### User Story 3 - Lançar, assinar e enviar a avaliação (Priority: P1)

Como Avaliador da banca (Orientador, 1º Avaliador, 2º Avaliador ou Suplente acionado), lanço
conceito, nota e observações nos 9 critérios (a Parte Escrita já antes da sessão, como rascunho),
vinculo a minha assinatura (anexada ou a do perfil) e envio a avaliação assinada; até a liberação
do resultado, posso reabrir e reenviar.

**Why this priority**: sem os 3 envios assinados não há nota final nem liberação (User Story 4).

**Independent Test**: com uma sessão Em Andamento, abrir o formulário como membro efetivo,
lançar os 9 critérios com assinatura e conferir o envio, a nota individual e o estado "Enviada",
sem liberar o resultado.

**Acceptance Scenarios**:

1. **Given** a sessão está Em Andamento e o Avaliador abriu o formulário Avaliação, **When**
   preenche Conceito e Nota dos 9 critérios, anexa a assinatura e aciona Enviar avaliação
   assinada, **Then** o sistema calcula a nota individual, grava o envio com data e hora e muda o
   status da avaliação para enviada (US-25 cenário 1); com um PNG de 500 KB anexado, a prévia
   aparece no formulário antes do envio, e a assinatura fica associada à avaliação com data e hora
   (US-26 cenário 1).
2. **Given** o Avaliador escolheu o conceito Competente, **When** informa a nota 7,5, **Then** o
   sistema aceita a nota, pois está na faixa de 6,0 a 7,9 (US-25 cenário 2).
3. **Given** o Avaliador não preencheu Observações, **When** envia a avaliação, **Then** o
   sistema aceita o envio (US-25 cenário 3).
4. **Given** a sessão está Agendada (ou Reagendada), **When** o Avaliador preenche a Parte
   Escrita e aciona Salvar, **Then** o sistema grava o rascunho, mantém a Parte Oral, o bloco de
   assinatura e o envio bloqueados, e o status mostra rascunho salvo (US-25 cenário 5; US-26
   cenário 9).
5. **Given** a sessão está Em Andamento e o Orientador ainda não acionou Liberar Resultado,
   **When** o Avaliador aciona Reabrir minha avaliação, ajusta uma nota e reenvia com a
   assinatura, **Then** o sistema recalcula a nota individual e atualiza os totais (US-25
   cenário 6); entre a reabertura e o reenvio, a avaliação fica "Rascunho salvo", sem assinatura.
6. **Given** o Avaliador tem assinatura salva no perfil, **When** opta por usá-la e aciona
   Enviar avaliação assinada, **Then** o sistema usa a imagem do perfil sem novo envio de
   arquivo (US-26 cenário 2).
7. **Given** o Avaliador anexou uma nova imagem, **When** marca Salvar esta imagem no meu perfil
   e envia a avaliação, **Then** o sistema grava a imagem na avaliação e atualiza a assinatura do
   perfil (US-26 cenário 3).
8. **Given** o Avaliador já carregou uma imagem, **When** aciona Atualizar imagem e seleciona
   outro arquivo PNG, **Then** o sistema troca a prévia no formulário (US-26 cenário 4).
9. **Given** o Avaliador escolheu o conceito Competente, **When** informa a nota 8,5, **Then** o
   sistema não salva, destaca o campo Nota e exibe "A nota deve situar-se entre o valor mínimo e
   o máximo para o conceito selecionado (ex.: de 6,0 a 7,9 para Competente)" (US-25 cenário 11).
10. **Given** um dos 9 critérios está sem conceito ou sem nota, **When** o Avaliador aciona
    Enviar avaliação assinada, **Then** o sistema bloqueia, destaca as pendências e exibe "Todos
    os 9 critérios devem conter conceito e nota" (US-25 cenário 12).
11. **Given** o Avaliador preencheu os 9 critérios e não anexou nem selecionou assinatura,
    **When** aciona Enviar avaliação assinada, **Then** o sistema destaca o bloco de assinatura e
    exibe "A assinatura do membro da banca é obrigatória para finalizar a avaliação" (US-25
    cenário 13; US-26 cenário 8).
12. **Given** o Avaliador selecionou um arquivo de 3 MB, **When** o sistema valida o arquivo,
    **Then** exibe "O arquivo de assinatura deve ter tamanho máximo de 2 MB" e não grava (US-26
    cenário 6).
13. **Given** o Avaliador selecionou um arquivo .pdf, **When** o sistema valida o arquivo,
    **Then** exibe "Formato não suportado. Envie a assinatura em PNG ou JPG" e não atualiza a
    prévia (US-26 cenário 7).
14. **Given** um docente (ou qualquer usuário) não integra a banca da defesa, ou é Suplente
    ainda não acionado, **When** tenta abrir a avaliação por link direto, **Then** o sistema
    exibe "Acesso restrito aos membros avaliadores da banca" (US-25 cenário 14; US-26 cenário
    10).
15. **Given** a defesa está Realizada, **When** o Avaliador abre o formulário, **Then** o
    formulário aparece só para leitura, sem os botões de edição e de envio (US-25 cenário 15).
16. **Given** o Avaliador digitou 501 caracteres em Observações, **When** aciona Salvar ou
    Enviar avaliação assinada, **Then** o sistema destaca o campo Observações e informa o limite
    de 500 caracteres (US-25 cenário 16).
17. **Given** o Avaliador não está autenticado, **When** tenta abrir o formulário de avaliação,
    **Then** o sistema exibe a tela de login e, após a autenticação, o formulário (US-26 cenário
    5).
18. **Given** a sessão está Agendada, **When** o Avaliador abre o formulário, **Then** o bloco de
    assinatura e o botão de envio ficam bloqueados e só o rascunho da Parte Escrita é permitido
    (US-26 cenário 9; mesmo caso do cenário 3.4 visto pela US-26, mantido para a rastreabilidade
    das duas US).
19. **Given** a sessão foi Cancelada, **When** um ex-membro da banca abre o formulário pelo
    endereço direto, **Then** o sistema exibe "Acesso restrito aos membros avaliadores da banca"
    (D12).

---

### User Story 4 - Apurar e liberar o resultado (Priority: P1)

Como Orientador (Presidente da banca), acompanho o status de envio dos 3 membros, vejo a nota
final apurada depois dos 3 envios, registro o parecer quando a regra exige e libero o resultado,
o que congela as notas, muda a sessão para Realizada, atualiza o Status do TCC e dispara os
documentos.

**Why this priority**: é o fechamento oficial da defesa e a origem dos documentos da feat-09 e do
fluxo da Versão Final (spec 005).

**Independent Test**: com uma sessão Em Andamento e os 3 envios feitos (ou não), abrir a janela
Sessão de defesa como Orientador e conferir o cálculo, o parecer automático ou escolhido, o
bloqueio de pendências e a liberação.

**Acceptance Scenarios**:

1. **Given** a sessão de TCC 2 está Em Andamento e os 3 membros enviaram as avaliações, **When**
   o Orientador registra o parecer Aprovado com Correções e aciona Liberar Resultado, **Then** o
   sistema bloqueia as notas, muda a sessão para Realizada e o Status do TCC para Aprovado com
   Correções, e o aluno passa a ver a nota final, o parecer e a Data Limite da Versão Final
   (US-27 cenário 1).
2. **Given** os 3 membros enviaram as avaliações, **When** o sistema calcula, **Then** cada nota
   individual vem da soma de nota vezes peso dividida por 10, e a nota final é a média das 3
   notas individuais, com uma casa decimal (US-27 cenário 2).
3. **Given** a sessão é de TCC 1 e a nota final é 7,2, **When** o Orientador aciona Liberar
   Resultado, **Then** o sistema fixa o parecer Aprovado para TCC 2 e muda o Status do TCC para
   Aprovado para TCC 2 (US-27 cenário 4).
4. **Given** a nota final em TCC 2 é 8,5, **When** o Orientador seleciona Aprovado e aciona
   Liberar Resultado, **Then** o Status do TCC passa a Aprovado e a Folha de Aprovação fica
   disponível ao aluno (US-27 cenário 5; o PDF é gerado sob demanda pela feat-09, que também
   testa o download).
5. **Given** a nota final é 5,4 e não há artigo Qualis A ou B homologado, **When** o Orientador
   aciona Liberar Resultado, **Then** o sistema fixa o parecer Reprovado, o Status do TCC passa a
   Reprovado, a Folha de Aprovação não é pedida e o aluno fica em modo somente consulta (US-27
   cenário 6).
6. **Given** a média é 5,4 e o trabalho tem artigo Qualis A homologado, **When** o sistema
   confere o artigo, **Then** a nota final passa a 6,0 (US-27 cenário 7).
7. **Given** a sessão está Em Andamento e o resultado não foi liberado, **When** um avaliador
   aciona Reabrir minha avaliação, corrige uma nota e reenvia, **Then** o sistema recalcula a
   nota individual, a média final e o parecer preliminar (US-27 cenário 8).
8. **Given** o suplente substituiu o 2º Avaliador, **When** o sistema calcula a média, **Then**
   usa a avaliação do suplente e descarta os registros do ausente (US-27 cenário 9).
9. **Given** o Orientador não está autenticado, **When** tenta abrir a sessão de defesa,
   **Then** o sistema exibe a tela de login e, após a autenticação, a sessão (US-27 cenário 10).
10. **Given** um membro ainda não enviou a avaliação, **When** o Orientador abre a sessão,
    **Then** o botão Liberar Resultado fica desabilitado e o sistema destaca o avaliador pendente
    (US-27 cenário 11).
11. **Given** a nota final em TCC 2 é 7,0 e o parecer não foi escolhido, **When** o Orientador
    tenta confirmar o Registrar parecer, **Then** o sistema exibe "Selecione o parecer da banca
    para continuar" (US-27 cenário 12), e o botão Liberar Resultado continua desabilitado
    enquanto não houver parecer (RBN-DEF-06.4; D1).
12. **Given** um avaliador titular abriu a sessão, **When** tenta liberar o resultado, **Then** o
    botão não aparece e a requisição é bloqueada com "Apenas o Orientador (Presidente da banca)
    pode liberar o resultado da defesa" (US-27 cenário 13).
13. **Given** o Orientador liberou o resultado, **When** um avaliador tenta reabrir a avaliação,
    **Then** o sistema bloqueia e os registros permanecem imutáveis (US-27 cenário 14).
14. **Given** a confirmação mostrou nota final 5,4 e parecer Reprovado, e um artigo Qualis A foi
    homologado antes da gravação, **When** o Orientador confirma a liberação, **Then** o sistema
    não grava e reabre a confirmação com a nova nota final e o novo parecer (D10).
15. **Given** a sessão Em Andamento tinha avaliações enviadas, **When** é reagendada (spec 007),
    **Then** as notas são mantidas, as avaliações voltam a "Rascunho salvo" sem assinatura, e
    cada membro precisa reenviar assinando quando a nova sessão estiver Em Andamento (D2).

---

### User Story 5 - Sigilo das notas e resultado para o aluno (Priority: P1)

Como membro da banca, vejo só a minha avaliação e o status de envio dos colegas até a liberação;
como Orientador, vejo também a nota final e o parecer depois dos 3 envios; como Aluno, só vejo a
nota final e o parecer depois da liberação, numa tela somente leitura.

**Why this priority**: o sigilo é regra de segurança da matriz (RAN-DEF-05, confidencialidade;
RBN-DEF-06.8) e precisa valer em todas as telas desde o primeiro rascunho.

**Independent Test**: com avaliações em rascunho e enviadas, abrir a sessão como cada perfil
antes e depois da liberação e conferir o que cada um vê.

**Acceptance Scenarios**:

1. **Given** a sessão está Em Andamento e o Orientador ainda não liberou o resultado, **When** um
   avaliador abre a sessão, **Then** vê só a própria avaliação e o status dos colegas (não
   avaliou, rascunho salvo ou enviada), e o aluno não vê nenhuma nota (US-27 cenário 3).
2. **Given** só 2 dos 3 membros enviaram, **When** o Orientador abre a sessão, **Then** não vê a
   nota final, só o status de cada membro e os pendentes em destaque (RBN-DEF-06.6, RBN-DEF-06.8).
3. **Given** os 3 membros enviaram e o resultado não foi liberado, **When** o Professor da
   Disciplina, a Secretaria do curso ou o Aluno abre a sessão, **Then** não vê nada do bloco de
   avaliação: nem nota, nem nota final, nem parecer, nem o status de envio dos membros (D7).
4. **Given** o resultado foi liberado, **When** qualquer pessoa que pode abrir a sessão (banca,
   Professor da Disciplina, Secretaria do curso ou Aluno) a abre, **Then** vê as notas por
   critério e por avaliador, a nota final e o parecer, somente leitura (RBN-DEF-06.8).
5. **Given** o resultado de TCC 2 foi liberado com parecer de aprovação, **When** o Aluno abre a
   aba Meu TCC, **Then** vê, somente leitura, a nota final, o parecer e a Data Limite da entrega
   do tipo Versão Final (RBN-DEF-06.5; Clarifications 2026-11-03: vale para Aprovado e para
   Aprovado com Correções).
6. **Given** o resultado foi liberado com o parecer Reprovado ou Aprovado para TCC 2, **When** o
   Aluno abre a aba Meu TCC, **Then** vê a nota final e o parecer, sem a Data Limite da Versão
   Final.
7. **Given** um avaliador escreveu Observações e o resultado foi liberado, **When** outro membro,
   o Professor da Disciplina, a Secretaria ou o Aluno abre a sessão, **Then** vê as notas, mas não
   as Observações desse avaliador (D7).
8. **Given** o resultado foi liberado, **When** quem pode abrir a sessão abre o Histórico da
   defesa, **Then** o evento "Liberação do Resultado" mostra a nota final e o parecer
   (RBN-DEF-01.6; D15).

---

### Edge Cases

- **Reagendamento de uma sessão Em Andamento** (spec 007, FR-019; D2): a banca e as notas salvas
  são mantidas, mas as avaliações enviadas voltam a "Rascunho salvo", sem data de envio e sem
  assinatura (FR-035). Enquanto a sessão estiver "Reagendada", a Parte Oral, a assinatura e o
  envio ficam bloqueados (RBN-DEF-05.1); as notas orais já lançadas continuam no rascunho e podem
  ser revistas quando a sessão voltar a "Em Andamento".
- **Reabrir minha avaliação** (D6) devolve o membro a "Rascunho salvo" (a data de envio e a
  assinatura são limpas e as notas continuam gravadas), e o botão Liberar Resultado volta a ficar
  desabilitado até o novo envio assinado (US-27, fluxo E; RBN-DEF-06.6).
- **Rascunho parcial** (D4): ao acionar Salvar, cada critério precisa estar vazio ou com conceito
  e nota; um critério com só um dos dois, ou com Observações sem conceito e nota, impede o
  salvamento com a MA-01 (as colunas `ava_nota` e `ava_conceito` são obrigatórias no dicionário).
- **Salvar com a sessão Em Andamento**: o botão Salvar continua disponível e grava os critérios
  preenchidos (das duas partes) como rascunho, sem assinatura e sem envio.
- **Parecer já registrado e reenvio que muda a nota**: o parecer escolhido em TCC 2 é preliminar
  (RBN-DEF-06.3: "só atualiza o Status do TCC na liberação"). Sempre que um reenvio mudar a
  nota final, o parecer escolhido é limpo (D3, revista): o parecer é limpo sempre que os 3
  envios deixam de estar completos (Reabrir, suplente, alteração da banca, reagendamento,
  cancelamento); no novo 3º envio, abaixo de 6,0 o sistema fixa Reprovado; com 6,0 ou mais, o
  Orientador escolhe de novo, e Liberar Resultado fica desabilitado até lá.
- **Homologação de artigo durante a deliberação**: a nota final exibida ao Orientador antes da
  liberação já considera o artigo homologado naquele momento, mas a gravada é a calculada na
  liberação, com o TCC travado (RBN-DEF-06.2; contrato §4 da spec 006). Se ela for diferente da
  mostrada na confirmação, a liberação não é gravada e a confirmação reabre (D10). Depois da
  liberação, uma mudança no artigo não altera a nota (US-20 E3).
- **Duas liberações ao mesmo tempo** (duas abas do Orientador): a segunda encontra a sessão já
  "Realizada" depois da trava e não grava nada; `transicionar_status` recusa "Realizada" →
  "Realizada".
- **Envio e liberação concorrentes**: o envio, a reabertura e a liberação travam a mesma sessão
  antes de conferir o status e o quórum, para que uma reabertura não passe depois da liberação.
- **Cancelamento, alteração da banca ou acionamento do suplente** (spec 007): as notas do membro
  que sai da banca são descartadas pela função real desta spec, dentro da mesma transação; o
  membro que entra começa "Não avaliou". Quem só troca de papel entre titulares na alteração
  da banca mantém o rascunho; quem passa a Suplente perde (D16; Q-135).
- **Turma arquivada com sessão Em Andamento** (pré-condição da US-27): não acontece, porque o
  arquivamento da turma é recusado enquanto houver sessão ativa (spec 004; D13).
- **Registro de cada envio** (RAN-DEF-05, Não Repúdio; D14): só o último envio de cada membro fica
  gravado (assinatura e data e hora), porque o dicionário tem uma coluna de cada; os envios
  anteriores, desfeitos por Reabrir minha avaliação, não ficam registrados. Limitação aceita.
- **Membro Externo com conta "Aguardando Ativação"** só avalia depois de ativar a conta
  (pré-condição da US-25: conta Ativa).
- **Falha na geração dos documentos** (feat-09): como os PDFs são gerados a cada download, a
  falha acontece no download (US-28 E3) e nunca desfaz a liberação; o envio das declarações é
  acionado depois de gravada a liberação.
- **Sessão Em Andamento sem liberação** depois de 1 hora: continua "Em Andamento" até a liberação
  ou o cancelamento (spec 007, Edge Cases); não há liberação automática.

## Requirements *(mandatory)*

### Functional Requirements — Critérios oficiais (US-25; RBN-DEF-04.1, RBN-DEF-04.2)

- **FR-001** [RBN-DEF-04.1]: O sistema MUST fornecer os 9 critérios oficiais da EST/UEA, fixos e
  iguais para os três cursos: Parte Escrita (Relevância do Tema 0,5; Metodologia 2,0; Revisão
  da Literatura 1,0; Resultados e Discussões 2,0; Conclusões 0,5; Redação 1,0) e Parte Oral
  (Organização 1,0; Domínio do Assunto 1,5; Postura perante a Banca 0,5), com soma exata 10,0, e
  MUST NOT oferecer a nenhum perfil, inclusive o Coordenador de Curso, forma de criar, editar ou
  remover critérios, pesos ou descrições.
- **FR-002** [RBN-DEF-04.2]: O sistema MUST exibir aos avaliadores a janela Critérios de
  avaliação, somente leitura, com componente, nome, peso e as descrições dos conceitos Exemplar,
  Competente e Necessita de Trabalho de cada critério, as somas 7,0 e 3,0 e o total 10,0,
  acessível a partir de Minhas bancas e do formulário Avaliação.

### Functional Requirements — Minhas bancas (US-25; RBN-DEF-05.4)

- **FR-003** [RBN-DEF-05.4]: O sistema MUST oferecer ao Docente e ao Membro Externo o item de
  menu Minhas bancas, com a lista das sessões de que o usuário é membro em `BancaDefesa`
  (inclusive como Suplente), exceto as Canceladas, com papel na banca, data, horário, aluno,
  título e status da sessão, em ordem cronológica.
- **FR-004** [RBN-DEF-05.4]: Nas sessões Agendada, Reagendada ou Em Andamento em que a avaliação
  do usuário está "Não avaliou" ou "Rascunho salvo", o sistema MUST destacar a linha como
  pendente, só para os membros efetivos (D11); cada linha MUST trazer os atalhos Documento (link
  mais recente do Documento para Defesa, quando houver), Critérios de avaliação e, para os
  membros efetivos, Avaliar. Clicar na sessão MUST abrir a janela Sessão de defesa (US-27 passo
  1), onde ficam Reabrir minha avaliação e Liberar Resultado.
- **FR-005** [RBN-DEF-05.4][RBN-DEF-08.3]: Nas sessões Realizadas, o sistema MUST exibir o botão
  Declaração quando a feat-09 informar que a declaração de participação do usuário existe.
- **FR-006** [RBN-DEF-05.4]: O Membro Externo MUST ver só as sessões para as quais foi designado;
  Minhas bancas é o seu ponto de entrada (US-25, fluxo E).

### Functional Requirements — Formulário de avaliação (US-25; RBN-DEF-05.1 a RBN-DEF-05.3)

- **FR-007** [RBN-DEF-05.3]: O sistema MUST abrir o formulário Avaliação só para os membros
  efetivos da sessão (`membros_efetivos`: Orientador, 1º e 2º Avaliador, com o suplente acionado
  no lugar do ausente), e MUST bloquear qualquer outro usuário, inclusive o Suplente não acionado
  e quem tenta pelo endereço direto, com "Acesso restrito aos membros avaliadores da banca".
- **FR-008** [RBN-DEF-05.2]: O formulário MUST mostrar o título, o aluno e o orientador do
  trabalho, o link do Documento para Defesa, as descrições dos conceitos e, para cada um dos 9
  critérios com o seu peso, os campos Conceito (lista com Exemplar, Competente e Necessita de
  Trabalho), Nota (uma casa decimal, com vírgula) e Observações (opcional, até 500 caracteres).
- **FR-009** [RBN-DEF-05.2]: O sistema MUST aceitar a Nota só dentro da faixa do conceito
  escolhido (Exemplar 8,0 a 10,0; Competente 6,0 a 7,9; Necessita de Trabalho 0,0 a 5,9), com no
  máximo uma casa decimal; fora da faixa, MUST não salvar, destacar o campo Nota e exibir "A nota
  deve situar-se entre o valor mínimo e o máximo para o conceito selecionado (ex.: de 6,0 a 7,9
  para Competente)".
- **FR-010** [RBN-DEF-05.2]: Com Observações acima de 500 caracteres em algum critério, o sistema
  MUST não salvar o formulário, destacar o campo e indicar o limite de 500 caracteres (MA-02).
- **FR-011** [RBN-DEF-05.1]: Com a sessão Agendada ou Reagendada, o sistema MUST habilitar só a
  Parte Escrita e o botão Salvar, com a nota informativa de que só a Parte Escrita pode ser
  avaliada e salva (MA-03), e MUST manter desabilitados a Parte Oral, o bloco de assinatura e o
  botão Enviar avaliação assinada, inclusive contra requisição direta.
- **FR-012** [RBN-DEF-05.1]: Com a sessão Em Andamento, o sistema MUST habilitar as duas partes,
  o bloco de assinatura, Salvar e Enviar avaliação assinada; para o suplente acionado, as duas
  partes ficam liberadas juntas (US-25, fluxo D).
- **FR-013** [RBN-DEF-05.1]: O botão Salvar MUST gravar como rascunho (linhas em `Avaliacoes`,
  com data e hora, sem `ban_data_envio`) os critérios preenchidos com conceito e nota, sem
  finalizar a avaliação; um critério com só conceito, só nota ou só Observações MUST impedir o
  salvamento (MA-01; D4).
  Depois de salvar, os demais membros veem o status "Rascunho salvo".
- **FR-014** [RBN-DEF-05.2]: Com a sessão Realizada, o formulário MUST aparecer só para leitura,
  com as notas fixadas, sem os botões de edição, de envio e de reabertura.

### Functional Requirements — Assinatura (US-26; RBN-DEF-05.2, campo 4)

- **FR-015** [RBN-DEF-05.2]: O formulário MUST trazer a seção Assinatura do Membro da Banca, com
  o botão Anexar imagem (PNG ou JPG, até 2 MB), a opção Salvar esta imagem no meu perfil e, quando
  o usuário tem assinatura no perfil (Docente ou Membro Externo, US-38), a prévia dessa assinatura
  e a opção de usá-la sem novo envio de arquivo.
- **FR-016** [RBN-DEF-05.2]: O sistema MUST validar a imagem anexada pelo tamanho e pelo formato
  real do arquivo: acima de 2 MB, MUST rejeitar sem gravar e exibir "O arquivo de assinatura deve
  ter tamanho máximo de 2 MB"; sem extensão .png, .jpg ou .jpeg (ou com conteúdo que não seja PNG
  ou JPG), MUST rejeitar, não atualizar a prévia e exibir "Formato não suportado. Envie a
  assinatura em PNG ou JPG"; com mais de 2000 × 1000 pixels, MUST rejeitar com a MA-14, sem
  reduzir a imagem (Clarifications, `/speckit-analyze` A1).
- **FR-017** [RBN-DEF-05.2]: Depois de carregar uma imagem, o Avaliador MUST poder trocá-la pelo
  botão Atualizar imagem antes do envio, com a prévia substituída.
- **FR-018** [RBN-DEF-05.2]: No envio, o sistema MUST guardar uma cópia da imagem usada (anexada
  ou do perfil) vinculada à avaliação do membro (`ban_assinatura_path`), em armazenamento sem URL
  pública, com a data e a hora do envio (`ban_data_envio`), para a Ata Final e a Folha de
  Aprovação; com Salvar esta imagem no meu perfil marcada, MUST também atualizar a assinatura do
  perfil.

### Functional Requirements — Envio, reabertura e nota individual (US-25, US-26; RBN-DEF-06.1)

- **FR-019** [RBN-DEF-05.2][RBN-DEF-06.1]: Ao acionar Enviar avaliação assinada, o sistema MUST
  conferir que os 9 critérios têm conceito e nota (senão, bloquear, destacar as pendências e
  exibir "Todos os 9 critérios devem conter conceito e nota") e que há assinatura (senão,
  destacar o bloco e exibir "A assinatura do membro da banca é obrigatória para finalizar a
  avaliação"), e MUST gravar as notas, a assinatura e a data e hora do envio, mudando a avaliação
  do membro para "Enviada".
- **FR-020** [RBN-DEF-06.1]: A nota individual de cada membro MUST ser a soma, nos 9 critérios, de
  nota × peso ÷ 10, com uma casa decimal e arredondamento comercial (a partir de 0,05 arredonda
  para cima), calculada em aritmética decimal exata, nunca em ponto flutuante.
- **FR-021** [RBN-DEF-06.1]: Com a sessão Em Andamento e antes da liberação, o membro que já
  enviou MUST poder acionar Reabrir minha avaliação, o que devolve a avaliação a "Rascunho salvo"
  sem apagar as notas, limpa a data de envio e a assinatura (D6) e limpa o parecer escolhido
  (D3, revista; Q-135); ao reenviar com a assinatura, o sistema MUST recalcular a nota
  individual, a nota final e o parecer preliminar. Com a avaliação Enviada, Salvar e Enviar
  ficam bloqueados até Reabrir (MA-13).
- **FR-022** [RBN-DEF-06.4]: Depois da liberação, o sistema MUST bloquear a reabertura, o
  salvamento e o envio de qualquer membro, também contra requisição direta (MA-04), mantendo os
  registros imutáveis.

### Functional Requirements — Nota final, parecer e liberação (US-27; RBN-DEF-06.2 a RBN-DEF-06.7)

- **FR-023** [RBN-DEF-06.6][RBN-DEF-06.4]: Enquanto algum dos 3 membros efetivos não tiver a
  avaliação "Enviada", o sistema MUST não calcular nem exibir a nota final e MUST destacar ao
  Orientador os avaliadores pendentes. O botão Liberar Resultado MUST ficar desabilitado
  (inclusive contra requisição direta) enquanto faltar algum envio ou, em TCC 2 com nota final
  6,0 ou mais, enquanto o parecer não estiver registrado (D1).
- **FR-024** [RBN-DEF-06.2]: Com os 3 envios, a nota final MUST ser a média aritmética simples
  das 3 notas individuais já arredondadas, com uma casa decimal e arredondamento comercial; com
  artigo Qualis A ou B homologado para o TCC (`tem_artigo_homologado_qualis_ab`), em TCC 1 ou TCC
  2, a nota final MUST ser o maior valor entre 6,0 e a média.
- **FR-025** [RBN-DEF-06.3]: O parecer MUST seguir a nota final e a etapa: nota final menor que
  6,0 → Reprovado, fixado pelo sistema, sem opções de aprovação; 6,0 ou mais em TCC 1 → Aprovado
  para TCC 2, fixado pelo sistema, sem o botão Registrar parecer; 6,0 ou mais em TCC 2 → o
  Orientador aciona Registrar parecer e escolhe Aprovado ou Aprovado com Correções. Ao confirmar
  o Registrar parecer sem escolha, o sistema MUST destacar o campo Parecer e exibir "Selecione o
  parecer da banca para continuar" (US-27 E3, passo 7; D1).
- **FR-026** [RBN-DEF-06.4]: Só o Orientador (Presidente da banca) MUST ver e acionar Liberar
  Resultado; para qualquer outro (avaliador titular, suplente, aluno ou outro docente), o botão
  não aparece e a requisição MUST ser bloqueada com "Apenas o Orientador (Presidente da banca)
  pode liberar o resultado da defesa".
- **FR-027** [RBN-DEF-06.4]: Liberar Resultado MUST pedir confirmação mostrando a nota final e o
  parecer (MA-05); confirmada, numa única transação, com o TCC e a sessão travados, o sistema
  MUST: recalcular a nota final com a homologação vigente e, se a nota final ou o parecer
  diferirem dos confirmados, não gravar nada e reabrir a confirmação com os novos valores (D10);
  gravar `def_nota_final`,
  `def_parecer` e `def_data_liberacao_resultado`; mudar a sessão de "Em Andamento" para
  "Realizada" por `transicionar_status` (que grava o evento "Liberação do Resultado"); e mudar o
  Status do TCC para o parecer por `atualizar_status_tcc`, com o gatilho "Liberação do
  resultado".
- **FR-028** [RBN-DEF-06.4][RBN-DEF-08.3]: Depois de gravada a liberação, o sistema MUST
  acionar o ponto de chamada da feat-09 para o envio das declarações de participação; enquanto a
  feat-09 não existir, o stub só registra o pedido em log. A Ata Final e a Folha de Aprovação
  (só em TCC 2 com parecer Aprovado ou Aprovado com Correções) MUST ficar disponíveis a partir da
  liberação, geradas sob demanda pela feat-09 a partir dos dados gravados (Clarifications
  2026-11-03); nenhum PDF é gravado.
- **FR-029** [RBN-DEF-06.7]: Com o parecer Reprovado, o Status do TCC MUST passar a Reprovado,
  sem pedido de Folha de Aprovação, e o aluno MUST ficar com acesso só de consulta (regra já
  aplicada pelo Status do TCC, RBN-CAD-08.5).
- **FR-030** [RBN-DEF-06.4]: Depois da liberação, o sistema MUST notificar, pela central de
  notificações e por e-mail, o Aluno, os membros efetivos da banca e a Secretaria do curso de que
  o resultado foi liberado, sem a nota no texto do e-mail (MA-06 a MA-08). **Diverge da US-27**,
  que só cita a Secretaria (D8; ver "Divergências em relação às US" e Q-131).

### Functional Requirements — Sigilo e resultado para o aluno (US-27; RBN-DEF-06.5, RBN-DEF-06.8)

- **FR-031** [RBN-DEF-06.8]: Antes da liberação, em qualquer tela (janela Sessão de defesa,
  Minhas bancas, formulário Avaliação, Defesas, Meu TCC), o sistema MUST mostrar a cada membro só
  a própria avaliação e o status de envio dos colegas ("Não avaliou", "Rascunho salvo" ou
  "Enviada"); só o Orientador MUST ver também a nota final e o parecer preliminar, e só depois dos
  3 envios (US-27 passo 2). Aluno, Professor da Disciplina e Secretaria MUST NOT ver nada do
  bloco de avaliação antes da liberação: nem notas, nem nota final, nem parecer, nem o status de
  envio dos membros (D7).
- **FR-032** [RBN-DEF-06.8]: Depois da liberação, as notas por critério e por avaliador, a nota
  final e o parecer MUST aparecer, somente leitura, a todos os que podem abrir a janela Sessão de
  defesa (spec 007, FR-030). As Observações de cada avaliador MUST ficar visíveis só a ele (D7).
- **FR-033** [RBN-DEF-06.5]: Depois da liberação, o sistema MUST mostrar ao Aluno, na aba Meu TCC,
  somente leitura, a nota final, o parecer e, em TCC 2 com parecer Aprovado ou Aprovado com
  Correções, a Data Limite da entrega do tipo Versão Final da turma (Clarifications 2026-11-03;
  Q-127). Sem essa entrega cadastrada na turma, a Data Limite não aparece.

### Functional Requirements — Descarte de avaliações (contrato §6 da spec 007)

- **FR-034** [RBN-DEF-02.2][RBN-DEF-02.4][RBN-DEF-03.3]: O sistema MUST oferecer
  `descartar_avaliacoes(sessao, membro=None)` que apaga as avaliações do membro informado (ou de
  todos, sem membro) e limpa a assinatura e a data de envio do membro que continua na banca, na
  transação de quem chama; o stub da spec 007 MUST passar a usar essa função sem mudar a
  assinatura nem os pontos de chamada (cancelamento, alteração da banca e acionamento do
  suplente). Na alteração da banca, MUST descartar as avaliações de quem saiu da banca ou passou
  a Suplente; quem só troca de papel entre titulares mantém o rascunho (D16; Q-135). Todo
  descarte MUST limpar o parecer escolhido (D3, revista).
- **FR-035** [RBN-DEF-03.3][RBN-DEF-05.1][RBN-DEF-06.6]: No reagendamento de uma sessão "Em
  Andamento" (spec 007), o sistema MUST manter as notas salvas e devolver todas as avaliações
  enviadas a "Rascunho salvo", limpando a data de envio, a assinatura e o parecer escolhido, na
  mesma transação do reagendamento (D2; D3 revista).

### Functional Requirements — Sessão cancelada e histórico

- **FR-036** [RBN-DEF-05.3][RBN-DEF-05.4]: O formulário Avaliação de uma sessão Cancelada MUST
  ser recusado a qualquer usuário, inclusive ex-membros da banca, com "Acesso restrito aos membros
  avaliadores da banca" (D12).
- **FR-037** [RBN-DEF-01.6]: Na janela Histórico da defesa (spec 007, FR-029), o evento
  "Liberação do Resultado" MUST mostrar a nota final e o parecer gravados na sessão (D15).

### Key Entities *(reaproveitadas da spec 001; nenhuma nova)*

- **Criterios**: os 9 critérios fixos, com componente, nome, peso e as três descrições de
  conceito.
- **Avaliacoes**: conceito, nota, observações e data e hora de cada membro em cada critério da
  sessão; ligada ao membro da banca pela FK composta.
- **BancaDefesa**: o membro na sessão; esta spec grava a cópia da assinatura usada e a data e
  hora do envio, de onde se deriva o estado da avaliação.
- **Defesas**: a sessão; esta spec grava o parecer, a nota final e a data da liberação.
- **HistoricoDefesas** e **HistoricoStatusTCC**: gravados só pelos serviços únicos das specs 007
  e 005 na liberação.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um avaliador lança e envia a avaliação completa dos 9 critérios, com a assinatura do
  perfil, em menos de 10 minutos a partir de Minhas bancas.
- **SC-002**: Em 100% dos casos de teste do cálculo, a nota individual e a nota final coincidem
  com o cálculo manual com uma casa decimal e arredondamento comercial, inclusive nos casos de
  fronteira (ex.: soma 6,05 → 6,1; soma 6,04 → 6,0; média de 5,9, 6,0 e 6,0 → 6,0; média 5,4
  com artigo Qualis A homologado → 6,0).
- **SC-003**: Em 100% dos testes, nenhuma nota individual, nota final ou parecer aparece, antes da
  liberação, a quem a regra de sigilo não permite (aluno, colegas de banca, Professor da
  Disciplina, Secretaria), em nenhuma tela nem por endereço direto.
- **SC-004**: 100% das mudanças de status da sessão e do TCC feitas por esta feature passam pelos
  serviços únicos (`transicionar_status` e `atualizar_status_tcc`), sem gravação direta de
  `def_status`, `tcc_status`, `Historico_Defesas` ou `Historico_Status_TCC`.
- **SC-005**: Depois da liberação, 100% das tentativas de salvar, enviar ou reabrir avaliações da
  sessão são recusadas, e as notas gravadas não mudam.
- **SC-006**: Todos os cenários de aceite das US-25, US-26 e US-27 têm pelo menos um teste
  automatizado, exceto o download da Declaração (US-25 cenário 9) e a liberação da Folha de
  Aprovação ao aluno (parte do US-27 cenário 5), que são da feat-09; aqui só o botão, o ponto de
  chamada e o utilitário de PDF são testados.
- **SC-007**: 100% das mensagens exibidas ao usuário são idênticas, caractere por caractere, ao
  texto entre aspas das US-25, US-26 e US-27, ou estão na tabela "Mensagens a validar com a PO"
  e em `docs/questoes-a-rever.md`.

## Assumptions

- Os 9 critérios já estão carregados (spec 001). Os descritores dos conceitos continuam
  provisórios até os oficiais (índice Q-03 e Q-18); esta spec só os exibe.
- A liberação é feita pelo Orientador (Presidente da banca) nos três cursos, mesmo onde quem
  agenda é o Professor da Disciplina (US-27, ator principal; RBN-DEF-06.4).
- O "Orientador" que libera é o membro com o papel "Orientador (Presidente)" na banca da sessão.
- A tela somente leitura do resultado para o aluno (RBN-DEF-06.5) é uma seção da aba Meu TCC
  (spec 005), além da janela Sessão de defesa que o aluno já abre (spec 007, FR-030).
- O "parecer preliminar" do TCC 2 é gravado em `def_parecer` ao registrar o parecer, mas só muda
  o Status do TCC na liberação (RBN-DEF-06.3). `def_nota_final` só é gravada na liberação
  (dicionário 3.6.1).
- A geração dos PDFs (Ata Final, Folha de Aprovação e declarações) é da feat-09, sempre sob
  demanda e sem gravar arquivo; esta spec entrega o `xhtml2pdf` e o utilitário de PDF em memória
  e aciona o envio das declarações depois de gravada a liberação. Uma falha nos PDFs não desfaz
  a liberação.
- Esta spec toca código já mesclado de outras features: o corpo de
  `services_defesa.descartar_avaliacoes` (spec 007), o menu (item Minhas bancas), a aba Meu TCC
  (seção do resultado, spec 005) e o `popular_demo` (avaliações de exemplo). Essas integrações
  foram aprovadas (Q-128, Clarifications 2026-11-03), com a condição de relatar cada mudança no
  plano e no PR.
- O arredondamento usa `Decimal` com `ROUND_HALF_UP` e `quantize(Decimal("0.1"))`, conforme a
  descrição da feature.

## Divergências em relação às US

Decisões desta spec que diferem do texto das US, para revisar depois com a PO:

| ID | Ponto | US | Decisão desta spec | Índice |
|---|---|---|---|---|
| DV-01 | Notificações da liberação do resultado | US-27 (atores secundários) só cita a Secretaria do curso, "notificada do encerramento da defesa" | Notifica também o Aluno e os membros efetivos da banca (FR-030; MA-06 e MA-07), sem a nota no e-mail | Q-131 |

## Mensagens a validar com a PO

Textos exibidos ao usuário sem texto exato nas US. Todos foram **aprovados** como estão (índice
Q-129, 2026-11-03). Todos os textos entre aspas nos FR acima são cópia exata das US.

| ID | Uso | Texto aprovado | Origem | Situação |
|---|---|---|---|---|
| MA-01 | Critério com só conceito ou só nota ao Salvar | "Informe o conceito e a nota do critério, ou deixe os dois em branco" | Edge Cases; FR-013 | Aprovada |
| MA-02 | Observações acima de 500 caracteres | "As observações devem ter até 500 caracteres" | US-25 E7 ("indica o limite de 500 caracteres", sem texto exato); FR-010 | Aprovada |
| MA-03 | Nota no formulário com a sessão Agendada ou Reagendada | "A sessão ainda não começou: só a Parte Escrita pode ser avaliada e salva." | US-25 B.a (sem texto exato); FR-011 | Aprovada |
| MA-04 | Tentativa de salvar, enviar ou reabrir depois da liberação | "O resultado desta defesa já foi liberado e as avaliações não podem mais ser alteradas" | US-27 E5 (sem texto exato); FR-022 | Aprovada |
| MA-05 | Confirmação de Liberar Resultado | "Liberar o resultado com nota final {nota} e parecer {parecer}? Depois disso, as notas não podem mais ser alteradas." | US-27 passo 8 (sem texto exato); FR-027 | Aprovada |
| MA-06 | Aviso ao Aluno (notificação e e-mail, assunto "SIGTCC: resultado da defesa") | "O resultado da sua defesa foi liberado. Consulte a nota final e o parecer na aba Meu TCC." | US-27 passo 13 (sem texto exato); FR-030 | Aprovada |
| MA-07 | Aviso aos membros da banca | "O resultado da defesa de {aluno} foi liberado. TCC: {titulo}." | US-27 (sem texto exato); FR-030 | Aprovada |
| MA-08 | Aviso à Secretaria do curso | "Defesa de {aluno} encerrada com parecer {parecer}. TCC: {titulo}." | US-27, atores secundários (sem texto exato); FR-030 | Aprovada |
| MA-09 | Confirmação na tela depois de Salvar | "Rascunho salvo" | US-25 B.c (sem texto exato); FR-013 | Aprovada |
| MA-10 | Confirmação na tela depois do envio | "Avaliação enviada com sucesso" | US-25 passo 12 (sem texto exato); FR-019 | Aprovada |
| MA-11 | Confirmação na tela depois da liberação | "Resultado liberado com sucesso" | US-27 passo 10 (sem texto exato); FR-027 | Aprovada |
| MA-12 | Minhas bancas sem nenhuma sessão | "Você não participa de nenhuma banca no momento" | DEF-05.4 (sem texto exato); FR-003 | Aprovada |
| MA-13 | Salvar ou Enviar com a avaliação já enviada, antes da liberação | "Sua avaliação já foi enviada. Para alterá-la, use Reabrir minha avaliação" | US-25 C (sem texto exato); FR-021; `/speckit-analyze` I1 | Aprovada (2026-11-03) |
| MA-14 | Imagem de assinatura PNG ou JPG com mais de 2000 × 1000 pixels | "A imagem da assinatura deve ter no máximo 2000 × 1000 pixels" | US-26 (sem texto exato; limite técnico de memória, research A5); FR-016; `/speckit-analyze` A1 | Aprovada (2026-11-03) |
