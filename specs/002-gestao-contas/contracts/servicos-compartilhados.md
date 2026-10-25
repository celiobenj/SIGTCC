# Contrato: o que as outras features usam da Gestão de Contas

**Feature**: [../spec.md](../spec.md) | **Pesquisa**: [../research.md](../research.md)

Mudar qualquer item deste contrato é mudança de comportamento para as outras features e começa pela
spec 002. Módulo: `sigtcc.apps.cadastro.services_contas` (exceto onde indicado). Direção das
importações: research C3 (`defesa` importa `services_contas`; nunca o contrário em `models.py`).

## 1. Listas de escolha e criação de vínculos (FR-028) – Vida do TCC, Defesa e Turmas (Q-67, Q-68, Q-77)

| Função | Resultado |
|---|---|
| `docentes_ativos() -> QuerySet[Docentes]` | docentes com `usu_status` 'Ativa'; base das listas de orientador, coorientador, Professor da Disciplina e avaliador |
| `membros_externos_disponiveis() -> QuerySet[MembrosExternos]` | todos os membros externos ('Aguardando Ativação', 'Ativa' e 'Expirada'; o Membro Externo não tem o status 'Inativa', RBN-CAD-03.3); a banca renova a validade dos expirados (US-06 A1) |
| `travar_e_conferir_ativo(usuario) -> bool` | trava a linha de `Usuarios` (`select_for_update`) e relê o status; docente: `True` se 'Ativa'; membro externo: sempre `True` depois da trava (pode ser renovado pela banca) |

**Regra de travas (research B1, C19)**: quem **cria um vínculo** com um docente ou membro externo
(turma, pedido ou convite de orientação e coorientação, orientação, coorientação, membro de banca,
papel de Coordenador) chama `travar_e_conferir_ativo` **na mesma transação do INSERT, no POST**, e
recusa se devolver `False`. Conferir só na lista não basta. Sem isso, uma inativação simultânea
deixa um docente inativo com vínculo aberto (SC-005). Ordem das travas: `Usuarios` (id crescente),
depois a especialização, depois `Cursos` (id crescente).

## 2. Validade do Membro Externo (FR-039, FR-041) – Defesa (Q-67)

| Função | Uso |
|---|---|
| `recalcular_validade(usuario, hoje=None) -> bool` | `usuario`: `Usuarios` do membro (outro tipo de conta: devolve `True` sem fazer nada). |

- **Quando**: dentro da transação da Defesa, depois de gravar o evento e o `Historico_Defesas`, uma
  vez por Membro Externo afetado, nestes gatilhos: membro incluído numa banca; sessão reagendada
  (cada membro externo da banca); sessão cancelada (cada membro externo da banca); membro retirado
  da banca; suplente acionado (só o suplente que entra; o substituído mantém a validade, spec Q33).
- **Garantias**: trava a conta com `no_key=True` (não conflita com os INSERTs em `Banca_Defesa`);
  roda num savepoint próprio; se falhar, devolve `False`, a validade anterior fica, o erro vai para o
  log e a transação da Defesa continua válida (US-06 E2). Idempotente: só depende do banco.
- **Premissas sobre os dados da Defesa** (a confirmar pelo Célio, Q-67): as linhas de
  `Banca_Defesa` de sessão Cancelada são mantidas; a retirada apaga a linha e grava 'Alteração da
  Banca' com `hdf_membro_removido`; o acionamento do suplente grava o substituído em
  `ban_usu_substituido` na mesma linha.
- **Ligar as chamadas em produção só depois que a proteção da prorrogação estiver no `develop`**
  (coluna `mem_prorrogado_ate` aprovada na Q-69; research C13; spec Q34 e Q36).

Regra completa em [../data-model.md](../data-model.md), seção 4.

## 3. Atalho da banca (FR-034) – Defesa, US-23

O botão "Cadastrar membro externo" leva a
`{% url 'cadastro:contas_membro_novo' %}?voltar=<caminho da tela da banca>`. Ao salvar, o usuário
volta a esse caminho com `membro=<mem_id>` acrescentado à query; ao cancelar, volta sem ele. Só
caminhos internos que resolvem numa rota são aceitos (research C23). **A tela da banca valida o
`membro` recebido** (existe, está em `membros_externos_disponiveis()` e o usuário pode compor a
banca); nunca confia no parâmetro.

## 4. Expiração (FR-040; research C15) – `sigtcc.apps.cadastro.services`

- `expirar_se_vencida(usuario) -> bool`: trava a conta, relê, grava 'Expirada' se ainda for 'Ativa'
  vencida e registra `CONTA_EXPIRADA` com autor "sistema". Usada pelo comando e pelo login.
- Comando `python manage.py expirar_membros_externos`: agendar uma vez por dia, depois da
  meia-noite (America/Manaus), no servidor (Q-67, item 4; Q-70). Idempotente.
- `services.autenticar` chama `expirar_se_vencida` no ramo de validade vencida, protegido: uma falha
  na gravação não muda o resultado do login (Q-71).

## 5. Acréscimos ao contrato da spec 003 (ciência: Julia Cohen, Q-71)

- `services.pedir_troca_email(conta, novo, autor=None)`: parâmetro opcional, só para o log.
- `services.confirmar_troca_email`: passa a gravar `usu_link_gerado_em = agora` na confirmação,
  invalidando os links de ativação e de redefinição anteriores (spec 002, Q31).
- `services.travar_email(email)`: trava consultiva por e-mail normalizado (research C4); também
  usada em `confirmar_troca_email`.
- `services.AUTOR_SISTEMA`: valor de autor "sistema" aceito por `registrar_evento`.
- `services.expirar_se_vencida(usuario)` (§4).
- `EventoAcesso`: `CONTA_CRIADA`, `CONTA_ALTERADA`, `CONTA_INATIVADA`, `CONTA_REATIVADA`,
  `ACESSO_PRORROGADO`, `CONTA_EXPIRADA`, `VALIDADE_RECALCULADA`, `SENHA_GESTOR_INCORRETA`.
- `acesso_negado.html` aceita uma mensagem no contexto (padrão: M-02) (research C21).
- `mensagens.M02_ACESSO_NEGADO` = "Você não tem permissão para esta ação" e
  `mensagens.M14_CAMPO_OBRIGATORIO` = "Campo obrigatório" (Q-50).
- `menu.py`: itens "Docentes", "Secretarias" e "Membros externos" (seção "Cadastros").

## 6. Comando dos Coordenadores iniciais (FR-045, FR-046)

`python manage.py criar_coordenadores --arquivo <caminho.csv>` (colunas `curso;nome;email;titulacao`,
UTF-8 com ou sem BOM, separador `;`, arquivo fora do repositório) ou `--curso "<nome>" --nome
"<nome>" --email <e-mail> --titulacao <Especialista|Mestre|Doutor>` (o e-mail fica no histórico do
shell; prefira `--arquivo`). Funciona em produção. A saída não mostra e-mails. Roteiro em
[../quickstart.md](../quickstart.md).
