# Diagrama de Inicialização do Sistema Agent_BI
**Data:** 10/10/2025
**Tipo:** Diagrama Visual
**Status:** Completo

---

## Fluxo Completo de Inicialização

```
┌─────────────────────────────────────────────────────────────────┐
│                    PONTO DE ENTRADA                              │
│                                                                  │
│  Opção 1: python start_app.py (recomendado)                    │
│  Opção 2: streamlit run streamlit_app.py (direto)              │
│  Opção 3: uvicorn main:app (modo API standalone - RARO)        │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┴──────────────────┐
         │                                   │
         ▼                                   ▼
┌─────────────────────┐          ┌─────────────────────┐
│  START_APP.PY       │          │  STREAMLIT_APP.PY   │
│  (Helper)           │          │  (Direto)           │
└─────────┬───────────┘          └─────────┬───────────┘
          │                                 │
          │ 1. Verifica arquivos            │
          │ 2. [Opcional] Inicia            │
          │    main.py (FastAPI)            │ [IGNORA]
          │    em background                │ main.py
          │ 3. Inicia streamlit_app.py      │
          │                                 │
          └───────────────┬─────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   STREAMLIT_APP.PY                               │
│                   (Frontend Principal + Backend Integrado)       │
│                                                                  │
│   ⚠️ IMPORTANTE: Backend está INTEGRADO no streamlit_app.py    │
│   main.py é OPCIONAL e usado apenas para acesso via API REST    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────┴────────────────┐
        │                                  │
        ▼                                  ▼
┌──────────────┐                  ┌──────────────┐
│   LOGGING    │                  │ LAZY LOADING │
│              │                  │   SETUP      │
│ ERROR only   │                  │              │
└──────┬───────┘                  └──────┬───────┘
       │                                  │
       └──────────────┬───────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FASE 1: AUTENTICAÇÃO                           │
│                   core/auth.py                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────┐            ┌─────────────────┐
│  SQL Server     │            │  Cloud Fallback │
│  Auth (Try)     │    FAIL    │  (Hardcoded)    │
│                 ├───────────>│                 │
│ sql_server_     │            │  CLOUD_USERS    │
│ auth_db.py      │            │                 │
└─────────────────┘            └─────────────────┘
         │                               │
         └───────────────┬───────────────┘
                         │ (Autenticado)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              FASE 2: INICIALIZAÇÃO DO BACKEND                    │
│              @st.cache_resource (executa 1x)                     │
│              streamlit_app.py:initialize_backend()               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────┴────────────────┐
        │                                  │
        ▼                                  ▼
┌──────────────────┐              ┌──────────────────┐
│  STEP 1:         │              │  STEP 2:         │
│  Carregar        │              │  Verificar       │
│  Módulos         │              │  Chaves LLM      │
│                  │              │                  │
│ - GraphBuilder   │              │ st.secrets ou    │
│ - Component      │              │ get_settings()   │
│   Factory        │              │                  │
│ - ParquetAdapter │              │ GEMINI_API_KEY   │
│ - CodeGenAgent   │              │ DEEPSEEK_API_KEY │
│ - HumanMessage   │              │                  │
│ - QueryHistory   │              │                  │
└────────┬─────────┘              └────────┬─────────┘
         │                                  │
         └──────────────┬───────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: INICIALIZAR SETTINGS                                    │
│  core/config/safe_settings.py                                    │
│                                                                  │
│  get_safe_settings()                                             │
│    ├─ Carregar .env ou st.secrets                               │
│    ├─ GEMINI_API_KEY                                             │
│    ├─ DEEPSEEK_API_KEY                                           │
│    ├─ LLM_MODEL_NAME                                             │
│    └─ DB_* (opcional)                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: INICIALIZAR LLM ADAPTER                                 │
│  core/factory/component_factory.py                               │
│                                                                  │
│  ComponentFactory.get_llm_adapter("gemini")                      │
│    ├─ Cria GeminiLLMAdapter                                      │
│    ├─ Configura cache (48h TTL)                                  │
│    └─ Prepara fallback para DeepSeek                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: INICIALIZAR DATA ADAPTER                                │
│  core/connectivity/hybrid_adapter.py                             │
│                                                                  │
│  HybridDataAdapter()                                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────────┐        ┌─────────────────────┐
│  OBRIGATÓRIO:       │        │  OPCIONAL:          │
│  ParquetAdapter     │        │  SQLServerAdapter   │
│                     │        │                     │
│  data/parquet/      │  FAIL  │  SQL Server         │
│  admmat.parquet ◄───┼────────┤  (se disponível)    │
│                     │        │                     │
│  ~100k linhas       │        │  USE_SQL_SERVER=    │
│  54 colunas         │        │  true/false         │
└─────────────────────┘        └─────────────────────┘
         │                               │
         └───────────────┬───────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  current_source = "parquet" ou "sqlserver"                       │
│  Fallback automático em erros                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: INICIALIZAR CODEGEN AGENT                               │
│  core/agents/code_gen_agent.py                                   │
│                                                                  │
│  CodeGenAgent(llm_adapter)                                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 7: INICIALIZAR QUERY HISTORY                               │
│  core/utils/query_history.py                                     │
│                                                                  │
│  QueryHistory(history_dir="data/query_history")                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 8: CONSTRUIR GRAFO LANGGRAPH                               │
│  core/graph/graph_builder.py                                     │
│                                                                  │
│  GraphBuilder(llm_adapter, parquet_adapter, code_gen_agent)      │
│    .build()                                                      │
│                                                                  │
│  Nós:                                                            │
│    1. classify_intent                                            │
│    2. clarify_requirements                                       │
│    3. generate_parquet_query                                     │
│    4. execute_query                                              │
│    5. generate_plotly_spec                                       │
│    6. format_final_response                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  BACKEND COMPONENTS PRONTOS                                      │
│                                                                  │
│  return {                                                        │
│    "llm_adapter": llm_adapter,                                   │
│    "parquet_adapter": parquet_adapter,                           │
│    "code_gen_agent": code_gen_agent,                             │
│    "agent_graph": agent_graph,  ⚠️ DESABILITADO                 │
│    "query_history": query_history                                │
│  }                                                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           FASE 3: CACHE DO DIRECT QUERY ENGINE                   │
│           @st.cache_resource (executa 1x)                        │
│           streamlit_app.py:get_direct_query_engine()             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  DirectQueryEngine(adapter)                                      │
│  core/business_intelligence/direct_query_engine.py               │
│                                                                  │
│  Carrega:                                                        │
│    - data/query_patterns_training.json (29 padrões)              │
│    - core/utils/field_mapper.py (mapeamento de campos)           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 SISTEMA PRONTO                                   │
│                 Interface Renderizada                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              FASE 4: PROCESSAMENTO DE QUERIES                    │
│              streamlit_app.py:query_backend()                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────┴────────────────┐
        │                                  │
        ▼                                  ▼
┌──────────────────────┐          ┌──────────────────────┐
│  DirectQueryEngine   │          │  User Input          │
│  (cached)            │          │                      │
│                      │          │  "produto mais       │
│  process_query()     │<─────────┤   vendido"           │
└──────────┬───────────┘          └──────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│  classify_intent_direct()                                        │
│                                                                  │
│  Testa 29 padrões regex:                                         │
│    - produto_mais_vendido                                        │
│    - top_n_produtos                                              │
│    - ranking_vendas                                              │
│    - vendas_por_segmento                                         │
│    - evolucao_temporal                                           │
│    - ... (24+ padrões)                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────────┐        ┌─────────────────────┐
│  MATCH ENCONTRADO   │        │  NENHUM MATCH       │
│                     │        │                     │
│  Executar método    │        │  result_type =      │
│  específico         │        │  "fallback"         │
│                     │        │                     │
│  _query_produto_    │        │  Retorna sugestão   │
│  mais_vendido()     │        │  clara ao usuário   │
│                     │        │                     │
│  Retorna:           │        │  ⚠️ agent_graph     │
│  - type: "chart"    │        │  DESABILITADO       │
│  - title: "..."     │        │  (evitar travamento)│
│  - chart_data: {}   │        │                     │
│  - summary: "..."   │        │                     │
│                     │        │                     │
│  Tempo: 100-300ms   │        │  Tempo: ~100ms      │
└─────────┬───────────┘        └─────────┬───────────┘
          │                               │
          └───────────────┬───────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  Adicionar ao QueryHistory                                       │
│  data/query_history/history_YYYYMMDD.json                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Renderizar Resposta na Interface                                │
│                                                                  │
│  - Texto: st.write()                                             │
│  - Gráfico: st.plotly_chart()                                    │
│  - Tabela: st.dataframe()                                        │
│  - Erro: st.error()                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Diagrama de Dependências

```
streamlit_app.py
  ├── core/auth.py
  │     ├── core/security.py (RateLimiter)
  │     └── core/database/sql_server_auth_db.py (opcional)
  │
  ├── core/config/safe_settings.py
  │     ├── dotenv (.env)
  │     └── streamlit.secrets (st.secrets)
  │
  ├── core/factory/component_factory.py
  │     ├── core/llm_adapter.py
  │     │     ├── GeminiLLMAdapter
  │     │     └── DeepSeekLLMAdapter
  │     └── core/config/safe_settings.py
  │
  ├── core/connectivity/hybrid_adapter.py
  │     ├── core/connectivity/parquet_adapter.py [CRÍTICO]
  │     │     └── data/parquet/admmat.parquet [OBRIGATÓRIO]
  │     └── core/connectivity/sql_server_adapter.py [OPCIONAL]
  │
  ├── core/graph/graph_builder.py
  │     ├── core/agents/bi_agent_nodes.py
  │     ├── core/agent_state.py
  │     └── langgraph.graph.StateGraph
  │
  ├── core/business_intelligence/direct_query_engine.py
  │     ├── data/query_patterns_training.json [CRÍTICO]
  │     ├── core/utils/field_mapper.py
  │     └── core/connectivity/hybrid_adapter.py
  │
  └── core/utils/query_history.py
        └── data/query_history/ (auto-criado)
