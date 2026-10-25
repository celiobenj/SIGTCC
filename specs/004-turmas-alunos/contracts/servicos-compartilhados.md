# Contrato: o que as outras features podem usar (feature 004)

**Feature**: [../spec.md](../spec.md) | **Pesquisa**: [../research.md](../research.md)

Mudar qualquer item deste contrato é mudança de comportamento para as outras features e começa pela
spec 004. Os serviços da spec 003 (base visual, `@perfil_requerido`, papéis, regra da Q27,
notificações, log) continuam valendo como estão em
`specs/003-acesso-login/contracts/servicos-compartilhados.md`.

## 1. Turma arquivada (FR-008; RBN-CAD-04.5) – `sigtcc.apps.cadastro.services_turmas`

| Item | Uso |
|---|---|
| `turma_arquivada(turma) -> bool` | consulta, sem trava; para decidir se um botão aparece |
| `exigir_turma_ativa(turma)` | idem; levanta `TurmaArquivada`; **não** garante a gravação |
| `travar_turma_ativa(tur_id) -> Turmas` | **obrigatória antes de gravar** em tabela ligada à turma: chamar dentro de `transaction.atomic()`; trava a turma (`select_for_update`), relê e levanta `TurmaArquivada` se arquivada (research B5, B17) |
| `TurmaArquivada` | exceção; a view mostra a MT-25 ("Esta turma está arquivada e só pode ser consultada.") |

Quem usa: entregas e envios (US-15, US-16, US-43), atas (US-19/20), agendamento de defesa (US-21),
Versão Final (US-34) e os lembretes de prazo (só turmas 'Ativa').

## 2. Participação encerrada (FR-025; RBN-CAD-08.5)

| Item | Uso |
|---|---|
| `participacao_encerrada(tcc) -> bool` | Status do TCC em `STATUS_PARTICIPACAO_ENCERRADA` ('Desistente', 'Reprovado', 'Jubilado') |
| `STATUS_TCC_EM_CURSO` | ('Sem Proposta', 'Em Andamento', 'Apto para Defesa'): TCC em curso numa turma (spec Q7). Não confundir com o "TCC ativo" da RBN-CAD-01.3 (spec 002) |

Quem usa: editar o TCC (US-13), indicar ou trocar orientador (US-17, US-18) e enviar entregas
(US-16): desabilitam o botão e recusam no serviço, sem exceção. Pedidos de orientação e convites de
coorientação pendentes são cancelados no encerramento (spec Q14; índice Q-40).

## 3. Turma, aluno e curso

| Item | Uso |
|---|---|
| `turma_para(usuario, tur_id, acao, travar=False) -> Turmas` | `acao` nas constantes `CONSULTAR`, `ALTERAR`, `TRANSFERIR`; confere existência (404), permissão (`PermissionDenied`) e, para alterar e transferir, turma arquivada (`TurmaArquivada`); com `travar=True`, chamar dentro de `transaction.atomic()` |
| `permissoes.pode_consultar_turma`, `pode_alterar_turma`, `pode_transferir` | regras por turma, em `permissoes.py` (B2) |
| `vinculo_na_turma(turma, alu_id) -> Alunos` | aluno matriculado na turma, senão 404 (B2) |
| `turma_tem_orientador_automatico(turma) -> bool` | TCC 2 de um curso em `CURSOS_COM_ORIENTADOR_AUTOMATICO` (`cargas.py`); renomear curso (US-39) exige revisar a constante |
| `curso_do_codigo(codigo) -> Cursos \| None` | curso do NUCOMP pelo código da UEA; `None` = "Código não reconhecido". Definida em `services.py` e reexportada por `services_turmas`; `services.curso_do_aluno` delega a ela |
| `criar_entregas_do_aluno(aluno, turma)`, `remover_entregas_sem_envio(aluno, turma)` | registros do aluno nas entregas da turma (spec Q17 e Q18; research B22). A US-43 cria os registros dos alunos já matriculados ao cadastrar uma entrega nova (índice Q-41) |

**Regra das entregas para as outras features**: listas de entregas, lembretes de prazo, a marcação
'Não Entregue' (US-15) e os relatórios de entrega consideram só alunos com `Alunos_Turmas` atual na
turma e com a participação não encerrada (`participacao_encerrada`). Registros com envio de alunos
excluídos ou transferidos ficam só como histórico. `Solicitacoes_Orientacao.sol_data_resposta` de
pedido 'Cancelado' pelo encerramento ou pela transferência é a data do cancelamento, não uma
resposta do docente.

A regra Q27 da spec 003 continua: o papel "Professor da Disciplina" vale com qualquer turma; alterar
dados exige ser o Professor **desta** turma, não arquivada.

## 4. Notificações e log (acréscimos ao contrato da spec 003; índice Q-42)

| Item | Uso |
|---|---|
| `services.notificar(usuario, mensagem, link=None)` | única forma de criar `Notificacoes`: corta em 500 caracteres com "…", aceita só link interno válido (`destino_da_notificacao`) e preenche data e hora (research B21) |
| `services.EventoAcesso.TURMA_EXCLUIDA` | `registrar_evento(TURMA_EXCLUIDA, conta=None, autor=<Professor>, detalhe="tur_id=<id> identificador=<identificador>")`, depois do commit |

## 5. Avisos para o Épico 3 (Relatórios)

- O aluno 'Aprovado para TCC 2' tem dois TCCs (o de TCC 1, com esse Status, e o de TCC 2) e o
  registro de publicação copiado: relatórios de publicações e de aproveitamento contam o aluno e a
  publicação uma vez, pelo TCC mais recente (research B7).
- Justificativas são texto livre: o exportador CSV e XLSX neutraliza fórmulas (`=`, `+`, `-`, `@` no
  início da célula) (research B25).
