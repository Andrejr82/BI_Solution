# Arquivos Principais para Inicialização do Sistema
**Data:** 10/10/2025
**Tipo:** Documentação Técnica
**Status:** Completo

---

## Visão Geral

Este documento mapeia **todos os arquivos críticos** necessários para a inicialização do sistema Agent_BI, incluindo a ordem de carregamento, dependências e funções de cada componente.

---

## 1. ARQUIVOS DE PONTO DE ENTRADA

### 1.1. `start_app.py` (Recomendado)
**Função:** Inicializador multiplataforma que orquestra o startup completo

**Responsabilidades:**
- Verifica existência de arquivos necessários
- Valida ambiente virtual (.venv)
- Inicia backend FastAPI (opcional, em background)
- Inicia frontend Streamlit (foreground)
- Gerencia shutdown gracefully

**Como usar:**
```bash
python start_app.py
```

**Sequência de inicialização:**
```
1. Verificar streamlit_app.py existe
2. Verificar ambiente virtual (.venv)
3. [Opcional] Iniciar FastAPI backend (main.py)
   └─ uvicorn main:app --host 0.0.0.0 --port 8000
4. Iniciar Streamlit frontend
   └─ streamlit run streamlit_app.py
```

**Arquivos verificados:**
- `streamlit_app.py` (obrigatório)
- `main.py` (opcional)
- `.venv/Scripts/activate` ou `.venv/bin/activate`

---

### 1.2. `streamlit_app.py` (Principal)
**Função:** Aplicação Streamlit - Frontend principal do sistema

**Responsabilidades:**
- Autenticação de usuários
- Inicialização do backend integrado (LangGraph + LLM + Dados)
- Interface de chat
- Renderização de gráficos e tabelas
- Histórico de queries

**Como usar diretamente:**
```bash
streamlit run streamlit_app.py
```

**Fluxo de inicialização interno:**
```
1. Configurar logging (ERROR only)
2. Carregar autenticação (lazy loading)
   └─ core/auth.py
3. Login do usuário
4. Inicializar backend (cache @st.cache_resource)
   ├─ Carregar settings (core/config/safe_settings.py)
   ├─ Inicializar LLM Adapter (ComponentFactory)
   ├─ Inicializar HybridDataAdapter (SQL Server + Parquet)
   ├─ Inicializar CodeGenAgent
   ├─ Construir grafo LangGraph (GraphBuilder)
   └─ Inicializar QueryHistory
5. Renderizar interface do usuário
6. Processar queries via DirectQueryEngine ou agent_graph
```

---

### 1.3. `main.py` (Opcional)
**Função:** Backend FastAPI standalone (modo API)

**Responsabilidades:**
- Servir API REST para queries
- Endpoint `/api/v1/query` - processar consultas
- Endpoint `/status` - health check

**Uso:**
- **Modo integrado (padrão):** NÃO necessário (backend embutido no streamlit_app.py)
- **Modo API standalone:** `uvicorn main:app --host 0.0.0.0 --port 8000`

**Quando usar:** Apenas se precisar acessar o sistema via API REST externa (não pelo Streamlit)

---

## 2. COMPONENTES CORE DE INICIALIZAÇÃO

### 2.1. Configuração

#### `core/config/safe_settings.py`
**Prioridade:** CRÍTICA (primeiro componente carregado)

**Função:**
- Carrega variáveis de ambiente (.env ou Streamlit secrets)
- Valida chaves de API (GEMINI_API_KEY, DEEPSEEK_API_KEY)
- Configura conexão SQL Server (opcional)

**Variáveis essenciais:**
```python
# LLM (obrigatório - pelo menos uma)
GEMINI_API_KEY=sk-...
DEEPSEEK_API_KEY=sk-...

# Modelos
GEMINI_MODEL_NAME=gemini-2.5-flash
DEEPSEEK_MODEL_NAME=deepseek-chat

# SQL Server (opcional)
DB_SERVER=localhost
DB_NAME=seu_banco
DB_USER=usuario
DB_PASSWORD=senha
DB_DRIVER=ODBC Driver 17 for SQL Server

# Flags
USE_SQL_SERVER=false  # false = usa apenas Parquet
FALLBACK_TO_PARQUET=true
```

