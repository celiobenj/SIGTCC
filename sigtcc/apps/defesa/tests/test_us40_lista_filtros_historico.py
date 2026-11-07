"""US-40 Ver a lista de sessões de defesa e filtrar por período: um teste por cenário de aceite
(User Story 5 da spec 007), com a aplicação do filtro de Curso da US-39. O cenário 13 (histórico
pela tela de orientandos) fica fora do escopo de teste desta spec (Edge Cases).

O relógio fica parado numa quarta-feira (18/11/2026), com o login no mesmo relógio, para os
atalhos de período não dependerem do dia em que os testes rodam.

[US-40][US-39][RBN-DEF-01.4][RBN-DEF-01.5][RBN-DEF-01.6][FR-024 a FR-030] (tasks T053)
"""

from datetime import date, datetime, time
from unittest import mock

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from sigtcc.apps.cadastro.choices import StatusConta
from sigtcc.apps.cadastro.models import Coordenadores, Turmas
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_coordenador, criar_secretaria
from sigtcc.apps.cadastro.tests.apoio_orientacao import vincular_coorientador
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, LC, SI, TesteTurmas, curso
from sigtcc.apps.defesa import services_defesa
from sigtcc.apps.defesa.choices import FormatoSessao, PapelBanca, StatusSessao
from sigtcc.apps.defesa.models import BancaDefesa
from sigtcc.apps.defesa.tests.apoio_defesa import (
    agendar_sessao_de,
    avancar_para,
    docente,
    tcc_apto,
)

AGORA = datetime(2026, 11, 18, 8, 0)  # quarta-feira
LISTA = reverse("defesa:defesas")
VAZIO = "Nenhuma sessão de defesa encontrada para o período e filtros selecionados"


class TesteDefesasBase(TesteTurmas):
    """Relógio parado em AGORA e sessões em datas conhecidas."""

    def setUp(self):
        super().setUp()
        relogio = mock.patch("django.utils.timezone.now", return_value=AGORA)
        relogio.start()
        self.addCleanup(relogio.stop)

    def entrar(self, usuario):
        if usuario.usu_status != StatusConta.ATIVA:
            usuario.usu_status = StatusConta.ATIVA
            usuario.save(update_fields=["usu_status"])
        self.client.force_login(usuario)

    def sessao(self, curso_nome=EC, dia=date(2026, 11, 20), hora=time(14, 0), **kwargs):
        tcc, professor, orientador = tcc_apto(curso_nome, **kwargs)
        banca = {
            "primeiro_avaliador": docente(curso_nome),
            "segundo_avaliador": docente(curso_nome),
        }
        sessao = agendar_sessao_de(tcc, orientador, banca, data=dia, h_inicio=hora)
        return sessao, professor, orientador, banca

    def listadas(self, usuario, **filtros):
        self.entrar(usuario)
        resposta = self.client.get(LISTA, filtros)
        self.assertEqual(resposta.status_code, 200)
        return resposta, list(resposta.context["sessoes"])


