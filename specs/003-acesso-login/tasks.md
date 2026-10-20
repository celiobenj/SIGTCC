# Tasks: Acesso e Login do SIGTCC

**Input**: Design documents from `specs/003-acesso-login/`

**Prerequisites**: [plan.md](plan.md) (aprovado em 2026-10-20), [spec.md](spec.md) (aprovada em
2026-10-20), [research.md](research.md), [data-model.md](data-model.md),
[contracts/rotas.md](contracts/rotas.md), [contracts/servicos-compartilhados.md](contracts/servicos-compartilhados.md),
[quickstart.md](quickstart.md)

**Aprovação**: tasks aprovado por Julia Cohen em 2026-10-20.

**Tests**: obrigatórios (constituição, princípio VI): cada cenário Dado/Quando/Então das US-10, 11, 12,
37 e 38 vira pelo menos um teste, mais os testes da base comum, de segurança, de mensagens exatas e do
log. Os testes de cada história vêm antes da implementação e devem falhar primeiro.

**Organization**: as histórias são as da spec: US1 = primeiro acesso (US-10), US2 = login e saída
(US-11), US3 = reenvio do link (US-37), US4 = recuperar e alterar a senha (US-12), US5 = perfil e
notificações (US-38), US6 = base comum para as outras features.

**Branch**: `feature/feat-02-acesso-e-login` (Q-09 do índice). Commits atômicos ao fim de cada fase,
só com os testes da fase passando, mostrando o `git status` antes (CLAUDE.md). Formato:
`feat(feat-02): <imperativo, até 72 caracteres, sem ponto final>`. Não fazer push, merge nem tag.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência de tarefa incompleta)
- **[Story]**: história da spec (US1 a US6)

## Regras para todas as tarefas

- Comentários e docstrings em português; cada classe, função, template e teste indica as US e RBN que
  atende (constituição, princípio II). Cada tarefa termina com `Rastreabilidade:`.
- Mensagens: sempre pelas constantes de `sigtcc/apps/cadastro/mensagens.py` (T004), nunca texto solto.
- Nenhuma tabela, coluna ou migração nova (FR-028). Nenhum JavaScript do protótipo.
- Regras em `services.py`; views só orquestram; templates sem regra (constituição, princípio IV).
- Serviços que alteram a conta: `transaction.atomic()` + `select_for_update()` na linha de `Usuarios`,
  com o link revalidado no POST (research A17).
- Datas: `django.utils.timezone.now()` (sem fuso, `USE_TZ = False`); testes avançam o relógio com
  `unittest.mock.patch("django.utils.timezone.now")`; nunca `signing.loads(max_age=...)` (A3, A19).
- Referências: "Q27" (sem hífen) é questão das Clarifications da spec; "Q-27" (com hífen) é item do
  índice `docs/questoes-a-rever.md`.
- Testes usam `force_login` (o backend não autentica por senha, A1), e-mail `locmem`, caches locais
  para `default` e `acesso` e `SIGTCC_EMAIL_SINCRONO = True`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: configuração do projeto para sessão, e-mail, cache do login, log e rotas.

