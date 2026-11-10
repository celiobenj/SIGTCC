# Research: Avaliação e Resultados do SIGTCC

**Feature**: [spec.md](spec.md) | **Plano**: [plan.md](plan.md) | **Data**: 2026-11-03

Decisões técnicas da feature 008 (US-25, US-26 e US-27). Cada item traz a decisão, o motivo e as
alternativas descartadas. Os nomes de função são os do contrato
([contracts/servicos-avaliacoes.md](contracts/servicos-avaliacoes.md)); o plano não traz código de
produção.

## A1. Organização do código no app `defesa`

**Decisão**: módulo de regras novo `sigtcc/apps/defesa/services_avaliacoes.py` (avaliação,
cálculo, sigilo, parecer e liberação), permissões novas em `permissoes_defesa.py` (mesmo arquivo da
spec 007), `forms_avaliacoes.py`, `views_avaliacoes.py`, rotas no `urls.py` já existente do app
(`app_name = "defesa"`), textos MA-01 a MA-14 e os das US-25 a US-27 em `mensagens.py`, templates em
`sigtcc/templates/defesa/`. O utilitário de PDF fica em `sigtcc/apps/defesa/pdf.py` (A9).

**Motivo**: a spec 007 já criou o app e o padrão (um serviço por domínio). A avaliação tem domínio
próprio (`Avaliacoes`, `Criterios` e os campos de envio de `BancaDefesa`) e é consumida pela spec
007 (`descartar_avaliacoes`) e pela feat-09 (cálculo e resultado), então merece módulo próprio,
como pede a descrição da feature (`services_avaliacoes.py`).

**Alternativas**: acrescentar tudo em `services_defesa.py` (arquivo já grande, com ~1000 linhas, e
misturaria agenda com avaliação); colocar o PDF em `cadastro` (os PDFs são do Épico 2).

## A2. Estado da avaliação de cada membro

**Decisão**: derivado, sem coluna nova (dicionário 3.6.4):

| Estado (rótulo da RBN-DEF-06.8) | Condição |
|---|---|
| Não avaliou | nenhuma linha em `Avaliacoes` para (sessão, membro) |
| Rascunho salvo | há linhas e `ban_data_envio` é nulo |
| Enviada | `ban_data_envio` preenchido |

`estado_da_avaliacao(sessao, membro)` e `estados_da_banca(sessao)` (uma consulta para os 3
membros efetivos, com `Count` sobre `Avaliacoes`, sem consulta por linha).

**Alternativas**: coluna de status em `BancaDefesa` (fora do dicionário; princípio III).

## A3. Cálculo das notas (RBN-DEF-06.1, RBN-DEF-06.2)

**Decisão**: tudo em `Decimal`, nunca `float`:

- nota individual = `Σ(ava_nota × cri_peso) / 10`, arredondada com
  `quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)`;
- nota final = média simples das 3 notas individuais **já arredondadas**, com o mesmo
  arredondamento;
- com artigo Qualis A ou B homologado (`services_artigos.tem_artigo_homologado_qualis_ab`), nota
  final = `max(Decimal("6.0"), média)`;
- os pesos vêm de `Criterios.cri_peso` (carga da spec 001), nunca de constante no código. Um
  teste confere que a soma dos pesos é 10,0 e as somas por componente são 7,0 e 3,0 (FR-001).

Casos de fronteira testados (SC-002): soma 6,05 → 6,1; 6,04 → 6,0; média de 5,9, 6,0 e 6,0 →
5,966… → 6,0; média 5,4 com Qualis A → 6,0; média 7,0 com Qualis B → 7,0.

**Alternativas**: `round()` do Python (arredonda meio para o par: 6,05 → 6,0 em `float`, errado
para a regra "a partir de 0,05 arredonda para cima"); calcular no banco com `ROUND()` do
PostgreSQL (correto, mas espalha a regra entre SQL e Python e dificulta o teste unitário).

## A4. Formulário Avaliação: salvar, enviar e reabrir (US-25, US-26)

**Decisão**:

