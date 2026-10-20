"""Modelos do Épico 1 (Cadastro): 27 das 36 tabelas do dicionário de dados de 18/10.

Nomes de tabela e de coluna exatamente como no dicionário (db_table e db_column explícitos;
research D5). Campos com "Nulo? Sim" usam null=True e blank=True; FKs usam PROTECT (research R5).
As restrições do banco (CHECKs e unicidades) ficam em Meta.constraints (spec 001, US2).

Referências: specs/001-modelo-dados/data-model.md e docs/fonte/Modelo_Logico_e_Dicionario_18_10.md.
"""

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    DiaSemana,
    GatilhoStatusTCC,
    Homologacao,
    ModalidadeTCC,
    OrigemOrientacao,
    QualisCapes,
    StatusConta,
    StatusCoorientacao,
    StatusEntrega,
    StatusOrientacao,
    StatusSolicitacao,
    StatusSubmissao,
    StatusTCC,
    StatusTurma,
    TipoEntrega,
    TipoEventoTurma,
    TipoSolicitacao,
    Titulacao,
)
from sigtcc.apps.cadastro.fields import CharFixoField, TimestampField
from sigtcc.apps.cadastro.managers import UsuariosManager

PROTECT = models.PROTECT


# ---------------------------------------------------------------------------------------------
# 3.1 Entidades base e domínios fixos
# ---------------------------------------------------------------------------------------------


class Cursos(models.Model):
    """Cursos de graduação do NUCOMP (dicionário 3.1.1).

    [US-39][RBN-CAD-14.1][US-03][RBN-CAD-01.1]
    """

    cur_id = models.AutoField(primary_key=True)
    cur_nome = models.CharField(max_length=100)
    cur_descricao = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "Cursos"
        verbose_name = "curso"
        verbose_name_plural = "cursos"

    def __str__(self):
        return self.cur_nome


class EquivalenciaCursos(models.Model):
    """Equivalência entre o código de curso da UEA e o curso do NUCOMP (dicionário 3.1.2).

    [US-08][RBN-CAD-05.7]
    """

    eqc_codigo_uea = models.CharField(max_length=20, primary_key=True)
    eqc_cur = models.ForeignKey(Cursos, on_delete=PROTECT, db_column="eqc_cur_id")

    class Meta:
        db_table = "Equivalencia_Cursos"
        verbose_name = "equivalência de curso"
        verbose_name_plural = "equivalências de cursos"

    def __str__(self):
        return self.eqc_codigo_uea


class Disciplinas(models.Model):
    """Disciplinas de TCC (dicionário 3.1.3).

    [US-07][RBN-CAD-04.1]
    """

    dis_id = models.AutoField(primary_key=True)
    dis_codigo = models.CharField(max_length=20, unique=True)
    dis_nome = models.CharField(max_length=100, null=True, blank=True)
    dis_descricao = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "Disciplinas"
        verbose_name = "disciplina"
        verbose_name_plural = "disciplinas"

    def __str__(self):
        return self.dis_codigo


class AreasInteresse(models.Model):
    """As 10 áreas fixas de interesse do NUCOMP/UEA (dicionário 3.1.5).

    [US-13][RBN-CAD-08.1]
    """

    ari_id = models.AutoField(primary_key=True)
    ari_nome = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "Areas_Interesse"
        verbose_name = "área de interesse"
        verbose_name_plural = "áreas de interesse"

    def __str__(self):
        return self.ari_nome


# ---------------------------------------------------------------------------------------------
# 3.2 Hierarquia de usuários
# ---------------------------------------------------------------------------------------------


