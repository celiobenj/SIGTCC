# Research: Gestão de Contas do SIGTCC

**Feature**: [spec.md](spec.md) | **Plano**: [plan.md](plan.md) | **Data**: 2026-10-22

Decisões técnicas do Phase 0. Cada uma no formato Decisão / Por quê / Alternativas. Os IDs C1 a C24
são citados no plano, no data-model, nos contratos e, depois, nas tarefas.

**Revisão de 2026-10-22**: o `arquiteto-django` revisou o plano (2 bloqueantes, 11 importantes, 13
menores). Os ajustes técnicos foram aplicados aqui, marcados com o ID do achado (B1, I1...). Os que
dependiam de decisão de comportamento foram decididos pela responsável (plan, "Decisões da revisão";
spec, Clarifications Q30 a Q35).

## C1. Onde fica o código

- **Decisão**: no app `sigtcc/apps/cadastro`, em módulos novos por assunto, como na spec 004:
  `services_contas.py` (regras), `forms_contas.py`, `views_contas.py` e os comandos
  `criar_coordenadores.py` e `expirar_membros_externos.py`. Templates em
  `sigtcc/templates/cadastro/contas/`. Ajustes pontuais em `services.py`, `permissoes.py`,
  `mensagens.py`, `urls.py`, `menu.py` e `views.py` (`acesso_negado`, C21).
- **Por quê**: `services.py` já tem 1.136 linhas e é contrato da spec 003; a spec 004 já usou o
  mesmo padrão, que está em aprovação com o Célio (índice Q-42 e Q-70).
- **Alternativas**: tudo em `services.py` e `views.py`; um app novo `contas` (fora do PGCS 2.3).

## C2. Curso do usuário e alcance das ações (FR-009; Clarifications Q5 e Q26) [I11]

- **Decisão**: em `permissoes.py` (funções puras, só leem `models` do cadastro):
  `curso_do_usuario(usuario)` → Curso Coordenado (`Coordenadores.cor_cur`) do Coordenador,
  `Secretarios.sec_cur` da Secretaria, `None` para os demais; `curso_do_registro(registro)` →
  `Docentes.doc_cur` (Curso de Lotação, Q26) ou `Secretarios.sec_cur`; `pode_gerir(usuario,
  registro)` compara os dois com o valor **atual** do registro, relido depois da trava no serviço
  (C19). O Curso Coordenado escolhido no formulário pode ser qualquer curso sem Coordenador (Q5).
- **Por quê**: segue a US-03 (Q26) e o RBN-CAD-14.1; a mesma função serve à lista (botões), ao
  serviço (recusa) e aos testes (SC-004).
- **Alternativas**: guardar o curso na sessão (fica velho quando o papel muda).

## C3. Permissões por ação e direção das importações [I11]

- **Decisão**: as views usam `@perfil_requerido` da spec 003 para o perfil; o vínculo com o objeto
  fica no serviço, que confere de novo depois da trava (C19):
  - perfil e curso: `permissoes.py` (C2);
  - Professor da Disciplina que altera dados: `permissoes.professor_com_turma_ativa` (Q10);
  - consultas que leem `Banca_Defesa` (vínculo do Orientador, vínculos da inativação, validade):
    `services_contas.py`, que importa `sigtcc.apps.defesa.models`.
  Direção das importações (sem ciclo): `views_contas` → `services_contas` → `services` →
  `permissoes` → `models`; `services_contas` → `defesa.models`. `permissoes.py` nunca importa
  `defesa`; `defesa.models` nunca importa `services_contas` (a Defesa chama o contrato a partir das
  suas views ou serviços).
- **Por quê**: contrato da spec 003, §2; `permissoes.py` é importado por `backends.py` e `services.py`.
- **Alternativas**: decorador novo por curso (repetiria a regra fora do serviço).

## C4. Unicidade do e-mail, inclusive em gravações simultâneas (FR-001; SC-003) [I4]

