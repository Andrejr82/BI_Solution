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

# ═══════════════════════════════════════════════════════════════════════════
# 🚀 DASHBOARD DE PERFORMANCE (v2.2)
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("### 🚀 Dashboard de Performance em Tempo Real")
st.markdown("<div class='info-box'>Monitore performance de queries, cache e inicialização do sistema</div>", unsafe_allow_html=True)

try:
    from core.utils.performance_tracker import get_performance_tracker

    tracker = get_performance_tracker()

    # Seletor de janela de tempo
    col_time, col_refresh = st.columns([3, 1])
    with col_time:
        window_minutes = st.selectbox(
            "Janela de tempo",
            [5, 15, 30, 60, 120, 240],
            index=3,  # Default: 60 minutos
            help="Período de tempo para análise de métricas"
        )
    with col_refresh:
        if st.button("🔄 Atualizar", use_container_width=True):
            st.rerun()

    # Obter estatísticas
    stats = tracker.get_stats(window_minutes=window_minutes)
    startup_stats = tracker.get_startup_stats()

    # ─────────────────────────────────────────────────────────────────────
    # MÉTRICAS PRINCIPAIS
    # ─────────────────────────────────────────────────────────────────────
    st.markdown("#### 📊 Métricas Principais")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "⏱️ Uptime",
            stats['uptime_formatted'],
            help="Tempo desde última inicialização"
        )

    with col2:
        queries_color = "normal"
        if stats['avg_query_time_ms'] > 5000:
            queries_color = "inverse"  # Vermelho
        elif stats['avg_query_time_ms'] > 3000:
            queries_color = "off"  # Amarelo

        st.metric(
            "⚡ Tempo Médio Query",
            f"{stats['avg_query_time_ms']}ms",
            delta=f"P95: {stats['p95_query_time_ms']}ms",
            delta_color=queries_color,
            help="Tempo médio de execução de queries (P95 = 95º percentil)"
        )

    with col3:
        cache_color = "normal" if stats['cache_hit_rate'] >= 50 else "inverse"
        st.metric(
            "💾 Cache Hit Rate",
            f"{stats['cache_hit_rate']}%",
            delta=f"{stats['cache_hits']} hits",
            delta_color=cache_color,
            help="Porcentagem de respostas servidas do cache (ideal: >50%)"
        )

    with col4:
        st.metric(
            "📈 Queries/min",
            f"{stats['queries_per_minute']}",
            delta=f"{stats['total_queries']} total",
            help="Taxa de queries processadas por minuto"
        )

    with col5:
        error_color = "inverse" if stats['error_rate'] > 5 else "normal"
        st.metric(
            "❌ Taxa de Erro",
            f"{stats['error_rate']}%",
            delta=f"{stats['errors']} erros",
            delta_color=error_color,
            help="Porcentagem de queries com erro (ideal: <5%)"
        )

    # ─────────────────────────────────────────────────────────────────────
    # PERFORMANCE DETALHADA
    # ─────────────────────────────────────────────────────────────────────
    st.markdown("#### 🔍 Performance Detalhada")

    col_perf1, col_perf2, col_perf3 = st.columns(3)

    with col_perf1:
        st.markdown("**📊 Estatísticas de Query**")
        query_stats_df = pd.DataFrame({
            "Métrica": ["Mínimo", "Média", "P95", "Máximo"],
            "Tempo (ms)": [
                stats['min_query_time_ms'],
                stats['avg_query_time_ms'],
                stats['p95_query_time_ms'],
                stats['max_query_time_ms']
            ]
        })
        st.dataframe(query_stats_df, use_container_width=True, hide_index=True)

    with col_perf2:
        st.markdown("**💾 Estatísticas de Cache**")
        cache_stats_df = pd.DataFrame({
            "Métrica": ["Hits", "Misses", "Hit Rate", "Total Ops"],
            "Valor": [
                stats['cache_hits'],
                stats['cache_misses'],
                f"{stats['cache_hit_rate']}%",
                stats['cache_hits'] + stats['cache_misses']
            ]
        })
        st.dataframe(cache_stats_df, use_container_width=True, hide_index=True)

    with col_perf3:
        st.markdown("**🚀 Tempo de Inicialização**")
        if startup_stats['count'] > 0:
            startup_df = pd.DataFrame({
                "Métrica": ["Último", "Média", "Mínimo", "Máximo"],
                "Tempo (ms)": [
                    f"{startup_stats['last_startup_ms']}",
                    f"{startup_stats['avg_startup_ms']}",
                    f"{startup_stats['min_startup_ms']}",
                    f"{startup_stats['max_startup_ms']}"
                ]
            })
            st.dataframe(startup_df, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum dado de startup coletado ainda")

    # ─────────────────────────────────────────────────────────────────────
    # QUERIES RECENTES & ERROS
    # ─────────────────────────────────────────────────────────────────────
    col_recent1, col_recent2 = st.columns(2)

    with col_recent1:
        st.markdown("**⏱️ Queries Recentes** (últimas 10)")
        recent_queries = tracker.get_recent_queries(limit=10)
        if recent_queries:
            queries_df = pd.DataFrame([
                {
                    "Tempo": q['timestamp'].split('T')[1][:8],
                    "Duração (ms)": round(q['duration_ms'], 2),
                    "Tipo": q['type'],
                    "Status": "✅" if q['success'] else "❌"
                }
                for q in recent_queries
            ])
            st.dataframe(queries_df, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma query registrada ainda")

    with col_recent2:
        st.markdown("**⚠️ Erros Recentes** (últimos 10)")
        recent_errors = tracker.get_recent_errors(limit=10)
        if recent_errors:
            errors_df = pd.DataFrame([
                {
                    "Tempo": e['timestamp'].split('T')[1][:8],
                    "Erro": e['error'][:50] + "..." if len(e['error']) > 50 else e['error']
                }
                for e in recent_errors
            ])
            st.dataframe(errors_df, use_container_width=True, hide_index=True)
        else:
            st.success("✅ Nenhum erro registrado!")

    # ─────────────────────────────────────────────────────────────────────
    # ESTATÍSTICAS LIFETIME
    # ─────────────────────────────────────────────────────────────────────
    with st.expander("📊 Estatísticas Lifetime (desde inicialização)", expanded=False):
        col_life1, col_life2, col_life3, col_life4 = st.columns(4)

        with col_life1:
            st.metric("Total Queries", stats['lifetime_queries'])

        with col_life2:
            st.metric("Cache Hits", stats['lifetime_cache_hits'])

        with col_life3:
            st.metric("Cache Hit Rate", f"{stats['lifetime_cache_hit_rate']}%")

        with col_life4:
            st.metric("Total Erros", stats['lifetime_errors'])

    # ─────────────────────────────────────────────────────────────────────
    # ALERTAS DE PERFORMANCE
    # ─────────────────────────────────────────────────────────────────────
    st.markdown("#### ⚠️ Alertas de Performance")

    alerts = []

    # Alerta: Query time alto
    if stats['avg_query_time_ms'] > 5000:
        alerts.append(("🔴 CRÍTICO", f"Tempo médio de query muito alto: {stats['avg_query_time_ms']}ms (ideal: <3000ms)"))
    elif stats['avg_query_time_ms'] > 3000:
        alerts.append(("🟡 ATENÇÃO", f"Tempo médio de query alto: {stats['avg_query_time_ms']}ms (ideal: <3000ms)"))

    # Alerta: Cache hit rate baixo
    if stats['cache_hit_rate'] < 30 and (stats['cache_hits'] + stats['cache_misses']) > 10:
        alerts.append(("🟡 ATENÇÃO", f"Cache hit rate baixo: {stats['cache_hit_rate']}% (ideal: >50%)"))

    # Alerta: Taxa de erro alta
    if stats['error_rate'] > 10:
        alerts.append(("🔴 CRÍTICO", f"Taxa de erro muito alta: {stats['error_rate']}% (ideal: <5%)"))
    elif stats['error_rate'] > 5:
        alerts.append(("🟡 ATENÇÃO", f"Taxa de erro elevada: {stats['error_rate']}% (ideal: <5%)"))

    # Alerta: Muitos erros absolutos
    if stats['errors'] > 10:
        alerts.append(("🔴 CRÍTICO", f"{stats['errors']} erros nos últimos {window_minutes} minutos"))

    if alerts:
        for severity, message in alerts:
            if "CRÍTICO" in severity:
                st.error(f"{severity}: {message}")
            else:
                st.warning(f"{severity}: {message}")
    else:
        st.success("✅ Nenhum alerta de performance - sistema operando normalmente!")

    # Botão de salvar snapshot
    if st.button("💾 Salvar Snapshot de Métricas", help="Salva estado atual das métricas em arquivo JSON"):
        tracker.save_snapshot()
        st.success("✅ Snapshot salvo em data/metrics/")

except ImportError:
    st.warning("⚠️ PerformanceTracker não disponível. Instale dependências: `pip install -r requirements.txt`")
except Exception as e:
    st.error(f"❌ Erro ao carregar dashboard de performance: {e}")
    logging.error(f"Erro no dashboard de performance: {e}", exc_info=True)

st.markdown("---")

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

# ✅ CORREÇÃO CONTEXT7: Backend agora é gerenciado via @st.cache_resource
# Não está mais no session_state, mas sim como singleton via cache
# O backend está sempre disponível via initialize_backend() do streamlit_app
backend_status = "✅ Gerenciado via Cache Resource"
backend_time = "Singleton"
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
    # ✅ CORREÇÃO CONTEXT7: Backend não está mais no session_state
    # Está gerenciado via @st.cache_resource no streamlit_app.py
    # Verificar cache diretamente no diretório
    import os
    cache_dir = os.path.join(os.getcwd(), "data", "cache")
    if os.path.exists(cache_dir):
        cache_enabled = True
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
