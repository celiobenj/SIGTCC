"""Permissões por perfil nas rotas da feature 005 (contracts/rotas.md; SC-004) — T033.

Todas as 11 rotas da feature (as 9 originais e as 2 listas de turmas do Aluno, FR-031), perfil por
perfil: sem login (login com `next`); outro Docente
(403, M-02); Secretaria do curso (403 — Clarifications, sessão 2026-10-22); Coorientador do
NUCOMP com coorientação aceita (403 no histórico — Clarifications); aluno de outra turma (404,
sem IDOR); turma arquivada (consulta liberada, ações com a MT-25 ou sem efeito); e nenhum dado
muda por GET.

[SC-004][Clarifications][contracts/rotas.md][FR-009][FR-017][FR-027][FR-030][FR-031]
"""

from datetime import timedelta
from urllib.parse import urlparse

from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    StatusConta,
    StatusCoorientacao,
    StatusEntrega,
    StatusTCC,
    StatusTurma,
    TipoEntrega,
)
from sigtcc.apps.cadastro.models import (
    Coorientacoes,
    EntregasMarcos,
    HistoricoEnviosEntregas,
    TurmasMarcos,
)
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo, criar_secretaria
from sigtcc.apps.cadastro.tests.apoio_tcc import cadastrar_entrega, enviar_link
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    TesteTurmas,
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)

# Rotas do Aluno (o próprio, pela turma) e do Professor da Disciplina (contracts/rotas.md).
ROTAS_DO_ALUNO = ("meu_tcc", "historico_status_aluno", "minhas_entregas", "entrega_enviar")
# Listas do item "Turmas" do Aluno (FR-031, Q-89): sem turma no endereço; cada aluno vê só as dele.
ROTAS_DE_LISTA_DO_ALUNO = ("minhas_turmas", "minhas_turmas_arquivadas")
ROTAS_DO_PROFESSOR = (
    "historico_status",
    "entregas",
    "entrega_cadastrar",
    "entrega_acompanhar",
    "aluno_versao_final",
)
LINK_PDF = "https://drive.google.com/versao-final.pdf"


