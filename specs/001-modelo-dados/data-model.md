# Data Model: Modelo de dados do SIGTCC

**Feature**: [spec.md](spec.md) | **Plano**: [plan.md](plan.md) | **Pesquisa**: [research.md](research.md)

Fonte única: `docs/fonte/Modelo_Logico_e_Dicionario_18_10.md` (seções 2 e 3). Este documento não
cria tabela, coluna nem restrição nova: mapeia cada tabela e coluna do dicionário para o modelo
Django, com o app, o atributo Python e a restrição que garante cada regra. Se algo aqui divergir do
dicionário, vale o dicionário e este documento deve ser corrigido. As seções "Transições" são
informativas (vêm da matriz de 17/10, não do dicionário) e não fazem parte do contrato.

## Convenções

- **Atributo**: igual à coluna, exceto FK (sem `_id`, com `db_column`) e `Usuarios.password`
  (coluna `usu_senha`). Ver [contracts/modelos-orm.md](contracts/modelos-orm.md).
- **Tipos**: `INT` → `IntegerField` (`AutoField` na PK identity); `VARCHAR(n)` →
  `CharField(max_length=n)`; `CHAR(10)` → `CharFixoField(max_length=10)`; `DECIMAL(3,1)` →
  `DecimalField(3, 1)`; `TIMESTAMP` → `TimestampField` (campo próprio, `db_type` `timestamp`, com
  `USE_TZ=False`; research R1); `TIME` → `TimeField`;
  `DATE` → `DateField`; `BOOLEAN` → `BooleanField`.
- **Nulo = Sim** → `null=True, blank=True`. **Nulo = Não** → padrão do Django.
- **PK identity** → `AutoField(primary_key=True)` (BY DEFAULT, D4).
- **FK** → `on_delete=PROTECT` (R5); `related_name` explícito quando há mais de uma FK para o mesmo
  modelo.
- **CHECK de domínio** → `CheckConstraint(condition=Q(<campo>__in=<Choices>.values))`; campos
  anuláveis aceitam também `NULL`.
- **Nome das restrições**: `<tipo>_<db_table em minúsculas>_<sufixo>`, com tipo `ck` (CHECK), `uq`
  (unicidade) ou `fk` (FK criada por SQL). Sufixo: o nome da coluna nos CHECKs de domínio e de
  faixa; uma descrição curta nos demais. Até 63 caracteres; nomes únicos no projeto (`models.E032`).
- **PK composta**: `pk = models.CompositePrimaryKey(...)` com os nomes de coluna (`attname`), na
  ordem do dicionário. Confirmar o SQL gerado com `sqlmigrate` na implementação (research D3).
- **Índices**: o Django cria índices nas FKs e índices `_like` em `CharField` único ou PK. Não são
  colunas e não contrariam o dicionário; o teste de conformidade os ignora (research R11).
- **Rastreabilidade**: cada classe tem docstring em português com as US e RBN que atende
  (constituição, princípio II).

## Domínios (`TextChoices`)

