"""Apoio aos testes da feature 005: Proposta, entregas e envios de link em memória.

Só usa os modelos (não depende de services_tcc nem de services_entregas), para os testes poderem
vir antes do código, no mesmo padrão de apoio_turmas.py (spec 004). Constrói sobre
`apoio_turmas.criar_turma_de`/`matricular_aluno`.

[infraestrutura de teste da feature 005][research C8]
"""

from django.utils import timezone

from sigtcc.apps.cadastro.choices import ModalidadeTCC, StatusEntrega, TipoEntrega
from sigtcc.apps.cadastro.models import EntregasMarcos, HistoricoEnviosEntregas, TurmasMarcos
from sigtcc.apps.cadastro.tests.apoio_turmas import proximo


def salvar_proposta(tcc, titulo="Título do trabalho", resumo="Resumo do trabalho", **dados):
    """Grava a Proposta direto no TCC (sem passar por services_tcc.salvar_proposta, ainda não
    implementado nesta fase) — só o suficiente para montar o cenário de um teste.
    [US-13][RBN-CAD-07.1]
    """
    tcc.tcc_titulo = titulo
    tcc.tcc_resumo = resumo
    tcc.tcc_modalidade = dados.get("modalidade", ModalidadeTCC.MONOGRAFIA)
    tcc.tcc_subtitulo = dados.get("subtitulo")
    tcc.tcc_link_proposta = dados.get("link_proposta")
    tcc.save(
        update_fields=[
            "tcc_titulo",
            "tcc_resumo",
            "tcc_modalidade",
            "tcc_subtitulo",
            "tcc_link_proposta",
        ]
    )
    return tcc


def cadastrar_entrega(turma, tipo=TipoEntrega.OUTRA, titulo=None, data_limite=None):
    """Entrega (Turmas_Marcos) cadastrada na turma, sem os registros dos alunos (quem precisar
    deles usa entrega_do_aluno/apoio_turmas ou o próprio serviço de cadastro). [US-43][RBN-CAD-09.1]
    """
    return TurmasMarcos.objects.create(
        tma_tur=turma,
        tma_tipo=tipo,
        tma_titulo=titulo or f"Entrega {proximo()}",
        tma_data_limite=data_limite or timezone.now(),
    )


def enviar_link(entrega, aluno, link, quando=None):
    """Registra um envio (ou substituição) do link desta entrega pelo aluno, na data pedida —
    para controlar, nos testes de prazo, a diferença entre "Entregue" e "Entregue com Atraso"
    sem depender do relógio real. Cria o registro de Entregas_Marcos do aluno se não existir
    ainda (`get_or_create`, sem calcular ent_status: quem testa a regra do cálculo é
    services_entregas.enviar_entrega, não esta fábrica). [US-15][US-29][RBN-CAD-09.2]
    """
    registro, _ = EntregasMarcos.objects.get_or_create(
        ent_tma=entrega, ent_alu=aluno, defaults={"ent_status": StatusEntrega.AGUARDANDO_ENVIO}
    )
    return HistoricoEnviosEntregas.objects.create(
        hen_ent=registro, hen_link=link, hen_data_envio=quando or timezone.now()
    )
