"""Apoio aos testes da feature 002 (Gestão de Contas): docentes, Coordenadores e Secretarias por
curso, membros externos, vínculos que impedem a inativação e bancas de defesa.

Só usa os modelos e as fábricas das specs 001, 003 e 004 (não depende de services_contas), para os
testes poderem vir antes do código.

[infraestrutura de teste da feature 002][US-03][US-04][US-05][US-06][US-50]
"""

from datetime import datetime

from django.utils import timezone

from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    OrigemOrientacao,
    StatusConta,
    StatusCoorientacao,
    StatusEntrega,
    StatusOrientacao,
    StatusTurma,
    TipoEntrega,
    TipoSolicitacao,
    Titulacao,
)
from sigtcc.apps.cadastro.models import (
    Coordenadores,
    Coorientacoes,
    Docentes,
    EntregasMarcos,
    MembrosExternos,
    Orientacoes,
    Secretarios,
    TurmasMarcos,
)
from sigtcc.apps.cadastro.tests.apoio_acesso import SENHA, TesteAcesso, _com_senha
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    LC,
    SI,
    criar_solicitacao,
    criar_turma_de,
    curso,
)
from sigtcc.apps.cadastro.tests.fabricas import criar_usuario, proximo

__all__ = ["EC", "SI", "LC", "SENHA", "TesteContas", "curso"]


class TesteContas(TesteAcesso):
    """Base dos testes da feature 002 (a mesma da spec 003: e-mail em memória, caches locais)."""


def docente_de(
    curso_nome=EC, status=StatusConta.ATIVA, email=None, titulacao=Titulacao.DOUTOR, senha=SENHA
):
    """Docente lotado no curso, com senha (se a conta não for 'Aguardando Ativação').

    Devolve o Usuarios. [US-03][RBN-CAD-01.1]
    """
    if status == StatusConta.AGUARDANDO_ATIVACAO:
        senha = None
    usuario = _com_senha(criar_usuario(email=email, status=status), senha)
    Docentes.objects.create(doc=usuario, doc_titulacao=titulacao, doc_cur=curso(curso_nome))
    return usuario


def coordenador_de(curso_nome=EC, lotado_em=None, status=StatusConta.ATIVA, email=None):
    """Docente Coordenador do curso; lotado_em permite lotação diferente (Q26).

    Devolve o Usuarios. [US-03][RBN-CAD-01.1][RBN-CAD-14.1]
    """
    usuario = docente_de(lotado_em or curso_nome, status=status, email=email)
    Coordenadores.objects.create(cor_cur=curso(curso_nome), cor_doc=usuario.docentes)
    return usuario


def secretaria_de(curso_nome=EC, status=StatusConta.ATIVA, email=None, senha=SENHA):
    """Conta de Secretaria vinculada ao curso. Devolve o Usuarios. [US-03][RBN-CAD-02.1]"""
    if status == StatusConta.AGUARDANDO_ATIVACAO:
        senha = None
    usuario = _com_senha(criar_usuario(email=email, status=status), senha)
    Secretarios.objects.create(sec=usuario, sec_cur=curso(curso_nome))
    return usuario


def membro(
    status=StatusConta.ATIVA,
    validade=None,
    email=None,
    titulacao=Titulacao.MESTRE,
    instituicao="Universidade Federal do Amazonas",
    senha=SENHA,
):
    """Membro Externo com validade opcional. Devolve o Usuarios. [US-05][RBN-CAD-03.1]"""
    if status == StatusConta.AGUARDANDO_ATIVACAO:
        senha = None
    usuario = _com_senha(
        criar_usuario(email=email or f"membro{proximo()}@ufam.edu.br", status=status), senha
    )
    MembrosExternos.objects.create(
        mem=usuario,
        mem_titulacao=titulacao,
        mem_instituicao=instituicao,
        mem_validade_ate=validade,
    )
    return usuario


def turma_do_docente(docente, status=StatusTurma.ATIVA, descricao=DescricaoTurma.TCC_1):
    """Turma em que o docente é Professor da Disciplina. [US-07][RBN-CAD-04.1]"""
    return criar_turma_de(docente, descricao=descricao, status=status)


def orientacao_ativa(docente, tcc):
    """Orientação 'Ativa' do docente no TCC. [US-17][RBN-CAD-10.1]"""
    return Orientacoes.objects.create(
        ori_tcc=tcc,
        ori_doc=docente.docentes,
        ori_origem=OrigemOrientacao.PEDIDO_ACEITO,
        ori_status=StatusOrientacao.ATIVA,
        ori_data_inicio=timezone.now(),
    )


def coorientacao_ativa(docente, tcc):
    """Coorientação 'Ativa' do docente no TCC. [US-45][RBN-CAD-10.3]"""
    return Coorientacoes.objects.create(
        coo_tcc=tcc,
        coo_doc=docente.docentes,
        coo_status=StatusCoorientacao.ATIVA,
        coo_data_inicio=timezone.now(),
    )


def convite_pendente(docente, tcc):
    """Convite de coorientação 'Aguardando Aceite'. [US-45][RBN-CAD-10.3]"""
    return criar_solicitacao(tcc, docente, tipo=TipoSolicitacao.COORIENTACAO)


def banca(defesa, usuario, papel=None, substituido=None):
    """Membro na banca da sessão (1º Avaliador por padrão). [US-23][RBN-DEF-02.1]"""
    from sigtcc.apps.defesa.choices import PapelBanca
    from sigtcc.apps.defesa.models import BancaDefesa

    return BancaDefesa.objects.create(
        ban_def=defesa,
        ban_usu=usuario,
        ban_papel=papel or PapelBanca.PRIMEIRO_AVALIADOR,
        ban_usu_substituido=substituido,
    )


def evento_defesa(defesa, evento, data_hora, removido=None):
    """Linha de Historico_Defesas (cancelamento, alteração da banca...). [US-40][RBN-DEF-01.6]"""
    from sigtcc.apps.defesa.models import HistoricoDefesas

    if not isinstance(data_hora, datetime):
        data_hora = datetime(data_hora.year, data_hora.month, data_hora.day, 10, 0)
    return HistoricoDefesas.objects.create(
        hdf_def=defesa,
        hdf_evento=evento,
        hdf_data_hora=data_hora,
        hdf_membro_removido=removido,
    )


def marco_versao_final(turma, aluno, status=StatusEntrega.AGUARDANDO_ENVIO):
    """Entrega 'Versão Final' da turma e o registro do aluno nela. [US-16][RBN-CAD-09.5]"""
    marco = TurmasMarcos.objects.create(
        tma_tur=turma,
        tma_tipo=TipoEntrega.VERSAO_FINAL,
        tma_titulo=f"Versão Final {proximo()}",
        tma_data_limite=timezone.now(),
    )
    return EntregasMarcos.objects.create(ent_tma=marco, ent_alu=aluno, ent_status=status)