class TesteListaEVisibilidade(TesteDefesasBase):
    """Cenários 1 a 5, 12, 16 e 17. [US-40][US-39][RBN-DEF-01.4][FR-024][FR-027][FR-028]"""

    def test_cenario_1_periodo_letivo_em_ordem_cronologica(self):
        segunda, _p, ori, _b = self.sessao(dia=date(2026, 11, 25))
        primeira, *_ = self.sessao(dia=date(2026, 11, 20))
        fora, *_ = self.sessao()
        Turmas.objects.filter(pk=fora.def_tcc.tcc_tur_id).update(tur_ano=2026, tur_semestre=1)
        secretaria = criar_secretaria(curso=curso(EC))
        resposta, sessoes = self.listadas(secretaria)
        self.assertEqual(sessoes, [primeira, segunda])
        for coluna in (
            "Data",
            "Horário",
            "Aluno",
            "Título",
            "Orientador",
            "Local ou Link",
            "Status",
        ):
            self.assertContains(resposta, f"<th>{coluna}</th>", html=True)
        self.assertContains(resposta, "14:00–15:00")
        self.assertContains(resposta, ori.usu_nome)

    def test_cenario_2_aluno_ve_so_a_propria(self):
        minha, *_ = self.sessao()
        self.sessao()
        _resposta, sessoes = self.listadas(minha.def_tcc.tcc_alu.alu)
        self.assertEqual(sessoes, [minha])

    def test_cenario_3_avaliador_so_onde_consta(self):
        sessao, _p, _o, banca = self.sessao()
        self.sessao()
        _resposta, sessoes = self.listadas(banca["primeiro_avaliador"])
        self.assertEqual(sessoes, [sessao])

    def test_coorientador_com_convite_aceito_tambem_ve(self):
        sessao, *_ = self.sessao()
        coorientador = docente()
        vincular_coorientador(sessao.def_tcc, coorientador)
        _resposta, sessoes = self.listadas(coorientador)
        self.assertEqual(sessoes, [sessao])

    def test_cenario_4_professor_ve_a_turma(self):
        professor = docente(SI)
        a, *_ = self.sessao(SI, professor=professor)
        b, *_ = self.sessao(SI, professor=professor, dia=date(2026, 11, 21))
        self.sessao(SI)
        _resposta, sessoes = self.listadas(professor)
        self.assertEqual(sessoes, [a, b])

    def test_cenario_5_secretaria_ve_o_curso_do_filtro(self):
        da_si, *_ = self.sessao(SI)
        self.sessao(EC)
        resposta, sessoes = self.listadas(criar_secretaria(curso=curso(SI)))
        self.assertEqual(sessoes, [da_si])
        self.assertContains(resposta, 'name="curso"')

    def test_cenario_12_coordenador_escolhe_todos(self):
        coordenador = criar_coordenador()
        Coordenadores.objects.filter(cor_doc_id=coordenador.pk).update(cor_cur=curso(LC))
        sessoes_criadas = [
            self.sessao(nome, dia=date(2026, 11, 20 + i))[0] for i, nome in enumerate((EC, SI, LC))
        ]
        _resposta, do_curso = self.listadas(coordenador)
        self.assertEqual(do_curso, [sessoes_criadas[2]])
        _resposta, todas = self.listadas(coordenador, curso="todos")
        self.assertEqual(todas, sessoes_criadas)

    def test_filtro_de_curso_nao_aparece_para_aluno_e_docente(self):
        sessao, professor, _o, _b = self.sessao()
        for usuario in (sessao.def_tcc.tcc_alu.alu, professor):
            with self.subTest(usuario=usuario.usu_nome):
                resposta, _s = self.listadas(usuario)
                self.assertNotContains(resposta, 'name="curso"')

    def test_cenario_16_sem_login(self):
        self.client.logout()
        self.assertRedirects(
            self.client.get(LISTA),
            f"{reverse('cadastro:entrar')}?next={LISTA}",
            fetch_redirect_response=False,
        )

    def test_cenario_17_nenhuma_sessao(self):
        resposta, sessoes = self.listadas(docente())
        self.assertEqual(sessoes, [])
        self.assertContains(resposta, VAZIO)
        self.assertContains(resposta, "<th>Status</th>", html=True)