**Lazy Loading:** ✅ Carregado sob demanda via `get_safe_settings()`

---

### 2.2. Autenticação

#### `core/auth.py`
**Prioridade:** ALTA (antes de inicializar backend)

**Função:**
- Sistema de login adaptativo (SQL Server ou Cloud fallback)
- Rate limiting (proteção contra força bruta)
- Gerenciamento de sessão com expiração
- Auditoria de logins

**Modos de autenticação:**
1. **SQL Server** (prioritário)
   - Usa `core/database/sql_server_auth_db.py`
   - Senhas com hash bcrypt
   - Gerenciamento de tentativas

2. **Cloud Fallback** (se SQL indisponível)
   - Usuários hardcoded em `CLOUD_USERS`
   - Usuários padrão: admin/admin, user/user123, cacula/cacula123

**Lazy Loading:** ✅ Autenticação carregada sob demanda

---

### 2.3. Adaptadores LLM

#### `core/llm_adapter.py`
**Prioridade:** CRÍTICA (necessário para processar queries)

**Classes principais:**
- `GeminiLLMAdapter` - Cliente Gemini 2.5 Flash (prioritário)
- `DeepSeekLLMAdapter` - Cliente DeepSeek (fallback)

**Características:**
- Cache de respostas (48h TTL) - ECONOMIA DE CRÉDITOS
- Fallback automático Gemini → DeepSeek em rate limit
- Detecção inteligente de quota exceeded

**Integração com ComponentFactory:**
```python
from core.factory.component_factory import ComponentFactory
llm = ComponentFactory.get_llm_adapter("gemini")
```

**Rate Limit Handling:**
```
Rate limit Gemini detectado
    ↓
ComponentFactory.set_gemini_unavailable(True)
    ↓
Próximas chamadas usam DeepSeek automaticamente
```

---

#### `core/factory/component_factory.py`
**Prioridade:** CRÍTICA (gerencia todos os adaptadores)

**Função:**
- Factory pattern para criar componentes
- Singleton para LLM adapters (reuso de instâncias)
- Fallback automático Gemini → DeepSeek

**Métodos principais:**
```python
ComponentFactory.get_llm_adapter("gemini")        # LLM principal
ComponentFactory.get_llm_adapter("deepseek")      # LLM fallback
ComponentFactory.set_gemini_unavailable(True)     # Ativar fallback
ComponentFactory.try_restore_gemini()             # Tentar restaurar
```

---

### 2.4. Adaptadores de Dados

#### `core/connectivity/hybrid_adapter.py`
**Prioridade:** CRÍTICA (acesso aos dados)

**Função:**
- Adapter híbrido com fallback automático SQL Server → Parquet
- Garante zero downtime
- Executa queries com filtros inteligentes

**Lógica de inicialização:**
```
1. SEMPRE inicializar ParquetAdapter (obrigatório)
   └─ Arquivo: data/parquet/admmat.parquet

2. Se USE_SQL_SERVER=true:
   ├─ Tentar conectar SQL Server
   ├─ Se sucesso: usar SQL Server como primário
   └─ Se falha: fallback para Parquet

3. Executar queries:
   ├─ Tentar SQL Server primeiro (se disponível)
   └─ Fallback automático para Parquet em erro
```

**Dependências:**
- `core/connectivity/parquet_adapter.py` (obrigatório)
- `core/connectivity/sql_server_adapter.py` (opcional)

**Status atual:** Sistema usa **apenas Parquet** (USE_SQL_SERVER=false)

---

#### `core/connectivity/parquet_adapter.py`
**Prioridade:** CRÍTICA (fonte de dados principal)

**Função:**
- Lê arquivo Parquet admmat.parquet
- Executa queries com filtros otimizados
- Retorna dados em formato dict/list

