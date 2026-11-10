"""US-25, janela Critérios de avaliação (User Story 1 da spec 008): cenários 1.1 e 1.2.

[US-25][RBN-DEF-04.1][RBN-DEF-04.2][FR-001][FR-002] (tasks T016)
"""

from django.urls import get_resolver, reverse

from sigtcc.apps.cadastro.choices import StatusConta
from sigtcc.apps.cadastro.tests.apoio_acesso import (
    criar_coordenador,
    criar_membro_externo,
    criar_secretaria,
)
from sigtcc.apps.cadastro.tests.apoio_turmas import TesteTurmas, criar_aluno_novo
from sigtcc.apps.defesa.models import Criterios
from sigtcc.apps.defesa.tests.apoio_defesa import docente

CRITERIOS = reverse("defesa:criterios")

ESCRITA = [
    ("Relevância do Tema", "0,5"),
    ("Metodologia", "2,0"),
    ("Revisão da Literatura", "1,0"),
    ("Resultados e Discussões", "2,0"),
    ("Conclusões", "0,5"),
    ("Redação", "1,0"),
]
ORAL = [("Organização", "1,0"), ("Domínio do Assunto", "1,5"), ("Postura perante a Banca", "0,5")]


class TesteCriterios(TesteTurmas):
    """Cenários 1.1 e 1.2. [US-25][RBN-DEF-04.1][RBN-DEF-04.2]"""

    def test_cenario_1_1_nove_criterios_pesos_somas_e_descricoes(self):
        for usuario in (docente(), criar_membro_externo()):
            with self.subTest(usuario=usuario.usu_email):
                self.client.force_login(usuario)
                resposta = self.client.get(CRITERIOS)
                self.assertEqual(resposta.status_code, 200)
                texto = resposta.content.decode()
                for nome, peso in ESCRITA + ORAL:
                    self.assertIn(nome, texto)
                    self.assertIn(f'<td class="nw">{peso}</td>', texto)
                self.assertIn("<b>7,0</b>", texto)
                self.assertIn("<b>3,0</b>", texto)
                self.assertIn("<b>10,0</b>", texto)
                for faixa in (
                    "Exemplar (8,0 a 10,0)",
                    "Competente (6,0 a 7,9)",
                    "Necessita de Trabalho (0,0 a 5,9)",
                ):
                    self.assertIn(faixa, texto)
                criterio = Criterios.objects.first()
                self.assertContains(resposta, criterio.cri_desc_exemplar)

    def test_cenario_1_2_somente_leitura_para_todos(self):
        self.client.force_login(criar_coordenador())
        resposta = self.client.get(CRITERIOS)
        self.assertEqual(resposta.status_code, 200)
        self.assertNotIn("<form", resposta.content.decode().split("<main>", 1)[1])
        antes = list(Criterios.objects.values_list("cri_id", "cri_nome", "cri_peso"))
        self.assertEqual(self.client.post(CRITERIOS, {"cri_peso": "5,0"}).status_code, 200)
        self.assertEqual(
            list(Criterios.objects.values_list("cri_id", "cri_nome", "cri_peso")), antes
        )
        # Nenhuma rota do sistema grava critérios.
        nomes = {nome for nome in get_resolver().reverse_dict if isinstance(nome, str)}
        self.assertFalse([nome for nome in nomes if "criterio" in nome and nome != "criterios"])

    def test_cenario_1_2_aluno_e_secretaria_sem_acesso(self):
        for usuario in (criar_aluno_novo(status_conta=StatusConta.ATIVA).alu, criar_secretaria()):
            with self.subTest(usuario=usuario.usu_email):
                self.client.force_login(usuario)
                self.assertEqual(self.client.get(CRITERIOS).status_code, 403)
