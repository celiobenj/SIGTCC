**MODELO LÓGICO E DICIONÁRIO DE DADOS**

| **Nome do Projeto:**   | Sistema de Gestão de TCC do NUCOMP-UEA (SIGTCC)                                       |
|------------------------|---------------------------------------------------------------------------------------|
| **Instituição:**       | UEA – Universidade do Estado do Amazonas (NUCOMP)                                     |
| **Equipe do Projeto:** | Célio Benjamim, Julia Cohen, Leandra Matos, Maria Luísa Gomes, Maria Luiza Guimarães. |
| **Data:**              | 18/10/2026                                                                            |

# SUMÁRIO

[**SUMÁRIO 1**](#)

[**1. INTRODUÇÃO 3**](#introdução)

[**2. MODELO LÓGICO RELACIONAL 3**](#modelo-lógico-relacional)

[**3. DICIONÁRIO DE DADOS 4**](#dicionário-de-dados)

> [**3.1 Entidades Base e Domínios Fixos
> 4**](#entidades-base-e-domínios-fixos)
>
> [3.1.1 Tabela Cursos 4](#tabela-cursos)
>
> [3.1.2 Tabela Equivalencia_Cursos 5](#tabela-equivalencia_cursos)
>
> [3.1.3 Tabela Disciplinas 5](#tabela-disciplinas)
>
> [3.1.4 Tabela Criterios 5](#tabela-criterios)
>
> [3.1.5 Tabela Areas_Interesse 5](#tabela-areas_interesse)
>
> [3.1.6 Tabela Ouvintes 6](#tabela-ouvintes)
>
> [**3.2 Hierarquia de Usuários 6**](#hierarquia-de-usuários)
>
> [3.2.1 Tabela Usuarios 6](#tabela-usuarios)
>
> [3.2.2 Tabela Alunos 6](#tabela-alunos)
>
> [3.2.3 Tabela Docentes 7](#tabela-docentes)
>
> [3.2.4 Tabela MembrosExternos 7](#tabela-membrosexternos)
>
> [3.2.5 Tabela Secretarios 7](#tabela-secretarios)
>
> [3.2.6 Tabela CoorientadoresExternos
> 7](#tabela-coorientadoresexternos)
>
> [**3.3 Turmas, Matrículas e Histórico Acadêmico
> 8**](#turmas-matrículas-e-histórico-acadêmico)
>
> [3.3.1 Tabela Coordenadores 8](#tabela-coordenadores)
>
> [3.3.2 Tabela Turmas 8](#tabela-turmas)
>
> [3.3.3 Tabela Alunos_Turmas 8](#tabela-alunos_turmas)
>
> [3.3.4 Tabela Historico_Alunos_Turmas
> 9](#tabela-historico_alunos_turmas)
>
> [**3.4 Entregas e Atividades das Turmas
> 9**](#entregas-e-atividades-das-turmas)
>
> [3.4.1 Tabela Turmas_Marcos 9](#tabela-turmas_marcos)
>
> [3.4.2 Tabela Entregas_Marcos 9](#tabela-entregas_marcos)
>
> [3.4.3 Tabela Historico_Envios_Entregas
> 10](#tabela-historico_envios_entregas)
>
> [**3.5 TCC, Orientação e Publicações
> 10**](#tcc-orientação-e-publicações)
>
> [3.5.1 Tabela TCCs 10](#tabela-tccs)
>
> [3.5.2 Tabela Orientacoes 11](#tabela-orientacoes)
>
> [3.5.3 Tabela Coorientacoes 11](#tabela-coorientacoes)
>
> [3.5.4 Tabela PalavrasChave_TCC 12](#tabela-palavraschave_tcc)
>
> [3.5.5 Tabela Solicitacoes_Orientacao
> 12](#tabela-solicitacoes_orientacao)
>
> [3.5.6 Tabela Historico_Status_TCC 13](#tabela-historico_status_tcc)
>
> [3.5.7 Tabela Artigos 13](#tabela-artigos)
>
> [3.5.8 Tabela Encontro_Orientacao 14](#tabela-encontro_orientacao)
>
> [3.5.9 Tabela Comentarios_Encontro 14](#tabela-comentarios_encontro)
>
> [**3.6 Defesas, Banca, Avaliações e Atas
> 14**](#defesas-banca-avaliações-e-atas)
>
> [3.6.1 Tabela Defesas 14](#tabela-defesas)
>
> [3.6.2 Tabela Defesas_Presenciais 15](#tabela-defesas_presenciais)
>
> [3.6.3 Tabela Defesas_Remotas 15](#tabela-defesas_remotas)
>
> [3.6.4 Tabela Banca_Defesa 15](#tabela-banca_defesa)
>
> [3.6.5 Tabela Presenca_Ouvintes 16](#tabela-presenca_ouvintes)
>
> [3.6.6 Tabela Avaliacoes 16](#tabela-avaliacoes)
>
> [3.6.7 Tabela Historico_Defesas 16](#tabela-historico_defesas)
>
> [**3.7 Notificações 17**](#notificações)
>
> [3.7.1 Tabela Notificacoes 17](#tabela-notificacoes)

[**4. REGRAS ATENDIDAS FORA DO BANCO DE DADOS
17**](#regras-atendidas-fora-do-banco-de-dados)

# 1. INTRODUÇÃO

Este documento apresenta o modelo lógico relacional e o dicionário de
dados do Sistema de Gestão de TCC do NUCOMP-UEA (SIGTCC). O modelo foi
derivado da Matriz de Requisitos do SIGTCC e adota o PostgreSQL como
sistema gerenciador de banco de dados, em conformidade com a arquitetura
definida para o projeto (Python com Django e PostgreSQL).

A seção 2 apresenta o modelo lógico em notação textual. A seção 3
detalha cada tabela, com tipo, obrigatoriedade, chave e descrição de
cada campo, e as restrições de integridade. A seção 4 relaciona as
regras da matriz atendidas pela aplicação, sem estrutura própria no
banco.

# 2. MODELO LÓGICO RELACIONAL

**Convenção de chaves:** os campos em negrito e sublinhados compõem a
chave primária; a indicação \[FK Tabela.coluna\] identifica a chave
estrangeira simples, e a indicação \[FK Tabela(coluna1, coluna2)\]
identifica a chave estrangeira composta, registrada no último campo do
grupo.

**1. Cursos** (**<u>cur_id</u>**, cur_nome, cur_descricao)

**2. Equivalencia_Cursos** (**<u>eqc_codigo_uea</u>**, eqc_cur_id *\[FK
Cursos.cur_id\]*)

**3. Disciplinas** (**<u>dis_id</u>**, dis_codigo, dis_nome,
dis_descricao)

**4. Criterios** (**<u>cri_id</u>**, cri_nome, cri_componente,
cri_descricao, cri_desc_exemplar, cri_desc_competente,
cri_desc_necessita_trabalho, cri_peso)

**5. Areas_Interesse** (**<u>ari_id</u>**, ari_nome)

**6. Ouvintes** (**<u>ouv_id</u>**, ouv_matricula, ouv_nome)

**7. Usuarios** (**<u>usu_id</u>**, usu_nome, usu_email, usu_senha,
usu_status, usu_link_gerado_em)

**8. Alunos** (**<u>alu_id</u>** *\[FK Usuarios.usu_id\]*,
alu_matricula, alu_codigo_curso)

**9. Docentes** (**<u>doc_id</u>** *\[FK Usuarios.usu_id\]*,
doc_titulacao, doc_cur_id *\[FK Cursos.cur_id\]*, doc_assinatura_path)

**10. MembrosExternos** (**<u>mem_id</u>** *\[FK Usuarios.usu_id\]*,
mem_titulacao, mem_instituicao, mem_assinatura_path, mem_validade_ate)

**11. Secretarios** (**<u>sec_id</u>** *\[FK Usuarios.usu_id\]*,
sec_cur_id *\[FK Cursos.cur_id\]*)

**12. CoorientadoresExternos** (**<u>cext_id</u>**, cext_nome,
cext_email, cext_instituicao)

**13. Coordenadores** (**<u>cor_cur_id</u>** *\[FK Cursos.cur_id\]*,
cor_doc_id *\[FK Docentes.doc_id\]*)

**14. Turmas** (**<u>tur_id</u>**, tur_identificador, tur_descricao,
tur_doc_id *\[FK Docentes.doc_id\]*, tur_dis_id *\[FK
Disciplinas.dis_id\]*, tur_cur_id *\[FK Cursos.cur_id\]*, tur_ano,
tur_semestre, tur_dia_da_semana, tur_hora_inicio, tur_hora_termino,
tur_local, tur_status)

**15. Alunos_Turmas** (**<u>mat_alu_id</u>** *\[FK Alunos.alu_id\]*,
**<u>mat_tur_id</u>** *\[FK Turmas.tur_id\]*, mat_data_inscricao)

**16. Historico_Alunos_Turmas** (**<u>hat_id</u>**, hat_alu_id *\[FK
Alunos.alu_id\]*, hat_tur_origem_id *\[FK Turmas.tur_id\]*,
hat_tur_destino_id *\[FK Turmas.tur_id\]*, hat_tipo_evento,
hat_justificativa, hat_data_hora, hat_usu_id *\[FK Usuarios.usu_id\]*)

**17. Turmas_Marcos** (**<u>tma_id</u>**, tma_tur_id *\[FK
Turmas.tur_id\]*, tma_tipo, tma_titulo, tma_instrucao, tma_data_limite)

**18. Entregas_Marcos** (**<u>ent_id</u>**, ent_tma_id *\[FK
Turmas_Marcos.tma_id\]*, ent_alu_id *\[FK Alunos.alu_id\]*, ent_status,
ent_feedback, ent_data_avaliacao, ent_correcoes_conferidas_em)

**19. Historico_Envios_Entregas** (**<u>hen_id</u>**, hen_ent_id *\[FK
Entregas_Marcos.ent_id\]*, hen_link, hen_data_envio)

**20. TCCs** (**<u>tcc_id</u>**, tcc_alu_id *\[FK Alunos.alu_id\]*,
tcc_tur_id *\[FK Turmas.tur_id\]*, tcc_ari_id *\[FK
Areas_Interesse.ari_id\]*, tcc_modalidade, tcc_titulo, tcc_subtitulo,
tcc_resumo, tcc_link_proposta, tcc_status,
tcc_justificativa_encerramento)

**21. Orientacoes** (**<u>ori_id</u>**, ori_tcc_id *\[FK TCCs.tcc_id\]*,
ori_doc_id *\[FK Docentes.doc_id\]*, ori_origem, ori_status,
ori_data_inicio, ori_data_fim)

**22. Coorientacoes** (**<u>coo_id</u>**, coo_tcc_id *\[FK
TCCs.tcc_id\]*, coo_doc_id *\[FK Docentes.doc_id\]*, coo_cext_id *\[FK
CoorientadoresExternos.cext_id\]*, coo_status, coo_data_inicio,
coo_data_fim)

**23. PalavrasChave_TCC** (**<u>pal_tcc_id</u>** *\[FK TCCs.tcc_id\]*,
**<u>pal_palavra</u>**)

**24. Solicitacoes_Orientacao** (**<u>sol_id</u>**, sol_tcc_id *\[FK
TCCs.tcc_id\]*, sol_doc_id *\[FK Docentes.doc_id\]*, sol_tipo,
sol_status, sol_data_solicitacao, sol_data_resposta)

**25. Historico_Status_TCC** (**<u>hst_id</u>**, hst_tcc_id *\[FK
TCCs.tcc_id\]*, hst_tur_id *\[FK Turmas.tur_id\]*, hst_status_anterior,
hst_status_novo, hst_gatilho, hst_data_hora, hst_usu_id *\[FK
Usuarios.usu_id\]*)

**26. Artigos** (**<u>art_id</u>** *\[FK TCCs.tcc_id\]*,
art_veiculo_publicacao, art_link_doi, art_qualis_capes,
art_status_submissao, art_homologacao, art_homologado_por *\[FK
Usuarios.usu_id\]*, art_data_homologacao)

**27. Encontro_Orientacao** (**<u>enc_id</u>**, enc_tcc_id *\[FK
TCCs.tcc_id\]*, enc_data, enc_pauta, enc_metas)

**28. Comentarios_Encontro** (**<u>com_id</u>**, com_enc_id *\[FK
Encontro_Orientacao.enc_id\]*, com_usu_id *\[FK Usuarios.usu_id\]*,
com_texto, com_data_hora)

**29. Defesas** (**<u>def_id</u>**, def_tcc_id *\[FK TCCs.tcc_id\]*,
def_data, def_h_inicio, def_formato, def_status, def_parecer,
def_nota_final, def_ocorrencias, def_data_liberacao_resultado,
def_ata_final_path, def_folha_aprovacao_path)

**30. Defesas_Presenciais** (**<u>dep_def_id</u>** *\[FK
Defesas.def_id\]*, dep_local)

**31. Defesas_Remotas** (**<u>der_def_id</u>** *\[FK Defesas.def_id\]*,
der_link)

**32. Banca_Defesa** (**<u>ban_def_id</u>** *\[FK Defesas.def_id\]*,
**<u>ban_usu_id</u>** *\[FK Usuarios.usu_id\]*, ban_papel,
ban_usu_substituido_id *\[FK Usuarios.usu_id\]*,
ban_justificativa_substituicao, ban_assinatura_path, ban_data_envio)

**33. Presenca_Ouvintes** (**<u>pre_def_id</u>** *\[FK
Defesas.def_id\]*, **<u>pre_ouv_id</u>** *\[FK Ouvintes.ouv_id\]*)

**34. Avaliacoes** (**<u>ava_def_id</u>**, **<u>ava_usu_id</u>** *\[FK
Banca_Defesa(ban_def_id, ban_usu_id)\]*, **<u>ava_cri_id</u>** *\[FK
Criterios.cri_id\]*, ava_conceito, ava_nota, ava_observacoes,
ava_data_hora)

**35. Historico_Defesas** (**<u>hdf_id</u>**, hdf_def_id *\[FK
Defesas.def_id\]*, hdf_evento, hdf_status_anterior, hdf_status_novo,
hdf_data_anterior, hdf_hora_anterior, hdf_data_nova, hdf_hora_nova,
hdf_membro_removido_id *\[FK Usuarios.usu_id\]*, hdf_membro_incluido_id
*\[FK Usuarios.usu_id\]*, hdf_justificativa, hdf_data_hora, hdf_usu_id
*\[FK Usuarios.usu_id\]*)

**36. Notificacoes** (**<u>not_id</u>**, not_usu_id *\[FK
Usuarios.usu_id\]*, not_mensagem, not_link_tela, not_data_hora,
not_lida)

# 3. DICIONÁRIO DE DADOS

Os identificadores descritos como GENERATED ALWAYS AS IDENTITY são
gerados pelo banco. Na coluna Chave, PK indica chave primária, FK indica
chave estrangeira e AK indica chave alternativa (valor único). Os
valores entre aspas na descrição formam o domínio do campo e são
garantidos por restrição CHECK.

## 3.1 Entidades Base e Domínios Fixos

### 3.1.1 Tabela Cursos

| **Campo**     | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                      |
|---------------|--------------|-----------|-----------|----------------------------------------------------|
| cur_id        | INT          | Não       | PK        | Identificador único (GENERATED ALWAYS AS IDENTITY) |
| cur_nome      | VARCHAR(100) | Não       | \-        | Nome oficial do curso de graduação no NUCOMP       |
| cur_descricao | VARCHAR(255) | Sim       | \-        | Descrição detalhada sobre o curso                  |

### 3.1.2 Tabela Equivalencia_Cursos

| **Campo**      | **Tipo**    | **Nulo?** | **Chave** | **Descrição**                                 |
|----------------|-------------|-----------|-----------|-----------------------------------------------|
| eqc_codigo_uea | VARCHAR(20) | Não       | PK        | Código do curso na UEA (ex.: EST08MCPD)       |
| eqc_cur_id     | INT         | Não       | FK        | Referência ao curso do NUCOMP (Cursos.cur_id) |

### 3.1.3 Tabela Disciplinas

| **Campo**     | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                                   |
|---------------|--------------|-----------|-----------|-----------------------------------------------------------------|
| dis_id        | INT          | Não       | PK        | Identificador único (GENERATED ALWAYS AS IDENTITY)              |
| dis_codigo    | VARCHAR(20)  | Não       | AK        | Código da disciplina de TCC                                     |
| dis_nome      | VARCHAR(100) | Sim       | \-        | Nome da disciplina (opcional; o cadastro exige apenas o código) |
| dis_descricao | VARCHAR(255) | Sim       | \-        | Ementa ou descrição complementar da disciplina                  |

### 3.1.4 Tabela Criterios

| **Campo**                   | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                                       |
|-----------------------------|--------------|-----------|-----------|---------------------------------------------------------------------|
| cri_id                      | INT          | Não       | PK        | Identificador do critério (GENERATED ALWAYS AS IDENTITY)            |
| cri_nome                    | VARCHAR(100) | Não       | \-        | Nome do critério de avaliação                                       |
| cri_componente              | VARCHAR(20)  | Não       | \-        | Componente da avaliação ('Parte Escrita', 'Parte Oral')             |
| cri_descricao               | VARCHAR(255) | Sim       | \-        | Descrição do objetivo do critério                                   |
| cri_desc_exemplar           | VARCHAR(255) | Não       | \-        | Descritor exigido para o conceito Exemplar                          |
| cri_desc_competente         | VARCHAR(255) | Não       | \-        | Descritor exigido para o conceito Competente                        |
| cri_desc_necessita_trabalho | VARCHAR(255) | Não       | \-        | Descritor exigido para o conceito Necessita de Trabalho             |
| cri_peso                    | DECIMAL(3,1) | Não       | \-        | Peso do critério no cálculo (faixa de 0.0 a 10.0, uma casa decimal) |

### 3.1.5 Tabela Areas_Interesse

| **Campo** | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                      |
|-----------|--------------|-----------|-----------|----------------------------------------------------|
| ari_id    | INT          | Não       | PK        | Identificador único (GENERATED ALWAYS AS IDENTITY) |
| ari_nome  | VARCHAR(100) | Não       | AK        | Uma das 10 áreas fixas de interesse do NUCOMP/UEA  |

### 3.1.6 Tabela Ouvintes

| **Campo**     | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                      |
|---------------|--------------|-----------|-----------|----------------------------------------------------|
| ouv_id        | INT          | Não       | PK        | Identificador único (GENERATED ALWAYS AS IDENTITY) |
| ouv_matricula | CHAR(10)     | Não       | AK        | Matrícula com exatamente 10 dígitos numéricos      |
| ouv_nome      | VARCHAR(150) | Não       | \-        | Nome completo do ouvinte (até 150 caracteres)      |

## 3.2 Hierarquia de Usuários

### 3.2.1 Tabela Usuarios

| **Campo**          | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                                                                                                                                               |
|--------------------|--------------|-----------|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| usu_id             | INT          | Não       | PK        | Identificador do usuário (GENERATED ALWAYS AS IDENTITY)                                                                                                                     |
| usu_nome           | VARCHAR(150) | Não       | \-        | Nome completo (até 150 caracteres)                                                                                                                                          |
| usu_email          | VARCHAR(100) | Sim       | AK        | Endereço de e-mail único do usuário (institucional; o Membro Externo pode usar qualquer domínio). Nulo para o Aluno até o primeiro acesso e após o reset do primeiro acesso |
| usu_senha          | VARCHAR(255) | Sim       | \-        | Hash da senha de acesso (entrada de 8 a 64 caracteres). Nulo enquanto a conta estiver 'Aguardando Ativação' e após o reset do primeiro acesso                               |
| usu_status         | VARCHAR(30)  | Não       | \-        | Status da conta ('Aguardando Ativação', 'Ativa', 'Inativa', 'Expirada')                                                                                                     |
| usu_link_gerado_em | TIMESTAMP    | Sim       | \-        | Data e hora de geração do último link de ativação ou de redefinição de senha; compõe o token assinado, de modo que cada novo link invalida o anterior                       |

**Restrição:** UNIQUE (usu_email) quando usu_email não for nulo (vários
Alunos podem estar sem e-mail antes do primeiro acesso).

### 3.2.2 Tabela Alunos

| **Campo**        | **Tipo**    | **Nulo?** | **Chave** | **Descrição**                                            |
|------------------|-------------|-----------|-----------|----------------------------------------------------------|
| alu_id           | INT         | Não       | PK / FK   | Referência a Usuarios(usu_id)                            |
| alu_matricula    | CHAR(10)    | Não       | AK        | Matrícula acadêmica de exatamente 10 dígitos numéricos   |
| alu_codigo_curso | VARCHAR(20) | Não       | \-        | Código informado no cadastro (validado via equivalência) |

### 3.2.3 Tabela Docentes

| **Campo**           | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                                                                                                                                     |
|---------------------|--------------|-----------|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| doc_id              | INT          | Não       | PK / FK   | Referência a Usuarios(usu_id)                                                                                                                                     |
| doc_titulacao       | VARCHAR(20)  | Não       | \-        | Titulação acadêmica ('Especialista', 'Mestre', 'Doutor')                                                                                                          |
| doc_cur_id          | INT          | Não       | FK        | Curso de Lotação (Cursos.cur_id)                                                                                                                                  |
| doc_assinatura_path | VARCHAR(255) | Sim       | \-        | Caminho da imagem de assinatura do perfil (PNG ou JPG, até 2 MB), reutilizável na avaliação da banca e usada na Ata Final quando o docente é Coordenador de Curso |

### 3.2.4 Tabela MembrosExternos

| **Campo**           | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                                                                                                                                                                       |
|---------------------|--------------|-----------|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| mem_id              | INT          | Não       | PK / FK   | Referência a Usuarios(usu_id)                                                                                                                                                                       |
| mem_titulacao       | VARCHAR(20)  | Não       | \-        | Titulação acadêmica ('Especialista', 'Mestre', 'Doutor')                                                                                                                                            |
| mem_instituicao     | VARCHAR(150) | Não       | \-        | Instituição de Origem (até 150 caracteres)                                                                                                                                                          |
| mem_assinatura_path | VARCHAR(255) | Sim       | \-        | Caminho da imagem de assinatura do perfil (PNG ou JPG, até 2 MB), reutilizável na avaliação da banca                                                                                                |
| mem_validade_ate    | DATE         | Sim       | \-        | Data final de validade da conta: 7 dias corridos após a defesa mais distante em que o membro está vinculado, ou a data resultante da prorrogação manual. Nulo enquanto não houver vínculo com banca |

### 3.2.5 Tabela Secretarios

| **Campo**  | **Tipo** | **Nulo?** | **Chave** | **Descrição**                   |
|------------|----------|-----------|-----------|---------------------------------|
| sec_id     | INT      | Não       | PK / FK   | Referência a Usuarios(usu_id)   |
| sec_cur_id | INT      | Não       | FK        | Curso Vinculado (Cursos.cur_id) |

**Restrição:** Uma Secretaria com Status da Conta 'Ativa' por curso.
Como o status pertence a Usuarios, a regra é garantida por validação na
aplicação.

### 3.2.6 Tabela CoorientadoresExternos

| **Campo**        | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                                                                                                   |
|------------------|--------------|-----------|-----------|---------------------------------------------------------------------------------------------------------------------------------|
| cext_id          | INT          | Não       | PK        | Identificador único (GENERATED ALWAYS AS IDENTITY)                                                                              |
| cext_nome        | VARCHAR(150) | Não       | \-        | Nome completo (até 150 caracteres)                                                                                              |
| cext_email       | VARCHAR(100) | Sim       | AK        | Endereço de e-mail opcional (único quando informado); quando informado, o registro existente com o mesmo e-mail é reaproveitado |
| cext_instituicao | VARCHAR(150) | Sim       | \-        | Instituição de Origem opcional (até 150 caracteres)                                                                             |

**Restrição:** UNIQUE (cext_email) quando cext_email não for nulo. A
proibição de repetir o coorientador no mesmo trabalho fica em
Coorientacoes.

## 3.3 Turmas, Matrículas e Histórico Acadêmico

### 3.3.1 Tabela Coordenadores

| **Campo**  | **Tipo** | **Nulo?** | **Chave** | **Descrição**                                                                 |
|------------|----------|-----------|-----------|-------------------------------------------------------------------------------|
| cor_cur_id | INT      | Não       | PK / FK   | Curso coordenado (Cursos.cur_id); um Coordenador de Curso por curso           |
| cor_doc_id | INT      | Não       | AK / FK   | Docente coordenador (Docentes.doc_id); um docente coordena no máximo um curso |

### 3.3.2 Tabela Turmas

| **Campo**         | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                                                                           |
|-------------------|--------------|-----------|-----------|---------------------------------------------------------------------------------------------------------|
| tur_id            | INT          | Não       | PK        | Identificador único (GENERATED ALWAYS AS IDENTITY)                                                      |
| tur_identificador | VARCHAR(30)  | Não       | AK        | Código da turma (até 30 caracteres, ex.: ECP06_T01)                                                     |
| tur_descricao     | VARCHAR(10)  | Não       | \-        | Descrição ('TCC 1' ou 'TCC 2')                                                                          |
| tur_doc_id        | INT          | Não       | FK        | Professor da Disciplina responsável pela turma                                                          |
| tur_dis_id        | INT          | Não       | FK        | Disciplina associada                                                                                    |
| tur_cur_id        | INT          | Não       | FK        | Curso associado                                                                                         |
| tur_ano           | INT          | Não       | \-        | Ano letivo (exatamente 4 dígitos)                                                                       |
| tur_semestre      | INT          | Não       | \-        | Semestre letivo (1 ou 2)                                                                                |
| tur_dia_da_semana | VARCHAR(20)  | Não       | \-        | Dia da semana ('segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado') |
| tur_hora_inicio   | TIME         | Não       | \-        | Horário de início das aulas                                                                             |
| tur_hora_termino  | TIME         | Não       | \-        | Horário de término das aulas                                                                            |
| tur_local         | VARCHAR(100) | Não       | \-        | Local da aula (até 100 caracteres)                                                                      |
| tur_status        | VARCHAR(20)  | Não       | \-        | Estado de vigência da turma ('Ativa' ou 'Arquivada')                                                    |

**Restrição:** CHECK (tur_hora_termino \> tur_hora_inicio).

### 3.3.3 Tabela Alunos_Turmas

| **Campo**          | **Tipo**  | **Nulo?** | **Chave** | **Descrição**                      |
|--------------------|-----------|-----------|-----------|------------------------------------|
| mat_alu_id         | INT       | Não       | PK / FK   | Referência a Alunos(alu_id)        |
| mat_tur_id         | INT       | Não       | PK / FK   | Referência a Turmas(tur_id)        |
| mat_data_inscricao | TIMESTAMP | Não       | \-        | Data e hora do vínculo com a turma |

### 3.3.4 Tabela Historico_Alunos_Turmas

| **Campo**          | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                        |
|--------------------|--------------|-----------|-----------|------------------------------------------------------|
| hat_id             | INT          | Não       | PK        | Identificador (GENERATED ALWAYS AS IDENTITY)         |
| hat_alu_id         | INT          | Não       | FK        | Referência ao aluno movimentado                      |
| hat_tur_origem_id  | INT          | Não       | FK        | Turma de origem da movimentação                      |
| hat_tur_destino_id | INT          | Sim       | FK        | Turma de destino (preenchido em transferências)      |
| hat_tipo_evento    | VARCHAR(20)  | Não       | \-        | Tipo da movimentação ('Exclusão' ou 'Transferência') |
| hat_justificativa  | VARCHAR(500) | Não       | \-        | Justificativa do evento (até 500 caracteres)         |
| hat_data_hora      | TIMESTAMP    | Não       | \-        | Data e hora do registro do evento                    |
| hat_usu_id         | INT          | Não       | FK        | Usuário autor do registro da movimentação            |

## 3.4 Entregas e Atividades das Turmas

### 3.4.1 Tabela Turmas_Marcos

| **Campo**       | **Tipo**      | **Nulo?** | **Chave** | **Descrição**                                                                  |
|-----------------|---------------|-----------|-----------|--------------------------------------------------------------------------------|
| tma_id          | INT           | Não       | PK        | Identificador (GENERATED ALWAYS AS IDENTITY)                                   |
| tma_tur_id      | INT           | Não       | FK        | Referência a Turmas(tur_id)                                                    |
| tma_tipo        | VARCHAR(30)   | Não       | \-        | Tipo da entrega ('Proposta', 'Documento para Defesa', 'Versão Final', 'Outra') |
| tma_titulo      | VARCHAR(100)  | Não       | \-        | Título da atividade (até 100 caracteres)                                       |
| tma_instrucao   | VARCHAR(1000) | Sim       | \-        | Instruções para realização (até 1000 caracteres)                               |
| tma_data_limite | TIMESTAMP     | Não       | \-        | Data e hora limite do prazo (válido até 23:59)                                 |

**Restrição:** UNIQUE (tma_tur_id, tma_tipo) quando tma_tipo \<\>
'Outra' (índice único parcial): uma entrega de cada tipo por turma,
exceto 'Outra', que pode se repetir.

### 3.4.2 Tabela Entregas_Marcos

| **Campo**                   | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                                                                                                               |
|-----------------------------|--------------|-----------|-----------|---------------------------------------------------------------------------------------------------------------------------------------------|
| ent_id                      | INT          | Não       | PK        | Identificador (GENERATED ALWAYS AS IDENTITY)                                                                                                |
| ent_tma_id                  | INT          | Não       | FK        | Referência a Turmas_Marcos(tma_id)                                                                                                          |
| ent_alu_id                  | INT          | Não       | FK        | Referência a Alunos(alu_id)                                                                                                                 |
| ent_status                  | VARCHAR(30)  | Não       | \-        | Status da entrega ('Aguardando Envio', 'Entregue', 'Entregue com Atraso', 'Não Entregue', 'Devolvida para Ajuste', 'Homologada')            |
| ent_feedback                | VARCHAR(500) | Sim       | \-        | Mensagem da devolução para ajuste mais recente (até 500 caracteres)                                                                         |
| ent_data_avaliacao          | TIMESTAMP    | Sim       | \-        | Data e hora da homologação ou da devolução mais recente                                                                                     |
| ent_correcoes_conferidas_em | TIMESTAMP    | Sim       | \-        | Data e hora em que o Orientador confirmou 'Correções Conferidas' na Versão Final (Sistemas de Informação, parecer 'Aprovado com Correções') |

**Restrição:** UNIQUE (ent_tma_id, ent_alu_id): uma entrega por aluno
por atividade.

**Restrição:** Em turma de Sistemas de Informação, com parecer 'Aprovado
com Correções', a homologação da Versão Final exige
ent_correcoes_conferidas_em preenchido (validação na aplicação).

### 3.4.3 Tabela Historico_Envios_Entregas

| **Campo**      | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                 |
|----------------|--------------|-----------|-----------|-----------------------------------------------|
| hen_id         | INT          | Não       | PK        | Identificador (GENERATED ALWAYS AS IDENTITY)  |
| hen_ent_id     | INT          | Não       | FK        | Referência a Entregas_Marcos(ent_id)          |
| hen_link       | VARCHAR(500) | Não       | \-        | URL do arquivo submetido (até 500 caracteres) |
| hen_data_envio | TIMESTAMP    | Não       | \-        | Data e hora exata do envio ou da substituição |

## 3.5 TCC, Orientação e Publicações

### 3.5.1 Tabela TCCs

| **Campo**                      | **Tipo**      | **Nulo?** | **Chave** | **Descrição**                                                                                                                                                                            |
|--------------------------------|---------------|-----------|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| tcc_id                         | INT           | Não       | PK        | Identificador único (GENERATED ALWAYS AS IDENTITY)                                                                                                                                       |
| tcc_alu_id                     | INT           | Não       | FK        | Referência ao aluno autor do trabalho                                                                                                                                                    |
| tcc_tur_id                     | INT           | Não       | FK        | Turma atual do TCC; na transferência para TCC 2, a mesma linha passa a referenciar a nova turma                                                                                          |
| tcc_ari_id                     | INT           | Sim       | FK        | Área de interesse acadêmica selecionada                                                                                                                                                  |
| tcc_modalidade                 | VARCHAR(30)   | Sim       | \-        | Modalidade do trabalho ('Monografia' ou 'Artigo Científico'); obrigatória a partir de 'Em Andamento'                                                                                     |
| tcc_titulo                     | VARCHAR(250)  | Sim       | \-        | Título principal (até 250 caracteres); obrigatório a partir de 'Em Andamento'                                                                                                            |
| tcc_subtitulo                  | VARCHAR(250)  | Sim       | \-        | Subtítulo do trabalho (até 250 caracteres)                                                                                                                                               |
| tcc_resumo                     | VARCHAR(1000) | Sim       | \-        | Resumo do trabalho de conclusão (até 1000 caracteres); obrigatório a partir de 'Em Andamento'                                                                                            |
| tcc_link_proposta              | VARCHAR(500)  | Sim       | \-        | Link do documento da proposta (até 500 caracteres)                                                                                                                                       |
| tcc_status                     | VARCHAR(50)   | Não       | \-        | Status do trabalho ('Sem Proposta', 'Em Andamento', 'Apto para Defesa', 'Aprovado para TCC 2', 'Aprovado', 'Aprovado com Correções', 'Concluído', 'Reprovado', 'Desistente', 'Jubilado') |
| tcc_justificativa_encerramento | VARCHAR(500)  | Sim       | \-        | Motivo do encerramento precoce do trabalho (até 500 caracteres)                                                                                                                          |

**Restrição:** CHECK condicionado a tcc_status: tcc_titulo, tcc_resumo e
tcc_modalidade são obrigatórios a partir de 'Em Andamento'. Em 'Sem
Proposta' a linha já existe, e esses três campos podem ficar nulos.

**Restrição:** UNIQUE (tcc_alu_id, tcc_tur_id): no máximo uma Proposta
por aluno em cada turma. O aluno reprovado, desistente ou jubilado
inicia um novo TCC na nova turma.

**Restrição:** O orientador atual do TCC é obtido em Orientacoes, no
vínculo com ori_status 'Ativa'.

### 3.5.2 Tabela Orientacoes

| **Campo**       | **Tipo**    | **Nulo?** | **Chave** | **Descrição**                                                                                                                                 |
|-----------------|-------------|-----------|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| ori_id          | INT         | Não       | PK        | Identificador (GENERATED ALWAYS AS IDENTITY)                                                                                                  |
| ori_tcc_id      | INT         | Não       | FK        | Referência ao TCC                                                                                                                             |
| ori_doc_id      | INT         | Não       | FK        | Docente orientador                                                                                                                            |
| ori_origem      | VARCHAR(20) | Não       | \-        | Origem do vínculo ('Pedido Aceito' ou 'Automático', este último nas turmas de TCC 2 de Engenharia de Computação e Licenciatura em Computação) |
| ori_status      | VARCHAR(20) | Não       | \-        | Estado do vínculo ('Ativa' ou 'Encerrada')                                                                                                    |
| ori_data_inicio | TIMESTAMP   | Não       | \-        | Data e hora de início do vínculo                                                                                                              |
| ori_data_fim    | TIMESTAMP   | Sim       | \-        | Data e hora de encerramento do vínculo (troca de orientador ou transferência de turma)                                                        |

**Restrição:** UNIQUE (ori_tcc_id) quando ori_status = 'Ativa' (índice
único parcial): no máximo um orientador ativo por TCC. Os vínculos
encerrados formam o histórico de orientação.

### 3.5.3 Tabela Coorientacoes

| **Campo**       | **Tipo**    | **Nulo?** | **Chave** | **Descrição**                                           |
|-----------------|-------------|-----------|-----------|---------------------------------------------------------|
| coo_id          | INT         | Não       | PK        | Identificador (GENERATED ALWAYS AS IDENTITY)            |
| coo_tcc_id      | INT         | Não       | FK        | Referência ao TCC                                       |
| coo_doc_id      | INT         | Sim       | FK        | Docente coorientador (mutuamente exclusivo com externo) |
| coo_cext_id     | INT         | Sim       | FK        | Coorientador externo (mutuamente exclusivo com docente) |
| coo_status      | VARCHAR(20) | Não       | \-        | Estado do vínculo ('Ativa', 'Substituída', 'Encerrada') |
| coo_data_inicio | TIMESTAMP   | Não       | \-        | Data e hora de início do vínculo                        |
| coo_data_fim    | TIMESTAMP   | Sim       | \-        | Data e hora de encerramento do vínculo                  |

**Restrição:** CHECK: exatamente um entre coo_doc_id e coo_cext_id é
preenchido.

**Restrição:** UNIQUE (coo_tcc_id, coo_doc_id) e UNIQUE (coo_tcc_id,
coo_cext_id) quando coo_status = 'Ativa' (índices únicos parciais): o
mesmo docente ou coorientador externo não é registrado duas vezes no
mesmo trabalho.

### 3.5.4 Tabela PalavrasChave_TCC

| **Campo**   | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                        |
|-------------|--------------|-----------|-----------|------------------------------------------------------|
| pal_tcc_id  | INT          | Não       | PK / FK   | Referência ao TCC vinculado                          |
| pal_palavra | VARCHAR(100) | Não       | PK        | Palavra-chave (até 100 caracteres; de 1 a 5 por TCC) |

### 3.5.5 Tabela Solicitacoes_Orientacao

| **Campo**            | **Tipo**    | **Nulo?** | **Chave** | **Descrição**                                                                                                                                                                                           |
|----------------------|-------------|-----------|-----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| sol_id               | INT         | Não       | PK        | Identificador (GENERATED ALWAYS AS IDENTITY)                                                                                                                                                            |
| sol_tcc_id           | INT         | Não       | FK        | Referência ao TCC                                                                                                                                                                                       |
| sol_doc_id           | INT         | Não       | FK        | Docente convidado                                                                                                                                                                                       |
| sol_tipo             | VARCHAR(20) | Não       | \-        | Tipo da solicitação ('Orientação', 'Troca de Orientação' ou 'Coorientação')                                                                                                                             |
| sol_status           | VARCHAR(20) | Não       | \-        | Estado da solicitação: em 'Orientação' e 'Troca de Orientação', 'Aguardando Resposta', 'Aceito', 'Recusado' ou 'Cancelado'; em 'Coorientação', 'Aguardando Aceite', 'Aceito', 'Recusado' ou 'Cancelado' |
| sol_data_solicitacao | TIMESTAMP   | Não       | \-        | Data e hora do envio do pedido                                                                                                                                                                          |
| sol_data_resposta    | TIMESTAMP   | Sim       | \-        | Data e hora da resposta do docente ou do cancelamento                                                                                                                                                   |

**Restrição:** CHECK condicionado a sol_tipo para os valores de
sol_status.

**Restrição:** UNIQUE (sol_tcc_id) quando sol_tipo em ('Orientação',
'Troca de Orientação') e sol_status = 'Aguardando Resposta' (índice
único parcial): um pedido de orientação pendente por TCC.

**Restrição:** Na confirmação do agendamento da defesa, o pedido 'Troca
de Orientação' com status 'Aguardando Resposta' passa a 'Cancelado'.

### 3.5.6 Tabela Historico_Status_TCC

| **Campo**           | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                                                                                                                                                                                  |
|---------------------|--------------|-----------|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| hst_id              | INT          | Não       | PK        | Identificador (GENERATED ALWAYS AS IDENTITY)                                                                                                                                                                   |
| hst_tcc_id          | INT          | Não       | FK        | Referência ao TCC                                                                                                                                                                                              |
| hst_tur_id          | INT          | Não       | FK        | Turma do TCC no momento da mudança; preserva o período letivo após a transferência para TCC 2                                                                                                                  |
| hst_status_anterior | VARCHAR(50)  | Sim       | \-        | Status anterior (nulo no primeiro registro, quando o novo status é 'Sem Proposta')                                                                                                                             |
| hst_status_novo     | VARCHAR(50)  | Não       | \-        | Novo status atribuído                                                                                                                                                                                          |
| hst_gatilho         | VARCHAR(100) | Não       | \-        | Gatilho da mudança ('Vínculo à turma', 'Proposta salva', 'Transferência para TCC 2', 'Indicação de Apto para Defesa', 'Liberação do resultado', 'Homologação da Versão Final', 'Encerramento da participação') |
| hst_data_hora       | TIMESTAMP    | Não       | \-        | Data e hora exata da alteração                                                                                                                                                                                 |
| hst_usu_id          | INT          | Não       | FK        | Usuário cuja ação disparou a mudança                                                                                                                                                                           |

### 3.5.7 Tabela Artigos

| **Campo**              | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                                                                                                        |
|------------------------|--------------|-----------|-----------|--------------------------------------------------------------------------------------------------------------------------------------|
| art_id                 | INT          | Não       | PK / FK   | Referência ao TCC (TCCs.tcc_id)                                                                                                      |
| art_veiculo_publicacao | VARCHAR(150) | Sim       | \-        | Veículo de publicação (até 150 caracteres)                                                                                           |
| art_link_doi           | VARCHAR(500) | Não       | \-        | Link/DOI obrigatório do artigo (até 500 caracteres)                                                                                  |
| art_qualis_capes       | VARCHAR(5)   | Sim       | \-        | Estrato Qualis ('A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'C')                                                                 |
| art_status_submissao   | VARCHAR(30)  | Sim       | \-        | Status de submissão ('Submetido', 'Em Revisão', 'Aceito', 'Publicado', 'Rejeitado')                                                  |
| art_homologacao        | VARCHAR(20)  | Sim       | \-        | Estado do aproveitamento ('Em Análise', 'Homologado', 'Recusado')                                                                    |
| art_homologado_por     | INT          | Sim       | FK        | Usuário responsável pela decisão mais recente (FK para Usuarios; a regra de que seja Coordenador de Curso é garantida por validação) |
| art_data_homologacao   | TIMESTAMP    | Sim       | \-        | Data e hora da decisão mais recente de homologação ou recusa                                                                         |

**Restrição:** A alteração de art_qualis_capes, art_status_submissao ou
art_link_doi em artigo já analisado retorna art_homologacao para 'Em
Análise'.

### 3.5.8 Tabela Encontro_Orientacao

| **Campo**  | **Tipo**      | **Nulo?** | **Chave** | **Descrição**                                              |
|------------|---------------|-----------|-----------|------------------------------------------------------------|
| enc_id     | INT           | Não       | PK        | Identificador (GENERATED ALWAYS AS IDENTITY)               |
| enc_tcc_id | INT           | Não       | FK        | Referência ao TCC                                          |
| enc_data   | DATE          | Não       | \-        | Data de realização da reunião (sem horário)                |
| enc_pauta  | VARCHAR(2000) | Não       | \-        | Pauta discutida no encontro (até 2000 caracteres)          |
| enc_metas  | VARCHAR(2000) | Não       | \-        | Metas acordadas para a próxima etapa (até 2000 caracteres) |

### 3.5.9 Tabela Comentarios_Encontro

| **Campo**     | **Tipo**      | **Nulo?** | **Chave** | **Descrição**                                        |
|---------------|---------------|-----------|-----------|------------------------------------------------------|
| com_id        | INT           | Não       | PK        | Identificador (GENERATED ALWAYS AS IDENTITY)         |
| com_enc_id    | INT           | Não       | FK        | Referência ao encontro de orientação                 |
| com_usu_id    | INT           | Não       | FK        | Autor do comentário (orientador ou coorientador)     |
| com_texto     | VARCHAR(1000) | Não       | \-        | Texto do comentário registrado (até 1000 caracteres) |
| com_data_hora | TIMESTAMP     | Não       | \-        | Data e hora do registro                              |

## 3.6 Defesas, Banca, Avaliações e Atas

### 3.6.1 Tabela Defesas

| **Campo**                    | **Tipo**      | **Nulo?** | **Chave** | **Descrição**                                                                                                                                       |
|------------------------------|---------------|-----------|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| def_id                       | INT           | Não       | PK        | Identificador (GENERATED ALWAYS AS IDENTITY)                                                                                                        |
| def_tcc_id                   | INT           | Não       | FK        | Referência ao TCC vinculado                                                                                                                         |
| def_data                     | DATE          | Não       | \-        | Data de realização da sessão de defesa                                                                                                              |
| def_h_inicio                 | TIME          | Não       | \-        | Horário de início da sessão                                                                                                                         |
| def_formato                  | VARCHAR(20)   | Não       | \-        | Formato da sessão ('Presencial' ou 'Remota')                                                                                                        |
| def_status                   | VARCHAR(30)   | Não       | \-        | Status da sessão ('Agendada', 'Em Andamento', 'Realizada', 'Reagendada', 'Cancelada')                                                               |
| def_parecer                  | VARCHAR(30)   | Sim       | \-        | Parecer final da banca ('Reprovado', 'Aprovado para TCC 2', 'Aprovado', 'Aprovado com Correções')                                                   |
| def_nota_final               | DECIMAL(3,1)  | Sim       | \-        | Nota final (0.0 a 10.0, uma casa decimal), gravada na liberação do resultado com a homologação de artigo vigente nesse momento                      |
| def_ocorrencias              | VARCHAR(2000) | Sim       | \-        | Registro de ocorrências da sessão de defesa (até 2000 caracteres)                                                                                   |
| def_data_liberacao_resultado | TIMESTAMP     | Sim       | \-        | Data e hora da liberação formal do resultado pelo Orientador                                                                                        |
| def_ata_final_path           | VARCHAR(255)  | Sim       | \-        | Caminho do PDF da Ata Final gerado na liberação do resultado, com a banca, as notas, as assinaturas e o Coordenador de Curso vigentes nesse momento |
| def_folha_aprovacao_path     | VARCHAR(255)  | Sim       | \-        | Caminho do PDF da Folha de Aprovação gerado na liberação do resultado (somente TCC 2, parecer 'Aprovado' ou 'Aprovado com Correções')               |

**Restrição:** A aplicação da nota mínima por artigo homologado (Qualis
A ou B) é derivada: ocorre quando a média das três notas, bloqueadas
após a liberação, é menor que 6,0 e def_nota_final é 6,0.

### 3.6.2 Tabela Defesas_Presenciais

| **Campo**  | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                           |
|------------|--------------|-----------|-----------|---------------------------------------------------------|
| dep_def_id | INT          | Não       | PK / FK   | Referência a Defesas(def_id)                            |
| dep_local  | VARCHAR(100) | Não       | \-        | Sala ou auditório da sessão física (até 100 caracteres) |

### 3.6.3 Tabela Defesas_Remotas

| **Campo**  | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                                 |
|------------|--------------|-----------|-----------|---------------------------------------------------------------|
| der_def_id | INT          | Não       | PK / FK   | Referência a Defesas(def_id)                                  |
| der_link   | VARCHAR(500) | Não       | \-        | Link da sala virtual de videoconferência (até 500 caracteres) |

### 3.6.4 Tabela Banca_Defesa

| **Campo**                      | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                                                                                                                 |
|--------------------------------|--------------|-----------|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| ban_def_id                     | INT          | Não       | PK / FK   | Referência a Defesas(def_id)                                                                                                                  |
| ban_usu_id                     | INT          | Não       | PK / FK   | Integrante da banca examinadora (Usuarios.usu_id; a regra de que seja Docente ou Membro Externo é garantida por validação)                    |
| ban_papel                      | VARCHAR(30)  | Não       | \-        | Papel na banca ('Orientador (Presidente)', '1º Avaliador', '2º Avaliador', 'Suplente')                                                        |
| ban_usu_substituido_id         | INT          | Sim       | FK        | Membro da banca que foi substituído pelo suplente                                                                                             |
| ban_justificativa_substituicao | VARCHAR(500) | Sim       | \-        | Justificativa do acionamento do suplente (até 500 caracteres)                                                                                 |
| ban_assinatura_path            | VARCHAR(255) | Sim       | \-        | Cópia da imagem de assinatura usada no envio da avaliação (anexada ou reutilizada do perfil), mantida para a Ata Final e a Folha de Aprovação |
| ban_data_envio                 | TIMESTAMP    | Sim       | \-        | Data e hora do envio final da avaliação com a assinatura; nulo enquanto a avaliação não for enviada                                           |

**Restrição:** O estado da avaliação de cada membro é derivado: 'Não
Avaliou' quando não há linhas em Avaliacoes; 'Rascunho' quando há linhas
e ban_data_envio é nulo; 'Enviada' quando ban_data_envio está
preenchido.

### 3.6.5 Tabela Presenca_Ouvintes

| **Campo**  | **Tipo** | **Nulo?** | **Chave** | **Descrição**                 |
|------------|----------|-----------|-----------|-------------------------------|
| pre_def_id | INT      | Não       | PK / FK   | Referência a Defesas(def_id)  |
| pre_ouv_id | INT      | Não       | PK / FK   | Referência a Ouvintes(ouv_id) |

### 3.6.6 Tabela Avaliacoes

| **Campo**       | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                                          |
|-----------------|--------------|-----------|-----------|------------------------------------------------------------------------|
| ava_def_id      | INT          | Não       | PK / FK   | Componente PK que identifica a defesa da banca                         |
| ava_usu_id      | INT          | Não       | PK / FK   | Componente PK que identifica o avaliador da banca                      |
| ava_cri_id      | INT          | Não       | PK / FK   | Referência a Criterios(cri_id)                                         |
| ava_conceito    | VARCHAR(30)  | Não       | \-        | Conceito atribuído ('Exemplar', 'Competente', 'Necessita de Trabalho') |
| ava_nota        | DECIMAL(3,1) | Não       | \-        | Nota numérica atribuída (0.0 a 10.0, uma casa decimal)                 |
| ava_observacoes | VARCHAR(500) | Sim       | \-        | Observações adicionais do avaliador (até 500 caracteres)               |
| ava_data_hora   | TIMESTAMP    | Não       | \-        | Data e hora do registro da pontuação                                   |

### 3.6.7 Tabela Historico_Defesas

| **Campo**              | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                                                                                                                                      |
|------------------------|--------------|-----------|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| hdf_id                 | INT          | Não       | PK        | Identificador (GENERATED ALWAYS AS IDENTITY)                                                                                                                       |
| hdf_def_id             | INT          | Não       | FK        | Referência a Defesas(def_id)                                                                                                                                       |
| hdf_evento             | VARCHAR(30)  | Não       | \-        | Evento registrado ('Agendamento', 'Reagendamento', 'Cancelamento', 'Início Automático', 'Acionamento do Suplente', 'Alteração da Banca', 'Liberação do Resultado') |
| hdf_status_anterior    | VARCHAR(30)  | Sim       | \-        | Status da sessão antes do evento (nulo no primeiro registro, quando o novo status é 'Agendada')                                                                    |
| hdf_status_novo        | VARCHAR(30)  | Sim       | \-        | Novo status da sessão; nulo nos eventos que não alteram o status (acionamento do suplente e alteração da banca)                                                    |
| hdf_data_anterior      | DATE         | Sim       | \-        | Data da sessão antes do reagendamento                                                                                                                              |
| hdf_hora_anterior      | TIME         | Sim       | \-        | Horário da sessão antes do reagendamento                                                                                                                           |
| hdf_data_nova          | DATE         | Sim       | \-        | Data da sessão definida no agendamento ou no reagendamento                                                                                                         |
| hdf_hora_nova          | TIME         | Sim       | \-        | Horário da sessão definido no agendamento ou no reagendamento                                                                                                      |
| hdf_membro_removido_id | INT          | Sim       | FK        | Membro retirado da banca (alteração da banca)                                                                                                                      |
| hdf_membro_incluido_id | INT          | Sim       | FK        | Membro incluído na banca (alteração da banca)                                                                                                                      |
| hdf_justificativa      | VARCHAR(500) | Sim       | \-        | Justificativa do evento (até 500 caracteres); obrigatória no reagendamento, no cancelamento e na alteração da banca                                                |
| hdf_data_hora          | TIMESTAMP    | Não       | \-        | Data e hora do evento                                                                                                                                              |
| hdf_usu_id             | INT          | Sim       | FK        | Usuário responsável pelo evento; nulo no início automático da sessão                                                                                               |

**Restrição:** A nota final e o parecer do evento de liberação são lidos
de Defesas, que ficam bloqueados após a liberação.

## 3.7 Notificações

### 3.7.1 Tabela Notificacoes

| **Campo**     | **Tipo**     | **Nulo?** | **Chave** | **Descrição**                                                            |
|---------------|--------------|-----------|-----------|--------------------------------------------------------------------------|
| not_id        | INT          | Não       | PK        | Identificador (GENERATED ALWAYS AS IDENTITY)                             |
| not_usu_id    | INT          | Não       | FK        | Usuário destinatário da notificação                                      |
| not_mensagem  | VARCHAR(500) | Não       | \-        | Texto exibido na central de notificações (até 500 caracteres)            |
| not_link_tela | VARCHAR(255) | Sim       | \-        | Endereço da tela relacionada, para acesso direto a partir da notificação |
| not_data_hora | TIMESTAMP    | Não       | \-        | Data e hora da criação da notificação                                    |
| not_lida      | BOOLEAN      | Não       | \-        | Indica se a notificação foi marcada como lida (padrão: falso)            |

**Restrição:** O envio por e-mail das notificações é feito pela
aplicação e não é armazenado.

# 4. REGRAS ATENDIDAS FORA DO BANCO DE DADOS

As regras abaixo são atendidas pela aplicação ou por recursos do
framework Django, sem estrutura própria no modelo lógico. A relação é
mantida para garantir a rastreabilidade entre a matriz de requisitos e o
banco de dados.

| **Nº** | **Regra da matriz**                                                                                                                                                                            | **Mecanismo**                                                                                                                                 |
|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| 1      | Bloqueio do acesso por 15 minutos após 3 tentativas de senha incorretas                                                                                                                        | Controle em cache com expiração automática (biblioteca de controle de tentativas de login, como django-axes).                                 |
| 2      | Links de ativação e de redefinição de senha válidos por 24 horas, com invalidação do link anterior                                                                                             | Tokens assinados do Django com validade de 24 horas, calculados com usu_link_gerado_em; um novo link altera esse valor e invalida o anterior. |
| 3      | Troca de e-mail concluída somente após confirmação no novo endereço                                                                                                                            | Token assinado que contém o novo e-mail; usu_email só é atualizado após a confirmação.                                                        |
| 4      | Código de validação único na declaração de participação em banca                                                                                                                               | Código assinado gerado a partir da defesa e do membro, verificável sem armazenamento.                                                         |
| 5      | Registro de autor, data e hora na exclusão de turma, na homologação e na devolução da Versão Final e na decisão de aproveitamento do artigo                                                    | Biblioteca de auditoria (como django-simple-history), que registra cada inclusão, alteração e exclusão com usuário, data e hora.              |
| 6      | Lembretes de prazo 7 dias, 48 horas e 24 horas antes da Data Limite                                                                                                                            | Tarefa agendada que gera registros em Notificacoes e envia os e-mails, exceto em turmas arquivadas.                                           |
| 7      | Mudanças de estado por data: entrega para Não Entregue após a Data Limite, sessão para Em Andamento na data e no horário marcados, conta do Membro Externo para Expirada após mem_validade_ate | Tarefa agendada que aplica as mudanças e registra os eventos correspondentes (por exemplo, Início Automático em Historico_Defesas).           |
| 8      | Datas e horários válidos (data do encontro não futura, Data Limite não anterior ao cadastro, defesa posterior ao agendamento) e conflito de horário da banca                                   | Validação na aplicação antes da gravação.                                                                                                     |
| 9      | Tipo de entrega compatível com a turma (Proposta somente em TCC 1; Versão Final somente em TCC 2)                                                                                              | Validação na aplicação no cadastro da entrega, pois depende de tur_descricao.                                                                 |
| 10     | Composição da banca: membros entre Docentes com conta Ativa e Membros Externos; Orientador e coorientadores fora da lista de avaliadores; exatamente 3 titulares e no máximo 1 suplente        | Validação na aplicação na composição e na alteração da banca.                                                                                 |
| 11     | Nota com uma casa decimal                                                                                                                                                                      | Validação no formulário: o tipo DECIMAL(3,1) arredonda um valor com duas casas (7,55 é gravado como 7,6) em vez de recusá-lo.                 |
| 12     | Uma Secretaria ativa por curso                                                                                                                                                                 | Validação na aplicação no cadastro da Secretaria.                                                                                             |
