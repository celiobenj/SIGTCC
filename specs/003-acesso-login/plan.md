# Implementation Plan: Acesso e Login do SIGTCC

**Branch**: `feature/feat-02-acesso-e-login` (renomeada de `feature/feat-02-turmas`; ver Q-09 do índice) | **Date**: 2026-10-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-acesso-login/spec.md` (aprovada por Julia Cohen em
2026-10-20)

**Responsável**: Julia Cohen (US-10, US-11, US-12, US-37 e US-38).

## Summary

Implementar no app `cadastro` o primeiro acesso, o login com bloqueio, a saída, a recuperação e a
troca de senha, o reenvio do link de ativação, o reset do primeiro acesso, o perfil e a central de
notificações, com as mensagens exatas das US e as 17 provisórias da tabela M. A feature também
entrega o que as outras vão reutilizar: a base visual do protótipo de 17/10 (`base.html`, includes e
CSS), a verificação de perfil (`@perfil_requerido` e papéis derivados dos dados), as funções de link
de ativação e de redefinição e o comando `criar_conta_teste`.

Abordagem: regras em `services.py` (login na ordem de Q12, bloqueio no cache, links assinados com
`usu_link_gerado_em`), views finas, formulários que mostram só o primeiro erro, sessões de 60 minutos
e registro de eventos em arquivo de log. Nenhuma tabela ou coluna nova: usa o modelo da spec 001.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Django 5.2.18, psycopg 3, python-dotenv (já no `requirements.txt` da
feature 001). Nenhuma dependência nova (research A11: a imagem de assinatura é validada sem Pillow).

**Storage**: PostgreSQL 16 com as tabelas da spec 001 (nenhuma nova). Sessões em `django_session`
(framework). Contador e bloqueio de login no cache em arquivo (`CACHE_DIR`, spec 001 D2). Imagens de
assinatura em `sigtcc/media/assinaturas/`. Eventos em `LOG_DIR/acesso.log`.

**Testing**: test runner do Django contra PostgreSQL; `override_settings` para o backend de e-mail
em memória (`locmem`) e cache local nos testes; `assertLogs` para o log; avanço do relógio com
`unittest.mock.patch` em `django.utils.timezone.now` para 24 horas, 15 minutos e 60 minutos.

**Target Platform**: servidor web Linux ou Windows; navegadores atuais (Chrome, Firefox, Edge,
Safari), de 360 px de largura para cima (Q22).

**Project Type**: aplicação web monolítica com renderização no servidor (Django MVT).

**Performance Goals**: primeiro acesso completo em até 3 minutos pelo usuário (SC-003, teste manual).
Sem RNF de tempo de resposta para o login nas fontes.

**Constraints**: nenhuma tabela ou coluna nova (FR-028); mensagens idênticas às US e à tabela M
(SC-002); senhas nunca em tela, log ou texto puro (SC-008); segredos e endereços de e-mail só no
`.env`; nenhum JavaScript do protótipo reaproveitado.

**Scale/Scope**: 5 US (47 cenários), 29 FR, 17 mensagens provisórias; cerca de 15 telas, 20 rotas e
3 e-mails; centenas de usuários.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Verificação | Resultado |
|---|---|---|
| I. Especificação primeiro | spec 003 aprovada por Julia Cohen em 2026-10-20, sem marcadores pendentes; plan e tasks serão aprovados antes do código. | PASSA (aprovação do plan e do tasks pendente) |
| II. Rastreabilidade | Views, serviços, formulários, templates e testes levam [US-XX][RBN-...]; testes nomeados pelo cenário da US. | PASSA |
| III. Modelo de dados oficial | Nenhuma tabela ou coluna nova; só leitura e escrita nas colunas da spec 001 ([data-model.md](data-model.md)). Links, bloqueio e log fora de tabelas, como prevê a seção 4 do dicionário (itens 1 a 3). | PASSA |
| IV. Arquitetura | Tudo em `sigtcc/apps/cadastro`; regras em `services.py`, views só orquestram, templates sem regra; templates em `sigtcc/templates/{base.html, includes/, cadastro/}`, static em `sigtcc/static/`. | PASSA |
| V. Qualidade | lint.bat; comentários em português. | PASSA |
| VI. Testes de aceitação | Um teste por cenário das 5 US (47), mais base comum, mensagens exatas e log; mensagens comparadas com as constantes de `mensagens.py`, conferidas contra a US e a tabela M. | PASSA |
| VII. Segurança e LGPD | Senha só como hash (PBKDF2); links assinados com validade; bloqueio por tentativas; sessão de 60 min; CSRF; cookies `HttpOnly` e `Secure` fora do DEBUG; log sem dados sensíveis; `logs/` e `media/` fora do Git; cada perfil só acessa o seu papel (FR-025). | PASSA |
| VIII. Gerência de configuração | Commits atômicos por fase (regra do CLAUDE.md); branch `feature/feat-02-acesso-e-login`. | PASSA (nome da branch: Q-09 do índice) |
| IX. Governança | Itens de configuração para o Célio no PR: `settings.py` (sessão, e-mail, log, backend, validador, processadores de contexto), `.env.example` (variáveis novas), `.gitignore` (`logs/`, Q-23) e os módulos fora da árvore do PGCS 2.3 (research A17). | PASSA (revisão no PR) |

**Re-check após a Fase 1**: data-model, contratos e quickstart não criam tabela, coluna nem regra fora
da spec. Dois pontos que a spec não cobria foram decididos no plano e registrados como pendência
(Q-24 do índice: mensagem do link adulterado) ou proposta (A4, Q-21). Resultado mantido.

## Project Structure

### Documentation (this feature)

```text
specs/003-acesso-login/
├── spec.md
├── plan.md                         # Este arquivo
├── research.md                     # Fase 0: decisões A1–A17
├── data-model.md                   # Fase 1: tabelas usadas, transições e dados fora das tabelas
├── quickstart.md                   # Fase 1: roteiro manual, checklist visual e testes
├── contracts/
│   ├── rotas.md                    # rotas, acesso, templates e e-mails
│   └── servicos-compartilhados.md  # o que as outras features reutilizam
├── checklists/requirements.md
└── tasks.md                        # Fase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
.env.example                       # + EMAIL_*, DEFAULT_FROM_EMAIL, SITE_URL, LOG_DIR
.gitignore                         # + logs/ (Q-23)
sigtcc/
├── settings.py                    # AUTHENTICATION_BACKENDS, LOGIN_URL, SESSION_*, EMAIL_*, LOGGING,
│                                  # AUTH_PASSWORD_VALIDATORS, processadores de contexto
├── urls.py                        # include("sigtcc.apps.cadastro.urls"); media em DEBUG
├── apps/cadastro/
│   ├── services.py                # login, bloqueio, links, senha, e-mail, reset, log (A1–A6, A13, A16)
│   ├── forms.py                   # formulários com primeiro erro (A9)
│   ├── views.py                   # telas da feature
│   ├── urls.py                    # rotas (contracts/rotas.md)
│   ├── permissoes.py              # tipo_conta, papeis, perfil_requerido, SigtccBackend (A1, A7)
│   ├── contexto.py                # processadores de contexto: menu e sino (A8)
│   ├── menu.py                    # registro de itens do menu (A8)
│   ├── mensagens.py               # textos das US e M-01 a M-17 (A9)
│   ├── validators.py              # regra de senha (A10)
│   ├── management/commands/criar_conta_teste.py   # (A15)
│   └── tests/
│       ├── test_us10_primeiro_acesso.py
│       ├── test_us11_login.py
│       ├── test_us12_senha.py
│       ├── test_us37_reenvio.py
│       ├── test_us38_perfil_notificacoes.py
│       ├── test_base_comum.py
│       ├── test_mensagens.py
│       └── test_log_acesso.py
├── templates/
│   ├── base.html                  # barra superior, menu lateral, mensagens (A14)
│   ├── base_publica.html          # telas sem login
│   ├── acesso_negado.html         # 403 com a M-02
│   ├── includes/{barra_superior,menu_lateral,mensagens,campo}.html
│   └── cadastro/
│       ├── entrar.html, primeiro_acesso.html, primeiro_acesso_form.html, ativar.html,
│       │   link_vencido.html, esqueci_senha.html, redefinir_senha.html, painel.html,
│       │   perfil.html, alterar_senha.html, confirmar_email.html, notificacoes.html,
│       │   aluno.html, confirmar_reset.html
│       └── emails/{ativacao,redefinicao,confirmar_email}.txt
└── static/
    ├── css/sigtcc.css             # tokens e componentes do protótipo (A14)
    └── js/sigtcc.js               # menu e avisos, escrito do zero (A14)
