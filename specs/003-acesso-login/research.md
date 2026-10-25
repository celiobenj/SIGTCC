# Research: Acesso e Login do SIGTCC

**Feature**: [spec.md](spec.md) (aprovada em 2026-10-20) | **Plano**: [plan.md](plan.md) | **Data**: 2026-10-20

Formato: Decisão / Justificativa / Alternativas. As decisões partem do que a spec 001 já fixou
(`specs/001-modelo-dados/research.md`: D1 `Usuarios` como usuário do Django sem colunas extras, D2
bloqueio no cache, R1 `USE_TZ = False`) e das Clarifications Q1 a Q28 da spec 003. Nenhuma decisão
cria tabela ou coluna (FR-028).

**Revisão de 2026-10-20**: o agente `arquiteto-django` revisou este plano. Os achados B1 (decidido
na spec, Q26), B2, I1 a I10 e os 20 menores foram aplicados com aprovação de Julia Cohen; o I8 foi
decidido na spec (Q27) e o I6 também passou pela spec (Q28). Cada correção cita o achado entre
colchetes, por exemplo [B2].

---

## A1. Login com ordem própria de verificação (FR-007 a FR-010; Q12, Q4, Q17)

**Decisão**: a regra do login fica em `services.autenticar(credencial, senha)`, que devolve um
resultado com um dos estados abaixo, avaliados exatamente nesta ordem (FR-008). A view só traduz o
estado em mensagem e chama `django.contrib.auth.login(request, usuario, backend="sigtcc.apps.cadastro.backends.SigtccBackend")` [m8].

1. `VAZIO`: credencial ou senha em branco.
2. Busca da conta: credencial com exatamente 10 dígitos → `Alunos.alu_matricula`; senão
   `Usuarios.usu_email__iexact` (Q13). Mais de uma conta com o mesmo e-mail (diferença só de
   maiúsculas) → registra `EMAIL_DUPLICADO` no log e trata como não encontrada [I3]. Sem conta →
   `NAO_ENCONTRADA`, **depois de calcular um hash fictício da senha recebida** (como o `ModelBackend`
   faz com `UserModel().set_password(senha)`), para o tempo de resposta não revelar se a conta existe
   [I1].
3. `AGUARDANDO`: conta 'Aguardando Ativação', sem conferir senha.
4. `BLOQUEADA` (com minutos restantes): bloqueio vigente (A2).
5. Senha: fora de 8 a 64 caracteres ou incorreta → `SENHA_INCORRETA` e conta a tentativa (Q17); na
   terceira falha seguida o resultado já é `BLOQUEADA`, com a M-01 (US-11, cenário 5) [m8].
6. Com a senha correta: confere o bloqueio **de novo** (outra requisição pode tê-lo gravado
   enquanto a senha era conferida) [I2]; se não houver bloqueio, apaga o contador (FR-009: a senha
   correta zera o contador, qualquer que seja o status) e devolve `INATIVA`, `EXPIRADA` (status
   'Expirada' ou Membro Externo com `mem_validade_ate < timezone.now().date()`, Q4) [m1] ou `OK`.

Usuário já logado que abre `/entrar/` é levado ao painel [m8].

**Redirecionamento depois do login [B2]**: o `next` vem num campo oculto do formulário, preservado
quando há erro, e só é usado se `url_has_allowed_host_and_scheme(next, allowed_hosts={request.get_host()}, require_https=request.is_secure())`
for verdadeiro; senão, o destino é o painel. Testes com `next` externo (`https://outro.site/`) e
`//outro.site`.

**Backend [m9]**: `sigtcc/apps/cadastro/backends.py` com `SigtccBackend(ModelBackend)`, o único em
`AUTHENTICATION_BACKENDS`. `authenticate()` devolve sempre `None`, para que nem `authenticate()` nem
`Client.login()` pulem a ordem e o bloqueio (os testes usam `force_login`). `get_user()` carrega o
usuário com `select_related` das quatro especializações (`alunos`, `docentes`, `membrosexternos`,
`secretarios`) numa consulta só [I9], e `user_can_authenticate` exige `usu_status == 'Ativa'` **e**
validade não vencida, para uma conta inativada ou expirada perder a sessão na próxima página.

