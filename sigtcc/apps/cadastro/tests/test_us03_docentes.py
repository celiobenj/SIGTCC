"""Testes de aceite da US-03 sobre docentes (cenários 1 a 17, 22 a 31, 33 a 36 e 39) e das
Clarifications Q5, Q8, Q26 e Q32 (tasks T014). O cenário 32 (troca de e-mail) fica em
test_troca_email_gestor.py.

[US-03][RBN-CAD-01.1][RBN-CAD-01.2][RBN-CAD-01.4][RBN-CAD-11.3][RBN-CAD-14.1][FR-001][FR-005]
[FR-006][FR-014][FR-015][FR-016][Q5][Q8][Q26][Q32]
"""

from unittest import mock

from django.core import mail
from django.db import DatabaseError
from django.urls import reverse

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import DescricaoTurma, StatusConta, StatusTCC
from sigtcc.apps.cadastro.models import Coordenadores, Docentes, Usuarios
from sigtcc.apps.cadastro.tests.apoio_acesso import SENHA, criar_aluno_com_turma
from sigtcc.apps.cadastro.tests.apoio_contas import (
    EC,
    LC,
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

NOVO = reverse("cadastro:contas_docente_novo")
LISTA = reverse("cadastro:contas_docentes")


def editar(docente):
    """Endereço da edição do docente (Usuarios)."""
    return reverse("cadastro:contas_docente_editar", args=[docente.pk])


def dados(curso_nome=SI, **campos):
    """POST válido do formulário de Docente, lotado no curso informado."""
    valores = {
        "nome": "Maria Luiza Souza",
        "email": "mlsg@uea.edu.br",
        "titulacao": "Doutor",
        "curso_lotacao": curso(curso_nome).pk,
    }
    valores.update(campos)
    return {chave: valor for chave, valor in valores.items() if valor is not None}


def dados_de(docente, **campos):
    """POST de alteração com os dados atuais do docente (Usuarios), com um nome válido (as
    fábricas criam nomes com número, que a US-03 E4 recusa)."""
    valores = {
        "nome": "Nome Do Docente",
        "email": docente.usu_email,
        "titulacao": docente.docentes.doc_titulacao,
        "curso_lotacao": docente.docentes.doc_cur_id,
    }
    valores.update(campos)
    return {chave: valor for chave, valor in valores.items() if valor is not None}


class CadastroDocenteTest(TesteContas):
    """US-03 fluxo principal, A1 a A3, E1 a E5 e E8 (cenários 1 a 17). [FR-012 a FR-015]"""

    def setUp(self):
        super().setUp()
        self.secretaria = secretaria_de(SI)
        self.client.force_login(self.secretaria)

    def test_cenario_01_secretaria_cadastra_docente_comum(self):
        resposta = self.client.post(NOVO, dados(), follow=True)
        self.assertContains(resposta, mensagens.DOCENTE_CADASTRADO)
        conta = Usuarios.objects.get(usu_email="mlsg@uea.edu.br")
        self.assertEqual(conta.usu_status, StatusConta.AGUARDANDO_ATIVACAO)
        self.assertIsNone(conta.password)
        self.assertFalse(Coordenadores.objects.filter(cor_doc_id=conta.pk).exists())
        self.assertEqual(mail.outbox, [])

    def test_cenario_02_coordenador_cadastra_docente_do_curso(self):
        self.client.force_login(coordenador_de(SI))
        self.client.post(NOVO, dados())
        conta = Usuarios.objects.get(usu_email="mlsg@uea.edu.br")
        self.assertEqual(conta.usu_status, StatusConta.AGUARDANDO_ATIVACAO)
        self.assertEqual(mail.outbox, [])

    def test_cenario_03_docente_com_papel_de_coordenador(self):
        self.client.post(NOVO, dados(coordenador="on", curso_coordenado=curso(SI).pk))
        conta = Usuarios.objects.get(usu_email="mlsg@uea.edu.br")
        self.assertEqual(Coordenadores.objects.get(cor_doc_id=conta.pk).cor_cur, curso(SI))

    def test_cenario_04_desmarcar_o_papel_descarta_o_curso_coordenado(self):
        self.client.post(NOVO, dados(curso_coordenado=curso(SI).pk))
        conta = Usuarios.objects.get(usu_email="mlsg@uea.edu.br")
        self.assertFalse(Coordenadores.objects.filter(cor_doc_id=conta.pk).exists())

    def test_cenario_05_email_de_outro_docente_ou_secretaria(self):
        docente_de(email="maria@uea.edu.br")
        resposta = self.client.post(NOVO, dados(email="maria@uea.edu.br"))
        self.assertContains(resposta, mensagens.EMAIL_JA_CADASTRADO)
        self.assertEqual(Usuarios.objects.filter(usu_email="maria@uea.edu.br").count(), 1)

    def test_cenario_05_sem_diferenciar_maiusculas(self):
        docente_de(email="maria@uea.edu.br")
        resposta = self.client.post(NOVO, dados(email="Maria@UEA.edu.br "))
        self.assertContains(resposta, mensagens.EMAIL_JA_CADASTRADO)

    def test_cenario_06_email_de_membro_externo_ou_aluno(self):
        membro(email="carlos@uea.edu.br")
        criar_aluno_com_turma(email="aluno@uea.edu.br")
        for email in ("carlos@uea.edu.br", "aluno@uea.edu.br"):
            with self.subTest(email=email):
                resposta = self.client.post(NOVO, dados(email=email))
                self.assertContains(resposta, mensagens.EMAIL_JA_CADASTRADO)

    def test_cenario_07_email_de_docente_inativo(self):
        docente_de(email="ana@uea.edu.br", status=StatusConta.INATIVA)
        resposta = self.client.post(NOVO, dados(email="ana@uea.edu.br"))
        self.assertContains(resposta, mensagens.EMAIL_JA_CADASTRADO)

    def test_cenarios_08_09_10_email_fora_do_formato_institucional(self):
        longo = "a" * (101 - len("@uea.edu.br")) + "@uea.edu.br"
        self.assertEqual(len(longo), 101)
        for email in ("maria@gmail.com", "maria.uea.edu.br", longo):
            with self.subTest(email=email):
                resposta = self.client.post(NOVO, dados(email=email))
                self.assertContains(resposta, mensagens.EMAIL_INSTITUCIONAL_CONTAS)
        self.assertEqual(Docentes.objects.count(), 0)

    def test_cenario_11_nome_com_numero(self):
        resposta = self.client.post(NOVO, dados(nome="Maria Souza 2"))
        self.assertContains(resposta, mensagens.NOME_INVALIDO)
        self.assertEqual(Docentes.objects.count(), 0)

    def test_cenario_12_nome_com_acentos_e_limite_de_150(self):
        self.client.post(NOVO, dados(nome="João Gonçalves Álvares"))
        self.assertTrue(Usuarios.objects.filter(usu_nome="João Gonçalves Álvares").exists())
        resposta = self.client.post(NOVO, dados(nome="A" * 151, email="outro@uea.edu.br"))
        self.assertContains(resposta, mensagens.NOME_INVALIDO)

    def test_cenario_13_titulacao_vazia(self):
        resposta = self.client.post(NOVO, dados(titulacao=""))
        self.assertContains(resposta, mensagens.M14_CAMPO_OBRIGATORIO)
        self.assertEqual(Docentes.objects.count(), 0)

    def test_cenario_14_papel_marcado_sem_curso_coordenado(self):
        resposta = self.client.post(NOVO, dados(coordenador="on"))
        self.assertContains(resposta, mensagens.M14_CAMPO_OBRIGATORIO)
        self.assertEqual(Docentes.objects.count(), 0)

    def test_cenario_15_curso_ja_tem_coordenador(self):
        coordenador_de(SI)
        resposta = self.client.post(NOVO, dados(coordenador="on", curso_coordenado=curso(SI).pk))
        self.assertContains(resposta, mensagens.CURSO_JA_TEM_COORDENADOR)
        self.assertFalse(Usuarios.objects.filter(usu_email="mlsg@uea.edu.br").exists())

    def test_cenario_16_titulacao_fora_da_lista(self):
        resposta = self.client.post(NOVO, dados(titulacao="Livre-docente"))
        self.assertContains(resposta, mensagens.OPCAO_INVALIDA)

    def test_cenario_17_curso_de_lotacao_de_outro_curso(self):
        resposta = self.client.post(NOVO, dados(curso_nome=EC))
        self.assertContains(resposta, mensagens.SO_DO_SEU_CURSO_CADASTRO)
        self.assertEqual(Docentes.objects.count(), 0)

    def test_q5_curso_coordenado_pode_ser_qualquer_curso_sem_coordenador(self):
        self.client.post(NOVO, dados(coordenador="on", curso_coordenado=curso(LC).pk))
        conta = Usuarios.objects.get(usu_email="mlsg@uea.edu.br")
        self.assertEqual(Coordenadores.objects.get(cor_doc_id=conta.pk).cor_cur, curso(LC))

    def test_log_conta_criada_sem_email_completo(self):
        with self.assertLogs("sigtcc.acesso", "INFO") as log:
            self.client.post(NOVO, dados())
        self.assertTrue(any("CONTA_CRIADA" in linha for linha in log.output))
        self.assertFalse(any("mlsg@uea.edu.br" in linha for linha in log.output))


class AcessoAoCadastroTest(TesteContas):
    """US-03 E9 e cenários 22 e 23. [FR-007][FR-010]"""

    def test_cenario_22_perfis_sem_permissao(self):
        contas = {
            "aluno": criar_aluno_com_turma(email="a1@uea.edu.br", status=StatusConta.ATIVA).alu,
            "docente comum": docente_de(),
            "membro externo": membro(),
        }
        for nome, conta in contas.items():
            with self.subTest(perfil=nome):
                self.client.force_login(conta)
                resposta = self.client.get(NOVO)
                self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)

    def test_cenario_23_cancelar_volta_a_listagem_sem_criar(self):
        self.client.force_login(secretaria_de(SI))
        resposta = self.client.get(NOVO)
        self.assertContains(resposta, f'href="{LISTA}">Cancelar')
        self.assertEqual(Docentes.objects.count(), 0)


