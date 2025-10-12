@echo off
REM Script para limpar cache e testar sistema

cd /d "%~dp0\.."

echo.
echo ========================================
echo   LIMPANDO CACHE E TESTANDO
echo ========================================
echo.

REM Limpar cache de respostas LLM
echo [1/3] Limpando cache de respostas...
del /Q data\cache\*.json 2>nul
echo [OK] Cache limpo

REM Limpar cache Python
echo [2/3] Limpando cache Python...
del /Q /S __pycache__ 2>nul
del /Q /S *.pyc 2>nul
echo [OK] Cache Python limpo

REM Executar teste
echo [3/3] Executando teste completo...
echo.
python scripts\test_gemini_complete.py

pause
