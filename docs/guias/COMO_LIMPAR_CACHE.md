# Guia: Como Limpar o Cache do Sistema

**Tipo:** Guia Operacional
**Status:** Atual
**Criado em:** 2025-10-17
**Última atualização:** 2025-10-17
**Autor:** Doc Agent
**Relacionado a:**
- [Fix: Sistema de Cache](../fixes/FIX_CACHE_SYSTEM.md)
- [Transferências Master](../implementacoes/TRANSFERENCIAS_MASTER.md)

---

## Resumo Executivo

Este guia descreve os procedimentos para limpeza de cache do sistema Agent_Solution_BI. O cache é utilizado para otimizar performance de consultas, mas pode precisar ser limpo em casos de:

- Dados inconsistentes ou desatualizados
- Mudanças na estrutura do banco de dados
- Testes e desenvolvimento
- Problemas de performance por cache corrompido
- Atualizações de sistema

**Tempo estimado:** 2-5 minutos
**Nível de risco:** Baixo (não afeta dados permanentes)

---

## Índice

1. [Tipos de Cache](#tipos-de-cache)
2. [Quando Limpar o Cache](#quando-limpar-o-cache)
3. [Métodos de Limpeza](#metodos-de-limpeza)
4. [Limpeza via Interface Streamlit](#limpeza-via-interface-streamlit)
5. [Limpeza via Script](#limpeza-via-script)
6. [Limpeza Manual](#limpeza-manual)
7. [Verificação Pós-Limpeza](#verificacao-pos-limpeza)
8. [Troubleshooting](#troubleshooting)
9. [Boas Práticas](#boas-praticas)

---

## Tipos de Cache

O sistema Agent_Solution_BI utiliza múltiplos níveis de cache:

### 1. Cache de Consultas SQL
**Localização:** `C:\Users\André\Documents\Agent_Solution_BI\data\cache\`
**Formato:** Arquivos JSON com hash MD5
**TTL:** 30 minutos (configurável)
**Tamanho típico:** 50-100 MB

**Exemplo de arquivo:**
```
data/cache/a7d3be14e07a13eac35d2696b6f9cdbc.json
```

**Conteúdo:**
```json
{
  "query": "SELECT * FROM Transferencias_Unes WHERE...",
  "params": {"une_origem": "UNE1"},
  "timestamp": "2025-10-17T10:30:00",
  "ttl": 1800,
  "data": [...]
}
```

### 2. Cache de Grafos de Agentes
**Localização:** `C:\Users\André\Documents\Agent_Solution_BI\data\cache_agent_graph\`
**Formato:** Arquivos Pickle (.pkl)
**TTL:** 60 minutos
**Tamanho típico:** 10-30 MB

**Exemplo de arquivo:**
```
data/cache_agent_graph/4628b41d2deea0f8a311f871bc420292.pkl
```

### 3. Cache de Sessão Streamlit
**Localização:** Memória RAM (session_state)
**Formato:** Objetos Python
**TTL:** Duração da sessão do usuário
**Tamanho típico:** 5-20 MB

### 4. Cache de Learning/Patterns
**Localização:** `C:\Users\André\Documents\Agent_Solution_BI\data\learning\`
**Formato:** JSON/JSONL
**TTL:** Permanente (não é cache, são dados de aprendizado)
**Tamanho típico:** 1-5 MB

**Nota:** Não limpar arquivos de learning sem backup!

---

## Quando Limpar o Cache

### Sintomas que Indicam Necessidade de Limpeza

#### Alta Prioridade (Limpar Imediatamente)
- ❌ Dados desatualizados sendo exibidos
- ❌ Erros de "cache corrompido" nos logs
- ❌ Consultas retornando resultados inconsistentes
- ❌ Sistema travando ou ficando lento após várias consultas

#### Média Prioridade (Limpar em Manutenção)
- ⚠️ Cache ocupando >500 MB de espaço
- ⚠️ Após atualização do schema do banco de dados
- ⚠️ Após mudanças em core/tools/une_tools.py
- ⚠️ Performance degradando ao longo do dia

#### Baixa Prioridade (Opcional)
- ℹ️ Testes de desenvolvimento
- ℹ️ Mudança de ambiente (dev → prod)
- ℹ️ Manutenção preventiva mensal

### Quando NÃO Limpar o Cache

- ✅ Sistema funcionando normalmente
- ✅ Durante horário de pico de uso
- ✅ Antes de backup (fazer backup primeiro)
- ✅ Sem motivo específico (cache melhora performance)

---

## Métodos de Limpeza

### Comparação de Métodos

| Método | Velocidade | Facilidade | Granularidade | Recomendado Para |
|--------|-----------|-----------|---------------|-----------------|
| Interface Streamlit | ⚡ Rápido | ⭐⭐⭐ Fácil | Cache de consultas | Usuários finais |
| Script Python | ⚡⚡ Muito Rápido | ⭐⭐ Médio | Todos os tipos | Administradores |
| Script Batch | ⚡⚡⚡ Instantâneo | ⭐⭐⭐ Fácil | Todos os tipos | Windows users |
| Manual | 🐌 Lento | ⭐ Difícil | Total | Emergências |

---

## Limpeza via Interface Streamlit

### Método 1: Botão de Limpeza (Recomendado)

**Passo a Passo:**

1. Acesse a aplicação Streamlit
2. Navegue até a página **"Transferências"** ou **"Configurações"**
3. Localize o botão **"Limpar Cache"** na sidebar ou no topo da página
4. Clique no botão
5. Aguarde a confirmação: "Cache limpo com sucesso!"

**Código de Referência:**
```python
# Em pages/7_📦_Transferências.py
if st.sidebar.button("🗑️ Limpar Cache"):
    limpar_cache_transferencias()
    st.success("Cache de transferências limpo com sucesso!")
    st.rerun()
```

**Vantagens:**
- ✅ Interface amigável
- ✅ Não requer conhecimento técnico
- ✅ Confirmação visual imediata
- ✅ Seguro (não afeta outros dados)

**Desvantagens:**
- ❌ Limpa apenas cache de consultas SQL
- ❌ Requer aplicação Streamlit rodando

### Método 2: Session State Reset

**Quando usar:** Cache de sessão corrompido

**Passo a Passo:**

1. Na aplicação Streamlit, pressione `R` (rerun)
2. Ou clique em "Rerun" no menu superior direito
3. Ou feche e reabra o navegador

**Vantagens:**
- ✅ Rápido
- ✅ Limpa cache de sessão
- ✅ Não requer permissões

**Desvantagens:**
- ❌ Não limpa cache persistente
- ❌ Perde estado da aplicação

---

## Limpeza via Script

### Método 3: Script Python (Mais Completo)

**Localização:** `C:\Users\André\Documents\Agent_Solution_BI\scripts\limpar_cache.py`

**Uso Básico:**
```bash
# Navegar até o diretório do projeto
cd C:\Users\André\Documents\Agent_Solution_BI

# Executar script
python scripts/limpar_cache.py
```

**Opções Avançadas:**
```bash
# Limpar apenas cache SQL
python scripts/limpar_cache.py --tipo sql

# Limpar apenas cache de grafos
python scripts/limpar_cache.py --tipo graph

# Limpar tudo (exceto learning)
python scripts/limpar_cache.py --all

# Modo dry-run (mostra o que seria deletado)
python scripts/limpar_cache.py --dry-run

# Limpar cache mais antigo que N dias
python scripts/limpar_cache.py --older-than 7
```

**Código do Script:**
```python
# scripts/limpar_cache.py
import os
import glob
import shutil
from datetime import datetime, timedelta
import argparse

def limpar_cache_sql(older_than_days=None):
    """Limpa cache de consultas SQL"""
    cache_dir = "data/cache"
    arquivos_deletados = 0

    for arquivo in glob.glob(f"{cache_dir}/*.json"):
        if older_than_days:
            # Verificar data do arquivo
            file_time = datetime.fromtimestamp(os.path.getmtime(arquivo))
            if datetime.now() - file_time < timedelta(days=older_than_days):
                continue

        os.remove(arquivo)
        arquivos_deletados += 1

    print(f"✅ {arquivos_deletados} arquivos de cache SQL deletados")
    return arquivos_deletados

def limpar_cache_graph(older_than_days=None):
    """Limpa cache de grafos de agentes"""
    cache_dir = "data/cache_agent_graph"
    arquivos_deletados = 0

    for arquivo in glob.glob(f"{cache_dir}/*.pkl"):
        if older_than_days:
            file_time = datetime.fromtimestamp(os.path.getmtime(arquivo))
            if datetime.now() - file_time < timedelta(days=older_than_days):
                continue

        os.remove(arquivo)
        arquivos_deletados += 1

    print(f"✅ {arquivos_deletados} arquivos de cache de grafos deletados")
    return arquivos_deletados

def limpar_tudo(older_than_days=None):
    """Limpa todos os tipos de cache"""
    total = 0
    total += limpar_cache_sql(older_than_days)
    total += limpar_cache_graph(older_than_days)
    print(f"\n🎉 Total: {total} arquivos deletados")
    return total

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Limpar cache do Agent_Solution_BI")
    parser.add_argument("--tipo", choices=["sql", "graph", "all"], default="all")
    parser.add_argument("--older-than", type=int, help="Dias")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    print("🧹 Limpando cache...")

    if args.dry_run:
        print("⚠️ MODO DRY-RUN (nada será deletado)")

    if args.tipo == "sql":
        limpar_cache_sql(args.older_than)
    elif args.tipo == "graph":
        limpar_cache_graph(args.older_than)
    else:
        limpar_tudo(args.older_than)
```

**Vantagens:**
- ✅ Controle granular
- ✅ Opções avançadas
- ✅ Pode ser agendado (cron/task scheduler)
- ✅ Logs detalhados

**Desvantagens:**
- ❌ Requer Python instalado
- ❌ Linha de comando

### Método 4: Script Batch (Windows)

**Localização:** `C:\Users\André\Documents\Agent_Solution_BI\scripts\limpar_cache.bat`

**Uso:**
1. Navegue até `scripts/` no Windows Explorer
2. Clique duplo em `limpar_cache.bat`
3. Confirme a ação no prompt

**Código do Script:**
```batch
@echo off
echo ============================================
echo   Limpeza de Cache - Agent_Solution_BI
echo ============================================
echo.

set "CACHE_SQL=..\data\cache"
set "CACHE_GRAPH=..\data\cache_agent_graph"

echo Limpando cache SQL...
del /Q "%CACHE_SQL%\*.json" 2>nul
echo ✓ Cache SQL limpo

echo.
echo Limpando cache de grafos...
del /Q "%CACHE_GRAPH%\*.pkl" 2>nul
echo ✓ Cache de grafos limpo

echo.
echo ============================================
echo   Limpeza concluída com sucesso!
echo ============================================
pause
```

**Vantagens:**
- ✅ Muito fácil de usar
- ✅ Não requer Python
- ✅ Interface visual (prompt)

**Desvantagens:**
- ❌ Apenas Windows
- ❌ Menos controle
- ❌ Sem validações

---

## Limpeza Manual

### Método 5: Deletar Arquivos Manualmente

**Quando usar:** Emergências, acesso remoto sem shell

**Passo a Passo:**

1. Abra o Windows Explorer
2. Navegue até `C:\Users\André\Documents\Agent_Solution_BI\data\`
3. Entre na pasta `cache/`
4. Selecione todos os arquivos `.json` (Ctrl+A)
5. Delete (Delete ou Shift+Delete para permanente)
6. Repita para `cache_agent_graph/` (arquivos `.pkl`)

**Importante:**
- ⚠️ **NÃO deletar as pastas**, apenas os arquivos dentro
- ⚠️ **NÃO deletar** arquivos em `data/learning/` (são dados de aprendizado)
- ⚠️ **NÃO deletar** arquivos em `data/query_history/` (são históricos)

**Estrutura Correta Após Limpeza:**
```
data/
├── cache/                    # Vazio (OK)
├── cache_agent_graph/        # Vazio (OK)
├── learning/                 # Manter todos os arquivos
│   ├── error_counts_*.json
│   ├── error_log_*.jsonl
│   └── successful_queries_*.jsonl
├── query_history/            # Manter todos os arquivos
│   └── history_*.json
└── query_patterns.json       # Manter
```

---

## Verificação Pós-Limpeza

### Checklist de Verificação

Após limpar o cache, verifique:

#### 1. Cache Foi Limpo
```bash
# Via linha de comando
dir data\cache\*.json
dir data\cache_agent_graph\*.pkl

# Deve retornar "0 arquivo(s)" ou "File Not Found"
```

#### 2. Aplicação Funciona
1. Inicie o Streamlit: `streamlit run app.py`
2. Acesse uma página (ex: Transferências)
3. Faça uma consulta
4. Verifique se retorna dados

#### 3. Cache Recria Automaticamente
1. Faça a mesma consulta novamente
2. Verifique que está mais rápida (cache foi criado)
3. Confirme novos arquivos em `data/cache/`

```bash
# Deve mostrar novos arquivos
dir data\cache\*.json
```

#### 4. Logs Sem Erros
```bash
# Verificar logs (se existirem)
type logs\app.log | findstr /I "error cache"
```

### Testes de Validação

**Teste 1: Consulta Básica**
```python
# No Python ou no app
from core.tools.une_tools import get_transferencias_unes

resultado = get_transferencias_unes(limit=10)
assert resultado["success"] == True
print("✅ Consulta básica OK")
```

**Teste 2: Cache Funcional**
```python
import time

# Primeira consulta (cria cache)
start = time.time()
get_transferencias_unes(une_origem="UNE1")
time1 = time.time() - start

# Segunda consulta (usa cache)
start = time.time()
get_transferencias_unes(une_origem="UNE1")
time2 = time.time() - start

assert time2 < time1 * 0.5  # Deve ser pelo menos 2x mais rápido
print("✅ Cache funcional OK")
```

---

## Troubleshooting

### Problema 1: "Permissão Negada" ao Deletar

**Sintomas:**
```
Erro: Acesso negado ao deletar arquivo X
```

**Causas:**
- Arquivo em uso pela aplicação Streamlit
- Arquivo bloqueado pelo sistema
- Falta de permissões

**Soluções:**

1. Feche o Streamlit:
```bash
# Ctrl+C no terminal onde Streamlit está rodando
# Ou via Task Manager: matar processo python.exe
```

2. Verifique processos:
```bash
tasklist | findstr python
```

3. Execute como Administrador:
```bash
# Clique direito no script .bat → "Executar como administrador"
```

4. Use ferramenta de desbloqueio:
```bash
# Instalar handle.exe (Sysinternals)
handle.exe arquivo.json
# Matar processo que está segurando o arquivo
```

### Problema 2: Cache Recria Instantaneamente

**Sintomas:**
- Cache deletado mas volta imediatamente
- Arquivos reaparecem após limpeza

**Causas:**
- Streamlit rodando em background
- Serviço automatizado criando cache
- Múltiplas instâncias da aplicação

**Soluções:**

1. Pare TODOS os processos Python:
```bash
taskkill /F /IM python.exe
```

2. Verifique serviços:
```bash
services.msc
# Procurar por serviços relacionados
```

3. Reinicie a máquina (última opção)

### Problema 3: Cache Limpo Mas Dados Ainda Desatualizados

**Sintomas:**
- Cache deletado mas dados antigos aparecem
- Limpeza não resolveu inconsistência

**Causas:**
- Cache em múltiplos níveis (ex: browser cache)
- Session state do Streamlit
- Cache no banco de dados

**Soluções:**

1. Limpe cache do navegador:
```
Chrome: Ctrl+Shift+Delete
Firefox: Ctrl+Shift+Delete
Edge: Ctrl+Shift+Delete
```

2. Force reload no Streamlit:
```python
# No app
st.cache_data.clear()
st.cache_resource.clear()
```

3. Reinicie sessão:
- Feche aba do navegador
- Limpe cookies
- Abra nova aba

4. Verifique cache do banco:
```sql
-- SQL Server
DBCC FREEPROCCACHE;  -- Limpa cache de queries
DBCC DROPCLEANBUFFERS;  -- Limpa cache de dados
```

### Problema 4: Erro "Module Not Found" Após Limpeza

**Sintomas:**
```
ImportError: No module named 'xxx'
```

**Causas:**
- Script de limpeza deletou arquivos errados
- Arquivo `.pkl` corrompido de import

**Soluções:**

1. Verifique integridade:
```bash
git status
# Se arquivos do código foram deletados, restaure:
git checkout -- arquivo_deletado.py
```

2. Reinstale dependências:
```bash
pip install -r requirements.txt
```

3. Restaure backup (se disponível)

---

## Boas Práticas

### Frequência de Limpeza

**Recomendações:**

| Ambiente | Frequência | Método |
|----------|-----------|--------|
| Desenvolvimento | Diária ou sob demanda | Script Python / Manual |
| Homologação | Semanal | Script agendado |
| Produção | Mensal (ou sob demanda) | Script Python com backup |

### Automação de Limpeza

**Windows Task Scheduler:**

1. Abra Task Scheduler (`taskschd.msc`)
2. Criar Tarefa Básica
3. Nome: "Limpar Cache Agent_Solution_BI"
4. Gatilho: Semanal, Domingo, 02:00
5. Ação: Iniciar programa
   - Programa: `python.exe`
   - Argumentos: `scripts/limpar_cache.py --older-than 7`
   - Iniciar em: `C:\Users\André\Documents\Agent_Solution_BI`

**Linux Cron:**
```bash
# crontab -e
0 2 * * 0 cd /path/to/Agent_Solution_BI && python scripts/limpar_cache.py --older-than 7
```

### Backup Antes de Limpar

**Criar Backup:**
```bash
# Windows
xcopy data\cache data\cache_backup\ /E /I
xcopy data\cache_agent_graph data\cache_agent_graph_backup\ /E /I

# Linux
cp -r data/cache data/cache_backup
cp -r data/cache_agent_graph data/cache_agent_graph_backup
```

**Restaurar Backup:**
```bash
# Windows
xcopy data\cache_backup\* data\cache\ /E /Y

# Linux
cp -r data/cache_backup/* data/cache/
```

### Monitoramento de Cache

**Script de Monitoramento:**
```python
# scripts/monitor_cache.py
import os
import glob

def tamanho_cache():
    total_sql = sum(os.path.getsize(f) for f in glob.glob("data/cache/*.json"))
    total_graph = sum(os.path.getsize(f) for f in glob.glob("data/cache_agent_graph/*.pkl"))

    print(f"Cache SQL: {total_sql / 1024 / 1024:.2f} MB")
    print(f"Cache Graph: {total_graph / 1024 / 1024:.2f} MB")
    print(f"Total: {(total_sql + total_graph) / 1024 / 1024:.2f} MB")

    if total_sql + total_graph > 500 * 1024 * 1024:  # 500 MB
        print("⚠️ Cache acima de 500 MB - considere limpeza")

if __name__ == "__main__":
    tamanho_cache()
```

**Executar:**
```bash
python scripts/monitor_cache.py
```

### Logs de Limpeza

**Adicionar ao Script:**
```python
import logging
from datetime import datetime

logging.basicConfig(
    filename=f"logs/cache_cleanup_{datetime.now().strftime('%Y%m%d')}.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

logging.info(f"Limpeza iniciada - {arquivos_deletados} arquivos deletados")
```

---

## Referências

### Documentos Relacionados
- [Fix: Sistema de Cache](../fixes/FIX_CACHE_SYSTEM.md)
- [Transferências Master](../implementacoes/TRANSFERENCIAS_MASTER.md)
- [LIMPAR_CACHE_README.md](../arquivados/cache/LIMPAR_CACHE_README.md) (arquivado)

### Scripts
- `C:\Users\André\Documents\Agent_Solution_BI\scripts\limpar_cache.py`
- `C:\Users\André\Documents\Agent_Solution_BI\scripts\limpar_cache.bat`
- `C:\Users\André\Documents\Agent_Solution_BI\scripts\monitor_cache.py`

### Configurações
- `core/tools/une_tools.py` (lógica de cache)
- `app.py` (configuração Streamlit cache)

---

**Última revisão:** 2025-10-17 por Doc Agent
