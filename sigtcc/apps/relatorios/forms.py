"""Filtros dos relatórios (spec 010, C2; contrato §2): herda o FiltroPeriodoForm da feat-07, sem
alterá-lo, e só cria os campos que o relatório declara.

Os dados são normalizados no __init__, antes da validação: o formulário recebe sempre o endereço,
fica vinculado e ignoraria `initial` (research R3). Valor forjado volta ao padrão sem virar erro de
campo, porque um erro desligaria a validação de datas do pai (research R4).

[US-31][US-47][US-32][US-33][RBN-DEF-01.5][RBN-CAD-14.1][FR-010][FR-011][FR-012][FR-013][FR-014]
[FR-015][FR-016]
"""

from dataclasses import dataclass
from urllib.parse import urlencode

from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.utils import timezone

from sigtcc.apps.cadastro.models import Cursos, Docentes, Turmas
from sigtcc.apps.cadastro.permissoes import tem_perfil
from sigtcc.apps.cadastro.services_contas import filtro_de_curso
from sigtcc.apps.defesa import mensagens as mensagens_defesa
from sigtcc.apps.defesa import services_defesa
from sigtcc.apps.defesa.forms_defesa import FiltroPeriodoForm

PERFIS_DE_GESTAO = ("coordenador", "secretaria")
ATALHO_PADRAO = "periodo_letivo"
TODOS = "todos"
AGRUPAMENTOS = (("curso", "Curso"), ("area", "Área de Interesse"), ("modalidade", "Modalidade"))
ABRANGENCIAS = (
    (TODOS, "Todos"),
    ("aprovados", "Todos os Aprovados"),
    ("concluidos", "Apenas Concluídos"),
)
MAXIMO_DE_DIGITOS = 9
_CAMPOS_DE_PERIODO = ("atalho", "atalho_anterior", "data_inicial", "data_final")


def _identificador_valido(valor):
    """Id de Curso ou Docente: decimal comum e curto. `"²".isdigit()` é verdadeiro e quebraria em
    int(), e um número gigante também (research R4). [FR-010]
    """
    return bool(valor) and valor.isascii() and valor.isdecimal() and len(valor) <= MAXIMO_DE_DIGITOS


def _rotulo_de_periodo(ano, semestre):
    """Período letivo como aparece nas telas. [FR-013]"""
    return f"{ano}/{semestre}"


@dataclass(frozen=True)
class Filtros:
    """Filtros aplicados à consulta (contrato §2). Ou `ano` e `semestre`, ou `inicio` e `fim`,
    nunca os dois. `cur_id=None` significa Todos só com `gestao=True`; fora da gestão, `doc_id` é
    sempre o do usuário, nunca None (research R4). [FR-012][FR-015][FR-016]
    """

    gestao: bool
    doc_id: int | None = None
    cur_id: int | None = None
    ano: int | None = None
    semestre: int | None = None
    inicio: object = None
    fim: object = None
    agrupar_por: str = ""
    abrangencia: str = ""
    aplicados: tuple = ()
    consulta: str = ""

    def periodo_q(self, prefixo=""):
        """Q sobre Defesas do período, ou None se o relatório não filtra período.

        [RBN-DEF-01.5][FR-012]
        """
        if self.inicio is not None:
            return services_defesa.filtro_de_periodo(
                "intervalo", self.inicio, self.fim, prefixo=prefixo
            )
        if self.ano is not None:
            return services_defesa.filtro_de_periodo(
                ATALHO_PADRAO, prefixo=prefixo, ano_semestre=(self.ano, self.semestre)
            )
        return None

    def resumo(self):
        """Linha "Mostrando": só o que foi de fato aplicado (research R14). [FR-076]"""
        return " · ".join(valor for _, valor in self.aplicados)

    def querystring(self):
        """Forma canônica dos filtros, para a exportação e o redirecionamento. [FR-018]"""
        return self.consulta


