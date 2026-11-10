"""Cálculo das notas (SC-002; research A3), estado da avaliação (research A2) e descarte e volta a
rascunho (contrato §1): Decimal com uma casa e ROUND_HALF_UP, só os membros efetivos.

[US-27][US-25][RBN-DEF-04.1][RBN-DEF-06.1][RBN-DEF-06.2][RBN-DEF-06.6][RBN-DEF-06.8] (tasks T008)
"""

from decimal import Decimal

from django.core.files.storage import default_storage
from django.db import connection, transaction
from django.db.models import Sum

from sigtcc.apps.cadastro.choices import DescricaoTurma, Homologacao, StatusSubmissao
from sigtcc.apps.cadastro.tests.apoio_orientacao import salvar_artigo
from sigtcc.apps.defesa import services_avaliacoes
from sigtcc.apps.defesa.choices import Parecer, StatusSessao
from sigtcc.apps.defesa.models import Avaliacoes, BancaDefesa, Criterios, Defesas
from sigtcc.apps.defesa.tests.apoio_avaliacao import (
    TesteAvaliacao,
    criterios,
    enviar,
    existe,
    lancar,
    lancar_e_enviar,
    png,
    sessao_em_andamento,
)

D = Decimal


def notas_com(indice, nota, base="6.0"):
    """9 notas iguais a `base`, com o critério de índice `indice` (ordem da carga) trocado."""
    notas = [D(base)] * 9
    notas[indice] = D(nota)
    return notas


class TestePesos(TesteAvaliacao):
    """Os pesos vêm de Criterios e somam 10,0 (7,0 + 3,0). [US-25][RBN-DEF-04.1][FR-001]"""

    def test_pesos_somam_dez(self):
        por_parte = dict(
            Criterios.objects.values("cri_componente")
            .annotate(total=Sum("cri_peso"))
            .values_list("cri_componente", "total")
        )
        self.assertEqual(por_parte, {"Parte Escrita": D("7.0"), "Parte Oral": D("3.0")})
        self.assertEqual(sum(c.cri_peso for c in criterios()), D("10.0"))


class TesteNotaIndividual(TesteAvaliacao):
    """Nota individual = Σ(nota × peso) / 10, uma casa, ROUND_HALF_UP. [US-27][RBN-DEF-06.1]"""

    def setUp(self):
        super().setUp()
        self.cenario = sessao_em_andamento()
        self.sessao = self.cenario["sessao"]
        self.membro = self.cenario["av1"]

    def nota(self, notas):
        lancar(self.sessao, self.membro, notas)
        return services_avaliacoes.nota_individual(self.sessao, self.membro)

    def test_soma_6_05_arredonda_para_6_1(self):
        # Relevância do Tema (peso 0,5) com 7,0 e o resto com 6,0: 60,5 / 10 = 6,05.
        self.assertEqual(self.nota(notas_com(0, "7.0")), D("6.1"))

    def test_soma_6_04_arredonda_para_6_0(self):
        # Relevância do Tema com 6,8: 60,4 / 10 = 6,04.
        self.assertEqual(self.nota(notas_com(0, "6.8")), D("6.0"))

    def test_todas_10_dao_10(self):
        self.assertEqual(self.nota(D("10.0")), D("10.0"))

    def test_resultado_e_decimal_com_uma_casa(self):
        nota = self.nota(notas_com(7, "7.3"))
        self.assertIsInstance(nota, Decimal)
        self.assertEqual(nota.as_tuple().exponent, -1)

    def test_sem_os_9_criterios_nao_ha_nota(self):
        lancar(self.sessao, self.membro, D("7.0"), criterios_lancados=criterios()[:6])
        self.assertIsNone(services_avaliacoes.nota_individual(self.sessao, self.membro))


