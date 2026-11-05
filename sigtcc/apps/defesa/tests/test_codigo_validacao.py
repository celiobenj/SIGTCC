"""Código de validação da declaração de participação (spec 009, research B6; FR-020; SC-004):
16 caracteres Base32, determinístico, diferente por membro e por sessão e dependente da
SECRET_KEY.

[US-30][RBN-DEF-08.3] (spec 009, tasks T012)
"""

import re
from types import SimpleNamespace

from django.test import SimpleTestCase, override_settings

from sigtcc.apps.defesa import services_documentos

BASE32 = re.compile(r"^[A-Z2-7]{16}$")


def objeto(pk):
    """Sessão ou usuário mínimos: o código só usa o pk. [US-30][RBN-DEF-08.3]"""
    return SimpleNamespace(pk=pk)


class TesteCodigoDeValidacao(SimpleTestCase):
    """codigo_de_validacao e codigo_formatado. [US-30][RBN-DEF-08.3]"""

    def test_so_letras_maiusculas_e_digitos_de_2_a_7_com_16_caracteres(self):
        for def_id, usu_id in ((1, 1), (7, 42), (12345, 999999)):
            with self.subTest(def_id=def_id, usu_id=usu_id):
                codigo = services_documentos.codigo_de_validacao(objeto(def_id), objeto(usu_id))
                self.assertRegex(codigo, BASE32)

    def test_igual_em_duas_chamadas(self):
        """SC-004: a segunda via sai com o mesmo código do e-mail. [US-30][RBN-DEF-08.3]"""
        primeiro = services_documentos.codigo_de_validacao(objeto(7), objeto(42))
        segundo = services_documentos.codigo_de_validacao(objeto(7), objeto(42))
        self.assertEqual(primeiro, segundo)

    def test_diferente_entre_membros_e_entre_sessoes(self):
        codigo = services_documentos.codigo_de_validacao
        base = codigo(objeto(7), objeto(42))
        self.assertNotEqual(base, codigo(objeto(7), objeto(43)))
        self.assertNotEqual(base, codigo(objeto(8), objeto(42)))
        # "7:42" e "74:2" não podem colidir pela concatenação.
        self.assertNotEqual(codigo(objeto(7), objeto(42)), codigo(objeto(74), objeto(2)))

    def test_muda_com_outra_secret_key(self):
        """Risco aceito (research B6): trocar a SECRET_KEY muda os códigos. [US-30]"""
        atual = services_documentos.codigo_de_validacao(objeto(7), objeto(42))
        with override_settings(SECRET_KEY="outra-chave-de-teste-" + "x" * 40):
            outro = services_documentos.codigo_de_validacao(objeto(7), objeto(42))
        self.assertRegex(outro, BASE32)
        self.assertNotEqual(atual, outro)

    def test_formatado_em_quatro_grupos(self):
        self.assertEqual(
            services_documentos.codigo_formatado("ABCDEFGHIJKLMNOP"), "ABCD EFGH IJKL MNOP"
        )
