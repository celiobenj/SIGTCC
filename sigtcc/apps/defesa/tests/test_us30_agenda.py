"""US-30, agenda de defesas em PDF (User Story 6 da spec 009): cenários 6.1 a 6.7, o filtro
inválido, a sessão vencida já iniciada, a falha de geração e o botão na tela Defesas.

[US-30][RBN-DEF-08.1][RBN-DEF-01.5][RBN-CAD-14.1] (spec 009, tasks T037)
"""

import os
from datetime import date, time, timedelta
from unittest import mock

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro.tests.apoio_acesso import criar_membro_externo, criar_secretaria
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, SI, curso
from sigtcc.apps.defesa import pdf
from sigtcc.apps.defesa.choices import FormatoSessao, StatusSessao
from sigtcc.apps.defesa.models import Defesas
from sigtcc.apps.defesa.tests.apoio_avaliacao import TesteAvaliacao, sessao_com_banca
from sigtcc.apps.defesa.tests.apoio_defesa import agendar_sessao_de, docente, tcc_apto
from sigtcc.apps.defesa.tests.apoio_documentos import texto_do_pdf

NOVEMBRO = {"data_inicial": "01/11/2026", "data_final": "30/11/2026"}
SEM_DEFESAS = "Não existem defesas agendadas para o período selecionado"
E3 = "Erro ao gerar os documentos da defesa. Tente realizar o download novamente em instantes"
BOTAO = "Agenda de defesas (PDF)"


def junto(texto):
    """Texto do PDF com as quebras de linha trocadas por um espaço. [US-30][RBN-DEF-08.1]"""
    return " ".join(texto.split())


def mover(sessao, data, h_inicio=None):
    """Muda a data (e o horário) da sessão direto, só para montar o cenário. [US-30]"""
    campos = {"def_data": data}
    if h_inicio is not None:
        campos["def_h_inicio"] = h_inicio
    Defesas.objects.filter(pk=sessao.pk).update(**campos)


class BaseAgenda(TesteAvaliacao):
    """Downloads da agenda. [US-30][RBN-DEF-08.1]"""

    def baixar(self, usuario, follow=False, **filtros):
        """GET da agenda com os filtros (novembro de 2026 por padrão). [US-30][RBN-DEF-08.1]"""
        self.client.force_login(usuario)
        parametros = {**NOVEMBRO, **filtros}
        return self.client.get(reverse("defesa:agenda"), parametros, follow=follow)

    def conferir_pdf(self, resposta):
        """PDF entregue como anexo agenda_defesas.pdf. [US-30][RBN-DEF-08.1]"""
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta["Content-Type"], "application/pdf")
        self.assertEqual(
            resposta["Content-Disposition"], 'attachment; filename="agenda_defesas.pdf"'
        )
        return junto(texto_do_pdf(resposta))


