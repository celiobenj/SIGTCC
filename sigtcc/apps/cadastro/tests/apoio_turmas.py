"""Apoio aos testes da feature 004: turmas, alunos matriculados, TCCs, defesas, entregas,
solicitações e arquivos de importação em memória.

Só usa os modelos (não depende de services_turmas), para os testes poderem vir antes do código.

[infraestrutura de teste da feature 004][research B24]
"""

import csv
import io
from datetime import time

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from openpyxl import Workbook

from sigtcc.apps.cadastro.cargas import (
    CURSO_ENG_COMPUTACAO,
    CURSO_LIC_COMPUTACAO,
    CURSO_SIST_INFORMACAO,
)
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    DiaSemana,
    GatilhoStatusTCC,
    ModalidadeTCC,
    StatusConta,
    StatusEntrega,
    StatusSolicitacao,
    StatusTCC,
    StatusTurma,
    TipoEntrega,
    TipoSolicitacao,
)
from sigtcc.apps.cadastro.models import (
    Alunos,
    AlunosTurmas,
    Cursos,
    EntregasMarcos,
    HistoricoEnviosEntregas,
    HistoricoStatusTCC,
    SolicitacoesOrientacao,
    TCCs,
    Turmas,
    TurmasMarcos,
    Usuarios,
)
from sigtcc.apps.cadastro.tests.apoio_acesso import TesteAcesso
from sigtcc.apps.cadastro.tests.fabricas import criar_disciplina, proximo

CABECALHO = ("Matrícula", "Nome Completo", "Curso")
EC, SI, LC = CURSO_ENG_COMPUTACAO, CURSO_SIST_INFORMACAO, CURSO_LIC_COMPUTACAO
STATUS_COM_PROPOSTA = {
    StatusTCC.EM_ANDAMENTO,
    StatusTCC.APTO_PARA_DEFESA,
    StatusTCC.APROVADO_PARA_TCC_2,
    StatusTCC.APROVADO,
    StatusTCC.APROVADO_COM_CORRECOES,
    StatusTCC.CONCLUIDO,
    StatusTCC.REPROVADO,
    StatusTCC.DESISTENTE,
    StatusTCC.JUBILADO,
}


class TesteTurmas(TesteAcesso):
    """Base dos testes da feature 004 (a mesma da spec 003: e-mail em memória, caches locais)."""


def curso(nome=EC):
    """Curso do NUCOMP da carga da spec 001."""
    return Cursos.objects.get(cur_nome=nome)


def criar_turma_de(
    professor,
    descricao=DescricaoTurma.TCC_1,
    curso_nome=EC,
    status=StatusTurma.ATIVA,
    ano=2026,
    semestre=2,
    identificador=None,
):
    """Turma do professor (Usuarios com Docentes). [US-07][RBN-CAD-04.1]"""
    return Turmas.objects.create(
        tur_identificador=identificador or f"T{proximo():04d}_TESTE",
        tur_descricao=descricao,
        tur_doc=professor.docentes,
        tur_dis=criar_disciplina(),
        tur_cur=curso(curso_nome),
        tur_ano=ano,
        tur_semestre=semestre,
        tur_dia_da_semana=DiaSemana.SEGUNDA,
        tur_hora_inicio=time(14, 0),
        tur_hora_termino=time(16, 0),
        tur_local="Laboratório LSI",
        tur_status=status,
    )


def criar_aluno_novo(matricula=None, nome=None, codigo_curso="EST08MCPD", status_conta=None):
    """Aluno sem turma (conta 'Aguardando Ativação' por padrão). [US-08][RBN-CAD-05.1]"""
    usuario = Usuarios.objects.create_user(
        None,
        nome or f"Aluno Teste {proximo()}",
        usu_status=status_conta or StatusConta.AGUARDANDO_ATIVACAO,
    )
    return Alunos.objects.create(
        alu=usuario,
        alu_matricula=matricula or f"{2026200000 + proximo():010d}",
        alu_codigo_curso=codigo_curso,
    )


