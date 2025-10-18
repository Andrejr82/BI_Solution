@echo off
REM ========================================
REM Script de Limpeza de Cache - Streamlit
REM Agent_Solution_BI
REM ========================================

echo.
echo ========================================
echo  LIMPEZA DE CACHE - STREAMLIT
echo ========================================
echo.

REM 1. Limpar cache do Streamlit via CLI
echo [1/4] Limpando cache do Streamlit...
streamlit cache clear 2>nul
if %errorlevel% == 0 (
    echo       OK - Cache limpo via CLI
) else (
    echo       AVISO - Comando streamlit nao disponivel
)

REM 2. Deletar pasta de cache (Windows)
echo.
echo [2/4] Deletando pasta de cache...
if exist "%USERPROFILE%\.streamlit\cache" (
    rmdir /s /q "%USERPROFILE%\.streamlit\cache"
    echo       OK - Pasta cache deletada
) else (
    echo       INFO - Pasta cache nao existe
)

REM 3. Limpar arquivos temporários do Python
echo.
echo [3/4] Limpando arquivos .pyc e __pycache__...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
echo       OK - Arquivos temporarios limpos

REM 4. Limpar session state (opcional)
echo.
echo [4/4] Limpando session state do Streamlit...
if exist "%USERPROFILE%\.streamlit\session_state" (
    rmdir /s /q "%USERPROFILE%\.streamlit\session_state"
    echo       OK - Session state limpo
) else (
    echo       INFO - Session state nao existe
)

echo.
echo ========================================
echo  LIMPEZA CONCLUIDA!
echo ========================================
echo.
echo Proximos passos:
echo 1. Reiniciar o Streamlit: streamlit run streamlit_app.py
echo 2. Fazer login na aplicacao
echo 3. Testar pagina de Transferencias
echo.
echo Pressione qualquer tecla para sair...
pause >nul
