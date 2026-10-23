# [Feat-04] Gestão de Contas (US-03, US-04, US-05, US-06, US-50)

**Origem**: `feature/feat-04-gestao-de-contas` → **Destino**: `develop` (merge `--no-ff`, PGCS 6.4)

**Spec**: `specs/002-gestao-contas/` (spec.md, plan.md, research.md, data-model.md, contracts/rotas.md, contracts/servicos-compartilhados.md, quickstart.md, tasks.md)

**Responsável**: Maria Luiza Guimarães (US-03 a US-06 escritas por Maria Luísa Gomes)

> **Base**: a feat-03 já está na `develop`. O diff traz só os commits da feat-04 (`git log origin/develop..HEAD`).

### 1. Resumo da Alteração

Implementa a Gestão de Contas no app `cadastro`, sobre o modelo da feat-01 e a base da feat-02. **Nenhuma tabela nova.** Uma coluna nova, `MembrosExternos.mem_prorrogado_ate DATE NULL`, aprovada pela autora do dicionário (índice Q-69). O dicionário em `docs/fonte/` foi atualizado no mesmo commit da migração `0006`, e `makemigrations --check` responde "No changes detected".

- **Docentes e Secretaria (US-03)**:
  - Cadastro, alteração e listagem de docentes, com filtro de Curso e orientandos por TCC 1 e TCC 2 (alerta acima de 5).
  - Papel de Coordenador: um por curso; o Curso Coordenado pode ser qualquer curso sem Coordenador (Q5); docente 'Inativa' não recebe o papel (MC-10, Q32).
  - Uma Secretaria não inativa por curso (Q7).
  - Ações restritas ao curso do usuário (RBN-CAD-14.1). O docente pertence ao seu Curso de Lotação (Q26).
  - Contas criadas como 'Aguardando Ativação', sem envio de e-mail (Q1).
- **Inativar e reativar (US-04)**:
  - Cinco vínculos impedem a inativação: TCC ativo, convite de coorientação, banca em aberto, turma não arquivada e papel de Coordenador. O alerta lista todos os motivos (Q14, Q18). A verificação é repetida na confirmação, com a conta travada.
  - Reativação do docente.
  - Inativação da Secretaria, sem reativação (Q27).
- **Membros externos (US-05)**:
  - Cadastro com validade de 30 dias (Q12) e alteração.
  - Lista sem filtro de Curso (Q19). O Professor da Disciplina só com turmas arquivadas consulta, mas não altera (Q10).
  - Atalho da banca: `?voltar=` aceita só caminho interno que existe e volta com `membro=<id>`.
- **Troca de e-mail pelo gestor (US-03 A11, US-05 A3)**:
  - Pede "Sua senha" (MC-11; sem limite de tentativas, com log, Q35).
  - Envia link ao novo e-mail (MC-12), e o e-mail só muda depois da confirmação (Q17). Falha no envio grava os demais campos (MC-13, Q24).
  - A confirmação invalida os links antigos de ativação e de redefinição (Q31).
  - O e-mail de Membro Externo 'Ativa' ou 'Expirada' só é trocado pela Secretaria e pelo Coordenador (Q30).
- **Validade e expiração (US-06)**:
  - `recalcular_validade(usuario, hoje=None)` para a Defesa chamar. A regra usa a defesa mais distante + 7, cancelamento ou retirada + 7 (Q13) e o membro substituído pelo suplente (Q33), e protege a prorrogação (Q36). Roda num savepoint e é idempotente.
  - Comando `expirar_membros_externos` (agendar 1 vez por dia) e gravação de 'Expirada' no login.
- **Prorrogação (US-50)**:
  - O botão aparece para o Orientador da banca (sessão não Cancelada), o Professor com turma ativa, a Secretaria e o Coordenador (Q10, Q11).
  - Soma 7 dias à validade ou grava hoje + 7, e guarda a data em `mem_prorrogado_ate`.
- **Coordenadores iniciais (RNF de Instalabilidade do RAN-CAD-01)**: comando `criar_coordenadores`, que lê um CSV fora do repositório e não mostra e-mails na saída.
- **Integridade**:
  - Ordem única de travas: conta → especialização → curso → e-mail, com releitura depois de travar.
  - Trava consultiva por e-mail (unicidade sem diferenciar maiúsculas), gravação só dos campos editáveis (`update_fields`) e expiração conta a conta.
