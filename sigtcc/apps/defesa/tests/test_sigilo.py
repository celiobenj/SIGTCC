"""Sigilo das notas e resultado para o aluno (User Story 5 da spec 008; SC-003): cenários 5.1 a
5.8 por perfil e por tela, antes e depois da liberação, e a parte do cenário 4.1 que trata do
aluno (/speckit-analyze I3).

[US-27][RBN-DEF-06.5][RBN-DEF-06.8][FR-031 a FR-033] (tasks T036)
"""

from datetime import datetime
from decimal import Decimal

from django.urls import reverse

from sigtcc.apps.cadastro.choices import DescricaoTurma, TipoEntrega
from sigtcc.apps.cadastro.models import Turmas
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_secretaria
from sigtcc.apps.cadastro.tests.apoio_tcc import cadastrar_entrega
from sigtcc.apps.cadastro.tests.apoio_turmas import SI
from sigtcc.apps.defesa import services_avaliacoes
from sigtcc.apps.defesa.choices import Parecer, StatusSessao
from sigtcc.apps.defesa.models import BancaDefesa
from sigtcc.apps.defesa.tests.apoio_avaliacao import (
    TesteAvaliacao,
    lancar,
    lancar_e_enviar,
    sessao_com_banca,
)
from sigtcc.apps.defesa.tests.apoio_defesa import docente

D = Decimal
OBS = "Observação reservada do primeiro avaliador"


class BaseSigilo(TesteAvaliacao):
    """Sessão Em Andamento de TCC 1: Orientador 8,6; 1º Avaliador 7,3 (com Observações); 2º
    Avaliador 9,1 (nota final 8,3). [US-27][RBN-DEF-06.8]
    """

    descricao = DescricaoTurma.TCC_1

    def setUp(self):
        super().setUp()
        self.cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO, descricao=self.descricao)
        self.sessao = self.cenario["sessao"]
        self.tcc = self.cenario["tcc"]
        self.secretaria = criar_secretaria(curso=self.tcc.tcc_tur.tur_cur)
        self.url_sessao = reverse("defesa:sessao", args=[self.sessao.pk])
        self.url_avaliacao = reverse("defesa:avaliacao", args=[self.sessao.pk])
        self.url_meu_tcc = reverse("cadastro:meu_tcc", args=[self.tcc.tcc_tur_id])

    def enviar(self, chave, nota, **dados):
        lancar_e_enviar(self.sessao, self.cenario[chave], D(nota), **dados)

    def tres_envios(self):
        self.enviar("orientador", "8.6")
        self.enviar("av1", "7.3", observacoes=OBS)
        self.enviar("av2", "9.1")

    def liberar(self):
        services_avaliacoes.liberar_resultado(
            self.cenario["orientador"], self.sessao.pk, D("8.3"), Parecer.APROVADO_PARA_TCC_2
        )
        self.sessao.refresh_from_db()

    def pagina(self, usuario, url=None):
        self.client.force_login(usuario)
        return self.client.get(url or self.url_sessao)

    def terceiros(self):
        return {
            "Professor da Disciplina": self.cenario["professor"],
            "Secretaria": self.secretaria,
            "Aluno": self.cenario["aluno"],
            "Suplente não acionado": self.cenario["suplente"],
        }


