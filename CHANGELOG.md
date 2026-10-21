# Changelog

Histórico de alterações do SIGTCC por baseline (PGCS 7.3). Versões no padrão SemVer.

## [Não lançado]

### Adicionado

- Projeto Django 5.2 na estrutura do PGCS 2.3 (apps `cadastro`, `defesa` e `relatorios`),
  configuração por `.env`, `requirements.txt` com versões fixas, `pyproject.toml`, `.flake8` e
  `lint.bat` (feat-01).
- Modelo de dados (spec 001, feat-01):
  - as 36 tabelas e 201 colunas do dicionário de dados de 18/10, com nomes, tipos, tamanhos e
    nulidade do documento, conferidos por teste que lê o próprio dicionário;
  - 49 restrições nomeadas: 48 CHECKs e unicidades (inclusive parciais) e a FK composta
    `Avaliacoes` → `Banca_Defesa`;
  - carga inicial: 3 cursos, 10 Áreas de Interesse e os 9 critérios oficiais de avaliação
    (pesos 7,0 + 3,0) com descritores provisórios;
  - 53 testes automatizados (conformidade, restrições, usuários e cargas).
- Acesso e Login (spec 003, feat-02; US-10, US-11, US-12, US-37 e US-38), sem tabelas novas:
  - primeiro acesso do Aluno (matrícula e e-mail institucional) e de Docente, Secretaria e
    Membro Externo (e-mail), com link de ativação assinado de 24 horas, só o mais recente válido,
    e reenvio do link vencido;
  - login por matrícula ou e-mail, com as mensagens da US-11 na ordem da spec, bloqueio de
    15 minutos após 3 senhas incorretas (cache próprio `acesso`) e sessão de 60 minutos sem uso;
  - alterar a senha (as outras sessões caem), "Esqueci minha senha" com mensagem genérica e
    reset do primeiro acesso pelo Professor da Disciplina de turma ativa do aluno;
  - "Meu perfil" com os campos de cada papel, imagem de assinatura PNG ou JPG sem URL pública,
    troca de e-mail confirmada pelo novo endereço e central de notificações com sino;
  - base comum para as outras features: layout do protótipo de 17/10 (`base.html`,
    `sigtcc.css`), `perfil_requerido` e papéis, menu por app (`menu.py`), funções de link e o
    comando `criar_conta_teste`;
  - log de eventos de acesso em `LOG_DIR/acesso.log`, sem senhas, links nem e-mails completos;
  - 176 testes novos (229 no total).
- Turmas e Alunos (spec 004, feat-03; US-07, US-08 e US-09), sem tabelas novas:
  - turmas de TCC 1 e TCC 2: cadastro, edição (Descrição e Curso travados depois do primeiro
    aluno), exclusão só da turma que nunca teve aluno e arquivamento com as condições da US-07;
    turma arquivada só para consulta (MT-25 pelo endereço direto);
  - matrícula individual e importação por CSV ou XLSX com prévia (até 2 MB e 200 linhas, ";" ou
    ",", UTF-8 ou Windows-1252, XLSX com `defusedxml` e limite de descompressão), contas novas
    'Aguardando Ativação' e orientador automático nas turmas de TCC 2 de Engenharia de Computação
    e Licenciatura em Computação;
  - transferência entre turmas de TCC 2 do mesmo curso e período, com o mesmo TCC, o histórico e
    as notificações ao aluno e aos dois professores;
  - exclusão do aluno sem Proposta (duas etapas, notificação com o motivo), encerramento da
    participação como Desistente, Reprovado ou Jubilado e lista de excluídos ou transferidos;
  - acesso por turma: Professor da Disciplina e Secretaria do curso (só consulta e
    transferência); serviços compartilhados `participacao_encerrada`, `travar_turma_ativa` e
    `notificar()`;
  - carga da equivalência de cursos (EST08MCPD, EST31MSII e EST03MLV) e dependências `openpyxl`
    e `defusedxml`;
  - 192 testes novos (421 no total).

### Pendências registradas

- Spec 003 (índice `docs/questoes-a-rever.md`): validar as 17 mensagens provisórias M-01 a
  M-17 com a PO (Q-01); confirmar a branch `feature/feat-02-acesso-e-login` (Q-09); aprovar os
  itens de configuração da feature 003 (Q-23 e Q-27); ciência da regra compartilhada do
  Professor da Disciplina (Q-29 a Q-32); índice único em `lower(usu_email)` (Q-28).
- Spec 004 (índice `docs/questoes-a-rever.md`): validar os 31 textos provisórios MT-01 a MT-32
  com a PO (Q-36); confirmar a branch `feature/feat-03-turmas-e-alunos` (Q-34); confirmar a recusa
  do aluno 'Aprovado para TCC 2' em turma de TCC 1 (Q-39); ciência da regra do encerramento
  (Q-40); registros de entrega ao cadastrar entrega nova (Q-41); aprovar os itens de configuração
  da feature 004 (Q-42).

- Trocar os descritores provisórios dos critérios pelos textos da planilha oficial de avaliação
  da EST/UEA antes do TP3 (18/11/2026) – spec 001, FR-014a e SC-007.
- Consultar Maria Luiza Guimarães sobre os desvios e as restrições descritas só em texto
  (identity BY DEFAULT, CHECKs de matrícula, ano, semestre e faixas de nota, `CHECK` de e-mail
  vazio e ordem física das colunas) – plan.md da spec 001, Pendências.
