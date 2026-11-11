"""US-48: Defesas realizadas no período (cenários 1 a 9) e as decisões C1 a C5 da spec 011.

[US-48][RBN-REL-03.1][RBN-DEF-01.2][RBN-DEF-01.5][RBN-CAD-14.1][FR-010] (tasks T010)
"""

from datetime import date, time
from io import BytesIO

from django.http import QueryDict
from django.urls import reverse
from pypdf import PdfReader

from sigtcc.apps.cadastro.choices import DescricaoTurma, StatusTCC
from sigtcc.apps.cadastro.tests.apoio_contas import (
    coordenador_de,
    docente_de,
    membro,
    secretaria_de,
)
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, SI, criar_turma_de, curso
from sigtcc.apps.defesa.choices import PapelBanca, Parecer, StatusSessao
from sigtcc.apps.defesa.models import Defesas
from sigtcc.apps.defesa.services_defesa import intervalo_do_atalho
from sigtcc.apps.relatorios import registro, services_operacionais
from sigtcc.apps.relatorios.forms import FiltroRelatorioForm
from sigtcc.apps.relatorios.tests.apoio_relatorios import (
    TesteRelatorios,
    aluno_com_status,
    banca_de,
    sessao_realizada,
)

ID = "defesas-realizadas"
COLUNAS = ["Data/Horário", "Aluno", "Orientador", "Banca", "Modalidade do TCC", "Parecer"]


