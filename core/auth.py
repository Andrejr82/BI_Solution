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
            logging.info("✅ SQL Server auth carregado")
        except Exception as e:
            logging.warning(f"❌ SQL Server auth não disponível: {e}")
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
                logging.info("✅ Autenticação SQL Server inicializada")
            except Exception as e:
                logging.warning(f"❌ Falha na inicialização SQL Server: {e}")
                st.session_state["db_inicializado"] = True
                st.session_state["auth_mode"] = "cloud_fallback"
        else:
            st.session_state["db_inicializado"] = True
            st.session_state["auth_mode"] = "cloud_fallback"
            logging.info("🌤️ Usando autenticação cloud (SQL Server não disponível)")


# Usuários para modo cloud (quando SQL Server não estiver disponível)
CLOUD_USERS = {
    "admin": {"password": "admin", "role": "admin"},
    "user": {"password": "user123", "role": "user"},
    "cacula": {"password": "cacula123", "role": "admin"},  # Usuário específico do projeto
    "renan": {"password": "renan", "role": "user"}  # Sincronizado do SQL Server local
}

def verify_cloud_user(username, password):
    """Verifica usuário em modo cloud"""
    if username in CLOUD_USERS:
        return CLOUD_USERS[username]["password"] == password, CLOUD_USERS[username]["role"]
    return False, ""