- [ ] T001 Atualizar `.env.example` com `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`, `EMAIL_HOST=`, `EMAIL_PORT=587`, `EMAIL_HOST_USER=`, `EMAIL_HOST_PASSWORD=`, `EMAIL_USE_TLS=True`, `EMAIL_TIMEOUT=10`, `DEFAULT_FROM_EMAIL=nao-responda@uea.edu.br`, `SITE_URL=http://localhost:8000`, `LOG_DIR=logs`, `CACHE_ACESSO_DIR=cache_acesso` e `COOKIES_SEGUROS=False` (cada uma com comentário em português), e acrescentar `/logs/` e `/cache_acesso/` ao `.gitignore`. — Rastreabilidade: [infraestrutura da feature 003][índice Q-23][índice Q-27]
- [ ] T002 Atualizar `sigtcc/settings.py` (research A1, A2, A5, A6, A13, A19): `AUTHENTICATION_BACKENDS = ["sigtcc.apps.cadastro.backends.SigtccBackend"]`; `LOGIN_URL = "cadastro:entrar"`; `LOGIN_REDIRECT_URL = "cadastro:painel"`; `SESSION_COOKIE_AGE = 3600`, `SESSION_SAVE_EVERY_REQUEST = True`, `SESSION_EXPIRE_AT_BROWSER_CLOSE = True`, `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = "Lax"`, `SESSION_COOKIE_SECURE` e `CSRF_COOKIE_SECURE` iguais a `COOKIES_SEGUROS == "True"`; `SECURE_REFERRER_POLICY = "same-origin"` e `SECURE_CONTENT_TYPE_NOSNIFF = True` declarados com comentário "não afrouxar (A3, A11)"; `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `EMAIL_TIMEOUT` (int, padrão 10), `DEFAULT_FROM_EMAIL` e `SITE_URL` do `.env`; `SIGTCC_EMAIL_SINCRONO = False`; `CACHES["acesso"]` com `FileBasedCache`, `LOCATION` = `CACHE_ACESSO_DIR` (relativo a `BASE_DIR`, padrão `cache_acesso`) e `OPTIONS={"MAX_ENTRIES": 100000}`; `LOG_DIR` do `.env` (padrão `logs`), criado com `mkdir(parents=True, exist_ok=True)`, e `LOGGING` com o logger `sigtcc.acesso` (nível INFO, `propagate=False`) num `logging.handlers.RotatingFileHandler` (`LOG_DIR/acesso.log`, `maxBytes=5*1024*1024`, `backupCount=5`, `delay=True`, `encoding="utf-8"`, formato `%(asctime)s | %(message)s`); `AUTH_PASSWORD_VALIDATORS = [{"NAME": "sigtcc.apps.cadastro.validators.RegraSenhaSigtcc"}]`; processadores de contexto `sigtcc.apps.cadastro.contexto.menu` e `sigtcc.apps.cadastro.contexto.notificacoes_nao_lidas`. — Rastreabilidade: [US-11][RBN-CAD-06.4][RBN-CAD-06.6][FR-011][FR-029][spec Q18][spec Q21][índice Q-27]
- [ ] T003 Criar `sigtcc/apps/cadastro/urls.py` com `app_name = "cadastro"` e `urlpatterns = []` (as rotas entram em cada fase) e atualizar `sigtcc/urls.py` com `path("", include("sigtcc.apps.cadastro.urls"))` e `handler403 = "sigtcc.apps.cadastro.views.acesso_negado"`, **sem** publicar `MEDIA_URL` (as assinaturas não têm URL pública, A11). — Rastreabilidade: [infraestrutura da feature 003][FR-025][FR-020]

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: mensagens, regra de senha, backend, permissões, log, base visual, painel e conta de teste,
usados por todas as histórias.

**⚠️ CRITICAL**: nenhuma história começa antes desta fase.

- [ ] T004 [P] Criar `sigtcc/apps/cadastro/mensagens.py` com constantes de texto exato. Das US (copiar caractere por caractere): `LINK_ATIVACAO_ENVIADO = "Enviamos um link de ativação para o seu e-mail"`, `CONTA_ATIVADA = "Conta ativada"`, `DADOS_NAO_ENCONTRADOS = "Dados não encontrados. Procure o Professor da Disciplina ou a Secretaria"`, `CONTA_JA_ATIVA = "Esta conta já está ativa"`, `EMAIL_INSTITUCIONAL = "Informe o seu e-mail institucional da UEA (@uea.edu.br)"`, `MATRICULA_FORMATO = "A matrícula deve ter 10 dígitos numéricos"`, `EMAIL_DE_OUTRA_CONTA_ALUNO = "Este e-mail já está vinculado a outra conta. Procure o Professor da Disciplina"`, `REGRA_SENHA = "A senha deve ter de 8 a 64 caracteres, com ao menos 1 letra e 1 número"`, `SENHAS_NAO_CONFEREM = "As senhas não conferem"`, `LINK_SUBSTITUIDO = "Link inválido. Use o link mais recente enviado ao seu e-mail"`, `CREDENCIAL_INVALIDA = "Credencial ou senha inválida"`, `ACESSO_EXPIRADO = "Seu acesso expirou. Procure o Orientador, o Professor da Disciplina, a Secretaria ou o Coordenador de Curso"`, `CONTA_NAO_ATIVADA = "Conta ainda não ativada"`, `CONTA_INATIVA = "Conta inativa"`, `INFORME_CREDENCIAL = "Informe a credencial e a senha"`, `SENHA_ALTERADA = "Senha alterada com sucesso"`, `SENHA_ATUAL_INCORRETA = "Senha atual incorreta"`, `ESQUECI_GENERICA = "Se a conta existir, enviaremos um link para o e-mail cadastrado"`, `LINK_INVALIDO_OU_VENCIDO = "Link inválido ou vencido. Solicite um novo"`, `LINK_ATIVACAO_VENCEU = "Este link de ativação venceu"`, `NOVO_LINK_ENVIADO = "Enviamos um novo link para o seu e-mail"`, `PERFIL_ATUALIZADO = "Perfil atualizado"`, `SEM_NOTIFICACOES = "Você não tem notificações"`, `ITEM_INDISPONIVEL = "Este item não está mais disponível"`; rótulos de botão e link `PRIMEIRO_ACESSO`, `ESQUECI_MINHA_SENHA`, `ENTRAR`, `ENVIAR`, `ATIVAR_CONTA`, `REENVIAR_LINK = "Reenviar link de ativação"`, `SALVAR`, `ALTERAR_SENHA`, `RESETAR_PRIMEIRO_ACESSO`, `MARCAR_COMO_LIDAS`, `MEU_PERFIL`, `SAIR`, `CONFIRMAR_NOVO_EMAIL = "Confirmar novo e-mail"`. Provisórias, com o ID no nome e o texto exato da tabela "Mensagens a validar com a PO" da spec: `M01_BLOQUEIO` (com `{minutos}` no lugar de N), `M02_ACESSO_NEGADO`, `M03_ORIENTACAO_CONTA_ATIVA`, `M04_ASSINATURA_FORMATO`, `M05_EMAIL_EM_USO`, `M06_CONFIRMACAO_EMAIL_ENVIADA`, `M07_EMAIL_ATUALIZADO`, `M08_REFAZER_PRIMEIRO_ACESSO`, `M09_LINK_EMAIL_INVALIDO = LINK_INVALIDO_OU_VENCIDO`, `M10_EMAIL_INVALIDO`, `M11_EMAIL_INSTITUCIONAL = EMAIL_INSTITUCIONAL`, `M12_CONFIRMAR_RESET` (com `{nome}`), `M13_RESET_CONCLUIDO`, `M14_CAMPO_OBRIGATORIO`, `M15_CONTA_INATIVA = CONTA_INATIVA`, `M16_ACESSO_EXPIRADO = ACESSO_EXPIRADO`, `M17_FALHA_ENVIO`. Docstring do módulo: "provisórias até a validação da PO (Q-01; spec Q25)". — Rastreabilidade: [US-10][US-11][US-12][US-37][US-38][SC-002]
- [ ] T005 [P] Criar `sigtcc/apps/cadastro/validators.py` com `RegraSenhaSigtcc` (validador do Django: `validate(password, user=None)` levanta `ValidationError(REGRA_SENHA)` se a senha tiver menos de 8 ou mais de 64 caracteres, não tiver ao menos um caractere de `[A-Za-z]` ou não tiver ao menos um de `[0-9]`; letras acentuadas e outros caracteres são aceitos mas não contam como a letra; `get_help_text()` devolve `REGRA_SENHA`) e a função `senha_atende_regra(senha) -> bool`. — Rastreabilidade: [US-10][RBN-CAD-06.3][US-12][RBN-CAD-06.5][Q17]
- [ ] T006 [P] Criar `sigtcc/apps/cadastro/backends.py` com `SigtccBackend(ModelBackend)`: `authenticate()` devolve sempre `None`; `get_user(user_id)` carrega `Usuarios` com `select_related("alunos", "docentes", "membrosexternos", "secretarios")` e devolve o usuário só se `user_can_authenticate`; `user_can_authenticate(usuario)` exige `usu_status == "Ativa"` e, se a conta for de Membro Externo com `mem_validade_ate`, `mem_validade_ate >= timezone.now().date()` (research A1, Q4). — Rastreabilidade: [US-11][RBN-CAD-06.4][RBN-CAD-03.3][Q4][Q18]
- [ ] T007 Criar `sigtcc/apps/cadastro/permissoes.py` (research A7): `tipo_conta(usuario)` → `"aluno"`, `"docente"`, `"secretaria"`, `"membro_externo"` ou `None`, pelas relações já carregadas; `papeis(usuario)` → `frozenset` com `"coordenador"` (existe `Coordenadores` com `cor_doc` = docente), `"professor_disciplina"` (é `tur_doc` de **pelo menos uma turma, ativa ou arquivada**, spec Q27), `"orientador"` (`Orientacoes` com `ori_status = "Ativa"`) e `"coorientador"` (`Coorientacoes` com `coo_doc` e `coo_status = "Ativa"`), calculado na primeira chamada e guardado em `usuario._papeis_cache`; `tem_perfil(usuario, *perfis)`; `professor_com_turma_ativa(professor, aluno=None)` (professor `Usuarios` com `Docentes`; verdadeiro se é `tur_doc` de turma com `tur_status = "Ativa"` e, com `aluno`, se o aluno está em `AlunosTurmas` dessa turma; base RBN-CAD-04.5); `pode_resetar_primeiro_acesso(professor, aluno)` = `professor_com_turma_ativa(professor, aluno)`; decorador `perfil_requerido(*perfis)` (sem argumentos: só login; sem login: `redirect_to_login` com `next`; sem permissão: `raise PermissionDenied`) e `PerfilRequeridoMixin` (`perfis_permitidos`). Docstrings com as regras compartilhadas do contrato §2. — Rastreabilidade: [FR-025][Q27][RBN-CAD-04.5][RNF RAN-CAD-01 e RAN-CAD-02]
- [ ] T008 Criar `sigtcc/apps/cadastro/services.py`, parte comum (research A12, A13, A18): `EventoAcesso` (enum com `LOGIN_SENHA_INCORRETA`, `BLOQUEIO`, `SENHA_ALTERADA`, `SENHA_REDEFINIDA`, `RESET_PRIMEIRO_ACESSO`, `TROCA_EMAIL_PEDIDA`, `TROCA_EMAIL_CONFIRMADA`, `EMAIL_DUPLICADO`, `FALHA_ENVIO_EMAIL`); `registrar_evento(evento, conta, autor=None, detalhe="")` gravando no logger `sigtcc.acesso` a linha `evento | conta=<usu_id ou -> | autor=<usu_id ou própria> | detalhe`, sem senha, token, link nem e-mail completo; `normalizar_email(email)` (strip, `BaseUserManager.normalize_email`, `None` se vazio); `email_em_uso(email, exceto=None)` (`usu_email__iexact`, excluindo `exceto`); `item_indisponivel(request)` (grava `ITEM_INDISPONIVEL` em `messages` e redireciona para `cadastro:notificacoes`); `enviar_email(destino, assunto, template, contexto)` que usa `send_mail` e, em exceção, registra `FALHA_ENVIO_EMAIL` só com o tipo da exceção e relança. — Rastreabilidade: [FR-029][Q21][Q13][I3][Q10]
- [ ] T009 [P] Criar `sigtcc/apps/cadastro/menu.py` com `ITENS = [{"rotulo": "Início", "icone": "home", "rota": "cadastro:painel", "perfis": ("aluno", "docente", "secretaria", "membro_externo"), "ordem": 0}]` e `sigtcc/apps/cadastro/contexto.py` com `menu(request)` (junta os `ITENS` de todos os `apps.get_app_configs()` que têm módulo `menu`, filtra por `tem_perfil`, resolve `rota` com `reverse` e ordena por `ordem` e `secao`) e `notificacoes_nao_lidas(request)` (contagem de `Notificacoes` com `not_usu` = usuário e `not_lida = False`); os dois devolvem `{}` para visitante anônimo, sem consultar o banco (research A8). — Rastreabilidade: [FR-022][FR-025][RBN-CAD-13.2]
- [ ] T010 [P] Criar `sigtcc/static/css/sigtcc.css` a partir do visual do protótipo `docs/fonte/prototipo/prototipo_17_10.html` (research A14): variáveis do `:root` do protótipo (`--azul #1967d2`, `--azul-claro #e8f0fe`, `--azul-btn #1a73e8`, `--verde #137333`, `--verde-claro #e6f4ea`, `--laranja #e37400`, `--amarelo #f9ab00`, `--amarelo-claro #fef7e0`, `--vermelho #c5221f`, `--vermelho-claro #fce8e6`, `--roxo #9334e6`, `--teal #129eaf`, `--texto #202124`, `--texto2 #5f6368`, `--texto3 #80868b`, `--borda #dadce0`, `--fundo #fff`, `--fundo2 #f8f9fa`, `--hover #f1f3f4`, `--radius 8px`, `--sombra`, `--sombra2`, `--fonte` Roboto e `--fonte-tit` Figtree); barra superior de 64 px, menu lateral (gaveta), `.btn`, `.btn.pri`, `.btn.txt`, `.campo` com erro por campo, `.alerta.info|aviso|erro|sucesso`, aviso temporário, `.cartao`, `.tabela`, `.badge` do sino, `.ms` (Material Symbols); ajustes em `@media (max-width:900px)` e `(max-width:600px)` e layout sem rolagem horizontal a partir de 360 px. Comentário no topo: "visual do protótipo de 17/10; nenhum código JavaScript copiado". — Rastreabilidade: [FR-024][Q22][SC-007]
- [ ] T011 [P] Criar `sigtcc/static/js/sigtcc.js`, escrito do zero: abrir e fechar o menu lateral pelo botão da barra superior e fechar avisos temporários; sem lógica de negócio. — Rastreabilidade: [FR-024]
- [ ] T012 Criar os templates base em `sigtcc/templates/`: `base.html` (fontes Roboto/Figtree e Material Symbols pelo mesmo `<link>` do Google Fonts do protótipo, `sigtcc.css`, `sigtcc.js`; blocos `titulo`, `conteudo`, `scripts`; inclui barra superior, menu lateral e mensagens), `base_publica.html` (sem menu e sem sino), `acesso_negado.html` (M-02), `includes/barra_superior.html` (nome do sistema, botão de menu, sino com a contagem de `notificacoes_nao_lidas` e área do menu do usuário; só usa `{% url %}` de rotas que já existem: "Sair" entra em T020, "Meu perfil" e o link do sino para a central entram em T042), `includes/menu_lateral.html` (itens do contexto `menu`), `includes/mensagens.html` (`django.contrib.messages` como alertas) e `includes/campo.html` (rótulo, ajuda, destaque e erro; texto, e-mail, senha, número, data, arquivo, `select` e `checkbox`). — Rastreabilidade: [FR-024][FR-022][US-11][US-38]
- [ ] T013 Criar em `sigtcc/apps/cadastro/views.py` as views `acesso_negado(request, exception=None)` (status 403, `acesso_negado.html` com `M02_ACESSO_NEGADO`), `inicio` (logado → `painel`; senão → `entrar`) e `painel` (`@perfil_requerido()`, mostra boas-vindas e o tipo de conta), o template `sigtcc/templates/cadastro/painel.html` e as rotas `inicio` (`/`) e `painel` (`/painel/`) em `sigtcc/apps/cadastro/urls.py`. — Rastreabilidade: [US-11][FR-010][FR-025][Q7]
- [ ] T014 Criar `sigtcc/apps/cadastro/forms.py` com a classe base `FormularioPrimeiroErro(forms.Form)`: valida os campos na ordem declarada e, depois de `full_clean`, mantém em `errors` só o primeiro campo com erro; campos obrigatórios usam `M14_CAMPO_OBRIGATORIO` como mensagem de `required` (research A9). — Rastreabilidade: [FR-003][Q12][M-14]
- [ ] T015 Criar `sigtcc/apps/cadastro/management/__init__.py`, `management/commands/__init__.py` e `management/commands/criar_conta_teste.py` (research A15): opções `--perfil` (`aluno`, `docente`, `coordenador`, `secretaria`, `membro_externo`), `--status` (`aguardando` ou `ativa`, padrão `aguardando`), `--email`, `--matricula`, `--senha`, `--curso` (nome, padrão "Engenharia de Computação"), `--turma <identificador>` (reaproveita se existir; senão cria `Disciplinas` de teste e turma "TCC 1" ativa com esse identificador), `--professor <email>` (`tur_doc` na criação; padrão: o próprio docente, ou um docente de teste), `--arquivada` e `--validade AAAA-MM-DD`; matrícula a turma com `AlunosTurmas`; recusa coordenador repetido no curso com mensagem clara; recusa com `DEBUG = False`; imprime o `usu_id`; usa `Usuarios.objects.create_user` e nunca informa identificador. — Rastreabilidade: [FR-027][infraestrutura de teste da feature 003]
- [ ] T016 Criar `sigtcc/apps/cadastro/tests/apoio_acesso.py` com a classe base `TesteAcesso(TestCase)` decorada com `override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", CACHES={"default": locmem, "acesso": locmem}, SIGTCC_EMAIL_SINCRONO=True, SITE_URL="http://testserver")`, `setUp` que limpa os dois caches, e funções `criar_aluno_com_turma(...)`, `criar_docente_ativo(...)`, `criar_membro_externo(...)`, `criar_notificacao(...)` e `avancar_relogio(minutos=..., horas=...)` (context manager com `patch("django.utils.timezone.now")`), reaproveitando `sigtcc/apps/cadastro/tests/fabricas.py`. — Rastreabilidade: [infraestrutura de teste da feature 003]

