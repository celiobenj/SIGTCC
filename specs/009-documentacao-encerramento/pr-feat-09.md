# [Feat-09] Documentação e Encerramento (US-28, US-30)

**Origem:** `feature/feat-09-documentos` -> **Destino:** `develop` (merge `--no-ff`, PGCS 6.4)
**Spec:** `specs/009-documentacao-encerramento/` (`spec.md`, `plan.md`, `research.md`,
`data-model.md`, `contracts/`, `quickstart.md`, `tasks.md`)
**Responsável:** Célio Benjamim

### 1. Resumo da Alteração

Encerramento da defesa no app `defesa` (Épico 2), sem tabela, coluna nem migração nova (grava só
`Ouvintes`, `Presenca_Ouvintes` e `Defesas.def_ocorrencias`):

- **Ata Final e Folha de Aprovação** (US-28; DEF-07.1 a 07.3): PDFs gerados sob demanda a cada
  download e nunca gravados, com as notas e as assinaturas da banca (a Folha sem nenhuma nota) e
  a assinatura do Coordenador de Curso. Ficam na janela "Sessão de defesa" e na aba Meu TCC
  (documentos de cada sessão Realizada). Há recusa por perfil, antes da liberação, para a Folha
  de TCC 1 e para trabalho reprovado. A E2 (Coordenador sem assinatura ou curso sem Coordenador)
  vale na liberação e em todo download (Q-140): o Orientador recebe um alerta e o Coordenador ou a
  Secretaria do curso é notificado.
- **Ouvintes** (US-30; DEF-08.2): janela "Ouvintes" para o Presidente da banca e o Professor da
  Disciplina, com a sessão Em Andamento ou Realizada, e os botões Adicionar, Remover e Salvar
  (`ouvintes.js`). A Secretaria do curso vê a lista só para leitura.
- **Ocorrências** (DEF-08.5): janela do Presidente da banca até a liberação, com contador de
  2.000 caracteres. A Secretaria e o Professor da Disciplina leem.
- **Ouvintes das defesas** (DEF-08.4): tela e item de menu só da Secretaria, com filtros de
  período e de Curso e 2 horas por sessão assistida.
- **Declaração de participação** (DEF-08.3): PDF com código de validação (HMAC da `SECRET_KEY`,
  sem armazenamento), enviado por e-mail a cada membro efetivo na liberação, numa thread, sem
  travar a tela. A segunda via fica em "Minhas bancas" e na janela da sessão.
- **Agenda de defesas (PDF)** (DEF-08.1): botão na tela Defesas, com as sessões Agendadas e
  Reagendadas do período, agrupadas por dia.
- **Risco aceito (research B6):** se a `SECRET_KEY` for trocada, os códigos de validação das
  segundas vias seguintes mudam. Isso só acontece em incidente, porque a troca também derruba
  todas as sessões de login. Sem a tela de verificação (S-07), o efeito é a segunda via sair com
  um código diferente do e-mail original. O documento diz que o código não é assinatura digital.

**Commits**

| Commit | Título | Arquivos |
|---|---|---|
| `829ac28` | docs(feat-09): especificar documentacao e encerramento | 13 (spec, plano, tasks; emenda da spec 008; diagramas; índice) |
| `6c305bd` | test(feat-09): apoio de sessao liberada e coordenador | 3 |
| `d75e50b` | feat(feat-09): base de permissoes e servicos de documentos | 12 |
| `49f32f5` | feat(feat-09): gerar ata final e folha de aprovacao sob demanda | 17 |
| `7448869` | feat(feat-09): registrar ouvintes da sessao de defesa | 12 |
| `bcf445c` | feat(feat-09): listar ouvintes das defesas para a secretaria | 7 |
| `7ba54de` | feat(feat-09): gerar agenda de defesas em pdf | 8 |
| `a33c24d` | feat(feat-09): registrar ocorrencias da sessao | 9 |
| `a9c093b` | feat(feat-09): enviar declaracao de participacao na liberacao | 12 |
| `050fce4` | chore(feat-09): popular demonstracao e atualizar documentos | 7 |
| `6c5f4a3` | docs(feat-09): registrar a validacao manual | 3 |
| (este) | docs(feat-09): preparar o texto do pr | 2 (este arquivo e o plan) |