class TesteSigiloAntesDaLiberacao(BaseSigilo):
    """Cenários 5.1 a 5.3. [US-27][RBN-DEF-06.6][RBN-DEF-06.8][FR-031]"""

    def test_cenario_5_1_avaliador_ve_so_a_propria_e_os_estados(self):
        self.enviar("orientador", "8.6")
        self.enviar("av1", "7.3", observacoes=OBS)
        lancar(self.sessao, self.cenario["av2"], D("9.1"))
        pagina = self.pagina(self.cenario["av1"])
        self.assertContains(pagina, "data-bloco-avaliacao")
        self.assertContains(pagina, "Rascunho salvo")
        self.assertContains(pagina, "Enviada")
        self.assertContains(pagina, "nota individual 7,3")
        for proibido in ("8,6", "9,1", "8,3", "Nota final"):
            self.assertNotContains(pagina, proibido)
        visao = services_avaliacoes.visao_da_avaliacao(self.cenario["av1"], self.sessao)
        self.assertEqual(visao["avaliadores"], [])
        self.assertIsNone(visao["nota_final"])

    def test_cenario_5_2_orientador_sem_os_3_envios_nao_ve_a_nota(self):
        self.enviar("orientador", "8.6")
        self.enviar("av1", "7.3")
        pagina = self.pagina(self.cenario["orientador"])
        self.assertNotContains(pagina, "Nota final")
        self.assertContains(pagina, "Pendentes:")
        self.assertNotContains(pagina, "7,3")
        self.enviar("av2", "9.1")
        pagina = self.pagina(self.cenario["orientador"])
        self.assertContains(pagina, "8,3")
        self.assertContains(pagina, "Aprovado para TCC 2")
        self.assertNotContains(pagina, "7,3")

    def test_cenario_5_3_terceiros_nao_veem_nada_do_bloco(self):
        self.tres_envios()
        for nome, usuario in self.terceiros().items():
            with self.subTest(perfil=nome):
                pagina = self.pagina(usuario)
                self.assertEqual(pagina.status_code, 200)
                for proibido in (
                    "data-bloco-avaliacao",
                    "data-bloco-resultado",
                    "Enviada",
                    "8,3",
                    "7,3",
                    "Aprovado para TCC 2",
                ):
                    self.assertNotContains(pagina, proibido)

    def test_endereco_direto_e_outras_telas(self):
        self.tres_envios()
        self.assertEqual(self.pagina(self.cenario["aluno"], self.url_avaliacao).status_code, 403)
        url_liberar = reverse("defesa:liberar_resultado", args=[self.sessao.pk])
        self.assertEqual(self.pagina(self.cenario["professor"], url_liberar).status_code, 403)
        formulario = self.pagina(self.cenario["av1"], self.url_avaliacao)
        self.assertContains(formulario, OBS)
        for proibido in ("8,6", "9,1", "8,3"):
            self.assertNotContains(formulario, proibido)
        bancas = self.pagina(self.cenario["av2"], reverse("defesa:minhas_bancas"))
        for proibido in ("7,3", "8,6", "8,3", OBS):
            self.assertNotContains(bancas, proibido)
        for usuario in (self.cenario["professor"], self.secretaria, self.cenario["aluno"]):
            defesas = self.pagina(usuario, reverse("defesa:defesas"))
            for proibido in ("7,3", "8,3", "Enviada"):
                self.assertNotContains(defesas, proibido)
        meu_tcc = self.pagina(self.cenario["aluno"], self.url_meu_tcc)
        self.assertNotContains(meu_tcc, "Resultado da defesa")
        self.assertNotContains(meu_tcc, "8,3")

    def test_professor_da_disciplina_que_e_orientador_ve_como_orientador(self):
        professor = docente(SI)
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO, curso_nome=SI)
        # Mesmo cenário com o Professor da Disciplina presidindo a banca (revisão I-05).
        Turmas.objects.filter(pk=cenario["tcc"].tcc_tur_id).update(tur_doc=professor.docentes)
        BancaDefesa.objects.filter(ban_def=cenario["sessao"], ban_usu=cenario["orientador"]).update(
            ban_usu=professor
        )
        for usuario, nota in ((professor, "6.0"), (cenario["av1"], "6.0"), (cenario["av2"], "6.0")):
            lancar_e_enviar(cenario["sessao"], usuario, D(nota))
        visao = services_avaliacoes.visao_da_avaliacao(professor, cenario["sessao"])
        self.assertTrue(visao["orientador"])
        self.assertEqual(visao["nota_final"], D("6.0"))
        self.client.force_login(professor)
        pagina = self.client.get(reverse("defesa:sessao", args=[cenario["sessao"].pk]))
        self.assertContains(pagina, "data-bloco-resultado")


