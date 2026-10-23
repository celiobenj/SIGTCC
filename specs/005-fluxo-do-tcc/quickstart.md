# Quickstart: validar o Fluxo do TCC e Entregas

**Feature**: [spec.md](spec.md) | **Rotas**: [contracts/rotas.md](contracts/rotas.md) |
**Serviços**: [contracts/servicos-compartilhados.md](contracts/servicos-compartilhados.md)

Roteiro para provar, num ambiente de desenvolvimento, que a Proposta, o Status do TCC, as
entregas, a Versão Final e a homologação funcionam como na spec. Não contém código de
implementação.

## Pré-requisitos

- Features 001, 003 e 004 aplicadas; `python manage.py migrate` (nenhuma migração nova desta
  feature).
- `.env` com `DEBUG=True`; servidor com `python manage.py runserver`.
- `python manage.py criar_conta_teste` **não cria o registro de TCC**: ele só cria a conta e, com
  `--turma`, o vínculo `Alunos_Turmas` direto no banco (sem passar por `services_turmas.
  matricular`). Para ter o TCC "Sem Proposta" (gatilho "Vínculo à turma"), matricule o aluno pela
  tela "Matricular alunos" (spec 004), não pelo comando.

## 1. Contas e turma de teste

```bash
python manage.py criar_conta_teste --perfil docente --status ativa --email prof@uea.edu.br --senha Tcc@2026a --curso "Engenharia de Computação"
python manage.py criar_conta_teste --perfil aluno --status ativa --matricula 2026000321 --email aluno1@uea.edu.br --senha Tcc@2026a
python manage.py criar_conta_teste --perfil aluno --status ativa --matricula 2026000322 --email aluno2@uea.edu.br --senha Tcc@2026a
```

Como `prof`, em "Turmas" → "Nova turma": TCC 1, Engenharia de Computação, Identificador
`ECP07_T01` (base do roteiro da spec 004). Depois, "Matricular alunos" → "Matrícula individual"
para `2026000321` e `2026000322` — cada um nasce com o TCC "Sem Proposta" (cenário 1 da US-14).

## 2. Roteiro manual

| # | Ação | Resultado esperado |
|---|---|---|
| a | Como `aluno1`, no menu lateral, abrir "Turmas" (item do Aluno, FR-031) → `ECP07_T01` | a turma abre na aba "Meu TCC", com as abas "Meu TCC" e "Atividades"; só aparecem as turmas de `aluno1`; etiqueta "Sem Proposta"; campos Título, Subtítulo, Resumo, Modalidade, Link e botão "Salvar Proposta" (US-13, passo 2) |
| b | Preencher Título, Resumo e Modalidade "Monografia" e salvar | "Proposta salva"; etiqueta muda para "Em Andamento"; campos Área de Interesse e Palavras-Chave aparecem (cenário 1 da US-13) |
| c | Selecionar Área "Segurança da Informação", informar as palavras "LGPD", "LGPD" (repetida) e salvar; depois corrigir para "LGPD" e "criptografia" | 1ª tentativa: "Palavra-chave repetida." (MF-03, sem salvar); 2ª tentativa: "Alterações salvas" (cenário 2 da US-13; Clarifications) |
| d | Abrir o link "Histórico do Status do TCC" na aba Meu TCC | lista com 1 linha (Sem Proposta → Em Andamento, gatilho "Proposta salva", `aluno1` como responsável) e a trilha com "Em Andamento" destacado (cenários 2 e 11 da US-14) |
| e | Como `prof`, no menu lateral, abrir "Turmas" → `ECP07_T01` (aba "Alunos") → aba "Atividades" → "Cadastrar atividade": Título "Entrega do Documento", Tipo "Documento para Defesa", Data Limite para hoje + 5 dias | "Entrega cadastrada"; `aluno1` e `aluno2` notificados; cada um com status "Aguardando Envio" (cenário 1 da US-43) |
| f | Tentar cadastrar outra entrega do tipo "Documento para Defesa" na mesma turma | "A turma já tem uma entrega deste tipo" (cenário 9 da US-43) |
| g | Como `aluno1`, abrir "Turmas" → `ECP07_T01` → aba "Atividades" → a entrega cadastrada, informar um link `https://drive.google.com/...` e enviar | "Entrega enviada"; status "Entregue"; `prof` notificado (cenário 1 da US-15) |
| h | Pelo shell (ou alterando a Data Limite para ontem antes do passo e), repetir o envio com `aluno2` depois do prazo | envio aceito com status "Entregue com Atraso" (cenário 3 da US-15) |
| i | Como `prof`, abrir a entrega cadastrada em "Atividades" | tabela com `aluno1` "Entregue" e o link, `aluno2` "Entregue com Atraso" e o link (cenário 1 da US-16) |
| j | Pelo shell, levar o TCC de `aluno1` para uma turma de TCC 2 com `tcc_status = 'Aprovado'` e cadastrar a entrega "Versão Final" com Data Limite futura | aba Meu TCC de `aluno1` mostra a seção "Versão final" com "Aguardando Envio" e campo Link (pré-condição da US-29) |
| k | Como `aluno1`, enviar o link da Versão Final | "Versão Final enviada"; status "Entregue"; `prof` notificado (cenário 1 da US-29) |
| l | Como `prof`, abrir a tela de homologação de `aluno1` e acionar "Homologar" | "Versão Final homologada"; status de envio "Homologada"; Status do TCC "Concluído" (gatilho "Homologação da Versão Final"); Secretaria notificada (cenário 1 da US-44) |
| m | Repetir j e k com `aluno2` (TCC 2, parecer "Aprovado com Correções"); como `prof`, acionar "Devolver para Ajuste" com a Mensagem "Falta a ficha catalográfica" | status "Devolvida para Ajuste"; `aluno2` notificado; "Versão Final devolvida para ajuste" (MF-02) na tela do Professor (cenário 3 da US-44) |
| n | Tentar abrir a aba "Meu TCC" sem estar autenticado | tela de login (US-11), com retorno à aba Meu TCC depois do login (cenário 7 da US-13 e cenário 17 da US-14) |
| o | Como um Docente que não é `prof` nem orientador, tentar abrir o Histórico de `aluno1` | sem acesso ao histórico (cenário 19 da US-14; Clarifications — Secretaria e Coorientador também sem acesso) |

## 3. Verificação cruzada com a spec 006 (fronteira, sem implementar)

Como não existe ainda a "tela de orientandos" nem a "tela do aluno" completa (US-41), confirme
pelo shell que `services_turmas.atualizar_status_tcc` rejeita um gatilho fora da lista:

```python
from sigtcc.apps.cadastro import services_turmas
from sigtcc.apps.cadastro.models import TCCs

tcc = TCCs.objects.first()
services_turmas.atualizar_status_tcc(tcc, tcc.tcc_tur, autor, "Status Inventado", "gatilho qualquer")
# Deve levantar ValueError — nenhuma linha de histórico é criada.
```

Isso prova a User Story 2, cenário 11 (FR-012), sem depender da spec 006 existir.
