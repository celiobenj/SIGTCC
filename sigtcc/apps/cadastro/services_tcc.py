"""Regras da Proposta, dos dados do TCC e do Status/histórico/trilha do app cadastro (spec 005).

Domínio `TCCs`/`Historico_Status_TCC`: Proposta e dados do TCC com mudança de tema (US-13);
confidencialidade do Resumo (FR-007a); consulta do histórico e da trilha do Status, sem checagem
de perfil (US-14, research C9). Este módulo importa `services_turmas` (que expõe o serviço único
de gravação do Status, `criar_tcc_com_historico`/`atualizar_status_tcc`, FR-012), nunca o
contrário.

[US-13][US-14][RBN-CAD-07.1][RBN-CAD-08.1][RBN-CAD-08.2][RBN-CAD-08.3][RBN-CAD-08.7][RBN-CAD-08.8]
[research C1][research C3][research C9]
"""
