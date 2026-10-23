"""Regras da Proposta, dos dados do TCC e do Status/histórico/trilha do app cadastro (spec 005).

Domínio `TCCs`/`Historico_Status_TCC`: Proposta e dados do TCC com mudança de tema (US-13);
confidencialidade do Resumo (FR-007a); consulta do histórico e da trilha do Status, sem checagem
de perfil (US-14, research C9). Este módulo importa `services_turmas` (que expõe o serviço único
de gravação do Status, `criar_tcc_com_historico`/`atualizar_status_tcc`, FR-012), nunca o
contrário.

[US-13][US-14][RBN-CAD-07.1][RBN-CAD-08.1][RBN-CAD-08.2][RBN-CAD-08.3][RBN-CAD-08.7][RBN-CAD-08.8]
[research C1][research C3][research C9]
"""

from sigtcc.apps.cadastro.choices import StatusCoorientacao, StatusOrientacao, TipoSolicitacao
from sigtcc.apps.cadastro.models import (
    Coorientacoes,
    HistoricoStatusTCC,
    Orientacoes,
    SolicitacoesOrientacao,
)
from sigtcc.apps.cadastro.services_turmas import STATUS_SOLICITACAO_PENDENTE


def pode_ver_resumo(usuario, tcc):
    """O Resumo da Proposta (tcc_resumo) só é visível a quem a FR-007a autoriza (RAN-CAD-07 NFR
    de Confidencialidade; research C3): o próprio Aluno dono do TCC, o Orientador **atual**
    (`Orientacoes.ori_status='Ativa'`), um Docente com `Solicitacoes_Orientacao` de Orientação
    ainda pendente para esse TCC, o Coorientador do NUCOMP **com coorientação aceita**
    (`Coorientacoes.coo_status='Ativa'`, só `coo_doc`, nunca `coo_cext`) ou o Professor da
    Disciplina da turma do TCC. Qualquer outro Docente (inclusive sem vínculo) recebe False.

    Única forma permitida de decidir essa visibilidade (contrato `servicos-compartilhados.md`,
    §1): toda view desta spec, da spec 006 ou do Épico 3 que exiba `tcc_resumo` MUST chamar esta
    função antes, nunca reimplementar a regra.
    [US-13][RAN-CAD-07][FR-007a][research C3]
    """
    if usuario is None or not getattr(usuario, "is_authenticated", False):
        return False
    if tcc.tcc_alu_id == usuario.pk:
        return True
    if Orientacoes.objects.filter(
        ori_tcc=tcc, ori_status=StatusOrientacao.ATIVA, ori_doc_id=usuario.pk
    ).exists():
        return True
    # Só o pedido de Orientação (TipoSolicitacao.ORIENTACAO); a Coorientação tem regra própria,
    # abaixo, com coo_status='Ativa' (Coorientador do NUCOMP sem coorientação aceita não vê).
    if SolicitacoesOrientacao.objects.filter(
        sol_tcc=tcc,
        sol_doc_id=usuario.pk,
        sol_tipo=TipoSolicitacao.ORIENTACAO,
        sol_status__in=STATUS_SOLICITACAO_PENDENTE,
    ).exists():
        return True
    if Coorientacoes.objects.filter(
        coo_tcc=tcc, coo_status=StatusCoorientacao.ATIVA, coo_doc_id=usuario.pk
    ).exists():
        return True
    if tcc.tcc_tur.tur_doc_id == usuario.pk:
        return True
    return False


def historico_do_status(tcc):
    """Todas as linhas do histórico do Status deste TCC, da mais antiga à mais recente (mesmo
    dado usado pela trilha do FR-010), **sem nenhuma checagem de perfil** — quem chama decide se
    autoriza (research C9; contrato `servicos-compartilhados.md`, §2). A view desta spec aplica a
    checagem (Aluno dono, Orientador atual, Professor da Disciplina — nunca Secretaria nem
    Coorientador) antes de chamar; a spec 006 (tela de orientandos) chama direto, com a própria
    checagem (Orientador do TCC) por fora.
    [US-14][RBN-CAD-08.7][FR-009][FR-010][research C9]
    """
    return HistoricoStatusTCC.objects.filter(hst_tcc=tcc).order_by("hst_data_hora", "hst_id")
