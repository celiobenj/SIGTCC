"""Testes de aceite da US-19: registrar, consultar, editar e comentar atas de orientação (spec
006, User Story 4).

Cenários 1 a 16 da US-19, mais: troca de enc_id por ata de outro TCC (404), atas do TCC 1 no
TCC 2 só para consulta (Q6), ex-orientador sem acesso (Q10), limites (MO-19), data de hoje
aceita, mesma Data do Encontro (D14) e turma arquivada nas rotas do docente.

[US-19][RBN-CAD-11.1][RBN-CAD-11.2][FR-021 a FR-025][Q6][Q10][D14] (tasks T031)
"""

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services_atas
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    GatilhoStatusTCC,
    StatusConta,
    StatusOrientacao,
    StatusTCC,
    StatusTurma,
)
from sigtcc.apps.cadastro.models import (
    ComentariosEncontro,
    EncontroOrientacao,
    HistoricoStatusTCC,
    Orientacoes,
    TCCs,
)
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo
from sigtcc.apps.cadastro.tests.apoio_orientacao import (
    comentar,
    criar_convite,
    registrar_ata,
    vincular_coorientador,
    vincular_orientador,
)
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    SI,
    TesteTurmas,
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)

HOJE = timezone.now().date


def dados(data=None, pauta="Pauta do encontro", metas="Metas acordadas"):
    """Formulário da ata (data no formato do campo date)."""
    data = data or (HOJE() - timedelta(days=1))
    return {"data": data.strftime("%Y-%m-%d"), "pauta": pauta, "metas": metas}


class AtasTestBase(TesteTurmas):
    """Aluno com Orientador e Coorientador, numa turma de TCC 1 de SI."""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=SI)
        self.aluno = matricular_aluno(
            self.turma, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        )
        self.tcc = tcc_de(self.aluno, self.turma)
        self.orientador = criar_docente_ativo()
        self.coorientador = criar_docente_ativo()
        vincular_orientador(self.tcc, self.orientador)
        vincular_coorientador(self.tcc, docente=self.coorientador)

    def url(self, rota, *args):
        return reverse(f"cadastro:{rota}", args=args)

    def como(self, usuario):
        self.client.force_login(usuario)


