# 🔧 API Reference - Agent_Solution_BI

**Versão:** 3.0
**Data de Atualização:** 21 de setembro de 2025
**Base URL:** `http://localhost:8000` (desenvolvimento) | `https://your-domain.com` (produção)

---

## 📋 **Visão Geral da API**

A API do Agent_Solution_BI fornece endpoints RESTful para integração com o sistema de Business Intelligence conversacional. Construída com **FastAPI**, oferece documentação automática e validação de dados robusta.

### **Características Principais:**
- 🚀 **FastAPI**: Framework moderno e de alta performance
- 📝 **OpenAPI/Swagger**: Documentação automática interativa
- ✅ **Pydantic**: Validação automática de dados
- 🔒 **Autenticação**: Baseada em sessões e tokens
- 📊 **Rate Limiting**: Proteção contra abuso
- 🔄 **Async Support**: Operações assíncronas

---

## 🎯 **Endpoints Principais**

### **Documentação Interativa**
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

---

## 💬 **Endpoints de Consulta**

### **POST /api/v1/query**
**Descrição:** Endpoint principal para envio de consultas em linguagem natural.

#### **Request**
```json
{
  "user_query": "Mostre a evolução das vendas nos últimos 6 meses",
  "session_id": "usuario123_20250921"
}
```

#### **Request Schema**
```python
class QueryRequest(BaseModel):
    user_query: str = Field(..., description="Consulta do usuário em linguagem natural", min_length=1, max_length=1000)
    session_id: str = Field(..., description="ID de sessão para gerenciar o estado da conversa", regex="^[a-zA-Z0-9_-]+$")
```

#### **Response Success (200)**
```json
{
  "status": "success",
  "response": {
    "text": "Aqui está a evolução das vendas dos últimos 6 meses...",
    "chart_data": {
      "type": "line",
      "data": [
        {"month": "2025-03", "sales": 125000},
        {"month": "2025-04", "sales": 130000},
        {"month": "2025-05", "sales": 140000}
      ],
      "chart_config": {
        "title": "Evolução das Vendas - Últimos 6 Meses",
        "x_axis": "month",
        "y_axis": "sales"
      }
    },
    "metadata": {
      "intent": "gerar_grafico",
      "execution_time": 2.34,
      "data_points": 6
    }
  },
  "session_id": "usuario123_20250921",
  "timestamp": "2025-09-21T10:30:00Z"
}
```

#### **Response Error (400)**
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_QUERY",
    "message": "Consulta muito vaga. Por favor, seja mais específico.",
    "details": "A consulta precisa conter informações sobre o que você deseja analisar."
  },
  "session_id": "usuario123_20250921",
  "timestamp": "2025-09-21T10:30:00Z"
}
```

#### **Response Error (500)**
```json
{
  "status": "error",
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Erro interno do sistema",
    "details": "Falha na comunicação com o serviço de IA"
  },
  "session_id": "usuario123_20250921",
  "timestamp": "2025-09-21T10:30:00Z"
}
```

#### **Exemplos de Uso**

**cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Quais são os 10 produtos mais vendidos?",
    "session_id": "usuario123_20250921"
  }'
```

**Python (requests):**
```python
import requests

url = "http://localhost:8000/api/v1/query"
payload = {
    "user_query": "Mostre a evolução das vendas mensais",
    "session_id": "usuario123_20250921"
}

response = requests.post(url, json=payload)
data = response.json()

if data["status"] == "success":
    print(data["response"]["text"])
    chart_data = data["response"]["chart_data"]
else:
    print(f"Erro: {data['error']['message']}")
```

**JavaScript (fetch):**
```javascript
const query = async (userQuery, sessionId) => {
  try {
    const response = await fetch('/api/v1/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_query: userQuery,
        session_id: sessionId
      })
    });

    const data = await response.json();

    if (data.status === 'success') {
      return data.response;
    } else {
      throw new Error(data.error.message);
    }
  } catch (error) {
    console.error('Erro na consulta:', error);
    throw error;
  }
};
```

---

## 🔍 **Endpoints de Sistema**

### **GET /health**
**Descrição:** Verifica o status de saúde do sistema e suas dependências.

