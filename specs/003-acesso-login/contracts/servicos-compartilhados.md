# Contrato: o que as outras features podem usar

**Feature**: [../spec.md](../spec.md) (história 6; FR-024 a FR-027) | **Pesquisa**: [../research.md](../research.md)

Mudar qualquer item deste contrato é mudança de comportamento para as outras features e começa pela
spec 003.

## 1. Base visual (FR-024)

- Toda tela interna estende `base.html` e preenche `{% block titulo %}` e `{% block conteudo %}`
  (opcional: `{% block scripts %}`). Telas públicas estendem `base_publica.html`.
- Campos: `{% include "includes/campo.html" with campo=form.<nome> %}` (rótulo, ajuda, destaque e erro
  do campo). Atende `input` de texto, e-mail, senha, número, data e arquivo, `select` e `checkbox`.
  Erros que não são de campo: `django.contrib.messages`, mostrados por `includes/mensagens.html`.
- Classes de `static/css/sigtcc.css`: `btn`, `btn pri`, `btn txt`, `alerta info|aviso|erro|sucesso`,
  `campo`, `cartao`, `tabela`; variáveis de cor do protótipo (`--azul`, `--verde`, `--vermelho`,
  `--texto`, `--borda` e demais); ícones com `<span class="ms">nome_do_icone</span>`.
- Responsivo a partir de 360 px (Q22). Nenhuma feature copia o JavaScript do protótipo.
- `FormularioPrimeiroErro` (`sigtcc.apps.cadastro.forms`) é opcional: use quando a US pedir só o
  primeiro erro.

## 2. Verificação de perfil (FR-025) – `sigtcc.apps.cadastro.permissoes`

| Item | Uso |
|---|---|
| `tipo_conta(usuario) -> str \| None` | `"aluno"`, `"docente"`, `"secretaria"`, `"membro_externo"` ou `None` (conta sem especialização, sem acesso a páginas com perfil) |
| `papeis(usuario) -> frozenset[str]` | subconjunto de `{"coordenador", "professor_disciplina", "orientador", "coorientador"}`; calculado na primeira chamada e guardado no objeto do usuário da requisição |
| `tem_perfil(usuario, *perfis) -> bool` | verdadeiro se o tipo de conta **ou** algum papel estiver em `perfis` |
| `@perfil_requerido(*perfis)` | decorador de view. Sem argumentos: só exige login. Sem login → login com `next`. Sem permissão → `PermissionDenied` |
| `PerfilRequeridoMixin` | o mesmo para views de classe (`perfis_permitidos = (...)`) |
| `professor_com_turma_ativa(professor, aluno=None) -> bool` | regra compartilhada da spec Q27 (abaixo); `professor`: `Usuarios` com `Docentes`; `aluno`: `Alunos` ou `None` |
| `pode_resetar_primeiro_acesso(professor, aluno) -> bool` | decide se o botão "Resetar primeiro acesso" aparece (US-41, Q-13 do índice); mesmos tipos |