**Justificativa**: o `authenticate()` padrão só diz "deu certo" ou "não deu", e a US-11 exige seis
mensagens numa ordem fixa.

**Alternativas**: `LoginView` com `AuthenticationForm` (uma mensagem só, sem ordem configurável).

## A2. Bloqueio por tentativas num cache próprio (FR-009; spec 001 D2; Q16)

**Decisão [I2]**:
- Alias de cache próprio, `CACHES["acesso"]`: `FileBasedCache` numa pasta própria, `CACHE_ACESSO_DIR`
  do `.env` (padrão `cache_acesso`, ao lado da pasta do cache padrão, não dentro dela, e fora do Git),
  com `OPTIONS={"MAX_ENTRIES": 100000}`. O padrão do Django (300 entradas) apaga ao acaso um terço dos
  arquivos quando passa do limite, o que faria bloqueios vigentes sumirem. É item de configuração
  para o Célio (Q-27 do índice).
- Chaves: `acesso:falhas:<usu_id>` (contador) e `acesso:bloqueio:<usu_id>` (instante do fim do
  bloqueio, em ISO). A lógica compara o instante gravado com `timezone.now()`; o tempo de vida das
  chaves (24 h e 16 min) serve só para limpeza, e os testes avançam o relógio com `patch` em
  `django.utils.timezone.now` sem depender do relógio do cache.
- Na terceira falha seguida, o bloqueio é gravado com `cache.add` (não sobrescreve um bloqueio já
  gravado por requisição paralela) e o contador é zerado. A senha correta, fora do bloqueio, apaga o
  contador. A conferência do bloqueio é repetida depois da senha correta (A1, passo 6).
- "N" da M-01: `ceil(segundos_restantes / 60)`, no mínimo 1 (Q16).

**Risco residual aceito**: o contador não é atômico no cache em arquivo; muitas requisições em
paralelo podem somar algumas tentativas além de 3 antes do bloqueio. A conferência dupla impede que
alguma delas entre com a conta já bloqueada.

**Alternativas**: `django-axes` (cria tabelas); colunas em `Usuarios` (fora do dicionário); Redis
(serviço extra).

## A3. Links assinados, sem tabela (FR-006, FR-014, FR-016 a FR-018, FR-021, FR-026; dicionário, seção 4, itens 2 e 3)

**Decisão**: os links usam `django.core.signing.dumps/loads` com a `SECRET_KEY` e um `salt` por tipo.
A idade é calculada **só** pelo instante que vem no link contra `timezone.now()`; `max_age` do
`signing` não é usado, porque ele lê `time.time()` [m1].

| Tipo | Salt | Conteúdo assinado | Validade e invalidação |
|---|---|---|---|
| Ativação | `sigtcc.ativacao` | `usu_id`, `gerado_em` (= `usu_link_gerado_em` relido do banco, ISO com microssegundos) [m2] | 24 h a partir de `gerado_em`; substituído quando `usu_link_gerado_em` muda (novo pedido, reenvio, reset) |
| Redefinição de senha | `sigtcc.redefinicao` | `usu_id`, `gerado_em`, `resumo_senha` (HMAC de 12 caracteres do hash atual da senha) [m3] | 24 h; substituído quando `usu_link_gerado_em` muda; usado quando a senha muda por qualquer caminho (o `resumo_senha` deixa de bater) |
| Troca de e-mail | `sigtcc.troca_email` | `usu_id`, `resumo_email_atual` (HMAC do e-mail atual) [m4], `novo_email`, `emitido_em` | 24 h (Q11); deixa de valer quando o e-mail da conta muda (A4; spec Q24) |

Gerar um link de ativação ou de redefinição grava `usu_link_gerado_em = timezone.now()`; gravar a
senha **não** altera essa coluna (ela continua sendo "o momento do último link gerado", como no
dicionário) [m3].

**Estados do link de ativação** (FR-016, Q5, Q23, Q26), avaliados nesta ordem:
`ADULTERADO` → `ATIVA` → `INATIVA` → `EXPIRADA` (status ou validade) → `SEM_EMAIL` → `SUBSTITUIDO` →
`VENCIDO` → `VALIDO`. `VALIDO` exige `usu_status == 'Aguardando Ativação'` [B1].

