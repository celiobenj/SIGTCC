"""Permissões de todas as rotas da feature 004 (SC-004; contracts/rotas.md).

Ordem das conferências (research B2): turma existe (404) → permissão (403 com a M-02) → turma
arquivada (MT-25). Nas rotas do aluno, o aluno precisa estar matriculado na turma (404).

[SC-004][FR-008][FR-009][Q9][I-7][US-07][US-08][US-09]
"""

from urllib.parse import urlparse

from django.urls import reverse

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import DescricaoTurma, StatusTCC, StatusTurma
from sigtcc.apps.cadastro.models import AlunosTurmas, Turmas
from sigtcc.apps.cadastro.tests.apoio_acesso import (
    criar_coordenador,
    criar_docente_ativo,
    criar_secretaria,
)
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    SI,
    TesteTurmas,
    criar_turma_de,
    curso,
    matricular_aluno,
    tcc_de,
)

# Rotas sem turma: nome → perfis que entram.
ROTAS_GERAIS = ("turmas", "turmas_arquivadas", "turma_nova", "modelo_importacao")
# Rotas da turma (tur_id) e do aluno (tur_id, alu_id).
ROTAS_DA_TURMA = (
    "turma",
    "turma_editar",
    "turma_excluir",
    "turma_arquivar",
    "matricular",
    "importar",
    "importar_confirmar",
    "importar_resumo",
    "importar_cancelar",
    "excluidos_transferidos",
)
ROTAS_DO_ALUNO = ("aluno_editar", "aluno_transferir", "aluno_excluir", "aluno_encerrar")
# Rotas só por POST (as outras abrem com GET).
SO_POST = ("importar_confirmar", "importar_cancelar")
# Rotas que a Secretaria do curso da turma abre (spec Q9).
DA_SECRETARIA = ("turmas", "turmas_arquivadas", "turma", "aluno_transferir")
# Ações que mudam dados: na turma arquivada, MT-25 (FR-008).
ACOES = (
    "turma_editar",
    "turma_excluir",
    "turma_arquivar",
    "matricular",
    "importar",
    "importar_confirmar",
    "aluno_editar",
    "aluno_transferir",
    "aluno_excluir",
    "aluno_encerrar",
)


