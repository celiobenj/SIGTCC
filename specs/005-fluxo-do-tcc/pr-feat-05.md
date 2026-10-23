# [Feat-05] Fluxo do TCC e Entregas (US-13, US-14, US-15, US-16, US-29, US-43, US-44)

**Origem**: `feature/feat-05-fluxo-do-tcc` → **Destino**: `develop` (merge `--no-ff`, PGCS 6.4)

**Spec**: `specs/005-fluxo-do-tcc/` (spec.md, plan.md, research.md, data-model.md, contracts/rotas.md, contracts/servicos-compartilhados.md, quickstart.md, tasks.md)

**Responsável**: Leandra Matos (US-13 a 16, 29, 43 e 44). Implementação: Julia Cohen (Phases 1 a 5 e parte da 6) e Célio Benjamim (Phases 6 a 13).

> **Base**: a feat-03 (spec 004) e a feat-04 (spec 002) já estão na `develop`, trazida para esta branch por merge em `206e154` (PGCS 4.3.A e 6.2). Os 3 conflitos de texto (`sigtcc/apps/cadastro/urls.py`, `sigtcc/apps/cadastro/mensagens.py` e `docs/questoes-a-rever.md`) foram resolvidos mantendo os blocos das duas features; o índice de questões ficou sem IDs repetidos (93 questões). O diff do PR traz só a feat-05.

### 1. Resumo da Alteração

Implementa o ciclo de vida do TCC e das entregas no app `cadastro`, sobre o modelo de dados da feat-01, **sem criar tabelas, colunas nem migrações** (`makemigrations --check --dry-run` → "No changes detected").

- **Proposta e dados do TCC (US-13)**: aba Meu TCC com Título, Subtítulo, Resumo (com contador de caracteres restantes), Modalidade e Link; "Salvar Proposta" muda o Status para "Em Andamento" e cumpre a entrega do tipo Proposta ("Entregue" ou "Entregue com Atraso"). Depois, Área de Interesse e de 1 a 5 Palavras-Chave, sem repetir (MF-03). Mudança de tema enquanto "Em Andamento" — qualquer campo, inclusive Área e Palavras-Chave — com aviso ao Orientador (MF-04). O serviço trava turma → aluno → TCC e confere de novo o Status; turma arquivada no meio do salvamento mostra a MT-25. Resumo visível só a quem `pode_ver_resumo` autoriza (FR-007a).
- **Status, histórico e trilha (US-14)**: serviço único de gravação do Status (FR-012) em `services_turmas.py`: `criar_tcc_com_historico` (gatilhos de criação) e `atualizar_status_tcc` (gatilhos de transição), validados contra a tabela fixa `TRANSICOES_VALIDAS`. Os três pontos da spec 004 (`matricular`, `_copiar_tcc_aprovado`, `encerrar_participacao`) passaram a usá-las, sem mudar comportamento (Q-82). Histórico cronológico e trilha com a etapa atual destacada, para o Aluno e para o Professor da Disciplina (link na lista de alunos da turma); Secretaria e Coorientador não veem (Clarifications).
- **Cadastro de entregas (US-43)**: aba Atividades do Professor, com Tipo restrito por etapa, Data Limite não anterior a hoje (MF-06) e um tipo por turma, exceto "Outra". Cria o registro "Aguardando Envio" de cada aluno já matriculado e o avisa no sistema (MF-05, com link para a aba Atividades) e por e-mail (MF-11).
- **Envio de link (US-15)**: envio e substituição até a Data Limite, status pelo primeiro envio, envio depois do prazo aceito como "Entregue com Atraso" (com o TCC "Em Andamento", RBN-CAD-09.2), aviso ao Professor a cada envio (MF-07). Regra única `envio_liberado`, conferida de novo no serviço com trava em `Entregas_Marcos` e `TCCs`. O campo Link vem com o link mais recente, pronto para substituir. Comando agendado `enviar_lembretes_entrega`: grava "Não Entregue" nas entregas vencidas sem envio (FR-020) e envia os lembretes 7 dias, 48h e 24h antes (MF-08, no sistema e por e-mail, MF-12), sem repetir e sem alcançar participação encerrada.
- **Acompanhamento (US-16)**: tabela por aluno com status de envio e link mais recente; no tipo Proposta, "Ver Proposta" somente leitura. Só o Professor da Disciplina, também com a turma arquivada (consulta).
- **Versão Final (US-29)**: seção "Versão final" na aba Meu TCC (turma de TCC 2), liberada só com o parecer Aprovado ou Aprovado com Correções; aviso MF-01 depois da Data Limite; reenvio após devolução; "Disponível após a liberação do resultado" antes do parecer; somente leitura depois de homologada. Seção Defesa com o parecer (lido do histórico) e os botões Ata Final e Folha de Aprovação desabilitados até a spec 006 (Q-87).
- **Homologação ou devolução (US-44)**: tela da Versão Final do aluno para o Professor da Disciplina. Homologar muda o status para "Homologada", conclui o TCC (gatilho "Homologação da Versão Final") e notifica a Secretaria do curso (MF-09). Devolver para Ajuste exige Mensagem de até 500 caracteres e notifica o Aluno (MF-10). Em Sistemas de Informação com "Aprovado com Correções", Homologar só depois de "Correções Conferidas" (campo gravado pela spec 006). Autor, data e hora das duas ações no log de acesso (dicionário 18/10, seção 4, item 5).
- **Navegação (FR-031; Q-89)**: item de menu "Turmas" próprio do Aluno (turmas ativas e arquivadas em que está matriculado), abas "Meu TCC" | "Atividades" do Aluno e "Alunos" | "Atividades" do Professor; a tela da turma da spec 004 continua fechada ao Aluno (FR-010 da spec 004) e só recebeu acréscimos (barra de abas e link de histórico).
- **Serviços para a spec 006** (`contracts/servicos-compartilhados.md`): `atualizar_status_tcc`, `historico_do_status`, `pode_ver_resumo`, `link_mais_recente` e o campo `ent_correcoes_conferidas_em`.

