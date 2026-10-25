# Contrato: o que outras features podem chamar (feature 006)

**Feature**: [../spec.md](../spec.md) | **Pesquisa**: [../research.md](../research.md) | **Modelo**: [../data-model.md](../data-model.md)

Mudar qualquer item deste contrato é mudança de comportamento para o módulo de Defesa (US-21 a
US-28, `sigtcc/apps/defesa`) e para os Relatórios (Épico 3), e começa pela spec 006. Continuam
valendo, como estão, os contratos das specs 002
(`specs/002-gestao-contas/contracts/servicos-compartilhados.md`), 003, 004 e 005, com as mudanças
dos itens de configuração do [plano](../plan.md#itens-de-configuração-código-de-outras-specs) (IC-04
a IC-07, IC-12 e IC-13).

## 1. Orientador e coorientadores de um TCC (composição da banca, US-23)

| Item | Uso |
|---|---|
| `services_orientacao.orientador_atual(tcc) -> Docentes \| None` | vínculo 'Ativa' em `Orientacoes` (no máximo um) |
| `services_orientacao.coorientadores_ativos(tcc) -> list` | `Coorientacoes` 'Ativa': docentes do NUCOMP (`coo_doc`) e externos (`coo_cext`); o convite pendente **não** entra (RBN-CAD-10.4) |
| `services_orientacao.papeis_no_tcc(usuario, tcc) -> set[str]` | **todos** os papéis por vínculo ativo (Q10): `"aluno"`, `"orientador"`, `"coorientador"`, `"professor"`; conjunto vazio sem vínculo. O Professor da Disciplina de turma com orientador automático tem `{"professor", "orientador"}`. A Defesa usa para decidir quem vê a sessão; orientador e coorientadores não podem ser avaliadores |
| `services_orientacao.e_orientador_atual(usuario, tcc) -> bool` e `e_coorientador_ativo(usuario, tcc) -> bool` | predicados para cada rota ou regra testar o papel que exige, sem depender de prioridade entre papéis (research R10) |

A Defesa **nunca** grava em `Orientacoes`, `Coorientacoes` ou `Solicitacoes_Orientacao`
diretamente, exceto pelo serviço do item 3.

## 2. Estado do TCC para o agendamento (US-21, US-24)

| Item | Uso |
|---|---|
| Status 'Apto para Defesa' | gravado só pela US-42, pelo `atualizar_status_tcc` (spec 005), gatilho "Indicação de Apto para Defesa"; a Defesa lista para agendamento os TCCs com esse Status |
| `services_orientacao.tcc_copiado(tcc) -> bool` | TCC 1 já copiado para o TCC 2 (Q6): fica só para consulta e não deve ser agendado |
| `services_orientacao.pode_alterar_no_tcc(tcc) -> bool` | turma não arquivada, participação não encerrada e TCC não copiado (FR-007) |

## 3. Cancelamento da troca de orientador no agendamento (FR-008; RBN-CAD-10.6)

| Item | Uso |
|---|---|
| `services_orientacao.cancelar_troca_no_agendamento(tcc, agora) -> SolicitacoesOrientacao \| None` | **obrigatória** na confirmação do agendamento (US-24), dentro da mesma transação, com quem chama tendo travado **na ordem completa turma → aluno (`Alunos`) → TCC** (research R2), para não entrar em deadlock com o envio ou o aceite da troca, que travam turma → aluno → TCC → conta → solicitação. `agora` MUST ser o mesmo valor gravado em `Historico_Defesas.hdf_data_hora` do evento 'Agendamento' (FR-050; research R3): é essa igualdade que faz o link mostrar "Este pedido foi cancelado porque a defesa foi agendada". Cancela o pedido de Troca de Orientação pendente, mantém o orientador atual e avisa o Aluno e o docente no sistema (MO-06) na mesma transação (as notificações são linhas do banco; só e-mails ficam para depois do commit). Sem pedido pendente, devolve `None` e não faz nada. |

A troca e o Substituir/Remover de coorientador são bloqueados enquanto houver `Defesas` com
`def_status` 'Agendada', 'Reagendada' ou 'Em Andamento' (RBN-CAD-10.6, 10.7). A 006 lê esse status;
quem o grava é a Defesa.

