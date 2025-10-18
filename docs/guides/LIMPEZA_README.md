# Guia de Limpeza do Projeto Agent_Solution_BI

**Deploy Agent - 2025-10-17**

## Visão Geral

Este documento descreve o processo completo de limpeza e manutenção do projeto Agent_Solution_BI, incluindo remoção de arquivos temporários, limpeza de cache e reorganização de scripts.

## Arquivos de Limpeza

### Scripts Principais

1. **cleanup_project.py** - Script Python completo de limpeza
   - Remove arquivos temporários
   - Limpa cache desatualizado (>3 dias)
   - Consolida scripts duplicados
   - Organiza estrutura de diretórios
   - Gera relatório detalhado

2. **EXECUTAR_LIMPEZA.bat** - Script batch para execução fácil
   - Interface amigável
   - Confirmação antes de executar
   - Integração com Git

3. **scripts/limpar_cache.py** - Script específico para cache
   - Limpeza rápida apenas de cache
   - Mantém dados recentes

## Uso

### Limpeza Completa (Recomendado)

```bash
# Windows
EXECUTAR_LIMPEZA.bat

# Linux/Mac
python cleanup_project.py
```

### Limpeza Apenas de Cache

```bash
# Windows
cd scripts
limpar_cache.bat

# Linux/Mac
python scripts/limpar_cache.py
```

## Processo de Limpeza

### 1. Arquivos Temporários

**Removidos:**
- `temp_read_transferencias.py`
- `temp_*.py`
- `scratch_*.py`

**Localização:** Raiz do projeto

### 2. Cache

**Diretórios:**
- `data/cache/` - Cache de queries SQL
- `data/cache_agent_graph/` - Cache de grafos de agentes

**Política de Retenção:**
- Manter: Últimos 3 dias
- Remover: Mais de 3 dias
- Verificar: A cada 7 dias

**Estrutura Mantida:**
```
data/
├── cache/              # Cache de queries (JSONs)
├── cache_agent_graph/  # Cache de grafos (PKL)
├── feedback/           # Feedback de usuários
├── learning/           # Dados de aprendizado
└── query_history/      # Histórico de queries
```

### 3. Scripts Consolidados

**Antes:**
- `clear_cache.bat` (raiz)
- `scripts/clear_cache.bat`
- `scripts/limpar_cache.bat`
- `scripts/limpar_cache.py`

**Depois:**
- `scripts/limpar_cache.py` (versão completa)
- `scripts/limpar_cache.bat` (unificado)

### 4. Scripts de Diagnóstico

**Reorganização:**

```
scripts/
├── diagnostics/                              # NOVO
│   ├── README.md
│   ├── diagnostico_sugestoes_automaticas.py
│   ├── diagnostico_transferencias_unes.py
│   ├── DIAGNOSTICO_TRANSFERENCIAS.bat
│   └── analyze_une1_data.py
├── limpar_cache.py
└── limpar_cache.bat
```

## Backup

### Localização

Todos os arquivos removidos são copiados para:
```
backup_cleanup/
├── temp_read_transferencias.py
├── clear_cache.bat
└── ...
```

### Retenção de Backup

- **Duração:** 30 dias
- **Limpeza:** Manual
- **Localização:** `.gitignore` (não versionado)

## Relatórios

### Relatório JSON

**Arquivo:** `.cleanup_report.json`

**Conteúdo:**
```json
{
  "timestamp": "2025-10-17T...",
  "project": "Agent_Solution_BI",
  "agent": "Deploy Agent",
  "results": [...],
  "summary": {
    "total_files_removed": 150,
    "total_files_moved": 4,
    "total_files_created": 3,
    "total_space_freed_mb": 12.5,
    "total_errors": 0
  }
}
```

### Relatório de Console

Gerado automaticamente durante a execução com:
- Timestamp de cada ação
- Status colorido (INFO/SUCCESS/WARNING/ERROR)
- Resumo executivo
- Detalhamento por categoria

