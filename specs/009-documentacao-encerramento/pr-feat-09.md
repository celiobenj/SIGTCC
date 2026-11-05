# [Feat-09] Documentação e Encerramento (US-28, US-30)

Rascunho do texto do PR. O template completo do PGCS 6.3 será preenchido na revisão do
`revisor-pgcs`; esta versão registra a validação manual (T051).

## Validação manual (T051)

Feita em 2026-11-05 por Claude a pedido de Célio Benjamim, no banco local separado
`sigtcc_validacao` populado pelo `popular_demo` (e-mail no console; nenhum envio real), pelo
navegador (telas com JavaScript) e por script com o `Client` do Django contra o mesmo banco
(PDFs lidos com o pypdf). Roteiro do [quickstart.md](quickstart.md):

| # | Resultado |
|---|---|
| 1 | Sessão Realizada de Eng. Comp. (Coordenador com assinatura): Ata, Folha e Declaração baixam (PDF, nome sem dado pessoal), sem E2. O `popular_demo` não traz sessão pronta para liberar nesse curso; o passo foi ajustado no quickstart |
| 2 | Ata "… Curso II" com as notas 8,5 / 8,0 / 7,5, nota final 8,0, parecer, data 31/10/2026 e o Coordenador; template com 4 assinaturas (3 da banca e a do Coordenador, todas existentes no disco). Folha sem nenhuma nota, "Manaus, 31 de outubro de 2026", 3 assinaturas |
| 3 | Aluno de TCC 2: aba Meu TCC com os links da Ata e da Folha |
| 4 | Suplente não acionado: 403 "Você não tem permissão para acessar os documentos desta defesa" |
| 5 | Sessão de SI (Coordenadora sem assinatura): Registrar parecer › Liberar Resultado; Coordenadora notificada com a MX-03 e link para `/perfil/`; download da Ata pelo Presidente com "Não foi possível gerar a Ata Final…"; Folha disponível |
| 6 | Secretaria de SI: Ata com a MX-08 |
| 7 | Aluna de TCC 1: "A Folha de Aprovação não se aplica ao TCC 1" |
| 8 | Segunda via da declaração dos 3 membros efetivos com o código de validação calculado |
| 9 | Janela Ouvintes: Adicionar cria a linha (JavaScript); Salvar → "Ouvintes salvos com sucesso" |
| 10 | "Ana 2" e "12345abc90" → mensagens da US-30 com os campos destacados; matrícula repetida → "Este aluno já foi registrado como ouvinte nesta defesa"; nada gravado |
| 11 | Secretaria de SI vê ouvintes e ocorrências da sessão Em Andamento, sem botões; Avaliadores não veem |
| 12 | Ocorrências com 2.001 caracteres → "As ocorrências devem ter até 2.000 caracteres" com a caixa destacada; texto curto → "Ocorrências salvas com sucesso"; contador "Caracteres restantes" funciona |
| 13 | Docente da banca que não é o Presidente (2º Avaliador da sessão de SI TCC 1) em Ocorrências: 403 "Você não tem permissão para esta ação". A mesma docente, Professora da Disciplina de SI TCC 2, tem na sessão Realizada dessa turma o botão Ouvintes e não o de Ocorrências |
| 13a | Presidente da sessão de TCC 1 (aluna já no TCC 2) abre a sessão e vê ouvintes e ocorrências |
| 14 | Secretaria de Eng. Comp.: Ouvintes das defesas com 6 linhas e "2 horas" em cada (com 654 px de largura a tabela rola na horizontal, como na Q-141) |
| 15 | Agenda: botão na tela Defesas; PDF agrupado por dia (08/11 e 17/11) para o Orientador e para o Coordenador |
| 16 | Período sem sessões: "Não existem defesas agendadas para o período selecionado" |
| 17 | Visitante no endereço da Ata: login com `next` |

Observações:
- As assinaturas do `popular_demo` são a mesma imagem; o PDF guarda uma cópia só e a desenha em
  cada linha. A contagem por imagem distinta é conferida nos testes automatizados.
- O banco local `sigtcc` não foi tocado.
