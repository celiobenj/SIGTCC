"""US-28, Ata Final e Folha de Aprovação (User Story 1 da spec 009).

Parte de serviço (tasks T013): situacao_da_ata nos 3 casos e com o arquivo do Coordenador
ausente (Q-140); dados_da_folha sem nenhuma nota; dados_da_ata com o suplente acionado na linha
do titular; a data dos documentos é a da defesa (def_data; P12).

Parte de view (tasks T022): um teste por cenário 1.1 a 1.19, o Edge Case "Coordenador cadastra a
assinatura depois da liberação" e o parâmetro `origem` com valor livre. O texto dos PDFs é lido
com apoio_documentos.texto_do_pdf e as imagens com numero_de_imagens (pypdf).

[US-28][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-07.3][RBN-CAD-13.1] (spec 009, tasks T013 e T022)
"""

import os
from datetime import date, time
from unittest import mock

from django.conf import settings
from django.core.files.storage import default_storage
from django.urls import reverse

from sigtcc.apps.cadastro import services
from sigtcc.apps.cadastro.choices import DescricaoTurma, StatusTCC
from sigtcc.apps.cadastro.models import Notificacoes, TCCs
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_secretaria
from sigtcc.apps.defesa import mensagens, pdf, services_avaliacoes, services_documentos
from sigtcc.apps.defesa.choices import PapelBanca, Parecer, StatusSessao
from sigtcc.apps.defesa.models import BancaDefesa
from sigtcc.apps.defesa.tests.apoio_avaliacao import (
    TesteAvaliacao,
    assinatura_no_perfil,
    enviar,
    lancar,
    sessao_com_banca,
)
from sigtcc.apps.defesa.tests.apoio_defesa import agendar_sessao_de, avancar_para, docente
from sigtcc.apps.defesa.tests.apoio_documentos import (
    copia_de_assinatura,
    liberar,
    numero_de_imagens,
    preparar_liberacao,
    sessao_liberada,
    texto_do_pdf,
)

DATA_DA_DEFESA = date(2026, 11, 20)


def chaves(valor):
    """Todas as chaves de dicionários aninhados (em listas e dicionários). [US-28]"""
    if isinstance(valor, dict):
        encontradas = set(valor)
        for item in valor.values():
            encontradas |= chaves(item)
        return encontradas
    if isinstance(valor, (list, tuple)):
        encontradas = set()
        for item in valor:
            encontradas |= chaves(item)
        return encontradas
    return set()


class TesteSituacaoDaAta(TesteAvaliacao):
    """situacao_da_ata: E2 só com caminho vazio ou curso sem Coordenador (FR-006; Q-140).
    [US-28][RBN-DEF-07.1][RBN-CAD-13.1]
    """

    def test_coordenador_com_assinatura(self):
        cenario = sessao_liberada()
        self.assertIsNone(services_documentos.situacao_da_ata(cenario["sessao"]))

    def test_curso_sem_coordenador(self):
        cenario = sessao_liberada(com_coordenador=False)
        self.assertEqual(
            services_documentos.situacao_da_ata(cenario["sessao"]),
            services_documentos.SEM_COORDENADOR,
        )

    def test_coordenador_sem_assinatura(self):
        cenario = sessao_liberada(assinatura_coordenador=False)
        self.assertEqual(
            services_documentos.situacao_da_ata(cenario["sessao"]),
            services_documentos.SEM_ASSINATURA,
        )

    def test_arquivo_ausente_nao_e_e2_e_a_ata_sai_sem_a_imagem(self):
        """Q-140: caminho gravado e arquivo apagado do disco (deploy no Render): sem E2; a Ata
        sai sem a imagem do Coordenador e a ausência vai ao log. [US-28][RBN-DEF-07.1]
        """
        cenario = sessao_liberada()
        caminho = services.caminho_da_assinatura(cenario["coordenador"])
        default_storage.delete(caminho)
        self.assertIsNone(services_documentos.situacao_da_ata(cenario["sessao"]))
        with self.assertLogs("sigtcc.defesa", level="WARNING") as log:
            dados = services_documentos.dados_da_ata(cenario["sessao"])
        self.assertEqual(dados["coordenador"]["nome"], cenario["coordenador"].usu_nome)
        self.assertIsNone(dados["coordenador"]["assinatura"])
        self.assertIn(caminho, "".join(log.output))
        # As assinaturas dos membros continuam (cópias da avaliação presentes).
        self.assertTrue(all(membro["assinatura"] for membro in dados["membros"]))


