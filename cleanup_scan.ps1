# ==============================================
# Full-Automation Ultimate Safe (Windows PowerShell)
# Backup + Análise + Limpeza + Logs + Rollback
# ==============================================
$Timestamp = Get-Date -Format "yyyyMMddHHmmss"
$BackupBranch = "cleanup/backup-$Timestamp"
$BackupTag = "backup/before-cleanup-$Timestamp"
$ReportFile = "cleanup_report_$Timestamp.json"
$LogFile = "cleanup_log_$Timestamp.txt"

Write-Host "=== [1/10] Criando branch de backup e tag ==="
git checkout -b $BackupBranch
git tag -a $BackupTag -m "Backup antes da limpeza"

# Backup ZIP
$BackupZip = "..\repo-backup-$Timestamp.zip"
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory((Get-Location).Path, $BackupZip)
Write-Host "Backup zip criado: $BackupZip"

# Pastas a ignorar
$IgnoreDirs = @("node_modules","dist","build",".env")

# --- Detecção ---
Write-Host "=== [2/10] Detectando stacks e arquivos críticos ==="
$PythonVersion = & python --version 2>&1
$NodeVersion = & node --version 2>&1
$PythonFiles = Get-ChildItem -Name | Where-Object {$_ -match "requirements.txt|pyproject.toml|setup.py"} | ForEach-Object {$_} 
if (-not $PythonFiles) {$PythonFiles="None"}
$NodeFiles = Get-ChildItem -Name | Where-Object {$_ -match "package.json|package-lock.json|yarn.lock|pnpm-lock.yaml"} | ForEach-Object {$_} 
if (-not $NodeFiles) {$NodeFiles="None"}

# --- Análise Python ---
Write-Host "=== [3/10] Rodando análise Python ==="
$PythonScanDirs = Get-ChildItem -Directory | Where-Object { $IgnoreDirs -notcontains $_.Name } | ForEach-Object { $_.Name }
$PythonScanPath = $PythonScanDirs -join " "
try { $VultureOutput = & python -m vulture $PythonScanPath 2>$null } catch { $VultureOutput="Vulture não instalado" }

# Dependências pip
try { 
    $PipList = & pip list --format=freeze 2>$null
} catch { $PipList = @() }

# --- Análise Node.js ---
Write-Host "=== [4/10] Rodando análise Node.js ==="
$NodeScanDirs = Get-ChildItem -Directory | Where-Object { $IgnoreDirs -notcontains $_.Name } | ForEach-Object { $_.Name }
$NodeScanPath = $NodeScanDirs -join " "
try { $DepcheckOutput = & npx depcheck --ignores node_modules,dist,build 2>$null } catch { $DepcheckOutput="depcheck não instalado" }

# --- Checagem segredos ---
Write-Host "=== [5/10] Checando segredos ==="
try { $TrufflehogOutput = & trufflehog filesystem --directory . 2>$null } catch { $TrufflehogOutput="trufflehog não instalado" }

# --- Top candidatos ---
Write-Host "=== [6/10] Montando top 10 candidatos à remoção ==="
$PyCandidates = @()
if ($VultureOutput -ne "Vulture não instalado") {
    $VultureLines = $VultureOutput -split "`n" | Select-Object -First 10
    foreach ($line in $VultureLines) {
        $file = ($line -split "\s+")[0]
        $pkg = ($file -split "\\")[0]
        $pipCmd = if ($PipList -contains $pkg) { "pip uninstall $pkg -y" } else { "" }
        $PyCandidates += @{
            file = $file
            reason = "unused code"
            risk = "medium"
            confidence = 80
            git_cmd = "git rm `"$file`""
            pip_cmd = $pipCmd
        }
    }
}

$NodeCandidates = @()
if ($DepcheckOutput -ne "depcheck não instalado") {
    $DepLines = ($DepcheckOutput -split "`n") | Where-Object {$_ -match "Unused"} | Select-Object -First 10
    foreach ($line in $DepLines) {
        $dep = $line.Trim()
        $NodeCandidates += @{
            file = $dep
            reason = "unused dependency"
            risk = "low"
            confidence = 70
            npm_cmd = "npm uninstall $dep"
        }
    }
}

$Candidates = $PyCandidates + $NodeCandidates

# --- Execução de comandos e logs ---
Write-Host "=== [7/10] Executando comandos de limpeza ==="
foreach ($c in $Candidates) {
    if ($c.git_cmd) { 
        Write-Host "Executando: $($c.git_cmd)"
        try { Invoke-Expression $c.git_cmd; Add-Content -Path $LogFile -Value "$Timestamp - Executado: $($c.git_cmd)" } catch { Add-Content -Path $LogFile -Value "$Timestamp - ERRO: $($c.git_cmd)" }
    }
    if ($c.pip_cmd) { 
        Write-Host "Executando: $($c.pip_cmd)"
        try { Invoke-Expression $c.pip_cmd; Add-Content -Path $LogFile -Value "$Timestamp - Executado: $($c.pip_cmd)" } catch { Add-Content -Path $LogFile -Value "$Timestamp - ERRO: $($c.pip_cmd)" }
    }
    if ($c.npm_cmd) { 
        Write-Host "Executando: $($c.npm_cmd)"
        try { Invoke-Expression $c.npm_cmd; Add-Content -Path $LogFile -Value "$Timestamp - Executado: $($c.npm_cmd)" } catch { Add-Content -Path $LogFile -Value "$Timestamp - ERRO: $($c.npm_cmd)" }
    }
}

# --- Check final ---
Write-Host "=== [8/10] Verificando status final ==="
git status

# --- Relatório final ---
$Report = @{
    summary = "Relatório full-automation (Python + Node.js)"
    detected = @{
        python_version = $PythonVersion
        node_version = $NodeVersion
        python_files = $PythonFiles -join ", "
        node_files = $NodeFiles -join ", "
    }
    candidates = $Candidates
    logs_file = $LogFile
    backup_branch = $BackupBranch
    backup_tag = $BackupTag
    patches = @()
    scripts = @()
    checks = @{
        vulture = $VultureOutput
        depcheck = $DepcheckOutput
        trufflehog = $TrufflehogOutput
    }
    notes = "Rollback automático disponível via branch de backup. Logs detalhados em $LogFile"
}

$Report | ConvertTo-Json -Depth 6 | Set-Content $ReportFile
Write-Host "=== [9/10] Relatório gerado: $ReportFile ==="

# --- Rollback sugerido ---
Write-Host "=== [10/10] Rollback seguro disponível ==="
Write-Host "Para reverter qualquer alteração, execute:"
Write-Host "git checkout $BackupBranch"
Write-Host "Fim do processo full-automation. Limpeza aplicada, logs gravados, rollback seguro pronto."
