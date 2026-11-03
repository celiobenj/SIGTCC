# [Feat-07] Agendamento e Banca (US-21, US-22, US-23, US-24, US-40)

**Origem:** `feature/feat-07-agendamento` -> **Destino:** `develop` (merge `--no-ff`, PGCS 6.4)

**Spec:** `specs/007-agendamento-banca/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, `tasks.md`)

**Responsável:** Célio Benjamim (R do épico no RACI; Leandra Matos, A); spec e implementação: Julia Cohen. Responsáveis pelas US de origem: Célio Benjamim (US-21 a 24 e 40) e Maria Luísa Gomes (US-39, mecanismo do filtro de Curso)

### 1. Resumo da Alteração

Implementa o agendamento da defesa e a banca no app `defesa`, sem tabela nem coluna nova
(`makemigrations --check`: "No changes detected"):

- **Agendar a defesa (US-21):** formulário "Agendar sessão de defesa" (TCC só entre os Aptos, sem
  sessão ativa e sob a responsabilidade do usuário pelo curso: Orientador em Eng. Comp., Professor
  da Disciplina em SI e LC), com Local ou Link da Videochamada e a reserva de 1 hora; tela
  "Defesas", aba "Defesas" da turma e link "Agendar defesa" na tela de orientandos.
- **Banca (US-23):** Presidente fixo (orientador atual), listas só com docentes 'Ativa' e Membros
  Externos, sem a orientação e sem quem já foi escolhido, cadastro rápido do Membro Externo
  (atalho do contrato §3 da spec 002), "Alterar banca" e "Acionar suplente", com justificativa e
  evento no histórico.
- **Conflito de horário (US-22):** rejeita, numa única mensagem com o nome e o papel de cada
  membro, qualquer sobreposição na janela de 1 hora; trava os docentes propostos antes da
  consulta (duas sessões novas para o mesmo docente: só uma é gravada).
- **Confirmar, reagendar, cancelar e início automático (US-24):** avisos ao Aluno e a toda a banca
  com o link do Documento para Defesa, cancelamento da troca de orientador pendente, reagendamento
  (também com a sessão Em Andamento) e cancelamento (o TCC continua Apto); o status passa a "Em
  Andamento" ao chegar o horário, ao abrir as telas ou pelo comando `iniciar_sessoes`.
- **Lista, filtros e histórico (US-40, US-39):** visibilidade por perfil somada por OR, filtros de
  período (atalhos e intervalo), Status e Curso (Coordenador e Secretaria), janela "Sessão de
  defesa" e "Histórico da defesa" com os eventos de todas as sessões do TCC.
- **Contratos para a feat-08 e a feat-09** (`contracts/servicos-defesa.md`): `agendar_sessao`,
  `transicionar_status`, `registrar_evento`, `membros_efetivos`, `historico_da_sessao`, filtro de
  período (`filtro_de_periodo`, `FiltroPeriodoForm`), `sessao.html` com os blocos reservados e o
  stub `services_defesa.descartar_avaliacoes` (no lugar de `services_avaliacoes.descartar_avaliacoes`
  até a feat-08; contrato §6).
- **Contrato da spec 002 ligado (Q-67):** `travar_e_conferir_ativo` ao incluir alguém na banca e
  `recalcular_validade` dos Membros Externos nos eventos de banca (US-06).
- **`popular_demo`:** cenário completo do roteiro da T056 (contas, docentes extras para as bancas,
  TCCs Aptos sem sessão, sessões em cada status, suplentes) e a tabela do roteiro no fim.

**Decisões tomadas na implementação** (spec, Clarifications da sessão 2026-10-31, Julia Cohen):
permissões de alterar banca, reagendar e cancelar pela matriz (perfil que agenda pelo curso;
Secretaria do curso em reagendar e cancelar); janela da sessão para banca (inclusive o Suplente),
Professor da Disciplina, Secretaria do curso e Aluno do próprio TCC; histórico com todas as
sessões do TCC; período letivo atual pelas turmas ativas.

**Itens de configuração em código de specs já mescladas (IC-01 a IC-06, índice Q-123, aprovação de Célio Benjamim):**

| IC | Arquivo(s) (spec de origem) | Mudança |
|---|---|---|
| IC-01 | `sigtcc/urls.py` (003) | + `include("sigtcc.apps.defesa.urls")` |
| IC-02 | `cadastro/menu.py` (003) | + item "Defesas" (aluno, docente, secretaria e membro externo) |
| IC-03 | `cadastro/tcc/_abas_professor.html` (005) | + aba "Defesas" para o Professor da Disciplina |
| IC-04 | `orientacao/orientacoes.html`, `views_orientacao.py` (006) | + link "Agendar defesa" na linha do orientando que o docente pode agendar |
| IC-05 | `popular_demo.py` (005/006) | + docentes extras, TCCs Aptos sem sessão, sessões em cada status pelos serviços e o roteiro da T056 |
| IC-06 | `cadastro/views.py` (003) | + mensagens próprias de 403 da US-21 E7 e da US-40 E5 em `MENSAGENS_403` |

Todos os IC são só acréscimo: nenhum muda o comportamento de outra feature, e os testes das specs
de origem continuam passando. `services_turmas.encerrar_participacao` (spec 004) não foi alterado:
o MT30 continua recusando o encerramento com sessão ativa.

### 2. Rastreabilidade com o Projeto

* **Feature Impactada:** Feature 07 – Agendamento e Banca
* **Histórias de Usuário Atendidas:** US-21, US-22, US-23, US-24, US-40 (e a aplicação da US-39 à tela Defesas)
* **Cartão no Trello:** 4.4 Interface e documentos do módulo de Defesa

### 3. Checklist Técnico da Equipe (Definition of Done)

- [x] Lint aprovado: `pre-commit run --all-files` (isort, black `--line-length 100`, flake8 `--max-line-length 100`) sem ocorrências.
- [x] Não há variáveis, imports ou trechos de código não utilizados (flake8 limpo).
- [x] `makemigrations --check --dry-run`: "No changes detected" (a spec 007 não cria tabela nem coluna); nenhuma migração existente na `develop` foi alterada ou apagada.
- [x] Os arquivos `.env`, `.env.local` e os diretórios `sigtcc/media/` e `staticfiles/` NÃO foram adicionados ao Git (`git ls-files`: só `.env.example`).
- [x] A interface segue a paleta e os padrões do protótipo de 17/10: telas conferidas em 360, 768 e 1280 px, sem problema (T056).
- [x] Não há quebras de layout nem erros acusados no console do navegador com o sistema rodando (T056, 31/10/2026).

**Testes automatizados:** suíte completa em 31/10/2026, no commit `1440564`
(`manage.py test --noinput --parallel 4`): 1308 testes, todos passando, mais 1 falha esperada já
marcada como `expectedFailure` (anterior a esta spec). Rodar com `--noinput`, sem `--keepdb`: com
`--keepdb`, a segunda rodada seguida perde as cargas das migrações no banco de teste depois dos
`TransactionTestCase`; o problema já existia antes desta spec (reproduzido no commit `88fe62a`).

### 4. Evidência da Validação Manual (Critérios de Aceite das USs)

Roteiro manual do `quickstart.md` (seção 2, passos a a n) executado por Julia Cohen em
31/10/2026, sobre o cenário do `popular_demo --local`: **sem defeito**. Conferência visual em 360,
768 e 1280 px sem problema (inclui o JavaScript da troca de formato e da seção Banca,
`alternar_formato.js` e `banca.js`) e console do navegador sem erros. Registro na seção 5 do
`quickstart.md` (T056).

Os cenários de aceite também estão cobertos por testes automatizados (um ou mais por cenário
Dado/Quando/Então): `test_us21_agendar.py`, `test_us23_banca.py`, `test_us22_conflito.py` (com a
corrida de duas sessões novas), `test_us24_confirmar_reagendar_cancelar.py`,
`test_us40_lista_filtros_historico.py`, `test_permissoes_defesa.py` (cada perfil contra cada rota
pelo endereço direto), `test_mensagens_defesa.py` e `test_base_defesa.py` (contratos e cenário do
`popular_demo`).

- [x] Cenário 1: Agendar a defesa presencial ou remota, pelo perfil do curso (US-21)
- [x] Cenário 2: Compor a banca, alterar antes da sessão e acionar o suplente durante (US-23)
- [x] Cenário 3: Rejeitar o agendamento, o reagendamento ou a alteração com conflito de horário (US-22)
- [x] Cenário 4: Confirmar com avisos, cancelar a troca pendente, reagendar, cancelar e iniciar automaticamente (US-24)
- [x] Cenário 5: Lista por perfil com filtros de período, Status e Curso, e Histórico da defesa (US-40, US-39)

Fora do escopo de teste desta spec (Edge Cases): o histórico aberto pela tela do aluno ou de
orientandos (US-40 B) e a transição para "Realizada" (US-24 E, feat-08).

**Pendências registradas em `docs/questoes-a-rever.md` (não bloqueiam o merge):**
- Q-123: aprovação dos IC-01 a IC-06 (Célio Benjamim, configuração).
- Q-124: os 13 textos provisórios MD-01 a MD-13 (Profa. Diana).
- Q-79: agendar no servidor o comando `iniciar_sessoes` (Célio Benjamim).
- Q-67: contrato da spec 002 com a Defesa; esta spec liga o recálculo da validade do Membro
  Externo, a trava e conferência da conta ao incluir na banca, o atalho de cadastro e as listas só
  com contas 'Ativa'; continua aberto o item 4 (rotina diária de expiração no servidor).
- Q-125: `services_defesa.descartar_avaliacoes` é stub (só log) até a feat-08 entregar
  `services_avaliacoes.descartar_avaliacoes` real (contrato §6; Célio Benjamim).
- Q-126: confirmar o nome e o ícone do item de menu "Defesas" (IC-02).

**Aviso ao revisor:** dois títulos de commit ficaram sem verbo no imperativo (`4958d6b` "tela de
agendamento da defesa (US-21)" e `31a228a` "cenarios de conflito de horario da banca (US-22)");
já estão no `origin`, e corrigi-los exigiria reescrever o histórico.

### 5. Revisão por Pares (Peer Review)

* **Revisor Designado:** Célio Benjamim (consome os contratos da feature na feat-08 e na feat-09)
* **Parecer do Revisor:**

[ ] Aprovado integralmente para merge

[ ] Solicitação de ajustes (detalhar nos comentários)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