| Classe | App | Valores | Usada em |
|---|---|---|---|
| `StatusConta` | cadastro | Aguardando Ativação, Ativa, Inativa, Expirada | `usu_status` |
| `Titulacao` | cadastro | Especialista, Mestre, Doutor | `doc_titulacao`, `mem_titulacao` |
| `DescricaoTurma` | cadastro | TCC 1, TCC 2 | `tur_descricao` |
| `StatusTurma` | cadastro | Ativa, Arquivada | `tur_status` |
| `DiaSemana` | cadastro | segunda-feira, terça-feira, quarta-feira, quinta-feira, sexta-feira, sábado | `tur_dia_da_semana` |
| `TipoEventoTurma` | cadastro | Exclusão, Transferência | `hat_tipo_evento` |
| `TipoEntrega` | cadastro | Proposta, Documento para Defesa, Versão Final, Outra | `tma_tipo` |
| `StatusEntrega` | cadastro | Aguardando Envio, Entregue, Entregue com Atraso, Não Entregue, Devolvida para Ajuste, Homologada | `ent_status` |
| `ModalidadeTCC` | cadastro | Monografia, Artigo Científico | `tcc_modalidade` |
| `StatusTCC` | cadastro | Sem Proposta, Em Andamento, Apto para Defesa, Aprovado para TCC 2, Aprovado, Aprovado com Correções, Concluído, Reprovado, Desistente, Jubilado | `tcc_status`, `hst_status_anterior`, `hst_status_novo` |
| `OrigemOrientacao` | cadastro | Pedido Aceito, Automático | `ori_origem` |
| `StatusOrientacao` | cadastro | Ativa, Encerrada | `ori_status` |
| `StatusCoorientacao` | cadastro | Ativa, Substituída, Encerrada | `coo_status` |
| `TipoSolicitacao` | cadastro | Orientação, Troca de Orientação, Coorientação | `sol_tipo` |
| `StatusSolicitacao` | cadastro | Aguardando Resposta, Aguardando Aceite, Aceito, Recusado, Cancelado | `sol_status` (combinação com o tipo em `ck_solicitacoes_orientacao_status_por_tipo`) |
| `GatilhoStatusTCC` | cadastro | Vínculo à turma, Proposta salva, Transferência para TCC 2, Indicação de Apto para Defesa, Liberação do resultado, Homologação da Versão Final, Encerramento da participação | `hst_gatilho` |
| `QualisCapes` | cadastro | A1, A2, A3, A4, B1, B2, B3, B4, C | `art_qualis_capes` |
| `StatusSubmissao` | cadastro | Submetido, Em Revisão, Aceito, Publicado, Rejeitado | `art_status_submissao` |
| `Homologacao` | cadastro | Em Análise, Homologado, Recusado | `art_homologacao` |
| `ComponenteCriterio` | defesa | Parte Escrita, Parte Oral | `cri_componente` |
| `FormatoSessao` | defesa | Presencial, Remota | `def_formato` |
| `StatusSessao` | defesa | Agendada, Em Andamento, Realizada, Reagendada, Cancelada | `def_status`, `hdf_status_anterior`, `hdf_status_novo` |
| `Parecer` | defesa | Reprovado, Aprovado para TCC 2, Aprovado, Aprovado com Correções | `def_parecer` |
| `PapelBanca` | defesa | Orientador (Presidente), 1º Avaliador, 2º Avaliador, Suplente | `ban_papel` |
| `Conceito` | defesa | Exemplar, Competente, Necessita de Trabalho | `ava_conceito` |
| `EventoDefesa` | defesa | Agendamento, Reagendamento, Cancelamento, Início Automático, Acionamento do Suplente, Alteração da Banca, Liberação do Resultado | `hdf_evento` |

Os valores de status coincidem com o `Glossario_Status` da matriz de 17/10 (D7).

---

## App `cadastro` (27 tabelas)

### Cursos — `Cursos` [US-39][RBN-CAD-14.1]

| Coluna | Atributo | Campo |
|---|---|---|
| cur_id | cur_id | AutoField PK |
| cur_nome | cur_nome | CharField(100) |
| cur_descricao | cur_descricao | CharField(255), nulo |

Carga inicial: 3 linhas (`0003_carga_cursos`).

### EquivalenciaCursos — `Equivalencia_Cursos` [US-08][RBN-CAD-05.7]

| Coluna | Atributo | Campo |
|---|---|---|
| eqc_codigo_uea | eqc_codigo_uea | CharField(20) PK |
| eqc_cur_id | eqc_cur | FK → Cursos |

Carga inicial: vazia (FR-016).

### Disciplinas — `Disciplinas`

| Coluna | Atributo | Campo |
|---|---|---|
| dis_id | dis_id | AutoField PK |
| dis_codigo | dis_codigo | CharField(20), `unique` |
| dis_nome | dis_nome | CharField(100), nulo |
| dis_descricao | dis_descricao | CharField(255), nulo |

### AreasInteresse — `Areas_Interesse` [US-13][RBN-CAD-08.1]

| Coluna | Atributo | Campo |
|---|---|---|
| ari_id | ari_id | AutoField PK |
| ari_nome | ari_nome | CharField(100), `unique` |

Carga inicial: 10 linhas (`0004_carga_areas_interesse`).

### Usuarios — `Usuarios` (AUTH_USER_MODEL)

| Coluna | Atributo | Campo |
|---|---|---|
| usu_id | usu_id | AutoField PK |
| usu_nome | usu_nome | CharField(150) |
| usu_email | usu_email | CharField(100), nulo, `unique` (R3) |
| usu_senha | password | CharField(255), nulo (D1) |
| usu_status | usu_status | CharField(30), `StatusConta` |
| usu_link_gerado_em | usu_link_gerado_em | TimestampField, nulo |

