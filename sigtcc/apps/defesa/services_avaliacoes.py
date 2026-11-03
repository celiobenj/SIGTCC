"""Regras da avaliação da banca e do resultado da defesa (spec 008, research A1 a A8): estado da
avaliação, cálculo das notas, descarte, sigilo, rascunho, envio assinado, reabertura, parecer,
liberação e resultado para o aluno.

Contrato em specs/008-avaliacao-resultados/contracts/servicos-avaliacoes.md. Cumpre o contrato da
spec 007: nunca grava def_status nem Historico_Defesas direto (só por
services_defesa.transicionar_status), nunca grava tcc_status nem Historico_Status_TCC direto
(só por services_turmas.atualizar_status_tcc) e nunca cria sessão. Cálculo sempre em Decimal,
com uma casa e ROUND_HALF_UP (research A3).

[US-25][US-26][US-27][RBN-DEF-04.1][RBN-DEF-05.1][RBN-DEF-05.2][RBN-DEF-05.3][RBN-DEF-06.1]
[RBN-DEF-06.2][RBN-DEF-06.3][RBN-DEF-06.4][RBN-DEF-06.6][RBN-DEF-06.8]
"""

import logging
import secrets
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Exists, OuterRef, Subquery
from django.utils import timezone

from sigtcc.apps.cadastro import services, services_artigos
from sigtcc.apps.cadastro.choices import DescricaoTurma, TipoEntrega
from sigtcc.apps.cadastro.models import HistoricoEnviosEntregas
from sigtcc.apps.cadastro.services_turmas import STATUS_SESSAO_ATIVA
from sigtcc.apps.defesa import mensagens, permissoes_defesa, services_defesa, services_documentos
from sigtcc.apps.defesa.choices import (
    ComponenteCriterio,
    Conceito,
    PapelBanca,
    Parecer,
    StatusSessao,
)
from sigtcc.apps.defesa.models import Avaliacoes, BancaDefesa, Criterios, Defesas

logger = logging.getLogger("sigtcc.defesa")

# Rótulos do estado da avaliação de cada membro (RBN-DEF-06.8; dicionário 3.6.4).
# [US-25][US-27][RBN-DEF-06.8]
NAO_AVALIOU = "Não avaliou"
RASCUNHO_SALVO = "Rascunho salvo"
ENVIADA = "Enviada"

# Uma casa decimal e arredondamento comercial (a partir de 0,05 arredonda para cima).
# [US-27][RBN-DEF-06.1][RBN-DEF-06.2]
UMA_CASA = Decimal("0.1")
NOTA_MINIMA = Decimal("6.0")
TOTAL_DE_CRITERIOS = 9
D0 = Decimal("0")


def arredondar(valor):
    """Uma casa decimal com ROUND_HALF_UP, sempre em Decimal (research A3).
    [US-27][RBN-DEF-06.1][RBN-DEF-06.2]
    """
    return Decimal(valor).quantize(UMA_CASA, rounding=ROUND_HALF_UP)


# =============================================================================================
# Estado da avaliação (research A2; dicionário 3.6.4)
# =============================================================================================


def _estado(data_envio, tem_notas):
    """Rótulo do estado pela regra do dicionário: Enviada (com data de envio), Rascunho salvo
    (com linhas em Avaliacoes) ou Não avaliou. [US-25][US-27][RBN-DEF-06.8]
    """
    if data_envio is not None:
        return ENVIADA
    return RASCUNHO_SALVO if tem_notas else NAO_AVALIOU


def _tem_notas():
    """Subconsulta: a linha de BancaDefesa tem linhas em Avaliacoes. [US-25][RBN-DEF-06.8]"""
    return Exists(
        Avaliacoes.objects.filter(
            ava_def_id=OuterRef("ban_def_id"), ava_usu_id=OuterRef("ban_usu_id")
        )
    )


def estado_da_avaliacao(sessao, membro):
    """ "Não avaliou", "Rascunho salvo" ou "Enviada" do membro na sessão (contrato §1).
    Membro fora da banca: "Não avaliou". [US-25][US-27][RBN-DEF-06.8]
    """
    linha = (
        BancaDefesa.objects.filter(ban_def=sessao, ban_usu=membro)
        .annotate(tem_notas=_tem_notas())
        .values("ban_data_envio", "tem_notas")
        .first()
    )
    if linha is None:
        return NAO_AVALIOU
    return _estado(linha["ban_data_envio"], linha["tem_notas"])


def estados_da_banca(sessao):
    """Estado de cada um dos 3 membros efetivos (Orientador, 1º e 2º Avaliador, com o suplente
    acionado no lugar do ausente), na ordem da banca, numa consulta só: lista de dicionários com
    membro, papel, estado e data_envio. O Suplente não acionado não entra (revisão I-06).
    [US-25][US-27][RBN-DEF-06.6][RBN-DEF-06.8]
    """
    linhas = (
        BancaDefesa.objects.select_related("ban_usu")
        .filter(ban_def=sessao, ban_papel__in=services_defesa.PAPEIS_TITULARES)
        .annotate(tem_notas=_tem_notas())
    )
    ordenadas = sorted(
        linhas, key=lambda linha: services_defesa.PAPEIS_TITULARES.index(linha.ban_papel)
    )
    return [
        {
            "membro": linha.ban_usu,
            "papel": linha.ban_papel,
            "estado": _estado(linha.ban_data_envio, linha.tem_notas),
            "data_envio": linha.ban_data_envio,
        }
        for linha in ordenadas
    ]


