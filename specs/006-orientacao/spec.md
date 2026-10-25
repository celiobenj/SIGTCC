# Feature Specification: Orientação, Atas e Publicações

**Feature Branch**: `feature/feat-06-orientacao`

**Created**: 2026-10-24

**Status**: Approved (Célio Benjamim, 2026-10-24)

**Input**: User description: "Orientação, Atas e Publicações do SIGTCC: US-17, US-18, US-19, US-20, US-36, US-41, US-42, US-45 e US-46, com o modelo de dados da spec 001 (sem tabelas novas), reaproveitando o que as specs 002 a 005 entregam; pontos de contato com o painel do aluno, a tela de orientandos, o serviço único do Status do TCC e a regra do Professor da Disciplina; para cada tela nova, como o usuário chega até ela; questões abertas que citam a spec 006 como entrada."

**Fontes**: `docs/fonte/Historias_de_Usuario_v3_3.md` (US-17, 18, 19, 20, 36, 41, 42, 45 e 46);
`docs/fonte/Matriz_Requisitos_17_10.md` (RAN-CAD-10, 11 e 12; RBN-CAD-08.9, 10.1 a 10.7, 11.1 a
11.5, 12.1 a 12.3; Glossário de status); `docs/fonte/Modelo_Logico_e_Dicionario_18_10.md` (tabelas
`Orientacoes`, `Coorientacoes`, `CoorientadoresExternos`, `Solicitacoes_Orientacao`,
`Encontro_Orientacao`, `Comentarios_Encontro`, `Artigos`).

## Dependências e reaproveitamento

- **Modelo de dados**: já existe (spec 001). Esta spec **não cria tabelas nem colunas**. Usa
  `Orientacoes` (orientador atual = vínculo 'Ativa'; histórico = vínculos 'Encerrada'),
  `Solicitacoes_Orientacao` (pedidos de Orientação e Troca de Orientação e convites de
  Coorientação, com o status de cada um), `Coorientacoes` (vínculo aceito, 'Ativa', 'Substituída' ou
  'Encerrada'), `CoorientadoresExternos`, `Encontro_Orientacao` (ata), `Comentarios_Encontro` e
  `Artigos` (publicação e aproveitamento), além de `TCCs`, `PalavrasChave_TCC`, `Turmas_Marcos` e
  `Entregas_Marcos` (spec 005, só leitura, exceto `ent_correcoes_conferidas_em`).
- **Spec 003 (Acesso e Login)** — `contracts/servicos-compartilhados.md`: base visual; verificação
  de perfil (`tipo_conta`, `papeis`, `tem_perfil`, `perfil_requerido`); a regra compartilhada do
  Professor da Disciplina (Q27 da spec 003: o papel vale com turma ativa ou arquivada, **mas ações
  que alteram dados exigem ser Professor de turma não arquivada ligada ao dado**,
  `professor_com_turma_ativa`); `pode_resetar_primeiro_acesso` e `resetar_primeiro_acesso`
  (botão "Resetar primeiro acesso" do painel do aluno, US-41); `notificar` e o envio de e-mail.
  **Muda nesta spec** (Clarifications D3): o reset acionado pelo painel e o "Cancelar" da
  confirmação voltam ao painel do aluno; o nome do aluno na turma deixa de levar à tela mínima de
  reset (`/alunos/<id>/`), que perde o caminho na interface e cujo endereço passa a levar ao painel.
- **Spec 002 (Gestão de Contas)** — `contracts/servicos-compartilhados.md`, §1:
  `docentes_ativos()` é a base das listas de orientador e de coorientador (só docentes 'Ativa'), e
  `travar_e_conferir_ativo(usuario)` é obrigatório, na mesma transação, ao criar pedido,
  convite, orientação e coorientação (índice Q-68). A listagem de docentes da spec 002 já mostra a
  quantidade de orientandos em TCC 1 e TCC 2, com alerta acima de 5 (RBN-CAD-11.3, US-18 F): esta
  spec só cria e encerra os vínculos que essa contagem lê.
- **Spec 004 (Turmas e Alunos)** — `contracts/servicos-compartilhados.md`: `turma_para`,
  `vinculo_na_turma`, `travar_turma_ativa`/`TurmaArquivada` (MT-25), `participacao_encerrada`,
  `turma_tem_orientador_automatico` (TCC 2 de Engenharia de Computação e de Licenciatura em
  Computação: o Professor da Disciplina já é o Orientador, origem 'Automático'),
  `encerrar_orientacoes_ativas` e as ações "Excluir da turma", "Encerrar participação" e
  "Transferir" (US-08 e US-09), que passam a ser acionadas também a partir do painel do aluno
  (US-41). O FR-010 da spec 004 (só Professor da Disciplina e Secretaria do curso abrem a turma)
  continua valendo. **Muda nesta spec**: (1) a aba "Alunos" vira blocos somente leitura
  (RBN-CAD-10.5) e as ações do Professor da Disciplina sobre o aluno, inclusive "Editar", passam para
  o painel (Clarifications Q1 e Q5); "Transferir aluno" continua no bloco só para a Secretaria do
  curso (RBN-CAD-05.6, US-08 D; Q4); (2) as telas de Editar e Encerrar participação abertas pelo
  painel voltam ao painel; Excluir e Transferir, depois de confirmados, voltam à aba "Alunos",
  porque o aluno sai da turma (FR-044); (3) a cópia para TCC 2 (`_copiar_tcc_aprovado`) passa a
  cancelar os pedidos e convites pendentes do TCC 1 (Q6, FR-051); (4) os cancelamentos automáticos
  (encerramento, transferência, cópia para TCC 2) e a orientação criada na transferência gravam a
  data e a hora iguais às do evento que os causou (Q7, FR-050); (5) o arquivamento da turma
  (`arquivar_turma`) passa a cancelar os pedidos e convites pendentes dos TCCs da turma (Q17,
  FR-053).
- **Spec 005 (Fluxo do TCC e Entregas)** — `contracts/servicos-compartilhados.md`:
  `services_turmas.atualizar_status_tcc` (serviço único do Status; a US-42 dispara o gatilho
  "Indicação de Apto para Defesa", sempre com turma → aluno → TCC travados por quem chama);
  `services_tcc.historico_do_status` (consulta sem checagem de perfil: esta spec aplica a checagem
  do Orientador na tela de orientandos, US-14 fluxo A); `services_tcc.pode_ver_resumo` (o "Ver
  proposta" da US-18 e o painel do aluno chamam esta função antes de mostrar o Resumo);
  `services_entregas.status_exibido` e `link_mais_recente` (coluna de entregas da tela de
  orientandos e seção Entregas do painel do aluno); o campo
  `Entregas_Marcos.ent_correcoes_conferidas_em`, **gravado por esta spec** pela ação "Correções
  Conferidas" (FR-029 da spec 005); as rotas `historico_status`, `aluno_versao_final` e as abas da
  turma (FR-031 da spec 005), que o painel do aluno passa a reunir. **Muda nesta spec**
  (Clarifications Q2): a devolução para ajuste da Versão Final passa a apagar a conferência; o
  link "Histórico do Status do TCC" sai da lista da aba "Alunos" para o painel (Q1); a tela de
  histórico abre também ao Orientador atual e o "Fechar" volta à tela de origem (tela de orientandos
  ou painel, US-14 A e B; FR-043); `pode_ver_resumo` passa a liberar o Resumo também ao docente de um
  pedido de **Troca de Orientação** pendente (hoje só o de Orientação: defeito encontrado na
  revisão, FR-013); Homologar e Devolver para Ajuste, abertos pelo painel, voltam ao painel; e o
  registro do histórico do Status passa a aceitar a data e a hora do evento, para o FR-050.
- **O que outras features podem consumir desta spec** (a detalhar no contrato do plano): o
  orientador atual e os coorientadores ativos de um TCC (Defesa, composição da banca: orientador e
  coorientadores ficam fora dos avaliadores); o cancelamento automático do pedido de troca pendente
  quando a defesa é agendada (US-17 E e US-18 E4, disparado pela feature de Agendamento, US-24); e o
  aproveitamento homologado do artigo com Qualis A ou B, que garante nota final mínima 6,0 na
  liberação do resultado (US-20; aplicado pela feature de Avaliação, US-27), lembrando que a
  apresentação perante a banca continua obrigatória (RBN-CAD-12.3). O cancelamento pelo agendamento
  MUST gravar a data e a hora do evento "Agendamento" do histórico da defesa (FR-050). Pontos que o
  módulo de Defesa acrescenta depois: o link "Histórico da defesa", o agendamento a partir da tela
  de orientandos, a abertura da sessão de defesa e o conteúdo da seção Defesa do painel do aluno e
  da aba Meu TCC (Q-87).

## Clarifications

### Entrada: questões abertas de `docs/questoes-a-rever.md` que citam esta spec

- **Q-13** (painel do aluno recebe "Resetar primeiro acesso"?): sim — decidido na própria descrição
  desta spec (Célio Benjamim, 2026-10-24): o painel do aluno (US-41) recebe o botão, usando
  `pode_resetar_primeiro_acesso`/`resetar_primeiro_acesso` da spec 003, só para o Professor da
  Disciplina de turma não arquivada do aluno. Na revisão de 2026-10-24 (D3), a tela mínima de reset
  da spec 003 perde o caminho na interface (o nome do aluno passa a abrir o painel) e o seu endereço
  passa a levar ao painel do aluno.
- **Q-29** (Professor da Disciplina com turma arquivada): esta spec segue a regra Q27 da spec 003 —
  consultas valem com turma ativa ou arquivada; ações que alteram dados exigem turma não arquivada
  ligada ao dado (FR-046).
- **Q-40** (encerramento da participação cancela pedidos e convites pendentes, spec 004): as telas
  desta spec mostram esses pedidos e convites como 'Cancelado' e, pelo link do e-mail, a mensagem
  provisória MO-12, com um texto para pedido e outro para convite (FR-012 e FR-050).
- **Q-68** (listas só com docentes 'Ativa' e trava da conta ao criar vínculos, spec 002): aplicado
  nos FR-002, FR-028 e FR-047.
- **Q-76, item 2** (a quantidade de orientandos exclui TCC encerrado ou turma arquivada?): a
  contagem é da spec 002; esta spec não a muda e só cria/encerra vínculos. A questão continua com a
  spec 002.
- **Q-81** (nome do link de histórico): a linha da tela de orientandos e o painel do aluno usam o
  mesmo nome provisório da spec 005, "Histórico do Status do TCC", até a resposta.
- **Q-87** (seção Defesa da aba Meu TCC: nota final e botões Ata Final e Folha de Aprovação): **fora
  do escopo desta spec**. A nota final é da US-27 e a Ata Final e a Folha de Aprovação são da US-28,
  ambas do módulo de Defesa (PGCS 4.3: `feat-08-avaliacao` e `feat-09-documentacao`; Cronograma,
  "Emissão de Atas e Documentos Oficiais", US-25 a US-28). A pendência deve ser redirecionada a
  essas features; os botões continuam desabilitados até lá.
- **Q-91** (TCC 2: linha nova em `TCCs` ou a mesma linha?): respondida na revisão desta spec
  (Session 2026-10-24, revisão, Q6): vale a linha nova da spec 004.

### Pontos decididos nesta especificação (a confirmar no `/speckit-clarify`)

- A tela "Orientações" aparece no menu de **todo Docente** (não só de quem já é orientador): é ali
  que chegam os pedidos e convites de quem ainda não orienta ninguém (US-18 e US-36, passo 1).
  Confirmado na Q11.
- O painel do aluno (US-41) é só do Professor da Disciplina da turma (RBN-CAD-08.9). A Secretaria
  do curso abre a turma só para consulta e aciona "Transferir aluno" no bloco, sem o painel
  (Session 2026-10-24, revisão, Q4).

### Session 2026-10-24

- Q1: As ações sobre o aluno que hoje ficam na linha da aba "Alunos" (Editar, Excluir da turma,
  Encerrar participação, Transferir e "Histórico do Status do TCC") passam só para o painel do aluno
  ou ficam também na lista? → A: **Só no painel** (Célio Benjamim, 2026-10-24), como na US-41: a aba
  "Alunos" vira uma lista de blocos de consulta, e as ações do Professor da Disciplina ficam só no
  painel do aluno. "Transferir" continua na lista **apenas para a Secretaria do curso**, que não abre
  o painel (spec 004, Q9). **Muda o comportamento da spec 004 já mesclada** (tela da turma e testes
  dela): registrado para ciência da responsável (índice Q-96). Confirmado e completado na revisão
  (Q4 e Q5).
- Q2: Quando aparece "Correções Conferidas" e o que a devolução faz com ela? → A: **Só depois do
  envio da Versão Final** (status de envio Entregue ou Entregue com Atraso), em TCC 2 de Sistemas de
  Informação com o Status "Aprovado com Correções" e ainda sem conferência; **a devolução para
  ajuste (US-44 D) apaga a conferência**, e o Orientador confere de novo depois do reenvio (Célio
  Benjamim, 2026-10-24). **Muda o comportamento da spec 005 já mesclada** (a devolução passa a limpar
  `ent_correcoes_conferidas_em`): registrado para ciência (índice Q-96).
- Q3: Texto da US-18 (passo 7 e cenário 1), "Pedido aceito. O aluno foi incluído no seu tela de
  orientandos"? → A: **Corrigir a concordância**: "Pedido aceito. O aluno foi incluído na sua tela de
  orientandos", como mensagem PROVISÓRIA MO-15 até a PO confirmar e a US ser corrigida (Célio
  Benjamim, 2026-10-24; índice Q-94).

