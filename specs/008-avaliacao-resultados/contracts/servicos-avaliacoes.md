# Contrato: o que a spec 007, a feat-09 e outras telas podem chamar (feature 008)

**Feature**: [../spec.md](../spec.md) | **Pesquisa**: [../research.md](../research.md)

Mudar qualquer item deste contrato é mudança de comportamento e começa pela spec 008. O contrato
da spec 007 (`specs/007-agendamento-banca/contracts/servicos-defesa.md`) continua valendo; esta
feature o cumpre: nunca grava `def_status` nem `Historico_Defesas` direto, nunca cria sessão, usa
`transicionar_status` só para "Em Andamento" → "Realizada".

## 1. Avaliações (`services_avaliacoes.py`)

| Item | Uso |
|---|---|
| `descartar_avaliacoes(sessao, membro=None)` | apaga as linhas de `Avaliacoes` do membro (ou de todos), limpa `ban_assinatura_path` e `ban_data_envio` e apaga a cópia da imagem depois do commit; limpa `def_parecer` (D3 revista, Q-135). Chamado pela spec 007 (cancelamento; alteração da banca para quem sai ou vai a Suplente; acionamento do suplente), dentro da transação dela, com a sessão já travada e **antes** do `delete()` da linha de `BancaDefesa` (para ler o caminho da cópia). Substitui o stub (contrato §6 da 007; Q-125). |
| `voltar_envios_a_rascunho(sessao)` | mantém as notas, limpa envio e assinatura de todos os membros e limpa `def_parecer`; chamado por `services_defesa.reagendar` antes de `transicionar_status` (D2). |
| `nota_individual`, `nota_final`, `estados_da_banca`, `resultado_da_sessao` | consideram só os `membros_efetivos` (um Suplente não acionado com linhas antigas não entra; revisão I-06). |
| `estado_da_avaliacao(sessao, membro)` / `estados_da_banca(sessao)` | "Não avaliou", "Rascunho salvo" ou "Enviada" (research A2). |
| `nota_individual(sessao, membro)` / `nota_final(sessao)` | `Decimal` com uma casa, `ROUND_HALF_UP` (research A3); `nota_final` devolve `None` sem os 3 envios. A feat-09 usa depois da liberação. |
| `resultado_da_sessao(sessao)` | para sessões "Realizada": nota final, parecer, data da liberação, notas individuais e por critério dos 3 membros efetivos, se o Qualis elevou a nota (para a observação da Ata, RBN-DEF-07.1). Fonte única da Ata Final, da Folha de Aprovação e da tela do aluno. |
| `visao_da_avaliacao(usuario, sessao)` | o que cada pessoa pode ver (research A7). Qualquer tela nova que mostre nota usa esta função. |

## 2. Documentos (`services_documentos.py`, ponto de chamada para a feat-09)

| Item | Uso |
|---|---|
| `ao_liberar_resultado(sessao)` | registrado com `transaction.on_commit(..., robust=True)` depois da liberação. **Stub** nesta feature (só log). A feat-09 troca o corpo para enviar as declarações de participação por e-mail (RBN-DEF-08.3), sem mudar a assinatura, rodando o trabalho pesado numa thread (como `enviar_email_apos_commit`) e registrando a falha só no log (D9). |
| `declaracao_disponivel(sessao, usuario) -> bool` | decide o botão Declaração em Minhas bancas. **Stub** que devolve `False`; a feat-09 troca o corpo. |
| `services_documentos.avisar_pendencia_da_ata(sessao) -> str \| None` (emenda de 2026-11-04, spec 009 P1; plan 009, research B5) | chamada por `views_avaliacoes.liberar_resultado` **depois do commit**, de forma síncrona, para mostrar ao Orientador o alerta da E2 e notificar o Coordenador ou a Secretaria do curso. Não grava nada da sessão, não desfaz a liberação e uma falha dela só vai para o log. |

## 3. PDF sob demanda (`pdf.py`)

| Item | Uso |
|---|---|
| `gerar_pdf(template, contexto) -> bytes` | gera o PDF em memória com o xhtml2pdf (importado só aqui); `link_callback` aceita só caminho relativo de `static/` ou `media/` resolvido dentro de `STATIC_ROOT`/finders ou `MEDIA_ROOT`, nunca esquema `http(s)`, `file` ou `data` (research A9); templates de PDF não estendem `base.html` e usam fontes locais; falha → `ErroAoGerarPdf` (com log). |
| `resposta_pdf(nome_arquivo, template, contexto) -> HttpResponse` | resposta para download (`attachment`, `no-store`). Quem chama confere a permissão antes; nenhum arquivo é persistido (o xhtml2pdf pode usar arquivo temporário durante a geração). |
| Imagem de assinatura ausente | o template mostra o espaço sem imagem (decisão de 2026-11-03). |

## 4. Travas (`services_defesa.py`, acrescentadas por esta feature)

| Item | Uso |
|---|---|
| `tcc_da_sessao(def_id)`, `travar_tcc(tcc_id)` e `travar_sessao(def_id)` | versões públicas das funções da spec 007 (turma → aluno → TCC → sessão), para a feat-08 e a feat-09 seguirem a mesma ordem. Chamar as travas dentro de `transaction.atomic()`. |
| `views_defesa.sessao_ou_404(def_id)` | busca a sessão depois de rodar o início automático; usada pelas views desta feature. |
