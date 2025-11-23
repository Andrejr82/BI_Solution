# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agent Solution BI is a conversational Business Intelligence platform with a modern React frontend and FastAPI backend sharing a unified Python core. The system uses LangGraph for AI workflow orchestration and supports multiple data sources (Parquet, SQL Server) with intelligent fallback.

## Architecture

### Architecture Design
- **Frontend React** (`frontend-react/`): Next.js 16 production UI at port 3000
- **Backend FastAPI** (`backend/`): Modern async API at port 8000
- **Core Backend** (`core/`): Shared business logic and LangGraph agents

The React frontend communicates with the FastAPI backend, which consumes the `core/` modules for AI/BI processing.

### Core Components Architecture
```
core/
├── agents/               # LangGraph agent nodes and workflows
│   ├── bi_agent_nodes.py         # BI query processing nodes
│   ├── caculinha_bi_agent.py     # Main BI agent orchestrator
│   └── conversational_reasoning_node.py  # v3.0 extended thinking
├── connectivity/         # Data adapters with fallback system
│   ├── hybrid_adapter.py         # Auto-fallback: Parquet → SQL Server
│   ├── parquet_adapter.py        # Primary Parquet/Polars adapter
│   └── sql_server_adapter.py     # Fallback SQL Server adapter
├── graph/               # LangGraph workflow builders
│   ├── agent.py                  # Graph construction
│   └── graph_builder.py          # Node orchestration
├── business_intelligence/  # BI-specific logic
│   ├── intent_classifier.py      # Query intent classification
│   └── generic_query_executor.py # Query execution engine
├── factory/             # Dependency injection and factories
├── config/              # Settings and configuration
└── utils/               # Cache, logging, helpers
```

### State Management
The system uses `AgentState` (TypedDict) in `core/agent_state.py` for LangGraph workflows:
- `messages`: LangChain message history
- `sql_query`: Generated SQL/Parquet queries
- `plotly_spec`/`plotly_fig`: Visualization specs
- `retrieved_data`: Query results
- `final_response`: Formatted user response
- `reasoning_mode`: "conversational" or "analytical" (v3.0)

## Development Commands

### Python Backend

**Environment Setup:**
```bash
# Create virtual environment (Windows)
python -m venv .venv_new
.venv_new\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Running Services:**
```bash
# FastAPI Backend
cd backend
python main.py
# or
uvicorn main:app --reload --port 8000
# → http://localhost:8000/docs (Swagger UI)

# Both backend entry points exist:
# - backend/main.py (modern FastAPI with async, lifespan, rate limiting)
# - scripts/caculinha_backend.py (legacy compatibility, simpler)
```

**Testing:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov-report=html

# Run specific test file
pytest tests/test_quick_wins_simple.py

# Verbose logging (configured in pytest.ini)
pytest -v --log-cli-level=INFO
```

### React Frontend

**Setup:**
```bash
cd frontend-react
npm install
# or
pnpm install
```

**Development:**
```bash
# Development server
npm run dev
# → http://localhost:3000

# Build for production
npm run build

# Start production server
npm run start

# Linting
npm run lint

# Testing
npm run test              # Run tests
npm run test:watch        # Watch mode
npm run test:coverage     # Coverage report
npm run test:ci           # CI mode with coverage
```

## Critical Patterns

### 1. LLM Adapter Factory Pattern
**Always use `ComponentFactory` to acquire LLM adapters. Never instantiate directly.**

```python
from core.factory.component_factory import ComponentFactory

# ✅ Correct
llm_adapter = ComponentFactory.get_llm_adapter()

# ❌ Wrong - bypasses fallback logic
from core.llm_adapter import LLMAdapter
adapter = LLMAdapter()
```

**Why:** `ComponentFactory` implements automatic fallback (Gemini → DeepSeek), rate limiting detection, and quota management via `ComponentFactory.set_gemini_unavailable(True)`.

See: `core/llm_adapter.py` for fallback implementation.

