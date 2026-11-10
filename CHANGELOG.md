# Changelog

Histórico de alterações do SIGTCC por baseline (PGCS 7.3). Versões no padrão SemVer.

## [Não lançado]

### Adicionado

- Agendamento e Banca (spec 007, feat-07; US-21, US-22, US-23, US-24 e US-40, com a US-39 na
  tela Defesas), no app `defesa`, sem tabela nem coluna nova:
  - "Agendar sessão de defesa": TCC só entre os Aptos sem sessão ativa e pelo perfil do curso
    (Orientador em Eng. Comp., Professor da Disciplina em SI e LC), Local ou Link da Videochamada
    e reserva de 1 hora; a partir do menu "Defesas", da aba "Defesas" da turma e da tela de
    orientandos.
  - Banca com Presidente fixo, listas sem a orientação e sem quem já foi escolhido, cadastro rápido
    do Membro Externo, "Alterar banca" e "Acionar suplente".
  - Conflito de horário da banca na janela de 1 hora, com todos os membros numa única mensagem e
    trava dos docentes contra agendamentos simultâneos.
  - Confirmação com avisos ao Aluno e à banca (com o link do Documento para Defesa), cancelamento
    da troca de orientador pendente, "Reagendar", "Cancelar sessão" e início automático ao chegar
    o horário (nas telas e pelo comando `iniciar_sessoes`).
  - Tela "Defesas" com visibilidade por perfil e filtros de período, Status e Curso; janelas
    "Sessão de defesa" e "Histórico da defesa".
  - Contratos para a feat-08 e a feat-09: status e histórico da sessão, membros efetivos, filtro de
    período e o template da sessão com os blocos reservados.
- `popular_demo` com o cenário do roteiro manual da spec 007 (TCCs Aptos sem sessão, uma sessão em
  cada status, suplentes) e a tabela de contas do roteiro.
- Avaliação e Resultados (spec 008, feat-08; US-25, US-26 e US-27), no app `defesa`, sem tabela nem
  coluna nova:
  - janela "Critérios de avaliação" (somente leitura) e tela "Minhas bancas" (item de menu para
    Docente e Membro Externo), com as pendências em destaque;
  - formulário "Avaliação" com rascunho (só a Parte Escrita antes da sessão), envio assinado
    (imagem anexada ou do perfil, até 2 MB e 2000 × 1000 pixels, cópia sem URL pública) e "Reabrir
    minha avaliação";
  - cálculo em `Decimal` com uma casa e arredondamento comercial, nota mínima 6,0 com artigo Qualis
    A ou B homologado, "Registrar parecer" e "Liberar Resultado" com confirmação (e nova
    confirmação se a nota mudar), Status do TCC pela liberação e aviso à Secretaria (o Aluno e a
    banca não recebem aviso do resultado; Q-131 B);
  - sigilo das notas por uma única função (`visao_da_avaliacao`) e seção "Resultado da defesa" na
    aba Meu TCC, com a Data Limite da Versão Final em TCC 2 aprovado;
  - `xhtml2pdf` 0.2.28 no `requirements.txt` e utilitário de PDF em memória (`defesa/pdf.py`), sem
    acesso à rede, para a feat-09; ponto de chamada `services_documentos.ao_liberar_resultado`;
  - `popular_demo` com avaliações de exemplo, uma sessão pronta para liberar e dois resultados
    liberados.