**Checkpoint**: base pronta; as histórias podem começar.

---

## Phase 3: User Story 2 - Fazer login e sair [US-11] (Priority: P1) 🎯 MVP

**Goal**: usuário com conta 'Ativa' entra pela credencial e senha, cai no painel e sai; três senhas
erradas seguidas bloqueiam a conta por 15 minutos.

**Independent Test**: com contas criadas por `criar_conta_teste`, entrar pela matrícula e pelo e-mail,
errar três vezes e confirmar o bloqueio, e sair.

### Tests for User Story 2 ⚠️

- [ ] T017 [US2] Criar `sigtcc/apps/cadastro/tests/test_us11_login.py` (classe `TesteAcesso`) com um teste por cenário da spec, história 2: `test_cenario1_aluno_pela_matricula` a `test_cenario12_campo_vazio` (mensagens pelas constantes de T004) e `test_cenario13_sair` (POST em `sair` encerra a sessão; página interna pede login); mais `test_ordem_q12_senha_errada_em_conta_inativa` ("Credencial ou senha inválida", conta tentativa), `test_senha_curta_conta_como_tentativa` (Q17), `test_validade_vencida_com_status_ativa` (Q4: `ACESSO_EXPIRADO`), `test_bloqueio_15_minutos_com_relogio` (`avancar_relogio(minutos=15)` libera; com 14 continua bloqueado; M-01 com minutos arredondados para cima), `test_senha_correta_em_conta_inativa_zera_contador` (FR-009), `test_next_externo_ignorado` (`next=https://outro.site/` e `next=//outro.site` vão ao painel; `next=/painel/` é seguido; B2), `test_logado_em_entrar_vai_ao_painel`, `test_credencial_inexistente_calcula_hash` (com `patch` em `Usuarios.set_password` ou no hasher, confirma que o hash é calculado também quando a conta não existe; I1) e `test_email_duplicado_nao_quebra` (duas contas com e-mails que só diferem em maiúsculas: `CREDENCIAL_INVALIDA` e evento `EMAIL_DUPLICADO` no log; I3). — Rastreabilidade: [US-11][RBN-CAD-06.4][RBN-CAD-06.6][RBN-CAD-03.3][FR-007]–[FR-011][SC-005]