#### **Response (200)**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-21T10:30:00Z",
  "version": "3.0.0",
  "uptime": 86400,
  "dependencies": {
    "llm": {
      "status": "healthy",
      "response_time": 0.45,
      "last_check": "2025-09-21T10:29:55Z"
    },
    "database": {
      "status": "healthy",
      "connection_pool": {
        "active": 2,
        "idle": 8,
        "max": 10
      },
      "last_check": "2025-09-21T10:29:55Z"
    },
    "parquet": {
      "status": "healthy",
      "file_size": "20.8MB",
      "last_modified": "2025-09-19T22:51:00Z",
      "records_count": 45678
    }
  }
}
```

#### **Response Error (503)**
```json
{
  "status": "unhealthy",
  "timestamp": "2025-09-21T10:30:00Z",
  "version": "3.0.0",
  "dependencies": {
    "llm": {
      "status": "error",
      "error": "API key invalid or quota exceeded",
      "last_check": "2025-09-21T10:29:55Z"
    },
    "database": {
      "status": "error",
      "error": "Connection timeout",
      "last_check": "2025-09-21T10:29:55Z"
    }
  }
}
```

### **GET /api/v1/info**
**Descrição:** Retorna informações básicas sobre a API e recursos disponíveis.

#### **Response (200)**
```json
{
  "api_version": "3.0.0",
  "name": "Agent_Solution_BI API",
  "description": "API para Business Intelligence conversacional",
  "features": [
    "Natural Language Processing",
    "Automatic Chart Generation",
    "Data Analysis",
    "Session Management"
  ],
  "supported_languages": ["pt-BR"],
  "data_sources": [
    {
      "name": "Products Database",
      "type": "parquet",
      "records": 45678,
      "last_updated": "2025-09-19T22:51:00Z"
    }
  ],
  "limits": {
    "max_query_length": 1000,
    "rate_limit": "100 requests/minute",
    "session_timeout": 3600
  }
}
```

---

## 📊 **Endpoints de Dados**

### **GET /api/v1/schema**
**Descrição:** Retorna o schema dos dados disponíveis para consulta.

#### **Response (200)**
```json
{
  "tables": {
    "products": {
      "description": "Dados de produtos e estoque",
      "columns": {
        "codigo": {
          "type": "integer",
          "description": "Código único do produto",
          "business_name": "Código do Produto"
        },
        "descricao": {
          "type": "string",
          "description": "Descrição do produto",
          "business_name": "Descrição"
        },
        "preco": {
          "type": "float",
          "description": "Preço de venda em reais",
          "business_name": "Preço"
        },
        "estoque": {
          "type": "integer",
          "description": "Quantidade em estoque",
          "business_name": "Estoque"
        },
        "categoria": {
          "type": "string",
          "description": "Categoria do produto",
          "business_name": "Categoria"
        },
        "fornecedor": {
          "type": "string",
          "description": "Nome do fornecedor",
          "business_name": "Fornecedor"
        },
        "data_ultima_venda": {
          "type": "datetime",
          "description": "Data da última venda",
          "business_name": "Última Venda"
        }
      },
      "row_count": 45678,
      "last_updated": "2025-09-19T22:51:00Z"
    }
  }
}
```

### **GET /api/v1/stats**
**Descrição:** Retorna estatísticas gerais dos dados.

#### **Response (200)**
```json
{
  "summary": {
    "total_products": 45678,
    "active_products": 42156,
    "categories_count": 156,
    "suppliers_count": 1247,
    "avg_price": 125.67,
    "total_stock_value": 15678900.45
  },
  "date_range": {
    "oldest_record": "2020-01-15T00:00:00Z",
    "newest_record": "2025-09-19T22:51:00Z",
    "data_coverage_days": 1978
  },
  "top_categories": [
    {"name": "Eletrônicos", "count": 8456, "percentage": 18.5},
    {"name": "Roupas", "count": 7234, "percentage": 15.8},
    {"name": "Casa e Jardim", "count": 6789, "percentage": 14.9}
  ]
}
```

---

## 📝 **Endpoints de Sessão**

### **POST /api/v1/session/start**
**Descrição:** Inicia uma nova sessão de conversa.

#### **Request**
```json
{
  "user_id": "usuario123",
  "context": {
    "department": "vendas",
    "role": "analyst"
  }
}
```

#### **Response (201)**
```json
{
  "session_id": "usuario123_20250921_103045",
  "created_at": "2025-09-21T10:30:45Z",
  "expires_at": "2025-09-21T11:30:45Z",
  "context": {
    "department": "vendas",
    "role": "analyst"
  }
}
```

### **GET /api/v1/session/{session_id}/history**
**Descrição:** Retorna o histórico de consultas da sessão.

#### **Response (200)**
```json
{
  "session_id": "usuario123_20250921_103045",
  "queries": [
    {
      "timestamp": "2025-09-21T10:31:00Z",
      "query": "Mostre vendas do último mês",
      "intent": "gerar_grafico",
      "execution_time": 2.1,
      "success": true
    },
    {
      "timestamp": "2025-09-21T10:32:15Z",
      "query": "Qual produto teve mais vendas?",
      "intent": "resposta_simples",
      "execution_time": 1.5,
      "success": true
    }
  ],
  "total_queries": 2,
  "avg_execution_time": 1.8
}
```

### **DELETE /api/v1/session/{session_id}**
**Descrição:** Encerra uma sessão ativa.

#### **Response (200)**
```json
{
  "message": "Sessão encerrada com sucesso",
  "session_id": "usuario123_20250921_103045",
  "ended_at": "2025-09-21T10:45:00Z",
  "duration": 875,
  "total_queries": 5
}
```

---

## 🚨 **Códigos de Erro**

### **Códigos HTTP Padrão**
- **200**: OK - Requisição bem-sucedida
- **201**: Created - Recurso criado com sucesso
- **400**: Bad Request - Dados de entrada inválidos
- **401**: Unauthorized - Autenticação necessária
- **403**: Forbidden - Acesso negado
- **404**: Not Found - Recurso não encontrado
- **422**: Unprocessable Entity - Dados válidos mas processamento falhou
- **429**: Too Many Requests - Rate limit excedido
- **500**: Internal Server Error - Erro interno do servidor
- **503**: Service Unavailable - Serviço temporariamente indisponível

### **Códigos de Erro Customizados**
```json
{
  "INVALID_QUERY": "Consulta inválida ou muito vaga",
  "LLM_ERROR": "Erro na comunicação com o serviço de IA",
  "DATA_NOT_FOUND": "Dados solicitados não encontrados",
  "SESSION_EXPIRED": "Sessão expirada",
  "RATE_LIMIT_EXCEEDED": "Limite de requisições excedido",
  "PARQUET_ERROR": "Erro ao acessar os dados",
  "CHART_GENERATION_ERROR": "Erro na geração do gráfico",
  "INVALID_SESSION": "Sessão inválida ou não encontrada"
}
```

---

## 🔒 **Autenticação e Segurança**

### **Autenticação por Sessão**
```python
# Headers necessários
headers = {
    "Content-Type": "application/json",
    "X-Session-ID": "usuario123_20250921_103045"
}
```

### **Rate Limiting**
- **Limite**: 100 requisições por minuto por IP
- **Headers de resposta**:
  ```
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 87
  X-RateLimit-Reset: 1632225600
  ```

### **Validação de Entrada**
- Consultas limitadas a 1000 caracteres
- Session IDs devem seguir padrão alfanumérico
- Validação automática via Pydantic

---

## 🔧 **SDK e Bibliotecas**

### **Python SDK**
```python
from agent_bi_client import AgentBIClient

