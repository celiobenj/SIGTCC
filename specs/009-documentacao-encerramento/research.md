# Research: Documentação e Encerramento do SIGTCC

**Feature**: [spec.md](spec.md) | **Plano**: [plan.md](plan.md) | **Data**: 2026-11-04 (revisão do
`arquiteto-django` incorporada em 2026-11-05: B-01 a B-03, I-01 a I-09, M-01 a M-14)

Cada item: **Decisão**, **Motivo** e **Alternativas rejeitadas**. Não há `NEEDS CLARIFICATION`
no Technical Context: as decisões de comportamento estão nas Clarifications da spec (P1 a P16,
Q-140, turma arquivada e B-03).

## B1. Organização do código no app `defesa`

- **Decisão**: dois módulos de regra no app `defesa` (Épico 2), cada um com seus forms e views:
  - documentos: `services_documentos.py` (já existe com os stubs da spec 008), `views_documentos.py`
    (Ata, Folha, Declaração e agenda). Dados da Ata Final, da Folha de Aprovação, da declaração e
    da agenda; situação da E2; código de validação; corpos reais de `ao_liberar_resultado` e
    `declaracao_disponivel`; aviso da E2 na liberação;
  - ouvintes: `services_ouvintes.py`, `forms_ouvintes.py` e `views_ouvintes.py` (novos): ouvintes da
    sessão, ocorrências e a lista "Ouvintes das defesas" (revisão M-13).
  Permissões acrescentadas a `permissoes_defesa.py`; textos em `mensagens.py`.
- **Motivo**: o pedido da feature ("services de geração de PDF e de ouvintes"); a geração já tem
  `pdf.py` (spec 008); ouvintes e ocorrências são escrita com trava e validação. Mesma divisão
  das specs 007/008 (`services_x`/`forms_x`/`views_x`).
- **Alternativas rejeitadas**: tudo em `services_defesa.py` (arquivo da 007 já grande); ocorrências
  em `services_avaliacoes.py` (são da US-30, não da avaliação).

## B2. Permissões de cada documento e ação

- **Decisão**: funções novas em `permissoes_defesa.py`, usadas pela view e pelo contexto da janela
  (botão aparece ⇔ endereço aceita). "Orientador do trabalho" é o **Presidente da banca**
  (Clarifications, B-03), por uma função pública `e_presidente(usuario, sessao)` que passa a ser a
  única regra (a privada `_e_presidente` da spec 008 delega para ela; revisão M-02).

  | Função | Regra |
  |---|---|
  | `e_presidente(usuario, sessao)` | papel Orientador (Presidente) na banca da sessão (já usada por `pode_registrar_parecer` e `pode_liberar`) |
  | `pode_baixar_documentos(usuario, sessao)` | resultado liberado **e** (membro efetivo, isto é, em `membros_efetivos(sessao)`; Professor da Disciplina da turma; Secretaria do curso da turma; Aluno do TCC). Suplente não acionado: não (P5) |
  | `pode_baixar_declaracao(usuario, sessao)` | resultado liberado e usuário em `membros_efetivos(sessao)` |
  | `pode_editar_ouvintes(usuario, sessao)` | sessão Em Andamento ou Realizada; turma não arquivada; Presidente ou Professor da Disciplina da turma |
  | `pode_ver_ouvintes(usuario, sessao)` | **sem depender de `pode_editar_ouvintes`** (revisão B-02): Presidente ou Professor da Disciplina da turma, em qualquer status, quando há presenças gravadas ou ele pode editar; Secretaria do curso só com a sessão Em Andamento ou Realizada (FR-009, P6) |
  | `pode_editar_ocorrencias(usuario, sessao)` | sessão Em Andamento, sem liberação, turma não arquivada, Presidente (P9; revisão I-01) |
  | `pode_ver_ocorrencias(usuario, sessao)` | Presidente, Professor da Disciplina da turma e Secretaria do curso, com texto gravado (P10) |
  | `pode_gerar_agenda(usuario)` | perfil `docente`, `coordenador` ou `secretaria`. Qualquer Docente, mesmo sem orientando ou turma: a agenda é pública (P2, RBN-DEF-08.1 "para divulgação"); o Aluno e o Membro Externo, não |
  | `pode_ver_ouvintes_das_defesas(usuario)` | perfil `secretaria` (P8) |