Restrições: `ck_usuarios_usu_status`. `last_login = None`; sem `PermissionsMixin`; `is_active`
derivado de `usu_status` (D1). `__str__` retorna `usu_nome` (o e-mail pode ser nulo). `save()` e
`create_user` gravam e-mail vazio como `None`; `create_user` converte depois de `normalize_email`,
que devolve `""` para `None` (research R3).

### Alunos — `Alunos`

| Coluna | Atributo | Campo |
|---|---|---|
| alu_id | alu | OneToOneField → Usuarios, PK |
| alu_matricula | alu_matricula | CharFixoField(10), `unique` |
| alu_codigo_curso | alu_codigo_curso | CharField(20) |

Restrições: `ck_alunos_alu_matricula` (`^[0-9]{10}$`). `alu_codigo_curso` não é FK
(validado pela aplicação contra `Equivalencia_Cursos`).

### Docentes — `Docentes`

| Coluna | Atributo | Campo |
|---|---|---|
| doc_id | doc | OneToOneField → Usuarios, PK |
| doc_titulacao | doc_titulacao | CharField(20), `Titulacao` |
| doc_cur_id | doc_cur | FK → Cursos |
| doc_assinatura_path | doc_assinatura_path | CharField(255), nulo |

Restrições: `ck_docentes_doc_titulacao`.

### MembrosExternos — `MembrosExternos`

| Coluna | Atributo | Campo |
|---|---|---|
| mem_id | mem | OneToOneField → Usuarios, PK |
| mem_titulacao | mem_titulacao | CharField(20), `Titulacao` |
| mem_instituicao | mem_instituicao | CharField(150) |
| mem_assinatura_path | mem_assinatura_path | CharField(255), nulo |
| mem_validade_ate | mem_validade_ate | DateField, nulo |

Restrições: `ck_membrosexternos_mem_titulacao`.

### Secretarios — `Secretarios`

| Coluna | Atributo | Campo |
|---|---|---|
| sec_id | sec | OneToOneField → Usuarios, PK |
| sec_cur_id | sec_cur | FK → Cursos |

"Uma Secretaria ativa por curso" fica na aplicação (dicionário 3.2.5; fora do escopo, FR-019).

### CoorientadoresExternos — `CoorientadoresExternos`

| Coluna | Atributo | Campo |
|---|---|---|
| cext_id | cext_id | AutoField PK |
| cext_nome | cext_nome | CharField(150) |
| cext_email | cext_email | CharField(100), nulo, `unique` (R3; `save()` grava vazio como `None`) |
| cext_instituicao | cext_instituicao | CharField(150), nulo |

### Coordenadores — `Coordenadores`

| Coluna | Atributo | Campo |
|---|---|---|
| cor_cur_id | cor_cur | OneToOneField → Cursos, PK |
| cor_doc_id | cor_doc | OneToOneField → Docentes (`unique`) |

### Turmas — `Turmas`

| Coluna | Atributo | Campo |
|---|---|---|
| tur_id | tur_id | AutoField PK |
| tur_identificador | tur_identificador | CharField(30), `unique` |
| tur_descricao | tur_descricao | CharField(10), `DescricaoTurma` |
| tur_doc_id | tur_doc | FK → Docentes |
| tur_dis_id | tur_dis | FK → Disciplinas |
| tur_cur_id | tur_cur | FK → Cursos |
| tur_ano | tur_ano | IntegerField |
| tur_semestre | tur_semestre | IntegerField |
| tur_dia_da_semana | tur_dia_da_semana | CharField(20), `DiaSemana` |
| tur_hora_inicio | tur_hora_inicio | TimeField |
| tur_hora_termino | tur_hora_termino | TimeField |
| tur_local | tur_local | CharField(100) |
| tur_status | tur_status | CharField(20), `StatusTurma` |

Restrições: `ck_turmas_tur_descricao`, `ck_turmas_tur_status`, `ck_turmas_tur_dia_da_semana`,
`ck_turmas_tur_semestre` (1 ou 2), `ck_turmas_tur_ano` (1000 a 9999),
`ck_turmas_horario` (`tur_hora_termino > tur_hora_inicio`).

### AlunosTurmas — `Alunos_Turmas`

| Coluna | Atributo | Campo |
|---|---|---|
| mat_alu_id | mat_alu | FK → Alunos |
| mat_tur_id | mat_tur | FK → Turmas |
| mat_data_inscricao | mat_data_inscricao | TimestampField |

PK: `pk = CompositePrimaryKey("mat_alu_id", "mat_tur_id")`.

### HistoricoAlunosTurmas — `Historico_Alunos_Turmas`

