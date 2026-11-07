"""Consultas dos relatórios (spec 010): uma função por relatório, que recebe o usuário e os
filtros e devolve a estrutura única. Só leitura: nenhum trecho grava dados.

[US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2]
[RBN-REL-02.3][RBN-REL-02.4][FR-005]
"""

from collections import defaultdict
from dataclasses import dataclass, field

from django.db.models import Case, Count, F, IntegerField, OuterRef, Q, Subquery, Value, When
from django.db.models.functions import Coalesce
from django.utils import timezone

from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    Homologacao,
    ModalidadeTCC,
    StatusConta,
    StatusOrientacao,
    StatusSubmissao,
    StatusTCC,
)
from sigtcc.apps.cadastro.fields import TimestampField
from sigtcc.apps.cadastro.mensagens import SEM_ORIENTADOR
from sigtcc.apps.cadastro.models import (
    AlunosTurmas,
    AreasInteresse,
    Coorientacoes,
    Cursos,
    Docentes,
    HistoricoStatusTCC,
    Orientacoes,
    TCCs,
)
from sigtcc.apps.defesa.choices import StatusSessao
from sigtcc.apps.defesa.models import BancaDefesa
from sigtcc.apps.defesa.services_defesa import PAPEIS_TITULARES

from . import graficos, mensagens
from .estrutura import Coluna, Kpi, Linha, Relatorio, SubLista, link_seguro
from .forms import FiltroRelatorioForm
from .registro import relatorio

# Classificação única do Status do TCC (FR-040). A homologação da Versão Final já leva a Concluído
# (RBN-CAD-09.5), então a classificação olha só o Status. [RBN-REL-02.1][RBN-REL-02.3]
GRUPOS_DE_STATUS = {
    "ativos": (
        StatusTCC.EM_ANDAMENTO,
        StatusTCC.APTO_PARA_DEFESA,
        StatusTCC.APROVADO,
        StatusTCC.APROVADO_COM_CORRECOES,
    ),
    "com_sucesso": (StatusTCC.CONCLUIDO, StatusTCC.APROVADO_PARA_TCC_2),
    "sem_sucesso": (StatusTCC.REPROVADO, StatusTCC.DESISTENTE, StatusTCC.JUBILADO),
}
# Status final encerra o vínculo sem data de fim nos atalhos por data (FR-022; research R18).
STATUS_FINAIS = GRUPOS_DE_STATUS["com_sucesso"] + GRUPOS_DE_STATUS["sem_sucesso"]
STATUS_DOS_TRABALHOS = GRUPOS_DE_STATUS["ativos"] + STATUS_FINAIS
ABRANGENCIAS = {
    "aprovados": (
        StatusTCC.APROVADO_PARA_TCC_2,
        StatusTCC.APROVADO,
        StatusTCC.APROVADO_COM_CORRECOES,
        StatusTCC.CONCLUIDO,
    ),
    "concluidos": (StatusTCC.CONCLUIDO,),
}


def montar_relatorio(usuario, registrado, dados):
    """Caminho único da tela e da exportação (research R1): devolve (form, relatorio), com
    relatorio=None e sem consulta quando o filtro é inválido. O arquivo reflete o momento do
    download. [FR-004][FR-005][FR-014][FR-018]
    """
    form = FiltroRelatorioForm(dados, usuario=usuario, registrado=registrado)
    if not form.is_valid():
        return form, None
    pronto = registrado.consulta(usuario, form.filtros())
    pronto.id = registrado.id
    pronto.titulo = registrado.nome
    pronto.frase = registrado.frase
    pronto.gerado_em = timezone.now()
    return form, pronto


# ---------------------------------------------------------------------------------------------
# Painel de atividades por docente (US-31)
# ---------------------------------------------------------------------------------------------

