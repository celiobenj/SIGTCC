"""Testes de aceite da US-50 (cenários 1 a 9) e das Clarifications Q10, Q11 e Q36 (tasks T037).

[US-50][RBN-CAD-03.3][FR-042][FR-043][FR-044][Q10][Q11][Q36]
"""

from datetime import date, datetime
from unittest import mock

from django.db import DatabaseError
from django.urls import reverse

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import StatusConta, StatusTCC, StatusTurma
from sigtcc.apps.cadastro.models import MembrosExternos, Usuarios
from sigtcc.apps.cadastro.tests.apoio_acesso import SENHA, criar_aluno_com_turma
from sigtcc.apps.cadastro.tests.apoio_contas import (
    EC,
    SI,
    TesteContas,
    banca,
    coordenador_de,
    docente_de,
    membro,
    orientacao_ativa,
    secretaria_de,
    turma_do_docente,
)
from sigtcc.apps.cadastro.tests.apoio_turmas import matricular_aluno, tcc_de
from sigtcc.apps.cadastro.tests.fabricas import criar_defesa
from sigtcc.apps.defesa.choices import StatusSessao

LISTA = reverse("cadastro:contas_membros")


def prorrogar(conta):
    """Endereço da ação de prorrogar (Usuarios do membro)."""
    return reverse("cadastro:contas_membro_prorrogar", args=[conta.pk])


def no_dia(dia):
    """Relógio parado às 10h do dia."""
    return mock.patch(
        "django.utils.timezone.now",
        return_value=datetime(dia.year, dia.month, dia.day, 10, 0),
    )


def validade(conta):
    return MembrosExternos.objects.get(pk=conta.pk).mem_validade_ate