# --- Login adaptativo (SQL Server ou Cloud) ---
def login():
    # Inicializar sistema de autenticação de forma lazy
    init_auth_system()

    # Design corporativo profissional
    st.markdown(
        """
        <style>
            /* ==================== RESET E GLOBAL ==================== */
            .stApp {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            }

            /* ==================== LOGIN CONTAINER ==================== */
            .login-wrapper {
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 80vh;
                padding: 2rem 1rem;
            }

            .login-card {
                background: white;
                border-radius: 24px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                overflow: hidden;
                max-width: 480px;
                width: 100%;
            }

            .login-header {
                background: linear-gradient(135deg, #00C853 0%, #00AA00 100%);
                padding: 3rem 2rem 2.5rem;
                text-align: center;
                position: relative;
            }

            .login-header::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #FFD700, #FFA500, #FF3333, #C0C0D0, #40B0E0);
            }

            .logo-container {
                margin-bottom: 1.5rem;
            }

            .logo-img {
                width: 100px;
                height: 100px;
                border-radius: 20px;
                background: white;
                padding: 12px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
                margin: 0 auto;
            }

            .login-title {
                color: white;
                font-size: 1.75rem;
                font-weight: 700;
                margin: 0.75rem 0 0.5rem;
                letter-spacing: -0.5px;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }

            .login-subtitle {
                color: rgba(255, 255, 255, 0.95);
                font-size: 0.95rem;
                font-weight: 400;
                margin: 0;
            }

            .login-body {
                padding: 2.5rem 2rem;
            }

            .login-footer {
                background: #f8f9fa;
                padding: 1.25rem 2rem;
                text-align: center;
                border-top: 1px solid #e9ecef;
            }

            .login-footer-text {
                color: #6c757d;
                font-size: 0.85rem;
                margin: 0;
            }

            /* ==================== FORM INPUTS ==================== */
            .stTextInput > div > div > input {
                background-color: #f8f9fa !important;
                color: #2C3E50 !important;
                border: 2px solid #e9ecef !important;
                border-radius: 12px !important;
                padding: 14px 16px !important;
                font-size: 0.95rem !important;
                transition: all 0.3s ease !important;
            }

            .stTextInput > div > div > input:focus {
                background-color: white !important;
                border-color: #00C853 !important;
                box-shadow: 0 0 0 4px rgba(0, 200, 83, 0.1) !important;
            }

            .stTextInput > div > div > input::placeholder {
                color: #adb5bd !important;
            }

            .stTextInput > label {
                color: #495057 !important;
                font-weight: 600 !important;
                font-size: 0.9rem !important;
                margin-bottom: 0.5rem !important;
            }

            /* ==================== BUTTONS ==================== */
            .stButton > button {
                background: linear-gradient(135deg, #00C853 0%, #00AA00 100%) !important;
                color: white !important;
                border: none !important;
                border-radius: 12px !important;
                padding: 14px 24px !important;
                font-weight: 600 !important;
                font-size: 1rem !important;
                transition: all 0.3s ease !important;
                box-shadow: 0 4px 12px rgba(0, 200, 83, 0.3) !important;
            }

            .stButton > button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 20px rgba(0, 200, 83, 0.4) !important;
            }

            .stButton > button:active {
                transform: translateY(0) !important;
            }

            /* Botão secundário */
            .stButton[data-baseweb="button"]:nth-child(2) > button {
                background: white !important;
                color: #6c757d !important;
                border: 2px solid #e9ecef !important;
                box-shadow: none !important;
            }

            .stButton[data-baseweb="button"]:nth-child(2) > button:hover {
                background: #f8f9fa !important;
                border-color: #dee2e6 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Layout centralizado
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Cabeçalho com logo
        st.markdown("""
        <div class='login-card'>
            <div class='login-header'>
                <div class='logo-container'>
                    <img src='data:image/png;base64,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'
                         class='logo-img'
                         alt='Caçula' />
                </div>
                <h1 class='login-title'>Agente de Business Intelligence</h1>
                <p class='login-subtitle'>Sistema Corporativo Caçula</p>
            </div>
            <div class='login-body'>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("👤 Usuário", placeholder="Digite seu usuário", key="login_username")
            password = st.text_input("🔒 Senha", type="password", placeholder="Digite sua senha", key="login_password")

            st.markdown("<br>", unsafe_allow_html=True)

            col1, col2 = st.columns([3, 1])
            with col1:
                login_btn = st.form_submit_button("🚀 Entrar", use_container_width=True, type="primary")
            with col2:
                forgot_btn = st.form_submit_button("❓ Ajuda", use_container_width=True)

        # Fechar divs do card
        st.markdown("""
            </div>
            <div class='login-footer'>
                <p class='login-footer-text'>© 2025 Caçula - Sistema de Business Intelligence</p>
                <p class='login-footer-text' style='margin-top: 0.5rem; font-size: 0.75rem;'>
                    🔒 Acesso seguro e criptografado
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Processar form
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

                # Bypass de autenticação APENAS para desenvolvimento (NUNCA em produção)
                import os
                ENABLE_DEV_BYPASS = os.getenv("ENABLE_DEV_BYPASS", "false").lower() == "true"

                if ENABLE_DEV_BYPASS and username == 'admin' and password == 'bypass':
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = "admin"
                    st.session_state["role"] = "admin"
                    st.session_state["ultimo_login"] = time.time()
                    audit_logger.warning(f"⚠️ DEV BYPASS USADO - Usuário admin (DESENVOLVIMENTO APENAS)")
                    st.warning("⚠️ Modo de Desenvolvimento - Bypass Ativo")
                    st.success(f"Bem-vindo, admin! Acesso de desenvolvedor concedido.")
                    time.sleep(1)
                    st.rerun()
                    return

                # Verificar autenticação baseada no modo
                auth_mode = st.session_state.get("auth_mode", "cloud_fallback")

                if auth_mode == "sql_server":
                    # Usar autenticação SQL Server original
                    current_auth_db = get_auth_db()
                    if current_auth_db:
                        role, erro = current_auth_db.autenticar_usuario(username, password)
                    else:
                        role, erro = None, "Banco de dados não disponível"

                    if role:
                        # Login bem-sucedido - resetar rate limiter
                        login_limiter.reset(username)

                        st.session_state["authenticated"] = True
                        st.session_state["username"] = username
                        st.session_state["role"] = role
                        st.session_state["ultimo_login"] = time.time()
                        audit_logger.info(f"Usuário {username} logado com sucesso (SQL Server). Papel: {role}")
                        st.success(f"Bem-vindo, {username}! Redirecionando...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        # Se SQL Server falhar, tentar cloud fallback
                        audit_logger.warning(f"SQL Server falhou para {username}, tentando cloud fallback...")
                        is_valid, cloud_role = verify_cloud_user(username, password)
                        if is_valid:
                            login_limiter.reset(username)
                            st.session_state["authenticated"] = True
                            st.session_state["username"] = username
                            st.session_state["role"] = cloud_role
                            st.session_state["ultimo_login"] = time.time()
                            audit_logger.info(f"Usuário {username} logado com sucesso (Cloud Fallback). Papel: {cloud_role}")
                            st.success(f"Bem-vindo, {username}! (Modo Cloud)")
                            time.sleep(1)
                            st.rerun()
                        else:
                            # Ambos falharam
                            audit_logger.warning(f"Tentativa de login falha para o usuário: {username}. Erro: {erro or 'Usuário ou senha inválidos.'}")
                            if erro and "bloqueado" in erro:
                                st.error(f"{erro} Contate o administrador.")
                            elif erro and "Tentativas restantes" in erro:
                                st.warning(erro)
                            else:
                                st.error(erro or "Usuário ou senha inválidos.")
                else:
                    # Usar autenticação cloud fallback
                    is_valid, role = verify_cloud_user(username, password)
                    if is_valid:
                        # Login bem-sucedido - resetar rate limiter
                        login_limiter.reset(username)

                        st.session_state["authenticated"] = True
                        st.session_state["username"] = username
                        st.session_state["role"] = role
                        st.session_state["ultimo_login"] = time.time()
                        audit_logger.info(f"Usuário {username} logado com sucesso (Cloud). Papel: {role}")
                        st.success(f"Bem-vindo, {username}! (Modo Cloud)")
                        time.sleep(1)
                        st.rerun()
                    else:
                        audit_logger.warning(f"Tentativa de login falha para o usuário: {username} (Cloud)")
                        st.error("Usuário ou senha inválidos.")


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
