# Research: Agendamento e Banca do SIGTCC

**Feature**: [spec.md](spec.md) (aprovada em 2026-10-30) | **Plano**: [plan.md](plan.md) | **Data**: 2026-10-30

Formato: Decisão / Justificativa / Alternativas. As decisões partem do modelo já existente da spec
001 (`sigtcc/apps/defesa/models.py` e `choices.py` — nenhuma tabela ou coluna nova), dos contratos
reais das specs 002, 004, 005 e 006, e das Clarifications da spec 007. Os IDs C1, C2… são desta
feature.

---

## C1. Organização do código no app `defesa`

**Decisão**: um único módulo de serviço, `services_defesa.py`, cobrindo as 5 User Stories, com
`permissoes_defesa.py` separado só para os predicados de permissão (mesmo padrão de
`cadastro/permissoes.py`):

| Arquivo | Conteúdo |
|---|---|
| `services_defesa.py` | agendamento (US-21), conflito de horário (US-22), banca (US-23), confirmação/notificação/reagendamento/cancelamento/transições (US-24), lista/filtros/histórico (US-40), `membros_efetivos`, `registrar_evento`, `transicionar_status` |
| `permissoes_defesa.py` | `pode_agendar(usuario, tcc)`, `pode_reagendar_ou_cancelar(usuario, sessao)`, `pode_alterar_banca(usuario, sessao)`, `pode_acionar_suplente(usuario, sessao)`, `pode_ver_sessao(usuario, sessao)` — lógica interna detalhada em C1a (achado importante I1 da revisão do `arquiteto-django`) |
| `forms_defesa.py` | formulários de cada ação |
| `views_defesa.py` | views finas |

**Alternativas**: dividir por domínio (ex.: `services_banca.py` separado de
`services_agendamento.py`), como nas specs 004/005/006 — rejeitada porque o conflito de horário
(US-22) precisa ler simultaneamente os dados do agendamento (data/horário) e os da banca (membros),
o que forçaria import circular entre os dois módulos; manter tudo em `services_defesa.py` evita
isso sem ficar maior que `services_turmas.py` (spec 004, ~1050 linhas) no fim da implementação.

### C1a. `pode_agendar(usuario, tcc)` — lógica interna (achado I1 da revisão do `arquiteto-django`)

```python
def pode_agendar(usuario, tcc):
    """FR-003: Orientador em Engenharia de Computação; Professor da Disciplina em Sistemas de
    Informação e Licenciatura em Computação."""
    curso = tcc.tcc_tur.tur_cur.cur_nome
    if curso == CURSO_ENG_COMPUTACAO:
        return services_orientacao.e_orientador_atual(usuario, tcc)
    # Sistemas de Informação e Licenciatura em Computação: Professor da Disciplina da turma
    # (mesmo predicado já usado em permissoes.py/services_turmas.py para outras ações da turma).
    return usuario.pk == tcc.tcc_tur.tur_doc_id
```

`CURSO_ENG_COMPUTACAO` reaproveita a constante já definida em `cadastro/cargas.py` (spec 001/004);
`e_orientador_atual` é o contrato da spec 006 (§1). Nenhuma lógica nova de identificação de curso
ou de papel — só a combinação dos dois predicados já existentes.

## C2. Criação da sessão e serviço único de transição de status (FR-017, FR-023)

**Revisão do `arquiteto-django` (2026-10-30, bloqueante B1)**: a primeira versão desta decisão
colapsava a criação da sessão dentro de `transicionar_status`, usando `(None, AGENDADA)` na tabela
de transições e citando "o mesmo padrão de `criar_tcc_com_historico`/`atualizar_status_tcc`" da
spec 005 — citação **incorreta**: a spec 005 manteve as duas funções **separadas** exatamente
porque `atualizar_status_tcc` lê `anterior = tcc.tcc_status` **do próprio objeto**, o que só faz
sentido para um objeto que já existe; para a criação, `anterior` vem de fora (ou é `None`), e o
objeto Python ainda nem existe no banco. Esta spec tinha o mesmo problema, sem a mesma correção.

