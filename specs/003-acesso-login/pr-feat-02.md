# [Feat-02] Acesso e Login (US-10, US-11, US-12, US-37, US-38)

**Origem**: `feature/feat-02-acesso-e-login` → **Destino**: `develop` (merge `--no-ff`, PGCS 6.4)

**Spec**: `specs/003-acesso-login/` (spec.md, plan.md, research.md, data-model.md, contracts/rotas.md, contracts/servicos-compartilhados.md, quickstart.md, tasks.md)

**Responsável**: Julia Cohen

> **Base**: a feat-01 já está na `develop` (PR #2, `b18c237`). Esta branch foi rebaseada sobre a `develop` (`a9c6f13`, PR #3), então o diff do PR traz só os commits da feat-02 (`git log develop..HEAD`).

### 1. Resumo da Alteração

Implementa o acesso ao SIGTCC sobre o modelo de dados da feat-01, **sem criar tabelas nem colunas** (FR-028): `makemigrations --check` responde "No changes detected".

- **Primeiro acesso (US-10)**: escolha entre "Aluno" (Matrícula e E-mail Institucional) e "Docente, Secretaria ou Membro Externo" (E-mail), com só o primeiro erro na ordem dos campos (Q12). O link de ativação é assinado (`django.core.signing`), vale 24 horas e só o mais recente funciona (`usu_link_gerado_em`). Ao ser aberto, o token sai da URL e vai para a sessão. A ativação é revalidada no POST com a conta travada (`select_for_update`). Falha no envio desfaz tudo e mostra a M-17.
- **Login e saída (US-11)**: serviço próprio (`services.autenticar`) com a ordem da spec (vazio, conta inexistente com hash fictício, aguardando, bloqueio, senha, status). O bloqueio de 15 minutos após 3 senhas incorretas vale por conta, não por credencial, e fica no cache próprio `acesso`. O `next` só é seguido se for do próprio site (B2). A sessão dura 60 minutos sem uso e termina ao fechar o navegador. `authenticate()` do Django sempre devolve `None`.
- **Senha (US-12)**: alterar a senha em "Meu perfil" (as outras sessões caem, Q19); "Esqueci minha senha" com mensagem genérica e envio depois do commit; link de redefinição que cai quando a senha muda. O "Resetar primeiro acesso" funciona só para o Professor da Disciplina de turma ativa do aluno (Q27) e só com a conta 'Ativa' ou 'Aguardando Ativação' (Q29, decidida na implementação).
- **Reenvio (US-37)**: só no estado vencido; conta resetada recebe a M-08.
- **Perfil e notificações (US-38)**: cada papel edita só os seus campos. A imagem de assinatura é PNG ou JPG com até 2 MB, com o tipo detectado pelos bytes, gravada em `media/assinaturas/` e servida só ao dono, sem URL pública. A troca de e-mail é confirmada em duas etapas pelo novo endereço (Q28). A central de notificações tem sino, 20 por página e "Este item não está mais disponível" para item removido.
- **Base comum para as outras features**: layout do protótipo de 17/10 (`base.html`, `base_publica.html`, includes, `static/css/sigtcc.css`; `sigtcc.js` escrito do zero), `@perfil_requerido` e `PerfilRequeridoMixin`, papéis do Docente, regra compartilhada `professor_com_turma_ativa`, menu por app (`menu.py`), `handler403` com a M-02, funções de link e o comando `criar_conta_teste` (contrato `servicos-compartilhados.md`).
- **Log de acesso (FR-029)**: `LOG_DIR/acesso.log`, uma linha por evento (senha errada, bloqueio, troca e redefinição de senha, reset, pedido e confirmação de troca de e-mail), sem senhas, links nem e-mails completos.

### 2. Rastreabilidade com o Projeto

* Feature Impactada: Feature 02 - Acesso e Login (spec 003), com a base comum usada pelas demais features
* Histórias de Usuário Atendidas: US-10 [RBN-CAD-06.1][RBN-CAD-06.2][RBN-CAD-06.3], US-11 [RBN-CAD-06.4][RBN-CAD-06.6][RBN-CAD-03.3], US-12 [RBN-CAD-06.5][RBN-CAD-06.7][RBN-CAD-06.8], US-37 [RBN-CAD-06.9], US-38 [RBN-CAD-13.1][RBN-CAD-13.2]. Cada classe, função, template e teste cita as US, RBN ou FR que atende; a conferência foi feita por script na T047.
* Requisitos da spec 003: FR-001 a FR-029; SC-001 a SC-009 (SC-003 e SC-007 pelo roteiro manual, ver seção 4).
* Cartão no Trello: [preencher]

**Commits deste PR** (só os da feat-02)

| Commit | Mensagem |
|---|---|
| 4de5375 | docs(feat-02): especificar acesso e login |
| 4efdff7 | docs: criar indice de questoes a rever |
| 0733512 | docs(feat-02): esclarecer spec de acesso e login |
| 83fe484 | docs(feat-02): planejar acesso e login |
| 265fcf9 | docs(feat-02): detalhar tarefas de acesso e login |
| 2e51743 | feat(feat-02): implementar login com base visual e permissoes |
| 1dd4d33 | feat(feat-02): implementar primeiro acesso com link de ativacao |
| b4785a2 | test(feat-02): cobrir a base comum e o comando de conta de teste |
| bfcf5f4 | feat(feat-02): reenviar link de ativacao vencido |
| 5e37dcf | docs(feat-02): registrar reset so para conta ativa ou aguardando |
| ccf73f9 | feat(feat-02): recuperar e alterar senha e resetar primeiro acesso |
| ff5fb5d | feat(feat-02): editar perfil e mostrar notificacoes |
| aa2ff68 | test(feat-02): cobrir mensagens, log e seguranca do acesso |
| eb66138 | docs(feat-02): registrar entrega no changelog e texto do pr |
| 3610a7f | docs(feat-02): registrar validacao manual e responder q-19 |
| (este) | docs(feat-02): atualizar commits do texto do pr |

### 3. Checklist Técnico da Equipe (Definition of Done)

- [x] O código foi verificado localmente com isort, black e flake8, o equivalente do `lint.bat` fora do Windows. Rodando duas vezes, a segunda passada não altera nada ("64 files left unchanged"), e o `flake8 sigtcc/` não aponta erros.
- [x] Não há variáveis, imports ou trechos de código não utilizados (flake8 limpo).
- [x] Migrações: nenhuma nova (FR-028); `makemigrations --check --dry-run` → "No changes detected".
- [x] O arquivo `.env` e a pasta `media/` NÃO foram adicionados ao Git. `.gitignore` ganhou `/logs/` e `/cache_acesso/`. Os testes de assinatura usam um `MEDIA_ROOT` temporário e não gravam em `sigtcc/media/`.
- [x] A interface segue a paleta e os padrões do protótipo de 17/10 (ISO/IEC 25010): tokens de cor, fontes e componentes do protótipo, conferidos em teste e no checklist visual em 360, 768 e 1280 px (quickstart, seção 3; T050, Julia Cohen, 2026-10-20).
- [x] Não há quebras de layout ou erros no console do navegador (roteiro manual, T050).

### 4. Evidência da Validação Manual (Critérios de Aceite das USs)

Suíte completa: `python manage.py test sigtcc.apps` → `Ran 229 tests ... OK` (53 da feat-01 e 176 novos). Roteiro manual do quickstart (seções 1 a 3, itens a a o, com o tempo do primeiro acesso do SC-003 e o checklist visual do SC-007) executado por Julia Cohen em 2026-10-20 (T050), sem divergências.

**US-10 – Primeiro acesso** (`test_us10_primeiro_acesso.py`, 33 testes)
- [x] Cenários 1 a 11, mais Q2, Q6, Q8, Q12, Q15, M-14, falha no envio (M-17), token fora da URL, link adulterado (Q23), conta inativada com link válido (B1, Q26) e revalidação no POST

**US-11 – Login e saída** (`test_us11_login.py`, 28 testes)
- [x] Cenários 1 a 12 e a saída (13), mais Q4, Q12, Q13, Q17, bloqueio pelo relógio (14 e 15 minutos), `next` externo (B2), hash sem conta (I1) e e-mail duplicado (I3)

**US-12 – Senha e reset** (`test_us12_senha.py`, 30 testes)
- [x] Cenários 1 a 8, mais Q19 (sessões), Q26 (GET e POST), Q9, Q27 e Q29 (reset), link de outro tipo e mensagem genérica com falha no envio

**US-37 – Reenvio** (`test_us37_reenvio.py`, 11 testes)
- [x] Cenários 1 a 5, mais reenvio só no estado vencido, sem token na sessão e falha no envio

**US-38 – Perfil e notificações** (`test_us38_perfil_notificacoes.py`, 33 testes)
- [x] Cenários 1 a 11 (o 9 na variante "item removido", Q10), mais Q11, Q28, M-05, M-09, assinatura disfarçada (I7), assinatura sem URL pública, falha no envio da troca, paginação e ordem

**História 6 – Base comum** (`test_base_comum.py`, 15; `test_criar_conta_teste.py`, 7)
- [x] Cenários 1 a 6, mais Q27, papéis numa consulta, menu por perfil, `PermissionDenied` em serviço e `PerfilRequeridoMixin`

**Transversais**
- [x] SC-002: `test_mensagens.py` confere cada texto contra as US, a matriz e a tabela de mensagens provisórias da spec
- [x] SC-009: `test_log_acesso.py` confere uma linha por evento, com conta e data, e sem dados sensíveis
- [x] SC-004, SC-006 e SC-008: `test_seguranca.py` cobre todas as páginas internas, a sessão de 60 minutos, os cookies, os links usados duas vezes e o reset concorrente

### Decisões e desvios registrados

| Decisão | Registro | Situação |
|---|---|---|
| Reset do primeiro acesso só para conta 'Ativa' ou 'Aguardando Ativação' | spec Q29, FR-015; índice Q-33 | Decidido por Julia Cohen na implementação (2026-10-20) |
| Ativar a conta não grava novo `usu_link_gerado_em` (a T023 dizia que sim); o link usado cai porque a conta fica 'Ativa' | research A3 e data-model; tasks T023 corrigida | Sem mudança de comportamento |
| Links da tela de login e da barra superior entram quando a rota existe (`{% url ... as %}` na tela de login; H1 na barra) | tasks T017, T020, T022 e T034 | Sem mudança de comportamento |
| Item "Notificações" no menu lateral não incluído (opcional na T042): o sino já leva à central | tasks T042 | A critério da equipe |
| "Sair" é rótulo da spec (FR-011), não das US | `mensagens.py`, `test_mensagens.py` | Registrado |

### Itens de configuração para revisão do Célio Benjamim (constituição, princípio IX; índice Q-23 e Q-27)

- [ ] `.env.example`: `CACHE_ACESSO_DIR`, `EMAIL_*`, `EMAIL_TIMEOUT`, `DEFAULT_FROM_EMAIL`, `SITE_URL`, `LOG_DIR`, `COOKIES_SEGUROS`
- [ ] `.gitignore`: `/logs/` e `/cache_acesso/`
- [ ] `sigtcc/settings.py`: `AUTHENTICATION_BACKENDS`, `LOGIN_URL`, regra de senha, sessão (3600 s, deslizante, fim ao fechar o navegador), cookies `HttpOnly`/`Lax` e `Secure` por `COOKIES_SEGUROS`, `SECURE_REFERRER_POLICY` e `NOSNIFF`, e-mail, `CACHES["acesso"]` (100.000 entradas), `LOGGING` com rotação 5 × 5 MB e processadores de contexto
- [ ] `sigtcc/urls.py`: `include` do cadastro e `handler403`; sem `MEDIA_URL` publicado
- [ ] Módulos fora da árvore do PGCS 2.3: `backends.py`, `permissoes.py`, `contexto.py`, `menu.py`, `mensagens.py`, `validators.py`, `management/commands/criar_conta_teste.py`; templates `base_publica.html` e `acesso_negado.html`
- [ ] Servidor de produção: agendar `python manage.py clearsessions`, fuso America/Manaus, limite de upload no servidor web e log do servidor sem o primeiro GET com token (research A3, A6, A11, A19)
- [ ] **Confirmar o nome da branch** `feature/feat-02-acesso-e-login` (índice Q-09; no PGCS 4.3 a feat-02 é Turmas)

### Pendências

| Pendência | Destino | Índice |
|---|---|---|
| Validar as 17 mensagens provisórias M-01 a M-17 (não bloqueiam o merge, spec Q25) | Profa. Diana (PO) | Q-01 |
| Ciência da regra do Professor da Disciplina (turma não arquivada para alterar dados) | Leandra, Célio, Maria Luísa, Maria Luiza | Q-29 a Q-32 |
| US-41 levar o botão "Resetar primeiro acesso" ao painel do aluno | Leandra Matos | Q-13 |
| Spec 002: criar contas sem enviar link; contas iniciais de Coordenador; US-06 mudar o status de Membro Externo vencido | Maria Luísa Gomes | Q-14 a Q-16 |
| Notificação de convite de banca cancelado (`services.item_indisponivel`) | Célio Benjamim | Q-12 |
| Índice único em `lower(usu_email)` (opcional, muda o esquema) | Maria Luiza Guimarães | Q-28 |

### 5. Revisão por Pares (Peer Review)

* Revisor Designado: [preencher: integrante da equipe] (itens de configuração: Célio Benjamim)
* Parecer do Revisor:

[ ] Aprovado integralmente para merge

[ ] Solicitação de ajustes (detalhar nos comentários)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
