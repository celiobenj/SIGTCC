<!--
Relatório de Impacto da Sincronização (Sync Impact Report)
- Emenda 2026-10-25: 1.0.1 → 1.0.2 (PATCH). O lint.bat foi substituído pelo pre-commit (PGCS 3.3):
  princípio V e passo 6 do fluxo citam `pre-commit run --all-files`; sem efeito semântico nas
  regras de qualidade (mesmas ferramentas e opções).
- Emenda 2026-10-24: 1.0.0 → 1.0.1 (PATCH). Referência às Histórias de Usuário trocada de v3.2 para
  v3.3 (seção II e "Restrições de Stack e Escopo"), a versão que está em docs/fonte/; sem efeito
  semântico (índice Q-62). Aprovação do responsável pela configuração e revisão por pares no PR.
- Versão: (modelo sem versão) → 1.0.0
- Motivo: primeira adoção da constituição (ratificação inicial).
- Princípios definidos (template tinha 5 espaços; a equipe adotou 9):
  I. Especificação Primeiro
  II. Rastreabilidade Obrigatória
  III. Modelo de Dados Oficial
  IV. Arquitetura Monólito Modular Django
  V. Qualidade de Código
  VI. Testes de Aceitação
  VII. Segurança e LGPD
  VIII. Gerência de Configuração
  IX. Governança de Escopo e Configuração
- Seções adicionadas: "Restrições de Stack e Escopo", "Fluxo de Desenvolvimento e Portões de
  Qualidade", "Governança".
- Seções removidas: nenhuma.
- Templates dependentes: não alterados por este comando (leem a constituição em tempo de execução).
- TODOs pendentes: nenhum.
- Fonte: docs/fonte/constituicao_base.md.
Este comentário é material temporário de revisão e deve ser removido antes do commit.
-->

# Constituição do SIGTCC

Sistema de Gestão de TCC do NUCOMP-UEA. Disciplina Engenharia de Software (ESTCMP025), 2026/2.
Product Owner: Profa. Diana Maria Camara de Carvalho. Equipe ++C.

## Princípios Fundamentais

### I. Especificação Primeiro

- Nenhuma funcionalidade DEVE ser implementada sem `spec.md`, `plan.md` e `tasks.md` aprovados
  pela pessoa responsável pela feature.
- Toda mudança de comportamento, inclusive após o merge, DEVE começar pela atualização da spec.

**Justificativa:** a especificação é a fonte da verdade do Spec-Driven Development; código sem
spec aprovada não tem critério objetivo de aceite.

### II. Rastreabilidade Obrigatória

- Toda spec, tarefa, teste e trecho de código (classe, função, template) DEVE indicar as US e os
  RBN que atende, no formato `[US-XX][RBN-CAD-YY.Z]`.
- As fontes de requisitos são a Matriz de Requisitos (versão de 17/10) e as Histórias de Usuário
  v3.3.
- Em divergência entre documentos, prevalece a Matriz. Se a divergência mudar o comportamento, a
  decisão DEVE ser tomada após consulta à equipe e registrada na seção "Clarifications" da spec;
  nenhuma pessoa ou agente escolhe sozinho.

**Justificativa:** permite verificar, em qualquer artefato, qual requisito o justifica e
comprovar a cobertura na avaliação da disciplina.

### III. Modelo de Dados Oficial

- Os models Django DEVEM seguir o Modelo Lógico e Dicionário de Dados de 18/10 (36 tabelas):
  nomes, tipos, tamanhos, nulidade e chaves. Quando o nome Django diferir, usar `db_table` e
  `db_column`.
- Nenhuma tabela ou campo DEVE ser criado fora do modelo lógico sem antes atualizar o documento.
- O módulo de Salas está fora do escopo desde 17/10; o local da defesa presencial é texto
  (`Defesas_Presenciais.dep_local`).

**Justificativa:** o modelo lógico e o DER V2 foram aprovados pela equipe; divergências no banco
quebram a rastreabilidade e a integração entre épicos.
(Fontes: Modelo Lógico, DER V2.)

### IV. Arquitetura Monólito Modular Django

- Monólito modular Django com renderização no servidor (MVT ≡ MVC), Python 3.12 e PostgreSQL.
- Apps: `sigtcc/apps/cadastro` (Épico 1), `sigtcc/apps/defesa` (Épico 2),
  `sigtcc/apps/relatorios` (Épico 3); templates em `sigtcc/templates/<app>/`; arquivos estáticos
  em `sigtcc/static/`.
- Regras de negócio DEVEM ficar no Model e em `services.py`; views apenas orquestram; templates
  NÃO DEVEM conter regra de negócio.

**Justificativa:** estrutura única e previsível para cinco pessoas trabalhando em paralelo,
alinhada ao PGCS. (Fonte: PGCS 2.1 a 2.3.)

### V. Qualidade de Código

