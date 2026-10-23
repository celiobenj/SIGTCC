"""Testes de aceite da US-04 (cenários 1 a 25) e das Clarifications Q14, Q16, Q18 e Q27 (tasks
T030).

[US-04][RBN-CAD-01.3][RBN-CAD-02.3][FR-024][FR-025][FR-026][FR-027][FR-028][FR-029][FR-030]
[Q14][Q16][Q18][Q27]
"""

from unittest import mock

from django.db import DatabaseError
from django.urls import reverse

from sigtcc.apps.cadastro import mensagens, services_contas
from sigtcc.apps.cadastro.choices import (
    StatusConta,
    StatusEntrega,
    StatusSolicitacao,
    StatusTCC,
    StatusTurma,
    TipoSolicitacao,
)
from sigtcc.apps.cadastro.models import Coordenadores, Orientacoes, Usuarios
from sigtcc.apps.cadastro.tests.apoio_acesso import SENHA, criar_aluno_com_turma
from sigtcc.apps.cadastro.tests.apoio_contas import (
    EC,
    SI,
    TesteContas,
    banca,
    convite_pendente,
    coordenador_de,
    coorientacao_ativa,
    curso,
    docente_de,
    marco_versao_final,
    orientacao_ativa,
    secretaria_de,
    turma_do_docente,
)
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    criar_defesa_de,
    criar_solicitacao,
    matricular_aluno,
    tcc_de,
)
from sigtcc.apps.defesa.choices import StatusSessao

LISTA = reverse("cadastro:contas_docentes")
LISTA_SEC = reverse("cadastro:contas_secretarias")


def inativar(conta):
    """Endereço da inativação do docente (Usuarios)."""
    return reverse("cadastro:contas_docente_inativar", args=[conta.pk])


def reativar(conta):
    """Endereço da reativação do docente (Usuarios)."""
    return reverse("cadastro:contas_docente_reativar", args=[conta.pk])


def alerta_tcc(n):
    """Texto do alerta com só o motivo (a) (US-04 E1; Q18)."""
    return mensagens.NAO_E_POSSIVEL_INATIVAR.format(motivos=mensagens.MOTIVO_TCC_ATIVO.format(n=n))


def alerta_unico(motivo):
    """Texto do alerta com um só motivo."""
    return mensagens.NAO_E_POSSIVEL_INATIVAR.format(motivos=motivo)


