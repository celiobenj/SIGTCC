"""Restrições do banco no app cadastro: cada uma tem um teste de recusa e um de aceitação.

Toda recusa é verificada dentro de transaction.atomic(). As FKs são adiadas (DEFERRABLE INITIALLY
DEFERRED, research R5), por isso os testes de FK executam SET CONSTRAINTS ALL IMMEDIATE antes.

[base de todas as US; sem RBN específica][spec 001, US2 cenários 1 a 8 e 10][FR-004]–[FR-012]
[SC-002]
"""

from django.db import IntegrityError, connection, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from sigtcc.apps.cadastro.choices import (
    GatilhoStatusTCC,
    OrigemOrientacao,
    StatusCoorientacao,
    StatusEntrega,
    StatusOrientacao,
    StatusSolicitacao,
    StatusTCC,
    TipoEntrega,
    TipoSolicitacao,
    Titulacao,
)
from sigtcc.apps.cadastro.models import (
    Alunos,
    AlunosTurmas,
    AreasInteresse,
    Artigos,
    Coordenadores,
    Coorientacoes,
    Disciplinas,
    Docentes,
    EntregasMarcos,
    HistoricoAlunosTurmas,
    HistoricoStatusTCC,
    MembrosExternos,
    Orientacoes,
    PalavrasChaveTCC,
    SolicitacoesOrientacao,
)
from sigtcc.apps.cadastro.tests import fabricas as f


class RestricoesTestCase(TestCase):
    """Base com as asserções de recusa e aceitação."""

    def assertRecusa(self, funcao, imediato=False):
        """O banco recusa a gravação (IntegrityError), sem quebrar a transação do teste."""
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                if imediato:
                    with connection.cursor() as cursor:
                        cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
                funcao()

    def assertAceita(self, funcao):
        """O banco aceita a gravação."""
        with transaction.atomic():
            return funcao()


