"""US-30, ouvintes da sessão (User Story 2 da spec 009): cenários 2.1 a 2.12, o FR-009 ("os
demais perfis não veem a lista"), a corrida da turma arquivada (403, não 500), o TOTAL_FORMS
adulterado e a linha extra vazia.

[US-30][RBN-DEF-08.2] (spec 009, tasks T029)
"""

from unittest import mock

from django.urls import reverse

from sigtcc.apps.cadastro.choices import StatusTurma
from sigtcc.apps.cadastro.models import Turmas
from sigtcc.apps.cadastro.services_turmas import TurmaArquivada
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_secretaria
from sigtcc.apps.defesa.choices import StatusSessao
from sigtcc.apps.defesa.models import Ouvintes, PresencaOuvintes
from sigtcc.apps.defesa.tests.apoio_avaliacao import TesteAvaliacao, sessao_com_banca
from sigtcc.apps.defesa.tests.apoio_defesa import docente
from sigtcc.apps.defesa.tests.apoio_documentos import ouvinte, presenca, sessao_liberada

SALVOS = "Ouvintes salvos com sucesso"
MATRICULA = "A matrícula deve conter exatamente 10 dígitos numéricos"
REPETIDO = "Este aluno já foi registrado como ouvinte nesta defesa"
NOME = "O nome deve conter apenas letras, acentos e espaços e ter até 150 caracteres"
FORA_DO_STATUS = "O registro de ouvintes fica disponível apenas durante ou após a sessão"
M02 = "Você não tem permissão para esta ação"


def dados(linhas, iniciais=0, remover=(), total=None):
    """POST do formset "ouv": `linhas` = [(nome, matrícula)]; `remover` = índices marcados em
    Remover; `total` adultera o TOTAL_FORMS. [US-30][RBN-DEF-08.2]
    """
    corpo = {
        "ouv-TOTAL_FORMS": str(len(linhas) if total is None else total),
        "ouv-INITIAL_FORMS": str(iniciais),
        "ouv-MIN_NUM_FORMS": "0",
        "ouv-MAX_NUM_FORMS": "200",
    }
    for indice, (nome, matricula) in enumerate(linhas):
        corpo[f"ouv-{indice}-nome"] = nome
        corpo[f"ouv-{indice}-matricula"] = matricula
        if indice in remover:
            corpo[f"ouv-{indice}-DELETE"] = "on"
    return corpo


class BaseOuvintes(TesteAvaliacao):
    """Janela Ouvintes e bloco ouvintes da sessão. [US-30][RBN-DEF-08.2]"""

    def url(self, sessao):
        """Endereço da janela Ouvintes. [US-30]"""
        return reverse("defesa:ouvintes", args=[sessao.pk])

    def url_sessao(self, sessao):
        """Endereço da janela Sessão de defesa. [US-30]"""
        return reverse("defesa:sessao", args=[sessao.pk])

    def salvar(self, usuario, sessao, corpo, follow=False):
        """POST da janela Ouvintes como o usuário. [US-30][RBN-DEF-08.2]"""
        self.client.force_login(usuario)
        return self.client.post(self.url(sessao), corpo, follow=follow)

    def janela(self, usuario, sessao):
        """HTML da janela Sessão de defesa como o usuário. [US-30][RBN-DEF-08.2]"""
        self.client.force_login(usuario)
        return self.client.get(self.url_sessao(sessao))

    def matriculas(self, sessao):
        """Matrículas com presença na sessão. [US-30][RBN-DEF-08.2]"""
        return set(
            PresencaOuvintes.objects.filter(pre_def=sessao).values_list(
                "pre_ouv__ouv_matricula", flat=True
            )
        )