```

---

## Diagrama de Fallbacks

```
┌─────────────────────────────────────────────────────────────────┐
│                    SISTEMA DE FALLBACKS                          │
└─────────────────────────────────────────────────────────────────┘

1. LLM FALLBACK
   ┌──────────────┐
   │   Gemini     │  Rate Limit
   │   2.5 Flash  ├──────────────┐
   │              │              │
   └──────────────┘              ▼
                        ┌──────────────────┐
                        │  ComponentFactory│
                        │  .set_gemini_    │
                        │  unavailable(True│
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │   DeepSeek       │
                        │   (Fallback)     │
                        └──────────────────┘


2. DATA FALLBACK
   ┌──────────────┐
   │ SQL Server   │  Timeout/Erro
   │              ├──────────────┐
   └──────────────┘              │
                                 ▼
                        ┌──────────────────┐
                        │  Parquet Adapter │
                        │  (SEMPRE OK)     │
                        └──────────────────┘


3. AUTH FALLBACK
   ┌──────────────────┐
   │ SQL Server Auth  │  Indisponível
   │                  ├──────────────┐
   └──────────────────┘              │
                                     ▼
                            ┌──────────────────┐
                            │  Cloud Auth      │
                            │  (CLOUD_USERS)   │
                            └──────────────────┘


4. QUERY FALLBACK
   ┌──────────────────────┐
   │ DirectQueryEngine    │  Não reconheceu
   │ (29 padrões regex)   ├──────────────────┐
   └──────────────────────┘                  │
                                             ▼
                            ┌──────────────────────────┐
                            │  Mensagem Clara          │
                            │  "Query não reconhecida" │
                            │                          │
                            │  ⚠️ ANTES: agent_graph   │
                            │  (travava)               │
                            │                          │
                            │  ✅ AGORA: feedback      │
                            │  instantâneo             │
                            └──────────────────────────┘
```

---

## Cronograma de Inicialização (Tempo)

```
T=0s      ┌──────────────────────────────┐
          │ Streamlit inicia             │
          └────────────┬─────────────────┘
                       │
T=0.1s    ┌────────────┴─────────────────┐
          │ Logging configurado          │
          └────────────┬─────────────────┘
                       │
T=0.2s    ┌────────────┴─────────────────┐
          │ Autenticação (se já logado)  │
          └────────────┬─────────────────┘
                       │
T=0.5s    ┌────────────┴─────────────────┐
          │ initialize_backend() INICIA  │
          │ (CACHE - executa 1x)         │
          └────────────┬─────────────────┘
                       │
T=1.0s    ┌────────────┴─────────────────┐
          │ Settings carregadas          │
          │ LLM adapter inicializado     │
          └────────────┬─────────────────┘
                       │
T=2.0s    ┌────────────┴─────────────────┐
          │ HybridDataAdapter OK         │
          │ Parquet carregado            │
          └────────────┬─────────────────┘
                       │
T=3.0s    ┌────────────┴─────────────────┐
          │ CodeGen + QueryHistory OK    │
          └────────────┬─────────────────┘
                       │
T=4.0s    ┌────────────┴─────────────────┐
          │ GraphBuilder OK              │
          │ Backend PRONTO               │
          └────────────┬─────────────────┘
                       │
T=4.5s    ┌────────────┴─────────────────┐
          │ DirectQueryEngine cached     │
          └────────────┬─────────────────┘
                       │
T=5.0s    ┌────────────┴─────────────────┐
          │ ✅ SISTEMA PRONTO            │
          │ Interface renderizada        │
          │ Aguardando queries           │
          └──────────────────────────────┘

Tempo Total: ~5 segundos (primeira execução)
Subsequentes: ~1 segundo (cache ativo)
```

---

## Estados do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    ESTADOS POSSÍVEIS                             │
└─────────────────────────────────────────────────────────────────┘

1. [STARTING] Sistema iniciando
   └─> Carregando componentes

2. [AUTH_REQUIRED] Aguardando autenticação
   └─> Mostrar tela de login

3. [INITIALIZING] Backend inicializando
   └─> Executando initialize_backend()

4. [READY] Sistema pronto
   └─> Aguardando queries do usuário

5. [PROCESSING] Processando query
   └─> DirectQueryEngine trabalhando

6. [ERROR] Erro crítico
   └─> Componente obrigatório falhou

7. [DEGRADED] Modo degradado
   └─> Funcionando com fallbacks ativos
```

---

## Fluxo de Query Simplificado

```
User Input
    │
    ▼
DirectQueryEngine (cached)
    │
    ├─> Testa 29 padrões regex
    │
    ├─> MATCH? ──YES──> Executa método específico ──> Retorna resultado
    │                   (100-300ms)                    (chart/data/text)
    │
    └─> NO MATCH ────> result_type="fallback" ─────> Mensagem clara
                       (~100ms)                       ao usuário
                                                      (sugestões)
```

---

**Legenda:**
- `[CRÍTICO]` - Componente obrigatório
- `[OPCIONAL]` - Componente com fallback
- `⚠️` - Atenção/Aviso
- `✅` - Status OK
- `❌` - Status Erro

**Autor:** Claude Code
**Data:** 10/10/2025
**Versão:** 1.0