- **Motivo**: uma função por regra, sem condicional de permissão em template. O Presidente
  continua na banca depois da matrícula no TCC 2 e sempre abre a janela da sessão
  (`pode_ver_sessao`), o que não vale para o orientador atual (B-03).
- **Alternativas rejeitadas**: `e_orientador_atual` (perde o direito ao encerrar a orientação do
  TCC 1 e dá botão a quem não abre a sessão); reaproveitar `pode_ver_sessao` (inclui o Suplente
  não acionado e libera antes da liberação).

## B3. Recusas e mensagens das views

- **Decisão**:
  - sem login: `perfil_requerido()` leva ao login com `next`, e a ação segue depois (US-28
    cenário 9; US-30 cenário 11);
  - documentos sem permissão e antes da liberação: `PermissionDenied(SEM_PERMISSAO_DOCUMENTOS)`,
    texto acrescentado a `MENSAGENS_403` (`cadastro/views.py`, IC-11) (P13). As rotas da Ata, da
    Folha e da Declaração usam `perfil_requerido()` (qualquer logado), para que o Aluno e a
    Secretaria recebam esse texto, e não a M-02 do decorador (revisão I-04);
  - Folha de TCC 1 ou Reprovado, E2 e falha na geração (E3): redireciona para a origem (janela da
    sessão ou aba Meu TCC, pelo parâmetro `origem` com valores fixos `sessao`/`meu_tcc`, nunca uma
    URL livre) com `messages.error` e o texto exato;
  - ouvintes e ocorrências sem permissão (inclusive turma arquivada): `PermissionDenied` sem
    texto, e o handler403 mostra a M-02 "Você não tem permissão para esta ação" (US-30 E9). A
    `TurmaArquivada` levantada por `travar_tcc` numa corrida (turma arquivada entre o GET e o
    POST) é convertida em `PermissionDenied` pela view, nunca erro 500 (revisão I-01).
- **Motivo**: as recusas de permissão já usam o handler403 nas specs 007 e 008; as demais são
  condições do documento, que a US manda exibir sem sair do fluxo.

## B4. Ata Final e Folha de Aprovação

- **Decisão**: `dados_da_ata(sessao)` e `dados_da_folha(sessao)` montam um dicionário de valores
  simples (strings, `Decimal`, datas) a partir de:
  - `services_avaliacoes.resultado_da_sessao(sessao)`: nota final, parecer, notas individuais dos
    3 membros efetivos e `elevada_pelo_qualis` (observação da Ata);
  - `membros_efetivos(sessao)` na ordem Orientador, 1º Avaliador, 2º Avaliador, com o papel da
    linha da banca (o suplente acionado ocupa o papel do substituído) e a titulação lida no
    momento (`doc_titulacao` ou `mem_titulacao`);
  - assinaturas: uma função única `_imagem_existente(caminho)` confere `default_storage.exists`;
    existe → `media/<caminho>` ao template; ausente → `None`, o template não emite `<img>` e o
    serviço registra no log (decisão de 2026-11-03 e Q-140). Assim o `xhtml2pdf` nunca recebe
    recurso inexistente e não há risco de a ausência virar E3 (revisão M-08). Membros:
    `BancaDefesa.ban_assinatura_path` (cópia da avaliação, spec 008); Coordenador:
    `services.caminho_da_assinatura(docente do Coordenador)` (a mesma função da spec 003, também
    usada pela E2);
  - o Coordenador do curso da turma (`Coordenadores.cor_cur = tur_cur`): nome e assinatura;
  - `def_data` como data da defesa (P12); na Folha, "Manaus, DD de mês de AAAA" com o mês por
    extenso em português (tabela fixa no serviço, sem depender do locale).
  Títulos: "Ata Final de Avaliação de Trabalho de Conclusão de Curso I" ou "II"
  (`services_avaliacoes.e_tcc_2`). Folha: papéis Presidente, Avaliador e Avaliador; nenhum número
  de nota no template (SC-001).
