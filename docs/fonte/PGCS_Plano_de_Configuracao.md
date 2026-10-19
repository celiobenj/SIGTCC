**PLANO DE GERÊNCIA DE CONFIGURAÇÃO DO SOFTWARE (PGCS)**

| **Nome do Projeto:** | Sistema de Gestão de TCC do NUCOMP-UEA (SIGTCC)   |
|----------------------|---------------------------------------------------|
| **Instituição:**     | UEA – Universidade do Estado do Amazonas (NUCOMP) |
| **Responsável:**     | Célio Benjamim                                    |
| **Data:**            | 21/10/2026                                        |

# Controle do Documento e Histórico de Revisões

| **Versão** | **Data**   | **Descrição da Alteração**                                                                                                                                       | **Autor / Responsável** |
|------------|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------|
| 1          | 21/10/2026 | Estruturação inicial do PGCS para o marco TP2: arquitetura MVT, organização de diretórios, GitFlow, padronização de commits, modelo de Pull Request e baselines. | Célio Benjamim          |

# 1. Introdução e Gerência de Configuração

Este Plano de Gerência de Configuração de Software (PGCS) formaliza as
políticas de controle de versão, estratégias de ramificação, regras de
escrita de commits, ciclo de vida de Pull Requests, arquitetura de
pastas, auditorias técnicas e linhas de base (baselines) do Sistema de
Gestão de TCC do NUCOMP-UEA (SIGTCC).

O SIGTCC centraliza o fluxo dos Trabalhos de Conclusão de Curso da
Escola Superior de Tecnologia da UEA em três módulos integrados:
Cadastro e Manutenção, Gestão da Defesa e Relatórios e Informações
Gerenciais. O sistema é concebido como uma aplicação web responsiva em
Python 3.12 e Django, utilizando banco relacional PostgreSQL.

A condução da gerência de configuração observa os preceitos normativos
da IEEE Std 828-2012 (Standard for Configuration Management in Systems
and Software Engineering), os processos de ciclo de vida da ISO/IEC/IEEE
12207:2017 e as características de qualidade de software da ISO/IEC
25010.

## 1.1 Escopo da Configuração

Este plano rege os artefatos técnicos versionados no repositório oficial
do projeto:

- Código-fonte Python, rotas, regras de negócio e camada de acesso a
  > dados;

- Interfaces web, gabaritos de apresentação e folhas de estilo;

- Scripts de banco de dados e migrações estruturais do ORM;

- Rotinas locais de automação para ambiente Windows (lint.bat);

- Especificação formal de dependências do ambiente (requirements.txt);

- Histórico cumulativo de entregas (CHANGELOG.md).

**Fronteira com a Gestão Documental:** Os artefatos de planejamento
gerencial (Termo de Abertura, Matriz de Requisitos, EAP e Plano de
Integração) permanecem armazenados e mantidos no Google Drive
institucional e no quadro Trello do projeto, preservando a
rastreabilidade externa sem poluir a árvore de código do repositório
Git.

## 1.2 Itens de Configuração (Configuration Items - CIs)

| **Identificador** | **Item de Configuração (CI)**         | **Descrição do Componente**                                                 | **Localização no Repositório**     |
|-------------------|---------------------------------------|-----------------------------------------------------------------------------|------------------------------------|
| CI-01             | Aplicação Backend e Lógica de Negócio | Módulos Django (apps), regras de domínio, validações e serviços.            | sigtcc/apps/                       |
| CI-02             | Esquema de Banco de Dados             | Modelos relacionais e arquivos versionados de migração.                     | sigtcc/apps/\*/migrations/         |
| CI-03             | Camada de Apresentação (Frontend)     | Gabaritos de tela (templates) e recursos estáticos (static).                | sigtcc/templates/ e sigtcc/static/ |
| CI-04             | Protótipo Navegável de Telas          | Telas estáticas homologadas no marco TP1 (Anexo D).                         | Branch dedicada prototype          |
| CI-05             | Especificação de Pacotes              | Dependências de terceiros e bibliotecas homologadas.                        | requirements.txt                   |
| CI-06             | Parâmetros de Qualidade               | Regras de análise estática e formatação PEP 8.                              | .flake8, pyproject.toml            |
| CI-07             | Registro de Alterações                | Histórico de modificações associado às baselines.                           | CHANGELOG.md                       |
| CI-08             | Matriz de Requisitos                  | Mapeamento e rastreabilidade dos requisitos funcionais e não funcionais.    | docs/Matriz_de_Requisitos.pdf      |
| CI-09             | Product Backlog e Cronograma          | Planejamento das sprints, épicos, histórias de usuário e prazos de entrega. | docs/Backlog_Cronograma.pdf        |

