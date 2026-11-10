# Feature Specification: Documentação e Encerramento do SIGTCC

**Feature Branch**: `feature/feat-09-documentos`

**Created**: 2026-11-04

**Status**: Approved (Célio Benjamim, 2026-11-05)

**Input**: User description: "Documentação e Encerramento do SIGTCC: US-28 (Ata Final e Folha de Aprovação) e US-30 (ouvintes, ocorrências, declaração de participação, listagem de ouvintes das defesas e agenda de defesas em PDF). Use as seções dessas US em docs/fonte/Historias_de_Usuario_v3_4.md, com regras (RBN), fluxos alternativos, exceções e cenários de aceite. Os PDFs são gerados uma sob demanda. Usar membros_efetivos (o suplente entra no lugar do substituído), o filtro de período e de Curso da spec 007, os blocos do template sessao.html e o ponto de chamada da liberação deixado pela spec 008 (confira o contrato dela em specs/008-*/contracts/). Sem a assinatura do Coordenador, aplicar a E2 da US-28. Falha na geração: registrar no log e não gravar arquivo corrompido."

**Responsável pelas US de origem**: Célio Benjamim (US-28 e US-30).

**Fontes**: Histórias de Usuário v3.4 (US-28 e US-30); Matriz de Requisitos de 17/10, aba
`Requisitos_Defesa` (RAN-DEF-07 e RAN-DEF-08: RBN-DEF-07.1 a 07.3 e 08.1 a 08.5; REQ-WNT-08 e
REQ-WNT-09); dicionário de dados de 18/10 (3.1.6 Ouvintes, 3.6.1 Defesas, 3.6.5 Presenca_Ouvintes
e a regra 4 da seção de mecanismos: "Código assinado gerado a partir da defesa e do membro,
verificável sem armazenamento"); diagramas `LiberarResultadoDefesa` (28) e
`RegistrarOuvintesAgenda` (PlantUML v2).

## Dependências e reaproveitamento

- **Modelo de dados**: já existe (spec 001). Esta spec **não cria tabelas nem colunas**. Usa:
  - `Ouvintes` (3.1.6): `ouv_matricula` CHAR(10), única no sistema (AK), e `ouv_nome`
    VARCHAR(150); um aluno ouvinte tem um registro só, reaproveitado em todas as sessões;
  - `Presenca_Ouvintes` (3.6.5): presença (sessão, ouvinte), PK composta, o que já impede a mesma
    matrícula duas vezes na mesma sessão;
  - `Defesas` (3.6.1): grava `def_ocorrencias` (VARCHAR(2000)). **Não grava**
    `def_ata_final_path` nem `def_folha_aprovacao_path`: os PDFs são gerados sob demanda e nunca
    gravados (decisão de 2026-11-03, spec 008; índice Q-133);
  - lê `BancaDefesa`, `Avaliacoes`, `Criterios`, `Coordenadores`, `Docentes`, `MembrosExternos`,
    `TCCs`, `Turmas` e `Cursos`.
- **Contrato da spec 007** (`specs/007-agendamento-banca/contracts/servicos-defesa.md`):
  - `services_defesa.membros_efetivos(sessao)`: os 3 membros que constam nos documentos e que
    recebem a declaração; o suplente acionado entra na linha do titular substituído (US-28 D;
    RBN-DEF-02.2);
  - componente do filtro de período (`periodo_letivo_atual`, `filtro_de_periodo`,
    `FiltroPeriodoForm`) e o filtro de Curso (`services_contas.filtro_de_curso`, spec 002), para
    a agenda em PDF e a lista de ouvintes (RBN-DEF-01.5, RBN-CAD-14.1);
  - template `defesa/sessao.html`: esta spec preenche os blocos `{% block documentos %}` (Ata
    Final e Folha de Aprovação), `{% block ouvintes %}` e `{% block ocorrencias %}`;
  - permissões de abertura da janela Sessão de defesa (FR-030 da spec 007), sem alteração.
  - Esta spec **nunca** grava `def_status` nem `Historico_Defesas` e nunca cria sessão.
- **Contrato da spec 008** (`specs/008-avaliacao-resultados/contracts/servicos-avaliacoes.md`):
  - `services_avaliacoes.resultado_da_sessao(sessao)`: fonte única da Ata Final e da Folha de
    Aprovação (nota final, parecer, notas individuais e por critério dos 3 membros efetivos e se
    o artigo Qualis elevou a nota); a data impressa nos documentos é a data da defesa
    (`def_data`), não a `data_liberacao` que o serviço também devolve (P12);
  - as imagens de assinatura dos membros vêm da cópia gravada na avaliação enviada
    (`BancaDefesa.ban_assinatura_path`, spec 008), não do perfil;
  - `services_documentos.ao_liberar_resultado(sessao)`: ponto de chamada registrado depois do
    commit da liberação, com `robust=True`; esta spec troca o corpo do stub, sem mudar a
    assinatura, para enviar as declarações por e-mail numa thread, com a falha só no log;
  - **emenda à spec 008** (P1, 2026-11-04): `views_avaliacoes.liberar_resultado` passa a chamar,
    depois do commit, uma verificação síncrona desta spec que aplica a E2 da US-28 (alerta na tela
    ao Orientador e notificação). Registrada nas Clarifications e no contrato §2 da spec 008;
  - `services_documentos.declaracao_disponivel(sessao, usuario)`: esta spec troca o corpo do stub
    para decidir o botão Declaração de Minhas bancas;
  - `pdf.gerar_pdf` e `pdf.resposta_pdf`: geração em memória, sem acesso à rede, entrega só
    depois da permissão; falha vira `ErroAoGerarPdf`, com log;
  - templates de PDF não estendem `base.html` e usam as fontes locais (research A9 da spec 008).
- **Serviços de outras specs**: `services.notificar` e `services.enviar_email_apos_commit` (spec
  004, contrato §4); `services.caminho_da_assinatura` (spec 003) para a assinatura do
  Coordenador; `services_turmas.turma_arquivada` (spec 004) para a turma arquivada. "Orientador
  do trabalho" é o **Presidente da banca** (papel Orientador (Presidente) da sessão; Clarifications,
  B-03), não o orientador atual do TCC.
- **Telas de entrada**: Minhas bancas (spec 008), a aba Defesas da turma e a tela Defesas (spec
  007) levam à janela Sessão de defesa, onde ficam os botões dos documentos; a aba Meu TCC (spec
  005) tem os botões próprios do Aluno.

## Clarifications

### Session 2026-11-04

