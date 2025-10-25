# 🎯 PLANO FINAL - FIX RESPOSTAS LLM NO STREAMLIT APP

**Data:** 13/10/2025
**Problema:** LLM responde corretamente no Playground mas resposta não aparece no Streamlit App principal
**Status:** 🔴 CRÍTICO - Requer ação imediata

---

## 📊 DIAGNÓSTICO COMPLETO

### ✅ O QUE FUNCIONA (Playground)

**Playground (pages/10_🤖_Gemini_Playground.py):**
```python
# Linha 186-202: FLUXO SIMPLES
response = gemini.get_completion(
    messages=messages,
    temperature=temperature,
    max_tokens=max_tokens,
    json_mode=json_mode,
    stream=False
)

if "error" in response:
    response_content = f"❌ Erro: {response['error']}"
else:
    response_content = response.get("content", "")  # ✅ SIMPLES E DIRETO
    if not response_content:
        response_content = "❌ Resposta vazia recebida do modelo."

# Adiciona ao chat e exibe
st.session_state.chat_history.append({
    "role": "assistant",
    "content": response_content  # ✅ TEXTO PURO
})
st.rerun()  # ✅ RENDERIZA IMEDIATAMENTE
```

**Por que funciona:**
1. ✅ Resposta LLM é extraída diretamente: `response.get("content")`
2. ✅ Formato simples: STRING de texto puro
3. ✅ Renderização direta: `st.markdown(message["content"])`
4. ✅ Zero transformações entre LLM → UI

---

### ❌ O QUE NÃO FUNCIONA (Streamlit App)

**Streamlit App (streamlit_app.py + agent_graph):**
```
User Query
    ↓
agent_graph.invoke() [LangGraph]
    ↓
classify_intent (OK)
    ↓
generate_parquet_query (OK - gera filtros)
    ↓
execute_query (OK - retorna dados)
    ↓
generate_plotly_spec [CodeGenAgent]
    ├─ Gera código Python (OK)
    ├─ Executa código (OK)
    └─ Retorna resultado (OK)
    ↓
format_final_response ⚠️ PROBLEMA AQUI
    ├─ Estrutura resposta como:
    │   {"type": "data", "content": [...]}
    │   ou
    │   {"type": "chart", "content": {...}}
    │   ou
    │   {"type": "text", "content": "..."}  # ⚠️ Problema aqui!
    └─ Retorna: {"final_response": {...}}
    ↓
streamlit_app.py (linhas 249-600)
    ├─ Recebe: msg["content"] = {"type": "text", "content": "..."}
    ├─ response_type = "text"
    ├─ content = "..."
    └─ st.write(content)  # ⚠️ MAS CONTENT PODE SER {...} NÃO STRING!
```

**Problemas identificados:**

1. **🔴 CRÍTICO: `format_final_response` linha 397**
   ```python
   response = {"type": "text", "content": "Não consegui processar a sua solicitação."}
   ```
   - Este é o FALLBACK quando não há `plotly_spec` nem `retrieved_data`
   - Mas o CodeGenAgent RETORNOU dados! Eles estão sendo perdidos!

2. **🔴 CRÍTICO: Resposta do CodeGenAgent não é processada corretamente**
   - `bi_agent_nodes.py` linhas 361-371:
   ```python
   elif code_gen_response.get("type") == "dataframe":
       # Converte DataFrame para dicionários
       df_result = code_gen_response.get("output")
       return {"retrieved_data": df_result.to_dict(orient='records')}
   elif code_gen_response.get("type") == "text":
       # ⚠️ AQUI: Retorna como final_response
       return {"final_response": {"type": "text", "content": str(code_gen_response.get("output"))}}
   ```
   - Se CodeGenAgent retornar `type="text"`, vai para `final_response` DIRETO
   - Mas se retornar `type="dataframe"`, vai para `retrieved_data`
   - E `format_final_response` só processa `retrieved_data` se existir!

3. **🔴 CRÍTICO: Renderização no streamlit_app.py linha 569-574**
   ```python
   else:
       # 📝 Para respostas de texto, também mostrar contexto se disponível
       user_query = response_data.get("user_query")
       if user_query and msg["role"] == "assistant":
           st.caption(f"📝 Pergunta: {user_query}")

       st.write(content)  # ⚠️ CONTENT PODE SER {} NÃO STRING!
   ```
   - Se `content` for um dict/object, `st.write()` vai renderizar JSON
   - Usuário vê `{}` ou estrutura interna, não a RESPOSTA DA LLM

