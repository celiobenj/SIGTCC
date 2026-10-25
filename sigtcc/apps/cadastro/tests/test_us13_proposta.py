"""Testes de aceite da US-13: registrar a Proposta, cadastrar os dados do TCC e alterar o tema
(spec 005, Phase 3, T010).

Os 7 cenários de aceite do spec.md (ver seção "User Story 1"), mais os cenários de exceção das
US originais (campo obrigatório, limite de caracteres, link inválido, nenhuma Palavra-Chave,
sexta Palavra-Chave inexistente, Status Desistente/Reprovado/Jubilado, turma arquivada) e o
cenário de Palavra-Chave repetida (MF-03, Clarifications).

[US-13][RBN-CAD-07.1][RBN-CAD-08.1][RBN-CAD-08.2][FR-001 a FR-007a]
"""

from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    ModalidadeTCC,
    OrigemOrientacao,
    StatusConta,
    StatusOrientacao,
    StatusTCC,
    StatusTurma,
    TipoEntrega,
)
from sigtcc.apps.cadastro.models import (
    AreasInteresse,
    EntregasMarcos,
    Notificacoes,
    Orientacoes,
    PalavrasChaveTCC,
)
from sigtcc.apps.cadastro.tests.apoio_acesso import avancar_relogio, criar_docente_ativo
from sigtcc.apps.cadastro.tests.apoio_tcc import cadastrar_entrega
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    TesteTurmas,
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)

DADOS_PROPOSTA = {
    "titulo": "Sistema de Gestão de TCC",
    "subtitulo": "",
    "resumo": "Resumo do trabalho de conclusão de curso.",
    "modalidade": ModalidadeTCC.MONOGRAFIA,
    "link": "",
}


class MeuTCCTestBase(TesteTurmas):
    """Turma de TCC 1 com um aluno vinculado; login do aluno (self.client)."""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC)
        self.aluno = matricular_aluno(
            self.turma, status_tcc=StatusTCC.SEM_PROPOSTA, status_conta=StatusConta.ATIVA
        )
        self.client.force_login(self.aluno.alu)

    def url(self, turma=None):
        return reverse("cadastro:meu_tcc", args=[(turma or self.turma).pk])

    def tcc(self):
        return tcc_de(self.aluno, self.turma)


