# Contrato: telas, rotas e navegação (feature 006)

**Feature**: [../spec.md](../spec.md) | **Plano**: [../plan.md](../plan.md) | **Pesquisa**: [../research.md](../research.md)

Todas as rotas ficam no app `cadastro` (`app_name = "cadastro"`), em `sigtcc/apps/cadastro/urls.py`
(IC-10). São 29 rotas novas, mais mudanças em rotas já existentes (seção 6). Toda rota exige login
(`perfil_requerido`); sem sessão, ela leva ao login com `next`, preservando `?secao=` (research R12).
Para cada tela, a coluna "Chega por" diz o caminho na navegação (FR-040 a FR-045, FR-052; SC-005):
nenhuma tela depende de endereço digitado.

Convenções:
- **404 sem vínculo**: o usuário tem o perfil, mas não tem vínculo com o objeto. A resposta não
  revela que o objeto existe, como no padrão `vinculo_na_turma`.
- **403 (M-02)**: o usuário não tem o perfil.
- **POST com CSRF**: todo POST usa CSRF. Nenhum GET grava (research R4).
- **Objeto aninhado na URL** (research R10): `coo_id`, `sol_id` e `enc_id` são sempre buscados
  filtrando pelo TCC do contexto (`coo_tcc=tcc`, `sol_tcc=tcc` com o `sol_tipo` da rota,
  `enc_tcc=tcc`); um ID de outro TCC dá 404. As atas do TCC de origem, listadas no TCC 2 só para
  consulta, nunca são editadas nem comentadas pela rota do TCC 2. Cada rota com ID tem um teste de
  troca de ID em `test_permissoes_orientacao.py`.
- **Turma do TCC conferida depois da trava**: nas gravações, se `tcc.tcc_tur_id` não for a turma
  travada (aluno transferido no meio tempo), 404 (research R2).
- **Turma arquivada**: as rotas do Aluno e do Docente redirecionam à própria tela (seção do Meu TCC
  ou `orientacoes`) com a MT-25, sem passar pela tela da turma (research R2).

## 1. Aluno: aba "Meu TCC" (prefixo `turmas/<tur_id>/meu-tcc/`)

Chega por: item "Turmas" do Aluno → turma → aba "Meu TCC" (spec 005, FR-031). As seções
Orientação, Atas de orientação e Publicação do artigo ficam dentro dessa aba (IC-09); `?secao=`
abre a aba já na seção.

| # | Rota | Nome | Métodos | Tela / ação | Volta | FR |
|---|---|---|---|---|---|---|
| 1 | `orientacao/pedido/` | `enviar_pedido_orientacao` | POST | Indicar orientador ou Trocar de orientador | Meu TCC `?secao=orientacao` | FR-001 a FR-005 |
| 2 | `orientacao/pedido/cancelar/` | `cancelar_pedido_orientacao` | POST | Cancelar Pedido | idem | FR-004 |
| 3 | `coorientadores/novo/` | `registrar_coorientador` | GET, POST | Janela "Registrar coorientador" | "Cancelar"/"Salvar" → seção Orientação | FR-028 |
| 4 | `coorientadores/<coo_id>/substituir/` | `substituir_coorientador` | GET, POST | Mesma janela (US-45 D) | idem | FR-030 |
| 5 | `coorientadores/<coo_id>/remover/` | `remover_coorientador` | GET (confirmação MO-14), POST | Remover coorientador | idem | FR-030 |
| 6 | `convites/<sol_id>/remover/` | `remover_convite_coorientacao` | GET (MO-14), POST | Remover convite pendente | idem | FR-029 |
| 7 | `atas/` | `minhas_atas` | GET | Lista de atas (+ atas do TCC 1, Q6) | "Voltar" → seção Atas | FR-023, FR-042 |
| 8 | `atas/nova/` | `registrar_ata_aluno` | GET, POST | Janela "Registrar ata de orientação" | "Cancelar"/"Salvar" → seção Atas | FR-021, FR-022 |
| 9 | `atas/<enc_id>/editar/` | `editar_ata_aluno` | GET, POST | Edição da ata | → lista de atas | FR-024 |
| 10 | `publicacao/` | `salvar_publicacao_aluno` | POST | "Salvar publicação" | Meu TCC `?secao=publicacao` | FR-034, FR-036 |

Acesso: só o próprio Aluno da turma (`services_tcc.turma_do_aluno`); o TCC do contexto é o dele
nessa turma (`tcc_do_aluno`), e as rotas 4, 5, 6 e 9 buscam o objeto por esse TCC. As gravações
exigem `pode_alterar_no_tcc` (FR-007); fora dessas condições, o botão não aparece e o POST é
recusado (MT-25 com a turma arquivada; nos outros casos, M-02).

## 2. Docente: tela "Orientações" (prefixo `orientacoes/`)

