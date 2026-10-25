"""Modelos do Épico 2 (Defesa): 9 das 36 tabelas do dicionário de dados de 18/10.

Mesmas convenções do app cadastro (research D5, R5). A FK composta Avaliacoes → Banca_Defesa
existe só no banco, criada pela migração 0002_fk_composta_avaliacoes (research D3).

Referências: specs/001-modelo-dados/data-model.md e docs/fonte/Modelo_Logico_e_Dicionario_18_10.md.
"""

from django.conf import settings
from django.db import models
from django.db.models import Q

from sigtcc.apps.cadastro.choices import restricao_dominio
from sigtcc.apps.cadastro.fields import CharFixoField, TimestampField
from sigtcc.apps.defesa.choices import (
    ComponenteCriterio,
    Conceito,
    EventoDefesa,
    FormatoSessao,
    PapelBanca,
    Parecer,
    StatusSessao,
)

PROTECT = models.PROTECT
USUARIO = settings.AUTH_USER_MODEL


class Criterios(models.Model):
    """Os 9 critérios oficiais de avaliação da EST/UEA, fixos e não editáveis (dicionário 3.1.4).

    [US-25][RBN-DEF-04.1][RBN-DEF-04.2]
    """

    cri_id = models.AutoField(primary_key=True)
    cri_nome = models.CharField(max_length=100)
    cri_componente = models.CharField(max_length=20, choices=ComponenteCriterio.choices)
    cri_descricao = models.CharField(max_length=255, null=True, blank=True)
    cri_desc_exemplar = models.CharField(max_length=255)
    cri_desc_competente = models.CharField(max_length=255)
    cri_desc_necessita_trabalho = models.CharField(max_length=255)
    cri_peso = models.DecimalField(max_digits=3, decimal_places=1)

    class Meta:
        db_table = "Criterios"
        constraints = [
            restricao_dominio("ck_criterios_cri_componente", "cri_componente", ComponenteCriterio),
            models.CheckConstraint(
                condition=Q(cri_peso__gte=0, cri_peso__lte=10), name="ck_criterios_cri_peso"
            ),
        ]
        verbose_name = "critério de avaliação"
        verbose_name_plural = "critérios de avaliação"

    def __str__(self):
        """Representação em texto do registro. [US-25][RBN-DEF-04.1][RBN-DEF-04.2]"""
        return self.cri_nome


class Ouvintes(models.Model):
    """Ouvintes das sessões de defesa (dicionário 3.1.6).

    [US-30][RBN-DEF-08.2]
    """

    ouv_id = models.AutoField(primary_key=True)
    ouv_matricula = CharFixoField(max_length=10, unique=True)
    ouv_nome = models.CharField(max_length=150)

    class Meta:
        db_table = "Ouvintes"
        constraints = [
            models.CheckConstraint(
                condition=Q(ouv_matricula__regex=r"^[0-9]{10}$"), name="ck_ouvintes_ouv_matricula"
            ),
        ]
        verbose_name = "ouvinte"
        verbose_name_plural = "ouvintes"

    def __str__(self):
        """Representação em texto do registro. [US-30][RBN-DEF-08.2]"""
        return self.ouv_nome


class Defesas(models.Model):
    """Sessão de defesa do TCC, com resultado e documentos gerados (dicionário 3.6.1).

    [US-21][RBN-DEF-01.1][US-24][RBN-DEF-01.2][US-27][RBN-DEF-06.3][RBN-DEF-06.4]
    [US-28][RBN-DEF-07.1]
    """

    def_id = models.AutoField(primary_key=True)
    def_tcc = models.ForeignKey("cadastro.TCCs", on_delete=PROTECT, db_column="def_tcc_id")
    def_data = models.DateField()
    def_h_inicio = models.TimeField()
    def_formato = models.CharField(max_length=20, choices=FormatoSessao.choices)
    def_status = models.CharField(max_length=30, choices=StatusSessao.choices)
    def_parecer = models.CharField(max_length=30, null=True, blank=True, choices=Parecer.choices)
    def_nota_final = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    def_ocorrencias = models.CharField(max_length=2000, null=True, blank=True)
    def_data_liberacao_resultado = TimestampField(null=True, blank=True)
    def_ata_final_path = models.CharField(max_length=255, null=True, blank=True)
    def_folha_aprovacao_path = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "Defesas"
        constraints = [
            restricao_dominio("ck_defesas_def_formato", "def_formato", FormatoSessao),
            restricao_dominio("ck_defesas_def_status", "def_status", StatusSessao),
            restricao_dominio("ck_defesas_def_parecer", "def_parecer", Parecer, aceita_nulo=True),
            models.CheckConstraint(
                condition=Q(def_nota_final__gte=0, def_nota_final__lte=10)
                | Q(def_nota_final__isnull=True),
                name="ck_defesas_def_nota_final",
            ),
        ]
        verbose_name = "defesa"
        verbose_name_plural = "defesas"