class InativacaoDocenteTest(TesteContas):
    """US-04 fluxo principal e E1 a E8 (cenários 1 a 18, 24 e 25)."""

    def setUp(self):
        super().setUp()
        self.client.force_login(secretaria_de(SI))
        self.docente = docente_de(SI, email="prof@uea.edu.br")
        self.professor = docente_de(SI)

    def _tcc(self, status, orientador=None):
        """TCC no Status pedido numa turma de outro professor, orientado pelo docente."""
        turma = turma_do_docente(self.professor)
        aluno = matricular_aluno(turma, status_tcc=status)
        tcc = tcc_de(aluno, turma)
        if orientador is not False:
            orientacao_ativa(orientador or self.docente, tcc)
        return tcc

    def _tentar(self):
        """GET da inativação: devolve a mensagem de erro (ou None) e a resposta seguida."""
        resposta = self.client.get(inativar(self.docente), follow=True)
        return resposta

    def _status(self):
        self.docente.refresh_from_db()
        return self.docente.usu_status

    def test_cenario_01_inativar_sem_vinculos(self):
        resposta = self.client.get(inativar(self.docente))
        self.assertContains(
            resposta, mensagens.CONFIRMAR_INATIVAR_DOCENTE.format(nome=self.docente.usu_nome)
        )
        resposta = self.client.post(inativar(self.docente), follow=True)
        self.assertContains(resposta, mensagens.DOCENTE_INATIVADO)
        self.assertEqual(self._status(), StatusConta.INATIVA)
        ativos = services_contas.docentes_ativos().values_list("pk", flat=True)
        self.assertNotIn(self.docente.pk, ativos)

    def test_cenario_02_orientando_com_tcc_em_andamento(self):
        self._tcc(StatusTCC.EM_ANDAMENTO)
        resposta = self._tentar()
        self.assertContains(resposta, alerta_tcc(1))
        self.assertContains(resposta, "orientandos")
        self.assertEqual(self._status(), StatusConta.ATIVA)

    def test_cenario_03_coorientando_com_tcc_apto(self):
        tcc = self._tcc(StatusTCC.APTO_PARA_DEFESA, orientador=False)
        coorientacao_ativa(self.docente, tcc)
        resposta = self._tentar()
        self.assertContains(resposta, alerta_tcc(1))
        self.assertContains(resposta, "coorientandos com TCC ativo")

    def test_cenario_04_aprovado_sem_versao_final_homologada(self):
        tcc = self._tcc(StatusTCC.APROVADO_COM_CORRECOES)
        marco_versao_final(tcc.tcc_tur, tcc.tcc_alu, status=StatusEntrega.ENTREGUE)
        self.assertContains(self._tentar(), alerta_tcc(1))

    def test_cenario_04_aprovado_com_versao_final_homologada_nao_impede(self):
        tcc = self._tcc(StatusTCC.APROVADO)
        marco_versao_final(tcc.tcc_tur, tcc.tcc_alu, status=StatusEntrega.HOMOLOGADA)
        self.client.post(inativar(self.docente))
        self.assertEqual(self._status(), StatusConta.INATIVA)

    def test_cenario_05_convite_de_coorientacao_pendente(self):
        convite_pendente(self.docente, self._tcc(StatusTCC.EM_ANDAMENTO, orientador=False))
        self.assertContains(self._tentar(), alerta_unico(mensagens.MC05_CONVITE_1))

    def test_cenarios_06_e_07_banca_em_aberto(self):
        for status in (StatusSessao.AGENDADA, StatusSessao.REAGENDADA, StatusSessao.EM_ANDAMENTO):
            with self.subTest(status=status):
                defesa = criar_defesa_de(
                    self._tcc(StatusTCC.APTO_PARA_DEFESA, orientador=False), status
                )
                linha = banca(defesa, self.docente)
                self.assertContains(self._tentar(), alerta_unico(mensagens.MC06_BANCA_1))
                linha.delete()

    def test_cenario_08_turma_nao_arquivada(self):
        turma_do_docente(self.docente)
        self.assertContains(self._tentar(), alerta_unico(mensagens.MC07_TURMA_1))

    def test_cenario_09_coordenador_de_curso(self):
        Coordenadores.objects.create(cor_cur=curso(EC), cor_doc=self.docente.docentes)
        self.assertContains(self._tentar(), alerta_unico(mensagens.MOTIVO_COORDENADOR))

    def test_cenario_10_todos_os_motivos(self):
        self._tcc(StatusTCC.EM_ANDAMENTO)
        self._tcc(StatusTCC.EM_ANDAMENTO)
        turma_do_docente(self.docente)
        turma_do_docente(self.docente)
        esperado = (
            mensagens.NAO_E_POSSIVEL_INATIVAR.format(
                motivos=mensagens.MOTIVO_TCC_ATIVO.format(n=2)
                + " e "
                + mensagens.MC07_TURMAS.format(n=2)
            )
            + mensagens.FIM_ALERTA_VINCULOS
        )
        self.assertContains(self._tentar(), esperado)

    def test_alerta_com_tres_motivos_usa_virgula_e_e(self):
        contagens = {"tcc_ativo": 1, "convites": 2, "bancas": 0, "turmas": 0, "coordenador": True}
        self.assertEqual(
            services_contas.alerta_de_vinculos(contagens),
            mensagens.NAO_E_POSSIVEL_INATIVAR.format(
                motivos=mensagens.MOTIVO_TCC_ATIVO.format(n=1)
                + ", "
                + mensagens.MC05_CONVITES.format(n=2)
                + " e "
                + mensagens.MOTIVO_COORDENADOR
            )
            + mensagens.FIM_ALERTA_VINCULOS,
        )

    def test_cenario_11_tcc_sem_proposta_nao_impede(self):
        self._tcc(StatusTCC.SEM_PROPOSTA)
        self.client.post(inativar(self.docente))
        self.assertEqual(self._status(), StatusConta.INATIVA)

    def test_cenario_12_vinculos_encerrados_nao_impedem(self):
        for status in (
            StatusTCC.CONCLUIDO,
            StatusTCC.REPROVADO,
            StatusTCC.DESISTENTE,
            StatusTCC.JUBILADO,
        ):
            self._tcc(status)
        for status in (StatusSessao.REALIZADA, StatusSessao.CANCELADA):
            banca(
                criar_defesa_de(self._tcc(StatusTCC.APTO_PARA_DEFESA, False), status), self.docente
            )
        criar_solicitacao(
            self._tcc(StatusTCC.EM_ANDAMENTO, False),
            self.docente,
            tipo=TipoSolicitacao.COORIENTACAO,
            status=StatusSolicitacao.RECUSADO,
        )
        turma_do_docente(self.docente, status=StatusTurma.ARQUIVADA)
        self.client.post(inativar(self.docente))
        self.assertEqual(self._status(), StatusConta.INATIVA)

    def test_cenario_13_coordenador_desmarcado_pode_ser_inativado(self):
        linha = Coordenadores.objects.create(cor_cur=curso(SI), cor_doc=self.docente.docentes)
        linha.delete()
        self.client.post(inativar(self.docente))
        self.assertEqual(self._status(), StatusConta.INATIVA)
        self.assertFalse(Coordenadores.objects.filter(cor_cur=curso(SI)).exists())

    def test_cenario_14_cancelar_nao_altera(self):
        resposta = self.client.get(inativar(self.docente))
        self.assertContains(resposta, f'href="{LISTA}">Cancelar')
        self.assertEqual(self._status(), StatusConta.ATIVA)

    def test_cenario_15_vinculo_que_surge_durante_a_confirmacao(self):
        self.assertEqual(self.client.get(inativar(self.docente)).status_code, 200)
        convite_pendente(self.docente, self._tcc(StatusTCC.EM_ANDAMENTO, orientador=False))
        resposta = self.client.post(inativar(self.docente), follow=True)
        self.assertContains(resposta, alerta_unico(mensagens.MC05_CONVITE_1))
        self.assertEqual(self._status(), StatusConta.ATIVA)

    def test_cenario_16_login_negado_e_historico_mantido(self):
        tcc = self._tcc(StatusTCC.CONCLUIDO)
        self.client.post(inativar(self.docente))
        self.client.logout()
        resposta = self.client.post(
            reverse("cadastro:entrar"), {"credencial": "prof@uea.edu.br", "senha": SENHA}
        )
        self.assertContains(resposta, mensagens.CONTA_INATIVA)
        self.assertTrue(
            Orientacoes.objects.filter(ori_tcc=tcc, ori_doc_id=self.docente.pk).exists()
        )

    def test_cenario_17_lista_mostra_reativar_para_inativo(self):
        Usuarios.objects.filter(pk=self.docente.pk).update(usu_status=StatusConta.INATIVA)
        resposta = self.client.get(LISTA)
        self.assertContains(resposta, reativar(self.docente))
        self.assertNotContains(resposta, inativar(self.docente))

    def test_cenario_18_outro_curso_sem_acoes_e_recusa_direta(self):
        outro = docente_de(EC)
        resposta = self.client.get(LISTA, {"curso": curso(EC).pk})
        self.assertNotContains(resposta, inativar(outro))
        resposta = self.client.post(inativar(outro))
        self.assertContains(resposta, mensagens.SO_DO_SEU_CURSO_ALTERACAO, status_code=403)
        outro.refresh_from_db()
        self.assertEqual(outro.usu_status, StatusConta.ATIVA)

    def test_e10_status_incompativel_pelo_endereco_direto(self):
        aguardando = docente_de(SI, status=StatusConta.AGUARDANDO_ATIVACAO)
        for conta, rota in (
            (aguardando, inativar),
            (aguardando, reativar),
            (self.docente, reativar),
        ):
            with self.subTest(rota=rota.__name__):
                resposta = self.client.post(rota(conta), follow=True)
                self.assertContains(resposta, mensagens.MC10_STATUS_INCOMPATIVEL)
        aguardando.refresh_from_db()
        self.assertEqual(aguardando.usu_status, StatusConta.AGUARDANDO_ATIVACAO)

    def test_cenario_24_aluno_nao_abre_docentes(self):
        aluno = criar_aluno_com_turma(email="al@uea.edu.br", status=StatusConta.ATIVA).alu
        self.client.force_login(aluno)
        resposta = self.client.get(LISTA)
        self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)

    def test_cenario_25_falha_ao_gravar(self):
        with (
            mock.patch.object(Usuarios, "save", side_effect=DatabaseError),
            self.assertLogs("sigtcc.contas", "ERROR"),
        ):
            resposta = self.client.post(inativar(self.docente), follow=True)
        self.assertContains(resposta, mensagens.FALHA_AO_SALVAR)
        self.assertEqual(self._status(), StatusConta.ATIVA)

    def test_log_de_inativacao(self):
        with self.assertLogs("sigtcc.acesso", "INFO") as log:
            self.client.post(inativar(self.docente))
        self.assertTrue(any("CONTA_INATIVADA" in linha for linha in log.output))


