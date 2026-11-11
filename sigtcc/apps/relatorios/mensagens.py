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

# MR-03 e MR-04 de Formação e evasão. [US-32][RBN-REL-02.3]
COMO_FORMACAO = (
    "Matriculados = Sem Proposta + Ativos + Com Sucesso + Sem Sucesso. Os cartões do topo não "
    "mostram Sem Proposta, por isso não somam Matriculados.",
    "Matriculados são os vínculos com as turmas do período, exceto os alunos excluídos da turma.",
    "Aprovado sem Versão Final homologada conta como Ativo.",
    "Cada aluno é contado pelo último Status do histórico do TCC na turma do período.",
)
DEFINICAO_MATRICULADOS = "Alunos vinculados às turmas do período, exceto os excluídos da turma"
DEFINICAO_SEM_PROPOSTA = "Alunos que ainda não salvaram a Proposta"

# MR-03 e MR-04 do Histórico de indicadores do NUCOMP. [US-32 A][RBN-REL-02.4]
COMO_HISTORICO = (
    "Cada indicador conta pelo período letivo da turma, porque os registros não têm data de "
    "semestre.",
    "Alunos Vinculados usa a mesma definição de Matriculados.",
    "Artigos Publicados conta cada artigo uma vez, no período do primeiro TCC do aluno com "
    "Publicado; se o link for alterado depois, as cópias contam como artigos diferentes.",
    "Desistências são as transições para Desistente no histórico das turmas do período.",
)
DEFINICAO_ALUNOS_VINCULADOS = "Alunos com vínculo em turmas do período"
DEFINICAO_DEFESAS_REALIZADAS = "Sessões com status Realizada"
DEFINICAO_ARTIGOS_PUBLICADOS = "Artigos com Status de Submissão Publicado"
DEFINICAO_DESISTENCIAS = "Transições para Desistente no período"

# MR-03 e MR-04 de Participação de Membros Externos. [US-47][RBN-REL-01.2]
COMO_MEMBROS = (
    "Conta pessoas distintas: quem participou de várias bancas conta uma vez.",
    "Entram só os membros efetivos das sessões Realizadas: Presidente, 1º e 2º Avaliador e o "
    "Suplente acionado.",
    "Cada instituição aparece como foi escrita no cadastro do Membro Externo.",
)
DEFINICAO_QUANTIDADE_PESSOAS = "Pessoas distintas nas sessões Realizadas do período"
ROTULO_DOCENTES_NUCOMP = "Docentes do NUCOMP"
ROTULO_MEMBROS_EXTERNOS = "Membros Externos"
ROTULO_INSTITUICAO = "Instituição de origem: {nome}"

# Relatórios operacionais (spec 011; Clarifications C10, índice Q-157): descrições MR-15 a MR-18,
# "Como é calculado" (MR-03) e definições de coluna (MR-04).
# [US-48][US-49][US-34][US-35][RBN-REL-03.1][RBN-REL-03.2][RBN-REL-03.3][RBN-REL-03.4]
MR15_DESCRICAO_DEFESAS = "Sessões Realizadas no período, com banca e parecer"
MR16_DESCRICAO_TURMAS = "Turmas do período com o Status do TCC de cada aluno"
MR17_DESCRICAO_ALUNO_ORIENTADOR = "Alunos de TCC 1 com o orientador; Aprovados para TCC 2 primeiro"
MR18_DESCRICAO_HORAS = "Presenças de ouvintes nas sessões Realizadas, 2 horas cada"

COMO_DEFESAS = (
    "Lista só as sessões com status Realizada, pela data da sessão no período escolhido.",
    "Orientador é quem presidiu a banca; Banca traz o 1º e o 2º Avaliador que atuaram, com o "
    "Suplente acionado no papel que ocupou.",
    "O Curso é o da turma do TCC da sessão. O Professor da Disciplina vê as sessões das suas "
    "turmas.",
)
COMO_TURMAS = (
    "Uma linha por turma do período letivo, com os alunos matriculados nela.",
    "O Status de cada aluno é o último registrado no histórico do TCC naquela turma; quem ainda "
    "não salvou a Proposta aparece como Sem Proposta.",
    "Reprovado, Desistente e Jubilado aparecem destacados. O Professor da Disciplina vê só as "
    "suas turmas.",
)
COMO_ALUNO_ORIENTADOR = (
    "Lista os alunos das turmas de TCC 1 do período letivo.",
    "Orientador é o do TCC na turma: o vínculo ativo ou, sem ele, o mais recente.",
    "O Status é o último registrado no histórico do TCC na turma: quem já foi matriculado em "
    "TCC 2 continua como Aprovado para TCC 2 no período de origem.",
    "Os Aprovados para TCC 2 vêm primeiro e destacados; depois, os demais, pelo nome.",
)
COMO_HORAS = (
    "Uma linha por presença de ouvinte em sessão Realizada do período: quem assistiu a 3 bancas "
    "aparece em 3 linhas.",
    "Cada presença vale 2 horas complementares; o Total soma as horas de todas as linhas.",
    "O Curso é o da turma do TCC da sessão. O Professor da Disciplina vê as sessões das suas "
    "turmas.",
)
DEFINICAO_ORIENTADOR_PRESIDENTE = "Orientador (Presidente) da banca da sessão"
DEFINICAO_BANCA_EFETIVA = "1º e 2º Avaliador que atuaram na sessão"
DEFINICAO_TOTAL_ALUNOS = "Alunos matriculados na turma"
DEFINICAO_STATUS_NA_TURMA = "Último Status registrado no histórico do TCC na turma"
DEFINICAO_ORIENTADOR_TCC_1 = "Orientador do TCC na turma de TCC 1"
DEFINICAO_HORAS = "2 horas complementares por presença"
TITULO_ALUNOS = "Alunos"
ROTULO_TOTAL = "Total"
