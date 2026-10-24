"""Regras da publicação do artigo e do aproveitamento pelo Coordenador (spec 006; research R1).

Ciclo do aproveitamento (RBN-CAD-12.3; dicionário 3.5.7; Q16): Status Aceito ou Publicado leva a
"Em Análise"; alterar Qualis, Status ou Link de um artigo já analisado sempre volta a "Em
Análise", antes ou depois da liberação; depois da liberação, só a recusa de artigo Homologado fica
bloqueada (US-20 E3). Toda gravação em Artigos trava turma → aluno → TCC → Artigos (research R8,
R9). Os eventos do log ficam num enum local, como o EventoFluxoTCC da spec 005 (research R9, A23).

[US-46][US-20][RBN-CAD-12.1][RBN-CAD-12.2][RBN-CAD-12.3][FR-034 a FR-039][Q16][D10][D11]
"""

import enum

from django.db import transaction
from django.http import Http404
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import (
    GatilhoStatusTCC,
    Homologacao,
    ModalidadeTCC,
    StatusSubmissao,
)
from sigtcc.apps.cadastro.models import Alunos, Artigos, HistoricoStatusTCC, TCCs, Turmas
from sigtcc.apps.cadastro.permissoes import curso_id_do_usuario
from sigtcc.apps.cadastro.services import registrar_evento
from sigtcc.apps.cadastro.services_orientacao import (
    ALUNO,
    ORIENTADOR,
    orientador_atual,
    papeis_no_tcc,
    pode_alterar_no_tcc,
    tcc_copiado,
)
from sigtcc.apps.cadastro.services_turmas import travar_turma_ativa

# Status de Submissão que levam o artigo à análise do Coordenador (RBN-CAD-12.2).
STATUS_ANALISAVEL = (StatusSubmissao.ACEITO, StatusSubmissao.PUBLICADO)
# Qualis que garantem a nota mínima 6,0 (RBN-CAD-12.3; RBN-DEF-06.2).
QUALIS_A_OU_B = ("A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4")


class EventoArtigo(enum.Enum):
    """Decisões do Coordenador no log de eventos (D10): a tabela guarda só a mais recente, o log
    guarda todas. `registrar_evento` só usa `.value` (mesmo padrão de EventoFluxoTCC, spec 005).
    [US-20][RAN-CAD-12 NFR][FR-038][D10][research R9]
    """

    APROVEITAMENTO_HOMOLOGADO = "APROVEITAMENTO_HOMOLOGADO"
    APROVEITAMENTO_RECUSADO = "APROVEITAMENTO_RECUSADO"
    APROVEITAMENTO_DESFEITO = "APROVEITAMENTO_DESFEITO"


def artigo_do_tcc(tcc):
    """Registro de publicação do TCC (um por TCC), ou None. [US-46][RBN-CAD-12.1]"""
    return Artigos.objects.filter(art=tcc).first()


def etiqueta_aproveitamento(artigo):
    """Etiqueta da seção: MO-22 enquanto não houver análise (Status diferente de Aceito ou
    Publicado e aproveitamento nulo ou "Em Análise"); senão, o aproveitamento (D10).
    [US-46][RBN-CAD-12.3][FR-034][D10]
    """
    if artigo is None:
        return mensagens.MO22_AGUARDANDO_PUBLICACAO
    if artigo.art_status_submissao not in STATUS_ANALISAVEL and artigo.art_homologacao in (
        None,
        Homologacao.EM_ANALISE,
    ):
        return mensagens.MO22_AGUARDANDO_PUBLICACAO
    return artigo.art_homologacao or mensagens.MO22_AGUARDANDO_PUBLICACAO


def contexto_publicacao(tcc, somente_leitura=False):
    """Estado da seção "Publicação do artigo" (só em Artigo Científico; D10), ou None.

    [US-46][RBN-CAD-12.1][FR-034][FR-007]
    """
    if tcc.tcc_modalidade != ModalidadeTCC.ARTIGO_CIENTIFICO:
        return None
    artigo = artigo_do_tcc(tcc)
    return {
        "artigo": artigo,
        "etiqueta": etiqueta_aproveitamento(artigo),
        "pode_salvar": not somente_leitura and pode_alterar_no_tcc(tcc),
        "inicial": (
            {
                "veiculo": artigo.art_veiculo_publicacao or "",
                "link": artigo.art_link_doi,
                "qualis": artigo.art_qualis_capes or "",
                "status": artigo.art_status_submissao or "",
            }
            if artigo
            else {}
        ),
    }


