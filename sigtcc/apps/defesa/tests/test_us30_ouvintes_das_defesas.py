"""US-30, Ouvintes das defesas (User Story 4 da spec 009): cenários 4.1 a 4.7, o número constante
de consultas e o item de menu só da Secretaria.

[US-30][RBN-DEF-08.4][RBN-DEF-01.5][RBN-CAD-14.1] (spec 009, tasks T033)
"""

from datetime import date

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from sigtcc.apps.cadastro.tests.apoio_acesso import criar_membro_externo, criar_secretaria
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, SI, curso
from sigtcc.apps.defesa.choices import StatusSessao
from sigtcc.apps.defesa.models import Defesas
from sigtcc.apps.defesa.tests.apoio_avaliacao import TesteAvaliacao, sessao_com_banca
from sigtcc.apps.defesa.tests.apoio_defesa import docente
from sigtcc.apps.defesa.tests.apoio_documentos import ouvinte, presenca

NOVEMBRO = {"data_inicial": "01/11/2026", "data_final": "30/11/2026"}
MX07 = "Nenhum ouvinte encontrado para o período e filtros selecionados"
URL = "/ouvintes-das-defesas/"


class BaseOuvintesDasDefesas(TesteAvaliacao):
    """Secretaria de Engenharia de Computação e sessões com ouvintes. [US-30][RBN-DEF-08.4]"""

    def setUp(self):
        super().setUp()
        self.secretaria = criar_secretaria(curso=curso(EC))

    def consultar(self, usuario=None, **filtros):
        """GET da tela com os filtros (novembro de 2026 por padrão). [US-30][RBN-DEF-08.4]"""
        self.client.force_login(usuario or self.secretaria)
        return self.client.get(reverse("defesa:ouvintes_das_defesas"), {**NOVEMBRO, **filtros})

    def sessao_com_ouvintes(self, status=StatusSessao.REALIZADA, curso_nome=EC, ouvintes=()):
        """Sessão no status com as presenças dos ouvintes [(matrícula, nome)].
        [US-30][RBN-DEF-08.2][RBN-DEF-08.4]
        """
        cenario = sessao_com_banca(status, curso_nome=curso_nome)
        for matricula, nome in ouvintes:
            presenca(cenario["sessao"], ouvinte(matricula, nome))
        return cenario