### 2. Data Adapter Pattern
Use `HybridDataAdapter` for automatic Parquet → SQL Server fallback:

```python
from core.connectivity.hybrid_adapter import HybridDataAdapter

adapter = HybridDataAdapter()
await adapter.connect()
result = await adapter.query("SELECT * FROM vendas")
# Automatically falls back to SQL Server if Parquet fails
```

Location: `core/connectivity/hybrid_adapter.py`

### 3. Response Caching
Cache is persistent with 6-hour TTL. Preserve `cache_context` parameter:

```python
from core.utils.response_cache import ResponseCache

cache = ResponseCache()
cached = cache.get(prompt, cache_context="parquet")
if not cached:
    result = expensive_operation()
    cache.set(prompt, result, cache_context="parquet")
```

Cache files: `data/cache/`

### 4. Lazy Loading
Heavy imports and configurations load on-demand. Maintain this pattern to reduce startup time (critical for cloud deployments):

```python
# ✅ Good - lazy import
def generate_chart():
    import plotly.graph_objects as go  # Import only when needed
    return go.Figure(...)

# ❌ Bad - eager import at module level
import plotly.graph_objects as go  # Slows down ALL imports
```

### 5. LangGraph Node Structure
Nodes follow this signature:

```python
from core.agent_state import AgentState

def my_node(state: AgentState) -> AgentState:
    """
    Node must accept AgentState and return modified AgentState.
    Use state.get() for optional fields.
    """
    messages = state["messages"]
    # Process...
    return {
        **state,
        "final_response": {"text": "...", "plotly_spec": {...}}
    }
```

Example nodes: `core/agents/bi_agent_nodes.py`

## Data Flow

### Query Processing Pipeline
1. User input → `intent_classifier.py` (classify query type)
2. Intent → LangGraph workflow (`core/graph/agent.py`)
3. Nodes execute sequentially:
   - `generate_parquet_query` → SQL/filter generation
   - `execute_query` → Data retrieval via adapters
   - `generate_plotly_spec` → Visualization spec
   - Format final response
4. Response → Frontend (React via FastAPI)

### Data Sources
- **Primary**: Parquet files in `data/*.parquet` (read via Polars/Dask)
- **Fallback**: SQL Server (configured in `.env`)
- **Cache**: `data/cache/*.json` (6-hour TTL)
- **History**: `data/query_history/*.json` (daily files)

## Configuration

### Environment Variables (`.env`)
```env
# LLM Configuration
GEMINI_API_KEY=<your-key>          # Primary LLM
DEEPSEEK_API_KEY=<backup-key>      # Fallback LLM

# Database (optional)
SQL_SERVER=localhost
SQL_DATABASE=db_name
SQL_USERNAME=user
SQL_PASSWORD=pass

# API Settings
PORT=5000
HOST=0.0.0.0

# Cache
CACHE_AUTO_CLEAN=True
CACHE_MAX_AGE_DAYS=7
```

### Backend Settings
Backend uses Pydantic settings (`backend/app/config/settings.py`):
- `ENVIRONMENT`: development/production
- `DEBUG`: Enable/disable debug mode
- `LOG_LEVEL`: INFO/DEBUG/WARNING
- `BACKEND_CORS_ORIGINS`: CORS configuration

## Testing Patterns

### Unit Tests
```python
import pytest
from core.connectivity.parquet_adapter import ParquetAdapter

@pytest.mark.asyncio
async def test_parquet_query():
    adapter = ParquetAdapter()
    result = await adapter.query("SELECT * FROM vendas LIMIT 10")
    assert len(result) > 0
```

### Mocking LLM Calls
```python
from unittest.mock import Mock, patch

@patch('core.llm_adapter.LLMAdapter.generate')
def test_with_mock_llm(mock_generate):
    mock_generate.return_value = "Mocked response"
    # Test code...
```

### Test Data
Use fixtures in `data/` for reproducible tests. Parquet files are committed to repo.

## Common Tasks