class TesteDadosDaAta(TesteAvaliacao):
    """dados_da_ata (FR-001; FR-008). [US-28][RBN-DEF-07.1]"""

    def test_tcc_2_com_notas_assinaturas_e_coordenador(self):
        cenario = sessao_liberada()
        dados = services_documentos.dados_da_ata(cenario["sessao"])
        self.assertEqual(
            dados["titulo_documento"],
            "Ata Final de Avaliação de Trabalho de Conclusão de Curso II",
        )
        self.assertEqual(dados["aluno"], cenario["aluno"].usu_nome)
        self.assertEqual(dados["titulo"], cenario["tcc"].tcc_titulo)
        self.assertEqual(dados["curso"], cenario["tcc"].tcc_tur.tur_cur.cur_nome)
        self.assertEqual(dados["nota_final"], "8,0")
        self.assertEqual(dados["parecer"], Parecer.APROVADO)
        self.assertIsNone(dados["observacao_qualis"])
        self.assertEqual(
            [(m["papel"], m["nome"]) for m in dados["membros"]],
            [
                ("Orientador (Presidente)", cenario["orientador"].usu_nome),
                ("1º Avaliador", cenario["av1"].usu_nome),
                ("2º Avaliador", cenario["av2"].usu_nome),
            ],
        )
        for membro in dados["membros"]:
            self.assertEqual(membro["nota"], "8,0")
            self.assertTrue(membro["titulacao"])
            self.assertTrue(membro["assinatura"].lstrip("/").startswith("media/assinaturas_banca/"))
        self.assertTrue(
            dados["coordenador"]["assinatura"].lstrip("/").startswith("media/assinaturas/")
        )

    def test_tcc_1_tem_titulo_i(self):
        cenario = sessao_liberada(etapa=DescricaoTurma.TCC_1)
        dados = services_documentos.dados_da_ata(cenario["sessao"])
        self.assertEqual(
            dados["titulo_documento"],
            "Ata Final de Avaliação de Trabalho de Conclusão de Curso I",
        )
        self.assertEqual(dados["parecer"], Parecer.APROVADO_PARA_TCC_2)

    def test_suplente_acionado_na_linha_do_titular(self):
        """US-28 cenário 6 (serviço): o suplente acionado ocupa a linha do 2º Avaliador
        substituído; o ausente não aparece. [US-28][RBN-DEF-07.1][RBN-DEF-02.2]
        """
        cenario = sessao_liberada(suplente_acionado=True)
        dados = services_documentos.dados_da_ata(cenario["sessao"])
        nomes = [membro["nome"] for membro in dados["membros"]]
        self.assertEqual(dados["membros"][2]["papel"], "2º Avaliador")
        self.assertEqual(dados["membros"][2]["nome"], cenario["suplente"].usu_nome)
        self.assertNotIn(cenario["ausente"].usu_nome, nomes)
        self.assertEqual(len(nomes), 3)

    def test_data_e_a_da_defesa(self):
        """P12: a data é def_data, não a da liberação. [US-28][RBN-DEF-07.1][RBN-DEF-07.2]"""
        cenario = sessao_liberada()
        sessao = cenario["sessao"]
        self.assertEqual(sessao.def_data, DATA_DA_DEFESA)
        self.assertNotEqual(sessao.def_data_liberacao_resultado.date(), DATA_DA_DEFESA)
        self.assertEqual(services_documentos.dados_da_ata(sessao)["data_defesa"], "20/11/2026")
        self.assertEqual(
            services_documentos.dados_da_folha(sessao)["local_e_data"],
            "Manaus, 20 de novembro de 2026",
        )


class TesteDadosDaFolha(TesteAvaliacao):
    """dados_da_folha e folha_aplicavel (FR-002 a FR-004; SC-001). [US-28][RBN-DEF-07.2]"""

    def test_sem_nenhuma_chave_de_nota(self):
        cenario = sessao_liberada()
        dados = services_documentos.dados_da_folha(cenario["sessao"])
        for chave in chaves(dados):
            with self.subTest(chave=chave):
                self.assertNotIn("nota", chave)
                self.assertNotIn("media", chave)
        self.assertEqual(
            [membro["papel"] for membro in dados["membros"]],
            ["Presidente", "Avaliador", "Avaliador"],
        )
        self.assertEqual(
            dados["frase"],
            "Trabalho de Conclusão de Curso defendido e aprovado pela banca avaliadora "
            "constituída pelos professores:",
        )
        self.assertTrue(all(membro["assinatura"] for membro in dados["membros"]))

    def test_folha_aplicavel(self):
        casos = (
            ({}, None),
            ({"parecer": Parecer.APROVADO_COM_CORRECOES}, None),
            ({"etapa": DescricaoTurma.TCC_1}, mensagens.FOLHA_NAO_SE_APLICA),
            ({"parecer": Parecer.REPROVADO}, mensagens.FOLHA_REPROVADO),
        )
        for argumentos, esperado in casos:
            with self.subTest(**{chave: str(valor) for chave, valor in argumentos.items()}):
                cenario = sessao_liberada(**argumentos)
                self.assertEqual(services_documentos.folha_aplicavel(cenario["sessao"]), esperado)
        self.assertEqual(
            mensagens.FOLHA_NAO_SE_APLICA, "A Folha de Aprovação não se aplica ao TCC 1"
        )
        self.assertEqual(
            mensagens.FOLHA_REPROVADO, "Documento indisponível para trabalhos reprovados"
        )


