# Quickstart: validar Acesso e Login

**Feature**: [spec.md](spec.md) | **Rotas**: [contracts/rotas.md](contracts/rotas.md) |
**Serviços**: [contracts/servicos-compartilhados.md](contracts/servicos-compartilhados.md)

Roteiro para provar, num ambiente de desenvolvimento, que o primeiro acesso, o login, a recuperação
de senha, o perfil e as notificações funcionam como na spec. Não contém código de implementação.

## Pré-requisitos

- Feature 001 aplicada (`python manage.py migrate` sem pendências).
- `.env` com `DEBUG=True` e as variáveis novas desta feature (ver `.env.example`):
  `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`, `DEFAULT_FROM_EMAIL`,
  `SITE_URL=http://localhost:8000` e `LOG_DIR=logs`.
- Servidor: `python manage.py runserver`. Os e-mails, com os links, aparecem no terminal do servidor.

## 1. Criar contas de teste pelo shell (FR-027)

```bash
python manage.py criar_conta_teste --perfil aluno --status aguardando --matricula 2026000001 --turma
python manage.py criar_conta_teste --perfil aluno --status ativa --matricula 2026000002 --email aluno2@uea.edu.br --senha Tcc@2026a --turma
python manage.py criar_conta_teste --perfil docente --status ativa --email docente@uea.edu.br --senha Tcc@2026a --turma
python manage.py criar_conta_teste --perfil coordenador --status ativa --email coord@uea.edu.br --senha Tcc@2026a
python manage.py criar_conta_teste --perfil secretaria --status aguardando --email secretaria@uea.edu.br
python manage.py criar_conta_teste --perfil membro_externo --status ativa --email externo@ufam.edu.br --senha Tcc@2026a --validade 2026-10-01
```

Esperado: cada comando mostra o `usu_id` criado. Com `DEBUG=False`, o comando recusa.

## 2. Roteiro manual (cronometrar o item a: SC-003, até 3 minutos)

| # | Ação | Resultado esperado |
|---|---|---|
| a | `/primeiro-acesso/` → "Aluno" → matrícula 2026000001 e um e-mail @uea.edu.br; abrir o link do terminal; criar a senha `Tcc@2026a` | "Enviamos um link de ativação para o seu e-mail"; depois "Conta ativada" na tela de login (US-10) |
| b | Entrar com a matrícula 2026000001 e depois com o e-mail | painel do Aluno nos dois casos (US-11) |
| c | Errar a senha 3 vezes com a matrícula 2026000002 e tentar com o e-mail e a senha certa | bloqueio de 15 min com o tempo restante (M-01), também pelo e-mail (US-11, cenários 5 e 6) |
| d | Entrar como `externo@ufam.edu.br` (validade vencida) | "Seu acesso expirou. Procure o Orientador, o Professor da Disciplina, a Secretaria ou o Coordenador de Curso" (Q4) |
| e | "Esqueci minha senha" com `docente@uea.edu.br`; abrir o link e redefinir | mensagem genérica; nova senha entra; o link usado dá "Link inválido ou vencido. Solicite um novo" (US-12) |
| f | Como `docente@uea.edu.br` (Professor da Disciplina da turma do aluno 2026000001), abrir `/alunos/<id>/` e resetar o primeiro acesso | M-12 e M-13; o aluno volta a 'Aguardando Ativação', sem e-mail; o link antigo mostra a tela de vencido e o reenvio mostra a M-08 (US-12, US-37; Q5) |
| g | Em "Meu perfil" do docente, enviar um PNG e depois um PDF | "Perfil atualizado"; com o PDF, M-04 e nada salvo (US-38) |
| h | Como `coord@uea.edu.br` (sem turma, portanto sem o papel Professor da Disciplina), abrir `/alunos/<id>/` | 403 com a M-02 (FR-025) |
| i | Criar 3 notificações pelo shell para o docente e abrir uma pelo sino | contador de 3 para 2; notificação com endereço inexistente: "Este item não está mais disponível" (US-38; Q10) |
| j | Ficar logado e trocar a senha em "Meu perfil" com outra sessão aberta noutro navegador | a outra sessão pede login na próxima página (Q19) |
| k | Conferir `logs/acesso.log` | uma linha por evento (senha errada, bloqueio, redefinição, reset, troca de e-mail), sem senhas nem links (FR-029, SC-009) |

## 3. Checklist de revisão visual (SC-007; Q16, Q22)

Comparar cada tela com `docs/fonte/prototipo/prototipo_17_10.html`, nas larguras 360, 768 e 1280 px:

- [ ] Paleta (azul, verde, vermelho, cinzas) e fontes Roboto e Figtree iguais às do protótipo
- [ ] Ícones Material Symbols nos mesmos lugares (menu, sino, avatar)
- [ ] Barra superior de 64 px com nome do sistema, sino com contador e menu do usuário
- [ ] Menu lateral recolhido abaixo de 900 px e aberto pelo botão de menu
- [ ] Campos com rótulo, erro destacado no campo e mensagem abaixo
- [ ] Alertas e avisos temporários com as cores do protótipo
- [ ] Sem rolagem horizontal nem conteúdo cortado em 360 px

## 4. Testes automatizados (SC-001, SC-002, SC-004 a SC-006, SC-008, SC-009)

```bash
python manage.py test sigtcc.apps.cadastro
```

Esperado: todos passam, inclusive os 53 testes da feature 001. Grupos novos: um arquivo por US
(`test_us10_primeiro_acesso.py`, `test_us11_login.py`, `test_us12_senha.py`, `test_us37_reenvio.py`,
`test_us38_perfil_notificacoes.py`), mais `test_base_comum.py` (história 6), `test_mensagens.py`
(texto exato das mensagens, SC-002) e `test_log_acesso.py` (SC-009).

## 5. Qualidade

`lint.bat` (ou isort, black e flake8) sem erros.
