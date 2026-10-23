# Contrato: telas e rotas da Gestão de Contas

**Feature**: [../spec.md](../spec.md) | **Pesquisa**: [../research.md](../research.md)

Todas as rotas ficam no namespace `cadastro` (`sigtcc/apps/cadastro/urls.py`) e as views em
`views_contas.py`. Templates em `sigtcc/templates/cadastro/contas/`, estendendo `base.html` (contrato
da spec 003, §1). Ações que gravam são POST com CSRF; GET só exibe. Sem login: tela de login com
`next` (FR-010). Perfil sem permissão: 403 com M-02 (Q9). Fora do curso: 403 com a mensagem do
FR-009, renderizando `acesso_negado.html` com a mensagem (research C21). Rotas com id buscam pela
especialização (`Docentes`, `Secretarios`, `MembrosExternos`): id de outro tipo de conta dá 404
(C22). Toda ação que grava redireciona depois do POST (PRG).

| Rota (nome) | Caminho | Método | Perfis | Template | US / FR |
|---|---|---|---|---|---|
| `contas_docentes` | `/cadastros/docentes/?curso=<id\|todos>` | GET | Secretaria, Coordenador | `contas/docentes.html` | US-03 A7; FR-017 a FR-019 |
| `contas_docente_novo` | `/cadastros/docentes/novo/` | GET, POST | Secretaria, Coordenador | `contas/form_docente.html` | US-03; FR-012 a FR-015 |
| `contas_docente_editar` | `/cadastros/docentes/<doc_id>/editar/` | GET, POST | Secretaria, Coordenador do Curso de Lotação | `contas/form_docente.html` (+ "Sua senha") | US-03 A8 a A11; FR-008, FR-016 |
| `contas_docente_inativar` | `/cadastros/docentes/<doc_id>/inativar/` | GET (verifica e confirma), POST | idem | `contas/confirmar.html` ou alerta na lista | US-04; FR-025 a FR-028 |
| `contas_docente_reativar` | `/cadastros/docentes/<doc_id>/reativar/` | GET (confirma), POST | idem | `contas/confirmar.html` | US-04 A1; FR-029 |
| `contas_secretarias` | `/cadastros/secretarias/?curso=<id\|todos>` | GET | Coordenador (ações), Secretaria (só lista) | `contas/secretarias.html` | US-03 A4; FR-023 |
| `contas_secretaria_nova` | `/cadastros/secretarias/nova/` | GET, POST | Coordenador | `contas/form_secretaria.html` | US-03 A4; FR-020, FR-021 |
| `contas_secretaria_editar` | `/cadastros/secretarias/<sec_id>/editar/` | GET, POST | Coordenador do curso | `contas/form_secretaria.html` | US-03 A5; FR-008, FR-022 |
| `contas_secretaria_inativar` | `/cadastros/secretarias/<sec_id>/inativar/` | GET, POST | Coordenador do curso | `contas/confirmar.html` | US-04 A2; FR-024 |
| `contas_membros` | `/cadastros/membros-externos/` | GET | Orientador, Professor da Disciplina, Secretaria, Coordenador | `contas/membros.html` | US-05, US-50; FR-031, FR-036 |
| `contas_membro_novo` | `/cadastros/membros-externos/novo/?voltar=<caminho interno>` | GET, POST | idem (Professor só com turma não arquivada) | `contas/form_membro.html` | US-05; FR-032 a FR-034 |
| `contas_membro_editar` | `/cadastros/membros-externos/<mem_id>/editar/` | GET, POST | idem | `contas/form_membro.html` (+ "Sua senha") | US-05 A2, A3, A6; FR-008, FR-035 |
| `contas_membro_prorrogar` | `/cadastros/membros-externos/<mem_id>/prorrogar/` | POST | C11 (permissão conferida antes do status) | volta a `contas_membros` (PRG) | US-50; FR-042 a FR-044 |

Rotas da spec 003 reaproveitadas: `cadastro:confirmar_email` (link enviado ao novo e-mail, C7),
`cadastro:entrar` (login, mensagens de conta), `cadastro:primeiro_acesso_email` (ativação das contas
criadas aqui).

## Menu lateral (`menu.py`)

| Rótulo | Ícone | Rota | Perfis | Ordem | Seção |
|---|---|---|---|---|---|
| Docentes | `badge` | `cadastro:contas_docentes` | `secretaria`, `coordenador` | 20 | Cadastros |
| Secretarias | `support_agent` | `cadastro:contas_secretarias` | `secretaria`, `coordenador` | 21 | Cadastros |
| Membros externos | `person_add` | `cadastro:contas_membros` | `orientador`, `professor_disciplina`, `secretaria`, `coordenador` | 22 | Cadastros |

O protótipo de 17/10 junta as três listas em abas de uma tela "Cadastros"; aqui são três páginas
com o mesmo visual (abas como links), porque o JavaScript do protótipo não é reaproveitado. A
Secretaria vê a aba Secretarias só para consulta (FR-023).

## Atalho da banca (FR-034)

`?voltar=` aceita só caminho interno: começa com `/`, passa por `url_has_allowed_host_and_scheme`
e resolve numa rota (`resolve()`). O valor vai num campo oculto e é revalidado no POST. Ao salvar,
redireciona para `voltar` com `membro=<mem_id>` acrescentado à query com `urllib.parse`; ao cancelar,
para `voltar` sem o parâmetro. Valor inválido é ignorado (volta à lista). A tela de destino valida o
membro recebido (contrato de serviços, §3; research C23).