**Mudanças em código e documentos de outras specs** (aprovadas na Q-128, relatadas aqui):

| IC | Arquivo | O que mudou | Motivo |
|---|---|---|---|
| IC-01 | `defesa/services_documentos.py` (008) | corpos reais de `ao_liberar_resultado` e `declaracao_disponivel`, sem mudar a assinatura nem o ponto de chamada; funções novas do contrato §1 | contrato §2 da 008; FR-019 a FR-021 |
| IC-02 | `defesa/views_avaliacoes.py` (008) | depois da liberação, chama `avisar_pendencia_da_ata` e mostra o alerta da E2 (`messages.warning`), sem desfazer nem bloquear a liberação | P1; emenda registrada na spec 008 (Q-144) |
| IC-03 | `defesa/views_defesa.py`, `defesa/sessao.html` (007/008) | `contexto_da_sessao` com `documentos` e `ouvintes`; blocos documentos, ouvintes e ocorrências | contrato §3 da 007; FR-003, FR-009, FR-013 |
| IC-04 | `defesa/minhas_bancas.html` (008) | atalho "Declaração" aponta para `defesa:declaracao` (segunda via) | FR-021 |
| IC-05 | `cadastro/views_tcc.py`, `cadastro/tcc/meu_tcc.html` (005/008) | documentos da defesa na aba Meu TCC; saem os botões desabilitados "Ata Final" e "Folha de Aprovação" | FR-003; P14 |
| IC-06 | `defesa/views_defesa.py`, `defesa/defesas.html` (007) | botão "Agenda de defesas (PDF)" com os filtros atuais | FR-022 |
| IC-07 | `cadastro/menu.py` (003) | item "Ouvintes das defesas" (Secretaria) | FR-016 |
| IC-08 | `defesa/permissoes_defesa.py`, `urls.py`, `mensagens.py` (007/008) | só acréscimos: permissões, 7 rotas, textos das US-28/US-30 e MX | research B2, B3 |
| IC-09 | `cadastro/management/commands/popular_demo.py` | ouvintes, ocorrências, Suplente não acionado, assinatura do Coordenador de Eng. Comp. e Coordenadores de SI e LC sem assinatura (E2) | research B14 |
| IC-10 | `docs/diagramas/Diagramas_Sequencia_PlantUML_v2.md` | nota do diagrama 05 (ocorrências só do Orientador); passo da E2 na liberação no diagrama 28 | P9; P1 (Q-144) |
| IC-11 | `cadastro/views.py` (003) | `SEM_PERMISSAO_DOCUMENTOS` em `MENSAGENS_403` | US-28 E6 |
| IC-12 | `cadastro/services.py` (003) | `enviar_email(..., anexos=None)`: com anexos usa `EmailMessage`; sem anexos, a mesma chamada a `send_mail` de antes | research B7; revisão M-04 |
| IC-13 | `specs/008-avaliacao-resultados/spec.md`, `contracts/servicos-avaliacoes.md` | Clarifications de 2026-11-04 e linha nova no §2 (`avisar_pendencia_da_ata`) | mudança depois do merge começa pela spec; revisão I-09 |
| IC-14 | `defesa/pdf.py` (008) | `threading.Lock` de módulo em volta de `gerar_pdf` | revisão I-07 (estado global do xhtml2pdf) |
| IC-15 | `defesa/services_avaliacoes.py` (008) | docstring de `minhas_bancas` (consulta a mais nas sessões Realizadas) | revisão M-11 |
| IC-16 | `defesa/tests/apoio_avaliacao.py`, `test_us27_liberacao.py`, `test_minhas_bancas.py`, `test_pdf.py` (008); `cadastro/tests/test_navegacao_tcc.py` (004/005) | apoio cria Coordenador com assinatura; alerta da E2 na liberação; link da Declaração; teste das duas threads (IC-14); botões desabilitados do Meu TCC saíram (IC-05) | revisão I-06; research B15 |
| IC-17 | `docs/diagramas/Rastreabilidade_Diagramas_Codigo.md`, `CHANGELOG.md`, `docs/arquitetura/Componentes_SIGTCC.drawio` | `:GeradorDocumentosPDF` deixa de ser stub; entram `services_ouvintes`, `views_documentos` e `views_ouvintes`; entrada da feat-09; rótulo do componente Defesa (PNG fica na Q-137) | revisão I-09 |
| IC-18 | `defesa/permissoes_defesa.py` (008) | `_e_presidente` delega para a pública `e_presidente` | revisão M-02; B-03 |