class ListagemTest(TesteContas):
    """US-03 A7 e cenários 24 a 27 (RBN-CAD-01.4, RBN-CAD-11.3, RBN-CAD-14.1). [FR-017][FR-018]"""

    def setUp(self):
        super().setUp()
        self.client.force_login(secretaria_de(SI))

    def test_cenario_24_lista_do_curso_com_as_colunas(self):
        docente = docente_de(SI, email="d1@uea.edu.br", titulacao="Mestre")
        docente_de(EC, email="d2@uea.edu.br")
        resposta = self.client.get(LISTA)
        for coluna in (
            "Nome",
            "E-mail",
            "Titulação",
            "Curso de Lotação",
            "Papéis",
            "Status da Conta",
            "Orientandos (TCC 1 / TCC 2)",
        ):
            self.assertContains(resposta, coluna)
        self.assertContains(resposta, docente.usu_nome)
        self.assertContains(resposta, "d1@uea.edu.br")
        self.assertNotContains(resposta, "d2@uea.edu.br")

    def test_cenario_25_filtro_todos(self):
        for nome, email in ((EC, "e@uea.edu.br"), (SI, "s@uea.edu.br"), (LC, "l@uea.edu.br")):
            docente_de(nome, email=email)
        resposta = self.client.get(LISTA, {"curso": "todos"})
        for email in ("e@uea.edu.br", "s@uea.edu.br", "l@uea.edu.br"):
            self.assertContains(resposta, email)

    def test_cenario_26_curso_sem_docentes(self):
        resposta = self.client.get(LISTA, {"curso": curso(LC).pk})
        self.assertContains(resposta, mensagens.NENHUM_REGISTRO)

    def test_filtro_invalido_volta_ao_curso_do_usuario(self):
        docente_de(SI, email="s@uea.edu.br")
        resposta = self.client.get(LISTA, {"curso": "abc"})
        self.assertContains(resposta, "s@uea.edu.br")

    def test_cenario_27_conta_aguardando_ativacao_e_zero_orientandos(self):
        self.client.post(NOVO, dados())
        resposta = self.client.get(LISTA)
        self.assertContains(resposta, "Aguardando Ativação")
        self.assertContains(resposta, "0 / 0")
        self.client.logout()
        resposta = self.client.post(
            reverse("cadastro:entrar"), {"credencial": "mlsg@uea.edu.br", "senha": SENHA}
        )
        self.assertContains(resposta, mensagens.CONTA_NAO_ATIVADA)
        self.assertContains(resposta, mensagens.PRIMEIRO_ACESSO)

    def test_q8_orientandos_por_tcc1_e_tcc2_com_alerta_acima_de_5(self):
        orientador = docente_de(SI, email="o@uea.edu.br")
        professor = docente_de(SI, email="p@uea.edu.br")
        turma1 = turma_do_docente(professor, descricao=DescricaoTurma.TCC_1)
        turma2 = turma_do_docente(professor, descricao=DescricaoTurma.TCC_2)
        for turma, quantidade in ((turma1, 4), (turma2, 2)):
            for _ in range(quantidade):
                aluno = matricular_aluno(turma, status_tcc=StatusTCC.EM_ANDAMENTO)
                orientacao_ativa(orientador, tcc_de(aluno, turma))
        resposta = self.client.get(LISTA)
        self.assertContains(resposta, "4 / 2")
        self.assertContains(resposta, "Mais de 5 orientandos")


