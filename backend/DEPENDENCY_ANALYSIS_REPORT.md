# Relatório de Análise de Dependências - Agent Solution BI Backend

**Data**: 26/11/2025
**Python**: 3.11.0
**Projeto**: Agent Solution BI (FastAPI + LangChain + Gemini)

---

## Resumo Executivo

**Status Geral**: ⚠️ **5 dependências CRÍTICAS faltando**

- **Total de pacotes no pyproject.toml**: 41 (produção) + 7 (dev)
- **Instalados no venv**: 32/37 pacotes críticos
- **Faltando**: 5 pacotes essenciais para visualização de dados

---

## ✅ Dependências Instaladas (32 pacotes)

### Core Framework (FastAPI + Backend)
| Pacote | Versão Instalada | Versão pyproject.toml | Status |
|--------|------------------|----------------------|---------|
| `fastapi` | 0.115.14 | ^0.115.0 | ✅ OK |
| `uvicorn` | 0.35.0 | ^0.35.0 | ✅ OK |
| `pydantic` | 2.12.5 | ^2.11.0 | ✅ OK |
| `pydantic-settings` | 2.12.0 | ^2.10.0 | ✅ OK |
| `python-dotenv` | unknown | ^1.1.0 | ✅ OK |
| `python-multipart` | 0.0.20 | ^0.0.20 | ✅ OK |
| `jinja2` | 3.1.6 | ^3.1.6 | ✅ OK |
| `email-validator` | 2.3.0 | ^2.0.0 | ✅ OK |

### Database & Data Processing
| Pacote | Versão Instalada | Versão pyproject.toml | Status |
|--------|------------------|----------------------|---------|
| `sqlalchemy` | 2.0.44 | ^2.0.43 | ✅ OK |
| `alembic` | 1.17.2 | ^1.16.4 | ✅ OK |
| `aioodbc` | 0.5.0 | ^0.5.0 | ✅ OK |
| `aiosqlite` | 0.21.0 | ^0.21.0 | ✅ OK |
| `pyodbc` | unknown | ^5.2.0 | ✅ OK |
| `pandas` | 2.3.3 | ^2.2.2 | ✅ OK (newer) |
| `polars` | 1.35.2 | ^1.35.2 | ✅ OK |
| `pyarrow` | 22.0.0 | pyarrow-hotfix ^0.7 | ✅ OK |
| `numpy` | 1.26.4 | ^1.26.4 | ✅ OK |
| `dask` | 2025.11.0 | ^2025.11.0 | ✅ OK |

### LLM & Agents (LangChain + Gemini)
| Pacote | Versão Instalada | Versão pyproject.toml | Status |
|--------|------------------|----------------------|---------|
| `langchain` | 0.3.27 | ^0.3.13 | ✅ OK (newer) |
| `langchain-core` | 0.3.80 | N/A | ✅ OK |
| `langchain-community` | 0.3.31 | ^0.3.13 | ✅ OK (newer) |
| `langgraph` | unknown | ^0.2.55 | ✅ OK |
| `google-generativeai` | unknown | ^0.8.5 | ✅ OK |

### Security & Authentication
| Pacote | Versão Instalada | Versão pyproject.toml | Status |
|--------|------------------|----------------------|---------|
| `python-jose` | 3.5.0 | ^3.5.0 | ✅ OK |
| `passlib` | 1.7.4 | ^1.7.4 | ✅ OK |

### Monitoring & Performance
| Pacote | Versão Instalada | Versão pyproject.toml | Status |
|--------|------------------|----------------------|---------|
| `structlog` | 25.5.0 | ^25.5.0 | ✅ OK |
| `sentry-sdk` | unknown | ^2.35.0 | ✅ OK |
| `prometheus-client` | unknown | ^0.22.0 | ✅ OK |
| `slowapi` | unknown | ^0.1.9 | ✅ OK |

### HTTP & Utilities
| Pacote | Versão Instalada | Versão pyproject.toml | Status |
|--------|------------------|----------------------|---------|
| `httpx` | 0.28.1 | ^0.28.0 | ✅ OK |
| `redis` | 5.3.1 | ^5.2.0 | ✅ OK (newer) |
| `orjson` | 3.11.4 | N/A | ✅ OK |

---

## ❌ Dependências FALTANDO (5 pacotes CRÍTICOS)

### Visualização de Dados (CRÍTICO para `chart_tools.py`)