class TesteNotaFinal(TesteAvaliacao):
    """Nota final = média das 3 individuais arredondadas; Qualis A ou B eleva a 6,0.
    [US-27][RBN-DEF-06.2][RBN-DEF-06.6]
    """

    def setUp(self):
        super().setUp()
        self.cenario = sessao_em_andamento()
        self.sessao = self.cenario["sessao"]
        self.membros = [self.cenario[chave] for chave in ("orientador", "av1", "av2")]

    def enviar_todos(self, *notas):
        for membro, nota in zip(self.membros, notas):
            lancar_e_enviar(self.sessao, membro, nota)

    def artigo(self, qualis):
        salvar_artigo(
            self.cenario["tcc"],
            qualis=qualis,
            status=StatusSubmissao.PUBLICADO,
            art_homologacao=Homologacao.HOMOLOGADO,
        )

    def test_media_de_5_9_6_0_e_6_0_da_6_0(self):
        self.enviar_todos(D("5.9"), D("6.0"), D("6.0"))
        self.assertEqual(services_avaliacoes.nota_final(self.sessao), D("6.0"))

    def test_media_5_4_com_qualis_a_homologado_vira_6_0(self):
        self.enviar_todos(D("5.4"), D("5.4"), D("5.4"))
        self.assertEqual(services_avaliacoes.nota_final(self.sessao), D("5.4"))
        self.artigo("A2")
        calculo = services_avaliacoes.calculo(self.sessao)
        self.assertEqual(calculo["nota_final"], D("6.0"))
        self.assertTrue(calculo["elevada_pelo_qualis"])

    def test_media_7_0_com_qualis_b_continua_7_0(self):
        self.enviar_todos(D("7.0"), D("7.0"), D("7.0"))
        self.artigo("B3")
        calculo = services_avaliacoes.calculo(self.sessao)
        self.assertEqual(calculo["nota_final"], D("7.0"))
        self.assertFalse(calculo["elevada_pelo_qualis"])

    def test_qualis_c_ou_nao_homologado_nao_eleva(self):
        self.enviar_todos(D("5.0"), D("5.0"), D("5.0"))
        salvar_artigo(self.cenario["tcc"], qualis="C", art_homologacao=Homologacao.HOMOLOGADO)
        self.assertEqual(services_avaliacoes.nota_final(self.sessao), D("5.0"))

    def test_todas_10_dao_10(self):
        self.enviar_todos(D("10.0"), D("10.0"), D("10.0"))
        self.assertEqual(services_avaliacoes.nota_final(self.sessao), D("10.0"))

    def test_media_das_individuais_ja_arredondadas(self):
        # Individuais 6,1 (soma 6,05), 6,0 (soma 6,04) e 7,0: média 6,366… → 6,4.
        lancar_e_enviar(self.sessao, self.membros[0], notas_com(0, "7.0"))
        lancar_e_enviar(self.sessao, self.membros[1], notas_com(0, "6.8"))
        lancar_e_enviar(self.sessao, self.membros[2], D("7.0"))
        self.assertEqual(services_avaliacoes.nota_final(self.sessao), D("6.4"))

    def test_sem_os_3_envios_nao_ha_nota_final(self):
        lancar_e_enviar(self.sessao, self.membros[0], D("8.0"))
        lancar_e_enviar(self.sessao, self.membros[1], D("8.0"))
        lancar(self.sessao, self.membros[2], D("8.0"))
        self.assertIsNone(services_avaliacoes.nota_final(self.sessao))
        self.assertIsNone(services_avaliacoes.calculo(self.sessao))

    def test_suplente_nao_acionado_com_linhas_antigas_fica_fora(self):
        lancar(self.sessao, self.cenario["suplente"], D("0.0"))
        self.enviar_todos(D("8.0"), D("8.0"), D("8.0"))
        self.assertEqual(services_avaliacoes.nota_final(self.sessao), D("8.0"))
        self.assertEqual(
            [item["membro"] for item in services_avaliacoes.estados_da_banca(self.sessao)],
            self.membros,
        )

    def test_parecer_automatico_pela_nota_e_pela_etapa(self):
        self.assertEqual(
            services_avaliacoes.parecer_automatico(self.sessao, D("5.9")), Parecer.REPROVADO
        )
        self.assertEqual(
            services_avaliacoes.parecer_automatico(self.sessao, D("6.0")),
            Parecer.APROVADO_PARA_TCC_2,
        )


