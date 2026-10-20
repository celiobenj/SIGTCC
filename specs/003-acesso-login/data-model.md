# Data Model: Acesso e Login do SIGTCC

**Feature**: [spec.md](spec.md) | **Plano**: [plan.md](plan.md) | **Pesquisa**: [research.md](research.md)

Esta feature **não cria tabela nem coluna** (FR-028). Ela lê e grava tabelas da spec 001
(`specs/001-modelo-dados/data-model.md`) e guarda o resto em lugares que não são tabelas de negócio:
cache, links assinados, sessão do framework e arquivo de log.

## Tabelas usadas

| Tabela (modelo) | Colunas lidas | Colunas gravadas | Onde |
|---|---|---|---|
| `Usuarios` (`Usuarios`) | `usu_id`, `usu_nome`, `usu_email`, `usu_senha` (`password`), `usu_status`, `usu_link_gerado_em` | `usu_email` (primeiro acesso do Aluno, troca de e-mail confirmada, reset), `usu_senha` (ativação, troca, redefinição, reset), `usu_status` (ativação, reset), `usu_link_gerado_em` (cada link de ativação ou redefinição gerado, cada senha gravada, reset) | US-10, US-11, US-12, US-37, US-38 |
| `Alunos` | `alu_id`, `alu_matricula`, `alu_codigo_curso` | — | login por matrícula, primeiro acesso, perfil (só leitura) |
| `Docentes` | `doc_id`, `doc_titulacao`, `doc_cur_id`, `doc_assinatura_path` | `doc_assinatura_path` | perfil (US-38) |
| `MembrosExternos` | `mem_id`, `mem_titulacao`, `mem_instituicao`, `mem_assinatura_path`, `mem_validade_ate` | `mem_titulacao`, `mem_instituicao`, `mem_assinatura_path` | perfil (US-38); login e primeiro acesso conferem `mem_validade_ate` (Q4) |
| `Secretarios` | `sec_id`, `sec_cur_id` | — | perfil (só leitura) |
| `Coordenadores` | `cor_cur_id`, `cor_doc_id` | — | papel `coordenador` (permissões, menu) |
| `Turmas` | `tur_id`, `tur_doc_id`, `tur_status`, `tur_identificador`, `tur_descricao` | — | papel `professor_disciplina`; quem pode resetar (Q9) |
| `Alunos_Turmas` | `mat_alu_id`, `mat_tur_id` | — | "matrícula sem turma" (US-10 E1); aluno da turma do Professor (Q9) |
| `Orientacoes` | `ori_doc_id`, `ori_status` | — | papel `orientador` |
| `Coorientacoes` | `coo_doc_id`, `coo_status` | — | papel `coorientador` |
| `Cursos` | `cur_id`, `cur_nome` | — | perfil (curso de lotação, curso vinculado) |
| `Notificacoes` | `not_id`, `not_usu_id`, `not_mensagem`, `not_link_tela`, `not_data_hora`, `not_lida` | `not_lida` | sino e central (US-38) |

Nenhum identificador é informado em gravação (spec 001, FR-003). Nenhuma `Notificacao` é criada
por esta feature (FR-028); nos testes, elas são criadas pelas fábricas.

## Regras de dados aplicadas pela aplicação

- **E-mail**: comparação e unicidade sem diferenciar maiúsculas (`iexact`, Q13); gravado como
  digitado, com o domínio em minúsculas (`normalize_email`, spec 001); vazio vira `NULL` (spec 001).
  Aluno: domínio `@uea.edu.br`. Até 100 caracteres.
- **Matrícula**: exatamente 10 dígitos (já garantido pelo banco, spec 001).
- **Senha**: 8 a 64 caracteres, ao menos um de `A–Z`/`a–z` e um de `0–9` (Q17); gravada só como hash.
- **Titulação**: um de `Titulacao.values` (spec 001). **Instituição de Origem**: até 150 caracteres.
- **Assinatura**: PNG ou JPG, até 2 MB; o caminho gravado tem até 255 caracteres (A11).

## Transições do Status da Conta feitas por esta feature

| De | Para | Gatilho | Requisito |
|---|---|---|---|
| Aguardando Ativação | Ativa | senha criada pelo link de ativação válido | FR-005 (US-10) |
| Ativa | Aguardando Ativação | "Resetar primeiro acesso" pelo Professor da Disciplina (só Aluno) | FR-015 (US-12; RBN-CAD-06.8) |
| Aguardando Ativação (com e-mail) | Aguardando Ativação (sem e-mail) | reset antes da ativação | FR-015 |

'Inativa' e 'Expirada' são só lidas aqui (US-04 e US-06, spec 002). Com `mem_validade_ate` vencida,
a conta é tratada como 'Expirada' sem mudar o status (Q4).

## Dados fora das tabelas de negócio

| Dado | Onde fica | Conteúdo | Validade |
|---|---|---|---|
| Contador de senhas incorretas | cache em arquivo (`CACHE_DIR`) | `acesso:falhas:<usu_id>` → inteiro | 24 h (só limpeza); zera na senha correta e no bloqueio |
| Bloqueio | cache em arquivo | `acesso:bloqueio:<usu_id>` → instante do fim | 15 min |
| Link de ativação | assinado, dentro da URL | `usu_id`, `gerado_em` (salt `sigtcc.ativacao`) | 24 h; substituído se `usu_link_gerado_em` mudar |
| Link de redefinição | assinado, dentro da URL | `usu_id`, `gerado_em` (salt `sigtcc.redefinicao`) | 24 h; inválido depois de usado (a senha nova atualiza `usu_link_gerado_em`) |
| Link de troca de e-mail | assinado, dentro da URL | `usu_id`, `email_atual`, `novo_email`, `emitido_em` (salt `sigtcc.troca_email`) | 24 h; inválido se o e-mail da conta mudou (proposta A4, Q-21) |
| Sessão | tabela `django_session` (framework) | usuário e resumo da senha | 60 min sem uso; fim ao fechar o navegador (Q18) |
| Eventos de acesso | `LOG_DIR/acesso.log` (fora do Git) | data e hora, evento, conta, autor, detalhe sem dados sensíveis | rotação de 5 × 5 MB (A13) |
| Imagens de assinatura | `media/assinaturas/` (fora do Git) | arquivo PNG ou JPG | substituído a cada envio |

## Estados de um link de ativação (FR-016; Q5)

Avaliados nesta ordem; o primeiro que se aplica define a tela:

1. Assinatura inválida ou adulterada → "Link inválido. Use o link mais recente enviado ao seu e-mail".
2. Conta 'Ativa' → "Esta conta já está ativa" e ida para o login.
3. Conta sem e-mail (resetada) → tela de vencido com o botão; o clique mostra a M-08.
4. `gerado_em` ≠ `usu_link_gerado_em` → "Link inválido. Use o link mais recente enviado ao seu e-mail".
5. Mais de 24 h desde `gerado_em` → "Este link de ativação venceu" e o botão "Reenviar link de ativação".
6. Senão → formulário de ativação.

O item 1 (assinatura adulterada) não está na spec; a proposta é usar o mesmo texto do item 4, porque
nos dois casos o link não é o mais recente válido. Decisão pendente com a Julia (Q-24 do índice).