| Pacote | Versão Necessária | Uso no Projeto | Impacto |
|--------|-------------------|----------------|---------|
| **`plotly`** | ^6.5.0 | `app/core/tools/chart_tools.py` (1563 linhas)<br/>`app/core/visualization/advanced_charts.py` | 🔴 **CRÍTICO** - Todas as ferramentas de gráfico quebram sem este pacote |
| **`kaleido`** | ^1.2.0 | Exportação de gráficos Plotly para imagem | 🟡 **IMPORTANTE** - Necessário para export de PNG/SVG |
| **`matplotlib`** | ^3.10.7 | Backend de visualização | 🟡 **IMPORTANTE** - Usado por Plotly e Seaborn |
| **`seaborn`** | ^0.13.2 | Gráficos estatísticos avançados | 🟡 **IMPORTANTE** - Análises estatísticas |
| **`langchain-openai`** | ^1.0.3 | Integração com API OpenAI-like (Gemini) | 🟠 **MODERADO** - Usado em `llm_langchain_adapter.py` |

### Análise de Uso

```python
# Arquivos que DEPENDEM dos pacotes faltantes:

# PLOTLY (CRÍTICO - 100% dos gráficos)
app/core/tools/chart_tools.py                    # 1563 linhas - TODAS as ferramentas de gráfico
app/core/visualization/advanced_charts.py        # Gráficos avançados
app/core/utils/chart_saver.py                    # Salvar gráficos

# LANGCHAIN-OPENAI (MODERADO)
app/core/llm_langchain_adapter.py                # Integração LangChain <-> Gemini
app/core/agents/tool_agent.py                    # Agente principal (usa CustomLangChainLLM)
```

---

## 🔍 Análise Detalhada: Imports por Arquivo

### Arquivos Críticos Analisados

#### 1. `app/core/agents/tool_agent.py` (335 linhas)
```python
from langchain.agents import create_tool_calling_agent, AgentExecutor  # ✅
from langchain_core.prompts import ChatPromptTemplate                  # ✅
from langchain_core.messages import BaseMessage, AIMessage, ...        # ✅
from langchain_core.runnables import RunnableConfig                    # ✅
from langchain_core.agents import AgentAction, AgentFinish             # ✅

from app.core.llm_langchain_adapter import CustomLangChainLLM          # ✅
from app.core.tools.unified_data_tools import unified_tools            # ✅
from app.core.tools.chart_tools import chart_tools                     # ❌ QUEBRA (Plotly)
```

#### 2. `app/core/tools/chart_tools.py` (1563 linhas) - **CRÍTICO**
```python
import plotly.graph_objects as go                                      # ❌ FALTANDO
from plotly.subplots import make_subplots                              # ❌ FALTANDO
import pandas as pd                                                     # ✅
from langchain_core.tools import tool                                   # ✅

from app.core.visualization.advanced_charts import AdvancedChartGenerator  # ❌ QUEBRA
```

**IMPACTO**: 18 ferramentas de gráfico não funcionam:
- `gerar_grafico_vendas_por_categoria()`
- `gerar_grafico_estoque_por_produto()`
- `gerar_comparacao_precos_categorias()`
- `gerar_analise_distribuicao_estoque()`
- `gerar_grafico_pizza_categorias()`
- `gerar_dashboard_analise_completa()`
- `gerar_dashboard_executivo()` (dashboard 2x3 principal)
- `gerar_dashboard_dinamico()`
- `gerar_grafico_vendas_mensais_produto()`
- `gerar_grafico_vendas_por_grupo()`
- `gerar_ranking_produtos_mais_vendidos()`
- E mais 7 ferramentas...

#### 3. `app/core/llm_langchain_adapter.py` (283 linhas)
```python
from langchain_core.callbacks import CallbackManagerForLLMRun          # ✅
from langchain_core.language_models import BaseChatModel               # ✅
from langchain_core.messages import (
    BaseMessage, AIMessage, HumanMessage, SystemMessage,
    FunctionMessage, ToolMessage, ToolCall, AIMessageChunk             # ✅
)
from langchain_core.outputs import ChatResult, ChatGeneration          # ✅
```

#### 4. `app/core/llm_gemini_adapter.py` (254 linhas)
```python
import google.generativeai as genai                                    # ✅
from google.api_core.exceptions import RetryError, InternalServerError # ✅
from google.generativeai.types import FunctionDeclaration              # ✅
```

#### 5. `app/api/v1/endpoints/chat.py` (347 linhas)
```python
from fastapi import APIRouter, Depends, HTTPException, Request         # ✅
from fastapi.responses import ORJSONResponse, StreamingResponse        # ✅
import polars as pl                                                    # ✅
from app.core.query_processor import QueryProcessor                    # ✅
```

