"""Descritores oficiais dos 9 critérios de avaliação (planilha "ECP AVALIAÇÃO DE TCC" da EST/UEA).

Textos copiados da planilha entregue pela professora (aba Avaliação_Orientador; as abas dos
avaliadores têm os mesmos textos), sem alterar palavras: só espaços sobrando e linhas em branco
foram retirados. Usados pela migração 0005_descritores_oficiais (FR-014a, Q-03 e Q-18).

[US-25][RBN-DEF-04.1][FR-014a]
"""

DESCRITORES_OFICIAIS = {
    "Relevância do Tema": {
        "cri_desc_exemplar": (
            "1. O tema tem relevância científica e aborda conteúdos e/ou pesquisas "
            "relacionadas ao estado da arte na área da Computação;\n"
            "2. O conteúdo do trabalho foi focado no tema e com profundidade adequada para "
            "um pleno entendimento do problema abordado;\n"
            "3. O tema conjuga de maneira não-trivial diferentes habillidades desenvolvidas "
            "pelo estudante ao longo do curso."
        ),
        "cri_desc_competente": (
            "1. A apresentação do tema não é embasada por argumentos que permitam destacar "
            "a sua relevância nem tampouco sua relação com a área da Computação;\n"
            "2. Em algumas ocasiões, não ficou clara a relação entre o conteúdo do trabalho "
            "e o tema proposto, podendo esta apresentação ter sido superficial ou pouco "
            "coesa para prover um bom entendimento do problema abordado;\n"
            "3. O tema conjuga múltiplas habilidades desenvolvidas pelo estudante ao longo "
            "do curso;"
        ),
        "cri_desc_necessita_trabalho": (
            "1. Há uma dissociação entre o tema e o seu embasamento, de tal modo que não é "
            "possível identificar sua relevância e possíveis contribuições para a área da "
            "Computação;\n"
            "2. O conteúdo do trabalho foge ao tema proposto;\n"
            "3. O tema conjuga superficialmente habilidades pontuais desenvolvidas pelo "
            "estudante ao longo do curso."
        ),
    },
    "Metodologia": {
        "cri_desc_exemplar": (
            "Metodologia está bem descrita, aderente aos objetivos propostos e com "
            "justificativas pautadas em critérios técnico-científicos."
        ),
        "cri_desc_competente": (
            "Metodologia está regular, pouco aderente aos objetivos propostos e com "
            "significativa necessidade de melhorias nas justificativas."
        ),
        "cri_desc_necessita_trabalho": (
            "Metodologia está severamente aquém da qualidade necessária e incompatível com "
            "o nível de formação almejado."
        ),
    },
    "Revisão da Literatura": {
        "cri_desc_exemplar": (
            "1. O documento apresenta revisão bibliográfica focada no tema e de "
            "profundidade adequada para o entendimento do trabalho;\n"
            "2. Apresenta seção de trabalhos relacionados, em quantidade adequada e "
            "comparando qualitativa e quantitativamente as características e resultados dos "
            "trabalhos correlatos;\n"
            "3. Há entendimento das normas de ABNT, sobretudo é possível verificar o "
            "emprego correto para citações e indicações de referências correlatas."
        ),
        "cri_desc_competente": (
            "1. Demonstra fundamento, porém a capacidade conceitual e articulação "
            "teórico-metodológica (ou teórico-prática) carece de melhorias;\n"
            "2. Apresenta seção de trabalhos relacionados, com quantidade adequada, porém "
            "necessita de um aprofundamento nos aspectos comparativos de ordem qualitativa "
            "e quantitativa;\n"
            "3. As referências adotadas, em certa medida, são adequadas e com certa "
            "atualidade, mas não foram muito além em termos de representatividade."
        ),
        "cri_desc_necessita_trabalho": (
            "1. A revisão bibliográfica é superficial ao tema, carecendo de conceitos "
            "elementares para o entendimento do trabalho;\n"
            "2. Compreende poucos trabalhos correlatos ou é inexistente, sendo insuficiente "
            "para o tema considerado;\n"
            "3. As referências adotadas são pouco adequadas, antigas e/ou insuficientes "
            "para sustentar o trabalho. Também há indícios de desleixo com relação as "
            "normas da ABNT."
        ),
    },
    "Resultados e Discussões": {
        "cri_desc_exemplar": (
            "Os resultados estão detalhados, mostram-se compatíveis com o prazo de "
            "desenvolvimento e condizentes com a metodologia apresentadas."
        ),
        "cri_desc_competente": (
            "Os resultados apresentados são regulares, mostrando-se limitados dado o prazo "
            "de desenvolvimento e/ou a metodologia apresentados."
        ),
        "cri_desc_necessita_trabalho": (
            "Não há evidências da obtenção dos resultados propostos para o prazo de "
            "desenvolvimento."
        ),
    },
    "Conclusões": {
        "cri_desc_exemplar": (
            "As conclusões apresentadas são fortemente coerentes com o trabalho "
            "desenvolvido e contemplam uma análise crítica e comparativa das suas vantagens "
            "e limitações.\n"
            "As sugestões para as próximas etapas do trabalho ou pesquisas futuras são "
            "resultado de uma reflexão bem pautadas em critérios técnico-científicos."
        ),
        "cri_desc_competente": (
            "As conclusões apresentadas são limitadas para descrever o trabalho "
            "desenvolvido, com grande potencial de melhoria na anállise crítica e "
            "comparativa das vantagens e limitações.\n"
            "As próximas etapas do trabalho precisam ser delicadamente revistas em face do "
            "cronograma disponível e/ou de critérios técnico-científicos."
        ),
        "cri_desc_necessita_trabalho": (
            "As considerações estão severamente aquém da qualidade necessária e são "
            "incompatíveis com o nível de formação almejado."
        ),
    },
    "Redação": {
        "cri_desc_exemplar": (
            "1. Escrito de forma organizada e sistemática, e há evidências de esforço dos "
            "autores para a elaboração de um texto que se preocupa com a compreensão do "
            "leitor;\n"
            "2. As informações são apresentadas de forma clara e explicitamente "
            "relacionadas aos aspectos que o texto dá suporte;\n"
            "3. Atende às boas práticas de comunicação escrita (linguagem, pontuação, "
            "ortografia, encadeamento das ideias, etc.); é organizado de forma lógica, "
            "facilitando a leitura, compreensão e localização de informações;\n"
            "4. Há aspectos a serem corrigidos e melhorados, mas o trabalho demonstra "
            "habilidade acima da média e atenção aos detalhes."
        ),
        "cri_desc_competente": (
            "1. O texto possui uma organização, porém apresenta algumas imprecisões que "
            "dificultam a compreensão do leitor;\n"
            "2. É possível observar qualidade técnica no texto, mas há perdas de conexões "
            "entre os aspectos que deveriam sustentar o trabalho;\n"
            "3. A apresentação das informações carece de melhorias, ou porque faltou "
            "clareza ou porque apresentou algumas lacunas na forma de relacionar "
            "explicitamente as informações aos aspectos estabelecidos na análise.\n"
            "4. O trabalho está na média, mas exigirá um pouco mais de esforço para "
            "deixá-lo no nível Exemplar."
        ),
        "cri_desc_necessita_trabalho": (
            "1. A escrita apresenta muitas faltas, dificultando a compreensão do leitor;\n"
            "2. O texto possui baixa qualidade técnica, com frequentes perdas de conexões "
            "entre os aspectos que deveriam sustentar o trabalho, podendo ser impreciso até "
            "mesmo no foco adotado;\n"
            "3. É pouco fundamentado, e demonstra muitas carências na capacidade conceitual "
            "e articulação teórico- metodológica (ou teórico-prática).\n"
            "4. O trabalho está severamente aquém da qualidade necessária para o nível de "
            "formação almejado."
        ),
    },
    "Organização": {
        "cri_desc_exemplar": (
            "1. Organizou e encadeou as ideias com conectores adequados e diversificados, "
            "sem repetições;\n"
            "2. Apresentou conjunto de slides com adequado conteúdo de informações a serem "
            "comunicadas, ótima qualidade e padronização dos textos e imagens;\n"
            "3. A apresentação fluiu conforme uma ótima sequencia lógica de apresentação "
            "das informações;\n"
            "4. Realizou a apresentação em tempo igual ou muito próximo ao tempo total "
            "disponível."
        ),
        "cri_desc_competente": (
            "1. Organizou e encadeou as ideias com poucos conectores e/ou com repetições, "
            "mas sem comprometer a compreensão do conteúdo;\n"
            "2. Apesar de alguns slides com problemas de qualidade visual e padronização, "
            "não houve prejuízo à compreensão do conteúdo;\n"
            "3. Houve desvios na sua sequência lógica, mas o entendimento não foi "
            "prejudicado. Eventualmente houve desproporcionalidade na exposição de alguns "
            "conteúdos;\n"
            "4. A apresentação foi além ou aquém do tempo disponível, eventualmente houve "
            "leitura do conteúdo dos slides, mas tais aspectos não comprometeram a "
            "apresentação com um todo."
        ),
        "cri_desc_necessita_trabalho": (
            "1. Não organizou nem encadeou as ideias com uso de conectores, limitando-se a "
            "justapor ideias de forma desarticulada e confusa;\n"
            "2. Apresentou conjunto de slides com total ausência de qualidade visual e "
            "padronização, contendo excesso de texto e incluindo imagens de baixa qualidade "
            "ou ilegíveis. Houve grave prejuízo ao acompanhamento da apresentação e ao "
            "entendimento do conteúdo;\n"
            "3. A apresentação oral deu-se majoritariamente por meio da leitura dos slides. "
            "Houve ausência de proporcionalidade entre a importância e volume de cada "
            "assunto;\n"
            "4. Realizou a apresentação de forma negligente, sub-utilizando o tempo "
            "disponível ou extrapolando-o, o que neste segundo caso impediu a conclusão da "
            "apresentação."
        ),
    },
    "Domínio do Assunto": {
        "cri_desc_exemplar": (
            "1- Organiza e encadeia as ideias com conectores adequados e diversificados, "
            "sem repetições.\n"
            "2- Expressa-se oralmente sem recurso à leitura dos slides.\n"
            "1. Adota uma atitude adequada, com gestos e expressões faciais coerentes e "
            "expressivos, que cativam a atenção do auditório e que reforçam a mensagem "
            "transmitida.\n"
            "2- Emprega um tom de voz audível e com entoação expressiva.\n"
            "3. Utiliza um estilo de linguagem (coloquial, literário ou técnico) adequado à "
            "(ao) situação/tema."
        ),
        "cri_desc_competente": (
            "1- Organiza e encadeia as ideias com recurso a conectores geralmente "
            "adequados, embora pouco diversificados e com repetições.\n"
            "2- Expressa-se oralmente recorrendo algumas vezes à leitura dos slides.\n"
            "1- Adota uma atitude geralmente adequada, com gestos e expressões faciais "
            "coerentes, ainda que pouco expressivas, que cativam pontualmente a atenção do "
            "auditório.\n"
            "2- Emprega um tom de voz audível e, pontualmente, com entoação expressiva.\n"
            "3. Utiliza um estilo de linguagem (coloquial, literário ou técnico) "
            "globalmente adequado à(ao) situação/tema, ainda que com falhas pontuais."
        ),
        "cri_desc_necessita_trabalho": (
            "1- Não organiza nem encadeia as ideias com recurso a conectores, limitando-se "
            "a justapor ideias de forma desarticulada e confusa.\n"
            "2- Expressa-se oralmente com recurso exclusivo à leitura dos slides.\n"
            "Adota uma atitude desadequada,\n"
            "negligente ou provocadora; ou emprega um tom de voz imperceptível ou "
            "estridente; ou utiliza um estilo de linguagem (coloquial, literário ou "
            "técnico) inadequado à(ao) situação/tema."
        ),
    },
    "Postura perante a Banca": {
        "cri_desc_exemplar": (
            "1- Compreendeu perfeitamente às arguições conseguindo respondê-las de imediato "
            "om propriedade, segurança, usando termos técnicos-científicos corretos e "
            "adequados;\n"
            "2. Demonstrou atitude positiva perante a banca, colocando-se a disposição para "
            "responder questionamentos de forma coerente e respeitosa;\n"
            "3. Demonstrou maturidade em compreender as sugestões de melhorias e/ou "
            "apontamento de erros feitos pela banca;\n"
            "4. Aceitou as considerações dos avaliadores de maneira respeitosa e esclareceu "
            "suas dúvidas de forma clara, objetiva e com segurança;\n"
            "5. Não realizou interrupções fora do tempo;"
        ),
        "cri_desc_competente": (
            "1. Precisou de intervenção do orientador para compreender algumas arguições, "
            "mas conseguiu responder de forma satisfatória;\n"
            "2. Demonstrou pouca resistência em aceitar as considerações da banca;\n"
            "3- Demonstrou compreender a maioria das sugestões de melhorias e possíveis "
            "erros apontados pela banca.\n"
            "5- Realizou mais de uma interrupção fora do tempo."
        ),
        "cri_desc_necessita_trabalho": (
            "1- Apesar da intervenção do orientador para compreender todas as arguições, "
            "não conseguiu respondê-las;.\n"
            "2- Demonstrou atitude negativa perante a banca, colocando-se em posição "
            "defensiva e/ou agressiva;\n"
            "3- Interrompeu diversas vezes os arguidores de forma desrespeitosa;\n"
            "4-Insistiu em defender suas ideias em relação ao trabalho, ainda que a banca "
            "tenha considerado insatisfatório."
        ),
    },
}
