**Cronograma do Projeto**

| **Projeto**         | SIGTCC – Sistema de Gestão de TCC do NUCOMP-UEA                                                                           | **Disciplina**                        | Engenharia de Software (ESTCMP025) |
|---------------------|---------------------------------------------------------------------------------------------------------------------------|---------------------------------------|------------------------------------|
| **Curso**           | Engenharia da Computação – UEA/EST                                                                                        | **Professora**                        | Diana Maria Camara de Carvalho     |
| **Turma / Período** | ECP06_T01 – 02-2026                                                                                                       | **Gerente do projeto (Scrum Master)** | Leandra das Chagas Matos           |
| **Equipe**          | Célio Lima Benjamim, Julia Cohen, Leandra das Chagas Matos, Maria Luísa Saraiva Gomes, Maria Luiza Nobre Vieira Guimarães | **Versão / Data**                     | 3.0 - 30/09/2026                   |

# **1. Abordagem de gestão**

> **Método:** Scrum, com o quadro “SIGTCC – Backlog e Sprints” no
> Trello. Cada atividade deste cronograma corresponde a um cartão do
> quadro, com o mesmo ID, datas e estimativa em horas.
>
> **Fontes:** Plano de Ensino, Matriz de Requisitos (Anexo A do Plano de
> Integração, planilha
> Matriz_Requisitos_SIGTCC_30_09:([<u>https://docs.google.com/spreadsheets/d/1lBcCRWC1EWeQz13y8Fg5Lb2ujcm1HWFW/edit?usp=sharing&ouid=102696095191280145494&rtpof=true&sd=true</u>](https://docs.google.com/spreadsheets/d/1lBcCRWC1EWeQz13y8Fg5Lb2ujcm1HWFW/edit?usp=sharing&ouid=102696095191280145494&rtpof=true&sd=true)
> ), EAP, Product Backlog e quadro do Trello.
>
> **Timebox:** Cada sprint é um intervalo de tempo fixo que termina em
> uma entrega do Plano de Ensino (TP1 a TP4); o Objetivo da Sprint fica
> registrado no quadro.
>
> **Controle:** ao final de cada sprint, o cronograma é revisado e os
> parâmetros H e FF são recalibrados com o esforço realizado. As
> alterações são registradas na seção 7.

# **2. Marcos do projeto**

| **Marco** | **Entrega**                         | **Data limite** | **Sprint**    | **Conteúdo principal**                                                                                                                                                                                                                       |
|-----------|-------------------------------------|-----------------|---------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| M1        | **TP1 – Primeiro trabalho parcial** | 30/09/2026      | Sprints 1 e 2 | Definição e planejamento inicial do projeto: Levantamento e documentação dos requisitos, prototipação inicial e planos de integração, escopo, EAP e cronograma.                                                                              |
| M2        | **TP2 – Segundo trabalho parcial**  | 21/10/2026      | Sprint 3      | Especificação e estruturação do sistema: Documentação de sistema, modelagem de dados, regras lógicas do módulo de Cadastro e atualização dos planos de projeto e de configuração.                                                            |
| M3        | **TP3 – Terceiro trabalho parcial** | 18/11/2026      | Sprint 4      | Consolidação do planejamento técnico e da qualidade: Evolução do modelo de dados e das regras lógicas, interface e documentos do módulo de Defesa, plano de teste, plano de avaliação por ponto de função e atualização do plano de projeto. |
| M4        | **TP4 – Quarto trabalho parcial**   | 09/12/2026      | Sprint 5      | Finalização e encerramento: Execução dos casos de teste, implementação dos relatórios, implantação em produção, fechamento do plano de projeto e formalização do encerramento.                                                               |

# **3. Método de estimativa e parâmetros**

As durações seguem a técnica de estimativa paramétrica: Quantidade de
trabalho (esforço em horas) dividida pela capacidade efetiva de quem
executa. Para cada atividade:

> **1.** Duração (dias úteis) D = ⌈ E ÷ (R × H × FF) ⌉
>
> **2.** Início = maior valor entre o início da sprint e o dia útil
> seguinte ao término das predecessoras
>
> **3.** Término = Início + (D − 1) dias úteis, descontando fins de
> semana e dias não úteis
>
> **4.** Folga = dias úteis entre o Término e o fim da sprint
>
> **5.** Capacidade da sprint = N × H × FF × dias úteis da sprint;
> Utilização = Carga (soma dos esforços) ÷ Capacidade

| **Símbolo** | **Parâmetro**                     | **Valor adotado**                                          | **Justificativa / fonte**                                                                                                                                                                                      |
|-------------|-----------------------------------|------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **E**       | **Esforço da atividade**          | Horas do cartão no Trello                                  | Estimativa registrada pela equipe em cada cartão. Convenção: “1 semana” = 40 h (5 dias úteis × 8 h).                                                                                                           |
| **R**       | **Nº de responsáveis**            | 1 a 5 (Equipe = 5)                                         | Definido por atividade na seção 4.                                                                                                                                                                             |
| **H**       | **Dedicação diária por membro**   | 4 h por dia útil                                           | Premissa da equipe: disciplina de 4 créditos cursada em paralelo a outras disciplinas. Revisada ao final de cada sprint.                                                                                       |
| **FF**      | **Fator de foco**                 | 0,80                                                       | Desconta 20% para as reuniões Scrum (planning, daily, review, retrospectiva), retrabalho e interrupções.                                                                                                       |
| **C**       | **Capacidade efetiva por pessoa** | H × FF = 3,2 h por dia útil                                | Calibração com a Sprint 2: três cartões de 16 h, com 1 responsável cada, planejados no Trello em 4 a 5 dias úteis (3,2 a 4,0 h/dia). Adotado o limite inferior, mais conservador.                              |
| **Cal**     | **Calendário de dias úteis**      | Segunda a sexta, exceto 12/10, 28/10, 02/11, 20/11 e 08/12 | Feriados nacionais e municipal de Manaus em 2026; 28/10 é ponto facultativo (Dia do Servidor) e não há aula nessa data no Plano de Ensino. O ponto facultativo de 15/10 (Dia do Professor) não foi descontado. |

# **4. Cronograma por sprint**

| **ID**                                                                              | **Atividade (cartão do Trello)**                                                                          | **Descrição e rastreabilidade (requisitos, backlog, EAP)**                                                                                                                                                                                                   | **Responsável**              | **Esforço (h)** | **Dur. (d.u.)** | **Predecessora.** | **Início** | **Término** | **Folga (d.u.)** | **Status**   |
|-------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------|-----------------|-----------------|-------------------|------------|-------------|------------------|--------------|
| **Sprint 1 – Objetivo: Parte 1/2 da primeira entrega de ES (14/09 a 24/09)**        |                                                                                                           |                                                                                                                                                                                                                                                              |                              |                 |                 |                   |            |             |                  |              |
| **1.1**                                                                             | **Levantar e analisar requisitos**                                                                        | Levantamento das necessidades do NUCOMP com as professoras-clientes e análise dos requisitos, classificados em alto nível (RAN), baixo nível (RBN) e não funcionais (ISO/IEC 25010), com prioridade MoSCoW. Entregável: matriz de requisitos.                | Equipe ++C (5)               | 40              | **8**           | —                 | 14/09      | 23/09       | 1                | Concluído    |
| **1.2**                                                                             | **Documentar requisitos (funcionais, de qualidade e de domínio)**                                         | Documentação da Matriz de Requisitos: 27 RANs e 186 RBNs, sendo 152 Must, 27 Should e 7 Could, além de 10 itens Won't Have.                                                                                                                                  | Equipe ++C (5)               | 40              | **8**           | —                 | 14/09      | 23/09       | 1                | Concluído    |
| **1.3**                                                                             | **Documentar plano de escopo**                                                                            | Plano de escopo do SIGTCC: 3 módulos/épicos (Cadastro, Defesa, Relatórios), EAP com 5 entregas e 19 pacotes de trabalho e exclusões do escopo (10 requisitos Won't Have).                                                                                    | Célio Benjamim               | 40              | **9**           | —                 | 14/09      | 24/09       | 0                | Concluído    |
| **Sprint 2 – Objetivo: Parte 2/2 e fechamento da primeira entrega (24/09 a 30/09)** |                                                                                                           |                                                                                                                                                                                                                                                              |                              |                 |                 |                   |            |             |                  |              |
| **2.1**                                                                             | **Documento do cronograma completo**                                                                      | Este documento: marcos do Plano de Ensino, sequenciamento, estimativa paramétrica das durações e capacidade da equipe por sprint.                                                                                                                            | Maria Luísa Gomes            | 16              | **4**           | —                 | 24/09      | 29/09       | 1                | Em andamento |
| **2.2**                                                                             | **Prototipação (baseada nos requisitos de domínio)**                                                      | Protótipo de telas a partir dos requisitos de domínio e de qualidade de uso, priorizando fluxos Must Have: login e primeiro acesso (RAN-CAD-07), proposta e TCC (RAN-CAD-08/09), agendamento e avaliação da defesa (RAN-DEF-01 a 06) e relatórios (RAN-REL). | Julia Cohen                  | 16              | **5**           | —                 | 23/09      | 29/09       | 1                | Concluído    |
| **2.3**                                                                             | **Backlog completo do produto**                                                                           | Product Backlog derivado da matriz: 3 épicos, 11 features e 40 US (25 em Cadastro, 10 em Defesa e 5 em Relatórios) , com critérios de aceitação rastreados aos RBNs.                                                                                         | Célio Benjamim               | 16              | **5**           | —                 | 23/09      | 29/09       | 1                | Concluído    |
| **2.4**                                                                             | **Documentar plano de integração**                                                                        | Plano de gerenciamento da integração: termo de abertura, controle integrado de mudanças (matriz de requisitos, backlog e cronograma) e critérios de encerramento. Gestão do Projeto.                                                                         | Leandra Matos                | 15              | **12**          | —                 | 14/09      | 29/09       | 1                | Concluído    |
| **2.5**                                                                             | **Refinamento final dos documentos entregáveis**                                                          | Revisão cruzada de consistência entre matriz de requisitos, EAP/backlog, planos, cronograma e protótipo; correção das inconsistências encontradas e empacotamento da entrega do TP1.                                                                         | Maria Luiza Guimarães        | 16              | **3**           | —                 | 28/09      | 30/09       | 0                | Em andamento |
| **M1**                                                                              | **ENTREGA DO TP1**                                                                                        |                                                                                                                                                                                                                                                              | Equipe ++C (5)               | —               | —               | 2.5               | 30/09      | 30/09       | —                | **Marco**    |
| **Sprint 3 – Objetivo: entrega do TP2 (01/10 a 21/10)**                             |                                                                                                           |                                                                                                                                                                                                                                                              |                              |                 |                 |                   |            |             |                  |              |
| **3.1**                                                                             | **Documentação de sistema: casos de uso/US, sequência, componentes, pacotes e implantação (UML ou C4)**   | Documentação de sistema a partir do backlog: casos de uso/US, diagramas de sequência dos fluxos críticos (orientação, agendamento e avaliação da defesa), componentes, pacotes e implantação.                                                                | Maria Luísa Gomes            | 16              | **5**           | —                 | 01/10      | 07/10       | 9                | A fazer      |
| **3.2**                                                                             | **Modelo lógico e físico de dados; implementação do modelo de dados**                                     | Modelos lógico e físico e implementação do banco: usuários, turmas, salas, TCC, atividades, orientação e atas, publicações, sessões, bancas e avaliação.                                                                                                     | Maria Luiza Guimarães        | 16              | **5**           | —                 | 01/10      | 07/10       | 9                | A fazer      |
| **3.3**                                                                             | **Implementação da camada de interface e das regras lógicas**                                             | Interface e regras lógicas do Épico 1 (Cadastro): contas e acesso, proposta, TCC, entregas, orientação e atas, priorizando os RBNs Must Have.                                                                                                                | Julia Cohen                  | 16              | **5**           | 3.1, 3.2          | 08/10      | 15/10       | 4                | A fazer      |
| **3.4**                                                                             | **Atualização do plano de projeto (risco, RH, partes interessadas, comunicação) e plano de configuração** | Atualização do plano de projeto (riscos, recursos humanos, partes interessadas, comunicação) e plano de gerenciamento de configuração (repositório Git, versionamento da matriz e do backlog).                                                               | Célio Benjamim               | 16              | **5**           | 3.1               | 08/10      | 15/10       | 4                | A fazer      |
| **3.5**                                                                             | **Revisão final dos entregáveis do TP2**                                                                  | Consistência entre documentação, modelo de dados, regras implementadas e planos atualizados.                                                                                                                                                                 | Leandra Matos                | 15              | **1**           | 3.3, 3.4          | 16/10      | 16/10       | 3                | A fazer      |
| **M2**                                                                              | **ENTREGA DO TP2**                                                                                        |                                                                                                                                                                                                                                                              | Equipe ++C (5)               | —               | —               | 3.5               | 21/10      | 21/10       | —                | **Marco**    |
| **Sprint 4 – Objetivo: entrega do TP3 (22/10 a 18/11)**                             |                                                                                                           |                                                                                                                                                                                                                                                              |                              |                 |                 |                   |            |             |                  |              |
| **4.1**                                                                             | **Atualização do modelo de dados e das regras lógicas**                                                   | Modelo de dados e regras lógicas do Épico 2 (Defesa): sessão, banca, conflito de horário e sala (US-22), critérios e cálculo de notas.                                                                                                                       | Leandra Matos                | 16              | **5**           | —                 | 22/10      | 29/10       | 13               | A fazer      |
| **4.2**                                                                             | **Plano de avaliação do projeto por ponto de função**                                                     | Contagem de pontos de função das funcionalidades da matriz e estimativa de esforço e valor do projeto (pacote 1.3 da EAP).                                                                                                                                   | Maria Luísa Gomes            | 16              | **5**           |                   | 22/10      | 29/10       | 13               | A fazer      |
| **4.3**                                                                             | **Documento de plano de teste de software**                                                               | Plano de teste: níveis e tipos de teste, ambiente e critérios de entrada e saída; casos de teste derivados dos critérios de aceitação das US e priorizados por MoSCoW.                                                                                       | Maria Luiza Guimarães        | 16              | **5**           | 4.1               | 30/10      | 06/11       | 8                | A fazer      |
| **4.4**                                                                             | **Interface e documentos do módulo de Defesa**                                                            | Telas de agendamento, composição da banca e avaliação; geração da Ata Final e da Folha de Aprovação em PDF com as imagens das assinaturas (US-21 a US-28; pacotes 3.2 a 3.4 da EAP).                                                                         | Célio Benjamim               | 16              | **5**           | 4.2               | 30/10      | 06/11       | 3                | A fazer      |
| **4.5**                                                                             | **Registro de ouvintes e agenda de defesas**                                                              | Registro de nome e matrícula dos ouvintes por sessão e agenda de defesas em PDF (US-30; pacote 3.5 da EAP).                                                                                                                                                  | Equipe ++C (5)               | 15              | **1**           | 4.3               | 30/10      | 04/11       | 2                | A fazer      |
| **4.6**                                                                             | **Atualização do plano de projeto**                                                                       | Atualização do plano de projeto e do plano de qualidade (qualidade de produto conforme os requisitos não funcionais ISO/IEC 25010 da matriz, riscos e cronograma)                                                                                            | Julia Cohen                  | 16              | **5**           | 4.1               | 09/11      | 13/11       | 8                | A fazer      |
| **4.7**                                                                             | **Revisão final dos entregáveis**                                                                         | Consistência entre modelo de dados, regras, interface e documentos da Defesa, plano de teste, plano de projeto e estimativa por ponto de função; empacotamento da entrega.                                                                                   | Leandra Matos                | 8               | **3**           | 4.1               | 16/11      | 16/11       | 10               | A fazer      |
| **M3**                                                                              | **ENTREGA DO TP3**                                                                                        |                                                                                                                                                                                                                                                              | Equipe ++C (5)               | —               | —               | 4.4               | 18/11      | 18/11       | —                | **Marco**    |
| **Sprint 5 – Objetivo: entrega do TP4 e encerramento do projeto (19/11 a 09/12)**   |                                                                                                           |                                                                                                                                                                                                                                                              |                              |                 |                 |                   |            |             |                  |              |
| **5.1**                                                                             | **Implementar os casos de teste de software**                                                             | Implementação e execução dos casos de teste, com registro de defeitos e correções e rastreabilidade RBN - US - caso de teste.                                                                                                                                | Maria Luiza Guimarães        | 15              | **5**           | —                 | 19/11      | 26/11       | 8                | A fazer      |
| **5.2**                                                                             | **Implementação dos relatórios**                                                                          | Relatórios do Épico 3: docentes e bancas, produção acadêmica e operacionais, com filtro por período letivo e exportação em PDF, CSV e XLSX.                                                                                                                  | Julia Cohen e Célio Benjamim | 15              | **3**           | —                 | 19/11      | 26/11       | 10               | A fazer      |
| **5.3**                                                                             | **Implantação em produção**                                                                               | Publicação do sistema no ambiente de produção (Django e PostgreSQL em nuvem), configuração do envio de e-mail e carga inicial de dados reais (salas, docentes e uma turma piloto).                                                                           | Leandra Matos                | 16              | **5**           | 5.1, 5.2          | 27/11      | 03/12       | 3                | A fazer      |
| **5.4**                                                                             | **Atualização e fechamento do plano de projeto; termo de encerramento**                                   | Fechamento do plano de projeto: Termo de encerramento e aceite das entregas.                                                                                                                                                                                 | Maria Luísa Gomes            | 15              | **5**           | 5.1, 5.2          | 27/11      | 03/12       | 3                | A fazer      |
| **5.5**                                                                             | **Revisão final e homologação**                                                                           | Homologação com as professoras-clientes no ambiente de produção, correção de pendências e conferência dos entregáveis do TP4.                                                                                                                                | Equipe ++C (5)               | 15              | **1**           | 5.3, 5.4          | 04/12      | 07/12       | 2                | A fazer      |
| **M4**                                                                              | **ENTREGA DO TP4**                                                                                        |                                                                                                                                                                                                                                                              | Equipe ++C (5)               | —               | —               | 5.4               | 09/12      | 09/12       | —                | **Marco**    |

# **5. Capacidade e carga por sprint**

<table>
<colgroup>
<col style="width: 6%" />
<col style="width: 14%" />
<col style="width: 7%" />
<col style="width: 10%" />
<col style="width: 9%" />
<col style="width: 8%" />
<col style="width: 42%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>Sprint</strong></th>
<th><strong>Janela</strong></th>
<th><strong>Dias úteis</strong></th>
<th><strong>Capacidade (h)</strong></th>
<th><strong>Carga (h)</strong></th>
<th><strong>Utilização</strong></th>
<th><strong>Leitura</strong></th>
</tr>
<tr class="odd">
<th><strong>Sprint 1</strong></th>
<th>14/09 a 24/09</th>
<th>9</th>
<th>144</th>
<th>120</th>
<th><strong>83%</strong></th>
<th>Sprint executada; carga próxima da capacidade.</th>
</tr>
<tr class="header">
<th><strong>Sprint 2</strong></th>
<th>24/09 a 30/09</th>
<th>5</th>
<th>80</th>
<th>79</th>
<th><strong>99%</strong></th>
<th>Sprint executada; carga praticamente igual à capacidade</th>
</tr>
<tr class="odd">
<th><strong>Sprint 3</strong></th>
<th>01/10 a 21/10</th>
<th>14</th>
<th>224</th>
<th>79</th>
<th><strong>35%</strong></th>
<th>Estimativas preliminares dos cartões; utilização baixa indica margem
para refinar o escopo no Sprint Planning.</th>
</tr>
<tr class="header">
<th><strong>Sprint 4</strong></th>
<th>22/10 a 18/11</th>
<th>18</th>
<th>288</th>
<th>103</th>
<th><strong>36%</strong></th>
<th>Estimativas preliminares dos cartões, inclui interface e documentos
da Defesa, ouvintes e agenda e ponto de função</th>
</tr>
<tr class="odd">
<th><strong>Sprint 5</strong></th>
<th>19/11 a 09/12</th>
<th>13</th>
<th>208</th>
<th>76</th>
<th><strong>37%</strong></th>
<th>Estimativas preliminares dos cartões, inclui a implantação em
produção; utilização baixa indica margem para refinar o escopo no Sprint
Planning.</th>
</tr>
<tr class="header">
<th><strong>Total</strong></th>
<th>14/09 a 09/12</th>
<th><strong>59</strong></th>
<th><strong>944</strong></th>
<th><strong>457</strong></th>
<th><strong>48%</strong></th>
<th><p>As janelas das Sprints 1 e 2 compartilham o dia 24/09; ele é</p>
<p>contado nas duas.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **6. Acompanhamento da Execução real**

| **ID**                                                                              | **Atividade**                                                                     | **Responsável**       | **Início planejado** | **Término planejado** | **Início real** | **Novo Término planejado** | **Término real** | **Status**     |
|-------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|-----------------------|----------------------|-----------------------|-----------------|----------------------------|------------------|----------------|
| **Sprint 1 – Objetivo: Parte 1/2 da primeira entrega de ES (14/09 a 24/09)**        |                                                                                   |                       |                      |                       |                 |                            |                  |                |
| **1.1**                                                                             | **Levantar e analisar requisitos**                                                | Equipe ++C (5)        | 14/09                | 23/09                 | 14/09           | 23/09                      | 23/09            | Concluído      |
| **1.2**                                                                             | **Documentar requisitos (funcionais, de qualidade e de domínio)**                 | Equipe ++C (5)        | 14/09                | 23/09                 | 14/09           | 23/09                      | 23/09            | Concluído      |
| **1.3**                                                                             | **Documentar plano de escopo**                                                    | Célio Benjamim        | 14/09                | 24/09                 | 16/09           | 26/09                      | 25/09            | Concluído      |
| **Sprint 2 – Objetivo: Parte 2/2 e fechamento da primeira entrega (24/09 a 30/09)** |                                                                                   |                       |                      |                       |                 |                            |                  |                |
| **2.1**                                                                             | **Documento do cronograma completo**                                              | Maria Luísa Gomes     | 24/09                | 29/09                 | 24/09           | 30/09                      | 30/09            | Concluído      |
| **2.2**                                                                             | **Prototipação (baseada nos requisitos de domínio)**                              | Julia Cohen           | 23/09                | 29/09                 | 23/09           | 30/09                      | 30/09            | Concluído      |
| **2.3**                                                                             | **Backlog completo do produto**                                                   | Célio Benjamim        | 23/09                | 29/09                 | 23/09           | 29/09                      | 29/09            | Concluído      |
| **2.4**                                                                             | **Documentar plano de integração**                                                | Leandra Matos         | 14/09                | 29/09                 | 14/09           | 30/09                      | 30/09            | Concluído      |
| **2.5**                                                                             | **Refinamento final dos documentos entregáveis**                                  | Maria Luiza Guimarães | 28/09                | 30/09                 | 28/09           | 30/09                      | 30/09            | Concluído      |
| **M1**                                                                              | **ENTREGA DO TP1**                                                                | Equipe ++C (5)        | 30/09                | 30/09                 | 30/09           | 30/09                      | 30/09            | **Marco**      |
| **Sprint 3 – Objetivo: entrega do TP2 (01/10 a 21/10)**                             |                                                                                   |                       |                      |                       |                 |                            |                  |                |
| **3.1**                                                                             | **Documentação de sistema: US,**                                                  | Maria Luísa Gomes     | 01/10                | 07/10                 | 07/10           | 18/10                      | 18/10            | Concluído      |
| **3.1**                                                                             | **Documentação de sistema: Diagrama de sequência**                                | Maria Luísa Gomes     | 01/10                | 07/10                 | 17/10           | 19/10                      |                  | Revisão        |
| **3.1**                                                                             | **Documentação de sistema:** Diagrama de componentes                              | Maria Luísa Gomes     | 01/10                | 07/10                 | 20/10           | 22/10                      | 20/10            | Concluído      |
| **3.1**                                                                             | **Documentação de sistema:** Diagrama de classe                                   | Maria Luísa Gomes     | 01/10                | 07/10                 | 19/10           | 20/10                      |                  | Em andamento   |
| **3.1**                                                                             | **Documentação de sistema:** Diagrama de pacotes                                  | Maria Luísa Gomes     | 01/10                | 07/10                 | 20/10           | 22/10                      | 20/10            | Concluído      |
| **3.1**                                                                             | **Documentação de sistema: Diagrama de implantação**                              | Maria Luísa Gomes     | 01/10                | 07/10                 | 20/10           | 22/10                      | 20/10            | Concluído      |
| **3.1**                                                                             | **Documentação de sistema: US**                                                   | Célio Benjamim        | 01/10                | 07/10                 | 07/10           | 18/10                      | 18/10            | Concluído      |
| **3.1**                                                                             | **Documentação de sistema: US**                                                   | Leandra Matos         | 01/10                | 07/10                 | 07/10           | 18/10                      | 18/10            | Concluído      |
| **3.1**                                                                             | **Documentação de sistema: US**                                                   | Julia Cohen           | 01/10                | 07/10                 | 07/10           | 18/10                      | 18/10            | Concluído      |
| **3.1**                                                                             | **Documentação de sistema: US**                                                   | Maria Luiza Guimarães | 01/10                | 07/10                 | 07/10           | 18/10                      | 18/10            | Concluído      |
| **3.1**                                                                             | **Documentação de sistema:** Diagrama de sequência                                | Célio Benjamim        | 01/10                | 07/10                 | 19/10           | 19/10                      |                  | Revisão        |
| **3.1**                                                                             | **Documentação de sistema:** Diagrama de sequência                                | Leandra Matos         | 01/10                | 07/10                 | 16/10           | 19/10                      |                  | Revisão        |
| **3.1**                                                                             | **Documentação de sistema:** Diagrama de sequência                                | Julia Cohen           | 01/10                | 07/10                 | 16/10           | 19/10                      |                  | Revisão        |
| **3.1**                                                                             | **Documentação de sistema: Diagrama de sequência**                                | Maria Luiza Guimarães | 01/10                | 07/10                 | 16/10           | 19/10                      | 20/10            | Concluído      |
| **3.2**                                                                             | **Modelo lógico de dados; implementação do modelo de dados**                      | Maria Luiza Guimarães | 01/10                | 07/10                 | 06/10           | 16/10                      | 17/10            | Concluído      |
| **3.2**                                                                             | **Modelo físico de dados; implementação do modelo de dados**                      | Maria Luiza Guimarães | 01/10                | 07/10                 | 18/10           | 20/10                      | 19/10            | Concluído      |
| **3.3**                                                                             | **Implementação da camada de interface e das regras lógicas**                     | Julia Cohen           | 08/10                | 15/10                 | 18/10           | 23/10                      |                  | Em andamento   |
| **3.4**                                                                             | **Atualização do plano de projeto (risco, RH, partes interessadas, comunicação)** | Célio Benjamim        | 08/10                | 15/10                 |                 | Tp3 - 13/11                |                  | Adiado/A fazer |
| **3.4**                                                                             | **Plano de configuração**                                                         | Célio Benjamim        | 08/10                | 15/10                 | 16/10           | 18/10                      | 18/10            | Concluído      |
| **3.5**                                                                             | **Revisão final dos entregáveis do TP2**                                          | Leandra Matos         | 16/10                | 16/10                 |                 | 23/10                      |                  | A fazer        |
| **M2**                                                                              | **ENTREGA DO TP2**                                                                | Equipe ++C (5)        | 21/10                | 21/10                 | 23/10           | 23/10                      | 23/10            | **Marco**      |

# 

# **7. Matriz RACI**

**R – Responsible (Executor):** Quem desenvolve e executa a entrega.

**A – Accountable (Aprovador / Dono):** O responsável final pela entrega
(apenas **1 por linha**).

**C – Consulted (Consultado):** Quem presta apoio técnico ou tira
dúvidas.

**I – Informed (Informado):** Quem é apenas notificado do status

| Épico / Feature / Entrega técnica.                | Requisitos                                                                                 | Célio Benjamim | Julia Cohen | Leandra Matos | Maria Luísa Gomes | Maria Luiza Guimarães |
|---------------------------------------------------|--------------------------------------------------------------------------------------------|----------------|-------------|---------------|-------------------|-----------------------|
| 1\. Gestão de Contas, Acesso e Permissões         | US-03 a US-06, US-39 (Perfis, papéis de usuário, permissões e filtros por curso)           | C              | C           | A             | R                 | C                     |
| 2\. Autenticação, Turmas e Matrículas             | US-07 a US-12, US-37, US-38 (Login, vincular alunos/professores a turmas e histórico)      | C              | R           | A             | C                 | C                     |
| 3\. Proposta, Orientação e Vida do TCC            | US-13 a US-20, US-29, US-36 (Submissão de proposta, aceite de orientação e acompanhamento) | C              | C           | R / A         | C                 | C                     |
| 4\. Agendamento, Bancas e Defesas                 | US-21 a US-28, US-30, US-40 (Marcação de banca, comissão avaliadora e gestão de ouvintes)  | R              | C           | A             | C                 | C                     |
| 5\. Emissão de Atas e Documentos Oficiais         | US-25 a US-28 (Geração de PDFs de ata, folha de aprovação e certificados)                  | R              | C           | A             | C                 | C                     |
| 6\. Entregas Finais e Termos de Versão            | US-41 a US-46 (Envio de versão final, validação de orientador e termo de autorização)      | C              | C           | R / A         | C                 | C                     |
| 7\. Relatórios Acadêmicos e Gerenciais            | US-31 a US-35, US-47 a US-49 (Métricas de aprovação, evasão, bancas e carga horária)       | C              | C           | A             | C                 | R                     |
| 8\. Levantamento de Requisitos e Escopo           | Mapeamento de regras de negócio, elicitação e documento de plano de escopo                 | R              | R           | A             | R                 | R                     |
| 9\. Arquitetura e Modelagem do Sistema            | Diagramas UML/C4, Arquitetura MVC (Django) e Especificação de APIs                         | C              | C           | A             | R                 | C                     |
| 10\. Engenharia e Modelagem de Dados              | Modelo Lógico, Modelo Físico e Scripts do Banco de Dados PostgreSQL                        | C              | C           | A             | C                 | R                     |
| 11\. Prototipação e Interface (UI/UX)             | Protótipo de telas navegáveis, componentes visuais e usabilidade                           | C              | R           | A             | C                 | C                     |
| 12\. Planejamento, Backlog e Gestão do Cronograma | Escrita do Product Backlog (USs), estimativa de esforço e cronograma do projeto            | R              | C           | A             | R                 | C                     |
| 13\. Plano de Testes e Garantia de Qualidade      | Casos de teste, execução de testes unitários/sistema e contagem de Pontos de Função        | C              | C           | A             | C                 | R                     |
| 14\. Implantação, Deploy e Homologação            | Configuração de ambiente de produção, deploy e homologação com cliente                     | R              | R           | R / A         | R                 | R                     |

# **8. Premissas, restrições**

> Premissa: H = 4 h e FF = 0,80 valem para todos os membros e são
> recalibrados a cada sprint com o esforço realizado.
>
> Premissa: As estimativas em horas dos cartões das Sprints 3 a 5 são
> preliminares e serão refinadas no Sprint Planning de cada sprint.
>
> Restrição: As datas TP1 a TP4 são fixas (Plano de Ensino); o que se
> ajusta é o escopo de cada sprint, nunca a data de entrega.
>
> Restrição: Os dias não úteis de 12/10, 28/10, 02/11, 20/11 e 08/12
> reduzem a capacidade das Sprints 3 a 5.

# **9. Diagrama de Gantt**

O cronograma do projeto foi elaborado com base no ciclo de
desenvolvimento ágil por *Sprints*. Para otimizar a visualização e a
rastreabilidade das atividades no Diagrama de Gantt, a execução está
apresentada de forma agrupada (Sprints 1 e 2, Sprints 3 e 4, Sprint 5),
para melhor visualização.

Figura
1 - Diagrama de Gantt com a Sprint 1 e 2



Figura 2 - Diagrama de Gantt com a Sprint 3 e 4



Figura 3 - Diagrama de Gantt com a Sprint 5

# **8. Controle de versões e aprovação**

| **Versão** | **Data**   | **Descrição da alteração**                                                                                                                                                                                                                                                         | **Autor**                 |
|------------|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------|
| 1.0        | 27/09/2026 | Criação do cronograma com base no Plano de Ensino e no quadro do Trello.                                                                                                                                                                                                           | Maria Luísa Saraiva Gomes |
| 2.0        | 29/09/2026 | Definição das responsabilidades de cada membro considerando o sequenciamento das atividades.                                                                                                                                                                                       | Maria Luísa Saraiva Gomes |
| 3.0        | 30/09/2026 | Estimativa paramétrica das durações (esforço, capacidade e calendário), datas alinhadas ao Trello, descrições vinculadas à Matriz de Requisitos e ao Product Backlog.                                                                                                              | Maria Luísa Saraiva Gomes |
| 4.0        | 18/10/2026 | Inclusão da tabela de acompanhamento de execução real para preservar a *baseline* original. Também, foi realizado o alinhamento da Matriz RACI para detalhar explicitamente as responsabilidades de arquitetura, modelagem de dados e artefatos de documentação técnica por membro | Maria Luísa Saraiva Gomes |



Aprovação: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
(Scrum Master)
\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
(Professora) Data: \_\_\_/\_\_\_\_/\_\_\_\_\_\_