### Implementation for User Story 2

- [ ] T018 [US2] Acrescentar em `sigtcc/apps/cadastro/services.py` (research A1, A2): `ResultadoLogin` (estado em `VAZIO`, `NAO_ENCONTRADA`, `AGUARDANDO`, `BLOQUEADA`, `SENHA_INCORRETA`, `INATIVA`, `EXPIRADA`, `OK`; mais `usuario` e `minutos_restantes`); funções de bloqueio no `caches["acesso"]` (`acesso:falhas:<usu_id>` com tempo de vida de 24 h; `acesso:bloqueio:<usu_id>` com o instante do fim em ISO, gravado com `cache.add` e tempo de vida de 16 min; comparação sempre com `timezone.now()`); e `autenticar(credencial, senha)` exatamente na ordem do A1: vazio → busca (10 dígitos → `Alunos.alu_matricula`; senão `usu_email__iexact`; `MultipleObjectsReturned` → evento `EMAIL_DUPLICADO` e não encontrada) → sem conta: `Usuarios().set_password(senha)` e `NAO_ENCONTRADA` → `AGUARDANDO` → bloqueio vigente → senha fora de 8 a 64 ou incorreta: conta tentativa, evento `LOGIN_SENHA_INCORRETA`, e na terceira grava o bloqueio, zera o contador, evento `BLOQUEIO` e devolve `BLOQUEADA` → senha correta: confere o bloqueio de novo, zera o contador e devolve `INATIVA`, `EXPIRADA` (status ou `mem_validade_ate < timezone.now().date()`) ou `OK`. — Rastreabilidade: [US-11][RBN-CAD-06.4][RBN-CAD-06.6][Q12][Q4][Q16][Q17][I1][I2][I3]
- [ ] T019 [US2] Acrescentar em `sigtcc/apps/cadastro/forms.py` o `FormularioLogin` (`credencial` até 100 caracteres, `senha` com `PasswordInput`, `next` oculto; sem validar formato da senha, que é tratado no serviço). — Rastreabilidade: [US-11][RBN-CAD-06.4][FR-007]
- [ ] T020 [US2] Criar em `sigtcc/apps/cadastro/views.py` as views `entrar` (GET/POST; logado → painel; traduz cada `ResultadoLogin` na mensagem exata e, em `AGUARDANDO`, mostra o link "Primeiro acesso"; em `OK`, `login(request, usuario, backend="sigtcc.apps.cadastro.backends.SigtccBackend")` e redireciona para o `next` só se `url_has_allowed_host_and_scheme(next, allowed_hosts={request.get_host()}, require_https=request.is_secure())`, senão painel) e `sair` (só POST, `logout`, redireciona para `entrar`); o template `sigtcc/templates/cadastro/entrar.html` (estende `base_publica.html`; links "Primeiro acesso" e "Esqueci minha senha"; botão "Entrar"); as rotas `entrar` (`/entrar/`) e `sair` (`/sair/`) em `sigtcc/apps/cadastro/urls.py`; e o botão "Sair" (formulário POST com CSRF) no menu do usuário em `sigtcc/templates/includes/barra_superior.html`. — Rastreabilidade: [US-11][RBN-CAD-06.4][FR-008]–[FR-011][B2]
- [ ] T021 [US2] Rodar `python manage.py test sigtcc.apps.cadastro.tests.test_us11_login` até tudo passar; rodar a suíte da feature 001 para confirmar que nada quebrou. — Rastreabilidade: [US-11][SC-001][SC-005]

**Checkpoint**: login, bloqueio e saída funcionando (MVP).

---

## Phase 4: User Story 1 - Criar a senha no primeiro acesso [US-10] (Priority: P1)

**Goal**: conta 'Aguardando Ativação' pede o link em "Primeiro acesso", abre o link e cria a senha.

**Independent Test**: conta 'Aguardando Ativação' criada pelo shell; pedir o primeiro acesso, abrir o
link do e-mail e criar a senha; a conta fica 'Ativa'.

### Tests for User Story 1 ⚠️

- [ ] T022 [US1] Criar `sigtcc/apps/cadastro/tests/test_us10_primeiro_acesso.py` com `test_cenario1` a `test_cenario11` da história 1 da spec (o 3 com `avancar_relogio(horas=25)`); mais `test_q2_email_novo_ignorado` (aluno já com e-mail: o link vai ao registrado, mesma mensagem), `test_q8_email_de_aluno_no_formulario_de_email` (`DADOS_NAO_ENCONTRADOS`), `test_q6_conta_inativa` (`M15_CONTA_INATIVA`) e `test_q6_conta_expirada_e_validade_vencida` (`M16_ACESSO_EXPIRADO`), `test_q12_so_o_primeiro_erro` (matrícula fora do formato e e-mail fora do domínio juntos: só `MATRICULA_FORMATO`), `test_q15_formato_do_email_ignorado_ainda_validado`, `test_m14_campo_vazio`, `test_i5_falha_no_envio_desfaz` (backend que levanta exceção: `M17_FALHA_ENVIO`, `usu_link_gerado_em` e e-mail do aluno inalterados, link anterior ainda válido), `test_token_sai_da_url` (GET em `ativar/<token>/` redireciona para `definir-senha/` e o token fica na sessão), `test_definir_senha_sem_token_na_sessao` (tratado como `ADULTERADO`: `LINK_SUBSTITUIDO`), `test_b1_link_valido_em_conta_inativada` (pedido, depois `usu_status='Inativa'`, abrir o link: `M15_CONTA_INATIVA`, conta não ativada), `test_link_adulterado` (Q23) e `test_post_revalida_link` (link substituído entre o GET e o POST: não ativa). — Rastreabilidade: [US-10][RBN-CAD-06.1][RBN-CAD-06.2][RBN-CAD-06.3][FR-001]–[FR-006][Q2][Q5][Q6][Q8][Q12][Q15][Q23][Q26][B1][I4][I5]

### Implementation for User Story 1

