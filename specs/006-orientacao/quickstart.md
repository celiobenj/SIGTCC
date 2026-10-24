# Quickstart: validação da feature 006 (Orientação, Atas e Publicações)

**Feature**: [spec.md](spec.md) | **Rotas**: [contracts/rotas.md](contracts/rotas.md) | **Modelo**: [data-model.md](data-model.md)

Roteiro para provar que a feature funciona de ponta a ponta, **sempre pela navegação** (SC-005):
nenhum passo digita endereço. Use a base de desenvolvimento local (PostgreSQL 16) e as contas de
teste criadas pelo comando da spec 003. Não repita senhas no chat nem em documentos; elas ficam no
arquivo de exemplo de configuração do projeto.

## 1. Pré-requisitos

```bash
.venv/Scripts/python.exe manage.py migrate
```

```bash
.venv/Scripts/python.exe manage.py test sigtcc.apps.cadastro --keepdb
```

A suíte completa deve passar, inclusive os testes das specs 003 a 005 ajustados pelo IC-11.

Dados mínimos, criados pela interface ou pelas fábricas de `tests/apoio_orientacao.py`:

| Papel | Conta | Situação |
|---|---|---|
| Professor da Disciplina | P | turma de TCC 1 de Sistemas de Informação (sem orientador automático) com 3 alunos: A1 com Proposta, A2 sem Proposta e A3 |
| Docentes | D1, D2, D3 | 'Ativa'; D3 sem nenhum vínculo |
| Coordenador | C | de Sistemas de Informação |
| Secretaria | S | do mesmo curso |
| Turma de TCC 2 de Engenharia de Computação | — | orientador automático, para o passo 9 |

## 2. Pedido e resposta (US-17, US-18; SC-001, SC-002)

1. A1: "Turmas" → turma → "Meu TCC", seção Orientação. Escolha D1 em "Indicar orientador" e acione
   "Enviar pedido". **Esperado**: "Pedido enviado a [D1]. Aguardando resposta", lista bloqueada e
   "Cancelar Pedido". Tempo menor que 1 minuto.
2. D1: o sino (MO-01) abre "Orientações" com o pedido. "Ver proposta" mostra o Resumo; "Fechar"
   volta. Acione "Aceitar". **Esperado**: MO-15; A1 aparece na tela de orientandos com o Papel
   Orientador. A1 recebe MO-02 e P recebe MO-04, que leva ao painel de A1.
3. A2 (sem Proposta) indica D2; D2 recusa. **Esperado**: "Pedido recusado"; A2 vê a lista livre de
   novo e recebe MO-03; P **não** é avisado (Q9).
4. D3, sem vínculos: o menu tem "Orientações", e a tela abre com as 3 seções vazias (MO-24, Q11).
5. A1 troca para D2 ("Trocar de orientador"). D2 aciona "Ver proposta" e vê o Resumo (IC-05) e
   depois "Aceitar". **Esperado**: D1 recebe MO-05 e perde A1 da tela de orientandos e o acesso às
   atas (Q10). A seção Orientação de A1 mostra D2 e o histórico (FR-049).
6. D1 abre o link antigo do pedido de A1: **Esperado** "Aceito" com data e hora, sem botões.

## 3. Coorientação (US-45, US-36)

7. A1: "Registrar coorientador" → Docente do NUCOMP → D3. **Esperado**: "Aguardando Aceite"; D2
   notificado (MO-08). No e-mail de D3 (MO-07), "Aceitar" **só abre** a tela com o convite
   destacado (Q14); a resposta é dada na tela.
8. D3 aceita: "Convite aceito"; o trabalho aparece com o Papel Coorientador, só com "Atas" e
   "Registrar ata". A1 registra um "Externo ao NUCOMP" com um e-mail já cadastrado em outro
   trabalho: **Esperado** MO-25, com Nome e Instituição mantidos (Q13).
9. Na turma de TCC 2 de Engenharia de Computação, a seção Orientação mostra o professor como
   Orientador, sem listas.

## 4. Atas (US-19)

