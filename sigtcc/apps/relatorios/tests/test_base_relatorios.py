"""Base do módulo Relatórios: viabilidade das consultas no PostgreSQL, estrutura e registro.

[US-31][US-32][RBN-REL-01.1][RBN-CAD-08.7][FR-003][FR-018][FR-066][research R5][research R6]
(tasks T002, T004 e T005)
"""

from datetime import date
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.db.models import Count, OuterRef, Q, Subquery, Value
from django.db.models.functions import Coalesce
from django.test import SimpleTestCase
from django.urls import reverse

from sigtcc.apps.cadastro.choices import StatusTCC
from sigtcc.apps.cadastro.models import AlunosTurmas, HistoricoStatusTCC, Usuarios
from sigtcc.apps.cadastro.tests.apoio_contas import coordenador_de, docente_de, secretaria_de
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, SI, criar_turma_de, matricular_aluno
from sigtcc.apps.defesa.tests.apoio_defesa import docente
from sigtcc.apps.relatorios import exportacao, mensagens, registro
from sigtcc.apps.relatorios.estrutura import (
    Coluna,
    Kpi,
    Linha,
    Relatorio,
    SubLista,
    link_seguro,
)
from sigtcc.apps.relatorios.registro import relatorio
from sigtcc.apps.relatorios.tests.apoio_relatorios import (
    TesteRelatorios,
    aluno_com_status,
    banca_de,
    cenario_hostil,
    registrar_status,
    sessao_realizada,
)


class TesteViabilidadeDaConsulta(TesteRelatorios):
    """Subconsulta do último registro em Count(filter=...) sobre values(): research R5, R6."""

    def _consulta(self):
        """Uma linha por curso, com o Status por período. [US-32][RBN-CAD-08.7]"""
        ultimo = (
            HistoricoStatusTCC.objects.filter(
                hst_tcc__tcc_alu=OuterRef("mat_alu"), hst_tcc__tcc_tur=OuterRef("mat_tur")
            )
            .order_by("-hst_data_hora", "-hst_id")
            .values("hst_status_novo")[:1]
        )
        return (
            AlunosTurmas.objects.annotate(
                status=Coalesce(Subquery(ultimo), Value(StatusTCC.SEM_PROPOSTA.value))
            )
            .values("mat_tur__tur_cur")
            .annotate(
                matriculados=Count("mat_alu"),
                sem_proposta=Count("mat_alu", filter=Q(status=StatusTCC.SEM_PROPOSTA)),
                ativos=Count("mat_alu", filter=Q(status=StatusTCC.EM_ANDAMENTO)),
                sem_sucesso=Count("mat_alu", filter=Q(status=StatusTCC.DESISTENTE)),
            )
            .order_by("mat_tur__tur_cur")
        )

    def test_uma_linha_por_curso_com_o_ultimo_registro(self):
        """R5 e R6: agrupa só pelo curso e lê o último registro de cada TCC."""
        professor = docente()
        turma_ec = criar_turma_de(professor, curso_nome=EC)
        turma_si = criar_turma_de(professor, curso_nome=SI)
        aluno_com_status(turma_ec, StatusTCC.EM_ANDAMENTO)
        tcc = aluno_com_status(turma_ec, StatusTCC.EM_ANDAMENTO)
        registrar_status(tcc, StatusTCC.DESISTENTE)
        matricular_aluno(turma_si)
        linhas = list(self._consulta())
        self.assertEqual(len(linhas), 2)
        por_curso = {linha["mat_tur__tur_cur"]: linha for linha in linhas}
        ec = por_curso[turma_ec.tur_cur_id]
        self.assertEqual(
            (ec["matriculados"], ec["ativos"], ec["sem_sucesso"], ec["sem_proposta"]),
            (2, 1, 1, 0),
        )
        self.assertEqual(por_curso[turma_si.tur_cur_id]["sem_proposta"], 1)

    def test_explain_do_postgresql(self):
        """R6: o PostgreSQL aceita a subconsulta correlacionada dentro de FILTER."""
        plano = self._consulta().explain()
        self.assertIn("Aggregate", plano)
        self.assertEqual(connection.vendor, "postgresql")