---

## 🎯 PLANO DE CORREÇÃO

### **FASE 1: ADICIONAR LOGS CRÍTICOS (15 min)**

**Objetivo:** Identificar EXATAMENTE onde a resposta é perdida

**Arquivo:** `core/agents/bi_agent_nodes.py`

**Ação 1.1:** Adicionar logs em `generate_plotly_spec` (linha 353-376)

```python
# APÓS linha 354:
logger.info("🚀 Calling code_gen_agent.generate_and_execute_code...")
code_gen_response = code_gen_agent.generate_and_execute_code(code_gen_input)

# ✅ ADICIONAR LOGS DETALHADOS:
logger.info(f"📋 CodeGenAgent response type: {code_gen_response.get('type')}")
logger.info(f"📋 CodeGenAgent response keys: {list(code_gen_response.keys())}")

# Se tipo for 'dataframe' ou 'text', logar tamanho/conteúdo
if code_gen_response.get("type") == "dataframe":
    df_result = code_gen_response.get("output")
    logger.info(f"📊 DataFrame result: {len(df_result)} rows, {len(df_result.columns)} cols")
    logger.info(f"📊 DataFrame sample: {df_result.head(3).to_dict(orient='records')}")
elif code_gen_response.get("type") == "text":
    text_output = str(code_gen_response.get("output"))
    logger.info(f"📝 Text result length: {len(text_output)}")
    logger.info(f"📝 Text result preview: {text_output[:500]}...")
```

**Ação 1.2:** Adicionar logs em `format_final_response` (linha 378-407)

```python
# APÓS linha 383:
logger.info(f"[NODE] format_final_response: Formatando resposta para '{user_query}'")

# ✅ ADICIONAR LOGS DETALHADOS DE ESTADO:
logger.info(f"🔍 STATE KEYS: {list(state.keys())}")
logger.info(f"🔍 clarification_needed: {state.get('clarification_needed')}")
logger.info(f"🔍 plotly_spec exists: {bool(state.get('plotly_spec'))}")
logger.info(f"🔍 retrieved_data exists: {bool(state.get('retrieved_data'))}")
logger.info(f"🔍 final_response exists: {bool(state.get('final_response'))}")

# Se retrieved_data existir, logar detalhes
if state.get("retrieved_data"):
    data = state.get("retrieved_data")
    logger.info(f"📊 retrieved_data type: {type(data)}")
    logger.info(f"📊 retrieved_data length: {len(data) if isinstance(data, list) else 'N/A'}")
    if isinstance(data, list) and len(data) > 0:
        logger.info(f"📊 retrieved_data sample keys: {list(data[0].keys())}")
```

---

### **FASE 2: CORRIGIR LÓGICA DE RESPOSTA (30 min)**

**Problema:** `format_final_response` não processa corretamente quando CodeGenAgent retorna dados

**Arquivo:** `core/agents/bi_agent_nodes.py`

**Correção 2.1:** Modificar `format_final_response` (linha 378-407)

```python
def format_final_response(state: AgentState) -> Dict[str, Any]:
    """
    Formata a resposta final para o utilizador.
    """
    user_query = state['messages'][-1]['content']
    logger.info(f"[NODE] format_final_response: Formatando resposta para '{user_query}'")

    # 🔍 LOGS DETALHADOS
    logger.info(f"🔍 STATE KEYS: {list(state.keys())}")

    # 📝 Construir resposta baseada no estado
    response = {}

    # ✅ PRIORIDADE 1: Verificar se já existe final_response (resposta direta do CodeGenAgent)
    if state.get("final_response"):
        logger.info(f"✅ Using pre-formatted final_response from state")
        response = state.get("final_response")
        # Garantir que user_query esteja presente
        if "user_query" not in response:
            response["user_query"] = user_query

    # ✅ PRIORIDADE 2: Clarificação
    elif state.get("clarification_needed"):
        response = {"type": "clarification", "content": state.get("clarification_options")}
        logger.info(f"💬 CLARIFICATION RESPONSE for query: '{user_query}'")

    # ✅ PRIORIDADE 3: Gráfico
    elif state.get("plotly_spec"):
        response = {"type": "chart", "content": state.get("plotly_spec")}
        response["user_query"] = user_query
        logger.info(f"📈 CHART RESPONSE for query: '{user_query}'")

    # ✅ PRIORIDADE 4: Dados tabulares
    elif state.get("retrieved_data"):
        data = state.get("retrieved_data")
        response = {"type": "data", "content": _clean_json_values(data)}
        response["user_query"] = user_query
        logger.info(f"📊 DATA RESPONSE for query: '{user_query}' - {len(data)} rows")

    # ❌ FALLBACK: Se nenhum dos acima
    else:
        response = {"type": "text", "content": "❌ Não consegui processar a sua solicitação. Tente reformular a pergunta."}
        response["user_query"] = user_query
        logger.warning(f"❓ FALLBACK RESPONSE for query: '{user_query}' - No data in state")
        logger.warning(f"❓ State keys available: {list(state.keys())}")

    # ✅ GARANTIR que a pergunta do usuário seja preservada no histórico
    final_messages = state['messages'] + [{"role": "assistant", "content": response}]

    # 🔍 LOG DO RESULTADO FINAL
    logger.info(f"✅ FINAL RESPONSE - Type: {response.get('type')}, User Query: '{user_query}'")
    logger.info(f"📋 MESSAGE HISTORY - Total messages: {len(final_messages)}")

    return {"messages": final_messages, "final_response": response}
```

