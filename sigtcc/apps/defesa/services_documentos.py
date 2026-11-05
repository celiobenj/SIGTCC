"""Documentos da defesa (spec 009, research B1 a B8; contrato
specs/009-documentacao-encerramento/contracts/servicos-documentos.md): Ata Final, Folha de
Aprovação, declaração de participação e a situação da E2 da US-28; e o ponto de chamada da
feat-09 na liberação do resultado (spec 008, research A10; contrato §2 de
specs/008-avaliacao-resultados/contracts/servicos-avaliacoes.md).

Os documentos são PDFs sob demanda (pdf.gerar_pdf, em memória): nada é gravado em disco nem no
banco (SC-003). Os dados vêm do resultado congelado na liberação
(services_avaliacoes.resultado_da_sessao) e da data da defesa (def_data); o Coordenador e as
titulações são lidos no momento do download (Clarifications).

STUBS até as fases seguintes da feat-09 (tasks T043 e T044), sem mudar a assinatura nem o ponto
de chamada:
- ao_liberar_resultado(sessao): registrado por services_avaliacoes.liberar_resultado com
  transaction.on_commit(..., robust=True), depois de gravada a liberação; enviará as
  declarações de participação por e-mail (RBN-DEF-08.3), com o trabalho pesado numa thread e a
  falha só no log (D9).
- declaracao_disponivel(sessao, usuario): decide o botão Declaração de Minhas bancas.

[US-27][US-25][US-28][US-30][RBN-DEF-06.4][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-08.3]
[RBN-DEF-05.4][RBN-CAD-13.1]
"""

import base64
import logging

from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.crypto import salted_hmac

from sigtcc.apps.cadastro import services
from sigtcc.apps.cadastro.models import Coordenadores
from sigtcc.apps.cadastro.permissoes import especializacao
from sigtcc.apps.defesa import mensagens, services_avaliacoes, services_defesa
from sigtcc.apps.defesa.choices import PapelBanca
from sigtcc.apps.defesa.models import BancaDefesa

logger = logging.getLogger("sigtcc.defesa")


def ao_liberar_resultado(sessao):
    """STUB: só registra em log que a liberação pediu o envio das declarações (feat-09, T043).
    [US-27][US-30][RBN-DEF-06.4][RBN-DEF-08.3]
    """
    logger.info("Liberação do resultado: declarações pedidas (stub), sessão %s", sessao.pk)


def declaracao_disponivel(sessao, usuario):
    """STUB: a declaração de participação ainda não existe (feat-09, T044); sempre False.
    [US-25][US-30][RBN-DEF-05.4][RBN-DEF-08.3]
    """
    return False


# =============================================================================================
# Situação da Ata Final: E2 da US-28 (research B5; Q-140)
# =============================================================================================

# Motivos da E2: o curso da turma não tem Coordenador de Curso, ou o Coordenador nunca
# cadastrou a assinatura no perfil (caminho vazio). [US-28][RBN-DEF-07.1][RBN-CAD-13.1]
SEM_COORDENADOR = "sem_coordenador"
SEM_ASSINATURA = "sem_assinatura"


def _coordenador_do_curso(sessao):
    """Linha de Coordenadores do curso da turma do TCC da sessão (com o docente e a conta), ou
    None. [US-28][RBN-DEF-07.1][RBN-CAD-13.1]
    """
    return (
        Coordenadores.objects.select_related("cor_doc__doc")
        .filter(cor_cur_id=sessao.def_tcc.tcc_tur.tur_cur_id)
        .first()
    )


def situacao_da_ata(sessao):
    """None quando a Ata Final pode ser gerada; senão o motivo da E2 (FR-006): SEM_COORDENADOR
    (o curso da turma não tem linha em Coordenadores) ou SEM_ASSINATURA
    (services.caminho_da_assinatura do Coordenador vazio). Caminho gravado com o arquivo
    ausente do disco: None, e a Ata sai sem a imagem (Q-140).
    [US-28][RBN-DEF-07.1][RBN-CAD-13.1]
    """
    coordenador = _coordenador_do_curso(sessao)
    if coordenador is None:
        return SEM_COORDENADOR
    if not services.caminho_da_assinatura(coordenador.cor_doc.doc):
        return SEM_ASSINATURA
    return None


