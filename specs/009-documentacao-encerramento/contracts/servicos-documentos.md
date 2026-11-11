# Contrato: serviços da feat-09

**Feature**: [spec.md](../spec.md) | **Plano**: [plan.md](../plan.md)

O que esta feature oferece a outras partes do sistema (spec 008, aba Meu TCC, `popular_demo` e o
Épico 3) e o que consome. Assinaturas em Python; nomes definitivos para o `/speckit-tasks`.

## 1. `services_documentos.py` (Épico 2)

| Função | Contrato |
|---|---|
| `ao_liberar_resultado(sessao)` | **Corpo real** (assinatura e ponto de chamada da spec 008 inalterados). Relê a sessão, monta no callback itens só com valores simples (contexto, assunto, corpo, endereço e `pk` da conta) e os entrega a `_enviar_declaracoes(itens)`, sem acesso ao banco, numa thread (ou síncrono com `SIGTCC_EMAIL_SINCRONO`). Falha só no log; nunca levanta (research B7) |
| `declaracao_disponivel(sessao, usuario) -> bool` | **Corpo real**: `pode_baixar_declaracao(usuario, sessao)` (research B8) |
| `avisar_pendencia_da_ata(sessao) -> str \| None` | **Emenda à spec 008** (contrato §2 dela). Chamada por `views_avaliacoes.liberar_resultado` depois do commit. Relê a sessão; com a E2, numa transação própria, notifica o Coordenador (MX-03, link para o perfil) ou cada Secretaria do curso (MX-09, link para a sessão) e devolve o texto da E2; senão `None`. Exceção: log e `None` (research B5) |
| `situacao_da_ata(sessao) -> str \| None` | `SEM_COORDENADOR`, `SEM_ASSINATURA` ou `None`. Caminho gravado com arquivo ausente: `None` (Q-140) |
| `dados_da_ata(sessao) -> dict` / `dados_da_folha(sessao) -> dict` | Contexto simples dos PDFs (research B4). Só com resultado liberado |
| `folha_aplicavel(sessao) -> str \| None` | `None` se a Folha existe; senão a mensagem (`FOLHA_NAO_SE_APLICA` ou `FOLHA_REPROVADO`) |
| `codigo_de_validacao(sessao, usuario) -> str` | 16 caracteres `A-Z2-7`, determinístico (research B6) |
| `dados_da_declaracao(sessao, usuario) -> dict` | Contexto da declaração com o código; só para membro efetivo |
| `agenda_de_defesas(usuario, periodo, cur_id) -> list` | Dias com as sessões Agendadas e Reagendadas (research B12); `cur_id` ignorado fora de Coordenador e Secretaria |
| `visao_dos_documentos(usuario, sessao) -> dict` | Botões do bloco `documentos` |
| `documentos_do_aluno(tcc) -> list` | Sessões Realizadas e liberadas do TCC com os botões aplicáveis (P14) |

## 2. `services_ouvintes.py` (Épico 2)

| Função | Contrato |
|---|---|
| `salvar_ouvintes(usuario, def_id, linhas)` | Grava a lista inteira numa transação, com a trava turma → aluno → TCC → sessão (`travar_tcc` + `travar_sessao`) e as matrículas novas em ordem crescente; duplicata só dentro da lista enviada; levanta `ErroOuvintes` (campo e mensagem) sem gravar nada (research B9) |
| `ouvintes_da_sessao(sessao) -> QuerySet` | Ouvintes da sessão, por nome |
| `registrar_ocorrencias(usuario, def_id, texto)` | Grava `def_ocorrencias`, com a mesma trava turma → aluno → TCC → sessão (research B10) |
| `visao_da_sessao(usuario, sessao) -> dict` | Blocos `ouvintes` e `ocorrencias` |
| `ouvintes_das_defesas(periodo, cur_id) -> QuerySet` | `periodo`: o Q sobre `Defesas` de `FiltroPeriodoForm.filtro()` (sem prefixo); `cur_id`: curso ou `None` (todos). Linhas da tela da Secretaria, reaproveitável pelo relatório RBN-REL-03.4 (Épico 3) (research B11) |

## 3. Consumido de outras specs (sem mudança de assinatura)

- Spec 007: `membros_efetivos`, `travar_tcc`, `travar_sessao`, `tcc_da_sessao`,
  `FiltroPeriodoForm.filtro()` (Q sobre `Defesas`, sem mudança), `iniciar_sessoes_vencidas`,
  `views_defesa.sessao_ou_404`,
  `contexto_da_sessao` (acréscimo de chaves), blocos de `sessao.html`.
- Spec 008: `resultado_da_sessao`, `e_tcc_2`, `permissoes_defesa._e_presidente` (passa a delegar
  para a pública `e_presidente`), `pdf.gerar_pdf` (com a trava de módulo, IC-14), `pdf.resposta_pdf`,
  `ErroAoGerarPdf`, `defesa/pdf/base_pdf.html`.
- Spec 002/003/006: `services_contas.filtro_de_curso`, `services.notificar`,
  `services.enviar_email` (com o novo parâmetro opcional `anexos`, IC-12),
  `services.caminho_da_assinatura`, `services_turmas.turma_arquivada`. O "Orientador do
  trabalho" é o Presidente da banca, não `e_orientador_atual` (Clarifications, B-03).

## 4. Regras que nenhum chamador pode quebrar

- Nenhum PDF é gravado em disco ou banco (SC-003); `def_ata_final_path` e
  `def_folha_aprovacao_path` continuam nulos.
- Esta feature nunca grava `def_status`, `Historico_Defesas` nem cria sessão (contrato da 007).
- `Ouvintes` nunca é alterado nem apagado; só `Presenca_Ouvintes` muda.
- O aviso da E2 e o envio das declarações nunca desfazem nem bloqueiam a liberação.
