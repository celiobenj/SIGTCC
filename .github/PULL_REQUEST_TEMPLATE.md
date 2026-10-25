**Origem:** `feature/feat-XX-nome` -> **Destino:** `develop` (merge `--no-ff`, PGCS 6.4)
**Spec:** `specs/00X-nome-feature/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, `tasks.md`)
**Responsável:** [Nome do integrante]

### 1. Resumo da Alteração

[Descreva sucintamente o que foi desenvolvido, corrigido ou ajustado tecnicamente neste PR]

### 2. Rastreabilidade com o Projeto

* **Feature Impactada:** [Ex.: Feature 02 - Acesso e Login | Feature 07 - Agendamento e Banca]
* **Histórias de Usuário Atendidas:** [Ex.: US-10, US-11, US-12, US-37, US-38]
* **Cartão no Trello:** [Link ou título da atividade correspondente no quadro do Sprint]

### 3. Checklist Técnico da Equipe (Definition of Done)

- [ ] O código foi aprovado na verificação completa do pre-commit (`pre-commit run --all-files`).
- [ ] Não há variáveis, imports ou trechos de código não utilizados.
- [ ] As migrações do PostgreSQL foram criadas, aplicadas e testadas com sucesso (ou `makemigrations --check` sem alterações).
- [ ] Os arquivos `.env` e os diretórios `sigtcc/media/` e `staticfiles/` NÃO foram adicionados ao Git.
- [ ] A interface segue a paleta e os padrões de usabilidade estabelecidos na ISO/IEC 25010, quando aplicável.
- [ ] Não há quebras de layout ou erros acusados no console do navegador, quando aplicável.

### 4. Evidência da Validação Manual (Critérios de Aceite das USs)

[Checklist dos testes manuais executados pelo autor para demonstrar conformidade]

- [ ] Cenário 1: [Ex.: Primeiro acesso com sucesso via link assinado com expiração de 24 horas]
- [ ] Cenário 2: [Ex.: Bloqueio automático de 15 minutos após 3 tentativas de senha incorretas]
- [ ] Cenário 3: [Ex.: Alteração de senha exigindo validação da senha atual]

### 5. Revisão por Pares (Peer Review)

* **Revisor Designado:** [Nome do membro da equipe que realizou a revisão independente]
* **Parecer do Revisor:**
  - [ ] Aprovado integralmente para merge
  - [ ] Solicitação de ajustes (detalhar nos comentários)
