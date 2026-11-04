"""Ponto de chamada da feat-09 (US-28 e US-30) na liberação do resultado (spec 008, research
A10; contrato §2 de specs/008-avaliacao-resultados/contracts/servicos-avaliacoes.md).

STUBS até a feat-09 entregar as funções reais. A feat-09 troca só o corpo, sem mudar a
assinatura nem o ponto de chamada:
- ao_liberar_resultado(sessao): registrado por services_avaliacoes.liberar_resultado com
  transaction.on_commit(..., robust=True), depois de gravada a liberação; a feat-09 envia as
  declarações de participação por e-mail (RBN-DEF-08.3), com o trabalho pesado numa thread (como
  enviar_email_apos_commit) e a falha só no log (D9). A Ata Final e a Folha de Aprovação não são
  geradas aqui: são PDFs sob demanda, a cada download (research A9).
- declaracao_disponivel(sessao, usuario): decide o botão Declaração de Minhas bancas.

[US-27][US-25][RBN-DEF-06.4][RBN-DEF-08.3][RBN-DEF-05.4]
"""

import logging

logger = logging.getLogger("sigtcc.defesa")


def ao_liberar_resultado(sessao):
    """STUB: só registra em log que a liberação pediu o envio das declarações (feat-09).
    [US-27][US-30][RBN-DEF-06.4][RBN-DEF-08.3]
    """
    logger.info("Liberação do resultado: declarações pedidas (stub), sessão %s", sessao.pk)


def declaracao_disponivel(sessao, usuario):
    """STUB: a declaração de participação ainda não existe (feat-09); sempre False.
    [US-25][US-30][RBN-DEF-05.4][RBN-DEF-08.3]
    """
    return False
