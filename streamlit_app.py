'''
Interface de Usuário (Frontend) para o Agent_BI.
Versão integrada que não depende de API externa.
Cache clear trigger: 2025-09-21 20:52 - ValidationError fix applied
'''
import streamlit as st
import uuid
import pandas as pd
import logging

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
            logging.info("✅ Autenticação carregada")
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

# Importações do backend para integração direta - TESTE INDIVIDUAL
import_errors = []
BACKEND_AVAILABLE = True

# Teste cada import individualmente para melhor diagnóstico
try:
    from core.graph.graph_builder import GraphBuilder
except Exception as e:
    import_errors.append(f"GraphBuilder: {e}")
    BACKEND_AVAILABLE = False

# Settings importadas via lazy loading - não na inicialização
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

try:
    from core.factory.component_factory import ComponentFactory
except Exception as e:
    import_errors.append(f"OpenAILLMAdapter: {e}")
    BACKEND_AVAILABLE = False

try:
    from core.connectivity.parquet_adapter import ParquetAdapter
except Exception as e:
    import_errors.append(f"ParquetAdapter: {e}")
    BACKEND_AVAILABLE = False

try:
    from core.agents.code_gen_agent import CodeGenAgent
except Exception as e:
    import_errors.append(f"CodeGenAgent: {e}")
    BACKEND_AVAILABLE = False

try:
    from langchain_core.messages import HumanMessage
except Exception as e:
    import_errors.append(f"LangChain: {e}")
    BACKEND_AVAILABLE = False

try:
    from core.utils.query_history import QueryHistory
except Exception as e:
    import_errors.append(f"QueryHistory: {e}")
    BACKEND_AVAILABLE = False

if import_errors:
    logging.warning(f"Erros de import detectados: {import_errors}")
else:
    logging.info("Todos os imports do backend foram bem-sucedidos")

# --- Autenticação ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated or sessao_expirada():
    st.session_state.authenticated = False
    login()
