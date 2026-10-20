"""Domínios do Épico 1, com os valores do Glossario_Status da matriz de 17/10 e do dicionário de
dados de 18/10 (research D7).

Cada classe também gera o CHECK do banco em Meta.constraints, para tela e banco não divergirem.

[infraestrutura da feature 001, sem US específica][FR-008][FR-009][FR-010]
"""

from django.db import models


class StatusConta(models.TextChoices):
    """Status da Conta (usu_status). [US-04][RBN-CAD-01.3][RBN-CAD-02.3][US-06][RBN-CAD-03.3]"""

    AGUARDANDO_ATIVACAO = "Aguardando Ativação", "Aguardando Ativação"
    ATIVA = "Ativa", "Ativa"
    INATIVA = "Inativa", "Inativa"
    EXPIRADA = "Expirada", "Expirada"


class Titulacao(models.TextChoices):
    """Titulação acadêmica (doc_titulacao, mem_titulacao). [US-03][RBN-CAD-01.1][US-05]"""

    ESPECIALISTA = "Especialista", "Especialista"
    MESTRE = "Mestre", "Mestre"
    DOUTOR = "Doutor", "Doutor"


class DescricaoTurma(models.TextChoices):
    """Descrição da turma (tur_descricao). [US-07][RBN-CAD-04.1]"""

    TCC_1 = "TCC 1", "TCC 1"
    TCC_2 = "TCC 2", "TCC 2"


class StatusTurma(models.TextChoices):
    """Vigência da turma (tur_status). [US-07][RBN-CAD-04.5]"""

    ATIVA = "Ativa", "Ativa"
    ARQUIVADA = "Arquivada", "Arquivada"


class DiaSemana(models.TextChoices):
    """Dia da semana das aulas (tur_dia_da_semana). [US-07][RBN-CAD-04.1]"""

    SEGUNDA = "segunda-feira", "segunda-feira"
    TERCA = "terça-feira", "terça-feira"
    QUARTA = "quarta-feira", "quarta-feira"
    QUINTA = "quinta-feira", "quinta-feira"
    SEXTA = "sexta-feira", "sexta-feira"
    SABADO = "sábado", "sábado"


class TipoEventoTurma(models.TextChoices):
    """Movimentação do aluno (hat_tipo_evento). [US-09][RBN-CAD-05.4][US-08][RBN-CAD-05.6]"""

    EXCLUSAO = "Exclusão", "Exclusão"
    TRANSFERENCIA = "Transferência", "Transferência"


class TipoEntrega(models.TextChoices):
    """Tipo de entrega (tma_tipo). [US-43][RBN-CAD-09.1]"""

    PROPOSTA = "Proposta", "Proposta"
    DOCUMENTO_PARA_DEFESA = "Documento para Defesa", "Documento para Defesa"
    VERSAO_FINAL = "Versão Final", "Versão Final"
    OUTRA = "Outra", "Outra"


class StatusEntrega(models.TextChoices):
    """Status da entrega (ent_status). [US-15][RBN-CAD-09.3][US-44][RBN-CAD-09.5]"""

    AGUARDANDO_ENVIO = "Aguardando Envio", "Aguardando Envio"
    ENTREGUE = "Entregue", "Entregue"
    ENTREGUE_COM_ATRASO = "Entregue com Atraso", "Entregue com Atraso"
    NAO_ENTREGUE = "Não Entregue", "Não Entregue"
    DEVOLVIDA_PARA_AJUSTE = "Devolvida para Ajuste", "Devolvida para Ajuste"
    HOMOLOGADA = "Homologada", "Homologada"


class ModalidadeTCC(models.TextChoices):
    """Modalidade do trabalho (tcc_modalidade). [US-13][RBN-CAD-07.1]"""

    MONOGRAFIA = "Monografia", "Monografia"
    ARTIGO_CIENTIFICO = "Artigo Científico", "Artigo Científico"


class StatusTCC(models.TextChoices):
    """Status do TCC (tcc_status, hst_status_anterior, hst_status_novo). [US-14][RBN-CAD-08.3]"""

    SEM_PROPOSTA = "Sem Proposta", "Sem Proposta"
    EM_ANDAMENTO = "Em Andamento", "Em Andamento"
    APTO_PARA_DEFESA = "Apto para Defesa", "Apto para Defesa"
    APROVADO_PARA_TCC_2 = "Aprovado para TCC 2", "Aprovado para TCC 2"
    APROVADO = "Aprovado", "Aprovado"
    APROVADO_COM_CORRECOES = "Aprovado com Correções", "Aprovado com Correções"
    CONCLUIDO = "Concluído", "Concluído"
    REPROVADO = "Reprovado", "Reprovado"
    DESISTENTE = "Desistente", "Desistente"
    JUBILADO = "Jubilado", "Jubilado"