_COLUNAS_ATIVIDADES = (
    Coluna("docente", "Docente"),
    Coluna("curso", "Curso", definicao=mensagens.DEFINICAO_CURSO_LOTACAO),
    Coluna(
        "tcc1",
        "Quantidade de Orientandos em TCC 1",
        numerica=True,
        definicao=mensagens.DEFINICAO_ORIENTANDOS_TCC_1,
    ),
    Coluna(
        "tcc2",
        "Quantidade de Orientandos em TCC 2",
        numerica=True,
        definicao=mensagens.DEFINICAO_ORIENTANDOS_TCC_2,
    ),
    Coluna(
        "coorientacoes",
        "Quantidade de Coorientações",
        numerica=True,
        definicao=mensagens.DEFINICAO_COORIENTACOES,
    ),
    Coluna("bancas", "Total de Bancas", numerica=True, definicao=mensagens.DEFINICAO_BANCAS),
)
_COLUNAS_VINCULOS = (
    Coluna("aluno", "Nome do Aluno"),
    Coluna("titulo", "Título do Trabalho"),
    Coluna("papel", "Papel"),
    Coluna("status", "Status do TCC"),
)
_COLUNAS_BANCAS = (
    Coluna("data", "Data"),
    Coluna("papel", "Papel na banca"),
    Coluna("aluno", "Nome do Aluno"),
    Coluna("titulo", "Título do Trabalho"),
)
PAPEL_ORIENTADOR = "Orientador"
PAPEL_COORIENTADOR = "Coorientador"
PAPEL_SUPLENTE = "Suplente"


@dataclass
class _Atividade:
    """Atividades de um docente: colunas e sub-listas saem das mesmas listas, numa passagem, e por
    isso não divergem (research R7). [US-31][RBN-REL-01.1][FR-023]
    """

    tcc1: set = field(default_factory=set)
    tcc2: set = field(default_factory=set)
    coorientacoes: set = field(default_factory=set)
    vinculos: dict = field(default_factory=dict)
    bancas: list = field(default_factory=list)

    def tem_atividade(self):
        """Algum vínculo ou banca no período. [US-31 E3]"""
        return bool(self.vinculos or self.bancas)


def _fim_efetivo(campo_fim, campo_tcc):
    """Fim do vínculo: a data de fim; sem ela, com o TCC em Status final, a data do último registro
    do histórico (research R18). [US-31][RBN-REL-01.1][RBN-CAD-08.7][FR-022]
    """
    ultimo = (
        HistoricoStatusTCC.objects.filter(hst_tcc=OuterRef(campo_tcc))
        .order_by("-hst_data_hora", "-hst_id")
        .values("hst_data_hora")[:1]
    )
    return Coalesce(
        F(campo_fim),
        Case(
            When(
                **{f"{campo_tcc}__tcc_status__in": STATUS_FINAIS},
                then=Subquery(ultimo, output_field=TimestampField()),
            ),
            default=Value(None, output_field=TimestampField()),
            output_field=TimestampField(),
        ),
        output_field=TimestampField(),
    )


def _vinculos_do_periodo(vinculos, prefixo, filtros):
    """Vínculos do período, Ativos, Encerrados ou Substituídos (FR-023): pelas turmas no Período
    Letivo; em vigor no intervalo nos demais (FR-022). [US-31][RBN-REL-01.1]
    """
    if filtros.inicio is None:
        return vinculos.filter(
            **{
                f"{prefixo}_tcc__tcc_tur__tur_ano": filtros.ano,
                f"{prefixo}_tcc__tcc_tur__tur_semestre": filtros.semestre,
            }
        )
    return vinculos.annotate(
        fim_efetivo=_fim_efetivo(f"{prefixo}_data_fim", f"{prefixo}_tcc")
    ).filter(
        Q(fim_efetivo__isnull=True) | Q(fim_efetivo__date__gte=filtros.inicio),
        **{f"{prefixo}_data_inicio__date__lte": filtros.fim},
    )


