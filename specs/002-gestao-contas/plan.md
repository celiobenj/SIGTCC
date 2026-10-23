# Implementation Plan: Gestão de Contas do SIGTCC

**Branch**: `feature/feat-04-gestao-de-contas` | **Date**: 2026-10-22 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-gestao-contas/spec.md` (aprovada por Maria Luiza
Guimarães em 2026-10-22)

**Responsável pela implementação**: Maria Luiza Guimarães ("Maria Luiza Nobre" no documento de US).
As US-03 a US-06 foram escritas por Maria Luísa Gomes.

**Aprovação**: plano aprovado por Maria Luiza Guimarães ("Maria Luiza Nobre") em 2026-10-22, depois
da revisão do `arquiteto-django` e das decisões D1 a D6.

**Revisão de 2026-10-22**: o `arquiteto-django` revisou o plano (2 bloqueantes, 11 importantes, 13
menores). Os ajustes técnicos foram aplicados no research (marcados com o ID do achado: B1, I1 a
I5, I9 a I11, m1 a m4, m7 a m13), no data-model e nos contratos. Os que dependem de decisão de
comportamento (D1 a D6) foram decididos pela responsável em 2026-10-22 e registrados na spec
(Clarifications, Q30 a Q35) e no índice.

## Summary

Implementar no app `cadastro` o cadastro, a alteração e a listagem de Docentes (com o papel de
Coordenador de Curso) e da Secretaria, a inativação e a reativação com verificação de vínculos, o
cadastro e a alteração de Membros Externos, a regra de validade do acesso do membro (cálculo pelas
bancas, recálculo chamado pela Defesa e expiração automática), a prorrogação manual e o comando que
cria os Coordenadores iniciais. Mensagens exatas das US-03, 04, 05, 06 e 50 e as MC-01 a MC-13.

Abordagem: regras em `services_contas.py`, views finas em `views_contas.py`, formulários em
`forms_contas.py`, permissão por perfil com `@perfil_requerido` e por objeto no serviço (curso do
registro, turma não arquivada, vínculo com a banca). Gravações que disputam um curso travam a linha
do curso; toda transação segue uma ordem global de travas (conta, especialização, cursos, e-mail) e
relê os dados depois de travar (research C19); campos são gravados com `update_fields` (C20). As
outras features que criam vínculos com docentes e membros travam a conta e conferem 'Ativa'
(contrato §1). A troca de e-mail pelo gestor reaproveita o link de confirmação da spec 003. Nenhuma
tabela nova; uma coluna nova (`MembrosExternos.mem_prorrogado_ate`, Q-69), com a migração
e a atualização do dicionário no mesmo commit.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Django 5.2.18, psycopg 3.3.6, python-dotenv (já no `requirements.txt`).
Nenhuma dependência nova.

**Storage**: PostgreSQL 16 com as tabelas da spec 001 (nenhuma nova; [data-model.md](data-model.md)).
Log de eventos no `LOG_DIR/acesso.log` da spec 003. Token da troca de e-mail assinado (sem
armazenamento).

**Testing**: test runner do Django contra PostgreSQL; base `TesteAcesso` e fábricas da spec 003
(`tests/apoio_acesso.py`, `tests/fabricas.py`) e da spec 004 (`tests/apoio_turmas.py`: turmas, TCCs,
defesas, solicitações); `force_login`; e-mail em memória (`mail.outbox`); relógio com
`avancar_relogio`; tempo do filtro medido com margem (SC-009); concorrência com `TransactionTestCase`
e duas conexões (research C24). Testes pendentes de outras pessoas marcados com o ID da questão
(Q-52). A suíte atual já falha em `test_mensagens.py` e `test_mensagens_turmas.py`, que abrem
a US v3.2 (Q-77).

**Target Platform**: servidor web Linux ou Windows (fuso America/Manaus); navegadores atuais, de
360 px para cima (spec 003, Q22).

**Project Type**: aplicação web monolítica com renderização no servidor (Django MVT).

**Performance Goals**: filtro de Curso atualiza as listas em menos de 2 s (SC-009); listas com uma
consulta por página para contagens (research C9, C11); cadastro de docente em até 2 min e prorrogação
em até 30 s (SC-008, manual); instalação com 3 Coordenadores em até 10 min (SC-007, manual).

**Constraints**: nenhuma tabela nova e uma só coluna nova, aprovada pela autora do dicionário
(Q-69; princípio III); mensagens idênticas às US e à tabela
MC (SC-002); nenhuma ação fora do curso ou sem perfil (SC-004); nenhum e-mail na criação de contas
(Q1); e-mail só muda após confirmação (Q17); nenhum JavaScript do protótipo; nenhum dado pessoal no
repositório (comando dos Coordenadores lê arquivo externo).

**Scale/Scope**: 5 US + comando (119 cenários: 40 + 25 + 23 + 18 + 9 + 4), 48 FR, 13 mensagens MC;
3 cursos, dezenas de docentes por curso, centenas de membros externos; 7 templates de tela (mais o
include das abas) e 13 rotas.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Verificação | Resultado |
|---|---|---|
| I. Especificação primeiro | spec 002 aprovada em 2026-10-22 (Status da spec); plan e tasks ainda a aprovar antes de implementar. | PASSA |
| II. Rastreabilidade | Serviços, views, forms, templates, comandos e testes levam [US-XX][RBN-...]; testes nomeados pelo cenário. Tabela US → RBN → FR na spec. A constituição ainda cita a US v3.2 (índice Q-62). | PASSA |
| III. Modelo de dados oficial | Nenhuma tabela nova. Uma coluna nova, `MembrosExternos.mem_prorrogado_ate DATE NULL`, aprovada pela autora do dicionário (Q-69; spec Q36); o dicionário (Drive e cópia em `docs/fonte/`) é atualizado no mesmo commit do model e da migração, antes de qualquer uso ([data-model.md](data-model.md); research C13). | PASSA |
| IV. Arquitetura | Tudo em `sigtcc/apps/cadastro`; regras em `services_contas.py` e `permissoes.py`; views só orquestram; templates sem regra, em `sigtcc/templates/cadastro/contas/`; static em `sigtcc/static/` (sem arquivo novo; só ajustes em `sigtcc.css` e `sigtcc.js`). `services_contas.py` fora de `services.py`: mesma exceção da spec 004 (Complexity Tracking; Célio, Q-42 e Q-70). | PASSA com exceção justificada |
| V. Qualidade | `lint.bat`; comentários em português. | PASSA |
| VI. Testes de aceitação | Um teste por cenário (119) e testes de permissão, curso, concorrência, mensagens exatas, log e comando. | PASSA (1 pendente de outra pessoa: Q-52) |
| VII. Segurança e LGPD | Perfil e curso conferidos no serviço depois das travas, inclusive pelo endereço direto, com 404 para id de outro tipo de conta (SC-004; C22); senha do gestor para trocar e-mail; troca de e-mail de Membro Externo 'Ativa' ou 'Expirada' só pela Secretaria e pelo Coordenador (Q30); confirmação invalida links antigos (Q31); e-mail só muda pelo link; ordem global de travas e dados relidos (C19); `update_fields` explícito (C20); `?voltar=` só interno e resolvível (C23); log sem e-mail, valores nem traceback (C18); dados dos Coordenadores fora do Git e fora da saída do comando. Ameaça de tomada de conta pela troca de e-mail mitigada e risco restante aceito (Q30). | PASSA |
| VIII. Gerência de configuração | Branch `feature/feat-04-gestao-de-contas`; commits atômicos por fase; uma migração de esquema (coluna da Q-69), no mesmo commit do model e do dicionário. | PASSA |
| IX. Governança | Textos provisórios com a PO (Q-58); prioridade da US-50 com a PO (Q-63); itens de configuração ao Célio (Q-70). | PASSA |

**Reavaliação depois do Phase 1 e da revisão**: nenhuma violação nova. Acréscimos ao contrato da
spec 003, sem mudar o que existe: parâmetro `autor` em `pedir_troca_email`, `travar_email`,
`AUTOR_SISTEMA`, `expirar_se_vencida` (chamada protegida no login), eventos novos em
`EventoAcesso`, mensagem opcional em `acesso_negado.html`, textos da M-02 e da M-14 (Q-50), itens
de menu
([contracts/servicos-compartilhados.md](contracts/servicos-compartilhados.md), §5; ciência da Julia,
Q-71).

## Project Structure

### Documentation (this feature)

```text
specs/002-gestao-contas/
├── spec.md              # aprovada em 2026-10-22
├── plan.md              # este arquivo
├── research.md          # Phase 0 (C1 a C24)
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   ├── rotas.md                     # telas, rotas e menu
│   └── servicos-compartilhados.md   # o que Defesa e Vida do TCC usam
├── checklists/requirements.md
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
docs/fonte/Modelo_Logico_e_Dicionario_18_10.md   # + mem_prorrogado_ate; descrição de mem_validade_ate (Q-69, Q-44)
sigtcc/apps/cadastro/
├── models.py                          # + MembrosExternos.mem_prorrogado_ate (Q-69)
├── migrations/0006_membrosexternos_mem_prorrogado_ate.py   # nova (só esta coluna)
├── services_contas.py                 # novo: regras, vínculos, validade, contrato §1 a §3
├── forms_contas.py                    # novo: docente, secretaria, membro, "Sua senha"
├── views_contas.py                    # novo
├── permissoes.py                      # + curso_do_usuario, curso_do_registro, pode_gerir (C2)
├── services.py                        # + autor em pedir_troca_email, travar_email, AUTOR_SISTEMA,
│                                      #   expirar_se_vencida, eventos novos (C4, C15, C18)
├── views.py                           # acesso_negado com mensagem opcional (C21)
├── mensagens.py                       # + textos das US-03 a 06 e 50, MC-01 a MC-13; M-02 e M-14
├── urls.py                            # + rotas de contracts/rotas.md
├── menu.py                            # + Docentes, Secretarias, Membros externos
├── management/commands/
│   ├── criar_coordenadores.py         # novo (C17)
│   └── expirar_membros_externos.py    # novo (C15)
└── tests/
    ├── apoio_contas.py                # fábricas: docente de curso, coordenador, vínculos, bancas
    ├── test_us03_docentes.py
    ├── test_us03_secretarias.py
    ├── test_us04_inativacao.py
    ├── test_us05_membros.py
    ├── test_us06_validade.py
    ├── test_us50_prorrogacao.py
    ├── test_troca_email_gestor.py
    ├── test_comando_coordenadores.py
    ├── test_permissoes_contas.py      # SC-004: cada ação, cada perfil, curso, endereço direto
    ├── test_concorrencia_contas.py    # TransactionTestCase: e-mail, Coordenador, Secretaria,
    │                                  #   inativação × vínculo novo, expiração × prorrogação
    ├── test_contrato_contas.py        # recalcular_validade (savepoint, idempotência), listas
    └── test_mensagens_contas.py       # SC-002
