"""Serviço notificar() e curso_do_codigo (spec 004, research B6 e B21).

[US-08][US-09][RBN-CAD-05.7][RBN-CAD-13.2][B-1][I-5]
"""

from datetime import timedelta

from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services
from sigtcc.apps.cadastro.models import Alunos, Notificacoes
from sigtcc.apps.cadastro.tests.apoio_acesso import TesteAcesso, criar_docente_ativo
from sigtcc.apps.cadastro.tests.fabricas import criar_aluno


class NotificarTest(TesteAcesso):
    """notificar(): corte em 500, link só interno, data e hora. [B21]"""

    def setUp(self):
        super().setUp()
        self.usuario = criar_docente_ativo()

    def test_mensagem_ate_500_fica_inteira(self):
        """Mensagem de 500 caracteres não é cortada."""
        notificacao = services.notificar(self.usuario, "a" * 500)
        self.assertEqual(notificacao.not_mensagem, "a" * 500)

    def test_mensagem_longa_cortada_com_reticencias(self):
        """Acima de 500, corta e termina com "…"."""
        notificacao = services.notificar(self.usuario, "b" * 700)
        self.assertEqual(len(notificacao.not_mensagem), 500)
        self.assertTrue(notificacao.not_mensagem.endswith("…"))

    def test_corta_primeiro_o_campo_longo(self):
        """B-1: a justificativa é cortada e o resto da frase da MT-21 fica inteiro."""
        texto = services.montar_mensagem_cortada(
            mensagens.MT21_NOTIFICACAO_EXCLUSAO,
            "justificativa",
            identificador="X" * 30,
            justificativa="j" * 500,
        )
        self.assertEqual(len(texto), 500)
        self.assertTrue(texto.startswith(f"Você foi excluído da turma {'X' * 30}. Motivo: jjj"))
        self.assertTrue(texto.endswith("…"))

    def test_link_interno_aceito_e_externo_descartado(self):
        """Só caminho interno válido vira not_link_tela."""
        interno = services.notificar(self.usuario, "ok", link="/painel/")
        externo = services.notificar(self.usuario, "ok", link="https://outro.site/")
        self.assertEqual(interno.not_link_tela, "/painel/")
        self.assertIsNone(externo.not_link_tela)

    def test_data_hora_e_nao_lida(self):
        """A notificação nasce não lida e com data e hora."""
        notificacao = services.notificar(self.usuario, "ok")
        self.assertFalse(Notificacoes.objects.get(pk=notificacao.pk).not_lida)
        self.assertIsNotNone(notificacao.not_data_hora)


class CursoDoCodigoTest(TesteAcesso):
    """curso_do_codigo e curso_do_aluno (delegação). [RBN-CAD-05.7][B6]"""

    def test_codigo_reconhecido(self):
        self.assertEqual(services.curso_do_codigo("EST08MCPD").cur_nome, "Engenharia de Computação")

    def test_codigo_nao_reconhecido_ou_vazio(self):
        self.assertIsNone(services.curso_do_codigo("EST99XXXX"))
        self.assertIsNone(services.curso_do_codigo(""))

    def test_curso_do_aluno_continua_igual(self):
        """A função da spec 003 dá o nome ou "Código não reconhecido"."""
        aluno = criar_aluno()
        self.assertEqual(services.curso_do_aluno(aluno), "Engenharia de Computação")
        Alunos.objects.filter(pk=aluno.pk).update(alu_codigo_curso="EST99XXXX")
        aluno.refresh_from_db()
        self.assertEqual(services.curso_do_aluno(aluno), mensagens.CURSO_NAO_RECONHECIDO)


class NotificarComInstanteTest(TesteAcesso):
    """Spec 006 (IC-12; FR-050): notificar(..., agora=X) grava exatamente X, para a MO-26 servir
    à dedução do motivo TURMA_ARQUIVADA. [US-38][RBN-CAD-13.2][FR-050][FR-053][IC-12]
    """

    def test_agora_informado_vai_para_not_data_hora(self):
        usuario = criar_docente_ativo()
        instante = timezone.now() - timedelta(minutes=3)
        aviso = services.notificar(usuario, "Aviso", agora=instante)
        aviso.refresh_from_db()
        self.assertEqual(aviso.not_data_hora, instante)