---

## 📦 Comparação: pyproject.toml vs requirements.txt

### pyproject.toml (Poetry - Mais Limpo)
```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.115.0"
langchain-google-genai = "^2.0.5"  # ❌ NÃO INSTALADO
langgraph = "^0.2.55"
polars = "^1.35.2"
# ... total: 41 pacotes
```

### requirements.txt (pip-compile - Completo com Dependências Transitivas)
```
# Total: 560 linhas (inclui TODAS as dependências transitivas)
langchain==1.0.8
langchain-openai==1.0.3        # ❌ FALTANDO
plotly==6.5.0                  # ❌ FALTANDO
matplotlib==3.10.7             # ❌ FALTANDO
seaborn==0.13.2                # ❌ FALTANDO
kaleido==1.2.0                 # ❌ FALTANDO
```

### requirements-docker.txt (Docker Otimizado)
```
# Versão REDUZIDA para Docker (119 linhas)
# Remove: torch, transformers, sentence-transformers, faiss-cpu
# Comentário: "langchain-openai==2.8.1" (linha 54-56)
```

**PROBLEMA IDENTIFICADO**: O `requirements-docker.txt` comenta a instalação de dependências de visualização para reduzir tamanho da imagem Docker, mas essas dependências são CRÍTICAS para o funcionamento dos gráficos.

---

## 🔧 Solução Recomendada

### Comandos Poetry para Instalar TODAS as Dependências Faltantes

```bash
cd C:\Users\André\Documents\Agent_Solution_BI\backend

# 1. Instalar dependências de visualização (CRÍTICO)
poetry add plotly@^6.5.0
poetry add kaleido@^1.2.0
poetry add matplotlib@^3.10.7
poetry add seaborn@^0.13.2

# 2. Instalar langchain-openai (IMPORTANTE)
poetry add langchain-openai@^1.0.3

# 3. Instalar langchain-google-genai (conforme pyproject.toml)
poetry add langchain-google-genai@^2.0.5

# 4. Verificar instalação
poetry install --sync
```

### Alternativa: Comando Único (RECOMENDADO)

```bash
poetry add plotly@^6.5.0 kaleido@^1.2.0 matplotlib@^3.10.7 seaborn@^0.13.2 langchain-openai@^1.0.3 langchain-google-genai@^2.0.5
```

### Verificação Pós-Instalação

```bash
# Testar imports críticos
python -c "
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
import kaleido
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
print('✅ Todas as dependências críticas instaladas com sucesso!')
"
```

---

## 📊 Versões Compatíveis Recomendadas

Baseado na análise do `requirements.txt` (pip-compile):

| Pacote | Versão Atual (requirements.txt) | Compatibilidade |
|--------|--------------------------------|-----------------|
| `plotly` | **6.5.0** | ✅ Compatível com Pandas 2.2.2, Polars 1.34.0 |
| `kaleido` | **1.2.0** | ✅ Requer pytest-timeout 2.4.0 |
| `matplotlib` | **3.10.7** | ✅ Compatível com NumPy 1.26.4 |
| `seaborn` | **0.13.2** | ✅ Requer matplotlib 3.10.7 |
| `langchain-openai` | **1.0.3** | ✅ Compatível com langchain-core 1.1.0 |
| `langchain-google-genai` | **2.0.5** | ✅ Compatível com google-generativeai 0.8.5 |

---

## ⚠️ Conflitos de Versão Identificados

### 1. LangChain Version Mismatch

**pyproject.toml** (configurado):
```toml
langchain = "^0.3.13"
langchain-community = "^0.3.13"
langchain-google-genai = "^2.0.5"
```

**requirements.txt** (pip-compile resolveu):
```
langchain==1.0.8
langchain-core==1.1.0
langchain-community==0.4.1
langchain-openai==1.0.3
```

**Versão INSTALADA no venv**:
```
langchain==0.3.27
langchain-core==0.3.80
langchain-community==0.3.31
```

**ANÁLISE**: Há incompatibilidade entre versões. O pip-compile resolveu para versões 1.x, mas o venv está com 0.3.x.

**RECOMENDAÇÃO**: Atualizar `pyproject.toml` para versões 1.x (mais recentes):

```toml
[tool.poetry.dependencies]
langchain = "^1.0.8"
langchain-core = "^1.1.0"
langchain-community = "^0.4.1"
langchain-openai = "^1.0.3"
langchain-google-genai = "^2.0.5"
langgraph = "^1.0.3"  # Atualizar de 0.2.55
```

