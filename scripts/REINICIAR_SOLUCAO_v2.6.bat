@echo off
echo ======================================================================
echo  REINICIALIZACAO LIMPA - SOLUCAO v2.6
echo ======================================================================
echo.
echo [1/3] Matando processos Python...
taskkill /F /IM python.exe /T 2>nul
if %errorlevel% equ 0 (
    echo   OK: Processos Python finalizados
) else (
    echo   AVISO: Nenhum processo Python encontrado
)
echo.

echo [2/3] Aguardando 3 segundos...
timeout /t 3 /nobreak >nul
echo   OK: Aguardado
echo.

echo [3/3] Iniciando Streamlit com cache limpo...
echo.
echo ======================================================================
echo  STREAMLIT INICIANDO - Versao 2.6
echo ======================================================================
echo.
echo Agora teste a query: "grafico de vendas segmentos une 2365"
echo O erro de format specifier NAO deve mais ocorrer!
echo.
echo ======================================================================
echo.

streamlit run streamlit_app.py