### Session 2026-10-24 (revisão do `analista-requisitos`)

Respostas de Célio Benjamim à conferência da spec contra as US-17 a 20, 36, 41, 42, 45 e 46 (v3.3),
a matriz de 17/10 e o modelo lógico.

- Q4: A matriz (RBN-CAD-10.5) diz que a lista é somente leitura e a US-41 E2, que quem não é o
  Professor da Disciplina não vê a lista nem os painéis; já a RBN-CAD-05.6 e a US-08 D deixam a
  Secretaria do curso transferir o aluno ("aciona Transferir no aluno") e a US-07 E8 a deixa abrir
  a turma só para consulta. Como fica? → A: **Seguir a RBN-CAD-05.6 e a US-08 D** (a matriz
  prevalece): para o Professor da Disciplina, a aba "Alunos" é uma lista de blocos somente leitura
  (RBN-CAD-10.5 e 08.9) e todas as ações ficam no painel; a Secretaria do curso abre a turma só para
  consulta (US-07 E8), vê os blocos sem abrir o painel (RBN-CAD-08.9) e aciona "Transferir aluno" no
  bloco. A US-41 E2 e as RBN-CAD-08.9 e 10.5, que não citam a Secretaria, precisam ser conferidas
  pela PO (índice Q-97).
- Q5: Onde fica o "Editar" dos dados do aluno (RBN-CAD-05.3; US-08 C: "na linha do aluno"), com a
  lista somente leitura e o painel da RBN-CAD-08.9 sem "Editar"? → A: **No painel**, junto com as
  ações da RBN-CAD-08.9. A PO deve incluir a ação na RBN-CAD-08.9 e na US-41 e ajustar a US-08 C
  (índice Q-98).
- Q6 (índice Q-91): Na transferência para TCC 2, vale a linha nova em `TCCs` (código da spec 004) ou
  a mesma linha (dicionário 3.5.1)? → A: **Linha nova**. Consequências nesta spec (FR-051): o
  registro de publicação vai para o TCC 2 com o aproveitamento já decidido (RBN-CAD-08.6 e 12.3); a
  orientação não automática e as coorientações ativas também (spec 004); as atas ficam no TCC 1 e
  aparecem, só para consulta, na lista de atas do TCC 2, identificadas pela turma de TCC 1; a tela
  "Aproveitamento de artigos" mostra só o TCC atual do aluno, sem repetir o artigo do TCC 1; os
  pedidos e convites pendentes do TCC 1 são cancelados na cópia (MO-18); e o TCC 1 fica só para
  consulta. O dicionário 3.5.1 deve ser ajustado (índice Q-91).
- Q7: Como saber o motivo de um pedido ou convite 'Cancelado', se a tabela não tem a coluna? → A:
  **Sem coluna nova; regra de dedução** (FR-050): todo cancelamento automático grava em
  `sol_data_resposta` a mesma data e hora do evento que o causou, e o motivo é o evento com essa data
  e hora; sem evento coincidente, o cancelamento foi do aluno.
- Q8: Depois da liberação do resultado, alterar Qualis, Status ou Link desfaz a homologação que já
  valeu? → ~~A: **Não** (aproveitamento congelado depois da liberação)~~. **Resposta substituída pela
  Q16** (revisão do plano, 2026-10-24): segue a RBN-CAD-12.3, as US-46 C e US-20 D e E3 e o
  dicionário 3.5.7 como estão; a Q-100 foi respondida sem ajuste de documento.
- Q9: Na recusa do pedido de orientação, a RBN-CAD-10.2 diz que "o resultado é comunicado … ao
  Professor da Disciplina"; a US-18 D só avisa o Aluno. Quem é avisado? → A: **Seguir a US**: na
  recusa, só o Aluno; o Professor da Disciplina é avisado no aceite (FR-010 e FR-011). A PO deve
  conferir a RBN-CAD-10.2 (índice Q-99).
- Q10 (`/speckit-clarify`): Depois da troca de orientador, o ex-orientador continua vendo as atas do
  aluno? → A: **Não**: perde o acesso, como o coorientador removido (RBN-CAD-10.7; US-36 D). Só o
  vínculo ativo dá acesso às atas (FR-023). Confirma a D4.
- Q11 (`/speckit-clarify`): O item de menu "Orientações" aparece para todo Docente ou só para quem
  tem orientando, coorientação ou pedido ou convite pendente? → A: **Para todo Docente** (US-18 e
  US-36, passo 1); sem pedidos, convites nem orientandos, a tela abre com as seções vazias (MO-24).
  Confirma o primeiro dos "Pontos decididos".
- Q12 (`/speckit-clarify`): Com o botão "Resetar primeiro acesso" no painel do aluno, o que fazer com
  a tela provisória de reset da spec 003 (`/alunos/<id>/`, FR-015 da spec 003)? → A: **Retirar a
  tela**; o endereço antigo passa a abrir o painel do aluno, e o reset fica só no painel
  (RBN-CAD-06.8 e 08.9; US-41). Com o painel restrito ao Professor da Disciplina da turma do aluno,
  a observação de LGPD S-02 deixa de valer. Confirma a D3.
- Q13 (`/speckit-clarify`): No coorientador externo com e-mail já cadastrado em outro trabalho, o
  sistema mantém o Nome e a Instituição gravados ou grava os digitados? → A: **Mantém os gravados**
  e reaproveita o registro (`cext_email` único), avisando o aluno com a MO-25; um aluno não altera o
  registro que aparece no TCC de outro. Confirma a D9.
- Q14 (`/speckit-clarify`): O e-mail e a notificação do convite de coorientação trazem os botões
  "Aceitar" e "Recusar" (RBN-CAD-10.4), e o clique responde direto ou abre a tela? (a US-36 diz que o
  convite "nunca é respondido pelo e-mail") → A: **Os botões existem, mas só abrem a tela
  Orientações** com o convite destacado; a resposta é dada na tela, depois do login, com o registro
  de quem respondeu, da data e da hora. Atende a matriz e a US. Confirma a D7.

### Session 2026-10-24 (revisão do plano pelo `arquiteto-django`)

Respostas de Célio Benjamim aos pontos da revisão do plano que mudavam comportamento. A spec continua
aprovada; as mudanças abaixo foram feitas a pedido dele e estão refletidas nos FR indicados. As
soluções só de implementação ficaram no plano (research R1 a R21), por delegação dele.

- Q15: Com o reaproveitamento do coorientador externo pelo e-mail (Q13), um aluno que digita um
  e-mail já cadastrado vê o Nome e a Instituição gravados por outro TCC (MO-25). Limitar o aviso? →
  A: **Não; ciente, fica como está** (LGPD: ciência registrada; o dado exposto é o nome e a
  instituição de um coorientador, nunca o TCC nem o aluno em que ele atua).
- Q16 (substitui a Q8): O dicionário 3.5.7 e a RBN-CAD-12.3 mandam o artigo voltar a "Em Análise" a
  cada alteração de Qualis, Status ou Link, sem limite de tempo, o que contradizia a Q8. → A:
  **Seguir estritamente os documentos consolidados**: alterar Qualis, Status ou Link de um artigo já
  analisado **sempre** desfaz a decisão e o artigo volta a "Em Análise", antes ou depois da
  liberação (RBN-CAD-12.3; US-46 C; US-20 D; dicionário 3.5.7). O Coordenador homologa e recusa a
  qualquer tempo, exceto **recusar um artigo Homologado depois da liberação**, que fica indisponível
  (US-20 C e E3). A nota já liberada não muda: vale a homologação existente na liberação
  (RBN-CAD-12.3; RBN-DEF-06.2 e 06.4, aplicadas pela US-27). FR-036, FR-038 e FR-051 ajustados;
  US9 cenários 10 e 11 refeitos; MO-21 reescrita; Q-100 respondida.
- Q17: Uma turma pode ser arquivada (RBN-CAD-04.5) com pedidos ou convites pendentes de TCCs "Sem
  Proposta" ou já aprovados, que ficariam para sempre com um "Aceitar" que sempre falha. → A:
  **Cancelar os pendentes no arquivamento** (FR-053; motivo deduzido no FR-050; MO-26). Muda a
  spec 004 já mesclada (`arquivar_turma`; item de configuração IC-12, índice Q-114). Para o link
  continuar mostrando "cancelado pelo aluno" quando o aluno cancelou antes do arquivamento (US-18 E3
  e US-36 E3), o arquivamento é reconhecido pela notificação MO-26 que ele grava com a mesma data e
  hora e com o link da solicitação, sem coluna nova (FR-050). A regra nova na US-07 foi levada à
  PO para ciência (índice Q-117).
- Q18: O FR-052 mandava as notificações do encerramento da participação e da transferência
  levarem à tela Orientações com a MO-12 e a MO-17, mas a spec 004 já avisa os docentes com a MT-31
  (encerramento) e a MT-22 (transferência). → A: **Manter as notificações da spec 004** como estão;
  a MO-12 e a MO-17 ficam só como texto do link do pedido ou convite cancelado (FR-052 ajustado).

### Decisões propostas na revisão (a validar; índice Q-101)

Lacunas que as fontes não resolvem e que não contrariam as US nem a matriz. Ficam como proposta
desta spec até a validação; a D3, a D4, a D7 e a D9 foram decididas por Célio Benjamim no
`/speckit-clarify` (Q10 a Q14):

- **D1 (navegação)**: cada tela e janela tem a volta definida nos FR-042 a FR-045 e no FR-052; o
  link de pedido ou convite abre a tela "Orientações" com o estado no topo (FR-012); os textos dos
  E2 a E5 das US-18 e US-36 valem no lugar do aviso genérico de item indisponível da spec 003
  (índice Q-12).
- **D2 (histórico de orientação)**: a seção Orientação da aba Meu TCC e a do painel mostram o
  histórico dos vínculos (orientadores e coorientadores anteriores, com datas) e dos pedidos e
  convites recusados ou cancelados (FR-049), que as US citam ("a troca fica no histórico") sem dizer
  onde se consulta.
- **D3 (tela mínima de reset da spec 003; decidida na Q12)**: perde o caminho na interface e o seu endereço passa a
  levar ao painel do aluno; o reset passa a ser feito pelo painel (Q-13; observação S-02).
- **D4 (envolvidos nas atas, RAN-CAD-11 NFR; decidida na Q10)**: veem as atas o Aluno, o Orientador e os
  Coorientadores **atuais** e o Professor da Disciplina; o ex-orientador (troca ou transferência)
  perde o acesso, como o coorientador removido (US-36 D; RBN-CAD-10.7).