- [ ] T023 [US1] Acrescentar em `sigtcc/apps/cadastro/services.py` (research A3, A5, A17): `ResultadoLink` (estado em `ADULTERADO`, `ATIVA`, `INATIVA`, `EXPIRADA`, `SEM_EMAIL`, `SUBSTITUIDO`, `VENCIDO`, `VALIDO`, mais `usuario`); `gerar_link_ativacao(usuario)` (grava `usu_link_gerado_em = timezone.now()`, relê do banco e assina `{"usu_id", "gerado_em": isoformat com microssegundos}` com `signing.dumps(..., salt="sigtcc.ativacao")`; devolve `SITE_URL + reverse("cadastro:ativar", args=[token])`); `validar_link_ativacao(token)` na ordem do data-model (`ADULTERADO` → `ATIVA` → `INATIVA` → `EXPIRADA` → `SEM_EMAIL` → `SUBSTITUIDO` → `VENCIDO` pela idade de `gerado_em` contra `timezone.now()` > 24 h → `VALIDO` só com 'Aguardando Ativação'); `enviar_link_ativacao(usuario)` (gera, grava e envia o `emails/ativacao.txt` dentro de `transaction.atomic()`; em falha desfaz e devolve `False`); `pedir_primeiro_acesso(dados)` para os dois formulários (Q2, Q8, Q12, Q15; registra o e-mail do Aluno só se ele não tiver e-mail; `select_for_update`); e `ativar_conta(token, senha)` (revalida com a conta travada; grava `set_password`, `usu_status = "Ativa"` e um novo `usu_link_gerado_em`, invalidando o link). — Rastreabilidade: [US-10][RBN-CAD-06.1][RBN-CAD-06.2][RBN-CAD-06.3][FR-002][FR-005][FR-006][FR-016][FR-026][Q2][Q5][Q23][Q26][B1][I4][I5]
- [ ] T024 [US1] Acrescentar em `sigtcc/apps/cadastro/forms.py`, sobre `FormularioPrimeiroErro`: `PrimeiroAcessoAlunoForm` (`matricula`: exatamente 10 dígitos, `MATRICULA_FORMATO`; `email`: formato, até 100 caracteres, domínio `@uea.edu.br`, `EMAIL_INSTITUCIONAL`), `PrimeiroAcessoEmailForm` (`email`: formato `nome@domínio`, até 100 caracteres, `M10_EMAIL_INVALIDO`) e `AtivacaoForm` (`senha` e `confirmacao`, mascaradas; `RegraSenhaSigtcc` com `REGRA_SENHA`; diferentes → `SENHAS_NAO_CONFEREM`). — Rastreabilidade: [US-10][RBN-CAD-06.1][RBN-CAD-06.2][RBN-CAD-06.3][FR-001][FR-003][FR-004][Q12]
- [ ] T025 [US1] Criar em `sigtcc/apps/cadastro/views.py` as views `primeiro_acesso` (escolha "Aluno" ou "Docente, Secretaria ou Membro Externo"), `primeiro_acesso_aluno`, `primeiro_acesso_email` (mostram `LINK_ATIVACAO_ENVIADO`, as mensagens de recusa de FR-003, com `CONTA_JA_ATIVA` sempre seguida do complemento `M03_ORIENTACAO_CONTA_ATIVA`, ou `M17_FALHA_ENVIO`), `ativar` (GET: guarda o token em `request.session["token_ativacao"]` e redireciona para `definir_senha`) e `definir_senha` (lê o token da sessão; sem token → `LINK_SUBSTITUIDO`; mostra o formulário só em `VALIDO`, a tela de vencido em `VENCIDO`/`SEM_EMAIL`, ou a mensagem do estado; no POST válido chama `ativar_conta`, remove o token da sessão e redireciona para `entrar` com `CONTA_ATIVADA`); os templates `sigtcc/templates/cadastro/primeiro_acesso.html`, `primeiro_acesso_form.html`, `ativar.html`, `link_vencido.html` (aviso `LINK_ATIVACAO_VENCEU` e botão "Reenviar link de ativação" por POST) e `emails/ativacao.txt`; e as rotas `primeiro_acesso`, `primeiro_acesso_aluno`, `primeiro_acesso_email`, `ativar` e `definir_senha` (contracts/rotas.md). — Rastreabilidade: [US-10][RBN-CAD-06.1][RBN-CAD-06.2][RBN-CAD-06.3][FR-001]–[FR-005][FR-016]
- [ ] T026 [US1] Rodar `python manage.py test sigtcc.apps.cadastro.tests.test_us10_primeiro_acesso` até passar, e de novo `test_us11_login`. — Rastreabilidade: [US-10][SC-001][SC-006]

**Checkpoint**: primeiro acesso e login completos.

---

## Phase 5: User Story 6 - Base comum para as demais features (Priority: P1)

**Goal**: as outras features podem usar o layout, a verificação de perfil, a regra da Q27, as funções
de link e o comando de conta de teste.

**Independent Test**: página de exemplo restrita a um perfil é negada aos outros; telas com o layout;
link gerado fora das telas funciona; comando cria contas.

### Tests for User Story 6 ⚠️

- [ ] T027 [P] [US6] Criar `sigtcc/apps/cadastro/tests/test_base_comum.py` (com uma `urls` de teste via `override_settings(ROOT_URLCONF=...)` que declara views de exemplo com `@perfil_requerido("professor_disciplina")`, `@perfil_requerido("coordenador")` e uma que levanta `PermissionDenied` num serviço): `test_cenario1_sem_login_vai_ao_login_e_volta`, `test_cenario2_aluno_negado_pelo_endereco_direto` (403 com `M02_ACESSO_NEGADO`, sem dados), `test_cenario3_coordenador_permitido_e_docente_negado`, `test_cenario4_layout` (parte disponível nesta fase: barra superior, sino com contagem, "Sair", menu lateral e `sigtcc.css` no HTML; "Meu perfil" e o link do sino são conferidos em T039), `test_cenario5_link_gerado_fora_das_telas`, `test_q27_professor_so_de_turma_arquivada` (`"professor_disciplina" in papeis(...)` e `professor_com_turma_ativa(...)` falso), `test_papeis_calculados_uma_vez` (`assertNumQueries` na segunda chamada), `test_contexto_anonimo_sem_consulta` (`assertNumQueries(0)` no processador), `test_menu_filtra_por_perfil` e `test_permission_denied_em_servico_usa_handler403`. — Rastreabilidade: [FR-024][FR-025][FR-026][Q27][RBN-CAD-04.5][SC-004][SC-007]
- [ ] T028 [P] [US6] Criar `sigtcc/apps/cadastro/tests/test_criar_conta_teste.py` (com `override_settings(DEBUG=True)`): `test_cenario6_conta_pelo_shell` (história 6, cenário 6: cria cada perfil, 'Aguardando Ativação' e 'Ativa', e a conta criada entra pelo login quando 'Ativa'); `--turma` reaproveita a turma existente e matricula o aluno; `--professor` define o `tur_doc`; `--arquivada` cria turma 'Arquivada'; coordenador repetido no curso é recusado; com `DEBUG=False` o comando recusa. — Rastreabilidade: [FR-027][infraestrutura de teste da feature 003]

### Implementation for User Story 6

- [ ] T029 [US6] Rodar `python manage.py test sigtcc.apps.cadastro.tests.test_base_comum sigtcc.apps.cadastro.tests.test_criar_conta_teste` e corrigir `permissoes.py`, `contexto.py`, `menu.py`, `views.py`, os templates base e o comando até passar. — Rastreabilidade: [FR-024]–[FR-027][SC-004]

**Checkpoint**: base comum pronta para as outras features.

---

## Phase 6: User Story 3 - Reenviar o link de ativação vencido [US-37] (Priority: P2)

**Goal**: link vencido oferece o reenvio; o novo link invalida o anterior.

**Independent Test**: gerar um link, avançar o relógio em mais de 24 horas, reenviar e ativar pelo
link novo; o antigo não ativa.

### Tests for User Story 3 ⚠️

