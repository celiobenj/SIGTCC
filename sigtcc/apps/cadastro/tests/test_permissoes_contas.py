"""Testes de permissão da Gestão de Contas: curso do usuário e do registro (T005) e recusa com
mensagem (T007). A matriz completa de rotas e perfis entra na T040 (SC-004).

[US-03][US-04][US-05][US-50][RBN-CAD-14.1][FR-009][FR-010][SC-004][Q5][Q26]
"""

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