def _guardar_vinculo(atividade, tcc, papel):
    """Sub-lista deduplicada por (TCC, papel): dois vínculos iguais são uma linha só.

    [US-31][FR-023][research R7]
    """
    atividade.vinculos[(tcc.pk, papel)] = tcc


def _recorte_de_docentes(usuario, filtros):
    """Q de docente para cada consulta: fora da gestão, sempre o próprio usuário, mesmo que a
    consulta seja chamada sem o formulário; docente escolhido prevalece sobre o Curso (P2); o
    Curso é o de Lotação, sem cortar contagens. [RAN-REL-01][FR-016][FR-027][research R4]
    """
    if not filtros.gestao:
        return usuario.pk, None
    return filtros.doc_id, None if filtros.doc_id else filtros.cur_id


def _atividades(doc_id, cur_id, filtros):
    """Três consultas, juntadas em Python por docente, sem consulta por linha (research R7).

    [US-31][RBN-REL-01.1][FR-021][FR-023][FR-024]
    """
    atividades = defaultdict(_Atividade)
    orientacoes = Orientacoes.objects.select_related("ori_tcc__tcc_alu__alu", "ori_tcc__tcc_tur")
    coorientacoes = Coorientacoes.objects.select_related(
        "coo_tcc__tcc_alu__alu", "coo_tcc__tcc_tur"
    ).filter(coo_doc__isnull=False)
    bancas = (
        BancaDefesa.objects.select_related("ban_def__def_tcc__tcc_alu__alu")
        .filter(
            filtros.periodo_q("ban_def__"),
            ban_def__def_status=StatusSessao.REALIZADA,
            ban_papel__in=PAPEIS_TITULARES,
            ban_usu__docentes__isnull=False,
        )
        .order_by("ban_def__def_data", "ban_def_id")
    )
    if doc_id is not None:
        orientacoes = orientacoes.filter(ori_doc_id=doc_id)
        coorientacoes = coorientacoes.filter(coo_doc_id=doc_id)
        bancas = bancas.filter(ban_usu_id=doc_id)
    elif cur_id is not None:
        orientacoes = orientacoes.filter(ori_doc__doc_cur_id=cur_id)
        coorientacoes = coorientacoes.filter(coo_doc__doc_cur_id=cur_id)
        bancas = bancas.filter(ban_usu__docentes__doc_cur_id=cur_id)
    for orientacao in _vinculos_do_periodo(orientacoes, "ori", filtros):
        atividade, tcc = atividades[orientacao.ori_doc_id], orientacao.ori_tcc
        colunas = {DescricaoTurma.TCC_1: atividade.tcc1, DescricaoTurma.TCC_2: atividade.tcc2}
        colunas[tcc.tcc_tur.tur_descricao].add(tcc.tcc_alu_id)
        _guardar_vinculo(atividade, tcc, PAPEL_ORIENTADOR)
    for coorientacao in _vinculos_do_periodo(coorientacoes, "coo", filtros):
        atividade, tcc = atividades[coorientacao.coo_doc_id], coorientacao.coo_tcc
        atividade.coorientacoes.add(tcc.tcc_alu_id)
        _guardar_vinculo(atividade, tcc, PAPEL_COORIENTADOR)
    for banca in bancas:
        atividades[banca.ban_usu_id].bancas.append(banca)
    return atividades


def _docentes_das_linhas(doc_id, cur_id, atividades):
    """Docentes da tabela: o escolhido; ou todo docente com conta Ativa, com zeros, mais os
    Inativos e Aguardando Ativação com atividade. [US-31 C][RBN-REL-01.1][FR-021]
    """
    docentes = Docentes.objects.select_related("doc", "doc_cur").order_by("doc__usu_nome", "pk")
    if doc_id is not None:
        return docentes.filter(pk=doc_id)
    docentes = docentes.filter(Q(doc__usu_status=StatusConta.ATIVA) | Q(pk__in=list(atividades)))
    return docentes.filter(doc_cur_id=cur_id) if cur_id is not None else docentes