**Decisão (corrigida)**: duas funções públicas, como na spec 005 — uma cria a sessão, a outra
transiciona uma sessão já existente. Nenhuma outra chama `Defesas.objects.create(...)` nem grava
`def_status` fora delas (FR-023).

```python
# novo_status → evento correspondente no histórico (FR-023; 1:1, sem ambiguidade — achado
# importante I4 da revisão do arquiteto-django).
EVENTO_DA_TRANSICAO = {
    StatusSessao.REAGENDADA: EventoDefesa.REAGENDAMENTO,
    StatusSessao.EM_ANDAMENTO: EventoDefesa.INICIO_AUTOMATICO,
    StatusSessao.CANCELADA: EventoDefesa.CANCELAMENTO,
    StatusSessao.REALIZADA: EventoDefesa.LIBERACAO_DO_RESULTADO,  # feat-08, US-27
}

# (status_atual, novo_status) permitidos para TRANSIÇÃO (sessão já existente). A criação
# (None → AGENDADA) não entra aqui: é feita por `agendar_sessao`, nunca por `transicionar_status`.
TRANSICOES_VALIDAS = {
    (StatusSessao.AGENDADA, StatusSessao.REAGENDADA),
    (StatusSessao.REAGENDADA, StatusSessao.REAGENDADA),       # reagendar de novo
    (StatusSessao.AGENDADA, StatusSessao.EM_ANDAMENTO),       # início automático
    (StatusSessao.REAGENDADA, StatusSessao.EM_ANDAMENTO),
    (StatusSessao.AGENDADA, StatusSessao.CANCELADA),
    (StatusSessao.REAGENDADA, StatusSessao.CANCELADA),
    (StatusSessao.EM_ANDAMENTO, StatusSessao.CANCELADA),
    (StatusSessao.EM_ANDAMENTO, StatusSessao.REALIZADA),      # feat-08, US-27
}


def agendar_sessao(tcc, dados_basicos, dados_banca, autor):
    """Único ponto que cria a sessão (FR-001 a FR-020; FR-023). Pressupõe o TCC já travado e
    o conflito de horário já verificado (C3) pelo chamador — não valida nem trava nada por si.
    """
    sessao = Defesas.objects.create(def_tcc=tcc, def_status=StatusSessao.AGENDADA, **dados_basicos)
    _criar_local_ou_link(sessao, dados_basicos)
    _compor_banca(sessao, dados_banca)  # cria as linhas de BancaDefesa (research C4)
    registrar_evento(sessao, EventoDefesa.AGENDAMENTO, justificativa=None, autor=autor)
    return sessao


def transicionar_status(sessao, novo_status, autor, justificativa=None, **dados_evento):
    """Único ponto que muda def_status de uma sessão **já existente** e grava Historico_Defesas
    (FR-017, FR-023). Pressupõe a sessão já travada (`select_for_update`) pelo chamador, na mesma
    ordem de C3 — não trava nada por si. Levanta ValueError se a transição não estiver em
    TRANSICOES_VALIDAS; nesse caso, nenhuma linha é gravada.
    """
    anterior = sessao.def_status
    if (anterior, novo_status) not in TRANSICOES_VALIDAS:
        raise ValueError(f"Transição inválida: {anterior!r} → {novo_status!r}")
    sessao.def_status = novo_status
    sessao.save(update_fields=["def_status"])
    return registrar_evento(
        sessao, EVENTO_DA_TRANSICAO[novo_status], justificativa, autor, **dados_evento
    )
```

**"Alteração da Banca" e "Acionamento do Suplente"** (FR-011, FR-013) **não mudam `def_status`**
(data-model.md) — por isso chamam `registrar_evento(...)` **diretamente**, nunca
`transicionar_status` (que exigiria uma transição de status inexistente). Isso não contradiz o
FR-023 ("nenhum outro ponto do código grave `def_status`..."): a proibição é sobre gravar
`def_status`, não sobre chamar `registrar_evento` — esclarecimento acrescentado aqui por ser uma
leitura possível do texto do FR (achado menor M2 da revisão).

