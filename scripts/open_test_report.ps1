# Script PowerShell para abrir o último relatório de teste

$reportDir = "reports/tests"
$projectRoot = Split-Path -Parent $PSScriptRoot

Set-Location $projectRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ABRINDO ULTIMO RELATORIO DE TESTE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Encontrar o último arquivo
$lastReport = Get-ChildItem "$reportDir/test_gemini_complete_*.txt" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $lastReport) {
    Write-Host "[ERRO] Nenhum relatorio encontrado!" -ForegroundColor Red
    Write-Host "Execute primeiro: python scripts/test_gemini_complete.py" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "Arquivo: $($lastReport.Name)" -ForegroundColor Cyan
Write-Host "Data: $($lastReport.LastWriteTime)" -ForegroundColor Cyan
Write-Host ""

# Perguntar como abrir
Write-Host "Como deseja visualizar?"
Write-Host "[1] Notepad"
Write-Host "[2] VS Code (se instalado)"
Write-Host "[3] Navegador padrão"
Write-Host "[4] Mostrar no terminal"
Write-Host ""

$choice = Read-Host "Escolha (1-4)"

switch ($choice) {
    "1" {
        notepad $lastReport.FullName
    }
    "2" {
        code $lastReport.FullName
    }
    "3" {
        Start-Process $lastReport.FullName
    }
    "4" {
        Get-Content $lastReport.FullName | Out-Host
        Write-Host ""
        pause
    }
    default {
        notepad $lastReport.FullName
    }
}

Write-Host ""
Write-Host "Relatorio completo disponivel em:" -ForegroundColor Green
Write-Host $lastReport.FullName -ForegroundColor Cyan
