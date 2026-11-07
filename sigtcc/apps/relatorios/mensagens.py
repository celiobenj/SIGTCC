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

# MR-03 e MR-04 do Painel de atividades por docente. [US-31][RBN-REL-01.1]
COMO_ATIVIDADES = (
    "No período letivo, as orientações e coorientações contam pelas turmas do período. Numa troca "
    "de orientador, os dois docentes contam.",
    "Num intervalo de datas, conta o vínculo em vigor em algum dia do intervalo. Sem data de fim, "
    "o vínculo termina na data do Status final do TCC.",
    "Um intervalo que cruze a matrícula em TCC 2 conta o aluno em TCC 1 e em TCC 2. Depois da "
    "matrícula, o aluno Aprovado para TCC 2 conta até essa data.",
    "Cada aluno conta uma vez por coluna.",
    "Total de Bancas conta as sessões Realizadas em que o docente atuou como Presidente, 1º "
    "Avaliador, 2º Avaliador ou Suplente acionado.",
)
DEFINICAO_CURSO_LOTACAO = "Curso de Lotação do docente"
DEFINICAO_ORIENTANDOS_TCC_1 = "Alunos orientados em turmas de TCC 1"
DEFINICAO_ORIENTANDOS_TCC_2 = "Alunos orientados em turmas de TCC 2"
DEFINICAO_COORIENTACOES = "Coorientações aceitas"
DEFINICAO_BANCAS = (
    "Sessões Realizadas como Presidente, 1º Avaliador, 2º Avaliador ou Suplente acionado"
)

# MR-03 e MR-04 de Produção de TCCs e Artigos. [US-33][RBN-REL-02.1][RBN-REL-02.2]
COMO_PRODUCAO = (
    "Total de Trabalhos = Ativos + Com Sucesso + Sem Sucesso; os TCCs Sem Proposta não entram.",
    "Ativos: Em Andamento, Apto para Defesa, Aprovado e Aprovado com Correções sem Versão Final "
    "homologada. Com Sucesso: Concluído e Aprovado para TCC 2. Sem Sucesso: Reprovado, Desistente "
    "e Jubilado.",
    "Cada trabalho é contado pelo último Status do histórico do TCC na turma do período.",
    "Todos os Aprovados considera Aprovado para TCC 2, Aprovado, Aprovado com Correções e "
    "Concluído; Apenas Concluídos, somente Concluído.",
)
COMO_ARTIGOS = (
    "Lista os TCCs na modalidade Artigo Científico das turmas do período.",
    "O Orientador é o do vínculo ativo; sem ele, o do vínculo mais recente.",
)
DEFINICAO_TOTAL_TRABALHOS = "Ativos + Com Sucesso + Sem Sucesso"
DEFINICAO_ATIVOS = (
    "Em Andamento, Apto para Defesa, Aprovado e Aprovado com Correções sem Versão Final homologada"
)
DEFINICAO_COM_SUCESSO = "Concluído e Aprovado para TCC 2"
DEFINICAO_SEM_SUCESSO = "Reprovado, Desistente e Jubilado"
NAO_INFORMADA = "Não informada"
