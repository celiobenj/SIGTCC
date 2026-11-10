"""Testes do contrato de serviços da spec 002 (specs/002-gestao-contas/contracts/
servicos-compartilhados.md): listas de escolha, trava e conferência de conta ativa e atalho da banca
(T006). O recálculo da validade e a expiração entram na T042.

[US-04][US-05][FR-028][FR-034][research C3][C19][C23][B1][m1]
"""

from django.db import transaction
from django.test import RequestFactory

from sigtcc.apps.cadastro import services_contas
from sigtcc.apps.cadastro.choices import StatusConta
from sigtcc.apps.cadastro.tests.apoio_contas import TesteContas, docente_de, membro


class ListasDeEscolhaTest(TesteContas):
    """docentes_ativos e membros_externos_disponiveis (contrato §1). [FR-028]"""

    def test_docentes_ativos_so_com_conta_ativa(self):
        ativo = docente_de()
        inativo = docente_de(status=StatusConta.INATIVA)
        aguardando = docente_de(status=StatusConta.AGUARDANDO_ATIVACAO)
        ids = set(services_contas.docentes_ativos().values_list("pk", flat=True))
        self.assertIn(ativo.pk, ids)
        self.assertNotIn(inativo.pk, ids)
        self.assertNotIn(aguardando.pk, ids)

    def test_membros_disponiveis_inclui_todos_os_status_do_membro(self):
        contas = [
            membro(status=StatusConta.AGUARDANDO_ATIVACAO),
            membro(status=StatusConta.ATIVA),
            membro(status=StatusConta.EXPIRADA),
        ]
        ids = set(services_contas.membros_externos_disponiveis().values_list("pk", flat=True))
        self.assertTrue({c.pk for c in contas} <= ids)


class TravarEConferirAtivoTest(TesteContas):
    """travar_e_conferir_ativo, para quem cria vínculos (contrato §1; research B1)."""

    def test_docente_ativo_e_inativo(self):
        with transaction.atomic():
            self.assertTrue(services_contas.travar_e_conferir_ativo(docente_de()))
            self.assertFalse(
                services_contas.travar_e_conferir_ativo(docente_de(status=StatusConta.INATIVA))
            )

    def test_membro_expirado_pode_receber_banca(self):
        with transaction.atomic():
            conta = membro(status=StatusConta.EXPIRADA)
            self.assertTrue(services_contas.travar_e_conferir_ativo(conta))

    def test_travar_contas_devolve_relidas_por_id(self):
        a, b = docente_de(), docente_de()
        with transaction.atomic():
            contas = services_contas.travar_contas(b.pk, a.pk)
        self.assertEqual(set(contas), {a.pk, b.pk})


class AtalhoDaBancaTest(TesteContas):
    """destino_interno e com_parametro (research C23; m1). [FR-034]"""

    def setUp(self):
        super().setUp()
        self.request = RequestFactory().get("/")

    def test_aceita_caminho_interno_que_resolve(self):
        self.assertEqual(services_contas.destino_interno("/painel/", self.request), "/painel/")

    def test_recusa_externo_protocolo_relativo_e_inexistente(self):
        for valor in (
            "https://evil.example/",
            "//evil.example/painel/",
            "/nao-existe/",
            "painel/",
            "",
            None,
        ):
            self.assertIsNone(services_contas.destino_interno(valor, self.request), valor)

    def test_com_parametro_preserva_a_query(self):
        self.assertEqual(
            services_contas.com_parametro("/painel/?aba=banca&membro=3", "membro", 9),
            "/painel/?aba=banca&membro=9",
        )
        self.assertEqual(
            services_contas.com_parametro("/painel/", "membro", 9), "/painel/?membro=9"
        )


class RecalculoNoContratoTest(TesteContas):
    """recalcular_validade como a Defesa chama (contrato §2): dentro da transação dela,
    idempotente, sem efeito para outro tipo de conta. [US-06][FR-039][FR-041][research C14][I1]
    """

    def test_dentro_da_transacao_de_quem_chama_e_idempotente(self):
        from datetime import date

        from sigtcc.apps.cadastro.models import MembrosExternos
        from sigtcc.apps.cadastro.tests.apoio_contas import banca
        from sigtcc.apps.cadastro.tests.fabricas import criar_defesa

        conta = membro()
        with transaction.atomic():
            banca(criar_defesa(def_data=date(2026, 12, 1)), conta)
            self.assertTrue(services_contas.recalcular_validade(conta, hoje=date(2026, 11, 1)))
            self.assertTrue(services_contas.recalcular_validade(conta, hoje=date(2026, 11, 1)))
        self.assertEqual(
            MembrosExternos.objects.get(pk=conta.pk).mem_validade_ate, date(2026, 12, 8)
        )

    def test_outro_tipo_de_conta_devolve_true(self):
        self.assertTrue(services_contas.recalcular_validade(docente_de()))


class DesempenhoDoFiltroTest(TesteContas):
    """SC-009: o filtro de Curso atualiza a lista em menos de 2 segundos (RNF de Comportamento
    Temporal do RAN-CAD-14), medido com margem e sem contar consultas exatas (research C10).
    [US-03][RBN-CAD-14.1][FR-018][SC-009]
    """

    def test_lista_com_60_docentes_por_curso(self):
        import time

        from django.urls import reverse

        from sigtcc.apps.cadastro.tests.apoio_contas import EC, LC, SI, secretaria_de

        for nome in (EC, SI, LC):
            for _ in range(60):
                docente_de(nome)
        self.client.force_login(secretaria_de(SI))
        inicio = time.perf_counter()
        resposta = self.client.get(reverse("cadastro:contas_docentes"), {"curso": "todos"})
        decorrido = time.perf_counter() - inicio
        self.assertEqual(resposta.status_code, 200)
        self.assertLess(decorrido, 2.0)
