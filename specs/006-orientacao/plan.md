# Implementation Plan: Orientação, Atas e Publicações do SIGTCC

**Branch**: `feature/feat-06-orientacao` | **Date**: 2026-10-24 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/006-orientacao/spec.md` (aprovada por Célio Benjamim em
2026-10-24, depois da conferência do `analista-requisitos`, de 6 respostas na revisão (Q4 a Q9) e de
5 perguntas do `/speckit-clarify` (Q10 a Q14))

**Responsável pelas US**: Leandra Matos (US-17, 18, 19, 20, 36, 41, 42, 45 e 46).
**Configuração e aprovação da spec**: Célio Benjamim.

**Aprovação do plano**: aprovado por Leandra Matos (responsável pelas US) e Célio Benjamim
(configuração) em 2026-10-24, depois da revisão e da reconferência do `arquiteto-django`. Os itens de
configuração IC-01 a IC-14 ficaram aprovados com o plano (índice Q-103 a Q-116, respondidas); a
ciência de Julia Cohen (specs 003 e 004) continua na Q-96.

**Revisão do `arquiteto-django`** (2026-10-24): 34 pontos (1 bloqueante, 12 importantes, 21
menores), todos tratados. Os que mudavam comportamento foram respondidos por Célio Benjamim (spec,
Clarifications Q15 a Q18); os de implementação, por delegação dele, estão no
[research.md](research.md) (marcados [A1] a [A34]) e nos demais artefatos. A reconferência fechou os
34 pontos e trouxe 12 problemas de texto e de trava, também tratados ([N1] a [N12]; IC-14).

## Summary

Implementar no app `cadastro` (Épico 1) a orientação do TCC sobre o modelo de dados já existente
(spec 001; nenhuma tabela ou coluna nova):
- o pedido, o cancelamento e a troca de orientador pelo Aluno (US-17);
- a resposta do docente e a tela de orientandos (US-18);
- o convite de coorientação e a sua resposta (US-45, US-36);
- as atas de orientação com comentários (US-19);
- a indicação de Apto para Defesa (US-42) e a ação "Correções Conferidas";
- a publicação do artigo (US-46) e o aproveitamento pelo Coordenador (US-20);
- a aba "Alunos" em blocos e o painel do aluno (US-41), que reúne as ações já entregues pelas
  specs 003, 004 e 005.

Abordagem: regras em três módulos novos, um por domínio de dados:
- `services_orientacao.py`: `Solicitacoes_Orientacao`, `Orientacoes`, `Coorientacoes` e
  `CoorientadoresExternos`; a tela de orientandos, Apto para Defesa, Correções Conferidas, o motivo
  do cancelamento (FR-050) e o histórico de orientação (FR-049);
- `services_atas.py`: `Encontro_Orientacao` e `Comentarios_Encontro`;
- `services_artigos.py`: `Artigos`.

As views ficam finas, em `views_orientacao.py`, `views_atas.py`, `views_artigos.py` e
`views_painel.py`. O plano reaproveita sem duplicar:
- spec 003: `perfil_requerido`, `papeis`, `professor_com_turma_ativa`, `curso_id_do_usuario`,
  `pode_resetar_primeiro_acesso`/`resetar_primeiro_acesso`, `notificar`, `enviar_email`,
  `registrar_evento`, `normalizar_email`, `travar_email`;
- spec 002: `docentes_ativos`, `travar_e_conferir_ativo`, `validar_nome_completo`;
- spec 004: `turma_para`, `vinculo_na_turma`, `tcc_do_aluno`, `travar_turma_ativa`/`TurmaArquivada`,
  `participacao_encerrada`, `turma_tem_orientador_automatico`, `encerrar_orientacoes_ativas`,
  `STATUS_SESSAO_ATIVA`, `STATUS_SOLICITACAO_PENDENTE`;
- spec 005: `atualizar_status_tcc`, `pode_ver_resumo`, `historico_do_status`, `status_exibido`,
  `link_mais_recente`, `turma_do_aluno`, `palavras_chave_do`, `versao_final_do_aluno`,
  `exige_correcoes_conferidas`, `STATUS_ENVIO_AVALIAVEL`, `mensagens.LINK_HTTPS_500`.

Mudanças em código já mesclado: todas estão listadas como itens de configuração IC-01 a IC-14 e no
índice (Q-103 a Q-116). As maiores são:
- a aba "Alunos" vira blocos de consulta;
- as telas de ação voltam ao painel;
- os cancelamentos automáticos gravam o mesmo instante do evento que os causou;
- a cópia para TCC 2 cancela os pendentes do TCC 1, e o arquivamento da turma cancela os pendentes
  dos seus TCCs (Q17);
- `pode_ver_resumo` passa a aceitar o pedido de troca;
- a devolução para ajuste apaga a conferência;
- a tela provisória de reset da spec 003 sai.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Django 5.2, psycopg 3 e python-dotenv, já no `requirements.txt`. Nenhuma
dependência nova: a feature não lê arquivos, não gera PDF e não chama serviços externos além do
e-mail que já existe.

**Storage**: PostgreSQL 16, com as tabelas já existentes da spec 001: `Orientacoes`, `Coorientacoes`,
`CoorientadoresExternos`, `Solicitacoes_Orientacao`, `Encontro_Orientacao`, `Comentarios_Encontro`
e `Artigos`. Também lê e grava sem alterar o esquema: `TCCs`, `Historico_Status_TCC`,
`Entregas_Marcos` (só `ent_correcoes_conferidas_em`), `Historico_Alunos_Turmas` e
`Historico_Defesas` (app `defesa`, só leitura). Nenhuma migração de esquema nem de dados
([data-model.md](data-model.md)).

**Testing**: test runner do Django contra PostgreSQL. Reaproveita `tests/apoio_acesso.py`,
`apoio_contas.py`, `apoio_turmas.py` e `apoio_tcc.py`, e acrescenta `tests/apoio_orientacao.py`
(fábricas de pedido, convite, orientação, coorientação, ata e artigo). Usa
`captureOnCommitCallbacks(execute=True)` para os e-mails. A regra do instante do evento (FR-050) é
testada com o **relógio real**, sem congelar o tempo, e com um teste negativo por motivo (research
R3).

**Target Platform**: servidor web Linux ou Windows (fuso America/Manaus); navegadores atuais, de
360 px para cima (spec 003, Q22). Segue o protótipo de 17/10:
- layout, paleta, fontes Roboto e Figtree e ícones Material Symbols;
- itens de menu "Orientações" (`supervisor_account`) e "Aproveitamento de artigos" (`article`) na
  seção "Gestão";
- `viewOrientacoes`, `viewAlunoTurma`, `secaoOrientacaoAluno` e `viewArtigos` só como referência
  visual. A lógica em JavaScript do protótipo não é reaproveitada.

**Project Type**: aplicação web monolítica com renderização no servidor (Django MVT).

**Performance Goals**: SC-001 (pedido em menos de 1 minuto) e SC-002 (resposta em até 2
acionamentos) são metas do roteiro manual ([quickstart.md](quickstart.md)), não de carga. A tela de
orientandos, a aba "Alunos" e o painel não podem fazer consultas por linha: usam
`select_related`/`prefetch_related` (research R14).

**Constraints**:
- nenhuma tabela ou coluna nova;
- mensagens idênticas às US ou provisórias (MO-01 a MO-26);
- o Status do TCC só muda por `atualizar_status_tcc` (spec 005, FR-012);
- nenhuma ação em turma arquivada, com a participação encerrada ou em TCC já copiado para o TCC 2
  (FR-007, FR-046);
- ordem de trava turma → aluno (`Alunos`) → TCC → conta do docente → solicitação, artigo ou
  entrega, com a turma do TCC conferida depois da trava (research R2); o Coordenador trava a turma
  sem exigir que esteja ativa (D11);
- todo objeto com ID na URL é buscado filtrando pelo TCC do contexto, senão 404 (research R10);
- e-mails só depois do commit (`transaction.on_commit`); notificações no sistema na mesma transação da gravação (são linhas do banco, como na spec 004);
- nenhum endereço de volta montado a partir de texto vindo do usuário (research R5).

**Scale/Scope**:
- 9 US, com 99 cenários mais 7 pontos de contato;
- 53 FR (FR-001 a FR-053) e 26 mensagens provisórias (MO-01 a MO-26);
- cerca de 14 telas ou janelas e 29 rotas novas, mais 11 rotas existentes que mudam
  ([contracts/rotas.md](contracts/rotas.md));
- 14 itens de configuração em código de outras specs.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Verificação | Resultado |
|---|---|---|
| I. Especificação primeiro | Spec 006 aprovada por Célio Benjamim em 2026-10-24, sem marcadores `[NEEDS CLARIFICATION]` (Q1 a Q18 em Clarifications; Q15 a Q18 vieram da revisão do plano). O plano e o `tasks.md` ainda precisam da aprovação de Leandra Matos antes do `/speckit-implement`. | PASSA |
| II. Rastreabilidade | Todo FR traz `[RBN-...]` ou a decisão de Clarifications. Services, views, forms, templates e testes levam `[US-XX][RBN-...]`. Cada IC aponta a sua questão no índice. | PASSA |
| III. Modelo de dados oficial | Nenhuma tabela ou coluna nova ([data-model.md](data-model.md)). As lacunas do modelo (ata sem autor, motivo do cancelamento, só a decisão mais recente do artigo) foram aceitas sem coluna nova (Q7, D14; índice Q-102). O ciclo do artigo segue o dicionário 3.5.7 sem exceção (Q16). A divergência do dicionário 3.5.1 sobre a linha do TCC 2 está na Q-91, respondida, com ajuste do documento pendente. | PASSA com pendência documental (Q-91, Q-102) |
| IV. Arquitetura | Tudo em `sigtcc/apps/cadastro`. Regras em `services_orientacao.py`, `services_atas.py` e `services_artigos.py`; views só orquestram; templates sem regra (decisões de botão vêm prontas do service). Templates em `sigtcc/templates/cadastro/`; static em `sigtcc/static/`. Três módulos `services_*` são a mesma exceção já aceita nas specs 004 e 005 (Complexity Tracking). | PASSA com exceção justificada (já aceita) |
| V. Qualidade | `lint.bat` (isort, black, flake8 com 100); comentários em português. | PASSA |
| VI. Testes de aceitação | Um teste por cenário das 9 US (99) e pelos 7 pontos de contato. Além deles: permissões (SC-006, inclusive pelo endereço direto), mensagens exatas (SC-003, `test_mensagens_orientacao.py`), navegação (SC-005), regra do motivo (FR-050) e concorrência (aceite duplo, aceite de pedido cancelado, Apto com condição mudada). | PASSA |
| VII. Segurança e LGPD | Objetos aninhados na URL (coorientação, solicitação, ata) só pelo TCC do contexto, senão 404, com teste de troca de ID por rota (research R10). O link de pedido ou convite não revela existência nem estado a outro docente (R4). Resumo só por `pode_ver_resumo`. Atas só ao vínculo ativo (Q10). Exposição do nome e da instituição do coorientador externo reaproveitado: ciência registrada (Q15). O painel é só do Professor da Disciplina da turma, e a retirada da tela provisória resolve a S-02. O link do e-mail nunca grava resposta (Q14). Não há redirecionamento aberto: a volta é por valor fechado (research R5). Aceites, recusas e decisões do Coordenador ficam com autor, data e hora; as decisões do Coordenador também vão para o log (D10). | PASSA |
| VIII. Gerência de configuração | Branch `feature/feat-06-orientacao`; commits atômicos por fase. Código de specs já mescladas (003, 004 e 005) só muda pelos IC-01 a IC-14, cada um com questão no índice (Q-103 a Q-116) e com os testes dessas specs ajustados no mesmo PR (IC-11). | PASSA (ICs pendentes de aprovação) |
| IX. Governança | MO-01 a MO-26 aguardam a PO (Q-95). As divergências com a matriz aguardam a PO: Q-97 a Q-99 (a Q-100 foi respondida pela Q16, sem ajuste de documento). As decisões D1 a D14 ainda abertas estão na Q-101; os ICs, nas Q-103 a Q-116; a regra nova do arquivamento vai à PO para ciência (Q-117). | PASSA (pendências não bloqueantes) |

**Reavaliação depois do Phase 1**: o design não criou tabela, coluna nem dependência. As decisões de
research R3 (instante do evento) e R5 (volta por valor fechado) mudam assinaturas de funções da
spec 004 e da spec 005 só com parâmetros **opcionais**, mantendo o comportamento de quem não os
passa; os testes das specs 004 e 005 continuam valendo, exceto os listados no IC-11. Nenhuma
violação nova. **Reavaliação depois da revisão do `arquiteto-django`**: o arquivamento que cancela
pendentes (IC-12) e o helper de e-mail (IC-13) são mudanças de comportamento e de estrutura em
código mesclado, cobertas por IC e questão no índice; nenhuma tabela ou coluna nova.

## Project Structure

### Documentation (this feature)

```text
specs/006-orientacao/
├── spec.md                          # aprovada em 2026-10-24
├── plan.md                          # este arquivo
├── research.md                      # Phase 0 (R1 a R21)
├── data-model.md                    # Phase 1 (nenhuma tabela nova; estados e regras derivadas)
├── quickstart.md                    # Phase 1 (roteiro manual pela navegação, SC-005)
├── contracts/
│   ├── rotas.md                     # telas, rotas, perfis e caminho de navegação
│   └── servicos-compartilhados.md   # o que Defesa (US-21 a 28) e Relatórios podem chamar
├── checklists/requirements.md       # 16/16
└── tasks.md                         # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
sigtcc/apps/cadastro/
├── services_orientacao.py           # novo: pedidos, troca, convites, coorientadores, orientandos,
│                                     #   Apto, Correções Conferidas, motivo (FR-050), histórico
├── services_atas.py                 # novo: atas e comentários, visibilidade (US-19)
├── services_artigos.py              # novo: publicação e aproveitamento (US-46, US-20)
├── forms_orientacao.py              # novo: indicar/trocar orientador, coorientador
├── forms_atas.py                    # novo: ata e comentário
├── forms_artigos.py                 # novo: publicação
├── views_orientacao.py              # novo: tela Orientações, links, aceite/recusa, ações da linha
├── views_atas.py                    # novo: lista, registro, edição e comentário (3 entradas)
├── views_artigos.py                 # novo: publicação (Aluno, Orientador) e aproveitamento
├── views_painel.py                  # novo: painel do aluno (US-41)
├── urls.py                          # IC-10: + rotas novas (contracts/rotas.md)
├── menu.py                          # IC-01: + "Orientações" e seção "Gestão"
├── mensagens.py                     # IC-10: + textos das US e MO-01 a MO-26
├── services.py                      # IC-13: + enviar_email_apos_commit (helper compartilhado)
│                                     # IC-12: notificar ganha agora=None opcional
├── services_turmas.py               # IC-02: alunos_da_turma sem consulta por linha
│                                     # IC-04: instante do evento; trava e cancela pendentes do TCC 1
│                                     # IC-12: arquivar_turma cancela os pendentes da turma
├── services_tcc.py                  # IC-05: pode_ver_resumo aceita Troca de Orientação
│                                     # IC-06: + contexto_historico (era views_tcc._contexto_historico)
├── services_entregas.py             # IC-07: devolução apaga ent_correcoes_conferidas_em
│                                     # IC-13: _enviar_email_ao_aluno chama o helper
│                                     # IC-14: enviar_entrega trava turma → aluno → TCC → entrega
├── views_turmas.py                  # IC-02 e IC-03: blocos da aba Alunos; volta ao painel
├── views_tcc.py                     # IC-06 e IC-09: histórico com "Fechar"; seções do Meu TCC
├── views_entregas.py                # IC-07: Versão Final volta ao painel
├── views.py                         # IC-08: tela provisória de reset vira redirecionamento
└── tests/
    ├── apoio_orientacao.py          # novo
    ├── test_us17_pedido_orientacao.py
    ├── test_us18_resposta_orientandos.py
    ├── test_us41_painel_aluno.py
    ├── test_us19_atas.py
    ├── test_us42_apto_defesa.py
    ├── test_us45_coorientadores.py
    ├── test_us36_convite_coorientacao.py
    ├── test_us46_publicacao.py
    ├── test_us20_aproveitamento.py
    ├── test_motivo_cancelamento.py  # FR-050 (6 motivos, relógio real, testes negativos)
    ├── test_arquivamento_pendentes.py # FR-053 (IC-12)
    ├── test_permissoes_orientacao.py
    ├── test_mensagens_orientacao.py # SC-003, padrão de test_mensagens_tcc.py
    └── test_navegacao_orientacao.py # SC-005: menu, links, volta de cada tela