# Inicializar cliente
client = AgentBIClient(base_url="http://localhost:8000")

# Iniciar sessão
session = client.start_session(user_id="usuario123")

# Fazer consulta
response = client.query(
    "Mostre vendas do último trimestre",
    session_id=session.id
)

# Acessar resultados
print(response.text)
if response.has_chart:
    chart = response.chart_data
    print(f"Gráfico: {chart.title}")
```

### **JavaScript SDK**
```javascript
import { AgentBIClient } from 'agent-bi-js-client';

const client = new AgentBIClient({
  baseURL: 'http://localhost:8000'
});

// Fazer consulta
const response = await client.query({
  userQuery: 'Top 10 produtos mais vendidos',
  sessionId: 'usuario123_20250921'
});

console.log(response.text);
if (response.chartData) {
  renderChart(response.chartData);
}
```

---

## 📊 **Webhooks**

### **Configuração de Webhooks**
```json
{
  "url": "https://your-app.com/webhook/agent-bi",
  "events": ["query.completed", "error.occurred"],
  "secret": "webhook_secret_key"
}
```

### **Payload do Webhook**
```json
{
  "event": "query.completed",
  "timestamp": "2025-09-21T10:30:00Z",
  "session_id": "usuario123_20250921",
  "data": {
    "query": "Vendas mensais",
    "intent": "gerar_grafico",
    "execution_time": 2.1,
    "success": true
  }
}
```

---

## 🧪 **Ambiente de Testes**

### **Dados de Teste**
```json
{
  "test_queries": [
    "Qual é o preço do produto 12345?",
    "Mostre vendas dos últimos 3 meses",
    "Top 5 categorias por faturamento"
  ],
  "test_session_id": "test_session_123",
  "expected_response_time": "< 3 segundos"
}
```

### **Endpoint de Teste**
```bash
# Teste básico de funcionamento
curl -X GET "http://localhost:8000/health"

# Teste de consulta
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"user_query": "teste", "session_id": "test_123"}'
```

---

## 📈 **Monitoramento e Logs**

### **Métricas Disponíveis**
- **Latência**: Tempo de resposta por endpoint
- **Throughput**: Requisições por minuto
- **Taxa de Erro**: Percentual de falhas
- **Uso de LLM**: Tokens consumidos

### **Logs Estruturados**
```json
{
  "timestamp": "2025-09-21T10:30:00Z",
  "level": "INFO",
  "endpoint": "/api/v1/query",
  "session_id": "usuario123_20250921",
  "execution_time": 2.1,
  "intent": "gerar_grafico",
  "success": true
}
```

---

## 🔄 **Versionamento**

### **Estratégia de Versionamento**
- **URL Path**: `/api/v1/`, `/api/v2/`
- **Backward Compatibility**: Mantida por 12 meses
- **Deprecation Notices**: Headers de resposta

### **Versões Suportadas**
- **v1** (atual): Totalmente suportada
- **v0** (legada): Deprecated - suporte até dezembro 2025

---

**📝 Esta documentação é gerada automaticamente e mantida atualizada.**
**📧 Para dúvidas técnicas:** dev-team@company.com
**🔧 Para suporte de integração:** api-support@company.com