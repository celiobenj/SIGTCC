"""Testes de aceite da US-10: criar a senha no primeiro acesso (spec 003, história 1).

Um teste por cenário (1 a 11 da US-10), mais os casos das Clarifications e da revisão.

[US-10][RBN-CAD-06.1][RBN-CAD-06.2][RBN-CAD-06.3][FR-001]-[FR-006][Q2][Q5][Q6][Q8][Q12][Q15]
[Q23][Q26][B1][I4][I5]
"""

from datetime import timedelta
from smtplib import SMTPException
from unittest import mock

from django.core import mail
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape

from sigtcc.apps.cadastro import mensagens, services
from sigtcc.apps.cadastro.choices import StatusConta
from sigtcc.apps.cadastro.models import Alunos, Usuarios
from sigtcc.apps.cadastro.services import EstadoLink
from sigtcc.apps.cadastro.tests.apoio_acesso import (
    SENHA,
    TesteAcesso,
    avancar_relogio,
    caminho_do_link,
    criar_aluno_com_turma,
    criar_docente_ativo,
    criar_membro_externo,
)
from sigtcc.apps.cadastro.tests.fabricas import criar_aluno

URL_ALUNO = reverse("cadastro:primeiro_acesso_aluno")
URL_EMAIL = reverse("cadastro:primeiro_acesso_email")
URL_DEFINIR = reverse("cadastro:definir_senha")