def _imagem_existente(caminho):
    """Endereço da imagem de assinatura para o template do PDF (MEDIA_URL + caminho, resolvido
    pelo pdf.link_callback dentro do MEDIA_ROOT), ou None quando não há caminho ou o arquivo não
    existe no armazenamento (registrado no log); com None, o template não emite <img> e o
    xhtml2pdf nunca recebe recurso inexistente (research B4; revisão M-08; Q-140).
    [US-28][US-30][RBN-DEF-07.1][RBN-DEF-07.2]
    """
    if not caminho:
        return None
    if not default_storage.exists(caminho):
        logger.warning("Imagem de assinatura ausente no armazenamento: %s", caminho)
        return None
    return f"{settings.MEDIA_URL}{caminho}"


# =============================================================================================
# Código de validação da declaração (research B6; RBN-DEF-08.3; dicionário, regra 4)
# =============================================================================================

TAMANHO_DO_CODIGO = 16


def codigo_de_validacao(sessao, usuario):
    """Código de validação da declaração do membro na sessão (FR-020): HMAC-SHA256 com a
    SECRET_KEY sobre "<def_id>:<usu_id>", em Base32 (A-Z e 2-7) sem o "=", nos 16 primeiros
    caracteres. Determinístico (a segunda via sai igual; SC-004), diferente por membro e por
    sessão, sem armazenamento. [US-30][RBN-DEF-08.3]
    """
    resumo = salted_hmac(
        "sigtcc.declaracao", f"{sessao.pk}:{usuario.pk}", algorithm="sha256"
    ).digest()
    return base64.b32encode(resumo).decode("ascii").rstrip("=")[:TAMANHO_DO_CODIGO]


def codigo_formatado(codigo):
    """O código em quatro grupos de 4 separados por espaço (só na apresentação).
    [US-30][RBN-DEF-08.3]
    """
    return " ".join(codigo[inicio : inicio + 4] for inicio in range(0, len(codigo), 4))


# =============================================================================================
# Datas por extenso e formatação (research B4)
# =============================================================================================

# Tabela fixa em português, sem depender do locale do servidor. [US-28][RBN-DEF-07.2]
_MESES = (
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
)


def _mes_por_extenso(mes):
    """Nome do mês (1 a 12) em português, em minúsculas. [US-28][RBN-DEF-07.2]"""
    return _MESES[mes - 1]


def _data_curta(data):
    """Data em DD/MM/AAAA. [US-28][US-30][RBN-DEF-07.1][RBN-DEF-08.3]"""
    return data.strftime("%d/%m/%Y")


def _data_por_extenso(data):
    """Data em "DD de mês de AAAA". [US-28][RBN-DEF-07.2]"""
    return f"{data.day:02d} de {_mes_por_extenso(data.month)} de {data.year}"


def _nota(valor):
    """Nota com uma casa e vírgula decimal (ex.: "8,0"), ou None. [US-28][RBN-DEF-07.1]"""
    return None if valor is None else f"{valor:.1f}".replace(".", ",")


# =============================================================================================
# Folha de Aprovação: quando existe (FR-003, FR-004)
# =============================================================================================


def folha_aplicavel(sessao):
    """None quando a Folha de Aprovação existe (TCC 2 com parecer Aprovado ou Aprovado com
    Correções); senão a mensagem da recusa: "A Folha de Aprovação não se aplica ao TCC 1" ou
    "Documento indisponível para trabalhos reprovados" (US-28 cenários 12 e 13).
    [US-28][RBN-DEF-07.2][RBN-DEF-07.3]
    """
    if not services_avaliacoes.e_tcc_2(sessao):
        return mensagens.FOLHA_NAO_SE_APLICA
    if sessao.def_parecer in services_avaliacoes.PARECERES_DE_TCC_2:
        return None
    return mensagens.FOLHA_REPROVADO