- [ ] T030 [US3] Criar `sigtcc/apps/cadastro/tests/test_us37_reenvio.py` com `test_cenario1` a `test_cenario5` da história 3 da spec (o 5 com a conta resetada: tela de vencido e, no clique, `M08_REFAZER_PRIMEIRO_ACESSO`, sem e-mail enviado); mais `test_reenvio_so_em_vencido` (POST com link válido, substituído, inativo ou ativo não reenvia e leva à tela do estado), `test_reenvio_sem_token_na_sessao` (`LINK_SUBSTITUIDO`), `test_falha_no_envio_do_reenvio` (`M17_FALHA_ENVIO`, link anterior intacto) e `test_token_sai_da_sessao_depois_do_reenvio`. — Rastreabilidade: [US-37][RBN-CAD-06.9][FR-016]–[FR-018][Q5][Q13]

### Implementation for User Story 3

- [ ] T031 [US3] Acrescentar em `sigtcc/apps/cadastro/services.py` `reenviar_link_ativacao(token)`: com a conta travada, só reenvia no estado `VENCIDO` (chama `enviar_link_ativacao`); em `SEM_EMAIL` devolve o estado sem enviar; nos demais, devolve o estado. — Rastreabilidade: [US-37][RBN-CAD-06.9][FR-017][FR-018]
- [ ] T032 [US3] Criar em `sigtcc/apps/cadastro/views.py` a view `reenviar_link` (só POST; lê o token da sessão; mostra `NOVO_LINK_ENVIADO`, `M08_REFAZER_PRIMEIRO_ACESSO`, `M17_FALHA_ENVIO` ou leva à tela do estado; remove o token da sessão ao terminar), ajustar `sigtcc/templates/cadastro/link_vencido.html` para mostrar o resultado e acrescentar a rota `reenviar_link` (`/primeiro-acesso/reenviar/`). — Rastreabilidade: [US-37][RBN-CAD-06.9][FR-017][FR-018]
- [ ] T033 [US3] Rodar `python manage.py test sigtcc.apps.cadastro.tests.test_us37_reenvio` e `test_us10_primeiro_acesso` até passar. — Rastreabilidade: [US-37][SC-006]

---

## Phase 7: User Story 4 - Recuperar ou alterar a senha [US-12] (Priority: P2)

**Goal**: alterar a senha logado, redefinir por "Esqueci minha senha" e resetar o primeiro acesso de um
aluno.

**Independent Test**: alterar a senha; pedir e usar o link de redefinição; resetar o primeiro acesso
como Professor de turma ativa do aluno.

### Tests for User Story 4 ⚠️

- [ ] T034 [US4] Criar `sigtcc/apps/cadastro/tests/test_us12_senha.py` com `test_cenario1` a `test_cenario8` da história 4 da spec (com `captureOnCommitCallbacks(execute=True)` para o e-mail de redefinição); mais `test_q19_troca_derruba_outras_sessoes` (dois clientes logados; depois da troca, o outro é levado ao login e o atual continua), `test_q19_redefinicao_derruba_todas`, `test_link_de_redefinicao_usado_e_substituido` (`LINK_INVALIDO_OU_VENCIDO`), `test_q26_redefinicao_em_conta_inativa_ou_expirada` (`M15`/`M16`, senha não muda; conferido no GET e no POST), `test_esqueci_sempre_generica` (e-mail inexistente, conta aguardando, conta ativa e falha no envio: mesma mensagem), `test_esqueci_formato_invalido` (`M10_EMAIL_INVALIDO`), `test_q9_professor_de_turma_arquivada_ve_tela_sem_botao`, `test_q27_reset_recusado_sem_turma_ativa` (POST direto: 403), `test_coordenador_sem_turma_nao_abre_tela_do_aluno` (403) e `test_reset_invalida_links_e_sessoes_do_aluno`. — Rastreabilidade: [US-12][RBN-CAD-06.5][RBN-CAD-06.7][RBN-CAD-06.8][FR-012]–[FR-015][Q9][Q19][Q26][Q27]

### Implementation for User Story 4

- [ ] T035 [US4] Acrescentar em `sigtcc/apps/cadastro/services.py` (research A3, A5, A16): `alterar_senha(usuario, atual, nova)` (confere `check_password`, grava `set_password`, evento `SENHA_ALTERADA`); `gerar_link_redefinicao(usuario)` (grava `usu_link_gerado_em`; assina `usu_id`, `gerado_em` e `resumo_senha` = HMAC de 12 caracteres do hash da senha, salt `sigtcc.redefinicao`); `enviar_link_redefinicao(email) -> None` (recebe o e-mail digitado na tela, como no contrato §4; normaliza; só para conta 'Ativa' com validade em dia gera o link e envia o `emails/redefinicao.txt` em `transaction.on_commit`, numa `threading.Thread` sem acesso ao banco, ou na própria requisição se `SIGTCC_EMAIL_SINCRONO`; falha só no log); `validar_link_redefinicao(token)` (`ADULTERADO` → `INATIVA` → `EXPIRADA` → `SUBSTITUIDO`, inclusive senha trocada → `VENCIDO` → `VALIDO`); `redefinir_senha(token, nova)` (revalida com a conta travada; grava; evento `SENHA_REDEFINIDA`); e `resetar_primeiro_acesso(professor, aluno)` (conta travada; `pode_resetar_primeiro_acesso` senão `PermissionDenied`; `usu_email = None`, `password = None`, `usu_status = "Aguardando Ativação"`, `usu_link_gerado_em = timezone.now()`; evento `RESET_PRIMEIRO_ACESSO` com `autor`). — Rastreabilidade: [US-12][RBN-CAD-06.5][RBN-CAD-06.7][RBN-CAD-06.8][FR-012]–[FR-015][Q19][Q26][Q27][I1][I4]
- [ ] T036 [US4] Acrescentar em `sigtcc/apps/cadastro/forms.py`: `AlterarSenhaForm` (`senha_atual` mascarada de 8 a 64 caracteres, `nova_senha` com `RegraSenhaSigtcc`, `confirmacao`; `SENHAS_NAO_CONFEREM`), `EsqueciSenhaForm` (`email` com `M10_EMAIL_INVALIDO`) e `NovaSenhaForm` (igual ao `AtivacaoForm`). — Rastreabilidade: [US-12][RBN-CAD-06.5][RBN-CAD-06.7][FR-012][FR-013][FR-014]
- [ ] T037 [US4] Criar em `sigtcc/apps/cadastro/views.py` as views `alterar_senha` (`@perfil_requerido()`; `update_session_auth_hash` depois de gravar; `SENHA_ALTERADA` ou `SENHA_ATUAL_INCORRETA`), `esqueci_senha` (sempre `ESQUECI_GENERICA` com formato válido), `redefinir_senha` (GET: token na sessão e redireciona para `nova_senha`), `nova_senha` (sem token → `LINK_INVALIDO_OU_VENCIDO`; estados inativa/expirada → `M15`/`M16`; POST válido → redefine, remove o token e leva ao login), `aluno` (`@perfil_requerido("professor_disciplina")`; mostra nome, matrícula, e-mail e Status da Conta; botão só se `pode_resetar_primeiro_acesso`) e `resetar_primeiro_acesso` (GET: confirmação com `M12_CONFIRMAR_RESET`; POST: serviço e `M13_RESET_CONCLUIDO`); os templates `sigtcc/templates/cadastro/alterar_senha.html`, `esqueci_senha.html`, `redefinir_senha.html`, `aluno.html`, `confirmar_reset.html` e `emails/redefinicao.txt`; e as rotas `alterar_senha`, `esqueci_senha`, `redefinir_senha`, `nova_senha`, `aluno` e `resetar_primeiro_acesso` (contracts/rotas.md). — Rastreabilidade: [US-12][RBN-CAD-06.5][RBN-CAD-06.7][RBN-CAD-06.8][FR-012]–[FR-015]
- [ ] T038 [US4] Rodar `python manage.py test sigtcc.apps.cadastro.tests.test_us12_senha` até passar, e de novo as fases 3 a 6. — Rastreabilidade: [US-12][SC-001]

