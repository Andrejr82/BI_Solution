@echo off
REM ============================================================
REM Script de instalacao de dependencias RAG
REM Autor: Code Agent
REM Data: 2025-10-24
REM ============================================================

echo.
echo ============================================================
echo  INSTALACAO DE DEPENDENCIAS RAG
echo ============================================================
echo.

cd /d "%~dp0.."

REM Ativar ambiente virtual se existir
if exist "venv\Scripts\activate.bat" (
    echo Ativando ambiente virtual...
    call venv\Scripts\activate.bat
) else (
    echo AVISO: Ambiente virtual nao encontrado
    echo Continuando com Python global...
)

echo.
echo Executando script de instalacao...
echo.

python scripts\install_rag_dependencies.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo  INSTALACAO CONCLUIDA COM SUCESSO!
    echo ============================================================
    echo.
) else (
    echo.
    echo ============================================================
    echo  INSTALACAO FALHOU - VERIFIQUE OS LOGS ACIMA
    echo ============================================================
    echo.
)

pause
