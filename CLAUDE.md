# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Agent Solution BI - Lojas Caçula** is a conversational Business Intelligence platform that combines a reactive SolidJS frontend with a FastAPI backend, enabling data analysis through natural language queries powered by - **Language Model**: Google Gemini 3.0 Flash (`gemini-3-flash-preview`).

## Quick Start Commands

### Development

```bash
# Start both backend + frontend (Windows)
start.bat

# Or use npm scripts
npm run dev              # Start both backend + frontend
npm run dev:backend      # Backend only (port 8000)
npm run dev:frontend     # Frontend only (port 3000)
npm run clean:ports      # Kill ports 8000 and 3000
```

### Backend-Specific

```bash
# Setup (first time)
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Running
.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Testing
.venv\Scripts\python.exe -m pytest

# Linting & Formatting
.venv\Scripts\python.exe -m ruff check app/
.venv\Scripts\python.exe -m black app/
```

### Frontend-Specific

```bash
cd frontend-solid
pnpm install
pnpm dev          # Dev server
pnpm build        # Production build
pnpm lint         # ESLint check
pnpm lint:fix     # Auto-fix ESLint issues
pnpm test         # Run Vitest tests
pnpm test:ui      # Vitest UI
pnpm test:coverage # Coverage report
```

## Architecture Overview

### Backend (FastAPI + Python 3.11+)

**Entry Point:** `backend/main.py` - FastAPI application with lifespan management, CORS, rate limiting, and structured logging.

**Core Agent System:**
- **LangGraph Orchestration:** Multi-step agent workflows in `backend/app/core/graph/`
- **Gemini Native Function Calling:** Modern agent in `backend/app/core/agents/caculinha_bi_agent.py` replaces legacy keyword-based routing
- **Tool System:** Business intelligence tools in `backend/app/core/tools/`:
  - `une_tools.py` - Core UNE (store) operations
  - `chart_tools.py` - Universal chart generation (`gerar_grafico_universal`)
  - `flexible_query_tool.py` - Generic data queries
  - `sql_server_tools.py` - SQL Server integration
  - `mcp_parquet_tools.py` - Parquet file operations via MCP

**Data Layer:**
- **Hybrid Adapter:** `backend/app/infrastructure/data/hybrid_adapter.py` - Switches between Parquet (primary) and SQL Server (fallback)
- **Parquet Adapter:** `backend/app/infrastructure/data/parquet_adapter.py` - Fast analytics using Polars
- **SQL Server Adapter:** `backend/app/infrastructure/data/sql_server_adapter.py` - ODBC connection to SQL Server
- **Main Dataset:** `backend/data/parquet/admmat.parquet` (1.1M+ records, 97 columns)

**Key Patterns:**
1. **LLM Factory:** `ComponentFactory.get_llm_adapter()` provides Gemini adapter with automatic fallback to DeepSeek
2. **Response Caching:** `ResponseCache` with 6-hour TTL for LLM responses
3. **Lazy Loading:** Heavy imports and configs loaded on-demand
4. **Agent State:** `backend/app/core/agent_state.py` defines state shape (`messages`, `sql_query`, `plotly_spec`, `final_response`)

**API Endpoints:** (`backend/app/api/v1/endpoints/`)
- `chat.py` - Main conversational BI endpoint
- `analytics.py` - Analytics data queries
- `rupturas.py` - Stock rupture analysis
- `transfers.py` - Stock transfer suggestions
- `auth.py` - JWT authentication
- `admin.py` - Admin operations

### Frontend (SolidJS + TailwindCSS)

**Entry Point:** `frontend-solid/src/index.tsx`

**Key Pages:** (`frontend-solid/src/pages/`)
- `Chat.tsx` - Conversational BI interface
- `Dashboard.tsx` - KPI overview
- `Rupturas.tsx` - Stock rupture analysis with drill-down
- `Analytics.tsx` - Advanced analytics charts
- `Transfers.tsx` - Stock transfer recommendations
- `Login.tsx` - Authentication

**Theme:** Lojas Caçula Light Mode
- Primary: `#8B7355` (Marrom Caçula)
- Accent: `#C9A961` (Dourado/Bronze)
- Success: `#2D7A3E` (Verde Oliva)
- Alert: `#B94343` (Vermelho Terroso)
- Background: `#FAFAFA`

**Proxy Setup:** Vite dev server proxies `/api` and `/health` to `http://127.0.0.1:8000`

## Important Architectural Decisions

### Agent System

The system has migrated from legacy keyword-based routing to **Gemini Native Function Calling**:
- **Modern Agent:** `CaculinhaBIAgent` in `backend/app/core/agents/caculinha_bi_agent.py`
- **Tool Selection:** Tools are ordered by specificity (generic first, specific last)
- **Context7 Storytelling:** Agent NEVER reveals internal tools/errors to users
- **Markdown Tables:** When tools return markdown tables, agent must include the entire table in response

### Data Access Pattern

```python
# CORRECT - Use ComponentFactory
from app.core.factory.component_factory import ComponentFactory
llm = ComponentFactory.get_llm_adapter()

# CORRECT - Use data adapters
from app.infrastructure.data.hybrid_adapter import HybridDataAdapter
adapter = HybridDataAdapter()
await adapter.connect()
```

### Chart Generation (Best Practice 2025)

**CRITICAL UPDATE (2025-12-27):** Use the **NEW universal chart tool v2** with dynamic filters:

