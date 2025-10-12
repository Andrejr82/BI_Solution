# Script PowerShell para Configurar Atualização Automática do Parquet
# Executa: .\scripts\setup_scheduled_task.ps1

$TaskName = "Agent_BI_Update_Parquet"
$ScriptPath = "C:\Users\André\Documents\Agent_Solution_BI\scripts\update_parquet_scheduled.bat"
$Description = "Atualização automática do Parquet a partir do SQL Server às 03:00h"

# Verificar se tarefa já existe e removê-la
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removendo tarefa existente..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Criar ação (executar o batch)
$Action = New-ScheduledTaskAction -Execute $ScriptPath

# Criar trigger (diariamente às 03:00h)
$Trigger = New-ScheduledTaskTrigger -Daily -At 3:00AM

# Criar configurações
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# Criar principal (executar com usuário atual)
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U

# Registrar a tarefa
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description $Description

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Tarefa agendada criada com sucesso!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Nome da tarefa: $TaskName"
Write-Host "Horário: Diariamente às 03:00h"
Write-Host "Script: $ScriptPath"
Write-Host ""
Write-Host "Para verificar: Get-ScheduledTask -TaskName '$TaskName'"
Write-Host "Para executar manualmente: Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "Para desabilitar: Disable-ScheduledTask -TaskName '$TaskName'"
Write-Host "Para remover: Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