**Estados do link de redefinição**: `ADULTERADO` → `INATIVA` → `EXPIRADA` → `SUBSTITUIDO` (inclusive
senha já trocada) → `VENCIDO` → `VALIDO`, que exige conta 'Ativa' e validade não vencida, conferido
no GET e de novo no POST [B1]. Conta 'Aguardando Ativação' (resetada depois do pedido) cai em
`SUBSTITUIDO`, porque o reset atualiza `usu_link_gerado_em`.

**Token fora da URL depois de aberto [m5]**: o GET com o token valida, guarda o token na sessão e
redireciona para uma URL fixa sem ele (`/primeiro-acesso/definir-senha/` e
`/redefinir-senha/nova/`), como faz o `PasswordResetConfirmView` do Django. Assim o token não fica no
histórico do navegador nem no `Referer`. Sem token na sessão (acesso direto à URL fixa ou sessão
vencida), as telas `definir_senha`, `nova_senha` e `reenviar_link` tratam o caso como `ADULTERADO`. O
token sai da sessão assim que a ativação, a redefinição ou o reenvio terminam. `SECURE_REFERRER_POLICY = "same-origin"` (padrão do Django)
fica declarado no `settings.py` e não pode ser afrouxado. O log de acesso do servidor web ainda grava
a primeira URL com o token; isso fica fora do FR-029 e vai como observação para a configuração do
servidor (Q-27 do índice).

**Alternativas**: `PasswordResetTokenGenerator` (não distingue vencido de substituído e depende de
`last_login`, que não existe, D1); tabela de tokens (fora do dicionário).

## A4. Link de troca de e-mail (Q11; spec Q24 e Q28)

**Decisão** (aceita por Julia Cohen em 2026-10-20; Q-21 do índice, spec Q24): o link de troca não usa
`usu_link_gerado_em`, para não invalidar um link de redefinição pendente. Ele carrega um resumo do
e-mail atual e só vale enquanto a conta ainda tiver esse e-mail; quando uma troca é confirmada, os
outros links pendentes deixam de valer. Sem confirmação, os links pendentes valem; o primeiro
confirmado vence.

**Confirmação em duas etapas [I6; spec Q28]**: o GET mostra o novo e-mail e o botão "Confirmar novo
e-mail"; só o POST troca. No POST, dentro de `transaction.atomic()` com `select_for_update()` na
conta, o serviço revalida o link e confere de novo se o novo e-mail continua livre (`iexact`); se não
estiver, M-05. Um `IntegrityError` do banco também vira M-05.

**Limitação aceita por Julia Cohen em 2026-10-20 [m4]**: na sequência A → B → A, um link antigo para B volta a valer enquanto as
24 h não passarem, porque o e-mail atual é de novo A. O novo e-mail aparece legível no link; ele vai
justamente para esse endereço, então não há vazamento além do próprio destinatário.

## A5. Envio de e-mail (FR-002, FR-013, FR-017, FR-021; Q13)

**Decisão**:
- `django.core.mail.send_mail` com o backend do `.env` (`EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`,
  `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL`) e
  `EMAIL_TIMEOUT = 10` segundos [I5]. Em desenvolvimento, `console.EmailBackend`.
- **Primeiro acesso, reenvio e troca de e-mail [I5]**: gerar o link, gravar (`usu_link_gerado_em` e,
  no Aluno, o e-mail) e enviar acontecem dentro de um `transaction.atomic()`; se o envio falhar, a
  transação é desfeita (o link anterior continua valendo, o e-mail do Aluno não fica gravado) e aparece
  a M-17. Na troca de e-mail feita junto com outros campos do perfil, a falha desfaz o salvamento
  inteiro [m13].
- **"Esqueci minha senha" [I1]**: a resposta é sempre a mensagem genérica. Para conta 'Ativa', o link
  é gerado na requisição e o e-mail sai em `transaction.on_commit`, numa `threading.Thread` sem acesso
  ao banco, para o tempo de resposta não depender do servidor de e-mail. Falha nesse envio só vai para
  o log. Nos testes, o setting `SIGTCC_EMAIL_SINCRONO = True` faz esse envio acontecer na própria
  requisição (sem thread), e os testes usam `captureOnCommitCallbacks(execute=True)` para o
  `mail.outbox` estar preenchido na asserção; em produção o setting fica `False`.
