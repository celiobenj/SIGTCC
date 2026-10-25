# Research: Orientação, Atas e Publicações (feature 006)

**Feature**: [spec.md](spec.md) | **Plano**: [plan.md](plan.md)

A spec não deixou nenhum `[NEEDS CLARIFICATION]`: Q1 a Q18 estão em Clarifications. As decisões
abaixo são de projeto, ou seja, de como implementar. Cada uma traz a decisão, a justificativa e as
alternativas consideradas.

**Revisão do `arquiteto-django` (2026-10-24)**: os 34 pontos da revisão foram tratados. Os que
mudavam comportamento foram decididos por Célio Benjamim (Clarifications Q15 a Q18). Os de
implementação foram decididos aqui, por delegação dele. As decisões citam o ponto da revisão entre
colchetes, por exemplo [A1]; os pontos resolvidos fora deste arquivo (A8, A16, A18, A21, A24, A29,
A31, A34) estão na spec, no data-model, no contrato da spec 005, no quickstart e no plano. Os 12
problemas da reconferência aparecem como [N1] a [N12].

## R1. Divisão em módulos e reaproveitamento

- **Decisão**: três módulos de serviço novos:
  - `services_orientacao.py`: solicitações, orientações, coorientações, tela de orientandos, Apto,
    Correções Conferidas, motivo do cancelamento e histórico de orientação;
  - `services_atas.py`: atas e comentários;
  - `services_artigos.py`: publicação e aproveitamento.

  Para cada um há `forms_*` e `views_*` com o mesmo nome, mais `views_painel.py` para o painel do
  aluno, que só monta o contexto chamando os services das specs 003 a 006.

  Reaproveitados sem cópia [A27]:
  - `forms_contas.validar_nome_completo` (nome do coorientador externo);
  - `mensagens.LINK_HTTPS_500` e a mesma checagem de `forms_tcc.py` e `forms_entregas.py` (Link ou
    DOI) [A9];
  - `STATUS_SESSAO_ATIVA`, `STATUS_SOLICITACAO_PENDENTE` e `STATUS_ENVIO_AVALIAVEL` (constantes já
    existentes);
  - `services_tcc.palavras_chave_do` ("Ver proposta");
  - `services.travar_email` (coorientador externo, R17);
  - `permissoes.curso_id_do_usuario` (curso do Coordenador, R9) [A25].
- **Justificativa**: cada módulo corresponde a um domínio de dados com uma regra de acesso
  própria. É o mesmo padrão já aceito para `services_turmas.py`, `services_tcc.py` e
  `services_entregas.py`.
- **Alternativas**: um módulo só (grande demais, regras misturadas); regras em `permissoes.py`
  (é da spec 003 e trata de perfil, não de vínculo com o TCC).

## R2. Ordem de trava e concorrência

- **Decisão**: toda gravação roda em `transaction.atomic()` e trava sempre na mesma ordem:
  1. turma (`travar_turma_ativa`, spec 004);
  2. aluno: a linha de `Alunos` com `select_for_update`, **obrigatória em toda gravação da 006**
     [A14];
  3. TCC (`select_for_update`);
  4. conta do docente (`travar_e_conferir_ativo`, spec 002), quando a ação cria pedido, convite,
     orientação ou coorientação;
  5. a linha de `Solicitacoes_Orientacao`, de `Artigos` ou de `Entregas_Marcos`, quando existe.

  **Coordenador** [N2]: Homologar e Recusar travam a turma com `select_for_update` **sem exigir que
  esteja ativa** (D11 e FR-046: as decisões do Coordenador não seguem a regra de turma arquivada);
  todas as outras gravações usam `travar_turma_ativa`.

  Regras complementares:
  - **Turma do TCC conferida depois da trava** [A14]: a view lê `sol → TCC → turma` sem trava,
    trava na ordem acima e confere `tcc.tcc_tur_id == turma.pk`. Se divergir (o aluno foi
    transferido nesse meio tempo), a ação responde 404, como um objeto que não pertence à tela.
  - **Reconferência**: depois de travar, o serviço relê o estado e confere de novo as condições
    (FR-012, FR-027). Exemplos: um pedido que já não está pendente mostra o estado atual; o Apto com
    a condição mudada é recusado com a MO-20; o aceite de uma troca reconfere que não há sessão de
    defesa em `STATUS_SESSAO_ATIVA` [A20].
  - **Índices únicos**: as gravações que podem violar `uq_orientacoes_uma_ativa_por_tcc`,
    `uq_solicitacoes_orientacao_pedido_pendente` ou `uq_coorientacoes_*` rodam num savepoint
    (`transaction.atomic()` interno), e o `IntegrityError` vira o mesmo tratamento do duplo clique,
    como em `cadastrar_entrega` (spec 005).
  - **Convite pendente** [A19]: não há índice único para convite; quem serializa dois convites ao
    mesmo docente no mesmo TCC é a trava do TCC (passo 3), seguida da conferência.
  - **Turma arquivada nas rotas novas** [A11]: as views do Aluno e do Docente capturam
    `TurmaArquivada` e redirecionam à própria tela de origem (`meu_tcc?secao=…` ou `orientacoes`)
    com a MT-25, como `views_tcc.py:136-138`. Não usam `trata_turma_arquivada`, que leva à tela da
    turma, fechada ao Aluno e ao Orientador.
