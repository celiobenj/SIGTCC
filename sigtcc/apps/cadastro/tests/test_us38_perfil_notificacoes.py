"""Testes de aceite da US-38: editar o perfil e ver as notificações (spec 003, história 5).

Um teste por cenário (1 a 11 da US-38; o 9 na variante "item removido", Q10), mais os casos das
Clarifications e da revisão.

[US-38][RBN-CAD-13.1][RBN-CAD-13.2][FR-019]-[FR-023][Q10][Q11][Q14][Q24][Q28][I6][I7]
"""

import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from smtplib import SMTPException
from unittest import mock

from django.core import mail
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import StatusConta, Titulacao
from sigtcc.apps.cadastro.models import (
    Docentes,
    MembrosExternos,
    Notificacoes,
    Usuarios,
)
from sigtcc.apps.cadastro.tests.apoio_acesso import (
    SENHA,
    TesteAcesso,
    avancar_relogio,
    caminho_do_link,
    criar_aluno_com_turma,
    criar_docente_ativo,
    criar_membro_externo,
    criar_notificacao,
    criar_secretaria,
)

URL_PERFIL = reverse("cadastro:perfil")
URL_NOTIFICACOES = reverse("cadastro:notificacoes")
URL_MARCAR = reverse("cadastro:marcar_lidas")

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 64
PDF = b"%PDF-1.4\n" + b"\x00" * 64


def arquivo(nome, conteudo, tipo="application/octet-stream"):
    """Arquivo enviado pelo formulário."""
    return SimpleUploadedFile(nome, conteudo, content_type=tipo)


