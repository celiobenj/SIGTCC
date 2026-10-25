# Quickstart: validar a Gestão de Contas

**Feature**: [spec.md](spec.md) | **Rotas**: [contracts/rotas.md](contracts/rotas.md) |
**Serviços**: [contracts/servicos-compartilhados.md](contracts/servicos-compartilhados.md)

Roteiro para conferir a feature de ponta a ponta. Ambiente Windows com `venv`, PostgreSQL 16 e o
`.env` da spec 003 (banco, e-mail de console e `LOG_DIR`).

## 1. Preparar

```bat
venv\Scripts\activate
python manage.py migrate
python manage.py test sigtcc.apps.cadastro
```

Resultado esperado: os testes desta feature passam, inclusive os de aceite `test_us03_*`,
`test_us04_*`, `test_us05_*`, `test_us06_*`, `test_us50_*`, `test_comando_coordenadores` e os de
concorrência. O teste marcado como pendente da Q-52 (texto de expiração) aparece como "expected
failure", com o ID no motivo. Atenção:
`test_mensagens.py` e `test_mensagens_turmas.py` (specs 003 e 004) falham enquanto abrirem a US
v3.2, que não existe no repositório (índice Q-77); isso não é efeito desta feature.

## 2. Instalação nova: Coordenadores iniciais (história 6; SC-007, cronometrar)

1. Crie, **fora do repositório**, `coordenadores.csv` com `curso;nome;email;titulacao` e uma linha
   por curso (Engenharia de Computação, Sistemas de Informação, Licenciatura em Computação).
2. `python manage.py criar_coordenadores --arquivo C:\caminho\coordenadores.csv`
   - Esperado: "criado" para os três cursos; nenhum e-mail enviado; nenhum e-mail na saída. Um
     CSV salvo pelo Excel (UTF-8 com BOM) também funciona.
3. Rode o comando de novo. Esperado: os três recusados com "O curso já possui Coordenador..." e
   nenhuma conta duplicada.
4. Com o e-mail de um Coordenador, faça "Primeiro acesso" (spec 003), abra o link do console, crie a
   senha e entre. Esperado: o menu mostra "Docentes", "Secretarias" e "Membros externos".

## 3. Docentes e Secretaria (US-03; SC-008, cronometrar)

1. Em Secretarias, "Nova secretaria" do seu curso → "Secretaria cadastrada com sucesso".
2. Tente outra Secretaria para o mesmo curso → "O curso já possui Secretaria vinculada".
3. Em Docentes, "Cadastrar Docente" com e-mail `@uea.edu.br` → "Docente cadastrado com sucesso",
   status "Aguardando Ativação", 0 orientandos.
4. Repita com `@gmail.com` → "Informe um e-mail institucional (@uea.edu.br)".
5. Troque o filtro de Curso para "Todos" e para um curso sem docentes ("Nenhum registro"); a lista
   atualiza em menos de 2 segundos (SC-009).
6. Edite o e-mail do docente: sem "Sua senha" correta → MC-11; com a senha → MC-12. O console mostra
   o link enviado ao novo e-mail; até abrir o link e clicar em "Confirmar novo e-mail", o login
   continua com o e-mail antigo.

## 4. Inativar e reativar (US-04)

1. Inative um docente sem vínculos → "Deseja inativar o docente NOME?" → "Docente inativado"; o login
   dele responde "Conta inativa".
2. Reative → MC-01 e MC-02; o login volta a funcionar com a senha antiga.
3. Com `criar_conta_teste` e dados criados no shell (turma ativa, orientação de TCC Em Andamento),
   tente inativar → alerta "Não é possível inativar: o docente possui 1 orientandos ou coorientandos
   com TCC ativo e é Professor da Disciplina de 1 turma não arquivada. Encerre ou transfira esses
   vínculos primeiro".
4. Como Coordenador, inative a Secretaria → MC-04; cadastre outra para o curso.

## 5. Membros externos, validade e prorrogação (US-05, US-06, US-50)

1. Cadastre um membro com e-mail de outro domínio → "Membro externo cadastrado com sucesso";
   validade = hoje + 30.
2. Abra `/cadastros/membros-externos/novo/?voltar=/painel/`, salve e confira o retorno com
   `?membro=<id>`.
3. Ponha a validade no passado (shell) e rode `python manage.py expirar_membros_externos`. Esperado:
   status "Expirada" sem tentativa de login (SC-006).
4. "Prorrogar" na linha → "Acesso prorrogado até DD/MM/AAAA" (hoje + 7) e status "Ativa".
5. No shell, crie uma defesa Agendada com o membro na banca e chame
   `services_contas.recalcular_validade(usuario)`. Esperado: data da defesa + 7.

## 6. Conferir o log

`LOG_DIR\acesso.log` deve ter `CONTA_CRIADA`, `CONTA_INATIVADA`, `CONTA_REATIVADA`,
`TROCA_EMAIL_PEDIDA`, `ACESSO_PRORROGADO` e `CONTA_EXPIRADA`, com autor (ou "sistema"), sem e-mail
completo nem senha (FR-047).
