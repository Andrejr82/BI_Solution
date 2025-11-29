# ⚡ OTIMIZAÇÕES DO AGENTE BI - Sprint 1

**Data:** 2025-11-27
**Objetivo:** Reduzir tempo de resposta de 30s+ para < 5s

---

## 🎯 PROBLEMAS IDENTIFICADOS

1. **ProductAgent recursivo** - Chamava LLM para extrair filtros (LENTÍSSIMO)
2. **Sem cache de dados** - Cada query carregava Parquet do zero
3. **Sem validação rápida** - Queries simples passavam pelo agente completo
4. **Timeout muito alto** - 30s permitia lentidão sem feedback
5. **Muitas iterações** - AgentExecutor com 15 iterações (padrão)
6. **Modelo lento** - Configuração default do Gemini

---

## ✅ OTIMIZAÇÕES IMPLEMENTADAS

### 1. **Ferramentas Ultra-Rápidas** (`backend/app/core/tools/fast_product_tools.py`)

**Criado:** 6 ferramentas otimizadas com cache global

```python
# Cache global do DataFrame (carrega 1x na memória)
_CACHED_DF = None  # Carrega no primeiro acesso

# Ferramentas disponíveis:
- listar_colunas() - Lista colunas (com @lru_cache)
- buscar_preco_produto(codigo) - Preço instantâneo
- buscar_estoque_produto(codigo) - Estoque instantâneo
- buscar_info_produto(codigo) - Todas as informações
- buscar_produtos_por_categoria(categoria) - Filtro por categoria
- top_produtos_mais_vendidos(limite) - Rankings
```

**Ganho esperado:** < 500ms para queries simples (preço, estoque)

---

### 2. **Agente Otimizado** (`backend/app/core/agents/tool_agent.py`)

**Mudanças:**

```python
# ANTES
self.tools = unified_tools + date_time_tools + chart_tools

# DEPOIS (fast_tools primeiro!)
self.tools = fast_product_tools + date_time_tools + chart_tools

# ANTES (AgentExecutor padrão)
AgentExecutor(agent=agent, tools=self.tools, verbose=True)

# DEPOIS
AgentExecutor(
    agent=agent,
    tools=self.tools,
    max_iterations=3,  # Reduzido de 15
    max_execution_time=5.0,  # Timeout de 5s
    verbose=True
)
```

**Prompt atualizado:**
- Instruções para usar `buscar_preco_produto()` DIRETAMENTE
- Sem perguntar confirmação antes de executar ferramentas
- Priorizar ferramentas fast_tools

**Ganho esperado:** 3-5s para queries que precisam do agente

---

### 3. **Gemini Otimizado** (`backend/app/core/llm_gemini_adapter.py`)

**ANTES:**
```python
self.model_name = "models/gemini-2.0-flash-exp"
self.max_retries = 3
self.retry_delay = 2
# Sem generation_config
```

**DEPOIS:**
```python
self.model_name = "gemini-2.5-flash"  # Mais rápido e preciso
self.max_retries = 1  # Sem retries desnecessários
self.retry_delay = 0.5  # 500ms entre tentativas

self.generation_config = {
    "temperature": 0.3,  # Mais determinístico
    "top_p": 0.8,  # Menos variação
    "top_k": 20,  # Menos candidatos
    "max_output_tokens": 4096,  # ✅ Suficiente para gráficos JSON
}

# Timeout por request
response = chat_session.send_message(
    message,
    request_options={"timeout": 5.0}
)
```

**Ganho esperado:** 1-2s de economia por chamada LLM

---

### 4. **Chat Endpoint** (`backend/app/api/v1/endpoints/chat.py`)

**ANTES:**
```python
result = await asyncio.wait_for(
    processor.process_query(query),
    timeout=30.0  # Muito permissivo
)
```

**DEPOIS:**
```python
result = await asyncio.wait_for(
    processor.process_query(query),
    timeout=7.0  # Falha rápida se lento
)
```

**Ganho:** Feedback rápido ao usuário se algo der errado

---

## 📊 COMPARAÇÃO DE PERFORMANCE

### Query: "qual é o preço do produto 369947?"

| Versão | Tempo | Status |
|--------|-------|--------|
| **ANTES** | 30s+ | ❌ TIMEOUT |
| **DEPOIS (esperado)** | < 3s | ✅ EXCELENTE |

**Fluxo otimizado:**
1. User: "qual é o preço do produto 369947?"
2. Supervisor → ToolAgent
3. ToolAgent vê `fast_product_tools` primeiro
4. Chama `buscar_preco_produto("369947")` (cache hit, < 500ms)
5. Retorna: "O preço do produto 369947 é **R$ XX,XX**"
6. **Total: < 3s**

---

## 🔧 CONFIGURAÇÕES IMPORTANTES

### Gemini API
```bash
# .env
GEMINI_API_KEY=your-key-here
GEMINI_MODEL_NAME=gemini-2.5-flash  # Opcional (padrão já configurado)
```

### Timeouts (stack completo)
```
Gemini request: 5s
AgentExecutor: 5s
QueryProcessor: (sem timeout próprio)
Chat endpoint: 7s
```

**Total máximo:** 7s antes de retornar erro ao usuário

---

## 🧪 COMO TESTAR

### 1. Reinstalar dependências (se necessário)
```bash
cd backend
pip install -r requirements.txt
```

### 2. Testar com script
```bash
cd backend
python test_agent_speed.py
```

### 3. Testar no ChatBI
```
Query 1: "qual é o preço do produto 369947?"
Esperado: < 3s

Query 2: "qual o estoque do produto 59294?"
Esperado: < 3s

Query 3: "me mostre informações completas do produto 369947"
Esperado: < 5s
```

---

## ⚠️ LIMITAÇÕES CONHECIDAS

1. **Primeira query lenta** - Cache ainda não carregado (1-2s extra)
2. **Queries complexas** - Ainda podem demorar 5-7s se precisarem de múltiplas ferramentas
3. **Gráficos** - Geração de gráficos ainda demora 3-5s (Plotly + Gemini)

---

## 🚀 PRÓXIMOS PASSOS (SE AINDA LENTO)

1. **Pre-warm cache** - Carregar dados na inicialização do servidor
2. **Query classifier** - Detectar queries simples ANTES do agente
3. **Response cache** - Cache de respostas frequentes
4. **Async tools** - Paralelizar chamadas de ferramentas
5. **Gemini Pro** - Testar modelo ainda mais rápido (se disponível)

---

## 📝 ARQUIVOS MODIFICADOS

```
backend/app/core/tools/fast_product_tools.py  [NOVO]
backend/app/core/agents/tool_agent.py         [MODIFICADO]
backend/app/core/llm_gemini_adapter.py        [MODIFICADO]
backend/app/api/v1/endpoints/chat.py          [MODIFICADO]
backend/test_agent_speed.py                   [NOVO - TESTE]
```

---

**Status:** ✅ Código pronto, aguardando teste no ambiente real
