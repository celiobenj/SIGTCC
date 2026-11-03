# Data Model: Avaliação e Resultados do SIGTCC

**Feature**: [spec.md](spec.md) | **Plano**: [plan.md](plan.md) | **Data**: 2026-11-03

**Nenhuma tabela, coluna ou migração nova.** Todas as tabelas abaixo já existem (spec 001), com os
nomes, tipos e restrições do Modelo Lógico e Dicionário de Dados de 18/10. Esta página mapeia cada
model para a tabela oficial e diz o que a feature lê e grava.

## Criterios (`Criterios`, dicionário 3.1.4) — só leitura

| Campo | Tipo | Uso nesta feature |
|---|---|---|
| `cri_id` | INT, PK | ordem dos critérios no formulário e na janela de consulta |
| `cri_nome` | VARCHAR(100) | rótulo do critério |
| `cri_componente` | VARCHAR(20), `ComponenteCriterio` | Parte Escrita ou Parte Oral (libera a parte conforme o status, FR-011/FR-012) |
| `cri_descricao` | VARCHAR(255), nulo | texto de apoio na janela Critérios |
| `cri_desc_exemplar`, `cri_desc_competente`, `cri_desc_necessita_trabalho` | VARCHAR(255) | descrições dos conceitos (FR-002, FR-008) |
| `cri_peso` | DECIMAL(3,1) | cálculo da nota individual (research A3) |

Os 9 registros vêm da carga da spec 001; nenhuma tela grava nesta tabela (FR-001).

## Avaliacoes (`Avaliacoes`, dicionário 3.6.6) — leitura e gravação

| Campo | Tipo | Regra |
|---|---|---|
| (`ava_def_id`, `ava_usu_id`, `ava_cri_id`) | PK composta; FK composta para `Banca_Defesa` (adiada até o commit) e FK para `Criterios` | uma linha por membro e critério |
| `ava_conceito` | VARCHAR(30), `Conceito`, não nulo | Exemplar, Competente ou Necessita de Trabalho |
| `ava_nota` | DECIMAL(3,1), não nulo, CHECK 0 a 10 | dentro da faixa do conceito (FR-009): 8,0–10,0; 6,0–7,9; 0,0–5,9 |
| `ava_observacoes` | VARCHAR(500), nulo | opcional (FR-010); visível só ao autor (D7) |
| `ava_data_hora` | TIMESTAMP, não nulo | instante do último salvamento ou envio da linha |

- **Gravação**: só por `services_avaliacoes` (salvar, enviar, descartar). Um critério **liberado**
  esvaziado no Salvar apaga a linha; critérios bloqueados pelo status não são tocados; um critério
  com só conceito, só nota ou só observações não é gravado (MA-01; D4). Com a avaliação Enviada,
  nada é gravado até Reabrir.
- **Liberação**: depois de `def_data_liberacao_resultado` preenchido, nenhuma linha muda (FR-022).
- **Descarte** (`descartar_avaliacoes`): apaga as linhas do membro (ou de todos), na transação de
  quem chama (cancelamento, alteração da banca, acionamento do suplente; spec 007).

## BancaDefesa (`Banca_Defesa`, dicionário 3.6.4) — leitura; grava 2 colunas

| Campo | Uso nesta feature |
|---|---|
| `ban_def_id`, `ban_usu_id` (PK) | membro da sessão; `membros_efetivos` (spec 007) define quem avalia |
| `ban_papel` | papel exibido em Minhas bancas; "Orientador (Presidente)" libera o resultado |
| `ban_usu_substituido_id`, `ban_justificativa_substituicao` | só leitura (gravados pela spec 007) |
| `ban_assinatura_path` | **gravado**: caminho da cópia da imagem usada no envio (research A5); limpo ao reabrir, ao descartar e ao voltar a rascunho no reagendamento |
| `ban_data_envio` | **gravado**: instante do envio; limpo nas mesmas situações |

**Estado derivado** (dicionário 3.6.4; rótulos da RBN-DEF-06.8): Não avaliou / Rascunho salvo /
Enviada (research A2).

## Defesas (`Defesas`, dicionário 3.6.1) — leitura; grava 3 colunas

| Campo | Uso nesta feature |
|---|---|
| `def_status` | **só leitura**; a mudança "Em Andamento" → "Realizada" é feita por `services_defesa.transicionar_status` |
| `def_parecer` | **gravado**: parecer escolhido em TCC 2 (preliminar; limpo quando os 3 envios deixam de estar completos: reabrir, descartar, voltar a rascunho; D3 revista, Q-135) e o parecer final na liberação |
| `def_nota_final` | **gravado só na liberação**, com a homologação de artigo vigente nesse momento |
| `def_data_liberacao_resultado` | **gravado na liberação**; preenchido = registros imutáveis |
| `def_ocorrencias` | não usado (feat-09) |
| `def_ata_final_path`, `def_folha_aprovacao_path` | **não usados**: os PDFs são gerados sob demanda e não são gravados (decisão de 2026-11-03; research A9). Ficam sempre nulos; a eventual remoção das colunas é decisão do modelo lógico (índice Q-133) |

## Tabelas gravadas por serviço de outra spec

| Model (`db_table`) | Gravado por | Quando |
|---|---|---|
| `HistoricoDefesas` (`Historico_Defesas`) | `services_defesa.transicionar_status` (spec 007) | evento "Liberação do Resultado"; lida na janela Histórico (D15) |
| `TCCs` (`TCCs`) e `HistoricoStatusTCC` (`Historico_Status_TCC`) | `services_turmas.atualizar_status_tcc` (spec 005) | gatilho "Liberação do resultado" |
| `Docentes` (`Docentes`), `MembrosExternos` (`Membros_Externos`) | `services.salvar_assinatura` (spec 003) | "Salvar esta imagem no meu perfil" (`doc_assinatura_path`, `mem_assinatura_path`) |
| `Notificacoes` (`Notificacoes`, dicionário 3.7.1) | `services.notificar` (spec 004) | avisos MA-06 a MA-08 |

## Tabelas só lidas

| Model (`db_table`) | Por quê |
|---|---|
| `Turmas` (`Turmas`) | etapa (TCC 1 ou TCC 2) para o parecer e a Data Limite |
| `TurmasMarcos` (`Turmas_Marcos`) | Data Limite da entrega do tipo Versão Final (FR-033) |
| `Artigos` (`Artigos`) | Qualis A ou B homologado, por `services_artigos.tem_artigo_homologado_qualis_ab` |
| `Docentes`, `MembrosExternos` | caminho da assinatura do perfil para a opção "usar a do perfil" |
| `Cursos` (`Cursos`), `Secretarios` (`Secretarios`) | a quem avisar na liberação (Secretaria do curso) |

Os `db_table` acima são conferidos contra `models.py` no `/speckit-tasks`; onde o model usa outro
nome, vale o do dicionário.

## Transições

```text
Avaliação do membro:   Não avaliou ──Salvar──▶ Rascunho salvo ──Enviar──▶ Enviada
                                                   ▲                       │
                                                   └──Reabrir / reagendar──┘
                       (qualquer estado) ──descartar──▶ Não avaliou

Sessão (spec 007):     Em Andamento ──liberar_resultado──▶ Realizada  (só por transicionar_status)

TCC (spec 005):        Apto para Defesa ──Liberação do resultado──▶ Aprovado para TCC 2 | Aprovado
                                                                   | Aprovado com Correções | Reprovado
```
