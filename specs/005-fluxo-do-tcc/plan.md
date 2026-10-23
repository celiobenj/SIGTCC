# Implementation Plan: Fluxo do TCC e Entregas do SIGTCC

**Branch**: `feature/feat-05-fluxo-do-tcc` | **Date**: 2026-10-22 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/005-fluxo-do-tcc/spec.md` (aprovada por Julia Cohen em
2026-10-22, depois da conferência do `analista-requisitos` e de 3 perguntas do `/speckit-clarify`)

**Responsável**: Leandra Matos (US-13, 14, 15, 16, 29, 43 e 44).

**Aprovação**: plano aprovado por Julia Cohen em 2026-10-22, depois de duas rodadas de revisão do
`arquiteto-django` (3 bloqueantes e 4 importantes corrigidos, confirmados fechados em 2026-10-22).

## Summary

Implementar no app `cadastro` (Épico 1) o ciclo de vida do TCC e das entregas, sobre o modelo de
dados já existente (spec 001, nenhuma tabela ou coluna nova): a Proposta e os dados do TCC com
mudança de tema (US-13); o Status do TCC somente leitura, atualizado por 7 gatilhos fixos, com
histórico e trilha (US-14); o cadastro de entregas pelo Professor da Disciplina, inclusive para
alunos já matriculados (US-43, índice Q-41); o envio e a substituição do link pelo Aluno, com
lembretes de prazo (US-15); o acompanhamento das entregas pelo Professor (US-16); o envio da Versão
Final do TCC 2 (US-29); e a homologação ou devolução para ajuste da Versão Final, que conclui o TCC
(US-44).

Abordagem: regras em `services_tcc.py` (novo, Proposta/TCC/Status/histórico/trilha — US-13 e US-14)
e `services_entregas.py` (novo, entregas — US-43, 15, 16, 29 e 44), views finas em `views_tcc.py` e
`views_entregas.py`, reaproveitando de `services_turmas.py` (spec 004) a permissão por turma
(`turma_para`, `vinculo_na_turma`), `participacao_encerrada`, `travar_turma_ativa`,
`turma_tem_orientador_automatico` e `criar_entregas_do_aluno`. O serviço de gravação do Status e do
histórico (FR-012) já existe como função privada `_registrar_historico` em `services_turmas.py`
(usada hoje pelos gatilhos da spec 004: Vínculo à turma, Transferência para TCC 2, Encerramento da
participação); esta spec mantém `_registrar_historico` privada e acrescenta, no mesmo arquivo,
**duas** funções públicas, validadas contra a mesma tabela de transições do FR-008 (não só a
existência do gatilho): `criar_tcc_com_historico` (para os 2 gatilhos que criam o TCC — Vínculo à
turma e Transferência para TCC 2, cujo "status anterior" não está no objeto, está em `None` ou
noutra linha) e `atualizar_status_tcc` (para os 5 gatilhos que mudam o status de um TCC já
existente — Proposta salva, Indicação de Apto, Liberação do resultado, Homologação da Versão
Final e Encerramento da participação), que pressupõe quem chama já travou turma → aluno → TCC
antes (`select_for_update`, research C4) — revisão do `arquiteto-django` de 2026-10-22 (ver
research C2 e Complexity Tracking).

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Django 5.2, psycopg 3, python-dotenv (já no `requirements.txt`). Nenhuma
dependência nova — esta feature não lê arquivos nem gera PDF.

**Storage**: PostgreSQL 16, com as tabelas já existentes da spec 001 (`TCCs`, `PalavrasChave_TCC`,
`Historico_Status_TCC`, `Turmas_Marcos`, `Entregas_Marcos`, `Historico_Envios_Entregas`). Nenhuma
migração de esquema; nenhuma migração de dados (ao contrário da spec 004, que teve a carga de
equivalência de cursos).

**Testing**: test runner do Django contra PostgreSQL; reaproveita `tests/apoio_acesso.py` e
`tests/apoio_turmas.py` (`criar_turma_de`, `matricular_aluno`, `tcc_de`) da spec 004; relógio
controlado (`avancar_relogio` ou equivalente) para testar Data Limite, lembretes de prazo (7 dias,
48h, 24h) e a diferença entre "Entregue" e "Entregue com Atraso".

**Target Platform**: servidor web Linux ou Windows (fuso America/Manaus); navegadores atuais, de
360 px para cima (spec 003, Q22), seguindo a base visual da spec 003/004.

**Project Type**: aplicação web monolítica com renderização no servidor (Django MVT).

**Performance Goals**: SC-001 (Aluno salva a Proposta em menos de 2 minutos) e SC-003 (Professor
cadastra uma entrega em menos de 1 minuto) são metas de teste manual (roteiro do `quickstart.md`),
não de carga; sem meta de requisições por segundo.

**Constraints**: nenhuma tabela ou coluna nova; mensagens idênticas às US-13, 14, 15, 16, 29, 43 e
44 ou marcadas como provisórias (MF-01 a MF-03); Status do TCC nunca editado fora do serviço único
(FR-012); nenhuma ação em turma arquivada (`travar_turma_ativa`/`TurmaArquivada`, MT-25); lembretes
de prazo fora de uma view síncrona (rotina agendada, a configurar pelo Célio — mesmo padrão da
`executar_rotina_agendada` do PGCS 3.6, se já existir, ou criada por esta feature).

**Scale/Scope**: 7 US (97 cenários: 89 originais + 4 da conferência/clarify + 4 da navegação,
sessão 2026-10-23), 32 FR (FR-001 a FR-031 e FR-007a), 3 mensagens provisórias (MF-01 a MF-03);
cerca de 11 telas e 13 rotas novas (2 delas de navegação do Aluno, FR-031, Q-89).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Verificação | Resultado |
|---|---|---|
| I. Especificação primeiro | spec 005 aprovada por Julia Cohen em 2026-10-22, sem marcadores `[NEEDS CLARIFICATION]` (3 perguntas resolvidas no `/speckit-clarify`). | PASSA |
| II. Rastreabilidade | Todo FR já traz `[RBN-CAD-XX]`; services, views, forms, templates e testes levam `[US-XX][RBN-...]`. | PASSA |
| III. Modelo de dados oficial | Nenhuma tabela ou coluna nova ([data-model.md](data-model.md)); `TCCs`, `PalavrasChave_TCC`, `Historico_Status_TCC`, `Turmas_Marcos`, `Entregas_Marcos` e `Historico_Envios_Entregas` já existem com os campos, tipos e restrições do dicionário (confirmado em `models.py` e `choices.py`, spec 001). | PASSA |
| IV. Arquitetura | Tudo em `sigtcc/apps/cadastro`; regras em `services_tcc.py` e `services_entregas.py` (novos), views só orquestram, templates sem regra; templates em `sigtcc/templates/cadastro/tcc/`, static reaproveitado. O princípio fala em `services.py`: `services_tcc.py` e `services_entregas.py` são exceção justificada, no mesmo padrão já aceito para `services_turmas.py` e `importacao.py` da spec 004 (Complexity Tracking). | PASSA com exceção justificada (mesma já aceita na spec 004) |
| V. Qualidade | `lint.bat` (isort, black, flake8); comentários em português. | PASSA |
| VI. Testes de aceitação | Um teste por cenário das 7 US (97), mais permissões (Secretaria e Coorientador excluídos, Clarifications), mensagens exatas e concorrência (trava turma → aluno → TCC antes de `atualizar_status_tcc`, duplo clique em envio de entrega e em Palavra-Chave, research C2, C3, C4 e C7, revisão do `arquiteto-django`). | PASSA |
| VII. Segurança e LGPD | Resumo da Proposta restrito por `services_tcc.pode_ver_resumo` (Aluno, Orientador, Coorientador do NUCOMP e Professor da Disciplina — FR-007a, RAN-CAD-07 NFR, research C3); Status/histórico restritos por `services_tcc.historico_do_status` + checagem na view (Aluno/Orientador/Professor, sem Secretaria nem Coorientador — Clarifications, research C9); link de entrega só `https://`; nenhum arquivo hospedado (só links); mudanças de Status, envios, homologação e devolução com autor, data e hora (`Historico_Status_TCC`, `Historico_Envios_Entregas`). | PASSA |
| VIII. Gerência de configuração | Commits atômicos por fase; branch `feature/feat-05-fluxo-do-tcc`; `services_turmas.py` (spec 004, já mesclada) ganha `atualizar_status_tcc` pública e `TRANSICOES_VALIDAS`, sem alterar `_copiar_tcc_aprovado` (exceção documentada, research C2); testes de regressão da spec 004 (US-08, US-09) precisam continuar passando sem alteração, no mesmo PR. Navegação (FR-031, Q-89): `menu.py` e `templates/cadastro/turmas/turma.html` (spec 004, já mesclados) recebem só acréscimos — um item de menu do Aluno e o include da barra de abas —, sem mudar o FR-010 da spec 004 nem os testes dela. | PASSA (refatoração e acréscimos: ver Pendências, Q-82 e Q-89) |
| IX. Governança | Mensagens MF-01 a MF-03 pendentes de validação da PO; nomes de aba (Q-80) e do link de histórico (Q-81) pendentes de confirmação de Leandra Matos ou da PO; refatoração de `services_turmas.py` (Q-82) pendente de aprovação de Leandra e Célio. | PASSA (pendências não bloqueantes) |