class ReativacaoDocenteTest(TesteContas):
    """US-04 A1 e cenários 19 e 20. [FR-029]"""

    def setUp(self):
        super().setUp()
        self.client.force_login(coordenador_de(SI))

    def test_cenario_19_reativar(self):
        docente = docente_de(SI, status=StatusConta.INATIVA)
        resposta = self.client.get(reativar(docente))
        self.assertContains(
            resposta, mensagens.MC01_CONFIRMAR_REATIVAR.format(nome=docente.usu_nome)
        )
        resposta = self.client.post(reativar(docente), follow=True)
        self.assertContains(resposta, mensagens.MC02_DOCENTE_REATIVADO)
        docente.refresh_from_db()
        self.assertEqual(docente.usu_status, StatusConta.ATIVA)
        self.assertTrue(docente.check_password(SENHA))
        self.assertIn(docente.pk, services_contas.docentes_ativos().values_list("pk", flat=True))

    def test_cenario_20_inativo_de_outro_curso(self):
        docente = docente_de(EC, status=StatusConta.INATIVA)
        resposta = self.client.get(LISTA, {"curso": curso(EC).pk})
        self.assertNotContains(resposta, reativar(docente))
        resposta = self.client.post(reativar(docente))
        self.assertEqual(resposta.status_code, 403)
        docente.refresh_from_db()
        self.assertEqual(docente.usu_status, StatusConta.INATIVA)