- **D5 (participação encerrada, RBN-CAD-08.5: "apenas para consultar")**: orientação, atas e
  publicação ficam só para consulta do Aluno; o vínculo de orientação é encerrado (spec 004, Q10) e
  o trabalho sai da tela de orientandos.
- **D6 (tela de orientandos)**: só vínculos ativos; o de turma arquivada continua ativo e aparece no
  fim (US-18 G). A "Lista somente leitura" da RBN-CAD-11.4 vale para os dados da linha; as ações são
  as da US-18 passo 7.
- **D7 (e-mail do convite, RBN-CAD-10.4 × US-36; decidida na Q14)**: o e-mail e a notificação trazem os botões
  "Aceitar" e "Recusar" como links que abrem a tela "Orientações" com o convite; a resposta é dada
  na tela, nunca pelo e-mail.
- **D8 (estados da coorientação)**: "Substituir" grava 'Substituída' e "Remover" grava 'Encerrada';
  a coorientação encerrada pela troca de orientador, pela transferência ou pelo encerramento também
  fica 'Encerrada'; a lista de Docentes do NUCOMP exclui quem já tem convite pendente no trabalho.
- **D9 (coorientador externo com e-mail já cadastrado; decidida na Q13)**: o registro existente é reaproveitado sem
  alterar Nome e Instituição, que continuam os já gravados.
- **D10 (publicação)**: só o Link ou DOI é obrigatório (RBN-CAD-12.1); sem análise, a etiqueta
  mostra a MO-22; mudar a modalidade para Monografia esconde a seção e tira o artigo da tela do
  Coordenador, sem apagar o registro; cada decisão do Coordenador vai também para o log de eventos,
  porque a tabela guarda só a mais recente.
- **D11 (Coordenador)**: as decisões do Coordenador seguem a regra da liberação (US-20 E3; Q16), e
  não a de turma arquivada do FR-046; o curso do artigo é o da turma do TCC.
- **D12 (painel do aluno)**: a seção Versão Final traz os botões "Homologar" e "Devolver para
  Ajuste" (US-44 passo 3), que abrem as confirmações da spec 005 e voltam ao painel; a seção Defesa
  mostra a MO-23 até o módulo de Defesa; a seção Publicação só aparece em Artigo Científico.
- **D13 (pendentes em situações não previstas)**: o convite pendente ao docente que passa a ser o
  orientador (troca aceita ou transferência) é cancelado (MO-17), como a spec 004 já faz na
  transferência; o pedido pendente a um docente inativado continua pendente até o aluno cancelar (o
  aceite é recusado, Q-68).
- **D14 (ata sem autor)**: sem coluna nova, pela mesma orientação da Q7; na mesma Data do Encontro,
  a mais recente é a última registrada (índice Q-102).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Aluno indica, cancela ou troca o orientador [US-17] (Priority: P1)

Como Aluno, indico o meu orientador e, quando necessário, cancelo o pedido ou troco de orientador,
para que o meu trabalho tenha a orientação registrada no sistema.

**Why this priority**: sem orientador não há tela de orientandos, atas acompanhadas, coorientação
nem Apto para Defesa; é a entrada de toda a feature.

**Independent Test**: com um aluno matriculado numa turma sem orientador automático, enviar o
pedido, cancelar, enviar de novo e, com a resposta simulada pelo serviço, conferir a seção
Orientação.

**Acceptance Scenarios** (cenários 1 a 12 da US-17):

1. **Given** o Aluno autenticado, vinculado à turma e sem orientador, **When** seleciona um docente
   na lista "Indicar orientador" e aciona "Enviar pedido", **Then** o pedido fica "Aguardando
   Resposta", a lista fica bloqueada, aparece "Pedido enviado a [nome do docente]. Aguardando
   resposta" e o botão "Cancelar Pedido"; **and** após o aceite, a seção mostra o docente como
   Orientador.
2. **Given** o TCC "Sem Proposta", **When** o Aluno envia o pedido, **Then** ele fica "Aguardando
   Resposta" e o docente recebe a notificação e o e-mail com "Proposta ainda não registrada" no
   lugar do título.
3. **Given** o pedido "Aguardando Resposta", **When** o docente recusa, **Then** o Aluno é notificado
   e a lista "Indicar orientador" volta a ficar disponível.
4. **Given** o pedido "Aguardando Resposta", **When** o Aluno aciona "Cancelar Pedido", **Then** o
   pedido passa a "Cancelado" e a lista volta a ficar disponível.
5. **Given** o TCC "Em Andamento" com o orientador X e sem sessão de defesa Agendada, Reagendada ou
   Em Andamento, **When** o Aluno escolhe Y em "Trocar de orientador" e envia, **Then** X continua
   Orientador até Y aceitar; **and** após o aceite, X é notificado e a troca vai para o histórico.
6. **Given** o pedido de troca para Y sem resposta, **When** a defesa é agendada, **Then** o pedido
   passa a "Cancelado", o orientador atual é mantido e o Aluno e Y são avisados.
7. **Given** o Aluno numa turma de TCC 2 de Engenharia de Computação, **When** abre a seção
   Orientação, **Then** o professor da turma já aparece como Orientador, sem a lista "Indicar
   orientador".
8. **Given** o Aluno sem sessão, **When** tenta abrir a aba Meu TCC, **Then** vê a tela de login
   (US-11); **and** após o login, abre a aba Meu TCC na seção Orientação.
9. **Given** o pedido "Aguardando Resposta", **When** o Aluno abre a seção Orientação, **Then** a
   lista aparece bloqueada e só o botão "Cancelar Pedido" está disponível.
10. **Given** a defesa do TCC Agendada, **When** o Aluno abre a seção Orientação, **Then** a lista
    "Trocar de orientador" aparece desabilitada.
11. **Given** o TCC Desistente, **When** o Aluno abre a seção Orientação, **Then** ela aparece só
    para consulta, sem indicar nem trocar orientador.
12. **Given** a turma arquivada, **When** o Aluno abre a seção Orientação em "Turmas arquivadas",
    **Then** ela aparece só para consulta, sem indicar, trocar ou cancelar pedido.

---

### User Story 2 - Docente aceita ou recusa pedidos e consulta a tela de orientandos [US-18] (Priority: P1)

Como Docente do NUCOMP, aceito ou recuso os pedidos de orientação e consulto os meus orientandos
na tela de orientandos, para assumir a orientação e acompanhar os trabalhos em um só lugar.

**Why this priority**: completa o vínculo de orientação e é a tela onde o Orientador registra atas,
indica Apto para Defesa, confere correções e acessa o histórico.

**Independent Test**: com um pedido pendente criado por fábrica, aceitar pela tela Orientações e
conferir o vínculo, as notificações e a linha do aluno na tela de orientandos.

**Acceptance Scenarios** (cenários 1 a 14 da US-18):

1. **Given** o docente com um pedido "Aguardando Resposta", **When** abre "Orientações" no menu e
   aciona "Aceitar", **Then** vira Orientador e vê "Pedido aceito. O aluno foi incluído na sua tela
   de orientandos" (MO-15, Clarifications Q3); **and** o pedido sai da seção, o aluno
   aparece na tela de orientandos com o Papel Orientador, e o Aluno e o Professor da Disciplina são
   notificados.
2. **Given** o docente autenticado com o e-mail do pedido, **When** acessa o link, **Then** abre a
   tela Orientações com o pedido na seção "Pedidos de orientação".
3. **Given** a notificação do pedido no sino, **When** o docente a seleciona, **Then** abre a tela
   Orientações com o pedido.
4. **Given** o pedido de um aluno com Proposta, **When** o docente aciona "Ver proposta", **Then** vê
   Título, Subtítulo, Resumo, Modalidade e Link do Documento da Proposta só para leitura; **and** ao
   fechar, volta à linha com "Aceitar" e "Recusar".
5. **Given** o pedido de um aluno "Sem Proposta", **When** o docente abre a tela, **Then** a linha
   mostra "Proposta ainda não registrada", sem o botão "Ver proposta".
6. **Given** o pedido pendente, **When** o docente aciona "Recusar", **Then** a recusa é registrada,
   aparece "Pedido recusado" e o pedido sai da seção; **and** o Aluno é notificado e pode indicar
   outro orientador.
7. **Given** o aluno com o orientador X e pedido de troca para Y, **When** Y aceita, **Then** Y vira
   Orientador, X é notificado, a troca vai para o histórico e o aluno sai da tela de orientandos de X.
8. **Given** o docente já com 5 orientandos, **When** aceita mais um, **Then** a listagem de docentes
   (spec 002) mostra 6, com alerta, para o Coordenador e a Secretaria.
9. **Given** o docente Orientador de dois alunos, um de turma arquivada, **When** abre
   "Orientações", **Then** vê os dois com Nome do Aluno, Curso, Turma, Título, Modalidade, Papel,
   Status do TCC, entregas e atas; **and** o da turma arquivada aparece no fim, só para consultar as
   atas.
10. **Given** o docente sem sessão, **When** acessa o link do pedido, **Then** vê o login; **and**
    depois abre a tela Orientações com o pedido.
11. **Given** o docente Z abre o link de um pedido feito a Y, **When** a página carrega, **Then** vê
    "Este pedido não está disponível para o seu usuário", sem "Aceitar" e "Recusar".
12. **Given** o pedido cancelado pelo Aluno, **When** o docente abre o link, **Then** vê "Este pedido
    foi cancelado pelo aluno", sem os botões.
13. **Given** o pedido de troca sem resposta, **When** a defesa é agendada, **Then** o pedido passa a
    "Cancelado", o orientador atual é mantido e o docente e o Aluno são avisados; pelo link, "Este
    pedido foi cancelado porque a defesa foi agendada".
14. **Given** o pedido já aceito, **When** o docente abre o link de novo, **Then** vê "Aceito", com a
    data e a hora, sem os botões.

Pontos de contato acrescentados pela descrição desta spec (não são cenários das US-18):

15. **Given** o Orientador na tela de orientandos, **When** aciona "Histórico do Status do TCC" na
    linha do aluno, **Then** vê o histórico e a trilha do Status (US-14, fluxo A; FR-009 da spec
    005); o Coorientador não tem esse link (Clarifications da spec 005).
16. **Given** o TCC 2 de Sistemas de Informação com parecer "Aprovado com Correções", **When** o
    Orientador aciona "Correções Conferidas" na linha do aluno e confirma, **Then** a conferência é
    gravada com a data e a hora e o botão Homologar passa a ficar disponível ao Professor da
    Disciplina (US-44 B e cenário 3; FR-029 da spec 005); o botão só aparece depois do envio da
    Versão Final e não aparece em Engenharia de Computação, Licenciatura em Computação nem com o
    parecer "Aprovado"; depois de uma devolução para ajuste, a conferência é apagada e o botão volta
    após o reenvio (Clarifications Q2).
17. **Given** um pedido de **Troca de Orientação** pendente feito ao docente Y, **When** Y aciona
    "Ver proposta", **Then** vê também o Resumo (FR-013; correção do `pode_ver_resumo` da spec 005).

---

### User Story 3 - Professor da Disciplina vê os alunos da turma e o painel de cada aluno [US-41] (Priority: P1)

Como Professor da Disciplina, vejo os alunos da minha turma, com ou sem orientador, e abro o painel
de cada um, para acompanhar a turma em um só lugar e acessar as ações sobre cada aluno.

**Why this priority**: é a "tela do aluno" que as specs 003, 004 e 005 deixaram pendente (reset do
primeiro acesso, encerrar, transferir, histórico, Versão Final) e o ponto de consulta das atas pelo
Professor (US-19 F).

**Independent Test**: com uma turma de 3 alunos (um sem orientador, um sem Proposta), abrir a aba
"Alunos" e o painel de um aluno, conferindo as seções e os botões de ação.

**Acceptance Scenarios** (cenários 1 a 7 da US-41):

1. **Given** o Professor da Disciplina e a turma com 3 alunos, **When** abre a turma e o bloco de um
   aluno, **Then** a aba "Alunos" mostra os 3 blocos e o painel abre com Proposta e TCC, Orientação e
   coorientação, Entregas, Atas, Publicação, Defesa e Versão Final; **and** "Fechar" volta à aba
   "Alunos".
