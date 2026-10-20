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

### Pendências registradas

- Trocar os descritores provisórios dos critérios pelos textos da planilha oficial de avaliação
  da EST/UEA antes do TP3 (18/11/2026) – spec 001, FR-014a e SC-007.
- Carregar os códigos de curso da UEA em `Equivalencia_Cursos` quando confirmados no Lyceum ou
  com a Secretaria – spec 001, FR-016.
- Consultar Maria Luiza Guimarães sobre os desvios e as restrições descritas só em texto
  (identity BY DEFAULT, CHECKs de matrícula, ano, semestre e faixas de nota, `CHECK` de e-mail
  vazio e ordem física das colunas) – plan.md da spec 001, Pendências.