def tres_envios(estados):
    """Os 3 membros efetivos enviaram (quórum, RBN-DEF-06.6). [US-27][RBN-DEF-06.6]"""
    return len(estados) == 3 and all(item["estado"] == ENVIADA for item in estados)


# =============================================================================================
# Cálculo das notas (research A3; RBN-DEF-06.1 e 06.2)
# =============================================================================================


def _soma_ponderada(linhas):
    """Σ(nota × peso) / 10 arredondada, a partir de pares (nota, peso). [US-27][RBN-DEF-06.1]"""
    total = sum((Decimal(nota) * Decimal(peso) for nota, peso in linhas), Decimal("0"))
    return arredondar(total / Decimal("10"))


def nota_individual(sessao, membro):
    """Nota individual do membro: Σ(ava_nota × cri_peso) / 10, uma casa, ROUND_HALF_UP, com os
    pesos de Criterios (nunca constante no código). None enquanto o membro não tiver os 9
    critérios lançados. [US-25][US-27][RBN-DEF-06.1]
    """
    linhas = list(
        Avaliacoes.objects.filter(ava_def=sessao, ava_usu=membro).values_list(
            "ava_nota", "ava_cri__cri_peso"
        )
    )
    if len(linhas) != TOTAL_DE_CRITERIOS:
        return None
    return _soma_ponderada(linhas)


def _media(notas):
    """Média simples das notas individuais já arredondadas, arredondada. [US-27][RBN-DEF-06.2]"""
    return arredondar(sum(notas, Decimal("0")) / Decimal(len(notas)))


def calculo(sessao, tcc=None):
    """Cálculo completo com os 3 envios: notas individuais dos membros efetivos (na ordem da
    banca), média, se um artigo Qualis A ou B homologado elevou a nota e a nota final
    (max(6,0, média) com o artigo; RBN-DEF-06.2). None sem os 3 envios. A homologação é a
    vigente agora: na liberação, quem chama já travou o TCC.
    [US-27][RBN-DEF-06.1][RBN-DEF-06.2][RBN-DEF-06.6]
    """
    estados = estados_da_banca(sessao)
    if not tres_envios(estados):
        return None
    individuais = [nota_individual(sessao, item["membro"]) for item in estados]
    if any(nota is None for nota in individuais):
        return None
    media = _media(individuais)
    tem_artigo = services_artigos.tem_artigo_homologado_qualis_ab(tcc or sessao.def_tcc)
    final = max(NOTA_MINIMA, media) if tem_artigo else media
    return {
        "individuais": list(zip(estados, individuais)),
        "media": media,
        "nota_final": final,
        "elevada_pelo_qualis": final > media,
    }


def nota_final(sessao, tcc=None):
    """Nota final (contrato §1): média das 3 notas individuais já arredondadas, uma casa,
    ROUND_HALF_UP; com artigo Qualis A ou B homologado, max(6,0, média). None sem os 3 envios.
    Só os membros efetivos entram (revisão I-06). [US-27][RBN-DEF-06.1][RBN-DEF-06.2]
    """
    resultado = calculo(sessao, tcc)
    return resultado["nota_final"] if resultado else None


# =============================================================================================
# Descarte e volta a rascunho (contrato §1; FR-034, FR-035; D2, D3 revista, D16)
# =============================================================================================


def _apagar_depois_do_commit(caminhos):
    """Apaga as cópias das imagens de assinatura só depois do commit (se a transação desfizer,
    os arquivos continuam com as linhas que os apontam). [US-26][RBN-DEF-05.2][research A5]
    """
    caminhos = [caminho for caminho in caminhos if caminho]
    if not caminhos:
        return

    def apagar():
        """Apaga cada cópia; arquivo já ausente (deploy) é ignorado. [US-26][research A5]"""
        for caminho in caminhos:
            try:
                default_storage.delete(caminho)
            except OSError:
                logger.warning("Cópia de assinatura não apagada: %s", caminho)

    transaction.on_commit(apagar)


def _limpar_envio(linhas_da_banca):
    """Limpa a assinatura e a data de envio das linhas de BancaDefesa e agenda a remoção das
    cópias das imagens depois do commit. [US-25][US-26][RBN-DEF-05.2][RBN-DEF-06.6]
    """
    caminhos = list(
        linhas_da_banca.filter(ban_assinatura_path__isnull=False).values_list(
            "ban_assinatura_path", flat=True
        )
    )
    linhas_da_banca.update(ban_assinatura_path=None, ban_data_envio=None)
    _apagar_depois_do_commit(caminhos)


