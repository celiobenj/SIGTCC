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
CSS), a verificação de perfil (`@perfil_requerido`, papéis derivados dos dados e a regra
compartilhada da Q27), as funções de link e de e-mail e o comando `criar_conta_teste`.

Abordagem: regras em `services.py` (login na ordem de Q12 com tempo de resposta igual para conta
inexistente, bloqueio num cache próprio, links assinados que nunca reativam conta inativa ou
expirada, serviços que alteram a conta com a linha travada), views finas, formulários que mostram só
o primeiro erro, sessões de 60 minutos, assinaturas sem URL pública e registro de eventos em arquivo
de log. Nenhuma tabela ou coluna nova.

**Revisão de 2026-10-20**: o `arquiteto-django` revisou o plano; os achados B1, B2, I1 a I10 e os 20
menores foram aplicados (research, data-model, contratos e quickstart), com as decisões Q26, Q27 e
Q28 registradas na spec. Na reconferência, os 12 achados estavam fechados; os 5 menores restantes e
os 6 pontos novos também foram aplicados.

**Aprovação**: plano aprovado por Julia Cohen em 2026-10-20.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Django 5.2.18, psycopg 3, python-dotenv (já no `requirements.txt`). Nenhuma
dependência nova (a assinatura é validada pelos bytes, research A11; o envio em segundo plano usa
`threading`, A5).

**Storage**: PostgreSQL 16 com as tabelas da spec 001 (nenhuma nova). Sessões em `django_session`
(framework). Bloqueio de login num alias de cache próprio, `CACHES["acesso"]` (`FileBasedCache` na
pasta `CACHE_ACESSO_DIR`, ao lado da do cache padrão, até 100.000 entradas, research A2). Assinaturas em `MEDIA_ROOT/assinaturas/`, sem
URL pública. Eventos em `LOG_DIR/acesso.log`.

**Testing**: test runner do Django contra PostgreSQL; `override_settings` com e-mail em memória
(`locmem`) e cache local; `force_login` (o backend não autentica por senha, A1); `assertLogs` para o
log; avanço do relógio com `unittest.mock.patch` em `django.utils.timezone.now` (24 h, 15 min e 60
min), sem depender do relógio do cache nem do `max_age` do `signing`; `SIGTCC_EMAIL_SINCRONO = True`
e `captureOnCommitCallbacks(execute=True)` para conferir o e-mail de "Esqueci minha senha" (A5).

**Target Platform**: servidor web Linux ou Windows, no fuso America/Manaus (research A19);
navegadores atuais (Chrome, Firefox, Edge, Safari), de 360 px para cima (Q22).

**Project Type**: aplicação web monolítica com renderização no servidor (Django MVT).

**Performance Goals**: primeiro acesso completo em até 3 minutos pelo usuário (SC-003, teste manual).
`EMAIL_TIMEOUT` de 10 segundos para o envio não travar a requisição.

**Constraints**: nenhuma tabela ou coluna nova (FR-028); mensagens idênticas às US e à tabela M
(SC-002); senhas nunca em tela, log ou texto puro (SC-008); segredos e endereços de e-mail só no
`.env`; nenhum JavaScript do protótipo reaproveitado; nenhum link reativa conta inativa ou expirada
(Q26).

