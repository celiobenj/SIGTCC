# Rastreabilidade: diagramas de sequência × código

Correspondência entre os participantes dos diagramas de sequência
([`Diagramas_Sequencia_PlantUML_v2.md`](Diagramas_Sequencia_PlantUML_v2.md)) e o código do SIGTCC
na v0.2.1, para os diagramas do Épico 1 (Cadastro e Manutenção).

- **Telas** (`boundary`): os nomes visíveis (abas, botões, seções e mensagens) seguem as Histórias
  de Usuário v3.4 e os diagramas; a tabela indica o template e a view.
- **Controladores** (`control`): o projeto usa o MVT do Django (PGCS 2.2), com as regras em
  `services*.py`. Os nomes do código não foram trocados pelos dos diagramas; a correspondência fica
  registrada aqui (decisão do hotfix v0.2.1).
- **Entidades** (`entity`): os modelos seguem o dicionário de dados de 18/10 (plural, `db_table`
  explícito), e os diagramas usam o singular.

Os diagramas da Defesa (01 a 06 e 28) e dos Relatórios (23 a 26) serão implementados nos Épicos 2
e 3.

## Telas

| Participante | Template (`sigtcc/templates/`) | View (`sigtcc/apps/cadastro/`) | Diagramas |
|---|---|---|---|
| `:TelaAcesso` | `cadastro/entrar.html`, `primeiro_acesso*.html`, `ativar.html`, `link_vencido.html`, `esqueci_senha.html`, `redefinir_senha.html` | `views.py` | 15, 16 |
| `:TelaAlunoDaTurma` | `cadastro/turmas/painel_aluno.html`, `cadastro/confirmar_reset.html` | `views.py`, `views_orientacao.py` | 15 |
| `:TelaMeuPerfil` | `cadastro/perfil.html`, `alterar_senha.html`, `confirmar_email.html` | `views.py` | 15, 16, 17 |
| `:TelaNotificacoes` | `cadastro/notificacoes.html` | `views.py` | 17 |
| `:TelaCadastroConta`, `:TelaAlteracaoConta` | `cadastro/contas/form_docente.html`, `form_secretaria.html`, `form_membro.html` | `views_contas.py` | 18, 19 |
| `:TelaDocentes` | `cadastro/contas/docentes.html`, `secretarias.html`, `confirmar.html` | `views_contas.py` | 20 |
| `:TelaMembrosExternos` | `cadastro/contas/membros.html` | `views_contas.py` | 21 |
| `:TelaListagem` | listas com o filtro Curso: `contas/docentes.html`, `secretarias.html`, `orientacao/aproveitamento.html` | `views_contas.py`, `views_artigos.py` | 22 |
| `:TelaTurmas` | `cadastro/turmas/lista.html`, `arquivadas.html`, `form_turma.html`, `turma.html`, `confirmar.html` | `views_turmas.py` | 33 |
| `:TelaMatricula` | `cadastro/turmas/matricular.html`, `importar.html`, `previa.html`, `resumo.html`, `editar_aluno.html` | `views_turmas.py` | 35 |
| `:TelaAlunosDaTurma`, `:TelaAlunos` | aba Alunos: `cadastro/turmas/turma.html`; `excluir_aluno.html`, `encerrar.html`, `transferir.html`, `excluidos_transferidos.html` | `views_turmas.py`, `views_orientacao.py` | 09, 36 |
| `:TelaAluno` | `cadastro/turmas/painel_aluno.html`, `cadastro/tcc/homologar_versao_final.html` | `views_orientacao.py`, `views_entregas.py` | 09, 29 |
| `:TelaMeuTCC` | `cadastro/tcc/meu_tcc.html`, `_secao_orientacao.html`, `_coorientadores.html`, `_secao_atas.html`, `_secao_publicacao.html`, `historico_status.html` | `views_tcc.py`, `views_orientacao.py`, `views_artigos.py` | 07, 09, 12, 30 |
| `:TelaEntregas` | aba Entregas: `cadastro/tcc/entregas.html`, `minhas_entregas.html`, `form_entrega.html`, `enviar_entrega.html`, `acompanhamento_entrega.html` | `views_entregas.py` | 09, 10, 11 |
| `:TelaOrientacoes`, `:TelaOrientandos` | `cadastro/orientacao/orientacoes.html`, `ver_proposta.html`, `publicacao.html` | `views_orientacao.py`, `views_artigos.py` | 09, 13, 29, 31 |
| `:TelaAtas` | `cadastro/orientacao/atas.html`, `form_ata.html` | `views_atas.py` | 32 |
| `:TelaAproveitamentoArtigos` | `cadastro/orientacao/aproveitamento.html` | `views_artigos.py` | 30 |

## Controladores e serviços