def _limpar_parecer(sessao):
    """Limpa o parecer escolhido: os 3 envios deixaram de estar completos (D3 revista, Q-135).
    [US-27][RBN-DEF-06.1][RBN-DEF-06.3]
    """
    Defesas.objects.filter(pk=sessao.pk).update(def_parecer=None)
    sessao.def_parecer = None


def descartar_avaliacoes(sessao, membro=None):
    """Descarta as avaliações do membro (ou de todos, com membro=None), na transação de quem
    chama (contrato §1; substitui o stub da spec 007, Q-125): apaga as linhas de Avaliacoes,
    limpa a assinatura e a data de envio da linha de BancaDefesa quando ela ainda existe (por
    isso a spec 007 chama antes do delete() da linha), apaga a cópia da imagem depois do commit
    e limpa o parecer escolhido (D3 revista). Chamado pela spec 007 no cancelamento, na
    alteração da banca (quem sai ou passa a Suplente) e no acionamento do suplente.
    [US-23][US-24][US-27][RBN-DEF-02.2][RBN-DEF-02.4][RBN-DEF-03.3][FR-034]
    """
    avaliacoes = Avaliacoes.objects.filter(ava_def=sessao)
    banca = BancaDefesa.objects.filter(ban_def=sessao)
    if membro is not None:
        avaliacoes = avaliacoes.filter(ava_usu=membro)
        banca = banca.filter(ban_usu=membro)
    avaliacoes.delete()
    _limpar_envio(banca)
    _limpar_parecer(sessao)
    logger.info(
        "Avaliações descartadas: sessão %s, membro %s",
        sessao.pk,
        membro.pk if membro is not None else "todos",
    )


def voltar_envios_a_rascunho(sessao):
    """Reagendamento de sessão "Em Andamento" (D2; FR-035): mantém as notas e devolve todas as
    avaliações enviadas a "Rascunho salvo", limpando a data de envio, a assinatura (cópia apagada
    depois do commit) e o parecer escolhido, na transação do reagendamento. Inofensivo numa
    sessão "Agendada" ou "Reagendada" (sem envios).
    [US-24][US-27][RBN-DEF-03.3][RBN-DEF-05.1][RBN-DEF-06.6][FR-035]
    """
    _limpar_envio(BancaDefesa.objects.filter(ban_def=sessao))
    _limpar_parecer(sessao)


# =============================================================================================
# Etapa e parecer (RBN-DEF-06.3)
# =============================================================================================


def e_tcc_2(sessao):
    """A sessão é de TCC 2 (pela turma do TCC). [US-27][RBN-DEF-06.3][RBN-DEF-06.5]"""
    return sessao.def_tcc.tcc_tur.tur_descricao == DescricaoTurma.TCC_2


PARECERES_DE_TCC_2 = (Parecer.APROVADO, Parecer.APROVADO_COM_CORRECOES)


def parecer_automatico(sessao, nota):
    """Parecer pela nota final e pela etapa (RBN-DEF-06.3): abaixo de 6,0, Reprovado (fixado
    pelo sistema, ignorando um def_parecer gravado); 6,0 ou mais em TCC 1, Aprovado para TCC 2;
    6,0 ou mais em TCC 2, o parecer registrado pelo Orientador (Aprovado ou Aprovado com
    Correções) ou None enquanto não houver. [US-27][RBN-DEF-06.3]
    """
    if nota is None:
        return None
    if nota < NOTA_MINIMA:
        return Parecer.REPROVADO
    if not e_tcc_2(sessao):
        return Parecer.APROVADO_PARA_TCC_2
    return sessao.def_parecer if sessao.def_parecer in PARECERES_DE_TCC_2 else None


# =============================================================================================
# Notas por critério e por avaliador e sigilo (research A7; RBN-DEF-06.8)
# =============================================================================================


def _criterios():
    """Os 9 critérios na ordem da carga (cri_id). [US-25][RBN-DEF-04.1][RBN-DEF-04.2]"""
    return list(Criterios.objects.order_by("cri_id"))


def notas_por_avaliador(sessao, criterios=None):
    """Para cada membro efetivo (na ordem da banca): membro, papel, nota individual e as linhas
    de cada critério (critério, conceito, nota e observações), numa consulta para as notas.
    Sem filtro de sigilo: quem chama decide o que mostrar (visao_da_avaliacao).
    [US-27][RBN-DEF-06.1][RBN-DEF-06.8]
    """
    criterios = criterios if criterios is not None else _criterios()
    estados = estados_da_banca(sessao)
    notas = {}
    for avaliacao in Avaliacoes.objects.filter(
        ava_def=sessao, ava_usu_id__in=[item["membro"].pk for item in estados]
    ):
        notas[(avaliacao.ava_usu_id, avaliacao.ava_cri_id)] = avaliacao
    avaliadores = []
    for item in estados:
        linhas = [(criterio, notas.get((item["membro"].pk, criterio.pk))) for criterio in criterios]
        completas = [(av.ava_nota, criterio.cri_peso) for criterio, av in linhas if av]
        individual = _soma_ponderada(completas) if len(completas) == len(criterios) else None
        avaliadores.append({**item, "linhas": linhas, "nota_individual": individual})
    return avaliadores