class AtasTest(AtasTestBase):
    """Cenários 1 a 16. [US-19]"""

    def test_cenario1_aluno_registra(self):
        self.como(self.aluno.alu)
        resposta = self.client.post(
            self.url("registrar_ata_aluno", self.turma.pk), dados(), follow=True
        )
        self.assertContains(resposta, mensagens.ATA_REGISTRADA)
        self.assertEqual(EncontroOrientacao.objects.filter(enc_tcc=self.tcc).count(), 1)
        self.assertEqual(resposta.redirect_chain[-1][0].split("?")[1], "secao=atas")

    def test_cenario2_orientador_registra_pela_linha(self):
        self.como(self.orientador)
        resposta = self.client.post(self.url("registrar_ata_docente", self.tcc.pk), dados())
        self.assertRedirects(resposta, self.url("orientacoes"), fetch_redirect_response=False)
        self.assertEqual(EncontroOrientacao.objects.filter(enc_tcc=self.tcc).count(), 1)

    def test_cenario3_coorientador_registra(self):
        self.como(self.coorientador)
        self.client.post(self.url("registrar_ata_docente", self.tcc.pk), dados())
        self.assertEqual(EncontroOrientacao.objects.filter(enc_tcc=self.tcc).count(), 1)

    def test_cenario4_ordem_da_mais_recente(self):
        for dias in (10, 5, 1):
            registrar_ata(self.tcc, data=HOJE() - timedelta(days=dias), pauta=f"P{dias}")
        self.como(self.aluno.alu)
        resposta = self.client.get(self.url("minhas_atas", self.turma.pk))
        texto = resposta.content.decode()
        self.assertLess(texto.index("P1<"), texto.index("P5<"))
        self.assertLess(texto.index("P5<"), texto.index("P10<"))

    def test_d14_mesma_data_a_ultima_registrada_primeiro(self):
        primeira = registrar_ata(self.tcc, data=HOJE(), pauta="Primeira")
        segunda = registrar_ata(self.tcc, data=HOJE(), pauta="Segunda")
        atas = services_atas.atas_do_tcc(self.tcc)
        self.assertEqual([a.pk for a in atas], [segunda.pk, primeira.pk])

    def test_cenario5_orientador_comenta(self):
        ata = registrar_ata(self.tcc)
        self.como(self.orientador)
        self.client.post(self.url("comentar_ata", self.tcc.pk, ata.pk), {"texto": "Muito bom"})
        comentario = ComentariosEncontro.objects.get(com_enc=ata)
        self.assertEqual(comentario.com_usu_id, self.orientador.pk)
        resposta = self.client.get(self.url("atas_orientando", self.tcc.pk))
        self.assertContains(resposta, "Muito bom")
        self.assertContains(resposta, self.orientador.usu_nome)

    def test_cenario6_aluno_edita_as_metas(self):
        ata = registrar_ata(self.tcc)
        self.como(self.aluno.alu)
        self.client.post(
            self.url("editar_ata_aluno", self.turma.pk, ata.pk), dados(metas="Novas metas")
        )
        ata.refresh_from_db()
        self.assertEqual(ata.enc_metas, "Novas metas")

    def test_cenario7_e_14_professor_so_leitura(self):
        ata = registrar_ata(self.tcc)
        self.como(self.professor)
        resposta = self.client.get(self.url("atas_painel", self.turma.pk, self.aluno.pk))
        self.assertContains(resposta, ata.enc_pauta)
        self.assertNotContains(resposta, "Registrar ata")
        self.assertNotContains(resposta, ">Editar<")
        self.assertNotContains(resposta, ">Comentar<")

    def test_cenario8_aluno_sem_orientador_e_depois_do_aceite(self):
        Orientacoes.objects.filter(ori_tcc=self.tcc).delete()
        ata = registrar_ata(self.tcc)
        novo = criar_docente_ativo()
        self.como(novo)
        self.assertEqual(self.client.get(self.url("atas_orientando", self.tcc.pk)).status_code, 404)
        vincular_orientador(self.tcc, novo)
        self.assertContains(
            self.client.get(self.url("atas_orientando", self.tcc.pk)), ata.enc_pauta
        )

    def test_cenario9_sem_sessao(self):
        resposta = self.client.get(self.url("minhas_atas", self.turma.pk))
        self.assertEqual(resposta.status_code, 302)

    def test_cenario10_data_futura(self):
        self.como(self.aluno.alu)
        resposta = self.client.post(
            self.url("registrar_ata_aluno", self.turma.pk), dados(data=HOJE() + timedelta(days=1))
        )
        self.assertContains(resposta, mensagens.DATA_ENCONTRO_FUTURA)
        self.assertFalse(EncontroOrientacao.objects.exists())

    def test_data_de_hoje_aceita(self):
        self.como(self.aluno.alu)
        self.client.post(self.url("registrar_ata_aluno", self.turma.pk), dados(data=HOJE()))
        self.assertEqual(EncontroOrientacao.objects.count(), 1)

    def test_cenario11_metas_em_branco(self):
        self.como(self.aluno.alu)
        resposta = self.client.post(self.url("registrar_ata_aluno", self.turma.pk), dados(metas=""))
        self.assertContains(resposta, "com-erro")
        self.assertContains(resposta, mensagens.M14_CAMPO_OBRIGATORIO)

    def test_cenario12_comentario_acima_do_limite(self):
        ata = registrar_ata(self.tcc)
        self.como(self.orientador)
        resposta = self.client.post(
            self.url("comentar_ata", self.tcc.pk, ata.pk), {"texto": "x" * 1001}
        )
        self.assertContains(resposta, mensagens.MO19_COMENTARIO)
        self.assertFalse(ComentariosEncontro.objects.exists())

    def test_limites_da_pauta_e_das_metas(self):
        self.como(self.aluno.alu)
        resposta = self.client.post(
            self.url("registrar_ata_aluno", self.turma.pk), dados(pauta="x" * 2001)
        )
        self.assertContains(resposta, mensagens.MO19_PAUTA)
        resposta = self.client.post(
            self.url("registrar_ata_aluno", self.turma.pk), dados(metas="x" * 2001)
        )
        self.assertContains(resposta, mensagens.MO19_METAS)

    def test_cenario13_aluno_ve_editar_mas_nao_comentar(self):
        registrar_ata(self.tcc)
        self.como(self.aluno.alu)
        resposta = self.client.get(self.url("minhas_atas", self.turma.pk))
        self.assertContains(resposta, ">Editar<")
        self.assertNotContains(resposta, ">Comentar<")

    def test_cenario15_turma_arquivada_so_consulta(self):
        ata = registrar_ata(self.tcc)
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save()
        self.como(self.orientador)
        resposta = self.client.get(self.url("atas_orientando", self.tcc.pk))
        self.assertContains(resposta, ata.enc_pauta)
        self.assertNotContains(resposta, ">Editar<")
        self.assertNotContains(resposta, ">Comentar<")
        self.assertNotContains(resposta, "Registrar ata")
        for rota, args in (
            ("registrar_ata_docente", (self.tcc.pk,)),
            ("editar_ata_docente", (self.tcc.pk, ata.pk)),
            ("comentar_ata", (self.tcc.pk, ata.pk)),
        ):
            with self.subTest(rota=rota):
                resposta = self.client.get(self.url(rota, *args), follow=True)
                self.assertContains(resposta, mensagens.MT25_TURMA_ARQUIVADA)
                self.assertEqual(
                    resposta.redirect_chain[-1][0], self.url("atas_orientando", self.tcc.pk)
                )
        self.client.post(self.url("comentar_ata", self.tcc.pk, ata.pk), {"texto": "x"})
        self.assertFalse(ComentariosEncontro.objects.exists())

    def test_cenario16_convite_pendente_nao_ve(self):
        convidado = criar_docente_ativo()
        criar_convite(self.tcc, convidado)
        self.como(convidado)
        self.assertEqual(self.client.get(self.url("atas_orientando", self.tcc.pk)).status_code, 404)


