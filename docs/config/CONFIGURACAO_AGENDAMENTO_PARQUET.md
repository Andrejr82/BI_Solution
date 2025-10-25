# Configuração do Agendamento Automático do Parquet

## Visão Geral

Sistema de atualização automática do arquivo `admmat.parquet` a partir do SQL Server, executado diariamente às **03:00h** (horário de baixa carga).

## Arquivos Criados

1. **`scripts/update_parquet_from_sql.py`** - Script Python que atualiza o Parquet
2. **`scripts/update_parquet_scheduled.bat`** - Batch wrapper para execução agendada
3. **`scripts/setup_scheduled_task.ps1`** - Script PowerShell para configurar agendamento

## Método 1: Configuração Automática (Recomendado)

### Execute PowerShell como Administrador:

1. Clique com botão direito no **Iniciar** → **Windows PowerShell (Admin)**
2. Navegue até o diretório do projeto:
   ```powershell
   cd "C:\Users\André\Documents\Agent_Solution_BI"
   ```
3. Execute o script de configuração:
   ```powershell
   .\scripts\setup_scheduled_task.ps1
   ```

### Verificação:

```powershell
# Ver detalhes da tarefa
Get-ScheduledTask -TaskName "Agent_BI_Update_Parquet"

# Executar manualmente (para teste)
Start-ScheduledTask -TaskName "Agent_BI_Update_Parquet"

# Ver último resultado
Get-ScheduledTaskInfo -TaskName "Agent_BI_Update_Parquet"
```

## Método 2: Configuração Manual via GUI

### 1. Abrir Agendador de Tarefas

- Pressione `Win + R`
- Digite: `taskschd.msc`
- Pressione Enter

### 2. Criar Nova Tarefa

1. No menu **Ações** → **Criar Tarefa...**
2. Na aba **Geral**:
   - Nome: `Agent_BI_Update_Parquet`
   - Descrição: `Atualização automática do Parquet a partir do SQL Server`
   - Selecione: **Executar estando o usuário conectado ou não**
   - Desmarque: **Não armazenar senha**

### 3. Configurar Acionador (Trigger)

1. Aba **Acionadores** → **Novo...**
2. Configurações:
   - Iniciar a tarefa: **De acordo com um agendamento**
   - Configurações: **Diariamente**
   - Horário: **03:00:00**
   - Repetir: **Não**
   - Habilitada: **Sim**

### 4. Configurar Ação

1. Aba **Ações** → **Novo...**
2. Configurações:
   - Ação: **Iniciar um programa**
   - Programa/script:
     ```
     C:\Users\André\Documents\Agent_Solution_BI\scripts\update_parquet_scheduled.bat
     ```
   - Iniciar em:
     ```
     C:\Users\André\Documents\Agent_Solution_BI
     ```

### 5. Configurações Adicionais

1. Aba **Configurações**:
   - ✅ Permitir que a tarefa seja executada sob demanda
   - ✅ Executar tarefa logo que possível após inicialização perdida
   - ✅ Se a tarefa falhar, reiniciar a cada: **1 minuto**
   - ✅ Tentativas de reinicialização: **3**

## Verificação da Configuração

### Executar Teste Manual

1. Abrir PowerShell/CMD no diretório do projeto:
   ```cmd
   cd "C:\Users\André\Documents\Agent_Solution_BI"
   ```

2. Executar o batch diretamente:
   ```cmd
   scripts\update_parquet_scheduled.bat
   ```

3. Verificar logs:
   ```cmd
   type logs\parquet_update.log
   type logs\scheduled_updates.log
   ```

### Testar via Task Scheduler

```powershell
# Executar agora (teste)
Start-ScheduledTask -TaskName "Agent_BI_Update_Parquet"

# Verificar status
Get-ScheduledTaskInfo -TaskName "Agent_BI_Update_Parquet"

# Ver histórico
Get-ScheduledTask -TaskName "Agent_BI_Update_Parquet" | Get-ScheduledTaskInfo
```

## Relatórios Diários Automáticos

### Localização dos Relatórios

Após cada atualização, um relatório detalhado é gerado automaticamente em:
```
reports/parquet_updates/relatorio_YYYYMMDD.md
```

### Conteúdo do Relatório

Cada relatório inclui:

#### 1. Status da Atualização
- Sucesso ou falha da operação
- Timestamp da execução

#### 2. Estatísticas de Dados
- Linhas atualizadas
- Total de colunas
- Tamanho do arquivo Parquet
- Tempo total de execução

