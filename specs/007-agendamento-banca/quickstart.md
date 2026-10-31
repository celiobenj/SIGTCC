# Quickstart: validar o Agendamento e a Banca

**Feature**: [spec.md](spec.md) | **Rotas**: [contracts/rotas.md](contracts/rotas.md) |
**Serviços**: [contracts/servicos-defesa.md](contracts/servicos-defesa.md)

Roteiro manual (T056) para provar, num ambiente de desenvolvimento, que o agendamento, a banca, o
conflito de horário, a confirmação/reagendamento/cancelamento e a lista com filtros funcionam
como na spec. O cenário inteiro vem pronto do `popular_demo`: é só entrar com as contas abaixo.
Não contém código de implementação.

## Pré-requisitos

- Features 001 a 007 aplicadas; `python manage.py migrate` (nenhuma migração nova desta feature).
- `.env` com `DEBUG=True`.
- **Atenção: o `popular_demo` apaga todos os dados do banco** (mantém só as cargas das migrações).
  Use um banco local de teste.

```bash
python manage.py popular_demo --senha Demo2026sig --confirmar --local
# digite o nome do banco quando pedir
python manage.py runserver
```

No fim, o comando imprime três tabelas: **Roteiro da spec 007** (cada conta, curso, login e para
que serve), **Quem pode agendar o quê** e **Sessões de defesa**. Todas as contas usam a senha
passada em `--senha`; alunos entram com a matrícula ou o e-mail. As datas são relativas ao dia em
que o comando rodou.

## 1. O cenário pronto

| Conta (nome no demo) | Papel no roteiro |
|---|---|
| Adriana Lopes Viana (Orientadora, Eng. Comp.) | Agenda o TCC Apto de um orientando; outro orientando dela (documento enviado, sem a indicação de Apto) **não** aparece na lista |
| Carlos Eduardo Pinheiro (Orientador, Eng. Comp.) | Agenda o TCC Apto de um orientando; está na banca da sessão Agendada |
| Renata Silveira Cruz (Orientadora, Eng. Comp.) | Agenda o TCC Apto com **pedido de troca de orientador pendente**; preside a sessão Agendada (Alterar banca) |
| Fernando Costa Lima (Professor TCC 1, Eng. Comp.) | Aba Defesas da turma; não agenda TCC de Eng. Comp. |
| Eduardo Farias Brito (Professor TCC 1, Sist. Inf.) | Agenda os 2 TCCs Aptos de Sist. Inf.; reagenda e cancela as sessões de SI |
| Roberto Cunha Matos (Orientador, Sist. Inf.) | Não agenda em Sist. Inf. (E7 pelo endereço direto) |
| Simone Arruda Paes (Orientadora, Sist. Inf.) | Preside a sessão Em Andamento com suplente (Acionar suplente) |
| Beatriz Lemos Aragão (docente extra, Eng. Comp.) | Está na sessão **Agendada daqui a 3 dias às 14:00** (conflito de horário) |
| Henrique Matos Couto (docente extra, Eng. Comp.) | Livre para compor bancas |
| Sandra Pires Lacerda (docente extra, Sist. Inf.) | Suplente da sessão Em Andamento |
| Marcos Vinícius Teixeira (Membro Externo, Ativa) | Suplente da sessão Agendada |
| Helena Duarte Campos (Membro Externo, Expirada) | Aparece entre os avaliadores; ao entrar numa banca, a validade é renovada (US-06) |
| Coordenadores e Secretarias de Eng. Comp. e Sist. Inf. | Filtro de Curso; a Secretaria reagenda e cancela; o Coordenador não abre a janela da sessão |

TCCs Aptos sem sessão (todos com Proposta, Área e Palavra-Chave, orientador aceito, coorientador
do NUCOMP aceito e Documento para Defesa enviado): 2 em Eng. Comp. (quem agenda é o Orientador),
2 em Sist. Inf. (quem agenda é o Professor da Disciplina), 1 em Eng. Comp. com troca de orientador
pendente e o de Lic. Comp., cuja sessão foi cancelada. Sessões existentes: uma em cada status
(Agendada, Reagendada, Em Andamento, Realizada, Cancelada).