| Coluna | Atributo | Campo |
|---|---|---|
| hat_id | hat_id | AutoField PK |
| hat_alu_id | hat_alu | FK → Alunos |
| hat_tur_origem_id | hat_tur_origem | FK → Turmas (`related_name="historicos_origem"`) |
| hat_tur_destino_id | hat_tur_destino | FK → Turmas, nulo (`related_name="historicos_destino"`) |
| hat_tipo_evento | hat_tipo_evento | CharField(20), `TipoEventoTurma` |
| hat_justificativa | hat_justificativa | CharField(500) |
| hat_data_hora | hat_data_hora | TimestampField |
| hat_usu_id | hat_usu | FK → Usuarios |

Restrições: `ck_historico_alunos_turmas_hat_tipo_evento`.

### TurmasMarcos — `Turmas_Marcos`

| Coluna | Atributo | Campo |
|---|---|---|
| tma_id | tma_id | AutoField PK |
| tma_tur_id | tma_tur | FK → Turmas |
| tma_tipo | tma_tipo | CharField(30), `TipoEntrega` |
| tma_titulo | tma_titulo | CharField(100) |
| tma_instrucao | tma_instrucao | CharField(1000), nulo |
| tma_data_limite | tma_data_limite | TimestampField |

Restrições: `ck_turmas_marcos_tma_tipo`; `uq_turmas_marcos_tipo_por_turma` (`tma_tur`, `tma_tipo`)
com `condition=~Q(tma_tipo="Outra")`.

### EntregasMarcos — `Entregas_Marcos`

| Coluna | Atributo | Campo |
|---|---|---|
| ent_id | ent_id | AutoField PK |
| ent_tma_id | ent_tma | FK → TurmasMarcos |
| ent_alu_id | ent_alu | FK → Alunos |
| ent_status | ent_status | CharField(30), `StatusEntrega` |
| ent_feedback | ent_feedback | CharField(500), nulo |
| ent_data_avaliacao | ent_data_avaliacao | TimestampField, nulo |
| ent_correcoes_conferidas_em | ent_correcoes_conferidas_em | TimestampField, nulo |

Restrições: `ck_entregas_marcos_ent_status`; `uq_entregas_marcos_aluno_atividade` (`ent_tma`,
`ent_alu`).

### HistoricoEnviosEntregas — `Historico_Envios_Entregas`

| Coluna | Atributo | Campo |
|---|---|---|
| hen_id | hen_id | AutoField PK |
| hen_ent_id | hen_ent | FK → EntregasMarcos |
| hen_link | hen_link | CharField(500) |
| hen_data_envio | hen_data_envio | TimestampField |

### TCCs — `TCCs`

| Coluna | Atributo | Campo |
|---|---|---|
| tcc_id | tcc_id | AutoField PK |
| tcc_alu_id | tcc_alu | FK → Alunos |
| tcc_tur_id | tcc_tur | FK → Turmas |
| tcc_ari_id | tcc_ari | FK → AreasInteresse, nulo |
| tcc_modalidade | tcc_modalidade | CharField(30), nulo, `ModalidadeTCC` |
| tcc_titulo | tcc_titulo | CharField(250), nulo |
| tcc_subtitulo | tcc_subtitulo | CharField(250), nulo |
| tcc_resumo | tcc_resumo | CharField(1000), nulo |
| tcc_link_proposta | tcc_link_proposta | CharField(500), nulo |
| tcc_status | tcc_status | CharField(50), `StatusTCC` |
| tcc_justificativa_encerramento | tcc_justificativa_encerramento | CharField(500), nulo |

Restrições: `ck_tccs_tcc_status`; `ck_tccs_tcc_modalidade` (aceita nulo);
`ck_tccs_campos_obrigatorios_com_proposta` (R7; Clarifications Q1);
`uq_tccs_aluno_turma` (`tcc_alu`, `tcc_tur`).

**Transições de `tcc_status`** — *informativo, fora do contrato*. Fonte: RBN-CAD-08.3 da matriz de
17/10 (gatilho de cada valor); o estado de origem ("De") é inferido e deve ser confirmado nas specs
das features que aplicam as transições (Épicos 1 e 2). O banco não restringe transições.

