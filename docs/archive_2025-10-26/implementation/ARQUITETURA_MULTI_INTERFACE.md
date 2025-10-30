# 🏗️ Arquitetura Multi-Interface - Agent Solution BI

## 📋 Visão Geral

O **Agent Solution BI** agora oferece **3 interfaces diferentes** que compartilham o mesmo backend:

1. **Frontend React** (claude-share-buddy) - Interface moderna e profissional
2. **Streamlit** (streamlit_app.py) - Interface rápida para prototipagem
3. **API FastAPI** (api_server.py) - Endpoints REST para integração

## 🎯 Arquitetura do Sistema

```
┌──────────────────────────────────────────────────────────────┐
│                    INTERFACES DO USUÁRIO                     │
├─────────────────┬──────────────────┬─────────────────────────┤
│  Frontend React │    Streamlit     │   Outras Aplicações     │
│  (Port 8080)    │   (Port 8501)    │   (Integração via API)  │
│                 │                  │                         │
│  - Chat BI      │  - Chat BI       │  - Mobile Apps          │
│  - Dashboards   │  - Dashboard     │  - Desktop Apps         │
│  - Admin Panel  │  - Análises      │  - Scripts Python       │
│  - 14 páginas   │  - Gráficos      │  - Outros Sistemas      │
└────────┬────────┴────────┬─────────┴────────────┬────────────┘
         │                 │                      │
         │ HTTP/REST       │ Python API           │ HTTP/REST
         │ (via Proxy)     │ (Direto)             │ (Direto)
         │                 │                      │
┌────────▼─────────────────▼──────────────────────▼────────────┐
│                  API FASTAPI (Port 5000)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  /api/chat      /api/metrics     /api/examples       │   │
│  │  /api/queries   /api/feedback    /api/diagnostics    │   │
│  │  /docs          /redoc           /health             │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                         │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │     Backend Components (Lazy Loading)                 │   │
│  │  - LLM Adapter (Gemini)                              │   │
│  │  - Parquet Adapter (Polars/Dask)                     │   │
│  │  - Code Gen Agent                                     │   │
│  │  - Agent Graph (LangGraph)                           │   │
│  │  - Query History                                      │   │
│  └────────────────────────────────────────────────────────┘   │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│                   CAMADA DE DADOS                             │
│  ┌────────────────┬─────────────────┬──────────────┐        │
│  │ Parquet Files  │  SQL Server     │  Cache       │        │
│  │ (Data Lake)    │  (Opcional)     │  (Redis/Mem) │        │
│  └────────────────┴─────────────────┴──────────────┘        │
└───────────────────────────────────────────────────────────────┘
```

## 🔧 Componentes Principais

### 1. API FastAPI (`api_server.py`)

**Responsabilidades:**
- Servir endpoints REST para todas as interfaces
- Inicializar e gerenciar backend components (lazy loading)
- Processar requisições de chat com IA
- Fornecer métricas e diagnósticos
- Documentação automática (Swagger/Redoc)

**Endpoints Disponíveis:**
```python
GET  /                      # Info da API
GET  /api/health            # Status do sistema
POST /api/chat              # Processar mensagem
GET  /api/metrics           # Métricas do sistema
GET  /api/queries/history   # Histórico de consultas
GET  /api/examples          # Exemplos de perguntas
POST /api/save-chart        # Salvar gráfico
POST /api/feedback          # Enviar feedback
GET  /api/diagnostics/db    # Diagnóstico do banco
GET  /api/learning/metrics  # Métricas de ML
GET  /docs                  # Documentação Swagger
GET  /redoc                 # Documentação Redoc
```

**Tecnologias:**
- FastAPI 0.116.1
- Uvicorn (ASGI server)
- Pydantic (validação)
- CORS middleware

### 2. Frontend React (`frontend/`)

**Responsabilidades:**
- Interface moderna e responsiva
- 14 páginas completas
- Comunicação via proxy Vite
- Visualizações interativas

**Comunicação:**
```typescript
// Vite proxy redireciona para FastAPI
fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({ message: 'Top 10 produtos' })
})
// → http://localhost:5000/api/chat
```

**Tecnologias:**
- React 18.3 + TypeScript
- Vite (build + dev server + proxy)
- Tailwind CSS + shadcn/ui
- TanStack Query
- React Router

### 3. Streamlit (`streamlit_app.py`)

**Responsabilidades:**
- Interface rápida para prototipagem
- Acesso direto ao backend Python
- Visualizações Plotly
- Chat com IA

**Comunicação:**
```python
# Streamlit chama diretamente o backend
from core.graph.graph_builder import GraphBuilder

agent_graph = GraphBuilder(...).build()
result = agent_graph.invoke({"query": "Top 10 produtos"})
```

**Tecnologias:**
- Streamlit
- Acesso direto ao core Python
- Plotly para gráficos

### 4. Backend Core (`core/`)

**Responsabilidades:**
- Lógica de negócio
- Processamento de IA
- Acesso a dados
- Geração de código

**Componentes:**
- **LLM Adapter** - Interface com Gemini
- **Parquet Adapter** - Leitura otimizada de dados
- **Code Gen Agent** - Geração de código Python
- **Agent Graph** - Orquestração LangGraph
- **Query History** - Histórico de consultas

## 🚀 Como Executar

### Opção 1: API + Frontend React

```bash
# Terminal 1 - API FastAPI
python api_server.py
# → http://localhost:5000

# Terminal 2 - Frontend React
cd frontend
npm run dev
# → http://localhost:8080
```

### Opção 2: Streamlit

```bash
streamlit run streamlit_app.py
# → http://localhost:8501
```

### Opção 3: Todos Juntos

```bash
# Terminal 1
python api_server.py

# Terminal 2
streamlit run streamlit_app.py

# Terminal 3
cd frontend && npm run dev
```

