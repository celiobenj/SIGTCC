"""Carga inicial dos 9 critérios oficiais, com descritores provisórios (data migration 0004).

[US-25][RBN-DEF-04.1][spec 001, US3 cenários 2 e 5][FR-014][FR-017][SC-004][SC-005]
"""

from decimal import Decimal

from django.apps import apps
from django.db.models import Sum
from django.test import TestCase

from sigtcc.apps.defesa import cargas
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

DESCRITORES = {
    "cri_desc_exemplar": (
        "PROVISÓRIO – Exemplar (nota de 8,0 a 10,0). "
        "Texto oficial pendente da planilha de avaliação da EST/UEA."
    ),
    "cri_desc_competente": (
        "PROVISÓRIO – Competente (nota de 6,0 a 7,9). "
        "Texto oficial pendente da planilha de avaliação da EST/UEA."
    ),
    "cri_desc_necessita_trabalho": (
        "PROVISÓRIO – Necessita de Trabalho (nota de 0,0 a 5,9). "
        "Texto oficial pendente da planilha de avaliação da EST/UEA."
    ),
}


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

    def test_descritores_provisorios(self):
        """Os 27 descritores são os textos provisórios, até 255 caracteres (FR-014)."""
        for criterio in Criterios.objects.all():
            self.assertIsNone(criterio.cri_descricao)
            for campo, texto in DESCRITORES.items():
                with self.subTest(criterio=criterio.cri_nome, campo=campo):
                    valor = getattr(criterio, campo)
                    self.assertEqual(valor, texto)
                    self.assertTrue(valor.startswith("PROVISÓRIO"))
                    self.assertLessEqual(len(valor), 255)

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