- **Um formulário com 9 linhas** (um `Form` por critério num `formset` fixo, ordem dos critérios
  pela carga), campos Conceito, Nota (aceita vírgula; uma casa) e Observações (até 500). A
  validação da faixa do conceito (FR-009) e o "tudo ou nada" por critério (FR-013, MA-01; D4)
  ficam no form; a regra de "quais partes estão liberadas" (FR-011, FR-012) fica no serviço, que
  recebe só os critérios liberados e recusa os demais mesmo vindos por POST direto.
- **Salvar** (`salvar_rascunho`): grava em `Avaliacoes` os critérios **liberados** preenchidos
  (insere ou atualiza; um critério liberado esvaziado tem a linha apagada), com
  `ava_data_hora = agora`; não mexe em `ban_data_envio`. Os critérios bloqueados pelo status (a
  Parte Oral com a sessão Agendada ou Reagendada) **não são lidos, nem atualizados, nem
  apagados**: as notas orais de um rascunho continuam gravadas (D2; revisão I-01).
- **Avaliação já Enviada** (revisão I-02): com o membro "Enviada", o formulário fica só leitura
  até Reabrir minha avaliação; Salvar e Enviar recebidos por POST são recusados com a MA-13
  ("Sua avaliação já foi enviada. Para alterá-la, use Reabrir minha avaliação"; `/speckit-analyze`
  I1) — sem regravar notas nem a cópia da assinatura. A MA-04 fica só para depois da liberação.
- **Enviar** (`enviar_avaliacao`): exige os 9 critérios (E3) e a assinatura (E4), grava as linhas,
  a cópia da assinatura (A5) e `ban_data_envio = agora`.
- **Reabrir** (`reabrir_avaliacao`): só com a sessão "Em Andamento", sem liberação e com o membro
  "Enviada"; limpa `ban_data_envio` e `ban_assinatura_path` (a cópia é apagada depois do commit);
  as notas ficam (D6).
- **Trava**: as três operações travam turma → aluno → TCC → sessão (a mesma ordem da spec 007,
  research C3) e depois a linha `BancaDefesa` do membro, e reconferem status, liberação e vínculo
  depois de travar. Assim, um envio ou uma reabertura nunca passa no meio de uma liberação.
- **Início automático** (revisão I-04): as views `avaliacao`, `reabrir`, `registrar_parecer` e
  `liberar_resultado` chamam `services_defesa.iniciar_sessoes_vencidas()` antes da transação
  principal, como as telas da spec 007 (`_sessao_ou_404`, que passa a ser pública como
  `sessao_ou_404`), para que a Parte Oral se abra no horário marcado.
- O suplente acionado já está em `membros_efetivos` com o papel do titular; nada especial no
  formulário (US-25 D).

**Alternativas**: um formulário por componente (Parte Escrita e Parte Oral separados) — a US-25
descreve um formulário só, com a Parte Oral desabilitada antes da sessão.

## A5. Assinatura na avaliação (US-26; FR-015 a FR-018)

**Decisão**:

- A assinatura continua no armazenamento atual (`default_storage`, disco do serviço), como hoje no
  Meu perfil (spec 003); **nenhuma mudança de armazenamento** (decisão de 2026-11-03, plan).
- Validação pelo mesmo serviço da US-38: `services.tipo_da_assinatura(arquivo)` (tamanho até 2 MB
  e conteúdo real PNG ou JPG), com as mensagens da US-26 E2 e E3 (que diferem das da US-38).
  Como `tipo_da_assinatura` devolve `None` nos dois casos, o form confere `arquivo.size` antes,
  para escolher a mensagem certa (revisão M-09).
- **Dimensões** (revisão I-11): no envio, a imagem é aberta com o Pillow (já trazido pelo
  xhtml2pdf) e recusada se não abrir (mensagem de formato da US-26 E3) ou se passar de 2000 ×
  1000 pixels (MA-14, sem reduzir a imagem; `/speckit-analyze` A1), para que um PNG pequeno em
  bytes e enorme em pixels não estoure a memória do worker ao montar o PDF.
- **Cópia órfã** (revisão M-11): se a transação do envio desfizer depois de a cópia ter sido
  gravada, a cópia é apagada no tratamento da exceção; se o arquivo do perfil sumir no meio, o
  envio cai na mensagem da assinatura obrigatória (US-26 E4).
