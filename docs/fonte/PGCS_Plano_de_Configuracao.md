**PLANO DE GERÊNCIA DE CONFIGURAÇÃO DO SOFTWARE (PGCS)**

| **Nome do Projeto:** | Sistema de Gestão de TCC do NUCOMP-UEA (SIGTCC)   |
|----------------------|---------------------------------------------------|
| **Instituição:**     | UEA – Universidade do Estado do Amazonas (NUCOMP) |
| **Responsável:**     | Célio Benjamim                                    |
| **Data:**            | 21/10/2026                                        |

# Controle do Documento e Histórico de Revisões

| **Versão** | **Data**   | **Descrição da Alteração**                                                                                                                                                                                                                                      | **Autor / Responsável** |
|------------|------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------|
| **1.0**    | 18/10/2026 | Estruturação inicial do PGCS para o marco TP2: arquitetura MVT, organização de diretórios, GitFlow, padronização de commits, modelo de Pull Request e baselines.                                                                                                | Célio Benjamim          |
| **1.1**    | 20/10/2026 | Incorporação do ambiente multiplataforma (Windows e macOS), substituição do lint.bat pelo pre-commit, fluxo SDD (specs/ e .specify/), definição de logs em stdout e arquitetura de implantação em produção (Vercel, Neon, Vercel Blob, Brevo e GitHub Actions). | Célio Benjamim          |

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
Python 3.12 e Django, utilizando banco relacional PostgreSQL 16,
desenvolvida em estações Windows e macOS e implantada em plataformas
gratuitas de hospedagem.

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

- Configuração das verificações automáticas de qualidade, executadas a
  > cada commit em Windows e macOS (.pre-commit-config.yaml);

- Especificação formal de dependências de execução e de desenvolvimento
  > do ambiente (requirements.txt e requirements-dev.txt);

- Arquivos de configuração da implantação em produção (vercel.json e
  > .python-version);

- Rotina agendada do sistema, executada pelo GitHub Actions
  > (.github/workflows/);

- Especificações, planos e tarefas de cada feature, produzidos no fluxo
  > de desenvolvimento orientado a especificação (specs/ e .specify/);

**Fronteira com a Gestão Documental:** Os artefatos de planejamento
gerencial (Termo de Abertura, Matriz de Requisitos, EAP, Plano de
Integração, Modelo Lógico e Histórias de Usuário) são mantidos no Google
Drive institucional e no quadro Trello do projeto, que permanecem como
fonte oficial. O diretório docs/fonte/ do repositório guarda cópias
desses artefatos, convertidas em Markdown, apenas como referência para o
desenvolvimento; em caso de divergência, prevalece a versão do Google
Drive.

## 1.2 Itens de Configuração (Configuration Items - CIs)

| **Identificador** | **Item de Configuração (CI)**         | **Descrição do Componente**                                                                                 | **Localização no Repositório**                                           |
|-------------------|---------------------------------------|-------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| **CI-01**         | Aplicação Backend e Lógica de Negócio | Módulos Django (apps), regras de domínio, validações e serviços.                                            | sigtcc/apps/                                                             |
| **CI-02**         | Esquema de Banco de Dados             | Modelos relacionais e arquivos versionados de migração.                                                     | sigtcc/apps/\*/migrations/                                               |
| **CI-03**         | Camada de Apresentação (Frontend)     | Gabaritos de tela (templates) e recursos estáticos (static).                                                | sigtcc/templates/ e sigtcc/static/                                       |
| **CI-04**         | Protótipo Navegável de Telas          | Telas estáticas homologadas no marco TP1 (Anexo D).                                                         | Branch dedicada prototype                                                |
| **CI-05**         | Especificação de Pacotes              | Dependências de execução do sistema e ferramentas de desenvolvimento.                                       | requirements.txt e requirements-dev.txt                                  |
| **CI-06**         | Parâmetros de Qualidade               | Regras de análise estática, formatação PEP 8, verificação a cada commit e padronização de quebras de linha. | .flake8, pyproject.toml, .pre-commit-config.yaml e .gitattributes        |
| **CI-07**         | Registro de Alterações                | Histórico de modificações associado às baselines.                                                           | CHANGELOG.md                                                             |
| **CI-08**         | Matriz de Requisitos                  | Cópia de referência da Matriz de Requisitos.                                                                | docs/fonte/Matriz_Requisitos_17_10.md e .xlsx                            |
| **CI-09**         | Product Backlog e Cronograma          | Cópia de referência do cronograma e das Histórias de Usuário.                                               | docs/fonte/Cronograma_18_10.md e docs/fonte/Historias_de_Usuario_v3_2.md |
| **CI-10**         | Configuração de Implantação           | Versão do interpretador Python e parâmetros da plataforma de hospedagem.                                    | .python-version e vercel.json                                            |
| **CI-11**         | Rotina Agendada                       | Workflow que aciona, de hora em hora, as mudanças de estado por data e os lembretes de prazo.               | .github/workflows/rotina-agendada.yml                                    |
| **CI-12**         | Diagramas de Implantação              | Diagramas C4 dos ambientes de desenvolvimento e de produção.                                                | docs/arquitetura/Implantacao_SIGTCC.drawio e .pdf                        |
| **CI-13**         | Especificações das Features           | Especificação, pesquisa técnica, plano, tarefas e texto do Pull Request de cada feature.                    | specs/                                                                   |

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

├── .claude/ \# Agentes e skills do fluxo de especificação

├── .github/

│ ├── PULL_REQUEST_TEMPLATE.md

│ └── workflows/

│ └── rotina-agendada.yml \# Aciona as mudanças por data e os lembretes
de hora em hora

├── .specify/ \# Constituição, modelos e scripts do fluxo de
especificação

├── docs/

│ ├── arquitetura/ \# Diagramas de implantação (draw.io e PDF)

│ ├── fonte/ \# Cópias de referência dos documentos do Google Drive

│ └── questoes-a-rever.md \# Índice de questões abertas

├── specs/ \# Especificações de cada feature (spec, plan, tasks)

