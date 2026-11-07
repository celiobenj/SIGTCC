"""Permissões do módulo Relatórios: recorte do Docente, cenários 1.12 e 1.13.

[US-31][RBN-REL-01.1][RAN-REL-01][FR-004][FR-016][SC-004] (tasks T023)
"""

import csv
from io import StringIO

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
from sigtcc.apps.relatorios import mensagens
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
    """2.9 e 2.10: quem não é Coordenador não vê na lista nem abre por endereço. [FR-004][SC-004]"""

    RELATORIOS = ("producao-tccs", "artigos")

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