- O código DEVE seguir PEP 8, verificado com `isort`, `black --line-length 100` e
  `flake8 --max-line-length 100`, executados pelo pre-commit (`pre-commit run --all-files`).
- Todo código DEVE ter comentários em português do Brasil.

**Justificativa:** padrão uniforme reduz conflitos de merge e facilita a revisão por pares.
(Fonte: PGCS 3.2 e 3.3.)

### VI. Testes de Aceitação

- Cada cenário Dado/Quando/Então das US DEVE ter pelo menos um teste automatizado Django.
- Mensagens exibidas ao usuário DEVEM ser verificadas nos testes com o texto exato da US.

**Justificativa:** os cenários de aceite são o contrato com a Product Owner; testá-los
automaticamente comprova a entrega. (Fontes: template das US; Cronograma 4.3 e 5.1.)

### VII. Segurança e LGPD

- Segredos DEVEM ficar somente no `.env`, que nunca é versionado.
- O diretório `media/` (assinaturas e PDFs) DEVE ficar fora do Git.
- Senhas DEVEM ser armazenadas com hash.
- Cada perfil DEVE acessar somente as funções do seu papel.

**Justificativa:** o sistema trata dados pessoais de alunos e professores e documentos
assinados. (Fontes: PGCS 3.4; RNFs ISO/IEC 25010 da Matriz.)

### VIII. Gerência de Configuração

- GitFlow com as branches `main`, `develop`, `feature/feat-XX-nome`, `release/vX.Y.Z`,
  `bugfix/epico-X-nome` e `hotfix/vX.Y.Z`.
- Commits DEVEM seguir Conventional Commits.
- Todo PR vai para `develop`, com o template do PGCS preenchido e revisão por outra pessoa da
  equipe; merge com `--no-ff`.
- Migrações DEVEM estar no mesmo PR da alteração do model.
- Baselines: v0.2.0 (TP2), v0.3.0 (TP3) e v1.0.0 (TP4).

**Justificativa:** histórico limpo e baselines auditáveis para cada entrega da disciplina.
(Fonte: PGCS 4 a 7.)

### IX. Governança de Escopo e Configuração

- Mudanças de escopo e de requisitos DEVEM ser aprovadas pela Product Owner (Profa. Diana).
- Mudanças de configuração, de estrutura do projeto ou desta constituição DEVEM passar pelo
  responsável pela configuração (Célio Benjamim) por meio de PR revisado.
- Esta constituição é versionada com SemVer.

**Justificativa:** separa quem decide o quê (produto) de quem decide como o repositório é
mantido (configuração). (Fonte: PGCS 8.1.)

## Restrições de Stack e Escopo

- Stack: Python 3.12, Django e PostgreSQL; ambiente de desenvolvimento Windows com `venv`.
- Fora do escopo: módulo de Salas (removido em 17/10).
- Documentos de referência ficam em `docs/fonte/`: Histórias de Usuário v3.3, Modelo Lógico e
  Dicionário de Dados (18/10), DER V2, PGCS e Cronograma (18/10).
- `.env` e `media/` NÃO DEVEM ser commitados.

## Fluxo de Desenvolvimento e Portões de Qualidade

1. `/speckit-specify` → `/speckit-clarify`: spec a partir das US, com divergências resolvidas e
   registradas em "Clarifications".
2. `/speckit-plan`: o plano DEVE passar pela verificação desta constituição (modelo lógico,
   arquitetura MVT, estrutura de pastas).
3. `/speckit-tasks` → `/speckit-analyze`: tarefas pequenas e ordenadas, com consistência
   spec × plan × tasks confirmada antes de codar.
4. Aprovação da pessoa responsável pela feature antes de `/speckit-implement`.
5. `/speckit-implement` e `/speckit-converge`: implementação com testes de aceite.
6. Antes do PR: `pre-commit run --all-files` sem erros, testes passando, migrações incluídas, rastreabilidade
   US/RBN presente e checklist do PGCS 6.3 preenchido.

## Governança

- Esta constituição prevalece sobre outras práticas do projeto. O `CLAUDE.md` e os agentes em
  `.claude/agents/` DEVEM estar alinhados a ela.
- Emendas: propostas por PR, revisadas por outra pessoa da equipe e
  aprovadas pelo responsável pela configuração (Célio Benjamim); mudanças que afetem escopo ou
  requisitos também exigem aprovação da Product Owner.
- Versionamento (SemVer):
  - MAJOR: remoção ou redefinição incompatível de princípio ou regra de governança.
  - MINOR: novo princípio ou seção, ou ampliação material de orientação.
  - PATCH: esclarecimentos, redação e correções sem efeito semântico.
- Conformidade: toda revisão de PR e a etapa `/speckit-analyze` DEVEM verificar a aderência a
  estes princípios; qualquer exceção DEVE ser justificada por escrito no `plan.md` ou no PR.

**Versão**: 1.0.2 | **Ratificada**: 2026-10-19 | **Última emenda**: 2026-10-25
