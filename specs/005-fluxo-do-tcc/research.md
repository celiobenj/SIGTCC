# Research: Fluxo do TCC e Entregas do SIGTCC

**Feature**: [spec.md](spec.md) (aprovada em 2026-10-22) | **Plano**: [plan.md](plan.md) | **Data**: 2026-10-22

Formato: Decisão / Justificativa / Alternativas. As decisões partem do modelo já existente da spec
001 (`models.py`, `choices.py` — nenhuma tabela ou coluna nova), dos serviços compartilhados das
specs 003 e 004 (`contracts/servicos-compartilhados.md`), das Clarifications da spec 005 e do
código já mesclado de `services_turmas.py`. Os IDs C1, C2… são desta feature.

---

## C1. Organização do código no app `cadastro`

**Decisão**: dois módulos novos, por domínio de dados:

| Arquivo | Conteúdo |
|---|---|
| `services_tcc.py` | Proposta e dados do TCC (US-13), Status/histórico/trilha (US-14) |
| `services_entregas.py` | cadastro de entregas (US-43), envio e substituição de link (US-15, US-29), acompanhamento (US-16), homologação e devolução (US-44) |
| `services_turmas.py` (spec 004, já mesclada) | `atualizar_status_tcc` pública (C2); `criar_entregas_do_aluno`, `participacao_encerrada`, `travar_turma_ativa`, `turma_tem_orientador_automatico` continuam lá, só importados pelos dois módulos novos |
| `forms_tcc.py`, `forms_entregas.py` | formulários de cada domínio |
| `views_tcc.py`, `views_entregas.py` | views finas |

Templates em `sigtcc/templates/cadastro/tcc/`. Os módulos com sufixo `_tcc` e `_entregas` são
acréscimos à árvore do PGCS 2.3, no mesmo padrão já aceito para `services_turmas.py` e
`importacao.py` (spec 004) — exceção justificada ao princípio IV (Complexity Tracking do plano).

**Alternativas**: um único `services_fluxo_tcc.py`: misturaria dois domínios (`TCCs` vs.
`Turmas_Marcos`/`Entregas_Marcos`) com gatilhos e responsáveis diferentes, dificultando a revisão;
estender `services_turmas.py` com tudo: o arquivo já tem ~1050 linhas (spec 004) e cresceria além do
razoável para uma única revisão de PR.

## C2. Serviço único de gravação do Status do TCC (FR-008, FR-012)

