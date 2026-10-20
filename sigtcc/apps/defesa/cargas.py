"""Carga inicial dos 9 critérios oficiais de avaliação da EST/UEA (research D6).

Os descritores são provisórios (spec FR-014): a planilha oficial de avaliação ainda não está em
docs/fonte/. A troca pelos textos oficiais será uma data migration nova antes do TP3 (FR-014a),
sem alterar nome, componente, peso nem identificador. Esta função não deve ser alterada.

[US-25][RBN-DEF-04.1][FR-014]
"""

from decimal import Decimal

# (componente, nome, peso) conforme RBN-DEF-04.1: 7,0 na Parte Escrita e 3,0 na Parte Oral.
CRITERIOS = (
    ("Parte Escrita", "Relevância do Tema", Decimal("0.5")),
    ("Parte Escrita", "Metodologia", Decimal("2.0")),
    ("Parte Escrita", "Revisão da Literatura", Decimal("1.0")),
    ("Parte Escrita", "Resultados e Discussões", Decimal("2.0")),
    ("Parte Escrita", "Conclusões", Decimal("0.5")),
    ("Parte Escrita", "Redação", Decimal("1.0")),
    ("Parte Oral", "Organização", Decimal("1.0")),
    ("Parte Oral", "Domínio do Assunto", Decimal("1.5")),
    ("Parte Oral", "Postura perante a Banca", Decimal("0.5")),
)

# Descritores provisórios, iguais para os 9 critérios até a troca (travessão U+2013).
DESCRITORES_PROVISORIOS = {
    "cri_desc_exemplar": (
        "PROVISÓRIO – Exemplar (nota de 8,0 a 10,0). "
        "Texto oficial pendente da planilha de avaliação da EST/UEA."
    ),
    "cri_desc_competente": (
        "PROVISÓRIO – Competente (nota de 6,0 a 7,9). "
        "Texto oficial pendente da planilha de avaliação da EST/UEA."
    ),
    "cri_desc_necessita_trabalho": (
        "PROVISÓRIO – Necessita de Trabalho (nota de 0,0 a 5,9). "
        "Texto oficial pendente da planilha de avaliação da EST/UEA."
    ),
}


def carregar_criterios_provisorios(apps, schema_editor):
    """Insere os 9 critérios, sem duplicar se já existirem. [US-25][RBN-DEF-04.1][FR-014]"""
    criterios = apps.get_model("defesa", "Criterios")
    for componente, nome, peso in CRITERIOS:
        criterios.objects.get_or_create(
            cri_nome=nome,
            defaults={
                "cri_componente": componente,
                "cri_peso": peso,
                "cri_descricao": None,
                **DESCRITORES_PROVISORIOS,
            },
        )


def remover_criterios(apps, schema_editor):
    """Reverte a carga dos critérios (só os nomes carregados)."""
    apps.get_model("defesa", "Criterios").objects.filter(
        cri_nome__in=[nome for _, nome, _ in CRITERIOS]
    ).delete()