**Arquivo de dados:**
```
data/parquet/admmat.parquet  (obrigatório)
```

**Lazy Loading:** DataFrame carregado sob demanda

---

### 2.5. Motor de Query

#### `core/business_intelligence/direct_query_engine.py`
**Prioridade:** ALTA (processamento de queries)

**Função:**
- Classifica intenção da query (29 padrões regex)
- Executa queries simples rapidamente (100-300ms)
- Retorna "fallback" para queries não reconhecidas

**Padrões suportados:**
- Produto mais vendido
- Top N produtos/segmentos/UNEs
- Ranking de vendas
- Evolução temporal
- Análise ABC
- Produtos sem movimento
- Estoque (alto/baixo/rotação)
- E mais 20+ padrões...

**Cache:** ✅ Inicializado com @st.cache_resource no streamlit_app.py

**Dependências:**
- `data/query_patterns_training.json` (29 padrões)
- `core/utils/field_mapper.py` (mapeamento de campos)

---

### 2.6. Grafo LangGraph

#### `core/graph/graph_builder.py`
**Prioridade:** MÉDIA (usado apenas para queries complexas)

**Função:**
- Constrói máquina de estados LangGraph
- Orquestra fluxo de processamento de queries complexas

**Nós do grafo:**
```
1. classify_intent          - Classifica intenção
2. clarify_requirements     - Solicita esclarecimentos
3. generate_parquet_query   - Gera filtros
4. execute_query            - Executa query
5. generate_plotly_spec     - Gera gráficos
6. format_final_response    - Formata resposta
```

**Status atual:** ⚠️ DESABILITADO temporariamente (ver `docs/SOLUCAO_TRAVAMENTO_AGENTGRAPH_10_10_2025.md`)

**Motivo:** `agent_graph.invoke()` não tinha timeout e causava travamentos

**Fallback:** Queries não reconhecidas retornam mensagem clara ao usuário

---

## 3. ARQUIVOS DE DADOS ESSENCIAIS

### 3.1. Dados Parquet
```
data/parquet/admmat.parquet (OBRIGATÓRIO)
```
**Tamanho:** ~100k linhas
**Colunas principais:**
- une, codigo, nome_produto, une_nome
- nomesegmento, nome_categoria
- mes_01 a mes_12 (vendas mensais)
- estoque_atual, venda_30_d
- preco_38_percent

**Fallback:** Sistema NÃO funciona sem este arquivo

---

### 3.2. Configurações de Query
```
data/query_patterns_training.json (CRÍTICO)
```
**Conteúdo:** 29 padrões regex para classificação de queries

**Estrutura:**
```json
{
  "patterns": [
    {
      "pattern_id": "produto_mais_vendido",
      "keywords": ["produto", "mais vendido"],
      "regex": "...",
      "examples": ["produto mais vendido"]
    }
  ]
}
```

**Validação:** JSON deve estar válido (sem caracteres extras)

---

### 3.3. Histórico de Queries
```
data/query_history/history_YYYYMMDD.json (auto-criado)
```
**Função:** Registra todas as queries executadas

**Estrutura:**
```json
{
  "session_id": "uuid",
  "query": "texto",
  "timestamp": "ISO8601",
  "success": true,
  "results_count": 10,
  "processing_time": 0.25
}
```

---

## 4. ORDEM DE INICIALIZAÇÃO COMPLETA

### Fase 1: Pré-inicialização (streamlit_app.py:1-130)
```
1. Configurar logging básico (ERROR only)
2. Definir funções de lazy loading (get_auth_functions, get_backend_module)
3. Verificar autenticação
   └─ Se não autenticado: mostrar login
   └─ Se autenticado: prosseguir
```

