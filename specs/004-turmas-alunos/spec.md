# Feature Specification: Turmas e Alunos do SIGTCC

**Feature Branch**: `feature/feat-03-turmas-e-alunos`

**Created**: 2026-10-20

**Status**: Aprovada por Julia Cohen em 2026-10-20

**Input**: User description: "Use o número 004 para esta spec. Turmas e Alunos do SIGTCC: US-07, US-08
e US-09. Use as seções dessas US em docs/fonte/Historias_de_Usuario_v3_2.md, com regras (RBN), fluxos
alternativos, mensagens exatas e cenários de aceite; IDs da matriz de 17/10. O modelo de dados já
existe (spec 001); não crie tabelas. Reutilize da spec 003 a base visual, @perfil_requerido, o papel
Professor da Disciplina (spec Q27, RBN-CAD-04.5) e a criação de contas 'Aguardando Ativação' para os
alunos importados. Inclua a importação de alunos por CSV (US-08) conforme o meu diagrama de
sequência. Não crie nem troque de branch: use a feature/feat-03-turmas-e-alunos."

**Responsável**: Julia Cohen (responsável pelas US-07, US-08 e US-09 no documento de US).

**Fontes**: `docs/fonte/Historias_de_Usuario_v3_2.md` (US-07, US-08, US-09);
`docs/fonte/Matriz_Requisitos_17_10.md` (RAN-CAD-04, RAN-CAD-05; RBN-CAD-04.1 a 04.5, 05.1 a 05.8,
08.3, 08.4, 08.5 e 08.7; Glossario_Status); `docs/fonte/Modelo_Logico_e_Dicionario_18_10.md` (tabelas
existentes); `docs/fonte/prototipo/prototipo_17_10.html` (só o visual: telas "Gerenciar turmas de
TCC", "Matricular alunos na turma" e "Excluir aluno da turma"); `specs/001-modelo-dados/` (modelo de
dados); `specs/003-acesso-login/` (base visual, verificação de perfil, papel Professor da Disciplina,
conta 'Aguardando Ativação', log e mensagens provisórias).

**Rastreabilidade**: [US-07][RBN-CAD-04.1][RBN-CAD-04.2][RBN-CAD-04.3][RBN-CAD-04.4][RBN-CAD-04.5] ·
[US-08][RBN-CAD-05.1][RBN-CAD-05.2][RBN-CAD-05.3][RBN-CAD-05.5][RBN-CAD-05.6][RBN-CAD-05.7] ·
[US-09][RBN-CAD-05.4][RBN-CAD-05.8][RBN-CAD-08.4][RBN-CAD-08.5] · apoio: [RBN-CAD-08.3][RBN-CAD-08.7]

## Clarifications

### Session 2026-10-20

- Q1 (resolvida pela matriz, sem mudar comportamento): a US-09 usa "Encerrar participação" no fluxo
  principal da exclusão e "Excluir da turma" no cenário 1. A matriz (RBN-CAD-05.4) diz que o
  Professor "clica em Excluir". Esta spec usa "Excluir da turma" para a exclusão (aluno sem
  Proposta) e "Encerrar participação" para o encerramento (aluno com Proposta), como no cenário 11
  da US-09.
- Q2 (respondida por Julia Cohen em 2026-10-20): arquivo com linhas inválidas é rejeitado inteiro
  (matriz, RAN-CAD-05) ou só as linhas inválidas (US-08, cenário 4)? → A: Importa as linhas válidas
  e rejeita só as inválidas, com o número da linha e o motivo, como no cenário 4 da US-08. O texto da
  matriz é lido como "a linha inválida é rejeitada, indicando quais linhas têm erro".
- Q3 (respondida por Julia Cohen em 2026-10-20; divergência com o Modelo Lógico): como gravar o Curso
  do aluno, se `Alunos` só guarda o código de curso da UEA (até 20 caracteres)? → A: O campo Curso
  aceita só o código de curso da UEA (até 20 caracteres), com sugestões tiradas da tabela de
  equivalência (código e nome do curso do NUCOMP). O curso do NUCOMP é sempre derivado desse código
  pela equivalência; sem correspondência, "Código não reconhecido". Nada muda no modelo. Os códigos
  carregados estão na Q5.
- Q4 (respondida por Julia Cohen em 2026-10-20): a importação aceita CSV e XLSX ou só CSV? → A: CSV e
  XLSX nesta entrega, como na matriz (RBN-CAD-05.2) e na US-08. A leitura de XLSX exige uma
  dependência nova, item de configuração para o Célio Benjamim no plano.
- Q5 (respondida por Julia Cohen em 2026-10-20, com as Q-17, Q-37 e Q-38 do índice): quais códigos
  de curso da UEA a tabela de equivalência guarda e de onde vem o curso do aluno? → A: A tabela
  guarda os códigos completos, no formato do exemplo do dicionário: EST08MCPD = Engenharia de
  Computação, EST31MSII = Sistemas de Informação e EST03MLV = Licenciatura em Computação
  (definitivos, mas "sujeitos a mudança": cada mudança entra por uma nova carga, sem mudar código).
  O curso do aluno vem do código informado no campo Curso (matrícula individual ou coluna Curso do
  arquivo), comparado inteiro com a tabela (Q3); a matrícula não é usada para isso. Informação
  registrada para referência: a matrícula tem 2 dígitos do ano, 2 da unidade (EST = 15), 2 do curso
  (08, 31 e 03, iguais aos do código) e 4 da posição (ex.: 2415080008); ESTECP, ESTSNF e ESTLIC são
  prefixos do Código da Disciplina da turma, não códigos de curso do aluno.
- Q6 (resolvida pelo diagrama de sequência "Matrícula por CSV" da responsável e pela matriz,
  RBN-CAD-08.6): aluno com Status do TCC 'Aprovado para TCC 2' matriculado em turma de TCC 2 →
  A: O sistema cria na nova turma um TCC carregado com os dados do TCC 1 (título, subtítulo,
  resumo, modalidade, link da proposta, área de interesse, palavras-chave, orientador, coorientadores
  e registro de publicação) e Status 'Em Andamento'; o TCC 1 fica como histórico do período anterior
  (diagrama: `criar(aluno, turma, tccAnterior)`). Nas turmas com orientador automático, prevalece o
  professor da turma; o orientador de TCC 1 fica no histórico e, se o novo orientador era
  coorientador, a coorientação é encerrada.
- Q7: O que acontece quando o Professor matricula um aluno que já tem TCC em andamento noutra turma
  não arquivada ('Sem Proposta', 'Em Andamento' ou 'Apto para Defesa') ou cujo último TCC já
  terminou ('Aprovado', 'Aprovado com Correções' ou 'Concluído')? → A: A matrícula (individual ou a
  linha do arquivo) é recusada com o motivo (MT-26 ou MT-27, PROVISÓRIAS). O aluno com TCC ativo
  noutra turma só muda de turma pela Transferência (RBN-CAD-05.6); o aluno com TCC aprovado ou
  concluído não é rematriculado.