class TesteListaDaSecretaria(BaseOuvintesDasDefesas):
    """Cenários 4.1 a 4.5. [US-30][RBN-DEF-08.4][RBN-DEF-01.5][RBN-CAD-14.1]"""

    def test_cenario_4_1_colunas(self):
        cenario = self.sessao_com_ouvintes(ouvintes=[("2022010001", "Ana Souza")])
        pagina = self.consultar()
        for coluna in (
            "Nome Completo",
            "Matrícula",
            "Título",
            "Aluno",
            "Orientador",
            "Data da defesa",
            "Horas complementares",
        ):
            self.assertContains(pagina, f"<th>{coluna}</th>", html=False)
        self.assertContains(pagina, "Ana Souza")
        self.assertContains(pagina, "2022010001")
        self.assertContains(pagina, cenario["tcc"].tcc_titulo)
        self.assertContains(pagina, cenario["aluno"].usu_nome)
        self.assertContains(pagina, cenario["orientador"].usu_nome)
        self.assertContains(pagina, "20/11/2026")
        self.assertContains(pagina, '<td class="nw">2 horas</td>', html=False)

    def test_cenario_4_2_duas_sessoes_duas_linhas(self):
        self.sessao_com_ouvintes(ouvintes=[("2022010001", "Ana Souza")])
        self.sessao_com_ouvintes(ouvintes=[("2022010001", "Ana Souza")])
        pagina = self.consultar()
        self.assertContains(pagina, "data-linha-ouvinte", count=2)
        self.assertContains(pagina, '<td class="nw">2 horas</td>', count=2, html=False)

    def test_cenario_4_3_so_sessoes_realizadas(self):
        self.sessao_com_ouvintes(StatusSessao.EM_ANDAMENTO, ouvintes=[("2022010001", "Ana Souza")])
        self.sessao_com_ouvintes(StatusSessao.CANCELADA, ouvintes=[("2022010002", "Beto Lima")])
        self.sessao_com_ouvintes(ouvintes=[("2022010003", "Carla Dias")])
        pagina = self.consultar()
        self.assertContains(pagina, "Carla Dias")
        self.assertNotContains(pagina, "Ana Souza")
        self.assertNotContains(pagina, "Beto Lima")

    def test_cenario_4_4_filtro_de_curso(self):
        self.sessao_com_ouvintes(ouvintes=[("2022010001", "Ana Souza")])
        self.sessao_com_ouvintes(curso_nome=SI, ouvintes=[("2022010002", "Beto Lima")])
        # Padrão: o curso da Secretaria (RBN-CAD-14.1).
        pagina = self.consultar()
        self.assertContains(pagina, "Ana Souza")
        self.assertNotContains(pagina, "Beto Lima")
        pagina = self.consultar(curso=str(curso(SI).pk))
        self.assertContains(pagina, "Beto Lima")
        self.assertNotContains(pagina, "Ana Souza")
        pagina = self.consultar(curso="todos")
        self.assertContains(pagina, "Ana Souza")
        self.assertContains(pagina, "Beto Lima")
        pagina = self.consultar(curso="abc")
        self.assertContains(pagina, "Ana Souza")
        self.assertNotContains(pagina, "Beto Lima")

    def test_filtro_de_periodo(self):
        cenario = self.sessao_com_ouvintes(ouvintes=[("2022010001", "Ana Souza")])
        Defesas.objects.filter(pk=cenario["sessao"].pk).update(def_data=date(2026, 12, 10))
        self.assertNotContains(self.consultar(), "Ana Souza")
        pagina = self.consultar(data_inicial="01/12/2026", data_final="31/12/2026")
        self.assertContains(pagina, "Ana Souza")
        pagina = self.consultar(data_inicial="31/12/2026", data_final="01/12/2026")
        self.assertContains(pagina, "A data inicial não pode ser superior à data final")

    def test_cenario_4_5_sem_ouvintes(self):
        self.sessao_com_ouvintes()
        self.assertContains(self.consultar(), MX07)

    def test_consultas_constantes(self):
        cenario = self.sessao_com_ouvintes(ouvintes=[("2022010001", "Ana Souza")])
        # Uma requisição antes, para os caches da sessão de login e do menu não contarem.
        self.consultar()
        with CaptureQueriesContext(connection) as uma:
            self.assertEqual(self.consultar().status_code, 200)
        for indice in range(2, 11):
            presenca(
                cenario["sessao"], ouvinte(f"20220100{indice:02d}", f"Aluno {chr(64 + indice)}")
            )
        with CaptureQueriesContext(connection) as dez:
            pagina = self.consultar()
        self.assertContains(pagina, "data-linha-ouvinte", count=10)
        self.assertEqual(len(uma), len(dez))


class TesteAcesso(BaseOuvintesDasDefesas):
    """Cenários 4.6 e 4.7 e o item de menu (P8). [US-30][RBN-DEF-08.4]"""

    def test_cenario_4_6_outros_perfis_recusados(self):
        cenario = sessao_com_banca(StatusSessao.REALIZADA)
        for usuario in (
            docente(),
            cenario["professor"],
            cenario["coordenador"],
            cenario["aluno"],
            criar_membro_externo(),
        ):
            with self.subTest(usuario=usuario.pk):
                self.client.force_login(usuario)
                resposta = self.client.get(URL)
                self.assertContains(
                    resposta, "Você não tem permissão para esta ação", status_code=403
                )

    def test_cenario_4_7_login_e_depois_a_tela(self):
        resposta = self.client.get(URL)
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("cadastro:entrar"), resposta["Location"])
        self.assertIn("next=", resposta["Location"])
        self.client.force_login(self.secretaria)
        self.assertEqual(self.client.get(URL).status_code, 200)

    def test_menu_so_da_secretaria(self):
        cenario = sessao_com_banca(StatusSessao.REALIZADA)
        self.client.force_login(self.secretaria)
        self.assertContains(self.client.get(reverse("cadastro:painel")), "Ouvintes das defesas")
        for usuario in (cenario["professor"], cenario["coordenador"], cenario["aluno"]):
            with self.subTest(usuario=usuario.pk):
                self.client.force_login(usuario)
                pagina = self.client.get(reverse("cadastro:painel"))
                self.assertNotContains(pagina, "Ouvintes das defesas")
