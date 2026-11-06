"""Consultas dos relatórios (spec 010): uma função por relatório, que recebe o usuário e os
filtros e devolve a estrutura única. Só leitura: nenhum trecho grava dados.

[US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2]
[RBN-REL-02.3][RBN-REL-02.4][FR-005]
"""

from django.utils import timezone

from sigtcc.apps.cadastro.choices import StatusTCC

from .forms import FiltroRelatorioForm

# Classificação única do Status do TCC (FR-040). A homologação da Versão Final já leva a Concluído
# (RBN-CAD-09.5), então a classificação olha só o Status. [RBN-REL-02.1][RBN-REL-02.3]
GRUPOS_DE_STATUS = {
    "ativos": (
        StatusTCC.EM_ANDAMENTO,
        StatusTCC.APTO_PARA_DEFESA,
        StatusTCC.APROVADO,
        StatusTCC.APROVADO_COM_CORRECOES,
    ),
    "com_sucesso": (StatusTCC.CONCLUIDO, StatusTCC.APROVADO_PARA_TCC_2),
    "sem_sucesso": (StatusTCC.REPROVADO, StatusTCC.DESISTENTE, StatusTCC.JUBILADO),
}
# Status final encerra o vínculo sem data de fim nos atalhos por data (FR-022; research R18).
STATUS_FINAIS = GRUPOS_DE_STATUS["com_sucesso"] + GRUPOS_DE_STATUS["sem_sucesso"]


def montar_relatorio(usuario, registrado, dados):
    """Caminho único da tela e da exportação (research R1): devolve (form, relatorio), com
    relatorio=None e sem consulta quando o filtro é inválido. O arquivo reflete o momento do
    download. [FR-004][FR-005][FR-014][FR-018]
    """
    form = FiltroRelatorioForm(dados, usuario=usuario, registrado=registrado)
    if not form.is_valid():
        return form, None
    relatorio = registrado.consulta(usuario, form.filtros())
    relatorio.id = registrado.id
    relatorio.titulo = registrado.nome
    relatorio.frase = registrado.frase
    relatorio.gerado_em = timezone.now()
    return form, relatorio
