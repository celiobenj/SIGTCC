# Data Model: Documentação e Encerramento do SIGTCC

**Feature**: [spec.md](spec.md) | **Plano**: [plan.md](plan.md) | **Data**: 2026-11-04

**Nenhuma tabela, coluna, restrição ou migração nova.** Todas as tabelas já existem (spec 001) e
foram conferidas contra o dicionário de 18/10.

## Tabelas gravadas por esta feature

| Model Django | `db_table` | Dicionário | Colunas gravadas | Regra |
|---|---|---|---|---|
| `defesa.Ouvintes` | `Ouvintes` | 3.1.6 | `ouv_matricula` CHAR(10) AK, `ouv_nome` VARCHAR(150) | Criado na primeira presença da matrícula; nunca alterado nem apagado por esta feature (P4; Edge Cases). `CHECK ck_ouvintes_ouv_matricula` (`^[0-9]{10}$`) já existe |
| `defesa.PresencaOuvintes` | `Presenca_Ouvintes` | 3.6.5 | `pre_def_id`, `pre_ouv_id` (PK composta, FKs) | Uma linha por ouvinte na sessão; criada e apagada por `salvar_ouvintes` (research B9). A PK impede a mesma matrícula duas vezes na sessão |
| `defesa.Defesas` | `Defesas` | 3.6.1 | só `def_ocorrencias` VARCHAR(2000), nulo | Gravado por `registrar_ocorrencias` com a sessão Em Andamento e sem liberação (research B10); vazio grava `NULL` |

## Tabelas só lidas

| Model | `db_table` | Dicionário | Uso |
|---|---|---|---|
| `defesa.Defesas` | `Defesas` | 3.6.1 | `def_status`, `def_data`, `def_h_inicio`, `def_parecer`, `def_nota_final`, `def_data_liberacao_resultado` (liberado ⇔ não nulo) |
| `defesa.BancaDefesa` | `Banca_Defesa` | 3.6.4 | papel, substituído e `ban_assinatura_path` (assinatura impressa nos documentos) |
| `defesa.Avaliacoes`, `defesa.Criterios` | `Avaliacoes`, `Criterios` | 3.6.6, 3.1.4 | só por `services_avaliacoes.resultado_da_sessao` |
| `defesa.DefesasPresenciais`, `defesa.DefesasRemotas` | `Defesas_Presenciais`, `Defesas_Remotas` | 3.6.2, 3.6.3 | local (texto) ou link na agenda |
| `cadastro.Coordenadores` | `Coordenadores` | 3.3.1 | Coordenador do curso da turma (E2) |
| `cadastro.Docentes` | `Docentes` | 3.2.3 | `doc_titulacao`, `doc_assinatura_path` (Coordenador; E2 só com caminho vazio, Q-140) |
| `cadastro.MembrosExternos` | `MembrosExternos` | 3.2.4 | `mem_titulacao` |
| `cadastro.Secretarios` | `Secretarios` | 3.2.5 | Secretaria do curso (permissões, MX-09) |
| `cadastro.TCCs`, `cadastro.Turmas`, `cadastro.Cursos`, `cadastro.Alunos`, `cadastro.Usuarios` | idem | 3.5.1, 3.3.2, 3.1.1, 3.2.2, 3.2.1 | título, aluno, curso, etapa (TCC 1/2), turma arquivada, nome e e-mail |
| `cadastro.Notificacoes` | `Notificacoes` | 3.7.1 | gravada por `services.notificar` (MX-03, MX-09) |

## Colunas sem uso

`Defesas.def_ata_final_path` e `Defesas.def_folha_aprovacao_path` continuam sempre nulas: os
documentos são sob demanda (spec 008; índice Q-133).

## Dados calculados (sem armazenamento)

| Dado | Origem | Regra |
|---|---|---|
| Resultado da Ata e da Folha | `resultado_da_sessao(sessao)` + `membros_efetivos(sessao)` | Congelado na liberação; titulações e Coordenador lidos no download (Clarifications) |
| Situação da Ata (E2) | `situacao_da_ata(sessao)` | `SEM_COORDENADOR`, `SEM_ASSINATURA` ou `None` (research B5) |
| Código de validação | `codigo_de_validacao(sessao, usuario)` | HMAC-SHA256 com a `SECRET_KEY`, Base32, 16 caracteres (research B6) |
| Horas complementares | uma linha de `Presenca_Ouvintes` em sessão Realizada | 2 horas por sessão assistida (RBN-DEF-08.4); valor fixo exibido, não gravado |

## Estados que governam as ações

| Ação | Status da sessão | Outras condições |
|---|---|---|
| Baixar Ata Final | Realizada (liberada) | `situacao_da_ata` = `None` |
| Baixar Folha de Aprovação | Realizada (liberada) | TCC 2 e parecer Aprovado ou Aprovado com Correções |
| Baixar Declaração | Realizada (liberada) | membro efetivo |
| Editar ouvintes | Em Andamento ou Realizada | turma não arquivada; Presidente da banca ou Professor da Disciplina |
| Ver ouvintes (só leitura) | Presidente e Professor da Disciplina: qualquer, com presenças (P3, turma arquivada); Secretaria do curso: Em Andamento ou Realizada (P6) | regra própria, sem depender de quem edita (revisão B-02) |
| Editar ocorrências | Em Andamento, sem liberação | turma não arquivada; Presidente da banca (B-03) |
| Agenda | Agendada ou Reagendada | — |
| Ouvintes das defesas | Realizada | Secretaria |