### 2. Rastreabilidade com o Projeto

* **Feature Impactada:** Feature 05 - Fluxo do TCC e Entregas (spec 005)
* **Histórias de Usuário Atendidas:** US-13 [RBN-CAD-07.1][RBN-CAD-08.1][RBN-CAD-08.2], US-14 [RBN-CAD-08.3][RBN-CAD-08.7][RBN-CAD-08.8], US-43 [RBN-CAD-09.1][RBN-CAD-09.6], US-15 [RBN-CAD-09.2][RBN-CAD-09.3][RBN-CAD-09.6], US-16 [RBN-CAD-09.4], US-29 [RBN-CAD-09.2][RBN-CAD-09.3], US-44 [RBN-CAD-09.3][RBN-CAD-09.5]. Cada classe, função, template e teste cita as US, RBN ou FR que atende.
* **Requisitos da spec 005:** FR-001 a FR-031 e FR-007a; SC-001 a SC-006 (SC-001 e SC-003 também pelo roteiro manual, ver seção 4); 99 cenários de aceite.
* **Cartão no Trello:** [preencher]

**Commits deste PR** (só os da feat-05)

| Commit | Mensagem |
|---|---|
| afc027c | docs(feat-05): especificar fluxo do tcc e entregas |
| f124630 | docs(feat-05): planejar fluxo do tcc e entregas |
| 86e4672 | feat(feat-05): criar esqueleto dos modulos do fluxo do tcc |
| 01df45c | feat(feat-05): acrescentar atualizar_status_tcc e historico_do_status |
| 4d36874 | feat(feat-05): aceitar campos extras na criacao do tcc 2 |
| 962a10a | feat(feat-05): implementar proposta e dados do TCC (US-13) |
| cc2fa20 | feat(feat-05): implementar historico e trilha do status do tcc (US-14) |
| 8775851 | feat(feat-05): cadastrar entregas da turma pelo professor (US-43) |
| 692301e | feat(feat-05): implementar parte do envio de entregas |
| 50f1ad5 | feat(feat-05): concluir envio de entregas e lembretes de prazo (US-15) |
| 8f0da6a | feat(feat-05): acompanhar entregas dos alunos da turma (US-16) |
| 53ea94b | feat(feat-05): enviar a versao final do tcc 2 (US-29) |
| 6d3bd68 | feat(feat-05): homologar ou devolver a versao final (US-44) |
| b2b94d6 | test(feat-05): conferir mensagens exatas e permissoes do fluxo do tcc |
| c880bc0 | docs(feat-05): renumerar questoes da spec 005 para Q-80 a Q-91 |
| 8c603ff | docs(feat-05): especificar navegacao do aluno e do professor (Q-89) |
| 7c11e8b | docs(feat-05): corrigir contagens e rastreio da navegacao apos analise |
| 8979b1f | feat(feat-05): navegar pelas turmas do aluno e abas da turma (Q-89) |
| 43417a8 | test(feat-05): cobrir permissoes das listas do aluno e roteiro (T041) |
| bae7f39 | docs(feat-05): registrar correcoes da revisao na spec e nas tarefas |
| e847caf | fix(feat-05): avisar orientador por area e palavras e reconferir tcc |
| ec28eba | feat(feat-05): gravar nao entregue e enviar e-mail das entregas |
| ac04edb | feat(feat-05): registrar autor da homologacao e da devolucao no log |
| 0c5a3c6 | docs(feat-05): registrar validacao manual e achados do roteiro |
| 030dc98 | fix(feat-05): mostrar link do historico e preencher o campo link |
| df1cc38 | docs(feat-05): preencher texto e checklist do pr |
| 206e154 | chore(feat-05): trazer a develop com a gestao de contas (feat-04) |
| (este) | docs(feat-05): registrar reteste e merge no texto do pr |

