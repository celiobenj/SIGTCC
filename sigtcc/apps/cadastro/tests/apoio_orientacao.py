"""Apoio aos testes da feature 006: pedidos, convites, orientações, coorientações, atas,
comentários, artigos, liberação do resultado e agendamento de defesa.

Só usa os modelos (não depende de services_orientacao, services_atas nem services_artigos), para
os testes poderem vir antes do código, no mesmo padrão de apoio_turmas.py e apoio_tcc.py.

[infraestrutura de teste da feature 006] (tasks T006)
"""

from django.utils import timezone

from sigtcc.apps.cadastro.choices import (
    GatilhoStatusTCC,
    OrigemOrientacao,
    StatusCoorientacao,
    StatusOrientacao,
    StatusSolicitacao,
    StatusTCC,
    TipoSolicitacao,
)
from sigtcc.apps.cadastro.models import (
    Artigos,
    ComentariosEncontro,
    Coorientacoes,
    CoorientadoresExternos,
    EncontroOrientacao,
    HistoricoStatusTCC,
    Orientacoes,
    SolicitacoesOrientacao,
)
from sigtcc.apps.cadastro.tests.apoio_turmas import proximo
from sigtcc.apps.defesa.choices import EventoDefesa, StatusSessao
from sigtcc.apps.defesa.models import HistoricoDefesas


def criar_pedido(tcc, docente, tipo=TipoSolicitacao.ORIENTACAO, quando=None):
    """Pedido de Orientação ou de Troca de Orientação 'Aguardando Resposta'. [US-17][RBN-CAD-10.1]

    `docente` é o Usuarios do docente.
    """
    return SolicitacoesOrientacao.objects.create(
        sol_tcc=tcc,
        sol_doc=docente.docentes,
        sol_tipo=tipo,
        sol_status=StatusSolicitacao.AGUARDANDO_RESPOSTA,
        sol_data_solicitacao=quando or timezone.now(),
    )


def criar_convite(tcc, docente, quando=None):
    """Convite de coorientação 'Aguardando Aceite'. [US-45][RBN-CAD-10.4]"""
    return SolicitacoesOrientacao.objects.create(
        sol_tcc=tcc,
        sol_doc=docente.docentes,
        sol_tipo=TipoSolicitacao.COORIENTACAO,
        sol_status=StatusSolicitacao.AGUARDANDO_ACEITE,
        sol_data_solicitacao=quando or timezone.now(),
    )


def vincular_orientador(tcc, docente, origem=OrigemOrientacao.PEDIDO_ACEITO, quando=None):
    """Orientação 'Ativa' do docente no TCC. [US-18][RBN-CAD-10.2]"""
    return Orientacoes.objects.create(
        ori_tcc=tcc,
        ori_doc=docente.docentes,
        ori_origem=origem,
        ori_status=StatusOrientacao.ATIVA,
        ori_data_inicio=quando or timezone.now(),
    )


def criar_externo(nome=None, email=None, instituicao=None):
    """Coorientador externo ao NUCOMP, sem conta. [US-45][RBN-CAD-10.3]"""
    return CoorientadoresExternos.objects.create(
        cext_nome=nome or f"Externo Teste {proximo()}",
        cext_email=email,
        cext_instituicao=instituicao,
    )


def vincular_coorientador(tcc, docente=None, externo=None, quando=None):
    """Coorientação 'Ativa' de um docente do NUCOMP (Usuarios) ou de um externo. [US-36][US-45]"""
    return Coorientacoes.objects.create(
        coo_tcc=tcc,
        coo_doc=docente.docentes if docente is not None else None,
        coo_cext=externo,
        coo_status=StatusCoorientacao.ATIVA,
        coo_data_inicio=quando or timezone.now(),
    )


def registrar_ata(tcc, data=None, pauta="Pauta do encontro", metas="Metas acordadas"):
    """Ata de orientação do TCC. [US-19][RBN-CAD-11.1]"""
    return EncontroOrientacao.objects.create(
        enc_tcc=tcc,
        enc_data=data or timezone.now().date(),
        enc_pauta=pauta,
        enc_metas=metas,
    )


def comentar(ata, usuario, texto="Comentário do orientador", quando=None):
    """Comentário de um docente numa ata. [US-19][RBN-CAD-11.2]"""
    return ComentariosEncontro.objects.create(
        com_enc=ata, com_usu=usuario, com_texto=texto, com_data_hora=quando or timezone.now()
    )


def salvar_artigo(tcc, link="https://doi.org/10.1000/teste", qualis=None, status=None, **campos):
    """Registro de publicação do TCC (um por TCC). [US-46][RBN-CAD-12.1]"""
    return Artigos.objects.create(
        art=tcc,
        art_link_doi=link,
        art_qualis_capes=qualis,
        art_status_submissao=status,
        **campos,
    )


def liberar_resultado(tcc, autor, novo_status=StatusTCC.APROVADO_PARA_TCC_2, quando=None):
    """Simula a liberação do resultado (US-27): gatilho "Liberação do resultado" no histórico.

    Grava direto (sem o serviço da spec 005), só para montar o cenário. [US-20][RBN-DEF-06.4]
    """
    anterior = tcc.tcc_status
    tcc.tcc_status = novo_status
    tcc.save(update_fields=["tcc_status"])
    return HistoricoStatusTCC.objects.create(
        hst_tcc=tcc,
        hst_tur=tcc.tcc_tur,
        hst_status_anterior=anterior,
        hst_status_novo=novo_status,
        hst_gatilho=GatilhoStatusTCC.LIBERACAO_DO_RESULTADO,
        hst_data_hora=quando or timezone.now(),
        hst_usu=autor,
    )


def agendar_defesa(tcc, autor, agora=None):
    """Sessão 'Agendada' com o evento 'Agendamento' no histórico da defesa, como a futura US-24.

    Devolve (defesa, agora): o mesmo instante deve ir para o cancelamento da troca (FR-050).
    [US-24][RBN-DEF-03.2][FR-050]
    """
    from sigtcc.apps.cadastro.tests.fabricas import criar_defesa

    agora = agora or timezone.now()
    defesa = criar_defesa(tcc=tcc, def_status=StatusSessao.AGENDADA)
    HistoricoDefesas.objects.create(
        hdf_def=defesa,
        hdf_evento=EventoDefesa.AGENDAMENTO,
        hdf_status_novo=StatusSessao.AGENDADA,
        hdf_data_hora=agora,
        hdf_usu=autor,
    )
    return defesa, agora