class FiltroRelatorioForm(FiltroPeriodoForm):
    """Componente de filtros do módulo, com os campos declarados pelo relatório.

    Curso e Docente só existem na gestão; fora dela, o valor do endereço nem entra (FR-016).
    [US-31][US-47][RBN-DEF-01.5][RBN-CAD-14.1][FR-010]
    """

    atalho_anterior = forms.CharField(required=False, widget=forms.HiddenInput)
    ano_semestre = forms.ChoiceField(
        label="Ano/Semestre", required=False, widget=forms.Select(attrs={"class": "inp"})
    )
    curso = forms.ChoiceField(
        label="Curso", required=False, widget=forms.Select(attrs={"class": "inp"})
    )
    docente = forms.ChoiceField(
        label="Docente", required=False, widget=forms.Select(attrs={"class": "inp"})
    )
    agrupar_por = forms.ChoiceField(
        label="Agrupar por",
        required=False,
        choices=AGRUPAMENTOS,
        widget=forms.Select(attrs={"class": "inp"}),
    )
    abrangencia = forms.ChoiceField(
        label="Abrangência",
        required=False,
        choices=ABRANGENCIAS,
        widget=forms.Select(attrs={"class": "inp"}),
    )

    field_order = (
        "atalho",
        "ano_semestre",
        "data_inicial",
        "data_final",
        "agrupar_por",
        "abrangencia",
        "curso",
        "docente",
    )

    def __init__(self, dados, *, usuario, registrado, hoje=None):
        super().__init__(dados.copy())
        self.usuario = usuario
        self.registrado = registrado
        self.hoje = hoje or timezone.now().date()
        self.gestao = tem_perfil(usuario, *PERFIS_DE_GESTAO)
        self._cur_id = None
        self._retirar_campos_nao_declarados()
        if "ano_semestre" in self.fields and "periodo" not in registrado.filtros:
            self.fields["ano_semestre"].label = "Período letivo"
        self._normalizar()

    def _retirar_campos_nao_declarados(self):
        """Só ficam os campos do relatório; Curso e Docente, só na gestão. [FR-010][FR-016]"""
        declarados = set(self.registrado.filtros)
        if not self.gestao:
            declarados -= {"curso", "docente"}
        if "periodo" not in declarados:
            for nome in _CAMPOS_DE_PERIODO:
                del self.fields[nome]
        for nome in ("ano_semestre", "curso", "docente", "agrupar_por", "abrangencia"):
            if nome not in declarados:
                del self.fields[nome]

    def _normalizar(self):
        """Padrões e valores forjados, antes de validar (research R3, R4). [FR-012][FR-015]"""
        if "atalho" in self.fields:
            self._normalizar_periodo()
        if "ano_semestre" in self.fields:
            self._normalizar_ano_semestre()
        if "curso" in self.fields:
            self._normalizar_curso()
        if "docente" in self.fields:
            self._normalizar_docente()
        for nome, padrao in (("agrupar_por", "curso"), ("abrangencia", TODOS)):
            if nome in self.fields and self.data.get(nome) not in dict(self.fields[nome].choices):
                self.data[nome] = padrao

    def _normalizar_periodo(self):
        """Quem troca o atalho descarta as datas recebidas, o que também sai de um erro de datas
        invertidas; atalho por datas preenche as datas (research R3). [FR-012][US-31 B]
        """
        validos = dict(self.fields["atalho"].choices)
        atalho = self.data.get("atalho")
        if atalho not in validos:
            atalho = ATALHO_PADRAO
        anterior = self.data.get("atalho_anterior")
        if anterior in validos and anterior != atalho:
            self.data["data_inicial"] = self.data["data_final"] = ""
        tem_datas = self.data.get("data_inicial") or self.data.get("data_final")
        if atalho != ATALHO_PADRAO and not tem_datas:
            inicio, fim = services_defesa.intervalo_do_atalho(atalho, self.hoje)
            self.data["data_inicial"], self.data["data_final"] = (
                inicio.isoformat(),
                fim.isoformat(),
            )
        self.data["atalho"] = self.data["atalho_anterior"] = atalho

    def _normalizar_ano_semestre(self):
        """Períodos com turma cadastrada e o atual, que é o padrão. [FR-013][US-32][US-33]"""
        periodos = set(Turmas.objects.values_list("tur_ano", "tur_semestre").distinct())
        atual = services_defesa.periodo_letivo_atual(self.hoje)
        periodos.add(atual)
        self.fields["ano_semestre"].choices = [
            (f"{ano}-{semestre}", _rotulo_de_periodo(ano, semestre))
            for ano, semestre in sorted(periodos, reverse=True)
        ]
        if self.data.get("ano_semestre") not in dict(self.fields["ano_semestre"].choices):
            self.data["ano_semestre"] = f"{atual[0]}-{atual[1]}"

    def _normalizar_curso(self):
        """Padrão no curso do usuário; a troca vale só para a tela aberta. [RBN-CAD-14.1][FR-015]"""
        self.fields["curso"].choices = [
            *((str(curso.pk), curso.cur_nome) for curso in Cursos.objects.order_by("cur_nome")),
            (TODOS, "Todos"),
        ]
        valor = self.data.get("curso")
        if valor != TODOS and not _identificador_valido(valor):
            valor = None
        self._cur_id, self.data["curso"] = filtro_de_curso(self.usuario, valor)

    def _normalizar_docente(self):
        """ "Todos" e cada docente do NUCOMP; padrão "Todos". [US-31 C][FR-010]"""
        docentes = Docentes.objects.select_related("doc").order_by("doc__usu_nome")
        self.fields["docente"].choices = [
            (TODOS, "Todos"),
            *((str(docente.pk), docente.doc.usu_nome) for docente in docentes),
        ]
        valor = self.data.get("docente")
        if not _identificador_valido(valor) or valor not in dict(self.fields["docente"].choices):
            self.data["docente"] = TODOS

    def clean(self):
        """Valida as datas pelo pai e leva a mensagem da US ao campo. [FR-014][US-31 E2]"""
        dados = super().clean()
        if mensagens_defesa.DATA_INICIAL_MAIOR in self.non_field_errors():
            del self._errors[NON_FIELD_ERRORS]
            self.add_error("data_inicial", mensagens_defesa.DATA_INICIAL_MAIOR)
        return dados

    def filtro(self):
        """O filtro() herdado recua para o Período Letivo em filtro inválido; aqui, nunca
        (research R2). [FR-014]
        """
        raise NotImplementedError("Use filtros()")

    def querystring(self):
        """Filtros aplicados, em forma canônica, para link e redirecionamento. [FR-018]"""
        return urlencode([(nome, self.data[nome]) for nome in self.fields if self.data.get(nome)])

    def _rotulo_escolhido(self, nome):
        """Rótulo da opção aplicada num campo de lista. [FR-076]"""
        return dict(self.fields[nome].choices)[self.data[nome]]

    def _periodo(self):
        """Campos de período de Filtros e o que a linha "Mostrando" exibe. [FR-012][research R14]"""
        limpos = self.cleaned_data
        inicial, final = limpos.get("data_inicial"), limpos.get("data_final")
        if inicial and final:
            texto = f"{inicial:%d/%m/%Y} a {final:%d/%m/%Y}"
            return {"inicio": inicial, "fim": final}, ("Período", texto)
        if "ano_semestre" in self.fields:
            ano, semestre = (int(parte) for parte in self.data["ano_semestre"].split("-"))
            rotulo = _rotulo_de_periodo(ano, semestre)
            return {"ano": ano, "semestre": semestre}, ("Período letivo", rotulo)
        if "atalho" in self.fields:
            ano, semestre = services_defesa.periodo_letivo_atual(self.hoje)
            rotulo = _rotulo_de_periodo(ano, semestre)
            return {"ano": ano, "semestre": semestre}, ("Período letivo", rotulo)
        return {}, None

    def filtros(self):
        """Filtros da consulta; só com o formulário válido. Fora da gestão, doc_id é o do usuário
        (research R4). [FR-016][RAN-REL-01]
        """
        campos, periodo = self._periodo()
        aplicados = [periodo] if periodo else []
        doc_id = None if self.gestao else self.usuario.pk
        if "docente" in self.fields and self.data["docente"] != TODOS:
            doc_id = int(self.data["docente"])
            aplicados.append(("Docente", self._rotulo_escolhido("docente")))
        elif "curso" in self.fields:
            aplicados.append(("Curso", self._rotulo_escolhido("curso")))
        if "agrupar_por" in self.fields:
            campos["agrupar_por"] = self.data["agrupar_por"]
            aplicados.append(("Agrupar por", self._rotulo_escolhido("agrupar_por")))
        if "abrangencia" in self.fields:
            campos["abrangencia"] = self.data["abrangencia"]
            aplicados.append(("Abrangência", self._rotulo_escolhido("abrangencia")))
        return Filtros(
            gestao=self.gestao,
            doc_id=doc_id,
            cur_id=self._cur_id,
            aplicados=tuple(aplicados),
            consulta=self.querystring(),
            **campos,
        )
