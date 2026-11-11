"""Permissões do módulo Relatórios: recorte do Docente, cenários 1.12 e 1.13, relatórios do
Coordenador e a matriz completa de perfis.

[US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RAN-REL-01][FR-004][FR-005][FR-016]
[SC-004] (tasks T023, T030, T037, T044 e T048)
"""

import csv
from io import StringIO

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from sigtcc.apps.cadastro.choices import DescricaoTurma, StatusConta
from sigtcc.apps.cadastro.models import Usuarios
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_usuario
from sigtcc.apps.cadastro.tests.apoio_contas import (
    coordenador_de,
    docente_de,
    membro,
    secretaria_de,
)
from sigtcc.apps.cadastro.tests.apoio_orientacao import vincular_coorientador
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, criar_turma_de, curso
from sigtcc.apps.relatorios import mensagens, registro
from sigtcc.apps.relatorios.tests.apoio_relatorios import TesteRelatorios, aluno_com_status

ID = "atividades-docente"


class TesteRecorteDoDocente(TesteRelatorios):
    """1.12: fora da gestão, só a própria linha, mesmo trocando o endereço. [FR-016]"""

    def setUp(self):
        super().setUp()
        self.professor = docente_de(EC)
        self.turma = criar_turma_de(self.professor)
        self.outro = docente_de(EC)
        Usuarios.objects.filter(pk=self.outro.pk).update(usu_nome="Docente Sigiloso")
        self.tcc = aluno_com_status(self.turma, orientador=self.outro)
        self.consulta = f"?docente={self.outro.pk}&curso={curso(EC).pk}&curso=todos"

    def perfis_sem_gestao(self):
        """Docente puro, Professor, Orientador e Coorientador."""
        puro = docente_de(EC)
        orientador = docente_de(EC)
        aluno_com_status(self.turma, orientador=orientador)
        coorientador = docente_de(EC)
        vincular_coorientador(self.tcc, coorientador)
        return {
            "docente": puro,
            "professor": self.professor,
            "orientador": orientador,
            "coorientador": coorientador,
        }

    def test_tela(self):
        """O filtro forjado não entra na tela."""
        for nome, usuario in self.perfis_sem_gestao().items():
            with self.subTest(perfil=nome):
                self.client.force_login(usuario)
                resposta = self.client.get(
                    reverse("relatorios:relatorio", args=[ID]) + self.consulta
                )
                linhas = resposta.context["relatorio"].linhas
                self.assertEqual(len(linhas), 1)
                self.assertEqual(linhas[0].valores["docente"], usuario.usu_nome)
                self.assertNotContains(resposta, "Sigiloso")

    def test_exportacao(self):
        """Nem nos 3 formatos."""
        for nome, usuario in self.perfis_sem_gestao().items():
            self.client.force_login(usuario)
            for formato in ("pdf", "csv", "xlsx"):
                with self.subTest(perfil=nome, formato=formato):
                    resposta = self.client.get(
                        reverse("relatorios:exportar", args=[ID, formato]) + self.consulta
                    )
                    self.assertEqual(resposta.status_code, 200)
                    if formato == "csv":
                        texto = resposta.content.decode("utf-8-sig")
                        linhas = list(csv.reader(StringIO(texto), delimiter=";"))
                        self.assertNotIn("Sigiloso", texto)
                        self.assertIn([usuario.usu_nome], [linha[:1] for linha in linhas])

    def test_coordenador_escolhe_o_docente(self):
        """Na gestão, o filtro vale."""
        self.client.force_login(coordenador_de(EC))
        resposta = self.client.get(reverse("relatorios:relatorio", args=[ID]) + self.consulta)
        self.assertEqual(
            [item.valores["docente"] for item in resposta.context["relatorio"].linhas],
            ["Docente Sigiloso"],
        )