class SalvarPropostaTest(MeuTCCTestBase):
    """Cenário 1: Proposta salva, Status Sem Proposta → Em Andamento. [US-13][FR-002]"""

    def test_cenario1_proposta_salva(self):
        resposta = self.client.post(
            self.url(), {"acao": "salvar_proposta", **DADOS_PROPOSTA}, follow=True
        )
        self.assertContains(resposta, mensagens.PROPOSTA_SALVA)
        tcc = self.tcc()
        self.assertEqual(tcc.tcc_status, StatusTCC.EM_ANDAMENTO)
        self.assertEqual(tcc.tcc_titulo, DADOS_PROPOSTA["titulo"])
        # Botão "Salvar Proposta" escondido; Área de Interesse e Palavras-Chave liberadas.
        self.assertNotContains(resposta, "Salvar Proposta")
        self.assertContains(resposta, "Área de Interesse")

    def test_cenario6_campo_obrigatorio(self):
        """E2: Título em branco não salva, mostra "Campo obrigatório". [FR-007]"""
        dados = {**DADOS_PROPOSTA, "titulo": ""}
        resposta = self.client.post(self.url(), {"acao": "salvar_proposta", **dados})
        self.assertContains(resposta, mensagens.M14_CAMPO_OBRIGATORIO)
        self.assertEqual(self.tcc().tcc_status, StatusTCC.SEM_PROPOSTA)

    def test_cenario6_limite_caracteres_titulo(self):
        """E3: Título com 251 caracteres não salva. [FR-007]"""
        dados = {**DADOS_PROPOSTA, "titulo": "A" * 251}
        resposta = self.client.post(self.url(), {"acao": "salvar_proposta", **dados})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(self.tcc().tcc_status, StatusTCC.SEM_PROPOSTA)

    def test_cenario6_link_invalido(self):
        """E4: link sem https:// não salva, mostra a mensagem exata. [FR-007]"""
        dados = {**DADOS_PROPOSTA, "link": "www.exemplo.com/proposta.pdf"}
        resposta = self.client.post(self.url(), {"acao": "salvar_proposta", **dados})
        self.assertContains(resposta, mensagens.LINK_HTTPS_500)
        self.assertEqual(self.tcc().tcc_status, StatusTCC.SEM_PROPOSTA)

    def test_cenario3_entrega_proposta_cumprida_no_prazo(self):
        """Cenário 3 (dentro do prazo): entrega do tipo Proposta vira "Entregue". [FR-003]"""
        with avancar_relogio(dias=10) as data_limite:
            entrega = cadastrar_entrega(
                self.turma, tipo=TipoEntrega.PROPOSTA, data_limite=data_limite
            )
        self.client.post(self.url(), {"acao": "salvar_proposta", **DADOS_PROPOSTA})
        registro = EntregasMarcos.objects.get(ent_tma=entrega, ent_alu=self.aluno)
        self.assertEqual(registro.ent_status, "Entregue")

    def test_cenario3_entrega_proposta_cumprida_com_atraso(self):
        """Cenário 3 (depois do prazo): entrega do tipo Proposta vira "Entregue com Atraso".

        [FR-003]
        """
        with avancar_relogio(dias=2) as data_limite:
            entrega = cadastrar_entrega(
                self.turma, tipo=TipoEntrega.PROPOSTA, data_limite=data_limite
            )
        with avancar_relogio(dias=5):
            # Reloga dentro do salto de tempo: a sessão expira em 1h reais (SESSION_COOKIE_AGE),
            # então o avanço de dias por avancar_relogio precisa de um novo login "no futuro".
            self.client.force_login(self.aluno.alu)
            self.client.post(self.url(), {"acao": "salvar_proposta", **DADOS_PROPOSTA})
        registro = EntregasMarcos.objects.get(ent_tma=entrega, ent_alu=self.aluno)
        self.assertEqual(registro.ent_status, "Entregue com Atraso")