- Q8: Quando o aluno sem Proposta é excluído da turma, o TCC 'Sem Proposta' criado na matrícula é
  apagado ou guardado? → A: Apagado: a exclusão remove o vínculo, o TCC 'Sem Proposta' e o histórico
  de status desse TCC; o registro auditável é o do histórico de alunos da turma (autor, data, hora e
  justificativa), mostrado na lista de excluídos ou transferidos. Se a resposta da PO na Q-02 do
  índice mudar o tratamento do aluno que desiste antes da Proposta, a mudança começa pela spec.
- Q9: Além do Professor da Disciplina, quem pode abrir uma turma e ver a lista de alunos, só para
  consulta? → A: Só a Secretaria do curso da turma, seguindo exatamente os atores da matriz
  (RAN-CAD-04: Docente/Professor da Disciplina; RAN-CAD-05: Professor da Disciplina/Secretaria). Ela
  consulta as turmas do seu curso, ativas e arquivadas, e usa "Transferir". Coordenador de Curso e
  outros Docentes não abrem a turma (acesso não permitido, M-02 da spec 003).
- Q10: Quando o Professor encerra a participação do aluno, a orientação e a coorientação ativas
  desse TCC também são encerradas? → A: Sim. A orientação e a coorientação 'Ativa' do TCC passam a
  'Encerrada', com a data de fim igual à data do encerramento; o histórico fica guardado.
- Q11: Que variações de arquivo CSV a importação aceita? → A: CSV com separador ";" ou ","
  (detectado pela linha de cabeçalhos), em UTF-8 (com ou sem BOM) ou Windows-1252; no XLSX, só a
  primeira planilha é lida. O modelo de importação para download é um CSV em UTF-8 com ";".
- Q12 (respondida por Julia Cohen em 2026-10-20, no planejamento): uma turma sem alunos, mas com
  histórico de alunos excluídos ou transferidos, pode ser excluída? → A: Não. A exclusão vale só
  para a turma que nunca teve aluno (criada por engano); com histórico, aparece "A turma possui
  alunos matriculados. Use a opção Arquivar", e o registro de exclusões e transferências
  (RBN-CAD-05.8) fica guardado.

### Session 2026-10-21 (revisão do plano pelo arquiteto-django)

- Q13 (achado B-3): há limite de linhas no arquivo de importação? → A: Sim, até 200 linhas de alunos
  (sem contar o cabeçalho); acima disso, o arquivo não é processado e aparece "Arquivo fora do
  modelo. Baixe o modelo de importação" (texto do cenário 5 da US-08).