def _sem_observacoes(linhas):
    """As mesmas linhas sem o texto das Observações (D7: visíveis só ao autor).
    [US-27][RBN-DEF-06.8]
    """
    return [
        (criterio, {"conceito": av.ava_conceito, "nota": av.ava_nota} if av else None)
        for criterio, av in linhas
    ]


def _com_observacoes(linhas):
    """As linhas do próprio avaliador, com as Observações. [US-25][US-27][RBN-DEF-06.8]"""
    return [
        (
            criterio,
            (
                {
                    "conceito": av.ava_conceito,
                    "nota": av.ava_nota,
                    "observacoes": av.ava_observacoes,
                }
                if av
                else None
            ),
        )
        for criterio, av in linhas
    ]


def visao_da_avaliacao(usuario, sessao):
    """O que o usuário pode ver da avaliação da sessão (research A7; RBN-DEF-06.8; D7). Única
    fonte do sigilo: views e templates só exibem o que vem aqui. Pressupõe que o usuário já pode
    abrir a sessão (permissoes_defesa.pode_ver_sessao).

    - Antes da liberação: o membro efetivo vê a própria avaliação (com as Observações) e o
      estado de envio dos colegas; o Orientador (Presidente) vê também a nota final e o parecer
      preliminar, só com os 3 envios. Suplente não acionado, Professor da Disciplina, Secretaria
      e Aluno não veem nada do bloco (nem os estados). Sessão Cancelada: nada.
    - Depois da liberação: todos veem as notas por critério e por avaliador, a nota final e o
      parecer; as Observações, só o autor.
    O papel efetivo na banca prevalece sobre Professor da Disciplina e Secretaria (revisão I-05).
    [US-25][US-27][RBN-DEF-06.8][RBN-DEF-06.6][FR-031][FR-032]
    """
    linha = BancaDefesa.objects.filter(ban_def=sessao, ban_usu_id=usuario.pk).first()
    papel = linha.ban_papel if linha is not None else None
    efetivo = papel in services_defesa.PAPEIS_TITULARES
    visao = {
        "papel": papel,
        "membro_efetivo": efetivo,
        "orientador": papel == PapelBanca.ORIENTADOR_PRESIDENTE,
        "liberado": sessao.def_data_liberacao_resultado is not None,
        "mostra_bloco": False,
        "estados": [],
        "propria": None,
        "avaliadores": [],
        "nota_final": None,
        "parecer": None,
    }
    if visao["liberado"]:
        avaliadores = []
        for item in notas_por_avaliador(sessao):
            proprio = item["membro"].pk == usuario.pk
            linhas = (
                _com_observacoes(item["linhas"]) if proprio else _sem_observacoes(item["linhas"])
            )
            avaliadores.append({**item, "linhas": linhas, "proprio": proprio})
        visao.update(
            mostra_bloco=True,
            avaliadores=avaliadores,
            nota_final=sessao.def_nota_final,
            parecer=sessao.def_parecer,
        )
        return visao
    if not efetivo or sessao.def_status == StatusSessao.CANCELADA:
        return visao
    avaliadores = notas_por_avaliador(sessao)
    proprio = next(item for item in avaliadores if item["membro"].pk == usuario.pk)
    visao.update(
        mostra_bloco=True,
        estados=[
            {key: item[key] for key in ("membro", "papel", "estado", "data_envio")}
            for item in avaliadores
        ],
        propria={
            "estado": proprio["estado"],
            "nota_individual": proprio["nota_individual"],
            "linhas": _com_observacoes(proprio["linhas"]),
        },
    )
    if visao["orientador"]:
        resultado = calculo(sessao)
        if resultado is not None:
            visao["nota_final"] = resultado["nota_final"]
            visao["parecer"] = parecer_automatico(sessao, resultado["nota_final"])
    return visao


# =============================================================================================
# Critérios e Minhas bancas (research A8; RBN-DEF-04.2, RBN-DEF-05.4)
# =============================================================================================


def criterios_por_componente():
    """Os 9 critérios agrupados por componente, com a soma dos pesos de cada parte e o total
    (FR-002): [(componente, [critérios], soma)], total. Só leitura. [US-25][RBN-DEF-04.1]
    [RBN-DEF-04.2]
    """
    todos = _criterios()
    partes = []
    for componente in ComponenteCriterio:
        da_parte = [criterio for criterio in todos if criterio.cri_componente == componente]
        partes.append((componente.label, da_parte, sum((c.cri_peso for c in da_parte), D0)))
    return partes, sum((c.cri_peso for c in todos), D0)