- Q: Os PDFs são gravados? → A (Célio Benjamim, na descrição desta feature, confirmando a decisão
  de 2026-11-03 da spec 008): **não; são gerados sob demanda**, a cada download, com os dados
  congelados na liberação (notas, parecer, membros efetivos e assinaturas da avaliação). O nome e
  a assinatura do Coordenador e as titulações dos membros são lidos no momento do download (não há
  histórico; risco aceito, S-05). Nenhum arquivo é gravado, inclusive em falha (US-28 E3).
- Q: Sem a assinatura do Coordenador de Curso, o que acontece? → A (Célio Benjamim, na descrição
  desta feature): **aplica-se a E2 da US-28**: a Ata Final não é gerada, o Orientador é alertado
  com "Não foi possível gerar a Ata Final: o Coordenador de Curso não possui assinatura cadastrada
  no perfil" e a Coordenação é notificada para regularizar o cadastro.
- Q: A E2 vale também quando o caminho da assinatura existe no perfil, mas o arquivo sumiu do
  disco do serviço (deploy no Render gratuito)? → A (Célio Benjamim, 2026-11-04): **não**. A E2
  vale só quando o Coordenador nunca cadastrou a assinatura (caminho vazio) ou quando o curso não
  tem Coordenador. Com o caminho gravado e o arquivo ausente, a Ata sai sem a imagem dele, como as
  dos membros, e a ausência vai para o log. Índice Q-140.

Conferência do analista-requisitos (2026-11-04): pontos P1 a P16, ajustes de cobertura (B) e de
texto (C.7), todos decididos por Célio Benjamim na mesma data conforme a recomendação:

- Q (P1): Quando a E2 é aplicada? → A: **na liberação e em todo download da Ata Final**. Na
  liberação, o Orientador vê o alerta da E2 na tela e o Coordenador recebe a notificação (MX-03),
  uma vez por liberação; a liberação não é desfeita nem bloqueada. No download, o Orientador vê a
  mensagem da E2 e os demais perfis veem a MX-08; o download não repete a notificação. O diagrama
  28 só põe a E2 no download; a US-28 (E2 e cenário 10) prevalece. Exige **emenda à spec 008**
  (Clarifications e contrato §2), relatada (Q-128; índice Q-144).
- Q (P2): Quem gera a agenda e o que entra nela? → A: o Orientador (Docente) e o Professor da
  Disciplina geram a agenda de **todas** as sessões Agendadas e Reagendadas do período, sem filtro
  de Curso; o Coordenador e a Secretaria, também com o filtro de Curso. A agenda é pública
  (RBN-DEF-08.1: "para divulgação") e não segue a visibilidade da lista Defesas. FR-022 e FR-024.
- Q (P3): Sessão Reagendada tem o botão Ouvintes? → A: **não** (a matriz só libera Em Andamento
  e Realizada); a mensagem é a da E7. As presenças já gravadas (sessão Em Andamento reagendada)
  continuam e aparecem só para leitura até a sessão voltar a Em Andamento.
- Q (P4): Matrícula já cadastrada com outro nome? → A: **mantém o nome gravado, sem aviso**, como
  no diagrama 05. A MX-02 sai.
- Q (P5): O Suplente não acionado baixa os documentos? → A: **não**; só os membros efetivos da
  banca (a Ata é deles), além do Professor da Disciplina e da Secretaria; o Aluno baixa só a Folha
  de Aprovação (decisão de 10/11/2026). FR-005.
- Q (P6): A Secretaria vê os ouvintes de uma sessão Em Andamento? → A: **sim, só leitura, na
  janela da sessão** (Em Andamento e Realizada; "durante e após", RBN-DEF-08.2). O menu "Ouvintes
  das defesas" mostra só as sessões Realizadas (RBN-DEF-08.4). FR-009.
- Q (P7): Como o Professor da Disciplina consulta os ouvintes da turma? → A: **pela janela de cada
  sessão**; o menu "Ouvintes das defesas" é só da Secretaria (P8).
- Q (P8): Quem usa "Ouvintes das defesas"? → A: **só a Secretaria**. O consolidado com exportação
  fica para o relatório do Épico 3 (RBN-REL-03.4).
- Q (P9): O Professor da Disciplina registra ocorrências? → A: **não; só o Orientador**
  (RBN-DEF-08.5, a matriz prevalece). A US-30 E9 e o cenário 19 citam ouvintes **ou ocorrências**
  para os dois perfis: nesta spec, o cenário 19 vale para ouvintes com os dois perfis e, para
  ocorrências, só com o Orientador. A nota do diagrama 05 foi corrigida; a US-30 fica para o dono
  do documento de US (índice Q-143).
- Q (P10): Quem vê as ocorrências? → A: o Orientador, a Secretaria do curso e o Professor da
  Disciplina da turma. Avaliadores, Suplente e Aluno **não** veem. FR-014.
- Q (P11): Há tela de verificação do código da declaração? → A: **não** nesta feature; ideia
  futura S-07.
- Q (P12): Qual data sai nos documentos? → A: **a data da defesa** (`def_data`), não a da
  liberação. FR-008.
- Q (P13): Que mensagem tem a recusa antes da liberação e a da declaração? → A: **o texto da
  US-28 E6** ("Você não tem permissão para acessar os documentos desta defesa") nos dois casos,
  sem mensagem nova. FR-005 e FR-021.
- Q (P14): Com mais de uma sessão Realizada do mesmo TCC, o que o Meu TCC mostra? → A: **os
  documentos de todas as sessões Realizadas do TCC**, cada um com a data da defesa. Minhas
  bancas, a aba Defesas da turma e a tela Defesas levam à janela da sessão. FR-003.
- Q (P15): E o curso sem Coordenador cadastrado? → A: **aplica-se a E2** e a notificação vai à
  Secretaria do curso (MX-09).
- Q (P16): Qual o texto da declaração? → A: a MX-05 continua provisória e o modelo institucional
  é pedido à PO (índice Q-142).
- Ajustes de cobertura (B): a MX-06 tem texto exato no diagrama 05 e deixa de ser provisória; o
  FR-013 destaca a caixa de texto (E5); entram cenários de login para as ocorrências, a lista de
  ouvintes e a agenda; o FR-017 cita a origem do filtro de Curso (spec 002); o FR-001 e o FR-002
  dizem que as assinaturas dos membros vêm da cópia da avaliação; a SC-005 (agenda em 5 segundos)
  sai, porque não tem base na matriz.
- Q: Depois que a turma é arquivada, o Orientador e o Professor da Disciplina ainda podem
  adicionar ou remover ouvintes de uma sessão Realizada? → A (Célio Benjamim, 2026-11-04,
  `/speckit-clarify`): **não**. Com a turma arquivada, os ouvintes ficam só para leitura: o botão
  Ouvintes não aparece e o endereço direto é recusado com "Você não tem permissão para esta ação",
  como nas demais US com turma arquivada. FR-009 e FR-012.
