**TEMPLATE DAS HISTÓRIAS DE USUÁRIO**

**SIGTCC \| Sistema de Gestão de TCC do NUCOMP-UEA**

| **Nome do Projeto:**   | Sistema de Gestão de TCC do NUCOMP-UEA (SIGTCC)                                        |
|------------------------|----------------------------------------------------------------------------------------|
| **Instituição:**       | UEA – Universidade do Estado do Amazonas (NUCOMP)                                      |
| **Disciplina:**        | Engenharia de Software (ESTCMP025), período 2026/2                                     |
| **Equipe do Projeto:** | Célio Benjamim, Julia Cohen, Leandra Matos, Maria Luísa Gomes e Maria Luiza Guimarães. |
| **Data de entrega:**   | 07/10/2026                                                                             |

# Como usar este documento

- As 40 US estão agrupadas por responsável, na ordem da tabela abaixo, e
  > o responsável também aparece na tabela de identificação de cada US.
  > As mudanças de lógica de 17/10, que seguem a nova Matriz de
  > Requisitos, estão destacadas em amarelo.

- Toda US usa o mesmo template, nesta ordem: identificação, descrição,
  > atores, pré-condições, fluxo principal, fluxos alternativos, fluxos
  > de exceção, pós-condições, regras aplicáveis, critérios de aceite,
  > tela no protótipo, diagrama de sequência e checklist.

- Atores, pré-condições, fluxos de exceção e pós-condições estão em
  > branco. O texto em cinza orienta o preenchimento e deve ser
  > substituído.

- Em "Diagrama de sequência", o diagrama relacionado já vem indicado
  > quando existe. Informe o link do diagrama no campo "Link" logo
  > abaixo. Se a US não tiver diagrama próprio, mantenha o motivo e
  > apague o campo.

- Ao terminar uma US, marque o checklist "Pronta para desenvolver" e
  > peça a revisão de outra pessoa.

[Como usar este documento 1](#)

[Célio Benjamim: Defesa 4](#)

> [US-21 Agendar a defesa 4](#)
>
> [US-22 Impedir agendamentos conflitantes 8](#)
>
> [US-23 Compor a banca 12](#)
>
> [US-24 Notificar a banca e atualizar o status da sessão 18](#)
>
> [US-40 Ver a lista de sessões de defesa e filtrar por período 24](#)
>
> [US-25 Lançar as notas dos critérios oficiais 28](#)
>
> [US-26 Enviar a imagem da assinatura 36](#)
>
> [US-27 Liberar o resultado final 39](#)
>
> [US-28 Gerar a Ata Final e a Folha de Aprovação 43](#)
>
> [US-30 Registrar ouvintes e gerar a agenda em PDF 46](#)

[Leandra Matos: Vida do TCC 50](#)

> [US-13 Registrar a Proposta, cadastrar os dados do TCC e alterar o
> tema 50](#)
>
> [US-14 Atualizar o Status do TCC e consultar o histórico e a trilha
> 55](#)
>
> [US-43 Cadastrar as entregas da turma 59](#)
>
> [US-15 Enviar ou substituir o link de uma entrega 63](#)
>
> [US-16 Acompanhar as entregas dos alunos da turma 68](#)
>
> [US-29 Enviar a Versão Final do TCC 2 70](#)
>
> [US-44 Homologar ou devolver para ajuste a Versão Final do TCC 2
> 74](#)
>
> [US-17 Indicar, cancelar ou trocar o orientador 79](#)
>
> [US-18 Aceitar ou recusar pedido de orientação e consultar o painel de
> orientandos 83](#)
>
> [US-45 Registrar, substituir ou remover coorientadores 88](#)
>
> [US-36 Aceitar ou recusar o convite de coorientação e acompanhar o
> trabalho no painel de orientandos 92](#)
>
> [US-19 Registrar, consultar, editar e comentar atas de orientação
> 96](#)
>
> [US-46 Registrar a publicação do artigo
> 101](#us-46-registrar-a-publicação-do-artigo)
>
> [US-20 Homologar ou recusar o aproveitamento do artigo
> 104](#us-20-homologar-ou-recusar-o-aproveitamento-do-artigo)
>
> [US-41 Ver os alunos da turma e o painel de cada aluno
> 108](#us-41-ver-os-alunos-da-turma-e-o-painel-de-cada-aluno)
>
> [US-42 Indicar que o TCC está apto para defesa
> 111](#us-42-indicar-que-o-tcc-está-apto-para-defesa)

[Julia Cohen: Turmas e acesso 114](#)

> [US-07 Gerenciar turmas de TCC 114](#us-07-gerenciar-turmas-de-tcc)
>
> [US-08 Matricular alunos na turma 118](#)
>
> [US-09 Excluir aluno da turma 122](#)
>
> [US-10 Criar a senha no primeiro acesso 125](#)
>
> [US-11 Fazer login 131](#)
>
> [US-12 Recuperar ou alterar a senha 135](#)
>
> [US-37 Reenviar o link de ativação vencido 138](#)
>
> [US-38 Editar o perfil e ver as notificações 141](#)

[Maria Luísa Gomes: Contas e filtro de curso 145](#)

> [US-03 Cadastrar e alterar docentes e secretaria 145](#)
>
> [US-04 Inativar e reativar docentes e secretaria 156](#)
>
> [US-05 Cadastrar e alterar membros externos 165](#)
>
> [US-06 Expirar o acesso de membros externos 172](#)
>
> [US-39 Filtrar listas e relatórios por curso 177](#)

[Maria Luiza Nobre: Relatórios 181](#)

> [US-31 Consultar e exportar o painel de atividades por docente 181](#)
>
> [US-47 Consultar e exportar o relatório de participação de Membros
> Externos 184](#)
>
> [US-32 Consultar e exportar o relatório de formação e evasão e o
> histórico de indicadores do NUCOMP 188](#)
>
> [US-33 Consultar e exportar os relatórios de produção de TCCs e de
> artigos 192](#)
>
> [US-48 Consultar e exportar a lista de defesas realizadas no período
> 196](#)
>
> [US-49 Consultar e exportar o relatório de turmas e alunos 199](#)
>
> [US-34 Consultar e exportar o relatório de aluno e orientador para
> apoio à matrícula
> 202](#us-34-consultar-e-exportar-o-relatório-de-aluno-e-orientador-para-apoio-à-matrícula)
>
> [US-35 Consultar e exportar o relatório de horas complementares de
> ouvintes
> 205](#us-35-consultar-e-exportar-o-relatório-de-horas-complementares-de-ouvintes)
>
> [US-50 Prorrogar o acesso de membro externo
> 208](#us-50-prorrogar-o-acesso-de-membro-externo)

# Célio Benjamim: Defesa

## US-21 Agendar a defesa

| **Épico:**                | Gestão da Defesa           |
|---------------------------|----------------------------|
| **Feature:**              | Agendamento e Banca        |
| **Requisitos da matriz:** | RBN-DEF-01.1, RBN-DEF-01.3 |
| **Prioridade (MoSCoW):**  | Must Have                  |
| **Responsável:**          | Célio Benjamim             |

**Descrição**

Como Orientador ou Professor da Disciplina, quero agendar a data,
horário e local ou link da defesa, para que a sessão fique oficialmente
marcada no calendário acadêmico.

**Atores**

> **Ator principal:** Orientador (no curso de Engenharia de Computação)
> ou Professor da Disciplina (nos cursos de Sistemas de Informação e
> Licenciatura em Computação).
>
> **Atores secundários:** Membros da banca examinadora (Orientador,
> avaliadores e suplente) e Aluno do TCC.

**Pré-condições**

- O Orientador ou Professor da Disciplina está autenticado no sistema,
  > com o Status da Conta Ativa (US-11). Sem sessão ativa, aplica-se o
  > E1.

- O TCC a ser defendido está com o Status do TCC Apto para Defesa
  > (RBN-CAD-11.5). A entrega do Documento para Defesa já foi conferida
  > na indicação de aptidão (US-42) e não é verificada novamente nesta
  > US.

- O TCC não possui outra sessão de defesa com status Agendada,
  > Reagendada ou Em Andamento.

- O Orientador ou Professor da Disciplina tem perfil e acesso
  > correspondentes ao curso da turma do TCC (Orientador em Engenharia
  > de Computação; Professor da Disciplina em Sistemas de Informação ou
  > Licenciatura em Computação).

**Fluxo principal**

1.  No menu lateral, o Orientador ou Professor da Disciplina acessa a
    > tela de agendamento de defesa (pelo Painel de orientandos ou pela
    > lista de defesas da turma).

2.  O sistema exibe o formulário de agendamento com a listagem dos TCCs
    > elegíveis (Status do TCC Apto para Defesa, sem sessão ativa e sob
    > a responsabilidade do usuário).

3.  O Orientador ou Professor da Disciplina seleciona o TCC a ser
    > defendido no campo correspondente (cada opção exibe o título do
    > trabalho e o nome do aluno).

4.  O Orientador ou Professor da Disciplina seleciona a Data da defesa
    > no calendário (formato DD/MM/AAAA, não anterior à data atual).

5.  O Orientador ou Professor da Disciplina informa o Horário de Início
    > da sessão (formato HH:MM, padrão 24 horas). O sistema indica a
    > reserva automática de 1 hora para a sessão.

6.  O Orientador ou Professor da Disciplina seleciona o Formato da
    > Sessão na lista suspensa (Presencial ou Remota).

7.  O sistema ajusta automaticamente os campos de localização conforme o
    > formato selecionado.

8.  O Orientador ou Professor da Disciplina informa o Local em texto
    > livre (até 100 caracteres, ex.: sala ou laboratório como A_12 ou
    > Laboratório LSI, se Presencial) ou insere a URL da videochamada
    > (iniciada por https:// e com até 500 caracteres, se Remota).

9.  O Orientador ou Professor da Disciplina clica no botão para
    > prosseguir com o agendamento.

10. O sistema valida os campos informados (E2 a E6) e avança para a
    > composição da banca (US-23) e checagem de conflitos de horário
    > (US-22). O fluxo termina.

**Fluxos alternativos**

1.  Trabalho não elegível ou com sessão de defesa ativa (passo 2): Se o
    > TCC não possuir Status do TCC "Apto para Defesa" ou já possuir
    > sessão Agendada, Reagendada ou Em Andamento, o sistema não o exibe
    > na lista de opções para seleção.

2.  Alternância do formato da sessão (passo 7): Se o Orientador ou
    > Professor da Disciplina alternar o formato de Presencial para
    > Remota (ou vice-versa) durante o preenchimento, o sistema limpa os
    > dados do campo anterior e exibe o campo correspondente à nova
    > escolha.

3.  Apresentação do aviso de duração da etapa (passo 9): No formulário,
    > o sistema exibe nota informativa de que a apresentação oral dispõe
    > de 15 minutos em TCC 1 e 20 minutos em TCC 2, seguida da arguição
    > da banca.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): Caso o Orientador ou Professor
> da Disciplina tente acessar a tela de agendamento sem sessão ativa
> (pelo menu, endereço direto ou link), o sistema exibe a tela de login
> (US-11). Após a autenticação, direciona para o agendamento e o fluxo
> prossegue a partir do passo 2.
>
> E2. Campo obrigatório em branco (passo 9): TCC, Data, Horário de
> Início, Formato da Sessão, Local (se Presencial) ou Link da
> Videochamada (se Remota) não preenchido. O sistema não avança, destaca
> o campo e exibe "Campo obrigatório". Retorna ao formulário para
> preenchimento.
>
> E3. Data ou horário retroativo (passo 9): Data anterior à data de hoje
> ou horário já ultrapassado no mesmo dia. O sistema rejeita o avanço e
> exibe: "A data e o horário devem ser posteriores ao momento atual".
> Retorna ao passo 4.
>
> E4. Local acima do limite de caracteres (passo 9): Campo Local
> informado com mais de 100 caracteres. O sistema não avança, destaca o
> campo e informa o limite de até 100 caracteres. Retorna ao passo 8.
>
> E5. URL de videochamada inválida (passo 9): Endereço remoto sem
> iniciar por https:// ou com mais de 500 caracteres. O sistema não
> avança, destaca o campo e exibe: "O link deve começar com https:// e
> ter até 500 caracteres". Retorna ao passo 8.
>
> E6. Acesso por perfil não autorizado no curso (passo 1): Se um
> Professor da Disciplina tentar agendar TCC de Engenharia de
> Computação, ou um Orientador tentar agendar TCC de Sistemas de
> Informação ou Licenciatura em Computação, o sistema bloqueia o acesso
> à funcionalidade informando a restrição institucional por curso
> (RBN-DEF-01.3). O fluxo termina.

**Pós-condições**

- Os dados básicos da sessão (TCC, data, horário, formato e local/link)
  > foram preenchidos e validados.

- A janela de 1 hora de reserva para a sessão foi calculada pelo
  > sistema.

- O agendamento é encaminhado para a composição da banca examinadora
  > (US-23) e para a validação de conflitos de agenda dos membros
  > (US-22).

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                                | **Resumo da regra em uma frase**                                                                                                                                         |
|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **DEF-01.1** | O sistema deve mostrar um formulário de agendamento da defesa que deve conter os campos TCC, Data, Horário de Início, Formato da Sessão, Local e Link da Videochamada. | Formulário com TCC (só Apto para Defesa), Data, Horário de Início, Formato, Local em texto livre (Presencial) e Link da Videochamada (Remota).                           |
| **DEF-01.3** | O sistema deve restringir quem pode agendar a sessão de defesa, conforme o curso do trabalho, e somente para TCCs com Status Apto para Defesa.                         | Restringe a ação de agendar ao Orientador (no curso de Engenharia de Computação) ou ao Professor da Disciplina (em Sistemas de Informação e Licenciatura em Computação). |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Permitido apenas para TCCs com status "Apto para Defesa".
>
> 2\. Presencial exige Local (texto livre); Remoto exige Link de
> Videochamada.

***Cenário 1: Agendamento presencial com sucesso***

> **Dado que** o Orientador (em Engenharia de Computação) ou o Professor
> da Disciplina (em Sistemas de Informação ou Licenciatura) está
> autenticado no sistema,
>
> **E** o TCC selecionado está com status "Apto para Defesa",
>
> **Quando** seleciona o formato "Presencial", preenche uma data e
> horário válidos e informa o Local da sessão em texto livre,
>
> **E** clica em prosseguir,
>
> **Então** o sistema aceita os dados da sessão e encaminha para a tela
> de composição de banca.

***Cenário 2: Agendamento remoto com sucesso***

> **Dado que** o Orientador ou Professor da Disciplina acessou o
> formulário de agendamento de um TCC apto,
>
> **Quando** seleciona o formato "Remota", preenche uma data e horário
> válidos e informa uma URL válida,
>
> **E** clica em prosseguir,
>
> **Então** o sistema valida as informações e permite avançar para a
> próxima etapa.

***Cenário 3: Tentativa de agendamento de TCC não apto***

> **Dado que** um trabalho de TCC está em elaboração com Status "Em
> Andamento",
>
> **Quando** o Orientador ou Professor da Disciplina abre a lista de
> seleção de TCC no formulário de agendamento,
>
> **Então** o referido trabalho não é exibido entre as opções
> disponíveis para agendamento.

***Cenário 4: Tentativa de agendamento presencial sem informar o
Local***

> **Dado que** o Orientador ou Professor da Disciplina escolheu o
> formato "Presencial",
>
> **Quando** deixa o campo Local em branco e tenta prosseguir,
>
> **Então** o sistema bloqueia o avanço, mantém os demais dados
> preenchidos e exibe a mensagem de que o Local é obrigatório para
> sessões presenciais.

***Cenário 5: Tentativa de agendamento remoto com link inválido***

> **Dado que** o Orientador ou Professor da Disciplina escolheu o
> formato 'Remota',
>
> **Quando** informa um link sem o protocolo https:// ou deixa o campo
> vazio e tenta prosseguir,
>
> **Então** o sistema não aceita a submissão e indica o erro de
> preenchimento no campo Link da Videochamada.

***Cenário 6: Data ou horário no passado***

> **Dado que** o Orientador ou Professor da Disciplina está preenchendo
> o formulário de agendamento,
>
> **Quando** seleciona uma data anterior ao dia de hoje ou um horário
> anterior ao momento do agendamento,
>
> **Então** o sistema bloqueia o envio e sinaliza que a defesa deve ser
> marcada para data e horário futuros.

***Cenário 7: Bloqueio de agendamento por perfil não autorizado conforme
o curso***

> **Dado que** o TCC pertence a uma turma do curso de Sistemas de
> Informação ou Licenciatura em Computação,
>
> **Quando** um Docente que atua apenas como Orientador tenta agendar a
> defesa deste trabalho,
>
> **Então** o sistema não disponibiliza a opção de agendamento para ele,
> restringindo essa ação ao Professor da Disciplina daquela turma.

***Cenário 8: Campo Local acima do limite de caracteres***

> **Dado que** o Orientador ou Professor da Disciplina escolheu o
> formato "Presencial",
>
> **Quando** digita um texto com 114 caracteres no campo Local e tenta
> prosseguir,
>
> **Então** o sistema bloqueia o avanço, destaca o campo e indica o
> limite máximo de 100 caracteres.

***Cenário 9: Acesso sem estar autenticado***

> **Dado que** o Orientador ou Professor da Disciplina não possui uma
> sessão ativa no sistema,
>
> **Quando** tenta acessar a URL direta da funcionalidade de agendamento
> de defesa,
>
> **Então** o sistema redireciona o Orientador ou Professor da
> Disciplina para a tela de login (US-11) e, após o login bem-sucedido,
> abre o formulário de agendamento.

**Tela no protótipo**

**Tela:** Agendar sessão de defesa



**Diagrama de sequência**

**Diagrama relacionado:** \[nome do diagrama ou "sem diagrama próprio" e
o motivo\]

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[X\] Descrição no formato Como, Quero, Para que
>
> \[X\] Requisitos da matriz conferidos
>
> \[X\] Fluxo principal e fluxos alternativos escritos
>
> \[X\] Atores, pré-condições e pós-condições preenchidos
>
> \[X\] Fluxos de exceção escritos
>
> \[X\] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-22 Impedir agendamentos conflitantes

| **Épico:**                | Gestão da Defesa    |
|---------------------------|---------------------|
| **Feature:**              | Agendamento e Banca |
| **Requisitos da matriz:** | RBN-DEF-03.1        |
| **Prioridade (MoSCoW):**  | Must Have           |
| **Responsável:**          | Célio Benjamim      |

**Descrição**

Como Orientador ou Professor da Disciplina, quero que o sistema impeça
agendamentos com conflito de horário da banca examinadora, para que as
defesas ocorram sem choque de agendas entre os docentes.

**Atores**

> **Ator principal:** Orientador (no curso de Engenharia de Computação)
> ou Professor da Disciplina (nos cursos de Sistemas de Informação e
> Licenciatura em Computação), responsável por submeter os dados da
> defesa.
>
> **Atores secundários:** Membros da Banca Examinadora (Orientador, 1º
> Avaliador, 2º Avaliador e Suplente, cujas agendas são validadas pelo
> sistema) e Aluno do TCC.

**Pré-condições**

- O Orientador ou Professor da Disciplina preencheu os dados da sessão
  > na tela de agendamento (US-21) e indicou os membros da banca
  > examinadora (US-23).

- A data informada é válida e a combinação de data e horário de início é
  > estritamente posterior ao momento do agendamento (US-21).

- O Orientador ou Professor da Disciplina acionou o comando para
  > salvar/confirmar o agendamento da defesa.

**Fluxo principal**

1.  O Orientador ou Professor da Disciplina submete a proposta de
    > agendamento contendo data, horário, formato, local/link e banca
    > preenchidos (US-21 e US-23).

2.  O sistema calcula a janela de tempo da defesa considerando o horário
    > de início informado e a reserva automática de 1 hora de duração
    > (RBN-DEF-01.1).

3.  O sistema pesquisa na base de dados as defesas registradas com
    > status "Agendada", "Reagendada" ou "Em Andamento" na mesma data
    > (RBN-DEF-01.2).

4.  O sistema verifica se algum membro da banca (Orientador, 1º
    > Avaliador, 2º Avaliador ou Suplente) possui sobreposição no
    > intervalo de 1 hora com as sessões ativas localizadas (E1 a E3).

5.  O sistema confirma a total disponibilidade de todos os integrantes
    > da banca examinadora.

6.  O sistema autoriza a persistência do agendamento e encaminha a
    > execução para a confirmação da sessão e disparo de notificações
    > (fluxo da US-24). O fluxo termina.

**Fluxos alternativos**

1.  Sessão composta sem indicação de suplente (passo 4): Se o Orientador
    > ou Professor da Disciplina não preencheu o campo opcional de
    > Suplente na US-23, o sistema executa a checagem de sobreposição de
    > horário exclusivamente para os 3 membros titulares (Orientador, 1º
    > Avaliador e 2º Avaliador). O fluxo prossegue a partir do passo 5.

2.  Local presencial coincidente com outra defesa (DEF-03.1; passo 4):
    > Se o Local em texto livre informado coincidir com o local digitado
    > em outra defesa no mesmo horário (ex.: "Laboratório LSI"), o
    > sistema não realiza validação sobre a sala física por se tratar de
    > campo de texto livre. A checagem restringe-se exclusivamente aos
    > docentes da banca. O fluxo prossegue a partir do passo 5.

3.  Sessão no formato Remota (passo 4): Se o formato selecionado for
    > "Remota" com URL de videochamada, o sistema aplica exatamente a
    > mesma rotina de validação temporal sobre os membros da banca
    > examinadora. O fluxo prossegue a partir do passo 5.

4.  Revalidação em reagendamento de defesa (US-24; passo 1): Quando o
    > Orientador ou Professor da Disciplina aciona a ação de "Reagendar"
    > de uma sessão já existente, o sistema pesquisa eventuais conflitos
    > para a nova data e horário, desconsiderando da checagem a própria
    > sessão que está sendo reagendada. O fluxo prossegue a partir do
    > passo 2.

**Fluxos de exceção**

> E1. Conflito de agenda de membro titular da banca (passo 4): Se o
> Orientador, o 1º Avaliador ou o 2º Avaliador possuir outra sessão
> Agendada, Reagendada ou Em Andamento com sobreposição no intervalo de
> 1 hora, o sistema rejeita o salvamento, não grava nenhum dado no banco
> e exibe mensagem identificando o docente indisponível (ex.: "O docente
> selecionado já possui uma defesa agendada neste horário"). Retorna ao
> formulário para troca do membro ou ajuste de horário.
>
> E2. Conflito de agenda de membro suplente (passo 4): Se o docente
> selecionado como Suplente possuir choque de horário com outra sessão
> ativa no mesmo intervalo, o sistema bloqueia a submissão, não salva a
> sessão e alerta sobre a indisponibilidade do suplente. Retorna ao
> formulário para indicação de outro suplente ou alteração de horário.
>
> E3. Múltiplos conflitos de horário simultaneamente (passo 4): Se dois
> ou mais membros da banca examinadora apresentarem choques simultâneos
> de horário, o sistema rejeita a operação e consolida em uma única
> mensagem de alerta todos os membros em conflito. Retorna ao formulário
> para correção.
>
> E4. Conflito com sessão em andamento (passo 4): Se um dos membros
> estiver vinculado a uma defesa que atingiu seu horário e encontra-se
> com o status "Em Andamento", o sistema computa a janela de 1 hora a
> partir do início da referida sessão e bloqueia a nova sobreposição.
> Retorna ao formulário para alteração de horário.

**Pós-condições**

- A inexistência de sobreposição de horários para todos os membros da
  > banca examinadora foi validada matematicamente.

- O sistema liberou a transição para a US-24, permitindo salvar o
  > registro com status "Agendada" e disparar os e-mails e notificações.

- Em qualquer caso de conflito, nenhum registro de defesa ou vínculo de
  > banca é persistido no banco de dados.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                     | **Resumo da regra em uma frase**                                                                                                   |
|--------------|---------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| **DEF-03.1** | O sistema deve validar a tentativa de agendamento da sessão de defesa antes de confirmá-la. | Valida o agendamento e rejeita sobreposição no intervalo de 1 hora com qualquer membro da banca; o Local não entra na verificação. |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Validação "Hard Fail" no salvamento.
>
> 2\. Bloqueia se qualquer Membro da Banca estiver ocupado no intervalo
> reservado de 1 hora.

***Cenário 1: Agendamento sem nenhum conflito de agenda***

> **Dado que** todos os membros da banca (Orientador, 1º Avaliador, 2º
> Avaliador e Suplente) estão livres no intervalo de 1 hora pretendido,
>
> **Quando** o Orientador ou Professor da Disciplina confirma o envio do
> agendamento da defesa,
>
> **Então** o sistema valida a ausência de conflitos e prossegue com a
> persistência dos dados da sessão.

***Cenário 2: Mesmo Local em horários sobrepostos***

> **Dado que** o Local "A_12" já foi informado em outra defesa das 14:00
> às 15:00, com outra banca,
>
> **Quando** o Orientador ou Professor da Disciplina agenda uma defesa
> presencial com o Local "A_12", com início às 14:30 do mesmo dia, sem
> conflito na agenda dos membros da banca,
>
> **Então** o sistema não verifica o campo Local e prossegue com o
> agendamento com sucesso.

***Cenário 3: Choque de horário com membro titular da banca***

> **Dado que** um docente indicado como 1º Avaliador já está
> participando de uma banca agendada das 10:00 às 11:00,
>
> **Quando** o Orientador ou Professor da Disciplina tenta agendar outra
> defesa incluindo esse docente, entre 10:00 e 11:00 do mesmo dia,
>
> **Então** o sistema bloqueia o salvamento no banco de dados, informa o
> nome do avaliador com conflito de agenda e não registra a sessão.

***Cenário 4: Choque de horário com o Orientador***

> **Dado que** o Orientador do trabalho já preside outra defesa marcada
> para o dia 20/10/2026 das 14:00 às 15:00,
>
> **Quando** tenta agendar uma nova defesa para outro orientando no
> mesmo dia 20/10/2026 com início às 14:30,
>
> **Então** o sistema rejeita a operação, informa que o próprio
> orientador já possui uma defesa agendada nesse intervalo e não grava o
> agendamento.

***Cenário 5: Choque de horário com o 2º Avaliador titular***

> **Dado que** a docente indicada como 2ª Avaliadora integra uma banca
> agendada das 16:00 às 17:00,
>
> **Quando** o Orientador ou Professor da Disciplina tenta agendar uma
> defesa das 16:15 às 17:15 do mesmo dia com essa docente na banca
> titular,
>
> **Então** o sistema bloqueia a gravação, destaca o nome da 2ª
> Avaliadora como indisponível e mantém os dados do formulário
> preenchidos para ajuste.

***Cenário 6: Choque de horário com membro suplente***

> **Dado que** o docente indicado como Suplente já possui outra defesa
> com status "Agendada" no mesmo intervalo de 1 hora,
>
> **Quando** o Orientador ou Professor da Disciplina tenta concluir o
> agendamento,
>
> **Então** o sistema rejeita a solicitação, aponta a indisponibilidade
> do suplente e exige a correção antes de salvar.

***Cenário 7: Múltiplos membros da banca com choque simultâneo de
horários***

> **Dado que** o 1º Avaliador e o 2º Avaliador selecionados possuem
> outras defesas ativas coincidentes com o horário pretendido,
>
> **Quando** o Orientador ou Professor da Disciplina aciona o botão para
> salvar o agendamento,
>
> **Então** o sistema rejeita a gravação e apresenta uma mensagem
> consolidada informando a indisponibilidade de ambos os avaliadores.

***Cenário 8: Choque com sessão que transitou para o status "Em
Andamento"***

> **Dado que** uma defesa anterior envolvendo o 1º Avaliador atingiu o
> horário previsto e seu status atualizou para "Em Andamento",
>
> **Quando** o Orientador ou Professor da Disciplina submete um novo
> agendamento com esse mesmo docente cujo intervalo de 1 hora colida com
> a sessão em curso,
>
> **Então** o sistema identifica a sobreposição com a sessão em
> andamento e impede o agendamento.

***Cenário 9: Choque com sessão com status "Reagendada"***

> **Dado que** uma banca envolvendo o docente indicado possui status
> "Reagendada" para as 15:30 às 16:30,
>
> **Quando** o Orientador ou Professor da Disciplina tenta agendar uma
> defesa com esse docente com início às 16:00,
>
> **Então** o sistema reconhece a sobreposição de horários e rejeita a
> criação da nova sessão.

***Cenário 10: Sessões consecutivas no mesmo dia sem sobreposição***

> **Dado que** um avaliador participa de uma defesa agendada das 14:00
> às 15:00,
>
> **Quando** o Orientador ou Professor da Disciplina agenda uma nova
> defesa com esse mesmo avaliador iniciando exatamente às 15:00 do mesmo
> dia,
>
> **Então** o sistema valida que não há sobreposição no intervalo e
> confirma o agendamento com sucesso.

***Cenário 11: Agendamento de sessão remota com banca disponível***

> **Dado que** a sessão é no formato "Remota" e todos os membros da
> banca possuem horário vago na data e hora selecionadas,
>
> **Quando** o Orientador ou Professor da Disciplina envia o
> agendamento,
>
> **Então** o sistema valida a disponibilidade dos integrantes
> considerando apenas os membros e avança para a confirmação.

***Cenário 12: Validação durante reagendamento de sessão***

> **Dado que** o Orientador ou Professor da Disciplina está reagendando
> uma defesa existente das 14:00 para as 16:00,
>
> **Quando** submete o reagendamento e nenhum membro possui choque de
> horário às 16:00,
>
> **Então** o sistema valida a ausência de conflitos e atualiza os dados
> da sessão.

**Tela no protótipo**

**Tela:** Agendar sessão de defesa



**Diagrama de sequência**

**Diagrama relacionado:** \[nome do diagrama ou "sem diagrama próprio" e
o motivo\]

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[X\] Descrição no formato Como, Quero, Para que
>
> \[X\] Requisitos da matriz conferidos
>
> \[X\] Fluxo principal e fluxos alternativos escritos
>
> \[X\] Atores, pré-condições e pós-condições preenchidos
>
> \[X\] Fluxos de exceção escritos
>
> \[X\] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-23 Compor a banca

| **Épico:**                | Gestão da Defesa                                       |
|---------------------------|--------------------------------------------------------|
| **Feature:**              | Agendamento e Banca                                    |
| **Requisitos da matriz:** | RBN-DEF-02.1, RBN-DEF-02.2, RBN-DEF-02.3, RBN-DEF-02.4 |
| **Prioridade (MoSCoW):**  | Must Have                                              |
| **Responsável:**          | Célio Benjamim                                         |

**Descrição**

Como Orientador ou Professor da Disciplina, quero compor a banca
examinadora com avaliadores titulares e suplente, para que a sessão de
defesa possua quórum formal para avaliação acadêmica.

**Atores**

> **Ator principal:** Orientador (no curso de Engenharia de Computação)
> ou Professor da Disciplina (nos cursos de Sistemas de Informação e
> Licenciatura em Computação). No acionamento de suplente durante a
> sessão (DEF-02.2), o Orientador é o ator principal exclusivo.
>
> **Atores secundários:** Membros da Banca Examinadora (1º Avaliador, 2º
> Avaliador e Suplente), Aluno do TCC e Docente cadastrado como Membro
> Externo.

**Pré-condições**

- O Orientador ou Professor da Disciplina está autenticado no sistema,
  > com o Status da Conta Ativa (US-11). Sem sessão ativa, aplica-se o
  > E1.

- Os dados básicos da sessão de defesa (TCC, data, horário, formato e
  > local/link) foram preenchidos no formulário de agendamento (US-21).

- O TCC selecionado possui Orientador previamente vinculado, que
  > presidirá a banca.

- Existem docentes do NUCOMP com Status da Conta Ativa e/ou Membros
  > Externos cadastrados na base de dados para seleção.

**Fluxo principal**

1.  No formulário de agendamento da defesa (US-21), o Orientador ou
    > Professor da Disciplina acessa a seção "Banca examinadora".

2.  O sistema vincula automaticamente a banca ao TCC da sessão e exibe o
    > campo "Orientador (Presidente)" preenchido em modo somente leitura
    > com o orientador do trabalho, sem opção de alteração ou remoção.

3.  O Orientador ou Professor da Disciplina abre a lista suspensa do
    > campo "1º Avaliador" e seleciona um docente com Status da Conta
    > Ativa ou um Membro Externo.

4.  O sistema atualiza dinamicamente as opções da lista do 2º Avaliador,
    > removendo a pessoa já escolhida como 1º Avaliador.

5.  O Orientador ou Professor da Disciplina seleciona o 2º Avaliador na
    > lista suspensa.

6.  O sistema atualiza dinamicamente a lista de opções do campo
    > Suplente, removendo os dois avaliadores titulares já selecionados.

7.  Opcionalmente, o Orientador ou Professor da Disciplina seleciona um
    > avaliador no campo "Suplente" (ou mantém a opção "Sem suplente").

8.  O Orientador ou Professor da Disciplina clica no botão "Agendar".

9.  O sistema valida o preenchimento obrigatório dos avaliadores
    > titulares e a unicidade dos integrantes da banca (E2 a E4).

10. O sistema envia a composição da banca para a verificação de
    > conflitos de horário dos membros (US-22). O fluxo termina.

**Fluxos alternativos**

1.  Composição sem indicação de suplente (passo 7): O Orientador ou
    > Professor da Disciplina opta por não indicar suplente e mantém o
    > campo como "Sem suplente". O sistema aceita a composição formada
    > apenas pelos 3 membros titulares (Presidente, 1º Avaliador e 2º
    > Avaliador). O fluxo prossegue a partir do passo 8.

2.  Cadastro rápido de Membro Externo ausente da lista (DEF-02.3; passos
    > 3 ou 5): Se o avaliador externo desejado não constar na lista
    > suspensa, o Orientador ou Professor da Disciplina aciona o link "O
    > Membro Externo não está na lista? Cadastrar". O sistema abre a
    > janela modal de cadastro rápido com Nome Completo, E-mail,
    > Titulação e Instituição de Origem. O Orientador ou Professor da
    > Disciplina preenche os dados e clica em "Salvar" (US-05). O
    > sistema valida as informações, grava o Membro Externo com Status
    > da Conta Aguardando Ativação e já o seleciona automaticamente no
    > campo da banca que estava sendo preenchido. O fluxo prossegue a
    > partir do passo 4 ou do passo 6.

3.  Alteração da banca antes da sessão (DEF-02.4; passo 1): Com a sessão
    > Agendada ou Reagendada, o Orientador (em Engenharia de Computação)
    > ou o Professor da Disciplina (em Sistemas de Informação ou
    > Licenciatura) acessa os detalhes da sessão, clica no botão
    > "Alterar banca", troca o 1º Avaliador, o 2º Avaliador ou o
    > Suplente, informa a Justificativa obrigatória (até 500 caracteres)
    > e confirma. O sistema revalida conflitos de horário do novo membro
    > (US-22), descarta eventuais avaliações salvas pelo membro
    > substituído, grava a alteração e notifica os membros incluídos, os
    > membros removidos e o Aluno. O fluxo termina.

4.  Acionamento do suplente durante a sessão (DEF-02.2; passo 1):
    > Durante a realização da defesa (status "Em Andamento"), constatada
    > a ausência de um titular, o Orientador clica no botão "Acionar
    > suplente", seleciona o Avaliador Substituído (1º ou 2º Avaliador),
    > digita a Justificativa obrigatória (até 500 caracteres) e
    > confirma. O sistema promove o Suplente a titular no lugar do
    > ausente, descarta notas prévias eventualmente salvas pelo ausente
    > e libera o formulário completo de avaliação escrita e oral para o
    > suplente. O fluxo termina.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): Caso o Orientador ou Professor
> da Disciplina tente acessar o agendamento de defesa sem sessão ativa,
> o sistema apresenta a tela de login (US-11). Após a autenticação,
> exibe a tela de agendamento e o fluxo prossegue a partir do passo 1.
> Em caso de falha na autenticação, aplicam-se as exceções da US-11.
>
> E2. Avaliador titular não selecionado (passo 9): O Orientador ou
> Professor da Disciplina tenta agendar sem escolher o 1º Avaliador ou o
> 2º Avaliador. O sistema não avança, destaca o campo pendente e exibe
> "Campo obrigatório". Retorna ao passo 3 ou passo 5.
>
> E3. Membro titular duplicado ou coorientador indicado (passo 9): Se
> houver tentativa de selecionar o mesmo docente em mais de um papel ou
> indicar orientador/coorientador do trabalho, o sistema bloqueia a
> submissão e exibe "Selecione avaliadores distintos que não façam parte
> da orientação do trabalho". Retorna ao passo 3.
>
> E4. Conflito de horário de membro da banca (passo 10): O sistema
> identifica que algum avaliador titular ou o suplente possui outra
> defesa ativa no intervalo reservado de 1 hora (US-22). O sistema
> bloqueia a gravação (Hard Fail) e exibe o alerta informando o membro
> com indisponibilidade. Retorna ao formulário para troca do membro ou
> alteração do horário da sessão.
>
> E5. Alteração de banca sem justificativa (fluxo alternativo C): O
> Orientador ou Professor da Disciplina confirma a alteração da banca
> deixando o campo Justificativa em branco ou com mais de 500
> caracteres. O sistema não salva, destaca o campo e exibe "Informe uma
> justificativa de até 500 caracteres". Retorna ao formulário de
> alteração de banca.
>
> E6. Ausência do Orientador antes da sessão (fluxo alternativo C): Caso
> o Orientador informe que não poderá comparecer à defesa, a banca não
> pode ter seu Presidente substituído por alteração simples de membros;
> a sessão deve ser reagendada (US-24). O sistema não altera a banca e
> exibe "A ausência do Orientador exige o reagendamento da sessão". O
> fluxo termina.
>
> E7. Ausência de membro titular em sessão sem suplente (fluxo
> alternativo D): Se um avaliador titular faltar durante a sessão e não
> houver suplente indicado previamente na composição, o botão "Acionar
> suplente" não aparece no painel; o Orientador deve acionar o
> reagendamento da sessão com justificativa (US-24). O fluxo termina.
>
> E8. Acionamento de suplente sem justificativa (fluxo alternativo D): O
> Orientador seleciona o avaliador substituído mas confirma o modal de
> acionamento com o campo Justificativa vazio ou com mais de 500
> caracteres. O sistema não efetiva a substituição e destaca o campo
> obrigatório. Retorna ao formulário de acionamento de suplente.

**Pós-condições**

- A banca examinadora foi formalmente vinculada ao TCC, composta pelo
  > Orientador (Presidente) e por dois avaliadores titulares (e
  > opcionalmente um suplente).

- Nenhum orientador ou coorientador foi alocado como avaliador titular
  > ou suplente.

- Após a validação de conflitos (US-22), a banca fica apta para a
  > confirmação do agendamento e disparo das notificações (US-24).

- No caso de acionamento de suplente durante a sessão, o suplente assume
  > o papel de titular, as notas do substituído são descartadas e o novo
  > membro passa a acessar as fichas de avaliação.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                                                            | **Resumo da regra em uma frase**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|--------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **DEF-02.1** | O sistema deve mostrar um formulário de composição da banca, vinculado automaticamente ao TCC da sessão, que deve conter os campos Orientador (Presidente), 1º Avaliador, 2º Avaliador e Suplente. | Associa a banca examinadora diretamente ao TCC selecionado no agendamento em modo somente leitura. Define de forma automática e não editável o Orientador do TCC como primeiro membro e Presidente da banca avaliadora. Apresenta lista suspensa obrigatória contendo docentes ativos e membros externos, excluindo o orientador e coorientadores do trabalho. Apresenta lista suspensa obrigatória com os mesmos avaliadores elegíveis, filtrando e impedindo a seleção do docente já escolhido como 1º Avaliador. Apresenta campo opcional em lista suspensa para indicação de um suplente entre os membros elegíveis não selecionados como titulares. |
| **DEF-02.2** | \[Exceção\] O sistema deve permitir o acionamento do suplente, com o formulário que deve conter os campos Avaliador Substituído e Justificativa.                                                   | Disponibiliza botão exclusivo ao Orientador durante a sessão em andamento para substituir um titular ausente pelo suplente, descartando avaliações prévias do ausente e liberando o formulário completo ao suplente. Apresenta seleção única entre o 1º e o 2º Avaliador no formulário de acionamento de suplente. Exige preenchimento obrigatório de justificativa textual com até 500 caracteres para efetivar a substituição pelo suplente.                                                                                                                                                                                                           |
| **DEF-02.3** | \[Exceção\] O sistema deve permitir o cadastro de Membro Externo ausente da lista.                                                                                                                 | Permite que o usuário acione o atalho de cadastro rápido de membro externo caso o avaliador desejado não conste na listagem.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **DEF-02.4** | \[Exceção\] O sistema deve permitir a alteração da banca antes da sessão.                                                                                                                          | Permite alterar avaliadores titulares ou suplente antes do início da sessão com justificativa obrigatória de até 500 caracteres, revalidando conflitos de agenda e descartando eventuais avaliações salvas pelo substituído.                                                                                                                                                                                                                                                                                                                                                                                                                             |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Orientador é o Presidente fixo (sem edição).
>
> 2\. Coorientadores são filtrados e não aparecem na lista de escolha.
>
> 3\. Permite acionar suplente justificado em caso de ausência.

***Cenário 1: Composição padrão da banca com sucesso***

> **Dado que** o Orientador ou Professor da Disciplina está no
> formulário de agendamento de um TCC apto,
>
> **Quando** visualiza o Orientador fixo como Presidente, seleciona a
> docente Camila Freitas Duarte como 1ª Avaliadora, o docente Tiago
> Barros Sena como 2º Avaliador e define um suplente opcional,
>
> **E** clica em "Agendar",
>
> **Então** o sistema vincula os membros ao TCC e submete a composição
> para a validação de disponibilidade de horários (US-22).

***Cenário 2: Composição da banca sem indicação de suplente***

> **Dado que** o Orientador ou Professor da Disciplina preencheu a 1ª
> Avaliadora e o 2º Avaliador,
>
> **Quando** mantém o campo Suplente com a opção "Sem suplente"
> selecionada e clica em "Agendar",
>
> **Então** o sistema aceita a banca composta por 3 membros titulares e
> avança para a validação de conflitos sem exigir suplente.

***Cenário 3: Bloqueio de coorientadores e membros da orientação***

> **Dado que** o TCC possui o docente Eduardo Lins Carvalho registrado
> como coorientador aceito,
>
> **Quando** o Orientador ou Professor da Disciplina abre as listas
> suspensas de 1º Avaliador, 2º Avaliador ou Suplente,
>
> **Então** o sistema não exibe o Orientador do TCC nem o coorientador
> Eduardo Lins Carvalho entre as opções de escolha.

***Cenário 4: Exclusão mútua entre avaliadores titulares e suplente***

> **Dado que** a docente "Camila Freitas Duarte" foi selecionada no
> campo 1º Avaliador,
>
> **Quando** o Orientador ou Professor da Disciplina abre as opções dos
> campos 2º Avaliador ou Suplente,
>
> **Então** o sistema oculta "Camila Freitas Duarte" dessas listas,
> impedindo a indicação da mesma pessoa em mais de uma posição.

***Cenário 5: Tentativa de agendar sem selecionar avaliador titular***

> **Dado que** o Orientador ou Professor da Disciplina está no
> formulário de banca,
>
> **Quando** deixa o campo 1º Avaliador ou 2º Avaliador sem
> preenchimento e clica em "Agendar",
>
> **Então** o sistema não salva o agendamento, destaca o campo em aberto
> e exibe a mensagem "Campo obrigatório".

***Cenário 6: Acionamento justificado de suplente durante a sessão***

> **Dado que** a defesa está com status "Em Andamento", possui suplente
> cadastrado e o 2º Avaliador titular não compareceu,
>
> **Quando** o Orientador clica em "Acionar suplente", seleciona o 2º
> Avaliador como substituído, informa a justificativa com 250 caracteres
> e confirma,
>
> **Então** o sistema promove o suplente a membro titular, descarta
> eventuais notas preliminares do titular substituído e libera as fichas
> de avaliação para o novo titular.

***Cenário 7: Tentativa de acionar suplente sem justificativa***

> **Dado que** o Orientador abriu a janela de acionamento do suplente
> durante a sessão,
>
> **Quando** seleciona o avaliador a ser substituído mas deixa o campo
> Justificativa em branco e clica em confirmar,
>
> **Então** o sistema bloqueia a substituição e alerta que o
> preenchimento da justificativa é obrigatório.

***Cenário 8: Ausência de avaliador em sessão sem suplente cadastrado***

> **Dado que** uma defesa está "Em Andamento" mas foi agendada sem
> suplente,
>
> **Quando** um avaliador titular falta à sessão e o Orientador verifica
> as ações disponíveis,
>
> **Então** o sistema não disponibiliza o botão "Acionar suplente" e
> orienta que a defesa deve ser reagendada com justificativa.

***Cenário 9: Alteração da composição da banca antes da defesa***

> **Dado que** a defesa está com status "Agendada" e um avaliador
> titular informou previamente que terá compromisso acadêmico,
>
> **Quando** o Orientador ou Professor da Disciplina clica em "Alterar
> banca", seleciona o novo avaliador, digita a justificativa da troca e
> salva,
>
> **Então** o sistema valida que o novo membro não tem conflito de
> horário, atualiza a banca examinadora, descarta avaliações prévias do
> membro removido e dispara notificação a todos os envolvidos.

***Cenário 10: Alteração de banca rejeitada por conflito de horário do
novo membro***

> **Dado que** o Orientador ou Professor da Disciplina abriu a tela de
> alteração de banca,
>
> **Quando** seleciona um docente substituto que já possui outra banca
> agendada no mesmo horário, insere a justificativa e salva,
>
> **Então** o sistema rejeita a alteração (Hard Fail), não substitui o
> membro e exibe o alerta de conflito de agenda do docente indicado.

***Cenário 11: Tentativa de alteração de banca sem justificativa***

> **Dado que** o Orientador ou Professor da Disciplina está na janela de
> alteração de banca de uma defesa agendada,
>
> **Quando** troca o avaliador titular mas deixa o campo Justificativa
> em branco e clica em salvar,
>
> **Então** o sistema bloqueia o salvamento e exige a justificativa de
> até 500 caracteres.

***Cenário 12: Ausência do Orientador antes da sessão***

> **Dado que** a defesa está agendada e o Orientador comunica que não
> poderá comparecer na data marcada,
>
> **Quando** o Orientador ou Professor da Disciplina tenta alterar a
> composição da banca substituindo o Orientador,
>
> **Então** o sistema bloqueia a alteração do Presidente e indica que a
> ausência do Orientador exige o reagendamento formal da sessão.

***Cenário 13: Cadastro rápido de membro externo diretamente pelo
formulário da banca***

> **Dado que** o avaliador externo convidado não consta na lista
> suspensa de membros da banca,
>
> **Quando** o Orientador ou Professor da Disciplina clica em "O Membro
> Externo não está na lista? Cadastrar", preenche os dados cadastrais
> solicitados e salva,
>
> **Então** o sistema cadastra o membro externo e já o seleciona de
> forma automática no campo de avaliador correspondente.

***Cenário 14: Acesso sem estar autenticado***

> **Dado que** o Orientador ou Professor da Disciplina não possui sessão
> ativa no sistema,
>
> **Quando** tenta acessar diretamente a etapa de composição da banca,
>
> **Então** o sistema apresenta a tela de login (US-11) e, após a
> autenticação bem-sucedida, retorna ao formulário.

**Tela no protótipo**

**Tela:** Agendar sessão de defesa





**Diagrama de sequência**

**Diagrama relacionado:** \[nome do diagrama ou "sem diagrama próprio" e
o motivo\]

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[X\] Descrição no formato Como, Quero, Para que
>
> \[X\] Requisitos da matriz conferidos
>
> \[X\] Fluxo principal e fluxos alternativos escritos
>
> \[X\] Atores, pré-condições e pós-condições preenchidos
>
> \[X\] Fluxos de exceção escritos
>
> \[X\] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-24 Notificar a banca e atualizar o status da sessão

| **Épico:**                | Gestão da Defesa                         |
|---------------------------|------------------------------------------|
| **Feature:**              | Agendamento e Banca                      |
| **Requisitos da matriz:** | RBN-DEF-01.2, RBN-DEF-03.2, RBN-DEF-03.3 |
| **Prioridade (MoSCoW):**  | Must Have                                |
| **Responsável:**          | Célio Benjamim                           |

**Descrição**

Como Orientador ou Professor da Disciplina, quero confirmar o
agendamento da defesa para notificar a banca examinadora com o link do
Documento para Defesa e atualizar o status da sessão, garantindo a
ciência de todos os envolvidos, o cancelamento de pedidos de troca
pendentes e a integridade do ciclo acadêmico.

**Atores**

> **Ator principal:** Orientador (no curso de Engenharia de Computação)
> ou Professor da Disciplina (nos cursos de Sistemas de Informação e
> Licenciatura em Computação), responsável por confirmar o agendamento.
> No reagendamento e cancelamento da sessão (DEF-03.3), atuam o
> Orientador, o Professor da Disciplina ou a Secretaria do curso. Na
> liberação do resultado final (gatilho para a transição para
> "Realizada"), o Orientador é o ator exclusivo.
>
> **Atores secundários:** Membros da Banca Examinadora (Orientador, 1º
> Avaliador, 2º Avaliador e Suplente), Aluno do TCC (notificados da
> sessão) e Docente com pedido de troca de orientador pendente
> (notificado do cancelamento do pedido).

**Pré-condições**

- O Orientador ou Professor da Disciplina concluiu o preenchimento dos
  > dados da sessão (US-21) e a indicação dos membros da banca
  > examinadora (US-23).

- A validação de ausência de conflitos de horário na banca examinadora
  > foi realizada com sucesso pelo sistema (US-22).

- O aluno do TCC efetuou a entrega do tipo "Documento para Defesa" com
  > URL válida cadastrada no sistema (US-15 e US-43).

- Para reagendamento ou cancelamento, a sessão deve estar registrada com
  > status Agendada, Reagendada ou Em Andamento (esta última antes da
  > liberação do resultado).

**Fluxo principal**

1.  O sistema valida com sucesso a ausência de conflitos de horário dos
    > membros da banca examinadora (US-22).

2.  O Orientador ou Professor da Disciplina confirma a gravação da
    > sessão de defesa.

3.  O sistema grava os dados da sessão na base de dados e define o
    > status da sessão automaticamente com o valor "Agendada"
    > (RBN-DEF-01.2).

4.  O sistema recupera a URL da versão escrita submetida na entrega do
    > tipo "Documento para Defesa" vinculada ao TCC (RBN-CAD-09.2).

5.  O sistema gera a mensagem de notificação formal contendo data,
    > horário, formato, local ou link da videochamada, título do
    > trabalho, nome do aluno e o link da entrega do Documento para
    > Defesa para leitura prévia da Parte Escrita.

6.  O sistema dispara a notificação por e-mail e pela central interna do
    > sistema para o aluno e para todos os membros da banca (Orientador,
    > 1º Avaliador, 2º Avaliador e Suplente).

7.  O sistema disponibiliza o acesso às fichas de avaliação da Parte
    > Escrita aos avaliadores no painel "Minhas bancas" (US-25).

8.  O sistema verifica se existe pedido de troca de orientador pendente
    > (sem resposta) para o referido TCC; existindo, cancela
    > automaticamente o pedido e envia notificação de cancelamento ao
    > aluno e ao docente indicado (US-17 e US-18).

9.  O sistema publica a sessão na lista de defesas (US-40) e na agenda
    > pública de defesas (US-30). O Orientador ou Professor da
    > Disciplina permanece na tela com a confirmação "Defesa agendada
    > com sucesso". O fluxo termina.

**Fluxos alternativos**

1.  Reagendamento da sessão (DEF-03.3; passo 3): Com a sessão Agendada,
    > Reagendada ou Em Andamento (antes da liberação do resultado), o
    > Orientador (em Engenharia), o Professor da Disciplina (em
    > SI/Licenciatura) ou a Secretaria do curso acessa os detalhes da
    > defesa, aciona o botão "Reagendar", define a nova data/horário e
    > insere a Justificativa obrigatória (até 500 caracteres). O sistema
    > revalida conflitos (US-22), mantém a banca composta e notas
    > parciais salvas, altera o status da sessão para "Reagendada",
    > atualiza a agenda e notifica os membros da banca e o aluno por
    > e-mail e no sistema com os dados retificados. O fluxo termina.

2.  Cancelamento da sessão (DEF-03.3; passo 3): Com a sessão Agendada,
    > Reagendada ou Em Andamento (antes da liberação do resultado), o
    > Orientador, Professor da Disciplina ou Secretaria aciona o botão
    > "Cancelar sessão", informa a Justificativa obrigatória (até 500
    > caracteres) e confirma. O sistema altera o status da sessão para
    > "Cancelada", descarta eventuais avaliações salvas, mantém o Status
    > do TCC como "Apto para Defesa" para permitir nova marcação
    > (US-21), atualiza a agenda de defesas e notifica a banca e o
    > aluno. O fluxo termina.

3.  Transição temporal para "Em Andamento" (DEF-01.2; passo 3): Quando o
    > relógio do sistema atinge a data e o horário previstos de uma
    > sessão com status "Agendada" ou "Reagendada", o sistema altera
    > automaticamente o status da sessão para "Em Andamento", mantendo-o
    > somente leitura e desbloqueando o formulário da Parte Oral para os
    > membros da banca (US-25). O fluxo termina.

4.  Transição para "Realizada" após conclusão da avaliação (DEF-01.2;
    > passo 3): Durante a sessão ("Em Andamento"), após a conclusão de
    > todas as avaliações, quando o Orientador registra o parecer e
    > aciona "Liberar Resultado" (US-27), o sistema altera
    > automaticamente o status da sessão para "Realizada" e dispara a
    > geração dos documentos formais (US-28). O fluxo termina.

5.  Agendamento de TCC sem pedido de troca pendente (passo 8): Se o TCC
    > não possuir solicitação de troca de orientador em aberto, o
    > sistema não dispara ações de cancelamento e prossegue diretamente
    > para a publicação e finalização do agendamento. O fluxo prossegue
    > a partir do passo 9.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 2): Caso o Orientador, Professor da
> Disciplina ou Secretaria tente confirmar agendamento, reagendamento ou
> cancelamento sem sessão ativa, o sistema apresenta a tela de login
> (US-11). Após a autenticação, direciona para a tela da ação solicitada
> e o fluxo prossegue a partir do passo 2 (ou dos fluxos alternativos A
> ou B). Em caso de falha na autenticação, aplicam-se as exceções da
> US-11.
>
> E2. Reagendamento bloqueado por conflito de horário (fluxo alternativo
> A): Ao submeter nova data e horário no reagendamento, o sistema
> detecta sobreposição no intervalo de 1 hora com a agenda de qualquer
> membro da banca (US-22). O sistema rejeita o reagendamento (Hard
> Fail), exibe o alerta identificando o docente indisponível e mantém os
> dados no formulário para correção. Retorna ao fluxo alternativo A.
>
> E3. Justificativa ausente ou com mais de 500 caracteres (fluxos
> alternativos A ou B): O Orientador, Professor da Disciplina ou
> Secretaria confirma o reagendamento ou cancelamento deixando o campo
> Justificativa em branco ou com mais de 500 caracteres. O sistema não
> salva a alteração, destaca o campo e exibe "Informe uma justificativa
> de até 500 caracteres". Retorna ao formulário de reagendamento ou
> cancelamento.
>
> E4. Ação bloqueada em sessão já concluída (fluxos alternativos A ou
> B): Caso o Orientador, Professor da Disciplina ou Secretaria tente
> reagendar ou cancelar uma sessão que já possui status "Realizada", o
> sistema não disponibiliza os botões e impede a ação. O fluxo termina.
>
> E5. Acesso não autorizado para reagendamento ou cancelamento (fluxos
> alternativos A ou B): Se um usuário que não seja o Orientador do TCC
> (em Engenharia), o Professor da Disciplina da turma (em
> SI/Licenciatura) ou a Secretaria do curso tentar acionar o
> reagendamento ou cancelamento, o sistema bloqueia o acesso e exibe
> "Você não tem permissão para esta ação". O fluxo termina.

**Pós-condições**

- A sessão de defesa foi gravada na base de dados com o status
  > "Agendada" (ou atualizada para "Reagendada" / "Cancelada").

- A notificação formal contendo data, horário, local/link e o link do
  > Documento para Defesa foi entregue por e-mail e na central interna
  > aos avaliadores e ao aluno.

- O pedido de troca de orientador que estava pendente para o trabalho
  > foi cancelado compulsoriamente no sistema.

- As fichas de avaliação da Parte Escrita foram disponibilizadas aos
  > membros da banca.

- Em caso de cancelamento, a sessão passou para "Cancelada" e o Status
  > do TCC permaneceu "Apto para Defesa" para permitir nova marcação.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                      | **Resumo da regra em uma frase**                                                                                                                                                                                                                                                                                                     |
|--------------|----------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **DEF-01.2** | O sistema deve atualizar automaticamente o status da sessão, com um dos valores: Agendada, Em Andamento, Realizada, Reagendada ou Cancelada. | Atualiza de forma automática e não editável o estado da sessão entre Agendada, Em Andamento, Realizada, Reagendada ou Cancelada, conforme o momento temporal ou evento de processo.                                                                                                                                                  |
| **DEF-03.2** | O sistema deve confirmar o agendamento da sessão de defesa e notificar a banca composta especificamente para essa sessão.                    | Grava a sessão como Agendada, notifica a banca e o Aluno com o link da entrega do tipo Documento para Defesa e cancela o pedido de troca de orientador pendente.                                                                                                                                                                     |
| **DEF-03.3** | \[Exceção\] O sistema deve permitir o reagendamento ou cancelamento da sessão, com o formulário que deve conter o campo Justificativa.       | Permite o reagendamento (mantendo a banca e revalidando conflitos) ou o cancelamento da sessão (retornando o TCC a Apto para Defesa e descartando notas) mediante justificativa formal. Exige o preenchimento obrigatório de justificativa textual com até 500 caracteres em formulário específico de reagendamento ou cancelamento. |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Envia e-mail automático com link da Parte Escrita.
>
> 2\. Atualiza o status para "Agendada", "Reagendada", "Em Andamento",
> "Realizada" ou "Cancelada"

***Cenário 1: Confirmação e notificação de agendamento***

> **Dado que** o Orientador ou Professor da Disciplina concluiu o
> formulário de agendamento e banca sem conflitos de horário,
>
> **Quando** confirma a gravação da defesa,
>
> **Então** o sistema define o status da sessão como "Agendada",
>
> **E** envia notificação no sistema e e-mail aos membros da banca e ao
> aluno contendo data, horário, local/link e a URL da entrega do tipo
> Documento para Defesa.

***Cenário 2: Cancelamento automático de pedido de troca de orientador
no agendamento***

> **Dado que** o aluno solicitou a troca para um novo orientador e o
> pedido ainda está com status Pendente (sem resposta),
>
> **Quando** o Orientador ou Professor da Disciplina agenda a sessão de
> defesa desse TCC,
>
> **Então** o sistema cancela compulsoriamente o pedido de troca
> pendente, mantém o orientador atual e notifica o aluno e o docente
> indicado sobre o cancelamento do pedido.

***Cenário 3: Agendamento de TCC sem pedido de troca pendente***

> **Dado que** o TCC apto possui orientador definitivo e nenhuma
> solicitação de troca pendente,
>
> **Quando** o Orientador ou Professor da Disciplina conclui o
> agendamento da defesa,
>
> **Então** o sistema grava a sessão como "Agendada" e não gera
> notificações de cancelamento de orientação.

***Cenário 4: Transição automática para "Em Andamento" na data e hora
marcadas***

> **Dado que** uma sessão de defesa está com status "Agendada" ou
> "Reagendada",
>
> **Quando** o relógio do sistema atinge a data e o horário de início da
> sessão,
>
> **Então** o sistema altera o status da sessão automaticamente para "Em
> Andamento",
>
> **E** desbloqueia o formulário de avaliação da Parte Oral para os
> membros da banca.

***Cenário 5: Transição para "Realizada" ao liberar o resultado***

> **Dado que** a defesa está com status "Em Andamento" e todas as notas
> foram apuradas,
>
> **Quando** o Orientador clica em "Liberar Resultado" no painel da
> banca,
>
> **Então** o sistema altera o status da sessão automaticamente para
> "Realizada",
>
> **E** atualiza o Status do TCC conforme o parecer homologado.

***Cenário 6: Reagendamento de defesa com justificativa***

> **Dado que** a defesa está com status "Agendada" e o Orientador ou
> Professor da Disciplina precisa alterar a data,
>
> **Quando** clica em "Reagendar", seleciona a nova data/horário sem
> conflitos, insere uma justificativa válida com até 500 caracteres e
> confirma,
>
> **Então** o sistema atualiza o status para "Reagendada", preserva a
> banca e eventuais notas parciais salvas e notifica todos os envolvidos
> com os novos dados.

***Cenário 7: Cancelamento de sessão com justificativa e preservação do
TCC apto***

> **Dado que** ocorreu um imprevisto impeditivo em uma defesa com status
> "Agendada",
>
> **Quando** o Orientador, Professor da Disciplina ou Secretaria clica
> em "Cancelar sessão", informa a justificativa e confirma,
>
> **Então** o sistema define o status da sessão como "Cancelada",
> descarta eventuais avaliações salvas, mantém o Status do TCC como
> "Apto para Defesa" para permitir nova marcação e notifica os
> participantes.

***Cenário 8: Reagendamento bloqueado por conflito de horário na
banca***

> **Dado que** o Orientador ou Professor da Disciplina está reagendando
> uma defesa,
>
> **Quando** informa uma nova data e horário em que um dos membros da
> banca já possui outra defesa ativa,
>
> **Então** o sistema rejeita a alteração (*Hard Fail*), não salva a
> nova data e alerta sobre o conflito de agenda do avaliador.

***Cenário 9: Tentativa de reagendamento sem preenchimento de
justificativa***

> **Dado que** o Orientador, Professor da Disciplina ou Secretaria abriu
> o modal de reagendamento,
>
> **Quando** define nova data e horário mas deixa o campo Justificativa
> em branco e tenta confirmar,
>
> **Então** o sistema impede a operação, mantém a sessão inalterada e
> indica que o preenchimento da justificativa é obrigatório.

***Cenário 10: Tentativa de cancelamento de sessão sem justificativa***

> **Dado que** o Orientador ou Professor da Disciplina abriu o modal de
> cancelamento de sessão,
>
> **Quando** clica em confirmar mantendo o campo Justificativa vazio,
>
> **Então** o sistema não cancela a sessão e destaca a obrigatoriedade
> da justificativa com até 500 caracteres.

***Cenário 11: Justificativa de cancelamento acima do limite de
caracteres***

> **Dado que** o Orientador, Professor da Disciplina ou Secretaria está
> preenchendo o formulário de cancelamento da sessão,
>
> **Quando** digita um texto com 501 caracteres no campo Justificativa e
> tenta confirmar,
>
> **Então** o sistema bloqueia o cancelamento, destaca o campo e alerta
> sobre o limite máximo de 500 caracteres.

***Cenário 12: Tentativa de reagendar ou cancelar sessão já Realizada***

> **Dado que** uma defesa já foi concluída e encontra-se com status
> "Realizada",
>
> **Quando** o Orientador, Professor da Disciplina ou Secretaria
> visualiza os detalhes da sessão,
>
> **Então** o sistema não disponibiliza os botões "Reagendar" e
> "Cancelar sessão", mantendo o registro histórico imutável.

***Cenário 13: Tentativa de reagendamento por perfil não autorizado***

> **Dado que** um docente que não é o Orientador do TCC nem o Professor
> da Disciplina daquela turma está autenticado,
>
> **Quando** tenta acionar a ação de reagendamento da defesa,
>
> **Então** o sistema nega a operação informando que a ação é restrita
> aos responsáveis pela turma e orientação.

***Cenário 14: Acesso sem estar autenticado***

> **Dado que** o Orientador, Professor da Disciplina, Membro da Banca ou
> Aluno não possui sessão ativa no sistema,
>
> **Quando** tenta acessar o link direto da sessão de defesa ou das
> ações de reagendamento/cancelamento,
>
> **Então** o sistema direciona para a tela de login (US-11) e, após a
> autenticação, restabelece a navegação.

***Cenário 15: Notificação contendo o link do Documento para Defesa***

> **Dado que** a defesa foi agendada com sucesso,
>
> **Quando** os avaliadores abrem a notificação no sistema ou no e-mail
> recebido,
>
> **Então** a mensagem exibe a URL clicável que redireciona diretamente
> ao documento entregue pelo aluno para avaliação prévia da Parte
> Escrita.

**Tela no protótipo**

**Tela:** Defesas / Sessão de defesa





**Diagrama de sequência**

**Diagrama relacionado:** \[nome do diagrama ou "sem diagrama próprio" e
o motivo\]

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[X\] Descrição no formato Como, Quero, Para que
>
> \[X\] Requisitos da matriz conferidos
>
> \[X\] Fluxo principal e fluxos alternativos escritos
>
> \[X\] Atores, pré-condições e pós-condições preenchidos
>
> \[X\] Fluxos de exceção escritos
>
> \[X\] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-40 Ver a lista de sessões de defesa e filtrar por período

| **Épico:**                | Gestão da Defesa                         |
|---------------------------|------------------------------------------|
| **Feature:**              | Agendamento e Banca                      |
| **Requisitos da matriz:** | RBN-DEF-01.4, RBN-DEF-01.5, RBN-DEF-01.6 |
| **Prioridade (MoSCoW):**  | Must Have                                |
| **Responsável:**          | Célio Benjamim                           |

**Descrição**

Como Aluno, Docente (Orientador, Coorientador ou Avaliador), Professor
da Disciplina, Coordenador de Curso ou Secretaria, quero consultar a
lista de sessões de defesa e filtrar as ocorrências por período, status
e curso, para que eu possa acompanhar as defesas agendadas ou realizadas
dentro do escopo da minha atuação acadêmica.

**Atores**

> **Ator principal:** Aluno, Docente (Orientador, Coorientador ou
> Avaliador da banca), Professor da Disciplina, Coordenador de Curso ou
> Secretaria (conforme o perfil institucional autenticado que realiza a
> consulta).
>
> **Atores secundários:** Não há atores secundários (trata-se de uma
> funcionalidade estrita de consulta, filtragem e auditoria histórica de
> dados consolidados).

**Pré-condições**

- O Aluno, Docente, Professor da Disciplina, Coordenador de Curso ou
  > Secretaria está autenticado no sistema, com o Status da Conta Ativa
  > (US-11). Sem sessão ativa, aplica-se o E1.

- O usuário possui perfil institucional vinculado a pelo menos um curso
  > ou turma do NUCOMP.

- Existem turmas e defesas cadastradas no período consultado (caso não
  > existam defesas cadastradas no intervalo, aplica-se o fluxo
  > alternativo A).

**Fluxo principal**

1.  No menu lateral do sistema, o Aluno, Docente, Professor da
    > Disciplina, Coordenador de Curso ou Secretaria seleciona o item
    > Defesas.

2.  O sistema identifica o perfil e os vínculos institucionais do
    > usuário autenticado e recupera o Período Letivo atual como filtro
    > de data padrão (RBN-DEF-01.5).

3.  O sistema aplica o controle de visibilidade conforme o papel de
    > negócio do usuário (RBN-DEF-01.4):

- O Aluno, Orientador, Coorientador (com convite aceito) e Avaliador
  > visualizam apenas as sessões em que constam nominalmente;

- O Professor da Disciplina visualiza todas as sessões dos alunos
  > matriculados em sua turma;

- O Coordenador de Curso e a Secretaria visualizam todas as sessões de
  > defesa do curso selecionado no filtro.

4.  O sistema renderiza a listagem das defesas em ordem cronológica com
    > as colunas: Data, Horário, Aluno, Título do Trabalho, Orientador,
    > Local ou Link e Status da sessão (RBN-DEF-01.2).

5.  O Aluno, Docente, Professor da Disciplina, Coordenador de Curso ou
    > Secretaria seleciona um atalho de período na lista suspensa (Esta
    > Semana, Este Mês ou Próximos 30 Dias) ou preenche manualmente os
    > campos Data Inicial e Data Final via calendário (E2 e E3).

6.  Opcionalmente, o usuário escolhe um filtro de Status na lista
    > suspensa (Agendada, Reagendada, Em Andamento, Realizada, Cancelada
    > ou Todos).

7.  O sistema aplica os filtros de data e status e atualiza
    > instantaneamente a tabela com as sessões correspondentes.

8.  O usuário clica no botão "Histórico" na linha de uma defesa
    > específica.

9.  O sistema abre uma janela modal somente leitura contendo a linha do
    > tempo completa e auditável de todos os eventos da defesa
    > (agendamento, reagendamento, cancelamento, acionamento de
    > suplente, início automático e liberação do resultado), registrando
    > data, hora, o nome do responsável pela ação e eventuais
    > justificativas informadas (RBN-DEF-01.6).

10. O usuário clica em "Fechar" no modal e retorna à listagem de
    > defesas. O fluxo termina.

**Fluxos alternativos**

1.  Consulta sem registros no período selecionado (passo 4 ou passo 7):
    > Se não existirem defesas cadastradas para o período, status ou
    > curso filtrados, o sistema mantém os cabeçalhos da tabela e exibe
    > a mensagem informativa: "Nenhuma sessão de defesa encontrada para
    > o período e filtros selecionados". O usuário pode redefinir os
    > parâmetros de busca. O fluxo prossegue a partir do passo 5.

2.  Filtragem por curso pela Secretaria ou Coordenador de Curso
    > (RBN-CAD-14.1; passo 3): Quando a Secretaria ou o Coordenador de
    > Curso acessa a tela, o sistema disponibiliza adicionalmente a
    > lista suspensa "Curso" (Engenharia de Computação, Sistemas de
    > Informação, Licenciatura em Computação ou Todos), preenchida por
    > padrão com o curso do usuário autenticado (US-39). A Secretaria ou
    > Coordenador seleciona outro curso ou "Todos" e o sistema recarrega
    > a tabela de defesas correspondente. O fluxo prossegue a partir do
    > passo 4.

3.  Consulta do histórico pelo painel do aluno (RBN-CAD-08.9; passo 1):
    > No painel individual do aluno da turma (US-41) ou no Painel de
    > orientandos (US-18), o Professor da Disciplina ou o Orientador
    > clica no link "Histórico da defesa". O sistema abre diretamente a
    > mesma janela modal do passo 9. Ao fechar o modal, o usuário
    > retorna à tela em que estava. O fluxo termina.

4.  Histórico de sessão que sofreu reagendamento ou cancelamento (passo
    > 9): Ao consultar o histórico de uma defesa que teve data/hora
    > alterada ou foi cancelada, o modal exibe a data/hora do evento, o
    > nome do responsável, os horários anterior e retificado e a
    > Justificativa obrigatória preenchida na ação (US-24). O fluxo
    > prossegue a partir do passo 10.

5.  Histórico de sessão com acionamento de suplente (passo 9): Ao
    > consultar o histórico de uma sessão na qual o suplente assumiu a
    > vaga de titular, o modal exibe o evento de acionamento com data,
    > hora, o Orientador como autor da substituição, o avaliador titular
    > substituído e a Justificativa obrigatória registrada (US-23). O
    > fluxo prossegue a partir do passo 10.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): Caso o Aluno, Docente,
> Professor da Disciplina, Coordenador de Curso ou Secretaria tente
> acessar a listagem de defesas sem uma sessão ativa no navegador (via
> menu ou URL direta), o sistema apresenta a tela de login (US-11). Após
> a autenticação com sucesso, direciona para a tela de defesas e o fluxo
> prossegue a partir do passo 2. Em caso de falha na autenticação,
> aplicam-se as exceções da US-11.
>
> E2. Intervalo de datas inconsistente no filtro manual (passo 5): O
> usuário preenche uma Data Inicial que é cronologicamente posterior à
> Data Final informada (ex.: Data Inicial 25/11/2026 e Data Final
> 10/11/2026). O sistema bloqueia a consulta, mantém os dados anteriores
> na tabela e emite a mensagem de alerta: "A data inicial não pode ser
> superior à data final". Retorna ao passo 5.
>
> E3. Formato de data inválido no filtro manual (passo 5): O usuário
> digita uma data fora do padrão DD/MM/AAAA ou com dia/mês inválidos
> (ex.: 31/02/2026). O sistema não aplica o filtro, destaca o campo com
> erro e exibe: "Informe uma data válida no formato DD/MM/AAAA". Retorna
> ao passo 5.
>
> E4. Acesso indevido a dados de sessão por URL direta (passo 3): Se um
> docente tentar forçar a abertura de uma defesa pela URL na qual não
> faça parte da banca examinadora nem seja o Professor da Disciplina
> daquela turma, o sistema bloqueia o acesso e exibe: "Você não tem
> permissão para visualizar esta defesa". O fluxo termina.

**Pós-condições**

- Nenhum registro ou dado acadêmico é modificado na base de dados
  > (trata-se de uma consulta apenas de leitura).

- A listagem de defesas reflete os filtros temporais, de status e de
  > curso selecionados pelo usuário.

- O histórico completo de eventos de cada defesa é consultado e auditado
  > com garantia de sigilo e isolamento entre perfis institucionais.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                         | **Resumo da regra em uma frase**                                                                                                                                                              |
|--------------|-----------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **DEF-01.4** | O sistema deve exibir a lista de sessões de defesa.             | Apresenta listagem cronológica apenas de leitura contendo data, horário, estudante, título, orientador, local/link e estado, restringindo a visibilidade ao âmbito de atuação de cada perfil. |
| **DEF-01.5** | O sistema deve permitir filtrar as defesas por período.         | Disponibiliza filtro por datas inicial/final via calendário com atalhos predefinidos (com padrão no Período Letivo atual), aplicável de forma uniforme a todas as listagens de defesa.        |
| **DEF-01.6** | O sistema deve registrar e exibir o histórico da defesa do TCC. | Exibe um registro cronológico auditável apenas de leitura com todos os eventos, datas, justificativas e responsáveis de cada sessão do TCC.                                                   |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Lista com data, horário, aluno, título, orientador, local ou link
> e status; cada perfil vê as sessões de que participa, e Coordenação e
> Secretaria veem todas.
>
> 2\. Filtro por data inicial e final e atalhos (período letivo, esta
> semana, este mês, próximas, realizadas), aplicado também à agenda, aos
> ouvintes e aos relatórios de defesas.

***Cenário 1: Consulta padrão da listagem com filtro inicial do período
letivo***

> **Dado que** o Orientador, Professor da Disciplina, Coordenador de
> Curso ou Secretaria está autenticado no sistema,
>
> **Quando** acessa a tela de listagem de defesas no menu principal,
>
> **Então** o sistema carrega os registros do Período Letivo atual
> ordenados cronologicamente,
>
> **E** exibe as colunas Data, Horário, Aluno, Título, Orientador, Local
> ou Link e Status.

***Cenário 2: Restrição de visibilidade para perfil Aluno***

> **Dado que** o Aluno "José Silva" está autenticado no sistema,
>
> **Quando** abre a tela de sessões de defesa,
>
> **Então** o sistema exibe exclusivamente a sessão de defesa vinculada
> ao seu próprio TCC, ocultando as defesas dos demais estudantes.

***Cenário 3: Restrição de visibilidade para Docente avaliador da
banca***

> **Dado que** a docente "Camila Freitas Duarte" atua como 1ª Avaliadora
> em duas defesas e não possui papel de Coordenação nem de Secretaria,
>
> **Quando** acessa a listagem de defesas,
>
> **Então** o sistema exibe apenas as duas defesas em que ela integra a
> banca examinadora.

***Cenário 4:Visibilidade das defesas da turma pelo Professor da
Disciplina***

> **Dado que** o docente "Marcos Vinícius Lobato" é Professor da
> Disciplina da turma "TCC 2 · ECP08_LOBATO",
>
> **Quando** acessa a tela de defesas,
>
> **Então** o sistema exibe todas as defesas agendadas e realizadas dos
> alunos matriculados naquela turma específica.

***Cenário 5: Visibilidade total e filtro por curso para Coordenação e
Secretaria***

> **Dado que** um usuário com o papel de Secretaria ou Coordenador de
> Curso de Engenharia de Computação está autenticado,
>
> **Quando** visualiza a tela de defesas,
>
> **Então** o sistema exibe todas as defesas do curso de Engenharia de
> Computação, independentemente de quem compõe a banca examinadora,
>
> **E** disponibiliza a lista suspensa de Curso para alternar entre
> cursos do NUCOMP.

***Cenário 6: Utilização do atalho de período "Esta Semana"***

> **Dado que** o usuário deseja consultar apenas as bancas da semana
> corrente,
>
> **Quando** seleciona o atalho "Esta Semana" na lista suspensa de
> período,
>
> **Então** o sistema preenche automaticamente as datas inicial e final
> da semana atual e atualiza a listagem de imediato.

***Cenário 7: Utilização do atalho de período "Este Mês"***

> **Dado que** o usuário está na tela de defesas,
>
> **Quando** seleciona o atalho "Este Mês" no filtro de período,
>
> **Então** o sistema ajusta as datas para o primeiro e último dia do
> mês corrente e filtra os registros correspondentes.

***Cenário 8: Utilização do atalho de período "Próximos 30 Dias"***

> **Dado que** o Orientador deseja verificar os compromissos do próximo
> mês,
>
> **Quando** seleciona o atalho "Próximos 30 Dias" no filtro de defesas,
>
> **Então** o sistema calcula o intervalo de 30 dias a partir da data de
> hoje e exibe as bancas agendadas nesse período.

***Cenário 9: Filtragem manual por intervalo de datas válido***

> **Dado que** a Secretaria precisa emitir uma consulta específica,
>
> **Quando** seleciona a Data Inicial "01/10/2026" e a Data Final
> "15/10/2026" no calendário,
>
> **Então** o sistema recupera e exibe todas as defesas ocorridas ou
> agendadas exclusivamente dentro desse intervalo.

***Cenário 10: Filtragem por status da sessão***

> **Dado que** existem defesas com múltiplos status cadastrados na base
> de dados,
>
> **Quando** o Professor da Disciplina seleciona o status "Agendada" no
> filtro de status,
>
> **Então** a tabela oculta as defesas realizadas ou canceladas e
> apresenta apenas as sessões que estão agendadas.

***Cenário 11: Consulta sem registros encontrados para o filtro
aplicado***

> **Dado que** não há defesas marcadas para o período entre 01/01/2026 e
> 10/01/2026,
>
> **Quando** o usuário aplica esse intervalo de datas,
>
> **Então** o sistema exibe a mensagem "Nenhuma sessão de defesa
> encontrada para o período e filtros selecionados" e mantém os filtros
> acessíveis para nova busca.

***Cenário 12: Visualização do histórico completo da defesa com eventos
de processo***

> **Dado que** uma defesa passou por agendamento inicial, início de
> sessão e homologação do resultado,
>
> **Quando** o Aluno, Docente ou Secretaria clica no botão "Histórico"
> dessa defesa,
>
> **Então** o sistema abre a janela modal exibindo a sequência
> cronológica dos eventos, os horários, os nomes dos responsáveis e o
> resultado homologado.

***Cenário 13: Histórico registrando evento de reagendamento com
justificativa***

> **Dado que** uma defesa foi reagendada pelo Orientador com
> justificativa formal,
>
> **Quando** o usuário abre o modal de histórico dessa sessão,
>
> **Então** o sistema evidencia o horário anterior, o novo horário
> marcado, o autor da alteração e o texto da justificativa.

***Cenário 14: Histórico registrando evento de cancelamento da sessão***

> **Dado que** uma defesa foi cancelada pela Secretaria devido a força
> maior,
>
> **Quando** o usuário consulta o histórico dessa defesa,
>
> **Então** o sistema exibe o registro de cancelamento com data, hora, o
> nome do responsável e a justificativa apresentada.

***Cenário 15: Histórico registrando evento de acionamento de
suplente***

> **Dado que** o Orientador acionou o suplente durante a sessão para
> substituir o 2º Avaliador ausente,
>
> **Quando** o usuário visualiza o histórico da defesa,
>
> **Então** o sistema lista o evento de substituição, registrando o
> titular ausente, o suplente promovido e a justificativa.

***Cenário 16: Validação de intervalo de datas manual invertido (E2)***

> **Dado que** o usuário está personalizando os campos de data no
> filtro,
>
> **Quando** informa uma Data Inicial posterior à Data Final e tenta
> aplicar a filtragem,
>
> **Então** o sistema não atualiza a tabela e exibe a mensagem de erro
> "A data inicial não pode ser superior à data final".

***Cenário 17: Validação de formato de data inválido (E3)***

> **Dado que** o usuário está digitando manualmente a data no campo de
> filtro,
>
> **Quando** insere o valor "32/10/2026",
>
> **Então** o sistema destaca o campo e alerta que a data informada não
> é válida.

***Cenário 18: Acesso sem autenticação redireciona para a tela de login
(E1)***

> **Dado que** o usuário não possui uma sessão ativa no sistema,
>
> **Quando** tenta acessar o endereço direto da lista de sessões de
> defesa,
>
> **Então** o sistema direciona para a tela de login (US-11) e, após a
> autenticação, exibe a listagem de defesas.

**Tela no protótipo**

**Tela:** Defesas



**Diagrama de sequência**

**Diagrama relacionado:** Sem diagrama próprio, por se tratar de uma
funcionalidade estrita de consulta, filtragem e exibição de dados
agregados.

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[X\] Descrição no formato Como, Quero, Para que
>
> \[X\] Requisitos da matriz conferidos
>
> \[X\] Fluxo principal e fluxos alternativos escritos
>
> \[X\] Atores, pré-condições e pós-condições preenchidos
>
> \[X\] Fluxos de exceção escritos
>
> \[X\] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

##  

## US-25 Lançar as notas dos critérios oficiais

| **Épico:**                | Gestão da Defesa                                                                   |
|---------------------------|------------------------------------------------------------------------------------|
| **Feature:**              | Avaliação e Resultados                                                             |
| **Requisitos da matriz:** | RBN-DEF-04.1, RBN-DEF-04.2, RBN-DEF-05.1, RBN-DEF-05.2, RBN-DEF-05.3, RBN-DEF-05.4 |
| **Prioridade (MoSCoW):**  | Must Have                                                                          |
| **Responsável:**          | Célio Benjamim                                                                     |

**Descrição**

Como Avaliador (Docente ou Membro Externo integrante da banca
examinadora), quero consultar os critérios oficiais da EST/UEA, lançar
os conceitos e notas nos 9 critérios e assinar visualmente o formulário,
para que minha avaliação individual seja formalmente computada no
cálculo da nota final do TCC.

**Atores**

> **Ator principal:** Avaliador da banca examinadora
> (Orientador/Presidente, 1º Avaliador titular, 2º Avaliador titular ou
> Suplente ativado durante a sessão; podendo ser Docente do NUCOMP ou
> Membro Externo).
>
> **Atores secundários:** Orientador do TCC (acompanha o status de envio
> de cada membro para iniciar a deliberação na US-27) e Aluno do TCC
> (cujo trabalho é avaliado).

**Pré-condições**

- O Avaliador (Docente ou Membro Externo) está autenticado no sistema,
  > com o Status da Conta Ativa (US-11). Sem sessão ativa, aplica-se o
  > E1.

- A sessão de defesa foi previamente agendada e possui status Agendada,
  > Reagendada ou Em Andamento (US-21 e US-24).

- O usuário autenticado consta como membro titular da banca daquela
  > defesa (Orientador, 1º Avaliador, 2º Avaliador ou Suplente ativado
  > por acionamento oficial na US-23).

- O Aluno realizou a entrega do tipo "Documento para Defesa" com URL
  > pública válida acessível no sistema (US-15).

**Fluxo principal**

1.  No menu lateral do sistema, o Avaliador (Docente ou Membro Externo)
    > seleciona o item Minhas bancas (RBN-DEF-05.4).

2.  O sistema lista as sessões de defesa em que o Avaliador participa,
    > destacando visualmente as avaliações pendentes com atalhos para o
    > documento do trabalho e para os critérios de avaliação
    > (RBN-DEF-05.4).

3.  O Avaliador clica no botão "Avaliar" na linha da defesa
    > correspondente.

4.  O sistema verifica a composição da banca (RBN-DEF-05.3), identifica
    > o status da sessão (RBN-DEF-05.1) e abre o formulário de avaliação
    > exibindo os dados do trabalho, a tabela fixa dos critérios
    > oficiais (RBN-DEF-04.1) e o link para visualização do Documento
    > para Defesa.

5.  O Avaliador consulta o texto do trabalho entregue pelo estudante e a
    > descrição dos 9 critérios oficiais de avaliação da EST/UEA.

6.  Para cada um dos 6 critérios do Componente Parte Escrita (Relevância
    > do Tema, Metodologia, Revisão da Literatura, Resultados e
    > Discussões, Conclusões e Redação), o Avaliador seleciona o
    > Conceito na lista suspensa obrigatória: "Exemplar", "Competente"
    > ou "Necessita de Trabalho" (RBN-DEF-05.2).

7.  O Avaliador informa a Nota numérica com uma casa decimal para cada
    > critério da Parte Escrita, respeitando rigorosamente a faixa do
    > conceito escolhido: Exemplar (8,0 a 10,0), Competente (6,0 a 7,9)
    > ou Necessita de Trabalho (0,0 a 5,9) (RBN-DEF-05.2; E2).

8.  Opcionalmente, o Avaliador preenche apontamentos no campo
    > Observações (até 500 caracteres) em qualquer dos critérios
    > escritos (E8).

9.  Antes da data da defesa (sessão com status Agendada ou Reagendada),
    > o Avaliador clica no botão "Salvar". O sistema salva as notas da
    > Parte Escrita como rascunho sem finalizar a avaliação, mantendo os
    > campos da Parte Oral bloqueados (RBN-DEF-05.1).

10. Durante a realização da apresentação da defesa (status da sessão
    > alterado automaticamente para "Em Andamento"), o sistema
    > desbloqueia os campos dos 3 critérios do Componente Parte Oral
    > (Organização, Domínio do Assunto e Postura perante a banca) e o
    > botão "Enviar avaliação assinada" (RBN-DEF-05.1).

11. O Avaliador seleciona o Conceito, digita a Nota numérica válida
    > dentro da faixa e insere eventuais Observações para os 3 critérios
    > da Parte Oral (E2 e E8).

12. O Avaliador vincula a sua assinatura visual obrigatória no
    > formulário, anexando um arquivo PNG/JPG de até 2 MB ou marcando a
    > opção para reutilizar a assinatura salva em seu perfil
    > institucional (US-26; E5).

13. O Avaliador clica no botão "Enviar avaliação assinada".

14. O sistema valida o preenchimento integral dos 9 critérios e da
    > assinatura visual (E4 e E5), calcula a nota individual do membro
    > multiplicando as notas pelos seus pesos com uma casa decimal e
    > arredondamento comercial (RBN-DEF-06.1), grava o envio com data e
    > hora e atualiza o status da avaliação do membro para "enviada". O
    > fluxo termina.

**Fluxos alternativos**

1.  Consulta prévia dos critérios vigentes da EST/UEA (DEF-04.2; passo
    > 1): Na tela Minhas bancas, o Avaliador aciona o link "Critérios de
    > avaliação". O sistema abre uma tela ou modal somente leitura
    > exibindo os 6 critérios da Parte Escrita (peso 7,0), os 3
    > critérios da Parte Oral (peso 3,0), a soma dos pesos igual a 10,0
    > e a descrição dos níveis conceituais (Exemplar, Competente e
    > Necessita de Trabalho). O Avaliador consulta as normas e fecha a
    > janela. O fluxo prossegue a partir do passo 3.

2.  Reabertura e reenvio de avaliação durante a deliberação da banca
    > (DEF-06.1; passo 14): Durante a sessão ("Em Andamento") e antes de
    > o Orientador clicar em "Liberar Resultado" (US-27), o Avaliador
    > clica no botão "Reabrir minha avaliação", ajusta os conceitos,
    > notas ou observações de qualquer critério e clica novamente em
    > "Enviar avaliação assinada". O sistema recalcula a nota individual
    > e atualiza os totais para a deliberação. O fluxo termina.

3.  Avaliador suplente acionado para substituir titular ausente
    > (DEF-05.3 e DEF-02.2; passo 3): Quando o Suplente for ativado pelo
    > Orientador durante a sessão (US-23), a linha da defesa em Minhas
    > bancas passa a exibir o botão "Avaliar" habilitado para o
    > suplente. Ao abrir o formulário, o Suplente visualiza os campos da
    > Parte Escrita e da Parte Oral liberados conjuntamente para
    > preenchimento integral em tempo real. O fluxo prossegue a partir
    > do passo 5.

4.  Avaliador com perfil de Membro Externo (passo 1): O Membro Externo
    > autenticado acessa diretamente o painel Minhas bancas (já que não
    > possui permissão para turmas e relatórios institucionais),
    > visualizando exclusivamente as defesas para as quais foi
    > designado. O fluxo prossegue a partir do passo 3.

5.  Download de declaração de participação em defesa Realizada (DEF-05.4
    > e DEF-08.3; passo 2): Na tela Minhas bancas, para sessões que
    > atingiram o status "Realizada", o sistema exibe o botão
    > "Declaração" ao lado dos dados da banca. O Avaliador clica no
    > botão e o sistema faz o download de sua declaração individual em
    > PDF contendo o código de validação institucional (US-30). O fluxo
    > termina.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): Caso o Avaliador tente acessar
> a tela Minhas bancas ou o formulário de avaliação sem sessão ativa no
> navegador, o sistema exibe a tela de login (US-11). Após a
> autenticação, direciona o Avaliador para a tela solicitada e o fluxo
> prossegue a partir do passo 2. Em caso de falha na autenticação,
> aplicam-se as exceções da US-11.
>
> E2. Nota fora da faixa do conceito selecionado (passos 7 ou 11): Se o
> Avaliador digitar uma nota fora dos limites do conceito atribuído
> (ex.: digitar 8,5 tendo marcado "Competente", ou 5,5 tendo marcado
> "Exemplar"), o sistema não salva, destaca o campo da nota e exibe: "A
> nota deve situar-se entre o valor mínimo e o máximo para o conceito
> selecionado (ex.: de 6,0 a 7,9 para Competente)". Retorna ao passo 7
> ou ao passo 11.
>
> E3. Tentativa de avaliar a Parte Oral antes da sessão (passo 9):
> Enquanto a defesa estiver com status "Agendada" ou "Reagendada", os
> campos dos 3 critérios da Parte Oral e o botão de submissão definitiva
> permanecem desabilitados. O sistema permite apenas acionar o botão
> "Salvar" para gravar o rascunho da Parte Escrita. Retorna ao passo 9.
>
> E4. Envio com critérios obrigatórios em branco (passo 13): Se o
> Avaliador clicar em "Enviar avaliação assinada" deixando qualquer um
> dos 9 critérios sem conceito selecionado ou sem nota numérica
> preenchida, o sistema bloqueia o envio, destaca as pendências e exibe:
> "Todos os 9 critérios devem conter conceito e nota". Retorna ao passo
> 6 ou ao passo 11.
>
> E5. Submissão sem assinatura visual vinculada (passo 13): Se o
> Avaliador preencher todos os critérios mas tentar submeter a avaliação
> definitiva sem anexar imagem e sem marcar a reutilização da assinatura
> do perfil (US-26), o sistema impede o envio e exibe: "A assinatura do
> membro da banca é obrigatória para finalizar a avaliação". Retorna ao
> passo 12.
>
> E6. Acesso por docente ou membro externo não integrante da banca
> (passo 3): Se um usuário autenticado que não seja o Orientador, o 1º
> Avaliador, o 2º Avaliador ou o Suplente ativado tentar acessar a
> avaliação daquele TCC (seja por link direto ou menu), o sistema nega o
> acesso e exibe: "Acesso restrito aos membros avaliadores da banca"
> (RBN-DEF-05.3). O fluxo termina.
>
> E7. Tentativa de edição em sessão já Realizada ou Cancelada (passo 3):
> Se a defesa já estiver com status "Realizada" (resultado liberado pelo
> Orientador) ou "Cancelada", o sistema exibe o formulário de avaliação
> apenas para leitura, com as notas fixadas e sem botões de edição ou
> envio. O fluxo termina.
>
> E8. Observações acima do limite de caracteres (passos 8 ou 11): Se o
> texto digitado no campo Observações de qualquer critério ultrapassar
> 500 caracteres, o sistema não salva o formulário, destaca o campo e
> indica o limite máximo de 500 caracteres. Retorna ao passo 8 ou ao
> passo 11.

**Pós-condições**

- Os conceitos e notas numéricas dos 9 critérios oficiais foram
  > persistidos no banco de dados vinculados ao Avaliador e à defesa.

- A nota individual do Avaliador foi calculada com uma casa decimal e
  > arredondamento comercial pela média ponderada dos pesos oficiais
  > (RBN-DEF-06.1).

- A imagem da assinatura visual do Avaliador foi chancelada e associada
  > ao registro da avaliação com registro de data e hora (US-26).

- O status da avaliação do membro passou para "enviada", liberando a
  > verificação de quórum de avaliações para o cálculo da nota final
  > pelo Orientador (US-27).

- No salvamento prévio antes da defesa, as notas da Parte Escrita foram
  > preservadas como rascunho sem oficialização do envio.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                                 | **Resumo da regra em uma frase**                                                                                                                                                                                                                                                                                                                                                                                              |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **DEF-04.1** | O sistema deve fornecer, de forma fixa e não editável, os 9 critérios oficiais de avaliação da EST/UEA.                                                                 | Disponibiliza de forma fixa e imutável os 6 critérios da Parte Escrita (peso total 7,0) e os 3 da Parte Oral (peso total 3,0), somando peso 10,0.                                                                                                                                                                                                                                                                             |
| **DEF-04.2** | O sistema deve permitir a consulta dos critérios vigentes pelos avaliadores.                                                                                            | Exibe tela somente leitura com o nome, peso e descritivos das faixas conceituais de cada critério oficial para consulta rápida dos avaliadores.                                                                                                                                                                                                                                                                               |
| **DEF-05.1** | O sistema deve liberar a avaliação da Parte Escrita antes da banca e a da Parte Oral apenas durante a sessão.                                                           | Libera o preenchimento da Parte Escrita nas sessões agendadas e desbloqueia os critérios da Parte Oral e o envio final apenas com a sessão Em Andamento.                                                                                                                                                                                                                                                                      |
| **DEF-05.2** | O sistema deve mostrar um formulário de avaliação que deve conter, para cada critério, os campos Conceito, Nota e Observações, e o campo Assinatura do Membro da Banca. | Apresenta campo em lista suspensa obrigatória para cada critério, com seleção única entre: Exemplar, Competente ou Necessita de Trabalho. Apresenta campo numérico com uma casa decimal que aceita estritamente valores contidos na faixa do conceito escolhido (8,0 a 10,0; 6,0 a 7,9; 0,0 a 5,9). Disponibiliza campo de texto livre opcional para apontamentos do avaliador com limite de até 500 caracteres por critério. |
| **DEF-05.3** | O sistema deve restringir o acesso ao formulário de avaliação aos membros da banca da sessão.                                                                           | Restringe o acesso ao formulário exclusivamente ao Orientador, ao 1º e ao 2º Avaliador (ou Suplente ativado) designados para a sessão específica.                                                                                                                                                                                                                                                                             |
| **DEF-05.4** | O sistema deve exibir ao Docente e ao Membro Externo as bancas de que participa.                                                                                        | Lista as bancas ativas do usuário com papel desempenhado, data, status, destaque para avaliações pendentes e atalhos ao documento do TCC e aos critérios.                                                                                                                                                                                                                                                                     |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. 9 Critérios da EST fixos no sistema (peso total 10,0).
>
> 2\. Notas bloqueadas no limite do conceito (Ex: Competente = 6,0 a
> 7,9).
>
> 3\. Parte Oral só é desbloqueada no dia/hora da sessão.

***Cenário 1: Lançamento de notas completo e submissão com sucesso na
sessão em andamento***

> **Dado que** o Avaliador (Orientador, 1º Avaliador ou 2º Avaliador)
> está com a defesa no status "Em Andamento",
>
> **E** vinculou a sua assinatura visual com sucesso (conforme US-26),
>
> **Quando** preenche os conceitos e notas numéricas válidas para todos
> os 9 critérios da Parte Escrita e da Parte Oral,
>
> **E** clica em "Enviar avaliação assinada",
>
> **Então** o sistema valida as notas e a assinatura, calcula a nota
> individual do avaliador e atualiza o status da sua avaliação para
> "enviada".

***Cenário 2: Rascunho da Parte Escrita salvo com sucesso antes da
defesa***

> **Dado que** a defesa está com status "Agendada" e faltam 3 dias para
> a sessão,
>
> **Quando** o Avaliador preenche os conceitos e notas dos 6 critérios
> da Parte Escrita e clica em "Salvar",
>
> **Então** o sistema grava as notas da Parte Escrita como rascunho,
>
> **E** mantém o formulário da Parte Oral bloqueado para edição
> (DEF-05.1).

***Cenário 3: Bloqueio de nota superior à faixa do conceito
selecionado***

> **Dado que** o Avaliador selecionou o conceito "Competente" para o
> critério Metodologia,
>
> **Quando** digita a nota "8,5" no campo correspondente e tenta
> avançar,
>
> **Então** o sistema bloqueia a gravação e exibe mensagem informando
> que para o conceito Competente a nota deve situar-se entre 6,0 e 7,9.

***Cenário 4: Bloqueio de nota inferior à faixa do conceito
selecionado***

> **Dado que** o Avaliador selecionou o conceito "Exemplar" para o
> critério Domínio do Assunto,
>
> **Quando** digita a nota "7,5" e tenta salvar,
>
> **Então** o sistema impede o salvamento e alerta que para o conceito
> Exemplar a nota deve situar-se entre 8,0 e 10,0.

***Cenário 5: Bloqueio de nota com mais de uma casa decimal***

> **Dado que** o Avaliador está inserindo a nota do critério Relevância
> do Tema,
>
> **Quando** digita a nota "8,75" com duas casas decimais,
>
> **Então** o sistema formata e restringe a entrada para apenas uma casa
> decimal ou alerta sobre o formato exigido.

***Cenário 6: Bloqueio da Parte Oral antes do início da sessão***

> **Dado que** a defesa está com status "Agendada" ou "Reagendada",
>
> **Quando** o Avaliador abre o formulário de avaliação,
>
> **Então** o sistema permite editar apenas os critérios da Parte
> Escrita,
>
> **E** mantém os 3 critérios da Parte Oral e o botão "Enviar avaliação
> assinada" bloqueados e desabilitados para edição.

***Cenário 7: Desbloqueio da Parte Oral ao atingir o horário da
sessão***

> **Dado que** a sessão estava com status "Agendada",
>
> **Quando** o relógio do sistema atinge o horário de início da defesa e
> o status transita para "Em Andamento",
>
> **Então** o sistema desbloqueia os campos de conceito, nota e
> observações da Parte Oral e habilita o botão "Enviar avaliação
> assinada".

***Cenário 8: Bloqueio de submissão com critério em branco***

> **Dado que** o Avaliador preencheu 8 critérios,
>
> **Quando** deixa o conceito e a nota do critério Postura perante a
> banca em branco e clica em "Enviar avaliação assinada",
>
> **Então** o sistema bloqueia o envio definitivo, destaca o critério
> pendente e alerta sobre o preenchimento obrigatório de todos os 9
> critérios.

***Cenário 9: Bloqueio de submissão sem assinatura visual***

> **Dado que** o Avaliador preencheu os 9 critérios com notas válidas,
>
> **Quando** tenta enviar a avaliação sem fazer o upload da assinatura e
> sem reutilizar a assinatura do perfil,
>
> **Então** o sistema não envia a avaliação e destaca a obrigatoriedade
> da assinatura visual.

***Cenário 10: Bloqueio de acesso para docente não integrante da
banca***

> **Dado que** um docente autenticado não é Orientador, Avaliador
> titular nem Suplente ativo da defesa,
>
> **Quando** tenta abrir o formulário de avaliação desse trabalho por
> link direto ou menu,
>
> **Então** o sistema bloqueia o acesso e exibe a mensagem "Acesso
> restrito aos membros avaliadores da banca".

***Cenário 11: Painel Minhas Bancas exibindo defesas e destacando
avaliações pendentes***

> **Dado que** um docente foi cadastrado como avaliador titular em duas
> bancas distintas,
>
> **Quando** acessa o menu "Minhas bancas",
>
> **Então** o sistema lista as defesas em que participa, indicando
> papel, data e horário, e destaca as bancas que estão com avaliação
> pendente de envio.

***Cenário 12: Consulta dos 9 critérios oficiais e descrições
conceituais***

> **Dado que** o Avaliador está no painel Minhas bancas ou no formulário
> de avaliação,
>
> **Quando** aciona o link "Critérios de avaliação",
>
> **Então** o sistema abre a visualização somente leitura detalhando os
> 9 critérios da EST/UEA, pesos e descritivos das faixas Exemplar,
> Competente e Necessita de Trabalho.

***Cenário 13: Reabertura e retificação de notas durante a deliberação
da banca***

> **Dado que** o Avaliador já havia enviado sua avaliação, mas a banca
> está reunida em deliberação antes da liberação oficial,
>
> **Quando** clica em "Reabrir minha avaliação", altera a nota de
> Redação de 8,0 para 8,5 e clica novamente em enviar,
>
> **Então** o sistema atualiza as notas gravadas e recalcula a nota
> individual daquele avaliador.

***Cenário 14: Avaliação integral realizada por Suplente convocado***

> **Dado que** o Suplente foi oficialmente acionado pelo Orientador
> durante a sessão para substituir um titular ausente,
>
> **Quando** o Suplente abre a avaliação em Minhas bancas,
>
> **Então** o sistema disponibiliza o formulário completo com a Parte
> Escrita e a Parte Oral liberadas para preenchimento em tempo real.

***Cenário 15: Download da declaração de participação em defesa
Realizada***

> **Dado que** uma defesa na qual o docente participou já teve o
> resultado liberado e está com status "Realizada",
>
> **Quando** o docente acessa a tela Minhas bancas e clica no botão
> "Declaração" na linha correspondente,
>
> **Então** o sistema realiza o download da declaração de participação
> em banca em formato PDF com código validador.

***Cenário 16: Campo Observações com mais de 500 caracteres bloqueado***

> **Dado que** o Avaliador está inserindo apontamentos no campo
> Observações de um critério,
>
> **Quando** digita um texto com 501 caracteres e tenta salvar,
>
> **Então** o sistema bloqueia o salvamento, destaca o campo e indica o
> limite máximo de 500 caracteres.

***Cenário 17: Tentativa de alteração de notas após liberação do
resultado***

> **Dado que** o Orientador já clicou em "Liberar Resultado" e a defesa
> está com status "Realizada",
>
> **Quando** um Avaliador tenta reabrir a sua avaliação,
>
> **Então** o formulário é exibido apenas para consulta, com os campos
> bloqueados e sem botão de reenvio de notas.

***Cenário 18: Acesso sem autenticação redirecionando para a tela de
login (E1)***

> **Dado que** o Avaliador não possui uma sessão ativa no sistema,
>
> **Quando** tenta acessar o endereço direto da tela Minhas bancas ou do
> formulário de avaliação,
>
> **Então** o sistema redireciona para a tela de login (US-11) e, após a
> autenticação bem-sucedida, abre a tela solicitada.

**Tela no protótipo**

**Tela:** Minhas bancas / Avaliação





**Diagrama de sequência**

**Diagrama relacionado:** \[nome do diagrama ou "sem diagrama próprio" e
o motivo\]

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[X\] Descrição no formato Como, Quero, Para que
>
> \[X\] Requisitos da matriz conferidos
>
> \[X\] Fluxo principal e fluxos alternativos escritos
>
> \[X\] Atores, pré-condições e pós-condições preenchidos
>
> \[X\] Fluxos de exceção escritos
>
> \[X\] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-26 Enviar a imagem da assinatura

| **Épico:**                | Gestão da Defesa       |
|---------------------------|------------------------|
| **Feature:**              | Avaliação e Resultados |
| **Requisitos da matriz:** | RBN-DEF-05.2           |
| **Prioridade (MoSCoW):**  | Must Have              |
| **Responsável:**          | Célio Benjamim         |

**Descrição**

Como Avaliador (Docente ou Membro Externo integrante da banca
examinadora), quero anexar a imagem da minha assinatura visual ou
reutilizar a assinatura cadastrada no meu perfil, para que a avaliação
individual seja chancelada com registro de data e hora e conste na Ata
Final e na Folha de Aprovação.

**Atores**

> **Ator principal:** Avaliador da banca examinadora
> (Orientador/Presidente, 1º Avaliador titular, 2º Avaliador titular ou
> Suplente ativado durante a sessão; podendo ser Docente do NUCOMP ou
> Membro Externo).
>
> **Atores secundários:** Membros da banca examinadora e Aluno do TCC
> (que terão as assinaturas consolidadas nos documentos finais gerados
> na US-28).

**Pré-condições**

- O Avaliador (Docente ou Membro Externo) está autenticado no sistema,
  > com o Status da Conta Ativa (US-11). Sem sessão ativa, aplica-se o
  > E1.

- A sessão de defesa encontra-se com o status "Em Andamento" (US-24).

- O Avaliador é membro titular da banca da defesa (Orientador, 1º
  > Avaliador, 2º Avaliador ou Suplente convocado na US-23) e concluiu o
  > preenchimento de notas e conceitos dos 9 critérios oficiais (US-25).

- Para a opção de reutilização, o Avaliador possui imagem de assinatura
  > previamente cadastrada e salva no seu perfil institucional (US-38).

**Fluxo principal**

1.  No formulário de avaliação da defesa (US-25), após preencher os
    > conceitos e notas dos 9 critérios oficiais, o Avaliador acessa a
    > seção "Assinatura do Membro da Banca".

2.  O sistema apresenta o bloco de assinatura com o botão "Anexar imagem
    > (PNG ou JPG, até 2 MB)", a opção "Salvar esta imagem no meu
    > perfil" e a pré-visualização da assinatura já cadastrada no perfil
    > (quando existente).

3.  O Avaliador aciona o botão "Anexar imagem" e seleciona um arquivo de
    > imagem no seu dispositivo (ou opta por manter a assinatura já
    > carregada do perfil).

4.  O sistema processa o arquivo, valida o formato (PNG, JPG ou JPEG),
    > confere o tamanho máximo de 2 MB (E2 e E3) e renderiza a prévia
    > visual da assinatura no formulário.

5.  Opcionalmente, o Avaliador marca a caixa de seleção "Salvar esta
    > imagem no meu perfil" para atualizar a imagem de assinatura padrão
    > da sua conta (US-38).

6.  O Avaliador confere a prévia exibida e clica no botão "Enviar
    > avaliação assinada".

7.  O sistema valida a presença da assinatura (E4), associa a imagem da
    > assinatura à avaliação individual, registra a data e a hora do
    > envio junto ao registro e desbloqueia a conclusão da avaliação do
    > membro (US-25). O fluxo termina.

**Fluxos alternativos**

1.  Reutilização de assinatura salva no perfil institucional (DEF-05.2,
    > campo 4; passo 3): O Avaliador que já possui imagem cadastrada no
    > perfil (US-38) visualiza a prévia da assinatura já carregada na
    > seção. O Avaliador opta por reutilizar essa assinatura sem
    > realizar novo upload. O fluxo prossegue a partir do passo 6.

2.  Atualização da assinatura do perfil a partir do envio da avaliação
    > (passo 5): Ao anexar uma nova imagem de assinatura, o Avaliador
    > marca a opção "Salvar esta imagem no meu perfil". O sistema grava
    > a nova imagem na avaliação da defesa e atualiza simultaneamente a
    > imagem de assinatura do perfil do usuário para avaliações futuras
    > (US-38). O fluxo prossegue a partir do passo 6.

3.  Substituição da imagem antes da submissão definitiva (passo 4): Após
    > carregar uma imagem, o Avaliador clica no botão "Atualizar
    > imagem", seleciona outro arquivo PNG ou JPG e o sistema substitui
    > a prévia anterior no formulário. O fluxo prossegue a partir do
    > passo 4.

4.  Avaliador com perfil de Membro Externo (passo 3): O Membro Externo
    > da banca anexa sua imagem de assinatura diretamente pelo botão de
    > upload ou reutiliza a assinatura que informou no seu perfil de
    > acesso (US-38). O fluxo prossegue a partir do passo 4.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): Caso o Avaliador tente acessar
> a tela de avaliação sem uma sessão ativa, o sistema exibe a tela de
> login (US-11). Após a autenticação, direciona para o formulário de
> avaliação e o fluxo prossegue a partir do passo 1. Em caso de falha na
> autenticação, aplicam-se as exceções da US-11.
>
> E2. Arquivo com tamanho superior a 2 MB (passo 4): O Avaliador tenta
> anexar uma imagem de assinatura com tamanho maior que 2 MB. O sistema
> rejeita o carregamento, não grava o arquivo e exibe a mensagem: "O
> arquivo de assinatura deve ter tamanho máximo de 2 MB". Retorna ao
> passo 3.
>
> E3. Formato de imagem não suportado (passo 4): O Avaliador seleciona
> um arquivo que não possua extensão .png, .jpg ou .jpeg (ex.: .pdf,
> .svg, .bmp). O sistema bloqueia o upload, não atualiza a prévia e
> exibe: "Formato não suportado. Envie a assinatura em PNG ou JPG".
> Retorna ao passo 3.
>
> E4. Tentativa de submissão sem assinatura vinculada (passo 6): O
> Avaliador preenche os critérios de avaliação mas aciona "Enviar
> avaliação assinada" sem anexar imagem e sem selecionar a assinatura do
> perfil. O sistema bloqueia a submissão, destaca o bloco de assinatura
> e exibe: "A assinatura do membro da banca é obrigatória para finalizar
> a avaliação". Retorna ao passo 3.
>
> E5. Defesa fora do status Em Andamento (passo 1): Enquanto a sessão
> estiver com status Agendada ou Reagendada, o bloco de assinatura e o
> botão de submissão final permanecem bloqueados, sendo permitido apenas
> salvar a Parte Escrita como rascunho (US-25). O fluxo termina.
>
> E6. Usuário não pertencente à banca examinadora (passo 1): Caso um
> usuário autenticado que não componha a banca examinadora tente acessar
> o formulário, o sistema bloqueia o acesso e exibe: "Acesso restrito
> aos membros avaliadores da banca" (RBN-DEF-05.3). O fluxo termina.

**Pós-condições**

- A imagem da assinatura visual do Avaliador foi chancelada e vinculada
  > à avaliação individual do trabalho, com registro auditável de data e
  > hora de envio.

- A submissão da avaliação do membro foi concluída com sucesso no status
  > "enviada" (US-25).

- A imagem da assinatura ficou disponível no banco de dados para ser
  > replicada automaticamente na Ata Final (RBN-DEF-07.1) e na Folha de
  > Aprovação (RBN-DEF-07.2) na US-28.

- Caso a opção de salvar no perfil tenha sido marcada, a assinatura
  > padrão da conta do docente foi atualizada (US-38).

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                                 | **Resumo da regra em uma frase**                                                                                                                                                                                      |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **DEF-05.2** | O sistema deve mostrar um formulário de avaliação que deve conter, para cada critério, os campos Conceito, Nota e Observações, e o campo Assinatura do Membro da Banca. | Disponibiliza campo obrigatório para anexo de imagem de assinatura (PNG/JPG até 2 MB) ou reutilização em um clique da assinatura já cadastrada no perfil, registrando data/hora e replicando-a nos documentos finais. |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Upload obrigatório de arquivo PNG ou JPG (até 2 MB).
>
> 2\. Permite reaproveitar imagem já salva no perfil do usuário.

***Cenário 1: Upload de nova imagem de assinatura em formato PNG com
sucesso***

> **Dado que** o Avaliador concluiu o preenchimento de notas no
> formulário de avaliação,
>
> **Quando** anexa um arquivo no formato PNG com tamanho de 1,2 MB e
> clica em "Enviar avaliação assinada",
>
> **Então** o sistema aceita a imagem, registra a data e horário do
> envio e conclui a submissão com chancela visual.

***Cenário 2: Upload de nova imagem de assinatura em formato JPG com
sucesso***

> **Dado que** o Avaliador está na seção de assinatura do formulário,
>
> **Quando** anexa um arquivo no formato JPG com tamanho de 800 KB e
> confirma o envio,
>
> **Então** o sistema valida o arquivo, processa a imagem e salva a
> avaliação individual assinada.

***Cenário 3: Reaproveitamento da assinatura salva no perfil
institucional***

> **Dado que** o docente possui uma assinatura previamente cadastrada e
> salva em seu perfil institucional,
>
> **Quando** abre o formulário de avaliação com as notas preenchidas e
> mantém a assinatura do perfil vinculada,
>
> **Então** o sistema associa essa imagem à defesa sem exigir novo
> upload.

***Cenário 4: Atualização da assinatura do perfil a partir do envio da
avaliação***

> **Dado que** o Avaliador anexou uma nova assinatura na avaliação e
> marcou a caixa "Salvar esta imagem no meu perfil",
>
> **Quando** aciona o botão "Enviar avaliação assinada",
>
> **Então** o sistema associa a assinatura à defesa atual e atualiza
> simultaneamente a imagem de assinatura cadastrada no perfil do
> usuário.

***Cenário 5: Tentativa de upload com arquivo superior a 2 MB (E2)***

> **Dado que** o Avaliador está no campo de assinatura do formulário de
> avaliação,
>
> **Quando** tenta carregar um arquivo de imagem com 3,5 MB,
>
> **Então** o sistema bloqueia o carregamento e exibe mensagem de erro
> informando o limite máximo de 2 MB.

***Cenário 6: Tentativa de upload com formato não suportado - arquivo
PDF (E3)***

> **Dado que** o Avaliador tenta enviar a sua assinatura em formato PDF,
>
> **Quando** seleciona o arquivo no campo de upload,
>
> **Então** o sistema recusa o envio e informa que são aceitos apenas
> arquivos nos formatos PNG ou JPG.

***Cenário 7: Tentativa de upload com formato não suportado - arquivo
SVG ou BMP (E3)***

> **Dado que** o Avaliador tenta carregar um arquivo de imagem com
> extensão .svg ou .bmp,
>
> **Quando** anexa o arquivo,
>
> **Então** o sistema rejeita o documento e indica que o formato não é
> aceito.

***Cenário 8: Bloqueio de submissão da avaliação sem assinatura visual
vinculada (E4)***

> **Dado que** o Avaliador preencheu os 9 critérios oficiais de
> avaliação,
>
> **Quando** tenta finalizar a submissão deixando o campo de assinatura
> em branco e sem assinatura de perfil vinculada,
>
> **Então** o sistema bloqueia a submissão da avaliação e sinaliza que a
> assinatura visual é obrigatória para homologação das notas.

***Cenário 9: Substituição da imagem de assinatura antes da submissão
final***

> **Dado que** o Avaliador carregou uma imagem mas deseja trocá-la por
> outra mais nítida,
>
> **Quando** clica em "Atualizar imagem" e seleciona um novo arquivo
> válido no formato PNG,
>
> **Então** o sistema substitui a imagem anterior e exibe a nova prévia
> visual no formulário.

***Cenário 10: Membro Externo realizando upload de sua assinatura
visual***

> **Dado que** um Membro Externo compõe a banca examinadora e está
> avaliando o trabalho,
>
> **Quando** anexa seu arquivo JPG de assinatura com 500 KB e submete a
> avaliação,
>
> **Então** o sistema vincula a assinatura do membro externo aos
> registros da sessão.

***Cenário 11: Tentativa de envio de assinatura em sessão que não está
Em Andamento (E5)***

> **Dado que** a defesa encontra-se com status "Agendada",
>
> **Quando** o Avaliador abre o formulário de avaliação com
> antecedência,
>
> **Então** o sistema mantém o campo de assinatura desabilitado para
> envio final, permitindo apenas gravar as notas da Parte Escrita como
> rascunho.

***Cenário 12: Tentativa de acesso ao bloco de assinatura por docente
não integrante da banca (E6)***

> **Dado que** um docente autenticado não faz parte da banca examinadora
> daquele TCC,
>
> **Quando** tenta acessar o formulário de avaliação por URL direta,
>
> **Então** o sistema bloqueia a visualização e alerta que o acesso é
> restrito aos membros avaliadores da banca.

***Cenário 13: Acesso sem autenticação redirecionando para a tela de
login (E1)***

> **Dado que** o Avaliador não possui uma sessão ativa no sistema,
>
> **Quando** tenta abrir a tela de avaliação da defesa,
>
> **Então** o sistema redireciona para a tela de login (US-11) e, após a
> autenticação bem-sucedida, exibe o formulário de avaliação.

***Cenário 14: Registro de carimbo de data e hora junto à assinatura
enviada***

> **Dado que** o Avaliador concluiu o envio da avaliação assinada com
> sucesso,
>
> **Quando** a operação é persistida no banco de dados,
>
> **Então** o sistema registra a data e horário exatos da aposição da
> assinatura para auditoria formal e posterior inserção na Ata Final.

**Tela no protótipo**

**Tela:** Avaliação (Assinatura do Membro da Banca)



**Diagrama de sequência**

**Diagrama relacionado:** \[nome do diagrama ou "sem diagrama próprio" e
o motivo\]

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[X\] Descrição no formato Como, Quero, Para que
>
> \[X\] Requisitos da matriz conferidos
>
> \[X\] Fluxo principal e fluxos alternativos escritos
>
> \[X\] Atores, pré-condições e pós-condições preenchidos
>
> \[X\] Fluxos de exceção escritos
>
> \[X\] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-27 Liberar o resultado final

| **Épico:**                | Gestão da Defesa                                                                                               |
|---------------------------|----------------------------------------------------------------------------------------------------------------|
| **Feature:**              | Avaliação e Resultados                                                                                         |
| **Requisitos da matriz:** | RBN-DEF-06.1, RBN-DEF-06.2, RBN-DEF-06.3, RBN-DEF-06.4, RBN-DEF-06.5, RBN-DEF-06.6, RBN-DEF-06.7, RBN-DEF-06.8 |
| **Prioridade (MoSCoW):**  | Must Have                                                                                                      |
| **Responsável:**          | Célio Benjamim                                                                                                 |

**Descrição**

Como Orientador (Presidente da banca examinadora), quero apurar as notas
individuais dos avaliadores, definir o parecer da banca e liberar o
resultado final da defesa, para que a avaliação acadêmica seja
oficializada, os documentos formais sejam emitidos e o estudante tenha
acesso ao resultado e aos prazos subsequentes.

**Atores**

> **Ator principal:** Orientador do TCC (Presidente da banca
> examinadora, responsável por conduzir a deliberação, registrar o
> parecer e liberar o resultado final).
>
> **Atores secundários:** Membros titulares da banca (1º Avaliador, 2º
> Avaliador e Suplente ativado, que enviam suas notas e participam da
> deliberação), Aluno do TCC (cujo resultado é homologado e
> disponibilizado) e Secretaria do curso (notificada do encerramento da
> defesa para os registros acadêmicos).

**Pré-condições**

- O Orientador está autenticado no sistema, com o Status da Conta Ativa
  > (US-11). Sem sessão ativa, aplica-se o E1.

- A sessão de defesa encontra-se com o status "Em Andamento" (US-24).

- Todos os 3 membros da banca examinadora (Orientador, 1º Avaliador e 2º
  > Avaliador, ou o suplente ativado oficialmente na US-23) submeteram
  > as suas avaliações completas com notas nos 9 critérios e assinatura
  > visual vinculada (US-25 e US-26). Sem os 3 envios concluídos,
  > aplica-se o E2.

- O TCC está vinculado a uma turma ativa de TCC 1 ou TCC 2.

**Fluxo principal**

1.  No menu lateral do sistema (em "Minhas bancas" ou "Defesas"), o
    > Orientador acessa a tela da sessão de defesa em andamento
    > (RBN-DEF-01.2).

2.  O sistema exibe o painel de deliberação da banca indicando o status
    > de envio da avaliação de cada um dos 3 membros titulares
    > (Orientador, 1º Avaliador e 2º Avaliador).

3.  O sistema registra a submissão assinada do último avaliador pendente
    > (conforme US-25 e US-26).

4.  O sistema calcula a nota individual de cada membro multiplicando a
    > nota de cada critério pelo seu peso, dividindo por 10 e somando os
    > resultados, gerando a nota do avaliador com uma casa decimal por
    > arredondamento comercial (RBN-DEF-06.1).

5.  O sistema calcula a nota final do TCC pela média aritmética simples
    > das 3 notas individuais arredondadas dos membros, aplicando uma
    > casa decimal com arredondamento comercial (RBN-DEF-06.2).

6.  O sistema confere se há artigo científico Qualis A ou B homologado
    > pela Coordenação para o trabalho (RBN-CAD-12.3); havendo, aplica a
    > regra de nota mínima e ajusta a nota final para o maior valor
    > entre 6,0 e a média calculada.

7.  O Orientador visualiza a nota final apurada e define o parecer da
    > banca conforme a nota e a disciplina do TCC (RBN-DEF-06.3; E3 e
    > E4):

- Em TCC 1 com nota final ≥ 6,0: o sistema define e fixa automaticamente
  > o parecer como "Aprovado para TCC 2";

- Em TCC 2 com nota final ≥ 6,0: o Orientador seleciona o parecer na
  > lista suspensa entre "Aprovado" ou "Aprovado com Correções";

- Em TCC 1 ou TCC 2 com nota final \< 6,0: o sistema define e fixa
  > compulsoriamente o parecer como "Reprovado" (E3).

8.  O Orientador clica no botão "Liberar Resultado" (RBN-DEF-06.4).

9.  O sistema bloqueia definitivamente a edição e o reenvio de notas e
    > conceitos por parte de todos os membros da banca examinadora (E6).

10. O sistema altera o status da sessão de defesa automaticamente para
    > "Realizada" (RBN-DEF-01.2).

11. O sistema atualiza o Status do TCC na base de dados conforme o
    > parecer homologado (Aprovado para TCC 2, Aprovado, Aprovado com
    > Correções ou Reprovado) e grava a transição com autor, data, hora
    > e gatilho no histórico (RBN-CAD-08.3; US-14).

12. O sistema dispara a geração da Ata Final e da Folha de Aprovação
    > assinadas em PDF (US-28).

13. O sistema disponibiliza na área do Aluno, em tela somente leitura, a
    > nota final, o parecer homologado e, em caso de TCC 2 com
    > correções, a Data Limite da entrega do tipo Versão Final
    > (RBN-DEF-06.5). O fluxo termina.

**Fluxos alternativos**

1.  Reajuste consensual de notas durante a deliberação verbal (DEF-06.1;
    > passos 2 a 7): Durante a deliberação da banca perante a sessão
    > ("Em Andamento") e antes do clique em "Liberar Resultado",
    > qualquer membro da banca (Orientador ou avaliadores) clica no
    > botão "Reabrir minha avaliação" (US-25), retifica conceitos, notas
    > ou observações e reenvia com a sua assinatura visual. O sistema
    > recalcula de imediato a nota individual do membro, a média final e
    > o parecer preliminar. O fluxo prossegue a partir do passo 4.

2.  Aplicação de aproveitamento de artigo científico Qualis A ou B
    > (DEF-06.2; passo 6): Se a média simples apurada das notas da banca
    > resultar em valor inferior a 6,0 (ex.: 5,4), mas o trabalho possui
    > artigo científico Qualis A ou B homologado pela Coordenação de
    > Curso (US-20), o sistema eleva compulsoriamente a nota final para
    > 6,0. O fluxo prossegue a partir do passo 7.

3.  Aprovação direta em TCC 2 sem correções (DEF-06.3; passo 7): Em
    > sessão de TCC 2 com nota final ≥ 6,0, a banca conclui que o texto
    > não requer alterações. O Orientador seleciona a opção "Aprovado"
    > na lista suspensa do parecer e clica em "Liberar Resultado". O
    > Status do TCC passa para "Aprovado" e a Folha de Aprovação
    > assinada é liberada de imediato ao aluno para o encerramento do
    > trabalho (US-28). O fluxo prossegue a partir do passo 8.

4.  Sigilo de notas e deliberação reservada (DEF-06.8; passos 2 a 7):
    > Antes do acionamento de "Liberar Resultado", cada avaliador
    > visualiza exclusivamente a sua própria avaliação e os indicadores
    > de status dos colegas ("não avaliou", "rascunho salvo" ou
    > "enviada"), e o Aluno não possui acesso a nenhuma nota ou cálculo.
    > O Orientador visualiza a nota final apenas após a conclusão dos 3
    > envios. As notas completas por critério e por membro só se tornam
    > visíveis para todos após o passo 8. O fluxo prossegue a partir do
    > passo 8.

5.  Defesa avaliada com atuação de Suplente (passo 3): Caso um titular
    > tenha sido substituído pelo suplente durante a sessão (US-23), o
    > sistema utiliza a avaliação assinada submetida pelo suplente no
    > cálculo da média, descartando os registros do membro ausente. O
    > fluxo prossegue a partir do passo 4.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): Caso o Orientador tente acessar
> a tela da sessão ou acionar a liberação sem sessão ativa no navegador,
> o sistema exibe a tela de login (US-11). Após a autenticação,
> direciona para a sessão de defesa e o fluxo prossegue a partir do
> passo 2. Em caso de falha na autenticação, aplicam-se as exceções da
> US-11.
>
> E2. Bloqueio por avaliações ou assinaturas pendentes (passo 2):
> Enquanto qualquer membro da banca examinadora não submeter o
> formulário completo de avaliação com a respectiva assinatura visual
> (US-25 e US-26), o sistema não calcula a nota final, mantém o botão
> "Liberar Resultado" desabilitado e destaca ao Orientador quais
> avaliadores estão com status pendente (RBN-DEF-06.6). O fluxo de
> liberação fica interrompido. Retorna ao passo 2.
>
> E3. Reprovação por nota final inferior a 6,0 (passo 7): Se a nota
> final apurada for menor que 6,0 (e sem artigo Qualis A/B homologado),
> o sistema fixa o parecer exclusivamente como "Reprovado",
> desabilitando opções de aprovação (RBN-DEF-06.3 e RBN-DEF-06.7). Ao
> acionar "Liberar Resultado", o Status do TCC passa compulsoriamente a
> Reprovado, a Folha de Aprovação não é gerada e o Aluno tem seu acesso
> convertido para modo somente consulta (RBN-CAD-08.5). O fluxo
> encerra-se no passo 13.
>
> E4. Parecer não selecionado em TCC 2 (passo 7): Em sessão de TCC 2 com
> nota final ≥ 6,0, se o Orientador tentar acionar o botão "Liberar
> Resultado" sem ter selecionado entre "Aprovado" ou "Aprovado com
> Correções" na lista suspensa, o sistema impede a finalização, destaca
> o campo obrigatório e exibe: "Selecione o parecer da banca para
> continuar". Retorna ao passo 7.
>
> E5. Tentativa de liberação por usuário que não seja o Orientador
> (passo 8): Se um avaliador titular, suplente, aluno ou outro docente
> tentar disparar a ação de liberação de resultado, o sistema não
> disponibiliza o botão e bloqueia a requisição, exibindo: "Apenas o
> Orientador (Presidente da banca) pode liberar o resultado da defesa"
> (RBN-DEF-06.4). O fluxo termina.
>
> E6. Tentativa de alteração de notas após liberação do resultado (passo
> 9): Após o Orientador clicar em "Liberar Resultado", o sistema
> bloqueia em definitivo a reabertura de avaliações e não aceita novos
> lançamentos de notas, tornando todos os registros imutáveis
> (RBN-DEF-06.4). O fluxo termina.

**Pós-condições**

- As notas individuais dos 3 membros da banca examinadora e a nota final
  > do TCC foram calculadas e congeladas no banco de dados.

- O status da sessão de defesa foi alterado de "Em Andamento" para
  > "Realizada" (RBN-DEF-01.2).

- O Status do TCC foi atualizado na base de dados conforme o parecer
  > homologado (Aprovado para TCC 2, Aprovado, Aprovado com Correções ou
  > Reprovado) e registrado no histórico acadêmico com autor, data e
  > hora (US-14).

- A Ata Final em PDF e, nos casos de TCC 2 aprovado, a Folha de
  > Aprovação em PDF foram geradas assinadas para download imediato
  > (US-28).

- O Aluno passou a visualizar a nota final e o parecer oficial, bem como
  > a Data Limite da entrega da Versão Final (em TCC 2 com correções).

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                               | **Resumo da regra em uma frase**                                                                                                                                                                         |
|--------------|---------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **DEF-06.1** | O sistema deve calcular a nota de cada avaliador.                                     | Calcula a nota individual com uma casa decimal e arredondamento comercial pela média ponderada dos 9 critérios após o envio com assinatura, permitindo reenvio até a liberação.                          |
| **DEF-06.2** | O sistema deve calcular a nota final.                                                 | Calcula a média aritmética simples das notas arredondadas dos 3 membros com uma casa decimal, garantindo nota mínima 6,0 caso haja artigo Qualis A ou B homologado.                                      |
| **DEF-06.3** | O sistema deve permitir que o Orientador registre o parecer da banca.                 | Atribui parecer automático de Reprovado (nota \< 6,0) ou Aprovado para TCC 2 (em TCC 1 com nota ≥ 6,0), e exige seleção em lista suspensa entre Aprovado ou Aprovado com Correções em TCC 2.             |
| **DEF-06.4** | O sistema deve permitir que o Orientador libere o resultado da defesa.                | Disponibiliza botão de liberação após a conclusão dos 3 envios e definição do parecer, bloqueando a edição de notas, gerando a Ata/Folha, mudando a sessão para Realizada e atualizando o Status do TCC. |
| **DEF-06.5** | O sistema deve exibir ao Aluno a nota final e o parecer.                              | Disponibiliza ao aluno tela somente leitura com a nota final, o parecer homologado e, no caso de TCC 2 com correções, a data limite para entrega da versão final.                                        |
| **DEF-06.6** | \[Exceção\] O sistema deve impedir o cálculo com notas pendentes.                     | Bloqueia a apuração da nota final e desabilita a liberação do resultado enquanto houver avaliação ou assinatura pendente de qualquer um dos 3 membros da banca titular.                                  |
| **DEF-06.7** | \[Exceção\] O sistema deve tratar a reprovação na banca.                              | Atualiza o Status do TCC para Reprovado quando a nota for inferior a 6,0, restringindo o acesso do estudante ao sistema exclusivamente em modo de consulta.                                              |
| **DEF-06.8** | \[Exceção\] O sistema deve ocultar as notas individuais até a liberação do resultado. | Mantém o sigilo das notas individuais entre os próprios avaliadores e para o aluno durante a deliberação, exibindo-as apenas após a liberação formal do resultado pelo orientador.                       |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Média gerada com exatidão matemática (1 casa decimal).
>
> 2\. Bloqueio do cálculo se faltar o envio de algum avaliador.
>
> 3\. Define o parecer automaticamente se a nota for \< 6,0.

***Cenário 1: Liberação de resultado com aprovação com correções em TCC
2***

> **Dado que** os 3 membros da banca enviaram as avaliações completas e
> assinadas de uma defesa de TCC 2,
>
> **E** as notas individuais foram calculadas em 8,0, 8,5 e 9,0 (média
> final 8,5),
>
> **Quando** o Orientador seleciona o parecer "Aprovado com Correções" e
> clica em "Liberar Resultado",
>
> **Então** o sistema bloqueia as notas em definitivo,
>
> **E** altera o status da sessão para "Realizada",
>
> **E** atualiza o Status do TCC para "Aprovado com Correções",
>
> **E** disponibiliza a nota 8,5, o parecer e a Data Limite da entrega
> da Versão Final no painel do Aluno.

***Cenário 2: Liberação de resultado com aprovação direta em TCC 2 sem
correções***

> **Dado que** as notas da banca de TCC 2 resultaram na média final 9,2
> sem necessidade de ajustes,
>
> **Quando** o Orientador seleciona o parecer "Aprovado" na lista
> suspensa e clica em "Liberar Resultado",
>
> **Então** o sistema homologa o resultado,
>
> **E** atualiza o Status do TCC para "Aprovado",
>
> **E** dispara a geração da Ata Final e da Folha de Aprovação assinadas
> para download imediato pelo Aluno (US-28).

***Cenário 3: Liberação de resultado em TCC 1 com parecer automático
"Aprovado para TCC 2"***

> **Dado que** a defesa realizada pertence a uma turma de TCC 1 e todos
> os 3 avaliadores enviaram as notas,
>
> **Quando** o sistema apura a média aritmética das notas igual a 7,2,
>
> **Então** o sistema define automaticamente o parecer como "Aprovado
> para TCC 2" sem exigir seleção em lista suspensa,
>
> **E** ao clicar em "Liberar Resultado", oficializa a transição do
> trabalho para apto à continuidade em TCC 2.

***Cenário 4: Arredondamento comercial da nota individual do avaliador
(RBN-DEF-06.1)***

> **Dado que** a soma ponderada dos 9 critérios preenchidos por um
> avaliador resultou exatamente em 8,45,
>
> **Quando** o sistema processa a nota individual desse avaliador,
>
> **Então** a nota individual é arredondada comercialmente para cima,
> fixando o valor em 8,5.

***Cenário 5: Arredondamento comercial da nota final da banca
(RBN-DEF-06.2)***

> **Dado que** as notas individuais dos 3 membros da banca foram 7,3,
> 7,3 e 7,4 (soma 22,0 e média 7,333...),
>
> **Quando** o sistema calcula a nota final da defesa,
>
> **Então** a nota final é arredondada comercialmente para 7,3 com uma
> casa decimal.

***Cenário 6: Arredondamento comercial da nota final a partir de fração
0,05 para cima***

> **Dado que** as notas individuais dos 3 membros da banca foram 8,1,
> 8,2 e 8,4 (soma 24,7 e média 8,233...) e em outro caso resultou em
> média 8,25,
>
> **Quando** o sistema apura a média com fração igual ou superior a
> 0,05,
>
> **Então** o sistema arredonda a nota final para 8,3 com exatidão
> matemática.

***Cenário 7: Bloqueio de cálculo e liberação por avaliação pendente
(E2 - DEF-06.6)***

> **Dado que** o Orientador e o 1º Avaliador já submeteram suas fichas,
> mas o 2º Avaliador ainda não enviou sua avaliação,
>
> **Quando** o Orientador visualiza o painel de deliberação da defesa,
>
> **Então** o sistema não calcula a nota final,
>
> **E** mantém o botão "Liberar Resultado" desabilitado,
>
> **E** destaca visualmente que a avaliação do 2º Avaliador está
> pendente.

***Cenário 8: Bloqueio de cálculo por pendência de assinatura visual de
membro da banca***

> **Dado que** os avaliadores preencheram as notas dos critérios, mas um
> dos membros não anexou nem selecionou a assinatura visual (US-26),
>
> **Quando** o Orientador consulta o painel da sessão,
>
> **Então** o sistema considera a avaliação daquele membro incompleta e
> bloqueia o cálculo da média final e a liberação do resultado.

***Cenário 9: Reprovação automática por nota inferior a 6,0 em TCC 1
(E3 - DEF-06.7)***

> **Dado que** a média ponderada dos 3 membros da banca em uma defesa de
> TCC 1 resultou em 5,2 e não há artigo científico Qualis A/B
> homologado,
>
> **Quando** o Orientador consolida as notas no painel,
>
> **Então** o sistema define compulsoriamente o parecer como
> "Reprovado",
>
> **E** ao acionar "Liberar Resultado", atualiza o Status do TCC para
> Reprovado e restringe o acesso do estudante exclusivamente para modo
> de consulta (RBN-CAD-08.5).

***Cenário 10: Reprovação automática por nota inferior a 6,0 em TCC 2
(E3 - DEF-06.7)***

> **Dado que** a média da banca em uma defesa de TCC 2 resultou em 4,8
> sem artigo Qualis A/B homologado,
>
> **Quando** o Orientador abre a deliberação,
>
> **Então** a lista suspensa de parecer é substituída pelo texto fixo
> "Reprovado",
>
> **E** a liberação registra o Status do TCC como Reprovado e impede a
> emissão da Folha de Aprovação (US-28).

***Cenário 11: Aplicação da nota mínima de 6,0 por artigo científico
Qualis A ou B homologado (DEF-06.2)***

> **Dado que** a média apurada da banca examinadora foi 5,6, mas o
> estudante possui artigo Qualis B homologado pelo Coordenador de Curso
> (US-20),
>
> **Quando** o sistema processa a nota final na deliberação,
>
> **Então** a nota final do TCC é automaticamente ajustada para 6,0,
>
> **E** o trabalho fica formalmente apto a receber parecer aprovatório.

***Cenário 12: Artigo com Qualis C homologado não altera nota inferior a
6,0***

> **Dado que** o estudante possui artigo homologado com estrato Qualis C
> e a média apurada da banca resultou em 5,4,
>
> **Quando** o sistema processa o cálculo da nota final,
>
> **Então** a nota final permanece fixada em 5,4 (sem garantia de nota
> mínima) e o parecer é estabelecido como Reprovado.

***Cenário 13: Reajuste consensual de notas por avaliador durante a
deliberação (Fluxo Alternativo A)***

> **Dado que** todos os 3 avaliadores haviam enviado notas preliminares,
>
> **Quando** a banca delibera verbalmente e a 1ª Avaliadora reabre sua
> avaliação, altera a nota de Metodologia e reenvia a ficha assinada,
>
> **Então** o sistema recalcula de imediato a nota individual da 1ª
> Avaliadora e atualiza a média final no painel do Orientador antes da
> liberação.

***Cenário 14: Sigilo absoluto das notas individuais entre os
avaliadores antes da homologação (DEF-06.8)***

> **Dado que** a defesa está "Em Andamento" e o 1º Avaliador já submeteu
> a sua nota,
>
> **Quando** o 2º Avaliador acessa o sistema para preencher ou
> visualizar a sessão antes da deliberação final,
>
> **Então** o sistema não exibe as notas do 1º Avaliador, apresentando
> unicamente o indicador de que a avaliação foi "enviada".

***Cenário 15: Sigilo absoluto das notas e do parecer para o Aluno antes
da liberação (DEF-06.8)***

> **Dado que** as avaliações individuais já foram enviadas pelos membros
> da banca mas o Orientador ainda não clicou em "Liberar Resultado",
>
> **Quando** o Aluno acessa a aba do seu trabalho no sistema,
>
> **Então** o sistema oculta a nota final, as notas parciais e o
> parecer, exibindo apenas que a defesa está em andamento.

***Cenário 16: Bloqueio por parecer não selecionado em TCC 2 com nota
aprovatória (E4)***

> **Dado que** a defesa de TCC 2 obteve média final 8,8,
>
> **Quando** o Orientador clica em "Liberar Resultado" mantendo a lista
> suspensa de parecer com a opção padrão "Selecione...",
>
> **Então** o sistema bloqueia a liberação, mantém a sessão "Em
> Andamento" e alerta que a escolha entre Aprovado ou Aprovado com
> Correções é obrigatória.

***Cenário 17: Tentativa de liberação por usuário sem perfil de
Orientador (E5)***

> **Dado que** um docente que atua apenas como 1º Avaliador da banca
> está autenticado na sessão,
>
> **Quando** visualiza o painel de deliberação da defesa,
>
> **Então** o sistema não disponibiliza o botão "Liberar Resultado",
> reservando a ação exclusivamente ao Orientador do trabalho.

***Cenário 18: Bloqueio definitivo de edição e integridade pós-liberação
(E6)***

> **Dado que** o Orientador liberou o resultado e o status da sessão
> transicionou para "Realizada",
>
> **Quando** qualquer membro da banca tenta reabrir a avaliação ou
> editar notas e conceitos,
>
> **Então** o sistema bloqueia qualquer alteração e exibe as fichas e
> cálculos em modo somente leitura.

**Tela no protótipo**

**Tela:** Sessão de defesa



**Diagrama de sequência**

**Diagrama relacionado:** \[nome do diagrama ou "sem diagrama próprio" e
o motivo\]

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[X\] Descrição no formato Como, Quero, Para que
>
> \[X\] Requisitos da matriz conferidos
>
> \[X\] Fluxo principal e fluxos alternativos escritos
>
> \[X\] Atores, pré-condições e pós-condições preenchidos
>
> \[X\] Fluxos de exceção escritos
>
> \[X\] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-28 Gerar a Ata Final e a Folha de Aprovação

| **Épico:**                | Gestão da Defesa                         |
|---------------------------|------------------------------------------|
| **Feature:**              | Documentação e Encerramento              |
| **Requisitos da matriz:** | RBN-DEF-07.1, RBN-DEF-07.2, RBN-DEF-07.3 |
| **Prioridade (MoSCoW):**  | Must Have                                |
| **Responsável:**          | Célio Benjamim                           |

**Descrição**

Como Orientador, Aluno ou Secretaria, quero dispor da Ata Final e da
Folha de Aprovação geradas e assinadas em PDF logo após a liberação do
resultado da defesa, para que a avaliação acadêmica tenha validade
formal e o estudante possa fazer download os documentos para compor a
Versão Final e o dossiê da biblioteca.

**Atores**

> **Ator principal:** Orientador (ao liberar o resultado na US-27,
> dispara a geração automática dos documentos) e Aluno, Professor da
> Disciplina ou Secretaria (que consultam e baixam dos arquivos em PDF
> na US-28).
>
> **Atores secundários:** Coordenador de Curso (cuja assinatura visual
> cadastrada no perfil institucional é inserida na Ata Final) e Membros
> da Banca Examinadora (cujas assinaturas visuais enviadas na avaliação
> são replicadas nos documentos).

**Pré-condições**

- O Orientador concluiu a deliberação da banca e acionou o botão
  > "Liberar Resultado" na tela da sessão de defesa (US-27).

- O status da sessão de defesa foi atualizado para "Realizada" (US-24) e
  > o Status do TCC foi homologado conforme o parecer (US-14 e US-27).

- As imagens de assinatura dos 3 membros da banca examinadora foram
  > validadas e vinculadas durante o envio da avaliação (US-25 e US-26).

- O Coordenador de Curso do NUCOMP possui imagem de assinatura
  > cadastrada e homologada no seu perfil de usuário (US-38 e
  > RBN-CAD-13.1). Sem assinatura no perfil, aplica-se o E2.

- Para acessar o download, o Aluno, Membro da Banca, Professor da
  > Disciplina ou Secretaria deve estar autenticado no sistema com
  > Status da Conta Ativa (US-11). Sem sessão ativa, aplica-se o E1.

**Fluxo principal**

1.  O Orientador conclui a deliberação e aciona o comando "Liberar
    > Resultado" no painel da banca examinadora (passo 8 da US-27).

2.  O sistema recupera os dados acadêmicos do TCC (título do trabalho,
    > nome do estudante, curso, modalidade e data da defesa), as notas
    > individuais apuradas dos 3 avaliadores, a média final calculada e
    > o parecer homologado (RBN-DEF-06.4).

3.  O sistema recupera as imagens das assinaturas dos 3 examinadores da
    > banca (enviadas na avaliação, US-26) e a imagem da assinatura
    > cadastrada no perfil do Coordenador de Curso do NUCOMP
    > (RBN-CAD-13.1).

4.  O sistema gera a Ata Final em formato PDF não editável com cabeçalho
    > oficial UEA/EST, nome do curso, identificação dos membros da banca
    > com titulações e papéis, notas individuais, nota final, parecer,
    > menção a artigo Qualis (se aplicável), data da defesa, assinaturas
    > dos 3 examinadores e nome/assinatura do Coordenador de Curso
    > (RBN-DEF-07.1).

5.  O sistema verifica a disciplina da turma do trabalho e identifica
    > que se trata de uma turma de TCC 2 com parecer aprovatório
    > (Aprovado ou Aprovado com Correções) (RBN-DEF-07.2).

6.  O sistema gera a Folha de Aprovação em PDF não editável contendo o
    > cabeçalho institucional UEA/EST, título do trabalho, nome do
    > estudante, termo formal de aprovação da banca, data ("Manaus, DD
    > de mês de AAAA") e assinaturas dos 3 examinadores, omitindo todas
    > as notas e médias numéricas (RBN-DEF-07.2).

7.  O sistema armazena os arquivos PDF e disponibiliza de imediato os
    > botões de ação "Ata Final (PDF)" e "Folha de Aprovação (PDF)" nos
    > detalhes da defesa para a banca examinadora, Professor da
    > Disciplina e Secretaria (RBN-DEF-07.3).

8.  O sistema disponibiliza de imediato os botões de download da "Ata
    > Final" e da "Folha de Aprovação" na aba Meu TCC para o Aluno,
    > permitindo que este utilize a folha assinada para estruturar a
    > Versão Final (RBN-DEF-07.3).

9.  O Aluno, Orientador, Professor da Disciplina ou Secretaria clica no
    > botão correspondente ao documento pretendido e o sistema executa o
    > download o arquivo PDF assinado. O fluxo termina.

**Fluxos alternativos**

1.  Defesa em turma de TCC 1 (RBN-DEF-07.2; passo 5): Se a defesa
    > pertencer a uma turma da disciplina TCC 1, o sistema identifica a
    > etapa letiva e gera unicamente a Ata Final em PDF (com título "Ata
    > Final de Avaliação de Trabalho de Conclusão de Curso I"); a
    > geração da Folha de Aprovação é suprimida pelo sistema. O sistema
    > disponibiliza apenas o botão "Ata Final (PDF)" para consulta e
    > download. O fluxo prossegue a partir do passo 7.

2.  Trabalho com parecer Reprovado na banca (RBN-DEF-06.7 e
    > RBN-DEF-07.2; passo 5): Se a nota final for inferior a 6,0 e o
    > parecer registrado for "Reprovado", o sistema gera exclusivamente
    > a Ata Final registrando formalmente a reprovação; a Folha de
    > Aprovação não é gerada. O sistema disponibiliza apenas o download
    > da Ata Final. O fluxo prossegue a partir do passo 7.

3.  Folha de Aprovação no parecer Aprovado com Correções (RBN-DEF-07.3;
    > passo 8): Quando o parecer da banca em TCC 2 for "Aprovado com
    > Correções", o sistema disponibiliza o botão da Folha de Aprovação
    > ao Aluno logo na liberação do resultado, para que o estudante
    > possa compor o PDF unificado da Versão Final corrigida (US-29); a
    > conferência das correções requeridas pela banca é efetuada
    > posteriormente pelo Professor da Disciplina no fluxo de
    > homologação da Versão Final (US-44). O fluxo prossegue a partir do
    > passo 9.

4.  Defesa avaliada com atuação de membro suplente (RBN-DEF-02.2 e
    > RBN-DEF-07.1; passos 3 e 4): Se um avaliador titular foi
    > substituído pelo Suplente durante a sessão (US-23), o sistema
    > recupera o nome, titulação e imagem de assinatura do Suplente e
    > monta a Ata Final e a Folha de Aprovação com os dados do Suplente
    > na linha do avaliador titular substituído. O fluxo prossegue a
    > partir do passo 4.

5.  Bonificação de artigo Qualis A ou B aplicada na nota final
    > (RBN-DEF-06.2 e RBN-DEF-07.1; passo 4): Caso a nota final tenha
    > sido fixada no limite mínimo de 6,0 em decorrência de artigo
    > científico homologado pela Coordenação (US-20), o sistema insere
    > compulsoriamente na Ata Final a observação: *"Em caso de artigos,
    > se Qualis A ou B, a nota final será o valor máximo entre 6,0 e a
    > média dos avaliadores"*. O fluxo prossegue a partir do passo 5.

6.  Download posterior via menu Defesas ou Minhas Bancas (passo 9): A
    > qualquer momento após a conclusão da sessão, os membros da banca
    > examinadora (pelo menu Minhas bancas), o Aluno (pela aba Meu TCC),
    > o Professor da Disciplina (pela aba Turmas) ou a Secretaria (pela
    > lista de Defesas) podem acessar a sessão realizada e baixar os
    > PDFs arquivados. O fluxo termina.

**Fluxos de exceção**

> E1. Usuário não autenticado no download (passo 9): Caso o Aluno,
> Membro da Banca, Professor da Disciplina ou Secretaria tente acessar
> ao endereço direto de download de um documento sem uma sessão ativa, o
> sistema apresenta a tela de login (US-11). Após a autenticação,
> direciona para o arquivo solicitado e inicia a transferência. Em caso
> de falha na autenticação, aplicam-se as exceções da US-11.
>
> E2. Ausência de imagem de assinatura do Coordenador de Curso (passo
> 3): Se o Coordenador de Curso do NUCOMP não tiver cadastrado a imagem
> de sua assinatura no seu perfil institucional (US-38 e RBN-CAD-13.1),
> o sistema bloqueia a finalização da geração da Ata Final, alerta o
> Orientador com a mensagem: *"Não foi possível gerar a Ata Final: o
> Coordenador de Curso não possui assinatura cadastrada no perfil"* e
> emite notificação à Coordenação para regularização cadastral imediata.
> Retorna ao painel da banca.
>
> E3. Falha de processamento na renderização do PDF (passos 4 ou 6):
> Caso ocorra indisponibilidade de serviço ou falha na conversão de
> documentos na camada de aplicação, o sistema não gera arquivos
> corrompidos, registra a falha nos logs e exibe: *"Erro ao gerar os
> documentos da defesa. Tente realizar o download novamente em
> instantes"*. Retorna ao passo 7.
>
> E4. Tentativa de download de Folha de Aprovação em TCC 1 (passo 9):
> Caso um usuário tente acessar o download de Folha de Aprovação para um
> trabalho pertencente a uma turma de TCC 1, o sistema bloqueia a
> requisição e exibe: *"A Folha de Aprovação não se aplica ao TCC 1"*. O
> fluxo termina.
>
> E5. Tentativa de baixar de Folha de Aprovação de TCC reprovado (passo
> 9): Caso um usuário tente acessar a Folha de Aprovação de um trabalho
> com parecer Reprovado, o sistema bloqueia o download e informa:
> *"Documento indisponível para trabalhos reprovados"*. O fluxo termina.
>
> E6. Usuário sem permissão de acesso à defesa (passo 9): Se um docente
> que não integra a banca examinadora nem é o Professor da Disciplina
> daquela turma tentar baixar a Ata Final ou a Folha de Aprovação
> daquele aluno, o sistema nega o acesso e exibe: *"Você não tem
> permissão para acessar os documentos desta defesa"*. O fluxo termina.

**Pós-condições**

- A Ata Final em formato PDF não editável foi montada, chancelada
  > visualmente com as assinaturas dos 3 examinadores da banca e do
  > Coordenador de Curso, e arquivada na base de dados do SIGTCC.

- Em turmas de TCC 2 com parecer aprovatório (Aprovado ou Aprovado com
  > Correções), a Folha de Aprovação em PDF não editável foi gerada com
  > a supressão de notas numéricas e arquivada.

- Os botões de download da Ata Final e da Folha de Aprovação foram
  > disponibilizados de imediato na tela da sessão para os membros da
  > banca examinadora, Professor da Disciplina e Secretaria.

- O Aluno passou a dispor do download imediato da Ata Final e da Folha
  > de Aprovação no seu painel, ficando apto a anexar a folha no arquivo
  > único da Versão Final (US-29).

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                            | **Resumo da regra em uma frase**                                                                                                                                                                                                                 |
|--------------|------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **DEF-07.1** | O sistema deve gerar a Ata Final assinada em PDF.                                  | Gera automaticamente documento PDF não editável com cabeçalho oficial, notas individuais, média final, parecer, menção a Qualis (se aplicável), data da defesa, assinaturas dos três membros da banca e nome/assinatura do Coordenador de Curso. |
| **DEF-07.2** | O sistema deve gerar a Folha de Aprovação assinada em PDF.                         | Gera automaticamente documento PDF não editável exclusivo para TCC 2 aprovado (com ou sem correções), contendo dados do trabalho, termo formal de aprovação e assinaturas da banca com omissão total de notas.                                   |
| **DEF-07.3** | O sistema deve permitir o download da Ata Final e da Folha de Aprovação assinadas. | Download da Ata Final e da Folha de Aprovação; o Aluno recebe a Folha na liberação do resultado, também no Aprovado com Correções.                                                                                                               |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. PDFs gerados automaticamente após a liberação da nota.
>
> 2\. Imagens das assinaturas dos 3 membros da banca nos documentos e,
> na Ata Final, nome e assinatura do Coordenador de Curso.
>
> 3\. Folha de Aprovação gerada apenas para TCC 2 e disponível ao aluno
> na liberação.

***Cenário 1: Geração completa da Ata e Folha de Aprovação em TCC 2 com
parecer Aprovado***

> **Dado que** uma defesa de TCC 2 foi avaliada e obteve o parecer
> "Aprovado",
>
> **Quando** o Orientador aciona o comando "Liberar Resultado" no painel
> da banca,
>
> **Então** o sistema gera automaticamente os arquivos PDF não editáveis
> da Ata Final e da Folha de Aprovação,
>
> **E** insere as imagens de assinatura dos 3 avaliadores em ambos os
> documentos,
>
> **E** insere o nome e assinatura do Coordenador de Curso na Ata Final,
>
> **E** disponibiliza de imediato o download de ambos os documentos para
> o Aluno, banca examinadora, Professor da Disciplina e Secretaria.

***Cenário 2: Disponibilização imediata da Folha de Aprovação no parecer
Aprovado com Correções***

> **Dado que** o estudante de TCC 2 obteve média 7,8 com parecer
> "Aprovado com Correções",
>
> **Quando** o Orientador libera o resultado final da sessão,
>
> **Então** o sistema disponibiliza de imediato na aba Meu TCC o
> download da Ata Final e da Folha de Aprovação assinada,
>
> **E** permite ao Aluno baixar a folha para montar o PDF único da
> Versão Final antes da entrega (US-29).

***Cenário 3: Geração exclusiva da Ata Final em sessão de TCC 1***

> **Dado que** a defesa realizada pertence a uma turma de TCC 1 e o
> estudante obteve nota final 8,0 ("Aprovado para TCC 2"),
>
> **Quando** o Orientador libera o resultado da defesa,
>
> **Então** o sistema gera unicamente o arquivo PDF da Ata Final de TCC
> 1,
>
> **E** não gera a Folha de Aprovação para a referida sessão.

***Cenário 4: Não geração de Folha de Aprovação em caso de Reprovação***

> **Dado que** a banca examinadora apurou média final inferior a 6,0
> resultando em parecer "Reprovado" em TCC 2,
>
> **Quando** o Orientador homologa a liberação do resultado,
>
> **Então** o sistema emite unicamente a Ata Final com o registro de
> reprovação,
>
> **E** bloqueia compulsoriamente a emissão da Folha de Aprovação.

***Cenário 5: Omissão absoluta de notas numéricas na Folha de
Aprovação***

> **Dado que** a Folha de Aprovação de TCC 2 foi gerada pelo sistema,
>
> **Quando** o documento em PDF é aberto para visualização ou impressão,
>
> **Então** o texto exibe o título do trabalho, nome do estudante, termo
> de aprovação e assinaturas dos 3 membros,
>
> **E** não apresenta nenhum campo, menção ou valor de notas individuais
> ou média final da banca.

***Cenário 6: Imagens das assinaturas dos 3 membros da banca presentes
nos documentos***

> **Dado que** o Orientador, o 1º Avaliador e a 2ª Avaliadora enviaram
> suas assinaturas na avaliação (US-26),
>
> **Quando** os documentos em PDF são renderizados pelo sistema,
>
> **Então** a Ata Final e a Folha de Aprovação trazem posicionadas nos
> respectivos blocos as assinaturas digitalizadas dos 3 docentes.

***Cenário 7: Nome e imagem da assinatura do Coordenador de Curso na Ata
Final***

> **Dado que** o Coordenador de Curso possui imagem de assinatura
> cadastrada no seu perfil institucional,
>
> **Quando** o sistema gera a Ata Final da defesa,
>
> **Então** o rodapé do documento exibe o nome completo do Coordenador
> de Curso e estampa a imagem de sua assinatura visual.

***Cenário 8: Inclusão da menção formal a artigo Qualis A ou B na Ata
Final***

> **Dado que** a nota final da defesa foi fixada em 6,0 em decorrência
> de aproveitamento de artigo científico homologado (US-20),
>
> **Quando** o sistema gera a Ata Final em PDF,
>
> **Então** o documento insere obrigatoriamente a observação: "Em caso
> de artigos, se Qualis A ou B, a nota final será o valor máximo entre
> 6,0 e a média dos avaliadores".

***Cenário 9: Adequação dos signatários da banca quando há atuação de
Suplente***

> **Dado que** o 2º Avaliador foi substituído pelo Suplente durante a
> apresentação da defesa (US-23),
>
> **Quando** o sistema gera a Ata Final e a Folha de Aprovação,
>
> **Então** os documentos substituem o nome, titulação e assinatura do
> titular ausente pelos dados e assinatura do Suplente ativo.

***Cenário 10: Download dos documentos pela Secretaria do curso***

> **Dado que** a Secretaria do curso de Engenharia de Computação acessa
> à sessão de defesa realizada,
>
> **Quando** clica nos botões "Ata Final (PDF)" e "Folha de Aprovação
> (PDF)",
>
> **Então** o sistema executa o download dos dois documentos assinados
> para arquivo e trâmites acadêmicos.

***Cenário 11: Download dos documentos pelo Professor da Disciplina***

> **Dado que** o Professor da Disciplina consulta a turma de TCC 2 na
> aba Alunos,
>
> **Quando** abre os detalhes da defesa do aluno aprovado e aciona o
> botão de download,
>
> **Então** o sistema inicia a transferência dos arquivos PDF assinados.

***Cenário 12: Download dos documentos pelos avaliadores em Minhas
Bancas***

> **Dado que** um docente que atuou como 1º Avaliador acessa o menu
> Minhas bancas,
>
> **Quando** localiza a defesa realizada e clica no botão para baixar a
> Ata Final,
>
> **Então** o sistema transfere o documento assinado para visualização e
> comprovação das notas.

***Cenário 13: Bloqueio por ausência de assinatura no perfil do
Coordenador de Curso (E2)***

> **Dado que** o Coordenador de Curso do NUCOMP ainda não fez o upload
> de sua assinatura no perfil institucional,
>
> **Quando** o Orientador clica em "Liberar Resultado" na sessão de
> defesa,
>
> **Então** o sistema suspende a emissão da Ata Final, alerta o
> Orientador sobre a pendência do Coordenador e envia notificação à
> Coordenação para regularização.

***Cenário 14: Integridade do arquivo PDF não editável***

> **Dado que** a Ata Final e a Folha de Aprovação foram geradas pelo
> sistema,
>
> **Quando** o Aluno, Avaliador ou Secretaria tenta abrir ou alterar o
> conteúdo textual dos arquivos gerados,
>
> **Então** os documentos encontram-se estruturados em formato PDF
> estático e protegido contra edição de dados e notas.

***Cenário 15: Tentativa de baixar a Folha de Aprovação em TCC 1
bloqueada (E4)***

> **Dado que** uma defesa realizada pertence a uma turma de TCC 1,
>
> **Quando** o Aluno, Avaliador ou Secretaria tenta acessar diretamente
> ao endereço de download da Folha de Aprovação daquele trabalho,
>
> **Então** o sistema bloqueia a requisição e informa que a Folha de
> Aprovação não se aplica ao TCC 1.

***Cenário 16: Tentativa de baixar a Folha de Aprovação de TCC reprovado
bloqueada (E5)***

> **Dado que** um trabalho foi reprovado pela banca examinadora,
>
> **Quando** o Aluno, Avaliador ou Secretaria tenta acessar ao link da
> Folha de Aprovação dessa defesa,
>
> **Então** o sistema recusa a solicitação e informa que o documento não
> é gerado para trabalhos reprovados.

***Cenário 17: Bloqueio de download para docente sem vínculo com a
defesa (E6)***

> **Dado que** um docente autenticado não fez parte da banca examinadora
> nem é o Professor da Disciplina daquela turma,
>
> **Quando** tenta baixar os documentos oficiais da defesa pela URL
> direta,
>
> **Então** o sistema bloqueia o acesso e exibe a mensagem de permissão
> negada.

***Cenário 18: Acesso ao download sem autenticação redirecionando para
login (E1)***

> **Dado que** o usuário não possui uma sessão ativa no sistema,
>
> **Quando** tenta abrir o link direto de download da Ata Final ou da
> Folha de Aprovação,
>
> **Então** o sistema redireciona para a tela de login (US-11) e, após a
> autenticação bem-sucedida, realiza o download do documento.

**Tela no protótipo**

**Tela:** Sessão de defesa



**Diagrama de sequência**

**Diagrama relacionado:** \[nome do diagrama ou "sem diagrama próprio" e
o motivo\]

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[X\] Descrição no formato Como, Quero, Para que
>
> \[X\] Requisitos da matriz conferidos
>
> \[X\] Fluxo principal e fluxos alternativos escritos
>
> \[X\] Atores, pré-condições e pós-condições preenchidos
>
> \[X\] Fluxos de exceção escritos
>
> \[X\] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-30 Registrar ouvintes e gerar a agenda em PDF

| **Épico:**                | Gestão da Defesa                                                     |
|---------------------------|----------------------------------------------------------------------|
| **Feature:**              | Documentação e Encerramento                                          |
| **Requisitos da matriz:** | RBN-DEF-08.1, RBN-DEF-08.2, RBN-DEF-08.3, RBN-DEF-08.4, RBN-DEF-08.5 |
| **Prioridade (MoSCoW):**  | Should Have                                                          |
| **Responsável:**          | Célio Benjamim                                                       |

**Descrição**

Como Orientador, Professor da Disciplina, Coordenador de Curso ou
Secretaria, quero registrar a presença de alunos ouvintes, relatar
eventuais ocorrências da banca examinadora e gerar a agenda oficial de
defesas em PDF, para que a divulgação pública das sessões seja
viabilizada e a comprovação de horas complementares e participação em
bancas seja formalizada.

**Atores**

> **Ator principal:** Orientador (responsável pelo registro de ouvintes
> e pelo relato de ocorrências da sessão), Professor da Disciplina
> (responsável pelo registro e consulta de ouvintes de sua turma),
> Coordenador de Curso e Secretaria (responsáveis pela emissão da agenda
> pública de defesas em PDF e pela consulta consolidada das horas
> complementares).
>
> **Atores secundários:** Alunos ouvintes (estudantes presentes na
> apresentação que recebem o cômputo de 2 horas de atividades
> complementares), Membros titulares da banca examinadora (que recebem
> automaticamente a declaração de participação com código de validação
> institucional) e Aluno que defendeu o TCC.

**Pré-condições**

- O Orientador, Professor da Disciplina, Coordenador de Curso ou
  > Secretaria está autenticado no sistema, com o Status da Conta Ativa
  > (US-11). Sem sessão ativa, aplica-se o E1.

- Para o registro de alunos ouvintes, a sessão de defesa deve estar com
  > status "Em Andamento" ou "Realizada" (US-24). Em defesas agendadas
  > ou canceladas, aplica-se o E7.

- Para o relato de ocorrências da sessão, a defesa deve estar com status
  > "Em Andamento" e o resultado ainda não pode ter sido liberado pelo
  > Orientador (US-27). Com a sessão finalizada, aplica-se o E6.

- Para a emissão da agenda pública de defesas em PDF, devem existir
  > defesas com status "Agendada" ou "Reagendada" no período letivo ou
  > intervalo de datas filtrado (RBN-DEF-08.1).

- Para o envio automático da declaração de participação em banca, a
  > sessão de defesa deve ter atingido o status "Realizada" após a
  > homologação das notas na US-27.

**Fluxo principal**

1.  Na tela de Defesas (US-40) ou no Painel de orientandos (US-18), o
    > Orientador ou Professor da Disciplina localiza e abre a sessão de
    > defesa correspondente (com status "Em Andamento" ou "Realizada").

2.  O sistema exibe o modal de detalhes da sessão apresentando os botões
    > de ação "Ouvintes" e "Ocorrências".

3.  O Orientador ou Professor da Disciplina clica no botão "Ouvintes".

4.  O sistema abre a janela modal de registro de presença contendo a
    > listagem de ouvintes já adicionados, os campos Nome Completo e
    > Matrícula e os botões "Adicionar", "Cancelar" e "Salvar"
    > (RBN-DEF-08.2).

5.  O Orientador ou Professor da Disciplina clica em "+ Adicionar" e
    > informa o Nome Completo (até 150 caracteres, apenas letras,
    > acentos e espaços) e a Matrícula institucional (exatamente 10
    > dígitos numéricos) do estudante presente como ouvinte (E2 a E4).

6.  O Orientador ou Professor da Disciplina repete o passo 5 para cada
    > aluno ouvinte participante da apresentação.

7.  O Orientador ou Professor da Disciplina clica no botão "Salvar".

8.  O sistema valida os formatos preenchidos, verifica a ausência de
    > matrícula duplicada na mesma sessão (E2 a E4), grava a presença
    > dos ouvintes vinculada à defesa e exibe a mensagem "Ouvintes
    > salvos com sucesso".

9.  Antes da homologação do resultado final, o Orientador clica no botão
    > "Ocorrências" nos detalhes da sessão, preenche o campo de texto
    > livre com os apontamentos relevantes ou incidentes ocorridos
    > durante a arguição (até 2.000 caracteres; E5) e salva o registro
    > (RBN-DEF-08.5).

10. O sistema grava as ocorrências relatadas e disponibiliza o texto em
    > modo somente leitura para a Secretaria e para o Professor da
    > Disciplina.

11. Quando o Orientador libera o resultado final e a defesa transiciona
    > para o status "Realizada" (US-27), o sistema consolida a listagem
    > de ouvintes confirmados, vincula a equivalência de 2 horas de
    > atividades complementares por sessão assistida a cada registro e a
    > disponibiliza à Secretaria do curso (RBN-DEF-08.4).

12. Concomitantemente à liberação do resultado, o sistema gera e envia
    > automaticamente por e-mail a cada membro titular efetivo da banca
    > examinadora a sua declaração individual de participação em PDF
    > contendo código alfanumérico único de autenticidade
    > (RBN-DEF-08.3).

13. Na tela principal de Defesas (US-40), a qualquer momento, o
    > Orientador, Professor da Disciplina, Coordenador de Curso ou
    > Secretaria aciona o botão "Agenda de defesas (PDF)".

14. O sistema aplica os filtros de período e curso definidos em tela
    > (RBN-DEF-01.5 e RBN-CAD-14.1), compila todas as defesas com status
    > "Agendada" ou "Reagendada" (E8) e gera o arquivo PDF público
    > agrupado cronologicamente por dia, contendo data, horário (padrão
    > 24h), título do trabalho, nome do aluno, nome do orientador e
    > local físico ou link da videochamada (RBN-DEF-08.1). O fluxo
    > termina.

**Fluxos alternativos**

1.  Remoção de aluno ouvinte registrado incorretamente (passo 4): Na
    > janela modal de ouvintes, o Orientador ou Professor da Disciplina
    > localiza o estudante cadastrado por engano e clica no botão
    > "Remover" ao lado da respectiva linha. O sistema exclui o registro
    > da listagem temporária. O usuário clica em "Salvar" e o sistema
    > persiste a lista atualizada. O fluxo prossegue a partir do passo
    > 8.

2.  Sessão de defesa sem ocorrências a registrar (passo 9): Se a
    > apresentação e a arguição ocorrerem com total normalidade, o
    > Orientador opta por manter o campo Ocorrências vazio e não
    > preenche nenhum texto (campo opcional). O fluxo prossegue a partir
    > do passo 11.

3.  Consulta da lista de ouvintes pela Secretaria para cômputo de horas
    > (RBN-DEF-08.4; passo 11): No módulo de apoio operacional ou na
    > tela de defesas, a Secretaria do curso filtra pelo período letivo
    > e curso, acessa a sessão realizada e visualiza a lista somente
    > leitura com Nome Completo, Matrícula, dados da defesa e a
    > indicação de 2 horas de atividades complementares por ouvinte para
    > lançamento manual no sistema institucional acadêmico. O fluxo
    > termina.

4.  Geração da agenda de defesas com filtro por curso pela Coordenação
    > ou Secretaria (RBN-DEF-08.1; passo 13): O Coordenador de Curso ou
    > a Secretaria seleciona um curso específico do NUCOMP (ou a opção
    > "Todos") na lista suspensa do filtro (US-39) e clica em "Agenda de
    > defesas (PDF)". O sistema gera o documento PDF contendo
    > exclusivamente as bancas do curso selecionado (ou de todos os
    > cursos) agrupadas por data. O fluxo termina.

5.  Download da segunda via da declaração de participação pelo membro da
    > banca (RBN-DEF-08.3; passo 12): O docente titular ou membro
    > externo que integrou a banca examinadora acessa o menu "Minhas
    > bancas" (US-25) e, na linha da defesa concluída (status
    > "Realizada"), clica no botão "Declaração". O sistema realiza o
    > download imediato da declaração de participação em PDF com o mesmo
    > código alfanumérico validador emitido no encerramento da sessão. O
    > fluxo termina.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1 ou passo 13): Caso o Orientador,
> Professor da Disciplina, Coordenador de Curso ou Secretaria tente
> acessar os detalhes da sessão, o formulário de ouvintes ou a emissão
> da agenda sem sessão ativa no navegador, o sistema exibe a tela de
> login (US-11). Após a autenticação, direciona o usuário para a tela
> solicitada e o fluxo prossegue a partir do passo 1 ou do passo 13. Em
> caso de falha na autenticação, aplicam-se as exceções da US-11.
>
> E2. Matrícula com quantidade de dígitos incorreta ou caracteres não
> numéricos (passo 7): O Orientador ou Professor da Disciplina insere
> uma matrícula com número de dígitos diferente de exatamente 10 ou
> contendo letras e símbolos. O sistema não salva o formulário, destaca
> o campo com erro e exibe: *"A matrícula deve conter exatamente 10
> dígitos numéricos"*. Retorna ao formulário de ouvintes no passo 5.
>
> E3. Matrícula de ouvinte em duplicidade na mesma sessão (passo 7): O
> Orientador ou Professor da Disciplina tenta adicionar uma matrícula
> que já consta inserida na lista de ouvintes daquela mesma defesa. O
> sistema bloqueia a gravação e exibe a mensagem de alerta: *"Este aluno
> já foi registrado como ouvinte nesta defesa"*. Retorna ao formulário
> no passo 5.
>
> E4. Nome Completo de ouvinte em formato inválido ou vazio (passo 7): O
> usuário submete o formulário com o campo Nome Completo em branco,
> contendo algarismos numéricos ou ultrapassando 150 caracteres. O
> sistema impede o salvamento, destaca o campo e informa: *"O nome deve
> conter apenas letras, acentos e espaços e ter até 150 caracteres"*.
> Retorna ao passo 5.
>
> E5. Relato de ocorrências acima do limite de caracteres (passo 9): O
> Orientador insere um texto no campo Ocorrências que ultrapassa 2.000
> caracteres. O sistema bloqueia a gravação, destaca a caixa de texto e
> alerta sobre o limite máximo de 2.000 caracteres. Retorna ao passo 9.
>
> E6. Tentativa de editar ocorrências após a liberação do resultado
> (passo 9): Se o resultado final da defesa já tiver sido homologado
> pelo Orientador (status "Realizada"), o sistema congela o campo
> Ocorrências e não permite edições, mantendo-o apenas para consulta
> (RBN-DEF-08.5). O fluxo termina.
>
> E7. Registro de ouvintes em sessão não iniciada ou cancelada (passo
> 1): Caso o usuário tente abrir a lista de presença em uma defesa que
> ainda possui status "Agendada" ou que foi "Cancelada", o sistema não
> disponibiliza o botão "Ouvintes" e informa: *"O registro de ouvintes
> fica disponível apenas durante ou após a sessão"*. O fluxo termina.
>
> E8. Tentativa de emissão da agenda em PDF sem defesas no período
> (passo 14): Se não houver nenhuma defesa com status Agendada ou
> Reagendada no período letivo ou no intervalo de datas selecionado, o
> sistema não gera um arquivo em branco e exibe: *"Não existem defesas
> agendadas para o período selecionado"*. Retorna ao passo 13.
>
> E9. Usuário sem permissão para registrar ouvintes ou ocorrências
> (passo 3 ou passo 9): Caso um estudante ou docente que não seja o
> Orientador do trabalho nem o Professor da Disciplina daquela turma
> tente acionar as ações de presença ou relato de ocorrências, o sistema
> bloqueia o acesso e exibe: *"Você não tem permissão para esta ação"*.
> O fluxo termina.

**Pós-condições**

- A relação de alunos ouvintes confirmados (Nome Completo e Matrícula de
  > 10 dígitos) foi persistida na base de dados vinculada à sessão de
  > defesa.

- Com a defesa no status "Realizada", a lista de ouvintes com
  > equivalência a 2 horas complementares por sessão foi disponibilizada
  > à Secretaria para lançamento externo no sistema institucional
  > acadêmico.

- O relato de ocorrências registrado pelo Orientador foi armazenado na
  > sessão e disponibilizado em modo leitura para a Secretaria e para o
  > Professor da Disciplina.

- A declaração individual de participação em banca em PDF com código
  > alfanumérico único foi gerada e enviada aos membros titulares
  > examinadores.

- O documento PDF da agenda pública de defesas foi gerado e exportado
  > com agrupamento cronológico por data.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                           | **Resumo da regra em uma frase**                                                                                                                                                                                                                                                                                                                           |
|--------------|-------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **DEF-08.1** | O sistema deve gerar a agenda de defesas em PDF, com as sessões agrupadas por dia.                                | Exporta documento PDF público agrupando cronologicamente por data as defesas agendadas ou reagendadas do período e curso filtrados, com horário, título, aluno, orientador e local/link.                                                                                                                                                                   |
| **DEF-08.2** | O sistema deve mostrar um formulário de registro de ouvintes que deve conter os campos Nome Completo e Matrícula. | Disponibiliza campo de texto com até 150 caracteres (apenas letras, acentos e espaços) com botões para adicionar/remover ouvintes nas sessões Em Andamento ou Realizadas, bloqueando matrícula duplicada na mesma sessão. Exige o preenchimento de campo numérico composto por exatamente 10 dígitos para a matrícula institucional de cada aluno ouvinte. |
| **DEF-08.3** | O sistema deve emitir declaração de participação em banca.                                                        | Envia automaticamente por e-mail declaração individual em PDF com código alfanumérico único de autenticidade a cada membro efetivo da banca após a liberação do resultado da sessão.                                                                                                                                                                       |
| **DEF-08.4** | O sistema deve disponibilizar à Secretaria a lista de ouvintes vinculados a cada sessão de defesa.                | Apresenta à Secretaria tela de consulta com filtro de período e curso, listando os ouvintes por defesa e indicando a equivalência de 2 horas complementares por sessão assistida para lançamento externo.                                                                                                                                                  |
| **DEF-08.5** | O sistema deve mostrar um formulário de registro da sessão que deve conter o campo Ocorrências.                   | Disponibiliza ao Orientador campo opcional de texto livre com até 2.000 caracteres para relatar incidentes da sessão até a liberação do resultado, visível apenas para leitura à Secretaria e ao Professor da Disciplina.                                                                                                                                  |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Registro de Nome e Matrícula de ouvintes atrelado à sessão.
>
> 2\. PDF da agenda filtra por período e ordena cronologicamente.

***Cenário 1: Registro de alunos ouvintes com sucesso durante a
sessão***

> **Dado que** a defesa de TCC está com o status "Em Andamento",
>
> **Quando** o Orientador ou Professor da Disciplina clica em
> "Ouvintes", informa o Nome Completo "Larissa Campos Freire" e a
> Matrícula com 10 dígitos "2415080044",
>
> **E** aciona o botão "Salvar",
>
> **Então** o sistema valida as informações e insere o estudante na
> lista oficial de ouvintes daquela defesa.

***Cenário 2: Adição de múltiplos ouvintes na mesma sessão***

> **Dado que** o Orientador está na janela modal de registro de
> presença,
>
> **Quando** adiciona três linhas sucessivas com nomes e matrículas
> válidas de 10 dígitos e clica em "Salvar",
>
> **Então** o sistema grava os três alunos ouvintes vinculados àquela
> defesa e exibe a mensagem de confirmação.

***Cenário 3: Bloqueio de matrícula de ouvinte duplicada na mesma defesa
(E3)***

> **Dado que** a estudante com matrícula "2415080044" já foi adicionada
> na lista da sessão atual,
>
> **Quando** o Orientador ou Professor da Disciplina tenta inserir
> novamente a mesma matrícula nessa mesma defesa,
>
> **Então** o sistema bloqueia a gravação e informa que a aluna já está
> registrada como ouvinte nesta defesa.

***Cenário 4: Validação de matrícula com formato inválido - menos de 10
dígitos (E2)***

> **Dado que** o Orientador ou Professor da Disciplina está no
> formulário de presença,
>
> **Quando** digita a matrícula "24150800" contendo apenas 8 dígitos e
> tenta salvar,
>
> **Então** o sistema não salva o registro e alerta que a matrícula deve
> ter exatamente 10 dígitos numéricos.

***Cenário 5: Validação de matrícula contendo letras ou caracteres
especiais (E2)***

> **Dado que** o Orientador ou Professor da Disciplina está preenchendo
> o formulário de ouvintes,
>
> **Quando** insere a matrícula "24150800AB" e tenta salvar,
>
> **Então** o sistema recusa a entrada e sinaliza que a matrícula aceita
> exclusivamente algarismos numéricos.

***Cenário 6: Validação de Nome Completo de ouvinte com caracteres
inválidos (E4)***

> **Dado que** o Orientador ou Professor da Disciplina preencheu o campo
> de nome com "Carlos Souza 123",
>
> **Quando** aciona o comando para salvar o ouvinte,
>
> **Então** o sistema bloqueia o registro e indica que o nome deve
> conter apenas letras, acentos e espaços.

***Cenário 7: Remoção de ouvinte cadastrado incorretamente antes de
salvar (Fluxo Alternativo A)***

> **Dado que** o Orientador ou Professor da Disciplina adicionou um
> ouvinte por engano no modal de presença,
>
> **Quando** clica no botão "Remover" correspondente à linha do aluno e
> confirma o salvamento,
>
> **Então** o sistema exclui o registro e atualiza a relação de ouvintes
> da sessão.

***Cenário 8: Registro de ocorrências da sessão pelo Orientador antes da
liberação do resultado***

> **Dado que** a defesa está em andamento e ocorreu uma queda temporária
> de conexão na apresentação remota,
>
> **Quando** o Orientador abre o campo Ocorrências, relata o ocorrido
> com 300 caracteres e salva antes de liberar as notas,
>
> **Então** o sistema salva o registro e o disponibiliza para leitura à
> Secretaria e ao Professor da Disciplina.

***Cenário 9: Bloqueio de edição de ocorrências após liberação do
resultado (E6)***

> **Dado que** o Orientador já liberou o resultado da defesa e a sessão
> transitou para o status "Realizada",
>
> **Quando** o Orientador abre os detalhes da defesa,
>
> **Então** o campo Ocorrências é exibido apenas para leitura,
> permanecendo desabilitado para alterações ou inclusões.

***Cenário 10: Validação de texto de ocorrências com mais de 2.000
caracteres (E5)***

> **Dado que** o Orientador está preenchendo o relato da banca,
>
> **Quando** cola um texto com 2.001 caracteres no campo Ocorrências e
> tenta salvar,
>
> **Então** o sistema bloqueia o salvamento e alerta sobre o limite
> máximo de 2.000 caracteres.

***Cenário 11: Emissão e envio automático da declaração de participação
aos examinadores***

> **Dado que** a defesa de TCC teve o seu resultado liberado pelo
> Orientador e passou ao status "Realizada",
>
> **Quando** a finalização da sessão é processada pelo sistema,
>
> **Então** o sistema envia automaticamente por e-mail a declaração de
> participação em PDF com código alfanumérico único para cada membro
> efetivo da banca examinadora.

***Cenário 12: Download de segunda via da declaração em Minhas Bancas
(Fluxo Alternativo E)***

> **Dado que** um docente participou de uma banca cuja sessão já está no
> status "Realizada",
>
> **Quando** acessa a tela Minhas bancas e aciona o botão "Declaração"
> na linha correspondente,
>
> **Então** o sistema realiza o download da declaração individual em PDF
> com código validador.

***Cenário 13: Disponibilização da lista de ouvintes com 2 horas para a
Secretaria (RBN-DEF-08.4)***

> **Dado que** uma defesa concluída possui 12 ouvintes confirmados,
>
> **Quando** a Secretaria do curso consulta a sessão no módulo
> operacional,
>
> **Então** o sistema exibe os nomes, matrículas e a anotação explícita
> de "2 horas complementares" por ouvinte para lançamento no sistema
> acadêmico.

***Cenário 14: Geração da agenda pública de defesas em PDF agrupada por
dia***

> **Dado que** existem quatro defesas com status "Agendada" distribuídas
> entre os dias 15 e 16 de outubro,
>
> **Quando** a Secretaria ou Coordenação clica no botão "Agenda de
> defesas (PDF)" com o período letivo filtrado,
>
> **Então** o sistema gera o arquivo PDF com as sessões agrupadas
> cronologicamente por data, exibindo horário (HH:MM), título, aluno,
> orientador e local ou link.

***Cenário 15: Geração de agenda de defesas filtrada por curso (Fluxo
Alternativo D)***

> **Dado que** a Secretaria de Engenharia de Computação selecionou o seu
> curso no filtro de Curso,
>
> **Quando** clica em "Agenda de defesas (PDF)",
>
> **Então** o sistema exporta o PDF da agenda contendo exclusivamente as
> bancas do curso de Engenharia de Computação.

***Cenário 16: Tentativa de gerar agenda em PDF sem defesas no período
selecionado (E8)***

> **Dado que** não há defesas marcadas para a próxima semana,
>
> **Quando** a Secretaria ou Coordenação filtra "Esta Semana" e aciona o
> botão "Agenda de defesas (PDF)",
>
> **Então** o sistema não gera o arquivo em branco e emite o aviso: "Não
> existem defesas agendadas para o período selecionado".

***Cenário 17: Bloqueio de registro de ouvintes em defesa com status
"Agendada" (E7)***

> **Dado que** a defesa está agendada para data futura,
>
> **Quando** o Professor da Disciplina ou Orientador abre os detalhes da
> sessão antes do horário de início,
>
> **Então** o botão de registro de ouvintes permanece indisponível,
> informando que a presença só pode ser registrada durante ou após a
> sessão.

***Cenário 18: Acesso sem autenticação redireciona para a tela de login
(E1)***

> **Dado que** o Orientador, Professor da Disciplina ou Secretaria não
> possui uma sessão ativa no sistema,
>
> **Quando** tenta abrir a URL direta da funcionalidade de ouvintes ou
> da agenda em PDF,
>
> **Então** o sistema redireciona para a tela de login (US-11) e, após a
> autenticação bem-sucedida, restabelece o acesso solicitado.

**Tela no protótipo**

**Tela:** Ouvintes / Defesas





**Diagrama de sequência**

**Diagrama relacionado:** \[nome do diagrama ou "sem diagrama próprio" e
o motivo\]

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[X\] Descrição no formato Como, Quero, Para que
>
> \[X\] Requisitos da matriz conferidos
>
> \[X\] Fluxo principal e fluxos alternativos escritos
>
> \[X\] Atores, pré-condições e pós-condições preenchidos
>
> \[X\] Fluxos de exceção escritos
>
> \[X\] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

# Leandra Matos: Vida do TCC

## US-13 Registrar a Proposta, cadastrar os dados do TCC e alterar o tema

| **Épico:**                | Cadastro e Manutenção                    |
|---------------------------|------------------------------------------|
| **Feature:**              | Fluxo do TCC e Entregas                  |
| **Requisitos da matriz:** | RBN-CAD-07.1, RBN-CAD-08.1, RBN-CAD-08.2 |
| **Prioridade (MoSCoW):**  | Must Have                                |
| **Responsável:**          | Leandra Matos                            |

**Descrição**

Como Aluno, quero registrar a Proposta do meu TCC, informar a Área de
Interesse e as Palavras-Chave e alterar o tema enquanto o TCC estiver Em
Andamento, para que o meu trabalho fique definido e atualizado no
sistema.

**Atores**

> **Ator principal:** Aluno.
>
> **Atores secundários:** Orientador, quando houver, que recebe a
> notificação de cada mudança de tema.

**Pré-condições**

- O Aluno está autenticado no sistema, com o Status da Conta Ativa
  > (US-11). Sem sessão ativa, aplica-se o fluxo de exceção E1.

- O Aluno está vinculado a uma turma não arquivada (US-08). A Proposta é
  > criada nessa turma, que é a turma ativa do aluno. Com a turma
  > arquivada, aplica-se o E9.

- Para registrar a Proposta, o TCC está com o Status Sem Proposta e
  > ainda não existe Proposta do aluno nessa turma.

- Para alterar a Proposta ou os dados do TCC (mudança de tema), o TCC
  > está com o Status Em Andamento. Com outro Status, aplica-se o E7 ou
  > o E8.

- A indicação de orientador (US-17) não depende da Proposta.

**Fluxo principal**

> 1\. No menu lateral do sistema, o Aluno acessa o item Turmas e
> seleciona a sua turma (ex.: TCC 1 · ECP07_T01).
>
> 2\. O sistema abre a tela da turma na aba Meu TCC e exibe a seção
> Proposta, com a etiqueta Sem Proposta, os campos Título, Subtítulo,
> Resumo (com o contador de caracteres restantes), Modalidade e Link do
> Documento da Proposta e o botão Salvar Proposta.
>
> 3\. O Aluno informa o Título (obrigatório, até 250 caracteres) e,
> opcionalmente, o Subtítulo (até 250 caracteres).
>
> 4\. O Aluno informa o Resumo (obrigatório, até 1.000 caracteres) e
> seleciona a Modalidade na lista (Monografia ou Artigo Científico).
>
> 5\. Opcionalmente, o Aluno insere no campo Link do Documento da
> Proposta o endereço de um arquivo com acesso público, iniciado por
> https:// e com até 500 caracteres.
>
> 6\. O Aluno aciona o botão Salvar Proposta.
>
> 7\. O sistema valida os campos (E2 a E4), cria a Proposta na turma
> ativa do aluno, muda o Status do TCC de Sem Proposta para Em Andamento
> e grava a mudança no histórico com o gatilho Proposta salva (US-14).
>
> 8\. Se a turma tiver uma entrega do tipo Proposta, o sistema registra
> essa entrega como cumprida, com a data e a hora do salvamento, e
> define o status de envio: Entregue, quando o salvamento ocorre até
> 23:59 da Data Limite, ou Entregue com Atraso, quando ocorre depois
> (CAD-09.3).
>
> 9\. O sistema mantém o Aluno na aba Meu TCC, exibe "Proposta salva",
> troca a etiqueta para Em Andamento, esconde o botão Salvar Proposta e
> libera, abaixo da Proposta, os campos Área de Interesse e
> Palavras-Chave e o botão Salvar alterações.
>
> 10\. O Aluno seleciona a Área de Interesse na lista de 10 áreas
> (Engenharia de Software, Inteligência Artificial, Redes de
> Computadores, Banco de Dados, Sistemas Embarcados, Segurança da
> Informação, Interação Humano-Computador, Ciência de Dados, Computação
> Gráfica ou Educação em Computação).
>
> 11\. O Aluno informa de 1 a 5 Palavras-Chave, uma em cada caixa, com
> até 100 caracteres cada, e aciona o botão Salvar alterações.
>
> 12\. O sistema valida os campos (E3, E5 e E6), grava a Área de
> Interesse e as Palavras-Chave no TCC e mantém o Aluno na aba Meu TCC,
> com a mensagem "Alterações salvas" e os campos preenchidos. O fluxo
> termina.

**Fluxos alternativos**

> A. Mudança de tema com orientador (CAD-08.2; passo 2): com o Status Em
> Andamento, o Aluno abre a aba Meu TCC, altera um ou mais dos campos
> Título, Subtítulo, Resumo, Modalidade, Link do Documento da Proposta,
> Área de Interesse e Palavras-Chave e aciona o botão Salvar alterações.
> O sistema valida com as mesmas regras (E2 a E6), grava e envia uma
> notificação ao Orientador. O Aluno permanece na aba Meu TCC, com a
> mensagem "Alterações salvas". O fluxo termina.
>
> B. Mudança de tema sem orientador (passo 2): igual ao fluxo A, mas o
> sistema não envia notificação, porque o trabalho ainda não tem
> orientador. O fluxo termina.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o Aluno tente acessar a
> tela da turma sem sessão ativa (pelo menu, pelo endereço da página ou
> por um link recebido), o sistema apresenta a tela de login (US-11).
> Após a autenticação, o sistema exibe a aba Meu TCC da turma, e o fluxo
> prossegue a partir do passo 2. Em caso de falha na autenticação,
> aplicam-se as exceções da US-11.
>
> E2. Campo obrigatório em branco (passo 7): o Título, o Resumo ou a
> Modalidade não foi preenchido. O sistema não salva, destaca o campo e
> exibe "Campo obrigatório". Retorna ao passo 3.
>
> E3. Texto acima do limite (passos 7 ou 12): Título ou Subtítulo com
> mais de 250 caracteres, Resumo com mais de 1.000 ou Palavra-Chave com
> mais de 100. O sistema não salva, destaca o campo e informa o limite.
> No Resumo, o contador exibe os caracteres restantes durante a
> digitação. Retorna ao passo 3 ou ao passo 11.
>
> E4. Link do Documento da Proposta inválido (passo 7): o endereço não
> começa com https:// ou tem mais de 500 caracteres. O sistema não
> salva, destaca o campo e exibe "O link deve começar com https:// e ter
> até 500 caracteres". Retorna ao passo 5.
>
> E5. Nenhuma Palavra-Chave (passo 12): o Aluno aciona o botão Salvar
> alterações sem preencher nenhuma caixa de Palavra-Chave. O sistema não
> salva e exibe "Informe de 1 a 5 Palavras-Chave". Retorna ao passo 11.
>
> E6. Sexta Palavra-Chave (passo 11): o formulário tem apenas 5 caixas
> de Palavra-Chave, e o sistema não deixa adicionar outra. Retorna ao
> passo 11.
>
> E7. Status diferente de Em Andamento (passo 2): com o TCC no Status
> Apto para Defesa, por exemplo, os campos da Proposta, a Área de
> Interesse e as Palavras-Chave aparecem apenas para leitura, sem os
> botões Salvar Proposta e Salvar alterações. Não há mudança de tema. O
> fluxo termina.
>
> E8. Aluno com o Status Desistente, Reprovado ou Jubilado (CAD-08.5;
> passo 2): o Aluno consegue acessar o sistema, mas a aba Meu TCC
> permanece disponível apenas para consulta, com os botões de edição
> desabilitados. O fluxo termina.
>
> E9. Turma arquivada (passo 2): a turma aparece em Turmas arquivadas, e
> a aba Meu TCC permanece disponível apenas para consulta, sem os botões
> Salvar Proposta e Salvar alterações. O fluxo termina.

**Pós-condições**

- A Proposta foi criada na turma ativa do aluno e passou a identificar o
  > trabalho no sistema.

- O Status do TCC foi alterado de Sem Proposta para Em Andamento, e a
  > mudança foi registrada no histórico (US-14).

- A entrega do tipo Proposta da turma, quando existente, foi cumprida
  > com a data e a hora do salvamento, com o status de envio Entregue ou
  > Entregue com Atraso.

- A Área de Interesse e as Palavras-Chave foram gravadas no TCC.

- Na mudança de tema, os campos alterados foram gravados e o Orientador,
  > quando existente, foi notificado.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                                                                       | **Resumo da regra em uma frase**                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-07.1** | O sistema deve mostrar um formulário de cadastro da Proposta que deve conter os campos Título, Subtítulo, Resumo, Modalidade e Link do Documento da Proposta, e registrar a Proposta na turma ativa do aluno. | Formulário da Proposta com Título, Subtítulo, Resumo, Modalidade e Link do Documento da Proposta (opcional); salvar cria a Proposta na turma ativa, muda o Status do TCC para Em Andamento e cumpre a entrega do tipo Proposta, se houver.                                                                                                                                                                                                                                                           |
| **CAD-08.1** | O sistema deve mostrar um formulário de cadastro do TCC que deve conter os campos Área de Interesse e Palavras-Chave.                                                                                         | Área de Interesse escolhida numa lista de 10 áreas fixas (Engenharia de Software, Inteligência Artificial, Redes de Computadores, Banco de Dados, Sistemas Embarcados, Segurança da Informação, Interação Humano-Computador, Ciência de Dados, Computação Gráfica e Educação em Computação), liberada depois de salvar a Proposta e exigida para o Apto para Defesa. De 1 a 5 Palavras-Chave, com até 100 caracteres cada, liberadas depois de salvar a Proposta e exigidas para o Apto para Defesa. |
| **CAD-08.2** | \[Exceção\] O sistema deve permitir a mudança do tema do TCC: Título, Subtítulo, Resumo, Modalidade, Link do Documento da Proposta, Área de Interesse e Palavras-Chave.                                       | Enquanto o Status for Em Andamento, o aluno pode mudar o tema (Título, Subtítulo, Resumo, Modalidade, Link do Documento da Proposta, Área e Palavras-Chave), e o orientador é avisado de cada alteração.                                                                                                                                                                                                                                                                                             |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Exige Título, Resumo e Modalidade; o Subtítulo e o Link do
> Documento da Proposta são opcionais. Área de Interesse e
> Palavras-Chave são preenchidas depois, no cadastro do TCC.
>
> 2\. Ao salvar, o Status do TCC muda para "Em Andamento".

***Cenário 1: Proposta salva com sucesso (fluxo principal, passos 1 a
9)***

> **Dado que** o Aluno está autenticado, vinculado à turma TCC 1 ·
> ECP07_T01 e com o TCC no Status Sem Proposta
>
> **Quando** abre a aba Meu TCC, preenche Título, Resumo e a Modalidade
> Monografia e aciona o botão Salvar Proposta
>
> **Então** o sistema cria a Proposta na turma, exibe "Proposta salva" e
> muda a etiqueta para Em Andamento
>
> **E** esconde o botão Salvar Proposta e libera os campos Área de
> Interesse e Palavras-Chave

***Cenário 2: Área de Interesse e Palavras-Chave salvas (fluxo
principal, passos 10 a 12)***

> **Dado que** o Aluno já salvou a Proposta e está na aba Meu TCC
>
> **Quando** seleciona a área Sistemas Embarcados, informa as
> Palavras-Chave IoT, hidrologia e LoRa e aciona o botão Salvar
> alterações
>
> **Então** o sistema grava a área e as 3 Palavras-Chave e exibe
> "Alterações salvas"

***Cenário 3: Proposta cumpre a entrega do tipo Proposta (passo 8)***

> **Dado que** a turma tem uma entrega do tipo Proposta com Data Limite
> 10/09
>
> **Quando** o Aluno salva a Proposta em 08/09
>
> **Então** a entrega do tipo Proposta passa ao status Entregue

***Cenário 4: Proposta salva após a Data Limite da entrega do tipo
Proposta (passo 8)***

> **Dado que** a turma tem uma entrega do tipo Proposta com Data Limite
> 10/09
>
> **Quando** o Aluno salva a Proposta em 12/09
>
> **Então** a entrega do tipo Proposta passa ao status Entregue com
> Atraso e o Status do TCC passa a Em Andamento

***Cenário 5: mudança de tema com orientador (fluxo alternativo A)***

> **Dado que** o TCC está Em Andamento e tem orientador vinculado
>
> **Quando** o Aluno altera o Título na aba Meu TCC e aciona o botão
> Salvar alterações
>
> **Então** o novo Título é gravado e exibido
>
> **E** o Orientador recebe uma notificação da alteração

***Cenário 6: mudança de tema sem orientador (fluxo alternativo B)***

> **Dado que** o TCC está Em Andamento e ainda não tem orientador
>
> **Quando** o Aluno altera o Resumo e aciona o botão Salvar alterações
>
> **Então** o novo Resumo é gravado e nenhuma notificação é enviada

***Cenário 7: acesso sem estar autenticado (E1)***

> **Dado que** o Aluno não está autenticado
>
> **Quando** tenta abrir a tela da sua turma
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre a aba Meu TCC da turma

***Cenário 8: campo obrigatório em branco (E2)***

> **Dado que** o Aluno está na seção Proposta
>
> **Quando** deixa o Resumo em branco e aciona o botão Salvar Proposta
>
> **Então** o sistema não salva, destaca o Resumo e exibe "Campo
> obrigatório"

***Cenário 9: texto acima do limite (E3)***

> **Dado que** o Aluno está na seção Proposta
>
> **Quando** informa um Título com 251 caracteres e aciona o botão
> Salvar Proposta
>
> **Então** o sistema não salva, destaca o Título e informa o limite de
> 250 caracteres

***Cenário 10: Link do Documento da Proposta inválido (E4)***

> **Dado que** o Aluno está na seção Proposta com Título, Resumo e
> Modalidade preenchidos
>
> **Quando** informa o link drive.google.com/proposta, sem https://, e
> aciona o botão Salvar Proposta
>
> **Então** o sistema não salva e exibe "O link deve começar com
> https:// e ter até 500 caracteres"

***Cenário 11: nenhuma Palavra-Chave (E5)***

> **Dado que** o Aluno selecionou a Área de Interesse
>
> **Quando** deixa as 5 caixas de Palavra-Chave vazias e aciona o botão
> Salvar alterações
>
> **Então** o sistema não salva e exibe "Informe de 1 a 5
> Palavras-Chave"

***Cenário 12: sexta Palavra-Chave (E6)***

> **Dado que** o Aluno já preencheu as 5 caixas de Palavra-Chave
>
> **Quando** procura onde informar uma sexta Palavra-Chave
>
> **Então** o formulário não oferece uma sexta caixa

***Cenário 13: mudança de tema bloqueada pelo Status (E7)***

> **Dado que** o TCC está com o Status Apto para Defesa
>
> **Quando** o Aluno abre a aba Meu TCC
>
> **Então** os campos da Proposta e do TCC aparecem apenas para leitura,
> sem os botões Salvar Proposta e Salvar alterações

***Cenário 14: aluno Desistente (E8)***

> **Dado que** o Professor da Disciplina registrou o aluno como
> Desistente
>
> **Quando** o Aluno abre a aba Meu TCC
>
> **Então** visualiza os dados apenas para consulta, com os botões de
> edição desabilitados

***Cenário 15: turma arquivada (E9)***

> **Dado que** a turma do aluno foi arquivada
>
> **Quando** o Aluno abre a turma em Turmas arquivadas
>
> **Então** a aba Meu TCC aparece apenas para consulta

**Tela no protótipo**

**Tela**: Turmas de alunos



**Tela:** Proposta e cadastro do
TCC

**Diagrama de sequência**

**Diagrama relacionado:** Proposta e entrega

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[x\] Tela do protótipo e diagrama de sequência indicados
>
> \[x\] Revisada por outra pessoa (nome:)

## US-14 Atualizar o Status do TCC e consultar o histórico e a trilha

| **Épico:**                | Cadastro e Manutenção                    |
|---------------------------|------------------------------------------|
| **Feature:**              | Fluxo do TCC e Entregas                  |
| **Requisitos da matriz:** | RBN-CAD-08.3, RBN-CAD-08.7, RBN-CAD-08.8 |
| **Prioridade (MoSCoW):**  | Must Have (CAD-08.8: Could Have)         |
| **Responsável:**          | Leandra Matos                            |

**Descrição**

Como Aluno, quero que o Status do meu TCC seja atualizado
automaticamente a cada gatilho e que eu possa consultar o histórico e a
trilha do Status, para acompanhar a etapa em que o trabalho se encontra
sem depender de atualização manual.

**Atores**

> **Ator principal:** Aluno, alvo do resultado: é o Status do seu TCC
> que muda a cada gatilho.
>
> **Atores secundários:** Orientador e Professor da Disciplina, que
> consultam o Status, o histórico e a trilha. Os usuários que disparam
> cada gatilho (banca, Professor da Disciplina e Secretaria) são atores
> das respectivas US.

**Pré-condições**

- O aluno está vinculado a uma turma (US-08). O vínculo é o primeiro
  > gatilho e define o Status Sem Proposta.

- A mudança de Status não tem tela própria: ela ocorre quando a ação do
  > gatilho é concluída na sua US, por um usuário autenticado.

- Para consultar o Status, o histórico e a trilha, o Aluno, o Orientador
  > ou o Professor da Disciplina precisa estar autenticado, com o Status
  > da Conta Ativa (US-11). Sem sessão ativa, aplica-se o E1.

**Fluxo principal**

> 1\. Um usuário conclui, em outra tela do sistema, uma ação que é
> gatilho: vincular o aluno à turma (US-08), salvar a Proposta (US-13),
> confirmar Apto para Defesa (US-42), liberar o resultado da banca
> (US-27), homologar a Versão Final (US-44), registrar Desistente,
> Reprovado ou Jubilado no encerramento da participação (US-09) ou
> vincular à turma de TCC 2 um aluno Aprovado para TCC 2 (US-08).
>
> 2\. O sistema identifica o novo Status pela tabela de gatilhos
> (CAD-08.3) e o grava no TCC. O Status não é informado nem selecionado
> por nenhum usuário.
>
> 3\. O sistema grava no histórico o Status anterior, o novo Status, a
> data e a hora, o usuário cuja ação disparou a mudança e o gatilho
> (Vínculo à turma, Proposta salva, Transferência para TCC 2, Indicação
> de Apto para Defesa, Liberação do resultado, Homologação da Versão
> Final ou Encerramento da participação).
>
> 4\. No menu lateral do sistema, o Aluno acessa o item Turmas e
> seleciona a sua turma.
>
> 5\. O sistema abre a aba Meu TCC e exibe o novo Status na etiqueta ao
> lado do título da seção Proposta.
>
> 6\. O Aluno aciona o link Histórico do Status do TCC, abaixo dos
> campos do TCC.
>
> 7\. O sistema abre o histórico em lista cronológica, somente leitura,
> com Status anterior, Status novo, data e hora, responsável e gatilho,
> e exibe a trilha do Status do TCC com a etapa atual destacada.
>
> 8\. O Aluno fecha o histórico e retorna à aba Meu TCC. O fluxo
> termina.

**Fluxos alternativos**

> A. Consulta pelo Orientador (passo 4): no item Orientações do menu
> lateral, o Orientador visualiza o Status de cada orientando na coluna
> Status do TCC do Painel de orientandos e aciona o link Histórico na
> linha do aluno. O sistema exibe o mesmo conteúdo do passo 7, e o
> Orientador retorna ao painel ao fechar. O fluxo termina.
>
> B. Consulta pelo Professor da Disciplina (passo 4): no menu lateral, o
> Professor acessa o item Turmas, seleciona a turma, abre a aba Alunos,
> seleciona o bloco do aluno (painel do aluno, US-41) e aciona o link
> Histórico do Status do TCC. O sistema exibe o mesmo conteúdo do passo
> 7, e o Professor retorna ao painel do aluno ao fechar. O fluxo
> termina.
>
> C. Transferência para o TCC 2 (passo 1): quando o aluno com o Status
> Aprovado para TCC 2 é vinculado à turma de TCC 2, o Status do TCC
> retorna a Em Andamento. A cópia dos dados e da orientação nessa
> transferência (CAD-08.6) é tratada na US-08. O histórico do período
> anterior é mantido (CAD-08.6). O fluxo prossegue a partir do passo 3.
>
> D. Entrega atrasada ou não enviada (passo 1): o Status do TCC não
> muda. O atraso é registrado apenas no status de envio da entrega
> (US-15). O fluxo termina.
>
> E. Trilha encerrada (passo 7): com Reprovado, Desistente ou Jubilado,
> a trilha termina na etapa em que o status ocorreu. O fluxo prossegue a
> partir do passo 8.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 4): caso o Aluno, o Orientador ou o
> Professor da Disciplina tente acessar a aba Meu TCC, o Painel de
> orientandos ou o painel do aluno sem sessão ativa (pelo menu, pelo
> endereço da página ou por um link recebido), o sistema apresenta a
> tela de login (US-11). Após a autenticação, o sistema exibe a tela que
> o usuário tentou abrir, e o fluxo prossegue a partir do passo 5. Em
> caso de falha na autenticação, aplicam-se as exceções da US-11.
>
> E2. Tentativa de edição manual (passo 5): o Status aparece apenas como
> etiqueta, sem campo nem botão para mudá-lo, para qualquer perfil. O
> fluxo termina.
>
> E3. Usuário sem vínculo com o trabalho (passo 4): um Docente que não é
> o Orientador do aluno nem o Professor da Disciplina da turma não
> visualiza o histórico nem a trilha desse TCC. O fluxo termina.

**Pós-condições**

- O Status do TCC foi atualizado para o valor definido pelo último
  > gatilho.

- O histórico recebeu um registro com o Status anterior, o novo Status,
  > a data e a hora, o responsável e o gatilho.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                                                                       | **Resumo da regra em uma frase**                                                                                                                                                                                                               |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-08.3** | O sistema deve exibir o Status do TCC, com um dos valores: Sem Proposta, Em Andamento, Apto para Defesa, Aprovado, Aprovado com Correções, Aprovado para TCC 2, Reprovado, Concluído, Desistente ou Jubilado. | Status do TCC somente leitura, definido por gatilhos (Sem Proposta, Em Andamento, Apto para Defesa, Aprovado para TCC 2, Aprovado, Aprovado com Correções, Concluído, Reprovado, Desistente, Jubilado); o atraso de entrega não muda o Status. |
| **CAD-08.7** | O sistema deve registrar e exibir o histórico do Status do TCC.                                                                                                                                               | Cada mudança do Status do TCC fica no histórico com o status anterior e o novo, data e hora, responsável e gatilho, visível ao Aluno, ao Orientador e ao Professor da Disciplina.                                                              |
| **CAD-08.8** | O sistema deve exibir a trilha do Status do TCC.                                                                                                                                                              | Trilha do Status do TCC: em TCC 1, Em Andamento, Apto para Defesa e Aprovado para TCC 2; em TCC 2, Em Andamento, Apto para Defesa, Aprovado ou Aprovado com Correções e Concluído.                                                             |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Gatilhos fixos: Apto para Defesa, Aprovado para TCC 2, Aprovado,
> Aprovado com Correções, Concluído, Reprovado, Desistente e Jubilado
> (sem edição manual do status).
>
> 2\. Na transferência para o TCC 2, o Status retorna a Em Andamento; a
> herança dos metadados da proposta é tratada na US-08.

***Cenário 1: Sem Proposta ao vincular o aluno à turma (passos 1 a 3)***

> **Dado que** o Professor da Disciplina vinculou o aluno à turma TCC 1
> · ECP07_T01 (US-08)
>
> **Quando** o vínculo é gravado
>
> **Então** o TCC é criado com o Status Sem Proposta e o histórico
> registra o Status anterior vazio, Sem Proposta, a data e a hora, o
> Professor da Disciplina e o gatilho Vínculo à turma

***Cenário 2: Em Andamento ao salvar a Proposta (passos 1 a 3)***

> **Dado que** o TCC está com o Status Sem Proposta
>
> **Quando** o Aluno salva a Proposta (US-13)
>
> **Então** o Status passa a Em Andamento e o histórico registra Sem
> Proposta, Em Andamento, a data e a hora, o Aluno e o gatilho Proposta
> salva

***Cenário 3: Apto para Defesa***

> **Dado que** o TCC está Em Andamento e a entrega do tipo Documento
> para Defesa está Entregue
>
> **Quando** o Orientador confirma Apto para Defesa (US-42)
>
> **Então** o Status passa a Apto para Defesa e o histórico registra o
> Orientador como responsável

***Cenário 4: Aprovado para TCC 2***

> **Dado que** o TCC 1 está Apto para Defesa e a defesa foi realizada
>
> **Quando** a banca libera o resultado com nota final 7,0
>
> **Então** o Status passa a Aprovado para TCC 2

***Cenário 5: Aprovado***

> **Dado que** o TCC 2 está Apto para Defesa e a defesa foi realizada
>
> **Quando** a banca libera o resultado com nota final 8,0 e parecer
> Aprovado
>
> **Então** o Status passa a Aprovado

***Cenário 6: Aprovado com Correções***

> **Dado que** o TCC 2 está Apto para Defesa e a defesa foi realizada
>
> **Quando** a banca libera o resultado com nota final 7,5 e parecer
> Aprovado com Correções
>
> **Então** o Status passa a Aprovado com Correções

***Cenário 7: Reprovado pela banca***

> **Dado que** o TCC está Apto para Defesa e a defesa foi realizada
>
> **Quando** a banca libera o resultado com nota final 5,0
>
> **Então** o Status passa a Reprovado

***Cenário 8: Concluído***

> **Dado que** o Aluno enviou o link da Versão Final do TCC 2
>
> **Quando** o Professor da Disciplina aciona o botão Homologar (US-44)
>
> **Então** o Status passa a Concluído

***Cenário 9: Desistente ou Jubilado***

> **Dado que** o TCC está Em Andamento
>
> **Quando** o Professor da Disciplina registra a desistência ou o
> jubilamento do aluno, com justificativa (US-09)
>
> **Então** o Status passa a Desistente ou Jubilado e o histórico
> registra o Professor como responsável

***Cenário 10: Reprovado registrado pelo Professor da Disciplina***

> **Dado que** o TCC está Em Andamento
>
> **Quando** o Professor da Disciplina encerra a participação do aluno
> com o Status Reprovado e a justificativa (US-09)
>
> **Então** o Status passa a Reprovado e o histórico registra o
> Professor como responsável e o gatilho Encerramento da participação

***Cenário 11: consulta do histórico pelo Aluno (passos 4 a 8)***

> **Dado que** o Aluno está autenticado e o TCC já mudou de Status duas
> vezes
>
> **Quando** abre a aba Meu TCC e aciona o link Histórico do Status do
> TCC
>
> **Então** o sistema exibe as duas mudanças, da mais antiga para a mais
> recente, com Status anterior, Status novo, data e hora, responsável e
> gatilho
>
> **E** exibe a trilha com a etapa atual destacada

***Cenário 12: consulta pelo Orientador (fluxo alternativo A)***

> **Dado que** o Orientador está autenticado e tem o aluno no Painel de
> orientandos
>
> **Quando** aciona o link Histórico na linha do aluno
>
> **Então** o sistema exibe o histórico e a trilha do TCC desse aluno

***Cenário 13: consulta pelo Professor da Disciplina (fluxo alternativo
B)***

> **Dado que** o Professor da Disciplina está no painel de um aluno da
> sua turma
>
> **Quando** aciona o link Histórico do Status do TCC
>
> **Então** o sistema exibe o histórico e a trilha do TCC desse aluno

***Cenário 14: transferência para o TCC 2 (fluxo alternativo C)***

> **Dado que** o aluno está Aprovado para TCC 2
>
> **Quando** é vinculado à turma de TCC 2 (US-08)
>
> **Então** o Status do TCC retorna a Em Andamento e o histórico
> registra o gatilho Transferência para TCC 2

***Cenário 15: Versão Final não entregue no prazo (fluxo alternativo
D)***

> **Dado que** o TCC 2 está Aprovado, sem link da Versão Final, e a Data
> Limite da entrega do tipo Versão Final é 30/11
>
> **Quando** chega o dia 01/12
>
> **Então** o Status do TCC permanece Aprovado e a entrega do tipo
> Versão Final passa a Não Entregue

***Cenário 16: trilha encerrada (fluxo alternativo E)***

> **Dado que** o TCC 1 passou a Reprovado após a defesa
>
> **Quando** o Aluno abre a trilha do Status do TCC
>
> **Então** a trilha termina em Reprovado, sem a etapa Aprovado para TCC
> 2

***Cenário 17: acesso sem estar autenticado (E1)***

> **Dado que** o Aluno não está autenticado
>
> **Quando** tenta abrir a aba Meu TCC
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre a aba Meu TCC com o Status atual

***Cenário 18: sem edição manual (E2)***

> **Dado que** o Professor da Disciplina abre o painel de um aluno
>
> **Quando** procura alterar o Status do TCC
>
> **Então** o Status aparece apenas como etiqueta, sem campo nem botão
> de edição

***Cenário 19: usuário sem vínculo com o trabalho (E3)***

> **Dado que** um Docente não é o Orientador do aluno nem o Professor da
> Disciplina da turma
>
> **Quando** tenta abrir o histórico desse TCC
>
> **Então** o sistema não exibe o histórico nem a trilha

**Tela no protótipo**

**Tela:** Meu TCC aluno



**Tela:** Histórico do Status do TCC



**Diagrama de sequência**

**Diagrama relacionado:** sem diagrama próprio: as transições aparecem
como passos nos diagramas "Proposta e entrega" e "Lançamento de notas e
liberação do resultado".

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[x\] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-43 Cadastrar as entregas da turma

| **Épico:**                | Cadastro e Manutenção            |
|---------------------------|----------------------------------|
| **Feature:**              | Fluxo do TCC e Entregas          |
| **Requisitos da matriz:** | RBN-CAD-09.1, RBN-CAD-09.6       |
| **Prioridade (MoSCoW):**  | Must Have (CAD-09.6: Could Have) |
| **Responsável:**          | Leandra Matos                    |

**Descrição**

Como Professor da Disciplina, quero cadastrar as entregas da minha
turma, com tipo, título, instruções e Data Limite, para que os alunos
saibam o que devem enviar e até quando.

**Atores**

> **Ator principal:** Professor da Disciplina responsável pela turma.
>
> **Atores secundários:** Alunos da turma, que recebem a notificação da
> nova entrega.

**Pré-condições**

- O Professor da Disciplina está autenticado, com o Status da Conta
  > Ativa (US-11). Sem sessão ativa, aplica-se o E1.

- O Professor é o Professor da Disciplina da turma, e a turma não está
  > arquivada. Com a turma arquivada, aplica-se o E4; para outro
  > docente, aplica-se o E5.

**Fluxo principal**

> 1\. No menu lateral do sistema, o Professor da Disciplina acessa o
> item Turmas, seleciona a turma e abre a aba Atividades.
>
> 2\. O sistema exibe a lista de entregas já cadastradas e o botão
> Cadastrar atividade.
>
> 3\. O Professor aciona o botão Cadastrar atividade. O sistema abre a
> janela Cadastrar atividade com os campos Título, Tipo, Instruções e
> Data Limite e os botões Cancelar e Cadastrar.
>
> 4\. O Professor informa o Título (obrigatório, até 100 caracteres,
> ex.: Entrega do Documento) e seleciona o Tipo na lista (Proposta,
> Documento para Defesa, Versão Final ou Outra; neste fluxo, Documento
> para Defesa).
>
> 5\. O Professor informa as Instruções (opcional, até 1.000
> caracteres), seleciona a Data Limite no calendário (DD/MM/AAAA; o
> prazo vale até 23:59) e aciona o botão Cadastrar.
>
> 6\. O sistema valida os campos (E2 e E3), cria a entrega com o status
> de envio Aguardando Envio para cada aluno da turma e fecha a janela.
>
> 7\. O sistema envia a cada aluno da turma uma notificação no sistema e
> um e-mail com o Título e a Data Limite.
>
> 8\. O sistema mantém o Professor na aba Atividades, com a mensagem
> "Entrega cadastrada" e a nova entrega na lista. O fluxo termina.

**Fluxos alternativos**

> A. Tipos por etapa (passo 4): em turma de TCC 1, a lista Tipo exibe
> Proposta, Documento para Defesa e Outra; em turma de TCC 2, Documento
> para Defesa, Versão Final e Outra. O fluxo prossegue a partir do passo
> 5.
>
> B. Entrega do tipo Proposta (passo 6): a entrega é criada sem campo de
> link para o aluno, porque é cumprida quando o aluno salva a Proposta
> (US-13). O fluxo prossegue a partir do passo 7.
>
> C. Entrega do tipo Versão Final (passo 6): a Data Limite define o
> prazo pós-banca para a entrega do texto final corrigido (US-29). O
> fluxo prossegue a partir do passo 7.
>
> D. Cancelamento do cadastro (passo 5): o Professor aciona o botão
> Cancelar. A janela fecha e nenhuma entrega é criada. O fluxo termina.
>
> E. Aluno vinculado após o cadastro da entrega (passo 6): quando um
> aluno é vinculado à turma depois do cadastro (US-08), o sistema cria
> para ele a entrega com o status de envio Aguardando Envio ou, se a
> Data Limite já venceu, Não Entregue (CAD-09.3). O fluxo termina.
>
> F. Entrega do tipo Proposta cadastrada após o salvamento da Proposta
> (passo 6): para o aluno que já salvou a Proposta (US-13), o sistema
> cria a entrega com o status de envio Entregue, considerando a data e a
> hora do salvamento (CAD-07.1). O fluxo prossegue a partir do passo 7.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o Professor da Disciplina
> tente acessar a aba Atividades da turma sem sessão ativa (pelo menu,
> pelo endereço da página ou por um link recebido), o sistema apresenta
> a tela de login (US-11). Após a autenticação, o sistema exibe a aba
> Atividades da turma, e o fluxo prossegue a partir do passo 2. Em caso
> de falha na autenticação, aplicam-se as exceções da US-11.
>
> E2. Cadastro inválido (passo 6): Título em branco ou com mais de 100
> caracteres, Instruções com mais de 1.000 caracteres, Data Limite em
> branco ou anterior à data do cadastro. O sistema não salva, destaca o
> campo e informa o motivo. Retorna ao passo 4.
>
> E3. Tipo repetido (passo 6): a turma já tem uma entrega do tipo
> Proposta, Documento para Defesa ou Versão Final. O sistema não salva e
> exibe "A turma já tem uma entrega deste tipo". Retorna ao passo 4.
>
> E4. Turma arquivada (passo 2): a aba Atividades permanece disponível
> apenas para consulta, sem o botão Cadastrar atividade. O fluxo
> termina.
>
> E5. Usuário que não é o Professor da Disciplina da turma (passo 2): o
> botão Cadastrar atividade não aparece. O fluxo termina.

**Pós-condições**

- A entrega foi cadastrada na turma com o status de envio Aguardando
  > Envio para cada aluno.

- Os alunos da turma foram notificados no sistema e por e-mail.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                         | **Resumo da regra em uma frase**                                                                                                                                                |
|--------------|---------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-09.1** | O sistema deve mostrar um formulário de cadastro de entrega que deve conter os campos Tipo, Título, Instruções e Data Limite.   | Cadastro de entrega com Tipo (Proposta, Documento para Defesa, Versão Final ou Outra, no máximo uma de cada um dos três primeiros por turma), Título, Instruções e Data Limite. |
| **CAD-09.6** | O sistema deve notificar os alunos sobre nova entrega e sobre o prazo de entrega, e o Professor da Disciplina sobre cada envio. | Notificações de nova entrega, de prazo (7 dias, 48 horas e 24 horas antes) e de cada envio; sem lembretes em turma arquivada.                                                   |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. A entrega tem Tipo, Título, Instruções e Data Limite; a turma tem
> no máximo uma entrega de cada um dos tipos Proposta, Documento para
> Defesa e Versão Final.
>
> 2\. Ao cadastrar, cada aluno da turma é notificado e fica com o status
> Aguardando Envio.

***Cenário 1: cadastro da entrega (fluxo principal)***

> **Dado que** o Professor da Disciplina está autenticado e na aba
> Atividades da turma TCC 2 · ECP08_LOBATO
>
> **Quando** aciona o botão Cadastrar atividade, informa o Título
> Entrega do Documento, o Tipo Documento para Defesa e a Data Limite
> 25/09/2026 e aciona o botão Cadastrar
>
> **Então** a entrega aparece na aba Atividades com o status Aguardando
> Envio para cada aluno e o sistema exibe "Entrega cadastrada"
>
> **E** cada aluno recebe a notificação no sistema e o e-mail com o
> Título e a Data Limite

***Cenário 2: tipos por etapa (fluxo alternativo A)***

> **Dado que** o Professor da Disciplina está cadastrando uma entrega em
> turma de TCC 1
>
> **Quando** abre a lista Tipo
>
> **Então** a lista exibe Proposta, Documento para Defesa e Outra, sem
> Versão Final

***Cenário 3: entrega do tipo Proposta (fluxo alternativo B)***

> **Dado que** o Professor da Disciplina cadastra uma entrega do tipo
> Proposta em turma de TCC 1
>
> **Quando** aciona o botão Cadastrar
>
> **Então** a entrega é criada sem campo de link para os alunos

***Cenário 4: entrega do tipo Versão Final (fluxo alternativo C)***

> **Dado que** o Professor da Disciplina cadastra uma entrega do tipo
> Versão Final em turma de TCC 2 com Data Limite 30/11
>
> **Quando** aciona o botão Cadastrar
>
> **Então** a Data Limite 30/11 passa a ser o prazo de envio da Versão
> Final

***Cenário 5: cancelamento do cadastro (fluxo alternativo D)***

> **Dado que** o Professor da Disciplina está na janela Cadastrar
> atividade
>
> **Quando** aciona o botão Cancelar
>
> **Então** a janela fecha e nenhuma entrega é criada

***Cenário 6: aluno vinculado após o cadastro da entrega (fluxo
alternativo E)***

> **Dado que** a turma tem a entrega Entrega do Documento com Data
> Limite 25/09/2026
>
> **Quando** um aluno é vinculado à turma em 20/09/2026
>
> **Então** a entrega aparece para esse aluno com o status Aguardando
> Envio

***Cenário 7: entrega do tipo Proposta após o salvamento da***
***Proposta*** ***(fluxo alternativo F)***

> **Dado que** um aluno da turma de TCC 1 salvou a Proposta em 02/09
>
> **Quando** o Professor da Disciplina cadastra, em 05/09, a entrega do
> tipo Proposta
>
> **Então** a entrega desse aluno é criada com o status Entregue

***Cenário 8: acesso sem estar autenticado (E1)***

> **Dado que** o Professor da Disciplina não está autenticado
>
> **Quando** tenta abrir a aba Atividades da turma
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre a aba Atividades da turma

***Cenário 9: cadastro inválido (E2)***

> **Dado que** o Professor da Disciplina está na janela Cadastrar
> atividade
>
> **Quando** seleciona uma Data Limite anterior à data de hoje e aciona
> o botão Cadastrar
>
> **Então** o sistema não salva e destaca a Data Limite

***Cenário 10: tipo repetido (E3)***

> **Dado que** a turma já tem uma entrega do tipo Documento para Defesa
>
> **Quando** o Professor da Disciplina cadastra outra entrega desse tipo
>
> **Então** o sistema não salva e exibe "A turma já tem uma entrega
> deste tipo"

***Cenário 11: turma arquivada (E4)***

> **Dado que** a turma foi arquivada
>
> **Quando** o Professor da Disciplina abre a aba Atividades
>
> **Então** as entregas aparecem apenas para consulta, sem o botão
> Cadastrar atividade

***Cenário 12: usuário sem permissão (E5)***

> **Dado que** um Docente não é o Professor da Disciplina da turma
>
> **Quando** abre a turma
>
> **Então** o botão Cadastrar atividade não aparece

**Tela no protótipo**

**Tela:** Turma aba de entregas



**Tela:** Cadastro de entrega  


**Diagrama de sequência**

**Diagrama relacionado:** Proposta e entrega

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[x\] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-15 Enviar ou substituir o link de uma entrega

| **Épico:**                | Cadastro e Manutenção                    |
|---------------------------|------------------------------------------|
| **Feature:**              | Fluxo do TCC e Entregas                  |
| **Requisitos da matriz:** | RBN-CAD-09.2, RBN-CAD-09.3, RBN-CAD-09.6 |
| **Prioridade (MoSCoW):**  | Must Have (CAD-09.6: Could Have)         |
| **Responsável:**          | Leandra Matos                            |

**Descrição**

Como Aluno, quero enviar e, até a Data Limite, substituir o link das
entregas da minha turma, sendo lembrado do prazo, para que o meu envio
fique registrado e seja acompanhado pelo Professor da Disciplina.

**Atores**

> **Ator principal:** Aluno.
>
> **Atores secundários:** Professor da Disciplina, que recebe a
> notificação de cada envio e de cada substituição.

**Pré-condições**

- O Aluno está autenticado, com o Status da Conta Ativa (US-11). Sem
  > sessão ativa, aplica-se o E1.

- O Aluno está vinculado a uma turma não arquivada, e a entrega foi
  > cadastrada pelo Professor da Disciplina (US-43). Com a turma
  > arquivada, aplica-se o E6.

- Nas entregas do tipo Documento para Defesa e Outra, o TCC do Aluno
  > está com o Status Em Andamento; com outro Status, aplica-se o E4 ou
  > o E5. A entrega do tipo Versão Final é tratada na US-29, e a do tipo
  > Proposta, na US-13.

**Fluxo principal**

> 1\. No menu lateral do sistema, o Aluno acessa o item Turmas,
> seleciona a sua turma e abre a aba Atividades.
>
> 2\. O sistema lista as entregas da turma com Título, Data Limite e o
> status de envio do Aluno.
>
> 3\. O Aluno seleciona a entrega Entrega do Documento. O sistema abre a
> janela da entrega com Título, Data Limite, Instruções, status de envio
> (Aguardando Envio), o campo Link e os botões Cancelar e Enviar.
>
> 4\. O Aluno insere no campo Link o endereço do arquivo (obrigatório,
> iniciado por https://, até 500 caracteres, com acesso público, ex.:
> https://drive.google.com/...) e aciona o botão Enviar.
>
> 5\. O sistema valida o link (E2), registra o envio com o aluno, a data
> e a hora e calcula o status de envio: Entregue, porque o primeiro
> envio ocorreu até 23:59 da Data Limite.
>
> 6\. O sistema envia ao Professor da Disciplina uma notificação no
> sistema com o envio.
>
> 7\. O sistema fecha a janela e mantém o Aluno na aba Atividades, com a
> mensagem "Entrega enviada" e o status Entregue ao lado da entrega. O
> fluxo termina.

**Fluxos alternativos**

> A. Acesso pela notificação (passo 1): o Aluno seleciona o ícone de
> notificações (sino), no canto superior direito, e, em seguida, a
> notificação da nova entrega. O sistema abre a aba Atividades da turma.
> O e-mail da nova entrega (fora do sistema) apenas informa o Título e a
> Data Limite; para realizar o envio, o Aluno precisa acessar o sistema.
> O fluxo prossegue a partir do passo 2.
>
> B. Envio após a Data Limite (passo 5): o primeiro envio ocorre após as
> 23:59 da Data Limite. O sistema aceita o link e registra o status
> Entregue com Atraso. O fluxo prossegue a partir do passo 6.
>
> C. Prazo vencido sem envio (passo 1): quando passa das 23:59 da Data
> Limite e o Aluno não enviou, o sistema muda o status para Não
> Entregue. O envio permanece permitido e, caso ocorra, segue o fluxo
> alternativo B. O fluxo termina.
>
> D. Substituição do link até a Data Limite (passo 3): o Aluno abre a
> entrega já enviada, substitui o endereço no campo Link e aciona o
> botão Enviar. O sistema registra a substituição com a data e a hora,
> mantém o status calculado pelo primeiro envio e notifica o Professor
> da Disciplina no sistema. O fluxo prossegue a partir do passo 7.
>
> E. Lembretes de prazo (Could Have) (passo 1): 7 dias, 48 horas e 24
> horas antes da Data Limite, o sistema envia notificação no sistema e
> e-mail apenas aos alunos que ainda não enviaram. Em turma arquivada,
> os lembretes não são enviados. O fluxo prossegue a partir do passo 1.
>
> F. Entrega do tipo Proposta (passo 3): a janela da entrega não tem o
> campo Link e exibe o status e o aviso "Esta entrega é cumprida ao
> salvar a Proposta" (US-13). O fluxo termina.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o Aluno tente acessar a
> aba Atividades da turma sem sessão ativa (pelo menu, pelo endereço da
> página ou por um link recebido), o sistema apresenta a tela de login
> (US-11). Após a autenticação, o sistema exibe a aba Atividades da
> turma, e o fluxo prossegue a partir do passo 2. Em caso de falha na
> autenticação, aplicam-se as exceções da US-11.
>
> E2. Link inválido (passo 5): o campo Link está vazio, não começa com
> https:// ou tem mais de 500 caracteres. O sistema não salva e exibe "O
> link deve começar com https:// e ter até 500 caracteres". Retorna ao
> passo 4.
>
> E3. Substituição após a Data Limite (passo 3): o campo Link aparece
> apenas para leitura, sem o botão Enviar, e o status não muda. O fluxo
> termina.
>
> E4. TCC fora de Em Andamento (passo 3): nas entregas do tipo Documento
> para Defesa e Outra, se o TCC não está Em Andamento (por exemplo, Apto
> para Defesa), o campo Link aparece apenas para leitura, sem o botão
> Enviar. O fluxo termina.
>
> E5. Aluno com o Status Desistente, Reprovado ou Jubilado (CAD-08.5;
> passo 3): o Aluno pode acessar a aba Atividades, mas o botão Enviar
> permanece desabilitado. O fluxo termina.
>
> E6. Turma arquivada (passo 2): a aba Atividades permanece disponível
> apenas para consulta, sem o botão Enviar. O fluxo termina.

**Pós-condições**

- O envio foi registrado com o aluno, a data e a hora, e o status de
  > envio passou a Entregue ou Entregue com Atraso.

- Na substituição, o novo link e a substituição foram registrados, e o
  > status calculado pelo primeiro envio foi mantido.

- O Professor da Disciplina foi notificado.

- O Status do TCC não foi alterado pelo atraso (US-14).

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                                                                                                 | **Resumo da regra em uma frase**                                                                                                                                                      |
|--------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-09.2** | O sistema deve mostrar um formulário de envio da entrega que deve conter o campo Link.                                                                                                                                                  | Envio por link https:// (na Versão Final, PDF com a Folha de Aprovação e a ficha catalográfica); a troca do link é permitida até a Data Limite e vale o primeiro envio para o status. |
| **CAD-09.3** | O sistema deve registrar automaticamente o status de envio de cada aluno na entrega, com um dos valores: Aguardando Envio, Entregue, Entregue com Atraso, Não Entregue e, somente na Versão Final, Devolvida para Ajuste ou Homologada. | Status de envio: Aguardando Envio, Entregue, Entregue com Atraso, Não Entregue e, na Versão Final, Devolvida para Ajuste ou Homologada; o atraso não muda o Status do TCC.            |
| **CAD-09.6** | O sistema deve notificar os alunos sobre nova entrega e sobre o prazo de entrega, e o Professor da Disciplina sobre cada envio.                                                                                                         | Notificações de nova entrega, de prazo (7 dias, 48 horas e 24 horas antes) e de cada envio; sem lembretes em turma arquivada.                                                         |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Apenas URLs (ex: https://...).
>
> 2\. Sistema registra automaticamente o status de envio: "Entregue",
> "Entregue com Atraso" ou "Não Entregue", com base na data do primeiro
> envio e na Data Limite da entrega.

***Cenário 1: envio no prazo (fluxo principal)***

> **Dado que** existe a entrega do tipo Documento para Defesa com Data
> Limite 20/11 e o TCC está Em Andamento
>
> **Quando** o Aluno abre a entrega na aba Atividades, informa um link
> https:// e aciona o botão Enviar em 18/11
>
> **Então** o envio é registrado com a data e a hora, o status passa a
> Entregue e o sistema exibe "Entrega enviada"
>
> **E** o Professor da Disciplina recebe a notificação no sistema

***Cenário 2: acesso pela notificação (fluxo alternativo A)***

> **Dado que** o Aluno está autenticado e recebeu a notificação da nova
> entrega
>
> **Quando** seleciona o ícone de notificações (sino) e, em seguida, a
> notificação
>
> **Então** o sistema abre a aba Atividades da turma com a nova entrega

***Cenário 3: envio com atraso (fluxo alternativo B)***

> **Dado que** a Data Limite da entrega foi 20/11
>
> **Quando** o Aluno envia o link em 21/11
>
> **Então** o envio é aceito e o status passa a Entregue com Atraso

***Cenário 4: prazo vencido sem envio (fluxo alternativo C)***

> **Dado que** o Aluno não enviou o link
>
> **Quando** passa das 23:59 da Data Limite
>
> **Então** o status muda para Não Entregue e o envio permanece
> disponível

***Cenário 5: substituição do link no prazo (fluxo alternativo D)***

> **Dado que** o Aluno enviou o link em 18/11 e a Data Limite é 20/11
>
> **Quando** substitui o link em 19/11 e aciona o botão Enviar
>
> **Então** o sistema grava o novo link e a substituição, o status
> permanece Entregue e o Professor da Disciplina é notificado

***Cenário 6: lembrete de prazo (fluxo alternativo E)***

> **Dado que** faltam 48 horas para a Data Limite e o Aluno não enviou o
> link
>
> **Quando** o sistema verifica os prazos
>
> **Então** o Aluno recebe o lembrete no sistema e por e-mail

***Cenário 7: entrega do tipo Proposta (fluxo alternativo F)***

> **Dado que** a turma de TCC 1 tem uma entrega do tipo Proposta
>
> **Quando** o Aluno abre essa entrega na aba Atividades
>
> **Então** a janela não tem o campo Link e exibe "Esta entrega é
> cumprida ao salvar a Proposta"

***Cenário 8: acesso sem estar autenticado (E1)***

> **Dado que** o Aluno não está autenticado
>
> **Quando** tenta abrir a aba Atividades da turma
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre a aba Atividades da turma

***Cenário 9: link inválido (E2)***

> **Dado que** o Aluno está na janela da entrega
>
> **Quando** informa um endereço sem https:// e aciona o botão Enviar
>
> **Então** o sistema não salva e exibe "O link deve começar com
> https:// e ter até 500 caracteres"

***Cenário 10: substituição após o prazo (E3)***

> **Dado que** o Aluno enviou o link em 18/11 e a Data Limite foi 20/11
>
> **Quando** abre a entrega em 22/11
>
> **Então** o campo Link aparece apenas para leitura, sem o botão
> Enviar, e o status permanece Entregue

***Cenário 11: TCC fora de Em Andamento (E4)***

> **Dado que** o TCC do Aluno está Apto para Defesa
>
> **Quando** o Aluno abre uma entrega do tipo Outra
>
> **Então** o campo Link aparece apenas para leitura, sem o botão Enviar

***Cenário 12: aluno Jubilado (E5)***

> **Dado que** o TCC do Aluno está com o Status Jubilado
>
> **Quando** o Aluno abre uma entrega da turma
>
> **Então** o botão Enviar aparece desabilitado

***Cenário 13: turma arquivada (E6)***

> **Dado que** a turma foi arquivada
>
> **Quando** o Aluno abre a aba Atividades
>
> **Então** as entregas aparecem apenas para consulta, sem o botão
> Enviar

**Tela no protótipo**

**Tela:** Aba de entregas da turma visão aluno



**Tela:** Entrega de entrega



**Diagrama de sequência**

**Diagrama relacionado:** Proposta e entrega

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[x\] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-16 Acompanhar as entregas dos alunos da turma

| **Épico:**                | Cadastro e Manutenção   |
|---------------------------|-------------------------|
| **Feature:**              | Fluxo do TCC e Entregas |
| **Requisitos da matriz:** | RBN-CAD-09.4            |
| **Prioridade (MoSCoW):**  | Must Have               |
| **Responsável:**          | Leandra Matos           |

**Descrição**

Como Professor da Disciplina, quero acompanhar, por aluno, o status de
envio e o link de cada entrega da minha turma, para saber quem já enviou
e consultar o material enviado.

**Atores**

> **Ator principal:** Professor da Disciplina responsável pela turma.
>
> **Atores secundários:** Não há atores secundários.

**Pré-condições**

- O Professor da Disciplina está autenticado, com o Status da Conta
  > Ativa (US-11). Sem sessão ativa, aplica-se o E1.

- O Professor é o Professor da Disciplina da turma. Para outro docente,
  > aplica-se o E2.

- A turma tem pelo menos uma entrega cadastrada (US-43). Sem entregas,
  > aplica-se o E3.

**Fluxo principal**

> 1\. No menu lateral do sistema, o Professor da Disciplina acessa o
> item Turmas e seleciona a turma.
>
> 2\. O sistema abre a tela da turma. O Professor seleciona a aba
> Atividades.
>
> 3\. O sistema lista as entregas da turma com Título, Tipo e Data
> Limite.
>
> 4\. O Professor seleciona uma entrega (ex.: Entrega do Documento, do
> tipo Documento para Defesa).
>
> 5\. O sistema abre a janela da entrega com Título, Data Limite e
> Instruções e uma tabela somente leitura, com uma linha por aluno da
> turma e as colunas Aluno (nome e matrícula), Status de envio e Link
> (endereço mais recente, com a data e a hora do envio).
>
> 6\. O Professor acessa o link de um aluno. O arquivo abre fora do
> SIGTCC, no serviço em que o aluno o publicou (ex.: Google Drive).
>
> 7\. O Professor aciona o botão Fechar e retorna à aba Atividades da
> turma. O fluxo termina.

**Fluxos alternativos**

> A. Aluno sem envio (passo 5): a linha exibe Aguardando Envio (prazo
> não vencido) ou Não Entregue (prazo vencido) e a coluna Link vazia.
> Não há reprovação automática nem mudança no Status do TCC. O fluxo
> prossegue a partir do passo 7.
>
> B. Envio com atraso (passo 5): a linha exibe Entregue com Atraso e o
> link. O fluxo prossegue a partir do passo 6.
>
> C. Entrega do tipo Proposta (passo 6): no lugar do link, a linha exibe
> Ver Proposta, que abre a Proposta registrada pelo aluno, somente
> leitura (US-13). O fluxo prossegue a partir do passo 7.
>
> D. Turma arquivada (passo 1): no menu lateral, o Professor acessa o
> item Turmas arquivadas e seleciona a turma e segue os passos 2 a 7,
> apenas para consulta.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o Professor da Disciplina
> tente acessar a aba Atividades da turma sem sessão ativa (pelo menu,
> pelo endereço da página ou por um link recebido), o sistema apresenta
> a tela de login (US-11). Após a autenticação, o sistema exibe a aba
> Atividades da turma, e o fluxo prossegue a partir do passo 3. Em caso
> de falha na autenticação, aplicam-se as exceções da US-11.
>
> E2. Usuário que não é o Professor da Disciplina da turma (passo 4): o
> sistema não exibe a janela de acompanhamento da entrega. O fluxo
> termina.
>
> E3. Turma sem entregas (passo 3): a aba Atividades exibe "Nenhuma
> entrega cadastrada" e o botão Cadastrar atividade (US-43). O fluxo
> termina.

**Pós-condições**

- Nenhum dado foi alterado: a consulta é somente leitura e não registra
  > nota nem parecer.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                    | **Resumo da regra em uma frase**                                                                           |
|--------------|--------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|
| **CAD-09.4** | O sistema deve exibir ao Professor da Disciplina o acompanhamento das entregas, por aluno. | Lista por aluno com o status de envio e o link; na entrega do tipo Proposta, mostra a Proposta registrada. |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Lista somente leitura com o status de envio e o link de cada
> aluno.
>
> 2\. Sem julgamento da entrega: quem não envia fica como "Não
> Entregue", sem reprovação automática.

***Cenário 1: acompanhamento da entrega (fluxo principal)***

> **Dado que** a turma tem 3 alunos e 2 enviaram o link da entrega do
> tipo Documento para Defesa
>
> **Quando** o Professor da Disciplina abre a aba Atividades e seleciona
> a entrega
>
> **Então** o sistema exibe 3 linhas, duas com o status Entregue e o
> link e uma com Aguardando Envio

***Cenário 2: aluno sem envio após o prazo (fluxo alternativo A)***

> **Dado que** a Data Limite venceu e um aluno não enviou
>
> **Quando** o Professor da Disciplina abre a entrega
>
> **Então** a linha do aluno exibe Não Entregue, sem link e sem mudança
> no Status do TCC

***Cenário 3: envio com atraso (fluxo alternativo B)***

> **Dado que** um aluno enviou o link um dia após a Data Limite
>
> **Quando** o Professor da Disciplina abre a entrega
>
> **Então** a linha do aluno exibe Entregue com Atraso e o link

***Cenário 4: entrega do tipo Proposta (fluxo alternativo C)***

> **Dado que** a turma de TCC 1 tem a entrega do tipo Proposta e o aluno
> salvou a Proposta
>
> **Quando** o Professor da Disciplina abre a entrega e aciona o botão
> Ver Proposta na linha do aluno
>
> **Então** o sistema exibe a Proposta do aluno somente para leitura

***Cenário 5: turma arquivada (fluxo alternativo D)***

> **Dado que** a turma foi arquivada
>
> **Quando** o Professor da Disciplina abre a turma em Turmas arquivadas
> e seleciona uma entrega
>
> **Então** a lista aparece apenas para consulta

***Cenário 6: acesso sem estar autenticado (E1)***

> **Dado que** o Professor da Disciplina não está autenticado
>
> **Quando** tenta abrir a aba Atividades da turma
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre a aba Atividades da turma

***Cenário 7: acesso restrito (E2)***

> **Dado que** um Docente não é o Professor da Disciplina da turma
>
> **Quando** tenta abrir o acompanhamento da entrega
>
> **Então** o sistema não exibe a lista

***Cenário 8: turma sem entregas (E3)***

> **Dado que** a turma ainda não tem entregas cadastradas
>
> **Quando** o Professor da Disciplina abre a aba Atividades
>
> **Então** o sistema exibe "Nenhuma entrega cadastrada" e o botão
> Cadastrar atividade

**Tela no protótipo**

**Tela:** Acompanhamento de entregas da atividade



**Tela:** Acompanhamento de entregas da atividade do tipo Proposta



Tela: Proposta a partir do acompanhamento de entregas da atividade



**Diagrama de sequência**

**Diagrama relacionado:** sem diagrama próprio: é uma consulta somente
leitura; os envios vêm do diagrama "Proposta e entrega".

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[x\] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-29 Enviar a Versão Final do TCC 2

| **Épico:**                | Cadastro e Manutenção      |
|---------------------------|----------------------------|
| **Feature:**              | Fluxo do TCC e Entregas    |
| **Requisitos da matriz:** | RBN-CAD-09.2, RBN-CAD-09.3 |
| **Prioridade (MoSCoW):**  | Must Have                  |
| **Responsável:**          | Leandra Matos              |

**Descrição**

Como Aluno, quero enviar o link da Versão Final corrigida do TCC 2, com
a Folha de Aprovação assinada e a ficha catalográfica, para que ela seja
homologada e o TCC seja concluído.

**Atores**

> **Ator principal:** Aluno.
>
> **Atores secundários:** Professor da Disciplina, que recebe a
> notificação do envio.

**Pré-condições**

- A banca liberou o resultado do TCC 2 com o parecer Aprovado ou
  > Aprovado com Correções (US-27), e a Folha de Aprovação está
  > disponível ao Aluno (US-28). Antes da liberação, aplica-se o E3; com
  > o parecer Reprovado, o E7.

- A turma de TCC 2 tem a entrega do tipo Versão Final cadastrada pelo
  > Professor da Disciplina, com a Data Limite (US-43).

- O Aluno está autenticado, com o Status da Conta Ativa (US-11). Sem
  > sessão ativa, aplica-se o E1.

**Fluxo principal**

> 1\. No menu lateral do sistema, o Aluno acessa o item Turmas,
> seleciona a sua turma de TCC 2 e abre a aba Meu TCC.
>
> 2\. O sistema exibe, na seção Defesa, a nota final, o parecer e a Data
> Limite da Versão Final, com os botões Ata Final e Folha de Aprovação,
> e, na seção Versão final, o status de envio Aguardando Envio, o campo
> Link da Versão Final e o botão Enviar.
>
> 3\. O Aluno aciona o botão Folha de Aprovação, e o sistema baixa o
> arquivo (US-28).
>
> 4\. Fora do sistema, o Aluno faz as correções pedidas pela banca e
> monta um único PDF com o texto final corrigido, a Folha de Aprovação
> assinada e a ficha catalográfica, publicado com acesso público (ex.:
> Google Drive).
>
> 5\. No sistema, na seção Versão final, o Aluno insere no campo Link da
> Versão Final o endereço do PDF (obrigatório, iniciado por https://,
> até 500 caracteres) e aciona o botão Enviar.
>
> 6\. O sistema valida o link (E2), registra o envio com a data e a
> hora, muda o status de envio para Entregue (envio até 23:59 da Data
> Limite) e notifica o Professor da Disciplina no sistema.
>
> 7\. O sistema mantém o Aluno na aba Meu TCC, com a mensagem "Versão
> Final enviada" e o status Entregue. A homologação segue na US-44. O
> fluxo termina.

**Fluxos alternativos**

> A. Parecer Aprovado, sem correções (passo 4): o Aluno monta o PDF sem
> alterações no texto, apenas com a Folha de Aprovação assinada e a
> ficha catalográfica. O fluxo prossegue a partir do passo 5.
>
> B. Envio após a Data Limite (passo 6): após as 23:59 da Data Limite, a
> seção Versão final exibe o aviso "Data Limite vencida: o envio será
> registrado como Entregue com Atraso", e o sistema registra Entregue
> com Atraso. O fluxo prossegue a partir do passo 7.
>
> C. Prazo vencido sem link (passo 1): o status de envio passa a Não
> Entregue, o Status do TCC não muda (permanece Aprovado ou Aprovado com
> Correções) e o Aluno ainda pode enviar, com atraso. O fluxo termina.
>
> D. Substituição do link antes da Data Limite (passo 5): o Aluno
> substitui o endereço no campo Link da Versão Final e aciona o botão
> Enviar. O sistema registra a substituição com a data e a hora, mantém
> o status calculado pelo primeiro envio e notifica o Professor da
> Disciplina no sistema (CAD-09.6). O fluxo prossegue a partir do passo
> 7.
>
> E. Reenvio após devolução para ajuste (passo 2): quando o Professor da
> Disciplina devolve a Versão Final (US-44), a seção Versão final exibe
> o status Devolvida para Ajuste e a mensagem do Professor. O Aluno
> substitui o link e aciona o botão Enviar, e o status retorna a
> Entregue ou Entregue com Atraso, conforme a Data Limite. O fluxo
> prossegue a partir do passo 6.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o Aluno tente acessar a
> aba Meu TCC sem sessão ativa (pelo menu, pelo endereço da página ou
> por um link recebido), o sistema apresenta a tela de login (US-11).
> Após a autenticação, o sistema exibe a aba Meu TCC da turma de TCC 2,
> e o fluxo prossegue a partir do passo 2. Em caso de falha na
> autenticação, aplicam-se as exceções da US-11.
>
> E2. Link inválido (passo 6): o campo Link da Versão Final está vazio,
> não começa com https:// ou tem mais de 500 caracteres. O sistema não
> salva e exibe "O link deve começar com https:// e ter até 500
> caracteres". Retorna ao passo 5.
>
> E3. Resultado ainda não liberado (passo 2): a seção Versão final exibe
> "Disponível após a liberação do resultado", sem o campo Link da Versão
> Final. O fluxo termina.
>
> E4. TCC 1 (passo 2): a turma de TCC 1 não tem a entrega do tipo Versão
> Final, e a aba Meu TCC não exibe a seção Versão final. O fluxo
> termina.
>
> E5. Substituição após a Data Limite (passo 5): com o link já enviado e
> fora da devolução para ajuste, após as 23:59 da Data Limite o campo
> Link da Versão Final aparece apenas para leitura, sem o botão Enviar,
> e o status não muda. O fluxo termina.
>
> E6. Versão Final homologada (passo 2): com o status de envio
> Homologada (US-44), a seção Versão final exibe o link apenas para
> leitura, sem o botão Enviar. O fluxo termina.
>
> E7. Parecer Reprovado (passo 2): com o Status do TCC Reprovado, a aba
> Meu TCC não exibe o campo Link da Versão Final, porque a entrega só
> fica disponível com o Status Aprovado ou Aprovado com Correções
> (CAD-09.2). O fluxo termina.

**Pós-condições**

- O envio da Versão Final foi registrado com a data e a hora, e o status
  > de envio passou a Entregue ou Entregue com Atraso.

- O Professor da Disciplina foi notificado do envio.

- O Status do TCC não foi alterado pelo envio nem pelo atraso.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                                                                                                 | **Resumo da regra em uma frase**                                                                                                                                                      |
|--------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-09.2** | O sistema deve mostrar um formulário de envio da entrega que deve conter o campo Link.                                                                                                                                                  | Envio por link https:// (na Versão Final, PDF com a Folha de Aprovação e a ficha catalográfica); a troca do link é permitida até a Data Limite e vale o primeiro envio para o status. |
| **CAD-09.3** | O sistema deve registrar automaticamente o status de envio de cada aluno na entrega, com um dos valores: Aguardando Envio, Entregue, Entregue com Atraso, Não Entregue e, somente na Versão Final, Devolvida para Ajuste ou Homologada. | Status de envio: Aguardando Envio, Entregue, Entregue com Atraso, Não Entregue e, na Versão Final, Devolvida para Ajuste ou Homologada; o atraso não muda o Status do TCC.            |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. A Versão Final é uma entrega da turma, enviada por link de um
> único PDF com a Folha de Aprovação assinada e a ficha catalográfica.
>
> 2\. Link submetido atrasado gera tag "Entregue com Atraso".

***Cenário 1: Versão Final enviada no prazo (fluxo principal)***

> **Dado que** o TCC 2 foi aprovado com correções e a Data Limite da
> Versão Final é 30/11
>
> **Quando** o Aluno informa o link do PDF final na seção Versão final e
> aciona o botão Enviar em 25/11
>
> **Então** o envio é registrado, o status passa a Entregue e o sistema
> exibe "Versão Final enviada"
>
> **E** o Professor da Disciplina recebe a notificação no sistema

***Cenário 2: parecer Aprovado, sem correções (fluxo alternativo A)***

> **Dado que** o TCC 2 foi aprovado sem correções
>
> **Quando** o Aluno envia o link do PDF com a Folha de Aprovação
> assinada e a ficha catalográfica
>
> **Então** o envio é registrado com o status Entregue

***Cenário 3: envio com atraso (fluxo alternativo B)***

> **Dado que** a Data Limite da Versão Final já passou
>
> **Quando** o Aluno envia o link
>
> **Então** o envio é aceito com o status Entregue com Atraso

***Cenário 4: prazo vencido sem link (fluxo alternativo C)***

> **Dado que** o TCC 2 está Aprovado e sem link da Versão Final
>
> **Quando** vence a Data Limite da entrega do tipo Versão Final
>
> **Então** o status de envio passa a Não Entregue e o Status do TCC
> permanece Aprovado

***Cenário 5: substituição do link antes da Data Limite (fluxo
alternativo D)***

> **Dado que** o Aluno enviou o link em 20/11 e a Data Limite é 30/11
>
> **Quando** substitui o link em 22/11 e aciona o botão Enviar
>
> **Então** o sistema grava o novo link e a substituição, e o status
> permanece Entregue

***Cenário 6: reenvio após devolução (fluxo alternativo E)***

> **Dado que** o Professor da Disciplina devolveu a Versão Final com a
> mensagem "Falta a ficha catalográfica"
>
> **Quando** o Aluno envia o novo link dentro da Data Limite
>
> **Então** o status retorna a Entregue

***Cenário 7: acesso sem estar autenticado (E1)***

> **Dado que** o Aluno não está autenticado
>
> **Quando** tenta abrir a aba Meu TCC
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre a aba Meu TCC da turma de TCC 2

***Cenário 8: link inválido (E2)***

> **Dado que** o Aluno está na seção Versão final
>
> **Quando** deixa o campo Link da Versão Final vazio e aciona o botão
> Enviar
>
> **Então** o sistema não salva e exibe "O link deve começar com
> https:// e ter até 500 caracteres"

***Cenário 9: resultado ainda não liberado (E3)***

> **Dado que** a defesa do TCC 2 ainda não teve o resultado liberado
>
> **Quando** o Aluno abre a aba Meu TCC
>
> **Então** a seção Versão final exibe "Disponível após a liberação do
> resultado", sem o campo de link

***Cenário 10: TCC 1 (E4)***

> **Dado que** o Aluno está em uma turma de TCC 1
>
> **Quando** abre a aba Meu TCC
>
> **Então** a seção Versão final não aparece

***Cenário 11: substituição após a Data Limite (E5)***

> **Dado que** o Aluno enviou o link da Versão Final em 20/11 e a Data
> Limite foi 30/11
>
> **Quando** abre a seção Versão final em 02/12
>
> **Então** o campo Link da Versão Final aparece apenas para leitura,
> sem o botão Enviar, e o status permanece Entregue

***Cenário 12: Versão Final homologada (E6)***

> **Dado que** o Professor da Disciplina homologou a Versão Final
>
> **Quando** o Aluno abre a seção Versão final
>
> **Então** o link aparece apenas para leitura, com o status Homologada
> e sem o botão Enviar

***Cenário 13: parecer Reprovado (E7)***

> **Dado que** a banca do TCC 2 liberou o resultado com o parecer
> Reprovado
>
> **Quando** o Aluno abre a aba Meu TCC
>
> **Então** o campo Link da Versão Final não aparece

**Tela no protótipo**

**Tela:** Versão final do TCC 2: envio pelo Aluno



**Diagrama de sequência**

**Diagrama relacionado:** Proposta e entrega (trecho da versão final:
confirmação das correções, envio e homologação)

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[x\] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-44 Homologar ou devolver para ajuste a Versão Final do TCC 2

| **Épico:**                | Cadastro e Manutenção      |
|---------------------------|----------------------------|
| **Feature:**              | Fluxo do TCC e Entregas    |
| **Requisitos da matriz:** | RBN-CAD-09.5, RBN-CAD-09.3 |
| **Prioridade (MoSCoW):**  | Must Have                  |
| **Responsável:**          | Leandra Matos              |

**Descrição**

Como Professor da Disciplina, quero homologar a Versão Final enviada
pelo aluno ou devolvê-la para ajuste, para que o TCC seja concluído
somente com a versão corrigida e conferida.

**Atores**

> **Ator principal:** Professor da Disciplina responsável pela turma de
> TCC 2.
>
> **Atores secundários:** Orientador (aciona o botão Correções
> Conferidas em Sistemas de Informação, no parecer Aprovado com
> Correções), Aluno (recebe a devolução) e Secretaria (notificada na
> homologação).

**Pré-condições**

- O Aluno enviou o link da Versão Final (US-29), com o status de envio
  > Entregue ou Entregue com Atraso. Sem envio, aplica-se o E4.

- O Professor da Disciplina e, quando for o caso, o Orientador estão
  > autenticados, com o Status da Conta Ativa (US-11). Sem sessão ativa,
  > aplica-se o E1.

- O Professor é o Professor da Disciplina da turma de TCC 2 do aluno;
  > para outro docente, aplica-se o E5. Em Engenharia de Computação e em
  > Licenciatura em Computação, ele é também o Orientador (US-07).

**Fluxo principal**

> 1\. No menu lateral do sistema, o Professor da Disciplina acessa o
> item Turmas, seleciona a turma de TCC 2, abre a aba Alunos e seleciona
> o bloco do aluno.
>
> 2\. O sistema abre o painel do aluno (US-41). Na seção Versão final,
> exibe o link enviado, a data e a hora do envio, o status Entregue e os
> botões Homologar e Devolver para Ajuste.
>
> 3\. O Professor acessa o link. O PDF abre fora do SIGTCC, onde o
> Professor confere o texto final, a Folha de Aprovação assinada, a
> ficha catalográfica e, no parecer Aprovado com Correções, as correções
> pedidas pela banca.
>
> 4\. Ao retornar ao painel do aluno, o Professor aciona o botão
> Homologar. Não há campos para preencher.
>
> 5\. O sistema registra a homologação com o Professor, a data e a hora,
> muda o status de envio para Homologada e o Status do TCC para
> Concluído, com o gatilho Homologação da Versão Final (US-14), e
> notifica a Secretaria para concluir os trâmites acadêmicos.
>
> 6\. O sistema mantém o Professor no painel do aluno, exibe "Versão
> Final homologada" e o status Homologada e remove os botões Homologar e
> Devolver para Ajuste. O fluxo termina.

**Fluxos alternativos**

> A. Parecer Aprovado, sem correções (passo 3): o Professor confere
> apenas o texto final, a Folha de Aprovação assinada e a ficha
> catalográfica. O fluxo prossegue a partir do passo 4.
>
> B. Sistemas de Informação com parecer Aprovado com Correções (passo
> 4): o Professor da Disciplina não é o Orientador. Antes da
> homologação, o Orientador, no item Orientações do menu lateral, no
> Painel de orientandos, aciona o botão Correções Conferidas na linha do
> aluno, sem preencher campos, e confirma. Somente então o botão
> Homologar torna-se disponível ao Professor. Nesse intervalo, nenhuma
> alteração ocorre para o Aluno. O fluxo prossegue a partir do passo 4.
>
> C. Acesso pela notificação (passo 1): o Professor seleciona o ícone de
> notificações (sino) e, em seguida, a notificação do envio da Versão
> Final. O sistema abre o painel do aluno. O fluxo prossegue a partir do
> passo 2.
>
> D. Devolver para Ajuste (passo 4): o Professor aciona o botão Devolver
> para Ajuste. O sistema abre a janela com o campo Mensagem
> (obrigatória, até 500 caracteres). O Professor informa o que precisa
> ser ajustado e confirma. O sistema muda o status de envio para
> Devolvida para Ajuste e notifica o Aluno, que reenvia o link (US-29).
> O Professor permanece no painel do aluno, com a mensagem "Versão Final
> devolvida para ajuste". O fluxo termina.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o Professor da Disciplina
> ou o Orientador tente acessar o painel do aluno ou o Painel de
> orientandos sem sessão ativa (pelo menu, pelo endereço da página ou
> por um link recebido), o sistema apresenta a tela de login (US-11).
> Após a autenticação, o sistema exibe a tela que o usuário tentou
> abrir, e o fluxo prossegue a partir do passo 2 (Professor) ou do fluxo
> alternativo B (Orientador). Em caso de falha na autenticação,
> aplicam-se as exceções da US-11.
>
> E2. Correções não conferidas em Sistemas de Informação (passo 4):
> enquanto o Orientador não acionou o botão Correções Conferidas, o
> botão Homologar permanece indisponível ao Professor da Disciplina. O
> fluxo é retomado no passo 4 após o fluxo alternativo B.
>
> E3. Devolução sem mensagem (fluxo alternativo D): o Professor confirma
> a devolução com o campo Mensagem vazio ou com mais de 500 caracteres.
> O sistema não devolve e destaca o campo. Retorna ao fluxo alternativo
> D.
>
> E4. Versão Final ainda não enviada (passo 2): sem envio do Aluno, a
> seção Versão final exibe o status Aguardando Envio ou Não Entregue,
> sem os botões Homologar e Devolver para Ajuste. O fluxo termina.
>
> E5. Usuário que não é o Professor da Disciplina da turma (passo 1): o
> painel do aluno e os botões Homologar e Devolver para Ajuste não
> aparecem. O fluxo termina.

**Pós-condições**

- Na homologação, o status de envio passou a Homologada, o Status do TCC
  > passou a Concluído, a homologação foi registrada com o Professor, a
  > data e a hora, e a Secretaria foi notificada.

- Na devolução, o status de envio passou a Devolvida para Ajuste, e o
  > Aluno foi notificado com a mensagem do Professor.

- Em Sistemas de Informação, com parecer Aprovado com Correções, o
  > acionamento de Correções Conferidas foi registrado antes da
  > homologação.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                                                                                                 | **Resumo da regra em uma frase**                                                                                                                                                               |
|--------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-09.5** | O sistema deve permitir que o Professor da Disciplina homologue a Versão Final de TCC 2 ou a devolva para ajuste.                                                                                                                       | O Professor da Disciplina homologa a Versão Final, o que confirma as correções, ou a devolve para ajuste; em SI, com Aprovado com Correções, o Orientador clica antes em Correções Conferidas. |
| **CAD-09.3** | O sistema deve registrar automaticamente o status de envio de cada aluno na entrega, com um dos valores: Aguardando Envio, Entregue, Entregue com Atraso, Não Entregue e, somente na Versão Final, Devolvida para Ajuste ou Homologada. | Status de envio: Aguardando Envio, Entregue, Entregue com Atraso, Não Entregue e, na Versão Final, Devolvida para Ajuste ou Homologada; o atraso não muda o Status do TCC.                     |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. A homologação pelo Professor da Disciplina confirma a Versão Final
> e, no Aprovado com Correções, as correções; em Sistemas de Informação,
> o Orientador aciona antes Correções Conferidas.
>
> 2\. A devolução para ajuste exige mensagem ao aluno.

***Cenário 1: Versão Final homologada (fluxo principal)***

> **Dado que** o Aluno enviou o link da Versão Final
>
> **Quando** o Professor da Disciplina abre o painel do aluno, confere o
> PDF e aciona o botão Homologar
>
> **Então** o status de envio passa a Homologada, o Status do TCC passa
> a Concluído e a Secretaria é notificada
>
> **E** o sistema exibe "Versão Final homologada" no painel do aluno

***Cenário 2: parecer Aprovado, sem correções (fluxo alternativo A)***

> **Dado que** o TCC 2 foi aprovado sem correções e o Aluno enviou o
> link
>
> **Quando** o Professor da Disciplina confere o PDF e aciona o botão
> Homologar
>
> **Então** o Status do TCC passa a Concluído

***Cenário 3: correções conferidas em Sistemas de Informação (fluxo
alternativo B)***

> **Dado que** o TCC 2 de Sistemas de Informação foi aprovado com
> correções e o Aluno enviou o link
>
> **Quando** o Orientador aciona o botão Correções Conferidas no Painel
> de orientandos e confirma
>
> **Então** o botão Homologar torna-se disponível ao Professor da
> Disciplina

***Cenário 4: acesso pela notificação (fluxo alternativo C)***

> **Dado que** o Professor da Disciplina recebeu a notificação do envio
> da Versão Final
>
> **Quando** seleciona o ícone de notificações (sino) e, em seguida, a
> notificação
>
> **Então** o sistema abre o painel do aluno na seção Versão final

***Cenário 5: devolução para ajuste (fluxo alternativo D)***

> **Dado que** o Aluno enviou o link
>
> **Quando** o Professor da Disciplina aciona o botão Devolver para
> Ajuste, informa a Mensagem "Falta a ficha catalográfica" e confirma
>
> **Então** o status passa a Devolvida para Ajuste e o Aluno é
> notificado para reenviar

***Cenário 6: acesso sem estar autenticado (E1)***

> **Dado que** o Professor da Disciplina não está autenticado
>
> **Quando** tenta abrir o painel do aluno
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre o painel do aluno

***Cenário 7: correções ainda não conferidas em Sistemas de Informação
(E2)***

> **Dado que** o TCC 2 de Sistemas de Informação foi aprovado com
> correções e o Aluno enviou o link
>
> **Quando** o Orientador ainda não acionou o botão Correções Conferidas
>
> **Então** o botão Homologar permanece indisponível ao Professor da
> Disciplina e nenhuma alteração ocorre para o Aluno

***Cenário 8: devolução sem mensagem (E3)***

> **Dado que** o Professor da Disciplina acionou o botão Devolver para
> Ajuste
>
> **Quando** confirma com o campo Mensagem vazio
>
> **Então** o sistema não devolve e destaca o campo Mensagem

***Cenário 9: Versão Final ainda não enviada (E4)***

> **Dado que** o Aluno ainda não enviou o link da Versão Final
>
> **Quando** o Professor da Disciplina abre o painel do aluno
>
> **Então** a seção Versão final exibe Aguardando Envio, sem os botões
> Homologar e Devolver para Ajuste

***Cenário 10: usuário sem permissão (E5)***

> **Dado que** um Docente não é o Professor da Disciplina da turma
>
> **Quando** procura a Versão Final do aluno
>
> **Então** os botões Homologar e Devolver para Ajuste não aparecem para
> ele

**Tela no protótipo**

**Tela:** Painel do aluno: Versão final; Painel de orientandos:
Correções Conferidas (Sistemas de Informação)



**Diagrama de sequência**

**Diagrama relacionado:** Proposta e entrega (trecho da versão final:
confirmação das correções, envio e homologação)

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[x\] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-17 Indicar, cancelar ou trocar o orientador

| **Épico:**                | Cadastro e Manutenção                    |
|---------------------------|------------------------------------------|
| **Feature:**              | Orientação, Atas e Publicações           |
| **Requisitos da matriz:** | RBN-CAD-10.1, RBN-CAD-10.2, RBN-CAD-10.6 |
| **Prioridade (MoSCoW):**  | Must Have                                |
| **Responsável:**          | Leandra Matos                            |

**Descrição**

Como Aluno, quero indicar o meu orientador e, quando necessário,
cancelar o pedido ou trocar de orientador, para que o meu trabalho tenha
a orientação registrada no sistema.

**Atores**

> **Ator principal:** Aluno.
>
> **Atores secundários:** Docente indicado, que recebe o pedido (US-18),
> e orientador atual, notificado na troca.

**Pré-condições**

- O Aluno está autenticado, com o Status da Conta Ativa (US-11). Sem
  > sessão ativa, aplica-se o E1.

- O Aluno está vinculado a uma turma não arquivada (US-08), com ou sem
  > Proposta registrada. Com a turma arquivada, aplica-se o E5.

- O TCC do Aluno não está com o Status Desistente, Reprovado ou
  > Jubilado; caso contrário, aplica-se o E4.

- A turma não usa orientador automático (turmas de TCC 2 de Engenharia
  > de Computação e de Licenciatura em Computação, US-07); caso
  > contrário, aplica-se o fluxo alternativo F.

**Fluxo principal**

> 1\. No menu lateral do sistema, o Aluno acessa o item Turmas,
> seleciona a sua turma, abre a aba Meu TCC e acessa a seção Orientação.
>
> 2\. O sistema exibe "Sem orientador", a lista Indicar orientador e o
> botão Enviar pedido. A lista contém todos os Docentes com o Status da
> Conta Ativa, de qualquer curso do NUCOMP, e cada opção exibe nome,
> titulação e curso.
>
> 3\. O Aluno seleciona um docente na lista e aciona o botão Enviar
> pedido.
>
> 4\. O sistema registra o pedido como Aguardando Resposta, bloqueia a
> lista e exibe "Pedido enviado a \[nome do docente\]. Aguardando
> resposta" e o botão Cancelar Pedido.
>
> 5\. O sistema envia ao docente um e-mail e uma notificação no sistema
> com o nome do aluno, o título do trabalho e o link do pedido (US-18).
>
> 6\. O docente aceita o pedido (US-18), e o Aluno recebe uma
> notificação no sistema (ícone de sino).
>
> 7\. Ao abrir a aba Meu TCC, o Aluno visualiza na seção Orientação o
> docente como Orientador, a lista Trocar de orientador e o botão
> Registrar coorientador (US-45). O fluxo termina.

**Fluxos alternativos**

> A. Pedido sem Proposta (passo 3): se o TCC está Sem Proposta, a lista
> Indicar orientador aparece normalmente, e o e-mail e a notificação ao
> docente exibem "Proposta ainda não registrada" no lugar do título. O
> fluxo prossegue a partir do passo 4.
>
> B. Pedido recusado (passo 6): o Aluno recebe uma notificação no
> sistema. Na seção Orientação, a lista Indicar orientador torna-se
> novamente disponível. Retorna ao passo 3.
>
> C. Cancelamento do pedido (passo 4): enquanto o pedido está Aguardando
> Resposta, o Aluno aciona o botão Cancelar Pedido. O sistema marca o
> pedido como Cancelado e libera a lista Indicar orientador. Retorna ao
> passo 2.
>
> D. Troca de orientador (CAD-10.6; passo 2): com o Status Em Andamento
> ou Apto para Defesa e sem sessão de defesa Agendada, Reagendada ou Em
> Andamento, a seção Orientação exibe a lista Trocar de orientador e o
> botão Enviar pedido. O Aluno seleciona outro docente e aciona o botão
> Enviar pedido. O sistema registra o pedido do tipo Troca de
> Orientação. O orientador atual permanece até o aceite do novo; após o
> aceite, o antigo é notificado e a troca é registrada no histórico. Se
> o novo orientador era coorientador do trabalho, a coorientação é
> encerrada. O fluxo prossegue a partir do passo 4.
>
> E. Pedido de troca pendente no agendamento (passo 4): quando a defesa
> é agendada (US-24), o pedido de troca ainda sem resposta é cancelado
> automaticamente, o orientador atual é mantido e o Aluno e o docente
> são avisados. O fluxo termina.
>
> F. Turma com orientador automático (passo 2): a seção Orientação já
> exibe o professor da turma como Orientador, sem a lista Indicar
> orientador. A troca é feita pelo Professor da Disciplina ou pela
> Secretaria, por transferência de turma (US-08). O fluxo termina.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o Aluno tente acessar a
> aba Meu TCC sem sessão ativa (pelo menu, pelo endereço da página ou
> por um link recebido), o sistema apresenta a tela de login (US-11).
> Após a autenticação, o sistema exibe a aba Meu TCC da turma, na seção
> Orientação, e o fluxo prossegue a partir do passo 2. Em caso de falha
> na autenticação, aplicam-se as exceções da US-11.
>
> E2. Pedido pendente (passo 2): enquanto o docente não responde, a
> lista Indicar orientador permanece bloqueada, e o único botão
> disponível é Cancelar Pedido. O fluxo prossegue a partir do passo 6
> após a resposta do docente.
>
> E3. Troca bloqueada (passo 2): com sessão de defesa Agendada,
> Reagendada ou Em Andamento, ou com o Status fora de Em Andamento e
> Apto para Defesa, a lista Trocar de orientador aparece desabilitada. O
> fluxo termina.
>
> E4. Aluno com o Status Desistente, Reprovado ou Jubilado (CAD-08.5;
> passo 2): a seção Orientação permanece disponível apenas para
> consulta, sem indicar nem trocar orientador. O fluxo termina.
>
> E5. Turma arquivada (passo 2): a seção Orientação permanece disponível
> apenas para consulta, sem a lista Indicar orientador, a lista Trocar
> de orientador e o botão Cancelar Pedido. O fluxo termina.

**Pós-condições**

- O pedido de orientação foi registrado como Aguardando Resposta, e o
  > docente foi notificado por e-mail e no sistema.

- Após o aceite (US-18), o Aluno passou a ter um único orientador ativo.

- No cancelamento, o pedido foi registrado como Cancelado; na troca, o
  > vínculo anterior foi registrado no histórico.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                     | **Resumo da regra em uma frase**                                                                                                                          |
|--------------|---------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-10.1** | O sistema deve permitir que o Aluno indique seu orientador, notificando o Docente indicado. | O Aluno indica o orientador a partir do vínculo à turma, com ou sem Proposta; um pedido pendente por vez, que pode ser cancelado; o docente é notificado. |
| **CAD-10.2** | O sistema deve permitir que o Docente aceite ou recuse o pedido de orientação.              | Na recusa, o Aluno é notificado e a lista de orientador volta a ficar disponível.                                                                         |
| **CAD-10.6** | \[Exceção\] O sistema deve permitir a troca de orientador até o agendamento da defesa.      | Troca de orientador até o agendamento da defesa; o pedido de troca ainda sem resposta é cancelado automaticamente quando a defesa é agendada.             |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Orientador pode ser indicado logo após o vínculo à turma, com ou
> sem Proposta.
>
> 2\. Troca de orientador permitida apenas até o agendamento da defesa;
> nas turmas com orientador automático, a troca é feita pelo Professor
> da Disciplina ou pela Secretaria.

***Cenário 1: pedido de orientação enviado e aceito (fluxo principal)***

> **Dado que** o Aluno está autenticado, vinculado à turma e sem
> orientador
>
> **Quando** seleciona um docente na lista Indicar orientador e aciona o
> botão Enviar pedido
>
> **Então** o pedido passa a Aguardando Resposta, a lista permanece
> bloqueada e aparece o botão Cancelar Pedido
>
> **E**, após o aceite do docente, a seção Orientação exibe o docente
> como Orientador

***Cenário 2: pedido sem Proposta (fluxo alternativo A)***

> **Dado que** o TCC está Sem Proposta
>
> **Quando** o Aluno seleciona um docente e aciona o botão Enviar pedido
>
> **Então** o pedido passa a Aguardando Resposta e o docente recebe a
> notificação com "Proposta ainda não registrada"

***Cenário 3: pedido recusado (fluxo alternativo B)***

> **Dado que** o pedido do Aluno está Aguardando Resposta
>
> **Quando** o docente recusa o pedido
>
> **Então** o Aluno recebe a notificação e a lista Indicar orientador
> torna-se novamente disponível

***Cenário 4: cancelamento do pedido (fluxo alternativo C)***

> **Dado que** o pedido de orientação está Aguardando Resposta
>
> **Quando** o Aluno aciona o botão Cancelar Pedido
>
> **Então** o pedido passa a Cancelado e a lista Indicar orientador
> torna-se novamente disponível

***Cenário 5: troca de orientador (fluxo alternativo D)***

> **Dado que** o TCC está Em Andamento, tem o orientador X e não tem
> sessão de defesa agendada
>
> **Quando** o Aluno seleciona o docente Y em Trocar de orientador e
> envia o pedido
>
> **Então** X permanece como orientador até Y aceitar
>
> **E**, após o aceite, X é notificado e a troca é registrada no
> histórico

***Cenário 6: pedido de troca cancelado no agendamento (fluxo
alternativo E)***

> **Dado que** o Aluno pediu a troca para o docente Y e Y ainda não
> respondeu
>
> **Quando** a defesa do TCC é agendada
>
> **Então** o pedido passa a Cancelado, o orientador atual é mantido e o
> Aluno e Y são avisados

***Cenário 7: turma com orientador automático (fluxo alternativo F)***

> **Dado que** o Aluno está numa turma de TCC 2 de Engenharia de
> Computação
>
> **Quando** abre a seção Orientação
>
> **Então** o professor da turma já aparece como Orientador e não há a
> lista Indicar orientador

***Cenário 8: acesso sem estar autenticado (E1)***

> **Dado que** o Aluno não está autenticado
>
> **Quando** tenta abrir a aba Meu TCC
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre a aba Meu TCC na seção Orientação

***Cenário 9: pedido pendente (E2)***

> **Dado que** o pedido de orientação está Aguardando Resposta
>
> **Quando** o Aluno abre a seção Orientação
>
> **Então** a lista Indicar orientador aparece bloqueada e apenas o
> botão Cancelar Pedido está disponível

***Cenário 10: troca bloqueada após o agendamento (E3)***

> **Dado que** a defesa do TCC está Agendada
>
> **Quando** o Aluno abre a seção Orientação
>
> **Então** a lista Trocar de orientador aparece desabilitada

***Cenário 11: aluno Desistente (E4)***

> **Dado que** o TCC do Aluno está com o Status Desistente
>
> **Quando** o Aluno abre a seção Orientação
>
> **Então** a seção aparece apenas para consulta, sem indicar nem trocar
> orientador

***Cenário 12: turma arquivada (E5)***

> **Dado que** a turma do aluno foi arquivada
>
> **Quando** o Aluno abre a seção Orientação em Turmas arquivadas
>
> **Então** a seção aparece apenas para consulta, sem indicar, trocar ou
> cancelar pedido

**Tela no protótipo**

**Tela:** Orientação do TCC: indicação e troca de orientador



**Diagrama de sequência**

**Diagrama relacionado:** Indicação e aceite de orientador e
coorientador

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[x\] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-18 Aceitar ou recusar pedido de orientação e consultar o painel de orientandos

| **Épico:**                | Cadastro e Manutenção                                                |
|---------------------------|----------------------------------------------------------------------|
| **Feature:**              | Orientação, Atas e Publicações                                       |
| **Requisitos da matriz:** | RBN-CAD-10.1, RBN-CAD-10.2, RBN-CAD-11.3, RBN-CAD-11.4, RBN-CAD-10.6 |
| **Prioridade (MoSCoW):**  | Must Have                                                            |
| **Responsável:**          | Leandra Matos                                                        |

**Descrição**

Como Docente do NUCOMP, quero aceitar ou recusar os pedidos de
orientação que recebo e consultar os meus orientandos no painel de
orientandos, para que eu assuma a orientação dos trabalhos que aceitar e
acompanhe esses trabalhos em um único lugar.

**Atores**

> **Ator principal:** Docente do NUCOMP indicado no pedido. Ao aceitar,
> passa a ser o Orientador do trabalho.
>
> **Atores secundários:** Aluno que fez o pedido (recebe o resultado),
> Professor da Disciplina da turma do aluno (recebe o resultado),
> orientador atual (apenas no pedido de troca), Coordenador de Curso e
> Secretaria (visualizam o alerta de mais de 5 orientandos).

**Pré-condições**

- O Aluno enviou um pedido de orientação para este docente (US-17), e o
  > pedido está Aguardando Resposta: não foi cancelado pelo Aluno nem
  > pelo agendamento da defesa.

- O sistema já enviou ao docente o e-mail e a notificação no sistema
  > (ícone de sino) com o nome do aluno, o título do trabalho (ou
  > "Proposta ainda não registrada") e o link do pedido.

- Para responder, o docente precisa estar autenticado no sistema, com o
  > Status da Conta Ativa (US-11). O pedido nunca é respondido pelo
  > e-mail: o e-mail contém apenas o link que abre o sistema. Sem sessão
  > ativa, aplica-se o E1.

**Fluxo principal**

> 1\. No menu lateral do sistema, o docente seleciona o item
> Orientações.
>
> 2\. O sistema abre a tela Orientações. Na parte superior, encontra-se
> a seção Pedidos de orientação, com uma linha por pedido Aguardando
> Resposta exibindo o nome do aluno, o título do trabalho, a turma, a
> data e a hora do pedido e os botões Ver proposta, Recusar e Aceitar.
>
> 3\. O docente aciona o botão Aceitar na linha do pedido. Não há campos
> para preencher.
>
> 4\. O sistema registra o aceite com o docente, a data e a hora,
> vincula o docente como Orientador do trabalho e marca o pedido como
> Aceito.
>
> 5\. O sistema envia ao Aluno uma notificação no sistema e ao Professor
> da Disciplina da turma um e-mail e uma notificação no sistema, com o
> resultado.
>
> 6\. O sistema soma 1 à quantidade de orientandos do docente na
> listagem de docentes, em TCC 1 ou em TCC 2, de acordo com a turma do
> aluno.
>
> 7\. O sistema mantém o docente na tela Orientações, exibe "Pedido
> aceito. O aluno foi incluído no seu Painel de orientandos", remove o
> pedido da seção Pedidos de orientação e exibe o aluno no Painel de
> orientandos, logo abaixo, com Nome do Aluno, Curso, Turma, Título,
> Modalidade, Papel (Orientador), Status do TCC e status de envio das
> entregas, e com as ações da linha: Atas e Registrar ata (US-19),
> Histórico (US-14), Publicação, na modalidade Artigo Científico
> (US-46), Apto para Defesa (US-42) e, em Sistemas de Informação,
> Correções Conferidas (US-44). O fluxo termina.

**Fluxos alternativos**

> A. Entrada pelo e-mail (passo 1): no e-mail (fora do sistema), o
> docente acessa o link do pedido. O navegador abre o SIGTCC na tela
> Orientações, com o pedido na seção Pedidos de orientação, e o fluxo
> prossegue a partir do passo 3. Se o docente não estiver autenticado,
> aplica-se o E1.
>
> B. Entrada pela notificação no sistema (passo 1): já dentro do
> sistema, o docente seleciona o ícone de notificações (sino), no canto
> superior direito, e, em seguida, a notificação do pedido. O sistema
> abre a tela Orientações, e o fluxo prossegue a partir do passo 2.
>
> C. Ver a proposta antes de decidir (passo 3): o docente aciona o botão
> Ver proposta. O sistema abre uma janela com Título, Subtítulo, Resumo,
> Modalidade e Link do Documento da Proposta, somente leitura. O docente
> aciona o botão Fechar e retorna ao passo 3. Se o aluno ainda não
> salvou a Proposta, a linha exibe "Proposta ainda não registrada" e o
> botão Ver proposta não aparece.
>
> D. Recusa (CAD-10.2; passo 3): o docente aciona o botão Recusar, sem
> preencher campos. O sistema registra a recusa com o docente, a data e
> a hora, remove o pedido da seção, notifica o Aluno no sistema e libera
> novamente a lista Indicar orientador para o Aluno (US-17). O docente
> permanece na tela Orientações, com a mensagem "Pedido recusado", e o
> aluno não é incluído no painel. O fluxo termina.
>
> E. Pedido de troca de orientador (CAD-10.6; passo 3): a linha do
> pedido exibe também o nome do orientador atual. Ao aceitar, o vínculo
> anterior é encerrado, o orientador anterior é notificado, a troca vai
> para o histórico de orientação e o aluno é removido do painel dele. Se
> quem aceita era coorientador do trabalho, a coorientação é encerrada.
> Se o docente recusar, o orientador atual é mantido. O fluxo prossegue
> a partir do passo 5.
>
> F. Mais de 5 orientandos (CAD-11.3; passo 6): o aceite não é
> bloqueado. A listagem de docentes, vista pelo Coordenador de Curso e
> pela Secretaria, passa a exibir a quantidade com alerta visual. O
> fluxo prossegue a partir do passo 7.
>
> G. Consulta posterior do painel (CAD-11.4; passo 7): posteriormente, o
> Orientador seleciona o item Orientações no menu lateral e visualiza o
> Painel de orientandos. Os orientandos vinculados automaticamente nas
> turmas de TCC 2 de Engenharia de Computação e de Licenciatura em
> Computação (US-07) aparecem da mesma forma, os trabalhos em que ele é
> Coorientador aparecem com o Papel Coorientador (US-36), e os
> orientandos de turmas arquivadas aparecem no fim, apenas com acesso às
> atas. O fluxo termina.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o docente tente acessar a
> tela Orientações sem sessão ativa (pelo menu, pelo endereço da página
> ou por um link recebido), o sistema apresenta a tela de login (US-11).
> Após a autenticação, o sistema exibe a tela Orientações, na seção
> Pedidos de orientação, e o fluxo prossegue a partir do passo 2. Em
> caso de falha na autenticação, aplicam-se as exceções da US-11.
>
> E2. Pedido de outro docente (passo 2): se quem está autenticado não é
> o docente indicado (ex.: abriu o link de um e-mail encaminhado), o
> sistema exibe "Este pedido não está disponível para o seu usuário" e
> não exibe os botões Aceitar e Recusar. O fluxo termina.
>
> E3. Pedido cancelado pelo Aluno (CAD-10.1; passo 2): o pedido é
> removido da seção Pedidos de orientação. Se o docente abre o link do
> e-mail, o sistema exibe "Este pedido foi cancelado pelo aluno" e não
> exibe os botões. O fluxo termina.
>
> E4. Pedido de troca cancelado pelo agendamento (CAD-10.6; passo 2):
> quando a defesa é agendada (US-24) e o pedido de troca ainda não foi
> respondido, o sistema cancela o pedido, o orientador atual é mantido e
> o docente e o Aluno são avisados. Pelo link do e-mail, o sistema exibe
> "Este pedido foi cancelado porque a defesa foi agendada" e não exibe
> os botões. O fluxo termina.
>
> E5. Pedido já respondido (passo 2): se o docente abre o link do e-mail
> após responder, o sistema exibe a decisão registrada (Aceito ou
> Recusado), com a data e a hora, e não exibe os botões. O fluxo
> termina.

**Pós-condições**

- No aceite, o docente foi vinculado como Orientador do trabalho, o
  > aceite foi registrado com o docente, a data e a hora, o aluno foi
  > incluído no Painel de orientandos e a contagem de orientandos foi
  > atualizada.

- No aceite, o Aluno e o Professor da Disciplina foram notificados, e o
  > registro de coorientadores foi liberado ao Aluno (US-45).

- Na recusa, a recusa foi registrada com o docente, a data e a hora, o
  > Aluno foi notificado e a lista Indicar orientador foi novamente
  > liberada ao Aluno.

- Nos dois casos, o pedido deixou de constar como Aguardando Resposta.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                                                   | **Resumo da regra em uma frase**                                                                                                                                                |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-10.1** | O sistema deve permitir que o Aluno indique seu orientador, notificando o Docente indicado.                                                                                               | O Aluno indica o orientador a partir do vínculo à turma, com ou sem Proposta; um pedido pendente por vez, que pode ser cancelado; o docente é notificado.                       |
| **CAD-10.2** | O sistema deve permitir que o Docente aceite ou recuse o pedido de orientação.                                                                                                            | Botões Aceitar e Recusar; ao aceitar, o docente vira Orientador do trabalho, e o Aluno e o Professor da Disciplina são avisados.                                                |
| **CAD-11.3** | O sistema deve exibir a quantidade de orientandos de cada docente.                                                                                                                        | A listagem de docentes mostra quantos orientandos cada um tem, em TCC 1 e em TCC 2, com alerta para o Coordenador e a Secretaria acima de 5.                                    |
| **CAD-11.4** | O sistema deve permitir ao Orientador visualizar seu painel de orientandos e, quando houver coorientação aceita, ao Coorientador do NUCOMP visualizar seus coorientandos no mesmo painel. | O Orientador vê o painel de orientandos (aluno, curso, turma, título, modalidade, papel, status, entregas e atas); o coorientador do NUCOMP vê ali só os trabalhos que aceitou. |
| **CAD-10.6** | \[Exceção\] O sistema deve permitir a troca de orientador até o agendamento da defesa.                                                                                                    | Troca de orientador até o agendamento da defesa; o pedido de troca ainda sem resposta é cancelado automaticamente quando a defesa é agendada.                                   |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Ao aceitar, o Docente ganha papel de Orientador.
>
> 2\. Exibição de alerta visual se o docente exceder 5 orientandos.

***Cenário 1: aceite do pedido pela tela Orientações (fluxo
principal)***

> **Dado que** o docente está autenticado e tem um pedido Aguardando
> Resposta da aluna Heloísa Martins Cruz
>
> **Quando** seleciona o item Orientações no menu lateral e em Aceitar
> na linha do pedido
>
> **Então** passa a ser o Orientador do trabalho e o sistema exibe
> "Pedido aceito. O aluno foi incluído no seu Painel de orientandos"
>
> **E** a aluna é removida da seção Pedidos de orientação, aparece no
> Painel de orientandos com o Papel Orientador, e a Aluna e o Professor
> da Disciplina são notificados

***Cenário 2: entrada pelo link do e-mail (fluxo alternativo A)***

> **Dado que** o docente está autenticado e recebeu o e-mail do pedido
>
> **Quando** acessa o link do pedido no e-mail
>
> **Então** o navegador abre o SIGTCC na tela Orientações, com o pedido
> na seção Pedidos de orientação

***Cenário 3: entrada pela notificação no sistema (fluxo alternativo
B)***

> **Dado que** o docente está autenticado e o ícone de sino exibe a
> notificação do pedido
>
> **Quando** seleciona o ícone de notificações e, em seguida, a
> notificação
>
> **Então** o sistema abre a tela Orientações com o pedido na seção
> Pedidos de orientação

***Cenário 4: ver a proposta (fluxo alternativo C)***

> **Dado que** o pedido é de um aluno que já salvou a Proposta
>
> **Quando** o docente aciona o botão Ver proposta
>
> **Então** o sistema exibe Título, Subtítulo, Resumo, Modalidade e Link
> do Documento da Proposta somente para leitura
>
> **E**, ao acionar o botão Fechar, o docente retorna à linha do pedido
> com os botões Aceitar e Recusar

***Cenário 5: pedido sem Proposta (fluxo alternativo C)***

> **Dado que** o pedido é de um aluno com o TCC Sem Proposta
>
> **Quando** o docente abre a tela Orientações
>
> **Então** a linha do pedido exibe "Proposta ainda não registrada" e
> não exibe o botão Ver proposta

***Cenário 6: recusa do pedido (fluxo alternativo D)***

> **Dado que** o docente tem um pedido Aguardando Resposta
>
> **Quando** aciona o botão Recusar
>
> **Então** o sistema registra a recusa, exibe "Pedido recusado" e
> remove o pedido da seção
>
> **E** o Aluno é notificado e pode indicar outro orientador

***Cenário 7: aceite de pedido de troca (fluxo alternativo E)***

> **Dado que** o aluno tem o orientador X e pediu a troca para o docente
> Y
>
> **Quando** Y aciona o botão Aceitar
>
> **Então** Y passa a ser o Orientador, X é notificado e a troca vai
> para o histórico
>
> **E** o aluno é removido do Painel de orientandos de X

***Cenário 8: alerta de mais de 5 orientandos (fluxo alternativo F)***

> **Dado que** o docente já tem 5 orientandos
>
> **Quando** aceita mais um pedido
>
> **Então** a listagem de docentes exibe 6 orientandos com alerta visual
> para o Coordenador de Curso e a Secretaria

***Cenário 9: painel de orientandos (fluxo alternativo G)***

> **Dado que** o docente é Orientador de dois alunos, um deles de uma
> turma arquivada
>
> **Quando** seleciona o item Orientações no menu lateral
>
> **Então** visualiza os dois alunos no Painel de orientandos com Nome
> do Aluno, Curso, Turma, Título, Modalidade, Papel, Status do TCC,
> entregas e atas
>
> **E** o aluno da turma arquivada aparece no fim, apenas para consultar
> as atas

***Cenário 10: acesso pelo link sem estar autenticado (E1)***

> **Dado que** o docente não está autenticado
>
> **Quando** acessa o link do pedido no e-mail
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre a tela Orientações com o pedido na seção
> Pedidos de orientação

***Cenário 11: pedido de outro docente (E2)***

> **Dado que** o docente Z está autenticado e abre o link de um pedido
> feito ao docente Y
>
> **Quando** o sistema carrega a página
>
> **Então** exibe "Este pedido não está disponível para o seu usuário" e
> não exibe os botões Aceitar e Recusar

***Cenário 12: pedido cancelado pelo aluno (E3)***

> **Dado que** o Aluno cancelou o pedido antes da resposta
>
> **Quando** o docente abre o link do pedido no e-mail
>
> **Então** o sistema exibe "Este pedido foi cancelado pelo aluno" e não
> exibe os botões

***Cenário 13: pedido de troca cancelado no agendamento (E4)***

> **Dado que** o Aluno pediu troca de orientador e o novo docente ainda
> não respondeu
>
> **Quando** a defesa do TCC é agendada
>
> **Então** o pedido passa a Cancelado, o orientador atual é mantido e o
> docente e o Aluno são avisados

***Cenário 14: pedido já respondido (E5)***

> **Dado que** o docente já aceitou o pedido
>
> **Quando** abre novamente o link do pedido no e-mail
>
> **Então** o sistema exibe "Aceito", com a data e a hora, e não exibe
> os botões

**Tela no protótipo**

**Tela:** Pedidos de orientação, Painel de orientandos e Listagem de
docentes



**Diagrama de sequência**

**Diagrama relacionado:** Indicação e aceite de orientador e
coorientador

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[x\] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-45 Registrar, substituir ou remover coorientadores

| **Épico:**                | Cadastro e Manutenção          |
|---------------------------|--------------------------------|
| **Feature:**              | Orientação, Atas e Publicações |
| **Requisitos da matriz:** | RBN-CAD-10.3, RBN-CAD-10.7     |
| **Prioridade (MoSCoW):**  | Should Have                    |
| **Responsável:**          | Leandra Matos                  |

**Descrição**

Como Aluno, quero registrar coorientadores do NUCOMP ou externos e, até
o agendamento da defesa, substituí-los ou removê-los, para que a
coorientação do meu trabalho fique registrada no sistema.

**Atores**

> **Ator principal:** Aluno.
>
> **Atores secundários:** Docente do NUCOMP indicado como coorientador
> (recebe o convite, US-36) e Orientador (notificado de cada registro,
> substituição e remoção).

**Pré-condições**

- O Aluno está autenticado, com o Status da Conta Ativa (US-11). Sem
  > sessão ativa, aplica-se o E1.

- O Aluno tem orientador vinculado, por aceite (US-18) ou
  > automaticamente (US-07); caso contrário, aplica-se o E2.

- O TCC do Aluno não está com o Status Desistente, Reprovado ou
  > Jubilado, e a turma não está arquivada; caso contrário, aplica-se o
  > E6 ou o E7.

**Fluxo principal**

> 1\. No menu lateral do sistema, o Aluno acessa o item Turmas,
> seleciona a sua turma, abre a aba Meu TCC e acessa a seção Orientação.
>
> 2\. O sistema exibe o Orientador, a lista de coorientadores já
> registrados, com os botões Substituir e Remover em cada um, e o botão
> Registrar coorientador.
>
> 3\. O Aluno aciona o botão Registrar coorientador. O sistema abre a
> janela com a lista Tipo (Docente do NUCOMP ou Externo ao NUCOMP).
>
> 4\. O Aluno seleciona Docente do NUCOMP. O sistema exibe a lista de
> Docentes com o Status da Conta Ativa, sem o orientador e sem os
> coorientadores já registrados.
>
> 5\. O Aluno seleciona o docente e aciona o botão Salvar.
>
> 6\. O sistema registra o coorientador como "Aguardando Aceite", envia
> o convite ao docente (US-36) e notifica o Orientador no sistema.
>
> 7\. O sistema fecha a janela e mantém o Aluno na aba Meu TCC, com o
> coorientador na seção Orientação, a etiqueta "Aguardando Aceite" e os
> botões Substituir e Remover. O fluxo termina.

**Fluxos alternativos**

> A. Coorientador externo (passo 4): o Aluno seleciona Externo ao
> NUCOMP. O sistema exibe os campos Nome Completo (obrigatório, apenas
> letras, acentos e espaços, até 150 caracteres), E-mail (opcional,
> formato nome@domínio, de qualquer domínio, até 100 caracteres) e
> Instituição de Origem (opcional, até 150 caracteres). O Aluno preenche
> os campos e aciona o botão Salvar. O sistema registra o coorientador
> sem acesso ao sistema e sem convite e notifica o Orientador. O fluxo
> prossegue a partir do passo 7.
>
> B. Mais de um coorientador (passo 7): o Aluno repete os passos 3 a 7
> para cada coorientador. Não há limite de quantidade. Retorna ao passo
> 3.
>
> C. Cancelamento do convite (CAD-10.4; passo 7): enquanto o convite
> está "Aguardando Aceite", o Aluno aciona o botão Remover no
> coorientador e confirma. O convite é cancelado e o docente não pode
> mais aceitá-lo (US-36). O fluxo termina.
>
> D. Substituir coorientador (CAD-10.7; passo 2): sem sessão de defesa
> Agendada, Reagendada ou Em Andamento, o Aluno aciona o botão
> Substituir no coorientador. O sistema abre a mesma janela do passo 3,
> e a seleção obedece às regras dos passos 4 e 5 ou do fluxo alternativo
> A. O vínculo anterior é registrado no histórico, e o Orientador e,
> quando o substituído é docente do NUCOMP, o próprio docente são
> notificados no sistema. O fluxo prossegue a partir do passo 6.
>
> E. Remover coorientador (CAD-10.7; passo 2): sem sessão de defesa
> Agendada, Reagendada ou Em Andamento, o Aluno aciona o botão Remover
> no coorientador e confirma na mensagem. O vínculo é registrado no
> histórico, o Orientador e, quando o removido é docente do NUCOMP, o
> próprio docente são notificados no sistema, e o coorientador do NUCOMP
> perde o acesso ao trabalho. O fluxo termina.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o Aluno tente acessar a
> aba Meu TCC sem sessão ativa (pelo menu, pelo endereço da página ou
> por um link recebido), o sistema apresenta a tela de login (US-11).
> Após a autenticação, o sistema exibe a aba Meu TCC da turma, na seção
> Orientação, e o fluxo prossegue a partir do passo 2. Em caso de falha
> na autenticação, aplicam-se as exceções da US-11.
>
> E2. Coorientador antes do orientador (passo 2): sem orientador
> vinculado, o botão Registrar coorientador não aparece. O fluxo
> termina.
>
> E3. Coorientador repetido (passo 4): o docente já registrado não
> aparece na lista. No externo, se o E-mail já está registrado como
> coorientador do trabalho, o sistema não salva e exibe "Este e-mail já
> está registrado como coorientador". Retorna ao passo 4.
>
> E4. Coorientador externo com campo inválido (fluxo alternativo A):
> Nome Completo em branco, com números ou com mais de 150 caracteres;
> E-mail fora do formato nome@domínio ou com mais de 100 caracteres;
> Instituição de Origem com mais de 150 caracteres. O sistema não salva
> e destaca o campo. Retorna ao fluxo alternativo A.
>
> E5. Substituição ou remoção bloqueada (passo 2): com sessão de defesa
> Agendada, Reagendada ou Em Andamento, os botões Substituir e Remover
> aparecem desabilitados. O fluxo termina.
>
> E6. Aluno com o Status Desistente, Reprovado ou Jubilado (CAD-08.5;
> passo 2): a seção Orientação permanece disponível apenas para
> consulta, sem os botões Registrar coorientador, Substituir e Remover.
> O fluxo termina.
>
> E7. Turma arquivada (passo 2): a seção Orientação permanece disponível
> apenas para consulta, sem os botões Registrar coorientador, Substituir
> e Remover. O fluxo termina.

**Pós-condições**

- O coorientador foi registrado: o do NUCOMP como "Aguardando Aceite",
  > com convite enviado, e o externo sem acesso ao sistema.

- Na substituição e na remoção, o vínculo anterior foi registrado no
  > histórico, e o coorientador do NUCOMP removido perdeu o acesso ao
  > trabalho.

- O Orientador foi notificado de cada registro, substituição e remoção.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                                                  | **Resumo da regra em uma frase**                                                                                                                                                                                                                                                                                                                                                                                                          |
|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-10.3** | O sistema deve permitir que o Aluno registre coorientadores, com o formulário de coorientador externo ao NUCOMP que deve conter os campos Nome Completo, E-mail e Instituição de Origem. | Depois de ter orientador, o Aluno registra quantos coorientadores quiser: Docente do NUCOMP (recebe convite, US-36) ou Externo (só para documentação, sem acesso); o orientador é avisado. Nome Completo do coorientador externo obrigatório, só com letras, acentos e espaços, até 150 caracteres. E-mail do coorientador externo opcional, de qualquer domínio, até 100 caracteres. Instituição de Origem opcional, até 150 caracteres. |
| **CAD-10.7** | \[Exceção\] O sistema deve permitir a troca e a remoção de coorientador até o agendamento da defesa.                                                                                     | O Aluno substitui ou remove coorientador até o agendamento da defesa; o vínculo antigo fica no histórico e o removido perde o acesso.                                                                                                                                                                                                                                                                                                     |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Coorientadores sem limite de quantidade: docente do NUCOMP
> selecionado em lista; externo com Nome Completo obrigatório e E-mail e
> Instituição de Origem opcionais.
>
> 2\. Substituição e remoção de coorientador permitidas apenas até o
> agendamento da defesa.

***Cenário 1: coorientador do NUCOMP registrado (fluxo principal)***

> **Dado que** o Aluno está autenticado e tem orientador vinculado
>
> **Quando** aciona o botão Registrar coorientador, seleciona Docente do
> NUCOMP, seleciona um docente e aciona o botão Salvar
>
> **Então** o coorientador aparece com "Aguardando Aceite", o docente
> recebe o convite e o Orientador é notificado

***Cenário 2: coorientador externo (fluxo alternativo A)***

> **Dado que** o Aluno tem orientador vinculado
>
> **Quando** seleciona Externo ao NUCOMP, preenche Nome Completo, E-mail
> e Instituição de Origem e aciona o botão Salvar
>
> **Então** o coorientador é registrado sem acesso ao sistema e o
> Orientador é notificado

***Cenário 3: coorientador externo apenas com Nome (fluxo alternativo
A)***

> **Dado que** o Aluno selecionou Externo ao NUCOMP
>
> **Quando** preenche apenas o Nome Completo e aciona o botão Salvar
>
> **Então** o coorientador é registrado sem e-mail e sem instituição,
> porque esses campos são opcionais

***Cenário 4: segundo coorientador (fluxo alternativo B)***

> **Dado que** o trabalho já tem um coorientador
>
> **Quando** o Aluno registra outro coorientador
>
> **Então** a seção Orientação exibe os dois coorientadores

***Cenário 5: cancelamento do convite (fluxo alternativo C)***

> **Dado que** o convite de coorientação está "Aguardando Aceite"
>
> **Quando** o Aluno aciona o botão Remover no coorientador e confirma
>
> **Então** o convite é cancelado e o docente não pode mais aceitá-lo

***Cenário 6: substituir coorientador (fluxo alternativo D)***

> **Dado que** o trabalho tem o coorientador do NUCOMP X e não tem
> sessão de defesa agendada
>
> **Quando** o Aluno aciona o botão Substituir em X e registra o
> coorientador Z
>
> **Então** Z é registrado, o vínculo de X é registrado no histórico e o
> Orientador e X são notificados

***Cenário 7: remover coorientador (fluxo alternativo E)***

> **Dado que** o trabalho tem o coorientador do NUCOMP X
>
> **Quando** o Aluno aciona o botão Remover em X e confirma
>
> **Então** X é removido da seção Orientação, perde o acesso ao trabalho
> e é notificado

***Cenário 8: acesso sem estar autenticado (E1)***

> **Dado que** o Aluno não está autenticado
>
> **Quando** tenta abrir a aba Meu TCC
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre a aba Meu TCC na seção Orientação

***Cenário 9: coorientador antes do orientador (E2)***

> **Dado que** o Aluno ainda não tem orientador vinculado
>
> **Quando** abre a seção Orientação
>
> **Então** o botão Registrar coorientador não aparece

***Cenário 10: coorientador repetido (E3)***

> **Dado que** o docente X já é coorientador do trabalho
>
> **Quando** o Aluno abre a lista de Docentes do NUCOMP para registrar
> outro coorientador
>
> **Então** o docente X não aparece na lista

***Cenário 11: coorientador externo sem Nome (E4)***

> **Dado que** o Aluno selecionou Externo ao NUCOMP
>
> **Quando** preenche E-mail e Instituição de Origem, deixa o Nome
> Completo em branco e aciona o botão Salvar
>
> **Então** o sistema não salva e destaca o Nome Completo como
> obrigatório

***Cenário 12: substituição ou remoção bloqueada (E5)***

> **Dado que** a defesa do TCC está Agendada
>
> **Quando** o Aluno abre a seção Orientação
>
> **Então** os botões Substituir e Remover aparecem desabilitados

***Cenário 13: aluno Desistente (E6)***

> **Dado que** o TCC do Aluno está com o Status Desistente
>
> **Quando** o Aluno abre a seção Orientação
>
> **Então** a seção aparece apenas para consulta, sem os botões
> Registrar coorientador, Substituir e Remover

***Cenário 14: turma arquivada (E7)***

> **Dado que** a turma do aluno foi arquivada
>
> **Quando** o Aluno abre a seção Orientação em Turmas arquivadas
>
> **Então** os coorientadores aparecem apenas para consulta, sem os
> botões Registrar coorientador, Substituir e Remover

**Tela no protótipo**

**Tela:** Orientação do TCC: registro de coorientadores



**Diagrama de sequência**

**Diagrama relacionado:** Indicação e aceite de orientador e
coorientador

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[x\] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-36 Aceitar ou recusar o convite de coorientação e acompanhar o trabalho no painel de orientandos

| **Épico:**                | Cadastro e Manutenção                        |
|---------------------------|----------------------------------------------|
| **Feature:**              | Orientação, Atas e Publicações               |
| **Requisitos da matriz:** | RBN-CAD-10.3, RBN-CAD-10.4, RBN-CAD-11.4     |
| **Prioridade (MoSCoW):**  | Must Have (CAD-10.3 e CAD-10.4: Should Have) |
| **Responsável:**          | Leandra Matos                                |

**Descrição**

Como Docente do NUCOMP, quero aceitar ou recusar o convite de
coorientação e, após o aceite, acompanhar o trabalho no painel de
orientandos, para que eu participe da orientação do aluno.

**Atores**

> **Ator principal:** Docente do NUCOMP indicado como coorientador. Ao
> aceitar, passa a ser Coorientador do trabalho.
>
> **Atores secundários:** Aluno (registra o coorientador, pode cancelar
> o convite e recebe o resultado) e Orientador (recebe o resultado).

**Pré-condições**

- O Aluno registrou o docente como coorientador do tipo Docente do
  > NUCOMP (US-45), e o convite está "Aguardando Aceite".

- O sistema já enviou ao docente o convite por e-mail e no sistema
  > (ícone de sino), com o nome do aluno, o título do trabalho e o link
  > do convite.

- Para responder, o docente precisa estar autenticado no sistema, com o
  > Status da Conta Ativa (US-11). O convite nunca é respondido pelo
  > e-mail: o e-mail contém apenas o link que abre o sistema. Sem sessão
  > ativa, aplica-se o E1.

**Fluxo principal**

> 1\. No menu lateral do sistema, o docente seleciona o item
> Orientações.
>
> 2\. O sistema abre a tela Orientações. Na parte superior, encontra-se
> a seção Convites de coorientação, com uma linha por convite exibindo o
> nome do aluno, o título do trabalho, a turma, o nome do Orientador e
> os botões Recusar e Aceitar.
>
> 3\. O docente aciona o botão Aceitar na linha do convite. Não há
> campos para preencher.
>
> 4\. O sistema registra o aceite com o docente, a data e a hora e
> vincula o docente como Coorientador do trabalho.
>
> 5\. O sistema envia ao Aluno e ao Orientador uma notificação no
> sistema com o aceite.
>
> 6\. O sistema mantém o docente na tela Orientações, exibe "Convite
> aceito", remove o convite da seção e exibe o trabalho no Painel de
> orientandos com o Papel Coorientador, o Status do TCC, o status das
> entregas e as ações Atas e Registrar ata (US-19). O fluxo termina.

**Fluxos alternativos**

> A. Entrada pelo e-mail (passo 1): no e-mail (fora do sistema), o
> docente acessa o link do convite. O navegador abre o SIGTCC na tela
> Orientações, com o convite na seção Convites de coorientação, e o
> fluxo prossegue a partir do passo 3. Se o docente não estiver
> autenticado, aplica-se o E1.
>
> B. Entrada pela notificação no sistema (passo 1): já dentro do
> sistema, o docente seleciona o ícone de notificações (sino) e, em
> seguida, a notificação do convite. O sistema abre a tela Orientações,
> e o fluxo prossegue a partir do passo 2.
>
> C. Recusa (passo 3): o docente aciona o botão Recusar, sem preencher
> campos. O sistema remove o docente da lista de coorientadores do
> trabalho, registra a recusa no histórico com o docente, a data e a
> hora e notifica o Aluno no sistema, que pode indicar outro
> coorientador (US-45). O docente permanece na tela Orientações, com a
> mensagem "Convite recusado". O fluxo termina.
>
> D. Remoção ou substituição posterior (US-45; passo 6): se o Aluno
> remove ou substitui o coorientador, o trabalho é removido do Painel de
> orientandos do docente e ele perde o acesso às atas. O fluxo termina.
>
> E. Coorientador externo ao NUCOMP (passo 1): não recebe convite,
> porque não tem acesso ao sistema. O fluxo termina.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o docente tente acessar a
> tela Orientações sem sessão ativa (pelo menu, pelo endereço da página
> ou por um link recebido), o sistema apresenta a tela de login (US-11).
> Após a autenticação, o sistema exibe a tela Orientações, na seção
> Convites de coorientação, e o fluxo prossegue a partir do passo 2. Em
> caso de falha na autenticação, aplicam-se as exceções da US-11.
>
> E2. Convite de outro docente (passo 2): se quem está autenticado não é
> o docente convidado, o sistema exibe "Este convite não está disponível
> para o seu usuário" e não exibe os botões. O fluxo termina.
>
> E3. Convite cancelado pelo Aluno (CAD-10.4; passo 2): o convite é
> removido da seção. Pelo link do e-mail, o sistema exibe "Este convite
> foi cancelado pelo aluno" e não exibe os botões. O fluxo termina.
>
> E4. Convite já respondido (passo 2): pelo link do e-mail, o sistema
> exibe a decisão registrada (Aceito ou Recusado), com a data e a hora,
> e não exibe os botões. O fluxo termina.
>
> E5. Convite pendente (passo 2): enquanto o convite está "Aguardando
> Aceite", ele não conta como coorientação, e o trabalho não aparece no
> Painel de orientandos nem nas atas do docente. O fluxo prossegue a
> partir do passo 3 somente após o aceite.

**Pós-condições**

- No aceite, o docente foi vinculado como Coorientador do trabalho, o
  > aceite foi registrado e o trabalho foi incluído no Painel de
  > orientandos com o Papel Coorientador. O Aluno e o Orientador foram
  > notificados.

- Na recusa, o docente foi removido da lista de coorientadores, a recusa
  > foi registrada no histórico e o Aluno foi notificado.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                                                   | **Resumo da regra em uma frase**                                                                                                                                   |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-10.3** | O sistema deve permitir que o Aluno registre coorientadores, com o formulário de coorientador externo ao NUCOMP que deve conter os campos Nome Completo, E-mail e Instituição de Origem.  | O Aluno registra um docente do NUCOMP como coorientador; o docente só vê o trabalho depois de aceitar.                                                             |
| **CAD-10.4** | O sistema deve permitir que o docente do NUCOMP indicado como coorientador aceite ou recuse a coorientação.                                                                               | Convite por e-mail e no sistema com Aceitar e Recusar; enquanto pendente aparece "Aguardando Aceite", pode ser cancelado pelo aluno e não conta como coorientação. |
| **CAD-11.4** | O sistema deve permitir ao Orientador visualizar seu painel de orientandos e, quando houver coorientação aceita, ao Coorientador do NUCOMP visualizar seus coorientandos no mesmo painel. | O coorientador vê no painel, com o papel Coorientador, só os trabalhos cuja coorientação aceitou.                                                                  |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Convite por e-mail e no sistema, com os botões Aceitar e Recusar.
>
> 2\. Após o aceite, vê o painel de coorientandos (status, entregas e
> atas) e registra atas.
>
> 3\. Na recusa, o docente é removido da lista de coorientadores, a
> recusa é registrada no histórico e o aluno pode indicar outro
> coorientador.

***Cenário 1: aceite do convite pela tela Orientações (fluxo
principal)***

> **Dado que** o docente está autenticado e tem um convite "Aguardando
> Aceite"
>
> **Quando** seleciona o item Orientações no menu lateral e em Aceitar
> na linha do convite
>
> **Então** passa a ser Coorientador, o sistema exibe "Convite aceito" e
> o trabalho aparece no Painel de orientandos com o Papel Coorientador
>
> **E** o Aluno e o Orientador são notificados

***Cenário 2: entrada pelo link do e-mail (fluxo alternativo A)***

> **Dado que** o docente está autenticado e recebeu o e-mail do convite
>
> **Quando** acessa o link do convite no e-mail
>
> **Então** o navegador abre o SIGTCC na tela Orientações, com o convite
> na seção Convites de coorientação

***Cenário 3: entrada pela notificação no sistema (fluxo alternativo
B)***

> **Dado que** o docente está autenticado e o ícone de sino exibe a
> notificação do convite
>
> **Quando** seleciona o ícone de notificações e, em seguida, a
> notificação
>
> **Então** o sistema abre a tela Orientações com o convite na seção
> Convites de coorientação

***Cenário 4: recusa do convite (fluxo alternativo C)***

> **Dado que** o docente tem um convite "Aguardando Aceite"
>
> **Quando** aciona o botão Recusar
>
> **Então** é removido da lista de coorientadores do trabalho, a recusa
> é registrada no histórico e o sistema exibe "Convite recusado"
>
> **E** o Aluno é notificado e pode indicar outro coorientador

***Cenário 5: remoção posterior (fluxo alternativo D)***

> **Dado que** o docente é Coorientador do trabalho
>
> **Quando** o Aluno o remove da coorientação
>
> **Então** o trabalho é removido do Painel de orientandos do docente e
> ele perde o acesso às atas

***Cenário 6: coorientador externo (fluxo alternativo E)***

> **Dado que** o Aluno registrou um coorientador Externo ao NUCOMP
>
> **Quando** o registro é salvo
>
> **Então** nenhum convite é enviado

***Cenário 7: acesso pelo link sem estar autenticado (E1)***

> **Dado que** o docente não está autenticado
>
> **Quando** acessa o link do convite no e-mail
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre a tela Orientações com o convite na seção
> Convites de coorientação

***Cenário 8: convite de outro docente (E2)***

> **Dado que** o docente Z está autenticado e abre o link de um convite
> feito ao docente Y
>
> **Quando** o sistema carrega a página
>
> **Então** exibe "Este convite não está disponível para o seu usuário"
> e não exibe os botões

***Cenário 9: convite cancelado pelo aluno (E3)***

> **Dado que** o convite está "Aguardando Aceite"
>
> **Quando** o Aluno cancela o convite e o docente abre o link do e-mail
>
> **Então** o sistema exibe "Este convite foi cancelado pelo aluno" e o
> docente não pode mais aceitar

***Cenário 10: convite já respondido (E4)***

> **Dado que** o docente já recusou o convite
>
> **Quando** abre novamente o link do convite no e-mail
>
> **Então** o sistema exibe "Recusado", com a data e a hora, e não exibe
> os botões

***Cenário 11: convite pendente (E5)***

> **Dado que** o convite está "Aguardando Aceite"
>
> **Quando** o docente abre o Painel de orientandos
>
> **Então** o trabalho não aparece no painel

**Tela no protótipo**

**Tela:** Convite de coorientação e Painel de orientandos



**Diagrama de sequência**

**Diagrama relacionado:** Indicação e aceite de orientador e
coorientador

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[x\] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-19 Registrar, consultar, editar e comentar atas de orientação

| **Épico:**                | Cadastro e Manutenção          |
|---------------------------|--------------------------------|
| **Feature:**              | Orientação, Atas e Publicações |
| **Requisitos da matriz:** | RBN-CAD-11.1, RBN-CAD-11.2     |
| **Prioridade (MoSCoW):**  | Must Have                      |
| **Responsável:**          | Leandra Matos                  |

**Descrição**

Como Aluno, Orientador ou Coorientador, quero registrar, consultar e
editar as atas dos encontros de orientação, e, como Orientador ou
Coorientador, comentá-las, para que a assiduidade fique comprovada.

**Atores**

> **Ator principal:** Aluno, que registra a ata na maior parte das
> vezes.
>
> **Atores secundários:** Orientador e Coorientador do NUCOMP com
> coorientação aceita (também registram, editam e comentam) e Professor
> da Disciplina (apenas consulta).

**Pré-condições**

- O usuário está autenticado, com o Status da Conta Ativa (US-11). Sem
  > sessão ativa, aplica-se o E1.

- O Aluno está vinculado a uma turma não arquivada (US-08). Com a turma
  > arquivada, aplica-se o E7.

- Para o Orientador, o aluno é seu orientando. Para o Coorientador, a
  > coorientação foi aceita (US-36); com o convite pendente, aplica-se o
  > E8.

**Fluxo principal**

> 1\. No menu lateral do sistema, o Aluno acessa o item Turmas,
> seleciona a sua turma, abre a aba Meu TCC e acessa a seção Atas de
> orientação.
>
> 2\. O sistema exibe a quantidade de encontros registrados e os botões
> Registrar ata e Ver atas.
>
> 3\. O Aluno aciona o botão Registrar ata. O sistema abre a janela
> Registrar ata de orientação com os campos Data do Encontro, Pauta
> Discutida e Metas Acordadas e os botões Cancelar e Salvar.
>
> 4\. O Aluno seleciona a Data do Encontro no calendário (DD/MM/AAAA,
> sem data futura).
>
> 5\. O Aluno informa a Pauta Discutida (obrigatória, até 2.000
> caracteres) e as Metas Acordadas (obrigatórias, até 2.000 caracteres)
> e aciona o botão Salvar.
>
> 6\. O sistema valida os campos (E2 a E4) e grava a ata no histórico de
> atas do aluno.
>
> 7\. O sistema fecha a janela e mantém o Aluno na aba Meu TCC, com a
> mensagem "Ata registrada" e a quantidade de encontros atualizada.
>
> 8\. O sistema exibe a ata no topo do histórico de atas, visível ao
> Aluno, ao Orientador, ao Coorientador com coorientação aceita e ao
> Professor da Disciplina. O fluxo termina.

**Fluxos alternativos**

> A. Ata registrada pelo Orientador (passo 1): no item Orientações do
> menu lateral, no Painel de orientandos, o Orientador aciona o botão
> Registrar ata na linha do aluno. O sistema abre a mesma janela do
> passo 3, e o fluxo prossegue com os passos 4 a 6. O Orientador
> permanece no Painel de orientandos.
>
> B. Ata registrada pelo Coorientador do NUCOMP (passo 1): igual ao
> fluxo A, pela linha do trabalho com o Papel Coorientador.
>
> C. Consulta das atas (passo 2): o Aluno aciona o link Ver atas (ou o
> Orientador e o Coorientador acionam o link Atas na linha do aluno). O
> sistema exibe a lista da ata mais recente para a mais antiga, com Data
> do Encontro, Pauta Discutida, Metas Acordadas e comentários (com o
> autor, a data e a hora de cada comentário), e os botões Editar e
> Comentar, conforme o perfil. O fluxo termina.
>
> D. Comentário (fluxo alternativo C): na lista de atas, o Orientador ou
> o Coorientador aciona o botão Comentar na ata, informa o Comentário
> (até 1.000 caracteres) e aciona o botão Salvar. O comentário aparece
> abaixo da ata. O fluxo termina.
>
> E. Edição (fluxo alternativo C): na lista de atas, o Aluno, o
> Orientador ou o Coorientador aciona o botão Editar na ata. O sistema
> abre a mesma janela do passo 3 com os dados atuais, e as regras são as
> mesmas. O fluxo prossegue a partir do passo 6.
>
> F. Consulta pelo Professor da Disciplina (passo 1): no menu lateral, o
> Professor acessa o item Turmas, seleciona a turma, abre a aba Alunos,
> seleciona o bloco do aluno e, no painel do aluno, abre as atas, apenas
> para leitura. O fluxo termina.
>
> G. Aluno sem orientador (passo 8): enquanto o Aluno não tem orientador
> vinculado, a ata registrada fica visível ao Aluno e ao Professor da
> Disciplina. Após o vínculo do orientador (US-18) ou do coorientador
> (US-36), as atas anteriores passam a ser visíveis também a eles. O
> fluxo termina.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o usuário tente acessar a
> aba Meu TCC ou a tela Orientações sem sessão ativa (pelo menu, pelo
> endereço da página ou por um link recebido), o sistema apresenta a
> tela de login (US-11). Após a autenticação, o sistema exibe a tela que
> o usuário tentou abrir, e o fluxo prossegue a partir do passo 2. Em
> caso de falha na autenticação, aplicam-se as exceções da US-11.
>
> E2. Data futura (passo 6): a Data do Encontro é posterior a hoje. O
> sistema não salva e exibe "A Data do Encontro não pode ser futura".
> Retorna ao passo 4.
>
> E3. Campo em branco (passo 6): Data do Encontro, Pauta Discutida ou
> Metas Acordadas sem preenchimento. O sistema não salva e destaca o
> campo. Retorna ao passo 4.
>
> E4. Texto acima do limite (passo 6): Pauta Discutida ou Metas
> Acordadas com mais de 2.000 caracteres, ou Comentário com mais de
> 1.000. O sistema não salva e informa o limite. Retorna ao passo 5.
>
> E5. Aluno sem a opção de comentar (fluxo alternativo C): na lista de
> atas, o Aluno visualiza o botão Editar, mas não o botão Comentar. O
> fluxo termina.
>
> E6. Professor da Disciplina sem edição (fluxo alternativo F): o
> Professor visualiza as atas sem os botões Registrar ata, Editar e
> Comentar. O fluxo termina.
>
> E7. Turma arquivada (passo 2): as atas permanecem disponíveis apenas
> para consulta, sem os botões Registrar ata, Editar e Comentar. O fluxo
> termina.
>
> E8. Coorientador com convite pendente (fluxo alternativo B): enquanto
> o convite está "Aguardando Aceite", o docente não visualiza as atas do
> trabalho. O fluxo termina.

**Pós-condições**

- A ata foi gravada e incluída no topo do histórico de atas do aluno.

- A quantidade de encontros registrados foi atualizada.

- Na edição e no comentário, a ata foi atualizada com o novo conteúdo ou
  > com o comentário.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                              | **Resumo da regra em uma frase**                                                                                                                                                                                                                               |
|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-11.1** | O sistema deve mostrar um formulário de registro da ata de orientação que deve conter os campos Data do Encontro, Pauta Discutida e Metas Acordadas. | Data do Encontro no calendário, sem data futura; a ata é registrada pelo Aluno, pelo Orientador ou pelo Coorientador do NUCOMP com coorientação aceita. Pauta Discutida obrigatória, até 2.000 caracteres. Metas Acordadas obrigatórias, até 2.000 caracteres. |
| **CAD-11.2** | O sistema deve permitir a consulta, a edição e o registro de comentários nas atas de orientação.                                                     | Histórico de atas do mais recente para o mais antigo, visto pelo Aluno, Orientador, Coorientador e Professor da Disciplina; Aluno, Orientador e Coorientador editam; Orientador e Coorientador comentam (até 1.000 caracteres).                                |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Formulário exige Data, Pauta e Metas Acordadas.
>
> 2\. O Orientador e o Coorientador podem adicionar comentários à ata.

***Cenário 1: ata registrada pelo Aluno (fluxo principal)***

> **Dado que** o Aluno está autenticado, tem orientador vinculado e está
> na seção Atas de orientação da aba Meu TCC
>
> **Quando** aciona o botão Registrar ata, seleciona a Data do Encontro
> de ontem, preenche Pauta Discutida e Metas Acordadas e aciona o botão
> Salvar
>
> **Então** o sistema exibe "Ata registrada" e a ata aparece no topo do
> histórico para o Aluno, o Orientador e o Professor da Disciplina

***Cenário 2: ata registrada pelo Orientador (fluxo alternativo A)***

> **Dado que** o Orientador está no Painel de orientandos
>
> **Quando** aciona o botão Registrar ata na linha do aluno, preenche os
> campos e aciona o botão Salvar
>
> **Então** a ata aparece no topo do histórico de atas do aluno

***Cenário 3: ata registrada pelo Coorientador (fluxo alternativo B)***

> **Dado que** o docente aceitou a coorientação do trabalho
>
> **Quando** aciona o botão Registrar ata na linha do trabalho, preenche
> os campos e aciona o botão Salvar
>
> **Então** a ata aparece no topo do histórico de atas do aluno

***Cenário 4: consulta das atas (fluxo alternativo C)***

> **Dado que** o aluno tem 3 atas registradas
>
> **Quando** o Aluno aciona o link Ver atas
>
> **Então** o sistema exibe as 3 atas, da mais recente para a mais
> antiga, com os comentários de cada uma

***Cenário 5: comentário do Orientador (fluxo alternativo D)***

> **Dado que** existe uma ata registrada pelo Aluno
>
> **Quando** o Orientador aciona o botão Comentar, escreve um comentário
> e aciona o botão Salvar
>
> **Então** o comentário aparece abaixo da ata

***Cenário 6: edição da ata (fluxo alternativo E)***

> **Dado que** existe uma ata registrada pelo Aluno
>
> **Quando** o Aluno aciona o botão Editar, altera as Metas Acordadas e
> aciona o botão Salvar
>
> **Então** a ata exibe as novas Metas Acordadas

***Cenário 7: consulta pelo Professor da Disciplina (fluxo alternativo
F)***

> **Dado que** o Professor da Disciplina abriu o painel de um aluno da
> turma
>
> **Quando** abre as atas
>
> **Então** visualiza as atas apenas para leitura

***Cenário 8: ata registrada sem orientador (fluxo alternativo G)***

> **Dado que** o Aluno ainda não tem orientador vinculado
>
> **Quando** registra uma ata
>
> **Então** a ata fica visível ao Aluno e ao Professor da Disciplina
>
> **E**, após o aceite do orientador, passa a ser visível também a ele

***Cenário 9: acesso sem estar autenticado (E1)***

> **Dado que** o Aluno não está autenticado
>
> **Quando** tenta abrir a aba Meu TCC
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre a aba Meu TCC na seção Atas de orientação

***Cenário 10: data futura (E2)***

> **Dado que** o Aluno está na janela Registrar ata de orientação
>
> **Quando** seleciona a Data do Encontro de amanhã e aciona o botão
> Salvar
>
> **Então** o sistema não salva e exibe "A Data do Encontro não pode ser
> futura"

***Cenário 11: campo em branco (E3)***

> **Dado que** o Aluno está na janela Registrar ata de orientação
>
> **Quando** deixa as Metas Acordadas em branco e aciona o botão Salvar
>
> **Então** o sistema não salva e destaca o campo Metas Acordadas

***Cenário 12: texto acima do limite (E4)***

> **Dado que** o Orientador está comentando uma ata
>
> **Quando** informa um comentário com 1.001 caracteres e aciona o botão
> Salvar
>
> **Então** o sistema não salva e informa o limite de 1.000 caracteres

***Cenário 13: Aluno sem a opção de comentar (E5)***

> **Dado que** existe uma ata registrada
>
> **Quando** o Aluno abre a lista de atas
>
> **Então** visualiza o botão Editar, mas não o botão Comentar

***Cenário 14: Professor da Disciplina sem edição (E6)***

> **Dado que** existe uma ata registrada
>
> **Quando** o Professor da Disciplina abre as atas do aluno
>
> **Então** não visualiza os botões Registrar ata, Editar e Comentar

***Cenário 15: turma arquivada (E7)***

> **Dado que** a turma do aluno foi arquivada
>
> **Quando** o Orientador abre as atas
>
> **Então** as atas aparecem apenas para consulta

***Cenário 16: coorientador com convite pendente (E8)***

> **Dado que** o convite de coorientação está "Aguardando Aceite"
>
> **Quando** o docente procura as atas do trabalho
>
> **Então** o trabalho e as atas não aparecem para ele

**Tela no protótipo**

**Tela:** Atas de orientação



**Diagrama de sequência**

**Diagrama relacionado:** sem diagrama próprio, por ser um cadastro
simples com consulta.

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[x\] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-46 Registrar a publicação do artigo

| **Épico:**                | Cadastro e Manutenção          |
|---------------------------|--------------------------------|
| **Feature:**              | Orientação, Atas e Publicações |
| **Requisitos da matriz:** | RBN-CAD-12.1                   |
| **Prioridade (MoSCoW):**  | Must Have                      |
| **Responsável:**          | Leandra Matos                  |

**Descrição**

Como Aluno, quero registrar e atualizar a publicação do artigo do meu
TCC, com veículo, link ou DOI, estrato Qualis/CAPES e status de
submissão, para que o Coordenador de Curso possa analisar o
aproveitamento do artigo.

**Atores**

> **Ator principal:** Aluno.
>
> **Atores secundários:** Orientador, que também pode registrar e
> atualizar a publicação.

**Pré-condições**

- O Aluno está autenticado, com o Status da Conta Ativa (US-11). Sem
  > sessão ativa, aplica-se o E1.

- O TCC está na modalidade Artigo Científico (US-13); na modalidade
  > Monografia, aplica-se o E4.

- Cada TCC tem um único registro de publicação.

**Fluxo principal**

> 1\. No menu lateral do sistema, o Aluno acessa o item Turmas,
> seleciona a sua turma, abre a aba Meu TCC e acessa a seção Publicação
> do artigo.
>
> 2\. O sistema exibe a etiqueta de aproveitamento, os campos Veículo de
> Publicação, Link ou DOI, Estrato Qualis/CAPES e Status de Submissão e
> o botão Salvar publicação.
>
> 3\. O Aluno informa o Veículo de Publicação (até 150 caracteres) e
> insere no campo Link ou DOI o endereço iniciado por https://
> (obrigatório, até 500 caracteres; pode ser o link da publicação, o DOI
> ou um arquivo público para conferência).
>
> 4\. O Aluno seleciona o Estrato Qualis/CAPES na lista (A1, A2, A3, A4,
> B1, B2, B3, B4 ou C) e o Status de Submissão na lista (Submetido, Em
> Revisão, Aceito, Publicado ou Rejeitado) e aciona o botão Salvar
> publicação.
>
> 5\. O sistema valida os campos (E2 e E3) e grava o registro de
> publicação do TCC.
>
> 6\. O sistema mantém o Aluno na aba Meu TCC, com a mensagem
> "Publicação salva". Com o Status de Submissão Aceito ou Publicado, a
> etiqueta de aproveitamento exibe Em Análise e o artigo passa a constar
> do painel do Coordenador de Curso (US-20). O fluxo termina.

**Fluxos alternativos**

> A. Publicação registrada pelo Orientador (passo 1): no item
> Orientações do menu lateral, no Painel de orientandos, o Orientador
> aciona o link Publicação na linha do aluno. O sistema abre a mesma
> seção do passo 2. O fluxo prossegue a partir do passo 3.
>
> B. Status Submetido, Em Revisão ou Rejeitado (passo 6): o registro é
> gravado, mas o artigo não aparece no painel de análise do Coordenador.
> O fluxo termina.
>
> C. Atualização após a análise (passo 4): se o Aluno ou o Orientador
> altera o Estrato Qualis/CAPES, o Status de Submissão ou o Link ou DOI
> de um artigo já analisado e aciona o botão Salvar publicação, a
> decisão do Coordenador é desfeita e o aproveitamento retorna para Em
> Análise. O fluxo prossegue a partir do passo 5.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o Aluno tente acessar a
> aba Meu TCC sem sessão ativa (pelo menu, pelo endereço da página ou
> por um link recebido), o sistema apresenta a tela de login (US-11).
> Após a autenticação, o sistema exibe a aba Meu TCC da turma, na seção
> Publicação do artigo, e o fluxo prossegue a partir do passo 2. Em caso
> de falha na autenticação, aplicam-se as exceções da US-11.
>
> E2. Link ou DOI inválido (passo 5): o campo está vazio, não começa com
> https:// ou tem mais de 500 caracteres. O sistema não salva, destaca o
> campo e exibe "O link deve começar com https:// e ter até 500
> caracteres". Retorna ao passo 3.
>
> E3. Veículo de Publicação acima do limite (passo 5): mais de 150
> caracteres. O sistema não salva e informa o limite. Retorna ao passo
> 3.
>
> E4. Modalidade Monografia (passo 1): a aba Meu TCC não exibe a seção
> Publicação do artigo. O fluxo termina.

**Pós-condições**

- O registro de publicação foi gravado no TCC.

- Com o Status de Submissão Aceito ou Publicado, o aproveitamento foi
  > registrado como Em Análise.

- Na atualização de um artigo já analisado, a decisão anterior foi
  > desfeita.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                                | **Resumo da regra em uma frase**                                                                                                                                                                                                                                                                                                                                                                       |
|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-12.1** | O sistema deve mostrar um formulário de publicação do artigo que deve conter os campos Veículo de Publicação, Link ou DOI, Estrato Qualis/CAPES e Status de Submissão. | Veículo de Publicação em texto de até 150 caracteres; o formulário só aparece na modalidade Artigo Científico, é preenchido pelo Aluno ou pelo Orientador e há um registro por TCC. Link ou DOI obrigatório, iniciado por https://, com até 500 caracteres. Estrato Qualis/CAPES em lista: A1 a A4, B1 a B4 ou C. Status de Submissão em lista: Submetido, Em Revisão, Aceito, Publicado ou Rejeitado. |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Formulário do aluno com Veículo de Publicação, Link ou DOI
> (obrigatório), Estrato Qualis/CAPES e Status de Submissão.
>
> 2\. O formulário aparece apenas na modalidade Artigo Científico.

***Cenário 1: registro da publicação pelo Aluno (fluxo principal)***

> **Dado que** o Aluno está autenticado e o TCC está na modalidade
> Artigo Científico
>
> **Quando** preenche Veículo de Publicação, Link ou DOI iniciado por
> https://, Estrato Qualis/CAPES B1 e Status de Submissão Aceito e
> aciona o botão Salvar publicação
>
> **Então** o registro é gravado, o sistema exibe "Publicação salva" e o
> aproveitamento exibe Em Análise

***Cenário 2: publicação registrada pelo Orientador (fluxo alternativo
A)***

> **Dado que** o Orientador está no Painel de orientandos
>
> **Quando** aciona o link Publicação na linha do aluno, preenche os
> campos e aciona o botão Salvar publicação
>
> **Então** o registro de publicação é gravado no TCC do aluno

***Cenário 3: artigo ainda em revisão (fluxo alternativo B)***

> **Dado que** o Aluno salvou a publicação com o Status de Submissão Em
> Revisão
>
> **Quando** o Coordenador abre o painel Aproveitamento de artigos
>
> **Então** o artigo não aparece na lista

***Cenário 4: atualização desfaz a decisão (fluxo alternativo C)***

> **Dado que** o artigo foi homologado
>
> **Quando** o Aluno muda o Estrato Qualis/CAPES e aciona o botão Salvar
> publicação
>
> **Então** a homologação é desfeita e o aproveitamento retorna para Em
> Análise

***Cenário 5: acesso sem estar autenticado (E1)***

> **Dado que** o Aluno não está autenticado
>
> **Quando** tenta abrir a aba Meu TCC
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre a seção Publicação do artigo

***Cenário 6: link inválido (E2)***

> **Dado que** o Aluno está na seção Publicação do artigo
>
> **Quando** informa um Link ou DOI sem https://, ou deixa o campo em
> branco, e aciona o botão Salvar publicação
>
> **Então** o sistema não salva e destaca o campo Link ou DOI

***Cenário 7: Veículo de Publicação acima do limite (E3)***

> **Dado que** o Aluno está na seção Publicação do artigo
>
> **Quando** informa um Veículo de Publicação com 151 caracteres e
> aciona o botão Salvar publicação
>
> **Então** o sistema não salva e informa o limite de 150 caracteres

***Cenário 8: monografia sem formulário (E4)***

> **Dado que** o TCC está na modalidade Monografia
>
> **Quando** o Aluno abre a aba Meu TCC
>
> **Então** a seção Publicação do artigo não aparece

**Tela no protótipo**

**Tela:** Meu TCC: Publicação do artigo  


**Diagrama de sequência**

**Diagrama relacionado:** sem diagrama próprio: cadastro e decisão
simples; a nota mínima entra no diagrama "Lançamento de notas e
liberação do resultado".

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[x\] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-20 Homologar ou recusar o aproveitamento do artigo

| **Épico:**                | Cadastro e Manutenção          |
|---------------------------|--------------------------------|
| **Feature:**              | Orientação, Atas e Publicações |
| **Requisitos da matriz:** | RBN-CAD-12.2, RBN-CAD-12.3     |
| **Prioridade (MoSCoW):**  | Must Have                      |
| **Responsável:**          | Leandra Matos                  |

**Descrição**

Como Coordenador de Curso, quero analisar os artigos Aceitos ou
Publicados dos alunos do meu curso e homologar ou recusar o
aproveitamento de cada um, para que o artigo homologado em Qualis A ou B
garanta a nota mínima do TCC.

**Atores**

> **Ator principal:** Coordenador de Curso.
>
> **Atores secundários:** Não há atores secundários.

**Pré-condições**

- O Coordenador de Curso está autenticado, com o Status da Conta Ativa
  > (US-11). Sem sessão ativa, aplica-se o E1.

- O Aluno ou o Orientador registrou a publicação com o Status de
  > Submissão Aceito ou Publicado (US-46).

- O aluno é do curso que o Coordenador coordena; para artigo de outro
  > curso, aplica-se o E2.

**Fluxo principal**

> 1\. No menu lateral do sistema, na área Gestão, o Coordenador de Curso
> seleciona o item Aproveitamento de artigos.
>
> 2\. O sistema abre o painel com o filtro Curso (Engenharia de
> Computação, Sistemas de Informação, Licenciatura em Computação ou
> Todos), já com o curso do Coordenador, e uma linha por artigo Aceito
> ou Publicado, com Aluno, Orientador, Título do TCC, Veículo de
> Publicação, Estrato Qualis/CAPES, o link abrir, o aproveitamento (Em
> Análise, Homologado ou Recusado) e os botões Homologar e Recusar.
>
> 3\. O Coordenador aciona o link abrir. O artigo abre fora do SIGTCC,
> no endereço informado, onde o Coordenador confere os critérios do
> curso.
>
> 4\. Ao retornar ao painel, o Coordenador aciona o botão Homologar na
> linha do artigo. Não há campos para preencher.
>
> 5\. O sistema registra a homologação com o Coordenador, a data e a
> hora e muda o aproveitamento para Homologado.
>
> 6\. O sistema mantém o Coordenador no painel, com a mensagem
> "Aproveitamento homologado". Com Qualis A ou B, na liberação do
> resultado (US-27) a nota final mínima do TCC é 6,0, em TCC 1 e em TCC
> 2, e a apresentação perante a banca permanece obrigatória. O fluxo
> termina.

**Fluxos alternativos**

> A. Recusa (passo 4): o Coordenador aciona o botão Recusar. O sistema
> registra a recusa com o Coordenador, a data e a hora e muda o
> aproveitamento para Recusado. Não há nota mínima. O Coordenador
> permanece no painel, com a mensagem "Aproveitamento recusado". O fluxo
> termina.
>
> B. Homologado com Qualis C (passo 6): o aproveitamento passa a
> Homologado, mas não garante a nota mínima; vale a nota calculada pela
> banca. O fluxo termina.
>
> C. Revisão da decisão (passo 2): até a liberação do resultado, o
> Coordenador pode acionar o botão Recusar em um artigo já Homologado. O
> fluxo prossegue como no fluxo alternativo A.
>
> D. Artigo alterado após a análise (passo 2): quando o Aluno ou o
> Orientador altera o Estrato Qualis/CAPES, o Status de Submissão ou o
> Link ou DOI (US-46), o artigo retorna ao painel com o aproveitamento
> Em Análise. O fluxo prossegue a partir do passo 3.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o Coordenador de Curso
> tente acessar o painel Aproveitamento de artigos sem sessão ativa
> (pelo menu, pelo endereço da página ou por um link recebido), o
> sistema apresenta a tela de login (US-11). Após a autenticação, o
> sistema exibe o painel Aproveitamento de artigos, e o fluxo prossegue
> a partir do passo 2. Em caso de falha na autenticação, aplicam-se as
> exceções da US-11.
>
> E2. Artigo de outro curso (passo 2): ao selecionar outro curso ou
> Todos no filtro Curso (CAD-14.1), o painel exibe os artigos desses
> cursos apenas para consulta, sem os botões Homologar e Recusar, que
> ficam disponíveis somente nos artigos do curso que o Coordenador
> coordena (CAD-12.3). O fluxo termina.
>
> E3. Recusa após a liberação do resultado (passo 4): após a liberação
> (US-27), o botão Recusar fica indisponível no artigo já Homologado,
> porque vale a homologação existente na liberação (CAD-12.3). O fluxo
> termina.
>
> E4. Usuário que não é Coordenador de Curso (passo 1): o item
> Aproveitamento de artigos não aparece no menu lateral. O fluxo
> termina.

**Pós-condições**

- O aproveitamento do artigo foi registrado como Homologado ou Recusado,
  > com o Coordenador, a data e a hora.

- Com homologação em Qualis A ou B, a nota final mínima de 6,0 passou a
  > valer para a liberação do resultado.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                          | **Resumo da regra em uma frase**                                                                                                                              |
|--------------|----------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-12.2** | O sistema deve exibir ao Coordenador de Curso um painel visual para análise do aproveitamento dos artigos Aceitos ou Publicados. | Painel do Coordenador de Curso com os artigos Aceitos ou Publicados (aluno, orientador, título, veículo, Qualis e link), com filtro de Curso.                 |
| **CAD-12.3** | O sistema deve permitir que o Coordenador de Curso homologue ou recuse o aproveitamento do artigo.                               | O Coordenador Homologa ou Recusa; homologação em Qualis A ou B garante nota final mínima 6,0 em TCC 1 e TCC 2; mudar Qualis, Status ou Link desfaz a decisão. |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Painel com os artigos Aceitos ou Publicados do curso do
> Coordenador, com filtro de Curso.
>
> 2\. Se homologado como A ou B, garante nota ≥ 6,0 em TCC 1 e TCC 2.

***Cenário 1: artigo homologado com nota mínima (fluxo principal)***

> **Dado que** o artigo tem Qualis A2 e Status Publicado e o Coordenador
> de Curso está no painel Aproveitamento de artigos
>
> **Quando** aciona o link abrir, confere o artigo e aciona o botão
> Homologar na linha do artigo
>
> **Então** o aproveitamento passa a Homologado e, na liberação do
> resultado, a nota final mínima é 6,0

***Cenário 2: recusa do aproveitamento (fluxo alternativo A)***

> **Dado que** o artigo está Em Análise no painel
>
> **Quando** o Coordenador aciona o botão Recusar
>
> **Então** o aproveitamento passa a Recusado e não há nota mínima

***Cenário 3: Qualis C (fluxo alternativo B)***

> **Dado que** o artigo foi homologado com Qualis C
>
> **Quando** o resultado da banca é liberado
>
> **Então** a nota final é a calculada pela banca, sem nota mínima
> garantida

***Cenário 4: revisão da decisão antes da liberação (fluxo alternativo
C)***

> **Dado que** o artigo está Homologado e o resultado ainda não foi
> liberado
>
> **Quando** o Coordenador aciona o botão Recusar
>
> **Então** o aproveitamento passa a Recusado

***Cenário 5: artigo alterado após a análise (fluxo alternativo D)***

> **Dado que** o artigo foi homologado e o Aluno alterou o Estrato
> Qualis/CAPES
>
> **Quando** o Coordenador abre o painel
>
> **Então** o artigo aparece com o aproveitamento Em Análise

***Cenário 6: acesso sem estar autenticado (E1)***

> **Dado que** o Coordenador de Curso não está autenticado
>
> **Quando** tenta abrir o painel Aproveitamento de artigos
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre o painel Aproveitamento de artigos

***Cenário 7: artigo de outro curso (E2)***

> **Dado que** o Coordenador coordena Engenharia de Computação
>
> **Quando** seleciona Sistemas de Informação no filtro Curso do painel
> Aproveitamento de artigos
>
> **Então** visualiza os artigos de Sistemas de Informação sem os botões
> Homologar e Recusar

***Cenário 8: recusa após a liberação (E3)***

> **Dado que** o resultado do TCC já foi liberado com o artigo
> Homologado
>
> **Quando** o Coordenador abre o painel
>
> **Então** o botão Recusar desse artigo está indisponível

***Cenário 9: usuário sem permissão (E4)***

> **Dado que** um Docente não é Coordenador de Curso
>
> **Quando** abre o menu lateral
>
> **Então** o item Aproveitamento de artigos não aparece

**Tela no protótipo**

**Tela:** Painel de análise do aproveitamento de artigos



**Diagrama de sequência**

**Diagrama relacionado:** sem diagrama próprio: cadastro e decisão
simples; a nota mínima entra no diagrama "Lançamento de notas e
liberação do resultado".

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[x\] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-41 Ver os alunos da turma e o painel de cada aluno

| **Épico:**                | Cadastro e Manutenção             |
|---------------------------|-----------------------------------|
| **Feature:**              | Orientação, Atas e Publicações    |
| **Requisitos da matriz:** | RBN-CAD-10.5, RBN-CAD-08.9        |
| **Prioridade (MoSCoW):**  | Must Have (CAD-08.9: Should Have) |
| **Responsável:**          | Leandra Matos                     |

**Descrição**

Como Professor da Disciplina, quero ver os alunos da minha turma, com ou
sem orientador, e abrir o painel de cada um, para que eu acompanhe a
turma em um único lugar e acesse as ações sobre cada aluno.

**Atores**

> **Ator principal:** Professor da Disciplina responsável pela turma.
>
> **Atores secundários:** Não há atores secundários.

**Pré-condições**

- O Professor da Disciplina está autenticado, com o Status da Conta
  > Ativa (US-11). Sem sessão ativa, aplica-se o E1.

- O Professor é o Professor da Disciplina da turma. Para outro docente,
  > aplica-se o E2.

- A turma tem alunos vinculados (US-08).

**Fluxo principal**

> 1\. No menu lateral do sistema, o Professor da Disciplina acessa o
> item Turmas e seleciona a turma.
>
> 2\. O sistema abre a tela da turma na aba Alunos e exibe um bloco por
> aluno, com Nome, Matrícula, Curso, Título (ou "Sem Proposta"), Área de
> Interesse, Orientador (ou "Sem orientador") e Status do TCC.
>
> 3\. O Professor seleciona o bloco de um aluno.
>
> 4\. O sistema abre o painel do aluno, somente leitura, com as seções
> Proposta e TCC, Orientação e coorientação, Entregas, Atas, Publicação,
> Defesa e Versão Final, e os botões de ação do Professor: Excluir aluno
> e Encerrar participação (US-09), Transferir aluno (US-08), Resetar
> primeiro acesso (US-12) e Homologar ou Devolver para Ajuste a Versão
> Final (US-44).
>
> 5\. O Professor consulta as seções e aciona o botão Fechar.
>
> 6\. O sistema retorna à aba Alunos da turma. O fluxo termina.

**Fluxos alternativos**

> A. Aluno sem orientador (passo 2): o bloco exibe "Sem orientador". O
> fluxo prossegue a partir do passo 3.
>
> B. Aluno sem Proposta (passo 2): o bloco exibe "Sem Proposta" no lugar
> do Título. O fluxo prossegue a partir do passo 3.
>
> C. Uso de uma ação do painel (passo 5): o Professor aciona um dos
> botões de ação, e o fluxo prossegue na US correspondente (US-08,
> US-09, US-12 ou US-44).
>
> D. Turma arquivada (passo 1): no menu lateral, o Professor acessa o
> item Turmas arquivadas e seleciona a turma. A lista e os painéis
> aparecem apenas para consulta, sem os botões de ação. O fluxo
> prossegue a partir do passo 3.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o Professor da Disciplina
> tente acessar a tela da turma sem sessão ativa (pelo menu, pelo
> endereço da página ou por um link recebido), o sistema apresenta a
> tela de login (US-11). Após a autenticação, o sistema exibe a aba
> Alunos da turma, e o fluxo prossegue a partir do passo 2. Em caso de
> falha na autenticação, aplicam-se as exceções da US-11.
>
> E2. Usuário que não é o Professor da Disciplina da turma (passo 2): o
> sistema não exibe a lista nem os painéis dos alunos. O fluxo termina.

**Pós-condições**

- Nenhum dado foi alterado pela consulta.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                    | **Resumo da regra em uma frase**                                                                                                                                   |
|--------------|------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-10.5** | O sistema deve permitir que o Professor da Disciplina visualize os alunos da turma, com ou sem orientador. | Lista somente leitura com Nome, Matrícula, Área de Interesse e Orientador de cada aluno, mostrando "Sem orientador" quando for o caso.                             |
| **CAD-08.9** | O sistema deve permitir que o Professor da Disciplina abra o painel individual de cada aluno da turma.     | Um bloco por aluno abre o painel com Proposta e TCC, orientação, entregas, atas, publicação, defesa e versão final; acesso só do Professor da Disciplina da turma. |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Lista com Nome, Matrícula, Área de Interesse e Orientador,
> exibindo "Sem orientador" quando for o caso.
>
> 2\. O painel do aluno reúne todos os dados do TCC e só o Professor da
> Disciplina da turma tem acesso.

***Cenário 1: lista da turma e painel do aluno (fluxo principal)***

> **Dado que** o Professor da Disciplina está autenticado e a turma tem
> 3 alunos
>
> **Quando** seleciona a turma no menu lateral e, em seguida, o bloco de
> um aluno
>
> **Então** o sistema exibe os 3 blocos na aba Alunos e abre o painel
> com Proposta e TCC, orientação, entregas, atas, publicação, defesa e
> Versão Final
>
> **E**, ao acionar o botão Fechar, o Professor retorna à aba Alunos

***Cenário 2: aluno sem orientador (fluxo alternativo A)***

> **Dado que** um aluno da turma ainda não tem orientador
>
> **Quando** o Professor da Disciplina abre a turma
>
> **Então** o bloco do aluno exibe "Sem orientador"

***Cenário 3: aluno sem Proposta (fluxo alternativo B)***

> **Dado que** um aluno da turma ainda não salvou a Proposta
>
> **Quando** o Professor da Disciplina abre a turma
>
> **Então** o bloco do aluno exibe "Sem Proposta" no lugar do Título

***Cenário 4: ação a partir do painel (fluxo alternativo C)***

> **Dado que** o Professor da Disciplina está no painel de um aluno
>
> **Quando** aciona o botão Encerrar participação
>
> **Então** o sistema abre o encerramento da participação (US-09)

***Cenário 5: turma arquivada (fluxo alternativo D)***

> **Dado que** a turma foi arquivada
>
> **Quando** o Professor da Disciplina abre a turma em Turmas arquivadas
> e seleciona o bloco de um aluno
>
> **Então** o painel aparece apenas para consulta, sem os botões de ação

***Cenário 6: acesso sem estar autenticado (E1)***

> **Dado que** o Professor da Disciplina não está autenticado
>
> **Quando** tenta abrir a tela da turma
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre a aba Alunos da turma

***Cenário 7: acesso restrito (E2)***

> **Dado que** um Docente não é o Professor da Disciplina da turma
>
> **Quando** tenta abrir a turma
>
> **Então** o sistema não exibe a lista nem os painéis

**Tela no protótipo**

**Tela:** Turma: alunos e painel individual



**Diagrama de sequência**

**Diagrama relacionado:** sem diagrama próprio, por ser uma consulta; as
ações do painel estão nas US-08, US-09, US-12 e US-44.

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[x\] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-42 Indicar que o TCC está apto para defesa

| **Épico:**                | Cadastro e Manutenção          |
|---------------------------|--------------------------------|
| **Feature:**              | Orientação, Atas e Publicações |
| **Requisitos da matriz:** | RBN-CAD-11.5                   |
| **Prioridade (MoSCoW):**  | Must Have                      |
| **Responsável:**          | Leandra Matos                  |

**Descrição**

Como Orientador, quero indicar que o TCC do meu orientando está apto
para defesa, para que a defesa possa ser agendada.

**Atores**

> **Ator principal:** Orientador do aluno.
>
> **Atores secundários:** Não há atores secundários.

**Pré-condições**

- O Orientador está autenticado, com o Status da Conta Ativa (US-11).
  > Sem sessão ativa, aplica-se o E1.

- O aluno é orientando do docente, com o Papel Orientador.

- O TCC está com o Status Em Andamento; com outro Status, aplica-se o
  > E4.

- A turma tem a entrega do tipo Documento para Defesa, e o aluno a
  > enviou (status Entregue ou Entregue com Atraso). Sem a entrega
  > cadastrada, aplica-se o E5; sem o envio, o E2.

- A Área de Interesse e pelo menos uma Palavra-Chave estão preenchidas
  > (US-13); caso contrário, aplica-se o E3.

**Fluxo principal**

> 1\. No menu lateral do sistema, o Orientador seleciona o item
> Orientações.
>
> 2\. O sistema abre a tela Orientações e exibe o Painel de orientandos.
> Na linha de cada aluno, na coluna de ações, o sistema confere as
> condições e exibe o botão Apto para Defesa habilitado apenas quando
> todas são cumpridas.
>
> 3\. O Orientador aciona o botão Apto para Defesa na linha do aluno.
>
> 4\. O sistema abre a mensagem de confirmação "Confirmar que o TCC de
> \[nome do aluno\] está apto para defesa?", com os botões Cancelar e
> Confirmar. Não há campos para preencher.
>
> 5\. O Orientador aciona o botão Confirmar.
>
> 6\. O sistema muda o Status do TCC para Apto para Defesa e grava a
> mudança no histórico com o Orientador, a data e a hora e o gatilho
> Indicação de Apto para Defesa (US-14).
>
> 7\. O sistema mantém o Orientador no Painel de orientandos, exibe "TCC
> indicado como apto para defesa", exibe a etiqueta Apto para Defesa na
> linha do aluno e remove o botão Apto para Defesa.
>
> 8\. O sistema passa a listar o TCC para o agendamento da defesa
> (US-21) e mantém a mudança de tema bloqueada para o Aluno (US-13). O
> fluxo termina.

**Fluxos alternativos**

> A. Cancelamento na confirmação (passo 5): o Orientador aciona o botão
> Cancelar. A mensagem fecha, nenhuma alteração ocorre e o Status
> permanece Em Andamento. O fluxo termina.
>
> B. Coorientador (passo 2): na linha com o Papel Coorientador, o botão
> Apto para Defesa não aparece; a indicação é apenas do Orientador. O
> fluxo termina.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o Orientador tente acessar
> a tela Orientações sem sessão ativa (pelo menu, pelo endereço da
> página ou por um link recebido), o sistema apresenta a tela de login
> (US-11). Após a autenticação, o sistema exibe a tela Orientações, no
> Painel de orientandos, e o fluxo prossegue a partir do passo 2. Em
> caso de falha na autenticação, aplicam-se as exceções da US-11.
>
> E2. Entrega do tipo Documento para Defesa pendente (passo 2): com o
> status Aguardando Envio ou Não Entregue, o botão Apto para Defesa
> aparece indisponível. O fluxo termina.
>
> E3. Dados do TCC incompletos (passo 2): sem Área de Interesse ou sem
> nenhuma Palavra-Chave, o botão Apto para Defesa aparece indisponível.
> O fluxo termina.
>
> E4. Status diferente de Em Andamento (passo 2): o botão Apto para
> Defesa não aparece na linha do aluno. O fluxo termina.
>
> E5. Turma sem entrega do tipo Documento para Defesa cadastrada (passo
> 2): o botão aparece indisponível e o sistema informa ao Orientador "A
> entrega do tipo Documento para Defesa precisa ser cadastrada pelo
> Professor da Disciplina". O fluxo termina.

**Pós-condições**

- O Status do TCC foi alterado para Apto para Defesa, e a mudança foi
  > registrada no histórico com o Orientador como responsável.

- O TCC passou a estar disponível para o agendamento da defesa (US-21),
  > e a mudança de tema foi bloqueada para o Aluno.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                           | **Resumo da regra em uma frase**                                                                                                                                                                   |
|--------------|-----------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-11.5** | O sistema deve permitir que o Orientador indique que o TCC está apto para defesa. | Apto para Defesa exige Status Em Andamento, entrega do tipo Documento para Defesa enviada e Área de Interesse e Palavra-Chave preenchidas; sem a entrega cadastrada, o sistema avisa o Orientador. |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. O botão só fica disponível quando todas as condições são
> cumpridas.
>
> 2\. Ao confirmar, o Status muda para Apto para Defesa, o que libera o
> agendamento da defesa (US-21).

***Cenário 1: TCC indicado como apto (fluxo principal)***

> **Dado que** o TCC está Em Andamento, a entrega do tipo Documento para
> Defesa está Entregue e a Área e duas Palavras-Chave estão preenchidas
>
> **Quando** o Orientador abre Orientações, aciona o botão Apto para
> Defesa na linha do aluno e aciona o botão Confirmar
>
> **Então** o Status passa a Apto para Defesa, o sistema exibe "TCC
> indicado como apto para defesa" e o histórico registra o Orientador, a
> data e a hora e o gatilho Indicação de Apto para Defesa

***Cenário 2: confirmação cancelada (fluxo alternativo A)***

> **Dado que** o botão Apto para Defesa está disponível
>
> **Quando** o Orientador aciona o botão e, em seguida, o botão Cancelar
>
> **Então** a mensagem fecha e o Status permanece Em Andamento

***Cenário 3: coorientador sem o botão (fluxo alternativo B)***

> **Dado que** o docente é Coorientador do trabalho
>
> **Quando** abre o Painel de orientandos
>
> **Então** a linha do trabalho não exibe o botão Apto para Defesa

***Cenário 4: acesso sem estar autenticado (E1)***

> **Dado que** o Orientador não está autenticado
>
> **Quando** tenta abrir a tela Orientações
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre o Painel de orientandos

***Cenário 5: entrega pendente (E2)***

> **Dado que** a entrega do tipo Documento para Defesa do aluno está Não
> Entregue
>
> **Quando** o Orientador abre o Painel de orientandos
>
> **Então** o botão Apto para Defesa está indisponível

***Cenário 6: dados do TCC incompletos (E3)***

> **Dado que** o TCC está sem Palavras-Chave
>
> **Quando** o Orientador abre o Painel de orientandos
>
> **Então** o botão Apto para Defesa está indisponível

***Cenário 7: Status diferente de Em Andamento (E4)***

> **Dado que** o TCC já está Apto para Defesa
>
> **Quando** o Orientador abre o Painel de orientandos
>
> **Então** o botão Apto para Defesa não aparece na linha do aluno

***Cenário 8: turma sem a entrega cadastrada (E5)***

> **Dado que** a turma não tem entrega do tipo Documento para Defesa
> cadastrada
>
> **Quando** o Orientador abre o Painel de orientandos
>
> **Então** o botão Apto para Defesa está indisponível e o sistema
> informa que a entrega precisa ser cadastrada pelo Professor da
> Disciplina

**Tela no protótipo**

**Tela:** Painel de orientandos: TCC do aluno



**Diagrama de sequência**

**Diagrama relacionado:** sem diagrama próprio, por ser um botão com
validação de condições; a mudança de status segue a US-14.

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[x\] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

# Julia Cohen: Turmas e acesso

## US-07 Gerenciar turmas de TCC

| **Épico:**                | Cadastro e Manutenção                                                |
|---------------------------|----------------------------------------------------------------------|
| **Feature:**              | Turmas e Alunos                                                      |
| **Requisitos da matriz:** | RBN-CAD-04.1, RBN-CAD-04.2, RBN-CAD-04.3, RBN-CAD-04.4, RBN-CAD-04.5 |
| **Prioridade (MoSCoW):**  | Must Have (CAD-04.4 e CAD-04.5: Should Have)                         |
| **Responsável:**          | Julia Cohen                                                          |

**Descrição**

Como Docente do NUCOMP, quero cadastrar, alterar, excluir e arquivar as
turmas de TCC 1 e TCC 2 para que os alunos tenham uma turma onde ser
matriculados e acompanhados.

**Atores**

> **Ator principal:** Docente do NUCOMP, que passa a ser o Professor da
> Disciplina da turma que cria.
>
> **Atores secundários:** Alunos da turma, afetados pela orientação
> automática em TCC 2 (CAD-04.2) e pelo arquivamento (CAD-04.5).

**Pré-condições**

- O Docente está autenticado e com o Status da Conta Ativa (US-11).

- Para editar, excluir ou arquivar, o Docente é o Professor da
  > Disciplina da turma.

**Fluxo principal**

1.  O Professor acessa o menu Turmas e clica em "Nova turma".

2.  O sistema exibe o formulário de cadastro da turma.

3.  O Professor informa Código da Disciplina, Descrição (TCC 1 ou TCC
    > 2), Identificador, Ano, Semestre, Dia da Semana, Horários de
    > Início e de Término, <span class="mark">Local (texto livre, até
    > 100 caracteres, com a sala ou o laboratório da aula) e
    > Curso</span>.

4.  O Professor clica em "Salvar".

5.  O sistema valida os campos obrigatórios, o formato de cada campo, os
    > horários e a unicidade do Identificador no sistema.

6.  O sistema registra a turma, vincula o Docente como Professor da
    > Disciplina e exibe "Turma cadastrada com sucesso". Nas turmas de
    > TCC 2 de Engenharia de Computação e de Licenciatura em Computação,
    > ele também passa a ser o Orientador de todos os alunos
    > matriculados na turma (US-08 e US-17).

7.  Para manter a turma, o Professor da Disciplina abre a turma e usa o
    > botão “Editar”, no cabeçalho, ou o botão de informações, que abre
    > “Dados da turma” com as opções “Editar”, “Excluir” e “Arquivar”
    > (fluxos alternativos A a C).

**Fluxos alternativos**

1.  Edição da turma (CAD-04.3): o Professor da Disciplina clica em
    > "Editar", altera os campos e salva; o sistema repete as validações
    > do passo 5. Se a turma já tiver alunos vinculados, os campos
    > Descrição e Curso ficam bloqueados.

2.  Exclusão de turma vazia (CAD-04.4): se a turma não tiver alunos
    > vinculados, o Professor da Disciplina clica em "Excluir" e
    > confirma na mensagem; a turma é removida definitivamente do
    > sistema.

3.  Arquivamento (CAD-04.5): o Professor da Disciplina clica em
    > "Arquivar". O sistema verifica se nenhum TCC da turma está Em
    > Andamento ou Apto para Defesa, se não há sessão de defesa
    > Agendada, Reagendada ou Em Andamento e, em TCC 2, se a Data Limite
    > da entrega do tipo Versão Final (US-15) já passou. Com as três
    > condições atendidas, pede confirmação, encerra as movimentações da
    > turma e a move para a área de turmas arquivadas, disponível só
    > para consulta, com alunos, TCCs, entregas, atas, defesas e
    > vínculos preservados.

**Fluxos de exceção**

> E1. Campo inválido (CAD-04.1): campo obrigatório vazio; Código da
> Disciplina fora do padrão (só letras maiúsculas e números, sem
> espaços, até 20 caracteres, ex.: ESTCMP025); Identificador fora do
> padrão (letras maiúsculas, números e "\_", até 30 caracteres, ex.:
> ECP06_T01) ou já usado em outra turma do sistema; Ano sem 4 dígitos;
> Local com mais de 100 caracteres; ou horário de término anterior ou
> igual ao de início. O sistema destaca o campo com a mensagem
> correspondente e não salva. Retorna ao passo 3.
>
> E2. Exclusão de turma com alunos: o sistema bloqueia a exclusão e
> exibe "A turma possui alunos matriculados. Use a opção Arquivar".
>
> E3. Arquivamento bloqueado: se alguma condição do fluxo C não for
> atendida, o sistema não arquiva e informa o motivo: "Há TCC Em
> Andamento ou Apto para Defesa", "Há sessão de defesa ativa" ou "A Data
> Limite da Versão Final ainda não venceu ou não foi cadastrada".
>
> E4. Turma arquivada (CAD-04.5): a turma sai da listagem principal e
> fica só para consulta. Alunos, importação, entregas, envios, atas,
> agendamento de defesa e Versão Final ficam bloqueados para alteração,
> e os lembretes de prazo (US-15) deixam de ser enviados.
>
> E5. Usuário sem permissão: quem não é o Professor da Disciplina da
> turma não vê as opções Editar, Excluir e Arquivar.

**Pós-condições**

- A turma fica registrada, com o Docente como Professor da Disciplina,
  > pronta para receber alunos (US-08) e entregas (US-15).

- Nas turmas de TCC 2 de Engenharia de Computação e de Licenciatura em
  > Computação, o Professor da Disciplina é o Orientador dos alunos
  > matriculados.

- Uma turma arquivada fica na área de turmas arquivadas, só para
  > consulta, sem novas movimentações e sem lembretes de prazo.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                                                                                                                        | **Resumo da regra em uma frase**                                                                                                                                                                                                                      |
|--------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-04.1** | O sistema deve mostrar um formulário de cadastro da turma que deve conter os campos Código da Disciplina, Descrição da Turma (TCC 1 ou TCC 2), Identificador da Turma, Ano, Semestre, Dia da Semana, Horário de Início e Horário de Término, Local e Curso.    | Formulário da turma com Código da Disciplina, Descrição (TCC 1 ou TCC 2), Identificador único, Ano, Semestre, Dia da Semana, Horário de Início e de Término, Local em texto livre e Curso; a Data Limite da Versão Final não faz mais parte da turma. |
| **CAD-04.2** | O sistema deve vincular automaticamente o Docente que criou a turma como seu Professor da Disciplina responsável e, nas turmas de TCC 2 de Engenharia de Computação e de Licenciatura em Computação, como Orientador de todos os alunos matriculados na turma. | O Docente que cria a turma vira o Professor da Disciplina e, nas turmas de TCC 2 de Engenharia de Computação e de Licenciatura em Computação, também o Orientador de todos os alunos matriculados.                                                    |
| **CAD-04.3** | O sistema deve permitir a alteração de Código da Disciplina, Descrição da Turma, Identificador da Turma, Ano, Semestre, Dia da Semana, Horário de Início e Horário de Término, Local e Curso da turma.                                                         | O Professor da Disciplina altera os campos da turma, com Descrição e Curso bloqueados quando há alunos vinculados.                                                                                                                                    |
| **CAD-04.4** | O sistema deve permitir a exclusão da turma.                                                                                                                                                                                                                   | A turma só pode ser excluída se não tiver alunos matriculados.                                                                                                                                                                                        |
| **CAD-04.5** | O sistema deve permitir o arquivamento da turma, que encerra as movimentações da turma e a mantém disponível apenas para consulta.                                                                                                                             | Arquivar encerra as movimentações e deixa a turma só para consulta; exige nenhum TCC Em Andamento ou Apto para Defesa, nenhuma sessão ativa e, em TCC 2, a Data Limite da entrega do tipo Versão Final vencida.                                       |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. O Local é informado em texto livre; a Data Limite da Versão Final
> passa a ser cadastrada na entrega do tipo Versão Final (US-15).
>
> 2\. Permite exclusão (se vazia) ou arquivamento.
>
> 3\. Prof. criador ganha papel de Professor da Disciplina.

***Cenário 1:*** Cadastro de turma de TCC 1 com sucesso

> **Dado que** o Professor está autenticado
>
> **Quando** preenche os campos obrigatórios com a Descrição TCC 1 e
> clica em "Salvar"
>
> **Então** o sistema registra a turma e exibe "Turma cadastrada com
> sucesso"
>
> **E** o Professor fica vinculado como Professor da Disciplina da turma

***Cenário 2: Arquivamento bloqueado com TCC em andamento***

> **Dado que** a turma tem um TCC com Status Em Andamento
>
> **Quando** o Professor clica em "Arquivar"
>
> **Então** o sistema não arquiva a turma e informa que há TCC em
> andamento ou Apto para Defesa

***Cenário 3:*** Horário de término inválido

> **Dado que** o Professor informou Horário de Início 10:00 e Horário de
> Término 08:00
>
> **Quando** clica em "Salvar"
>
> **Então** o sistema exibe "O horário de término deve ser posterior ao
> de início" e não salva

***Cenário 4:*** Exclusão bloqueada de turma com alunos

> **Dado que** a turma possui alunos matriculados
>
> **Quando** o Professor clica em "Excluir"
>
> **Então** o sistema bloqueia a exclusão e exibe "A turma possui alunos
> matriculados. Use a opção Arquivar"

***Cenário 5:*** Exclusão de turma vazia

> **Dado que** a turma não possui alunos matriculados
>
> **Quando** o Professor clica em "Excluir" e confirma
>
> **Então** o sistema remove a turma da lista de turmas

***Cenário 6:*** Turma arquivada em modo leitura

> **Dado que** a turma foi arquivada
>
> **Quando** o Professor abre a turma
>
> **Então** o sistema exibe os dados apenas para consulta
>
> **E** as opções Editar, Matricular alunos e Excluir aluno ficam
> indisponíveis

***Cenário 7:*** Orientador automático em TCC 2

> **Dado que** o Docente criou uma turma de TCC 2 de Licenciatura em
> Computação
>
> **Quando** os alunos são matriculados nessa turma (US-08)
>
> **Então** o Docente passa a ser o Orientador de todos esses alunos

***Cenário 8:*** Edição de turma com alunos vinculados

> **Dado que** a turma já tem alunos matriculados
>
> **Quando** o Professor da Disciplina clica em "Editar"
>
> **Então** os campos Descrição e Curso aparecem bloqueados
>
> **E** os demais campos podem ser alterados

***Cenário 9:*** Arquivamento com sucesso

> **Dado que** a turma de TCC 2 não tem TCC Em Andamento ou Apto para
> Defesa, não tem sessão de defesa ativa e a Data Limite da Versão Final
> já passou
>
> **Quando** o Professor da Disciplina clica em "Arquivar" e confirma
>
> **Então** a turma vai para a área de turmas arquivadas e fica
> disponível só para consulta

***Cenário 10:*** Arquivamento bloqueado pela Data Limite

> **Dado que** a Data Limite da Versão Final da turma de TCC 2 é
> 30/11/2026 e hoje é 20/11/2026
>
> **Quando** o Professor da Disciplina clica em "Arquivar"
>
> **Então** o sistema não arquiva e informa "A Data Limite da Versão
> Final ainda não venceu ou não foi cadastrada"

***Cenário 11:*** Arquivamento bloqueado por sessão ativa

> **Dado que** a turma tem uma sessão de defesa Agendada
>
> **Quando** o Professor da Disciplina clica em "Arquivar"
>
> **Então** o sistema não arquiva e informa "Há sessão de defesa ativa"

***Cenário 12:*** Local acima do limite

> **Dado que** o Professor está no formulário da turma
>
> **Quando** informa um Local com 101 caracteres e clica em "Salvar"
>
> **Então** o sistema destaca o campo Local e não salva a turma

***Cenário 13:*** Identificador repetido

> **Dado que** já existe no sistema uma turma com o Identificador
> ECP06_T01
>
> **Quando** o Professor cadastra outra turma com o mesmo Identificador
> e clica em "Salvar"

**Então** o sistema destaca o campo Identificador e não salva a turma

**Tela no protótipo**

**Tela:** Gerenciar turmas de TCC



**Diagrama de sequência**

**Diagrama relacionado:** Sem diagrama próprio: cadastro, edição e
arquivamento simples, com validações locais já descritas no fluxo.

**Link:** –

**Pronta para desenvolver**

> \[ \] Descrição no formato Como, Quero, Para que
>
> \[ \] Requisitos da matriz conferidos
>
> \[ \] Fluxo principal e fluxos alternativos escritos
>
> \[ \] Atores, pré-condições e pós-condições preenchidos
>
> \[ \] Fluxos de exceção escritos
>
> \[ \] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-08 Matricular alunos na turma

| **Épico:**                | Cadastro e Manutenção                                                              |
|---------------------------|------------------------------------------------------------------------------------|
| **Feature:**              | Turmas e Alunos                                                                    |
| **Requisitos da matriz:** | RBN-CAD-05.1, RBN-CAD-05.2, RBN-CAD-05.3, RBN-CAD-05.5, RBN-CAD-05.6, RBN-CAD-05.7 |
| **Prioridade (MoSCoW):**  | Must Have (CAD-05.2: Should Have)                                                  |
| **Responsável:**          | Julia Cohen                                                                        |

**Descrição**

Como Professor da Disciplina, quero matricular alunos na turma, um a um
ou por arquivo CSV/XLSX, para que eles entrem na turma e possam fazer o
primeiro acesso.

**Atores**

> **Ator principal:** Professor da Disciplina; na transferência, também
> a Secretaria do curso.
>
> **Atores secundários:** Aluno, que recebe uma conta com o Status da
> Conta Aguardando Ativação, e os orientadores antigo e novo,
> notificados na transferência (CAD-05.6).

**Pré-condições**

- O Professor da Disciplina está autenticado e com o Status da Conta
  > Ativa (US-11).

- A turma existe e não está arquivada (US-07).

- Na importação, o arquivo é CSV ou XLSX, tem até 2 MB e traz na
  > primeira linha os cabeçalhos Matrícula, Nome Completo e Curso.

**Fluxo principal**

1.  O Professor da Disciplina abre a turma e clica em "Matricular
    > alunos".

2.  O sistema oferece duas opções: "Matrícula individual" e "Importar
    > arquivo (CSV/XLSX)".

3.  Na matrícula individual, o Professor informa Matrícula, Nome
    > Completo e Curso (escolhendo um curso do NUCOMP ou digitando o
    > código de curso da UEA, com sugestões ao digitar) e clica em
    > "Salvar".

4.  O sistema valida os campos, reconhece o curso pela tabela de
    > equivalência (CAD-05.7) e verifica se a matrícula já existe.

5.  O sistema cria a conta do aluno com o Status da Conta "Aguardando
    > Ativação", vincula-o à turma com o Status do TCC Sem Proposta e
    > exibe "Aluno matriculado com sucesso".

6.  Na importação, o Professor seleciona o arquivo CSV ou XLSX, de até 2
    > MB, com os cabeçalhos Matrícula, Nome Completo e Curso.

7.  O sistema lê o arquivo, valida cada linha, reconhece o curso de cada
    > código da UEA e exibe uma prévia com os alunos novos, os já
    > cadastrados, as linhas com erro e os códigos não reconhecidos.

8.  O Professor confere a prévia e clica em "Confirmar importação".

9.  O sistema cria as contas novas, vincula todos os alunos válidos à
    > turma e exibe um resumo com o total de matriculados, as linhas
    > rejeitadas com o motivo e a quantidade de códigos de curso não
    > reconhecidos.

**Fluxos alternativos**

1.  Matrícula já cadastrada (CAD-05.5): nos passos 4 ou 7, o sistema não
    > cria nova conta; vincula o aluno à turma mantendo a mesma conta,
    > e-mail, senha e histórico. Se o Status do TCC for Aprovado para
    > TCC 2, o TCC é transferido para a turma de TCC 2 (US-14); se for
    > Reprovado, Desistente ou Jubilado, o aluno registra uma nova
    > Proposta na turma (US-13).

2.  Aluno já matriculado nesta turma: o sistema ignora o registro e
    > informa "Aluno já matriculado nesta turma".

3.  Código de curso não reconhecido ou diferente do curso da turma
    > (CAD-05.7): o aluno é cadastrado normalmente; o curso aparece como
    > "Código não reconhecido" ou o sistema exibe um alerta de
    > divergência com o curso da turma.

4.  Edição dos dados (CAD-05.3): na lista da turma, o Professor clica em
    > "Editar", altera Nome Completo ou Curso e salva; o sistema repete
    > as validações. A Matrícula aparece só para leitura.

5.  Transferência (CAD-05.6): na troca de orientador em turma com
    > orientador automático (US-07), o Professor da Disciplina da turma
    > de origem ou a Secretaria do curso clica em "Transferir" no aluno,
    > escolhe a Turma de Destino (TCC 2, do mesmo curso e período
    > letivo, não arquivada) e escreve a Justificativa (até 500
    > caracteres). O TCC, o Status do TCC e o histórico vão para a nova
    > turma, o professor dela passa a ser o orientador e, se ele era
    > coorientador do trabalho, a coorientação é encerrada. O aluno e os
    > orientadores antigo e novo são notificados, e a transferência fica
    > registrada com autor, data, hora e justificativa.

**Fluxos de exceção**

> E1. Matrícula inválida: com menos ou mais de 10 dígitos, ou com
> letras, o sistema exibe "A matrícula deve ter 10 dígitos numéricos" e
> não salva. Na importação, a linha vai para a lista de erros.
>
> E2. Campo obrigatório vazio ou Nome Completo fora da regra (só letras,
> acentos e espaços, até 150 caracteres): o sistema rejeita o registro e
> informa o motivo; na importação, a rejeição é por linha.
>
> E3. Arquivo fora do modelo: extensão diferente de CSV ou XLSX, arquivo
> com mais de 2 MB ou cabeçalhos faltando. O sistema não processa o
> arquivo e exibe "Arquivo fora do modelo. Baixe o modelo de
> importação".
>
> E4. Transferência não permitida (CAD-05.6): o TCC não está Em
> Andamento nem Apto para Defesa, há sessão Agendada, Reagendada ou Em
> Andamento, não existe turma de TCC 2 do novo orientador no período ou
> a Justificativa está vazia. O sistema não transfere e informa o
> motivo.
>
> E5. Turma arquivada: o sistema bloqueia a matrícula e a importação
> (CAD-04.5, US-07).

**Pós-condições**

- Cada aluno vinculado começa com o Status do TCC Sem Proposta, menos o
  > aprovado em TCC 1, cujo TCC volta para Em Andamento na turma de TCC
  > 2 (US-14). Os alunos novos ficam com o Status da Conta Aguardando
  > Ativação, prontos para o primeiro acesso (US-10).

- Alunos que já tinham conta mantêm conta, e-mail, senha e histórico das
  > turmas anteriores.

- O resumo da importação mostra as linhas rejeitadas, com o motivo, e
  > quantos códigos de curso não foram reconhecidos.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                               | **Resumo da regra em uma frase**                                                                                                                                                                    |
|--------------|-----------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-05.1** | O sistema deve mostrar um formulário de cadastro do aluno que deve conter os campos Matrícula, Nome Completo e Curso. | A Matrícula do aluno é obrigatória, tem exatamente 10 dígitos numéricos e é única no sistema. O Nome Completo do aluno é obrigatório. O Curso do aluno é obrigatório e deve ser um curso do NUCOMP. |
| **CAD-05.2** | O sistema deve permitir a importação de alunos por arquivo nos formatos CSV ou XLSX.                                  | O Professor pode matricular vários alunos de uma vez enviando um arquivo CSV ou XLSX com Matrícula, Nome Completo e Código do Curso.                                                                |
| **CAD-05.3** | O sistema deve permitir a alteração de Nome Completo e Curso do aluno.                                                | O Professor da Disciplina pode corrigir o Nome e o Curso do aluno; a Matrícula, que identifica o aluno, não é alterada.                                                                             |
| **CAD-05.5** | \[Exceção\] O sistema deve permitir o vínculo de aluno já cadastrado a uma nova turma.                                | Se a matrícula já existe, o sistema não cria nova conta: só vincula o aluno à nova turma e mantém o histórico.                                                                                      |
| **CAD-05.6** | \[Exceção\] O sistema deve permitir transferir o aluno para a turma de TCC 2 de outro orientador.                     | O Professor pode transferir o aluno para a turma de TCC 2 de outro orientador, e o histórico do TCC é mantido.                                                                                      |
| **CAD-05.7** | O sistema deve reconhecer o curso do NUCOMP a partir do código de curso do sistema acadêmico da UEA.                  | Na importação, o código de curso do sistema acadêmico da UEA é convertido no curso do NUCOMP correspondente.                                                                                        |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Matrícula restrita a 10 dígitos.
>
> 2\. Matrícula já existente não cria conta nova, apenas vincula à nova
> turma mantendo histórico.

***Cenário 1:*** Matrícula individual de aluno novo

> **Dado que** o Professor está na turma e não existe aluno com a
> matrícula 2026000123
>
> **Quando** informa a Matrícula 2026000123, o Nome Completo e o Curso e
> clica em "Salvar"
>
> **Então** o sistema cria a conta com o Status da Conta "Aguardando
> Ativação"
>
> **E** vincula o aluno à turma

***Cenário 2:*** Matrícula com formato inválido

> **Dado que** o Professor está no formulário de matrícula individual
>
> **Quando** informa a matrícula "20260001", com 8 dígitos, e clica em
> "Salvar"
>
> **Então** o sistema exibe "A matrícula deve ter 10 dígitos numéricos"
> e não salva

***Cenário 3:*** Aluno já cadastrado em outra turma

> **Dado que** o aluno 2026000123 já cursou uma turma de TCC 1
>
> **Quando** o Professor o matricula em uma turma de TCC 2
>
> **Então** o sistema não cria uma nova conta
>
> **E** vincula o aluno à turma de TCC 2, mantendo o histórico da turma
> anterior

***Cenário 4:*** Importação por CSV com linhas válidas e inválidas

> **Dado que** o arquivo CSV tem 30 linhas, 2 delas com matrícula de 9
> dígitos
>
> **Quando** o Professor envia o arquivo e confirma a importação
>
> **Então** o sistema matricula os 28 alunos válidos
>
> **E** exibe um resumo com as 2 linhas rejeitadas e o motivo de cada
> uma

***Cenário 5:*** Arquivo fora do modelo

> **Dado que** o Professor está na opção de importação
>
> **Quando** envia um arquivo PDF
>
> **Então** o sistema não processa o arquivo e exibe "Arquivo fora do
> modelo. Baixe o modelo de importação"

***Cenário 6:*** Transferência para outra turma de TCC 2

> **Dado que** o TCC do aluno está Em Andamento numa turma de TCC 2 de
> Engenharia de Computação e não há sessão de defesa ativa
>
> **Quando** o Professor da Disciplina clica em "Transferir", escolhe a
> turma de TCC 2 de outro orientador do mesmo curso e período e escreve
> a justificativa
>
> **Então** o aluno passa a constar apenas na turma de destino, com o
> professor dela como orientador
>
> **E** o aluno e os dois orientadores são notificados

***Cenário 7:*** Código de curso reconhecido

> **Dado que** o arquivo CSV tem uma linha com o código de curso da UEA
> de Engenharia de Computação
>
> **Quando** o Professor envia o arquivo e confirma a importação
>
> **Então** o sistema matricula o aluno no curso Engenharia de
> Computação do NUCOMP

***Cenário 8:*** Código de curso não reconhecido

> **Dado que** o arquivo CSV tem uma linha com um código de curso que
> não está na tabela de equivalência
>
> **Quando** o Professor envia o arquivo e confirma a importação
>
> **Então** o aluno é matriculado e o curso dele aparece como "Código
> não reconhecido"
>
> **E** o resumo informa quantos códigos não foram reconhecidos

***Cenário 9:*** Aluno já matriculado nesta turma

> **Dado que** o aluno 2026000123 já está na turma
>
> **Quando** o Professor tenta matriculá-lo de novo
>
> **Então** o sistema ignora o registro e informa "Aluno já matriculado
> nesta turma"

***Cenário 10:*** Edição do nome do aluno

> **Dado que** o aluno está matriculado na turma
>
> **Quando** o Professor clica em "Editar", corrige o Nome Completo e
> salva
>
> **Então** o sistema grava o novo nome
>
> **E** a Matrícula continua sem opção de edição

***Cenário 11:*** Matrícula em turma arquivada

> **Dado que** a turma foi arquivada
>
> **Quando** o Professor abre a turma
>
> **Então** a opção "Matricular alunos" fica indisponível

***Cenário 12:*** Transferência bloqueada por sessão ativa

> **Dado que** o TCC do aluno tem uma sessão de defesa Agendada
>
> **Quando** o Professor da Disciplina tenta transferi-lo
>
> **Então** o sistema não transfere e informa o motivo

***Cenário 13:*** Aluno aprovado em TCC 1 matriculado em TCC 2

> **Dado que** o TCC do aluno está com o Status Aprovado para TCC 2
>
> **Quando** o Professor o matricula numa turma de TCC 2
>
> **Então** o TCC é transferido para a nova turma com os dados do TCC 1
> (US-14)
>
> **E** o Status do TCC volta para Em Andamento

***Cenário 14:*** Arquivo acima de 2 MB

> **Dado que** o Professor está na opção de importação
>
> **Quando** envia um arquivo XLSX de 3 MB
>
> **Então** o sistema não processa o arquivo e exibe "Arquivo fora do
> modelo. Baixe o modelo de importação"

**Tela no protótipo**

**Tela:** Matricular alunos na turma



**Diagrama de sequência**

**Diagrama relacionado:** Matrícula por CSV

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[ \] Descrição no formato Como, Quero, Para que
>
> \[ \] Requisitos da matriz conferidos
>
> \[ \] Fluxo principal e fluxos alternativos escritos
>
> \[ \] Atores, pré-condições e pós-condições preenchidos
>
> \[ \] Fluxos de exceção escritos
>
> \[ \] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-09 Excluir aluno da turma

| **Épico:**                | Cadastro e Manutenção                                  |
|---------------------------|--------------------------------------------------------|
| **Feature:**              | Turmas e Alunos                                        |
| **Requisitos da matriz:** | RBN-CAD-05.4, RBN-CAD-05.8, RBN-CAD-08.4, RBN-CAD-08.5 |
| **Prioridade (MoSCoW):**  | Must Have (CAD-05.8: Should Have)                      |
| **Responsável:**          | Julia Cohen                                            |

**Descrição**

Como Professor da Disciplina, quero excluir da turma o aluno vinculado
por engano ou encerrar a participação do aluno como Desistente,
Reprovado ou Jubilado, para que a turma, o histórico e o registro de
evasão fiquem corretos.

**Atores**

> **Ator principal:** Professor da Disciplina.
>
> **Atores secundários:** Aluno, que é notificado e perde o acesso à
> turma (exclusão) ou passa a ter acesso só de consulta (encerramento,
> CAD-08.5).

**Pré-condições**

- O Professor da Disciplina está autenticado e com o Status da Conta
  > Ativa (US-11).

- O aluno está vinculado à turma do Professor, que não está arquivada
  > (US-07).

- A exclusão vale para aluno sem Proposta; o encerramento, para aluno
  > com Proposta.

**Fluxo principal**

1.  O Professor da Disciplina abre o painel do aluno na turma (US-41) e
    > clica em "Encerrar participação".

2.  O sistema confere que o aluno não tem Proposta cadastrada e exibe o
    > formulário de exclusão com o campo Justificativa.

3.  O Professor escreve a justificativa e clica em "Confirmar".

4.  O sistema valida a justificativa e pede a confirmação final.

5.  O Professor confirma a exclusão.

6.  O sistema retira o aluno da turma, registra autor, data, hora e
    > justificativa e envia ao aluno uma notificação dentro do sistema
    > com o motivo.

7.  O sistema exibe "Aluno excluído da turma", e o aluno passa a
    > aparecer na lista de excluídos ou transferidos (CAD-05.8).

**Fluxos alternativos**

1.  Encerramento da participação (CAD-08.4): se o aluno já tem Proposta,
    > o Professor clica em "Encerrar participação". O sistema exibe o
    > formulário com Status (Desistente, Reprovado ou Jubilado) e
    > Justificativa; o Professor preenche e confirma. O Status do TCC
    > muda, a transição fica no histórico do TCC com o Professor da
    > Disciplina como responsável (CAD-08.7, US-14), o registro entra no
    > relatório de evasão (US-32) e o acesso do aluno fica restrito
    > (CAD-08.5).

2.  Cancelamento: se o Professor cancelar na confirmação final, nada é
    > alterado e o aluno continua na turma.

3.  Consulta dos excluídos ou transferidos (CAD-05.8): o Professor abre
    > a lista, só de leitura, com nome, matrícula, data e hora, autor e
    > justificativa de cada exclusão ou transferência.

**Fluxos de exceção**

> E1. Justificativa vazia ou com mais de 500 caracteres: o sistema exibe
> "Informe uma justificativa de até 500 caracteres" e não conclui.
> Retorna ao passo 3.
>
> E2. Status não selecionado no encerramento: o sistema exibe "Selecione
> o Status do aluno" e não conclui.
>
> E3. Exclusão de aluno com Proposta (CAD-05.4): o sistema não exclui e
> exibe "O aluno já tem Proposta. Use Encerrar participação".
>
> E4. Turma arquivada: o sistema bloqueia a exclusão e o encerramento
> (CAD-04.5, US-07).
>
> E5. Acesso restrito (CAD-08.5): o aluno com Status Desistente,
> Reprovado ou Jubilado continua entrando no sistema, mas só consulta o
> próprio histórico. Os botões de editar o TCC, indicar ou trocar de
> orientador e enviar entregas daquela turma ficam desabilitados para os
> três status, sem exceção.

**Pós-condições**

- Na exclusão, o aluno deixa a turma, perde o acesso a ela e aparece na
  > lista de excluídos ou transferidos, com o registro de autor, data,
  > hora e justificativa.

- No encerramento, o Status do TCC passa a Desistente, Reprovado ou
  > Jubilado, a transição fica no histórico e o registro alimenta o
  > relatório de evasão (US-32).

- O aluno com participação encerrada fica só com acesso de consulta ao
  > próprio histórico.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                             | **Resumo da regra em uma frase**                                                                                                                                                                        |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-05.4** | O sistema deve permitir a exclusão do aluno da turma, com o formulário de exclusão que deve conter o campo Justificativa.                                           | A exclusão vale só para aluno sem Proposta (vínculo feito por engano) e exige Justificativa de até 500 caracteres; o aluno perde o acesso à turma e é notificado com o motivo.                          |
| **CAD-05.8** | O sistema deve exibir os alunos excluídos ou transferidos da turma.                                                                                                 | Lista só de leitura, para o Professor da Disciplina, com nome, matrícula, data e hora, autor e justificativa de cada exclusão ou transferência.                                                         |
| **CAD-08.4** | O sistema deve mostrar um formulário de encerramento da participação do aluno que deve conter os campos Status (Desistente, Reprovado ou Jubilado) e Justificativa. | Para aluno com Proposta, o Professor encerra a participação escolhendo Desistente, Reprovado ou Jubilado e escrevendo a Justificativa de até 500 caracteres; o registro alimenta o relatório de evasão. |
| **CAD-08.5** | \[Exceção\] O sistema deve restringir o acesso do aluno cujo TCC esteja com Status Desistente, Reprovado ou Jubilado.                                               | O aluno Desistente, Reprovado ou Jubilado continua entrando, mas só consulta o histórico; editar o TCC, indicar ou trocar orientador e enviar entregas daquela turma ficam desabilitados, sem exceção.  |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Exige preenchimento de justificativa (até 500 caracteres).
>
> 2\. Aluno excluído/reprovado perde acesso de envio e fica apenas em
> modo leitura.

***Cenário 1:*** Exclusão de aluno vinculado por engano

> **Dado que** o aluno está na turma e não tem Proposta cadastrada
>
> **Quando** o Professor clica em "Excluir da turma", escreve a
> justificativa e confirma
>
> **Então** o sistema retira o aluno da turma e o mostra na lista de
> excluídos ou transferidos
>
> **E** o aluno recebe uma notificação com o motivo

***Cenário 2:*** Exclusão bloqueada para aluno com Proposta

> **Dado que** o aluno já salvou a Proposta
>
> **Quando** o Professor tenta excluí-lo da turma
>
> **Então** o sistema não exclui e exibe "O aluno já tem Proposta. Use
> Encerrar participação"

***Cenário 3:*** Encerramento da participação como Desistente

> **Dado que** o aluno tem Proposta e o TCC está Em Andamento
>
> **Quando** o Professor clica em "Encerrar participação", escolhe
> Desistente, escreve a justificativa e confirma
>
> **Então** o Status do TCC passa a Desistente e a transição fica no
> histórico, com o Professor da Disciplina como responsável
>
> **E** o registro entra no relatório de evasão

***Cenário 4:*** Justificativa não preenchida

> **Dado que** o Professor abriu o formulário de exclusão
>
> **Quando** clica em "Confirmar" sem escrever a justificativa
>
> **Então** o sistema exibe "Informe uma justificativa de até 500
> caracteres"
>
> **E** o aluno continua na turma

***Cenário 5:*** Justificativa acima do limite

> **Dado que** o Professor abriu o formulário de encerramento
>
> **Quando** escreve uma justificativa com 501 caracteres e clica em
> "Confirmar"
>
> **Então** o sistema exibe "Informe uma justificativa de até 500
> caracteres" e não conclui

***Cenário 6:*** Status não selecionado

> **Dado que** o Professor abriu o formulário de encerramento
>
> **Quando** escreve a justificativa e confirma sem escolher o Status
>
> **Então** o sistema exibe “Selecione o Status do aluno”
>
> **E** o Status do TCC não muda

***Cenário 7:*** Aluno com participação encerrada em modo leitura

> **Dado que** a participação do aluno foi encerrada com o Status
> Reprovado
>
> **Quando** ele entra no sistema e tenta enviar o link de uma entrega
>
> **Então** o botão de envio está desabilitado
>
> **E** o aluno ainda consegue consultar o próprio histórico

***Cenário 8:*** Restrição sem exceção

> **Dado que** o TCC do aluno está com o Status Jubilado
>
> **Quando** o aluno tenta editar o TCC ou indicar um orientador
>
> **Então** os botões estão desabilitados

***Cenário 9:*** Consulta dos excluídos ou transferidos

> **Dado que** um aluno foi excluído e outro foi transferido da turma
>
> **Quando** o Professor abre a lista de excluídos ou transferidos
>
> **Então** o sistema mostra os dois com nome, matrícula, data e hora,
> autor e justificativa

***Cenário 10:*** Cancelamento

> **Dado que** o Professor preencheu o formulário de exclusão
>
> **Quando** cancela na confirmação final
>
> **Então** o aluno continua na turma e nada é registrado

***Cenário 11:*** Turma arquivada

> **Dado que** a turma foi arquivada
>
> **Quando** o Professor abre o painel de um aluno
>
> **Então** as opções "Excluir da turma" e "Encerrar participação" ficam
> indisponíveis

**Tela no protótipo**

**Tela:** Excluir aluno da turma



**Diagrama de sequência**

**Diagrama relacionado:** Sem diagrama próprio: atualização do Status de
um único aluno, sem troca de mensagens entre vários objetos.

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[ \] Descrição no formato Como, Quero, Para que
>
> \[ \] Requisitos da matriz conferidos
>
> \[ \] Fluxo principal e fluxos alternativos escritos
>
> \[ \] Atores, pré-condições e pós-condições preenchidos
>
> \[ \] Fluxos de exceção escritos
>
> \[ \] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-10 Criar a senha no primeiro acesso

| **Épico:**                | Cadastro e Manutenção                    |
|---------------------------|------------------------------------------|
| **Feature:**              | Acesso e Login                           |
| **Requisitos da matriz:** | RBN-CAD-06.1, RBN-CAD-06.2, RBN-CAD-06.3 |
| **Prioridade (MoSCoW):**  | Must Have                                |
| **Responsável:**          | Julia Cohen                              |

**Descrição**

Como Aluno, Docente, Secretaria ou Membro Externo novo, quero criar a
minha senha a partir de um link para que possa fazer o primeiro acesso.

**Atores**

> **Ator principal:** Aluno, Docente, Secretaria ou Membro Externo com o
> Status da Conta Aguardando Ativação.
>
> **Atores secundários:** Serviço de e-mail (envio do link) e quem criou
> a conta: o Professor da Disciplina para o Aluno (US-08), a Coordenação
> ou a Secretaria para Docente e Secretaria (US-03) e para o Membro
> Externo (US-05).

**Pré-condições**

- A conta foi criada com o Status da Conta Aguardando Ativação (US-03,
  > US-05 ou US-08).

- O usuário tem acesso ao e-mail: o institucional, no caso do Aluno, ou
  > o cadastrado na conta, nos demais perfis.

**Fluxo principal**

1.  O usuário, Aluno, Docente, Secretaria ou Membro Externo, clica em
    > "Primeiro acesso" na tela de login e escolhe o seu perfil.

2.  O sistema exibe o formulário do perfil: Matrícula e E-mail
    > Institucional para Aluno; E-mail para Docente, Secretaria e Membro
    > Externo.

3.  O usuário preenche os dados e clica em "Enviar".

4.  O sistema localiza a conta com o Status da Conta "Aguardando
    > Ativação", registra o e-mail (no caso do Aluno) e gera um link de
    > ativação válido por 24 horas.

5.  O sistema envia o link ao e-mail e exibe "Enviamos um link de
    > ativação para o seu e-mail".

6.  O usuário abre o link dentro do prazo.

7.  O sistema exibe o formulário de ativação com os campos Senha e
    > Confirmação de Senha.

8.  O usuário define a senha e clica em "Ativar conta".

9.  O sistema valida a senha, muda o Status da Conta para Ativa,
    > invalida o link e direciona o usuário para a tela de login com a
    > mensagem "Conta ativada".

**Fluxos alternativos**

1.  Link vencido: se o link for aberto depois de 24 horas, o sistema
    > exibe um aviso e o botão "Reenviar link de ativação" (US-37).

2.  Novo pedido de primeiro acesso: se o usuário pedir o primeiro acesso
    > de novo antes de usar o link, o sistema invalida o link anterior,
    > gera um novo link válido por 24 horas e o envia ao mesmo e-mail.
    > Só o link mais recente ativa a conta.

**Fluxos de exceção**

> E1. Dados não encontrados: matrícula ou e-mail sem conta, ou matrícula
> sem turma. O sistema exibe "Dados não encontrados. Procure o Professor
> da Disciplina ou a Secretaria".
>
> E2. Conta já ativa: se a matrícula ou o e-mail já concluiu o primeiro
> acesso, o sistema exibe "Esta conta já está ativa" e orienta a usar
> "Esqueci minha senha" (US-12) ou, no caso do Aluno com e-mail errado,
> procurar o Professor da Disciplina para o reset do primeiro acesso
> (US-12).
>
> E3. E-mail do Aluno fora do domínio institucional: o sistema exibe
> "Informe o seu e-mail institucional da UEA (@uea.edu.br)". Retorna ao
> passo 3.
>
> E4. Matrícula fora do formato: se a matrícula não tiver exatamente 10
> dígitos numéricos, o sistema destaca o campo, exibe "A matrícula deve
> ter 10 dígitos numéricos" e não envia o link. Retorna ao passo 3.
>
> E5. E-mail já usado em outra conta: o E-mail Institucional do Aluno
> deve ser único no sistema. Se já estiver vinculado a outra conta, o
> sistema não envia o link e exibe "Este e-mail já está vinculado a
> outra conta. Procure o Professor da Disciplina". Retorna ao passo 3.
>
> E6. Senha fora da regra: o sistema exibe "A senha deve ter de 8 a 64
> caracteres, com ao menos 1 letra e 1 número". Retorna ao passo 8.
>
> E7. Confirmação diferente da senha: o sistema exibe "As senhas não
> conferem". Retorna ao passo 8.

**Pós-condições**

- O Status da Conta passa de Aguardando Ativação para Ativa e a senha
  > fica gravada.

- No caso do Aluno, o e-mail institucional fica vinculado à conta.

- O link de ativação deixa de valer, e o usuário já pode fazer login
  > (US-11).

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                         | **Resumo da regra em uma frase**                                                                                                                                        |
|--------------|---------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-06.1** | O sistema deve mostrar um formulário de primeiro acesso do Aluno que deve conter os campos Matrícula e E-mail Institucional.    | O Aluno inicia o primeiro acesso com a Matrícula cadastrada pelo Professor e o seu E-mail Institucional.                                                                |
| **CAD-06.2** | O sistema deve mostrar um formulário de primeiro acesso de Docente, Secretaria e Membro Externo que deve conter o campo E-mail. | Docente, Secretaria e Membro Externo iniciam o primeiro acesso com o E-mail já cadastrado na conta.                                                                     |
| **CAD-06.3** | O sistema deve mostrar um formulário de ativação de conta que deve conter os campos Senha e Confirmação de Senha.               | <span class="mark">Senha de 8 a 64 caracteres, com letra e número, e confirmação idêntica; ao salvar, o Status da Conta passa de Aguardando Ativação para Ativa.</span> |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Link de ativação dura 24 horas.
>
> 2\. Senha de 8 a 64 caracteres, exigindo pelo menos 1 letra e 1
> número.

***Cenário 1:*** Primeiro acesso do aluno com sucesso

> <span class="mark">**Dado que** o aluno foi matriculado e a conta está
> com o Status "Aguardando Ativação"</span>
>
> **Quando** informa a matrícula e o e-mail institucional, abre o link
> recebido e define uma senha válida
>
> <span class="mark">**Então** o sistema muda o Status da Conta para
> Ativa</span>
>
> **E** direciona o aluno para a tela de login com a mensagem "Conta
> ativada"

***Cenário 2:*** Primeiro acesso de docente

> **Dado que** o docente foi cadastrado com o seu e-mail
>
> **Quando** informa esse e-mail em "Primeiro acesso"
>
> **Então** o sistema envia ao e-mail um link de ativação válido por 24
> horas

***Cenário 3:*** Link de ativação vencido

> **Dado que** o link foi gerado há mais de 24 horas e não foi usado
>
> **Quando** o usuário abre o link
>
> **Então** o sistema não exibe o formulário de senha
>
> **E** exibe um aviso e o botão "Reenviar link de ativação"

***Cenário 4:*** Senha fora da regra

> **Dado que** o usuário está no formulário de ativação
>
> **Quando** informa a senha "abcdefgh", sem número, e clica em "Ativar
> conta"
>
> **Então** o sistema exibe "A senha deve ter de 8 a 64 caracteres, com
> ao menos 1 letra e 1 número" e não ativa a conta

***Cenário 5:*** Confirmação de senha diferente

> **Dado que** o usuário está no formulário de ativação
>
> **Quando** informa uma Confirmação de Senha diferente da Senha
>
> **Então** o sistema exibe "As senhas não conferem" e não ativa a conta

***Cenário 6:*** Dados não encontrados

> **Dado que** não existe aluno com a matrícula 2026000999
>
> **Quando** o usuário informa essa matrícula e um e-mail institucional
> em "Primeiro acesso"
>
> **Então** o sistema exibe "Dados não encontrados. Procure o Professor
> da Disciplina ou a Secretaria" e não envia o link

***Cenário 7:*** Conta já ativa

> **Dado que** a conta do aluno está com o Status Ativa
>
> **Quando** ele informa a matrícula e o e-mail em "Primeiro acesso"
>
> **Então** o sistema exibe "Esta conta já está ativa"
>
> **E** orienta a usar "Esqueci minha senha" ou procurar o Professor da
> Disciplina

***Cenário 8:*** E-mail fora do domínio institucional

> **Dado que** o aluno está no formulário de primeiro acesso
>
> **Quando** informa o e-mail "aluno@gmail.com" e clica em "Enviar"
>
> **Então** o sistema exibe "Informe o seu e-mail institucional da UEA
> (@uea.edu.br)" e não envia o link

***Cenário 9:*** E-mail já usado em outra conta

> **Dado que** o e-mail "ana.eng24@uea.edu.br" já está vinculado à conta
> de outro aluno
>
> **Quando** um aluno informa a sua matrícula e esse e-mail em "Primeiro
> acesso"
>
> **Então** o sistema exibe "Este e-mail já está vinculado a outra
> conta. Procure o Professor da Disciplina" e não envia o link

***Cenário 10:*** Matrícula fora do formato

> **Dado que** o aluno está no formulário de primeiro acesso
>
> **Quando** informa a matrícula "20260001", com 8 dígitos, e clica em
> "Enviar"
>
> **Então** o sistema exibe "A matrícula deve ter 10 dígitos numéricos"
> e não envia o link

***Cenário 11:*** Novo pedido invalida o link anterior

> **Dado que** o aluno pediu o primeiro acesso e recebeu um link que
> ainda não usou
>
> **Quando** pede o primeiro acesso de novo e depois abre o link
> anterior
>
> **Então** o sistema exibe "Link inválido. Use o link mais recente
> enviado ao seu e-mail"
>
> **E** apenas o novo link permite ativar a conta

**Tela no protótipo**

**Tela:** Criar a senha no primeiro acesso





**Diagrama de sequência**

**Diagrama relacionado:** Primeiro acesso e login.

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[ \] Descrição no formato Como, Quero, Para que
>
> \[ \] Requisitos da matriz conferidos
>
> \[ \] Fluxo principal e fluxos alternativos escritos
>
> \[ \] Atores, pré-condições e pós-condições preenchidos
>
> \[ \] Fluxos de exceção escritos
>
> \[ \] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-11 Fazer login

| **Épico:**                | Cadastro e Manutenção                    |
|---------------------------|------------------------------------------|
| **Feature:**              | Acesso e Login                           |
| **Requisitos da matriz:** | RBN-CAD-06.4, RBN-CAD-06.6, RBN-CAD-03.3 |
| **Prioridade (MoSCoW):**  | Must Have                                |
| **Responsável:**          | Julia Cohen                              |

**Descrição**

Como Aluno, Docente, Secretaria ou Membro Externo, quero fazer login com
a minha credencial e senha para que eu acesse o painel do meu perfil.

**Atores**

> **Ator principal:** Aluno, Docente, Secretaria ou Membro Externo.
>
> **Atores secundários:** Não há. A contagem de tentativas, o bloqueio
> temporário e a verificação do Status da Conta são regras do próprio
> login (CAD-06.4 e CAD-06.6) e aparecem no fluxo principal e nos fluxos
> de exceção.

**Pré-condições**

- A conta existe e o usuário já criou a senha no primeiro acesso
  > (US-10).

- Só a conta com o Status da Conta Ativa consegue entrar; os demais
  > status são tratados nos fluxos de exceção.

**Fluxo principal**

1.  O usuário acessa a tela de login.

2.  O sistema exibe os campos Credencial e Senha.

3.  O usuário informa a credencial e a senha e clica em "Entrar".

4.  O sistema identifica a conta pela credencial e
    > <span class="mark">verifica se o Status da Conta é Ativa e se a
    > conta não está bloqueada</span>.

5.  O sistema confere a senha e zera o contador de tentativas
    > incorretas.

6.  O sistema abre a sessão e direciona o usuário para o painel do seu
    > perfil (Aluno, Docente, Secretaria, Coordenador de Curso ou Membro
    > Externo).

**Fluxos alternativos**

1.  Login do Aluno pelo e-mail: o Aluno pode informar o e-mail
    > institucional no lugar da matrícula; o restante do fluxo é igual.

**Fluxos de exceção**

> E1. Senha incorreta: o sistema soma uma tentativa e exibe "Credencial
> ou senha inválida", sem informar qual dos dois está errado. Retorna ao
> passo 3.
>
> E2. Bloqueio por tentativas (CAD-06.6): na terceira senha incorreta
> seguida para a mesma conta, qualquer que seja a credencial usada
> (matrícula ou e-mail), o sistema bloqueia a conta por 15 minutos e
> exibe uma mensagem com o bloqueio e o tempo restante. Durante o
> bloqueio, até a senha correta é recusada.
>
> E3. Membro Externo com o Status da Conta Expirada (CAD-03.3): o login
> segue o Status da Conta. Com a conta Expirada, o sistema nega o acesso
> e exibe "Seu acesso expirou. Procure o Orientador, o Professor da
> Disciplina, a Secretaria ou o Coordenador de Curso". Quando a conta
> volta para Ativa, por nova banca, reagendamento ou prorrogação
> (US-06), o login volta a funcionar com o mesmo e-mail e a mesma senha.
>
> E4. Conta com o Status Aguardando Ativação: o sistema exibe "Conta
> ainda não ativada" e o link "Primeiro acesso" (US-10).
>
> E5. Conta com o Status Inativa (Docente ou Secretaria inativados,
> US-04): o sistema nega o acesso e exibe "Conta inativa".
>
> E6. Campo vazio: sem credencial ou sem senha, o sistema exibe "Informe
> a credencial e a senha" e não tenta autenticar. Retorna ao passo 3.

**Pós-condições**

- A sessão fica aberta e o usuário vê o painel do seu perfil.

- O contador de tentativas incorretas da conta volta a zero.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                                                                                       | **Resumo da regra em uma frase**                                                                                                                                                                                                        |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-06.4** | O sistema deve mostrar um formulário de login que deve conter os campos Credencial e Senha.                                                                                                                                   | <span class="mark">Login com Credencial (matrícula ou e-mail para Aluno; e-mail para os demais) e Senha, aceito só para conta com Status da Conta Ativa.</span>                                                                         |
| **CAD-06.6** | \[Exceção\] O sistema deve bloquear o acesso após 3 tentativas de senha incorretas.                                                                                                                                           | Após 3 senhas incorretas seguidas, o acesso fica bloqueado por 15 minutos.                                                                                                                                                              |
| **CAD-03.3** | O sistema deve permitir a manutenção do Status da Conta do Membro Externo, com os valores Aguardando Ativação, Ativa ou Expirada, expirando o acesso 7 dias após a defesa e permitindo a renovação ou a prorrogação da conta. | <span class="mark">Status da Conta do Membro Externo (Aguardando Ativação, Ativa ou Expirada): Ativa até 7 dias após a defesa mais distante; nova banca, reagendamento ou Prorrogar devolvem o acesso com o mesmo login e senha.</span> |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Alunos: Matrícula ou E-mail. Docentes e externos: E-mail.
>
> 2\. Bloqueio automático de 15 min após 3 erros.

***Cenário 1:*** Login do aluno pela matrícula

> **Dado que** o aluno tem conta ativa
>
> **Quando** informa a matrícula e a senha correta e clica em "Entrar"
>
> **Então** o sistema abre a sessão e exibe o painel do Aluno

***Cenário 2:*** Login do aluno pelo e-mail

**Dado que** o aluno tem conta ativa com o e-mail institucional
vinculado

**Quando** informa o e-mail institucional e a senha correta e clica em
"Entrar"

**Então** o sistema abre a sessão e exibe o painel do Aluno

***Cenário 3:*** Login do docente pelo e-mail

**Dado que** o docente tem conta ativa

**Quando** informa o e-mail e a senha correta e clica em "Entrar"

**Então** o sistema abre a sessão e exibe o painel do Docente

***Cenário 4:*** Senha incorreta

> **Dado que** o usuário não tem tentativas incorretas registradas
>
> **Quando** informa a credencial correta e uma senha errada
>
> **Então** o sistema exibe "Credencial ou senha inválida"
>
> **E** registra uma tentativa incorreta

***Cenário 5:*** Bloqueio após 3 erros

> **Dado que** o usuário já errou a senha 2 vezes seguidas
>
> **Quando** erra a senha pela terceira vez
>
> **Então** o sistema bloqueia o acesso por 15 minutos e mostra o tempo
> restante
>
> **E** recusa novas tentativas até o fim do prazo, mesmo com a senha
> correta

***Cenário 6:*** Bloqueio vale para matrícula e e-mail juntos

> **Dado que** o aluno errou a senha 2 vezes usando a matrícula
>
> **Quando** erra a senha pela terceira vez usando o e-mail
> institucional
>
> **Então** o sistema bloqueia a conta por 15 minutos
>
> **E** recusa o login tanto pela matrícula quanto pelo e-mail até o fim
> do prazo

***Cenário 7:*** Contador zerado após login correto

> **Dado que** o usuário errou a senha 2 vezes seguidas
>
> **Quando** informa a senha correta na terceira tentativa
>
> **Então** o sistema abre a sessão e zera o contador de tentativas
> incorretas
>
> **E** um novo erro depois disso conta como a primeira tentativa

***Cenário 8:*** Membro Externo com conta expirada

> **Dado que** a conta do Membro Externo está com o Status Expirada
>
> **Quando** ele informa e-mail e senha corretos
>
> **Então** o sistema nega o acesso e exibe "Seu acesso expirou. Procure
> o Orientador, o Professor da Disciplina, a Secretaria ou o Coordenador
> de Curso"

***Cenário 9:*** Membro Externo com conta reativada

> **Dado que** a conta do Membro Externo voltou para o Status Ativa
> depois de uma nova banca (US-06)
>
> **Quando** ele informa e-mail e a mesma senha de antes
>
> **Então** o sistema abre a sessão e exibe o painel do Membro Externo

***Cenário 10:*** Conta aguardando ativação

> **Dado que** o aluno foi matriculado e a conta está com o Status
> Aguardando Ativação
>
> **Quando** informa a matrícula e uma senha e clica em "Entrar"
>
> **Então** o sistema exibe "Conta ainda não ativada" e o link "Primeiro
> acesso"

***Cenário 11:*** Conta inativa

> **Dado que** a conta do docente está com o Status Inativa (US-04)
>
> **Quando** ele informa e-mail e senha corretos
>
> **Então** o sistema nega o acesso e exibe "Conta inativa"

***Cenário 12:*** Campo vazio

> **Dado que** o usuário está na tela de login
>
> **Quando** clica em "Entrar" sem informar a credencial ou sem informar
> a senha
>
> **Então** o sistema exibe "Informe a credencial e a senha" e não tenta
> autenticar

**Tela no protótipo**

**Tela:** Fazer login



**Diagrama de sequência**

**Diagrama relacionado:** Primeiro acesso e login.

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[ \] Descrição no formato Como, Quero, Para que
>
> \[ \] Requisitos da matriz conferidos
>
> \[ \] Fluxo principal e fluxos alternativos escritos
>
> \[ \] Atores, pré-condições e pós-condições preenchidos
>
> \[ \] Fluxos de exceção escritos
>
> \[ \] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-12 Recuperar ou alterar a senha

| **Épico:**                | Cadastro e Manutenção                    |
|---------------------------|------------------------------------------|
| **Feature:**              | Acesso e Login                           |
| **Requisitos da matriz:** | RBN-CAD-06.5, RBN-CAD-06.7, RBN-CAD-06.8 |
| **Prioridade (MoSCoW):**  | Must Have                                |
| **Responsável:**          | Julia Cohen                              |

**Descrição**

Como Aluno, Docente, Secretaria ou Membro Externo, quero recuperar ou
alterar a minha senha para que eu volte a ter acesso em caso de perda.

**Atores**

> **Ator principal:** Aluno, Docente, Secretaria ou Membro Externo; no
> reset do primeiro acesso, o Professor da Disciplina.
>
> **Atores secundários:** Serviço de e-mail (envio do link de
> redefinição) e Aluno, no caso do reset.

**Pré-condições**

- Para alterar a senha, o usuário está autenticado com o Status da Conta
  > Ativa (US-11).

- Para recuperar a senha, a conta está Ativa e o usuário sabe o e-mail
  > cadastrado.

- Para resetar o primeiro acesso, o aluno está na turma do Professor da
  > Disciplina.

**Fluxo principal**

- O usuário autenticado acessa "Meu perfil" e clica em "Alterar senha".

- O sistema exibe os campos Senha Atual, Nova Senha e Confirmação da
  > Nova Senha.

- O usuário preenche os campos e clica em "Salvar".

- O sistema confere a senha atual e valida a nova senha e a confirmação.

- O sistema grava a nova senha e exibe "Senha alterada com sucesso".

**Fluxos alternativos**

1.  Esqueci minha senha (CAD-06.7): na tela de login, o usuário clica em
    > "Esqueci minha senha" e informa o e-mail cadastrado. O sistema
    > envia um link de redefinição válido por 24 horas e exibe "Se a
    > conta existir, enviaremos um link para o e-mail cadastrado". Ao
    > abrir o link, o usuário informa Nova Senha e Confirmação, com a
    > mesma regra do primeiro acesso; o sistema grava a senha e invalida
    > o link.

2.  Reset do primeiro acesso (CAD-06.8): quando o aluno vinculou um
    > e-mail errado no primeiro acesso, o Professor da Disciplina abre o
    > painel do aluno (US-41), clica em "Resetar primeiro acesso" e
    > confirma. O sistema limpa o e-mail e a senha vinculados, invalida
    > os links de ativação pendentes e volta a conta para "Aguardando
    > Ativação". A opção só aparece para alunos da turma do Professor.

**Fluxos de exceção**

> E1. Link de redefinição vencido ou já usado: o sistema exibe "Link
> inválido ou vencido. Solicite um novo".
>
> E2. Senha atual incorreta: o sistema exibe "Senha atual incorreta" e
> não altera a senha. Retorna ao passo 3.
>
> E3. Nova senha fora da regra ou confirmação diferente: o sistema exibe
> "A senha deve ter de 8 a 64 caracteres, com ao menos 1 letra e 1
> número" ou "As senhas não conferem". Retorna ao passo 3.
>
> E4. Conta que não está Ativa: em "Esqueci minha senha", o sistema
> exibe a mesma mensagem genérica e não envia o link. A conta Aguardando
> Ativação usa o Primeiro acesso (US-10); a Inativa ou Expirada segue as
> US-04 e US-06.

**Pós-condições**

- A nova senha fica gravada e o link de redefinição deixa de valer.

- No reset, a conta do aluno volta para Aguardando Ativação, sem e-mail
  > e sem senha, e ele refaz o primeiro acesso (US-10).

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                   | **Resumo da regra em uma frase**                                                                                                                                                                                                                                                    |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-06.5** | O sistema deve mostrar um formulário de alteração de senha que deve conter os campos Senha Atual, Nova Senha e Confirmação da Nova Senha. | A Senha Atual, de 8 a 64 caracteres e exibida mascarada, deve ser igual à senha em uso para que a alteração seja aceita. A Nova Senha segue a mesma regra da ativação: 8 a 64 caracteres, com ao menos 1 letra e 1 número. A Confirmação da Nova Senha deve ser igual à Nova Senha. |
| **CAD-06.7** | \[Exceção\] O sistema deve permitir a recuperação de senha de Aluno, Docente, Secretaria e Membro Externo.                                | Qualquer perfil pode usar "Esqueci minha senha", informando o e-mail cadastrado, e receber um link de redefinição válido por 24 horas.                                                                                                                                              |
| **CAD-06.8** | \[Exceção\] O sistema deve permitir que o Professor da Disciplina resete o vínculo de primeiro acesso do Aluno.                           | O Professor da Disciplina pode resetar o primeiro acesso de um aluno da sua turma, limpando o e-mail e a senha vinculados por engano e invalidando os links pendentes.                                                                                                              |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Validação de senha atual para alteração.
>
> 2\. Envio de link 24h para "Esqueci minha senha".
>
> 3\. Prof. da Disciplina pode resetar e-mail errado de aluno.

***Cenário 1:*** Alteração de senha com sucesso

> **Dado que** o usuário está autenticado
>
> **Quando** informa a senha atual correta e uma nova senha válida,
> igual à confirmação, e clica em "Salvar"
>
> **Então** o sistema grava a nova senha e exibe "Senha alterada com
> sucesso"

***Cenário 2:*** Senha atual incorreta

> **Dado que** o usuário está no formulário de alteração de senha
>
> **Quando** informa uma senha atual errada
>
> **Então** o sistema exibe "Senha atual incorreta" e mantém a senha
> anterior

***Cenário 3:*** Recuperação por "Esqueci minha senha"

> **Dado que** o usuário tem conta ativa e esqueceu a senha
>
> **Quando** clica em "Esqueci minha senha", informa o e-mail
> cadastrado, abre o link em menos de 24 horas e define uma nova senha
> válida
>
> **Então** o sistema grava a nova senha
>
> **E** o link deixa de valer

***Cenário 4:*** Link de recuperação vencido

> **Dado que** o link de recuperação foi gerado há mais de 24 horas
>
> **Quando** o usuário abre o link
>
> **Então** o sistema exibe "Link inválido ou vencido. Solicite um novo"

***Cenário 5:*** Reset do primeiro acesso pelo Professor

> **Dado que** o aluno vinculou um e-mail errado no primeiro acesso
>
> **Quando** o Professor da Disciplina clica em "Resetar primeiro
> acesso" e confirma
>
> **Então** a conta do aluno volta para "Aguardando Ativação", sem
> e-mail e sem senha
>
> **E** o aluno pode refazer o primeiro acesso com o e-mail correto

***Cenário 6:*** Nova senha fora da regra

> **Dado que** o usuário está no formulário de alteração de senha
>
> **Quando** informa a nova senha "12345678", sem letra
>
> **Então** o sistema exibe "A senha deve ter de 8 a 64 caracteres, com
> ao menos 1 letra e 1 número" e mantém a senha anterior

***Cenário 7:*** Reset só para alunos da própria turma

> **Dado que** o aluno pertence a outra turma
>
> **Quando** o Professor da Disciplina abre o perfil desse aluno
>
> **Então** a opção "Resetar primeiro acesso" não aparece

***Cenário 8:*** Recuperação de conta que não está ativa

> **Dado que** a conta está com o Status Aguardando Ativação
>
> **Quando** o usuário pede "Esqueci minha senha"
>
> **Então** o sistema exibe a mensagem genérica e não envia o link

**Tela no protótipo**

**Tela:** Recuperar ou alterar a senha



**Diagrama de sequência**

**Diagrama relacionado:** Sem diagrama próprio: a recuperação reutiliza
a geração e o envio de link mostrados no diagrama "Primeiro acesso e
login".

**Link:** –

**Pronta para desenvolver**

> \[ \] Descrição no formato Como, Quero, Para que
>
> \[ \] Requisitos da matriz conferidos
>
> \[ \] Fluxo principal e fluxos alternativos escritos
>
> \[ \] Atores, pré-condições e pós-condições preenchidos
>
> \[ \] Fluxos de exceção escritos
>
> \[ \] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-37 Reenviar o link de ativação vencido

| **Épico:**                | Cadastro e Manutenção |
|---------------------------|-----------------------|
| **Feature:**              | Acesso e Login        |
| **Requisitos da matriz:** | RBN-CAD-06.9          |
| **Prioridade (MoSCoW):**  | Must Have             |
| **Responsável:**          | Julia Cohen           |

**Descrição**

Como Aluno, Docente, Secretaria ou Membro Externo que ainda não ativou a
conta, quero receber um novo link de ativação quando o anterior vencer
para que eu consiga fazer o primeiro acesso.

**Atores**

> **Ator principal:** Aluno, Docente, Secretaria ou Membro Externo com o
> Status da Conta Aguardando Ativação.
>
> **Atores secundários:** Serviço de e-mail (envio do novo link).

**Pré-condições**

- A conta está com o Status da Conta Aguardando Ativação e tem e-mail
  > vinculado.

- O link de ativação anterior foi gerado há mais de 24 horas e não foi
  > usado.

**Fluxo principal**

1.  O usuário abre um link de ativação gerado há mais de 24 horas.

2.  O sistema verifica que o link venceu e exibe o aviso "Este link de
    > ativação venceu" com o botão "Reenviar link de ativação".

3.  O usuário clica em "Reenviar link de ativação".

4.  O sistema invalida o link anterior e gera um novo link válido por 24
    > horas.

5.  O sistema envia o novo link ao e-mail cadastrado na conta e exibe
    > "Enviamos um novo link para o seu e-mail".

6.  O usuário abre o novo link e continua a ativação pela US-10, a
    > partir do passo 7.

**Fluxos alternativos**

1.  Novo pedido pelo Primeiro acesso: o usuário também pode pedir um
    > novo link refazendo o Primeiro acesso (US-10, fluxo alternativo
    > B); o resultado é o mesmo, e o link anterior deixa de valer.

**Fluxos de exceção**

> E1. Link antigo usado depois do reenvio: o sistema exibe "Link
> inválido. Use o link mais recente enviado ao seu e-mail".
>
> E2. Conta já ativa: o sistema exibe "Esta conta já está ativa" e
> direciona o usuário para o login.
>
> E3. Conta resetada pelo Professor (US-12): sem e-mail vinculado, o
> sistema não reenvia e orienta o aluno a refazer o "Primeiro acesso".

**Pós-condições**

- Existe um novo link de ativação válido por 24 horas, e o anterior
  > deixa de valer.

- A conta continua Aguardando Ativação, sem senha definida, até o
  > usuário criar a senha (US-10).

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                             | **Resumo da regra em uma frase**                                                                         |
|--------------|-------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| **CAD-06.9** | \[Exceção\] O sistema deve tratar o link de ativação não utilizado dentro do prazo. | O link de ativação não usado em 24 horas vence, e o usuário pode pedir um novo, que invalida o anterior. |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Link vencido após 24 horas exibe aviso e o botão "Reenviar link de
> ativação".
>
> 2\. Cada novo link invalida o anterior.

***Cenário 1:*** Aviso ao abrir link vencido

> **Dado que** o link de ativação foi gerado há mais de 24 horas e não
> foi usado
>
> **Quando** o usuário abre o link
>
> **Então** o sistema não exibe o formulário de senha
>
> **E** exibe o aviso "Este link de ativação venceu" e o botão "Reenviar
> link de ativação"

***Cenário 2:*** Reenvio do link

> **Dado que** o usuário está no aviso de link vencido
>
> **Quando** clica em "Reenviar link de ativação"
>
> **Então** o sistema gera um novo link válido por 24 horas e o envia ao
> e-mail cadastrado
>
> **E** exibe "Enviamos um novo link para o seu e-mail"

***Cenário 3:*** Link anterior invalidado

> **Dado que** um novo link de ativação já foi enviado
>
> **Quando** o usuário abre o link anterior
>
> **Então** o sistema exibe "Link inválido. Use o link mais recente
> enviado ao seu e-mail"

***Cenário 4:*** Conta já ativa

> **Dado que** a conta do usuário já foi ativada
>
> **Quando** ele abre um link de ativação antigo
>
> **Então** o sistema exibe "Esta conta já está ativa" e direciona para
> o login

***Cenário 5:*** Conta resetada pelo Professor

> **Dado que** o Professor da Disciplina resetou o primeiro acesso do
> aluno (US-12)
>
> **Quando** o aluno abre o link antigo e clica em "Reenviar link de
> ativação"
>
> **Então** o sistema não reenvia e orienta o aluno a refazer o
> "Primeiro acesso"

**Tela no protótipo**

**Tela:** Reenviar o link de ativação vencido



**Diagrama de sequência**

**Diagrama relacionado:** Primeiro acesso e login.

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[ \] Descrição no formato Como, Quero, Para que
>
> \[ \] Requisitos da matriz conferidos
>
> \[ \] Fluxo principal e fluxos alternativos escritos
>
> \[ \] Atores, pré-condições e pós-condições preenchidos
>
> \[ \] Fluxos de exceção escritos
>
> \[ \] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-38 Editar o perfil e ver as notificações

| **Épico:**                | Cadastro e Manutenção      |
|---------------------------|----------------------------|
| **Feature:**              | Acesso e Login             |
| **Requisitos da matriz:** | RBN-CAD-13.1, RBN-CAD-13.2 |
| **Prioridade (MoSCoW):**  | Must Have                  |
| **Responsável:**          | Julia Cohen                |

**Descrição**

Como Aluno, Docente, Secretaria ou Membro Externo, quero editar o meu
perfil e ver as minhas notificações para que meus dados fiquem
atualizados e eu não perca nenhum aviso.

**Atores**

> **Ator principal:** Aluno, Docente, Secretaria ou Membro Externo.
>
> **Atores secundários:** Os usuários cujas ações geram as notificações
> nas outras US: o Professor da Disciplina (entregas, US-15), o Aluno e
> o Orientador (orientação, US-17 e US-18) e quem agenda a defesa
> (bancas, US-21).

**Pré-condições**

- O usuário está autenticado com o Status da Conta Ativa (US-11).

**Fluxo principal**

1.  O usuário clica no seu ícone no topo da tela e escolhe "Meu perfil".

2.  O sistema exibe os dados da conta, com os campos editáveis do perfil
    > habilitados e os demais só para leitura.

3.  O usuário altera os campos que o seu perfil permite (CAD-13.1): o
    > Aluno, o E-mail Institucional; o Docente, inclusive o Coordenador
    > de Curso, a Imagem de Assinatura (PNG ou JPG, até 2 MB, usada na
    > avaliação, na Ata Final e na Folha de Aprovação); o Membro
    > Externo, E-mail, Titulação, Instituição de Origem e Imagem de
    > Assinatura. A Secretaria só consulta os próprios dados, que são
    > alterados pelo Coordenador de Curso (US-03). Depois, clica em
    > "Salvar".

4.  O sistema valida os dados e grava as alterações, exibindo "Perfil
    > atualizado". Se o e-mail mudou, envia um link de confirmação ao
    > novo endereço, e a troca só vale depois da confirmação.

5.  O usuário clica no ícone de sino, que mostra o número de
    > notificações não lidas.

6.  O sistema exibe a central de notificações, da mais recente para a
    > mais antiga, com título, data e hora.

7.  O usuário clica em uma notificação.

8.  O sistema marca a notificação como lida, atualiza o contador e abre
    > a tela relacionada (ex.: entrega, convite de banca ou pedido de
    > orientação).

**Fluxos alternativos**

1.  Marcar como lidas: o sistema marca as notificações como lidas e zera
    > o contador.

2.  Sem notificações: o sistema exibe "Você não tem notificações".

**Fluxos de exceção**

> E1. Item relacionado indisponível: se o item da notificação foi
> removido ou cancelado, o sistema marca a notificação como lida e exibe
> "Este item não está mais disponível".
>
> E2. Dado em formato inválido: e-mail fora do formato, e-mail
> institucional do Aluno fora do domínio @uea.edu.br, e-mail já usado
> por outra conta, ou imagem de assinatura que não seja PNG ou JPG ou
> que passe de 2 MB. O sistema destaca o campo e não salva. Retorna ao
> passo 3.
>
> E3. Troca de e-mail não confirmada: enquanto o link enviado ao novo
> endereço não for aberto, o e-mail antigo continua valendo para login e
> notificações.

**Pós-condições**

- Os dados alterados ficam gravados no perfil.

- As notificações abertas ficam marcadas como lidas, e o contador mostra
  > só as que faltam.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                                                                          | **Resumo da regra em uma frase**                                                                                                                                                                                                                                                                                                                    |
|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-13.1** | O sistema deve permitir que o usuário altere, no próprio perfil: E-mail Institucional (Aluno); Imagem de Assinatura (Docente); E-mail, Titulação, Instituição de Origem e Imagem de Assinatura (Membro Externo). | Cada perfil edita só o que a matriz libera: o Aluno, o E-mail Institucional; o Docente, inclusive o Coordenador, a Imagem de Assinatura (PNG ou JPG, até 2 MB); o Membro Externo, E-mail, Titulação, Instituição de Origem e Imagem de Assinatura; a Secretaria, nenhum campo. A troca de e-mail exige confirmação por link e respeita a unicidade. |
| **CAD-13.2** | O sistema deve exibir a central de notificações do usuário.                                                                                                                                                      | A central de notificações mostra o número de não lidas e as mais recentes, com data e hora, a opção Marcar como lidas e o acesso direto à tela relacionada.                                                                                                                                                                                         |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Cada perfil edita apenas os dados permitidos (ex.: imagem de
> assinatura do docente).
>
> 2\. Central de notificações com contador de não lidas, data e hora e
> acesso direto à tela relacionada.

***Cenário 1:*** Edição de dado permitido

> **Dado que** o Docente está em "Meu perfil"
>
> **Quando** envia uma nova imagem de assinatura em PNG e clica em
> "Salvar"
>
> **Então** o sistema grava a alteração e exibe "Perfil atualizado"

***Cenário 2:*** Campos não editáveis

> **Dado que** o Aluno está em "Meu perfil"
>
> **Quando** tenta alterar a Matrícula ou o Curso
>
> **Então** o sistema mantém esses campos bloqueados para edição

***Cenário 3:*** Formato inválido

> **Dado que** o Docente está em "Meu perfil"
>
> **Quando** envia a imagem de assinatura em um arquivo PDF
>
> **Então** o sistema exibe a mensagem de formato não aceito e não salva

***Cenário 4:*** Abrir notificação não lida

> **Dado que** o usuário tem 3 notificações não lidas
>
> **Quando** clica em uma delas na central de notificações
>
> **Então** o sistema abre a tela relacionada
>
> **E** o contador de não lidas passa para 2

***Cenário 5:*** Aluno altera o e-mail institucional

> **Dado que** o Aluno está em "Meu perfil"
>
> **Quando** troca o e-mail institucional por outro @uea.edu.br que não
> está em uso e clica em "Salvar"
>
> **Então** o sistema envia um link de confirmação ao novo e-mail
>
> **E** o novo e-mail só passa a valer depois que o link é aberto

***Cenário 6:*** E-mail institucional fora do domínio

> **Dado que** o Aluno está em "Meu perfil"
>
> **Quando** informa o e-mail "aluno@gmail.com" e clica em "Salvar"
>
> **Então** o sistema destaca o campo e não salva

***Cenário 7:*** Membro Externo altera a titulação

> **Dado que** o Membro Externo está em "Meu perfil"
>
> **Quando** muda a Titulação de Mestre para Doutor e clica em "Salvar"
>
> **Então** o sistema grava a alteração e exibe "Perfil atualizado"

***Cenário 8:*** Secretaria só consulta o perfil

> **Dado que** a Secretaria está em "Meu perfil"
>
> **Quando** abre os dados da conta
>
> **Então** todos os campos aparecem só para leitura e o botão "Salvar"
> não aparece

***Cenário 9:*** Item da notificação indisponível

> **Dado que** o usuário tem uma notificação de um convite de banca que
> foi cancelado
>
> **Quando** clica nessa notificação
>
> **Então** o sistema exibe "Este item não está mais disponível" e marca
> a notificação como lida

***Cenário 10:*** Marcar como lidas

> **Dado que** o usuário tem 5 notificações não lidas
>
> **Quando** clica em "Marcar como lidas"
>
> **Então** o contador de não lidas fica zerado

***Cenário 11:*** Imagem de assinatura acima de 2 MB

> **Dado que** o Docente está em "Meu perfil"
>
> **Quando** envia uma imagem de assinatura em JPG com 3 MB
>
> **Então** o sistema destaca o campo e não salva

**Tela no protótipo**

**Tela:** \[nome da tela, Anexo D\]





**Diagrama de sequência**

**Diagrama relacionado:** Sem diagrama próprio: consulta e edição
simples de dados do próprio usuário.

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[ \] Descrição no formato Como, Quero, Para que
>
> \[ \] Requisitos da matriz conferidos
>
> \[ \] Fluxo principal e fluxos alternativos escritos
>
> \[ \] Atores, pré-condições e pós-condições preenchidos
>
> \[ \] Fluxos de exceção escritos
>
> \[ \] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

# Maria Luísa Gomes: Contas e filtro de curso

## US-03 Cadastrar e alterar docentes e secretaria

| **Épico:**                | Cadastro e Manutenção                                                |
|---------------------------|----------------------------------------------------------------------|
| **Feature:**              | Gestão de Contas                                                     |
| **Requisitos da matriz:** | RBN-CAD-01.1, RBN-CAD-01.2, RBN-CAD-01.4, RBN-CAD-02.1, RBN-CAD-02.2 |
| **Prioridade (MoSCoW):**  | Must Have                                                            |
| **Responsável:**          | Maria Luísa Gomes                                                    |

**Descrição**

Como Coordenação ou Secretaria, quero cadastrar e alterar Docentes e
Secretaria para que tenham os papéis e permissões no sistema.

**Atores**

- **Ator principal:** Secretaria ou Coordenador de Curso (cadastra e
  > altera Docente); Coordenador de Curso (cadastra e altera
  > Secretaria).

- **Atores secundários:** Docente ou Secretaria cadastrado, que ativa a
  > conta depois pelo primeiro acesso (US-10); módulo de login (US-11),
  > que passa a reconhecer a conta; US-39, que fornece o filtro de Curso
  > da listagem.

**Pré-condições**

1.  O usuário está autenticado (US-11), com a conta ativa, como
    > Secretaria ou Coordenador de Curso.

2.  O usuário tem um curso associado: Curso Coordenado (Coordenador) ou
    > Curso Vinculado (Secretaria).

3.  Os cursos do NUCOMP (Engenharia de Computação, Sistemas de
    > Informação e Licenciatura em Computação) estão disponíveis nas
    > listas suspensas.

4.  Para cadastrar ou alterar Secretaria, o usuário é o Coordenador do
    > curso.

5.  Para alterar, o docente ou a Secretaria já está cadastrado e
    > pertence ao curso do usuário (CAD-14.1).

**Fluxo principal (cadastro de Docente)**

1.  A Secretaria ou o Coordenador de Curso acessa o menu Cadastros e
    > clica em “Cadastrar Docente”.

2.  O sistema exibe o formulário com Nome Completo, E-mail
    > Institucional, Titulação, Curso de Lotação e Papéis.

3.  O usuário preenche os campos e, se o docente for coordenar um curso,
    > marca o papel “Coordenador de Curso”.

4.  Ao marcar o papel, o sistema exibe o campo Curso Coordenado como
    > obrigatório, e o usuário seleciona o curso.

5.  O usuário clica em “Cadastrar”.

6.  O sistema valida os campos obrigatórios, os formatos, a unicidade do
    > e-mail e, se houver papel de Coordenador, se o curso já tem
    > Coordenador.

7.  O sistema cria a conta com o Status da Conta “Aguardando Ativação”,
    > exibe “Docente salvo” e o inclui na listagem de docentes. O
    > docente define a senha pelo primeiro acesso (US-10).

**Fluxos alternativos**

**A1. Docente comum (CAD-01.1).** No passo 3, o checkbox Papéis fica
desmarcado. O campo Curso Coordenado não aparece, e o sistema cria a
conta como Docente comum.

**A2. Docente Coordenador (CAD-01.1).** No passo 3, o usuário marca
“Coordenador de Curso”. O sistema exige o Curso Coordenado e, ao salvar,
cria o docente com o papel de Coordenador vinculado a esse curso.

**A3. Papel desmarcado antes de salvar.** Se o usuário desmarcar o
checkbox depois de marcá-lo, o campo Curso Coordenado some, o valor
escolhido é descartado e o fluxo segue como A1.

**A4. Cadastro de Secretaria (CAD-02.1).** (1) O Coordenador clica em
“Cadastrar secretaria”. (2) O sistema exibe Nome Completo, E-mail
Institucional e Curso Vinculado. (3) O Coordenador preenche e clica em
“Salvar”. (4) O sistema valida campos, formatos, unicidade do e-mail e
se o curso já tem Secretaria. (5) O sistema cria a conta com o Status
“Aguardando Ativação”, e a inclui na lista de Secretarias.

**A5. Curso liberado por inativação.** Se a Secretaria anterior do curso
foi inativada (US-04), o curso volta a aceitar o cadastro de uma nova
Secretaria (CAD-02.1).

**A6. Cancelamento.** Se o usuário clicar em “Cancelar”, o sistema
descarta o preenchimento, não cria conta e volta à listagem.

**A7. Listagem de docentes (CAD-01.4).** (1) A Secretaria ou o
Coordenador abre “Docentes”. (2) O sistema exibe a lista somente leitura
com Nome, E-mail Institucional, Titulação, Curso de Lotação, Papéis,
Status da Conta (Aguardando Ativação, Ativa ou Inativa) e quantidade de
orientandos, já filtrada pelo curso do usuário (US-39). (3) O usuário
troca o filtro de Curso e o sistema atualiza a lista. Sem docentes,
exibe “Nenhum registro”.

**A8. Alteração dos dados do docente (CAD-01.2).** (1) Na listagem, o
usuário clica em “Editar”. (2) O sistema exibe Nome Completo, E-mail
Institucional, Titulação, Curso de Lotação, Papéis e Curso Coordenado
preenchidos. (3) O usuário altera e clica em “Salvar”. (4) O sistema
repete as validações do cadastro. (5) O sistema grava e exibe “Dados
atualizados”.

**A9. Marcar o papel Coordenador na alteração (CAD-01.2).** O usuário
marca “Coordenador de Curso” e escolhe o Curso Coordenado. Se o curso
não tem Coordenador, o sistema grava o papel.

**A10. Desmarcar o papel Coordenador (CAD-01.2).** O usuário desmarca o
papel e salva. O docente passa a Docente comum, e o curso fica sem
Coordenador até um novo cadastro. É o passo prévio para inativar um
Coordenador (US-04).

**A11. Troca de Curso de Lotação ou de e-mail.** O novo Curso de Lotação
vale para as listas e relatórios. O novo e-mail passa a ser o login, com
a senha existente mantida.

**A12. Alteração dos dados da Secretaria (CAD-02.2).** (1) O Coordenador
clica em “Editar” na lista de Secretarias. (2) O sistema exibe Nome
Completo, E-mail Institucional e Curso Vinculado. (3) O Coordenador
altera e salva. (4) O sistema aplica as validações do cadastro e exibe
“Dados atualizados”.

**Fluxos de exceção**

**E1. Curso já tem Coordenador (CAD-01.1 e 01.2).** No cadastro ou na
alteração, o sistema exibe “O curso já possui Coordenador. Desmarque o
papel no coordenador atual para continuar” e não salva. Retorna ao passo
3.

**E2. Curso já tem Secretaria (CAD-02.1 e 02.2).** No cadastro, ou ao
trocar o Curso Vinculado, o sistema exibe “O curso já possui Secretaria
vinculada” e não salva.

**E3. E-mail já cadastrado.** O e-mail é único no sistema: vale para
Docente, Secretaria, Membro Externo e Aluno, inclusive contas inativas
ou expiradas, e para cadastros feitos no mesmo instante por outro
usuário. O sistema exibe “Este e-mail já está cadastrado” e não salva.

**E4. E-mail fora do padrão.** Formato inválido, domínio diferente de
@uea.edu.br ou mais de 100 caracteres. O sistema exibe “Informe um
e-mail institucional (@uea.edu.br)” e não salva.

**E5. Campo obrigatório vazio.** Nome, E-mail, Titulação, Curso de
Lotação, Curso Coordenado (com o papel marcado) ou Curso Vinculado
(Secretaria). O sistema destaca o campo com “Campo obrigatório” e não
salva.

**E6. Nome inválido.** Nome com números ou símbolos, ou com mais de 150
caracteres. O sistema exibe “O nome deve conter apenas letras e até 150
caracteres” e não salva.

**E7. Opção fora das listas.** Titulação diferente de Especialista,
Mestre ou Doutor, ou curso fora do NUCOMP. O sistema rejeita e exibe
“Selecione uma opção válida”.

**E8. Curso diferente do curso do usuário (CAD-14.1).** Os cadastros e
alterações ficam restritos ao próprio curso. Para docente ou Secretaria
de outro curso, o sistema não exibe Editar, e o acesso direto exibe
“Você só pode cadastrar e alterar dados do seu curso” e não salva (a
confirmar com a equipe).

**E9. Usuário sem permissão.** A Secretaria não vê “Nova secretaria” nem
“Editar” na lista de Secretarias. Aluno, Docente comum e Membro Externo
não veem o menu Cadastros. O acesso direto pela URL é bloqueado com
“Você não tem permissão para esta ação”.

**E10. Falha ao gravar.** O sistema exibe “Não foi possível salvar.
Tente novamente”, não grava e mantém os dados preenchidos no formulário.

**Pós-condições**

- Cadastro: a conta do Docente ou da Secretaria existe com o Status da
  > Conta “Aguardando Ativação”, sem senha e sem login até o primeiro
  > acesso (US-10).

- O docente aparece na listagem, com 0 orientandos, e a Secretaria na
  > lista de Secretarias.

- Com o papel marcado, o curso passa a ter exatamente um Coordenador.
  > Cada curso tem no máximo uma Secretaria.

- O e-mail cadastrado é o login e não pode ser usado por outro cadastro.

- Alteração: os novos dados estão gravados e refletidos na listagem, nas
  > bancas e nos relatórios.

- Em qualquer exceção, nenhum dado é gravado.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                                                                                                                                        | **Resumo da regra em uma frase**                                                                                                                                                                                                                                                               |
|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-01.1** | O sistema deve mostrar um formulário de cadastro do Docente (professor do NUCOMP, incluindo Professor da Disciplina, Orientador e Coordenador de Curso) que deve conter os campos Nome Completo, E-mail Institucional, Titulação, Curso de Lotação, Papéis e Curso Coordenado. | Formulário do Docente com Nome Completo, E-mail Institucional (@uea.edu.br, único), Titulação, Curso de Lotação, Papéis (caixa Coordenador de Curso) e Curso Coordenado (só com o papel marcado, um Coordenador por curso); ao salvar, a conta fica com o Status da Conta Aguardando Ativação. |
| **CAD-01.2** | O sistema deve permitir a alteração de Nome Completo, E-mail Institucional, Titulação, Curso de Lotação, Papéis e Curso Coordenado do Docente.                                                                                                                                 | A Secretaria ou o Coordenador altera esses campos do docente do seu curso, com as mesmas regras de formato e unicidade do cadastro.                                                                                                                                                            |
| **CAD-01.4** | O sistema deve exibir a listagem de docentes, com o filtro de Curso.                                                                                                                                                                                                           | Listagem somente leitura com Nome, E-mail, Titulação, Curso de Lotação, Papéis, Status da Conta e quantidade de orientandos; o filtro de Curso só muda a exibição.                                                                                                                             |
| **CAD-02.1** | O sistema deve mostrar um formulário de cadastro da Secretaria que deve conter os campos Nome Completo, E-mail Institucional e Curso Vinculado.                                                                                                                                | Formulário da Secretaria com Nome Completo, E-mail Institucional e Curso Vinculado (uma Secretaria por curso), cadastrada pelo Coordenador; ao salvar, a conta fica com o Status da Conta Aguardando Ativação.                                                                                 |
| **CAD-02.2** | O sistema deve permitir a alteração de Nome Completo, E-mail Institucional e Curso Vinculado da Secretaria.                                                                                                                                                                    | O Coordenador de Curso altera os dados da Secretaria, com as mesmas regras de formato do cadastro.                                                                                                                                                                                             |

Critérios do backlog (ponto de partida):

> 1\. Exige e-mail institucional (@uea.edu.br) único.
>
> 2\. Checkbox define quem recebe papel de Coordenador.

**Cenário 1: Cadastro de docente comum (fluxo principal, A1)**

Dado que a Secretaria está autenticada e não existe o e-mail
mlsg@uea.edu.br

Quando preenche Nome, E-mail, Titulação Doutor e Curso de Lotação, deixa
Coordenador desmarcado e clica em “Salvar”

Então o sistema cria a conta como Docente comum, com o Status da Conta
“Aguardando Ativação”, e exibe “Docente cadastrado com sucesso”

**Cenário 2: Cadastro por Coordenador (fluxo principal)**

Dado que o Coordenador de Sistemas de Informação está autenticado

Quando cadastra um docente lotado em Sistemas de Informação e salva

Então o sistema cria a conta com o Status da Conta “Aguardando Ativação”

**Cenário 3: Docente cadastrado como Coordenador (A2, critério 2)**

Dado que o curso Sistemas de Informação não tem Coordenador

Quando o usuário marca “Coordenador de Curso”, seleciona Sistemas de
Informação em Curso Coordenado e salva

Então o sistema cria o docente com o papel de Coordenador vinculado a
esse curso

**Cenário 4: Papel desmarcado antes de salvar (A3)**

Dado que o usuário marcou “Coordenador de Curso” e escolheu um Curso
Coordenado

Quando desmarca o checkbox e salva

Então o campo Curso Coordenado some e o sistema cria o docente como
Docente comum

**Cenário 5: E-mail duplicado entre docentes (E3, critério 1)**

Dado que já existe um docente com o e-mail maria@uea.edu.br

Quando o usuário tenta cadastrar outro Docente ou uma Secretaria com
esse e-mail

Então o sistema não salva e exibe “Este e-mail já está cadastrado”

**Cenário 6: E-mail já usado por outro perfil (E3)**

Dado que o e-mail carlos@uea.edu.br pertence a um Membro Externo ou a um
Aluno

Quando o usuário tenta cadastrar um Docente com esse e-mail

Então o sistema não salva e exibe “Este e-mail já está cadastrado”

**Cenário 7: E-mail de docente inativo (E3)**

Dado que o docente ana@uea.edu.br está com o Status da Conta Inativa

Quando o usuário tenta cadastrar um novo docente com esse e-mail

Então o sistema não salva e exibe “Este e-mail já está cadastrado” E o
usuário deve reativar o docente existente (US-04)

**Cenário 8: E-mail fora do domínio institucional (E4, critério 1)**

Dado que o usuário está no formulário de Docente

Quando informa maria@gmail.com e clica em “Salvar”

Então o sistema exibe “Informe um e-mail institucional (@uea.edu.br)” e
não salva

**Cenário 9: E-mail sem formato válido (E4)**

Dado que o usuário está no formulário de Docente

Quando informa “maria.uea.edu.br”, sem arroba, e clica em “Salvar”

Então o sistema exibe “Informe um e-mail institucional (@uea.edu.br)” e
não salva

**Cenário 10: E-mail com mais de 100 caracteres (E4)**

Dado que o usuário está no formulário de Docente

Quando informa um e-mail de @uea.edu.br com 101 caracteres

Então o sistema exibe “Informe um e-mail institucional (@uea.edu.br)” e
não salva

**Cenário 11: Nome com números (E6)**

Dado que o usuário está no formulário de Docente

Quando informa o nome “Maria Souza 2” e salva

Então o sistema exibe “O nome deve conter apenas letras e até 150
caracteres” e não salva

**Cenário 12: Nome com acentos aceito e limite de 150 caracteres
(CAD-01.1)**

Dado que o usuário está no formulário de Docente

Quando informa o nome “João Gonçalves Álvares” e, em outra tentativa, um
nome com 151 caracteres

Então o sistema aceita o primeiro e rejeita o segundo com “O nome deve
conter apenas letras e até 150 caracteres”

**Cenário 13: Campo obrigatório vazio (E5)**

Dado que o usuário está no formulário de Docente

Quando clica em “Salvar” sem informar a Titulação

Então o sistema destaca o campo com “Campo obrigatório” e não salva

**Cenário 14: Coordenador sem Curso Coordenado (E5)**

Dado que o usuário marcou “Coordenador de Curso”

Quando clica em “Salvar” sem escolher o Curso Coordenado

Então o sistema destaca o campo com “Campo obrigatório” e não salva

**Cenário 15: Curso já possui Coordenador (E1)**

Dado que o curso Sistemas de Informação já tem um Coordenador

Quando o usuário marca “Coordenador de Curso” e seleciona esse curso

Então o sistema exibe o alerta e impede o cadastro até que o papel seja
desmarcado no coordenador atual

**Cenário 16: Opção fora da lista (E7)**

Dado que o usuário está no formulário de Docente

Quando a requisição envia a Titulação “Livre-docente”

Então o sistema rejeita com “Selecione uma opção válida” e não salva

**Cenário 17: Docente de outro curso (E8, a confirmar)**

Dado que a Secretaria de Sistemas de Informação está autenticada

Quando tenta cadastrar um docente com Curso de Lotação Engenharia de
Computação

Então o sistema exibe “Você só pode cadastrar e alterar dados do seu
curso” e não salva

**Cenário 18: Cadastro de Secretaria com sucesso (A4)**

Dado que o Coordenador de Curso está autenticado e o curso escolhido não
tem Secretaria

Quando informa Nome Completo, E-mail Institucional e Curso Vinculado e
clica em “Salvar”

Então o sistema cria a conta da Secretaria com o Status da Conta
“Aguardando Ativação” e exibe “Secretaria cadastrada com sucesso”

**Cenário 19: Curso já possui Secretaria (E2)**

Dado que o curso escolhido já tem uma Secretaria

Quando o Coordenador tenta cadastrar outra Secretaria para esse curso

Então o sistema não salva e exibe “O curso já possui Secretaria
vinculada”

**Cenário 20: Curso liberado após inativar a Secretaria (A5)** Dado que
a Secretaria do curso foi inativada Quando o Coordenador cadastra uma
nova Secretaria para o curso Então o sistema cria a nova conta e o curso
volta a ter uma Secretaria ativa

**Cenário 21: Secretaria não cadastra Secretaria (E9)** Dado que a
Secretaria está autenticada Quando acessa o menu Cadastros Então o
sistema não exibe a opção “Nova secretaria” e bloqueia o acesso direto à
tela

**Cenário 22: Perfil sem acesso ao menu Cadastros (E9)** Dado que um
Aluno, um Docente comum ou um Membro Externo está autenticado Quando
tenta abrir a tela de cadastro de docente pela URL Então o sistema nega
o acesso e exibe “Você não tem permissão para esta ação”

**Cenário 23: Cancelamento do cadastro (A6)** Dado que o usuário
preencheu parte do formulário de Docente Quando clica em “Cancelar”
Então o sistema volta à listagem e nenhuma conta é criada

**Cenário 24: Listagem de docentes (A7, CAD-01.4)** Dado que a
Secretaria de Sistemas de Informação está autenticada Quando abre
“Docentes” Então o sistema exibe os docentes do curso com Nome, E-mail,
Titulação, Curso de Lotação, Papéis, Status da Conta e quantidade de
orientandos

**Cenário 25: Filtro de Curso na listagem (A7, US-39)** Dado que a
listagem está filtrada pelo curso do usuário Quando o usuário escolhe
“Todos” no filtro de Curso Então o sistema lista os docentes dos três
cursos

**Cenário 26: Listagem sem docentes (A7)** Dado que o curso escolhido no
filtro não tem docentes Quando o sistema aplica o filtro Então exibe
“Nenhum registro”

**Cenário 27: Docente recém-cadastrado ainda não entra (pós-condição,
US-11)** Dado que o docente foi cadastrado e está com o Status da Conta
“Aguardando Ativação” Quando tenta fazer login Então o sistema nega o
acesso com “Conta ainda não ativada” e oferece o link “Primeiro acesso”
E o docente aparece na listagem com 0 orientandos

**Cenário 28: Falha ao gravar (E10)** Dado que o usuário preencheu o
formulário corretamente Quando o sistema não consegue gravar a conta
Então exibe “Não foi possível salvar. Tente novamente”, não grava e
mantém os dados no formulário

**Cenário 29: Alteração dos dados do docente (A8, CAD-01.2)** Dado que o
Coordenador abriu a edição de um docente do seu curso Quando altera a
Titulação para Doutor e clica em “Salvar” Então o sistema grava e exibe
“Dados atualizados”

**Cenário 30: Alteração com e-mail duplicado (E3)** Dado que a
Secretaria abriu a edição do docente João Quando informa o e-mail de
outro usuário Então o sistema exibe “Este e-mail já está cadastrado” e
não grava

**Cenário 31: Alteração com dado inválido (E4, E6)** Dado que a
Secretaria abriu a edição de um docente Quando informa o nome “João 2”
ou um e-mail fora de @uea.edu.br Então o sistema exibe a mensagem do
campo e não grava

**Cenário 32: Alteração do e-mail muda o login (A11)** Dado que o
docente já tem o Status da Conta Ativa Quando a Secretaria altera o
e-mail para novo@uea.edu.br e salva Então o novo e-mail passa a ser o
login e a senha existente continua valendo

**Cenário 33: Marcar papel Coordenador na alteração (A9)** Dado que o
curso Licenciatura em Computação não tem Coordenador Quando o
Coordenador de Curso edita um docente, marca o papel e escolhe esse
curso Então o sistema grava o docente como Coordenador desse curso

**Cenário 34: Papel Coordenador em curso que já tem Coordenador (E1)**
Dado que o curso já tem um Coordenador Quando o usuário marca o papel em
outro docente desse curso e salva Então o sistema exibe o alerta e não
grava

**Cenário 35: Desmarcar o papel libera o curso (A10)** Dado que o
docente é o Coordenador do curso Quando o usuário desmarca o papel e
salva Então o docente vira Docente comum e o curso passa a aceitar um
novo Coordenador

**Cenário 36: Troca do Curso de Lotação (A11)** Dado que a Secretaria
abriu a edição de um docente do seu curso Quando altera o Curso de
Lotação e salva Então o sistema grava e o docente passa a aparecer na
listagem do novo curso

**Cenário 37: Alteração dos dados da Secretaria (A12, CAD-02.2)** Dado
que o Coordenador de Curso abriu a edição da Secretaria Quando corrige o
Nome Completo e salva Então o sistema grava e exibe “Dados atualizados”

**Cenário 38: Troca do Curso Vinculado para curso com Secretaria (E2)**
Dado que o curso Engenharia de Computação já tem uma Secretaria Quando o
Coordenador altera o Curso Vinculado de outra Secretaria para esse curso
Então o sistema exibe “O curso já possui Secretaria vinculada” e não
grava

**Cenário 39: Alteração em registro de outro curso (E8)** Dado que o
usuário filtrou os docentes de outro curso pelo filtro Quando tenta
editar um desses docentes Então o sistema não exibe o botão “Editar” e,
no acesso direto, exibe “Você só pode cadastrar e alterar dados do seu
curso”

**Cenário 40: Secretaria não edita Secretaria (E9)** Dado que a
Secretaria está autenticada Quando abre a lista de Secretarias Então o
sistema não exibe “Editar” e bloqueia o acesso direto à ação

**Tela no protótipo**

**Tela:** Cadastros
(Docentes)

**Tela:** Docentes



**Tela:** Cadastros (Secretaria)



**Tela:** Cadastros (Docentes - editar)



**Tela:** Cadastros (Secretaria - editar)



**Diagrama de sequência**

**Diagrama relacionado:** \[nome do diagrama ou "sem diagrama próprio" e
o motivo\]

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[x \] Descrição no formato Como, Quero, Para que
>
> \[x \] Requisitos da matriz conferidos
>
> \[x \] Fluxo principal e fluxos alternativos escritos
>
> \[x \] Atores, pré-condições e pós-condições preenchidos
>
> \[x \] Fluxos de exceção escritos
>
> x\[ \] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-04 Inativar e reativar docentes e secretaria

| **Épico:**                | Cadastro e Manutenção                                  |
|---------------------------|--------------------------------------------------------|
| **Feature:**              | Gestão de Contas                                       |
| **Requisitos da matriz:** | RBN-CAD-01.3, RBN-CAD-01.2, RBN-CAD-02.2, RBN-CAD-02.3 |
| **Prioridade (MoSCoW):**  | Must Have                                              |
| **Responsável:**          | Maria Luísa Gomes                                      |

**Descrição**

Como Coordenação ou Secretaria, quero inativar docentes e a Secretaria,
e reativar docentes, para que percam ou recuperem o acesso ao sistema
conforme o Status da Conta.

**Atores**

> **Ator principal:** Secretaria ou Coordenador de Curso ( inativar ou
> reativar Docente); Coordenador de Curso (inativar Secretaria)
>
> **Atores secundários:** Docente ou Secretaria afetado; módulos de
> orientação e coorientação (US-17, US-18, US-36 e US-45), banca (US-21
> e US-23) e turmas (US-07), consultados para verificar os vínculos;
> login (US-11); listagem de docentes (US-03); filtro de Curso (US-39)

**Pré-condições**

- O usuário está autenticado (US-11) como Secretaria ou Coordenador de
  > Curso, com a conta ativa.

- O docente ou a Secretaria pertence ao curso do usuário (CAD-14.1).

- Para inativar, o Status da Conta está Ativa. Para reativar docente,
  > está Inativa.

- Para inativar a Secretaria, o usuário é o Coordenador do curso.

**Fluxo principal**

1.  A Secretaria ou o Coordenador de Curso abre a listagem de docentes
    > (US-03) e clica em “Inativar” no docente.

2.  O sistema verifica os vínculos em aberto: TCCs ativos como
    > orientador ou coorientador (Em Andamento, Apto para Defesa,
    > Aprovado ou Aprovado com Correções, enquanto a Versão Final não
    > foi homologada), convites de coorientação sem resposta, bancas
    > Agendadas, Reagendadas ou Em Andamento, turmas não arquivadas e o
    > papel de Coordenador.

3.  Sem nenhum vínculo, o sistema pede a confirmação “Deseja inativar o
    > docente Nome?”.

4.  O usuário confirma, e o sistema repete a verificação de vínculos.

5.  O sistema muda o Status da Conta para “Inativa”, bloqueia o login e
    > retira o docente das listas de orientador, coorientador e
    > avaliador.

6.  O sistema mantém todo o histórico do docente.

**Fluxos alternativos**

A1. Reativação do docente (CAD-01.3). (1) O usuário filtra pelo seu
curso e clica em “Reativar” no docente com Status Inativa. (2) O sistema
pede confirmação. (3) O usuário confirma. (4) O Status da Conta volta a
Ativa, o docente volta a fazer login e a aparecer nas listas de
orientador e avaliador.

A2. Inativação da Secretaria (CAD-02.3). (1) O Coordenador clica em
“Inativar” na Secretaria. (2) O sistema pede confirmação. (3) O
Coordenador confirma. (4) O Status da Conta passa a Inativa, a conta
perde o login, mantém o histórico, e o curso fica livre para o cadastro
de uma nova Secretaria (US-03, A5).

A3. Inativar depois de encerrar os vínculos. Depois que o usuário
encerra ou transfere os vínculos apontados (orientandos, convites,
bancas, turmas ou papel de Coordenador), a inativação segue o fluxo
principal. Para tirar o papel de Coordenador, o usuário altera o docente
na US-03 (A10).

A4. Vínculos que não bloqueiam. TCC Pendente, Concluído, Reprovado,
Desistente, Jubilado ou Aprovado para TCC 2, convite já respondido,
banca Realizada ou Cancelada e turma arquivada não impedem a inativação.

A5. Cancelamento. Se o usuário cancelar na confirmação, nada é alterado.

**Fluxos de exceção**

**E1. Orientandos ou coorientandos com TCC ativo (CAD-01.3).** TCC Em
Andamento, Apto para Defesa, Aprovado ou Aprovado com Correções,
enquanto a Versão Final não foi homologada. O sistema não inativa e
exibe “Não é possível inativar: o docente possui N orientandos ou
coorientandos com TCC ativo”.

**E2. Convite de coorientação sem resposta.** O sistema não inativa e
informa o motivo.

**E3. Banca em aberto.** Sessão Agendada, Reagendada ou Em Andamento. O
sistema não inativa e informa o motivo.

**E4. Turma não arquivada.** Turma sob responsabilidade do docente. O
sistema não inativa e informa o motivo.

**E5. Papel de Coordenador de Curso.** O sistema não inativa e exibe que
o docente é Coordenador do curso.

**E6. Vários vínculos ao mesmo tempo.** O alerta lista todos os motivos,
por exemplo “possui 2 orientandos com TCC ativo e é Coordenador do
curso. Encerre ou transfira esses vínculos primeiro”. Retorna à listagem
sem alterar a conta.

**E7. Vínculo surgiu durante a confirmação.** Se, entre o passo 3 e o
passo 4, aparecer um vínculo (por exemplo, um convite de coorientação),
o sistema bloqueia a inativação e exibe o motivo.

**E8. Registro de outro curso (CAD-14.1).** O filtro só altera a
visualização. Para docente ou Secretaria de outro curso, o sistema não
exibe Inativar nem Reativar.

**E9. Sem permissão.** A Secretaria não vê Inativar na lista de
Secretarias. Aluno, Docente comum e Membro Externo não acessam a tela.

**E10. Ação indisponível para o status.** Docente com Status Inativa não
tem o botão “Inativar”, e docente com Status Ativa não tem o botão
“Reativar”.

**E11. Falha ao gravar.** O sistema exibe “Não foi possível salvar.
Tente novamente” e mantém a conta como estava.

**Pós-condições**

- Inativação de docente: Status da Conta “Inativa”, login bloqueado com
  > “Conta inativa” (US-11), fora das listas de orientador, coorientador
  > e avaliador, histórico de TCCs, bancas e atas mantido.

- Reativação: Status da Conta Ativa, login liberado e docente de volta
  > às listas, como Docente comum.

- Inativação de Secretaria: conta sem login, histórico mantido e curso
  > livre para uma nova Secretaria.

- Em qualquer exceção, nenhuma conta é alterada.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                           | **Resumo da regra em uma frase**                                                                                                                                                                                                                                  |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-01.3** | O sistema deve permitir a manutenção do Status da Conta do Docente, com os valores Aguardando Ativação, Ativa ou Inativa, por meio da inativação e da reativação. | A inativação é bloqueada enquanto houver vínculos (TCC ativo, convite sem resposta, banca em aberto, turma não arquivada ou papel de Coordenador), pede confirmação e informa o motivo; a reativação devolve o login e vale só para docentes do curso do usuário. |
| **CAD-02.3** | O sistema deve permitir a manutenção do Status da Conta da Secretaria, com os valores Aguardando Ativação, Ativa ou Inativa, por meio da inativação.              | A inativação, feita pelo Coordenador, pede confirmação, bloqueia o login, mantém o histórico e libera o curso para uma nova Secretaria.                                                                                                                           |

**Critérios de aceite**

*Critérios do backlog:*

1.  Bloqueia a inativação se o docente tiver orientandos ou
    > coorientandos com TCC ativo, convite de coorientação pendente,
    > banca agendada, turma não arquivada ou o papel de Coordenador; o
    > alerta informa o motivo.

2.  Histórico é mantido.

**Cenário 1: Inativação de docente sem vínculos (fluxo principal)** Dado
que o docente não tem orientandos ativos, convites pendentes, bancas em
aberto, turmas não arquivadas nem o papel de Coordenador Quando a
Secretaria clica em “Inativar” e confirma Então o sistema muda o Status
da Conta para “Inativa” e exibe “Docente inativado” E o docente deixa de
aparecer nas listas de orientador e de avaliador

**Cenário 2: Bloqueio por orientando com TCC ativo (E1, critério 1)**
Dado que o docente é orientador de um aluno com TCC Em Andamento Quando
o usuário clica em “Inativar” Então o sistema não inativa e exibe o
alerta “orientandos com TCC ativo”

**Cenário 3: Bloqueio por coorientando com TCC ativo (E1)** Dado que o
docente é coorientador de um aluno com TCC Apto para Defesa Quando o
usuário clica em “Inativar” Então o sistema não inativa e exibe o alerta
“coorientandos com TCC ativo”

**Cenário 4: Aprovado com Correções sem Versão Final homologada (E1)**
Dado que o docente orienta um TCC Aprovado com Correções cuja Versão
Final ainda não foi homologada Quando o usuário clica em “Inativar”
Então o sistema não inativa e informa que o TCC ainda é ativo

**Cenário 5: Bloqueio por convite de coorientação sem resposta (E2)**
Dado que o docente recebeu um convite de coorientação e ainda não
respondeu Quando o usuário clica em “Inativar” Então o sistema não
inativa e informa o convite pendente

**Cenário 6: Bloqueio por banca Agendada (E3)** Dado que o docente é
membro de uma banca com sessão Agendada Quando o usuário clica em
“Inativar” Então o sistema não inativa e informa a banca em aberto

**Cenário 7: Bloqueio por banca Reagendada ou Em Andamento (E3)** Dado
que o docente é membro de uma banca Reagendada ou Em Andamento Quando o
usuário clica em “Inativar” Então o sistema não inativa e informa a
banca em aberto

**Cenário 8: Bloqueio por turma não arquivada (E4)** Dado que o docente
é Professor da Disciplina de uma turma que não foi arquivada Quando o
usuário clica em “Inativar” Então o sistema não inativa e informa a
turma

**Cenário 9: Bloqueio por papel de Coordenador (E5)** Dado que o docente
é Coordenador do curso Sistemas de Informação Quando o usuário clica em
“Inativar” Então o sistema não inativa e informa que o docente é
Coordenador de Curso

**Cenário 10: Vários motivos juntos (E6)** Dado que o docente tem
orientandos ativos e uma turma não arquivada Quando o usuário clica em
“Inativar” Então o alerta lista os dois motivos, para que o usuário
saiba tudo o que precisa encerrar

**Cenário 11: TCC Pendente não bloqueia (A4)** Dado que o único
orientando do docente está com o TCC Pendente Quando o usuário clica em
“Inativar” e confirma Então o sistema inativa o docente

**Cenário 12: Outros vínculos que não bloqueiam (A4)** Dado que o
docente só tem orientandos com TCC Concluído, Reprovado, Desistente ou
Jubilado, bancas Realizadas ou Canceladas, convites respondidos e turmas
arquivadas Quando o usuário clica em “Inativar” e confirma Então o
sistema inativa o docente

**Cenário 13: Inativar um Coordenador em dois passos (A3)** Dado que o
docente é Coordenador e não tem outros vínculos Quando o usuário
desmarca o papel na US-03 e, depois, clica em “Inativar” e confirma
Então o sistema inativa o docente e o curso fica sem Coordenador até
novo cadastro

**Cenário 14: Cancelamento da confirmação (A5)** Dado que o usuário
clicou em “Inativar” em um docente sem vínculos Quando cancela na
confirmação Então o Status da Conta continua Ativa e nada é alterado

**Cenário 15: Vínculo surgiu durante a confirmação (E7)** Dado que o
docente estava sem vínculos quando o usuário abriu a confirmação Quando
um aluno envia um convite de coorientação ao docente antes de o usuário
confirmar Então o sistema bloqueia a inativação e informa o convite
pendente

**Cenário 16: Histórico mantido e login bloqueado (critério 2)** Dado
que o docente foi inativado Quando ele tenta fazer login e a Coordenação
consulta os relatórios antigos Então o sistema nega o acesso com “Conta
inativa” E os TCCs, bancas e atas anteriores do docente continuam
visíveis

**Cenário 17: Ação indisponível para o status (E10)** Dado que o docente
está com o Status da Conta Inativa Quando o usuário abre a listagem
Então o botão “Inativar” não aparece e aparece o botão “Reativar”

**Cenário 18: Docente de outro curso (E8)** Dado que a Secretaria de
Sistemas de Informação filtra por Engenharia de Computação Quando tenta
inativar ou reativar um docente desse curso Então o sistema não exibe as
ações e, no acesso direto, exibe “Você só pode alterar dados do seu
curso”

**Cenário 19: Reativação de docente (A1)** Dado que o docente do curso
do usuário está com o Status da Conta Inativa Quando o usuário clica em
“Reativar” e confirma Então o Status volta a Ativa, o docente volta a
fazer login e a aparecer nas listas de orientador e avaliador

**Cenário 20: Reativação de docente de outro curso (E8)** Dado que o
docente Inativo pertence a outro curso Quando o usuário tenta reativá-lo
Então o sistema não exibe o botão “Reativar” e bloqueia a ação direta

**Cenário 21: Inativação da Secretaria (A2, CAD-02.3)** Dado que o curso
tem uma Secretaria com Status da Conta Ativa Quando o Coordenador clica
em “Inativar” e confirma Então o Status passa a Inativa, a conta perde o
login e mantém o histórico

**Cenário 22: Curso liberado para nova Secretaria (A2)** Dado que a
Secretaria do curso está Inativa Quando o Coordenador cadastra uma nova
Secretaria para o curso (US-03) Então o sistema aceita o cadastro

**Cenário 23: Secretaria não inativa Secretaria (E9)** Dado que a
Secretaria está autenticada Quando abre a lista de Secretarias Então o
sistema não exibe “Inativar” e bloqueia o acesso direto à ação

**Cenário 24: Perfil sem permissão (E9)** Dado que um Aluno está
autenticado Quando tenta abrir a tela de docentes pela URL Então o
sistema nega o acesso e exibe “Você não tem permissão para esta ação”

**Cenário 25: Falha ao gravar (E11)** Dado que o usuário confirmou a
inativação de um docente sem vínculos Quando o sistema não consegue
gravar Então exibe “Não foi possível salvar. Tente novamente” e o
docente continua com o Status Ativa

**Tela no protótipo**

**Tela:** Docentes



**Tela:** Docentes



**Tela:** Docentes

**Tela:** Secretarias



**Tela:** Secretarias



**Diagrama de sequência**

**Diagrama relacionado:** \[nome do diagrama ou "sem diagrama próprio" e
o motivo\]

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[ \] Descrição no formato Como, Quero, Para que
>
> \[ \] Requisitos da matriz conferidos
>
> \[ \] Fluxo principal e fluxos alternativos escritos
>
> \[ \] Atores, pré-condições e pós-condições preenchidos
>
> \[ \] Fluxos de exceção escritos
>
> \[ \] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-05 Cadastrar e alterar membros externos

| **Épico:**                | Cadastro e Manutenção      |
|---------------------------|----------------------------|
| **Feature:**              | Gestão de Contas           |
| **Requisitos da matriz:** | RBN-CAD-03.1, RBN-CAD-03.2 |
| **Prioridade (MoSCoW):**  | Must Have                  |
| **Responsável:**          | Maria Luísa Gomes          |

**Descrição**

Como Orientador, Professor da Disciplina, Secretaria ou Coordenador de
Curso quero cadastrar e alterar Membros Externos para que possam acessar
às bancas.

**Atores**

> **Ator principal:** Orientador, Professor da Disciplina, Secretaria ou
> Coordenador de Curso.
>
> **Atores secundários:** Membro Externo (avaliador de fora do NUCOMP ou
> da UEA), que ativa a conta pelo primeiro acesso (US-10); composição da
> banca (US-23), de onde parte o cadastro pelo atalho; regra de validade
> do acesso (US-06).

**Pré-condições**

1.  O usuário está autenticado (US-11) com um dos perfis acima e com a
    > conta ativa.

2.  Para cadastrar pelo atalho, o usuário está compondo uma banca
    > (US-23) e o avaliador externo desejado não aparece na lista.

3.  Para alterar dados, o Membro Externo já está cadastrado.

**Fluxo principal**

1.  O usuário acessa o menu “Membros externos” e clica em “Novo membro
    > externo”.

2.  O sistema exibe o formulário com Nome Completo, E-mail, Titulação e
    > Instituição de Origem.

3.  O usuário preenche os campos e clica em “Salvar”.

4.  O sistema valida os campos obrigatórios, os formatos e a unicidade
    > do e-mail.

5.  O sistema cria a conta com o Status da Conta “Aguardando Ativação”,
    > exibe “Membro externo cadastrado com sucesso” e o inclui na lista
    > de avaliadores disponíveis para a banca.

6.  O membro externo define a senha pelo primeiro acesso (US-10). A
    > validade do acesso segue a US-06, inclusive enquanto ele ainda não
    > tem banca vinculada.

**Fluxos alternativos**

**A1. Cadastro pelo atalho da banca (DEF-02.3).** (1) Ao compor a banca
(US-23), o usuário não encontra o avaliador e o sistema orienta a
cadastrá-lo. (2) O usuário clica em “Cadastrar membro externo”. (3) O
sistema abre o mesmo formulário. (4) O usuário preenche e salva. (5) O
sistema valida, cria a conta e volta à banca com o novo membro já
selecionado.

**A2. Alteração dos dados (CAD-03.2).** (1) O usuário abre a lista de
membros externos e clica em “Editar”. (2) O sistema exibe Nome Completo,
E-mail, Titulação e Instituição de Origem preenchidos. (3) O usuário
altera e clica em “Salvar”. (4) O sistema repete as validações do
cadastro e exibe “Dados atualizados”.

**A3. Alteração do e-mail.** O novo e-mail passa a ser o login. A senha
já definida é mantida, e o histórico do membro continua ligado à mesma
conta.

**A4. E-mail de qualquer domínio (CAD-03.1).** O sistema aceita e-mails
como ana@ufam.edu.br, carlos@empresa.com.br ou joao@gmail.com, sem
exigir @uea.edu.br.

**A5. Cadastro sem banca vinculada.** O membro pode ser cadastrado antes
de ser indicado a uma banca. A conta fica válida por 30 dias corridos a
partir do cadastro (US-06, fluxo H). Ao ser vinculado a uma banca, passa
a valer a regra da defesa mais distante mais 7 dias.

**A6. Alteração de membro com conta expirada.** A alteração é permitida.
Ela não reativa o acesso, que só volta com nova banca ou prorrogação
(US-06).

**A7. Cancelamento.** Se o usuário clicar em “Cancelar” no cadastro ou
na alteração, o sistema descarta o preenchimento. No atalho da banca,
volta à composição sem novo membro.

**Fluxos de exceção**

**E1. E-mail já cadastrado (CAD-03.1).** O e-mail é único no sistema,
para todos os perfis, inclusive contas expiradas. O sistema exibe “Este
e-mail já está cadastrado” e não salva. Se for um membro com conta
expirada, o usuário deve selecioná-lo na banca ou prorrogá-lo (US-06).

**E2. E-mail em formato inválido.** Sem arroba, sem domínio ou com mais
de 100 caracteres. O sistema exibe “Informe um e-mail válido” e não
salva.

**E3. Campo obrigatório vazio.** Nome, E-mail, Titulação ou Instituição
de Origem. O sistema destaca o campo com “Campo obrigatório” e não
salva. Retorna ao passo 3.

**E4. Nome inválido (CAD-03.1).** Nome com números ou símbolos, ou com
mais de 150 caracteres. O sistema exibe “O nome deve conter apenas
letras e até 150 caracteres” e não salva.

**E5. Instituição de Origem fora da regra (CAD-03.1).** Texto com mais
de 150 caracteres ou com caracteres que não sejam letras, números,
espaços e pontuação. O sistema exibe “Informe a instituição com até 150
caracteres” e não salva.

**E6. Titulação fora da lista (CAD-03.1).** Valor diferente de
Especialista, Mestre ou Doutor. O sistema rejeita com “Selecione uma
opção válida”.

**E7. Usuário sem permissão.** Aluno, Docente sem papel de Orientador,
Professor da Disciplina ou Coordenador, e o próprio Membro Externo não
veem o menu “Membros externos”. O acesso direto é bloqueado com “Você
não tem permissão para esta ação”.

**E8. Alteração inválida (CAD-03.2).** Na alteração valem as mesmas
exceções E1 a E6. O sistema não grava e mantém os dados anteriores.

**E9. Falha ao gravar.** O sistema exibe “Não foi possível salvar. Tente
novamente”, não grava e mantém o preenchimento.

**Pós-condições**

- A conta do Membro Externo existe com o Status da Conta “Aguardando
  > Ativação”, sem senha até o primeiro acesso.

- O membro aparece na lista de Membros externos e na lista de
  > avaliadores da composição da banca (1º Avaliador, 2º Avaliador e
  > Suplente).

- O e-mail é o login e fica reservado, não pode ser usado por outro
  > cadastro.

- A validade do acesso está definida: 30 dias a partir do cadastro, ou a
  > regra da defesa se já houver banca (US-06).

- Após alteração, os novos dados estão gravados e valem nas bancas e
  > relatórios.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                                                        | **Resumo da regra em uma frase**                                                                                                                                                          |
|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-03.1** | O sistema deve mostrar um formulário de cadastro do Membro Externo (avaliador de fora do NUCOMP ou da UEA) que deve conter os campos Nome Completo, E-mail, Titulação e Instituição de Origem. | Formulário do Membro Externo com Nome Completo, E-mail de qualquer domínio (único), Titulação e Instituição de Origem; ao salvar, a conta fica com o Status da Conta Aguardando Ativação. |
| **CAD-03.2** | O sistema deve permitir a alteração de Nome Completo, E-mail, Titulação e Instituição de Origem do Membro Externo.                                                                             | O Orientador, o Professor da Disciplina, a Secretaria ou o Coordenador pode alterar os dados do Membro Externo, com as mesmas regras de formato do cadastro.                              |

**Critérios de aceite**

***Critérios do backlog:***

1.  **Aceita qualquer domínio de e-mail.**

2.  **Exige Nome, Titulação e Instituição de Origem.**

**Cenário 1: Cadastro com sucesso (fluxo principal)** Dado que o
Orientador está autenticado e o e-mail ana@ufam.edu.br não existe Quando
informa Nome, E-mail, Titulação Doutor e Instituição de Origem e clica
em “Salvar” Então o sistema cria a conta com o Status da Conta
“Aguardando Ativação” e exibe “Membro externo cadastrado com sucesso”

**Cenário 2: Cadastro por cada perfil permitido (CAD-03.1**) Dado que o
Professor da Disciplina, a Secretaria ou o Coordenador de Curso está
autenticado Quando cadastra um Membro Externo com dados válidos Então o
sistema cria a conta com o Status da Conta “Aguardando Ativação”

**Cenário 3: E-mail de qualquer domínio (A4, critério 1)** Dado que o
usuário está no formulário de Membro Externo Quando informa o e-mail
carlos@empresa.com.br e preenche os demais campos Então o sistema aceita
o e-mail e cadastra o membro

**Cenário 4: E-mail duplicado (E1)** Dado que já existe um usuário com o
e-mail luisa@ufam.edu.br Quando o usuário tenta cadastrar outro membro
com esse e-mail Então o sistema não salva e exibe “Este e-mail já está
cadastrado”

**Cenário 5: E-mail de membro com conta expirada (E1)** Dado que o
membro luisa@ufam.edu.br tem a conta expirada Quando o usuário tenta
cadastrá-lo de novo Então o sistema exibe “Este e-mail já está
cadastrado” e o usuário deve selecioná-lo na banca ou prorrogar o acesso
(US-06)

**Cenário 6: E-mail em formato inválido (E2)** Dado que o usuário está
no formulário de Membro Externo Quando informa “ana.ufam.edu.br” e clica
em “Salvar” Então o sistema exibe “Informe um e-mail válido” e não salva

**Cenário 7: E-mail com mais de 100 caracteres (E2)** Dado que o usuário
está no formulário de Membro Externo Quando informa um e-mail com 101
caracteres Então o sistema exibe “Informe um e-mail válido” e não salva

**Cenário 8: Instituição de Origem vazia (E3, critério 2)** Dado que o
usuário está no formulário de Membro Externo Quando clica em “Salvar”
sem informar a Instituição de Origem Então o sistema destaca o campo com
“Campo obrigatório” e não salva

**Cenário 9: Nome ou Titulação vazios (E3, critério 2)** Dado que o
usuário está no formulário de Membro Externo Quando deixa o Nome ou a
Titulação em branco e clica em “Salvar” Então o sistema destaca o campo
com “Campo obrigatório” e não salva

**Cenário 10: Nome fora da regra (E4**) Dado que o usuário está no
formulário de Membro Externo Quando informa o nome “Ana Souza 2” e clica
em “Salvar” Então o sistema exibe “O nome deve conter apenas letras e
até 150 caracteres” e não salva

**Cenário 11: Instituição com números e pontuação (CAD-03.1)** Dado que
o usuário está no formulário de Membro Externo Quando informa a
instituição “Univ. Federal do Amazonas (UFAM) - Campus 2” Então o
sistema aceita o texto e salva

**Cenário 12: Instituição acima de 150 caracteres (E5)** Dado que o
usuário está no formulário de Membro Externo Quando informa uma
instituição com 151 caracteres Então o sistema exibe “Informe a
instituição com até 150 caracteres” e não salva

**Cenário 13: Titulação fora da lista (E6)** Dado que o usuário está no
formulário de Membro Externo Quando a requisição envia a Titulação
“Livre-docente” Então o sistema rejeita com “Selecione uma opção válida”
e não salva

**Cenário 14: Cadastro pelo atalho da banca (A1, DEF-02.3)** Dado que o
usuário está compondo a banca (US-23) e o avaliador não está na lista
Quando cadastra o membro externo pelo atalho e salva Então o sistema
volta à banca com o novo membro selecionado

**Cenário 15: Cancelamento no atalho (A7)** Dado que o usuário abriu o
cadastro pelo atalho da banca Quando clica em “Cancelar” Então o sistema
volta à composição da banca sem criar conta

**Cenário 16: Alteração de dados (A2, CAD-03.2)** Dado que o Membro
Externo já está cadastrado Quando o Orientador corrige a Titulação e
salva Então o sistema grava e exibe “Dados atualizados”

**Cenário 17: Alteração do e-mail (A3)** Dado que o membro já ativou a
conta Quando a Secretaria altera o e-mail para novo@ufam.edu.br e salva
Então o novo e-mail passa a ser o login e a senha existente continua
valendo

**Cenário 18: Alteração com e-mail duplicado ou dado inválido (E8)**
Dado que o usuário abriu a edição de um membro Quando informa um e-mail
já usado por outro usuário ou um nome com números Então o sistema não
grava e mantém os dados anteriores

**Cenário 19: Alteração de membro expirado (A6)** Dado que a conta do
membro está expirada Quando o Coordenador corrige a Instituição de
Origem e salva Então o sistema grava a alteração e o acesso continua
bloqueado

**Cenário 20: Cadastro sem banca (A5)** Dado que o membro foi cadastrado
em 01/10/2026 e não está em nenhuma banca Quando o sistema define a
validade do acesso Então a conta vale até 31/10/2026

**Cenário 21: Aluno sem permissão (E7)** Dado que um Aluno está
autenticado Quando tenta acessar a tela de membros externos Então o
sistema nega o acesso e exibe “Você não tem permissão para esta ação”

**Cenário 22: Docente comum sem permissão (E7)** Dado que um Docente sem
papel de Orientador, Professor da Disciplina ou Coordenador está
autenticado Quando abre o menu lateral Então o sistema não exibe
“Membros externos” e bloqueia o acesso direto à tela

**Cenário 23: Falha ao gravar (E9)** Dado que o usuário preencheu o
formulário corretamente Quando o sistema não consegue gravar Então exibe
“Não foi possível salvar. Tente novamente” e mantém os dados no
formulário

**Tela no protótipo**

**Tela:** Cadastros (Membros externos)



**Tela:** Cadastrar (Membros externos)



**Diagrama de sequência**

**Diagrama relacionado:** \[nome do diagrama ou "sem diagrama próprio" e
o motivo\]

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: )

## US-06 Expirar o acesso de membros externos

| **Épico:**                | Cadastro e Manutenção |
|---------------------------|-----------------------|
| **Feature:**              | Gestão de Contas      |
| **Requisitos da matriz:** | RBN-CAD-03.3          |
| **Prioridade (MoSCoW):**  | Must Have             |
| **Responsável:**          | Maria Luísa Gomes     |

**Descrição**

Como Sistema, quero expirar o acesso de Membros Externos após 7 dias da
defesa para que a segurança seja mantida. O sistema também renova o
acesso automaticamente quando o membro é vinculado a uma nova banca ou a
defesa é reagendada.

**Atores**

> **Ator principal: Sistema, que calcula a validade e muda o Status da
> Conta.**
>
> **Atores secundários:** módulo de bancas (US-21, US-23 e US-24:
> vínculo, reagendamento e cancelamento da sessão); login (US-11);
> Membro Externo; cadastro do membro (US-05); prorrogação manual
> (US-50).

**Pré-condições**

- O Membro Externo está cadastrado (US-05).

- Para a validade da defesa, o membro está vinculado a uma banca (US-23)
  > com sessão que não esteja Cancelada.

**Fluxo principal**

1.  O membro externo é vinculado a uma banca com sessão Agendada, e o
    > sistema calcula a validade do acesso: data da defesa mais distante
    > em que ele esteja vinculado, mais 7 dias corridos.

2.  O membro externo faz login normalmente até a data de validade.

3.  Passada a validade, o membro tenta fazer login.

4.  O sistema muda o Status da Conta para Expirada, nega o acesso
    > (US-11) e exibe "Seu acesso expirou. Procure a coordenação do
    > curso".

5.  O sistema mantém Nome, E-mail, Titulação e Instituição de Origem no
    > histórico, e as bancas e notas dele continuam nos relatórios.

6.  Para reabrir o acesso, ocorre uma prorrogação automática (A1 e A2)
    > ou a prorrogação manual (US-50).

**Fluxos alternativos**

A1. Nova banca (CAD-03.3). O membro é vinculado a uma nova banca, no
mesmo semestre ou em outro. O sistema volta o Status da Conta para Ativa
ou estende a validade até 7 dias corridos após a nova data de defesa,
sem novo cadastro. Se a nova defesa for mais distante, ela passa a
definir a validade.

A2. Defesa reagendada (CAD-03.3). Com a sessão Reagendada, o sistema
recalcula a validade para 7 dias corridos após a nova data, seja ela
anterior ou posterior à data antiga.

A3. Sessão cancelada. O sistema ignora sessões Canceladas no cálculo da
validade. Se não restar nenhuma sessão válida, a conta expira 7 dias
corridos após a data do cancelamento.

A4. Defesa mais distante. Se o membro participa de duas ou mais bancas,
o sistema usa a data da defesa mais distante, e não a primeira.

A5. Membro sem banca. Enquanto o membro não estiver vinculado a nenhuma
banca, a conta fica válida por 30 dias corridos a partir do cadastro
(US-05). Ao ser vinculado, passa a valer a regra da defesa mais 7 dias.

A6. Defesa realizada. Com a sessão Realizada, a validade continua sendo
a data da defesa mais 7 dias corridos, sem mudança.

A7. Membro retirado da banca antes da sessão (DEF-02.10). O sistema
recalcula a validade sem essa sessão (a confirmar o prazo quando não
restar nenhuma banca).

**Fluxos de exceção**

**E1. Login com conta expirada.** O sistema nega o acesso e exibe “Seu
acesso expirou. Procure a coordenação do curso”, orientando o contato
com o Orientador, o Professor da Disciplina, a Secretaria ou o
Coordenador. O acesso volta com nova banca, reagendamento ou prorrogação
manual (US-50).

**E2. Falha ao recalcular a validade.** O sistema mantém a validade
anterior, registra o erro e tenta de novo na próxima atualização da
banca.

**Pós-condições**

- A validade do acesso do membro está gravada e vale até o fim do dia da
  > data de validade.

- Passada a validade, o Status da Conta fica Expirada e o login é
  > bloqueado, mas os dados cadastrais e as participações em bancas
  > continuam no histórico e nos relatórios.

- Com nova banca, reagendamento ou prorrogação, o Status volta a Ativa e
  > o membro entra com o mesmo login e a mesma senha.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                                                                                       | **Resumo da regra em uma frase**                                                                                                                                                                                                                                                                |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-03.3** | O sistema deve permitir a manutenção do Status da Conta do Membro Externo, com os valores Aguardando Ativação, Ativa ou Expirada, expirando o acesso 7 dias após a defesa e permitindo a renovação ou a prorrogação da conta. | O Status da Conta fica Ativa até 7 dias corridos após a defesa mais distante (sessões Canceladas não contam) e depois Expirada, sem apagar os dados do histórico; nova banca ou reagendamento renovam o acesso automaticamente, com o mesmo login e senha. A prorrogação manual está na US-50.. |

**Critérios de aceite**

*Critérios do backlog:*

> 1\. Bloqueia login 7 dias após a data da defesa.
>
> 2\. Permite prorrogação manual (US-50) ou automática se vinculado a
> nova banca.

**Cenário 1: Validade calculada (fluxo principal, critério 1)**

**Dado** que o membro externo está vinculado a uma defesa Agendada para
20/10/2026

**Quando** o sistema calcula a validade do acesso

**Então** a conta fica ativa até 27/10/2026

**Cenário 2: Login no último dia da validade**

**Dado** que a validade do membro termina em 27/10/2026

**Quando** ele faz login em 27/10/2026 com e-mail e senha corretos

**Então** o sistema permite o acesso

**Cenário 3: Login bloqueado após a validade (E1, critério 1)**

**Dado** que a validade do membro externo terminou em 27/10/2026

**Quando** ele tenta fazer login em 28/10/2026 com e-mail e senha
corretos

**Então** o Status da Conta passa a Expirada, o sistema nega o acesso e
exibe “Seu acesso expirou. Procure a coordenação do curso”

**Cenário 4: Dados mantidos no histórico**

**Dado** que a conta do membro externo expirou

**Quando** a Coordenação consulta bancas e relatórios do período

**Então** os dados cadastrais e a participação do membro continuam
visíveis

**Cenário 5: Defesa mais distante (A4)**

**Dado** que o membro tem defesas Agendadas em 20/10/2026 e 05/11/2026

**Quando** o sistema calcula a validade

**Então** a conta vale até 12/11/2026, contada da defesa mais distante

**Cenário 6: Sessão cancelada não conta (A3)**

**Dado** que o membro tem uma defesa Cancelada em 25/10/2026 e outra
Agendada em 15/10/2026

**Quando** o sistema calcula a validade

**Então** a conta vale até 22/10/2026

**Cenário 7: Única defesa cancelada (A3)**

**Dado** que a única defesa do membro, marcada para 20/10/2026, foi
cancelada em 12/10/2026

**Quando o sistema recalcula a validade**

**Então** a conta vale até 19/10/2026

**Cenário 8: Renovação automática por nova banca (A1, critério 2)**

**Dado** que o Status da Conta do membro externo é Expirada

**Quando** ele é vinculado a uma nova banca com defesa em 10/11/2026

**Então** o Status volta a Ativa até 17/11/2026, sem novo cadastro

**Cenário 9: Nova banca mais distante estende a validade (A1)**

**Dado** que a conta do membro vale até 27/10/2026

**Quando** ele é vinculado a uma nova banca com defesa em 05/11/2026

**Então** a validade passa para 12/11/2026

**Cenário 10: Reagendamento para data posterior (A2)**

**Dado** que a defesa do membro foi reagendada de 20/10/2026 para
03/11/2026

**Quando** o sistema recebe o reagendamento

**Então** a validade passa para 10/11/2026

**Cenário 11: Reagendamento para data anterior (A2)**

**Dado** que a defesa do membro foi reagendada de 20/10/2026 para
15/10/2026

**Quando** o sistema recebe o reagendamento

**Então** a validade passa para 22/10/2026

**Cenário 12: Membro sem banca fora do prazo (A5)**

**Dado** que o membro externo foi cadastrado em 01/10/2026 e não está em
nenhuma banca

**Quando** tenta fazer login em 05/11/2026

**Então** o sistema nega o acesso, porque a validade de 30 dias terminou
em 31/10/2026

**Cenário 13: Membro sem banca dentro do prazo (A5)**

**Dado** que o membro foi cadastrado em 01/10/2026 e não está em nenhuma
banca

**Quando** faz login em 10/10/2026

**Então** o sistema permite o acesso

**Cenário 14: Vínculo posterior à banca substitui os 30 dias (A5)**

**Dado** que o membro foi cadastrado em 01/10/2026 e vinculado em
20/10/2026 a uma defesa de 10/11/2026

**Quando** o sistema recalcula a validade

**Então** a conta vale até 17/11/2026

**Cenário 15: Defesa realizada (A6)**

**Dado** que a defesa do membro foi Realizada em 20/10/2026

**Quando** o sistema mantém a validade

**Então** a conta continua valendo até 27/10/2026

**Cenário 16: Mesmo login e mesma senha após a renovação (E1)**

**Dado** que o acesso do membro foi renovado por nova banca

**Quando** ele faz login com o e-mail e a senha de antes

**Então** o sistema permite o acesso sem novo cadastro

**Cenário 17: Membro retirado da banca (A7, a confirmar)**

**Dado** que o membro foi removido de uma banca Agendada antes da sessão

**Quando** o sistema recalcula a validade

**Então** a validade deixa de considerar essa sessão

**Cenário 18: Falha ao recalcular (E2)**

**Dado** que uma banca do membro foi reagendada

**Quando** o sistema não consegue recalcular a validade

**Então** mantém a validade anterior e registra o erro

**Tela no protótipo**

**Tela:Cadastro (** Membros externos)



**Diagrama de sequência**

**Diagrama relacionado:** \[nome do diagrama ou "sem diagrama próprio" e
o motivo\]

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[\] Revisada por outra pessoa (nome: )

## US-39 Filtrar listas e relatórios por curso

| **Épico:**                | Cadastro e Manutenção |
|---------------------------|-----------------------|
| **Feature:**              | Acesso e Login        |
| **Requisitos da matriz:** | RBN-CAD-14.1          |
| **Prioridade (MoSCoW):**  | Must Have             |
| **Responsável:**          | Maria Luísa Gomes     |

**Descrição**

Como Coordenação ou Secretaria, quero ver listas, painéis e relatórios
filtrados pelo meu curso para que eu acompanhe o que é da minha
responsabilidade.

**Atores**

> **Ator principal:** Coordenador de Curso ou Secretaria.
>
> **Atores secundários:** Telas de listas, painéis e relatórios do
> sistema (docentes, turmas, defesas, relatórios, aproveitamento de
> artigos).

**Pré-condições**

- O usuário está autenticado (US-11) como Coordenador de Curso ou
  > Secretaria.

- O usuário tem um curso associado: Curso Coordenado (Coordenador) ou
  > Curso Vinculado (Secretaria).

- A lista, o painel ou o relatório está aberto.

**Fluxo principal**

1.  O Coordenador de Curso ou a Secretaria abre uma lista, painel ou
    > relatório.

2.  O sistema exibe o filtro de Curso já preenchido com o Curso
    > Coordenado do Coordenador ou o Curso Vinculado da Secretaria.

3.  O sistema mostra apenas os registros desse curso.

4.  O usuário escolhe outra opção no filtro (outro curso ou “Todos”).

5.  O sistema atualiza a tela em menos de 2 segundos com os registros da
    > opção escolhida.

6.  Ao abrir outra tela, o filtro volta a vir preenchido com o curso do
    > usuário.

**Fluxos alternativos**

**A1. Troca para outro curso específico.** O usuário escolhe Engenharia
de Computação, Sistemas de Informação ou Licenciatura em Computação, e o
sistema mostra só os registros desse curso.

**A2. Troca para “Todos”.** O sistema mostra os registros dos três
cursos.

**A3. Volta ao curso do usuário.** O usuário escolhe de novo o próprio
curso, e o sistema mostra os registros dele.

**A4. Filtro combinado com outros filtros da tela.** O filtro de Curso
soma-se aos filtros da própria tela (por exemplo, período, docente ou
abrangência), e o sistema mostra só os registros que atendem a todos.

**A5. Painéis e relatórios.** A mesma regra vale para painéis e
relatórios, que também abrem filtrados pelo curso do usuário.

**A6. Troca vale só para a tela aberta.** A escolha do filtro não é
guardada para as demais telas.

**A7. Lista com registros de vários cursos.** Com “Todos” ou outro
curso, as ações continuam disponíveis só nos registros do próprio curso
do usuário.

**Fluxos de exceção**

**E1. Ação em registro de outro curso.** Ao ver registros de outro
curso, o usuário não consegue cadastrar, alterar, inativar, transferir
nem homologar. Os botões de ação ficam indisponíveis.

**E2. Acesso direto a registro de outro curso.** Se o usuário tentar a
ação por link direto, o sistema exibe “Você só pode alterar dados do seu
curso” e não executa.

**E3. Nenhum registro.** Se o curso escolhido não tiver registros, o
sistema exibe “Nenhum registro”.

**E4. Perfil sem o filtro.** Aluno, Docente comum e Membro Externo não
veem o filtro, e cada um vê apenas os próprios dados.

**E5. Atualização lenta ou com falha.** Se a atualização passar de 2
segundos, o sistema mostra um indicador de carregamento. Se falhar,
exibe “Não foi possível atualizar. Tente novamente” e mantém a lista
anterior.

**Pós-condições**

- A tela mostra somente os registros da opção escolhida no filtro de
  > Curso.

- O filtro volta a vir com o curso do usuário ao abrir outra tela.

- Nenhum dado é alterado pelo filtro.

- As ações de cadastro, alteração, inativação, transferência e
  > homologação continuam restritas ao curso do usuário.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                             | **Resumo da regra em uma frase**                                                                                                                                                                                                                                                                                                                |
|--------------|-----------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-14.1** | O sistema deve aplicar o filtro de Curso nas visualizações do Coordenador de Curso e da Secretaria. | Toda lista, painel e relatório do Coordenador e da Secretaria tem o filtro de Curso (Engenharia de Computação, Sistemas de Informação, Licenciatura em Computação ou Todos), que vem preenchido com o curso do usuário, pode ser trocado só na tela aberta e afeta apenas a visualização, e não as ações, que ficam restritas ao próprio curso. |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Filtro de Curso (Engenharia de Computação, Sistemas de Informação,
> Licenciatura em Computação ou Todos).
>
> 2\. Vem preenchido com o curso do usuário logado e pode ser trocado na
> tela aberta.

**Cenário 1: Filtro da Secretaria (fluxo principal, critério 2)**

Dado que a Secretaria do curso Sistemas de Informação está autenticada

Quando abre a listagem de docentes

Então o filtro de Curso vem com Sistemas de Informação e a lista mostra
apenas docentes desse curso

**Cenário 2: Filtro do Coordenador (critério 2)**

Dado que o Coordenador de Engenharia de Computação está autenticado

Quando abre o relatório de turmas

Então o filtro de Curso vem com Engenharia de Computação

**Cenário 3: Opções do filtro (critério 1)**

Dado que o usuário abriu uma lista

Quando abre o filtro de Curso

Então o sistema oferece Engenharia de Computação, Sistemas de
Informação, Licenciatura em Computação e Todos, com uma única escolha

**Cenário 4: Troca para outro curso (A1)**

Dado que a lista está filtrada pelo curso do usuário

Quando escolhe Licenciatura em Computação

Então o sistema mostra só os registros desse curso

**Cenário 5: Troca para Todos (A2)**

Dado que o usuário está em uma lista com o filtro no seu curso

Quando escolhe “Todos”

Então o sistema atualiza a lista em menos de 2 segundos com os registros
dos três cursos

**Cenário 6: Volta ao curso do usuário (A3)**

Dado que o filtro está em “Todos”

Quando o usuário escolhe o próprio curso

Então o sistema mostra só os registros dele

**Cenário 7: Troca vale só para a tela aberta (A6)**

Dado que o usuário trocou o filtro para Licenciatura em Computação em
uma tela

Quando abre outra tela

Então o filtro vem com o curso do próprio usuário

**Cenário 8: Filtro em painel e relatório (A5)**

Dado que o Coordenador abre o painel de atividades por docente e o
relatório de produção de TCCs

Quando as telas carregam

Então cada uma vem filtrada pelo curso do Coordenador

**Cenário 9: Filtro combinado com o período (A4)**

Dado que o usuário filtrou o relatório pelo período letivo 2026/2

Quando escolhe o curso Sistemas de Informação

Então o sistema mostra só os registros de Sistemas de Informação nesse
período

**Cenário 10: Ação restrita ao próprio curso (E1)**

Dado que o usuário está vendo docentes de outro curso pelo filtro

Quando tenta inativar um desses docentes

Então o sistema não exibe o botão e não permite a ação

**Cenário 11: Acesso direto à ação em outro curso (E2)**

Dado que o usuário conhece o link de uma ação em registro de outro curso

Quando abre o link

Então o sistema exibe “Você só pode alterar dados do seu curso” e não
executa

**Cenário 12: Lista mista com “Todos” (A7)**

Dado que o filtro está em “Todos”

Quando a lista mostra registros dos três cursos

Então os botões de ação aparecem só nos registros do curso do usuário

**Cenário 13: Sem registros (E3)**

Dado que o curso escolhido não tem registros na tela aberta

Quando o sistema aplica o filtro

Então exibe “Nenhum registro”

**Cenário 14: Perfil sem filtro (E4)**

Dado que um Aluno, um Docente comum ou um Membro Externo está
autenticado

Quando abre uma tela com dados do curso

Então o sistema não exibe o filtro de Curso e mostra só os dados
próprios

**Cenário 15: Lentidão na atualização (E5)**

Dado que a atualização demora mais de 2 segundos

Quando o usuário escolhe uma opção no filtro

Então o sistema mostra um indicador de carregamento até concluir

**Cenário 16: Falha na atualização (E5)**

Dado que o usuário escolheu uma opção no filtro

Quando o sistema não consegue carregar os registros

Então exibe “Não foi possível atualizar. Tente novamente” e mantém a
lista anterior

**Tela no protótipo**

**Tela:** Relatórios (filtrado por Curso)

**Diagrama de sequência**

**Diagrama relacionado:** \[nome do diagrama ou "sem diagrama próprio" e
o motivo\]

**Link:** \[link do diagrama no Astah ou na pasta do projeto\]

**Pronta para desenvolver**

> \[ \] Descrição no formato Como, Quero, Para que
>
> \[ \] Requisitos da matriz conferidos
>
> \[ \] Fluxo principal e fluxos alternativos escritos
>
> \[ \] Atores, pré-condições e pós-condições preenchidos
>
> \[ \] Fluxos de exceção escritos
>
> \[ \] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

# Maria Luiza Nobre: Relatórios

## US-31 Consultar e exportar o painel de atividades por docente

| **Épico:**                | Relatórios e Informações Gerenciais |
|---------------------------|-------------------------------------|
| **Feature:**              | Dashboards de Produção              |
| **Requisitos da matriz:** | RBN-REL-01.1                        |
| **Prioridade (MoSCoW):**  | Must Have                           |
| **Responsável:**          | Maria Luiza Nobre                   |

**Descrição**

Como Docente, quero consultar e exportar o meu painel de atividades, com
orientações, coorientações e participações em banca no período, para
comprovar as minhas atividades.

**Atores**

> **Ator principal:** Docente do NUCOMP.
>
> **Atores secundários:** Coordenador de Curso e Secretaria, que
> consultam o painel de qualquer docente (fluxo alternativo C).

**Pré-condições**

- O usuário está autenticado, com o Status da Conta Ativa (US-11). Sem
  > sessão ativa, aplica-se o E1.

- O usuário tem o perfil Docente, Coordenador de Curso ou Secretaria;
  > para o perfil Aluno, aplica-se o E4.

**Fluxo principal**

> 1\. No menu lateral do sistema, na área Gestão, o Docente seleciona o
> item Relatórios.
>
> 2\. O sistema abre a tela Relatórios, com a lista de relatórios
> disponíveis ao perfil, e o Docente seleciona Painel de atividades por
> docente.
>
> 3\. O sistema exibe o painel com os filtros Período (lista: Período
> Letivo, Esta Semana, Este Mês ou Próximos 30 Dias), Ano/Semestre, Data
> Inicial e Data Final (DD/MM/AAAA, por calendário), preenchidos por
> padrão com o período letivo atual, e os botões PDF, CSV e XLSX. Para o
> docente comum, os filtros Docente e Curso não aparecem.
>
> 4\. O Docente seleciona o atalho Período Letivo no filtro Período e o
> semestre desejado no filtro Ano/Semestre.
>
> 5\. O sistema atualiza a pré-visualização, somente leitura, com uma
> única linha referente ao próprio Docente e as colunas Docente, Curso
> (Curso de Lotação), Quantidade de Orientandos em TCC 1, Quantidade de
> Orientandos em TCC 2, Quantidade de Coorientações (aceitas) e Total de
> Bancas no período (sessões Realizadas em que atuou como Presidente, 1º
> Avaliador, 2º Avaliador ou Suplente acionado). As orientações contam
> pelas turmas do período.
>
> 6\. O Docente aciona a seta ao lado do seu nome para expandir a linha.
>
> 7\. O sistema exibe duas sub-listas: Orientações e coorientações, com
> Nome do Aluno, Título do Trabalho, Papel (Orientador ou Coorientador)
> e Status do TCC, e Bancas, com Data, Papel na banca, Nome do Aluno e
> Título do Trabalho.
>
> 8\. O Docente aciona o botão PDF, CSV ou XLSX, no canto superior
> direito do relatório.
>
> 9\. O sistema gera o arquivo no formato escolhido, com os dados, as
> sub-listas e os filtros exibidos em tela, disponibiliza o arquivo para
> download e mantém o Docente na tela do painel. O fluxo termina.

**Fluxos alternativos**

> A. Período informado por datas (passo 4): o Docente informa Data
> Inicial e Data Final no calendário (DD/MM/AAAA), e o sistema considera
> o intervalo informado. O fluxo prossegue a partir do passo 5.
>
> B. Atalho Esta Semana, Este Mês ou Próximos 30 Dias (passo 4): o
> sistema preenche automaticamente Data Inicial e Data Final com as
> datas do atalho. O fluxo prossegue a partir do passo 5.
>
> C. Consulta pelo Coordenador de Curso ou pela Secretaria (passo 3): o
> painel exibe também o filtro Docente (lista com "Todos" e cada docente
> do NUCOMP; padrão "Todos") e o filtro Curso (lista: Engenharia de
> Computação, Sistemas de Informação, Licenciatura em Computação ou
> Todos), preenchido por padrão com o curso do usuário (US-39). A
> pré-visualização exibe uma linha por docente do filtro, e cada linha
> pode ser expandida como no passo 6. O fluxo prossegue a partir do
> passo 4.
>
> D. Docente sem orientações ou coorientações no período (passo 7): a
> sub-lista Orientações e coorientações exibe "Nenhum registro". O fluxo
> prossegue a partir do passo 8.
>
> E. Docente sem bancas no período (passo 7): a sub-lista Bancas exibe
> "Nenhum registro", e o Total de Bancas é 0. O fluxo prossegue a partir
> do passo 8.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o usuário tente acessar a
> tela Relatórios sem sessão ativa (pelo menu, pelo endereço da página
> ou por um link recebido), o sistema apresenta a tela de login (US-11).
> Após a autenticação, o sistema exibe o Painel de atividades por
> docente, e o fluxo prossegue a partir do passo 3. Em caso de falha na
> autenticação, aplicam-se as exceções da US-11.
>
> E2. Intervalo de datas inválido (passo 5): a Data Inicial é posterior
> à Data Final. O sistema não atualiza a pré-visualização e exibe "A
> data inicial não pode ser superior à data final". Retorna ao passo 4.
>
> E3. Nenhum registro para os filtros (passo 5): a pré-visualização
> exibe a tabela vazia com a mensagem "Nenhum registro encontrado para
> os filtros selecionados", e os botões PDF, CSV e XLSX permanecem
> desabilitados. O fluxo termina.
>
> E4. Perfil Aluno (passo 1): o menu lateral do Aluno não exibe o item
> Relatórios. O fluxo termina.

**Pós-condições**

- Nenhum dado foi alterado: o painel é somente leitura.

- Na exportação, o arquivo foi gerado com os dados, as sub-listas e os
  > filtros exibidos em tela.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                 | **Resumo da regra em uma frase**                                                                                                                                                                                                                                                                             |
|--------------|-------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **REL-01.1** | O sistema deve emitir o painel de atividades por docente, reunindo orientações, coorientações e participações em banca. | Painel com uma linha por docente (orientandos em TCC 1 e em TCC 2, coorientações aceitas e bancas Realizadas no período), expansível em orientações e bancas; o docente comum vê apenas o próprio extrato, e o Coordenador de Curso e a Secretaria filtram por Docente e Curso; exporta em PDF, CSV ou XLSX. |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Lista de orientandos e suas participações em bancas.
>
> 2\. O Docente vê só o seu perfil; Coordenação e Secretaria veem todos
> e possuem um filtro em que podem selecionar "Todos" ou um docente
> específico.
>
> 3\. Exportação obrigatória e formatada para PDF, CSV e XLSX.

***Cenário 1: Docente consulta e exporta o próprio painel (fluxo
principal)***

> **Dado que** o Docente está autenticado e é orientador de 1 aluno em
> TCC 1 e de 1 aluno em TCC 2
>
> **Quando** abre o Painel de atividades por docente com o período
> letivo 2026/2, expande a linha e aciona o botão PDF
>
> **Então** o painel exibe apenas a linha do Docente, com Orientandos em
> TCC 1 igual a 1 e Orientandos em TCC 2 igual a 1, sem os filtros
> Docente e Curso
>
> **E** o navegador baixa o PDF com a linha e as sub-listas exibidas

***Cenário 2: período informado por datas (fluxo alternativo A)***

> **Dado que** o usuário está na tela do relatório
>
> **Quando** informa a Data Inicial 01/09/2026 e a Data Final 30/09/2026
> no calendário
>
> **Então** a pré-visualização considera apenas o intervalo informado

***Cenário 3: seleção por atalho de período (fluxo alternativo B)***

> **Dado que** o usuário está na tela do relatório
>
> **Quando** seleciona o atalho Este Mês no filtro Período
>
> **Então** o sistema preenche Data Inicial e Data Final com o primeiro
> e o último dia do mês e atualiza a pré-visualização

***Cenário 4: Coordenador de Curso consulta todos os docentes (fluxo
alternativo C)***

> **Dado que** o Coordenador de Curso de Sistemas de Informação está
> autenticado
>
> **Quando** abre o Painel de atividades por docente
>
> **Então** o painel exibe os filtros Docente, com "Todos", e Curso, com
> Sistemas de Informação, e uma linha por docente

***Cenário 5: Secretaria filtra um docente específico (fluxo alternativo
C)***

> **Dado que** a Secretaria está no Painel de atividades por docente
>
> **Quando** seleciona um docente no filtro Docente
>
> **Então** a pré-visualização exibe apenas a linha desse docente

***Cenário 6: docente sem orientações (fluxo alternativo D)***

> **Dado que** o Docente não orienta nem coorienta nenhum aluno no
> período
>
> **Quando** expande a sua linha
>
> **Então** a sub-lista Orientações e coorientações exibe "Nenhum
> registro"

***Cenário 7: docente sem bancas (fluxo alternativo E)***

> **Dado que** o Docente não participou de nenhuma banca Realizada no
> período
>
> **Quando** expande a sua linha
>
> **Então** a sub-lista Bancas exibe "Nenhum registro" e o Total de
> Bancas é 0

***Cenário 8: acesso sem estar autenticado (E1)***

> **Dado que** o usuário não está autenticado
>
> **Quando** tenta abrir a tela Relatórios
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre o relatório Painel de atividades por docente

***Cenário 9: intervalo de datas inválido (E2)***

> **Dado que** o usuário está na tela do relatório
>
> **Quando** informa a Data Inicial 30/11/2026 e a Data Final 01/11/2026
>
> **Então** o sistema não atualiza a pré-visualização e exibe "A data
> inicial não pode ser superior à data final"

***Cenário 10: nenhum registro para os filtros (E3)***

> **Dado que** o Coordenador de Curso filtrou um curso sem docentes com
> atividade no período
>
> **Quando** o sistema atualiza a pré-visualização
>
> **Então** exibe a tabela vazia com a mensagem "Nenhum registro
> encontrado para os filtros selecionados"
>
> **E** os botões PDF, CSV e XLSX permanecem desabilitados

***Cenário 11: perfil Aluno (E4)***

> **Dado que** o usuário autenticado é Aluno
>
> **Quando** abre o menu lateral
>
> **Então** o item Relatórios não aparece

**Tela no protótipo**

**Tela:** Relatórios: Painel de atividades por docente



**Diagrama de sequência**

**Diagrama relacionado:** sem diagrama próprio: consulta de relatório
somente leitura, sem alteração de dados.

**Link:** não se aplica.

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[x\] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-47 Consultar e exportar o relatório de participação de Membros Externos

| **Épico:**                | Relatórios e Informações Gerenciais |
|---------------------------|-------------------------------------|
| **Feature:**              | Dashboards de Produção              |
| **Requisitos da matriz:** | RBN-REL-01.2                        |
| **Prioridade (MoSCoW):**  | Could Have                          |
| **Responsável:**          | Maria Luiza Nobre                   |

**Descrição**

Como Coordenador de Curso, quero consultar e exportar a participação de
docentes do NUCOMP e de Membros Externos nas bancas realizadas no
período, com as instituições de origem dos externos, para acompanhar a
composição das bancas do curso.

**Atores**

> **Ator principal:** Coordenador de Curso.
>
> **Atores secundários:** Secretaria, que consulta o relatório pelo
> mesmo fluxo (fluxo alternativo D).

**Pré-condições**

- O usuário está autenticado, com o Status da Conta Ativa (US-11). Sem
  > sessão ativa, aplica-se o E1.

- O usuário tem o perfil Coordenador de Curso ou Secretaria; caso
  > contrário, aplica-se o E4.

**Fluxo principal**

> 1\. No menu lateral do sistema, na área Gestão, o Coordenador de Curso
> seleciona o item Relatórios.
>
> 2\. O sistema abre a tela Relatórios, e o Coordenador seleciona
> Participação de Membros Externos.
>
> 3\. O sistema exibe o relatório com os filtros Período (lista: Período
> Letivo, Esta Semana, Este Mês ou Próximos 30 Dias), Ano/Semestre, Data
> Inicial e Data Final (DD/MM/AAAA, por calendário), preenchidos por
> padrão com o período letivo atual, o filtro Curso (lista: Engenharia
> de Computação, Sistemas de Informação, Licenciatura em Computação ou
> Todos), preenchido por padrão com o curso do usuário (US-39), e os
> botões PDF, CSV e XLSX.
>
> 4\. O Coordenador seleciona o atalho Período Letivo no filtro Período,
> o semestre no filtro Ano/Semestre e o curso no filtro Curso.
>
> 5\. O sistema atualiza a pré-visualização, somente leitura, com as
> colunas Descrição e Quantidade: uma linha com a quantidade de docentes
> do NUCOMP distintos e uma com a quantidade de Membros Externos
> distintos que atuaram como membros efetivos nas sessões Realizadas do
> período, e uma linha por instituição de origem dos Membros Externos,
> com a quantidade de membros de cada uma.
>
> 6\. O Coordenador aciona o botão PDF, CSV ou XLSX, no canto superior
> direito do relatório.
>
> 7\. O sistema gera o arquivo no formato escolhido, com os dados e os
> filtros exibidos em tela, disponibiliza o arquivo para download e
> mantém o Coordenador na tela do relatório. O fluxo termina.

**Fluxos alternativos**

> A. Período informado por datas (passo 4): o Coordenador informa Data
> Inicial e Data Final no calendário (DD/MM/AAAA). O fluxo prossegue a
> partir do passo 5.
>
> B. Atalho Esta Semana, Este Mês ou Próximos 30 Dias (passo 4): o
> sistema preenche automaticamente Data Inicial e Data Final com as
> datas do atalho. O fluxo prossegue a partir do passo 5.
>
> C. Curso Todos (passo 4): o Coordenador seleciona Todos no filtro
> Curso, e a pré-visualização considera as sessões de todos os cursos do
> NUCOMP. O fluxo prossegue a partir do passo 5.
>
> D. Consulta pela Secretaria (passo 1): a Secretaria segue os mesmos
> passos, com o filtro Curso preenchido por padrão com o seu Curso
> Vinculado. O fluxo prossegue a partir do passo 2.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o Coordenador de Curso ou
> a Secretaria tente acessar a tela Relatórios sem sessão ativa (pelo
> menu, pelo endereço da página ou por um link recebido), o sistema
> apresenta a tela de login (US-11). Após a autenticação, o sistema
> exibe o relatório Participação de Membros Externos, e o fluxo
> prossegue a partir do passo 3. Em caso de falha na autenticação,
> aplicam-se as exceções da US-11.
>
> E2. Intervalo de datas inválido (passo 5): a Data Inicial é posterior
> à Data Final. O sistema não atualiza a pré-visualização e exibe "A
> data inicial não pode ser superior à data final". Retorna ao passo 4.
>
> E3. Nenhum registro para os filtros (passo 5): a pré-visualização
> exibe a tabela vazia com a mensagem "Nenhum registro encontrado para
> os filtros selecionados", e os botões PDF, CSV e XLSX permanecem
> desabilitados. O fluxo termina.
>
> E4. Perfil sem acesso (passo 2): para o Docente que não é Coordenador
> de Curso, o item Participação de Membros Externos não aparece na lista
> de relatórios. O fluxo termina.

**Pós-condições**

- Nenhum dado foi alterado: o relatório é somente leitura.

- Na exportação, o arquivo foi gerado com os dados e os filtros exibidos
  > em tela.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                | **Resumo da regra em uma frase**                                                                                                                                                                                                                                                                              |
|--------------|------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **REL-01.2** | O sistema deve emitir o relatório de participação de Membros Externos. | Disponível ao Coordenador de Curso e à Secretaria: quantidade de pessoas distintas, entre docentes do NUCOMP e Membros Externos, que atuaram como membros efetivos nas sessões Realizadas do período, com as instituições de origem dos externos; filtros de período e de Curso; exporta em PDF, CSV ou XLSX. |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Relatório de membros externos acessível somente por Coordenadores
> e Secretários.
>
> 2\. Exportação obrigatória e formatada para PDF, CSV e XLSX.

***Cenário 1: Coordenador consulta e exporta a participação (fluxo
principal)***

> **Dado que** no período 2026/2 houve sessões Realizadas com 4 docentes
> do NUCOMP e 1 Membro Externo da Universidade Federal do Amazonas
>
> **Quando** o Coordenador de Curso abre o relatório com o período
> 2026/2 e aciona o botão XLSX
>
> **Então** a pré-visualização exibe Docentes do NUCOMP 4, Membros
> Externos 1 e Instituição de origem: Universidade Federal do Amazonas 1
>
> **E** o navegador baixa o arquivo XLSX com esses dados

***Cenário 2: período informado por datas (fluxo alternativo A)***

> **Dado que** o usuário está na tela do relatório
>
> **Quando** informa a Data Inicial 01/09/2026 e a Data Final 30/09/2026
> no calendário
>
> **Então** a pré-visualização considera apenas o intervalo informado

***Cenário 3: seleção por atalho de período (fluxo alternativo B)***

> **Dado que** o usuário está na tela do relatório
>
> **Quando** seleciona o atalho Este Mês no filtro Período
>
> **Então** o sistema preenche Data Inicial e Data Final com o primeiro
> e o último dia do mês e atualiza a pré-visualização

***Cenário 4: curso Todos (fluxo alternativo C)***

> **Dado que** o Coordenador está no relatório
>
> **Quando** seleciona Todos no filtro Curso
>
> **Então** a pré-visualização considera as sessões de todos os cursos
> do NUCOMP

***Cenário 5: consulta pela Secretaria (fluxo alternativo D)***

> **Dado que** a Secretaria de Engenharia de Computação está autenticada
>
> **Quando** abre o relatório Participação de Membros Externos
>
> **Então** o filtro Curso aparece preenchido com Engenharia de
> Computação

***Cenário 6: acesso sem estar autenticado (E1)***

> **Dado que** o usuário não está autenticado
>
> **Quando** tenta abrir a tela Relatórios
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre o relatório Participação de Membros Externos

***Cenário 7: intervalo de datas inválido (E2)***

> **Dado que** o usuário está na tela do relatório
>
> **Quando** informa a Data Inicial 30/11/2026 e a Data Final 01/11/2026
>
> **Então** o sistema não atualiza a pré-visualização e exibe "A data
> inicial não pode ser superior à data final"

***Cenário 8: nenhum registro para os filtros (E3)***

> **Dado que** não há dados para o período selecionado no relatório
> Participação de Membros Externos
>
> **Quando** o sistema atualiza a pré-visualização
>
> **Então** exibe a tabela vazia com a mensagem "Nenhum registro
> encontrado para os filtros selecionados"
>
> **E** os botões PDF, CSV e XLSX permanecem desabilitados

***Cenário 9: perfil sem acesso (E4)***

> **Dado que** o usuário autenticado é Docente e não é Coordenador de
> Curso
>
> **Quando** abre a tela Relatórios
>
> **Então** o item Participação de Membros Externos não aparece na lista

**Tela no protótipo**

**Tela:** Relatórios: Participação de Membros Externos



**Diagrama de sequência**

**Diagrama relacionado:** sem diagrama próprio: consulta de relatório
somente leitura, sem alteração de dados.

**Link:** não se aplica.

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[x\] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-32 Consultar e exportar o relatório de formação e evasão e o histórico de indicadores do NUCOMP

| **Épico:**                | Relatórios e Informações Gerenciais |
|---------------------------|-------------------------------------|
| **Feature:**              | Dashboards de Produção              |
| **Requisitos da matriz:** | RBN-REL-02.3, RBN-REL-02.4          |
| **Prioridade (MoSCoW):**  | Must Have (REL-02.4: Should Have)   |
| **Responsável:**          | Maria Luiza Nobre                   |

**Descrição**

Como Coordenador de Curso, quero consultar e exportar o relatório de
formação e evasão de um período letivo e o histórico de indicadores do
NUCOMP, para acompanhar a situação do curso ao longo dos semestres.

**Atores**

> **Ator principal:** Coordenador de Curso.
>
> **Atores secundários:** Não há atores secundários.

**Pré-condições**

- O usuário está autenticado, com o Status da Conta Ativa (US-11). Sem
  > sessão ativa, aplica-se o E1.

- O usuário tem o perfil Coordenador de Curso; caso contrário, aplica-se
  > o E3.

**Fluxo principal**

> 1\. No menu lateral do sistema, na área Gestão, o Coordenador de Curso
> seleciona o item Relatórios.
>
> 2\. O sistema abre a tela Relatórios, e o Coordenador seleciona
> Formação e evasão.
>
> 3\. O sistema exibe o relatório com o filtro Período letivo (lista no
> formato Ano/Semestre, com o período letivo atual selecionado por
> padrão), o filtro Curso (lista: Engenharia de Computação, Sistemas de
> Informação, Licenciatura em Computação ou Todos), preenchido por
> padrão com o curso do usuário (US-39), e os botões PDF, CSV e XLSX.
>
> 4\. O Coordenador seleciona o período letivo e o curso.
>
> 5\. O sistema atualiza a pré-visualização, somente leitura, com uma
> linha por curso e a linha Total, nas colunas Curso, Matriculados
> (alunos vinculados às turmas do período, exceto os excluídos da
> turma), Sem Proposta, Ativos (Em Andamento, Apto para Defesa, Aprovado
> e Aprovado com Correções sem Versão Final homologada), Com Sucesso
> (Concluído e Aprovado para TCC 2) e Sem Sucesso (Reprovado, Desistente
> e Jubilado). Sem Proposta + Ativos + Com Sucesso + Sem Sucesso =
> Matriculados. Cada aluno é contado pelo último Status do TCC
> registrado no histórico para a turma do período (CAD-08.7).
>
> 6\. O Coordenador aciona o botão PDF, CSV ou XLSX, no canto superior
> direito do relatório.
>
> 7\. O sistema gera o arquivo no formato escolhido, com os dados e os
> filtros exibidos em tela, disponibiliza o arquivo para download e
> mantém o Coordenador na tela do relatório. O fluxo termina.

**Fluxos alternativos**

> A. Histórico de indicadores do NUCOMP (passo 2): o Coordenador
> seleciona Histórico de indicadores do NUCOMP. O sistema exibe apenas o
> filtro Curso, sem filtro de período, e uma linha por período letivo
> cadastrado, do mais antigo ao mais recente, com as colunas Período
> letivo, Alunos Vinculados (alunos com vínculo em turmas do período),
> Defesas Realizadas (sessões com status Realizada), Artigos Publicados
> (artigos com Status de Submissão Publicado) e Desistências (transições
> para Desistente no período). O fluxo prossegue a partir do passo 6.
>
> B. Curso Todos (passo 4): o Coordenador seleciona Todos no filtro
> Curso, e a pré-visualização exibe uma linha por curso do NUCOMP e a
> linha Total. O fluxo prossegue a partir do passo 5.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o Coordenador de Curso
> tente acessar a tela Relatórios sem sessão ativa (pelo menu, pelo
> endereço da página ou por um link recebido), o sistema apresenta a
> tela de login (US-11). Após a autenticação, o sistema exibe o
> relatório Formação e evasão, e o fluxo prossegue a partir do passo 3.
> Em caso de falha na autenticação, aplicam-se as exceções da US-11.
>
> E2. Nenhum registro para os filtros (passo 5): a pré-visualização
> exibe a tabela vazia com a mensagem "Nenhum registro encontrado para
> os filtros selecionados", e os botões PDF, CSV e XLSX permanecem
> desabilitados. O fluxo termina.
>
> E3. Perfil sem acesso (passo 2): para quem não é Coordenador de Curso,
> os itens Formação e evasão e Histórico de indicadores do NUCOMP não
> aparecem na lista de relatórios. O fluxo termina.

**Pós-condições**

- Nenhum dado foi alterado: os relatórios são somente leitura.

- Na exportação, o arquivo foi gerado com os dados e os filtros exibidos
  > em tela.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                     | **Resumo da regra em uma frase**                                                                                                                                                                                 |
|--------------|-------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **REL-02.3** | O sistema deve emitir o relatório de formação e evasão.     | Uma linha por curso da turma, com Matriculados = Sem Proposta + Ativos + Com Sucesso + Sem Sucesso; filtros de Período Letivo e Curso; exporta em PDF, CSV ou XLSX.                                              |
| **REL-02.4** | O sistema deve emitir o histórico de indicadores do NUCOMP. | Uma linha por período letivo, do mais antigo ao mais recente, com Alunos Vinculados, Defesas Realizadas, Artigos Publicados e Desistências; sem filtro de período, apenas de Curso; exporta em PDF, CSV ou XLSX. |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Valores de Sem Proposta, Ativos, Com Sucesso e Sem Sucesso.
>
> 2\. Cálculos exatos com base no Status do TCC: a soma das colunas é
> igual ao total de Matriculados.

***Cenário 1: Coordenador consulta e exporta o relatório de formação e
evasão (fluxo principal)***

> **Dado que** a turma de Engenharia de Computação de 2026/2 tem 12
> alunos: 2 Sem Proposta, 9 Ativos, 1 Com Sucesso e 0 Sem Sucesso
>
> **Quando** o Coordenador de Curso abre Formação e evasão com o período
> 2026/2 e aciona o botão CSV
>
> **Então** a pré-visualização exibe Matriculados 12, Sem Proposta 2,
> Ativos 9, Com Sucesso 1 e Sem Sucesso 0
>
> **E** o navegador baixa o arquivo CSV com esses dados

***Cenário 2: soma igual ao total de Matriculados (fluxo principal)***

> **Dado que** o período 2026/2 tem 8 alunos matriculados
>
> **Quando** o Coordenador gera o relatório desse período
>
> **Então** a soma de Sem Proposta, Ativos, Com Sucesso e Sem Sucesso é
> igual a 8

***Cenário 3: aprovado sem Versão Final conta como Ativo (fluxo
principal)***

> **Dado que** um aluno de TCC 2 está com o Status Aprovado e sem Versão
> Final homologada
>
> **Quando** o Coordenador gera o relatório do período
>
> **Então** esse aluno é contado na coluna Ativos, e não em Com Sucesso

***Cenário 4: período anterior contado pelo histórico (fluxo
principal)***

> **Dado que** um aluno foi Aprovado para TCC 2 na turma de 2026/1 e
> hoje está Em Andamento na turma de TCC 2 de 2026/2
>
> **Quando** o Coordenador gera o relatório de 2026/1
>
> **Então** esse aluno é contado na coluna Com Sucesso de 2026/1

***Cenário 5: histórico de indicadores (fluxo alternativo A)***

> **Dado que** o sistema tem os períodos 2025/2, 2026/1 e 2026/2
>
> **Quando** o Coordenador seleciona Histórico de indicadores do NUCOMP
>
> **Então** o sistema exibe 3 linhas, de 2025/2 a 2026/2, com Alunos
> Vinculados, Defesas Realizadas, Artigos Publicados e Desistências, sem
> filtro de período

***Cenário 6: curso Todos (fluxo alternativo B)***

> **Dado que** o Coordenador está em Formação e evasão
>
> **Quando** seleciona Todos no filtro Curso
>
> **Então** a pré-visualização exibe uma linha por curso do NUCOMP e a
> linha Total

***Cenário 7: acesso sem estar autenticado (E1)***

> **Dado que** o usuário não está autenticado
>
> **Quando** tenta abrir a tela Relatórios
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre o relatório Formação e evasão

***Cenário 8: nenhum registro para os filtros (E2)***

> **Dado que** não há dados para o período selecionado no relatório
> Formação e evasão
>
> **Quando** o sistema atualiza a pré-visualização
>
> **Então** exibe a tabela vazia com a mensagem "Nenhum registro
> encontrado para os filtros selecionados"
>
> **E** os botões PDF, CSV e XLSX permanecem desabilitados

***Cenário 9: perfil sem acesso (E3)***

> **Dado que** o usuário autenticado não é Coordenador de Curso
>
> **Quando** abre a tela Relatórios
>
> **Então** os itens Formação e evasão e Histórico de indicadores do
> NUCOMP não aparecem na lista

**Tela no protótipo**

**Tela:** Relatórios: Formação e evasão



**Tela:** Relatórios: Histórico de indicadores do NUCOMP



**Diagrama de sequência**

**Diagrama relacionado:** sem diagrama próprio: consulta de relatório
somente leitura, sem alteração de dados.

**Link:** não se aplica.

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[x\] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-33 Consultar e exportar os relatórios de produção de TCCs e de artigos

| **Épico:**                | Relatórios e Informações Gerenciais |
|---------------------------|-------------------------------------|
| **Feature:**              | Dashboards de Produção              |
| **Requisitos da matriz:** | RBN-REL-02.1, RBN-REL-02.2          |
| **Prioridade (MoSCoW):**  | Must Have                           |
| **Responsável:**          | Maria Luiza Nobre                   |

**Descrição**

Como Coordenador de Curso, quero consultar e exportar os relatórios de
produção de TCCs, agrupados por curso, área de interesse ou modalidade,
e de artigos, para analisar as áreas de maior interesse e a produção
científica do curso.

**Atores**

> **Ator principal:** Coordenador de Curso.
>
> **Atores secundários:** Não há atores secundários.

**Pré-condições**

- O usuário está autenticado, com o Status da Conta Ativa (US-11). Sem
  > sessão ativa, aplica-se o E1.

- O usuário tem o perfil Coordenador de Curso; caso contrário, aplica-se
  > o E3.

**Fluxo principal**

> 1\. No menu lateral do sistema, na área Gestão, o Coordenador de Curso
> seleciona o item Relatórios.
>
> 2\. O sistema abre a tela Relatórios, e o Coordenador seleciona
> Produção de TCCs.
>
> 3\. O sistema exibe o relatório com os filtros Período letivo (lista
> Ano/Semestre, padrão o período atual), Agrupar por (lista: Curso, Área
> de Interesse ou Modalidade; padrão Curso), Abrangência (lista: Todos,
> Todos os Aprovados ou Apenas Concluídos; padrão Todos) e o filtro
> Curso (lista: Engenharia de Computação, Sistemas de Informação,
> Licenciatura em Computação ou Todos), preenchido por padrão com o
> curso do usuário (US-39), e os botões PDF, CSV e XLSX.
>
> 4\. O Coordenador seleciona o período letivo, o agrupamento Curso, a
> abrangência Todos e o curso.
>
> 5\. O sistema atualiza a pré-visualização, somente leitura, com uma
> linha por valor do agrupamento (curso da turma) e a linha Total, nas
> colunas Total de Trabalhos, Ativos (Em Andamento, Apto para Defesa,
> Aprovado e Aprovado com Correções sem Versão Final homologada), Com
> Sucesso (Concluído e Aprovado para TCC 2) e Sem Sucesso (Reprovado,
> Desistente e Jubilado). Total de Trabalhos = Ativos + Com Sucesso +
> Sem Sucesso, e por isso os TCCs Sem Proposta não entram no relatório.
> Cada trabalho é contado pelo último Status do TCC registrado no
> histórico para a turma do período (CAD-08.7).
>
> 6\. O Coordenador aciona o botão PDF, CSV ou XLSX, no canto superior
> direito do relatório.
>
> 7\. O sistema gera o arquivo no formato escolhido, com os dados e os
> filtros exibidos em tela, disponibiliza o arquivo para download e
> mantém o Coordenador na tela do relatório. O fluxo termina.

**Fluxos alternativos**

> A. Agrupamento por Área de Interesse (passo 4): o Coordenador
> seleciona Área de Interesse no filtro Agrupar por. A pré-visualização
> exibe uma linha por uma das 10 áreas, e os trabalhos sem área aparecem
> na linha "Não informada". O fluxo prossegue a partir do passo 5.
>
> B. Agrupamento por Modalidade (passo 4): o Coordenador seleciona
> Modalidade, e a pré-visualização exibe as linhas Monografia e Artigo
> Científico. O fluxo prossegue a partir do passo 5.
>
> C. Abrangência Todos os Aprovados ou Apenas Concluídos (passo 4): com
> Todos os Aprovados, a pré-visualização considera os trabalhos Aprovado
> para TCC 2, Aprovado, Aprovado com Correções e Concluído; com Apenas
> Concluídos, apenas os Concluídos. O fluxo prossegue a partir do passo
> 5.
>
> D. Relatório de artigos (passo 2): o Coordenador seleciona Artigos. O
> sistema exibe os filtros Período letivo e Curso e a pré-visualização
> dos TCCs na modalidade Artigo Científico das turmas do período, com as
> colunas Título do TCC, Aluno, Orientador, Veículo, Estrato
> Qualis/CAPES, Status de Submissão, Aproveitamento (Em Análise,
> Homologado ou Recusado) e Link ou DOI. O link abre o artigo fora do
> sistema. O fluxo prossegue a partir do passo 6.
>
> E. Curso Todos (passo 4): o Coordenador seleciona Todos no filtro
> Curso, e a pré-visualização considera os trabalhos de todos os cursos
> do NUCOMP. O fluxo prossegue a partir do passo 5.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o Coordenador de Curso
> tente acessar a tela Relatórios sem sessão ativa (pelo menu, pelo
> endereço da página ou por um link recebido), o sistema apresenta a
> tela de login (US-11). Após a autenticação, o sistema exibe o
> relatório Produção de TCCs, e o fluxo prossegue a partir do passo 3.
> Em caso de falha na autenticação, aplicam-se as exceções da US-11.
>
> E2. Nenhum registro para os filtros (passo 5): a pré-visualização
> exibe a tabela vazia com a mensagem "Nenhum registro encontrado para
> os filtros selecionados", e os botões PDF, CSV e XLSX permanecem
> desabilitados. O fluxo termina.
>
> E3. Perfil sem acesso (passo 2): para quem não é Coordenador de Curso,
> os itens Produção de TCCs e Artigos não aparecem na lista de
> relatórios. O fluxo termina.

**Pós-condições**

- Nenhum dado foi alterado: os relatórios são somente leitura.

- Na exportação, o arquivo foi gerado com os dados e os filtros exibidos
  > em tela.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                      | **Resumo da regra em uma frase**                                                                                                                                                                                |
|--------------|--------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **REL-02.1** | O sistema deve emitir o relatório de produção de TCCs, agrupável por Curso, Área de Interesse ou Modalidade. | Produção de TCCs agrupada por Curso, Área de Interesse ou Modalidade, com Total de Trabalhos = Ativos + Com Sucesso + Sem Sucesso; filtros de Período Letivo, Abrangência e Curso; exporta em PDF, CSV ou XLSX. |
| **REL-02.2** | O sistema deve emitir o relatório de artigos.                                                                | Lista dos TCCs na modalidade Artigo Científico das turmas do período, com dados de publicação e aproveitamento; filtros de Período Letivo e Curso; exporta em PDF, CSV ou XLSX.                                 |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Agrupamento por Curso, Modalidade e pelas 10 Áreas de Interesse.
>
> 2\. Exportação obrigatória e formatada para PDF, CSV e XLSX.
>
> 3\. Visualização apenas pelo Coordenador de curso.
>
> 4\. A tabela deve conter as colunas Total de Trabalhos, Ativos, Com
> Sucesso e Sem Sucesso.

***Cenário 1: Coordenador consulta e exporta a produção de TCCs por
curso (fluxo principal)***

> **Dado que** Engenharia de Computação tem 10 trabalhos em 2026/2: 9
> Ativos, 1 Com Sucesso e 0 Sem Sucesso
>
> **Quando** o Coordenador de Curso abre Produção de TCCs agrupado por
> Curso e aciona o botão PDF
>
> **Então** a pré-visualização exibe Total de Trabalhos 10, Ativos 9,
> Com Sucesso 1 e Sem Sucesso 0
>
> **E** o navegador baixa o PDF com esses dados

***Cenário 2: agrupamento por Área de Interesse (fluxo alternativo A)***

> **Dado que** um trabalho do período não tem Área de Interesse
> preenchida
>
> **Quando** o Coordenador seleciona Área de Interesse no filtro Agrupar
> por
>
> **Então** a pré-visualização exibe uma linha por área e esse trabalho
> na linha "Não informada"

***Cenário 3: agrupamento por Modalidade (fluxo alternativo B)***

> **Dado que** o Coordenador está em Produção de TCCs
>
> **Quando** seleciona Modalidade no filtro Agrupar por
>
> **Então** a pré-visualização exibe as linhas Monografia e Artigo
> Científico

***Cenário 4: abrangência Apenas Concluídos (fluxo alternativo C)***

> **Dado que** o período tem 1 trabalho Concluído e 9 Ativos
>
> **Quando** o Coordenador seleciona Apenas Concluídos no filtro
> Abrangência
>
> **Então** a pré-visualização considera apenas o trabalho Concluído

***Cenário 5: relatório de artigos (fluxo alternativo D)***

> **Dado que** o período tem um TCC na modalidade Artigo Científico com
> aproveitamento Homologado
>
> **Quando** o Coordenador seleciona Artigos
>
> **Então** a pré-visualização exibe o Título do TCC, Aluno, Orientador,
> Veículo, Estrato Qualis/CAPES, Status de Submissão, Aproveitamento
> Homologado e o Link ou DOI

***Cenário 6: curso Todos (fluxo alternativo E)***

> **Dado que** o Coordenador está em Produção de TCCs
>
> **Quando** seleciona Todos no filtro Curso
>
> **Então** a pré-visualização considera os trabalhos de todos os cursos
> do NUCOMP

***Cenário 7: acesso sem estar autenticado (E1)***

> **Dado que** o usuário não está autenticado
>
> **Quando** tenta abrir a tela Relatórios
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre o relatório Produção de TCCs

***Cenário 8: nenhum registro para os filtros (E2)***

> **Dado que** não há dados para o período selecionado no relatório
> Produção de TCCs
>
> **Quando** o sistema atualiza a pré-visualização
>
> **Então** exibe a tabela vazia com a mensagem "Nenhum registro
> encontrado para os filtros selecionados"
>
> **E** os botões PDF, CSV e XLSX permanecem desabilitados

***Cenário 9: perfil sem acesso (E3)***

> **Dado que** o usuário autenticado não é Coordenador de Curso
>
> **Quando** abre a tela Relatórios
>
> **Então** os itens Produção de TCCs e Artigos não aparecem na lista

**Tela no protótipo**

**Tela:** Relatórios: Produção de TCCs



**Tela:** Relatórios: Artigos



**Diagrama de sequência**

**Diagrama relacionado:** sem diagrama próprio: consulta de relatório
somente leitura, sem alteração de dados.

**Link:** não se aplica.

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[x\] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-48 Consultar e exportar a lista de defesas realizadas no período

| **Épico:**                | Relatórios e Informações Gerenciais |
|---------------------------|-------------------------------------|
| **Feature:**              | Apoio Operacional                   |
| **Requisitos da matriz:** | RBN-REL-03.1                        |
| **Prioridade (MoSCoW):**  | Must Have                           |
| **Responsável:**          | Maria Luiza Nobre                   |

**Descrição**

Como Secretaria, quero consultar e exportar a lista das defesas
realizadas no período, com aluno, orientador, banca, modalidade e
parecer, para conferir e arquivar os registros das defesas do curso.

**Atores**

> **Ator principal:** Secretaria.
>
> **Atores secundários:** Coordenador de Curso e Professor da
> Disciplina, que consultam o relatório pelo mesmo fluxo (fluxos
> alternativos C e D).

**Pré-condições**

- O usuário está autenticado, com o Status da Conta Ativa (US-11). Sem
  > sessão ativa, aplica-se o E1.

- O usuário tem o perfil Secretaria, Coordenador de Curso ou Professor
  > da Disciplina; caso contrário, aplica-se o E4.

**Fluxo principal**

> 1\. No menu lateral do sistema, na área Gestão, a Secretaria seleciona
> o item Relatórios.
>
> 2\. O sistema abre a tela Relatórios, e a Secretaria seleciona Defesas
> realizadas no período.
>
> 3\. O sistema exibe o relatório com os filtros Período (lista: Período
> Letivo, Esta Semana, Este Mês ou Próximos 30 Dias), Ano/Semestre, Data
> Inicial e Data Final (DD/MM/AAAA, por calendário), preenchidos por
> padrão com o período letivo atual, o filtro Curso (lista: Engenharia
> de Computação, Sistemas de Informação, Licenciatura em Computação ou
> Todos), preenchido por padrão com o curso do usuário (US-39), e os
> botões PDF, CSV e XLSX.
>
> 4\. A Secretaria seleciona o atalho Período Letivo no filtro Período,
> o semestre no filtro Ano/Semestre e o curso no filtro Curso.
>
> 5\. O sistema atualiza a pré-visualização, somente leitura,
> exclusivamente com as sessões de status Realizada do período, nas
> colunas Data/Horário, Aluno, Orientador, Banca, Modalidade do TCC e
> Parecer.
>
> 6\. A Secretaria aciona o botão PDF, CSV ou XLSX, no canto superior
> direito do relatório.
>
> 7\. O sistema gera o arquivo no formato escolhido, com os dados e os
> filtros exibidos em tela, disponibiliza o arquivo para download e
> mantém a Secretaria na tela do relatório. O fluxo termina.

**Fluxos alternativos**

> A. Período informado por datas (passo 4): a Secretaria informa Data
> Inicial e Data Final no calendário (DD/MM/AAAA). O fluxo prossegue a
> partir do passo 5.
>
> B. Atalho Esta Semana, Este Mês ou Próximos 30 Dias (passo 4): o
> sistema preenche automaticamente Data Inicial e Data Final com as
> datas do atalho. O fluxo prossegue a partir do passo 5.
>
> C. Consulta pelo Coordenador de Curso (passo 1): o Coordenador segue
> os mesmos passos, com o filtro Curso preenchido por padrão com o seu
> Curso Coordenado. O fluxo prossegue a partir do passo 2.
>
> D. Consulta pelo Professor da Disciplina (passo 3): o relatório exibe
> apenas os filtros de período. Para o Professor da Disciplina, o filtro
> Curso não aparece. O fluxo prossegue a partir do passo 4.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o usuário tente acessar a
> tela Relatórios sem sessão ativa (pelo menu, pelo endereço da página
> ou por um link recebido), o sistema apresenta a tela de login (US-11).
> Após a autenticação, o sistema exibe o relatório Defesas realizadas no
> período, e o fluxo prossegue a partir do passo 3. Em caso de falha na
> autenticação, aplicam-se as exceções da US-11.
>
> E2. Intervalo de datas inválido (passo 5): a Data Inicial é posterior
> à Data Final. O sistema não atualiza a pré-visualização e exibe "A
> data inicial não pode ser superior à data final". Retorna ao passo 4.
>
> E3. Nenhum registro para os filtros (passo 5): a pré-visualização
> exibe a tabela vazia com a mensagem "Nenhum registro encontrado para
> os filtros selecionados", e os botões PDF, CSV e XLSX permanecem
> desabilitados. O fluxo termina.
>
> E4. Perfil sem acesso (passo 2): para o Aluno e para o Docente que não
> é Coordenador de Curso nem Professor da Disciplina, o item Defesas
> realizadas no período não aparece. O fluxo termina.

**Pós-condições**

- Nenhum dado foi alterado: o relatório é somente leitura.

- Na exportação, o arquivo foi gerado com os dados e os filtros exibidos
  > em tela.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                         | **Resumo da regra em uma frase**                                                                                                                                                                                                           |
|--------------|-----------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **REL-03.1** | O sistema deve emitir a lista de defesas realizadas no período. | Lista apenas das sessões com status Realizada no período, com Data/Horário, Aluno, Orientador, Banca, Modalidade do TCC e Parecer; filtro de período e, para o Coordenador de Curso e a Secretaria, de Curso; exporta em PDF, CSV ou XLSX. |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. A lista de defesas mostra só as sessões com status Realizada.
>
> 2\. O relatório exporta em PDF, CSV ou XLSX.

***Cenário 1: Secretaria consulta e exporta as defesas realizadas (fluxo
principal)***

> **Dado que** no período 2026/2 há 3 sessões Realizadas e 1 sessão
> Agendada
>
> **Quando** a Secretaria abre Defesas realizadas no período com 2026/2
> e aciona o botão PDF
>
> **Então** a pré-visualização exibe apenas as 3 sessões Realizadas, com
> Data/Horário, Aluno, Orientador, Banca, Modalidade do TCC e Parecer
>
> **E** o navegador baixa o PDF com essas 3 sessões

***Cenário 2: período informado por datas (fluxo alternativo A)***

> **Dado que** o usuário está na tela do relatório
>
> **Quando** informa a Data Inicial 01/09/2026 e a Data Final 30/09/2026
> no calendário
>
> **Então** a pré-visualização considera apenas o intervalo informado

***Cenário 3: seleção por atalho de período (fluxo alternativo B)***

> **Dado que** o usuário está na tela do relatório
>
> **Quando** seleciona o atalho Este Mês no filtro Período
>
> **Então** o sistema preenche Data Inicial e Data Final com o primeiro
> e o último dia do mês e atualiza a pré-visualização

***Cenário 4: consulta pelo Coordenador de Curso (fluxo alternativo
C)***

> **Dado que** o Coordenador de Curso de Sistemas de Informação está
> autenticado
>
> **Quando** abre Defesas realizadas no período
>
> **Então** o filtro Curso aparece preenchido com Sistemas de Informação

***Cenário 5: consulta pelo Professor da Disciplina (fluxo alternativo
D)***

> **Dado que** o usuário autenticado é Professor da Disciplina e não é
> Coordenador de Curso
>
> **Quando** abre Defesas realizadas no período
>
> **Então** o relatório exibe os filtros de período, sem o filtro Curso

***Cenário 6: acesso sem estar autenticado (E1)***

> **Dado que** o usuário não está autenticado
>
> **Quando** tenta abrir a tela Relatórios
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre o relatório Defesas realizadas no período

***Cenário 7: intervalo de datas inválido (E2)***

> **Dado que** o usuário está na tela do relatório
>
> **Quando** informa a Data Inicial 30/11/2026 e a Data Final 01/11/2026
>
> **Então** o sistema não atualiza a pré-visualização e exibe "A data
> inicial não pode ser superior à data final"

***Cenário 8: nenhum registro para os filtros (E3)***

> **Dado que** não há dados para o período selecionado no relatório
> Defesas realizadas no período
>
> **Quando** o sistema atualiza a pré-visualização
>
> **Então** exibe a tabela vazia com a mensagem "Nenhum registro
> encontrado para os filtros selecionados"
>
> **E** os botões PDF, CSV e XLSX permanecem desabilitados

***Cenário 9: perfil sem acesso (E4)***

> **Dado que** o usuário autenticado é Docente e não é Coordenador de
> Curso nem Professor da Disciplina
>
> **Quando** abre a tela Relatórios
>
> **Então** o item Defesas realizadas no período não aparece na lista

**Tela no protótipo**

**Tela:** relatório sem tela no protótipo.

**Diagrama de sequência**

**Diagrama relacionado:** sem diagrama próprio: consulta de relatório
somente leitura, sem alteração de dados.

**Link:** não se aplica.

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-49 Consultar e exportar o relatório de turmas e alunos

| **Épico:**                | Relatórios e Informações Gerenciais |
|---------------------------|-------------------------------------|
| **Feature:**              | Apoio Operacional                   |
| **Requisitos da matriz:** | RBN-REL-03.2                        |
| **Prioridade (MoSCoW):**  | Should Have                         |
| **Responsável:**          | Maria Luiza Nobre                   |

**Descrição**

Como Secretaria, quero consultar e exportar as turmas do período com os
alunos matriculados e o Status do TCC de cada um, com destaque para
Reprovado, Desistente e Jubilado, para conferir a situação dos alunos de
cada turma.

**Atores**

> **Ator principal:** Secretaria.
>
> **Atores secundários:** Coordenador de Curso e Professor da
> Disciplina, que consultam o relatório (fluxos alternativos A e B).

**Pré-condições**

- O usuário está autenticado, com o Status da Conta Ativa (US-11). Sem
  > sessão ativa, aplica-se o E1.

- O usuário tem o perfil Secretaria, Coordenador de Curso ou Professor
  > da Disciplina; caso contrário, aplica-se o E3.

**Fluxo principal**

> 1\. No menu lateral do sistema, na área Gestão, a Secretaria seleciona
> o item Relatórios.
>
> 2\. O sistema abre a tela Relatórios, e a Secretaria seleciona Turmas
> e alunos.
>
> 3\. O sistema exibe o relatório com o filtro Período letivo (lista no
> formato Ano/Semestre, com o período letivo atual selecionado por
> padrão), o filtro Curso (lista: Engenharia de Computação, Sistemas de
> Informação, Licenciatura em Computação ou Todos), preenchido por
> padrão com o curso do usuário (US-39), e os botões PDF, CSV e XLSX.
>
> 4\. A Secretaria seleciona o período letivo e o curso.
>
> 5\. O sistema atualiza a pré-visualização, somente leitura, com uma
> linha por turma e as colunas Turma, TCC 1 ou TCC 2, Professor da
> Disciplina, Total de Alunos e a lista de alunos matriculados, com o
> Status do TCC ao lado de cada nome. Quem ainda não salvou a Proposta
> aparece com "Sem Proposta", e os Status Reprovado, Desistente e
> Jubilado aparecem destacados visualmente. Em turmas de períodos
> anteriores, o Status exibido é o último registrado no histórico para
> aquela turma (CAD-08.7).
>
> 6\. A Secretaria aciona o botão PDF, CSV ou XLSX, no canto superior
> direito do relatório.
>
> 7\. O sistema gera o arquivo no formato escolhido, com os dados e os
> filtros exibidos em tela, disponibiliza o arquivo para download e
> mantém a Secretaria na tela do relatório. O fluxo termina.

**Fluxos alternativos**

> A. Consulta pelo Coordenador de Curso (passo 1): o Coordenador segue
> os mesmos passos, com o filtro Curso preenchido por padrão com o seu
> Curso Coordenado. O fluxo prossegue a partir do passo 2.
>
> B. Consulta pelo Professor da Disciplina (passo 3): o relatório exibe
> apenas as turmas em que o usuário é o Professor da Disciplina. Para o
> Professor da Disciplina, o filtro Curso não aparece. O fluxo prossegue
> a partir do passo 4.
>
> C. Curso Todos (passo 4): a Secretaria seleciona Todos no filtro
> Curso, e a pré-visualização exibe as turmas de todos os cursos do
> NUCOMP. O fluxo prossegue a partir do passo 5.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o usuário tente acessar a
> tela Relatórios sem sessão ativa (pelo menu, pelo endereço da página
> ou por um link recebido), o sistema apresenta a tela de login (US-11).
> Após a autenticação, o sistema exibe o relatório Turmas e alunos, e o
> fluxo prossegue a partir do passo 3. Em caso de falha na autenticação,
> aplicam-se as exceções da US-11.
>
> E2. Nenhum registro para os filtros (passo 5): a pré-visualização
> exibe a tabela vazia com a mensagem "Nenhum registro encontrado para
> os filtros selecionados", e os botões PDF, CSV e XLSX permanecem
> desabilitados. O fluxo termina.
>
> E3. Perfil sem acesso (passo 2): para o Aluno e para o Docente que não
> é Coordenador de Curso nem Professor da Disciplina, o item Turmas e
> alunos não aparece. O fluxo termina.

**Pós-condições**

- Nenhum dado foi alterado: o relatório é somente leitura.

- Na exportação, o arquivo foi gerado com os dados, os destaques e os
  > filtros exibidos em tela.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                               | **Resumo da regra em uma frase**                                                                                                                                                                                                                           |
|--------------|-------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **REL-03.2** | O sistema deve emitir o relatório de turmas e alunos. | Turmas do período com o Status do TCC ao lado de cada aluno ("Sem Proposta" para quem não salvou a Proposta) e destaque visual para Reprovado, Desistente e Jubilado; o Professor da Disciplina vê apenas as próprias turmas; exporta em PDF, CSV ou XLSX. |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. O relatório de turmas mostra o Status de cada aluno e destaca
> Reprovado, Desistente e Jubilado.
>
> 2\. O relatório exporta em PDF, CSV ou XLSX.

***Cenário 1: Secretaria consulta e exporta as turmas do período (fluxo
principal)***

> **Dado que** a turma ECP07_T01 de 2026/2 tem 7 alunos, 3 deles Sem
> Proposta
>
> **Quando** a Secretaria abre Turmas e alunos com 2026/2 e aciona o
> botão XLSX
>
> **Então** a pré-visualização exibe a turma com TCC 1, o Professor da
> Disciplina, Total de Alunos 7 e cada aluno com o Status do TCC ao lado
> do nome, 3 deles com "Sem Proposta"
>
> **E** o navegador baixa o arquivo XLSX com esses dados

***Cenário 2: destaque de situações críticas (fluxo principal)***

> **Dado que** um aluno da turma está com o Status Desistente
>
> **Quando** a Secretaria abre Turmas e alunos
>
> **Então** o Status Desistente desse aluno aparece destacado
> visualmente

***Cenário 3: consulta pelo Coordenador de Curso (fluxo alternativo
A)***

> **Dado que** o Coordenador de Curso de Engenharia de Computação está
> autenticado
>
> **Quando** abre Turmas e alunos
>
> **Então** o filtro Curso aparece preenchido com Engenharia de
> Computação

***Cenário 4: Professor da Disciplina vê apenas as próprias turmas
(fluxo alternativo B)***

> **Dado que** o Professor da Disciplina é responsável pela turma
> ECP07_T01 e não pela turma SIN07_T01
>
> **Quando** abre Turmas e alunos
>
> **Então** a pré-visualização exibe apenas a turma ECP07_T01, sem o
> filtro Curso

***Cenário 5: curso Todos (fluxo alternativo C)***

> **Dado que** a Secretaria está em Turmas e alunos
>
> **Quando** seleciona Todos no filtro Curso
>
> **Então** a pré-visualização exibe as turmas de todos os cursos do
> NUCOMP

***Cenário 6: acesso sem estar autenticado (E1)***

> **Dado que** o usuário não está autenticado
>
> **Quando** tenta abrir a tela Relatórios
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre o relatório Turmas e alunos

***Cenário 7: nenhum registro para os filtros (E2)***

> **Dado que** não há dados para o período selecionado no relatório
> Turmas e alunos
>
> **Quando** o sistema atualiza a pré-visualização
>
> **Então** exibe a tabela vazia com a mensagem "Nenhum registro
> encontrado para os filtros selecionados"
>
> **E** os botões PDF, CSV e XLSX permanecem desabilitados

***Cenário 8: perfil sem acesso (E3)***

> **Dado que** o usuário autenticado é Docente e não é Coordenador de
> Curso nem Professor da Disciplina
>
> **Quando** abre a tela Relatórios
>
> **Então** o item Turmas e alunos não aparece na lista

**Tela no protótipo**

**Tela:** relatório sem tela no protótipo.

**Diagrama de sequência**

**Diagrama relacionado:** sem diagrama próprio: consulta de relatório
somente leitura, sem alteração de dados.

**Link:** não se aplica.

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-34 Consultar e exportar o relatório de aluno e orientador para apoio à matrícula

| **Épico:**                | Relatórios e Informações Gerenciais |
|---------------------------|-------------------------------------|
| **Feature:**              | Apoio Operacional                   |
| **Requisitos da matriz:** | RBN-REL-03.3                        |
| **Prioridade (MoSCoW):**  | Should Have                         |
| **Responsável:**          | Maria Luiza Nobre                   |

**Descrição**

Como Secretaria, quero consultar e exportar o relatório de aluno e
orientador, com os alunos Aprovados para TCC 2 listados primeiro e
destacados, para identificar os alunos que devem ser matriculados na
disciplina de TCC 2 no sistema acadêmico da UEA (Lyceum).

**Atores**

> **Ator principal:** Secretaria.
>
> **Atores secundários:** Coordenador de Curso e Professor da
> Disciplina, que consultam o relatório (fluxos alternativos A e B).

**Pré-condições**

- O usuário está autenticado, com o Status da Conta Ativa (US-11). Sem
  > sessão ativa, aplica-se o E1.

- O usuário tem o perfil Secretaria, Coordenador de Curso ou Professor
  > da Disciplina; caso contrário, aplica-se o E3.

**Fluxo principal**

> 1\. No menu lateral do sistema, na área Gestão, a Secretaria seleciona
> o item Relatórios.
>
> 2\. O sistema abre a tela Relatórios, e a Secretaria seleciona Aluno e
> orientador (apoio à matrícula).
>
> 3\. O sistema exibe o relatório com o filtro Período letivo (lista no
> formato Ano/Semestre, com o período letivo atual selecionado por
> padrão), o filtro Curso (lista: Engenharia de Computação, Sistemas de
> Informação, Licenciatura em Computação ou Todos), preenchido por
> padrão com o curso do usuário (US-39), e os botões PDF, CSV e XLSX.
>
> 4\. A Secretaria seleciona o período letivo e o curso.
>
> 5\. O sistema atualiza a pré-visualização, somente leitura, com as
> colunas Matrícula, Nome do Aluno, Orientador (aceito em TCC 1) e
> Status do TCC. Os alunos com o Status Aprovado para TCC 2 aparecem
> primeiro e destacados visualmente. O Status exibido é o último
> registrado no histórico para a turma do período (CAD-08.7), de modo
> que o aluno já transferido para o TCC 2 continua listado como Aprovado
> para TCC 2 no período de origem.
>
> 6\. A Secretaria aciona o botão PDF, CSV ou XLSX, no canto superior
> direito do relatório.
>
> 7\. O sistema gera o arquivo no formato escolhido, com os dados e os
> filtros exibidos em tela, disponibiliza o arquivo para download e
> mantém a Secretaria na tela do relatório. Fora do SIGTCC, a Secretaria
> utiliza o arquivo na matrícula dos alunos em TCC 2. O fluxo termina.

**Fluxos alternativos**

> A. Consulta pelo Coordenador de Curso (passo 1): o Coordenador segue
> os mesmos passos, com o filtro Curso preenchido por padrão com o seu
> Curso Coordenado. O fluxo prossegue a partir do passo 2.
>
> B. Consulta pelo Professor da Disciplina (passo 3): o relatório exibe
> apenas o filtro Período letivo. Para o Professor da Disciplina, o
> filtro Curso não aparece. O fluxo prossegue a partir do passo 4.
>
> C. Curso Todos (passo 4): a Secretaria seleciona Todos no filtro
> Curso, e a pré-visualização exibe os alunos de todos os cursos do
> NUCOMP. O fluxo prossegue a partir do passo 5.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o usuário tente acessar a
> tela Relatórios sem sessão ativa (pelo menu, pelo endereço da página
> ou por um link recebido), o sistema apresenta a tela de login (US-11).
> Após a autenticação, o sistema exibe o relatório Aluno e orientador
> (apoio à matrícula), e o fluxo prossegue a partir do passo 3. Em caso
> de falha na autenticação, aplicam-se as exceções da US-11.
>
> E2. Nenhum registro para os filtros (passo 5): a pré-visualização
> exibe a tabela vazia com a mensagem "Nenhum registro encontrado para
> os filtros selecionados", e os botões PDF, CSV e XLSX permanecem
> desabilitados. O fluxo termina.
>
> E3. Perfil sem acesso (passo 2): para o Aluno e para o Docente que não
> é Coordenador de Curso nem Professor da Disciplina, o item Aluno e
> orientador (apoio à matrícula) não aparece. O fluxo termina.

**Pós-condições**

- Nenhum dado foi alterado: o relatório é somente leitura.

- Na exportação, o arquivo foi gerado com os dados e os filtros exibidos
  > em tela, com os alunos Aprovados para TCC 2 no início.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                         | **Resumo da regra em uma frase**                                                                                                                                                                                                                |
|--------------|---------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **REL-03.3** | O sistema deve emitir o relatório de aluno e orientador para apoio à matrícula. | Alunos com Matrícula, Nome, Orientador aceito em TCC 1 e Status do TCC, com os Aprovados para TCC 2 listados primeiro e destacados, para a Secretaria identificar quem deve ser matriculado na próxima disciplina; exporta em PDF, CSV ou XLSX. |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. O relatório cruza "Aluno, Orientador e Status do TCC".
>
> 2\. Evidencia visualmente os alunos "Aprovados para TCC 2".
>
> 3\. O relatório exporta em PDF, CSV ou XLSX.

***Cenário 1: Secretaria consulta e exporta o relatório (fluxo
principal)***

> **Dado que** no período 2026/2 há 2 alunos Aprovados para TCC 2 e 5
> alunos Em Andamento
>
> **Quando** a Secretaria abre Aluno e orientador (apoio à matrícula)
> com 2026/2 e aciona o botão CSV
>
> **Então** a pré-visualização exibe os 2 alunos Aprovados para TCC 2 no
> topo, destacados, seguidos dos demais, com Matrícula, Nome do Aluno,
> Orientador e Status do TCC
>
> **E** o navegador baixa o arquivo CSV na mesma ordem

***Cenário 2: consulta pelo Coordenador de Curso (fluxo alternativo
A)***

> **Dado que** o Coordenador de Curso de Licenciatura em Computação está
> autenticado
>
> **Quando** abre Aluno e orientador (apoio à matrícula)
>
> **Então** o filtro Curso aparece preenchido com Licenciatura em
> Computação

***Cenário 3: consulta pelo Professor da Disciplina (fluxo alternativo
B)***

> **Dado que** um Professor da Disciplina que não é Coordenador de Curso
> está autenticado
>
> **Quando** abre Aluno e orientador (apoio à matrícula)
>
> **Então** o relatório exibe o filtro Período letivo, sem o filtro
> Curso

***Cenário 4: curso Todos (fluxo alternativo C)***

> **Dado que** a Secretaria está no relatório
>
> **Quando** seleciona Todos no filtro Curso
>
> **Então** a pré-visualização exibe os alunos de todos os cursos do
> NUCOMP

***Cenário 5: acesso sem estar autenticado (E1)***

> **Dado que** o usuário não está autenticado
>
> **Quando** tenta abrir a tela Relatórios
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre o relatório Aluno e orientador (apoio à
> matrícula)

***Cenário 6: nenhum registro para os filtros (E2)***

> **Dado que** não há dados para o período selecionado no relatório
> Aluno e orientador (apoio à matrícula)
>
> **Quando** o sistema atualiza a pré-visualização
>
> **Então** exibe a tabela vazia com a mensagem "Nenhum registro
> encontrado para os filtros selecionados"
>
> **E** os botões PDF, CSV e XLSX permanecem desabilitados

***Cenário 7: perfil sem acesso (E3)***

> **Dado que** o usuário autenticado é Docente e não é Coordenador de
> Curso nem Professor da Disciplina
>
> **Quando** abre a tela Relatórios
>
> **Então** o item Aluno e orientador (apoio à matrícula) não aparece na
> lista

**Tela no protótipo**

**Tela:** relatório sem tela no protótipo.

**Diagrama de sequência**

**Diagrama relacionado:** sem diagrama próprio: consulta de relatório
somente leitura, sem alteração de dados.

**Link:** não se aplica.

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-35 Consultar e exportar o relatório de horas complementares de ouvintes

| **Épico:**                | Relatórios e Informações Gerenciais |
|---------------------------|-------------------------------------|
| **Feature:**              | Apoio Operacional                   |
| **Requisitos da matriz:** | RBN-REL-03.4                        |
| **Prioridade (MoSCoW):**  | Could Have                          |
| **Responsável:**          | Maria Luiza Nobre                   |

**Descrição**

Como Secretaria, quero consultar e exportar o relatório de horas
complementares dos ouvintes das defesas realizadas no período, para
lançar as horas no sistema acadêmico da UEA.

**Atores**

> **Ator principal:** Secretaria.
>
> **Atores secundários:** Coordenador de Curso e Professor da
> Disciplina, que consultam o relatório (fluxo alternativo C).

**Pré-condições**

- O usuário está autenticado, com o Status da Conta Ativa (US-11). Sem
  > sessão ativa, aplica-se o E1.

- O usuário tem o perfil Secretaria, Coordenador de Curso ou Professor
  > da Disciplina; caso contrário, aplica-se o E4.

- Os ouvintes foram registrados nas sessões pelo Orientador ou pelo
  > Professor da Disciplina (US-30).

**Fluxo principal**

> 1\. No menu lateral do sistema, na área Gestão, a Secretaria seleciona
> o item Relatórios.
>
> 2\. O sistema abre a tela Relatórios, e a Secretaria seleciona Horas
> complementares de ouvintes.
>
> 3\. O sistema exibe o relatório com os filtros Período (lista: Período
> Letivo, Esta Semana, Este Mês ou Próximos 30 Dias), Ano/Semestre, Data
> Inicial e Data Final (DD/MM/AAAA, por calendário), preenchidos por
> padrão com o período letivo atual, o filtro Curso (lista: Engenharia
> de Computação, Sistemas de Informação, Licenciatura em Computação ou
> Todos), preenchido por padrão com o curso do usuário (US-39), e os
> botões PDF, CSV e XLSX.
>
> 4\. A Secretaria seleciona o atalho Período Letivo no filtro Período,
> o semestre no filtro Ano/Semestre e o curso no filtro Curso.
>
> 5\. O sistema atualiza a pré-visualização, somente leitura, com uma
> linha por presença de ouvinte nas sessões de status Realizada do
> período, nas colunas Nome do Ouvinte, Matrícula, Data da Defesa e
> Horas (2 horas por linha), e com o total de horas ao final. Quem
> assistiu a 3 bancas aparece em 3 linhas.
>
> 6\. A Secretaria aciona o botão PDF, CSV ou XLSX, no canto superior
> direito do relatório.
>
> 7\. O sistema gera o arquivo no formato escolhido, com os dados e os
> filtros exibidos em tela, disponibiliza o arquivo para download e
> mantém a Secretaria na tela do relatório. Fora do SIGTCC, a Secretaria
> utiliza o arquivo no lançamento das horas. O fluxo termina.

**Fluxos alternativos**

> A. Período informado por datas (passo 4): a Secretaria informa Data
> Inicial e Data Final no calendário (DD/MM/AAAA). O fluxo prossegue a
> partir do passo 5.
>
> B. Atalho Esta Semana, Este Mês ou Próximos 30 Dias (passo 4): o
> sistema preenche automaticamente Data Inicial e Data Final com as
> datas do atalho. O fluxo prossegue a partir do passo 5.
>
> C. Consulta pelo Coordenador de Curso ou pelo Professor da Disciplina
> (passo 1): o usuário segue os mesmos passos. Para o Coordenador, o
> filtro Curso vem com o seu Curso Coordenado. Para o Professor da
> Disciplina, o filtro Curso não aparece. O fluxo prossegue a partir do
> passo 2.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o usuário tente acessar a
> tela Relatórios sem sessão ativa (pelo menu, pelo endereço da página
> ou por um link recebido), o sistema apresenta a tela de login (US-11).
> Após a autenticação, o sistema exibe o relatório Horas complementares
> de ouvintes, e o fluxo prossegue a partir do passo 3. Em caso de falha
> na autenticação, aplicam-se as exceções da US-11.
>
> E2. Intervalo de datas inválido (passo 5): a Data Inicial é posterior
> à Data Final. O sistema não atualiza a pré-visualização e exibe "A
> data inicial não pode ser superior à data final". Retorna ao passo 4.
>
> E3. Nenhum registro para os filtros (passo 5): a pré-visualização
> exibe a tabela vazia com a mensagem "Nenhum registro encontrado para
> os filtros selecionados", e os botões PDF, CSV e XLSX permanecem
> desabilitados. O fluxo termina.
>
> E4. Perfil sem acesso (passo 2): para o Aluno e para o Docente que não
> é Coordenador de Curso nem Professor da Disciplina, o item Horas
> complementares de ouvintes não aparece. O fluxo termina.

**Pós-condições**

- Nenhum dado foi alterado: o relatório é somente leitura.

- Na exportação, o arquivo foi gerado com uma linha por presença, as
  > horas e o total exibidos em tela.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                              | **Resumo da regra em uma frase**                                                                                                                                                                                                                                                          |
|--------------|--------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **REL-03.4** | O sistema deve emitir o relatório consolidado de horas complementares para ouvintes. | Uma linha por presença de ouvinte em sessão Realizada do período, com Nome do Ouvinte, Matrícula, Data da Defesa e 2 horas complementares por linha, e o total de horas ao final; filtro de período e, para o Coordenador de Curso e a Secretaria, de Curso; exporta em PDF, CSV ou XLSX. |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Uma linha por presença: quem assistiu a 3 bancas aparece 3 vezes.
>
> 2\. Atribui a cada registro a equivalência de 2 horas complementares.

***Cenário 1: Secretaria consulta e exporta as horas dos ouvintes (fluxo
principal)***

> **Dado que** no período 2026/2 o ouvinte de matrícula 2415080011
> assistiu a 3 sessões Realizadas
>
> **Quando** a Secretaria abre Horas complementares de ouvintes com
> 2026/2 e aciona o botão XLSX
>
> **Então** a pré-visualização exibe 3 linhas desse ouvinte, cada uma
> com a Data da Defesa e 2 horas, e o total de horas ao final
>
> **E** o navegador baixa o arquivo XLSX com essas linhas

***Cenário 2: apenas sessões Realizadas (fluxo principal)***

> **Dado que** um ouvinte foi registrado em uma sessão que depois foi
> Cancelada
>
> **Quando** a Secretaria abre o relatório do período
>
> **Então** essa presença não aparece no relatório

***Cenário 3: período informado por datas (fluxo alternativo A)***

> **Dado que** o usuário está na tela do relatório
>
> **Quando** informa a Data Inicial 01/09/2026 e a Data Final 30/09/2026
> no calendário
>
> **Então** a pré-visualização considera apenas o intervalo informado

***Cenário 4: seleção por atalho de período (fluxo alternativo B)***

> **Dado que** o usuário está na tela do relatório
>
> **Quando** seleciona o atalho Este Mês no filtro Período
>
> **Então** o sistema preenche Data Inicial e Data Final com o primeiro
> e o último dia do mês e atualiza a pré-visualização

***Cenário 5: consulta pelo Professor da Disciplina (fluxo alternativo
C)***

> **Dado que** um Professor da Disciplina que não é Coordenador de Curso
> está autenticado
>
> **Quando** abre Horas complementares de ouvintes
>
> **Então** o relatório exibe os filtros de período, sem o filtro Curso

***Cenário 6: acesso sem estar autenticado (E1)***

> **Dado que** o usuário não está autenticado
>
> **Quando** tenta abrir a tela Relatórios
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre o relatório Horas complementares de ouvintes

***Cenário 7: intervalo de datas inválido (E2)***

> **Dado que** o usuário está na tela do relatório
>
> **Quando** informa a Data Inicial 30/11/2026 e a Data Final 01/11/2026
>
> **Então** o sistema não atualiza a pré-visualização e exibe "A data
> inicial não pode ser superior à data final"

***Cenário 8: nenhum registro para os filtros (E3)***

> **Dado que** não há dados para o período selecionado no relatório
> Horas complementares de ouvintes
>
> **Quando** o sistema atualiza a pré-visualização
>
> **Então** exibe a tabela vazia com a mensagem "Nenhum registro
> encontrado para os filtros selecionados"
>
> **E** os botões PDF, CSV e XLSX permanecem desabilitados

***Cenário 9: perfil sem acesso (E4)***

> **Dado que** o usuário autenticado é Docente e não é Coordenador de
> Curso nem Professor da Disciplina
>
> **Quando** abre a tela Relatórios
>
> **Então** o item Horas complementares de ouvintes não aparece na lista

**Tela no protótipo**

**Tela:** relatório sem tela no protótipo.

**Diagrama de sequência**

**Diagrama relacionado:** sem diagrama próprio: consulta de relatório
somente leitura, sem alteração de dados.

**Link:** não se aplica.

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)

## US-50 Prorrogar o acesso de membro externo

| **Épico:**                | Cadastro e Manutenção |
|---------------------------|-----------------------|
| **Feature:**              | Gestão de Contas      |
| **Requisitos da matriz:** | RBN-CAD-03.3          |
| **Prioridade (MoSCoW):**  | Could Have            |
| **Responsável:**          | Maria Luiza Nobre     |

**Descrição**

Como Orientador, quero prorrogar por mais 7 dias corridos o acesso de um
Membro Externo da banca do meu orientando, para que ele continue
acessando o sistema após o fim da validade da conta.

**Atores**

> **Ator principal:** Orientador do TCC cuja banca inclui o Membro
> Externo.
>
> **Atores secundários:** Professor da Disciplina da turma, Secretaria e
> Coordenador de Curso, que prorrogam pelo mesmo fluxo (fluxo
> alternativo C), e Membro Externo, que volta a fazer login com a conta
> Ativa.

**Pré-condições**

- O usuário está autenticado, com o Status da Conta Ativa (US-11). Sem
  > sessão ativa, aplica-se o E1.

- O usuário é Orientador do TCC cuja banca inclui o Membro Externo,
  > Professor da Disciplina da turma, Secretaria ou Coordenador de
  > Curso; caso contrário, aplica-se o E2.

- O Membro Externo está cadastrado (US-05), com o Status da Conta Ativa
  > ou Expirada; com a conta Aguardando Ativação, aplica-se o E3.

**Fluxo principal**

> 1\. No menu lateral do sistema, o Orientador seleciona o item Membros
> externos.
>
> 2\. O sistema abre a tela Membros externos e lista os membros com
> Nome, E-mail, Instituição de Origem, Status da Conta e validade do
> acesso, com o botão Prorrogar na linha dos membros da banca do
> orientando.
>
> 3\. O Orientador aciona o botão Prorrogar na linha de um membro com o
> Status da Conta Ativa.
>
> 4\. O sistema soma 7 dias corridos à validade atual e grava a nova
> validade (CAD-03.3).
>
> 5\. O sistema mantém o Orientador na tela Membros externos, exibe
> "Acesso prorrogado até DD/MM/AAAA" e atualiza a validade na linha do
> membro. O fluxo termina.

**Fluxos alternativos**

> A. Conta expirada (passo 3): o Orientador aciona o botão Prorrogar na
> linha de um membro com o Status da Conta Expirada. O sistema soma 7
> dias corridos a partir da data de hoje e muda o Status da Conta para
> Ativa, e o membro volta a fazer login com o mesmo e-mail e a mesma
> senha. O fluxo prossegue a partir do passo 5.
>
> B. Prorrogações sucessivas (passo 5): o Orientador aciona novamente o
> botão Prorrogar, e o sistema soma mais 7 dias corridos à validade
> vigente. O fluxo prossegue a partir do passo 5.
>
> C. Prorrogação pelo Professor da Disciplina, pela Secretaria ou pelo
> Coordenador de Curso (passo 1): o usuário segue os mesmos passos, e o
> sistema exibe o botão Prorrogar na linha dos membros externos. O fluxo
> prossegue a partir do passo 2.

**Fluxos de exceção**

> E1. Usuário não autenticado (passo 1): caso o usuário tente acessar a
> tela Membros externos sem sessão ativa (pelo menu, pelo endereço da
> página ou por um link recebido), o sistema apresenta a tela de login
> (US-11). Após a autenticação, o sistema exibe a tela Membros externos,
> e o fluxo prossegue a partir do passo 2. Em caso de falha na
> autenticação, aplicam-se as exceções da US-11.
>
> E2. Usuário sem permissão (passo 2): para o Aluno, para o Docente sem
> os papéis permitidos, para o Orientador sem vínculo com a banca do
> membro e para o próprio Membro Externo, o botão Prorrogar não aparece.
> Pelo endereço da ação, o sistema exibe "Você não tem permissão para
> esta ação" e não altera a validade. O fluxo termina.
>
> E3. Conta Aguardando Ativação (passo 2): o membro que ainda não criou
> a senha não tem validade a prorrogar, e o botão Prorrogar não aparece
> na sua linha. O fluxo termina.
>
> E4. Falha ao gravar a nova validade (passo 4): o sistema não consegue
> gravar a nova validade, exibe "Não foi possível prorrogar o acesso.
> Tente novamente" e mantém a validade anterior. Retorna ao passo 3.

**Pós-condições**

- A nova validade do acesso foi gravada, e o Status da Conta do membro
  > passou a Ativa ou permaneceu Ativa.

- O membro passou a fazer login com o mesmo e-mail e a mesma senha até a
  > nova validade.

- Os dados cadastrais e as participações em bancas foram mantidos no
  > histórico e nos relatórios.

- Em qualquer exceção, a validade anterior foi mantida.

**Regras aplicáveis**

| **RBN**      | **Requisito na matriz**                                                                                                                                                                                                       | **Resumo da regra em uma frase**                                                                                                                                                                                                                                                                              |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CAD-03.3** | O sistema deve permitir a manutenção do Status da Conta do Membro Externo, com os valores Aguardando Ativação, Ativa ou Expirada, expirando o acesso 7 dias após a defesa e permitindo a renovação ou a prorrogação da conta. | O Orientador do TCC, o Professor da Disciplina, a Secretaria ou o Coordenador de Curso pode prorrogar a validade da conta por mais 7 dias corridos, contados a partir da data de vencimento atual, caso esteja ativa, ou da data da prorrogação, caso esteja expirada, alterando o Status da Conta para Ativa |

**Critérios de aceite**

*Critérios do backlog (ponto de partida):*

> 1\. Permite prorrogação manual (botão).

***Cenário 1: prorrogação de conta vigente (fluxo principal, critério
1)***

> **Dado que** o Orientador está na tela Membros externos e a conta de
> um membro da banca do seu orientando vale até 27/10/2026
>
> **Quando** aciona o botão Prorrogar na linha desse membro
>
> **Então** a validade passa para 03/11/2026 e o sistema exibe "Acesso
> prorrogado até 03/11/2026"

***Cenário 2: prorrogação de conta expirada (fluxo alternativo A)***

> **Dado que** o Status da Conta do membro é Expirada desde 01/10/2026 e
> hoje é 06/10/2026
>
> **Quando** o Orientador aciona o botão Prorrogar
>
> **Então** a validade passa para 13/10/2026 e o Status da Conta volta a
> Ativa
>
> **E** o membro faz login com o mesmo e-mail e a mesma senha

***Cenário 3: prorrogações sucessivas (fluxo alternativo B)***

> **Dado que** a conta do membro vale até 27/10/2026
>
> **Quando** o Orientador aciona o botão Prorrogar duas vezes
>
> **Então** a validade passa para 10/11/2026

***Cenário 4: prorrogação pela Secretaria (fluxo alternativo C)***

> **Dado que** a Secretaria está autenticada e abre a tela Membros
> externos
>
> **Quando** aciona o botão Prorrogar na linha de um membro com a conta
> Ativa
>
> **Então** o sistema soma 7 dias corridos à validade e exibe a nova
> validade

***Cenário 5: acesso sem estar autenticado (E1)***

> **Dado que** o Orientador não está autenticado
>
> **Quando** tenta abrir a tela Membros externos
>
> **Então** o sistema exibe a tela de login (US-11)
>
> **E**, após o login, abre a tela Membros externos

***Cenário 6: Orientador sem vínculo com a banca (E2)***

> **Dado que** o Orientador não orienta o TCC da banca do membro
>
> **Quando** abre a tela Membros externos
>
> **Então** o botão Prorrogar não aparece na linha desse membro

***Cenário 7: acesso direto sem permissão (E2)***

> **Dado que** um Aluno está autenticado
>
> **Quando** abre o endereço da ação de prorrogar
>
> **Então** o sistema exibe "Você não tem permissão para esta ação" e
> não altera a validade

***Cenário 8: conta Aguardando Ativação (E3)***

> **Dado que** o membro ainda não criou a senha
>
> **Quando** o Orientador abre a tela Membros externos
>
> **Então** o botão Prorrogar não aparece na linha desse membro

***Cenário 9: falha ao gravar a nova validade (E4)***

> **Dado que** o Orientador acionou o botão Prorrogar
>
> **Quando** o sistema não consegue gravar a nova validade
>
> **Então** exibe "Não foi possível prorrogar o acesso. Tente novamente"
> e mantém a validade anterior

**Tela no protótipo**

**Tela:** Membros externos

**Diagrama de sequência**

**Diagrama relacionado:** sem diagrama próprio: ação simples sobre a
validade da conta; a regra de validade está na US-06.

**Link:** não se aplica.

**Pronta para desenvolver**

> \[x\] Descrição no formato Como, Quero, Para que
>
> \[x\] Requisitos da matriz conferidos
>
> \[x\] Fluxo principal e fluxos alternativos escritos
>
> \[x\] Atores, pré-condições e pós-condições preenchidos
>
> \[x\] Fluxos de exceção escritos
>
> \[x\] Um cenário para cada critério de aceite e para cada exceção
>
> \[ \] Tela do protótipo e diagrama de sequência indicados
>
> \[ \] Revisada por outra pessoa (nome: \_\_\_\_\_\_\_\_\_\_\_\_\_\_)
