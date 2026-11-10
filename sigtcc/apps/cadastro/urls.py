"""Rotas do app cadastro (specs/003-acesso-login/contracts/rotas.md, specs/004 e specs/002).

[US-10][US-11][US-12][US-37][US-38][FR-025][US-03][US-04][US-05][US-50]
"""

from django.urls import path

from sigtcc.apps.cadastro import (
    views,
    views_artigos,
    views_atas,
    views_contas,
    views_entregas,
    views_orientacao,
    views_painel,
    views_tcc,
    views_turmas,
)

app_name = "cadastro"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("entrar/", views.entrar, name="entrar"),
    path("sair/", views.sair, name="sair"),
    path("primeiro-acesso/", views.primeiro_acesso, name="primeiro_acesso"),
    path("primeiro-acesso/aluno/", views.primeiro_acesso_aluno, name="primeiro_acesso_aluno"),
    path("primeiro-acesso/email/", views.primeiro_acesso_email, name="primeiro_acesso_email"),
    path("primeiro-acesso/ativar/<str:token>/", views.ativar, name="ativar"),
    path("primeiro-acesso/definir-senha/", views.definir_senha, name="definir_senha"),
    path("primeiro-acesso/reenviar/", views.reenviar_link, name="reenviar_link"),
    path("esqueci-minha-senha/", views.esqueci_senha, name="esqueci_senha"),
    path("redefinir-senha/nova/", views.nova_senha, name="nova_senha"),
    path("redefinir-senha/<str:token>/", views.redefinir_senha, name="redefinir_senha"),
    path("painel/", views.painel, name="painel"),
    path("perfil/", views.perfil, name="perfil"),
    path("perfil/assinatura/", views.assinatura, name="assinatura"),
    path("perfil/senha/", views.alterar_senha, name="alterar_senha"),
    path("perfil/email/confirmar/<str:token>/", views.confirmar_email, name="confirmar_email"),
    path("notificacoes/", views.notificacoes, name="notificacoes"),
    path("notificacoes/marcar-lidas/", views.marcar_lidas, name="marcar_lidas"),
    path("notificacoes/<int:not_id>/", views.abrir_notificacao, name="abrir_notificacao"),
    path("alunos/<int:alu_id>/", views.aluno, name="aluno"),
    path(
        "alunos/<int:alu_id>/resetar-primeiro-acesso/",
        views.resetar_primeiro_acesso,
        name="resetar_primeiro_acesso",
    ),
    # Spec 004: turmas (contracts/rotas.md). [US-07][US-08][US-09]
    path("turmas/", views_turmas.turmas, name="turmas"),
    path("turmas/arquivadas/", views_turmas.turmas_arquivadas, name="turmas_arquivadas"),
    path("turmas/nova/", views_turmas.turma_nova, name="turma_nova"),
    path("turmas/<int:tur_id>/", views_turmas.turma, name="turma"),
    path("turmas/<int:tur_id>/editar/", views_turmas.turma_editar, name="turma_editar"),
    path("turmas/<int:tur_id>/excluir/", views_turmas.turma_excluir, name="turma_excluir"),
    path("turmas/<int:tur_id>/arquivar/", views_turmas.turma_arquivar, name="turma_arquivar"),
    path("turmas/<int:tur_id>/matricular/", views_turmas.matricular, name="matricular"),
    path("turmas/<int:tur_id>/importar/", views_turmas.importar, name="importar"),
    path(
        "turmas/<int:tur_id>/importar/confirmar/",
        views_turmas.importar_confirmar,
        name="importar_confirmar",
    ),
    path(
        "turmas/<int:tur_id>/importar/resumo/",
        views_turmas.importar_resumo,
        name="importar_resumo",
    ),
    path(
        "turmas/<int:tur_id>/importar/cancelar/",
        views_turmas.importar_cancelar,
        name="importar_cancelar",
    ),
    path(
        "turmas/modelo-importacao.csv",
        views_turmas.modelo_importacao,
        name="modelo_importacao",
    ),
    path(
        "turmas/<int:tur_id>/alunos/<int:alu_id>/editar/",
        views_turmas.aluno_editar,
        name="aluno_editar",
    ),
    path(
        "turmas/<int:tur_id>/alunos/<int:alu_id>/transferir/",
        views_turmas.aluno_transferir,
        name="aluno_transferir",
    ),
    path(
        "turmas/<int:tur_id>/alunos/<int:alu_id>/excluir/",
        views_turmas.aluno_excluir,
        name="aluno_excluir",
    ),
    path(
        "turmas/<int:tur_id>/alunos/<int:alu_id>/encerrar/",
        views_turmas.aluno_encerrar,
        name="aluno_encerrar",
    ),
    path(
        "turmas/<int:tur_id>/excluidos-transferidos/",
        views_turmas.excluidos_transferidos,
        name="excluidos_transferidos",
    ),
    # Spec 005: fluxo do TCC e entregas (contracts/rotas.md). [US-13][US-14]
    # Spec 005: item "Turmas" do Aluno (contracts/rotas.md; FR-031, Q-89). [US-13][US-15]
    path("minhas-turmas/", views_tcc.minhas_turmas, name="minhas_turmas"),
    path(
        "minhas-turmas/arquivadas/",
        views_tcc.minhas_turmas_arquivadas,
        name="minhas_turmas_arquivadas",
    ),
    path("turmas/<int:tur_id>/meu-tcc/", views_tcc.meu_tcc, name="meu_tcc"),
    path(
        "turmas/<int:tur_id>/meu-tcc/historico/",
        views_tcc.historico_status_aluno,
        name="historico_status_aluno",
    ),
    path(
        "turmas/<int:tur_id>/alunos/<int:alu_id>/historico/",
        views_tcc.historico_status,
        name="historico_status",
    ),
    path("turmas/<int:tur_id>/entregas/", views_entregas.entregas, name="entregas"),
    path(
        "turmas/<int:tur_id>/entregas/nova/",
        views_entregas.entrega_cadastrar,
        name="entrega_cadastrar",
    ),
    # Spec 005: acompanhamento da entrega pelo Professor (contracts/rotas.md). [US-16]
    path(
        "turmas/<int:tur_id>/entregas/<int:tma_id>/",
        views_entregas.entrega_acompanhar,
        name="entrega_acompanhar",
    ),
    # Spec 005: envio e substituição do link pelo Aluno (contracts/rotas.md). [US-15]
    path(
        "turmas/<int:tur_id>/minhas-entregas/",
        views_entregas.minhas_entregas,
        name="minhas_entregas",
    ),
    path(
        "turmas/<int:tur_id>/minhas-entregas/<int:tma_id>/",
        views_entregas.entrega_enviar,
        name="entrega_enviar",
    ),
    # Spec 005: homologação ou devolução da Versão Final (contracts/rotas.md). [US-44]
    path(
        "turmas/<int:tur_id>/alunos/<int:alu_id>/versao-final/",
        views_entregas.aluno_versao_final,
        name="aluno_versao_final",
    ),
    # Spec 002: Gestão de Contas (specs/002-gestao-contas/contracts/rotas.md). [US-03]
    path("cadastros/docentes/", views_contas.docentes, name="contas_docentes"),
    path("cadastros/docentes/novo/", views_contas.docente_novo, name="contas_docente_novo"),
    path(
        "cadastros/docentes/<int:doc_id>/editar/",
        views_contas.docente_editar,
        name="contas_docente_editar",
    ),
    # [US-04]
    path(
        "cadastros/docentes/<int:doc_id>/inativar/",
        views_contas.docente_inativar,
        name="contas_docente_inativar",
    ),
    path(
        "cadastros/docentes/<int:doc_id>/reativar/",
        views_contas.docente_reativar,
        name="contas_docente_reativar",
    ),
    path("cadastros/secretarias/", views_contas.secretarias, name="contas_secretarias"),
    path(
        "cadastros/secretarias/nova/",
        views_contas.secretaria_nova,
        name="contas_secretaria_nova",
    ),
    path(
        "cadastros/secretarias/<int:sec_id>/editar/",
        views_contas.secretaria_editar,
        name="contas_secretaria_editar",
    ),
    path(
        "cadastros/secretarias/<int:sec_id>/inativar/",
        views_contas.secretaria_inativar,
        name="contas_secretaria_inativar",
    ),
    # [US-05]
    path("cadastros/membros-externos/", views_contas.membros, name="contas_membros"),
    path(
        "cadastros/membros-externos/novo/",
        views_contas.membro_novo,
        name="contas_membro_novo",
    ),
    path(
        "cadastros/membros-externos/<int:mem_id>/editar/",
        views_contas.membro_editar,
        name="contas_membro_editar",
    ),
    # [US-50]
    path(
        "cadastros/membros-externos/<int:mem_id>/prorrogar/",
        views_contas.membro_prorrogar,
        name="contas_membro_prorrogar",
    ),
    # Spec 006: seção Orientação do Aluno (contracts/rotas.md §1). [US-17][US-45]
    path(
        "turmas/<int:tur_id>/meu-tcc/orientacao/pedido/",
        views_orientacao.enviar_pedido_orientacao,
        name="enviar_pedido_orientacao",
    ),
    path(
        "turmas/<int:tur_id>/meu-tcc/orientacao/pedido/cancelar/",
        views_orientacao.cancelar_pedido_orientacao,
        name="cancelar_pedido_orientacao",
    ),
    # Spec 006: painel do aluno (contracts/rotas.md §3). [US-41]
    path(
        "turmas/<int:tur_id>/alunos/<int:alu_id>/",
        views_painel.painel_aluno,
        name="painel_aluno",
    ),
    path(
        "turmas/<int:tur_id>/alunos/<int:alu_id>/atas/",
        views_atas.atas_painel,
        name="atas_painel",
    ),
    # Spec 006: coorientadores do Aluno (contracts/rotas.md §1, rotas 3 a 6). [US-45]
    path(
        "turmas/<int:tur_id>/meu-tcc/coorientadores/novo/",
        views_orientacao.registrar_coorientador,
        name="registrar_coorientador",
    ),
    path(
        "turmas/<int:tur_id>/meu-tcc/coorientadores/<int:coo_id>/substituir/",
        views_orientacao.substituir_coorientador,
        name="substituir_coorientador",
    ),
    path(
        "turmas/<int:tur_id>/meu-tcc/coorientadores/<int:coo_id>/remover/",
        views_orientacao.remover_coorientador,
        name="remover_coorientador",
    ),
    path(
        "turmas/<int:tur_id>/meu-tcc/convites/<int:sol_id>/remover/",
        views_orientacao.remover_convite_coorientacao,
        name="remover_convite_coorientacao",
    ),
    # Spec 006: atas do Aluno (contracts/rotas.md §1, rotas 7 a 9). [US-19]
    path("turmas/<int:tur_id>/meu-tcc/atas/", views_atas.minhas_atas, name="minhas_atas"),
    path(
        "turmas/<int:tur_id>/meu-tcc/atas/nova/",
        views_atas.registrar_ata_aluno,
        name="registrar_ata_aluno",
    ),
    path(
        "turmas/<int:tur_id>/meu-tcc/atas/<int:enc_id>/editar/",
        views_atas.editar_ata_aluno,
        name="editar_ata_aluno",
    ),
    # Spec 006: publicação do Aluno (contracts/rotas.md §1, rota 10). [US-46]
    path(
        "turmas/<int:tur_id>/meu-tcc/publicacao/",
        views_artigos.salvar_publicacao_aluno,
        name="salvar_publicacao_aluno",
    ),
    # Spec 006: aproveitamento de artigos do Coordenador (contracts/rotas.md §4). [US-20]
    path("artigos/", views_artigos.aproveitamento_artigos, name="aproveitamento_artigos"),
    path(
        "artigos/<int:tcc_id>/homologar/",
        views_artigos.homologar_artigo,
        name="homologar_artigo",
    ),
    path("artigos/<int:tcc_id>/recusar/", views_artigos.recusar_artigo, name="recusar_artigo"),
    # Spec 006: tela Orientações do docente (contracts/rotas.md §2). [US-18][US-36]
    path("orientacoes/", views_orientacao.orientacoes, name="orientacoes"),
    path(
        "orientacoes/solicitacoes/<int:sol_id>/aceitar/",
        views_orientacao.aceitar_solicitacao,
        name="aceitar_solicitacao",
    ),
    path(
        "orientacoes/solicitacoes/<int:sol_id>/recusar/",
        views_orientacao.recusar_solicitacao,
        name="recusar_solicitacao",
    ),
    path(
        "orientacoes/solicitacoes/<int:sol_id>/proposta/",
        views_orientacao.ver_proposta,
        name="ver_proposta",
    ),
    path(
        "orientacoes/tcc/<int:tcc_id>/atas/",
        views_atas.atas_orientando,
        name="atas_orientando",
    ),
    path(
        "orientacoes/tcc/<int:tcc_id>/atas/nova/",
        views_atas.registrar_ata_docente,
        name="registrar_ata_docente",
    ),
    path(
        "orientacoes/tcc/<int:tcc_id>/atas/<int:enc_id>/editar/",
        views_atas.editar_ata_docente,
        name="editar_ata_docente",
    ),
    path(
        "orientacoes/tcc/<int:tcc_id>/atas/<int:enc_id>/comentar/",
        views_atas.comentar_ata,
        name="comentar_ata",
    ),
    path(
        "orientacoes/tcc/<int:tcc_id>/publicacao/",
        views_artigos.publicacao_orientando,
        name="publicacao_orientando",
    ),
    path(
        "orientacoes/tcc/<int:tcc_id>/apto/",
        views_orientacao.indicar_apto,
        name="indicar_apto",
    ),
    path(
        "orientacoes/tcc/<int:tcc_id>/historico/",
        views_orientacao.historico_orientando,
        name="historico_orientando",
    ),
    path(
        "orientacoes/tcc/<int:tcc_id>/correcoes-conferidas/",
        views_orientacao.correcoes_conferidas,
        name="correcoes_conferidas",
    ),
    path(
        "orientacoes/pedidos/<int:sol_id>/",
        views_orientacao.pedido_orientacao,
        name="pedido_orientacao",
    ),
    path(
        "orientacoes/convites/<int:sol_id>/",
        views_orientacao.convite_coorientacao,
        name="convite_coorientacao",
    ),
]