| De (inferido) | Para | Gatilho (`hst_gatilho`) | Fonte |
|---|---|---|---|
| — | Sem Proposta | Vínculo à turma | RBN-CAD-08.3 (RBN-CAD-05.1, 05.2, 05.5) |
| Sem Proposta | Em Andamento | Proposta salva | RBN-CAD-08.3, RBN-CAD-07.1 |
| Aprovado para TCC 2 | Em Andamento | Transferência para TCC 2 | RBN-CAD-08.3, RBN-CAD-08.6 |
| Em Andamento | Apto para Defesa | Indicação de Apto para Defesa | RBN-CAD-08.3, RBN-CAD-11.5 |
| Apto para Defesa | Aprovado para TCC 2 / Aprovado / Aprovado com Correções / Reprovado | Liberação do resultado | RBN-CAD-08.3, RBN-DEF-06.3, RBN-DEF-06.4 |
| Aprovado / Aprovado com Correções | Concluído | Homologação da Versão Final | RBN-CAD-08.3, RBN-CAD-09.5 |
| status com Proposta | Desistente / Reprovado / Jubilado | Encerramento da participação | RBN-CAD-08.3, RBN-CAD-08.4; spec, Clarifications Q1 |

### Orientacoes — `Orientacoes`

| Coluna | Atributo | Campo |
|---|---|---|
| ori_id | ori_id | AutoField PK |
| ori_tcc_id | ori_tcc | FK → TCCs |
| ori_doc_id | ori_doc | FK → Docentes |
| ori_origem | ori_origem | CharField(20), `OrigemOrientacao` |
| ori_status | ori_status | CharField(20), `StatusOrientacao` |
| ori_data_inicio | ori_data_inicio | TimestampField |
| ori_data_fim | ori_data_fim | TimestampField, nulo |

Restrições: `ck_orientacoes_ori_origem`, `ck_orientacoes_ori_status`;
`uq_orientacoes_uma_ativa_por_tcc` (`ori_tcc`) com `condition=Q(ori_status="Ativa")`.

### Coorientacoes — `Coorientacoes`

| Coluna | Atributo | Campo |
|---|---|---|
| coo_id | coo_id | AutoField PK |
| coo_tcc_id | coo_tcc | FK → TCCs |
| coo_doc_id | coo_doc | FK → Docentes, nulo |
| coo_cext_id | coo_cext | FK → CoorientadoresExternos, nulo |
| coo_status | coo_status | CharField(20), `StatusCoorientacao` |
| coo_data_inicio | coo_data_inicio | TimestampField |
| coo_data_fim | coo_data_fim | TimestampField, nulo |

Restrições: `ck_coorientacoes_coo_status`; `ck_coorientacoes_docente_ou_externo` (R7);
`uq_coorientacoes_docente_ativo` (`coo_tcc`, `coo_doc`) e `uq_coorientacoes_externo_ativo`
(`coo_tcc`, `coo_cext`), ambas com `condition=Q(coo_status="Ativa")`.

### PalavrasChaveTCC — `PalavrasChave_TCC`

| Coluna | Atributo | Campo |
|---|---|---|
| pal_tcc_id | pal_tcc | FK → TCCs |
| pal_palavra | pal_palavra | CharField(100) |

PK: `pk = CompositePrimaryKey("pal_tcc_id", "pal_palavra")`. O limite de 1 a 5 por TCC é da aplicação.

### SolicitacoesOrientacao — `Solicitacoes_Orientacao`

| Coluna | Atributo | Campo |
|---|---|---|
| sol_id | sol_id | AutoField PK |
| sol_tcc_id | sol_tcc | FK → TCCs |
| sol_doc_id | sol_doc | FK → Docentes |
| sol_tipo | sol_tipo | CharField(20), `TipoSolicitacao` |
| sol_status | sol_status | CharField(20), `StatusSolicitacao` |
| sol_data_solicitacao | sol_data_solicitacao | TimestampField |
| sol_data_resposta | sol_data_resposta | TimestampField, nulo |

Restrições: `ck_solicitacoes_orientacao_sol_tipo`; `ck_solicitacoes_orientacao_status_por_tipo` (R7):
'Orientação'/'Troca de Orientação' → Aguardando Resposta, Aceito, Recusado, Cancelado;
'Coorientação' → Aguardando Aceite, Aceito, Recusado, Cancelado;
`uq_solicitacoes_orientacao_pedido_pendente` (`sol_tcc`) com
`condition=Q(sol_tipo__in=["Orientação", "Troca de Orientação"], sol_status="Aguardando Resposta")`.

### HistoricoStatusTCC — `Historico_Status_TCC`