- Q (revisão do `arquiteto-django` no plan, B-03): quem é o "Orientador do trabalho" que registra
  ouvintes e ocorrências e vê as ocorrências? → A (Célio Benjamim, 2026-11-05): **o Presidente da
  banca** (papel Orientador (Presidente) na sessão), o mesmo que libera o resultado e vê a mensagem
  da E2. O orientador atual do TCC não serve: a matrícula no TCC 2 encerra a orientação do TCC 1
  (o Presidente perderia as ocorrências que escreveu), e um orientador novo depois de uma troca
  ganharia um botão numa sessão que não consegue abrir. FR-009, FR-012 a FR-015 e cenário 3.8.
  Índice Q-145.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Baixar a Ata Final e a Folha de Aprovação (Priority: P1)

Como membro efetivo da banca, Professor da Disciplina ou Secretaria, baixo, depois da liberação do
resultado, a Ata Final e, em TCC 2 aprovado, a Folha de Aprovação; como Aluno, baixo só a Folha de
Aprovação. Os PDFs são não editáveis, no padrão institucional (modelos em `docs/`), gerados na
hora com os dados congelados da sessão, as assinaturas da banca e, na Ata, as do Coordenador de
Curso.

**Why this priority**: são os documentos formais da defesa e a Folha entra na Versão Final do
TCC 2 (US-29); sem eles o encerramento do trabalho fica incompleto.

**Independent Test**: com uma sessão Realizada (TCC 1, TCC 2 aprovado e Reprovado), baixar cada
documento como cada perfil e conferir o conteúdo, os botões e as recusas.

**Acceptance Scenarios**:

1. **Given** o Orientador liberou o resultado de um TCC 2 com parecer Aprovado, **When** o sistema
   gera os documentos, **Then** cria a Ata Final com as notas e as assinaturas dos 3 examinadores e
   do Coordenador, e a Folha de Aprovação sem notas, **And** exibe os botões de download para a
   banca, o Professor da Disciplina e a Secretaria, e o botão da Folha também ao aluno; o aluno
   não recebe a Ata (US-28 cenário 1; decisão de 10/11/2026).
2. **Given** a Folha de Aprovação foi gerada, **When** o Aluno aciona o botão na aba Meu TCC,
   **Then** o sistema baixa o PDF assinado (US-28 cenário 2).
3. **Given** a defesa é de uma turma de TCC 1, **When** o sistema gera os documentos, **Then** cria
   só a Ata Final de TCC I e exibe só o botão Ata Final (PDF) (US-28 cenário 3).
4. **Given** o parecer é Reprovado, **When** o sistema gera os documentos, **Then** cria só a Ata
   Final, com o registro da reprovação (US-28 cenário 4).
5. **Given** o parecer é Aprovado com Correções, **When** o resultado é liberado, **Then** o aluno
   já pode baixar a Folha de Aprovação, e a conferência das correções fica para a US-44 (US-28
   cenário 5).
6. **Given** o suplente substituiu o 1º Avaliador, **When** o sistema monta os documentos, **Then**
   coloca nome, titulação e assinatura do suplente na linha do titular substituído (US-28 cenário
   6).
7. **Given** a nota final foi fixada em 6,0 por artigo Qualis A homologado, **When** o sistema gera
   a Ata Final, **Then** insere a observação "Em caso de artigos, se Qualis A ou B, a nota final
   será o valor máximo entre 6,0 e a média dos avaliadores" (US-28 cenário 7).
8. **Given** a sessão está Realizada, **When** a Secretaria abre a sessão na lista Defesas, **Then**
   baixa a Ata Final e a Folha de Aprovação (US-28 cenário 8; geradas na hora, não arquivadas).
9. **Given** o usuário não está autenticado, **When** tenta abrir o endereço de download, **Then** o
   sistema exibe a tela de login e, após a autenticação, inicia o download (US-28 cenário 9).
10. **Given** o Coordenador de Curso não tem assinatura no perfil, **When** o Orientador libera o
    resultado, **Then** o sistema não gera a Ata Final, alerta o Orientador com "Não foi possível
    gerar a Ata Final: o Coordenador de Curso não possui assinatura cadastrada no perfil" e
    notifica a Coordenação (US-28 cenário 10); enquanto a assinatura não for cadastrada, o download
    da Ata Final mostra a mesma mensagem ao Orientador e a MX-08 aos demais perfis (P1).
11. **Given** o serviço de conversão está indisponível, **When** o sistema tenta gerar os
    documentos, **Then** não gera arquivo corrompido, registra a falha e exibe "Erro ao gerar os
    documentos da defesa. Tente realizar o download novamente em instantes" (US-28 cenário 11).
12. **Given** o trabalho é de TCC 1, **When** o usuário tenta baixar a Folha de Aprovação, **Then**
    o sistema exibe "A Folha de Aprovação não se aplica ao TCC 1" (US-28 cenário 12).
13. **Given** o parecer é Reprovado, **When** o usuário tenta baixar a Folha de Aprovação, **Then**
    o sistema exibe "Documento indisponível para trabalhos reprovados" (US-28 cenário 13).
14. **Given** um docente não integra a banca nem é o Professor da Disciplina da turma, **When**
    tenta baixar a Ata Final, **Then** o sistema exibe "Você não tem permissão para acessar os
    documentos desta defesa" (US-28 cenário 14).
15. **Given** o Suplente da banca não foi acionado, **When** tenta baixar a Ata Final, **Then** o
    sistema exibe "Você não tem permissão para acessar os documentos desta defesa" (P5).
16. **Given** o resultado da sessão ainda não foi liberado, **When** o Aluno ou um membro abre o
    endereço de download, **Then** o sistema exibe "Você não tem permissão para acessar os
    documentos desta defesa" (P13).
17. **Given** o curso do TCC não tem Coordenador cadastrado, **When** o Orientador libera o
    resultado, **Then** vale a E2 e a Secretaria do curso é notificada (MX-09; P15).
18. **Given** a assinatura do Coordenador está cadastrada, mas o arquivo sumiu do disco, **When**
    alguém baixa a Ata Final, **Then** o PDF sai sem a imagem do Coordenador e a ausência vai para o
    log (Q-140).
19. **Given** o TCC teve duas sessões Realizadas (Reprovado e, depois, Aprovado), **When** o Aluno
    abre a aba Meu TCC, **Then** vê os documentos de cada sessão, com a data da defesa (P14).

---

### User Story 2 - Registrar os ouvintes da sessão (Priority: P2)

Como Orientador do trabalho ou Professor da Disciplina da turma, registro, durante ou depois da
sessão, o Nome Completo e a Matrícula dos alunos que assistiram à defesa, e removo os registrados
por engano. A Secretaria do curso consulta a lista na janela da sessão, só para leitura.

