# Ambientes do SIGTCC: construção e implantação real

O projeto tem duas visões de ambiente, que não devem ser confundidas:

1. **Visão de construção**: o que existe hoje para desenvolver, validar e entregar na disciplina
   Engenharia de Software (ESTCMP025, 2026/2). Usa só planos gratuitos.
2. **Visão de implantação real**: como o sistema ficaria em produção de verdade, para uso
   contínuo do NUCOMP/EST/UEA, com escala, retenção de dados e operação. É um alvo, **não está
   implementado**.

O PGCS (seção 9) descreve a visão de construção. Este documento a resume e acrescenta a visão de
implantação real.

## 1. Visão de construção (entrega da disciplina)

| Ambiente | Para quê | Onde roda | Como |
|---|---|---|---|
| Desenvolvimento | Escrever e testar | Estação de cada integrante | `runserver` em `venv`, PostgreSQL 16 local; e-mail no terminal; arquivos em `sigtcc/media/` |
| Validação (homologação) | A Product Owner e a professora validarem as funcionalidades | Render, plano Free | `gunicorn`, banco PostgreSQL 16 do Render, `WhiteNoise`, Brevo (porta 2525), dados fictícios (`popular_demo`) |

Características e limites aceitos (PGCS 9.5, `docs/deploy-render.md`):

- o serviço dorme após 15 minutos sem acesso;
- o disco é efêmero: assinaturas, cache e arquivos enviados somem a cada reinício ou deploy (PDFs
  são gerados a cada download, sem gravar arquivo);
- o banco gratuito expira 30 dias depois de criado;
- nada roda agendado: `enviar_lembretes_entrega`, `expirar_membros_externos` e `iniciar_sessoes`
  são executados por execução manual (decisão Q-67 C, 09/11/2026); as telas aplicam as regras
  por data, e os comandos completam o registro e os lembretes;
- só dados fictícios (LGPD).

Passo a passo: [`deploy-render.md`](deploy-render.md).

## 2. Visão de implantação real (alvo para produção)

Pontos que a produção real precisa resolver e que o ambiente de validação deixa de fora. Cada
linha diz o que muda em relação à visão de construção e o que isso exige do sistema.

| Tema | Alvo em produção real | Exige do sistema |
|---|---|---|
| Aplicação | Várias instâncias sem estado atrás de um balanceador, com TLS e domínio institucional | Nenhum dado em disco ou em memória do processo |
| Banco | PostgreSQL 16 gerenciado, sem expiração, com backup automático, restauração testada e réplica de leitura se a carga pedir | Só a `DATABASE_URL` muda |
| Arquivos (assinaturas, evidências) | Armazenamento de objetos privado, com versionamento e cópia de segurança | Trocar `default_storage` por um backend de objetos; hoje as imagens ficam em `MEDIA_ROOT` (S-04 e S-06 da `questoes-a-rever.md`) |
| Cache e bloqueio de login | Cache compartilhado entre instâncias (Redis ou equivalente) | Hoje o cache é em arquivo (`cache/`, `cache_acesso/`), válido para uma instância |
| Tarefas por data | Agendador do ambiente (cron do servidor, Cron Job da plataforma ou fila com agendamento) chamando `iniciar_sessoes`, `expirar_membros_externos` e `enviar_lembretes_entrega` | Os comandos já existem e são idempotentes; falta só o agendamento |
| E-mail e declarações | Remetente do domínio da UEA (SPF e DKIM), fila de envio com nova tentativa | Hoje o envio roda em thread depois do commit; numa fila, o contrato de `enviar_email_apos_commit` se mantém |
| PDFs | Geração no mesmo processo, como hoje, ou worker dedicado se o volume crescer | `pdf._TRAVA_PDF` serializa por processo; com várias instâncias, cada uma gera o seu |
| Logs e monitoramento | Logs centralizados, alerta de erro e de indisponibilidade | `LOG_STDOUT` já envia à saída padrão (PGCS 9.6) |
| Entrega contínua | Ambiente de pré-produção, migração testada antes da produção, reversão documentada | Hoje só a `main` é implantada (PGCS 9.2) |
| Segredos e dados pessoais | Cofre de segredos, retenção e descarte conforme a LGPD, auditoria de acesso | Fora do escopo do código atual |

Nada desta seção faz parte da entrega da disciplina. Ela serve de referência para a decisão de
implantar o SIGTCC na UEA depois do semestre.