| Coluna | Atributo | Campo |
|---|---|---|
| hst_id | hst_id | AutoField PK |
| hst_tcc_id | hst_tcc | FK → TCCs |
| hst_tur_id | hst_tur | FK → Turmas |
| hst_status_anterior | hst_status_anterior | CharField(50), nulo, `StatusTCC` |
| hst_status_novo | hst_status_novo | CharField(50), `StatusTCC` |
| hst_gatilho | hst_gatilho | CharField(100), `GatilhoStatusTCC` |
| hst_data_hora | hst_data_hora | TimestampField |
| hst_usu_id | hst_usu | FK → Usuarios |

Restrições: `ck_historico_status_tcc_hst_status_anterior` (aceita nulo), `ck_historico_status_tcc_hst_status_novo`,
`ck_historico_status_tcc_hst_gatilho`.

### Artigos — `Artigos`

| Coluna | Atributo | Campo |
|---|---|---|
| art_id | art | OneToOneField → TCCs, PK |
| art_veiculo_publicacao | art_veiculo_publicacao | CharField(150), nulo |
| art_link_doi | art_link_doi | CharField(500) |
| art_qualis_capes | art_qualis_capes | CharField(5), nulo, `QualisCapes` |
| art_status_submissao | art_status_submissao | CharField(30), nulo, `StatusSubmissao` |
| art_homologacao | art_homologacao | CharField(20), nulo, `Homologacao` |
| art_homologado_por | art_homologado_por | FK → Usuarios, nulo, `db_column="art_homologado_por"` |
| art_data_homologacao | art_data_homologacao | TimestampField, nulo |

Restrições: `ck_artigos_art_qualis_capes`, `ck_artigos_art_status_submissao`,
`ck_artigos_art_homologacao` (todas aceitam nulo).

### EncontroOrientacao — `Encontro_Orientacao`

| Coluna | Atributo | Campo |
|---|---|---|
| enc_id | enc_id | AutoField PK |
| enc_tcc_id | enc_tcc | FK → TCCs |
| enc_data | enc_data | DateField |
| enc_pauta | enc_pauta | CharField(2000) |
| enc_metas | enc_metas | CharField(2000) |

### ComentariosEncontro — `Comentarios_Encontro`

| Coluna | Atributo | Campo |
|---|---|---|
| com_id | com_id | AutoField PK |
| com_enc_id | com_enc | FK → EncontroOrientacao |
| com_usu_id | com_usu | FK → Usuarios |
| com_texto | com_texto | CharField(1000) |
| com_data_hora | com_data_hora | TimestampField |

### Notificacoes — `Notificacoes`

| Coluna | Atributo | Campo |
|---|---|---|
| not_id | not_id | AutoField PK |
| not_usu_id | not_usu | FK → Usuarios |
| not_mensagem | not_mensagem | CharField(500) |
| not_link_tela | not_link_tela | CharField(255), nulo |
| not_data_hora | not_data_hora | TimestampField |
| not_lida | not_lida | BooleanField(`db_default=False`) (R6) |

---

## App `defesa` (9 tabelas)

### Criterios — `Criterios` [US-25][RBN-DEF-04.1]

| Coluna | Atributo | Campo |
|---|---|---|
| cri_id | cri_id | AutoField PK |
| cri_nome | cri_nome | CharField(100) |
| cri_componente | cri_componente | CharField(20), `ComponenteCriterio` |
| cri_descricao | cri_descricao | CharField(255), nulo |
| cri_desc_exemplar | cri_desc_exemplar | CharField(255) |
| cri_desc_competente | cri_desc_competente | CharField(255) |
| cri_desc_necessita_trabalho | cri_desc_necessita_trabalho | CharField(255) |
| cri_peso | cri_peso | DecimalField(3, 1) |

Restrições: `ck_criterios_cri_componente`, `ck_criterios_cri_peso` (0,0 a 10,0).

Carga inicial (`0004_carga_criterios_provisorios`):

| Componente | Critério | Peso |
|---|---|---|
| Parte Escrita | Relevância do Tema | 0,5 |
| Parte Escrita | Metodologia | 2,0 |
| Parte Escrita | Revisão da Literatura | 1,0 |
| Parte Escrita | Resultados e Discussões | 2,0 |
| Parte Escrita | Conclusões | 0,5 |
| Parte Escrita | Redação | 1,0 |
| Parte Oral | Organização | 1,0 |
| Parte Oral | Domínio do Assunto | 1,5 |
| Parte Oral | Postura perante a Banca | 0,5 |

