"""Segurança e integridade da feature 004.

SC-006: exclusão de turma no log; exclusão, transferência e encerramento com autor, data e hora.
SC-005: nenhuma matrícula repetida na mesma turma nem segunda conta, na matrícula e na importação,
inclusive em duas importações do mesmo aluno abertas ao mesmo tempo. Upload acima de 2 MB recusado
e nenhum valor de célula do arquivo no log (B-3).

[SC-005][SC-006][B-3][US-07][US-08][US-09]
"""

import logging
from datetime import timedelta

from django.test import Client
from django.urls import reverse
from django.utils import timezone

from sigtcc.apps.cadastro import mensagens, services_turmas
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    GatilhoStatusTCC,
    StatusTCC,
    TipoEventoTurma,
)
from sigtcc.apps.cadastro.models import (
    Alunos,
    AlunosTurmas,
    HistoricoAlunosTurmas,
    HistoricoStatusTCC,
    Usuarios,
)
from sigtcc.apps.cadastro.tests.apoio_acesso import criar_docente_ativo
from sigtcc.apps.cadastro.tests.apoio_turmas import (
    EC,
    TesteTurmas,
    arquivo_csv,
    criar_turma_de,
    matricular_aluno,
    tcc_de,
)

MATRICULA = "2026555001"
NOME = "Valentina Cassiopeia Reis"


class _Coletor(logging.Handler):
    """Guarda todas as mensagens de log emitidas durante o teste."""

    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.textos = []

    def emit(self, record):
        self.textos.append(record.getMessage())


class AuditoriaTest(TesteTurmas):
    """SC-006: quem fez, quando e por quê. [SC-006]"""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.client.force_login(self.professor)

    def assert_agora(self, momento):
        self.assertLess(abs(timezone.now() - momento), timedelta(minutes=1))

    def test_exclusao_de_turma_no_log(self):
        turma = criar_turma_de(self.professor, identificador="SEG_T01")
        with self.assertLogs("sigtcc.acesso") as log:
            with self.captureOnCommitCallbacks(execute=True):
                self.client.post(reverse("cadastro:turma_excluir", args=[turma.pk]))
        self.assertIn(f"TURMA_EXCLUIDA | conta=- | autor={self.professor.pk}", log.output[0])

    def test_exclusao_do_aluno_com_autor_data_e_hora(self):
        turma = criar_turma_de(self.professor)
        aluno = matricular_aluno(turma)
        services_turmas.excluir_aluno(self.professor, turma.pk, aluno.pk, "Vínculo por engano")
        registro = HistoricoAlunosTurmas.objects.get(hat_alu=aluno)
        self.assertEqual(registro.hat_tipo_evento, TipoEventoTurma.EXCLUSAO)
        self.assertEqual(registro.hat_usu_id, self.professor.pk)
        self.assertEqual(registro.hat_justificativa, "Vínculo por engano")
        self.assert_agora(registro.hat_data_hora)

    def test_transferencia_com_autor_data_e_hora(self):
        origem = criar_turma_de(self.professor, descricao=DescricaoTurma.TCC_2, curso_nome=EC)
        destino = criar_turma_de(
            criar_docente_ativo(), descricao=DescricaoTurma.TCC_2, curso_nome=EC
        )
        aluno = matricular_aluno(origem, status_tcc=StatusTCC.EM_ANDAMENTO)
        services_turmas.transferir(self.professor, origem.pk, aluno.pk, destino.pk, "Troca")
        registro = HistoricoAlunosTurmas.objects.get(hat_alu=aluno)
        self.assertEqual(registro.hat_tipo_evento, TipoEventoTurma.TRANSFERENCIA)
        self.assertEqual(registro.hat_usu_id, self.professor.pk)
        self.assertEqual(registro.hat_tur_destino_id, destino.pk)
        self.assert_agora(registro.hat_data_hora)

    def test_encerramento_com_autor_data_e_hora(self):
        turma = criar_turma_de(self.professor)
        aluno = matricular_aluno(turma, status_tcc=StatusTCC.EM_ANDAMENTO)
        services_turmas.encerrar_participacao(
            self.professor, turma.pk, aluno.pk, StatusTCC.JUBILADO, "Prazo máximo excedido"
        )
        registro = HistoricoStatusTCC.objects.get(
            hst_tcc=tcc_de(aluno, turma),
            hst_gatilho=GatilhoStatusTCC.ENCERRAMENTO_DA_PARTICIPACAO,
        )
        self.assertEqual(registro.hst_usu_id, self.professor.pk)
        self.assert_agora(registro.hst_data_hora)


