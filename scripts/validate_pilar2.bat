@echo off
REM ============================================================================
REM Script de Validacao - Pilar 2: Few-Shot Learning
REM
REM Valida que todos os componentes foram implementados corretamente
REM ============================================================================

echo.
echo ================================================================================
echo VALIDACAO - PILAR 2: FEW-SHOT LEARNING
echo ================================================================================
echo.

cd /d "%~dp0.."

echo [1/2] Verificando ambiente Python...
python --version
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)

echo.
echo [2/2] Executando validacao completa...
echo.

python scripts\validate_pilar2.py

if errorlevel 1 (
    echo.
    echo ================================================================================
    echo FALHA: Algumas validacoes falharam!
    echo ================================================================================
    echo.
    echo Revise os erros acima e corrija os problemas.
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo SUCESSO: Todas as validacoes passaram!
echo ================================================================================
echo.
echo O Pilar 2 - Few-Shot Learning esta 100%% implementado e pronto para uso!
echo.
echo Proximos passos:
echo   1. Execute: scripts\test_few_shot.bat
echo   2. Execute: python scripts\demo_few_shot.py
echo   3. Integre no code_gen_agent.py (veja INTEGRACAO_FEW_SHOT.md)
echo.

pause
