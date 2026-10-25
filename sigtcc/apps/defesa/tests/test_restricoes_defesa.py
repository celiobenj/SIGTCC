"""Restrições do banco no app defesa: cada uma tem um teste de recusa e um de aceitação.

[US-25][RBN-DEF-05.2][US-23][RBN-DEF-02.1][US-30][RBN-DEF-08.2][spec 001, US2 cenário 9][FR-004]
[FR-005][FR-010][SC-002]
"""

from decimal import Decimal

from django.test import TestCase

from sigtcc.apps.cadastro.tests import fabricas as f
from sigtcc.apps.cadastro.tests.test_restricoes_cadastro import RestricoesTestCase
from sigtcc.apps.defesa.choices import Conceito, EventoDefesa, PapelBanca
from sigtcc.apps.defesa.models import (
    Avaliacoes,
    BancaDefesa,
    HistoricoDefesas,
    Ouvintes,
    PresencaOuvintes,
)


def avaliar(membro, criterio, **campos):
    """Grava a avaliação de um membro da banca num critério."""
    valores = {
        "ava_def_id": membro.ban_def_id,
        "ava_usu_id": membro.ban_usu_id,
        "ava_cri": criterio,
        "ava_conceito": Conceito.COMPETENTE,
        "ava_nota": Decimal("7.0"),
        "ava_data_hora": f.AGORA,
    }
    valores.update(campos)
    return Avaliacoes.objects.create(**valores)


def registrar_evento(**campos):
    """Grava um evento no histórico da defesa."""
    valores = {
        "hdf_def": f.criar_defesa(),
        "hdf_evento": EventoDefesa.AGENDAMENTO,
        "hdf_data_hora": f.AGORA,
    }
    valores.update(campos)
    return HistoricoDefesas.objects.create(**valores)


def criar_ouvinte(matricula=None):
    """Grava um ouvinte com matrícula única."""
    return Ouvintes.objects.create(
        ouv_matricula=matricula or f"{2026500000 + f.proximo():010d}", ouv_nome="Ouvinte"
    )