**Reavaliação depois do Phase 1 e da revisão do `arquiteto-django` (2026-10-22)**: 3 achados
bloqueantes e 4 importantes foram corrigidos no research e nos contratos (ver research C2, C3, C4,
C7 e C9): a tabela `TRANSICOES_VALIDAS` valida a transição completa, não só o gatilho; as duas
funções públicas (`criar_tcc_com_historico` para os 2 gatilhos de criação, `atualizar_status_tcc`
para os 5 de transição) documentam a pré-condição de trava de quem chama e resolvem corretamente
de onde vem o "status anterior" em cada caso (do objeto, de fora, ou de outra linha);
`pode_ver_resumo` e `historico_do_status` passam a ser funções centralizadas, não regra só em
texto; `select_for_update` foi acrescentado ao envio de entrega e à gravação de Palavra-Chave.
Nenhuma violação nova da constituição. Os 3 pontos já existentes da spec 004 (`matricular`,
`_copiar_tcc_aprovado`, `encerrar_participacao`) passam a chamar uma das duas funções públicas em
vez do padrão manual, sem mudar comportamento; os testes da spec 004 continuam cobrindo esses
casos.

## Project Structure

### Documentation (this feature)

```text
specs/005-fluxo-do-tcc/
├── spec.md                          # aprovada em 2026-10-22
├── plan.md                          # este arquivo
├── research.md                      # Phase 0 (C1 a C9)
├── data-model.md                    # Phase 1 (nenhuma tabela nova)
├── quickstart.md                    # Phase 1
├── contracts/
│   ├── rotas.md                     # telas e rotas novas
│   └── servicos-compartilhados.md   # o que a spec 006 pode chamar
├── checklists/requirements.md       # já validado (16/16)
└── tasks.md                         # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
sigtcc/apps/cadastro/
├── services_tcc.py                  # novo: C3, C9 — Proposta, pode_ver_resumo(), historico_do_status()
├── services_entregas.py             # novo: C5 a C7 — cadastro, envio, acompanhamento, homologação
├── services_turmas.py               # + criar_tcc_com_historico() e atualizar_status_tcc()
│                                     #   públicas, TRANSICOES_VALIDAS (C2); _registrar_historico
│                                     #   continua privada, chamada só por essas duas
├── forms_tcc.py                     # novo: Proposta, TCC (área/palavras-chave)
├── forms_entregas.py                # novo: cadastro de entrega, envio de link, devolução
├── views_tcc.py                     # novo: aba Meu TCC, histórico do Status, "Turmas" do Aluno
│                                     #   (minhas_turmas, minhas_turmas_arquivadas; FR-031)
├── views_entregas.py                # novo: aba Atividades (cadastro, envio, acompanhamento), homologação
├── urls.py                          # + rotas novas (contracts/rotas.md)
├── menu.py                          # + item "Turmas" do Aluno (rota minhas_turmas), logo depois
│                                     #   de "Início" (FR-031, Q-89); o item "Turmas" de Docente e
│                                     #   Secretaria (spec 004) não muda
├── mensagens.py                     # + textos das US-13, 14, 15, 16, 29, 43, 44 e MF-01 a MF-03
└── tests/
    ├── apoio_tcc.py                 # novo: fábricas de Proposta, entregas e links de envio
    ├── test_us13_proposta.py
    ├── test_us14_status_historico.py
    ├── test_us43_cadastro_entregas.py
    ├── test_us15_envio_entrega.py
    ├── test_us16_acompanhamento.py
    ├── test_us29_versao_final.py
    ├── test_us44_homologacao.py
    ├── test_permissoes_tcc.py        # Secretaria e Coorientador excluídos (Clarifications)
    ├── test_mensagens_tcc.py         # SC-006, igual ao padrão de test_mensagens_turmas.py
    └── test_navegacao_tcc.py         # FR-031: menu e lista do Aluno, abas por perfil (Q-89)
sigtcc/templates/cadastro/tcc/
├── meu_tcc.html                     # Proposta + TCC + Status + link Histórico + Versão final
├── historico_status.html            # lista cronológica + trilha (US-14)
├── entregas.html                    # aba Atividades do Professor: lista + Cadastrar atividade
├── form_entrega.html                # cadastro de entrega (US-43)
├── acompanhamento_entrega.html       # tabela por aluno (US-16)
├── minhas_entregas.html             # aba Atividades do Aluno: lista com status
├── enviar_entrega.html              # envio/substituição de link (US-15, US-29)
├── homologar_versao_final.html      # Homologar / Devolver para Ajuste (US-44)
├── minhas_turmas.html               # "Turmas" e "Turmas arquivadas" do Aluno (FR-031)
├── _abas_aluno.html                 # abas Meu TCC | Atividades (meu_tcc, minhas_entregas)
└── _abas_professor.html             # abas Alunos | Atividades (turma.html da spec 004, entregas)
sigtcc/templates/cadastro/turmas/
└── turma.html                       # (spec 004) + include de _abas_professor.html (FR-031)
```

