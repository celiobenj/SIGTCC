"""Testes da navegação até as telas da spec 005 (FR-031; Clarifications, sessão 2026-10-23;
índice Q-89) — spec 005, Phase 11, T036.

Cenários 8 e 9 da US1, 9 da US4 e 6 da US5 do `spec.md`: o item de menu "Turmas" do Aluno e as
listas `minhas_turmas`/`minhas_turmas_arquivadas`; as abas "Meu TCC" e "Atividades" do Aluno; as
abas "Alunos" e "Atividades" do Professor na tela da turma da spec 004 (a Secretaria não vê
"Atividades"); e a tela da turma da spec 004 continua fechada ao Aluno (FR-010 da spec 004).
Escritos antes de `services_tcc.turmas_do_aluno`, `views_tcc.minhas_turmas` e dos includes de
abas (T037 a T040): devem falhar até a implementação.

[US-13][US-15][US-16][US-43][FR-031][Q-89]
"""

from urllib.parse import parse_qs, urlparse

from django.urls import reverse

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import DescricaoTurma, StatusConta, StatusTCC, StatusTurma
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo, criar_secretaria
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    TesteTurmas,
    criar_turma_de,
    matricular_aluno,
)


def _href(nome, *args):
    """Atributo href de um link para a rota (para conferir links no HTML)."""
    return f'href="{reverse(f"cadastro:{nome}", args=args)}"'


class NavegacaoTestBase(TesteTurmas):
    """Professor com uma turma ativa e uma arquivada; Aluno matriculado nas duas; outra turma de
    outro professor com outro aluno."""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(
            self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC, identificador="ECP07_T01"
        )
        self.arquivada = criar_turma_de(
            self.professor,
            descricao=DescricaoTurma.TCC_1,
            curso_nome=EC,
            status=StatusTurma.ARQUIVADA,
            identificador="ECP07_T00",
            ano=2025,
        )
        self.aluno = matricular_aluno(
            self.turma, status_tcc=StatusTCC.EM_ANDAMENTO, status_conta=StatusConta.ATIVA
        )
        matricular_aluno(self.arquivada, aluno=self.aluno, status_tcc=StatusTCC.SEM_PROPOSTA)
        self.outra = criar_turma_de(criar_docente_ativo(), curso_nome=EC, identificador="ECP07_T99")
        matricular_aluno(self.outra, status_tcc=StatusTCC.EM_ANDAMENTO)

    def entrar_como_aluno(self):
        self.client.force_login(self.aluno.alu)


