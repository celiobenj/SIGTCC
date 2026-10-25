"""Concorrência da feature 006 (T057; research R2, N1): duas operações quase simultâneas em
threads com conexões próprias — nenhum deadlock, nenhum erro 500 e um resultado só.

Casos: dois aceites do mesmo pedido; aceite × cancelamento pelo aluno; dois convites ao mesmo
docente; dois externos com o mesmo e-mail; Correções Conferidas × reenvio da Versão Final
(IC-14); arquivamento × aceite.

Usa `TransactionTestCase` com `serialized_rollback=True`, como test_us15_envio_entrega.py: as
threads precisam enxergar os dados confirmados, e o flush restaura as cargas das migrações.

[US-17][US-18][US-36][US-45][US-07][US-29][FR-047][FR-053][research R2][N1] (tasks T057)
"""

import threading
from datetime import timedelta

from django.db import close_old_connections
from django.http import Http404
from django.test import TransactionTestCase
from django.utils import timezone

from sigtcc.apps.cadastro import services_entregas, services_orientacao, services_turmas
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    StatusConta,
    StatusEntrega,
    StatusOrientacao,
    StatusSolicitacao,
    StatusTCC,
    TipoEntrega,
    TipoSolicitacao,
)
from sigtcc.apps.cadastro.models import (
    Coorientacoes,
    CoorientadoresExternos,
    EntregasMarcos,
    Orientacoes,
    SolicitacoesOrientacao,
)
from sigtcc.apps.cadastro.services_turmas import ErroTurma, TurmaArquivada
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo
from sigtcc.apps.cadastro.tests.apoio_orientacao import criar_pedido, vincular_orientador
from sigtcc.apps.cadastro.tests.apoio_tcc import cadastrar_entrega, enviar_link
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    SI,
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)

ESPERADOS = (
    Http404,
    TurmaArquivada,
    ErroTurma,
    services_orientacao.SolicitacaoRespondida,
    services_orientacao.ErroOrientacao,
)


def em_paralelo(*funcoes):
    """Roda as funções em threads ao mesmo tempo; devolve as exceções inesperadas."""
    barreira = threading.Barrier(len(funcoes))
    inesperadas = []

    def rodar(funcao):
        try:
            barreira.wait(timeout=5)
            funcao()
        except ESPERADOS:
            pass
        except Exception as exc:  # pragma: no cover - diagnóstico de falha do teste
            inesperadas.append(exc)
        finally:
            close_old_connections()

    threads = [threading.Thread(target=rodar, args=(f,)) for f in funcoes]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
    return inesperadas