class SegurancaAtasTest(AtasTestBase):
    """Troca de enc_id, ex-orientador e atas do TCC 1 no TCC 2. [research R10][Q6][Q10]"""

    def test_enc_id_de_outro_tcc_404(self):
        outro_aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        alheia = registrar_ata(tcc_de(outro_aluno, self.turma))
        self.como(self.orientador)
        for rota in ("editar_ata_docente", "comentar_ata"):
            with self.subTest(rota=rota):
                self.assertEqual(
                    self.client.get(self.url(rota, self.tcc.pk, alheia.pk)).status_code, 404
                )
        self.como(self.aluno.alu)
        resposta = self.client.get(self.url("editar_ata_aluno", self.turma.pk, alheia.pk))
        self.assertEqual(resposta.status_code, 404)

    def test_ex_orientador_perde_o_acesso(self):
        Orientacoes.objects.filter(ori_tcc=self.tcc).update(
            ori_status=StatusOrientacao.ENCERRADA, ori_data_fim=timezone.now()
        )
        self.como(self.orientador)
        self.assertEqual(self.client.get(self.url("atas_orientando", self.tcc.pk)).status_code, 404)

    def test_atas_do_tcc1_no_tcc2_so_consulta(self):
        self.tcc.tcc_status = StatusTCC.APROVADO_PARA_TCC_2
        self.tcc.save()
        ata1 = registrar_ata(self.tcc, pauta="Ata do TCC 1")
        turma2 = criar_turma_de(criar_docente_ativo(), descricao=DescricaoTurma.TCC_2)
        tcc2 = TCCs.objects.create(
            tcc_alu=self.aluno,
            tcc_tur=turma2,
            tcc_status=StatusTCC.EM_ANDAMENTO,
            tcc_titulo="T",
            tcc_resumo="R",
            tcc_modalidade="Monografia",
        )
        HistoricoStatusTCC.objects.create(
            hst_tcc=tcc2,
            hst_tur=turma2,
            hst_status_anterior=StatusTCC.APROVADO_PARA_TCC_2,
            hst_status_novo=StatusTCC.EM_ANDAMENTO,
            hst_gatilho=GatilhoStatusTCC.TRANSFERENCIA_PARA_TCC_2,
            hst_data_hora=timezone.now(),
            hst_usu=self.professor,
        )
        vincular_orientador(tcc2, self.orientador)
        self.como(self.orientador)
        resposta = self.client.get(self.url("atas_orientando", tcc2.pk))
        self.assertContains(resposta, "Ata do TCC 1")
        self.assertContains(resposta, f"Atas do TCC 1 · {self.turma.tur_identificador}")
        resposta = self.client.get(self.url("editar_ata_docente", tcc2.pk, ata1.pk))
        self.assertEqual(resposta.status_code, 404)

    def test_comentario_existente_aparece_com_autor(self):
        ata = registrar_ata(self.tcc)
        comentar(ata, self.coorientador, "Ver referências")
        self.como(self.aluno.alu)
        resposta = self.client.get(self.url("minhas_atas", self.turma.pk))
        self.assertContains(resposta, "Ver referências")
        self.assertContains(resposta, self.coorientador.usu_nome)
