"""Carga inicial dos domínios fixos do app cadastro, usada pelas data migrations (research D6).

As funções recebem o registro de apps da migração (apps.get_model), usam get_or_create pela chave
natural e nunca informam identificador (spec FR-003, FR-017). Mudanças futuras viram funções e
migrações novas; as existentes não são alteradas.

[US-39][RBN-CAD-14.1][US-13][RBN-CAD-08.1][FR-013][FR-015]
"""

# Nomes dos cursos do NUCOMP, usados também pelas regras da spec 004 (orientador automático e
# equivalência de cursos). Renomear um curso (US-39) exige revisar estas constantes.
# [US-39][RBN-CAD-14.1][US-07][RBN-CAD-04.2][spec 004, research B8]
CURSO_ENG_COMPUTACAO = "Engenharia de Computação"
CURSO_SIST_INFORMACAO = "Sistemas de Informação"
CURSO_LIC_COMPUTACAO = "Licenciatura em Computação"

# Cursos do NUCOMP (spec FR-013). cur_descricao fica nulo: as fontes não trazem o texto.
CURSOS = (
    CURSO_ENG_COMPUTACAO,
    CURSO_SIST_INFORMACAO,
    CURSO_LIC_COMPUTACAO,
)

# Turmas de TCC 2 destes cursos têm orientador automático (RBN-CAD-04.2). [US-07][spec 004, B8]
CURSOS_COM_ORIENTADOR_AUTOMATICO = (CURSO_ENG_COMPUTACAO, CURSO_LIC_COMPUTACAO)

# Códigos de curso da UEA e o curso do NUCOMP correspondente (spec 004, Q5; índice Q-17 e Q-37).
# "Sujeitos a mudança": cada mudança entra por uma nova migração de carga. [US-08][RBN-CAD-05.7]
EQUIVALENCIA_CURSOS = (
    ("EST08MCPD", CURSO_ENG_COMPUTACAO),
    ("EST31MSII", CURSO_SIST_INFORMACAO),
    ("EST03MLV", CURSO_LIC_COMPUTACAO),
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
    # Apaga por SQL: o delete() do ORM com os modelos históricos da migração falha ao percorrer o
    # OneToOneField de Coordenadores. As FKs do banco continuam impedindo apagar linha referenciada.
    schema_editor.execute('DELETE FROM "Cursos" WHERE cur_nome = ANY(%s)', [list(CURSOS)])


def carregar_areas_interesse(apps, schema_editor):
    """Insere as 10 áreas, sem duplicar se já existirem. [US-13][RBN-CAD-08.1][FR-015]"""
    areas = apps.get_model("cadastro", "AreasInteresse")
    for nome in AREAS_INTERESSE:
        areas.objects.get_or_create(ari_nome=nome)


def remover_areas_interesse(apps, schema_editor):
    """Reverte a carga de áreas (só os nomes carregados), por SQL como remover_cursos."""
    schema_editor.execute(
        'DELETE FROM "Areas_Interesse" WHERE ari_nome = ANY(%s)', [list(AREAS_INTERESSE)]
    )


def carregar_equivalencia_cursos(apps, schema_editor):
    """Insere os códigos de curso da UEA, sem duplicar se já existirem.

    [US-08][RBN-CAD-05.7][spec 004, FR-015a][Q5]
    """
    cursos = apps.get_model("cadastro", "Cursos")
    equivalencias = apps.get_model("cadastro", "EquivalenciaCursos")
    for codigo, nome in EQUIVALENCIA_CURSOS:
        equivalencias.objects.get_or_create(
            eqc_codigo_uea=codigo, defaults={"eqc_cur": cursos.objects.get(cur_nome=nome)}
        )


def remover_equivalencia_cursos(apps, schema_editor):
    """Reverte a carga da equivalência (só os códigos carregados), por SQL como as demais."""
    schema_editor.execute(
        'DELETE FROM "Equivalencia_Cursos" WHERE eqc_codigo_uea = ANY(%s)',
        [[codigo for codigo, _ in EQUIVALENCIA_CURSOS]],
    )
