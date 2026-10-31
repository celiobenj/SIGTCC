"""US-21 Agendar a defesa: um teste por cenário de aceite (User Story 1 da spec 007) e as
integrações com as telas já mescladas (menu, aba Defesas da turma, tela de orientandos).

[US-21][RBN-DEF-01.1][RBN-DEF-01.3][FR-001 a FR-006] (tasks T032)
"""

from datetime import datetime, timedelta

from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro.choices import StatusConta, StatusTCC
from sigtcc.apps.cadastro.tests.apoio_turmas import SI, TesteTurmas, tcc_de
from sigtcc.apps.defesa.choices import FormatoSessao, StatusSessao
from sigtcc.apps.defesa.models import Defesas, DefesasPresenciais, DefesasRemotas
from sigtcc.apps.defesa.tests.apoio_defesa import agendar_sessao_de, docente, tcc_apto

URL = reverse("defesa:agendar")


def daqui_a(dias=10):
    """Data futura, relativa a hoje, para o formulário aceitar."""
    return (timezone.now() + timedelta(days=dias)).date()


class TesteAgendarDefesa(TesteTurmas):
    """Cenários 1 a 12 da US-21. [US-21][RBN-DEF-01.1][RBN-DEF-01.3]"""

    def setUp(self):
        super().setUp()
        self.tcc, self.professor, self.orientador = tcc_apto()
        self.av1, self.av2 = docente(), docente()

    def dados(self, **troca):
        dados = {
            "tcc": self.tcc.pk,
            "data": daqui_a().isoformat(),
            "h_inicio": "14:00",
            "formato": FormatoSessao.PRESENCIAL,
            "local": "Laboratório LSI",
            "link": "",
            "primeiro_avaliador": self.av1.pk,
            "segundo_avaliador": self.av2.pk,
            "suplente": "",
        }
        dados.update(troca)
        return dados

    def postar(self, usuario=None, url=URL, **troca):
        self.client.force_login(usuario or self.orientador)
        return self.client.post(url, self.dados(**troca))

    def test_cenario_1_presencial_pelo_orientador_de_engenharia(self):
        self.client.force_login(self.orientador)
        resposta = self.client.post(URL, self.dados(), follow=True)
        self.assertRedirects(resposta, reverse("defesa:defesas"))
        self.assertContains(resposta, "Defesa agendada com sucesso")
        sessao = Defesas.objects.get(def_tcc=self.tcc)
        self.assertEqual(sessao.def_status, StatusSessao.AGENDADA)
        self.assertEqual(
            DefesasPresenciais.objects.get(dep_def=sessao).dep_local, "Laboratório LSI"
        )

    def test_cenario_2_remota_pelo_professor_de_sistemas(self):
        tcc, professor, _orientador = tcc_apto(SI)
        self.tcc = tcc
        self.postar(
            professor,
            formato=FormatoSessao.REMOTA,
            local="",
            link="https://meet.google.com/abc-defg-hij",
            primeiro_avaliador=docente(SI).pk,
            segundo_avaliador=docente(SI).pk,
        )
        sessao = Defesas.objects.get(def_tcc=tcc)
        self.assertEqual(
            DefesasRemotas.objects.get(der_def=sessao).der_link,
            "https://meet.google.com/abc-defg-hij",
        )

    def test_cenario_3_indica_a_reserva_de_1_hora(self):
        self.client.force_login(self.orientador)
        resposta = self.client.get(URL)
        self.assertContains(resposta, "O sistema reserva 1 hora para a sessão.")
        self.assertContains(resposta, "15 minutos em TCC 1 e 20 minutos em TCC 2")

    def test_cenario_4_a_partir_da_turma_lista_so_a_turma(self):
        tcc_si, professor, _o = tcc_apto(SI)
        outra_turma, _p, _o2 = tcc_apto(SI, professor=professor)
        self.client.force_login(professor)
        resposta = self.client.get(f"{URL}?turma={tcc_si.tcc_tur_id}")
        self.assertEqual(list(resposta.context["form"].fields["tcc"].queryset), [tcc_si])
        self.assertNotContains(resposta, f'value="{outra_turma.pk}"')
        turma = self.client.get(reverse("defesa:turma_defesas", args=[tcc_si.tcc_tur_id]))
        self.assertContains(turma, f"{URL}?turma={tcc_si.tcc_tur_id}")

    def test_cenario_5_troca_de_formato_descarta_o_local(self):
        self.client.force_login(self.orientador)
        resposta = self.client.get(URL)
        self.assertContains(resposta, 'data-caixa-formato="Presencial"')
        self.assertContains(resposta, "js/alternar_formato.js")
        self.postar(formato=FormatoSessao.REMOTA, link="https://meet.example.org/x")
        sessao = Defesas.objects.get(def_tcc=self.tcc)
        self.assertFalse(DefesasPresenciais.objects.filter(dep_def=sessao).exists())

    def test_cenario_6_sem_login_vai_ao_login_e_volta(self):
        for url in (reverse("defesa:defesas"), URL):
            with self.subTest(url=url):
                resposta = self.client.get(url)
                self.assertRedirects(
                    resposta,
                    f"{reverse('cadastro:entrar')}?next={url}",
                    fetch_redirect_response=False,
                )

    def test_cenario_7_tcc_nao_apto_ou_com_sessao_nao_aparece(self):
        nao_apto, _p, orientador = tcc_apto()
        nao_apto.tcc_status = StatusTCC.EM_ANDAMENTO
        nao_apto.save(update_fields=["tcc_status"])
        agendar_sessao_de(self.tcc, self.orientador)
        self.client.force_login(self.orientador)
        resposta = self.client.get(URL, follow=True)
        self.assertRedirects(resposta, reverse("defesa:defesas"))
        self.assertContains(resposta, "Nenhum TCC disponível para agendamento")
        self.client.force_login(orientador)
        self.assertContains(
            self.client.get(URL, follow=True), "Nenhum TCC disponível para agendamento"
        )

    def test_cenario_8_presencial_sem_local(self):
        resposta = self.postar(local="")
        self.assertFormError(resposta.context["form"], "local", "Campo obrigatório")
        self.assertFalse(Defesas.objects.exists())

    def test_cenario_8_campos_obrigatorios(self):
        resposta = self.postar(tcc="", data="", h_inicio="", formato="")
        form = resposta.context["form"]
        for campo in ("tcc", "data", "h_inicio", "formato"):
            self.assertFormError(form, campo, "Campo obrigatório")

    def test_cenario_9_data_ou_horario_no_passado(self):
        ontem = (timezone.now() - timedelta(days=1)).date().isoformat()
        uma_hora_atras = (timezone.now() - timedelta(hours=1)).strftime("%H:%M")
        hoje = timezone.now().date().isoformat()
        for data, hora in ((ontem, "14:00"), (hoje, uma_hora_atras)):
            if datetime.fromisoformat(f"{data}T{hora}") > timezone.now():
                continue  # perto da meia-noite, "uma hora atrás" cai em outro dia
            with self.subTest(data=data, hora=hora):
                resposta = self.postar(data=data, h_inicio=hora)
                self.assertFormError(
                    resposta.context["form"],
                    "data",
                    "A data e o horário devem ser posteriores ao momento atual",
                )
        self.assertFalse(Defesas.objects.exists())

    def test_cenario_10_local_com_101_caracteres(self):
        resposta = self.postar(local="L" * 101)
        self.assertFormError(
            resposta.context["form"], "local", "O Local deve ter até 100 caracteres"
        )
        self.assertFalse(Defesas.objects.exists())

    def test_cenario_11_link_sem_https(self):
        for link in ("meet.google.com/abc", "http://meet.google.com/abc", "https://" + "a" * 495):
            with self.subTest(link=link[:30]):
                resposta = self.postar(formato=FormatoSessao.REMOTA, local="", link=link)
                self.assertFormError(
                    resposta.context["form"],
                    "link",
                    "O link deve começar com https:// e ter até 500 caracteres",
                )
        self.assertFalse(Defesas.objects.exists())

    def test_cenario_12_professor_de_engenharia_nao_agenda(self):
        self.client.force_login(self.professor)
        resposta = self.client.get(f"{URL}?tcc={self.tcc.pk}")
        self.assertContains(resposta, "Este TCC não pode ser agendado por você", status_code=403)
        resposta = self.postar(self.professor)
        self.assertEqual(resposta.status_code, 302)  # o TCC nem aparece na lista: E2
        self.assertFalse(Defesas.objects.exists())

    def test_orientador_de_sistemas_tambem_nao_agenda(self):
        tcc, _professor, orientador = tcc_apto(SI)
        self.client.force_login(orientador)
        resposta = self.client.get(f"{URL}?tcc={tcc.pk}")
        self.assertContains(resposta, "Este TCC não pode ser agendado por você", status_code=403)


