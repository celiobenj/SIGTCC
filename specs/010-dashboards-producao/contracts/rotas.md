# Rotas: Dashboards de Produção

Namespace `relatorios`. Todas só `GET`. Sem sessão, vai ao login com `next`. Ordem na exportação:
login, `exigir_modulo(usuario)` (403 com a MR-06 para quem não é Docente nem Secretaria), 404 do id, `pode_abrir` (403 com a MR-06), 404 do formato, formulário, consulta, arquivo.

| Rota | Nome | Perfis | Resposta |
|---|---|---|---|
| `/relatorios/` | `relatorios:lista` | Docente, Secretaria | Lista por perfil, com a MR-05 |
| `/relatorios/<id>/` | `relatorios:relatorio` | Perfis do registro | Relatório; id desconhecido é 404; sem perfil é 403 com a MR-06 |
| `/relatorios/<id>/exportar/<formato>/` | `relatorios:exportar` | Perfis do registro | Arquivo (`pdf`, `csv` ou `xlsx`); formato desconhecido é 404; sem registros, filtro inválido ou falha: volta ao relatório com os mesmos filtros |

## Ids dos relatórios

| Id (ordem) | Relatório | Perfis (`tem_perfil`) | Filtros |
|---|---|---|---|
| `atividades-docente` (10) | Painel de atividades por docente | `docente`, `secretaria` | periodo, ano_semestre; gestão: curso e docente |
| `membros-externos` (20) | Participação de Membros Externos | `coordenador`, `secretaria` | periodo, ano_semestre, curso |
| `producao-tccs` (30) | Produção de TCCs | `coordenador` | ano_semestre, agrupar_por, abrangencia, curso |
| `artigos` (40) | Artigos | `coordenador` | ano_semestre, curso |
| `formacao-evasao` (50) | Formação e evasão | `coordenador` | ano_semestre, curso |
| `historico-nucomp` (60) | Histórico de indicadores do NUCOMP | `coordenador` | curso |

## Parâmetros

`atalho`, `atalho_anterior`, `ano_semestre` (`2026-2`), `data_inicial`, `data_final`, `curso`
(id ou `todos`), `docente` (id ou `todos`), `agrupar_por` (`curso`, `area`, `modalidade`),
`abrangencia` (`todos`, `aprovados`, `concluidos`).

## Menu

`sigtcc/apps/relatorios/menu.py`: rótulo "Relatórios", ícone `table_chart`, rota `relatorios:lista`,
perfis `docente` e `secretaria`, seção "Gestão", ordem 31.
