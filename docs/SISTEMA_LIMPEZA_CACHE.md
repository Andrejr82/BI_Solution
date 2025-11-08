# Sistema Automático de Limpeza de Cache

## 📋 Visão Geral

O Agent_Solution_BI implementa um sistema inteligente de limpeza automática de cache que:

✅ Remove arquivos de cache antigos automaticamente
✅ Detecta mudanças no código e invalida cache
✅ Libera espaço em disco
✅ Melhora performance do sistema
✅ É totalmente configurável via `.env`

---

## 🚀 Funcionamento

### Execução Automática

O sistema é executado **automaticamente** no startup do Streamlit, limpando:

1. **`__pycache__/`** - Bytecode Python compilado
2. **`.streamlit/cache/`** - Cache do Streamlit
3. **`data/cache/`** - Cache de respostas LLM
4. **`data/cache_agent_graph/`** - Cache de grafos

### Versionamento Inteligente

O sistema gera um hash único baseado nos arquivos `.py` do projeto. Quando o código é modificado:

- 🔄 **Cache é invalidado automaticamente**
- 🗑️ **Todos os arquivos antigos são removidos**
- ✅ **Nova versão é registrada**

---

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```bash
# Habilitar/desabilitar limpeza automática (default: true)
CACHE_AUTO_CLEAN=true

# Idade máxima dos arquivos de cache em dias (default: 7)
CACHE_MAX_AGE_DAYS=7

# Forçar limpeza completa ignorando idade (default: false)
CACHE_FORCE_CLEAN=false
```

### Streamlit Secrets (.streamlit/secrets.toml)

```toml
CACHE_AUTO_CLEAN = true
CACHE_MAX_AGE_DAYS = 7
CACHE_FORCE_CLEAN = false
```

---

## 📊 Logs e Monitoramento

O sistema registra todas as operações no log:

```
🧹 Executando limpeza automática de cache (max_age: 7d, force: false)...
✅ Cache limpo: 42 arquivos removidos (15.32 MB)
🔄 Cache invalidado - código foi modificado
```

### Informações Registradas

- Total de arquivos removidos
- Espaço liberado (MB)
- Versão do código (hash)
- Se cache foi invalidado por mudanças

---

## 🛠️ Uso Manual

### Executar Limpeza Manualmente

```python
from core.utils.cache_cleaner import run_cache_cleanup

# Limpeza normal (arquivos > 7 dias)
stats = run_cache_cleanup(max_age_days=7, force=False)

# Limpeza completa (todos os arquivos)
stats = run_cache_cleanup(force=True)

# Verificar estatísticas
print(f"Removidos: {stats['pycache_removed'] + stats['old_files_removed']} arquivos")
print(f"Espaço: {stats['pycache_size_mb'] + stats['old_files_size_mb']:.2f} MB")
```

### Teste Standalone

```bash
cd C:\Users\André\Documents\Agent_Solution_BI
python core/utils/cache_cleaner.py
```

---

## 📁 Estrutura de Arquivos

```
Agent_Solution_BI/
├── core/
│   └── utils/
│       └── cache_cleaner.py      # Módulo de limpeza
├── data/
│   ├── cache/                     # Cache LLM (limpável)
│   ├── cache_agent_graph/         # Cache grafos (limpável)
│   └── .cache_version             # Info de versionamento
├── __pycache__/                   # Bytecode (limpável)
└── .streamlit/
    └── cache/                      # Cache Streamlit (limpável)
```

---

## ⚡ Performance

### Antes da Implementação
- Cache acumulava indefinidamente
- Limpeza manual necessária
- Risco de cache desatualizado

### Depois da Implementação
- ✅ Limpeza automática
- ✅ Cache sempre atualizado
- ✅ Espaço em disco otimizado
- ✅ Zero intervenção manual

---

## 🔍 Troubleshooting

### "Limpeza de cache não executada"

**Causa**: `CACHE_AUTO_CLEAN=false` no `.env`
**Solução**: Definir `CACHE_AUTO_CLEAN=true`

### "Erro na limpeza de cache"

**Causa**: Permissões insuficientes
**Solução**: Executar com permissões adequadas ou verificar logs

### Desabilitar Limpeza Temporariamente

```bash
# No .env
CACHE_AUTO_CLEAN=false
```

---

## 📝 Changelog

### v2.0 (2025-11-02)
- ✅ Sistema automático de limpeza implementado
- ✅ Versionamento por hash de código
- ✅ Configuração via `.env` e `secrets.toml`
- ✅ Logs estruturados
- ✅ Integração com Streamlit startup

---

## 🎯 Benefícios

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Manutenção** | Manual | Automática |
| **Espaço em Disco** | Crescimento ilimitado | Controlado |
| **Performance** | Cache desatualizado | Sempre fresco |
| **Confiabilidade** | Dependente de intervenção | Zero touch |

---

## 📚 Referências

- **Módulo**: `core/utils/cache_cleaner.py`
- **Integração**: `streamlit_app.py` (linhas 44-84)
- **Configuração**: `core/config/safe_settings.py` (linhas 38-41)