- **Decisão**: antes de conferir e gravar um e-mail (cadastro, comando, pedido de troca e, na spec
  003, `confirmar_troca_email`), a transação pega a trava consultiva
  `SELECT pg_advisory_xact_lock(hashtext(lower(%s)))` com o e-mail normalizado; depois roda
  `email_em_uso` (sem diferenciar maiúsculas) e grava. A restrição única de `usu_email` continua como
  segunda barreira (IntegrityError → "Este e-mail já está cadastrado"). Formato: Docente e
  Secretaria com `@uea.edu.br` e até 100 caracteres; Membro Externo com qualquer domínio
  (validador do Django) e até 100 caracteres. Utilitário `travar_email(email)` em `services.py`
  (acréscimo ao contrato da spec 003; ciência da Julia, Q-71).
- **Por quê**: o índice único diferencia maiúsculas; "Maria@" e "maria@" gravados ao mesmo tempo
  passariam, e o login das duas contas pararia (EMAIL_DUPLICADO). Sem coluna nem índice novo
  (o índice em `lower(usu_email)` continua opcional, Q-28).
- **Alternativas**: trava da tabela inteira; índice funcional (exige o dicionário).

## C5. Um Coordenador e uma Secretaria por curso (FR-014, FR-021; US-03 E3)

- **Decisão**: toda gravação que cria ou move um Coordenador ou uma Secretaria trava a linha do
  curso (`Cursos.objects.select_for_update()`), na ordem global da C19, e só então confere a regra.
  O Coordenador também tem as restrições de `Coordenadores` (PK em `cor_cur`, único em `cor_doc`).
  A Secretaria conta 'Aguardando Ativação' e 'Ativa' (Q7).
- **Por quê**: "uma Secretaria por curso" não tem restrição no banco (dicionário, regra 12).
- **Alternativas**: índice único parcial (exige o dicionário; Q-60).

## C6. Papel de Coordenador (FR-013, FR-014; US-03 A1 a A3 e A10) [I7, m11]

- **Decisão**: marcar o papel cria a linha em `Coordenadores`; trocar o Curso Coordenado apaga a
  linha antiga e cria a nova na mesma transação; desmarcar apaga a linha. A edição trava a conta do
  docente e os cursos envolvidos na ordem da C19, relê o status e grava. Marcar o papel para docente
  'Inativa' é recusado com a MC-10 (spec Q32; D3). Depois de gravar, a view redireciona (PRG): quem desmarcou o próprio papel
  perde o menu de Coordenador já na página seguinte (`_papeis_cache` vale só para a requisição).
  Formulário: o campo Curso Coordenado fica sempre no HTML e é ignorado com a caixa desmarcada; o
  `sigtcc.js` só mostra e esconde.
- **Por quê**: `Coordenadores` é a única fonte do papel (dicionário 3.3.1; `permissoes.papeis`).

## C7. Troca de e-mail pelo gestor (FR-008; Q17, Q24, Q28) [B2, I3, m12, m13]

- **Decisão**: reaproveitar `services.pedir_troca_email(conta, novo, autor=None)` da spec 003 (token
  assinado com o novo e-mail e o resumo do e-mail atual; confirmação por POST em
  `cadastro:confirmar_email`, sem login). Fluxo da alteração:
  1. o formulário tem "Sua senha" (sem `render_value`), obrigatório só quando o e-mail muda;
     conferido com `services.senha_atual_confere(request.user, senha)` (inclui a regra de 8 a 64
     caracteres); errada: MC-11 e evento `SENHA_GESTOR_INCORRETA` no log; nada é gravado;
  2. transação 1: trava a conta (C19), grava só os campos editáveis com `update_fields` (C20);
  3. transação 2, depois da 1: trava do e-mail (C4) e `pedir_troca_email`; falha no envio → MC-13
     (campos da 1 já gravados, e-mail sem mudança, Q24); sucesso → MC-12.
  "O e-mail mudou?" compara sem diferenciar maiúsculas: só a caixa da parte local não abre troca
  (m12; limitação registrada). A unicidade no formulário usa "Este e-mail já está cadastrado"; a
  M-05 só aparece na confirmação. Links pendentes de troca valem até vencer ou outro ser confirmado
  (Q28).