- No envio, o sistema guarda uma **cópia** da imagem usada em
  `assinaturas_banca/<def_id>_<usu_id>_<aleatório>.<ext>` e o caminho em `ban_assinatura_path`
  (dicionário: "Cópia da imagem de assinatura usada no envio"), para que uma troca posterior no
  perfil não mude a avaliação já enviada. A cópia anterior do mesmo membro é apagada depois do
  commit.
- "Usar a assinatura do perfil": copia o arquivo de `doc_assinatura_path`/`mem_assinatura_path`.
  Se o arquivo do perfil não existir mais no disco (deploy no Render gratuito), a opção não
  aparece, e o membro anexa uma imagem.
- "Salvar esta imagem no meu perfil": chama `services.salvar_assinatura` (spec 003) na mesma
  transação.
- **Prévia** (US-26 passo 4 e fluxo C, "Atualizar imagem"): mostrada no navegador
  (`URL.createObjectURL`) antes do envio, com conferência de tamanho e extensão no próprio
  navegador para dar a mensagem na hora; o servidor confere de novo no envio (é a validação que
  vale). A prévia da assinatura do perfil usa a rota já existente `cadastro:assinatura`.
- A cópia da avaliação só é servida ao próprio membro (`defesa:assinatura_avaliacao`), por view
  que confere a permissão e nunca por URL pública.

**Alternativas**: armazenamento externo privado (descartado em 2026-11-03: a equipe aceitou que
as imagens sumam a cada deploy; ideias futuras S-04 e S-06 no índice); upload em dois passos com
prévia gravada no servidor (gravaria arquivos que podem ser abandonados).

## A6. Parecer, nota final e liberação (US-27)

**Decisão**:

- **Nota final e parecer preliminar** (`apuracao(sessao)`): calculados na hora, só com os 3
  envios; parecer automático para nota < 6,0 (Reprovado) e TCC 1 ≥ 6,0 (Aprovado para TCC 2); em
  TCC 2 ≥ 6,0, o parecer é o gravado em `def_parecer` pelo Registrar parecer (ou nenhum).
- **Registrar parecer** (`registrar_parecer`): só o Orientador (Presidente), sessão "Em
  Andamento", 3 envios, TCC 2 e nota ≥ 6,0; grava `def_parecer` (Aprovado ou Aprovado com
  Correções). Sem escolha: "Selecione o parecer da banca para continuar" (D1).
- **Parecer limpo quando os 3 envios deixam de estar completos** (D3, revista na revisão B-01,
  Célio Benjamim, 2026-11-03; Q-135): não há coluna para guardar a nota do momento do registro,
  então o critério é o conjunto de envios. `def_parecer` é limpo em `reabrir_avaliacao`,
  `descartar_avaliacoes` (acionamento do suplente, alteração da banca, cancelamento) e
  `voltar_envios_a_rascunho` (reagendamento). No novo 3º envio, o Orientador escolhe de novo,
  mesmo que a nota final seja igual. `apuracao` também ignora um `def_parecer` gravado quando a
  nota final ficou abaixo de 6,0 (o parecer passa a Reprovado automático). Testes dos quatro
  caminhos.
- **Quem é o Orientador** (revisão M-07): `pode_liberar` e `pode_registrar_parecer` usam o papel
  na banca (`ban_papel == "Orientador (Presidente)"`), como a spec; `registrar_parecer` recusa
  com a mensagem da US-27 E4, porque registrar o parecer é parte da liberação (US-27 passos 6 a
  8).
- **Liberar** (`liberar_resultado(usuario, def_id, nota_confirmada, parecer_confirmado)`): GET
  mostra a confirmação MA-05 com a nota e o parecer; o POST traz os valores mostrados. Numa
  transação: trava turma → aluno → TCC → sessão; confere Orientador (E4), "Em Andamento", 3
  envios, parecer (D1); recalcula com a homologação vigente; se diferir do confirmado, não grava
  e devolve os valores novos para a tela reabrir a confirmação (D10); grava `def_nota_final`,
  `def_parecer` e `def_data_liberacao_resultado`; `transicionar_status(sessao, REALIZADA,
  usuario)` (evento "Liberação do Resultado"); `atualizar_status_tcc(tcc, turma, usuario,
  parecer, LIBERACAO_DO_RESULTADO)`; notificações (MA-06 a MA-08) e e-mails depois do commit;
  ponto de chamada da feat-09 depois do commit (A10).
