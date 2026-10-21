# Data Model: Turmas e Alunos do SIGTCC

**Feature**: [spec.md](spec.md) | **Plano**: [plan.md](plan.md) | **Pesquisa**: [research.md](research.md)

Esta feature **não cria tabela nem coluna** (FR-028). Lê e grava tabelas da spec 001
(`specs/001-modelo-dados/data-model.md`). A única migração é de dados: a carga de
`Equivalencia_Cursos` (FR-015a).

## Tabelas usadas

| Tabela (classe Django) | Lidas | Gravadas | Onde |
|---|---|---|---|
| `Turmas` (`Turmas`) | todas as colunas | todas (cadastro, edição); `tur_status` (arquivamento); exclusão da linha | US-07 |
| `Disciplinas` (`Disciplinas`) | `dis_codigo` | nova linha quando o Código da Disciplina não existe | US-07 (B3) |
| `Cursos` (`Cursos`) | `cur_id`, `cur_nome` | — | turma, equivalência, orientação automática |
| `Equivalencia_Cursos` (`EquivalenciaCursos`) | `eqc_codigo_uea`, `eqc_cur_id` | carga inicial (EST08MCPD, EST31MSII, EST03MLV) | US-08 (FR-015, FR-015a) |
| `Usuarios` (`Usuarios`) | `usu_id`, `usu_nome`, `usu_status` | nova conta do aluno ('Aguardando Ativação', sem e-mail, sem senha); `usu_nome` (edição) | US-08 |
| `Alunos` (`Alunos`) | `alu_matricula`, `alu_codigo_curso` | nova linha; `alu_codigo_curso` (edição) | US-08 |
| `Alunos_Turmas` (`AlunosTurmas`) | `mat_alu_id`, `mat_tur_id` | nova linha (matrícula, transferência); exclusão da linha (exclusão do aluno, transferência) | US-08, US-09 |
| `TCCs` (`TCCs`) | todas | novo TCC 'Sem Proposta'; novo TCC carregado do TCC 1 (Q6); `tcc_tur` (transferência); `tcc_status` e `tcc_justificativa_encerramento` (encerramento); exclusão do TCC 'Sem Proposta' (Q8) | US-08, US-09 |
| `Historico_Status_TCC` (`HistoricoStatusTCC`) | — | nova linha a cada transição; exclusão das linhas do TCC excluído (Q8) | RBN-CAD-08.7 |
| `Orientacoes` (`Orientacoes`) | ativas do TCC | orientação automática; `ori_status = 'Encerrada'` e `ori_data_fim` (B7, B13, B15); exclusão da automática do TCC excluído | RBN-CAD-04.2 |
| `Coorientacoes` (`Coorientacoes`) | ativas do TCC; existência (B14) | `coo_status = 'Encerrada'`, `coo_data_fim`; cópia no TCC 2 (B7) | RBN-CAD-05.6, 08.6 |
| `Solicitacoes_Orientacao` (`SolicitacoesOrientacao`) | pendentes do TCC; existência (B14) | `sol_status = 'Cancelado'`, `sol_data_resposta` = data do cancelamento (não é resposta do docente; a US-17 deve mostrar como "cancelado em") (encerramento, Q14; convites ao professor de destino na transferência, B13) | US-09, RBN-CAD-05.6 |
| `Encontro_Orientacao` (`EncontroOrientacao`) | existência (B14) | — | exclusão do aluno |
| `Entregas_Marcos` (`EntregasMarcos`) | do aluno nas entregas da turma | criação na matrícula e no destino da transferência; exclusão das sem envio (exclusão e origem da transferência) (B22, Q17) | US-08, US-09 |
| `Historico_Envios_Entregas` (`HistoricoEnviosEntregas`) | existência de envio (B22) | — | US-09, transferência |
| `PalavrasChave_TCC` (`PalavrasChaveTCC`), `Artigos` (`Artigos`) | do TCC 1; existência (B14) | cópia para o TCC 2, todas as colunas (B7) | RBN-CAD-08.6 |
| `Historico_Alunos_Turmas` (`HistoricoAlunosTurmas`) | por turma de origem | 'Exclusão' (sem destino) e 'Transferência' (com destino), com justificativa, autor, data e hora | RBN-CAD-05.4, 05.6, 05.8 |
| `Turmas_Marcos` (`TurmasMarcos`) | 'Versão Final' e todas as entregas da turma | exclusão das linhas da turma excluída (B4) | US-07 |
| `Defesas` (`defesa.Defesas`) | `def_status` dos TCCs da turma; existência (B14) | — | arquivamento, transferência, encerramento (Q14) |
| `Notificacoes` (`Notificacoes`) | — | aluno excluído; aluno e orientadores na transferência, sempre pelo `notificar()` (B21) | US-08, US-09 |
| `Secretarios`, `Docentes` (`Secretarios`, `Docentes`) | curso da Secretaria; Professor da Disciplina | — | permissões (B2) |

