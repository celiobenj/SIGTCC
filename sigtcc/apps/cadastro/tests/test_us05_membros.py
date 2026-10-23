"""Testes de aceite da US-05 (cenários 1 a 16 e 18 a 23; o 17, troca de e-mail, fica em
test_troca_email_gestor.py) e das Clarifications Q10, Q12 e Q19 (tasks T023).

[US-05][RBN-CAD-03.1][RBN-CAD-03.2][RBN-DEF-02.3][FR-031][FR-032][FR-033][FR-034][FR-035]
[FR-036][FR-038][Q10][Q12][Q19]
"""

from datetime import date, datetime
from unittest import mock

from django.core import mail
from django.db import DatabaseError
from django.urls import reverse

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import StatusConta, StatusTCC, StatusTurma
from sigtcc.apps.cadastro.models import MembrosExternos, Usuarios
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_aluno_com_turma
from sigtcc.apps.cadastro.tests.apoio_contas import (
    EC,
    SI,
    TesteContas,
    coordenador_de,
    docente_de,
    membro,
    orientacao_ativa,
    secretaria_de,
    turma_do_docente,
)
from sigtcc.apps.cadastro.tests.apoio_turmas import matricular_aluno, tcc_de

LISTA = reverse("cadastro:contas_membros")
NOVO = reverse("cadastro:contas_membro_novo")


def editar(conta):
    """Endereço da edição do membro (Usuarios)."""
    return reverse("cadastro:contas_membro_editar", args=[conta.pk])


def dados(**campos):
    """POST válido do formulário de Membro Externo."""
    valores = {
        "nome": "Ana Souza",
        "email": "ana@ufam.edu.br",
        "titulacao": "Doutor",
        "instituicao": "Universidade Federal do Amazonas",
    }
    valores.update(campos)
    return valores


def orientador():
    """Docente com orientação 'Ativa' (papel Orientador). Devolve o Usuarios."""
    professor = docente_de(EC)
    turma = turma_do_docente(professor)
    aluno = matricular_aluno(turma, status_tcc=StatusTCC.EM_ANDAMENTO)
    conta = docente_de(EC)
    orientacao_ativa(conta, tcc_de(aluno, turma))
    return conta