#### 3. Performance
- Tempo de leitura do SQL Server
- Tempo de gravação do Parquet
- Velocidade (linhas por segundo)

#### 4. Comparação com Versão Anterior
- Linhas adicionadas
- Linhas removidas
- Variação percentual

#### 5. Detalhes de Backup
- Nome do backup criado
- Total de backups mantidos

#### 6. Informações Técnicas
- Conexão SQL Server
- Chunks processados
- Configurações utilizadas

#### 7. Erros e Avisos
- Stack trace completo (se houver erros)
- Avisos durante a execução

### Exemplo de Relatório

Ver: `reports/parquet_updates/exemplo_relatorio.md`

### Retenção de Relatórios

- Últimos **30 dias** são mantidos automaticamente
- Relatórios mais antigos são removidos automaticamente

## Logs e Monitoramento

### Arquivos de Log

1. **`logs/parquet_update.log`** - Log detalhado do script Python
2. **`logs/scheduled_updates.log`** - Log resumido das execuções agendadas
3. **`reports/parquet_updates/relatorio_YYYYMMDD.md`** - Relatório diário estruturado
4. **Event Viewer** - Logs do Windows Task Scheduler

### Verificar Logs e Relatórios via PowerShell

```powershell
# Ver últimas 20 linhas do log
Get-Content logs\parquet_update.log -Tail 20

# Monitorar em tempo real
Get-Content logs\parquet_update.log -Wait

# Ver relatório mais recente
$latest = Get-ChildItem reports\parquet_updates\relatorio_*.md | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Get-Content $latest.FullName

# Listar todos os relatórios
Get-ChildItem reports\parquet_updates\relatorio_*.md | Format-Table Name, LastWriteTime, Length
```

## Backup Automático

O script mantém automaticamente os **últimos 7 backups** do Parquet:

- Formato: `admmat.backup_YYYYMMDD_HHMMSS.parquet`
- Localização: `data/parquet/`
- Limpeza: Automática (mantém apenas os 7 mais recentes)

## Solução de Problemas

### Tarefa não executa

1. **Verificar permissões**:
   - Tarefa precisa rodar com usuário que tem acesso ao SQL Server
   - Verificar se senha do usuário não expirou

2. **Verificar conexão SQL Server**:
   ```powershell
   # Testar conexão
   Test-NetConnection -ComputerName "FAMILIA\SQLJR" -Port 1433
   ```

3. **Verificar variáveis de ambiente**:
   - Arquivo `.env` deve estar configurado
   - Variáveis: DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

### Tarefa falha com erro

1. **Ver log de erro**:
   ```cmd
   type logs\parquet_update.log
   ```

2. **Executar manualmente para debug**:
   ```cmd
   python scripts\update_parquet_from_sql.py
   ```

3. **Verificar Event Viewer**:
   - `Win + R` → `eventvwr.msc`
   - Bibliotecas do Windows → Microsoft → Windows → TaskScheduler

## Desabilitar/Remover Agendamento

### Via PowerShell

```powershell
# Desabilitar (manter configuração)
Disable-ScheduledTask -TaskName "Agent_BI_Update_Parquet"

# Habilitar novamente
Enable-ScheduledTask -TaskName "Agent_BI_Update_Parquet"

# Remover completamente
Unregister-ScheduledTask -TaskName "Agent_BI_Update_Parquet" -Confirm:$false
```

### Via GUI

1. Abrir Agendador de Tarefas (`taskschd.msc`)
2. Localizar: **Agent_BI_Update_Parquet**
3. Botão direito → **Desabilitar** ou **Excluir**

## Performance Esperada

- **Tempo de execução**: 5-15 minutos (depende da carga do SQL Server)
- **Tamanho do Parquet**: ~30-50 MB
- **Linhas processadas**: ~1.1 milhão
- **Uso de memória**: ~500 MB (pico durante leitura)

## Integração com o Sistema

Após a atualização do Parquet às 03:00h:

1. **DirectQueryEngine** detecta automaticamente o novo arquivo
2. **Cache Dask** é limpo automaticamente na primeira query
3. Queries continuam usando **SQL Server como primário**
4. Parquet atualizado serve como **fallback** se SQL falhar

## Suporte

Em caso de problemas:

1. Verificar logs em `logs/`
2. Executar script manualmente para debug
3. Verificar Event Viewer do Windows
4. Revisar configurações de rede/firewall

---

**Data de criação**: 11/10/2025
**Versão**: 1.0
