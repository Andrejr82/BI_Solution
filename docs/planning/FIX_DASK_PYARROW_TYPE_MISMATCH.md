# ✅ Fix Dask/PyArrow Type Mismatch Error

**Data:** 2025-10-18
**Status:** RESOLVIDO E TESTADO

---

## 🎯 Problema

**Erro:** `Function 'equal' has no kernel matching input types (string, int8)`

**Query que causava erro:** "quais segmentos estão com ruptura?"

**Causa raiz:**
- Coluna `estoque_atual` armazenada como STRING no Parquet
- LLM gerava filtro `estoque_atual <= 0` (comparação numérica)
- Dask/PyArrow tentava aplicar filtro ANTES de carregar dados
- PyArrow não consegue comparar string com int → ERRO

---

## 🔧 Solução Implementada

### Estratégia em 3 Passos

1. **Separar filtros**: STRING (seguros para PyArrow) vs NUMÉRICOS (aplicar depois)
2. **Carregar dados** com apenas filtros string
3. **Converter tipos** e aplicar filtros numéricos em pandas

### Código Implementado

**Arquivo:** `core/connectivity/parquet_adapter.py`

**Mudança 1: Detectar colunas problemáticas (linha 70)**
```python
# Columns that need type conversion BEFORE filtering
NUMERIC_COLUMNS_IN_STRING_FORMAT = ['estoque_une', 'ESTOQUE_UNE', 'estoque_atual']
```

**Mudança 2: Separar filtros (linhas 90-97)**
```python
# Check if this is a numeric comparison on a string-typed column
if column in NUMERIC_COLUMNS_IN_STRING_FORMAT and op in ['>=', '<=', '>', '<']:
    # Defer to pandas (after type conversion)
    try:
        numeric_value = float(value_str) if '.' in value_str else int(value_str)
        pandas_filters.append((column, op, numeric_value))
        logger.info(f"Deferred numeric filter to pandas: {column} {op} {numeric_value}")
        continue
```

**Mudança 3: Aplicar apenas filtros seguros ao PyArrow (linhas 122-131)**
```python
# Read Parquet with only string filters (safe for PyArrow)
if pyarrow_filters:
    logger.info(f"Applying PyArrow filters: {pyarrow_filters}")
    ddf = dd.read_parquet(
        self.file_path,
        engine='pyarrow',
        filters=pyarrow_filters
    )
else:
    logger.info("No PyArrow filters. Reading full dataset.")
    ddf = dd.read_parquet(self.file_path, engine='pyarrow')
```

**Mudança 4: Converter tipos após carregamento (linhas 140-146)**
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

**Mudança 5: Aplicar filtros numéricos em pandas (linhas 163-177)**
```python
# NOW apply numeric filters in pandas (after type conversion)
if pandas_filters:
    logger.info(f"Applying pandas filters after type conversion: {pandas_filters}")
    for column, op, value in pandas_filters:
        if op == '>=':
            computed_df = computed_df[computed_df[column] >= value]
        elif op == '<=':
            computed_df = computed_df[computed_df[column] <= value]
        elif op == '>':
            computed_df = computed_df[computed_df[column] > value]
        elif op == '<':
            computed_df = computed_df[computed_df[column] < value]
        elif op == '=':
            computed_df = computed_df[computed_df[column] == value]
        elif op == '!=':
            computed_df = computed_df[computed_df[column] != value]
```

---

## ✅ Teste de Validação

**Query:** `estoque_atual <= 0`

**Resultado:**
```
[OK] Query executada com sucesso!
[OK] Registros retornados: 352,041

Top 5 segmentos com ruptura:
  ARMARINHO E CONFECÇÃO: 74,195
  SAZONAIS: 65,938
  TECIDOS: 47,036
  PAPELARIA: 44,492
  ARTES: 38,981
```

**Status:** ✅ **FUNCIONANDO 100%**

---

## 📊 Comparação: Antes vs Depois

### Antes (ERRO)
```
Dask lê Parquet → PyArrow aplica filtro estoque_atual <= 0
                → ERRO: can't compare string with int8
                → Query falha
```

### Depois (SUCESSO)
```
Dask lê Parquet → PyArrow aplica apenas filtros string
                → Pandas converte estoque_atual para float64
                → Pandas aplica filtro <= 0
                → Query retorna 352,041 registros
```

---

## 🔑 Pontos-Chave

1. **Problema de timing**: Conversão de tipo acontecia tarde demais
2. **Solução**: Mover filtros numéricos para DEPOIS da conversão
3. **Performance**: Mantém otimização PyArrow para filtros string
4. **Compatibilidade**: Funciona com colunas lowercase e UPPERCASE
5. **Automático**: Usuário não precisa fazer nada

---

## 🚀 Próximos Passos

- ✅ Solução testada e validada
- ✅ Cache limpo automaticamente (> 24h)
- ⏸️ Monitorar performance em produção
- ⏸️ Considerar converter Parquet source para tipos numéricos corretos

---

**Versão:** 1.0
**Autor:** Claude Code
**Data:** 2025-10-18
**Status:** ✅ PROBLEMA RESOLVIDO