├── .env.example \# Gabarito de variáveis de ambiente sem credenciais
reais

├── .flake8 \# Regras do Flake8

├── .gitattributes \# Padronização de quebras de linha entre Windows e
macOS

├── .gitignore \# Exclusão formal de arquivos temporários e sensíveis

├── .pre-commit-config.yaml \# Verificações de qualidade executadas a
cada commit

├── .python-version \# Versão do interpretador usada na implantação
(3.12)

├── CHANGELOG.md \# Histórico cumulativo de alterações por baseline

├── CLAUDE.md \# Regras do assistente de codificação

├── GUIA_SDD.md \# Guia do fluxo de desenvolvimento orientado a
especificação

├── README.md \# Instruções de configuração, instalação e execução

├── manage.py \# Utilitário de linha de comando do Django

├── pyproject.toml \# Configuração do Black e do isort

├── requirements.txt \# Dependências de execução do sistema

├── requirements-dev.txt \# Ferramentas de desenvolvimento (pre-commit,
Black, isort, Flake8)

├── vercel.json \# Parâmetros da plataforma de hospedagem

└── sigtcc/

├── settings.py \# Núcleo de configuração, lido a partir de variáveis de
ambiente

├── storages.py \# Armazenamento de arquivos no Vercel Blob (produção)

├── urls.py

├── wsgi.py

├── asgi.py

├── apps/

│ ├── cadastro/ \# Épico 1 (modelos, serviços, telas, testes e comandos)

│ │ └── management/commands/

│ │ ├── criar_conta_teste.py

│ │ └── executar_rotina_agendada.py \# Mudanças por data e lembretes de
prazo

│ ├── defesa/ \# Épico 2

│ │ └── services.py \# Geração dos PDFs (xhtml2pdf) na liberação do
resultado

│ └── relatorios/ \# Épico 3

├── templates/

│ ├── cadastro/

│ ├── defesa/

│ │ └── pdf/ \# Templates da Ata Final e da Folha de Aprovação

│ ├── includes/

│ └── relatorios/

├── static/

└── media/ \# Assinaturas e PDFs do ambiente local (ignorado no Git)

# 3. Padrões de Qualidade de Código, Segurança e Configuração de Ambiente

## 3.1 Linguagem, Ambiente Virtual e Banco Local

O desenvolvimento utiliza estritamente o interpretador Python 3.12, em
estações Windows e macOS, cada uma com um ambiente virtual dedicado
(venv).

No Windows:

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt -r requirements-dev.txt

pre-commit install



No macOS:

python3.12 -m venv venv

source venv/bin/activate

pip install -r requirements.txt -r requirements-dev.txt

pre-commit install



**Banco de dados local:** Cada desenvolvedor instala o PostgreSQL 16 na
própria máquina (no Windows, pelo instalador oficial; no macOS, pelo
Postgres.app ou pelo Homebrew), cria o banco sigtcc e preenche as
variáveis DB_NAME, DB_USER, DB_PASSWORD, DB_HOST e DB_PORT do arquivo
.env. A estrutura é criada com python manage.py migrate e a tabela de
cache com python manage.py createcachetable.

## 3.2 Análise Estática e Guia de Estilo

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

- As três ferramentas são executadas automaticamente pelo pre-commit
  > antes de cada commit, nas mesmas versões para todos os integrantes,
  > independentemente do sistema operacional. As regras continuam nos
  > arquivos .flake8 e pyproject.toml. Um commit com falha na
  > verificação é bloqueado até a correção dos arquivos apontados.

## 3.3 Verificação Automática de Qualidade (pre-commit)

O script lint.bat é substituído pelo framework pre-commit, que executa
isort, Black e Flake8 em Windows e macOS, nas mesmas versões fixadas no
repositório e lendo as regras de .flake8 e pyproject.toml:

# .pre-commit-config.yaml

repos:

\- repo: https://github.com/pycqa/isort

rev: 9.0.2

hooks:

\- id: isort

\- repo: https://github.com/psf/black

rev: 26.10.1

hooks:

\- id: black

\- repo: https://github.com/pycqa/flake8

rev: 7.4.1

hooks:

\- id: flake8



| **Nº** | **Descrição**                                                                                                                                                                                                                                       |
|--------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **1**  | A ativação é feita uma única vez por integrante, com pre-commit install, após a criação do ambiente virtual (seção 3.1).                                                                                                                            |
| **2**  | A cada git commit, as verificações são executadas apenas sobre os arquivos alterados.                                                                                                                                                               |
| **3**  | A verificação completa do projeto, exigida antes da abertura de Pull Requests e na auditoria de linha de base, é feita com pre-commit run --all-files.                                                                                              |
| **4**  | As versões das ferramentas são atualizadas de forma controlada com pre-commit autoupdate, em commit do tipo chore(config), mantendo-as iguais às do requirements-dev.txt.                                                                           |
| **5**  | As referências ao lint.bat são substituídas por pre-commit run --all-files na constituição, no README.md, no CLAUDE.md, no GUIA_SDD.md e no modelo de Pull Request. As especificações de features já concluídas permanecem como registro histórico. |

O arquivo .gitattributes contém a regra \* text=auto eol=lf, para que os
arquivos de texto sejam versionados com a mesma quebra de linha em
Windows e macOS.

## 3.4 Gestão de Segurança e LGPD

- **Variáveis de Ambiente:** É terminantemente vedado comitar chaves de
  > segurança (SECRET_KEY), credenciais do PostgreSQL, a chave do
  > serviço de e-mail, o token da rotina agendada ou o token do
  > armazenamento de arquivos. O repositório fornece o arquivo
  > .env.example, a partir do qual cada membro cria seu .env local. Em
  > produção, os valores são cadastrados apenas no painel da plataforma
  > de hospedagem (escopo Production) e nos segredos do repositório no
  > GitHub.