class TesteConteudoDaAgenda(BaseAgenda):
    """Cenários 6.1, 6.2, 6.4 e 6.5. [US-30][RBN-DEF-08.1][RBN-CAD-14.1]"""

    def test_cenario_6_1_agrupada_por_dia(self):
        primeira = sessao_com_banca(StatusSessao.AGENDADA)
        mover(primeira["sessao"], date(2026, 11, 25), time(9, 30))
        segunda = sessao_com_banca(StatusSessao.REAGENDADA)
        tcc, _, orientador = tcc_apto()
        banca = {"primeiro_avaliador": docente(), "segundo_avaliador": docente()}
        remota = agendar_sessao_de(
            tcc,
            orientador,
            banca,
            data=date(2026, 11, 20),
            h_inicio=time(8, 0),
            formato=FormatoSessao.REMOTA,
            local=None,
            link="https://meet.example.org/defesa",
        )
        texto = self.conferir_pdf(self.baixar(primeira["orientador"]))
        self.assertIn("Agenda de defesas", texto)
        # Dias em ordem cronológica; no mesmo dia, por horário.
        self.assertLess(texto.index("20/11/2026"), texto.index("25/11/2026"))
        self.assertLess(texto.index("08:00"), texto.index("14:00"))
        self.assertLess(texto.index("14:00"), texto.index("09:30"))
        self.assertEqual(texto.count("20/11/2026"), 1)
        for cenario in (primeira, segunda):
            self.assertIn(cenario["aluno"].usu_nome, texto)
            self.assertIn(cenario["orientador"].usu_nome, texto)
        self.assertIn(tcc.tcc_alu.alu.usu_nome, texto)
        self.assertIn(remota.def_tcc.tcc_titulo, texto)
        self.assertIn("Laboratório LSI", texto)
        self.assertIn("https://meet.example.org/defesa", texto)

    def test_cenario_6_2_coordenador_com_filtro_de_curso(self):
        engenharia = sessao_com_banca(StatusSessao.AGENDADA, curso_nome=EC)
        sistemas = sessao_com_banca(StatusSessao.AGENDADA, curso_nome=SI)
        texto = self.conferir_pdf(self.baixar(engenharia["coordenador"], curso=str(curso(SI).pk)))
        self.assertIn(sistemas["aluno"].usu_nome, texto)
        self.assertNotIn(engenharia["aluno"].usu_nome, texto)
        texto = self.conferir_pdf(self.baixar(engenharia["coordenador"], curso="todos"))
        self.assertIn(sistemas["aluno"].usu_nome, texto)
        self.assertIn(engenharia["aluno"].usu_nome, texto)
        # A Secretaria, com o curso dela por padrão.
        secretaria = criar_secretaria(curso=curso(SI))
        texto = self.conferir_pdf(self.baixar(secretaria))
        self.assertIn(sistemas["aluno"].usu_nome, texto)
        self.assertNotIn(engenharia["aluno"].usu_nome, texto)

    def test_cenario_6_4_so_agendadas_e_reagendadas(self):
        agendada = sessao_com_banca(StatusSessao.AGENDADA)
        fora = [
            sessao_com_banca(status)
            for status in (
                StatusSessao.EM_ANDAMENTO,
                StatusSessao.REALIZADA,
                StatusSessao.CANCELADA,
            )
        ]
        texto = self.conferir_pdf(self.baixar(agendada["orientador"]))
        self.assertIn(agendada["aluno"].usu_nome, texto)
        for cenario in fora:
            self.assertNotIn(cenario["aluno"].usu_nome, texto)

    def test_cenario_6_5_orientador_recebe_todas_as_sessoes(self):
        propria = sessao_com_banca(StatusSessao.AGENDADA)
        outras = [
            sessao_com_banca(StatusSessao.AGENDADA, curso_nome=SI if indice % 2 else EC)
            for indice in range(5)
        ]
        texto = self.conferir_pdf(self.baixar(propria["orientador"]))
        for cenario in (propria, *outras):
            self.assertIn(cenario["aluno"].usu_nome, texto)
        # O filtro de Curso não vale para quem não é Coordenador nem Secretaria (P2).
        texto = self.conferir_pdf(self.baixar(propria["professor"], curso=str(curso(SI).pk)))
        for cenario in (propria, *outras):
            self.assertIn(cenario["aluno"].usu_nome, texto)


