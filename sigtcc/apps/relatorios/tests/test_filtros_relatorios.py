"""Filtros dos relatórios: padrões, atalhos, datas e valores forjados (research R2 a R4).

[US-31][US-47][RBN-DEF-01.5][RBN-CAD-14.1][FR-010][FR-012][FR-013][FR-014][FR-015][FR-016]
(tasks T008)
"""

from datetime import date

from django.http import QueryDict

from sigtcc.apps.cadastro.tests.apoio_contas import coordenador_de, secretaria_de
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, SI, criar_turma_de, curso
from sigtcc.apps.defesa import mensagens as mensagens_defesa
from sigtcc.apps.defesa.tests.apoio_defesa import docente
from sigtcc.apps.relatorios.forms import FiltroRelatorioForm
from sigtcc.apps.relatorios.registro import RelatorioRegistrado
from sigtcc.apps.relatorios.tests.apoio_relatorios import TesteRelatorios

HOJE = date(2026, 11, 18)
TODOS_OS_FILTROS = ("periodo", "ano_semestre", "curso", "docente", "agrupar_por", "abrangencia")


def registrado(filtros=TODOS_OS_FILTROS):
    """Relatório de exemplo, sem passar pelo registro global."""
    return RelatorioRegistrado(
        "exemplo", "Exemplo", "Descrição", "Frase", ("docente",), filtros, 1, None
    )


class FiltroValidado(FiltroRelatorioForm):
    """Atalho dos testes: valida e devolve os filtros."""

    def filtros_validos(self):
        self.full_clean()
        assert not self.errors, self.errors
        return self.filtros()