### 2. Rastreabilidade com o Projeto

* **Feature Impactada:** Feature 09 - Documentação e Encerramento
* **Histórias de Usuário Atendidas:** US-28, US-30 (RBN-DEF-07.1 a 07.3, 08.1 a 08.5)
* **Cartão no Trello:** Sprint 4 — Documentação e Encerramento

### 3. Checklist Técnico da Equipe (Definition of Done)

- [x] Lint aprovado: isort, black (`--line-length 100`) e flake8 (`--max-line-length 100`) sem
  ocorrências em `sigtcc/` (2026-11-05).
- [x] Não há variáveis, imports ou trechos de código não utilizados (flake8 limpo).
- [x] `makemigrations --check --dry-run`: "No changes detected" (a spec 009 não cria tabela nem
  coluna).
- [x] Os arquivos `.env` e os diretórios `sigtcc/media/` e `staticfiles/` NÃO foram adicionados ao
  Git.
- [x] A interface segue a paleta e os padrões de usabilidade da ISO/IEC 25010 e do protótipo de
  17/10 (validação manual de 2026-11-05). Observação: a 654 px de largura, a tabela de Ouvintes
  das defesas rola na horizontal, como na Q-141.
- [x] Não há quebras de layout nem erros no console do navegador com as telas da feature
  (validação manual de 2026-11-05).

**Testes automatizados**: suíte inteira com 1570 testes em 2026-11-05: 1 falha esperada já
existente (Q-52) e 1 falha no teste intermitente da Q-119
(`test_base_comum.test_cenario5_link_gerado_fora_das_telas`, spec 003, fora do escopo desta
feature; na rodada da fase 9 a mesma suíte passou inteira). Testes novos da feature:
`test_us28_documentos`, `test_us30_ouvintes`, `test_us30_ocorrencias`,
`test_us30_ouvintes_das_defesas`, `test_us30_declaracao`, `test_us30_agenda`,
`test_codigo_validacao`, `test_mensagens_documentos`, `test_permissoes_documentos` e
`cadastro/test_enviar_email_anexos`.

### 4. Evidência da Validação Manual (Critérios de Aceite das USs)

- [x] Cenário 1: Ata Final e Folha de Aprovação depois da liberação, com as recusas por perfil e
  para o TCC 1 (US-28): passos 1 a 4, 7 e 17.
- [x] Cenário 2: E2 da US-28 (Coordenador sem assinatura) na liberação e no download (US-28 E2;
  Q-140): passos 5 e 6.
- [x] Cenário 3: Ouvintes e ocorrências da sessão, com validações e permissões (US-30; DEF-08.2,
  08.5): passos 9 a 13a.
- [x] Cenário 4: Ouvintes das defesas para a Secretaria (DEF-08.4): passo 14.
- [x] Cenário 5: Declaração de participação com código de validação (DEF-08.3): passo 8.
- [x] Cenário 6: Agenda de defesas em PDF (DEF-08.1): passos 15 e 16.

#### Validação manual (T051)

Feita em 2026-11-05 por Claude a pedido de Célio Benjamim, no banco local separado
`sigtcc_validacao` populado pelo `popular_demo` (e-mail no console; nenhum envio real). As telas
com JavaScript foram conferidas no navegador, e o restante por script com o `Client` do Django
contra o mesmo banco (PDFs lidos com o pypdf). Roteiro do [quickstart.md](quickstart.md):