def _sublistas_do_docente(atividade):
    """Sub-listas "Orientações e coorientações" e "Bancas", em ordem definida (research R7), sem
    link para turma nem sessão (P4). [US-31 passo 7][RBN-CAD-08.3][FR-025]
    """
    vinculos = sorted(
        atividade.vinculos.items(),
        key=lambda item: (item[1].tcc_alu.alu.usu_nome, item[1].pk, item[0][1]),
    )
    linhas_de_vinculo = tuple(
        Linha(
            {
                "aluno": tcc.tcc_alu.alu.usu_nome,
                "titulo": tcc.tcc_titulo or "",
                "papel": papel,
                "status": tcc.tcc_status,
            }
        )
        for (_, papel), tcc in vinculos
    )
    linhas_de_banca = tuple(
        Linha(
            {
                "data": f"{banca.ban_def.def_data:%d/%m/%Y}",
                "papel": PAPEL_SUPLENTE if banca.ban_usu_substituido_id else banca.ban_papel,
                "aluno": banca.ban_def.def_tcc.tcc_alu.alu.usu_nome,
                "titulo": banca.ban_def.def_tcc.tcc_titulo or "",
            }
        )
        for banca in atividade.bancas
    )
    return (
        SubLista("Orientações e coorientações", _COLUNAS_VINCULOS, linhas_de_vinculo),
        SubLista("Bancas", _COLUNAS_BANCAS, linhas_de_banca),
    )


def _kpis_de_atividades(filtros, linhas):
    """KPIs do extrato do Docente e da visão de gestão. [US-31][FR-072]"""
    soma = {
        chave: sum(linha.valores[chave] for linha in linhas)
        for chave in ("tcc1", "tcc2", "coorientacoes", "bancas")
    }
    if not filtros.gestao:
        return (
            Kpi("Orientandos TCC 1", soma["tcc1"]),
            Kpi("Orientandos TCC 2", soma["tcc2"]),
            Kpi("Coorientações", soma["coorientacoes"]),
            Kpi("Bancas", soma["bancas"]),
        )
    return (
        Kpi("Docentes", len(linhas)),
        Kpi("Orientações", soma["tcc1"] + soma["tcc2"]),
        Kpi("Coorientações", soma["coorientacoes"]),
        Kpi("Bancas", soma["bancas"]),
    )


def _grafico_de_bancas(filtros, linhas):
    """Bancas por docente, só na gestão e só com quem tem banca; sem nenhuma, sem gráfico.

    [US-31][FR-072]
    """
    itens = [
        (linha.valores["docente"], linha.valores["bancas"])
        for linha in linhas
        if linha.valores["bancas"]
    ]
    return graficos.barras(itens) if filtros.gestao and itens else None


@relatorio(
    id="atividades-docente",
    nome="Painel de atividades por docente",
    descricao=mensagens.MR08_DESCRICAO_ATIVIDADES,
    frase=mensagens.MR08_DESCRICAO_ATIVIDADES,
    perfis=("docente", "secretaria"),
    filtros=("periodo", "ano_semestre", "curso", "docente"),
    ordem=10,
)
def atividades_docente(usuario, filtros):
    """Uma linha por docente, expansível em orientações e bancas; o Docente comum vê só a própria.
    [US-31][RBN-REL-01.1][RBN-DEF-01.5][RBN-CAD-10.4][RBN-CAD-14.1][FR-021][FR-022][FR-023]
    [FR-024][FR-025][FR-027]
    """
    doc_id, cur_id = _recorte_de_docentes(usuario, filtros)
    atividades = _atividades(doc_id, cur_id, filtros)
    linhas = []
    for docente in _docentes_das_linhas(doc_id, cur_id, atividades):
        atividade = atividades.get(docente.pk, _Atividade())
        linhas.append(
            Linha(
                {
                    "docente": docente.doc.usu_nome,
                    "curso": docente.doc_cur.cur_nome,
                    "tcc1": len(atividade.tcc1),
                    "tcc2": len(atividade.tcc2),
                    "coorientacoes": len(atividade.coorientacoes),
                    "bancas": len(atividade.bancas),
                },
                sublistas=_sublistas_do_docente(atividade),
            )
        )
    alguem_ativo = any(atividade.tem_atividade() for atividade in atividades.values())
    return Relatorio(
        colunas=_COLUNAS_ATIVIDADES,
        linhas=tuple(linhas),
        kpis=_kpis_de_atividades(filtros, linhas),
        grafico=_grafico_de_bancas(filtros, linhas),
        como_calculado=mensagens.COMO_ATIVIDADES,
        tem_registros=doc_id is not None or alguem_ativo,
        rotulo_linha="docente",
    )


