"""Apoio aos testes da feature 010: alunos com Status conhecido, sessões Realizadas, artigos e
dados hostis, sobre as fábricas das specs 004, 006 e 007.

[US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2]
[RBN-REL-02.3][RBN-REL-02.4][research R15] (tasks T001)
"""

from datetime import date, time

from django.utils import timezone

from sigtcc.apps.cadastro.choices import GatilhoStatusTCC, StatusTCC
from sigtcc.apps.cadastro.models import HistoricoStatusTCC
from sigtcc.apps.cadastro.tests.apoio_orientacao import salvar_artigo, vincular_orientador
from sigtcc.apps.cadastro.tests.apoio_turmas import TesteTurmas, matricular_aluno, tcc_de
from sigtcc.apps.defesa.choices import FormatoSessao, PapelBanca, StatusSessao
from sigtcc.apps.defesa.models import BancaDefesa, Defesas

# Conteúdo que uma planilha, o HTML ou o PDF poderiam interpretar (research R15).
DADOS_HOSTIS = (
    "=1+1",
    "-x",
    "@a",
    "<script>alert(1)</script>",
    'aspas "duplas"',
    "#REF!",
    "a\x0bb",
)
LINK_HOSTIL = "javascript:alert(1)"
LINK_LONGO = "https://doi.org/" + "a" * 484


class TesteRelatorios(TesteTurmas):
    """Base dos testes da feature 010."""


def registrar_status(tcc, status, quando=None, turma=None, autor=None):
    """Grava a mudança de Status no histórico e no TCC, como o serviço único faz.

    `turma` permite simular um registro feito noutra turma (hst_tur). [US-32][RBN-CAD-08.7]
    """
    HistoricoStatusTCC.objects.create(
        hst_tcc=tcc,
        hst_tur=turma or tcc.tcc_tur,
        hst_status_anterior=tcc.tcc_status,
        hst_status_novo=status,
        hst_gatilho=GatilhoStatusTCC.LIBERACAO_DO_RESULTADO,
        hst_data_hora=quando or timezone.now(),
        hst_usu=autor or tcc.tcc_tur.tur_doc.doc,
    )
    tcc.tcc_status = status
    tcc.save(update_fields=["tcc_status"])
    return tcc


def aluno_com_status(turma, status=StatusTCC.EM_ANDAMENTO, quando=None, orientador=None, **dados):
    """Aluno matriculado com o Status gravado também no histórico. Devolve o TCC.

    [US-32][RBN-CAD-08.7]
    """
    aluno = matricular_aluno(turma, status_tcc=StatusTCC.EM_ANDAMENTO, **dados)
    tcc = tcc_de(aluno, turma)
    if status == StatusTCC.SEM_PROPOSTA:
        tcc.tcc_status = status
        tcc.tcc_titulo = tcc.tcc_resumo = tcc.tcc_modalidade = None
        tcc.save()
    else:
        registrar_status(tcc, status, quando)
    if orientador is not None:
        vincular_orientador(tcc, orientador)
    return tcc


def sessao_realizada(tcc, banca, data=None):
    """Sessão Realizada com a banca informada: lista de (usuario, papel, substituido), direto nos
    modelos, sem o fluxo de avaliação (feat-08). [US-31][US-47][RBN-DEF-01.2][RBN-DEF-02.2]
    """
    sessao = Defesas.objects.create(
        def_tcc=tcc,
        def_data=data or date(2026, 11, 20),
        def_h_inicio=time(14, 0),
        def_formato=FormatoSessao.PRESENCIAL,
        def_status=StatusSessao.REALIZADA,
    )
    for usuario, papel, *resto in banca:
        BancaDefesa.objects.create(
            ban_def=sessao,
            ban_usu=usuario,
            ban_papel=papel,
            ban_usu_substituido=resto[0] if resto else None,
        )
    return sessao


def banca_de(presidente, primeiro, segundo, suplente=None):
    """Lista de membros para sessao_realizada. [US-23][RBN-DEF-02.1]"""
    banca = [
        (presidente, PapelBanca.ORIENTADOR_PRESIDENTE),
        (primeiro, PapelBanca.PRIMEIRO_AVALIADOR),
        (segundo, PapelBanca.SEGUNDO_AVALIADOR),
    ]
    if suplente is not None:
        banca.append((suplente, PapelBanca.SUPLENTE))
    return banca


def artigo(tcc, status=None, homologacao=None, link="https://doi.org/10.1000/teste"):
    """Artigo do TCC. [US-33][RBN-CAD-12.1][RBN-CAD-12.3]"""
    return salvar_artigo(tcc, link=link, status=status, art_homologacao=homologacao)
