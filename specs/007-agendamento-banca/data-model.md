# Data Model: Agendamento e Banca do SIGTCC

**Feature**: [spec.md](spec.md) | **Pesquisa**: [research.md](research.md)

**Nenhuma tabela nem coluna nova.** As 5 entidades abaixo já existem em
`sigtcc/apps/defesa/models.py` (spec 001, dicionário seções 3.6.1 a 3.6.4 e 3.6.7) e em
`choices.py`. Esta spec só acrescenta regras de transição e validação em `services_defesa.py`
sobre o que já existe.

## Defesas (`Defesas`)

| Campo Django | Coluna | Tipo | Regra desta spec |
|---|---|---|---|
| `def_id` | `def_id` | PK | — |
| `def_tcc` | `def_tcc_id` | FK TCCs | só TCC "Apto para Defesa" sem sessão ativa (FR-003) |
| `def_data` | `def_data` | Date | não anterior a hoje (FR-005) |
| `def_h_inicio` | `def_h_inicio` | Time | reserva automática de 1h (FR-002) |
| `def_formato` | `def_formato` | enum `FormatoSessao` | Presencial/Remota (FR-001, FR-004) |
| `def_status` | `def_status` | enum `StatusSessao` | **somente gravado por** `transicionar_status` (FR-017, FR-023; research C2) |
| `def_parecer` | `def_parecer` | enum `Parecer`, opcional | fora do escopo desta spec (feat-08) |
| `def_nota_final` | `def_nota_final` | Decimal, opcional | fora do escopo desta spec (feat-08) |
| `def_ocorrencias` | `def_ocorrencias` | até 2000, opcional | fora do escopo desta spec (feat-09) |
| `def_data_liberacao_resultado` | `def_data_liberacao_resultado` | Timestamp, opcional | fora do escopo desta spec (feat-08) |
| `def_ata_final_path`, `def_folha_aprovacao_path` | idem | opcional | fora do escopo desta spec (feat-09) |

**Restrição usada por esta spec**: `STATUS_SESSAO_ATIVA` (já definida em `services_turmas.py`,
spec 004) = `('Agendada', 'Reagendada', 'Em Andamento')` — um TCC não pode ter duas sessões
nesses status ao mesmo tempo (FR-003); esta spec reaproveita a mesma constante em
`services_defesa.py` (import de `services_turmas`, sem duplicar o valor).

**Transições de `def_status`** (FR-017; `EventoDefesa`) — esta spec grava 4 dos eventos (os
demais são da feat-08/feat-09, pela mesma função `transicionar_status`):

| Evento | De | Para | Quem dispara |
|---|---|---|---|
| **Agendamento** | — | Agendada | **esta spec, US-21/24** |
| **Reagendamento** | Agendada/Reagendada | Reagendada | **esta spec, US-24** |
| **Cancelamento** | Agendada/Reagendada/Em Andamento | Cancelada | **esta spec, US-24** |
| **Início Automático** | Agendada/Reagendada | Em Andamento | **esta spec, US-24** (view ou comando agendado) |
| **Acionamento do Suplente** | (sem mudar `def_status`) | — | **esta spec, US-23** (só histórico) |
| **Alteração da Banca** | (sem mudar `def_status`) | — | **esta spec, US-23** (só histórico) |
| Liberação do Resultado | Em Andamento | Realizada | feat-08 (US-27), via `transicionar_status` |

## DefesasPresenciais (`DefesasPresenciais`) / DefesasRemotas (`DefesasRemotas`)

Um para um com `Defesas` (`dep_def`/`der_def`, PK = FK). `dep_local`: texto livre até 100
caracteres (FR-001, FR-005). `der_link`: até 500 caracteres, `https://` (FR-001, FR-005). Só uma
das duas linhas existe por sessão, conforme `def_formato`; ao trocar o formato (FR-004), a linha
antiga é removida e a nova é criada.

## BancaDefesa (`BancaDefesa`)

PK composta `(ban_def_id, ban_usu_id)` — **um membro, um papel, uma linha**; não há como a mesma
pessoa ter duas linhas na mesma sessão (reforça FR-009, "nenhum docente repetido em dois papéis",
a nível de banco). Campos usados por esta spec: `ban_papel` (`PapelBanca`), `ban_usu_substituido`
e `ban_justificativa_substituicao` (acionamento do suplente e alteração de banca, FR-011, FR-013).
`ban_assinatura_path` e `ban_data_envio` são da feat-08 (avaliação), fora do escopo.

**Regra de atualização** (research C4): alterar um papel ou acionar o suplente **substitui** a
linha do membro trocado (`delete()` + `create()`, ou `update()` de `ban_papel` na linha do
suplente promovido) — não existe histórico de composição de banca na própria tabela; o histórico
fica só em `HistoricoDefesas` (`membro_removido`/`membro_incluido`).

## HistoricoDefesas (`HistoricoDefesas`)

Uma linha por evento (`EventoDefesa`), gravada só por `registrar_evento`/`transicionar_status`
(FR-023). Campos usados por esta spec: `hdf_status_anterior`/`hdf_status_novo` (transições),
`hdf_data_anterior`/`hdf_hora_anterior`/`hdf_data_nova`/`hdf_hora_nova` (reagendamento),
`hdf_membro_removido`/`hdf_membro_incluido` (alteração de banca e acionamento de suplente),
`hdf_justificativa`, `hdf_data_hora`, `hdf_usu` (responsável). Consulta exposta pelo FR-029
(`historico_da_sessao`, research C7), sem checagem de perfil — a view aplica a checagem.