- **Ameaça (B2) e mitigação (spec Q30; D1)**: o link é confirmado por quem controla o novo
  endereço, e o dono da conta não é avisado. Mitigação decidida: a troca de e-mail de Membro
  Externo com conta 'Ativa' ou 'Expirada' é só da Secretaria e do Coordenador. `pode_trocar_email(usuario,
  conta)` em `services_contas.py`; o formulário mostra o campo só para leitura aos demais e o
  serviço recusa com M-02 se o e-mail vier diferente. Risco restante aceito e registrado.
- **Links antigos (spec Q31; D2)**: `confirmar_troca_email` (spec 003) passa a gravar
  `usu_link_gerado_em = agora` na mesma transação, o que invalida os links de ativação e de
  redefinição emitidos antes (estado `SUBSTITUIDO` da spec 003). Coluna existente; ciência da Julia
  (Q-71).
- **Limite de tentativas da senha (spec Q35; D6)**: sem limite; cada erro registra
  `SENHA_GESTOR_INCORRETA`.
- **Alternativas**: coluna de e-mail pendente (não existe no dicionário).

## C8. Verificação de vínculos na inativação (FR-026, FR-027; US-04 E1 a E7) [B1, m5]

- **Decisão**: `vinculos_do_docente(docente)` em `services_contas.py`, cinco contagens: (a) TCCs com
  orientação ou coorientação ativa do docente e Status do TCC Em Andamento, Apto para Defesa,
  Aprovado ou Aprovado com Correções sem a Versão Final homologada (marco 'Versão Final' com
  `ent_status` diferente de 'Homologada'), cada TCC uma vez; (b) convites 'Coorientação' em
  'Aguardando Aceite'; (c) `Banca_Defesa` em sessão 'Agendada', 'Reagendada' ou 'Em Andamento';
  (d) turmas 'Ativa' do docente; (e) linha em `Coordenadores`. Alerta com os motivos na ordem (a) a
  (e), motivo (a) sempre no plural (Q18), MC-05 a MC-07 no singular com N = 1 (Q14).
- **Concorrência (B1)**: a inativação trava a conta (`Usuarios`) e a linha de `Docentes`, na ordem
  da C19, e repete a verificação antes de gravar (cenário 15). Isso só fecha a corrida se **quem
  cria o vínculo** também travar a conta da pessoa e conferir 'Ativa' na mesma transação, no POST
  (contrato §1, regra de travas). No READ COMMITTED, o INSERT de uma turma ou convite pega só KEY
  SHARE em `Docentes` e não espera a trava da inativação; com a regra do contrato, as duas
  transações se serializam na linha de `Usuarios`. A spec 004 precisa do ajuste em `criar_turma`
  (Julia, Q-77); Vida do TCC e Defesa seguem o contrato (Q-67, Q-68). Teste com `TransactionTestCase`
  e duas conexões.
- **Nota (m5)**: um TCC 'Aprovado' sem a Versão Final homologada numa turma já arquivada bloquearia
  o docente para sempre. Se a homologação sempre levar o TCC a 'Concluído' (a confirmar com a
  Leandra, Q-76), basta o Status do TCC e a consulta ao marco sai.

## C9. Quantidade de orientandos (FR-017; RBN-CAD-11.3; Q8) [m6]

- **Decisão**: anotar a listagem com duas contagens: TCCs com `Orientacoes` 'Ativa' do docente em
  turma 'TCC 1' e em 'TCC 2'; alerta visual (`alerta aviso`) quando a soma passa de 5. Uma consulta
  para a página. Se a contagem exclui TCC encerrado ou turma arquivada é critério da US-18
  (Leandra, Q-76); até a resposta, conta toda orientação 'Ativa'.

## C10. Filtro de Curso (FR-018, FR-023; RBN-CAD-14.1; SC-009)

- **Decisão**: `?curso=<cur_id>` ou `?curso=todos`; sem parâmetro, o curso do usuário; valor
  inválido volta ao padrão. Sem paginação (dezenas por curso). Membros externos sem filtro (Q19).
  Teste de tempo com margem, sem `assertNumQueries` exato.

## C11. Quem vê "Prorrogar" (FR-042; Q11; US-50) [m7]