class TesteEstadoDaAvaliacao(TesteAvaliacao):
    """Não avaliou, Rascunho salvo e Enviada (research A2; dicionário 3.6.4).
    [US-25][US-27][RBN-DEF-06.8]
    """

    def test_os_tres_estados(self):
        cenario = sessao_em_andamento()
        sessao = cenario["sessao"]
        lancar(sessao, cenario["av1"], D("7.0"), criterios_lancados=criterios()[:2])
        lancar_e_enviar(sessao, cenario["av2"], D("7.0"))
        estados = {
            item["membro"]: item["estado"] for item in services_avaliacoes.estados_da_banca(sessao)
        }
        self.assertEqual(
            estados,
            {
                cenario["orientador"]: "Não avaliou",
                cenario["av1"]: "Rascunho salvo",
                cenario["av2"]: "Enviada",
            },
        )
        self.assertEqual(
            services_avaliacoes.estado_da_avaliacao(sessao, cenario["av1"]), "Rascunho salvo"
        )
        self.assertEqual(
            services_avaliacoes.estado_da_avaliacao(sessao, cenario["suplente"]), "Não avaliou"
        )

    def test_estados_numa_consulta(self):
        cenario = sessao_em_andamento()
        with self.assertNumQueries(1):
            services_avaliacoes.estados_da_banca(cenario["sessao"])


class TesteDescarteEVoltaARascunho(TesteAvaliacao):
    """descartar_avaliacoes e voltar_envios_a_rascunho (contrato §1; FR-034, FR-035; D2, D3).
    [US-23][US-24][US-27][RBN-DEF-02.2][RBN-DEF-02.4][RBN-DEF-03.3]
    """

    def setUp(self):
        super().setUp()
        self.cenario = sessao_em_andamento(descricao=DescricaoTurma.TCC_2)
        self.sessao = self.cenario["sessao"]
        self.copias = {}
        for chave in ("orientador", "av1", "av2"):
            membro = self.cenario[chave]
            lancar(self.sessao, membro, D("8.0"))
            caminho = default_storage.save(f"assinaturas_banca/{chave}.png", png())
            enviar(self.sessao, membro, caminho)
            self.copias[chave] = caminho
        Defesas.objects.filter(pk=self.sessao.pk).update(def_parecer=Parecer.APROVADO)
        self.sessao.refresh_from_db()

    def linha(self, chave):
        return BancaDefesa.objects.get(ban_def=self.sessao, ban_usu=self.cenario[chave])

    def test_descartar_um_membro(self):
        with self.captureOnCommitCallbacks(execute=True):
            services_avaliacoes.descartar_avaliacoes(self.sessao, self.cenario["av2"])
        self.assertFalse(
            Avaliacoes.objects.filter(ava_def=self.sessao, ava_usu=self.cenario["av2"]).exists()
        )
        self.assertEqual(Avaliacoes.objects.filter(ava_def=self.sessao).count(), 18)
        linha = self.linha("av2")
        self.assertIsNone(linha.ban_data_envio)
        self.assertIsNone(linha.ban_assinatura_path)
        self.assertFalse(existe(self.copias["av2"]))
        self.assertTrue(existe(self.copias["av1"]))
        self.sessao.refresh_from_db()
        self.assertIsNone(self.sessao.def_parecer)

    def test_descartar_todos(self):
        with self.captureOnCommitCallbacks(execute=True):
            services_avaliacoes.descartar_avaliacoes(self.sessao)
        self.assertFalse(Avaliacoes.objects.filter(ava_def=self.sessao).exists())
        for chave in ("orientador", "av1", "av2"):
            self.assertFalse(existe(self.copias[chave]))

    def test_copia_so_apagada_depois_do_commit(self):
        with self.captureOnCommitCallbacks(execute=False):
            services_avaliacoes.descartar_avaliacoes(self.sessao, self.cenario["av1"])
            self.assertTrue(existe(self.copias["av1"]))

    def test_voltar_a_rascunho_mantem_as_notas(self):
        with self.captureOnCommitCallbacks(execute=True):
            services_avaliacoes.voltar_envios_a_rascunho(self.sessao)
        self.assertEqual(Avaliacoes.objects.filter(ava_def=self.sessao).count(), 27)
        for item in services_avaliacoes.estados_da_banca(self.sessao):
            self.assertEqual(item["estado"], "Rascunho salvo")
        self.assertFalse(existe(self.copias["orientador"]))
        self.sessao.refresh_from_db()
        self.assertIsNone(self.sessao.def_parecer)

    def test_fk_composta_valida_depois_do_descarte(self):
        with transaction.atomic():
            services_avaliacoes.descartar_avaliacoes(self.sessao, self.cenario["av1"])
            BancaDefesa.objects.filter(ban_def=self.sessao, ban_usu=self.cenario["av1"]).delete()
            connection.check_constraints()
        self.assertEqual(self.sessao.def_status, StatusSessao.EM_ANDAMENTO)