# 2. Arquitetura de Software e Estrutura de Diretórios

## 2.1 Justificativa Arquitetural: Monólito com Renderização no Servidor (SSR)

O Plano de Integração do SIGTCC (Seção 3.2.3) estabelece que a interface
web é gerada pelo próprio servidor, consumindo diretamente a camada de
aplicação.

Dessa forma, o sistema não é construído como uma Single Page Application
(SPA) com repositórios ou raízes isoladas de front-end (ex.: React/Vue)
e back-end (ex.: FastAPI/Node). A separação física em pastas
independentes de front e back exigiria o desenvolvimento e a manutenção
de uma API REST intermediária completa, o que acarretaria sobrecarga de
esforço incompatível com o cronograma acadêmico de cinco sprints.

O SIGTCC adota a arquitetura de Monólito Modular com Renderização no
Servidor (Server-Side Rendering - SSR):

- O servidor processa as regras de negócio, consulta o PostgreSQL e
  > renderiza diretamente o código HTML final enviado ao navegador.

- O código de apresentação (HTML, CSS e JavaScript utilitário) reside no
  > mesmo projeto, perfeitamente estruturado e modularizado dentro do
  > ecossistema do Django.

## 2.2 O Padrão MVC Tradicional versus MVT do Django

Conceitualmente, o sistema segue o padrão MVC (Model-View-Controller).
No entanto, o Django adota a denominação equivalente MVT
(Model-View-Template):

| **Componente MVC** | **Equivalente MVT no Django** | **Papel no SIGTCC**                                                                          | **Onde Reside no Código**          |
|--------------------|-------------------------------|----------------------------------------------------------------------------------------------|------------------------------------|
| Model              | Model                         | Mapeamento relacional dos dados no PostgreSQL e regras de validação cadastral.               | apps/\*/models.py                  |
| Controller         | View + urls.py                | Intercepta requisições HTTP, executa regras de negócio, aciona cálculos e define a resposta. | apps/\*/views.py e apps/\*/urls.py |
| View               | Template                      | Apresentação visual da interface com inserção dinâmica de variáveis via sintaxe Django.      | templates/\*/\*.html               |

## 2.3 Árvore Completa de Diretórios do Projeto

A raiz do repositório organiza as camadas de apresentação, módulos de
negócio e arquivos utilitários da seguinte forma:

SIGTCC/

├── .gitignore \# Exclusão formal de arquivos temporários e sensíveis

├── .env.example \# Gabarito de variáveis de ambiente sem credenciais
reais

├── CHANGELOG.md \# Histórico cumulativo de alterações por baseline

├── README.md \# Instruções de configuração, instalação e execução

├── requirements.txt \# Dependências Python oficiais (Python 3.12)

├── lint.bat \# Script de verificação de qualidade para Windows

└── sigtcc/

├── \_\_init\_\_.py

├── settings.py \# Núcleo de configuração do projeto Django

├── urls.py \# Roteamento global de endereços do sistema

├── wsgi.py \# Interface de execução do servidor web

├── asgi.py

├── apps/ \# Módulos funcionais alinhados aos Épicos do Backlog

│ ├── cadastro/ \# Épico 1: Cadastro e Manutenção

│ │ ├── migrations/ \# Versionamento estrutural do banco de dados

│ │ ├── models.py \# \[Model\] Usuarios, Turmas, Alunos, Docentes, TCCs,
Propostas e Orientacoes

│ │ ├── views.py \# \[Controller\] Lógica das telas de cadastramento

│ │ ├── forms.py \# Validação estruturada de entradas de usuário

│ │ ├── urls.py \# Mapeamento de rotas do módulo de cadastro

│ │ └── admin.py

│ ├── defesa/ \# Épico 2: Gestão da Defesa

│ │ ├── migrations/

│ │ ├── models.py \# \[Model\] Defesa, Banca, Notas e Ouvintes

