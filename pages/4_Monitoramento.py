"""
Módulo para pages/4_Monitoramento.py. Fornece funções utilitárias, incluindo 'get_settings' e outras. Define componentes da interface de utilizador (UI).
"""

import streamlit as st
import os
import time
import pandas as pd
import logging

# Importação condicional para funcionar no cloud
try:
    from sqlalchemy import create_engine
    from core.database import sql_server_auth_db as auth_db
    # Settings importadas com lazy loading
    DB_AVAILABLE = True
except Exception as e:
    logging.warning(f"Database components não disponíveis: {e}")
    DB_AVAILABLE = False

def get_settings():
    """Obtém settings de forma lazy"""
    try:
        from core.config.safe_settings import get_safe_settings
        return get_safe_settings()
    except Exception:
        return None

# Verificar se é admin
if st.session_state.get("role") != "admin":
    st.error("❌ Acesso negado. Esta página é restrita a administradores.")
    st.stop()

st.markdown("<h1 class='main-header'>Monitoramento do Sistema</h1>", unsafe_allow_html=True)
st.markdown("<div class='info-box'>Acompanhe os logs do sistema e o status dos principais serviços.</div>", unsafe_allow_html=True)

# --- LOGS DO SISTEMA ---
st.markdown("### Logs do Sistema")
log_dir = os.path.join(os.getcwd(), "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_files = [f for f in os.listdir(log_dir) if f.endswith(".log")]
if not log_files:
    st.warning("Nenhum arquivo de log encontrado.")
else:
    selected_log = st.selectbox("Selecione o arquivo de log", log_files)
    keyword = st.text_input("Filtrar por palavra-chave (opcional)")
    log_level = st.selectbox("Filtrar por nível", ["Todos", "INFO", "WARNING", "ERROR", "DEBUG"])
    log_path = os.path.join(log_dir, selected_log)
    log_lines = []
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if keyword and keyword.lower() not in line.lower():
                    continue
                if log_level != "Todos" and log_level not in line:
                    continue
                log_lines.append(line.strip())
    st.write(f"Total de linhas exibidas: {len(log_lines)}")
    st.dataframe(pd.DataFrame(log_lines, columns=["Log"]), use_container_width=True)

# --- STATUS DOS SERVIÇOS ---
st.markdown("### Status dos Serviços")
status_data = []

# Checagem do Backend Integrado
backend_status = "❌ Não inicializado"
backend_time = "-"
try:
    start = time.time()
    if 'backend_components' in st.session_state and st.session_state.backend_components:
        components = st.session_state.backend_components
        if components.get("agent_graph"):
            backend_time = f"{(time.time() - start)*1000:.0f} ms"
            backend_status = "✅ Operacional (LangGraph)"
        else:
            backend_status = "⚠️ Parcialmente inicializado"
    else:
        backend_status = "❌ Não disponível"
except Exception as e:
    backend_status = f"❌ Erro: {str(e)[:30]}"
status_data.append({"Serviço": "Backend LangGraph", "Status": backend_status, "Tempo": backend_time})
# Checagem do Banco de Dados
db_status = "❌ Não configurado"
db_time = "-"
if DB_AVAILABLE:
    try:
        start = time.time()
        current_settings = get_settings()
        if current_settings and hasattr(current_settings, 'get_sql_connection_string'):
            conn_str = current_settings.get_sql_connection_string()
            if conn_str:
                engine = create_engine(conn_str)
                with engine.connect() as conn:
                    conn.execute("SELECT 1")
                db_time = f"{(time.time() - start)*1000:.0f} ms"
                db_status = "✅ Conectado (SQL Server)"
        else:
            db_status = "⚠️ Configuração ausente"
    except Exception as e:
        db_status = f"❌ Erro: {str(e)[:30]}"
else:
    db_status = "🌤️ Modo Cloud (sem DB)"
status_data.append({"Serviço": "Banco de Dados SQL", "Status": db_status, "Tempo": db_time})
# Checagem dos LLMs (Gemini/DeepSeek)
try:
    from core.factory.component_factory import ComponentFactory

    # Verificar Gemini
    gemini_status = "-"
    gemini_time = "-"
    try:
        current_settings = get_settings()
        if current_settings and current_settings.GEMINI_API_KEY:
            gemini_adapter = ComponentFactory.get_llm_adapter("gemini")
            if gemini_adapter:
                start = time.time()
                response = gemini_adapter.get_completion([{"role": "user", "content": "ping"}], max_tokens=1)
                gemini_time = f"{(time.time() - start)*1000:.0f} ms"
                gemini_status = "OK" if response and not response.get('error') else "ERRO"
            else:
                gemini_status = "Adaptador não disponível"
        else:
            gemini_status = "Chave API não configurada"
    except Exception as e:
        gemini_status = f"FALHA ({str(e)[:30]})"

    # Verificar DeepSeek
    deepseek_status = "-"
    deepseek_time = "-"
    try:
        current_settings = get_settings()
        if current_settings and current_settings.DEEPSEEK_API_KEY:
            deepseek_adapter = ComponentFactory.get_llm_adapter("deepseek")
            if deepseek_adapter:
                start = time.time()
                response = deepseek_adapter.get_completion([{"role": "user", "content": "ping"}], max_tokens=1)
                deepseek_time = f"{(time.time() - start)*1000:.0f} ms"
                deepseek_status = "OK" if response and not response.get('error') else "ERRO"
            else:
                deepseek_status = "Adaptador não disponível"
        else:
            deepseek_status = "Chave API não configurada"
    except Exception as e:
        deepseek_status = f"FALHA ({str(e)[:30]})"

except Exception as e:
    gemini_status = f"FALHA ({str(e)[:30]})"
    deepseek_status = f"FALHA ({str(e)[:30]})"

status_data.append({"Serviço": "LLM (Gemini)", "Status": gemini_status, "Tempo": gemini_time})
status_data.append({"Serviço": "LLM (DeepSeek)", "Status": deepseek_status, "Tempo": deepseek_time})
st.dataframe(pd.DataFrame(status_data), use_container_width=True)

# --- ECONOMIA DE CRÉDITOS LLM ---
st.markdown("---")
st.markdown("### 💰 Economia de Créditos LLM (Gemini/DeepSeek)")

# Estatísticas do cache
cache_enabled = False
cache_files = 0
cache_size = 0
cache_ttl = 48

try:
    if 'backend_components' in st.session_state and st.session_state.backend_components:
        llm_adapter = st.session_state.backend_components.get("llm_adapter")

        if llm_adapter:
            # Verificar se tem método get_cache_stats
            if hasattr(llm_adapter, 'get_cache_stats'):
                cache_stats = llm_adapter.get_cache_stats()
                cache_enabled = cache_stats.get("cache_enabled", False)
                cache_files = cache_stats.get("total_files", 0)
                cache_size = cache_stats.get("total_size_mb", 0)
                cache_ttl = cache_stats.get("ttl_hours", 48)
            else:
                # Fallback: verificar atributos diretamente
                cache_enabled = getattr(llm_adapter, 'cache_enabled', False)
                if hasattr(llm_adapter, 'cache_dir'):
                    import os
                    cache_dir = llm_adapter.cache_dir
                    if os.path.exists(cache_dir):
                        cache_files = len([f for f in os.listdir(cache_dir) if f.endswith('.json')])
                        total_bytes = sum(os.path.getsize(os.path.join(cache_dir, f))
                                        for f in os.listdir(cache_dir) if f.endswith('.json'))
                        cache_size = round(total_bytes / (1024 * 1024), 2)

    # Exibir métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Cache Ativo", "✅ Sim" if cache_enabled else "❌ Não")
    with col2:
        st.metric("Respostas Cacheadas", cache_files)
    with col3:
        st.metric("Tamanho Cache", f"{cache_size} MB")
    with col4:
        st.metric("TTL Cache", f"{cache_ttl}h")

    # Informações adicionais
    if cache_enabled:
        st.success(f"💡 **Cache Ativo:** Cada hit no cache economiza 1 chamada ao LLM e reduz custos significativamente!")

        # Estimativa de economia (baseado em preços Gemini 2.5 Flash-Lite)
        if cache_files > 0:
            estimated_savings = cache_files * 0.0001  # $0.10 por 1M tokens ≈ $0.0001 por request média
            st.info(f"💰 **Economia Estimada:** ~${estimated_savings:.2f} USD em chamadas de API")
    else:
        st.warning("⚠️ Cache desativado. Ative o cache para reduzir custos de LLM.")

except Exception as e:
    st.error(f"❌ Erro ao carregar estatísticas de cache: {e}")
    logging.error(f"Erro em economia LLM: {e}")

# --- Função para admins aprovarem redefinição de senha ---
def painel_aprovacao_redefinicao():
    """Painel para aprovação de redefinições de senha - com fallback seguro"""
    st.markdown("<h3>Solicitações de Redefinição de Senha</h3>", unsafe_allow_html=True)

    if not DB_AVAILABLE:
        st.info("🌤️ **Modo Cloud:** Sistema de redefinição de senha não disponível.\n\nPara gerenciar usuários em modo cloud, use o Painel de Administração.")
        return

    try:
        import sqlite3

        # Verificar se auth_db tem DB_PATH
        if not hasattr(auth_db, 'DB_PATH'):
            st.info("ℹ️ **Banco de dados não configurado**\n\nEm modo cloud, use autenticação hardcoded via `core/auth.py`")
            return

        # Verificar se o arquivo do banco existe
        if not os.path.exists(auth_db.DB_PATH):
            st.warning("⚠️ Arquivo de banco de dados não encontrado. Sistema rodando em modo cloud.")
            return

        conn = sqlite3.connect(auth_db.DB_PATH)
        c = conn.cursor()

        # Verificar se a tabela existe
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        if not c.fetchone():
            st.warning("⚠️ Tabela de usuários não encontrada. Inicialize o banco de dados primeiro.")
            conn.close()
            return

        c.execute("SELECT username FROM usuarios WHERE redefinir_solicitado=1 AND redefinir_aprovado=0")
        pendentes = [row[0] for row in c.fetchall()]

        if not pendentes:
            st.success("✅ Nenhuma solicitação pendente de redefinição de senha.")
        else:
            st.info(f"📋 {len(pendentes)} solicitação(ões) pendente(s)")
            for user in pendentes:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Usuário:** {user}")
                with col2:
                    if st.button(f"✅ Aprovar", key=f"approve_{user}"):
                        if hasattr(auth_db, 'aprovar_redefinicao'):
                            auth_db.aprovar_redefinicao(user)
                            st.success(f"Solicitação de {user} aprovada!")
                            st.rerun()
                        else:
                            st.error("Função de aprovação não disponível")
        conn.close()
    except Exception as e:
        st.error(f"❌ Erro ao acessar solicitações: {str(e)}")
        logging.error(f"Erro no painel_aprovacao_redefinicao: {e}")

# --- Função para usuário redefinir senha após aprovação ---
def tela_redefinir_senha():
    st.markdown("<h3>Redefinir Senha</h3>", unsafe_allow_html=True)
    st.info("Sua solicitação foi aprovada. Defina uma nova senha para continuar.")
    username = st.session_state.get("username")
    nova = st.text_input("Nova senha", type="password")
    nova2 = st.text_input("Confirme a nova senha", type="password")
    if st.button("Redefinir senha", use_container_width=True, help="Salvar nova senha"):
        if not nova or not nova2:
            st.warning("Preencha ambos os campos.")
        elif nova != nova2:
            st.error("As senhas não coincidem.")
        elif len(nova) < 6:
            st.warning("A senha deve ter pelo menos 6 caracteres.")
        else:
            try:
                if DB_AVAILABLE and hasattr(auth_db, 'redefinir_senha'):
                    auth_db.redefinir_senha(username, nova)
                else:
                    st.error("Sistema de redefinição não disponível no Streamlit Cloud")
                    return
                st.success("Senha redefinida com sucesso! Você será redirecionado para o login.")
                time.sleep(2)
                for k in ["authenticated", "username", "role", "ultimo_login"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()
            except Exception as e:
                st.error(str(e))

# --- Checagem para exibir tela de redefinição após aprovação ---
def checar_redefinicao_aprovada():
    """Verifica se usuário deve redefinir senha - com fallback seguro"""
    if not DB_AVAILABLE:
        return False

    username = st.session_state.get("username")
    if not username:
        return False

    try:
        import sqlite3
        # Verificar se auth_db tem DB_PATH
        if not hasattr(auth_db, 'DB_PATH'):
            logging.warning("auth_db.DB_PATH não disponível")
            return False

        conn = sqlite3.connect(auth_db.DB_PATH)
        c = conn.cursor()
        c.execute("SELECT redefinir_aprovado FROM usuarios WHERE username=?", (username,))
        row = c.fetchone()
        conn.close()
        return bool(row and row[0])
    except Exception as e:
        logging.error(f"Erro ao verificar redefinição aprovada: {e}")
        return False

# --- Após login, checar se usuário deve redefinir senha ---
if st.session_state.get("authenticated") and checar_redefinicao_aprovada():
    tela_redefinir_senha()
    st.stop()

# --- Aba Monitoramento: admins podem aprovar redefinições ---
elif st.session_state.get("role") == "admin":
    painel_aprovacao_redefinicao()
