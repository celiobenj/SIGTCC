"""Vínculo, papéis e permissões da feature 006 (SC-006; research R10).

Seção "vínculo" (T007): papéis por vínculo ativo, orientador automático com dois papéis,
ex-orientador e convite pendente sem papel (Q10; US-19 #16), TCC copiado para o TCC 2 (Q6) e
link único da solicitação. As seções de rotas e de concorrência vêm em T056 e T057.

[US-17][US-18][US-19][US-36][RBN-CAD-10.4][RBN-CAD-11.2][FR-007][FR-023][FR-046][Q6][Q10]
"""

from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import services_orientacao as so
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    GatilhoStatusTCC,
    OrigemOrientacao,
    StatusOrientacao,
    StatusTCC,
    StatusTurma,
    TipoSolicitacao,
)
from sigtcc.apps.cadastro.models import HistoricoStatusTCC, TCCs
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo
from sigtcc.apps.cadastro.tests.apoio_orientacao import (
    criar_convite,
    criar_externo,
    criar_pedido,
    vincular_coorientador,
    vincular_orientador,
)
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    TesteTurmas,
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)


class VinculoTest(TesteTurmas):
    """Papéis por vínculo ativo e regras de alteração no TCC. [FR-007][FR-046][Q10]"""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.orientador = criar_docente_ativo()
        self.coorientador = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor)
        self.aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        self.tcc = tcc_de(self.aluno, self.turma)

    def test_cada_papel_por_vinculo_ativo(self):
        vincular_orientador(self.tcc, self.orientador)
        vincular_coorientador(self.tcc, docente=self.coorientador)
        self.assertEqual(so.papeis_no_tcc(self.aluno.alu, self.tcc), {"aluno"})
        self.assertEqual(so.papeis_no_tcc(self.orientador, self.tcc), {"orientador"})
        self.assertEqual(so.papeis_no_tcc(self.coorientador, self.tcc), {"coorientador"})
        self.assertEqual(so.papeis_no_tcc(self.professor, self.tcc), {"professor"})
        self.assertTrue(so.e_orientador_atual(self.orientador, self.tcc))
        self.assertTrue(so.e_coorientador_ativo(self.coorientador, self.tcc))
        self.assertEqual(so.orientador_atual(self.tcc).pk, self.orientador.pk)
        self.assertEqual(len(so.coorientadores_ativos(self.tcc)), 1)

    def test_sem_vinculo_conjunto_vazio(self):
        outro = criar_docente_ativo()
        self.assertEqual(so.papeis_no_tcc(outro, self.tcc), set())
        self.assertFalse(so.e_orientador_atual(outro, self.tcc))
        self.assertIsNone(so.orientador_atual(self.tcc))

    def test_orientador_automatico_tem_dois_papeis(self):
        """TCC 2 de EC: o Professor da Disciplina é também o Orientador (R10; US-18 G)."""
        turma2 = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        aluno2 = matricular_aluno(turma2, status_tcc=StatusTCC.EM_ANDAMENTO)
        tcc2 = tcc_de(aluno2, turma2)
        vincular_orientador(tcc2, self.professor, origem=OrigemOrientacao.AUTOMATICO)
        self.assertEqual(so.papeis_no_tcc(self.professor, tcc2), {"professor", "orientador"})
        self.assertTrue(so.e_orientador_atual(self.professor, tcc2))

    def test_ex_orientador_sem_papel(self):
        """Q10: depois da troca, o ex-orientador perde o vínculo e o acesso."""
        orientacao = vincular_orientador(self.tcc, self.orientador)
        orientacao.ori_status = StatusOrientacao.ENCERRADA
        orientacao.ori_data_fim = timezone.now()
        orientacao.save()
        self.assertEqual(so.papeis_no_tcc(self.orientador, self.tcc), set())

    def test_convite_pendente_nao_da_papel(self):
        """US-19 #16: o convite 'Aguardando Aceite' não conta como coorientação."""
        criar_convite(self.tcc, self.coorientador)
        self.assertEqual(so.papeis_no_tcc(self.coorientador, self.tcc), set())

    def test_coorientador_externo_nao_e_usuario(self):
        vincular_coorientador(self.tcc, externo=criar_externo())
        self.assertEqual(len(so.coorientadores_ativos(self.tcc)), 1)

    def test_pode_alterar_no_tcc(self):
        self.assertTrue(so.pode_alterar_no_tcc(self.tcc))
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save()
        self.tcc.refresh_from_db()
        self.assertFalse(so.pode_alterar_no_tcc(self.tcc))

    def test_participacao_encerrada_nao_altera(self):
        self.tcc.tcc_status = StatusTCC.DESISTENTE
        self.tcc.save()
        self.assertFalse(so.pode_alterar_no_tcc(self.tcc))

    def test_link_da_solicitacao(self):
        pedido = criar_pedido(self.tcc, self.orientador)
        troca = criar_pedido(
            criar_tcc_extra(self), self.orientador, TipoSolicitacao.TROCA_DE_ORIENTACAO
        )
        convite = criar_convite(self.tcc, self.coorientador)
        self.assertEqual(
            so.link_da_solicitacao(pedido), reverse("cadastro:pedido_orientacao", args=[pedido.pk])
        )
        self.assertEqual(
            so.link_da_solicitacao(troca), reverse("cadastro:pedido_orientacao", args=[troca.pk])
        )
        self.assertEqual(
            so.link_da_solicitacao(convite),
            reverse("cadastro:convite_coorientacao", args=[convite.pk]),
        )