### 3. Checklist Técnico da Equipe (Definition of Done)

- [x] O código foi verificado com isort, black e flake8 (equivalente do `lint.bat`; nem esta branch nem a `develop` têm `pre-commit` configurado): `isort --check-only sigtcc/`, `black --check sigtcc/` e `flake8 sigtcc/` sem apontamentos (2026-10-23).
- [x] Não há variáveis, imports ou trechos de código não utilizados (flake8 limpo).
- [x] Migrações: nenhuma nesta feature (nenhum arquivo em `migrations/` no diff); `makemigrations --check --dry-run` → "No changes detected"; nenhuma migração antiga alterada. Depois do merge da `develop` (que traz a `0006` da spec 002), também "No changes detected" (merge simulado).
- [x] O arquivo `.env` e as pastas `sigtcc/media/` e `staticfiles/` NÃO foram adicionados ao Git (`git ls-files`). A feature não grava arquivos: entregas são só links `https://`.
- [x] A interface segue a paleta e os padrões do protótipo de 17/10 (ISO/IEC 25010): conferida no roteiro manual (Célio Benjamim, 2026-10-23, "itens de UI/UX ok").
- [x] Não há quebras de layout ou erros no console do navegador (reteste, Célio Benjamim, 2026-10-23).

### 4. Evidência da Validação Manual (Critérios de Aceite das USs)

Suíte completa (2026-10-23): `python manage.py test sigtcc.apps` → **652 testes, 650 OK**. Os que podem falhar são anteriores e de fora desta feature: `test_mensagens.test_textos_das_us` e `test_mensagens_turmas.test_textos_das_us` (specs 003/004: procuram `Historias_de_Usuario_v3_2.md`; índice Q-77 da develop) e `test_base_comum.test_cenario5_link_gerado_fora_das_telas` (spec 003: passa ou falha conforme o relógio ao gerar dois links seguidos). Depois do merge da `develop`, somam-se as falhas M-02 e M-14 do `test_mensagens` que já existem na `develop` (tabela da spec 003 não atualizada pela Q-50).

