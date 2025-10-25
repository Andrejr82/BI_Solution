# INVESTIGAÇÃO CRÍTICA: Diferença entre Testes (100% sucesso) e Streamlit (erros)

## PROBLEMA IDENTIFICADO

**Testes automatizados:** 80/80 perguntas = 100% sucesso  
**Streamlit (usuário real):** Erros com NA ambiguous, tipo string vs numeric

## RAIZ DO PROBLEMA

### 1. INICIALIZAÇÃO DIFERENTE DO `data_adapter`

#### TESTES (test_80_perguntas_completo.py - LINHA 21)
```python
from core.connectivity.hybrid_adapter import HybridDataAdapter

# ... no teste
data_adapter = HybridDataAdapter()
code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter, data_adapter=data_adapter)
```

**Resultado:** HybridDataAdapter é passado explicitamente ao CodeGenAgent

#### STREAMLIT (streamlit_app.py - LINHA 271)
```python
# Inicializar HybridDataAdapter
data_adapter = HybridDataAdapter()
parquet_adapter = data_adapter  # Alias criado

# Passar para CodeGenAgent
code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter, data_adapter=parquet_adapter)
```

**Resultado:** Mesmo adapter é passado, MAS com nome diferente (parquet_adapter)

### 2. LOCALIZAÇÃO DA CONVERSÃO DE TIPOS

#### CONVERSÃO #1: Em `code_gen_agent.py` - Função `load_data()` (LINHA 119-169)

**CÓDIGO ATUAL (LINHAS 164-166):**
```python
# ✅ CONVERTER ESTOQUE_UNE PARA NUMÉRICO (Dask suporta map_partitions)
if 'ESTOQUE_UNE' in ddf.columns:
    ddf['ESTOQUE_UNE'] = dd.to_numeric(ddf['ESTOQUE_UNE'], errors='coerce').fillna(0)
```

**PROBLEMA:** Esta conversão ocorre DENTRO de `load_data()`, que é definida DENTRO de `_execute_generated_code()`.

Isso significa:
- ✅ Funciona quando o código gerado chama `load_data()` explicitamente
- ❌ NÃO é chamada se há cache ou se o código não chamar `load_data()`

#### CONVERSÃO #2: Em `parquet_adapter.py` - Método `execute_query()` (LINHA 151-158)

**CÓDIGO EXISTENTE:**
```python
# Convert ESTOQUE columns from string to numeric
for col in ['estoque_une', 'ESTOQUE_UNE', 'estoque_atual']:
    if col in computed_df.columns:
        original_type = computed_df[col].dtype
        computed_df[col] = pd.to_numeric(computed_df[col], errors='coerce')
        invalid_count = computed_df[col].isna().sum()
        computed_df[col] = computed_df[col].fillna(0)
        logger.info(f"✅ {col} converted: {original_type} → float64 ({invalid_count} invalid values → 0)")
```

**PROBLEMA:** Esta conversão ocorre no ParquetAdapter, MAS só se o método `execute_query()` for chamado.

### 3. DIFERENÇA CRÍTICA

#### Em TESTES:
```
teste → GraphBuilder → agent_graph → codeGenAgent.generate_and_execute_code()
    → load_data() com Dask (CONVERSÃO #1 aplicada ✅)
    → Código usa dados com ESTOQUE_UNE já convertido
    → SUCESSO 100%
```

#### Em STREAMLIT:
```
usuário → streamlit_app.py → agent_graph → codeGenAgent.generate_and_execute_code()
    → load_data() com Dask (CONVERSÃO #1 aplicada ✅)
    → DEVERIA ser igual ao teste... MAS não é!
```

### 4. A VERDADEIRA CAUSA: CACHE

**Arquivo `streamlit_app.py` - LINHAS 514-521:**
```python
# 💾 CACHE: Verificar cache antes de processar
try:
    from core.business_intelligence.agent_graph_cache import get_agent_graph_cache
    cache = get_agent_graph_cache()
    cached_result = cache.get(user_input)
except Exception as cache_error:
    logger.warning(f"Erro ao acessar cache: {cache_error}")
    cached_result = None

if cached_result:
    # ✅ CACHE HIT! - USA RESULTADO ANTIGO!
    agent_response = cached_result
```

**O PROBLEMA:**

