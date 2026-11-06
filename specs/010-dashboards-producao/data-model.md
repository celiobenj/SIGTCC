# Data Model: Dashboards de Produção

**Nenhuma tabela, coluna ou migração nova.** Tudo é leitura.

## Tabelas só lidas

| Tabela (`db_table`) | Model | Campos Django | Para quê |
|---|---|---|---|
| `Turmas` | `Turmas` | `tur_ano`, `tur_semestre`, `tur_descricao`, `tur_cur` | Período, TCC 1 ou TCC 2 e curso da turma |
| `Alunos_Turmas` | `AlunosTurmas` | `mat_alu`, `mat_tur` | Matriculados e Alunos Vinculados |
| `TCCs` | `TCCs` | `tcc_status`, `tcc_alu`, `tcc_tur`, `tcc_titulo`, `tcc_modalidade`, `tcc_ari` | Trabalhos, agrupamentos e título |
| `Historico_Status_TCC` | `HistoricoStatusTCC` | `hst_tcc`, `hst_tur`, `hst_status_novo`, `hst_data_hora`, `hst_id` | Status por período e Desistências |
| `Orientacoes` | `Orientacoes` | `ori_tcc`, `ori_doc`, `ori_status`, `ori_data_inicio`, `ori_data_fim` | Painel e coluna Orientador |
| `Coorientacoes` | `Coorientacoes` | `coo_tcc`, `coo_doc`, `coo_status`, `coo_data_inicio`, `coo_data_fim` | Painel |
| `Artigos` | `Artigos` | `art`, `art_veiculo_publicacao`, `art_qualis_capes`, `art_status_submissao`, `art_homologacao`, `art_link_doi` | Artigos e Artigos Publicados |
| `Areas_Interesse` | `AreasInteresse` | `ari_nome` | Agrupamento |
| `Defesas` | `Defesas` | `def_tcc`, `def_data`, `def_status` | Sessões Realizadas |
| `Banca_Defesa` | `BancaDefesa` | `ban_def`, `ban_usu`, `ban_papel`, `ban_usu_substituido` | Bancas e membros efetivos |
| `Usuarios`, `Alunos`, `Docentes`, `Coordenadores`, `Secretarios`, `MembrosExternos`, `Cursos` | de mesmo nome | nome, `usu_status`, `doc_cur`, `cor_cur`, `sec_cur`, `mem_instituicao` | Linhas, filtros e padrão de curso |

## Dados calculados (sem armazenamento)

| Dado | Regra | Fonte |
|---|---|---|
| Status por período | Último registro do histórico do TCC na turma; sem TCC, Sem Proposta | FR-041; research R5 |
| Grupo | `GRUPOS_DE_STATUS`: Ativos, Com Sucesso, Sem Sucesso; Sem Proposta à parte | FR-040 |
| Matriculados | Vínculos em `Alunos_Turmas` das turmas do período | FR-042 |
| Total de Trabalhos | Ativos + Com Sucesso + Sem Sucesso | FR-061 |
| Orientandos e Coorientações | Alunos distintos por coluna e docente | FR-022, FR-023; research R7 |
| Fim efetivo do vínculo | Data de fim; sem ela, com TCC em Status final, a data do último registro do histórico | FR-022; research R18 |
| Total de Bancas | Sessões Realizadas distintas, papéis titulares | FR-024; research R7 |
| Artigos Publicados | Primeiro período de cada par aluno e link | FR-052; research R11 |

## Estruturas em memória

Definidas em [contracts/base-relatorios.md](contracts/base-relatorios.md): `Relatorio`, `Coluna`,
`Celula`, `Linha`, `SubLista`, `Kpi`, `Grafico`, `RelatorioRegistrado` e `Filtros`.

## Estados que entram nas contas

- **Status do TCC**: os 10 valores de `StatusTCC` caem em exatamente um grupo.
- **Sessão**: só `Realizada`.
- **Conta do docente**: Ativa sempre aparece na gestão; Inativa e Aguardando Ativação, só com atividade.
- **Vínculos**: `Ativa`, `Encerrada` e `Substituída` contam (FR-023).
