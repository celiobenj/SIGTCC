@echo off
rem Script de qualidade do SIGTCC (PGCS 3.3).
rem Caminho corrigido de apps/sigtcc/ para sigtcc/ (research R12); as opções de linha (100)
rem vêm de pyproject.toml e .flake8 (research R13). Item de configuração: revisão do Célio Benjamim.

echo ===================================================
echo [SIGTCC] Executando Verificacoes de Qualidade de Codigo
echo ===================================================

echo [1/3] Ordenando imports com isort...
isort sigtcc/

echo [2/3] Formatando codigo com Black...
black sigtcc/

echo [3/3] Executando analise estatica com Flake8...
flake8 sigtcc/

if %ERRORLEVEL% EQU 0 (
echo ===================================================
echo [SUCESSO] Codigo aprovado nos padroes de qualidade!
echo ===================================================
) else (
echo ===================================================
echo [FALHA] Corrija os erros apontados pelo Flake8 acima.
echo ===================================================
)
