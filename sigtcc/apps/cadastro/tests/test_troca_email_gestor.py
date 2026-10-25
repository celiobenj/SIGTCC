"""Testes da troca de e-mail pelo gestor (tasks T027): US-03 cenário 32, US-05 cenário 17 e as
Clarifications Q17, Q24, Q28, Q30, Q31 e Q35.

[US-03][US-05][RBN-CAD-01.2][RBN-CAD-02.2][RBN-CAD-03.2][FR-008][Q17][Q24][Q28][Q30][Q31][Q35]
"""

from unittest import mock

from django.core import mail
from django.urls import reverse

from sigtcc.apps.cadastro import mensagens, services
from sigtcc.apps.cadastro.choices import StatusConta, StatusTCC
from sigtcc.apps.cadastro.models import Usuarios
from sigtcc.apps.cadastro.services import EstadoLink
from sigtcc.apps.cadastro.tests.apoio_acesso import SENHA, caminho_do_link
from sigtcc.apps.cadastro.tests.apoio_contas import (
    EC,
    SI,
    TesteContas,
    coordenador_de,
    curso,
    docente_de,
    membro,
    orientacao_ativa,
    secretaria_de,
    turma_do_docente,
)
from sigtcc.apps.cadastro.tests.apoio_turmas import matricular_aluno, tcc_de


def editar_docente(conta):
    return reverse("cadastro:contas_docente_editar", args=[conta.pk])


def editar_membro(conta):
    return reverse("cadastro:contas_membro_editar", args=[conta.pk])


def dados_docente(conta, **campos):
    """POST de alteração do docente com nome válido e os dados atuais."""
    valores = {
        "nome": "Nome Do Docente",
        "email": conta.usu_email,
        "titulacao": conta.docentes.doc_titulacao,
        "curso_lotacao": conta.docentes.doc_cur_id,
    }
    valores.update(campos)
    return valores


def dados_membro(conta, **campos):
    """POST de alteração do membro com nome válido e os dados atuais."""
    valores = {
        "nome": "Nome Do Membro",
        "email": conta.usu_email,
        "titulacao": conta.membrosexternos.mem_titulacao,
        "instituicao": conta.membrosexternos.mem_instituicao,
    }
    valores.update(campos)
    return valores


def confirmar(cliente, mensagem):
    """Abre o link do e-mail e clica em "Confirmar novo e-mail" (spec 003, Q28)."""
    caminho = caminho_do_link(mensagem)
    cliente.get(caminho)
    return cliente.post(caminho)


class TrocaEmailDocenteTest(TesteContas):
    """US-03 A11 e cenário 32 (Q17, Q24, Q35). [FR-008]"""

    def setUp(self):
        super().setUp()
        self.secretaria = secretaria_de(SI)
        self.client.force_login(self.secretaria)
        self.docente = docente_de(SI, email="antigo@uea.edu.br")

    def test_cenario_32_email_muda_so_depois_da_confirmacao(self):
        resposta = self.client.post(
            editar_docente(self.docente),
            dados_docente(self.docente, email="novo@uea.edu.br", sua_senha=SENHA),
            follow=True,
        )
        self.assertContains(resposta, mensagens.MC12_TROCA_EMAIL_ENVIADA)
        self.assertEqual(mail.outbox[-1].to, ["novo@uea.edu.br"])
        self.docente.refresh_from_db()
        self.assertEqual(self.docente.usu_email, "antigo@uea.edu.br")
        self.assertEqual(self.docente.usu_nome, "Nome Do Docente")
        anonimo = self.client_class()
        resposta = confirmar(anonimo, mail.outbox[-1])
        self.assertContains(resposta, mensagens.M07_EMAIL_ATUALIZADO)
        self.docente.refresh_from_db()
        self.assertEqual(self.docente.usu_email, "novo@uea.edu.br")
        self.assertTrue(self.docente.check_password(SENHA))

    def test_senha_errada_mc11_nada_gravado_e_log_sem_limite(self):
        for _ in range(4):
            with self.assertLogs("sigtcc.acesso", "INFO") as log:
                resposta = self.client.post(
                    editar_docente(self.docente),
                    dados_docente(self.docente, email="novo@uea.edu.br", sua_senha="Errada123"),
                )
            self.assertContains(resposta, mensagens.MC11_SENHA_INCORRETA)
            self.assertTrue(any("SENHA_GESTOR_INCORRETA" in linha for linha in log.output))
        self.docente.refresh_from_db()
        self.assertNotEqual(self.docente.usu_nome, "Nome Do Docente")
        self.assertEqual(mail.outbox, [])

    def test_sem_senha_tambem_e_mc11(self):
        resposta = self.client.post(
            editar_docente(self.docente), dados_docente(self.docente, email="novo@uea.edu.br")
        )
        self.assertContains(resposta, mensagens.MC11_SENHA_INCORRETA)

    def test_q24_falha_no_envio_grava_os_demais_campos(self):
        with mock.patch.object(services, "enviar_email", side_effect=RuntimeError):
            resposta = self.client.post(
                editar_docente(self.docente),
                dados_docente(self.docente, email="novo@uea.edu.br", sua_senha=SENHA),
                follow=True,
            )
        self.assertContains(resposta, mensagens.MC13_FALHA_ENVIO_TROCA)
        self.docente.refresh_from_db()
        self.assertEqual(self.docente.usu_nome, "Nome Do Docente")
        self.assertEqual(self.docente.usu_email, "antigo@uea.edu.br")

    def test_m12_so_a_caixa_diferente_nao_abre_troca(self):
        resposta = self.client.post(
            editar_docente(self.docente),
            dados_docente(self.docente, email="ANTIGO@uea.edu.br"),
            follow=True,
        )
        self.assertContains(resposta, mensagens.DADOS_ATUALIZADOS)
        self.assertEqual(mail.outbox, [])

    def test_m05_so_na_confirmacao_se_o_email_ficou_ocupado(self):
        self.client.post(
            editar_docente(self.docente),
            dados_docente(self.docente, email="novo@uea.edu.br", sua_senha=SENHA),
        )
        docente_de(EC, email="novo@uea.edu.br")
        resposta = confirmar(self.client_class(), mail.outbox[-1])
        self.assertContains(resposta, mensagens.M05_EMAIL_EM_USO)
        self.docente.refresh_from_db()
        self.assertEqual(self.docente.usu_email, "antigo@uea.edu.br")

    def test_q28_dois_links_pendentes_o_primeiro_vale_ate_outro_ser_confirmado(self):
        for email in ("errado@uea.edu.br", "certo@uea.edu.br"):
            self.client.post(
                editar_docente(self.docente),
                dados_docente(self.docente, email=email, sua_senha=SENHA),
            )
        primeiro, segundo = mail.outbox[-2], mail.outbox[-1]
        self.assertContains(confirmar(self.client_class(), segundo), mensagens.M07_EMAIL_ATUALIZADO)
        resposta = confirmar(self.client_class(), primeiro)
        self.assertContains(resposta, mensagens.M09_LINK_EMAIL_INVALIDO)

    def test_q31_confirmacao_invalida_link_de_ativacao_antigo(self):
        conta = docente_de(SI, status=StatusConta.AGUARDANDO_ATIVACAO, email="errado@uea.edu.br")
        link_antigo = services.gerar_link_ativacao(conta)
        token = link_antigo.rstrip("/").rsplit("/", 1)[-1]
        self.client.post(
            editar_docente(conta), dados_docente(conta, email="certo@uea.edu.br", sua_senha=SENHA)
        )
        confirmar(self.client_class(), mail.outbox[-1])
        self.assertEqual(services.validar_link_ativacao(token).estado, EstadoLink.SUBSTITUIDO)