**Correção 2.2:** Modificar `generate_plotly_spec` para garantir resposta correta (linha 358-376)

```python
# APÓS linha 354:
logger.info("🚀 Calling code_gen_agent.generate_and_execute_code...")
code_gen_response = code_gen_agent.generate_and_execute_code(code_gen_input)

# ✅ LOGS DETALHADOS
logger.info(f"📋 CodeGenAgent response type: {code_gen_response.get('type')}")
logger.info(f"📋 CodeGenAgent response keys: {list(code_gen_response.keys())}")

# Processa a resposta do CodeGenAgent
if code_gen_response.get("type") == "chart":
    plotly_spec = json.loads(code_gen_response.get("output"))
    logger.info(f"📈 Chart generated successfully")
    return {"plotly_spec": plotly_spec}

elif code_gen_response.get("type") == "dataframe":
    # ✅ CORREÇÃO: Converter DataFrame para lista de dicionários
    df_result = code_gen_response.get("output")
    logger.info(f"📊 DataFrame result: {len(df_result)} rows")

    # ✅ IMPORTANTE: Garantir que seja lista de dicts
    if isinstance(df_result, pd.DataFrame):
        data_list = df_result.to_dict(orient='records')
    else:
        data_list = df_result

    logger.info(f"📊 Converted to {len(data_list)} records")
    return {"retrieved_data": data_list}

elif code_gen_response.get("type") == "text":
    # ✅ CORREÇÃO: Garantir que texto seja STRING
    text_output = str(code_gen_response.get("output"))
    logger.info(f"📝 Text result length: {len(text_output)}")

    # ✅ RETORNAR COMO final_response para que seja processado corretamente
    return {
        "final_response": {
            "type": "text",
            "content": text_output,
            "user_query": user_query
        }
    }

elif code_gen_response.get("type") == "error":
    error_msg = code_gen_response.get("output", "Erro desconhecido")
    logger.error(f"❌ CodeGenAgent error: {error_msg}")
    return {
        "final_response": {
            "type": "text",
            "content": f"❌ Erro ao processar: {error_msg}",
            "user_query": user_query
        }
    }

else:
    # ✅ FALLBACK: Tipo desconhecido
    logger.warning(f"⚠️ Unknown CodeGenAgent response type: {code_gen_response.get('type')}")
    return {
        "final_response": {
            "type": "text",
            "content": f"⚠️ Resposta inesperada do agente: {code_gen_response.get('output')}",
            "user_query": user_query
        }
    }
```

---

### **FASE 3: MELHORAR RENDERIZAÇÃO NO STREAMLIT (15 min)**

**Arquivo:** `streamlit_app.py`

**Correção 3.1:** Garantir renderização correta de respostas de texto (linha 569-574)

```python
else:
    # 📝 Para respostas de texto
    user_query = response_data.get("user_query")
    if user_query and msg["role"] == "assistant":
        st.caption(f"📝 Pergunta: {user_query}")

    # ✅ GARANTIR que content seja STRING
    if isinstance(content, str):
        st.markdown(content)
    elif isinstance(content, dict):
        # Se for dict, tentar extrair mensagem
        if "message" in content:
            st.markdown(content["message"])
        elif "text" in content:
            st.markdown(content["text"])
        else:
            # Último recurso: mostrar JSON formatado
            st.warning("⚠️ Resposta em formato não esperado:")
            st.json(content)
    else:
        # Converter para string
        st.markdown(str(content))
```

