@echo off
echo ========================================
echo   DIAGNOSTICO FRONTEND - Agent BI
echo ========================================
echo.

echo [1/5] Verificando Node.js e npm...
node --version
npm --version
echo.

echo [2/5] Verificando dependencias do frontend...
cd frontend-solid
if not exist node_modules (
    echo [AVISO] node_modules nao encontrado!
    echo [INFO] Instalando dependencias...
    call npm install
) else (
    echo [OK] node_modules encontrado
)
echo.

echo [3/5] Limpando cache do Vite...
if exist node_modules\.vite (
    rd /s /q node_modules\.vite
    echo [OK] Cache do Vite limpo
) else (
    echo [INFO] Cache do Vite nao encontrado
)
echo.

echo [4/5] Verificando arquivos principais...
if exist src\index.tsx (
    echo [OK] index.tsx encontrado
) else (
    echo [ERRO] index.tsx NAO encontrado!
)

if exist index.html (
    echo [OK] index.html encontrado
) else (
    echo [ERRO] index.html NAO encontrado!
)

if exist vite.config.ts (
    echo [OK] vite.config.ts encontrado
) else (
    echo [ERRO] vite.config.ts NAO encontrado!
)
echo.

echo [5/5] Iniciando frontend em modo de desenvolvimento...
echo [INFO] Verifique o console do navegador para erros JavaScript
echo [INFO] Pressione Ctrl+C para encerrar
echo.
call npm run dev

cd ..
