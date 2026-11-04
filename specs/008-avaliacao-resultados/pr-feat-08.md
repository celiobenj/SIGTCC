# [Feat-08] Avaliação e Resultados (US-25, US-26, US-27)

**Origem:** `feature/feat-08-avaliacao` -> **Destino:** `develop` (merge `--no-ff`, PGCS 6.4)
**Spec:** `specs/008-avaliacao-resultados/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, `tasks.md`)
**Responsável:** Célio Benjamim

### 1. Resumo da Alteração

Avaliação da banca e liberação do resultado no app `defesa` (Épico 2), sem tabela, coluna nem
migração nova:

- **Critérios e Minhas bancas** (DEF-04.1, DEF-04.2, DEF-05.4): janela "Critérios de avaliação"
  somente leitura; tela "Minhas bancas" (menu para Docente e Membro Externo) com pendências em
  destaque e atalhos Documento, Critérios, Avaliar e Declaração.
- **Avaliação** (US-25, US-26): formulário com os 9 critérios, rascunho (só a Parte Escrita antes da
  sessão), envio com assinatura anexada ou do perfil (PNG/JPG até 2 MB e 2000 × 1000 pixels,
  cópia guardada sem URL pública) e "Reabrir minha avaliação".
- **Resultado** (US-27): nota individual e final em `Decimal` com arredondamento comercial,
  nota mínima 6,0 com artigo Qualis A ou B homologado, "Registrar parecer", "Liberar Resultado"
  com confirmação (e nova confirmação se a nota mudar), sessão para "Realizada" só por
  `transicionar_status`, Status do TCC só por `atualizar_status_tcc`, avisos ao Aluno, à banca e
  à Secretaria.
- **Sigilo** (DEF-06.8): uma única função (`visao_da_avaliacao`) decide o que cada perfil vê;
  seção "Resultado da defesa" na aba Meu TCC, com a Data Limite da Versão Final em TCC 2 aprovado.
- **Infraestrutura para a feat-09**: `xhtml2pdf` 0.2.28 e `defesa/pdf.py` (PDF em memória, sem
  acesso à rede, entregue só depois da permissão); stubs `services_documentos.ao_liberar_resultado`
  e `declaracao_disponivel`. **Sem armazenamento externo**: os PDFs serão gerados sob demanda e
  nunca gravados (decisão de 2026-11-03, Q-134).

**Commits**

| Commit | Título | Arquivos |
|---|---|---|
| `88dc08e` | docs(feat-08): especificar e planejar avaliacao e resultados | spec, plano, tasks; emendas da spec 007; índice |
| `206c0da` | chore(config): adicionar xhtml2pdf as dependencias | 1 |
| `626d1b4` | feat(feat-08): gerar PDF em memoria sem acesso a rede | 8 |
| `4dc3a36` | feat(feat-08): calcular notas e descartar avaliacoes | 12 |
| `78b9de5` | feat(feat-08): exibir criterios e minhas bancas | 10 |
| `34e1e24` | feat(feat-08): lancar e enviar a avaliacao assinada | 13 |
| `5c82d38` | feat(feat-08): liberar o resultado da defesa | 15 |
| `df65ff0` | feat(feat-08): mostrar o resultado ao aluno com sigilo | 7 |
| `f71fd55` | feat(feat-08): popular avaliacoes de demonstracao | 6 |
| (este) | docs(feat-08): atualizar diagramas, changelog e texto do PR | documentação |

**Mudanças em código e documentos de outras specs** (aprovadas na Q-128, relatadas aqui):

| IC | Arquivo | O que mudou | Motivo |
|---|---|---|---|
| IC-01 | `defesa/services_defesa.py` (007) | `descartar_avaliacoes` delega para `services_avaliacoes`; descarte antes de apagar a linha da banca em `acionar_suplente` e `alterar_banca`; `alterar_banca` mantém o rascunho só na troca entre titulares e atualiza a linha de quem continua; `reagendar` devolve envios a rascunho; `tcc_da_sessao`, `travar_tcc` e `travar_sessao` públicas | Contrato §6 da 007 (Q-125); D16 e Q-135; D2 |
| IC-02 | `cadastro/menu.py` | item "Minhas bancas" | FR-003 |
| IC-03 | `defesa/tests/test_base_defesa.py`, `test_us23_banca.py`, `test_us24_confirmar_reagendar_cancelar.py` (007) | teste do stub trocado pelo da delegação; casos da troca entre titulares, ida a Suplente, cópia apagada e reagendamento | D16, Q-135, D2, D3 |
| IC-04 | `requirements.txt` | `xhtml2pdf` 0.2.28 e dependências (sem pycairo/rlPyCairo) | PGCS 3.7 |
| IC-05 | `defesa/views_defesa.py`, `defesa/sessao.html` (007) | blocos `avaliacao` e `resultado`; `sessao_ou_404` pública | contrato §3 da 007 |
| IC-06 | `defesa/historico.html` (007) | nota final e parecer no evento "Liberação do Resultado" | D15 |
| IC-07 | `cadastro/views_tcc.py`, `cadastro/tcc/meu_tcc.html` (005) | seção "Resultado da defesa" | FR-033 |
| IC-08 | `cadastro/management/commands/popular_demo.py` | avaliações de exemplo; deixa de esvaziar `Criterios` (Q-139) | research A12 |
| IC-09 | `defesa/permissoes_defesa.py`, `urls.py`, `mensagens.py` (007) | acréscimos | revisão M-05 |
| IC-10 | `specs/007-agendamento-banca/spec.md` | emendas FR-011 e FR-019 | D2, D16 |
| IC-11 | `specs/007-agendamento-banca/contracts/servicos-defesa.md` | §6 entregue, ordem do descarte, travas públicas | revisão I-09 |

Documentos: diagrama 28 (geração no download; US-28 E2 mantida com a Q-140), rastreabilidade
diagrama → código, rótulos dos `.drawio` de componentes e implantação e CHANGELOG.

### 2. Rastreabilidade com o Projeto

* **Feature Impactada:** Feature 08 - Avaliação e Resultados
* **Histórias de Usuário Atendidas:** US-25, US-26, US-27 (RBN-DEF-04.1, 04.2, 05.1 a 05.4, 06.1 a 06.8)
* **Cartão no Trello:** Sprint 4 — Avaliação e Resultados

### 3. Checklist Técnico da Equipe (Definition of Done)

- [x] Lint aprovado: `pre-commit run --all-files` (isort, black, flake8) sem ocorrências.
- [x] Não há variáveis, imports ou trechos de código não utilizados (flake8 limpo).
- [x] `makemigrations --check --dry-run`: "No changes detected" (a spec 008 não cria tabela nem coluna).
- [x] Os arquivos `.env` e os diretórios `sigtcc/media/` e `staticfiles/` NÃO foram adicionados ao Git.
- [ ] A interface segue a paleta e os padrões do protótipo de 17/10 (pendente da validação manual, Q-138).
- [ ] Não há quebras de layout nem erros no console do navegador (pendente da validação manual, Q-138).

**Testes automatizados**: suíte inteira com 1437 testes, OK (1 falha esperada já existente, `test_us06_validade.test_cenario_03_texto_da_us06_pendente_da_q52`, Q-52), em 2026-11-03. O teste instável da Q-119 (spec 003) falhou às vezes durante a implementação, fora do escopo desta feature.

**Instalação no Linux limpo** (research A9): pendente (Q-136). O Docker da estação estava parado;
a árvore instalada no Windows não tem pycairo nem rlPyCairo.

### 4. Evidência da Validação Manual (Critérios de Aceite das USs)

Pendente (Q-138): roteiro de 16 passos de [quickstart.md](quickstart.md), a fazer antes do merge.

- [ ] Cenário 1: Consultar os critérios e ver as minhas bancas (US-25 A; DEF-05.4)
- [ ] Cenário 2: Rascunho antes da sessão, envio assinado e reabertura (US-25, US-26)
- [ ] Cenário 3: Registrar o parecer e liberar o resultado, com a sessão Realizada e o Status do TCC (US-27)
- [ ] Cenário 4: Sigilo por perfil antes e depois da liberação e resultado na aba Meu TCC (US-27, DEF-06.8)

**Pendências registradas**: Q-131 (DV-01, PO), Q-132 (textos da matriz e das US-27/US-28, PO),
Q-133 (colunas `*_path`, modelo lógico), Q-134 (PGCS no Drive), Q-136 (Linux limpo), Q-137 (PNG
dos diagramas), Q-138 (validação manual), Q-139 (`Criterios` no banco do Render), Q-140 (US-28 E2
na feat-09).

### 5. Revisão por Pares (Peer Review)

* **Revisor Designado:** [a definir]
* **Parecer do Revisor:**
  - [ ] Aprovado integralmente para merge
  - [ ] Solicitação de ajustes (detalhar nos comentários)
