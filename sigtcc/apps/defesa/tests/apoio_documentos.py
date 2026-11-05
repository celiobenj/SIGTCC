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
    o caminho. [US-26][US-28][RBN-DEF-05.2][RBN-DEF-07.1]
    """
    nome = f"assinaturas_banca/{sessao.pk}_{membro.pk}_teste.png"
    return default_storage.save(nome, ContentFile(_imagem("PNG", 300, 100)))


def sessao_liberada(etapa="TCC 2", parecer=Parecer.APROVADO, suplente_acionado=False, **dados):
    """Sessão Realizada com o resultado liberado. `etapa` é "TCC 1" ou "TCC 2"; `parecer` decide
    as notas (Reprovado: 5,0; os demais: 8,0) e, em TCC 2 aprovado, é registrado pelo
    Orientador antes da liberação; `suplente_acionado` aciona o Suplente no lugar do 2º
    Avaliador antes dos envios. Os demais argumentos vão para sessao_com_banca (curso_nome,
    com_coordenador, assinatura_coordenador). Devolve o dicionário de sessao_com_banca, com a
    sessão relida e mais `membros` (os 3 efetivos, na ordem da banca) e `ausente` (o titular
    substituído ou None). [US-27][US-28][US-30][RBN-DEF-06.4][RBN-DEF-07.1][RBN-DEF-08.3]
    """
    descricao = DescricaoTurma(etapa)
    cenario = sessao_com_banca(StatusSessao.EM_ANDAMENTO, descricao=descricao, **dados)
    sessao, orientador = cenario["sessao"], cenario["orientador"]
    cenario["ausente"] = None
    if suplente_acionado:
        services_defesa.acionar_suplente(
            orientador, sessao.pk, PapelBanca.SEGUNDO_AVALIADOR, "Ausência do 2º Avaliador"
        )
        cenario["ausente"] = cenario["av2"]
    membros = services_defesa.membros_efetivos(sessao)
    nota = NOTA_REPROVADO if parecer == Parecer.REPROVADO else NOTA_APROVADO
    for membro in membros:
        lancar(sessao, membro, nota)
        enviar(sessao, membro, copia_de_assinatura(sessao, membro))
    sessao.refresh_from_db()
    if descricao == DescricaoTurma.TCC_2 and parecer != Parecer.REPROVADO:
        services_avaliacoes.registrar_parecer(orientador, sessao.pk, parecer)
        sessao.refresh_from_db()
    atual = services_avaliacoes.apuracao(sessao)
    resultado = services_avaliacoes.liberar_resultado(
        orientador, sessao.pk, atual["nota_final"], atual["parecer"]
    )
    assert resultado.liberado, "A liberação do cenário de teste falhou"
    sessao.refresh_from_db()
    cenario["sessao"] = sessao
    cenario["membros"] = membros
    return cenario


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