class Usuarios(AbstractBaseUser):
    """Conta de acesso de qualquer perfil (dicionário 3.2.1); modelo de usuário do Django.

    Só as 6 colunas do dicionário (research D1): last_login removido, sem PermissionsMixin
    (sem is_staff, is_superuser e grupos). A senha fica no atributo password, coluna usu_senha.

    [US-10][RBN-CAD-06.3][US-11][RBN-CAD-06.4][US-04][RBN-CAD-01.3][RBN-CAD-02.3]
    [US-06][RBN-CAD-03.3]
    """

    usu_id = models.AutoField(primary_key=True)
    usu_nome = models.CharField(max_length=150)
    usu_email = models.CharField(max_length=100, null=True, blank=True, unique=True)
    password = models.CharField(max_length=255, null=True, blank=True, db_column="usu_senha")
    usu_status = models.CharField(max_length=30, choices=StatusConta.choices)
    usu_link_gerado_em = TimestampField(null=True, blank=True)

    # Remove a coluna last_login herdada; o Django deixa de registrar o sinal que a atualiza.
    last_login = None

    objects = UsuariosManager()

    USERNAME_FIELD = "usu_email"
    EMAIL_FIELD = "usu_email"
    REQUIRED_FIELDS = ["usu_nome"]

    class Meta:
        db_table = "Usuarios"
        verbose_name = "usuário"
        verbose_name_plural = "usuários"

    @property
    def is_active(self):
        """Só a conta 'Ativa' faz login (derivado do status, sem coluna; research D1)."""
        return self.usu_status == StatusConta.ATIVA

    def __str__(self):
        # O e-mail pode ser nulo (Aluno antes do primeiro acesso); por isso usa o nome.
        return self.usu_nome


class Alunos(models.Model):
    """Especialização de Usuarios para o aluno (dicionário 3.2.2).

    [US-08][RBN-CAD-05.1][RBN-CAD-05.7]
    """

    alu = models.OneToOneField(Usuarios, on_delete=PROTECT, primary_key=True, db_column="alu_id")
    alu_matricula = CharFixoField(max_length=10, unique=True)
    # Código informado no cadastro; não é FK (validado contra Equivalencia_Cursos na aplicação).
    alu_codigo_curso = models.CharField(max_length=20)

    class Meta:
        db_table = "Alunos"
        verbose_name = "aluno"
        verbose_name_plural = "alunos"

    def __str__(self):
        return self.alu_matricula


class Docentes(models.Model):
    """Especialização de Usuarios para o docente do NUCOMP (dicionário 3.2.3).

    [US-03][RBN-CAD-01.1]
    """

    doc = models.OneToOneField(Usuarios, on_delete=PROTECT, primary_key=True, db_column="doc_id")
    doc_titulacao = models.CharField(max_length=20, choices=Titulacao.choices)
    doc_cur = models.ForeignKey(Cursos, on_delete=PROTECT, db_column="doc_cur_id")
    doc_assinatura_path = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "Docentes"
        verbose_name = "docente"
        verbose_name_plural = "docentes"


class MembrosExternos(models.Model):
    """Especialização de Usuarios para o avaliador externo (dicionário 3.2.4).

    [US-05][RBN-CAD-03.1][US-06][RBN-CAD-03.3]
    """

    mem = models.OneToOneField(Usuarios, on_delete=PROTECT, primary_key=True, db_column="mem_id")
    mem_titulacao = models.CharField(max_length=20, choices=Titulacao.choices)
    mem_instituicao = models.CharField(max_length=150)
    mem_assinatura_path = models.CharField(max_length=255, null=True, blank=True)
    mem_validade_ate = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "MembrosExternos"
        verbose_name = "membro externo"
        verbose_name_plural = "membros externos"


class Secretarios(models.Model):
    """Especialização de Usuarios para a Secretaria do curso (dicionário 3.2.5).

    "Uma Secretaria ativa por curso" fica na aplicação (dicionário 3.2.5; spec FR-019).

    [US-03][RBN-CAD-02.1]
    """

    sec = models.OneToOneField(Usuarios, on_delete=PROTECT, primary_key=True, db_column="sec_id")
    sec_cur = models.ForeignKey(Cursos, on_delete=PROTECT, db_column="sec_cur_id")

    class Meta:
        db_table = "Secretarios"
        verbose_name = "secretaria"
        verbose_name_plural = "secretarias"


class CoorientadoresExternos(models.Model):
    """Coorientador de fora do NUCOMP, sem conta de acesso (dicionário 3.2.6).

    [US-45][RBN-CAD-10.3]
    """

    cext_id = models.AutoField(primary_key=True)
    cext_nome = models.CharField(max_length=150)
    cext_email = models.CharField(max_length=100, null=True, blank=True, unique=True)
    cext_instituicao = models.CharField(max_length=150, null=True, blank=True)

    class Meta:
        db_table = "CoorientadoresExternos"
        verbose_name = "coorientador externo"
        verbose_name_plural = "coorientadores externos"

    def __str__(self):
        return self.cext_nome


