"""Testes de aceite da US-12: recuperar ou alterar a senha (spec 003, história 4).

Um teste por cenário (1 a 8 da US-12), mais os casos das Clarifications.

[US-12][RBN-CAD-06.5][RBN-CAD-06.7][RBN-CAD-06.8][FR-012]-[FR-015][Q9][Q19][Q26][Q27][Q29]
"""

from smtplib import SMTPException
from unittest import mock

from django.core import mail
from django.test import Client
from django.urls import reverse

from sigtcc.apps.cadastro import mensagens, services
from sigtcc.apps.cadastro.choices import StatusConta, StatusTurma
from sigtcc.apps.cadastro.models import Usuarios
from sigtcc.apps.cadastro.services import EstadoLink
from sigtcc.apps.cadastro.tests.apoio_acesso import (
    SENHA,
    TesteAcesso,
    avancar_relogio,
    caminho_do_link,
    criar_aluno_com_turma,
    criar_coordenador,
    criar_docente_ativo,
    criar_membro_externo,
)
from sigtcc.apps.cadastro.tests.fabricas import criar_turma

URL_SENHA = reverse("cadastro:alterar_senha")
URL_ESQUECI = reverse("cadastro:esqueci_senha")
URL_NOVA = reverse("cadastro:nova_senha")
NOVA = "NovaSenha99"


def url_aluno(aluno):
    """Tela mínima do aluno."""
    return reverse("cadastro:aluno", args=[aluno.pk])


def url_reset(aluno):
    """Confirmação e execução do reset."""
    return reverse("cadastro:resetar_primeiro_acesso", args=[aluno.pk])


class AlterarSenhaTest(TesteAcesso):
    """Alterar a senha em "Meu perfil" (cenários 1, 2 e 6; Q19). [US-12][RBN-CAD-06.5]"""

    def setUp(self):
        super().setUp()
        self.usuario = criar_docente_ativo(email="prof@uea.edu.br")
        self.client.force_login(self.usuario)

    def alterar(self, atual=SENHA, nova=NOVA, confirmacao=None):
        dados = {
            "senha_atual": atual,
            "nova_senha": nova,
            "confirmacao": confirmacao if confirmacao is not None else nova,
        }
        return self.client.post(URL_SENHA, dados, follow=True)

    def senha_confere(self, senha):
        return Usuarios.objects.get(pk=self.usuario.pk).check_password(senha)

    def test_cenario1_senha_alterada(self):
        """Dado usuário logado, quando informa a atual e uma nova válida, então grava."""
        resposta = self.alterar()
        self.assertContains(resposta, mensagens.SENHA_ALTERADA)
        self.assertTrue(self.senha_confere(NOVA))

    def test_cenario2_senha_atual_errada(self):
        """Dado o formulário, quando a senha atual está errada, então mantém a anterior."""
        resposta = self.alterar(atual="Errada123")
        self.assertContains(resposta, mensagens.SENHA_ATUAL_INCORRETA)
        self.assertTrue(self.senha_confere(SENHA))

    def test_cenario6_nova_senha_sem_letra(self):
        """Dado o formulário, quando a nova é "12345678", então a regra e mantém a anterior."""
        resposta = self.alterar(nova="12345678")
        self.assertContains(resposta, mensagens.REGRA_SENHA)
        self.assertTrue(self.senha_confere(SENHA))

    def test_confirmacao_diferente(self):
        """FR-012: confirmação diferente da nova senha."""
        resposta = self.alterar(confirmacao="Outra1234")
        self.assertContains(resposta, mensagens.SENHAS_NAO_CONFEREM)
        self.assertTrue(self.senha_confere(SENHA))

    def test_q19_troca_derruba_outras_sessoes(self):
        """Q19: as outras sessões caem; quem alterou continua logado."""
        outro = Client()
        outro.force_login(self.usuario)
        self.alterar()
        self.assertEqual(self.client.get(reverse("cadastro:painel")).status_code, 200)
        resposta = outro.get(reverse("cadastro:painel"))
        self.assertRedirects(resposta, "/entrar/?next=/painel/")

    def test_alterar_senha_exige_login(self):
        """Sem login, a tela pede login."""
        self.client.post(reverse("cadastro:sair"))
        self.assertRedirects(self.client.get(URL_SENHA), f"/entrar/?next={URL_SENHA}")


