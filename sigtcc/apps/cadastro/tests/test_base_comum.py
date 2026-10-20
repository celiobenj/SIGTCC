"""Testes da base comum para as demais features (spec 003, história 6).

[FR-024][FR-025][FR-026][Q27][RBN-CAD-04.5][SC-004][SC-007]
"""

from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.core import mail
from django.test import RequestFactory, override_settings
from django.urls import reverse

from sigtcc.apps.cadastro import contexto, mensagens, services
from sigtcc.apps.cadastro.backends import SigtccBackend
from sigtcc.apps.cadastro.choices import StatusConta, StatusTurma
from sigtcc.apps.cadastro.models import Usuarios
from sigtcc.apps.cadastro.permissoes import (
    papeis,
    pode_resetar_primeiro_acesso,
    professor_com_turma_ativa,
    tem_perfil,
    tipo_conta,
)
from sigtcc.apps.cadastro.tests.apoio_acesso import (
    SENHA,
    TesteAcesso,
    caminho_do_link,
    criar_aluno_com_turma,
    criar_coordenador,
    criar_docente_ativo,
    criar_membro_externo,
    criar_notificacao,
    criar_secretaria,
)
from sigtcc.apps.cadastro.tests.fabricas import criar_turma
from sigtcc.apps.cadastro.tests.urls_teste import DADO_DA_PAGINA