2. **Given** um aluno sem orientador, **When** o Professor abre a turma, **Then** o bloco mostra "Sem
   orientador".
3. **Given** um aluno sem Proposta, **When** o Professor abre a turma, **Then** o bloco mostra "Sem
   Proposta" no lugar do Título.
4. **Given** o Professor no painel de um aluno, **When** aciona "Encerrar participação", **Then**
   abre o encerramento da participação (US-09, spec 004).
5. **Given** a turma arquivada, **When** o Professor a abre em "Turmas arquivadas" e seleciona um
   bloco, **Then** o painel aparece só para consulta, sem botões de ação.
6. **Given** o Professor sem sessão, **When** tenta abrir a turma, **Then** vê o login; **and**
   depois abre a aba "Alunos".
7. **Given** um Docente que não é o Professor da Disciplina da turma, **When** tenta abrir a turma,
   **Then** não vê a lista nem os painéis.

Pontos de contato acrescentados na revisão (Clarifications Q4; FR-044):

8. **Given** a Secretaria do curso numa turma com orientador automático, **When** abre a turma,
   **Then** vê os blocos só para consulta, sem abrir o painel, e o botão "Transferir aluno" no bloco
   do aluno que pode ser transferido.
9. **Given** o Professor no painel de um aluno, **When** aciona "Encerrar participação" e confirma
   ou cancela, **Then** volta ao painel do aluno.

---

### User Story 4 - Aluno, Orientador e Coorientador registram, consultam, editam e comentam atas [US-19] (Priority: P1)

Como Aluno, Orientador ou Coorientador, registro, consulto e edito as atas dos encontros de
orientação e, como Orientador ou Coorientador, comento-as, para comprovar a assiduidade.

**Why this priority**: Must Have (RBN-CAD-11.1 e 11.2) e base do acompanhamento da orientação.

**Independent Test**: registrar uma ata como Aluno, outra como Orientador, comentar e editar, e
conferir a ordem e a visibilidade para o Professor da Disciplina.

**Acceptance Scenarios** (cenários 1 a 16 da US-19):

1. **Given** o Aluno com orientador, na seção "Atas de orientação" da aba Meu TCC, **When** registra
   a ata com a Data do Encontro de ontem, Pauta e Metas, **Then** vê "Ata registrada" e a ata fica
   no topo do histórico para Aluno, Orientador e Professor da Disciplina.
2. **Given** o Orientador na tela de orientandos, **When** aciona "Registrar ata" na linha do aluno e
   salva, **Then** a ata fica no topo do histórico do aluno.
3. **Given** o docente que aceitou a coorientação, **When** registra a ata pela linha do trabalho,
   **Then** a ata fica no topo do histórico.
4. **Given** 3 atas, **When** o Aluno aciona "Ver atas", **Then** vê as 3, da mais recente para a
   mais antiga, com os comentários.
5. **Given** uma ata do Aluno, **When** o Orientador comenta e salva, **Then** o comentário aparece
   abaixo da ata, com autor, data e hora.
6. **Given** uma ata do Aluno, **When** o Aluno edita as Metas e salva, **Then** a ata mostra as novas
   Metas.
7. **Given** o Professor da Disciplina no painel de um aluno, **When** abre as atas, **Then** as vê só
   para leitura.
8. **Given** o Aluno sem orientador, **When** registra uma ata, **Then** ela fica visível ao Aluno e
   ao Professor da Disciplina; **and** após o aceite do orientador, também a ele.
9. **Given** o Aluno sem sessão, **When** tenta abrir a aba Meu TCC, **Then** vê o login; **and**
   depois abre a seção "Atas de orientação".
10. **Given** a janela de registro, **When** o Aluno escolhe a data de amanhã e salva, **Then** não
    salva e vê "A Data do Encontro não pode ser futura".
11. **Given** a janela de registro, **When** deixa as Metas em branco, **Then** não salva e o campo é
    destacado.
12. **Given** o Orientador comentando, **When** informa 1.001 caracteres, **Then** não salva e vê
    "Informe o comentário com até 1.000 caracteres" (MO-19).
13. **Given** uma ata, **When** o Aluno abre a lista, **Then** vê "Editar", mas não "Comentar".
14. **Given** uma ata, **When** o Professor da Disciplina abre as atas, **Then** não vê "Registrar
    ata", "Editar" nem "Comentar".
15. **Given** a turma arquivada, **When** o Orientador abre as atas, **Then** elas aparecem só para
    consulta.
16. **Given** o convite de coorientação "Aguardando Aceite", **When** o docente procura as atas,
    **Then** o trabalho e as atas não aparecem para ele.

---

### User Story 5 - Orientador indica que o TCC está apto para defesa [US-42] (Priority: P1)

Como Orientador, indico que o TCC do meu orientando está apto para defesa, para que a defesa possa
ser agendada.

**Why this priority**: Must Have (RBN-CAD-11.5); é o gatilho "Indicação de Apto para Defesa" do
Status do TCC e a porta do módulo de Defesa.

**Independent Test**: com um TCC "Em Andamento", a entrega "Documento para Defesa" enviada e Área e
Palavra-Chave preenchidas, indicar Apto e conferir o Status e o histórico.

**Acceptance Scenarios** (cenários 1 a 8 da US-42):

1. **Given** o TCC "Em Andamento", a entrega "Documento para Defesa" Entregue e Área e duas
   Palavras-Chave preenchidas, **When** o Orientador aciona "Apto para Defesa" e "Confirmar", **Then**
   o Status passa a "Apto para Defesa", aparece "TCC indicado como apto para defesa" e o histórico
   registra o Orientador, a data, a hora e o gatilho "Indicação de Apto para Defesa".
2. **Given** o botão disponível, **When** o Orientador aciona e depois "Cancelar", **Then** a
   mensagem fecha e o Status continua "Em Andamento".
3. **Given** o docente Coorientador, **When** abre a tela de orientandos, **Then** a linha não tem o
   botão "Apto para Defesa".
4. **Given** o Orientador sem sessão, **When** tenta abrir "Orientações", **Then** vê o login;
   **and** depois abre a tela de orientandos.
5. **Given** a entrega "Documento para Defesa" Não Entregue, **When** o Orientador abre a tela,
   **Then** o botão está indisponível.
6. **Given** o TCC sem Palavras-Chave, **When** o Orientador abre a tela, **Then** o botão está
   indisponível.
7. **Given** o TCC já "Apto para Defesa", **When** o Orientador abre a tela, **Then** o botão não
   aparece.
8. **Given** a turma sem a entrega "Documento para Defesa" cadastrada, **When** o Orientador abre a
   tela, **Then** o botão está indisponível e aparece "A entrega do tipo Documento para Defesa
   precisa ser cadastrada pelo Professor da Disciplina".

---

### User Story 6 - Aluno registra, substitui ou remove coorientadores [US-45] (Priority: P2)

Como Aluno, registro coorientadores do NUCOMP ou externos e, até o agendamento da defesa, substituo
ou removo, para que a coorientação fique registrada.

**Why this priority**: Should Have na matriz (RBN-CAD-10.3 e 10.7); depende do orientador vinculado.

**Independent Test**: com orientador vinculado, registrar um coorientador do NUCOMP e um externo,
substituir e remover, conferindo os estados e as notificações.

**Acceptance Scenarios** (cenários 1 a 14 da US-45):

1. **Given** o Aluno com orientador, **When** registra um Docente do NUCOMP e salva, **Then** o
   coorientador aparece com "Aguardando Aceite", o docente recebe o convite e o Orientador é
   notificado.
2. **Given** o Aluno com orientador, **When** registra um "Externo ao NUCOMP" com Nome, E-mail e
   Instituição,
   **Then** o coorientador é registrado sem acesso ao sistema e o Orientador é notificado.
3. **Given** "Externo ao NUCOMP" selecionado, **When** preenche só o Nome Completo e salva,
   **Then** o
   coorientador é registrado sem e-mail e sem instituição.
4. **Given** um coorientador já registrado, **When** o Aluno registra outro, **Then** a seção mostra
   os dois.
5. **Given** o convite "Aguardando Aceite", **When** o Aluno aciona "Remover" e confirma, **Then** o
   convite é cancelado e o docente não pode mais aceitá-lo.
6. **Given** o coorientador do NUCOMP X e nenhuma sessão de defesa agendada, **When** o Aluno
   substitui X por Z, **Then** Z é registrado, o vínculo de X vai para o histórico e o Orientador e X
   são notificados.
7. **Given** o coorientador do NUCOMP X, **When** o Aluno o remove e confirma, **Then** X sai da
   seção, perde o acesso ao trabalho e é notificado.
8. **Given** o Aluno sem sessão, **When** tenta abrir a aba Meu TCC, **Then** vê o login; **and**
   depois abre a seção Orientação.
9. **Given** o Aluno sem orientador, **When** abre a seção Orientação, **Then** o botão "Registrar
   coorientador" não aparece.
10. **Given** o docente X já coorientador, **When** o Aluno abre a lista de Docentes do NUCOMP,
    **Then** X não aparece.
11. **Given** "Externo ao NUCOMP" selecionado, **When** deixa o Nome em branco e salva, **Then**
    não salva e o
    Nome Completo é destacado como obrigatório.
12. **Given** a defesa Agendada, **When** o Aluno abre a seção, **Then** "Substituir" e "Remover"
    aparecem desabilitados.
13. **Given** o TCC Desistente, **When** o Aluno abre a seção, **Then** ela aparece só para consulta,
    sem "Registrar coorientador", "Substituir" e "Remover".
14. **Given** a turma arquivada, **When** o Aluno abre a seção em "Turmas arquivadas", **Then** os
    coorientadores aparecem só para consulta, sem os botões.

---

### User Story 7 - Docente aceita ou recusa o convite de coorientação e acompanha o trabalho [US-36] (Priority: P2)

Como Docente do NUCOMP, aceito ou recuso o convite de coorientação e, após o aceite, acompanho o
trabalho na tela de orientandos.

**Why this priority**: Should Have (RBN-CAD-10.4); depende da US-45.

**Independent Test**: com um convite pendente criado por fábrica, aceitar e recusar pela tela
Orientações, conferindo o vínculo, as notificações e a linha com o Papel Coorientador.

**Acceptance Scenarios** (cenários 1 a 11 da US-36):

1. **Given** um convite "Aguardando Aceite", **When** o docente abre "Orientações" e aciona
   "Aceitar", **Then** vira Coorientador, vê "Convite aceito" e o trabalho aparece com o Papel
   Coorientador; **and** o Aluno e o Orientador são notificados.
2. **Given** o e-mail do convite, **When** o docente acessa o link, **Then** abre a tela Orientações
   com o convite na seção "Convites de coorientação".
3. **Given** a notificação do convite no sino, **When** o docente a seleciona, **Then** abre a tela
   Orientações com o convite.
4. **Given** um convite pendente, **When** o docente aciona "Recusar", **Then** sai da lista de
   coorientadores do trabalho, a recusa vai para o histórico e aparece "Convite recusado"; **and** o
   Aluno é notificado e pode indicar outro coorientador.
5. **Given** o docente Coorientador, **When** o Aluno o remove, **Then** o trabalho sai da tela de
   orientandos dele e ele perde o acesso às atas.
6. **Given** um coorientador Externo registrado, **When** o registro é salvo, **Then** nenhum convite
   é enviado.
7. **Given** o docente sem sessão, **When** acessa o link do convite, **Then** vê o login; **and**
   depois abre a tela Orientações com o convite.
8. **Given** o docente Z abre o link de um convite feito a Y, **When** a página carrega, **Then** vê
   "Este convite não está disponível para o seu usuário", sem os botões.
9. **Given** o convite cancelado pelo Aluno, **When** o docente abre o link, **Then** vê "Este
   convite foi cancelado pelo aluno" e não pode aceitar.
10. **Given** o convite já recusado, **When** o docente abre o link de novo, **Then** vê "Recusado",
    com a data e a hora, sem os botões.
11. **Given** o convite "Aguardando Aceite", **When** o docente abre a tela de orientandos, **Then**
    o trabalho não aparece.

---