class MenuETurmasDoAlunoTest(NavegacaoTestBase):
    """Cenários 8 e 9 da US1: item "Turmas" do Aluno e as listas. [US-13][FR-031]"""

    def test_menu_do_aluno_tem_o_item_turmas_proprio(self):
        self.entrar_como_aluno()
        resposta = self.client.get(reverse("cadastro:painel"))
        self.assertContains(resposta, _href("minhas_turmas"))
        self.assertNotContains(resposta, _href("turmas"))

    def test_menu_do_docente_e_da_secretaria_nao_tem_o_item_do_aluno(self):
        for usuario in (self.professor, criar_secretaria(curso=self.turma.tur_cur)):
            with self.subTest(usuario=usuario.usu_email):
                self.client.force_login(usuario)
                resposta = self.client.get(reverse("cadastro:painel"))
                self.assertNotContains(resposta, _href("minhas_turmas"))

    def test_cenario8_lista_so_as_turmas_ativas_do_aluno_e_leva_ao_meu_tcc(self):
        self.entrar_como_aluno()
        resposta = self.client.get(reverse("cadastro:minhas_turmas"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "ECP07_T01")
        self.assertContains(resposta, _href("meu_tcc", self.turma.pk))
        self.assertNotContains(resposta, "ECP07_T00")  # arquivada: só na outra lista
        self.assertNotContains(resposta, "ECP07_T99")  # turma de que não participa
        self.assertContains(resposta, _href("minhas_turmas_arquivadas"))
        # Sem acesso à tela da turma da spec 004 (lista de colegas).
        self.assertNotContains(resposta, _href("turma", self.turma.pk))

    def test_cenario8_aluno_continua_sem_a_tela_da_turma_da_spec_004(self):
        """FR-010 da spec 004 sem mudança: o Aluno recebe 403 na tela da turma."""
        self.entrar_como_aluno()
        resposta = self.client.get(reverse("cadastro:turma", args=[self.turma.pk]))
        self.assertContains(resposta, mensagens.M02_ACESSO_NEGADO, status_code=403)

    def test_cenario9_turmas_arquivadas_do_aluno_so_consulta(self):
        self.entrar_como_aluno()
        resposta = self.client.get(reverse("cadastro:minhas_turmas_arquivadas"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "ECP07_T00")
        self.assertNotContains(resposta, "ECP07_T01")
        self.assertContains(resposta, _href("minhas_turmas"))
        resposta = self.client.get(reverse("cadastro:meu_tcc", args=[self.arquivada.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(resposta, "Salvar Proposta")
        self.assertNotContains(resposta, "Salvar alterações")

    def test_sem_login_vai_para_o_login_com_next(self):
        url = reverse("cadastro:minhas_turmas")
        resposta = self.client.get(url)
        self.assertEqual(resposta.status_code, 302)
        destino = urlparse(resposta["Location"])
        self.assertEqual(destino.path, reverse("cadastro:entrar"))
        self.assertEqual(parse_qs(destino.query)["next"], [url])

    def test_docente_e_secretaria_recebem_403_nas_listas_do_aluno(self):
        for usuario in (self.professor, criar_secretaria(curso=self.turma.tur_cur)):
            self.client.force_login(usuario)
            for nome in ("minhas_turmas", "minhas_turmas_arquivadas"):
                with self.subTest(usuario=usuario.usu_email, rota=nome):
                    self.assertEqual(self.client.get(reverse(f"cadastro:{nome}")).status_code, 403)


class AbasDoAlunoTest(NavegacaoTestBase):
    """Cenário 9 da US4: abas "Meu TCC" e "Atividades" do Aluno. [US-13][US-15][FR-031]"""

    def test_meu_tcc_mostra_as_abas_com_meu_tcc_atual(self):
        self.entrar_como_aluno()
        resposta = self.client.get(reverse("cadastro:meu_tcc", args=[self.turma.pk]))
        self.assertContains(resposta, _href("minhas_entregas", self.turma.pk))
        self.assertContains(
            resposta,
            f'{_href("meu_tcc", self.turma.pk)} aria-current="page"',
        )

    def test_cenario9_us4_aba_atividades_lista_as_entregas_com_atividades_atual(self):
        self.entrar_como_aluno()
        resposta = self.client.get(reverse("cadastro:minhas_entregas", args=[self.turma.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, _href("meu_tcc", self.turma.pk))
        self.assertContains(
            resposta,
            f'{_href("minhas_entregas", self.turma.pk)} aria-current="page"',
        )


class AbasDoProfessorTest(NavegacaoTestBase):
    """Cenário 6 da US5: abas "Alunos" e "Atividades" do Professor. [US-16][US-43][FR-031]"""

    def test_cenario6_turma_da_spec_004_mostra_alunos_e_atividades_ao_professor(self):
        self.client.force_login(self.professor)
        resposta = self.client.get(reverse("cadastro:turma", args=[self.turma.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, _href("entregas", self.turma.pk))
        self.assertContains(resposta, f'{_href("turma", self.turma.pk)} aria-current="page"')

    def test_cenario6_secretaria_nao_ve_a_aba_atividades(self):
        self.client.force_login(criar_secretaria(curso=self.turma.tur_cur))
        resposta = self.client.get(reverse("cadastro:turma", args=[self.turma.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(resposta, _href("entregas", self.turma.pk))

    def test_cenario6_aba_atividades_volta_para_alunos(self):
        self.client.force_login(self.professor)
        resposta = self.client.get(reverse("cadastro:entregas", args=[self.turma.pk]))
        self.assertContains(resposta, _href("turma", self.turma.pk))
        self.assertContains(resposta, f'{_href("entregas", self.turma.pk)} aria-current="page"')


class HistoricoPeloProfessorTest(NavegacaoTestBase):
    """Cenário 12 da US2 (validação manual de 2026-10-23; T048): na lista de alunos da tela da
    turma (spec 004), o Professor tem o link "Histórico do Status do TCC" de cada aluno; a
    Secretaria do curso não vê o link. [US-14][FR-009][FR-031]
    """

    def test_professor_ve_e_abre_o_historico_do_aluno(self):
        self.client.force_login(self.professor)
        resposta = self.client.get(reverse("cadastro:turma", args=[self.turma.pk]))
        self.assertContains(resposta, _href("historico_status", self.turma.pk, self.aluno.pk))
        self.assertContains(resposta, "Histórico do Status do TCC")
        resposta = self.client.get(
            reverse("cadastro:historico_status", args=[self.turma.pk, self.aluno.pk])
        )
        self.assertEqual(resposta.status_code, 200)

    def test_secretaria_nao_ve_o_link_do_historico(self):
        self.client.force_login(criar_secretaria(curso=self.turma.tur_cur))
        resposta = self.client.get(reverse("cadastro:turma", args=[self.turma.pk]))
        self.assertNotContains(resposta, _href("historico_status", self.turma.pk, self.aluno.pk))