class TesteDadosDaDeclaracao(TesteAvaliacao):
    """dados_da_declaracao (MX-05; FR-020). [US-30][RBN-DEF-08.3]"""

    def test_texto_codigo_e_referencia(self):
        cenario = sessao_liberada()
        sessao, membro = cenario["sessao"], cenario["av1"]
        dados = services_documentos.dados_da_declaracao(sessao, membro)
        codigo = services_documentos.codigo_formatado(
            services_documentos.codigo_de_validacao(sessao, membro)
        )
        self.assertEqual(dados["codigo"], codigo)
        self.assertEqual(dados["papel"], "1º Avaliador")
        self.assertEqual(dados["referencia"], f"Defesa nº {sessao.pk}")
        self.assertIn(f"Código de validação: {codigo}.", dados["texto"])
        self.assertIn("Este código não constitui assinatura digital.", dados["texto"])
        self.assertIn("realizada em 20/11/2026", dados["texto"])

    def test_so_para_membro_efetivo(self):
        cenario = sessao_liberada()
        for usuario in (cenario["suplente"], cenario["aluno"], cenario["professor"]):
            with self.subTest(usuario=usuario.pk):
                with self.assertRaises(ValueError):
                    services_documentos.dados_da_declaracao(cenario["sessao"], usuario)


# =============================================================================================
# Parte de view (tasks T022): cenários 1.1 a 1.19
# =============================================================================================

ATA_II = "Ata Final de Avaliação de Trabalho de Conclusão de Curso II"
ATA_I = "Ata Final de Avaliação de Trabalho de Conclusão de Curso I"
SEM_PERMISSAO = "Você não tem permissão para acessar os documentos desta defesa"
E2 = (
    "Não foi possível gerar a Ata Final: o Coordenador de Curso não possui assinatura cadastrada "
    "no perfil"
)
E3 = "Erro ao gerar os documentos da defesa. Tente realizar o download novamente em instantes"
MX08 = (
    "A Ata Final está indisponível: o Coordenador de Curso ainda não cadastrou a assinatura no "
    "perfil"
)


def arquivos_em_media():
    """Todos os arquivos do MEDIA_ROOT (temporário nos testes). [US-28][SC-003]"""
    return sorted(
        os.path.join(raiz, nome)
        for raiz, _, nomes in os.walk(settings.MEDIA_ROOT)
        for nome in nomes
    )


def junto(texto):
    """Texto do PDF com as quebras de linha e espaços repetidos trocados por um espaço.
    [US-28][RBN-DEF-07.1]
    """
    return " ".join(texto.split())


