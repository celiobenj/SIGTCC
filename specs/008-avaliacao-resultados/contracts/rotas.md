# Contrato: rotas e telas da feature 008

**Feature**: [../spec.md](../spec.md) | **Plano**: [../plan.md](../plan.md)

Todas as rotas ficam em `sigtcc/apps/defesa/urls.py` (`app_name = "defesa"`, incluído pela spec
007). Todas exigem login (`perfil_requerido`); sem sessão, a tela de login e depois a página
pedida (US-25 E1, US-26 E1, US-27 E1). Nenhuma rota entrega arquivo por endereço público. As
rotas com `<def_id>` passam por `views_defesa.sessao_ou_404`, que roda o início automático das
sessões antes (research A4).

| Nome | Método e caminho | View | Quem | Tela / efeito | Erros |
|---|---|---|---|---|---|
| `defesa:minhas_bancas` | GET `/minhas-bancas/` | `views_avaliacoes.minhas_bancas` | perfis `docente` e `membro_externo` | Minhas bancas (FR-003 a FR-006) | outro perfil: 403 com `SEM_PERMISSAO_PAGINA` (spec 003) |
| `defesa:criterios` | GET `/defesas/criterios/` | `views_avaliacoes.criterios` | perfis `docente` e `membro_externo` | janela Critérios de avaliação, somente leitura (FR-002) | outro perfil: 403 |
| `defesa:avaliacao` | GET e POST `/defesas/<def_id>/avaliacao/` | `views_avaliacoes.avaliacao` | membro efetivo da sessão | formulário Avaliação; POST com `acao=salvar` ou `acao=enviar` (FR-007 a FR-019) | fora da banca, Suplente não acionado ou sessão Cancelada: "Acesso restrito aos membros avaliadores da banca" (FR-007, FR-036); avaliação já Enviada (até Reabrir): só leitura, POST recusado com MA-13; depois da liberação: só leitura, POST recusado com MA-04 |
| `defesa:reabrir_avaliacao` | POST `/defesas/<def_id>/avaliacao/reabrir/` | `views_avaliacoes.reabrir` | membro efetivo com avaliação Enviada | volta a Rascunho salvo (FR-021) | sessão fora de Em Andamento ou liberada: MA-04 |
| `defesa:assinatura_avaliacao` | GET `/defesas/<def_id>/avaliacao/assinatura/` | `views_avaliacoes.assinatura` | o próprio membro | imagem da cópia da assinatura (`ban_assinatura_path`), `FileResponse` | qualquer outro: 404; arquivo ausente: 404 |
| `defesa:registrar_parecer` | POST `/defesas/<def_id>/parecer/` | `views_avaliacoes.registrar_parecer` | Orientador (Presidente) | grava o parecer de TCC 2 (FR-025) | sem escolha: "Selecione o parecer da banca para continuar"; outro usuário: "Apenas o Orientador (Presidente da banca) pode liberar o resultado da defesa" |
| `defesa:liberar_resultado` | GET e POST `/defesas/<def_id>/liberar/` | `views_avaliacoes.liberar_resultado` | Orientador (Presidente) | GET: confirmação MA-05; POST: liberação (FR-026 a FR-030); nota ou parecer automático mudou: reabre a confirmação com os novos valores (D10); em TCC 2 a nota subiu a 6,0 ou mais: volta à sessão para Registrar parecer | outro usuário: mensagem da US-27 E4; pendências ou sem parecer: volta à sessão com o botão desabilitado (FR-023) |

## Telas existentes que mudam

| Tela | Arquivo | Mudança |
|---|---|---|
| Sessão de defesa (spec 007) | `defesa/sessao.html` | esta feature preenche `{% block avaliacao %}` (`defesa/_bloco_avaliacao.html`: estados, Avaliar, Reabrir minha avaliação) e `{% block resultado %}` (`defesa/_bloco_resultado.html`: nota final, parecer, Registrar parecer, Liberar Resultado), com o que `visao_da_avaliacao` permitir (research A7). A view `views_defesa.sessao` passa esse contexto (IC-05). |
| Histórico da defesa (spec 007) | `defesa/historico.html` | nota final e parecer no evento "Liberação do Resultado" (D15; IC-06) |
| Menu lateral | `cadastro/menu.py` | item "Minhas bancas" (IC-02) |
| Aba Meu TCC (spec 005) | `cadastro/tcc/meu_tcc.html` | inclui `defesa/_resultado_aluno.html`: nota final, parecer e Data Limite da Versão Final em TCC 2 aprovado (FR-033; IC-07) |

## Telas novas

| Template | Conteúdo |
|---|---|
| `defesa/minhas_bancas.html` | tabela (papel, data, horário, aluno, título, status), destaque de pendência, atalhos Documento, Critérios de avaliação, Avaliar e Declaração; vazia: MA-12 |
| `defesa/criterios.html` | 9 critérios por componente, pesos, somas 7,0 / 3,0 / 10,0 e descrições dos conceitos |
| `defesa/avaliacao.html` | cabeçalho (título, aluno, orientador, link do Documento), 9 linhas, nota MA-03 antes da sessão, bloco Assinatura do Membro da Banca, botões Salvar e Enviar avaliação assinada; só leitura depois da liberação |
| `defesa/confirmar_liberacao.html` | confirmação MA-05 com nota final e parecer |
| `defesa/_bloco_avaliacao.html`, `defesa/_bloco_resultado.html`, `defesa/_resultado_aluno.html` | parciais acima |
| `defesa/emails/resultado_secretaria.txt` | e-mail da MA-08 (Q-131 B, 10/11/2026: só a Secretaria) |

O JavaScript da página Avaliação só faz a prévia da imagem, a conferência imediata do tamanho e da
extensão e a habilitação dos campos; nenhuma regra de negócio (a validação que vale é no servidor).
