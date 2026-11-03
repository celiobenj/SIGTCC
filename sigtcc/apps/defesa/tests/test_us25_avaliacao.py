"""US-25, formulário Avaliação (User Story 3 da spec 008): cenários 3.1 a 3.5, 3.9, 3.10 e 3.14 a
3.19, mais os casos da revisão (I-01, I-02, I-04) e a reabertura.

[US-25][RBN-DEF-05.1][RBN-DEF-05.2][RBN-DEF-05.3][RBN-DEF-06.1][FR-007 a FR-022] (tasks T022)
"""

from datetime import timedelta
from decimal import Decimal

from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro.choices import DescricaoTurma
from sigtcc.apps.defesa import services_avaliacoes, services_defesa
from sigtcc.apps.defesa.choices import Conceito, PapelBanca, Parecer, StatusSessao
from sigtcc.apps.defesa.models import Avaliacoes, BancaDefesa, Defesas
from sigtcc.apps.defesa.tests.apoio_avaliacao import (
    TesteAvaliacao,
    criterios,
    formulario,
    lancar,
    lancar_e_enviar,
    png,
    sessao_com_banca,
)
from sigtcc.apps.defesa.tests.apoio_defesa import agendar_sessao_de, avancar_para, docente

ACESSO_RESTRITO = "Acesso restrito aos membros avaliadores da banca"
FAIXA = (
    "A nota deve situar-se entre o valor mínimo e o máximo para o conceito selecionado "
    "(ex.: de 6,0 a 7,9 para Competente)"
)
D = Decimal


