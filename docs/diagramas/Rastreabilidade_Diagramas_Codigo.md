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
e 3. A spec 008 (Avaliação e Resultados) acrescentou abaixo os participantes dos diagramas 04
(`AvaliarCriterios`) e 28 (`LiberarResultadoDefesa`), com o código do app `defesa`. A spec 009
(Documentação e Encerramento) acrescentou os do diagrama 05 (`RegistrarOuvintesAgenda`) e
completou o `:GeradorDocumentosPDF` do diagrama 28.

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
| `:TelaAvaliacao` (spec 008) | `defesa/avaliacao.html`, `defesa/criterios.html`, `defesa/minhas_bancas.html` | `defesa/views_avaliacoes.py` (`avaliacao`, `reabrir`, `assinatura`, `criterios`, `minhas_bancas`) | 04 |
| `:TelaSessaoDefesa` (spec 008) | `defesa/sessao.html` com `_bloco_avaliacao.html` e `_bloco_resultado.html`; `defesa/confirmar_liberacao.html`; `defesa/_resultado_aluno.html` (aba Meu TCC) | `defesa/views_defesa.py` (`sessao`), `defesa/views_avaliacoes.py` (`registrar_parecer`, `liberar_resultado`) | 28 |
| `:TelaSessaoDefesa` (spec 009) | blocos `_bloco_documentos.html`, `_bloco_ouvintes.html` e `_bloco_ocorrencias.html` de `defesa/sessao.html`; `defesa/_documentos_aluno.html` (aba Meu TCC); PDFs `defesa/pdf/ata_final.html`, `folha_aprovacao.html` e `declaracao.html` | `defesa/views_documentos.py` (`ata_final`, `folha_aprovacao`, `declaracao`) | 28 |
| `:TelaDefesas` (spec 009, diagrama 05) | `defesa/form_ouvintes.html` (com `static/js/ouvintes.js`), `defesa/form_ocorrencias.html`, `defesa/ouvintes_das_defesas.html`, botão "Agenda de defesas (PDF)" de `defesa/defesas.html` e o PDF `defesa/pdf/agenda.html` | `defesa/views_ouvintes.py` (`ouvintes`, `ocorrencias`, `ouvintes_das_defesas`), `defesa/views_documentos.py` (`agenda`) | 05 |

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
| `:ControladorAvaliacao` (spec 008) | `defesa/services_avaliacoes.py`: `salvar_rascunho`, `enviar_avaliacao`, `reabrir_avaliacao`, `criterios_liberados`, `nota_individual`, `estado_da_avaliacao`, `estados_da_banca`, `descartar_avaliacoes`, `voltar_envios_a_rascunho`, `minhas_bancas` |
| `:ControladorResultado` (spec 008) | `defesa/services_avaliacoes.py`: `apuracao`, `nota_final`, `parecer_automatico`, `registrar_parecer`, `liberar_resultado`, `visao_da_avaliacao`, `resultado_da_sessao`, `resultado_para_o_aluno`; a sessão muda só por `services_defesa.transicionar_status` e o TCC por `services_turmas.atualizar_status_tcc` |
| `:ControladorResultado` (spec 009) | `defesa/services_documentos.py`: `avisar_pendencia_da_ata` (E2 da US-28 depois do commit da liberação, chamada por `views_avaliacoes.liberar_resultado`) |
| `:GeradorDocumentosPDF` (specs 008 e 009) | `defesa/pdf.py`: `gerar_pdf` (com a trava de módulo `_TRAVA_PDF`), `resposta_pdf` (PDF sob demanda, em memória, nunca gravado); `defesa/services_documentos.py`: `situacao_da_ata`, `dados_da_ata`, `dados_da_folha`, `folha_aplicavel`, `dados_da_declaracao`, `codigo_de_validacao`, `agenda_de_defesas`, `visao_dos_documentos`, `documentos_do_aluno`, `ao_liberar_resultado` (envio das declarações por e-mail) e `declaracao_disponivel` |
| `:ControladorEventosDefesa` (spec 009, diagrama 05) | `defesa/services_ouvintes.py`: `salvar_ouvintes`, `ouvintes_da_sessao`, `registrar_ocorrencias`, `visao_da_sessao`, `ouvintes_das_defesas`; `defesa/forms_ouvintes.py`: `OuvintesFormSet`, `OcorrenciasForm`; permissões em `defesa/permissoes_defesa.py` (`pode_editar_ouvintes`, `pode_ver_ouvintes`, `pode_editar_ocorrencias`, `pode_ver_ocorrencias`, `pode_gerar_agenda`, `pode_ver_ouvintes_das_defesas`) |

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
| `HistoricoDefesa` | `defesa.HistoricoDefesas` | `Avaliacao` (spec 008) | `defesa.Avaliacoes` |
| `Criterio` (spec 008) | `defesa.Criterios` | `Ouvinte` (spec 009) | `defesa.Ouvintes` e `defesa.PresencaOuvintes` |