**Scale/Scope**: 5 US (47 cenários), 29 FR, 17 mensagens provisórias; cerca de 15 telas, 22 rotas e
3 e-mails; centenas de usuários.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Verificação | Resultado |
|---|---|---|
| I. Especificação primeiro | spec 003, plan e tasks aprovados por Julia Cohen em 2026-10-20, sem marcadores pendentes. | PASSA |
| II. Rastreabilidade | Views, serviços, formulários, templates e testes levam [US-XX][RBN-...]; testes nomeados pelo cenário da US. | PASSA |
| III. Modelo de dados oficial | Nenhuma tabela ou coluna nova; só leitura e escrita nas colunas da spec 001 ([data-model.md](data-model.md)); `usu_link_gerado_em` continua sendo "o momento do último link gerado" (research A3). Links, bloqueio e log fora de tabelas, como prevê a seção 4 do dicionário (itens 1 a 3). | PASSA |
| IV. Arquitetura | Tudo em `sigtcc/apps/cadastro`; regras em `services.py`, views só orquestram, templates sem regra; templates em `sigtcc/templates/{base.html, includes/, cadastro/}`, static em `sigtcc/static/`. | PASSA |
| V. Qualidade | lint.bat; comentários em português. | PASSA |
| VI. Testes de aceitação | Um teste por cenário das 5 US (47), mais base comum, segurança, mensagens exatas, log e comando de teste. | PASSA |
| VII. Segurança e LGPD | Senha só como hash; login com tempo igual para conta inexistente; bloqueio com conferência dupla; `next` validado; links assinados que saem da URL e não reativam contas; serviços com a conta travada; sessão de 60 min; CSRF; cookies `HttpOnly`, `SameSite=Lax` e `Secure` por `.env`; assinaturas sem URL pública e validadas pelos bytes; log sem dados sensíveis; `logs/` e `media/` fora do Git; cada perfil só acessa o seu papel (FR-025, Q27). | PASSA |
| VIII. Gerência de configuração | Commits atômicos por fase (regra do CLAUDE.md); branch `feature/feat-02-acesso-e-login`. | PASSA (nome da branch: Q-09 do índice) |
| IX. Governança | Itens de configuração para o Célio no PR listados na Q-27 do índice (além da Q-23). | PASSA (revisão no PR) |

**Re-check após a Fase 1 e a revisão do arquiteto**: data-model, contratos e quickstart não criam
tabela, coluna nem regra fora da spec. Os pontos que a spec não cobria foram decididos pela Julia e
levados à spec (Q23, Q24, Q26, Q27 e Q28). Resultado mantido.

## Project Structure

### Documentation (this feature)