# ---------------------------------------------------------------------------------------------
# Status por período e colunas comuns (US-32 e US-33)
# ---------------------------------------------------------------------------------------------


def ultimo_status(**filtro):
    """Subconsulta do último registro do histórico: a busca é pelo TCC, e não pela turma do
    registro, porque a transferência não grava histórico na turma de destino (research R5).
    [US-32][US-33][RBN-CAD-08.7][RAN-REL-02][FR-041]
    """
    return Subquery(
        HistoricoStatusTCC.objects.filter(**filtro)
        .order_by("-hst_data_hora", "-hst_id")
        .values("hst_status_novo")[:1]
    )


def _contagens_por_grupo(campo):
    """Contagens de Ativos, Com Sucesso e Sem Sucesso sobre a anotação `status`, numa consulta.
    [US-32][US-33][RBN-REL-02.1][RBN-REL-02.3][FR-040]
    """
    return {
        grupo: Count(campo, filter=Q(status__in=status))
        for grupo, status in GRUPOS_DE_STATUS.items()
    }


_COLUNAS_DE_GRUPO = (
    Coluna("ativos", "Ativos", numerica=True, definicao=mensagens.DEFINICAO_ATIVOS),
    Coluna("com_sucesso", "Com Sucesso", numerica=True, definicao=mensagens.DEFINICAO_COM_SUCESSO),
    Coluna("sem_sucesso", "Sem Sucesso", numerica=True, definicao=mensagens.DEFINICAO_SEM_SUCESSO),
)


def _valores_de_grupo(contagem):
    """Colunas de grupo de uma linha, com zeros quando o valor não tem trabalho. [FR-040]"""
    return {grupo: contagem.get(grupo, 0) for grupo in GRUPOS_DE_STATUS}


# ---------------------------------------------------------------------------------------------
# Produção de TCCs (US-33)
# ---------------------------------------------------------------------------------------------

_AGRUPAMENTOS = {
    "curso": ("tcc_tur__tur_cur__cur_nome", "Curso"),
    "area": ("tcc_ari__ari_nome", "Área de Interesse"),
    "modalidade": ("tcc_modalidade", "Modalidade"),
}


def _rotulos_do_agrupamento(filtros, contagens):
    """Valores do agrupamento, com zeros: as 10 áreas e, se houver, "Não informada"; as duas
    modalidades; os cursos do filtro. [US-33 A, B, E][FR-061][FR-062]
    """
    if filtros.agrupar_por == "area":
        rotulos = list(
            AreasInteresse.objects.order_by("ari_nome").values_list("ari_nome", flat=True)
        )
        return rotulos + ([None] if None in contagens else [])
    if filtros.agrupar_por == "modalidade":
        return [ModalidadeTCC.MONOGRAFIA.value, ModalidadeTCC.ARTIGO_CIENTIFICO.value]
    return _nomes_de_curso(filtros)