class AlteracaoDocenteTest(TesteContas):
    """US-03 A8 a A11 e cenários 28 a 31, 33 a 36 e 39. [FR-006][FR-014][FR-016]"""

    def setUp(self):
        super().setUp()
        self.coordenador = coordenador_de(SI)
        self.client.force_login(self.coordenador)

    def test_cenario_28_falha_ao_gravar_mantem_os_dados(self):
        with (
            mock.patch(
                "sigtcc.apps.cadastro.services_contas.Docentes.objects.create",
                side_effect=DatabaseError,
            ),
            self.assertLogs("sigtcc.contas", "ERROR") as log,
        ):
            resposta = self.client.post(NOVO, dados())
        self.assertIn("DatabaseError", log.output[0])
        self.assertContains(resposta, mensagens.FALHA_AO_SALVAR)
        self.assertContains(resposta, 'value="mlsg@uea.edu.br"')
        self.assertFalse(Usuarios.objects.filter(usu_email="mlsg@uea.edu.br").exists())

    def test_cenario_29_alterar_titulacao(self):
        docente = docente_de(SI, titulacao="Mestre")
        resposta = self.client.post(
            editar(docente), dados_de(docente, titulacao="Doutor"), follow=True
        )
        self.assertContains(resposta, mensagens.DADOS_ATUALIZADOS)
        docente.docentes.refresh_from_db()
        self.assertEqual(docente.docentes.doc_titulacao, "Doutor")

    def test_cenario_30_email_de_outro_usuario(self):
        docente = docente_de(SI, email="joao@uea.edu.br")
        docente_de(EC, email="outro@uea.edu.br")
        resposta = self.client.post(editar(docente), dados_de(docente, email="outro@uea.edu.br"))
        self.assertContains(resposta, mensagens.EMAIL_JA_CADASTRADO)
        docente.refresh_from_db()
        self.assertEqual(docente.usu_email, "joao@uea.edu.br")

    def test_cenario_31_nome_ou_email_invalidos(self):
        docente = docente_de(SI)
        for campos, texto in (
            ({"nome": "João 2"}, mensagens.NOME_INVALIDO),
            ({"email": "joao@gmail.com"}, mensagens.EMAIL_INSTITUCIONAL_CONTAS),
        ):
            with self.subTest(campos=campos):
                resposta = self.client.post(editar(docente), dados_de(docente, **campos))
                self.assertContains(resposta, texto)
        docente.refresh_from_db()
        self.assertNotEqual(docente.usu_nome, "João 2")

    def test_cenario_33_papel_para_curso_sem_coordenador(self):
        docente = docente_de(SI)
        self.client.post(
            editar(docente), dados_de(docente, coordenador="on", curso_coordenado=curso(LC).pk)
        )
        self.assertEqual(Coordenadores.objects.get(cor_doc_id=docente.pk).cor_cur, curso(LC))

    def test_cenario_34_curso_ja_tem_coordenador(self):
        docente = docente_de(SI)
        resposta = self.client.post(
            editar(docente), dados_de(docente, coordenador="on", curso_coordenado=curso(SI).pk)
        )
        self.assertContains(resposta, mensagens.CURSO_JA_TEM_COORDENADOR)
        self.assertFalse(Coordenadores.objects.filter(cor_doc_id=docente.pk).exists())

    def test_cenario_35_desmarcar_o_papel_libera_o_curso(self):
        outro = coordenador_de(LC, lotado_em=SI)
        self.client.post(editar(outro), dados_de(outro))
        self.assertFalse(Coordenadores.objects.filter(cor_doc_id=outro.pk).exists())
        docente = docente_de(SI)
        self.client.post(
            editar(docente), dados_de(docente, coordenador="on", curso_coordenado=curso(LC).pk)
        )
        self.assertEqual(Coordenadores.objects.get(cor_cur=curso(LC)).cor_doc_id, docente.pk)

    def test_cenario_36_troca_do_curso_de_lotacao(self):
        self.client.force_login(secretaria_de(SI))
        docente = docente_de(SI, email="move@uea.edu.br")
        self.client.post(editar(docente), dados_de(docente, curso_lotacao=curso(EC).pk))
        docente.docentes.refresh_from_db()
        self.assertEqual(docente.docentes.doc_cur, curso(EC))
        resposta = self.client.get(LISTA, {"curso": curso(EC).pk})
        self.assertContains(resposta, "move@uea.edu.br")

    def test_cenario_39_docente_de_outro_curso(self):
        docente = docente_de(EC)
        resposta = self.client.get(LISTA, {"curso": curso(EC).pk})
        self.assertNotContains(resposta, editar(docente))
        resposta = self.client.get(editar(docente))
        self.assertContains(resposta, mensagens.SO_DO_SEU_CURSO_CADASTRO, status_code=403)
        resposta = self.client.post(editar(docente), dados_de(docente, nome="Outro Nome"))
        self.assertEqual(resposta.status_code, 403)
        docente.refresh_from_db()
        self.assertNotEqual(docente.usu_nome, "Outro Nome")

    def test_q26_coordenador_de_outro_curso_nao_edita_o_proprio_cadastro(self):
        coordenador = coordenador_de(LC, lotado_em=EC)
        self.client.force_login(coordenador)
        resposta = self.client.get(editar(coordenador))
        self.assertContains(resposta, mensagens.SO_DO_SEU_CURSO_CADASTRO, status_code=403)
        self.client.force_login(secretaria_de(EC))
        self.assertEqual(self.client.get(editar(coordenador)).status_code, 200)

    def test_q32_papel_para_docente_inativo_e_recusado(self):
        docente = docente_de(SI, status=StatusConta.INATIVA)
        resposta = self.client.post(
            editar(docente), dados_de(docente, coordenador="on", curso_coordenado=curso(LC).pk)
        )
        self.assertContains(resposta, mensagens.MC10_STATUS_INCOMPATIVEL)
        self.assertFalse(Coordenadores.objects.filter(cor_doc_id=docente.pk).exists())

    def test_m11_desmarcar_o_proprio_papel_leva_ao_painel(self):
        resposta = self.client.post(editar(self.coordenador), dados_de(self.coordenador))
        self.assertRedirects(resposta, reverse("cadastro:painel"), fetch_redirect_response=False)
        self.assertEqual(self.client.get(LISTA).status_code, 403)

    def test_c20_alteracao_nao_desfaz_status_gravado_por_outra_acao(self):
        docente = docente_de(SI)
        formulario = dados_de(docente, nome="Nome Novo")
        Usuarios.objects.filter(pk=docente.pk).update(usu_status=StatusConta.INATIVA)
        self.client.post(editar(docente), formulario)
        docente.refresh_from_db()
        self.assertEqual(docente.usu_nome, "Nome Novo")
        self.assertEqual(docente.usu_status, StatusConta.INATIVA)