- **Templates**: `defesa/pdf/ata_final.html` e `defesa/pdf/folha_aprovacao.html`, estendendo
  `defesa/pdf/base_pdf.html` (fontes Roboto locais, sem `base.html`); cabeçalho textual
  "Universidade do Estado do Amazonas – Escola Superior de Tecnologia" e o nome do curso (não há
  logotipo oficial em `static/img/`).
- **Nome do arquivo**: `ata_final_<def_id>.pdf`, `folha_aprovacao_<def_id>.pdf` (sem nome de
  pessoa, LGPD).
- **Alternativas rejeitadas**: ler as notas direto de `Avaliacoes` (duplicaria o cálculo da 008);
  usar a assinatura do perfil do membro (a da avaliação é a assinada no envio).

## B5. E2 da US-28 (Coordenador sem assinatura)

- **Decisão**: `situacao_da_ata(sessao)` devolve `None` (Ata pode ser gerada) ou um motivo:
  `SEM_COORDENADOR` (o curso da turma não tem linha em `Coordenadores`) ou `SEM_ASSINATURA`
  (`caminho_da_assinatura` do Coordenador vazio). Caminho gravado com arquivo ausente: `None`;
  a Ata sai sem a imagem (B4; Q-140).

  **Na liberação** (emenda à spec 008, P1): `views_avaliacoes.liberar_resultado`, no ramo
  `resultado.liberado`, chama `services_documentos.avisar_pendencia_da_ata(sessao)`. Esse ramo
  roda **depois do commit** e depois dos callbacks `on_commit` da liberação: `ATOMIC_REQUESTS` não
  está ligado, `perfil_requerido` não abre transação e `services_avaliacoes.liberar_resultado`
  fecha o próprio `atomic()` antes de devolver (conferido na revisão). A função:
  - relê a sessão pelo `pk` (não usa a instância lida antes da liberação; revisão M-09);
  - com motivo, numa `transaction.atomic()` própria (as notificações entram todas ou nenhuma;
    M-09), notifica (`services.notificar`) o Coordenador com a MX-03 e **link para
    `cadastro:perfil`**, onde ele cadastra a assinatura (a janela da sessão é recusada ao
    Coordenador fora da banca; revisão I-05), ou, sem Coordenador, cada conta Secretaria ativa do
    curso com a MX-09 e link para a sessão; devolve o texto da E2;
  - sem motivo, devolve `None`;
  - qualquer exceção vai ao log e devolve `None` (a liberação nunca falha por causa dela).
  A view mostra o texto com `messages.warning` depois da MA-11.

  **No download da Ata**: com motivo, a view não gera o PDF e redireciona com a mensagem da E2
  (Presidente) ou a MX-08 (demais); não notifica de novo (P1).
- **Motivo**: a E2 depende de dado que muda; como o PDF é sob demanda, basta verificar a cada
  download. Uma notificação por liberação (que acontece uma vez por sessão) evita repetir avisos.
- **Alternativas rejeitadas**: verificar o arquivo no disco para a E2 (cada deploy no Render
  bloquearia as Atas; Q-140); notificar a cada download; pôr a verificação em
  `ao_liberar_resultado` (sem acesso à resposta para o alerta).

## B6. Código de validação da declaração (RBN-DEF-08.3; dicionário, regra 4)

