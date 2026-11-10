"""Visual do protótipo de 17/10 nas listas de Docentes, Secretarias, Membros externos, Orientações
e Aproveitamento: botão flutuante de cadastro (.fab) só para quem cadastra, filtro em .filtros,
linha em destaque do docente acima do limite de orientandos, avatar com cor e chips com a cor do
status. Só aparência: as regras continuam nos testes de cada US.

[US-03][US-05][US-18][US-20][RBN-CAD-08.3][RBN-CAD-11.3][RBN-CAD-12.3]
"""

from django.test import SimpleTestCase
from django.urls import reverse

from sigtcc.apps.cadastro.choices import DescricaoTurma, Homologacao, StatusConta, StatusTCC
from sigtcc.apps.cadastro.templatetags.chips_tags import cor_homologacao, cor_status_tcc
from sigtcc.apps.cadastro.templatetags.turmas_tags import cor_avatar
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo
from sigtcc.apps.cadastro.tests.apoio_contas import (
    SI,
    TesteContas,
    coordenador_de,
    docente_de,
    orientacao_ativa,
    secretaria_de,
    turma_do_docente,
)
from sigtcc.apps.cadastro.tests.apoio_orientacao import criar_pedido, vincular_orientador
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)

FAB = 'class="fab"'


class CorDosChipsTest(SimpleTestCase):
    """Filtros cor_status_tcc (chipSit do protótipo) e cor_homologacao."""

    def test_status_do_tcc(self):
        esperado = {
            StatusTCC.CONCLUIDO: "verde",
            StatusTCC.APROVADO: "verde",
            StatusTCC.APROVADO_PARA_TCC_2: "verde",
            StatusTCC.REPROVADO: "vermelho",
            StatusTCC.DESISTENTE: "vermelho",
            StatusTCC.JUBILADO: "vermelho",
            StatusTCC.APROVADO_COM_CORRECOES: "amarelo",
            StatusTCC.APTO_PARA_DEFESA: "roxo",
            StatusTCC.SEM_PROPOSTA: "",
            StatusTCC.EM_ANDAMENTO: "azul",
        }
        for status, cor in esperado.items():
            with self.subTest(status=status):
                self.assertEqual(cor_status_tcc(status), cor)
        self.assertEqual(len(esperado), len(StatusTCC.choices))

    def test_homologacao(self):
        self.assertEqual(cor_homologacao(Homologacao.HOMOLOGADO), "verde")
        self.assertEqual(cor_homologacao(Homologacao.RECUSADO), "vermelho")
        self.assertEqual(cor_homologacao(Homologacao.EM_ANALISE), "amarelo")
        self.assertEqual(cor_homologacao(None), "")


class ListasDeContasTest(TesteContas):
    """Docentes, Secretarias e Membros externos."""

    def test_docentes_com_fab_e_filtros(self):
        self.client.force_login(secretaria_de(SI))
        resposta = self.client.get(reverse("cadastro:contas_docentes"))
        self.assertContains(resposta, FAB, count=1)
        self.assertContains(resposta, reverse("cadastro:contas_docente_novo"))
        self.assertContains(resposta, 'class="filtros mt16"')

    def test_docente_acima_do_limite_em_destaque(self):
        self.client.force_login(secretaria_de(SI))
        orientador = docente_de(SI, email="o@uea.edu.br")
        professor = docente_de(SI, email="p@uea.edu.br")
        turma = turma_do_docente(professor, descricao=DescricaoTurma.TCC_1)
        for _ in range(6):
            aluno = matricular_aluno(turma, status_tcc=StatusTCC.EM_ANDAMENTO)
            orientacao_ativa(orientador, tcc_de(aluno, turma))
        resposta = self.client.get(reverse("cadastro:contas_docentes"))
        self.assertContains(resposta, 'class="alerta-amarelo"', count=1)

    def test_secretarias_fab_so_para_quem_cadastra(self):
        self.client.force_login(coordenador_de(SI))
        self.assertContains(self.client.get(reverse("cadastro:contas_secretarias")), FAB, count=1)
        self.client.force_login(secretaria_de(SI))
        resposta = self.client.get(reverse("cadastro:contas_secretarias"))
        self.assertNotContains(resposta, FAB)
        self.assertNotContains(resposta, reverse("cadastro:contas_secretaria_nova"))

    def test_membros_externos_com_fab(self):
        self.client.force_login(secretaria_de(SI))
        resposta = self.client.get(reverse("cadastro:contas_membros"))
        self.assertContains(resposta, FAB, count=1)
        self.assertContains(resposta, reverse("cadastro:contas_membro_novo"))


class OrientacoesTest(TesteContas):
    """Avatar com cor e chip do Status do TCC na tela Orientações."""

    def test_avatar_e_chip_com_cor(self):
        professor = criar_docente_ativo()
        turma = criar_turma_de(professor, curso_nome=SI)
        docente = criar_docente_ativo()
        orientando = matricular_aluno(
            turma, status_tcc=StatusTCC.APTO_PARA_DEFESA, status_conta=StatusConta.ATIVA
        )
        vincular_orientador(tcc_de(orientando, turma), docente)
        pedinte = matricular_aluno(turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        criar_pedido(tcc_de(pedinte, turma), docente)
        self.client.force_login(docente)
        resposta = self.client.get(reverse("cadastro:orientacoes"))
        nome = pedinte.alu.usu_nome
        self.assertContains(resposta, f'style="background:{cor_avatar(nome)}"')
        self.assertContains(resposta, '<span class="chip roxo">Apto para Defesa</span>', html=True)