**Why this priority**: a lista de ouvintes é a base das horas complementares (User Story 4); não
bloqueia o resultado da defesa (US-30 é Should Have).

**Independent Test**: com sessões Em Andamento, Realizada, Agendada e Cancelada, abrir a janela
Ouvintes como Orientador, Professor da Disciplina e outro docente, adicionar, remover e salvar.

**Acceptance Scenarios**:

1. **Given** a sessão está Em Andamento, **When** o Orientador adiciona dois alunos, com Nome
   Completo e Matrícula de 10 dígitos, e aciona Salvar, **Then** o sistema grava os ouvintes e
   exibe "Ouvintes salvos com sucesso" (US-30 cenário 1).
2. **Given** a sessão está Realizada, **When** o Professor da Disciplina registra um ouvinte e
   salva, **Then** o sistema grava o ouvinte (US-30 cenário 2).
3. **Given** um aluno foi registrado por engano, **When** o usuário aciona Remover na linha dele e
   salva, **Then** o sistema grava a lista sem esse aluno (US-30 cenário 3).
4. **Given** o usuário informou a matrícula 12345678 ou 12345abc90, **When** aciona Salvar,
   **Then** o sistema exibe "A matrícula deve conter exatamente 10 dígitos numéricos" (US-30
   cenário 12).
5. **Given** o aluno de matrícula 2022010001 já consta como ouvinte da sessão, **When** o usuário
   tenta adicioná-lo de novo, **Then** o sistema exibe "Este aluno já foi registrado como ouvinte
   nesta defesa" (US-30 cenário 13).
6. **Given** o usuário informou o nome "Ana 2" ou deixou o campo em branco, **When** aciona Salvar,
   **Then** o sistema exibe "O nome deve conter apenas letras, acentos e espaços e ter até 150
   caracteres" (US-30 cenário 14).
7. **Given** a sessão está Agendada, Reagendada ou Cancelada, **When** o usuário abre a sessão,
   **Then** o botão Ouvintes não aparece e o sistema informa "O registro de ouvintes fica
   disponível apenas durante ou após a sessão" (US-30 cenário 17; Reagendada, P3).
8. **Given** um docente não é o Orientador do trabalho nem o Professor da Disciplina da turma,
   **When** tenta registrar ouvintes, **Then** o sistema exibe "Você não tem permissão para esta
   ação" (US-30 cenário 19).
9. **Given** o usuário não está autenticado, **When** tenta abrir a sessão de defesa, **Then** o
   sistema exibe a tela de login e, após a autenticação, a tela pedida (US-30 cenário 11).
10. **Given** a sessão está Em Andamento com ouvintes, **When** a Secretaria do curso abre a
    sessão, **Then** vê a lista de ouvintes só para leitura, sem Adicionar, Remover e Salvar (P6).
11. **Given** o aluno de matrícula 2022010001 já está cadastrado como ouvinte com outro nome,
    **When** o usuário o registra em outra sessão com nome diferente e salva, **Then** o sistema
    grava a presença com o nome já cadastrado, sem aviso (P4).
12. **Given** a turma do TCC foi arquivada, **When** o Orientador abre a sessão Realizada, **Then**
    o botão Ouvintes não aparece, a lista fica só para leitura e o envio direto é recusado com
    "Você não tem permissão para esta ação" (Clarifications).

---

### User Story 3 - Relatar as ocorrências da sessão (Priority: P3)

Como Orientador, registro, até a liberação do resultado, os apontamentos ou incidentes da
arguição, que a Secretaria e o Professor da Disciplina consultam somente para leitura; os
Avaliadores, o Suplente e o Aluno não veem as ocorrências.

**Why this priority**: campo opcional (RBN-DEF-08.5, Could Have), complementar à Ata.

**Independent Test**: com uma sessão Em Andamento, salvar ocorrências como Orientador e conferir a
leitura pela Secretaria e pelo Professor da Disciplina; depois da liberação, conferir que só há
consulta.

**Acceptance Scenarios**:

1. **Given** a sessão está Em Andamento e o resultado não foi liberado, **When** o Orientador
   aciona Ocorrências, escreve os apontamentos e salva, **Then** o sistema grava o texto e o
   exibe, somente leitura, à Secretaria e ao Professor da Disciplina (US-30 cenário 4).
2. **Given** a sessão correu com normalidade, **When** o Orientador deixa o campo Ocorrências
   vazio, **Then** o sistema não exige o preenchimento (US-30 cenário 5).
3. **Given** o Orientador digitou 2.001 caracteres, **When** aciona Salvar, **Then** o sistema
   não salva, destaca a caixa de texto e avisa do limite de 2.000 caracteres (US-30 cenário 15 e
   E5; MX-01).
4. **Given** a sessão está Realizada, **When** o Orientador abre a sessão, **Then** as ocorrências
   aparecem só para consulta (US-30 cenário 16).
5. **Given** um docente não é o Orientador do trabalho, inclusive o Professor da Disciplina,
   **When** tenta registrar ocorrências, **Then** o sistema exibe "Você não tem permissão para esta
   ação" (US-30 cenário 19, lido conforme RBN-DEF-08.5; P9).
6. **Given** um Avaliador ou o Aluno abre a sessão com ocorrências gravadas, **When** a janela é
   exibida, **Then** as ocorrências não aparecem (P10).
7. **Given** o usuário não está autenticado, **When** tenta abrir o endereço de Ocorrências,
   **Then** o sistema exibe a tela de login e, após a autenticação, a tela pedida (US-30 cenário
   11).
8. **Given** o aluno aprovado no TCC 1 foi matriculado no TCC 2 (a orientação do TCC 1 foi
   encerrada), **When** o Presidente da banca do TCC 1 abre a sessão Realizada, **Then** ele ainda
   vê as ocorrências e a lista de ouvintes (B-03).

---

### User Story 4 - Consultar os ouvintes das defesas para as horas complementares (Priority: P2)

Como Secretaria, abro "Ouvintes das defesas", filtro por período e curso e vejo, das sessões
Realizadas, cada ouvinte com a indicação de 2 horas de atividades complementares, para lançar no
sistema acadêmico da instituição.

**Why this priority**: é o uso final da lista de ouvintes (RBN-DEF-08.4); sem ela a Secretaria não
tem de onde tirar as horas.

**Independent Test**: com ouvintes em sessões Realizadas de cursos e períodos diferentes, abrir a
tela como Secretaria e conferir colunas e filtros.

**Acceptance Scenarios**:

1. **Given** existem sessões Realizadas com ouvintes no período, **When** a Secretaria abre
   Ouvintes das defesas e filtra por período e curso, **Then** o sistema lista Nome Completo,
   Matrícula, título do trabalho, aluno, orientador, data da defesa e a indicação de 2 horas por
   ouvinte (US-30 cenário 6).
2. **Given** um ouvinte assistiu a duas defesas Realizadas, **When** a Secretaria consulta, **Then**
   ele aparece uma vez em cada sessão, com 2 horas em cada (RBN-DEF-08.4: "por sessão assistida").
3. **Given** uma sessão Em Andamento ou Cancelada tem ouvintes, **When** a Secretaria consulta,
   **Then** esses ouvintes não aparecem (só sessões Realizadas, RBN-DEF-08.4).
4. **Given** a Secretaria não tem acesso a outro curso, **When** troca o filtro de Curso, **Then**
   vale a regra do filtro de Curso da US-39 (spec 002).
5. **Given** não há ouvintes nas sessões Realizadas dos filtros, **When** a Secretaria consulta,
   **Then** o sistema exibe "Nenhum ouvinte encontrado para o período e filtros selecionados"
   (MX-07).
6. **Given** um docente (inclusive o Professor da Disciplina ou o Coordenador) abre o endereço de
   Ouvintes das defesas, **When** a tela é pedida, **Then** o sistema recusa o acesso (P8).
7. **Given** o usuário não está autenticado, **When** tenta abrir Ouvintes das defesas, **Then** o
   sistema exibe a tela de login e, após a autenticação, a tela pedida (US-30 cenário 11).

---

### User Story 5 - Declaração de participação na banca (Priority: P3)

Como membro efetivo da banca (Docente ou Membro Externo), recebo por e-mail, na liberação do
resultado, a declaração individual de participação em PDF, com código de validação, e posso
baixar a segunda via em Minhas bancas, com o mesmo código.

**Why this priority**: comprovação de participação (RBN-DEF-08.3, Could Have).

**Independent Test**: liberar o resultado de uma sessão e conferir os e-mails e a segunda via em
Minhas bancas, inclusive com suplente acionado.

**Acceptance Scenarios**:

1. **Given** o Orientador liberou o resultado e a sessão ficou Realizada, **When** o sistema
   encerra a sessão, **Then** consolida os ouvintes e envia por e-mail a cada membro titular a
   declaração em PDF com código único (US-30 cenário 7).
2. **Given** a sessão está Realizada, **When** um membro titular aciona Declaração em Minhas
   bancas, **Then** o sistema baixa a declaração com o mesmo código de validação (US-30 cenário 8).
3. **Given** o suplente foi acionado no lugar do 2º Avaliador, **When** o resultado é liberado,
   **Then** a declaração vai para o suplente (papel de 2º Avaliador) e não para o titular ausente;
   o Suplente não acionado não recebe declaração (membros efetivos, RBN-DEF-08.3).
4. **Given** o envio de um e-mail falha, **When** o resultado é liberado, **Then** a liberação não é
   desfeita, a falha fica no log e a segunda via continua disponível em Minhas bancas.

---

### User Story 6 - Agenda de defesas em PDF (Priority: P2)

Como Orientador, Professor da Disciplina, Coordenador de Curso ou Secretaria, gero, na tela
Defesas, a agenda pública de todas as defesas Agendadas e Reagendadas do período (e do curso, para
a Coordenação e a Secretaria), em PDF agrupado por dia, para divulgar pelos canais institucionais.

**Why this priority**: divulgação das sessões (RBN-DEF-08.1, Should Have).

**Independent Test**: com sessões em vários status, cursos e datas, gerar a agenda com filtros
diferentes e conferir o conteúdo e a recusa sem defesas.

**Acceptance Scenarios**:

1. **Given** existem defesas Agendadas e Reagendadas no período, **When** o usuário aciona Agenda
   de defesas (PDF), **Then** o sistema gera o PDF agrupado por dia, com data, horário, título,
   aluno, orientador e local ou link (US-30 cenário 9).
2. **Given** o Coordenador de Curso escolheu Sistemas de Informação no filtro de Curso, **When**
   aciona Agenda de defesas (PDF), **Then** o PDF traz só as bancas desse curso (US-30 cenário 10).
3. **Given** não há defesas Agendadas ou Reagendadas no período, **When** o usuário aciona Agenda de
   defesas (PDF), **Then** o sistema exibe "Não existem defesas agendadas para o período
   selecionado" e não gera arquivo (US-30 cenário 18).
4. **Given** há sessões Em Andamento, Realizadas e Canceladas no período, **When** o usuário gera a
   agenda, **Then** elas não aparecem (só Agendada e Reagendada, RBN-DEF-08.1).
5. **Given** um Orientador tem só uma banca no período e há outras cinco Agendadas, **When** gera
   a agenda, **Then** o PDF traz as seis sessões, de todos os cursos (P2).
6. **Given** o usuário não está autenticado, **When** tenta abrir o endereço da agenda, **Then** o
   sistema exibe a tela de login e, após a autenticação, inicia o download (US-30 cenário 11).
7. **Given** o Aluno ou o Membro Externo abre o endereço da agenda, **When** a agenda é pedida,
   **Then** o sistema recusa o acesso (a US-30 F não os lista).

---

### Edge Cases

- **Sessão Reagendada e ouvintes**: a E7 cita "Agendada ou Cancelada"; uma sessão Reagendada também
  ainda não ocorreu, então o botão Ouvintes não aparece nela (mesma mensagem da E7; P3). Uma sessão
  Em Andamento reagendada (spec 007, D2 da spec 008) mantém os ouvintes já registrados, mostrados
  só para leitura até voltar a Em Andamento.
- **Mesmo aluno ouvinte em várias sessões**: o registro em `Ouvintes` é único por matrícula; a
  presença em cada sessão é uma linha própria. Se o nome informado para uma matrícula já cadastrada
  for diferente do gravado, vale o nome gravado, sem aviso (P4).
- **Remover um ouvinte** apaga só a presença naquela sessão; o registro do aluno continua (pode
  ter presença em outras sessões).
- **Assinatura de membro da banca ausente no disco** (deploy no Render gratuito): o PDF sai sem a
  imagem daquele membro (decisão de 2026-11-03, spec 008); não há texto no lugar.
- **Assinatura do Coordenador cadastrada, mas ausente no disco**: a Ata sai sem a imagem dele, sem
  E2, e a ausência vai para o log (Q-140).
- **Coordenador trocado depois da liberação**: a Ata gerada depois mostra o Coordenador atual (não
  há histórico de coordenadores; risco aceito, ideia futura S-05).
- **Curso sem Coordenador cadastrado**: tratado como Coordenador sem assinatura (E2); a
  notificação vai à Secretaria do curso (MX-09; P15).