class CadastroMembroTest(TesteContas):
    """US-05 fluxo principal, A1, A4, A5 e E1 a E8 (cenários 1 a 15 e 20 a 23)."""

    def setUp(self):
        super().setUp()
        self.orientador = orientador()
        self.client.force_login(self.orientador)

    def test_cenario_01_orientador_cadastra(self):
        resposta = self.client.post(NOVO, dados(), follow=True)
        self.assertContains(resposta, mensagens.MEMBRO_CADASTRADO)
        conta = Usuarios.objects.get(usu_email="ana@ufam.edu.br")
        self.assertEqual(conta.usu_status, StatusConta.AGUARDANDO_ATIVACAO)
        self.assertEqual(mail.outbox, [])

    def test_cenario_02_professor_secretaria_e_coordenador_cadastram(self):
        professor = docente_de(EC)
        turma_do_docente(professor)
        for indice, conta in enumerate((professor, secretaria_de(SI), coordenador_de(SI))):
            with self.subTest(perfil=indice):
                self.client.force_login(conta)
                self.client.post(NOVO, dados(email=f"m{indice}@empresa.com"))
                self.assertEqual(
                    Usuarios.objects.get(usu_email=f"m{indice}@empresa.com").usu_status,
                    StatusConta.AGUARDANDO_ATIVACAO,
                )

    def test_cenario_03_email_de_qualquer_dominio(self):
        self.client.post(NOVO, dados(email="carlos@empresa.com.br"))
        self.assertTrue(Usuarios.objects.filter(usu_email="carlos@empresa.com.br").exists())

    def test_cenarios_04_e_05_email_ja_usado_inclusive_expirado(self):
        membro(email="luisa@ufam.edu.br", status=StatusConta.EXPIRADA)
        resposta = self.client.post(NOVO, dados(email="luisa@ufam.edu.br"))
        self.assertContains(resposta, mensagens.EMAIL_JA_CADASTRADO)
        self.assertEqual(Usuarios.objects.filter(usu_email="luisa@ufam.edu.br").count(), 1)

    def test_cenarios_06_e_07_email_invalido(self):
        longo = "a" * (101 - len("@ufam.edu.br")) + "@ufam.edu.br"
        for email in ("ana.ufam.edu.br", longo):
            with self.subTest(email=email):
                resposta = self.client.post(NOVO, dados(email=email))
                self.assertContains(resposta, mensagens.EMAIL_VALIDO)
        self.assertEqual(MembrosExternos.objects.count(), 0)

    def test_cenarios_08_e_09_campos_obrigatorios(self):
        for campo in ("instituicao", "nome", "titulacao"):
            with self.subTest(campo=campo):
                resposta = self.client.post(NOVO, dados(**{campo: ""}))
                self.assertContains(resposta, mensagens.M14_CAMPO_OBRIGATORIO)
        self.assertEqual(MembrosExternos.objects.count(), 0)

    def test_cenario_10_nome_com_numero(self):
        resposta = self.client.post(NOVO, dados(nome="Ana Souza 2"))
        self.assertContains(resposta, mensagens.NOME_INVALIDO)

    def test_cenario_11_instituicao_com_pontuacao(self):
        instituicao = "Univ. Federal do Amazonas (UFAM) - Campus 2"
        self.client.post(NOVO, dados(instituicao=instituicao))
        self.assertEqual(MembrosExternos.objects.get().mem_instituicao, instituicao)

    def test_cenario_12_instituicao_com_151_caracteres(self):
        resposta = self.client.post(NOVO, dados(instituicao="U" * 151))
        self.assertContains(resposta, mensagens.INSTITUICAO_INVALIDA)

    def test_cenario_13_titulacao_fora_da_lista(self):
        resposta = self.client.post(NOVO, dados(titulacao="Livre-docente"))
        self.assertContains(resposta, mensagens.OPCAO_INVALIDA)

    def test_cenario_14_atalho_da_banca_volta_com_o_membro(self):
        voltar = reverse("cadastro:painel") + "?aba=banca"
        resposta = self.client.post(f"{NOVO}?voltar={voltar}", dados(voltar=voltar))
        conta = Usuarios.objects.get(usu_email="ana@ufam.edu.br")
        self.assertRedirects(resposta, f"{voltar}&membro={conta.pk}", fetch_redirect_response=False)

    def test_cenario_15_cancelar_pelo_atalho_volta_sem_criar(self):
        voltar = reverse("cadastro:painel")
        resposta = self.client.get(NOVO, {"voltar": voltar})
        self.assertContains(resposta, f'href="{voltar}">Cancelar')
        self.assertEqual(MembrosExternos.objects.count(), 0)

    def test_atalho_com_destino_externo_e_ignorado(self):
        destinos = ("https://evil.example/", "//evil.example/", "/nao-existe/")
        for indice, voltar in enumerate(destinos):
            with self.subTest(voltar=voltar):
                email = f"atalho{indice}@ufam.edu.br"
                resposta = self.client.post(NOVO, dados(email=email, voltar=voltar))
                self.assertRedirects(resposta, LISTA, fetch_redirect_response=False)

    def test_cenario_20_validade_de_30_dias_sem_banca(self):
        with mock.patch("django.utils.timezone.now", return_value=datetime(2026, 10, 1, 10, 0)):
            self.client.post(NOVO, dados())
        self.assertEqual(MembrosExternos.objects.get().mem_validade_ate, date(2026, 10, 31))

    def test_cenario_21_aluno_nao_acessa(self):
        aluno = criar_aluno_com_turma(email="al@uea.edu.br", status=StatusConta.ATIVA).alu
        self.client.force_login(aluno)
        resposta = self.client.get(LISTA)
        self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)

    def test_cenario_22_docente_sem_papel_nao_ve_o_menu(self):
        docente = docente_de(EC)
        self.client.force_login(docente)
        resposta = self.client.get(reverse("cadastro:painel"))
        self.assertNotContains(resposta, LISTA)
        self.assertEqual(self.client.get(LISTA).status_code, 403)

    def test_cenario_23_falha_ao_gravar(self):
        with (
            mock.patch(
                "sigtcc.apps.cadastro.services_contas.MembrosExternos.objects.create",
                side_effect=DatabaseError,
            ),
            self.assertLogs("sigtcc.contas", "ERROR"),
        ):
            resposta = self.client.post(NOVO, dados())
        self.assertContains(resposta, mensagens.FALHA_AO_SALVAR)
        self.assertContains(resposta, 'value="ana@ufam.edu.br"')
        self.assertFalse(Usuarios.objects.filter(usu_email="ana@ufam.edu.br").exists())

    def test_q10_professor_so_com_turma_arquivada_ve_mas_nao_cadastra(self):
        professor = docente_de(EC)
        turma_do_docente(professor, status=StatusTurma.ARQUIVADA)
        self.client.force_login(professor)
        resposta = self.client.get(LISTA)
        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(resposta, mensagens.NOVO_MEMBRO_EXTERNO)
        self.assertEqual(self.client.get(NOVO).status_code, 403)

    def test_q19_lista_sem_filtro_de_curso(self):
        membro(email="x@empresa.com")
        resposta = self.client.get(LISTA)
        self.assertContains(resposta, "x@empresa.com")
        self.assertNotContains(resposta, 'name="curso"')

    def test_id_de_outro_tipo_de_conta_da_404(self):
        self.assertEqual(self.client.get(editar(docente_de(EC))).status_code, 404)


