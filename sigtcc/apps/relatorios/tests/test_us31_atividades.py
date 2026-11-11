"""US-31: Painel de atividades por docente (cenários 1.1 a 1.11, 1.14 e 1.15 e as regras de
contagem).

[US-31][RBN-REL-01.1][RBN-DEF-01.5][RBN-CAD-10.4][RBN-CAD-14.1][FR-021][FR-022][FR-023][FR-024]
[FR-025][FR-027][SC-001] (tasks T021, T022, T025 e T026)
"""

from datetime import date, datetime
from io import BytesIO

from django.db import connection
from django.http import QueryDict
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from pypdf import PdfReader

from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    StatusConta,
    StatusCoorientacao,
    StatusOrientacao,
    StatusTCC,
)
from sigtcc.apps.cadastro.models import Usuarios
from sigtcc.apps.cadastro.tests.apoio_contas import coordenador_de, docente_de, secretaria_de
from sigtcc.apps.cadastro.tests.apoio_orientacao import (
    criar_externo,
    vincular_coorientador,
    vincular_orientador,
)
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, SI, criar_turma_de, curso
from sigtcc.apps.defesa import services_defesa
from sigtcc.apps.defesa.choices import PapelBanca
from sigtcc.apps.defesa.services_defesa import intervalo_do_atalho
from sigtcc.apps.relatorios import graficos, mensagens, registro, services_relatorios
from sigtcc.apps.relatorios.forms import FiltroRelatorioForm
from sigtcc.apps.relatorios.tests.apoio_relatorios import (
    TesteRelatorios,
    aluno_com_status,
    banca_de,
    registrar_status,
    sessao_realizada,
)

ID = "atividades-docente"
NOME_ATOR = "Docente Alvo"


class TesteAtividades(TesteRelatorios):
    """Cenário comum: um docente alvo, turmas de TCC 1 e TCC 2 em 2026/2."""

    def setUp(self):
        super().setUp()
        self.professor = docente_de(EC)
        self.alvo = docente_de(EC)
        Usuarios.objects.filter(pk=self.alvo.pk).update(usu_nome=NOME_ATOR)
        self.alvo.refresh_from_db()
        self.turma1 = criar_turma_de(self.professor, ano=2026, semestre=2)
        self.turma2 = criar_turma_de(
            self.professor, descricao=DescricaoTurma.TCC_2, ano=2026, semestre=2
        )
        self.url = reverse("relatorios:relatorio", args=[ID])

    def abrir(self, usuario, consulta=""):
        self.client.force_login(usuario)
        return self.client.get(self.url + consulta)

    def consulta(self, usuario, texto=""):
        """Relatório direto do serviço, sem a tela."""
        form = FiltroRelatorioForm(QueryDict(texto), usuario=usuario, registrado=registro.obter(ID))
        self.assertTrue(form.is_valid(), form.errors)
        return services_relatorios.atividades_docente(usuario, form.filtros())

    def linha(self, relatorio, nome=NOME_ATOR):
        return next(item for item in relatorio.linhas if item.valores["docente"] == nome)


