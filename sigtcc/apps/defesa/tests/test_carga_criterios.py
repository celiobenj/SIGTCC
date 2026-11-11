"""Carga dos 9 critérios oficiais (migration 0004) e dos descritores oficiais (migration 0005).

[US-25][RBN-DEF-04.1][spec 001, US3 cenários 2 e 5][FR-014][FR-017][SC-004][SC-005]
"""

import importlib
from decimal import Decimal

from django.apps import apps
from django.db.models import Sum
from django.test import TestCase

from sigtcc.apps.defesa import cargas, descritores_oficiais
from sigtcc.apps.defesa.models import Criterios

CRITERIOS = [
    ("Parte Escrita", "Relevância do Tema", Decimal("0.5")),
    ("Parte Escrita", "Metodologia", Decimal("2.0")),
    ("Parte Escrita", "Revisão da Literatura", Decimal("1.0")),
    ("Parte Escrita", "Resultados e Discussões", Decimal("2.0")),
    ("Parte Escrita", "Conclusões", Decimal("0.5")),
    ("Parte Escrita", "Redação", Decimal("1.0")),
    ("Parte Oral", "Organização", Decimal("1.0")),
    ("Parte Oral", "Domínio do Assunto", Decimal("1.5")),
    ("Parte Oral", "Postura perante a Banca", Decimal("0.5")),
]


class CargaCriteriosTest(TestCase):
    """Cenários da US3 da spec 001 para o app defesa."""

    def test_cenario2_nove_criterios(self):
        """Dada a carga aplicada, então existem exatamente os 9 critérios com componente e peso."""
        self.assertCountEqual(
            Criterios.objects.values_list("cri_componente", "cri_nome", "cri_peso"), CRITERIOS
        )

    def test_soma_dos_pesos(self):
        """Pesos: 7,0 na Parte Escrita, 3,0 na Parte Oral e 10,0 no total (RBN-DEF-04.1, SC-004)."""
        soma = dict(
            Criterios.objects.values("cri_componente")
            .annotate(total=Sum("cri_peso"))
            .values_list("cri_componente", "total")
        )
        self.assertEqual(soma, {"Parte Escrita": Decimal("7.0"), "Parte Oral": Decimal("3.0")})
        self.assertEqual(Criterios.objects.aggregate(t=Sum("cri_peso"))["t"], Decimal("10.0"))

    def test_descritores_oficiais(self):
        """Os 27 descritores são os da planilha oficial da EST/UEA, sem texto provisório."""
        oficiais = descritores_oficiais.DESCRITORES_OFICIAIS
        self.assertCountEqual(oficiais, [nome for _, nome, _ in CRITERIOS])
        for criterio in Criterios.objects.all():
            self.assertIsNone(criterio.cri_descricao)
            for campo, texto in oficiais[criterio.cri_nome].items():
                with self.subTest(criterio=criterio.cri_nome, campo=campo):
                    valor = getattr(criterio, campo)
                    self.assertEqual(valor, texto)
                    self.assertNotIn("PROVISÓRIO", valor)
                    self.assertLessEqual(len(valor), 1000)

    def test_reaplicacao_da_carga_nao_volta_ao_provisorio(self):
        """A carga da 0004 reaplicada não sobrescreve os descritores oficiais."""
        cargas.carregar_criterios_provisorios(apps, None)
        self.assertFalse(
            Criterios.objects.filter(cri_desc_exemplar__startswith="PROVISÓRIO").exists()
        )

    def test_reaplicacao(self):
        """Aplicar a carga de novo não duplica nem muda identificadores (FR-017, SC-005)."""
        antes = sorted(Criterios.objects.values_list("cri_id", "cri_nome"))
        cargas.carregar_criterios_provisorios(apps, None)
        self.assertEqual(sorted(Criterios.objects.values_list("cri_id", "cri_nome")), antes)

    def test_fr017_nenhuma_outra_tabela_do_defesa_com_dados(self):
        """A carga não insere defesas, bancas nem nada além dos critérios (FR-017)."""
        for modelo in apps.get_app_config("defesa").get_models():
            if modelo is Criterios:
                continue
            with self.subTest(tabela=modelo._meta.db_table):
                self.assertEqual(modelo.objects.count(), 0)


class MigracaoDescritoresTest(TestCase):
    """Hotfix v0.3.1: a 0005 roda num banco em que um popular_demo antigo esvaziou Criterios
    (deploy do Render de 11/11/2026). [US-25][RBN-DEF-04.1][FR-014a]
    """

    def aplicar_0005(self):
        migracao = importlib.import_module(
            "sigtcc.apps.defesa.migrations.0005_descritores_oficiais"
        )
        migracao.aplicar_descritores_oficiais(apps, None)

    def test_tabela_vazia_recarrega_e_aplica_os_oficiais(self):
        """Dado Criterios vazia, quando a 0005 roda, então os 9 critérios voltam com os oficiais."""
        Criterios.objects.all().delete()
        self.aplicar_0005()
        self.assertCountEqual(
            Criterios.objects.values_list("cri_componente", "cri_nome", "cri_peso"), CRITERIOS
        )
        self.assertFalse(
            Criterios.objects.filter(cri_desc_exemplar__startswith="PROVISÓRIO").exists()
        )

    def test_com_os_criterios_nao_duplica_nem_muda_ids(self):
        """Com os 9 critérios, a 0005 só grava os descritores (mesmos identificadores)."""
        antes = sorted(Criterios.objects.values_list("cri_id", "cri_nome"))
        self.aplicar_0005()
        self.assertEqual(sorted(Criterios.objects.values_list("cri_id", "cri_nome")), antes)
