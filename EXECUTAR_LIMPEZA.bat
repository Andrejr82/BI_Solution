@echo off
REM ============================================================================
REM Script de Limpeza Completa do Projeto Agent_Solution_BI
REM Deploy Agent - 2025-10-17
REM ============================================================================

SETLOCAL EnableDelayedExpansion

COLOR 0A
CLS

echo ============================================================================
echo   LIMPEZA COMPLETA DO PROJETO AGENT_SOLUTION_BI
echo ============================================================================
echo.
echo  Este script ira:
echo  1. Remover arquivos temporarios
echo  2. Limpar cache desatualizado (mais de 3 dias)
echo  3. Consolidar scripts de limpeza
echo  4. Organizar scripts de diagnostico
echo  5. Verificar status Git
echo.
echo ============================================================================
echo.

set /p CONFIRM="Deseja continuar com a limpeza? (S/N): "
if /i not "%CONFIRM%"=="S" (
    echo.
    echo Operacao cancelada pelo usuario.
    pause
    exit /b 0
)

echo.
echo ============================================================================
echo   EXECUTANDO LIMPEZA...
echo ============================================================================
echo.

cd /d "%~dp0"

REM Verificar se Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado. Certifique-se de que o Python esta instalado.
    pause
    exit /b 1
)

REM Executar script de limpeza
python cleanup_project.py

if errorlevel 1 (
    echo.
    echo ============================================================================
    echo   ERRO: A limpeza encontrou problemas!
    echo ============================================================================
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo   LIMPEZA CONCLUIDA COM SUCESSO!
echo ============================================================================
echo.
echo  Verifique o relatorio em: .cleanup_report.json
echo  Backup criado em: backup_cleanup/
echo.

REM Perguntar sobre commit Git
echo ============================================================================
echo   PROXIMO PASSO: GIT
echo ============================================================================
echo.
set /p GIT_COMMIT="Deseja adicionar as alteracoes ao Git? (S/N): "
if /i "%GIT_COMMIT%"=="S" (
    echo.
    echo Adicionando alteracoes ao Git...
    git add -A
    echo.
    echo Execute manualmente o commit:
    echo   git commit -m "chore: Limpeza de arquivos temporarios e reorganizacao de scripts"
    echo.
)

echo.
pause
ENDLOCAL