class RedefinirSenhaTest(TesteAcesso):
    """ "Esqueci minha senha" e o link de redefinição (cenários 3, 4 e 8; Q19, Q26).

    [US-12][RBN-CAD-06.7]
    """

    def esqueci(self, email):
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(URL_ESQUECI, {"email": email}, follow=True)

    def redefinir(self, senha=NOVA, confirmacao=None):
        dados = {"senha": senha, "confirmacao": confirmacao if confirmacao is not None else senha}
        return self.client.post(URL_NOVA, dados, follow=True)

    def test_cenario3_redefinicao_pelo_link(self):
        """Dado conta ativa, quando pede, abre o link e define a senha, então grava e o link cai."""
        usuario = criar_docente_ativo(email="prof@uea.edu.br")
        resposta = self.esqueci("prof@uea.edu.br")
        self.assertContains(resposta, mensagens.ESQUECI_GENERICA)
        self.assertEqual(mail.outbox[0].to, ["prof@uea.edu.br"])
        caminho = caminho_do_link(mail.outbox[0])
        self.client.get(caminho)
        resposta = self.redefinir()
        self.assertRedirects(resposta, reverse("cadastro:entrar"))
        self.assertTrue(Usuarios.objects.get(pk=usuario.pk).check_password(NOVA))
        resposta = self.client.get(caminho, follow=True)
        self.assertContains(resposta, mensagens.LINK_INVALIDO_OU_VENCIDO)

    def test_cenario4_link_vencido(self):
        """Dado link com mais de 24 h, quando é aberto, então "Link inválido ou vencido...".."""
        criar_docente_ativo(email="prof@uea.edu.br")
        self.esqueci("prof@uea.edu.br")
        with avancar_relogio(horas=24, minutos=1):
            resposta = self.client.get(caminho_do_link(mail.outbox[0]), follow=True)
        self.assertContains(resposta, mensagens.LINK_INVALIDO_OU_VENCIDO)
        self.assertNotContains(resposta, 'name="senha"')

    def test_cenario8_conta_aguardando_nao_recebe(self):
        """Dado conta 'Aguardando Ativação', quando pede, então mensagem genérica e sem link."""
        criar_docente_ativo(
            email="prof@uea.edu.br", senha=None, status=StatusConta.AGUARDANDO_ATIVACAO
        )
        resposta = self.esqueci("prof@uea.edu.br")
        self.assertContains(resposta, mensagens.ESQUECI_GENERICA)
        self.assertEqual(len(mail.outbox), 0)

    def test_esqueci_sempre_generica(self):
        """Q13: e-mail inexistente, conta inativa e falha no envio têm a mesma mensagem."""
        criar_docente_ativo(email="inativo@uea.edu.br", status=StatusConta.INATIVA)
        criar_docente_ativo(email="prof@uea.edu.br")
        for email in ("ninguem@uea.edu.br", "inativo@uea.edu.br"):
            self.assertContains(self.esqueci(email), mensagens.ESQUECI_GENERICA)
        self.assertEqual(len(mail.outbox), 0)
        with mock.patch(
            "sigtcc.apps.cadastro.services.send_mail", side_effect=SMTPException("fora")
        ):
            with self.assertLogs("sigtcc.acesso") as log:
                resposta = self.esqueci("prof@uea.edu.br")
        self.assertContains(resposta, mensagens.ESQUECI_GENERICA)
        self.assertIn("FALHA_ENVIO_EMAIL", log.output[0])

    def test_esqueci_formato_invalido(self):
        """M-10: e-mail fora do formato."""
        self.assertContains(self.esqueci("sem-arroba"), mensagens.M10_EMAIL_INVALIDO)
        self.assertContains(self.esqueci(""), mensagens.M14_CAMPO_OBRIGATORIO)

    def test_link_de_redefinicao_usado_e_substituido(self):
        """SC-006: link substituído por outro pedido, ou com a senha já trocada, não vale."""
        usuario = criar_docente_ativo(email="prof@uea.edu.br")
        self.esqueci("prof@uea.edu.br")
        primeiro = caminho_do_link(mail.outbox[0]).split("/")[-2]
        with avancar_relogio(minutos=1):
            self.esqueci("prof@uea.edu.br")
        self.assertEqual(services.validar_link_redefinicao(primeiro).estado, EstadoLink.SUBSTITUIDO)
        segundo = caminho_do_link(mail.outbox[1]).split("/")[-2]
        usuario.set_password("Trocada123")
        usuario.save()
        self.assertEqual(services.validar_link_redefinicao(segundo).estado, EstadoLink.SUBSTITUIDO)

    def test_q19_redefinicao_derruba_todas(self):
        """Q19: a redefinição encerra todas as sessões abertas da conta."""
        usuario = criar_docente_ativo(email="prof@uea.edu.br")
        logado = Client()
        logado.force_login(usuario)
        self.esqueci("prof@uea.edu.br")
        self.client.get(caminho_do_link(mail.outbox[0]))
        self.redefinir()
        self.assertRedirects(logado.get(reverse("cadastro:painel")), "/entrar/?next=/painel/")

    def test_q26_redefinicao_em_conta_inativa_ou_expirada(self):
        """Q26: conta que deixou de estar 'Ativa' não redefine; GET e POST mostram M-15/M-16."""
        casos = (
            (
                criar_docente_ativo(email="ina@uea.edu.br"),
                StatusConta.INATIVA,
                mensagens.M15_CONTA_INATIVA,
            ),
            (
                criar_membro_externo(email="exp@ufam.edu.br"),
                StatusConta.EXPIRADA,
                mensagens.M16_ACESSO_EXPIRADO,
            ),
        )
        for usuario, status, mensagem in casos:
            with self.subTest(status=status):
                self.esqueci(usuario.usu_email)
                caminho = caminho_do_link(mail.outbox[-1])
                self.client.get(caminho)
                self.assertContains(self.client.get(URL_NOVA), 'name="senha"')
                Usuarios.objects.filter(pk=usuario.pk).update(usu_status=status)
                # POST com o formulário já aberto (conferência no POST).
                self.assertContains(self.redefinir(), mensagem)
                # Link aberto de novo (conferência no GET).
                self.assertContains(self.client.get(caminho, follow=True), mensagem)
                self.assertTrue(Usuarios.objects.get(pk=usuario.pk).check_password(SENHA))
                Usuarios.objects.filter(pk=usuario.pk).update(usu_status=StatusConta.ATIVA)

    def test_q26_post_revalida(self):
        """Q26 e A17: conta inativada entre o GET e o POST não tem a senha redefinida."""
        usuario = criar_docente_ativo(email="prof@uea.edu.br")
        self.esqueci("prof@uea.edu.br")
        self.client.get(caminho_do_link(mail.outbox[0]))
        self.assertContains(self.client.get(URL_NOVA), 'name="senha"')
        Usuarios.objects.filter(pk=usuario.pk).update(usu_status=StatusConta.INATIVA)
        self.assertContains(self.redefinir(), mensagens.M15_CONTA_INATIVA)
        self.assertTrue(Usuarios.objects.get(pk=usuario.pk).check_password(SENHA))

    def test_token_sai_da_url_e_da_sessao(self):
        """A3: o token vai para a sessão, sai da URL e sai da sessão depois de usado."""
        criar_docente_ativo(email="prof@uea.edu.br")
        self.esqueci("prof@uea.edu.br")
        resposta = self.client.get(caminho_do_link(mail.outbox[0]))
        self.assertRedirects(resposta, URL_NOVA)
        self.assertIn("token_redefinicao", self.client.session)
        self.redefinir()
        self.assertNotIn("token_redefinicao", self.client.session)

    def test_nova_senha_sem_token(self):
        """A3: sem token na sessão, "Link inválido ou vencido. Solicite um novo"."""
        self.assertContains(self.client.get(URL_NOVA), mensagens.LINK_INVALIDO_OU_VENCIDO)

    def test_nova_senha_segue_a_regra(self):
        """FR-014: a nova senha segue a regra de FR-004."""
        criar_docente_ativo(email="prof@uea.edu.br")
        self.esqueci("prof@uea.edu.br")
        self.client.get(caminho_do_link(mail.outbox[0]))
        self.assertContains(self.redefinir("abcdefgh"), mensagens.REGRA_SENHA)
        self.assertContains(self.redefinir(NOVA, "Outra1234"), mensagens.SENHAS_NAO_CONFEREM)

    def test_link_de_outro_tipo(self):
        """Caso de borda: link de ativação não serve para redefinir, e vice-versa."""
        usuario = criar_docente_ativo(email="prof@uea.edu.br")
        ativacao = services.gerar_link_ativacao(usuario).split("/")[-2]
        self.assertEqual(services.validar_link_redefinicao(ativacao).estado, EstadoLink.ADULTERADO)
        redefinicao = services.gerar_link_redefinicao(usuario).split("/")[-2]
        self.assertEqual(services.validar_link_ativacao(redefinicao).estado, EstadoLink.ADULTERADO)

    def test_link_esqueci_senha_no_login(self):
        """O link "Esqueci minha senha" aparece na tela de login."""
        resposta = self.client.get(reverse("cadastro:entrar"))
        self.assertContains(resposta, f'<a href="{URL_ESQUECI}">Esqueci minha senha</a>')


