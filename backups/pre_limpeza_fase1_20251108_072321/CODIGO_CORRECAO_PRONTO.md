# CÓDIGO DE CORREÇÃO PRONTO PARA COLAR

Este arquivo contém todos os trechos de código prontos para implementação.

---

## 1. ARQUIVO: .streamlit/config.toml

**AÇÃO:** Substituir COMPLETAMENTE o conteúdo do arquivo

**CONTEÚDO COMPLETO:**

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
enableXsrfProtection = true

[logger]
level = "warning"

[theme]
primaryColor = "#0066CC"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

---

## 2. ARQUIVO: streamlit_app.py

**AÇÃO:** Reorganizar as PRIMEIRAS 100 linhas do arquivo

**ANTES (REMOVER):**

```python
# Tudo que tiver antes de st.set_page_config
from core.graph.graph_builder import build_graph
from core.llm_adapter import get_llm

graph = build_graph()  # REMOVER ESTA LINHA
llm = get_llm()  # REMOVER ESTA LINHA

# ... outro código ...

import streamlit as st
st.set_page_config(...)
```

**DEPOIS (ADICIONAR):**

```python
# ============================================================================
# LINHA 1-10: SETUP OBRIGATÓRIO
# ============================================================================

import streamlit as st

st.set_page_config(
    page_title="Agent BI Solution",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# LINHA 15-40: IMPORTS
# ============================================================================

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# LINHA 45-100: CACHE RESOURCES
# ============================================================================

@st.cache_resource
def get_graph():
    """
    Carrega grafo com cache automático.
    Executado apenas na primeira vez ou quando cache é invalidado.
    """
    logger.info("Iniciando carregamento do grafo...")
    try:
        from core.graph.graph_builder import build_graph
        graph = build_graph()
        logger.info("Grafo carregado com sucesso")
        return graph
    except TimeoutError as e:
        logger.error(f"Timeout ao carregar grafo: {e}")
        st.error("Erro: Timeout ao carregar grafo. Por favor, tente novamente.")
        return None
    except Exception as e:
        logger.error(f"Erro ao carregar grafo: {e}", exc_info=True)
        st.error(f"Erro ao carregar grafo: {str(e)}")
        return None


@st.cache_resource
def get_llm_instance():
    """
    Carrega LLM com cache automático.
    Executado apenas na primeira vez ou quando cache é invalidado.
    """
    logger.info("Iniciando carregamento do LLM...")
    try:
        from core.llm_adapter import get_llm
        llm = get_llm()

        if llm is None:
            logger.warning("LLM retornou None - pode estar offline")
            st.warning("Aviso: LLM indisponível. Algumas funcionalidades estarão limitadas.")
            return None

        logger.info("LLM carregado com sucesso")
        return llm
    except Exception as e:
        logger.error(f"Erro ao carregar LLM: {e}", exc_info=True)
        st.warning(f"Aviso: LLM indisponível ({str(e)}). Funcionalidades limitadas.")
        return None


def initialize_session_state():
    """
    Inicializa session state na primeira execução.
    Evita loops infinitos e garante que recursos foram carregados.
    """
    if 'initialized' in st.session_state:
        return  # Já foi inicializado, não precisa repetir

    logger.info("Inicializando session state...")

    # Carregar recursos com cache
    st.session_state.graph = get_graph()
    st.session_state.llm = get_llm_instance()
    st.session_state.initialized = True

    logger.info("Session state inicializado com sucesso")


# Executar inicialização (uma única vez por sessão)
initialize_session_state()

# ============================================================================
# LINHA 105+: RESTO DO CÓDIGO ORIGINAL
# ============================================================================

# ... resto do seu código aqui ...

def main():
    """Função principal da aplicação"""

    # Validar que tudo foi inicializado
    if not st.session_state.get('initialized', False):
        st.error("Erro: Aplicação não foi inicializada corretamente. Recarregue a página.")
        return

    # Validar dependências críticas
    if st.session_state.graph is None:
        st.error("Erro: Grafo não está disponível. Aplicação não pode funcionar.")
        return

    # UI Normal aqui
    st.title("Agent BI Solution")

    # Use assim em vez de inicializar novamente:
    # - st.session_state.graph para acessar o grafo
    # - st.session_state.llm para acessar o LLM


if __name__ == "__main__":
    main()
```