Chega por: item de menu **"Orientações"**, para todo Docente (IC-01; FR-040; Q11). Os links de
e-mail e de notificação de pedido e de convite também levam a ela.

| # | Rota | Nome | Métodos | Tela / ação | Volta | FR |
|---|---|---|---|---|---|---|
| 11 | `` (raiz `orientacoes/`) | `orientacoes` | GET | "Pedidos de orientação", "Convites de coorientação" e a tela de orientandos (seções vazias: MO-24) | tela de topo | FR-009, FR-014, FR-031, FR-040 |
| 12 | `pedidos/<sol_id>/` | `pedido_orientacao` | GET | Mesma tela, com o pedido destacado ou o aviso de estado (FR-012; `?acao=` só destaca) | — | FR-012 |
| 13 | `convites/<sol_id>/` | `convite_coorientacao` | GET | Idem para o convite (FR-033; Q14) | — | FR-033 |
| 14 | `solicitacoes/<sol_id>/aceitar/` | `aceitar_solicitacao` | POST | Aceitar pedido ou convite | → `orientacoes` (MO-15 ou "Convite aceito") | FR-010, FR-032 |
| 15 | `solicitacoes/<sol_id>/recusar/` | `recusar_solicitacao` | POST | Recusar | → `orientacoes` ("Pedido recusado"/"Convite recusado") | FR-011, FR-032 |
| 16 | `solicitacoes/<sol_id>/proposta/` | `ver_proposta` | GET | Janela "Ver proposta" (Resumo por `pode_ver_resumo`, IC-05) | "Fechar" → `orientacoes` | FR-013 |
| 17 | `tcc/<tcc_id>/atas/` | `atas_orientando` | GET | Lista de atas (Orientador e Coorientador com vínculo ativo) | "Voltar" → `orientacoes` | FR-023, FR-043 |
| 18 | `tcc/<tcc_id>/atas/nova/` | `registrar_ata_docente` | GET, POST | "Registrar ata de orientação" | → `orientacoes` | FR-022 |
| 19 | `tcc/<tcc_id>/atas/<enc_id>/editar/` | `editar_ata_docente` | GET, POST | Edição | → `atas_orientando` | FR-024 |
| 20 | `tcc/<tcc_id>/atas/<enc_id>/comentar/` | `comentar_ata` | GET, POST | Campo de comentário abaixo da ata | → `atas_orientando` | FR-024 |
| 21 | `tcc/<tcc_id>/historico/` | `historico_orientando` | GET | Histórico do Status (só o Orientador atual; template da spec 005, IC-06) | "Fechar" → `orientacoes` | FR-015, FR-043 |
| 22 | `tcc/<tcc_id>/publicacao/` | `publicacao_orientando` | GET, POST | "Publicação do artigo" do orientando (só Artigo Científico) | "Voltar" → `orientacoes` | FR-035 |
| 23 | `tcc/<tcc_id>/apto/` | `indicar_apto` | GET (confirmação), POST | Apto para Defesa | "Cancelar"/"Confirmar" → `orientacoes` | FR-026, FR-027 |
| 24 | `tcc/<tcc_id>/correcoes-conferidas/` | `correcoes_conferidas` | GET (MO-13), POST | Correções Conferidas | → `orientacoes` | FR-016 |

Acesso: `perfil_requerido("docente")`.
- Nas rotas 12 e 13, a solicitação é buscada com o `sol_tipo` da rota. Inexistente, de outro tipo
  ou de outro docente: a mesma resposta, o aviso "não está disponível para o seu usuário", sem
  revelar existência nem estado (research R4).
- Nas rotas 14 a 16, só o docente indicado ou convidado age; nos outros casos, 404.
- Nas rotas 17 a 24, o acesso é pelos predicados de `papeis_no_tcc` (research R10):
  `e_orientador_atual` nas rotas 21 a 24; `e_orientador_atual` ou `e_coorientador_ativo` nas
  rotas 17 a 20; sem vínculo, 404. O Professor da Disciplina que é orientador automático entra como
  Orientador.
- Linha de turma arquivada (FR-014, "só com acesso às atas"): as rotas 21 a 24 dão 404, inclusive
  no GET; a rota 17 abre só para leitura; o GET das rotas 18 a 20 volta à 17 com a MT-25, e o POST
  é recusado com a MT-25.
- As gravações conferem `pode_alterar_no_tcc` (FR-046).

## 3. Professor da Disciplina: painel do aluno

Chega por: "Turmas" (ou "Turmas arquivadas") → turma → aba "Alunos" → bloco do aluno (IC-02;
FR-044).