**Validação manual (T035, Célio Benjamim, 2026-10-23)** — banco de desenvolvimento recriado e preparado para o roteiro (backup do anterior em `logs/`, fora do Git):
- [x] a–d: Proposta, Palavra-Chave repetida (MF-03), "Alterações salvas", histórico e trilha do Aluno
- [x] e–g: cadastro de entrega, tipo repetido e envio no prazo
- [x] h–i: na primeira rodada, o segundo aluno estava "Sem Proposta", e o envio de "Documento para Defesa" só fica disponível com o TCC "Em Andamento" (RBN-CAD-09.2; US-15, E4) — regra correta; o passo h do `quickstart.md` foi corrigido para salvar a Proposta antes. **Reteste OK**: envio depois do prazo como "Entregue com Atraso" e acompanhamento do Professor
- [x] j–k: Versão Final cadastrada e enviada (TCC 2)
- [x] l: homologação, TCC "Concluído", Secretaria notificada
- [x] m: devolução para ajuste com a MF-02
- [x] n: acesso sem login
- [x] o e histórico pelo Professor: **reteste OK**. Faltava o link para o histórico de um aluno (a tela do aluno, US-41, é da spec 006); acrescentado na lista de alunos da turma (FR-031; cenário 12 da US2). A consulta pelo Orientador é da tela de orientandos da spec 006
- [x] Campo Link preenchido com o link já enviado (cenário 10 da US4): **reteste OK** (melhoria pedida na validação)
- [x] UI/UX conferida
- [x] Demais passos do roteiro retestados sem divergência (Célio Benjamim, 2026-10-23)

**Testes automatizados por US**
- [x] **US-13 – Proposta** (`test_us13_proposta.py`, 26): cenários 1 a 9, exceções, aviso ao Orientador por Área e Palavras-Chave, reconferência do Status, turma arquivada no salvamento e contador do Resumo
- [x] **US-14 – Status, histórico e trilha** (`test_us14_status_historico.py`, 39; `test_base_turmas.py`, 21): cenários 1 a 12, `TRANSICOES_VALIDAS`, `pode_ver_resumo` nas 5 categorias, trilhas de TCC 1, TCC 2 e encerrada
- [x] **US-43 – Cadastro de entregas** (`test_us43_cadastro_entregas.py`, 24): cenários de aceite, tipo repetido, alunos já matriculados (Q-41), e-mail da nova entrega, turma arquivada e permissão
- [x] **US-15 – Envio de link** (`test_us15_envio_entrega.py`, 49): cenários 1 a 13, campo Link preenchido, rotina "Não Entregue", lembretes (janelas, não repetição, exclusões, e-mail) e dois testes de concorrência
- [x] **US-16 – Acompanhamento** (`test_us16_acompanhamento.py`, 15): cenários 1 a 8
- [x] **US-29 – Versão Final** (`test_us29_versao_final.py`, 23): cenários 1 a 13, reenvio após devolução e campo Link preenchido
- [x] **US-44 – Homologação** (`test_us44_homologacao.py`, 22): cenários 1 a 10, Sistemas de Informação, autor no log, turma arquivada (MT-25) e turma de TCC 1
- [x] **SC-004** (`test_permissoes_tcc.py`, 9): as 11 rotas, perfil por perfil; **FR-031** (`test_navegacao_tcc.py`, 14): menu, listas e abas por perfil, histórico pelo Professor
- [x] **SC-006** (`test_mensagens_tcc.py`, 4): textos das US na v3.3 e MF-01 a MF-12 contra a tabela da spec

### Decisões e desvios registrados