- **Justificativa**: é a ordem usada pela maior parte das specs 004 e 005 (turma → aluno → TCC),
  o que evita deadlock entre as features. `atualizar_status_tcc` exige o TCC já travado por quem
  chama. **Exceção encontrada na reconferência** [N1]: `services_entregas.enviar_entrega` (spec 005)
  trava a entrega antes do TCC e não trava a turma, o que pode dar deadlock com "Correções
  Conferidas" (R15) e, já hoje, com Homologar e Devolver da Versão Final. O IC-14 faz
  `enviar_entrega` travar turma → aluno → TCC → entrega (achando a entrega primeiro sem trava, para
  saber a turma, e relendo-a travada). A turma é travada com `Turmas.objects.select_for_update()`,
  **sem exigir que esteja ativa**: a decisão continua com `envio_liberado` (404 com a turma
  arquivada), porque `views_entregas.entrega_enviar` não trata `TurmaArquivada` e daria erro 500. `encerrar_participacao`, `excluir_aluno` e `transferir` não
  travam `Alunos`, mas a trava da turma vem antes e serializa tudo, então ficam como estão.
- **Alternativas**: trava só da solicitação (não protege o "um orientador ativo" contra uma troca
  concorrente); confiar só nos índices únicos (sem mensagem ao usuário).

## R3. Instante do evento e motivo do cancelamento (FR-050; Q7, Q17)

- **Decisão**: `_registrar_historico`, `atualizar_status_tcc`, `criar_tcc_com_historico` e
  `_criar_orientacao_automatica` ganham o parâmetro opcional `agora=None`; sem ele, continuam usando
  `timezone.now()`. Os eventos que cancelam solicitações calculam `agora = timezone.now()` **uma
  vez** e passam esse mesmo objeto ao histórico, ao vínculo e ao `sol_data_resposta`:
  - `encerrar_participacao` (004);
  - `transferir` (004);
  - `_copiar_tcc_aprovado` (004);
  - `arquivar_turma` (004; IC-12, R21);
  - aceite de troca (006);
  - o futuro agendamento (US-24).

  `services_orientacao.motivo_do_cancelamento(sol)` devolve um valor do enum Python
  `MotivoCancelamento` (não é tabela nem coluna): `AGENDAMENTO`, `ENCERRAMENTO`,
  `DOCENTE_VIROU_ORIENTADOR`, `COPIA_TCC_2`, `TURMA_ARQUIVADA` ou `ALUNO`. Com `X =
  sol.sol_data_resposta`, as consultas são fixas [A12]:
  1. só no tipo Troca de Orientação: `HistoricoDefesas(hdf_def__def_tcc=sol.sol_tcc,
     hdf_evento='Agendamento', hdf_data_hora=X)`;
  2. `HistoricoStatusTCC(hst_tcc=sol.sol_tcc, hst_gatilho=ENCERRAMENTO_DA_PARTICIPACAO,
     hst_data_hora=X)`;
  3. só no tipo Coorientação: `Orientacoes(ori_tcc=sol.sol_tcc, ori_doc=sol.sol_doc,
     ori_data_inicio=X)`;
  4. `HistoricoStatusTCC(hst_tcc__tcc_alu=sol.sol_tcc.tcc_alu, hst_gatilho=TRANSFERENCIA_PARA_TCC_2,
     hst_data_hora=X)` com `hst_tcc` diferente de `sol.sol_tcc`;
  5. `Notificacoes(not_usu=sol.sol_doc, not_link_tela=<link da solicitação>, not_data_hora=X)`:
     `TURMA_ARQUIVADA` (MO-26). `Turmas` não guarda a data do arquivamento, e por isso o
     arquivamento grava a notificação MO-26 com o mesmo `agora` e com o link da própria
     solicitação (rota 12 ou 13), dentro da transação; `services.notificar` ganha `agora=None`
     opcional (IC-12) [N3]. O link sai sempre de um helper único,
     `services_orientacao.link_da_solicitacao(sol)` (rota 12 para pedidos, 13 para convites), usado
     pelas notificações MO-01, MO-07, MO-16 e MO-26 e por esta consulta; `test_arquivamento_pendentes.py`
     confere `not_link_tela == link_da_solicitacao(sol)` além do motivo. A notificação MO-01 ou MO-07 da mesma solicitação tem o mesmo link, mas
     a data e a hora do envio, nunca iguais às do cancelamento. Notificações não são apagadas pelo
     sistema (US-38);
  6. nos outros casos: `ALUNO`. O pedido que o aluno cancelou antes do arquivamento continua
     "cancelado pelo aluno", como mandam as US-18 E3 e US-36 E3.

  Contraexemplo que as consultas fixas resolvem: na cópia para uma turma de TCC 2 com orientador
  automático P, um convite pendente a P no TCC 1 recebe o mesmo `agora` da orientação automática do
  TCC 2. Como a consulta 3 exige `ori_tcc = sol_tcc`, o motivo sai `COPIA_TCC_2`, e não
  `DOCENTE_VIROU_ORIENTADOR`.
