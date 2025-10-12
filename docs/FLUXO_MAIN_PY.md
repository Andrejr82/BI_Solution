# Fluxo do main.py (Backend FastAPI Standalone)
**Data:** 10/10/2025
**Tipo:** Documentação Técnica
**Status:** Completo

---

## Visão Geral

O arquivo `main.py` é um **backend FastAPI standalone OPCIONAL** que serve como API REST gateway. Ele **NÃO é necessário** para o funcionamento normal do sistema, pois o `streamlit_app.py` já possui backend integrado.

---

## Quando Usar main.py

### ✅ Use main.py se:
- Precisa acessar o sistema via API REST (não via interface web)
- Quer integrar com outros sistemas/serviços
- Precisa de endpoints programáticos
- Quer separar frontend e backend fisicamente

### ❌ NÃO use main.py se:
- Usa apenas a interface Streamlit web
- Quer o modo integrado (mais simples)
- Não precisa de acesso via API

---

## Arquitetura: Modo Integrado vs Modo API

### Modo Integrado (Padrão - Recomendado)
```
┌─────────────────────────────────┐
│      streamlit_app.py           │
│                                 │
│  ┌────────────┐  ┌───────────┐ │
│  │  Frontend  │  │  Backend  │ │
│  │  (UI)      │  │  (Logic)  │ │
│  └────────────┘  └───────────┘ │
│                                 │
│  - LLM Adapter                  │
│  - HybridDataAdapter            │
│  - DirectQueryEngine            │
│  - LangGraph (desabilitado)     │
└─────────────────────────────────┘

Comando: streamlit run streamlit_app.py
Porta: 8501
```

### Modo API Standalone (Opcional)
```
┌─────────────────┐        ┌─────────────────┐
│  main.py        │        │ streamlit_app.py│
│  (Backend API)  │◄───────┤  (Frontend)     │
│                 │  HTTP  │                 │
│  FastAPI        │        │  Chamadas API   │
│  Port 8000      │        │                 │
└─────────────────┘        └─────────────────┘

Comando Backend: uvicorn main:app --host 0.0.0.0 --port 8000
Comando Frontend: streamlit run streamlit_app.py
```

**⚠️ NOTA:** Este modo requer configuração adicional no streamlit_app.py

---

## Fluxo de Inicialização do main.py

### 1. Importações
```python
# main.py:1-20
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Componentes do sistema
from core.graph.graph_builder import GraphBuilder
from core.config.settings import settings
from core.llm_adapter import OpenAILLMAdapter
from core.connectivity.sql_server_adapter import SQLServerAdapter
from core.agents.code_gen_agent import CodeGenAgent
```

### 2. Modelos Pydantic
```python
# main.py:22-28
class QueryRequest(BaseModel):
    user_query: str
    session_id: str

class QueryResponse(BaseModel):
    response: dict
```

### 3. Inicialização da Aplicação FastAPI
```python
# main.py:30-43
app = FastAPI(
    title="Agent_BI - API Gateway",
    description="Backend FastAPI para a nova arquitetura com LangGraph.",
    version="3.0.0"
)

# Instanciar componentes
llm_adapter = OpenAILLMAdapter()
db_adapter = SQLServerAdapter(connection_string=settings.SQL_SERVER_CONNECTION_STRING)
code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter)
graph_builder = GraphBuilder(llm_adapter=llm_adapter, db_adapter=db_adapter, code_gen_agent=code_gen_agent)
agent_graph = graph_builder.build()
```

### 4. Endpoints

#### POST /api/v1/query
```python
# main.py:46-72
@app.post("/api/v1/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    # Processar query via agent_graph
    initial_state = {
        "messages": [{"role": "user", "content": request.user_query}]
    }

    final_state = agent_graph.invoke(initial_state)

    response_content = final_state.get("final_response", {
        "type": "error",
        "content": "Ocorreu um erro inesperado no processamento do agente."
    })

    return QueryResponse(response=response_content)
```

#### GET /status
```python
# main.py:74-76
@app.get("/status")
def status():
    return {"status": "Agent_BI API is running"}
```

---

## Como Usar main.py

### Opção 1: Via start_app.py (Recomendado)
```bash
python start_app.py
```
**O que acontece:**
1. `start_app.py` detecta que `main.py` existe
2. Inicia FastAPI em background (porta 8000)
3. Inicia Streamlit em foreground (porta 8501)

**Código relevante em start_app.py:74-88:**
```python
backend_exists = check_file_exists("main.py")
backend_process = None

if backend_exists:
    backend_process = subprocess.Popen(
        [python_cmd, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(3)
```

### Opção 2: Manualmente
```bash
# Terminal 1: Backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend (se necessário)
streamlit run streamlit_app.py
```

### Opção 3: Docker/Produção
```bash
# Dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Endpoints Disponíveis

### POST /api/v1/query
**Descrição:** Processar consulta de usuário

**Request:**
```json
{
  "user_query": "produto mais vendido",
  "session_id": "uuid-123"
}
```

**Response:**
```json
{
  "response": {
    "type": "chart",
    "title": "Produto Mais Vendido",
    "content": "O produto mais vendido é X com 1000 vendas",
    "chart_data": {
      "x": [...],
      "y": [...]
    }
  }
}
```

**Exemplo com curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "produto mais vendido",
    "session_id": "test-123"
  }'
```

**Exemplo com Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "user_query": "produto mais vendido",
        "session_id": "test-123"
    }
)

