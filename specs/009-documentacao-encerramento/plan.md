# Implementation Plan: Documentação e Encerramento do SIGTCC

**Status**: Approved (Célio Benjamim, 2026-11-05) — revisão do `arquiteto-django` incorporada
(B-01 a B-03, I-01 a I-09, M-01 a M-14)

**Branch**: `feature/feat-09-documentos` | **Date**: 2026-11-04 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/009-documentacao-encerramento/spec.md`, depois da
conferência do `analista-requisitos` (P1 a P16) e do `/speckit-clarify` (Q-140 e turma
arquivada), decididos por Célio Benjamim em 2026-11-04, e da decisão B-03 da revisão do plano
(Presidente da banca, 2026-11-05).

**Responsável pelas US de origem**: Célio Benjamim (US-28 e US-30).

## Summary

Implementar no app `sigtcc/apps/defesa` (Épico 2) o encerramento da defesa: Ata Final e Folha de
Aprovação em PDF sob demanda, com a E2 da US-28 (US-28; RBN-DEF-07.1 a 07.3); ouvintes da sessão
e ocorrências (RBN-DEF-08.2, 08.5); a lista "Ouvintes das defesas" da Secretaria (RBN-DEF-08.4);
a declaração de participação por e-mail e a segunda via, com código de validação sem
armazenamento (RBN-DEF-08.3); e a agenda de defesas em PDF (RBN-DEF-08.1). Tudo sobre tabelas
já existentes (`Ouvintes`, `Presenca_Ouvintes` e `Defesas.def_ocorrencias`) — **nenhuma tabela,
coluna ou migração nova**.

Abordagem: corpos reais em `services_documentos.py` (stubs da spec 008) e módulo novo
`services_ouvintes.py`; PDFs pelo utilitário `pdf.py` da spec 008 (memória, sem rede, nada
gravado); contrato da spec 007 (`membros_efetivos`, travas, filtros, blocos de `sessao.html`) e
da spec 008 (`resultado_da_sessao`, `ao_liberar_resultado`, `declaracao_disponivel`). A E2 na
liberação exige uma emenda pequena à spec 008 (`views_avaliacoes.liberar_resultado`), já
registrada nas Clarifications e no contrato §2 dela (Q-144).

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Django 5.2.18, psycopg 3, python-dotenv, `xhtml2pdf` 0.2.28 (spec 008).
Nenhuma dependência nova; `pypdf==6.21.4` (já fixado no `requirements.txt`) é usado só nos
testes.

**Storage**: PostgreSQL 16, tabelas da spec 001: grava `Ouvintes`, `Presenca_Ouvintes` e
`Defesas.def_ocorrencias`; lê `Defesas`, `Defesas_Presenciais`, `Defesas_Remotas`,
`Banca_Defesa`, `Avaliacoes`, `Criterios`, `Coordenadores`, `Docentes`, `MembrosExternos`,
`Secretarios`, `Usuarios`, `Alunos`, `TCCs`, `Turmas`, `Cursos`; grava `Notificacoes` só por `services.notificar`. Arquivos: só leitura das
imagens de assinatura no `default_storage`; **nenhum PDF gravado**. Nenhuma migração
([data-model.md](data-model.md)).

**Testing**: test runner do Django contra PostgreSQL; reaproveita `apoio_defesa.py` e
`apoio_avaliacao.py`; acrescenta `apoio_documentos.py`. `MEDIA_ROOT` temporário,
`captureOnCommitCallbacks(execute=True)`, `SIGTCC_EMAIL_SINCRONO=True`, `mail.outbox`, `pypdf`
para o texto dos PDFs, `mock.patch` para a falha de geração (research B15).

**Target Platform**: servidor web Linux (Render) ou Windows local, fuso America/Manaus; telas do
protótipo de 17/10 só como referência visual.

**Project Type**: aplicação web monolítica com renderização no servidor (Django MVT).

**Performance Goals**: sem meta numérica (a SC-005 antiga saiu, ajuste B). Listas e a agenda em
uma consulta cada, sem consulta por linha (research B11, B12); a liberação não espera os PDFs
das declarações (thread, research B7).

**Constraints**:
- nenhuma tabela, coluna ou migração nova; nunca gravar `def_status`, `Historico_Defesas`,
  `def_ata_final_path` ou `def_folha_aprovacao_path`;
- nenhum PDF gravado; nenhuma URL pública de arquivo; download só depois da permissão;
- ordem de trava turma → aluno → TCC → sessão (`travar_tcc` + `travar_sessao`, specs 007 e
  008); matrículas novas de ouvintes em ordem crescente (research B9);
- "Orientador do trabalho" = Presidente da banca (B-03);
- `pdf.gerar_pdf` serializado por trava de módulo (a thread das declarações e os downloads
  podem coincidir; research B7);
- permissões só em `permissoes_defesa.py` e visões calculadas no serviço (templates sem regra);
- a E2 e as declarações nunca desfazem nem bloqueiam a liberação;
- mensagens idênticas às US-28 e US-30, ou as MX provisórias (Q-142).

**Scale/Scope**: 6 histórias (56 cenários de aceite), 24 FR, 7 rotas novas, 6 telas ou janelas
novas, 4 PDFs, 1 e-mail, 18 itens de configuração em código ou documento já mesclado.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Verificação | Resultado |
|---|---|---|
| I. Especificação primeiro | Spec 009 com Clarifications de 2026-11-04 e 2026-11-05 (P1 a P16, Q-140, turma arquivada, B-03), sem `[NEEDS CLARIFICATION]`; checklist 16/16. Falta a aprovação formal da spec e deste plano por Célio Benjamim antes do `/speckit-implement`. | PASSA |
| II. Rastreabilidade | Todo FR com `[RBN-DEF-XX]`; código e testes levarão `[US-28]`, `[US-30]` e os RBN. | PASSA |
| III. Modelo de dados oficial | Nenhuma tabela ou coluna nova; `Ouvintes` (3.1.6), `Presenca_Ouvintes` (3.6.5) e `Defesas.def_ocorrencias` (3.6.1) conferidos contra o dicionário. O código de validação é calculado, como manda a regra 4 dos mecanismos do dicionário. | PASSA |
| IV. Arquitetura | Tudo no app `defesa` (Épico 2); regras em `services_documentos.py` e `services_ouvintes.py`; permissões em `permissoes_defesa.py`; views só orquestram; templates em `sigtcc/templates/defesa/`. | PASSA |
| V. Qualidade | pre-commit (isort, black -l 100, flake8 100); comentários em português com `[US-XX][RBN-...]`. | PASSA |
| VI. Testes de aceitação | Um teste por cenário das 6 histórias (SC-005), mais código de validação, mensagens exatas e os ajustes das specs 005 e 008. | PASSA |
| VII. Segurança e LGPD | Downloads conferem a permissão e o estado antes de gerar; nomes de arquivo sem nome de pessoa; código com HMAC da `SECRET_KEY`; ouvintes (nome e matrícula) visíveis só a quem edita e à Secretaria do curso; `media/` fora do Git. | PASSA |
| VIII. Gerência de configuração | Branch `feature/feat-09-documentos`; código de outras specs listado em "Itens de configuração" e relatado no PR (Q-128). | PASSA |
| IX. Governança | Divergências registradas: US-30 E9 × RBN-DEF-08.5 (Q-143, segue a matriz); E2 na liberação × diagrama 28 (Q-144); textos provisórios (Q-142). | PASSA com ressalva (texto da US-30 é do dono do documento de US) |

**Reavaliação depois do Phase 1**: nenhuma violação nova. O design não cria tabela, coluna nem
dependência; a emenda à spec 008 está registrada na própria spec 008 (Clarifications, sessão de
2026-11-04) e no contrato §2 dela.

## Project Structure

### Documentation (this feature)

```text
specs/009-documentacao-encerramento/
├── spec.md                          # Clarifications de 2026-11-04
├── plan.md                          # este arquivo
├── research.md                      # Phase 0 (B1 a B15, com a revisão incorporada)
├── data-model.md                    # Phase 1 (nenhuma tabela nova)
├── quickstart.md                    # Phase 1
├── contracts/
│   ├── rotas.md                     # 7 rotas novas e telas
│   └── servicos-documentos.md       # o que a spec 008, o Meu TCC e o Épico 3 chamam
├── checklists/requirements.md       # 16/16
└── tasks.md                         # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
sigtcc/apps/defesa/
├── services_documentos.py                # IC-01: corpos reais dos stubs + Ata, Folha, E2,
│                                         #   código, declaração, agenda, visões
├── services_ouvintes.py                  # novo: ouvintes, ocorrências, Ouvintes das defesas
├── forms_ouvintes.py                     # novo: OuvinteForm (formset), OcorrenciasForm
├── views_documentos.py                   # novo: Ata, Folha, Declaração e agenda
├── views_ouvintes.py                     # novo: ouvintes, ocorrências, Ouvintes das defesas
├── pdf.py                                # IC-14: trava de módulo em gerar_pdf
├── views_avaliacoes.py                   # IC-02: aviso da E2 depois da liberação (emenda 008)
├── views_defesa.py                       # IC-03: contexto dos blocos; IC-06: botão da agenda
├── permissoes_defesa.py                  # IC-08: + funções do research B2; e_presidente
│                                         #   pública (_e_presidente delega)
├── urls.py                               # IC-08: + 7 rotas
├── mensagens.py                          # IC-08: + textos das US-28/US-30 e MX-01 a MX-09
└── tests/
    ├── apoio_documentos.py
    ├── apoio_avaliacao.py                # IC-16: Coordenador com assinatura por padrão
    ├── test_us28_documentos.py
    ├── test_us30_ouvintes.py
    ├── test_us30_ocorrencias.py
    ├── test_us30_ouvintes_das_defesas.py
    ├── test_us30_declaracao.py
    ├── test_us30_agenda.py
    ├── test_codigo_validacao.py
    ├── test_permissoes_documentos.py
    └── test_mensagens_documentos.py
