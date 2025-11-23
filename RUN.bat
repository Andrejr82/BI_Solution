@echo off
REM ========================================================================
REM Agent Solution BI - Windows Launcher
REM ========================================================================
REM
REM Este script inicia toda a stack do Agent Solution BI:
REM - Backend FastAPI (port 8000)
REM - Frontend React (port 3000)
REM
REM Uso:
REM   - Duplo clique neste arquivo
REM   - Ou execute: RUN.bat
REM
REM ========================================================================

title Agent Solution BI - System Launcher

echo.
echo ========================================================================
echo           AGENT SOLUTION BI - UNIFIED LAUNCHER
echo ========================================================================
echo.
echo  Arquitetura: React (Frontend) + FastAPI (Backend) + Core
echo  LLM: Gemini 2.5 Flash ^| Data: Parquet + SQL Server
echo.
echo ========================================================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Python nao encontrado! Instale Python 3.11+ primeiro.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version

REM Verifica se run.py existe
if not exist "run.py" (
    echo [ERRO] Arquivo run.py nao encontrado!
    echo Execute este script do diretorio raiz do projeto.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo  Iniciando sistema...
echo ========================================================================
echo.
echo  Para encerrar: Pressione Ctrl+C
echo.

REM Executa o launcher Python
python run.py

REM Se chegou aqui, o script foi encerrado
echo.
echo ========================================================================
echo  Sistema encerrado
echo ========================================================================
echo.
pause