class TesteEstrutura(SimpleTestCase):
    """Estrutura única: valor canônico, células ordenadas e link (contrato §3). [FR-018][FR-066]"""

    COLUNAS = (Coluna("nome", "Nome"), Coluna("total", "Total", numerica=True))

    def test_recusa_valor_fora_do_canonico(self):
        """bool, date e None não entram: a tela e o arquivo divergiriam."""
        for valor in (True, None, date(2026, 11, 5), 1.5):
            with self.subTest(valor=valor), self.assertRaises(TypeError):
                Linha({"nome": valor})

    def test_celulas_na_ordem_das_colunas(self):
        """A ordem vem das colunas, não do dicionário, e toda célula é Celula."""
        celulas = Linha({"total": 3, "nome": "Ana"}).celulas(self.COLUNAS)
        self.assertEqual([(c.texto, c.numerica) for c in celulas], [("Ana", False), (3, True)])

    def test_valor_ausente_sai_vazio(self):
        """Vazio é "", nunca "-", que ganharia a proteção de fórmula no CSV."""
        self.assertEqual(Linha({}).celulas(self.COLUNAS)[0].texto, "")

    def test_link_seguro_so_com_https(self):
        """FR-066: só https com netloc vira link; o resto é texto."""
        self.assertEqual(link_seguro("https://doi.org/10.1/x").url, "https://doi.org/10.1/x")
        for valor in (
            "http://doi.org/x",
            "javascript:alert(1)",
            "https://",
            "10.1000/xyz",
            "https://a.b/c d",
            "https://[",
        ):
            with self.subTest(valor=valor):
                celula = link_seguro(valor)
                self.assertIsNone(celula.url)
                self.assertEqual(celula.texto, valor)

    def test_tem_registros_deriva_das_linhas(self):
        """Sem sobrescrever, sem linhas é sem registros."""
        self.assertFalse(Relatorio(self.COLUNAS, ()).tem_registros)
        self.assertTrue(Relatorio(self.COLUNAS, (Linha({"nome": "A"}),)).tem_registros)
        zerado = Relatorio(self.COLUNAS, (Linha({"total": 0}),), tem_registros=False)
        self.assertFalse(zerado.tem_registros)

    def test_no_maximo_quatro_kpis(self):
        """FR-072: no máximo 4 KPIs."""
        with self.assertRaises(ValueError):
            Relatorio(self.COLUNAS, (), kpis=tuple(Kpi(str(n), n) for n in range(5)))

    def test_sublistas_exigem_a_coluna_da_linha_mae(self):
        """Contrato §3: sem rotulo_linha, o arquivo não saberia a linha-mãe."""
        sublista = SubLista("Bancas", (Coluna("data", "Data"),), ())
        with self.assertRaises(ValueError):
            Relatorio(self.COLUNAS, (Linha({"nome": "A"}, sublistas=(sublista,)),))

    def test_linhas_prontas_resolvem_as_sublistas(self):
        """A sub-lista chega pronta, com destaque, para o template e os exportadores."""
        colunas = (Coluna("data", "Data"),)
        item = Linha({"data": "05/11/2026"}, destaque=True)
        sublista = SubLista("Bancas", colunas, (item,))
        relatorio = Relatorio(
            self.COLUNAS, (Linha({"nome": "A"}, sublistas=(sublista,)),), rotulo_linha="nome"
        )
        pronta = relatorio.linhas_prontas()[0].sublistas[0]
        self.assertEqual(pronta.linhas[0].celulas[0].texto, "05/11/2026")
        self.assertTrue(pronta.linhas[0].destaque)
        self.assertEqual(relatorio.rotulo_da_linha_mae(), "Nome")


class TesteRegistro(SimpleTestCase):
    """Registro por decorador; erro de declaração falha ao carregar (R13). [FR-003][FR-004]"""

    def _registrar(self, id="exemplo", perfis=("coordenador",), filtros=("curso",)):
        return relatorio(id, "Exemplo", "Descrição", "Frase", perfis, filtros, 90)(
            lambda u, f: None
        )

    def test_registra_e_obtem(self):
        """O decorador devolve a função e guarda a declaração."""
        with mock.patch.dict(registro._RELATORIOS, clear=False):
            self._registrar()
            self.assertEqual(registro.obter("exemplo").nome, "Exemplo")
        self.assertIsNone(registro.obter("exemplo"))

    def test_declaracao_invalida_nao_carrega(self):
        """Perfis vazios abririam a todos: tem_perfil sem perfis é verdadeiro."""
        casos = (
            {"perfis": ()},
            {"perfis": ["coordenador"]},
            {"perfis": ("reitor",)},
            {"filtros": ("turma",)},
            {"id": "Com Espaco"},
        )
        for caso in casos:
            with self.subTest(caso=caso), mock.patch.dict(registro._RELATORIOS):
                with self.assertRaises(ImproperlyConfigured):
                    self._registrar(**caso)

    def test_id_repetido_nao_carrega(self):
        """Um id só por relatório."""
        with mock.patch.dict(registro._RELATORIOS):
            self._registrar()
            with self.assertRaises(ImproperlyConfigured):
                self._registrar()


