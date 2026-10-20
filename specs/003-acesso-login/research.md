# Research: Acesso e Login do SIGTCC

**Feature**: [spec.md](spec.md) (aprovada em 2026-10-20) | **Plano**: [plan.md](plan.md) | **Data**: 2026-10-20

Formato: Decisão / Justificativa / Alternativas. As decisões partem do que a spec 001 já fixou
(`specs/001-modelo-dados/research.md`: D1 `Usuarios` como usuário do Django sem colunas extras, D2
bloqueio no cache, R1 `USE_TZ = False`) e das Clarifications Q1 a Q22 da spec 003. Nenhuma decisão
cria tabela ou coluna (FR-028).

---

## A1. Login com ordem própria de verificação (FR-007 a FR-010; Q12, Q4, Q17)

**Decisão**: a regra do login fica num serviço, `services.autenticar(credencial, senha)`, que devolve
um resultado com um dos estados `VAZIO`, `NAO_ENCONTRADA`, `AGUARDANDO`, `BLOQUEADA` (com minutos
restantes), `SENHA_INCORRETA`, `INATIVA`, `EXPIRADA` ou `OK` (com o usuário), avaliados exatamente na
ordem de FR-008. A view só traduz o estado em mensagem e chama `django.contrib.auth.login`.

- Credencial com exatamente 10 dígitos: busca `Alunos.alu_matricula`; senão, `Usuarios.usu_email`
  sem diferenciar maiúsculas (`iexact`, Q13).
- Senha fora de 8 a 64 caracteres: `SENHA_INCORRETA`, contando tentativa (Q17).
- `EXPIRADA` também quando a conta é de Membro Externo e `mem_validade_ate < hoje` (Q4).
- Um backend próprio, `SigtccBackend(ModelBackend)`, é registrado em `AUTHENTICATION_BACKENDS` só para
  recuperar o usuário da sessão: `user_can_authenticate` exige `usu_status == 'Ativa'` (o `is_active`
  da spec 001) **e** validade não vencida. Assim, uma conta inativada ou expirada perde a sessão na
  próxima página.

**Justificativa**: o `authenticate()` padrão só diz "deu certo" ou "não deu", e a US-11 exige seis
mensagens diferentes numa ordem fixa. Centralizar no serviço permite testar a ordem sem tela.

**Alternativas**: `LoginView` do Django com `AuthenticationForm` (mensagens fixas, sem ordem
configurável); vários backends (a ordem entre backends não distingue status).

## A2. Bloqueio por tentativas no cache (FR-009; spec 001 D2; Q16)

**Decisão**: duas chaves no cache em arquivo já configurado (`CACHES`, spec 001):
- `acesso:falhas:<usu_id>`: contador de senhas incorretas seguidas (validade de 24 horas, só para
  limpar lixo);
- `acesso:bloqueio:<usu_id>`: instante do fim do bloqueio, com validade de 15 minutos.

Na terceira falha, grava o bloqueio e zera o contador. A senha correta (fora do bloqueio) apaga o
contador. O "N" da M-01 é `ceil(segundos_restantes / 60)`, no mínimo 1 (Q16). A chave é o `usu_id`,
então matrícula e e-mail somam juntos (US-11, cenário 6).

**Justificativa**: decidido na spec 001 (D2), sem coluna nova.

**Alternativas**: `django-axes` (cria tabelas); colunas em `Usuarios` (fora do dicionário).

## A3. Links assinados, sem tabela (FR-006, FR-014, FR-016 a FR-018, FR-021, FR-026; dicionário, seção 4, itens 2 e 3)

**Decisão**: os links usam `django.core.signing` (assinatura com a `SECRET_KEY` e um `salt` por tipo),
sem gravar nada além do que já existe:

| Tipo | Salt | Conteúdo assinado | Validade e invalidação |
|---|---|---|---|
| Ativação | `sigtcc.ativacao` | `usu_id`, `gerado_em` (= `usu_link_gerado_em` no momento da geração) | 24 h a partir de `gerado_em`; substituído quando `usu_link_gerado_em` da conta muda (novo pedido, reenvio ou reset) |
| Redefinição de senha | `sigtcc.redefinicao` | `usu_id`, `gerado_em` | igual à ativação; usado quando a senha muda, porque gravar a senha atualiza `usu_link_gerado_em` |
| Troca de e-mail | `sigtcc.troca_email` | `usu_id`, `email_atual`, `novo_email`, `emitido_em` | 24 h a partir de `emitido_em` (Q11); deixa de valer se o e-mail da conta já não for `email_atual` (proposta para a Q-21, ver A4) |