class TesteFiltros(TesteDefesasBase):
    """Cenários 6 a 10, 18 e 19. [US-40][RBN-DEF-01.5][FR-025][FR-026]"""

    def setUp(self):
        super().setUp()
        self.secretaria = criar_secretaria(curso=curso(EC))
        self.por_dia = {
            dia: self.sessao(dia=date(2026, *dia))[0]
            for dia in ((11, 16), (11, 22), (11, 23), (11, 30), (12, 1), (12, 18), (12, 19))
        }

    def dias(self, **filtros):
        _resposta, sessoes = self.listadas(self.secretaria, **filtros)
        return [(s.def_data.month, s.def_data.day) for s in sessoes]

    def test_cenario_6_esta_semana(self):
        self.assertEqual(self.dias(atalho="esta_semana"), [(11, 16), (11, 22)])

    def test_cenario_7_este_mes(self):
        self.assertEqual(self.dias(atalho="este_mes"), [(11, 16), (11, 22), (11, 23), (11, 30)])

    def test_cenario_8_proximos_30_dias(self):
        self.assertEqual(
            self.dias(atalho="proximos_30_dias"), [(11, 22), (11, 23), (11, 30), (12, 1), (12, 18)]
        )

    def test_cenario_9_intervalo_manual(self):
        dias = self.dias(data_inicial="10/11/2026", data_final="25/11/2026")
        self.assertEqual(dias, [(11, 16), (11, 22), (11, 23)])

    def test_cenario_10_filtro_de_status(self):
        avancar_para(self.por_dia[(11, 16)], StatusSessao.REALIZADA)
        self.assertEqual(self.dias(status=StatusSessao.REALIZADA), [(11, 16)])

    def test_cenario_18_intervalo_invertido(self):
        resposta, sessoes = self.listadas(
            self.secretaria, data_inicial="25/11/2026", data_final="10/11/2026"
        )
        self.assertContains(resposta, "A data inicial não pode ser superior à data final")
        self.assertEqual(len(sessoes), 7)  # a lista do Período Letivo, sem o filtro

    def test_cenario_19_data_invalida(self):
        resposta, _s = self.listadas(
            self.secretaria, data_inicial="31/02/2026", data_final="10/03/2026"
        )
        self.assertFormError(
            resposta.context["form"],
            "data_inicial",
            "Informe uma data válida no formato DD/MM/AAAA",
        )

    def test_trocar_o_curso_nao_faz_uma_consulta_por_linha(self):
        # RBN-CAD-14.1 (até 2 segundos): o número de consultas não cresce com as linhas.
        self.entrar(self.secretaria)

        def consultas():
            with CaptureQueriesContext(connection) as capturadas:
                resposta = self.client.get(LISTA, {"curso": "todos"})
            return len(capturadas), len(resposta.context["sessoes"])

        consultas()  # a primeira depois do login grava a sessão de acesso
        antes, linhas = consultas()
        for i in range(5):
            self.sessao(SI, dia=date(2026, 11, 24 + i))
        depois, mais_linhas = consultas()
        self.assertEqual((linhas, mais_linhas), (7, 12))
        self.assertEqual(antes, depois)


class TesteJanelaEHistorico(TesteDefesasBase):
    """Cenários 11, 14, 15 e 20: janela da sessão e Histórico da defesa.
    [US-40][RBN-DEF-01.6][FR-029][FR-030]
    """

    def setUp(self):
        super().setUp()
        self.sessao_, self.professor, self.orientador, self.banca = self.sessao()
        self.url_sessao = reverse("defesa:sessao", args=[self.sessao_.pk])
        self.url_historico = reverse("defesa:historico", args=[self.sessao_.pk])

    def test_cenario_11_historico_com_data_hora_e_responsavel(self):
        self.entrar(self.orientador)
        pagina = self.client.get(self.url_sessao)
        self.assertContains(pagina, self.url_historico)
        resposta = self.client.get(self.url_historico)
        self.assertContains(resposta, "Agendamento")
        self.assertContains(resposta, self.orientador.usu_nome)
        self.assertContains(resposta, f'href="{LISTA}"')  # Fechar volta à lista

    def test_cenario_14_reagendada_e_depois_cancelada(self):
        services_defesa.reagendar(
            self.orientador,
            self.sessao_.pk,
            {
                "data": date(2026, 11, 27),
                "h_inicio": time(9, 0),
                "formato": FormatoSessao.REMOTA,
                "link": "https://meet.example.org/a",
            },
            "Banca em viagem",
        )
        services_defesa.cancelar(self.orientador, self.sessao_.pk, "Aluno adoeceu")
        self.entrar(self.orientador)
        resposta = self.client.get(self.url_historico)
        for texto in (
            "Reagendamento",
            "Horário anterior: 20/11/2026 às 14:00; novo horário: 27/11/2026 às 09:00",
            "Banca em viagem",
            "Cancelamento",
            "Aluno adoeceu",
        ):
            self.assertContains(resposta, texto)

    def test_cenario_15_alteracao_da_banca_e_suplente(self):
        novo = docente()
        banca = {
            PapelBanca.PRIMEIRO_AVALIADOR: self.banca["primeiro_avaliador"],
            PapelBanca.SEGUNDO_AVALIADOR: novo,
        }
        services_defesa.alterar_banca(self.orientador, self.sessao_.pk, banca, "Licença médica")
        self.entrar(self.orientador)
        resposta = self.client.get(self.url_historico)
        self.assertContains(resposta, "Alteração da Banca")
        self.assertContains(resposta, f"Saiu: {self.banca['segundo_avaliador'].usu_nome}")
        self.assertContains(resposta, f"Entrou: {novo.usu_nome}")
        self.assertContains(resposta, "Licença médica")

    def test_historico_reune_as_sessoes_canceladas_do_tcc(self):
        avancar_para(self.sessao_, StatusSessao.CANCELADA, self.orientador)
        nova = agendar_sessao_de(
            self.sessao_.def_tcc,
            self.orientador,
            {"primeiro_avaliador": docente(), "segundo_avaliador": docente()},
            data=date(2026, 12, 4),
        )
        self.entrar(self.orientador)
        resposta = self.client.get(reverse("defesa:historico", args=[nova.pk]))
        self.assertContains(resposta, "20/11/2026")
        self.assertContains(resposta, "04/12/2026")

    def test_inicio_automatico_aparece_como_sistema(self):
        avancar_para(self.sessao_, StatusSessao.EM_ANDAMENTO)
        self.entrar(self.orientador)
        self.assertContains(self.client.get(self.url_historico), "Sistema")

    def test_cenario_20_quem_nao_pode_ver_a_sessao(self):
        coorientador = docente()
        vincular_coorientador(self.sessao_.def_tcc, coorientador)
        coordenador = criar_coordenador()
        for usuario in (docente(), coorientador, coordenador, criar_secretaria(curso=curso(SI))):
            with self.subTest(usuario=usuario.usu_nome):
                self.entrar(usuario)
                for url in (self.url_sessao, self.url_historico):
                    self.assertContains(
                        self.client.get(url),
                        "Você não tem permissão para visualizar esta defesa",
                        status_code=403,
                    )

    def test_quem_pode_ver_a_sessao(self):
        suplente = docente()
        BancaDefesa.objects.create(
            ban_def=self.sessao_, ban_usu=suplente, ban_papel=PapelBanca.SUPLENTE
        )
        for usuario in (
            self.orientador,
            self.banca["primeiro_avaliador"],
            suplente,
            self.professor,
            criar_secretaria(curso=curso(EC)),
            self.sessao_.def_tcc.tcc_alu.alu,
        ):
            with self.subTest(usuario=usuario.usu_nome):
                self.entrar(usuario)
                self.assertEqual(self.client.get(self.url_sessao).status_code, 200)
                self.assertEqual(self.client.get(self.url_historico).status_code, 200)

    def test_linha_da_lista_so_abre_para_quem_pode_ver(self):
        coorientador = docente()
        vincular_coorientador(self.sessao_.def_tcc, coorientador)
        self.entrar(coorientador)
        self.assertNotContains(self.client.get(LISTA), self.url_sessao)
        self.entrar(self.orientador)
        self.assertContains(self.client.get(LISTA), self.url_sessao)