# ---------------------------------------------------------------------------------------------
# 3.3 Turmas, matrículas e histórico acadêmico
# ---------------------------------------------------------------------------------------------


class Coordenadores(models.Model):
    """Coordenador de Curso: um por curso, e um docente coordena no máximo um (dicionário 3.3.1).

    [US-03][RBN-CAD-01.1]
    """

    cor_cur = models.OneToOneField(
        Cursos, on_delete=PROTECT, primary_key=True, db_column="cor_cur_id"
    )
    cor_doc = models.OneToOneField(Docentes, on_delete=PROTECT, db_column="cor_doc_id")

    class Meta:
        db_table = "Coordenadores"
        verbose_name = "coordenador de curso"
        verbose_name_plural = "coordenadores de curso"


class Turmas(models.Model):
    """Turma de TCC 1 ou TCC 2 (dicionário 3.3.2).

    [US-07][RBN-CAD-04.1][RBN-CAD-04.5]
    """

    tur_id = models.AutoField(primary_key=True)
    tur_identificador = models.CharField(max_length=30, unique=True)
    tur_descricao = models.CharField(max_length=10, choices=DescricaoTurma.choices)
    tur_doc = models.ForeignKey(Docentes, on_delete=PROTECT, db_column="tur_doc_id")
    tur_dis = models.ForeignKey(Disciplinas, on_delete=PROTECT, db_column="tur_dis_id")
    tur_cur = models.ForeignKey(Cursos, on_delete=PROTECT, db_column="tur_cur_id")
    tur_ano = models.IntegerField()
    tur_semestre = models.IntegerField()
    tur_dia_da_semana = models.CharField(max_length=20, choices=DiaSemana.choices)
    tur_hora_inicio = models.TimeField()
    tur_hora_termino = models.TimeField()
    tur_local = models.CharField(max_length=100)
    tur_status = models.CharField(max_length=20, choices=StatusTurma.choices)

    class Meta:
        db_table = "Turmas"
        verbose_name = "turma"
        verbose_name_plural = "turmas"

    def __str__(self):
        return self.tur_identificador


class AlunosTurmas(models.Model):
    """Vínculo do aluno com a turma (dicionário 3.3.3); PK composta.

    [US-08][RBN-CAD-05.1][RBN-CAD-05.5]
    """

    pk = models.CompositePrimaryKey("mat_alu_id", "mat_tur_id")
    mat_alu = models.ForeignKey(Alunos, on_delete=PROTECT, db_column="mat_alu_id")
    mat_tur = models.ForeignKey(Turmas, on_delete=PROTECT, db_column="mat_tur_id")
    mat_data_inscricao = TimestampField()

    class Meta:
        db_table = "Alunos_Turmas"
        verbose_name = "matrícula na turma"
        verbose_name_plural = "matrículas nas turmas"


class HistoricoAlunosTurmas(models.Model):
    """Exclusões e transferências de alunos entre turmas (dicionário 3.3.4).

    [US-09][RBN-CAD-05.4][RBN-CAD-05.8][US-08][RBN-CAD-05.6]
    """

    hat_id = models.AutoField(primary_key=True)
    hat_alu = models.ForeignKey(Alunos, on_delete=PROTECT, db_column="hat_alu_id")
    hat_tur_origem = models.ForeignKey(
        Turmas,
        on_delete=PROTECT,
        db_column="hat_tur_origem_id",
        related_name="historicos_origem",
    )
    hat_tur_destino = models.ForeignKey(
        Turmas,
        on_delete=PROTECT,
        null=True,
        blank=True,
        db_column="hat_tur_destino_id",
        related_name="historicos_destino",
    )
    hat_tipo_evento = models.CharField(max_length=20, choices=TipoEventoTurma.choices)
    hat_justificativa = models.CharField(max_length=500)
    hat_data_hora = TimestampField()
    hat_usu = models.ForeignKey(Usuarios, on_delete=PROTECT, db_column="hat_usu_id")

    class Meta:
        db_table = "Historico_Alunos_Turmas"
        verbose_name = "histórico de aluno na turma"
        verbose_name_plural = "históricos de alunos nas turmas"