```python
from app.core.tools.universal_chart_generator import gerar_grafico_universal_v2

# This is the RECOMMENDED chart function (supports UNE, segment, category filters)
gerar_grafico_universal_v2(
    descricao="vendas por segmento",  # What to visualize
    filtro_une=1685,                  # Filter by store
    filtro_segmento="ARMARINHO",      # Filter by segment
    tipo_grafico="auto",              # auto, bar, pie, line
    limite=10                         # Max items
)

# Legacy tool (DEPRECATED - no filter support):
# gerar_grafico_automatico(descricao="...")  # DO NOT USE
```

**Why v2:**
- ✅ Supports dynamic filters (UNE, segment, category)
- ✅ Auto-detects dimension and metric from description
- ✅ No recursive tool calls (faster, no timeout)
- ✅ Context7 compliant (no emoji in logs)

### Error Handling & Fallback

- **LLM Fallback:** `backend/app/core/llm_factory.py` detects rate/quota issues and switches providers
- **Data Fallback:** HybridAdapter switches from Parquet to SQL Server on connection failure
- **Preserve Logging:** All fallback mechanisms use structured logging - maintain this pattern

## Authentication & Security

- **JWT Tokens:** Access token expires in 60 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Segment-Based Access Control:** Users see only data from their permitted segments
- **PII Masking:** CPF, email, phone are masked automatically
- **Secure Code Execution:** AI-generated code runs in controlled environment

**Test Users:**
- `admin` / `admin` - All segments
- `hugo.mendes` / `123456` - ARMARINHO E CONFECÇÃO segment only

## Environment Variables

Create `backend/.env`:

```env
PROJECT_NAME="Agent BI"
API_V1_STR="/api/v1"

# AI
GEMINI_API_KEY="your_api_key_here"
LLM_MODEL_NAME="gemini-3-flash-preview"

# Security
SECRET_KEY="generate_secure_key_here"
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Supabase (optional)
USE_SUPABASE_AUTH=true
SUPABASE_URL="https://xxx.supabase.co"
SUPABASE_ANON_KEY="xxx"
SUPABASE_SERVICE_ROLE_KEY="xxx"
```

## Database Schema

**Main Table:** `admmat.parquet` (1,113,822 records, 97 columns)

**Key Columns:**
- **Identification:** `PRODUTO` (code), `NOME` (name)
- **Location:** `UNE` (store code), `UNE_NOME` (store name)
- **Classification:** `NOMESEGMENTO`, `NOMECATEGORIA`, `NOMEFABRICANTE`
- **Stock:** `ESTOQUE_UNE` (current), `ESTOQUE_LV` (green line), `ESTOQUE_CD` (distribution center)
- **Sales:** `VENDA_30DD` (last 30 days), `ULTIMA_VENDA_DATA_UNE`
- **Prices:** `PRECO_VENDA`, `PRECO_CUSTO`

## Code Style & Conventions

### Backend (Python)
- Follow **PEP8**
- Use `ruff` for linting, `black` for formatting
- Preserve lazy loading patterns for cloud deployment
- Document fallback mechanisms with justification
- Use structured logging (`structlog`)

### Frontend (TypeScript/SolidJS)
- Use ESLint configuration
- Follow reactive SolidJS patterns
- Maintain consistent color theme
- Use TailwindCSS utility classes

## Testing

### Backend
```bash
cd backend
.venv\Scripts\python.exe -m pytest
```

Test files should mock LLM adapters and query engines. Use `backend/data/` for test fixtures.

### Frontend
```bash
cd frontend-solid
pnpm test           # Run tests
pnpm test:ui        # Interactive UI
pnpm test:coverage  # Coverage report
```

## Important Notes

1. **Tool System:** When adding new BI capabilities, create tools in `backend/app/core/tools/` and register them in `CaculinhaBIAgent.bi_tools`

2. **Cache Management:** `ResponseCache` uses 6-hour TTL. When modifying cache logic, document cost/latency impact in `backend/app/core/utils/response_cache.py`

3. **Prompt Engineering:** System prompts are in agent files. When modifying, preserve:
   - Context7 storytelling guidelines
   - Markdown table handling
   - Tool disclosure prevention

4. **Data Templates:** Chart specs and query templates in `backend/data/` feed `plotly_spec` - preserve format when modifying

5. **Frontend State:** Chat sessions stored in `backend/app/data/sessions/` as JSON

6. **Windows-Specific:** This project uses Windows-specific paths (`.venv\Scripts\activate`). Adjust for Linux/Mac if needed.

7. **Port Management:** Backend runs on 8000, frontend on 3000. Use `npm run clean:ports` if ports are busy.

## Common Tasks

### Adding a New Tool
1. Create tool in `backend/app/core/tools/`
2. Define as LangChain `@tool` with proper schema
3. Register in `CaculinhaBIAgent.bi_tools` list
4. Update system prompt examples if needed

### Adding a New Endpoint
1. Create endpoint in `backend/app/api/v1/endpoints/`
2. Add to router in `backend/app/api/v1/router.py`
3. Use dependency injection for data adapter
4. Add rate limiting with `@limiter.limit()`

### Modifying LLM Behavior
1. Edit system prompt in `backend/app/core/agents/caculinha_bi_agent.py`
2. Test with various queries
3. Check logs in `logs/` directory

### Debugging
- Backend logs: `logs/backend.log` or console output
- Frontend: Browser DevTools console
- Structured logs: `agentbi.api`, `agentbi.chat`, `agentbi.security`, `agentbi.audit`

## Deployment Notes

- **Production:** Use Alembic migrations instead of `Base.metadata.create_all()`
- **Environment:** Set `ENVIRONMENT=production` to disable `/docs` and `/redoc`
- **Lazy Loading:** Critical for cloud cold starts - preserve pattern
- **CORS:** Configure `BACKEND_CORS_ORIGINS` for production domains