@relatorio(
    id="producao-tccs",
    nome="Produção de TCCs",
    descricao=mensagens.MR12_DESCRICAO_PRODUCAO,
    frase=mensagens.MR12_DESCRICAO_PRODUCAO,
    perfis=("coordenador",),
    filtros=("ano_semestre", "agrupar_por", "abrangencia", "curso"),
    ordem=30,
)
def producao_tccs(usuario, filtros):
    """Uma linha por valor do agrupamento e a linha Total, com Total de Trabalhos = Ativos + Com
    Sucesso + Sem Sucesso; o arquivo segue o agrupamento da tela (P3).
    [US-33][RBN-REL-02.1][RBN-CAD-08.3][RBN-CAD-08.7][FR-060][FR-061][FR-062][FR-063][FR-064]
    """
    campo, rotulo_da_coluna = _AGRUPAMENTOS[filtros.agrupar_por]
    trabalhos = TCCs.objects.filter(
        tcc_tur__tur_ano=filtros.ano, tcc_tur__tur_semestre=filtros.semestre
    )
    if filtros.cur_id is not None:
        trabalhos = trabalhos.filter(tcc_tur__tur_cur_id=filtros.cur_id)
    status_validos = ABRANGENCIAS.get(filtros.abrangencia, STATUS_DOS_TRABALHOS)
    linhas_do_banco = (
        trabalhos.annotate(status=ultimo_status(hst_tcc=OuterRef("pk")))
        .filter(status__in=status_validos)
        .values(campo)
        .annotate(total=Count("pk"), **_contagens_por_grupo("pk"))
        .order_by()
    )
    contagens = {linha[campo]: linha for linha in linhas_do_banco}
    linhas = []
    for valor in _rotulos_do_agrupamento(filtros, contagens):
        contagem = contagens.get(valor, {})
        linhas.append(
            Linha(
                {
                    "grupo": valor or mensagens.NAO_INFORMADA,
                    "total": contagem.get("total", 0),
                    **_valores_de_grupo(contagem),
                }
            )
        )
    soma = {
        chave: sum(linha.valores[chave] for linha in linhas)
        for chave in ("total", *GRUPOS_DE_STATUS)
    }
    itens = [
        (linha.valores["grupo"], linha.valores["total"])
        for linha in linhas
        if linha.valores["total"]
    ]
    return Relatorio(
        colunas=(
            Coluna("grupo", rotulo_da_coluna),
            Coluna(
                "total",
                "Total de Trabalhos",
                numerica=True,
                definicao=mensagens.DEFINICAO_TOTAL_TRABALHOS,
            ),
            *_COLUNAS_DE_GRUPO,
        ),
        linhas=tuple(linhas),
        totais=(Linha({"grupo": "Total", **soma}),),
        kpis=(
            Kpi("Total de Trabalhos", soma["total"]),
            Kpi("Ativos", soma["ativos"]),
            Kpi("Com Sucesso", soma["com_sucesso"]),
            Kpi("Sem Sucesso", soma["sem_sucesso"]),
        ),
        grafico=graficos.barras(itens) if itens else None,
        como_calculado=mensagens.COMO_PRODUCAO,
        tem_registros=soma["total"] > 0,
    )


# ---------------------------------------------------------------------------------------------
# Artigos (US-33 fluxo D)
# ---------------------------------------------------------------------------------------------

_COLUNAS_ARTIGOS = (
    Coluna("titulo", "Título do TCC"),
    Coluna("aluno", "Aluno"),
    Coluna("orientador", "Orientador"),
    Coluna("veiculo", "Veículo"),
    Coluna("qualis", "Estrato Qualis/CAPES"),
    Coluna("status", "Status de Submissão"),
    Coluna("aproveitamento", "Aproveitamento"),
    Coluna("link", "Link ou DOI"),
)


def _nome_do_orientador():
    """Vínculo ativo; sem ele, o mais recente, numa subconsulta (research R16). [FR-065]"""
    return Subquery(
        Orientacoes.objects.filter(ori_tcc=OuterRef("pk"))
        .annotate(
            prioridade=Case(
                When(ori_status=StatusOrientacao.ATIVA, then=0),
                default=1,
                output_field=IntegerField(),
            )
        )
        .order_by("prioridade", "-ori_data_inicio", "-ori_id")
        .values("ori_doc__doc__usu_nome")[:1]
    )


