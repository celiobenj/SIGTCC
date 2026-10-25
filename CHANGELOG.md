# Changelog

Histórico de alterações do SIGTCC por baseline (PGCS 7.3). Versões no padrão SemVer.

## [Não lançado]

Nada ainda.

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
- Armazenamento externo privado para assinaturas e PDFs.
- Rotina agendada (GitHub Actions de hora em hora) para prazos, expiração e início das sessões.
- Fluxo real do resultado da defesa nas US-29 e US-44 e seção Defesa do painel do aluno.

## [v0.1.0] - 30/09/2026 - Marco TP1

Baseline 1, sem tag no Git.

### Adicionado

- Criação e estruturação do repositório central.
- Publicação do protótipo de telas navegável na branch `prototype` (GitHub Pages).
- Levantamento da Matriz de Requisitos e consolidação do Plano de Integração.
