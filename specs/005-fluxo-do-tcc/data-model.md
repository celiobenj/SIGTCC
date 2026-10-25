# Data Model: Fluxo do TCC e Entregas do SIGTCC

**Feature**: [spec.md](spec.md) | **Pesquisa**: [research.md](research.md)

**Nenhuma tabela nem coluna nova.** As 6 entidades abaixo já existem em `sigtcc/apps/cadastro/
models.py` (spec 001, dicionário seções 3.4 e 3.5) e em `choices.py`. Esta spec só acrescenta
regras de transição e validação em `services_tcc.py`/`services_entregas.py` sobre o que já existe.

## TCCs (`TCCs`)

| Campo Django | Coluna | Tipo | Regra desta spec |
|---|---|---|---|
| `tcc_id` | `tcc_id` | PK | — |
| `tcc_alu` | `tcc_alu_id` | FK Alunos | — |
| `tcc_tur` | `tcc_tur_id` | FK Turmas | muda na transferência para TCC 2 (spec 004) |
| `tcc_ari` | `tcc_ari_id` | FK AreasInteresse, opcional | liberado só depois da Proposta salva (FR-004) |
| `tcc_modalidade` | `tcc_modalidade` | enum `ModalidadeTCC`, opcional até "Em Andamento" | obrigatório a partir de "Em Andamento" (constraint já existe) |
| `tcc_titulo` | `tcc_titulo` | até 250, opcional até "Em Andamento" | FR-001, FR-007 |
| `tcc_subtitulo` | `tcc_subtitulo` | até 250, opcional | FR-001 |
| `tcc_resumo` | `tcc_resumo` | até 1000, opcional até "Em Andamento" | FR-001, FR-007; confidencialidade FR-007a |
| `tcc_link_proposta` | `tcc_link_proposta` | até 500, opcional, `https://` | FR-001, FR-007 |
| `tcc_status` | `tcc_status` | enum `StatusTCC` | **somente gravado por** `services_turmas.criar_tcc_com_historico` (na criação) ou `services_turmas.atualizar_status_tcc` (numa transição) — nunca diretamente (FR-008, FR-012; research C2) |
| `tcc_justificativa_encerramento` | `tcc_justificativa_encerramento` | até 500, opcional | gravado pela spec 004 (US-09); esta spec só lê |

Restrições já existentes e usadas por esta spec: `UNIQUE (tcc_alu, tcc_tur)` (FR-002, "ainda não
existir Proposta dele nessa turma"); `CHECK` título/resumo/modalidade obrigatórios fora de "Sem
Proposta" (garante que FR-002/FR-005 não deixem a Proposta incompleta).

**Transições de `tcc_status`** (FR-008; `GatilhoStatusTCC`) — esta spec grava 2 dos 7 gatilhos
(demais já gravados pela spec 004 ou a gravar pela spec 006, todos pela mesma função):

| Gatilho | De | Para | Quem dispara |
|---|---|---|---|
| Vínculo à turma | — | Sem Proposta | spec 004 (matrícula) |
| **Proposta salva** | Sem Proposta | Em Andamento | **esta spec, US-13** |
| Transferência para TCC 2 | Aprovado para TCC 2 | Em Andamento | spec 004 (transferência/matrícula) |
| Indicação de Apto para Defesa | Em Andamento | Apto para Defesa | spec 006 |
| Liberação do resultado | Apto para Defesa | Aprovado para TCC 2 / Aprovado / Aprovado com Correções / Reprovado | spec 006 |
| **Homologação da Versão Final** | Aprovado / Aprovado com Correções | Concluído | **esta spec, US-44** |
| Encerramento da participação | Em Andamento / Apto para Defesa | Desistente / Reprovado / Jubilado | spec 004 |

Aluno "Sem Proposta" nunca é origem do gatilho "Encerramento da participação": a US-09 trata esse
caso pela exclusão do aluno da turma, não pelo encerramento (`STATUS_TCC_ENCERRAVEL` em
`services_turmas.py` só libera a partir de "Em Andamento" ou "Apto para Defesa"; achado da revisão
do `arquiteto-django`, bloqueante #2).

## PalavrasChave_TCC (`PalavrasChaveTCC`)

PK composta `(pal_tcc_id, pal_palavra)`. Regra desta spec: de 1 a 5 linhas por `tcc_id` (FR-004,
FR-007), sem duplicar `pal_palavra` para o mesmo TCC (Clarifications, sessão 2026-10-22; a PK
composta já impediria duplicata exata no banco, mas a validação do formulário evita o
`IntegrityError` e mostra a mensagem MF-03 ao aluno).

## Historico_Status_TCC (`HistoricoStatusTCC`)

Somente leitura para esta spec (exceto via `atualizar_status_tcc`, que é quem grava). Campos:
`hst_tcc`, `hst_tur` (turma no momento da mudança — preserva o período na transferência), `hst_
status_anterior` (nulo só no primeiro registro), `hst_status_novo`, `hst_gatilho` (enum já fixo),
`hst_data_hora`, `hst_usu` (responsável). Consulta exposta pelo FR-009 (trilha do FR-010 é uma
leitura derivada, sem tabela própria).

## Turmas_Marcos (`TurmasMarcos`)

Campos: `tma_tur`, `tma_tipo` (enum `TipoEntrega`: Proposta, Documento para Defesa, Versão Final,
Outra), `tma_titulo` (até 100), `tma_instrucao` (até 1000, opcional), `tma_data_limite`.
`UniqueConstraint` parcial já existe para impedir duplicar Proposta/Documento para Defesa/Versão
Final por turma (FR-014); "Outra" pode repetir.

## Entregas_Marcos (`EntregasMarcos`)

Campos: `ent_tma`, `ent_alu`, `ent_status` (enum `StatusEntrega`), `ent_feedback` (mensagem da
devolução mais recente, até 500), `ent_data_avaliacao` (homologação ou devolução), `ent_
correcoes_conferidas_em` (preenchido pelo Orientador antes da homologação em Sistemas de
Informação com parecer "Aprovado com Correções" — FR-029; esta spec só lê e valida esse campo na
homologação; quem grava é a ação "Correções Conferidas" da spec 006). `UniqueConstraint (ent_tma,
ent_alu)` já garante uma entrega por aluno por atividade (base de FR-015/FR-016).

## Historico_Envios_Entregas (`HistoricoEnviosEntregas`)

Campos: `hen_ent`, `hen_link` (até 500, `https://`), `hen_data_envio`. Cada envio e cada
substituição gera uma linha nova (nunca `UPDATE` do link); o status de envio (`ent_status`) é
calculado a partir do **primeiro** registro desta tabela para a entrega (research C7), e o link
"mais recente" exibido ao professor (FR-026) é o último registro por `hen_data_envio`.