def _documento_da_sessao():
    """Subconsulta: link mais recente do Documento para Defesa do aluno na turma do TCC, pela
    mesma regra de services_defesa.link_do_documento (entrega de Data Limite mais recente, envio
    mais recente), numa consulta só para toda a lista (revisão M-12). [US-25][RBN-DEF-05.4]
    [RBN-CAD-09.2]
    """
    return Subquery(
        HistoricoEnviosEntregas.objects.filter(
            hen_ent__ent_alu_id=OuterRef("ban_def__def_tcc__tcc_alu_id"),
            hen_ent__ent_tma__tma_tur_id=OuterRef("ban_def__def_tcc__tcc_tur_id"),
            hen_ent__ent_tma__tma_tipo=TipoEntrega.DOCUMENTO_PARA_DEFESA,
        )
        .order_by(
            "-hen_ent__ent_tma__tma_data_limite",
            "-hen_ent__ent_tma_id",
            "-hen_data_envio",
            "-hen_id",
        )
        .values("hen_link")[:1]
    )


def minhas_bancas(usuario):
    """Tela Minhas bancas (FR-003 a FR-006): as linhas de BancaDefesa do usuário (inclusive como
    Suplente), sem as sessões "Cancelada", em ordem cronológica, com sessão, TCC, aluno e turma
    carregados, o estado da avaliação, o destaque de pendência (só membro efetivo, sessão
    Agendada, Reagendada ou Em Andamento e avaliação ainda não Enviada; D11), o link do Documento
    para Defesa e se a declaração existe (feat-09). Roda antes o início automático das sessões
    (research A8). Sem consulta por linha. [US-25][RBN-DEF-05.4][RBN-DEF-08.3][FR-003 a FR-006]
    """
    services_defesa.iniciar_sessoes_vencidas()
    linhas = (
        BancaDefesa.objects.filter(ban_usu_id=usuario.pk)
        .exclude(ban_def__def_status=StatusSessao.CANCELADA)
        .select_related("ban_def__def_tcc__tcc_alu__alu", "ban_def__def_tcc__tcc_tur")
        .annotate(tem_notas=_tem_notas(), documento=_documento_da_sessao())
        .order_by("ban_def__def_data", "ban_def__def_h_inicio", "ban_def_id")
    )
    resultado = []
    for linha in linhas:
        sessao = linha.ban_def
        efetivo = linha.ban_papel in services_defesa.PAPEIS_TITULARES
        estado = _estado(linha.ban_data_envio, linha.tem_notas)
        resultado.append(
            {
                "sessao": sessao,
                "papel": linha.ban_papel,
                "membro_efetivo": efetivo,
                "estado": estado if efetivo else None,
                "pendente": efetivo
                and sessao.def_status in STATUS_SESSAO_ATIVA
                and estado != ENVIADA,
                "documento": linha.documento,
                "declaracao": sessao.def_status == StatusSessao.REALIZADA
                and services_documentos.declaracao_disponivel(sessao, usuario),
            }
        )
    return resultado


# =============================================================================================
# Formulário Avaliação: rascunho, envio assinado e reabertura (research A4, A5; US-25, US-26)
# =============================================================================================

# Faixa da nota de cada conceito (RBN-DEF-05.2; FR-009). [US-25][RBN-DEF-05.2]
FAIXAS = {
    Conceito.EXEMPLAR: (Decimal("8.0"), Decimal("10.0")),
    Conceito.COMPETENTE: (Decimal("6.0"), Decimal("7.9")),
    Conceito.NECESSITA_DE_TRABALHO: (Decimal("0.0"), Decimal("5.9")),
}

# Maior imagem de assinatura aceita, em pixels (MA-14; research A5, revisão I-11). [US-26]
LARGURA_MAXIMA, ALTURA_MAXIMA = 2000, 1000

# Status em que só a Parte Escrita pode ser avaliada e salva (RBN-DEF-05.1). [US-25]
STATUS_ANTES_DA_SESSAO = (StatusSessao.AGENDADA, StatusSessao.REAGENDADA)


class ErroAvaliacao(Exception):
    """Ação recusada com a mensagem exata da US ou da tabela MA; `campo` aponta o que destacar
    ("assinatura") e `pendentes`, os critérios incompletos (cri_id). Nada é gravado.
    [US-25][US-26][US-27][RBN-DEF-05.1][RBN-DEF-05.2][RBN-DEF-06.4]
    """

    def __init__(self, mensagem, campo=None, pendentes=()):
        """Guarda a mensagem, o campo e os critérios pendentes. [US-25][US-26][US-27]"""
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.campo = campo
        self.pendentes = tuple(pendentes)


class AcessoRestrito(ErroAvaliacao):
    """Quem não é membro efetivo, ou sessão Cancelada (FR-007, FR-036): a view responde 403 com
    "Acesso restrito aos membros avaliadores da banca". [US-25][US-26][RBN-DEF-05.3]
    """

    def __init__(self):
        """Mensagem fixa da US-25 E8. [US-25][RBN-DEF-05.3]"""
        super().__init__(mensagens.ACESSO_RESTRITO)