def matricular_aluno(turma, aluno=None, status_tcc=StatusTCC.SEM_PROPOSTA, autor=None, **dados):
    """Vincula o aluno à turma com um TCC no Status pedido e o histórico do vínculo.

    Para Status com Proposta, preenche título, resumo e modalidade (CHECK da spec 001).
    [US-08][RBN-CAD-05.1][RBN-CAD-08.3]
    """
    aluno = aluno or criar_aluno_novo(**dados)
    AlunosTurmas.objects.create(mat_alu=aluno, mat_tur=turma, mat_data_inscricao=timezone.now())
    campos = {}
    if status_tcc in STATUS_COM_PROPOSTA:
        campos = {
            "tcc_titulo": "Título do trabalho",
            "tcc_resumo": "Resumo do trabalho",
            "tcc_modalidade": ModalidadeTCC.MONOGRAFIA,
        }
    tcc = TCCs.objects.create(tcc_alu=aluno, tcc_tur=turma, tcc_status=status_tcc, **campos)
    HistoricoStatusTCC.objects.create(
        hst_tcc=tcc,
        hst_tur=turma,
        hst_status_anterior=None,
        hst_status_novo=StatusTCC.SEM_PROPOSTA,
        hst_gatilho=GatilhoStatusTCC.VINCULO_A_TURMA,
        hst_data_hora=timezone.now(),
        hst_usu=autor or turma.tur_doc.doc,
    )
    return aluno


def tcc_de(aluno, turma):
    """TCC do aluno na turma."""
    return TCCs.objects.get(tcc_alu=aluno, tcc_tur=turma)


def criar_defesa_de(tcc, status):
    """Sessão de defesa do TCC no Status pedido. [US-21][RBN-DEF-01.1]"""
    from sigtcc.apps.cadastro.tests.fabricas import criar_defesa

    return criar_defesa(tcc=tcc, def_status=status)


def criar_entrega(turma, tipo=TipoEntrega.OUTRA, data_limite=None, titulo=None):
    """Entrega cadastrada na turma. [US-43][RBN-CAD-09.1]"""
    return TurmasMarcos.objects.create(
        tma_tur=turma,
        tma_tipo=tipo,
        tma_titulo=titulo or f"Entrega {proximo()}",
        tma_data_limite=data_limite or timezone.now(),
    )


def entrega_do_aluno(entrega, aluno, status=StatusEntrega.AGUARDANDO_ENVIO):
    """Registro do aluno na entrega. [US-16][RBN-CAD-09.2]"""
    return EntregasMarcos.objects.create(ent_tma=entrega, ent_alu=aluno, ent_status=status)


def criar_envio(registro):
    """Um envio (link) do aluno numa entrega. [US-16][RBN-CAD-09.3]"""
    return HistoricoEnviosEntregas.objects.create(
        hen_ent=registro, hen_link="https://drive.example/arquivo", hen_data_envio=timezone.now()
    )


def criar_solicitacao(tcc, docente, tipo=TipoSolicitacao.ORIENTACAO, status=None):
    """Pedido de orientação ou convite de coorientação. [US-17][RBN-CAD-10.1][US-45]"""
    if status is None:
        status = (
            StatusSolicitacao.AGUARDANDO_ACEITE
            if tipo == TipoSolicitacao.COORIENTACAO
            else StatusSolicitacao.AGUARDANDO_RESPOSTA
        )
    return SolicitacoesOrientacao.objects.create(
        sol_tcc=tcc,
        sol_doc=docente.docentes,
        sol_tipo=tipo,
        sol_status=status,
        sol_data_solicitacao=timezone.now(),
    )


def arquivo_csv(linhas, separador=";", codificacao="utf-8", cabecalho=CABECALHO, nome=None):
    """Arquivo CSV em memória, como o enviado pelo formulário."""
    texto = io.StringIO()
    escritor = csv.writer(texto, delimiter=separador, lineterminator="\n")
    if cabecalho:
        escritor.writerow(cabecalho)
    escritor.writerows(linhas)
    return SimpleUploadedFile(
        nome or "alunos.csv", texto.getvalue().encode(codificacao), content_type="text/csv"
    )


def arquivo_xlsx(linhas, planilhas=1, cabecalho=CABECALHO, nome="alunos.xlsx"):
    """Arquivo XLSX em memória; as planilhas extras recebem lixo que não deve ser lido."""
    livro = Workbook()
    folha = livro.active
    if cabecalho:
        folha.append(list(cabecalho))
    for linha in linhas:
        folha.append(list(linha))
    for numero in range(1, planilhas):
        extra = livro.create_sheet(f"Extra{numero}")
        extra.append(["Matrícula", "Nome Completo", "Curso"])
        extra.append(["9999999999", "Nao Deve Entrar", "EST08MCPD"])
    saida = io.BytesIO()
    livro.save(saida)
    return SimpleUploadedFile(
        nome,
        saida.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
