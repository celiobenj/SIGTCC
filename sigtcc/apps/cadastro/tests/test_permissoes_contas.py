"""Testes de permissão da Gestão de Contas: curso do usuário e do registro (T005) e recusa com
mensagem (T007). A matriz completa de rotas e perfis entra na T040 (SC-004).

[US-03][US-04][US-05][US-50][RBN-CAD-14.1][FR-009][FR-010][SC-004][Q5][Q26]
"""

from django.urls import reverse

from sigtcc.apps.cadastro import permissoes
from sigtcc.apps.cadastro.tests.apoio_contas import (
    EC,
    LC,
    SI,
    TesteContas,
    coordenador_de,
    curso,
    docente_de,
    membro,
    secretaria_de,
)


class CursoDoUsuarioTest(TesteContas):
    """curso_do_usuario, curso_id_do_registro e pode_gerir (research C2). [FR-009][Q5][Q26]"""

    def test_coordenador_usa_o_curso_coordenado(self):
        coordenador = coordenador_de(LC, lotado_em=SI)
        self.assertEqual(permissoes.curso_do_usuario(coordenador), curso(LC))

    def test_registro_do_coordenador_pertence_ao_curso_de_lotacao(self):
        coordenador = coordenador_de(LC, lotado_em=SI)
        self.assertEqual(permissoes.curso_id_do_registro(coordenador.docentes), curso(SI).pk)

    def test_coordenador_de_outro_curso_nao_gere_o_proprio_cadastro(self):
        # Q26: lotado em SI, coordena LC; o registro dele é de SI.
        coordenador = coordenador_de(LC, lotado_em=SI)
        self.assertFalse(permissoes.pode_gerir(coordenador, coordenador.docentes))
        self.assertTrue(permissoes.pode_gerir(secretaria_de(SI), coordenador.docentes))
        self.assertTrue(permissoes.pode_gerir(coordenador_de(SI), coordenador.docentes))

    def test_coordenador_lotado_no_proprio_curso_gere_o_proprio_cadastro(self):
        coordenador = coordenador_de(EC)
        self.assertTrue(permissoes.pode_gerir(coordenador, coordenador.docentes))

    def test_secretaria_usa_o_curso_vinculado(self):
        secretaria = secretaria_de(SI)
        self.assertEqual(permissoes.curso_do_usuario(secretaria), curso(SI))
        self.assertTrue(permissoes.pode_gerir(secretaria, docente_de(SI).docentes))
        self.assertFalse(permissoes.pode_gerir(secretaria, docente_de(EC).docentes))
        self.assertTrue(permissoes.pode_gerir(coordenador_de(SI), secretaria.secretarios))

    def test_docente_comum_e_membro_nao_tem_curso(self):
        self.assertIsNone(permissoes.curso_do_usuario(docente_de(EC)))
        self.assertIsNone(permissoes.curso_do_usuario(membro()))
        self.assertFalse(permissoes.pode_gerir(docente_de(EC), docente_de(EC).docentes))

    def test_registro_de_outro_tipo_e_recusado(self):
        with self.assertRaises(TypeError):
            permissoes.curso_id_do_registro(membro().membrosexternos)


class RecusaComMensagemTest(TesteContas):
    """403 com M-02 (handler403) e 403 com a mensagem do FR-009 (research C21). [FR-009][FR-010]"""

    def test_recusa_fora_do_curso_mostra_a_mensagem_com_403(self):
        from django.contrib.messages.storage.fallback import FallbackStorage
        from django.test import RequestFactory

        from sigtcc.apps.cadastro import mensagens
        from sigtcc.apps.cadastro.services_contas import ForaDoCurso
        from sigtcc.apps.cadastro.views_contas import recusa_fora_do_curso

        request = RequestFactory().get("/cadastros/docentes/1/editar/")
        request.user = secretaria_de(SI)
        request.session = self.client.session
        request._messages = FallbackStorage(request)
        resposta = recusa_fora_do_curso(request, ForaDoCurso(mensagens.SO_DO_SEU_CURSO_CADASTRO))
        self.assertEqual(resposta.status_code, 403)
        self.assertIn(mensagens.SO_DO_SEU_CURSO_CADASTRO, resposta.content.decode())

    def test_handler403_continua_com_a_m02(self):
        from sigtcc.apps.cadastro import mensagens

        self.client.force_login(membro())
        resposta = self.client.get("/turmas/")
        self.assertEqual(resposta.status_code, 403)
        self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)