class TesteSigiloDepoisDaLiberacao(BaseSigilo):
    """Cenários 5.4, 5.6 a 5.8. [US-27][RBN-DEF-06.5][RBN-DEF-06.8][FR-032][FR-033]"""

    def setUp(self):
        super().setUp()
        self.tres_envios()
        self.liberar()

    def test_cenario_5_4_todos_veem_as_notas_e_o_resultado(self):
        pessoas = {**self.terceiros(), "Orientador": self.cenario["orientador"]}
        for nome, usuario in pessoas.items():
            with self.subTest(perfil=nome):
                pagina = self.pagina(usuario)
                for visivel in ("data-bloco-resultado", "8,6", "7,3", "9,1", "8,3"):
                    self.assertContains(pagina, visivel)
                self.assertContains(pagina, "Aprovado para TCC 2")

    def test_cenario_5_7_observacoes_so_ao_autor(self):
        self.assertContains(self.pagina(self.cenario["av1"]), OBS)
        for usuario in (
            self.cenario["orientador"],
            self.cenario["av2"],
            self.cenario["professor"],
            self.secretaria,
            self.cenario["aluno"],
        ):
            with self.subTest(usuario=usuario.usu_nome):
                self.assertNotContains(self.pagina(usuario), OBS)

    def test_cenario_5_6_tcc_1_sem_data_limite(self):
        cadastrar_entrega(
            self.tcc.tcc_tur,
            tipo=TipoEntrega.VERSAO_FINAL,
            data_limite=datetime(2026, 12, 15, 23, 59),
        )
        pagina = self.pagina(self.cenario["aluno"], self.url_meu_tcc)
        self.assertContains(pagina, "Resultado da defesa")
        self.assertContains(pagina, "8,3")
        self.assertContains(pagina, "Aprovado para TCC 2")
        self.assertNotContains(pagina, "Data Limite da Versão Final")

    def test_cenario_5_8_historico_com_nota_e_parecer(self):
        pagina = self.pagina(
            self.cenario["professor"], reverse("defesa:historico", args=[self.sessao.pk])
        )
        self.assertContains(pagina, "Nota final: 8,3; parecer: Aprovado para TCC 2")


class TesteResultadoDoAlunoTcc2(BaseSigilo):
    """Cenários 5.5 e 5.6 em TCC 2 e a parte do cenário 4.1 que trata do aluno (Q-127).
    [US-27][RBN-DEF-06.5][FR-033]
    """

    descricao = DescricaoTurma.TCC_2

    def liberar_tcc2(self, parecer, nota="7.0"):
        for chave in ("orientador", "av1", "av2"):
            self.enviar(chave, nota)
        if parecer in services_avaliacoes.PARECERES_DE_TCC_2:
            services_avaliacoes.registrar_parecer(
                self.cenario["orientador"], self.sessao.pk, parecer
            )
        services_avaliacoes.liberar_resultado(
            self.cenario["orientador"], self.sessao.pk, D(nota), parecer
        )

    def versao_final(self):
        return cadastrar_entrega(
            self.tcc.tcc_tur,
            tipo=TipoEntrega.VERSAO_FINAL,
            data_limite=datetime(2026, 12, 15, 23, 59),
        )

    def test_cenario_4_1_e_5_5_aprovado_com_correcoes_mostra_a_data_limite(self):
        self.versao_final()
        self.liberar_tcc2(Parecer.APROVADO_COM_CORRECOES)
        pagina = self.pagina(self.cenario["aluno"], self.url_meu_tcc)
        self.assertContains(pagina, "Resultado da defesa")
        self.assertContains(pagina, "7,0")
        self.assertContains(pagina, "Aprovado com Correções")
        self.assertContains(pagina, "Data Limite da Versão Final</span><b>15/12/2026 23:59")

    def test_cenario_5_5_aprovado_mostra_a_data_limite(self):
        self.versao_final()
        self.liberar_tcc2(Parecer.APROVADO)
        resultado = services_avaliacoes.resultado_para_o_aluno(self.tcc)
        self.assertEqual(resultado["data_limite"], datetime(2026, 12, 15, 23, 59))

    def test_cenario_5_6_reprovado_sem_data_limite(self):
        self.versao_final()
        self.liberar_tcc2(Parecer.REPROVADO, nota="5.0")
        resultado = services_avaliacoes.resultado_para_o_aluno(self.tcc)
        self.assertEqual(resultado["parecer"], Parecer.REPROVADO)
        self.assertIsNone(resultado["data_limite"])

    def test_sem_a_entrega_versao_final_sem_data_limite(self):
        self.liberar_tcc2(Parecer.APROVADO)
        self.assertIsNone(services_avaliacoes.resultado_para_o_aluno(self.tcc)["data_limite"])

    def test_resultado_da_sessao_para_a_feat_09(self):
        self.liberar_tcc2(Parecer.APROVADO)
        self.sessao.refresh_from_db()
        resultado = services_avaliacoes.resultado_da_sessao(self.sessao)
        self.assertEqual(resultado["nota_final"], D("7.0"))
        self.assertEqual(len(resultado["avaliadores"]), 3)
        self.assertFalse(resultado["elevada_pelo_qualis"])