Descritores provisórios (FR-014), iguais para os 9 critérios até a troca (FR-014a):
- Exemplar: `PROVISÓRIO – Exemplar (nota de 8,0 a 10,0). Texto oficial pendente da planilha de avaliação da EST/UEA.`
- Competente: `PROVISÓRIO – Competente (nota de 6,0 a 7,9). Texto oficial pendente da planilha de avaliação da EST/UEA.`
- Necessita de Trabalho: `PROVISÓRIO – Necessita de Trabalho (nota de 0,0 a 5,9). Texto oficial pendente da planilha de avaliação da EST/UEA.`

`cri_descricao` fica nulo.

### Ouvintes — `Ouvintes`

| Coluna | Atributo | Campo |
|---|---|---|
| ouv_id | ouv_id | AutoField PK |
| ouv_matricula | ouv_matricula | CharFixoField(10), `unique` |
| ouv_nome | ouv_nome | CharField(150) |

Restrições: `ck_ouvintes_ouv_matricula`.

### Defesas — `Defesas`

| Coluna | Atributo | Campo |
|---|---|---|
| def_id | def_id | AutoField PK |
| def_tcc_id | def_tcc | FK → cadastro.TCCs |
| def_data | def_data | DateField |
| def_h_inicio | def_h_inicio | TimeField |
| def_formato | def_formato | CharField(20), `FormatoSessao` |
| def_status | def_status | CharField(30), `StatusSessao` |
| def_parecer | def_parecer | CharField(30), nulo, `Parecer` |
| def_nota_final | def_nota_final | DecimalField(3, 1), nulo |
| def_ocorrencias | def_ocorrencias | CharField(2000), nulo |
| def_data_liberacao_resultado | def_data_liberacao_resultado | TimestampField, nulo |
| def_ata_final_path | def_ata_final_path | CharField(255), nulo |
| def_folha_aprovacao_path | def_folha_aprovacao_path | CharField(255), nulo |

Restrições: `ck_defesas_def_formato`, `ck_defesas_def_status`, `ck_defesas_def_parecer` (aceita
nulo), `ck_defesas_def_nota_final` (0,0 a 10,0 ou nulo).

**Transições de `def_status`** — *informativo, fora do contrato*. Fonte: RBN-DEF-01.2 da matriz de
17/10 e descrições de `Historico_Defesas` no dicionário (3.6.7); o estado de origem é inferido e
deve ser confirmado na spec da feature de defesa. O banco não restringe transições.

| De (inferido) | Para | Evento (`hdf_evento`) | Fonte |
|---|---|---|---|
| — | Agendada | Agendamento | RBN-DEF-01.2 (RBN-DEF-03.2); dicionário 3.6.7 |
| Agendada / Reagendada | Reagendada | Reagendamento | RBN-DEF-01.2 (RBN-DEF-03.3) |
| Agendada / Reagendada | Cancelada | Cancelamento | RBN-DEF-01.2 (RBN-DEF-03.3) |
| Agendada / Reagendada | Em Andamento | Início Automático | RBN-DEF-01.2; dicionário seção 4, item 7 |
| Em Andamento | Realizada | Liberação do Resultado | RBN-DEF-01.2 (RBN-DEF-06.4) |
| (sem mudança) | (nulo) | Acionamento do Suplente, Alteração da Banca | dicionário 3.6.7 (`hdf_status_novo`) |

### DefesasPresenciais — `Defesas_Presenciais`

| Coluna | Atributo | Campo |
|---|---|---|
| dep_def_id | dep_def | OneToOneField → Defesas, PK |
| dep_local | dep_local | CharField(100) |

### DefesasRemotas — `Defesas_Remotas`

| Coluna | Atributo | Campo |
|---|---|---|
| der_def_id | der_def | OneToOneField → Defesas, PK |
| der_link | der_link | CharField(500) |

### BancaDefesa — `Banca_Defesa`

| Coluna | Atributo | Campo |
|---|---|---|
| ban_def_id | ban_def | FK → Defesas |
| ban_usu_id | ban_usu | FK → cadastro.Usuarios (`related_name="bancas"`) |
| ban_papel | ban_papel | CharField(30), `PapelBanca` |
| ban_usu_substituido_id | ban_usu_substituido | FK → cadastro.Usuarios, nulo (`related_name="substituicoes_banca"`) |
| ban_justificativa_substituicao | ban_justificativa_substituicao | CharField(500), nulo |
| ban_assinatura_path | ban_assinatura_path | CharField(255), nulo |
| ban_data_envio | ban_data_envio | TimestampField, nulo |

PK: `pk = CompositePrimaryKey("ban_def_id", "ban_usu_id")`. Restrições: `ck_banca_defesa_ban_papel`.