class MatrizDePermissoesTest(TesteContas):
    """SC-004: cada rota da Gestão de Contas para cada perfil, inclusive pelo endereço direto,
    sem nenhum dado do registro na resposta 403 (tasks T040; contracts/rotas.md).
    [US-03][US-04][US-05][US-50][SC-004][FR-009][FR-010][research C21][C22]
    """

    def setUp(self):
        super().setUp()
        from sigtcc.apps.cadastro.choices import StatusConta, StatusTCC, StatusTurma
        from sigtcc.apps.cadastro.tests.apoio_acesso import criar_aluno_com_turma
        from sigtcc.apps.cadastro.tests.apoio_contas import orientacao_ativa, turma_do_docente
        from sigtcc.apps.cadastro.tests.apoio_turmas import matricular_aluno, tcc_de

        professor = docente_de(EC)
        turma = turma_do_docente(professor)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        orientador = docente_de(EC)
        orientacao_ativa(orientador, tcc_de(aluno, turma))
        arquivado = docente_de(EC)
        turma_do_docente(arquivado, status=StatusTurma.ARQUIVADA)
        self.perfis = {
            "aluno": criar_aluno_com_turma(email="al@uea.edu.br", status=StatusConta.ATIVA).alu,
            "docente comum": docente_de(EC),
            "orientador": orientador,
            "professor arquivado": arquivado,
            "secretaria": secretaria_de(SI),
            "coordenador": coordenador_de(SI),
            "membro externo": membro(),
        }
        alvo_docente = docente_de(SI, email="alvo.docente@uea.edu.br")
        alvo_inativo = docente_de(SI, email="alvo.inativo@uea.edu.br", status=StatusConta.INATIVA)
        alvo_secretaria = secretaria_de(SI, email="alvo.sec@uea.edu.br")
        alvo_membro = membro(email="alvo.membro@ufam.edu.br")
        gestao = {"secretaria", "coordenador"}
        self.rotas = [
            ("contas_docentes", [], "get", gestao),
            ("contas_docente_novo", [], "get", gestao),
            ("contas_docente_editar", [alvo_docente.pk], "get", gestao),
            ("contas_docente_inativar", [alvo_docente.pk], "get", gestao),
            ("contas_docente_reativar", [alvo_inativo.pk], "get", gestao),
            ("contas_secretarias", [], "get", gestao),
            ("contas_secretaria_nova", [], "get", {"coordenador"}),
            ("contas_secretaria_editar", [alvo_secretaria.pk], "get", {"coordenador"}),
            ("contas_secretaria_inativar", [alvo_secretaria.pk], "get", {"coordenador"}),
            (
                "contas_membros",
                [],
                "get",
                {"orientador", "professor arquivado", "secretaria", "coordenador"},
            ),
            ("contas_membro_novo", [], "get", {"orientador", "secretaria", "coordenador"}),
            (
                "contas_membro_editar",
                [alvo_membro.pk],
                "get",
                {"orientador", "secretaria", "coordenador"},
            ),
            ("contas_membro_prorrogar", [alvo_membro.pk], "post", gestao),
        ]
        self.emails_dos_alvos = (
            "alvo.docente@uea.edu.br",
            "alvo.inativo@uea.edu.br",
            "alvo.sec@uea.edu.br",
            "alvo.membro@ufam.edu.br",
        )

    def test_cada_rota_para_cada_perfil(self):
        for nome, args, metodo, permitidos in self.rotas:
            url = reverse(f"cadastro:{nome}", args=args)
            for perfil, conta in self.perfis.items():
                with self.subTest(rota=nome, perfil=perfil):
                    self.client.force_login(conta)
                    resposta = getattr(self.client, metodo)(url)
                    if perfil in permitidos:
                        self.assertIn(resposta.status_code, (200, 302))
                    else:
                        self.assertEqual(resposta.status_code, 403)
                        texto = resposta.content.decode()
                        for email in self.emails_dos_alvos:
                            self.assertNotIn(email, texto)

    def test_visitante_vai_ao_login_com_next(self):
        self.client.logout()
        for nome, args, metodo, _ in self.rotas:
            with self.subTest(rota=nome):
                url = reverse(f"cadastro:{nome}", args=args)
                resposta = getattr(self.client, metodo)(url)
                self.assertEqual(resposta.status_code, 302)
                self.assertIn(reverse("cadastro:entrar"), resposta["Location"])

    def test_id_de_outro_tipo_de_conta_da_404(self):
        self.client.force_login(self.perfis["coordenador"])
        membro_id = membro().pk
        docente_id = docente_de(SI).pk
        for nome, alvo in (
            ("contas_docente_editar", membro_id),
            ("contas_docente_inativar", membro_id),
            ("contas_secretaria_editar", docente_id),
            ("contas_membro_editar", docente_id),
        ):
            with self.subTest(rota=nome):
                url = reverse(f"cadastro:{nome}", args=[alvo])
                self.assertEqual(self.client.get(url).status_code, 404)
