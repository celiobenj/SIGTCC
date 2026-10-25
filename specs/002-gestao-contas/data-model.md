# Data Model: Gestão de Contas do SIGTCC

**Feature**: [spec.md](spec.md) | **Plano**: [plan.md](plan.md) | **Pesquisa**: [research.md](research.md)

**Nenhuma tabela nova** (princípio III). Todas as tabelas são da spec 001 e seguem o dicionário de
18/10. **Uma coluna nova**, aprovada pela autora do dicionário (Q-69; spec Q36):

| Tabela | Coluna | Tipo | Nulo? | Descrição |
|---|---|---|---|---|
| `MembrosExternos` | `mem_prorrogado_ate` | DATE | Sim | Data de validade dada pela última prorrogação manual (US-50); o recálculo pela banca (US-06) nunca deixa `mem_validade_ate` antes dela. Nula enquanto não houver prorrogação |

A cópia do dicionário em `docs/fonte/` recebe a coluna (seção 3.2.4 e a linha do modelo lógico) e a
nova descrição de `mem_validade_ate` (Q-44) no mesmo commit do model e da migração.

## 1. Tabelas escritas por esta feature

| Tabela (model) | Colunas usadas | Operações | FR |
|---|---|---|---|
| `Usuarios` (`Usuarios`) | `usu_nome`, `usu_email`, `usu_senha` (nula na criação), `usu_status` | cria; altera só `usu_nome` (`update_fields`, C20); muda status só nas ações próprias; e-mail só pela confirmação do link (C7) | FR-001 a FR-008, FR-024, FR-025, FR-029, FR-040, FR-043 |
| `Docentes` (`Docentes`) | `doc_titulacao`, `doc_cur_id` (Curso de Lotação) | cria; altera | FR-012, FR-016 |
| `Coordenadores` (`Coordenadores`) | `cor_cur_id` (PK), `cor_doc_id` (único) | cria, troca e apaga a linha do papel (C6) | FR-013, FR-014, FR-045 |
| `Secretarios` (`Secretarios`) | `sec_cur_id` (Curso Vinculado) | cria; altera | FR-020 a FR-022 |
| `MembrosExternos` (`MembrosExternos`) | `mem_titulacao`, `mem_instituicao`, `mem_validade_ate`, `mem_prorrogado_ate` (nova) | cria (validade = cadastro + 30, Q12); altera; recalcula; prorroga (grava as duas datas) | FR-032 a FR-044 |

## 2. Tabelas só lidas

| Tabela | Para quê | Pesquisa |
|---|---|---|
| `Cursos` | listas suspensas, filtro e trava por curso | C5, C10 |
| `Turmas` (`tur_doc_id`, `tur_status`, `tur_descricao`) | vínculo (d), Professor com turma não arquivada, TCC 1 e TCC 2 na contagem | C8, C9, C11 |
| `TCCs` (`tcc_status`), `Orientacoes` (`ori_status`), `Coorientacoes` (`coo_status`) | vínculo (a), contagem de orientandos, Orientador da banca | C8, C9, C11 |
| `Turmas_Marcos` (`tma_tipo` 'Versão Final'), `Entregas_Marcos` (`ent_status` 'Homologada') | TCC aprovado ainda ativo enquanto a Versão Final não foi homologada | C8 |
| `Solicitacoes_Orientacao` (`sol_tipo` 'Coorientação', `sol_status` 'Aguardando Aceite') | vínculo (b) | C8 |
| `Defesas` (`def_data`, `def_status`), `Banca_Defesa` (`ban_usu_id`) | vínculo (c), validade, Orientador da banca | C8, C11, C14 |
| `Historico_Defesas` (`hdf_evento`, `hdf_membro_removido_id`, `hdf_data_hora`) | data do cancelamento e da retirada | C14 |

## 3. Estados da conta (`usu_status`)

Valores do Glossario_Status: 'Aguardando Ativação', 'Ativa', 'Inativa', 'Expirada'.

### Docente e Secretaria