class SalvarAlteracoesTest(MeuTCCTestBase):
    """Cenários 2, 4 e 7: Área de Interesse, Palavras-Chave e mudança de tema.

    [US-13][FR-004][FR-005]
    """

    def setUp(self):
        super().setUp()
        # Proposta já salva (Status "Em Andamento"), direto no banco (sem passar pelo serviço).
        tcc = self.tcc()
        tcc.tcc_titulo = DADOS_PROPOSTA["titulo"]
        tcc.tcc_resumo = DADOS_PROPOSTA["resumo"]
        tcc.tcc_modalidade = DADOS_PROPOSTA["modalidade"]
        tcc.tcc_status = StatusTCC.EM_ANDAMENTO
        tcc.save()
        self.area = AreasInteresse.objects.first()

    def _dados(self, **extra):
        dados = {
            **DADOS_PROPOSTA,
            "area_interesse": self.area.pk,
            "palavra_chave_1": "IoT",
            "palavra_chave_2": "",
            "palavra_chave_3": "",
            "palavra_chave_4": "",
            "palavra_chave_5": "",
        }
        dados.update(extra)
        return dados

    def test_cenario2_area_e_palavras_chave_salvas(self):
        resposta = self.client.post(
            self.url(), {"acao": "salvar_alteracoes", **self._dados()}, follow=True
        )
        self.assertContains(resposta, mensagens.ALTERACOES_SALVAS)
        tcc = self.tcc()
        self.assertEqual(tcc.tcc_ari_id, self.area.pk)
        self.assertEqual(
            list(
                PalavrasChaveTCC.objects.filter(pal_tcc=tcc).values_list("pal_palavra", flat=True)
            ),
            ["IoT"],
        )

    def test_cenario4_mudanca_de_tema_com_orientador_notifica(self):
        orientador = criar_docente_ativo()
        Orientacoes.objects.create(
            ori_tcc=self.tcc(),
            ori_doc=orientador.docentes,
            ori_origem=OrigemOrientacao.PEDIDO_ACEITO,
            ori_status=StatusOrientacao.ATIVA,
            ori_data_inicio=timezone.now(),
        )
        dados = self._dados(titulo="Novo Título do Trabalho")
        self.client.post(self.url(), {"acao": "salvar_alteracoes", **dados}, follow=True)
        self.assertEqual(self.tcc().tcc_titulo, "Novo Título do Trabalho")
        self.assertTrue(Notificacoes.objects.filter(not_usu_id=orientador.pk).exists())

    def test_cenario4_mudanca_de_tema_sem_orientador_nao_notifica(self):
        dados = self._dados(titulo="Outro Título do Trabalho")
        self.client.post(self.url(), {"acao": "salvar_alteracoes", **dados}, follow=True)
        self.assertEqual(self.tcc().tcc_titulo, "Outro Título do Trabalho")
        self.assertFalse(Notificacoes.objects.exists())

    def test_cenario6_nenhuma_palavra_chave(self):
        """E5: nenhuma caixa de Palavra-Chave preenchida. [FR-007]"""
        dados = self._dados(palavra_chave_1="")
        resposta = self.client.post(self.url(), {"acao": "salvar_alteracoes", **dados})
        self.assertContains(resposta, mensagens.INFORME_PALAVRAS_CHAVE)
        self.assertFalse(PalavrasChaveTCC.objects.filter(pal_tcc=self.tcc()).exists())

    def test_sexta_palavra_chave_nao_existe(self):
        """E6: o formulário só tem 5 caixas de Palavra-Chave. [FR-007]"""
        resposta = self.client.get(self.url())
        self.assertNotContains(resposta, "palavra_chave_6")

    def test_cenario7_palavra_chave_repetida(self):
        """MF-03 (Clarifications): mesma Palavra-Chave em duas caixas não salva. [FR-007]"""
        dados = self._dados(palavra_chave_1="IoT", palavra_chave_2="IoT")
        resposta = self.client.post(self.url(), {"acao": "salvar_alteracoes", **dados})
        self.assertContains(resposta, mensagens.MF03_PALAVRA_CHAVE_REPETIDA)
        self.assertFalse(PalavrasChaveTCC.objects.filter(pal_tcc=self.tcc()).exists())


