# Análise Preliminar de Performance - Query "KPIs principais por segmento une mad"

**Data:** 2025-10-21
**Status:** ⚠️ Query com falha (ArrowMemoryError)
**Analista:** Claude Code

---

## 📋 Sumário Executivo

**Problema:** Query "KPIs principais por segmento une mad" falha com erro `ArrowMemoryError: realloc of size 8910592 failed`

**Causa Raiz:** `load_data()` carrega 2.2M linhas na memória SEM aplicar filtros antes

**Impacto:** Timeout/crash em queries que precisam filtrar grandes datasets

---

## 🔍 Análise Detalhada do Fluxo

### 1. Código Gerado pelo LLM

```python
# Código gerado (conforme log de erro 20251021)
df = load_data()  # ❌ CARREGA TUDO (2.2M linhas)

une_mad_df = df[df['UNE'] == 'MAD']  # Filtro aplicado TARDE DEMAIS

kpis_por_segmento_mad = une_mad_df.groupby('NOMESEGMENTO').agg(
    Venda_Total=('VENDA_30DD', 'sum'),
    Estoque_Total=('ESTOQUE_UNE', 'sum'),
    Preco_Medio=('LIQUIDO_38', 'mean')
).reset_index()

result = kpis_por_segmento_mad[['NOMESEGMENTO', 'Venda_Total', 'Estoque_Total', 'Preco_Medio']]
```

### 2. Execução de `load_data()` (code_gen_agent.py:119-188)

**Etapas internas (estimativa de tempo):**

| Etapa | Tempo Estimado | Memória | Operação |
|-------|----------------|---------|----------|
| 1. `dd.read_parquet()` | ~0.5s | Lazy (mínima) | Cria task graph Dask |
| 2. Conversão de tipos (`dd.to_numeric`) | ~0.3s | Lazy (mínima) | Adiciona tarefas ao graph |
| 3. **`.compute()`** | **5-15s** | **❌ 500MB-2GB** | **MATERIALIZA 2.2M LINHAS** |
| 4. Retorno para pandas | ~0.1s | Cópia em memória | DataFrame pandas |
| **TOTAL** | **6-16s** | **❌ Alto** | **Bottleneck crítico** |

---

## 🚨 Bottlenecks Identificados

### Bottleneck #1: Carregamento Completo do Dataset ⚠️⚠️⚠️

**Localização:** `code_gen_agent.py:184-186`

```python
self.logger.info(f"⚡ load_data(): Convertendo Dask → pandas ({ddf.npartitions} partições)")
start_compute = time.time()
df_pandas = ddf.compute()  # ❌ PROBLEMA AQUI!
```

**Problema:**
- Carrega **todas as 2.2M linhas** do dataset na memória
- Ignora completamente o filtro `UNE == 'MAD'` (que reduziria para ~100k linhas)
- PyArrow tenta alocar mais memória e falha

**Dados:**
- Dataset completo: ~1.1M linhas (admmat.parquet) + outros arquivos = **2.2M linhas total**
- Tamanho estimado: **500MB - 2GB** em memória (pandas)
- UNE 'MAD' filtrado: ~100k linhas (~50MB)

**Impacto:**
- **Tempo:** +5-15s desnecessários
- **Memória:** +500MB-2GB desnecessários
- **Risco:** ArrowMemoryError / MemoryError / Timeout

---

### Bottleneck #2: Filtro Aplicado Tarde Demais ⚠️

**Localização:** Código gerado pelo LLM

```python
df = load_data()  # Já carregou tudo
une_mad_df = df[df['UNE'] == 'MAD']  # Filtro em memória (tarde)
```

**Problema:**
- Filtro aplicado DEPOIS de `.compute()`
- Pandas precisa varrer 2.2M linhas em memória
- Desperdiça ~95% dos dados carregados

**Solução Ideal (Predicate Pushdown):**
```python
# Filtrar ANTES de compute (no Dask)
ddf = dd.read_parquet(file)
ddf_filtered = ddf[ddf['UNE'] == 'MAD']  # Lazy filter
df = ddf_filtered.compute()  # Carrega apenas ~100k linhas
```

---

### Bottleneck #3: Ignorar PolarsDaskAdapter Híbrido ⚠️

**Problema:**
- `load_data()` reimplementa leitura Dask do zero
- **NÃO usa** `PolarsDaskAdapter` (que já tem predicate pushdown!)
- Perde todos os benefícios da arquitetura híbrida

**Código Atual (code_gen_agent.py:144):**
```python
ddf = dd.read_parquet(parquet_pattern, engine='pyarrow')  # Ignora adapter!
```

**Deveria ser:**
```python
# Usar adapter com filtros
result_list = self.data_adapter.execute_query({'UNE': 'MAD'})
df = pd.DataFrame(result_list)  # Apenas 100k linhas
```

---

## 📊 Breakdown de Tempo Estimado (Sem Profiling Real)

### Cenário ATUAL (Código Problemático):

| Fase | Tempo | Memória | Status |
|------|-------|---------|--------|
| 1. LLM gera código | ~2-5s | Mínima | ✅ OK |
| 2. `load_data()` - read_parquet (lazy) | ~0.5s | Mínima | ✅ OK |
| 3. `load_data()` - conversão tipos (lazy) | ~0.3s | Mínima | ✅ OK |
| 4. **`load_data()` - `.compute()`** | **5-15s** | **500MB-2GB** | ❌ BOTTLENECK |
| 5. Filtro `UNE == 'MAD'` em pandas | ~0.5s | Já em memória | ⚠️ Tarde |
| 6. GroupBy + agregações | ~0.2s | Mínima | ✅ OK |
| **TOTAL** | **8-21s** | **Alto** | ❌ Falha (OOM) |