- **Mudanças no código da spec 003** (acréscimos do contrato, ciência da Julia pendente na Q-71):
  - `pedir_troca_email(..., autor=None)`, `travar_email`, `AUTOR_SISTEMA` e `expirar_se_vencida`;
  - eventos novos no log;
  - gravação de 'Expirada' no login e invalidação de links em `confirmar_troca_email`;
  - M-02 e M-14 com os textos das US (Q-50).

  Os testes da spec 003 continuam verdes.

### 2. Rastreabilidade com o Projeto

* **Feature Impactada:** Feature 04 - Gestão de Contas (spec 002)
* **Histórias de Usuário Atendidas:** US-03 [RBN-CAD-01.1][RBN-CAD-01.2][RBN-CAD-01.4][RBN-CAD-02.1][RBN-CAD-02.2], US-04 [RBN-CAD-01.3][RBN-CAD-02.3], US-05 [RBN-CAD-03.1][RBN-CAD-03.2][RBN-DEF-02.3], US-06 [RBN-CAD-03.3][RBN-DEF-02.4], US-50 [RBN-CAD-03.3]; apoio [RBN-CAD-11.3][RBN-CAD-14.1][RBN-CAD-06.2]. Cada classe, função, template e teste cita as US, RBN ou FR que atende (conferido por script, T045).
* **Requisitos da spec 002:** FR-001 a FR-048; SC-001 a SC-009 (SC-007 e SC-008 são manuais, ver seção 4).
* **Cartão no Trello:** [preencher]

**Commits deste PR**

| Commit | Mensagem |
|---|---|
| f07ed03 | docs(feat-04): especificar gestao de contas |
| c1fa96b | docs(feat-04): planejar gestao de contas |
| cf458a1 | chore(feat-04): adicionar textos e fabricas de teste da gestao de contas |
| aa087d5 | feat(feat-04): adicionar coluna mem_prorrogado_ate em MembrosExternos |
| 6034559 | feat(feat-04): preparar base da gestao de contas |
| 6a42dca | feat(feat-04): cadastrar alterar e listar docentes e secretaria |
| 4795105 | feat(feat-04): criar comando dos coordenadores iniciais |
| c09d0c8 | feat(feat-04): cadastrar e alterar membros externos |
| 2c197b6 | feat(feat-04): inativar e reativar docentes e secretaria |
| e8f3af4 | feat(feat-04): trocar email pelo gestor com confirmacao |
| 4da0580 | feat(feat-04): calcular validade e expirar membros externos |
| 8ed016d | feat(feat-04): prorrogar acesso de membro externo |
| 3a47339 | test(feat-04): cobrir permissoes, concorrencia e contrato |
| (este) | docs(feat-04): adicionar texto do pr da gestao de contas |

### 3. Checklist Técnico da Equipe (Definition of Done)

- [x] Código verificado com isort, black (100) e flake8 (100) na árvore `sigtcc/` inteira, só em modo de checagem: sem pendências (T043).
- [x] Não há variáveis, imports ou trechos de código não utilizados (flake8 limpo).
- [x] Migrações: só a `0006_membrosexternos_mem_prorrogado_ate` (coluna nula, com o dicionário no mesmo commit); `makemigrations --check --dry-run` → "No changes detected"; nenhuma migração antiga alterada.
- [x] `.env` e `media/` NÃO foram adicionados ao Git (`git ls-files`).
- [ ] A interface segue a paleta e os padrões do protótipo de 17/10 (ISO/IEC 25010): templates com as classes da base visual da feat-02; **falta a conferência visual manual** (T044).
- [ ] Não há quebras de layout ou erros no console do navegador: **falta o roteiro manual** (T044).

### 4. Evidência da Validação Manual (Critérios de Aceite das USs)

