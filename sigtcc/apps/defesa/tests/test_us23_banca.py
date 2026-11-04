"""US-23 Compor a banca: um teste por cenário de aceite (User Story 2 da spec 007).

[US-23][RBN-DEF-02.1][RBN-DEF-02.2][RBN-DEF-02.3][RBN-DEF-02.4][FR-007 a FR-013] (tasks T038)
"""

import shutil
import tempfile
from datetime import timedelta
from decimal import Decimal
from urllib.parse import urlencode

from django.core.files.storage import default_storage
from django.db import connection, transaction
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro.choices import StatusConta, Titulacao
from sigtcc.apps.cadastro.models import MembrosExternos, Notificacoes
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_membro_externo
from sigtcc.apps.cadastro.tests.apoio_orientacao import vincular_coorientador
from sigtcc.apps.cadastro.tests.apoio_turmas import SI, TesteTurmas
from sigtcc.apps.defesa import services_avaliacoes, services_defesa
from sigtcc.apps.defesa.choices import FormatoSessao, PapelBanca, StatusSessao
from sigtcc.apps.defesa.models import Avaliacoes, BancaDefesa, Defesas
from sigtcc.apps.defesa.tests.apoio_avaliacao import criterios, enviar, lancar, png
from sigtcc.apps.defesa.tests.apoio_defesa import (
    agendar_sessao_de,
    avancar_para,
    docente,
    tcc_apto,
)

AGENDAR = reverse("defesa:agendar")


def daqui_a(dias=10):
    """Data futura para o formulário aceitar."""
    return (timezone.now() + timedelta(days=dias)).date()