| # | Rota | Nome | Métodos | Tela | Volta | FR |
|---|---|---|---|---|---|---|
| 25 | `turmas/<tur_id>/alunos/<alu_id>/` | `painel_aluno` | GET | Painel: seções, botões de ação e link do histórico | "Fechar" → `turma` | FR-017 a FR-020, FR-049 |
| 26 | `turmas/<tur_id>/alunos/<alu_id>/atas/` | `atas_painel` | GET | Atas só para leitura | "Voltar" → painel | FR-023, FR-044 |

Acesso: `turma_para(..., CONSULTAR)`, `turma.tur_doc_id == usuario`, `vinculo_na_turma(turma,
alu_id)` e `tcc_do_aluno(turma, aluno)` (research R10). A Secretaria, outro Docente e o Aluno
recebem 403 (M-02; FR-020); um `alu_id` sem vínculo com a turma dá 404. A rota 26 lista só as atas
desse TCC e as do TCC de origem. Turma arquivada: o painel abre sem botões de ação, inclusive sem
"Resetar primeiro acesso" (US-41 D; FR-019).

## 4. Coordenador de Curso: aproveitamento de artigos

Chega por: menu, seção **"Gestão"**, item **"Aproveitamento de artigos"**, só para o Coordenador
(IC-01; FR-041).

| # | Rota | Nome | Métodos | Tela / ação | Volta | FR |
|---|---|---|---|---|---|---|
| 27 | `artigos/` | `aproveitamento_artigos` | GET (`?curso=`) | Tabela com filtro Curso | tela de topo | FR-037 |
| 28 | `artigos/<tcc_id>/homologar/` | `homologar_artigo` | POST | Homologar | → `artigos/?curso=` ("Aproveitamento homologado") | FR-038 |
| 29 | `artigos/<tcc_id>/recusar/` | `recusar_artigo` | POST | Recusar | idem ("Aproveitamento recusado") | FR-038 |

Acesso: `perfil_requerido("coordenador")`. Homologar e Recusar travam a turma sem exigir que esteja
ativa (D11; FR-046) e valem só para artigos do curso
coordenado, em Artigo Científico, com Status Aceito ou Publicado e de TCC não copiado; senão, 404
(research R9). Depois da liberação, só a recusa de artigo Homologado é bloqueada (MO-21; US-20 E3).
O `?curso=` é validado contra `Cursos` antes de ir para o redirecionamento; o link "abrir" sai com
`rel="noopener noreferrer"`.

## 5. Destino das notificações (FR-052)

| Notificação | Destinatário | `not_link_tela` |
|---|---|---|
| MO-01, MO-16 | docente indicado | `pedido_orientacao` (rota 12) |
| MO-07 | docente convidado | `convite_coorientacao` (rota 13) |
| MO-02, MO-03, MO-06 (aluno), MO-10 (aluno), MO-11 | Aluno | `meu_tcc` `?secao=orientacao` |
| MO-04 | Professor da Disciplina | `painel_aluno` (rota 25) |
| MO-05, MO-06 (docente), MO-08, MO-09, MO-10 (orientador), MO-18 | docentes | `orientacoes` (rota 11) |
| MO-26 | docente do pedido ou convite cancelado pelo arquivamento | `pedido_orientacao` ou `convite_coorientacao` da solicitação (rota 12 ou 13), gravada com o instante do arquivamento (dedução do motivo, research R3) |
| MT-31 (encerramento) e MT-22 (transferência), da spec 004 | docentes | sem mudança (Q18); a MO-12 e a MO-17 são só textos do link do pedido ou convite cancelado |

## 6. Rotas já existentes que mudam (itens de configuração)

| Rota (nome) | Spec | Mudança | IC |
|---|---|---|---|
| `turmas/<tur_id>/` (`turma`) | 004 | Aba "Alunos" em blocos; o bloco abre o painel (Professor) ou tem "Transferir aluno" (Secretaria) | IC-02 |
| `aluno_editar`, `aluno_encerrar`, `aluno_excluir`, `aluno_transferir` | 004 | Aceitam `?volta=painel` (valor fechado, research R5), também nos redirecionamentos de erro | IC-03 |
| `historico_status` (Professor) e `historico_status_aluno` | 005 | "Fechar" volta ao painel (Professor) ou à aba Meu TCC (Aluno) | IC-06 |
| `aluno_versao_final` | 005 | `?volta=painel` | IC-07 |
| `meu_tcc` | 005 | 3 seções novas e `?secao=` | IC-09 |
| `alunos/<alu_id>/` (`aluno`) | 003 | Deixa de mostrar a tela provisória e redireciona ao `painel_aluno` (turma mais recente do aluno em que quem abre é o Professor: não arquivada primeiro, depois `tur_ano`, `tur_semestre` e `tur_id` decrescentes; sem turma, 403) | IC-08 |
| `alunos/<alu_id>/resetar-primeiro-acesso/` | 003 | Depois do reset e no "Cancelar", redireciona para `cadastro:aluno`, que resolve o painel no servidor (nenhum `tur_id` vindo do usuário) | IC-08 |