## Integração com Git

### Status Atual

O Git mostra 118 arquivos de cache deletados (marcados com "D").

### Ação Recomendada

```bash
# Adicionar todas as deleções ao staging
git add -u

# Ou adicionar tudo (incluindo novos arquivos)
git add -A

# Commit
git commit -m "chore: Limpeza de arquivos temporários e reorganização de scripts"

# Push
git push origin main
```

### Arquivos Não Versionados

Conforme `.gitignore_cleanup`:
- Cache (`data/cache/*.json`)
- Cache de grafos (`data/cache_agent_graph/*.pkl`)
- Backups (`backup_*/`)
- Arquivos temporários (`temp_*.py`)
- Relatórios de limpeza (`.cleanup_report.*`)

## Automação

### Script Agendado (Windows)

```batch
REM Criar tarefa agendada para limpeza semanal
schtasks /create /tn "Agent_BI_Cleanup" /tr "C:\path\to\EXECUTAR_LIMPEZA.bat" /sc weekly /d SUN /st 02:00
```

### Cron (Linux/Mac)

```bash
# Adicionar ao crontab para execução semanal (domingos às 2h)
0 2 * * 0 cd /path/to/Agent_Solution_BI && python cleanup_project.py
```

## Segurança

### Dados Protegidos

**NUNCA são deletados:**
- `data/feedback/` - Feedback de usuários
- `data/learning/` - Dados de aprendizado
- `data/query_history/` - Histórico de queries
- `data/query_patterns.json` - Padrões aprendidos
- Código-fonte (`core/`, `pages/`, etc.)
- Configurações (`config.py`, `.env`)
- Documentação (`docs/`, `README.md`)

### Credenciais

**Nunca expor:**
- Arquivos `.env`
- Secrets do GitHub
- Tokens de API
- Senhas de banco de dados

**Verificar antes de commit:**
```bash
git diff --cached
```

## Manutenção Recomendada

### Diária
- Nenhuma ação necessária (cache auto-gerenciado)

### Semanal
- Executar limpeza completa: `EXECUTAR_LIMPEZA.bat`
- Verificar relatório de limpeza
- Revisar espaço em disco

### Mensal
- Revisar backup_cleanup/ e deletar backups antigos
- Atualizar `.gitignore` se necessário
- Verificar logs em `data/learning/error_log_*.jsonl`

### Trimestral
- Revisar e arquivar dados de learning antigos
- Compactar histórico de queries antigo
- Atualizar documentação

## Troubleshooting

### Erro: "Python não encontrado"

**Solução:**
```bash
# Verificar instalação
python --version

# Instalar Python (Windows)
# Download: https://www.python.org/downloads/

# Adicionar ao PATH
set PATH=%PATH%;C:\Python311
```

### Erro: "Permissão negada"

**Solução:**
```bash
# Windows: Executar como Administrador
# Linux/Mac: Usar sudo
sudo python cleanup_project.py
```

### Cache não está sendo limpo

**Verificar:**
1. Permissões de escrita em `data/cache/`
2. Arquivos não estão bloqueados por outro processo
3. Política de retenção em `cleanup_project.py`

**Debug:**
```python
# Verificar idade dos arquivos
import os
from datetime import datetime
from pathlib import Path

cache_dir = Path("data/cache")
for f in cache_dir.glob("*.json"):
    age = (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days
    print(f"{f.name}: {age} dias")
```

### Git mostra muitos arquivos deletados

**Solução:**
```bash
# Staged deletions (adicionar ao commit)
git add -u

# Unstaged deletions (restaurar arquivos)
git restore .
```

## Contato e Suporte

**Deploy Agent**
- Documentação completa em: `docs/`
- Issues: GitHub Issues
- Logs: `data/learning/error_log_*.jsonl`

---

**Última Atualização:** 2025-10-17
**Versão:** 1.0
**Autor:** Deploy Agent