def _linha_de_artigo(tcc):
    """Linha do TCC; sem registro de publicação, células vazias e a MR-14. [FR-065][FR-066]"""
    artigo = getattr(tcc, "artigos", None)
    return Linha(
        {
            "titulo": tcc.tcc_titulo or "",
            "aluno": tcc.tcc_alu.alu.usu_nome,
            "orientador": tcc.orientador or SEM_ORIENTADOR,
            "veiculo": (artigo.art_veiculo_publicacao or "") if artigo else "",
            "qualis": (artigo.art_qualis_capes or "") if artigo else "",
            "status": (artigo.art_status_submissao or "") if artigo else "",
            "aproveitamento": (artigo.art_homologacao if artigo else None)
            or mensagens.MR14_APROVEITAMENTO_SEM_ANALISE,
            "link": link_seguro(artigo.art_link_doi) if artigo else "",
        }
    )


@relatorio(
    id="artigos",
    nome="Artigos",
    descricao=mensagens.MR13_DESCRICAO_ARTIGOS,
    frase=mensagens.MR13_DESCRICAO_ARTIGOS,
    perfis=("coordenador",),
    filtros=("ano_semestre", "curso"),
    ordem=40,
)
def artigos(usuario, filtros):
    """TCCs na modalidade Artigo Científico das turmas do período.
    [US-33 D][RBN-REL-02.2][RBN-CAD-10.5][RBN-CAD-12.1][RBN-CAD-12.3][FR-065][FR-066]
    """
    trabalhos = (
        TCCs.objects.select_related("tcc_alu__alu", "artigos")
        .filter(
            tcc_modalidade=ModalidadeTCC.ARTIGO_CIENTIFICO,
            tcc_tur__tur_ano=filtros.ano,
            tcc_tur__tur_semestre=filtros.semestre,
        )
        .annotate(orientador=_nome_do_orientador())
        .order_by("tcc_alu__alu__usu_nome", "pk")
    )
    if filtros.cur_id is not None:
        trabalhos = trabalhos.filter(tcc_tur__tur_cur_id=filtros.cur_id)
    trabalhos = list(trabalhos)
    linhas = tuple(_linha_de_artigo(tcc) for tcc in trabalhos)
    com_artigo = [tcc.artigos for tcc in trabalhos if getattr(tcc, "artigos", None)]
    return Relatorio(
        colunas=_COLUNAS_ARTIGOS,
        linhas=linhas,
        kpis=(
            Kpi("Artigos", len(linhas)),
            Kpi(
                "Publicados",
                sum(a.art_status_submissao == StatusSubmissao.PUBLICADO for a in com_artigo),
            ),
            Kpi(
                "Homologados", sum(a.art_homologacao == Homologacao.HOMOLOGADO for a in com_artigo)
            ),
        ),
        como_calculado=mensagens.COMO_ARTIGOS,
    )


# ---------------------------------------------------------------------------------------------
# Formação e evasão (US-32)
# ---------------------------------------------------------------------------------------------

_LEGENDA_FORMACAO = (
    ("Sem Proposta", "cinza"),
    ("Ativos", "azul"),
    ("Com Sucesso", "verde"),
    ("Sem Sucesso", "vermelho"),
)


def _status_do_vinculo():
    """Status do aluno na turma do vínculo: último registro do TCC que está na turma, e, sem TCC,
    Sem Proposta (research R5). [US-32][RBN-CAD-08.7][RBN-CAD-05.6][FR-041]
    """
    return Coalesce(
        ultimo_status(hst_tcc__tcc_alu=OuterRef("mat_alu"), hst_tcc__tcc_tur=OuterRef("mat_tur")),
        Value(StatusTCC.SEM_PROPOSTA.value),
    )