- **Decisão**: `pode_prorrogar(usuario, membro)` em `services_contas.py`: perfil (Secretaria,
  Coordenador, Professor da Disciplina com turma não arquivada, ou Orientador com orientação 'Ativa'
  de TCC com sessão não Cancelada e o membro em `Banca_Defesa`) **e** conta 'Ativa' ou 'Expirada'
  (ou validade vencida). A view confere primeiro a permissão (M-02) e só depois o status (MC-09),
  para não revelar o estado da conta a quem não pode. A lista anota o vínculo numa consulta.

## C12. Prorrogação (FR-043, FR-044) [m8]

- **Decisão**: POST em `membros-externos/<id>/prorrogar/`; numa transação, trava a conta (C19),
  relê `MembrosExternos` e calcula: 'Ativa' em dia → validade + 7; 'Expirada', vencida ou nula →
  hoje + 7 e status 'Ativa'; grava a mesma data em `mem_prorrogado_ate` (spec Q36). Redireciona
  para a lista com "Acesso prorrogado até DD/MM/AAAA" (PRG).
  O botão é desabilitado depois do clique (`sigtcc.js`, só apresentação); dois POSTs que cheguem
  mesmo assim somam 14 dias, como a US-50 cenário 3 (comportamento correto para dois cliques
  intencionais). Falha: "Não foi possível prorrogar o acesso. Tente novamente". Log
  `ACESSO_PRORROGADO`. Sem tela de confirmação (a US não pede).

## C13. Data da última prorrogação (Q15; índice Q-47 e Q-69) [I9]

- **Decisão**: o log da spec 003 é um arquivo (`LOG_DIR/acesso.log`), que pode ser girado ou apagado
  e fica fora da transação do banco: não serve para regra. Pedida à Maria Luiza Guimarães a coluna
  `MembrosExternos.mem_prorrogado_ate DATE NULL` (Q-69), **aprovada em 2026-10-22** (spec Q36). A
  prorrogação grava a nova validade em `mem_validade_ate` e em `mem_prorrogado_ate`; o recálculo
  usa `_data_protegida(membro)` (lê `mem_prorrogado_ate`) e nunca grava validade anterior a ela.
  O dicionário (cópia em `docs/fonte/`) é atualizado no mesmo commit do model e da migração, para
  o `test_conformidade_dicionario` continuar verde. A Defesa liga o recálculo depois da proteção
  implementada (spec Q34).

## C14. Regra de validade e recálculo (FR-037 a FR-039, FR-041; US-06) [I1, I8, m3, m9]

- **Decisão**: `recalcular_validade(usuario, hoje=None) -> bool` em `services_contas.py`:
  - **Quem chama e quando (I1)**: a Defesa, **dentro da sua transação**, depois de gravar o evento
    e o `Historico_Defesas`, uma vez por Membro Externo afetado. Para outros tipos de conta, devolve
    `True` sem fazer nada.
  - **Savepoint (I1)**: o cálculo roda num `transaction.atomic()` interno; a exceção é capturada
    **fora** dele, a validade anterior fica, o erro vai para o log só com `type(erro).__name__` e a
    conta (m3), e a função devolve `False`; a transação da Defesa continua válida.
  - **Trava (I1)**: `select_for_update(no_key=True, of=("self",))` na conta, que não conflita com o
    KEY SHARE dos INSERTs em `Banca_Defesa`; depois da trava, relê `MembrosExternos`.
  - **Cálculo** (só depende do banco: idempotente): (1) sessões com o membro em `Banca_Defesa`
    (como `ban_usu` ou como `ban_usu_substituido`, spec Q33) e `def_status` diferente de
    'Cancelada' → maior `def_data` + 7; (2) senão, o evento mais recente
    entre 'Cancelamento' de sessão em que ele está em `Banca_Defesa` e 'Alteração da Banca' com
    `hdf_membro_removido` = membro → data local de `hdf_data_hora` + 7; (3) senão, mantém a validade
    gravada (cadastro + 30). Depois, a proteção da C13: `max(resultado, mem_prorrogado_ate)` quando
    a coluna não é nula.
  - **Status**: validade hoje ou futura e conta 'Expirada' → 'Ativa'. Validade no passado e conta
    'Ativa' → grava 'Expirada' na hora (m9). 'Aguardando Ativação' não muda de status.
  - **Premissas sobre os dados da Defesa (I8)**, escritas no contrato §2: linhas de `Banca_Defesa`
    de sessão Cancelada são mantidas; a retirada apaga a linha e grava 'Alteração da Banca' com
    `hdf_membro_removido`; a substituição pelo suplente grava o substituído em
    `ban_usu_substituido` na mesma linha. A substituição mantém a validade do substituído e não é
    gatilho de recálculo (spec Q33; D4); a confirmação das premissas é do Célio (Q-67).
