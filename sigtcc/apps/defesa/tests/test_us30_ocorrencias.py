"""US-30, ocorrências da sessão (User Story 3 da spec 009): cenários 3.1 a 3.8, o limite com
quebras de linha CRLF, a corrida da turma arquivada e o Edge Case "Ocorrências e reagendamento".

[US-30][RBN-DEF-08.5] (spec 009, tasks T041)
"""

from datetime import date, time
from unittest import mock

from django.urls import reverse

from sigtcc.apps.cadastro import services_turmas
from sigtcc.apps.cadastro.choices import DescricaoTurma, StatusTurma
from sigtcc.apps.cadastro.models import Turmas
from sigtcc.apps.cadastro.services_turmas import TurmaArquivada
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_secretaria
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, criar_turma_de
from sigtcc.apps.defesa import services_defesa
from sigtcc.apps.defesa.choices import FormatoSessao, StatusSessao
from sigtcc.apps.defesa.models import Defesas, HistoricoDefesas
from sigtcc.apps.defesa.tests.apoio_avaliacao import TesteAvaliacao, sessao_com_banca
from sigtcc.apps.defesa.tests.apoio_defesa import avancar_para, docente
from sigtcc.apps.defesa.tests.apoio_documentos import ouvinte, presenca, sessao_liberada

SALVAS = "Ocorrências salvas com sucesso"
MX01 = "As ocorrências devem ter até 2.000 caracteres"
M02 = "Você não tem permissão para esta ação"
TEXTO = "Queda de energia por 10 minutos durante a arguição"


class BaseOcorrencias(TesteAvaliacao):
    """Janela Ocorrências e bloco ocorrencias da sessão. [US-30][RBN-DEF-08.5]"""

    def url(self, sessao):
        """Endereço da janela Ocorrências. [US-30]"""
        return reverse("defesa:ocorrencias", args=[sessao.pk])

    def url_sessao(self, sessao):
        """Endereço da janela Sessão de defesa. [US-30]"""
        return reverse("defesa:sessao", args=[sessao.pk])

    def salvar(self, usuario, sessao, texto, follow=False):
        """POST da janela Ocorrências como o usuário. [US-30][RBN-DEF-08.5]"""
        self.client.force_login(usuario)
        return self.client.post(self.url(sessao), {"ocorrencias": texto}, follow=follow)

    def janela(self, usuario, sessao):
        """HTML da janela Sessão de defesa como o usuário. [US-30][RBN-DEF-08.5]"""
        self.client.force_login(usuario)
        return self.client.get(self.url_sessao(sessao))

    def gravado(self, sessao):
        """def_ocorrencias relido do banco. [US-30][RBN-DEF-08.5]"""
        return Defesas.objects.get(pk=sessao.pk).def_ocorrencias


class TesteRegistro(BaseOcorrencias):
    """Cenários 3.1, 3.2 e 3.3. [US-30][RBN-DEF-08.5]"""

    def setUp(self):
        super().setUp()
        self.cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        self.sessao = self.cenario["sessao"]
        self.secretaria = criar_secretaria(curso=self.cenario["tcc"].tcc_tur.tur_cur)

    def test_cenario_3_1_grava_e_mostra_a_secretaria_e_ao_professor(self):
        eventos = HistoricoDefesas.objects.count()
        self.client.force_login(self.cenario["orientador"])
        pagina = self.client.get(self.url(self.sessao))
        self.assertContains(pagina, 'data-contador="2000"')
        self.assertContains(pagina, "js/contador.js")
        resposta = self.salvar(self.cenario["orientador"], self.sessao, TEXTO, follow=True)
        self.assertRedirects(resposta, self.url_sessao(self.sessao))
        self.assertContains(resposta, SALVAS)
        self.assertEqual(self.gravado(self.sessao), TEXTO)
        self.assertEqual(HistoricoDefesas.objects.count(), eventos)
        for usuario in (self.secretaria, self.cenario["professor"]):
            with self.subTest(usuario=usuario.pk):
                pagina = self.janela(usuario, self.sessao)
                self.assertContains(pagina, TEXTO)
                self.assertNotContains(pagina, self.url(self.sessao))

    def test_cenario_3_2_campo_vazio_e_permitido(self):
        self.salvar(self.cenario["orientador"], self.sessao, TEXTO)
        resposta = self.salvar(self.cenario["orientador"], self.sessao, "", follow=True)
        self.assertContains(resposta, SALVAS)
        self.assertIsNone(self.gravado(self.sessao))

    def test_cenario_3_3_acima_de_2000_nao_salva(self):
        resposta = self.salvar(self.cenario["orientador"], self.sessao, "a" * 2001)
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, MX01)
        self.assertContains(resposta, "inp erro")
        self.assertIsNone(self.gravado(self.sessao))

    def test_2000_com_quebras_crlf_aceito(self):
        # 1.000 linhas de "a" + quebra: 1.999 caracteres com LF, 2.998 com CRLF.
        texto = "\r\n".join(["a"] * 1000)
        resposta = self.salvar(self.cenario["orientador"], self.sessao, texto, follow=True)
        self.assertContains(resposta, SALVAS)
        self.assertEqual(self.gravado(self.sessao), "\n".join(["a"] * 1000))
        exato = "\r\n".join(["a" * 9] * 200)[:-1] + "b"
        self.assertEqual(len(exato.replace("\r\n", "\n")), 1999)
        exato += "c"
        resposta = self.salvar(self.cenario["orientador"], self.sessao, exato, follow=True)
        self.assertContains(resposta, SALVAS)
        self.assertEqual(len(self.gravado(self.sessao)), 2000)