Suíte completa: `python manage.py test sigtcc.apps.cadastro sigtcc.apps.defesa` → 628 testes (207 novos da feat-04).
- Falha esperada: 1, o texto de expiração da US-06 no login, que depende da Q-52 (Julia).
- Problemas que já existiam antes desta feature: 2 erros, porque `test_mensagens.py` e `test_mensagens_turmas.py` abrem a US v3.2, que não existe no repositório (Q-77); e 1 falha intermitente da spec 003 (`test_cenario5_link_gerado_fora_das_telas`), que depende do relógio.

**Validação manual (T044)**
- [ ] Roteiro do `quickstart.md` (seções 1 a 6)
- [ ] SC-007: instalação nova com 3 Coordenadores, primeiro acesso e cadastros em até 10 minutos
- [ ] SC-008: cadastrar um docente em até 2 minutos e prorrogar o acesso de um membro em até 30 segundos
- [ ] Revisão visual em 360, 768 e 1280 px, comparando com o protótipo de 17/10

**Testes automatizados por US**
- [x] **US-03:** `test_us03_docentes.py` (39 testes) e `test_us03_secretarias.py` (11) cobrem os cenários 1 a 31 e 33 a 40, mais Q5, Q7, Q8, Q26 e Q32.
- [x] **US-04:** `test_us04_inativacao.py` (28) cobre os cenários 1 a 25, mais Q14, Q16, Q18, Q27 e o status incompatível (MC-10).
- [x] **US-05:** `test_us05_membros.py` (24) cobre os cenários 1 a 16 e 18 a 23, mais Q10, Q12, Q19 e o atalho da banca.
- [x] **Troca de e-mail:** `test_troca_email_gestor.py` (14) cobre o cenário 32 da US-03 e o 17 da US-05, mais Q17, Q24, Q28, Q30, Q31 e Q35.
- [x] **US-06:** `test_us06_validade.py` (28) cobre os cenários 1 a 18, a expiração pelo login e pelo comando (SC-006), Q13, Q33 e Q36. O texto de expiração da US-06 é a falha esperada (Q-52).
- [x] **US-50:** `test_us50_prorrogacao.py` (15) cobre os cenários 1 a 9, Q10, Q11 e Q36.
- [x] **Coordenadores iniciais:** `test_comando_coordenadores.py` (11) cobre os cenários 1 a 4, CSV com BOM, saída sem e-mail e `DEBUG = False`.
- [x] **Segurança e integridade:**
  - `test_permissoes_contas.py` (12): as 13 rotas para 8 perfis, visitante e 404 para id de outro tipo de conta (SC-004);
  - `test_concorrencia_contas.py` (6): duas conexões disputando e-mail, Coordenador, Secretaria, inativação contra vínculo novo, expiração contra prorrogação e edição contra inativação (SC-003);
  - `test_contrato_contas.py` (11): contrato com as outras features e tempo do filtro com 180 docentes (SC-009);
  - `test_mensagens_contas.py` (3): textos contra a US v3.3 e a tabela MC (SC-002);
  - `test_log_contas.py` (5): eventos do log.

### 5. Pendências que não bloqueiam o merge

| Pendência | Com quem | Índice |
|---|---|---|
| Ciência dos acréscimos ao código da spec 003 e atualização do texto dela | Julia Cohen | Q-71 |
| Texto de expiração da US-06 no login (M-16) | Julia Cohen | Q-52 |
| Testes das specs 003 e 004 que abrem a US v3.2; `criar_turma` travar e conferir docente 'Ativa' | Julia Cohen | Q-77 |
| Chamar `recalcular_validade` nos eventos de banca, travar a conta ao incluir na banca e validar o membro do atalho; agendar a expiração | Célio Benjamim | Q-67, Q-70 |
| Listas de orientador e coorientador só com docentes 'Ativa' e trava ao criar vínculo | Leandra Matos | Q-68 |
| Diagramas de sequência das US-03 a 06; expiração na rotina agendada única ou comando próprio | dono do documento de US, Leandra e Célio | Q-79 |
| Textos provisórios MC-11 a MC-13; prioridade da US-50 | Profa. Diana (PO) | Q-58, Q-63 |
| Atualizar o dicionário no Drive (`mem_prorrogado_ate`, descrição de `mem_validade_ate`) | Maria Luiza Guimarães | Q-69, Q-44 |

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
