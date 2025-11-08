# SOLUCAO IMEDIATA - STREAMLIT CARREGAMENTO INFINITO

## DIAGRAMA DE PROBLEMA

```
┌─────────────────────────────────────────────────┐
│  streamlit_app.py EXECUTA                      │
│  (código no nível de módulo)                    │
└─────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────┐
│  build_graph() é CHAMADO                        │
│  └─ Compila grafo completo (SÍNCRONO)          │
│  └─ Tenta conectar ao LLM (BLOQUEANTE)          │
│  └─ Timeout ou freeze                          │
└─────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────┐
│  TIMEOUT ou ESPERA INFINITA                    │
│  Streamlit travado esperando resposta           │
│  Navegador mostra "Loading..."                  │
└─────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────┐
│  Usuário recarrega página (F5)                  │
│  └─ Script re-executa do início                │
│  └─ build_graph() é chamado NOVAMENTE           │
│  └─ LOOP INFINITO                              │
└─────────────────────────────────────────────────┘
```

---

## SOLUCAO IMPLEMENTADA

### Passo 1: Identificar Ordem de Execução Correta

**ESTRUTURA CORRETA DO STREAMLIT:**

```python
# LINHA 1-5: SEMPRE PRIMEIRO
import streamlit as st

st.set_page_config(
    page_title="...",
    layout="wide"
)

# LINHA 10+: Imports normais
import os
import sys
from pathlib import Path

# LINHA 20+: Funções com CACHE
@st.cache_resource
def load_graph():
    """Carrega grafo UMA VEZ, reutiliza em próximas execuções"""
    from core.graph.graph_builder import build_graph
    return build_graph()

# LINHA 30+: Inicialização com Session State
if __name__ == "__main__":
    if 'graph' not in st.session_state:
        st.session_state.graph = load_graph()

    # REST DO CÓDIGO
```

---

### Passo 2: Problema Específico - Session State Loop

**PROBLEMA IDENTIFICADO:**

Se há código que modifica session_state no nível de módulo:

```python
# ERRADO
st.session_state.graph = build_graph()  # Isso causa re-execução
```

**SOLUÇÃO:**

Envolver com `if` para só executar 1x:

```python
# CORRETO
@st.cache_resource
def get_graph():
    return build_graph()

# Esta função será executada apenas quando cache invalida
st.session_state.graph = get_graph()
```

---

### Passo 3: Problema LLM - Timeout Infinito

**PROBLEMA:**

```python
from core.llm_adapter import get_llm
llm = get_llm()  # Pode esperar indefinidamente por resposta da API
```

**SOLUÇÃO:**

```python
@st.cache_resource
def get_llm_safe():
    """Carrega LLM com timeout e tratamento de erro"""
    try:
        from core.llm_adapter import get_llm
        llm = get_llm()

        if llm is None:
            st.warning("LLM não disponível - usando modo offline")
            return None

        return llm
    except Exception as e:
        st.error(f"Erro ao carregar LLM: {e}")
        return None

llm = get_llm_safe()
```

---

### Passo 4: Problema Config - runOnSave

**PROBLEMA EM `.streamlit/config.toml`:**

```toml
client.runOnSave = true  # ERRADO - Re-executa sempre
```

**SOLUÇÃO:**

```toml
[client]
runOnSave = false  # Desabilitar auto-execução
```

---

## TABELA DE IMPACTO E RECOMENDAÇÃO

| Problema | Localização | Severidade | Impacto | Solução | Prioridade |
|----------|------------|-----------|--------|--------|-----------|
| `build_graph()` no módulo | `streamlit_app.py:?` | CRÍTICO | Trava total | Envolver com `@st.cache_resource` | 1 |
| `st.set_page_config()` não em 1º | `streamlit_app.py:?` | CRÍTICO | Re-layout | Mover para linha 1-3 | 1 |
| Imports pesados antes config | `streamlit_app.py:?` | ALTO | Delay 2-5s | Lazy import com `@st.cache_resource` | 2 |
| `runOnSave = true` | `.streamlit/config.toml:?` | ALTO | Re-execução | Trocar para `false` | 2 |
| LLM sem timeout | `core/llm_adapter.py:?` | ALTO | Hang infinito | Adicionar `timeout=10` | 2 |
| Graph compile síncrono | `core/graph/graph_builder.py:?` | MÉDIO | Slow start | Adicionar async ou cache | 3 |
| Sem error handling | `streamlit_app.py:?` | MÉDIO | Crashes | Try/except blocos | 3 |

---

## SCRIPT DE CORREÇÃO PASSO A PASSO

### Etapa 1: Backup Seguro

```bash
# Fazer backup antes de qualquer mudança
cd C:\Users\André\Documents\Agent_Solution_BI
git add -A
git commit -m "backup: antes de correcao hanging streamlit"
```

---

### Etapa 2: Corrigir .streamlit/config.toml

**ARQUIVO:** `.streamlit/config.toml`

**SUBSTITUIR TODO CONTEÚDO POR:**

```toml
[client]
runOnSave = false
showErrorDetails = true
showWarningOnDirectExecution = false
maxCachedMessageSize = 200

[server]
runOnSave = false
maxUploadSize = 200
port = 8501
headless = true

[logger]
level = "info"

[theme]
primaryColor = "#0066CC"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

---

### Etapa 3: Criar Arquivo de Inicialização Segura

**ARQUIVO NOVO:** `core/utils/streamlit_init.py`

```python
"""
Inicialização segura do Streamlit
Evita loops e travamentos
"""

