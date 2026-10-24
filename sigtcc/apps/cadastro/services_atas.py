"""Regras das atas de orientação e dos comentários (spec 006; research R1).

Visibilidade só por vínculo ativo (Q10): Aluno, Orientador atual, Coorientador com coorientação
aceita e Professor da Disciplina; o convite pendente não dá acesso (US-19 #16). Toda ata aberta
pela URL é buscada filtrando pelo TCC do contexto (research R10, A1): as atas do TCC 1, listadas
no TCC 2 só para consulta (Q6), nunca são editadas nem comentadas pela rota do TCC 2.

[US-19][RBN-CAD-11.1][RBN-CAD-11.2][FR-021 a FR-025][Q6][Q10][D14]
"""

from django.db import transaction
from django.db.models import Prefetch
from django.http import Http404
from django.utils import timezone

from sigtcc.apps.cadastro.models import Alunos, ComentariosEncontro, EncontroOrientacao, TCCs
from sigtcc.apps.cadastro.services_orientacao import (
    ALUNO,
    COORIENTADOR,
    ORIENTADOR,
    PROFESSOR,
    papeis_no_tcc,
    pode_alterar_no_tcc,
    tcc_de_origem,
)
from sigtcc.apps.cadastro.services_turmas import travar_turma_ativa

# Quem vê, registra e edita, e quem comenta (FR-022 a FR-024).
VEEM = {ALUNO, ORIENTADOR, COORIENTADOR, PROFESSOR}
REGISTRAM = {ALUNO, ORIENTADOR, COORIENTADOR}
COMENTAM = {ORIENTADOR, COORIENTADOR}


def atas_do_tcc(tcc):
    """Atas do TCC, da mais recente para a mais antiga; na mesma Data do Encontro, a última
    registrada primeiro (D14); com os comentários (autor, data e hora) já carregados.
    [US-19][RBN-CAD-11.2][FR-023][D14]
    """
    comentarios = ComentariosEncontro.objects.select_related("com_usu").order_by(
        "com_data_hora", "com_id"
    )
    return list(
        EncontroOrientacao.objects.filter(enc_tcc=tcc)
        .prefetch_related(Prefetch("comentariosencontro_set", queryset=comentarios))
        .order_by("-enc_data", "-enc_id")
    )


def papeis_nas_atas(usuario, tcc):
    """Papéis do usuário que valem para as atas, ou 404 sem vínculo (sem revelar o TCC).

    [US-19][RBN-CAD-11.2][FR-023][FR-025][Q10]
    """
    papeis = papeis_no_tcc(usuario, tcc) & VEEM
    if not papeis:
        raise Http404
    return papeis


def contexto_lista(usuario, tcc):
    """Lista de atas (FR-023): as do TCC e, no TCC 2, as do TCC 1 abaixo, só para consulta,
    identificadas pela turma de TCC 1; e o que o usuário pode fazer (FR-024, FR-025).
    [US-19][RBN-CAD-11.2][FR-023][FR-024][FR-025][Q6]
    """
    papeis = papeis_nas_atas(usuario, tcc)
    alteravel = pode_alterar_no_tcc(tcc)
    origem = tcc_de_origem(tcc)
    return {
        "tcc": tcc,
        "atas": atas_do_tcc(tcc),
        "origem": origem,
        "atas_origem": atas_do_tcc(origem) if origem else [],
        "pode_registrar": alteravel and bool(papeis & REGISTRAM),
        "pode_editar": alteravel and bool(papeis & REGISTRAM),
        "pode_comentar": alteravel and bool(papeis & COMENTAM),
    }


def _travar(usuario, tcc_id, papeis_exigidos):
    """Trava turma ativa → aluno → TCC (research R2), confere a turma do TCC depois da trava e o
    papel exigido; TurmaArquivada com a turma arquivada; 404 sem vínculo ou sem alteração
    possível (participação encerrada ou TCC copiado, FR-007).
    [US-19][FR-022][FR-024][FR-046][research R2]
    """
    achado = TCCs.objects.filter(pk=tcc_id).values("tcc_tur_id", "tcc_alu_id").first()
    if achado is None:
        raise Http404
    turma = travar_turma_ativa(achado["tcc_tur_id"])
    Alunos.objects.select_for_update().filter(pk=achado["tcc_alu_id"]).first()
    tcc = (
        TCCs.objects.select_for_update(of=("self",))
        .select_related("tcc_tur", "tcc_alu__alu")
        .get(pk=tcc_id)
    )
    if tcc.tcc_tur_id != turma.pk:
        raise Http404
    if not (papeis_no_tcc(usuario, tcc) & papeis_exigidos) or not pode_alterar_no_tcc(tcc):
        raise Http404
    return tcc


def registrar_ata(usuario, tcc_id, dados):
    """ "Registrar ata de orientação" pelo Aluno, pelo Orientador ou pelo Coorientador com
    coorientação aceita (FR-021, FR-022). [US-19][RBN-CAD-11.1][FR-021][FR-022]
    """
    with transaction.atomic():
        tcc = _travar(usuario, tcc_id, REGISTRAM)
        return EncontroOrientacao.objects.create(
            enc_tcc=tcc,
            enc_data=dados["data"],
            enc_pauta=dados["pauta"],
            enc_metas=dados["metas"],
        )


def ata_do_tcc(tcc, enc_id):
    """Ata pelo id, só se for deste TCC (research R10, A1), senão 404. [US-19][FR-024]"""
    ata = EncontroOrientacao.objects.filter(pk=enc_id, enc_tcc=tcc).first()
    if ata is None:
        raise Http404
    return ata


def editar_ata(usuario, tcc_id, enc_id, dados):
    """Edição da ata pelo Aluno, pelo Orientador ou pelo Coorientador (FR-024), com as mesmas
    regras do registro. [US-19][RBN-CAD-11.2][FR-024]
    """
    with transaction.atomic():
        tcc = _travar(usuario, tcc_id, REGISTRAM)
        ata = EncontroOrientacao.objects.select_for_update().filter(pk=enc_id, enc_tcc=tcc).first()
        if ata is None:
            raise Http404
        ata.enc_data = dados["data"]
        ata.enc_pauta = dados["pauta"]
        ata.enc_metas = dados["metas"]
        ata.save(update_fields=["enc_data", "enc_pauta", "enc_metas"])
    return ata


def comentar_ata(docente, tcc_id, enc_id, texto):
    """Comentário do Orientador ou do Coorientador abaixo da ata, com autor, data e hora
    (FR-024); o Aluno não comenta. [US-19][RBN-CAD-11.2][FR-024]
    """
    with transaction.atomic():
        tcc = _travar(docente, tcc_id, COMENTAM)
        ata = ata_do_tcc(tcc, enc_id)
        return ComentariosEncontro.objects.create(
            com_enc=ata, com_usu=docente, com_texto=texto, com_data_hora=timezone.now()
        )
