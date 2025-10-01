# Script de limpeza para PowerShell v2

try {
    Write-Host "Removendo caches e logs..."
    if (Test-Path ".\__pycache__") { Remove-Item -Path ".\__pycache__" -Recurse -Force }
    if (Test-Path ".\cache") { Remove-Item -Path ".\cache" -Recurse -Force }
    if (Test-Path ".\logs") { Remove-Item -Path ".\logs" -Recurse -Force }
    if (Test-Path ".\tests\results") { Remove-Item -Path ".\tests\results" -Recurse -Force }

    Write-Host "Removendo ferramentas de desenvolvimento e testes..."
    if (Test-Path ".\.github") { Remove-Item -Path ".\.github" -Recurse -Force }
    if (Test-Path ".\.claude") { Remove-Item -Path ".\.claude" -Recurse -Force }
    if (Test-Path ".\.devcontainer") { Remove-Item -Path ".\.devcontainer" -Recurse -Force }
    if (Test-Path ".\.vercel") { Remove-Item -Path ".\.vercel" -Recurse -Force }
    if (Test-Path ".\dev_tools") { Remove-Item -Path ".\dev_tools" -Recurse -Force }
    if (Test-Path ".\maintenance") { Remove-Item -Path ".\maintenance" -Recurse -Force }
    if (Test-Path ".\tests") { Remove-Item -Path ".\tests" -Recurse -Force }
    if (Test-Path ".\build.sh") { Remove-Item -Path ".\build.sh" -Force }
    if (Test-Path ".\test_simple_import.py") { Remove-Item -Path ".\test_simple_import.py" -Force }
    if (Test-Path ".\test_streamlit_cloud_simulation.py") { Remove-Item -Path ".\test_streamlit_cloud_simulation.py" -Force }

    Write-Host "Arquivando documentos de desenvolvimento..."
    $archiveFolder = ".\docs\archive"
    if (-not (Test-Path $archiveFolder)) { New-Item -Path $archiveFolder -ItemType Directory -Force }

    # Move arquivos de relatório que correspondem ao padrão
    $reportFiles = Get-ChildItem -Path ".\docs\relatorio_*.md" -ErrorAction SilentlyContinue
    if ($reportFiles) {
        $reportFiles | Move-Item -Destination $archiveFolder -Force
    }

    # Move arquivos específicos
    $logFile = ".\docs\analise_arquitetura_logs.md"
    if (Test-Path $logFile) { Move-Item -Path $logFile -Destination $archiveFolder -Force }

    $sessionFile = ".\docs\sessao_correcoes_criticas_2025-09-18.md"
    if (Test-Path $sessionFile) { Move-Item -Path $sessionFile -Destination $archiveFolder -Force }

    Write-Host "Limpeza concluída com sucesso."
}
catch {
    Write-Host -ForegroundColor Red "Ocorreu um erro durante a execução do script:"
    Write-Host -ForegroundColor Red $_.Exception.Message
    exit 1
}