- **Precisão** [A13]: a coluna é `timestamp` com microssegundos e `USE_TZ=False`. A igualdade é
  exata porque o mesmo objeto Python é gravado nas linhas. Fica proibido (contrato §5):
  - truncar o instante ou passar por `replace(microsecond=0)`;
  - usar `Now()` do banco, `auto_now` ou `auto_now_add` nesses campos;
  - chamar `timezone.now()` de novo dentro do mesmo evento.
- **Testes** [A13]: `test_motivo_cancelamento.py` usa o **relógio real** (sem congelar o tempo, que
  faria todos os `timezone.now()` iguais e esconderia a falta do IC-04). Para cada motivo, um
  teste confere a igualdade gravada, e um teste negativo confere que o aluno cancela e, depois, o
  evento acontece: o motivo continua `ALUNO`. Os registros da base de desenvolvimento gravados
  antes do IC-04 aparecem como "cancelado pelo aluno"; isso é aceito (base sem produção).
- **Justificativa**: o usuário não quer coluna nova (Q7). Com o mesmo objeto `datetime` gravado nas
  duas linhas, a igualdade é exata, sem janela de tolerância. O caso que a dedução por ordem errava
  fica certo: o aluno cancela a troca e depois a defesa é agendada; os instantes diferem e o motivo
  é `ALUNO`.
- **Alternativas**: coluna de motivo (recusada na Q7); janela de tolerância de segundos (falha com
  ações próximas); deduzir pelo estado atual do TCC (falha no exemplo acima).

## R4. Página do link de pedido ou convite (FR-012, FR-033; D1, Q14)

- **Decisão**: as rotas `orientacoes/pedidos/<sol_id>/` e `orientacoes/convites/<sol_id>/`
  renderizam a própria tela Orientações (mesmo template e mesma view base), com o item destacado
  ou com um aviso de estado no topo: E2 a E5, MO-12, MO-17, MO-18, MO-26 ou a decisão com data e
  hora. A ordem das verificações é fixa [A6]:
  1. sem sessão: login com `next`; sem o perfil Docente: 403 (M-02), por
     `perfil_requerido("docente")`;
  2. a solicitação é buscada com o `sol_tipo` da rota (pedidos: Orientação ou Troca de Orientação;
     convites: Coorientação). Se não existir, for de outro tipo ou de outro docente, a resposta é
     **a mesma**: o aviso "não está disponível para o seu usuário" (E5), sem revelar se o
     `sol_id` existe nem o seu estado;
  3. só para o docente indicado ou convidado, o estado: pendente (destacado), decidido (data e
     hora) ou cancelado (motivo do R3).

  Os botões "Aceitar" e "Recusar" do e-mail (Q14) apontam para essas mesmas rotas, com
  `?acao=aceitar` ou `?acao=recusar`, que só **destacam** o botão; a gravação é sempre um POST na
  tela, com CSRF.