- Documentação e Encerramento (spec 009, feat-09; US-28 e US-30), no app `defesa`, sem tabela nem
  coluna nova:
  - Ata Final e Folha de Aprovação em PDF, gerados sob demanda a cada download e nunca gravados,
    com as notas e as assinaturas da banca (a Folha sem nenhuma nota) e a assinatura do
    Coordenador de Curso; botões na janela "Sessão de defesa" e na aba Meu TCC (documentos de
    cada sessão Realizada); recusas por perfil, antes da liberação, da Folha de TCC 1 e de
    reprovado, e a E2 (Coordenador sem assinatura ou curso sem Coordenador) na liberação e em
    todo download;
  - janela "Ouvintes" (Presidente da banca e Professor da Disciplina, com a sessão Em Andamento ou
    Realizada), com Adicionar, Remover e Salvar, e a lista só leitura para a Secretaria do curso;
  - janela "Ocorrências" do Presidente da banca, até a liberação, com contador de 2.000
    caracteres, e leitura pela Secretaria e pelo Professor da Disciplina;
  - tela "Ouvintes das defesas" (item de menu só da Secretaria), com os filtros de período e de
    Curso e 2 horas por sessão assistida;
  - "Agenda de defesas (PDF)" na tela Defesas, com as sessões Agendadas e Reagendadas do período,
    agrupadas por dia;
  - declaração de participação em PDF, com código de validação, enviada por e-mail a cada membro
    efetivo na liberação (numa thread, sem travar a tela) e segunda via em "Minhas bancas" e na
    janela da sessão;
  - `popular_demo` com ouvintes e ocorrências nas sessões Realizadas, Suplente não acionado,
    assinatura do Coordenador de Eng. Comp. e Coordenadores de SI e LC sem assinatura (E2), e a
    tabela de contas do roteiro da spec 009.
- Dashboards de Produção (spec 010, feat-10; US-31, US-47, US-32 e US-33), no app `relatorios`,
  sem tabela nem coluna nova e só de leitura:
  - tela "Relatórios" (item de menu na seção Gestão, para Docente e Secretaria), com a lista de
    relatórios por perfil e layout único (Padrão visual com as 10 heurísticas de Nielsen);
  - Painel de atividades por docente (o Docente vê só a própria linha), Participação de Membros
    Externos, Formação e evasão, Histórico de indicadores do NUCOMP, Produção de TCCs e Artigos;
  - contagens pelo último registro do histórico do TCC na turma do período, com
    Matriculados = Sem Proposta + Ativos + Com Sucesso + Sem Sucesso e
    Total de Trabalhos = Ativos + Com Sucesso + Sem Sucesso;
  - filtros de período (atalhos, Ano/Semestre e datas), Curso e Docente no endereço da página;
  - exportação em PDF, CSV (UTF-8 com BOM, `;`) e XLSX da mesma estrutura da tela, com proteção
    contra fórmula;
  - gráficos em HTML/CSS e SVG, sem biblioteca nova, com a tabela como fonte de verdade;
  - base reaproveitável pela feat-11: registro de relatórios por decorador, formulário de filtros,
    estrutura única e exportação genérica (`contracts/base-relatorios.md`).
- `popular_demo` com o cenário dos relatórios: troca de orientador, Suplente acionado em período
  passado, terceiro período letivo com artigo copiado e Membros Externos de duas instituições numa
  sessão Realizada (a 1ª Avaliadora dessa sessão passa a ser um Membro Externo).

### Alterado

- Descritores dos 9 critérios trocados pelos textos da planilha oficial da EST/UEA (migration
  `defesa/0005_descritores_oficiais`, reversível); as colunas `cri_desc_*` passam a VARCHAR(1000), com
  o dicionário ajustado, e as telas Avaliação e Critérios respeitam as quebras de linha (spec 001,
  FR-014a; Q-03 e Q-18).
- Ata Final e Folha de Aprovação no padrão institucional da UEA/EST (logos, cabeçalho de três
  linhas, "1. Dados de Identificação", tabela de notas e assinaturas, conforme os modelos em
  `docs/`). O Aluno baixa só a Folha de Aprovação: a Ata, que traz as notas individuais, dá 403
  ao Aluno e some da aba Meu TCC (`pode_baixar_ata` e `pode_baixar_folha`; spec 009). O cargo do
  Coordenador e a titulação saem na forma neutra, "Coordenador(a) do Curso" e "Doutor(a)", porque
  o cadastro não guarda gênero (Q-155).
