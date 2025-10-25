@echo off
echo ========================================
echo REINICIALIZACAO LIMPA DO SISTEMA
echo ========================================
echo.

echo [1/4] Matando processos Python...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul
echo OK - Processos Python encerrados
echo.

echo [2/4] Limpando cache de dados...
rd /s /q "data\cache" 2>nul
rd /s /q "data\cache_agent_graph" 2>nul
mkdir "data\cache" 2>nul
mkdir "data\cache_agent_graph" 2>nul
echo OK - Cache de dados limpo
echo.

echo [3/4] Limpando arquivo de versao...
del /q "data\cache\.prompt_version" 2>nul
echo OK - Arquivo de versao removido
echo.

echo [4/4] Sistema pronto para reiniciar!
echo.
echo ========================================
echo PROXIMOS PASSOS:
echo ========================================
echo 1. Execute: streamlit run streamlit_app.py
echo 2. Teste a query: grafico evolucao vendas produto 59294
echo.
echo Versao do Prompt: 2.4_all_double_braces_removed_20251020
echo ========================================
echo.
pause