│ │ ├── views.py \# \[Controller\] Agendamento, avaliação e liberação

│ │ ├── forms.py \# Validação de banca, critérios e agendamento

│ │ ├── services.py \# Lógica auxiliar: PDFs (Ata/Folha) e validação de
conflito

│ │ └── urls.py \# Mapeamento de rotas do módulo de defesa

│ └── relatorios/ \# Épico 3: Relatórios e Informações Gerenciais

│ ├── views.py \# \[Controller\] Consultas e consolidação de indicadores

│ ├── services.py \# Mecanismos de exportação para PDF, CSV e XLSX

│ └── urls.py \# Mapeamento de rotas de relatórios

├── templates/ \# Camada de Apresentação (Frontend - Gabaritos HTML)

│ ├── base.html \# Template mestre (estrutura comum, cabeçalho UEA e
rodapé)

│ ├── includes/ \# Componentes reutilizáveis (navbar, alertas, modais)

│ ├── cadastro/ \# Telas associadas ao Módulo de Cadastro

│ ├── defesa/ \# Telas de agendamento, deliberação e documentos

│ └── relatorios/ \# Telas de visualização gerencial e tabelas

├── static/ \# Arquivos estáticos servidos pelo sistema (Frontend)

│ ├── css/ \# Estilização visual (paleta oficial da EST/UEA)

│ ├── js/ \# Scripts para manipulação de DOM e máscaras

│ └── img/ \# Brasões institucionais e identidades visuais

└── media/ \# Armazenamento de arquivos dinâmicos (Ignorado no Git)

├── assinaturas/ \# Imagens de assinatura anexadas pelos avaliadores

└── documentos/ \# PDFs gerados das Atas Finais e Folhas de Aprovação

# 3. Padrões de Qualidade de Código e Ambiente Local

## 3.1 Linguagem e Ambiente Virtual

O desenvolvimento utiliza estritamente o interpretador Python 3.12. Para
garantir o isolamento das dependências, cada desenvolvedor deve operar
dentro de um ambiente virtual dedicado (venv), instalado e ativado no
Windows:

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

## 3.2 Análise Estática e Guia de Estilo

O código-fonte deve atender integralmente à PEP 8 e às convenções de
codificação do Django. A conferência é operacionalizada pelo trio
clássico:

- **1. flake8:** Identifica erros de sintaxe, variáveis locais não
  > utilizadas, importações desnecessárias e linhas com comprimento
  > inadequado.

- **2. black:** Executa a formatação determinística dos arquivos com
  > tamanho máximo de linha ajustado para 100 caracteres.

- **3. isort:** Harmoniza os blocos de importação em três agrupamentos
  > ordenados (módulos built-in do Python, dependências externas como
  > Django, e módulos internos do SIGTCC).

## 3.3 Script de Qualidade para Windows (lint.bat)

Para facilitar a execução rotineira antes da abertura de Pull Requests,
o arquivo lint.bat é disponibilizado na raiz do projeto:

@echo off

echo ===================================================

echo \[SIGTCC\] Executando Verificacoes de Qualidade de Codigo

echo ===================================================

echo \[1/3\] Ordenando imports com isort...

isort apps/sigtcc/

echo \[2/3\] Formatando codigo com Black...

black --line-length 100 apps/sigtcc/

echo \[3/3\] Executando analise estatica com Flake8...

flake8 --max-line-length 100 --exclude=migrations,venv apps/sigtcc/

if %ERRORLEVEL% EQU 0 (

echo ===================================================

echo \[SUCESSO\] Codigo aprovado nos padroes de qualidade!

echo ===================================================

) else (

echo ===================================================

echo \[FALHA\] Corrija os erros apontados pelo Flake8 acima.

echo ===================================================

)

## 3.4 Gestão de Segurança e LGPD

- **Variáveis de Ambiente:** É terminantemente vedado comitar chaves de
  > segurança (SECRET_KEY), credenciais do PostgreSQL ou senhas do
  > servidor de e-mail. O repositório fornece o arquivo .env.example, a
  > partir do qual cada membro cria seu .env local.