class DefesasPresenciais(models.Model):
    """Local da sessão presencial, em texto (dicionário 3.6.2; Salas fora do escopo).

    [US-21][RBN-DEF-01.1]
    """

    dep_def = models.OneToOneField(
        Defesas, on_delete=PROTECT, primary_key=True, db_column="dep_def_id"
    )
    dep_local = models.CharField(max_length=100)

    class Meta:
        db_table = "Defesas_Presenciais"
        verbose_name = "defesa presencial"
        verbose_name_plural = "defesas presenciais"


class DefesasRemotas(models.Model):
    """Link da sessão remota (dicionário 3.6.3).

    [US-21][RBN-DEF-01.1]
    """

    der_def = models.OneToOneField(
        Defesas, on_delete=PROTECT, primary_key=True, db_column="der_def_id"
    )
    der_link = models.CharField(max_length=500)

    class Meta:
        db_table = "Defesas_Remotas"
        verbose_name = "defesa remota"
        verbose_name_plural = "defesas remotas"


class BancaDefesa(models.Model):
    """Membros da banca examinadora de cada sessão (dicionário 3.6.4); PK composta.

    [US-23][RBN-DEF-02.1][RBN-DEF-02.2][US-26][RBN-DEF-05.2]
    """

    pk = models.CompositePrimaryKey("ban_def_id", "ban_usu_id")
    ban_def = models.ForeignKey(Defesas, on_delete=PROTECT, db_column="ban_def_id")
    ban_usu = models.ForeignKey(
        USUARIO, on_delete=PROTECT, db_column="ban_usu_id", related_name="bancas"
    )
    ban_papel = models.CharField(max_length=30, choices=PapelBanca.choices)
    ban_usu_substituido = models.ForeignKey(
        USUARIO,
        on_delete=PROTECT,
        null=True,
        blank=True,
        db_column="ban_usu_substituido_id",
        related_name="substituicoes_banca",
    )
    ban_justificativa_substituicao = models.CharField(max_length=500, null=True, blank=True)
    ban_assinatura_path = models.CharField(max_length=255, null=True, blank=True)
    ban_data_envio = TimestampField(null=True, blank=True)

    class Meta:
        db_table = "Banca_Defesa"
        constraints = [
            restricao_dominio("ck_banca_defesa_ban_papel", "ban_papel", PapelBanca),
        ]
        verbose_name = "membro da banca"
        verbose_name_plural = "membros da banca"


class PresencaOuvintes(models.Model):
    """Presença dos ouvintes em cada sessão (dicionário 3.6.5); PK composta.

    [US-30][RBN-DEF-08.2][RBN-DEF-08.4]
    """

    pk = models.CompositePrimaryKey("pre_def_id", "pre_ouv_id")
    pre_def = models.ForeignKey(Defesas, on_delete=PROTECT, db_column="pre_def_id")
    pre_ouv = models.ForeignKey(Ouvintes, on_delete=PROTECT, db_column="pre_ouv_id")

    class Meta:
        db_table = "Presenca_Ouvintes"
        verbose_name = "presença de ouvinte"
        verbose_name_plural = "presenças de ouvintes"


