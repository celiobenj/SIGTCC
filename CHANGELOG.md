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

### Pendências registradas

- Spec 003 (índice `docs/questoes-a-rever.md`): validar as 17 mensagens provisórias M-01 a
  M-17 com a PO (Q-01); confirmar a branch `feature/feat-02-acesso-e-login` (Q-09); aprovar os
  itens de configuração da feature 003 (Q-23 e Q-27); ciência da regra compartilhada do
  Professor da Disciplina (Q-29 a Q-32); índice único em `lower(usu_email)` (Q-28).

- Trocar os descritores provisórios dos critérios pelos textos da planilha oficial de avaliação
  da EST/UEA antes do TP3 (18/11/2026) – spec 001, FR-014a e SC-007.
- Carregar os códigos de curso da UEA em `Equivalencia_Cursos` quando confirmados no Lyceum ou
  com a Secretaria – spec 001, FR-016.
- Consultar Maria Luiza Guimarães sobre os desvios e as restrições descritas só em texto
  (identity BY DEFAULT, CHECKs de matrícula, ano, semestre e faixas de nota, `CHECK` de e-mail
  vazio e ordem física das colunas) – plan.md da spec 001, Pendências.