# =============================================================================================
# Dados da Ata Final, da Folha de Aprovação e da declaração (research B4 e B6)
# =============================================================================================

# Cabeçalho textual dos documentos (não há logotipo oficial em static/img/).
# [US-28][US-30][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-08.3]
CABECALHO = "Universidade do Estado do Amazonas – Escola Superior de Tecnologia"
TITULO_DA_ATA = "Ata Final de Avaliação de Trabalho de Conclusão de Curso {etapa}"
# Texto exato da US-28 e da matriz (RBN-DEF-07.1). [US-28][RBN-DEF-07.1]
OBSERVACAO_QUALIS = (
    "Em caso de artigos, se Qualis A ou B, a nota final será o valor máximo entre 6,0 e a média "
    "dos avaliadores"
)
# Frase da Folha de Aprovação (FR-002). [US-28][RBN-DEF-07.2]
FRASE_DA_FOLHA = (
    "Trabalho de Conclusão de Curso defendido e aprovado pela banca avaliadora constituída pelos "
    "professores:"
)
LOCAL_DA_FOLHA = "Manaus"
# Papéis impressos na Folha, na ordem Orientador, 1º e 2º Avaliador (FR-002).
# [US-28][RBN-DEF-07.2]
PAPEIS_DA_FOLHA = ("Presidente", "Avaliador", "Avaliador")


def _titulacao(usuario):
    """Titulação lida no momento (doc_titulacao do Docente ou mem_titulacao do Membro
    Externo), ou "" se a conta não tiver nenhuma das duas. [US-28][US-30][RBN-DEF-07.1]
    """
    docente = especializacao(usuario, "docentes")
    if docente is not None:
        return docente.get_doc_titulacao_display()
    externo = especializacao(usuario, "membrosexternos")
    if externo is not None:
        return externo.get_mem_titulacao_display()
    return ""


def _membros_do_documento(sessao):
    """Os 3 membros efetivos (services_defesa.membros_efetivos), na ordem Orientador, 1º e 2º
    Avaliador, cada um com o papel da linha da banca (o suplente acionado ocupa o papel do
    substituído), nome, titulação lida no momento e a assinatura da cópia gravada no envio da
    avaliação (ban_assinatura_path, por _imagem_existente). Só valores simples.
    [US-28][US-30][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-02.2]
    """
    membros = services_defesa.membros_efetivos(sessao)
    linhas = {
        linha.ban_usu_id: linha
        for linha in BancaDefesa.objects.filter(
            ban_def=sessao, ban_usu_id__in=[membro.pk for membro in membros]
        )
    }
    return [
        {
            "usu_id": membro.pk,
            "papel": PapelBanca(linhas[membro.pk].ban_papel).label,
            "nome": membro.usu_nome,
            "titulacao": _titulacao(membro),
            "assinatura": _imagem_existente(linhas[membro.pk].ban_assinatura_path),
        }
        for membro in membros
    ]


def _dados_comuns(sessao):
    """Cabeçalho, curso, aluno, título do trabalho e data da defesa (def_data; P12).
    [US-28][US-30][RBN-DEF-07.1][RBN-DEF-07.2][RBN-DEF-08.3]
    """
    tcc = sessao.def_tcc
    return {
        "def_id": sessao.pk,
        "cabecalho": CABECALHO,
        "curso": tcc.tcc_tur.tur_cur.cur_nome,
        "aluno": tcc.tcc_alu.alu.usu_nome,
        "titulo": tcc.tcc_titulo,
        "data_defesa": _data_curta(sessao.def_data),
    }