def _nomes_de_curso(filtros):
    """Uma linha por curso do NUCOMP; com curso escolhido, só ele. [US-32 B][FR-042]"""
    cursos = Cursos.objects.order_by("cur_nome")
    if filtros.cur_id is not None:
        cursos = cursos.filter(pk=filtros.cur_id)
    return list(cursos.values_list("cur_nome", flat=True))


@relatorio(
    id="formacao-evasao",
    nome="Formação e evasão",
    descricao=mensagens.MR10_DESCRICAO_FORMACAO,
    frase=mensagens.MR10_DESCRICAO_FORMACAO,
    perfis=("coordenador",),
    filtros=("ano_semestre", "curso"),
    ordem=50,
)
def formacao_evasao(usuario, filtros):
    """Uma linha por curso e a linha Total, com Matriculados = Sem Proposta + Ativos + Com Sucesso
    + Sem Sucesso. Aluno excluído da turma não tem vínculo e não conta; quem desiste com Proposta
    continua, em Sem Sucesso. A Q-02 segue aberta para o aluno sem Proposta.
    [US-32][RBN-REL-02.3][RBN-CAD-05.4][RBN-CAD-08.3][RBN-CAD-08.7][FR-041][FR-042][FR-043][Q-02]
    """
    vinculos = AlunosTurmas.objects.filter(
        mat_tur__tur_ano=filtros.ano, mat_tur__tur_semestre=filtros.semestre
    )
    if filtros.cur_id is not None:
        vinculos = vinculos.filter(mat_tur__tur_cur_id=filtros.cur_id)
    contagens = {
        linha["mat_tur__tur_cur__cur_nome"]: linha
        for linha in vinculos.annotate(status=_status_do_vinculo())
        .values("mat_tur__tur_cur__cur_nome")
        .annotate(
            matriculados=Count("mat_alu"),
            sem_proposta=Count("mat_alu", filter=Q(status=StatusTCC.SEM_PROPOSTA)),
            **_contagens_por_grupo("mat_alu"),
        )
        .order_by()
    }
    linhas = []
    for nome in _nomes_de_curso(filtros):
        contagem = contagens.get(nome, {})
        linhas.append(
            Linha(
                {
                    "curso": nome,
                    "matriculados": contagem.get("matriculados", 0),
                    "sem_proposta": contagem.get("sem_proposta", 0),
                    **_valores_de_grupo(contagem),
                }
            )
        )
    soma = {
        chave: sum(linha.valores[chave] for linha in linhas)
        for chave in ("matriculados", "sem_proposta", *GRUPOS_DE_STATUS)
    }
    barras = [
        (
            linha.valores["curso"],
            (
                linha.valores["sem_proposta"],
                linha.valores["ativos"],
                linha.valores["com_sucesso"],
                linha.valores["sem_sucesso"],
            ),
        )
        for linha in linhas
    ]
    return Relatorio(
        colunas=(
            Coluna("curso", "Curso"),
            Coluna(
                "matriculados",
                "Matriculados",
                numerica=True,
                definicao=mensagens.DEFINICAO_MATRICULADOS,
            ),
            Coluna(
                "sem_proposta",
                "Sem Proposta",
                numerica=True,
                definicao=mensagens.DEFINICAO_SEM_PROPOSTA,
            ),
            *_COLUNAS_DE_GRUPO,
        ),
        linhas=tuple(linhas),
        totais=(Linha({"curso": "Total", **soma}),),
        kpis=(
            Kpi("Matriculados", soma["matriculados"]),
            Kpi("Ativos", soma["ativos"]),
            Kpi("Com Sucesso", soma["com_sucesso"]),
            Kpi("Sem Sucesso", soma["sem_sucesso"]),
        ),
        grafico=graficos.empilhado(barras, _LEGENDA_FORMACAO),
        como_calculado=mensagens.COMO_FORMACAO,
        tem_registros=soma["matriculados"] > 0,
    )
