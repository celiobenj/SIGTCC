"""Testes de aceite da US-11: fazer login e sair (spec 003, história 2).

Um teste por cenário (1 a 12 da US-11 e 13, a saída), mais os casos das Clarifications.

[US-11][RBN-CAD-06.4][RBN-CAD-06.6][RBN-CAD-03.3][FR-007]-[FR-011][SC-005]
"""

from datetime import timedelta
from unittest import mock

from django.core.cache import caches
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import StatusConta
from sigtcc.apps.cadastro.models import Usuarios
from sigtcc.apps.cadastro.tests.apoio_acesso import (
    SENHA,
    TesteAcesso,
    avancar_relogio,
    criar_aluno_com_turma,
    criar_docente_ativo,
    criar_membro_externo,
)
from sigtcc.apps.cadastro.tests.fabricas import criar_usuario

# Início fixo da M-01; o fim traz os minutos restantes.
INICIO_M01 = mensagens.M01_BLOQUEIO.split("{minutos}")[0]


class LoginTest(TesteAcesso):
    """Cenários de aceite da US-11. [US-11][RBN-CAD-06.4][RBN-CAD-06.6]"""

    def entrar(self, credencial, senha, follow=False, **extras):
        """Envia o formulário de login."""
        dados = {"credencial": credencial, "senha": senha, **extras}
        return self.client.post(reverse("cadastro:entrar"), dados, follow=follow)

    def falhas(self, usuario):
        """Contador de senhas incorretas da conta no cache."""
        return caches["acesso"].get(f"acesso:falhas:{usuario.pk}")

    def assertLogado(self, usuario):
        """A sessão foi aberta para o usuário."""
        self.assertEqual(int(self.client.session.get("_auth_user_id", 0)), usuario.pk)

    def assertNaoLogado(self):
        """Nenhuma sessão aberta."""
        self.assertNotIn("_auth_user_id", self.client.session)

    def aluno_ativo(self, matricula="2026000001", email="ana@uea.edu.br"):
        """Aluno com conta 'Ativa' e senha."""
        return criar_aluno_com_turma(
            matricula=matricula, email=email, status=StatusConta.ATIVA, senha=SENHA
        )

    # ------------------------------------------------------------------ cenários da US-11

    def test_cenario1_aluno_pela_matricula(self):
        """Dado aluno ativo, quando entra pela matrícula, então vê o painel do Aluno."""
        aluno = self.aluno_ativo()
        resposta = self.entrar("2026000001", SENHA, follow=True)
        self.assertLogado(aluno.alu)
        self.assertContains(resposta, "Painel do Aluno")

    def test_cenario2_aluno_pelo_email_institucional(self):
        """Dado aluno ativo com e-mail, quando entra pelo e-mail, então vê o painel do Aluno."""
        aluno = self.aluno_ativo()
        resposta = self.entrar("ana@uea.edu.br", SENHA, follow=True)
        self.assertLogado(aluno.alu)
        self.assertContains(resposta, "Painel do Aluno")

    def test_cenario3_docente_pelo_email(self):
        """Dado docente ativo, quando entra pelo e-mail, então vê o painel do Docente."""
        docente = criar_docente_ativo(email="prof@uea.edu.br")
        resposta = self.entrar("prof@uea.edu.br", SENHA, follow=True)
        self.assertLogado(docente)
        self.assertContains(resposta, "Painel do Docente")

    def test_cenario4_senha_errada_registra_tentativa(self):
        """Dado sem tentativas, quando erra a senha, então "Credencial ou senha inválida" e 1."""
        docente = criar_docente_ativo(email="prof@uea.edu.br")
        resposta = self.entrar("prof@uea.edu.br", "Errada123")
        self.assertContains(resposta, mensagens.CREDENCIAL_INVALIDA)
        self.assertEqual(self.falhas(docente), 1)
        self.assertNaoLogado()

    def test_cenario5_terceira_senha_errada_bloqueia(self):
        """Dado 2 erros, quando erra a terceira, então bloqueia 15 min, mesmo com a correta."""
        criar_docente_ativo(email="prof@uea.edu.br")
        self.entrar("prof@uea.edu.br", "Errada123")
        self.entrar("prof@uea.edu.br", "Errada123")
        resposta = self.entrar("prof@uea.edu.br", "Errada123")
        self.assertContains(resposta, mensagens.M01_BLOQUEIO.format(minutos=15))
        resposta = self.entrar("prof@uea.edu.br", SENHA)
        self.assertContains(resposta, INICIO_M01)
        self.assertNaoLogado()

    def test_cenario6_bloqueio_por_conta_e_nao_por_credencial(self):
        """Dado 2 erros pela matrícula, quando erra pelo e-mail, então as duas ficam bloqueadas."""
        self.aluno_ativo()
        self.entrar("2026000001", "Errada123")
        self.entrar("2026000001", "Errada123")
        resposta = self.entrar("ana@uea.edu.br", "Errada123")
        self.assertContains(resposta, INICIO_M01)
        self.assertContains(self.entrar("2026000001", SENHA), INICIO_M01)
        self.assertContains(self.entrar("ana@uea.edu.br", SENHA), INICIO_M01)
        self.assertNaoLogado()

    def test_cenario7_senha_correta_zera_contador(self):
        """Dado 2 erros, quando acerta, então entra e o próximo erro conta como o primeiro."""
        docente = criar_docente_ativo(email="prof@uea.edu.br")
        self.entrar("prof@uea.edu.br", "Errada123")
        self.entrar("prof@uea.edu.br", "Errada123")
        self.entrar("prof@uea.edu.br", SENHA)
        self.assertLogado(docente)
        self.assertIsNone(self.falhas(docente))
        self.client.post(reverse("cadastro:sair"))
        self.entrar("prof@uea.edu.br", "Errada123")
        self.assertEqual(self.falhas(docente), 1)

    def test_cenario8_membro_externo_expirado(self):
        """Dado Membro Externo 'Expirada', quando entra com a senha certa, então acesso expirado."""
        criar_membro_externo(email="ext@ufam.edu.br", status=StatusConta.EXPIRADA)
        resposta = self.entrar("ext@ufam.edu.br", SENHA)
        self.assertContains(resposta, mensagens.ACESSO_EXPIRADO)
        self.assertNaoLogado()

    def test_cenario9_membro_externo_reativado(self):
        """Dado Membro Externo que voltou a 'Ativa', quando entra, então vê o seu painel."""
        membro = criar_membro_externo(email="ext@ufam.edu.br", status=StatusConta.EXPIRADA)
        self.entrar("ext@ufam.edu.br", SENHA)
        Usuarios.objects.filter(pk=membro.pk).update(usu_status=StatusConta.ATIVA)
        resposta = self.entrar("ext@ufam.edu.br", SENHA, follow=True)
        self.assertLogado(membro)
        self.assertContains(resposta, "Painel do Membro Externo")

    def test_cenario10_conta_aguardando_ativacao(self):
        """Dado aluno 'Aguardando Ativação', quando tenta entrar, então "Conta ainda não ativada".

        O link "Primeiro acesso" é conferido em test_us10_primeiro_acesso (rota da fase 4).
        """
        aluno = criar_aluno_com_turma(matricula="2026000001")
        resposta = self.entrar("2026000001", "QualquerSenha1")
        self.assertContains(resposta, mensagens.CONTA_NAO_ATIVADA)
        self.assertIsNone(self.falhas(aluno.alu))
        self.assertNaoLogado()

    def test_cenario11_docente_inativo(self):
        """Dado docente 'Inativa', quando entra com a senha certa, então "Conta inativa"."""
        criar_docente_ativo(email="prof@uea.edu.br", status=StatusConta.INATIVA)
        resposta = self.entrar("prof@uea.edu.br", SENHA)
        self.assertContains(resposta, mensagens.CONTA_INATIVA)
        self.assertNaoLogado()

    def test_cenario12_campo_vazio(self):
        """Dado a tela de login, quando falta credencial ou senha, então não tenta autenticar."""
        docente = criar_docente_ativo(email="prof@uea.edu.br")
        for credencial, senha in (("", SENHA), ("prof@uea.edu.br", ""), ("  ", "")):
            with self.subTest(credencial=credencial, senha=senha):
                resposta = self.entrar(credencial, senha)
                self.assertContains(resposta, mensagens.INFORME_CREDENCIAL)
        self.assertIsNone(self.falhas(docente))
        self.assertNaoLogado()

    def test_cenario13_sair(self):
        """Dado usuário logado, quando clica em "Sair", então a sessão acaba e volta ao login."""
        docente = criar_docente_ativo()
        self.client.force_login(docente)
        resposta = self.client.post(reverse("cadastro:sair"))
        self.assertRedirects(resposta, reverse("cadastro:entrar"))
        self.assertNaoLogado()
        resposta = self.client.get(reverse("cadastro:painel"))
        self.assertRedirects(resposta, f"{reverse('cadastro:entrar')}?next=/painel/")

    def test_sair_so_por_post(self):
        """ "Sair" muda o estado: GET não encerra a sessão (contracts/rotas.md)."""
        docente = criar_docente_ativo()
        self.client.force_login(docente)
        self.assertEqual(self.client.get(reverse("cadastro:sair")).status_code, 405)
        self.assertLogado(docente)

    # ------------------------------------------------------------------ Clarifications

    def test_ordem_q12_senha_errada_em_conta_inativa(self):
        """Q12: senha errada em conta 'Inativa' mostra "Credencial ou senha inválida" e conta."""
        docente = criar_docente_ativo(email="prof@uea.edu.br", status=StatusConta.INATIVA)
        resposta = self.entrar("prof@uea.edu.br", "Errada123")
        self.assertContains(resposta, mensagens.CREDENCIAL_INVALIDA)
        self.assertNotContains(resposta, mensagens.CONTA_INATIVA)
        self.assertEqual(self.falhas(docente), 1)

    def test_senha_curta_conta_como_tentativa(self):
        """Q17: senha fora de 8 a 64 caracteres é senha incorreta e conta tentativa."""
        docente = criar_docente_ativo(email="prof@uea.edu.br")
        for senha in ("curta1", "a1" * 33):
            self.assertContains(
                self.entrar("prof@uea.edu.br", senha), mensagens.CREDENCIAL_INVALIDA
            )
        self.assertEqual(self.falhas(docente), 2)

    def test_validade_vencida_com_status_ativa(self):
        """Q4: Membro Externo 'Ativa' com a validade vencida recebe a mensagem de expiração."""
        ontem = timezone.now().date() - timedelta(days=1)
        criar_membro_externo(email="ext@ufam.edu.br", validade=ontem)
        resposta = self.entrar("ext@ufam.edu.br", SENHA)
        self.assertContains(resposta, mensagens.ACESSO_EXPIRADO)
        self.assertNaoLogado()

    def test_validade_de_hoje_ainda_entra(self):
        """Q4: a data de hoje ainda está dentro da validade."""
        membro = criar_membro_externo(email="ext@ufam.edu.br", validade=timezone.now().date())
        self.entrar("ext@ufam.edu.br", SENHA)
        self.assertLogado(membro)

    def test_bloqueio_15_minutos_com_relogio(self):
        """Q16: com 14 minutos ainda bloqueia (N = 1); com 15 minutos a senha certa entra."""
        docente = criar_docente_ativo(email="prof@uea.edu.br")
        for _ in range(3):
            self.entrar("prof@uea.edu.br", "Errada123")
        with avancar_relogio(minutos=14):
            resposta = self.entrar("prof@uea.edu.br", SENHA)
            self.assertContains(resposta, mensagens.M01_BLOQUEIO.format(minutos=1))
        with avancar_relogio(minutos=15):
            self.entrar("prof@uea.edu.br", SENHA)
            self.assertLogado(docente)

    def test_novo_bloqueio_logo_depois_do_anterior(self):
        """Um bloqueio novo vale mesmo com o registro do anterior ainda no cache (A2)."""
        criar_docente_ativo(email="prof@uea.edu.br")
        for _ in range(3):
            self.entrar("prof@uea.edu.br", "Errada123")
        with avancar_relogio(minutos=15):
            for _ in range(3):
                self.entrar("prof@uea.edu.br", "Errada123")
            resposta = self.entrar("prof@uea.edu.br", SENHA)
            self.assertContains(resposta, INICIO_M01)
            self.assertNaoLogado()

    def test_senha_correta_em_conta_inativa_zera_contador(self):
        """FR-009: a senha correta zera o contador, qualquer que seja o status."""
        docente = criar_docente_ativo(email="prof@uea.edu.br", status=StatusConta.INATIVA)
        self.entrar("prof@uea.edu.br", "Errada123")
        self.entrar("prof@uea.edu.br", SENHA)
        self.assertIsNone(self.falhas(docente))

    def test_next_externo_ignorado(self):
        """B2: next externo leva ao painel; next interno é seguido."""
        criar_docente_ativo(email="prof@uea.edu.br")
        for destino in ("https://outro.site/", "//outro.site", "/\\outro.site"):
            with self.subTest(next=destino):
                resposta = self.entrar("prof@uea.edu.br", SENHA, next=destino)
                self.assertRedirects(resposta, reverse("cadastro:painel"))
                self.client.post(reverse("cadastro:sair"))
        resposta = self.entrar("prof@uea.edu.br", SENHA, next="/painel/?aba=1")
        self.assertRedirects(resposta, "/painel/?aba=1")

    def test_next_volta_no_formulario(self):
        """O next da URL vai num campo oculto do formulário e é mantido quando há erro."""
        resposta = self.client.get(reverse("cadastro:entrar") + "?next=/painel/")
        self.assertContains(resposta, 'name="next" value="/painel/"')
        resposta = self.entrar("x@uea.edu.br", "Errada123", next="/painel/")
        self.assertContains(resposta, 'name="next" value="/painel/"')

    def test_logado_em_entrar_vai_ao_painel(self):
        """Usuário já logado que abre a tela de login vai ao painel."""
        self.client.force_login(criar_docente_ativo())
        self.assertRedirects(
            self.client.get(reverse("cadastro:entrar")), reverse("cadastro:painel")
        )

    def test_credencial_inexistente_calcula_hash(self):
        """I1: sem conta, o hash da senha é calculado do mesmo jeito; sem contador e sem log."""
        with mock.patch.object(Usuarios, "set_password", autospec=True) as calculo:
            with self.assertNoLogs("sigtcc.acesso"):
                resposta = self.entrar("ninguem@uea.edu.br", "Senha1234")
        self.assertContains(resposta, mensagens.CREDENCIAL_INVALIDA)
        calculo.assert_called_once()

    def test_email_duplicado_nao_quebra(self):
        """I3: dois e-mails que só diferem em maiúsculas: credencial inválida e evento técnico."""
        criar_usuario(email="dup@uea.edu.br")
        criar_usuario(email="DUP@uea.edu.br")
        with self.assertLogs("sigtcc.acesso") as log:
            resposta = self.entrar("Dup@uea.edu.br", SENHA)
        self.assertContains(resposta, mensagens.CREDENCIAL_INVALIDA)
        self.assertEqual(len(log.output), 1)
        self.assertIn("EMAIL_DUPLICADO | conta=- | autor=- | contas=2", log.output[0])

    def test_email_sem_diferenciar_maiusculas(self):
        """Q13: o e-mail da credencial é comparado sem diferenciar maiúsculas."""
        docente = criar_docente_ativo(email="prof@uea.edu.br")
        self.entrar("PROF@UEA.EDU.BR", SENHA)
        self.assertLogado(docente)

    def test_senha_mascarada(self):
        """FR-007: a senha é exibida mascarada e não volta preenchida depois de um erro."""
        criar_docente_ativo(email="prof@uea.edu.br")
        resposta = self.entrar("prof@uea.edu.br", "Errada123")
        self.assertContains(resposta, 'type="password"')
        self.assertNotContains(resposta, "Errada123")