**Pré-condição obrigatória de quem chama** (mesma regra da spec 005, research C2): nem
`agendar_sessao` nem `transicionar_status` travam nada por si — quem chama trava antes, na ordem e
com a trava por docente de C3 (corrigida abaixo). A feat-08 (transição "Realizada") trava a sessão
antes de chamar `transicionar_status`.

**`autor=None`**: o início automático (chamado pelo comando de gestão agendado, sem usuário
logado) passa `autor=None`; `hdf_usu_id` aceita nulo no dicionário (3.6.7) exatamente para esse
caso — não é um erro a validar (achado menor M3 da revisão).

**Alternativas**: manter as duas funções numa só, com um parâmetro `criando=True/False` — rejeitada
por ser a mesma armadilha corrigida aqui: um "anterior" que às vezes vem do objeto e às vezes vem
de fora é o tipo exato de ambiguidade que gerou os 3 bloqueantes da spec 005 (ver
`specs/005-fluxo-do-tcc/research.md`, C2). Validar só que o `novo_status` é um valor do enum, sem
checar a transição — rejeitada pelo mesmo motivo da spec 005: um erro de cálculo de quem chama
passaria sem erro.

## C3. Ordem de trava (concorrência)

**Revisão do `arquiteto-django` (2026-10-30, bloqueante B2)**: a primeira versão desta decisão
propunha travar (`select_for_update`) as sessões **já existentes** candidatas a conflito. Isso não
cobre o Edge Case que a própria spec pede para evitar: duas sessões **novas**, para o mesmo
docente, em horários que se sobrepõem, agendadas quase ao mesmo tempo — nenhuma das duas sessões
existe ainda quando cada transação consulta conflitos, então não há nada para `select_for_update`
travar, e as duas transações concluem "sem conflito" e comitam.

**Decisão (corrigida)**: travar **os próprios docentes/membros propostos**, não as sessões deles,
antes de consultar conflitos — serializa qualquer par de transações que toquem o mesmo conjunto de
pessoas, independentemente de já terem sessão ou não:

```python
def _travar_membros(ids_usuarios):
    """Trava, em ordem fixa por pk (evita deadlock), os usuários propostos para a banca —
    serializa duas transações que disputam o mesmo docente, mesmo quando nenhuma das sessões
    em jogo existe ainda (research C3; bloqueante B2 da revisão do arquiteto-django)."""
    return list(
        Usuarios.objects.filter(pk__in=sorted(ids_usuarios)).select_for_update().order_by("pk")
    )
```

Usada, sempre **antes** de consultar `Defesas`/`BancaDefesa` para verificar conflito (FR-014 a
FR-016), nos 3 fluxos que propõem membro **novo** à agenda: `agendar_sessao` (banca inteira nova),
`reagendar` (mesma banca, novo horário) e `alterar_banca` (só o membro novo). `acionar_suplente`
**não** chama `_travar_membros`: o suplente já passou pela checagem de conflito quando entrou na
banca original (FR-013; cenário 6 da US-23 não pede revalidação), e promovê-lo a titular não propõe
ninguém novo à agenda — ver research C4. Depois da trava, nos 3 fluxos que a usam, a consulta de
conflito (`Defesas.objects.filter(def_status__in=STATUS_SESSAO_ATIVA, ...)` com join em
`BancaDefesa`) lê um estado que não pode mudar sob os pés da transação, porque qualquer outra
transação que também tente usar um desses docentes já está bloqueada esperando a mesma trava.

**Ordem completa de trava** (turma(s) do TCC → aluno → TCC → **membros propostos** → sessão →
banca), reaplicando o padrão das specs 004/005/006 com o acréscimo da trava por membro antes da
checagem de conflito, nos 3 fluxos listados (research C4 detalha `alterar_banca` usando a mesma
`_travar_membros`, achado B3 da revisão, e explica por que `acionar_suplente` não precisa).