sigtcc/templates/defesa/
├── _bloco_documentos.html, _bloco_ouvintes.html, _bloco_ocorrencias.html   # novos
├── form_ouvintes.html, form_ocorrencias.html, ouvintes_das_defesas.html   # novos
├── _documentos_aluno.html                                                  # novo (Meu TCC)
├── pdf/ata_final.html, folha_aprovacao.html, declaracao.html, agenda.html # novos
├── emails/declaracao.txt                                                   # novo
├── sessao.html                           # IC-03: blocos documentos, ouvintes, ocorrencias
├── defesas.html                          # IC-06: botão "Agenda de defesas (PDF)"
└── minhas_bancas.html                    # IC-04: Declaração aponta para defesa:declaracao
sigtcc/static/js/ouvintes.js              # novo: Adicionar/Remover linhas do formset
sigtcc/apps/cadastro/
├── menu.py                               # IC-07: + "Ouvintes das defesas" (secretaria)
├── views.py                              # IC-11: SEM_PERMISSAO_DOCUMENTOS em MENSAGENS_403
├── services.py                           # IC-12: enviar_email aceita anexos (opcional)
├── tests/test_enviar_email_anexos.py     # novo (T007)
├── views_tcc.py                          # IC-05: documentos do aluno na aba Meu TCC
└── management/commands/popular_demo.py   # IC-09: ouvintes, ocorrências, assinatura do
                                          #   Coordenador (research B14)