@dataclass
class Assinatura:
    """Escolha da assinatura no envio (US-26): o arquivo anexado (já conferido pelo formulário
    quanto ao tamanho e ao formato, com o `tipo` "png" ou "jpg"), ou a do perfil, e se a imagem
    anexada também vai para o perfil. [US-26][RBN-DEF-05.2]
    """

    arquivo: object = None
    tipo: str = None
    usar_perfil: bool = False
    salvar_no_perfil: bool = False


def nota_na_faixa(conceito, nota):
    """A nota está na faixa do conceito (FR-009). [US-25][RBN-DEF-05.2]"""
    faixa = FAIXAS.get(conceito)
    return faixa is not None and nota is not None and faixa[0] <= nota <= faixa[1]


def criterios_liberados(sessao, criterios=None):
    """Critérios que podem ser lançados agora (RBN-DEF-05.1): só a Parte Escrita com a sessão
    Agendada ou Reagendada; os 9 com a sessão Em Andamento; nenhum nos demais status.
    [US-25][US-26][RBN-DEF-05.1][FR-011][FR-012]
    """
    criterios = criterios if criterios is not None else _criterios()
    if sessao.def_data_liberacao_resultado is not None:
        return []
    if sessao.def_status == StatusSessao.EM_ANDAMENTO:
        return list(criterios)
    if sessao.def_status in STATUS_ANTES_DA_SESSAO:
        return [c for c in criterios if c.cri_componente == ComponenteCriterio.PARTE_ESCRITA]
    return []


def _vazio(dados):
    """Critério sem conceito, sem nota e sem Observações. [US-25][RBN-DEF-05.1]"""
    return not dados or (
        not dados.get("conceito") and dados.get("nota") is None and not dados.get("observacoes")
    )


def _completo(dados):
    """Critério com conceito e nota. [US-25][RBN-DEF-05.2]"""
    return bool(dados) and bool(dados.get("conceito")) and dados.get("nota") is not None


def _conferir_linhas(linhas, liberados):
    """Defesa em profundidade da regra do formulário: cada critério liberado vazio ou com
    conceito e nota (MA-01), nota na faixa do conceito (FR-009) e Observações até 500 (MA-02).
    [US-25][RBN-DEF-05.2][FR-009][FR-010][FR-013]
    """
    for criterio in liberados:
        dados = linhas.get(criterio.pk)
        if _vazio(dados):
            continue
        if not _completo(dados):
            raise ErroAvaliacao(mensagens.MA01_CONCEITO_E_NOTA, pendentes=[criterio.pk])
        if not nota_na_faixa(dados["conceito"], dados["nota"]):
            raise ErroAvaliacao(mensagens.NOTA_FORA_DA_FAIXA, pendentes=[criterio.pk])
        if len(dados.get("observacoes") or "") > 500:
            raise ErroAvaliacao(mensagens.MA02_OBSERVACOES_LONGAS, pendentes=[criterio.pk])


def _gravar_linhas(sessao, usuario, linhas, liberados, agora):
    """Grava os critérios liberados: insere ou atualiza os preenchidos e apaga a linha de um
    critério liberado esvaziado. Critérios bloqueados pelo status não são lidos, nem
    atualizados, nem apagados (revisão I-01). [US-25][RBN-DEF-05.1][RBN-DEF-05.2][FR-013]
    """
    for criterio in liberados:
        dados = linhas.get(criterio.pk)
        chave = {"ava_def": sessao, "ava_usu": usuario, "ava_cri": criterio}
        if _vazio(dados):
            Avaliacoes.objects.filter(**chave).delete()
            continue
        Avaliacoes.objects.update_or_create(
            **chave,
            defaults={
                "ava_conceito": dados["conceito"],
                "ava_nota": dados["nota"],
                "ava_observacoes": dados.get("observacoes") or None,
                "ava_data_hora": agora,
            },
        )


def _travar_para_avaliar(usuario, def_id):
    """Trava turma → aluno → TCC → sessão → linha de BancaDefesa do membro (mesma ordem da spec
    007, research A4) e reconfere, depois de travar, o vínculo (AcessoRestrito) e a liberação ou
    a sessão Realizada (MA-04). Chamar dentro de transaction.atomic().
    [US-25][US-27][RBN-DEF-05.3][RBN-DEF-06.4][FR-007][FR-022]
    """
    services_defesa.travar_tcc(services_defesa.tcc_da_sessao(def_id))
    sessao = services_defesa.travar_sessao(def_id)
    if not permissoes_defesa.pode_avaliar(usuario, sessao):
        raise AcessoRestrito()
    linha = (
        BancaDefesa.objects.select_for_update().filter(ban_def=sessao, ban_usu_id=usuario.pk).get()
    )
    if (
        sessao.def_data_liberacao_resultado is not None
        or sessao.def_status == StatusSessao.REALIZADA
    ):
        raise ErroAvaliacao(mensagens.MA04_RESULTADO_LIBERADO)
    return sessao, linha