- Textos dos e-mails em `templates/cadastro/emails/`. Links absolutos com `SITE_URL` do `.env`, que
  inclui o subcaminho se a aplicação for publicada fora da raiz [m18].
- Exceções de envio são registradas só pelo tipo (por exemplo `SMTPRecipientsRefused`), nunca com a
  mensagem, que pode trazer o endereço [m12].

**Alternativas**: fila de tarefas (Celery, por exemplo): serviço extra; fica como evolução se o envio
em thread não bastar.

## A6. Sessão (FR-011; Q18, Q19)

**Decisão**: sessões no banco (`django_session`, do framework) com `SESSION_COOKIE_AGE = 3600`,
`SESSION_SAVE_EVERY_REQUEST = True` (janela deslizante de 60 minutos), `SESSION_EXPIRE_AT_BROWSER_CLOSE =
True`, `SESSION_COOKIE_HTTPONLY = True` e `SESSION_COOKIE_SAMESITE = "Lax"` [m11].
`SESSION_COOKIE_SECURE` e `CSRF_COOKIE_SECURE` vêm do `.env` (`COOKIES_SEGUROS`, `True` em produção
com HTTPS); ligados num servidor só HTTP, impediriam o login [m11].

Q19 sem código extra: o Django guarda na sessão um resumo da senha (`get_session_auth_hash`, que
funciona com senha nula). Quando a senha muda, toda sessão com o resumo antigo deixa de valer; em "Meu
perfil", `update_session_auth_hash` mantém a atual. Uma conta inativada, expirada ou resetada perde a
sessão pelo `user_can_authenticate` (A1).

**Limitações e operação [m11]**: navegadores que restauram abas podem manter o cookie depois de
fechados; o limite de 60 minutos no servidor cobre esse caso. Sessões vencidas são apagadas pelo
`python manage.py clearsessions`, a agendar no servidor (Q-27).

## A7. Verificação de perfil reutilizável (FR-025; RNF do RAN-CAD-01 e RAN-CAD-02; spec Q27)

**Decisão**: módulo `sigtcc/apps/cadastro/permissoes.py`:
- `tipo_conta(usuario)`: `"aluno"`, `"docente"`, `"secretaria"`, `"membro_externo"` ou `None` (conta
  sem especialização, que não acessa nenhuma página com perfil declarado) [I9]. Usa as relações já
  carregadas pelo `get_user` (A1).
- `papeis(usuario)`: conjunto calculado **só quando usado** e guardado no próprio objeto do usuário
  da requisição (`usuario._papeis_cache`) [I9]:
  - `"coordenador"`: aparece em `Coordenadores.cor_doc`;
  - `"professor_disciplina"`: é `tur_doc` de **pelo menos uma turma, ativa ou arquivada** (spec Q27)
    [I8];
  - `"orientador"`: `Orientacoes` com `ori_status = 'Ativa'`;
  - `"coorientador"`: `Coorientacoes` com `coo_doc` e `coo_status = 'Ativa'`.
- `professor_com_turma_ativa(professor, aluno=None)`: regra compartilhada da Q27 para **ações que
  alteram dados**, com base no RBN-CAD-04.5 (turma arquivada "não recebe movimentação"). `professor`
  é o `Usuarios` logado (com `Docentes`); `aluno`, quando informado, é uma instância de `Alunos`. É
  verdadeiro se o professor é `tur_doc` de uma turma com `tur_status = 'Ativa'` (e, com `aluno`, se o
  aluno está matriculado nela). `pode_resetar_primeiro_acesso(professor, aluno)` usa os mesmos tipos.
- `@perfil_requerido(*perfis)` e `PerfilRequeridoMixin`: sem argumentos, exige só estar logado [I9];
  sem login, redireciona para `LOGIN_URL` com `?next=`; sem permissão, levanta `PermissionDenied`,
  que o `handler403` de `sigtcc/urls.py` mostra com `acesso_negado.html` e a M-02 [I9].
- Os papéis são **globais** ("tem alguma orientação ativa"), não por objeto: cada feature confere,
  no seu `services.py`, o vínculo com o TCC, a defesa ou a turma que está sendo acessada [I9].

**Alternativas**: grupos e permissões do Django (não existem, D1); checagem em cada view.

## A8. Menu lateral e sino (FR-022, FR-024, FR-025)