class TesteRecusasDaAgenda(BaseAgenda):
    """Cenários 6.3, 6.6 e 6.7, filtro inválido, sessão vencida e falha de geração.
    [US-30][RBN-DEF-08.1]
    """

    def test_cenario_6_3_sem_defesas(self):
        cenario = sessao_com_banca(StatusSessao.REALIZADA)
        resposta = self.baixar(cenario["orientador"])
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(resposta["Location"].startswith(reverse("defesa:defesas")))
        self.assertIn("data_inicial=01%2F11%2F2026", resposta["Location"])
        resposta = self.baixar(cenario["orientador"], follow=True)
        self.assertContains(resposta, SEM_DEFESAS)
        self.assertNotEqual(resposta["Content-Type"], "application/pdf")

    def test_cenario_6_6_login_e_depois_o_download(self):
        cenario = sessao_com_banca(StatusSessao.AGENDADA)
        endereco = f"{reverse('defesa:agenda')}?data_inicial=01/11/2026&data_final=30/11/2026"
        resposta = self.client.get(endereco)
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("cadastro:entrar"), resposta["Location"])
        self.assertIn("next=", resposta["Location"])
        self.client.force_login(cenario["orientador"])
        self.conferir_pdf(self.client.get(endereco))

    def test_cenario_6_7_aluno_e_membro_externo_recusados(self):
        cenario = sessao_com_banca(StatusSessao.AGENDADA)
        for usuario in (cenario["aluno"], criar_membro_externo()):
            with self.subTest(usuario=usuario.pk):
                resposta = self.baixar(usuario)
                self.assertContains(
                    resposta, "Você não tem permissão para esta ação", status_code=403
                )

    def test_filtro_invalido_volta_sem_pdf(self):
        cenario = sessao_com_banca(StatusSessao.AGENDADA)
        resposta = self.baixar(
            cenario["orientador"], data_inicial="30/11/2026", data_final="01/11/2026"
        )
        self.assertEqual(resposta.status_code, 302)
        self.assertIn("data_inicial=30%2F11%2F2026", resposta["Location"])
        resposta = self.client.get(resposta["Location"])
        self.assertContains(resposta, "A data inicial não pode ser superior à data final")

    def test_sessao_vencida_ja_iniciada_nao_aparece(self):
        vencida = sessao_com_banca(StatusSessao.AGENDADA)
        ontem = timezone.now().date() - timedelta(days=1)
        mover(vencida["sessao"], ontem)
        futura = sessao_com_banca(StatusSessao.AGENDADA)
        mover(futura["sessao"], ontem + timedelta(days=10))
        filtros = {
            "data_inicial": ontem.strftime("%d/%m/%Y"),
            "data_final": (ontem + timedelta(days=20)).strftime("%d/%m/%Y"),
        }
        texto = self.conferir_pdf(self.baixar(vencida["orientador"], **filtros))
        self.assertIn(futura["aluno"].usu_nome, texto)
        self.assertNotIn(vencida["aluno"].usu_nome, texto)
        self.assertEqual(
            Defesas.objects.get(pk=vencida["sessao"].pk).def_status, StatusSessao.EM_ANDAMENTO
        )

    def test_falha_de_geracao(self):
        cenario = sessao_com_banca(StatusSessao.AGENDADA)
        antes = sorted(
            os.path.join(raiz, nome)
            for raiz, _, nomes in os.walk(settings.MEDIA_ROOT)
            for nome in nomes
        )
        with mock.patch(
            "sigtcc.apps.defesa.pdf.gerar_pdf", side_effect=pdf.ErroAoGerarPdf("conversor fora")
        ):
            resposta = self.baixar(cenario["orientador"], follow=True)
        self.assertContains(resposta, E3)
        self.assertNotEqual(resposta["Content-Type"], "application/pdf")
        depois = sorted(
            os.path.join(raiz, nome)
            for raiz, _, nomes in os.walk(settings.MEDIA_ROOT)
            for nome in nomes
        )
        self.assertEqual(antes, depois)


class TesteBotaoNaTelaDefesas(BaseAgenda):
    """Botão "Agenda de defesas (PDF)" na tela Defesas (IC-06; FR-022). [US-30][RBN-DEF-08.1]"""

    def test_botao_por_perfil(self):
        cenario = sessao_com_banca(StatusSessao.AGENDADA)
        secretaria = criar_secretaria(curso=curso(EC))
        for usuario in (
            cenario["orientador"],
            cenario["professor"],
            cenario["coordenador"],
            secretaria,
            docente(),
        ):
            with self.subTest(usuario=usuario.pk):
                self.client.force_login(usuario)
                pagina = self.client.get(reverse("defesa:defesas"), NOVEMBRO)
                self.assertContains(pagina, BOTAO)
                self.assertContains(
                    pagina,
                    f'{reverse("defesa:agenda")}?data_inicial=01%2F11%2F2026'
                    "&amp;data_final=30%2F11%2F2026",
                )
        for usuario in (cenario["aluno"], criar_membro_externo()):
            with self.subTest(usuario=usuario.pk):
                self.client.force_login(usuario)
                pagina = self.client.get(reverse("defesa:defesas"), NOVEMBRO)
                self.assertEqual(pagina.status_code, 200)
                self.assertNotContains(pagina, BOTAO)