class PermissoesTCCTest(TesteTurmas):
    """Turma de TCC 2 com um aluno "Aprovado" e a Versão Final já enviada."""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        self.aluno = matricular_aluno(
            self.turma, status_tcc=StatusTCC.APROVADO, status_conta=StatusConta.ATIVA
        )
        self.versao_final = cadastrar_entrega(
            self.turma,
            tipo=TipoEntrega.VERSAO_FINAL,
            titulo="Versão Final",
            data_limite=timezone.now() + timedelta(days=5),
        )
        EntregasMarcos.objects.create(
            ent_tma=self.versao_final, ent_alu=self.aluno, ent_status=StatusEntrega.ENTREGUE
        )
        enviar_link(self.versao_final, self.aluno, LINK_PDF)

    def url(self, nome):
        argumentos = {
            "meu_tcc": [self.turma.pk],
            "historico_status_aluno": [self.turma.pk],
            "minhas_entregas": [self.turma.pk],
            "entrega_enviar": [self.turma.pk, self.versao_final.pk],
            "historico_status": [self.turma.pk, self.aluno.pk],
            "entregas": [self.turma.pk],
            "entrega_cadastrar": [self.turma.pk],
            "entrega_acompanhar": [self.turma.pk, self.versao_final.pk],
            "aluno_versao_final": [self.turma.pk, self.aluno.pk],
            "minhas_turmas": [],
            "minhas_turmas_arquivadas": [],
        }[nome]
        return reverse(f"cadastro:{nome}", args=argumentos)

    def assert_negado(self, nome):
        resposta = self.client.get(self.url(nome))
        self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)

    def estado(self):
        """Fotografia dos dados que alguma rota poderia mudar."""
        registro = EntregasMarcos.objects.get(ent_tma=self.versao_final, ent_alu=self.aluno)
        return (
            tcc_de(self.aluno, self.turma).tcc_status,
            registro.ent_status,
            HistoricoEnviosEntregas.objects.count(),
            TurmasMarcos.objects.count(),
        )

    # ------------------------------------------------------------------ sem login

    def test_sem_login_vai_para_o_login_com_next(self):
        entrar = reverse("cadastro:entrar")
        for nome in ROTAS_DO_ALUNO + ROTAS_DE_LISTA_DO_ALUNO + ROTAS_DO_PROFESSOR:
            with self.subTest(rota=nome):
                resposta = self.client.get(self.url(nome))
                self.assertEqual(resposta.status_code, 302)
                destino = urlparse(resposta["Location"])
                self.assertEqual(destino.path, entrar)
                self.assertIn("next=", destino.query)

    # ------------------------------------------------------------------ outro Docente

    def test_outro_docente_recebe_403_em_todas_as_rotas(self):
        self.client.force_login(criar_docente_ativo())
        for nome in ROTAS_DO_ALUNO + ROTAS_DE_LISTA_DO_ALUNO + ROTAS_DO_PROFESSOR:
            with self.subTest(rota=nome):
                self.assert_negado(nome)

    # ------------------------------------------------------------------ Secretaria do curso

    def test_secretaria_do_curso_recebe_403(self):
        """Clarifications: a Secretaria não vê histórico, entregas nem a Proposta do aluno."""
        self.client.force_login(criar_secretaria(curso=self.turma.tur_cur))
        for nome in ROTAS_DO_ALUNO + ROTAS_DE_LISTA_DO_ALUNO + ROTAS_DO_PROFESSOR:
            with self.subTest(rota=nome):
                self.assert_negado(nome)

    # ------------------------------------------------------------------ Coorientador do NUCOMP

    def test_coorientador_com_coorientacao_ativa_recebe_403(self):
        """Clarifications: o Coorientador não ganha acesso ao histórico nem às entregas aqui."""
        coorientador = criar_docente_ativo()
        Coorientacoes.objects.create(
            coo_tcc=tcc_de(self.aluno, self.turma),
            coo_doc=coorientador.docentes,
            coo_status=StatusCoorientacao.ATIVA,
            coo_data_inicio=timezone.now(),
        )
        self.client.force_login(coorientador)
        for nome in ROTAS_DO_PROFESSOR:
            with self.subTest(rota=nome):
                self.assert_negado(nome)

    # ------------------------------------------------------------------ aluno (sem IDOR)

    def test_aluno_de_outra_turma_recebe_404_nas_rotas_do_aluno(self):
        outra_turma = criar_turma_de(criar_docente_ativo(), curso_nome=EC)
        intruso = matricular_aluno(
            outra_turma, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        )
        self.client.force_login(intruso.alu)
        for nome in ROTAS_DO_ALUNO:
            with self.subTest(rota=nome):
                self.assertEqual(self.client.get(self.url(nome)).status_code, 404)

    def test_aluno_nao_abre_as_rotas_do_professor(self):
        self.client.force_login(self.aluno.alu)
        for nome in ROTAS_DO_PROFESSOR:
            with self.subTest(rota=nome):
                self.assert_negado(nome)

    def test_dono_e_professor_abrem_as_proprias_rotas(self):
        self.client.force_login(self.aluno.alu)
        for nome in ROTAS_DO_ALUNO + ROTAS_DE_LISTA_DO_ALUNO:
            with self.subTest(rota=nome):
                self.assertEqual(self.client.get(self.url(nome)).status_code, 200)
        self.client.force_login(self.professor)
        for nome in ROTAS_DO_PROFESSOR:
            with self.subTest(rota=nome):
                self.assertEqual(self.client.get(self.url(nome)).status_code, 200)

    # ------------------------------------------------------------------ turma arquivada

    def test_turma_arquivada_libera_a_consulta_e_bloqueia_as_acoes(self):
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save(update_fields=["tur_status"])
        antes = self.estado()

        self.client.force_login(self.aluno.alu)
        for nome in ROTAS_DO_ALUNO:
            with self.subTest(consulta=nome):
                self.assertEqual(self.client.get(self.url(nome)).status_code, 200)
        self.client.post(self.url("entrega_enviar"), {"link": LINK_PDF})

        self.client.force_login(self.professor)
        for nome in ("historico_status", "entregas", "entrega_acompanhar", "aluno_versao_final"):
            with self.subTest(consulta=nome):
                self.assertEqual(self.client.get(self.url(nome)).status_code, 200)
        for nome, dados in (
            ("entrega_cadastrar", {"tipo": TipoEntrega.OUTRA, "titulo": "Nova"}),
            ("aluno_versao_final", {"acao": "homologar"}),
        ):
            with self.subTest(acao=nome):
                resposta = self.client.post(self.url(nome), dados, follow=True)
                self.assertContains(resposta, mensagens.MT25_TURMA_ARQUIVADA)
        self.assertEqual(self.estado(), antes)

    # ------------------------------------------------------------------ só POST muda dado

    def test_get_nunca_muda_dado(self):
        antes = self.estado()
        self.client.force_login(self.aluno.alu)
        self.client.get(self.url("entrega_enviar"), {"link": LINK_PDF})
        self.client.get(self.url("meu_tcc"), {"acao": "salvar_alteracoes"})
        self.client.force_login(self.professor)
        self.client.get(self.url("aluno_versao_final"), {"acao": "homologar"})
        self.client.get(self.url("entrega_cadastrar"), {"tipo": TipoEntrega.OUTRA, "titulo": "X"})
        self.assertEqual(self.estado(), antes)
