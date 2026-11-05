# Quickstart: validar a Documentação e Encerramento

**Feature**: [spec.md](spec.md) | **Plano**: [plan.md](plan.md)

## Pré-requisitos

- Ambiente local com `.venv`, PostgreSQL e `.env` (PGCS 3.1); sem dependência nova (`xhtml2pdf` e
  `pypdf` já fixados no `requirements.txt` desde a spec 008).
- Banco separado para a validação manual (o `popular_demo` apaga os dados):

```powershell
$env:DB_NAME = "sigtcc_validacao"
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py popular_demo --senha Tcc@2026a --confirmar --local
```

O cenário traz uma sessão Realizada com ouvintes e ocorrências, um curso cujo Coordenador tem
assinatura e outro sem (E2), e sessões Agendadas e Reagendadas no período (research B14).

## 1. Roteiro manual

| # | Perfil | Ação | Resultado esperado |
|---|---|---|---|
| 1 | Orientador (curso com assinatura do Coordenador) | Liberar o resultado de um TCC 2 Aprovado | Sem alerta da E2; e-mail com a declaração em PDF a cada membro efetivo (console de e-mail) |
| 2 | Membro efetivo | Sessão › **Ata Final (PDF)** e **Folha de Aprovação (PDF)** | Ata com notas, 3 assinaturas e Coordenador; Folha sem nenhuma nota |
| 3 | Aluno | Aba **Meu TCC** › documentos | Botões da sessão Realizada, com a data da defesa |
| 4 | Suplente não acionado | Endereço da Ata | "Você não tem permissão para acessar os documentos desta defesa" |
| 5 | Orientador (curso sem assinatura do Coordenador) | Liberar o resultado | Alerta da E2 na tela; Coordenador notificado; Ata recusada no download; Folha disponível |
| 6 | Secretaria do mesmo curso | Ata dessa sessão | MX-08 |
| 7 | Aluno de TCC 1 | Endereço da Folha | "A Folha de Aprovação não se aplica ao TCC 1" |
| 8 | Membro efetivo | **Minhas bancas** › **Declaração** | PDF com o mesmo código do e-mail |
| 9 | Orientador (sessão Em Andamento) | **Ouvintes** › 2 alunos › **Salvar** | "Ouvintes salvos com sucesso" |
| 10 | Orientador | Matrícula 12345abc90; nome "Ana 2"; matrícula repetida | Mensagens da US-30 (E2, E3, E4) com o campo destacado, nada gravado |
| 11 | Secretaria | Abrir a mesma sessão | Lista de ouvintes só leitura |
| 12 | Orientador | **Ocorrências** › 2.001 caracteres; depois um texto curto | MX-01 com a caixa destacada; depois "Ocorrências salvas com sucesso" |
| 13 | Professor da Disciplina | Endereço de Ocorrências | "Você não tem permissão para esta ação" |
| 13a | Presidente da banca de TCC 1 (aluno já matriculado no TCC 2) | Abrir a sessão Realizada do TCC 1 | Ocorrências e ouvintes visíveis (B-03) |
| 14 | Secretaria | Menu **Ouvintes das defesas**, período e curso | Ouvintes das sessões Realizadas com "2 horas" |
| 15 | Orientador e Coordenador | Tela Defesas › **Agenda de defesas (PDF)** | Orientador: todas as Agendadas/Reagendadas do período; Coordenador: só o curso do filtro |
| 16 | Qualquer um da agenda | Período sem sessões | "Não existem defesas agendadas para o período selecionado" |
| 17 | Visitante | Endereço da Ata | Login e, depois, o download |

## 2. Verificação automática

```powershell
.venv\Scripts\python.exe manage.py test sigtcc.apps.defesa
.venv\Scripts\python.exe manage.py test
pre-commit run --all-files
```

Esperado: todos os testes passam, inclusive os ajustados das specs 005 e 008 (aba Meu TCC,
Minhas bancas e liberação), e o pre-commit não acusa nada.