- Todas as questões em aberto de `docs/questoes-a-rever.md` respondidas em 10/11/2026; o
  comentário temporário de revisão saiu da constituição (Q-11), sem mudar a versão.
- O aviso do resultado da defesa vai só à Secretaria do curso: saem os avisos ao Aluno (MA-06) e à
  banca (MA-07) e a divergência DV-01 (Q-131 B; spec 008).
- Quem recebeu uma notificação de sessão de defesa e saiu da banca vê "Este item não está mais
  disponível" em vez do 403 (Q-12; specs 003 e 007).
- Documentação: `docs/ambientes.md` separa a visão de construção (desenvolvimento e validação no
  Render, para a disciplina) da implantação real (produção escalável); as tarefas por data rodam
  por execução manual, sem agendador (Q-67 C); FR-007 da spec 001 sem CHECK no banco (Q-06 B).
- Emendas da spec 010 na spec 007: `filtro_de_periodo` aceita outro período letivo
  (`ano_semestre`, opcional) e as datas dos atalhos saem de `intervalo_do_atalho`, sem mudar a tela
  Defesas (IC-03; Q-153).
- A Defesa passa a renovar a validade do Membro Externo nos eventos de banca e a conferir a conta
  de quem entra na banca (contrato da spec 002; Q-67).
- Menu com o item "Defesas" (também para o Membro Externo), aba "Defesas" na turma, link "Agendar
  defesa" na tela de orientandos e as mensagens de acesso negado da US-21 E7 e da US-40 E5 (IC-01
  a IC-06; Q-123).
- Emendas da spec 008 na spec 007: o descarte de avaliações deixa de ser stub; na alteração da
  banca, quem só troca de papel entre titulares mantém o rascunho e quem sai ou passa a Suplente
  perde (D16, Q-135); o reagendamento de sessão Em Andamento devolve os envios a "Rascunho salvo",
  mantendo as notas (D2).
- Decisão de configuração (Q-134): **sem armazenamento externo**. Os PDFs (Ata Final, Folha de
  Aprovação e declarações) são gerados sob demanda, a cada download, e nunca gravados; as
  assinaturas continuam no disco do serviço (risco aceito). Sai do "Planejado para a v0.3.0".
- Emendas da spec 009 nas specs 003, 005 e 008: `enviar_email` aceita anexos (IC-12);
  `gerar_pdf` serializa a renderização com uma trava (IC-14); a liberação do resultado mostra o
  alerta da E2 da US-28 depois da confirmação e notifica o Coordenador ou a Secretaria do curso
  (IC-02; Q-144); `ao_liberar_resultado` e `declaracao_disponivel` deixam de ser stubs; o atalho
  "Declaração" de Minhas bancas baixa a segunda via (IC-04); saem os botões desabilitados "Ata
  Final" e "Folha de Aprovação" do cartão Defesa da aba Meu TCC (IC-05).

### Corrigido

- Tabelas de todo o sistema não partem mais palavras ("Engenhari/a de/Computaç/ão", "Adria/na"):
  o texto só quebra entre palavras, colunas curtas, endereços e palavras com hífen ficam numa
  linha, e a tabela rola dentro do próprio bloco (`fix(core)`, verificado com o Playwright em 360,
  768 e 1280 px).
- `popular_demo` não esvazia mais a tabela `Criterios` (carga da spec 001) e a recarrega se um
  `popular_demo` anterior a apagou.

## [v0.2.1] - 25/10/2026 - Hotfix: nomes iguais às US v3.4 e aos diagramas

Correção de rótulos da interface para coincidirem exatamente com as Histórias de Usuário v3.4 e
com os diagramas de sequência PlantUML v2. O comportamento não muda.

### Alterado

