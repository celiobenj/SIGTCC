"""Domínios do Épico 2, com os valores do Glossario_Status da matriz de 17/10 e do dicionário de
dados de 18/10 (research D7).

[infraestrutura da feature 001, sem US específica][FR-008][FR-010]
"""

from django.db import models


class ComponenteCriterio(models.TextChoices):
    """Componente da avaliação (cri_componente). [US-25][RBN-DEF-04.1]"""

    PARTE_ESCRITA = "Parte Escrita", "Parte Escrita"
    PARTE_ORAL = "Parte Oral", "Parte Oral"


class FormatoSessao(models.TextChoices):
    """Formato da sessão de defesa (def_formato). [US-21][RBN-DEF-01.1]"""

    PRESENCIAL = "Presencial", "Presencial"
    REMOTA = "Remota", "Remota"


class StatusSessao(models.TextChoices):
    """Status da sessão (def_status, hdf_status_anterior, hdf_status_novo).
    [US-24][RBN-DEF-01.2][RBN-DEF-03.3]"""

    AGENDADA = "Agendada", "Agendada"
    EM_ANDAMENTO = "Em Andamento", "Em Andamento"
    REALIZADA = "Realizada", "Realizada"
    REAGENDADA = "Reagendada", "Reagendada"
    CANCELADA = "Cancelada", "Cancelada"


class Parecer(models.TextChoices):
    """Parecer final da banca (def_parecer). [US-27][RBN-DEF-06.3]"""

    REPROVADO = "Reprovado", "Reprovado"
    APROVADO_PARA_TCC_2 = "Aprovado para TCC 2", "Aprovado para TCC 2"
    APROVADO = "Aprovado", "Aprovado"
    APROVADO_COM_CORRECOES = "Aprovado com Correções", "Aprovado com Correções"


class PapelBanca(models.TextChoices):
    """Papel na banca (ban_papel); "º" é o indicador ordinal U+00BA. [US-23][RBN-DEF-02.1]"""

    ORIENTADOR_PRESIDENTE = "Orientador (Presidente)", "Orientador (Presidente)"
    PRIMEIRO_AVALIADOR = "1º Avaliador", "1º Avaliador"
    SEGUNDO_AVALIADOR = "2º Avaliador", "2º Avaliador"
    SUPLENTE = "Suplente", "Suplente"


class Conceito(models.TextChoices):
    """Conceito atribuído pelo avaliador (ava_conceito). [US-25][RBN-DEF-05.2]"""

    EXEMPLAR = "Exemplar", "Exemplar"
    COMPETENTE = "Competente", "Competente"
    NECESSITA_DE_TRABALHO = "Necessita de Trabalho", "Necessita de Trabalho"


class EventoDefesa(models.TextChoices):
    """Evento do histórico da defesa (hdf_evento). [US-40][RBN-DEF-01.6][US-24][RBN-DEF-03.3]"""

    AGENDAMENTO = "Agendamento", "Agendamento"
    REAGENDAMENTO = "Reagendamento", "Reagendamento"
    CANCELAMENTO = "Cancelamento", "Cancelamento"
    INICIO_AUTOMATICO = "Início Automático", "Início Automático"
    ACIONAMENTO_DO_SUPLENTE = "Acionamento do Suplente", "Acionamento do Suplente"
    ALTERACAO_DA_BANCA = "Alteração da Banca", "Alteração da Banca"
    LIBERACAO_DO_RESULTADO = "Liberação do Resultado", "Liberação do Resultado"