- **Decisão**: `codigo_de_validacao(sessao, usuario)`:
  `salted_hmac("sigtcc.declaracao", f"{def_id}:{usu_id}", algorithm="sha256").digest()`,
  codificado em Base32 (`A-Z` e `2-7`), sem o `=`, nos **16 primeiros caracteres**, impresso em
  quatro grupos separados por espaço (`ABCD EFGH IJKL MNOP`) só na apresentação. Determinístico
  (segunda via igual; SC-004), diferente por membro e por sessão, sem armazenamento. A declaração
  imprime também a referência "Defesa nº {def_id}", que, com o código e o membro, é o que a
  futura tela S-07 precisará pedir para recalcular (revisão M-12). O documento diz que o código
  não constitui assinatura digital (REQ-WNT-09).
- **Motivo**: o `Signer` do Django gera `:`, `-` e `_`; o HMAC com a `SECRET_KEY` impede que
  alguém fabrique um código válido. 16 caracteres Base32 = 80 bits.
- **Risco aceito**: trocar a `SECRET_KEY` muda os códigos das segundas vias seguintes (e também
  derruba todas as sessões de login, por isso só acontece em incidente). Sem tela de verificação
  (S-07), o impacto é a segunda via sair com código diferente do e-mail original. Registrado no PR.
- **Alternativas rejeitadas**: UUID gravado (exige coluna, fora do dicionário); hash sem chave.

## B7. Declaração por e-mail na liberação (US-30 D; RBN-DEF-08.3)

- **Decisão**: `ao_liberar_resultado(sessao)` (registrado pela spec 008 com
  `transaction.on_commit(..., robust=True)`) passa a:
  1. no próprio callback, **reler a sessão pelo `pk`** (M-09) e montar, para cada membro efetivo
     com e-mail, um item só com valores simples: o contexto da declaração (`dados_da_declaracao`),
     assunto e corpo do e-mail (MX-04), o endereço e o `pk` da conta (nunca a instância; I-08);
  2. entregar a lista a `_enviar_declaracoes(itens)`, função de trabalho sem acesso ao banco:
     com `SIGTCC_EMAIL_SINCRONO`, chamada ali mesmo; sem ele, numa
     `threading.Thread(daemon=True)`. Para cada item, gera o PDF (`pdf.gerar_pdf`, em memória) e
     envia com `services.enviar_email(..., anexos=[...])`; cada falha de um membro não interrompe
     os demais. A thread termina com `connection.close()` num `finally`, por defesa (I-08);
  3. falha de geração: só o log do `gerar_pdf` (já faz `logger.exception`), sem registro de
     evento (o rótulo `FALHA_ENVIO_EMAIL` é só para envio; M-03); falha de envio: o registro que
     `enviar_email` já faz (`FALHA_ENVIO_EMAIL` pelo `pk` da conta).
- **Segurança da geração em paralelo (I-07)**: o `xhtml2pdf`/`reportlab` têm estado global
  (registro de fontes, `rl_config`) e não garantem execução segura em várias threads. `pdf.gerar_pdf`
  passa a serializar a renderização com um `threading.Lock` de módulo (IC-14, spec 008). O custo é
  um download esperar a geração em curso (segundos), aceitável para o volume do sistema.
- **Helper de e-mail com anexo (IC-12)**: `enviar_email` (spec 003) ganha `anexos=None` (lista de
  `(nome, bytes, tipo)`). Sem anexos, a chamada literal `send_mail` continua igual, porque cinco
  testes da spec 003 fazem `mock.patch("sigtcc.apps.cadastro.services.send_mail")`
  (`test_log_acesso`, `test_us10`, `test_us12`, `test_us37`, `test_us38`); com anexos, usa
  `EmailMessage`. O docstring passa a dizer "template de e-mail" (a declaração usa
  `defesa/emails/`; M-04).
- **Risco aceito**: no Render, uma thread daemon morre num restart ou deploy; a segunda via em
  Minhas bancas cobre a declaração não enviada (FR-021).
