# Contrato: rotas e telas da feature 003

**Feature**: [../spec.md](../spec.md) | **Pesquisa**: [../research.md](../research.md)

Todas as rotas ficam em `sigtcc/apps/cadastro/urls.py` (`app_name = "cadastro"`), incluídas na raiz
por `sigtcc/urls.py`. "Público" = sem login. Mensagens: o texto exato está na spec (US) ou na tabela
"Mensagens a validar com a PO" (M-xx, provisórias).

| Nome da rota | Caminho | Métodos | Acesso | Template | Requisitos |
|---|---|---|---|---|---|
| `inicio` | `/` | GET | público | — (redireciona: com login → `painel`; sem login → `entrar`) | FR-010 |
| `entrar` | `/entrar/` | GET, POST | público | `cadastro/entrar.html` | FR-007 a FR-010; US-11 |
| `sair` | `/sair/` | POST | logado | — (redireciona para `entrar`) | FR-011 |
| `primeiro_acesso` | `/primeiro-acesso/` | GET | público | `cadastro/primeiro_acesso.html` (escolha "Aluno" ou "Docente, Secretaria ou Membro Externo") | FR-001; Q8 |
| `primeiro_acesso_aluno` | `/primeiro-acesso/aluno/` | GET, POST | público | `cadastro/primeiro_acesso_form.html` | FR-001 a FR-003; US-10 |
| `primeiro_acesso_email` | `/primeiro-acesso/email/` | GET, POST | público | `cadastro/primeiro_acesso_form.html` | FR-001 a FR-003; US-10 |
| `ativar` | `/primeiro-acesso/ativar/<token>/` | GET, POST | público | `cadastro/ativar.html` ou `cadastro/link_vencido.html` | FR-004, FR-005, FR-016; US-10, US-37 |
| `reenviar_link` | `/primeiro-acesso/reenviar/<token>/` | POST | público | `cadastro/link_vencido.html` (com resultado) | FR-017, FR-018; US-37 |
| `esqueci_senha` | `/esqueci-minha-senha/` | GET, POST | público | `cadastro/esqueci_senha.html` | FR-013; US-12 |
| `redefinir_senha` | `/redefinir-senha/<token>/` | GET, POST | público | `cadastro/redefinir_senha.html` | FR-014; US-12 |
| `painel` | `/painel/` | GET | logado (todos os tipos) | `cadastro/painel.html` | FR-010; Q7 |
| `perfil` | `/perfil/` | GET, POST | logado | `cadastro/perfil.html` | FR-019 a FR-021; US-38 |
| `alterar_senha` | `/perfil/senha/` | GET, POST | logado | `cadastro/alterar_senha.html` | FR-012; US-12 |
| `confirmar_email` | `/perfil/email/confirmar/<token>/` | GET | público (o link pode ser aberto noutro navegador) | `cadastro/confirmar_email.html` | FR-021; Q11 |
| `notificacoes` | `/notificacoes/` | GET | logado | `cadastro/notificacoes.html` (20 por página, `?pagina=`) | FR-022; Q14 |
| `abrir_notificacao` | `/notificacoes/<not_id>/` | GET | logado, dono da notificação | — (redireciona para `not_link_tela` ou volta à central com a mensagem) | FR-023; Q10 |
| `marcar_lidas` | `/notificacoes/marcar-lidas/` | POST | logado | — (volta à central) | FR-022 |
| `aluno` | `/alunos/<alu_id>/` | GET | papel `professor_disciplina` | `cadastro/aluno.html` (botão só para Professor de turma ativa do aluno) | FR-015; Q3, Q9 |
| `resetar_primeiro_acesso` | `/alunos/<alu_id>/resetar-primeiro-acesso/` | GET (confirmação, M-12), POST (executa, M-13) | papel `professor_disciplina` e turma ativa do aluno | `cadastro/confirmar_reset.html` | FR-015; US-12; RBN-CAD-06.8 |

Respostas gerais:
- Página interna sem login: redireciona para `/entrar/?next=<caminho>`; depois do login, volta ao
  caminho (história 6, cenário 1).
- Logado sem permissão: status 403, `acesso_negado.html`, M-02 (FR-025).
- Todo formulário usa proteção CSRF; ações que mudam dados são só POST.
- Notificação de outro usuário: 404 (não revela que existe).
- Telas públicas usam `base_publica.html`; as demais, `base.html` (barra superior, sino e menu).

## E-mails enviados

| Evento | Template | Para | Conteúdo |
|---|---|---|---|
| Pedido de primeiro acesso ou reenvio | `cadastro/emails/ativacao.txt` | e-mail da conta | nome, link de ativação, validade de 24 horas |
| "Esqueci minha senha" | `cadastro/emails/redefinicao.txt` | e-mail da conta 'Ativa' | nome, link de redefinição, validade de 24 horas |
| Troca de e-mail | `cadastro/emails/confirmar_email.txt` | novo e-mail | nome, link de confirmação, validade de 24 horas |

Os links são absolutos, montados com `SITE_URL` do `.env`.