class TestePerfisSemModulo(TesteRelatorios):
    """1.13: Aluno, Membro Externo e conta sem especialização. [FR-001][FR-004]"""

    def setUp(self):
        super().setUp()
        turma = criar_turma_de(docente_de(EC), descricao=DescricaoTurma.TCC_1)
        self.perfis = {
            "aluno": aluno_com_status(turma, status_conta=StatusConta.ATIVA).tcc_alu.alu,
            "membro externo": membro(),
            "sem especialização": criar_usuario(),
        }
        self.rotas = [
            reverse("relatorios:lista"),
            reverse("relatorios:relatorio", args=[ID]),
            *(reverse("relatorios:exportar", args=[ID, f]) for f in ("pdf", "csv", "xlsx")),
        ]

    def test_negado_com_a_mr06(self):
        """Lista, tela e exportação."""
        for nome, usuario in self.perfis.items():
            self.client.force_login(usuario)
            for rota in self.rotas:
                with self.subTest(perfil=nome, rota=rota):
                    resposta = self.client.get(rota)
                    self.assertContains(resposta, mensagens.MR06_SEM_PERMISSAO, status_code=403)


class TesteRelatoriosDoCoordenador(TesteRelatorios):
    """2.9, 2.10, 3.8 e 3.9: quem não é Coordenador não vê na lista nem abre por endereço.

    [FR-004][SC-004]
    """

    RELATORIOS = ("producao-tccs", "artigos", "formacao-evasao", "historico-nucomp")

    def setUp(self):
        super().setUp()
        professor = docente_de(EC)
        criar_turma_de(professor)
        self.perfis = {
            "docente": docente_de(EC),
            "professor": professor,
            "secretaria": secretaria_de(EC),
        }

    def test_fora_da_lista(self):
        """2.9."""
        for nome, usuario in self.perfis.items():
            with self.subTest(perfil=nome):
                self.client.force_login(usuario)
                ids = [i.id for i in self.client.get(reverse("relatorios:lista")).context["lista"]]
                for relatorio in self.RELATORIOS:
                    self.assertNotIn(relatorio, ids)

    def test_endereco_direto(self):
        """2.10: tela e os 3 formatos."""
        for nome, usuario in self.perfis.items():
            self.client.force_login(usuario)
            for relatorio in self.RELATORIOS:
                rotas = [
                    reverse("relatorios:relatorio", args=[relatorio]),
                    *(
                        reverse("relatorios:exportar", args=[relatorio, formato])
                        for formato in ("pdf", "csv", "xlsx")
                    ),
                ]
                for rota in rotas:
                    with self.subTest(perfil=nome, rota=rota):
                        self.assertContains(
                            self.client.get(rota), mensagens.MR06_SEM_PERMISSAO, status_code=403
                        )


class TesteMembrosExternos(TesteRelatorios):
    """5.10: o Docente comum não abre, por tela nem por exportação; a Secretaria abre. [FR-004]"""

    def rotas(self):
        return [
            reverse("relatorios:relatorio", args=["membros-externos"]),
            *(
                reverse("relatorios:exportar", args=["membros-externos", formato])
                for formato in ("pdf", "csv", "xlsx")
            ),
        ]

    def test_docente_comum_negado(self):
        """5.10."""
        self.client.force_login(docente_de(EC))
        for rota in self.rotas():
            with self.subTest(rota=rota):
                self.assertContains(
                    self.client.get(rota), mensagens.MR06_SEM_PERMISSAO, status_code=403
                )

    def test_secretaria_e_coordenador_abrem(self):
        """US-47 D."""
        for usuario in (secretaria_de(EC), coordenador_de(EC)):
            self.client.force_login(usuario)
            self.assertEqual(self.client.get(self.rotas()[0]).status_code, 200)


TODOS = ("atividades-docente", "membros-externos", "producao-tccs", "artigos")
TODOS += ("formacao-evasao", "historico-nucomp")
# Relatórios operacionais da spec 011 (IC-02): Coordenador, Secretaria e Professor da Disciplina.
# [US-48][US-49][US-34][US-35][RAN-REL-03]
OPERACIONAIS = ("defesas-realizadas", "turmas-alunos", "aluno-orientador", "horas-ouvintes")
TODOS += OPERACIONAIS
SO_GESTAO = ("atividades-docente", "membros-externos", *OPERACIONAIS)