class ResetPrimeiroAcessoTest(TesteAcesso):
    """Reset do primeiro acesso pelo Professor da Disciplina (cenários 5 e 7; Q9, Q27, Q29).

    [US-12][RBN-CAD-06.8][FR-015]
    """

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo(email="prof@uea.edu.br")
        self.turma = criar_turma(tur_doc=self.professor.docentes)
        self.aluno = criar_aluno_com_turma(
            matricula="2026000001",
            email="errado@uea.edu.br",
            status=StatusConta.ATIVA,
            senha=SENHA,
            turma=self.turma,
        )
        self.client.force_login(self.professor)

    def conta(self):
        return Usuarios.objects.get(pk=self.aluno.pk)

    def test_cenario5_reset_do_primeiro_acesso(self):
        """Dado e-mail errado, quando o Professor reseta e confirma, então a conta volta."""
        # Spec 006 (IC-08, IC-11): o endereço antigo leva ao painel do aluno, onde está o botão.
        resposta = self.client.get(url_aluno(self.aluno), follow=True)
        self.assertContains(resposta, mensagens.RESETAR_PRIMEIRO_ACESSO)
        self.assertContains(resposta, "2026000001")
        resposta = self.client.get(url_reset(self.aluno))
        nome = self.aluno.alu.usu_nome
        self.assertContains(resposta, mensagens.M12_CONFIRMAR_RESET.format(nome=nome))
        with self.assertLogs("sigtcc.acesso") as log:
            resposta = self.client.post(url_reset(self.aluno), follow=True)
        self.assertContains(resposta, mensagens.M13_RESET_CONCLUIDO)
        conta = self.conta()
        self.assertEqual(conta.usu_status, StatusConta.AGUARDANDO_ATIVACAO)
        self.assertIsNone(conta.usu_email)
        self.assertIsNone(conta.password)
        self.assertIn(
            f"RESET_PRIMEIRO_ACESSO | conta={conta.pk} | autor={self.professor.pk}", log.output[0]
        )
        anonimo = Client()
        resposta = anonimo.post(
            reverse("cadastro:primeiro_acesso_aluno"),
            {"matricula": "2026000001", "email": "certo@uea.edu.br"},
            follow=True,
        )
        self.assertContains(resposta, mensagens.LINK_ATIVACAO_ENVIADO)
        self.assertEqual(mail.outbox[-1].to, ["certo@uea.edu.br"])

    def test_cenario7_aluno_de_outra_turma(self):
        """Dado aluno de outra turma, quando o Professor abre o perfil, então sem o botão."""
        outro = criar_aluno_com_turma(status=StatusConta.ATIVA, senha=SENHA)
        # Spec 006 (IC-08, IC-11): sem turma em que seja o Professor, o endereço antigo nega o
        # acesso (M-02) e não há botão de reset.
        resposta = self.client.get(url_aluno(outro))
        self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)
        self.assertNotContains(resposta, mensagens.RESETAR_PRIMEIRO_ACESSO, status_code=403)
        self.assertEqual(self.client.post(url_reset(outro)).status_code, 403)

    def test_q9_professor_de_turma_arquivada_ve_tela_sem_botao(self):
        """Q9 e Q27: Professor só de turma arquivada vê a tela, sem o botão."""
        arquivado = criar_docente_ativo()
        turma = criar_turma(tur_doc=arquivado.docentes, tur_status=StatusTurma.ARQUIVADA)
        aluno = criar_aluno_com_turma(turma=turma)
        self.client.force_login(arquivado)
        # Spec 006 (IC-08, IC-11): o painel da turma arquivada abre só para consulta.
        resposta = self.client.get(url_aluno(aluno), follow=True)
        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(resposta, mensagens.RESETAR_PRIMEIRO_ACESSO)

    def test_q27_reset_recusado_sem_turma_ativa(self):
        """Q27: POST direto de quem não tem turma ativa do aluno é recusado (403)."""
        arquivado = criar_docente_ativo()
        turma = criar_turma(tur_doc=arquivado.docentes, tur_status=StatusTurma.ARQUIVADA)
        aluno = criar_aluno_com_turma(turma=turma, email="a@uea.edu.br")
        self.client.force_login(arquivado)
        self.assertEqual(self.client.get(url_reset(aluno)).status_code, 403)
        resposta = self.client.post(url_reset(aluno))
        self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)
        self.assertEqual(Usuarios.objects.get(pk=aluno.pk).usu_email, "a@uea.edu.br")

    def test_q29_reset_recusado_em_conta_inativa_ou_expirada(self):
        """Q29: conta 'Inativa' ou 'Expirada' não é resetada: sem botão e POST direto 403."""
        for status in (StatusConta.INATIVA, StatusConta.EXPIRADA):
            with self.subTest(status=status):
                Usuarios.objects.filter(pk=self.aluno.pk).update(usu_status=status)
                resposta = self.client.get(url_aluno(self.aluno), follow=True)
                self.assertNotContains(resposta, mensagens.RESETAR_PRIMEIRO_ACESSO)
                self.assertEqual(self.client.post(url_reset(self.aluno)).status_code, 403)
                self.assertEqual(self.conta().usu_status, status)

    def test_reset_de_conta_aguardando(self):
        """Reset antes da ativação: a conta fica sem e-mail (data-model, transições)."""
        aluno = criar_aluno_com_turma(email="x@uea.edu.br", turma=self.turma)
        self.client.post(url_reset(aluno))
        self.assertIsNone(Usuarios.objects.get(pk=aluno.pk).usu_email)

    def test_coordenador_sem_turma_nao_abre_tela_do_aluno(self):
        """A tela do aluno é do papel Professor da Disciplina: coordenador sem turma recebe 403."""
        self.client.force_login(criar_coordenador())
        resposta = self.client.get(url_aluno(self.aluno))
        self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)
        self.assertNotContains(resposta, "2026000001", status_code=403)

    def test_aluno_nao_abre_a_tela(self):
        """O próprio aluno não abre a tela de reset."""
        self.client.force_login(self.aluno.alu)
        self.assertEqual(self.client.get(url_aluno(self.aluno)).status_code, 403)

    def test_reset_invalida_links_e_sessoes_do_aluno(self):
        """RBN-CAD-06.8: o reset invalida os links pendentes e derruba a sessão do aluno."""
        aluno = criar_aluno_com_turma(email="pend@uea.edu.br", turma=self.turma)
        link = services.gerar_link_ativacao(Usuarios.objects.get(pk=aluno.pk)).split("/")[-2]
        sessao_aluno = Client()
        sessao_aluno.force_login(self.aluno.alu)
        with avancar_relogio(minutos=1):
            self.client.post(url_reset(aluno))
            self.client.post(url_reset(self.aluno))
        self.assertEqual(services.validar_link_ativacao(link).estado, EstadoLink.SEM_EMAIL)
        resposta = sessao_aluno.get(reverse("cadastro:painel"))
        self.assertRedirects(resposta, "/entrar/?next=/painel/")

    def test_aluno_inexistente_404(self):
        """Aluno que não existe: 404."""
        self.assertEqual(self.client.get(reverse("cadastro:aluno", args=[999999])).status_code, 404)