class PermissoesTurmasTest(TesteTurmas):
    """Cada rota de contracts/rotas.md, perfil por perfil. [SC-004]"""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        self.aluno = matricular_aluno(self.turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        # Destino possível da transferência (TCC 2, mesmo curso e período, outro professor).
        criar_turma_de(criar_docente_ativo(), descricao=DescricaoTurma.TCC_2, curso_nome=EC)

    def url(self, nome, aluno=None):
        if nome in ROTAS_GERAIS:
            return reverse(f"cadastro:{nome}")
        if nome in ROTAS_DO_ALUNO:
            return reverse(f"cadastro:{nome}", args=[self.turma.pk, (aluno or self.aluno).pk])
        return reverse(f"cadastro:{nome}", args=[self.turma.pk])

    def pedir(self, nome, aluno=None, follow=False):
        """GET, ou POST vazio nas rotas só por POST."""
        metodo = self.client.post if nome in SO_POST else self.client.get
        return metodo(self.url(nome, aluno), follow=follow)

    def todas(self):
        return ROTAS_GERAIS + ROTAS_DA_TURMA + ROTAS_DO_ALUNO

    def assert_negado(self, nome):
        resposta = self.pedir(nome)
        self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)

    # ------------------------------------------------------------------ (a) sem login

    def test_sem_login_vai_para_o_login_com_next(self):
        entrar = reverse("cadastro:entrar")
        for nome in self.todas():
            with self.subTest(rota=nome):
                resposta = self.pedir(nome)
                self.assertEqual(resposta.status_code, 302)
                destino = urlparse(resposta["Location"])
                self.assertEqual(destino.path, entrar)
                self.assertIn("next=", destino.query)

    # ------------------------------------------------------------------ (b) e (c) sem a turma

    def test_docente_de_outra_turma_e_coordenador_403(self):
        for usuario in (criar_docente_ativo(), criar_coordenador()):
            self.client.force_login(usuario)
            for nome in ROTAS_DA_TURMA + ROTAS_DO_ALUNO:
                with self.subTest(usuario=usuario.pk, rota=nome):
                    if nome == "turma":
                        # US-07 E8 (v3.4; hotfix v0.2.1): texto próprio ao abrir a turma.
                        resposta = self.pedir(nome)
                        self.assertContains(
                            resposta, mensagens.SEM_PERMISSAO_PAGINA, status_code=403
                        )
                    else:
                        self.assert_negado(nome)

    def test_secretaria_de_outro_curso_403(self):
        self.client.force_login(criar_secretaria(curso=curso(SI)))
        for nome in ROTAS_DA_TURMA + ROTAS_DO_ALUNO + ("turma_nova", "modelo_importacao"):
            with self.subTest(rota=nome):
                self.assert_negado(nome)

    # ------------------------------------------------------------------ (d) Secretaria do curso

    def test_secretaria_do_curso_so_consulta_e_transfere(self):
        self.client.force_login(criar_secretaria(curso=curso(EC)))
        for nome in self.todas():
            with self.subTest(rota=nome):
                if nome in DA_SECRETARIA:
                    self.assertEqual(self.pedir(nome).status_code, 200)
                else:
                    self.assert_negado(nome)

    def test_professor_abre_todas_as_rotas_da_turma(self):
        self.client.force_login(self.professor)
        for nome in self.todas():
            with self.subTest(rota=nome):
                self.assertIn(self.pedir(nome).status_code, (200, 302))

    # ------------------------------------------------------------------ (e) turma arquivada

    def arquivar(self):
        Turmas.objects.filter(pk=self.turma.pk).update(tur_status=StatusTurma.ARQUIVADA)

    def test_turma_arquivada_mt25_nas_acoes(self):
        self.arquivar()
        self.client.force_login(self.professor)
        for nome in ACOES:
            with self.subTest(rota=nome):
                resposta = self.pedir(nome, follow=True)
                self.assertContains(resposta, mensagens.MT25_TURMA_ARQUIVADA)
                self.assertEqual(
                    resposta.redirect_chain[-1][0],
                    reverse("cadastro:turma", args=[self.turma.pk]),
                )

    def test_turma_arquivada_403_antes_da_mt25_para_quem_nao_tem_permissao(self):
        self.arquivar()
        self.client.force_login(criar_docente_ativo())
        for nome in ACOES:
            with self.subTest(rota=nome):
                self.assert_negado(nome)

    def test_turma_arquivada_continua_consultavel(self):
        self.arquivar()
        self.client.force_login(self.professor)
        for nome in ("turma", "excluidos_transferidos"):
            with self.subTest(rota=nome):
                self.assertEqual(self.pedir(nome).status_code, 200)

    # ------------------------------------------------------------------ (f) aluno de outra turma

    def test_aluno_de_outra_turma_404(self):
        outro = matricular_aluno(criar_turma_de(criar_docente_ativo()))
        self.client.force_login(self.professor)
        for nome in ROTAS_DO_ALUNO:
            with self.subTest(rota=nome):
                self.assertEqual(self.client.get(self.url(nome, outro)).status_code, 404)

    def test_turma_inexistente_404(self):
        self.client.force_login(self.professor)
        for nome in ROTAS_DA_TURMA:
            with self.subTest(rota=nome):
                url = reverse(f"cadastro:{nome}", args=[999999])
                metodo = self.client.post if nome in SO_POST else self.client.get
                self.assertEqual(metodo(url).status_code, 404)

    # ------------------------------------------------------------------ (g) ações só por POST

    def test_rotas_so_post_recusam_get(self):
        self.client.force_login(self.professor)
        for nome in SO_POST:
            with self.subTest(rota=nome):
                self.assertEqual(self.client.get(self.url(nome)).status_code, 405)

    def test_get_das_acoes_nao_altera_nada(self):
        sem_proposta = matricular_aluno(self.turma)
        self.client.force_login(self.professor)
        for nome in ("turma_excluir", "turma_arquivar", "aluno_encerrar"):
            self.client.get(self.url(nome))
        self.client.get(self.url("aluno_excluir", sem_proposta))
        turma = Turmas.objects.get(pk=self.turma.pk)
        self.assertEqual(turma.tur_status, StatusTurma.ATIVA)
        self.assertTrue(AlunosTurmas.objects.filter(mat_tur=turma, mat_alu=sem_proposta).exists())
        self.assertEqual(tcc_de(self.aluno, turma).tcc_status, StatusTCC.EM_ANDAMENTO)