```

**Structure Decision**: tudo no app `cadastro` (Épico 1), na estrutura do PGCS 2.3. Os módulos
`permissoes.py`, `contexto.py`, `menu.py`, `mensagens.py`, `validators.py` e `management/` são
acréscimos à árvore do PGCS e vão para a revisão do Célio (research A17).

## Pendências desta feature

O índice central é [docs/questoes-a-rever.md](../../docs/questoes-a-rever.md); o registro local
continua aqui.

| Pendência | Destino | Índice |
|---|---|---|
| Validar as 17 mensagens provisórias (M-01 a M-17) antes da implementação | Profa. Diana (PO) | Q-01 |
| Confirmar o nome da branch `feature/feat-02-acesso-e-login` (antes: `feature/feat-02-turmas`) | Célio Benjamim | Q-09 |
| Aprovar `logs/` no `.gitignore` e as variáveis novas do `.env.example` | Célio Benjamim | Q-23 |
| Decidir a proposta A4 para o link de troca de e-mail "substituído" | Julia Cohen | Q-21 |
| Link de ativação com assinatura adulterada: usar o mesmo texto do link substituído ("Link inválido. Use o link mais recente enviado ao seu e-mail") ou outro? A spec não trata o caso | Julia Cohen | Q-24 |
| Itens de configuração do PR (settings, módulos fora da árvore do PGCS) | Célio Benjamim | revisão do PR |

## Complexity Tracking

Nenhuma violação da constituição. Duas escolhas que merecem registro:

| Escolha | Por quê | Alternativa mais simples rejeitada |
|---|---|---|
| Serviço de login próprio em vez do `LoginView` do Django | A US-11 e a Q12 exigem seis mensagens diferentes numa ordem fixa, e o bloqueio por conta vale para matrícula e e-mail | `LoginView` + `AuthenticationForm`: uma mensagem só e sem ordem configurável |
| Links assinados com idade calculada por `usu_link_gerado_em` | Distinguir "substituído" de "vencido" (US-37, cenário 3; Q5) sem tabela de tokens | `PasswordResetTokenGenerator`: não distingue os dois casos e depende de `last_login`, que não existe (spec 001, D1) |