### User Story 8 - Aluno ou Orientador registra a publicação do artigo [US-46] (Priority: P2)

Como Aluno, registro e atualizo a publicação do artigo do meu TCC (veículo, link ou DOI, Qualis e
status de submissão), para que o Coordenador analise o aproveitamento.

**Why this priority**: Must Have (RBN-CAD-12.1), mas só para a modalidade Artigo Científico.

**Independent Test**: com um TCC na modalidade Artigo Científico, salvar a publicação como Aluno e
como Orientador, conferindo o aproveitamento "Em Análise" com Aceito ou Publicado.

**Acceptance Scenarios** (cenários 1 a 8 da US-46):

1. **Given** o TCC Artigo Científico, **When** o Aluno salva Veículo, Link ou DOI `https://`, Qualis
   B1 e Status Aceito, **Then** o registro é gravado, aparece "Publicação salva" e o aproveitamento
   mostra "Em Análise".
2. **Given** o Orientador na tela de orientandos, **When** aciona "Publicação" na linha do aluno e
   salva, **Then** o registro é gravado no TCC do aluno.
3. **Given** a publicação salva com Status Em Revisão, **When** o Coordenador abre "Aproveitamento de
   artigos", **Then** o artigo não aparece.
4. **Given** o artigo homologado e o resultado ainda não liberado, **When** o Aluno muda o Qualis e
   salva, **Then** a homologação é desfeita e o aproveitamento volta a "Em Análise".
5. **Given** o Aluno sem sessão, **When** tenta abrir a aba Meu TCC, **Then** vê o login; **and**
   depois abre a seção "Publicação do artigo".
6. **Given** a seção Publicação, **When** o Aluno informa um Link ou DOI sem `https://` ou vazio,
   **Then** não salva, o campo é destacado e aparece "O link deve começar com https:// e ter até 500
   caracteres".
7. **Given** a seção Publicação, **When** informa um Veículo com 151 caracteres, **Then** não salva e
   vê "Informe o veículo de publicação com até 150 caracteres" (MO-19).
8. **Given** o TCC Monografia, **When** o Aluno abre a aba Meu TCC, **Then** a seção "Publicação do
   artigo" não aparece.

---

### User Story 9 - Coordenador de Curso homologa ou recusa o aproveitamento do artigo [US-20] (Priority: P2)

Como Coordenador de Curso, analiso os artigos Aceitos ou Publicados dos alunos do meu curso e
homologo ou recuso o aproveitamento, para que o artigo homologado em Qualis A ou B garanta a nota
mínima do TCC.

**Why this priority**: Must Have (RBN-CAD-12.2 e 12.3); depende da US-46. O efeito na nota é
aplicado pela feature de Avaliação (US-27).

**Independent Test**: com artigos Aceitos de dois cursos, abrir a tela como Coordenador de um deles,
homologar e recusar, conferindo o filtro e os botões.

**Acceptance Scenarios** (cenários 1 a 9 da US-20):

1. **Given** um artigo Qualis A2 Publicado, **When** o Coordenador abre o link, confere e aciona
   "Homologar", **Then** o aproveitamento passa a "Homologado" e aparece "Aproveitamento
   homologado"; na liberação do resultado, a nota final mínima é 6,0 (aplicada pela US-27).
2. **Given** um artigo "Em Análise", **When** o Coordenador aciona "Recusar", **Then** passa a
   "Recusado", aparece "Aproveitamento recusado" e não há nota mínima.
3. **Given** um artigo homologado com Qualis C, **When** o resultado é liberado, **Then** vale a
   nota da banca, sem nota mínima garantida.
4. **Given** um artigo Homologado e o resultado ainda não liberado, **When** o Coordenador aciona
   "Recusar", **Then** passa a "Recusado".
5. **Given** um artigo homologado cujo Qualis o Aluno alterou, **When** o Coordenador abre a tela,
   **Then** o artigo aparece "Em Análise".
6. **Given** o Coordenador sem sessão, **When** tenta abrir a tela, **Then** vê o login; **and**
   depois abre "Aproveitamento de artigos".
7. **Given** o Coordenador de Engenharia de Computação, **When** escolhe Sistemas de Informação no
   filtro, **Then** vê os artigos desse curso sem "Homologar" e "Recusar".
8. **Given** o resultado liberado com o artigo Homologado, **When** o Coordenador abre a tela,
   **Then** "Recusar" está indisponível nesse artigo.
9. **Given** um Docente que não é Coordenador, **When** abre o menu, **Then** o item "Aproveitamento
   de artigos" não aparece.

Pontos de contato acrescentados na revisão (Clarifications Q16, que substitui a Q8):

10. **Given** o resultado liberado e o artigo "Em Análise" (alterado depois da liberação), **When**
    o Coordenador abre a tela, **Then** o artigo aparece com "Homologar" e "Recusar" (só a recusa de
    artigo Homologado fica indisponível, US-20 E3).
11. **Given** o resultado liberado e o artigo Homologado, **When** o Aluno muda o Qualis e salva,
    **Then** a publicação é gravada, o aproveitamento volta a "Em Análise" e a nota já liberada não
    muda (RBN-DEF-06.4).

---

### Edge Cases

- **Orientador automático e troca**: em turma de TCC 2 de Engenharia de Computação ou de
  Licenciatura em Computação, o aluno não indica nem troca orientador; a troca é a transferência de
  turma da spec 004 (US-17 F; RBN-CAD-10.6). Esses orientandos aparecem na tela de orientandos do
  professor como os demais (US-18 G).
- **Novo orientador que era coorientador**: no aceite da troca, a coorientação dele no mesmo
  trabalho é encerrada (US-17 D, US-18 E; RBN-CAD-10.6). O mesmo docente nunca é Orientador e
  Coorientador do mesmo trabalho, e não aparece na lista de coorientadores possíveis.
- **Coorientador externo com e-mail já cadastrado em outro trabalho**: o registro do coorientador
  externo é reaproveitado sem alterar Nome e Instituição (dicionário 3.2.6, `cext_email` único;
  Clarifications D9); no mesmo trabalho, o e-mail
  repetido é recusado com "Este e-mail já está registrado como coorientador" (US-45 E3).
- **Pedido ou convite cancelado pelo encerramento da participação** (spec 004, Q-40): aparece como
  "Cancelado"; pelo link, MO-12 (texto de pedido ou de convite), com o motivo deduzido pelo FR-050.
- **Docente inativado** (spec 002): não aparece nas listas de escolha, mas continua nos registros
  antigos; aceitar um pedido ou convite com a conta já 'Inativa' é recusado (Q-68). O pedido
  pendente a esse docente continua pendente até o aluno cancelar (Clarifications D13).
- **Atas com o mesmo dia**: na mesma Data do Encontro, a mais recente é a última registrada
  (Clarifications D14).
- **Aluno aprovado em TCC 1 e copiado para o TCC 2** (spec 004; Clarifications Q6; FR-051): a
  publicação vai para o TCC 2 com o aproveitamento já decidido, e a orientação não automática e as
  coorientações ativas também; as atas ficam no TCC 1 e aparecem só para consulta na lista do TCC 2;
  os pedidos e convites pendentes do TCC 1 são cancelados (MO-18) e o TCC 1 fica só para consulta.
  Em turma com orientador automático, a orientação do TCC 2 segue a turma de destino.
- **Convite pendente ao docente que passa a ser o orientador** (troca aceita ou transferência): o
  convite é cancelado (MO-17), como a spec 004 já faz na transferência (Clarifications D13).
- **Mudança de modalidade com publicação registrada** (RBN-CAD-08.2): em Monografia, a seção some e
  o artigo sai da tela do Coordenador, sem apagar o registro; de volta a Artigo Científico, ele
  reaparece (Clarifications D10).
- **Participação encerrada** (RBN-CAD-08.5): orientação, atas e publicação ficam só para consulta do
  Aluno; o vínculo de orientação é encerrado (spec 004) e o trabalho sai da tela de orientandos
  (Clarifications D5).
- **Publicação alterada depois da liberação do resultado**: a alteração desfaz a decisão e o artigo
  volta a "Em Análise", como antes da liberação; a nota já liberada não muda (Clarifications Q16).
- **Turma arquivada com pedidos ou convites pendentes** (TCC "Sem Proposta" ou já aprovado): o
  arquivamento cancela os pendentes e avisa cada docente (FR-053; MO-26; Clarifications Q17).

## Requirements *(mandatory)*

### Functional Requirements — Indicação, cancelamento e troca de orientador (US-17)

- **FR-001** [RBN-CAD-10.1]: Na aba Meu TCC, seção Orientação, o sistema MUST mostrar ao Aluno de
  turma não arquivada, com participação não encerrada e sem orientador ativo nem pedido pendente,
  "Sem orientador", a lista "Indicar orientador" e o botão "Enviar pedido", com ou sem Proposta;
  com orientador, a seção MUST mostrar o nome do Orientador atual (US-17 passo 7).
- **FR-002** [RBN-CAD-10.1; Q-68]: A lista MUST conter todos os Docentes com o Status da Conta
  'Ativa', de qualquer curso do NUCOMP, cada opção com nome, titulação e curso; o envio MUST travar
  e reconferir a conta do docente na mesma gravação.
- **FR-003** [RBN-CAD-10.1]: Ao enviar, o sistema MUST registrar o pedido "Aguardando Resposta"
  (um pedido pendente por TCC), bloquear a lista, exibir "Pedido enviado a [nome do docente].
  Aguardando resposta" e o botão "Cancelar Pedido", e enviar ao docente e-mail e notificação no
  sistema com o nome do aluno, o título (ou "Proposta ainda não registrada") e o link do pedido
  (MO-01).
- **FR-004** [RBN-CAD-10.1]: Enquanto pendente, o Aluno MUST poder cancelar o pedido ("Cancelado"),
  e a lista MUST voltar a ficar disponível.
- **FR-005** [RBN-CAD-10.6]: Com o Status "Em Andamento" ou "Apto para Defesa" e sem sessão de
  defesa Agendada, Reagendada ou Em Andamento, a seção MUST mostrar a lista "Trocar de orientador"
  (sem o orientador atual) e o botão "Enviar pedido", registrando um pedido do tipo Troca de
  Orientação; fora dessas condições, a lista MUST aparecer desabilitada (E3).
- **FR-006** [RBN-CAD-10.6; RBN-CAD-04.2]: Em turma com orientador automático, a seção MUST mostrar o
  professor da turma como Orientador, sem as listas de indicar e trocar.
- **FR-007** [RBN-CAD-08.5; RBN-CAD-04.5; Clarifications D5, Q6]: Com a participação encerrada, a
  turma arquivada ou o TCC já copiado para o TCC 2, as seções Orientação, Atas de orientação e
  Publicação do artigo MUST ficar só para consulta, sem indicar, trocar, cancelar, registrar, editar
  nem salvar.
- **FR-008** [RBN-CAD-10.6]: O sistema MUST oferecer à feature de Agendamento (US-24) um serviço que,
  ao confirmar o agendamento, cancela o pedido de troca pendente do TCC, mantém o orientador atual
  e avisa o Aluno e o docente (MO-06).

### Functional Requirements — Resposta ao pedido e tela de orientandos (US-18)

- **FR-009** [RBN-CAD-10.2]: A tela "Orientações" MUST mostrar ao docente, no topo, a seção "Pedidos
  de orientação" com uma linha por pedido "Aguardando Resposta" feito a ele: nome do aluno, título
  (ou "Proposta ainda não registrada"), turma, data e hora, orientador atual (só no pedido de
  troca) e os botões "Ver proposta" (só com Proposta salva), "Recusar" e "Aceitar".
- **FR-010** [RBN-CAD-10.2; RAN-CAD-10 NFR Não Repúdio]: "Aceitar" MUST registrar o aceite com o
  docente, a data e a hora, vincular o docente como Orientador (origem "Pedido Aceito"), marcar o
  pedido "Aceito", notificar o Aluno no sistema e o Professor da Disciplina por e-mail e no sistema
  (MO-02, MO-04) e exibir "Pedido aceito. O aluno foi incluído na sua tela de orientandos" (MO-15,
  Clarifications Q3). No pedido de
  troca, MUST encerrar o vínculo anterior (histórico), notificar o orientador anterior (MO-05) e
  encerrar a coorientação de quem aceita, se houver.
