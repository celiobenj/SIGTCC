"""Mensagens do módulo Relatórios: textos exatos das US e os provisórios MR-01 a MR-14 (spec 010,
"Mensagens a validar com a PO"; índice Q-146). Só constantes: cadastro/views.py importa este
módulo para o handler403 (research R13).

[US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2]
[RBN-REL-02.3][RBN-REL-02.4]
"""

# Textos exatos das US (E3 da US-31 e da US-47, E2 da US-32 e da US-33; fluxos D e E da US-31).
NENHUM_REGISTRO_FILTROS = "Nenhum registro encontrado para os filtros selecionados"
NENHUM_REGISTRO = "Nenhum registro"

# Provisórios (Q-146).
MR01_SUGESTAO_VAZIO = "Tente outro período ou o curso Todos"
MR02_SEM_REGISTROS_EXPORTAR = "Sem registros para exportar"
MR05_SELECIONE = "Selecione um relatório na lista"
MR06_SEM_PERMISSAO = "Você não tem permissão para visualizar este relatório"
MR07_FALHA_ARQUIVO = "Não foi possível gerar o arquivo. Tente novamente"
MR08_DESCRICAO_ATIVIDADES = "Orientações, coorientações e bancas de cada docente no período"
MR09_DESCRICAO_MEMBROS = (
    "Docentes e Membros Externos nas bancas realizadas, com as instituições de origem"
)
MR10_DESCRICAO_FORMACAO = "Situação dos alunos do período letivo, por curso"
MR11_DESCRICAO_HISTORICO = "Vinculados, defesas, artigos e desistências em cada período letivo"
MR12_DESCRICAO_PRODUCAO = "Trabalhos do período por curso, área de interesse ou modalidade"
MR13_DESCRICAO_ARTIGOS = "TCCs na modalidade Artigo Científico, com publicação e aproveitamento"
MR14_APROVEITAMENTO_SEM_ANALISE = "Aguardando aceite ou publicação"