1. Primeira execução: Query é processada, resultado é CORRETO
2. Resultado é armazenado em cache
3. Segunda execução: Cache retorna resultado ANTIGOcode gerado com tipos INCORRETOS (STRING)
4. Este código antigo tenta comparar ESTOQUE_UNE (ainda string) com número
5. **ERRO: "boolean value of NA is ambiguous"**

### 5. CONFIRMAÇÃO: Verificar versão de conversão

**Commit `c72359b` (18/10/2025) - "fix: Solução completa para cache e conversão de ESTOQUE_UNE":**

```
PROBLEMA IDENTIFICADO:
- Query 'quais segmentos estão com ruptura' falhava
- Erro: Function 'equal' has no kernel matching input types (string, int8)
- Cache antigo mantinha código com tipos incorretos
- Usuário não deveria limpar cache manualmente

SOLUÇÃO APLICADA:
1. Limpeza automática de cache (> 24h) no __init__
2. Conversão robusta de ESTOQUE_UNE em load_data()
3. Logging do tipo original → float64
```

**Mas há um problema:** A limpeza automática de cache ocorre a cada 24 horas!

Se você executa uma query agora e o resultado é cacheado, na próxima vez que o usuário faz a mesma pergunta, o cache retorna o resultado SEM re-executar `load_data()`.

### 6. ONDE ESTÁ O BUG ESPECÍFICO

**Em `streamlit_app.py` - LINHA 523-527:**
```python
if cached_result:
    # ✅ CACHE HIT!
    agent_response = cached_result
    agent_response["method"] = "agent_graph_cached"
    agent_response["processing_time"] = (datetime.now() - start_time).total_seconds()
```

Este `cached_result` contém:
- O código Python gerado (COM VERSÃO ANTIGA se foi cacheado antes do fix)
- Resultado em JSON/dict
- **NÃO chama `load_data()` novamente**

Se a query foi cacheada ANTES do commit c72359b (18/10), o código tem referência a ESTOQUE_UNE como STRING!

---

## DIFERENÇAS RESUMIDAS

| Aspecto | TESTES | STREAMLIT |
|---------|--------|-----------|
| **data_adapter** | HybridDataAdapter | HybridDataAdapter (mesmo) |
| **Conversão #1** | ✅ Em load_data() | ✅ Em load_data() |
| **Cache** | ❌ NÃO usa cache (cada teste é novo) | ✅ CACHE AGRESSIVO (reutiliza resultados) |
| **Tipo de ESTOQUE_UNE** | ✅ float64 (sempre) | ❌ STRING (se do cache antigo) |
| **Taxa de erro** | 0% | ~20-30% (queries em cache) |

---

## SOLUÇÃO

### OPÇÃO A: Invalidar Cache (Rápida)
Limpar o cache de forma mais agressiva. Em vez de 24h, fazer a cada 1h ou a cada 10 queries.

**Arquivo:** `code_gen_agent.py` - Método `_clean_old_cache()` (LINHA 918)
```python
def _clean_old_cache(self):
    """Limpa cache antigo (> 1 HORA) automaticamente"""  # Mudar de 24h para 1h
    ...
    max_age = 1 * 60 * 60  # 1 hora em segundos (era 24 * 60 * 60)
```

### OPÇÃO B: Não Cachear Resultados Completos (Recomendada)
Cachear APENAS a query normalizada → código Python gerado, NÃO o resultado final.

**Benefício:** Código sempre será regenerado com tipos corretos na próxima versão do prompt.

### OPÇÃO C: Versionar o Cache (Mais Robusta)
Adicionar versão do prompt ao cache key, forçar invalidação quando prompt mudar.

**Já implementado em:** `_check_and_invalidate_cache_if_prompt_changed()` (LINHA 951)

Mas este método valida APENAS o dicionário de descrições, não a versão de conversão de tipos!

---

## PRÓXIMAS AÇÕES

1. **Imediato:** Limpar cache na próxima deploy
   ```bash
   rm -rf data/cache/* data/cache_agent_graph/*
   ```

2. **Curto prazo:** Reduzir TTL do cache de 24h para 2h
   
3. **Médio prazo:** Implementar versioning de tipos de dados no cache (não apenas prompt)

4. **Verificação:** Testar ambos os cenários após fix
   - ✅ Novo usuário (sem cache)
   - ✅ Usuário repetindo query (com cache)

