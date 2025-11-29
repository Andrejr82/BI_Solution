# 🔍 AUDITORIA COMPLETA DOS AGENTES

**Data:** 2025-11-26  
**Objetivo:** Revisar todos os prompts e referências de dados nos agentes  

---

## 📊 SCHEMA REAL DO PARQUET (admmat.parquet)

### Colunas Principais:
```python
PRODUTO              int64    # Código do produto
NOME                 object   # Nome/descrição
LIQUIDO_38           object   # Preço de venda (38% margem)
ULTIMA_ENTRADA_CUSTO_CD object # Custo
ESTOQUE_UNE          object   # Estoque na unidade
ESTOQUE_CD           object   # Estoque no CD
ESTOQUE_LV           object   # Estoque Linha Verde
VENDA_30DD           float64  # Vendas últimos 30 dias
NOMEFABRICANTE       object   # Fabricante
NOMEGRUPO            object   # Grupo/categoria
NOMESUBGRUPO         object   # Subgrupo
NOMESEGMENTO         object   # Segmento
NOMECATEGORIA        object   # Categoria
UNE                  int64    # Código da unidade
UNE_NOME             object   # Nome da loja
```

### Colunas de Vendas Mensais:
```python
MES_01, MES_02, ..., MES_12  # Vendas mensais
VENDA QTD JAN, FEV, MAR, ... # Vendas por mês (formato alternativo)
```

---

## 🔍 AGENTES IDENTIFICADOS

### 1. **tool_agent.py** ✅ CORRIGIDO
- **Status:** Prompt revisado e corrigido
- **Uso:** Agente principal do ChatBI
- **Prompt:** ChatPromptTemplate com instruções completas

### 2. **supervisor_agent.py** ✅ OK
- **Status:** Não tem prompt próprio
- **Uso:** Roteia queries para tool_agent
- **Ação:** Nenhuma necessária

### 3. **product_agent.py** ⚠️ PRECISA CORREÇÃO
- **Status:** Referências a colunas antigas
- **Uso:** Busca e análise de produtos
- **Problemas encontrados:**
  - Linha 163: Referência a `VENDA_30D` (correto: `VENDA_30DD`)
  - Linha 184: `PREÇO 38%` (correto: `LIQUIDO_38`)
  - Linha 200: `FABRICANTE` (correto: `NOMEFABRICANTE`)
  - Linha 204: `GRUPO` (correto: `NOMEGRUPO`)
  - Linha 244: `CÓDIGO` (correto: `PRODUTO`)
  - Linha 257-262: Múltiplas referências incorretas

### 4. **developer_agent.py** ✅ OK
- **Status:** Agente de desenvolvimento de código
- **Uso:** Não acessa dados do Parquet
- **Ação:** Nenhuma necessária

---

## 🔧 CORREÇÕES NECESSÁRIAS

### product_agent.py

#### Problema 1: Prompt de Extração de Filtros (Linhas 149-216)
```python
# ❌ ERRADO:
"PREÇO 38%"
"FABRICANTE"
"CATEGORIA"
"GRUPO"

# ✅ CORRETO:
"LIQUIDO_38"
"NOMEFABRICANTE"
"NOMECATEGORIA"
"NOMEGRUPO"
```

#### Problema 2: Método get_product_details (Linhas 242-276)
```python
# ❌ ERRADO:
filters = {"CÓDIGO": product_code}
prod[["CÓDIGO", "NOME", "PREÇO 38%", "FABRICANTE", "CATEGORIA", "GRUPO"]]

# ✅ CORRETO:
filters = {"PRODUTO": product_code}
prod[["PRODUTO", "NOME", "LIQUIDO_38", "NOMEFABRICANTE", "NOMECATEGORIA", "NOMEGRUPO"]]
```

#### Problema 3: Método get_sales_history (Linhas 308-373)
```python
# ❌ ERRADO:
product_row = df_admat[df_admat["CÓDIGO"] == product_code]
"VENDA 30D"
"VEND. QTD 30D"

# ✅ CORRETO:
product_row = df_admat[df_admat["PRODUTO"] == product_code]
"VENDA_30DD"
```

---

## ✅ PLANO DE AÇÃO

1. **Corrigir product_agent.py:**
   - [ ] Atualizar prompt de extração de filtros
   - [ ] Corrigir método `get_product_details`
   - [ ] Corrigir método `get_sales_history`
   - [ ] Atualizar todos os exemplos no código

2. **Validar tool_agent.py:**
   - [x] Prompt já corrigido
   - [x] Instruções alinhadas com schema real

3. **Testar integração:**
   - [ ] Testar busca de produtos
   - [ ] Testar consultas no ChatBI
   - [ ] Validar geração de gráficos

---

## 📝 OBSERVAÇÕES

- O `product_agent.py` **não é usado** pelo ChatBI atual
- O ChatBI usa apenas o `tool_agent.py` via `supervisor_agent.py`
- Mesmo assim, é importante corrigir para manter consistência
- O arquivo `CATALOGO_PARA_EDICAO.json` também pode precisar atualização

---

## 🎯 PRIORIDADE

1. **ALTA:** tool_agent.py ✅ CONCLUÍDO
2. **MÉDIA:** product_agent.py ⚠️ PENDENTE
3. **BAIXA:** Catálogo JSON (se existir)