class PrimeiroAcessoTest(TesteAcesso):
    """Cenários de aceite da US-10. [US-10][RBN-CAD-06.1][RBN-CAD-06.2][RBN-CAD-06.3]"""

    def pedir_aluno(self, matricula, email, follow=True):
        """Envia o formulário "Aluno" do primeiro acesso."""
        return self.client.post(URL_ALUNO, {"matricula": matricula, "email": email}, follow=follow)

    def pedir_email(self, email, follow=True):
        """Envia o formulário "Docente, Secretaria ou Membro Externo"."""
        return self.client.post(URL_EMAIL, {"email": email}, follow=follow)

    def abrir_ultimo_link(self):
        """Abre o link do último e-mail enviado (o token vai para a sessão)."""
        return self.client.get(caminho_do_link(mail.outbox[-1]), follow=True)

    def definir(self, senha=SENHA, confirmacao=None, follow=True):
        """Envia o formulário de ativação."""
        dados = {"senha": senha, "confirmacao": confirmacao if confirmacao is not None else senha}
        return self.client.post(URL_DEFINIR, dados, follow=follow)

    def status(self, usuario):
        """Status atual da conta no banco."""
        return Usuarios.objects.get(pk=usuario.pk).usu_status

    def aluno_aguardando(self, matricula="2026000001", email=None):
        """Aluno 'Aguardando Ativação' com turma."""
        return criar_aluno_com_turma(matricula=matricula, email=email)

    # ------------------------------------------------------------------ cenários da US-10

    def test_cenario1_aluno_ativa_a_conta(self):
        """Dado aluno aguardando, quando pede, abre o link e define a senha, então 'Ativa'."""
        aluno = self.aluno_aguardando()
        self.pedir_aluno("2026000001", "ana@uea.edu.br")
        self.assertEqual(mail.outbox[0].to, ["ana@uea.edu.br"])
        self.abrir_ultimo_link()
        resposta = self.definir()
        self.assertRedirects(resposta, reverse("cadastro:entrar"))
        self.assertContains(resposta, mensagens.CONTA_ATIVADA)
        conta = Usuarios.objects.get(pk=aluno.pk)
        self.assertEqual(conta.usu_status, StatusConta.ATIVA)
        self.assertTrue(conta.check_password(SENHA))
        self.assertNotEqual(conta.password, SENHA)

    def test_cenario2_docente_recebe_link_de_24_horas(self):
        """Dado docente cadastrado, quando informa o e-mail, então recebe link de 24 h."""
        docente = criar_docente_ativo(
            email="prof@uea.edu.br", senha=None, status=StatusConta.AGUARDANDO_ATIVACAO
        )
        resposta = self.pedir_email("prof@uea.edu.br")
        self.assertContains(resposta, mensagens.LINK_ATIVACAO_ENVIADO)
        self.assertEqual(mail.outbox[0].to, ["prof@uea.edu.br"])
        token = caminho_do_link(mail.outbox[0]).split("/")[-2]
        self.assertEqual(services.validar_link_ativacao(token).estado, EstadoLink.VALIDO)
        with avancar_relogio(horas=23, minutos=59):
            self.assertEqual(services.validar_link_ativacao(token).estado, EstadoLink.VALIDO)
        with avancar_relogio(horas=24, minutos=1):
            self.assertEqual(services.validar_link_ativacao(token).estado, EstadoLink.VENCIDO)
        self.assertEqual(self.status(docente), StatusConta.AGUARDANDO_ATIVACAO)

    def test_cenario3_link_vencido(self):
        """Dado link com mais de 24 h, quando é aberto, então aviso e botão de reenvio."""
        self.aluno_aguardando()
        self.pedir_aluno("2026000001", "ana@uea.edu.br")
        with avancar_relogio(horas=25):
            resposta = self.abrir_ultimo_link()
        self.assertContains(resposta, mensagens.LINK_ATIVACAO_VENCEU)
        self.assertContains(resposta, mensagens.REENVIAR_LINK)
        self.assertNotContains(resposta, 'name="senha"')

    def test_cenario4_senha_sem_numero(self):
        """Dado o formulário de ativação, quando a senha é "abcdefgh", então a regra e não ativa."""
        aluno = self.aluno_aguardando()
        self.pedir_aluno("2026000001", "ana@uea.edu.br")
        self.abrir_ultimo_link()
        resposta = self.definir("abcdefgh")
        self.assertContains(resposta, mensagens.REGRA_SENHA)
        self.assertEqual(self.status(aluno.alu), StatusConta.AGUARDANDO_ATIVACAO)

    def test_cenario5_confirmacao_diferente(self):
        """Dado o formulário de ativação, quando a confirmação difere, então erro."""
        aluno = self.aluno_aguardando()
        self.pedir_aluno("2026000001", "ana@uea.edu.br")
        self.abrir_ultimo_link()
        resposta = self.definir(SENHA, "Outra1234")
        self.assertContains(resposta, mensagens.SENHAS_NAO_CONFEREM)
        self.assertEqual(self.status(aluno.alu), StatusConta.AGUARDANDO_ATIVACAO)

    def test_cenario6_matricula_inexistente(self):
        """Dado matrícula sem aluno, quando informada, então "Dados não encontrados..."."""
        resposta = self.pedir_aluno("2026000999", "ana@uea.edu.br")
        self.assertContains(resposta, mensagens.DADOS_NAO_ENCONTRADOS)
        self.assertEqual(len(mail.outbox), 0)

    def test_cenario7_conta_ja_ativa(self):
        """Dado aluno 'Ativa', quando pede o primeiro acesso, então "Esta conta já está ativa"."""
        criar_aluno_com_turma(
            matricula="2026000001", email="ana@uea.edu.br", status=StatusConta.ATIVA, senha=SENHA
        )
        resposta = self.pedir_aluno("2026000001", "ana@uea.edu.br")
        self.assertContains(resposta, mensagens.CONTA_JA_ATIVA)
        self.assertContains(resposta, escape(mensagens.M03_ORIENTACAO_CONTA_ATIVA))
        self.assertEqual(len(mail.outbox), 0)

    def test_cenario8_email_fora_da_uea(self):
        """Dado o formulário do Aluno, quando o e-mail é @gmail.com, então pede o institucional."""
        self.aluno_aguardando()
        resposta = self.pedir_aluno("2026000001", "aluno@gmail.com")
        self.assertContains(resposta, mensagens.EMAIL_INSTITUCIONAL)
        self.assertEqual(len(mail.outbox), 0)

    def test_cenario9_email_de_outro_aluno(self):
        """Dado e-mail de outro aluno, quando informado, então "Este e-mail já está..."."""
        criar_aluno_com_turma(matricula="2026000002", email="ana.eng24@uea.edu.br")
        self.aluno_aguardando()
        resposta = self.pedir_aluno("2026000001", "ana.eng24@uea.edu.br")
        self.assertContains(resposta, mensagens.EMAIL_DE_OUTRA_CONTA_ALUNO)
        self.assertEqual(len(mail.outbox), 0)

    def test_cenario10_matricula_com_8_digitos(self):
        """Dado o formulário do Aluno, quando a matrícula tem 8 dígitos, então o formato."""
        resposta = self.pedir_aluno("20260001", "ana@uea.edu.br")
        self.assertContains(resposta, mensagens.MATRICULA_FORMATO)
        self.assertContains(resposta, "com-erro")
        self.assertEqual(len(mail.outbox), 0)

    def test_cenario11_so_o_link_mais_recente_ativa(self):
        """Dado link não usado, quando pede de novo e abre o anterior, então "Link inválido..."."""
        aluno = self.aluno_aguardando()
        self.pedir_aluno("2026000001", "ana@uea.edu.br")
        primeiro = caminho_do_link(mail.outbox[0])
        with avancar_relogio(minutos=1):
            self.pedir_aluno("2026000001", "ana@uea.edu.br")
            resposta = self.client.get(primeiro, follow=True)
            self.assertContains(resposta, mensagens.LINK_SUBSTITUIDO)
            self.assertNotContains(resposta, 'name="senha"')
            self.abrir_ultimo_link()
            self.definir()
        self.assertEqual(self.status(aluno.alu), StatusConta.ATIVA)

    # ------------------------------------------------------------------ Clarifications e revisão

    def test_matricula_sem_turma(self):
        """US-10 E1: aluno sem turma recebe "Dados não encontrados..."."""
        criar_aluno(matricula="2026000001")
        resposta = self.pedir_aluno("2026000001", "ana@uea.edu.br")
        self.assertContains(resposta, mensagens.DADOS_NAO_ENCONTRADOS)
        self.assertEqual(len(mail.outbox), 0)

    def test_q2_email_novo_ignorado(self):
        """Q2: aluno com e-mail registrado recebe o link nesse e-mail; o novo é ignorado."""
        aluno = self.aluno_aguardando()
        self.pedir_aluno("2026000001", "ana@uea.edu.br")
        resposta = self.pedir_aluno("2026000001", "outra@uea.edu.br")
        self.assertContains(resposta, mensagens.LINK_ATIVACAO_ENVIADO)
        self.assertEqual(mail.outbox[-1].to, ["ana@uea.edu.br"])
        self.assertEqual(Usuarios.objects.get(pk=aluno.pk).usu_email, "ana@uea.edu.br")

    def test_q15_formato_do_email_ignorado_ainda_validado(self):
        """Q15: o e-mail ignorado ainda passa por formato e domínio, mas não por unicidade."""
        self.aluno_aguardando()
        criar_aluno_com_turma(matricula="2026000002", email="ocupado@uea.edu.br")
        self.pedir_aluno("2026000001", "ana@uea.edu.br")
        resposta = self.pedir_aluno("2026000001", "ana@gmail.com")
        self.assertContains(resposta, mensagens.EMAIL_INSTITUCIONAL)
        resposta = self.pedir_aluno("2026000001", "ocupado@uea.edu.br")
        self.assertContains(resposta, mensagens.LINK_ATIVACAO_ENVIADO)
        self.assertEqual(mail.outbox[-1].to, ["ana@uea.edu.br"])

    def test_q8_email_de_aluno_no_formulario_de_email(self):
        """Q8 e A9: e-mail de Aluno no formulário dos demais recebe "Dados não encontrados..."."""
        self.aluno_aguardando()
        self.pedir_aluno("2026000001", "ana@uea.edu.br")
        mail.outbox.clear()
        resposta = self.pedir_email("ana@uea.edu.br")
        self.assertContains(resposta, mensagens.DADOS_NAO_ENCONTRADOS)
        self.assertEqual(len(mail.outbox), 0)

    def test_q8_secretaria_e_membro_externo_pelo_mesmo_formulario(self):
        """Q8: o formulário único aceita Secretaria e Membro Externo."""
        from sigtcc.apps.cadastro.tests.apoio_acesso import criar_secretaria

        criar_secretaria(email="sec@uea.edu.br", senha=None, status=StatusConta.AGUARDANDO_ATIVACAO)
        criar_membro_externo(
            email="ext@ufam.edu.br", senha=None, status=StatusConta.AGUARDANDO_ATIVACAO
        )
        self.assertContains(self.pedir_email("sec@uea.edu.br"), mensagens.LINK_ATIVACAO_ENVIADO)
        self.assertContains(self.pedir_email("EXT@ufam.edu.br"), mensagens.LINK_ATIVACAO_ENVIADO)
        self.assertEqual(len(mail.outbox), 2)

    def test_q6_conta_inativa(self):
        """Q6: primeiro acesso de conta 'Inativa' mostra a M-15 e não envia link."""
        criar_docente_ativo(email="prof@uea.edu.br", status=StatusConta.INATIVA)
        resposta = self.pedir_email("prof@uea.edu.br")
        self.assertContains(resposta, mensagens.M15_CONTA_INATIVA)
        self.assertEqual(len(mail.outbox), 0)

    def test_q6_conta_expirada_e_validade_vencida(self):
        """Q6 e Q4: conta 'Expirada' ou com a validade vencida mostra a M-16."""
        criar_membro_externo(email="exp@ufam.edu.br", status=StatusConta.EXPIRADA)
        ontem = timezone.now().date() - timedelta(days=1)
        criar_membro_externo(
            email="venc@ufam.edu.br",
            senha=None,
            status=StatusConta.AGUARDANDO_ATIVACAO,
            validade=ontem,
        )
        for email in ("exp@ufam.edu.br", "venc@ufam.edu.br"):
            with self.subTest(email=email):
                self.assertContains(self.pedir_email(email), escape(mensagens.M16_ACESSO_EXPIRADO))
        self.assertEqual(len(mail.outbox), 0)

    def test_q12_so_o_primeiro_erro(self):
        """Q12: matrícula fora do formato e e-mail fora do domínio: só o erro da matrícula."""
        resposta = self.pedir_aluno("123", "aluno@gmail.com")
        self.assertContains(resposta, mensagens.MATRICULA_FORMATO)
        self.assertNotContains(resposta, mensagens.EMAIL_INSTITUCIONAL)

    def test_q12_existencia_da_matricula_antes_do_email(self):
        """Q12: matrícula inexistente vem antes do e-mail fora do domínio."""
        resposta = self.pedir_aluno("2026000999", "aluno@gmail.com")
        self.assertContains(resposta, mensagens.DADOS_NAO_ENCONTRADOS)
        self.assertNotContains(resposta, mensagens.EMAIL_INSTITUCIONAL)

    def test_m10_email_invalido_no_formulario_dos_demais(self):
        """FR-003: e-mail fora do formato no segundo formulário mostra a M-10."""
        resposta = self.pedir_email("sem-arroba")
        self.assertContains(resposta, mensagens.M10_EMAIL_INVALIDO)

    def test_m14_campo_vazio(self):
        """M-14: campo obrigatório vazio."""
        self.assertContains(self.pedir_aluno("", ""), mensagens.M14_CAMPO_OBRIGATORIO)
        self.assertContains(self.pedir_email(""), mensagens.M14_CAMPO_OBRIGATORIO)

    def test_i5_falha_no_envio_desfaz(self):
        """I5: falha no envio mostra a M-17, não grava o e-mail e mantém o link anterior."""
        aluno = self.aluno_aguardando()
        self.pedir_aluno("2026000001", "ana@uea.edu.br")
        anterior = caminho_do_link(mail.outbox[0])
        gerado_em = Usuarios.objects.get(pk=aluno.pk).usu_link_gerado_em
        outro = self.aluno_aguardando(matricula="2026000002")
        falha = SMTPException("servidor fora")
        with mock.patch("sigtcc.apps.cadastro.services.send_mail", side_effect=falha):
            with self.assertLogs("sigtcc.acesso") as log:
                resposta = self.pedir_aluno("2026000001", "ana@uea.edu.br")
                self.assertContains(resposta, mensagens.M17_FALHA_ENVIO)
                resposta = self.pedir_aluno("2026000002", "beto@uea.edu.br")
                self.assertContains(resposta, mensagens.M17_FALHA_ENVIO)
        self.assertIn("FALHA_ENVIO_EMAIL", log.output[0])
        self.assertIn("SMTPException", log.output[0])
        self.assertNotIn("servidor fora", "".join(log.output))
        self.assertEqual(Usuarios.objects.get(pk=aluno.pk).usu_link_gerado_em, gerado_em)
        self.assertIsNone(Usuarios.objects.get(pk=outro.pk).usu_email)
        self.client.get(anterior)
        self.definir()
        self.assertEqual(self.status(aluno.alu), StatusConta.ATIVA)

    def test_token_sai_da_url(self):
        """A3: o GET com o token guarda o token na sessão e redireciona para a URL fixa."""
        self.aluno_aguardando()
        self.pedir_aluno("2026000001", "ana@uea.edu.br")
        caminho = caminho_do_link(mail.outbox[0])
        resposta = self.client.get(caminho)
        self.assertRedirects(resposta, URL_DEFINIR)
        self.assertEqual(self.client.session["token_ativacao"], caminho.split("/")[-2])
        resposta = self.client.get(URL_DEFINIR)
        self.assertContains(resposta, 'name="senha"')
        self.assertNotContains(resposta, caminho.split("/")[-2])

    def test_token_sai_da_sessao_depois_de_ativar(self):
        """A3: o token sai da sessão quando a ativação termina."""
        self.aluno_aguardando()
        self.pedir_aluno("2026000001", "ana@uea.edu.br")
        self.abrir_ultimo_link()
        self.definir()
        self.assertNotIn("token_ativacao", self.client.session)

    def test_definir_senha_sem_token_na_sessao(self):
        """A3: sem token na sessão, a tela trata como link adulterado."""
        resposta = self.client.get(URL_DEFINIR)
        self.assertContains(resposta, mensagens.LINK_SUBSTITUIDO)
        resposta = self.definir()
        self.assertContains(resposta, mensagens.LINK_SUBSTITUIDO)

    def test_link_adulterado(self):
        """Q23: link alterado ou cortado mostra "Link inválido. Use o link mais recente..."."""
        self.aluno_aguardando()
        self.pedir_aluno("2026000001", "ana@uea.edu.br")
        caminho = caminho_do_link(mail.outbox[0])
        for adulterado in (caminho[:-3] + "/", caminho.replace(":", "x:", 1)):
            with self.subTest(caminho=adulterado):
                resposta = self.client.get(adulterado, follow=True)
                self.assertContains(resposta, mensagens.LINK_SUBSTITUIDO)
                self.assertNotContains(resposta, 'name="senha"')

    def test_b1_link_valido_em_conta_inativada(self):
        """B1 e Q26: link válido aberto depois que a conta ficou 'Inativa' mostra a M-15."""
        aluno = self.aluno_aguardando()
        self.pedir_aluno("2026000001", "ana@uea.edu.br")
        Usuarios.objects.filter(pk=aluno.pk).update(usu_status=StatusConta.INATIVA)
        resposta = self.abrir_ultimo_link()
        self.assertContains(resposta, mensagens.M15_CONTA_INATIVA)
        self.assertNotContains(resposta, 'name="senha"')
        resposta = self.definir()
        self.assertEqual(self.status(aluno.alu), StatusConta.INATIVA)

    def test_link_de_conta_ja_ativa_vai_ao_login(self):
        """FR-016 (1): link de conta já ativa mostra "Esta conta já está ativa" no login."""
        aluno = self.aluno_aguardando()
        self.pedir_aluno("2026000001", "ana@uea.edu.br")
        caminho = caminho_do_link(mail.outbox[0])
        Usuarios.objects.filter(pk=aluno.pk).update(usu_status=StatusConta.ATIVA)
        resposta = self.client.get(caminho, follow=True)
        self.assertRedirects(resposta, reverse("cadastro:entrar"))
        self.assertContains(resposta, mensagens.CONTA_JA_ATIVA)

    def test_post_revalida_link(self):
        """A17: link substituído entre o GET e o POST não ativa a conta."""
        aluno = self.aluno_aguardando()
        self.pedir_aluno("2026000001", "ana@uea.edu.br")
        self.abrir_ultimo_link()
        with avancar_relogio(minutos=1):
            services.gerar_link_ativacao(Usuarios.objects.get(pk=aluno.pk))
        resposta = self.definir()
        self.assertContains(resposta, mensagens.LINK_SUBSTITUIDO)
        self.assertEqual(self.status(aluno.alu), StatusConta.AGUARDANDO_ATIVACAO)

    def test_us11_cenario10_link_primeiro_acesso(self):
        """US-11, cenário 10: "Conta ainda não ativada" com o link "Primeiro acesso" no login."""
        self.aluno_aguardando()
        resposta = self.client.post(
            reverse("cadastro:entrar"), {"credencial": "2026000001", "senha": "Qualquer1"}
        )
        self.assertContains(resposta, mensagens.CONTA_NAO_ATIVADA)
        self.assertContains(
            resposta, f'<a href="{reverse("cadastro:primeiro_acesso")}">Primeiro acesso</a>'
        )

    def test_tela_de_escolha(self):
        """FR-001 e Q8: "Primeiro acesso" oferece as duas escolhas."""
        resposta = self.client.get(reverse("cadastro:primeiro_acesso"))
        self.assertContains(resposta, URL_ALUNO)
        self.assertContains(resposta, URL_EMAIL)
        self.assertContains(resposta, "Docente, Secretaria ou Membro Externo")

    def test_aluno_sem_especializacao_nao_existe_para_email(self):
        """Conta sem tipo (sem especialização) não recebe link pelo formulário de e-mail."""
        Usuarios.objects.create_user("solta@uea.edu.br", "Conta solta")
        resposta = self.pedir_email("solta@uea.edu.br")
        self.assertContains(resposta, mensagens.DADOS_NAO_ENCONTRADOS)
        self.assertFalse(Alunos.objects.exists())