10. A1: seção "Atas de orientação" → "Registrar ata" com data de ontem. **Esperado**: "Ata
    registrada"; "Cancelar" e "Salvar" voltam à seção. Data de amanhã → "A Data do Encontro não pode
    ser futura".
11. D2: "Orientações" → linha de A1 → "Atas" → "Comentar" com 1.001 caracteres → MO-19; com 20
    caracteres, o comentário aparece com autor, data e hora. "Voltar" leva à tela de orientandos.
12. P: turma → bloco de A1 → painel → Atas: só leitura, sem "Registrar ata", "Editar" nem
    "Comentar"; "Voltar" leva ao painel.

## 5. Painel do aluno (US-41) e aba Alunos

13. P: turma → aba "Alunos": 3 blocos, só leitura, com "Sem orientador" e "Sem Proposta" onde
    couber. O bloco abre o painel com as 7 seções. "Encerrar participação" → "Cancelar" volta ao
    **painel** (IC-03). "Fechar" volta à aba.
14. S (Secretaria) abre a turma de TCC 2 com orientador automático: blocos sem painel, com
    "Transferir aluno" (Q4). *Teste de permissão, não de navegação*: abrir o painel pelo endereço
    dá 403 (M-02).
15. Endereço antigo `alunos/<id>/` (link guardado da spec 003; único passo que usa endereço, para
    provar o redirecionamento): leva ao painel (Q12).

## 6. Apto para Defesa e Correções Conferidas (US-42; FR-016)

16. Sem a entrega "Documento para Defesa" na turma: o botão aparece indisponível com o texto da US-42.
    Com a entrega enviada, Área e Palavra-Chave: "Apto para Defesa" → "Confirmar" → "TCC indicado
    como apto para defesa", e a etiqueta substitui o botão. O histórico (link da linha) mostra o
    gatilho; "Fechar" volta.
17. TCC 2 de Sistemas de Informação com "Aprovado com Correções" (fábrica): o botão só aparece depois
    do envio da Versão Final. Confirmar mostra a etiqueta "Correções conferidas em …". P devolve para
    ajuste pelo painel: a conferência é apagada (Q2) e a tela volta ao painel.

## 7. Publicação e aproveitamento (US-46, US-20)

18. A1 (Artigo Científico): seção "Publicação do artigo" → Link sem `https://` → mensagem da US. Com
    Qualis B1 e Status Aceito → "Publicação salva", etiqueta "Em Análise".
19. C: menu "Gestão" → "Aproveitamento de artigos" (filtro no curso de C) → "Homologar" →
    "Aproveitamento homologado". Filtro em outro curso: sem botões.
20. A1 muda o Qualis: volta a "Em Análise". C homologa de novo. Com a liberação simulada pelo
    gatilho (fábrica), "Recusar" fica indisponível no artigo Homologado (US-20 E3). A1 muda o
    Qualis outra vez: volta a "Em Análise", e C vê "Homologar" e "Recusar" (Q16).

## 8. Cancelamentos e TCC 2 (FR-050, FR-051)

21. Pedido pendente de A3 a D1; P encerra a participação de A3. D1 abre o link: MO-12 (texto de
    pedido).
22. TCC 1 aprovado com convite pendente, matriculado no TCC 2 (fábrica): o convite vira 'Cancelado'
    e o link mostra MO-18. As atas do TCC 1 aparecem abaixo na lista do TCC 2, e a tela do
    Coordenador mostra o artigo uma só vez.
23. Pedido pendente de A2 (TCC "Sem Proposta") a D1; P arquiva a turma (depois de resolver os
    demais TCCs). **Esperado**: D1 recebe a MO-26 no sino, que leva à tela Orientações; o pedido
    sumiu de "Pedidos de orientação" e o link antigo mostra o texto de link da MO-26 (Q17).

## 9. Resultado esperado

- Todos os passos chegam às telas pela navegação, exceto o passo 15, que é de propósito, e a
  conferência de permissão do passo 14.
- Mensagens iguais às US ou às MO da spec (SC-003).
- `lint.bat` sem erros e suíte completa passando antes do PR.
