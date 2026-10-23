# Contrato: o que a spec 006 (e outras) podem chamar (feature 005)

**Feature**: [../spec.md](../spec.md) | **Pesquisa**: [../research.md](../research.md)

Mudar qualquer item deste contrato é mudança de comportamento para a spec 006 (orientação, atas,
defesas e publicações — US-41, US-42, responsável Célio Benjamim) e começa pela spec 005. Os
serviços das specs 003 e 004 continuam valendo como estão em `specs/003-acesso-login/contracts/
servicos-compartilhados.md` e `specs/004-turmas-alunos/contracts/servicos-compartilhados.md`.

## 1. Dados da Proposta e do TCC (US-13; RBN-CAD-07.1, RAN-CAD-07 NFR Confidencialidade)

| Item | Uso |
|---|---|
| `TCCs` (modelo) | leitura direta pela 006: `tcc_titulo`, `tcc_subtitulo`, `tcc_modalidade`, `tcc_link_proposta`, `tcc_ari`, palavras-chave (`PalavrasChave_TCC`) |
| `services_tcc.pode_ver_resumo(usuario, tcc) -> bool` (FR-007a) | **única forma permitida** de decidir se `tcc_resumo` pode ser exibido a `usuario`: verdadeiro só para o próprio Aluno, o Orientador atual (`Orientacoes.ori_status='Ativa'`), um Docente com `Solicitacoes_Orientacao` pendente para esse TCC, o Coorientador do NUCOMP com `Coorientacoes.coo_status='Ativa'`, ou o Professor da Disciplina da turma do TCC. Título e Modalidade não têm essa restrição (visíveis também à banca, na agenda de defesas e nos relatórios). A spec 006 (telas de banca, agenda, atas) e o Épico 3 (relatórios) **devem chamar esta função** antes de exibir `tcc_resumo` em qualquer tela ou exportação nova — nunca reimplementar a regra (research C3; achado de revisão do `arquiteto-django`, importante #4). |
| `services_tcc.tcc_e_do_curso_com_orientador_automatico(tcc)` | reexporta `services_turmas.turma_tem_orientador_automatico(tcc.tcc_tur)`, para a 006 decidir se o Professor da Disciplina já é o Orientador (RBN-CAD-04.2) |

Esta spec **não** cria nem edita a Proposta por nenhum outro fluxo que o do Aluno (US-13); a 006
só lê.

## 2. Mudança e histórico de Status do TCC (US-14; RBN-CAD-08.3, 08.7, 08.8)

| Item | Uso |
|---|---|
| `services_turmas.atualizar_status_tcc(tcc, turma, autor, novo_status, gatilho)` | **única forma permitida** de mudar `tcc_status` de um TCC existente e gravar `Historico_Status_TCC`. Valida a **transição completa** `(tcc.tcc_status, gatilho) → novo_status` contra uma tabela fixa por gatilho (FR-008) — não só que o gatilho exista; uma transição fora da tabela levanta `ValueError` sem gravar nada. **Pré-condição obrigatória de quem chama**: já ter travado `Turmas` → `Alunos`/`AlunosTurmas` → `TCCs` (`select_for_update()`, dentro do mesmo `transaction.atomic()`) antes de chamar — a função não trava nada por si, e os dois gatilhos da 006 podem concorrer com os desta spec no mesmo TCC (ex.: liberação do resultado × homologação). A 006 chama esta função para os gatilhos "Indicação de Apto para Defesa" (US-42) e "Liberação do resultado" (US-27), calculando `novo_status` conforme a própria regra dela (RBN-DEF-06.3: nota final < 6,0 → Reprovado; TCC 1 ≥ 6,0 → Aprovado para TCC 2; TCC 2 ≥ 6,0 → Aprovado ou Aprovado com Correções, conforme o parecer da banca); a validação da transição pega um `novo_status` calculado errado antes de chegar ao banco. |
| `services_turmas.criar_tcc_com_historico(...)` | **não é usada pela 006** — só para os gatilhos de criação do TCC (Vínculo à turma, Transferência para TCC 2), ambos da spec 004. Citada aqui só para a 006 saber que existe e não deve chamá-la fora desses dois gatilhos. |
| `GatilhoStatusTCC` (choices) | os 7 gatilhos fixos; a 006 usa `GatilhoStatusTCC.INDICACAO_DE_APTO` e `GatilhoStatusTCC.LIBERACAO_DO_RESULTADO` |
| `services_turmas.STATUS_TCC_EM_CURSO` | `('Sem Proposta', 'Em Andamento', 'Apto para Defesa')`; já existe na spec 004, reaproveitado aqui |
| `services_tcc.historico_do_status(tcc) -> queryset` (FR-009, FR-010) | **única forma permitida** de consultar o histórico/trilha; não faz nenhuma checagem de perfil (quem chama decide se autoriza). A view desta spec (`views_tcc.historico_status`) aplica a checagem (Aluno dono, Orientador atual, Professor da Disciplina — **nunca** Secretaria do curso nem Coorientador do NUCOMP, Clarifications da spec 005, sessão 2026-10-22) antes de chamar. A 006 (tela de orientandos) chama esta função diretamente, aplicando a própria checagem (Orientador do TCC) por fora — nunca reimplementa a consulta nem estende o acesso ao Coorientador sem mudar esta spec primeiro (research C9). |

A 006 **nunca** escreve em `tcc_status` nem em `Historico_Status_TCC` diretamente — sempre por
`atualizar_status_tcc` (FR-012; SC-002), e sempre com o TCC já travado por ela mesma.

## 3. Estado das entregas (US-43, US-15, US-16, US-29, US-44; RBN-CAD-09.x)

| Item | Uso |
|---|---|
| `Turmas_Marcos`, `Entregas_Marcos` (modelos) | leitura pela 006: a entrega do tipo "Documento para Defesa" com `ent_status` em `('Entregue', 'Entregue com Atraso')` é pré-condição do botão "Apto para Defesa" (US-42) e o link mais recente (`Historico_Envios_Entregas`) é o documento enviado à banca no agendamento (US de Defesa) |
| `ent_correcoes_conferidas_em` (campo) | a 006 **grava** este campo (ação "Correções Conferidas" do Orientador, só em Sistemas de Informação com parecer "Aprovado com Correções") — é o único campo de `Entregas_Marcos` que a 006 escreve; tudo o mais nesta tabela é escrito só por esta spec (US-15, US-29, US-44) |
| `services_entregas.link_mais_recente(entrega)` | devolve o último `HistoricoEnviosEntregas` da entrega, para a 006 montar a notificação de agendamento com o link do Documento para Defesa |
| **Homologação** (FR-028, FR-029) | esta spec exige `ent_correcoes_conferidas_em` preenchido antes de liberar o botão Homologar quando o TCC é de Sistemas de Informação com parecer "Aprovado com Correções" (constraint de validação do dicionário, 3.4.2); a 006 deve gravar esse campo **antes** da homologação, não depois |

**Regra das entregas para outras features** (reaplicada da spec 004, agora também para a 006):
listas de entregas, lembretes de prazo e os relatórios de entrega consideram só alunos com
`Alunos_Turmas` atual na turma e com a participação não encerrada (`participacao_encerrada`,
spec 004). Registros de alunos excluídos ou transferidos ficam só como histórico (spec 004,
`remover_entregas_sem_envio`).

## 4. Avisos para o Épico 3 (Relatórios) e para a spec 006

- A confidencialidade do Resumo (item 1) vale para **qualquer** tela ou exportação nova, inclusive
  relatórios do Épico 3 que listem ou exportem `tcc_resumo`.
- `Historico_Status_TCC` é a base dos relatórios por período (RAN-REL-02); nenhuma feature deve
  recalcular Status a partir de outra fonte — sempre ler o histórico gravado por
  `atualizar_status_tcc`.
- Justificativas e mensagens de devolução são texto livre: exportações em CSV/XLSX devem
  neutralizar fórmulas (`=`, `+`, `-`, `@` no início da célula), mesma regra já registrada no
  contrato da spec 004 (research B25).