def salvar_rascunho(usuario, def_id, linhas):
    """Botão Salvar (FR-011 a FR-013): grava como rascunho os critérios liberados pelo status,
    sem assinatura e sem envio. Avaliação já Enviada: MA-13 (até Reabrir); depois da
    liberação: MA-04. `linhas` = {cri_id: {conceito, nota (Decimal), observacoes}}.
    [US-25][RBN-DEF-05.1][RBN-DEF-05.2][FR-011][FR-012][FR-013][FR-021][FR-022]
    """
    with transaction.atomic():
        sessao, linha = _travar_para_avaliar(usuario, def_id)
        if linha.ban_data_envio is not None:
            raise ErroAvaliacao(mensagens.MA13_AVALIACAO_JA_ENVIADA)
        liberados = criterios_liberados(sessao)
        if not liberados:
            raise ErroAvaliacao(mensagens.MA04_RESULTADO_LIBERADO)
        _conferir_linhas(linhas, liberados)
        _gravar_linhas(sessao, usuario, linhas, liberados, timezone.now())
    return sessao


def _conferir_dimensoes(conteudo):
    """Abre a imagem com o Pillow só para ler o tamanho em pixels: imagem que não abre, a
    mensagem de formato da US-26 E3; acima de 2000 × 1000, MA-14 (sem reduzir; research A5).
    [US-26][RBN-DEF-05.2][FR-016]
    """
    from PIL import Image, UnidentifiedImageError

    conteudo.seek(0)
    try:
        with Image.open(conteudo) as imagem:
            largura, altura = imagem.size
    except (UnidentifiedImageError, OSError, ValueError):
        raise ErroAvaliacao(mensagens.ASSINATURA_FORMATO, campo="assinatura")
    finally:
        conteudo.seek(0)
    if largura > LARGURA_MAXIMA or altura > ALTURA_MAXIMA:
        raise ErroAvaliacao(mensagens.MA14_ASSINATURA_GRANDE, campo="assinatura")


def assinatura_do_perfil(usuario):
    """Caminho da assinatura do perfil (US-38) se o arquivo ainda existe no disco; None se não
    há ou se sumiu (deploy no Render gratuito): a opção "usar a do perfil" não aparece.
    [US-26][US-38][RBN-DEF-05.2][FR-015][research A5]
    """
    caminho = services.caminho_da_assinatura(usuario)
    return caminho if caminho and default_storage.exists(caminho) else None


def _origem_da_assinatura(usuario, assinatura):
    """Conteúdo e tipo da imagem a copiar para a avaliação: o arquivo anexado ou a assinatura do
    perfil. Sem nenhuma (ou com o arquivo do perfil ausente): a mensagem da US-25 E4 / US-26 E4.
    [US-26][RBN-DEF-05.2][FR-015][FR-016][FR-019]
    """
    if assinatura is not None and assinatura.arquivo is not None:
        _conferir_dimensoes(assinatura.arquivo)
        return assinatura.arquivo, assinatura.tipo
    if assinatura is not None and assinatura.usar_perfil:
        caminho = assinatura_do_perfil(usuario)
        if caminho is not None:
            with default_storage.open(caminho, "rb") as arquivo:
                dados = arquivo.read()
            tipo = services.tipo_por_bytes(dados[:8])
            if tipo is not None:
                conteudo = ContentFile(dados)
                _conferir_dimensoes(conteudo)
                return conteudo, tipo
    raise ErroAvaliacao(mensagens.ASSINATURA_OBRIGATORIA, campo="assinatura")


def _copiar_assinatura(sessao, usuario, conteudo, tipo):
    """Grava a cópia da imagem usada em assinaturas_banca/<def_id>_<usu_id>_<aleatório>.<ext>,
    no default_storage (sem URL pública; servida só ao dono). Devolve o caminho.
    [US-26][RBN-DEF-05.2][FR-018][research A5]
    """
    conteudo.seek(0)
    nome = f"assinaturas_banca/{sessao.pk}_{usuario.pk}_{secrets.token_hex(8)}.{tipo}"
    return default_storage.save(nome, conteudo)