class Avaliacoes(models.Model):
    """Nota e conceito de cada membro da banca em cada critério (dicionário 3.6.6).

    ava_def e ava_usu não criam FKs simples (db_constraint=False): no banco, os dois formam a
    FK composta para Banca_Defesa, criada por RunSQL (research D3).

    [US-25][RBN-DEF-05.2]
    """

    pk = models.CompositePrimaryKey("ava_def_id", "ava_usu_id", "ava_cri_id")
    # O prefixo da PK já indexa ava_def_id (research D3).
    ava_def = models.ForeignKey(
        Defesas,
        on_delete=PROTECT,
        db_column="ava_def_id",
        db_constraint=False,
        db_index=False,
    )
    ava_usu = models.ForeignKey(
        USUARIO, on_delete=PROTECT, db_column="ava_usu_id", db_constraint=False
    )
    ava_cri = models.ForeignKey(Criterios, on_delete=PROTECT, db_column="ava_cri_id")
    ava_conceito = models.CharField(max_length=30, choices=Conceito.choices)
    ava_nota = models.DecimalField(max_digits=3, decimal_places=1)
    ava_observacoes = models.CharField(max_length=500, null=True, blank=True)
    ava_data_hora = TimestampField()

    class Meta:
        db_table = "Avaliacoes"
        constraints = [
            restricao_dominio("ck_avaliacoes_ava_conceito", "ava_conceito", Conceito),
            models.CheckConstraint(
                condition=Q(ava_nota__gte=0, ava_nota__lte=10), name="ck_avaliacoes_ava_nota"
            ),
        ]
        verbose_name = "avaliação"
        verbose_name_plural = "avaliações"


class HistoricoDefesas(models.Model):
    """Eventos da sessão: agendamento, reagendamento, cancelamento, banca e resultado
    (dicionário 3.6.7).

    [US-40][RBN-DEF-01.6][US-24][RBN-DEF-03.3]
    """

    hdf_id = models.AutoField(primary_key=True)
    hdf_def = models.ForeignKey(Defesas, on_delete=PROTECT, db_column="hdf_def_id")
    hdf_evento = models.CharField(max_length=30, choices=EventoDefesa.choices)
    hdf_status_anterior = models.CharField(
        max_length=30, null=True, blank=True, choices=StatusSessao.choices
    )
    hdf_status_novo = models.CharField(
        max_length=30, null=True, blank=True, choices=StatusSessao.choices
    )
    hdf_data_anterior = models.DateField(null=True, blank=True)
    hdf_hora_anterior = models.TimeField(null=True, blank=True)
    hdf_data_nova = models.DateField(null=True, blank=True)
    hdf_hora_nova = models.TimeField(null=True, blank=True)
    hdf_membro_removido = models.ForeignKey(
        USUARIO,
        on_delete=PROTECT,
        null=True,
        blank=True,
        db_column="hdf_membro_removido_id",
        related_name="+",
    )
    hdf_membro_incluido = models.ForeignKey(
        USUARIO,
        on_delete=PROTECT,
        null=True,
        blank=True,
        db_column="hdf_membro_incluido_id",
        related_name="+",
    )
    hdf_justificativa = models.CharField(max_length=500, null=True, blank=True)
    hdf_data_hora = TimestampField()
    hdf_usu = models.ForeignKey(
        USUARIO,
        on_delete=PROTECT,
        null=True,
        blank=True,
        db_column="hdf_usu_id",
        related_name="eventos_defesa",
    )

    class Meta:
        db_table = "Historico_Defesas"
        constraints = [
            restricao_dominio("ck_historico_defesas_hdf_evento", "hdf_evento", EventoDefesa),
            restricao_dominio(
                "ck_historico_defesas_hdf_status_anterior",
                "hdf_status_anterior",
                StatusSessao,
                aceita_nulo=True,
            ),
            restricao_dominio(
                "ck_historico_defesas_hdf_status_novo",
                "hdf_status_novo",
                StatusSessao,
                aceita_nulo=True,
            ),
        ]
        verbose_name = "histórico da defesa"
        verbose_name_plural = "históricos das defesas"