class SomenteLeituraTest(MeuTCCTestBase):
    """Cenário 5 e exceções: Status fora de Sem Proposta/Em Andamento, participação encerrada ou
    turma arquivada → campos somente leitura, sem botões de salvar. [US-13][FR-006]
    """

    def test_cenario5_bloqueio_apto_para_defesa(self):
        aluno = matricular_aluno(
            self.turma, status_tcc=StatusTCC.APTO_PARA_DEFESA, status_conta=StatusConta.ATIVA
        )
        self.client.force_login(aluno.alu)
        resposta = self.client.get(self.url())
        self.assertNotContains(resposta, "Salvar Proposta")
        self.assertNotContains(resposta, "Salvar alterações")

    def test_cenario5_bloqueio_desistente(self):
        aluno = matricular_aluno(
            self.turma, status_tcc=StatusTCC.DESISTENTE, status_conta=StatusConta.ATIVA
        )
        self.client.force_login(aluno.alu)
        resposta = self.client.get(self.url())
        self.assertNotContains(resposta, "Salvar Proposta")
        self.assertNotContains(resposta, "Salvar alterações")

    def test_cenario5_bloqueio_reprovado(self):
        aluno = matricular_aluno(
            self.turma, status_tcc=StatusTCC.REPROVADO, status_conta=StatusConta.ATIVA
        )
        self.client.force_login(aluno.alu)
        resposta = self.client.get(self.url())
        self.assertNotContains(resposta, "Salvar Proposta")
        self.assertNotContains(resposta, "Salvar alterações")

    def test_cenario5_bloqueio_jubilado(self):
        aluno = matricular_aluno(
            self.turma, status_tcc=StatusTCC.JUBILADO, status_conta=StatusConta.ATIVA
        )
        self.client.force_login(aluno.alu)
        resposta = self.client.get(self.url())
        self.assertNotContains(resposta, "Salvar Proposta")
        self.assertNotContains(resposta, "Salvar alterações")

    def test_cenario5_bloqueio_turma_arquivada(self):
        turma = criar_turma_de(
            self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC, status=StatusTurma.ATIVA
        )
        aluno = matricular_aluno(
            turma, status_tcc=StatusTCC.SEM_PROPOSTA, status_conta=StatusConta.ATIVA
        )
        turma.tur_status = StatusTurma.ARQUIVADA
        turma.save(update_fields=["tur_status"])
        self.client.force_login(aluno.alu)
        resposta = self.client.get(self.url(turma))
        self.assertNotContains(resposta, "Salvar Proposta")

    def test_proposta_nao_salva_fora_do_status_sem_proposta(self):
        """Defensivo: POST direto com o TCC já "Em Andamento" não refaz a Proposta (FR-002)."""
        tcc = self.tcc()
        tcc.tcc_titulo = DADOS_PROPOSTA["titulo"]
        tcc.tcc_resumo = DADOS_PROPOSTA["resumo"]
        tcc.tcc_modalidade = DADOS_PROPOSTA["modalidade"]
        tcc.tcc_status = StatusTCC.EM_ANDAMENTO
        tcc.save()
        self.client.post(
            self.url(), {"acao": "salvar_proposta", **DADOS_PROPOSTA, "titulo": "Outro"}
        )
        self.assertEqual(self.tcc().tcc_titulo, DADOS_PROPOSTA["titulo"])


class AcessoMeuTCCTest(MeuTCCTestBase):
    """Sem IDOR: um aluno não abre o Meu TCC de outro (vinculo_na_turma). [contracts/rotas.md]"""

    def test_aluno_sem_vinculo_na_turma_recebe_404(self):
        outro_aluno = matricular_aluno(
            criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_1, curso_nome=EC),
            status_conta=StatusConta.ATIVA,
        )
        self.client.force_login(outro_aluno.alu)
        resposta = self.client.get(self.url())
        self.assertEqual(resposta.status_code, 404)