# ---------------------------------------------------------------------------------------------
# 3.4 Entregas e atividades das turmas
# ---------------------------------------------------------------------------------------------


class TurmasMarcos(models.Model):
    """Entregas (atividades) cadastradas na turma (dicionário 3.4.1).

    [US-43][RBN-CAD-09.1]
    """

    tma_id = models.AutoField(primary_key=True)
    tma_tur = models.ForeignKey(Turmas, on_delete=PROTECT, db_column="tma_tur_id")
    tma_tipo = models.CharField(max_length=30, choices=TipoEntrega.choices)
    tma_titulo = models.CharField(max_length=100)
    tma_instrucao = models.CharField(max_length=1000, null=True, blank=True)
    tma_data_limite = TimestampField()

    class Meta:
        db_table = "Turmas_Marcos"
        verbose_name = "entrega da turma"
        verbose_name_plural = "entregas da turma"


class EntregasMarcos(models.Model):
    """Situação de cada aluno em cada entrega (dicionário 3.4.2).

    [US-15][RBN-CAD-09.3][US-44][RBN-CAD-09.5]
    """

    ent_id = models.AutoField(primary_key=True)
    ent_tma = models.ForeignKey(TurmasMarcos, on_delete=PROTECT, db_column="ent_tma_id")
    ent_alu = models.ForeignKey(Alunos, on_delete=PROTECT, db_column="ent_alu_id")
    ent_status = models.CharField(max_length=30, choices=StatusEntrega.choices)
    ent_feedback = models.CharField(max_length=500, null=True, blank=True)
    ent_data_avaliacao = TimestampField(null=True, blank=True)
    ent_correcoes_conferidas_em = TimestampField(null=True, blank=True)

    class Meta:
        db_table = "Entregas_Marcos"
        verbose_name = "entrega do aluno"
        verbose_name_plural = "entregas dos alunos"


class HistoricoEnviosEntregas(models.Model):
    """Links enviados (e substituídos) em cada entrega (dicionário 3.4.3).

    [US-15][RBN-CAD-09.2]
    """

    hen_id = models.AutoField(primary_key=True)
    hen_ent = models.ForeignKey(EntregasMarcos, on_delete=PROTECT, db_column="hen_ent_id")
    hen_link = models.CharField(max_length=500)
    hen_data_envio = TimestampField()

    class Meta:
        db_table = "Historico_Envios_Entregas"
        verbose_name = "envio de entrega"
        verbose_name_plural = "envios de entregas"


# ---------------------------------------------------------------------------------------------
# 3.5 TCC, orientação e publicações
# ---------------------------------------------------------------------------------------------


class TCCs(models.Model):
    """Trabalho de conclusão do aluno na turma (dicionário 3.5.1).

    [US-13][RBN-CAD-07.1][US-14][RBN-CAD-08.3][US-09][RBN-CAD-08.4]
    """

    tcc_id = models.AutoField(primary_key=True)
    tcc_alu = models.ForeignKey(Alunos, on_delete=PROTECT, db_column="tcc_alu_id")
    tcc_tur = models.ForeignKey(Turmas, on_delete=PROTECT, db_column="tcc_tur_id")
    tcc_ari = models.ForeignKey(
        AreasInteresse, on_delete=PROTECT, null=True, blank=True, db_column="tcc_ari_id"
    )
    tcc_modalidade = models.CharField(
        max_length=30, null=True, blank=True, choices=ModalidadeTCC.choices
    )
    tcc_titulo = models.CharField(max_length=250, null=True, blank=True)
    tcc_subtitulo = models.CharField(max_length=250, null=True, blank=True)
    tcc_resumo = models.CharField(max_length=1000, null=True, blank=True)
    tcc_link_proposta = models.CharField(max_length=500, null=True, blank=True)
    tcc_status = models.CharField(max_length=50, choices=StatusTCC.choices)
    tcc_justificativa_encerramento = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = "TCCs"
        verbose_name = "TCC"
        verbose_name_plural = "TCCs"


