"""Carga inicial dos domínios fixos do app cadastro (data migrations 0003 e 0004).

O banco de teste é criado com todas as migrações, então a carga já está aplicada.

[US-39][RBN-CAD-14.1][US-13][RBN-CAD-08.1][US-08][RBN-CAD-05.7][spec 001, US3 cenários 1, 3, 4 e 5]
[FR-013][FR-015][FR-016][FR-017][SC-004][SC-005]
"""

from django.apps import apps
from django.test import TestCase

from sigtcc.apps.cadastro import cargas
from sigtcc.apps.cadastro.models import AreasInteresse, Cursos, EquivalenciaCursos

CURSOS = ["Engenharia de Computação", "Sistemas de Informação", "Licenciatura em Computação"]

AREAS = [
    "Engenharia de Software",
    "Inteligência Artificial",
    "Redes de Computadores",
    "Banco de Dados",
    "Sistemas Embarcados",
    "Segurança da Informação",
    "Interação Humano-Computador",
    "Ciência de Dados",
    "Computação Gráfica",
    "Educação em Computação",
]


class CargaInicialCadastroTest(TestCase):
    """Cenários da US3 da spec 001 para o app cadastro."""

    def test_cenario1_cursos(self):
        """Dada a carga aplicada, então existem exatamente os 3 cursos do NUCOMP (FR-013)."""
        self.assertCountEqual(Cursos.objects.values_list("cur_nome", flat=True), CURSOS)
        self.assertFalse(Cursos.objects.filter(cur_descricao__isnull=False).exists())

    def test_cenario3_areas(self):
        """Dada a carga aplicada, então existem exatamente as 10 áreas de RBN-CAD-08.1 (FR-015)."""
        self.assertCountEqual(AreasInteresse.objects.values_list("ari_nome", flat=True), AREAS)

    def test_cenario4_equivalencia_vazia(self):
        """A carga da spec 001 não insere nada em Equivalencia_Cursos (FR-016).

        Os códigos confirmados entram depois, pela carga da spec 004 (FR-015a; Q-17 do índice):
        a tabela só pode conter os códigos dessa carga.
        """
        codigos = set(EquivalenciaCursos.objects.values_list("eqc_codigo_uea", flat=True))
        self.assertEqual(codigos, {codigo for codigo, _ in cargas.EQUIVALENCIA_CURSOS})

    def test_cenario5_reaplicacao(self):
        """Aplicar a carga de novo não duplica nem muda identificadores (FR-017, SC-005)."""
        antes_cursos = sorted(Cursos.objects.values_list("cur_id", "cur_nome"))
        antes_areas = sorted(AreasInteresse.objects.values_list("ari_id", "ari_nome"))
        cargas.carregar_cursos(apps, None)
        cargas.carregar_areas_interesse(apps, None)
        self.assertEqual(sorted(Cursos.objects.values_list("cur_id", "cur_nome")), antes_cursos)
        self.assertEqual(
            sorted(AreasInteresse.objects.values_list("ari_id", "ari_nome")), antes_areas
        )

    def test_fr017_nenhuma_outra_tabela_do_cadastro_com_dados(self):
        """A carga não insere usuários, turmas, TCCs nem nada além dos dois domínios (FR-017)."""
        for modelo in apps.get_app_config("cadastro").get_models():
            # Equivalencia_Cursos recebe a carga da spec 004 (FR-015a), conferida no cenário 4.
            if modelo in (Cursos, AreasInteresse, EquivalenciaCursos):
                continue
            with self.subTest(tabela=modelo._meta.db_table):
                self.assertEqual(modelo.objects.count(), 0)
