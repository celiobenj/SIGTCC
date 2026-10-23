"""Testes de concorrência da Gestão de Contas com duas conexões (tasks T041; SC-003; research C4,
C5, C15, C19, C20; B1, I2, I3, I4).

Cada teste abre uma transação numa thread (conexão A) que trava o mesmo registro e grava algo em
conflito; enquanto a trava está de pé, o serviço roda na conexão principal (B) e fica esperando.
Quando A confirma, B relê e decide: o resultado nunca pode ter as duas gravações em conflito.

[US-03][US-04][US-06][US-50][SC-003][SC-005][FR-001][FR-014][FR-021][FR-026][FR-040]
"""

import logging
import threading
import time
from datetime import timedelta
from unittest import mock

from django.db import connection, transaction
from django.test import TransactionTestCase, override_settings
from django.utils import timezone

from sigtcc.apps.cadastro import services, services_contas
from sigtcc.apps.cadastro.choices import StatusConta, Titulacao
from sigtcc.apps.cadastro.models import (
    Coordenadores,
    Docentes,
    MembrosExternos,
    Secretarios,
    Usuarios,
)
from sigtcc.apps.cadastro.services_contas import ErroDeCampo, VinculosEmAberto
from sigtcc.apps.cadastro.tests.apoio_contas import (
    SI,
    coordenador_de,
    curso,
    docente_de,
    membro,
    secretaria_de,
    turma_do_docente,
)

ESPERA = 0.6  # segundos que A segura a trava depois de B começar


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    SIGTCC_EMAIL_SINCRONO=True,
)
class ConcorrenciaContasTest(TransactionTestCase):
    """Gravações simultâneas resolvidas pelas travas da C19. [SC-003][B1]"""

    serialized_rollback = True  # mantém os cursos da carga da spec 001

    def setUp(self):
        super().setUp()
        for nome in ("sigtcc.acesso", "sigtcc.contas"):
            registro = logging.getLogger(nome)
            corretor = mock.patch.object(registro, "handlers", [logging.NullHandler()])
            corretor.start()
            self.addCleanup(corretor.stop)

    def _em_paralelo(self, conexao_a):
        """Roda conexao_a(pronto) numa thread: ela trava, sinaliza pronto, espera e confirma."""
        pronto = threading.Event()
        erros = []

        def alvo():
            try:
                with transaction.atomic():
                    conexao_a(pronto)
                    time.sleep(ESPERA)
            except Exception as erro:  # registra para o teste falhar com a causa
                erros.append(erro)
                pronto.set()
            finally:
                connection.close()

        thread = threading.Thread(target=alvo)
        thread.start()
        self.assertTrue(pronto.wait(10))
        return thread, erros

    def _terminar(self, thread, erros):
        thread.join(15)
        self.assertEqual(erros, [])

    def _dados_docente(self, email, **campos):
        dados = {
            "nome": "Docente Novo",
            "email": email,
            "titulacao": Titulacao.DOUTOR,
            "curso_lotacao": curso(SI),
            "coordenador": False,
            "curso_coordenado": None,
        }
        dados.update(campos)
        return dados

    def test_mesmo_email_com_caixa_diferente(self):
        secretaria = secretaria_de(SI)

        def a(pronto):
            services.travar_email("maria@uea.edu.br")
            Usuarios.objects.create_user("maria@uea.edu.br", "Maria A")
            pronto.set()

        thread, erros = self._em_paralelo(a)
        with self.assertRaises(ErroDeCampo) as erro:
            services_contas.cadastrar_docente(secretaria, self._dados_docente("MARIA@uea.edu.br"))
        self._terminar(thread, erros)
        self.assertEqual(erro.exception.campo, "email")
        self.assertEqual(Usuarios.objects.filter(usu_email__iexact="maria@uea.edu.br").count(), 1)

    def test_dois_coordenadores_para_o_mesmo_curso(self):
        secretaria = secretaria_de(SI)
        rival = docente_de(SI)

        def a(pronto):
            services_contas.travar_cursos(curso(SI).pk)
            Coordenadores.objects.create(cor_cur=curso(SI), cor_doc=rival.docentes)
            pronto.set()

        thread, erros = self._em_paralelo(a)
        dados = self._dados_docente(
            "coord@uea.edu.br", coordenador=True, curso_coordenado=curso(SI)
        )
        with self.assertRaises(ErroDeCampo):
            services_contas.cadastrar_docente(secretaria, dados)
        self._terminar(thread, erros)
        self.assertEqual(Coordenadores.objects.filter(cor_cur=curso(SI)).count(), 1)

    def test_duas_secretarias_para_o_mesmo_curso(self):
        coordenador = coordenador_de(SI)

        def a(pronto):
            services_contas.travar_cursos(curso(SI).pk)
            conta = Usuarios.objects.create_user("sec.a@uea.edu.br", "Secretaria A")
            Secretarios.objects.create(sec=conta, sec_cur=curso(SI))
            pronto.set()

        thread, erros = self._em_paralelo(a)
        with self.assertRaises(ErroDeCampo):
            services_contas.cadastrar_secretaria(
                coordenador,
                {"nome": "Secretaria B", "email": "sec.b@uea.edu.br", "curso_vinculado": curso(SI)},
            )
        self._terminar(thread, erros)
        self.assertEqual(Secretarios.objects.filter(sec_cur=curso(SI)).count(), 1)

    def test_inativacao_contra_vinculo_novo(self):
        secretaria = secretaria_de(SI)
        docente = docente_de(SI)

        def a(pronto):
            self.assertTrue(services_contas.travar_e_conferir_ativo(docente))
            turma_do_docente(docente)
            pronto.set()

        thread, erros = self._em_paralelo(a)
        with self.assertRaises(VinculosEmAberto):
            services_contas.inativar_docente(secretaria, docente.pk)
        self._terminar(thread, erros)
        docente.refresh_from_db()
        self.assertEqual(docente.usu_status, StatusConta.ATIVA)

    def test_expiracao_contra_prorrogacao(self):
        conta = membro(validade=timezone.now().date() - timedelta(days=1))
        nova = timezone.now().date() + timedelta(days=6)

        def a(pronto):
            services_contas.travar_conta(conta.pk)
            MembrosExternos.objects.filter(pk=conta.pk).update(
                mem_validade_ate=nova, mem_prorrogado_ate=nova
            )
            pronto.set()

        thread, erros = self._em_paralelo(a)
        expirou = services.expirar_se_vencida(conta)
        self._terminar(thread, erros)
        self.assertFalse(expirou)
        self.assertEqual(Usuarios.objects.get(pk=conta.pk).usu_status, StatusConta.ATIVA)

    def test_edicao_contra_inativacao(self):
        coordenador = coordenador_de(SI)
        docente = docente_de(SI)

        def a(pronto):
            services_contas.travar_conta(docente.pk)
            Usuarios.objects.filter(pk=docente.pk).update(usu_status=StatusConta.INATIVA)
            pronto.set()

        thread, erros = self._em_paralelo(a)
        services_contas.alterar_docente(
            coordenador,
            docente.pk,
            self._dados_docente(docente.usu_email, nome="Nome Corrigido"),
        )
        self._terminar(thread, erros)
        docente.refresh_from_db()
        self.assertEqual(docente.usu_nome, "Nome Corrigido")
        self.assertEqual(docente.usu_status, StatusConta.INATIVA)
        self.assertEqual(Docentes.objects.get(pk=docente.pk).doc_cur, curso(SI))