- **FR-011** [RBN-CAD-10.2]: "Recusar" MUST registrar a recusa com o docente, a data e a hora,
  notificar o Aluno (MO-03), liberar a lista "Indicar orientador" e exibir "Pedido recusado"; no
  pedido de troca, o orientador atual MUST ser mantido.
- **FR-012** [RBN-CAD-10.1; RBN-CAD-10.6; Clarifications Q7, D1]: O link do pedido (e-mail e
  notificação) MUST abrir a tela Orientações com o pedido destacado. Quando o pedido não pode mais
  ser respondido, a tela MUST mostrar no topo, como aviso, o estado do pedido, sem "Aceitar" e
  "Recusar", e o resto da tela normalmente: se quem abre não é o docente indicado, "Este pedido não
  está disponível para o seu usuário"; se cancelado, o texto do motivo deduzido pelo FR-050 (pelo
  aluno, "Este pedido foi cancelado pelo aluno"; pelo agendamento, "Este pedido foi cancelado porque
  a defesa foi agendada"; pelo encerramento da participação, a MO-12; pela cópia para o TCC 2, a
  MO-18; pelo arquivamento da turma, a MO-26); se já respondido, a decisão ("Aceito" ou "Recusado") com a data e a hora. Esses textos
  valem no lugar do aviso genérico de item indisponível da spec 003 (índice Q-12). Quem não é
  Docente MUST receber acesso negado (M-02). Responder a um pedido que mudou de estado ao mesmo
  tempo MUST ser recusado no servidor, mostrando o estado atual.
- **FR-013** [RBN-CAD-10.2; RAN-CAD-07 NFR]: "Ver proposta" MUST mostrar Título, Subtítulo, Resumo,
  Modalidade e Link do Documento da Proposta só para leitura, com o Resumo liberado por
  `pode_ver_resumo` (spec 005, FR-007a), que MUST liberar o Resumo ao docente de um pedido
  pendente de Orientação **ou de Troca de Orientação** (hoje só o de Orientação: correção na spec
  005).
- **FR-014** [RBN-CAD-11.4]: Abaixo, a tela de orientandos MUST listar, só para leitura, os trabalhos
  em que o docente é Orientador (vínculo ativo, por pedido ou automático) ou Coorientador
  (coorientação aceita e ativa): Nome do Aluno, Curso, Turma, Título, Modalidade, Papel, Status do
  TCC e status de envio das entregas; os de turma arquivada MUST aparecer no fim, só com acesso às
  atas. Vínculos encerrados (troca, transferência, encerramento da participação, remoção e o vínculo
  do TCC 1 depois da cópia para o TCC 2) MUST sair da tela (Clarifications D4 a D6). "Só para
  leitura" vale para os dados da linha; as ações são as do FR-015.
- **FR-015** [RBN-CAD-11.4; US-18 passo 7]: Na linha com o Papel Orientador, MUST haver as ações
  "Atas" e "Registrar ata" (US-19), "Histórico do Status do TCC" (US-14, fluxo A; nome provisório,
  Q-81), "Publicação" (só Artigo Científico, US-46), "Apto para Defesa" (US-42) e "Correções
  Conferidas" (FR-016); na linha com o Papel Coorientador, só "Atas" e "Registrar ata".
- **FR-016** [RBN-CAD-09.5; FR-029 da spec 005]: Em TCC 2 de Sistemas de Informação com o Status
  "Aprovado com Correções", a linha do Orientador MUST ter o botão "Correções Conferidas", sem
  campos, com confirmação (MO-13); confirmar MUST gravar `ent_correcoes_conferidas_em` na entrega
  Versão Final do aluno e liberar o botão Homologar ao Professor da Disciplina (spec 005). O botão
  MUST aparecer só depois do envio da Versão Final (Entregue ou Entregue com Atraso) e enquanto não
  houver conferência; a devolução para ajuste (US-44 D, spec 005) MUST apagar a conferência, que é
  feita de novo depois do reenvio (Clarifications Q2). Depois da confirmação, a linha MUST mostrar
  "Correções conferidas em DD/MM/AAAA HH:MM" (MO-13) no lugar do botão.

### Functional Requirements — Alunos da turma e painel do aluno (US-41)