class BaseDocumentos(TesteAvaliacao):
    """Downloads e telas da US-28 pela view. [US-28][RBN-DEF-07.3]"""

    def url(self, nome, sessao, origem=None):
        """Endereço do download (`ata_final` ou `folha_aprovacao`). [US-28]"""
        endereco = reverse(f"defesa:{nome}", args=[sessao.pk])
        return f"{endereco}?origem={origem}" if origem else endereco

    def baixar(self, usuario, nome, sessao, origem=None, follow=False):
        """GET do download como o usuário. [US-28][RBN-DEF-07.3]"""
        self.client.force_login(usuario)
        return self.client.get(self.url(nome, sessao, origem), follow=follow)

    def conferir_pdf(self, resposta, nome_arquivo):
        """Resposta 200 com o PDF em anexo e o nome sem dados pessoais. [US-28][RBN-DEF-07.1]"""
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta["Content-Type"], "application/pdf")
        self.assertEqual(resposta["Content-Disposition"], f'attachment; filename="{nome_arquivo}"')
        self.assertTrue(resposta.content.startswith(b"%PDF"))

    def conferir_recusa_403(self, resposta):
        """403 com o texto da US-28 E6. [US-28][RBN-DEF-07.3]"""
        self.assertContains(resposta, SEM_PERMISSAO, status_code=403)

    def janela(self, usuario, sessao):
        """HTML da janela Sessão de defesa como o usuário. [US-28][RBN-DEF-07.3]"""
        self.client.force_login(usuario)
        return self.client.get(reverse("defesa:sessao", args=[sessao.pk]))

    def meu_tcc(self, cenario):
        """HTML da aba Meu TCC como o Aluno. [US-28][RBN-DEF-07.3]"""
        self.client.force_login(cenario["aluno"])
        return self.client.get(reverse("cadastro:meu_tcc", args=[cenario["tcc"].tcc_tur_id]))

    def liberar_pela_tela(self, cenario):
        """POST de Liberar Resultado como o Orientador, com a confirmação da apuração; segue o
        redirecionamento. [US-27][RBN-DEF-06.4]
        """
        atual = cenario["apuracao"]
        self.client.force_login(cenario["orientador"])
        return self.client.post(
            reverse("defesa:liberar_resultado", args=[cenario["sessao"].pk]),
            {"nota": str(atual["nota_final"]), "parecer": atual["parecer"]},
            follow=True,
        )


class TesteDownloadsTcc2Aprovado(BaseDocumentos):
    """Cenários 1.1, 1.2, 1.5, 1.8 e 1.9. [US-28][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-07.3]"""

    def test_cenario_1_1_ata_folha_e_botoes(self):
        cenario = sessao_liberada()
        sessao = cenario["sessao"]
        secretaria = criar_secretaria(curso=cenario["tcc"].tcc_tur.tur_cur)
        ata = self.baixar(cenario["orientador"], "ata_final", sessao)
        self.conferir_pdf(ata, f"ata_final_{sessao.pk}.pdf")
        texto = junto(texto_do_pdf(ata))
        self.assertIn(ATA_II, texto)
        self.assertIn("Universidade do Estado do Amazonas – Escola Superior de Tecnologia", texto)
        for chave in ("orientador", "av1", "av2", "coordenador", "aluno"):
            self.assertIn(cenario[chave].usu_nome, texto)
        self.assertIn("Nota final: 8,0", texto)
        self.assertIn("Parecer: Aprovado", texto)
        self.assertIn("20/11/2026", texto)
        # 3 assinaturas da banca e a do Coordenador (FR-001).
        self.assertEqual(numero_de_imagens(ata), 4)
        folha = self.baixar(cenario["orientador"], "folha_aprovacao", sessao)
        self.conferir_pdf(folha, f"folha_aprovacao_{sessao.pk}.pdf")
        texto = junto(texto_do_pdf(folha))
        self.assertIn("Folha de Aprovação", texto)
        self.assertIn("defendido e aprovado pela banca avaliadora", texto)
        self.assertIn("Manaus, 20 de novembro de 2026", texto)
        self.assertNotIn("8,0", texto)
        self.assertNotIn("Nota", texto)
        self.assertEqual(numero_de_imagens(folha), 3)
        for nome in ("orientador", "av1", "av2", "professor", "aluno"):
            with self.subTest(perfil=nome):
                pagina = self.janela(cenario[nome], sessao)
                self.assertContains(pagina, self.url("ata_final", sessao))
                self.assertContains(pagina, self.url("folha_aprovacao", sessao))
        pagina = self.janela(secretaria, sessao)
        self.assertContains(pagina, "Ata Final (PDF)")
        self.assertContains(pagina, "Folha de Aprovação (PDF)")

    def test_cenario_1_2_aluno_baixa_a_folha_pelo_meu_tcc(self):
        cenario = sessao_liberada()
        sessao = cenario["sessao"]
        pagina = self.meu_tcc(cenario)
        self.assertContains(pagina, "Documentos da defesa")
        self.assertContains(pagina, self.url("folha_aprovacao", sessao, "meu_tcc"))
        self.assertContains(pagina, self.url("ata_final", sessao, "meu_tcc"))
        folha = self.baixar(cenario["aluno"], "folha_aprovacao", sessao, "meu_tcc")
        self.conferir_pdf(folha, f"folha_aprovacao_{sessao.pk}.pdf")
        self.assertEqual(numero_de_imagens(folha), 3)

    def test_cenario_1_5_aprovado_com_correcoes_tem_folha(self):
        cenario = sessao_liberada(parecer=Parecer.APROVADO_COM_CORRECOES)
        sessao = cenario["sessao"]
        self.assertContains(self.meu_tcc(cenario), self.url("folha_aprovacao", sessao, "meu_tcc"))
        folha = self.baixar(cenario["aluno"], "folha_aprovacao", sessao, "meu_tcc")
        self.conferir_pdf(folha, f"folha_aprovacao_{sessao.pk}.pdf")
        ata = self.baixar(cenario["aluno"], "ata_final", sessao)
        self.assertIn("Parecer: Aprovado com Correções", junto(texto_do_pdf(ata)))

    def test_cenario_1_8_secretaria_pela_lista_defesas(self):
        cenario = sessao_liberada()
        sessao = cenario["sessao"]
        secretaria = criar_secretaria(curso=cenario["tcc"].tcc_tur.tur_cur)
        self.client.force_login(secretaria)
        lista = self.client.get(
            reverse("defesa:defesas"), {"data_inicial": "01/11/2026", "data_final": "30/11/2026"}
        )
        self.assertContains(lista, reverse("defesa:sessao", args=[sessao.pk]))
        self.assertContains(self.janela(secretaria, sessao), self.url("ata_final", sessao))
        self.conferir_pdf(
            self.baixar(secretaria, "ata_final", sessao), f"ata_final_{sessao.pk}.pdf"
        )
        self.conferir_pdf(
            self.baixar(secretaria, "folha_aprovacao", sessao),
            f"folha_aprovacao_{sessao.pk}.pdf",
        )

    def test_cenario_1_9_login_e_depois_o_download(self):
        cenario = sessao_liberada()
        sessao = cenario["sessao"]
        endereco = self.url("ata_final", sessao)
        resposta = self.client.get(endereco)
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("cadastro:entrar"), resposta["Location"])
        self.assertIn("next=", resposta["Location"])
        self.client.force_login(cenario["aluno"])
        self.conferir_pdf(self.client.get(endereco), f"ata_final_{sessao.pk}.pdf")


