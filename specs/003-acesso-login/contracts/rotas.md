# Contrato: rotas e telas da feature 003

**Feature**: [../spec.md](../spec.md) | **Pesquisa**: [../research.md](../research.md)

Todas as rotas ficam em `sigtcc/apps/cadastro/urls.py` (`app_name = "cadastro"`), incluídas na raiz
por `sigtcc/urls.py`, que também define `handler403` (página `acesso_negado.html` com a M-02).
"Público" = sem login. Mensagens: texto exato da spec (US) ou da tabela "Mensagens a validar com a PO"
(M-xx, provisórias).

| Nome da rota | Caminho | Métodos | Acesso | Template | Requisitos |
|---|---|---|---|---|---|
| `inicio` | `/` | GET | público | — (com login → `painel`; sem login → `entrar`) | FR-010 |
| `entrar` | `/entrar/` | GET, POST | público (logado → `painel`) | `cadastro/entrar.html` | FR-007 a FR-010; US-11 |
| `sair` | `/sair/` | POST | logado | — (→ `entrar`) | FR-011 |
| `primeiro_acesso` | `/primeiro-acesso/` | GET | público | `cadastro/primeiro_acesso.html` (escolha "Aluno" ou "Docente, Secretaria ou Membro Externo") | FR-001; Q8 |
| `primeiro_acesso_aluno` | `/primeiro-acesso/aluno/` | GET, POST | público | `cadastro/primeiro_acesso_form.html` | FR-001 a FR-003; US-10 |
| `primeiro_acesso_email` | `/primeiro-acesso/email/` | GET, POST | público | `cadastro/primeiro_acesso_form.html` | FR-001 a FR-003; US-10 |
| `ativar` | `/primeiro-acesso/ativar/<token>/` | GET | público | — (guarda o token na sessão e redireciona para `definir_senha`) | FR-016; research A3 |
| `definir_senha` | `/primeiro-acesso/definir-senha/` | GET, POST | público, com token na sessão | `cadastro/ativar.html` ou `cadastro/link_vencido.html` | FR-004, FR-005, FR-016; US-10, US-37 |
| `reenviar_link` | `/primeiro-acesso/reenviar/` | POST | público, com token na sessão | `cadastro/link_vencido.html` (com o resultado) | FR-017, FR-018; US-37 |
| `esqueci_senha` | `/esqueci-minha-senha/` | GET, POST | público | `cadastro/esqueci_senha.html` | FR-013; US-12 |
| `redefinir_senha` | `/redefinir-senha/<token>/` | GET | público | — (guarda o token na sessão e redireciona para `nova_senha`) | FR-014; research A3 |
| `nova_senha` | `/redefinir-senha/nova/` | GET, POST | público, com token na sessão | `cadastro/redefinir_senha.html` | FR-014; US-12; Q26 |
| `painel` | `/painel/` | GET | logado (todos os tipos) | `cadastro/painel.html` | FR-010; Q7 |
| `perfil` | `/perfil/` | GET, POST | logado | `cadastro/perfil.html` | FR-019 a FR-021; US-38 |
| `assinatura` | `/perfil/assinatura/` | GET | logado (só a própria imagem) | — (`FileResponse` com o tipo detectado) | FR-020; research A11 |
| `alterar_senha` | `/perfil/senha/` | GET, POST | logado | `cadastro/alterar_senha.html` | FR-012; US-12 |
| `confirmar_email` | `/perfil/email/confirmar/<token>/` | GET (mostra o novo e-mail e o botão), POST (confirma) | público (o link pode ser aberto noutro navegador) | `cadastro/confirmar_email.html` | FR-021; Q11, Q28 |
| `notificacoes` | `/notificacoes/` | GET | logado | `cadastro/notificacoes.html` (20 por página, `?pagina=`) | FR-022; Q14 |
| `abrir_notificacao` | `/notificacoes/<not_id>/` | GET | logado, dono da notificação (senão 404) | — (marca como lida e redireciona, ou volta à central com `ITEM_INDISPONIVEL`) | FR-023; Q10 |
| `marcar_lidas` | `/notificacoes/marcar-lidas/` | POST | logado | — (volta à central) | FR-022 |
| `aluno` | `/alunos/<alu_id>/` | GET | papel `professor_disciplina` (qualquer turma, Q27) | `cadastro/aluno.html` (botão só se `pode_resetar_primeiro_acesso`) | FR-015; Q3, Q9, Q27 |
| `resetar_primeiro_acesso` | `/alunos/<alu_id>/resetar-primeiro-acesso/` | GET (confirmação, M-12), POST (executa, M-13) | papel `professor_disciplina` e turma ativa com o aluno (senão 403) | `cadastro/confirmar_reset.html` | FR-015; US-12; RBN-CAD-06.8 |

Regras gerais:
- Página interna sem login: redireciona para `/entrar/?next=<caminho>`. O `next` vai num campo oculto
  do formulário de login e só é seguido se `url_has_allowed_host_and_scheme` aceitar (mesmo host,
  HTTPS quando a requisição for HTTPS); senão, `painel` (research A1, achado B2).
- Logado sem permissão: `PermissionDenied` → `handler403` → `acesso_negado.html`, status 403, M-02.
- Formulários com CSRF; ações que mudam dados só por POST, com uma exceção registrada:
  `abrir_notificacao` marca a notificação como lida no GET (research A12).
- `reenviar_link` só reenvia no estado `VENCIDO`; em `SEM_EMAIL` mostra a M-08; nos demais estados
  leva à tela correspondente, sem reenviar (research A3).
- Tokens de ativação e de redefinição saem da URL logo no primeiro GET (guardados na sessão), e
  `SECURE_REFERRER_POLICY = "same-origin"` fica declarado (research A3). Sem token na sessão,
  `definir_senha`, `nova_senha` e `reenviar_link` tratam o caso como link `ADULTERADO`; o token sai da
  sessão quando a ação termina.
- Telas públicas usam `base_publica.html`; as demais, `base.html`.

## E-mails enviados

| Evento | Template | Para | Como é enviado |
|---|---|---|---|
| Pedido de primeiro acesso ou reenvio | `cadastro/emails/ativacao.txt` | e-mail da conta | na requisição, na mesma transação (falha desfaz e mostra a M-17) |
| "Esqueci minha senha" | `cadastro/emails/redefinicao.txt` | e-mail da conta 'Ativa' | depois do commit, em thread (falha só no log; mensagem genérica sempre) |
| Troca de e-mail | `cadastro/emails/confirmar_email.txt` | novo e-mail | na requisição, na mesma transação (falha desfaz e mostra a M-17) |

Links absolutos montados com `SITE_URL` do `.env`. `EMAIL_TIMEOUT = 10` segundos.