class ProrrogacaoTest(TesteContas):
    """US-50 fluxo principal, A a C e E1 a E4."""

    def setUp(self):
        super().setUp()
        professor = docente_de(EC)
        turma = turma_do_docente(professor)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.APTO_PARA_DEFESA)
        self.orientador = docente_de(EC)
        self.usuario = self.orientador
        orientacao_ativa(self.orientador, tcc_de(aluno, turma))
        self.defesa = criar_defesa(tcc=tcc_de(aluno, turma), def_data=date(2026, 10, 20))
        self.client.force_login(self.orientador)

    def _post(self, dia, conta, usuario=None, follow=False):
        """POST de prorrogar com o relógio no dia; o login é refeito no mesmo dia simulado (o
        tempo de inatividade da sessão, spec 003, usa o mesmo relógio)."""
        with no_dia(dia):
            self.client.force_login(usuario or self.usuario)
            return self.client.post(prorrogar(conta), follow=follow)

    def _da_banca(self, **campos):
        conta = membro(**campos)
        banca(self.defesa, conta)
        return conta

    def test_cenario_01_orientador_prorroga(self):
        conta = self._da_banca(validade=date(2026, 10, 27))
        self.assertContains(self.client.get(LISTA), prorrogar(conta))
        resposta = self._post(date(2026, 10, 25), conta, follow=True)
        self.assertContains(resposta, "Acesso prorrogado até 03/11/2026")
        self.assertEqual(validade(conta), date(2026, 11, 3))

    def test_cenario_02_expirada_volta_a_ativa(self):
        conta = self._da_banca(status=StatusConta.EXPIRADA, validade=date(2026, 10, 1))
        self._post(date(2026, 10, 6), conta)
        with no_dia(date(2026, 10, 6)):
            self.assertEqual(validade(conta), date(2026, 10, 13))
            self.assertEqual(Usuarios.objects.get(pk=conta.pk).usu_status, StatusConta.ATIVA)
            self.client.logout()
            resposta = self.client.post(
                reverse("cadastro:entrar"), {"credencial": conta.usu_email, "senha": SENHA}
            )
        self.assertEqual(resposta.status_code, 302)

    def test_cenario_03_duas_prorrogacoes_somam(self):
        conta = self._da_banca(validade=date(2026, 10, 27))
        self._post(date(2026, 10, 25), conta)
        self._post(date(2026, 10, 25), conta)
        self.assertEqual(validade(conta), date(2026, 11, 10))

    def test_cenario_04_secretaria_prorroga_qualquer_membro(self):
        conta = membro(validade=date(2026, 10, 27))
        resposta = self._post(date(2026, 10, 25), conta, secretaria_de(SI), follow=True)
        self.assertContains(resposta, "Acesso prorrogado até 03/11/2026")

    def test_coordenador_e_professor_com_turma_ativa_prorrogam(self):
        professor = docente_de(SI)
        turma_do_docente(professor)
        for conta_gestor in (coordenador_de(SI), professor):
            with self.subTest(gestor=conta_gestor.pk):
                conta = membro(validade=date(2026, 10, 27))
                self._post(date(2026, 10, 25), conta, conta_gestor)
                self.assertEqual(validade(conta), date(2026, 11, 3))

    def test_cenario_05_sem_login_vai_ao_login_e_volta(self):
        self.client.logout()
        resposta = self.client.get(LISTA)
        self.assertRedirects(
            resposta, f"{reverse('cadastro:entrar')}?next={LISTA}", fetch_redirect_response=False
        )

    def test_cenario_06_orientador_sem_vinculo_nao_ve_o_botao(self):
        conta = membro(validade=date(2026, 10, 27))
        self.assertNotContains(self.client.get(LISTA), prorrogar(conta))
        resposta = self.client.post(prorrogar(conta))
        self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)
        self.assertEqual(validade(conta), date(2026, 10, 27))

    def test_q11_sessao_cancelada_nao_da_vinculo(self):
        conta = membro(validade=date(2026, 10, 27))
        cancelada = criar_defesa(
            tcc=self.defesa.def_tcc, def_data=date(2026, 10, 25), def_status=StatusSessao.CANCELADA
        )
        banca(cancelada, conta)
        self.assertNotContains(self.client.get(LISTA), prorrogar(conta))

    def test_cenario_07_aluno_pelo_endereco_direto(self):
        conta = membro(validade=date(2026, 10, 27))
        self.client.force_login(
            criar_aluno_com_turma(email="al@uea.edu.br", status=StatusConta.ATIVA).alu
        )
        for metodo in (self.client.get, self.client.post):
            resposta = metodo(prorrogar(conta))
            self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)
        self.assertEqual(validade(conta), date(2026, 10, 27))

    def test_cenario_08_aguardando_ativacao_sem_botao_e_mc09(self):
        conta = self._da_banca(status=StatusConta.AGUARDANDO_ATIVACAO, validade=date(2026, 10, 27))
        self.assertNotContains(self.client.get(LISTA), prorrogar(conta))
        resposta = self.client.post(prorrogar(conta), follow=True)
        self.assertContains(resposta, mensagens.MC09_SEM_VALIDADE)
        self.assertEqual(validade(conta), date(2026, 10, 27))

    def test_cenario_09_falha_ao_gravar(self):
        conta = self._da_banca(validade=date(2026, 10, 27))
        with (
            mock.patch.object(MembrosExternos, "save", side_effect=DatabaseError),
            self.assertLogs("sigtcc.contas", "ERROR"),
        ):
            resposta = self.client.post(prorrogar(conta), follow=True)
        self.assertContains(resposta, mensagens.FALHA_AO_PRORROGAR)
        self.assertEqual(validade(conta), date(2026, 10, 27))

    def test_q10_professor_so_com_turma_arquivada_nao_prorroga(self):
        professor = docente_de(SI)
        turma_do_docente(professor, status=StatusTurma.ARQUIVADA)
        conta = membro(validade=date(2026, 10, 27))
        self.client.force_login(professor)
        self.assertNotContains(self.client.get(LISTA), prorrogar(conta))
        self.assertEqual(self.client.post(prorrogar(conta)).status_code, 403)

    def test_q36_prorrogacao_grava_a_data_protegida(self):
        conta = self._da_banca(validade=date(2026, 10, 27))
        self._post(date(2026, 10, 25), conta)
        self.assertEqual(
            MembrosExternos.objects.get(pk=conta.pk).mem_prorrogado_ate, date(2026, 11, 3)
        )

    def test_sem_validade_conta_de_hoje(self):
        conta = self._da_banca(validade=None)
        self._post(date(2026, 10, 25), conta)
        self.assertEqual(validade(conta), date(2026, 11, 1))

    def test_log_de_prorrogacao(self):
        conta = self._da_banca(validade=date(2026, 10, 27))
        with self.assertLogs("sigtcc.acesso", "INFO") as log:
            self._post(date(2026, 10, 25), conta)
        self.assertTrue(any("ACESSO_PRORROGADO" in linha for linha in log.output))