- **Justificativa**: uma tela só, sem página intermediária, como pedem os E1 ("abre a tela
  Orientações com o pedido"). O GET nunca grava, e não há link mágico.
- **Alternativas**: página própria de estado (mais uma tela sem caminho de volta); link assinado de
  uso único (opção C da Q14, recusada).

## R5. Volta das telas de ação ao painel (FR-044; IC-03, IC-07, IC-08)

- **Decisão**: as views de ação das specs 004 e 005 aceitam `?volta=painel` (POST: campo oculto
  `volta`). Só o valor `painel` é reconhecido; qualquer outro é ignorado. A URL de destino é montada
  no servidor com `reverse("cadastro:painel_aluno", args=[turma.pk, aluno.pk])`, com a turma e o
  aluno da própria rota, nunca a partir de texto do usuário. Excluir e Transferir confirmados
  voltam sempre à aba "Alunos".
  - **Caminhos de erro** [A33]: com `volta=painel`, os redirecionamentos de erro das views de ação
    (MT-19, `ALUNO_TEM_PROPOSTA` e a captura de `TurmaArquivada`) também voltam ao painel, com a
    mesma mensagem. Sem o parâmetro, continuam voltando à turma.
  - **Reset de primeiro acesso** (spec 003; IC-08) [A5]: a rota não tem `tur_id`. Depois do reset
    e no "Cancelar", ela redireciona para `cadastro:aluno`, que pelo IC-08 já resolve no servidor o
    painel da turma mais recente do aluno em que quem abre é o Professor da Disciplina. Nenhum
    `tur_id` vem do usuário. "Mais recente" [N12]: entre as turmas com `tur_doc` = quem abre e com
    vínculo do aluno, primeiro as não arquivadas, depois `tur_ano`, `tur_semestre` e `tur_id`
    decrescentes.
  - **Filtro Curso do Coordenador** [A5]: o `?curso=` só é reaproveitado no redirecionamento
    depois de validado contra `Cursos`; um valor inválido vira o curso do Coordenador.
- **Justificativa**: reaproveita as telas já testadas, sem redirecionamento aberto (segurança,
  princípio VII), e sem o parâmetro mantém o comportamento atual.
- **Alternativas**: `next=<url>` com `url_has_allowed_host_and_scheme` (aceita qualquer caminho
  interno, mais superfície de erro); duplicar as telas no painel.

## R6. TCC copiado para o TCC 2 (FR-007, FR-023, FR-051; Q6)

- **Decisão**: `services_orientacao.tcc_copiado(tcc)` é verdadeiro quando:
  - `tcc.tcc_status == 'Aprovado para TCC 2'`;
  - e existe outro TCC do mesmo aluno criado depois, isto é, com `Historico_Status_TCC` de gatilho
    "Transferência para TCC 2" posterior.

  `tcc_de_origem(tcc2)` devolve esse TCC 1, para a lista de atas do TCC 2 mostrar as atas do
  TCC 1 só para consulta. A cópia da publicação **com o aproveitamento** já é feita pela spec 004
  (`_copiar_tcc_aprovado`) e continua. O IC-04 acrescenta:
  - a trava do TCC 1 (`select_for_update`, depois do aluno), que hoje não existe [A14];
  - o cancelamento das solicitações pendentes do TCC 1, com o mesmo `agora` e o aviso MO-18.
- **Justificativa**: deriva só de dados que já existem (Q-91 respondida, linha nova), sem coluna de
  ligação entre os TCCs.
- **Alternativas**: coluna `tcc_origem_id` (fora do modelo); procurar pelo título igual (frágil).

## R7. "Resultado liberado" por linha de TCC (FR-038; US-20 E3; Q16)

- **Decisão**: `services_artigos.resultado_liberado(tcc)` = existe `Historico_Status_TCC` **desse**
  TCC com o gatilho `LIBERACAO_DO_RESULTADO`. Quando o módulo de Defesa existir, o resultado
  continua o mesmo, porque a US-27 dispara esse gatilho pelo `atualizar_status_tcc`. É usado só
  para a US-20 E3: depois da liberação, "Recusar" fica indisponível no artigo Homologado.
- **Justificativa**: no TCC 2 (linha nova), a liberação do TCC 1 não conta.
- **Alternativas**: ler `Defesas.def_data_liberacao_resultado` (a tabela existe, mas ainda não é
  preenchida por nenhuma feature).

## R8. Ciclo do aproveitamento e etiqueta (FR-034, FR-036 a FR-038; D10, Q16)

- **Decisão**: `services_artigos.salvar_publicacao(...)` trava turma → aluno → TCC → `Artigos`
  [A15] e:
  - a primeira vez que o Status fica Aceito ou Publicado e `art_homologacao` está nulo, ele passa a
    "Em Análise";
  - se Qualis, Status ou Link mudam num artigo já analisado ("Homologado" ou "Recusado"), ele volta
    a "Em Análise" **antes ou depois da liberação** (RBN-CAD-12.3; dicionário 3.5.7; Q16), e
    `art_homologado_por` e `art_data_homologacao` ficam com a última decisão até a próxima;
  - a decisão anterior fica no log (D10).

  A etiqueta (`etiqueta_aproveitamento(artigo)`) mostra a MO-22 quando o Status não é Aceito nem
  Publicado e o aproveitamento é nulo ou "Em Análise"; nos outros casos, mostra o valor de
  `art_homologacao`. O link "abrir" do `art_link_doi` sai com `target="_blank"` e
  `rel="noopener noreferrer"` [A9].
- **Justificativa**: segue a RBN-CAD-12.3, as US-46 C e US-20 D e o dicionário 3.5.7 sem limite de
  tempo. A nota já liberada não muda porque a US-27 lê a homologação no momento da liberação
  (RBN-DEF-06.4; contrato §4).
- **Alternativas**: apagar o autor da decisão anterior ao voltar a "Em Análise" (perde a
  responsabilização pedida pelo RAN-CAD-12 NFR); congelar depois da liberação (a Q8 antiga,
  substituída pela Q16).

## R9. Tela "Aproveitamento de artigos" e curso do Coordenador (FR-037, FR-038; D11)

- **Decisão**:
  - **Consulta**: artigos com Status Aceito ou Publicado, `tcc_modalidade` = Artigo Científico, e
    só do TCC atual do aluno, excluindo os TCCs para os quais `tcc_copiado` é verdadeiro.
  - **Filtro Curso**: os 3 cursos e Todos, pelo `tcc_tur.tur_cur`. O valor inicial é o curso do
    Coordenador, por `permissoes.curso_id_do_usuario` [A25].
  - **Homologar e Recusar** (`homologar_artigo`, `recusar_artigo` em `services_artigos`) [A3, A15]:
    travam turma → aluno → TCC → `Artigos` e, só depois, conferem; qualquer falha devolve 404 (sem
    revelar o artigo), exceto a do último item:
    - o artigo existe e é do curso que o Coordenador coordena;
    - a modalidade do TCC é Artigo Científico (D10);
    - o Status é Aceito ou Publicado;
    - o TCC não está copiado para o TCC 2 (`tcc_copiado`);
    - na recusa de artigo Homologado, o resultado ainda não foi liberado (R7); senão, MO-21.
  - **Log**: cada decisão grava `registrar_evento(EventoArtigo.APROVEITAMENTO_HOMOLOGADO |
    APROVEITAMENTO_RECUSADO, conta=<aluno>, autor=<coordenador>, detalhe="tcc_id=…")` depois do
    commit. `EventoArtigo` é um enum **local** de `services_artigos`, no mesmo padrão de
    `EventoFluxoTCC` da spec 005 (`registrar_evento` só usa `.value`), sem mexer em
    `services.EventoAcesso` nem no conjunto fechado de `test_log_acesso.py` [A23].
- **Justificativa**: RBN-CAD-12.2, 12.3 e 14.1; US-20 E3; Q6; D10; D11; Q16.
- **Alternativas**: filtrar pelo curso do aluno (dá o mesmo na prática, mas a turma é a unidade do
  TCC); acrescentar valores ao `EventoAcesso` (afeta o conjunto fechado da spec 003).

## R10. Permissões e vínculo (FR-014, FR-019, FR-020, FR-023 a FR-025, FR-046; Q10)

- **Decisão**: as funções de vínculo ficam em `services_orientacao` [A4]:
  - `papeis_no_tcc(usuario, tcc) -> set[str]` devolve **todos** os papéis por vínculo **ativo**
    (Q10): `"aluno"`, `"orientador"`, `"coorientador"` e `"professor"`. O Professor da Disciplina
    de uma turma com orientador automático é, ao mesmo tempo, `"professor"` e `"orientador"`;
  - os predicados `e_orientador_atual(usuario, tcc)` e `e_coorientador_ativo(usuario, tcc)`, que
    cada rota testa conforme o papel que exige (rotas 17 a 20: um dos dois; rotas 21 a 24: só o
    primeiro);
  - `pode_alterar_no_tcc(tcc)` combina turma não arquivada, participação não encerrada e TCC não
    copiado (FR-007).
- **Objetos aninhados na URL** [A1]: todo objeto com ID na rota é buscado **filtrando a FK pelo TCC
  do contexto**, senão 404:
  - `Coorientacoes(coo_id=…, coo_tcc=tcc)`;
  - `SolicitacoesOrientacao(sol_id=…, sol_tcc=tcc, sol_tipo=<tipo da rota>)`;
  - `EncontroOrientacao(enc_id=…, enc_tcc=tcc)`.

  O TCC do contexto é o do aluno logado na turma da rota (rotas 1 a 10) ou o `tcc_id` da rota, com
  o vínculo conferido (rotas 17 a 24). As atas do TCC de origem, mostradas no TCC 2 só para
  consulta (FR-023), **nunca** são editadas nem comentadas pela rota do TCC 2: a busca por
  `enc_tcc=tcc` já as exclui. `test_permissoes_orientacao.py` tem um teste por rota que troca cada
  ID por um de outro TCC e espera 404.
- **Turma arquivada na tela de orientandos** [A10, N7]: na linha de turma arquivada (FR-014, "só
  com acesso às atas"), as rotas 21 a 24 respondem como a falta de vínculo (404), inclusive no GET;
  a rota 17 abre só para leitura, sem "Registrar ata", "Editar" nem "Comentar"; o GET das rotas 18
  a 20 volta à 17 com a MT-25, e o POST é recusado com a MT-25.
- **Painel do aluno** [A2, A7]: o painel e a lista de atas do painel exigem
  `turma_para(..., CONSULTAR)`, `turma.tur_doc_id == usuario.pk`, `vinculo_na_turma(turma, alu_id)`
  (padrão das rotas `turmas/<tur_id>/alunos/<alu_id>/` da spec 004) e `tcc_do_aluno(turma, aluno)`.
  A lista mostra só as atas desse TCC e as do TCC de origem. A Secretaria recebe 403, mesmo padrão
  de `historico_status` da spec 005. O botão "Resetar primeiro acesso" só aparece com
  `pode_resetar_primeiro_acesso` **e** a turma do painel não arquivada (FR-019).
- **Justificativa**: a regra Q27 da spec 003 é reaproveitada pela turma; o vínculo é regra desta
  feature. Um conjunto de papéis evita o 404 ao orientador automático (US-18 G) e serve à Defesa,
  que exclui orientador e coorientadores dos avaliadores.
- **Alternativas**: um papel só por prioridade (falha no orientador automático); usar os papéis
  globais de `papeis()` (dizem se o docente orienta **alguém**, não **este** TCC).

## R11. Notificações e e-mails (FR-003, FR-010, FR-033, FR-052)

- **Decisão**: `services.notificar(usuario, mensagem, link)`, com o link do FR-052 montado por
  `reverse`, chamado **dentro** da transação da gravação, como na spec 004 (a notificação é uma
  linha do banco e deve ser gravada ou desfeita junto) [N5]. Os e-mails (MO-01, MO-16, MO-07 e MO-04) usam um helper **compartilhado**
  `services.enviar_email_apos_commit(usuario, assunto, template, contexto)`, extraído de
  `services_entregas._enviar_email_ao_aluno` (com a mesma lógica de `SIGTCC_EMAIL_SINCRONO` e
  thread), que passa a chamá-lo (IC-13) [A26]. A falha fica só no log. Os links absolutos dos
  e-mails usam `settings.SITE_URL + reverse(...)`, padrão de `services._url_absoluta`. Os templates
  de e-mail ficam em `templates/cadastro/emails/` (`pedido_orientacao.txt`,
  `pedido_troca.txt`, `convite_coorientacao.txt`, `orientacao_aceita.txt`); o do convite tem os
  dois links "Aceitar" e "Recusar" (R4).
- **Justificativa**: é o padrão já usado na spec 005 (Assumptions da spec 006), sem uma segunda
  cópia da regra de envio.
- **Alternativas**: copiar a função privada (duas cópias da regra de thread); e-mail síncrono
  (atrasa a resposta e grava antes do commit).

## R12. Abrir a aba Meu TCC na seção certa (E1 das US-17, 19, 45 e 46; FR-042)

- **Decisão**: os links e as notificações usam `?secao=orientacao|atas|publicacao`. A view
  `meu_tcc` passa o valor (só esses 3 aceitos) ao template, que põe `id` nas seções, e
  `static/js/secao.js` rola até a seção. Sem JavaScript, a página abre normalmente no topo.
- **Justificativa**: o fragmento `#` não chega ao servidor e se perde no POST do login; o
  parâmetro sobrevive ao `next` da spec 003.
- **Alternativas**: só `#âncora` (perde-se no login); três rotas diferentes (duplica a view).

## R13. Histórico do Status para o Orientador (FR-043; IC-06)

- **Decisão**: `views_tcc._contexto_historico` passa a ser a função pública
  `services_tcc.contexto_historico(tcc, url_voltar)` [A28]. Os três chamadores recebem `url_voltar`:
  - `historico_status` (Professor, spec 005): volta ao painel;
  - `historico_status_aluno` (Aluno, spec 005): volta à aba Meu TCC;
  - a rota nova `orientacoes/tcc/<tcc_id>/historico/` (`views_orientacao`), que confere o
    Orientador **atual**: volta à tela de orientandos.

  A função monta `turma = tcc.tcc_tur`, usada pelo template (`historico_status.html`) [N9].

  O template `historico_status.html` é reaproveitado. O Coorientador continua sem acesso (spec 005).
- **Justificativa**: não muda a permissão das rotas existentes, e por isso os testes de 403 da
  spec 005 continuam; a 006 não importa função privada de outro módulo.
- **Alternativas**: ampliar a rota da spec 005 ao Orientador (mexe na regra testada); importar a
  função privada.

## R14. Consultas sem N+1 (SC-001, SC-002)

- **Decisão**:
  - **Blocos da aba Alunos e tela de orientandos**: `select_related("tcc_alu__alu", "tcc_tur",
    "tcc_ari")`, com `Prefetch` das orientações ativas e anotação da contagem de atas
    (`Count("encontroorientacao")`). `services_turmas.alunos_da_turma` (IC-02) passa a resolver o
    curso por um dicionário de `Cursos` carregado uma vez, em vez de `curso_do_codigo` por linha
    [A22].
  - **Status das entregas e painel**: `status_exibido` e `link_mais_recente` sobre listas
    pré-carregadas de `Entregas_Marcos` e `Historico_Envios_Entregas` do aluno.
  - **Testes**: `assertNumQueries` na tela de orientandos e na aba "Alunos" com 1 e com 10 linhas,
    e no painel com 1 e com 5 entregas [A22].
- **Justificativa**: o número de consultas fica constante, sem crescer com a quantidade de linhas.

## R15. "Correções Conferidas" (FR-016; Q2)

- **Decisão**: `services_orientacao.conferir_correcoes(orientador, tcc_id)` trava turma → aluno →
  TCC → entrega Versão Final (`versao_final_do_aluno(..., travar=True)`, spec 005). Antes de gravar
  `ent_correcoes_conferidas_em = agora`, confere:
  - que é TCC 2 de Sistemas de Informação (`exige_correcoes_conferidas`, spec 005);
  - o Status "Aprovado com Correções";
  - o envio Entregue ou Entregue com Atraso;
  - que a entrega ainda não foi conferida.

  A apagada na devolução é o IC-07.
- **Justificativa**: reaproveita a regra já escrita na spec 005, e é o único campo de
  `Entregas_Marcos` que a 006 escreve (contrato 005, §3).

## R16. Apto para Defesa (FR-026, FR-027)

- **Decisão**: `estado_apto(tcc)` devolve um destes estados: ausente (Status ≠ Em Andamento ou já
  Apto), `sem_entrega_cadastrada` (com o texto da US-42 E3), `indisponivel` ou `disponivel`. O
  `indicar_apto(orientador, tcc_id)` trava, confere de novo (MO-20 se falhar) e chama
  `atualizar_status_tcc(tcc, turma, orientador, 'Apto para Defesa', INDICACAO_DE_APTO)`. A entrega
  "Documento para Defesa" é encontrada por `Turmas_Marcos.tma_tipo`.
- **Justificativa**: a regra de Status é da spec 005, e esta spec só dispara o gatilho (SC-007).

## R17. Coorientador externo (FR-028; Q13, Q15, D8, D9)

- **Decisão** [A17]: o e-mail é normalizado (`services.normalizar_email`). Com e-mail, o serviço:
  1. chama `services.travar_email(email)` (trava consultiva já existente, que serializa dois
     cadastros do mesmo e-mail ao mesmo tempo);
  2. procura com `cext_email__iexact=email`, `.order_by("cext_id").first()` (a unicidade do banco
     diferencia maiúsculas, então pode haver mais de uma linha antiga);
  3. se achar, reaproveita o registro sem gravar Nome e Instituição, e a janela mostra a MO-25
     (ciência de LGPD na Q15);
  4. se não achar, cria num savepoint; um `IntegrityError` (corrida que escapou da trava) faz reler
     e reaproveitar.

  Sem e-mail, é sempre um registro novo. O Nome passa por `forms_contas.validar_nome_completo`. A
  recusa "Este e-mail já está registrado como coorientador" vale quando há `Coorientacoes` 'Ativa'
  com esse externo no mesmo TCC (índice único `uq_coorientacoes_externo_ativo`).
- **Justificativa**: Q13, e `cext_email` é único no modelo.

## R18. Templates, includes e protótipo

- **Decisão**: as seções Orientação, Atas e Publicação são includes (`tcc/_secao_*.html`) usados
  por `meu_tcc.html` e por `painel_aluno.html` (este com `somente_leitura=True`). A confirmação
  genérica (`orientacao/confirmar.html`) recebe título, texto, `url_acao` e `url_cancelar`. O
  visual segue o protótipo de 17/10 sobre a base CSS da spec 003:
  - `viewOrientacoes`: três blocos;
  - `viewAlunoTurma`: painel em seções;
  - `viewArtigos`: tabela com filtro e botões.
- **Justificativa**: um só template por seção, a mesma informação para o Aluno e para o Professor,
  e a regra fica fora do template.

## R19. Menu (IC-01; Q11)

- **Decisão**: "Orientações" (perfil `docente`, ordem 12, logo depois de "Turmas") e "Aproveitamento
  de artigos" (perfil `coordenador`, ordem 30, `secao: "Gestão"`), como no protótipo. O item
  "Turmas arquivadas" da US não é criado: as specs 004 e 005 já têm o botão na tela Turmas
  (FR-042). Como `contexto.menu` ordena as seções pelo nome, "Gestão" aparece depois de
  "Cadastros"; no protótipo, "Cadastros" fica dentro de "Gestão". A diferença é só de posição e
  fica aceita, sem mexer em `contexto.py` [A32].
- **Justificativa**: FR-040 e FR-041; o processador `contexto.menu` já esconde o item cuja rota
  ainda não existe.

## R20. Testes de outras specs afetados (IC-11)

- **Decisão**: ajustar no mesmo PR, sem remover nenhum cenário:
  - `test_navegacao_tcc.py:177`: o histórico passa a sair do painel;
  - `test_us08_transferencia.py:190`: procura `">Transferir<"` e passa a procurar o texto do
    bloco, "Transferir aluno" [A30];
  - `test_us09_exclusao.py:174`: confere o "Cancelar" com e sem `volta`;
  - `test_us12_senha.py`: o reset passa pelo painel; a tela provisória redireciona;
  - `test_seguranca.py:152`;
  - `test_base_comum.py`: itens novos do menu;
  - `test_us07_*` (arquivamento): continua passando; o cancelamento dos pendentes ganha testes na
    006 (IC-12).

  O responsável roda a suíte completa antes do PR.
- **Justificativa**: o princípio VIII pede que mudanças em código mesclado venham com os testes no
  mesmo PR.

## R21. Arquivamento cancela os pendentes (FR-053; Q17; IC-12)

- **Decisão**: `services_turmas.arquivar_turma` (spec 004), depois de travar a turma e passar por
  `motivo_para_nao_arquivar`, e na mesma transação:
  1. trava os alunos da turma e depois os TCCs da turma (`select_for_update`, por `pk`), na ordem do
     R2;
  2. calcula `agora` uma vez e marca 'Cancelado' com `sol_data_resposta = agora` em todos os pedidos
     e convites pendentes desses TCCs;
  3. na mesma transação, grava a notificação MO-26 ao docente de cada solicitação, com
     `notificar(..., agora=agora)` e o link da solicitação (rota 12 ou 13), que também serve à
     dedução do motivo (R3) [N3, N5].

  O cancelamento é feito por uma função de `services_orientacao`
  (`cancelar_pendentes_da_turma(turma, agora)`), chamada pela spec 004, para a regra das
  solicitações ficar num só módulo. Como `services_orientacao` importa `services_turmas`, o import
  fica dentro de `arquivar_turma` (e da cópia para o TCC 2 no IC-04, se reaproveitar a função),
  para não haver import circular [N6]. A regra nova na US-07 C e na RBN-CAD-04.5 vai à PO para
  ciência (índice Q-117) [N4].
- **Justificativa**: Q17; evita o "Aceitar" que sempre falharia com a MT-25.
- **Alternativas**: esconder ou sinalizar os pendentes na tela (recusada na Q17).
