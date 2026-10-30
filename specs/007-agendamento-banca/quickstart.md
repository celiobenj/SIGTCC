# Quickstart: validar o Agendamento e a Banca

**Feature**: [spec.md](spec.md) | **Rotas**: [contracts/rotas.md](contracts/rotas.md) |
**Serviços**: [contracts/servicos-defesa.md](contracts/servicos-defesa.md)

Roteiro para provar, num ambiente de desenvolvimento, que o agendamento, a banca, o conflito de
horário, a confirmação/reagendamento/cancelamento e a lista com filtros funcionam como na spec.
Não contém código de implementação.

## Pré-requisitos

- Features 001 a 006 aplicadas; `python manage.py migrate` (nenhuma migração nova desta feature).
- `.env` com `DEBUG=True`; servidor com `python manage.py runserver`.
- Um TCC "Apto para Defesa" exige todo o ciclo anterior (Proposta → Status → Entrega do tipo
  Documento para Defesa entregue → Apto para Defesa via US-42, spec 006). Use `popular_demo`
  (depois de implementado, IC-05) ou monte o cenário manualmente pelas telas das specs 004 a 006.

## 1. Contas e TCCs de teste

```bash
python manage.py criar_conta_teste --perfil docente --status ativa --email orientador1@uea.edu.br --senha Tcc@2026a --curso "Engenharia de Computação"
python manage.py criar_conta_teste --perfil docente --status ativa --email avaliador1@uea.edu.br --senha Tcc@2026a --curso "Engenharia de Computação"
python manage.py criar_conta_teste --perfil docente --status ativa --email avaliador2@uea.edu.br --senha Tcc@2026a --curso "Engenharia de Computação"
python manage.py criar_conta_teste --perfil docente --status ativa --email suplente1@uea.edu.br --senha Tcc@2026a --curso "Engenharia de Computação"
```

Monte um TCC "Apto para Defesa" de `orientador1` (via Proposta, entrega do Documento para Defesa e
US-42) antes do roteiro.

## 2. Roteiro manual

| # | Ação | Resultado esperado |
|---|---|---|
| a | Como `orientador1`, "Defesas" → "Agendar defesa" | formulário com TCC pré-filtrado (só "Apto para Defesa", sem sessão ativa), nota de 15/20 minutos de apresentação (US-21, passo 4) |
| b | Preencher Data futura, Horário 14:00, Formato Presencial, Local "Laboratório LSI" | sistema indica a reserva de 1 hora (cenário 3 da US-21) |
| c | Na seção Banca: Orientador (Presidente) já preenchido e bloqueado; selecionar `avaliador1` como 1º Avaliador, `avaliador2` como 2º Avaliador, `suplente1` como Suplente | listas excluem quem já foi escolhido (cenário 2 da US-23) |
| d | Acionar "Agendar" | "Defesa agendada com sucesso"; sessão "Agendada"; `avaliador1`, `avaliador2`, `suplente1` e o aluno notificados (cenário 1 da US-24) |
| e | Agendar uma segunda sessão para `avaliador1` no mesmo intervalo, com outro TCC | sistema rejeita, identifica `avaliador1` como indisponível, nada é gravado (cenário 8 da US-22) |
| f | Como `orientador1`, abrir a sessão criada e acionar "Alterar banca", trocar o 2º Avaliador, informar Justificativa | troca gravada; `avaliador2` e o novo 2º Avaliador notificados (cenário 5 da US-23) |
| g | Acionar "Reagendar", nova data/horário, Justificativa | status "Reagendada"; banca e avaliações mantidas; todos notificados com os novos dados (cenário 5 da US-24) |
| h | Pelo shell, avançar o relógio até o horário da sessão (ou aguardar, em teste manual real) | status muda automaticamente para "Em Andamento" (cenário 7 da US-24) |
| i | Como `orientador1`, com a sessão "Em Andamento", acionar "Acionar suplente" escolhendo o 2º Avaliador como substituído | `suplente1` assume como 2º Avaliador titular; evento no histórico (cenário 7 da US-23) |
| j | Abrir "Histórico da defesa" | linha do tempo com agendamento, alteração de banca, reagendamento, início automático e acionamento de suplente, cada um com responsável e justificativa (cenário 11 da US-40) |
| k | Como a Secretaria do curso, abrir "Defesas" e trocar o filtro de Curso | lista recarrega em até 2 segundos com as sessões do curso escolhido (cenário 5 da US-40; RBN-CAD-14.1) |
| l | Acionar "Cancelar sessão" com Justificativa | status "Cancelada"; Status do TCC permanece "Apto para Defesa" (cenário 6 da US-24) |
| m | Tentar abrir a sessão como um Docente que não é da banca nem Professor da Disciplina | "Você não tem permissão para visualizar esta defesa" (cenário 9 da US-40) |

## 3. Verificação cruzada com a feat-08 (fronteira, sem implementar)

Como a feat-08 ainda não existe, confirme pelo shell que `transicionar_status` rejeita uma
transição fora da tabela:

```python
from sigtcc.apps.defesa import services_defesa
from sigtcc.apps.defesa.models import Defesas
from sigtcc.apps.defesa.choices import StatusSessao

sessao = Defesas.objects.first()
services_defesa.transicionar_status(sessao, StatusSessao.REALIZADA, autor, justificativa=None)
# Se sessao.def_status não for 'Em Andamento', deve levantar ValueError — nenhuma linha de
# histórico é criada.
```

Isso prova a validação de transição (research C2) sem depender da feat-08 existir.
