# Implementation Plan: Avaliação e Resultados do SIGTCC

**Status**: Approved (Célio Benjamim, 2026-11-03) — revisão do `arquiteto-django` incorporada
(B-01, I-01 a I-15, M-01 a M-13)

**Branch**: `feature/feat-08-avaliacao` | **Date**: 2026-11-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/008-avaliacao-resultados/spec.md`, depois da
conferência do `analista-requisitos` (D1 a D16, índice Q-130) e do `/speckit-clarify` (sem
ambiguidade crítica).

**Responsável pelas US de origem**: Célio Benjamim (US-25, US-26 e US-27).

## Summary

Implementar no app `sigtcc/apps/defesa` (Épico 2) a avaliação da banca e a liberação do resultado:
critérios fixos e sua consulta (DEF-04.1, DEF-04.2), Minhas bancas (DEF-05.4), o formulário
Avaliação com rascunho, envio assinado e reabertura (US-25, US-26), o cálculo das notas, o
parecer, a liberação e o resultado para o aluno (US-27), com o sigilo da RBN-DEF-06.8. Tudo sobre
as tabelas já existentes (`Criterios`, `Avaliacoes`, `Banca_Defesa`, `Defesas`) — **nenhuma
tabela, coluna ou migração nova**.

Abordagem: módulo de regras novo `services_avaliacoes.py`, consumindo o contrato da spec 007
(`transicionar_status`, `membros_efetivos`, blocos de `sessao.html`), da spec 005
(`atualizar_status_tcc`) e da spec 006 (`tem_artigo_homologado_qualis_ab`). A função real
`descartar_avaliacoes` substitui o stub da spec 007.

**Decisão de infraestrutura (Célio Benjamim, 2026-11-03)**: **nenhum arquivo é armazenado em
serviço externo**. As imagens de assinatura continuam no `default_storage` atual (disco do
serviço, apagado a cada deploy no Render gratuito; risco aceito). Os PDFs (Ata Final, Folha de
Aprovação e declarações, feat-09) são **gerados sob demanda**, a cada download, e nunca gravados.
Esta feature entrega, em commits `chore(config)`, o `xhtml2pdf` no `requirements.txt` e o
utilitário de PDF em memória com entrega por view que confere a permissão, sem endereço público
(research A9). Não há `STORAGES` externo. Os documentos que pressupunham PDFs gravados estão em
"Documentos a ajustar".

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Django 5.2.18, psycopg 3, python-dotenv (já no `requirements.txt`).
**Nova**: `xhtml2pdf` (geração de PDF em memória; PGCS 3.7), com a versão exata e as
dependências do `pip freeze` na instalação. Nenhum cliente de armazenamento externo.

**Storage**: PostgreSQL 16, tabelas já existentes (spec 001): `Criterios` (leitura), `Avaliacoes`
(leitura e gravação), `Banca_Defesa` (grava `ban_assinatura_path` e `ban_data_envio`), `Defesas`
(grava `def_parecer`, `def_nota_final`, `def_data_liberacao_resultado`). Arquivos: só a cópia da
imagem de assinatura da avaliação, no `default_storage` (disco), como as assinaturas do perfil.
Nenhuma migração ([data-model.md](data-model.md)).

**Testing**: test runner do Django contra PostgreSQL; reaproveita `apoio_acesso.py`,
`apoio_turmas.py`, `apoio_tcc.py`, `apoio_orientacao.py` e `defesa/tests/apoio_defesa.py`;
acrescenta `defesa/tests/apoio_avaliacao.py`. Imagens geradas em memória e `MEDIA_ROOT`
temporário (`override_settings`); `captureOnCommitCallbacks(execute=True)` para e-mails e para o
ponto de chamada da feat-09 (research A13).

**Target Platform**: servidor web Linux (Render) ou Windows local, fuso America/Manaus; telas do
protótipo de 17/10 ("Minhas bancas", "Avaliação", "Sessão de defesa") só como referência visual.

**Project Type**: aplicação web monolítica com renderização no servidor (Django MVT).

**Performance Goals**: SC-001 (avaliar em menos de 10 minutos) é meta de roteiro manual
([quickstart.md](quickstart.md)). Minhas bancas e a janela da sessão calculam os estados com
consultas agregadas, sem consulta por linha (research A2, A8).

**Constraints**:
- nenhuma tabela, coluna ou migração nova;
- `def_status` e `Historico_Defesas` só por `services_defesa.transicionar_status`; `tcc_status` só
  por `services_turmas.atualizar_status_tcc`; nunca criar sessão (contrato da spec 007);
- cálculo em `Decimal` com `ROUND_HALF_UP` (research A3);
- ordem de trava: turma → aluno → TCC → sessão → linha da banca, igual à da spec 007 (research
  A4, A6);
- sigilo por uma única função (`visao_da_avaliacao`), nunca em condicionais de template
  (research A7);
- e-mails e o ponto de chamada da feat-09 só depois do commit;
- nenhum PDF gravado; nenhuma URL pública de arquivo; `link_callback` do PDF sem acesso à rede
  (research A9);
- mensagens idênticas às US-25 a US-27, ou as MA-01 a MA-12 aprovadas (Q-129).

**Scale/Scope**: 5 histórias (52 cenários de aceite), 37 FR, 7 rotas novas, 4 telas novas, 3
parciais e 3 e-mails, 11 itens de configuração em código ou documento já mesclado.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Verificação | Resultado |
|---|---|---|
| I. Especificação primeiro | Spec 008 com Clarifications de 2026-11-03 (Q-125, Q-127 a Q-130), sem `[NEEDS CLARIFICATION]`; checklist 16/16. Falta a aprovação formal da spec e deste plano por Célio Benjamim antes do `/speckit-implement`. | PASSA |
| II. Rastreabilidade | Todo FR com `[RBN-DEF-XX]`; código e testes levarão `[US-25]`, `[US-26]`, `[US-27]` e os RBN. | PASSA |
| III. Modelo de dados oficial | Nenhuma tabela ou coluna nova; `Criterios`, `Avaliacoes`, `Banca_Defesa`, `Defesas` conferidas contra o dicionário (3.1.4, 3.6.1, 3.6.4, 3.6.6). As colunas `def_ata_final_path` e `def_folha_aprovacao_path` ficam sem uso (PDFs sob demanda); não são removidas sem atualizar o modelo (Q-133). | PASSA |
| IV. Arquitetura | Tudo no app `defesa` (Épico 2); regras em `services_avaliacoes.py`; permissões em `permissoes_defesa.py`; views só orquestram; templates sem regra (sigilo calculado no serviço). | PASSA |
| V. Qualidade | pre-commit (isort, black -l 100, flake8 100); comentários em português. | PASSA |
| VI. Testes de aceitação | Um teste por cenário das 5 histórias, mais cálculo (fronteiras), sigilo por perfil, mensagens exatas, concorrência envio × liberação e os ajustes da spec 007. | PASSA |
| VII. Segurança e LGPD | Formulário só para membros efetivos; sigilo da RBN-DEF-06.8; assinatura validada pelo conteúdo e servida só ao dono, sem URL pública; PDFs entregues só depois da permissão, sem gravar; `media/` continua fora do Git. | PASSA |
| VIII. Gerência de configuração | Branch `feature/feat-08-avaliacao`; infraestrutura em commits `chore(config)` separados; código de outras specs listado em "Itens de configuração" e relatado no PR (Q-128). | PASSA |
| IX. Governança | A geração sob demanda muda textos da matriz, das US-27/US-28, do dicionário e do PGCS: registrado para a PO (Q-132), para o modelo lógico (Q-133) e para a configuração (Q-134). A feat-08 não depende da resposta da Q-132: o ponto `ao_liberar_resultado` acomoda as duas saídas. | PASSA com ressalva (mudança de texto da matriz e das US é decisão da PO) |

**Reavaliação depois do Phase 1**: nenhuma violação nova. O design não cria tabela nem coluna; a
única dependência nova (`xhtml2pdf`) é a prevista no PGCS 3.7; o armazenamento externo previsto no
PGCS (3.4, 3.5 itens 8 e 9, 3.7, 9.1 e 9.5) foi retirado por decisão de configuração, registrada
na Q-134. A revisão do `arquiteto-django` (2026-11-03: B-01, I-01 a I-15, M-01 a M-13) foi
incorporada ao research, ao data-model, aos contratos e a este plano.

## Project Structure

### Documentation (this feature)

```text
specs/008-avaliacao-resultados/
├── spec.md                          # Clarifications de 2026-11-03
├── plan.md                          # este arquivo
├── research.md                      # Phase 0 (A1 a A13)
├── data-model.md                    # Phase 1 (nenhuma tabela nova)
├── quickstart.md                    # Phase 1
├── contracts/
│   ├── rotas.md                     # 7 rotas novas e telas
│   └── servicos-avaliacoes.md       # o que a spec 007 e a feat-09 chamam
├── checklists/requirements.md       # 16/16
└── tasks.md                         # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
requirements.txt                          # chore(config): + xhtml2pdf e dependências (PGCS 3.7)
sigtcc/apps/defesa/
├── pdf.py                                # chore(config): gerar_pdf, resposta_pdf, ErroAoGerarPdf
├── services_avaliacoes.py                # novo: estado, cálculo, salvar/enviar/reabrir,
│                                         #   descartar, voltar_envios_a_rascunho, sigilo,
│                                         #   parecer, liberação, resultado
├── services_documentos.py                # novo: stubs ao_liberar_resultado e
│                                         #   declaracao_disponivel (feat-09)
├── services_defesa.py                    # IC-01: descartar delega; alterar_banca (D16);
│                                         #   reagendar (D2); travar_tcc/travar_sessao públicas
├── permissoes_defesa.py                  # IC-09: + pode_avaliar, pode_reabrir,
│                                         #   pode_registrar_parecer, pode_liberar
├── forms_avaliacoes.py                   # novo: formset dos 9 critérios, assinatura, parecer,
│                                         #   confirmação da liberação
├── views_avaliacoes.py                   # novo: as 7 views de contracts/rotas.md
├── views_defesa.py                       # IC-05: contexto da avaliação e do resultado na
│                                         #   sessão; sessao_ou_404 pública
├── urls.py                               # IC-09: + 7 rotas
├── mensagens.py                          # IC-09: + textos das US-25 a US-27 e MA-01 a MA-12
└── tests/
    ├── apoio_avaliacao.py
    ├── test_us25_avaliacao.py
    ├── test_us26_assinatura.py
    ├── test_us27_liberacao.py
    ├── test_calculo_notas.py
    ├── test_sigilo.py
    ├── test_minhas_bancas.py
    ├── test_pdf.py
    └── test_mensagens_avaliacao.py