| Decisão | Registro | Situação |
|---|---|---|
| Serviço único do Status em `services_turmas.py` (spec 004, já mesclada), com `**campos_tcc` na criação do TCC 2 | research C2; T006; índice Q-82 | Aguarda aprovação de Leandra Matos e Célio Benjamim |
| Questões da spec 005 renumeradas de Q-44–Q-55 para Q-80–Q-91 (colidiam com as da spec 002) | `docs/questoes-a-rever.md`, cabeçalho | Feito (Célio Benjamim, 2026-10-23) |
| Navegação do Aluno por item "Turmas" próprio, sem abrir a tela da turma da spec 004 (alternativa B) | spec, Clarifications 2026-10-23; FR-031; Q-89 | Respondida (Célio Benjamim) |
| "Não Entregue" gravado pela rotina agendada (e calculado na tela enquanto ela não roda) | FR-020; Q-90 | Respondida (Célio Benjamim) |
| E-mail na nova entrega e no lembrete, com assuntos provisórios MF-11 e MF-12 | FR-015, FR-022; Q-84, Q-86 | Decidido; textos a validar com a PO |
| Autor da homologação e da devolução no log de acesso (como `TURMA_EXCLUIDA` da spec 004) | dicionário 18/10, seção 4, item 5; T046 | Decidido |
| Reenvio após devolução: status pela data do próprio reenvio, aceito também depois da Data Limite | FR-019, FR-025; T027 | Decidido na implementação |
| "Sistemas de Informação" na homologação = turma de TCC 2 sem orientador automático | FR-029; T030 | Decidido na implementação |
| Mensagem vazia na devolução usa `JUSTIFICATIVA_500` ("Informe uma justificativa…") | T030 (tasks aprovado) | Validar com a PO junto da Q-88 |
| Botões Ata Final e Folha de Aprovação desabilitados e sem nota final | T028; Q-87 | Até a spec 006 |
| Transferência para TCC 2 cria uma linha nova em `TCCs`; o dicionário 3.5.1 diz que a mesma linha passa a referenciar a nova turma | spec 004 (já mesclada); Q-91 | A confirmar com Maria Luiza Guimarães (anterior a esta feature) |

### Itens de configuração para revisão do Célio Benjamim (constituição, princípio IX)

- [ ] Alteração de `services_turmas.py` (spec 004): `TRANSICOES_VALIDAS`, `criar_tcc_com_historico`, `atualizar_status_tcc` (Q-82)
- [ ] Acréscimos em arquivos da spec 004: item "Turmas" do Aluno em `menu.py` e, em `templates/cadastro/turmas/turma.html`, a barra de abas e o link "Histórico do Status do TCC" (Q-89)
- [ ] Módulos novos: `services_tcc.py`, `services_entregas.py`, `forms_tcc.py`, `forms_entregas.py`, `views_tcc.py`, `views_entregas.py`, a subpasta `templates/cadastro/tcc/`, o template de e-mail `aviso_entrega.txt` e o script `static/js/contador.js` (exceção ao princípio IV, como na spec 004)
- [ ] Comando `enviar_lembretes_entrega`: agendar a execução **a cada hora** no servidor (grava "Não Entregue" e envia os lembretes; Q-86, Q-90)
- [ ] Eventos novos no log de acesso: `VERSAO_FINAL_HOMOLOGADA` e `VERSAO_FINAL_DEVOLVIDA` (enum próprio em `services_entregas.py`)

### Pendências

| Pendência | Destino | Índice |
|---|---|---|
| Nome da aba ("Atividades" ou "Entregas") | Profa. Diana ou Leandra Matos | Q-80 |
| Nome do link "Histórico do Status do TCC" | Profa. Diana ou Leandra Matos | Q-81 |
| Validar MF-01 a MF-12 | Profa. Diana (PO) | Q-83 a Q-88 |
| Botão Enviar desabilitado (US-15) × oculto (spec) para o aluno Jubilado | Leandra Matos | Q-92 |
| Entrega do tipo Proposta cadastrada depois da Proposta salva | Leandra Matos ou Profa. Diana | Q-93 |
| Transferência com linha nova em `TCCs` × dicionário | Maria Luiza Guimarães | Q-91 |
| Testes de mensagens das specs 003/004 apontando para a v3.2 das US (e M-02/M-14 na `develop`) | responsáveis pelas specs 003/004 | T034; Q-77 da develop |
| 6 commits da feature com a linha "Co-Authored-By: Claude" (já no GitHub; tirar exigiria reescrever o histórico) | Julia Cohen / Célio Benjamim | — |

### 5. Revisão por Pares (Peer Review)

* **Revisores Designados:** Leandra Matos (dona das US; código e regras) e Célio Benjamim (itens de configuração, Q-82 e Q-89)
* **Parecer do Revisor:**

[ ] Aprovado integralmente para merge

[ ] Solicitação de ajustes (detalhar nos comentários)