class TesteFormularioAvaliacao(TesteAvaliacao):
    """Cenários 3.1 a 3.5, 3.9, 3.10 e 3.14 a 3.19 do formulário Avaliação.
    [US-25][RBN-DEF-05.1][RBN-DEF-05.2][RBN-DEF-05.3]
    """

    def setUp(self):
        super().setUp()
        self.cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        self.sessao = self.cenario["sessao"]
        self.membro = self.cenario["av1"]
        self.url = reverse("defesa:avaliacao", args=[self.sessao.pk])

    def postar(self, dados, usuario=None):
        self.client.force_login(usuario or self.membro)
        return self.client.post(self.url, dados)

    def notas(self, membro=None):
        return dict(
            Avaliacoes.objects.filter(
                ava_def=self.sessao, ava_usu=membro or self.membro
            ).values_list("ava_cri__cri_nome", "ava_nota")
        )

    def linha(self, membro=None):
        return BancaDefesa.objects.get(ban_def=self.sessao, ban_usu=membro or self.membro)

    def test_cenario_3_1_envio_calcula_a_nota_e_grava_a_data(self):
        resposta = self.postar(formulario(D("8.0"), acao="enviar", arquivo=png()))
        self.assertRedirects(resposta, self.url, fetch_redirect_response=False)
        linha = self.linha()
        self.assertIsNotNone(linha.ban_data_envio)
        self.assertTrue(linha.ban_assinatura_path.startswith("assinaturas_banca/"))
        self.assertEqual(
            services_avaliacoes.estado_da_avaliacao(self.sessao, self.membro), "Enviada"
        )
        pagina = self.client.get(self.url)
        self.assertContains(pagina, "Avaliação enviada com sucesso")
        self.assertContains(pagina, "Nota individual")
        self.assertEqual(services_avaliacoes.nota_individual(self.sessao, self.membro), D("8.0"))

    def test_cenario_3_2_competente_com_7_5_aceito(self):
        self.postar(formulario(D("7.5")))
        self.assertEqual(set(self.notas().values()), {D("7.5")})

    def test_cenario_3_3_sem_observacoes_envia(self):
        self.postar(formulario(D("9.0"), acao="enviar", arquivo=png()))
        self.assertIsNotNone(self.linha().ban_data_envio)
        self.assertFalse(
            Avaliacoes.objects.filter(ava_def=self.sessao, ava_observacoes__isnull=False).exists()
        )

    def test_cenario_3_4_e_3_18_sessao_agendada_so_parte_escrita(self):
        cenario = sessao_com_banca(StatusSessao.AGENDADA)
        url = reverse("defesa:avaliacao", args=[cenario["sessao"].pk])
        self.client.force_login(cenario["av1"])
        pagina = self.client.get(url)
        self.assertContains(
            pagina, "A sessão ainda não começou: só a Parte Escrita pode ser avaliada e salva."
        )
        self.assertNotContains(pagina, "Enviar avaliação assinada")
        self.assertNotContains(pagina, "Assinatura do Membro da Banca")
        bloqueados = [form.bloqueado for form in pagina.context["formset"].forms]
        self.assertEqual(bloqueados, [False] * 6 + [True] * 3)
        # Por POST direto, a Parte Oral é ignorada e o envio é recusado.
        self.client.post(url, formulario(D("8.0")))
        self.assertEqual(
            Avaliacoes.objects.filter(ava_def=cenario["sessao"], ava_usu=cenario["av1"]).count(), 6
        )
        self.assertEqual(
            services_avaliacoes.estado_da_avaliacao(cenario["sessao"], cenario["av1"]),
            "Rascunho salvo",
        )
        resposta = self.client.post(url, formulario(D("8.0"), acao="enviar", arquivo=png()))
        self.assertContains(
            resposta, "A sessão ainda não começou: só a Parte Escrita pode ser avaliada e salva."
        )
        self.assertIsNone(
            BancaDefesa.objects.get(
                ban_def=cenario["sessao"], ban_usu=cenario["av1"]
            ).ban_data_envio
        )

    def test_salvar_reagendada_nao_apaga_notas_orais(self):
        lancar(self.sessao, self.membro, D("7.0"))
        services_defesa.transicionar_status(self.sessao, StatusSessao.REAGENDADA, None, "Teste")
        notas = [D("8.0")] * 6 + [None] * 3
        self.postar(formulario(notas))
        gravadas = self.notas()
        self.assertEqual(len(gravadas), 9)
        self.assertEqual(gravadas["Organização"], D("7.0"))
        self.assertEqual(gravadas["Metodologia"], D("8.0"))

    def test_cenario_3_5_reabrir_e_reenviar_recalcula_e_limpa_o_parecer(self):
        self.postar(formulario(D("7.0"), acao="enviar", arquivo=png()))
        Defesas.objects.filter(pk=self.sessao.pk).update(def_parecer=Parecer.APROVADO)
        resposta = self.client.post(reverse("defesa:reabrir_avaliacao", args=[self.sessao.pk]))
        self.assertRedirects(
            resposta,
            reverse("defesa:sessao", args=[self.sessao.pk]),
            fetch_redirect_response=False,
        )
        linha = self.linha()
        self.assertIsNone(linha.ban_data_envio)
        self.assertIsNone(linha.ban_assinatura_path)
        self.assertEqual(len(self.notas()), 9)
        self.sessao.refresh_from_db()
        self.assertIsNone(self.sessao.def_parecer)
        self.assertEqual(
            services_avaliacoes.estado_da_avaliacao(self.sessao, self.membro), "Rascunho salvo"
        )
        self.postar(formulario(D("9.0"), acao="enviar", arquivo=png()))
        self.assertEqual(services_avaliacoes.nota_individual(self.sessao, self.membro), D("9.0"))

    def test_avaliacao_enviada_recusa_salvar_e_enviar_com_ma13(self):
        self.postar(formulario(D("7.0"), acao="enviar", arquivo=png()))
        copia = self.linha().ban_assinatura_path
        for acao in ("salvar", "enviar"):
            with self.subTest(acao=acao):
                resposta = self.postar(formulario(D("9.0"), acao=acao, arquivo=png()))
                self.assertContains(
                    resposta,
                    "Sua avaliação já foi enviada. Para alterá-la, use Reabrir minha avaliação",
                )
        self.assertEqual(set(self.notas().values()), {D("7.0")})
        self.assertEqual(self.linha().ban_assinatura_path, copia)

    def test_cenario_3_9_competente_com_8_5_recusado(self):
        resposta = self.postar(formulario(D("8.5"), conceitos={0: Conceito.COMPETENTE}))
        self.assertContains(resposta, FAIXA)
        self.assertContains(resposta, "com-erro")
        self.assertEqual(self.notas(), {})

    def test_cenario_3_10_criterio_sem_nota_bloqueia_o_envio(self):
        notas = [D("8.0")] * 8 + [None]
        resposta = self.postar(formulario(notas, acao="enviar", arquivo=png()))
        self.assertContains(resposta, "Todos os 9 critérios devem conter conceito e nota")
        self.assertIsNone(self.linha().ban_data_envio)

    def test_ma01_criterio_incompleto_no_salvar(self):
        casos = {
            "só conceito": formulario(conceitos={0: Conceito.EXEMPLAR}),
            "só nota": formulario([D("8.0")] + [None] * 8, conceitos={0: ""}),
            "só observações": formulario(observacoes={0: "Bom trabalho"}),
        }
        for nome, dados in casos.items():
            with self.subTest(caso=nome):
                resposta = self.postar(dados)
                self.assertContains(
                    resposta, "Informe o conceito e a nota do critério, ou deixe os dois em branco"
                )
        self.assertEqual(self.notas(), {})

    def test_ma02_observacoes_com_501_caracteres(self):
        for acao in ("salvar", "enviar"):
            with self.subTest(acao=acao):
                resposta = self.postar(
                    formulario(D("8.0"), acao=acao, observacoes={2: "x" * 501}, arquivo=png())
                )
                self.assertContains(resposta, "As observações devem ter até 500 caracteres")
        self.assertEqual(self.notas(), {})
        self.postar(formulario(D("8.0"), observacoes={2: "x" * 500}))
        self.assertEqual(len(self.notas()), 9)

    def test_rascunho_salvo_com_ma09(self):
        resposta = self.postar(formulario([D("6.5")] * 3 + [None] * 6))
        self.assertRedirects(resposta, self.url, fetch_redirect_response=False)
        self.assertContains(self.client.get(self.url), "Rascunho salvo")
        self.assertEqual(len(self.notas()), 3)
        # Esvaziar um critério liberado apaga a linha.
        self.postar(formulario([D("6.5")] * 2 + [None] * 7))
        self.assertEqual(len(self.notas()), 2)

    def test_cenario_3_14_fora_da_banca_e_suplente_nao_acionado(self):
        for usuario in (docente(), self.cenario["suplente"], self.cenario["professor"]):
            with self.subTest(usuario=usuario.usu_email):
                self.client.force_login(usuario)
                for resposta in (
                    self.client.get(self.url),
                    self.client.post(self.url, formulario()),
                ):
                    self.assertEqual(resposta.status_code, 403)
                    self.assertContains(resposta, ACESSO_RESTRITO, status_code=403)

    def test_cenario_3_15_realizada_so_leitura(self):
        lancar_e_enviar(self.sessao, self.membro, D("8.0"))
        services_defesa.transicionar_status(self.sessao, StatusSessao.REALIZADA, None)
        Defesas.objects.filter(pk=self.sessao.pk).update(
            def_data_liberacao_resultado=timezone.now()
        )
        self.client.force_login(self.membro)
        pagina = self.client.get(self.url)
        self.assertEqual(pagina.status_code, 200)
        self.assertNotContains(pagina, 'value="salvar"')
        self.assertNotContains(pagina, "Enviar avaliação assinada")
        resposta = self.client.post(self.url, formulario(D("9.0")))
        self.assertContains(
            resposta,
            "O resultado desta defesa já foi liberado e as avaliações não podem mais ser alteradas",
        )
        self.assertEqual(set(self.notas().values()), {D("8.0")})

    def test_cenario_3_17_sem_login(self):
        resposta = self.client.get(self.url)
        self.assertRedirects(
            resposta, f"{reverse('cadastro:entrar')}?next={self.url}", fetch_redirect_response=False
        )

    def test_cenario_3_19_sessao_cancelada(self):
        services_defesa.transicionar_status(self.sessao, StatusSessao.CANCELADA, None, "Teste")
        self.client.force_login(self.membro)
        self.assertContains(self.client.get(self.url), ACESSO_RESTRITO, status_code=403)

    def test_suplente_acionado_avalia_as_duas_partes(self):
        services_defesa.acionar_suplente(
            self.cenario["orientador"], self.sessao.pk, PapelBanca.SEGUNDO_AVALIADOR, "Faltou"
        )
        suplente = self.cenario["suplente"]
        self.postar(formulario(D("8.0"), acao="enviar", arquivo=png()), usuario=suplente)
        self.assertEqual(services_avaliacoes.estado_da_avaliacao(self.sessao, suplente), "Enviada")

    def test_inicio_automatico_ao_abrir_no_horario(self):
        tcc = self.cenario["tcc"]
        services_defesa.transicionar_status(self.sessao, StatusSessao.CANCELADA, None, "Teste")
        inicio = timezone.now() - timedelta(minutes=5)
        sessao = agendar_sessao_de(
            tcc,
            self.cenario["orientador"],
            {"primeiro_avaliador": self.membro, "segundo_avaliador": docente()},
            data=inicio.date(),
            h_inicio=inicio.time().replace(second=0, microsecond=0),
        )
        self.client.force_login(self.membro)
        pagina = self.client.get(reverse("defesa:avaliacao", args=[sessao.pk]))
        sessao.refresh_from_db()
        self.assertEqual(sessao.def_status, StatusSessao.EM_ANDAMENTO)
        self.assertContains(pagina, "Enviar avaliação assinada")

    def test_reabrir_fora_de_andamento_recusado(self):
        cenario = sessao_com_banca(StatusSessao.AGENDADA)
        self.client.force_login(cenario["av1"])
        url = reverse("defesa:reabrir_avaliacao", args=[cenario["sessao"].pk])
        resposta = self.client.post(url, follow=True)
        self.assertContains(
            resposta,
            "O resultado desta defesa já foi liberado e as avaliações não podem mais ser alteradas",
        )


