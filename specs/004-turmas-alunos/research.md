# Research: Turmas e Alunos do SIGTCC

**Feature**: [spec.md](spec.md) (aprovada em 2026-10-20) | **Plano**: [plan.md](plan.md) | **Data**: 2026-10-20

Formato: Decisão / Justificativa / Alternativas. As decisões partem do modelo da spec 001 (nenhuma
tabela ou coluna nova, FR-028), dos serviços compartilhados da spec 003
(`specs/003-acesso-login/contracts/servicos-compartilhados.md`), das Clarifications Q1 a Q17 da spec
004 e do diagrama `docs/diagramas/US-08_matricula_por_csv.puml` (hoje página MatricularAluno de
`docs/diagramas/Diagramas_Sequencia_24_10.drawio`). Os IDs B1, B2… são desta feature.

**Revisão de 2026-10-21**: o `arquiteto-django` revisou o plano (3 bloqueantes, 13 importantes, 20
menores). Todos foram aplicados; as decisões de comportamento viraram as Clarifications Q13 a Q17 da
spec. Cada correção cita o achado entre colchetes, por exemplo [B-2], [I-7], [m3].

---

## B1. Organização do código no app `cadastro`

**Decisão**: tudo no app `cadastro` (Épico 1), em módulos próprios, para não misturar com o acesso
da spec 003:

| Arquivo | Conteúdo |
|---|---|
| `services_turmas.py` | turmas, matrícula, transferência, exclusão e encerramento, entregas do aluno, verificações reutilizáveis |
| `importacao.py` | leitura segura do CSV e do XLSX, validação do modelo e das linhas, prévia |
| `forms_turmas.py` | formulários da turma, da matrícula, da importação, da edição do aluno, da transferência, da exclusão e do encerramento |
| `views_turmas.py` | views finas que chamam os serviços |
| `permissoes.py` | + regras de permissão por turma (B2), junto das regras da spec 003 [m14] |
| `services.py` | + `notificar()` (B21) e `EventoAcesso.TURMA_EXCLUIDA` (B4) |
| `urls.py`, `menu.py`, `mensagens.py` | rotas, item "Turmas", textos das US-07, 08, 09 e MT-01 a MT-30 |

Templates em `sigtcc/templates/cadastro/turmas/`. Os módulos com sufixo `_turmas` e `importacao.py`
são acréscimos à árvore do PGCS 2.3. O princípio IV da constituição fala em `services.py`; aqui é
**exceção justificada** (Complexity Tracking do plano), e a alternativa de transformar `services.py`
num pacote que reexporta tudo fica para o Célio decidir (índice Q-42) [m15].

**Alternativas**: novo app `turmas` (o PGCS 2.3 põe Turmas no `cadastro`, Épico 1); pacote
`services/` com `__init__` que reexporta (mantém as importações; decisão de configuração).

## B2. Quem pode o quê em cada turma (FR-009, FR-010; spec Q9 e Q27 da spec 003) [I-6][I-7][m14]

**Decisão**: as regras ficam em `permissoes.py`, ao lado das da spec 003:
- `pode_consultar_turma(usuario, turma)`: Professor da Disciplina da turma (`tur_doc_id ==
  usuario.pk`) ou Secretaria do curso da turma (`Secretarios.sec_cur_id == tur_cur_id`).
- `pode_alterar_turma(usuario, turma)`: só o Professor da Disciplina da turma.
- `pode_transferir(usuario, turma)`: Professor da Disciplina da turma ou Secretaria do curso.

`services_turmas.turma_para(usuario, tur_id, acao)`, com `acao` em constantes `CONSULTAR`, `ALTERAR`
e `TRANSFERIR`, confere **nesta ordem**: existência (404), permissão (`PermissionDenied`, M-02 da
spec 003 pelo `handler403`), e só então, para `ALTERAR` e `TRANSFERIR`, turma arquivada
(`TurmaArquivada` → MT-25). Assim um docente de fora não descobre se a turma está arquivada. Nas
operações que gravam, `turma_para(..., travar=True)` usa `select_for_update` dentro de
`transaction.atomic()` e confere tudo depois de travar.