class CenariosDaSpecTest(RestricoesTestCase):
    """Cenários Dado/Quando/Então da US2 da spec 001."""

    def test_cenario1_tcc_status_fora_do_glossario(self):
        """Dado um TCC, quando o status é 'Finalizado', então o banco recusa (FR-008)."""
        self.assertRecusa(lambda: f.criar_tcc(tcc_status="Finalizado"))
        self.assertAceita(lambda: f.criar_tcc(tcc_status=StatusTCC.SEM_PROPOSTA))

    def test_cenario2_campos_obrigatorios_com_proposta(self):
        """Título, resumo e modalidade obrigatórios fora de 'Sem Proposta' (FR-011; Q1)."""
        self.assertRecusa(lambda: f.criar_tcc(tcc_status=StatusTCC.EM_ANDAMENTO))
        self.assertAceita(lambda: f.criar_tcc_com_proposta())
        self.assertRecusa(lambda: f.criar_tcc(tcc_status=StatusTCC.DESISTENTE))
        self.assertAceita(lambda: f.criar_tcc(tcc_status=StatusTCC.SEM_PROPOSTA))

    def test_cenario3_uma_orientacao_ativa(self):
        """No máximo uma orientação 'Ativa' por TCC; as encerradas formam o histórico (FR-007)."""
        tcc = f.criar_tcc_com_proposta()

        def orientar(status):
            return Orientacoes.objects.create(
                ori_tcc=tcc,
                ori_doc=f.criar_docente(),
                ori_origem=OrigemOrientacao.PEDIDO_ACEITO,
                ori_status=status,
                ori_data_inicio=f.AGORA,
            )

        self.assertAceita(lambda: orientar(StatusOrientacao.ATIVA))
        self.assertRecusa(lambda: orientar(StatusOrientacao.ATIVA))
        self.assertAceita(lambda: orientar(StatusOrientacao.ENCERRADA))

    def test_cenario4_uma_entrega_por_tipo(self):
        """Uma entrega de cada tipo por turma, exceto 'Outra' (FR-007)."""
        turma = f.criar_turma()
        self.assertAceita(lambda: f.criar_marco(turma, TipoEntrega.PROPOSTA))
        self.assertRecusa(lambda: f.criar_marco(turma, TipoEntrega.PROPOSTA))
        self.assertAceita(lambda: f.criar_marco(turma, TipoEntrega.OUTRA))
        self.assertAceita(lambda: f.criar_marco(turma, TipoEntrega.OUTRA))

    def test_cenario5_coorientacao_docente_ou_externo(self):
        """Exatamente um entre docente e externo, sem repetir vínculo ativo (FR-007, FR-011)."""
        tcc = f.criar_tcc_com_proposta()
        docente = f.criar_docente()

        def coorientar(doc=None, cext=None, status=StatusCoorientacao.ATIVA):
            return Coorientacoes.objects.create(
                coo_tcc=tcc,
                coo_doc=doc,
                coo_cext=cext,
                coo_status=status,
                coo_data_inicio=f.AGORA,
            )

        self.assertRecusa(
            lambda: coorientar(doc=f.criar_docente(), cext=f.criar_coorientador_externo())
        )
        self.assertRecusa(lambda: coorientar())
        self.assertAceita(lambda: coorientar(doc=docente))
        self.assertAceita(lambda: coorientar(cext=f.criar_coorientador_externo()))
        self.assertRecusa(lambda: coorientar(doc=docente))
        outro_tcc_docente = f.criar_docente()
        self.assertAceita(
            lambda: coorientar(doc=outro_tcc_docente, status=StatusCoorientacao.SUBSTITUIDA)
        )
        self.assertAceita(lambda: coorientar(doc=outro_tcc_docente))

    def test_cenario6_status_por_tipo(self):
        """sol_status depende do tipo; um pedido de orientação pendente por TCC (FR-007, FR-009)."""
        tcc = f.criar_tcc_com_proposta()

        def solicitar(tipo, status, alvo=tcc):
            return SolicitacoesOrientacao.objects.create(
                sol_tcc=alvo,
                sol_doc=f.criar_docente(),
                sol_tipo=tipo,
                sol_status=status,
                sol_data_solicitacao=f.AGORA,
            )

        self.assertRecusa(
            lambda: solicitar(TipoSolicitacao.COORIENTACAO, StatusSolicitacao.AGUARDANDO_RESPOSTA)
        )
        self.assertAceita(
            lambda: solicitar(TipoSolicitacao.COORIENTACAO, StatusSolicitacao.AGUARDANDO_ACEITE)
        )
        self.assertRecusa(
            lambda: solicitar(TipoSolicitacao.ORIENTACAO, StatusSolicitacao.AGUARDANDO_ACEITE)
        )
        self.assertAceita(
            lambda: solicitar(TipoSolicitacao.ORIENTACAO, StatusSolicitacao.AGUARDANDO_RESPOSTA)
        )
        self.assertRecusa(
            lambda: solicitar(
                TipoSolicitacao.TROCA_DE_ORIENTACAO, StatusSolicitacao.AGUARDANDO_RESPOSTA
            )
        )
        self.assertAceita(lambda: solicitar(TipoSolicitacao.ORIENTACAO, StatusSolicitacao.RECUSADO))

    def test_cenario7_emails(self):
        """E-mails nulos não colidem; e-mail repetido é recusado (FR-007)."""
        self.assertAceita(lambda: f.criar_usuario(email=None))
        self.assertAceita(lambda: f.criar_usuario(email=None))
        f.criar_usuario(email="repetido@uea.edu.br")
        self.assertRecusa(lambda: f.criar_usuario(email="repetido@uea.edu.br"))
        self.assertAceita(lambda: f.criar_coorientador_externo())
        self.assertAceita(lambda: f.criar_coorientador_externo())
        f.criar_coorientador_externo(email="externo@ufam.edu.br")
        self.assertRecusa(lambda: f.criar_coorientador_externo(email="externo@ufam.edu.br"))

    def test_cenario8_horario_turma(self):
        """tur_hora_termino tem de ser posterior a tur_hora_inicio (FR-011)."""
        from datetime import time

        self.assertRecusa(
            lambda: f.criar_turma(tur_hora_inicio=time(16, 0), tur_hora_termino=time(16, 0))
        )
        self.assertRecusa(
            lambda: f.criar_turma(tur_hora_inicio=time(16, 0), tur_hora_termino=time(14, 0))
        )
        self.assertAceita(
            lambda: f.criar_turma(tur_hora_inicio=time(14, 0), tur_hora_termino=time(16, 0))
        )

    def test_cenario10_fk_inexistente(self):
        """Referência a registro inexistente é recusada (FR-005)."""
        usuario = f.criar_usuario()
        self.assertRecusa(
            lambda: Docentes.objects.create(
                doc=usuario, doc_titulacao=Titulacao.MESTRE, doc_cur_id=999999
            ),
            imediato=True,
        )
        self.assertAceita(
            lambda: Docentes.objects.create(
                doc=usuario, doc_titulacao=Titulacao.MESTRE, doc_cur=f.criar_curso()
            )
        )

    def test_exclusao_protegida(self):
        """Excluir pelo ORM uma linha referenciada levanta ProtectedError (FR-005, R5)."""
        docente = f.criar_docente()
        with self.assertRaises(ProtectedError):
            docente.doc_cur.delete()

    def test_exclusao_recusada_pelo_banco(self):
        """DELETE por SQL de uma linha referenciada é recusado pelo próprio banco (FR-005)."""
        docente = f.criar_docente()

        def excluir():
            with connection.cursor() as cursor:
                cursor.execute('DELETE FROM "Cursos" WHERE cur_id = %s', [docente.doc_cur_id])

        self.assertRecusa(excluir, imediato=True)

    def test_fr012_not_lida_padrao_falso(self):
        """Notificação inserida sem not_lida nasce com false (FR-012, R6)."""
        usuario = f.criar_usuario()
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO "Notificacoes" (not_usu_id, not_mensagem, not_data_hora) '
                "VALUES (%s, %s, %s) RETURNING not_lida",
                [usuario.usu_id, "Mensagem de teste", f.AGORA],
            )
            self.assertIs(cursor.fetchone()[0], False)

    def test_pk_composta_recusa_duplicata(self):
        """As PKs compostas de Alunos_Turmas e PalavrasChave_TCC recusam duplicatas (FR-004)."""
        aluno, turma, outra_turma = f.criar_aluno(), f.criar_turma(), f.criar_turma()

        def matricular(t):
            return AlunosTurmas.objects.create(mat_alu=aluno, mat_tur=t, mat_data_inscricao=f.AGORA)

        self.assertAceita(lambda: matricular(turma))
        self.assertRecusa(lambda: matricular(turma))
        self.assertAceita(lambda: matricular(outra_turma))

        tcc = f.criar_tcc_com_proposta()
        self.assertAceita(
            lambda: PalavrasChaveTCC.objects.create(pal_tcc=tcc, pal_palavra="Django")
        )
        self.assertRecusa(
            lambda: PalavrasChaveTCC.objects.create(pal_tcc=tcc, pal_palavra="Django")
        )
        self.assertAceita(
            lambda: PalavrasChaveTCC.objects.create(pal_tcc=tcc, pal_palavra="PostgreSQL")
        )