- Q14 (achado I-11): o encerramento da participação é permitido com sessão de defesa ativa, e o que
  acontece com pedidos pendentes? → A: Mesmo critério da transferência (E4 da US-08): com sessão
  'Agendada', 'Reagendada' ou 'Em Andamento', o encerramento é recusado (MT-30, PROVISÓRIA). Ao
  encerrar, os pedidos de orientação e os convites de coorientação pendentes do TCC ('Aguardando
  Resposta' ou 'Aguardando Aceite') passam a 'Cancelado'. Ciência da Leandra Matos (índice Q-40).
- Q15 (achado I-12): Descrição e Curso continuam bloqueados quando todos os alunos saíram da turma? →
  A: Sim, com o mesmo critério da Q12: ficam bloqueados na turma que tem ou já teve aluno (vínculo,
  TCC ou histórico de exclusão ou transferência).
- Q16 (achado m10): aluno já cadastrado com a conta 'Inativa' ou 'Expirada' pode ser matriculado? →
  A: Sim, sem reativar a conta; o Professor vê o aviso MT-29 (PROVISÓRIA) de que o aluno não
  consegue entrar até a conta ser reativada pela Gestão de Contas (spec 002).
- Q17 (achado I-3): quem cria e remove os registros das entregas do aluno? → A: Esta feature cria os
  registros do aluno para as entregas que a turma já tem, na matrícula e na transferência (na turma
  de destino). Na exclusão do aluno, a exclusão NÃO é recusada: os registros sem envio são apagados
  e os com envio ficam como histórico. Na transferência, vale a mesma regra para as entregas da
  turma de origem. Ao cadastrar uma entrega nova, a US-43 (Leandra Matos) cria os registros dos
  alunos já matriculados (índice Q-41).

### Session 2026-10-21 (reconferência do arquiteto-django)

- Q18 (achado N1): o aluno que volta a uma turma onde já esteve (rematrícula depois de exclusão, ou
  transferência para uma turma de onde já saiu) e tem lá registros de entrega com envio guardados →
  A: O registro antigo volta para 'Aguardando Envio' (sem avaliação, feedback nem conferência de
  correções), e os envios anteriores ficam no histórico de envios. Assim o aluno não aparece como já
  tendo entregado algo de outro vínculo.
- Q19 (achado N5b): quando o encerramento cancela um pedido de orientação ou um convite de
  coorientação pendente, o docente convidado é avisado? → A: Sim, por notificação (MT-31,
  PROVISÓRIA).

## User Scenarios & Testing *(mandatory)*

Os cenários reproduzem os cenários de aceite das US, com as mensagens exatas entre aspas. As
prioridades indicam só a ordem de entrega: as três US são Must Have na matriz (com partes Should
Have: RBN-CAD-04.4, 04.5, 05.2 e 05.8).

### User Story 1 - Cadastrar e manter turmas de TCC [US-07] (Priority: P1)

O Docente cadastra turmas de TCC 1 e TCC 2 e passa a ser o Professor da Disciplina delas; depois
edita, exclui (se vazia) ou arquiva a turma.

**Why this priority**: sem turma, nenhum aluno pode ser matriculado nem fazer o primeiro acesso
(US-10 exige matrícula vinculada a turma).

**Independent Test**: com um Docente 'Ativa', cadastrar uma turma de TCC 1, editá-la, excluí-la
vazia; cadastrar outra e arquivá-la quando as condições forem atendidas.

**Acceptance Scenarios** (US-07, cenários 1 a 13):

1. **Dado que** o Professor está autenticado, **Quando** preenche os campos obrigatórios com a
   Descrição TCC 1 e clica em "Salvar", **Então** o sistema registra a turma e exibe "Turma
   cadastrada com sucesso" **E** o Professor fica vinculado como Professor da Disciplina da turma.
2. **Dado que** a turma tem um TCC com Status Em Andamento, **Quando** o Professor clica em
   "Arquivar", **Então** o sistema não arquiva a turma e informa "Há TCC Em Andamento ou Apto para
   Defesa".
3. **Dado que** o Professor informou Horário de Início 10:00 e Horário de Término 08:00, **Quando**
   clica em "Salvar", **Então** o sistema exibe "O horário de término deve ser posterior ao de
   início" e não salva.
4. **Dado que** a turma possui alunos matriculados, **Quando** o Professor clica em "Excluir",
   **Então** o sistema bloqueia a exclusão e exibe "A turma possui alunos matriculados. Use a opção
   Arquivar".
5. **Dado que** a turma não possui alunos matriculados, **Quando** o Professor clica em "Excluir" e
   confirma, **Então** o sistema remove a turma da lista de turmas.
6. **Dado que** a turma foi arquivada, **Quando** o Professor abre a turma, **Então** o sistema exibe
   os dados apenas para consulta **E** as opções Editar, Matricular alunos e Excluir aluno ficam
   indisponíveis.
7. **Dado que** o Docente criou uma turma de TCC 2 de Licenciatura em Computação, **Quando** os
   alunos são matriculados nessa turma (US-08), **Então** o Docente passa a ser o Orientador de
   todos esses alunos.
8. **Dado que** a turma já tem alunos matriculados, **Quando** o Professor da Disciplina clica em
   "Editar", **Então** os campos Descrição e Curso aparecem bloqueados **E** os demais campos podem
   ser alterados.
9. **Dado que** a turma de TCC 2 não tem TCC Em Andamento ou Apto para Defesa, não tem sessão de
   defesa ativa e a Data Limite da Versão Final já passou, **Quando** o Professor da Disciplina clica
   em "Arquivar" e confirma, **Então** a turma vai para a área de turmas arquivadas e fica disponível
   só para consulta.
10. **Dado que** a Data Limite da Versão Final da turma de TCC 2 é 30/11/2026 e hoje é 20/11/2026,
    **Quando** o Professor da Disciplina clica em "Arquivar", **Então** o sistema não arquiva e
    informa "A Data Limite da Versão Final ainda não venceu ou não foi cadastrada".
11. **Dado que** a turma tem uma sessão de defesa Agendada, **Quando** o Professor da Disciplina
    clica em "Arquivar", **Então** o sistema não arquiva e informa "Há sessão de defesa ativa".
12. **Dado que** o Professor está no formulário da turma, **Quando** informa um Local com 101
    caracteres e clica em "Salvar", **Então** o sistema destaca o campo Local e não salva a turma.
13. **Dado que** já existe no sistema uma turma com o Identificador ECP06_T01, **Quando** o Professor
    cadastra outra turma com o mesmo Identificador e clica em "Salvar", **Então** o sistema destaca o
    campo Identificador e não salva a turma.

---

### User Story 2 - Matricular alunos, um a um ou por arquivo [US-08] (Priority: P1)

O Professor da Disciplina matricula alunos na turma, individualmente ou por importação de arquivo,
com prévia antes de confirmar. Aluno novo recebe conta 'Aguardando Ativação'; aluno já cadastrado só
é vinculado à nova turma.

**Why this priority**: é o que permite ao aluno fazer o primeiro acesso (US-10) e iniciar o TCC.

**Independent Test**: numa turma ativa, matricular um aluno novo, um aluno já cadastrado e importar
um arquivo com linhas válidas e inválidas; conferir as contas criadas, os vínculos e o resumo.

**Acceptance Scenarios** (US-08, cenários 1 a 14):

1. **Dado que** o Professor está na turma e não existe aluno com a matrícula 2026000123, **Quando**
   informa a Matrícula 2026000123, o Nome Completo e o Curso e clica em "Salvar", **Então** o sistema
   cria a conta com o Status da Conta "Aguardando Ativação" **E** vincula o aluno à turma (e exibe
   "Aluno matriculado com sucesso", US-08, passo 5).
2. **Dado que** o Professor está no formulário de matrícula individual, **Quando** informa a
   matrícula "20260001", com 8 dígitos, e clica em "Salvar", **Então** o sistema exibe "A matrícula
   deve ter 10 dígitos numéricos" e não salva.
3. **Dado que** o aluno 2026000123 já cursou uma turma de TCC 1, **Quando** o Professor o matricula
   em uma turma de TCC 2, **Então** o sistema não cria uma nova conta **E** vincula o aluno à turma
   de TCC 2, mantendo o histórico da turma anterior.
4. **Dado que** o arquivo CSV tem 30 linhas, 2 delas com matrícula de 9 dígitos, **Quando** o
   Professor envia o arquivo e confirma a importação, **Então** o sistema matricula os 28 alunos
   válidos **E** exibe um resumo com as 2 linhas rejeitadas e o motivo de cada uma (Clarifications,
   Q2).
5. **Dado que** o Professor está na opção de importação, **Quando** envia um arquivo PDF, **Então** o
   sistema não processa o arquivo e exibe "Arquivo fora do modelo. Baixe o modelo de importação".
6. **Dado que** o TCC do aluno está Em Andamento numa turma de TCC 2 de Engenharia de Computação e
   não há sessão de defesa ativa, **Quando** o Professor da Disciplina clica em "Transferir", escolhe
   a turma de TCC 2 de outro orientador do mesmo curso e período e escreve a justificativa, **Então**
   o aluno passa a constar apenas na turma de destino, com o professor dela como orientador **E** o
   aluno e os dois orientadores são notificados.
7. **Dado que** o arquivo CSV tem uma linha com o código de curso da UEA de Engenharia de Computação
   (EST08MCPD; Clarifications, Q5), **Quando** o Professor envia o arquivo e confirma a importação,
   **Então** o sistema matricula o aluno no curso Engenharia de Computação do NUCOMP.
8. **Dado que** o arquivo CSV tem uma linha com um código de curso que não está na tabela de
   equivalência, **Quando** o Professor envia o arquivo e confirma a importação, **Então** o aluno é
   matriculado e o curso dele aparece como "Código não reconhecido" **E** o resumo informa quantos
   códigos não foram reconhecidos.
9. **Dado que** o aluno 2026000123 já está na turma, **Quando** o Professor tenta matriculá-lo de
   novo, **Então** o sistema ignora o registro e informa "Aluno já matriculado nesta turma".
10. **Dado que** o aluno está matriculado na turma, **Quando** o Professor clica em "Editar", corrige
    o Nome Completo e salva, **Então** o sistema grava o novo nome **E** a Matrícula continua sem
    opção de edição.
11. **Dado que** a turma foi arquivada, **Quando** o Professor abre a turma, **Então** a opção
    "Matricular alunos" fica indisponível.
12. **Dado que** o TCC do aluno tem uma sessão de defesa Agendada, **Quando** o Professor da
    Disciplina tenta transferi-lo, **Então** o sistema não transfere e informa o motivo.
13. **Dado que** o TCC do aluno está com o Status Aprovado para TCC 2, **Quando** o Professor o
    matricula numa turma de TCC 2, **Então** o TCC é transferido para a nova turma com os dados do
    TCC 1 (US-14) **E** o Status do TCC volta para Em Andamento.
14. **Dado que** o Professor está na opção de importação, **Quando** envia um arquivo XLSX de 3 MB,
    **Então** o sistema não processa o arquivo e exibe "Arquivo fora do modelo. Baixe o modelo de
    importação".

---

### User Story 3 - Excluir aluno ou encerrar a participação [US-09] (Priority: P2)

O Professor da Disciplina exclui da turma o aluno vinculado por engano (sem Proposta) ou encerra a
participação do aluno com Proposta como Desistente, Reprovado ou Jubilado; a turma mostra a lista de
excluídos ou transferidos.

**Why this priority**: corrige vínculos errados e alimenta o histórico e o relatório de evasão; só
faz sentido depois de haver alunos matriculados.

**Independent Test**: excluir um aluno sem Proposta, tentar excluir um com Proposta, encerrar a
participação de um aluno com TCC Em Andamento e conferir a lista de excluídos ou transferidos.

**Acceptance Scenarios** (US-09, cenários 1 a 11):

1. **Dado que** o aluno está na turma e não tem Proposta cadastrada, **Quando** o Professor clica em
   "Excluir da turma", escreve a justificativa e confirma, **Então** o sistema retira o aluno da
   turma e o mostra na lista de excluídos ou transferidos **E** o aluno recebe uma notificação com o
   motivo (e o sistema exibe "Aluno excluído da turma", US-09, passo 7).
2. **Dado que** o aluno já salvou a Proposta, **Quando** o Professor tenta excluí-lo da turma,
   **Então** o sistema não exclui e exibe "O aluno já tem Proposta. Use Encerrar participação".
3. **Dado que** o aluno tem Proposta e o TCC está Em Andamento, **Quando** o Professor clica em
   "Encerrar participação", escolhe Desistente, escreve a justificativa e confirma, **Então** o Status
   do TCC passa a Desistente e a transição fica no histórico, com o Professor da Disciplina como
   responsável **E** o registro entra no relatório de evasão.
4. **Dado que** o Professor abriu o formulário de exclusão, **Quando** clica em "Confirmar" sem
   escrever a justificativa, **Então** o sistema exibe "Informe uma justificativa de até 500
   caracteres" **E** o aluno continua na turma.
5. **Dado que** o Professor abriu o formulário de encerramento, **Quando** escreve uma justificativa
   com 501 caracteres e clica em "Confirmar", **Então** o sistema exibe "Informe uma justificativa de
   até 500 caracteres" e não conclui.
6. **Dado que** o Professor abriu o formulário de encerramento, **Quando** escreve a justificativa e
   confirma sem escolher o Status, **Então** o sistema exibe "Selecione o Status do aluno" **E** o
   Status do TCC não muda.
7. **Dado que** a participação do aluno foi encerrada com o Status Reprovado, **Quando** ele entra no
   sistema e tenta enviar o link de uma entrega, **Então** o botão de envio está desabilitado **E** o
   aluno ainda consegue consultar o próprio histórico. *Nesta feature, testa-se a regra reutilizável
   que diz se o aluno está restrito (FR-024); o botão de envio é da feature de Entregas (US-16).*
8. **Dado que** o TCC do aluno está com o Status Jubilado, **Quando** o aluno tenta editar o TCC ou
   indicar um orientador, **Então** os botões estão desabilitados. *Mesma observação do cenário 7:
   os botões são das features de TCC (US-13) e Orientação (US-17).*
9. **Dado que** um aluno foi excluído e outro foi transferido da turma, **Quando** o Professor abre a
   lista de excluídos ou transferidos, **Então** o sistema mostra os dois com nome, matrícula, data e
   hora, autor e justificativa.
10. **Dado que** o Professor preencheu o formulário de exclusão, **Quando** cancela na confirmação
    final, **Então** o aluno continua na turma e nada é registrado.
11. **Dado que** a turma foi arquivada, **Quando** o Professor abre o painel de um aluno, **Então**
    as opções "Excluir da turma" e "Encerrar participação" ficam indisponíveis.

---

### Edge Cases

- **Docente sem turma cria a primeira**: passa a ter o papel Professor da Disciplina (spec 003, Q27)
  e o item de menu correspondente.
- **Ação em turma arquivada pelo endereço direto** (RBN-CAD-04.5, E4 da US-07): editar, excluir,
  arquivar de novo, matricular, importar, editar aluno, transferir, excluir aluno e encerrar
  participação são recusados mesmo sem o botão; a turma continua visível para consulta.
- **Outro Docente na turma alheia** (E5 da US-07; Q9): não abre a turma, nem pelo endereço direto,
  e recebe a mensagem de acesso não permitido da spec 003 (M-02); vale também para o Coordenador
  de Curso que não é o Professor da Disciplina da turma.
- **Arquivamento de turma de TCC 1**: só as duas primeiras condições (sem TCC Em Andamento ou Apto
  para Defesa e sem sessão ativa); a Data Limite da Versão Final só é exigida em TCC 2.
- **TCC 2 sem entrega do tipo Versão Final cadastrada**: o arquivamento é recusado com "A Data Limite
  da Versão Final ainda não venceu ou não foi cadastrada".
- **Exclusão de turma**: a turma é removida definitivamente, e o evento fica registrado com autor,
  data e hora (matriz, RAN-CAD-04, Responsabilização). Só vale para a turma que nunca teve aluno;
  com histórico de exclusões ou transferências, só arquivar (Q12).
- **Orientador automático em TCC 2 de Sistemas de Informação ou em TCC 1**: não existe (RBN-CAD-04.2);
  o vínculo vem da indicação do orientador (US-17).
- **Matrícula repetida no mesmo arquivo**: a segunda ocorrência é rejeitada com "Aluno já matriculado
  nesta turma".
- **Aluno já cadastrado com Nome diferente no arquivo**: o vínculo usa a conta existente e não muda o
  nome (a correção do nome é pela edição, RBN-CAD-05.3).
- **Aluno já cadastrado com TCC Reprovado, Desistente ou Jubilado** (RBN-CAD-05.5): é vinculado à
  nova turma com um novo TCC 'Sem Proposta' e registra nova Proposta (US-13).
- **Aluno com TCC ativo noutra turma ou já aprovado ou concluído** (Q7): a matrícula é recusada (MT-26
  ou MT-27); para mudar de turma no período, usa-se a Transferência.
- **Aluno 'Aprovado para TCC 2' matriculado em turma de TCC 1**: caso não coberto pela US-08 nem pelo
  diagrama; proposta do planejamento: recusar com MT-28 (PROVISÓRIA), a confirmar pela responsável
  (índice Q-39).
- **Curso do aluno diferente do curso da turma** (RBN-CAD-05.7): o aluno é matriculado e aparece um
  alerta de divergência; relatórios, filtros e permissões usam sempre o curso da turma.
- **Arquivo com cabeçalhos em outra ordem**: aceito, desde que os três cabeçalhos estejam presentes
  na primeira linha.
- **CSV salvo pelo Excel em português** (Q11): separador ";" e codificação Windows-1252 são aceitos,
  com os acentos do Nome Completo preservados; XLSX com várias planilhas: só a primeira é lida.
- **Prévia abandonada**: se o Professor não confirmar a importação, nada é gravado.
- **Exclusão do aluno**: o aluno perde o acesso à turma; o TCC 'Sem Proposta' daquela turma é
  apagado (Q8); a conta continua existindo e pode ser vinculada de novo, a esta ou a outra turma.
- **Encerramento**: o aluno continua entrando no sistema, só para consultar o próprio histórico
  (RBN-CAD-08.5); a orientação e a coorientação ativas do TCC são encerradas (Q10), e o docente
  perde o papel "Orientador" se não tiver outra orientação ativa.
- **Transferência sem turma de TCC 2 de outro orientador no mesmo curso e período**: não é permitida
  e o motivo é informado (E4 da US-08).
- **Transferência quando o novo orientador era coorientador do trabalho**: a coorientação é encerrada
  (RBN-CAD-05.6).

## Requirements *(mandatory)*

### Functional Requirements

**Turmas [US-07][RBN-CAD-04.1 a 04.5]**

- **FR-001**: Qualquer Docente com conta 'Ativa' DEVE poder cadastrar uma turma com Código da
  Disciplina (só letras maiúsculas e números, sem espaços, até 20 caracteres), Descrição (lista: TCC
  1 ou TCC 2), Identificador (letras maiúsculas, números e "_", sem espaços, até 30 caracteres, único
  no sistema), Ano (exatamente 4 dígitos), Semestre (lista: 1 ou 2), Dia da Semana (lista: segunda-
  feira a sábado), Horário de Início e de Término (HH:MM, 24 horas, término posterior ao início),
  Local (texto livre, até 100 caracteres) e Curso (lista: Engenharia de Computação, Sistemas de
  Informação ou Licenciatura em Computação). Todos são obrigatórios (RBN-CAD-04.1).
- **FR-002**: Campo inválido DEVE ser destacado com a mensagem do campo, sem salvar: horário de
  término não posterior ao de início – "O horário de término deve ser posterior ao de início"; os
  demais casos (formato do Código da Disciplina, formato ou repetição do Identificador, Ano, Local
  acima de 100 caracteres, campo vazio) usam as mensagens PROVISÓRIAS MT-01 a MT-05 e a M-14 da spec
  003.
- **FR-003**: Ao salvar, o sistema DEVE registrar a turma com o Docente logado como Professor da
  Disciplina e exibir "Turma cadastrada com sucesso" (RBN-CAD-04.2).
- **FR-004**: Nas turmas de TCC 2 de Engenharia de Computação e de Licenciatura em Computação, o
  Professor da Disciplina DEVE passar a ser, automaticamente e sem exceção, o Orientador de todos os
  alunos matriculados na turma (orientação de origem "Automático"). Em TCC 1 e em TCC 2 de Sistemas
  de Informação não há orientador automático (RBN-CAD-04.2).
- **FR-005**: O Professor da Disciplina da turma DEVE poder editar todos os campos de FR-001, com as
  mesmas validações; na turma que tem ou já teve aluno (vínculo, TCC ou histórico de exclusão ou
  transferência), Descrição e Curso ficam bloqueados (RBN-CAD-04.3; Clarifications, Q15). Sucesso:
  MT-06 (PROVISÓRIA).
- **FR-006**: O Professor da Disciplina DEVE poder excluir a turma sem alunos vinculados, depois de
  confirmar (MT-07), removendo-a definitivamente (MT-08) e registrando a exclusão com autor, data e
  hora; com alunos, ou com histórico de alunos excluídos ou transferidos, a exclusão é bloqueada
  com "A turma possui alunos matriculados. Use a opção Arquivar" (RBN-CAD-04.4; Clarifications,
  Q12).
- **FR-007**: O Professor da Disciplina DEVE poder arquivar a turma, depois de confirmar (MT-09), só
  se: (a) nenhum TCC da turma estiver Em Andamento ou Apto para Defesa – senão "Há TCC Em Andamento
  ou Apto para Defesa"; (b) nenhuma sessão de defesa de TCC da turma estiver Agendada, Reagendada ou
  Em Andamento – senão "Há sessão de defesa ativa"; (c) em TCC 2, a Data Limite da entrega do tipo
  Versão Final da turma já tiver passado – senão "A Data Limite da Versão Final ainda não venceu ou
  não foi cadastrada". As condições são conferidas nessa ordem e aparece o primeiro motivo. Sucesso:
  MT-10 (PROVISÓRIA) (RBN-CAD-04.5).
- **FR-008**: A turma arquivada DEVE sair da listagem principal e ficar numa área de turmas
  arquivadas, só para consulta, com alunos, TCCs, entregas, atas, defesas e vínculos preservados. Nela
  ficam indisponíveis, inclusive pelo endereço direto: Editar, Excluir, Arquivar, Matricular alunos,
  importação, editar aluno, Transferir, Excluir da turma e Encerrar participação (ação recusada:
  MT-25). Esta feature também DEVE oferecer às outras features uma verificação reutilizável de
  "turma arquivada" para bloquear entregas, envios, atas, agendamento de defesa, Versão Final e
  lembretes de prazo (RBN-CAD-04.5; E4 da US-07).
- **FR-009**: As ações de manutenção da turma e dos seus alunos DEVEM ser aceitas só para o
  Professor da Disciplina da própria turma, com a turma não arquivada (spec 003, Q27; RBN-CAD-04.5);
  quem não é o Professor da Disciplina da turma não vê as opções Editar, Excluir e Arquivar (E5 da
  US-07). A Transferência também é aceita para a Secretaria do curso da turma (RBN-CAD-05.6).
- **FR-010**: O Docente DEVE ter um item de menu "Turmas" com a lista das turmas de que é Professor
  da Disciplina (não arquivadas) e acesso à área de turmas arquivadas; a turma aberta mostra os
  dados, os alunos (com Matrícula, Nome Completo, Curso e Status do TCC) e as ações permitidas. A
  Secretaria DEVE ter o item "Turmas" com as turmas do seu curso (ativas e arquivadas), só para
  consulta e com "Transferir". Nenhum outro perfil abre a turma, nem pelo endereço direto (M-02 da
  spec 003); o Coordenador de Curso só é Professor da Disciplina das turmas que ele mesmo criou
  (Clarifications, Q9).

**Matrícula de alunos [US-08][RBN-CAD-05.1, 05.2, 05.3, 05.5, 05.7]**

- **FR-011**: A matrícula individual DEVE pedir Matrícula (exatamente 10 dígitos numéricos, única no
  sistema – "A matrícula deve ter 10 dígitos numéricos"), Nome Completo (só letras, acentos e
  espaços, até 150 caracteres – MT-11) e Curso (código de curso da UEA, com letras maiúsculas e
  números, até 20 caracteres – MT-12; ao digitar, o sistema sugere os códigos da tabela de
  equivalência com o nome do curso do NUCOMP correspondente; Clarifications, Q3 e Q5).
- **FR-012**: Para matrícula inexistente, o sistema DEVE criar a conta do aluno com o Status da Conta
  'Aguardando Ativação', sem e-mail e sem senha, sem enviar link (spec 003, Q1: o aluno pede o link
  em "Primeiro acesso"), vinculá-lo à turma com um TCC no Status 'Sem Proposta' (transição registrada
  no histórico do Status do TCC com o gatilho "Vínculo à turma", RBN-CAD-08.3 e 08.7), criar os
  registros do aluno nas entregas que a turma já tem (status 'Aguardando Envio'; Q17) e exibir
  "Aluno matriculado com sucesso". Aluno já cadastrado com a conta 'Inativa' ou 'Expirada' é
  matriculado sem reativar a conta, e o Professor vê o aviso MT-29 (Q16).
- **FR-013**: Para matrícula já cadastrada, o sistema NÃO DEVE criar nova conta: vincula o aluno à
  turma mantendo conta, e-mail, senha e histórico. Se o Status do último TCC do aluno for 'Aprovado
  para TCC 2' e a turma for de TCC 2, o sistema cria na nova turma um TCC carregado com os dados do
  TCC 1 (Clarifications, Q6), com Status 'Em Andamento' (gatilho "Transferência para TCC 2", US-14,
  RBN-CAD-08.6), e o TCC 1 fica como histórico; se for 'Reprovado',
  'Desistente' ou 'Jubilado', o aluno ganha um novo TCC 'Sem Proposta' na nova turma (RBN-CAD-05.5).
  Se o aluno tiver TCC 'Sem Proposta', 'Em Andamento' ou 'Apto para Defesa' noutra turma não
  arquivada, a matrícula é recusada com MT-26; se algum TCC do aluno estiver 'Aprovado', 'Aprovado
  com Correções' ou 'Concluído', é recusada com MT-27 (Clarifications, Q7). Na importação, a recusa é
  por linha, com o motivo na prévia e no resumo.
- **FR-014**: Aluno já matriculado nesta turma DEVE ser ignorado com "Aluno já matriculado nesta
  turma" (uma mesma matrícula não pode ser vinculada duas vezes à mesma turma, RAN-CAD-05).
- **FR-015**: O curso do aluno DEVE ser reconhecido pelo código de curso da UEA informado no campo
  Curso, comparado inteiro com a tabela de equivalência entre códigos da UEA e cursos do NUCOMP; sem
  correspondência, aparece "Código não reconhecido". Se o curso reconhecido for diferente do curso
  da turma, o sistema exibe um alerta de divergência (MT-13) e matricula o aluno mesmo assim
  (RBN-CAD-05.7; Clarifications, Q3 e Q5).
- **FR-015a**: A tabela de equivalência DEVE ser carregada com EST08MCPD = Engenharia de Computação,
  EST31MSII = Sistemas de Informação e EST03MLV = Licenciatura em Computação. Mudanças de código
  entram por uma nova carga, sem tabela nova (Q5).
- **FR-016**: A importação DEVE aceitar um arquivo CSV ou XLSX de até 2 MB, com a primeira linha contendo os
  cabeçalhos Matrícula, Nome Completo e Curso, e validar cada linha pelas regras de FR-011, aceitando
  diretamente qualquer código de curso da UEA. Arquivo com outra extensão, acima de 2 MB ou sem algum
  cabeçalho NÃO é processado e o sistema exibe "Arquivo fora do modelo. Baixe o modelo de
  importação"; o modelo de importação fica disponível para download na mesma tela. Formatos aceitos:
  CSV e XLSX (RBN-CAD-05.2; Clarifications, Q4). O CSV pode usar ";" ou "," como separador e estar
  em UTF-8 (com ou sem BOM) ou Windows-1252; do XLSX, só a primeira planilha é lida; o modelo para
  download é um CSV em UTF-8 com ";" (Q11). Arquivo com mais de 200 linhas de alunos também não é
  processado e mostra a mesma mensagem (Q13).
- **FR-017**: Antes de gravar, a importação DEVE exibir uma prévia com os alunos novos, os já
  cadastrados, as linhas com erro (número da linha e motivo) e os códigos de curso não reconhecidos;
  nada é gravado até o Professor clicar em "Confirmar importação" (US-08, passos 7 e 8).
- **FR-018**: Ao confirmar, o sistema DEVE criar as contas novas, vincular os alunos válidos (FR-012
  a FR-014) e exibir um resumo com o total de matriculados, as linhas rejeitadas com o motivo e a
  quantidade de códigos de curso não reconhecidos (MT-15) (US-08, passo 9).
- **FR-019**: O Professor da Disciplina DEVE poder editar o Nome Completo e o Curso do aluno da
  turma, com as mesmas regras de FR-011; a Matrícula aparece só para leitura (RBN-CAD-05.3).
  Sucesso: MT-14 (PROVISÓRIA).

**Transferência [US-08][RBN-CAD-05.6]**

- **FR-020**: Em turma com orientador automático (FR-004), o Professor da Disciplina da turma de
  origem ou a Secretaria do curso DEVE poder transferir o aluno, escolhendo a Turma de Destino (lista
  só com turmas de TCC 2, do mesmo curso e período letivo, não arquivadas, de outro Professor da
  Disciplina) e escrevendo a Justificativa (obrigatória, até 500 caracteres – "Informe uma
  justificativa de até 500 caracteres").
- **FR-021**: A transferência DEVE ser recusada, informando o motivo (MT-17 a MT-19), se o TCC não
  estiver 'Em Andamento' nem 'Apto para Defesa', se houver sessão de defesa Agendada, Reagendada ou
  Em Andamento, ou se não existir turma de destino possível (E4 da US-08).
- **FR-022**: Na transferência, o TCC, o Status do TCC e o histórico DEVEM ir para a turma de
  destino; o aluno passa a constar só nela; a orientação automática anterior é encerrada e o
  professor da turma de destino passa a ser o orientador; se ele era coorientador do trabalho, a
  coorientação é encerrada; os registros das entregas da turma de origem sem envio são apagados e
  os com envio ficam como histórico, e o aluno ganha os registros das entregas da turma de destino
  (Q17); o aluno e os orientadores antigo e novo recebem notificação (MT-22); a transferência fica
  registrada com autor, data, hora e justificativa; o sistema exibe MT-16.

**Exclusão e encerramento [US-09][RBN-CAD-05.4, 05.8, 08.4, 08.5]**

- **FR-023**: Para aluno sem Proposta, o Professor da Disciplina DEVE poder clicar em "Excluir da
  turma", escrever a Justificativa (obrigatória, até 500 caracteres – "Informe uma justificativa de
  até 500 caracteres"), clicar em "Confirmar" e confirmar na mensagem final (MT-24). O sistema retira
  o aluno da turma, registra autor, data, hora e justificativa, envia ao aluno uma notificação com o
  motivo (MT-21) e exibe "Aluno excluído da turma". A exclusão apaga o vínculo, o TCC 'Sem
  Proposta' da turma e o histórico de status desse TCC (Clarifications, Q8), e os registros do aluno
  nas entregas da turma sem envio; os com envio ficam como histórico (Q17). Cancelar na confirmação
  final não altera nada.
  Para aluno com Proposta, a exclusão é recusada com "O aluno já tem Proposta. Use Encerrar
  participação" (RBN-CAD-05.4).
- **FR-024**: Para aluno com Proposta, o Professor da Disciplina DEVE poder clicar em "Encerrar
  participação", escolher o Status (lista: Desistente, Reprovado ou Jubilado – sem escolha, "Selecione
  o Status do aluno") e escrever a Justificativa (obrigatória, até 500 caracteres). O Status do TCC
  muda, a justificativa fica no TCC, a transição entra no histórico do Status do TCC com o Professor
  da Disciplina como responsável e o gatilho "Encerramento da participação" (RBN-CAD-08.7), e o
  registro passa a contar no relatório de evasão (US-32). A orientação e a coorientação 'Ativa' do
  TCC passam a 'Encerrada', com data de fim (Clarifications, Q10), e os pedidos de orientação e os
  convites de coorientação pendentes passam a 'Cancelado' (Q14), e o docente de cada pedido
  cancelado recebe a notificação MT-31 (Q19). Com sessão de defesa 'Agendada',
  'Reagendada' ou 'Em Andamento', o encerramento é recusado com MT-30 (Q14). Sucesso: MT-23
  (PROVISÓRIA) (RBN-CAD-08.4).
- **FR-025**: O aluno com TCC 'Desistente', 'Reprovado' ou 'Jubilado' DEVE continuar entrando no
  sistema, só para consultar o próprio histórico. Esta feature DEVE oferecer às outras features uma
  verificação reutilizável de "participação encerrada", que elas usam para desabilitar, sem exceção,
  editar o TCC, indicar ou trocar de orientador e enviar entregas daquela turma (RBN-CAD-08.5).
- **FR-026**: A turma DEVE ter uma lista de excluídos ou transferidos, só de leitura, visível ao
  Professor da Disciplina, com nome, matrícula, data e hora, autor e justificativa de cada exclusão
  ou transferência (RBN-CAD-05.8).

**Base e restrições**

- **FR-027**: Todas as telas DEVEM usar a base visual da spec 003 (layout do protótipo de 17/10) e a
  verificação de perfil da spec 003; os papéis e a regra do Professor da Disciplina são os do
  contrato de serviços da spec 003 (Q27).
- **FR-028**: Esta feature NÃO DEVE criar tabelas nem colunas: usa o modelo da spec 001 (Turmas,
  Disciplinas, Cursos, Alunos, Usuarios, Alunos_Turmas, Historico_Alunos_Turmas, TCCs,
  Historico_Status_TCC, Orientacoes, Coorientacoes, Solicitacoes_Orientacao, PalavrasChave_TCC,
  Artigos, Encontro_Orientacao, Equivalencia_Cursos, Turmas_Marcos, Entregas_Marcos,
  Historico_Envios_Entregas, Defesas, Docentes, Secretarios e Notificacoes).
- **FR-029**: Mensagens sem texto nas US DEVEM usar os textos PROVISÓRIOS da seção "Mensagens a
  validar com a PO" (MT-01 a MT-32), até a validação da PO.

### Key Entities *(include if feature involves data)*

Todas já existem (spec 001); nenhuma é criada.

- **Turma**: período letivo (Ano e Semestre), Descrição (TCC 1 ou TCC 2), Identificador único,
  horário, Local, Curso, Professor da Disciplina, disciplina e Status ('Ativa' ou 'Arquivada').
- **Aluno**: conta de usuário com Matrícula de 10 dígitos e o código de curso da UEA; o curso do
  NUCOMP vem da equivalência (Q3).
- **Vínculo aluno-turma**: data de inscrição; uma vez por turma.
- **TCC**: um por aluno e turma; Status do TCC e justificativa de encerramento; histórico de cada
  transição.
- **Histórico de alunos da turma**: exclusões e transferências, com autor, data e hora e
  justificativa.
- **Orientação e coorientação**: a orientação automática em TCC 2 de EC e LC e o encerramento da
  coorientação na transferência.
- **Equivalência de cursos**: código de curso da UEA (ex.: EST08MCPD) → curso do NUCOMP.
- **Entrega da turma (Versão Final)** e **Sessão de defesa**: só lidas, para as condições de
  arquivamento e de transferência.
- **Notificação**: aluno excluído; aluno e orientadores na transferência.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos cenários de aceite das US-07 (13), US-08 (14) e US-09 (11) passam em testes
  automatizados; os cenários 7 e 8 da US-09 são testados aqui pela regra de participação encerrada
  e, nos botões, pelas features donas deles.
- **SC-002**: 100% das mensagens desta feature com texto definido nas US são idênticas ao texto da
  US, caractere por caractere; as PROVISÓRIAS são idênticas à tabela da seção "Mensagens a validar
  com a PO".
- **SC-003**: A importação de um arquivo com até 60 alunos é concluída (do envio do arquivo ao resumo)
  em até 10 segundos (RAN-CAD-05, Comportamento Temporal).
- **SC-004**: Nenhuma ação de manutenção de turma ou de aluno é aceita para quem não é o Professor da
  Disciplina da turma (ou a Secretaria do curso, na transferência), nem em turma arquivada, verificado
  por teste para cada ação, inclusive pelo endereço direto.
- **SC-005**: Nenhuma matrícula fica vinculada duas vezes à mesma turma, e nenhum aluno já cadastrado
  ganha uma segunda conta, verificado por teste na matrícula individual e na importação.
- **SC-006**: Toda exclusão de turma, exclusão de aluno, transferência e encerramento fica
  registrada com autor, data e hora (e justificativa, quando houver), verificado por teste.
- **SC-007**: Um Professor cadastra uma turma e importa 30 alunos (com prévia e confirmação) em até 5
  minutos, sem ajuda, medido em teste manual cronometrado.

## Mensagens a validar com a PO

Textos sem definição nas US nem na matriz. São **PROVISÓRIOS**: servem para planejar, testar e
implementar e precisam da validação da Product Owner (Profa. Diana). Campo obrigatório vazio usa a
M-14 da spec 003 ("Preencha este campo."); ação recusada por permissão usa a M-02 da spec 003.

| ID | Situação em que aparece | Texto proposto (PROVISÓRIO) | Origem | Situação |
|---|---|---|---|---|
| MT-01 | Código da Disciplina fora do padrão | "Use só letras maiúsculas e números, sem espaços, com até 20 caracteres (ex.: ESTCMP025)." | US-07 E1; RBN-CAD-04.1, campo 1 | A validar |
| MT-02 | Identificador fora do padrão | "Use só letras maiúsculas, números e _, sem espaços, com até 30 caracteres (ex.: ECP06_T01)." | US-07 E1; RBN-CAD-04.1, campo 3 | A validar |
| MT-03 | Identificador já usado em outra turma | "Já existe uma turma com este Identificador." | US-07 E1 e cenário 13 | A validar |
| MT-04 | Ano sem 4 dígitos | "Informe o ano com 4 dígitos (ex.: 2026)." | US-07 E1; RBN-CAD-04.1, campo 4 | A validar |
| MT-05 | Local acima de 100 caracteres | "O Local deve ter até 100 caracteres." | US-07 E1 e cenário 12 | A validar |
| MT-06 | Turma alterada | "Turma atualizada com sucesso." | US-07, fluxo A | A validar |
| MT-07 | Confirmação da exclusão da turma | "Excluir a turma IDENTIFICADOR? Esta ação não pode ser desfeita." | US-07, fluxo B; RBN-CAD-04.4 | A validar |
| MT-08 | Turma excluída | "Turma excluída." | US-07, fluxo B | A validar |
| MT-09 | Confirmação do arquivamento | "Arquivar a turma IDENTIFICADOR? Ela ficará disponível só para consulta." | US-07, fluxo C; RBN-CAD-04.5 | A validar |
| MT-10 | Turma arquivada | "Turma arquivada." | US-07, fluxo C | A validar |
| MT-11 | Nome Completo fora da regra | "Informe o Nome Completo só com letras, acentos e espaços, com até 150 caracteres." | US-08 E2; RBN-CAD-05.1, campo 2 | A validar |
| MT-12 | Curso fora da regra | "Informe o código de curso da UEA, com letras maiúsculas e números, até 20 caracteres (ex.: EST08MCPD)." | RBN-CAD-05.1, campo 3; Clarifications, Q3 | A validar |
| MT-13 | Curso do aluno diferente do curso da turma | "O curso do aluno (CURSO DO ALUNO) é diferente do curso da turma (CURSO DA TURMA)." | US-08, fluxo 3; RBN-CAD-05.7 | A validar |
| MT-14 | Dados do aluno alterados | "Dados do aluno atualizados." | US-08, fluxo 4; RBN-CAD-05.3 | A validar |
| MT-15 | Resumo da importação | "Importação concluída: N alunos matriculados, R linhas rejeitadas e C códigos de curso não reconhecidos." | US-08, passo 9 | A validar |
| MT-16 | Transferência concluída | "Aluno transferido para a turma IDENTIFICADOR." | US-08, fluxo 5 | A validar |
| MT-17 | Transferência com TCC fora de Em Andamento ou Apto para Defesa | "Só é possível transferir aluno com TCC Em Andamento ou Apto para Defesa." | US-08 E4; RBN-CAD-05.6 | A validar |
| MT-18 | Transferência com sessão de defesa ativa | "Não é possível transferir: há sessão de defesa ativa." | US-08 E4 e cenário 12 | A validar |
| MT-19 | Sem turma de destino possível | "Não há turma de TCC 2 de outro orientador no mesmo curso e período." | US-08 E4 | A validar |
| MT-20 | (reservado; a Justificativa vazia na transferência usa o texto da US-09, "Informe uma justificativa de até 500 caracteres") | — | US-09 E1; RBN-CAD-05.6 | — |
| MT-21 | Notificação ao aluno excluído | "Você foi excluído da turma IDENTIFICADOR. Motivo: JUSTIFICATIVA" (a justificativa é cortada com "…" quando o texto passaria de 500 caracteres, o limite da notificação; achado B-1) | US-09, passo 6; RBN-CAD-05.4 | A validar |
| MT-22 | Notificações da transferência (aluno e orientadores) | "NOME foi transferido da turma ORIGEM para a turma DESTINO." | US-08, fluxo 5; RBN-CAD-05.6 | A validar |
| MT-23 | Participação encerrada | "Participação encerrada como STATUS." | US-09, fluxo 1 | A validar |
| MT-24 | Confirmação final da exclusão do aluno | "Excluir NOME da turma? O aluno perderá o acesso a ela." | US-09, passos 4 e 5 | A validar |
| MT-25 | Ação em turma arquivada pelo endereço direto | "Esta turma está arquivada e só pode ser consultada." | US-07 E4; RBN-CAD-04.5 | A validar |
| MT-26 | Aluno com TCC em andamento noutra turma | "O aluno já tem TCC em andamento na turma IDENTIFICADOR. Use Transferir." | Clarifications, Q7; RBN-CAD-05.5 e 05.6 | A validar |
| MT-27 | Aluno com TCC aprovado ou concluído | "O TCC deste aluno já foi aprovado ou concluído." | Clarifications, Q7 | A validar |
| MT-28 | Aluno 'Aprovado para TCC 2' matriculado em turma de TCC 1 | "O aluno foi aprovado em TCC 1. Matricule-o numa turma de TCC 2." | Planejamento (research B6); índice Q-39 | A validar (comportamento a confirmar) |
| MT-29 | Aluno matriculado com a conta 'Inativa' ou 'Expirada' | "A conta deste aluno está STATUS: ele não consegue entrar até a conta ser reativada pela Gestão de Contas." | Clarifications, Q16 | A validar |
| MT-30 | Encerramento com sessão de defesa ativa | "Não é possível encerrar a participação: há sessão de defesa ativa." | Clarifications, Q14; E4 da US-08 | A validar |
| MT-31 | Notificação ao docente de pedido ou convite cancelado pelo encerramento | "O pedido de TIPO para o TCC de NOME foi cancelado porque a participação do aluno foi encerrada." | Clarifications, Q19 | A validar |
| MT-32 | Confirmação da importação com prévia vencida (30 minutos), já usada ou de outra turma (research B10) | "A prévia da importação venceu ou não é desta turma. Envie o arquivo de novo." | Implementação (research B10, achado B-2) | A validar |

## Assumptions

- **Branch**: `feature/feat-03-turmas-e-alunos`, indicada pela responsável; a spec é a 004. No PGCS
  4.3, a feat-03 pode ter outro nome; a confirmação fica com o Célio Benjamim (a registrar no índice).
- **Precedência**: matriz de 17/10 > US v3.2. Divergência que muda comportamento vai para
  Clarifications.
- **Quem cria turma**: qualquer Docente 'Ativa' (o ator da US-07 é o "Docente do NUCOMP"); ao criar,
  ganha o papel Professor da Disciplina.
- **Secretaria**: vê as turmas do seu curso, ativas e arquivadas, só para consulta, e usa
  "Transferir" (RBN-CAD-05.6); não cadastra nem altera turmas (Q9).
- **Registro da exclusão de turma**: como a turma é removida definitivamente e não há tabela para
  esse evento, o registro com autor, data e hora vai para o arquivo de log de eventos da spec 003
  (FR-029 daquela spec), sem tabela nova.
- **Painel do aluno (US-41)**: as ações "Excluir da turma", "Encerrar participação", "Editar" e
  "Transferir" ficam na lista de alunos da turma nesta entrega; a US-41 (Leandra Matos) pode levá-las
  ao painel do aluno, como o reset do primeiro acesso.
- **Restrições nas outras features**: os botões de editar TCC (US-13), indicar ou trocar orientador
  (US-17) e enviar entregas (US-16), e os bloqueios de entregas, atas, defesas e lembretes em turma
  arquivada, são das features donas; esta entrega oferece as verificações reutilizáveis (FR-008 e
  FR-025).
- **Relatório de evasão (US-32)**: lê o histórico do Status do TCC; esta feature só grava a transição.
- **Mensagens**: as MT-01 a MT-32 são provisórias e, como na spec 003 (Q25), não bloqueiam as
  tarefas nem a implementação.
- **Equivalência de cursos** (Q5; índice Q-17, Q-37 e Q-38): carregada por esta feature (FR-015a)
  com os três códigos completos, no formato do exemplo do dicionário (`EST08MCPD`); o dicionário não
  muda.
- **Diagrama de sequência "Matrícula por CSV"** (US-08): salvo em
  `docs/diagramas/US-08_matricula_por_csv.puml` e conferido com FR-012 a FR-018. O diagrama não
  mostra a orientação automática em TCC 2 de EC e LC (FR-004), que vem da matriz (RBN-CAD-04.2) e
  continua valendo; nem os alunos já cadastrados com outro Status do TCC (por exemplo 'Em
  Andamento' em outra turma), caso para o `/speckit-clarify`.
- **Leitura de XLSX** (Q4): dependência nova, a definir no plano e aprovar com o Célio Benjamim.
- **Dependências**: specs 001 e 003 implementadas; o login, a base visual, a verificação de perfil e
  o log vêm da spec 003.