class TesteComporBancaNoAgendamento(TesteTurmas):
    """Cenários 1 a 5 e 8 a 11 da US-23 (seção Banca examinadora do agendamento).
    [US-23][RBN-DEF-02.1][RBN-DEF-02.3][FR-007 a FR-010]
    """

    def setUp(self):
        super().setUp()
        self.tcc, self.professor, self.orientador = tcc_apto()
        self.av1, self.av2, self.suplente = docente(), docente(), docente()
        self.client.force_login(self.orientador)

    def postar(self, **troca):
        dados = {
            "tcc": self.tcc.pk,
            "data": daqui_a().isoformat(),
            "h_inicio": "14:00",
            "formato": FormatoSessao.PRESENCIAL,
            "local": "Laboratório LSI",
            "primeiro_avaliador": self.av1.pk,
            "segundo_avaliador": self.av2.pk,
            "suplente": self.suplente.pk,
        }
        dados.update(troca)
        return self.client.post(AGENDAR, dados)

    def papeis(self):
        return dict(BancaDefesa.objects.values_list("ban_usu_id", "ban_papel"))

    def test_cenario_1_composicao_padrao(self):
        self.postar()
        self.assertEqual(
            self.papeis(),
            {
                self.orientador.pk: PapelBanca.ORIENTADOR_PRESIDENTE,
                self.av1.pk: PapelBanca.PRIMEIRO_AVALIADOR,
                self.av2.pk: PapelBanca.SEGUNDO_AVALIADOR,
                self.suplente.pk: PapelBanca.SUPLENTE,
            },
        )

    def test_cenario_2_listas_sem_os_ja_escolhidos_e_sem_a_orientacao(self):
        coorientador = docente()
        vincular_coorientador(self.tcc, coorientador)
        resposta = self.client.get(AGENDAR)
        self.assertContains(resposta, 'data-banca="segundo_avaliador"')
        self.assertContains(resposta, "js/banca.js")
        excluir = ",".join(str(pk) for pk in sorted([self.orientador.pk, coorientador.pk]))
        self.assertContains(resposta, f'data-excluir="{excluir}"')
        # Pela tela de orientandos (um TCC só), as listas já saem sem a orientação.
        form = self.client.get(f"{AGENDAR}?tcc={self.tcc.pk}").context["form"]
        candidatos = set(form.fields["primeiro_avaliador"].queryset)
        self.assertNotIn(self.orientador, candidatos)
        self.assertNotIn(coorientador, candidatos)
        self.assertIn(self.av1, candidatos)

    def test_cenario_3_presidente_fixo(self):
        resposta = self.client.get(f"{AGENDAR}?tcc={self.tcc.pk}")
        self.assertContains(
            resposta,
            f'<input class="inp" id="presidente" value="{self.orientador.usu_nome}" readonly>',
            html=True,
        )
        self.assertContains(resposta, f'data-orientador="{self.orientador.usu_nome}"')

    def test_cenario_4_sem_suplente(self):
        self.postar(suplente="")
        self.assertEqual(len(self.papeis()), 3)
        self.assertNotIn(PapelBanca.SUPLENTE, self.papeis().values())

    def test_cenario_5_cadastro_rapido_do_membro_externo(self):
        resposta = self.client.get(f"{AGENDAR}?tcc={self.tcc.pk}")
        self.assertContains(resposta, "O Membro Externo não está na lista? Cadastrar")
        voltar = f"{AGENDAR}?tcc={self.tcc.pk}&data={daqui_a().isoformat()}&campo=suplente"
        cadastro = f"{reverse('cadastro:contas_membro_novo')}?{urlencode({'voltar': voltar})}"
        resposta = self.client.post(
            cadastro,
            {
                "nome": "Rita Externa Souza",
                "email": "rita.souza@ufam.edu.br",
                "titulacao": Titulacao.DOUTOR,
                "instituicao": "UFAM",
                "voltar": voltar,
            },
        )
        membro = MembrosExternos.objects.select_related("mem").get(
            mem__usu_nome="Rita Externa Souza"
        )
        self.assertEqual(membro.mem.usu_status, StatusConta.AGUARDANDO_ATIVACAO)
        self.assertRedirects(
            resposta, f"{voltar}&membro={membro.pk}", fetch_redirect_response=False
        )
        form = self.client.get(resposta.url).context["form"]
        self.assertEqual(form["suplente"].value(), membro.pk)
        self.assertEqual(form["data"].value(), daqui_a().isoformat())
        self.assertIn(membro.mem, form.fields["suplente"].queryset)

    def test_cenario_5_membro_que_nao_e_externo_e_ignorado(self):
        url = f"{AGENDAR}?tcc={self.tcc.pk}&membro={self.av1.pk}&campo=suplente"
        self.assertIsNone(self.client.get(url).context["form"]["suplente"].value())

    def test_cenario_8_sem_login(self):
        self.client.logout()
        self.assertRedirects(
            self.client.get(AGENDAR),
            f"{reverse('cadastro:entrar')}?next={AGENDAR}",
            fetch_redirect_response=False,
        )

    def test_cenario_9_sem_o_segundo_avaliador(self):
        resposta = self.postar(segundo_avaliador="")
        self.assertFormError(resposta.context["form"], "segundo_avaliador", "Campo obrigatório")
        self.assertFalse(Defesas.objects.exists())

    def test_cenario_10_mesmo_docente_em_dois_papeis(self):
        resposta = self.postar(suplente=self.av1.pk)
        self.assertFormError(
            resposta.context["form"],
            None,
            "Selecione avaliadores distintos que não façam parte da orientação do trabalho",
        )
        self.assertFalse(Defesas.objects.exists())

    def test_cenario_11_coorientador_como_avaliador(self):
        coorientador = docente()
        vincular_coorientador(self.tcc, coorientador)
        for campo in ("primeiro_avaliador", "suplente"):
            with self.subTest(campo=campo):
                # Com um TCC só, a lista já não o oferece: só chega por requisição direta (E4).
                resposta = self.postar(**{campo: coorientador.pk})
                self.assertFormError(
                    resposta.context["form"],
                    campo,
                    "Selecione avaliadores distintos que não façam parte da orientação do trabalho",
                )
        # Com mais de um TCC na lista, a recusa vem da validação da banca no servidor.
        tcc_apto(orientador=self.orientador)
        resposta = self.postar(primeiro_avaliador=coorientador.pk)
        self.assertFormError(
            resposta.context["form"],
            None,
            "Selecione avaliadores distintos que não façam parte da orientação do trabalho",
        )
        self.assertFalse(Defesas.objects.exists())

    def test_membro_externo_expirado_pode_ser_avaliador(self):
        externo = criar_membro_externo(status=StatusConta.EXPIRADA, validade=daqui_a(-30))
        self.postar(primeiro_avaliador=externo.pk)
        self.assertEqual(self.papeis()[externo.pk], PapelBanca.PRIMEIRO_AVALIADOR)


