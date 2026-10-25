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

## Passo 4. Carregar os dados de demonstração

O banco nasce vazio, só com cursos e áreas. O plano gratuito não tem terminal no servidor, então
os comandos rodam **no seu computador, apontando para o banco do Render**.

1. No Render, abra o banco **sigtcc-db**. Em **Connections**, copie a **External Database URL**.
   Ela contém a senha do banco: não cole em arquivo do repositório nem em chat.
2. No PowerShell, na pasta do projeto, aponte o Django para o banco do Render (só nesta janela):

   ```powershell
   $env:DATABASE_URL = "cole-aqui-a-External-Database-URL"
   ```

3. Rode a carga, escolhendo a senha de todas as contas (8 a 64 caracteres, com letra e número):

   ```powershell
   .venv\Scripts\python.exe manage.py popular_demo --senha EscolhaUmaSenha1 --confirmar
   ```

   - O comando mostra o banco em que vai mexer (`Banco: <nome> em <host>`; o host do Render
     termina em `render.com`) e pede para digitar o nome desse banco. Ao confirmar, **apaga
     todos os dados** (contas, turmas, TCCs, notificações e sessões), mantendo só cursos,
     códigos de curso e áreas de interesse.
   - Depois monta os cenários pelos mesmos serviços das telas, numa única transação. Se algo
     falhar, nada é alterado.
   - No fim, lista as contas de cada perfil e os alunos com a situação de cada um. Pode rodar de
     novo sempre que quiser voltar ao estado inicial (leva cerca de 1 minuto pela internet).
4. Feche essa janela do PowerShell ou rode `Remove-Item Env:DATABASE_URL`. **Enquanto a variável
   existir, todo comando `manage.py` daquela janela mexe no banco do Render.**
5. Entregue à professora o link, a senha e a lista de contas por um canal privado.

### O que a carga monta

Os e-mails são fictícios (`demo.nome@uea.edu.br`). Os alunos entram com o e-mail ou a matrícula.

| Turma | Situação | O que dá para ver |
|---|---|---|
| ECP-TCC1-2026.1 | Arquivada | Aprovados para TCC 2, um Reprovado e um Desistente; só consulta |
| ECP-TCC2-2026.1 | Arquivada | Dois Concluídos, com a Versão Final homologada |
| ECP-TCC1-2026.2 | Ativa | Sem Proposta (com e sem pedido de orientação), pedido pendente, pedido recusado, troca de orientador pendente, coorientador do NUCOMP (aceito e convite pendente), coorientador externo, atas com comentários, entregas no prazo, com atraso e não entregues, "Apto para Defesa" disponível e já indicado, Proposta incompleta, artigo aguardando aproveitamento, Jubilado, aluno excluído e 2 contas aguardando o primeiro acesso |
| ECP-TCC2-2026.2-A | Ativa, orientador automático | Alunos vindos do TCC 1, Apto para Defesa, Aprovado com Versão Final para homologar, Concluído, Versão Final devolvida para ajuste e um aluno transferido |
| ECP-TCC2-2026.2-B | Ativa | Destino da transferência e alunos novos |
| SI-TCC1-2026.2 | Ativa | Orientações, Apto, pedido pendente, coorientador externo e artigo homologado |
| SI-TCC2-2026.2 | Ativa | Aprovado com Correções com e sem "Correções Conferidas", Reprovado e artigo recusado |
| LIC-TCC1-2026.2 | Ativa | Turma pequena de outro curso, para o filtro por curso |

Também cria os 3 Coordenadores, as Secretarias (uma inativa), docentes ativos, um inativo e um
aguardando ativação, e membros externos ativo, expirado e aguardando ativação. As notificações
geradas pelos próprios serviços aparecem no sino de cada conta.

O resultado da defesa ainda não tem tela (Épico 2). Os Status "Aprovado para TCC 2", "Aprovado",
"Aprovado com Correções" e "Reprovado" são simulados pelo mesmo serviço do Status, com o gatilho
"Liberação do resultado".

## Passo 5 (opcional). Envio real de e-mail

Sem este passo, o sistema funciona e os e-mails (primeiro acesso, "Esqueci minha senha",
notificações) só aparecem em **Logs**. Para enviar de verdade pelo **Brevo** (gratuito, 300
e-mails por dia):

1. Crie a conta em <https://www.brevo.com>.
2. Em **Senders, Domains & Dedicated IPs** > **Senders**, cadastre e confirme o e-mail remetente
   (pode ser o seu Gmail).
3. Em **SMTP & API** > **SMTP**, gere uma **SMTP key**. Anote o login que aparece na mesma tela
   (algo como `xxxx@smtp-brevo.com`).
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

**Use a porta 2525, mesmo que o Brevo mostre 587.** O plano gratuito do Render bloqueia as portas
SMTP 25, 465 e 587, e o Brevo aceita as mesmas credenciais na 2525. Com a 587, o envio fica
esperando e falha depois do `EMAIL_TIMEOUT` (10 segundos), e a tela não mostra erro.

### Como testar o envio

O jeito mais simples usa um e-mail seu, de qualquer domínio:

1. Entre no sistema como **Coordenador** (por exemplo `demo.ricardo.prado@uea.edu.br`).
2. Em **Gestão de Contas** > **Membros externos**, cadastre um membro com o **seu e-mail
   pessoal**.
3. O sistema envia o link de primeiro acesso. Confira:
   - a caixa de entrada e o spam do seu e-mail;
   - no Brevo, **Transactional** > **Logs** (ou **Statistics**): o envio aparece como
     *Delivered*;
   - no Render, aba **Logs**: se aparecer `FALHA_ENVIO_EMAIL`, o envio falhou. O texto ao lado
     traz o tipo do erro: `TimeoutError` indica porta bloqueada (use a 2525);
     `SMTPAuthenticationError` indica login ou SMTP key errados.
4. Se quiser, siga o link e conclua o primeiro acesso: isso testa o fluxo inteiro.

Os e-mails `demo.…@uea.edu.br` da carga não existem; os envios para eles voltam e aparecem como
*Bounced* no Brevo, o que é esperado.

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
| `popular_demo` diz que o banco é local | O `$env:DATABASE_URL` não foi definido naquela janela do PowerShell. O comando recusa banco local (`localhost`) sem a opção `--local`, então nada foi alterado. |
| Algo deu errado e quer recomeçar | Apague o Blueprint, o serviço e o banco no Render e repita o Passo 3. |