**Alternativas**: travar as sessões candidatas (versão original) — não cobre criação simultânea
(bloqueante B2); nenhuma trava, confiando só na verificação antes do commit — pior ainda, mesma
falha; `SELECT ... FOR UPDATE` direto em `BancaDefesa` das sessões ativas — não ajuda porque, de
novo, a sessão nova não tem linha de `BancaDefesa` ainda no momento da checagem.

## C4. Composição e alteração da banca (US-23)

**Decisão**: `_compor_banca(sessao, dados_banca)` (chamada por `agendar_sessao`, C2) grava uma
linha de `BancaDefesa` por membro (`ban_papel` = Orientador/1º Avaliador/2º Avaliador/Suplente),
com o Orientador vindo de `services_orientacao.orientador_atual(tcc)` (somente leitura, nunca
escolhido pelo formulário). `alterar_banca(sessao, papel, novo_membro, justificativa, autor)` —
depois de `_travar_membros([novo_membro.pk])` e de revalidar o conflito do novo membro (C3,
achado B3) — substitui a linha do papel indicado
(`BancaDefesa.objects.filter(ban_def=sessao, ban_papel=papel).delete()` + `create()` do novo
membro), chama o stub de `descartar_avaliacoes(sessao, membro=antigo)` e `registrar_evento(sessao,
EventoDefesa.ALTERACAO_DA_BANCA, justificativa, autor, membro_removido=antigo,
membro_incluido=novo_membro)` **diretamente** (não muda `def_status`, C2).
`acionar_suplente(sessao, papel_substituido, autor, justificativa)` — sem trava de membro nova,
porque o suplente já está na banca — promove o suplente: atualiza a linha do suplente para o
papel do titular ausente, grava `ban_usu_substituido` e `ban_justificativa_substituicao` na linha
nova, remove a linha antiga do titular ausente, chama o stub de descarte para o ausente e
`registrar_evento(sessao, EventoDefesa.ACIONAMENTO_DO_SUPLENTE, ...)` diretamente.

**Exclusão de orientador/coorientadores** (FR-008, FR-009): usa
`services_orientacao.e_orientador_atual(usuario, tcc)` e `e_coorientador_ativo(usuario, tcc)` para
validar no `clean()` do formulário — a lista de opções já os exclui na renderização, mas a
validação do servidor repete a checagem (E4 da US-23: "isso só ocorre por requisição direta").

## C5. Confirmação, notificação, reagendamento e cancelamento (US-24)

**Decisão**: `confirmar_agendamento(sessao, autor)` — chamada logo depois de `agendar_sessao` (C2),
na mesma transação — recupera o link via
`services_entregas.link_mais_recente(entrega_documento_defesa)`, monta a notificação (data,
horário, formato, local ou link, título, aluno, link do documento), chama
`services.notificar`/`enviar_email_apos_commit` para o Aluno e cada membro de `BancaDefesa`
(`membros_efetivos(sessao)`, contrato §2), e chama
`services_orientacao.cancelar_troca_no_agendamento(tcc, agora)` com o mesmo `agora` gravado no
evento 'Agendamento' de `Historico_Defesas` (regra do "mesmo instante", já estabelecida pelo
contrato da spec 006). `reagendar(sessao, dados, justificativa, autor)` — depois de
`_travar_membros` com os pks de `membros_efetivos(sessao)` (C3, achado B3) e de revalidar
conflito — chama `transicionar_status(..., StatusSessao.REAGENDADA, ...)` e notifica sem tocar na
banca nem nas avaliações. `cancelar(sessao, justificativa, autor)` chama `transicionar_status(...,
StatusSessao.CANCELADA, ...)`, o stub de `descartar_avaliacoes(sessao)` (todos os membros) e
notifica a banca e o Aluno; o Status do TCC permanece "Apto para Defesa" porque esta spec nunca
grava `tcc_status`.

## C6. Início automático e lista de sessões (US-40, FR-021, FR-025 a FR-028)