@override_settings(ROOT_URLCONF="sigtcc.apps.cadastro.tests.urls_teste")
class BaseComumTest(TesteAcesso):
    """Cenários da história 6. [FR-024][FR-025][FR-026]"""

    def professor(self, email="prof@uea.edu.br", status_turma=StatusTurma.ATIVA):
        """Docente que é Professor da Disciplina de uma turma."""
        docente = criar_docente_ativo(email=email)
        turma = criar_turma(tur_doc=docente.docentes, tur_status=status_turma)
        return docente, turma

    def assertNegado(self, resposta):
        """403 com a M-02 e sem nenhum dado da página."""
        self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)
        self.assertNotContains(resposta, DADO_DA_PAGINA, status_code=403)

    def test_cenario1_sem_login_vai_ao_login_e_volta(self):
        """Dado visitante, quando abre página interna, então login e depois volta à página."""
        resposta = self.client.get("/exemplo/professor/")
        self.assertRedirects(resposta, "/entrar/?next=/exemplo/professor/")
        self.professor()
        resposta = self.client.post(
            "/entrar/",
            {"credencial": "prof@uea.edu.br", "senha": SENHA, "next": "/exemplo/professor/"},
            follow=True,
        )
        self.assertEqual(resposta.redirect_chain[-1][0], "/exemplo/professor/")
        self.assertContains(resposta, DADO_DA_PAGINA)

    def test_cenario2_aluno_negado_pelo_endereco_direto(self):
        """Dado página do Professor, quando um Aluno a abre, então M-02 e nenhum dado."""
        aluno = criar_aluno_com_turma(status=StatusConta.ATIVA, senha=SENHA)
        self.client.force_login(aluno.alu)
        self.assertNegado(self.client.get("/exemplo/professor/"))

    def test_cenario3_coordenador_permitido_e_docente_negado(self):
        """Dado página do Coordenador, então o coordenador entra e o outro docente não."""
        self.client.force_login(criar_coordenador())
        self.assertContains(self.client.get("/exemplo/coordenador/"), DADO_DA_PAGINA)
        self.client.force_login(criar_docente_ativo())
        self.assertNegado(self.client.get("/exemplo/coordenador/"))

    def test_cenario4_layout(self):
        """Dado usuário logado, então a página tem barra superior, sino, menu e o visual.

        Parte disponível nesta fase; "Meu perfil" e o link do sino são conferidos em
        test_us38_perfil_notificacoes (fase 8, tasks H1).
        """
        docente = criar_docente_ativo()
        criar_notificacao(docente)
        criar_notificacao(docente)
        criar_notificacao(docente, lida=True)
        self.client.force_login(docente)
        resposta = self.client.get(reverse("cadastro:painel"))
        self.assertContains(resposta, 'class="topbar"')
        self.assertContains(resposta, '<span class="nome">SIGTCC</span>', html=False)
        self.assertContains(resposta, '<span class="badge" data-contador>2</span>', html=False)
        self.assertContains(resposta, ">Sair</button>")
        self.assertContains(resposta, 'id="menu-lateral"')
        self.assertContains(resposta, "Início")
        self.assertContains(resposta, "css/sigtcc.css")
        self.assertContains(resposta, "family=Figtree")
        self.assertContains(resposta, "Material+Symbols+Outlined")

    def test_cenario5_link_gerado_fora_das_telas(self):
        """Dado conta aguardando, quando o link é gerado por código, então a tela o aceita."""
        docente = criar_docente_ativo(senha=None, status=StatusConta.AGUARDANDO_ATIVACAO)
        anterior = services.gerar_link_ativacao(docente)
        link = services.gerar_link_ativacao(docente)
        self.assertTrue(link.startswith("http://testserver/primeiro-acesso/ativar/"))
        resposta = self.client.get(anterior.removeprefix("http://testserver"), follow=True)
        self.assertContains(resposta, mensagens.LINK_SUBSTITUIDO)
        resposta = self.client.get(link.removeprefix("http://testserver"), follow=True)
        self.assertContains(resposta, 'name="senha"')
        self.assertEqual(len(mail.outbox), 0)

    def test_enviar_link_ativacao_fora_das_telas(self):
        """Contrato §4: enviar_link_ativacao gera, grava e envia; o link do e-mail funciona."""
        docente = criar_docente_ativo(
            email="prof@uea.edu.br", senha=None, status=StatusConta.AGUARDANDO_ATIVACAO
        )
        self.assertTrue(services.enviar_link_ativacao(docente))
        resposta = self.client.get(caminho_do_link(mail.outbox[0]), follow=True)
        self.assertContains(resposta, 'name="senha"')

    def test_q27_professor_so_de_turma_arquivada(self):
        """Q27: turma arquivada dá o papel, mas não permite ações que alteram dados."""
        docente, turma = self.professor(status_turma=StatusTurma.ARQUIVADA)
        aluno = criar_aluno_com_turma(turma=turma)
        self.assertIn("professor_disciplina", papeis(docente))
        self.assertFalse(professor_com_turma_ativa(docente))
        self.assertFalse(pode_resetar_primeiro_acesso(docente, aluno))
        self.client.force_login(docente)
        self.assertContains(self.client.get("/exemplo/professor/"), DADO_DA_PAGINA)

    def test_q27_professor_de_turma_ativa(self):
        """Q27: com turma ativa do aluno, a ação é permitida; com aluno de outra turma, não."""
        docente, turma = self.professor()
        aluno = criar_aluno_com_turma(turma=turma)
        outro = criar_aluno_com_turma()
        self.assertTrue(professor_com_turma_ativa(docente))
        self.assertTrue(pode_resetar_primeiro_acesso(docente, aluno))
        self.assertFalse(pode_resetar_primeiro_acesso(docente, outro))

    def test_tipos_de_conta(self):
        """FR-025: tipo de conta de cada especialização; conta sem tipo vale None."""
        aluno = criar_aluno_com_turma()
        self.assertEqual(tipo_conta(aluno.alu), "aluno")
        self.assertEqual(tipo_conta(criar_docente_ativo()), "docente")
        self.assertEqual(tipo_conta(criar_secretaria()), "secretaria")
        self.assertEqual(tipo_conta(criar_membro_externo()), "membro_externo")
        self.assertIsNone(tipo_conta(Usuarios.objects.create_user("x@uea.edu.br", "Sem tipo")))
        self.assertIsNone(tipo_conta(AnonymousUser()))
        self.assertFalse(tem_perfil(AnonymousUser()))

    def test_papeis_calculados_uma_vez(self):
        """A7: os papéis saem numa consulta e ficam guardados no objeto do usuário."""
        docente = criar_coordenador()
        # Carregado como o backend carrega o usuário da sessão (A1).
        docente = SigtccBackend().get_user(docente.pk)
        with self.assertNumQueries(1):
            self.assertEqual(papeis(docente), frozenset({"coordenador"}))
        with self.assertNumQueries(0):
            papeis(docente)

    def test_contexto_anonimo_sem_consulta(self):
        """A8: para visitante anônimo, os processadores não consultam o banco."""
        requisicao = RequestFactory().get("/")
        requisicao.user = AnonymousUser()
        with self.assertNumQueries(0):
            self.assertEqual(contexto.menu(requisicao), {})
            self.assertEqual(contexto.notificacoes_nao_lidas(requisicao), {})

    def test_menu_filtra_por_perfil(self):
        """FR-025: o menu mostra só os itens permitidos; seção agrupa os itens."""
        itens = [
            {
                "rotulo": "Início",
                "icone": "home",
                "rota": "cadastro:painel",
                "perfis": ("aluno", "docente"),
                "ordem": 0,
            },
            {
                "rotulo": "Coordenação",
                "icone": "tune",
                "rota": "cadastro:painel",
                "perfis": ("coordenador",),
                "ordem": 1,
                "secao": "Gestão",
            },
            {
                "rotulo": "Inexistente",
                "icone": "x",
                "rota": "outra:rota",
                "perfis": ("docente",),
                "ordem": 2,
            },
        ]
        with mock.patch.object(contexto, "_itens_de_todos_os_apps", return_value=itens):
            self.client.force_login(criar_coordenador())
            resposta = self.client.get(reverse("cadastro:painel"))
            self.assertContains(resposta, "Coordenação")
            self.assertContains(resposta, '<div class="dr-sec">Gestão</div>', html=False)
            self.assertNotContains(resposta, "Inexistente")
            aluno = criar_aluno_com_turma(status=StatusConta.ATIVA, senha=SENHA)
            self.client.force_login(aluno.alu)
            resposta = self.client.get(reverse("cadastro:painel"))
            self.assertContains(resposta, "Início")
            self.assertNotContains(resposta, "Coordenação")

    def test_permission_denied_em_servico_usa_handler403(self):
        """Contrato §2: PermissionDenied em qualquer view ou serviço mostra a M-02."""
        self.client.force_login(criar_docente_ativo())
        self.assertNegado(self.client.get("/exemplo/servico/"))

    def test_mixin_de_view_de_classe(self):
        """PerfilRequeridoMixin: login, permissão e negação, como o decorador."""
        self.assertRedirects(
            self.client.get("/exemplo/secretaria/"), "/entrar/?next=/exemplo/secretaria/"
        )
        self.client.force_login(criar_secretaria())
        self.assertContains(self.client.get("/exemplo/secretaria/"), DADO_DA_PAGINA)
        self.client.force_login(criar_docente_ativo())
        self.assertNegado(self.client.get("/exemplo/secretaria/"))

    def test_conta_inativada_perde_a_sessao(self):
        """A1: conta que deixa de estar 'Ativa' perde a sessão na próxima página."""
        docente = criar_docente_ativo()
        self.client.force_login(docente)
        Usuarios.objects.filter(pk=docente.pk).update(usu_status=StatusConta.INATIVA)
        self.assertRedirects(self.client.get(reverse("cadastro:painel")), "/entrar/?next=/painel/")
