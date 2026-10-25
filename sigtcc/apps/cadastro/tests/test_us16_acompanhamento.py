"""Testes da US-16 (Professor acompanha as entregas dos alunos da turma) — spec 005, Phase 7, T024.

Os 8 cenários da US-16 (acompanhamento; aluno sem envio após o prazo; envio com atraso; entrega
do tipo Proposta com "Ver Proposta"; turma arquivada; acesso sem login; acesso restrito; turma
sem entregas), mais Secretaria do curso sem acesso, aluno com participação encerrada fora da
lista e o link mais recente (`link_mais_recente`, contrato §3). Escritos antes de
`services_entregas.acompanhamento_entrega` e `views_entregas.entrega_acompanhar`: devem falhar
até a implementação (T025).

[US-16][RBN-CAD-09.4][FR-026][FR-027]
"""

from datetime import timedelta
from urllib.parse import parse_qs, urlparse

from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services_entregas
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    StatusConta,
    StatusEntrega,
    StatusTCC,
    StatusTurma,
    TipoEntrega,
)
from sigtcc.apps.cadastro.models import EntregasMarcos
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo, criar_secretaria
from sigtcc.apps.cadastro.tests.apoio_tcc import cadastrar_entrega, enviar_link
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    TesteTurmas,
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)

LINK_1 = "https://drive.google.com/aluno-1"
LINK_2 = "https://drive.google.com/aluno-2"
LINK_NOVO = "https://drive.google.com/aluno-1-substituido"


class AcompanhamentoTestBase(TesteTurmas):
    """Turma de TCC 1 com 3 alunos "Em Andamento" e a entrega Documento para Defesa."""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        self.alunos = [
            matricular_aluno(
                self.turma, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
            )
            for _ in range(3)
        ]
        self.entrega = self.nova_entrega(TipoEntrega.DOCUMENTO_PARA_DEFESA, "Entrega do Documento")

    def nova_entrega(self, tipo, titulo, data_limite=None):
        """Entrega com o registro "Aguardando Envio" de cada aluno (como o cadastro, US-43)."""
        entrega = cadastrar_entrega(
            self.turma,
            tipo=tipo,
            titulo=titulo,
            data_limite=data_limite or timezone.now() + timedelta(days=5),
        )
        for aluno in self.alunos:
            EntregasMarcos.objects.create(
                ent_tma=entrega, ent_alu=aluno, ent_status=StatusEntrega.AGUARDANDO_ENVIO
            )
        return entrega

    def enviar(self, aluno, link, status, quando=None, entrega=None):
        """Envio registrado com o status já calculado (o cálculo é testado na US-15)."""
        entrega = entrega or self.entrega
        enviar_link(entrega, aluno, link, quando=quando)
        EntregasMarcos.objects.filter(ent_tma=entrega, ent_alu=aluno).update(ent_status=status)

    def url(self, entrega=None, turma=None):
        return reverse(
            "cadastro:entrega_acompanhar",
            args=[(turma or self.turma).pk, (entrega or self.entrega).pk],
        )

    def linhas(self, entrega=None):
        return services_entregas.acompanhamento_entrega((entrega or self.entrega).pk)

    def linha_de(self, aluno, entrega=None):
        return next(linha for linha in self.linhas(entrega) if linha["aluno"] == aluno)