**Vínculo do aluno com a turma** [I-7]: `vinculo_na_turma(turma, alu_id)` devolve o aluno só se
existir `Alunos_Turmas` com essa turma (404 se não), e é chamado em **todas** as rotas
`/turmas/<tur_id>/alunos/<alu_id>/...`, também no GET. Encerramento e transferência exigem ainda o
TCC do aluno nessa turma.

As listas usam `@perfil_requerido("docente", "secretaria")`; o item "Turmas" vai para `menu.py` com
`perfis=("docente", "secretaria")`. A lista de excluídos ou transferidos é só do Professor da
Disciplina (FR-026; matriz RBN-CAD-05.8) [I-4].

**Tela `/alunos/<alu_id>/` da spec 003** [I-8]: mostra e-mail e status de qualquer aluno a qualquer
Professor da Disciplina (decisão da spec 003, Q9; observação de LGPD S-02 do índice). Esta feature
não liga a lista de alunos a essa tela para a Secretaria (que levaria 403); para o Professor, o
link só aparece nos alunos da própria turma. Restringir a tela é bugfix da spec 003, a decidir
(registrado na S-02).

## B3. Turma e disciplina (FR-001 a FR-005; RBN-CAD-04.1 a 04.3; spec Q15)

**Decisão**:
- O Código da Disciplina vira `Disciplinas` por `get_or_create(dis_codigo=...)`; editar o código
  aponta a turma para outra disciplina e não apaga a anterior.