**Situação encontrada**: `services_turmas.py` já tem `_registrar_historico(tcc, turma, autor,
anterior, novo, gatilho)` (privada), chamada em 3 pontos: `matricular` (gatilho "Vínculo à
turma"), `_copiar_tcc_aprovado`/`transferir` (gatilho "Transferência para TCC 2") e
`encerrar_participacao` (gatilho "Encerramento da participação"). Em cada ponto, quem chama já fez
`tcc.tcc_status = novo` e `tcc.save(...)` **antes** de chamar a função — ou seja, a gravação do
Status e a gravação do histórico hoje são dois passos manuais repetidos, não um serviço único.

**Revisão do `arquiteto-django` (2026-10-22)**: a primeira versão desta decisão tinha 3 problemas
bloqueantes — (1) `_copiar_tcc_aprovado` não podia chamar a função genérica do mesmo jeito que os
outros pontos, porque o "anterior" correto pertence a uma **linha diferente** (`tcc1`, o TCC de
TCC 1), não ao TCC novo sendo criado; (2) faltava validar a **transição**
`(status_atual, gatilho) → novo_status`, só validava que o gatilho existia; (3) a função não
declarava que depende de o chamador já ter travado o TCC (`select_for_update`) antes. Ao corrigir
o achado (1), a revisão deste research identificou que **o mesmo problema vale para `matricular`**
(gatilho "Vínculo à turma"): ali também o TCC é criado já com `tcc_status=StatusTCC.SEM_PROPOSTA`
em `TCCs.objects.create(...)` — não é um `UPDATE` sobre um TCC existente, é uma criação, igual a
`_copiar_tcc_aprovado`. Uma função que faz `anterior = tcc.tcc_status` (lendo do objeto já criado
com o status final) nunca serve para os gatilhos de criação: o "anterior" desses dois gatilhos não
está no objeto, está em `None` (TCC novo, sem linha de origem) ou noutra linha (`tcc1`).

**Decisão (corrigida)**: dois gatilhos criam o TCC (status definido na criação, "anterior" vem de
fora do objeto) e cinco atualizam um TCC existente (status lido do próprio objeto antes de mudar).
`_registrar_historico` **permanece privada**, chamada só pelas duas funções públicas abaixo — nunca
diretamente por quem grava o Status:

```python
# Gatilho → conjunto de transições (status_atual, novo_status) permitidas (FR-008; data-model.md).
# status_atual=None só nos gatilhos de criação, quando não há TCC (nem linha de origem) anterior.
TRANSICOES_VALIDAS = {
    GatilhoStatusTCC.VINCULO_A_TURMA: {(None, StatusTCC.SEM_PROPOSTA)},
    GatilhoStatusTCC.PROPOSTA_SALVA: {(StatusTCC.SEM_PROPOSTA, StatusTCC.EM_ANDAMENTO)},
    GatilhoStatusTCC.TRANSFERENCIA_PARA_TCC_2: {
        (StatusTCC.APROVADO_PARA_TCC_2, StatusTCC.EM_ANDAMENTO)
    },
    GatilhoStatusTCC.INDICACAO_DE_APTO: {(StatusTCC.EM_ANDAMENTO, StatusTCC.APTO_PARA_DEFESA)},
    GatilhoStatusTCC.LIBERACAO_DO_RESULTADO: {
        (StatusTCC.APTO_PARA_DEFESA, StatusTCC.APROVADO_PARA_TCC_2),
        (StatusTCC.APTO_PARA_DEFESA, StatusTCC.APROVADO),
        (StatusTCC.APTO_PARA_DEFESA, StatusTCC.APROVADO_COM_CORRECOES),
        (StatusTCC.APTO_PARA_DEFESA, StatusTCC.REPROVADO),
    },
    GatilhoStatusTCC.HOMOLOGACAO_DA_VERSAO_FINAL: {
        (StatusTCC.APROVADO, StatusTCC.CONCLUIDO),
        (StatusTCC.APROVADO_COM_CORRECOES, StatusTCC.CONCLUIDO),
    },
    GatilhoStatusTCC.ENCERRAMENTO_DA_PARTICIPACAO: {
        (de, para)
        # Só EM_ANDAMENTO e APTO_PARA_DEFESA (STATUS_TCC_ENCERRAVEL, services_turmas.py linha 896);
        # aluno "Sem Proposta" é excluído da turma (US-09), não encerrado — RBN-CAD-05.4 recusa
        # "Encerrar participação" para quem já tem Proposta ao contrário (ALUNO_TEM_PROPOSTA na
        # exclusão prova que a regra é a inversa: sem Proposta → exclusão, não encerramento).
        for de in (StatusTCC.EM_ANDAMENTO, StatusTCC.APTO_PARA_DEFESA)
        for para in (StatusTCC.DESISTENTE, StatusTCC.REPROVADO, StatusTCC.JUBILADO)
    },
}


def _validar_transicao(anterior, novo_status, gatilho):
    """Levanta ValueError se (anterior → novo_status) não estiver prevista para o gatilho
    (FR-008) — chamada pelas duas funções públicas abaixo, nunca pulada."""
    if gatilho not in TRANSICOES_VALIDAS or (anterior, novo_status) not in TRANSICOES_VALIDAS[gatilho]:
        raise ValueError(f"Transição inválida: {anterior!r} → {novo_status!r} pelo gatilho {gatilho!r}")


def criar_tcc_com_historico(aluno, turma, autor, status_inicial, gatilho, anterior=None, **campos_tcc):
    """Único ponto que cria um TCC e grava o primeiro registro do histórico (FR-008, FR-012).

    Usada pelos 2 gatilhos de criação: "Vínculo à turma" (`anterior=None`, matrícula nova, sem
    `campos_tcc` — o TCC nasce "Sem Proposta", sem título/resumo/modalidade) e "Transferência para
    TCC 2" (`anterior` = status do TCC de origem, ex. `tcc1.tcc_status`, lido por quem chama
    **antes** de passar para esta função; `campos_tcc` = `tcc_titulo`, `tcc_subtitulo`,
    `tcc_resumo`, `tcc_modalidade`, `tcc_link_proposta`, `tcc_ari`, copiados do TCC de origem —
    **obrigatórios** nesse gatilho porque `status_inicial="Em Andamento"` cai na `CHECK
    ck_tccs_campos_obrigatorios_com_proposta` do dicionário, que exige esses campos fora de "Sem
    Proposta"; sem eles, o `INSERT` falha com `IntegrityError` antes mesmo de chegar ao
    `_registrar_historico`, como a implementação confirmou ao tentar aplicar a primeira versão
    desta função). Pressupõe turma, aluno e — na transferência — o TCC de origem já travados pelo
    chamador (`select_for_update`, research C4).
    """
    _validar_transicao(anterior, status_inicial, gatilho)
    tcc = TCCs.objects.create(
        tcc_alu=aluno, tcc_tur=turma, tcc_status=status_inicial, **campos_tcc
    )
    _registrar_historico(tcc, turma, autor, anterior, status_inicial, gatilho)
    return tcc


def atualizar_status_tcc(tcc, turma, autor, novo_status, gatilho):
    """Único ponto que muda tcc_status de um TCC **já existente** e grava o histórico (FR-008,
    FR-012). Usada pelos 5 gatilhos de transição: "Proposta salva", "Indicação de Apto para
    Defesa", "Liberação do resultado", "Homologação da Versão Final" e "Encerramento da
    participação". Pressupõe que o chamador já travou turma → aluno → TCC (`select_for_update`,
    dentro do mesmo `transaction.atomic()`, research C4) **antes** de chamar esta função — ela não
    trava nada por si. Levanta ValueError se a transição não for válida; nesse caso, nenhuma linha
    é gravada.
    """
    anterior = tcc.tcc_status
    _validar_transicao(anterior, novo_status, gatilho)
    tcc.tcc_status = novo_status
    tcc.save(update_fields=["tcc_status"])
    _registrar_historico(tcc, turma, autor, anterior, novo_status, gatilho)
```

Os 3 pontos já existentes passam a usar as funções públicas em vez do padrão manual atual:
`matricular` chama `criar_tcc_com_historico(aluno, turma, professor, StatusTCC.SEM_PROPOSTA,
GatilhoStatusTCC.VINCULO_A_TURMA)` (sem passar `anterior`, usa o `None` padrão);
`_copiar_tcc_aprovado` chama `criar_tcc_com_historico(aluno, turma, autor,
StatusTCC.EM_ANDAMENTO, GatilhoStatusTCC.TRANSFERENCIA_PARA_TCC_2, anterior=tcc1.tcc_status,
tcc_titulo=tcc1.tcc_titulo, tcc_subtitulo=tcc1.tcc_subtitulo, tcc_resumo=tcc1.tcc_resumo,
tcc_modalidade=tcc1.tcc_modalidade, tcc_link_proposta=tcc1.tcc_link_proposta,
tcc_ari=tcc1.tcc_ari)` — assinatura corrigida durante a implementação (T006), decisão de Julia
Cohen (2026-10-22): estender a função com `**campos_tcc` em vez de manter `_copiar_tcc_aprovado`
como exceção fora do FR-012;
`encerrar_participacao` chama `atualizar_status_tcc(tcc, turma, professor, status,
GatilhoStatusTCC.ENCERRAMENTO_DA_PARTICIPACAO)`. `services_tcc.py` (gatilho "Proposta salva") e
`services_entregas.py` (gatilho "Homologação da Versão Final") chamam `atualizar_status_tcc`; a
futura spec 006 (gatilhos "Indicação de Apto para Defesa" e "Liberação do resultado") também —
**sempre** dentro de uma transação que já travou o TCC antes. Nenhum outro lugar cria `TCCs` com
status definido nem grava em `tcc_status` fora dessas duas funções, e nenhum outro lugar cria
`HistoricoStatusTCC` diretamente (FR-012, SC-002).

Por tocar um arquivo já mesclado de outra feature, esta refatoração está registrada como pendência
de aprovação (Q-46) para Leandra Matos e Célio Benjamim; os testes da spec 004 (US-08 e US-09)
precisam continuar passando sem alteração.

**Alternativas**: duplicar a lógica em `services_tcc.py` — violaria o próprio FR-012 ("Status
nunca alterado fora do serviço") ao criar dois caminhos de gravação; validar só a existência do
gatilho, sem a tabela de transições — rejeitado pela revisão do `arquiteto-django`: um erro de
cálculo em quem chama (ex.: a spec 006 passando a constante errada de `novo_status`) passaria sem
erro e corromperia o histórico, justamente o que o "serviço único" deveria impedir; uma função só
(em vez de duas) tentando servir criação e atualização — rejeitado porque o "anterior" de um
`UPDATE` vem do próprio objeto e o de um `INSERT` vem de fora (ou é `None`); forçar os dois casos
na mesma assinatura exigiria o chamador simular um objeto com `tcc_status` já setado antes de
existir no banco, mais confuso do que duas funções pequenas e nomeadas pelo que fazem.

## C3. Validação de campos da Proposta e do TCC (US-13, FR-001 a FR-007a)

**Decisão**: um `ModelForm` sobre `TCCs` para os campos da Proposta (Título, Subtítulo, Resumo,
Modalidade, Link) e outro para Área de Interesse e Palavras-Chave (campo de texto livre dividido em
até 5 subcampos no template, sem JavaScript, como a spec 003/004 já fazem para listas pequenas).
Validação de Palavra-Chave repetida (Clarifications, sessão 2026-10-22) no `clean()` do formulário,
comparando os valores não vazios entre si antes de tentar salvar em `PalavrasChave_TCC`.

**Revisão do `arquiteto-django` (2026-10-22, importante #7)**: a validação do formulário não cobre
duas submissões quase simultâneas do mesmo aluno (duplo clique em "Salvar alterações") tentando
gravar a mesma `pal_palavra` para o mesmo `tcc_id` — a PK composta pegaria isso como
`IntegrityError`, não tratado. **Decisão**: `salvar_alteracoes_tcc(tcc, dados)` em
`services_tcc.py` roda dentro de `transaction.atomic()` com `TCCs.objects.select_for_update()`
no TCC (mesma ordem de C4) antes de apagar e recriar as linhas de `PalavrasChave_TCC`, e captura
`IntegrityError` nessa gravação, convertendo para a mensagem MF-03 como rede de segurança (a
validação do formulário já evita o caso comum; a trava e a captura cobrem o caso raro de corrida).

**Confidencialidade do Resumo (FR-007a)** — revisão do `arquiteto-django` (importante #4): a
decisão original deixava a regra só como texto no contrato, sem função testável — risco real de a
spec 006 ou o Épico 3 implementarem a regra errada. **Decisão**: `services_tcc.pode_ver_resumo
(usuario, tcc) -> bool` centraliza a checagem (Aluno dono, Orientador atual de `Orientacoes` com
`ori_status='Ativa'`, Docente com `Solicitacoes_Orientacao` pendente para esse TCC, Coorientador do
NUCOMP com `Coorientacoes.coo_status='Ativa'`, ou Professor da Disciplina da turma do TCC); a view
de "Meu TCC" desta spec e qualquer view futura da spec 006 ou do Épico 3 que exiba `tcc_resumo`
chamam essa função antes de mostrar o campo — nunca reimplementam a regra. Documentado no contrato
(`servicos-compartilhados.md`, §1) como a função a chamar, não só como regra em texto.

## C4. Trava e ordem de concorrência (research B17 da spec 004, reaplicada)

**Decisão**: toda gravação que muda `tcc_status` ou cria `Entregas_Marcos`/`HistoricoEnviosEntregas`
usa a mesma ordem já estabelecida pela spec 004: turma → aluno → TCC, dentro de
`transaction.atomic()`, com `select_for_update()` no TCC antes de ler `tcc_status` para decidir a
transição (evita duas requisições concorrentes — ex.: Aluno salvando a Proposta e Professor
encerrando a participação ao mesmo tempo — corromperem o histórico).

**Alternativas**: nenhuma trava explícita, confiando no padrão "última escrita vence" do Django:
rejeitado porque o histórico do Status perderia uma transição real (dois `UPDATE` sem trava podem
gravar dois registros de histórico com o mesmo "anterior", mascarando qual ocorreu primeiro).

**Reforço entre specs (revisão do `arquiteto-django`, bloqueante #3)**: esta ordem e esta trava são
**pré-condição obrigatória** para chamar `atualizar_status_tcc` (C2) — a função não trava nada por
si mesma. Isso importa especialmente entre specs diferentes: por exemplo, a spec 006 liberando o
resultado da banca enquanto esta spec homologa a Versão Final do mesmo TCC. Todo chamador de
`atualizar_status_tcc`, desta spec ou de outra, MUST abrir `transaction.atomic()` e travar
`Turmas` → `Alunos`/`AlunosTurmas` → `TCCs` (`select_for_update()`) antes de chamá-la; documentado
também no contrato (`servicos-compartilhados.md`, §2) como obrigação de quem chama.

## C5. Lembretes de prazo (FR-022, Could Have na matriz)

**Decisão**: função pura `entregas_para_lembrar(agora)` em `services_entregas.py`, que devolve as
`Entregas_Marcos` com `ent_status = 'Aguardando Envio'` cuja `tma_data_limite` esteja a 7 dias, 48h
ou 24h de distância de `agora` (com margem de ±1 hora, para tolerar o intervalo entre execuções da
rotina), em turma não arquivada. A chamada da rotina (comando de gestão ou `executar_rotina_agendada`
do PGCS 3.6, se já existir) fica fora do escopo desta view síncrona — pendência para o Célio
Benjamim decidir o agendamento (cron, Vercel cron job ou comando manual).

**Alternativas**: calcular o lembrete dentro da requisição HTTP de outra ação (ex.: ao abrir a
turma): descartado porque depende de alguém abrir a tela no momento exato, não é confiável.

## C6. Cadastro de entregas e "Outra" (US-43, FR-013 a FR-017)

**Decisão**: `cadastrar_entrega(professor, tur_id, dados)` em `services_entregas.py`, com a turma
travada (`travar_turma_ativa`), tenta criar `Turmas_Marcos` dentro de `transaction.atomic()`; a
`UniqueConstraint` do model já impede duplicar Proposta/Documento para Defesa/Versão Final — o
serviço captura `django.db.IntegrityError` nessa criação e traduz para a mensagem "A turma já tem
uma entrega deste tipo" (como a turma já está travada por `travar_turma_ativa` antes da criação, o
risco de corrida é baixo; a captura de `IntegrityError` é a rede de segurança, não o mecanismo
principal de checagem). Depois de criada a entrega, para cada `AlunosTurmas` ativo da turma com
`participacao_encerrada` falso, cria `Entregas_Marcos` com `ent_status` "Aguardando Envio" ou "Não
Entregue" (conforme `tma_data_limite` já vencida) — a mesma regra de `criar_entregas_do_aluno`
(spec 004), chamada aqui para os alunos já matriculados, igual ao que a spec 004 já faz para o
aluno que entra depois (matrícula/transferência). Notificação a cada aluno via
`services.notificar()`.

## C7. Envio de link, cálculo de status e Versão Final (US-15, US-29, FR-018 a FR-025)

**Decisão**: `enviar_entrega(aluno, tma_id, link)` roda dentro de `transaction.atomic()` com
`EntregasMarcos.objects.select_for_update()` na linha da entrega **e** `TCCs.objects.
select_for_update()` no TCC do aluno **antes** de consultar o primeiro envio, checar
`tcc.tcc_status` e recalcular o status (revisão do `arquiteto-django`, importante #6, mais o
achado A1 da análise `/speckit-analyze`: sem a trava em `Entregas_Marcos`, um duplo clique ou um
retry de rede no "Enviar" poderia gerar duas transações lendo `HistoricoEnviosEntregas` vazio ao
mesmo tempo; sem a trava no TCC, uma corrida com `atualizar_status_tcc`/`encerrar_participacao` —
que travam turma→aluno→TCC — poderia deixar passar um envio com um Status já mudado no meio da
requisição). Dentro da trava, cria `HistoricoEnviosEntregas` e
recalcula `ent_status` a partir do **primeiro** envio
(`HistoricoEnviosEntregas.objects.filter(hen_ent=entrega).order_by("hen_data_envio").first()`), não
do envio mais recente — substituir o link não muda o status já calculado (FR-019). Para a Versão
Final (`tma_tipo = 'Versão Final'`), o envio só é
aceito quando o TCC 2 está com `tcc_status` em `('Aprovado', 'Aprovado com Correções')` (FR-024);
a vinculação exata entre "parecer liberado" e `tcc_status` já é suficiente, sem precisar de um
campo "parecer" novo (não existe na tabela `TCCs` e não é necessário: `tcc_status` já distingue
Aprovado/Aprovado com Correções/Reprovado).

## C8. Testes e mensagens (SC-005, SC-006)

**Decisão**: `tests/apoio_tcc.py` com fábricas que partem de `apoio_turmas.criar_turma_de` e
`matricular_aluno` (spec 004) e adicionam `salvar_proposta(tcc, ...)`, `cadastrar_entrega(turma,
...)` e `enviar_link(entrega, aluno, link, quando=None)` para controlar a data do envio nos testes
de prazo. `test_mensagens_tcc.py` segue o mesmo padrão de `test_mensagens_turmas.py` (spec 004):
confere cada constante de `mensagens.py` contra o texto entre aspas das US, e as MF-01 a MF-03
contra a tabela "Mensagens a validar com a PO" do spec.md.

## C9. Separação entre consulta do histórico e checagem de perfil (US-14, FR-009)

**Revisão do `arquiteto-django` (importante #5)**: o contrato prometia que a spec 006 poderia
"chamar a mesma view" de histórico para o Orientador, mas a view desenhada checava o perfil
Professor da Disciplina embutido — a 006 chamando essa view para o Orientador receberia 403 e
teria que reimplementar a consulta, duplicando (e arriscando divergir) a regra do FR-009 que já
exclui Secretaria e Coorientador.

**Decisão**: extrair a consulta, sem nenhuma checagem de perfil, em `services_tcc.
historico_do_status(tcc) -> queryset` (ordenado do mais antigo ao mais recente, mesmo dado da
trilha do FR-010). A view `views_tcc.historico_status` desta spec aplica a checagem de perfil
(Aluno dono, Orientador atual, Professor da Disciplina da turma — nunca Secretaria nem
Coorientador, Clarifications) e chama essa função só depois de autorizar. A spec 006 (tela de
orientandos) importa e chama `historico_do_status(tcc)` diretamente, aplicando a própria checagem
(Orientador do TCC) por fora, sem duplicar a consulta. Documentado no contrato
(`servicos-compartilhados.md`, §2) como a função a reaproveitar, não a view.