class CorrecoesDaRevisaoUS13Test(MeuTCCTestBase):
    """Correções da revisão de 2026-10-23 (Phase 12, T042 e T043): aviso ao Orientador também por
    Área de Interesse e Palavras-Chave (US-13, fluxo A; FR-005), conferência de novo do Status e
    da turma no serviço (SC-004; research C4), turma arquivada no salvamento sem erro 500 e o
    contador de caracteres do Resumo (FR-001).

    [US-13][RBN-CAD-08.2][FR-001][FR-005][FR-006][SC-004][Q-83]
    """

    _dados = SalvarAlteracoesTest._dados

    def setUp(self):
        super().setUp()
        # Proposta já salva (Status "Em Andamento"), com Área e Palavra-Chave gravadas, para
        # mudar um campo de cada vez.
        tcc = self.tcc()
        tcc.tcc_titulo = DADOS_PROPOSTA["titulo"]
        tcc.tcc_resumo = DADOS_PROPOSTA["resumo"]
        tcc.tcc_modalidade = DADOS_PROPOSTA["modalidade"]
        tcc.tcc_status = StatusTCC.EM_ANDAMENTO
        self.area = AreasInteresse.objects.first()
        tcc.tcc_ari = self.area
        tcc.save()
        PalavrasChaveTCC.objects.create(pal_tcc=tcc, pal_palavra="IoT")
        self.orientador = criar_docente_ativo()
        Orientacoes.objects.create(
            ori_tcc=tcc,
            ori_doc=self.orientador.docentes,
            ori_origem=OrigemOrientacao.PEDIDO_ACEITO,
            ori_status=StatusOrientacao.ATIVA,
            ori_data_inicio=timezone.now(),
        )

    def salvar(self, **extra):
        return self.client.post(
            self.url(), {"acao": "salvar_alteracoes", **self._dados(**extra)}, follow=True
        )

    def avisos_ao_orientador(self):
        return Notificacoes.objects.filter(not_usu_id=self.orientador.pk).count()

    def test_mudanca_so_da_area_de_interesse_notifica_o_orientador(self):
        outra_area = AreasInteresse.objects.exclude(pk=self.area.pk).first()
        self.salvar(area_interesse=outra_area.pk)
        self.assertEqual(self.tcc().tcc_ari_id, outra_area.pk)
        self.assertEqual(self.avisos_ao_orientador(), 1)

    def test_mudanca_so_das_palavras_chave_notifica_o_orientador(self):
        self.salvar(palavra_chave_2="Segurança")
        self.assertEqual(self.avisos_ao_orientador(), 1)

    def test_salvar_sem_mudanca_nao_notifica(self):
        self.salvar()
        self.assertEqual(self.avisos_ao_orientador(), 0)

    def test_servico_confere_de_novo_o_status_depois_de_travar(self):
        """SC-004: se o TCC deixou de estar "Em Andamento" (ex.: participação encerrada no meio
        da requisição), o serviço não grava nada."""
        from django.http import Http404

        from sigtcc.apps.cadastro import services_tcc

        desatualizado = self.tcc()
        tcc = self.tcc()
        tcc.tcc_status = StatusTCC.DESISTENTE
        tcc.save(update_fields=["tcc_status"])
        with self.assertRaises(Http404):
            services_tcc.salvar_alteracoes_tcc(
                desatualizado, {**DADOS_PROPOSTA, "titulo": "Título indevido", "palavras_chave": []}
            )
        self.assertEqual(self.tcc().tcc_titulo, DADOS_PROPOSTA["titulo"])

    def test_servico_recusa_turma_arquivada(self):
        from sigtcc.apps.cadastro import services_tcc
        from sigtcc.apps.cadastro.services_turmas import TurmaArquivada

        tcc = self.tcc()
        self.turma.tur_status = StatusTurma.ARQUIVADA
        self.turma.save(update_fields=["tur_status"])
        with self.assertRaises(TurmaArquivada):
            services_tcc.salvar_alteracoes_tcc(
                tcc, {**DADOS_PROPOSTA, "titulo": "Título indevido", "palavras_chave": ["IoT"]}
            )
        self.assertEqual(self.tcc().tcc_titulo, DADOS_PROPOSTA["titulo"])

    def test_turma_arquivada_no_meio_do_salvamento_mostra_a_mt25_sem_erro(self):
        """A tela abriu com a turma ativa e ela foi arquivada antes do POST chegar ao serviço."""
        from unittest import mock

        from sigtcc.apps.cadastro import services_tcc
        from sigtcc.apps.cadastro.services_turmas import TurmaArquivada

        with mock.patch.object(
            services_tcc, "salvar_alteracoes_tcc", side_effect=TurmaArquivada(self.turma)
        ):
            resposta = self.salvar(titulo="Título indevido")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.redirect_chain[-1][0], self.url())
        self.assertContains(resposta, mensagens.MT25_TURMA_ARQUIVADA)

    def test_resumo_tem_o_contador_de_caracteres_restantes(self):
        """FR-001 (US-13, passo 2 e E3): o Resumo leva o contador, ligado por data-contador."""
        resposta = self.client.get(self.url())
        self.assertContains(resposta, "data-contador")
        self.assertContains(resposta, "js/contador.js")