sigtcc/templates/cadastro/tcc/meu_tcc.html  # IC-05: inclui _documentos_aluno.html; saem os
                                            #   botões desabilitados
```

**Structure Decision**: tudo no app `defesa` (PGCS 2.3). A lista "Ouvintes das defesas" fica no
`defesa` (é da US-30); o relatório consolidado com exportação (RBN-REL-03.4) será do app
`relatorios` e reaproveitará `services_ouvintes.ouvintes_das_defesas` (contrato §2).

## Ordem de implementação e commits

1. Fase base: `mensagens.py`, permissões (B2), `services_documentos` (situação da E2, código,
   dados da Ata/Folha/declaração), `apoio_documentos.py`, `test_codigo_validacao.py`; IC-11 e
   IC-12 (só acréscimos).
2. US1 Ata e Folha: views, PDFs, bloco `documentos`, aba Meu TCC (IC-03, IC-05), aviso da E2 na
   liberação (IC-02) e testes da US-28.
3. US2 ouvintes e US3 ocorrências: `services_ouvintes`, forms, janelas, blocos e `ouvintes.js`.
4. US4 Ouvintes das defesas: tela e menu (IC-07).
5. US5 declaração: trava do `pdf.py` (IC-14), `ao_liberar_resultado`, `declaracao_disponivel`,
   e-mail, rota, Minhas bancas (IC-04, IC-15).
6. US6 agenda: serviço, PDF, botão na tela Defesas (IC-06).
7. `popular_demo` (IC-09), documentos (IC-10, IC-13, IC-17), validação manual.

Cada fase num commit atômico, com os testes passando (CLAUDE.md).

## Itens de configuração (código de outras specs)

Aprovados pela Q-128 ("pode mexer no que for necessário, relatando"); cada um será relatado no PR.

| IC | Arquivo e spec de origem | O que muda | Por quê |
|---|---|---|---|
| IC-01 | `defesa/services_documentos.py` (008) | Corpos reais de `ao_liberar_resultado` e `declaracao_disponivel`, sem mudar assinatura nem ponto de chamada; funções novas do contrato §1 | Contrato §2 da 008; FR-019 a FR-021 |
| IC-02 | `defesa/views_avaliacoes.py` (008) | No ramo `resultado.liberado` de `liberar_resultado`, chama `avisar_pendencia_da_ata` e mostra o texto com `messages.warning` | P1; emenda registrada na spec 008 (Q-144) |
| IC-03 | `defesa/views_defesa.py` e `sessao.html` (007/008) | `contexto_da_sessao` ganha `documentos` e `ouvintes`; blocos `documentos`, `ouvintes` e `ocorrencias` incluem as parciais | Contrato §3 da 007; FR-003, FR-009, FR-013 |
| IC-04 | `defesa/minhas_bancas.html` (008) | Link "Declaração" passa de `defesa:sessao` para `defesa:declaracao` | FR-021 |
| IC-05 | `cadastro/views_tcc.py` e `cadastro/tcc/meu_tcc.html` (005/008) | Contexto `documentos_defesa`; inclui `_documentos_aluno.html`; saem os botões desabilitados "Ata Final" e "Folha de Aprovação" do cartão Defesa | FR-003; P14 |
| IC-06 | `defesa/views_defesa.py` (`defesas`) e `defesas.html` (007) | Botão "Agenda de defesas (PDF)" para `pode_gerar_agenda`, com a query string atual | FR-022 |
| IC-07 | `cadastro/menu.py` (003) | + item "Ouvintes das defesas" (perfil `secretaria`) | FR-016 |
| IC-08 | `defesa/permissoes_defesa.py`, `urls.py`, `mensagens.py` (007/008) | Só acréscimos | research B2, B3 |
| IC-09 | `cadastro/management/commands/popular_demo.py` | Ouvintes, ocorrências e assinatura de demonstração de um Coordenador, só por serviços | research B14 |
| IC-10 | `docs/diagramas/Diagramas_Sequencia_PlantUML_v2.md` | Nota do diagrama 05 (ocorrências só do Orientador), feita no `/speckit-clarify`; passo da E2 na liberação no diagrama 28 | P9; P1 (Q-144) |
| IC-11 | `cadastro/views.py` (003) | `SEM_PERMISSAO_DOCUMENTOS` em `MENSAGENS_403`; só acréscimo | US-28 E6; research B3 |
| IC-12 | `cadastro/services.py` (003) | `enviar_email(..., anexos=None)`: com anexos usa `EmailMessage`; sem anexos, a mesma chamada literal `send_mail` (cinco testes da 003 a substituem por `mock.patch`); docstring "template de e-mail" | research B7; revisão M-04 |
| IC-13 | `specs/008-avaliacao-resultados/spec.md` e `contracts/servicos-avaliacoes.md` (008, já mesclada) | Clarifications (sessão de 2026-11-04) e linha nova no §2, que passa a citar `services_documentos.avisar_pendencia_da_ata(sessao) -> str \| None`; feito no `/speckit-clarify` e na revisão do plano | CLAUDE.md: mudança depois do merge começa pela spec; revisão I-09 |
| IC-14 | `defesa/pdf.py` (008) | `threading.Lock` de módulo em volta da renderização de `gerar_pdf`; assinatura e comportamento iguais | Revisão I-07 (estado global do xhtml2pdf/reportlab) |
| IC-15 | `defesa/services_avaliacoes.py` (008) | Docstring de `minhas_bancas`: as sessões Realizadas fazem uma consulta a mais (Declaração) | Revisão M-11 |
| IC-16 | `defesa/tests/apoio_avaliacao.py`, `test_us27_liberacao.py`, `test_minhas_bancas.py`, `test_pdf.py` (008); `cadastro/tests/test_navegacao_tcc.py` (004/005) | Apoio cria Coordenador com assinatura por padrão; ajustes nominais do research B15 | Revisão I-06 |
| IC-17 | `docs/diagramas/Rastreabilidade_Diagramas_Codigo.md`, `CHANGELOG.md`, `docs/arquitetura/Componentes_SIGTCC.drawio` | Rastreabilidade: `:GeradorDocumentosPDF` deixa de ser "stubs da feat-09"; entram `services_ouvintes`, `views_documentos`, `views_ouvintes` e o participante do diagrama 05. CHANGELOG: entrada da feat-09. Componentes: rótulo do componente da Defesa com documentos e ouvintes (PNG fica na Q-137) | Revisão I-09 |
| IC-18 | `defesa/permissoes_defesa.py` (008) | `_e_presidente` passa a delegar para a pública `e_presidente` | Revisão M-02; B-03 |

Testes de outras specs a ajustar (IC-16; research B15): `apoio_avaliacao.sessao_com_banca` cria
um Coordenador com assinatura por padrão; `test_us27_liberacao.test_avisos_ao_aluno_banca_e_secretaria_sem_a_nota`
passa a esperar também o assunto da MX-04; novo teste do alerta da E2 em `test_us27_liberacao`;
`test_minhas_bancas` (destino do link Declaração e `declaracao_disponivel` real). Nenhum teste
atual confere os botões desabilitados do Meu TCC; um teste novo confere que saíram.

## Pendências desta feature

Índice central: [docs/questoes-a-rever.md](../../docs/questoes-a-rever.md).

| Pendência | Destino | Índice |
|---|---|---|
| Textos provisórios MX-01, MX-03 a MX-05, MX-07 a MX-09 e o modelo institucional da declaração | Profa. Diana (PO) | Q-142 |
| US-30 E9 e cenário 19 × RBN-DEF-08.5 (ocorrências só do Orientador) | Dono do documento de US | Q-143 |
| Emenda à spec 008 e passo da E2 no diagrama 28 | Célio Benjamim (ciência e diagrama) | Q-144 |
| "Orientador do trabalho" = Presidente da banca (decidida) | Célio Benjamim | Q-145 (respondida) |
| Textos que pressupõem PDFs gravados; colunas `_path` sem uso; PGCS | PO, Maria Luiza Guimarães, Célio | Q-132, Q-133, Q-134 |
| Tela de verificação do código; histórico de Coordenadores; assinatura no banco | PO | S-07, S-05, S-06 |

## Complexity Tracking

Nenhuma violação da constituição.

| Escolha | Por quê | Alternativa mais simples rejeitada |
|---|---|---|
| Módulo novo `services_ouvintes.py` | Escrita com trava e validação, consumida também pelo Épico 3; separada da geração de PDFs | Tudo em `services_documentos.py`: mistura gravação e geração |
| `enviar_email` com anexo opcional (IC-12) | A declaração vai por e-mail em PDF (US-30 D); um só ponto de envio e de registro da falha | Segundo helper de e-mail só para a defesa: duas regras de envio |
| Contexto das declarações lido no callback e PDF gerado na thread | A thread não abre conexão ao banco; a liberação não espera 3 PDFs | Gerar os PDFs no próprio `on_commit`: a resposta da liberação demora |
| Trava de módulo em `gerar_pdf` | O xhtml2pdf/reportlab têm estado global; a thread das declarações e um download podem coincidir | Sem trava: falha intermitente difícil de reproduzir |
