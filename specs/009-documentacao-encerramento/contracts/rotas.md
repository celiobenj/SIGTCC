# Contrato: rotas e telas da feat-09

**Feature**: [spec.md](../spec.md) | **Plano**: [plan.md](../plan.md)

Todas no namespace `defesa` (`sigtcc/apps/defesa/urls.py`); views em `views_documentos.py`
(documentos e agenda) e `views_ouvintes.py` (ouvintes, ocorrências e Ouvintes das defesas).
Todas com `perfil_requerido(...)`: sem login → tela de login com `next`, e a ação segue depois
(US-28 cenário 9; US-30 cenário 11). Recusas: research B3.

| Nome | Caminho | Métodos | Perfis (`perfil_requerido`) | Permissão (research B2) | Resposta |
|---|---|---|---|---|---|
| `ata_final` | `defesas/<int:def_id>/ata-final/` | GET | qualquer logado | `pode_baixar_documentos` (senão 403 com `SEM_PERMISSAO_DOCUMENTOS`) | PDF `ata_final_<def_id>.pdf`; E2 → redireciona com a E2 (Presidente da banca) ou MX-08; E3 → redireciona com `ERRO_AO_GERAR_DOCUMENTOS` |
| `folha_aprovacao` | `defesas/<int:def_id>/folha-aprovacao/` | GET | qualquer logado | `pode_baixar_documentos` | PDF `folha_aprovacao_<def_id>.pdf`; TCC 1 → `FOLHA_NAO_SE_APLICA`; Reprovado → `FOLHA_REPROVADO`; E3 |
| `declaracao` | `defesas/<int:def_id>/declaracao/` | GET | qualquer logado (revisão I-04) | `pode_baixar_declaracao` (senão 403 com `SEM_PERMISSAO_DOCUMENTOS`) | PDF `declaracao_participacao_<def_id>.pdf`; E3 |
| `ouvintes` | `defesas/<int:def_id>/ouvintes/` | GET, POST | `docente` | `pode_editar_ouvintes` (senão 403, M-02; `TurmaArquivada` da trava também vira 403) | GET: janela Ouvintes (formset). POST válido: grava a lista, "Ouvintes salvos com sucesso", volta à sessão. POST inválido: a janela com os erros e os campos destacados |
| `ocorrencias` | `defesas/<int:def_id>/ocorrencias/` | GET, POST | `docente` | `pode_editar_ocorrencias` (senão 403, M-02; `TurmaArquivada` da trava também vira 403) | GET: janela Ocorrências. POST válido: MX-06, volta à sessão. Acima de 2.000: MX-01, caixa destacada |
| `agenda` | `defesas/agenda/` | GET | `docente`, `coordenador`, `secretaria` | `pode_gerar_agenda` | PDF `agenda_defesas.pdf`; sem sessões → volta a `defesa:defesas` com `SEM_DEFESAS_AGENDADAS`; filtro inválido → volta com a query string original (a tela já mostra os erros do form); E3 |
| `ouvintes_das_defesas` | `ouvintes-das-defesas/` | GET | `secretaria` | `pode_ver_ouvintes_das_defesas` | Tela somente leitura com filtros de período e Curso; vazia → MX-07 |

Parâmetro `origem` dos downloads da Ata e da Folha: `sessao` (padrão) ou `meu_tcc`; qualquer
outro valor vale `sessao`. Decide só para onde a recusa redireciona (nunca uma URL livre).

`defesas/agenda/` fica antes de `defesas/<int:def_id>/` na lista (não há conflito, porque
`<int:...>` não casa com "agenda", mas a ordem deixa a leitura clara).

## Telas e parciais

| Template | Uso |
|---|---|
| `defesa/_bloco_documentos.html` | bloco `documentos` de `sessao.html`: botões Ata Final (PDF), Folha de Aprovação (PDF) e Declaração, conforme `visao_dos_documentos` |
| `defesa/_bloco_ouvintes.html` | bloco `ouvintes`: botão Ouvintes (quem edita) ou a mensagem da E7; lista só leitura (Secretaria, P3, turma arquivada) |
| `defesa/_bloco_ocorrencias.html` | bloco `ocorrencias`: botão Ocorrências (Orientador, Em Andamento, sem liberação) ou o texto só leitura (P10) |
| `defesa/form_ouvintes.html` | janela Ouvintes: linhas Nome Completo e Matrícula, Remover, Adicionar, Cancelar e Salvar |
| `defesa/form_ocorrencias.html` | janela Ocorrências: caixa de texto com contador de 2.000 caracteres, Cancelar e Salvar |
| `defesa/ouvintes_das_defesas.html` | tela da Secretaria (`_filtro_periodo.html` + filtro de Curso) |
| `defesa/_documentos_aluno.html` | aba Meu TCC: documentos de cada sessão Realizada do TCC (P14) |
| `defesa/pdf/ata_final.html`, `folha_aprovacao.html`, `declaracao.html`, `agenda.html` | PDFs; estendem `defesa/pdf/base_pdf.html` |
| `defesa/emails/declaracao.txt` | corpo do e-mail da declaração (MX-04) |

Botões novos em telas existentes: "Agenda de defesas (PDF)" em `defesa/defesas.html` (com a
query string atual); link "Declaração" de `defesa/minhas_bancas.html` passa a `defesa:declaracao`;
item de menu "Ouvintes das defesas" (`cadastro/menu.py`, perfil `secretaria`, ao lado do item
"Defesas", com ícone Material Symbols `groups`; ordem e seção definidas no `/speckit-tasks` pela
estrutura atual do `menu.py`).

As views da agenda e de Ouvintes das defesas chamam `services_defesa.iniciar_sessoes_vencidas()`
antes de consultar, como as demais telas da Defesa.
