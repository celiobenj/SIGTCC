# Contrato: o que as outras features podem usar

**Feature**: [../spec.md](../spec.md) (história 6; FR-024 a FR-027) | **Pesquisa**: [../research.md](../research.md)

Mudar qualquer item deste contrato é mudança de comportamento para as outras features e começa pela
spec 003.

## 1. Base visual (FR-024)

- Toda tela interna estende `base.html` e preenche `{% block titulo %}` e `{% block conteudo %}`
  (opcional: `{% block scripts %}`). Telas públicas estendem `base_publica.html`.
- Campos de formulário: `{% include "includes/campo.html" with campo=form.<nome> %}` (rótulo, ajuda,
  destaque e mensagem de erro do campo).
- Mensagens de sucesso, aviso e erro: `django.contrib.messages`; o `base.html` as mostra com
  `includes/mensagens.html`.
- Classes CSS disponíveis em `static/css/sigtcc.css`: `btn`, `btn pri`, `btn txt`, `alerta info|aviso|erro|sucesso`,
  `campo`, `cartao`, `tabela`; variáveis de cor `--azul`, `--verde`, `--vermelho`, `--texto`,
  `--borda` (e as demais do protótipo); ícones com `<span class="ms">nome_do_icone</span>`.
- Responsivo a partir de 360 px (Q22). Nenhuma feature copia o JavaScript do protótipo.

## 2. Verificação de perfil (FR-025) – `sigtcc.apps.cadastro.permissoes`

| Item | Uso |
|---|---|
| `tipo_conta(usuario) -> str` | `"aluno"`, `"docente"`, `"secretaria"` ou `"membro_externo"` |
| `papeis(usuario) -> frozenset[str]` | subconjunto de `{"coordenador", "professor_disciplina", "orientador", "coorientador"}` |
| `tem_perfil(usuario, *perfis) -> bool` | verdadeiro se o tipo de conta **ou** algum papel estiver em `perfis` |
| `@perfil_requerido(*perfis)` | decorador de view; sem login → login com `next`; sem permissão → 403 com a M-02 |
| `PerfilRequeridoMixin` | o mesmo para views de classe (`perfis_permitidos = (...)`) |

Os perfis aceitos são os oito nomes acima. Exemplo: `@perfil_requerido("coordenador", "secretaria")`.

## 3. Menu lateral (FR-025) – `sigtcc.apps.cadastro.menu`

`registrar_item(rotulo, icone, rota, perfis, ordem=100, secao=None)`, chamado no `ready()` do
`AppConfig` de cada app. O menu mostra só os itens cujo `perfis` inclui o tipo de conta ou um papel
do usuário.

## 4. Links (FR-026) – `sigtcc.apps.cadastro.services`

| Função | Resultado |
|---|---|
| `gerar_link_ativacao(usuario) -> str` | URL absoluta (24 h); grava `usu_link_gerado_em` e invalida os links anteriores |
| `enviar_link_ativacao(usuario) -> bool` | gera e envia ao e-mail da conta; `False` se o envio falhar (quem chama mostra a M-17) |
| `validar_link_ativacao(token) -> EstadoLink` | `ATIVA`, `SEM_EMAIL`, `SUBSTITUIDO`, `VENCIDO` ou `VALIDO` (com o usuário), na ordem de Q5 |
| `gerar_link_redefinicao(usuario) -> str` e `validar_link_redefinicao(token)` | iguais, para "Esqueci minha senha" |

Lembrete (Clarifications Q1): a criação de contas (spec 002) **não** envia link.

## 5. Ações de conta – `sigtcc.apps.cadastro.services`

| Função | Uso |
|---|---|
| `resetar_primeiro_acesso(professor, aluno)` | reset do RBN-CAD-06.8, com as regras de Q9; levanta `PermissionDenied` se o professor não tiver turma ativa com o aluno. Para a US-41 (Q-13 do índice) |
| `registrar_evento(evento, conta, autor=None, detalhe="")` | grava uma linha no log de acesso (FR-029), sem dados sensíveis |

## 6. Conta de teste (FR-027)

`python manage.py criar_conta_teste --perfil <aluno|docente|coordenador|secretaria|membro_externo> [--status aguardando|ativa] [--email ...] [--matricula ...] [--senha ...] [--turma] [--arquivada] [--validade AAAA-MM-DD]`.
Só com `DEBUG = True`. Roteiro em [../quickstart.md](../quickstart.md).