- **FR-017** [RBN-CAD-10.5; RBN-CAD-08.9; RBN-CAD-05.6; Clarifications Q1, Q4]: A aba "Alunos" da
  tela da turma (spec 004) MUST mostrar um bloco por aluno, somente leitura, com Nome, Matrícula,
  Curso, Título (ou "Sem Proposta"), Área de Interesse, Orientador (ou "Sem orientador") e Status do
  TCC; para o Professor da Disciplina, o bloco MUST abrir o painel do aluno, e as ações sobre o aluno
  MUST ficar só no painel (FR-019). A Secretaria do curso MUST ver os blocos só para consulta, sem
  abrir o painel, com o botão "Transferir aluno" no bloco quando a transferência for permitida
  (RBN-CAD-05.6; US-08 D; US-07 E8). As ações da turma ("Matricular alunos", "Excluídos ou
  transferidos", editar, arquivar e excluir a turma) não mudam.
- **FR-018** [RBN-CAD-08.9; US-44 passo 3; Clarifications D2, D12]: O painel do aluno MUST reunir,
  só para leitura, as seções Proposta e TCC (Resumo por `pode_ver_resumo`), Orientação e
  coorientação (com o histórico do FR-049), Entregas (status e link mais recente, spec 005), Atas
  (US-19 F), Publicação (só em Artigo Científico), Defesa (MO-23 até o módulo de Defesa) e Versão
  Final, e o botão "Fechar", que volta à aba "Alunos".
- **FR-019** [RBN-CAD-08.9; RBN-CAD-05.3; US-41 passo 4; Clarifications Q1, Q5, D12]: O painel MUST
  oferecer ao Professor da Disciplina de turma não arquivada os botões de ação da US-41: "Excluir
  aluno" e "Encerrar participação" (US-09), "Transferir aluno" (US-08), "Resetar primeiro acesso"
  (US-12, spec 003, só quando `pode_resetar_primeiro_acesso`) e, na seção Versão Final, "Homologar" e
  "Devolver para Ajuste" (US-44, spec 005); e também "Editar" os dados do aluno (US-08 C; Q5) e o
  link "Histórico do Status do TCC" (US-14 B; spec 005), cada um só quando a regra da sua spec
  permitir. Com a turma arquivada, nenhum botão de ação; o link de histórico continua.
- **FR-020** [RBN-CAD-08.9]: O painel MUST ser acessível só ao Professor da Disciplina da turma do
  aluno; outro Docente, a Secretaria e o Aluno MUST receber acesso negado (M-02).

### Functional Requirements — Atas de orientação (US-19)

- **FR-021** [RBN-CAD-11.1; US-19 passo 3]: A janela "Registrar ata de orientação" MUST ter Data do
  Encontro (calendário, DD/MM/AAAA, obrigatória, não futura — "A Data do Encontro não pode ser
  futura"), Pauta Discutida e Metas Acordadas (obrigatórias, até 2.000 caracteres cada) e os botões
  "Cancelar" e "Salvar"; campo em branco MUST ser destacado e texto acima do limite MUST mostrar a
  MO-19.
- **FR-022** [RBN-CAD-11.1]: A ata MUST poder ser registrada pelo Aluno (aba Meu TCC, seção "Atas de
  orientação", com a quantidade de encontros e os botões "Registrar ata" e "Ver atas"), pelo
  Orientador e pelo Coorientador com coorientação aceita (linha da tela de orientandos), exibindo
  "Ata registrada"; registrar e editar MUST exigir as condições do FR-007.
- **FR-023** [RBN-CAD-11.2]: A lista de atas MUST mostrar, da mais recente para a mais antiga, Data do
  Encontro, Pauta, Metas e os comentários (autor, data e hora), visível ao Aluno, ao Orientador
  atual, ao Coorientador com coorientação aceita e ativa e ao Professor da Disciplina da turma; atas
  registradas antes do vínculo passam a ser visíveis ao orientador ou coorientador depois dele, e
  quem perde o vínculo perde o acesso (Clarifications D4). No TCC 2, as atas do TCC 1 do mesmo aluno
  MUST aparecer abaixo, só para consulta, identificadas pela turma de TCC 1 (Q6).
- **FR-024** [RBN-CAD-11.2]: Aluno, Orientador e Coorientador MUST poder editar a ata (mesmas
  regras); Orientador e Coorientador MUST poder comentar (até 1.000 caracteres, com a MO-19 acima
  do limite); o Aluno MUST NOT
  ver "Comentar"; o Professor da Disciplina só consulta.
- **FR-025** [RBN-CAD-11.2; RBN-CAD-04.5]: Com a turma arquivada, as atas MUST ficar só para
  consulta; o docente com convite de coorientação pendente MUST NOT ver o trabalho nem as atas.

### Functional Requirements — Apto para Defesa (US-42)

- **FR-026** [RBN-CAD-11.5]: O botão "Apto para Defesa" MUST aparecer só na linha do Orientador e só
  com o Status "Em Andamento"; MUST ficar habilitado só com a entrega "Documento para Defesa" do
  aluno Entregue ou Entregue com Atraso e com Área de Interesse e ao menos uma Palavra-Chave; sem a
  entrega cadastrada na turma, MUST ficar indisponível e informar "A entrega do tipo Documento para
  Defesa precisa ser cadastrada pelo Professor da Disciplina".
- **FR-027** [RBN-CAD-11.5; RBN-CAD-08.3]: O botão MUST pedir confirmação "Confirmar que o TCC de
  [nome do aluno] está apto para defesa?" (Cancelar não altera nada); confirmar MUST mudar o Status
  para "Apto para Defesa" pelo serviço único da spec 005 (gatilho "Indicação de Apto para Defesa",
  Orientador como responsável), conferindo as condições de novo com turma, aluno e TCC travados, e
  exibir "TCC indicado como apto para defesa"; se as condições não valem mais, MUST recusar com a
  MO-20, sem mudar o Status. Depois da indicação, a linha MUST mostrar a etiqueta "Apto para
  Defesa" no lugar do botão (US-42 passo 7).

### Functional Requirements — Coorientadores (US-45)

- **FR-028** [RBN-CAD-10.3; Q-68]: Com orientador vinculado, turma não arquivada e participação não
  encerrada, a seção Orientação MUST mostrar os coorientadores (com "Aguardando Aceite" no convite
  pendente) e o botão "Registrar coorientador"; o tipo Docente do NUCOMP MUST listar só docentes
  'Ativa' que não sejam o orientador, coorientadores já registrados nem docentes com convite
  pendente no trabalho (Clarifications D8), e enviar convite (MO-07); o tipo "Externo ao NUCOMP" MUST
  pedir Nome Completo (obrigatório, só letras, acentos e espaços, até 150), E-mail
  (opcional, nome@domínio, até 100) e Instituição de Origem (opcional, até 150), sem convite e sem
  acesso; e-mail repetido no trabalho MUST ser recusado com "Este e-mail já está registrado como
  coorientador"; um e-mail já cadastrado em outro trabalho MUST reaproveitar o registro existente
  sem alterar Nome e Instituição e avisar o aluno com a MO-25 (Clarifications Q13). Cada registro MUST notificar o Orientador
  (MO-08); não há limite de quantidade.
- **FR-029** [RBN-CAD-10.4]: "Remover" num convite pendente MUST cancelá-lo após confirmação (MO-14),
  ('Cancelado'), sem que o docente possa mais aceitar; depois, a tela volta à seção Orientação.
- **FR-030** [RBN-CAD-10.7; Clarifications D8]: Sem sessão de defesa Agendada, Reagendada ou Em
  Andamento, "Substituir" (que abre a mesma janela do registro, US-45 D) e "Remover" (com
  confirmação, MO-14) MUST registrar o vínculo anterior no histórico ('Substituída' ou 'Encerrada'), notificar o Orientador e, se docente do
  NUCOMP, o próprio coorientador (MO-09), que perde o acesso ao trabalho; com sessão, os botões MUST
  aparecer desabilitados. Sem orientador, o botão "Registrar coorientador" MUST NOT aparecer.

### Functional Requirements — Convite de coorientação (US-36)

- **FR-031** [RBN-CAD-10.4]: A tela Orientações MUST ter a seção "Convites de coorientação" com uma
  linha por convite pendente: aluno, título, turma, Orientador e os botões "Recusar" e "Aceitar".
- **FR-032** [RBN-CAD-10.4; RAN-CAD-10 NFR]: "Aceitar" MUST registrar o aceite (docente, data e hora),
  vincular o Coorientador, notificar Aluno e Orientador (MO-10), exibir "Convite aceito" e incluir o
  trabalho na tela de orientandos com o Papel Coorientador; "Recusar" MUST registrar a recusa no
  histórico, notificar o Aluno (MO-11) e exibir "Convite recusado".
- **FR-033** [RBN-CAD-10.4]: O link do convite MUST seguir as mesmas regras do FR-012, com "Este
  convite não está disponível para o seu usuário", "Este convite foi cancelado pelo aluno", os
  demais motivos do FR-050 na forma de convite (MO-12, MO-17, MO-18, MO-26) e a decisão registrada. O
  e-mail e a notificação do convite MUST trazer os botões "Aceitar" e "Recusar" como links que abrem
  a tela Orientações com o convite destacado, sem resposta pelo e-mail; a resposta é dada na tela,
  depois do login (RBN-CAD-10.4; US-36; Clarifications Q14).

### Functional Requirements — Publicação do artigo (US-46)

- **FR-034** [RBN-CAD-12.1; Clarifications D10]: Só na modalidade Artigo Científico, a aba Meu TCC
  MUST ter a seção "Publicação do artigo" com a etiqueta de aproveitamento (MO-22 enquanto não houver
  análise), os campos Veículo de Publicação (opcional, até 150; MO-19 acima do limite), Link ou DOI
  (obrigatório, `https://`, até 500 — "O link deve começar com https:// e ter até 500 caracteres"),
  Estrato Qualis/CAPES (opcional: A1 a A4, B1 a B4, C) e Status de Submissão (opcional: Submetido, Em
  Revisão, Aceito, Publicado, Rejeitado) e o botão "Salvar publicação", um registro por TCC,
  exibindo "Publicação salva"; salvar MUST exigir as condições do FR-007.
- **FR-035** [RBN-CAD-12.1; US-46 A]: O Orientador MUST poder registrar e atualizar a publicação pelo
  link "Publicação" na tela de orientandos, que abre a seção "Publicação do artigo" do orientando
  numa tela própria do Orientador, com as mesmas regras e o botão "Voltar" para a tela de
  orientandos.
- **FR-036** [RBN-CAD-12.1; RBN-CAD-12.3; dicionário 3.5.7; Clarifications Q16]: Com Status Aceito
  ou Publicado, o aproveitamento MUST passar a "Em Análise" e o artigo entrar na tela do
  Coordenador; alterar Qualis, Status ou Link de um artigo já analisado MUST desfazer a decisão e
  voltar a "Em Análise", antes ou depois da liberação do resultado (US-46 C; US-20 D); a nota já
  liberada não muda (RBN-DEF-06.4).

### Functional Requirements — Aproveitamento do artigo (US-20)

- **FR-037** [RBN-CAD-12.2; RBN-CAD-14.1; Clarifications Q6, D10, D11]: A tela "Aproveitamento de
  artigos" MUST listar os artigos Aceitos ou Publicados dos TCCs na modalidade Artigo Científico, só
  do TCC atual de cada aluno (sem repetir o TCC 1 copiado), com Aluno, Orientador, Título, Veículo,
  Qualis, o link "abrir" e o aproveitamento, com o filtro Curso (os 3 cursos e Todos, pelo curso da
  turma do TCC) iniciando no curso do Coordenador.
- **FR-038** [RBN-CAD-12.3; RAN-CAD-12 NFR]: Nos artigos do curso que coordena, o Coordenador MUST
  poder "Homologar" ("Aproveitamento homologado") e "Recusar" ("Aproveitamento recusado"), com
  autor, data e hora (também no log de eventos, Clarifications D10); até a liberação do resultado,
  MUST poder recusar um artigo já homologado; depois dela, "Recusar" MUST ficar indisponível no
  artigo Homologado, e a recusa pelo endereço direto MUST ser recusada com a MO-21 (US-20 C e E3;
  Clarifications Q16); nos artigos de outros cursos, só consulta.
- **FR-039** [RBN-CAD-12.3]: O sistema MUST oferecer à feature de Avaliação (US-27) a consulta "o
  TCC tem artigo homologado em Qualis A ou B" (nota final mínima 6,0 em TCC 1 e TCC 2), sem aplicar
  a nota nesta spec; a apresentação perante a banca continua obrigatória (RBN-CAD-12.3).

### Functional Requirements — Navegação até cada tela (pedido da descrição; lição da Q-89)

- **FR-040**: O sistema MUST oferecer o item de menu **"Orientações"** a todo Docente, abrindo a tela
  com "Pedidos de orientação", "Convites de coorientação" e a tela de orientandos; os links de
  e-mail e as notificações de pedido e convite MUST abrir essa mesma tela; o destino de cada
  notificação está no FR-052. O item MUST aparecer mesmo sem pedidos, convites ou orientandos; nesse
  caso, cada seção vazia MUST mostrar o aviso da MO-24 (Clarifications Q11).
- **FR-041**: O sistema MUST oferecer o item de menu **"Aproveitamento de artigos"**, na seção
  "Gestão" (seção nova do menu), só ao Coordenador de Curso (US-20 E4).
- **FR-042** [Clarifications D1]: As seções **Orientação**, **Atas de orientação** e **Publicação do
  artigo** MUST ficar dentro da aba "Meu TCC" do Aluno (item "Turmas" do Aluno → turma → "Meu TCC",
  spec 005, FR-031), cada uma com endereço próprio de seção, para que o link e o login (E1) abram a
  aba já na seção certa. Para o Aluno: "Registrar ata" abre a janela do FR-021, e "Cancelar" ou
  "Salvar" voltam à seção Atas de orientação; "Ver atas" abre a lista de atas, com o botão "Voltar"
  para a seção; "Registrar coorientador" e "Substituir" abrem a mesma janela, e "Cancelar" ou
  "Salvar" voltam à seção Orientação; a confirmação de "Remover" volta à seção Orientação. Na lista
  de atas, "Editar" abre a ata no mesmo formulário e "Comentar" abre o campo de comentário abaixo da
  ata; os dois voltam à lista. Turma arquivada: pelo botão "Turmas arquivadas" que as specs 004 e
  005 já oferecem na tela Turmas (a US o chama de item de menu, que não é criado).
- **FR-043** [US-14 A]: Na tela de orientandos, cada ação da linha (Atas, Registrar ata, Histórico do
  Status do TCC, Publicação, Apto para Defesa, Correções Conferidas) MUST abrir a sua tela ou
  confirmação a partir da própria linha, voltando à tela de orientandos ao terminar, cancelar ou
  fechar. A tela de histórico do Status (spec 005) MUST abrir também ao Orientador atual do TCC e ter
  o botão "Fechar", que volta à tela de origem (tela de orientandos ou painel do aluno).
- **FR-044** [US-41 C; Clarifications D3]: O painel do aluno MUST abrir pelo bloco do aluno na aba
  "Alunos" da tela da turma (item "Turmas" → turma, ou "Turmas arquivadas" → turma); a lista de atas
  desta spec e as telas de ação das specs 003 a 005 MUST abrir a partir do painel; "Editar",
  "Encerrar participação", "Resetar primeiro acesso", "Homologar", "Devolver para Ajuste", o
  histórico do Status e a lista de atas MUST voltar ao painel ao terminar, cancelar ou fechar;
  "Excluir aluno" e "Transferir aluno", depois de confirmados, MUST voltar à aba "Alunos" (o aluno
  sai da turma) e, cancelados, ao painel; "Fechar" MUST voltar à aba "Alunos". A tela mínima de
  reset da spec 003 MUST ser retirada, e o seu endereço MUST abrir o painel do aluno na turma mais
  recente do aluno em que quem abre é o Professor da Disciplina; sem essa turma, acesso negado
  (M-02) (Clarifications Q12).
- **FR-045**: Nenhuma tela desta spec MUST depender de endereço digitado para ser alcançada; o roteiro
  manual (quickstart) MUST percorrer cada uma pela navegação.

### Functional Requirements — Regras transversais

- **FR-046** [Q27 da spec 003; Clarifications D11]: Ações que alteram dados (pedido, convite,
  aceite, recusa, ata, comentário, coorientador, publicação, Apto para Defesa, Correções Conferidas)
  MUST ser recusadas com a turma arquivada (MT-25), com a participação encerrada ou com o TCC já
  copiado para o TCC 2 (FR-007), e reconferidas no servidor, mesmo pelo endereço direto; consultas
  valem com turma ativa ou arquivada. As decisões do Coordenador seguem a regra da liberação do
  resultado (FR-038), e não a de turma arquivada.
- **FR-047** [RAN-CAD-10 NFR; Q-68]: O aluno MUST ter no máximo um orientador ativo e um pedido de
  orientação pendente; criar pedido, convite, orientação ou coorientação MUST travar e reconferir a
  conta 'Ativa' do docente (spec 002) e a turma, na mesma gravação.
- **FR-048** [constituição VI; SC-003]: Mensagens exibidas MUST ser o texto exato das US ou estar na
  tabela "Mensagens a validar com a PO" (MO-xx).

### Functional Requirements — Acrescentados na revisão de 2026-10-24

- **FR-049** [RAN-CAD-10 NFR; US-17 D; US-18 E; US-36 C; Clarifications D2]: A seção Orientação da
  aba Meu TCC e a seção Orientação e coorientação do painel MUST mostrar, quando houver, o histórico
  de orientação: orientadores e coorientadores anteriores (origem, datas de início e de fim e estado
  'Encerrada' ou 'Substituída') e os pedidos e convites recusados ou cancelados, com a data.
- **FR-050** [RBN-CAD-10.6; Clarifications Q7, D13]: Todo cancelamento automático de pedido ou
  convite MUST gravar em `sol_data_resposta` a mesma data e hora registradas pelo evento que o
  causou, na mesma gravação, e o motivo MUST ser deduzido nesta ordem, sem coluna nova: (1) evento
  "Agendamento" do histórico da defesa do TCC com essa data e hora → agendamento (só no pedido de
  Troca de Orientação); (2) gatilho "Encerramento da participação" no histórico do Status do TCC →
  encerramento (MO-12); (3) início de um vínculo de orientação do mesmo docente no TCC (troca aceita
  ou transferência) → o docente passou a ser o orientador (MO-17, só no convite); (4) gatilho
  "Transferência para TCC 2" no histórico do novo TCC do aluno → cópia para o TCC 2 (MO-18); (5)
  notificação MO-26 ao docente da solicitação, com o link dessa solicitação e essa data e hora,
  gravada pelo arquivamento da turma → turma arquivada (MO-26; FR-053; Clarifications Q17); (6) sem
  evento coincidente → cancelado pelo aluno (o pedido que o aluno cancelou antes do arquivamento
  continua "cancelado pelo aluno", como nas US-18 E3 e US-36 E3).
- **FR-051** [RBN-CAD-08.6; RBN-CAD-12.3; Clarifications Q6]: Na cópia para o TCC 2 (spec 004), o
  sistema MUST levar o registro de publicação com o aproveitamento já decidido, a orientação não
  automática e as coorientações ativas; MUST cancelar os pedidos e convites pendentes do TCC 1,
  avisando cada docente (MO-18); e MUST deixar o TCC 1 só para consulta. No TCC 2, a regra da
  liberação (FR-038) considera a liberação do resultado do TCC 2.
- **FR-052** [Clarifications D1, Q18]: Cada notificação desta spec MUST levar a uma tela: ao Aluno
  (MO-02, MO-03, MO-06, MO-10, MO-11), à aba Meu TCC, seção Orientação; ao docente indicado ou
  convidado (MO-01, MO-07, MO-16), à tela Orientações com o pedido ou convite (FR-012); ao
  Orientador e aos demais docentes avisados (MO-05, MO-06, MO-08, MO-09, MO-10, MO-18), à tela
  Orientações; ao docente do pedido ou convite cancelado pelo arquivamento (MO-26), à tela
  Orientações com esse pedido ou convite (FR-012, FR-033); ao Professor da Disciplina (MO-04), ao painel do aluno. O encerramento da
  participação e a transferência continuam avisando os docentes pelas notificações da spec 004
  (MT-31 e MT-22); a MO-12 e a MO-17 são só o texto exibido pelo link do pedido ou convite cancelado.
- **FR-053** [RBN-CAD-04.5; Clarifications Q17]: Ao arquivar a turma (spec 004, US-07), o sistema
  MUST cancelar, na mesma gravação, os pedidos e convites pendentes dos TCCs da turma, com a mesma
  data e hora em todos, e avisar no sistema, na mesma gravação e com essa data e hora, o docente de
  cada pedido ou convite (MO-26), com o link desse pedido ou convite (FR-012, FR-033).

### Key Entities *(reaproveitadas da spec 001; nenhuma nova)*

- **Solicitacoes_Orientacao**: pedido de Orientação ou de Troca de Orientação (Aguardando Resposta,
  Aceito, Recusado, Cancelado) e convite de Coorientação (Aguardando Aceite, Aceito, Recusado,
  Cancelado), com docente, datas de envio e de resposta; o motivo do cancelamento é deduzido pelo
  FR-050.
- **Orientacoes**: vínculo de orientação (origem Pedido Aceito ou Automático; Ativa ou Encerrada,
  com datas) — o histórico de trocas.
- **Coorientacoes** e **CoorientadoresExternos**: coorientação aceita (docente) ou registrada
  (externo), Ativa, Substituída (no "Substituir") ou Encerrada (no "Remover", na troca de
  orientador, na transferência e no encerramento), com datas.
- **Encontro_Orientacao** e **Comentarios_Encontro**: ata (data, pauta, metas) e comentários (autor,
  texto, data e hora).
- **Artigos**: publicação do TCC (veículo, link ou DOI, Qualis, status) e aproveitamento (estado,
  autor e data da decisão).
- **Entregas_Marcos.ent_correcoes_conferidas_em**: data e hora das "Correções Conferidas".

## Mensagens a validar com a PO

Textos exibidos ao usuário sem texto exato nas US — **PROVISÓRIOS**, pela convenção das specs 003
a 005. Todos os textos entre aspas nos FR acima são cópia exata das US.

| ID | Uso | Texto proposto (PROVISÓRIO) | Origem | Situação |
|---|---|---|---|---|
| MO-01 | Notificação e e-mail ao docente indicado (assunto do e-mail: "SIGTCC: pedido de orientação") | "{nome} pediu a sua orientação. TCC: {titulo}." ({titulo} é o título ou "Proposta ainda não registrada") | US-17 passo 5 (sem texto exato); revisão P20 | A validar |
| MO-02 | Notificação ao Aluno: pedido aceito | "{docente} aceitou ser o seu orientador." | US-17 passo 6; US-18 passo 5 | A validar |
| MO-03 | Notificação ao Aluno: pedido recusado | "{docente} recusou o seu pedido de orientação." | US-17 B; US-18 D | A validar |
| MO-04 | Notificação e e-mail ao Professor da Disciplina: aceite (assunto: "SIGTCC: orientação aceita") | "{docente} passou a orientar {nome} na turma {identificador}." | US-18 passo 5; RBN-CAD-10.2 | A validar |
| MO-05 | Notificação ao orientador anterior na troca | "{nome} trocou de orientador; a orientação passou a {docente}." | US-17 D; US-18 E | A validar |
| MO-06 | Aviso ao Aluno e ao docente: troca cancelada pelo agendamento | Ao Aluno: "O seu pedido de troca de orientador foi cancelado porque a defesa foi agendada." / Ao docente: "O pedido de troca de orientador de {nome} foi cancelado porque a defesa foi agendada." | US-17 E; US-18 E4 | A validar |
| MO-07 | Notificação e e-mail ao docente convidado (assunto: "SIGTCC: convite de coorientação") | "{nome} convidou você para coorientar o TCC. TCC: {titulo}." ({titulo} como na MO-01), com os botões "Aceitar" e "Recusar" como links para a tela Orientações | US-45 passo 6; US-36; RBN-CAD-10.4; Clarifications D7 | A validar |
| MO-08 | Notificação ao Orientador: coorientador registrado, substituído ou removido | Registro: "{nome} registrou {coorientador} como coorientador do TCC." / Substituição: "{nome} substituiu o coorientador {anterior} por {novo}." / Remoção: "{nome} removeu {coorientador} da coorientação do TCC." | US-45 passos 6, A, D, E | A validar |
| MO-09 | Notificação ao coorientador do NUCOMP substituído ou removido | "Você deixou de coorientar o TCC de {nome}." | US-45 D, E | A validar |
| MO-10 | Notificação ao Aluno e ao Orientador: convite aceito | Ao Aluno: "{docente} aceitou coorientar o seu TCC." / Ao Orientador: "{docente} aceitou coorientar o TCC de {nome}." | US-36 passo 5 | A validar |
| MO-11 | Notificação ao Aluno: convite recusado | "{docente} recusou o convite de coorientação." | US-36 C | A validar |
| MO-12 | Link de pedido ou convite cancelado pelo encerramento da participação | Pedido: "Este pedido foi cancelado porque a participação do aluno foi encerrada." / Convite: "Este convite foi cancelado porque a participação do aluno foi encerrada." | spec 004, Q-40; FR-050 | A validar |
| MO-13 | Confirmação e resultado de "Correções Conferidas" | "Confirmar que as correções do TCC de {nome} foram conferidas?" / "Correções conferidas" / etiqueta na linha: "Correções conferidas em {data e hora}" | US-44 B; FR-016 | A validar |
| MO-14 | Confirmação de "Remover" coorientador | "Remover {nome} da coorientação?" | US-45 C, E | A validar |
| MO-15 | Aceite do pedido de orientação (correção de concordância do texto da US-18) | "Pedido aceito. O aluno foi incluído na sua tela de orientandos" | US-18 passo 7 e cenário 1 ("no seu tela", erro da v3.3); Clarifications Q3; índice Q-94 | A validar |
| MO-16 | Notificação e e-mail ao docente indicado no pedido de troca (assunto: "SIGTCC: pedido de troca de orientação") | "{nome} pediu a troca de orientador para você. TCC: {titulo}. Orientador atual: {orientador}." | US-17 D; US-18 E (sem texto exato) | A validar |
| MO-17 | Link: convite cancelado porque o docente passou a ser o orientador (a notificação da transferência continua a MT-22 da spec 004; Clarifications Q18) | "Este convite foi cancelado porque o docente passou a ser o orientador do trabalho." | Clarifications D13; FR-050 | A validar |
| MO-18 | Link e notificação: pedido ou convite cancelado pela cópia para o TCC 2 | Link: "Este pedido foi cancelado porque o TCC passou para a turma de TCC 2." / "Este convite foi cancelado porque o TCC passou para a turma de TCC 2." / Notificação ao docente: "O {pedido de orientação ou convite de coorientação} de {nome} foi cancelado porque o TCC passou para a turma de TCC 2." | Clarifications Q6; FR-050, FR-051 | A validar |
| MO-19 | Limites de tamanho (atas, comentário e publicação) | "Informe a pauta com até 2.000 caracteres" / "Informe as metas com até 2.000 caracteres" / "Informe o comentário com até 1.000 caracteres" / "Informe o veículo de publicação com até 150 caracteres" | US-19 E4 e cenário 12; US-46 E3 e cenário 7 ("informa o limite", sem texto) | A validar |
| MO-20 | "Apto para Defesa" recusado porque as condições mudaram | "O TCC não atende mais às condições para ser indicado como apto para defesa." | FR-027 | A validar |
| MO-21 | Recusa de artigo Homologado pelo endereço direto depois da liberação do resultado (o botão já fica indisponível, US-20 E3) | "O resultado já foi liberado: a homologação deste artigo não pode mais ser recusada." | US-20 E3; Clarifications Q16; FR-038 | A validar |
| MO-22 | Etiqueta de aproveitamento sem análise (Status diferente de Aceito ou Publicado) | "Aguardando aceite ou publicação" | US-46 passo 2; Clarifications D10 | A validar |
| MO-23 | Seção Defesa do painel do aluno, antes do módulo de Defesa | "Nenhuma sessão de defesa registrada." | Clarifications D12 | A validar |
| MO-24 | Seções vazias da tela Orientações | "Nenhum pedido de orientação pendente." / "Nenhum convite de coorientação pendente." / "Nenhum orientando." | Clarifications Q11; FR-040 | A validar |
| MO-25 | Aviso ao Aluno: coorientador externo reaproveitado pelo e-mail | "Este coorientador já estava cadastrado: foram mantidos o nome e a instituição registrados." | Clarifications Q13; FR-028 | A validar |
| MO-26 | Link e notificação: pedido ou convite cancelado com a turma arquivada | Link: "Este pedido foi cancelado porque a turma foi arquivada." / "Este convite foi cancelado porque a turma foi arquivada." / Notificação ao docente: "O {pedido de orientação ou convite de coorientação} de {nome} foi cancelado porque a turma {identificador} foi arquivada." | Clarifications Q17; FR-050, FR-053 | A validar |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um Aluno envia o pedido de orientação em menos de 1 minuto, a partir do item "Turmas".
- **SC-002**: Um Docente aceita ou recusa um pedido em até 2 acionamentos, a partir do e-mail ou do
  sino.
- **SC-003**: 100% das mensagens exibidas são idênticas às das US ou estão na tabela MO-xx (MO-01 a
  MO-26).
- **SC-004**: Todos os 99 cenários de aceite das 9 US (mais os 7 pontos de contato das User Stories
  2, 3 e 9) têm pelo menos um teste automatizado; nos cenários 1 e 3 da US-20, a parte da nota mínima
  é testada pela consulta do FR-039, porque a nota é aplicada pela US-27.
- **SC-005**: 100% das telas novas são alcançadas pela navegação (menu, aba, link ou botão) no
  roteiro manual, sem endereço digitado.
- **SC-006**: 100% das ações que alteram dados são recusadas para quem não tem o papel ou o vínculo,
  e com a turma arquivada, nos testes de permissão, inclusive pelo endereço direto.
- **SC-007**: 100% das mudanças de Status feitas por esta spec (Apto para Defesa) passam pelo serviço
  único da spec 005, com o histórico gravado.

## Assumptions

- O efeito da homologação do artigo na nota (US-27), a geração da Ata Final e da Folha de Aprovação
  (US-28), o agendamento (US-21, US-24) e a composição da banca (US-23) são do módulo de Defesa;
  esta spec só expõe os dados e serviços que eles consomem.
- "Resultado liberado" (US-20 C e E3) é reconhecido pelo registro do gatilho "Liberação do
  resultado" no histórico do Status do TCC (spec 005), até o módulo de Defesa existir; vale para
  cada linha de TCC (no TCC 2, a liberação do TCC 1 não conta; Clarifications Q6 e Q16).
- O motivo de um pedido ou convite 'Cancelado' é deduzido pela regra do FR-050, sem coluna nova
  (Clarifications Q7).
- A ata não guarda o autor (o dicionário não tem a coluna); só os comentários guardam autor, data e
  hora (US-19 C). A lacuna fica aceita, sem coluna nova (Clarifications D14; índice Q-102).
- Os e-mails (pedido, MO-01; pedido de troca, MO-16; convite, MO-07; aceite ao Professor da
  Disciplina, MO-04) seguem o padrão da spec 005: depois da gravação, com a falha só no log; a
  notificação no sistema é a forma principal, e os demais avisos, inclusive a MO-06, saem só no
  sistema (índice Q-84).
- A listagem de docentes com a quantidade de orientandos (RBN-CAD-11.3) é da spec 002.
