# Data Model: Acesso e Login do SIGTCC

**Feature**: [spec.md](spec.md) | **Plano**: [plan.md](plan.md) | **Pesquisa**: [research.md](research.md)

Esta feature **não cria tabela nem coluna** (FR-028). Ela lê e grava tabelas da spec 001
(`specs/001-modelo-dados/data-model.md`) e guarda o resto em lugares que não são tabelas de negócio:
cache, links assinados, sessão do framework, arquivo de log e arquivos de assinatura.

## Tabelas usadas

| Tabela (modelo) | Colunas lidas | Colunas gravadas | Onde |
|---|---|---|---|
| `Usuarios` | `usu_id`, `usu_nome`, `usu_email`, `usu_senha` (`password`), `usu_status`, `usu_link_gerado_em` | `usu_email` (primeiro acesso do Aluno, troca de e-mail confirmada, reset); `usu_senha` (ativação, troca, redefinição, reset); `usu_status` (ativação, reset); `usu_link_gerado_em` (cada link de ativação ou de redefinição gerado e o reset; a gravação de senha **não** altera essa coluna, research A3) | US-10, US-11, US-12, US-37, US-38 |
| `Alunos` | `alu_id`, `alu_matricula`, `alu_codigo_curso` | — | login por matrícula, primeiro acesso, perfil |
| `Equivalencia_Cursos` | `eqc_codigo_uea`, `eqc_cur_id` | — | curso do Aluno exibido no perfil (vazia até a Q-17; sem correspondência: "Código não reconhecido", RBN-CAD-05.7) |
| `Docentes` | `doc_id`, `doc_titulacao`, `doc_cur_id`, `doc_assinatura_path` | `doc_assinatura_path` | perfil (US-38); papéis |
| `MembrosExternos` | `mem_id`, `mem_titulacao`, `mem_instituicao`, `mem_assinatura_path`, `mem_validade_ate` | `mem_titulacao`, `mem_instituicao`, `mem_assinatura_path` | perfil (US-38); login, links e primeiro acesso conferem `mem_validade_ate` (Q4, Q26) |
| `Secretarios` | `sec_id`, `sec_cur_id` | — | perfil (só leitura) |
| `Coordenadores` | `cor_cur_id`, `cor_doc_id` | — | papel `coordenador` |
| `Turmas` | `tur_id`, `tur_doc_id`, `tur_status`, `tur_identificador`, `tur_descricao` | — | papel `professor_disciplina` (qualquer turma, Q27); ações que alteram dados exigem turma 'Ativa' (Q27) |
| `Alunos_Turmas` | `mat_alu_id`, `mat_tur_id` | — | "matrícula sem turma" (US-10 E1); aluno da turma do Professor (Q9, Q27) |
| `Orientacoes` | `ori_doc_id`, `ori_status` | — | papel `orientador` |
| `Coorientacoes` | `coo_doc_id`, `coo_status` | — | papel `coorientador` |
| `Cursos` | `cur_id`, `cur_nome` | — | perfil (cursos de lotação e vinculado) |
| `Notificacoes` | `not_id`, `not_usu_id`, `not_mensagem`, `not_link_tela`, `not_data_hora`, `not_lida` | `not_lida` | sino e central (US-38) |

Nenhum identificador é informado em gravação (spec 001, FR-003). Nenhuma `Notificacao` é criada por
esta feature (FR-028); nos testes, as fábricas criam as notificações.

## Regras de dados aplicadas pela aplicação

- **E-mail**: busca e unicidade sem diferenciar maiúsculas (`iexact`, Q13) por
  `services.email_em_uso`; gravação como digitado, com o domínio em minúsculas
  (`services.normalizar_email`); vazio vira `NULL` (spec 001). Aluno: domínio `@uea.edu.br`. Até 100
  caracteres. Gravações em `transaction.atomic()`, com `IntegrityError` tratado como M-05 (research
  A18).
- **Matrícula**: exatamente 10 dígitos (garantido também pelo banco, spec 001).
- **Senha**: 8 a 64 caracteres, ao menos um de `A–Z`/`a–z` e um de `0–9` (Q17); só como hash.
- **Titulação**: um de `Titulacao.values` (spec 001). **Instituição de Origem**: até 150 caracteres.
- **Assinatura**: PNG ou JPEG pelos bytes, extensão coerente, até 2 MB; caminho relativo a
  `MEDIA_ROOT`, até 255 caracteres (research A11).
- **`not_link_tela`** (contrato para quem cria notificações): caminho relativo começando com `/`,
  sem host, query string opcional (research A12).

## Transições do Status da Conta feitas por esta feature