class AcompanhamentoServiceTest(AcompanhamentoTestBase):
    """`services_entregas.acompanhamento_entrega`: uma linha por aluno, com status e link.

    [US-16][RBN-CAD-09.4][FR-026]
    """

    def test_cenario1_tres_linhas_duas_entregues_com_link_e_uma_aguardando(self):
        """Cenário 1: 3 alunos, 2 enviaram -> 2 "Entregue" com o link e 1 "Aguardando Envio"."""
        self.enviar(self.alunos[0], LINK_1, StatusEntrega.ENTREGUE)
        self.enviar(self.alunos[1], LINK_2, StatusEntrega.ENTREGUE)
        linhas = self.linhas()
        self.assertEqual(len(linhas), 3)
        self.assertEqual(
            sorted(linha["status"] for linha in linhas),
            [StatusEntrega.AGUARDANDO_ENVIO, StatusEntrega.ENTREGUE, StatusEntrega.ENTREGUE],
        )
        self.assertEqual(self.linha_de(self.alunos[0])["envio"].hen_link, LINK_1)
        self.assertIsNone(self.linha_de(self.alunos[2])["envio"])

    def test_cenario2_sem_envio_apos_o_prazo_nao_entregue_sem_mudar_o_status_do_tcc(self):
        """Cenário 2 (fluxo alternativo A): Data Limite vencida sem envio -> "Não Entregue",
        sem link e sem mudança no Status do TCC. [FR-020][FR-026]
        """
        self.entrega.tma_data_limite = timezone.now() - timedelta(days=1)
        self.entrega.save(update_fields=["tma_data_limite"])
        linha = self.linha_de(self.alunos[2])
        self.assertEqual(linha["status"], StatusEntrega.NAO_ENTREGUE)
        self.assertIsNone(linha["envio"])
        self.assertEqual(tcc_de(self.alunos[2], self.turma).tcc_status, StatusTCC.EM_ANDAMENTO)

    def test_cenario3_envio_com_atraso_mostra_o_status_e_o_link(self):
        """Cenário 3 (fluxo alternativo B): "Entregue com Atraso" e o link."""
        self.enviar(self.alunos[0], LINK_1, StatusEntrega.ENTREGUE_COM_ATRASO)
        linha = self.linha_de(self.alunos[0])
        self.assertEqual(linha["status"], StatusEntrega.ENTREGUE_COM_ATRASO)
        self.assertEqual(linha["envio"].hen_link, LINK_1)

    def test_link_exibido_e_o_mais_recente(self):
        """FR-026: com substituição, a linha mostra o link mais recente (com data e hora)."""
        self.enviar(
            self.alunos[0], LINK_1, StatusEntrega.ENTREGUE, quando=timezone.now() - timedelta(1)
        )
        enviar_link(self.entrega, self.alunos[0], LINK_NOVO)
        self.assertEqual(self.linha_de(self.alunos[0])["envio"].hen_link, LINK_NOVO)
        registro = EntregasMarcos.objects.get(ent_tma=self.entrega, ent_alu=self.alunos[0])
        self.assertEqual(services_entregas.link_mais_recente(registro).hen_link, LINK_NOVO)

    def test_aluno_com_participacao_encerrada_fica_fora_da_lista(self):
        """Contrato §3 (regra das entregas): só alunos com participação não encerrada."""
        tcc = tcc_de(self.alunos[2], self.turma)
        tcc.tcc_status = StatusTCC.DESISTENTE
        tcc.save(update_fields=["tcc_status"])
        alunos = [linha["aluno"] for linha in self.linhas()]
        self.assertEqual(len(alunos), 2)
        self.assertNotIn(self.alunos[2], alunos)