class TesteConteudoPorEtapaEParecer(BaseDocumentos):
    """Cenários 1.3, 1.4, 1.6, 1.7, 1.12 e 1.13. [US-28][RBN-DEF-07.1][RBN-DEF-07.2]"""

    def test_cenario_1_3_tcc_1_so_ata_i(self):
        cenario = sessao_liberada(etapa=DescricaoTurma.TCC_1)
        sessao = cenario["sessao"]
        pagina = self.janela(cenario["orientador"], sessao)
        self.assertContains(pagina, "Ata Final (PDF)")
        self.assertNotContains(pagina, "Folha de Aprovação (PDF)")
        self.assertNotContains(
            self.meu_tcc(cenario), self.url("folha_aprovacao", sessao, "meu_tcc")
        )
        texto = junto(texto_do_pdf(self.baixar(cenario["orientador"], "ata_final", sessao)))
        self.assertIn(ATA_I, texto)
        self.assertNotIn(ATA_II, texto)

    def test_cenario_1_4_reprovado_so_ata_com_a_reprovacao(self):
        cenario = sessao_liberada(parecer=Parecer.REPROVADO)
        sessao = cenario["sessao"]
        pagina = self.janela(cenario["orientador"], sessao)
        self.assertContains(pagina, "Ata Final (PDF)")
        self.assertNotContains(pagina, "Folha de Aprovação (PDF)")
        texto = junto(texto_do_pdf(self.baixar(cenario["orientador"], "ata_final", sessao)))
        self.assertIn("Parecer: Reprovado", texto)
        self.assertIn("Nota final: 5,0", texto)

    def test_cenario_1_6_suplente_na_linha_do_titular(self):
        cenario = sessao_liberada(
            suplente_acionado=True, papel_substituido=PapelBanca.PRIMEIRO_AVALIADOR
        )
        sessao = cenario["sessao"]
        ata = self.baixar(cenario["orientador"], "ata_final", sessao)
        texto = junto(texto_do_pdf(ata))
        self.assertIn(f"1º Avaliador {cenario['suplente'].usu_nome}", texto)
        self.assertNotIn(cenario["ausente"].usu_nome, texto)
        self.assertEqual(numero_de_imagens(ata), 4)
        folha = junto(texto_do_pdf(self.baixar(cenario["orientador"], "folha_aprovacao", sessao)))
        self.assertIn(cenario["suplente"].usu_nome, folha)
        self.assertNotIn(cenario["ausente"].usu_nome, folha)

    def test_cenario_1_7_observacao_do_qualis(self):
        cenario = liberar(preparar_liberacao(nota=5.4, qualis="A1"))
        sessao = cenario["sessao"]
        self.assertEqual(str(sessao.def_nota_final), "6.0")
        ata = self.baixar(cenario["orientador"], "ata_final", sessao)
        self.assertIn(
            "Em caso de artigos, se Qualis A ou B, a nota final será o valor máximo entre 6,0 e a "
            "média dos avaliadores",
            junto(texto_do_pdf(ata)),
        )
        sem_qualis = sessao_liberada()
        ata = self.baixar(sem_qualis["orientador"], "ata_final", sem_qualis["sessao"])
        self.assertNotIn("Qualis", texto_do_pdf(ata))

    def test_cenario_1_12_folha_de_tcc_1_recusada(self):
        cenario = sessao_liberada(etapa=DescricaoTurma.TCC_1)
        sessao = cenario["sessao"]
        resposta = self.baixar(cenario["aluno"], "folha_aprovacao", sessao, follow=True)
        self.assertRedirects(resposta, reverse("defesa:sessao", args=[sessao.pk]))
        self.assertContains(resposta, "A Folha de Aprovação não se aplica ao TCC 1")
        resposta = self.baixar(cenario["aluno"], "folha_aprovacao", sessao, "meu_tcc", True)
        self.assertRedirects(
            resposta, reverse("cadastro:meu_tcc", args=[cenario["tcc"].tcc_tur_id])
        )
        self.assertContains(resposta, "A Folha de Aprovação não se aplica ao TCC 1")

    def test_cenario_1_13_folha_de_reprovado_recusada(self):
        cenario = sessao_liberada(parecer=Parecer.REPROVADO)
        resposta = self.baixar(
            cenario["professor"], "folha_aprovacao", cenario["sessao"], follow=True
        )
        self.assertContains(resposta, "Documento indisponível para trabalhos reprovados")
        self.assertNotEqual(resposta["Content-Type"], "application/pdf")