def relatorio_de_exemplo_registrado(perfis=("coordenador",), linhas=1):
    """Registra, só no teste, um relatório como a feat-11 fará. [FR-003][SC-007]"""

    @relatorio(
        "exemplo-base",
        "Relatório de exemplo",
        "Descrição curta",
        "Uma frase.",
        perfis,
        ("curso",),
        5,
    )
    def consulta(usuario, filtros):
        colunas = (Coluna("nome", "Nome"), Coluna("total", "Total", numerica=True))
        return Relatorio(
            colunas,
            tuple(Linha({"nome": f"Linha {n}", "total": n}) for n in range(linhas)),
            kpis=(Kpi("Linhas", linhas),),
        )

    return consulta


class TesteTelaDaBase(TesteRelatorios):
    """Um relatório de exemplo percorre a tela e os arquivos sem alterar a base.

    [US-31][US-47][RBN-REL-01.1][FR-001][FR-002][FR-004][FR-018][SC-004][SC-007] (tasks T020)
    """

    def setUp(self):
        super().setUp()
        patcher = mock.patch.dict(registro._RELATORIOS)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.coordenador = coordenador_de(EC)
        self.url = reverse("relatorios:relatorio", args=["exemplo-base"])

    def exportar(self, formato, consulta=""):
        return self.client.get(
            reverse("relatorios:exportar", args=["exemplo-base", formato]) + consulta
        )

    def test_relatorio_novo_na_lista_tela_e_arquivos(self):
        """SC-007: só o registro e a consulta."""
        relatorio_de_exemplo_registrado()
        self.client.force_login(self.coordenador)
        resposta = self.client.get(reverse("relatorios:lista"))
        self.assertContains(resposta, "Relatório de exemplo")
        self.assertContains(resposta, "Descrição curta")
        self.assertContains(resposta, mensagens.MR05_SELECIONE)
        resposta = self.client.get(self.url)
        self.assertContains(resposta, "Uma frase.")
        self.assertContains(resposta, "Linha 0")
        self.assertContains(resposta, "Mostrando:")
        self.assertContains(resposta, "Gerado em")
        for formato in ("pdf", "csv", "xlsx"):
            with self.subTest(formato=formato):
                arquivo = self.exportar(formato)
                self.assertEqual(arquivo.status_code, 200)
                self.assertIn("attachment", arquivo["Content-Disposition"])

    def test_item_do_menu(self):
        """FR-001: seção Gestão para Docente e Secretaria."""
        relatorio_de_exemplo_registrado()
        for usuario in (docente(), secretaria_de(EC), self.coordenador):
            with self.subTest(usuario=usuario.pk):
                self.client.force_login(usuario)
                resposta = self.client.get(reverse("relatorios:lista"))
                itens = [
                    item
                    for item in resposta.context["menu_itens"]
                    if item["rotulo"] == "Relatórios"
                ]
                self.assertEqual(itens[0]["secao"], "Gestão")

    def test_perfil_sem_acesso(self):
        """FR-004: o relatório some da lista e o endereço direto é negado, com a MR-06."""
        relatorio_de_exemplo_registrado()
        self.client.force_login(docente())
        resposta = self.client.get(reverse("relatorios:lista"))
        self.assertNotContains(resposta, "Relatório de exemplo")
        for destino in (self.url, reverse("relatorios:exportar", args=["exemplo-base", "csv"])):
            with self.subTest(destino=destino):
                negado = self.client.get(destino)
                self.assertContains(negado, mensagens.MR06_SEM_PERMISSAO, status_code=403)
                self.assertNotContains(negado, "Linha 0", status_code=403)

    def test_id_e_formato_desconhecidos(self):
        """Contrato de rotas: 404, depois da permissão."""
        relatorio_de_exemplo_registrado()
        self.client.force_login(self.coordenador)
        self.assertEqual(
            self.client.get(reverse("relatorios:relatorio", args=["nao-existe"])).status_code, 404
        )
        self.assertEqual(self.exportar("doc").status_code, 404)
        self.client.force_login(docente())
        self.assertEqual(self.exportar("doc").status_code, 403)

    def test_sem_registros_desabilita_e_nao_exporta(self):
        """E3: mensagem exata, sugestão, botões desabilitados e nenhum arquivo por endereço."""
        relatorio_de_exemplo_registrado(linhas=0)
        self.client.force_login(self.coordenador)
        resposta = self.client.get(self.url)
        self.assertContains(resposta, "Nenhum registro encontrado para os filtros selecionados")
        self.assertContains(resposta, mensagens.MR01_SUGESTAO_VAZIO)
        self.assertContains(resposta, f'disabled title="{mensagens.MR02_SEM_REGISTROS_EXPORTAR}"')
        self.assertNotContains(resposta, "/exportar/")
        arquivo = self.exportar("csv", "?curso=todos")
        self.assertRedirects(arquivo, f"{self.url}?curso=todos")

    def test_filtro_invalido_nao_consulta_nem_exporta(self):
        """FR-014: sem resultado de outro período e sem arquivo, com os filtros de volta."""

        @relatorio("com-datas", "Com datas", "D", "F", ("coordenador",), ("periodo",), 6)
        def consulta(usuario, filtros):
            raise AssertionError("Não deve consultar com filtro inválido")

        self.client.force_login(self.coordenador)
        consulta_url = "?data_inicial=2026-11-30&data_final=2026-11-01"
        resposta = self.client.get(
            reverse("relatorios:relatorio", args=["com-datas"]) + consulta_url
        )
        self.assertContains(resposta, "A data inicial não pode ser superior à data final")
        self.assertNotContains(resposta, "Mostrando:")
        arquivo = self.client.get(
            reverse("relatorios:exportar", args=["com-datas", "pdf"]) + consulta_url
        )
        self.assertEqual(arquivo.status_code, 302)
        self.assertIn("data_inicial=2026-11-30", arquivo["Location"])

    def test_falha_ao_gerar_volta_com_a_mr07(self):
        """Edge Cases: em qualquer formato, fica na tela e nada é baixado; o log só tem ids."""
        relatorio_de_exemplo_registrado()
        self.client.force_login(self.coordenador)
        for formato in ("pdf", "csv", "xlsx"):
            with self.subTest(formato=formato):
                with mock.patch.object(
                    exportacao, f"_{formato}", side_effect=ValueError("segredo")
                ), self.assertLogs("sigtcc.relatorios", "ERROR") as log:
                    resposta = self.exportar(formato)
                self.assertEqual(resposta.status_code, 302)
                self.assertTrue(resposta["Location"].startswith(self.url))
                self.assertContains(
                    self.client.get(resposta["Location"]), mensagens.MR07_FALHA_ARQUIVO
                )
                self.assertIn(f"formato={formato}", log.output[0])
                self.assertNotIn("segredo", log.output[0])

    def test_login_volta_ao_relatorio_pedido(self):
        """E1: sem sessão, vai ao login com o endereço do relatório."""
        relatorio_de_exemplo_registrado()
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(f"next={self.url}", resposta["Location"])

    def test_limpar_filtros_e_link_sem_query(self):
        """Heurística 3: o padrão vem de um link limpo."""
        relatorio_de_exemplo_registrado()
        self.client.force_login(self.coordenador)
        resposta = self.client.get(self.url + "?curso=todos")
        self.assertContains(resposta, f'<a class="btn txt" href="{self.url}">Limpar filtros</a>')