class TesteIntegracaoComTelasMescladas(TesteTurmas):
    """Menu, aba Defesas da turma e "Agendar defesa" na tela de orientandos (IC-02 a IC-04).
    [US-21][US-40][FR-006][FR-024]
    """

    def test_item_defesas_no_menu(self):
        tcc, _professor, orientador = tcc_apto()
        self.client.force_login(orientador)
        resposta = self.client.get(reverse("defesa:defesas"))
        self.assertContains(resposta, f'href="{reverse("defesa:defesas")}"')
        aluno = tcc.tcc_alu.alu
        aluno.usu_status = StatusConta.ATIVA
        aluno.save(update_fields=["usu_status"])
        self.client.force_login(aluno)
        self.assertEqual(self.client.get(reverse("defesa:defesas")).status_code, 200)

    def test_aba_defesas_so_para_o_professor_da_turma(self):
        tcc, professor, orientador = tcc_apto(SI)
        url = reverse("defesa:turma_defesas", args=[tcc.tcc_tur_id])
        self.client.force_login(professor)
        turma = self.client.get(reverse("cadastro:turma", args=[tcc.tcc_tur_id]))
        self.assertContains(turma, f'href="{url}"')
        self.client.force_login(orientador)
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_link_na_tela_de_orientandos_so_quando_pode_agendar(self):
        tcc, _professor, orientador = tcc_apto()
        self.client.force_login(orientador)
        link = f"{URL}?tcc={tcc.pk}&amp;de=orientacoes"
        self.assertContains(self.client.get(reverse("cadastro:orientacoes")), link)
        agendar_sessao_de(tcc, orientador)
        self.assertNotContains(self.client.get(reverse("cadastro:orientacoes")), link)

    def test_orientandos_volta_para_orientacoes(self):
        tcc, _professor, orientador = tcc_apto()
        self.client.force_login(orientador)
        resposta = self.client.post(
            f"{URL}?tcc={tcc.pk}&de=orientacoes",
            {
                "tcc": tcc.pk,
                "data": daqui_a().isoformat(),
                "h_inicio": "09:00",
                "formato": FormatoSessao.PRESENCIAL,
                "local": "Ludus",
                "primeiro_avaliador": docente().pk,
                "segundo_avaliador": docente().pk,
            },
        )
        self.assertRedirects(resposta, reverse("cadastro:orientacoes"))
        self.assertEqual(tcc_de(tcc.tcc_alu, tcc.tcc_tur).tcc_status, StatusTCC.APTO_PARA_DEFESA)
