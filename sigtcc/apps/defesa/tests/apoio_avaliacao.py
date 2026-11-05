"""Apoio aos testes da feature 008 (research A13): sessão "Em Andamento" com banca completa,
lançamento e envio de avaliações, imagens geradas em memória e MEDIA_ROOT temporário.

Monta o cenário com as fábricas da spec 007 (apoio_defesa). `lancar` e `enviar` gravam direto as
linhas de Avaliacoes e os campos de envio de BancaDefesa, só para montar o cenário (como
apoio_orientacao.liberar_resultado): quem testa as regras do formulário usa o serviço ou a tela.

Spec 009 (IC-16): sessao_com_banca cria por padrão o Coordenador de Curso com assinatura.

[infraestrutura de teste da feature 008][research A13] (tasks T004; spec 009 T001)
"""

import shutil
import tempfile
from decimal import Decimal
from io import BytesIO

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone
from PIL import Image

from sigtcc.apps.cadastro.choices import DescricaoTurma, StatusConta
from sigtcc.apps.cadastro.models import Coordenadores
from sigtcc.apps.cadastro.tests.apoio_turmas import EC, TesteTurmas, curso
from sigtcc.apps.defesa.choices import Conceito, StatusSessao
from sigtcc.apps.defesa.models import Avaliacoes, BancaDefesa, Criterios
from sigtcc.apps.defesa.tests.apoio_defesa import (
    agendar_sessao_de,
    avancar_para,
    docente,
    tcc_apto,
)

KB = 1024
MB = 1024 * KB