**Regras compartilhadas (spec Q27; base: matriz, Glossário e RBN-CAD-04.5, "turma arquivada não
recebe movimentação e fica para consulta"; ciência das responsáveis em Q-29 a Q-32 do índice)**:
- O papel `professor_disciplina` vale para o docente com **pelo menos uma turma, ativa ou
  arquivada**. Ele dá acesso de leitura às telas do papel.
- **Ações que alteram dados** (gravar, excluir, homologar, resetar etc.) exigem que o docente seja
  Professor de uma turma **não arquivada** relacionada ao dado: use `professor_com_turma_ativa` no
  `services.py` da feature, antes de gravar.
- Os papéis são **globais**: "orientador" quer dizer "tem alguma orientação ativa", não "orienta este
  TCC". Cada feature confere o vínculo com o objeto (TCC, defesa, turma) no próprio `services.py`.
- Levantar `django.core.exceptions.PermissionDenied` em qualquer view ou serviço basta: o
  `handler403` mostra a página padrão com a M-02.

## 3. Menu lateral (FR-025)

Cada app com itens de menu cria `menu.py` com `ITENS = [ {...}, ... ]`. Cada item tem `rotulo`,
`icone` (nome do Material Symbols), `rota` (**nome** da URL, por exemplo `"defesa:agenda"`),
`perfis` (tupla de tipos de conta e papéis), `ordem` (inteiro) e `secao` opcional (título de grupo no
menu, como "Gestão"). O cadastro junta os itens de todos os apps, sem depender da ordem de
carregamento e sem duplicar.

## 4. Links e e-mail (FR-026) – `sigtcc.apps.cadastro.services`

| Função | Resultado |
|---|---|
| `gerar_link_ativacao(usuario) -> str` | URL absoluta (24 h); grava `usu_link_gerado_em` e invalida os links anteriores |
| `enviar_link_ativacao(usuario) -> bool` | gera, grava e envia numa transação; `False` se o envio falhar (nada fica gravado; quem chama mostra a M-17) |
| `validar_link_ativacao(token) -> ResultadoLink` | estado `ADULTERADO`, `ATIVA`, `INATIVA`, `EXPIRADA`, `SEM_EMAIL`, `SUBSTITUIDO`, `VENCIDO` ou `VALIDO` (com o usuário), na ordem do data-model |
| `gerar_link_redefinicao(usuario) -> str`, `enviar_link_redefinicao(email) -> None` (recebe o e-mail digitado; só envia para conta 'Ativa' com validade em dia), `validar_link_redefinicao(token) -> ResultadoLink` | o mesmo para "Esqueci minha senha"; o envio é feito depois do commit, em segundo plano |
| `normalizar_email(email) -> str \| None` | remove espaços, domínio em minúsculas, `None` se vazio |
| `email_em_uso(email, exceto=None) -> bool` | verifica se outra conta já usa o e-mail, sem diferenciar maiúsculas |

**Para a spec 002 (Gestão de Contas)**:
- A criação de contas **não** envia link (spec Q1).
- Use `normalizar_email` e `email_em_uso` antes de criar ou alterar uma conta; o banco diferencia
  maiúsculas.
- A inativação (US-04) e a expiração (US-06) só mudam `usu_status`. As sessões caem sozinhas na
  próxima página, e os links pendentes passam a mostrar M-15 ou M-16 (spec Q26).

## 5. Ações de conta, notificações e log – `sigtcc.apps.cadastro.services`

| Função | Uso |
|---|---|
| `resetar_primeiro_acesso(professor, aluno) -> None` | `professor`: `Usuarios` com `Docentes`; `aluno`: instância de `Alunos`. Confere `pode_resetar_primeiro_acesso` de novo, numa transação com a conta travada; levanta `PermissionDenied` se faltar permissão. Mensagens: `mensagens.M12_CONFIRMAR_RESET` e `mensagens.M13_RESET_CONCLUIDO`; template de confirmação `cadastro/confirmar_reset.html` |
| `item_indisponivel(request) -> HttpResponseRedirect` | grava "Este item não está mais disponível" (`mensagens.ITEM_INDISPONIVEL`) e volta à central; para a tela de destino de uma notificação cujo item foi cancelado (Defesa, Q-12) |
| `registrar_evento(evento, conta, autor=None, detalhe="") -> None` | `evento`: valor de `EventoAcesso` (conjunto fechado); `conta`, `autor`: `Usuarios` ou `None`; `detalhe`: texto montado pelo sistema, nunca digitado pelo usuário; sem senha, token, link nem e-mail completo |

**Notificações (para quem as cria)**: `not_link_tela` é um caminho relativo começando com `/`, sem
host, com query string opcional (por exemplo `/defesa/convites/12/`). Endereços externos não são
seguidos.

**Assinaturas (para a Defesa)**: `doc_assinatura_path` e `mem_assinatura_path` guardam o caminho
relativo a `MEDIA_ROOT`; abra o arquivo com `django.core.files.storage.default_storage.open(caminho)`.
As imagens não têm URL pública.

## 6. Conta de teste (FR-027)

`python manage.py criar_conta_teste --perfil <aluno|docente|coordenador|secretaria|membro_externo> [--status aguardando|ativa] [--email ...] [--matricula ...] [--senha ...] [--curso "<nome>"] [--turma <identificador>] [--professor <email>] [--arquivada] [--validade AAAA-MM-DD]`.
Só com `DEBUG = True`. Roteiro em [../quickstart.md](../quickstart.md).