class TesteRecusas(BaseDocumentos):
    """Cenários 1.14, 1.15 e 1.16 e o parâmetro `origem` livre. [US-28][RBN-DEF-07.3]"""

    def test_cenario_1_14_docente_fora_da_banca_e_da_turma(self):
        cenario = sessao_liberada()
        for estranho in (docente(), cenario["coordenador"]):
            for nome in ("ata_final", "folha_aprovacao"):
                with self.subTest(usuario=estranho.pk, documento=nome):
                    self.conferir_recusa_403(self.baixar(estranho, nome, cenario["sessao"]))

    def test_cenario_1_15_suplente_nao_acionado(self):
        cenario = sessao_liberada()
        sessao = cenario["sessao"]
        for nome in ("ata_final", "folha_aprovacao"):
            with self.subTest(documento=nome):
                self.conferir_recusa_403(self.baixar(cenario["suplente"], nome, sessao))
        self.assertNotContains(self.janela(cenario["suplente"], sessao), "Ata Final (PDF)")

    def test_cenario_1_16_antes_da_liberacao(self):
        for status in (StatusSessao.EM_ANDAMENTO, StatusSessao.REALIZADA):
            cenario = sessao_com_banca(status, descricao=DescricaoTurma.TCC_2)
            for chave in ("aluno", "orientador", "av1"):
                for nome in ("ata_final", "folha_aprovacao"):
                    with self.subTest(status=status, perfil=chave, documento=nome):
                        self.conferir_recusa_403(
                            self.baixar(cenario[chave], nome, cenario["sessao"])
                        )
            self.assertNotContains(
                self.janela(cenario["orientador"], cenario["sessao"]), "Ata Final (PDF)"
            )

    def test_origem_com_valor_livre_volta_a_sessao(self):
        cenario = sessao_liberada(etapa=DescricaoTurma.TCC_1)
        sessao = cenario["sessao"]
        for origem in ("https://exemplo.org/", "//exemplo.org", "outra"):
            with self.subTest(origem=origem):
                resposta = self.baixar(cenario["aluno"], "folha_aprovacao", sessao, origem)
                self.assertRedirects(
                    resposta,
                    reverse("defesa:sessao", args=[sessao.pk]),
                    fetch_redirect_response=False,
                )