```text
(cadastro, comando)        --> Aguardando Ativação      [FR-005; sem link, Q1]
Aguardando Ativação  --primeiro acesso (spec 003)--> Ativa
Ativa     --inativar, sem vínculos (Docente) / Coordenador (Secretaria)--> Inativa   [FR-024, FR-025]
Inativa   --reativar (só Docente)--> Ativa                                           [FR-029]
```

- 'Aguardando Ativação' não é inativada nem reativada (Q7, Q-49); corrige-se pela alteração.
- Secretaria 'Inativa' não volta (Q27): a pessoa volta por novo cadastro, com outro e-mail.
- 'Aguardando Ativação' e 'Ativa' ocupam o curso da Secretaria (Q7).

### Membro Externo

```text
(cadastro)  --> Aguardando Ativação, validade = hoje + 30            [FR-033, FR-038]
Aguardando Ativação --primeiro acesso--> Ativa
Ativa     --dia seguinte ao fim da validade (rotina) ou login--> Expirada      [FR-040; C15]
Expirada  --recálculo com validade >= hoje--> Ativa                            [FR-039]
Expirada  --prorrogar--> Ativa, validade = hoje + 7                            [FR-043]
Ativa     --prorrogar--> Ativa, validade += 7                                  [FR-043]
```

- 'Aguardando Ativação' não tem "Prorrogar" (MC-09) e não muda de status no recálculo.
- 'Ativa' com a validade vencida é tratada como 'Expirada' em tudo (Edge Case).

## 4. Validade do Membro Externo (`mem_validade_ate`)

Ordem de cálculo em `recalcular_validade` (research C14):

1. Sessões não Canceladas (Agendada, Reagendada, Em Andamento, Realizada) com o membro na banca,
   inclusive como substituído pelo suplente (spec Q33): maior `def_data` + 7 dias corridos.
2. Sem nenhuma: o evento mais recente entre cancelamento de sessão do membro e retirada do membro
   da banca (`Historico_Defesas`), data local + 7 dias corridos (A3, A7; Q13).
3. Sem histórico de banca: mantém a validade gravada (cadastro + 30).
4. Proteção da prorrogação (Q15, Q36): nunca antes de `mem_prorrogado_ate`, quando não for nula
   (research C13).
5. Status: validade hoje ou futura e conta 'Expirada' → 'Ativa'; validade no passado e conta
   'Ativa' → 'Expirada' na hora (research C14, m9).

Premissas sobre os dados da Defesa (contrato §2; research C14, I8): linhas de `Banca_Defesa` de
sessão Cancelada são mantidas; a retirada apaga a linha e grava 'Alteração da Banca' com
`hdf_membro_removido`; o substituído pelo suplente fica em `ban_usu_substituido` e mantém a
validade (spec Q33). Confirmação das premissas: Célio (Q-67).

A validade vale até o fim do dia (fuso America/Manaus).

## 5. Invariantes e onde são garantidos

| Invariante | Garantia |
|---|---|
| E-mail único sem diferenciar maiúsculas (FR-001) | trava consultiva do e-mail + `email_em_uso` + `UNIQUE(usu_email)` (C4) |
| Um Coordenador por curso, um curso por docente (FR-014) | PK e UNIQUE de `Coordenadores` + trava do curso (C5, C19) |
| Uma Secretaria não inativa por curso (FR-021) | aplicação, com trava da linha do curso (C5) |
| Nenhum docente com vínculo inativado (FR-026) | verificação repetida com a conta travada (C8) **e** a regra do contrato §1: quem cria vínculo trava a conta e confere 'Ativa' (B1). Sem a adesão das outras features, a garantia não vale |
| Status e validade do membro coerentes sob concorrência (FR-039, FR-040, FR-043) | toda escrita com a conta travada e dados relidos (C15) |
| Campos não editados não são sobrescritos | `update_fields` explícito (C20) |
| E-mail só muda após confirmação (FR-008) | `confirmar_troca_email` da spec 003 (C7) |
| Titulação e curso só de listas (FR-004) | `choices` do formulário + `CHECK` do banco |