class Orientacoes(models.Model):
    """Vínculos de orientação; o ativo é o orientador atual (dicionário 3.5.2).

    [US-17][RBN-CAD-10.1][RBN-CAD-10.6][US-18][RBN-CAD-10.2]
    """

    ori_id = models.AutoField(primary_key=True)
    ori_tcc = models.ForeignKey(TCCs, on_delete=PROTECT, db_column="ori_tcc_id")
    ori_doc = models.ForeignKey(Docentes, on_delete=PROTECT, db_column="ori_doc_id")
    ori_origem = models.CharField(max_length=20, choices=OrigemOrientacao.choices)
    ori_status = models.CharField(max_length=20, choices=StatusOrientacao.choices)
    ori_data_inicio = TimestampField()
    ori_data_fim = TimestampField(null=True, blank=True)

    class Meta:
        db_table = "Orientacoes"
        verbose_name = "orientação"
        verbose_name_plural = "orientações"


class Coorientacoes(models.Model):
    """Vínculos de coorientação, com docente ou coorientador externo (dicionário 3.5.3).

    [US-45][RBN-CAD-10.3][RBN-CAD-10.7][US-36][RBN-CAD-10.4]
    """

    coo_id = models.AutoField(primary_key=True)
    coo_tcc = models.ForeignKey(TCCs, on_delete=PROTECT, db_column="coo_tcc_id")
    coo_doc = models.ForeignKey(
        Docentes, on_delete=PROTECT, null=True, blank=True, db_column="coo_doc_id"
    )
    coo_cext = models.ForeignKey(
        CoorientadoresExternos, on_delete=PROTECT, null=True, blank=True, db_column="coo_cext_id"
    )
    coo_status = models.CharField(max_length=20, choices=StatusCoorientacao.choices)
    coo_data_inicio = TimestampField()
    coo_data_fim = TimestampField(null=True, blank=True)

    class Meta:
        db_table = "Coorientacoes"
        verbose_name = "coorientação"
        verbose_name_plural = "coorientações"


class PalavrasChaveTCC(models.Model):
    """Palavras-chave do TCC (dicionário 3.5.4); PK composta. O limite de 1 a 5 é da aplicação.

    [US-13][RBN-CAD-08.1]
    """

    pk = models.CompositePrimaryKey("pal_tcc_id", "pal_palavra")
    pal_tcc = models.ForeignKey(TCCs, on_delete=PROTECT, db_column="pal_tcc_id")
    pal_palavra = models.CharField(max_length=100)

    class Meta:
        db_table = "PalavrasChave_TCC"
        verbose_name = "palavra-chave"
        verbose_name_plural = "palavras-chave"


class SolicitacoesOrientacao(models.Model):
    """Pedidos de orientação, troca de orientação e convites de coorientação (dicionário 3.5.5).

    [US-17][RBN-CAD-10.1][RBN-CAD-10.6][US-36][RBN-CAD-10.4]
    """

    sol_id = models.AutoField(primary_key=True)
    sol_tcc = models.ForeignKey(TCCs, on_delete=PROTECT, db_column="sol_tcc_id")
    sol_doc = models.ForeignKey(Docentes, on_delete=PROTECT, db_column="sol_doc_id")
    sol_tipo = models.CharField(max_length=20, choices=TipoSolicitacao.choices)
    sol_status = models.CharField(max_length=20, choices=StatusSolicitacao.choices)
    sol_data_solicitacao = TimestampField()
    sol_data_resposta = TimestampField(null=True, blank=True)

    class Meta:
        db_table = "Solicitacoes_Orientacao"
        verbose_name = "solicitação de orientação"
        verbose_name_plural = "solicitações de orientação"