class TesteE2DoCoordenador(BaseDocumentos):
    """Cenários 1.10, 1.17 e 1.18, a assinatura de membro ausente e o Edge Case da assinatura
    cadastrada depois da liberação. [US-28][US-27][RBN-DEF-07.1][RBN-CAD-13.1][RBN-DEF-06.4]
    """

    def test_cenario_1_10_coordenador_sem_assinatura(self):
        cenario = preparar_liberacao(assinatura_coordenador=False)
        sessao, coordenador = cenario["sessao"], cenario["coordenador"]
        pagina = self.liberar_pela_tela(cenario)
        self.assertContains(pagina, "Resultado liberado com sucesso")
        self.assertContains(pagina, E2)
        sessao.refresh_from_db()
        self.assertEqual(sessao.def_status, StatusSessao.REALIZADA)
        [aviso] = Notificacoes.objects.filter(not_usu=coordenador)
        self.assertEqual(
            aviso.not_mensagem,
            "Cadastre a imagem de assinatura no seu perfil: a Ata Final da defesa de "
            f"{cenario['aluno'].usu_nome} não pode ser gerada sem ela.",
        )
        self.assertEqual(aviso.not_link_tela, reverse("cadastro:perfil"))
        avisos = Notificacoes.objects.count()
        # Download: E2 ao Presidente, MX-08 aos demais, sem nova notificação (P1).
        resposta = self.baixar(cenario["orientador"], "ata_final", sessao, follow=True)
        self.assertRedirects(resposta, reverse("defesa:sessao", args=[sessao.pk]))
        self.assertContains(resposta, E2)
        for chave in ("av1", "aluno", "professor"):
            with self.subTest(perfil=chave):
                resposta = self.baixar(cenario[chave], "ata_final", sessao, follow=True)
                self.assertContains(resposta, MX08)
                self.assertNotContains(resposta, E2)
        self.assertEqual(Notificacoes.objects.count(), avisos)
        # A Folha não leva a assinatura do Coordenador e continua disponível.
        self.conferir_pdf(
            self.baixar(cenario["aluno"], "folha_aprovacao", sessao),
            f"folha_aprovacao_{sessao.pk}.pdf",
        )

    def test_cenario_1_17_curso_sem_coordenador_notifica_a_secretaria(self):
        cenario = preparar_liberacao(com_coordenador=False)
        secretaria = criar_secretaria(curso=cenario["tcc"].tcc_tur.tur_cur)
        sessao = cenario["sessao"]
        self.assertContains(self.liberar_pela_tela(cenario), E2)
        curso = cenario["tcc"].tcc_tur.tur_cur.cur_nome
        aviso = Notificacoes.objects.get(not_usu=secretaria, not_mensagem__startswith="O curso")
        self.assertEqual(
            aviso.not_mensagem,
            f"O curso {curso} não tem Coordenador de Curso cadastrado: a Ata Final da defesa de "
            f"{cenario['aluno'].usu_nome} não pode ser gerada.",
        )
        self.assertEqual(aviso.not_link_tela, reverse("defesa:sessao", args=[sessao.pk]))
        resposta = self.baixar(cenario["orientador"], "ata_final", sessao, follow=True)
        self.assertContains(resposta, E2)

    def test_cenario_1_18_arquivo_do_coordenador_ausente(self):
        cenario = sessao_liberada()
        default_storage.delete(services.caminho_da_assinatura(cenario["coordenador"]))
        with self.assertLogs("sigtcc.defesa", level="WARNING") as log:
            ata = self.baixar(cenario["orientador"], "ata_final", cenario["sessao"])
        self.conferir_pdf(ata, f"ata_final_{cenario['sessao'].pk}.pdf")
        self.assertIn(cenario["coordenador"].usu_nome, texto_do_pdf(ata))
        self.assertEqual(numero_de_imagens(ata), 3)
        self.assertIn("Imagem de assinatura ausente", "".join(log.output))

    def test_assinatura_de_membro_ausente_gera_o_pdf_sem_a_imagem(self):
        """Edge Case: assinatura de membro ausente no disco; o PDF sai sem a imagem dele, sem
        erro. [US-28][RBN-DEF-07.1][RBN-DEF-07.2]
        """
        cenario = sessao_liberada()
        linha = BancaDefesa.objects.get(ban_def=cenario["sessao"], ban_usu=cenario["av1"])
        default_storage.delete(linha.ban_assinatura_path)
        with self.assertLogs("sigtcc.defesa", level="WARNING"):
            ata = self.baixar(cenario["orientador"], "ata_final", cenario["sessao"])
        self.conferir_pdf(ata, f"ata_final_{cenario['sessao'].pk}.pdf")
        self.assertEqual(numero_de_imagens(ata), 3)
        with self.assertLogs("sigtcc.defesa", level="WARNING"):
            folha = self.baixar(cenario["orientador"], "folha_aprovacao", cenario["sessao"])
        self.conferir_pdf(folha, f"folha_aprovacao_{cenario['sessao'].pk}.pdf")
        self.assertEqual(numero_de_imagens(folha), 2)

    def test_coordenador_cadastra_a_assinatura_depois_da_liberacao(self):
        cenario = sessao_liberada(assinatura_coordenador=False)
        sessao = cenario["sessao"]
        resposta = self.baixar(cenario["orientador"], "ata_final", sessao, follow=True)
        self.assertContains(resposta, E2)
        assinatura_no_perfil(cenario["coordenador"])
        ata = self.baixar(cenario["orientador"], "ata_final", sessao)
        self.conferir_pdf(ata, f"ata_final_{sessao.pk}.pdf")
        self.assertEqual(numero_de_imagens(ata), 4)