sigtcc/templates/cadastro/
├── orientacao/                      # novo
│   ├── orientacoes.html             # Pedidos, Convites, orientandos (+ aviso de estado, FR-012)
│   ├── ver_proposta.html
│   ├── confirmar.html               # confirmação genérica (Apto, Correções, Remover)
│   ├── form_coorientador.html       # registrar e substituir (US-45)
│   ├── atas.html                    # lista com comentários; TCC 1 abaixo (Q6)
│   ├── form_ata.html                # "Registrar ata de orientação" e edição
│   ├── publicacao.html              # publicação pelo Orientador (FR-035)
│   └── aproveitamento.html          # tela do Coordenador (US-20)
├── tcc/
│   ├── _secao_orientacao.html       # novo, incluído em meu_tcc.html e no painel
│   ├── _secao_atas.html             # novo
│   ├── _secao_publicacao.html       # novo
│   ├── meu_tcc.html                 # IC-09: + 3 includes com âncora por `secao`
│   ├── historico_status.html        # IC-06: + botão "Fechar" (url_voltar)
│   └── homologar_versao_final.html  # IC-07: + volta ao painel
├── turmas/
│   ├── painel_aluno.html            # novo (US-41)
│   ├── turma.html                   # IC-02: blocos; "Transferir aluno" só da Secretaria
│   └── editar_aluno.html, encerrar.html, excluir_aluno.html, transferir.html   # IC-03
├── emails/                          # pedido_orientacao, pedido_troca, convite_coorientacao,
│                                     #   orientacao_aceita (.txt), junto dos e-mails existentes
├── confirmar_reset.html             # IC-08: "Cancelar" volta ao painel (por cadastro:aluno)
└── aluno.html                       # IC-08: removido (tela provisória da spec 003)
sigtcc/static/
├── css/                             # reaproveitado (base visual da spec 003); classes do bloco
│                                     #   e do painel acrescentadas ao CSS base (IC-10)
└── js/secao.js                      # novo: rola até a seção indicada por ?secao= (research R12)
```

**Structure Decision**: monólito Django do PGCS 2.3, app `cadastro` (Épico 1, "Cadastro e
Manutenção", ao qual pertencem as US-17 a 20, 36, 41, 42, 45 e 46). Os três módulos de serviço
seguem os três domínios de dados (solicitações e vínculos; atas; artigos), no mesmo padrão já
aceito nas specs 004 e 005. O painel do aluno fica em `templates/cadastro/turmas/` porque é aberto
pela tela da turma (US-41).

## Itens de configuração (código de outras specs)

Cada item é um acréscimo ou mudança em arquivo já mesclado na `develop`. Todos estão no índice para
aprovação de Célio Benjamim (configuração) e ciência da autora da spec de origem, além da Q-96.

| IC | Arquivo(s) e spec de origem | O que muda | Por quê | Testes da spec de origem | Índice |
|---|---|---|---|---|---|
| IC-01 | `menu.py` (003; itens de 002, 004 e 005) | + "Orientações" (`supervisor_account`, perfil `docente`, ordem 12). + "Aproveitamento de artigos" (`article`, perfil `coordenador`, ordem 30, seção nova "Gestão"). Itens existentes inalterados. | FR-040, FR-041; Q11; protótipo | `test_base_comum.py` (menu) conferido; só acréscimo | Q-103 |
| IC-02 | `templates/cadastro/turmas/turma.html` (004; abas da 005) e `views_turmas.turma` (004) | A tabela com ações vira blocos de consulta: Nome, Matrícula, Curso, Título ou "Sem Proposta", Área, Orientador ou "Sem orientador" e Status. Para o Professor da Disciplina, o bloco abre o painel. A Secretaria vê os blocos com "Transferir aluno". Saem da linha Editar, Excluir, Encerrar e o histórico. O contexto da view ganha título, área e orientador ativo, sem consulta por linha; `services_turmas.alunos_da_turma` passa a resolver o curso sem consulta por linha (research R14). | FR-017; Q1, Q4; RBN-CAD-10.5, 08.9, 05.6 | quebra `test_navegacao_tcc.py:177` e `test_us08_transferencia.py:190` (IC-11) | Q-104 |
| IC-03 | `views_turmas.py` (editar, encerrar, excluir, transferir) e os 4 templates de ação (004) | Aceitam `?volta=painel`, valor fechado (research R5). "Cancelar", o redirecionamento final e os redirecionamentos de erro (MT-19, `ALUNO_TEM_PROPOSTA`, turma arquivada) voltam ao painel. Excluir e Transferir confirmados voltam à aba "Alunos". Sem o parâmetro, o comportamento atual é mantido. | FR-044; US-41 C | `test_us09_exclusao.py:174` e testes de redirecionamento das US-08 e 09 continuam válidos sem o parâmetro; novos casos na 006 | Q-105 |
| IC-04 | `services_turmas.py` (004; funções públicas da 005) | (a) `_registrar_historico`, `atualizar_status_tcc`, `criar_tcc_com_historico` e `_criar_orientacao_automatica` ganham `agora=None` opcional. (b) `encerrar_participacao`, `transferir` e `_copiar_tcc_aprovado` passam o mesmo `agora` ao histórico, aos cancelamentos e à orientação. (c) `_copiar_tcc_aprovado` passa a travar o TCC 1 (depois do aluno), cancela pedidos e convites pendentes do TCC 1 e avisa cada docente (MO-18). As notificações MT-31 (encerramento) e MT-22 (transferência) não mudam (Q18). | FR-050, FR-051; Q6, Q7, Q18 | US-08 e 09 continuam passando; novos testes em `test_motivo_cancelamento.py` | Q-106 |
| IC-05 | `services_tcc.pode_ver_resumo` (005) | Aceita também `TipoSolicitacao.TROCA_DE_ORIENTACAO` pendente. | FR-013; defeito achado na revisão (C14) | `test_permissoes_tcc.py` continua; + 1 teste | Q-107 |
| IC-06 | `views_tcc._contexto_historico`, `historico_status`, `historico_status_aluno`, `services_tcc` e `templates/cadastro/tcc/historico_status.html` (005) | `_contexto_historico` vira a função pública `services_tcc.contexto_historico(tcc, url_voltar)`, que monta `turma = tcc.tcc_tur` para o template; os 3 chamadores (Professor → painel, Aluno → Meu TCC, rota nova do Orientador → tela de orientandos) passam `url_voltar`, e o template ganha o botão "Fechar". As permissões das rotas existentes não mudam (research R13). | FR-043; US-14 A e B | `test_us14_status_historico.py` e `test_permissoes_tcc.py` (Coorientador continua com 403) | Q-108 |
| IC-07 | `services_entregas.devolver_versao_final`, `views_entregas.aluno_versao_final`, `homologar_versao_final.html` (005) | A devolução grava `ent_correcoes_conferidas_em=None`. Com `?volta=painel`, a tela e o redirecionamento voltam ao painel. | FR-016, FR-044; Q2, D12 | `test_us44_homologacao.py` continua; + 1 teste | Q-109 |
| IC-08 | `views.aluno`, `views.resetar_primeiro_acesso`, `templates/cadastro/aluno.html`, `confirmar_reset.html` (003) | `aluno` deixa de renderizar e redireciona ao painel da turma mais recente do aluno em que quem abre é o Professor da Disciplina; sem turma, 403 (M-02). O template `aluno.html` é removido. O reset e o "Cancelar" redirecionam para `cadastro:aluno`, que resolve o painel no servidor (nenhum `tur_id` vindo do usuário; research R5). "Mais recente": não arquivada primeiro, depois `tur_ano`, `tur_semestre` e `tur_id` decrescentes. A rota `cadastro:aluno` continua existindo (endereço antigo). | FR-044; Q12, D3; S-02 | `test_us12_senha.py` (37-39, 292-389) e `test_seguranca.py:152` ajustados (IC-11) | Q-110 |
| IC-09 | `templates/cadastro/tcc/meu_tcc.html` e `views_tcc.meu_tcc` (005) | + 3 includes (Orientação, Atas de orientação, Publicação do artigo), com âncora e `?secao=`; o contexto vem dos services da 006. O comentário desatualizado das linhas 8 a 10 é corrigido (Q-87). | FR-042, FR-001, FR-022, FR-034 | `test_us14_status_historico.py:485-489` continua; só acréscimo | Q-111 |
| IC-10 | Arquivos compartilhados: `urls.py`, `mensagens.py` (003) e o CSS base (`static/css/`) | + rotas, + textos (US e MO-01 a MO-26), + classes de bloco e painel. Nada removido. Os eventos do log das decisões do Coordenador ficam num enum local de `services_artigos` (`EventoArtigo`), como o `EventoFluxoTCC` da spec 005, sem mexer em `services.EventoAcesso` (research R9). | FR-048; D10 | só acréscimo; `test_log_acesso.py` não muda | Q-112 |
| IC-11 | Testes de outras specs | Ajustados (só o caminho bloco → painel → ação): `test_navegacao_tcc.py`, `test_us08_transferencia.py` e `test_us12_senha.py`. Acrescentados: `test_notificar.py` (IC-12), `test_us08_matricula.py` (cópia para o TCC 2, IC-04) e `test_us15_envio_entrega.py` (ordem de trava, IC-14). `test_us09_exclusao.py`, `test_seguranca.py` e `test_base_comum.py` não precisaram mudar (conferido na implementação). Nenhum cenário de aceite é removido. | IC-02, IC-04, IC-08, IC-12, IC-14 | — | Q-113 |
| IC-12 | `services_turmas.arquivar_turma` (004) e `services.notificar` (003) | Depois das condições da RBN-CAD-04.5, na mesma transação, trava alunos e depois TCCs da turma (por `pk`) e chama `services_orientacao.cancelar_pendentes_da_turma(turma, agora)` (import dentro da função, sem import circular), que cancela os pedidos e convites pendentes com o mesmo instante e grava, também na transação, a MO-26 ao docente de cada um, com o link da solicitação. `notificar` ganha `agora=None` opcional, para a notificação ter o mesmo instante (dedução do motivo, FR-050). | FR-050, FR-053; Q17 | testes da US-07 continuam; novos em `test_arquivamento_pendentes.py` | Q-114 |
| IC-13 | `services.py` (003) e `services_entregas._enviar_email_ao_aluno` (005) | + `services.enviar_email_apos_commit(usuario, assunto, template, contexto)`, extraído de `_enviar_email_ao_aluno` (mesma regra de `SIGTCC_EMAIL_SINCRONO` e thread), que passa a chamá-lo. Comportamento da spec 005 inalterado. | R11; reaproveitamento sem cópia | testes de e-mail das US-15 e US-43 continuam | Q-115 |
| IC-14 | `services_entregas.enviar_entrega` (005) | Passa a travar turma (com `select_for_update` simples, sem exigir turma ativa) → aluno → TCC → entrega (acha a entrega sem trava para saber a turma e a relê travada), no lugar de entrega → TCC; a turma arquivada continua dando 404 por `envio_liberado`. Evita deadlock com "Correções Conferidas" (006) e com Homologar e Devolver da Versão Final (005). Regras de envio inalteradas. | research R2 [N1] | testes das US-15 e US-29 continuam; + 1 teste de ordem de trava e 1 de turma arquivada no meio (404) | Q-116 |

## Pendências desta feature

Índice central: [docs/questoes-a-rever.md](../../docs/questoes-a-rever.md).

| Pendência | Destino | Índice |
|---|---|---|
| Aprovar os IC-01 a IC-14 (código de specs já mescladas) | Célio Benjamim (config); ciência de Julia Cohen (003 e 004) e Leandra Matos (005) | Q-103 a Q-116, Q-96 |
| Ciência da regra nova no arquivamento (US-07 C; RBN-CAD-04.5): pendentes cancelados e MO-26 | Profa. Diana (PO) | Q-117 |
| Validar MO-01 a MO-26 | Profa. Diana (PO) | Q-95 |
| Divergências US × matriz decididas pela equipe: Secretaria na lista, "Editar" no painel, aviso na recusa | Profa. Diana (PO) | Q-97 a Q-99 |
| Decisões propostas ainda a validar (D1, D2, D5, D6, D8, D10 a D14) | Leandra Matos | Q-101 |
| Ajustar o dicionário 3.5.1 (linha nova do TCC 2) e ter ciência das lacunas aceitas | Maria Luiza Guimarães | Q-91, Q-102 |
| Nome do link de histórico ("Histórico" ou "Histórico do Status do TCC") | PO ou Leandra Matos | Q-81 |
| O contrato da spec 005 (§1) citava `services_tcc.tcc_e_do_curso_com_orientador_automatico`, que nunca foi criada; a linha foi corrigida para apontar `services_turmas.turma_tem_orientador_automatico(tcc.tcc_tur)`, que a 006 usa (só documento, sem código) | ciência de Leandra Matos (spec 005) | Q-96 (complemento) |
| Cancelamento da troca pendente no agendamento: a 006 entrega o serviço (contrato §3); a feature de Agendamento (US-24) o chama com o instante do evento "Agendamento" | Célio Benjamim (Defesa) | contrato §3 |

## Complexity Tracking

Nenhuma violação da constituição sem justificativa. A exceção já aceita (princípio IV: regras
também fora de `services.py`) é reaplicada. Escolhas que merecem registro:

| Escolha | Por quê | Alternativa mais simples rejeitada |
|---|---|---|
| Três módulos de serviço novos | Três domínios de dados com regras de acesso diferentes (vínculo ativo para atas; Coordenador do curso para artigos; docente indicado para solicitações). Arquivos menores facilitam a revisão. | Um `services_orientacao.py` só: passaria de 1.000 linhas e misturaria as três regras de acesso |
| Instante do evento passado como parâmetro opcional (IC-04) em vez de coluna de motivo | O usuário decidiu não criar coluna (Q7). O parâmetro opcional não muda quem já chama as funções. | Coluna `sol_motivo_cancelamento`: recusada (Q7); deduzir pela ordem das linhas: falha quando o aluno cancela antes do evento |
| Volta ao painel por `?volta=painel` com valor fechado (IC-03, IC-07) | Reaproveita as telas de ação já testadas das specs 004 e 005 sem duplicá-las e sem redirecionamento aberto | Copiar as telas para dentro do painel: duplicaria regras e testes; `next=<url>` livre: risco de redirecionamento aberto |
| Endereço da tela provisória mantido como redirecionamento (IC-08) | Não quebra links já enviados ou guardados e resolve a S-02 | Remover a rota (Q12, opção C, recusada) |
| `?secao=` + `static/js/secao.js` para os E1 | O fragmento `#secao` se perde no POST do login; o parâmetro sobrevive ao `next` | Só âncora `#`: falha no retorno do login (research R12) |