class TesteAlterarBancaEAcionarSuplente(TesteTurmas):
    """Cenários 6, 7 e 12 a 17 da US-23 (fluxos C e D). [US-23][RBN-DEF-02.2][RBN-DEF-02.4]
    [FR-011][FR-012][FR-013]
    """

    def setUp(self):
        super().setUp()
        self.tcc, self.professor, self.orientador = tcc_apto()
        self.av1, self.av2, self.suplente = docente(), docente(), docente()
        self.sessao = agendar_sessao_de(
            self.tcc,
            self.orientador,
            {
                "primeiro_avaliador": self.av1,
                "segundo_avaliador": self.av2,
                "suplente": self.suplente,
            },
            data=daqui_a(),
        )
        self.url_banca = reverse("defesa:alterar_banca", args=[self.sessao.pk])
        self.url_suplente = reverse("defesa:acionar_suplente", args=[self.sessao.pk])
        self.url_sessao = reverse("defesa:sessao", args=[self.sessao.pk])

    def alterar(self, usuario=None, **troca):
        self.client.force_login(usuario or self.orientador)
        dados = {
            "primeiro_avaliador": self.av1.pk,
            "segundo_avaliador": self.av2.pk,
            "suplente": self.suplente.pk,
            "justificativa": "Avaliador em licença médica",
        }
        dados.update(troca)
        return self.client.post(self.url_banca, dados)

    def test_cenario_6_alteracao_antes_da_defesa(self):
        novo = docente()
        self.client.force_login(self.orientador)
        self.assertContains(self.client.get(self.url_sessao), self.url_banca)
        resposta = self.alterar(segundo_avaliador=novo.pk)
        self.assertRedirects(resposta, self.url_sessao, fetch_redirect_response=False)
        self.assertContains(self.client.get(self.url_sessao), "Banca alterada com sucesso")
        banca = services_defesa.banca_por_papel(self.sessao)
        self.assertEqual(banca[PapelBanca.SEGUNDO_AVALIADOR], novo)
        for pessoa in (novo, self.tcc.tcc_alu.alu):
            aviso = Notificacoes.objects.get(not_usu=pessoa)
            self.assertEqual(aviso.not_link_tela, self.url_sessao)
        self.assertIsNone(Notificacoes.objects.get(not_usu=self.av2).not_link_tela)

    def test_cenario_7_acionamento_justificado_do_suplente(self):
        avancar_para(self.sessao, StatusSessao.EM_ANDAMENTO)
        self.client.force_login(self.orientador)
        self.assertContains(self.client.get(self.url_sessao), self.url_suplente)
        resposta = self.client.post(
            self.url_suplente,
            {"papel_substituido": PapelBanca.SEGUNDO_AVALIADOR, "justificativa": "Não compareceu"},
        )
        self.assertRedirects(resposta, self.url_sessao, fetch_redirect_response=False)
        self.assertEqual(
            services_defesa.membros_efetivos(self.sessao),
            [self.orientador, self.av1, self.suplente],
        )
        pagina = self.client.get(self.url_sessao)
        self.assertContains(pagina, "Suplente acionado com sucesso")
        self.assertContains(pagina, f"Suplente acionado: {self.suplente.usu_nome}")

    def test_cenario_12_conflito_do_novo_membro(self):
        ocupado = docente()
        outro, _p, outro_ori = tcc_apto()
        agendar_sessao_de(
            outro,
            outro_ori,
            {"primeiro_avaliador": ocupado, "segundo_avaliador": docente()},
            data=self.sessao.def_data,
        )
        resposta = self.alterar(primeiro_avaliador=ocupado.pk)
        self.assertContains(resposta, f"{ocupado.usu_nome} (1º Avaliador)")
        self.assertEqual(
            services_defesa.banca_por_papel(self.sessao)[PapelBanca.PRIMEIRO_AVALIADOR], self.av1
        )

    def test_cenario_13_sem_justificativa_ou_longa(self):
        for justificativa in ("", "x" * 501):
            with self.subTest(tamanho=len(justificativa)):
                resposta = self.alterar(segundo_avaliador=docente().pk, justificativa=justificativa)
                self.assertFormError(
                    resposta.context["form"],
                    "justificativa",
                    "Informe uma justificativa de até 500 caracteres",
                )
        self.assertEqual(
            services_defesa.banca_por_papel(self.sessao)[PapelBanca.SEGUNDO_AVALIADOR], self.av2
        )

    def test_cenario_14_ausencia_do_orientador(self):
        resposta = self.alterar(presidente=docente().pk)
        self.assertContains(resposta, "A ausência do Orientador exige o reagendamento da sessão")
        self.assertEqual(
            services_defesa.banca_por_papel(self.sessao)[PapelBanca.ORIENTADOR_PRESIDENTE],
            self.orientador,
        )

    def test_cenario_15_sem_suplente_nao_aparece_o_botao(self):
        BancaDefesa.objects.filter(ban_def=self.sessao, ban_usu=self.suplente).delete()
        avancar_para(self.sessao, StatusSessao.EM_ANDAMENTO)
        self.client.force_login(self.orientador)
        self.assertNotContains(self.client.get(self.url_sessao), self.url_suplente)
        self.assertEqual(self.client.get(self.url_suplente).status_code, 403)

    def test_cenario_16_acionamento_sem_justificativa(self):
        avancar_para(self.sessao, StatusSessao.EM_ANDAMENTO)
        self.client.force_login(self.orientador)
        resposta = self.client.post(
            self.url_suplente,
            {"papel_substituido": PapelBanca.PRIMEIRO_AVALIADOR, "justificativa": ""},
        )
        self.assertTrue(resposta.context["form"].has_error("justificativa"))
        self.assertEqual(
            BancaDefesa.objects.get(ban_def=self.sessao, ban_usu=self.suplente).ban_papel,
            PapelBanca.SUPLENTE,
        )

    def test_cenario_17_outro_perfil_nao_aciona(self):
        avancar_para(self.sessao, StatusSessao.EM_ANDAMENTO)
        self.client.force_login(self.av1)
        self.assertNotContains(self.client.get(self.url_sessao), self.url_suplente)
        resposta = self.client.post(
            self.url_suplente,
            {"papel_substituido": PapelBanca.SEGUNDO_AVALIADOR, "justificativa": "Faltou"},
        )
        self.assertContains(resposta, "Você não tem permissão para esta ação", status_code=403)

    def test_alterar_banca_pelo_curso_e_pelo_status(self):
        self.client.force_login(self.professor)
        self.assertNotContains(self.client.get(self.url_sessao), self.url_banca)
        self.assertEqual(self.alterar(self.professor).status_code, 403)
        avancar_para(self.sessao, StatusSessao.EM_ANDAMENTO)
        self.assertEqual(self.alterar().status_code, 403)

    def test_professor_de_sistemas_altera(self):
        tcc, professor, orientador = tcc_apto(SI)
        sessao = agendar_sessao_de(
            tcc,
            professor,
            {"primeiro_avaliador": docente(SI), "segundo_avaliador": docente(SI)},
            data=daqui_a(),
        )
        self.client.force_login(professor)
        url = reverse("defesa:alterar_banca", args=[sessao.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.client.force_login(orientador)
        self.assertEqual(self.client.get(url).status_code, 403)


class TesteDescarteNaBanca(TesteTurmas):
    """Spec 008 (IC-03; D16, Q-135; revisão I-07, I-08): troca entre titulares mantém o
    rascunho, ida a Suplente descarta e o acionamento do suplente apaga a cópia da assinatura do
    ausente, preservando ban_usu_substituido. [US-23][RBN-DEF-02.2][RBN-DEF-02.4][FR-011]
    """

    def setUp(self):
        super().setUp()
        midia = tempfile.mkdtemp(prefix="sigtcc_media_")
        self.addCleanup(shutil.rmtree, midia, ignore_errors=True)
        configuracao = override_settings(MEDIA_ROOT=midia)
        configuracao.enable()
        self.addCleanup(configuracao.disable)
        self.tcc, self.professor, self.orientador = tcc_apto()
        self.av1, self.av2, self.suplente = docente(), docente(), docente()
        self.sessao = agendar_sessao_de(
            self.tcc,
            self.orientador,
            {
                "primeiro_avaliador": self.av1,
                "segundo_avaliador": self.av2,
                "suplente": self.suplente,
            },
        )
        for membro in (self.av1, self.av2):
            lancar(self.sessao, membro, Decimal("7.0"), criterios_lancados=criterios()[:6])

    def banca(self, **trocas):
        banca = {
            PapelBanca.PRIMEIRO_AVALIADOR: self.av1,
            PapelBanca.SEGUNDO_AVALIADOR: self.av2,
            PapelBanca.SUPLENTE: self.suplente,
        }
        banca.update(trocas)
        return banca

    def notas_de(self, membro):
        return Avaliacoes.objects.filter(ava_def=self.sessao, ava_usu=membro).count()

    def test_troca_entre_titulares_mantem_o_rascunho(self):
        with transaction.atomic():
            services_defesa.alterar_banca(
                self.orientador,
                self.sessao.pk,
                self.banca(
                    **{
                        PapelBanca.PRIMEIRO_AVALIADOR: self.av2,
                        PapelBanca.SEGUNDO_AVALIADOR: self.av1,
                    }
                ),
                "Troca de papéis",
            )
            connection.check_constraints()
        banca = services_defesa.banca_por_papel(self.sessao)
        self.assertEqual(banca[PapelBanca.PRIMEIRO_AVALIADOR], self.av2)
        self.assertEqual((self.notas_de(self.av1), self.notas_de(self.av2)), (6, 6))

    def test_ida_a_suplente_descarta(self):
        services_defesa.alterar_banca(
            self.orientador,
            self.sessao.pk,
            self.banca(
                **{PapelBanca.SEGUNDO_AVALIADOR: self.suplente, PapelBanca.SUPLENTE: self.av2}
            ),
            "Avaliador passa a suplente",
        )
        self.assertEqual(
            services_defesa.banca_por_papel(self.sessao)[PapelBanca.SUPLENTE], self.av2
        )
        self.assertEqual(self.notas_de(self.av2), 0)
        self.assertEqual(self.notas_de(self.av1), 6)

    def test_quem_sai_da_banca_tem_as_notas_descartadas(self):
        services_defesa.alterar_banca(
            self.orientador,
            self.sessao.pk,
            self.banca(**{PapelBanca.PRIMEIRO_AVALIADOR: docente()}),
            "Avaliador em licença",
        )
        self.assertEqual(self.notas_de(self.av1), 0)
        self.assertFalse(BancaDefesa.objects.filter(ban_def=self.sessao, ban_usu=self.av1).exists())

    def test_acionamento_apaga_a_copia_do_ausente(self):
        avancar_para(self.sessao, StatusSessao.EM_ANDAMENTO)
        lancar(self.sessao, self.av2, Decimal("7.0"))
        caminho = default_storage.save("assinaturas_banca/ausente.png", png())
        enviar(self.sessao, self.av2, caminho)
        with self.captureOnCommitCallbacks(execute=True):
            services_defesa.acionar_suplente(
                self.orientador, self.sessao.pk, PapelBanca.SEGUNDO_AVALIADOR, "Não compareceu"
            )
        self.assertFalse(default_storage.exists(caminho))
        self.assertEqual(self.notas_de(self.av2), 0)
        linha = BancaDefesa.objects.get(ban_def=self.sessao, ban_usu=self.suplente)
        self.assertEqual(linha.ban_usu_substituido, self.av2)
        self.assertEqual(
            services_avaliacoes.estado_da_avaliacao(self.sessao, self.suplente), "Não avaliou"
        )