class TrocaEmailMembroTest(TesteContas):
    """US-05 A3, cenário 17 e a restrição da Q30. [FR-008][FR-035]"""

    def test_cenario_17_secretaria_troca_o_email_do_membro(self):
        conta = membro(email="ana@ufam.edu.br")
        self.client.force_login(secretaria_de(SI))
        self.client.post(
            editar_membro(conta), dados_membro(conta, email="novo@ufam.edu.br", sua_senha=SENHA)
        )
        conta.refresh_from_db()
        self.assertEqual(conta.usu_email, "ana@ufam.edu.br")
        confirmar(self.client_class(), mail.outbox[-1])
        conta.refresh_from_db()
        self.assertEqual(conta.usu_email, "novo@ufam.edu.br")
        self.assertTrue(conta.check_password(SENHA))

    def _orientador(self):
        professor = docente_de(EC)
        turma = turma_do_docente(professor)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        conta = docente_de(EC)
        orientacao_ativa(conta, tcc_de(aluno, turma))
        return conta

    def test_q30_orientador_nao_troca_email_de_conta_ativa_ou_expirada(self):
        self.client.force_login(self._orientador())
        for status in (StatusConta.ATIVA, StatusConta.EXPIRADA):
            with self.subTest(status=status):
                conta = membro(status=status)
                resposta = self.client.get(editar_membro(conta))
                self.assertContains(resposta, "disabled")
                resposta = self.client.post(
                    editar_membro(conta),
                    dados_membro(conta, email="meu@empresa.com", sua_senha=SENHA),
                )
                conta.refresh_from_db()
                self.assertNotEqual(conta.usu_email, "meu@empresa.com")
                self.assertEqual(mail.outbox, [])

    def test_q30_servico_recusa_troca_pelo_endereco_direto(self):
        from django.core.exceptions import PermissionDenied

        from sigtcc.apps.cadastro import services_contas

        orientador = self._orientador()
        conta = membro()
        dados = dados_membro(conta, email="meu@empresa.com", sua_senha=SENHA)
        dados.update({"titulacao": "Doutor"})
        with self.assertRaises(PermissionDenied):
            services_contas.alterar_membro(orientador, conta.pk, dados)

    def test_q30_orientador_troca_email_de_conta_aguardando_ativacao(self):
        self.client.force_login(self._orientador())
        conta = membro(status=StatusConta.AGUARDANDO_ATIVACAO)
        resposta = self.client.post(
            editar_membro(conta),
            dados_membro(conta, email="certo@empresa.com", sua_senha=SENHA),
            follow=True,
        )
        self.assertContains(resposta, mensagens.MC12_TROCA_EMAIL_ENVIADA)

    def test_coordenador_troca_email_de_conta_ativa(self):
        conta = membro()
        self.client.force_login(coordenador_de(SI))
        resposta = self.client.post(
            editar_membro(conta),
            dados_membro(conta, email="novo@empresa.com", sua_senha=SENHA),
            follow=True,
        )
        self.assertContains(resposta, mensagens.MC12_TROCA_EMAIL_ENVIADA)

    def test_secretaria_corrige_conta_aguardando_ativacao(self):
        self.client.force_login(secretaria_de(SI))
        conta = docente_de(SI, status=StatusConta.AGUARDANDO_ATIVACAO, email="errado@uea.edu.br")
        self.client.post(
            editar_docente(conta), dados_docente(conta, email="certo@uea.edu.br", sua_senha=SENHA)
        )
        confirmar(self.client_class(), mail.outbox[-1])
        self.assertTrue(Usuarios.objects.filter(usu_email="certo@uea.edu.br").exists())
        self.assertEqual(curso(SI).pk, Usuarios.objects.get(pk=conta.pk).docentes.doc_cur_id)