sigtcc/templates/defesa/
├── minhas_bancas.html, criterios.html, avaliacao.html, confirmar_liberacao.html   # novos
├── _bloco_avaliacao.html, _bloco_resultado.html, _resultado_aluno.html           # novos
├── emails/resultado_aluno.txt, resultado_banca.txt, resultado_secretaria.txt    # novos
└── historico.html                        # IC-06: nota e parecer na liberação (D15)
sigtcc/templates/cadastro/tcc/meu_tcc.html  # IC-07: inclui defesa/_resultado_aluno.html
sigtcc/static/js/avaliacao.js             # novo: prévia da imagem e habilitação dos campos
sigtcc/static/fonts/                      # novo: fontes TTF locais dos PDFs (research A9)
sigtcc/static/img/assinatura_demo.png     # novo: assinatura do popular_demo (research A12)
sigtcc/apps/cadastro/
├── menu.py                               # IC-02: + "Minhas bancas"
├── views_tcc.py                          # IC-07: contexto do resultado na aba Meu TCC
└── management/commands/popular_demo.py   # IC-08: avaliações de exemplo (research A12)
```

**Structure Decision**: tudo no app `defesa` (PGCS 2.3), com um módulo de serviço novo para o
domínio da avaliação (research A1). O utilitário de PDF fica no `defesa` porque todos os PDFs do
sistema (agenda, Ata, Folha, declaração) são do Épico 2.

## Ordem de implementação e commits

1. `chore(config)`: `xhtml2pdf` no `requirements.txt` (com `pip freeze` e conferência num Linux
   limpo, research A9); sem mudança no `settings.py`. Em seguida, `feat(feat-08)`: `pdf.py`,
   fontes locais e `test_pdf.py` (código de aplicação, PGCS 5.2; revisão M-01).
2. Fase base: `services_avaliacoes` (estado, cálculo, descartar, voltar a rascunho) e IC-01
   (stub substituído, ordem do descarte, D16, D2, travas públicas), com os testes da spec 007
   ajustados (IC-03).
3. Critérios e Minhas bancas (US1, US2) + IC-02.
4. Formulário Avaliação e assinatura (US3).
5. Parecer, liberação, notificações e ponto de chamada da feat-09 (US4) + IC-05, IC-06.
6. Sigilo e resultado do aluno (US5) + IC-07.
7. `popular_demo` (IC-08), mensagens e validação manual.

Cada fase num commit atômico, com os testes passando (CLAUDE.md).

## Itens de configuração (código de outras specs)

Aprovados pela Q-128 ("pode mexer no que for necessário, relatando"); cada um será relatado no PR.

| IC | Arquivo e spec de origem | O que muda | Por quê |
|---|---|---|---|
| IC-01 | `defesa/services_defesa.py` (007) | `descartar_avaliacoes` delega para `services_avaliacoes`; descarte antes do `delete()` em `acionar_suplente` e `alterar_banca`; `alterar_banca` mantém o rascunho só na troca entre titulares e atualiza a linha de quem continua; `reagendar` chama `voltar_envios_a_rascunho`; `tcc_da_sessao`, `travar_tcc` e `travar_sessao` públicas | Contrato §6 da 007 (Q-125); D16 e Q-135; D2; revisão I-07, M-08; research A11 |
| IC-02 | `cadastro/menu.py` (003) | + item "Minhas bancas" (perfis `docente` e `membro_externo`) | FR-003 |
| IC-03 | `defesa/tests/test_us23_banca.py`, `test_us24_confirmar_reagendar_cancelar.py`, `test_base_defesa.py` (007) | + casos da troca entre titulares (mantém rascunho), da ida a Suplente (descarta), da cópia da assinatura apagada e do reagendamento de sessão Em Andamento (volta a rascunho e limpa o parecer); `TesteDescartarAvaliacoesStub` substituído pelo teste da delegação (o stub deixa de existir) | D16, Q-135, D2, D3; revisão I-08 |
| IC-04 | `requirements.txt` (config) | + `xhtml2pdf` | PGCS 3.7; research A9 |
| IC-05 | `defesa/views_defesa.py` e `sessao.html` (007) | contexto e blocos `avaliacao` e `resultado`; `_sessao_ou_404` vira `sessao_ou_404` | contrato §3 da 007; revisão I-04 |
| IC-06 | `defesa/historico.html` (007) | nota final e parecer no evento "Liberação do Resultado" | D15; RBN-DEF-01.6 |
| IC-07 | `cadastro/views_tcc.py` e `cadastro/tcc/meu_tcc.html` (005) | seção "Resultado da defesa" | FR-033 |
| IC-08 | `cadastro/management/commands/popular_demo.py` | avaliações de exemplo, só por serviços, com a assinatura estática do repositório | research A12; revisão I-15 |
| IC-09 | `defesa/permissoes_defesa.py`, `defesa/urls.py`, `defesa/mensagens.py` (007) | acréscimos: permissões, 7 rotas, textos das US-25 a US-27 e MA-01 a MA-12; nada removido | revisão M-05 |
| IC-10 | `specs/007-agendamento-banca/spec.md` (007, já mesclada) | FR-011 (D16 e Q-135) e FR-019 (D2) e uma nota em Clarifications; feito no `/speckit-plan` desta feature | CLAUDE.md: mudança depois do merge começa pela spec; revisão I-09 |
| IC-11 | `specs/007-agendamento-banca/contracts/servicos-defesa.md` (007) | §6 entregue, ordem do descarte, travas públicas; feito no `/speckit-plan` | revisão I-09 |

## Documentos a ajustar (PDFs sob demanda, sem armazenamento externo)

Ajustes de texto; nenhum muda regra de negócio da feat-08. A matriz, as US e o dicionário são dos
donos no Drive; o PGCS é ajustado por Célio Benjamim no Drive e depois copiado para `docs/fonte/`.

| Documento | Trecho | Ajuste | Índice |
|---|---|---|---|
| Matriz 17/10, RBN-DEF-06.4, 07.1, 07.2 | "são geradas já assinadas", "gerado automaticamente após a liberação" | Ler como "disponível a partir da liberação, gerado a cada download com os dados congelados" | Q-132 (PO) |
| US-27, passo 12 e pós-condições | "dispara a geração da Ata Final e da Folha" | A liberação dispara só o envio das declarações | Q-132 |
| US-28, passo 6, pós-condições, cenário 8 | "armazena os PDFs", "arquivada no SIGTCC", "arquivadas" | Gerados sob demanda | Q-132 |
| Dicionário 3.6.1 | `def_ata_final_path`, `def_folha_aprovacao_path` | Sem uso; descrever como reservadas ou remover numa versão do modelo | Q-133 (Maria Luiza) |
| PGCS 3.4, 3.5 (itens 8 e 9), 3.7, 9.1, 9.5 | armazenamento externo privado, PDFs "gerados uma única vez" e "gravados" | Sem armazenamento externo; PDFs sob demanda; xhtml2pdf presente; assinaturas no disco efêmero (risco aceito) | Q-134 (Célio) |
| Diagrama 28 (PlantUML v2) | `gerarAtaFinal`/`gerarFolhaAprovacao` na liberação e `registrarResultado(..., paths)` | Geração no passo 4 (`baixarDocumento`) | Q-134 |
| `docs/arquitetura/Componentes_SIGTCC.drawio` e `Implantacao_SIGTCC.drawio`, e os PNG em `docs/arquitetura/imagens/` | "externo planejado para o TP3" | "PDFs gerados sob demanda; assinaturas no disco do serviço" | Q-134 |
| PGCS 2.4, legenda da Figura 2 | "com o Brevo e o armazenamento" | "com o Brevo" | Q-134 |
| `CHANGELOG.md`, planejado para a v0.3.0 | "Armazenamento externo privado para assinaturas e PDFs" | Retirar; registrar a decisão no CHANGELOG da v0.3.0 | Q-134 |

## Pendências desta feature

Índice central: [docs/questoes-a-rever.md](../../docs/questoes-a-rever.md).

| Pendência | Destino | Índice |
|---|---|---|
| Divergência DV-01 (notificações da liberação além da Secretaria) | Profa. Diana (PO) | Q-131 |
| Textos da matriz e das US-27/US-28 que pressupõem PDFs gravados | Profa. Diana (PO) | Q-132 |
| Colunas `def_ata_final_path` e `def_folha_aprovacao_path` sem uso | Maria Luiza Guimarães (modelo lógico) | Q-133 |
| PGCS, diagramas e CHANGELOG sem armazenamento externo | Célio Benjamim (config) | Q-134 |
| Ideias futuras: assinatura no navegador, histórico de Coordenadores, assinatura no banco | PO | S-04, S-05, S-06 |
| Regra do parecer (D3 revista) e ida a Suplente na alteração da banca | Célio Benjamim | Q-135 (respondida) |

## Complexity Tracking

Nenhuma violação da constituição.

| Escolha | Por quê | Alternativa mais simples rejeitada |
|---|---|---|
| Módulo novo `services_avaliacoes.py` em vez de ampliar `services_defesa.py` | Domínio próprio, consumido pela spec 007 e pela feat-09; o arquivo da 007 já é grande | Tudo em `services_defesa.py`: mistura agenda e avaliação |
| PDF sob demanda, sem gravar | Decisão de configuração: não armazenar arquivos; resolve a contradição entre o diagrama 28 e a D9 (falha no PDF não desfaz a liberação) | PDFs gravados na liberação com armazenamento externo (PGCS 1.2) |
| Funções públicas de trava em `services_defesa.py` | Mesma ordem de trava nas duas features sem importar função privada | Duplicar a lógica de trava na feat-08 |