Gerar um link de ativação ou de redefinição grava `usu_link_gerado_em = agora` (o momento entra no
link). A validação do link de ativação segue a ordem de Q5: (1) conta 'Ativa'; (2) conta sem e-mail;
(3) `gerado_em` diferente de `usu_link_gerado_em` (substituído); (4) mais de 24 horas (vencido); (5)
válido. O `salt` impede usar um tipo de link no lugar de outro (caso de borda "Link de outro tipo").

**Justificativa**: o dicionário (seção 4, item 2) já prevê "tokens assinados do Django com validade de
24 horas, calculados com `usu_link_gerado_em`; um novo link altera esse valor e invalida o anterior".
Calcular a idade a partir de `gerado_em`, e não do carimbo da assinatura, permite distinguir
"substituído" de "vencido".

**Alternativas**: `PasswordResetTokenGenerator` do Django (não distingue vencido de substituído e
depende de `last_login`, que não existe, D1); tabela de tokens (fora do dicionário).

## A4. Link de troca de e-mail "substituído" (Q11; questão Q-21 do índice)

**Proposta** (a decisão é da Julia; a Q-21 do índice continua aberta até a resposta): o link de troca
**não** usa `usu_link_gerado_em`, para não invalidar um link de redefinição pendente. Ele carrega o
e-mail atual da conta e só vale enquanto a conta ainda tiver esse e-mail. Na prática, quando uma troca
é confirmada, todos os outros links de troca pendentes deixam de valer. Dois links pendentes, sem
nenhuma confirmação, valem os dois: o primeiro confirmado vence.

**Justificativa**: evita que um link antigo devolva o e-mail anterior depois de uma troca, sem
coluna nova.

**Alternativa**: invalidar todo link de troca anterior ao gerar outro (exigiria guardar o momento do
último link de troca, e `usu_link_gerado_em` já é usado pela redefinição).

## A5. Envio de e-mail (FR-002, FR-013, FR-017, FR-021; Q13)

**Decisão**: `django.core.mail.send_mail` com o backend vindo do `.env` (`EMAIL_BACKEND`, `EMAIL_HOST`,
`EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL`). Em
desenvolvimento, `django.core.mail.backends.console.EmailBackend`: o e-mail, com o link, aparece no
terminal. Os textos dos e-mails ficam em `templates/cadastro/emails/`. O endereço absoluto do link
vem de `SITE_URL` (do `.env`), para que outras features possam gerar links fora de uma requisição.
Falha no envio (exceção do backend): registro no log e M-17, exceto em "Esqueci minha senha", que
mantém a mensagem genérica (Q13).

**Alternativas**: serviço externo de e-mail (fora do escopo e com custo).

## A6. Sessão (FR-011; Q18, Q19)

**Decisão**: sessões no banco (tabela `django_session`, do framework, admitida pela spec 001 FR-020)
com `SESSION_COOKIE_AGE = 3600`, `SESSION_SAVE_EVERY_REQUEST = True` (a hora conta a partir do último
uso) e `SESSION_EXPIRE_AT_BROWSER_CLOSE = True`. Cookies `HttpOnly`; `SESSION_COOKIE_SECURE` e
`CSRF_COOKIE_SECURE` ligados quando `DEBUG = False`.

Q19 sem código extra: o Django guarda na sessão um resumo da senha (`get_session_auth_hash`). Quando
a senha muda, toda sessão com o resumo antigo deixa de valer. Na troca em "Meu perfil",
`update_session_auth_hash` mantém só a sessão atual; na redefinição por link, nenhuma sessão é
mantida.

**Alternativas**: sessão em cache (perde-se ao limpar o cache); cookie assinado (sem como invalidar no
servidor).

## A7. Verificação de perfil reutilizável (FR-025; RNF do RAN-CAD-01 e RAN-CAD-02)

**Decisão**: módulo `sigtcc/apps/cadastro/permissoes.py` com:
- `tipo_conta(usuario)`: `"aluno"`, `"docente"`, `"secretaria"` ou `"membro_externo"`, pela tabela de
  especialização em que o `usu_id` aparece;
- `papeis(usuario)`: conjunto com `"coordenador"` (`Coordenadores.cor_doc`), `"professor_disciplina"`
  (alguma `Turmas.tur_doc` com `tur_status = 'Ativa'`), `"orientador"` (`Orientacoes` com
  `ori_status = 'Ativa'`) e `"coorientador"` (`Coorientacoes` com `coo_doc` e `coo_status = 'Ativa'`),
  calculado uma vez por requisição;
- decorador `@perfil_requerido(*perfis)` e mixin `PerfilRequeridoMixin`, que aceitam tipos de conta e
  papéis. Sem login: redireciona para `LOGIN_URL` com `?next=`. Com login e sem permissão: página
  `acesso_negado.html`, status 403, com a M-02 e nenhum dado da página.

