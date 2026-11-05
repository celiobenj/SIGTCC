"""Permissões da spec 009 (research B2; IC-08/IC-18): matriz perfil × status das funções novas de
permissoes_defesa (documentos, declaração, ouvintes, ocorrências, agenda e Ouvintes das
defesas), com o Suplente não acionado, o suplente acionado, a turma arquivada e o Presidente de
TCC 1 depois da matrícula no TCC 2 (B-03).

[US-28][US-30][RBN-DEF-07.3][RBN-DEF-08.1][RBN-DEF-08.2][RBN-DEF-08.3][RBN-DEF-08.4]
[RBN-DEF-08.5] (spec 009, tasks T009)
"""

from sigtcc.apps.cadastro import services_orientacao, services_turmas
from sigtcc.apps.cadastro.choices import DescricaoTurma, StatusTurma
from sigtcc.apps.cadastro.models import Turmas
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_membro_externo, criar_secretaria
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, criar_turma_de
from sigtcc.apps.defesa import permissoes_defesa as perm
from sigtcc.apps.defesa.choices import StatusSessao
from sigtcc.apps.defesa.models import Defesas
from sigtcc.apps.defesa.tests.apoio_avaliacao import TesteAvaliacao, sessao_com_banca
from sigtcc.apps.defesa.tests.apoio_documentos import ouvinte, presenca, sessao_liberada

# Status sem liberação (Realizada aqui é "antes da liberação": avancar_para não libera).
STATUS_SEM_LIBERACAO = (
    StatusSessao.AGENDADA,
    StatusSessao.REAGENDADA,
    StatusSessao.EM_ANDAMENTO,
    StatusSessao.REALIZADA,
    StatusSessao.CANCELADA,
)
TODOS = (
    "presidente",
    "av1",
    "av2",
    "suplente",
    "professor",
    "secretaria",
    "secretaria_outra",
    "coordenador",
    "aluno",
    "membro_externo",
)


def recarregar(sessao):
    """A sessão relida do banco (TCC e turma sem cache). [US-28][US-30]"""
    return Defesas.objects.select_related("def_tcc__tcc_tur").get(pk=sessao.pk)


class BasePermissoes(TesteAvaliacao):
    """Perfis de cada cenário e a conferência da matriz. [US-28][US-30][RBN-DEF-07.3]"""

    def perfis(self, cenario):
        """Usuarios de cada perfil da matriz, a partir do cenário de sessao_com_banca.
        [US-28][US-30]
        """
        tcc = cenario["tcc"]
        return {
            "presidente": cenario["orientador"],
            "av1": cenario["av1"],
            "av2": cenario["av2"],
            "suplente": cenario["suplente"],
            "professor": cenario["professor"],
            "secretaria": criar_secretaria(curso=tcc.tcc_tur.tur_cur),
            "secretaria_outra": criar_secretaria(),
            "coordenador": cenario["coordenador"],
            "aluno": cenario["aluno"],
            "membro_externo": criar_membro_externo(),
        }

    def conferir(self, funcao, sessao, perfis, permitidos):
        """Cada perfil recebe True se e somente se está em `permitidos`. [US-28][US-30]"""
        for nome in TODOS:
            with self.subTest(funcao=funcao.__name__, status=sessao.def_status, perfil=nome):
                self.assertEqual(funcao(perfis[nome], sessao), nome in permitidos)


