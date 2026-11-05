"""Apoio aos testes da feature 009 (research B15): sessão Realizada com o resultado liberado,
texto extraído dos PDFs e ouvintes da sessão.

Monta o cenário com o apoio da spec 008 (apoio_avaliacao): os 3 envios gravados direto, cada um
com uma cópia de assinatura no MEDIA_ROOT temporário, e a liberação pelo serviço
services_avaliacoes.liberar_resultado (com o parecer registrado antes em TCC 2 aprovado).

[US-28][US-30][RBN-DEF-07.1][RBN-DEF-08.2] (spec 009, tasks T002)
"""

from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from pypdf import PdfReader

from sigtcc.apps.cadastro.choices import DescricaoTurma
from sigtcc.apps.defesa import services_avaliacoes, services_defesa
from sigtcc.apps.defesa.choices import PapelBanca, Parecer, StatusSessao
from sigtcc.apps.defesa.models import Ouvintes, PresencaOuvintes
from sigtcc.apps.defesa.tests.apoio_avaliacao import _imagem, enviar, lancar, sessao_com_banca

# Nota de cada membro: abaixo de 6,0 o parecer é Reprovado (RBN-DEF-06.3).
NOTA_APROVADO = 8
NOTA_REPROVADO = 5


def copia_de_assinatura(sessao, membro):
    """Grava uma imagem PNG em assinaturas_banca/ (como a cópia do envio da spec 008) e devolve
    o caminho. A largura varia com o membro para cada cópia ter bytes próprios: o PDF reaproveita
    imagens idênticas, e assim cada assinatura conta como uma imagem no PDF (spec 009, T014).
    [US-26][US-28][RBN-DEF-05.2][RBN-DEF-07.1]
    """
    nome = f"assinaturas_banca/{sessao.pk}_{membro.pk}_teste.png"
    largura = 300 + membro.pk % 97
    return default_storage.save(nome, ContentFile(_imagem("PNG", largura, 100)))


def preparar_liberacao(
    etapa="TCC 2",
    parecer=Parecer.APROVADO,
    suplente_acionado=False,
    papel_substituido=PapelBanca.SEGUNDO_AVALIADOR,
    nota=None,
    qualis=None,
    **dados,
):
    """Sessão Em Andamento pronta para Liberar Resultado: os 3 envios com cópia de assinatura e,
    em TCC 2 aprovado, o parecer registrado pelo Orientador. `etapa` é "TCC 1" ou "TCC 2";
    `parecer` decide a nota de cada membro (Reprovado: 5,0; os demais: 8,0), salvo `nota`
    informada; `qualis` (ex.: "A1") grava um artigo publicado e homologado antes do parecer;
    `suplente_acionado` aciona o Suplente no lugar de `papel_substituido` antes dos envios. Os
    demais argumentos vão para sessao_com_banca (curso_nome, com_coordenador,
    assinatura_coordenador). Devolve o dicionário de sessao_com_banca com a sessão relida e mais
    `membros` (os 3 efetivos, na ordem da banca), `ausente` (o titular substituído ou None) e
    `apuracao` (nota final e parecer para a confirmação).
    [US-27][US-28][US-30][RBN-DEF-06.4][RBN-DEF-07.1][RBN-DEF-08.3]
    """
    from sigtcc.apps.cadastro.choices import Homologacao, StatusSubmissao
    from sigtcc.apps.cadastro.tests.apoio_orientacao import salvar_artigo

    descricao = DescricaoTurma(etapa)
    cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO, descricao=descricao, **dados)
    sessao, orientador = cenario["sessao"], cenario["orientador"]
    cenario["ausente"] = None
    if suplente_acionado:
        services_defesa.acionar_suplente(
            orientador, sessao.pk, papel_substituido, "Ausência do titular"
        )
        chave = "av1" if papel_substituido == PapelBanca.PRIMEIRO_AVALIADOR else "av2"
        cenario["ausente"] = cenario[chave]
    membros = services_defesa.membros_efetivos(sessao)
    if nota is None:
        nota = NOTA_REPROVADO if parecer == Parecer.REPROVADO else NOTA_APROVADO
    for membro in membros:
        lancar(sessao, membro, nota)
        enviar(sessao, membro, copia_de_assinatura(sessao, membro))
    if qualis:
        salvar_artigo(
            cenario["tcc"],
            qualis=qualis,
            status=StatusSubmissao.PUBLICADO,
            art_homologacao=Homologacao.HOMOLOGADO,
        )
    sessao.refresh_from_db()
    if descricao == DescricaoTurma.TCC_2 and parecer != Parecer.REPROVADO:
        services_avaliacoes.registrar_parecer(orientador, sessao.pk, parecer)
        sessao.refresh_from_db()
    cenario["sessao"] = sessao
    cenario["membros"] = membros
    cenario["apuracao"] = services_avaliacoes.apuracao(sessao)
    return cenario


def liberar(cenario):
    """Libera o resultado preparado por preparar_liberacao, pelo serviço da spec 008, e relê a
    sessão. [US-27][RBN-DEF-06.4]
    """
    sessao, atual = cenario["sessao"], cenario["apuracao"]
    resultado = services_avaliacoes.liberar_resultado(
        cenario["orientador"], sessao.pk, atual["nota_final"], atual["parecer"]
    )
    assert resultado.liberado, "A liberação do cenário de teste falhou"
    sessao.refresh_from_db()
    return cenario


def sessao_liberada(etapa="TCC 2", parecer=Parecer.APROVADO, suplente_acionado=False, **dados):
    """Sessão Realizada com o resultado liberado: preparar_liberacao (mesmos argumentos) e a
    liberação pelo serviço services_avaliacoes.liberar_resultado.
    [US-27][US-28][US-30][RBN-DEF-06.4][RBN-DEF-07.1][RBN-DEF-08.3]
    """
    return liberar(preparar_liberacao(etapa, parecer, suplente_acionado, **dados))


def numero_de_imagens(resposta):
    """Quantas imagens o PDF da resposta tem (imagens de bytes idênticos contam uma vez).
    [US-28][RBN-DEF-07.1][RBN-DEF-07.2]
    """
    leitor = PdfReader(BytesIO(resposta.content))
    return sum(len(pagina.images) for pagina in leitor.pages)


def texto_do_pdf(resposta):
    """Texto de todas as páginas do PDF da resposta (conteúdo em memória), lido com o pypdf.
    [US-28][US-30][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-08.1][RBN-DEF-08.3]
    """
    leitor = PdfReader(BytesIO(resposta.content))
    return "\n".join(pagina.extract_text() or "" for pagina in leitor.pages)


def ouvinte(matricula="2026000001", nome="Ana Souza"):
    """Registro de Ouvintes (criado se a matrícula ainda não existir; o nome gravado é mantido,
    P4). [US-30][RBN-DEF-08.2]
    """
    registro, _ = Ouvintes.objects.get_or_create(
        ouv_matricula=matricula, defaults={"ouv_nome": nome}
    )
    return registro


def presenca(sessao, registro):
    """Presença do ouvinte na sessão (Presenca_Ouvintes). [US-30][RBN-DEF-08.2][RBN-DEF-08.4]"""
    return PresencaOuvintes.objects.create(pre_def=sessao, pre_ouv=registro)