## 2. Roteiro manual

| # | Ação | Resultado esperado |
|---|---|---|
| a | Como Adriana, "Defesas" → "Agendar defesa" | lista TCC só com o orientando Apto; o orientando não Apto não aparece; nota de 15/20 minutos (US-21) |
| b | Preencher Data futura, Horário 14:00, Formato Presencial, Local "Laboratório LSI"; trocar o Formato para Remota e voltar | o campo do outro formato some e é limpo; dica da reserva de 1 hora (US-21 cenários 3 e 5) |
| c | Na seção Banca: Orientador (Presidente) já preenchido e bloqueado; escolher Henrique como 1º Avaliador e conferir as listas do 2º Avaliador e do Suplente | o Presidente e o coorientador não aparecem; o já escolhido some das listas seguintes (US-23 cenários 2 e 3) |
| d | Acionar "O Membro Externo não está na lista? Cadastrar" com o foco no Suplente, cadastrar e salvar | volta ao formulário com os campos preenchidos e o novo Membro Externo no Suplente (US-23 cenário 5) |
| e | Escolher Beatriz como 2º Avaliador, a data da sessão Agendada (daqui a 3 dias) às 14:30, e Agendar | recusa, nomeando Beatriz (2º Avaliador), sem gravar nada (US-22) |
| f | Trocar o horário para 16:00 e Agendar | "Defesa agendada com sucesso"; aluno e banca notificados, com o link do Documento para Defesa (US-24) |
| g | Como Renata, agendar o TCC com troca pendente | sessão Agendada; o pedido de troca é cancelado e o aluno e o docente indicado são avisados (US-24 fluxo A) |
| h | Como Eduardo, abrir a aba Defesas da turma SI-TCC1 e agendar um dos TCCs; como Roberto, abrir `/defesas/agendar/?tcc=<id>` de um TCC de SI | Eduardo agenda; Roberto vê "Este TCC não pode ser agendado por você" (US-21 E7) |
| i | Como Renata, abrir a sessão Agendada (de Thaís) → "Alterar banca", trocar o 2º Avaliador, informar Justificativa | troca gravada; avisos a quem entra, a quem sai e ao aluno (US-23 C) |
| j | Como Simone, abrir a sessão Em Andamento → "Acionar suplente", escolher o 2º Avaliador e informar Justificativa | Sandra assume como titular; evento no histórico (US-23 D) |
| k | Como a Secretaria de Eng. Comp., abrir a sessão Reagendada → "Reagendar" para outra data, e depois "Cancelar sessão" de outra | status Reagendada/Cancelada; TCC continua Apto; avisos (US-24 B e C) |
| l | Abrir "Histórico" de uma sessão | linha do tempo com responsável, horários anterior e novo e justificativa; "Sistema" no início automático (US-40) |
| m | Como Coordenador e Secretaria, trocar o filtro de Curso e os atalhos de período e de Status | a lista recarrega com os filtros combinados; datas invertidas e 31/02 mostram as mensagens da US-40 |
| n | Como Fernando (Professor de Eng. Comp.) ou um Coordenador, abrir uma sessão pelo endereço direto | "Você não tem permissão para visualizar esta defesa" (US-40 E5) |

## 3. Início automático

`python manage.py iniciar_sessoes` muda para "Em Andamento" as sessões cujo horário chegou (as
telas da Defesa fazem o mesmo ao abrir). Para ver: agende uma sessão para daqui a 2 minutos,
espere e abra a tela Defesas. O agendamento do comando no servidor é item de configuração (Q-79).

## 4. Verificação automática

```bash
python manage.py test sigtcc.apps.defesa --noinput
```

`test_base_defesa.TestePopularDemo` confere este cenário; cada US tem o seu `test_usXX_*.py`.

## 5. Resultado da validação manual (T056)

Executado por Julia Cohen em 31/10/2026, sobre o cenário do `popular_demo --local`:

- Roteiro manual da seção 2 (passos a a n): sem defeito.
- Conferência visual em 360, 768 e 1280 px: sem problema (inclui o JavaScript da troca de formato
  e da seção Banca, `alternar_formato.js` e `banca.js`).
- Console do navegador: sem erros.
