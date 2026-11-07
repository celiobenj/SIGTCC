"""Textos exibidos: cópia exata das US e dos provisórios da spec 010 (constituição, princípio VI).

[US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2]
[RBN-REL-02.3][RBN-REL-02.4][FR-014][FR-017][Q-146] (tasks T049)
"""

import re
from pathlib import Path

from django.test import SimpleTestCase

from sigtcc.apps.cadastro import mensagens as mensagens_cadastro
from sigtcc.apps.defesa import mensagens as mensagens_defesa
from sigtcc.apps.relatorios import mensagens

RAIZ = Path(__file__).resolve().parents[4]
APP = RAIZ / "sigtcc" / "apps" / "relatorios"


class TesteTextosDasUS(SimpleTestCase):
    """Mensagens exatas das US-31, 47, 32 e 33."""

    def test_textos_exatos(self):
        """E2 e E3 da US-31 e da US-47; E2 da US-32 e da US-33; D e E da US-31."""
        self.assertEqual(
            mensagens.NENHUM_REGISTRO_FILTROS,
            "Nenhum registro encontrado para os filtros selecionados",
        )
        self.assertEqual(mensagens.NENHUM_REGISTRO, "Nenhum registro")
        self.assertEqual(
            mensagens_defesa.DATA_INICIAL_MAIOR,
            "A data inicial não pode ser superior à data final",
        )
        self.assertEqual(mensagens_cadastro.SEM_ORIENTADOR, "Sem orientador")
        self.assertEqual(mensagens.NAO_INFORMADA, "Não informada")


class TesteProvisorios(SimpleTestCase):
    """MR-01 a MR-14 iguais à tabela da spec, que é a fonte da validação com a PO (Q-146)."""

    def test_iguais_a_spec(self):
        """Todo texto entre aspas da tabela existe em mensagens.py."""
        spec = (RAIZ / "specs" / "010-dashboards-producao" / "spec.md").read_text(encoding="utf-8")
        linhas = re.findall(r'^\| (MR-\d+) \| [^|]* \| "([^"]+)" \|', spec, re.M)
        self.assertEqual(len(linhas), 12)
        textos = {
            valor
            for nome, valor in vars(mensagens).items()
            if nome.isupper() and isinstance(valor, str)
        }
        for identificador, texto in linhas:
            with self.subTest(identificador=identificador):
                self.assertIn(texto, textos)

    def test_como_e_calculado_traz_as_formulas(self):
        """Heurística 10: as fórmulas da US em cada relatório que as tem."""
        self.assertIn(
            "Matriculados = Sem Proposta + Ativos + Com Sucesso + Sem Sucesso",
            mensagens.COMO_FORMACAO[0],
        )
        self.assertIn(
            "Total de Trabalhos = Ativos + Com Sucesso + Sem Sucesso", mensagens.COMO_PRODUCAO[0]
        )
        self.assertTrue(
            any(
                "Aprovado sem Versão Final homologada" in texto for texto in mensagens.COMO_FORMACAO
            )
        )


class TesteTextosCentralizados(SimpleTestCase):
    """Mensagem ao usuário só em mensagens.py: consultas, views e templates não a repetem."""

    def test_sem_mensagem_solta(self):
        """Nenhuma mensagem de mensagens.py copiada no código."""
        constantes = (
            mensagens.NENHUM_REGISTRO,
            mensagens.MR01_SUGESTAO_VAZIO,
            mensagens.MR02_SEM_REGISTROS_EXPORTAR,
            mensagens.MR05_SELECIONE,
            mensagens.MR06_SEM_PERMISSAO,
            mensagens.MR07_FALHA_ARQUIVO,
            mensagens.MR14_APROVEITAMENTO_SEM_ANALISE,
        )
        arquivos = [
            *(APP / nome for nome in ("views.py", "services_relatorios.py", "exportacao.py")),
            *(RAIZ / "sigtcc" / "templates" / "relatorios").rglob("*.html"),
        ]
        for arquivo in arquivos:
            conteudo = arquivo.read_text(encoding="utf-8")
            for texto in constantes:
                with self.subTest(arquivo=arquivo.name, texto=texto):
                    self.assertNotIn(texto, conteudo)