**Decisão [I9]**:
- Cada app que tem itens de menu expõe `menu.py` com a lista `ITENS` (dicionários com `rotulo`,
  `icone` do Material Symbols, `rota` = **nome** da URL, `perfis`, `ordem` e `secao` opcional, que
  agrupa os itens sob um título no menu). O processador de contexto `menu`, em
  `sigtcc/apps/cadastro/contexto.py`, percorre `apps.get_app_configs()`, junta os `ITENS`, filtra
  pelos perfis do usuário e resolve as rotas com `reverse` na hora de renderizar. Não depende da ordem
  do `ready()` nem duplica itens.
- `notificacoes_nao_lidas`: contagem de `Notificacoes` com `not_lida = false`.
- Para visitante anônimo, os dois processadores devolvem vazio sem consultar o banco.

## A9. Formulários com o primeiro erro e mensagens exatas (FR-003, FR-004, M-14; Q12)

**Decisão**: `forms.py` com a classe base `FormularioPrimeiroErro`, que valida os campos na ordem
declarada e mantém só o erro do primeiro campo com problema; cada campo valida formato, existência e
status nessa ordem. As mensagens vêm de `mensagens.py`, com as constantes das US (texto exato) e das
M-01 a M-17 (com o ID no nome, por exemplo `M01_BLOQUEIO`, e `ITEM_INDISPONIVEL` para "Este item não
está mais disponível"). O uso de `FormularioPrimeiroErro` é opcional nas outras features [I9].

E-mail de Aluno informado no formulário "Docente, Secretaria ou Membro Externo" → "Dados não
encontrados. Procure o Professor da Disciplina ou a Secretaria", para não contornar a exigência de
turma [m7].

## A10. Regra de senha (FR-004, FR-012; Q17)

**Decisão**: `validators.py` com o validador próprio: 8 a 64 caracteres, ao menos um caractere de
`[A-Za-z]` e um de `[0-9]`; outros caracteres são aceitos. `AUTH_PASSWORD_VALIDATORS` passa a ter só
esse validador, para valer também quando outras features chamarem
`django.contrib.auth.password_validation.validate_password` (o `set_password` em si não valida).
Hasher padrão do Django (PBKDF2).

## A11. Imagem de assinatura (FR-019, FR-020; RBN-CAD-13.1; PGCS 3.4)

**Decisão [I7]**:
- `forms.FileField` (o modelo guarda só o caminho, `CharField(255)`). Validação: até 2 MB; o tipo é
  decidido pelos bytes iniciais (PNG ou JPEG) e a extensão do nome precisa bater com ele; senão, M-04.
- Gravação com `default_storage` em `assinaturas/<usu_id>_<aleatório>.<ext do tipo detectado>`; o
  caminho gravado no modelo é **relativo a `MEDIA_ROOT`** e se abre com `default_storage.open(caminho)`
  (é o que a Defesa usa para a Ata e a Folha). O arquivo anterior é apagado em
  `transaction.on_commit`.
- **As assinaturas não são publicadas por `MEDIA_URL`**, nem em desenvolvimento: a prévia em "Meu
  perfil" sai pela rota `assinatura` (logado, só a própria imagem), com `FileResponse` e o tipo
  detectado. `SECURE_CONTENT_TYPE_NOSNIFF = True` (padrão) fica declarado.
- Uploads grandes são barrados antes da aplicação pelo limite do servidor web (observação para a
  configuração do servidor, Q-27); no Django, `DATA_UPLOAD_MAX_MEMORY_SIZE` fica no padrão [m13].

**Alternativas**: Pillow (dependência nova); `ImageField` (mudaria a coluna).

## A12. Central de notificações (FR-022, FR-023; Q10, Q14)

**Decisão**:
- Lista com `Paginator` (20 por página), por `not_data_hora` decrescente. "Marcar como lidas" é POST.
- Abrir uma notificação é um GET em rota própria que marca a notificação como lida antes de
  redirecionar. É mudança de estado por GET, aceita porque só afeta o próprio usuário e corresponde ao
  clique da US-38 [m10].
- **Formato de `not_link_tela` [I9]**: caminho relativo começando com `/`, sem host, com query string
  opcional. A central separa o caminho da query, testa o caminho com `django.urls.resolve` e só
  redireciona se `url_has_allowed_host_and_scheme` aceitar o endereço; caminho que não resolve →
  `ITEM_INDISPONIVEL` na central.
- Para o caso "cancelado" (feature de Defesa, Q-12), o contrato expõe
  `services.item_indisponivel(request)`, que grava a mensagem e redireciona para a central.

## A13. Registro de eventos de acesso (FR-029; Q21)

**Decisão**: logger `sigtcc.acesso`, `RotatingFileHandler(delay=True)` com 5 arquivos de 5 MB em
`LOG_DIR/acesso.log`; `LOG_DIR` vem do `.env` (padrão `logs`) e a pasta é criada na inicialização se
não existir [m12]. `logs/` fica no `.gitignore` (Q-23).

`services.registrar_evento(evento, conta, autor=None, detalhe="")` [m20]: `evento` é um valor do
conjunto fechado `EventoAcesso` (`LOGIN_SENHA_INCORRETA`, `BLOQUEIO`, `SENHA_ALTERADA`,
`SENHA_REDEFINIDA`, `RESET_PRIMEIRO_ACESSO`, `TROCA_EMAIL_PEDIDA`, `TROCA_EMAIL_CONFIRMADA`,
`EMAIL_DUPLICADO`, `FALHA_ENVIO_EMAIL`); `conta` e `autor` são instâncias de `Usuarios` (gravadas
como `usu_id`). `EMAIL_DUPLICADO` e `FALHA_ENVIO_EMAIL` são eventos técnicos, previstos no FR-029 fora
da contagem do SC-009: no primeiro, `conta` é `None` e o detalhe traz só a quantidade de contas
encontradas; no segundo, o detalhe traz só o tipo do erro; `detalhe` é um texto montado pelo sistema, **nunca** com algo digitado pelo usuário.
Uma linha por evento: `data hora | evento | conta=<id> | autor=<id ou própria> | detalhe`. Nunca
entram senha, token, link ou e-mail completo (só o domínio). Credencial inexistente não gera evento,
para não registrar o que foi digitado [m12].

## A14. Base visual (FR-024; Q16, Q22)

**Decisão**:
- `static/css/sigtcc.css` com os tokens do protótipo (`:root`: `--azul #1967d2`, `--azul-btn
  #1a73e8`, `--verde #137333`, `--vermelho #c5221f`, `--texto #202124`, `--borda #dadce0` e demais) e
  os componentes reescritos a partir do visual: barra superior de 64 px, menu lateral, botões, campos
  com erro por campo, alertas (`info`, `aviso`, `erro`, `sucesso`) e avisos temporários. Ajustes em
  900 e 600 px, como no protótipo; a partir de 360 px o menu recolhe e os formulários ocupam a largura.
- Roboto, Figtree e Material Symbols pelo Google Fonts, com o mesmo `<link>` do protótipo (a política
  de `Referer` `same-origin` impede que URLs internas vazem para o Google).
- `static/js/sigtcc.js` escrito do zero: abrir e fechar o menu e fechar avisos.
- `templates/base.html` (blocos `titulo`, `conteudo`, `scripts`), `base_publica.html` (telas sem
  login), `acesso_negado.html` (403) e os includes `barra_superior`, `menu_lateral`, `mensagens` e
  `campo`. O `includes/campo.html` atende `input` de texto, e-mail, senha, número, data e arquivo,
  `select` e `checkbox`; erros que não são de campo saem por `includes/mensagens.html` [I9].
- Checklist de revisão visual (Q16) no `quickstart.md`, em 360, 768 e 1280 px.

## A15. Conta de teste pelo shell (FR-027)

**Decisão [I10]**: `python manage.py criar_conta_teste` com:
- `--perfil` (`aluno`, `docente`, `coordenador`, `secretaria`, `membro_externo`), `--status`
  (`aguardando` ou `ativa`), `--email`, `--matricula`, `--senha`, `--validade AAAA-MM-DD`;
- `--curso <nome>` (padrão "Engenharia de Computação", um dos 3 da carga inicial);
- `--turma <identificador>`: reaproveita a turma se ela existir; se não existir, cria uma turma de
  TCC 1 ativa com esse identificador (e uma disciplina de teste). `--professor <email>` define o
  `tur_doc` na criação (padrão: o próprio docente, se o perfil for docente; senão, um docente de
  teste). `--arquivada` cria a turma como 'Arquivada';
- coordenador: recusa se o curso já tiver coordenador, com mensagem clara;
- recusa rodar com `DEBUG = False`. Nos testes, o comando roda com `override_settings(DEBUG=True)`
  [m14].

## A16. Reset do primeiro acesso (FR-015; Q3, Q9, Q27)

**Decisão**: a tela `alunos/<alu_id>/` abre para quem tem o papel `professor_disciplina` (qualquer
turma, Q27) e mostra nome, matrícula, e-mail e Status da Conta. O botão aparece só se
`pode_resetar_primeiro_acesso(professor, aluno)` for verdadeiro, ou seja, se
`professor_com_turma_ativa(professor, aluno)` (A7). O clique leva à confirmação (M-12); o POST chama
`services.resetar_primeiro_acesso(professor, aluno)`, que, em `transaction.atomic()` com
`select_for_update()` na conta [I4], confere a permissão de novo (`PermissionDenied` se faltar), grava
`usu_email = None`, `password = None`, `usu_status = 'Aguardando Ativação'` e
`usu_link_gerado_em = timezone.now()` (invalida os links), registra o evento e mostra a M-13. As
sessões do aluno caem pelo `user_can_authenticate` (A1).

Parâmetros: `professor` é o `Usuarios` logado (que precisa ter `Docentes`); `aluno` é a instância de
`Alunos` [I9].

## A17. Concorrência nos serviços que alteram a conta [I4]

**Decisão**: ativar, redefinir senha, pedir primeiro acesso, reenviar link, resetar e confirmar troca
de e-mail rodam em `transaction.atomic()` e começam com `Usuarios.objects.select_for_update().get(...)`.
Os links são validados de novo no POST, com a conta travada, e não só no GET. Assim, dois envios do
mesmo link não passam os dois, e uma ativação simultânea ao reset não deixa conta 'Ativa' sem e-mail.

## A18. Unicidade do e-mail sem diferenciar maiúsculas [I3]

**Decisão**: `services.normalizar_email(email)` (remove espaços; domínio em minúsculas, como a spec
001; `None` se vazio) e `services.email_em_uso(email, exceto=None)` (`iexact`, ignorando a conta
`exceto`) ficam no contrato para a spec 002 usar ao criar e alterar contas. Toda gravação de e-mail
desta feature roda em `transaction.atomic()` e trata `IntegrityError` como M-05. Um índice único em
`lower(usu_email)` daria a garantia no banco, mas muda o esquema: fica como pergunta à Maria Luiza
(Q-28 do índice), sem bloquear esta feature.

## A19. Datas sem fuso [m1]

Com `USE_TZ = False`, `timezone.now()` devolve a data e hora local sem fuso. A validade do Membro
Externo usa `timezone.now().date()` (e não `timezone.localdate()`, que exige data com fuso). No
Windows o Django não ajusta a variável `TZ`, então o horário segue o fuso da máquina: o servidor de
produção precisa estar em America/Manaus (observação para a configuração, Q-27).

## A20. Organização do código no app `cadastro`

| Arquivo | Conteúdo |
|---|---|
| `services.py` | login, bloqueio, links, senha, e-mail, reset, troca de e-mail, log, `item_indisponivel`, `normalizar_email`, `email_em_uso` |
| `forms.py` | formulários com primeiro erro |
| `views.py` | só orquestram |
| `urls.py` | rotas (`app_name = "cadastro"`) |
| `backends.py` | `SigtccBackend` |
| `permissoes.py` | `tipo_conta`, `papeis`, `professor_com_turma_ativa`, `pode_resetar_primeiro_acesso`, `perfil_requerido`, `PerfilRequeridoMixin` |
| `contexto.py`, `menu.py` | processadores de contexto e itens de menu do cadastro |
| `mensagens.py`, `validators.py` | textos e regra de senha |
| `management/commands/criar_conta_teste.py` | conta de teste |

Acréscimos à árvore do PGCS 2.3, para a revisão do Célio (Q-27): `backends.py`, `permissoes.py`,
`contexto.py`, `menu.py`, `mensagens.py`, `validators.py`, `management/`, `tests/`,
`templates/base_publica.html`, `templates/acesso_negado.html` e a pasta `logs/` [m15].