class ConcorrenciaOrientacaoTest(TransactionTestCase):
    """Corridas da orientação, dos convites e dos externos. [FR-047][research R2]"""

    serialized_rollback = True

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=SI)
        self.aluno = matricular_aluno(
            self.turma, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        )
        self.tcc = tcc_de(self.aluno, self.turma)
        self.docente = criar_docente_ativo()

    def test_dois_aceites_do_mesmo_pedido(self):
        pedido = criar_pedido(self.tcc, self.docente)
        erros = em_paralelo(
            lambda: services_orientacao.aceitar_solicitacao(self.docente, pedido.pk),
            lambda: services_orientacao.aceitar_solicitacao(self.docente, pedido.pk),
        )
        self.assertEqual(erros, [])
        self.assertEqual(
            Orientacoes.objects.filter(ori_tcc=self.tcc, ori_status=StatusOrientacao.ATIVA).count(),
            1,
        )

    def test_aceite_e_cancelamento_pelo_aluno(self):
        pedido = criar_pedido(self.tcc, self.docente)
        erros = em_paralelo(
            lambda: services_orientacao.aceitar_solicitacao(self.docente, pedido.pk),
            lambda: services_orientacao.cancelar_pedido(self.aluno.alu, self.turma.pk),
        )
        self.assertEqual(erros, [])
        pedido.refresh_from_db()
        ativa = Orientacoes.objects.filter(ori_tcc=self.tcc, ori_status="Ativa").exists()
        self.assertEqual(ativa, pedido.sol_status == StatusSolicitacao.ACEITO)
        self.assertIn(pedido.sol_status, (StatusSolicitacao.ACEITO, StatusSolicitacao.CANCELADO))

    def test_dois_convites_ao_mesmo_docente(self):
        vincular_orientador(self.tcc, criar_docente_ativo())
        dados = {"tipo": "docente", "docente": self.docente.pk}
        erros = em_paralelo(
            lambda: services_orientacao.registrar_coorientador(
                self.aluno.alu, self.turma.pk, dados
            ),
            lambda: services_orientacao.registrar_coorientador(
                self.aluno.alu, self.turma.pk, dados
            ),
        )
        self.assertEqual(erros, [])
        self.assertEqual(
            SolicitacoesOrientacao.objects.filter(
                sol_tcc=self.tcc, sol_tipo=TipoSolicitacao.COORIENTACAO
            ).count(),
            1,
        )

    def test_dois_externos_com_o_mesmo_email(self):
        outro = matricular_aluno(
            self.turma, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        )
        for tcc in (self.tcc, tcc_de(outro, self.turma)):
            vincular_orientador(tcc, criar_docente_ativo())
        dados = {"tipo": "externo", "nome": "Ana Externa", "email": "ana@ufam.edu.br"}
        erros = em_paralelo(
            lambda: services_orientacao.registrar_coorientador(
                self.aluno.alu, self.turma.pk, dict(dados)
            ),
            lambda: services_orientacao.registrar_coorientador(
                outro.alu, self.turma.pk, dict(dados)
            ),
        )
        self.assertEqual(erros, [])
        self.assertEqual(CoorientadoresExternos.objects.count(), 1)
        self.assertEqual(Coorientacoes.objects.count(), 2)

    def test_arquivamento_e_aceite(self):
        self.tcc.tcc_status = StatusTCC.SEM_PROPOSTA
        self.tcc.save()
        pedido = criar_pedido(self.tcc, self.docente)
        erros = em_paralelo(
            lambda: services_turmas.arquivar_turma(self.professor, self.turma.pk),
            lambda: services_orientacao.aceitar_solicitacao(self.docente, pedido.pk),
        )
        self.assertEqual(erros, [])
        pedido.refresh_from_db()
        self.assertIn(pedido.sol_status, (StatusSolicitacao.ACEITO, StatusSolicitacao.CANCELADO))


class ConcorrenciaVersaoFinalTest(TransactionTestCase):
    """Correções Conferidas × reenvio da Versão Final (IC-14; N1): sem deadlock. [FR-016]"""

    serialized_rollback = True

    def test_correcoes_e_reenvio(self):
        turma = criar_turma_de(criar_docente_ativo(), descricao=DescricaoTurma.TCC_2, curso_nome=SI)
        aluno = matricular_aluno(
            turma, status_tcc=StatusTCC.APROVADO_COM_CORRECOES, status_conta=StatusConta.ATIVA
        )
        tcc = tcc_de(aluno, turma)
        orientador = criar_docente_ativo()
        vincular_orientador(tcc, orientador)
        entrega = cadastrar_entrega(
            turma, tipo=TipoEntrega.VERSAO_FINAL, data_limite=timezone.now() + timedelta(days=5)
        )
        EntregasMarcos.objects.create(
            ent_tma=entrega, ent_alu=aluno, ent_status=StatusEntrega.ENTREGUE
        )
        enviar_link(entrega, aluno, "https://drive.example/vf1")
        erros = em_paralelo(
            lambda: services_orientacao.conferir_correcoes(orientador, tcc.pk),
            lambda: services_entregas.enviar_entrega(
                aluno, entrega.pk, "https://drive.example/vf2"
            ),
        )
        self.assertEqual(erros, [])