- **Coordenador cadastra a assinatura depois da liberação**: o download seguinte já gera a Ata, sem
  nova ação do Orientador (os PDFs são sob demanda).
- **Ocorrências e reagendamento**: a ocorrência registrada com a sessão Em Andamento continua
  gravada se a sessão for reagendada; volta a ser editável quando a sessão estiver Em Andamento de
  novo, até a liberação.
- **Declaração e segunda via com código igual**: o código é calculado a partir da sessão e do
  membro (dicionário, regra 4), então a segunda via sai sempre com o mesmo código, sem armazenar
  nada.
- **Agenda com filtro de período inválido**: valem as mensagens do filtro da spec 007 (datas
  invertidas ou fora do formato); nenhum PDF é gerado.
- **Falha na geração da agenda ou da declaração**: o mesmo tratamento da US-28 E3 (log, sem
  arquivo, mensagem); para a declaração enviada por e-mail, só o log.

## Requirements *(mandatory)*

### Functional Requirements — Ata Final e Folha de Aprovação (US-28; RBN-DEF-07.1 a 07.3)

- **FR-001** [RBN-DEF-07.1]: O sistema MUST gerar a Ata Final em PDF não editável, sob demanda, a
  partir da liberação do resultado, no padrão institucional de `docs/Modelo Ata final.pdf`, com:
  logos da UEA e da EST nas pontas e, centralizado, "Universidade do Estado do Amazonas - UEA",
  "Escola Superior de Tecnologia - EST" e "Curso de {curso}"; título "ATA FINAL DE AVALIAÇÃO DE
  TRABALHO DE CONCLUSÃO DE CURSO I" ou "II", conforme a etapa; "1. Dados de Identificação" (nome
  do aluno, título do trabalho e Professor Orientador); tabela de notas do Primeiro Avaliador, do
  Segundo Avaliador e do Orientador (o suplente acionado na linha do titular substituído) e a
  MÉDIA FINAL; parecer;
  a observação "Em caso de artigos, se Qualis A ou B, a nota final será o valor máximo entre 6,0 e
  a média dos avaliadores", quando aplicada; "Assinaturas:" com a imagem de assinatura de cada um
  dos 3 membros, tirada da cópia gravada em cada avaliação enviada (spec 008), e o nome; "Data:"
  com a data da defesa; e o nome, o cargo (Coordenador ou Coordenadora do Curso, flexionado pelo
  primeiro nome, pois o cadastro não guarda gênero) e a imagem de assinatura do Coordenador de
  Curso, lidos do perfil no momento do download.
- **FR-002** [RBN-DEF-07.2]: O sistema MUST gerar a Folha de Aprovação em PDF não editável, sob
  demanda, só em TCC 2 com parecer Aprovado ou Aprovado com Correções (modalidades Monografia e
  Artigo Científico), no padrão institucional de `docs/Modelo Folha de Aprovacao.pdf`, com: logos
  e cabeçalho da Ata; título "FOLHA DE APROVAÇÃO"; título do trabalho; nome do aluno; a
  frase "Trabalho de Conclusão de Curso defendido e aprovado pela banca avaliadora constituída
  pelos professores:"; os membros com titulação e papel (Presidente, Avaliador e Avaliador);
  "Manaus, DD de mês de AAAA" com a data da defesa; e as imagens das assinaturas dos 3 membros,
  tiradas da cópia gravada em cada avaliação enviada, sem nenhuma nota nem média.
- **FR-003** [RBN-DEF-07.3]: O sistema MUST oferecer um botão de download para cada documento,
  depois da liberação: na janela Sessão de defesa (bloco `documentos`, aberta por Minhas bancas,
  pela aba Defesas da turma ou pela tela Defesas) aos membros efetivos da banca, ao Professor da
  Disciplina da turma e à Secretaria do curso; e na aba Meu TCC ao Aluno, só com a Folha de
  Aprovação das sessões Realizadas do TCC, cada uma com a data da defesa (P14); o Aluno não recebe
  o botão da Ata Final. A Folha de Aprovação MUST aparecer só quando existir (TCC 2 aprovado); em
  TCC 1 e com parecer Reprovado, só a Ata Final (aos demais perfis).
- **FR-004** [RBN-DEF-07.3]: O sistema MUST recusar o download da Folha de Aprovação de TCC 1 com
  "A Folha de Aprovação não se aplica ao TCC 1" e de trabalho Reprovado com "Documento indisponível
  para trabalhos reprovados", também pelo endereço direto.
- **FR-005** [RBN-DEF-07.3]: O sistema MUST recusar o download, com "Você não tem permissão para
  acessar os documentos desta defesa", a quem não é membro efetivo da banca (inclusive o Suplente
  não acionado; P5), Professor da Disciplina da turma nem Secretaria do curso, e ao Aluno do TCC
  na Ata Final (a Folha de Aprovação ele baixa); MUST recusar com a mesma mensagem qualquer
  download antes da liberação do resultado (P13).
- **FR-006** [RBN-DEF-07.1][RBN-CAD-13.1]: Quando o Coordenador de Curso do curso do TCC nunca
  cadastrou a imagem de assinatura (caminho vazio no perfil) ou o curso não tem Coordenador, o
  sistema MUST não gerar a Ata Final. Na liberação, depois do commit, MUST alertar o Orientador na
  tela com "Não foi possível gerar a Ata Final: o Coordenador de Curso não possui assinatura
  cadastrada no perfil" e notificar, uma vez, o Coordenador (MX-03) ou, sem Coordenador, a
  Secretaria do curso (MX-09). Em todo download da Ata enquanto a situação durar, MUST mostrar a
  mesma mensagem ao Orientador e a MX-08 aos demais perfis, sem nova notificação. A liberação do
  resultado (spec 008) não é desfeita nem bloqueada. A Folha de Aprovação, que não leva a
  assinatura do Coordenador, continua disponível. Com o caminho gravado e o arquivo ausente do
  disco, a E2 não se aplica: a Ata sai sem a imagem e a ausência vai para o log (Q-140).
- **FR-007** [RBN-DEF-07.1][RBN-DEF-07.2]: Se a geração falhar, o sistema MUST não entregar nem
  gravar arquivo, MUST registrar a falha no log e MUST exibir "Erro ao gerar os documentos da
  defesa. Tente realizar o download novamente em instantes".
- **FR-008** [RBN-DEF-07.1][RBN-DEF-07.2]: Os dados dos documentos MUST vir do resultado congelado
  da sessão (nota final, parecer e notas e assinaturas dos membros efetivos) e da data da defesa
  (`def_data`), sem digitação manual (RAN-DEF-07, Maturidade); o nome e a assinatura do
  Coordenador e as titulações são lidos no momento do download (P12; Clarifications).

