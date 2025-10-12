@echo off
REM Script para visualizar o ultimo relatorio de teste

cd /d "%~dp0\.."

echo.
echo ========================================
echo   VISUALIZANDO ULTIMO RELATORIO
echo ========================================
echo.

REM Encontrar o ultimo arquivo de teste
for /f "delims=" %%a in ('dir /b /o-d reports\tests\test_gemini_complete_*.txt 2^>nul ^| findstr /n "^" ^| findstr "^1:"') do (
    set "LAST_FILE=%%a"
    goto :found
)

:found
set "LAST_FILE=%LAST_FILE:~2%"

if not defined LAST_FILE (
    echo [ERRO] Nenhum relatorio encontrado!
    echo Execute primeiro: python scripts/test_gemini_complete.py
    pause
    exit /b 1
)

echo Arquivo: %LAST_FILE%
echo.

REM Abrir no Notepad
notepad "reports\tests\%LAST_FILE%"

REM Ou mostrar no terminal
REM type "reports\tests\%LAST_FILE%"

exit /b 0
