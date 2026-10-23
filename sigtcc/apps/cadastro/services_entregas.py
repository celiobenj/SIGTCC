"""Regras das entregas da turma do app cadastro (spec 005).

Domínio `Turmas_Marcos`/`Entregas_Marcos`/`Historico_Envios_Entregas`: cadastro de entregas pelo
Professor da Disciplina (US-43), envio e substituição do link pelo Aluno, com lembretes de prazo
(US-15), envio da Versão Final do TCC 2 (US-29), acompanhamento das entregas pelo Professor
(US-16) e homologação ou devolução para ajuste da Versão Final (US-44). Este módulo importa
`services_turmas` (permissão por turma, `criar_entregas_do_aluno`, `atualizar_status_tcc`) e
`services_tcc`, nunca o contrário.

[US-15][US-16][US-29][US-43][US-44][RBN-CAD-09.1 a 09.6]
[research C1][research C5][research C6][research C7]
"""
