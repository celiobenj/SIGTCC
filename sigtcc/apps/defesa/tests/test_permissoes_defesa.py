"""Permissões da feature 007 pelo endereço direto (SC-004): cada perfil contra cada rota, numa
sessão de Engenharia de Computação (quem agenda é o Orientador) e numa de Sistemas de Informação
(quem agenda é o Professor da Disciplina). Sem permissão: 403, nunca o conteúdo.

[SC-004][US-21][US-23][US-24][US-40][RBN-DEF-01.3][RBN-DEF-01.4][RBN-DEF-02.2][RBN-DEF-02.4]
[RBN-DEF-03.3][FR-003][FR-011][FR-013][FR-022][FR-030] (tasks T054)
"""

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro.choices import StatusConta
from sigtcc.apps.cadastro.tests.apoio_acesso import (
    criar_coordenador,
    criar_membro_externo,
    criar_secretaria,
)
from sigtcc.apps.cadastro.tests.apoio_orientacao import vincular_coorientador
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, SI, TesteTurmas, curso
from sigtcc.apps.defesa.choices import StatusSessao
from sigtcc.apps.defesa.tests.apoio_defesa import (
    agendar_sessao_de,
    avancar_para,
    docente,
    tcc_apto,
)

# Rotas da sessão; "acionar_suplente" só vale com a sessão Em Andamento (testada à parte).
ROTAS = ("sessao", "historico", "alterar_banca", "reagendar", "cancelar")


def ativo(usuario):
    """Conta 'Ativa', para o login dos testes valer (o aluno da fábrica nasce aguardando)."""
    usuario.usu_status = StatusConta.ATIVA
    usuario.save(update_fields=["usu_status"])
    return usuario


class TestePermissoesPorRota(TesteTurmas):
    """Cada perfil, cada rota, as duas regras de curso. [SC-004][FR-003][FR-022][FR-030]"""

    def montar(self, curso_nome):
        tcc, professor, orientador = tcc_apto(curso_nome)
        avaliador, suplente, coorientador = docente(curso_nome), docente(curso_nome), docente()
        externo = criar_membro_externo()
        vincular_coorientador(tcc, coorientador)
        sessao = agendar_sessao_de(
            tcc,
            orientador,
            {"primeiro_avaliador": avaliador, "segundo_avaliador": externo, "suplente": suplente},
            data=(timezone.now() + timedelta(days=10)).date(),
        )
        coordenador = criar_coordenador()
        perfis = {
            "aluno": ativo(tcc.tcc_alu.alu),
            "orientador": orientador,
            "professor": professor,
            "avaliador": avaliador,
            "membro externo": externo,
            "suplente": suplente,
            "coorientador": coorientador,
            "coordenador": coordenador,
            "secretaria do curso": criar_secretaria(curso=curso(curso_nome)),
            "secretaria de outro curso": criar_secretaria(),
            "outro docente": docente(curso_nome),
        }
        return sessao, perfis

    def conferir(self, sessao, perfis, permitidos):
        for perfil, usuario in perfis.items():
            self.client.force_login(usuario)
            for rota in ROTAS:
                url = reverse(f"defesa:{rota}", args=[sessao.pk])
                esperado = 200 if perfil in permitidos[rota] else 403
                with self.subTest(perfil=perfil, rota=rota):
                    self.assertEqual(self.client.get(url).status_code, esperado)

    def test_engenharia_de_computacao(self):
        sessao, perfis = self.montar(EC)
        quem_ve = {
            "aluno",
            "orientador",
            "professor",
            "avaliador",
            "membro externo",
            "suplente",
            "secretaria do curso",
        }
        self.conferir(
            sessao,
            perfis,
            {
                "sessao": quem_ve,
                "historico": quem_ve,
                "alterar_banca": {"orientador"},
                "reagendar": {"orientador", "secretaria do curso"},
                "cancelar": {"orientador", "secretaria do curso"},
            },
        )

    def test_sistemas_de_informacao(self):
        sessao, perfis = self.montar(SI)
        quem_ve = {
            "aluno",
            "orientador",
            "professor",
            "avaliador",
            "membro externo",
            "suplente",
            "secretaria do curso",
        }
        self.conferir(
            sessao,
            perfis,
            {
                "sessao": quem_ve,
                "historico": quem_ve,
                "alterar_banca": {"professor"},
                "reagendar": {"professor", "secretaria do curso"},
                "cancelar": {"professor", "secretaria do curso"},
            },
        )

    def test_acionar_suplente_so_o_orientador_em_andamento(self):
        for curso_nome in (EC, SI):
            sessao, perfis = self.montar(curso_nome)
            url = reverse("defesa:acionar_suplente", args=[sessao.pk])
            self.client.force_login(perfis["orientador"])
            with self.subTest(curso=curso_nome, status="Agendada"):
                self.assertEqual(self.client.get(url).status_code, 403)
            avancar_para(sessao, StatusSessao.EM_ANDAMENTO)
            for perfil, usuario in perfis.items():
                self.client.force_login(usuario)
                with self.subTest(curso=curso_nome, perfil=perfil):
                    esperado = 200 if perfil == "orientador" else 403
                    self.assertEqual(self.client.get(url).status_code, esperado)

    def test_sessao_inexistente_da_404_antes_da_permissao(self):
        self.client.force_login(docente())
        for rota in (*ROTAS, "acionar_suplente"):
            with self.subTest(rota=rota):
                url = reverse(f"defesa:{rota}", args=[999999])
                self.assertEqual(self.client.get(url).status_code, 404)


class TestePermissoesDoAgendamento(TesteTurmas):
    """Agendar e aba Defesas da turma pelo endereço direto. [SC-004][FR-003][FR-006]"""

    def test_agendar_so_para_docente(self):
        tcc, _professor, _orientador = tcc_apto()
        for usuario in (ativo(tcc.tcc_alu.alu), criar_secretaria(curso=curso(EC))):
            self.client.force_login(usuario)
            with self.subTest(usuario=usuario.usu_nome):
                self.assertEqual(self.client.get(reverse("defesa:agendar")).status_code, 403)

    def test_aba_defesas_de_turma_alheia(self):
        tcc, professor, orientador = tcc_apto()
        url = reverse("defesa:turma_defesas", args=[tcc.tcc_tur_id])
        for usuario in (orientador, docente(), criar_secretaria(curso=curso(EC))):
            self.client.force_login(usuario)
            with self.subTest(usuario=usuario.usu_nome):
                self.assertEqual(self.client.get(url).status_code, 403)
        self.client.force_login(professor)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_tcc_de_outro_orientador_pelo_endereco_direto(self):
        tcc, _professor, _orientador = tcc_apto()
        self.client.force_login(docente())
        resposta = self.client.get(f"{reverse('defesa:agendar')}?tcc={tcc.pk}")
        self.assertContains(resposta, "Este TCC não pode ser agendado por você", status_code=403)