**Justificativa**: as outras features só declaram `@perfil_requerido("coordenador")`, por exemplo, sem
repetir a regra; os papéis vêm dos dados, como pede a spec.

**Alternativas**: grupos e permissões do Django (não existem, D1 da spec 001); checagem em cada view
(repetição).

## A8. Menu lateral e sino como dados de contexto (FR-022, FR-024, FR-025)

**Decisão**: dois `context_processors` em `sigtcc/apps/cadastro/contexto.py`:
- `menu`: lista de itens (rótulo, ícone Material Symbols, rota, perfis). Cada feature acrescenta os
  seus itens a um registro central (`sigtcc/apps/cadastro/menu.py`), e o processador filtra pelo tipo
  de conta e pelos papéis do usuário. Nesta feature: "Início" (painel) e, para Professor da
  Disciplina, nenhum item novo (a tela do aluno é aberta pelo endereço; a US-41 fará a lista);
- `notificacoes_nao_lidas`: contagem de `Notificacoes` do usuário com `not_lida = false`, para o sino.

**Justificativa**: o menu fica igual em todas as telas e cada feature só registra os seus itens.

## A9. Formulários com o primeiro erro e mensagens exatas (FR-003, FR-004, M-14; Q12)

**Decisão**: `forms.py` com uma classe base `FormularioPrimeiroErro`, que valida os campos na ordem
declarada e, ao achar o primeiro campo com erro, para e mantém só esse erro. Cada campo valida
formato, existência e status nessa ordem. As mensagens vêm de um módulo `mensagens.py`, com as
constantes das US (texto exato) e das M-01 a M-17 (provisórias, com o ID no nome, por exemplo
`M01_BLOQUEIO`). Trocar um texto validado pela PO é mudar só essa constante e o teste.

**Justificativa**: um só lugar para os 40 textos; os testes comparam com as mesmas constantes, e o
teste de "texto exato" (SC-002) compara as constantes com a US e com a tabela M da spec.

## A10. Regra de senha (FR-004, FR-012; Q17)

**Decisão**: validador próprio em `validators.py`: 8 a 64 caracteres, pelo menos um caractere de
`[A-Za-z]` e um de `[0-9]`; qualquer outro caractere é aceito. A senha é gravada com `set_password`
(hasher padrão do Django, PBKDF2). `AUTH_PASSWORD_VALIDATORS` passa a ter só o validador próprio, para
que a regra também valha quando outras features chamarem `django.contrib.auth.password_validation.
validate_password` (o `set_password` em si não valida).

## A11. Imagem de assinatura (FR-019, FR-020; RBN-CAD-13.1)

**Decisão**: o formulário usa `forms.FileField` (o modelo guarda só o caminho,
`doc_assinatura_path`/`mem_assinatura_path`, `CharField(255)` da spec 001). Validação: tamanho até
2 MB (2 × 1024 × 1024 bytes), extensão `.png`, `.jpg` ou `.jpeg` **e** assinatura do arquivo (bytes
iniciais de PNG ou JPEG), sem depender de biblioteca de imagem. O arquivo é gravado com
`default_storage` em `media/assinaturas/<usu_id>_<aleatório>.<ext>`; o arquivo anterior é apagado
depois que o novo caminho é salvo. Fora da regra: M-04.

**Alternativas**: Pillow para validar a imagem (dependência nova só para isso); `ImageField` no
modelo (mudaria a coluna, fora do dicionário).

## A12. Central de notificações (FR-022, FR-023; Q10, Q14)

**Decisão**: lista paginada com `Paginator` (20 por página), ordenada por `not_data_hora`
decrescente. Abrir uma notificação passa por uma rota própria que marca a notificação como lida e
depois testa `not_link_tela` com `django.urls.resolve`: se não resolver (`Resolver404`), mostra "Este
item não está mais disponível" na central; se resolver, redireciona. "Marcar como lidas" é um POST
que faz `update` de todas as não lidas do usuário. O caso "cancelado" fica com a feature de Defesa
(Q10; Q-12 do índice).

## A13. Registro de eventos de acesso (FR-029; Q21)

**Decisão**: `logging` do Python, logger `sigtcc.acesso`, com `RotatingFileHandler` (5 MB × 5
arquivos) em `LOG_DIR/acesso.log`; `LOG_DIR` vem do `.env` (padrão `logs`, relativo à raiz) e
`logs/` entra no `.gitignore` (Q-23 do índice, revisão do Célio). Uma linha por evento:
`data hora | evento | conta=<usu_id> | autor=<usu_id ou "própria"> | detalhe`, com evento em
`LOGIN_SENHA_INCORRETA`, `BLOQUEIO`, `SENHA_ALTERADA`, `SENHA_REDEFINIDA`, `RESET_PRIMEIRO_ACESSO`,
`TROCA_EMAIL_PEDIDA` e `TROCA_EMAIL_CONFIRMADA`. Nunca entram senha, link, token ou o e-mail novo
completo (só o domínio). Os testes usam `assertLogs`.