- **Diretório media/:** Imagens contendo assinaturas de membros de banca
  > (PNG/JPG até 2 MB) e documentos acadêmicos gerados contêm dados
  > protegidos e são mantidos exclusivamente em armazenamento local ou
  > no serviço de nuvem, sendo bloqueados no .gitignore para evitar
  > exposição no repositório.

# 4. Estratégia de Ramificação (GitFlow Clássico)

O ciclo de vida do código adota a metodologia GitFlow Clássico,
estabelecendo separação clara entre código em produção, linha de
desenvolvimento ativo e frentes de trabalho.

## 4.1 Branches Principais (Permanentes)

- **main:** Representa a versão estável, congelada e aceita formalmente
  > pela Product Owner (Profa. Diana) ao final dos marcos do projeto.
  > Nenhum membro da equipe comita diretamente na main. Todo avanço é
  > decorrente de merges originados de branches de release ou hotfix,
  > gerando obrigatoriamente uma tag de versão semântica.

- **develop:** Representa a linha de integração contínua do
  > desenvolvimento. Agrega as funcionalidades concluídas, revisadas e
  > aprovadas pela equipe. Deve sempre conter uma versão estável e
  > passível de execução local.

## 4.2 Branch de Isolamento do Protótipo

- **prototype:** Branch permanente e desacoplada do código Django,
  > criada para abrigar a versão de telas estáticas navegáveis gerada na
  > fase inicial. Hospeda o protótipo publicado no GitHub Pages
  > (https://celiobenj.github.io/SIGTCC/) sem interferir na evolução do
  > backend.

## 4.3 Branches de Suporte (Temporárias)

### A. Branches de Feature (feature/feat-XX-\*)

- **Origem:** develop \| **Destino:** develop.

- **Nomenclatura Obrigatória:** As branches são mapeadas diretamente
  > para as features do backlog:

  - feature/feat-01-usuarios (Gestão e cadastro de usuários e perfis);

  - feature/feat-02-turmas (Gestão de turmas e matrículas);

  - feature/feat-03-propostas (Submissão, avaliação e acompanhamento de
    > propostas de TCC).

- **Trabalho Concorrente:** Os desenvolvedores alocados na mesma Feature
  > compartilham a respectiva branch. Antes de enviar alterações ao
  > GitHub, o desenvolvedor deve sincronizar seu repositório local e
  > resolver conflitos de forma colaborativa.

### B. Branches de Estabilização de Marco (release/vX.X.X)

- **Origem:** develop \| **Destino:** main e develop.

- **Nomenclatura:** release/v0.2.0, release/v0.3.0 e release/v1.0.0.

- **Escopo de Atuação:** Aberta próxima às datas limites dos trabalhos
  > parciais (TP2, TP3 e TP4) para execução de checklists de aceitação,
  > ajustes finais de texto, atualização do CHANGELOG.md e preparação de
  > homologação, não recebendo novas funcionalidades.

### C. Branches de Correção Não Crítica (bugfix/epico-X-\*)

- **Origem:** develop \| **Destino:** develop.

- **Nomenclatura:** bugfix/epico-1-correcao-turma,
  > bugfix/epico-2-calculo-media.

- **Escopo:** Correção de falhas identificadas durante a integração na
  > branch develop antes do fechamento de um marco.

### D. Branches de Correção Emergencial (hotfix/vX.X.X)

- **Origem:** main \| **Destino:** main e develop.

- **Nomenclatura:** Ex.: hotfix/v0.2.1.

- **Escopo:** Tratamento de falhas graves detectadas no ambiente de
  > homologação após a publicação de uma baseline formal na main.

# 5. Padronização de Commits

Para assegurar legibilidade, rastreabilidade técnica e facilidade na
montagem do changelog, o SIGTCC adota a especificação Conventional
Commits 1.0.0 associada ao contexto do GitFlow.

## 5.1 Estrutura Padrão da Mensagem de Commit

Todo commit no repositório deve obedecer à seguinte estrutura:

\<tipo\>(\<escopo\>): \<descrição sucinta no tempo presente e modo
imperativo\>

\[corpo opcional detalhando a motivação técnica ou impacto\]

\[referência opcional ao cartão do Trello ou US\]

## 5.2 Tipos Permitidos de Commit

| **Tipo** | **Finalidade de Uso**                                                 | **Exemplo de Aplicação**                                           |
|----------|-----------------------------------------------------------------------|--------------------------------------------------------------------|
| feat     | Adição de uma nova funcionalidade ou regra de negócio.                | feat(feat-03): implementar validacao de prazo da proposta          |
| fix      | Correção de um defeito funcional ou erro no sistema.                  | fix(feat-02): corrigir bloqueio de inativacao de docente com banca |
| docs     | Alteração ou adição exclusiva em arquivos de documentação.            | docs: atualizar instrucoes de configuracao no README               |
| style    | Ajustes de formatação, espaçamento ou aspas sem alterar a lógica.     | style(feat-07): aplicar formatacao black nos templates de notas    |
| refactor | Reestruturação de código que não altera comportamento funcional.      | refactor(feat-07): modularizar funcao de calculo da media final    |
| test     | Adição ou correção de rotinas e scripts de verificação.               | test(feat-07): adicionar casos de teste manual para suplente       |
| chore    | Tarefas auxiliares de infraestrutura, scripts locais ou dependências. | chore: atualizar requirements com psycopg2-binary e pillow         |

## 5.3 Escopos Padronizados

O escopo identifica o módulo do sistema impactado pela alteração:

- **(feat-02):** Relacionado à Feature 02 (Gestão de Turmas);

- **(feat-03):** Relacionado à Feature 03 (Submissão e Avaliação de
  > Propostas);

- **(feat-07):** Relacionado à Feature 07 (Gestão e Avaliação de
  > Defesas);

- **(core):** Configurações globais do Django, arquivos de settings e
  > middleware;

- **(config):** Scripts de qualidade, ambiente e gerência de
  > configuração.

## 5.4 Regras de Ouro para os Commits

- **1. Atomicidade:** Cada commit deve representar uma única alteração
  > lógica coesa. Não misture formatação (style) com novas regras de
  > negócio (feat) no mesmo commit.

- **2. Verbo no Imperativo:** A primeira linha deve descrever a ação de
  > forma direta: use "implementar validação", "corrigir filtro",
  > "adicionar campo", e nunca "implementado" ou "corrigindo".

- **3. Sem Ponto Final:** A linha de título não termina com ponto final
  > e não deve exceder 72 caracteres.

- **4. Mensagens Claras:** Mensagens vagas como "ajustes", "subindo
  > código" ou "mudanças" são sumariamente proibidas.

# 6. Padronização de Pull Requests e Revisão Técnica por Pares

Em consonância com a seção 4.1.5.2 do Plano de Integração, toda
integração de código na branch develop ou main ocorre obrigatoriamente
via Pull Request revisado por outro integrante da equipe. Não são
permitidos direct pushes nessas branches.

## 6.1 Regras de Abertura e Nomenclatura do Pull Request

O título do Pull Request deve resumir a entrega seguindo a convenção:

\[Feat-XX\] Descrição da Feature (US-XX, US-YY)

Exemplos:

- \[Feat-07\] Implementação do Agendamento e Bloqueio de Conflitos
  > (US-21 e US-22)

- \[Feat-02\] Gestão e Importação de Turmas (US-01 e US-08)

- \[Hotfix\] Correção de Arredondamento da Nota Final (v0.2.1)

## 6.2 Governança de Esquema e Migrações de Banco de Dados

Para preservar a integridade referencial do PostgreSQL:

- Qualquer alteração em models.py deve conter os arquivos de migração
  > gerados (apps/\*/migrations/00XX\_\*.py) no próprio Pull Request;

- Se houver divergência de migrações com a branch develop, o
  > desenvolvedor deve resolver o conflito localmente utilizando o
  > comando oficial de unificação antes de solicitar o merge:

python manage.py makemigrations --merge

- É estritamente proibido resetar ou deletar o histórico de migrações
  > já consolidadas na develop.

## 6.3 Modelo Oficial de Pull Request (Template de PR)

Todo PR submetido no repositório GitHub deve conter o corpo estruturado
conforme o seguinte gabarito preenchido:

### 1. Resumo da Alteração

\[Descreva suscintamente o que foi desenvolvido, corrigido ou ajustado
tecnicamente neste PR\]

\### 2. Rastreabilidade com o Projeto

\* Feature Impactada: \[Ex.: Feature 02 - Gestão de Turmas \| Feature
07 - Gestão de Defesas\]

\* Histórias de Usuário Atendidas: \[Ex.: US-21, US-22\]

\* Cartão no Trello: \[Link ou título da atividade correspondente no
quadro do Sprint\]

\### 3. Checklist Técnico da Equipe (Definition of Done)

\- \[ \] O código foi verificado e aprovado localmente pelo script
\`lint.bat\` (Flake8, Black e isort).

\- \[ \] Não há variáveis, imports ou trechos de código não utilizados.

\- \[ \] As migrações do PostgreSQL foram criadas, aplicadas e testadas
com sucesso.

\- \[ \] O arquivo \`.env\` e arquivos da pasta \`media/\` NÃO foram
adicionados ao Git.

\- \[ \] A interface segue a paleta e os padrões de usabilidade
estabelecidos na ISO/IEC 25010.

\- \[ \] Não há quebras de layout ou erros acusados no console do
navegador.

\### 4. Evidência da Validação Manual (Critérios de Aceite das USs)

\[Checklist dos testes manuais executados pelo autor para demonstrar
conformidade\]

\- \[x\] Cenário 1: \[Ex.: Agendamento realizado com sucesso para TCC
com situação Apto para Defesa\]

\- \[x\] Cenário 2: \[Ex.: Bloqueio com Hard Fail ao tentar selecionar
sala já ocupada no mesmo horário\]

\- \[x\] Cenário 3: \[Ex.: Validação de URL remota exigindo protocolo
https://\]

\### 5. Revisão por Pares (Peer Review)

\* Revisor Designado: \[Nome do membro da equipe que realizou a revisão
independente\]

\* Parecer do Revisor:

\[ \] Aprovado integralmente para merge

\[ \] Solicitação de ajustes (detalhar nos comentários)

## 6.4 Política de Integração (Merge)

- Na branch develop, o merge deve ser efetuado utilizando a opção
  > "Create a merge commit" (--no-ff), preservando a visibilidade
  > histórica das ramificações de cada época de desenvolvimento.

- Na branch main, o merge proveniente de uma release/ é realizado sempre
  > via merge commit formal e acompanhado da criação da tag
  > correspondente.

# 7. Gestão de Linhas de Base (Baselines) e Versionamento

## 7.1 Padrão de Versionamento Semântico (SemVer 2.0.0)

As versões do sistema seguem o formato formal vMAJOR.MINOR.PATCH:

- **MAJOR (Maior):** Versão 1.0.0 final de homologação com entrega em
  > produção do SIGTCC (Marco TP4);

- **MINOR (Menor):** Incrementos parciais de novos módulos funcionais
  > estáveis nos marcos da disciplina (v0.2.0, v0.3.0);

- **PATCH (Correção):** Publicação de correções pontuais em baselines já
  > emitidas.

## 7.2 Linhas de Base Formais do Projeto (Baselines de Configuração)

As baselines do SIGTCC estão vinculadas às quatro entregas parciais
planejadas para o projeto:

| **Linha de Base** | **Tag Git** | **Marco Oficial** | **Data Limite** | **Conteúdo Técnico Congelado na Linha de Base**                                                                   |
|-------------------|-------------|-------------------|-----------------|-------------------------------------------------------------------------------------------------------------------|
| Baseline 1        | v0.1.0      | TP1               | 30/09/2026      | Declaração de escopo, matriz de requisitos, cronograma, protótipo na branch prototype e planos iniciais.          |
| Baseline 2        | v0.2.0      | TP2               | 21/10/2026      | Módulo de Cadastro funcional, modelagem de dados no PostgreSQL, telas em Django MVT e PGCS consolidado.           |
| Baseline 3        | v0.3.0      | TP3               | 18/11/2026      | Módulo de Gestão da Defesa (agendamento, validação de conflito, avaliação e PDFs da Ata/Folha) e plano de testes. |
| Baseline 4        | v1.0.0      | TP4               | 09/12/2026      | Sistema SIGTCC completo em produção, Módulo de Relatórios, execução dos testes e encerramento.                    |

## 7.3 Rastreabilidade de Versões (CHANGELOG.md)

O arquivo CHANGELOG.md na raiz do projeto reúne o sumário descritivo de
cada baseline estabelecida, estruturado nas subseções Adicionado,
Alterado e Corrigido:

# Histórico de Alterações (Changelog) - SIGTCC

\## \[v0.2.0\] - 21/10/2026 - Marco TP2

\### Adicionado

\- Estrutura monolítica em Django MVT e conexão oficial ao banco
PostgreSQL.

\- Modelagem de dados e migrações dos modelos de Usuário, Turma, Sala e
TCC.

\- Telas operacionais e formulários validados do Módulo de Cadastro
(Épico 1).

\- Script de qualidade \`lint.bat\` e documentação de configuração
(PGCS).

\- Remoção da entidade de Salas do escopo do projeto conforme
atualização da Matriz de Requisitos em 17/10.

\## \[v0.1.0\] - 30/09/2026 - Marco TP1

\### Adicionado

\- Criação e estruturação do repositório central monorepo.

\- Publicação do protótipo de telas navegável isolado na branch
\`prototype\`.

\- Levantamento da Matriz de Requisitos e consolidação do Plano de
Integração.

# 8. Procedimentos de Auditoria de Configuração e Responsabilidades

## 8.1 Matriz de Responsabilidades (RACI)

| **Atividade de Gerência de Configuração**                | **Célio Benjamim** | **Development Team** | **Profa. Diana (PO)** |
|----------------------------------------------------------|--------------------|----------------------|-----------------------|
| Redação, guarda e atualização periódica deste PGCS       | R/A                | C                    | I                     |
| Condução da Auditoria de Linha de Base nos Marcos TP     | R/A                | C                    | I                     |
| Criação de Tags e aprovação de merges para a main        | R/A                | I                    | I                     |
| Execução das rotinas locais do lint.bat antes de comitar | R                  | R                    | I                     |
| Revisão técnica por pares de Pull Requests na develop    | R                  | R/A                  | I                     |
| Homologação e aceite das entregas parciais de software   | C                  | C                    | R/A                   |

Convenção: R = Responsável pela Execução; A = Autoridade Final /
Aprovador; C = Consultado; I = Informado.

## 8.2 Rito de Auditoria de Linha de Base

Nas datas limites estipuladas no calendário acadêmico para as entregas
parciais (30/09, 21/10, 18/11 e 09/12), o responsável pela configuração
(Célio Benjamim) conduz formalmente a auditoria de congelamento técnico:

- **1. Auditoria de Branches:** Certifica que todos os códigos
  > planejados para o período foram integrados à develop estritamente
  > por meio de Pull Requests revisados e aprovados por pares.

- **2. Auditoria de Qualidade:** Executa o script de verificação e o
  > comando python manage.py check --deploy, atestando ausência de
  > pendências estáticas e de inconsistências de configuração.

- **3. Auditoria de Esquema:** Confere que nenhuma migração do banco
  > relacional PostgreSQL ficou desacompanhada de seus respectivos
  > arquivos no Git.

- **4. Fechamento e Tag:** Realiza o merge da branch release/vX.X.X para
  > a main, gera a tag assinada da versão (ex.: git tag -a v0.2.0 -m
  > "Release TP2") e atualiza o CHANGELOG.md.

- **5. Auditoria Documental:** Confirma que o checklist de testes
  > manuais da Definition of Done (DoD) foi preenchido para todas as
  > histórias de usuário compreendidas no marco.

# 9. Considerações Finais e Referências Normativas

Este plano estabelece as salvaguardas técnicas necessárias para que o
desenvolvimento do SIGTCC transcorra de maneira organizada, transparente
e com total rastreabilidade até o encerramento do semestre letivo.

## Referências

- ABNT NBR ISO/IEC 25010:2011: Engenharia de sistemas e software -
  > Requisitos e avaliação da qualidade de produto de software (SQuaRE).

- IEEE Std 828-2012: IEEE Standard for Configuration Management in
  > Systems and Software Engineering. New York: IEEE, 2012.

- ISO/IEC/IEEE 12207:2017: Systems and software engineering - Software
  > life cycle processes. Geneva: ISO, 2017.

- PYTHON SOFTWARE FOUNDATION: PEP 8 - Style Guide for Python Code, 2026.

- DJANGO SOFTWARE FOUNDATION: Django documentation: Coding style and
  > guidelines, 2026.

NUCOMP/EST-UEA: Plano de Integração do Projeto SIGTCC, 30/09/2026.
