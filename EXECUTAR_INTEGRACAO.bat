@echo off
echo ================================================================================
echo INTEGRACAO DynamicPrompt no CodeGenAgent
echo TAREFA 5 - PLANO_PILAR_4_EXECUCAO.md
echo ================================================================================
echo.

echo [1/2] Executando integracao...
python integrate_dynamic_prompt.py
if errorlevel 1 (
    echo.
    echo [ERRO] Integracao falhou!
    pause
    exit /b 1
)

echo.
echo [2/2] Validando integracao...
python validate_integration.py
if errorlevel 1 (
    echo.
    echo [AVISO] Validacao encontrou problemas. Verifique os logs acima.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo INTEGRACAO CONCLUIDA COM SUCESSO!
echo ================================================================================
echo.
echo Proximos passos:
echo   1. Testar com queries reais
echo   2. Monitorar logs de execucao
echo   3. Continuar para TAREFA 6 - FeedbackCollector
echo.
echo Documentacao: INTEGRACAO_DYNAMIC_PROMPT.md
echo.
pause
