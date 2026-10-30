# Contrato: o que a feat-08 e a feat-09 (Célio Benjamim) podem chamar (feature 007)

**Feature**: [../spec.md](../spec.md) | **Pesquisa**: [../research.md](../research.md)

Mudar qualquer item deste contrato é mudança de comportamento para "Avaliação e Resultados"
(feat-08, US-25 a US-28) e para o módulo de ouvintes/documentos (feat-09), e começa pela spec 007.
Os contratos das specs 002, 004, 005 e 006 continuam valendo como estão nos respectivos
`contracts/servicos-compartilhados.md`.

**Prazo crítico**: os itens 1 e 2 deste contrato (transição de status e histórico) precisam estar
prontos até **03/11**, porque a feat-08 depende deles para começar.

## 1. Status da sessão (US-24; RBN-DEF-01.2)

| Item | Uso |
|---|---|
| `services_defesa.agendar_sessao(tcc, dados_basicos, dados_banca, autor) -> Defesas` | **única forma permitida** de criar uma sessão (`def_status` sempre nasce `AGENDADA`); grava o evento 'Agendamento' em `Historico_Defesas` internamente. A feat-08/feat-09 **não chamam** esta função (não criam sessão); está aqui só para documentar que `transicionar_status` nunca cria, apenas transiciona uma sessão já existente. |
| `services_defesa.transicionar_status(sessao, novo_status, autor, justificativa=None, **dados_evento) -> Defesas` | **única forma permitida** de mudar `def_status` de uma sessão **já existente** e gravar `Historico_Defesas`. Valida a transição completa `(status atual, novo_status)` contra a tabela fixa `TRANSICOES_VALIDAS` (research C2) — não só que o `novo_status` seja um valor do enum; não aceita `status_atual=None` (isso é `agendar_sessao`). **Pré-condição obrigatória de quem chama**: já ter travado a sessão (`select_for_update()`, dentro do mesmo `transaction.atomic()`) antes de chamar — a função não trava nada por si. A feat-08 chama para `StatusSessao.REALIZADA` (US-27, liberação do resultado), só a partir de `EM_ANDAMENTO`. |
| `services_defesa._travar_membros(ids_usuarios) -> list[Usuarios]` | função interna (não faz parte do contrato de chamada da feat-08/feat-09), citada aqui só para que quem compuser lógica própria de concorrência sobre `BancaDefesa` saiba o padrão já usado: trava os `Usuarios` propostos para a banca (`select_for_update()`, ordenados por pk, dentro do mesmo `transaction.atomic()`) **antes** de checar conflito de horário — necessário porque, numa criação, não existe ainda nenhuma sessão para travar (research C3). Quem for gravar outra entidade que também disputa a agenda do mesmo docente (ex.: feat-08 ao agendar uma reunião de avaliação) deve travar os mesmos `Usuarios`, na mesma ordem, para não reabrir a corrida. |
| `StatusSessao` (choices) | os 5 valores fixos; a feat-08 usa `StatusSessao.REALIZADA` |
| `services_turmas.STATUS_SESSAO_ATIVA` | `('Agendada', 'Reagendada', 'Em Andamento')`; já existe na spec 004, reaproveitado aqui e pela feat-08 para checar se há sessão ativa antes de outras ações |

A feat-08 **nunca** escreve em `def_status` nem em `Historico_Defesas` diretamente — sempre por
`transicionar_status` (FR-017, FR-023; SC-003); a feat-08 também nunca cria `Defesas` (só esta spec
cria, por `agendar_sessao`).

## 2. Histórico e membros efetivos (US-23, US-40; RBN-DEF-01.6, RBN-DEF-02.2)

