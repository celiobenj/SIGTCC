# Data Model: Orientação, Atas e Publicações (feature 006)

**Feature**: [spec.md](spec.md) | **Plano**: [plan.md](plan.md) | **Pesquisa**: [research.md](research.md)

**Nenhuma tabela, coluna, índice ou migração nova.** Todas as tabelas abaixo já existem desde a
spec 001 (`sigtcc/apps/cadastro/models.py` e `sigtcc/apps/defesa/models.py`), com os nomes, tipos e
restrições do Modelo Lógico e Dicionário de 18/10. Este documento registra **como a feature usa**
cada tabela: quem grava, as transições de estado e as regras derivadas, que são calculadas e não
gravadas.

## 1. Tabelas gravadas por esta feature

### `Solicitacoes_Orientacao` (dicionário 3.5.5; model `SolicitacoesOrientacao`)

| Campo | Uso nesta feature |
|---|---|
| `sol_tcc_id`, `sol_doc_id` | TCC do aluno; docente indicado (pedido) ou convidado (convite) |
| `sol_tipo` | 'Orientação' (US-17 A), 'Troca de Orientação' (US-17 D) ou 'Coorientação' (US-45) |
| `sol_status` | ver as transições abaixo |
| `sol_data_solicitacao` | instante do envio |
| `sol_data_resposta` | instante do aceite, da recusa ou do cancelamento; no cancelamento automático, **igual** ao instante do evento que o causou (FR-050; research R3) |

Transições (CHECK `ck_solicitacoes_orientacao_status_por_tipo` já garante os valores por tipo):

```text
Pedido (Orientação / Troca de Orientação):
  [novo] → Aguardando Resposta ─┬─ Aceitar (docente indicado)      → Aceito
                                ├─ Recusar (docente indicado)      → Recusado
                                ├─ Cancelar Pedido (Aluno)         → Cancelado  (motivo ALUNO)
                                ├─ Agendamento da defesa (só troca) → Cancelado (motivo AGENDAMENTO)
                                ├─ Encerramento da participação     → Cancelado (motivo ENCERRAMENTO)
                                ├─ Cópia para o TCC 2               → Cancelado (motivo COPIA_TCC_2)
                                └─ Arquivamento da turma            → Cancelado (motivo TURMA_ARQUIVADA)
Convite (Coorientação):
  [novo] → Aguardando Aceite ───┬─ Aceitar / Recusar (docente convidado) → Aceito / Recusado
                                ├─ Remover (Aluno)                       → Cancelado (ALUNO)
                                ├─ Docente passa a Orientador (troca aceita ou transferência)
                                │                                         → Cancelado (DOCENTE_VIROU_ORIENTADOR)
                                ├─ Encerramento da participação           → Cancelado (ENCERRAMENTO)
                                ├─ Cópia para o TCC 2                     → Cancelado (COPIA_TCC_2)
                                └─ Arquivamento da turma                  → Cancelado (TURMA_ARQUIVADA)
```

Regras:
- Um pedido pendente por TCC: índice `uq_solicitacoes_orientacao_pedido_pendente` (FR-047); a
  gravação roda num savepoint, e a violação vira o tratamento do duplo clique (research R2).
- Um convite pendente por docente e TCC, pela aplicação (D8): não há índice único para convite. A
  lista de Docentes do NUCOMP exclui quem já tem convite pendente, e a gravação, serializada pela
  trava do TCC (research R2), confere de novo antes de criar a linha.
- Toda solicitação aberta pela URL é buscada com `sol_tcc` igual ao TCC do contexto e com o
  `sol_tipo` da rota (research R10).
- Criar a solicitação MUST travar e conferir a conta 'Ativa' do docente
  (`travar_e_conferir_ativo`, spec 002; Q-68).

### `Orientacoes` (3.5.2; model `Orientacoes`)

