@echo off
REM Script Unificado de Limpeza de Cache
REM Agent_Solution_BI - Deploy Agent
REM Data: 2025-10-17

echo ========================================
echo   Limpeza de Cache - Agent_Solution_BI
echo ========================================
echo.

cd /d "%~dp0.."
python scripts/limpar_cache.py

pause