**Decisão**: `sessoes_para_iniciar(agora)` (função pura, mesmo padrão de
`services_entregas.entregas_para_lembrar` da spec 005) devolve as sessões "Agendada"/"Reagendada"
cujo `def_data`+`def_h_inicio` já passou; aplicável tanto numa view (ao abrir a lista de Defesas,
chama a transição para as sessões encontradas antes de renderizar) quanto num comando de gestão
agendado (PGCS 9.4), documentado como pendência de agendamento para o Célio (mesmo tratamento do
research C5 da spec 005 para os lembretes de entrega).

`listar_defesas(usuario, filtros)` usa `select_related("def_tcc__tcc_alu__alu", "def_tcc__tcc_tur")`
e filtra por perfil (FR-024) **somando por `Q()` com OR** as condições de todos os perfis que o
usuário tem — nunca um if/elif que escolhe um único ramo — porque a mesma pessoa pode acumular
mais de um perfil em relação a sessões diferentes (ex.: Professor da Disciplina de uma turma e,
ao mesmo tempo, Avaliador de uma banca de outra turma; o resultado deve ser a união, não um dos
dois conjuntos):

```python
condicao = Q(def_tcc__tcc_alu=usuario)  # Aluno (só a própria sessão)
condicao |= Q(bancadefesa__ban_usu=usuario)  # Avaliador/Orientador/Suplente acionado
condicao |= Q(def_tcc__orientacoes__ori_usu=usuario, def_tcc__orientacoes__ori_ativo=True)
condicao |= Q(def_tcc__coorientacoes__coo_usu=usuario, def_tcc__coorientacoes__coo_ativo=True)
condicao |= Q(def_tcc__tcc_tur__tur_doc=usuario)  # Professor da Disciplina
if permissoes.e_coordenador_ou_secretaria(usuario):
    condicao |= Q(def_tcc__tcc_tur__tur_cur=permissoes.curso_id_do_usuario(usuario))
sessoes = Defesas.objects.filter(condicao).distinct()
```

Coordenador/Secretaria ainda usam `services_contas.filtro_de_curso(usuario, valor)` para trocar o
curso filtrado (US-39/US-40, FR-027), não para restringir o próprio acesso. O filtro de período
(FR-025) e o de Status (FR-026) se somam a esse `condicao` com `&`, sem consulta por linha. O
`.distinct()` evita linhas repetidas quando mais de uma condição bate na mesma sessão (ex.:
Orientador que também está na `BancaDefesa` como Presidente).

## C7. Histórico da defesa (US-40, FR-029)

**Decisão**: `historico_da_sessao(sessao) -> queryset` — todas as linhas de `Historico_Defesas`
daquela sessão, ordenadas por `hdf_data_hora`, **sem checagem de perfil** (quem chama decide se
autoriza), no mesmo padrão de `services_tcc.historico_do_status` (spec 005, research C9) — a view
desta spec aplica `pode_ver_sessao` antes de chamar; qualquer tela futura (painel do aluno, tela
de orientandos) que precise mostrar o link "Histórico da defesa" chama a mesma função, com a
própria checagem.

## C8. Mensagens e testes (SC-005, SC-006)

**Decisão**: `sigtcc/apps/defesa/mensagens.py` próprio do app (não dentro de
`cadastro/mensagens.py`), com as constantes exatas das US-21 a 24, 39 e 40. Se alguma mensagem
citada numa US não tiver o texto exato entre aspas na fonte, o `tasks.md` registra como provisória
(prefixo a definir, ex. `MD-XX`, "Mensagens Defesa"), no mesmo padrão já usado nas specs 004 a 006.
`tests/apoio_defesa.py` com fábricas que partem de `apoio_tcc`/`apoio_orientacao` (TCC "Apto para
Defesa" com Orientador vinculado) e acrescentam `agendar_sessao_de(tcc, **dados)`,
`compor_banca_de(sessao, **membros)` e `avancar_para(sessao, status)` (atalho de teste que chama
`transicionar_status` direto, sem passar pelas validações de UI).