| Participante | Código (`sigtcc/apps/cadastro/`) |
|---|---|
| `:ControladorAutenticacao` | `services.py`: `autenticar`, `pedir_primeiro_acesso`, `ativar_conta`, `reenviar_link_ativacao`, `alterar_senha`, `enviar_link_redefinicao`, `redefinir_senha`, `resetar_primeiro_acesso`, `expirar_se_vencida` |
| `:ControladorUsuario` | `services_contas.py`: `cadastrar_docente`, `alterar_docente`, `cadastrar_secretaria`, `alterar_secretaria`, `cadastrar_membro`, `alterar_membro`, `inativar_docente`, `reativar_docente`, `inativar_secretaria`, `prorrogar`, `recalcular_validade`; `services.py`: `atualizar_perfil`, `pedir_troca_email` |
| `:ControladorNotificacao`, `:ServicoNotificacao`, `:Controlador` (Notificar) | `services.py`: `notificar`, `abrir_notificacao`, `marcar_todas_lidas`, `enviar_email_apos_commit` |
| `:ServidorEmail` | backend de e-mail do Django (console no ambiente local; SMTP do Brevo em produção, PGCS 3.5) |
| `:ControladorCurso` | `services_contas.py`: `filtro_de_curso`; `permissoes.py`: `curso_id_do_usuario` |
| `:ControladorTurma` | `services_turmas.py`: `criar_turma`, `editar_turma`, `excluir_turma`, `arquivar_turma` |
| `:ControladorMatricula` | `services_turmas.py`: `matricular_individual`, `confirmar_importacao`, `editar_aluno`, `transferir`, `excluir_aluno`, `encerrar_participacao` |
| `:LeitorArquivo` | `importacao.py`: `ler_arquivo`, `montar_previa` |
| `:ControladorTCC` | `services_tcc.py`: `salvar_proposta`, `salvar_alteracoes_tcc`, `historico_do_status`; `services_turmas.py`: `criar_tcc_com_historico`, `atualizar_status_tcc` (diagrama 08); `services_orientacao.py`: `indicar_apto` (diagrama 31) |
| `:ControladorEntregas` | `services_entregas.py`: `cadastrar_entrega`, `enviar_entrega`, `acompanhamento_entrega`, `homologar_versao_final`, `devolver_versao_final`; `services_orientacao.py`: `conferir_correcoes` (diagrama 29, fluxo B) |
| `:ControladorOrientacao` | `services_orientacao.py`: `enviar_pedido`, `cancelar_pedido`, `aceitar_solicitacao`, `recusar_solicitacao`, `registrar_coorientador`, `remover_coorientador`, `remover_convite`, `orientandos` |
| `:ControladorAtas` | `services_atas.py`: `registrar_ata`, `editar_ata`, `comentar_ata` |
| `:ControladorArtigos` | `services_artigos.py`: `salvar_publicacao`, `artigos_para_analise`, `homologar_artigo`, `recusar_artigo` |
| `:ControladorTarefas` | comandos `enviar_lembretes_entrega` e `expirar_membros_externos` (`management/commands/`); o agendamento automático está planejado (PGCS 9.4) |
| `:ControladorBanca`, `:ControladorDefesa` | `services_contas.recalcular_validade` é o ponto de entrada da US-06 para o Épico 2; o restante fica no app `defesa` (planejado) |

## Entidades

| Diagrama | Modelo (dicionário de 18/10) | Diagrama | Modelo (dicionário de 18/10) |
|---|---|---|---|
| `Usuario` | `Usuarios` | `TurmaMarco` | `TurmasMarcos` |
| `Aluno` | `Alunos` | `EntregaMarco` | `EntregasMarcos` |
| `Docente` | `Docentes` | `HistoricoEnvioEntrega` | `HistoricoEnviosEntregas` |
| `Coordenador` | `Coordenadores` | `TCC` | `TCCs` |
| `Secretaria` | `Secretarios` | `AreaInteresse` | `AreasInteresse` |
| `MembroExterno` | `MembrosExternos` | `PalavraChaveTCC` | `PalavrasChaveTCC` |
| `CoorientadorExterno` | `CoorientadoresExternos` | `HistoricoStatusTCC` | `HistoricoStatusTCC` |
| `Turma` | `Turmas` | `Orientacao` | `Orientacoes` |
| `Disciplina` | `Disciplinas` | `Coorientacao` | `Coorientacoes` |
| `Matricula` | `AlunosTurmas` | `SolicitacaoOrientacao` | `SolicitacoesOrientacao` |
| `HistoricoAlunoTurma` | `HistoricoAlunosTurmas` | `EncontroOrientacao` | `EncontroOrientacao` |
| `EquivalenciaCurso` | `EquivalenciaCursos` | `ComentarioEncontro` | `ComentariosEncontro` |
| `Notificacao` | `Notificacoes` | `Artigo` | `Artigos` |
| `Defesa` | `defesa.Defesas` | `BancaDefesa` | `defesa.BancaDefesa` |
| `HistoricoDefesa` | `defesa.HistoricoDefesas` | | |