**Structure Decision**: monólito Django do PGCS 2.3, app `cadastro` (Épico 1, "Cadastro e
Manutenção", como toda a US-13 a 44 desta spec). Dois módulos novos por assunto (Proposta/Status
vs. entregas), no mesmo padrão de divisão já aceito para a spec 004 (`services_turmas.py` +
`importacao.py`).

## Pendências desta feature

Índice central: [docs/questoes-a-rever.md](../../docs/questoes-a-rever.md).

| Pendência | Destino | Índice |
|---|---|---|
| Acrescentar `criar_tcc_com_historico` e `atualizar_status_tcc` (públicas, FR-012, com `TRANSICOES_VALIDAS`) no mesmo arquivo `services_turmas.py`, mantendo `_registrar_historico` privada e sem mudar o comportamento dos 3 gatilhos já implementados pela spec 004 | Leandra Matos (autora desta spec) e Célio Benjamim (config, por tocar código já mesclado de outra feature) | Q-82 |
| Validar os textos provisórios MF-01 a MF-03 | Profa. Diana (PO) | — (seguem Q-36) |
| Confirmar o nome da aba ("Atividades" ou "Entregas", US-43) | Profa. Diana ou Leandra Matos | Q-80 |
| Confirmar o nome do link de histórico ("Histórico do Status do TCC" ou "Histórico", US-14) | Profa. Diana ou Leandra Matos | Q-81 |
| Rotina agendada para os lembretes de prazo (7 dias, 48h, 24h): usar `executar_rotina_agendada` do PGCS 3.6 se já existir, ou criar nesta feature | Célio Benjamim (config) | — |
| "Correções Conferidas" (Orientador, Sistemas de Informação) e "Apto para Defesa": a UI fica na "tela de orientandos" da spec 006 (ainda não existe); esta spec só expõe `atualizar_status_tcc` e o campo `ent_correcoes_conferidas_em` para a 006 chamar | Célio Benjamim (spec 006) | contrato §2 e §3 |
| Navegação (FR-031): item "Turmas" do Aluno e abas por perfil; `menu.py` e `turma.html` (spec 004) recebem só acréscimos — aprovar como item de configuração | Célio Benjamim (config) | Q-89 |
| "Tela do aluno" completa (painel único, US-41) ainda não existe; a homologação (US-44) ganha rota própria `/turmas/<tur_id>/alunos/<alu_id>/versao-final/`, a ser levada ao painel depois, como já ocorreu com US-09 na spec 004 | Leandra Matos | spec 004, Assumptions (mesmo padrão) |