class InativacaoSecretariaTest(TesteContas):
    """US-04 A2 e cenários 21 a 23 (Q27). [FR-024]"""

    def setUp(self):
        super().setUp()
        self.coordenador = coordenador_de(SI)
        self.secretaria = secretaria_de(SI, email="sec@uea.edu.br")

    def _inativar(self):
        return reverse("cadastro:contas_secretaria_inativar", args=[self.secretaria.pk])

    def test_cenarios_21_e_22_inativar_e_cadastrar_outra(self):
        self.client.force_login(self.coordenador)
        resposta = self.client.get(self._inativar())
        self.assertContains(
            resposta,
            mensagens.MC03_CONFIRMAR_INATIVAR_SECRETARIA.format(nome=self.secretaria.usu_nome),
        )
        resposta = self.client.post(self._inativar(), follow=True)
        self.assertContains(resposta, mensagens.MC04_SECRETARIA_INATIVADA)
        self.secretaria.refresh_from_db()
        self.assertEqual(self.secretaria.usu_status, StatusConta.INATIVA)
        self.client.post(
            reverse("cadastro:contas_secretaria_nova"),
            {
                "nome": "Nova Secretaria",
                "email": "nova@uea.edu.br",
                "curso_vinculado": curso(SI).pk,
            },
        )
        self.assertTrue(Usuarios.objects.filter(usu_email="nova@uea.edu.br").exists())

    def test_cenario_23_secretaria_nao_inativa(self):
        self.client.force_login(secretaria_de(EC))
        resposta = self.client.get(LISTA_SEC, {"curso": "todos"})
        self.assertNotContains(resposta, self._inativar())
        resposta = self.client.post(self._inativar())
        self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)

    def test_q27_secretaria_inativada_nao_tem_reativar(self):
        self.client.force_login(self.coordenador)
        self.client.post(self._inativar())
        resposta = self.client.get(LISTA_SEC)
        self.assertNotContains(resposta, "Reativar")