class TesteAvaliacao(TesteTurmas):
    """Base dos testes da feature 008: e-mail em memória e caches locais (TesteTurmas) e um
    MEDIA_ROOT temporário, apagado no fim da classe (research A13). [research A13]
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._midia = tempfile.mkdtemp(prefix="sigtcc_media_")
        cls.enterClassContext(override_settings(MEDIA_ROOT=cls._midia))
        cls.addClassCleanup(shutil.rmtree, cls._midia, ignore_errors=True)


def criterios():
    """Os 9 critérios da carga, na ordem (cri_id). [US-25][RBN-DEF-04.1]"""
    return list(Criterios.objects.order_by("cri_id"))


def conceito_da(nota):
    """Conceito cuja faixa contém a nota (RBN-DEF-05.2). [US-25][RBN-DEF-05.2]"""
    nota = Decimal(nota)
    if nota >= Decimal("8.0"):
        return Conceito.EXEMPLAR
    if nota >= Decimal("6.0"):
        return Conceito.COMPETENTE
    return Conceito.NECESSITA_DE_TRABALHO


def coordenador_do_curso(curso_nome=EC, com_assinatura=True):
    """Coordenador de Curso (Coordenadores) do curso, criado se o curso ainda não tiver um (o
    Coordenador é um só por curso, dicionário 3.3.1: a segunda sessão do mesmo curso reaproveita
    o existente). Com `com_assinatura`, garante uma imagem PNG no MEDIA_ROOT (temporário nos
    testes) como assinatura do perfil (doc_assinatura_path); sem ela, o caminho fica nulo (E2 da
    US-28). Devolve o Usuarios do Coordenador.
    [US-28][RBN-DEF-07.1][RBN-CAD-13.1] (spec 009, T001; IC-16)
    """
    existente = (
        Coordenadores.objects.select_related("cor_doc__doc")
        .filter(cor_cur=curso(curso_nome))
        .first()
    )
    if existente is not None:
        usuario, perfil = existente.cor_doc.doc, existente.cor_doc
    else:
        usuario = docente(curso_nome)
        perfil = usuario.docentes
        Coordenadores.objects.create(cor_cur=curso(curso_nome), cor_doc=perfil)
    if com_assinatura and not perfil.doc_assinatura_path:
        assinatura_no_perfil(usuario)
    elif not com_assinatura and perfil.doc_assinatura_path:
        perfil.doc_assinatura_path = None
        perfil.save(update_fields=["doc_assinatura_path"])
    return usuario


def sessao_com_banca(
    status=StatusSessao.EM_ANDAMENTO,
    curso_nome=EC,
    descricao=DescricaoTurma.TCC_1,
    suplente=True,
    com_coordenador=True,
    assinatura_coordenador=True,
):
    """Sessão no status pedido (pelo serviço único da spec 007), com Orientador, 1º e 2º
    Avaliador e, por padrão, um Suplente. Devolve um dicionário com sessao, tcc, professor,
    orientador, av1, av2, suplente, aluno e coordenador (Usuarios).

    Spec 009 (IC-16; research B15): por padrão cria também o Coordenador de Curso do curso da
    turma com assinatura no perfil, para a liberação não cair na E2 da US-28;
    `com_coordenador=False` deixa o curso sem Coordenador (coordenador = None) e
    `assinatura_coordenador=False` deixa o caminho da assinatura nulo.
    [US-25][US-27][US-28][RBN-DEF-02.1][RBN-DEF-07.1][RBN-CAD-13.1]
    """
    tcc, professor, orientador = tcc_apto(curso_nome, descricao)
    av1, av2 = docente(curso_nome), docente(curso_nome)
    banca = {"primeiro_avaliador": av1, "segundo_avaliador": av2}
    sup = docente(curso_nome) if suplente else None
    if sup is not None:
        banca["suplente"] = sup
    autor = orientador if curso_nome == EC else professor
    sessao = avancar_para(agendar_sessao_de(tcc, autor, banca), status)
    sessao.refresh_from_db()
    # Conta do aluno ativa, para entrar no sistema nos testes de sigilo.
    aluno = tcc.tcc_alu.alu
    aluno.usu_status = StatusConta.ATIVA
    aluno.save(update_fields=["usu_status"])
    coordenador = None
    if com_coordenador:
        coordenador = coordenador_do_curso(curso_nome, com_assinatura=assinatura_coordenador)
    else:
        # Curso sem Coordenador (E2 da US-28, MX-09), mesmo que outra sessão do teste tenha
        # criado um antes.
        Coordenadores.objects.filter(cor_cur=curso(curso_nome)).delete()
    return {
        "sessao": sessao,
        "tcc": tcc,
        "professor": professor,
        "orientador": orientador,
        "av1": av1,
        "av2": av2,
        "suplente": sup,
        "aluno": tcc.tcc_alu.alu,
        "coordenador": coordenador,
    }


def sessao_em_andamento(**dados):
    """Atalho de sessao_com_banca para a sessão "Em Andamento". [US-25][RBN-DEF-05.1]"""
    return sessao_com_banca(StatusSessao.EM_ANDAMENTO, **dados)


def lancar(sessao, membro, notas, observacoes=None, criterios_lancados=None):
    """Grava as notas do membro (rascunho): `notas` é uma nota para os 9 critérios ou uma lista
    com uma nota por critério (na ordem da carga); o conceito sai da faixa da nota.
    `criterios_lancados` limita aos critérios informados. [US-25][RBN-DEF-05.1][RBN-DEF-05.2]
    """
    lista = criterios_lancados or criterios()
    if not isinstance(notas, (list, tuple)):
        notas = [notas] * len(lista)
    agora = timezone.now()
    for criterio, nota in zip(lista, notas):
        Avaliacoes.objects.update_or_create(
            ava_def=sessao,
            ava_usu=membro,
            ava_cri=criterio,
            defaults={
                "ava_conceito": conceito_da(nota),
                "ava_nota": Decimal(str(nota)),
                "ava_observacoes": observacoes,
                "ava_data_hora": agora,
            },
        )


def enviar(sessao, membro, caminho=None):
    """Marca a avaliação do membro como "Enviada" (data de envio e, se informado, o caminho da
    cópia da assinatura). [US-25][US-26][RBN-DEF-05.2]
    """
    BancaDefesa.objects.filter(ban_def=sessao, ban_usu=membro).update(
        ban_data_envio=timezone.now(), ban_assinatura_path=caminho
    )


def lancar_e_enviar(sessao, membro, notas, **dados):
    """lancar + enviar, para montar os 3 envios. [US-25][US-27][RBN-DEF-06.6]"""
    lancar(sessao, membro, notas, **dados)
    enviar(sessao, membro)


def _imagem(formato, largura, altura, tamanho=None):
    """Bytes de uma imagem PNG ou JPEG válida; com `tamanho`, completa com bytes depois do fim
    da imagem até esse total (o arquivo continua abrindo no Pillow). [US-26][research A13]
    """
    saida = BytesIO()
    Image.new("RGB", (largura, altura), (20, 20, 20)).save(saida, format=formato)
    dados = saida.getvalue()
    if tamanho is not None and tamanho > len(dados):
        dados += b"\0" * (tamanho - len(dados))
    return dados


def png(nome="assinatura.png", tamanho=500 * KB, largura=600, altura=200):
    """PNG anexado (padrão: 500 KB, 600 × 200). [US-26][RBN-DEF-05.2]"""
    return SimpleUploadedFile(nome, _imagem("PNG", largura, altura, tamanho), "image/png")


def jpg(nome="assinatura.jpg", tamanho=None, largura=600, altura=200):
    """JPG anexado. [US-26][RBN-DEF-05.2]"""
    return SimpleUploadedFile(nome, _imagem("JPEG", largura, altura, tamanho), "image/jpeg")


def png_de_3_mb():
    """PNG de 3 MB (US-26 cenário 6). [US-26][RBN-DEF-05.2]"""
    return png(tamanho=3 * MB)


def png_gigante():
    """PNG pequeno em bytes e de 3000 × 3000 pixels (revisão I-11; MA-14). [US-26]"""
    return png(nome="gigante.png", tamanho=None, largura=3000, altura=3000)


def pdf_falso():
    """Arquivo .pdf (US-26 cenário 7). [US-26][RBN-DEF-05.2]"""
    return SimpleUploadedFile("assinatura.pdf", b"%PDF-1.4\n%falso\n", "application/pdf")


def assinatura_no_perfil(usuario, conteudo=None):
    """Grava uma imagem PNG como assinatura do perfil do Docente ou do Membro Externo (US-38)
    no MEDIA_ROOT temporário. Devolve o caminho. [US-26][US-38][RBN-DEF-05.2]
    """
    from sigtcc.apps.cadastro import services

    arquivo = SimpleUploadedFile("perfil.png", conteudo or _imagem("PNG", 400, 120), "image/png")
    return services.salvar_assinatura(usuario, arquivo, "png")


def existe(caminho):
    """O arquivo existe no armazenamento padrão. [US-26][research A5]"""
    return bool(caminho) and default_storage.exists(caminho)


def formulario(notas=None, acao="salvar", observacoes=None, conceitos=None, **extras):
    """Dados do POST do formulário Avaliação (formset "cri" com os 9 critérios): `notas` é uma
    nota para todos, uma lista (None = critério vazio) ou None (todos vazios); `conceitos`
    troca o conceito calculado pela faixa; `observacoes` = {índice: texto}.
    [US-25][US-26][RBN-DEF-05.2]
    """
    if notas is None or not isinstance(notas, (list, tuple)):
        notas = [notas] * 9
    dados = {
        "acao": acao,
        "cri-TOTAL_FORMS": "9",
        "cri-INITIAL_FORMS": "9",
        "cri-MIN_NUM_FORMS": "9",
        "cri-MAX_NUM_FORMS": "9",
    }
    for indice, nota in enumerate(notas):
        conceito = ""
        if conceitos and indice in conceitos:
            conceito = conceitos[indice]
        elif nota is not None:
            conceito = conceito_da(nota)
        dados[f"cri-{indice}-conceito"] = conceito
        dados[f"cri-{indice}-nota"] = "" if nota is None else str(nota).replace(".", ",")
        dados[f"cri-{indice}-observacoes"] = (observacoes or {}).get(indice, "")
    dados.update(extras)
    return dados