- **Alternativas rejeitadas**: fila de tarefas (infraestrutura nova, fora do PGCS); enviar só o
  link (a US-30 D manda o PDF).

## B8. Segunda via e `declaracao_disponivel`

- **Decisão**: `declaracao_disponivel(sessao, usuario)` decide sem consulta nova quando possível:
  `services_avaliacoes.minhas_bancas` já tem a linha da banca do usuário (papel e sessão); a
  declaração existe se a sessão está liberada e o papel é titular (o suplente acionado já ocupa o
  papel titular). A função recebe a sessão e o usuário (assinatura do contrato da 008 inalterada)
  e faz uma consulta por linha Realizada; o docstring de `minhas_bancas` ("sem consulta por linha")
  é corrigido para dizer que as sessões Realizadas fazem uma consulta a mais (M-11; IC-15). Rota
  `defesa:declaracao` gera o PDF com o mesmo `dados_da_declaracao` do e-mail (mesmo código). O
  link "Declaração" de Minhas bancas passa a apontar para essa rota (IC-04); o bloco `documentos`
  da janela mostra também o botão ao membro efetivo.
- **Motivo**: FR-021; mesmo conteúdo nas duas vias; Minhas bancas tem poucas sessões Realizadas
  por membro.

## B9. Ouvintes (US-30 A; RBN-DEF-08.2)

- **Decisão**:
  - Formulário: formset Django (`OuvinteForm`: `nome`, `matricula`; `can_delete=True` para
    Remover; `extra=1`, porque a linha extra vazia é ignorada; `max_num=200`, `absolute_max=200`
    e `validate_max=True` contra adulteração do `TOTAL_FORMS`; M-05) na janela
    `defesa/form_ouvintes.html` (M-13); "Adicionar" clona o `empty_form` por
    `static/js/ouvintes.js`. Cancelar volta à sessão sem gravar.
  - Validação no formulário e no serviço (o serviço é a fonte): matrícula `^[0-9]{10}$`; nome
    aparado, não vazio, até 150 caracteres, cada caractere letra (`str.isalpha()`, que aceita
    acentos e recusa "×" e "÷"; M-06) ou espaço. Duplicata conferida **só dentro da lista
    enviada**, que é o estado final da sessão (I-03): a mesma matrícula em duas linhas → "Este
    aluno já foi registrado como ouvinte nesta defesa" na linha repetida (US-30 cenário 13).
    Qualquer erro: nada é gravado e o campo é destacado (classe `erro`).
  - `salvar_ouvintes(usuario, def_id, linhas)` numa transação: trava turma → aluno → TCC → sessão
    (`travar_tcc(tcc_da_sessao(def_id))` e depois `travar_sessao`, mesma ordem das specs 007/008);
    confere `pode_editar_ouvintes` com a sessão travada; matrículas novas processadas **em ordem
    crescente** (I-02): o lock da sessão não serializa sessões diferentes, e duas sessões
    inserindo as mesmas matrículas novas em ordem inversa poderiam travar uma à outra no índice
    único (deadlock, `OperationalError`); com a ordem fixa, uma espera a outra. Para cada uma,
    `Ouvintes.objects.get_or_create(ouv_matricula=..., defaults={"ouv_nome": ...})` simples (o
    Django já trata o `IntegrityError` da AK); o existente é reaproveitado sem mudar o nome (P4).
    Apaga as presenças que saíram da lista e cria as novas (`bulk_create`). O registro em
    `Ouvintes` nunca é apagado.
  - **Risco aceito (I-03)**: se o Presidente e o Professor da Disciplina editarem a mesma lista
    ao mesmo tempo, o último a salvar vence (a trava só serializa os salvamentos). O volume (uma
    sessão, dois editores possíveis) não justifica controle de versão.
  - Mensagem "Ouvintes salvos com sucesso"; redireciona para a janela da sessão.