class TesteFalhaNaGeracao(BaseDocumentos):
    """Cenário 1.11 (E3): nada entregue nem gravado, mensagem exata. [US-28][RBN-DEF-07.1]"""

    def test_cenario_1_11_servico_de_conversao_indisponivel(self):
        cenario = sessao_liberada()
        sessao = cenario["sessao"]
        meu_tcc = reverse("cadastro:meu_tcc", args=[cenario["tcc"].tcc_tur_id])
        antes = arquivos_em_media()
        for nome in ("ata_final", "folha_aprovacao"):
            with self.subTest(documento=nome):
                with mock.patch(
                    "sigtcc.apps.defesa.pdf.gerar_pdf",
                    side_effect=pdf.ErroAoGerarPdf("conversor fora"),
                ):
                    resposta = self.baixar(cenario["aluno"], nome, sessao, "meu_tcc")
                self.assertRedirects(resposta, meu_tcc, fetch_redirect_response=False)
                self.assertContains(self.client.get(meu_tcc), E3)
        self.assertEqual(arquivos_em_media(), antes)

    def test_falha_real_do_conversor_vai_ao_log(self):
        cenario = sessao_liberada()
        with mock.patch("xhtml2pdf.pisa.CreatePDF", side_effect=RuntimeError("quebrou")):
            with self.assertLogs("sigtcc.defesa", level="ERROR"):
                resposta = self.baixar(
                    cenario["orientador"], "ata_final", cenario["sessao"], follow=True
                )
        self.assertContains(resposta, E3)


class TesteDuasSessoesNoMeuTcc(BaseDocumentos):
    """Cenário 1.19 (P14): o Meu TCC mostra os documentos de cada sessão Realizada do TCC, com a
    data da defesa, da mais recente para a mais antiga. [US-28][RBN-DEF-07.3]
    """

    def test_cenario_1_19_reprovado_e_depois_aprovado(self):
        cenario = sessao_liberada(parecer=Parecer.REPROVADO)
        primeira, tcc, orientador = cenario["sessao"], cenario["tcc"], cenario["orientador"]
        # Nova sessão do mesmo TCC (só para montar o cenário): volta a Apto para Defesa.
        TCCs.objects.filter(pk=tcc.pk).update(tcc_status=StatusTCC.APTO_PARA_DEFESA)
        tcc.refresh_from_db()
        banca = {"primeiro_avaliador": docente(), "segundo_avaliador": docente()}
        segunda = agendar_sessao_de(
            tcc, orientador, banca, data=date(2026, 12, 10), h_inicio=time(9, 0)
        )
        avancar_para(segunda, StatusSessao.EM_ANDAMENTO)
        for membro in (orientador, banca["primeiro_avaliador"], banca["segundo_avaliador"]):
            lancar(segunda, membro, 8)
            enviar(segunda, membro, copia_de_assinatura(segunda, membro))
        services_avaliacoes.registrar_parecer(orientador, segunda.pk, Parecer.APROVADO)
        segunda.refresh_from_db()
        atual = services_avaliacoes.apuracao(segunda)
        self.assertTrue(
            services_avaliacoes.liberar_resultado(
                orientador, segunda.pk, atual["nota_final"], atual["parecer"]
            ).liberado
        )
        pagina = self.meu_tcc(cenario).content.decode()
        self.assertIn("Defesa de 10/12/2026", pagina)
        self.assertIn("Defesa de 20/11/2026", pagina)
        self.assertLess(pagina.index("Defesa de 10/12/2026"), pagina.index("Defesa de 20/11/2026"))
        self.assertIn(self.url("ata_final", primeira, "meu_tcc"), pagina)
        self.assertNotIn(self.url("folha_aprovacao", primeira, "meu_tcc"), pagina)
        self.assertIn(self.url("ata_final", segunda, "meu_tcc"), pagina)
        self.assertIn(self.url("folha_aprovacao", segunda, "meu_tcc"), pagina)