- **D10 em TCC 2 quando a nota sobe a 6,0 ou mais** (revisão I-03): o novo parecer não é
  automático; a liberação não grava e volta à sessão com Registrar parecer disponível e Liberar
  Resultado desabilitado (D1), sem abrir a confirmação. Nos demais casos (parecer automático),
  a confirmação reabre com os valores novos.
- O parecer tem o mesmo texto do Status do TCC de destino (`Parecer` e `StatusTCC`), então o
  mapeamento é direto.
- **Imutável depois**: todo serviço de escrita confere `def_data_liberacao_resultado is None` e
  status "Em Andamento" (ou "Agendada"/"Reagendada" para o rascunho) depois de travar (FR-022,
  MA-04).

**Alternativas**: gravar `def_nota_final` antes da liberação (o dicionário diz "gravada na
liberação"); recalcular sem pedir nova confirmação quando a nota muda (D10 decidiu reabrir).

## A7. Sigilo (RBN-DEF-06.8; FR-031, FR-032; D7)

**Decisão**: uma função única, `visao_da_avaliacao(usuario, sessao)`, devolve o que cada pessoa
pode ver; views e templates só exibem o que vem nela:

**Mais de um papel** (revisão I-05): o papel efetivo na banca prevalece sobre Professor da
Disciplina e Secretaria. O Professor da Disciplina que é Orientador (Presidente), comum em
Sistemas de Informação e Licenciatura em Computação, vê como Orientador. Teste próprio.

| Quem | Antes da liberação | Depois da liberação |
|---|---|---|
| Membro efetivo (não Orientador) | a própria avaliação + estado dos colegas | notas por critério e por avaliador, nota final e parecer; as próprias Observações |
| Orientador (Presidente) | idem + nota final e parecer preliminar, só com os 3 envios | idem |
| Suplente não acionado | nada do bloco de avaliação | idem a membro |
| Professor da Disciplina, Secretaria, Aluno | nada do bloco de avaliação (nem estados) | notas por critério e por avaliador, nota final e parecer; nenhuma Observação |

Testes por perfil em todas as telas (sessão, Minhas bancas, formulário, Defesas, Meu TCC) e pelo
endereço direto (SC-003).

**Alternativas**: condicionais espalhados nos templates (contra o princípio IV e difícil de
testar).

## A8. Minhas bancas e Critérios (RBN-DEF-05.4, RBN-DEF-04.2)

**Decisão**:

- `minhas_bancas(usuario)`: linhas de `BancaDefesa` do usuário com a sessão, exceto
  "Cancelada", ordenadas por data e hora; `select_related` da sessão, TCC, aluno e turma; estados
  calculados numa consulta (A2); o link mais recente do Documento para Defesa de todas as linhas
  vem de uma consulta só (`Subquery` sobre `HistoricoEnviosEntregas`), sem chamar
  `link_do_documento` por linha (revisão M-12). Antes de listar, chama `services_defesa.iniciar_sessoes_vencidas()`
  (padrão das telas da spec 007).
- Item de menu "Minhas bancas" para os perfis `docente` e `membro_externo` (IC-02).
- Clicar na linha abre `defesa:sessao` (spec 007); a sessão já libera a banca toda (FR-030 da
  007).
- Janela "Critérios de avaliação": lê `Criterios` em ordem de carga; somente leitura; acessível a
  quem tem perfil `docente` ou `membro_externo` (é consulta de normas, sem dado pessoal).
- Botão Declaração: aparece quando `declaracao_disponivel(sessao, usuario)` (contrato com a
  feat-09) devolve verdadeiro; até a feat-09, a função devolve falso.

## A9. PDFs sob demanda (infraestrutura para a feat-09)

**Decisão (Célio Benjamim, 2026-11-03)**: **nenhum PDF é gravado**. A Ata Final, a Folha de
Aprovação e as declarações são geradas a cada pedido, a partir dos dados congelados na liberação,
e entregues direto na resposta. Esta feature entrega só a infraestrutura, em commits
`chore(config)`:

- `xhtml2pdf` no `requirements.txt` (versão exata do `pip freeze` na instalação, sem CVE
  conhecida, com as dependências que ele trouxer), item de configuração do PGCS 3.7. Antes do
  merge, `pip install -r requirements.txt` num Linux limpo com Python 3.12 (contêiner
  `python:3.12-slim`) para conferir que nenhuma dependência exige biblioteca de sistema (ex.:
  cairo, via svglib/rlPyCairo); se exigir, fixar a versão que não exige. Resultado no PR
  (revisão I-13);
- `sigtcc/apps/defesa/pdf.py`: `gerar_pdf(template, contexto) -> bytes` e
  `resposta_pdf(nome_arquivo, template, contexto) -> HttpResponse`
  (`Content-Disposition: attachment`, `Cache-Control: no-store`). O `xhtml2pdf` é importado só
  dentro de `gerar_pdf`, para não pesar na memória dos dois workers; um PDF por requisição
  (revisão I-11);
- `link_callback` fechado (revisão I-12): aceita só caminho relativo de `static/` ou de `media/`;
  qualquer esquema (`http:`, `https:`, `file:`, `data:`) ou caminho que, resolvido com
  `realpath`, saia de `STATIC_ROOT` (ou dos diretórios dos finders) e de `MEDIA_ROOT` devolve
  `None`, e a imagem não entra. Os templates de PDF **não estendem `base.html`** (que carrega
  fontes do Google) e usam fontes TTF locais em `sigtcc/static/`; autoescape ligado.
  `test_pdf.py` cobre `http://`, `file://` e `../`;
- uma falha na geração vira exceção própria (`ErroAoGerarPdf`), registrada no log, para a
  feat-09 exibir a mensagem da US-28 E3;
- **sem `STORAGES` externo**: o `default_storage` continua o padrão do Django (disco), sem
  mudança no `settings.py`;
- a view que entrega cada PDF é da feat-09 e segue a regra: confere a permissão, gera e
  devolve; sem endereço público e sem arquivo em disco.

Imagem de assinatura ausente (arquivo apagado por deploy): o PDF sai sem a imagem (decisão de
2026-11-03; assinatura eletrônica fora do escopo). Coordenador de Curso: o atual no momento do
download (risco aceito; ideia futura S-05).

**Alternativas**: armazenamento externo privado (Cloudflare R2, Backblaze B2 ou Supabase) e PDFs
gravados na liberação, como diziam o PGCS 3.4, 3.5 (itens 8 e 9), 3.7, 9.1 e 9.5 (descartado: a
equipe prefere não armazenar arquivos); WeasyPrint (melhor CSS, mas depende de bibliotecas do sistema, Pango/Cairo, que o
Render gratuito não garante; o PGCS já escolheu o xhtml2pdf).

Impacto nos documentos (ajustes de texto, sem mudança de regra de negócio): ver plan, "Documentos
a ajustar".

## A10. Ponto de chamada da feat-09

**Decisão**: depois do commit da liberação, `liberar_resultado` registra
`transaction.on_commit(..., robust=True)` para `services_documentos.ao_liberar_resultado(sessao)`
(nome combinado com a feat-09), que enviará as declarações de participação por e-mail
(RBN-DEF-08.3, PDF gerado em memória e anexado). Com `robust=True`, uma exceção não impede os
callbacks seguintes (os e-mails da liberação) nem vira erro 500; o contrato manda a feat-09
rodar o trabalho pesado numa thread, como `enviar_email_apos_commit`, com a falha só no log
(revisão I-10; D9). Até a feat-09, o módulo `services_documentos.py` existe só com esse stub, que
registra o pedido em log. A Ata e a Folha não são geradas na liberação (A9).

**Alternativas**: chamar dentro da transação (uma falha de e-mail ou de PDF desfaria a liberação,
contra a D9).

## A11. Mudanças em código de outras specs (Q-128)

**Decisão**: lista fechada no plan ("Itens de configuração"); cada uma relatada no PR:

- `services_defesa.descartar_avaliacoes` delega para `services_avaliacoes.descartar_avaliacoes`
  (contrato §6 da 007);
- **ordem do descarte** (revisão I-07): em `acionar_suplente` e `alterar_banca`,
  `descartar_avaliacoes` passa a ser chamado **antes** do `delete()` da linha de `BancaDefesa`,
  para ler `ban_assinatura_path` e apagar a cópia da imagem depois do commit (senão a imagem do
  ausente fica no disco sem referência);
- `services_defesa.alterar_banca` (D16, com a resposta da Q-135): quem só troca de papel **entre
  titulares** (1º ↔ 2º Avaliador) mantém o rascunho; quem sai da banca **ou passa a Suplente**
  tem as avaliações descartadas. Para quem continua na banca, a linha é atualizada
  (`update(ban_papel=...)`) em vez de apagada e recriada, preservando
  `ban_usu_substituido` e `ban_justificativa_substituicao` (revisão M-08); o teste chama
  `connection.check_constraints()` para provar a FK adiada;
- `services_defesa.reagendar` chama `services_avaliacoes.voltar_envios_a_rascunho(sessao)` antes
  de `transicionar_status` (D2; inofensivo quando a sessão estava "Agendada" ou "Reagendada",
  porque nelas não há envio);
- `services_defesa` ganha funções públicas `tcc_da_sessao(def_id)`, `travar_tcc(tcc_id)` e
  `travar_sessao(def_id)`, que só expõem as privadas `_tcc_da_sessao`, `_travar_tcc` e
  `_travar_sessao`, e `views_defesa.sessao_ou_404` deixa de ser privada (a feat-08 precisa da
  mesma ordem de trava e do início automático e não deve importar função privada);
- **spec 007 e contrato** (revisão I-09; CLAUDE.md: mudança depois do merge começa pela spec):
  FR-011 (D16), FR-019 (D2) e Clarifications da spec 007 e o contrato `servicos-defesa.md`
  (§6 entregue, ordem do descarte, travas públicas) atualizados no `/speckit-plan` desta
  feature;
- `defesa/historico.html` mostra a nota final e o parecer no evento "Liberação do Resultado"
  (D15), lidos de `Defesas`;
- `cadastro/menu.py`: item "Minhas bancas";
- aba Meu TCC (spec 005): seção "Resultado da defesa" (FR-033);
- `popular_demo`: avaliações de exemplo (A12).

## A12. Cenário de demonstração (`popular_demo`)

**Decisão**: sobre as sessões que a spec 007 já cria (uma por status), acrescentar, só por
`services_avaliacoes`: na sessão "Em Andamento", 2 avaliações enviadas e 1 rascunho; numa segunda
sessão "Em Andamento" de TCC 2, 3 envios (pronta para liberar); e uma sessão liberada (TCC 1,
Aprovado para TCC 2). Nunca criar `Avaliacoes` ou mudar status direto.

Assinaturas de demonstração (revisão I-15): o `popular_demo` roda na estação, com a
`DATABASE_URL` externa (PGCS 9.3), então qualquer imagem que ele grave fica no `media/` local e
não existe no Render. Os envios de demonstração usam uma imagem estática do repositório
(`sigtcc/static/img/assinatura_demo.png`), cujo caminho o serviço aceita como origem da cópia;
como a cópia em `media/` também não chega ao Render, o quickstart avisa que, em produção, a
imagem de assinatura das avaliações de demonstração não aparece (risco já aceito).

## A13. Testes

**Decisão**: um arquivo por US (`test_us25_avaliacao.py`, `test_us26_assinatura.py`,
`test_us27_liberacao.py`), mais `test_calculo_notas.py` (SC-002), `test_sigilo.py` (SC-003, por
perfil e por tela), `test_minhas_bancas.py`, `test_pdf.py` (gera um PDF de um template de teste e
confere o `link_callback` sem rede), `test_mensagens_avaliacao.py` (texto exato, SC-007) e
ajustes nos testes da spec 007: `test_us23_banca.py` (troca entre titulares mantém o rascunho,
ida a Suplente descarta, cópia da assinatura apagada no acionamento do suplente),
`test_us24_...` (reagendamento devolve envios a rascunho e limpa o parecer) e
`test_base_defesa.py` (o teste do stub, `TesteDescartarAvaliacoesStub`, dá lugar ao teste da
delegação; revisão I-08). Reaproveita `apoio_defesa.py` e
acrescenta fábricas de avaliação (`apoio_avaliacao.py`). Uploads com imagens geradas em memória
(PNG de 500 KB e de 3 MB; `.pdf` falso) e `MEDIA_ROOT` temporário nos testes.
