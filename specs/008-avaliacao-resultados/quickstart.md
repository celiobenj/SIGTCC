# Quickstart: validar a Avaliação e Resultados

**Feature**: [spec.md](spec.md) | **Plano**: [plan.md](plan.md)

## Pré-requisitos

- Ambiente local com `.venv`, PostgreSQL e `.env` (PGCS 3.1).
- Dependências atualizadas (esta feature acrescenta o `xhtml2pdf`):

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe manage.py migrate
```

- Cenário de demonstração (spec 007 + avaliações desta feature, research A12):

```powershell
.venv\Scripts\python.exe manage.py popular_demo --senha Tcc@2026a --confirmar --local
```

## 1. Roteiro manual

| # | Perfil | Ação | Resultado esperado |
|---|---|---|---|
| 1 | Docente da banca | Menu **Minhas bancas** | Sessões sem as Canceladas, pendentes em destaque, atalhos Documento, Critérios de avaliação e Avaliar |
| 2 | Docente da banca | **Critérios de avaliação** | 9 critérios, pesos, somas 7,0 / 3,0 / 10,0, descrições dos conceitos |
| 3 | Membro da sessão Agendada | **Avaliar**, Parte Escrita, **Salvar** | MA-03 visível; Parte Oral e assinatura bloqueadas; "Rascunho salvo" |
| 4 | Membro da sessão Em Andamento | Competente com 8,5 | Mensagem da US-25 E2 |
| 5 | Membro da sessão Em Andamento | 9 critérios, assinatura do perfil, **Enviar avaliação assinada** | "Enviada"; nota individual calculada |
| 6 | Professor da Disciplina e Aluno | Abrir a mesma sessão | Nada do bloco de avaliação (D7) |
| 7 | Orientador (sessão pronta para liberar, TCC 2) | **Liberar Resultado** sem parecer | Botão desabilitado (D1) |
| 8 | Orientador | **Registrar parecer** › Aprovado com Correções › **Liberar Resultado** › confirmar | Sessão "Realizada"; Status do TCC "Aprovado com Correções"; avisos ao Aluno, à banca e à Secretaria |
| 9 | Aluno | Aba **Meu TCC** | Nota final, parecer e Data Limite da Versão Final |
| 10 | Membro | **Reabrir minha avaliação** depois da liberação | Bloqueado (MA-04) |
| 11 | Quem abre a sessão | **Histórico** | Evento "Liberação do Resultado" com nota final e parecer |
| 12 | Membro que enviou (sessão Em Andamento, sem liberação) | **Reabrir minha avaliação** | "Rascunho salvo", sem assinatura; parecer escolhido limpo; Liberar Resultado desabilitado |
| 13 | Orientador com 2 de 3 envios | Abrir a sessão | Nota final oculta; pendente em destaque; Liberar Resultado desabilitado |
| 14 | Orientador | **Acionar suplente** no lugar do 2º Avaliador | Suplente vê **Avaliar** com as duas partes; avaliação do ausente descartada |
| 15 | Quem pode reagendar | **Reagendar** sessão Em Andamento com envios | Envios voltam a "Rascunho salvo"; notas mantidas |
| 16 | Membro | Anexar PNG de 3 MB e depois um .pdf | Mensagens da US-26 E2 e E3 |

Em produção (Render), as avaliações de demonstração não mostram a imagem da assinatura: o
`popular_demo` roda na estação e grava a cópia no `media/` local (research A12; risco aceito).

## 2. Verificação automática

```powershell
.venv\Scripts\python.exe manage.py test sigtcc.apps.defesa
.venv\Scripts\python.exe manage.py test
pre-commit run --all-files
```

Esperado: todos os testes passam, inclusive os da spec 007 ajustados (troca de papel na banca e
reagendamento), e o pre-commit não acusa nada.
