@echo off
REM ============================================================================
REM Script para executar testes de integração completos
REM Valida todas as tasks pendentes de task.md.resolved
REM ============================================================================

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║  🧪 TESTES DE INTEGRACAO - AGENT SOLUTION BI                   ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Navegar para raiz do projeto
cd /d "%~dp0.."

REM Ativar ambiente virtual se existir
if exist ".venv_new\Scripts\activate.bat" (
    echo 🔧 Ativando ambiente virtual...
    call .venv_new\Scripts\activate.bat
) else (
    echo ⚠️ Ambiente virtual não encontrado - usando Python global
)

REM Verificar se pytest está instalado
python -c "import pytest" 2>NUL
if errorlevel 1 (
    echo ❌ pytest não instalado! Instalando...
    pip install pytest pytest-asyncio httpx python-dotenv
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo 📋 PRÉ-REQUISITOS
echo ═══════════════════════════════════════════════════════════════
echo.

REM Verificar se backend está rodando
echo 🔍 Verificando backend...
curl -s http://localhost:8000/health >NUL 2>&1
if errorlevel 1 (
    echo ⚠️ BACKEND NÃO ESTÁ RODANDO!
    echo    Inicie com: cd backend ^&^& python main.py
    echo.
) else (
    echo ✅ Backend rodando em http://localhost:8000
)

REM Verificar se frontend está rodando
echo 🔍 Verificando frontend...
curl -s http://localhost:3000 >NUL 2>&1
if errorlevel 1 (
    echo ⚠️ FRONTEND NÃO ESTÁ RODANDO!
    echo    Inicie com: cd frontend-react ^&^& npm run dev
    echo.
) else (
    echo ✅ Frontend rodando em http://localhost:3000
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo 🚀 EXECUTANDO TESTES
echo ═══════════════════════════════════════════════════════════════
echo.

REM Executar testes com opções detalhadas
pytest tests/test_integration_complete.py ^
    -v ^
    --tb=short ^
    --color=yes ^
    --maxfail=5 ^
    -p no:warnings ^
    --log-cli-level=INFO

set TEST_EXIT_CODE=%ERRORLEVEL%

echo.
echo ═══════════════════════════════════════════════════════════════
echo 📊 RESULTADO
echo ═══════════════════════════════════════════════════════════════
echo.

if %TEST_EXIT_CODE%==0 (
    echo ✅ TODOS OS TESTES PASSARAM!
) else (
    echo ❌ ALGUNS TESTES FALHARAM!
    echo    Verifique os logs acima para detalhes
)

echo.
echo Exit Code: %TEST_EXIT_CODE%
echo.

pause
exit /b %TEST_EXIT_CODE%
