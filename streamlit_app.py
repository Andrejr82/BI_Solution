'''
Interface de Usuário (Frontend) para o Agent_BI.
Versão integrada que não depende de API externa.
Cache clear trigger: 2025-09-21 20:52 - ValidationError fix applied
'''
from dotenv import load_dotenv

# Forçar o recarregamento das variáveis de ambiente do arquivo .env
# Isso é crucial em desenvolvimento para evitar problemas de cache.
load_dotenv(override=True)
import streamlit as st
import uuid
import pandas as pd
import logging
import sys
import time
import re
from datetime import datetime

# ============================================================================
# CONFIGURAÇÃO DE LOGGING ESTRUTURADO
# Usa sistema centralizado de logs (logs/app_activity/, logs/errors/, etc.)
# ============================================================================
from core.config.logging_config import setup_logging
from core.security import mask_pii, get_pii_summary
from core.llm_service import get_llm_service

# Inicializar sistema de logs estruturado
setup_logging()

# Configurar logger específico do Streamlit
logger = logging.getLogger("streamlit_app")
logger.setLevel(logging.INFO)  # INFO para rastrear atividades

# Silenciar logs verbosos de bibliotecas externas
logging.getLogger("faiss").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

# Log de inicialização
logger.info("=" * 80)
logger.info("[STARTUP] Streamlit App Iniciado")
logger.info(f"[STARTUP] Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info("=" * 80)

# ============================================================================
# LIMPEZA AUTOMÁTICA DE CACHE
# Executa limpeza inteligente de cache com versionamento automático
# Configurável via .env ou Streamlit secrets:
#   - CACHE_AUTO_CLEAN (default: True)
#   - CACHE_MAX_AGE_DAYS (default: 7)
#   - CACHE_FORCE_CLEAN (default: False)
# ============================================================================
from core.utils.cache_cleaner import run_cache_cleanup
from core.config.settings import get_settings

# ✅ OTIMIZAÇÃO v2.2.3: Cache cleanup DESABILITADO no startup (ganho de 1-2s)
# Executa apenas após login bem-sucedido (não crítico para inicialização)
# Reduz tempo de startup de 8s → 6s

# ============================================================================
# ============================================================================
# CSS CUSTOMIZADO - DESIGN MINIMALISTA CLEAN (v3.0)
# Otimizado para performance máxima
# Data: 20/11/2025
# ============================================================================

@st.cache_data
def load_optimized_css():
    """Carrega CSS otimizado (cached para performance)"""
    css = """
/* 🤍 DESIGN MINIMALISTA CLEAN - Performance Optimized */
:root {
    --bg-primary: #FFFFFF;
    --bg-secondary: #F8F9FA;
    --bg-card: #FFFFFF;
    --bg-input: #FFFFFF;
    --bg-sidebar: #F8F9FA;
    --border: #E5E7EB;
    --border-focus: #3B82F6;
    --text-primary: #111827;
    --text-secondary: #6B7280;
    --text-tertiary: #9CA3AF;
    --accent: #3B82F6;
    --success: #10B981;
    --error: #EF4444;
}

/* ==================== GLOBAL - FORÇAR LIGHT THEME ==================== */
/* Forçar fundo branco em TODOS os containers principais */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
body,
html,
.main,
#root {
    background: var(--bg-primary) !important;
    background-color: var(--bg-primary) !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* Header e Footer também brancos */
[data-testid="stHeader"],
header,
footer {
    background: var(--bg-primary) !important;
    background-color: var(--bg-primary) !important;
}

/* Garantir que textos e spinners sejam sempre horizontais */
.stSpinner,
.stSpinner > div,
.stMarkdown,
.stText,
p, h1, h2, h3, h4, h5, h6,
span, div, label, button,
[data-testid="stMarkdownContainer"],
[data-testid="stText"] {
    writing-mode: horizontal-tb !important;
    text-orientation: mixed !important;
}

/* Forçar spinner horizontal */
.stSpinner > div {
    display: inline-block !important;
    vertical-align: middle !important;
}

/* ==================== SIDEBAR ==================== */
section[data-testid="stSidebar"] {
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border) !important;
}

section[data-testid="stSidebar"] button {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 6px !important;
    transition: border-color 150ms ease !important;
}

section[data-testid="stSidebar"] button:hover {
    border-color: var(--accent) !important;
}

/* ==================== CHAT MESSAGES ==================== */
.stChatMessage {
    background: transparent !important;
    border: none !important;
    padding: 16px 0 !important;
    margin: 8px 0 !important;
}

.stChatMessage[data-testid="user"] {
    background: var(--bg-secondary) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    border: 1px solid var(--border) !important;
}

.stChatMessage[data-testid="assistant"] {
    background: var(--bg-card) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    border: 1px solid var(--border) !important;
}

/* ==================== INPUT AREA ==================== */
.stChatInput {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
    padding: 12px 16px !important;
    transition: all 150ms ease !important;
}

.stChatInput:focus-within {
    border-color: var(--accent) !important;
    outline: 3px solid rgba(59, 130, 246, 0.1) !important;
    outline-offset: 0px !important;
}

textarea[data-testid="stChatInputTextArea"] {
    background: transparent !important;
    border: none !important;
    color: var(--text-primary) !important;
}

/* ==================== PLOTLY CHARTS ==================== */
.js-plotly-plot {
    background: var(--bg-card) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    border: 1px solid var(--border) !important;
}

/* ==================== DATAFRAMES ==================== */
.stDataFrame {
    background: var(--bg-card) !important;
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
}

.stDataFrame thead tr {
    background: var(--bg-secondary) !important;
    border-bottom: 2px solid var(--border) !important;
}

.stDataFrame tbody tr {
    border-bottom: 1px solid var(--border) !important;
}

.stDataFrame tbody tr:hover {
    background: var(--bg-secondary) !important;
}

/* ==================== BOTÕES ==================== */
.stButton button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    font-weight: 500 !important;
    transition: all 150ms ease !important;
}

.stButton button:hover {
    background: #2563EB !important;
    transform: translateY(-1px) !important;
}

/* Botões secundários (feedback, etc) */
button[kind="secondary"],
button[kind="tertiary"] {
    background: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
}

button[kind="secondary"]:hover,
button[kind="tertiary"]:hover {
    background: var(--bg-card) !important;
    border-color: var(--accent) !important;
}

/* ==================== EXPANDER ==================== */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    padding: 12px 16px !important;
    transition: all 150ms ease !important;
}

.streamlit-expanderHeader:hover {
    background: var(--bg-secondary) !important;
    border-color: var(--accent) !important;
}

.streamlit-expanderContent {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    padding: 16px !important;
}

/* ==================== SPINNER (SEM TEXTO) ==================== */
.stSpinner > div {
    border-color: var(--accent) transparent transparent transparent !important;
    width: 20px !important;
    height: 20px !important;
}

/* Remover TODO o texto do spinner */
.stSpinner p,
.stSpinner span,
.stSpinner div[data-testid="stMarkdownContainer"],
.element-container:has(.stSpinner) p,
.element-container:has(.stSpinner) span {
    display: none !important;
    font-size: 0 !important;
    visibility: hidden !important;
}

/* Garantir que apenas o ícone apareça */
.stSpinner {
    text-align: center !important;
}

/* ==================== MÉTRICAS ==================== */
div[data-testid="stMetricValue"] {
    font-size: 28px !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
}

div[data-testid="stMetricLabel"] {
    font-size: 13px !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
}

/* ==================== INPUTS GERAIS ==================== */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    padding: 8px 12px !important;
    transition: border-color 150ms ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--accent) !important;
    outline: 3px solid rgba(59, 130, 246, 0.1) !important;
    outline-offset: 0px !important;
}

/* ==================== SCROLLBAR ==================== */
::-webkit-scrollbar {
    width: 8px !important;
    height: 8px !important;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary) !important;
}

::-webkit-scrollbar-thumb {
    background: var(--border) !important;
    border-radius: 4px !important;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--text-tertiary) !important;
}

/* ==================== OTIMIZAÇÕES DE PERFORMANCE ==================== */
*:focus-visible {
    outline: 2px solid var(--accent) !important;
    outline-offset: 2px !important;
}
    """
    return f"<style>{css}</style>"

# Carregar CSS com cache (performance boost)
st.markdown(load_optimized_css(), unsafe_allow_html=True)

# ============================================================================
# ✅ OTIMIZAÇÃO v2.2: Cache automático com versionamento
# REMOVIDO: cache.clear_all() no startup (economiza 1-2s + preserva cache válido)
# O sistema de versionamento automático em agent_graph_cache.py já invalida
# o cache quando o código muda, sem precisar limpar tudo a cada reinício.
# ============================================================================

# ============================================================================
# FIM DO CSS CUSTOMIZADO
# ============================================================================

# ✅ FUNÇÃO DE NORMALIZAÇÃO DE QUERY PARA CACHE (20/10/2025)
def normalize_query_for_cache(query: str) -> str:
    """
    Normaliza query para melhorar taxa de cache hit.
    Remove palavras irrelevantes e padroniza formato.

    Exemplos:
        "gere um gráfico de vendas" -> "grafico vendas"
        "mostre o ranking de vendas" -> "ranking vendas"
        "me mostre os produtos" -> "produtos"
    """
    if not query:
        return query

    # Lowercase
    query = query.lower().strip()

    # Remover pontuação
    query = re.sub(r'[^\w\s]', ' ', query)

    # Remover artigos e palavras de comando comuns
    stopwords = [
        'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas',
        'de', 'da', 'do', 'das', 'dos', 'no', 'na', 'nos', 'nas',
        'gere', 'mostre', 'me', 'por', 'favor', 'por favor',
        'qual', 'quais', 'liste', 'listar'
    ]

    words = query.split()
    filtered_words = [w for w in words if w not in stopwords and len(w) > 1]

    # Normalizar variações comuns
    normalized = ' '.join(filtered_words)
    normalized = normalized.replace('grafico', 'gráfico')  # Padronizar acentuação
    normalized = normalized.replace('evolucao', 'evolução')
    normalized = normalized.replace('analise', 'análise')

    return normalized

# Funções de autenticação com lazy loading
AUTH_AVAILABLE = None
_auth_module = None

def get_auth_functions():
    """Carrega funções de autenticação usando lazy loading"""
    global AUTH_AVAILABLE, _auth_module

    if AUTH_AVAILABLE is None:
        try:
            from core.auth import login as _login, sessao_expirada as _sessao_expirada
            _auth_module = {"login": _login, "sessao_expirada": _sessao_expirada}
            AUTH_AVAILABLE = True
            # Log removido - não visível para usuário
        except Exception as e:
            logging.error(f"❌ Erro ao carregar autenticação: {e}")
            AUTH_AVAILABLE = False
            _auth_module = None

    return _auth_module

def login():
    """Função de login com lazy loading"""
    auth_funcs = get_auth_functions()
    if auth_funcs:
        return auth_funcs["login"]()
    else:
        # Fallback simples
        st.error("❌ Sistema de autenticação não disponível")
        st.info("🌤️ Modo cloud - acesso liberado")
        st.session_state.authenticated = True
        st.rerun()

def sessao_expirada():
    """Função de sessão expirada com lazy loading"""
    auth_funcs = get_auth_functions()
    if auth_funcs:
        return auth_funcs["sessao_expirada"]()
    else:
        return False

# ⚡ LAZY LOADING: Importações do backend só quando necessário
BACKEND_MODULES = {}
import_errors = []

def get_backend_module(module_name):
    """Carrega módulos do backend sob demanda (lazy loading)"""
    if module_name in BACKEND_MODULES:
        return BACKEND_MODULES[module_name]

    try:
        if module_name == "GraphBuilder":
            from core.graph.graph_builder import GraphBuilder
            BACKEND_MODULES[module_name] = GraphBuilder
        elif module_name == "ComponentFactory":
            from core.factory.component_factory import ComponentFactory
            BACKEND_MODULES[module_name] = ComponentFactory
        elif module_name == "ParquetAdapter":
            from core.connectivity.parquet_adapter import ParquetAdapter
            BACKEND_MODULES[module_name] = ParquetAdapter
        elif module_name == "CodeGenAgent":
            from core.agents.code_gen_agent import CodeGenAgent
            BACKEND_MODULES[module_name] = CodeGenAgent
        elif module_name == "HumanMessage":
            from langchain_core.messages import HumanMessage
            BACKEND_MODULES[module_name] = HumanMessage
        elif module_name == "QueryHistory":
            from core.utils.query_history import QueryHistory
            BACKEND_MODULES[module_name] = QueryHistory

        return BACKEND_MODULES[module_name]
    except Exception as e:
        import_errors.append(f"{module_name}: {e}")
        logging.error(f"Erro ao carregar {module_name}: {e}")
        return None

# Settings com lazy loading
settings = None

def get_settings():
    """Obtém settings de forma lazy e segura"""
    global settings
    if settings is None:
        try:
            from core.config.safe_settings import get_safe_settings
            settings = get_safe_settings()
        except Exception as e:
            logging.error(f"Erro ao carregar settings: {e}")
            settings = None
    return settings

# --- Autenticação ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated or sessao_expirada():
    st.session_state.authenticated = False
    login()
    st.stop()  # ✅ Parar execução - evita tela de login fantasma
else:
    # --- Configuração da Página ---
    st.set_page_config(page_title="Analisador de Dados Caçulinha", page_icon="📊", layout="wide")
    st.title("📊 Analisador de Dados Caçulinha")

    # --- Inicialização do Backend Integrado ---
    @st.cache_resource(show_spinner=False)
    def initialize_backend():
        """Inicializa os componentes do backend uma única vez"""
        debug_info = []

        try:
            # ⚡ Carregar módulos sob demanda
            GraphBuilder = get_backend_module("GraphBuilder")
            ComponentFactory = get_backend_module("ComponentFactory")
            ParquetAdapter = get_backend_module("ParquetAdapter")
            CodeGenAgent = get_backend_module("CodeGenAgent")
            HumanMessage = get_backend_module("HumanMessage")
            QueryHistory = get_backend_module("QueryHistory")

            # Verificar se módulos críticos foram carregados
            if not all([GraphBuilder, ComponentFactory, ParquetAdapter]):
                with st.sidebar:
                    st.error("❌ Módulos críticos do backend não disponíveis")
                    if import_errors:
                        st.write("**Erros:**")
                        for error in import_errors:
                            st.code(error)
                return None

            debug_info.append("✅ Módulos carregados com lazy loading")
            # Debug 2: Verificar secrets de LLM (Gemini ou DeepSeek)
            gemini_key = None
            deepseek_key = None
            secrets_status = "❌ Falhou"

            try:
                gemini_key = st.secrets.get("GEMINI_API_KEY")
                deepseek_key = st.secrets.get("DEEPSEEK_API_KEY")

                if gemini_key:
                    secrets_status = "✅ Gemini OK"
                    debug_info.append(f"Secrets Gemini: OK ({gemini_key[:10]}...)")
                elif deepseek_key:
                    secrets_status = "✅ DeepSeek OK"
                    debug_info.append(f"Secrets DeepSeek: OK ({deepseek_key[:10]}...)")
                else:
                    debug_info.append(f"Secrets: Nenhuma chave LLM encontrada")
            except Exception as e:
                debug_info.append(f"Secrets erro: {e}")

            # Debug 3: Fallback para settings
            if not gemini_key and not deepseek_key:
                try:
                    current_settings = get_settings()
                    if current_settings:
                        gemini_key = getattr(current_settings, 'GEMINI_API_KEY', None)
                        deepseek_key = getattr(current_settings, 'DEEPSEEK_API_KEY', None)
                    debug_info.append(f"Settings LLM: OK")
                except Exception as e:
                    debug_info.append(f"Settings erro: {e}")

            if not gemini_key and not deepseek_key:
                raise ValueError("Nenhuma chave LLM (GEMINI_API_KEY ou DEEPSEEK_API_KEY) encontrada em secrets nem settings")

            # Debug 4: Inicializar LLM
            debug_info.append("Inicializando LLM...")
            llm_adapter = ComponentFactory.get_llm_adapter("gemini")
            debug_info.append("✅ LLM OK")

            # Debug 5: Inicializar Data Adapter (Híbrido)
            debug_info.append("Inicializando HybridDataAdapter...")
            import os
            from core.connectivity.hybrid_adapter import HybridDataAdapter

            # Usar HybridAdapter que gerencia SQL Server e Parquet
            data_adapter = HybridDataAdapter()
            adapter_status = data_adapter.get_status()

            debug_info.append(f"✅ HybridAdapter OK - Fonte: {adapter_status['current_source'].upper()}")

            # Validar que temos dados (via Parquet que sempre existe)
            import pandas as pd
            parquet_check = os.path.join(os.getcwd(), "data", "parquet", "admmat.parquet")

            if os.path.exists(parquet_check):
                # ⚡ OTIMIZAÇÃO: NÃO chamar get_schema() pois carrega dados!
                # Apenas reportar que o Parquet está disponível
                debug_info.append(f"✅ Dataset: Parquet disponível em {parquet_check}")
            else:
                debug_info.append("⚠️ Parquet não encontrado")

            # Mostrar status da fonte de dados no sidebar APENAS para admins
            user_role = st.session_state.get('role', '')
            if user_role == 'admin':
                with st.sidebar.expander("📦 Detalhes da Fonte de Dados (Admin)", expanded=False):
                    fonte_icon = "🗄️" if adapter_status['current_source'] == 'sqlserver' else "📦"
                    fonte_nome = "SQL Server" if adapter_status['current_source'] == 'sqlserver' else "Parquet"

                    info_text = f"**{fonte_icon} Fonte de Dados: {fonte_nome}**\n\n"

                    if adapter_status['sql_enabled']:
                        info_text += f"SQL Server: {'✅ Conectado' if adapter_status['sql_available'] else '❌ Indisponível'}\n"

                    info_text += f"Parquet Fallback: {'✅ Ativo' if adapter_status['fallback_enabled'] else '❌ Desativado'}\n"

                    # ParquetAdapter usa lazy loading - não exibir informações detalhadas
                    info_text += f"\n**Dataset:** Parquet com lazy loading (Polars/Dask otimizado)"
                    info_text += f"\n**Performance:** Predicate pushdown ativo - filtra antes de carregar"

                    st.info(info_text)

            # Para compatibilidade com código legado, criar alias
            parquet_adapter = data_adapter

            # Debug 6: Inicializar CodeGen
            debug_info.append("Inicializando CodeGen...")
            code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter, data_adapter=parquet_adapter)
            debug_info.append("✅ CodeGen OK")

            # Debug 7: Inicializar QueryHistory
            debug_info.append("Inicializando QueryHistory...")
            history_path = os.path.join(os.getcwd(), "data", "query_history")
            query_history = QueryHistory(history_dir=history_path)
            debug_info.append("✅ QueryHistory OK")

            # Debug 8: Construir Grafo
            debug_info.append("Construindo grafo...")
            graph_builder = GraphBuilder(
                llm_adapter=llm_adapter,
                parquet_adapter=parquet_adapter,
                code_gen_agent=code_gen_agent
            )
            agent_graph = graph_builder.build()
            debug_info.append("✅ Grafo OK")

            debug_info.append("🎉 Backend inicializado com sucesso!")

            # Mostrar painel de diagnóstico para admins
            user_role = st.session_state.get('role', '')
            if user_role == 'admin':
                with st.sidebar.expander("⚙️ Painel de Diagnóstico do Backend (Admin)", expanded=False):
                    st.write("**Debug Log:**")
                    for info in debug_info:
                        if "✅" in info:
                            st.success(info)
                        elif "⚠️" in info:
                            st.warning(info)
                        elif "❌" in info:
                            st.error(info)
                        else:
                            st.info(info)

            return {
                "llm_adapter": llm_adapter,
                "parquet_adapter": parquet_adapter,
                "code_gen_agent": code_gen_agent,
                "agent_graph": agent_graph,
                "query_history": query_history
            }

        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            debug_info.append(f"❌ ERRO: {str(e)}")
            debug_info.append(f"📍 Tipo do erro: {type(e).__name__}")

            # Log do erro completo para debugging
            logging.error(f"Backend initialization failed: {str(e)}")
            logging.error(f"Traceback: {error_traceback}")

            # Mostrar debug completo na sidebar APENAS para admins
            user_role = st.session_state.get('role', '')
            if user_role == 'admin':
                with st.sidebar:
                    st.error("🚨 Backend Error (Admin)")
                    st.write("**Debug Log:**")
                    for info in debug_info:
                        if "✅" in info:
                            st.success(info)
                        elif "❌" in info:
                            st.error(info)
                        else:
                            st.info(info)

                    with st.expander("🐛 Erro Completo (Traceback)"):
                        st.code(error_traceback)
            else:
                with st.sidebar:
                    st.error("❌ Sistema temporariamente indisponível")
                    st.info("💡 Tente recarregar a página ou entre em contato com o suporte")

            return None

    # ✅ CORREÇÃO CONTEXT7: NÃO armazenar objetos não-serializáveis no session_state
    # O @st.cache_resource já funciona como singleton, então basta chamar initialize_backend()
    # sempre que precisar - o cache retornará a mesma instância automaticamente
    backend_components = initialize_backend()

    # Feedback visual apenas (sem armazenar no session_state)
    if backend_components:
        user_role = st.session_state.get('role', '')
        if user_role == 'admin':
            with st.sidebar:
                st.success("✅ Backend inicializado!")
    else:
        user_role = st.session_state.get('role', '')
        if user_role == 'admin':
            with st.sidebar:
                st.error("❌ Backend falhou")

    # --- Logout Button ---
    with st.sidebar:
        st.write(f"Bem-vindo, {st.session_state.get('username', '')}!")
        st.write(f"DEBUG: Role do usuário (sidebar): {st.session_state.get('role', '')}") # LINHA DE DEBUG

    # --- Modo de Consulta: 100% IA ---
    with st.sidebar:
        st.divider()

        # Logo removida do sidebar conforme solicitado (2025-10-26)
        # Logo aparece apenas no chat como avatar do assistente

        st.subheader("✨ Análise Inteligente com IA")

        st.info("""
            **Converse com a Caçulinha!**
            - Eu sou sua assistente de BI.
            - Faça perguntas sobre seus dados.
            - Peça análises e gráficos.
            - Estou aqui para ajudar!
        """)

        st.caption("💡 Alimentado por IA avançada (Gemini 2.5)")

    # --- Painel de Administração ---
    user_role = st.session_state.get('role', '')
    if user_role == 'admin':
        with st.sidebar:
            st.divider()
            with st.expander("⚙️ Administração", expanded=False):
                st.subheader("💾 Gerenciamento de Cache")

                # Estatísticas do cache
                try:
                    from core.business_intelligence.agent_graph_cache import get_agent_graph_cache
                    cache = get_agent_graph_cache()
                    stats = cache.get_stats()

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Cache Memória", stats['memory_entries'])
                    with col2:
                        st.metric("Cache Disco", stats['disk_entries'])

                    st.caption(f"TTL: {stats['ttl_hours']}h")

                    # Botão para limpar cache
                    if st.button("🧹 Limpar Cache"):
                        cache.clear_all()
                        st.success("✅ Cache limpo com sucesso!")
                        st.rerun()

                except Exception as e:
                    st.error(f"Erro ao carregar estatísticas do cache: {e}")

                st.divider()
                # Perguntas Rápidas (Ocultas - pode ser reativado via checkbox)
                if st.checkbox("⚡ Mostrar Perguntas Rápidas", value=False, key="show_quick_questions"):
                    st.subheader("⚡ Perguntas Rápidas")

                    # Perguntas populares por categoria
                    quick_actions = {
                        "🎯 Vendas": [
                            "Produto mais vendido",
                            "Top 10 produtos",
                            "Ranking de vendas na une scr"
                        ],
                        "🏬 UNEs/Lojas": [
                            "Ranking de vendas por UNE",
                            "Top 5 produtos da une 261",
                            "Vendas totais de cada une"
                        ],
                        "🏪 Segmentos": [
                            "Qual segmento mais vendeu?",
                            "Top 10 produtos do segmento TECIDOS",
                            "Ranking dos segmentos"
                        ],
                        "📈 Análises": [
                            "Evolução de vendas dos últimos 12 meses",
                            "Produtos sem movimento",
                            "Análise ABC de produtos"
                        ]
                    }

                    for categoria, perguntas in quick_actions.items():
                        with st.expander(categoria, expanded=False):
                            for pergunta in perguntas:
                                if st.button(pergunta, key=f"qa_{pergunta}", use_container_width=True):
                                    # Adicionar pergunta ao session state
                                    st.session_state['pergunta_selecionada'] = pergunta

                    st.caption("💡 Clique para executar")

    # --- Estado da Sessão ---

    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": {
                    "type": "text",
                    "content": "Olá! Eu sou a Caçulinha, sua assistente de BI. O que vamos analisar hoje?"
                }
            }
        ]

    # --- NOTA: DirectQueryEngine removido - 100% IA ---
    # get_direct_query_engine() foi removido - sistema usa apenas agent_graph
    # Data: 12/10/2025

    # --- Funções de Interação ---
    def query_backend(user_input: str):
        '''Processa a query diretamente usando o backend integrado.'''
        # Log removido - informação confidencial do usuário

        # 📝 GARANTIR que a pergunta do usuário seja sempre preservada
        user_message = {"role": "user", "content": {"type": "text", "content": user_input}}
        st.session_state.messages.append(user_message)

        # ✅ PROCESSAMENTO DIRETO (sem spinners - mais rápido)
        try:
            # Inicializar agent_response
            agent_response = None
            start_time = datetime.now()

            # 💾 CACHE: Verificar cache antes de processar (com normalização)
            try:
                from core.business_intelligence.agent_graph_cache import get_agent_graph_cache
                cache = get_agent_graph_cache()

                # ✅ OTIMIZAÇÃO: Normalizar query para melhorar cache hit rate
                normalized_query = normalize_query_for_cache(user_input)

                # Tentar com query normalizada primeiro
                cached_result = cache.get(normalized_query)

                # Fallback: tentar com query original se não encontrar
                if not cached_result:
                    cached_result = cache.get(user_input)

                if cached_result:
                    logger.info(f"✅ Cache HIT! Query normalizada: '{normalized_query}'")
                else:
                    logger.info(f"❌ Cache MISS. Query normalizada: '{normalized_query}'")

            except Exception as cache_error:
                logger.warning(f"Erro ao acessar cache: {cache_error}")
                cached_result = None

            if cached_result:
                # ✅ CACHE HIT!
                agent_response = cached_result
                agent_response["method"] = "agent_graph_cached"
                agent_response["processing_time"] = (datetime.now() - start_time).total_seconds()

                # Debug para admins
                user_role = st.session_state.get('role', '')
                if user_role == 'admin':
                    with st.expander("💾 Cache Hit!"):
                        st.success(f"✅ Resposta recuperada do cache")
                        st.write(f"**Fonte:** {cached_result.get('cache_source', 'unknown')}")
            else:
                # ❌ CACHE MISS: Processar com agent_graph
                logger.info("Cache miss. Processando com agent_graph...")
                # ✅ CORREÇÃO CONTEXT7: Acessar backend via cache_resource (não session_state)
                backend = initialize_backend()
                if backend and 'agent_graph' in backend:
                    agent_graph = backend['agent_graph']

                    # ✅ CORREÇÃO: Construir o histórico completo de mensagens
                    from langchain_core.messages import AIMessage
                    HumanMessage = get_backend_module("HumanMessage")
                    
                    langchain_messages = []
                    for msg in st.session_state.get('messages', []):
                        if msg.get("role") == "user":
                            # ✅ CORREÇÃO: Verificar tipo antes de chamar .get()
                            content = msg.get("content", {})
                            if isinstance(content, dict):
                                user_text = content.get("content", "")
                            elif isinstance(content, list):
                                # Se for lista, converter para string
                                user_text = str(content)
                            else:
                                # Se for string ou outro tipo, usar diretamente
                                user_text = str(content)
                            langchain_messages.append(HumanMessage(content=user_text))
                        elif msg.get("role") == "assistant":
                            # Para o assistente, podemos simplificar para o conteúdo textual por enquanto
                            # já que o grafo espera principalmente o texto.
                            assistant_content = msg.get("content", {})
                            if isinstance(assistant_content, dict):
                                text_content = assistant_content.get("content", "")
                                if isinstance(text_content, dict): # Caso de content aninhado
                                    text_content = text_content.get("content", "...")
                                langchain_messages.append(AIMessage(content=str(text_content)))
                            elif isinstance(assistant_content, list):
                                # Se for lista, converter para string
                                langchain_messages.append(AIMessage(content=str(assistant_content)))
                            else:
                                langchain_messages.append(AIMessage(content=str(assistant_content)))

                    # A última mensagem (a atual) já foi adicionada à session_state, então usamos a lista completa
                    
                    # 🔒 SEGURANÇA: Mascarar PII no input antes de enviar ao grafo
                    masked_query = mask_pii(user_input)
                    if masked_query != user_input:
                        logger.info(f"🔒 PII mascarado no input: {user_input} -> {masked_query}")
                    
                    graph_input = {"messages": langchain_messages, "query": masked_query}

                    # ✅ OTIMIZAÇÃO CONTEXT7: Configurar thread_id para checkpointing
                    # Permite recovery automático e isolamento de sessões
                    config = {
                        "configurable": {
                            "thread_id": st.session_state.session_id  # Usa session_id existente
                        }
                    }
                    logger.info(f"🔄 Checkpointing ativado - thread_id: {st.session_state.session_id}")

                    # ✅ STREAMING IMPLEMENTATION: Executar agent_graph com feedback visual

                    try:
                        # Status de progresso
                        status_container = st.empty()
                        status_container.markdown("🔄 *Processando sua pergunta...*")

                        # Executar grafo em modo streaming
                        agent_response = None
                        initial_feedback_shown = False

                        for event in agent_graph.stream(graph_input, config=config):
                            # Identificar qual nó foi executado
                            current_node = list(event.keys())[0] if isinstance(event, dict) else "unknown"

                            # Atualizar status baseado no nó
                            if current_node == "reasoning":
                                status_container.markdown("🧠 *Analisando intenção...*")
                            elif current_node == "generate_initial_feedback":
                                # 🎯 NOVO: Exibir feedback inicial ao usuário
                                state_update = event.get(current_node, {})
                                feedback_msg = state_update.get("initial_feedback", "")
                                if feedback_msg and not initial_feedback_shown:
                                    # Limpar status e mostrar feedback
                                    status_container.empty()
                                    # Adicionar mensagem de feedback nas mensagens do chat
                                    st.session_state.messages.append({"role": "assistant", "content": feedback_msg})
                                    with st.chat_message("assistant"):
                                        st.markdown(feedback_msg)
                                    initial_feedback_shown = True
                                    # Atualizar status para mostrar que está processando
                                    status_container.markdown("⚙️ *Processando...*")
                            elif current_node == "conversational_response":
                                status_container.markdown("💬 *Gerando resposta conversacional...*")
                            elif current_node == "classify_intent":
                                status_container.markdown("🎯 *Classificando tipo de consulta...*")
                            elif current_node == "generate_parquet_query":
                                status_container.markdown("🔍 *Preparando consulta de dados...*")
                            elif current_node == "execute_query":
                                status_container.markdown("📊 *Consultando dados...*")
                            elif current_node == "generate_plotly_spec":
                                status_container.markdown("📈 *Gerando visualização...*")
                            elif current_node == "format_final_response":
                                status_container.markdown("✍️ *Formatando resposta...*")

                            # Verificar se temos uma resposta final no estado
                            if isinstance(event, dict):
                                state_update = event.get(current_node, {})
                                if "final_response" in state_update:
                                    agent_response = state_update["final_response"]

                        # Limpar status
                        status_container.empty()

                        # Verificar se obtivemos resposta
                        if not agent_response:
                            agent_response = {
                                "type": "error",
                                "content": "Não foi possível obter uma resposta do agente."
                            }

                        # 🔒 SEGURANÇA: Mascarar PII na resposta se for dict com content
                        if isinstance(agent_response, dict) and "content" in agent_response:
                            content = agent_response["content"]
                            if isinstance(content, str):
                                masked_content = mask_pii(content)
                                if masked_content != content:
                                    agent_response["content"] = masked_content
                                    logger.info(f"🔒 PII mascarado na resposta")
                                    pii_summary = get_pii_summary()
                                    if pii_summary:
                                        logger.warning(f"🔒 Tipos de PII mascarados: {pii_summary}")

                    except Exception as e:
                        logger.error(f"❌ Erro no streaming: {e}", exc_info=True)
                        agent_response = {"type": "error", "content": f"Erro ao processar: {str(e)}"}
                else:
                    # 🔧 DIAGNÓSTICO: Verificar por que agent_graph não está disponível
                    error_details = []

                    if not backend:
                        error_details.append("❌ Backend não inicializado")
                    elif 'agent_graph' not in backend:
                        error_details.append("❌ Agent Graph não encontrado no backend")
                        available_keys = list(backend.keys())
                        error_details.append(f"Componentes disponíveis: {', '.join(available_keys)}")

                    error_msg = "🤖 **Sistema de IA Indisponível**\n\n"
                    error_msg += "O sistema não conseguiu inicializar o agente de IA.\n\n"
                    error_msg += "**💡 Solução:**\n"
                    error_msg += "1. Recarregue a página (F5)\n"
                    error_msg += "2. Verifique sua conexão de internet\n"
                    error_msg += "3. Se o problema persistir, entre em contato com o suporte"

                    # Adicionar detalhes técnicos apenas para admins
                    user_role = st.session_state.get('role', '')
                    if user_role == 'admin' and error_details:
                        error_msg += "\n\n**🔧 Detalhes Técnicos (Admin):**\n"
                        error_msg += "\n".join(error_details)

                    agent_response = {
                        "type": "error",
                        "content": error_msg,
                        "user_query": user_input,
                        "method": "agent_graph_unavailable"
                    }

            # ✅ GARANTIR estrutura correta da resposta
            if agent_response:
                assistant_message = {"role": "assistant", "content": agent_response}
                st.session_state.messages.append(assistant_message)
            else:
                # Fallback se agent_response não foi definido
                error_message = {
                    "role": "assistant",
                    "content": {
                        "type": "error",
                        "content": "Erro ao processar consulta. Tente novamente.",
                        "user_query": user_input
                    }
                }
                st.session_state.messages.append(error_message)

            # Resposta processada silenciosamente

        except Exception as e:
            # Erro fatal na invocação do agente. Parar a execução e notificar o usuário.
            logger.critical(f"Erro fatal ao invocar o backend: {e}", exc_info=True)
            st.error("🚨 Desculpe, ocorreu um erro crítico no sistema.")
            st.info("A equipe de desenvolvimento foi notificada. Por favor, atualize a página e tente novamente.")
                
            # Adiciona uma mensagem de erro clara ao chat para o usuário
            error_content = {
                "type": "text",
                "content": "❌ **Erro Interno**\n\nOcorreu uma falha inesperada ao processar sua solicitação. A equipe de suporte já foi notificada."
            }
            st.session_state.messages.append({"role": "assistant", "content": error_content})
            # Não fazer st.rerun() aqui para que o erro seja visível.

        # Log the query and its outcome
        backend = initialize_backend()
        if backend and backend.get("query_history"):
            query_history = backend["query_history"]
            
            # Default agent_response to an empty dict if it's not a dict
            if not isinstance(agent_response, dict):
                agent_response = {}

            # Safely determine if the main operation was successful
            is_success = agent_response.get("type") != "error"

            # Safely get result count from chart data if it exists
            results_count = 0
            if is_success and isinstance(agent_response.get("result"), dict):
                chart_data = agent_response["result"].get("chart_data", {})
                if isinstance(chart_data, dict):
                    results_count = len(chart_data.get("x", []))
            
            # Safely get error message
            error_message = None
            if not is_success:
                error_message = agent_response.get("content")
            
            # Get processing time from the response if available
            processing_time = agent_response.get("processing_time", 0.0)

            query_history.add_query(
                query=user_input,
                session_id=st.session_state.session_id,
                success=is_success,
                results_count=results_count,
                error=error_message,
                processing_time=processing_time
            )

        st.rerun()

    # --- Funções de Streaming ---
    def stream_text(text: str, speed: float = 0.01):
        """
        Generator para criar efeito de digitação (typewriter effect).
        Yields: caracteres um por um com delay entre eles.
        """
        import time
        for char in text:
            yield char
            time.sleep(speed)

    # --- Renderização da Interface ---
    # 🔍 DEBUG: Mostrar histórico de mensagens na sidebar (apenas para admins)
    user_role = st.session_state.get('role', '')
    if user_role == 'admin':
        with st.sidebar:
            st.write(f"**Total de mensagens:** {len(st.session_state.messages)}")
            if st.checkbox("Mostrar histórico debug"):
                for i, msg in enumerate(st.session_state.messages):
                    st.write(f"**{i+1}. {msg['role'].title()}:**")
                    content_preview = str(msg.get('content', {}))[:100] + "..." if len(str(msg.get('content', {}))) > 100 else str(msg.get('content', {}))
                    st.write(f"{content_preview}")

    # 💬 RENDERIZAR histórico de conversas
    for i, msg in enumerate(st.session_state.messages):
        try:
            # 🎨 CUSTOMIZAÇÃO: Usar logo Caçula otimizada para chat (53x80px)
            import os
            logo_chat_path = os.path.join(os.getcwd(), "assets", "images", "cacula_logo_chat.png")

            if msg["role"] == "assistant" and os.path.exists(logo_chat_path):
                # Usar logo Caçula otimizada para assistente (não cortada)
                with st.chat_message(msg["role"], avatar=logo_chat_path):
                    response_data = msg.get("content", {})
            else:
                # Usar avatar padrão
                with st.chat_message(msg["role"]):
                    response_data = msg.get("content", {})

            # ✅ Garantir que response_data seja um dicionário
            if not isinstance(response_data, dict):
                response_data = {"type": "text", "content": str(response_data)}

            response_type = response_data.get("type", "text")
            content = response_data.get("content", "Conteúdo não disponível")

            # 🔍 DEBUG: Log de renderização (removido print para evitar problemas)
            # if msg["role"] == "user":
            #     print(f"RENDERING USER MSG {i+1}: '{content}'")
            # else:
            #     print(f"RENDERING ASSISTANT MSG {i+1}: Type={response_type}")
            
            # 📈 RENDERIZAR GRÁFICOS
            if response_type == "chart":
                # ⚡ Imports sob demanda apenas quando necessário
                import plotly.graph_objects as go

                # 📝 Mostrar contexto da pergunta que gerou o gráfico
                user_query = response_data.get("user_query")
                if user_query:
                    st.caption(f"📝 Pergunta: {user_query}")

                try:
                    # Verificar se chart_data está em result ou no content diretamente
                    if 'result' in response_data and 'chart_data' in response_data['result']:
                        # Nosso formato personalizado
                        chart_data = response_data['result']['chart_data']

                        # Criar gráfico melhorado com cores e interatividade
                        chart_type = chart_data.get("type", "bar")
                        x_data = chart_data.get("x", [])
                        y_data = chart_data.get("y", [])
                        colors = chart_data.get("colors", None)

                        # Configurações comuns
                        height = chart_data.get("height", 500)
                        margin = chart_data.get("margin", {"l": 60, "r": 60, "t": 80, "b": 100})

                        # Criar figura baseado no tipo
                        fig = go.Figure()

                        if chart_type == "bar" and x_data and y_data:
                            # Gráfico de barras
                            fig.add_trace(go.Bar(
                                x=x_data,
                                y=y_data,
                                marker_color=colors if colors else '#1f77b4',
                                text=[f'{int(val):,}' for val in y_data],
                                textposition='outside',
                                name='Vendas',
                                hovertemplate='<b>%{x}</b><br>Vendas: %{y:,.0f}<extra></extra>'
                            ))

                            fig.update_layout(
                                xaxis_title="Categoria",
                                yaxis_title="Valor",
                                xaxis=dict(tickangle=-45),
                                yaxis=dict(gridcolor='rgba(128,128,128,0.2)')
                            )

                        elif chart_type == "pie" and x_data and y_data:
                            # Gráfico de pizza
                            fig.add_trace(go.Pie(
                                labels=x_data,
                                values=y_data,
                                textinfo='label+percent',
                                hovertemplate='<b>%{label}</b><br>Vendas: %{value:,.0f}<br>Percentual: %{percent}<extra></extra>'
                            ))
                            height = 600

                        elif chart_type == "line" and x_data and y_data:
                            # Gráfico de linha
                            fig.add_trace(go.Scatter(
                                x=x_data,
                                y=y_data,
                                mode='lines+markers',
                                line=dict(color=colors if colors else '#1f77b4', width=2),
                                marker=dict(size=8),
                                name='Tendência',
                                hovertemplate='<b>%{x}</b><br>Valor: %{y:,.0f}<extra></extra>'
                            ))

                            fig.update_layout(
                                xaxis_title="Período",
                                yaxis_title="Valor",
                                yaxis=dict(gridcolor='rgba(128,128,128,0.2)')
                            )

                        elif chart_type == "scatter" and x_data and y_data:
                            # Gráfico de dispersão
                            fig.add_trace(go.Scatter(
                                x=x_data,
                                y=y_data,
                                mode='markers',
                                marker=dict(
                                    size=10,
                                    color=colors if colors else y_data,
                                    colorscale='Viridis',
                                    showscale=True
                                ),
                                hovertemplate='<b>%{x}</b><br>Valor: %{y:,.0f}<extra></extra>'
                            ))

                            fig.update_layout(
                                xaxis_title="X",
                                yaxis_title="Y"
                            )

                        elif chart_type == "area" and x_data and y_data:
                            # Gráfico de área
                            fig.add_trace(go.Scatter(
                                x=x_data,
                                y=y_data,
                                fill='tozeroy',
                                mode='lines',
                                line=dict(color=colors if colors else '#1f77b4'),
                                name='Área',
                                hovertemplate='<b>%{x}</b><br>Valor: %{y:,.0f}<extra></extra>'
                            ))

                            fig.update_layout(
                                xaxis_title="Período",
                                yaxis_title="Valor",
                                yaxis=dict(gridcolor='rgba(128,128,128,0.2)')
                            )

                        elif chart_type == "histogram" and y_data:
                            # Histograma
                            fig.add_trace(go.Histogram(
                                x=y_data,
                                marker_color=colors if colors else '#1f77b4',
                                name='Distribuição'
                            ))

                            fig.update_layout(
                                xaxis_title="Valor",
                                yaxis_title="Frequência"
                            )

                        elif chart_type == "box" and y_data:
                            # Box plot
                            fig.add_trace(go.Box(
                                y=y_data,
                                name='Distribuição',
                                marker_color=colors if colors else '#1f77b4',
                                boxmean='sd'
                            ))

                            fig.update_layout(
                                yaxis_title="Valor"
                            )

                        elif chart_type == "heatmap" and x_data and y_data:
                            # Heatmap (requer dados em formato matriz)
                            z_data = chart_data.get("z", [[]])
                            fig.add_trace(go.Heatmap(
                                x=x_data,
                                y=y_data,
                                z=z_data,
                                colorscale='Viridis'
                            ))

                            fig.update_layout(
                                xaxis_title="X",
                                yaxis_title="Y"
                            )

                        elif chart_type == "funnel" and x_data and y_data:
                            # Funil
                            fig.add_trace(go.Funnel(
                                x=y_data,
                                y=x_data,
                                textinfo="value+percent total",
                                marker=dict(color=colors if colors else None)
                            ))

                        elif x_data and y_data:
                            # Fallback: tentar renderizar como barra
                            st.warning(f"⚠️ Tipo '{chart_type}' usando renderização padrão (barras)")
                            fig.add_trace(go.Bar(x=x_data, y=y_data))
                        else:
                            st.error("Dados do gráfico não disponíveis")
                            continue

                        # Layout comum para todos os gráficos
                        fig.update_layout(
                            title={
                                'text': response_data.get("title", "Gráfico"),
                                'x': 0.5,
                                'xanchor': 'center',
                                'font': {'size': 16, 'family': 'Arial Black'}
                            },
                            height=height,
                            margin=margin,
                            showlegend=chart_type in ["line", "area", "scatter"],
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(family="Arial, sans-serif", size=12, color="#333"),
                            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
                        )
                    else:
                        # Formato Plotly padrão (já completo)
                        if isinstance(content, str):
                            import json
                            chart_data = json.loads(content)
                        else:
                            chart_data = content

                        # Usar gráfico Plotly diretamente
                        fig = go.Figure(chart_data)

                    # Renderizar gráfico com chave única para evitar conflitos
                    import hashlib
                    import time

                    # Gerar chave única baseada na query e timestamp
                    user_query = response_data.get("user_query", "")
                    chart_key = hashlib.md5(f"{user_query}_{time.time()}".encode()).hexdigest()[:8]

                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True}, key=f"chart_{chart_key}")

                    # Botão para salvar gráfico
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("💾 Salvar no Dashboard", key=f"save_chart_{chart_key}"):
                            if "dashboard_charts" not in st.session_state:
                                st.session_state.dashboard_charts = []

                            chart_data = {
                                "title": response_data.get("title", "Gráfico"),
                                "type": "chart",
                                "output": fig,
                                "query": user_query,
                                "timestamp": datetime.now().isoformat()
                            }
                            st.session_state.dashboard_charts.append(chart_data)
                            st.success("✅ Gráfico salvo no Dashboard!")

                    with col2:
                        # Salvar gráfico em arquivo
                        import os
                        os.makedirs("reports/charts", exist_ok=True)

                        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                        title_safe = response_data.get("title", "grafico").replace(" ", "_")[:50]

                        # Salvar como HTML (sempre funciona)
                        filename_html = f"reports/charts/{title_safe}_{timestamp_str}.html"
                        fig.write_html(filename_html)

                        # Tentar salvar como PNG (requer kaleido)
                        filename_png = f"reports/charts/{title_safe}_{timestamp_str}.png"
                        try:
                            fig.write_image(filename_png, width=1200, height=800)
                            st.download_button(
                                label="📥 Download PNG",
                                data=open(filename_png, "rb").read(),
                                file_name=f"{title_safe}.png",
                                mime="image/png",
                                key=f"download_png_{chart_key}"
                            )
                        except Exception as e:
                            # Se falhar PNG, oferecer HTML
                            st.download_button(
                                label="📥 Download HTML",
                                data=open(filename_html, "r", encoding="utf-8").read(),
                                file_name=f"{title_safe}.html",
                                mime="text/html",
                                key=f"download_html_{chart_key}"
                            )
                            if st.session_state.get('role') == 'admin':
                                st.caption(f"ℹ️ PNG não disponível: {str(e)[:100]}")

                    # Mostrar informações adicionais
                    result_info = response_data.get("result", {})
                    if "total_unes" in result_info:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total de UNEs", result_info.get("total_unes", 0))
                        with col2:
                            st.metric("UNEs Exibidas", result_info.get("unes_exibidas", 0))
                        with col3:
                            st.metric("Total de Vendas", f"{result_info.get('total_vendas', 0):,.0f}")

                    # Interatividade: botões para drill-down por UNE (se aplicável)
                    if "produto_codigo" in result_info and result_info.get("total_unes", 0) > 1:
                        st.write("🔍 **Análise Detalhada por UNE:**")
                        st.info("💡 **Dica:** Para ver vendas mensais de uma UNE específica, pergunte: 'gráfico de barras do produto [código] na une [número]'")

                    st.success("✅ Gráfico gerado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao renderizar gráfico: {e}")
                    st.write("Dados do gráfico:", content)
            elif response_type == "multiple_charts" and isinstance(content, list):
                # ✅ CORREÇÃO: Renderizar múltiplos gráficos Plotly
                user_query = response_data.get("user_query")
                if user_query:
                    st.caption(f"📝 Pergunta: {user_query}")

                try:
                    import plotly.io as pio
                    import json

                    st.info(f"📊 {len(content)} gráficos gerados:")

                    for i, chart_json in enumerate(content):
                        # Parse JSON para Figure
                        fig = pio.from_json(chart_json)

                        # Exibir subtítulo para cada gráfico
                        chart_title = fig.layout.title.text if fig.layout.title and fig.layout.title.text else f"Gráfico {i+1}"
                        st.subheader(chart_title)

                        # Renderizar o gráfico
                        st.plotly_chart(fig, use_container_width=True, key=f"chart_{i}_{uuid.uuid4()}")

                    st.success(f"✅ {len(content)} gráficos gerados com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao renderizar múltiplos gráficos: {e}")
                    st.write("Dados dos gráficos:", content)
            elif response_type == "data" and isinstance(content, list):
                # 📝 Mostrar contexto da pergunta que gerou os dados
                user_query = response_data.get("user_query")
                if user_query:
                    st.caption(f"📝 Pergunta: {user_query}")

                if content:
                    # 💰 FORMATAÇÃO BRASILEIRA: Aplicar formatação R$ automaticamente
                    try:
                        from core.utils.dataframe_formatter import format_dataframe_for_display, create_download_csv

                        df_original = pd.DataFrame(content)

                        # Debug: Mostrar colunas ANTES da formatação (apenas para admin)
                        user_role = st.session_state.get('role', '')


                        df_formatado = format_dataframe_for_display(df_original, auto_detect=True)

                        # Preparar dados para download (necessário antes do DataFrame interativo)
                        csv_data, csv_filename = create_download_csv(df_original, filename_prefix="export")

                        # Debug: Confirmar formatação aplicada
                        if user_role == 'admin':
                            st.caption(f"✅ Formatação brasileira aplicada (R$, separadores de milhar)")

                        # Exibir DataFrame formatado
                        # ✅ Configuração avançada baseada em Context7 (/streamlit/docs)

                        # Configuração de colunas com formatação personalizada
                        column_config = {}

                        # Detectar e configurar colunas monetárias
                        for col in df_formatado.columns:
                            col_lower = str(col).lower()

                            # Colunas de vendas/valores monetários
                            if any(kw in col_lower for kw in ['venda', 'preco', 'liquido', 'valor', 'custo', 'mes_']):
                                column_config[col] = st.column_config.TextColumn(
                                    col,
                                    help=f"Valores em Reais (R$)",
                                    width="medium"
                                )

                            # Colunas de estoque/quantidades
                            elif any(kw in col_lower for kw in ['estoque', 'quantidade', 'qtd']):
                                column_config[col] = st.column_config.TextColumn(
                                    col,
                                    help=f"Quantidade em unidades",
                                    width="small"
                                )

                            # Colunas de texto (produto, categoria, etc)
                            elif any(kw in col_lower for kw in ['nome', 'descricao', 'categoria', 'segmento', 'fabricante']):
                                column_config[col] = st.column_config.TextColumn(
                                    col,
                                    help=f"Informação textual",
                                    width="large"
                                )

                        # Exibir DataFrame com seleção interativa
                        event = st.dataframe(
                            df_formatado,
                            use_container_width=True,
                            height=600,  # Altura fixa para scroll completo
                            hide_index=True,  # Ocultar índice numérico (melhor UX)
                            column_config=column_config,  # Formatação personalizada por coluna
                            row_height=35,  # Altura compacta para melhor densidade visual
                            on_select="rerun",  # Recarregar app quando linhas forem selecionadas
                            selection_mode="multi-row",  # Permitir seleção de múltiplas linhas
                            key=f"dataframe_main_{i}"  # ✅ FIX: Key único para evitar erro de ID duplicado
                        )

                        # Mostrar linhas selecionadas (se houver)
                        if event and hasattr(event, 'selection') and event.selection.get('rows'):
                            selected_rows = event.selection['rows']

                            if selected_rows:
                                st.info(f"🔍 **{len(selected_rows)} linha(s) selecionada(s)**")

                                # Mostrar dados das linhas selecionadas
                                with st.expander("📋 Ver detalhes das linhas selecionadas", expanded=False):
                                    selected_data = df_formatado.iloc[selected_rows]
                                    st.dataframe(
                                        selected_data,
                                        use_container_width=True,
                                        hide_index=True,
                                        column_config=column_config,
                                        key=f"dataframe_selected_{i}"  # ✅ FIX: Key único
                                    )

                                    # Botão para exportar apenas selecionados
                                    csv_selected = selected_data.to_csv(index=False, encoding='utf-8-sig')
                                    st.download_button(
                                        label="📥 Baixar linhas selecionadas (CSV)",
                                        data=csv_selected,
                                        file_name=f"selecionados_{csv_filename}",
                                        mime="text/csv",
                                        key=f"download_selected_{uuid.uuid4()}"
                                    )

                        # Botão de download com formatação (todos os dados)
                        st.download_button(
                            label="📥 Baixar CSV (formatado)",
                            data=csv_data,
                            file_name=csv_filename,
                            mime="text/csv",
                            key=f"download_csv_{uuid.uuid4()}"
                        )

                        st.info(f"📊 {len(content)} registros encontrados")
                    except Exception as e:
                        logger.warning(f"Erro ao formatar DataFrame: {e}")
                        # Fallback: exibir sem formatação (com recursos básicos)
                        st.dataframe(
                            pd.DataFrame(content),
                            use_container_width=True,
                            height=600,
                            hide_index=True,
                            row_height=35,  # Mesma densidade visual
                            on_select="rerun",
                            selection_mode="multi-row",
                            key=f"dataframe_fallback_{i}"  # ✅ FIX: Key único
                        )
                        st.info(f"📊 {len(content)} registros encontrados")
                else:
                    st.warning("⚠️ Nenhum dado encontrado para a consulta.")
            elif response_type == "clarification":
                st.markdown(content.get("message"))
                choices = content.get("choices", {})
                for choice_category, choice_list in choices.items():
                    for choice in choice_list:
                        if st.button(choice, key=f"btn_{choice}_{uuid.uuid4()}"):
                            query_backend(choice)
            elif response_type == "text_with_data":
                # 🆕 TEXTO COM OPÇÃO DE DOWNLOAD
                user_query = response_data.get("user_query")
                if user_query and msg["role"] == "assistant":
                    st.caption(f"📝 Pergunta: {user_query}")

                # Renderizar conteúdo textual
                if isinstance(content, str):
                    st.markdown(content, unsafe_allow_html=True)
                else:
                    st.markdown(str(content), unsafe_allow_html=True)

                # 📥 BOTÕES DE DOWNLOAD
                download_data = response_data.get("download_data", [])
                download_filename = response_data.get("download_filename", "dados_export")

                if download_data and isinstance(download_data, list) and len(download_data) > 0:
                    st.markdown("---")
                    st.markdown("### 📥 Exportar Dados")

                    # Converter para DataFrame
                    df_export = pd.DataFrame(download_data)

                    # Layout de colunas para botões
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        # Download CSV
                        csv_data = df_export.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="📄 Baixar CSV",
                            data=csv_data,
                            file_name=f"{download_filename}.csv",
                            mime="text/csv",
                            key=f"csv_{i}_{download_filename}",
                            help="Exportar dados em formato CSV (compatível com Excel)"
                        )

                    with col2:
                        # Download Excel
                        from io import BytesIO
                        buffer = BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                            df_export.to_excel(writer, index=False, sheet_name='Dados')
                        excel_data = buffer.getvalue()

                        st.download_button(
                            label="📊 Baixar Excel",
                            data=excel_data,
                            file_name=f"{download_filename}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"excel_{i}_{download_filename}",
                            help="Exportar dados em formato Excel (.xlsx)"
                        )

                    with col3:
                        # Download JSON
                        import json
                        json_data = json.dumps(download_data, indent=2, ensure_ascii=False)
                        st.download_button(
                            label="🔧 Baixar JSON",
                            data=json_data,
                            file_name=f"{download_filename}.json",
                            mime="application/json",
                            key=f"json_{i}_{download_filename}",
                            help="Exportar dados em formato JSON (para desenvolvedores)"
                        )

                    # Informação sobre os dados
                    st.caption(f"📊 Total de registros: {len(df_export):,} | Colunas: {', '.join(df_export.columns[:5])}{'...' if len(df_export.columns) > 5 else ''}")

            else:
                # 📝 Para respostas de texto, também mostrar contexto se disponível
                user_query = response_data.get("user_query")
                if user_query and msg["role"] == "assistant":
                    st.caption(f"📝 Pergunta: {user_query}")

                # ✅ STREAMING: Renderizar com efeito de digitação para novas mensagens
                is_last_message = (i == len(st.session_state.messages) - 1)

                if isinstance(content, str):
                    # Caso normal: content é string
                    if is_last_message and msg["role"] == "assistant":
                        # ✅ NOVA MENSAGEM: Streaming (typewriter effect)
                        st.write_stream(stream_text(content, speed=0.005))
                    else:
                        # Mensagem antiga do histórico: renderizar direto
                        st.markdown(content)
                elif isinstance(content, dict):
                    # Se content for dict, tentar extrair mensagem
                    if "message" in content:
                        if is_last_message and msg["role"] == "assistant":
                            st.write_stream(stream_text(content["message"], speed=0.005))
                        else:
                            st.markdown(content["message"])
                    elif "text" in content:
                        if is_last_message and msg["role"] == "assistant":
                            st.write_stream(stream_text(content["text"], speed=0.005))
                        else:
                            st.markdown(content["text"])
                    else:
                        # Último recurso: mostrar JSON formatado
                        st.warning("⚠️ Resposta em formato não esperado:")
                        st.json(content)
                else:
                    # Converter para string
                    text_content = str(content)
                    if is_last_message and msg["role"] == "assistant":
                        st.write_stream(stream_text(text_content, speed=0.005))
                    else:
                        st.markdown(text_content)

                # ✅ DEBUG PARA ADMINS: Mostrar estrutura da resposta
                if msg["role"] == "assistant" and st.session_state.get('role') == 'admin':
                    with st.expander("🔍 Debug (Admin)", expanded=False):
                        st.write("**Response Data Structure:**")
                        st.json(response_data)

                        st.write("**Response Type:**", response_type)
                        st.write("**Content Type:**", type(content).__name__)

                        if isinstance(content, str):
                            st.write("**Content Length:**", len(content))
                        elif isinstance(content, (list, dict)):
                            st.write("**Content Keys/Length:**",
                                    list(content.keys()) if isinstance(content, dict) else len(content))

                # ✅ FEEDBACK REMOVIDO - Interface limpa conforme solicitado

        except Exception as e:
            # ❌ Tratamento de erro na renderização
            st.error(f"Erro ao renderizar mensagem {i+1}: {str(e)}")
            st.write(f"Dados da mensagem: {msg}")

    # Verificar se há uma pergunta selecionada da página de exemplos
    if 'pergunta_selecionada' in st.session_state and st.session_state.pergunta_selecionada:
        pergunta = st.session_state.pergunta_selecionada
        st.session_state.pergunta_selecionada = None  # Limpar para não processar novamente
        query_backend(pergunta)
        st.rerun()

    with st.sidebar:
        st.divider()
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.role = ""
            # Clear chat history on logout
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": {
                        "type": "text",
                        "content": "Você foi desconectado. Faça login para continuar."
                    }
                }
            ]
            st.rerun()

    if prompt := st.chat_input("Faça sua pergunta..."):
        query_backend(prompt)