class UnicidadeTest(TesteTurmas):
    """SC-005: uma conta por matrícula e um vínculo por turma. [SC-005][RBN-CAD-05.1]"""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=EC)

    def contas(self):
        return Alunos.objects.filter(alu_matricula=MATRICULA).count()

    def vinculos(self, turma=None):
        return AlunosTurmas.objects.filter(
            mat_tur=turma or self.turma, mat_alu__alu_matricula=MATRICULA
        ).count()

    def cliente(self, professor=None):
        cliente = Client()
        cliente.force_login(professor or self.professor)
        return cliente

    def previa(self, cliente, turma=None):
        """Envia o arquivo com o aluno e devolve o token da prévia."""
        turma = turma or self.turma
        arquivo = arquivo_csv([(MATRICULA, NOME, "EST08MCPD")])
        cliente.post(reverse("cadastro:importar", args=[turma.pk]), {"arquivo": arquivo})
        return cliente.session["importacao"]["token"]

    def confirmar(self, cliente, token, turma=None):
        url = reverse("cadastro:importar_confirmar", args=[(turma or self.turma).pk])
        return cliente.post(url, {"token": token}, follow=True)

    def test_matricula_individual_repetida(self):
        cliente = self.cliente()
        url = reverse("cadastro:matricular", args=[self.turma.pk])
        dados = {"matricula": MATRICULA, "nome": NOME, "curso": "EST08MCPD"}
        cliente.post(url, dados)
        resposta = cliente.post(url, dados, follow=True)
        self.assertContains(resposta, mensagens.ALUNO_JA_NA_TURMA)
        self.assertEqual((self.contas(), self.vinculos()), (1, 1))

    def test_duas_importacoes_abertas_ao_mesmo_tempo_na_mesma_turma(self):
        """Duas abas com a prévia do mesmo aluno, confirmadas uma depois da outra."""
        primeira, segunda = self.cliente(), self.cliente()
        tokens = self.previa(primeira), self.previa(segunda)
        self.confirmar(primeira, tokens[0])
        resposta = self.confirmar(segunda, tokens[1])
        self.assertContains(resposta, mensagens.MT15_RESUMO_IMPORTACAO.format(n=0, r=1, c=0))
        self.assertEqual((self.contas(), self.vinculos()), (1, 1))
        self.assertEqual(Usuarios.objects.filter(usu_nome=NOME).count(), 1)

    def test_duas_importacoes_abertas_em_turmas_diferentes(self):
        """Dois professores importam o mesmo aluno novo: uma só conta."""
        outro = criar_docente_ativo()
        turma2 = criar_turma_de(outro, curso_nome=EC)
        primeira, segunda = self.cliente(), self.cliente(outro)
        tokens = self.previa(primeira), self.previa(segunda, turma2)
        self.confirmar(primeira, tokens[0])
        self.confirmar(segunda, tokens[1], turma2)
        self.assertEqual(self.contas(), 1)
        self.assertEqual(Usuarios.objects.filter(usu_nome=NOME).count(), 1)
        self.assertLessEqual(self.vinculos() + self.vinculos(turma2), 2)


class ArquivoTest(TesteTurmas):
    """B-3: limite de tamanho e nada do arquivo no log. [B-3][US-08][RBN-CAD-05.2]"""

    def setUp(self):
        super().setUp()
        self.professor = criar_docente_ativo()
        self.turma = criar_turma_de(self.professor, curso_nome=EC)
        self.client.force_login(self.professor)

    def test_upload_acima_de_2_mb_recusado(self):
        linhas = [(f"{2026700000 + n:010d}", "Aluno Grande", "EST08MCPD") for n in range(150)]
        arquivo = arquivo_csv(linhas)
        arquivo.file.seek(0, 2)
        arquivo.file.write(b"#" * (2 * 1024 * 1024))
        arquivo.size = arquivo.file.tell()
        arquivo.file.seek(0)
        resposta = self.client.post(
            reverse("cadastro:importar", args=[self.turma.pk]), {"arquivo": arquivo}
        )
        self.assertContains(resposta, mensagens.ARQUIVO_FORA_DO_MODELO)
        self.assertFalse(AlunosTurmas.objects.filter(mat_tur=self.turma).exists())

    def test_nenhum_valor_de_celula_no_log(self):
        coletor = _Coletor()
        raiz = logging.getLogger()
        nomes = ("", "sigtcc", "sigtcc.acesso", "django")
        niveis = {nome: logging.getLogger(nome).level for nome in nomes}
        for nome in nomes:
            logging.getLogger(nome).addHandler(coletor)
            logging.getLogger(nome).setLevel(logging.DEBUG)
        try:
            arquivo = arquivo_csv(
                [
                    (MATRICULA, NOME, "EST08MCPD"),
                    ("2026555002", "Zebedeu Quintiliano", "CURSOXYZ99"),
                    ("ERRO555", "Linha Invalida Teodora", "EST08MCPD"),
                ]
            )
            url = reverse("cadastro:importar", args=[self.turma.pk])
            self.client.post(url, {"arquivo": arquivo})
            token = self.client.session["importacao"]["token"]
            with self.captureOnCommitCallbacks(execute=True):
                self.client.post(
                    reverse("cadastro:importar_confirmar", args=[self.turma.pk]),
                    {"token": token},
                    follow=True,
                )
        finally:
            for nome in nomes:
                logging.getLogger(nome).removeHandler(coletor)
                logging.getLogger(nome).setLevel(niveis[nome])
        self.assertIs(raiz, logging.getLogger())
        texto = "\n".join(coletor.textos)
        for valor in (MATRICULA, NOME, "Zebedeu", "CURSOXYZ99", "ERRO555", "Teodora"):
            with self.subTest(valor=valor):
                self.assertNotIn(valor, texto)
