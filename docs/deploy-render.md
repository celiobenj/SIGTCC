# Deploy do ambiente de validação no Render

Roteiro para publicar o SIGTCC num link público, com o backend e o banco rodando, para a
Product Owner validar as funcionalidades já implementadas. Não é o ambiente de produção final do
PGCS (seção 9, previsto para o TP4): é um ambiente de validação, no plano gratuito do Render.

O repositório já traz o que o Render precisa:

| Arquivo | Para quê |
|---|---|
| `render.yaml` | "Blueprint": cria o banco PostgreSQL 16 e o serviço web de uma vez |
| `requirements.txt` | Inclui `gunicorn` (servidor web), `whitenoise` (CSS/JS) e `dj-database-url` |
| `sigtcc/settings.py` | Lê `DATABASE_URL` e o endereço público do Render; nada muda no ambiente local |

## O que acontece no deploy

A cada deploy, o Render:

1. baixa o código da branch escolhida no GitHub;
2. roda `pip install -r requirements.txt`, `collectstatic` e `migrate`, que cria as tabelas e
   carrega cursos e áreas pelas migrações;
3. sobe o sistema com `gunicorn` e publica o endereço `https://<nome>.onrender.com`.

O `SECRET_KEY` é gerado pelo Render. O `.env` não vai para o servidor e continua fora do Git.

## Passo 1. Enviar a branch para o GitHub

O Render lê o código do GitHub, não do seu computador. No PowerShell, na pasta do projeto:

```powershell
git push -u origin release/v0.2.0
```

Toda vez que você fizer push nessa branch, o Render publica de novo sozinho.

## Passo 2. Criar a conta no Render

1. Acesse <https://render.com> e clique em **Get Started**.
2. Escolha **GitHub** e entre com a conta que tem acesso ao repositório do SIGTCC.
3. Autorize o Render a ler os repositórios. Se o repositório estiver numa organização do GitHub,
   marque essa organização (ou "All repositories") na tela de permissões do GitHub.

O plano gratuito não cobra nada. Se o Render pedir um cartão para verificar a conta, nada é
cobrado enquanto tudo estiver no plano **Free**.

## Passo 3. Criar o banco e o sistema pelo Blueprint

1. No painel do Render, clique em **New +** e depois em **Blueprint**.
2. Escolha o repositório do SIGTCC. Se ele não aparecer, clique em **Configure account** e libere
   o acesso no GitHub.
3. Preencha:
   - **Blueprint Name:** `sigtcc`;
   - **Branch:** `release/v0.2.0`.
4. O Render mostra o que vai criar: o banco `sigtcc-db` e o serviço web `sigtcc`, ambos Free.
   Clique em **Deploy Blueprint**.
5. Espere de 5 a 10 minutos. Para acompanhar, abra o serviço **sigtcc** e a aba **Logs**. No
   final aparece algo como `Your service is live`.
6. O link fica no topo da página do serviço, por exemplo `https://sigtcc.onrender.com` (o Render
   pode acrescentar letras se o nome já existir). Abra: deve aparecer a tela de login do SIGTCC.

Se o build falhar, a causa aparece em **Logs**. Veja "Problemas comuns" no final.

## Passo 4. Criar as contas de acesso

O banco nasce vazio, só com cursos e áreas. O plano gratuito não tem terminal no servidor, então
as contas são criadas **do seu computador, apontando para o banco do Render**.

1. No Render, abra o banco **sigtcc-db**. Em **Connections**, copie a **External Database URL**.
   Ela contém a senha do banco: não cole em arquivo do repositório nem em chat.
2. No PowerShell, na pasta do projeto, aponte o Django para o banco do Render (só nesta janela):

   ```powershell
   $env:DATABASE_URL = "cole-aqui-a-External-Database-URL"
   ```

3. Crie uma conta por perfil, com e-mails fictícios e senhas de 8 a 64 caracteres, com letra e
   número. Exemplo (troque as senhas):

   ```powershell
   .venv\Scripts\python.exe manage.py criar_conta_teste --perfil coordenador --status ativa --email coordenador.demo@uea.edu.br --senha TroqueAqui1
   .venv\Scripts\python.exe manage.py criar_conta_teste --perfil secretaria --status ativa --email secretaria.demo@uea.edu.br --senha TroqueAqui1
   .venv\Scripts\python.exe manage.py criar_conta_teste --perfil docente --status ativa --email professor.demo@uea.edu.br --senha TroqueAqui1 --turma ECP_DEMO
   .venv\Scripts\python.exe manage.py criar_conta_teste --perfil docente --status ativa --email orientador.demo@uea.edu.br --senha TroqueAqui1
   .venv\Scripts\python.exe manage.py criar_conta_teste --perfil aluno --status ativa --matricula 2026000001 --email aluno.demo@uea.edu.br --senha TroqueAqui1 --turma ECP_DEMO
   .venv\Scripts\python.exe manage.py criar_conta_teste --perfil membro_externo --status ativa --email externo.demo@uea.edu.br --senha TroqueAqui1 --validade 2027-12-31
   ```

   - O docente com `--turma ECP_DEMO` vira o Professor da Disciplina de uma turma de TCC 1 de teste.
   - O aluno é matriculado nessa turma.
   - O comando roda no seu computador com o `DEBUG=True` do seu `.env`, mas grava no banco do
     Render, porque o `DATABASE_URL` tem prioridade sobre as variáveis `DB_*`.