## Complexity Tracking

Nenhuma violação da constituição sem justificativa. Exceção já aceita (reaplicada): princípio IV
(regras também fora de `services.py`). Escolhas que merecem registro:

| Escolha | Por quê | Alternativa mais simples rejeitada |
|---|---|---|
| Dois módulos novos (`services_tcc.py`, `services_entregas.py`) em vez de um só | TCC/Status (US-13, 14) e entregas (US-43, 15, 16, 29, 44) são dois domínios de dados (`TCCs`/`Historico_Status_TCC` vs. `Turmas_Marcos`/`Entregas_Marcos`) com responsáveis e gatilhos diferentes; manter dois arquivos pequenos facilita revisão | Um módulo `services_fluxo_tcc.py` só: ficaria maior que `services_turmas.py` e misturaria dois domínios |
| Promover `_registrar_historico` a `atualizar_status_tcc` pública, no mesmo arquivo `services_turmas.py` (spec 004) | Evita duplicar a lógica de gravação do histórico (violaria o próprio FR-012, "nunca alterado fora desse serviço"); manter no mesmo arquivo evita mover código já mesclado e revisado da spec 004 | Copiar a lógica para `services_tcc.py`: duplicaria código e criaria duas fontes de verdade para o histórico |
| Rotas de entrega e de homologação fora do painel único do aluno (US-41, ainda não implementado) | Mesma solução já aceita na spec 004 para US-09 (excluir/encerrar antes do painel existir) | Esperar a US-41 para implementar esta spec: atrasaria a entrega sem necessidade |
| Entrada própria do Aluno (item "Turmas" do Aluno e rotas `minhas_turmas`), com as abas desta spec, em vez de abrir ao Aluno a tela da turma da spec 004 (FR-031; Clarifications, sessão 2026-10-23) | Mantém o FR-010 da spec 004 (já mesclada) e não expõe a lista de colegas ao Aluno; as abas ficam em includes, reaproveitáveis pela spec 006 | Abrir `/turmas/<tur_id>/` ao Aluno: mudaria uma spec mesclada e os testes de permissão dela; só links no Painel: contraria o passo 1 das US-13 e 15 e não atende "Turmas arquivadas" |