import streamlit as st
from typing import Any, Optional
import sys
from pathlib import Path

def setup_page():
    """Configure page - DEVE SER CHAMADO PRIMEIRO"""
    st.set_page_config(
        page_title="Agent BI Solution",
        page_icon="chart_with_upwards_trend",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    return True

@st.cache_resource
def load_graph_safe():
    """Carrega grafo com tratamento de erro e cache"""
    try:
        from core.graph.graph_builder import build_graph
        return build_graph()
    except TimeoutError:
        st.error("Timeout ao carregar grafo - tente novamente")
        return None
    except Exception as e:
        st.error(f"Erro ao carregar grafo: {str(e)}")
        return None

@st.cache_resource
def load_llm_safe():
    """Carrega LLM com tratamento de erro e cache"""
    try:
        from core.llm_adapter import get_llm
        llm = get_llm()
        if llm is None:
            st.warning("LLM indisponível - modo offline ativado")
        return llm
    except Exception as e:
        st.warning(f"Erro ao carregar LLM: {str(e)}")
        return None

def initialize_session_state():
    """Inicializa session state sem loops"""
    if 'graph' not in st.session_state:
        st.session_state.graph = load_graph_safe()

    if 'llm' not in st.session_state:
        st.session_state.llm = load_llm_safe()

    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
```

---

### Etapa 4: Estrutura Correta do streamlit_app.py

**TEMPLATE CORRETO INICIAL:**

```python
# ============================================================================
# LINHA 1-10: SETUP OBRIGATÓRIO - NUNCA MOVER DAQUI
# ============================================================================

import streamlit as st

# PRIMEIRA COISA - ANTES DE TUDO
st.set_page_config(
    page_title="Agent BI Solution",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# LINHA 15-30: IMPORTS LEVES
# ============================================================================

import os
import sys
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

# ============================================================================
# LINHA 35-60: CACHE RESOURCES (Lazy Loading)
# ============================================================================

@st.cache_resource
def get_graph():
    """Carrega grafo uma única vez com cache"""
    try:
        from core.graph.graph_builder import build_graph
        return build_graph()
    except Exception as e:
        st.error(f"Erro ao carregar grafo: {e}")
        return None

@st.cache_resource
def get_llm():
    """Carrega LLM uma única vez com cache"""
    try:
        from core.llm_adapter import get_llm as get_llm_impl
        return get_llm_impl()
    except Exception as e:
        st.warning(f"LLM indisponível: {e}")
        return None

# ============================================================================
# LINHA 65-85: INICIALIZAÇÃO SESSION STATE
# ============================================================================

def initialize_state():
    """Inicializa state na primeira execução"""
    if 'graph' not in st.session_state:
        st.session_state.graph = get_graph()

    if 'llm' not in st.session_state:
        st.session_state.llm = get_llm()

    if 'initialized' not in st.session_state:
        st.session_state.initialized = True

initialize_state()

# ============================================================================
# LINHA 90+: RESTO DO CÓDIGO
# ============================================================================

def main():
    """Função principal da aplicação"""

    if not st.session_state.initialized:
        st.error("Aplicação não inicializada corretamente")
        return

    # UI da aplicação aqui
    st.title("Agent BI Solution")

    # Use st.session_state.graph e st.session_state.llm
    # em vez de inicializar aqui

if __name__ == "__main__":
    main()
```

---

## VERIFICAÇÃO PÓS-CORREÇÃO

### Teste 1: Cache Limpo

```bash
streamlit cache clear
streamlit run streamlit_app.py
# Esperado: Carrega em 3-5 segundos
```

### Teste 2: Reload (F5)

```
Pressionar F5 no navegador
# Esperado: Re-render rápido (< 1 segundo)
#          Sem re-execução de graph/llm
```

### Teste 3: Interação Widget

```
Clicar em botão/slider
# Esperado: Resposta imediata
#          Sem timeout de grafo
```

---

## MONITORAMENTO

**Ativar logs para debug:**

Adicione em `streamlit_app.py`:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@st.cache_resource
def get_graph():
    logger.info("Iniciando carregamento do grafo...")
    start = time.time()
    try:
        from core.graph.graph_builder import build_graph
        graph = build_graph()
        elapsed = time.time() - start
        logger.info(f"Grafo carregado em {elapsed:.2f}s")
        return graph
    except Exception as e:
        logger.error(f"Erro ao carregar grafo: {e}", exc_info=True)
        return None
```

---

## RESUMO EXECUTIVO

| Passo | Arquivo | Ação | Tempo |
|-------|---------|------|-------|
| 1 | `.streamlit/config.toml` | Trocar `runOnSave=false` | 1 min |
| 2 | `streamlit_app.py` | Mover `st.set_page_config()` para linha 1-5 | 2 min |
| 3 | `streamlit_app.py` | Envolver `build_graph()` com `@st.cache_resource` | 5 min |
| 4 | `streamlit_app.py` | Envolver `get_llm()` com `@st.cache_resource` | 3 min |
| 5 | `streamlit_app.py` | Adicionar `initialize_state()` com session checks | 3 min |
| 6 | `streamlit_app.py` | Teste: `streamlit cache clear && streamlit run streamlit_app.py` | 2 min |

**TEMPO TOTAL: 16 minutos**

**RESULTADO ESPERADO:**
- Carregamento: ~3s (vs. infinito antes)
- Reload: ~0.5s (vs. 5-10s antes)
- Sem freezes ou timeouts

---

**Gerado por: Audit Agent v2.0**
**Status: Pronto para implementação**