def enviar_avaliacao(usuario, def_id, linhas, assinatura):
    """Botão Enviar avaliação assinada (FR-019): só com a sessão Em Andamento (antes, MA-03);
    os 9 critérios com conceito e nota (senão "Todos os 9 critérios devem conter conceito e
    nota", com os pendentes); a assinatura anexada ou do perfil (senão a mensagem da US-25 E4).
    Grava as notas, a cópia da imagem (a anterior é apagada depois do commit; a nova, se a
    transação desfizer, revisão M-11), a data e hora do envio e, com "Salvar esta imagem no meu
    perfil", a assinatura do perfil (services.salvar_assinatura, na mesma transação).
    [US-25][US-26][RBN-DEF-05.1][RBN-DEF-05.2][RBN-DEF-06.1][FR-015 a FR-019]
    """
    copia = None
    try:
        with transaction.atomic():
            sessao, linha = _travar_para_avaliar(usuario, def_id)
            if linha.ban_data_envio is not None:
                raise ErroAvaliacao(mensagens.MA13_AVALIACAO_JA_ENVIADA)
            if sessao.def_status != StatusSessao.EM_ANDAMENTO:
                raise ErroAvaliacao(mensagens.MA03_SO_PARTE_ESCRITA)
            liberados = criterios_liberados(sessao)
            pendentes = [c.pk for c in liberados if not _completo(linhas.get(c.pk))]
            if pendentes:
                raise ErroAvaliacao(mensagens.CRITERIOS_INCOMPLETOS, pendentes=pendentes)
            _conferir_linhas(linhas, liberados)
            conteudo, tipo = _origem_da_assinatura(usuario, assinatura)
            agora = timezone.now()
            _gravar_linhas(sessao, usuario, linhas, liberados, agora)
            copia = _copiar_assinatura(sessao, usuario, conteudo, tipo)
            if assinatura.salvar_no_perfil and assinatura.arquivo is not None:
                assinatura.arquivo.seek(0)
                services.salvar_assinatura(usuario, assinatura.arquivo, tipo)
            anterior = linha.ban_assinatura_path
            BancaDefesa.objects.filter(ban_def=sessao, ban_usu_id=usuario.pk).update(
                ban_assinatura_path=copia, ban_data_envio=agora
            )
            _apagar_depois_do_commit([anterior])
    except Exception:
        if copia is not None:
            default_storage.delete(copia)
        raise
    return sessao


def reabrir_avaliacao(usuario, def_id):
    """Reabrir minha avaliação (FR-021; D6): só com a sessão Em Andamento e antes da liberação
    (senão MA-04); a avaliação volta a "Rascunho salvo" com as notas, sem data de envio e sem
    assinatura (cópia apagada depois do commit), e o parecer escolhido é limpo (D3 revista).
    Avaliação não enviada: nada muda. [US-25][US-27][RBN-DEF-06.1][RBN-DEF-06.4][FR-021]
    """
    with transaction.atomic():
        sessao, linha = _travar_para_avaliar(usuario, def_id)
        if sessao.def_status != StatusSessao.EM_ANDAMENTO:
            raise ErroAvaliacao(mensagens.MA04_RESULTADO_LIBERADO)
        if linha.ban_data_envio is None:
            return sessao
        _limpar_envio(BancaDefesa.objects.filter(ban_def=sessao, ban_usu_id=usuario.pk))
        _limpar_parecer(sessao)
    return sessao


def formulario_da_avaliacao(usuario, sessao):
    """Dados da tela Avaliação do membro efetivo (FR-008, FR-011 a FR-015): critérios, valores
    gravados (iniciais do formulário), critérios liberados, estado, se é só leitura (Enviada,
    Realizada ou liberada), se Salvar e Enviar ficam disponíveis, a nota MA-03, a nota individual,
    o Documento para Defesa, o Orientador e a assinatura do perfil disponível.
    [US-25][US-26][RBN-DEF-05.1][RBN-DEF-05.2][FR-008][FR-011][FR-012][FR-014][FR-015]
    """
    criterios = _criterios()
    linha = BancaDefesa.objects.get(ban_def=sessao, ban_usu_id=usuario.pk)
    gravadas = {
        av.ava_cri_id: av for av in Avaliacoes.objects.filter(ava_def=sessao, ava_usu_id=usuario.pk)
    }
    iniciais = []
    for criterio in criterios:
        av = gravadas.get(criterio.pk)
        iniciais.append(
            {
                "conceito": av.ava_conceito if av else "",
                "nota": av.ava_nota if av else None,
                "observacoes": (av.ava_observacoes or "") if av else "",
            }
        )
    enviada = linha.ban_data_envio is not None
    liberado = sessao.def_data_liberacao_resultado is not None
    somente_leitura = enviada or liberado or sessao.def_status == StatusSessao.REALIZADA
    liberados = [] if somente_leitura else criterios_liberados(sessao, criterios)
    presidente = services_defesa.banca_por_papel(sessao).get(PapelBanca.ORIENTADOR_PRESIDENTE)
    return {
        "criterios": criterios,
        "iniciais": iniciais,
        "liberados": {criterio.pk for criterio in liberados},
        "papel": linha.ban_papel,
        "estado": _estado(linha.ban_data_envio, bool(gravadas)),
        "data_envio": linha.ban_data_envio,
        "tem_copia": bool(linha.ban_assinatura_path),
        "somente_leitura": somente_leitura,
        "pode_salvar": bool(liberados),
        "pode_enviar": not somente_leitura and sessao.def_status == StatusSessao.EM_ANDAMENTO,
        "antes_da_sessao": sessao.def_status in STATUS_ANTES_DA_SESSAO,
        "nota_individual": nota_individual(sessao, usuario) if enviada else None,
        "documento": services_defesa.link_do_documento(sessao.def_tcc),
        "orientador": presidente,
        "assinatura_do_perfil": bool(assinatura_do_perfil(usuario)),
        "liberado": liberado,
    }