### Fase 2: Inicialização do Backend (streamlit_app.py:138-332)
```
@st.cache_resource
def initialize_backend():
    1. Carregar módulos (lazy loading)
       ├─ GraphBuilder
       ├─ ComponentFactory
       ├─ ParquetAdapter
       ├─ CodeGenAgent
       ├─ HumanMessage
       └─ QueryHistory

    2. Verificar chaves LLM
       ├─ st.secrets.GEMINI_API_KEY
       ├─ st.secrets.DEEPSEEK_API_KEY
       └─ Fallback para get_settings()

    3. Inicializar LLM
       └─ ComponentFactory.get_llm_adapter("gemini")

    4. Inicializar HybridDataAdapter
       ├─ ParquetAdapter (obrigatório)
       └─ [Opcional] SQLServerAdapter

    5. Inicializar CodeGenAgent
       └─ CodeGenAgent(llm_adapter)

    6. Inicializar QueryHistory
       └─ QueryHistory(history_dir)

    7. Construir grafo LangGraph
       └─ GraphBuilder(...).build()

    8. Retornar componentes
       └─ {llm_adapter, parquet_adapter, agent_graph, query_history}
```

### Fase 3: Cache de DirectQueryEngine (streamlit_app.py:428-443)
```
@st.cache_resource
def get_direct_query_engine():
    1. Obter DirectQueryEngine module
    2. Obter HybridDataAdapter do backend
    3. Criar DirectQueryEngine(adapter)
    4. Retornar engine (cached)
```

### Fase 4: Processamento de Queries (streamlit_app.py:446-589)
```
def query_backend(user_input):
    1. Obter DirectQueryEngine (cached)
    2. Processar query
       └─ direct_result = engine.process_query(user_input)

    3. Verificar result_type
       ├─ "error" → Mostrar erro
       ├─ "chart"/"data"/outros → Mostrar resultado
       └─ "fallback" → Mostrar mensagem de não reconhecido

    4. [DESABILITADO] Fallback para agent_graph

    5. Adicionar ao histórico
    6. Atualizar session_state
```

---

## 5. DEPENDÊNCIAS CRÍTICAS POR ARQUIVO

### streamlit_app.py
**Depende de:**
- core/auth.py (autenticação)
- core/config/safe_settings.py (configurações)
- core/factory/component_factory.py (LLM adapter)
- core/connectivity/hybrid_adapter.py (dados)
- core/graph/graph_builder.py (grafo)
- core/business_intelligence/direct_query_engine.py (queries)
- core/utils/query_history.py (histórico)
- data/parquet/admmat.parquet (dados)

### direct_query_engine.py
**Depende de:**
- core/connectivity/hybrid_adapter.py (dados)
- data/query_patterns_training.json (padrões)
- core/utils/field_mapper.py (mapeamento)

### hybrid_adapter.py
**Depende de:**
- core/connectivity/parquet_adapter.py (obrigatório)
- core/connectivity/sql_server_adapter.py (opcional)
- data/parquet/admmat.parquet (dados)

### component_factory.py
**Depende de:**
- core/llm_adapter.py (Gemini + DeepSeek)
- core/config/safe_settings.py (configurações)

### graph_builder.py
**Depende de:**
- core/agents/bi_agent_nodes.py (nós do grafo)
- core/agent_state.py (estado)
- core/llm_base.py (interface LLM)

---

## 6. ARQUIVOS OPCIONAIS (NÃO CRÍTICOS)

### main.py
**Função:** Backend FastAPI standalone
**Status:** Opcional (não usado em modo integrado)

### core/connectivity/sql_server_adapter.py
**Função:** Adapter para SQL Server
**Status:** Opcional (sistema usa apenas Parquet)

### core/database/sql_server_auth_db.py
**Função:** Autenticação via SQL Server
**Status:** Opcional (fallback para cloud auth)

---

## 7. MODO DE FALHA E FALLBACKS

### 7.1. LLM Fallback
```
Gemini indisponível (rate limit)
    ↓
ComponentFactory.set_gemini_unavailable(True)
    ↓
Próximas chamadas usam DeepSeek
```

### 7.2. Dados Fallback
```
SQL Server indisponível
    ↓
HybridAdapter usa Parquet automaticamente
    ↓
Zero downtime
```

