# Base para a constituição do SIGTCC

Texto para colar no comando `/speckit-constitution`. Cada princípio vem de um documento já
aprovado pela equipe (indicado entre parênteses). Ajustem antes de rodar, se a equipe decidir algo
diferente.

---

Crie a constituição do projeto SIGTCC (Sistema de Gestão de TCC do NUCOMP-UEA) com estes princípios,
em português do Brasil:

1. **Especificação primeiro.** Nenhuma funcionalidade é implementada sem spec.md, plan.md e
   tasks.md aprovados pela pessoa responsável. Mudança de comportamento começa pela spec.
2. **Rastreabilidade obrigatória.** Toda spec, tarefa, teste e trecho de código indica as US e os
   RBN que atende, no formato [US-XX][RBN-CAD-YY.Z]. Fontes: Matriz de Requisitos (17/10) e
   Histórias de Usuário v3.2. Em divergência, prevalece a Matriz; se mudar comportamento, a decisão
   é registrada na spec após consulta à equipe.
3. **Modelo de dados oficial.** Models Django seguem o Modelo Lógico e Dicionário de Dados de 18/10
   (36 tabelas): nomes, tipos, tamanhos, nulidade e chaves. Nenhuma tabela ou campo é criado fora
   dele sem atualizar o documento. Salas estão fora do escopo desde 17/10. (Modelo Lógico, DER V2)
4. **Arquitetura.** Monólito modular Django com renderização no servidor (MVT ≡ MVC), Python 3.12
   e PostgreSQL. Apps: sigtcc/apps/cadastro (Épico 1), defesa (Épico 2), relatorios (Épico 3);
   templates em sigtcc/templates/<app>/; static em sigtcc/static/. Regras de negócio no Model e em
   services.py; views só orquestram; templates sem regra. (PGCS 2.1 a 2.3)
5. **Qualidade de código.** PEP 8 com isort, black (linha de 100) e flake8 (100), via lint.bat.
   Todo código tem comentários em português. (PGCS 3.2 e 3.3)
6. **Testes de aceitação.** Cada cenário Dado/Quando/Então das US tem teste automatizado; mensagens
   ao usuário são verificadas com o texto exato da US. (Template das US; cronograma 4.3 e 5.1)
7. **Segurança e LGPD.** Segredos só no .env; media/ (assinaturas e PDFs) fora do Git; senhas com
   hash; cada perfil acessa só as funções do seu papel. (PGCS 3.4; RNFs ISO/IEC 25010 da Matriz)
8. **Gerência de configuração.** GitFlow: main, develop, feature/feat-XX-nome, release/vX.Y.Z,
   bugfix/epico-X-nome, hotfix/vX.Y.Z. Conventional Commits. PR para develop com template do PGCS e
   revisão por pares; merge --no-ff. Migrações sempre no mesmo PR do model. Baselines v0.2.0 (TP2),
   v0.3.0 (TP3), v1.0.0 (TP4). (PGCS 4 a 7)
9. **Governança.** Mudanças de escopo e de requisitos são aprovadas pela Product Owner (Profa.
   Diana); mudanças de configuração, estrutura ou desta constituição passam pelo responsável pela
   configuração (Célio Benjamim) por PR revisado. A constituição é versionada com SemVer. (PGCS 8.1)
