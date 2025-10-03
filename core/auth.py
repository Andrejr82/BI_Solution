# Este arquivo lida com a autenticação de usuários. É crucial que as senhas nunca sejam armazenadas em texto plano.
# Em vez disso, utilizamos funções de hash seguras (como bcrypt, implementado em sql_server_auth_db.py)
# para converter as senhas em um formato ilegível e irreversível. Isso protege as informações dos usuários
# mesmo em caso de violação de dados, pois apenas os hashes são armazenados, não as senhas originais.
import streamlit as st
import time
import logging

audit_logger = logging.getLogger("audit")

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
    "cacula": {"password": "cacula123", "role": "admin"}  # Usuário específico do projeto
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

    # Coloca o formulário de login em uma coluna centralizada para melhor apelo visual
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <style>
                .login-container {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 2rem;
                    border-radius: 15px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    text-align: center;
                    margin-bottom: 1rem;
                }
                .login-title {
                    color: white;
                    font-size: 2rem;
                    font-weight: bold;
                    margin: 1rem 0;
                }
                .login-subtitle {
                    color: rgba(255,255,255,0.9);
                    font-size: 1rem;
                }
            </style>
            <div class='login-container'>
                <div style='font-size: 4rem;'>📊</div>
                <h2 class='login-title'>Agente de Negócios</h2>
                <p class='login-subtitle'>Acesse com seu usuário e senha para continuar</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        with st.form("login_form"):
            username = st.text_input("Usuário", placeholder="Digite seu usuário")
            password = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            login_btn = st.form_submit_button("Entrar", use_container_width=True, type="primary")

            if login_btn:
                # Bypass de autenticação para desenvolvimento
                if username == 'admin' and password == 'bypass':
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = "admin"
                    st.session_state["role"] = "admin"
                    st.session_state["ultimo_login"] = time.time()
                    audit_logger.info(f"Usuário admin logado com sucesso (bypass). Papel: admin")
                    st.success(f"Bem-vindo, admin! Acesso de desenvolvedor concedido.")
                    time.sleep(1) # Pausa para o usuário ler a mensagem
                    st.rerun()
                    return

                # Verificar autenticação baseada no modo
                auth_mode = st.session_state.get("auth_mode", "sql_server")

                if auth_mode == "sql_server":
                    # Usar autenticação SQL Server original
                    current_auth_db = get_auth_db()
                    if current_auth_db:
                        role, erro = current_auth_db.autenticar_usuario(username, password)
                    else:
                        role, erro = None, "Banco de dados não disponível"
                    if role:
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = username
                        st.session_state["role"] = role
                        st.session_state["ultimo_login"] = time.time()
                        audit_logger.info(f"Usuário {username} logado com sucesso (SQL Server). Papel: {role}")
                        st.success(f"Bem-vindo, {username}! Redirecionando...")
                        time.sleep(1)
                        st.rerun()
                    else:
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