class OrigemOrientacao(models.TextChoices):
    """Origem do vínculo de orientação (ori_origem). [US-18][RBN-CAD-10.2][US-07][RBN-CAD-04.2]"""

    PEDIDO_ACEITO = "Pedido Aceito", "Pedido Aceito"
    AUTOMATICO = "Automático", "Automático"


class StatusOrientacao(models.TextChoices):
    """Estado do vínculo de orientação (ori_status). [US-17][RBN-CAD-10.6]"""

    ATIVA = "Ativa", "Ativa"
    ENCERRADA = "Encerrada", "Encerrada"


class StatusCoorientacao(models.TextChoices):
    """Estado do vínculo de coorientação (coo_status). [US-45][RBN-CAD-10.7]"""

    ATIVA = "Ativa", "Ativa"
    SUBSTITUIDA = "Substituída", "Substituída"
    ENCERRADA = "Encerrada", "Encerrada"


class TipoSolicitacao(models.TextChoices):
    """Tipo da solicitação (sol_tipo). [US-17][RBN-CAD-10.1][RBN-CAD-10.6][US-36][RBN-CAD-10.4]"""

    ORIENTACAO = "Orientação", "Orientação"
    TROCA_DE_ORIENTACAO = "Troca de Orientação", "Troca de Orientação"
    COORIENTACAO = "Coorientação", "Coorientação"


class StatusSolicitacao(models.TextChoices):
    """Estado da solicitação (sol_status); a combinação com o tipo é o CHECK
    ck_solicitacoes_orientacao_status_por_tipo. [US-17][RBN-CAD-10.1][US-36][RBN-CAD-10.4]"""

    AGUARDANDO_RESPOSTA = "Aguardando Resposta", "Aguardando Resposta"
    AGUARDANDO_ACEITE = "Aguardando Aceite", "Aguardando Aceite"
    ACEITO = "Aceito", "Aceito"
    RECUSADO = "Recusado", "Recusado"
    CANCELADO = "Cancelado", "Cancelado"


class GatilhoStatusTCC(models.TextChoices):
    """Gatilho da mudança de status do TCC (hst_gatilho). [US-14][RBN-CAD-08.7]"""

    VINCULO_A_TURMA = "Vínculo à turma", "Vínculo à turma"
    PROPOSTA_SALVA = "Proposta salva", "Proposta salva"
    TRANSFERENCIA_PARA_TCC_2 = "Transferência para TCC 2", "Transferência para TCC 2"
    INDICACAO_DE_APTO = "Indicação de Apto para Defesa", "Indicação de Apto para Defesa"
    LIBERACAO_DO_RESULTADO = "Liberação do resultado", "Liberação do resultado"
    HOMOLOGACAO_DA_VERSAO_FINAL = "Homologação da Versão Final", "Homologação da Versão Final"
    ENCERRAMENTO_DA_PARTICIPACAO = "Encerramento da participação", "Encerramento da participação"


class QualisCapes(models.TextChoices):
    """Estrato Qualis/CAPES (art_qualis_capes). [US-46][RBN-CAD-12.1]"""

    A1 = "A1", "A1"
    A2 = "A2", "A2"
    A3 = "A3", "A3"
    A4 = "A4", "A4"
    B1 = "B1", "B1"
    B2 = "B2", "B2"
    B3 = "B3", "B3"
    B4 = "B4", "B4"
    C = "C", "C"


class StatusSubmissao(models.TextChoices):
    """Status de submissão do artigo (art_status_submissao). [US-46][RBN-CAD-12.1]"""

    SUBMETIDO = "Submetido", "Submetido"
    EM_REVISAO = "Em Revisão", "Em Revisão"
    ACEITO = "Aceito", "Aceito"
    PUBLICADO = "Publicado", "Publicado"
    REJEITADO = "Rejeitado", "Rejeitado"


class Homologacao(models.TextChoices):
    """Aproveitamento do artigo (art_homologacao). [US-20][RBN-CAD-12.3]"""

    EM_ANALISE = "Em Análise", "Em Análise"
    HOMOLOGADO = "Homologado", "Homologado"
    RECUSADO = "Recusado", "Recusado"


def restricao_dominio(nome, campo, choices, aceita_nulo=False):
    """CHECK que aceita só os valores do domínio (e nulo, se o campo for anulável).

    Gerado da mesma classe usada em choices=, para tela e banco não divergirem (research D7).
    """
    condicao = models.Q(**{f"{campo}__in": choices.values})
    if aceita_nulo:
        condicao |= models.Q(**{f"{campo}__isnull": True})
    return models.CheckConstraint(condition=condicao, name=nome)
