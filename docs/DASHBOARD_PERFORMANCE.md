# 🚀 Dashboard de Performance - Guia Completo

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Funcionalidades](#funcionalidades)
3. [Como Usar](#como-usar)
4. [Integrando Tracking no Código](#integrando-tracking-no-código)
5. [Métricas Disponíveis](#métricas-disponíveis)
6. [Alertas de Performance](#alertas-de-performance)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

O **Dashboard de Performance v2.2** é um sistema de monitoramento em tempo real que rastreia:

- ⏱️ **Tempo de queries** (SQL, Parquet, LLM)
- 💾 **Cache hit/miss rate**
- 🚀 **Tempo de inicialização** de componentes
- ❌ **Taxa de erros**
- 📈 **Throughput** (queries por minuto)

### Acesso

O dashboard está disponível na página **"Monitoramento"** (apenas para administradores):

```
http://localhost:8501/Monitoramento
```

---

## 🌟 Funcionalidades

### 1. **Métricas Principais** (Cards no Topo)

- **Uptime**: Tempo desde última inicialização
- **Tempo Médio Query**: Com P95 (95º percentil)
- **Cache Hit Rate**: Porcentagem de cache hits
- **Queries/min**: Taxa de processamento
- **Taxa de Erro**: Porcentagem de falhas

### 2. **Performance Detalhada**

Três tabelas com estatísticas:

- **Queries**: Min/Média/P95/Máximo
- **Cache**: Hits/Misses/Hit Rate
- **Startup**: Tempos de inicialização de componentes

### 3. **Queries Recentes & Erros**

- **Últimas 10 queries**: Timestamp, duração, tipo, status
- **Últimos 10 erros**: Timestamp, mensagem de erro

### 4. **Estatísticas Lifetime**

Acumuladores desde a inicialização do sistema:

- Total de queries processadas
- Total de cache hits
- Cache hit rate global
- Total de erros

### 5. **Alertas Inteligentes**

O sistema emite alertas automáticos quando:

- ⚡ Tempo médio de query > 3000ms (🟡 ATENÇÃO) ou > 5000ms (🔴 CRÍTICO)
- 💾 Cache hit rate < 30% com volume significativo (🟡 ATENÇÃO)
- ❌ Taxa de erro > 5% (🟡 ATENÇÃO) ou > 10% (🔴 CRÍTICO)
- 🔥 Mais de 10 erros na janela de tempo (🔴 CRÍTICO)

### 6. **Exportação de Métricas**

Botão para salvar snapshot em formato JSON:

```
data/metrics/metrics_YYYYMMDD_HHMMSS.json
```

---

## 🎮 Como Usar

### Acessar o Dashboard

1. Faça login como **administrador**
2. Navegue para **"Monitoramento"** na sidebar
3. O dashboard de performance aparece no topo da página

### Selecionar Janela de Tempo

Use o dropdown para escolher o período de análise:

- **5 minutos**: Monitoramento em tempo quase-real
- **15 minutos**: Análise de curto prazo
- **30 minutos**: Análise de médio prazo
- **60 minutos** (padrão): Visão horária
- **2 horas**: Análise de longo prazo
- **4 horas**: Visão estendida

### Atualizar Métricas

Clique no botão **"🔄 Atualizar"** para refresh manual ou recarregue a página.

### Interpretar as Cores

#### Tempo de Query

- 🟢 **Normal**: < 3000ms (verde)
- 🟡 **Atenção**: 3000-5000ms (amarelo)
- 🔴 **Crítico**: > 5000ms (vermelho)

#### Cache Hit Rate

- 🟢 **Bom**: ≥ 50% (verde)
- 🔴 **Ruim**: < 50% (vermelho)

#### Taxa de Erro

- 🟢 **Normal**: ≤ 5% (verde)
- 🔴 **Crítico**: > 5% (vermelho)

---

## 🛠️ Integrando Tracking no Código

### 1. Rastrear Tempo de Startup

```python
from core.utils.performance_integration import track_startup

# Context manager (recomendado)
with track_startup("backend"):
    backend = initialize_backend()

with track_startup("llm"):
    llm_adapter = create_llm_adapter()
```

### 2. Rastrear Queries

#### Usando Decorator

```python
from core.utils.performance_integration import track_query_performance

@track_query_performance("sql")
def execute_sql_query(query: str):
    # Seu código aqui
    results = db.execute(query)
    return results

@track_query_performance("parquet")
def read_parquet_data(file_path: str):
    df = pl.read_parquet(file_path)
    return df

@track_query_performance("llm")
def call_llm(prompt: str):
    response = llm.invoke(prompt)
    return response
```

#### Usando Context Manager

```python
from core.utils.performance_integration import track_query_context

with track_query_context("sql"):
    results = db.execute(query)

with track_query_context("parquet"):
    df = pl.read_parquet(file_path)
```

### 3. Rastrear Cache Operations

#### Usando Decorator

```python
from core.utils.performance_integration import track_cache_operation

@track_cache_operation("llm")
def get_cached_response(prompt: str):
    if prompt in cache:
        return cache[prompt]  # Cache hit
    else:
        return None  # Cache miss
```

#### Manualmente

```python
from core.utils.performance_integration import (
    manual_track_cache_hit,
    manual_track_cache_miss
)

if prompt in cache:
    manual_track_cache_hit("llm")
    return cache[prompt]
else:
    manual_track_cache_miss("llm")
    response = call_llm(prompt)
    cache[prompt] = response
    return response
```

### 4. Rastrear Erros

```python
from core.utils.performance_integration import track_error

try:
    results = execute_query(query)
except Exception as e:
    track_error(str(e), context={"query": query, "duration_ms": duration})
    raise
```

---

## 📊 Métricas Disponíveis

### Query Metrics

| Métrica | Descrição | Ideal |
|---------|-----------|-------|
| `avg_query_time_ms` | Tempo médio de execução | < 3000ms |
| `min_query_time_ms` | Tempo mínimo de execução | - |
| `max_query_time_ms` | Tempo máximo de execução | < 10000ms |
| `p95_query_time_ms` | 95º percentil (95% das queries são mais rápidas) | < 5000ms |
| `queries_per_minute` | Taxa de processamento | Depende da carga |

### Cache Metrics

| Métrica | Descrição | Ideal |
|---------|-----------|-------|
| `cache_hits` | Número de cache hits | Alto |
| `cache_misses` | Número de cache misses | Baixo |
| `cache_hit_rate` | Porcentagem de hits | > 50% |

### Error Metrics

| Métrica | Descrição | Ideal |
|---------|-----------|-------|
| `errors` | Número de erros | 0 |
| `error_rate` | Taxa de erro (%) | < 5% |

### Startup Metrics

| Métrica | Descrição | Ideal |
|---------|-----------|-------|
| `last_startup_ms` | Último tempo de startup | < 5000ms |
| `avg_startup_ms` | Média de startup | < 6000ms |
| `min_startup_ms` | Mínimo de startup | - |
| `max_startup_ms` | Máximo de startup | < 10000ms |

---

## ⚠️ Alertas de Performance

### 🔴 Alertas Críticos

1. **Tempo médio de query > 5000ms**
   - **Ação**: Investigar queries lentas, otimizar Parquet/SQL, verificar LLM

2. **Taxa de erro > 10%**
   - **Ação**: Verificar logs, validar conexões, checar integridade de dados

3. **> 10 erros na janela de tempo**
   - **Ação**: Investigar causa raiz imediatamente

### 🟡 Alertas de Atenção

1. **Tempo médio de query > 3000ms**
   - **Ação**: Monitorar evolução, considerar otimizações

2. **Cache hit rate < 30%**
   - **Ação**: Aumentar TTL, verificar padrões de uso, otimizar cache

3. **Taxa de erro > 5%**
   - **Ação**: Investigar erros intermitentes

---

## 🔧 Troubleshooting

### Dashboard não aparece

1. Verificar que você está logado como **admin**
2. Verificar logs: `logs/streamlit.log`
3. Verificar se arquivo existe: `core/utils/performance_tracker.py`

### Nenhuma métrica aparece

**Problema**: Sistema não está rastreando queries

**Solução**:
1. Verificar se tracking está integrado no código (veja seção "Integrando Tracking")
2. Executar algumas queries no sistema
3. Clicar em "🔄 Atualizar"

### Métricas incorretas

**Problema**: Valores não fazem sentido

**Solução**:
1. Verificar se há múltiplas instâncias rodando
2. Reiniciar o sistema: `streamlit run streamlit_app.py`
3. Verificar logs para erros

### Erro ao salvar snapshot

**Problema**: Botão "💾 Salvar Snapshot" falha

**Solução**:
1. Verificar permissões de escrita em `data/metrics/`
2. Criar diretório manualmente: `mkdir -p data/metrics`
3. Verificar espaço em disco

---

## 📈 Exemplos Práticos

### Exemplo 1: Monitorar Query Lenta

```python
# No seu código
@track_query_performance("custom_query")
def process_user_request(user_input):
    # Processamento complexo
    time.sleep(2)  # Simula operação lenta
    return result

# No dashboard, você verá:
# - Tempo médio aumentado
# - Alerta se > 3000ms
# - Query aparecerá em "Queries Recentes"
```

### Exemplo 2: Melhorar Cache Hit Rate

```python
# Aumentar TTL do cache
@track_cache_operation("custom_cache")
def get_cached_data(key):
    # Seu código de cache
    pass

# No dashboard:
# - Monitore "Cache Hit Rate"
# - Objetivo: > 50%
# - Se baixo: aumentar TTL, melhorar chaves de cache
```

### Exemplo 3: Identificar Gargalos de Startup

```python
# Rastrear componentes críticos
with track_startup("database"):
    db_connection = connect_to_database()

with track_startup("ml_model"):
    model = load_ml_model()

# No dashboard, veja:
# - Qual componente demora mais
# - Compare com médias anteriores
# - Otimize o mais lento primeiro
```

---

## 🎯 Melhores Práticas

1. **Monitore regularmente**: Acesse dashboard diariamente
2. **Estabeleça baselines**: Anote tempos normais de query
3. **Aja nos alertas**: Não ignore alertas críticos
4. **Exporte snapshots**: Antes/depois de otimizações
5. **Compare janelas**: Use 5min para tempo real, 60min para tendências
6. **Integre tracking**: Adicione em todas queries críticas
7. **Documente mudanças**: Relacione melhorias com versões

---

## 📝 Changelog

### v2.2 (2025-11-03)

- ✅ Dashboard completo de performance
- ✅ Tracking automático via decorators
- ✅ Alertas inteligentes de performance
- ✅ Exportação de snapshots
- ✅ Thread-safe para multi-usuário
- ✅ Métricas lifetime + janelas customizáveis

---

## 🔗 Links Relacionados

- [Sistema de Cache](../core/utils/response_cache.py)
- [Performance Tracker](../core/utils/performance_tracker.py)
- [Integração](../core/utils/performance_integration.py)
- [Otimizações v2.2](./RELEASE_NOTES_v2.2.md)

---

**Desenvolvido com ❤️ usando Context7 best practices**