Nenhum identificador é informado em gravação (spec 001, FR-003).

## Regras de dados aplicadas pela aplicação

- **Turma**: Código da Disciplina `^[A-Z0-9]{1,20}$`; Identificador `^[A-Z0-9_]{1,30}$`, único; Ano com 4 dígitos; Semestre 1 ou 2; Dia da Semana de
  segunda-feira a sábado; término > início; Local até 100; Curso entre os 3 do NUCOMP. Descrição e
  Curso travados na turma que tem ou já teve aluno (Q15).
- **Aluno**: Matrícula `^\d{10}$` e única; Nome Completo só letras (com acentos) e espaços, até 150;
  Curso `^[A-Z0-9]{1,20}$` (código da UEA), reconhecido pela equivalência (código inteiro).
- **Vínculo**: uma vez por turma (PK composta de `Alunos_Turmas`); um TCC por aluno e turma
  (`uq_tccs_aluno_turma`).
- **Justificativas**: obrigatórias, até 500 caracteres (`hat_justificativa`,
  `tcc_justificativa_encerramento`), normalizadas (B18).
- **Notificação**: `not_mensagem` até 500 caracteres; o `notificar()` corta com "…" (B21).
- **Arquivo de importação**: até 2 MB, até 200 linhas de alunos (Q13), XLSX até 20 MB descompactado
  (B9).

## Transições do Status do TCC feitas por esta feature

| De | Para | Gatilho (`hst_gatilho`) | Responsável (`hst_usu`) | Requisito |
|---|---|---|---|---|
| — (TCC novo) | Sem Proposta | Vínculo à turma | Professor da Disciplina | FR-012, FR-013 |
| Aprovado para TCC 2 (TCC 1) | Em Andamento (TCC novo na turma de TCC 2) | Transferência para TCC 2 | Professor da Disciplina | FR-013 (Q6) |
| Em Andamento ou Apto para Defesa | Desistente, Reprovado ou Jubilado | Encerramento da participação | Professor da Disciplina | FR-024 |

A transferência (FR-022) não muda o Status: o mesmo TCC muda de turma, com o histórico.

## Estados da turma

| De | Para | Condição |
|---|---|---|
| (nova) | Ativa | cadastro (FR-003) |
| Ativa | Arquivada | sem TCC 'Em Andamento' ou 'Apto para Defesa', sem sessão 'Agendada', 'Reagendada' ou 'Em Andamento' e, em TCC 2, Data Limite da 'Versão Final' vencida (FR-007) |
| Ativa | (excluída) | nunca teve aluno (FR-006, Q12) |

## Outras transições

| Registro | De | Para | Quando |
|---|---|---|---|
| `Orientacoes`, `Coorientacoes` | Ativa | Encerrada (com data de fim) | encerramento (Q10); TCC 1 no B7; orientação automática e coorientação do novo orientador na transferência |
| `Solicitacoes_Orientacao` | Aguardando Resposta ou Aguardando Aceite | Cancelado | encerramento (Q14); convites ao professor de destino na transferência (B13) |
| `Entregas_Marcos` | (nova) | Aguardando Envio | matrícula; destino da transferência (B22) |
| `Entregas_Marcos` | qualquer (de vínculo anterior) | Aguardando Envio, sem avaliação | rematrícula ou transferência para turma onde o aluno já esteve; envios ficam no histórico (Q18) |

'Arquivada' não volta para 'Ativa' nesta feature.

## Dados fora das tabelas

| Dado | Onde fica | Validade |
|---|---|---|
| Prévia da importação | sessão do usuário (`importacao`: token, turma, instante, linhas válidas normalizadas e só número e motivo das com erro) | 30 minutos; sai da sessão antes de gravar ou ao cancelar; `token` marcado como usado (B10) |
| Exclusão de turma | `LOG_DIR/acesso.log` (evento `TURMA_EXCLUIDA`, com autor, data, hora e identificador) | rotação da spec 003 |
| Modelo de importação | gerado na hora (CSV UTF-8 com ";") | — |