class RestricoesDefesaTest(RestricoesTestCase):
    """CHECKs, faixas, unicidades e a FK composta do app defesa."""

    def test_cenario9_nota_fora_da_faixa(self):
        """Dada uma avaliação, quando a nota é 10,5 ou negativa, então o banco recusa (FR-010)."""
        membro, criterio = f.criar_membro_banca(), f.criar_criterio()
        self.assertRecusa(lambda: avaliar(membro, criterio, ava_nota=Decimal("10.5")))
        self.assertRecusa(lambda: avaliar(membro, criterio, ava_nota=Decimal("-0.1")))
        self.assertAceita(lambda: avaliar(membro, criterio, ava_nota=Decimal("10.0")))
        self.assertAceita(lambda: avaliar(membro, f.criar_criterio(), ava_nota=Decimal("0.0")))

    def test_faixas_de_peso_e_nota_final(self):
        """cri_peso e def_nota_final ficam entre 0,0 e 10,0; nota final pode ser nula."""
        self.assertRecusa(lambda: f.criar_criterio(cri_peso=Decimal("10.5")))
        self.assertRecusa(lambda: f.criar_criterio(cri_peso=Decimal("-0.1")))
        self.assertAceita(lambda: f.criar_criterio(cri_peso=Decimal("2.0")))
        self.assertRecusa(lambda: f.criar_defesa(def_nota_final=Decimal("10.5")))
        self.assertRecusa(lambda: f.criar_defesa(def_nota_final=Decimal("-0.1")))
        self.assertAceita(lambda: f.criar_defesa(def_nota_final=None))
        self.assertAceita(lambda: f.criar_defesa(def_nota_final=Decimal("6.0")))

    def test_dominios(self):
        """Um valor inválido recusado e um válido aceito em cada CHECK de domínio."""
        casos = [
            (
                "ck_criterios_cri_componente",
                lambda v: f.criar_criterio(cri_componente=v),
                "Parte Prática",
                ["Parte Oral"],
            ),
            (
                "ck_defesas_def_formato",
                lambda v: f.criar_defesa(def_formato=v),
                "Híbrida",
                ["Remota"],
            ),
            (
                "ck_defesas_def_status",
                lambda v: f.criar_defesa(def_status=v),
                "Adiada",
                ["Reagendada"],
            ),
            (
                "ck_defesas_def_parecer",
                lambda v: f.criar_defesa(def_parecer=v),
                "Aprovado com Louvor",
                [None, "Aprovado com Correções"],
            ),
            (
                "ck_banca_defesa_ban_papel",
                lambda v: f.criar_membro_banca(ban_papel=v),
                "3º Avaliador",
                ["Orientador (Presidente)", "2º Avaliador", "Suplente"],
            ),
            (
                "ck_avaliacoes_ava_conceito",
                lambda v: avaliar(f.criar_membro_banca(), f.criar_criterio(), ava_conceito=v),
                "Insuficiente",
                ["Exemplar"],
            ),
            (
                "ck_historico_defesas_hdf_evento",
                lambda v: registrar_evento(hdf_evento=v),
                "Adiamento",
                ["Início Automático"],
            ),
            (
                "ck_historico_defesas_hdf_status_anterior",
                lambda v: registrar_evento(hdf_status_anterior=v),
                "Adiada",
                [None, "Agendada"],
            ),
            (
                "ck_historico_defesas_hdf_status_novo",
                lambda v: registrar_evento(hdf_status_novo=v),
                "Adiada",
                [None, "Realizada"],
            ),
            ("ck_ouvintes_ouv_matricula", criar_ouvinte, "12345", ["2026000777"]),
        ]
        for restricao, gravar, invalido, validos in casos:
            with self.subTest(restricao=restricao, valor=invalido):
                self.assertRecusa(lambda: gravar(invalido))
            for valido in validos:
                with self.subTest(restricao=restricao, valor=valido):
                    self.assertAceita(lambda: gravar(valido))

    def test_unicidade_matricula_ouvinte(self):
        """ouv_matricula é única (FR-006)."""
        criar_ouvinte("2026123456")
        self.assertRecusa(lambda: criar_ouvinte("2026123456"))

    def test_fk_composta_recusa_avaliador_fora_da_banca(self):
        """Só membros da banca daquela defesa podem ser avaliados (FK composta, FR-005, D3)."""
        defesa, criterio, estranho = f.criar_defesa(), f.criar_criterio(), f.criar_usuario()
        self.assertRecusa(
            lambda: Avaliacoes.objects.create(
                ava_def=defesa,
                ava_usu=estranho,
                ava_cri=criterio,
                ava_conceito=Conceito.EXEMPLAR,
                ava_nota=Decimal("9.0"),
                ava_data_hora=f.AGORA,
            ),
            imediato=True,
        )
        membro = f.criar_membro_banca(defesa=defesa)
        self.assertAceita(lambda: avaliar(membro, criterio))

    def test_exclusao_banca_com_avaliacao(self):
        """Excluir membro com avaliações dá IntegrityError, não ProtectedError (contrato §4)."""
        membro = f.criar_membro_banca()
        avaliar(membro, f.criar_criterio())
        self.assertRecusa(lambda: BancaDefesa.objects.filter(pk=membro.pk).delete(), imediato=True)

    def test_pk_composta_recusa_duplicata(self):
        """As PKs compostas de Banca_Defesa, Presenca_Ouvintes e Avaliacoes recusam duplicatas."""
        defesa, usuario = f.criar_defesa(), f.criar_usuario()
        self.assertAceita(lambda: f.criar_membro_banca(defesa=defesa, usuario=usuario))
        self.assertRecusa(lambda: f.criar_membro_banca(defesa=defesa, usuario=usuario))
        self.assertAceita(lambda: f.criar_membro_banca(defesa=defesa))

        ouvinte = criar_ouvinte()
        self.assertAceita(lambda: PresencaOuvintes.objects.create(pre_def=defesa, pre_ouv=ouvinte))
        self.assertRecusa(lambda: PresencaOuvintes.objects.create(pre_def=defesa, pre_ouv=ouvinte))
        self.assertAceita(
            lambda: PresencaOuvintes.objects.create(pre_def=f.criar_defesa(), pre_ouv=ouvinte)
        )

        membro = BancaDefesa.objects.get(ban_def=defesa, ban_usu=usuario)
        criterio = f.criar_criterio()
        self.assertAceita(lambda: avaliar(membro, criterio))
        self.assertRecusa(lambda: avaliar(membro, criterio))
        self.assertAceita(lambda: avaliar(membro, f.criar_criterio()))


class PapelOrdinalTest(TestCase):
    """O "º" de 1º e 2º Avaliador é o indicador ordinal U+00BA (data-model, M9)."""

    def test_ordinal(self):
        self.assertEqual(PapelBanca.PRIMEIRO_AVALIADOR[1], "º")
        self.assertEqual(PapelBanca.SEGUNDO_AVALIADOR[1], "º")