### Adding a New LangGraph Node
1. Define node function in `core/agents/bi_agent_nodes.py` or new file
2. Accept/return `AgentState` TypedDict
3. Register in `core/graph/graph_builder.py`
4. Add unit tests

### Adding a New API Endpoint
1. Create endpoint in `backend/app/api/v1/endpoints/`
2. Import in `backend/app/api/v1/router.py`
3. Use dependency injection for `data_adapter` via `app.state`
4. Add rate limiting with `@limiter.limit("10/minute")`

### Modifying Prompt Templates
Templates are in:
- Python code: `core/agents/prompt_loader.py`
- JSON examples: `data/query_examples.json`
- Preserve format that generates valid `plotly_spec` JSON

### Cache Management
```bash
# Manual cache cleanup:
python -c "from core.utils.cache_cleaner import run_cache_cleanup; run_cache_cleanup()"
```

## Error Handling

### LLM Fallback
When Gemini fails (rate limit/quota):
- System auto-detects via exception handling in `core/llm_adapter.py`
- Sets `ComponentFactory.set_gemini_unavailable(True)`
- Subsequent calls use DeepSeek automatically
- Logs fallback event to `logs/`

### Data Adapter Fallback
When Parquet fails:
- `HybridDataAdapter` catches exception
- Switches `current_source = "sql_server"`
- Retries query on SQL Server
- Logs fallback to `logs/`

## Troubleshooting

### "Module not found" errors
Ensure project root is in PYTHONPATH:
```python
import sys
sys.path.insert(0, str(Path(__file__).parent))
```

### LLM quota exceeded
Check `logs/` for fallback events. System auto-switches to DeepSeek.

### Frontend build errors
```bash
cd frontend-react
rm -rf node_modules .next
pnpm install
pnpm run build
```

## Documentation References

Key documentation files in `docs/`:
- `MIGRATION_PLAN.md` - FastAPI + React architecture guide
- `INTEGRATION_SETUP.md` - Frontend-Backend integration guide
- `README.md` - Comprehensive project overview (Portuguese)
- `FASE_1_COMPLETA.md` / `FASE_2_COMPLETA.md` - Implementation phases

## Code Style

- Follow PEP 8 for Python
- Use `ruff` and `black` for formatting (configured in CI)
- TypeScript/React: ESLint + Prettier (configured in `frontend-react/`)
- Add type hints to all Python function signatures
- Document complex business logic with inline comments

## Git Workflow

Recent commits show:
- Main branch: `main`
- Feature branches: Use descriptive names
- Commits: Descriptive messages (see git log for style)
- Pre-commit hooks: Not configured (consider adding)

## Windows-Specific Notes

- Use `.venv_new\Scripts\activate` (not `source venv/bin/activate`)
- Batch scripts in `scripts/`: `RUN.bat`, `git_push_to_bi_solution.bat`
- Path separators: Use `Path` from pathlib for cross-platform compatibility

## Performance Considerations

1. **Backend startup**: Optimizations applied
   - Lazy imports for heavy libraries (Plotly, transformers)
   - Async initialization for FastAPI lifespan

2. **Query performance**:
   - Parquet + Polars is faster than SQL for analytical queries
   - Use `HybridDataAdapter` for automatic optimization

3. **LLM latency**:
   - Response cache reduces 90%+ of repeat queries to <100ms
   - Extended thinking mode (v3.0) adds latency for complex reasoning

## Security Notes

- PII masking: Use `core.security.mask_pii()` for logs
- Authentication: JWT tokens in `backend/app/config/security.py`
- Rate limiting: Configured via SlowAPI in `backend/main.py`
- SQL injection: Parameterized queries only (enforced by adapters)

## Version Information

- Python: 3.11+
- Node.js: 20+ (for React frontend)
- Key frameworks:
  - FastAPI 0.116+
  - LangChain 0.3.27
  - LangGraph 0.6.4
  - Next.js 16.0.3
  - React 19.2.0

Last updated: 2025-11-23
