"""Registro dos relatórios e permissões por perfil (spec 010, C1; contrato §1). A feat-11 inclui
um relatório só com o decorador, sem alterar lista, menu, permissões nem exportação.

Módulo sem consulta ao banco na importação e sem depender de services_relatorios (research R13).

[US-31][US-47][US-32][US-33][RBN-REL-01.1][RBN-REL-01.2][RBN-REL-02.1][RBN-REL-02.2]
[RBN-REL-02.3][RBN-REL-02.4][FR-002][FR-003][FR-004]
"""

import re
from dataclasses import dataclass

from django.core.exceptions import ImproperlyConfigured, PermissionDenied

from sigtcc.apps.cadastro.permissoes import PAPEIS, TIPOS_CONTA, tem_perfil

from . import mensagens

PERFIS_DO_MODULO = ("docente", "secretaria")
FILTROS_VALIDOS = ("periodo", "ano_semestre", "curso", "docente", "agrupar_por", "abrangencia")
_SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

_RELATORIOS = {}


@dataclass(frozen=True)
class RelatorioRegistrado:
    """Declaração de um relatório: quem abre e quais filtros usa. [FR-003]"""

    id: str
    nome: str
    descricao: str
    frase: str
    perfis: tuple
    filtros: tuple
    ordem: int
    consulta: object


def _conferir(id, perfis, filtros):
    """Falha ao carregar, nunca abrindo o relatório a todos: tem_perfil sem perfis devolve
    verdadeiro. [FR-003][FR-004][research R13]
    """
    if not _SLUG.match(id):
        raise ImproperlyConfigured(f"Id de relatório fora do formato: {id!r}")
    if id in _RELATORIOS:
        raise ImproperlyConfigured(f"Relatório registrado duas vezes: {id!r}")
    if not isinstance(perfis, tuple) or not perfis:
        raise ImproperlyConfigured(f"O relatório {id!r} precisa de perfis")
    desconhecidos = set(perfis) - set(TIPOS_CONTA + PAPEIS)
    if desconhecidos:
        raise ImproperlyConfigured(f"Perfis desconhecidos em {id!r}: {sorted(desconhecidos)}")
    desconhecidos = set(filtros) - set(FILTROS_VALIDOS)
    if desconhecidos:
        raise ImproperlyConfigured(f"Filtros desconhecidos em {id!r}: {sorted(desconhecidos)}")


def relatorio(id, nome, descricao, frase, perfis, filtros, ordem):
    """Decorador da função de consulta `f(usuario, filtros) -> Relatorio`. [FR-003]"""

    def registrar(consulta):
        """Guarda a declaração e devolve a função sem alteração. [FR-003]"""
        _conferir(id, perfis, filtros)
        _RELATORIOS[id] = RelatorioRegistrado(
            id, nome, descricao, frase, perfis, tuple(filtros), ordem, consulta
        )
        return consulta

    return registrar


def obter(id):
    """Relatório registrado, ou None. [FR-004]"""
    return _RELATORIOS.get(id)


def pode_abrir(usuario, registrado):
    """O usuário tem um dos perfis do relatório. [FR-002][FR-004]"""
    return tem_perfil(usuario, *registrado.perfis)


def relatorios_do_usuario(usuario):
    """Relatórios que o perfil vê na lista, na ordem do registro. [FR-002]"""
    return sorted(
        (item for item in _RELATORIOS.values() if pode_abrir(usuario, item)),
        key=lambda item: (item.ordem, item.nome),
    )


def exigir_modulo(usuario):
    """Só Docente e Secretaria entram no módulo; os demais recebem a MR-06. [FR-001][FR-004]"""
    if not tem_perfil(usuario, *PERFIS_DO_MODULO):
        raise PermissionDenied(mensagens.MR06_SEM_PERMISSAO)