**Acessar:**
- React: http://localhost:8080
- Streamlit: http://localhost:8501
- API Docs: http://localhost:5000/docs

## 🔄 Fluxo de Dados

### Exemplo: Usuário pergunta "Top 10 produtos"

#### Via Frontend React:

```
1. Usuário digita no Chat (React)
   ↓
2. React faz POST /api/chat via Vite proxy
   ↓
3. FastAPI recebe request
   ↓
4. FastAPI inicializa backend (lazy)
   ↓
5. Agent Graph processa query
   ↓
6. Parquet Adapter busca dados
   ↓
7. Code Gen gera código Python
   ↓
8. Executa e retorna resultado
   ↓
9. FastAPI formata response JSON
   ↓
10. React renderiza gráfico/tabela
```

#### Via Streamlit:

```
1. Usuário digita no Chat (Streamlit)
   ↓
2. streamlit_app.py chama query_backend()
   ↓
3. Backend inicializa (cached)
   ↓
4. Agent Graph processa query
   ↓
5. Parquet Adapter busca dados
   ↓
6. Code Gen gera código Python
   ↓
7. Executa e retorna resultado
   ↓
8. Streamlit renderiza gráfico/tabela
```

## 🎯 Quando Usar Cada Interface?

### Frontend React (Recomendado para Produção)

**Use quando:**
- ✅ Precisa de interface profissional
- ✅ Quer múltiplas páginas e funcionalidades
- ✅ Requer customização avançada
- ✅ Deploy em produção
- ✅ Acesso por múltiplos usuários

**Vantagens:**
- Interface moderna e responsiva
- 14 páginas completas
- Performance otimizada
- Fácil manutenção
- SEO friendly

### Streamlit (Recomendado para Desenvolvimento)

**Use quando:**
- ✅ Prototipagem rápida
- ✅ Demos e apresentações
- ✅ Análises exploratórias
- ✅ Desenvolvimento interno
- ✅ Scripts interativos

**Vantagens:**
- Desenvolvimento rápido
- Zero configuração frontend
- Python puro
- Ideal para cientistas de dados

### API FastAPI (Recomendado para Integrações)

**Use quando:**
- ✅ Integrar com outros sistemas
- ✅ Mobile apps
- ✅ Desktop apps
- ✅ Scripts automatizados
- ✅ Webhooks e automações

**Vantagens:**
- RESTful padrão
- Documentação automática
- Type hints (Pydantic)
- Alta performance
- Fácil consumo

## 🔐 Configuração de Ambiente

### Variáveis de Ambiente (`.env`)

```env
# IA
GEMINI_API_KEY=your_key_here

# API
HOST=0.0.0.0
PORT=5000

# Database (opcional)
SQL_SERVER=localhost
SQL_DATABASE=db_name
SQL_USERNAME=user
SQL_PASSWORD=pass

# Logging
LOG_LEVEL=INFO

# CORS (API)
CORS_ORIGINS=["http://localhost:8080", "http://localhost:8501"]
```

## 📊 Comparação das Interfaces

| Característica | React | Streamlit | API |
|----------------|-------|-----------|-----|
| **Complexidade** | Alta | Baixa | Média |
| **Desenvolvimento** | Lento | Rápido | Médio |
| **Performance** | Alta | Média | Alta |
| **Customização** | Total | Limitada | N/A |
| **Deploy** | Médio | Fácil | Fácil |
| **Manutenção** | Média | Fácil | Fácil |
| **Usuários** | Múltiplos | Limitado | Ilimitado |
| **Mobile** | Sim | Não | Sim |
| **SEO** | Sim | Não | N/A |
| **Produção** | ✅ Sim | ⚠️ Não recomendado | ✅ Sim |

## 🎨 Personalização

### Frontend React

```typescript
// frontend/src/index.css
:root {
  --color-primary: #10a37f;  // Alterar cor primária
  --color-secondary: #5436DA;
  // ...
}
```

### Streamlit

```python
# streamlit_app.py
st.markdown("""
<style>
:root {
    --color-primary: #10a37f;
}
</style>
""", unsafe_allow_html=True)
```

### API FastAPI

```python
# api_server.py
app = FastAPI(
    title="Seu Nome Customizado",
    description="Sua descrição",
    version="1.0.0"
)
```

## 🐛 Troubleshooting

### API não inicia?

```bash
# Verificar se porta está em uso
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Linux/Mac

# Alterar porta
export PORT=5001
python api_server.py
```

### Frontend não conecta à API?

```bash
# Verificar proxy em frontend/vite.config.ts
proxy: {
  '/api': {
    target: 'http://localhost:5000',  // Verificar porta
    changeOrigin: true
  }
}
```

### Streamlit erro de módulo?

```bash
# Reinstalar dependências
pip install -r requirements.txt
```

## 📚 Próximos Passos

1. **Escolher Interface Principal**
   - Produção: React
   - Desenvolvimento: Streamlit
   - Integração: API

2. **Testar Funcionalidades**
   - Chat com IA
   - Geração de gráficos
   - Histórico de queries
   - Feedback system

3. **Deploy**
   - Frontend: Vercel/Netlify
   - API: Railway/Render
   - Streamlit: Streamlit Cloud

## 🤝 Contribuindo

Cada interface tem seu próprio guia:

- **React**: Ver `frontend/README_FRONTEND.md`
- **Streamlit**: Ver `streamlit_app.py` (comentários)
- **API**: Ver `api_server.py` (docstrings)

## 📄 Licença

MIT License - Ver `LICENSE`

---

**Versão**: 1.0.0
**Data**: 2025-10-25
**Autor**: Equipe Agent Solution BI

**Status**: ✅ Arquitetura Multi-Interface Implementada