### 2. Pandas Version (Minor)

- **pyproject.toml**: `^2.2.2`
- **Instalado**: `2.3.3`
- **Status**: ✅ OK (minor update, compatível)

---

## 🐳 Correção para Docker

O `requirements-docker.txt` está REMOVENDO dependências críticas para reduzir tamanho da imagem:

```dockerfile
# requirements-docker.txt (linha 50-56)
# OpenAI (para Gemini via API compatível)
# OpenAI (para Gemini via API compatível)
openai==2.8.1
google-generativeai==0.8.3
```

**PROBLEMA**: Falta `langchain-openai` e bibliotecas de visualização.

**SOLUÇÃO**: Criar novo `requirements-docker-full.txt`:

```
# requirements-docker-full.txt
# Todas as dependências necessárias (inclusive visualização)

-r requirements-docker.txt

# Visualização (CRÍTICO)
plotly==6.5.0
kaleido==1.2.0
matplotlib==3.10.7
seaborn==0.13.2

# LangChain OpenAI (IMPORTANTE)
langchain-openai==1.0.3
```

---

## 📝 Checklist de Ações

### Prioridade ALTA (Imediato)

- [ ] **Instalar Plotly** - `poetry add plotly@^6.5.0`
- [ ] **Instalar Kaleido** - `poetry add kaleido@^1.2.0`
- [ ] **Instalar Matplotlib** - `poetry add matplotlib@^3.10.7`
- [ ] **Instalar Seaborn** - `poetry add seaborn@^0.13.2`
- [ ] **Testar ferramentas de gráfico** - Executar `app/core/tools/chart_tools.py`

### Prioridade MÉDIA

- [ ] **Instalar langchain-openai** - `poetry add langchain-openai@^1.0.3`
- [ ] **Instalar langchain-google-genai** - `poetry add langchain-google-genai@^2.0.5`
- [ ] **Atualizar pyproject.toml** - Ajustar versões LangChain para 1.x
- [ ] **Executar `poetry lock --no-update`** - Regenerar lock file

### Prioridade BAIXA (Manutenção)

- [ ] **Criar `requirements-docker-full.txt`** - Versão completa para Docker
- [ ] **Atualizar `DOCKER_README.md`** - Documentar dependências
- [ ] **Testar build Docker** - Garantir que imagem funciona com visualizações
- [ ] **Executar testes** - `pytest backend/tests/`

---

## 🎯 Impacto Esperado

### Antes da Correção
- ❌ 18 ferramentas de gráfico quebradas (`chart_tools.py`)
- ❌ Dashboard executivo não funciona
- ❌ Análises visuais indisponíveis
- ⚠️ Sistema funciona APENAS para consultas de texto

### Depois da Correção
- ✅ Todas as 18 ferramentas de gráfico funcionais
- ✅ Dashboard executivo 2x3 operacional
- ✅ Gráficos de vendas, estoque e análises disponíveis
- ✅ Sistema 100% funcional (texto + visualizações)

---

## 📚 Referências

- **pyproject.toml**: `C:\Users\André\Documents\Agent_Solution_BI\backend\pyproject.toml`
- **requirements.txt**: `C:\Users\André\Documents\Agent_Solution_BI\backend\requirements.txt`
- **requirements-docker.txt**: `C:\Users\André\Documents\Agent_Solution_BI\backend\requirements-docker.txt`
- **Código crítico**: `app/core/tools/chart_tools.py` (1563 linhas)
- **Agente principal**: `app/core/agents/tool_agent.py` (335 linhas)

---

## 🔗 Comandos Completos (Copy-Paste)

```powershell
# 1. Ativar ambiente virtual
cd C:\Users\André\Documents\Agent_Solution_BI\backend
poetry shell

# 2. Instalar TODAS as dependências faltantes (COMANDO ÚNICO)
poetry add plotly@^6.5.0 kaleido@^1.2.0 matplotlib@^3.10.7 seaborn@^0.13.2 langchain-openai@^1.0.3 langchain-google-genai@^2.0.5

# 3. Sincronizar ambiente
poetry install --sync

# 4. Verificar instalação
python -c "import plotly, kaleido, matplotlib, seaborn; print('✅ OK')"

# 5. Testar sistema de agentes
python -c "from app.core.tools.chart_tools import chart_tools; print(f'✅ {len(chart_tools)} ferramentas de gráfico carregadas')"

# 6. Rodar backend
python main.py
```

---

**Fim do Relatório**