| # | Resultado |
|---|---|
| 1 | Sessão Realizada de Eng. Comp. (Coordenador com assinatura): Ata, Folha e Declaração baixam (PDF, nome sem dado pessoal), sem E2. O `popular_demo` não traz sessão pronta para liberar nesse curso; o passo foi ajustado no quickstart |
| 2 | Ata "… Curso II" com as notas 8,5 / 8,0 / 7,5, nota final 8,0, parecer, data 31/10/2026 e o Coordenador; template com 4 assinaturas (3 da banca e a do Coordenador, todas existentes no disco). Folha sem nenhuma nota, "Manaus, 31 de outubro de 2026", 3 assinaturas |
| 3 | Aluno de TCC 2: aba Meu TCC com os links da Ata e da Folha |
| 4 | Suplente não acionado: 403 "Você não tem permissão para acessar os documentos desta defesa" |
| 5 | Sessão de SI (Coordenadora sem assinatura): Registrar parecer › Liberar Resultado; Coordenadora notificada com a MX-03 e link para `/perfil/`; download da Ata pelo Presidente com "Não foi possível gerar a Ata Final…"; Folha disponível |
| 6 | Secretaria de SI: Ata com a MX-08 |
| 7 | Aluna de TCC 1: "A Folha de Aprovação não se aplica ao TCC 1" |
| 8 | Segunda via da declaração dos 3 membros efetivos com o código de validação calculado |
| 9 | Janela Ouvintes: Adicionar cria a linha (JavaScript); Salvar → "Ouvintes salvos com sucesso" |
| 10 | "Ana 2" e "12345abc90" → mensagens da US-30 com os campos destacados; matrícula repetida → "Este aluno já foi registrado como ouvinte nesta defesa"; nada gravado |
| 11 | Secretaria de SI vê ouvintes e ocorrências da sessão Em Andamento, sem botões; Avaliadores não veem |
| 12 | Ocorrências com 2.001 caracteres → "As ocorrências devem ter até 2.000 caracteres" com a caixa destacada; texto curto → "Ocorrências salvas com sucesso"; contador "Caracteres restantes" funciona |
| 13 | Docente da banca que não é o Presidente (2º Avaliador da sessão de SI TCC 1) em Ocorrências: 403 "Você não tem permissão para esta ação". A mesma docente, Professora da Disciplina de SI TCC 2, tem na sessão Realizada dessa turma o botão Ouvintes e não o de Ocorrências |
| 13a | Presidente da sessão de TCC 1 (aluna já no TCC 2) abre a sessão e vê ouvintes e ocorrências |
| 14 | Secretaria de Eng. Comp.: Ouvintes das defesas com 6 linhas e "2 horas" em cada (com 654 px de largura a tabela rola na horizontal, como na Q-141) |
| 15 | Agenda: botão na tela Defesas; PDF agrupado por dia (08/11 e 17/11) para o Orientador e para o Coordenador |
| 16 | Período sem sessões: "Não existem defesas agendadas para o período selecionado" |
| 17 | Visitante no endereço da Ata: login com `next` |

Observações:
- As assinaturas do `popular_demo` são a mesma imagem; o PDF guarda uma cópia só e a desenha em
  cada linha. A contagem por imagem distinta é conferida nos testes automatizados.
- O banco local `sigtcc` não foi tocado.

**Pendências registradas** (`docs/questoes-a-rever.md`):
- **Desta feature:**
  - Q-142: textos provisórios MX-01, MX-03 a MX-05 e MX-07 a MX-09 e o modelo institucional da
    declaração (PO).
  - Q-143: US-30 E9 e cenário 19 × RBN-DEF-08.5 (dono do documento de US).
  - Q-144: ciência da emenda à spec 008 e passo da E2 no diagrama 28.
  - Q-145: "Orientador do trabalho" = Presidente da banca (respondida).
- **Herdadas da feat-08 e afetadas por esta:**
  - Q-132: textos da matriz e das US-27/US-28 que pressupõem PDFs gravados (PO).
  - Q-133: colunas `def_ata_final_path` e `def_folha_aprovacao_path` sem uso (modelo lógico).
  - Q-134: PGCS e diagramas com a decisão de 2026-11-03.
  - Q-137: PNG dos diagramas de arquitetura.
  - Q-141: rolagem horizontal das tabelas.
- **Ideias futuras:** S-05 (histórico de Coordenadores), S-06 (assinaturas no banco), S-07 (tela
  de verificação do código de validação).
- **Fora do escopo:** Q-119 (teste intermitente da spec 003).

### 5. Revisão por Pares (Peer Review)

* **Revisor Designado:** [a definir]
* **Parecer do Revisor:**
  - [ ] Aprovado integralmente para merge
  - [ ] Solicitação de ajustes (detalhar nos comentários)