class TesteRegistroDeOuvintes(BaseOuvintes):
    """Cenários 2.1, 2.2, 2.3 e 2.11, a linha vazia e o GET. [US-30][RBN-DEF-08.2]"""

    def test_cenario_2_1_orientador_adiciona_dois(self):
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        sessao = cenario["sessao"]
        corpo = dados([("Ana Souza", "2022010001"), ("João Araújo", "2022010002")])
        resposta = self.salvar(cenario["orientador"], sessao, corpo, follow=True)
        self.assertRedirects(resposta, self.url_sessao(sessao))
        self.assertContains(resposta, SALVOS)
        self.assertEqual(self.matriculas(sessao), {"2022010001", "2022010002"})
        self.assertEqual(Ouvintes.objects.get(ouv_matricula="2022010002").ouv_nome, "João Araújo")
        self.assertContains(resposta, "João Araújo")

    def test_cenario_2_2_professor_na_sessao_realizada(self):
        for cenario in (sessao_com_banca(StatusSessao.REALIZADA), sessao_liberada()):
            sessao = cenario["sessao"]
            with self.subTest(sessao=sessao.pk):
                resposta = self.salvar(
                    cenario["professor"], sessao, dados([("Maria Luísa", "2022010003")])
                )
                self.assertRedirects(resposta, self.url_sessao(sessao))
                self.assertEqual(self.matriculas(sessao), {"2022010003"})

    def test_cenario_2_3_remover_mantem_o_registro(self):
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        sessao = cenario["sessao"]
        presenca(sessao, ouvinte("2022010001", "Ana Souza"))
        presenca(sessao, ouvinte("2022010002", "Beto Lima"))
        self.client.force_login(cenario["orientador"])
        pagina = self.client.get(self.url(sessao))
        self.assertContains(pagina, 'value="2022010001"')
        self.assertContains(pagina, 'value="Beto Lima"')
        corpo = dados(
            [("Ana Souza", "2022010001"), ("Beto Lima", "2022010002"), ("", "")],
            iniciais=2,
            remover={1},
        )
        self.assertRedirects(
            self.salvar(cenario["orientador"], sessao, corpo), self.url_sessao(sessao)
        )
        self.assertEqual(self.matriculas(sessao), {"2022010001"})
        self.assertTrue(Ouvintes.objects.filter(ouv_matricula="2022010002").exists())

    def test_cenario_2_11_nome_gravado_mantido(self):
        outra = sessao_com_banca(StatusSessao.REALIZADA)["sessao"]
        presenca(outra, ouvinte("2022010001", "Ana Souza"))
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        sessao = cenario["sessao"]
        resposta = self.salvar(
            cenario["orientador"], sessao, dados([("Ana Maria Souza", "2022010001")]), True
        )
        self.assertContains(resposta, SALVOS)
        self.assertEqual(Ouvintes.objects.filter(ouv_matricula="2022010001").count(), 1)
        self.assertEqual(Ouvintes.objects.get(ouv_matricula="2022010001").ouv_nome, "Ana Souza")
        self.assertEqual(self.matriculas(sessao), {"2022010001"})
        self.assertEqual(self.matriculas(outra), {"2022010001"})

    def test_linha_extra_vazia_e_ignorada(self):
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        sessao = cenario["sessao"]
        corpo = dados([("Ana Souza", "2022010001"), ("", "")])
        self.assertRedirects(
            self.salvar(cenario["orientador"], sessao, corpo), self.url_sessao(sessao)
        )
        self.assertEqual(self.matriculas(sessao), {"2022010001"})

    def test_janela_tem_adicionar_cancelar_e_salvar(self):
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        self.client.force_login(cenario["orientador"])
        pagina = self.client.get(self.url(cenario["sessao"]))
        for texto in ("Nome Completo", "Matrícula", "Remover", "Adicionar", "Cancelar", "Salvar"):
            self.assertContains(pagina, texto)
        self.assertContains(pagina, "js/ouvintes.js")