class TesteApresentacao(TesteRelatorios):
    """Padrão visual nos 6 relatórios: KPIs, gráfico, escape, JavaScript e filtros no endereço.

    [US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-CAD-14.1][FR-015][FR-070][FR-072][FR-075]
    [FR-076] (tasks T050)
    """

    def setUp(self):
        super().setUp()
        self.client.force_login(cenario_hostil())

    def abrir(self, id, consulta="?curso=todos"):
        return self.client.get(reverse("relatorios:relatorio", args=[id]) + consulta)

    def test_no_maximo_4_kpis_e_1_grafico(self):
        """Heurística 8: nos 6 relatórios, com os tipos do guia."""
        tipos = {
            "atividades-docente": "barras",
            "membros-externos": "barras",
            "producao-tccs": "barras",
            "artigos": None,
            "formacao-evasao": "empilhado",
            "historico-nucomp": "linhas",
        }
        for id, tipo in tipos.items():
            with self.subTest(relatorio=id):
                resposta = self.abrir(id)
                relatorio = resposta.context["relatorio"]
                self.assertLessEqual(len(relatorio.kpis), 4)
                self.assertEqual(relatorio.grafico.tipo if relatorio.grafico else None, tipo)
                html = resposta.content.decode()
                graficos_na_tela = html.count('role="img"')
                self.assertEqual(graficos_na_tela, 1 if tipo else 0)

    def test_layout_unico(self):
        """Heurísticas 1, 4 e 10: mesmas peças e na mesma ordem nos 6."""
        pecas = (
            'class="rel-menu"',
            "rel-acoes",
            "rel-frase",
            "data-filtros",
            "Mostrando:",
            "rel-tabela",
            "Como é calculado",
            "Gerado em",
        )
        for id in registro._RELATORIOS:
            with self.subTest(relatorio=id):
                html = self.abrir(id).content.decode()
                posicoes = [html.index(peca) for peca in pecas]
                self.assertEqual(posicoes, sorted(posicoes))

    def test_numeros_com_ponto_em_css_e_svg(self):
        """Research R9: o pt-br não troca o ponto de `width` e `points`."""
        self.assertNotRegex(self.abrir("formacao-evasao").content.decode(), r"width: \d+,\d+%")
        html = self.abrir("historico-nucomp").content.decode()
        self.assertRegex(html, r'<polyline[^>]+points="\d+\.\d+,\d+\.\d+"')

    def test_conteudo_hostil_escapado_nos_atributos(self):
        """Research R9: aria-label, title e texto sempre com autoescape."""
        usuario = docente_de(EC)
        Usuarios.objects.filter(pk=usuario.pk).update(usu_nome='"><script>x</script>')
        tcc = aluno_com_status(criar_turma_de(usuario))
        sessao_realizada(tcc, banca_de(usuario, docente_de(EC), docente_de(EC)))
        html = self.abrir("atividades-docente").content.decode()
        self.assertNotIn("<script>x", html)
        self.assertIn("&lt;script&gt;x", html)

    def test_funciona_sem_javascript(self):
        """Research R8: botão Aplicar e sub-listas abertas, sem `hidden` no servidor."""
        html = self.abrir("atividades-docente").content.decode()
        self.assertIn(">Aplicar<", html.replace('<span class="ms">filter_list</span>', ">"))
        self.assertIn('aria-expanded="true"', html)
        self.assertNotIn("<tr hidden", html)

    def test_filtros_no_endereco(self):
        """Heurística 3: formulário GET; os links da lista não levam filtros, e os filtros voltam
        ao padrão ao abrir outro relatório (RBN-CAD-14.1)."""
        html = self.abrir("artigos", "?curso=todos&ano_semestre=2026-2").content.decode()
        self.assertIn('<form method="get"', html)
        self.assertIn(f'href="{reverse("relatorios:relatorio", args=["formacao-evasao"])}"', html)
        self.assertIn(f'href="{reverse("relatorios:exportar", args=["artigos", "csv"])}?', html)
        limpo = self.abrir("formacao-evasao", "")
        self.assertNotEqual(limpo.context["form"]["curso"].value(), "todos")

    def test_limpar_filtros_volta_ao_padrao(self):
        """Heurística 3: o link não tem query, e sem query vêm os padrões."""
        url = reverse("relatorios:relatorio", args=["producao-tccs"])
        html = self.abrir("producao-tccs", "?abrangencia=concluidos").content.decode()
        self.assertIn(f'<a class="btn txt" href="{url}">Limpar filtros</a>', html)
        self.assertEqual(
            self.abrir("producao-tccs", "").context["form"]["abrangencia"].value(), "todos"
        )

    def test_lista_em_links_e_cabecalho_com_definicao(self):
        """FR-071 e heurística 10."""
        html = self.abrir("formacao-evasao").content.decode()
        self.assertIn(f'title="{mensagens.DEFINICAO_MATRICULADOS}"', html)
        self.assertIn('aria-current="page"', html)


class TestePalavrasInteiras(SimpleTestCase):
    """Palavra com hífen ou travessão numa linha só, com o conteúdo escapado.

    fix(core): manter palavras inteiras nas tabelas em telas pequenas [FR-070]
    """

    def test_envolve_so_a_palavra_com_hifen(self):
        """O resto do texto continua quebrando entre palavras."""
        from sigtcc.apps.relatorios.templatetags.relatorios_tags import palavras_inteiras

        self.assertEqual(
            palavras_inteiras("Interação Humano-Computador"),
            'Interação <span class="nw">Humano-Computador</span>',
        )
        self.assertEqual(palavras_inteiras("14:00–17:40"), '<span class="nw">14:00–17:40</span>')
        self.assertEqual(palavras_inteiras(3), "3")

    def test_escapa_o_conteudo(self):
        """Autoescape mantido, inclusive dentro do <span>."""
        from sigtcc.apps.relatorios.templatetags.relatorios_tags import palavras_inteiras

        self.assertEqual(
            palavras_inteiras("<b>x-y</b>"),
            '<span class="nw">&lt;b&gt;x-y&lt;/b&gt;</span>',
        )