- Aba **Entregas** no lugar de "Atividades", para o Aluno e o Professor da Disciplina (US-15,
  US-16, US-43; Q-80). "Cadastrar atividade" continua.
- Gestão de Contas (US-03, US-05; Q-121): "Cadastrar docente", "Cadastrar secretaria",
  "Cadastrar membro externo", "Alterar" nas listas, botão "Cadastrar" no cadastro de docente,
  coluna "E-mail Institucional" em Docentes e colunas Nome Completo, E-mail, Titulação,
  Instituição de Origem e Acesso em Membros externos.
- Tela de orientandos (US-18): link "Histórico" (Q-81) e coluna "Status de envio das entregas".
- Tela do aluno (US-41, US-08, US-09): seções "Atas" e "Publicação"; botões "Editar",
  "Transferir" e "Excluir da turma".
- Docente que não é o Professor da Disciplina ao abrir a turma vê "Você não tem permissão para
  acessar esta página." (US-07 E8).
- Diagramas de sequência: o `.drawio` de 24/10 deu lugar aos 36 diagramas PlantUML v2, com a
  tabela de rastreabilidade participante → código em `docs/diagramas/`.
- Testes de mensagens da spec 002 voltam a conferir com a v3.4; a cópia da v3.3 em
  `docs/fonte/anteriores/` foi removida.

### Corrigido

- Roteiro de validação: a opção "Todos" do filtro de curso continua prevista na v3.4 (US-39,
  fluxo alternativo A).

## [v0.2.0] - 25/10/2026 - Marco TP2

Baseline 2: Módulo de Cadastro e Manutenção completo (30 US do Épico 1), sistema publicado no
Render a partir da `main` e PGCS 1.2. Suíte com 1115 testes automatizados.

### Adicionado

- Fluxo Spec-Driven Development com o Spec Kit (`specs/` e `.specify/`), constituição do
  projeto, `CLAUDE.md`, `GUIA_SDD.md`, agentes do fluxo e índice `docs/questoes-a-rever.md`
  (feat-00).
- Documentos de referência em `docs/fonte/` (matriz de 17/10, Histórias de Usuário v3.4, modelo
  lógico de 18/10, cronograma, PGCS e protótipo), diagramas de arquitetura em `docs/arquitetura/`
  (componentes, implantação e pacotes) e diagramas de sequência de 24/10 em `docs/diagramas/`
  (feat-00).
- Projeto Django 5.2 na estrutura do PGCS 2.3 (apps `cadastro`, `defesa` e `relatorios`),
  configuração por `.env`, `requirements.txt` com versões fixas, `pyproject.toml` e `.flake8`
  (feat-01).
- Modelo de dados (spec 001, feat-01):
  - as 36 tabelas e 201 colunas do dicionário de dados de 18/10, com nomes, tipos, tamanhos e
    nulidade do documento, conferidos por teste que lê o próprio dicionário;
  - 49 restrições nomeadas: 48 CHECKs e unicidades (inclusive parciais) e a FK composta
    `Avaliacoes` → `Banca_Defesa`;
  - carga inicial: 3 cursos, 10 Áreas de Interesse e os 9 critérios oficiais de avaliação
    (pesos 7,0 + 3,0) com descritores provisórios.
- Acesso e Login (spec 003, feat-02; US-10, US-11, US-12, US-37 e US-38), sem tabelas novas:
  - primeiro acesso do Aluno (matrícula e e-mail institucional) e de Docente, Secretaria e
    Membro Externo (e-mail), com link de ativação assinado de 24 horas, só o mais recente válido,
    e reenvio do link vencido;
  - login por matrícula ou e-mail, bloqueio de 15 minutos após 3 senhas incorretas e sessão de
    60 minutos sem uso;
  - alterar a senha (as outras sessões caem), "Esqueci minha senha" com mensagem genérica e
    reset do primeiro acesso pelo Professor da Disciplina;
  - "Meu perfil" com os campos de cada papel, imagem de assinatura sem URL pública, troca de
    e-mail confirmada pelo novo endereço e central de notificações com sino;
  - base comum: layout do protótipo de 17/10, `perfil_requerido`, menu por app, comando
    `criar_conta_teste` e log de eventos de acesso sem senhas, links nem e-mails completos.