- **Alternativas**: sinal `post_save` em `Banca_Defesa` (acoplamento escondido).

## C15. Expiração automática (FR-040; Q3; SC-006) [I2]

- **Decisão**: regra única para o membro: **toda escrita de `usu_status` ou `mem_validade_ate` é
  feita com a conta travada e decide com dados relidos depois da trava** (expiração, prorrogação,
  recálculo, inativação). Função `expirar_se_vencida(usuario) -> bool` em `services.py` (não em
  `services_contas.py`, para `autenticar` usá-la sem importação circular): transação curta, trava,
  relê status e validade, grava 'Expirada' se ainda for 'Ativa' vencida, registra `CONTA_EXPIRADA`
  com autor "sistema" (C18).
  - Comando `expirar_membros_externos`: lista as candidatas ('Ativa' com validade antes de hoje) e
    chama `expirar_se_vencida` para cada uma (centenas de contas; custo baixo). Idempotente.
    Agendamento diário: Q-67, item 4, e Q-70.
  - `autenticar` (spec 003): no ramo de validade vencida, chama `expirar_se_vencida` dentro de
    `try/except`; uma falha nessa gravação não muda o resultado do login (EXPIRADA). Ciência da Julia
    (Q-71).
  - Telas tratam 'Ativa' vencida como 'Expirada' (`permissoes.validade_vencida`).
- **Por quê**: o `UPDATE` em massa filtrado por subconsulta reexpiraria uma conta prorrogada no
  mesmo instante (a subconsulta é avaliada antes da espera pela trava).

## C16. Mensagem de expiração (Q4; índice Q-52) [m10]

- **Decisão**: o login continua com `mensagens.ACESSO_EXPIRADO` (M-16 da spec 003). A constante
  `ACESSO_EXPIRADO_US06` (texto da US-06) entra em `mensagens.py` marcada como **provisória até a
  Q-52**, usada só pelo teste do cenário 3 da US-06, que fica como falha esperada com o ID da
  questão. Com a resposta da Julia, a M-16 recebe o texto e a constante provisória sai.

## C17. Comando dos Coordenadores iniciais (FR-045, FR-046) [m4]

- **Decisão**: `python manage.py criar_coordenadores --arquivo <caminho.csv>` ou, para um curso,
  `--curso --nome --email --titulacao`. CSV lido com `encoding="utf-8-sig"` (BOM do Excel),
  `newline=""`, `delimiter=";"`, colunas `curso;nome;email;titulacao`. Cada curso numa transação. O
  núcleo `_criar_docente(dados, autor)` (validações e gravação, sem conferir permissão) é chamado
  pelo comando e pelo serviço da tela `cadastrar_docente(usuario, dados)`, que confere a permissão
  antes; a view nunca chama o núcleo. Ordem das validações no comando: curso existe → curso já tem
  Coordenador → nome, titulação e e-mail (formato e unicidade); assim a segunda execução recusa com
  "O curso já possui Coordenador..." (quickstart). Saída por curso: "criado" ou "recusado:
  <mensagem>", **sem o e-mail**. A ajuda do comando avisa que `--email` fica no histórico do shell
  e recomenda `--arquivo`. Log `CONTA_CRIADA` com autor "sistema". Funciona com `DEBUG = False`.

## C18. Log, textos e rastreabilidade [I5, m3]