| Evento | Gravação |
|---|---|
| Aceite de pedido de Orientação | nova linha 'Ativa', origem 'Pedido Aceito', `ori_data_inicio = agora` |
| Aceite de Troca de Orientação | a linha 'Ativa' anterior passa a 'Encerrada' com `ori_data_fim = agora`; nova linha 'Ativa' 'Pedido Aceito' com o mesmo `agora` |
| Turma com orientador automático, transferência e cópia para o TCC 2 | já gravados pela spec 004; o IC-04 passa a usar o mesmo `agora` do evento |
| Encerramento da participação | já gravado pela spec 004 (`encerrar_orientacoes_ativas`) |

Índice `uq_orientacoes_uma_ativa_por_tcc`: no máximo um orientador ativo (FR-047).

### `Coorientacoes` (3.5.3) e `CoorientadoresExternos` (3.2.6)

| Evento | `coo_status` |
|---|---|
| Aceite do convite (docente do NUCOMP) | nova linha 'Ativa' com `coo_doc` |
| Registro de "Externo ao NUCOMP" | nova linha 'Ativa' com `coo_cext` (registro reaproveitado pelo e-mail, sem alterar Nome e Instituição; Q13, Q15). A unicidade de `cext_email` no banco diferencia maiúsculas: a busca é por `iexact`, com `travar_email` e criação em savepoint (research R17) |
| Substituir | a anterior passa a 'Substituída' com `coo_data_fim`; a nova segue a regra de registro (D8) |
| Remover | 'Encerrada' com `coo_data_fim` (D8) |
| Troca de orientador aceita, ou transferência, quando o novo orientador era coorientador | 'Encerrada' (RBN-CAD-10.6; a transferência já é da spec 004) |
| Encerramento da participação | 'Encerrada' (spec 004) |

Restrições já existentes: `ck_coorientacoes_docente_ou_externo`, `uq_coorientacoes_docente_ativo` e
`uq_coorientacoes_externo_ativo`. O convite pendente **não** é linha de `Coorientacoes`: fica em
`Solicitacoes_Orientacao` até o aceite (RBN-CAD-10.4: "não conta como coorientação").

### `Encontro_Orientacao` (3.5.8) e `Comentarios_Encontro` (3.5.9)

| Campo | Regra |
|---|---|
| `enc_data` | obrigatória, não futura — "A Data do Encontro não pode ser futura". Comparada com `timezone.now().date()` (com `USE_TZ=False`, `timezone.localdate()` levanta erro; mesmo padrão de `permissoes.validade_vencida`) |
| `enc_pauta`, `enc_metas` | obrigatórias, até 2.000 caracteres (MO-19 acima do limite) |
| `com_usu_id`, `com_texto`, `com_data_hora` | só Orientador ou Coorientador com vínculo ativo; até 1.000 caracteres (MO-19) |

Ordem da lista: `enc_data` decrescente e, no mesmo dia, `enc_id` decrescente (D14). A ata não guarda
o autor (lacuna aceita, Q-102).

### `Artigos` (3.5.7)

| Campo | Regra |
|---|---|
| `art_id` | = `tcc_id` (um registro por TCC); só na modalidade Artigo Científico |
| `art_link_doi` | obrigatório, `https://`, até 500 |
| `art_veiculo_publicacao`, `art_qualis_capes`, `art_status_submissao` | opcionais (D10) |
| `art_homologacao`, `art_homologado_por`, `art_data_homologacao` | ver o ciclo abaixo (research R8) |

Ciclo do aproveitamento (RBN-CAD-12.3; dicionário 3.5.7; Q16), **antes e depois da liberação**:

```text
nulo ──(Status Aceito ou Publicado)──► Em Análise ──Homologar──► Homologado
                                          │  ▲                       │
                                          │  └──── Qualis, Status ou Link alterado ◄──┤
                                          └──Recusar──► Recusado ─────────────────────┘
Homologado ──Recusar──► Recusado   (só até a liberação do resultado; depois, MO-21, US-20 E3)
```

A nota já liberada não muda com transições posteriores: vale a homologação existente na liberação
(RBN-DEF-06.4; contrato §4). Toda gravação em `Artigos` trava turma → aluno → TCC → `Artigos`
(research R8, R9).

`art_homologado_por` e `art_data_homologacao` guardam só a decisão mais recente; cada decisão também
vai para o log (`EventoArtigo.APROVEITAMENTO_HOMOLOGADO`/`APROVEITAMENTO_RECUSADO`, enum local de
`services_artigos`; D10).

