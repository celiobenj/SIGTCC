"""Carga inicial dos domínios fixos do app cadastro, usada pelas data migrations (research D6).

As funções recebem o registro de apps da migração (apps.get_model), usam get_or_create pela chave
natural e nunca informam identificador (spec FR-003, FR-017). Mudanças futuras viram funções e
migrações novas; as existentes não são alteradas.

[US-39][RBN-CAD-14.1][US-13][RBN-CAD-08.1][FR-013][FR-015]
"""

# Cursos do NUCOMP (spec FR-013). cur_descricao fica nulo: as fontes não trazem o texto.
CURSOS = (
    "Engenharia de Computação",
    "Sistemas de Informação",
    "Licenciatura em Computação",
)

# As 10 áreas fixas de RBN-CAD-08.1 (spec FR-015).
AREAS_INTERESSE = (
    "Engenharia de Software",
    "Inteligência Artificial",
    "Redes de Computadores",
    "Banco de Dados",
    "Sistemas Embarcados",
    "Segurança da Informação",
    "Interação Humano-Computador",
    "Ciência de Dados",
    "Computação Gráfica",
    "Educação em Computação",
)


def carregar_cursos(apps, schema_editor):
    """Insere os 3 cursos, sem duplicar se já existirem. [US-39][RBN-CAD-14.1][FR-013]"""
    cursos = apps.get_model("cadastro", "Cursos")
    for nome in CURSOS:
        cursos.objects.get_or_create(cur_nome=nome)


def remover_cursos(apps, schema_editor):
    """Reverte a carga de cursos (só os nomes carregados)."""
    apps.get_model("cadastro", "Cursos").objects.filter(cur_nome__in=CURSOS).delete()


def carregar_areas_interesse(apps, schema_editor):
    """Insere as 10 áreas, sem duplicar se já existirem. [US-13][RBN-CAD-08.1][FR-015]"""
    areas = apps.get_model("cadastro", "AreasInteresse")
    for nome in AREAS_INTERESSE:
        areas.objects.get_or_create(ari_nome=nome)


def remover_areas_interesse(apps, schema_editor):
    """Reverte a carga de áreas (só os nomes carregados)."""
    apps.get_model("cadastro", "AreasInteresse").objects.filter(
        ari_nome__in=AREAS_INTERESSE
    ).delete()