class TesteDocumentosEDeclaracao(BasePermissoes):
    """pode_baixar_documentos e pode_baixar_declaracao (FR-005, FR-021; P5, P13).
    [US-28][US-30][RBN-DEF-07.3][RBN-DEF-08.3]
    """

    def test_antes_da_liberacao_ninguem_baixa(self):
        for status in STATUS_SEM_LIBERACAO:
            cenario = sessao_com_banca(status)
            sessao, perfis = recarregar(cenario["sessao"]), self.perfis(cenario)
            self.conferir(perm.pode_baixar_documentos, sessao, perfis, ())
            self.conferir(perm.pode_baixar_declaracao, sessao, perfis, ())

    def test_depois_da_liberacao(self):
        cenario = sessao_liberada()
        sessao, perfis = recarregar(cenario["sessao"]), self.perfis(cenario)
        self.conferir(
            perm.pode_baixar_documentos,
            sessao,
            perfis,
            ("presidente", "av1", "av2", "professor", "secretaria", "aluno"),
        )
        self.conferir(perm.pode_baixar_declaracao, sessao, perfis, ("presidente", "av1", "av2"))

    def test_suplente_acionado_entra_e_o_ausente_sai(self):
        cenario = sessao_liberada(suplente_acionado=True)
        sessao, perfis = recarregar(cenario["sessao"]), self.perfis(cenario)
        efetivos = ("presidente", "av1", "suplente")
        self.conferir(
            perm.pode_baixar_documentos,
            sessao,
            perfis,
            efetivos + ("professor", "secretaria", "aluno"),
        )
        self.conferir(perm.pode_baixar_declaracao, sessao, perfis, efetivos)

    def test_turma_arquivada_nao_tira_os_documentos(self):
        cenario = sessao_liberada()
        Turmas.objects.filter(pk=cenario["tcc"].tcc_tur_id).update(tur_status=StatusTurma.ARQUIVADA)
        sessao, perfis = recarregar(cenario["sessao"]), self.perfis(cenario)
        self.assertTrue(perm.pode_baixar_documentos(perfis["aluno"], sessao))
        self.assertTrue(perm.pode_baixar_declaracao(perfis["presidente"], sessao))


class TesteOuvintes(BasePermissoes):
    """pode_editar_ouvintes e pode_ver_ouvintes (FR-009, FR-012; P3, P6; revisão B-02).
    [US-30][RBN-DEF-08.2]
    """

    def test_em_andamento_e_realizada(self):
        for cenario in (
            sessao_com_banca(StatusSessao.EM_ANDAMENTO),
            sessao_com_banca(StatusSessao.REALIZADA),
            sessao_liberada(),
        ):
            sessao, perfis = recarregar(cenario["sessao"]), self.perfis(cenario)
            self.conferir(perm.pode_editar_ouvintes, sessao, perfis, ("presidente", "professor"))
            self.conferir(
                perm.pode_ver_ouvintes, sessao, perfis, ("presidente", "professor", "secretaria")
            )

    def test_agendada_reagendada_e_cancelada(self):
        for status in (StatusSessao.AGENDADA, StatusSessao.REAGENDADA, StatusSessao.CANCELADA):
            cenario = sessao_com_banca(status)
            sessao, perfis = recarregar(cenario["sessao"]), self.perfis(cenario)
            self.conferir(perm.pode_editar_ouvintes, sessao, perfis, ())
            # Sem presenças gravadas, ninguém vê a lista.
            self.conferir(perm.pode_ver_ouvintes, sessao, perfis, ())
            # Com presenças gravadas (sessão Em Andamento reagendada, P3): só leitura ao
            # Presidente e ao Professor da Disciplina; a Secretaria, não (P6).
            presenca(sessao, ouvinte(matricula=f"20260000{len(status):02d}"))
            self.conferir(perm.pode_ver_ouvintes, sessao, perfis, ("presidente", "professor"))

    def test_turma_arquivada(self):
        cenario = sessao_liberada()
        Turmas.objects.filter(pk=cenario["tcc"].tcc_tur_id).update(tur_status=StatusTurma.ARQUIVADA)
        sessao, perfis = recarregar(cenario["sessao"]), self.perfis(cenario)
        self.conferir(perm.pode_editar_ouvintes, sessao, perfis, ())
        # Sem presenças, o Presidente e o Professor não têm o que ler; a Secretaria vê a lista.
        self.conferir(perm.pode_ver_ouvintes, sessao, perfis, ("secretaria",))
        presenca(sessao, ouvinte())
        self.conferir(
            perm.pode_ver_ouvintes, sessao, perfis, ("presidente", "professor", "secretaria")
        )