---

### **FASE 4: ADICIONAR TRATAMENTO DE ERRO DETALHADO (10 min)**

**Arquivo:** `streamlit_app.py`

**Correção 4.1:** Adicionar expander de debug para admins (após linha 574)

```python
# APÓS renderizar resposta, adicionar debug para admins
if msg["role"] == "assistant" and st.session_state.get('role') == 'admin':
    with st.expander("🔍 Debug (Admin)", expanded=False):
        st.write("**Response Data Structure:**")
        st.json(response_data)

        st.write("**Response Type:**", response_type)
        st.write("**Content Type:**", type(content).__name__)

        if isinstance(content, str):
            st.write("**Content Length:**", len(content))
        elif isinstance(content, (list, dict)):
            st.write("**Content Keys/Length:**",
                    list(content.keys()) if isinstance(content, dict) else len(content))
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### **FASE 1: Logs (15 min)** - CRÍTICO
- [ ] Adicionar logs em `generate_plotly_spec` (linhas 353-376)
- [ ] Adicionar logs em `format_final_response` (linhas 378-407)
- [ ] Testar localmente com query simples
- [ ] Verificar logs no terminal

### **FASE 2: Correções (30 min)** - CRÍTICO
- [ ] Modificar `format_final_response` (linhas 378-407)
- [ ] Modificar `generate_plotly_spec` (linhas 358-376)
- [ ] Testar localmente com 3 queries:
  - [ ] "qual é o preço do produto 369947"
  - [ ] "ranking de vendas do tecido"
  - [ ] "top 10 produtos de papelaria"

### **FASE 3: Renderização (15 min)** - IMPORTANTE
- [ ] Modificar renderização de texto no streamlit_app.py (linhas 569-574)
- [ ] Adicionar tratamento de dict/string
- [ ] Testar que resposta aparece corretamente

### **FASE 4: Debug (10 min)** - OPCIONAL
- [ ] Adicionar expander de debug para admins
- [ ] Testar visualização de estrutura de dados
- [ ] Verificar que não quebra para usuários normais

### **FASE 5: Deploy (5 min)**
- [ ] Commit com mensagem clara
- [ ] Push para branch
- [ ] Merge para main
- [ ] Aguardar redeploy no Streamlit Cloud (2-3 min)
- [ ] Testar em produção

---

## 🎯 RESUMO EXECUTIVO

**Problema:** Resposta da LLM é gerada corretamente mas PERDIDA entre o CodeGenAgent e a renderização final

**Causa Raiz:**
1. `format_final_response` não processa `final_response` do estado (linha 397)
2. `generate_plotly_spec` retorna estrutura inconsistente para texto (linha 367)
3. Renderização assume que `content` é sempre string (linha 574)

**Solução:**
1. ✅ Adicionar logs para rastrear dados
2. ✅ Corrigir lógica de `format_final_response` para processar `final_response` PRIMEIRO
3. ✅ Garantir que `generate_plotly_spec` sempre retorna estrutura correta
4. ✅ Melhorar renderização para lidar com dict/string

**Tempo Estimado:** 70 minutos
**Prioridade:** 🔴 CRÍTICA
**Impacto:** ALTO - Fix completo do problema

---

## 📊 TESTE DE VALIDAÇÃO

Após implementação, testar estas 3 queries:

1. **Query Simples (Filtro)**
   - Input: "qual é o preço do produto 369947"
   - Esperado: Tabela com 36 linhas mostrando preços
   - Verificar: Dados aparecem corretamente

2. **Query Complexa (Ranking)**
   - Input: "ranking de vendas do tecido"
   - Esperado: Ranking com ~19,726 produtos ordenados
   - Verificar: Dados aparecem ordenados por VENDA_30DD

3. **Query com Limite (Top N)**
   - Input: "top 10 produtos de papelaria"
   - Esperado: Tabela com EXATAMENTE 10 linhas
   - Verificar: Apenas 10 produtos aparecem

**Critério de Sucesso:** 3/3 queries exibem resposta corretamente para o usuário

---

**Próximo Passo:** Implementar FASE 1 (logs) para confirmar diagnóstico