---

## Phase 8: User Story 5 - Editar o perfil e ver as notificações [US-38] (Priority: P3)

**Goal**: cada perfil edita só os campos permitidos; central de notificações com contador.

**Independent Test**: editar a assinatura do Docente e a titulação do Membro Externo; trocar o e-mail
do Aluno com confirmação; abrir notificações criadas pelo shell.

### Tests for User Story 5 ⚠️

- [ ] T039 [US5] Criar `sigtcc/apps/cadastro/tests/test_us38_perfil_notificacoes.py` com `test_cenario1` a `test_cenario11` da história 5 da spec (o 9 na variante "item removido": `not_link_tela` que não resolve; Q10); mais `test_q28_confirmacao_em_duas_etapas` (GET não troca; POST troca e mostra `M07_EMAIL_ATUALIZADO`), `test_q28_email_ocupado_na_confirmacao` (`M05_EMAIL_EM_USO`), `test_q11_so_m06_ao_salvar_com_troca`, `test_link_de_troca_vencido_e_depois_de_outra_troca` (`M09`), `test_assinatura_disfarcada` (arquivo `.png` com bytes de PDF: `M04`), `test_assinatura_so_do_proprio_usuario` (rota `assinatura`; sem login → login; nenhuma URL pública em `/media/`), `test_assinatura_anterior_apagada`, `test_falha_no_envio_da_troca_desfaz_tudo` (`M17`, nada salvo), `test_notificacoes_paginadas_de_20`, `test_link_externo_na_notificacao_nao_e_seguido`, `test_notificacao_de_outro_usuario_404`, `test_notificacoes_da_mais_recente_para_a_mais_antiga` (FR-022), `test_perfil_tem_link_alterar_senha` (FR-012) e `test_base_cenario4_layout_completo` (história 6, cenário 4: "Meu perfil" e o link do sino para a central na barra superior de uma página interna). — Rastreabilidade: [US-38][RBN-CAD-13.1][RBN-CAD-13.2][FR-019]–[FR-023][Q10][Q11][Q14][Q24][Q28][I6][I7]

### Implementation for User Story 5

- [ ] T040 [US5] Acrescentar em `sigtcc/apps/cadastro/services.py` (research A4, A11, A12): `salvar_assinatura(usuario, arquivo)` (até 2 MB; tipo pelos bytes iniciais, PNG `\x89PNG\r\n\x1a\n` ou JPEG `\xff\xd8\xff`; extensão coerente; grava com `default_storage` em `assinaturas/<usu_id>_<aleatório>.<ext>`; caminho relativo a `MEDIA_ROOT`; apaga o anterior em `transaction.on_commit`); `atualizar_perfil(usuario, dados, arquivo)` (só os campos do papel, FR-019; se o e-mail mudar, chama `pedir_troca_email` na mesma transação); `pedir_troca_email(usuario, novo)` (formato, domínio no Aluno, `email_em_uso`; assina `usu_id`, `resumo_email_atual`, `novo_email`, `emitido_em` com salt `sigtcc.troca_email`; envia `emails/confirmar_email.txt`; falha → desfaz tudo; evento `TROCA_EMAIL_PEDIDA`); `validar_link_troca_email(token)` e `confirmar_troca_email(token)` (conta travada; 24 h; e-mail atual ainda igual; novo e-mail livre, senão `M05`; `IntegrityError` → `M05`; evento `TROCA_EMAIL_CONFIRMADA`); `abrir_notificacao(usuario, not_id)` (404 se não for dele; marca lida; separa caminho e query de `not_link_tela`; só redireciona se `resolve` achar a rota e `url_has_allowed_host_and_scheme` aceitar; senão `ITEM_INDISPONIVEL`); `marcar_todas_lidas(usuario)`. — Rastreabilidade: [US-38][RBN-CAD-13.1][RBN-CAD-13.2][FR-019]–[FR-023][Q10][Q11][Q24][Q28][I6][I7]
- [ ] T041 [US5] Acrescentar em `sigtcc/apps/cadastro/forms.py`: `PerfilAlunoForm` (`email` institucional), `PerfilDocenteForm` (`assinatura` `FileField` opcional), `PerfilMembroExternoForm` (`email`, `titulacao` com `Titulacao.choices`, `instituicao` até 150 caracteres, `assinatura`); Secretaria sem formulário. Validações com `M10`, `M11`, `M05` e `M04`. — Rastreabilidade: [US-38][RBN-CAD-13.1][FR-019][FR-020][FR-021]
- [ ] T042 [US5] Criar em `sigtcc/apps/cadastro/views.py` as views `perfil` (`@perfil_requerido()`; campos do papel; Secretaria só leitura e sem "Salvar"; link "Alterar senha" para `alterar_senha` (FR-012); `PERFIL_ATUALIZADO` ou só `M06` quando há troca de e-mail), `assinatura` (logado; `FileResponse` da própria imagem, com o tipo detectado), `confirmar_email` (GET mostra o novo e-mail e o botão "Confirmar novo e-mail"; POST confirma), `notificacoes` (ordenadas da mais recente para a mais antiga; `Paginator` de 20, `?pagina=`; `SEM_NOTIFICACOES` quando vazia), `abrir_notificacao` e `marcar_lidas` (POST); os templates `sigtcc/templates/cadastro/perfil.html`, `confirmar_email.html`, `notificacoes.html` e `emails/confirmar_email.txt`; as rotas `perfil`, `assinatura`, `confirmar_email`, `notificacoes`, `abrir_notificacao` e `marcar_lidas`; "Meu perfil" no menu do usuário e o link do sino para `notificacoes` em `sigtcc/templates/includes/barra_superior.html` (H1); e o item "Notificações" no menu (`menu.py`), se a equipe quiser além do sino. — Rastreabilidade: [US-38][RBN-CAD-13.1][RBN-CAD-13.2][FR-019]–[FR-023]
- [ ] T043 [US5] Rodar `python manage.py test sigtcc.apps.cadastro.tests.test_us38_perfil_notificacoes` até passar, e a suíte do app inteiro. — Rastreabilidade: [US-38][SC-001]

**Checkpoint**: as seis histórias completas.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: testes transversais, qualidade, roteiro manual e preparação do PR.