| Item | Uso |
|---|---|
| `services_defesa.registrar_evento(sessao, tipo, justificativa, autor, **dados) -> HistoricoDefesas` | grava uma linha do histórico (`EventoDefesa`); chamada internamente por `agendar_sessao` (evento 'Agendamento') e por `transicionar_status` (demais transições de status), e diretamente por quem grava eventos sem mudança de status (Alteração da Banca, Acionamento do Suplente; a feat-08 segue o mesmo padrão se precisar registrar um evento sem mudar `def_status`). |
| `services_defesa.membros_efetivos(sessao) -> list[Usuarios]` | membros que **de fato** atuam na sessão — já considera o suplente acionado (substitui o titular ausente na composição real). A feat-08 usa para saber a quem pedir avaliação e para calcular o quórum; a feat-09 usa para a declaração de participação em banca. |
| `services_defesa.historico_da_sessao(sessao) -> queryset` | todas as linhas de `Historico_Defesas` da sessão, ordenadas por data/hora, **sem checagem de perfil** (quem chama decide se autoriza) — mesmo padrão de `services_tcc.historico_do_status` (spec 005, §2). |

## 3. Dados básicos da sessão (US-21; RBN-DEF-01.1)

| Item | Uso |
|---|---|
| `Defesas`, `DefesasPresenciais`, `DefesasRemotas` (modelos) | leitura direta pela feat-08/feat-09: `def_tcc`, `def_data`, `def_h_inicio`, `def_formato`, `dep_local`/`der_link`. Esta spec **não** grava `def_parecer`, `def_nota_final`, `def_ocorrencias`, `def_ata_final_path` nem `def_folha_aprovacao_path` — campos da feat-08/feat-09. |
| Template base `sigtcc/templates/defesa/sessao.html` | janela "Sessão de defesa" com blocos reservados `{% block avaliacao %}`, `{% block resultado %}`, `{% block documentos %}`, `{% block ouvintes %}`, `{% block ocorrencias %}`, para a feat-08/feat-09 preencherem sem reescrever o cabeçalho (data, horário, TCC, banca, status). |
| `BancaDefesa` (modelo) | leitura pela feat-08 para montar o formulário de avaliação por membro; a feat-08 **grava** `ban_assinatura_path` e `ban_data_envio` (campos que esta spec não usa). |

## 4. Componente do filtro de período (US-40, FR-025; RBN-DEF-01.5)

| Item | Uso |
|---|---|
| `services_defesa.componente_filtro_periodo(valor, periodo_letivo_atual) -> (data_inicial, data_final)` | resolve os atalhos (Período Letivo, Esta Semana, Este Mês, Próximos 30 Dias) ou o intervalo manual; reaproveitável pela agenda de defesas, pela lista de ouvintes e pelos relatórios (RAN-REL) da feat-08/feat-09, combinado com o filtro de Curso (`services_contas.filtro_de_curso`, spec 002). |

## 5. `popular_demo` (contrato)

`sigtcc/apps/cadastro/management/commands/popular_demo.py` ganha, por esta spec, TCCs "Apto para
Defesa" (um por curso) e uma sessão em cada um dos 5 valores de `StatusSessao`, criados só por
`services_defesa` (nunca `Defesas.objects.create()` direto, para já nascerem com `Historico_Defesas`
coerente). A feat-08 e a feat-09 reaproveitam esse cenário para testar sem montar os dados do zero.

## 6. Serviço que esta spec consome, ainda não entregue pela feat-08

| Item | Uso |
|---|---|
| `services_avaliacoes.descartar_avaliacoes(sessao, membro=None)` | **stub** nesta spec (`services_defesa.py`), chamado no cancelamento (todas as notas), na alteração de banca (só o membro substituído) e no acionamento do suplente (só o titular ausente). Quando a feat-08 entregar a função real (gravando em `Avaliacoes`), substitui o stub sem mudar a assinatura nem os 3 pontos de chamada. |

## 7. O que esta spec explicitamente NÃO faz (fronteira com a feat-08)

- Não implementa a liberação do resultado (US-27): a feat-08 chama `transicionar_status` para
  "Realizada" por conta própria, calculando o parecer e a nota conforme a própria regra dela
  (RBN-DEF-06.3).
- Não altera `services_turmas.encerrar_participacao` (spec 004): o encerramento da participação do
  aluno continua recusado quando há sessão de defesa ativa (MT30); não há cancelamento automático
  de sessão por esta via (Clarifications da spec 007, decisão revertida).
- Não grava nem lê `Avaliacoes`, `Criterios`, `Ouvintes` nem `PresencaOuvintes` — tabelas da
  feat-08/feat-09.