class TesteCenariosDaUS(TesteAtividades):
    """Cenários de aceite da US-31."""

    def test_cenario_1_docente_consulta_e_exporta(self):
        """1.1: uma linha, sem os filtros Docente e Curso, e o PDF com linha e sub-listas."""
        tcc = aluno_com_status(self.turma1, orientador=self.alvo, nome="Aluna Um")
        aluno_com_status(self.turma2, orientador=self.alvo)
        docente_de(EC)
        resposta = self.abrir(self.alvo, "?atalho=periodo_letivo&ano_semestre=2026-2")
        relatorio = resposta.context["relatorio"]
        self.assertEqual(len(relatorio.linhas), 1)
        valores = relatorio.linhas[0].valores
        self.assertEqual((valores["tcc1"], valores["tcc2"]), (1, 1))
        self.assertEqual(valores["curso"], EC)
        form = resposta.context["form"]
        self.assertNotIn("docente", form.fields)
        self.assertNotIn("curso", form.fields)
        arquivo = self.client.get(
            reverse("relatorios:exportar", args=[ID, "pdf"]) + "?ano_semestre=2026-2"
        )
        leitor = PdfReader(BytesIO(arquivo.content))
        texto = " ".join(pagina.extract_text() for pagina in leitor.pages)
        self.assertIn(NOME_ATOR, texto)
        self.assertIn("Aluna Um", texto)
        self.assertIn(tcc.tcc_titulo, texto)

    def test_cenario_2_periodo_por_datas(self):
        """1.2: considera apenas o intervalo informado."""
        turma = self.turma1
        dentro = aluno_com_status(turma)
        fora = aluno_com_status(turma)
        vincular_orientador(dentro, self.alvo, quando=datetime(2026, 9, 10, 8))
        vincular_orientador(fora, self.alvo, quando=datetime(2026, 10, 10, 8))
        sessao_realizada(
            dentro, banca_de(self.alvo, self.professor, docente_de(EC)), date(2026, 9, 20)
        )
        sessao_realizada(
            fora, banca_de(self.alvo, self.professor, docente_de(EC)), date(2026, 10, 20)
        )
        relatorio = self.consulta(self.alvo, "data_inicial=2026-09-01&data_final=2026-09-30")
        valores = relatorio.linhas[0].valores
        self.assertEqual((valores["tcc1"], valores["bancas"]), (1, 1))

    def test_cenario_3_atalho_este_mes(self):
        """1.3: preenche o primeiro e o último dia do mês."""
        resposta = self.abrir(self.alvo, "?atalho=este_mes")
        inicio, fim = intervalo_do_atalho("este_mes")
        form = resposta.context["form"]
        self.assertEqual(form["data_inicial"].value(), inicio.isoformat())
        self.assertEqual(form["data_final"].value(), fim.isoformat())
        self.assertContains(resposta, f"{inicio:%d/%m/%Y} a {fim:%d/%m/%Y}")

    def test_cenario_4_coordenador_ve_todos(self):
        """1.4: filtros Docente, com "Todos", e Curso, e uma linha por docente."""
        coordenador = coordenador_de(SI)
        outro = docente_de(SI)
        docente_de(EC)
        resposta = self.abrir(coordenador)
        form = resposta.context["form"]
        self.assertEqual(form["docente"].value(), "todos")
        self.assertEqual(form["curso"].value(), str(curso(SI).pk))
        aluno_com_status(self.turma1, orientador=outro)
        relatorio = self.abrir(coordenador).context["relatorio"]
        self.assertEqual(
            {linha.valores["docente"] for linha in relatorio.linhas},
            {coordenador.usu_nome, outro.usu_nome},
        )

    def test_cenario_5_secretaria_filtra_um_docente(self):
        """1.5: só a linha desse docente, mesmo de outro curso (P2)."""
        secretaria = secretaria_de(SI)
        aluno_com_status(self.turma1, orientador=self.alvo)
        docente_de(EC)
        relatorio = self.abrir(secretaria, f"?docente={self.alvo.pk}").context["relatorio"]
        self.assertEqual([item.valores["docente"] for item in relatorio.linhas], [NOME_ATOR])

    def test_cenario_6_sem_orientacoes(self):
        """1.6: a sub-lista exibe "Nenhum registro"."""
        resposta = self.abrir(self.alvo)
        self.assertEqual(resposta.context["linhas"][0].sublistas[0].linhas, [])
        self.assertContains(resposta, "Orientações e coorientações")
        self.assertContains(resposta, "<p>Nenhum registro</p>", count=2, html=True)

    def test_cenario_7_sem_bancas(self):
        """1.7: "Nenhum registro" e Total de Bancas 0."""
        aluno_com_status(self.turma1, orientador=self.alvo)
        resposta = self.abrir(self.alvo)
        self.assertEqual(resposta.context["relatorio"].linhas[0].valores["bancas"], 0)
        self.assertContains(resposta, "<p>Nenhum registro</p>", count=1, html=True)

    def test_cenario_8_sem_login_volta_ao_relatorio(self):
        """1.8: login e retorno ao relatório."""
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 302)
        self.assertIn("next=/relatorios/atividades-docente/", resposta["Location"])

    def test_cenario_9_datas_invertidas(self):
        """1.9: não atualiza e exibe a mensagem exata."""
        resposta = self.abrir(self.alvo, "?data_inicial=2026-11-30&data_final=2026-11-01")
        self.assertContains(resposta, "A data inicial não pode ser superior à data final")
        self.assertIsNone(resposta.context["relatorio"])

    def test_cenario_10_curso_sem_atividade(self):
        """1.10: tabela vazia, mensagem exata e botões desabilitados."""
        resposta = self.abrir(coordenador_de(SI))
        self.assertContains(resposta, "Nenhum registro encontrado para os filtros selecionados")
        self.assertContains(resposta, "disabled", count=3)
        self.assertNotContains(resposta, "/exportar/")

    def test_cenario_11_aluno_sem_o_item(self):
        """1.11: o item Relatórios não aparece."""
        tcc = aluno_com_status(self.turma1, status_conta=StatusConta.ATIVA)
        self.client.force_login(tcc.tcc_alu.alu)
        resposta = self.client.get(reverse("cadastro:perfil"))
        rotulos = [item["rotulo"] for item in resposta.context["menu_itens"]]
        self.assertNotIn("Relatórios", rotulos)

    def test_cenario_14_professor_da_disciplina_como_docente(self):
        """1.14: só o Painel, com a própria linha."""
        resposta = self.abrir(self.professor)
        # Dos relatórios da spec 010, só o Painel; a spec 011 acrescenta os operacionais, que o
        # Professor da Disciplina também abre (RAN-REL-03). [US-31][US-48][US-49][US-34][US-35]
        operacionais = {"defesas-realizadas", "turmas-alunos", "aluno-orientador", "horas-ouvintes"}
        ids = [item.id for item in resposta.context["lista"]]
        self.assertEqual([id for id in ids if id not in operacionais], [ID])
        self.assertEqual(set(ids) - {ID}, operacionais)
        self.assertEqual(len(resposta.context["relatorio"].linhas), 1)
        self.assertEqual(
            resposta.context["relatorio"].linhas[0].valores["docente"],
            self.professor.usu_nome,
        )

    def test_cenario_15_gestao_mostra_docentes_com_zeros(self):
        """1.15: um de 3 docentes com atividade; a tabela mostra os 3."""
        coordenador = coordenador_de(SI)
        ativo, parado = docente_de(SI), docente_de(SI)
        aluno_com_status(self.turma1, orientador=ativo)
        relatorio = self.abrir(coordenador).context["relatorio"]
        self.assertEqual(len(relatorio.linhas), 3)
        self.assertEqual(self.linha(relatorio, parado.usu_nome).valores["tcc1"], 0)
        self.assertEqual(self.linha(relatorio, ativo.usu_nome).valores["tcc1"], 1)

    def test_docente_escolhido_sem_atividade_tem_a_linha(self):
        """FR-021: com zeros, sem E3 e com exportação."""
        coordenador = coordenador_de(EC)
        resposta = self.abrir(coordenador, f"?docente={self.alvo.pk}")
        self.assertTrue(resposta.context["relatorio"].tem_registros)
        self.assertEqual(len(resposta.context["relatorio"].linhas), 1)