class ComMidiaTemporaria(TesteAcesso):
    """Base com MEDIA_ROOT temporário: os testes não gravam em sigtcc/media/."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pasta_midia = tempfile.mkdtemp(prefix="sigtcc-midia-")
        cls.enterClassContext(override_settings(MEDIA_ROOT=cls.pasta_midia))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.pasta_midia, ignore_errors=True)
        super().tearDownClass()


class PerfilTest(ComMidiaTemporaria):
    """ "Meu perfil" (cenários 1, 2, 3, 5, 6, 7, 8 e 11; Q11, Q28). [US-38][RBN-CAD-13.1]"""

    def salvar(self, dados, follow=True):
        return self.client.post(URL_PERFIL, dados, follow=follow)

    def caminho_assinatura(self, usuario):
        return Docentes.objects.get(pk=usuario.pk).doc_assinatura_path

    # ------------------------------------------------------------------ cenários da US-38

    def test_cenario1_docente_envia_assinatura_png(self):
        """Dado o Docente em "Meu perfil", quando envia PNG e salva, então "Perfil atualizado"."""
        docente = criar_docente_ativo()
        self.client.force_login(docente)
        resposta = self.salvar({"assinatura": arquivo("assinatura.png", PNG, "image/png")})
        self.assertContains(resposta, mensagens.PERFIL_ATUALIZADO)
        caminho = self.caminho_assinatura(docente)
        self.assertRegex(caminho, rf"^assinaturas/{docente.pk}_[0-9a-f]+\.png$")
        self.assertTrue(default_storage.exists(caminho))

    def test_cenario2_aluno_nao_altera_matricula_nem_curso(self):
        """Dado o Aluno, quando tenta alterar Matrícula ou Curso, então ficam bloqueados."""
        aluno = criar_aluno_com_turma(
            matricula="2026000001", email="ana@uea.edu.br", status=StatusConta.ATIVA, senha=SENHA
        )
        self.client.force_login(aluno.alu)
        resposta = self.client.get(URL_PERFIL)
        self.assertContains(resposta, "2026000001")
        # EST08MCPD é reconhecido pela carga da spec 004 (FR-015a).
        self.assertContains(resposta, "Engenharia de Computação")
        self.assertNotContains(resposta, 'name="matricula"')
        self.assertNotContains(resposta, 'name="curso"')
        self.salvar({"email": "ana@uea.edu.br", "matricula": "2026999999", "curso": "X"})
        aluno.refresh_from_db()
        self.assertEqual(aluno.alu_matricula, "2026000001")
        self.assertEqual(aluno.alu_codigo_curso, "EST08MCPD")

    def test_cenario3_assinatura_em_pdf(self):
        """Dado o Docente, quando envia PDF, então a M-04 e nada é salvo."""
        docente = criar_docente_ativo()
        self.client.force_login(docente)
        resposta = self.salvar({"assinatura": arquivo("assinatura.pdf", PDF, "application/pdf")})
        self.assertContains(resposta, mensagens.M04_ASSINATURA_FORMATO)
        self.assertNotContains(resposta, mensagens.PERFIL_ATUALIZADO)
        self.assertIsNone(self.caminho_assinatura(docente))

    def test_cenario5_aluno_troca_email_com_confirmacao(self):
        """Dado o Aluno, quando troca o e-mail, então troca só depois de confirmar."""
        aluno = criar_aluno_com_turma(email="ana@uea.edu.br", status=StatusConta.ATIVA, senha=SENHA)
        self.client.force_login(aluno.alu)
        resposta = self.salvar({"email": "ana.nova@uea.edu.br"})
        self.assertContains(resposta, mensagens.M06_CONFIRMACAO_EMAIL_ENVIADA)
        self.assertEqual(mail.outbox[0].to, ["ana.nova@uea.edu.br"])
        self.assertEqual(Usuarios.objects.get(pk=aluno.pk).usu_email, "ana@uea.edu.br")
        caminho = caminho_do_link(mail.outbox[0])
        resposta = self.client.get(caminho)
        self.assertContains(resposta, "ana.nova@uea.edu.br")
        self.assertContains(resposta, mensagens.CONFIRMAR_NOVO_EMAIL)
        resposta = self.client.post(caminho)
        self.assertContains(resposta, mensagens.M07_EMAIL_ATUALIZADO)
        self.assertEqual(Usuarios.objects.get(pk=aluno.pk).usu_email, "ana.nova@uea.edu.br")

    def test_cenario6_aluno_com_email_fora_da_uea(self):
        """Dado o Aluno, quando informa "aluno@gmail.com", então destaca o campo e não salva."""
        aluno = criar_aluno_com_turma(email="ana@uea.edu.br", status=StatusConta.ATIVA, senha=SENHA)
        self.client.force_login(aluno.alu)
        resposta = self.salvar({"email": "aluno@gmail.com"})
        self.assertContains(resposta, mensagens.M11_EMAIL_INSTITUCIONAL)
        self.assertContains(resposta, "com-erro")
        self.assertEqual(len(mail.outbox), 0)

    def test_cenario7_membro_externo_muda_titulacao(self):
        """Dado o Membro Externo, quando muda Mestre para Doutor, então "Perfil atualizado"."""
        membro = criar_membro_externo(email="ext@ufam.edu.br")
        self.client.force_login(membro)
        resposta = self.salvar(
            {
                "email": "ext@ufam.edu.br",
                "titulacao": Titulacao.DOUTOR,
                "instituicao": "Universidade Federal do Amazonas",
            }
        )
        self.assertContains(resposta, mensagens.PERFIL_ATUALIZADO)
        self.assertEqual(MembrosExternos.objects.get(pk=membro.pk).mem_titulacao, "Doutor")
        self.assertEqual(len(mail.outbox), 0)

    def test_cenario8_secretaria_so_leitura(self):
        """Dado a Secretaria, quando abre o perfil, então tudo só leitura e sem "Salvar"."""
        secretaria = criar_secretaria(email="sec@uea.edu.br")
        self.client.force_login(secretaria)
        resposta = self.client.get(URL_PERFIL)
        self.assertContains(resposta, "sec@uea.edu.br")
        self.assertNotContains(resposta, ">Salvar<")
        self.assertNotContains(resposta, 'name="email"')
        self.assertNotContains(resposta, 'type="file"')
        self.salvar({"email": "outro@uea.edu.br"})
        self.assertEqual(Usuarios.objects.get(pk=secretaria.pk).usu_email, "sec@uea.edu.br")
        self.assertEqual(len(mail.outbox), 0)

    def test_cenario11_assinatura_jpg_de_3_mb(self):
        """Dado o Docente, quando envia JPG de 3 MB, então destaca o campo e não salva."""
        docente = criar_docente_ativo()
        self.client.force_login(docente)
        grande = JPEG + b"\x00" * (3 * 1024 * 1024)
        resposta = self.salvar({"assinatura": arquivo("assinatura.jpg", grande, "image/jpeg")})
        self.assertContains(resposta, mensagens.M04_ASSINATURA_FORMATO)
        self.assertContains(resposta, "com-erro")
        self.assertIsNone(self.caminho_assinatura(docente))

    # ------------------------------------------------------------------ Clarifications e revisão

    def test_q28_confirmacao_em_duas_etapas(self):
        """Q28: o GET do link não troca o e-mail; só o POST do botão troca."""
        membro = criar_membro_externo(email="ext@ufam.edu.br")
        self.client.force_login(membro)
        self.salvar({"email": "novo@ufam.edu.br", "titulacao": "Mestre", "instituicao": "UFAM"})
        caminho = caminho_do_link(mail.outbox[0])
        self.client.get(caminho)
        self.client.get(caminho)
        self.assertEqual(Usuarios.objects.get(pk=membro.pk).usu_email, "ext@ufam.edu.br")
        self.assertContains(self.client.post(caminho), mensagens.M07_EMAIL_ATUALIZADO)

    def test_q28_email_ocupado_na_confirmacao(self):
        """Q28: novo e-mail ocupado por outra conta até a confirmação mostra a M-05."""
        membro = criar_membro_externo(email="ext@ufam.edu.br")
        self.client.force_login(membro)
        self.salvar({"email": "novo@ufam.edu.br", "titulacao": "Mestre", "instituicao": "UFAM"})
        criar_docente_ativo(email="NOVO@ufam.edu.br")
        resposta = self.client.post(caminho_do_link(mail.outbox[0]))
        self.assertContains(resposta, mensagens.M05_EMAIL_EM_USO)
        self.assertEqual(Usuarios.objects.get(pk=membro.pk).usu_email, "ext@ufam.edu.br")

    def test_email_em_uso_ao_salvar(self):
        """M-05: e-mail de outra conta (sem diferenciar maiúsculas) não é aceito."""
        criar_docente_ativo(email="ocupado@uea.edu.br")
        membro = criar_membro_externo(email="ext@ufam.edu.br")
        self.client.force_login(membro)
        resposta = self.salvar(
            {"email": "Ocupado@uea.edu.br", "titulacao": "Mestre", "instituicao": "UFAM"}
        )
        self.assertContains(resposta, mensagens.M05_EMAIL_EM_USO)
        self.assertEqual(len(mail.outbox), 0)

    def test_m10_email_fora_do_formato(self):
        """M-10: e-mail fora do formato no perfil."""
        membro = criar_membro_externo(email="ext@ufam.edu.br")
        self.client.force_login(membro)
        resposta = self.salvar({"email": "sem-arroba", "titulacao": "Mestre", "instituicao": "U"})
        self.assertContains(resposta, mensagens.M10_EMAIL_INVALIDO)

    def test_q11_so_m06_ao_salvar_com_troca(self):
        """Q11: salvar com troca de e-mail mostra só a M-06, sem "Perfil atualizado"."""
        membro = criar_membro_externo(email="ext@ufam.edu.br")
        self.client.force_login(membro)
        resposta = self.salvar(
            {"email": "novo@ufam.edu.br", "titulacao": "Doutor", "instituicao": "UFAM"}
        )
        self.assertContains(resposta, mensagens.M06_CONFIRMACAO_EMAIL_ENVIADA)
        self.assertNotContains(resposta, mensagens.PERFIL_ATUALIZADO)
        self.assertEqual(MembrosExternos.objects.get(pk=membro.pk).mem_titulacao, "Doutor")

    def test_link_de_troca_vencido_e_depois_de_outra_troca(self):
        """Q11 e Q24: link de troca com mais de 24 h, ou depois de outra troca, mostra a M-09."""
        aluno = criar_aluno_com_turma(email="ana@uea.edu.br", status=StatusConta.ATIVA, senha=SENHA)
        self.client.force_login(aluno.alu)
        self.salvar({"email": "b@uea.edu.br"})
        self.salvar({"email": "c@uea.edu.br"})
        link_b, link_c = (caminho_do_link(m) for m in mail.outbox)
        with avancar_relogio(horas=24, minutos=1):
            self.assertContains(self.client.get(link_b), mensagens.M09_LINK_EMAIL_INVALIDO)
        self.assertContains(self.client.post(link_c), mensagens.M07_EMAIL_ATUALIZADO)
        self.assertContains(self.client.post(link_b), mensagens.M09_LINK_EMAIL_INVALIDO)
        self.assertContains(self.client.post(link_c), mensagens.M09_LINK_EMAIL_INVALIDO)
        self.assertEqual(Usuarios.objects.get(pk=aluno.pk).usu_email, "c@uea.edu.br")

    def test_link_de_troca_adulterado(self):
        """M-09: link de troca alterado à mão."""
        resposta = self.client.get(reverse("cadastro:confirmar_email", args=["abc:def"]))
        self.assertContains(resposta, mensagens.M09_LINK_EMAIL_INVALIDO)

    def test_assinatura_disfarcada(self):
        """I7: o tipo vem dos bytes e a extensão precisa bater com ele."""
        docente = criar_docente_ativo()
        self.client.force_login(docente)
        for nome, conteudo in (("a.png", PDF), ("a.jpg", PNG), ("a.png", JPEG), ("a", PNG)):
            with self.subTest(nome=nome):
                resposta = self.salvar({"assinatura": arquivo(nome, conteudo, "image/png")})
                self.assertContains(resposta, mensagens.M04_ASSINATURA_FORMATO)
        self.assertIsNone(self.caminho_assinatura(docente))
        resposta = self.salvar({"assinatura": arquivo("a.JPEG", JPEG)})
        self.assertContains(resposta, mensagens.PERFIL_ATUALIZADO)
        self.assertTrue(self.caminho_assinatura(docente).endswith(".jpg"))

    def test_assinatura_so_do_proprio_usuario(self):
        """A11: a imagem sai pela rota assinatura, só para o dono; sem URL pública em /media/."""
        docente = criar_docente_ativo()
        self.client.force_login(docente)
        self.salvar({"assinatura": arquivo("a.png", PNG)})
        resposta = self.client.get(reverse("cadastro:assinatura"))
        self.assertEqual(resposta["Content-Type"], "image/png")
        self.assertEqual(b"".join(resposta.streaming_content), PNG)
        caminho = self.caminho_assinatura(docente)
        self.assertEqual(self.client.get(f"/media/{caminho}").status_code, 404)
        self.client.force_login(criar_docente_ativo())
        self.assertEqual(self.client.get(reverse("cadastro:assinatura")).status_code, 404)
        self.client.post(reverse("cadastro:sair"))
        resposta = self.client.get(reverse("cadastro:assinatura"))
        self.assertRedirects(resposta, f"/entrar/?next={reverse('cadastro:assinatura')}")

    def test_assinatura_anterior_apagada(self):
        """A11: a imagem anterior é apagada depois do commit."""
        docente = criar_docente_ativo()
        self.client.force_login(docente)
        with self.captureOnCommitCallbacks(execute=True):
            self.salvar({"assinatura": arquivo("a.png", PNG)})
        anterior = self.caminho_assinatura(docente)
        with self.captureOnCommitCallbacks(execute=True):
            self.salvar({"assinatura": arquivo("b.jpg", JPEG)})
        self.assertFalse(default_storage.exists(anterior))
        self.assertTrue(default_storage.exists(self.caminho_assinatura(docente)))

    def test_membro_externo_envia_assinatura(self):
        """FR-019: o Membro Externo também envia a assinatura."""
        membro = criar_membro_externo(email="ext@ufam.edu.br")
        self.client.force_login(membro)
        dados = {"email": "ext@ufam.edu.br", "titulacao": "Mestre", "instituicao": "UFAM"}
        self.salvar({**dados, "assinatura": arquivo("a.png", PNG)})
        caminho = MembrosExternos.objects.get(pk=membro.pk).mem_assinatura_path
        self.assertTrue(default_storage.exists(caminho))

    def test_falha_no_envio_da_troca_desfaz_tudo(self):
        """I5 e m13: falha no envio da troca mostra a M-17 e não salva nada."""
        membro = criar_membro_externo(email="ext@ufam.edu.br")
        self.client.force_login(membro)
        dados = {
            "email": "novo@ufam.edu.br",
            "titulacao": "Doutor",
            "instituicao": "UFAM",
            "assinatura": arquivo("a.png", PNG),
        }
        with mock.patch(
            "sigtcc.apps.cadastro.services.send_mail", side_effect=SMTPException("fora")
        ):
            resposta = self.salvar(dados)
        self.assertContains(resposta, mensagens.M17_FALHA_ENVIO)
        registro = MembrosExternos.objects.get(pk=membro.pk)
        self.assertEqual(registro.mem_titulacao, "Mestre")
        self.assertIsNone(registro.mem_assinatura_path)
        pasta = Path(self.pasta_midia) / "assinaturas"
        self.assertEqual(list(pasta.glob(f"{membro.pk}_*")), [])

    def test_perfil_tem_link_alterar_senha(self):
        """FR-012: "Meu perfil" leva a "Alterar senha"."""
        self.client.force_login(criar_docente_ativo())
        resposta = self.client.get(URL_PERFIL)
        self.assertContains(resposta, f'href="{reverse("cadastro:alterar_senha")}"')

    def test_perfil_exige_login(self):
        """Sem login, o perfil pede login."""
        self.assertRedirects(self.client.get(URL_PERFIL), f"/entrar/?next={URL_PERFIL}")


class NotificacoesTest(TesteAcesso):
    """Sino e central de notificações (cenários 4, 9 e 10; Q10, Q14). [US-38][RBN-CAD-13.2]"""

    def setUp(self):
        super().setUp()
        self.usuario = criar_docente_ativo()
        self.client.force_login(self.usuario)

    def nao_lidas(self):
        return Notificacoes.objects.filter(not_usu=self.usuario, not_lida=False).count()

    def abrir(self, notificacao, follow=True):
        url = reverse("cadastro:abrir_notificacao", args=[notificacao.pk])
        return self.client.get(url, follow=follow)

    def test_cenario4_abrir_notificacao(self):
        """Dado 3 não lidas, quando abre uma, então a tela relacionada e o contador vai a 2."""
        primeira = criar_notificacao(self.usuario, link="/painel/?origem=1")
        criar_notificacao(self.usuario)
        criar_notificacao(self.usuario)
        resposta = self.abrir(primeira)
        self.assertEqual(resposta.redirect_chain[-1][0], "/painel/?origem=1")
        self.assertContains(resposta, '<span class="badge" data-contador>2</span>', html=False)
        self.assertEqual(self.nao_lidas(), 2)

    def test_cenario9_item_removido(self):
        """Dado notificação de item removido, quando a abre, então a mensagem e marca lida (Q10)."""
        notificacao = criar_notificacao(self.usuario, link="/defesa/convites/999/")
        resposta = self.abrir(notificacao)
        self.assertEqual(resposta.redirect_chain[-1][0], URL_NOTIFICACOES)
        self.assertContains(resposta, mensagens.ITEM_INDISPONIVEL)
        self.assertEqual(self.nao_lidas(), 0)

    def test_cenario10_marcar_como_lidas(self):
        """Dado 5 não lidas, quando clica em "Marcar como lidas", então o contador zera."""
        for _ in range(5):
            criar_notificacao(self.usuario)
        outro = criar_docente_ativo()
        criar_notificacao(outro)
        resposta = self.client.post(URL_MARCAR, follow=True)
        self.assertEqual(self.nao_lidas(), 0)
        self.assertNotContains(resposta, "data-contador")
        self.assertEqual(Notificacoes.objects.filter(not_usu=outro, not_lida=False).count(), 1)

    def test_marcar_lidas_so_por_post(self):
        """ "Marcar como lidas" muda dados: só por POST."""
        self.assertEqual(self.client.get(URL_MARCAR).status_code, 405)

    def test_sem_notificacoes(self):
        """US-38 A2: "Você não tem notificações"."""
        self.assertContains(self.client.get(URL_NOTIFICACOES), mensagens.SEM_NOTIFICACOES)

    def test_notificacoes_paginadas_de_20(self):
        """Q14: 20 por página, com ?pagina=."""
        for _ in range(25):
            criar_notificacao(self.usuario)
        resposta = self.client.get(URL_NOTIFICACOES)
        self.assertEqual(resposta.content.decode().count("data-notificacao"), 20)
        resposta = self.client.get(URL_NOTIFICACOES + "?pagina=2")
        self.assertEqual(resposta.content.decode().count("data-notificacao"), 5)

    def test_notificacoes_da_mais_recente_para_a_mais_antiga(self):
        """FR-022 e Q14: da mais recente para a mais antiga, com data e hora."""
        base = datetime(2026, 10, 1, 9, 30)
        criar_notificacao(self.usuario, mensagem="Antiga", data_hora=base)
        criar_notificacao(self.usuario, mensagem="Recente", data_hora=base + timedelta(days=2))
        criar_notificacao(self.usuario, mensagem="Meio", data_hora=base + timedelta(days=1))
        html = self.client.get(URL_NOTIFICACOES).content.decode()
        self.assertLess(html.index("Recente"), html.index("Meio"))
        self.assertLess(html.index("Meio"), html.index("Antiga"))
        self.assertIn("01/10/2026 09:30", html)

    def test_link_externo_na_notificacao_nao_e_seguido(self):
        """A12: endereço externo não é seguido; aparece "Este item não está mais disponível"."""
        for link in ("https://outro.site/painel/", "//outro.site/painel/", "painel/"):
            with self.subTest(link=link):
                resposta = self.abrir(criar_notificacao(self.usuario, link=link))
                self.assertEqual(resposta.redirect_chain[-1][0], URL_NOTIFICACOES)
                self.assertContains(resposta, mensagens.ITEM_INDISPONIVEL)

    def test_notificacao_sem_link_volta_a_central(self):
        """Notificação sem tela relacionada: marca lida e volta à central."""
        notificacao = criar_notificacao(self.usuario)
        resposta = self.abrir(notificacao)
        self.assertEqual(resposta.redirect_chain[-1][0], URL_NOTIFICACOES)
        self.assertEqual(self.nao_lidas(), 0)

    def test_notificacao_de_outro_usuario_404(self):
        """A notificação de outra conta não abre nem é marcada."""
        alheia = criar_notificacao(criar_docente_ativo())
        self.assertEqual(self.abrir(alheia, follow=False).status_code, 404)
        alheia.refresh_from_db()
        self.assertFalse(alheia.not_lida)

    def test_base_cenario4_layout_completo(self):
        """História 6, cenário 4: "Meu perfil" e o link do sino para a central (tasks H1)."""
        criar_notificacao(self.usuario)
        resposta = self.client.get(reverse("cadastro:painel"))
        self.assertContains(resposta, f'href="{URL_PERFIL}"')
        self.assertContains(resposta, mensagens.MEU_PERFIL)
        self.assertContains(resposta, f'class="iconbtn" href="{URL_NOTIFICACOES}"')
        self.assertContains(resposta, ">Sair</button>")