4. Feche essa janela do PowerShell ou rode `Remove-Item Env:DATABASE_URL`. **Enquanto a variável
   existir, todo comando `manage.py` daquela janela mexe no banco do Render.**
5. Entregue à professora o link e os logins por um canal privado (e-mail ou mensagem), nunca pelo
   repositório.

Outra forma de criar contas é pelas telas. Entre como Coordenador e cadastre docentes, secretaria
e alunos. O link de primeiro acesso é enviado por e-mail; sem o Passo 5, ele aparece na aba
**Logs** do serviço (procure `Subject:` e o endereço `https://...`).

## Passo 5 (opcional). Envio real de e-mail

Sem este passo, o sistema funciona e os e-mails (primeiro acesso, "Esqueci minha senha",
notificações) só aparecem em **Logs**. Para enviar de verdade:

- O plano gratuito do Render bloqueia as portas SMTP comuns (25, 465 e 587), então o Gmail não
  funciona lá.
- O **Brevo** (gratuito, 300 e-mails por dia) aceita a porta **2525**.

1. Crie a conta em <https://www.brevo.com>.
2. Em **Senders, Domains & Dedicated IPs** > **Senders**, cadastre e confirme o e-mail remetente
   (pode ser o seu Gmail).
3. Em **SMTP & API** > **SMTP**, gere uma **SMTP key**. Anote o login que aparece na mesma tela.
4. No Render, abra o serviço **sigtcc** > **Environment** e cadastre:

   | Chave | Valor |
   |---|---|
   | `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` |
   | `EMAIL_HOST` | `smtp-relay.brevo.com` |
   | `EMAIL_PORT` | `2525` |
   | `EMAIL_USE_TLS` | `True` |
   | `EMAIL_HOST_USER` | o login SMTP do Brevo |
   | `EMAIL_HOST_PASSWORD` | a SMTP key |
   | `DEFAULT_FROM_EMAIL` | o remetente confirmado no passo 2 |

5. Clique em **Save, rebuild, and deploy**.

Para os e-mails chegarem, as contas precisam ter e-mails reais. Os `.demo@uea.edu.br` do Passo 4
não recebem nada.

## Limitações do plano gratuito

- **O sistema dorme depois de 15 minutos sem acesso.** O primeiro acesso seguinte demora cerca de
  1 minuto. Abra o link um pouco antes de apresentar.
- **Arquivos enviados não sobrevivem a um reinício** (ao dormir ou a cada deploy). Isso inclui a
  imagem da assinatura (US-38), o log de acesso e o bloqueio de login. Os dados do banco
  continuam.
- **O banco gratuito expira 30 dias depois de criado.** O Render avisa por e-mail. Depois disso,
  é preciso passar para um plano pago ou criar outro banco e repetir o Passo 4.
- **Nada roda agendado.** Os lembretes de entrega (US-15) e a expiração de membros externos não
  são automáticos. Se precisar, rode-os do seu computador com o `DATABASE_URL` do Passo 4:
  `enviar_lembretes_entrega` e `expirar_membros_externos`.
- **Use só dados fictícios.** Não cadastre dados pessoais reais de alunos (LGPD).

## Atualizar o sistema publicado

- Novo push na `release/v0.2.0`: o Render publica sozinho. As migrações novas rodam no build.
- Para publicar a partir de outra branch (por exemplo a `main`, depois do merge da release), abra
  o serviço > **Settings** > **Build & Deploy** > **Branch**.
- Para publicar de novo sem mudar o código, use **Manual Deploy** > **Deploy latest commit**.

## Problemas comuns

| Sintoma | O que fazer |
|---|---|
| Build falha em `pip install` | Confira se o `requirements.txt` da branch tem todas as dependências. |
| Build falha com `KeyError: 'SECRET_KEY'` | O serviço não foi criado pelo Blueprint. Em **Environment**, crie `SECRET_KEY` com um valor longo e aleatório. |
| `Bad Request (400)` ao abrir o link | Em **Environment**, crie `ALLOWED_HOSTS` com o domínio, sem `https://`. |
| Erro 403 (CSRF) ao entrar | Crie `CSRF_TRUSTED_ORIGINS` com `https://<o-seu-domínio>` e confira se `COOKIES_SEGUROS` é `True`. |
| Página sem estilo | Confira em **Logs** se o `collectstatic` rodou no build. |
| `criar_conta_teste` grava no banco local | O `$env:DATABASE_URL` não foi definido naquela janela do PowerShell. |
| Algo deu errado e quer recomeçar | Apague o Blueprint, o serviço e o banco no Render e repita o Passo 3. |