- **Alternativas rejeitadas**: gravar linha a linha por AJAX (contraria "lista inteira").

## B10. Ocorrências (US-30 B; RBN-DEF-08.5)

- **Decisão**: `OcorrenciasForm` (`Textarea`, opcional, contador com o `static/js/contador.js`
  existente). O `clean` normaliza `\r\n` → `\n` **antes** de conferir os 2.000 caracteres, para o
  limite bater com o contador (M-07). `registrar_ocorrencias(usuario, def_id, texto)` trava turma
  → aluno → TCC → sessão (`travar_tcc` + `travar_sessao`; M-14), confere `pode_editar_ocorrencias`
  e grava `def_ocorrencias` (`None` quando vazio) com `save(update_fields=["def_ocorrencias"])`.
  Acima de 2.000: MX-01 com a caixa destacada (E5). Sucesso: MX-06. Janela
  `defesa/form_ocorrencias.html`. Não grava `Historico_Defesas`.
- **Motivo**: campo opcional de `Defesas`; a trava evita gravar depois de uma liberação
  concorrente.

## B11. Ouvintes das defesas (US-30 C; RBN-DEF-08.4)

- **Decisão**: `ouvintes_das_defesas(periodo, cur_id)`, em que **`periodo` é o Q sobre `Defesas`
  devolvido por `FiltroPeriodoForm.filtro()`**, sem prefixo (B-01): a consulta é
  `PresencaOuvintes.objects.filter(pre_def__in=Defesas.objects.filter(periodo,
  def_status=Realizada, [def_tcc__tcc_tur__tur_cur_id=cur_id]))`, com `select_related` do ouvinte,
  do TCC e do aluno e o nome do Orientador (Presidente) por `Subquery`. Nenhuma mudança no form da
  spec 007. Ordem: data da defesa, título, nome do ouvinte. Colunas: Nome Completo, Matrícula,
  Título, Aluno, Orientador, Data da defesa, "2 horas". Sem linhas: MX-07. Filtros:
  `FiltroPeriodoForm` (spec 007) e `services_contas.filtro_de_curso` (spec 002). A view chama
  `services_defesa.iniciar_sessoes_vencidas()` antes, como todas as telas da Defesa (M-10). Sem
  paginação (dezenas de linhas por período).
- **Motivo**: reaproveita o Q do form sem duplicar a regra do atalho (inclusive o Período Letivo
  como padrão); o Épico 3 chama a mesma função com o mesmo tipo de `periodo`.
- **Alternativas rejeitadas**: `filtro(prefixo=...)` no form da 007 (mudança em código mesclado
  sem necessidade); exportação CSV agora (é o RBN-REL-03.4, Épico 3; P8).

## B12. Agenda de defesas em PDF (US-30 F; RBN-DEF-08.1)

- **Decisão**: rota `defesa:agenda` (GET) recebe os mesmos parâmetros da tela Defesas. A view
  chama `iniciar_sessoes_vencidas()` antes (M-10). `agenda_de_defesas(usuario, periodo, cur_id)`:
  `Defesas` com `def_status ∈ {Agendada, Reagendada}`, período aplicado (o Q do form); **sem** a
  visibilidade do perfil (P2); `cur_id` só para Coordenador e Secretaria; ordem `def_data`,
  `def_h_inicio`; agrupadas por dia, cada linha com horário HH:MM, título, aluno, Orientador
  (Presidente) e local (`dep_local`) ou link. Filtro inválido: redireciona para a tela Defesas
  com a query string original, que já mostra os erros do form (sem `messages.error` a mais; M-10).
  Sem sessões: redireciona para a tela Defesas com "Não existem defesas agendadas para o período
  selecionado". Template `defesa/pdf/agenda.html`; arquivo `agenda_defesas.pdf`.
- **Botão**: na tela Defesas, para `pode_gerar_agenda`, com a query string atual.