def criar_tcc_extra(teste):
    """Outro aluno e TCC na mesma turma (um pedido pendente por TCC)."""
    aluno = matricular_aluno(teste.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
    return tcc_de(aluno, teste.turma)


class TccCopiadoTest(TesteTurmas):
    """Q6: TCC 1 aprovado e copiado para o TCC 2 fica só para consulta. [FR-007][FR-051]"""

    def setUp(self):
        super().setUp()
        professor = criar_docente_ativo()
        self.turma1 = criar_turma_de(professor)
        self.aluno = matricular_aluno(self.turma1, status_tcc=StatusTCC.APROVADO_PARA_TCC_2)
        self.tcc1 = tcc_de(self.aluno, self.turma1)
        self.turma2 = criar_turma_de(criar_docente_ativo(), descricao=DescricaoTurma.TCC_2)
        self.tcc2 = TCCs.objects.create(
            tcc_alu=self.aluno,
            tcc_tur=self.turma2,
            tcc_status=StatusTCC.EM_ANDAMENTO,
            tcc_titulo="Título",
            tcc_resumo="Resumo",
            tcc_modalidade="Monografia",
        )
        HistoricoStatusTCC.objects.create(
            hst_tcc=self.tcc2,
            hst_tur=self.turma2,
            hst_status_anterior=StatusTCC.APROVADO_PARA_TCC_2,
            hst_status_novo=StatusTCC.EM_ANDAMENTO,
            hst_gatilho=GatilhoStatusTCC.TRANSFERENCIA_PARA_TCC_2,
            hst_data_hora=timezone.now(),
            hst_usu=professor,
        )

    def test_tcc1_copiado_e_tcc2_nao(self):
        self.assertTrue(so.tcc_copiado(self.tcc1))
        self.assertFalse(so.tcc_copiado(self.tcc2))
        self.assertFalse(so.pode_alterar_no_tcc(self.tcc1))
        self.assertTrue(so.pode_alterar_no_tcc(self.tcc2))

    def test_tcc_de_origem(self):
        self.assertEqual(so.tcc_de_origem(self.tcc2), self.tcc1)
        self.assertIsNone(so.tcc_de_origem(self.tcc1))

    def test_aprovado_sem_copia_nao_esta_copiado(self):
        HistoricoStatusTCC.objects.filter(hst_tcc=self.tcc2).delete()
        self.tcc2.delete()
        self.assertFalse(so.tcc_copiado(self.tcc1))


class PermissoesRotasTest(TesteTurmas):
    """T056: as 29 rotas novas (contracts/rotas.md) — sem sessão vai ao login; perfil errado
    recebe 403; sem vínculo, 404 (o painel, 403, FR-020; os links 12 e 13 mostram o aviso
    "não disponível"); POST sem CSRF é recusado. [FR-046][SC-006][contracts/rotas.md]
    """

    def setUp(self):
        super().setUp()
        from sigtcc.apps.cadastro.choices import ModalidadeTCC, StatusConta
        from sigtcc.apps.cadastro.tests.apoio_acesso import criar_coordenador
        from sigtcc.apps.cadastro.tests.apoio_orientacao import registrar_ata, salvar_artigo
        from sigtcc.apps.cadastro.tests.apoio_tcc import salvar_proposta

        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor)
        self.aluno = matricular_aluno(
            self.turma, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        )
        self.tcc = tcc_de(self.aluno, self.turma)
        salvar_proposta(self.tcc, modalidade=ModalidadeTCC.ARTIGO_CIENTIFICO)
        self.orientador = criar_docente_ativo()
        vincular_orientador(self.tcc, self.orientador)
        self.coo = vincular_coorientador(self.tcc, externo=criar_externo())
        self.convite = criar_convite(self.tcc, criar_docente_ativo())
        self.pedido = criar_pedido(
            self.tcc, criar_docente_ativo(), TipoSolicitacao.TROCA_DE_ORIENTACAO
        )
        self.ata = registrar_ata(self.tcc)
        salvar_artigo(self.tcc, status="Aceito")
        self.coordenador = criar_coordenador()
        outra = criar_turma_de(criar_docente_ativo())
        self.estranho_aluno = matricular_aluno(
            outra, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        ).alu
        self.estranho_docente = criar_docente_ativo()

    def rotas(self):
        """(nome, args, métodos, perfil dono)."""
        t, a, c = self.turma.pk, self.aluno.pk, self.tcc.pk
        return [
            ("enviar_pedido_orientacao", [t], "P", "aluno"),
            ("cancelar_pedido_orientacao", [t], "P", "aluno"),
            ("registrar_coorientador", [t], "G", "aluno"),
            ("substituir_coorientador", [t, self.coo.pk], "G", "aluno"),
            ("remover_coorientador", [t, self.coo.pk], "G", "aluno"),
            ("remover_convite_coorientacao", [t, self.convite.pk], "G", "aluno"),
            ("minhas_atas", [t], "G", "aluno"),
            ("registrar_ata_aluno", [t], "G", "aluno"),
            ("editar_ata_aluno", [t, self.ata.pk], "G", "aluno"),
            ("salvar_publicacao_aluno", [t], "P", "aluno"),
            ("orientacoes", [], "G", "docente"),
            ("pedido_orientacao", [self.pedido.pk], "G", "link"),
            ("convite_coorientacao", [self.convite.pk], "G", "link"),
            ("aceitar_solicitacao", [self.pedido.pk], "P", "docente"),
            ("recusar_solicitacao", [self.pedido.pk], "P", "docente"),
            ("ver_proposta", [self.pedido.pk], "G", "docente"),
            ("atas_orientando", [c], "G", "docente"),
            ("registrar_ata_docente", [c], "G", "docente"),
            ("editar_ata_docente", [c, self.ata.pk], "G", "docente"),
            ("comentar_ata", [c, self.ata.pk], "G", "docente"),
            ("historico_orientando", [c], "G", "docente"),
            ("publicacao_orientando", [c], "G", "docente"),
            ("indicar_apto", [c], "G", "docente"),
            ("correcoes_conferidas", [c], "G", "docente"),
            ("painel_aluno", [t, a], "G", "painel"),
            ("atas_painel", [t, a], "G", "painel"),
            ("aproveitamento_artigos", [], "G", "coordenador"),
            ("homologar_artigo", [c], "P", "coordenador"),
            ("recusar_artigo", [c], "P", "coordenador"),
        ]

    def pedir(self, cliente, nome, args, metodo):
        url = reverse(f"cadastro:{nome}", args=args)
        return cliente.post(url) if metodo == "P" else cliente.get(url)

    def test_29_rotas(self):
        self.assertEqual(len(self.rotas()), 29)

    def test_sem_sessao_vai_ao_login(self):
        for nome, args, metodo, _ in self.rotas():
            with self.subTest(rota=nome):
                resposta = self.pedir(self.client, nome, args, metodo)
                self.assertEqual(resposta.status_code, 302)
                self.assertIn(reverse("cadastro:entrar"), resposta.url)

    def test_perfil_errado_403(self):
        errado = {
            "aluno": self.orientador,
            "docente": self.aluno.alu,
            "link": self.aluno.alu,
            "painel": self.aluno.alu,
            "coordenador": self.orientador,
        }
        for nome, args, metodo, dono in self.rotas():
            with self.subTest(rota=nome):
                self.client.force_login(errado[dono])
                self.assertEqual(self.pedir(self.client, nome, args, metodo).status_code, 403)

    def test_sem_vinculo(self):
        esperado = {"aluno": 404, "docente": 404, "link": 200, "painel": 403}
        for nome, args, metodo, dono in self.rotas():
            if dono in ("coordenador",) or nome == "orientacoes":
                continue
            with self.subTest(rota=nome):
                usuario = self.estranho_aluno if dono == "aluno" else self.estranho_docente
                self.client.force_login(usuario)
                resposta = self.pedir(self.client, nome, args, metodo)
                self.assertEqual(resposta.status_code, esperado[dono])

    def test_coordenador_de_outro_curso_404(self):
        self.client.force_login(self.coordenador)
        for nome in ("homologar_artigo", "recusar_artigo"):
            with self.subTest(rota=nome):
                resposta = self.pedir(self.client, nome, [self.tcc.pk], "P")
                self.assertEqual(resposta.status_code, 404)

    def test_post_sem_csrf_recusado(self):
        from django.test import Client

        dono = {"aluno": self.aluno.alu, "docente": self.estranho_docente}
        cliente = Client(enforce_csrf_checks=True)
        for nome, args, metodo, perfil in self.rotas():
            if metodo != "P" or perfil not in dono:
                continue
            with self.subTest(rota=nome):
                cliente.force_login(dono[perfil])
                self.assertEqual(self.pedir(cliente, nome, args, "P").status_code, 403)