class TesteFiltroDePeriodoComAnoSemestre(TesteTurmas):
    """Spec 010 (IC-03): outro período letivo, por parâmetro opcional; sem ele, nada muda.
    [US-31][US-40][RBN-DEF-01.5][research R2]
    """

    def test_ano_semestre_escolhe_outro_periodo_letivo(self):
        """O par informado substitui o período atual."""
        filtro = services_defesa.filtro_de_periodo(
            "periodo_letivo", prefixo="ban_def__", ano_semestre=(2025, 1)
        )
        self.assertIn(("ban_def__def_tcc__tcc_tur__tur_ano", 2025), filtro.children)
        self.assertIn(("ban_def__def_tcc__tcc_tur__tur_semestre", 1), filtro.children)

    def test_sem_o_parametro_vale_o_periodo_atual(self):
        """Comportamento da feat-07."""
        with mock.patch.object(
            services_defesa, "periodo_letivo_atual", return_value=(2026, 2)
        ) as atual:
            filtro = services_defesa.filtro_de_periodo("periodo_letivo")
        atual.assert_called_once()
        self.assertIn(("def_tcc__tcc_tur__tur_ano", 2026), filtro.children)

    def test_intervalo_do_atalho(self):
        """Fonte única das datas dos atalhos."""
        hoje = date(2026, 11, 18)
        casos = {
            "esta_semana": (date(2026, 11, 16), date(2026, 11, 22)),
            "este_mes": (date(2026, 11, 1), date(2026, 11, 30)),
            "proximos_30_dias": (hoje, date(2026, 12, 18)),
        }
        for atalho, esperado in casos.items():
            with self.subTest(atalho=atalho):
                self.assertEqual(services_defesa.intervalo_do_atalho(atalho, hoje), esperado)

    def test_atalho_desconhecido(self):
        """Mesma exceção de antes da extração."""
        with self.assertRaises(ValueError):
            services_defesa.filtro_de_periodo("xyz")