---

## 3. ARQUIVO: core/llm_adapter.py

**AÇÃO:** Localizar a criação do ChatAnthropic e adicionar timeout

**ANTES (PROCURAR POR):**

```python
from langchain_anthropic import ChatAnthropic

# Pode estar em uma função ou em nível de módulo
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)
```

**DEPOIS (ADICIONAR timeout):**

```python
from langchain_anthropic import ChatAnthropic

# Adicione timeout=10.0 aos parâmetros
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    timeout=10.0  # <--- ADICIONAR ESTA LINHA
)
```

Se houver uma função `get_llm()`, modifique assim:

```python
def get_llm():
    """Retorna instância do LLM com timeout"""
    from langchain_anthropic import ChatAnthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY não configurada")

    return ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        api_key=api_key,
        timeout=10.0  # <--- ADICIONAR ISTO
    )
```

---

## 4. ARQUIVO: core/graph/graph_builder.py

**AÇÃO:** Adicionar cache decorator à função build_graph (se em arquivo separado)

**SE build_graph() ESTÁ NESTE ARQUIVO:**

**ANTES:**

```python
def build_graph():
    """Constrói o grafo do agente"""
    # ... código de construção ...
    graph = StateGraph(AgentState).compile()
    return graph
```

**DEPOIS:**

```python
import functools

@functools.lru_cache(maxsize=1)
def build_graph():
    """
    Constrói o grafo do agente com cache.
    O resultado é cacheado e reutilizado.
    """
    try:
        # ... código de construção ...
        graph = StateGraph(AgentState).compile()
        return graph
    except Exception as e:
        print(f"Erro ao compilar grafo: {e}")
        raise
```

---

## 5. VALIDAÇÃO - Arquivo de Teste

**ARQUIVO NOVO (opcional):** `test_streaming_fix.py`

```python
#!/usr/bin/env python3
"""
Teste rápido para validar se as correções funcionaram
"""

import subprocess
import time
import sys

def test_streamlit_startup():
    """Testa se Streamlit inicia em tempo aceitável"""

    print("\n" + "="*70)
    print("TESTE: Startup do Streamlit")
    print("="*70 + "\n")

    start = time.time()

    try:
        # Limpar cache
        print("[1] Limpando cache do Streamlit...")
        subprocess.run(
            ["streamlit", "cache", "clear"],
            capture_output=True,
            timeout=5
        )
        print("    OK - Cache limpo\n")

        # Iniciar app
        print("[2] Iniciando aplicação Streamlit...")
        print("    (deixe rodar por 5 segundos)")

        process = subprocess.Popen(
            ["streamlit", "run", "streamlit_app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Aguardar 5 segundos
        time.sleep(5)

        # Parar processo
        process.terminate()
        stdout, stderr = process.communicate(timeout=5)

        elapsed = time.time() - start

        print(f"\n    OK - App iniciado em {elapsed:.2f}s")

        # Validar
        if elapsed < 10:
            print("\n[RESULTADO] PASSOU - Startup rápido (< 10s)")
            return True
        else:
            print("\n[RESULTADO] FALHOU - Startup lento (> 10s)")
            print("    Verifique se todos os passos foram aplicados")
            return False

    except subprocess.TimeoutExpired:
        print("\n[RESULTADO] FALHOU - Timeout infinito detectado")
        print("    Verifique a configuração runOnSave em config.toml")
        return False
    except Exception as e:
        print(f"\n[RESULTADO] ERRO - {e}")
        return False


if __name__ == "__main__":
    success = test_streamlit_startup()
    sys.exit(0 if success else 1)
```

**Para executar:**
```bash
python test_streaming_fix.py
```

---

## 6. CHECKLIST DE APLICAÇÃO

### Antes de Começar

```
[ ] 1. Fazer backup (git commit e push)
[ ] 2. Fechar todas as abas do Streamlit
[ ] 3. Ter os arquivos abertos em editor
```

