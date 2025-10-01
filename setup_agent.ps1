param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("rapido","completo")]
    [string]$modo
)

Write-Host "========================================" -ForegroundColor Green
Write-Host " 🚀 Setup Agent_Solution_BI - PowerShell" -ForegroundColor Cyan
Write-Host "========================================`n"

# Perguntar se o usuário não passou parâmetro
if (-not $modo) {
    Write-Host "Selecione o modo de execucao:`n" -ForegroundColor Yellow
    Write-Host " [1] Setup RAPIDO   (limpeza + instalacao basica)"
    Write-Host " [2] Setup COMPLETO (limpeza + instalacao + audit fix)`n"
    $choice = Read-Host "Digite 1 ou 2"

    if ($choice -eq "1") { $modo = "rapido" }
    elseif ($choice -eq "2") { $modo = "completo" }
    else {
        Write-Host "❌ Opcao invalida." -ForegroundColor Red
        exit 1
    }
}

# Entrar na pasta do script
Set-Location -Path $PSScriptRoot

function Limpeza {
    Write-Host "🔄 Limpando dependencias antigas..." -ForegroundColor Yellow
    if (Test-Path "node_modules") { Remove-Item -Recurse -Force "node_modules" }
    if (Test-Path "package-lock.json") { Remove-Item -Force "package-lock.json" }
    npm cache clean --force | Out-Null
}

function Instalar-Rapido {
    Write-Host "📦 Instalando dependencias (sem audit)..." -ForegroundColor Green
    npm install --no-audit --no-fund
}

function Instalar-Completo {
    Write-Host "📦 Instalando dependencias..." -ForegroundColor Green
    npm install
    Write-Host "🛡 Rodando auditoria de seguranca (npm audit fix)..." -ForegroundColor Magenta
    npm audit fix
}

function Formatacao {
    Write-Host "🎨 Formatando codigo..." -ForegroundColor Cyan
    if (Test-Path ".eslintrc.json") {
        npx eslint . --fix
    } else {
        Write-Host "⚠ Nenhum ESLint configurado, pulando..."
    }

    if (Test-Path ".prettierrc.json") {
        npx prettier --write .
    } else {
        Write-Host "⚠ Nenhum Prettier configurado, pulando..."
    }
}

if ($modo -eq "rapido") {
    Write-Host "⚡ Modo RAPIDO selecionado" -ForegroundColor Cyan
    Limpeza
    Instalar-Rapido
    Formatacao
    Write-Host "✅ Setup rapido concluido!" -ForegroundColor Green
}
elseif ($modo -eq "completo") {
    Write-Host "🔥 Modo COMPLETO selecionado" -ForegroundColor Cyan
    Limpeza
    Instalar-Completo
    Formatacao
    Write-Host "✅ Setup completo concluido com audit!" -ForegroundColor Green
}

Write-Host "`n========================================"
Write-Host " ✅ Processo finalizado"
Write-Host "========================================"