## A14. Base visual (FR-024; Q16, Q22)

**Decisão**:
- `static/css/sigtcc.css` com os tokens de cor, fontes, raios e sombras do protótipo (`:root`:
  `--azul #1967d2`, `--azul-btn #1a73e8`, `--verde #137333`, `--vermelho #c5221f`, `--texto #202124`,
  `--borda #dadce0` etc.) e os componentes reescritos a partir do visual: barra superior de 64 px,
  menu lateral (gaveta), botões, campos com erro por campo, alertas (`info`, `aviso`, `erro`,
  `sucesso`) e aviso temporário (as mensagens do Django). Ajustes em 900 px e 600 px como no
  protótipo; a partir de 360 px o menu recolhe e os formulários ocupam a largura (Q22).
- Fontes Roboto e Figtree e ícones Material Symbols carregados do Google Fonts, com o mesmo `<link>` do
  protótipo.
- `static/js/sigtcc.js` mínimo, escrito do zero: abrir e fechar o menu lateral e fechar avisos. Nenhum
  código JavaScript do protótipo é copiado.
- `templates/base.html` com os blocos `titulo`, `conteudo` e `scripts`, e os includes
  `includes/barra_superior.html`, `includes/menu_lateral.html`, `includes/mensagens.html` e
  `includes/campo.html`. As telas sem login (login, primeiro acesso, ativação, redefinição) usam
  `base_publica.html`, sem menu e sem sino.
- Checklist de revisão visual (Q16) em `quickstart.md`, nas larguras 360, 768 e 1280 px.

**Alternativa**: fontes hospedadas no próprio servidor (sem dependência externa, mas exige baixar e
versionar os arquivos; pode ser adotado depois sem mudar as telas).

## A15. Conta de teste pelo shell (FR-027)

**Decisão**: comando de gestão `python manage.py criar_conta_teste`, com opções `--perfil`
(`aluno`, `docente`, `coordenador`, `secretaria`, `membro_externo`), `--status`
(`aguardando` ou `ativa`), `--email`, `--matricula`, `--senha`, `--turma` (cria disciplina e turma de
teste e vincula o aluno ou o docente), `--validade` (Membro Externo) e `--arquivada`. Recusa rodar com
`DEBUG = False`. Não substitui a Gestão de Contas (spec 002).

## A16. Reset do primeiro acesso (FR-015; Q3, Q9)

**Decisão**: tela `alunos/<alu_id>/` para quem tem o papel `professor_disciplina`, com nome,
matrícula, e-mail e Status da Conta. O botão aparece só se o docente é `tur_doc` de uma turma com
`tur_status = 'Ativa'` em que o aluno está matriculado (`Alunos_Turmas`). O clique leva a uma página
de confirmação (M-12) e o POST faz, numa transação: `usu_email = None`, `password = None`,
`usu_status = 'Aguardando Ativação'`, `usu_link_gerado_em = agora` (invalida os links); depois M-13,
registro no log e encerramento das sessões do aluno (a senha mudou, A6). O serviço
`services.resetar_primeiro_acesso(professor, aluno)` é o que a US-41 vai chamar (Q-13 do índice).

## A17. Organização do código no app `cadastro`

**Decisão**: tudo no app `sigtcc/apps/cadastro`, seguindo o MVT da constituição:

| Arquivo | Conteúdo |
|---|---|
| `services.py` | regras: `autenticar`, bloqueio, gerar, enviar e validar links, ativar, redefinir, alterar senha, trocar e-mail, resetar primeiro acesso, registrar evento |
| `forms.py` | formulários com primeiro erro e mensagens exatas |
| `views.py` | só orquestram: chamam o serviço, escolhem template e mensagem |
| `urls.py` | rotas com `app_name = "cadastro"` |
| `permissoes.py` | `tipo_conta`, `papeis`, `perfil_requerido`, `PerfilRequeridoMixin`, `SigtccBackend` |
| `contexto.py`, `menu.py` | processadores de contexto e registro do menu |
| `mensagens.py`, `validators.py` | textos das mensagens e regra de senha |
| `management/commands/criar_conta_teste.py` | conta de teste (A15) |

`permissoes.py`, `contexto.py`, `menu.py`, `mensagens.py`, `validators.py` e `management/` não
estão na árvore do PGCS 2.3: vão para a revisão do Célio no PR, como na feature 001.
