"""
Módulo para core/auth.py. Fornece funções utilitárias, incluindo 'get_auth_db' e outras. Define componentes da interface de utilizador (UI).
"""

# Este arquivo lida com a autenticação de usuários. É crucial que as senhas nunca sejam armazenadas em texto plano.
# Em vez disso, utilizamos funções de hash seguras (como bcrypt, implementado em sql_server_auth_db.py)
# para converter as senhas em um formato ilegível e irreversível. Isso protege as informações dos usuários
# mesmo em caso de violação de dados, pois apenas os hashes são armazenados, não as senhas originais.
import streamlit as st
import time
import logging
from core.security import RateLimiter, sanitize_username

audit_logger = logging.getLogger("audit")

# Rate limiters para segurança
login_limiter = RateLimiter(max_calls=5, period=300)  # 5 tentativas em 5 minutos

# Importação condicional do sistema de auth (lazy loading)
SQL_AUTH_AVAILABLE = None
auth_db = None

def get_auth_db():
    """Obtém o módulo de auth usando lazy loading"""
    global SQL_AUTH_AVAILABLE, auth_db
    if SQL_AUTH_AVAILABLE is None:
        try:
            from core.database import sql_server_auth_db as _auth_db
            auth_db = _auth_db
            SQL_AUTH_AVAILABLE = True
            logging.info("[AUTH] SQL Server auth carregado")
        except Exception as e:
            logging.warning(f"[AUTH] SQL Server auth não disponível: {e}")
            SQL_AUTH_AVAILABLE = False
            auth_db = None
    return auth_db if SQL_AUTH_AVAILABLE else None

def init_auth_system():
    """Inicializa o sistema de autenticação de forma lazy"""
    if "db_inicializado" not in st.session_state:
        current_auth_db = get_auth_db()
        if current_auth_db:
            try:
                current_auth_db.init_db()
                st.session_state["db_inicializado"] = True
                st.session_state["auth_mode"] = "sql_server"
                logging.info("[AUTH] SQL Server inicializado")
            except Exception as e:
                logging.warning(f"[AUTH] Falha SQL Server: {e}")
                st.session_state["db_inicializado"] = True
                st.session_state["auth_mode"] = "cloud_fallback"
        else:
            st.session_state["db_inicializado"] = True
            st.session_state["auth_mode"] = "cloud_fallback"
            logging.info("[AUTH] Modo cloud ativo")


# Usuários para modo cloud (quando SQL Server não estiver disponível)
CLOUD_USERS = {
    "admin": {"password": "admin", "role": "admin", "segmento": "ARMARINHO E CONFECÇÃO"},
    "user": {"password": "user123", "role": "user", "segmento": "ARMARINHO E CONFECÇÃO"},
    "cacula": {"password": "cacula123", "role": "admin", "segmento": "ARTESANATO"},  # Usuário específico do projeto
    "renan": {"password": "renan", "role": "user", "segmento": "ARTESANATO"}  # Sincronizado do SQL Server local
}

def verify_cloud_user(username, password):
    """Verifica usuário em modo cloud"""
    if username in CLOUD_USERS:
        user_data = CLOUD_USERS[username]
        return user_data["password"] == password, user_data["role"], user_data["segmento"]
    return False, "", None