- **Decisão**: eventos novos em `EventoAcesso`: `CONTA_CRIADA`, `CONTA_ALTERADA`, `CONTA_INATIVADA`,
  `CONTA_REATIVADA`, `ACESSO_PRORROGADO`, `CONTA_EXPIRADA`, `VALIDADE_RECALCULADA`,
  `SENHA_GESTOR_INCORRETA`. Autor "sistema": constante `services.AUTOR_SISTEMA` aceita por
  `registrar_evento` (hoje `autor=None` vira "própria"; acréscimo ao contrato da spec 003, Q-71), com
  teste. Detalhe: tipo de conta, curso ou validade e, em `CONTA_ALTERADA`, só os **nomes** dos campos
  alterados; nunca valores, e-mail completo nem traceback (erros só com `type(erro).__name__`). Textos
  das US e MC-01 a MC-13 em `mensagens.py`; `M02_ACESSO_NEGADO` e `M14_CAMPO_OBRIGATORIO` com os
  textos das US (Q-50). `test_mensagens_contas.py` lê `docs/fonte/Historias_de_Usuario_v3_3.md`.

## C19. Ordem global das travas [B1, I7]

- **Decisão**: toda transação desta feature trava, nesta ordem e só o que precisa: (1) linhas de
  `Usuarios` em `usu_id` crescente (`select_for_update(of=("self",))`; no recálculo, `no_key=True`,
  C14); (2) a linha de `Docentes`, `Secretarios` ou `MembrosExternos` da conta; (3) linhas de
  `Cursos` em `cur_id` crescente; (4) trava consultiva do e-mail (C4). Depois das travas, relê tudo
  o que decide a regra (status, curso atual, vínculos). O contrato §1 pede o mesmo às features que
  criam vínculos.
- **Por quê**: evita deadlock entre edição, inativação, papel de Coordenador e Secretaria, e fecha
  a corrida do B1.

## C20. Gravação só dos campos editáveis [I3]

- **Decisão**: formulários de `Usuarios` são `forms.Form` (não `ModelForm`). O serviço relê a conta
  com trava e grava com `update_fields` explícito: `usu_nome`; `doc_titulacao`, `doc_cur`;
  `sec_cur`; `mem_titulacao`, `mem_instituicao`. `usu_status` só muda nas ações próprias;
  `usu_email` só por `confirmar_troca_email` (e na criação); a senha nunca é tocada.
- **Por quê**: `save()` sem `update_fields` regravaria status, senha e e-mail lidos no início da
  requisição, desfazendo uma inativação, uma troca de senha ou uma confirmação de e-mail feitas ao
  mesmo tempo.

## C21. Recusa por curso com a mensagem do FR-009 [m2]

- **Decisão**: exceção `ForaDoCurso(mensagem)` em `services_contas.py`; as views a capturam e
  renderizam `acesso_negado.html` com a mensagem e `status=403`. Acréscimo ao template da spec 003:
  aceitar uma mensagem no contexto (padrão continua M-02). `PermissionDenied` sem mensagem segue para
  o `handler403` (M-02).

## C22. Endereço direto e tipo de conta [m7]

- **Decisão**: as rotas buscam pelo modelo da especialização (`Docentes`, `Secretarios`,
  `MembrosExternos`) com `get_object_or_404`: um id de outro tipo de conta dá 404. A permissão é
  conferida antes de qualquer dado do registro aparecer na resposta.

## C23. Atalho da banca (`?voltar=`) [m1]

- **Decisão**: `destino_interno(valor, request)` aceita só caminho relativo começando com "/", que
  passa por `url_has_allowed_host_and_scheme` **e** resolve numa rota (`resolve()`, como
  `destino_da_notificacao` da spec 003). O valor vai num campo oculto e é revalidado no POST. O
  retorno acrescenta `membro=<mem_id>` com `urllib.parse` (o caminho pode já ter query). O contrato
  §3 diz que a tela da banca **valida** o membro recebido (disponível e permitido).

## C24. Testes e suíte existente [I10]

- **Decisão**: `test_mensagens.py` e `test_mensagens_turmas.py` (specs 003 e 004) abrem
  `Historias_de_Usuario_v3_2.md`, que não existe: a suíte já falha antes desta feature. A troca para
  `v3_3` nesses dois testes é combinada com a Julia (Q-77). `test_mensagens_provisorias_da_spec`
  (spec 003) só passa depois que esta feature trocar a M-02 e a M-14. Concorrência (B1, I4, C5)
  testada com `TransactionTestCase` e duas conexões. Testes pendentes de outras pessoas com o ID no
  motivo (Q-52).