class TesteValidacao(BaseOuvintes):
    """Cenários 2.4, 2.5 e 2.6: nada é gravado e o campo é destacado. [US-30][RBN-DEF-08.2]"""

    def setUp(self):
        super().setUp()
        self.cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        self.sessao = self.cenario["sessao"]

    def recusar(self, linhas, mensagem, **extras):
        """POST recusado na própria janela, com a mensagem e o destaque. [US-30]"""
        resposta = self.salvar(self.cenario["orientador"], self.sessao, dados(linhas, **extras))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, mensagem)
        self.assertContains(resposta, "inp erro")
        return resposta

    def test_cenario_2_4_matricula_invalida(self):
        for matricula in ("12345678", "12345abc90", "", "20220100011"):
            with self.subTest(matricula=matricula):
                self.recusar([("Ana Souza", "2022010001"), ("Beto Lima", matricula)], MATRICULA)
                self.assertEqual(self.matriculas(self.sessao), set())
        self.assertFalse(Ouvintes.objects.exists())

    def test_cenario_2_5_matricula_repetida(self):
        self.recusar([("Ana Souza", "2022010001"), ("Ana S", "2022010001")], REPETIDO)
        self.assertEqual(self.matriculas(self.sessao), set())
        # Já consta como ouvinte e é adicionado de novo numa linha nova.
        presenca(self.sessao, ouvinte("2022010001", "Ana Souza"))
        self.recusar(
            [("Ana Souza", "2022010001"), ("Ana Souza", "2022010001")], REPETIDO, iniciais=1
        )
        self.assertEqual(self.matriculas(self.sessao), {"2022010001"})

    def test_cenario_2_6_nome_invalido(self):
        for nome in ("Ana 2", "", "   ", "Ana × Beto", "A" * 151):
            with self.subTest(nome=nome):
                self.recusar([(nome, "2022010001")], NOME)
        self.assertFalse(Ouvintes.objects.exists())
        # Acentos e espaços são aceitos.
        corpo = dados([("Ângela Conceição", "2022010001")])
        self.assertRedirects(
            self.salvar(self.cenario["orientador"], self.sessao, corpo),
            self.url_sessao(self.sessao),
        )

    def test_total_forms_adulterado(self):
        linhas = [(f"Aluno {chr(65 + i % 26)}", f"{2022000000 + i}") for i in range(201)]
        resposta = self.salvar(self.cenario["orientador"], self.sessao, dados(linhas))
        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(Ouvintes.objects.exists())
        resposta = self.salvar(
            self.cenario["orientador"],
            self.sessao,
            dados([("Ana Souza", "2022010001")], total=100000),
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(Ouvintes.objects.exists())


class TesteVisibilidadeEPermissoes(BaseOuvintes):
    """Cenários 2.7, 2.8, 2.9, 2.10 e 2.12, o FR-009 e a corrida da turma arquivada.
    [US-30][RBN-DEF-08.2]
    """

    def test_cenario_2_7_agendada_reagendada_e_cancelada(self):
        for status in (StatusSessao.AGENDADA, StatusSessao.REAGENDADA, StatusSessao.CANCELADA):
            cenario = sessao_com_banca(status)
            sessao = cenario["sessao"]
            for chave in ("orientador", "professor"):
                with self.subTest(status=status, perfil=chave):
                    pagina = self.janela(cenario[chave], sessao)
                    self.assertContains(pagina, FORA_DO_STATUS)
                    self.assertNotContains(pagina, self.url(sessao))
                    self.client.force_login(cenario[chave])
                    self.assertEqual(self.client.get(self.url(sessao)).status_code, 403)
                    resposta = self.salvar(cenario[chave], sessao, dados([("Ana", "2022010001")]))
                    self.assertEqual(resposta.status_code, 403)
            self.assertFalse(PresencaOuvintes.objects.filter(pre_def=sessao).exists())

    def test_cenario_2_8_outro_docente(self):
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        sessao = cenario["sessao"]
        for usuario in (docente(), cenario["av1"], cenario["suplente"], cenario["coordenador"]):
            with self.subTest(usuario=usuario.pk):
                self.client.force_login(usuario)
                self.assertContains(self.client.get(self.url(sessao)), M02, status_code=403)
                resposta = self.salvar(usuario, sessao, dados([("Ana Souza", "2022010001")]))
                self.assertContains(resposta, M02, status_code=403)
        self.assertFalse(PresencaOuvintes.objects.exists())

    def test_cenario_2_9_login_e_depois_a_tela(self):
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        sessao = cenario["sessao"]
        for endereco in (self.url_sessao(sessao), self.url(sessao)):
            with self.subTest(endereco=endereco):
                self.client.logout()
                resposta = self.client.get(endereco)
                self.assertEqual(resposta.status_code, 302)
                self.assertIn(reverse("cadastro:entrar"), resposta["Location"])
                self.assertIn("next=", resposta["Location"])
                self.client.force_login(cenario["orientador"])
                self.assertEqual(self.client.get(endereco).status_code, 200)

    def test_cenario_2_10_secretaria_so_leitura(self):
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        sessao = cenario["sessao"]
        presenca(sessao, ouvinte("2022010001", "Ana Souza"))
        secretaria = criar_secretaria(curso=cenario["tcc"].tcc_tur.tur_cur)
        pagina = self.janela(secretaria, sessao)
        self.assertContains(pagina, "data-bloco-ouvintes")
        self.assertContains(pagina, "Ana Souza")
        self.assertNotContains(pagina, self.url(sessao))
        self.assertNotContains(pagina, "Adicionar")
        self.assertNotContains(pagina, FORA_DO_STATUS)
        self.client.force_login(secretaria)
        self.assertEqual(self.client.get(self.url(sessao)).status_code, 403)
        resposta = self.salvar(secretaria, sessao, dados([("Beto Lima", "2022010002")]))
        self.assertEqual(resposta.status_code, 403)
        self.assertEqual(self.matriculas(sessao), {"2022010001"})

    def test_cenario_2_12_turma_arquivada(self):
        cenario = sessao_liberada()
        sessao = cenario["sessao"]
        presenca(sessao, ouvinte("2022010001", "Ana Souza"))
        Turmas.objects.filter(pk=cenario["tcc"].tcc_tur_id).update(tur_status=StatusTurma.ARQUIVADA)
        for chave in ("orientador", "professor"):
            with self.subTest(perfil=chave):
                pagina = self.janela(cenario[chave], sessao)
                self.assertContains(pagina, "Ana Souza")
                self.assertNotContains(pagina, self.url(sessao))
                resposta = self.salvar(cenario[chave], sessao, dados([("Beto Lima", "2022010002")]))
                self.assertContains(resposta, M02, status_code=403)
        self.assertEqual(self.matriculas(sessao), {"2022010001"})

    def test_fr_009_demais_perfis_nao_veem_a_lista(self):
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        sessao = cenario["sessao"]
        presenca(sessao, ouvinte("2022010001", "Ana Souza"))
        for chave in ("av1", "av2", "suplente", "aluno"):
            with self.subTest(perfil=chave):
                pagina = self.janela(cenario[chave], sessao)
                self.assertEqual(pagina.status_code, 200)
                self.assertNotContains(pagina, "data-bloco-ouvintes")
                self.assertNotContains(pagina, "Ana Souza")

    def test_corrida_da_turma_arquivada_vira_403(self):
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        sessao = cenario["sessao"]
        with mock.patch(
            "sigtcc.apps.defesa.services_defesa.travar_tcc",
            side_effect=TurmaArquivada(cenario["tcc"].tcc_tur),
        ):
            resposta = self.salvar(
                cenario["orientador"], sessao, dados([("Ana Souza", "2022010001")])
            )
        self.assertContains(resposta, M02, status_code=403)
        self.assertFalse(Ouvintes.objects.exists())