class TesteLeituraEPermissoes(BaseOcorrencias):
    """Cenários 3.4 a 3.8, a corrida da turma arquivada e o reagendamento.
    [US-30][RBN-DEF-08.5]
    """

    def test_cenario_3_4_realizada_so_consulta(self):
        cenario = sessao_liberada()
        sessao, orientador = cenario["sessao"], cenario["orientador"]
        Defesas.objects.filter(pk=sessao.pk).update(def_ocorrencias=TEXTO)
        pagina = self.janela(orientador, sessao)
        self.assertContains(pagina, TEXTO)
        self.assertNotContains(pagina, self.url(sessao))
        self.client.force_login(orientador)
        self.assertContains(self.client.get(self.url(sessao)), M02, status_code=403)
        resposta = self.salvar(orientador, sessao, "Outro texto")
        self.assertContains(resposta, M02, status_code=403)
        self.assertEqual(self.gravado(sessao), TEXTO)

    def test_cenario_3_5_professor_da_disciplina_e_outros_recusados(self):
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        sessao = cenario["sessao"]
        for usuario in (cenario["professor"], cenario["av1"], docente(), cenario["coordenador"]):
            with self.subTest(usuario=usuario.pk):
                self.client.force_login(usuario)
                self.assertContains(self.client.get(self.url(sessao)), M02, status_code=403)
                resposta = self.salvar(usuario, sessao, TEXTO)
                self.assertContains(resposta, M02, status_code=403)
        self.assertNotContains(self.janela(cenario["professor"], sessao), self.url(sessao))
        self.assertIsNone(self.gravado(sessao))

    def test_cenario_3_6_avaliadores_suplente_e_aluno_nao_veem(self):
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        sessao = cenario["sessao"]
        Defesas.objects.filter(pk=sessao.pk).update(def_ocorrencias=TEXTO)
        for chave in ("av1", "av2", "suplente", "aluno"):
            with self.subTest(perfil=chave):
                pagina = self.janela(cenario[chave], sessao)
                self.assertEqual(pagina.status_code, 200)
                self.assertNotContains(pagina, TEXTO)
                self.assertNotContains(pagina, "data-bloco-ocorrencias")

    def test_cenario_3_7_login_e_depois_a_tela(self):
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        endereco = self.url(cenario["sessao"])
        resposta = self.client.get(endereco)
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("cadastro:entrar"), resposta["Location"])
        self.assertIn("next=", resposta["Location"])
        self.client.force_login(cenario["orientador"])
        self.assertEqual(self.client.get(endereco).status_code, 200)

    def test_cenario_3_8_presidente_de_tcc_1_depois_do_tcc_2(self):
        cenario = sessao_liberada(etapa=DescricaoTurma.TCC_1)
        sessao, tcc1 = cenario["sessao"], cenario["tcc"]
        Defesas.objects.filter(pk=sessao.pk).update(def_ocorrencias=TEXTO)
        presenca(sessao, ouvinte("2022010001", "Ana Souza"))
        turma2 = criar_turma_de(cenario["professor"], DescricaoTurma.TCC_2, EC)
        services_turmas._copiar_tcc_aprovado(cenario["professor"], turma2, tcc1.tcc_alu, tcc1)
        pagina = self.janela(cenario["orientador"], sessao)
        self.assertContains(pagina, TEXTO)
        self.assertContains(pagina, "Ana Souza")

    def test_turma_arquivada_nao_edita(self):
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        sessao = cenario["sessao"]
        Turmas.objects.filter(pk=cenario["tcc"].tcc_tur_id).update(tur_status=StatusTurma.ARQUIVADA)
        resposta = self.salvar(cenario["orientador"], sessao, TEXTO)
        self.assertContains(resposta, M02, status_code=403)
        self.assertIsNone(self.gravado(sessao))

    def test_corrida_da_turma_arquivada_vira_403(self):
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        sessao = cenario["sessao"]
        with mock.patch(
            "sigtcc.apps.defesa.services_defesa.travar_tcc",
            side_effect=TurmaArquivada(cenario["tcc"].tcc_tur),
        ):
            resposta = self.salvar(cenario["orientador"], sessao, TEXTO)
        self.assertContains(resposta, M02, status_code=403)
        self.assertIsNone(self.gravado(sessao))

    def test_edge_case_ocorrencias_e_reagendamento(self):
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        sessao, orientador = cenario["sessao"], cenario["orientador"]
        self.salvar(orientador, sessao, TEXTO)
        services_defesa.reagendar(
            orientador,
            sessao.pk,
            {
                "data": date(2026, 11, 27),
                "h_inicio": time(10, 0),
                "formato": FormatoSessao.PRESENCIAL,
                "local": "Laboratório LSI",
            },
            "Queda de energia",
        )
        sessao.refresh_from_db()
        self.assertEqual(sessao.def_status, StatusSessao.REAGENDADA)
        self.assertEqual(self.gravado(sessao), TEXTO)
        pagina = self.janela(orientador, sessao)
        self.assertContains(pagina, TEXTO)
        self.assertNotContains(pagina, self.url(sessao))
        avancar_para(sessao, StatusSessao.EM_ANDAMENTO)
        pagina = self.janela(orientador, sessao)
        self.assertContains(pagina, TEXTO)
        self.assertContains(pagina, self.url(sessao))
        resposta = self.salvar(orientador, sessao, "Texto revisto", follow=True)
        self.assertContains(resposta, SALVAS)
        self.assertEqual(self.gravado(sessao), "Texto revisto")