### 7.3. Query Fallback
```
Query não reconhecida por DirectQueryEngine
    ↓
Retorna result_type="fallback"
    ↓
[ANTES] Usava agent_graph (travava)
[AGORA] Mostra mensagem clara ao usuário
```

### 7.4. Auth Fallback
```
SQL Server auth indisponível
    ↓
Usa cloud auth (CLOUD_USERS)
    ↓
Usuários hardcoded funcionam
```

---

## 8. CHECKLIST DE INICIALIZAÇÃO

### Arquivos Obrigatórios
- [ ] streamlit_app.py
- [ ] core/config/safe_settings.py
- [ ] core/llm_adapter.py
- [ ] core/factory/component_factory.py
- [ ] core/connectivity/parquet_adapter.py
- [ ] core/connectivity/hybrid_adapter.py
- [ ] core/business_intelligence/direct_query_engine.py
- [ ] data/parquet/admmat.parquet
- [ ] data/query_patterns_training.json

### Variáveis de Ambiente Obrigatórias
- [ ] GEMINI_API_KEY ou DEEPSEEK_API_KEY (pelo menos uma)

### Arquivos Opcionais
- [ ] start_app.py (helper de startup)
- [ ] main.py (modo API)
- [ ] core/auth.py (pode usar fallback cloud)
- [ ] core/connectivity/sql_server_adapter.py (pode usar apenas Parquet)

---

## 9. COMANDOS DE INICIALIZAÇÃO

### Modo Recomendado (via start_app.py)
```bash
python start_app.py
```

### Modo Direto (Streamlit)
```bash
streamlit run streamlit_app.py
```

### Modo API (Backend standalone)
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Ambiente Virtual
```bash
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

---

## 10. LOGS DE INICIALIZAÇÃO

### Sucesso Completo
```
[OK] Configurações carregadas com sucesso
[OK] Gemini API key encontrada
[OK] Parquet adapter inicializado: admmat.parquet
[OK] LLM OK
[OK] HybridDataAdapter OK - Fonte: PARQUET
[OK] Dataset: 100,000 produtos, 10 UNEs
[OK] CodeGen OK
[OK] QueryHistory OK
[OK] Grafo OK
[OK] Backend inicializado com sucesso!
```

### Falhas Comuns
```
[ERRO] GEMINI_API_KEY não encontrada
→ Solução: Adicionar ao .env ou st.secrets

[ERRO] Parquet não encontrado
→ Solução: Verificar data/parquet/admmat.parquet existe

[ERRO] JSON inválido: query_patterns_training.json
→ Solução: Validar JSON (remover caracteres extras)

[AVISO] SQL Server indisponível
→ Não é erro crítico - sistema usa Parquet
```

---

## 11. RESUMO EXECUTIVO

### Arquivos CRÍTICOS (sistema não funciona sem)
1. `streamlit_app.py` - Frontend principal
2. `core/config/safe_settings.py` - Configurações
3. `core/llm_adapter.py` - Processamento LLM
4. `core/connectivity/parquet_adapter.py` - Acesso a dados
5. `core/business_intelligence/direct_query_engine.py` - Motor de queries
6. `data/parquet/admmat.parquet` - Dados

### Arquivos IMPORTANTES (sistema funciona com fallback)
1. `core/auth.py` - Autenticação (fallback: cloud users)
2. `core/graph/graph_builder.py` - Queries complexas (desabilitado temporariamente)
3. `core/connectivity/sql_server_adapter.py` - SQL Server (fallback: Parquet)

### Variáveis de Ambiente CRÍTICAS
- `GEMINI_API_KEY` ou `DEEPSEEK_API_KEY`

### Ordem de Carregamento
```
1. Logging
2. Autenticação
3. Settings (safe_settings.py)
4. LLM Adapter (ComponentFactory)
5. Data Adapter (HybridDataAdapter)
6. DirectQueryEngine (cached)
7. [Opcional] LangGraph
```

---

**Autor:** Claude Code
**Data:** 10/10/2025
**Versão:** 1.0
**Status:** Completo e Validado
