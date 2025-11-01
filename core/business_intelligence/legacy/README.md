# 📦 Legacy Code - Módulos Descontinuados

## 📋 Conteúdo

Esta pasta contém módulos descontinuados do projeto Agent_Solution_BI que foram substituídos por soluções mais modernas e eficientes.

## 🗂️ Arquivos Movidos

### 1. **DirectQueryEngine** (Descontinuado em 31/10/2025)
- `direct_query_engine.py` - Motor de queries diretas (versão final)
- `direct_query_engine_backup.py` - Backup anterior
- `direct_query_engine_before_phase2.py` - Versão antes da Fase 2

**Razão da Descontinuação:**
- ❌ **Limitações hardcoded**: Aplicava `.head(20)` arbitrariamente mesmo quando usuário não pedia
- ❌ **Colunas pré-estabelecidas**: Retornava apenas `nome_produto` em vez de todas as colunas relevantes
- ❌ **Comportamento inconsistente**: Conflitava com as regras corretas do `CodeGenAgent`
- ❌ **Complexidade desnecessária**: Padrões regex complexos que falhavam frequentemente

**Substituído por:**
- ✅ `CodeGenAgent` - Gera código Python dinamicamente e executa consultas completas
- ✅ `GraphBuilder` - Orquestra fluxo de agentes inteligentes (100% LLM)

### 2. **HybridQueryEngine** (Descontinuado em 31/10/2025)
- `hybrid_query_engine.py` - Motor híbrido (cache + DirectQueryEngine + LLM fallback)

**Razão da Descontinuação:**
- ❌ Dependia do `DirectQueryEngine` (descontinuado)
- ❌ Complexidade de manutenção sem benefícios reais
- ❌ Não era usado em produção (`streamlit_app.py` já estava 100% IA)

**Substituído por:**
- ✅ Cache nativo do `GraphBuilder` em `core/graph/graph_builder.py`
- ✅ Sistema de self-healing do `CodeGenAgent`

### 3. **SmartCache** (Descontinuado em 31/10/2025)
- `smart_cache.py` - Cache inteligente para queries diretas

**Razão da Descontinuação:**
- ❌ Dependia do `DirectQueryEngine` para warm-up
- ❌ Cache específico para padrões regex (não aplicável a código dinâmico)

**Substituído por:**
- ✅ Cache em memória e disco do `GraphBuilder`
- ✅ RAG (Retrieval-Augmented Generation) com vetorização de queries bem-sucedidas

---

## 🚀 Arquitetura Atual (2025)

### Fluxo de Processamento de Queries

```
Usuário → streamlit_app.py → GraphBuilder → Agent Graph
                                    ↓
                            ┌───────┴────────┐
                            │                │
                    classify_intent    generate_code
                            │                │
                            ↓                ↓
                    BIAgentNodes     CodeGenAgent
                            │                │
                            └────────┬───────┘
                                     ↓
                              execute_query
                                     ↓
                            ParquetAdapter / PolarsDaskAdapter
```

### Componentes Ativos

1. **`core/graph/graph_builder.py`**
   - Orquestrador principal
   - Cache inteligente de resultados
   - Roteamento de agentes

2. **`core/agents/code_gen_agent.py`**
   - Geração dinâmica de código Python
   - Validação e self-healing
   - RAG com queries bem-sucedidas
   - **NÃO aplica limitações arbitrárias**

3. **`core/agents/bi_agent_nodes.py`**
   - Nós (estados) do grafo de agentes
   - Classificação de intenções (Few-Shot Learning)
   - Formatação de respostas

4. **`core/connectivity/parquet_adapter.py`**
   - Acesso aos dados Parquet
   - Otimização com Polars/Dask

---

## 📊 Problemas Corrigidos

### Problema 1: Limitação de 20 Registros
**Antes (DirectQueryEngine):**
```python
# direct_query_engine.py:1580
vendas_por_une_top = vendas_por_une.head(20)  # ❌ HARDCODED!
```

**Depois (CodeGenAgent):**
```python
# code_gen_agent.py:542-564
# Regras inteligentes:
# - "top 10" → .head(10)
# - "ranking de TODAS" → SEM .head()
# - "ranking" genérico → .head(10) como padrão
```

### Problema 2: Colunas Pré-Estabelecidas
**Antes (DirectQueryEngine):**
```python
# direct_query_engine.py:840
"produtos_exemplo": top_sem_vendas[['nome_produto']].to_dict('records')
# ❌ Apenas nome_produto!
```

**Depois (CodeGenAgent):**
```python
# Código gerado dinamicamente pelo LLM
result = sem_vendas_bar[[
    'codigo',
    'nome_produto',
    'nomesegmento',
    'estoque_atual',
    'venda_30_d'
]]
# ✅ Todas as colunas relevantes!
```

---

## 🔧 Como Recuperar Funcionalidade (se necessário)

Se algum teste antigo falhar, você pode:

1. **Atualizar testes** para usar `GraphBuilder` ao invés de `DirectQueryEngine`
2. **Consultar este código legacy** para entender a lógica de negócio original
3. **NÃO reativar** esses módulos - migre a funcionalidade para `CodeGenAgent`

---

## 📝 Histórico de Mudanças

| Data | Ação | Responsável |
|------|------|-------------|
| 31/10/2025 | Movido para legacy após análise de problemas de limitação | Claude Code |
| 12/10/2025 | DirectQueryEngine desabilitado no streamlit_app.py | Equipe de desenvolvimento |
| -- | Última versão funcional do DirectQueryEngine | -- |

---

## ⚠️ Avisos

- **NÃO USAR EM PRODUÇÃO** - Esses arquivos estão aqui apenas para referência histórica
- **NÃO IMPORTAR** - Importações desses módulos causarão erros
- **CONSULTAR APENAS** - Use como referência para entender regras de negócio antigas

---

## 📚 Documentação Relacionada

- [Plano de Correção de Erros LLM](../../../docs/planning/PLANO_CORRECAO_ERROS_LLM_2025-10-29.md)
- [Relatório Fase 1.1](../../../docs/reports/FASE_1_1_RELATORIO_COMPLETO.md)
- [Gemini Integration Guide](../../../docs/guides/GEMINI.md)

---

**Última atualização:** 31/10/2025
**Status:** Arquivado e descontinuado
