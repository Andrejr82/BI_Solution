@echo off
REM ============================================================================
REM Script de Teste - Few-Shot Learning
REM
REM Executa bateria completa de testes do Pilar 2
REM ============================================================================

echo.
echo ================================================================================
echo TESTE - PILAR 2: FEW-SHOT LEARNING
echo ================================================================================
echo.

cd /d "%~dp0.."

echo [1/3] Verificando ambiente Python...
python --version
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)

echo.
echo [2/3] Executando testes do FewShotManager...
echo.

python scripts\test_few_shot_learning.py

if errorlevel 1 (
    echo.
    echo ================================================================================
    echo FALHA: Alguns testes falharam!
    echo ================================================================================
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo SUCESSO: Todos os testes passaram!
echo ================================================================================
echo.

echo [3/3] Gerando relatorio de estatisticas...
python -m core.learning.few_shot_manager

echo.
echo ================================================================================
echo TESTE COMPLETO!
echo ================================================================================
echo.
echo Proximos passos:
echo 1. Integrar FewShotManager no code_gen_agent.py
echo 2. Testar com queries reais
echo 3. Monitorar melhoria de qualidade
echo.

pause