## 4. Aproveitamento do artigo na nota final (US-27; FR-039; RBN-CAD-12.3, RBN-DEF-06.2)

| Item | Uso |
|---|---|
| `services_artigos.tem_artigo_homologado_qualis_ab(tcc) -> bool` | verdadeiro com `art_homologacao='Homologado'` e Qualis A1 a A4 ou B1 a B4. A US-27 chama **no momento da liberação**, com o TCC **já travado** (turma → aluno → TCC), na mesma transação que dispara o gatilho "Liberação do resultado", e aplica a nota final mínima 6,0. Como a 006 também trava o TCC antes de gravar em `Artigos` (research R8 e R9), uma homologação ou alteração concorrente fica antes ou depois da liberação, nunca no meio. A apresentação perante a banca continua obrigatória |
| `services_artigos.resultado_liberado(tcc) -> bool` | gatilho "Liberação do resultado" no histórico **desse** TCC (R7). Depois dele, o Coordenador não pode recusar um artigo Homologado (US-20 E3); alterações do Aluno ou do Orientador continuam desfazendo a decisão (Q16), mas a nota já liberada não muda |

A US-27 **não** grava em `Artigos`: vale a homologação existente no momento da liberação
(RBN-CAD-12.3; RBN-DEF-06.4).

## 5. Motivo do cancelamento (FR-050)

| Item | Uso |
|---|---|
| `services_orientacao.MotivoCancelamento` | enum Python (`AGENDAMENTO`, `ENCERRAMENTO`, `DOCENTE_VIROU_ORIENTADOR`, `COPIA_TCC_2`, `TURMA_ARQUIVADA`, `ALUNO`); não é coluna |
| `services_orientacao.link_da_solicitacao(sol) -> str` | único lugar que monta o link de um pedido (rota 12) ou convite (rota 13); usado por toda notificação que aponta para a solicitação e pela dedução do motivo TURMA_ARQUIVADA |
| `services_orientacao.motivo_do_cancelamento(sol) -> MotivoCancelamento` | dedução pela igualdade exata de instante, com as consultas fixas do research R3, na ordem do FR-050 |
| `services_orientacao.cancelar_pendentes_da_turma(turma, agora)` | chamada só por `services_turmas.arquivar_turma` (IC-12), com a turma, os alunos e os TCCs já travados; cancela os pedidos e convites pendentes e grava, na mesma transação e com o mesmo `agora`, a MO-26 ao docente de cada um, com o link da solicitação (FR-053; dedução do motivo TURMA_ARQUIVADA, research R3) |

**Regra para qualquer feature que cancele solicitações** (Defesa, ou mudanças futuras das specs 004
e 005): calcular `agora = timezone.now()` **uma vez** no evento e gravar `sol_data_resposta` com
**esse mesmo** objeto no registro do evento (histórico da defesa, histórico do Status ou início do
vínculo de orientação). É proibido truncar o instante (por exemplo, `replace(microsecond=0)`), usar
`Now()` do banco, `auto_now` ou `auto_now_add` nesses campos, ou chamar `timezone.now()` de novo no
mesmo evento. Sem isso, o motivo aparece como "cancelado pelo aluno".

## 6. Avisos para o Épico 3 (Relatórios)

- Quantidade de orientandos e de coorientações por docente (RAN-REL; já citada na spec 002): ler
  `Orientacoes` e `Coorientacoes` com `*_status='Ativa'`; o convite pendente não conta.
- Atas não guardam o autor (Q-102). Relatórios de assiduidade contam `Encontro_Orientacao` por TCC e
  por período (`enc_data`).
- O Resumo da Proposta continua restrito a `pode_ver_resumo` (contrato da spec 005, §1).
- Os textos livres (pauta, metas, comentários, veículo) são exportados com neutralização de fórmulas
  (`=`, `+`, `-`, `@`), como no contrato da spec 004.
- No TCC 2 (linha nova, Q6), o artigo aparece uma vez por TCC. Relatórios por aluno devem
  considerar só o TCC atual (`tcc_copiado` falso), como a tela do Coordenador.