### Functional Requirements — Ouvintes (US-30; RBN-DEF-08.2)

- **FR-009** [RBN-DEF-08.2]: O sistema MUST exibir o botão Ouvintes na janela Sessão de defesa
  (bloco `ouvintes`) só ao Orientador do trabalho e ao Professor da Disciplina da turma, e só com a
  sessão Em Andamento ou Realizada; nas demais (Agendada, Reagendada e Cancelada), MUST não exibir
  o botão e informar "O registro de ouvintes fica disponível apenas durante ou após a sessão", e as
  presenças já gravadas aparecem só para leitura (P3). Com a sessão Em Andamento ou Realizada, a
  Secretaria do curso MUST ver a lista de ouvintes só para leitura (P6); os demais perfis não veem
  a lista. Com a turma arquivada, o botão Ouvintes MUST NOT aparecer e a lista fica só para
  leitura também ao Orientador e ao Professor da Disciplina (Clarifications).
- **FR-010** [RBN-DEF-08.2]: A janela Ouvintes MUST mostrar os ouvintes já registrados e permitir
  Adicionar (Nome Completo e Matrícula), Remover, Cancelar e Salvar; Salvar MUST gravar a lista
  inteira de uma vez e exibir "Ouvintes salvos com sucesso".
- **FR-011** [RBN-DEF-08.2]: O sistema MUST validar: Matrícula com exatamente 10 dígitos numéricos
  ("A matrícula deve conter exatamente 10 dígitos numéricos"); Nome Completo só com letras, acentos
  e espaços, não vazio, até 150 caracteres ("O nome deve conter apenas letras, acentos e espaços e
  ter até 150 caracteres"); e nenhuma matrícula repetida na mesma sessão ("Este aluno já foi
  registrado como ouvinte nesta defesa"). Com qualquer erro, nada é gravado e o campo é destacado.
  Matrícula já cadastrada reaproveita o registro existente e mantém o nome gravado, sem aviso (P4).
- **FR-012** [RBN-DEF-08.2]: Quem não é o Orientador do trabalho nem o Professor da Disciplina da
  turma MUST ser recusado, também pelo endereço direto, com "Você não tem permissão para esta
  ação"; a mesma recusa vale para gravar ouvintes com a turma arquivada.

### Functional Requirements — Ocorrências (US-30; RBN-DEF-08.5)

- **FR-013** [RBN-DEF-08.5]: O sistema MUST oferecer ao Orientador do trabalho, com a sessão Em
  Andamento e antes da liberação, o botão Ocorrências (bloco `ocorrencias`) com um campo de texto
  livre opcional de até 2.000 caracteres; acima disso, MUST não salvar, destacar a caixa de texto
  e avisar do limite (US-30 E5; MX-01). Ao salvar, MUST exibir "Ocorrências salvas com sucesso"
  (MX-06, diagrama 05).
- **FR-014** [RBN-DEF-08.5]: O texto gravado MUST aparecer somente para leitura à Secretaria do
  curso e ao Professor da Disciplina da turma e, depois da liberação, também ao Orientador, sem o
  botão de edição. Avaliadores, Suplente e Aluno MUST NOT ver as ocorrências (P10).
- **FR-015** [RBN-DEF-08.5]: Quem não é o Orientador do trabalho, inclusive o Professor da
  Disciplina (P9), MUST ser recusado ao tentar gravar ocorrências, também pelo endereço direto, com
  "Você não tem permissão para esta ação".

### Functional Requirements — Ouvintes das defesas (US-30; RBN-DEF-08.4)

- **FR-016** [RBN-DEF-08.4]: O sistema MUST oferecer só à Secretaria o item de menu "Ouvintes das
  defesas", somente leitura, com os ouvintes das sessões Realizadas: Nome Completo, Matrícula,
  título do trabalho, aluno, orientador, data da defesa e a indicação de 2 horas de atividades
  complementares por sessão assistida; sem resultados, MUST exibir a MX-07. Outros perfis MUST ser
  recusados (P8). O consolidado com exportação fica para o relatório do Épico 3 (RBN-REL-03.4).
- **FR-017** [RBN-DEF-08.4][RBN-DEF-01.5][RBN-CAD-14.1]: A lista MUST ter o filtro de período das
  defesas (spec 007) e o filtro de Curso (spec 002, US-39), com as mesmas regras e mensagens.
- **FR-018** [RBN-DEF-08.4]: O sistema MUST NOT emitir declaração ao ouvinte (as horas são lançadas
  pela Secretaria fora do sistema).

### Functional Requirements — Declaração de participação (US-30; RBN-DEF-08.3)

- **FR-019** [RBN-DEF-08.3]: Na liberação do resultado, depois do commit e sem travar a tela, o
  sistema MUST enviar a cada membro efetivo da banca (inclusive o suplente acionado e o Membro
  Externo) um e-mail com a declaração individual de participação em PDF, gerada em memória, com
  código de validação alfanumérico único (MX-04 e MX-05); falha de geração ou de envio MUST ir
  para o log, sem desfazer a liberação.
- **FR-020** [RBN-DEF-08.3]: O código MUST ser calculado a partir da sessão e do membro, sem
  armazenamento (dicionário, regra 4), e ser o mesmo na segunda via; o documento MUST dizer que o
  código não constitui assinatura digital (REQ-WNT-09).
- **FR-021** [RBN-DEF-08.3][RBN-DEF-05.4]: Em Minhas bancas, o botão Declaração MUST aparecer nas
  sessões Realizadas para os membros efetivos e baixar a segunda via; para quem não é membro
  efetivo (inclusive o Suplente não acionado) e antes da liberação, o download MUST ser recusado
  com "Você não tem permissão para acessar os documentos desta defesa" (US-28 E6; P13).

### Functional Requirements — Agenda de defesas (US-30; RBN-DEF-08.1)

- **FR-022** [RBN-DEF-08.1]: Na tela Defesas, o sistema MUST oferecer o botão "Agenda de defesas
  (PDF)" ao Orientador (Docente), ao Professor da Disciplina, ao Coordenador de Curso e à
  Secretaria, que gera o PDF com as sessões Agendadas e Reagendadas do período aplicado na tela,
  agrupadas por dia em ordem cronológica, cada uma com data (DD/MM/AAAA), horário (HH:MM, 24
  horas), título, aluno, orientador e local ou link. O Aluno e o Membro Externo MUST NOT ver o
  botão e MUST ser recusados pelo endereço direto.
- **FR-023** [RBN-DEF-08.1]: Sem defesas Agendadas ou Reagendadas nos filtros, o sistema MUST não
  gerar arquivo e exibir "Não existem defesas agendadas para o período selecionado".
- **FR-024** [RBN-DEF-08.1][RBN-CAD-14.1]: A agenda é pública (P2): para o Orientador e o Professor
  da Disciplina, MUST trazer todas as sessões Agendadas e Reagendadas do período, de todos os
  cursos, sem seguir a visibilidade da lista Defesas (spec 007, FR-024); para o Coordenador e a
  Secretaria, MUST aplicar também o filtro de Curso escolhido na tela.

### Key Entities *(reaproveitadas da spec 001; nenhuma nova)*

- **Ouvintes**: aluno ouvinte, único por matrícula, com nome.
- **PresencaOuvintes**: presença de um ouvinte numa sessão (a base das 2 horas por sessão).
- **Defesas**: a sessão; esta spec grava só `def_ocorrencias`.
- **BancaDefesa**, **Avaliacoes**, **Criterios**: lidos para os documentos (pelo resultado da
  spec 008).
- **Coordenadores** e **Docentes**: o Coordenador do curso e a assinatura do perfil dele.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% dos testes, a Ata Final e a Folha de Aprovação trazem exatamente a nota final,
  o parecer, as notas e os 3 membros efetivos gravados na liberação, e a Folha não contém nenhum
  número de nota.
- **SC-002**: 100% das tentativas de download por quem não tem permissão, antes da liberação ou de
  documento que não se aplica são recusadas com a mensagem da US, sem arquivo entregue.
- **SC-003**: Nenhum arquivo é gravado em disco pela geração dos documentos, nem em falha.
- **SC-004**: O código de validação da declaração é o mesmo em 100% das segundas vias e diferente
  entre membros e entre sessões.
- **SC-005**: Todos os cenários de aceite das US-28 e US-30 têm pelo menos um teste automatizado.
- **SC-006**: 100% das mensagens exibidas são idênticas às das US-28 e US-30 ou estão na tabela
  "Mensagens a validar com a PO".

## Assumptions

- PDFs sempre sob demanda, nunca gravados (decisão de 2026-11-03; Q-132 e Q-133 abertas para os
  textos da matriz, das US e do dicionário que falam em "arquivar").
- A E2 da US-28 é verificada na liberação (alerta e notificação) e a cada download da Ata; a
  liberação em si (spec 008) segue normalmente. O alerta ao Orientador aparece na tela depois de
  Liberar Resultado (emenda à spec 008, P1, relatada; índice Q-144).
- Ouvinte com matrícula já cadastrada: o registro existente é reaproveitado e vale o nome gravado,
  sem aviso, para não mudar o nome em presenças de outras sessões (P4).
- "Orientador do trabalho" é o Presidente da banca da sessão (Clarifications, B-03).
- O código de validação não tem tela pública de verificação nesta feature (a US não a pede);
  fica registrado como ideia futura S-07 (P11).
- A declaração é enviada só aos membros efetivos (3); o Suplente não acionado não recebe nem
  baixa documentos (P5).
- O conteúdo da declaração (nome e titulação do membro, papel, aluno, título, curso, data da
  defesa, código e a nota de que não é assinatura digital) segue o texto provisório MX-05, até a
  PO enviar o modelo institucional (P16; Q-142).
- A agenda usa o período aplicado na tela Defesas (e o Curso, para Coordenação e Secretaria) e
  traz todas as sessões Agendadas e Reagendadas, não só as da lista do perfil (P2); o Aluno e o
  Membro Externo não veem o botão (a US-30 não os lista).
- Esta spec toca código já mesclado: `services_documentos.py` (stubs da spec 008), Meu TCC
  (botões Ata Final e Folha de Aprovação, hoje desabilitados, spec 005), Minhas bancas (link da
  Declaração, spec 008), `views_avaliacoes.liberar_resultado` (alerta da E2, emenda à spec 008),
  tela Defesas (botão da agenda, spec 007), menu (item "Ouvintes das defesas") e `popular_demo`;
  e o documento `docs/diagramas/Diagramas_Sequencia_PlantUML_v2.md` (nota do diagrama 05, P9). Vale a autorização
  da Q-128, com cada mudança relatada no plano e no PR.

## Mensagens a validar com a PO

Textos sem texto exato nas US — **PROVISÓRIOS** (índice Q-142). Os textos entre aspas nos FR
são cópia exata das US-28 e US-30, da matriz ou do diagrama 05 (MX-06).

| ID | Uso | Texto proposto (PROVISÓRIO) | Origem | Situação |
|---|---|---|---|---|
| MX-01 | Ocorrências acima de 2.000 caracteres | "As ocorrências devem ter até 2.000 caracteres" | US-30 E5 ("avisa do limite", sem texto exato); FR-013 | A validar |
| MX-02 | (removida) | — | P4: vale o nome gravado, sem aviso, como no diagrama 05 | Removida |
| MX-03 | Notificação à Coordenação (E2) | "Cadastre a imagem de assinatura no seu perfil: a Ata Final da defesa de {aluno} não pode ser gerada sem ela." | US-28 E2 ("notifica a Coordenação para regularizar o cadastro", sem texto) | A validar |
| MX-04 | E-mail da declaração (assunto e corpo) | Assunto "SIGTCC: declaração de participação em banca"; corpo "Segue em anexo a declaração da sua participação na banca da defesa de {aluno} em {data}. Código de validação: {codigo}." | US-30 D (sem texto) | A validar |
| MX-05 | Texto da declaração em PDF | "Declaramos que {nome}, {titulacao}, participou como {papel} da banca examinadora da defesa do Trabalho de Conclusão de Curso \"{titulo}\", de {aluno}, do curso de {curso}, realizada em {data}. Código de validação: {codigo}. Este código não constitui assinatura digital." | US-30 D e RBN-DEF-08.3 (sem texto) | A validar |
| MX-06 | Confirmação depois de salvar as ocorrências | "Ocorrências salvas com sucesso" | Diagrama 05 (`RegistrarOuvintesAgenda`, passo 3.4); a US-30 B.d não traz texto | Texto exato do diagrama |
| MX-07 | Ouvintes das defesas sem resultados | "Nenhum ouvinte encontrado para o período e filtros selecionados" | US-30 C (sem texto) | A validar |
| MX-08 | Download da Ata com a E2, para quem não é o Orientador | "A Ata Final está indisponível: o Coordenador de Curso ainda não cadastrou a assinatura no perfil" | P1 (a E2 só tem texto para o Orientador); FR-006 | A validar |
| MX-09 | Notificação à Secretaria do curso sem Coordenador (E2) | "O curso {curso} não tem Coordenador de Curso cadastrado: a Ata Final da defesa de {aluno} não pode ser gerada." | P15; FR-006 | A validar |