def _travar_tcc(usuario, tcc_id, papeis):
    """Trava turma ativa → aluno → TCC (research R2) e confere o papel e a alteração (FR-007).

    [US-46][FR-034][FR-035][research R8]
    """
    achado = TCCs.objects.filter(pk=tcc_id).values("tcc_tur_id", "tcc_alu_id").first()
    if achado is None:
        raise Http404
    turma = travar_turma_ativa(achado["tcc_tur_id"])
    Alunos.objects.select_for_update().filter(pk=achado["tcc_alu_id"]).first()
    tcc = TCCs.objects.select_for_update(of=("self",)).select_related("tcc_alu__alu").get(pk=tcc_id)
    if (
        tcc.tcc_tur_id != turma.pk
        or not (papeis_no_tcc(usuario, tcc) & papeis)
        or not pode_alterar_no_tcc(tcc)
        or tcc.tcc_modalidade != ModalidadeTCC.ARTIGO_CIENTIFICO
    ):
        raise Http404
    return tcc


def salvar_publicacao(usuario, tcc_id, dados):
    """ "Salvar publicação" pelo Aluno ou pelo Orientador (FR-034 a FR-036): um registro por TCC;
    a primeira vez com Aceito ou Publicado, "Em Análise"; alterar Qualis, Status ou Link de um
    artigo já analisado volta a "Em Análise" a qualquer tempo (Q16), mantendo autor e data da
    última decisão; a decisão desfeita vai para o log (D10).
    [US-46][RBN-CAD-12.1][RBN-CAD-12.3][FR-034][FR-035][FR-036][Q16][D10][research R8]
    """
    with transaction.atomic():
        tcc = _travar_tcc(usuario, tcc_id, {ALUNO, ORIENTADOR})
        artigo = Artigos.objects.select_for_update().filter(art=tcc).first()
        novos = {
            "art_veiculo_publicacao": dados.get("veiculo") or None,
            "art_link_doi": dados["link"],
            "art_qualis_capes": dados.get("qualis") or None,
            "art_status_submissao": dados.get("status") or None,
        }
        if artigo is None:
            artigo = Artigos(art=tcc)
            mudou_analise = False
        else:
            mudou_analise = any(
                getattr(artigo, campo) != novos[campo]
                for campo in ("art_qualis_capes", "art_status_submissao", "art_link_doi")
            )
        decidido = artigo.art_homologacao in (Homologacao.HOMOLOGADO, Homologacao.RECUSADO)
        for campo, valor in novos.items():
            setattr(artigo, campo, valor)
        if decidido and mudou_analise:
            anterior = artigo.art_homologacao
            artigo.art_homologacao = Homologacao.EM_ANALISE
            transaction.on_commit(
                lambda: registrar_evento(
                    EventoArtigo.APROVEITAMENTO_DESFEITO,
                    tcc.tcc_alu.alu,
                    autor=usuario,
                    detalhe=f"tcc_id={tcc.pk} anterior={anterior}",
                )
            )
        elif artigo.art_homologacao is None and artigo.art_status_submissao in STATUS_ANALISAVEL:
            artigo.art_homologacao = Homologacao.EM_ANALISE
        artigo.save()
    return artigo


# =============================================================================================
# Aproveitamento pelo Coordenador (US-20; FR-037 a FR-039; research R7, R9)
# =============================================================================================


def resultado_liberado(tcc):
    """Gatilho "Liberação do resultado" no histórico **desse** TCC (no TCC 2, a do TCC 1 não
    conta). Usado só para a US-20 E3 (research R7; contrato §4). [US-20][FR-038][Q16]
    """
    return HistoricoStatusTCC.objects.filter(
        hst_tcc=tcc, hst_gatilho=GatilhoStatusTCC.LIBERACAO_DO_RESULTADO
    ).exists()


def tem_artigo_homologado_qualis_ab(tcc):
    """Consulta para a US-27 (FR-039; contrato §4): aproveitamento "Homologado" com Qualis A1 a
    A4 ou B1 a B4 — nota final mínima 6,0 em TCC 1 e em TCC 2, chamada na liberação com o TCC já
    travado; a apresentação perante a banca continua obrigatória.
    [US-20][US-27][RBN-CAD-12.3][RBN-DEF-06.2][FR-039]
    """
    return Artigos.objects.filter(
        art=tcc, art_homologacao=Homologacao.HOMOLOGADO, art_qualis_capes__in=QUALIS_A_OU_B
    ).exists()