- Turmas e Alunos (spec 004, feat-03; US-07, US-08 e US-09), sem tabelas novas:
  - turmas de TCC 1 e TCC 2: cadastro, edição, exclusão só da turma que nunca teve aluno e
    arquivamento com as condições da US-07; turma arquivada só para consulta;
  - matrícula individual e importação por CSV ou XLSX com prévia, contas novas 'Aguardando
    Ativação' e orientador automático nas turmas de TCC 2 de Engenharia de Computação e
    Licenciatura em Computação;
  - transferência entre turmas de TCC 2, exclusão do aluno sem Proposta, encerramento da
    participação (Desistente, Reprovado ou Jubilado) e lista de excluídos ou transferidos;
  - carga da equivalência de cursos e dependências `openpyxl` e `defusedxml`.
- Gestão de Contas (spec 002, feat-04; US-03, US-04, US-05, US-06 e US-50):
  - cadastro, alteração e listagem de docentes e da Secretaria, com filtro de Curso, papel de
    Coordenador (um por curso) e ações restritas ao curso do usuário;
  - inativação bloqueada por vínculos abertos (TCC ativo, convite, banca, turma e papel de
    Coordenador), reativação do docente e inativação da Secretaria;
  - membros externos com validade, troca de e-mail pelo gestor confirmada pelo novo endereço,
    expiração (comando `expirar_membros_externos` e conferência no login) e prorrogação de 7
    dias;
  - coluna `MembrosExternos.mem_prorrogado_ate` (migração `0006`, Q-69) e comando
    `criar_coordenadores` para a implantação.
- Fluxo do TCC e Entregas (spec 005, feat-05; US-13, US-14, US-15, US-16, US-29, US-43 e US-44),
  sem tabelas novas:
  - Proposta, Área de Interesse, Palavras-Chave e mudança de tema na aba Meu TCC;
  - serviço único do Status do TCC, com histórico, trilha e tabela fixa de transições;
  - cadastro de entregas por etapa, envio e substituição de link (Entregue, Entregue com Atraso
    e Não Entregue), acompanhamento por aluno e comando `enviar_lembretes_entrega`;
  - Versão Final do TCC 2, homologação (TCC Concluído) e devolução para ajuste.
- Orientação, Atas e Publicações (spec 006, feat-06; US-17, US-18, US-19, US-20, US-36, US-41,
  US-42, US-45 e US-46), sem tabelas novas:
  - pedido, cancelamento e troca de orientador, com a tela "Orientações" do docente;
  - convites de coorientação, coorientadores externos, substituição e remoção;
  - atas de orientação com comentários, Apto para Defesa e Correções Conferidas;
  - painel do aluno na aba Alunos da turma, publicação do artigo e tela de aproveitamento do
    Coordenador.
- Implantação no Render (release): Blueprint `render.yaml` (serviço web e PostgreSQL 16 no plano
  gratuito), `settings.py` lendo `DATABASE_URL` e o endereço do Render, arquivos estáticos pelo
  WhiteNoise, `gunicorn`, e-mail pelo Brevo por SMTP (porta 2525), log de acesso na saída padrão
  (`LOG_STDOUT`) e guia `docs/deploy-render.md`.
- Comando `popular_demo` (release): limpa o banco e carrega cenários fictícios de demonstração
  (68 contas, 8 turmas e 50 TCCs em todos os Status), com travas contra banco local.
- Verificação automática com `pre-commit` (isort, Black e Flake8), `requirements-dev.txt` e
  `.gitattributes` com `eol=lf` (release, PGCS 3.3).

### Alterado