### PresencaOuvintes — `Presenca_Ouvintes`

| Coluna | Atributo | Campo |
|---|---|---|
| pre_def_id | pre_def | FK → Defesas |
| pre_ouv_id | pre_ouv | FK → Ouvintes |

PK: `pk = CompositePrimaryKey("pre_def_id", "pre_ouv_id")`.

### Avaliacoes — `Avaliacoes`

| Coluna | Atributo | Campo |
|---|---|---|
| ava_def_id | ava_def | FK → Defesas, `db_constraint=False`, `db_index=False` (D3; o prefixo da PK já indexa a coluna) |
| ava_usu_id | ava_usu | FK → cadastro.Usuarios, `db_constraint=False` (D3) |
| ava_cri_id | ava_cri | FK → Criterios |
| ava_conceito | ava_conceito | CharField(30), `Conceito` |
| ava_nota | ava_nota | DecimalField(3, 1) |
| ava_observacoes | ava_observacoes | CharField(500), nulo |
| ava_data_hora | ava_data_hora | TimestampField |

PK: `pk = CompositePrimaryKey("ava_def_id", "ava_usu_id", "ava_cri_id")`. Restrições: `ck_avaliacoes_ava_conceito`,
`ck_avaliacoes_ava_nota` (0,0 a 10,0); `fk_avaliacoes_banca_defesa` criada por `RunSQL` na
migração `0002_fk_composta_avaliacoes` (D3), com o SQL:

```sql
ALTER TABLE "Avaliacoes" ADD CONSTRAINT fk_avaliacoes_banca_defesa
    FOREIGN KEY (ava_def_id, ava_usu_id) REFERENCES "Banca_Defesa" (ban_def_id, ban_usu_id)
    ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
-- reverse_sql:
ALTER TABLE "Avaliacoes" DROP CONSTRAINT fk_avaliacoes_banca_defesa;
```

Como o ORM não conhece essa relação, excluir uma `BancaDefesa` com avaliações não levanta
`ProtectedError`: a recusa vem do banco como `IntegrityError` no fim da transação (contrato, §4).

### HistoricoDefesas — `Historico_Defesas`

| Coluna | Atributo | Campo |
|---|---|---|
| hdf_id | hdf_id | AutoField PK |
| hdf_def_id | hdf_def | FK → Defesas |
| hdf_evento | hdf_evento | CharField(30), `EventoDefesa` |
| hdf_status_anterior | hdf_status_anterior | CharField(30), nulo, `StatusSessao` |
| hdf_status_novo | hdf_status_novo | CharField(30), nulo, `StatusSessao` |
| hdf_data_anterior | hdf_data_anterior | DateField, nulo |
| hdf_hora_anterior | hdf_hora_anterior | TimeField, nulo |
| hdf_data_nova | hdf_data_nova | DateField, nulo |
| hdf_hora_nova | hdf_hora_nova | TimeField, nulo |
| hdf_membro_removido_id | hdf_membro_removido | FK → cadastro.Usuarios, nulo (`related_name="+"`) |
| hdf_membro_incluido_id | hdf_membro_incluido | FK → cadastro.Usuarios, nulo (`related_name="+"`) |
| hdf_justificativa | hdf_justificativa | CharField(500), nulo |
| hdf_data_hora | hdf_data_hora | TimestampField |
| hdf_usu_id | hdf_usu | FK → cadastro.Usuarios, nulo (`related_name="eventos_defesa"`) |

Restrições: `ck_historico_defesas_hdf_evento`, `ck_historico_defesas_hdf_status_anterior`,
`ck_historico_defesas_hdf_status_novo` (ambas aceitam nulo).

---

## Conferência

- Tabelas: 27 (`cadastro`) + 9 (`defesa`) = 36.
- Colunas extras: nenhuma (D1: `Usuarios` tem exatamente as 6 colunas do dicionário).
- Tabelas fora das 36: só as internas do framework (`django_migrations`, `django_content_type`,
  `django_session`, `auth_permission`, `auth_group`, `auth_group_permissions`), sem dados de
  negócio (FR-020). O `django.contrib.admin` não é instalado nesta feature (D1), então não há
  `django_admin_log`.
- Desvio registrado: identidade BY DEFAULT (D4, spec FR-003).
- Domínios: 26 classes `TextChoices` (19 em `cadastro`, 7 em `defesa`).
- `TimestampField`: 21 colunas (todas as `TIMESTAMP` do dicionário).