class DominiosTest(RestricoesTestCase):
    """Um valor inválido recusado e um válido aceito em cada CHECK de domínio (FR-008, FR-010)."""

    def construtores(self):
        """(restrição, função que grava com o valor, inválido, válidos)."""
        tcc = f.criar_tcc_com_proposta

        def historico_tcc(**campos):
            valores = {
                "hst_tcc": tcc(),
                "hst_tur": f.criar_turma(),
                "hst_status_novo": StatusTCC.EM_ANDAMENTO,
                "hst_gatilho": GatilhoStatusTCC.PROPOSTA_SALVA,
                "hst_data_hora": f.AGORA,
                "hst_usu": f.criar_usuario(),
            }
            valores.update(campos)
            return HistoricoStatusTCC.objects.create(**valores)

        def artigo(**campos):
            return Artigos.objects.create(
                art=tcc(), art_link_doi="https://doi.org/10.1/x", **campos
            )

        return [
            ("ck_usuarios_usu_status", lambda v: f.criar_usuario(status=v), "Bloqueada", ["Ativa"]),
            (
                "ck_docentes_doc_titulacao",
                lambda v: Docentes.objects.create(
                    doc=f.criar_usuario(), doc_titulacao=v, doc_cur=f.criar_curso()
                ),
                "Graduado",
                ["Mestre"],
            ),
            (
                "ck_membrosexternos_mem_titulacao",
                lambda v: MembrosExternos.objects.create(
                    mem=f.criar_usuario(), mem_titulacao=v, mem_instituicao="UFAM"
                ),
                "Livre-docente",
                ["Especialista"],
            ),
            (
                "ck_turmas_tur_descricao",
                lambda v: f.criar_turma(tur_descricao=v),
                "TCC 3",
                ["TCC 2"],
            ),
            (
                "ck_turmas_tur_status",
                lambda v: f.criar_turma(tur_status=v),
                "Excluída",
                ["Arquivada"],
            ),
            (
                "ck_turmas_tur_dia_da_semana",
                lambda v: f.criar_turma(tur_dia_da_semana=v),
                "domingo",
                ["sábado"],
            ),
            (
                "ck_historico_alunos_turmas_hat_tipo_evento",
                lambda v: HistoricoAlunosTurmas.objects.create(
                    hat_alu=f.criar_aluno(),
                    hat_tur_origem=f.criar_turma(),
                    hat_tipo_evento=v,
                    hat_justificativa="Justificativa",
                    hat_data_hora=f.AGORA,
                    hat_usu=f.criar_usuario(),
                ),
                "Inclusão",
                ["Exclusão", "Transferência"],
            ),
            ("ck_turmas_marcos_tma_tipo", lambda v: f.criar_marco(tipo=v), "Relatório", ["Outra"]),
            (
                "ck_entregas_marcos_ent_status",
                lambda v: EntregasMarcos.objects.create(
                    ent_tma=f.criar_marco(), ent_alu=f.criar_aluno(), ent_status=v
                ),
                "Pendente",
                [StatusEntrega.AGUARDANDO_ENVIO],
            ),
            (
                "ck_tccs_tcc_modalidade",
                lambda v: f.criar_tcc_com_proposta(tcc_modalidade=v),
                "Relatório Técnico",
                ["Artigo Científico"],
            ),
            (
                "ck_orientacoes_ori_origem",
                lambda v: Orientacoes.objects.create(
                    ori_tcc=tcc(),
                    ori_doc=f.criar_docente(),
                    ori_origem=v,
                    ori_status=StatusOrientacao.ATIVA,
                    ori_data_inicio=f.AGORA,
                ),
                "Indicação",
                ["Automático"],
            ),
            (
                "ck_orientacoes_ori_status",
                lambda v: Orientacoes.objects.create(
                    ori_tcc=tcc(),
                    ori_doc=f.criar_docente(),
                    ori_origem=OrigemOrientacao.AUTOMATICO,
                    ori_status=v,
                    ori_data_inicio=f.AGORA,
                ),
                "Suspensa",
                ["Encerrada"],
            ),
            (
                "ck_coorientacoes_coo_status",
                lambda v: Coorientacoes.objects.create(
                    coo_tcc=tcc(), coo_doc=f.criar_docente(), coo_status=v, coo_data_inicio=f.AGORA
                ),
                "Cancelada",
                ["Substituída"],
            ),
            (
                "ck_solicitacoes_orientacao_sol_tipo",
                lambda v: SolicitacoesOrientacao.objects.create(
                    sol_tcc=tcc(),
                    sol_doc=f.criar_docente(),
                    sol_tipo=v,
                    sol_status=StatusSolicitacao.ACEITO,
                    sol_data_solicitacao=f.AGORA,
                ),
                "Banca",
                ["Troca de Orientação"],
            ),
            (
                "ck_historico_status_tcc_hst_status_anterior",
                lambda v: historico_tcc(hst_status_anterior=v),
                "Finalizado",
                [None, "Sem Proposta"],
            ),
            (
                "ck_historico_status_tcc_hst_status_novo",
                lambda v: historico_tcc(hst_status_novo=v),
                "Finalizado",
                ["Concluído"],
            ),
            (
                "ck_historico_status_tcc_hst_gatilho",
                lambda v: historico_tcc(hst_gatilho=v),
                "Edição manual",
                ["Vínculo à turma"],
            ),
            (
                "ck_artigos_art_qualis_capes",
                lambda v: artigo(art_qualis_capes=v),
                "A5",
                [None, "B4"],
            ),
            (
                "ck_artigos_art_status_submissao",
                lambda v: artigo(art_status_submissao=v),
                "Retirado",
                [None, "Em Revisão"],
            ),
            (
                "ck_artigos_art_homologacao",
                lambda v: artigo(art_homologacao=v),
                "Pendente",
                [None, "Em Análise"],
            ),
            (
                "ck_alunos_alu_matricula",
                lambda v: Alunos.objects.create(
                    alu=f.criar_usuario(), alu_matricula=v, alu_codigo_curso="EST08MCPD"
                ),
                "12345",
                ["2026000001"],
            ),
            ("ck_turmas_tur_ano", lambda v: f.criar_turma(tur_ano=v), 999, [2026]),
            ("ck_turmas_tur_semestre", lambda v: f.criar_turma(tur_semestre=v), 3, [1, 2]),
        ]

    def test_dominios(self):
        for restricao, gravar, invalido, validos in self.construtores():
            with self.subTest(restricao=restricao, valor=invalido):
                self.assertRecusa(lambda: gravar(invalido))
            for valido in validos:
                with self.subTest(restricao=restricao, valor=valido):
                    self.assertAceita(lambda: gravar(valido))

    def test_matricula_com_letras_e_ano_acima_de_4_digitos(self):
        """Matrícula só com dígitos (ck_alunos_alu_matricula) e ano até 9999 (ck_turmas_tur_ano)."""
        self.assertRecusa(
            lambda: Alunos.objects.create(
                alu=f.criar_usuario(), alu_matricula="ABCDEFGHIJ", alu_codigo_curso="X"
            )
        )
        self.assertRecusa(lambda: f.criar_turma(tur_ano=10000))