def artigos_para_analise(coordenador, curso_id):
    """Tela "Aproveitamento de artigos" (FR-037): artigos Aceitos ou Publicados de TCCs em Artigo
    Científico, só o TCC atual de cada aluno (sem o TCC 1 copiado; Q6), do curso da turma
    escolhido (None = Todos). Cada linha diz se o Coordenador decide (curso que coordena) e se
    "Recusar" está disponível (US-20 C e E3).
    [US-20][RBN-CAD-12.2][RBN-CAD-12.3][RBN-CAD-14.1][FR-037][FR-038][Q6][D11]
    """
    meu_curso = curso_id_do_usuario(coordenador)
    artigos = (
        Artigos.objects.select_related("art__tcc_alu__alu", "art__tcc_tur__tur_cur")
        .filter(
            art_status_submissao__in=STATUS_ANALISAVEL,
            art__tcc_modalidade=ModalidadeTCC.ARTIGO_CIENTIFICO,
        )
        .order_by("art__tcc_alu__alu__usu_nome")
    )
    if curso_id is not None:
        artigos = artigos.filter(art__tcc_tur__tur_cur_id=curso_id)
    linhas = []
    for artigo in artigos:
        tcc = artigo.art
        if tcc_copiado(tcc):
            continue
        orientador = orientador_atual(tcc)
        decide = tcc.tcc_tur.tur_cur_id == meu_curso
        homologado = artigo.art_homologacao == Homologacao.HOMOLOGADO
        linhas.append(
            {
                "artigo": artigo,
                "tcc": tcc,
                "aluno": tcc.tcc_alu.alu.usu_nome,
                "orientador": orientador.doc.usu_nome if orientador else "",
                "pode_homologar": decide and not homologado,
                "pode_recusar": decide
                and artigo.art_homologacao != Homologacao.RECUSADO
                and not (homologado and resultado_liberado(tcc)),
                "recusa_bloqueada": decide and homologado and resultado_liberado(tcc),
            }
        )
    return linhas


def _decidir(coordenador, tcc_id, decisao):
    """Homologar ou Recusar (FR-038): trava a turma **sem exigir que esteja ativa** (D11; FR-046)
    → aluno → TCC → Artigos (research R9, N2) e só então confere: artigo existente, do curso que
    o Coordenador coordena, Artigo Científico, Aceito ou Publicado e TCC não copiado (senão 404);
    na recusa de artigo Homologado depois da liberação, a MO-21. Autor, data e hora na tabela e
    no log (D10).
    [US-20][RBN-CAD-12.3][RAN-CAD-12 NFR][FR-038][D10][D11][research R9]
    """
    achado = TCCs.objects.filter(pk=tcc_id).values("tcc_tur_id", "tcc_alu_id").first()
    if achado is None:
        raise Http404
    with transaction.atomic():
        turma = Turmas.objects.select_for_update().filter(pk=achado["tcc_tur_id"]).first()
        Alunos.objects.select_for_update().filter(pk=achado["tcc_alu_id"]).first()
        tcc = (
            TCCs.objects.select_for_update(of=("self",))
            .select_related("tcc_alu__alu")
            .get(pk=tcc_id)
        )
        artigo = Artigos.objects.select_for_update().filter(art=tcc).first()
        if (
            artigo is None
            or turma is None
            or tcc.tcc_tur_id != turma.pk
            or turma.tur_cur_id != curso_id_do_usuario(coordenador)
            or tcc.tcc_modalidade != ModalidadeTCC.ARTIGO_CIENTIFICO
            or artigo.art_status_submissao not in STATUS_ANALISAVEL
            or tcc_copiado(tcc)
        ):
            raise Http404
        if (
            decisao == Homologacao.RECUSADO
            and artigo.art_homologacao == Homologacao.HOMOLOGADO
            and resultado_liberado(tcc)
        ):
            raise ErroArtigo(mensagens.MO21_RESULTADO_LIBERADO)
        artigo.art_homologacao = decisao
        artigo.art_homologado_por = coordenador
        artigo.art_data_homologacao = timezone.now()
        artigo.save(update_fields=["art_homologacao", "art_homologado_por", "art_data_homologacao"])
        evento = (
            EventoArtigo.APROVEITAMENTO_HOMOLOGADO
            if decisao == Homologacao.HOMOLOGADO
            else EventoArtigo.APROVEITAMENTO_RECUSADO
        )
        aluno = tcc.tcc_alu.alu
        transaction.on_commit(
            lambda: registrar_evento(evento, aluno, autor=coordenador, detalhe=f"tcc_id={tcc.pk}")
        )
    return artigo


class ErroArtigo(Exception):
    """Decisão recusada com uma mensagem (MO-21). [US-20][FR-038]"""

    def __init__(self, mensagem):
        """Guarda a mensagem exibida. [FR-048]"""
        super().__init__(mensagem)
        self.mensagem = mensagem


def homologar_artigo(coordenador, tcc_id):
    """ "Homologar" (FR-038). [US-20][RBN-CAD-12.3][FR-038]"""
    return _decidir(coordenador, tcc_id, Homologacao.HOMOLOGADO)


def recusar_artigo(coordenador, tcc_id):
    """ "Recusar" (FR-038; US-20 C e E3). [US-20][RBN-CAD-12.3][FR-038]"""
    return _decidir(coordenador, tcc_id, Homologacao.RECUSADO)