### `Entregas_Marcos.ent_correcoes_conferidas_em` (3.4.2)

O único campo de `Entregas_Marcos` que esta feature grava ("Correções Conferidas", FR-016). Volta a
nulo na devolução para ajuste (IC-07, Q2).

### `TCCs.tcc_status` e `Historico_Status_TCC` (3.5.1, 3.5.6)

Só pelo `atualizar_status_tcc` (spec 005), gatilho "Indicação de Apto para Defesa" (Em Andamento →
Apto para Defesa).

## 2. Tabelas só lidas

| Tabela | Para quê |
|---|---|
| `TCCs`, `PalavrasChave_TCC`, `Areas_Interesse` | blocos, linhas, "Ver proposta" (Resumo por `pode_ver_resumo`) e condição do Apto |
| `Turmas`, `Alunos_Turmas`, `Cursos`, `Coordenadores` | permissão por turma, turma arquivada, curso do Coordenador (`permissoes.curso_id_do_usuario`) |
| `Alunos` | trava da linha do aluno em toda gravação (research R2) |
| `Turmas_Marcos`, `Entregas_Marcos`, `Historico_Envios_Entregas` | coluna de entregas (status exibido) e entrega "Documento para Defesa" (Apto) |
| `Historico_Status_TCC` | resultado liberado (R7), TCC copiado (R6), motivo do cancelamento (R3) |
| `Notificacoes` | motivo TURMA_ARQUIVADA (R3): a MO-26 gravada pelo arquivamento com o mesmo instante e o link da solicitação. A 006 também grava notificações, sempre por `services.notificar` |
| `Historico_Alunos_Turmas` | histórico de orientação na transferência (FR-049) |
| `Historico_Defesas` (app `defesa`) | motivo AGENDAMENTO (evento 'Agendamento', R3); sessão Agendada, Reagendada ou Em Andamento bloqueia a troca e o Substituir/Remover (`Defesas.def_status`) |
| `Usuarios`, `Docentes`, `Alunos` | nomes, titulação, conta 'Ativa' (spec 002) |

## 3. Valores derivados (calculados, nunca gravados)

| Valor | Definição | Onde |
|---|---|---|
| `motivo_do_cancelamento(sol)` | FR-050, na ordem AGENDAMENTO, ENCERRAMENTO, DOCENTE_VIROU_ORIENTADOR, COPIA_TCC_2 (igualdade exata de instante, consultas fixas), TURMA_ARQUIVADA (notificação MO-26 com o mesmo instante), ALUNO | `services_orientacao` (R3) |
| `tcc_copiado(tcc)` / `tcc_de_origem(tcc)` | TCC 'Aprovado para TCC 2' com TCC mais novo do mesmo aluno / o TCC 1 de um TCC 2 | `services_orientacao` (R6) |
| `pode_alterar_no_tcc(tcc)` | turma não arquivada, participação não encerrada e TCC não copiado (FR-007, FR-046) | `services_orientacao` (R10) |
| `papeis_no_tcc(usuario, tcc)` | conjunto de papéis (aluno, orientador, coorientador, professor), só por vínculo ativo (Q10), com os predicados `e_orientador_atual` e `e_coorientador_ativo` | `services_orientacao` (R10) |
| `resultado_liberado(tcc)` | gatilho "Liberação do resultado" no histórico **desse** TCC | `services_artigos` (R7) |
| `etiqueta_aproveitamento(artigo)` | MO-22 ou o valor de `art_homologacao` | `services_artigos` (R8) |
| `estado_apto(tcc)` | ausente, sem entrega cadastrada, indisponível, disponível | `services_orientacao` (R16) |
| `historico_de_orientacao(tcc)` | vínculos encerrados ou substituídos e solicitações recusadas ou canceladas, por data | `services_orientacao` (FR-049) |
| `tem_artigo_homologado_qualis_ab(tcc)` | aproveitamento "Homologado" e Qualis A1 a A4 ou B1 a B4 | `services_artigos` (FR-039; contrato §4) |