class AlteracaoMembroTest(TesteContas):
    """US-05 A2, A6 e cenários 16, 18 e 19. [FR-035]"""

    def _dados_de(self, conta, **campos):
        valores = {
            "nome": "Ana Souza",
            "email": conta.usu_email,
            "titulacao": conta.membrosexternos.mem_titulacao,
            "instituicao": conta.membrosexternos.mem_instituicao,
        }
        valores.update(campos)
        return valores

    def test_cenario_16_orientador_corrige_a_titulacao(self):
        conta = membro(titulacao="Mestre")
        self.client.force_login(orientador())
        resposta = self.client.post(
            editar(conta), self._dados_de(conta, titulacao="Doutor"), follow=True
        )
        self.assertContains(resposta, mensagens.DADOS_ATUALIZADOS)
        conta.membrosexternos.refresh_from_db()
        self.assertEqual(conta.membrosexternos.mem_titulacao, "Doutor")

    def test_cenario_18_alteracao_invalida_nao_grava(self):
        conta = membro(email="m@ufam.edu.br")
        membro(email="outro@ufam.edu.br")
        self.client.force_login(secretaria_de(SI))
        for campos, texto in (
            ({"email": "outro@ufam.edu.br"}, mensagens.EMAIL_JA_CADASTRADO),
            ({"nome": "Ana 2"}, mensagens.NOME_INVALIDO),
        ):
            with self.subTest(campos=campos):
                resposta = self.client.post(editar(conta), self._dados_de(conta, **campos))
                self.assertContains(resposta, texto)
        conta.refresh_from_db()
        self.assertEqual(conta.usu_email, "m@ufam.edu.br")
        self.assertNotEqual(conta.usu_nome, "Ana 2")

    def test_cenario_19_alterar_membro_expirado_nao_reabre_o_acesso(self):
        conta = membro(status=StatusConta.EXPIRADA, validade=date(2026, 1, 10))
        self.client.force_login(coordenador_de(SI))
        self.client.post(editar(conta), self._dados_de(conta, instituicao="UFPA"))
        conta.refresh_from_db()
        conta.membrosexternos.refresh_from_db()
        self.assertEqual(conta.membrosexternos.mem_instituicao, "UFPA")
        self.assertEqual(conta.usu_status, StatusConta.EXPIRADA)
        self.assertEqual(conta.membrosexternos.mem_validade_ate, date(2026, 1, 10))

    def test_lista_mostra_validade_e_status_vencido_como_expirada(self):
        membro(email="v@ufam.edu.br", status=StatusConta.ATIVA, validade=date(2020, 1, 31))
        self.client.force_login(secretaria_de(SI))
        resposta = self.client.get(LISTA)
        self.assertContains(resposta, "31/01/2020")
        self.assertContains(resposta, "Expirada")