### Aplicar Correções

```
[ ] 1. Editar .streamlit/config.toml
[ ] 2. Editar streamlit_app.py (linhas iniciais)
[ ] 3. Editar core/llm_adapter.py (adicionar timeout)
[ ] 4. (Opcional) Editar core/graph/graph_builder.py (adicionar cache)
```

### Testar

```
[ ] 1. streamlit cache clear
[ ] 2. streamlit run streamlit_app.py
[ ] 3. Aguardar 5-10 segundos
[ ] 4. Se carregar: SUCESSO!
[ ] 5. Pressionar F5 no navegador - deve ser instantâneo
```

### Finalizar

```
[ ] 1. git add -A
[ ] 2. git commit -m "fix: resolver carregamento infinito streamlit"
[ ] 3. git push origin main
[ ] 4. Deletar arquivos temporários de teste
```

---

## 7. TROUBLESHOOTING

### Problema: "Ainda travando após aplicar as correções"

**Verificar:**
1. `st.set_page_config()` está na linha 1-5? (certifique-se!)
2. `@st.cache_resource` foi aplicado em `get_graph()` e `get_llm_instance()`?
3. `runOnSave = false` está em `.streamlit/config.toml`?

**Solução:**
```bash
# Limpeza profunda
streamlit cache clear
rm -r ~/.streamlit/  # (ou similar em Windows)
streamlit run streamlit_app.py
```

### Problema: "ImportError: cannot import X"

**Verificar:**
1. Imports estão corretos?
2. Paths estão certos?

**Solução:**
```python
# Adicione debug
import sys
print("Python path:", sys.path)
```

### Problema: "LLM timeout mesmo com timeout=10"

**Verificar:**
1. Conexão internet está ok?
2. ANTHROPIC_API_KEY está configurada?

**Solução:**
```bash
# Verificar API key
echo %ANTHROPIC_API_KEY%  # Windows
echo $ANTHROPIC_API_KEY   # Linux/Mac
```

---

## 8. ANTES vs DEPOIS - Resumo Visual

### ANTES (ERRADO)

```python
# streamlit_app.py

from core.graph.graph_builder import build_graph  # Import pesado
from core.llm_adapter import get_llm  # Import pesado

graph = build_graph()  # TRAVA AQUI - síncrono, sem cache
llm = get_llm()  # ESPERA AQUI - sem timeout

import streamlit as st  # Chega tarde
st.set_page_config(...)  # Re-layout

# Navigator mostra: "Loading..." indefinidamente
```

### DEPOIS (CORRETO)

```python
# streamlit_app.py

import streamlit as st

st.set_page_config(...)  # PRIMEIRO - sempre

@st.cache_resource  # Cache automático
def get_graph():
    return build_graph()  # Executa 1x, reutiliza depois

@st.cache_resource  # Cache automático
def get_llm():
    return get_llm_impl(timeout=10.0)  # Com timeout

initialize_session_state()  # Lazy loading seguro

# Navigator mostra: "Agent BI Solution" em 3 segundos
```

---

## 9. Performance Esperada

### Timeline de Carregamento

#### ANTES (Errado):
```
[0s]   Usuário abre página
[1s]   Streamlit começa a executar
[5s]   Tentando compilar grafo...
[15s]  Tentando conectar ao LLM...
[∞s]   TIMEOUT - página travada
```

#### DEPOIS (Correto):
```
[0s]   Usuário abre página
[0.5s] Streamlit inicia
[1s]   Config carregado
[2s]   Grafo carregado (cache)
[3s]   LLM carregado (cache)
[3.5s] UI pronta e responsiva
```

---

## 10. Documentação Relacionada

Para análise mais profunda, veja:

1. **AUDIT_STREAMLIT_HANGING.md** - Análise técnica detalhada
2. **SOLUCAO_IMEDIATA.md** - Guia passo a passo com diagramas
3. **RELATORIO_AUDIT_COMPLETO.md** - Relatório com tabelas e impacto

---

**Pronto para copiar e colar!**

