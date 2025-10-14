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
from datetime import datetime

# Configurar logging - APENAS para logs de erro críticos
# Usuários finais não veem logs técnicos
logging.basicConfig(
    level=logging.ERROR,  # Apenas erros
    format='%(message)s',
    stream=sys.stdout
)

# Configurar logger específico
logger = logging.getLogger("streamlit_app")
logger.setLevel(logging.ERROR)  # Apenas erros

# Silenciar logs de bibliotecas externas
logging.getLogger("faiss").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("core").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

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
        # DirectQueryEngine desabilitado - 100% IA (12/10/2025)
        # elif module_name == "DirectQueryEngine":
        #     from core.business_intelligence.direct_query_engine import DirectQueryEngine
        #     BACKEND_MODULES[module_name] = DirectQueryEngine

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
else:
    # --- Configuração da Página ---
    st.set_page_config(page_title="Assistente de Negócios", page_icon="📊", layout="wide")
    st.title("📊 Assistente de Negócios")

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

            # Debug 5: Inicializar HybridDataAdapter (SQL Server + Parquet fallback)
            debug_info.append("Inicializando HybridDataAdapter...")
            import os
            from core.connectivity.hybrid_adapter import HybridDataAdapter

            # Inicializar adapter híbrido (tenta SQL Server, fallback para Parquet)
            data_adapter = HybridDataAdapter()
            adapter_status = data_adapter.get_status()

            debug_info.append(f"✅ HybridDataAdapter OK - Fonte: {adapter_status['current_source'].upper()}")

            # Validar que temos dados (via Parquet que sempre existe)
            import pandas as pd
            parquet_path = os.path.join(os.getcwd(), "data", "parquet", "admmat.parquet")

            if os.path.exists(parquet_path):
                # Usar o adapter para obter informações de forma mais eficiente
                adapter_info = data_adapter.get_status()
                if adapter_info.get('current_source') == 'parquet':
                    # ⚡ OTIMIZAÇÃO: NÃO chamar get_schema() pois carrega 1.1M linhas!
                    # Apenas reportar que o Parquet está disponível
                    debug_info.append(f"✅ Dataset: Parquet disponível em {parquet_path}")
                else: # Se for SQL
                    debug_info.append("✅ Dataset: Conectado ao SQL Server")
            else:
                debug_info.append("⚠️ Parquet não encontrado, usando apenas SQL Server")

            # Mostrar status da fonte de dados no sidebar APENAS para admins
            user_role = st.session_state.get('role', '')
            if user_role == 'admin':
                with st.sidebar:
                    fonte_icon = "🗄️" if adapter_status['current_source'] == 'sqlserver' else "📦"
                    fonte_nome = "SQL Server" if adapter_status['current_source'] == 'sqlserver' else "Parquet"

                    info_text = f"**{fonte_icon} Fonte de Dados: {fonte_nome}**\n\n"

                    if adapter_status['sql_enabled']:
                        info_text += f"SQL Server: {'✅ Conectado' if adapter_status['sql_available'] else '❌ Indisponível'}\n"

                    info_text += f"Parquet Fallback: {'✅ Ativo' if adapter_status['fallback_enabled'] else '❌ Desativado'}\n"

                    # ⚡ OTIMIZAÇÃO: Apenas mostrar informações se DataFrame já estiver carregado
                    # NÃO forçar carregamento aqui para evitar travamentos
                    try:
                        if hasattr(data_adapter, '_dataframe') and data_adapter._dataframe is not None:
                            df = data_adapter._dataframe
                            info_text += f"\n**Dataset:**\n"
                            info_text += f"- {len(df):,} produtos\n"
                            if 'une_nome' in df.columns:
                                info_text += f"- {df['une_nome'].nunique()} UNEs\n\n"
                                info_text += f"**UNEs:** {', '.join(sorted(df['une_nome'].unique())[:5])}..."
                        else:
                            info_text += f"\n**Dataset:** Não carregado ainda (lazy loading ativo)"
                    except Exception as e:
                        logger.debug(f"Não foi possível obter informações do dataset: {e}")

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

    # Inicializar backend
    backend_components = initialize_backend()

    # Salvar no session_state para acesso em outras partes
    if backend_components:
        st.session_state.backend_components = backend_components
        user_role = st.session_state.get('role', '')
        if user_role == 'admin':
            with st.sidebar:
                st.success("✅ Backend inicializado!")
    else:
        st.session_state.backend_components = None
        user_role = st.session_state.get('role', '')
        if user_role == 'admin':
            with st.sidebar:
                st.error("❌ Backend falhou")

    # --- Logout Button ---
    with st.sidebar:
        st.write(f"Bem-vindo, {st.session_state.get('username', '')}!")
        st.write(f"DEBUG: Role do usuário (sidebar): {st.session_state.get('role', '')}") # LINHA DE DEBUG
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

    # --- Modo de Consulta: 100% IA ---
    with st.sidebar:
        st.divider()
        st.subheader("🤖 Análise Inteligente com IA")

        st.info("""
            ✨ **Sistema 100% IA Ativo**
            - Análise inteligente de dados
            - Qualquer tipo de pergunta
            - Respostas precisas e confiáveis
            - Processamento otimizado
        """)

        st.caption("💡 Alimentado por IA avançada (Gemini 2.5)")

    # --- Painel de Controle (Admin) ---
    user_role = st.session_state.get('role', '')
    if user_role == 'admin':
        with st.sidebar:
            st.divider()
            with st.expander("⚙️ Painel de Controle (Admin)", expanded=False):
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

    # --- Quick Actions (Perguntas Rápidas) - Apenas para Admin ---
    user_role = st.session_state.get('role', '')
    if user_role == 'admin':
        with st.sidebar:
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
                                st.rerun()

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
                    "content": "Olá! Como posso te ajudar?"
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

        with st.spinner("🤖 Processando com IA..."):
            try:
                # Inicializar agent_response
                agent_response = None
                start_time = datetime.now()

                # NOTA: DirectQueryEngine desabilitado - usando 100% IA (agent_graph)
                # Motivo: Taxa de acerto ~25% vs 100% com IA
                # Data: 12/10/2025

                # ✅ SEMPRE usar agent_graph (100% IA)
                if True:  # Simplificado para sempre processar com IA
                    # 💾 CACHE: Verificar cache antes de processar
                    try:
                        from core.business_intelligence.agent_graph_cache import get_agent_graph_cache
                        cache = get_agent_graph_cache()
                        cached_result = cache.get(user_input)
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
                        if st.session_state.backend_components and 'agent_graph' in st.session_state.backend_components:
                            agent_graph = st.session_state.backend_components['agent_graph']

                            # ✅ CORREÇÃO: Usar HumanMessage do LangChain, não dict
                            HumanMessage = get_backend_module("HumanMessage")
                            graph_input = {"messages": [HumanMessage(content=user_input)], "query": user_input}

                            # 🔧 TIMEOUT IMPLEMENTATION: Executar agent_graph com timeout
                            import threading
                            import queue

                            result_queue = queue.Queue()
                            timeout_seconds = 30  # 30 segundos de timeout

                            def invoke_agent_graph():
                                try:
                                    final_state = agent_graph.invoke(graph_input)
                                    result_queue.put(("success", final_state))
                                except Exception as e:
                                    result_queue.put(("error", str(e)))

                            # Executar em thread separada
                            thread = threading.Thread(target=invoke_agent_graph, daemon=True)
                            thread.start()
                            thread.join(timeout=timeout_seconds)

                            # Verificar resultado
                            if thread.is_alive():
                                # ⏰ TIMEOUT: Agent graph não respondeu a tempo
                                agent_response = {
                                    "type": "error",
                                    "content": f"⏰ **Tempo Limite Excedido**\n\n"
                                               f"O processamento da sua consulta demorou muito tempo (>{timeout_seconds}s).\n\n"
                                               f"**Sugestões:**\n"
                                               f"- Tente uma consulta mais específica\n"
                                               f"- Simplifique a pergunta\n"
                                               f"- Verifique sua conexão de internet",
                                    "user_query": user_input,
                                    "method": "agent_graph_timeout"
                                }
                                logger.warning(f"Agent graph timeout após {timeout_seconds}s para query: {user_input}")
                            else:
                                # ✅ SUCESSO ou ERRO: Obter resultado da thread
                                try:
                                    result_type, result = result_queue.get_nowait()

                                    if result_type == "success":
                                        final_state = result
                                        agent_response = final_state.get("final_response", {})
                                        agent_response["method"] = "agent_graph"
                                        agent_response["processing_time"] = (datetime.now() - start_time).total_seconds()

                                        # 💾 Salvar no cache para futuras queries similares
                                        try:
                                            cache.set(user_input, agent_response, metadata={"timestamp": datetime.now().isoformat()})
                                        except Exception as cache_save_error:
                                            logger.warning(f"Erro ao salvar no cache: {cache_save_error}")

                                        # Debug para admins
                                        user_role = st.session_state.get('role', '')
                                        if user_role == 'admin':
                                            with st.expander("🔍 Debug: agent_graph"):
                                                st.write(f"**Tempo de processamento:** {agent_response['processing_time']:.2f}s")
                                                st.write(f"**Tipo de resposta:** {agent_response.get('type', 'unknown')}")
                                    else:
                                        # ❌ ERRO na execução do agent_graph
                                        agent_response = {
                                            "type": "error",
                                            "content": f"❌ **Erro no Processamento**\n\n{result}\n\n"
                                                       f"Por favor, tente reformular sua consulta.",
                                            "user_query": user_input,
                                            "method": "agent_graph_error"
                                        }
                                        logger.error(f"Erro no agent_graph: {result}")
                                except queue.Empty:
                                    # Caso improvável: thread terminou mas sem resultado
                                    agent_response = {
                                        "type": "error",
                                        "content": "Erro inesperado ao processar consulta.",
                                        "user_query": user_input,
                                        "method": "agent_graph_empty"
                                    }
                        else:
                            # 🔧 DIAGNÓSTICO: Verificar por que agent_graph não está disponível
                            error_details = []

                            if not st.session_state.backend_components:
                                error_details.append("❌ Backend não inicializado")
                            elif 'agent_graph' not in st.session_state.backend_components:
                                error_details.append("❌ Agent Graph não encontrado no backend")
                                available_keys = list(st.session_state.backend_components.keys())
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
        if st.session_state.backend_components and st.session_state.backend_components.get("query_history"):
            query_history = st.session_state.backend_components["query_history"]
            
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
            elif response_type == "data" and isinstance(content, list):
                # 📝 Mostrar contexto da pergunta que gerou os dados
                user_query = response_data.get("user_query")
                if user_query:
                    st.caption(f"📝 Pergunta: {user_query}")

                if content:
                    st.dataframe(pd.DataFrame(content))
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
            else:
                # 📝 Para respostas de texto, também mostrar contexto se disponível
                user_query = response_data.get("user_query")
                if user_query and msg["role"] == "assistant":
                    st.caption(f"📝 Pergunta: {user_query}")

                # ✅ CORREÇÃO: Garantir renderização correta do content
                if isinstance(content, str):
                    # Caso normal: content é string
                    st.markdown(content)
                elif isinstance(content, dict):
                    # Se content for dict, tentar extrair mensagem
                    if "message" in content:
                        st.markdown(content["message"])
                    elif "text" in content:
                        st.markdown(content["text"])
                    else:
                        # Último recurso: mostrar JSON formatado
                        st.warning("⚠️ Resposta em formato não esperado:")
                        st.json(content)
                else:
                    # Converter para string
                    st.markdown(str(content))

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

                # ========================================
                # 🎯 FASE 1: FEEDBACK SYSTEM
                # ========================================
                if msg["role"] == "assistant" and response_type not in ["error", "clarification"]:
                    try:
                        from ui.feedback_component import render_feedback_buttons

                        render_feedback_buttons(
                            query=response_data.get("user_query", ""),
                            code=response_data.get("code", ""),
                            result_rows=response_data.get("result_rows", 0),
                            session_id=st.session_state.session_id,
                            user_id=st.session_state.get('username', 'anonymous'),
                            key_suffix=f"msg_{i}"
                        )
                    except Exception as feedback_error:
                        # Feedback não crítico - não bloquear UI
                        if st.session_state.get('role') == 'admin':
                            st.caption(f"⚠️ Feedback indisponível: {feedback_error}")

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

    if prompt := st.chat_input("Faça sua pergunta..."):
        query_backend(prompt)