class TesteOcorrencias(BasePermissoes):
    """pode_editar_ocorrencias e pode_ver_ocorrencias (FR-013 a FR-015; P9, P10; revisão I-01).
    [US-30][RBN-DEF-08.5]
    """

    def com_texto(self, sessao):
        """Grava um texto de ocorrências direto, só para montar o cenário. [US-30]"""
        Defesas.objects.filter(pk=sessao.pk).update(def_ocorrencias="Queda de energia")
        return recarregar(sessao)

    def test_edicao_so_do_presidente_em_andamento(self):
        for status in STATUS_SEM_LIBERACAO:
            cenario = sessao_com_banca(status)
            sessao, perfis = recarregar(cenario["sessao"]), self.perfis(cenario)
            permitidos = ("presidente",) if status == StatusSessao.EM_ANDAMENTO else ()
            self.conferir(perm.pode_editar_ocorrencias, sessao, perfis, permitidos)

    def test_depois_da_liberacao_e_com_turma_arquivada_nao_edita(self):
        cenario = sessao_liberada()
        sessao, perfis = recarregar(cenario["sessao"]), self.perfis(cenario)
        self.conferir(perm.pode_editar_ocorrencias, sessao, perfis, ())
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        Turmas.objects.filter(pk=cenario["tcc"].tcc_tur_id).update(tur_status=StatusTurma.ARQUIVADA)
        sessao, perfis = recarregar(cenario["sessao"]), self.perfis(cenario)
        self.conferir(perm.pode_editar_ocorrencias, sessao, perfis, ())

    def test_leitura_com_texto_gravado(self):
        for cenario in (sessao_com_banca(StatusSessao.EM_ANDAMENTO), sessao_liberada()):
            sessao, perfis = recarregar(cenario["sessao"]), self.perfis(cenario)
            self.conferir(perm.pode_ver_ocorrencias, sessao, perfis, ())
            sessao = self.com_texto(sessao)
            self.conferir(
                perm.pode_ver_ocorrencias,
                sessao,
                perfis,
                ("presidente", "professor", "secretaria"),
            )


class TesteAgendaEOuvintesDasDefesas(BasePermissoes):
    """pode_gerar_agenda (FR-022; P2) e pode_ver_ouvintes_das_defesas (FR-016; P8).
    [US-30][RBN-DEF-08.1][RBN-DEF-08.4]
    """

    def test_por_perfil(self):
        cenario = sessao_com_banca(StatusSessao.AGENDADA)
        perfis = self.perfis(cenario)
        for nome in TODOS:
            with self.subTest(perfil=nome):
                self.assertEqual(
                    perm.pode_gerar_agenda(perfis[nome]),
                    nome not in ("aluno", "membro_externo"),
                )
                self.assertEqual(
                    perm.pode_ver_ouvintes_das_defesas(perfis[nome]),
                    nome in ("secretaria", "secretaria_outra"),
                )


class TestePresidenteDeTcc1DepoisDoTcc2(BasePermissoes):
    """B-03: o Presidente da banca de TCC 1 continua com os direitos da sessão depois que o
    aluno aprovado é matriculado no TCC 2 (_copiar_tcc_aprovado encerra a orientação do TCC 1).
    [US-28][US-30][RBN-DEF-07.3][RBN-DEF-08.2][RBN-DEF-08.3][RBN-DEF-08.5]
    """

    def test_presidente_mantem_os_direitos(self):
        cenario = sessao_liberada(etapa=DescricaoTurma.TCC_1)
        tcc1, presidente = cenario["tcc"], cenario["orientador"]
        turma2 = criar_turma_de(cenario["professor"], DescricaoTurma.TCC_2, EC)
        services_turmas._copiar_tcc_aprovado(cenario["professor"], turma2, tcc1.tcc_alu, tcc1)
        tcc1.refresh_from_db()
        self.assertFalse(services_orientacao.e_orientador_atual(presidente, tcc1))
        Defesas.objects.filter(pk=cenario["sessao"].pk).update(def_ocorrencias="Sem incidentes")
        sessao = recarregar(cenario["sessao"])
        self.assertTrue(perm.e_presidente(presidente, sessao))
        self.assertTrue(perm.pode_baixar_documentos(presidente, sessao))
        self.assertTrue(perm.pode_baixar_declaracao(presidente, sessao))
        self.assertTrue(perm.pode_editar_ouvintes(presidente, sessao))
        self.assertTrue(perm.pode_ver_ouvintes(presidente, sessao))
        self.assertTrue(perm.pode_ver_ocorrencias(presidente, sessao))

    def test_e_presidente_e_a_regra_unica(self):
        cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO)
        sessao = recarregar(cenario["sessao"])
        for nome, usuario in self.perfis(cenario).items():
            with self.subTest(perfil=nome):
                esperado = nome == "presidente"
                self.assertEqual(perm.e_presidente(usuario, sessao), esperado)
                self.assertEqual(perm._e_presidente(usuario, sessao), esperado)