class AcompanhamentoViewTest(AcompanhamentoTestBase):
    """View `entrega_acompanhar` e aba Entregas do Professor. [US-16][FR-026][FR-027]"""

    def test_cenario1_tabela_com_as_tres_linhas(self):
        self.enviar(self.alunos[0], LINK_1, StatusEntrega.ENTREGUE)
        self.enviar(self.alunos[1], LINK_2, StatusEntrega.ENTREGUE)
        self.client.force_login(self.professor)
        resposta = self.client.get(self.url())
        self.assertEqual(resposta.status_code, 200)
        for aluno in self.alunos:
            self.assertContains(resposta, aluno.alu_matricula)
            self.assertContains(resposta, aluno.alu.usu_nome)
        self.assertContains(resposta, LINK_1)
        self.assertContains(resposta, LINK_2)
        self.assertContains(resposta, StatusEntrega.AGUARDANDO_ENVIO.label)
        self.assertContains(resposta, "Fechar")

    def test_aba_atividades_leva_ao_acompanhamento(self):
        """Passo 4: o Professor seleciona a entrega na aba Entregas."""
        self.client.force_login(self.professor)
        resposta = self.client.get(reverse("cadastro:entregas", args=[self.turma.pk]))
        self.assertContains(resposta, f'href="{self.url()}"')

    def test_cenario4_entrega_tipo_proposta_mostra_ver_proposta_somente_leitura(self):
        """Cenário 4 (fluxo alternativo C): no lugar do link, "Ver Proposta" com a Proposta do
        aluno, somente leitura (o Professor da turma pode ver o Resumo, FR-007a).
        [US-16][US-13][FR-007a][FR-026]
        """
        proposta = self.nova_entrega(TipoEntrega.PROPOSTA, "Proposta do TCC")
        tcc = tcc_de(self.alunos[0], self.turma)
        tcc.tcc_titulo = "Detecção de intrusão com IoT"
        tcc.tcc_resumo = "Resumo confidencial do trabalho"
        tcc.save(update_fields=["tcc_titulo", "tcc_resumo"])
        EntregasMarcos.objects.filter(ent_tma=proposta, ent_alu=self.alunos[0]).update(
            ent_status=StatusEntrega.ENTREGUE
        )
        self.client.force_login(self.professor)
        resposta = self.client.get(self.url(proposta))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Ver Proposta")
        self.assertContains(resposta, "Detecção de intrusão com IoT")
        self.assertContains(resposta, "Resumo confidencial do trabalho")
        # Somente leitura: nenhum botão de salvar da Proposta (US-13) nesta tela.
        self.assertNotContains(resposta, "Salvar Proposta")
        self.assertNotContains(resposta, "Salvar alterações")

    def test_cenario5_turma_arquivada_so_consulta(self):
        """Cenário 5 (fluxo alternativo D): turma arquivada — a lista aparece para consulta."""
        self.enviar(self.alunos[0], LINK_1, StatusEntrega.ENTREGUE)
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save(update_fields=["tur_status"])
        self.client.force_login(self.professor)
        resposta = self.client.get(self.url())
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, LINK_1)

    def test_cenario6_sem_login_vai_para_o_login_com_next(self):
        """Cenário 6 (E1): sem sessão, a tela de login, com retorno à mesma tela."""
        resposta = self.client.get(self.url())
        self.assertEqual(resposta.status_code, 302)
        destino = urlparse(resposta["Location"])
        self.assertEqual(destino.path, reverse("cadastro:entrar"))
        self.assertEqual(parse_qs(destino.query)["next"], [self.url()])

    def test_cenario7_docente_que_nao_e_o_professor_da_turma_nao_ve_a_lista(self):
        """Cenário 7 (E2): outro Docente não vê a lista (403, M-02)."""
        self.enviar(self.alunos[0], LINK_1, StatusEntrega.ENTREGUE)
        self.client.force_login(criar_docente_ativo())
        resposta = self.client.get(self.url())
        self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)
        self.assertNotContains(resposta, LINK_1, status_code=403)

    def test_secretaria_do_curso_nao_ve_a_lista(self):
        """FR-027: restrita ao Professor da Disciplina da turma (a Secretaria também não vê)."""
        self.client.force_login(criar_secretaria(curso=self.turma.tur_cur))
        self.assertEqual(self.client.get(self.url()).status_code, 403)

    def test_aluno_nao_abre_o_acompanhamento(self):
        self.client.force_login(self.alunos[0].alu)
        self.assertEqual(self.client.get(self.url()).status_code, 403)

    def test_entrega_de_outra_turma_recebe_404(self):
        outra_turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        self.client.force_login(self.professor)
        self.assertEqual(self.client.get(self.url(turma=outra_turma)).status_code, 404)

    def test_cenario8_turma_sem_entregas(self):
        """Cenário 8 (E3): "Nenhuma entrega cadastrada" e o botão "Cadastrar atividade"."""
        turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        self.client.force_login(self.professor)
        resposta = self.client.get(reverse("cadastro:entregas", args=[turma.pk]))
        self.assertContains(resposta, mensagens.NENHUMA_ENTREGA_CADASTRADA)
        self.assertNotContains(resposta, mensagens.NENHUMA_ENTREGA_CADASTRADA + ".")
        self.assertContains(resposta, "Cadastrar atividade")