class TesteServicoDoFormulario(TesteAvaliacao):
    """Recusas do serviço contra requisição direta (defesa em profundidade).
    [US-25][RBN-DEF-05.1][RBN-DEF-05.2]
    """

    def test_parte_oral_nao_e_gravada_antes_da_sessao(self):
        cenario = sessao_com_banca(StatusSessao.AGENDADA, descricao=DescricaoTurma.TCC_2)
        linhas = {
            c.pk: {"conceito": Conceito.EXEMPLAR, "nota": D("9.0"), "observacoes": ""}
            for c in criterios()
        }
        services_avaliacoes.salvar_rascunho(cenario["av1"], cenario["sessao"].pk, linhas)
        self.assertEqual(
            Avaliacoes.objects.filter(ava_def=cenario["sessao"], ava_usu=cenario["av1"]).count(), 6
        )

    def test_nota_fora_da_faixa_recusada_pelo_servico(self):
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        criterio = criterios()[0]
        linhas = {criterio.pk: {"conceito": Conceito.COMPETENTE, "nota": D("8.5")}}
        with self.assertRaises(services_avaliacoes.ErroAvaliacao) as erro:
            services_avaliacoes.salvar_rascunho(cenario["av1"], cenario["sessao"].pk, linhas)
        self.assertEqual(erro.exception.mensagem, FAIXA)

    def test_sessao_realizada_sem_suplente_nao_altera(self):
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO, suplente=False)
        avancar_para(cenario["sessao"], StatusSessao.CANCELADA)
        with self.assertRaises(services_avaliacoes.AcessoRestrito):
            services_avaliacoes.salvar_rascunho(cenario["av1"], cenario["sessao"].pk, {})