- Histórias de Usuário: v3.3 → v3.4 (revisão de redação). A v3.3 fica em `docs/fonte/anteriores/`
  só para os testes de mensagens da spec 002, até a revisão da Q-121.
- PGCS 1.1 → 1.2: produção no Render no lugar de Vercel, Neon e Vercel Blob; seção 2.4 com os
  diagramas de arquitetura; itens de configuração, árvore, variáveis, dependências, branches,
  baselines (TP2 em 25/10) e rito de auditoria atualizados.
- Diagramas de componentes, implantação e pacotes alinhados ao Render e ao código da v0.2.0.
- O `lint.bat` foi substituído pelo pre-commit; as ferramentas de desenvolvimento saíram do
  `requirements.txt`; constituição 1.0.2.
- Modelo de Pull Request igual ao PGCS 6.3; `.gitignore` com `/staticfiles/`, `*.dump` e `*.sql`.
- Exemplos de importação de alunos movidos da raiz para `specs/004-turmas-alunos/exemplos/`.
- O `.puml` da matrícula por CSV deu lugar à página MatricularAluno dos diagramas de sequência.

### Corrigido

- Reversão das cargas iniciais por SQL nas migrações (feat-01).
- Aviso ao orientador também na troca de Área e Palavras-Chave, com reconferência do TCC, e link
  do histórico e campo Link preenchido no envio de entrega (feat-05).
- Janela "Registrar coorientador" mostra só a caixa do Tipo escolhido (feat-06).
- Aluno "Sem Proposta" com pedido de orientação pode ser excluído da turma; os pendentes são
  cancelados com aviso ao docente (feat-06, Q-120).

### Pendências

- Q-121: revisar a spec 002 contra as US-03 a US-06 reescritas na v3.4 (rótulos, mensagens e
  passos novos) antes de alterar o código.
- US-39 (filtro por curso) parcial: existe nas listas de contas e no aproveitamento de artigos;
  faltam as telas de turmas e, nos próximos épicos, defesas e relatórios.
- Spec 002: evidência da validação manual (T044) ainda não registrada no `pr-feat-04.md`.
- Validação com a PO dos textos provisórios de mensagens (Q-01, Q-36, Q-95, Q-118) e das
  decisões da equipe pendentes de ciência (Q-97 a Q-99, Q-117).
- Aprovações de configuração e nomes de branch das specs 001 a 004 (Q-08 a Q-10, Q-23, Q-27,
  Q-34, Q-42 e Q-70), serviço único do Status (Q-82) e ciência dos IC-01 a IC-15 (Q-96).
- Teste instável `test_cenario5_link_gerado_fora_das_telas` no Windows (Q-119).
- Banco PostgreSQL gratuito do Render expira por volta de 24/11/2026: migrar para um banco que
  não expire (troca da `DATABASE_URL`).
- Descritores oficiais dos critérios de avaliação antes do TP3 (Q-03 e Q-18).

### Planejado para a v0.3.0 (TP3, 18/11/2026)

- Gestão da Defesa (Épico 2): agendamento sem conflito, banca, avaliação, liberação do resultado
  e PDFs da Ata Final e da Folha de Aprovação (xhtml2pdf).
- ~~Armazenamento externo privado para assinaturas e PDFs.~~ Retirado em 03/11/2026 (spec 008,
  Q-134): PDFs gerados sob demanda e assinaturas no disco do serviço.
- Rotina agendada (GitHub Actions de hora em hora) para prazos, expiração e início das sessões.
- Fluxo real do resultado da defesa nas US-29 e US-44 e seção Defesa do painel do aluno.

## [v0.1.0] - 30/09/2026 - Marco TP1

Baseline 1, sem tag no Git.

### Adicionado

- Criação e estruturação do repositório central.
- Publicação do protótipo de telas navegável na branch `prototype` (GitHub Pages).
- Levantamento da Matriz de Requisitos e consolidação do Plano de Integração.