class TesteRegrasDeContagem(TesteAtividades):
    """Regras de FR-022 a FR-027."""

    def test_status_final_encerra_o_vinculo_sem_data_de_fim(self):
        """R18: orientação e coorientação Ativas terminam na data do Status final."""
        for status in (StatusTCC.CONCLUIDO, StatusTCC.REPROVADO, StatusTCC.APROVADO_PARA_TCC_2):
            with self.subTest(status=status):
                tcc = aluno_com_status(self.turma1, quando=datetime(2026, 2, 1, 8))
                orientacao = vincular_orientador(tcc, self.alvo, quando=datetime(2026, 3, 1, 8))
                coorientacao = vincular_coorientador(
                    tcc, self.professor, quando=datetime(2026, 3, 1, 8)
                )
                registrar_status(tcc, status, datetime(2026, 6, 30, 8))
                antes = "data_inicial=2026-06-01&data_final=2026-06-30"
                depois = "data_inicial=2026-07-01&data_final=2026-07-31"
                self.assertEqual(self.consulta(self.alvo, antes).linhas[0].valores["tcc1"], 1)
                self.assertEqual(self.consulta(self.alvo, depois).linhas[0].valores["tcc1"], 0)
                self.assertEqual(
                    self.consulta(self.professor, antes).linhas[0].valores["coorientacoes"], 1
                )
                self.assertEqual(
                    self.consulta(self.professor, depois).linhas[0].valores["coorientacoes"], 0
                )
                orientacao.delete()
                coorientacao.delete()

    def test_aprovado_ainda_em_vigor(self):
        """R18: Aprovado e Aprovado com Correções aguardam a Versão Final."""
        for status in (StatusTCC.APROVADO, StatusTCC.APROVADO_COM_CORRECOES):
            with self.subTest(status=status):
                tcc = aluno_com_status(self.turma2, quando=datetime(2026, 2, 1, 8))
                orientacao = vincular_orientador(tcc, self.alvo, quando=datetime(2026, 3, 1, 8))
                registrar_status(tcc, status, datetime(2026, 6, 30, 8))
                relatorio = self.consulta(
                    self.alvo, "data_inicial=2026-07-01&data_final=2026-07-31"
                )
                self.assertEqual(relatorio.linhas[0].valores["tcc2"], 1)
                orientacao.delete()

    def test_data_de_fim_prevalece(self):
        """R18: a data real de fim vence a do Status final."""
        tcc = aluno_com_status(self.turma1, quando=datetime(2026, 2, 1, 8))
        orientacao = vincular_orientador(tcc, self.alvo, quando=datetime(2026, 3, 1, 8))
        registrar_status(tcc, StatusTCC.APROVADO_PARA_TCC_2, datetime(2026, 6, 30, 8))
        orientacao.ori_status = StatusOrientacao.ENCERRADA
        orientacao.ori_data_fim = datetime(2026, 8, 1, 8)
        orientacao.save()
        relatorio = self.consulta(self.alvo, "data_inicial=2026-07-01&data_final=2026-07-31")
        self.assertEqual(relatorio.linhas[0].valores["tcc1"], 1)

    def test_intervalo_que_cruza_a_matricula_no_tcc2(self):
        """FR-022 e FR-023: conta em TCC 1 e TCC 2; coorientação, uma vez."""
        instante = datetime(2026, 8, 1, 8)
        tcc1 = aluno_com_status(self.turma1)
        aluno = tcc1.tcc_alu
        tcc2 = aluno_com_status(self.turma2, aluno=aluno)
        orientacao = vincular_orientador(tcc1, self.alvo, quando=datetime(2026, 3, 1, 8))
        orientacao.ori_status, orientacao.ori_data_fim = StatusOrientacao.ENCERRADA, instante
        orientacao.save()
        vincular_orientador(tcc2, self.alvo, quando=instante)
        coorientacao = vincular_coorientador(tcc1, self.alvo, quando=datetime(2026, 3, 1, 8))
        coorientacao.coo_status, coorientacao.coo_data_fim = (
            StatusCoorientacao.ENCERRADA,
            instante,
        )
        coorientacao.save()
        vincular_coorientador(tcc2, self.alvo, quando=instante)
        valores = (
            self.consulta(self.alvo, "data_inicial=2026-07-01&data_final=2026-08-31")
            .linhas[0]
            .valores
        )
        self.assertEqual((valores["tcc1"], valores["tcc2"], valores["coorientacoes"]), (1, 1, 1))

    def test_troca_de_orientador_conta_os_dois(self):
        """FR-023: vínculos Encerrados contam, e a soma pode passar do número de alunos."""
        tcc = aluno_com_status(self.turma1)
        antigo = vincular_orientador(tcc, self.alvo, quando=datetime(2026, 8, 1, 8))
        antigo.ori_status = StatusOrientacao.ENCERRADA
        antigo.ori_data_fim = datetime(2026, 9, 1, 8)
        antigo.save()
        vincular_orientador(tcc, self.professor, quando=datetime(2026, 9, 1, 8))
        self.assertEqual(self.consulta(self.alvo).linhas[0].valores["tcc1"], 1)
        self.assertEqual(self.consulta(self.professor).linhas[0].valores["tcc1"], 1)

    def test_periodo_passado_com_vinculo_encerrado(self):
        """FR-023: a matrícula no TCC 2 encerra o vínculo do TCC 1, que continua contando."""
        passada = criar_turma_de(self.professor, ano=2026, semestre=1)
        tcc = aluno_com_status(passada)
        orientacao = vincular_orientador(tcc, self.alvo)
        orientacao.ori_status = StatusOrientacao.ENCERRADA
        orientacao.ori_data_fim = datetime(2026, 8, 1, 8)
        orientacao.save()
        self.assertEqual(
            self.consulta(self.alvo, "ano_semestre=2026-1").linhas[0].valores["tcc1"], 1
        )
        self.assertEqual(
            self.consulta(self.alvo, "ano_semestre=2026-2").linhas[0].valores["tcc1"], 0
        )

    def test_aluno_conta_uma_vez_por_coluna(self):
        """FR-023: dois vínculos com o mesmo docente, um aluno e uma linha na sub-lista."""
        tcc = aluno_com_status(self.turma1)
        antigo = vincular_orientador(tcc, self.alvo, quando=datetime(2026, 8, 1, 8))
        antigo.ori_status = StatusOrientacao.ENCERRADA
        antigo.ori_data_fim = datetime(2026, 9, 1, 8)
        antigo.save()
        vincular_orientador(tcc, self.alvo, quando=datetime(2026, 10, 1, 8))
        linha = self.consulta(self.alvo).linhas[0]
        self.assertEqual(linha.valores["tcc1"], 1)
        self.assertEqual(len(linha.sublistas[0].linhas), 1)

    def test_coorientador_externo_nao_gera_linha(self):
        """Edge Case: o externo não é docente do NUCOMP."""
        tcc = aluno_com_status(self.turma1)
        vincular_coorientador(tcc, externo=criar_externo())
        relatorio = self.consulta(coordenador_de(EC), "docente=todos")
        self.assertFalse(relatorio.tem_registros)

    def test_suplente(self):
        """FR-024: o acionado conta, com o papel "Suplente"; o não acionado e o substituído, não."""
        tcc = aluno_com_status(self.turma2)
        titular, acionado, reserva = docente_de(EC), docente_de(EC), docente_de(EC)
        sessao_realizada(
            tcc,
            [
                (self.alvo, PapelBanca.ORIENTADOR_PRESIDENTE),
                (self.professor, PapelBanca.PRIMEIRO_AVALIADOR),
                (acionado, PapelBanca.SEGUNDO_AVALIADOR, titular),
                (reserva, PapelBanca.SUPLENTE),
            ],
        )
        linha = self.consulta(acionado).linhas[0]
        self.assertEqual(linha.valores["bancas"], 1)
        self.assertEqual(linha.sublistas[1].linhas[0].valores["papel"], "Suplente")
        self.assertEqual(self.consulta(reserva).linhas[0].valores["bancas"], 0)
        self.assertEqual(self.consulta(titular).linhas[0].valores["bancas"], 0)

    def test_equivale_a_membros_efetivos(self):
        """R7: o filtro por papel é o mesmo que membros_efetivos usa."""
        tcc = aluno_com_status(self.turma2)
        suplente = docente_de(EC)
        sessao = sessao_realizada(
            tcc, banca_de(self.alvo, self.professor, docente_de(EC), suplente)
        )
        efetivos = services_defesa.membros_efetivos(sessao)
        for membro in efetivos:
            self.assertEqual(self.consulta(membro).linhas[0].valores["bancas"], 1)
        self.assertNotIn(suplente, efetivos)
        self.assertEqual(self.consulta(suplente).linhas[0].valores["bancas"], 0)

    def test_so_sessoes_realizadas(self):
        """FR-024: sessão de outro status não conta."""
        from sigtcc.apps.defesa.choices import StatusSessao

        tcc = aluno_com_status(self.turma2)
        sessao = sessao_realizada(tcc, banca_de(self.alvo, self.professor, docente_de(EC)))
        sessao.def_status = StatusSessao.AGENDADA
        sessao.save()
        self.assertEqual(self.consulta(self.alvo).linhas[0].valores["bancas"], 0)

    def test_inativos_so_com_atividade(self):
        """FR-021: Inativo e Aguardando Ativação só com atividade no período."""
        coordenador = coordenador_de(EC)
        inativo = docente_de(EC, status=StatusConta.INATIVA)
        parado = docente_de(EC, status=StatusConta.INATIVA)
        aguardando = docente_de(EC, status=StatusConta.AGUARDANDO_ATIVACAO)
        aluno_com_status(self.turma1, orientador=inativo)
        nomes = {
            item.valores["docente"] for item in self.consulta(coordenador, "curso=todos").linhas
        }
        self.assertIn(inativo.usu_nome, nomes)
        self.assertNotIn(parado.usu_nome, nomes)
        self.assertNotIn(aguardando.usu_nome, nomes)

    def test_filtro_curso_por_lotacao_sem_cortar_contagens(self):
        """FR-027: docente de SI com aluno de EC conta toda a atividade."""
        coordenador = coordenador_de(SI)
        lotado_em_si = docente_de(SI)
        turma_si = criar_turma_de(self.professor, curso_nome=SI)
        aluno_com_status(self.turma1, orientador=lotado_em_si)
        aluno_com_status(turma_si, orientador=lotado_em_si)
        aluno_com_status(self.turma1, orientador=self.alvo)
        relatorio = self.consulta(coordenador)
        self.assertEqual(self.linha(relatorio, lotado_em_si.usu_nome).valores["tcc1"], 2)
        self.assertNotIn(NOME_ATOR, [item.valores["docente"] for item in relatorio.linhas])

    def test_sublistas_em_ordem(self):
        """R7: bancas por data; orientações por nome do aluno."""
        beta = aluno_com_status(self.turma2, orientador=self.alvo, nome="Beta")
        alfa = aluno_com_status(self.turma2, orientador=self.alvo, nome="Alfa")
        membros = banca_de(self.alvo, self.professor, docente_de(EC))
        sessao_realizada(beta, membros, date(2026, 11, 20))
        sessao_realizada(alfa, membros, date(2026, 11, 10))
        vinculos, bancas = self.consulta(self.alvo).linhas[0].sublistas
        self.assertEqual([i.valores["aluno"] for i in vinculos.linhas], ["Alfa", "Beta"])
        self.assertEqual([i.valores["data"] for i in bancas.linhas], ["10/11/2026", "20/11/2026"])