result = response.json()
print(result["response"])
```

### GET /status
**Descrição:** Health check do backend

**Response:**
```json
{
  "status": "Agent_BI API is running"
}
```

**Exemplo:**
```bash
curl http://localhost:8000/status
```

---

## Diferenças entre main.py e streamlit_app.py

| Aspecto | main.py | streamlit_app.py |
|---------|---------|------------------|
| **Tipo** | Backend API REST | Frontend Web + Backend Integrado |
| **Framework** | FastAPI | Streamlit |
| **Porta** | 8000 | 8501 |
| **UI** | Nenhuma (apenas JSON) | Interface web completa |
| **Backend** | Separado | Integrado |
| **Autenticação** | Não implementada | Completa (SQL/Cloud) |
| **DirectQueryEngine** | Não usa | Usa (cached) |
| **agent_graph** | Usa diretamente | Desabilitado (hotfix) |
| **Quando usar** | API programática | Interface web |

---

## Diagrama de Fluxo: main.py

```
┌─────────────────────────────────────────────────────────────────┐
│                       MAIN.PY FLOW                               │
└─────────────────────────────────────────────────────────────────┘

Startup (uvicorn main:app)
    │
    ▼
┌─────────────────────────────────────┐
│  Importar Dependências              │
│  - FastAPI                          │
│  - GraphBuilder                     │
│  - LLM Adapters                     │
│  - DB Adapters                      │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Inicializar Componentes            │
│  1. llm_adapter = OpenAILLMAdapter()│
│  2. db_adapter = SQLServerAdapter() │
│  3. code_gen_agent = CodeGenAgent() │
│  4. graph_builder = GraphBuilder()  │
│  5. agent_graph = builder.build()   │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Criar Aplicação FastAPI            │
│  app = FastAPI(...)                 │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Registrar Endpoints                │
│  - POST /api/v1/query               │
│  - GET /status                      │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Servidor Pronto                    │
│  http://localhost:8000              │
└─────────────────────────────────────┘

Quando recebe POST /api/v1/query:
    │
    ▼
┌─────────────────────────────────────┐
│  1. Validar QueryRequest            │
│     - user_query: str               │
│     - session_id: str               │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  2. Criar Initial State             │
│     {                               │
│       "messages": [                 │
│         {"role": "user",            │
│          "content": user_query}     │
│       ]                             │
│     }                               │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  3. Invocar Agent Graph             │
│     final_state = agent_graph       │
│       .invoke(initial_state)        │
│                                     │
│  ⚠️ ATENÇÃO: Sem timeout!          │
│  Pode travar em queries complexas   │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  4. Extrair final_response          │
│     response_content =              │
│       final_state.get(              │
│         "final_response"            │
│       )                             │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  5. Retornar QueryResponse          │
│     {                               │
│       "response": response_content  │
│     }                               │
└─────────────────────────────────────┘
```

---

## Problemas Conhecidos do main.py

### 1. agent_graph.invoke() sem timeout
**Problema:** Mesmo problema que foi corrigido no streamlit_app.py
```python
# main.py:60 - VULNERÁVEL A TRAVAMENTOS
final_state = agent_graph.invoke(initial_state)  # ❌ SEM TIMEOUT!
```

**Solução:** Implementar timeout (mesma lógica do streamlit_app.py)

### 2. Não usa DirectQueryEngine
**Problema:** DirectQueryEngine é mais rápido (100-300ms) mas main.py não o usa
```python
# main.py sempre usa agent_graph (lento)
# Deveria tentar DirectQueryEngine primeiro
```

**Solução:** Adicionar lógica similar ao streamlit_app.py:
```python
# Pseudo-código
direct_engine = DirectQueryEngine(adapter)
direct_result = direct_engine.process_query(user_query)

if direct_result["type"] != "fallback":
    return direct_result  # Rápido!
else:
    # Fallback para agent_graph
    final_state = agent_graph.invoke(...)
```

### 3. Sem autenticação
**Problema:** Endpoints públicos sem controle de acesso
```python
# Qualquer um pode fazer POST /api/v1/query
```

**Solução:** Adicionar FastAPI dependencies com autenticação

### 4. Dependências desatualizadas
**Problema:** Usa `OpenAILLMAdapter` em vez de `GeminiLLMAdapter`
```python
# main.py:39 - DESATUALIZADO
llm_adapter = OpenAILLMAdapter()

# Deveria usar:
from core.factory.component_factory import ComponentFactory
llm_adapter = ComponentFactory.get_llm_adapter("gemini")
```

---

## Uso em Produção

### Recomendações
1. ✅ Implementar autenticação (JWT tokens)
2. ✅ Adicionar rate limiting
3. ✅ Implementar timeout no agent_graph
4. ✅ Adicionar health checks robustos
5. ✅ Usar DirectQueryEngine para queries simples
6. ✅ Adicionar logging adequado
7. ✅ Implementar CORS se necessário

### Exemplo de Produção com Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Backend FastAPI
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name api.agentbi.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Resumo Executivo

### main.py é OPCIONAL
- ✅ Sistema funciona 100% sem ele (modo integrado)
- ✅ Necessário apenas para acesso via API REST
- ⚠️ Tem problemas conhecidos (sem timeout, sem DirectQueryEngine)

### Quando NÃO usar
- Interface web Streamlit é suficiente
- Não precisa de API REST
- Quer simplicidade

### Quando usar
- Precisa integrar com outros sistemas
- Quer separação frontend/backend
- Acesso programático necessário

### Status Atual
- 🟡 Funcional mas desatualizado
- ⚠️ Vulnerável a travamentos (sem timeout)
- ❌ Não usa DirectQueryEngine (lento)
- ❌ Sem autenticação

---

**Autor:** Claude Code
**Data:** 10/10/2025
**Versão:** 1.0
**Status:** Completo

**Recomendação:** Use o modo integrado (`streamlit_app.py`) a menos que precise explicitamente de uma API REST.