class TesteFiltros(TesteRelatorios):
    """Formulário com o endereço recebido."""

    def setUp(self):
        super().setUp()
        self.coordenador = coordenador_de(SI)
        self.turma = criar_turma_de(docente(), ano=2026, semestre=2)
        criar_turma_de(docente(), ano=2025, semestre=2)

    def form(self, consulta="", usuario=None, filtros=TODOS_OS_FILTROS):
        return FiltroValidado(
            QueryDict(consulta),
            usuario=usuario or self.coordenador,
            registrado=registrado(filtros),
            hoje=HOJE,
        )

    def test_padroes_aparecem_no_formulario_vinculado(self):
        """US-31 passo 3 e US-47 cenário 5: o valor aplicado é o renderizado."""
        form = self.form()
        self.assertEqual(form["atalho"].value(), "periodo_letivo")
        self.assertEqual(form["ano_semestre"].value(), "2026-2")
        self.assertEqual(form["curso"].value(), str(curso(SI).pk))
        self.assertEqual(form["docente"].value(), "todos")
        self.assertEqual(form["agrupar_por"].value(), "curso")
        self.assertEqual(form["abrangencia"].value(), "todos")
        self.assertIn(f'value="{curso(SI).pk}" selected', str(form["curso"]))

    def test_filtros_do_periodo_letivo(self):
        """Período Letivo por ano e semestre, nunca junto com datas."""
        filtros = self.form("ano_semestre=2025-2").filtros_validos()
        self.assertEqual((filtros.ano, filtros.semestre), (2025, 2))
        self.assertIsNone(filtros.inicio)
        self.assertEqual(filtros.cur_id, curso(SI).pk)
        self.assertIn("2025/2", filtros.resumo())

    def test_atalho_preenche_as_datas(self):
        """US-31 cenário 3: Este Mês preenche o primeiro e o último dia do mês."""
        form = self.form("atalho=este_mes")
        self.assertEqual(form["data_inicial"].value(), "2026-11-01")
        self.assertEqual(form["data_final"].value(), "2026-11-30")
        filtros = form.filtros_validos()
        self.assertEqual((filtros.inicio, filtros.fim), (date(2026, 11, 1), date(2026, 11, 30)))
        self.assertIsNone(filtros.ano)
        self.assertIn("01/11/2026 a 30/11/2026", filtros.resumo())

    def test_trocar_o_atalho_descarta_as_datas(self):
        """Research R3: as datas de Este Mês não vencem a troca para Esta Semana."""
        form = self.form(
            "atalho=esta_semana&atalho_anterior=este_mes"
            "&data_inicial=2026-11-01&data_final=2026-11-30"
        )
        self.assertEqual(form["data_inicial"].value(), "2026-11-16")
        self.assertEqual(form["data_final"].value(), "2026-11-22")
        self.assertEqual(form["atalho_anterior"].value(), "esta_semana")

    def test_voltar_ao_periodo_letivo_limpa_as_datas(self):
        """Research R3: com Período Letivo, as datas ficam vazias."""
        form = self.form(
            "atalho=periodo_letivo&atalho_anterior=este_mes"
            "&data_inicial=2026-11-01&data_final=2026-11-30"
        )
        self.assertEqual(form["data_inicial"].value(), "")
        self.assertIsNone(form.filtros_validos().inicio)

    def test_mesmo_atalho_mantem_as_datas_editadas(self):
        """US-31 cenário 2: datas informadas valem como intervalo e vencem o Ano/Semestre."""
        filtros = self.form(
            "atalho=periodo_letivo&atalho_anterior=periodo_letivo&ano_semestre=2025-2"
            "&data_inicial=2026-09-01&data_final=2026-09-30"
        ).filtros_validos()
        self.assertEqual((filtros.inicio, filtros.fim), (date(2026, 9, 1), date(2026, 9, 30)))
        self.assertIsNone(filtros.ano)

    def test_sem_atalho_anterior_conta_como_nao_trocou(self):
        """Link digitado: as datas valem."""
        filtros = self.form(
            "atalho=periodo_letivo&data_inicial=2026-09-01&data_final=2026-09-30"
        ).filtros_validos()
        self.assertEqual(filtros.inicio, date(2026, 9, 1))

    def test_datas_invertidas_com_o_erro_junto_ao_campo(self):
        """US-31 E2: mensagem exata em Data Inicial, sem filtros."""
        form = self.form("data_inicial=2026-11-30&data_final=2026-11-01")
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["data_inicial"],
            ["A data inicial não pode ser superior à data final"],
        )
        self.assertEqual(form.non_field_errors(), [])

    def test_trocar_o_atalho_sai_do_erro_de_datas(self):
        """Research R3: o usuário não fica preso às datas invertidas."""
        form = self.form(
            "atalho=este_mes&atalho_anterior=periodo_letivo"
            "&data_inicial=2026-11-30&data_final=2026-11-01"
        )
        self.assertTrue(form.is_valid())

    def test_data_inexistente_e_data_sozinha(self):
        """US-40 E3 e E4: mesma mensagem do filtro da feat-07."""
        for consulta, campo in (
            ("data_inicial=2026-02-31&data_final=2026-03-01", "data_inicial"),
            ("data_inicial=2026-02-01", "data_final"),
        ):
            with self.subTest(consulta=consulta):
                form = self.form(consulta)
                self.assertFalse(form.is_valid())
                self.assertEqual(form.errors[campo], [mensagens_defesa.DATA_INVALIDA])

    def test_valores_forjados_voltam_ao_padrao(self):
        """Research R4: sem erro de campo, que desligaria a validação de datas."""
        form = self.form(
            "atalho=xyz&ano_semestre=1900-9&agrupar_por=x&abrangencia=x&docente=abc"
            "&data_inicial=2026-11-30&data_final=2026-11-01"
        )
        self.assertFalse(form.is_valid())
        self.assertIn("data_inicial", form.errors)
        self.assertEqual(form["atalho"].value(), "periodo_letivo")
        self.assertEqual(form["ano_semestre"].value(), "2026-2")
        self.assertEqual(form["agrupar_por"].value(), "curso")
        self.assertEqual(form["abrangencia"].value(), "todos")
        self.assertEqual(form["docente"].value(), "todos")

    def test_identificadores_que_quebrariam_o_int(self):
        """Research R4: "²" e número gigante voltam ao padrão, sem erro 500."""
        for valor in ("²", "٣", "9" * 5000):
            with self.subTest(valor=valor[:5]):
                form = self.form(f"curso={valor}&docente={valor}")
                self.assertEqual(form.filtros_validos().cur_id, curso(SI).pk)
                self.assertIsNone(form.filtros_validos().doc_id)

    def test_curso_todos_e_outro_curso(self):
        """RBN-CAD-14.1: a troca afeta só a visualização."""
        self.assertIsNone(self.form("curso=todos").filtros_validos().cur_id)
        self.assertEqual(self.form(f"curso={curso(EC).pk}").filtros_validos().cur_id, curso(EC).pk)

    def test_secretaria_vem_com_o_curso_vinculado(self):
        """US-47 fluxo D."""
        form = self.form(usuario=secretaria_de(EC))
        self.assertEqual(form["curso"].value(), str(curso(EC).pk))
        self.assertTrue(form.filtros_validos().gestao)

    def test_docente_escolhido_nao_cita_o_curso(self):
        """Research R14: o Curso não foi aplicado (P2)."""
        outro = docente(EC)
        filtros = self.form(f"docente={outro.pk}").filtros_validos()
        self.assertEqual(filtros.doc_id, outro.pk)
        self.assertNotIn("Sistemas de Informação", filtros.resumo())

    def test_fora_da_gestao_o_recorte_e_do_proprio_usuario(self):
        """FR-016: campo ausente nunca vira "Todos"; valor forjado não entra."""
        usuario, outro = docente(), docente()
        form = self.form(f"docente={outro.pk}&curso=todos&curso={curso(EC).pk}", usuario=usuario)
        self.assertNotIn("docente", form.fields)
        self.assertNotIn("curso", form.fields)
        filtros = form.filtros_validos()
        self.assertFalse(filtros.gestao)
        self.assertEqual(filtros.doc_id, usuario.pk)

    def test_so_os_campos_declarados(self):
        """Histórico: só o filtro Curso, sem período."""
        form = self.form(filtros=("curso",))
        self.assertEqual(list(form.fields), ["curso"])
        filtros = form.filtros_validos()
        self.assertIsNone(filtros.ano)
        self.assertIsNone(filtros.periodo_q())

    def test_so_ano_semestre_com_rotulo_da_us(self):
        """US-32 passo 3: filtro Período letivo, sem atalho."""
        form = self.form(filtros=("ano_semestre", "curso"))
        self.assertEqual(form.fields["ano_semestre"].label, "Período letivo")
        self.assertNotIn("atalho", form.fields)
        self.assertEqual(form.filtros_validos().ano, 2026)

    def test_periodo_atual_sem_turma_entra_na_lista(self):
        """FR-013: mesmo sem turma, o período atual está na lista."""
        from sigtcc.apps.cadastro.choices import StatusTurma
        from sigtcc.apps.cadastro.models import Turmas

        Turmas.objects.update(tur_status=StatusTurma.ARQUIVADA)
        form = FiltroRelatorioForm(
            QueryDict(""),
            usuario=self.coordenador,
            registrado=registrado(),
            hoje=date(2030, 3, 1),
        )
        self.assertIn(("2030-1", "2030/1"), list(form.fields["ano_semestre"].choices))

    def test_periodo_q_com_ano_e_prefixo(self):
        """Contrato §2: o período letivo escolhido, a partir de outro modelo."""
        q = self.form("ano_semestre=2025-2").filtros_validos().periodo_q("ban_def__")
        self.assertIn(("ban_def__def_tcc__tcc_tur__tur_ano", 2025), q.children)

    def test_filtro_herdado_proibido(self):
        """Research R2: o filtro() herdado recuaria para o Período Letivo."""
        with self.assertRaises(NotImplementedError):
            self.form().filtro()

    def test_querystring_canonica(self):
        """FR-018: a exportação recebe o que foi aplicado."""
        consulta = self.form("atalho=este_mes").filtros_validos().querystring()
        self.assertIn("atalho_anterior=este_mes", consulta)
        self.assertIn("data_inicial=2026-11-01", consulta)
        self.assertIn(f"curso={curso(SI).pk}", consulta)