class TesteApresentacao(TesteAtividades):
    """KPIs, gráfico e ajuda. [FR-072][FR-075][FR-076]"""

    def test_kpis_do_docente_sem_grafico(self):
        """Guia: os 4 números já dizem tudo."""
        aluno_com_status(self.turma1, orientador=self.alvo)
        relatorio = self.consulta(self.alvo)
        self.assertEqual(
            [(kpi.rotulo, kpi.valor) for kpi in relatorio.kpis],
            [
                ("Orientandos TCC 1", 1),
                ("Orientandos TCC 2", 0),
                ("Coorientações", 0),
                ("Bancas", 0),
            ],
        )
        self.assertIsNone(relatorio.grafico)

    def test_kpis_e_grafico_da_gestao(self):
        """FR-072: Docentes é o número de linhas; o gráfico só tem quem tem banca."""
        coordenador = coordenador_de(EC)
        tcc = aluno_com_status(self.turma2, orientador=self.alvo)
        sessao_realizada(tcc, banca_de(self.alvo, self.professor, docente_de(EC)))
        relatorio = self.consulta(coordenador)
        kpis = {kpi.rotulo: kpi.valor for kpi in relatorio.kpis}
        self.assertEqual(kpis["Docentes"], len(relatorio.linhas))
        self.assertEqual(kpis["Orientações"], 1)
        self.assertEqual(kpis["Bancas"], 3)
        self.assertEqual(len(relatorio.grafico.dados), 3)
        self.assertNotIn(coordenador.usu_nome, relatorio.grafico.resumo)

    def test_sem_banca_sem_grafico(self):
        """FR-072: o gráfico não aparece se ninguém tiver banca."""
        coordenador = coordenador_de(EC)
        aluno_com_status(self.turma1, orientador=self.alvo)
        self.assertIsNone(self.consulta(coordenador).grafico)

    def test_tela_com_ajuda_e_definicoes(self):
        """Heurísticas 1 e 10: Mostrando, Como é calculado e title nos cabeçalhos."""
        aluno_com_status(self.turma1, orientador=self.alvo)
        resposta = self.abrir(self.alvo, "?ano_semestre=2026-2")
        self.assertContains(resposta, "Mostrando: 2026/2")
        self.assertContains(resposta, "Como é calculado")
        self.assertContains(resposta, mensagens.COMO_ATIVIDADES[3])
        self.assertContains(resposta, f'title="{mensagens.DEFINICAO_CURSO_LOTACAO}"')

    def test_linha_expansivel_acessivel(self):
        """FR-025: botão real, aberto sem JavaScript."""
        resposta = self.abrir(self.alvo)
        self.assertContains(resposta, 'aria-expanded="true"')
        self.assertContains(resposta, 'aria-controls="linha-sub-1"')
        self.assertContains(resposta, 'id="linha-sub-1"')

    def test_largura_com_ponto(self):
        """R9: o pt-br não troca o ponto das larguras."""
        grafico = graficos.barras([("A", 3), ("B", 1)])
        self.assertEqual(grafico.dados[1]["largura"], "33.33")
        coordenador = coordenador_de(EC)
        tcc = aluno_com_status(self.turma2)
        sessao_realizada(tcc, banca_de(self.alvo, self.professor, docente_de(EC)))
        resposta = self.abrir(coordenador)
        self.assertContains(resposta, "width: 100.00%")