else:
    # --- Configuração da Página ---
    st.set_page_config(page_title="Agent_BI", page_icon="📊", layout="wide")
    st.title("📊 Agent_BI - Assistente Inteligente")

    # --- Inicialização do Backend Integrado ---
    @st.cache_resource
    def initialize_backend():
        """Inicializa os componentes do backend uma única vez"""
        debug_info = []

        # Debug 1: Verificar imports
        debug_info.append(f"BACKEND_AVAILABLE: {BACKEND_AVAILABLE}")
        if not BACKEND_AVAILABLE:
            with st.sidebar:
                st.error("❌ Imports do backend falharam")
                st.write("**Erros específicos:**")
                for error in import_errors:
                    st.code(error)
                st.write("**Possíveis soluções:**")
                st.info("1. Verificar requirements.txt\n2. Reinstalar dependências\n3. Verificar Python path")
            return None

        try:
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

            # Debug 5: Inicializar Parquet
            debug_info.append("Inicializando Parquet...")
            import os
            parquet_path = os.path.join(os.getcwd(), "data", "parquet", "admmat.parquet")

            if not os.path.exists(parquet_path):
                # ❌ ERRO CRÍTICO: Arquivo de dados não encontrado
                debug_info.append("❌ ERRO: Arquivo admmat.parquet não encontrado")
                raise FileNotFoundError(
                    f"Arquivo de dados não encontrado: {parquet_path}\n\n"
                    "AÇÃO NECESSÁRIA:\n"
                    "1. Verifique se o arquivo 'data/parquet/admmat.parquet' existe no repositório\n"
                    "2. Para Streamlit Cloud: configure o arquivo via Git ou external storage\n"
                    "3. Para desenvolvimento local: copie o arquivo para a pasta correta"
                )

            # Validar estrutura do arquivo
            import pandas as pd
            df_test = pd.read_parquet(parquet_path)
            required_columns = ['une', 'une_nome', 'codigo', 'nome_produto', 'mes_01']
            missing_columns = [col for col in required_columns if col not in df_test.columns]

            if missing_columns:
                debug_info.append(f"❌ ERRO: Colunas obrigatórias ausentes: {missing_columns}")
                raise ValueError(
                    f"Arquivo de dados inválido - faltam colunas: {missing_columns}\n"
                    f"Colunas esperadas: {required_columns}\n"
                    f"Colunas encontradas: {list(df_test.columns[:10])}"
                )

            if len(df_test) < 1000:
                debug_info.append(f"⚠️ AVISO: Dataset muito pequeno ({len(df_test)} linhas)")

            parquet_adapter = ParquetAdapter(file_path=parquet_path)
            debug_info.append(f"✅ Parquet OK ({len(df_test):,} produtos, {df_test['une_nome'].nunique()} UNEs)")

            # Mostrar UNEs disponíveis no sidebar para o usuário
            with st.sidebar:
                st.info(f"**📊 Dataset Carregado**\n\n"
                       f"- {len(df_test):,} produtos\n"
                       f"- {df_test['une_nome'].nunique()} UNEs\n\n"
                       f"**UNEs disponíveis:** {', '.join(sorted(df_test['une_nome'].unique()))}")

            # Debug 6: Inicializar CodeGen
            debug_info.append("Inicializando CodeGen...")
            code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter)
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
            debug_info.append(f"❌ ERRO: {str(e)}")

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

                    st.write("**Erro Completo:**")
                    st.code(str(e))
            else:
                with st.sidebar:
                    st.error("❌ Sistema temporariamente indisponível")

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


    # --- Estado da Sessão ---

    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": {
                    "type": "text",
                    "content": "Olá! Como posso ajudar você com seus dados hoje?"
                }
            }
        ]

    # --- Funções de Interação ---
    def query_backend(user_input: str):
        '''Processa a query diretamente usando o backend integrado.'''
        # 📝 GARANTIR que a pergunta do usuário seja sempre preservada
        user_message = {"role": "user", "content": {"type": "text", "content": user_input}}
        st.session_state.messages.append(user_message)

        with st.spinner("O agente está a pensar..."):
            try:
                # 🚀 PRIORIDADE: Tentar DirectQueryEngine primeiro (mais rápido e eficiente)
                # Tentar usar o DirectQueryEngine primeiro
                from core.business_intelligence.direct_query_engine import DirectQueryEngine
                from core.connectivity.parquet_adapter import ParquetAdapter

                adapter = ParquetAdapter('data/parquet/admmat.parquet')
                engine = DirectQueryEngine(adapter)
                direct_result = engine.process_query(user_input)

                # Verificar se o DirectQueryEngine conseguiu processar ou se precisa de fallback
                result_type = direct_result.get("type") if direct_result else None

                # 🔍 DEBUG: Mostrar resultado do DirectQueryEngine
                with st.expander("🔍 Debug: Resultado do DirectQueryEngine"):
                    st.write(f"**Result Type:** {result_type}")
                    st.write(f"**Title:** {direct_result.get('title', 'N/A')}")
                    st.write(f"**Summary:** {direct_result.get('summary', 'N/A')[:200]}")
                    st.write(f"**Has Result:** {'result' in direct_result}")
                    if 'result' in direct_result:
                        result_keys = list(direct_result['result'].keys()) if isinstance(direct_result.get('result'), dict) else []
                        st.write(f"**Result Keys:** {result_keys}")

                # ✅ FIX: Tratar erros explicitamente - não fazer fallback em erros de validação
                if result_type == "error":
                    # Mostrar erro do DirectQueryEngine ao usuário
                    error_msg = direct_result.get("error", "Erro desconhecido")
                    suggestion = direct_result.get("suggestion", "")

                    agent_response = {
                        "type": "error",
                        "content": f"❌ {error_msg}\n\n💡 {suggestion}" if suggestion else f"❌ {error_msg}",
                        "user_query": user_input,
                        "method": "direct_query"
                    }
                    st.write("⚠️ DirectQueryEngine retornou erro de validação")

                elif direct_result and result_type not in ["fallback", None]:
                    # SUCESSO: Usar o resultado do DirectQueryEngine
                    st.write("✅ Usando resultado do DirectQueryEngine")
                    agent_response = {
                        "type": direct_result.get("type", "text"),
                        "title": direct_result.get("title", ""),
                        "content": direct_result.get("summary", ""),
                        "result": direct_result.get("result", {}),
                        "user_query": user_input,
                        "method": "direct_query",
                        "processing_time": direct_result.get("processing_time", 0)
                    }
                else:
                    # FALLBACK: Usar o agent_graph
                    st.write("🔄 DirectQueryEngine não processou, usando fallback agent_graph...")
                    st.warning(f"⚠️ Motivo do fallback: result_type={result_type}")
                    if not backend_components or not backend_components.get("agent_graph"):
                        # Caso de fallback onde o grafo não está disponível
                        agent_response = {
                            "type": "text",
                            "content": f"⚠️ Sistema está sendo inicializado. Tente novamente em alguns segundos.\n\nSe o problema persistir, contate o administrador.",
                            "user_query": user_input
                        }
                    else:
                        # Chamar o agent_graph principal com medição de tempo
                        import time
                        start_time = time.time()
                        initial_state = {"messages": [HumanMessage(content=user_input)]}
                        final_state = backend_components["agent_graph"].invoke(initial_state)
                        end_time = time.time()

                        agent_response = final_state.get("final_response", {})
                        agent_response["method"] = "agent_graph"
                        agent_response["processing_time"] = end_time - start_time

                        # Garantir que a resposta inclui informações da pergunta
                        if "user_query" not in agent_response:
                            agent_response["user_query"] = user_input

                # ✅ GARANTIR estrutura correta da resposta
                assistant_message = {"role": "assistant", "content": agent_response}
                st.session_state.messages.append(assistant_message)

                # 🔍 LOG da resposta
                logging.info(f"AGENT RESPONSE ADDED: Type={agent_response.get('type', 'unknown')}")

            except Exception as e:
                # Tratamento de erro local
                logging.exception("Ocorreu um erro grave ao processar a consulta do usuário.")
                error_content = {
                    "type": "error",
                    "content": f"❌ Erro ao processar consulta: {str(e)}\n\nUm erro inesperado ocorreu. A equipe de desenvolvimento foi notificada."
                }
                st.session_state.messages.append({"role": "assistant", "content": error_content})

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
    # 🔍 DEBUG: Mostrar histórico de mensagens na sidebar (apenas para desenvolvimento)
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
                import json
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

                        if chart_type == "bar" and x_data and y_data:
                            # Gráfico de barras com melhorias visuais
                            fig = go.Figure()

                            # Adicionar barras com cores personalizadas
                            fig.add_trace(go.Bar(
                                x=x_data,
                                y=y_data,
                                marker_color=colors if colors else '#1f77b4',
                                text=[f'{int(val):,}' for val in y_data],
                                textposition='outside',
                                name='Vendas',
                                hovertemplate='<b>%{x}</b><br>Vendas: %{y:,.0f}<extra></extra>'
                            ))

                            # Configurações de layout melhoradas
                            height = chart_data.get("height", 500)
                            margin = chart_data.get("margin", {"l": 60, "r": 60, "t": 80, "b": 100})

                            fig.update_layout(
                                title={
                                    'text': response_data.get("title", "Gráfico"),
                                    'x': 0.5,
                                    'xanchor': 'center',
                                    'font': {'size': 16, 'family': 'Arial Black'}
                                },
                                xaxis_title="UNE",
                                yaxis_title="Vendas",
                                height=height,
                                margin=margin,
                                showlegend=False,
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(family="Arial, sans-serif", size=12, color="#333"),
                                xaxis=dict(tickangle=-45),
                                yaxis=dict(gridcolor='rgba(128,128,128,0.2)'),
                                hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
                            )
                        else:
                            # Fallback para formato personalizado sem dados
                            st.error("Dados do gráfico não disponíveis")
                            continue
                    else:
                        # Formato Plotly padrão (já completo)
                        if isinstance(content, str):
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

                st.write(content)

        except Exception as e:
            # ❌ Tratamento de erro na renderização
            st.error(f"Erro ao renderizar mensagem {i+1}: {str(e)}")
            st.write(f"Dados da mensagem: {msg}")

    if prompt := st.chat_input("Faça sua pergunta..."):
        query_backend(prompt)