```text
specs/003-acesso-login/
├── spec.md
├── plan.md                         # Este arquivo
├── research.md                     # Fase 0: decisões A1–A20
├── data-model.md                   # Fase 1: tabelas usadas, transições, estados dos links e dados fora das tabelas
├── quickstart.md                   # Fase 1: contas de teste, roteiro manual, checklist visual e testes
├── contracts/
│   ├── rotas.md                    # rotas, acesso, templates e e-mails
│   └── servicos-compartilhados.md  # o que as outras features reutilizam (com a regra da Q27)
├── checklists/requirements.md
└── tasks.md                        # Fase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
.env.example                       # + EMAIL_*, EMAIL_TIMEOUT, DEFAULT_FROM_EMAIL, SITE_URL, LOG_DIR, COOKIES_SEGUROS, CACHE_ACESSO_DIR
.gitignore                         # + logs/ (Q-23) e /cache_acesso/ (Q-27)
sigtcc/
├── settings.py                    # AUTHENTICATION_BACKENDS, LOGIN_URL, SESSION_*, CSRF/cookies, SECURE_REFERRER_POLICY,
│                                  # EMAIL_*, CACHES["acesso"], LOGGING, AUTH_PASSWORD_VALIDATORS, processadores de contexto
├── urls.py                        # include("sigtcc.apps.cadastro.urls"); handler403 (sem publicar assinaturas)
├── apps/cadastro/
│   ├── services.py                # login, bloqueio, links, senha, e-mail, reset, troca de e-mail, log (A1–A6, A12, A13, A16–A18)
│   ├── forms.py                   # formulários com primeiro erro (A9)
│   ├── views.py                   # telas da feature
│   ├── urls.py                    # rotas (contracts/rotas.md)
│   ├── backends.py                # SigtccBackend (A1)
│   ├── permissoes.py              # tipo_conta, papeis, professor_com_turma_ativa, pode_resetar_primeiro_acesso, perfil_requerido (A7)
│   ├── contexto.py                # processadores de contexto: menu e sino (A8)
│   ├── menu.py                    # ITENS do menu do cadastro (A8)
│   ├── mensagens.py               # textos das US, M-01 a M-17 e ITEM_INDISPONIVEL (A9)
│   ├── validators.py              # regra de senha (A10)
│   ├── management/commands/criar_conta_teste.py   # (A15)
│   └── tests/
│       ├── test_us10_primeiro_acesso.py
│       ├── test_us11_login.py
│       ├── test_us12_senha.py
│       ├── test_us37_reenvio.py
│       ├── test_us38_perfil_notificacoes.py
│       ├── test_base_comum.py
│       ├── test_seguranca.py
│       ├── test_mensagens.py
│       ├── test_log_acesso.py
│       └── test_criar_conta_teste.py
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

**Structure Decision**: tudo no app `cadastro` (Épico 1), na estrutura do PGCS 2.3. Os acréscimos à
árvore do PGCS estão em research A20 e vão para a revisão do Célio (Q-27).

## Pendências desta feature

O índice central é [docs/questoes-a-rever.md](../../docs/questoes-a-rever.md); o registro local
continua aqui.

| Pendência | Destino | Índice |
|---|---|---|
| Validar as 17 mensagens provisórias (M-01 a M-17); não bloqueiam as tarefas nem a implementação (spec Q25) | Profa. Diana (PO) | Q-01 |
| Confirmar o nome da branch `feature/feat-02-acesso-e-login` (renomeada de `feature/feat-02-turmas` em 2026-10-20) | Célio Benjamim | Q-09 (aberta) |
| Aprovar `logs/` no `.gitignore` e as variáveis novas do `.env.example` | Célio Benjamim | Q-23 |
| Aprovar os demais itens de configuração da feature 003: cache próprio do login, settings de sessão, cookies, e-mail e log, `handler403`, módulos e templates fora da árvore do PGCS, agendamento do `clearsessions`, fuso do servidor e limite de upload no servidor web | Célio Benjamim | Q-27 |
| Ciência da regra compartilhada da Q27 (Professor da Disciplina com qualquer turma; ações que alteram dados exigem turma não arquivada, RBN-CAD-04.5) | Leandra Matos, Célio Benjamim, Maria Luísa Gomes, Maria Luiza Guimarães | Q-29 a Q-32 |
| Índice único em `lower(usu_email)` para garantir no banco a unicidade sem diferenciar maiúsculas (opcional, muda o esquema) | Maria Luiza Guimarães | Q-28 |
| Observação de LGPD: a tela do aluno mostra os dados a qualquer Professor da Disciplina (FR-015, Q9) | Profa. Diana (PO), sem prazo | S-02 |
| ~~Link de troca de e-mail "substituído"~~ – respondida: proposta A4 aceita (spec Q24) | Julia Cohen | Q-21 (respondida em 2026-10-20) |
| ~~Link de ativação com assinatura adulterada~~ – respondida: mesma mensagem do link substituído (spec Q23) | Julia Cohen | Q-24 (respondida em 2026-10-20) |
| ~~Link em conta inativa ou expirada~~ – respondida: não ativa nem redefine; mensagem do status, M-15 ou M-16 (spec Q26) | Julia Cohen | Q-25 (respondida em 2026-10-20) |
| ~~Papel Professor da Disciplina~~ – respondida: qualquer turma; ações que alteram dados exigem turma não arquivada (spec Q27; regra no contrato de serviços) | Julia Cohen | Q-26 (respondida em 2026-10-20) |

## Complexity Tracking

Nenhuma violação da constituição. Escolhas que merecem registro:

| Escolha | Por quê | Alternativa mais simples rejeitada |
|---|---|---|
| Serviço de login próprio em vez do `LoginView` do Django | A US-11 e a Q12 exigem seis mensagens numa ordem fixa, e o bloqueio por conta vale para matrícula e e-mail | `LoginView` + `AuthenticationForm`: uma mensagem só e sem ordem configurável |
| Links assinados com idade calculada pelo instante do link | Distinguir "substituído" de "vencido" (US-37, cenário 3; Q5) sem tabela de tokens | `PasswordResetTokenGenerator`: não distingue os dois casos e depende de `last_login`, que não existe (spec 001, D1) |
| Alias de cache próprio para o login | O cache em arquivo padrão apaga entradas ao acaso acima de 300, o que derrubaria bloqueios vigentes | Usar o cache `default`: bloqueios somem com o uso das outras features |
| Envio de "Esqueci minha senha" em segundo plano | O tempo de resposta não pode revelar se a conta existe (Q13) | Envio síncrono: o SMTP denuncia as contas 'Ativa' |
