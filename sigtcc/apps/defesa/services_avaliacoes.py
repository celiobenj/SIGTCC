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
from decimal import ROUND_HALF_UP, Decimal

from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Exists, OuterRef, Subquery

from sigtcc.apps.cadastro import services_artigos
from sigtcc.apps.cadastro.choices import DescricaoTurma
from sigtcc.apps.defesa import services_defesa
from sigtcc.apps.defesa.choices import PapelBanca, Parecer
from sigtcc.apps.defesa.models import Avaliacoes, BancaDefesa, Defesas

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
    from sigtcc.apps.defesa.models import Criterios

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
    from sigtcc.apps.defesa.choices import StatusSessao

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
    from sigtcc.apps.defesa.choices import ComponenteCriterio

    todos = _criterios()
    partes = []
    for componente in ComponenteCriterio:
        da_parte = [criterio for criterio in todos if criterio.cri_componente == componente]
        partes.append((componente.label, da_parte, sum((c.cri_peso for c in da_parte), D0)))
    return partes, sum((c.cri_peso for c in todos), D0)


D0 = Decimal("0")


def _documento_da_sessao():
    """Subconsulta: link mais recente do Documento para Defesa do aluno na turma do TCC, pela
    mesma regra de services_defesa.link_do_documento (entrega de Data Limite mais recente, envio
    mais recente), numa consulta só para toda a lista (revisão M-12). [US-25][RBN-DEF-05.4]
    [RBN-CAD-09.2]
    """
    from sigtcc.apps.cadastro.choices import TipoEntrega
    from sigtcc.apps.cadastro.models import HistoricoEnviosEntregas

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
    from sigtcc.apps.cadastro.services_turmas import STATUS_SESSAO_ATIVA
    from sigtcc.apps.defesa import services_documentos
    from sigtcc.apps.defesa.choices import StatusSessao

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