class HistoricoStatusTCC(models.Model):
    """Histórico das mudanças do Status do TCC (dicionário 3.5.6).

    [US-14][RBN-CAD-08.7][RBN-CAD-08.8]
    """

    hst_id = models.AutoField(primary_key=True)
    hst_tcc = models.ForeignKey(TCCs, on_delete=PROTECT, db_column="hst_tcc_id")
    hst_tur = models.ForeignKey(Turmas, on_delete=PROTECT, db_column="hst_tur_id")
    hst_status_anterior = models.CharField(
        max_length=50, null=True, blank=True, choices=StatusTCC.choices
    )
    hst_status_novo = models.CharField(max_length=50, choices=StatusTCC.choices)
    hst_gatilho = models.CharField(max_length=100, choices=GatilhoStatusTCC.choices)
    hst_data_hora = TimestampField()
    hst_usu = models.ForeignKey(Usuarios, on_delete=PROTECT, db_column="hst_usu_id")

    class Meta:
        db_table = "Historico_Status_TCC"
        verbose_name = "histórico de status do TCC"
        verbose_name_plural = "históricos de status do TCC"


class Artigos(models.Model):
    """Publicação do artigo do TCC e seu aproveitamento (dicionário 3.5.7).

    [US-46][RBN-CAD-12.1][US-20][RBN-CAD-12.3]
    """

    art = models.OneToOneField(TCCs, on_delete=PROTECT, primary_key=True, db_column="art_id")
    art_veiculo_publicacao = models.CharField(max_length=150, null=True, blank=True)
    art_link_doi = models.CharField(max_length=500)
    art_qualis_capes = models.CharField(
        max_length=5, null=True, blank=True, choices=QualisCapes.choices
    )
    art_status_submissao = models.CharField(
        max_length=30, null=True, blank=True, choices=StatusSubmissao.choices
    )
    art_homologacao = models.CharField(
        max_length=20, null=True, blank=True, choices=Homologacao.choices
    )
    # A coluna do dicionário não termina em _id, por isso o db_column explícito (research D5).
    art_homologado_por = models.ForeignKey(
        Usuarios, on_delete=PROTECT, null=True, blank=True, db_column="art_homologado_por"
    )
    art_data_homologacao = TimestampField(null=True, blank=True)

    class Meta:
        db_table = "Artigos"
        verbose_name = "artigo"
        verbose_name_plural = "artigos"


class EncontroOrientacao(models.Model):
    """Atas dos encontros de orientação (dicionário 3.5.8).

    [US-19][RBN-CAD-11.1]
    """

    enc_id = models.AutoField(primary_key=True)
    enc_tcc = models.ForeignKey(TCCs, on_delete=PROTECT, db_column="enc_tcc_id")
    enc_data = models.DateField()
    enc_pauta = models.CharField(max_length=2000)
    enc_metas = models.CharField(max_length=2000)

    class Meta:
        db_table = "Encontro_Orientacao"
        verbose_name = "encontro de orientação"
        verbose_name_plural = "encontros de orientação"


class ComentariosEncontro(models.Model):
    """Comentários do orientador ou coorientador nas atas (dicionário 3.5.9).

    [US-19][RBN-CAD-11.2]
    """

    com_id = models.AutoField(primary_key=True)
    com_enc = models.ForeignKey(EncontroOrientacao, on_delete=PROTECT, db_column="com_enc_id")
    com_usu = models.ForeignKey(Usuarios, on_delete=PROTECT, db_column="com_usu_id")
    com_texto = models.CharField(max_length=1000)
    com_data_hora = TimestampField()

    class Meta:
        db_table = "Comentarios_Encontro"
        verbose_name = "comentário de encontro"
        verbose_name_plural = "comentários de encontros"


# ---------------------------------------------------------------------------------------------
# 3.7 Notificações
# ---------------------------------------------------------------------------------------------


class Notificacoes(models.Model):
    """Central de notificações do usuário (dicionário 3.7.1).

    [US-38][RBN-CAD-13.2]
    """

    not_id = models.AutoField(primary_key=True)
    not_usu = models.ForeignKey(Usuarios, on_delete=PROTECT, db_column="not_usu_id")
    not_mensagem = models.CharField(max_length=500)
    not_link_tela = models.CharField(max_length=255, null=True, blank=True)
    not_data_hora = TimestampField()
    # Padrão gravado na própria coluna, não só no Python (research R6; FR-012).
    not_lida = models.BooleanField(db_default=False)

    class Meta:
        db_table = "Notificacoes"
        verbose_name = "notificação"
        verbose_name_plural = "notificações"
