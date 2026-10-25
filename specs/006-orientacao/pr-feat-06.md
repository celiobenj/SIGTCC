# [Feat-06] Orientação, Atas e Publicações (US-17, US-18, US-19, US-20, US-36, US-41, US-42, US-45, US-46)

**Origem:** `feature/feat-06-orientacao` -> **Destino:** `develop` (merge `--no-ff`, PGCS 6.4)

**Spec:** `specs/006-orientacao/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, `tasks.md`)

**Responsável:** Leandra Matos (R/A do épico no RACI); implementação: Célio Benjamim

### 1. Resumo da Alteração

Implementa o ciclo de orientação do TCC no app `cadastro`, sem tabela nem coluna nova
(`makemigrations --check`: "No changes detected"):

- **Pedido e troca de orientador (US-17, US-18):** o Aluno pede orientação, cancela o pedido ou
  pede a troca; o docente aceita ou recusa na nova tela "Orientações" (menu, sino ou e-mail), com
  aviso de estado no link (cancelado pelo aluno, pelo agendamento, pelo encerramento, pela cópia
  para o TCC 2 ou pelo arquivamento da turma). Notificações no sistema (MO-01 a MO-26) e e-mails
  após o commit.
- **Coorientadores (US-45, US-36):** convite ao docente do NUCOMP, registro de externo
  (reaproveitado pelo e-mail, MO-25), substituir e remover, bloqueados com sessão de defesa ativa;
  aceite ou recusa do convite na tela Orientações.
- **Atas de orientação (US-19):** registro, edição e comentário por Aluno, Orientador e
  Coorientador; consulta pelo Professor da Disciplina no painel; atas do TCC 1 no TCC 2 só para
  consulta.
- **Apto para Defesa e Correções Conferidas (US-42; US-44 B):** indicação pelo Orientador com
  reconferência sob trava (MO-20) e mudança de Status pelo serviço único da spec 005.
- **Painel do aluno (US-41):** a aba "Alunos" da turma vira blocos de consulta; as ações do
  Professor da Disciplina (Editar, Resetar primeiro acesso, Transferir, Encerrar, Excluir,
  Histórico do Status, Homologar e Devolver a Versão Final) ficam no painel e voltam a ele
  (`?volta=painel`). A Secretaria continua com "Transferir aluno" no bloco.
- **Publicação e aproveitamento (US-46, US-20):** seção "Publicação do artigo" (Aluno) e tela do
  Orientador; tela "Aproveitamento de artigos" do Coordenador (seção "Gestão" do menu), com filtro
  Curso, regra da liberação (US-20 E3) e log próprio (`EventoArtigo`).
- **Meu TCC:** seções Orientação, Atas de orientação e Publicação do artigo, abertas pelo link já
  na seção (`?secao=`).
- **Arquivar a turma:** cancela os pedidos e convites pendentes e avisa cada docente (MO-26).

**Itens de configuração em código de specs já mescladas (IC-01 a IC-14, aprovados, Q-103 a Q-116; IC-15, Q-120):**

| IC | Arquivo(s) (spec de origem) | Mudança |
|---|---|---|
| IC-01 | `menu.py` (003) | + "Orientações" (docente) e + "Aproveitamento de artigos" (coordenador, seção "Gestão") |
| IC-02 | `turmas/turma.html`, `views_turmas.turma`, `services_turmas.alunos_da_turma` (004) | Aba "Alunos" em blocos de consulta, sem consulta por linha |
| IC-03 | `views_turmas.py` e os templates editar/encerrar/excluir/transferir (004) | `?volta=painel` (valor fechado); sem o parâmetro, nada muda |
| IC-04 | `services_turmas.py` (004/005) | `agora=None` opcional; a cópia para o TCC 2 trava o TCC 1 e cancela os pendentes dele (MO-18) |
| IC-05 | `services_tcc.pode_ver_resumo` (005) | Aceita Troca de Orientação pendente |
| IC-06 | `views_tcc`, `services_tcc.contexto_historico`, `historico_status.html` (005) | Histórico com botão "Fechar" e `url_voltar` |
| IC-07 | `services_entregas.devolver_versao_final`, `views_entregas`, `homologar_versao_final.html` (005) | A devolução limpa `ent_correcoes_conferidas_em`; volta ao painel |
| IC-08 | `views.aluno`, `aluno.html` removido (003) | A tela provisória vira redirecionamento ao painel; 403 sem turma |
| IC-09 | `meu_tcc.html`, `views_tcc.meu_tcc` (005) | + 3 seções da 006 |
| IC-10 | `urls.py`, `mensagens.py`, `static/css/sigtcc.css` (003) | Só acréscimos (rotas, textos, classes do protótipo) |
| IC-11 | Testes de outras specs | Caminho ajustado em `test_navegacao_tcc.py`, `test_us08_transferencia.py` e `test_us12_senha.py`; testes acrescentados em `test_notificar.py`, `test_us08_matricula.py` e `test_us15_envio_entrega.py`. Nenhum cenário de aceite removido. |
| IC-12 | `services_turmas.arquivar_turma` (004), `services.notificar` (003) | Arquivar cancela os pendentes da turma (MO-26); `notificar(agora=None)` |
| IC-13 | `services.py` (003), `services_entregas._enviar_email_ao_aluno` (005) | + `enviar_email_apos_commit`, compartilhado; comportamento da 005 inalterado |
| IC-14 | `services_entregas.enviar_entrega` (005) | Ordem de trava turma → aluno → TCC → entrega (evita deadlock) |
| IC-15 | `services_turmas._trabalho_movimentado` e `excluir_aluno`, `mensagens.py` (004) | Pedido de orientação ou convite de coorientação não impede mais a exclusão do aluno "Sem Proposta"; os pendentes são cancelados com aviso ao docente (MT-33) e cada solicitação vai para o log de acesso antes de ser apagada com o TCC (decisão de Célio Benjamim depois do teste manual; spec 004, FR-023 e Clarifications Q20; Q-120). Testes: em `test_us09_exclusao.py`, o caso "solicitação" saiu da lista de bloqueios do research B14 (não é cenário de aceite da US) e entraram 4 testes em `ExclusaoComPedidoTest` |

**Documentos fora da spec 006 alterados neste PR:**
- Constituição 1.0.0 → 1.0.1 (PATCH: referência às US v3.2 → v3.3; sem efeito semântico; Q-62). **Requer aprovação neste PR.**
- `CLAUDE.md`, `GUIA_SDD.md` e os agentes `analista-requisitos` e `testador-aceite` passam a citar `Historias_de_Usuario_v3_3.md`; `test_mensagens.py` e `test_mensagens_turmas.py` passam a conferir contra a v3.3.
- `specs/003-acesso-login/spec.md`: M-02 e M-14 alinhadas aos textos das US (Q-50; Clarifications Q30).
- `specs/005-fluxo-do-tcc/contracts/servicos-compartilhados.md`: correção do nome de uma função citada.
- `specs/004-turmas-alunos/spec.md` e `research.md`: FR-023, Clarifications Q20, MT-33 e leitura da RBN-CAD-05.4 no B14 (Q-120; IC-15). **Toca código já mesclado da spec 004.**
- `.claude/launch.json`: configuração `sigtcc` (`runserver` na porta 8000) para a pré-visualização da ferramenta de desenvolvimento, pedida na T060; sem segredo nem caminho pessoal.

### 2. Rastreabilidade com o Projeto

* **Feature Impactada:** Feature 06 – Orientação, Atas e Publicações
* **Histórias de Usuário Atendidas:** US-17, US-18, US-19, US-20, US-36, US-41, US-42, US-45, US-46
* **Cartão no Trello:** [preencher: cartão da Feat-06 no quadro do Sprint]

### 3. Checklist Técnico da Equipe (Definition of Done)

- [x] Lint aprovado: `isort --check-only --profile black --line-length 100`, `black --check --line-length 100` e `flake8 --max-line-length 100` sobre `sigtcc/`, sem ocorrências. O repositório não tem `.pre-commit-config.yaml`; a verificação equivale ao `lint.bat` citado no `.github/PULL_REQUEST_TEMPLATE.md`.
- [x] Não há variáveis, imports ou trechos de código não utilizados (flake8 limpo).
- [x] `makemigrations --check --dry-run`: "No changes detected" (a spec 006 não cria tabela nem coluna); nenhuma migração existente na `develop` foi alterada ou apagada.
- [x] Os arquivos `.env`, `.env.local` e os diretórios `sigtcc/media/` e `staticfiles/` NÃO foram adicionados ao Git (`git ls-files`: só `.env.example`).
- [x] A interface segue a paleta e os padrões de usabilidade da ISO/IEC 25010 e do protótipo de 17/10: as 11 telas foram conferidas em 1280 px e em 360 px (sem rolagem horizontal), registro em `tasks.md`, "Conferência visual".
- [x] Não há quebras de layout nem erros acusados no console do navegador com o sistema rodando (T061, 24/10/2026; conferência visual em 360, 768 e 1280 px sem problema).

**Testes automatizados:** suíte completa em 24/10/2026, depois do commit `6fc0bb6`, com 1115
testes: 1113 passando, 1 falha esperada já marcada como `expectedFailure` e 1 falha intermitente fora
da spec 006, `test_base_comum.BaseComumTest.test_cenario5_link_gerado_fora_das_telas` (spec 003):
os dois links de ativação às vezes recebem o mesmo instante no Windows (resolução de ~15 ms do
relógio), também sem as mudanças da 006; isolado, passou 5 vezes seguidas. Registrado na Q-119.
Inclui os 4 testes novos de `ExclusaoComPedidoTest` (IC-15) e os da janela do coorientador.

### 4. Evidência da Validação Manual (Critérios de Aceite das USs)

Roteiro manual do `quickstart.md` (passos 1 a 23) executado por Célio Benjamim em 24/10/2026,
registro na seção 10 do `quickstart.md` (T061):

- Passos 7 e 13: defeitos encontrados e corrigidos neste PR (só a caixa do Tipo visível na janela
  do coorientador, `dca41d1`; exclusão do aluno "Sem Proposta" com pedido, `9cf47f5`, Q-120).
- Passos 14 e 21: explicados pelas pré-condições que faltavam no roteiro, já acrescentadas (`9a51f52`).
- Passo 18: conferido sem defeito.
- Conferência visual em 360, 768 e 1280 px sem problema; console do navegador sem erros.

Os cenários de aceite também estão cobertos por testes automatizados (um ou mais por cenário
Dado/Quando/Então), e `test_navegacao_orientacao.py` percorre cada tela a partir do menu.

- [x] Cenário 1: Aluno pede orientador; o docente aceita em "Orientações" e o aluno é notificado (US-17, US-18)
- [x] Cenário 2: Pedido de troca de orientador e resposta do docente (US-17, US-18)
- [x] Cenário 3: Registro, convite, aceite, substituição e remoção de coorientador (US-45, US-36)
- [x] Cenário 4: Registro, edição e comentário de ata; consulta pelo Professor da Disciplina (US-19)
- [x] Cenário 5: Apto para Defesa e Correções Conferidas (US-42; US-44 B)
- [x] Cenário 6: Aba "Alunos" em blocos, painel do aluno e volta das telas de ação ao painel (US-41)
- [x] Cenário 7: Publicação e decisão de aproveitamento pelo Coordenador (US-46, US-20)
- [x] Cenário 8: Arquivar a turma cancela os pedidos e convites pendentes e avisa os docentes (Q-117)

**Pendências registradas em `docs/questoes-a-rever.md` (não bloqueiam o merge):**
- Q-95: os 26 textos provisórios MO-01 a MO-26.
- Q-97 a Q-99: divergências US × matriz decididas pela equipe (Secretaria na lista, "Editar" no painel, aviso na recusa).
- Q-101: decisões D1 a D14 da revisão da spec 006.
- Q-102: lacunas do modelo aceitas sem coluna nova; Q-91: ajuste do dicionário 3.5.1 (linha nova do TCC 2) com Maria Luiza Guimarães.
- Q-81: nome do link de histórico ("Histórico" ou "Histórico do Status do TCC"), provisório desde a spec 005.
- Q-117: regra nova de cancelamento dos pendentes ao arquivar a turma (ciência da PO).
- Q-118: textos de estado vazio vindos do protótipo.
- Q-119: teste instável da spec 003.
- Q-120: exclusão do aluno "Sem Proposta" com pedido (respondida por Célio Benjamim; IC-15; a MT-33 é provisória e entra na validação da Q-36).
- Q-96: ciência das responsáveis pelas specs 003/004 (Julia Cohen) e 005 (Leandra Matos) sobre os IC-01 a IC-15.

### 5. Revisão por Pares (Peer Review)

* **Revisores:** [revisores] (não pode ser quem escreveu o código)
* **Parecer do Revisor:**

[ ] Aprovado integralmente para merge

[ ] Solicitação de ajustes (detalhar nos comentários)