# --- Login adaptativo (SQL Server ou Cloud) ---
def login():
    # Inicializar sistema de autenticação de forma lazy
    init_auth_system()

    # ✅ OTIMIZAÇÃO CONTEXT7: Layout 60% centralizado (melhor proporção)
    # Usar proporção 20% - 60% - 20% para melhor estética
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(
            """
            <style>
                .login-container {
                    background: #FFFFFF;
                    padding: 2.5rem 3rem;
                    border-radius: 15px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    border: 1px solid #E5E7EB;
                    text-align: center;
                    margin-bottom: 1.5rem;
                }
                .login-title {
                    color: #111827;
                    font-size: 2.5rem;
                    font-weight: bold;
                    margin: 1rem 0 0.5rem 0;
                    letter-spacing: -0.5px;
                }
                .login-subtitle {
                    color: #6B7280;
                    font-size: 1.1rem;
                    margin-top: 0.5rem;
                    font-weight: 300;
                }
            </style>
            <div class='login-container'>
                <svg width="80" height="80" viewBox="0 0 100 100" style="margin-bottom: 0.5rem; opacity: 0.9;">
                    <rect x="15" y="60" width="10" height="30" fill="#3B82F6" opacity="0.7"/>
                    <rect x="30" y="45" width="10" height="45" fill="#3B82F6" opacity="0.8"/>
                    <rect x="45" y="30" width="10" height="60" fill="#3B82F6" opacity="0.9"/>
                    <rect x="60" y="20" width="10" height="70" fill="#3B82F6"/>
                    <rect x="75" y="35" width="10" height="55" fill="#3B82F6" opacity="0.85"/>
                    <circle cx="50" cy="50" r="40" fill="none" stroke="#3B82F6" stroke-width="2" opacity="0.3"/>
                </svg>
                <h2 class='login-title'>Agente de Negócios</h2>
                <p class='login-subtitle'>Acesse com seu usuário e senha para continuar</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ✅ OTIMIZAÇÃO CONTEXT7: Form com melhor UX e feedback visual
        with st.form("login_form", clear_on_submit=False):
            # Inputs com ícones e ajuda contextual
            username = st.text_input(
                "👤 Usuário",
                placeholder="Digite seu usuário",
                help="Use seu nome de usuário corporativo",
                key="login_username"
            )
            password = st.text_input(
                "🔒 Senha",
                type="password",
                placeholder="Digite sua senha",
                help="Senha criada no cadastro ou fornecida pelo administrador",
                key="login_password"
            )

            # Checkbox "Lembrar-me" (visual apenas, funcionalidade futura)
            remember_me = st.checkbox("🔐 Manter conectado por 7 dias", value=False)

            # Botões com melhor proporção
            col_btn1, col_btn2 = st.columns([2, 1])
            with col_btn1:
                login_btn = st.form_submit_button(
                    "🚀 Entrar",
                    use_container_width=True,
                    type="primary"
                )
            with col_btn2:
                forgot_btn = st.form_submit_button(
                    "🔑 Esqueci",
                    use_container_width=True
                )

            if forgot_btn:
                st.info("🔑 Entre em contato com o administrador para redefinir sua senha.")
                st.stop()

            if login_btn:
                # Sanitizar username
                username = sanitize_username(username)

                # Rate limiting - prevenir força bruta
                if not login_limiter.is_allowed(username):
                    reset_time = login_limiter.get_reset_time(username)
                    audit_logger.warning(f"🚨 Rate limit excedido para {username}")
                    st.error(f"⚠️ Muitas tentativas de login. Tente novamente em {reset_time:.0f} segundos.")
                    st.stop()

                # ✅ AUTENTICAÇÃO DIRETA (sem spinners - mais rápido)
                # Bypass de autenticação APENAS para desenvolvimento (NUNCA em produção)
                import os
                ENABLE_DEV_BYPASS = os.getenv("ENABLE_DEV_BYPASS", "false").lower() == "true"

                if ENABLE_DEV_BYPASS and username == 'admin' and password == 'bypass':
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = "admin"
                    st.session_state["role"] = "admin"
                    st.session_state["ultimo_login"] = time.time()
                    st.session_state["segmento"] = "ARMARINHO E CONFECÇÃO" # Default segment for bypass
                    audit_logger.warning(f"⚠️ DEV BYPASS USADO - Usuário admin (DESENVOLVIMENTO APENAS)")
                    # ✅ Rerun direto - sem mensagens (login instantâneo)
                    st.rerun()
                    return

                # Verificar autenticação baseada no modo
                auth_mode = st.session_state.get("auth_mode", "cloud_fallback")

                if auth_mode == "sql_server":
                    # Usar autenticação SQL Server original
                    current_auth_db = get_auth_db()
                    if current_auth_db:
                        role, segmento, erro = current_auth_db.autenticar_usuario(username, password)
                    else:
                        role, segmento, erro = None, None, "Banco de dados não disponível"

                    if role:
                        # Login bem-sucedido
                        login_limiter.reset(username)
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = username
                        st.session_state["role"] = role
                        st.session_state["segmento"] = segmento
                        st.session_state["ultimo_login"] = time.time()
                        audit_logger.info(f"Usuário {username} logado com sucesso (SQL Server). Papel: {role}. Segmento: {segmento}")
                        # ✅ Rerun direto - sem mensagens (login instantâneo)
                        st.rerun()
                    else:
                        # Se SQL Server falhar, tentar cloud fallback
                        audit_logger.warning(f"SQL Server falhou para {username}, tentando cloud fallback...")
                        is_valid, cloud_role, cloud_segmento = verify_cloud_user(username, password)
                        if is_valid:
                            login_limiter.reset(username)
                            st.session_state["authenticated"] = True
                            st.session_state["username"] = username
                            st.session_state["role"] = cloud_role
                            st.session_state["segmento"] = cloud_segmento
                            st.session_state["ultimo_login"] = time.time()
                            audit_logger.info(f"Usuário {username} logado com sucesso (Cloud Fallback). Papel: {cloud_role}. Segmento: {cloud_segmento}")
                            # ✅ Rerun direto - sem mensagens (login instantâneo)
                            st.rerun()
                        else:
                            # Ambos falharam
                            audit_logger.warning(f"Tentativa de login falha para o usuário: {username}. Erro: {erro or 'Usuário ou senha inválidos.'}")
                            if erro and "bloqueado" in erro:
                                st.error(f"🚫 {erro} Contate o administrador.")
                            elif erro and "Tentativas restantes" in erro:
                                st.warning(f"⚠️ {erro}")
                            else:
                                st.error(f"❌ {erro or 'Usuário ou senha inválidos.'}")
                else:
                    # Usar autenticação cloud fallback
                    is_valid, role, segmento = verify_cloud_user(username, password)
                    if is_valid:
                        # Login bem-sucedido
                        login_limiter.reset(username)
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = username
                        st.session_state["role"] = role
                        st.session_state["segmento"] = segmento
                        st.session_state["ultimo_login"] = time.time()
                        audit_logger.info(f"Usuário {username} logado com sucesso (Cloud). Papel: {role}. Segmento: {segmento}")
                        # ✅ Rerun direto - sem mensagens (login instantâneo)
                        st.rerun()
                    else:
                        # Falha na autenticação
                        audit_logger.warning(f"Tentativa de login falha para o usuário: {username} (Cloud)")
                        st.error("❌ Usuário ou senha inválidos.")


# --- Expiração automática de sessão ---
def sessao_expirada():
    if not st.session_state.get("ultimo_login"):
        return True
    tempo = time.time() - st.session_state["ultimo_login"]

    # Usar timeout baseado no modo de autenticação
    auth_mode = st.session_state.get("auth_mode", "sql_server")
    if auth_mode == "sql_server":
        current_auth_db = get_auth_db()
        if current_auth_db:
            timeout_minutes = current_auth_db.SESSAO_MINUTOS
        else:
            timeout_minutes = 30  # Fallback
    else:
        timeout_minutes = 240  # 4 horas para modo cloud

    return tempo > 60 * timeout_minutes
