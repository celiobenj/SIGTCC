"""Regras das entregas da turma do app cadastro (spec 005).

Domínio `Turmas_Marcos`/`Entregas_Marcos`/`Historico_Envios_Entregas`: cadastro de entregas pelo
Professor da Disciplina (US-43), envio e substituição do link pelo Aluno, com lembretes de prazo
(US-15), envio da Versão Final do TCC 2 (US-29), acompanhamento das entregas pelo Professor
(US-16) e homologação ou devolução para ajuste da Versão Final (US-44). Este módulo importa
`services_turmas` (permissão por turma, `criar_entregas_do_aluno`, `atualizar_status_tcc`) e
`services_tcc`, nunca o contrário.

[US-15][US-16][US-29][US-43][US-44][RBN-CAD-09.1 a 09.6]
[research C1][research C5][research C6][research C7]
"""

from django.db import IntegrityError, transaction
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services_turmas
from sigtcc.apps.cadastro.choices import StatusEntrega
from sigtcc.apps.cadastro.models import AlunosTurmas, EntregasMarcos, TCCs, TurmasMarcos
from sigtcc.apps.cadastro.services import notificar


class ErroEntrega(Exception):
    """Recusa do cadastro de entrega com a mensagem exata e, se houver, o campo a destacar.

    [US-43][FR-014][research C6]
    """

    def __init__(self, mensagem, campo=None):
        """Guarda a mensagem exata e o campo. [FR-014]"""
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.campo = campo


# =============================================================================================
# Cadastro de entregas pelo Professor da Disciplina (US-43; FR-013 a FR-017; research C6)
# =============================================================================================


def cadastrar_entrega(professor, tur_id, dados):
    """Cadastra uma entrega (`Turmas_Marcos`) na turma do Professor da Disciplina (passos 3 a 6
    da US-43) e cria, para cada aluno atualmente matriculado com participação não encerrada, o
    registro de status ("Aguardando Envio", ou "Não Entregue" se a Data Limite já estiver
    vencida), notificando cada um deles com o Título e a Data Limite (passo 7, MF-05, Q-48).

    A turma é travada antes da gravação (`travar_turma_ativa`, levanta `TurmaArquivada` se
    arquivada); a criação da entrega roda num savepoint próprio (`transaction.atomic()`
    aninhado, mesmo padrão de `services_tcc.salvar_alteracoes_tcc`, research C3) para a captura
    de `IntegrityError` da `UniqueConstraint` (Proposta/Documento para Defesa/Versão Final por
    turma) não invalidar a transação externa; o formulário já restringe o Tipo pela etapa
    (FR-013), então essa captura é a rede de segurança, não o mecanismo principal de checagem
    (research C6).
    [US-43][RBN-CAD-09.1][RBN-CAD-09.6][FR-013 a FR-016][Q-41][research C6]
    """
    with transaction.atomic():
        turma = services_turmas.travar_turma_ativa(tur_id)
        try:
            with transaction.atomic():
                entrega = TurmasMarcos.objects.create(
                    tma_tur=turma,
                    tma_tipo=dados["tipo"],
                    tma_titulo=dados["titulo"],
                    tma_instrucao=dados.get("instrucao") or None,
                    tma_data_limite=dados["data_limite"],
                )
        except IntegrityError:
            raise ErroEntrega(mensagens.ENTREGA_TIPO_REPETIDO, campo="tipo")

        status_inicial = (
            StatusEntrega.NAO_ENTREGUE
            if entrega.tma_data_limite < timezone.now()
            else StatusEntrega.AGUARDANDO_ENVIO
        )
        tccs_por_aluno = {t.tcc_alu_id: t for t in TCCs.objects.filter(tcc_tur=turma)}
        vinculos = AlunosTurmas.objects.filter(mat_tur=turma).select_related("mat_alu__alu")
        for vinculo in vinculos:
            aluno = vinculo.mat_alu
            tcc = tccs_por_aluno.get(aluno.pk)
            if tcc is not None and services_turmas.participacao_encerrada(tcc):
                continue
            EntregasMarcos.objects.create(ent_tma=entrega, ent_alu=aluno, ent_status=status_inicial)
            notificar(
                aluno.alu,
                mensagens.MF05_NOTIFICACAO_ENTREGA_CADASTRADA.format(
                    identificador=turma.tur_identificador,
                    titulo=entrega.tma_titulo,
                    data_limite=entrega.tma_data_limite.strftime("%d/%m/%Y"),
                ),
            )
    return entrega