class UnicidadesTest(RestricoesTestCase):
    """Unicidades simples e compostas de FR-006: a duplicata é recusada."""

    def test_unicidades_simples(self):
        Disciplinas.objects.create(dis_codigo="ESTCMP025")
        self.assertRecusa(lambda: Disciplinas.objects.create(dis_codigo="ESTCMP025"))

        AreasInteresse.objects.create(ari_nome="Área de teste")
        self.assertRecusa(lambda: AreasInteresse.objects.create(ari_nome="Área de teste"))

        f.criar_aluno(matricula="2026999999")
        self.assertRecusa(lambda: f.criar_aluno(matricula="2026999999"))

        f.criar_turma(tur_identificador="ECP06_T01")
        self.assertRecusa(lambda: f.criar_turma(tur_identificador="ECP06_T01"))

        docente = f.criar_docente()
        Coordenadores.objects.create(cor_cur=f.criar_curso(), cor_doc=docente)
        self.assertRecusa(
            lambda: Coordenadores.objects.create(cor_cur=f.criar_curso(), cor_doc=docente)
        )

    def test_unicidades_compostas(self):
        marco, aluno = f.criar_marco(), f.criar_aluno()

        def entregar():
            return EntregasMarcos.objects.create(
                ent_tma=marco, ent_alu=aluno, ent_status=StatusEntrega.AGUARDANDO_ENVIO
            )

        self.assertAceita(entregar)
        self.assertRecusa(entregar)

        turma = f.criar_turma()
        self.assertAceita(lambda: f.criar_tcc(tcc_alu=aluno, tcc_tur=turma))
        self.assertRecusa(lambda: f.criar_tcc(tcc_alu=aluno, tcc_tur=turma))
        self.assertAceita(lambda: f.criar_tcc(tcc_alu=aluno, tcc_tur=f.criar_turma()))