| De | Para | Gatilho | Requisito |
|---|---|---|---|
| Aguardando Ativação | Ativa | senha criada por link de ativação `VALIDO` | FR-005 (US-10) |
| Ativa | Aguardando Ativação | "Resetar primeiro acesso" por Professor da Disciplina com turma ativa do aluno (só Aluno) | FR-015 (US-12; RBN-CAD-06.8; Q27) |
| Aguardando Ativação (com e-mail) | Aguardando Ativação (sem e-mail) | reset antes da ativação | FR-015 |

'Inativa' e 'Expirada' são só lidas (US-04 e US-06, spec 002); o reset não vale para elas (spec Q29). Com `mem_validade_ate` vencida, a
conta é tratada como 'Expirada' sem mudar o status (Q4). Um link nunca tira uma conta de 'Inativa'
ou 'Expirada' (Q26).

## Dados fora das tabelas de negócio

| Dado | Onde fica | Conteúdo | Validade |
|---|---|---|---|
| Contador de senhas incorretas | cache próprio `acesso` (pasta `CACHE_ACESSO_DIR`, ao lado da do cache padrão, até 100.000 entradas) | `acesso:falhas:<usu_id>` → inteiro | zera na senha correta e no bloqueio; tempo de vida de 24 h só para limpeza |
| Bloqueio | cache `acesso` | `acesso:bloqueio:<usu_id>` → instante do fim (ISO) | comparado com `timezone.now()`; tempo de vida de 16 min só para limpeza |
| Link de ativação | assinado, na URL (e depois na sessão) | `usu_id`, `gerado_em` (salt `sigtcc.ativacao`) | 24 h; substituído se `usu_link_gerado_em` mudar |
| Link de redefinição | assinado, na URL (e depois na sessão) | `usu_id`, `gerado_em`, `resumo_senha` (salt `sigtcc.redefinicao`) | 24 h; substituído se `usu_link_gerado_em` mudar; usado quando a senha muda |
| Link de troca de e-mail | assinado, na URL | `usu_id`, `resumo_email_atual`, `novo_email`, `emitido_em` (salt `sigtcc.troca_email`) | 24 h; inválido se o e-mail da conta mudou (A4; spec Q24) |
| Sessão | `django_session` (framework) | usuário, resumo da senha e, durante a ativação ou a redefinição, o token (removido ao terminar; sem ele, a tela trata como `ADULTERADO`) | 60 min sem uso; fim ao fechar o navegador (Q18) |
| Eventos de acesso | `LOG_DIR/acesso.log` (fora do Git) | data e hora, evento, conta, autor, detalhe sem dados sensíveis | rotação de 5 × 5 MB (A13) |
| Imagens de assinatura | `MEDIA_ROOT/assinaturas/` (fora do Git, sem URL pública) | arquivo PNG ou JPEG | substituído a cada envio (A11) |

## Estados de um link de ativação (FR-016; Q5, Q23, Q26)

Avaliados nesta ordem, no GET e de novo no POST (com a conta travada, research A17):

| # | Estado | Condição | Tela ou mensagem |
|---|---|---|---|
| 0 | `ADULTERADO` | assinatura inválida | "Link inválido. Use o link mais recente enviado ao seu e-mail" (Q23) |
| 1 | `ATIVA` | conta 'Ativa' | "Esta conta já está ativa" e ida para o login |
| 2 | `INATIVA` | conta 'Inativa' | "Conta inativa" (M-15; Q26) |
| 3 | `EXPIRADA` | conta 'Expirada' ou Membro Externo com a validade vencida | "Seu acesso expirou. Procure o Orientador, o Professor da Disciplina, a Secretaria ou o Coordenador de Curso" (M-16; Q26) |
| 4 | `SEM_EMAIL` | conta sem e-mail (resetada) | tela de vencido com o botão; o clique mostra a M-08 |
| 5 | `SUBSTITUIDO` | `gerado_em` ≠ `usu_link_gerado_em` | "Link inválido. Use o link mais recente enviado ao seu e-mail" |
| 6 | `VENCIDO` | mais de 24 h desde `gerado_em` | "Este link de ativação venceu" e o botão "Reenviar link de ativação" |
| 7 | `VALIDO` | conta 'Aguardando Ativação' | formulário de ativação |

## Estados de um link de redefinição (FR-014; Q26)

`ADULTERADO` → `INATIVA` (M-15) → `EXPIRADA` (M-16) → `SUBSTITUIDO` (outro link gerado, senha já
trocada ou conta resetada) → `VENCIDO` → `VALIDO` (conta 'Ativa' e validade em dia). `ADULTERADO`,
`SUBSTITUIDO` e `VENCIDO` mostram "Link inválido ou vencido. Solicite um novo".
