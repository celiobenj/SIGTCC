"""Testes do comando criar_coordenadores (história 6 da spec 002; tasks T021).

Cenários 1 a 4 da história 6 (RNF de Instalabilidade do RAN-CAD-01), CSV com BOM, modo de um
curso, saída sem e-mail, DEBUG = False e log com autor "sistema".

[RAN-CAD-01][RBN-CAD-06.2][FR-045][FR-046][research C17]
"""

import io
import os
import tempfile

from django.core import mail
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings
from django.urls import reverse

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import StatusConta
from sigtcc.apps.cadastro.models import Coordenadores, Usuarios
from sigtcc.apps.cadastro.tests.apoio_contas import EC, LC, SI, TesteContas, curso, docente_de

LINHAS = [
    (EC, "Ana Engenharia", "ana.ec@uea.edu.br", "Doutor"),
    (SI, "Bruno Sistemas", "bruno.si@uea.edu.br", "Mestre"),
    (LC, "Carla Licenciatura", "carla.lc@uea.edu.br", "Doutor"),
]


class ComandoCoordenadoresTest(TesteContas):
    """História 6, cenários 1 a 4. [FR-045][FR-046]"""

    def _csv(self, linhas, bom=False):
        """CSV temporário (fora do repositório) com as linhas pedidas."""
        arquivo = tempfile.NamedTemporaryFile(
            "w", suffix=".csv", delete=False, encoding="utf-8-sig" if bom else "utf-8", newline=""
        )
        arquivo.write("curso;nome;email;titulacao\n")
        for linha in linhas:
            arquivo.write(";".join(linha) + "\n")
        arquivo.close()
        self.addCleanup(os.remove, arquivo.name)
        return arquivo.name

    def _rodar(self, *args, **opcoes):
        saida = io.StringIO()
        call_command("criar_coordenadores", *args, stdout=saida, **opcoes)
        return saida.getvalue()

    def test_cenario_1_cria_os_tres_coordenadores_sem_email(self):
        saida = self._rodar(arquivo=self._csv(LINHAS))
        for nome_curso, _nome, email, _titulacao in LINHAS:
            conta = Usuarios.objects.get(usu_email=email)
            self.assertEqual(conta.usu_status, StatusConta.AGUARDANDO_ATIVACAO)
            self.assertEqual(conta.docentes.doc_cur, curso(nome_curso))
            self.assertEqual(
                Coordenadores.objects.get(cor_doc_id=conta.pk).cor_cur, curso(nome_curso)
            )
            self.assertIn(f"{nome_curso}: criado", saida)
        self.assertEqual(mail.outbox, [])

    def test_cenario_2_primeiro_acesso_e_menu_cadastros(self):
        self._rodar(arquivo=self._csv(LINHAS[:1]))
        resposta = self.client.post(
            reverse("cadastro:primeiro_acesso_email"), {"email": "ana.ec@uea.edu.br"}, follow=True
        )
        self.assertContains(resposta, mensagens.LINK_ATIVACAO_ENVIADO)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["ana.ec@uea.edu.br"])
        conta = Usuarios.objects.get(usu_email="ana.ec@uea.edu.br")
        conta.set_password("Senha1234")
        conta.usu_status = StatusConta.ATIVA
        conta.save()
        self.client.force_login(conta)
        resposta = self.client.get(reverse("cadastro:painel"))
        self.assertContains(resposta, "Cadastros")
        self.assertContains(resposta, reverse("cadastro:contas_docentes"))

    def test_cenario_3_rodar_de_novo_nao_duplica(self):
        arquivo = self._csv(LINHAS)
        self._rodar(arquivo=arquivo)
        saida = self._rodar(arquivo=arquivo)
        for nome_curso, *_ in LINHAS:
            self.assertIn(f"{nome_curso}: recusado: {mensagens.CURSO_JA_TEM_COORDENADOR}", saida)
        self.assertEqual(Coordenadores.objects.count(), 3)
        self.assertEqual(Usuarios.objects.filter(docentes__isnull=False).count(), 3)

    def test_cenario_4_dados_invalidos_recusam_so_o_curso(self):
        docente_de(EC, email="ocupado@uea.edu.br")
        linhas = [
            (EC, "Ana Engenharia", "ocupado@uea.edu.br", "Doutor"),
            (SI, "Bruno Sistemas", "bruno@gmail.com", "Mestre"),
            (LC, "Carla 2", "carla.lc@uea.edu.br", "Livre-docente"),
        ]
        saida = self._rodar(arquivo=self._csv(linhas))
        self.assertIn(f"{EC}: recusado: {mensagens.EMAIL_JA_CADASTRADO}", saida)
        self.assertIn(f"{SI}: recusado: {mensagens.EMAIL_INSTITUCIONAL_CONTAS}", saida)
        self.assertIn(f"{LC}: recusado: {mensagens.NOME_INVALIDO}", saida)
        self.assertEqual(Coordenadores.objects.count(), 0)

    def test_um_curso_recusado_nao_impede_os_outros(self):
        linhas = [LINHAS[0], (SI, "Bruno Sistemas", "bruno@gmail.com", "Mestre"), LINHAS[2]]
        saida = self._rodar(arquivo=self._csv(linhas))
        self.assertIn(f"{EC}: criado", saida)
        self.assertIn(f"{LC}: criado", saida)
        self.assertEqual(Coordenadores.objects.count(), 2)

    def test_csv_com_bom_do_excel(self):
        saida = self._rodar(arquivo=self._csv(LINHAS[:1], bom=True))
        self.assertIn(f"{EC}: criado", saida)

    def test_modo_um_curso_pelas_opcoes(self):
        saida = self._rodar(
            curso=SI, nome="Bruno Sistemas", email="bruno.si@uea.edu.br", titulacao="Mestre"
        )
        self.assertIn(f"{SI}: criado", saida)

    def test_saida_sem_email(self):
        saida = self._rodar(arquivo=self._csv(LINHAS))
        for _curso, _nome, email, _titulacao in LINHAS:
            self.assertNotIn(email, saida)

    @override_settings(DEBUG=False)
    def test_funciona_com_debug_false(self):
        saida = self._rodar(arquivo=self._csv(LINHAS[:1]))
        self.assertIn(f"{EC}: criado", saida)

    def test_log_com_autor_sistema(self):
        with self.assertLogs("sigtcc.acesso", "INFO") as log:
            self._rodar(arquivo=self._csv(LINHAS[:1]))
        self.assertTrue(
            any("CONTA_CRIADA" in linha and "autor=sistema" in linha for linha in log.output)
        )

    def test_sem_dados_ou_colunas_erradas(self):
        with self.assertRaises(CommandError):
            self._rodar()
        arquivo = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
        arquivo.write("nome;email\nAna;ana@uea.edu.br\n")
        arquivo.close()
        self.addCleanup(os.remove, arquivo.name)
        with self.assertRaises(CommandError):
            self._rodar(arquivo=arquivo.name)