def dados_da_ata(sessao):
    """Contexto da Ata Final (FR-001; FR-008), só com valores simples e só com o resultado
    liberado: cabeçalho e curso; título "Ata Final de Avaliação de Trabalho de Conclusão de
    Curso I" ou "II" (pela etapa); aluno e título; os 3 membros efetivos com titulação, papel,
    nota individual e assinatura; nota final; parecer; a observação do Qualis quando a nota foi
    elevada; data da defesa; e o nome e a assinatura do Coordenador de Curso lidos agora
    (com o arquivo ausente, sem a imagem; Q-140). Quem chama confere situacao_da_ata antes.
    [US-28][RBN-DEF-07.1][RBN-DEF-06.5][RBN-CAD-13.1]
    """
    resultado = services_avaliacoes.resultado_da_sessao(sessao)
    if resultado is None:
        raise ValueError("A Ata Final só existe depois da liberação do resultado")
    notas = {item["membro"].pk: item["nota_individual"] for item in resultado["avaliadores"]}
    membros = [
        {**membro, "nota": _nota(notas.get(membro["usu_id"]))}
        for membro in _membros_do_documento(sessao)
    ]
    coordenador = _coordenador_do_curso(sessao)
    dados_coordenador = None
    if coordenador is not None:
        conta = coordenador.cor_doc.doc
        dados_coordenador = {
            "nome": conta.usu_nome,
            "assinatura": _imagem_existente(services.caminho_da_assinatura(conta)),
        }
    etapa = "II" if services_avaliacoes.e_tcc_2(sessao) else "I"
    return {
        **_dados_comuns(sessao),
        "titulo_documento": TITULO_DA_ATA.format(etapa=etapa),
        "membros": membros,
        "nota_final": _nota(resultado["nota_final"]),
        "parecer": resultado["parecer"],
        "observacao_qualis": OBSERVACAO_QUALIS if resultado["elevada_pelo_qualis"] else None,
        "coordenador": dados_coordenador,
    }


def dados_da_folha(sessao):
    """Contexto da Folha de Aprovação (FR-002; FR-008), só com valores simples e sem nenhuma
    nota nem média (SC-001): cabeçalho e curso; título; aluno; a frase da banca; os 3 membros
    com titulação, papel (Presidente, Avaliador e Avaliador) e assinatura; e "Manaus, DD de mês
    de AAAA" com a data da defesa. Quem chama confere folha_aplicavel antes.
    [US-28][RBN-DEF-07.2]
    """
    if sessao.def_data_liberacao_resultado is None:
        raise ValueError("A Folha de Aprovação só existe depois da liberação do resultado")
    membros = [
        {
            "papel": papel,
            "nome": membro["nome"],
            "titulacao": membro["titulacao"],
            "assinatura": membro["assinatura"],
        }
        for papel, membro in zip(PAPEIS_DA_FOLHA, _membros_do_documento(sessao))
    ]
    return {
        **_dados_comuns(sessao),
        "frase": FRASE_DA_FOLHA,
        "membros": membros,
        "local_e_data": f"{LOCAL_DA_FOLHA}, {_data_por_extenso(sessao.def_data)}",
    }


def dados_da_declaracao(sessao, usuario):
    """Contexto da declaração de participação do membro efetivo (US-30 D; FR-019 e FR-020; MX-05),
    o mesmo no e-mail e na segunda via: nome, titulação, papel na banca, aluno, título, curso,
    data da defesa, a referência "Defesa nº {def_id}", o código de validação formatado e o texto
    da declaração. Só para membro efetivo (senão ValueError); quem chama confere a permissão.
    [US-30][RBN-DEF-08.3]
    """
    linha = BancaDefesa.objects.filter(
        ban_def=sessao, ban_usu_id=usuario.pk, ban_papel__in=services_defesa.PAPEIS_TITULARES
    ).first()
    if linha is None:
        raise ValueError("A declaração só existe para os membros efetivos da banca")
    comuns = _dados_comuns(sessao)
    codigo = codigo_formatado(codigo_de_validacao(sessao, usuario))
    dados = {
        "nome": usuario.usu_nome,
        "titulacao": _titulacao(usuario),
        "papel": PapelBanca(linha.ban_papel).label,
        "aluno": comuns["aluno"],
        "titulo": comuns["titulo"],
        "curso": comuns["curso"],
        "data": comuns["data_defesa"],
        "codigo": codigo,
    }
    return {
        **comuns,
        **dados,
        "referencia": f"Defesa nº {sessao.pk}",
        "texto": mensagens.MX05_DECLARACAO.format(**dados),
    }