- `Turmas.tur_doc` = Docente logado na criação; `tur_status = 'Ativa'`.
- Validação (todos os erros por campo): Código `^[A-Z0-9]{1,20}$` (MT-01); Identificador
  `^[A-Z0-9_]{1,30}$` (MT-02) e único (MT-03); `IntegrityError` de `tur_identificador` num cadastro
  simultâneo também vira MT-03 [m3]; Ano `^[1-9]\d{3}$` (MT-04; "0123" violaria
  `ck_turmas_tur_ano`) [m1]; Local até 100 (MT-05), com espaços das pontas removidos, espaços
  repetidos juntados e sem caracteres de controle [m9]; término > início ("O horário de término deve
  ser posterior ao de início"); obrigatório vazio → M-14.
- **Trava de Descrição e Curso (Q15)** [I-12]: na turma que tem ou já teve aluno — existe
  `Alunos_Turmas`, `TCCs`, `Historico_Status_TCC` ou `Historico_Alunos_Turmas` (origem ou destino)
  da turma —, os dois campos vão `disabled` e o serviço ignora o que vier para eles. O mesmo teste
  `turma_ja_teve_aluno(turma)` serve à exclusão (B4, Q12).
- Horários `HH:MM` (24 h); Semestre, Dia da Semana, Descrição e Curso são listas.

## B4. Exclusão de turma (FR-006; RBN-CAD-04.4; spec Q12)

**Decisão**: `excluir_turma(professor, tur_id)` com a turma travada (B2). Só exclui se
`turma_ja_teve_aluno(turma)` for falso; senão, "A turma possui alunos matriculados. Use a opção
Arquivar". Apaga as `Turmas_Marcos` da turma e a turma. O evento vai ao log por
`transaction.on_commit` (não registra exclusão desfeita) [m4]:
`registrar_evento(EventoAcesso.TURMA_EXCLUIDA, conta=None, autor=professor,
detalhe=f"tur_id={id} identificador={identificador}")`. O identificador já passou pela regex
`^[A-Z0-9_]{1,30}$`, então não leva texto livre ao log, como pede a §5 do contrato da spec 003.

Concorrência com outras features: quem grava em tabela ligada à turma (por exemplo `Turmas_Marcos`)
usa `travar_turma_ativa` (B5), e a trava da exclusão serializa as duas operações [I-6].

## B5. Arquivamento e turma ativa (FR-007, FR-008; RBN-CAD-04.5) [I-6]

**Decisão**: `arquivar_turma(professor, tur_id)` com a turma travada, conferindo nesta ordem: (a)
`TCCs` da turma 'Em Andamento' ou 'Apto para Defesa'; (b) `Defesas` de TCC da turma 'Agendada',
'Reagendada' ou 'Em Andamento'; (c) só em TCC 2: `Turmas_Marcos` 'Versão Final' com `tma_data_limite <
timezone.now()`. Primeiro motivo encontrado volta com o texto exato da US-07. Sucesso: `tur_status =
'Arquivada'` (MT-10).

Contrato §1 (para as outras features):
- `turma_arquivada(turma) -> bool` (consulta, sem trava);
- `travar_turma_ativa(tur_id) -> Turmas`: dentro de `transaction.atomic()`, faz `select_for_update`,
  relê a turma e levanta `TurmaArquivada` se arquivada. **Obrigatória** para quem grava em tabela
  ligada à turma (entregas, envios, atas, agendamento de defesa, Versão Final);
- `exigir_turma_ativa(turma)` só para telas (decide se o botão aparece), nunca como garantia de
  gravação.

## B6. Matrícula de um aluno (FR-011 a FR-015; RBN-CAD-05.1, 05.5, 05.7; spec Q3, Q5 a Q7, Q16, Q17)

**Decisão**: `matricular(professor, turma, matricula, nome, codigo_curso) -> ResultadoMatricula`,
usado pela matrícula individual e por cada linha da importação, com a turma travada. Ordem (igual
ao diagrama):

1. Normalização e formato [m2]: tudo em NFC (`unicodedata.normalize`), espaços das pontas removidos
   e repetidos juntados. Matrícula `^\d{10}$` ("A matrícula deve ter 10 dígitos numéricos"); Nome:
   só letras latinas, inclusive acentuadas (cada letra com `str.isalpha()` e
   `unicodedata.name(c)` começando com "LATIN", o que exclui `×`, `÷`, `ª`, `º` e outras escritas)
   [N6] e espaços, até 150 (MT-11); Curso `^[A-Z0-9]{1,20}$` (MT-12).
2. Curso: `curso_do_codigo(codigo)`, definida em `services.py` (módulo de base); `services.
   curso_do_aluno` delega a ela e `services_turmas` a reexporta, sem importação circular
   (`services_turmas` importa `services`, nunca o contrário) [m13][N2]; sem correspondência → "Código não reconhecido"; diferente de
   `tur_cur` → alerta MT-13 (não impede).
3. Aluno pela matrícula, travado com `select_for_update` se existir [m8].
4. Já em `Alunos_Turmas` desta turma → "Aluno já matriculado nesta turma".
5. Aluno existente (Q7, conferido em **todos** os TCCs, não só no último) [m5]:
   - algum TCC 'Sem Proposta', 'Em Andamento' ou 'Apto para Defesa' em turma não arquivada → MT-26
     (com o identificador dessa turma);
   - algum TCC 'Aprovado', 'Aprovado com Correções' ou 'Concluído' → MT-27;
   - último TCC 'Aprovado para TCC 2' e turma de TCC 2 → cópia (B7); em turma de TCC 1 → MT-28
     (índice Q-39);
   - senão ('Reprovado', 'Desistente', 'Jubilado', ou TCC só em turma arquivada) → novo TCC.
   Conta 'Inativa' ou 'Expirada' (Q16): matrícula aceita, conta não muda, aviso MT-29 com o status.
6. Aluno novo: `Usuarios.objects.create_user(None, nome, usu_status='Aguardando Ativação')` e
   `Alunos(alu_matricula, alu_codigo_curso)`. Nome e curso de aluno existente não mudam.
7. `Alunos_Turmas(mat_data_inscricao=timezone.now())`, TCC 'Sem Proposta' e
   `Historico_Status_TCC(anterior=None, novo='Sem Proposta', gatilho='Vínculo à turma',
   hst_usu=professor, hst_tur=turma)`.
8. Orientação automática (B8) e registros das entregas (B22).

Concorrência [m7]: a criação do aluno novo roda num savepoint próprio; `IntegrityError` em
`alu_matricula` (outro cadastro simultâneo) desfaz só esse savepoint e repete o passo 3 com o aluno
já existente. Na importação, os alunos já cadastrados são travados em ordem crescente de matrícula
antes da confirmação, para duas importações simultâneas não se travarem [m8].

## B7. Aprovado para TCC 2 → novo TCC carregado (FR-013; RBN-CAD-08.6; spec Q6) [I-13][m6]

**Decisão** (diagrama: `criar(aluno, turma, tccAnterior)`), nesta ordem:
1. Orientações e coorientações 'Ativa' do TCC 1 → 'Encerrada', com data de fim (ficam no
   histórico).
2. Cria o TCC na turma de TCC 2 **direto** como 'Em Andamento' (sem passar por 'Sem Proposta'),
   copiando `tcc_titulo`, `tcc_subtitulo`, `tcc_resumo`, `tcc_modalidade`, `tcc_link_proposta` e
   `tcc_ari`; `tcc_justificativa_encerramento` fica vazia.
3. `Historico_Status_TCC(anterior='Aprovado para TCC 2', novo='Em Andamento', gatilho='Transferência
   para TCC 2')`.
4. Copia `PalavrasChave_TCC` e, se houver, o `Artigos` com **todas** as colunas
   (`art_veiculo_publicacao`, `art_link_doi`, `art_qualis_capes`, `art_status_submissao`,
   `art_homologacao`, `art_homologado_por`, `art_data_homologacao`): é o mesmo registro de publicação
   "carregado" (RBN-CAD-08.6), sem nova homologação.
5. Orientação: em turma com orientador automático, cria a automática (B8) e copia os
   coorientadores ativos do TCC 1, **exceto** o professor da turma (que passa a orientador); nas
   demais (TCC 2 de SI), cria orientação com o orientador do TCC 1 (`ori_origem` igual à do TCC 1)
   e copia todos os coorientadores ativos.

O TCC 1 continua na turma de TCC 1 com o Status 'Aprovado para TCC 2'. **Aviso no contrato (§5)**:
relatórios de publicações e de aproveitamento (Épico 3) devem contar o aluno e a publicação uma vez,
pelo TCC mais recente.

## B8. Orientação automática (FR-004; RBN-CAD-04.2) [m12]

**Decisão**: `turma_tem_orientador_automatico(turma)` = TCC 2 e curso em
`CURSOS_COM_ORIENTADOR_AUTOMATICO`, constante única em `cargas.py` (onde já estão os nomes dos
cursos da carga da spec 001), comparada pelo `cur_id` lido desses nomes. A dependência do nome do
curso fica registrada no contrato (§3): renomear um curso (US-39) exige revisar a constante. Cria
`Orientacoes(ori_doc=tur_doc, ori_origem='Automático', ori_status='Ativa', ori_data_inicio=now)`.

## B9. Importação: leitura segura do arquivo (FR-016; RBN-CAD-05.2; spec Q2, Q4, Q11, Q13) [B-3][m20]

**Decisão**: `importacao.ler_arquivo(arquivo) -> LeituraArquivo | ErroModelo`. Qualquer recusa abaixo
mostra "Arquivo fora do modelo. Baixe o modelo de importação":
- até 2 MB pelo `size` do upload; extensão `.csv` ou `.xlsx`;
- **XLSX**: bytes iniciais de ZIP (`PK\x03\x04`); antes do `openpyxl`, abre com `zipfile` e recusa se
  a soma de `file_size` das partes passar de 20 MB ou alguma parte tiver razão de compressão acima
  de 100 (zip bomb); lê com `openpyxl.load_workbook(read_only=True, data_only=True)`, primeira
  planilha, e fecha com `wb.close()` num `finally`. **Dependências novas**: `openpyxl` e
  `defusedxml` (o `openpyxl` usa o `defusedxml` quando instalado, contra "billion laughs" e
  "quadratic blowup"), com versão exata no `requirements.txt` (índice Q-42);
- **CSV**: decodifica em `utf-8-sig` e, se falhar, `cp1252`; separador por `csv.Sniffer` restrito a
  `";,"` sobre a linha de cabeçalhos (trata aspas) [m20]; `csv.reader`;
- **até 200 linhas de dados** (Q13): a leitura para na 201ª linha não vazia e recusa o arquivo;
- cabeçalhos em NFC, sem diferenciar maiúsculas e sem espaços nas pontas: Matrícula, Nome Completo e
  Curso, em qualquer ordem; colunas extras e linhas vazias ignoradas;
- células numéricas do XLSX viram texto sem ".0";
- exceções de leitura (`csv.Error`, `UnicodeDecodeError`, `zipfile.BadZipFile`,
  `openpyxl.utils.exceptions.InvalidFileException`, `KeyError`, `ValueError`, `OSError`) viram erro
  de modelo, nunca 500.

## B10. Importação: prévia e confirmação (FR-017, FR-018; diagrama) [B-2][I-10]

**Decisão**:
- `importacao.montar_previa(turma, linhas)` classifica cada linha como o diagrama (inválida, já
  matriculada, já cadastrada, nova, recusas MT-26 a MT-28, aviso MT-29, alerta de curso). Matrícula
  repetida no arquivo: a segunda é "Aluno já matriculado nesta turma".
- A prévia vai para `request.session["importacao"]` com: `token` (`secrets.token_urlsafe(16)`),
  `tur_id`, instante (ISO, sem fuso) e **só** as linhas válidas normalizadas (matrícula, nome,
  código do curso); das linhas com erro guarda só o número e o motivo [I-10]. Vale 30 minutos e uma
  por vez; enviar outro arquivo, de qualquer turma, substitui a anterior.
- "Confirmar importação" (POST com CSRF) traz o `token` num campo oculto. A view exige prévia na
  sessão, `token` igual, `tur_id` igual ao da URL e prazo em dia; senão volta para a importação com
  aviso e não grava nada [B-2]. A prévia **sai da sessão antes** de gravar (duplo clique e F5 não
  repetem a importação), e o `token` é marcado como usado de forma atômica com
  `caches["default"].add(f"importacao:{token}", 1, 3600)`: se já estiver marcado, um segundo POST
  simultâneo volta para a turma sem gravar nem trocar o resumo [N3]. O cache padrão (arquivo, até 300
  entradas) pode descartar entradas ao acaso, mas a marca só precisa durar os segundos entre dois POST
  simultâneos; a prévia já saiu da sessão e a turma travada impede dado duplicado (análise D5).
- Gravação: turma travada; alunos já cadastrados travados em ordem de matrícula (B6); `matricular`
  linha a linha, cada uma num savepoint; uma falha por mudança desde a prévia vai para as
  rejeitadas sem desfazer as outras (Q2).
- Resumo (MT-15) por POST/redirect/GET: só os números e as rejeitadas (número e motivo) ficam na
  sessão até a página do resumo ser mostrada.
- "Cancelar" na prévia remove a prévia; prévias vencidas somem na próxima importação e com o
  `clearsessions` agendado (índice Q-42). Abrir outra turma não mexe na prévia (GET não muda estado;
  o `token` e o `tur_id` já impedem a confusão de turmas) [N4].

**Desempenho (SC-003)**: até 200 linhas por arquivo; 60 linhas em até 10 segundos com folga. O teste
mede com margem e não usa `assertNumQueries` exato [m19].

## B11. Modelo de importação (FR-016; Q11)

**Decisão**: rota que devolve `modelo_importacao_alunos.csv`, gerado na hora: UTF-8 com BOM, ";", a
linha de cabeçalhos e uma de exemplo (`2415080008;Nome Completo do Aluno;EST08MCPD`).

## B12. Edição do aluno (FR-019; RBN-CAD-05.3) [I-7]

**Decisão**: `editar_aluno(professor, tur_id, alu_id, nome, codigo_curso)`: turma do Professor, não
arquivada, travada; aluno pelo `vinculo_na_turma` (404 se não matriculado nela); grava
`Usuarios.usu_nome` e `Alunos.alu_codigo_curso` com as regras do B6. Sucesso: MT-14.

## B13. Transferência (FR-020 a FR-022; RBN-CAD-05.6; spec Q17) [I-1][m6][m11]

**Decisão**: `transferir(autor, tur_origem_id, alu_id, tur_destino_id, justificativa)`, travando as
duas turmas em ordem de `tur_id` e depois o TCC (B17):
- permissão `TRANSFERIR` na origem (B2); origem com orientador automático (B8); aluno pelo
  `vinculo_na_turma` e TCC do aluno na origem;
- destinos possíveis: TCC 2, mesmo `tur_cur`, mesmo `tur_ano` e `tur_semestre`, 'Ativa', `tur_doc`
  diferente do da origem **e sem `Alunos_Turmas` nem `TCCs` do aluno** (evita
  `uq_tccs_aluno_turma` e a PK de `Alunos_Turmas`) [I-1]; nenhum → MT-19;
- TCC 'Em Andamento' ou 'Apto para Defesa' (senão MT-17); sem `Defesas` 'Agendada', 'Reagendada' ou
  'Em Andamento' (senão MT-18); Justificativa obrigatória até 500 (B18);
- efeito, nesta ordem: orientação automática ativa → 'Encerrada' com data de fim **antes** de criar
  a nova (unicidade de uma ativa por TCC) [m6]; `TCCs.tcc_tur = destino`; `Alunos_Turmas` da origem
  removido e criado no destino; nova orientação automática com o professor do destino; coorientação
  ativa do professor do destino → 'Encerrada'; convites de **coorientação** pendentes para o
  professor do destino (`sol_tipo='Coorientação'`, 'Aguardando Aceite') → 'Cancelado', com
  `sol_data_resposta` = data do cancelamento [m11][N5c]; entregas: as da
  origem sem envio são apagadas e as com envio ficam; o aluno ganha os registros das entregas do
  destino (B22, Q17); `Historico_Alunos_Turmas(tipo='Transferência', origem, destino,
  justificativa, hst_usu=autor)`; notificações MT-22 pelo `notificar()` (B21) para o aluno (sem
  link) e os dois orientadores (o novo com o link da turma de destino); MT-16.

## B14. Exclusão do aluno (FR-023; RBN-CAD-05.4; spec Q8, Q17) [B-1]

**Decisão**: duas etapas na mesma tela: (1) Justificativa e "Confirmar"; (2) confirmação final com a
MT-24, a justificativa num campo oculto, "Confirmar" e "Cancelar". `excluir_aluno(professor, tur_id,
alu_id, justificativa)` com a turma e o TCC travados e o aluno pelo `vinculo_na_turma`:
- TCC 'Sem Proposta' (senão "O aluno já tem Proposta. Use Encerrar participação");
- se o TCC tiver encontro (ata), orientação por pedido aceito, coorientação, palavra-chave,
  publicação ou defesa, a exclusão é recusada com a mesma mensagem (o trabalho já foi
  movimentado). Pedido de orientação ou convite de coorientação **não** impede (leitura da
  RBN-CAD-05.4 revista em 2026-10-24: o que decide é o Status "Sem Proposta"; spec, Clarifications
  Q20; índice Q-120). Na exclusão, os pendentes são cancelados com a MT-33 ao docente, cada
  solicitação vai para o log de acesso (`EventoExclusao.SOLICITACAO_REMOVIDA`: tipo, docente,
  status e datas; RNF de Não Repúdio do RAN-CAD-10) e todas são apagadas antes do TCC;
- apaga, nesta ordem: `Historico_Status_TCC` do TCC, orientação automática do TCC, o TCC, os
  registros de entrega do aluno nas entregas da turma **sem envio** (os com envio ficam como
  histórico, Q17; a exclusão não é recusada por eles), o `Alunos_Turmas`;
- grava `Historico_Alunos_Turmas(tipo='Exclusão', destino=None)` e notifica o aluno com a MT-21 pelo
  `notificar()`, que corta a justificativa com "…" para o texto caber em 500 caracteres [B-1].

## B15. Encerramento da participação (FR-024; RBN-CAD-08.4; spec Q10, Q14) [I-2]

**Decisão**: `encerrar_participacao(professor, tur_id, alu_id, status, justificativa)`, travando a
turma e depois o TCC (B17) e conferindo de novo, depois de travar, que o TCC ainda é da turma e o
Status:
- TCC 'Em Andamento' ou 'Apto para Defesa'; Status em Desistente, Reprovado ou Jubilado ("Selecione o
  Status do aluno"); Justificativa obrigatória até 500;
- sessão 'Agendada', 'Reagendada' ou 'Em Andamento' → recusa com MT-30 (Q14);
- grava `tcc_status`, `tcc_justificativa_encerramento`, `Historico_Status_TCC(gatilho='Encerramento
  da participação', hst_usu=professor)`; orientações e coorientações 'Ativa' → 'Encerrada' com data
  de fim (Q10); `Solicitacoes_Orientacao` do TCC 'Aguardando Resposta' ou 'Aguardando Aceite' →
  'Cancelado', com `sol_data_resposta` = data do cancelamento (Q14; o `CHECK` de status por tipo da
  spec 001 aceita 'Cancelado' nos três tipos), e o docente de cada pedido recebe a MT-31 pelo
  `notificar()` (Q19). MT-23.

Contrato §2: `participacao_encerrada(tcc) -> bool` (Desistente, Reprovado ou Jubilado), com as
constantes `STATUS_PARTICIPACAO_ENCERRADA` e `STATUS_TCC_EM_CURSO` ('Sem Proposta', 'Em Andamento',
'Apto para Defesa'), nomes distintos do "TCC ativo" da RBN-CAD-01.3 (spec 002) [m17].

## B16. Lista de excluídos ou transferidos (FR-026; RBN-CAD-05.8) [I-4]

**Decisão**: `Historico_Alunos_Turmas` com `hat_tur_origem = turma`, do mais recente para o mais
antigo: nome e matrícula do aluno, tipo, data e hora, autor, justificativa e, na transferência, a
turma de destino. Só leitura, **só para o Professor da Disciplina** (matriz e FR-026).

## B17. Concorrência: travas por serviço [I-2][m8]

**Decisão**: toda trava acontece dentro de `transaction.atomic()`, sempre na ordem turma(s) → aluno
→ TCC, e os serviços conferem tudo de novo depois de travar.

| Serviço | Travas, em ordem |
|---|---|
| `matricular` (e cada linha da importação) | turma → aluno existente |
| confirmação da importação | turma → alunos existentes, em ordem de matrícula |
| `editar_turma`, `excluir_turma`, `arquivar_turma` | turma |
| `editar_aluno` | turma → aluno |
| `transferir` | as duas turmas, em ordem de `tur_id` → TCC |
| `excluir_aluno` | turma → TCC |
| `encerrar_participacao` | turma → TCC |
| outras features que gravam em tabela ligada à turma | `travar_turma_ativa(tur_id)` (B5) |

## B18. Formulários e textos

**Decisão**: base `FormularioSigtcc` em `forms_turmas.py`: M-14 para obrigatório e **todos** os erros
por campo (a regra do primeiro erro é só do primeiro acesso, spec 003 Q12). Justificativas e Local
[m9]: NFC, espaços das pontas removidos, espaços repetidos juntados; texto só com espaços é vazio
("Informe uma justificativa de até 500 caracteres" nas justificativas; M-14 no Local); quebras de
linha viram espaço; caracteres de controle são recusados. Mensagens em `mensagens.py`: textos
exatos das US-07, 08 e 09 e as MT, com `{identificador}`, `{nome}`, `{status}`. Curso com sugestões
por `<datalist>` (sem JavaScript).

## B19. Telas (protótipo de 17/10, só o visual)

**Decisão**: telas "Gerenciar turmas de TCC", "Matricular alunos na turma" e "Excluir aluno da turma"
com a base visual da spec 003: lista de turmas em cartões, turma com cabeçalho e lista de alunos
(tabela com ações por linha), prévia em tabela com contadores. Confirmações em página própria.

## B20. Carga da equivalência de cursos (FR-015a; spec Q5)

**Decisão**: migração de dados em `cadastro/migrations/` com `EST08MCPD`, `EST31MSII` e `EST03MLV` →
cursos pelo `cur_nome`, idempotente (`get_or_create`) e reversível por SQL (padrão das cargas da
spec 001).

## B21. Serviço `notificar()` [I-5][B-1]

**Decisão**: a spec 004 é a primeira feature que cria notificações. `services.notificar(usuario,
mensagem, link=None)` (acréscimo ao contrato da spec 003, índice Q-42): corta `mensagem` em 500
caracteres com "…" no fim, aceita `link` só se `destino_da_notificacao(link)` o aceitar (senão grava
sem link), preenche `not_data_hora = timezone.now()` e `not_lida = False`. Os templates com campos
(MT-21, MT-22) cortam primeiro a parte variável longa (a justificativa), para o resto da frase ficar
inteiro. Teste: exclusão com justificativa de 500 caracteres e identificador de 30.

## B22. Registros das entregas do aluno (spec Q17) [I-3]

**Decisão**: `criar_entregas_do_aluno(aluno, turma)`: para cada `Turmas_Marcos` da turma, cria
`Entregas_Marcos(ent_tma, ent_alu, ent_status='Aguardando Envio')`; se já existir um registro de um
vínculo anterior (`uq_entregas_marcos_aluno_atividade`), ele volta para 'Aguardando Envio', com
`ent_feedback`, `ent_data_avaliacao` e `ent_correcoes_conferidas_em` vazios, e os envios anteriores
ficam em `Historico_Envios_Entregas` (spec Q18) [N1]. Usado na matrícula e na transferência
(destino).
`remover_entregas_sem_envio(aluno, turma)`: apaga os `Entregas_Marcos` do aluno nas entregas da
turma sem nenhum `Historico_Envios_Entregas`; os com envio ficam. Usado na exclusão e na
transferência (origem). Entregas cadastradas depois da matrícula: a US-43 cria os registros dos
alunos já matriculados (índice Q-41).

**Regra para as outras features** (contrato §3) [N1]: listas de entregas, lembretes de prazo, a
marcação 'Não Entregue' (US-15) e os relatórios de entrega consideram só alunos com `Alunos_Turmas`
atual na turma e com a participação não encerrada (`participacao_encerrada`); registros com envio de
alunos excluídos ou transferidos ficam só como histórico.

**Testes do XLSX** [N7]: um teste confere que o `openpyxl` está usando o `defusedxml`
(`openpyxl.xml.DEFUSEDXML is True`); o limite de razão de compressão (100) é conferido com uma
exportação real do sistema acadêmico da UEA antes de fechar a tarefa.

## B23. Limites do upload e dados na sessão [I-9][I-10]

**Decisão**: o Django grava o upload inteiro num arquivo temporário antes da view; o limite real fica
no servidor web (cerca de 2,5 MB, por exemplo `client_max_body_size` no nginx ou o equivalente no
IIS) ou num upload handler que aborte acima disso — item de configuração para o Célio (Q-42), que
também protege a assinatura da spec 003. A prévia guarda só o mínimo (B10) e há rotina agendada de
`clearsessions` (Q-42).

## B24. Testes e apoio [m19]

**Decisão**: `tests/apoio_turmas.py` com fábricas de turma, aluno matriculado, TCC em cada Status,
defesa, entrega com e sem envio e arquivos CSV e XLSX em memória. Acréscimo compatível em
`apoio_acesso.criar_secretaria(..., curso=None)` para testar "Secretaria do curso da turma". Os
serviços chamam `timezone.now()` pelo módulo (o `avancar_relogio` troca `django.utils.timezone.now`).
Testes de tempo com margem.

## B25. Exportações e relatórios (Épico 3) [m18]

**Decisão**: aviso no contrato (§5): justificativas são texto livre e entram nos relatórios de
evasão; o exportador CSV e XLSX do Épico 3 deve neutralizar fórmulas (`=`, `+`, `-`, `@` no início
da célula). Nome e código de curso já passam por regex. A versão do `openpyxl` vale também para o
`relatorios/services.py`.