- [ ] T044 [P] Criar `sigtcc/apps/cadastro/tests/test_mensagens.py` (SC-002): para cada constante das US em `mensagens.py`, confere que o texto aparece entre aspas em `docs/fonte/Historias_de_Usuario_v3_2.md` (normalizando quebras de linha); para M-01 a M-17, lê a tabela "Mensagens a validar com a PO" de `specs/003-acesso-login/spec.md` e confere cada texto. — Rastreabilidade: [SC-002][Q25][US-10][US-11][US-12][US-37][US-38]
- [ ] T045 [P] Criar `sigtcc/apps/cadastro/tests/test_log_acesso.py` (SC-009, FR-029): com `assertLogs("sigtcc.acesso")`, cada um dos 6 tipos de evento (senha errada, bloqueio, troca e redefinição de senha, reset, pedido e confirmação de troca de e-mail) gera exatamente uma linha com conta e data; nenhuma linha contém a senha, o token, o link ou o e-mail completo; os eventos técnicos `EMAIL_DUPLICADO` (sem conta) e `FALHA_ENVIO_EMAIL` (só o tipo do erro) também são conferidos. — Rastreabilidade: [FR-029][SC-008][SC-009][Q21]
- [ ] T046 [P] Criar `sigtcc/apps/cadastro/tests/test_seguranca.py`: link de ativação e de redefinição usado duas vezes em POSTs seguidos (só o primeiro vale; I4); ativação concorrente com reset não deixa conta 'Ativa' sem e-mail; cookies de sessão `HttpOnly` e `SameSite=Lax`; `SECURE_REFERRER_POLICY == "same-origin"`; senha nunca aparece no HTML nem no log (SC-008); `authenticate()` do Django devolve `None` com credenciais corretas (research A1). Sessão (FR-011, C1): `SESSION_COOKIE_AGE == 3600`, `SESSION_SAVE_EVERY_REQUEST` e `SESSION_EXPIRE_AT_BROWSER_CLOSE` ligados e cookie de sessão sem `Max-Age`/`Expires`; com `avancar_relogio(minutos=61)` sem uso, a próxima página interna leva ao login; com 59 minutos, continua logado. Todas as páginas (SC-004, C2): percorre as rotas internas de `specs/003-acesso-login/contracts/rotas.md` (`painel`, `perfil`, `assinatura`, `alterar_senha`, `notificacoes`, `abrir_notificacao`, `marcar_lidas`, `aluno`, `resetar_primeiro_acesso`, `sair`): sem login → `/entrar/?next=...`; e as restritas (`aluno`, `resetar_primeiro_acesso`) com Aluno, Secretaria e Membro Externo logados → 403 com `M02_ACESSO_NEGADO` e sem dados do aluno. — Rastreabilidade: [SC-004][SC-008][FR-011][FR-025][B1][B2][I4]
- [ ] T047 Conferir a rastreabilidade (constituição, princípio II): toda classe, função, template e teste novo em `sigtcc/apps/cadastro/` e `sigtcc/templates/` cita US, RBN ou FR. — Rastreabilidade: [infraestrutura da feature 003]
- [ ] T048 Rodar `lint.bat` (ou isort, black e flake8) duas vezes seguidas: a segunda não altera nada e o flake8 termina sem erros em `sigtcc/`. — Rastreabilidade: [infraestrutura da feature 003]
- [ ] T049 Rodar `python manage.py test sigtcc.apps.cadastro sigtcc.apps.defesa` em banco de teste novo (inclui os 53 testes da feature 001) e `python manage.py makemigrations --check --dry-run` (nenhuma migração nova, FR-028). — Rastreabilidade: [SC-001][FR-028]
- [ ] T050 Executar o roteiro de `specs/003-acesso-login/quickstart.md` do zero (seção 1 a 3): cronometrar o primeiro acesso (SC-003) e preencher o checklist de revisão visual em 360, 768 e 1280 px (SC-007); corrigir o quickstart se algum resultado esperado estiver diferente. — Rastreabilidade: [SC-003][SC-007][Q16][Q22]
- [ ] T051 Atualizar `CHANGELOG.md` com a entrega da feature 003 e as pendências abertas do índice (Q-01, Q-09, Q-23, Q-27 a Q-32; IDs do índice, não das Clarifications da spec). — Rastreabilidade: [infraestrutura da feature 003]
- [ ] T052 Preparar o texto do PR em `specs/003-acesso-login/pr-feat-02.md` com o template do PGCS 6.3, título `[Feat-02] Acesso e Login (US-10, US-11, US-12, US-37, US-38)`, usando o agente `revisor-pgcs` para o checklist, e listar os itens de configuração para o Célio (índice Q-23 e Q-27). Não fazer push nem abrir o PR sem pedido da responsável. — Rastreabilidade: [infraestrutura da feature 003]

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 → T002 → T003.
- **Foundational (Phase 2)**: depende do Setup; bloqueia todas as histórias. T004, T005, T006, T009,
  T010 e T011 em paralelo; T007 depende de T006; T008 depende de T004; T012 depende de T009 e T010;
  T013 depende de T007 e T012; T014 depende de T004; T015 e T016 por último. A barra superior só
  ganha links de rotas já criadas: "Sair" em T020 (fase 3), "Meu perfil" e o link do sino em T042
  (fase 8); o cenário 4 da história 6 é conferido em parte em T027 e completado em T039.
- **US2 (Phase 3)**: depende da Foundational. É o MVP.
- **US1 (Phase 4)**: depende da US2 (o fim da ativação leva ao login).
- **US6 (Phase 5)**: depende da US1 (o cenário 5 usa a geração de link).
- **US3 (Phase 6)**: depende da US1 (reenvio sobre o link de ativação).
- **US4 (Phase 7)**: depende da US2 (alterar senha exige login) e reaproveita os links da US1.
- **US5 (Phase 8)**: depende da US2 (perfil exige login).
- **Polish (Phase 9)**: depende de todas.

### User Story Dependencies

- US2 independente (depois da base); US1 usa o login; US3 usa a US1; US4 usa a US2 e a US1; US5 usa a
  US2; US6 confere o que a base e a US1 entregam.
- `views.py`, `services.py`, `forms.py` e `urls.py` são compartilhados: as tarefas de implementação
  das histórias são sequenciais entre si.

### Within Each User Story

- Testes escritos antes e falhando; depois serviço, formulário, view, template e rota; por fim rodar.
- Commit ao fim de cada fase, só com os testes da fase e das anteriores passando.

### Parallel Opportunities

- Foundational: T004, T005, T006, T009, T010, T011.
- US6: T027 e T028.
- Polish: T044, T045, T046.

---

## Parallel Example: Foundational

```bash
Task: "T004 mensagens.py"
Task: "T005 validators.py"
Task: "T006 backends.py"
Task: "T009 menu.py e contexto.py"
Task: "T010 sigtcc.css"
Task: "T011 sigtcc.js"
```

## Parallel Example: Polish

```bash
Task: "T044 test_mensagens.py"
Task: "T045 test_log_acesso.py"
Task: "T046 test_seguranca.py"
```

---

## Implementation Strategy

### MVP First (User Story 2 Only)

1. Fases 1 e 2 (configuração, base visual, permissões, conta de teste).
2. Fase 3 (US2): login, bloqueio e saída, com contas criadas por `criar_conta_teste`.
3. **Parar e validar**: `test_us11_login` verde; login manual pelo quickstart. Commit sugerido:
   `feat(feat-02): implementar login com bloqueio por tentativas`.

### Incremental Delivery

1. Setup + Foundational → `chore(feat-02): configurar sessao, email, cache e log do login` e
   `feat(feat-02): adicionar base visual, permissoes e conta de teste`.
2. US2 → login (MVP).
3. US1 → `feat(feat-02): implementar primeiro acesso com link de ativacao`.
4. US6 → `test(feat-02): cobrir a base comum e o comando de conta de teste`.
5. US3 → `feat(feat-02): reenviar link de ativacao vencido`.
6. US4 → `feat(feat-02): recuperar e alterar senha e resetar primeiro acesso`.
7. US5 → `feat(feat-02): editar perfil e mostrar notificacoes`.
8. Polish → `test(feat-02): ...` e `docs(feat-02): ...`.

---

## Notes

- [P] = arquivos diferentes, sem dependência de tarefa incompleta.
- As 17 mensagens provisórias não bloqueiam as tarefas (spec Q25); quando a PO validar (Q-01), trocar
  só as constantes de `mensagens.py` e a tabela da spec.
- Nenhuma tarefa cria tabela, coluna ou migração (FR-028).
- Pendências fora desta feature estão em [plan.md](plan.md) ("Pendências") e no índice
  [docs/questoes-a-rever.md](../../docs/questoes-a-rever.md).
