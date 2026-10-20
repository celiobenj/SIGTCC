# SIGTCC – Sistema de Gestão de TCC do NUCOMP-UEA

Projeto da disciplina Engenharia de Software (ESTCMP025), 2026/2. Monólito Django com renderização
no servidor, Python 3.12 e PostgreSQL 16 (PGCS, seções 2 e 3).

## Pré-requisitos

- Python 3.12
- PostgreSQL 16, com um usuário que tenha permissão `CREATEDB` (os testes criam um banco próprio)

## Instalação

Windows (padrão do PGCS 3.1):

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

macOS ou Linux:

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Preencha o `.env` (chave secreta, dados do banco e pasta do cache) e crie o banco com o nome de
`DB_NAME`:

```bash
createdb sigtcc
```

## Execução

```bash
python manage.py migrate     # cria as 36 tabelas e a carga inicial dos domínios fixos
python manage.py test sigtcc.apps.cadastro sigtcc.apps.defesa
```

Antes de abrir um Pull Request, rode `lint.bat` (isort, black e flake8, linha de 100).

## Documentação

- Constituição do projeto: `.specify/memory/constitution.md`
- Documentos de origem (matriz, histórias de usuário, dicionário de dados, PGCS): `docs/fonte/`
- Especificações por feature (Spec Kit): `specs/`
- Validação do modelo de dados: `specs/001-modelo-dados/quickstart.md`
