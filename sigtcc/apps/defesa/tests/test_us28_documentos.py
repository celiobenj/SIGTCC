"""US-28, Ata Final e Folha de Aprovação (User Story 1 da spec 009).

Parte de serviço (tasks T013): situacao_da_ata nos 3 casos e com o arquivo do Coordenador
ausente (Q-140); dados_da_folha sem nenhuma nota; dados_da_ata com o suplente acionado na linha
do titular; a data dos documentos é a da defesa (def_data; P12). Os testes de view (cenários 1.1
a 1.19) entram na Phase 3 (tasks T022).

[US-28][RBN-DEF-07.1][RBN-DEF-07.2][RBN-CAD-13.1] (spec 009, tasks T013)
"""

from datetime import date

from django.core.files.storage import default_storage

from sigtcc.apps.cadastro import services
from sigtcc.apps.cadastro.choices import DescricaoTurma
from sigtcc.apps.defesa import mensagens, services_documentos
from sigtcc.apps.defesa.choices import Parecer
from sigtcc.apps.defesa.tests.apoio_avaliacao import TesteAvaliacao
from sigtcc.apps.defesa.tests.apoio_documentos import sessao_liberada

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
