"""Testes de aceite da US-08: importação de alunos por CSV ou XLSX (spec 004, diagrama "Matrícula
por CSV").

Cenários 4, 5, 7, 8 e 14 da US-08, mais as Clarifications (Q2, Q4, Q11, Q13) e a revisão (B-2,
B-3, N3, N4, N7, I-10).

[US-08][RBN-CAD-05.2][RBN-CAD-05.5][RBN-CAD-05.7][FR-016]-[FR-018][SC-003][Q2][Q4][Q11][Q13]
"""

import io
import time
import zipfile

import openpyxl
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import StatusTCC, StatusTurma
from sigtcc.apps.cadastro.models import Alunos, AlunosTurmas, Usuarios
from sigtcc.apps.cadastro.tests.apoio_acesso import avancar_relogio, criar_docente_ativo
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    TesteTurmas,
    arquivo_csv,
    arquivo_xlsx,
    criar_turma_de,
    matricular_aluno,
)


def linhas_validas(quantidade, inicio=2026100000, curso="EST08MCPD"):
    """Linhas válidas com matrículas sequenciais."""
    return [
        (f"{inicio + n:010d}", f"Aluno Numero {chr(65 + n % 26)}", curso) for n in range(quantidade)
    ]


class ImportacaoTest(TesteTurmas):
    """Importação com prévia presa à turma e confirmação. [US-08][RBN-CAD-05.2]"""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=EC)
        self.client.force_login(self.professor)

    def enviar(self, arquivo, turma=None):
        url = reverse("cadastro:importar", args=[(turma or self.turma).pk])
        return self.client.post(url, {"arquivo": arquivo})

    def token(self):
        return self.client.session["importacao"]["token"]

    def confirmar(self, turma=None, token=None, follow=True):
        url = reverse("cadastro:importar_confirmar", args=[(turma or self.turma).pk])
        return self.client.post(url, {"token": token or self.token()}, follow=follow)

    def matriculados(self, turma=None):
        return AlunosTurmas.objects.filter(mat_tur=turma or self.turma).count()

    # ------------------------------------------------------------------ cenários da US-08

    def test_cenario4_linhas_validas_e_invalidas(self):
        """Dado 30 linhas, 2 com 9 dígitos, quando confirma, então 28 e as 2 com o motivo."""
        linhas = linhas_validas(28) + [
            ("202600001", "Nove Digitos A", "EST08MCPD"),
            ("202600002", "Nove Digitos B", "EST08MCPD"),
        ]
        previa = self.enviar(arquivo_csv(linhas))
        self.assertEqual(self.matriculados(), 0)
        self.assertContains(previa, mensagens.CONFIRMAR_IMPORTACAO)
        resposta = self.confirmar()
        self.assertEqual(self.matriculados(), 28)
        self.assertContains(resposta, mensagens.MT15_RESUMO_IMPORTACAO.format(n=28, r=2, c=0))
        self.assertContains(resposta, mensagens.MATRICULA_FORMATO, count=2)
        self.assertContains(resposta, "Linha 30")
        self.assertContains(resposta, "Linha 31")

    def test_cenario5_arquivo_pdf(self):
        pdf = SimpleUploadedFile("lista.pdf", b"%PDF-1.4 conteudo", content_type="application/pdf")
        resposta = self.enviar(pdf)
        self.assertContains(resposta, mensagens.ARQUIVO_FORA_DO_MODELO)
        self.assertNotIn("importacao", self.client.session)

    def test_cenario7_codigo_reconhecido(self):
        self.enviar(arquivo_csv([("2026100001", "Ana Maria", "EST08MCPD")]))
        resposta = self.confirmar()
        self.assertContains(resposta, mensagens.MT15_RESUMO_IMPORTACAO.format(n=1, r=0, c=0))
        pagina = self.client.get(reverse("cadastro:turma", args=[self.turma.pk]))
        self.assertContains(pagina, "Engenharia de Computação")

    def test_cenario8_codigo_nao_reconhecido(self):
        self.enviar(arquivo_csv([("2026100001", "Ana Maria", "EST99XXXX")]))
        resposta = self.confirmar()
        self.assertContains(resposta, mensagens.MT15_RESUMO_IMPORTACAO.format(n=1, r=0, c=1))
        pagina = self.client.get(reverse("cadastro:turma", args=[self.turma.pk]))
        self.assertContains(pagina, mensagens.CURSO_NAO_RECONHECIDO)

    def test_cenario14_xlsx_de_3_mb(self):
        grande = SimpleUploadedFile("alunos.xlsx", b"PK\x03\x04" + b"\x00" * (3 * 1024 * 1024))
        self.assertContains(self.enviar(grande), mensagens.ARQUIVO_FORA_DO_MODELO)

    # ------------------------------------------------------------------ formatos (Q4, Q11, Q13)

    def test_q11_csv_ponto_e_virgula_e_virgula(self):
        for separador in (";", ","):
            with self.subTest(separador=separador):
                turma = criar_turma_de(self.professor)
                self.enviar(
                    arquivo_csv(
                        linhas_validas(2, inicio=2026300000 + ord(separador) * 10),
                        separador=separador,
                    ),
                    turma=turma,
                )
                self.confirmar(turma=turma)
                self.assertEqual(self.matriculados(turma), 2)

    def test_q11_utf8_bom_e_windows1252_com_acentos(self):
        for codificacao, inicio in (("utf-8-sig", 2026400000), ("cp1252", 2026500000)):
            with self.subTest(codificacao=codificacao):
                turma = criar_turma_de(self.professor)
                linhas = [(f"{inicio:010d}", "João Conceição Ávila", "EST08MCPD")]
                self.enviar(arquivo_csv(linhas, codificacao=codificacao), turma=turma)
                self.confirmar(turma=turma)
                aluno = Alunos.objects.select_related("alu").get(alu_matricula=f"{inicio:010d}")
                self.assertEqual(aluno.alu.usu_nome, "João Conceição Ávila")

    def test_q11_xlsx_so_primeira_planilha(self):
        self.enviar(arquivo_xlsx(linhas_validas(3), planilhas=2))
        self.confirmar()
        self.assertEqual(self.matriculados(), 3)
        self.assertFalse(Alunos.objects.filter(alu_matricula="9999999999").exists())

    def test_xlsx_matricula_numerica_sem_ponto_zero(self):
        self.enviar(arquivo_xlsx([(2026100001, "Ana Maria", "EST08MCPD")]))
        self.confirmar()
        self.assertTrue(Alunos.objects.filter(alu_matricula="2026100001").exists())

    def test_cabecalhos_em_outra_ordem_e_maiusculas(self):
        arquivo = arquivo_csv(
            [("EST08MCPD", "Ana Maria", "2026100001")],
            cabecalho=("CURSO", " nome completo ", "Matrícula"),
        )
        self.enviar(arquivo)
        self.confirmar()
        self.assertTrue(Alunos.objects.filter(alu_matricula="2026100001").exists())

    def test_cabecalho_faltando_fora_do_modelo(self):
        arquivo = arquivo_csv([("2026100001", "Ana Maria")], cabecalho=("Matrícula", "Nome"))
        self.assertContains(self.enviar(arquivo), mensagens.ARQUIVO_FORA_DO_MODELO)

    def test_q13_201_linhas_fora_do_modelo_e_200_aceitas(self):
        self.assertContains(
            self.enviar(arquivo_csv(linhas_validas(201))), mensagens.ARQUIVO_FORA_DO_MODELO
        )
        self.assertContains(
            self.enviar(arquivo_csv(linhas_validas(200))), mensagens.CONFIRMAR_IMPORTACAO
        )

    def test_linhas_vazias_ignoradas(self):
        self.enviar(
            arquivo_csv(
                [
                    ("2026100001", "Ana Maria", "EST08MCPD"),
                    ("", "", ""),
                    ("2026100002", "Bia Lima", "EST08MCPD"),
                ]
            )
        )
        resposta = self.confirmar()
        self.assertContains(resposta, mensagens.MT15_RESUMO_IMPORTACAO.format(n=2, r=0, c=0))

    def test_zip_bomb_fora_do_modelo(self):
        """B-3: XLSX que se expande demais (soma acima de 20 MB ou razão acima de 100)."""
        saida = io.BytesIO()
        with zipfile.ZipFile(saida, "w", zipfile.ZIP_DEFLATED) as zipado:
            zipado.writestr("xl/sharedStrings.xml", b"A" * (21 * 1024 * 1024))
        bomba = SimpleUploadedFile("alunos.xlsx", saida.getvalue())
        self.assertLess(bomba.size, 2 * 1024 * 1024)
        self.assertContains(self.enviar(bomba), mensagens.ARQUIVO_FORA_DO_MODELO)

    def test_defusedxml_em_uso(self):
        """N7: o openpyxl usa o defusedxml (XML seguro)."""
        self.assertTrue(openpyxl.xml.DEFUSEDXML)

    def test_arquivo_corrompido_fora_do_modelo(self):
        corrompidos = (
            SimpleUploadedFile("alunos.csv", b"\x00\x01\x02\xff\xfe" * 50),
            SimpleUploadedFile("alunos.xlsx", b"PK\x03\x04 isto nao e zip"),
            SimpleUploadedFile("alunos.csv", b""),
        )
        for arquivo in corrompidos:
            with self.subTest(nome=arquivo.name, tamanho=arquivo.size):
                self.assertContains(self.enviar(arquivo), mensagens.ARQUIVO_FORA_DO_MODELO)

    # ------------------------------------------------------------------ prévia e confirmação

    def test_previa_sem_gravar_nada(self):
        contas = Usuarios.objects.count()
        self.enviar(arquivo_csv(linhas_validas(3)))
        self.assertEqual(Usuarios.objects.count(), contas)
        self.assertEqual(self.matriculados(), 0)

    def test_previa_classifica_como_o_diagrama(self):
        """Inválida, já na turma, já cadastrada, nova, recusa da Q7, aviso e código."""
        matricular_aluno(self.turma, matricula="2026100002")
        outra = criar_turma_de(criar_docente_ativo(), identificador="OUTRA_T09")
        matricular_aluno(outra, matricula="2026100003", status_tcc=StatusTCC.EM_ANDAMENTO)
        arquivada = criar_turma_de(criar_docente_ativo(), status=StatusTurma.ARQUIVADA)
        matricular_aluno(arquivada, matricula="2026100004", status_tcc=StatusTCC.REPROVADO)
        linhas = [
            ("123", "Ana Maria", "EST08MCPD"),
            ("2026100002", "Bia Lima", "EST08MCPD"),
            ("2026100003", "Caio Rocha", "EST08MCPD"),
            ("2026100004", "Davi Melo", "EST08MCPD"),
            ("2026100005", "Eva Lins", "EST99XXXX"),
            ("2026100006", "Fabio Reis", "EST31MSII"),
        ]
        previa = self.enviar(arquivo_csv(linhas))
        self.assertContains(previa, mensagens.MATRICULA_FORMATO)
        self.assertContains(previa, mensagens.ALUNO_JA_NA_TURMA)
        self.assertContains(previa, mensagens.MT26_TCC_EM_CURSO.format(identificador="OUTRA_T09"))
        self.assertContains(previa, "Já cadastrado")
        self.assertContains(previa, "Novo")
        self.assertContains(previa, mensagens.CURSO_NAO_RECONHECIDO)
        self.assertContains(
            previa,
            mensagens.MT13_CURSO_DIVERGENTE.format(
                curso_aluno="Sistemas de Informação", curso_turma="Engenharia de Computação"
            ),
        )

    def test_matricula_repetida_no_arquivo(self):
        linhas = [
            ("2026100001", "Ana Maria", "EST08MCPD"),
            ("2026100001", "Ana Maria", "EST08MCPD"),
        ]
        self.assertContains(self.enviar(arquivo_csv(linhas)), mensagens.ALUNO_JA_NA_TURMA)
        resposta = self.confirmar()
        self.assertContains(resposta, mensagens.MT15_RESUMO_IMPORTACAO.format(n=1, r=1, c=0))

    def test_b2_confirmar_com_token_de_outra_turma_recusa(self):
        """B-2: prévia da turma B confirmada na URL da turma A não grava nada."""
        turma_b = criar_turma_de(self.professor)
        self.enviar(arquivo_csv(linhas_validas(2)), turma=self.turma)
        self.enviar(arquivo_csv(linhas_validas(2, inicio=2026600000)), turma=turma_b)
        resposta = self.confirmar(turma=self.turma)
        self.assertContains(resposta, mensagens.MT32_PREVIA_INVALIDA)
        self.assertEqual(self.matriculados(self.turma), 0)
        self.assertEqual(self.matriculados(turma_b), 0)

    def test_b2_confirmar_com_token_errado_sem_previa_ou_vencida(self):
        self.enviar(arquivo_csv(linhas_validas(2)))
        self.assertContains(self.confirmar(token="outro"), mensagens.MT32_PREVIA_INVALIDA)
        token = self.token()
        with avancar_relogio(minutos=31):
            self.assertContains(self.confirmar(token=token), mensagens.MT32_PREVIA_INVALIDA)
        self.assertContains(self.confirmar(token="qualquer"), mensagens.MT32_PREVIA_INVALIDA)
        self.assertEqual(self.matriculados(), 0)

    def test_n3_segundo_post_nao_grava_nem_troca_resumo(self):
        """N3: o mesmo token confirmado duas vezes (POST simultâneo) só grava uma vez."""
        self.enviar(arquivo_csv(linhas_validas(2)))
        token = self.token()
        sessao = self.client.session
        dados_da_previa = dict(sessao["importacao"])
        self.confirmar(token=token)
        # Simula a segunda requisição, que leu a sessão antes da primeira salvar.
        sessao = self.client.session
        sessao["importacao"] = dados_da_previa
        sessao.save()
        resposta = self.confirmar(token=token)
        self.assertEqual(
            resposta.redirect_chain[-1][0], reverse("cadastro:turma", args=[self.turma.pk])
        )
        self.assertNotContains(resposta, mensagens.MT15_RESUMO_IMPORTACAO.format(n=0, r=2, c=0))
        self.assertEqual(self.matriculados(), 2)

    def test_f5_no_resumo_nao_repete(self):
        self.enviar(arquivo_csv(linhas_validas(2)))
        resposta = self.confirmar()
        url_resumo = resposta.redirect_chain[-1][0]
        self.assertEqual(url_resumo, reverse("cadastro:importar_resumo", args=[self.turma.pk]))
        segunda = self.client.get(url_resumo)
        self.assertEqual(segunda.status_code, 302)
        self.assertEqual(self.matriculados(), 2)

    def test_n4_abrir_outra_turma_nao_apaga_previa(self):
        outra = criar_turma_de(self.professor)
        self.enviar(arquivo_csv(linhas_validas(2)))
        self.client.get(reverse("cadastro:turma", args=[outra.pk]))
        self.confirmar()
        self.assertEqual(self.matriculados(), 2)

    def test_cancelar_apaga_previa(self):
        self.enviar(arquivo_csv(linhas_validas(2)))
        token = self.token()
        self.client.post(reverse("cadastro:importar_cancelar", args=[self.turma.pk]))
        self.assertNotIn("importacao", self.client.session)
        self.assertContains(self.confirmar(token=token), mensagens.MT32_PREVIA_INVALIDA)

    def test_previa_guarda_so_o_minimo(self):
        """I-10: das linhas com erro, a sessão guarda só o número e o motivo."""
        self.enviar(
            arquivo_csv(
                [("123", "Nome Secreto", "EST08MCPD"), ("2026100001", "Ana Maria", "EST08MCPD")]
            )
        )
        previa = self.client.session["importacao"]
        self.assertEqual(previa["erros"], [[2, mensagens.MATRICULA_FORMATO]])
        self.assertNotIn("Nome Secreto", str(previa))
        self.assertEqual(previa["linhas"], [[3, "2026100001", "Ana Maria", "EST08MCPD"]])

    def test_q2_linha_que_falha_na_confirmacao_nao_desfaz_outras(self):
        """Q2: aluno matriculado noutra turma entre a prévia e a confirmação vira rejeitada."""
        self.enviar(arquivo_csv(linhas_validas(3)))
        outra = criar_turma_de(criar_docente_ativo(), identificador="NOMEIO_T01")
        aluno = Alunos.objects.filter(alu_matricula="2026100001").first()
        self.assertIsNone(aluno)
        matricular_aluno(outra, matricula="2026100001", status_tcc=StatusTCC.EM_ANDAMENTO)
        resposta = self.confirmar()
        self.assertEqual(self.matriculados(), 2)
        self.assertContains(
            resposta, mensagens.MT26_TCC_EM_CURSO.format(identificador="NOMEIO_T01")
        )

    def test_resumo_mt15_com_contagens(self):
        linhas = linhas_validas(2) + [
            ("2026100099", "Eva Lins", "EST99XXXX"),
            ("abc", "Fabio Reis", "EST08MCPD"),
        ]
        self.enviar(arquivo_csv(linhas))
        resposta = self.confirmar()
        self.assertContains(resposta, mensagens.MT15_RESUMO_IMPORTACAO.format(n=3, r=1, c=1))

    def test_modelo_importacao_csv_utf8_bom_ponto_e_virgula(self):
        resposta = self.client.get(reverse("cadastro:modelo_importacao"))
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("modelo_importacao_alunos.csv", resposta["Content-Disposition"])
        conteudo = resposta.content
        self.assertTrue(conteudo.startswith(b"\xef\xbb\xbf"))
        texto = conteudo.decode("utf-8-sig").splitlines()
        self.assertEqual(texto[0], "Matrícula;Nome Completo;Curso")
        self.assertIn(";EST08MCPD", texto[1])

    def test_importacao_em_turma_arquivada(self):
        arquivada = criar_turma_de(self.professor, status=StatusTurma.ARQUIVADA)
        resposta = self.client.post(
            reverse("cadastro:importar", args=[arquivada.pk]),
            {"arquivo": arquivo_csv(linhas_validas(1))},
            follow=True,
        )
        self.assertContains(resposta, mensagens.MT25_TURMA_ARQUIVADA)

    def test_sc003_60_linhas_em_ate_10_segundos(self):
        """SC-003 (RAN-CAD-05): 60 alunos do envio ao resumo em até 10 segundos (com margem)."""
        inicio = time.monotonic()
        self.enviar(arquivo_csv(linhas_validas(60)))
        self.confirmar()
        decorrido = time.monotonic() - inicio
        self.assertEqual(self.matriculados(), 60)
        self.assertLess(decorrido, 10)