- **Imagens de Assinatura e Documentos Gerados:** O banco de dados
  > guarda apenas o caminho de cada arquivo, conforme o Modelo Lógico.
  > As imagens de assinatura (PNG/JPG até 2 MB) e os PDFs da Ata Final e
  > da Folha de Aprovação são gravados por meio do default_storage do
  > Django: no diretório sigtcc/media/ no ambiente local e em um
  > armazenamento Vercel Blob privado em produção. Os arquivos não
  > possuem endereço público: a aplicação verifica a permissão do
  > usuário antes de entregar cada arquivo. O diretório sigtcc/media/ é
  > bloqueado no .gitignore.

- **Geração dos PDFs:** A Ata Final e a Folha de Aprovação são geradas
  > uma única vez, na liberação do resultado, com a banca, as notas, as
  > assinaturas e o Coordenador de Curso vigentes nesse momento, e
  > permanecem inalteradas após a geração.

- **Localização dos Dados:** O banco de produção é provisionado na
  > região de São Paulo do serviço Neon, quando disponível no plano
  > gratuito. Na homologação, utilizam-se preferencialmente dados
  > fictícios.

## 3.5 Configuração do settings.py para Produção

O settings.py já lê segredos e parâmetros do ambiente pelo
python-dotenv. Os ajustes abaixo são aplicados na preparação da
implantação, sem alterar o comportamento do ambiente local:

| **Nº** | **Descrição**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|--------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **1**  | **Banco de dados:** Quando a variável DATABASE_URL existir (fornecida pela integração do Neon), a conexão é montada a partir dela; caso contrário, continuam valendo DB_NAME, DB_USER, DB_PASSWORD, DB_HOST e DB_PORT. Em produção, adotam-se também DISABLE_SERVER_SIDE_CURSORS = True e CONN_MAX_AGE = 0, exigidos pelo pooler do Neon.                                                                                                                                                        |
| **2**  | **Fuso horário:** Mantêm-se TIME_ZONE = "America/Manaus" e USE_TZ = False, já definidos no repositório, coerentes com as colunas TIMESTAMP sem fuso do Modelo Lógico. O servidor de produção opera em UTC, mas o Django aplica o fuso America/Manaus às datas e horas do sistema.                                                                                                                                                                                                                |
| **3**  | **Cache:** O cache em arquivo (CACHE_DIR e CACHE_ACESSO_DIR) é mantido no ambiente local. Em produção, os dois aliases (default e acesso) passam a usar o cache em banco do Django (DatabaseCache), pois o sistema de arquivos da plataforma é somente leitura e cada instância teria um cache próprio, o que permitiria contornar o bloqueio de login. A tabela técnica é criada com python manage.py createcachetable e não integra o Modelo Lógico, assim como a tabela de sessões do Django. |
| **4**  | **Log de eventos de acesso:** O log em arquivo (LOG_DIR) é mantido no ambiente local. Em production, o sistema de arquivos é somente leitura, o que impede a criação da pasta de log; os eventos em produção são direcionados à saída padrão (stdout), conforme a seção 9.6.                                                                                                                                                                                                                     |
| **5**  | **Envio de e-mail:** No ambiente local, mantém-se o backend de console. Em produção, utiliza-se o Brevo por meio da biblioteca django-anymail (EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend" e ANYMAIL = {"BREVO_API_KEY": ...}). A configuração SIGTCC_EMAIL_SINCRONO passa a ser lida da variável EMAIL_SINCRONO, com valor True em produção, pois a plataforma pode encerrar a execução logo após a resposta, interrompendo o envio feito em thread separada.                         |
| **6**  | **Arquivos estáticos:** STATIC_ROOT aponta para o diretório staticfiles/, que a plataforma de hospedagem utiliza para publicar os arquivos estáticos na CDN.                                                                                                                                                                                                                                                                                                                                     |
| **7**  | **HTTPS:** Em produção, COOKIES_SEGUROS = True, SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https") e CSRF_TRUSTED_ORIGINS com o endereço do sistema, para que os formulários sejam aceitos atrás do proxy da plataforma.                                                                                                                                                                                                                                                              |
| **8**  | **Armazenamento de arquivos:** A configuração STORAGES usa, no ambiente local, o armazenamento padrão do Django em sigtcc/media/ (MEDIA_ROOT) e, em produção, a classe de sigtcc/storages.py, que grava no Vercel Blob privado. O código existente que usa default_storage (por exemplo, a gravação da assinatura no perfil) não precisa ser alterado.                                                                                                                                           |
| **9**  | **Geração de PDF:** A Ata Final e a Folha de Aprovação são geradas pela biblioteca xhtml2pdf a partir dos templates de sigtcc/templates/defesa/pdf/, na liberação do resultado, e gravadas no armazenamento de arquivos.                                                                                                                                                                                                                                                                         |

## 3.6 Variáveis de Ambiente

| **Variável**                                                                                   | **Ambiente Local**                             | **Ambiente de Produção**               | **Finalidade**                                        |
|------------------------------------------------------------------------------------------------|------------------------------------------------|----------------------------------------|-------------------------------------------------------|
| **SECRET_KEY**                                                                                 | Valor local qualquer                           | Valor secreto exclusivo                | Chave criptográfica do Django.                        |
| **DEBUG**                                                                                      | True                                           | False                                  | Exibição de páginas de erro detalhadas.               |
| **ALLOWED_HOSTS**                                                                              | localhost,127.0.0.1                            | Domínio .vercel.app do projeto         | Domínios aceitos pela aplicação.                      |
| **CSRF_TRUSTED_ORIGINS**                                                                       | Não utilizada                                  | https:// seguido do domínio do projeto | Origens aceitas no envio de formulários.              |
| **COOKIES_SEGUROS**                                                                            | False                                          | True                                   | Cookies de sessão e CSRF apenas por HTTPS.            |
| **SITE_URL**                                                                                   | http://localhost:8000                          | https:// seguido do domínio do projeto | Endereço base dos links enviados por e-mail.          |
| **DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT**                                            | PostgreSQL 16 local                            | Não utilizadas                         | Conexão com o banco local.                            |
| **DATABASE_URL**                                                                               | Não utilizada                                  | Conexão com pooling do Neon            | Conexão da aplicação com o banco de produção.         |
| **DATABASE_URL_UNPOOLED**                                                                      | Não utilizada                                  | Conexão direta do Neon                 | Execução das migrações em produção.                   |
| **CACHE_DIR, CACHE_ACESSO_DIR**                                                                | cache, cache_acesso                            | Não utilizadas                         | Pastas do cache em arquivo no ambiente local.         |
| **LOG_DIR**                                                                                    | logs                                           | Não utilizada                          | Pasta do log de eventos de acesso no ambiente local.  |
| **EMAIL_BACKEND**                                                                              | django.core.mail.backends.console.EmailBackend | anymail.backends.brevo.EmailBackend    | Forma de envio dos e-mails.                           |
| **EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS, EMAIL_TIMEOUT** | Opcionais, para teste com SMTP                 | Não utilizadas                         | Envio por SMTP no ambiente local.                     |
| **EMAIL_SINCRONO**                                                                             | False                                          | True                                   | Envio do e-mail dentro da própria requisição.         |
| **BREVO_API_KEY**                                                                              | Não utilizada                                  | Chave de API do Brevo                  | Autenticação no serviço de e-mail.                    |
| **DEFAULT_FROM_EMAIL**                                                                         | nao-responda@uea.edu.br                        | Endereço remetente validado no Brevo   | Remetente das notificações.                           |
| **CRON_SECRET**                                                                                | Valor local qualquer                           | Valor secreto exclusivo                | Token exigido pela rota da rotina agendada.           |
| **BLOB_READ_WRITE_TOKEN**                                                                      | Não utilizada                                  | Token do armazenamento Vercel Blob     | Gravação e leitura de assinaturas e PDFs em produção. |

O arquivo .env.example lista todas as variáveis acima, sem valores
reais. O remetente nao-responda@uea.edu.br não pode ser usado em
produção, pois o domínio uea.edu.br não está autenticado no Brevo.

## 3.7 Dependências

| **Arquivo**              | **Pacote**                                                             | **Situação**                                                                                        |
|--------------------------|------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| **requirements.txt**     | Django (5.2.18), psycopg, psycopg-binary, python-dotenv e dependências | Já presentes.                                                                                       |
| **requirements.txt**     | django-anymail\[brevo\]                                                | Incluir: envio de e-mail pela API do Brevo.                                                         |
| **requirements.txt**     | xhtml2pdf                                                              | Incluir: geração dos PDFs da Ata Final e da Folha de Aprovação.                                     |
| **requirements.txt**     | openpyxl                                                               | Incluir na feature de importação e relatórios: planilhas XLSX.                                      |
| **requirements.txt**     | Cliente do Vercel Blob para Python                                     | Incluir: comunicação de sigtcc/storages.py com o Vercel Blob; o pacote é definido na implementação. |
| **requirements-dev.txt** | pre-commit, black, isort, flake8 e dependências                        | Mover do requirements.txt: ferramentas usadas apenas no ambiente local, nas versões já fixadas.     |

A plataforma de hospedagem instala somente o requirements.txt.

## 3.8 Itens Ignorados pelo Git (.gitignore)

Além dos itens .env, venv/, sigtcc/media/, .DS_Store, /cache/,
/cache_acesso/ e /logs/ que já constam do arquivo atual, acrescentam-se
ao .gitignore:

| **Nº** | **Descrição**                                                           |
|--------|-------------------------------------------------------------------------|
| **1**  | .env.local : variáveis baixadas da plataforma de hospedagem.            |
| **2**  | .vercel/ : vínculo local com o projeto na plataforma de hospedagem.     |
| **3**  | staticfiles/ : arquivos estáticos coletados, gerados na implantação.    |
| **4**  | \*.dump e \*.sql : cópias de segurança exportadas do banco de produção. |

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

- feature/feat-00-spec-kit (Configuração do fluxo Spec-Driven
  > Development e governança do repositório, sem US);

- feature/feat-01-modelo-de-dados (Modelo de dados do SIGTCC no
  > PostgreSQL 16; base de todas as features);

- feature/feat-02-acesso-e-login (Acesso e login: primeiro acesso,
  > login, senha, perfil e notificações);

- feature/feat-03-turmas-e-alunos (Gestão de turmas e matrícula de
  > alunos);

- feature/feat-04-gestao-de-contas (Gestão de contas, perfis e
  > permissões);

- feature/feat-05-fluxo-do-tcc (Fluxo do TCC e entregas);

- feature/feat-06-orientacao (Orientação, atas e publicações);

- feature/feat-07-agendamento (Agendamento da defesa e composição da
  > banca);

- feature/feat-08-avaliacao (Avaliação e resultados da defesa);

- feature/feat-09-documentacao (Documentação e encerramento);

- feature/feat-10-dashboards (Dashboards de produção);

- feature/feat-11-apoio-operacional (Relatórios de apoio operacional).

- **Trabalho Concorrente:** Os desenvolvedores alocados na mesma Feature
  > compartilham a respectiva branch. Antes de enviar alterações ao
  > GitHub, o desenvolvedor deve sincronizar seu repositório local (ou
  > rebasear sobre a develop atualizada, conforme praticado na feat-02)
  > e resolver conflitos de forma colaborativa.

- **Encerramento:** após o merge na develop, a branch de feature é
  > apagada no GitHub (botão “Delete branch”).

### B. Branches de Estabilização de Marco (release/vX.X.X)

- **Origem:** develop \| **Destino:** main e develop.

- **Nomenclatura:** release/v0.2.0, release/v0.3.0 e release/v1.0.0.

- **Escopo de Atuação:** Aberta próxima às datas limites dos trabalhos
  > parciais (TP2, TP3 e TP4) para execução de checklists de aceitação,
  > ajustes finais de texto, atualização do CHANGELOG.md e preparação de
  > homologação, não recebendo novas funcionalidades.

### C. Branches de Correção Não Crítica (bugfix/feat-XX-\*)

- **Origem:** develop \| **Destino:** develop.

- **Nomenclatura:** bugfix/feat-03-correcao-turma,
  > bugfix/feat-08-calculo-media.

- **Escopo:** Correção de falhas identificadas durante a integração na
  > branch develop antes do fechamento de um marco.

### D. Branches de Correção Emergencial (hotfix/vX.X.X)

- **Origem:** main \| **Destino:** main e develop.

- **Nomenclatura:** Ex.: hotfix/v0.2.1.

- **Escopo:** Tratamento de falhas graves detectadas no ambiente de
  > homologação/produção após a publicação de uma baseline formal na
  > main.

## 4.4 Fluxo de Desenvolvimento Orientado a Especificação (Spec-Driven Development - SDD)

O SIGTCC adota o método de desenvolvimento orientado a especificação
(SDD) apoiado pela ferramenta Spec Kit (.specify/). Antes de qualquer
linha de código ser escrita na branch feature/feat-XX-\*, a equipe gera
e aprova os artefatos de especificação no diretório
specs/00X-nome-feature/:

1.  **spec.md:** define o escopo funcional e as regras a partir das User
    > Stories e da Matriz de Requisitos;

2.  **plan.md e data-model.md:** detalham o planejamento arquitetural,
    > modelos do Django e contratos de rota/serviço;

3.  **tasks.md:** estabelece a lista ordenada de tarefas atômicas de
    > codificação.  
    > Esses artefatos garantem rastreabilidade bidirecional entre o
    > código e os requisitos, sendo comitados e revisados juntamente com
    > o código-fonte no Pull Request da feature.

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

| **Tipo** | **Finalidade de Uso**                                                 | **Exemplo de Aplicação**                                            |
|----------|-----------------------------------------------------------------------|---------------------------------------------------------------------|
| feat     | Adição de uma nova funcionalidade ou regra de negócio.                | feat(feat-02): implementar login com base visual e permissoes       |
| fix      | Correção de um defeito funcional ou erro no sistema.                  | fix(feat-01): corrigir bloqueio de inativacao de docente com banca  |
| docs     | Alteração ou adição exclusiva em arquivos de documentação.            | docs(feat-02): registrar entrega no changelog e texto do pr         |
| style    | Ajustes de formatação, espaçamento ou aspas sem alterar a lógica.     | style(feat-07): aplicar formatacao black nos templates de notas     |
| refactor | Reestruturação de código que não altera comportamento funcional.      | refactor(feat-07): modularizar funcao de calculo da media final     |
| test     | Adição ou correção de rotinas e scripts de verificação.               | test(feat-02): cobrir mensagens, log e seguranca do acesso          |
| chore    | Tarefas auxiliares de infraestrutura, scripts locais ou dependências. | chore(config): adicionar xhtml2pdf e django-anymail ao requirements |

## 5.3 Escopos Padronizados

O escopo identifica o módulo do sistema impactado pela alteração:

- **(feat-XX):** a feature correspondente na listagem da seção 4.3 (ex.:
  > feat-01 Modelo de Dados, feat-02 Acesso e Login, feat-03 Turmas e
  > Alunos, feat-07 Agendamento e Banca);

- **(core):** Configurações globais do Django, arquivos de settings.py,
  > storages.py e middleware;

- **(config):** Verificações de qualidade (.pre-commit-config.yaml),
  > ambiente, constituição do Spec Kit, workflows e gerência de
  > configuração.

## 5.4 Regras de Ouro para os Commits

- **1. Atomicidade:** Cada commit deve representar uma única alteração
  > lógica coesa. Não misture formatação (style) com novas regras de
  > negócio (feat) no mesmo commit.

- **2. Verbo no Imperativo:** A primeira linha deve descrever a ação de
  > forma direta: use "implementar login", "cobrir mensagens",
  > "adicionar template", e nunca "implementado" ou "adicionando".

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

- O título do Pull Request deve resumir a entrega seguindo a convenção
  praticada no repositório: \[Feat-XX\] Nome ou Descrição da Feature
  (US-XX, US-YY)

Exemplos reais e previstos:

- \[Feat-00\] Configuração do fluxo Spec-Driven Development (sem US)

- \[Feat-01\] Modelo de dados do SIGTCC (US-03, US-07, US-08, US-13,
  > US-25, US-39)

- \[Feat-02\] Acesso e Login (US-10, US-11, US-12, US-37, US-38)

- \[Feat-07\] Agendamento e Banca (US-21, US-22, US-23, US-24, US-40)

## 6.2 Governança de Esquema e Migrações de Banco de Dados

Para preservar a integridade referencial do PostgreSQL:

- Qualquer alteração em models.py deve conter os arquivos de migração
  > gerados (sigtcc/apps/\*/migrations/00XX\_\*.py) no próprio Pull
  > Request, enquanto features que não alteram o modelo de dados validam
  > makemigrations --check retornando "No changes detected";

- Se houver divergência de migrações com a branch develop, o
  > desenvolvedor deve resolver o conflito localmente utilizando o
  > comando oficial de unificação antes de solicitar o merge:

python manage.py makemigrations --merge

- É estritamente proibido resetar ou deletar o histórico de migrações
  > já consolidadas na develop.

## 6.3 Modelo Oficial de Pull Request (.github/PULL_REQUEST_TEMPLATE.md)

Todo PR submetido no repositório GitHub deve conter o corpo estruturado
conforme o seguinte gabarito preenchido:

# \[Feat-XX\] Nome da Feature (US-XX, US-YY)

\*\*Origem:\*\* \`feature/feat-XX-nome\` -\> \*\*Destino:\*\*
\`develop\` (merge \`--no-ff\`, PGCS 6.4)

\*\*Spec:\*\* \`specs/00X-nome-feature/\` (\`spec.md\`, \`plan.md\`,
\`research.md\`, \`data-model.md\`, \`contracts/\`, \`quickstart.md\`,
\`tasks.md\`)

\*\*Responsável:\*\* \[Nome do integrante\]

\### 1. Resumo da Alteração

\[Descreva sucintamente o que foi desenvolvido, corrigido ou ajustado
tecnicamente neste PR\]

\### 2. Rastreabilidade com o Projeto

\* \*\*Feature Impactada:\*\* \[Ex.: Feature 02 - Acesso e Login \|
Feature 07 - Agendamento e Banca\]

\* \*\*Histórias de Usuário Atendidas:\*\* \[Ex.: US-10, US-11, US-12,
US-37, US-38\]

\* \*\*Cartão no Trello:\*\* \[Link ou título da atividade
correspondente no quadro do Sprint\]

\### 3. Checklist Técnico da Equipe (Definition of Done)

\- \[ \] O código foi aprovado na verificação completa do pre-commit
(\`pre-commit run --all-files\`).

\- \[ \] Não há variáveis, imports ou trechos de código não utilizados.

\- \[ \] As migrações do PostgreSQL foram criadas, aplicadas e testadas
com sucesso (ou \`makemigrations --check\` sem alterações).

\- \[ \] Os arquivos \`.env\`, \`.env.local\` e os diretórios
\`sigtcc/media/\` e \`staticfiles/\` NÃO foram adicionados ao Git.

\- \[ \] A interface segue a paleta e os padrões de usabilidade
estabelecidos na ISO/IEC 25010.

\- \[ \] Não há quebras de layout ou erros acusados no console do
navegador.

\### 4. Evidência da Validação Manual (Critérios de Aceite das USs)

\[Checklist dos testes manuais executados pelo autor para demonstrar
conformidade\]

\- \[x\] Cenário 1: \[Ex.: Primeiro acesso com sucesso via link assinado
com expiração de 24 horas\]

\- \[x\] Cenário 2: \[Ex.: Bloqueio automático de 15 minutos após 3
tentativas de senha incorretas\]

\- \[x\] Cenário 3: \[Ex.: Alteração de senha exigindo validação da
senha atual\]

\### 5. Revisão por Pares (Peer Review)

\* \*\*Revisor Designado:\*\* \[Nome do membro da equipe que realizou a
revisão independente\]

\* \*\*Parecer do Revisor:\*\*

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

| **Linha de Base** | **Tag Git** | **Marco Oficial** | **Data Limite** | **Conteúdo Técnico Congelado na Linha de Base**                                                                                                                                                   |
|-------------------|-------------|-------------------|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Baseline 1**    | v0.1.0      | **TP1**           | 30/09/2026      | Declaração de escopo, matriz de requisitos, cronograma, protótipo na branch prototype e planos iniciais.                                                                                          |
| **Baseline 2**    | v0.2.0      | **TP2**           | 23/10/2026      | Módulo de Cadastro funcional (feat-00, feat-01, feat-02 e demais entregas do TP2), modelagem das 36 tabelas no PostgreSQL 16, telas em Django MVT, configuração de pre-commit e PGCS consolidado. |
| **Baseline 3**    | v0.3.0      | **TP3**           | 18/11/2026      | Módulo de Gestão da Defesa (agendamento, validação de conflito, avaliação e PDFs da Ata/Folha) e plano de testes.                                                                                 |
| **Baseline 4**    | v1.0.0      | **TP4**           | 09/12/2026      | Sistema SIGTCC completo em produção (Vercel/Neon), Módulo de Relatórios, execução dos testes e encerramento.                                                                                      |

## 7.3 Rastreabilidade de Versões (CHANGELOG.md)

O arquivo CHANGELOG.md na raiz do projeto reúne o sumário descritivo de
cada baseline estabelecida, estruturado nas subseções Adicionado,
Alterado e Corrigido:

# Histórico de Alterações (Changelog) - SIGTCC

\## \[v0.2.0\] - 23/10/2026 - Marco TP2

\### Adicionado

\- Configuração do fluxo Spec-Driven Development (\`specs/\` e
\`.specify/\`) e governança do repositório (\`feat-00\`).

\- Estrutura monolítica em Django 5.2.18 MVT e conexão oficial ao banco
PostgreSQL 16 (\`feat-01\`).

\- Implementação das 36 tabelas, 201 colunas, 49 restrições nomeadas e
cargas iniciais do Modelo Lógico (\`feat-01\`).

\- Implementação do fluxo de Acesso e Login: primeiro acesso,
autenticação com bloqueio em cache, redefinição de senha, perfil e
notificações (\`feat-02\`).

\- Verificação automática multiplataforma com \`pre-commit\` (Flake8,
Black e isort) e PGCS consolidado.

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

| **Atividade de Gerência de Configuração**                                          | **Célio Benjamim** | **Development Team** | **Profa. Diana (PO)** |
|------------------------------------------------------------------------------------|--------------------|----------------------|-----------------------|
| Redação, guarda e atualização periódica deste PGCS                                 | **R/A**            | C                    | I                     |
| Condução da Auditoria de Linha de Base nos Marcos TP                               | **R/A**            | C                    | I                     |
| Criação de Tags e aprovação de merges para a main                                  | **R/A**            | I                    | I                     |
| Execução das verificações do pre-commit antes de comitar                           | R                  | **R**                | I                     |
| Revisão técnica por pares de Pull Requests na develop                              | R                  | **R/A**              | I                     |
| Guarda das contas da hospedagem, do banco, do armazenamento e do serviço de e-mail | **R/A**            | I                    | I                     |
| Cadastro das variáveis de ambiente e dos segredos de produção                      | **R/A**            | C                    | I                     |
| Execução das migrações e da cópia de segurança em produção                         | **R/A**            | C                    | I                     |
| Homologação e aceite das entregas parciais de software                             | C                  | C                    | **R/A**               |

Convenção: R = Responsável pela Execução; A = Autoridade Final /
Aprovador; C = Consultado; I = Informado.

## 8.2 Rito de Auditoria de Linha de Base

Nas datas limites estipuladas no calendário acadêmico para as entregas
parciais (30/09, 23/10, 18/11 e 09/12), o responsável pela configuração
(Célio Benjamim) conduz formalmente a auditoria de congelamento técnico:

- **1. Auditoria de Branches:** Certifica que todos os códigos
  > planejados para o período foram integrados à develop estritamente
  > por meio de Pull Requests revisados e aprovados por pares, com
  > exclusão das branches temporárias já integradas.

- **2. Auditoria de Qualidade:** Executa pre-commit run --all-files e o
  > comando python manage.py check --deploy, atestando ausência de
  > pendências estáticas e de inconsistências de configuração.

- **3. Auditoria de Esquema:** Confere que nenhuma migração do banco
  > relacional PostgreSQL ficou desacompanhada de seus respectivos
  > arquivos no Git (makemigrations --check).

- **4. Fechamento e Tag:** Realiza o merge da branch release/vX.X.X para
  > a main, gera a tag assinada da versão (ex.: git tag -a v0.2.0 -m
  > "Release TP2") e atualiza o CHANGELOG.md.

- **5. Auditoria de Implantação:** Após o merge na main, confirma no
  > painel da plataforma de hospedagem que a implantação foi concluída,
  > executa as migrações em produção (python manage.py migrate, com
  > DATABASE_URL apontando para a conexão direta), acessa o sistema e
  > dispara um e-mail de teste.

- **6. Cópia de Segurança:** Exporta o banco de produção com pg_dump e
  > guarda o arquivo no Google Drive institucional, fora do repositório.

- **7. Auditoria Documental:** Confirma que o checklist de testes
  > manuais da Definition of Done (DoD) foi preenchido para todas as
  > histórias de usuário compreendidas no marco.

# 9. Ambientes e Implantação

O SIGTCC opera em dois ambientes, cada um representado por um diagrama
de implantação na notação C4 (CI-12). A hospedagem em produção utiliza
exclusivamente planos gratuitos, em conformidade com o orçamento
simbólico do projeto.

## 9.1 Ambientes do Projeto

| **Elemento**                  | **Ambiente de Desenvolvimento**                             | **Ambiente de Produção**                                      |
|-------------------------------|-------------------------------------------------------------|---------------------------------------------------------------|
| **Infraestrutura**            | Estação de cada integrante, Windows ou macOS                | Vercel, plano Hobby (Vercel Function, Linux)                  |
| **Execução da aplicação**     | python manage.py runserver, em venv                         | Vercel Function com Python 3.12                               |
| **Arquivos estáticos**        | Servidor de desenvolvimento do Django                       | CDN da plataforma de hospedagem (Vercel CDN)                  |
| **Banco de dados**            | PostgreSQL 16 instalado localmente                          | PostgreSQL 16 gerenciado no Neon, plano gratuito              |
| **Cache**                     | Arquivo (pastas cache e cache_acesso)                       | Banco de dados (DatabaseCache)                                |
| **Log de eventos de acesso**  | Arquivo (pasta logs)                                        | Saída padrão (stdout), exibida nos logs da Vercel (seção 9.6) |
| **Envio de e-mail**           | Exibido no terminal (backend de console)                    | Brevo, por API HTTPS, na própria requisição                   |
| **Geração de PDF**            | xhtml2pdf, na liberação do resultado                        | xhtml2pdf, na liberação do resultado                          |
| **Armazenamento de arquivos** | Diretório sigtcc/media/                                     | Vercel Blob privado                                           |
| **Rotina agendada**           | Executada manualmente pelo comando executar_rotina_agendada | GitHub Actions, de hora em hora                               |
| **Origem do código**          | Branch de trabalho local                                    | Branch main                                                   |

## 9.2 Vínculo entre Branches e Ambientes

| **Nº** | **Descrição**                                                                                                                                                                                                                                                                           |
|--------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **1**  | A branch main é a branch de produção da plataforma de hospedagem: cada merge na main, decorrente de release ou hotfix, gera uma nova implantação.                                                                                                                                       |
| **2**  | Pushes nas demais branches podem gerar implantações de pré-visualização automáticas, que não constituem ambiente oficial do projeto. As variáveis do banco de produção são cadastradas apenas no escopo Production, de modo que essas pré-visualizações não acessam os registros reais. |
| **3**  | A branch prototype continua publicada no GitHub Pages e não é implantada na plataforma de hospedagem.                                                                                                                                                                                   |
| **4**  | O repositório é público e permanece hospedado na conta pessoal do responsável pela configuração no GitHub (celiobenj), permitindo integração direta e gratuita com o plano Hobby da Vercel e com o GitHub Actions.                                                                      |

## 9.3 Procedimento de Implantação Inicial

| **Nº** | **Descrição**                                                                                                                                                                       |
|--------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **1**  | Criar a conta no Vercel (plano Hobby) com o login do GitHub e importar o repositório do SIGTCC.                                                                                     |
| **2**  | Adicionar o Neon pela integração do Vercel, com PostgreSQL 16 e na região de São Paulo quando disponível, para provisionar DATABASE_URL e DATABASE_URL_UNPOOLED.                    |
| **3**  | Criar no painel do Vercel um armazenamento Blob privado vinculado ao projeto, que provisiona BLOB_READ_WRITE_TOKEN.                                                                 |
| **4**  | Criar a conta no Brevo, validar o endereço remetente do projeto e gerar a chave de API.                                                                                             |
| **5**  | Cadastrar as demais variáveis da seção 3.6 no painel do Vercel, no escopo Production.                                                                                               |
| **6**  | Cadastrar CRON_SECRET e o endereço do sistema nos segredos do repositório no GitHub.                                                                                                |
| **7**  | Realizar o merge da release na main e aguardar a implantação: a plataforma instala o requirements.txt, coleta os arquivos estáticos e publica a aplicação.                          |
| **8**  | Executar python manage.py migrate, python manage.py createcachetable e o comando de criação da conta inicial, apontando DATABASE_URL para a conexão direta (DATABASE_URL_UNPOOLED). |
| **9**  | Acessar o sistema, autenticar-se, enviar uma imagem de assinatura de teste e disparar um e-mail de teste.                                                                           |

## 9.4 Rotina Agendada

O Modelo Lógico prevê uma tarefa agendada para as mudanças de estado por
data e para os lembretes de prazo. Em produção, essa tarefa é acionada
pelo GitHub Actions:

| **Nº** | **Descrição**                                                                                                                                                                                                                                                                                                                        |
|--------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **1**  | O workflow .github/workflows/rotina-agendada.yml é executado de hora em hora e envia uma requisição HTTPS à rota protegida da rotina, com o CRON_SECRET no cabeçalho Authorization.                                                                                                                                                  |
| **2**  | A rotina aplica as mudanças de estado por data previstas no Modelo Lógico (entrega para Não Entregue após a Data Limite, sessão para Em Andamento na data e no horário marcados e conta de Membro Externo para Expirada após mem_validade_ate) e registra os eventos correspondentes, como o Início Automático em Historico_Defesas. |
| **3**  | Como a rotina tem precisão de até uma hora, as telas que exibem esses status aplicam a mesma mudança, pelo mesmo serviço, quando encontram um registro com a data já vencida e a mudança ainda não aplicada. Assim, o status exibido está sempre correto e cada evento é registrado uma única vez.                                   |
| **4**  | A rotina também gera os lembretes de 7 dias, 48 horas e 24 horas antes da Data Limite, em Notificacoes e por e-mail, apenas para os alunos que ainda não enviaram a entrega e exceto em turmas arquivadas. Cada lembrete é registrado ao ser enviado, para que execuções seguidas não o repitam.                                     |
| **5**  | O agendamento do GitHub Actions é expresso em UTC; as comparações de data e hora são feitas no fuso America/Manaus, definido no settings.py.                                                                                                                                                                                         |
| **6**  | O GitHub Actions foi escolhido porque o agendador nativo do plano Hobby do Vercel executa no máximo uma vez por dia, frequência insuficiente para os lembretes de 48 e 24 horas e para o início das sessões.                                                                                                                         |
| **7**  | No ambiente local, a mesma rotina é executada manualmente pelo comando python manage.py executar_rotina_agendada.                                                                                                                                                                                                                    |

## 9.5 Limites dos Planos Gratuitos

| **Nº** | **Descrição**                                                                                                                                                                                                                                            |
|--------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **1**  | Cada requisição à aplicação aceita até 4,5 MB e cada execução dura até 300 segundos.                                                                                                                                                                     |
| **2**  | O sistema de arquivos da aplicação é somente leitura, razão pela qual os arquivos ficam no Vercel Blob, que oferece no plano Hobby 1 GB de armazenamento e 2.000 operações de envio por mês. Excedido o limite, o acesso ao Blob é suspenso por 30 dias. |
| **3**  | O banco gratuito do Neon oferece 1 GB por projeto e é suspenso após 5 minutos ocioso, sem retomada automática no acesso seguinte.                                                                                                                        |
| **4**  | O plano gratuito do Brevo permite 300 e-mails por dia e inclui a marca do serviço nas mensagens.                                                                                                                                                         |

## 9.6 Log de Eventos de Acesso em Produção

O log de eventos de acesso foi especificado na feat-02 como arquivo
local (LOG_DIR), sem criação de tabela no banco de dados. Como em
produção o ambiente serverless da Vercel possui sistema de arquivos
somente leitura, adota-se o direcionamento para a Saída padrão (stdout),
conforme comparativo abaixo:

| **Opção**                             | **Descrição**                                                                                                                                                                                                                                                                                                                                         |
|---------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Saída padrão (stdout) \[Adotada\]** | **Os eventos de acesso são enviados à saída padrão (StreamHandler) quando LOG_DIR não está definida, sendo exibidos nos Runtime Logs da plataforma de hospedagem.** **Escolhida para o projeto:** preserva integralmente a especificação da feat-02 ("sem criar tabelas nem colunas", FR-028), embora com retenção limitada ao plano Hobby da Vercel. |
| **Tabela técnica**                    | Os eventos seriam gravados em uma tabela técnica do Django, fora do Modelo Lógico, como as tabelas de sessão e de cache. Descartada nesta fase para não exigir migração adicional nem alterar a restrição arquitetural homologada na feat-02.                                                                                                         |

# 10. Considerações Finais e Referências Normativas

Este plano estabelece as salvaguardas técnicas necessárias para que o
desenvolvimento e a implantação do SIGTCC transcorram de maneira
organizada, transparente e com total rastreabilidade até o encerramento
do semestre letivo.

## Referências

- **BROWN, S.** *The C4 model for visualising software architecture*.
  > Disponível em: [<u>https://c4model.com/</u>](https://c4model.com/).
  > Acesso em: 20 out. 2026.

- **GITHUB.** *GitHub Actions documentation*. Disponível em:
  > [<u>https://docs.github.com/actions</u>](https://docs.github.com/actions).
  > Acesso em: 20 out. 2026.

- **NEON.** *Neon documentation*. Disponível em:
  > [<u>https://neon.com/docs</u>](https://neon.com/docs). Acesso em: 20
  > out. 2026.

- **PRE-COMMIT.** *pre-commit: a framework for managing and maintaining
  > multi-language pre-commit hooks*. Disponível em:
  > [<u>https://pre-commit.com/</u>](https://pre-commit.com/). Acesso
  > em: 20 out. 2026.

- **VERCEL.** *Deploy a Django app on Vercel*. Disponível em:
  > [<u>https://vercel.com/docs/frameworks/full-stack/django</u>](https://vercel.com/docs/frameworks/full-stack/django).
  > Acesso em: 20 out. 2026.

- **VERCEL.** *Usage & Pricing for Cron Jobs*. Disponível em:
  > [<u>https://vercel.com/docs/cron-jobs/usage-and-pricing</u>](https://vercel.com/docs/cron-jobs/usage-and-pricing).
  > Acesso em: 20 out. 2026.

- **VERCEL.** *Vercel Blob Pricing*. Disponível em:
  > [<u>https://vercel.com/docs/vercel-blob/usage-and-pricing</u>](https://vercel.com/docs/vercel-blob/usage-and-pricing).
  > Acesso em: 20 out. 2026.