class TesteDefesasRealizadas(TesteRelatorios):
    """Turma de TCC 1 de Engenharia de Computação de 2026/2."""

    def setUp(self):
        super().setUp()
        self.secretaria = secretaria_de(EC)
        self.professor = docente_de(EC)
        self.turma = criar_turma_de(self.professor)
        self.url = reverse("relatorios:relatorio", args=[ID])

    def consulta(self, texto="ano_semestre=2026-2", usuario=None):
        usuario = usuario or self.secretaria
        form = FiltroRelatorioForm(QueryDict(texto), usuario=usuario, registrado=registro.obter(ID))
        self.assertTrue(form.is_valid(), form.errors)
        return services_operacionais.defesas_realizadas(usuario, form.filtros())

    def sessao(self, nome="Aluno", data=None, turma=None, banca=None, parecer=Parecer.APROVADO):
        tcc = aluno_com_status(turma or self.turma, StatusTCC.APROVADO_PARA_TCC_2, nome=nome)
        membros = banca or banca_de(self.professor, docente_de(EC), docente_de(EC))
        sessao = sessao_realizada(tcc, membros, data)
        Defesas.objects.filter(pk=sessao.pk).update(def_parecer=parecer)
        return sessao

    def alunos(self, relatorio):
        return [linha.valores["aluno"] for linha in relatorio.linhas]

    def test_cenario_1_so_realizadas_e_pdf(self):
        """Dado 3 Realizadas e 1 Agendada, quando abre 2026/2 e aciona PDF, então só as 3."""
        for nome in ("Ana", "Bia", "Caio"):
            self.sessao(nome)
        agendada = self.sessao("Davi")
        Defesas.objects.filter(pk=agendada.pk).update(def_status=StatusSessao.AGENDADA)
        self.client.force_login(self.secretaria)
        resposta = self.client.get(self.url + "?ano_semestre=2026-2")
        relatorio = resposta.context["relatorio"]
        self.assertEqual([c.rotulo for c in relatorio.colunas], COLUNAS)
        self.assertEqual(self.alunos(relatorio), ["Ana", "Bia", "Caio"])
        arquivo = self.client.get(
            reverse("relatorios:exportar", args=[ID, "pdf"]) + "?ano_semestre=2026-2"
        )
        self.assertEqual(arquivo["Content-Type"], "application/pdf")
        texto = "\n".join(p.extract_text() for p in PdfReader(BytesIO(arquivo.content)).pages)
        for nome in ("Ana", "Bia", "Caio"):
            self.assertIn(nome, texto)
        self.assertNotIn("Davi", texto)

    def test_cenario_2_periodo_por_datas(self):
        """Considera apenas o intervalo informado."""
        self.sessao("Setembro", data=date(2026, 9, 10))
        self.sessao("Outubro", data=date(2026, 10, 10))
        relatorio = self.consulta("data_inicial=2026-09-01&data_final=2026-09-30")
        self.assertEqual(self.alunos(relatorio), ["Setembro"])

    def test_cenario_3_atalho_este_mes(self):
        """Preenche Data Inicial e Data Final com o primeiro e o último dia do mês."""
        self.client.force_login(self.secretaria)
        resposta = self.client.get(self.url + "?atalho=este_mes")
        inicio, fim = intervalo_do_atalho("este_mes")
        self.assertEqual(resposta.context["form"]["data_inicial"].value(), inicio.isoformat())
        self.assertEqual(resposta.context["form"]["data_final"].value(), fim.isoformat())

    def test_cenario_4_coordenador_com_o_curso_coordenado(self):
        """O filtro Curso aparece preenchido com Sistemas de Informação."""
        self.client.force_login(coordenador_de(SI))
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.context["form"]["curso"].value(), str(curso(SI).pk))

    def test_cenario_5_professor_sem_curso_e_so_as_suas_turmas(self):
        """Só os filtros de período, sem Curso, e só as sessões das turmas dele (C1)."""
        outro = docente_de(EC)
        self.sessao("Meu")
        self.sessao("Alheio", turma=criar_turma_de(outro))
        self.client.force_login(self.professor)
        resposta = self.client.get(self.url)
        self.assertNotIn("curso", resposta.context["form"].fields)
        self.assertIn("atalho", resposta.context["form"].fields)
        self.assertEqual(self.alunos(resposta.context["relatorio"]), ["Meu"])

    def test_cenario_6_login(self):
        """Sem sessão, a tela de login e o retorno ao relatório."""
        self.assertIn(f"next={self.url}", self.client.get(self.url)["Location"])

    def test_cenario_7_datas_invertidas(self):
        """Não atualiza e exibe a mensagem exata."""
        self.client.force_login(self.secretaria)
        resposta = self.client.get(self.url + "?data_inicial=2026-11-30&data_final=2026-11-01")
        self.assertContains(resposta, "A data inicial não pode ser superior à data final")
        self.assertIsNone(resposta.context["relatorio"])

    def test_cenario_8_sem_dados(self):
        """Mensagem exata e botões desabilitados."""
        self.client.force_login(self.secretaria)
        resposta = self.client.get(self.url)
        self.assertContains(resposta, "Nenhum registro encontrado para os filtros selecionados")
        self.assertContains(resposta, "disabled", count=3)

    def test_cenario_9_docente_comum_nao_ve(self):
        """O item não aparece na lista, e o endereço direto é recusado."""
        docente = docente_de(EC)
        self.client.force_login(docente)
        lista = self.client.get(reverse("relatorios:lista")).context["lista"]
        self.assertNotIn(ID, [item.id for item in lista])
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_c2_professor_que_e_coordenador_tem_o_curso(self):
        """Professor da Disciplina e Coordenador: filtro Curso e todas as turmas do curso (C2)."""
        coordenador = coordenador_de(EC)
        criar_turma_de(coordenador)
        self.sessao("De outro professor")
        self.client.force_login(coordenador)
        resposta = self.client.get(self.url)
        self.assertIn("curso", resposta.context["form"].fields)
        self.assertEqual(self.alunos(resposta.context["relatorio"]), ["De outro professor"])

    def test_c3_c4_c5_colunas(self):
        """Orientador = Presidente; Banca com os avaliadores efetivos; Data/Horário formatado."""
        primeiro, segundo, suplente = docente_de(EC), membro(), docente_de(EC)
        segundo.usu_nome = "Externa"
        segundo.save()
        primeiro.usu_nome = "Avaliador Um"
        primeiro.save()
        suplente.usu_nome = "Suplente Acionado"
        suplente.save()
        self.professor.usu_nome = "Orientadora"
        self.professor.save()
        banca = [
            (self.professor, PapelBanca.ORIENTADOR_PRESIDENTE),
            (primeiro, PapelBanca.PRIMEIRO_AVALIADOR),
            (suplente, PapelBanca.SEGUNDO_AVALIADOR, segundo),
            (segundo, PapelBanca.SUPLENTE),
        ]
        sessao = self.sessao("Ana", banca=banca, parecer=Parecer.APROVADO_COM_CORRECOES)
        Defesas.objects.filter(pk=sessao.pk).update(def_h_inicio=time(9, 30))
        valores = self.consulta().linhas[0].valores
        self.assertEqual(valores["data_horario"], "20/11/2026 09:30")
        self.assertEqual(valores["orientador"], "Orientadora")
        self.assertEqual(
            valores["banca"], "Avaliador Um (1º Avaliador); Suplente Acionado (2º Avaliador)"
        )
        self.assertEqual(valores["modalidade"], "Monografia")
        self.assertEqual(valores["parecer"], "Aprovado com Correções")

    def test_curso_e_todos(self):
        """Curso da turma do TCC da sessão; Todos traz os dois cursos."""
        self.sessao("EC")
        self.sessao("SI", turma=criar_turma_de(self.professor, curso_nome=SI))
        self.assertEqual(self.alunos(self.consulta()), ["EC"])
        self.assertEqual(self.alunos(self.consulta("curso=todos")), ["EC", "SI"])

    def test_ordem_por_data_e_hora(self):
        """Ordem por data, hora e aluno (C5)."""
        self.sessao("Depois", data=date(2026, 11, 21))
        self.sessao("Antes", data=date(2026, 11, 19))
        self.assertEqual(self.alunos(self.consulta()), ["Antes", "Depois"])

    def test_tcc_2_tambem_entra(self):
        """Sessões de turmas de TCC 2 também são defesas realizadas."""
        turma2 = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2)
        self.sessao("Final", turma=turma2)
        self.assertEqual(self.alunos(self.consulta()), ["Final"])
