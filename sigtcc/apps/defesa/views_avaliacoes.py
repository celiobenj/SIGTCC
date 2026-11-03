"""Views da avaliação da banca e do resultado da defesa (spec 008; contracts/rotas.md). Views
finas: as regras ficam em services_avaliacoes e permissoes_defesa; o sigilo, em
services_avaliacoes.visao_da_avaliacao.

[US-25][US-26][US-27][RBN-DEF-04.2][RBN-DEF-05.1 a RBN-DEF-05.4][RBN-DEF-06.3][RBN-DEF-06.4]
"""

from django.shortcuts import render

from sigtcc.apps.cadastro.permissoes import perfil_requerido
from sigtcc.apps.defesa import mensagens, services_avaliacoes


@perfil_requerido("docente", "membro_externo")
def criterios(request):
    """Janela "Critérios de avaliação" (FR-001, FR-002): os 9 critérios por componente, com
    peso, somas 7,0 e 3,0, total 10,0 e as descrições dos conceitos; somente leitura, sem ação
    de criar, editar ou remover para nenhum perfil. Outros perfis: 403.
    [US-25][RBN-DEF-04.1][RBN-DEF-04.2]
    """
    partes, total = services_avaliacoes.criterios_por_componente()
    return render(request, "defesa/criterios.html", {"partes": partes, "total": total})


@perfil_requerido("docente", "membro_externo")
def minhas_bancas(request):
    """Tela "Minhas bancas" (FR-003 a FR-006): as sessões de que o usuário é membro, sem as
    Canceladas, com papel, data, horário, aluno, título e status, as pendências em destaque e
    os atalhos Documento, Critérios de avaliação, Avaliar e Declaração; a linha abre a janela
    Sessão de defesa. Sem nenhuma, MA-12. [US-25][RBN-DEF-05.4][RBN-DEF-08.3]
    """
    contexto = {
        "bancas": services_avaliacoes.minhas_bancas(request.user),
        "sem_bancas": mensagens.MA12_SEM_BANCAS,
    }
    return render(request, "defesa/minhas_bancas.html", contexto)