class TesteSemConsultaPorLinha(TesteAtividades):
    """SC-001: o número de consultas não depende do número de docentes. [research R12]"""

    def _consultas(self, usuario):
        filtros = FiltroRelatorioForm(
            QueryDict("curso=todos"), usuario=usuario, registrado=registro.obter(ID)
        )
        self.assertTrue(filtros.is_valid())
        pronto = filtros.filtros()
        with CaptureQueriesContext(connection) as contexto:
            relatorio = services_relatorios.atividades_docente(usuario, pronto)
            relatorio.linhas_prontas()
        return len(contexto)

    def test_com_1_e_com_10_docentes(self):
        """Mesma contagem com mais docentes, alunos e bancas."""
        coordenador = coordenador_de(EC)
        tcc = aluno_com_status(self.turma2, orientador=self.alvo)
        sessao_realizada(tcc, banca_de(self.alvo, self.professor, docente_de(EC)))
        com_poucos = self._consultas(coordenador)
        for _ in range(10):
            orientador = docente_de(EC)
            tcc = aluno_com_status(self.turma2, orientador=orientador)
            vincular_coorientador(tcc, docente_de(EC))
            sessao_realizada(tcc, banca_de(orientador, self.professor, docente_de(EC)))
        self.assertEqual(self._consultas(coordenador), com_poucos)