sigtcc/templates/cadastro/contas/
├── abas.html                          # include: Docentes | Secretarias | Membros externos
├── docentes.html, form_docente.html
├── secretarias.html, form_secretaria.html
├── membros.html, form_membro.html
└── confirmar.html                     # inativar, reativar
sigtcc/static/css/sigtcc.css           # + estilos de abas e do alerta de orientandos (se faltarem)
sigtcc/static/js/sigtcc.js             # + mostrar/ocultar Curso Coordenado; desabilitar botão
sigtcc/templates/acesso_negado.html    # + mensagem opcional no contexto (C21)
```

**Structure Decision**: monólito Django do PGCS 2.3, app `cadastro` (Épico 1), com módulos novos por
assunto (research C1) e templates numa subpasta de `cadastro/`, como na spec 004.

## Decisões da revisão (da responsável, Maria Luiza Guimarães, 2026-10-22)

| ID | Questão | Origem | Decisão | Índice / spec |
|---|---|---|---|---|
| D1 | Ameaça de tomada de conta pela troca de e-mail do gestor: aceitar o risco ou mitigar (avisar o e-mail antigo; texto próprio no e-mail de confirmação, dizendo quem pediu; restringir a troca de e-mail de Membro Externo 'Ativa' à Secretaria e ao Coordenador) | B2; C7 | restringir a troca de e-mail de Membro Externo 'Ativa' ou 'Expirada' à Secretaria e ao Coordenador; sem aviso ao e-mail antigo; risco restante aceito | Q-72; Q30 |
| D2 | Invalidar links de ativação e de redefinição na confirmação da troca de e-mail (reabre a Q17) | I6 | invalida na confirmação | Q-73; Q31 |
| D3 | Recusar o papel de Coordenador para docente 'Inativa', e com que texto | I7; C6 | recusa com a MC-10 | Q-74; Q32 |
| D4 | Validade do membro substituído pelo suplente; premissas de gravação da Defesa | I8; C14 | a substituição mantém a validade; a sessão continua contando para o substituído | Q-75; Q33 (premissas de dados: Célio, Q-67) |
| D5 | Comportamento do recálculo sem a proteção da prorrogação | I9; C13 | Q-69 respondida (coluna aprovada); a Defesa liga o recálculo depois que a proteção estiver implementada | Q-69; Q34; Q36 |
| D6 | Limite de tentativas da "Sua senha" na troca de e-mail | m13; C7 | sem limite, com registro no log | Q-78; Q35 |

## Pendências desta feature

Índice central: [docs/questoes-a-rever.md](../../docs/questoes-a-rever.md).

| Pendência | Destino | Índice |
|---|---|---|
| Texto de expiração da US-06 no login (troca da M-16) | Julia Cohen | Q-52 |
| Validar os textos provisórios MC-11 a MC-13 | Profa. Diana (PO) | Q-58 |
| Prioridade da US-50 (Could Have × Must Have) | Profa. Diana (PO) | Q-63 |
| Atualizar o dicionário no Drive com `mem_prorrogado_ate` e a nova descrição de `mem_validade_ate` (a cópia em `docs/fonte/` é atualizada na T013) | Maria Luiza Guimarães | Q-69 e Q-44 (respondidas) |
| Ajuste do texto "uma Secretaria ativa por curso" no dicionário e no Glossário | Maria Luiza Guimarães e PO | Q-60 |
| Módulos novos, subpasta de templates, comandos novos e agendamento diário da expiração | Célio Benjamim | Q-70 (e Q-67, item 4) |
| Recálculo da validade dentro da transação da Defesa, travar a conta e conferir 'Ativa' ao incluir na banca, atalho da US-23 validando o membro, avaliadores só 'Ativa' | Célio Benjamim | Q-67 (complementada) |
| Listas de orientador e coorientador só com docentes 'Ativa'; travar a conta e conferir 'Ativa' ao criar orientação, coorientação e convite | Leandra Matos | Q-68 (complementada) |
| Homologação da Versão Final leva o TCC a 'Concluído'? Critério da contagem de orientandos | Leandra Matos | Q-76 |
| Acréscimos ao contrato e ao login da spec 003; trava do e-mail em `confirmar_troca_email`; autor "sistema" | Julia Cohen | Q-71 (complementada) |
| `criar_turma` travar e conferir o docente 'Ativa'; testes de mensagens das specs 003 e 004 abrem a US v3.2 | Julia Cohen | Q-77 |

## Complexity Tracking

Nenhuma violação da constituição sem justificativa. Exceção justificada: princípio IV (regras também
fora de `services.py`). Escolhas que merecem registro:

| Escolha | Por quê | Alternativa mais simples rejeitada |
|---|---|---|
| Módulos `services_contas.py`, `forms_contas.py` e `views_contas.py` (exceção ao princípio IV) | Mantém o contrato da spec 003 intacto e os arquivos pequenos; mesmo padrão da spec 004 | Crescer `services.py` (1.136 linhas) e `views.py`; ou pacote `services/` (decisão do Célio, Q-42) |
| Trava da linha do curso em cadastros de Coordenador e Secretaria | "Uma Secretaria por curso" não tem restrição no banco (C5) | Índice parcial (exige mudar o dicionário) |
| Coluna nova `MembrosExternos.mem_prorrogado_ate` (Q-69) | Proteção da prorrogação no recálculo (Q15); o log em arquivo não é confiável para regra (C13) | Ler o log (frágil) |
| Trava consultiva por e-mail (`pg_advisory_xact_lock`) | Unicidade sem diferenciar maiúsculas sob concorrência, sem índice novo (C4) | Índice em `lower(usu_email)` (exige o dicionário; Q-28) |
| Expiração conta a conta, com trava | Evita reexpirar uma conta prorrogada no mesmo instante (C15) | `UPDATE` em massa |
| Regra de travas imposta às outras features (contrato §1) | Única forma de garantir "nenhum docente inativo com vínculo" no READ COMMITTED (B1) | Trava só na inativação (não fecha a corrida) |