class TesteMatrizDePermissoes(TesteRelatorios):
    """6 relatórios × (lista, tela e 3 formatos) × 10 perfis. [FR-004][FR-005][SC-004]"""

    def setUp(self):
        super().setUp()
        professor = docente_de(EC)
        turma = criar_turma_de(professor)
        orientador, coorientador = docente_de(EC), docente_de(EC)
        tcc = aluno_com_status(turma, orientador=orientador, status_conta=StatusConta.ATIVA)
        vincular_coorientador(tcc, coorientador)
        # Perfil: relatórios que abre; None é o módulo inteiro negado.
        self.perfis = {
            "aluno": (tcc.tcc_alu.alu, None),
            "membro externo": (membro(), None),
            "sem especialização": (criar_usuario(), None),
            "docente": (docente_de(EC), ("atividades-docente",)),
            "professor": (professor, ("atividades-docente", *OPERACIONAIS)),
            "orientador": (orientador, ("atividades-docente",)),
            "coorientador": (coorientador, ("atividades-docente",)),
            "coordenador": (coordenador_de(EC), TODOS),
            "secretaria": (secretaria_de(EC), SO_GESTAO),
        }

    def rotas_de(self, relatorio):
        return [
            reverse("relatorios:relatorio", args=[relatorio]),
            *(
                reverse("relatorios:exportar", args=[relatorio, formato])
                for formato in ("pdf", "csv", "xlsx")
            ),
        ]

    def test_seis_relatorios_registrados(self):
        """Todo relatório do plan está registrado, e só eles."""
        self.assertEqual(set(TODOS), set(registro._RELATORIOS))

    def test_matriz(self):
        """Quem abre recebe a tela ou o arquivo; sem registros, volta ao relatório."""
        for nome, (usuario, permitidos) in self.perfis.items():
            self.client.force_login(usuario)
            lista = self.client.get(reverse("relatorios:lista"))
            self.assertEqual(lista.status_code, 403 if permitidos is None else 200, nome)
            if permitidos is not None:
                self.assertEqual(
                    {item.id for item in lista.context["lista"]}, set(permitidos), nome
                )
            for relatorio in TODOS:
                for rota in self.rotas_de(relatorio):
                    with self.subTest(perfil=nome, rota=rota):
                        resposta = self.client.get(rota)
                        if permitidos is not None and relatorio in permitidos:
                            self.assertIn(resposta.status_code, (200, 302))
                            if resposta.status_code == 302:
                                self.assertTrue(
                                    resposta["Location"].startswith(f"/relatorios/{relatorio}/")
                                )
                        else:
                            self.assertContains(
                                resposta, mensagens.MR06_SEM_PERMISSAO, status_code=403
                            )

    def test_anonimo_vai_ao_login(self):
        """O décimo perfil: sem sessão, login com o endereço pedido."""
        for relatorio in TODOS:
            for rota in [reverse("relatorios:lista"), *self.rotas_de(relatorio)]:
                with self.subTest(rota=rota):
                    resposta = self.client.get(rota)
                    self.assertEqual(resposta.status_code, 302)
                    self.assertIn(f"next={rota}", resposta["Location"])

    def test_id_e_formato_desconhecidos(self):
        """404 para id e formato; o formato só depois da permissão."""
        self.client.force_login(self.perfis["coordenador"][0])
        for rota in (
            reverse("relatorios:relatorio", args=["nao-existe"]),
            reverse("relatorios:exportar", args=["nao-existe", "csv"]),
            reverse("relatorios:exportar", args=["artigos", "doc"]),
        ):
            with self.subTest(rota=rota):
                self.assertEqual(self.client.get(rota).status_code, 404)

    def test_post_recusado(self):
        """FR-005: só GET, nas 3 rotas."""
        self.client.force_login(self.perfis["coordenador"][0])
        for rota in (reverse("relatorios:lista"), *self.rotas_de("artigos")):
            with self.subTest(rota=rota):
                self.assertEqual(self.client.post(rota).status_code, 405)

    def test_nenhuma_escrita(self):
        """FR-005: abrir e exportar não gravam nada."""
        self.client.force_login(self.perfis["coordenador"][0])
        for relatorio in TODOS:
            for rota in self.rotas_de(relatorio):
                with self.subTest(rota=rota), CaptureQueriesContext(connection) as contexto:
                    self.client.get(rota + "?curso=todos")
                escritas = [
                    consulta["sql"]
                    for consulta in contexto
                    if consulta["sql"].lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE"))
                    and "django_session" not in consulta["sql"]
                ]
                self.assertEqual(escritas, [])