## B13. Janela da sessão e Meu TCC

- **Decisão**:
  - `contexto_da_sessao` (spec 007/008) ganha `documentos`
    (`services_documentos.visao_dos_documentos`) e `ouvintes`
    (`services_ouvintes.visao_da_sessao`: lista, se pode editar, mensagem da E7, ocorrências e se
    pode editar). Os blocos `documentos`, `ouvintes` e `ocorrencias` de `sessao.html` incluem
    `_bloco_documentos.html`, `_bloco_ouvintes.html` e `_bloco_ocorrencias.html`.
  - Aba Meu TCC (P14): `services_documentos.documentos_do_aluno(tcc)` lista as sessões Realizadas
    e liberadas do TCC, da mais recente para a mais antiga, com data e botões; parcial
    `defesa/_documentos_aluno.html` em `meu_tcc.html`; saem os dois botões desabilitados do cartão
    "Defesa" da Versão Final (IC-05).

## B14. Cenário de demonstração (`popular_demo`)

- **Decisão**: acrescentar, só por serviços: ouvintes e ocorrências na sessão Realizada de
  demonstração; a assinatura estática `static/img/assinatura_demo.png` copiada para o perfil do
  Coordenador de um curso (Ata gerável) e outro curso sem assinatura do Coordenador (E2). Em
  produção, a cópia some no deploy seguinte e a Ata sai sem a imagem (Q-140).

## B15. Testes

- **Decisão**: arquivos novos em `sigtcc/apps/defesa/tests/`: `test_us28_documentos.py`,
  `test_us30_ouvintes.py`, `test_us30_ocorrencias.py`, `test_us30_ouvintes_das_defesas.py`,
  `test_us30_declaracao.py`, `test_us30_agenda.py`, `test_codigo_validacao.py`,
  `test_mensagens_documentos.py`; apoio `apoio_documentos.py`. PDFs conferidos pelo texto
  extraído com `pypdf` (já fixado no `requirements.txt`, `pypdf==6.21.4`; M-01) e pelo cabeçalho
  `%PDF`. E-mails com `mail.outbox`, `captureOnCommitCallbacks(execute=True)` e
  `SIGTCC_EMAIL_SINCRONO=True`; a função de trabalho `_enviar_declaracoes` testada à parte com
  `assertNumQueries(0)` (I-08). Falha de geração: `mock.patch` de `pdf.gerar_pdf` levantando
  `ErroAoGerarPdf`, conferindo que nada foi gravado em `MEDIA_ROOT` temporário (SC-003). Falha de
  envio: backend de e-mail que levanta, ou `mock.patch` de `EmailMessage.send` (nunca de
  `send_mail`, que a declaração não usa; M-04). Corrida da turma arquivada: `mock` da trava
  levantando `TurmaArquivada` (I-01). Cenário 3.8: aluno aprovado no TCC 1 e matriculado no
  TCC 2 (B-03).
- **Testes de outras specs (I-06)**: `apoio_avaliacao.sessao_com_banca` passa a criar por padrão
  um Coordenador com assinatura no curso da turma (IC-16), para a liberação dos testes da 008 não
  cair na E2. Ajustes nominais:
  - `test_us27_liberacao.test_avisos_ao_aluno_banca_e_secretaria_sem_a_nota`: com o Coordenador do
    apoio, não há MX-09; o conjunto de assuntos passa a incluir o da MX-04 (declarações);
  - `test_us27_liberacao`: novo teste do alerta da E2 depois da MA-11 (cenário sem Coordenador);
  - `test_minhas_bancas`: destino do link Declaração e `declaracao_disponivel` real;
  - aba Meu TCC: nenhum teste atual confere os botões desabilitados; novo teste confere que
    saíram e que a parcial `_documentos_aluno.html` aparece.
  As liberações pela view nos testes da 008 passam a gerar 3 PDFs (mais lentas); aceitável.