---

### Cenário IDEAL (Com Filtros no Adapter):

| Fase | Tempo | Memória | Status |
|------|-------|---------|--------|
| 1. LLM gera código | ~2-5s | Mínima | ✅ OK |
| 2. `adapter.execute_query({'UNE': 'MAD'})` - Polars scan | ~0.1s | Lazy | ✅ OK |
| 3. Polars filter (lazy) | ~0.01s | Lazy | ✅ OK |
| 4. Polars collect (apenas MAD) | ~0.2-0.5s | ~50MB | ✅ OK |
| 5. Conversão para pandas | ~0.01s | Já pequeno | ✅ OK |
| 6. GroupBy + agregações | ~0.02s | Mínima | ✅ OK |
| **TOTAL** | **2.5-5.5s** | **Baixo** | ✅ Sucesso |

**Ganho:** 3-4x mais rápido + 90% menos memória!

---

## 🎯 Comparação: Atual vs Ideal

| Métrica | Atual (Problema) | Ideal (Solução) | Melhoria |
|---------|------------------|-----------------|----------|
| **Tempo total** | 8-21s (ou falha) | 2.5-5.5s | **3-4x mais rápido** |
| **Memória pico** | 500MB-2GB | ~50MB | **90% redução** |
| **Linhas carregadas** | 2.2M linhas | ~100k linhas | **95% redução** |
| **Taxa de sucesso** | ❌ 0% (OOM) | ✅ 100% | **Resolve bug** |
| **Usa arquitetura híbrida** | ❌ Não | ✅ Sim | **Alinhamento** |

---

## 🔧 Planos de Correção Recomendados

### **Plano A: Filtros Opcionais em `load_data()` (RECOMENDADO)** ⭐

**Tempo de implementação:** 30 minutos
**Complexidade:** Baixa
**Risco:** Baixo

**Modificação:**
```python
# code_gen_agent.py - load_data()
def load_data(filters: Dict[str, Any] = None):
    if self.data_adapter and filters:
        # Usar adapter com filtros (Polars/Dask)
        result_list = self.data_adapter.execute_query(filters)
        return pd.DataFrame(result_list)
    else:
        # Sem filtros - carregar amostra (10k linhas)
        self.logger.warning("load_data() sem filtros - limitando a 10k linhas")
        # ... implementação
```

**Atualizar prompt LLM:**
```python
"""
✅ CORRETO - Passar filtros para load_data():
df = load_data(filters={'UNE': 'MAD'})

❌ ERRADO - Carregar tudo:
df = load_data()  # Timeout!
"""
```

**Vantagens:**
- ✅ Usa PolarsDaskAdapter (arquitetura híbrida)
- ✅ Correção mínima (~50 linhas)
- ✅ Não quebra código existente
- ✅ LLM aprende a usar filtros

**Desvantagens:**
- ⚠️ Depende de LLM gerar código com filtros

---

### **Plano B: Polars LazyFrame (Ideal a Longo Prazo)**

**Tempo:** 1-2 horas
**Complexidade:** Média
**Risco:** Médio

**Modificação:**
```python
def load_data():
    import polars as pl
    lf = pl.scan_parquet(file_path)  # LazyFrame
    # ... conversões de tipos (lazy)
    return lf  # NÃO computado!
```

**Código gerado precisa ser:**
```python
lf = load_data()  # Polars LazyFrame
lf_mad = lf.filter(pl.col('UNE') == 'MAD')  # Lazy
df = lf_mad.collect()  # Agora computa (apenas MAD)
```

**Vantagens:**
- ✅ Performance máxima (Polars puro)
- ✅ Impossível carregar tudo (lazy obriga filtros)

**Desvantagens:**
- ❌ LLM precisa aprender sintaxe Polars
- ❌ Taxa de erro inicial pode ser alta

---

### **Plano C: Auto-Filtro Inteligente**

**Tempo:** 2-3 horas
**Complexidade:** Alta
**Risco:** Médio-Alto

**Ideia:** Extrair filtros da query do usuário automaticamente (regex)

**Vantagens:**
- ✅ Transparente para LLM

**Desvantagens:**
- ⚠️ Regex pode falhar
- ⚠️ Mais complexo

---

## 📈 Impacto Esperado do Plano A

### Queries Afetadas:

| Tipo de Query | Antes | Depois | Ganho |
|---------------|-------|--------|-------|
| **KPIs por UNE específica** | Falha (OOM) | 2-3s | ✅ Resolve |
| **Ranking segmento específico** | 8-15s | 2-4s | **2-4x** |
| **Análise produto específico** | 5-10s | 0.5-1s | **10x** |
| **Query sem filtros** | 8-15s | 10k linhas (limitado) | ✅ Seguro |

### Estimativa de Melhoria:

- **70-80% das queries** usam filtros (UNE, segmento, produto)
- Ganho médio: **3-5x mais rápido**
- Redução de RAM: **80-90%**
- **100% das queries OOM resolvidas**

---

## ✅ Conclusões

### Bottleneck Principal:
**`load_data()` em `code_gen_agent.py:184` carrega 2.2M linhas sem filtros**

### Solução Recomendada:
**Plano A** - Adicionar suporte a filtros opcionais em `load_data()` + atualizar prompt

### Próximos Passos:
1. ✅ Aguardar profiling real terminar (validar estimativas)
2. Implementar Plano A (~30 min)
3. Testar com query problemática
4. Validar ganho de performance

---

**Documento gerado em:** 2025-10-21 19:05
**Status:** Aguardando profiling real para validação
**Próxima atualização:** Após execução do profiling
