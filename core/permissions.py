"""
Sistema de permissões de páginas por usuário
Suporta persistência no banco de dados SQL Server
"""
import streamlit as st
import logging

logger = logging.getLogger(__name__)

# Lazy loading do módulo de banco
_auth_db_module = None

def _get_auth_db():
    """Carrega módulo de auth usando lazy loading"""
    global _auth_db_module
    if _auth_db_module is None:
        try:
            from core.database import sql_server_auth_db
            _auth_db_module = sql_server_auth_db
        except Exception as e:
            logger.warning(f"Módulo de auth não disponível: {e}")
            _auth_db_module = False
    return _auth_db_module if _auth_db_module else None

# Páginas disponíveis no sistema
AVAILABLE_PAGES = {
    "3_Graficos_Salvos.py": "📊 Gráficos Salvos",
    "4_Monitoramento.py": "📈 Monitoramento",
    "5_📚_Exemplos_Perguntas.py": "📚 Exemplos de Perguntas",
    "6_❓_Ajuda.py": "❓ Ajuda",
    "6_Painel_de_Administração.py": "⚙️ Painel de Administração",
    "7_📦_Transferências.py": "📦 Transferências",
    "8_📊_Relatório_de_Transferências.py": "📊 Relatório de Transferências",
    "9_Diagnostico_DB.py": "🔧 Diagnóstico DB",
    "10_🤖_Gemini_Playground.py": "🤖 Gemini Playground",
    "11_🔐_Alterar_Senha.py": "🔐 Alterar Senha",
}

# Permissões padrão por role
DEFAULT_PERMISSIONS = {
    "admin": list(AVAILABLE_PAGES.keys()),  # Admin tem acesso a tudo
    "user": [  # User tem acesso às páginas de usuário final
        "3_Graficos_Salvos.py",
        "5_📚_Exemplos_Perguntas.py",
        "6_❓_Ajuda.py",
        "7_📦_Transferências.py",
        "8_📊_Relatório_de_Transferências.py",
        "10_🤖_Gemini_Playground.py",
        "11_🔐_Alterar_Senha.py",
    ]
}

def get_user_permissions(username, role):
    """
    Retorna lista de páginas que o usuário tem permissão
    Carrega do banco de dados se disponível, caso contrário usa session_state
    """
    # Admin sempre tem acesso total
    if role == "admin":
        return DEFAULT_PERMISSIONS["admin"]

    # 1. Tentar carregar do banco de dados
    auth_db = _get_auth_db()
    if auth_db:
        try:
            db_perms = auth_db.load_user_permissions(username)
            if db_perms is not None:  # None significa que não há permissões customizadas
                logger.info(f"Permissões carregadas do banco para {username}")
                return db_perms
        except Exception as e:
            logger.warning(f"Erro ao carregar permissões do banco: {e}")

    # 2. Fallback: Verificar session_state (temporário)
    custom_perms = st.session_state.get(f"permissions_{username}")
    if custom_perms:
        logger.info(f"Permissões carregadas do session_state para {username}")
        return custom_perms

    # 3. Usar permissões padrão baseadas em role
    return DEFAULT_PERMISSIONS.get(role, DEFAULT_PERMISSIONS["user"])

def has_page_permission(page_name):
    """
    Verifica se o usuário atual tem permissão para acessar uma página
    """
    if not st.session_state.get("authenticated"):
        return False

    username = st.session_state.get("username")
    role = st.session_state.get("role")

    # Admin sempre tem acesso
    if role == "admin":
        return True

    # Verificar permissões
    allowed_pages = get_user_permissions(username, role)
    return page_name in allowed_pages

def set_user_permissions(username, pages_list):
    """
    Define permissões customizadas para um usuário
    Salva no banco de dados se disponível, caso contrário usa session_state
    """
    # 1. Tentar salvar no banco de dados
    auth_db = _get_auth_db()
    if auth_db:
        try:
            success = auth_db.save_user_permissions(username, pages_list)
            if success:
                logger.info(f"✅ Permissões salvas no banco para {username}: {len(pages_list)} páginas")
                # Atualizar session_state também para refletir imediatamente
                st.session_state[f"permissions_{username}"] = pages_list
                return True
            else:
                logger.warning(f"⚠️ Falha ao salvar permissões no banco para {username}")
        except Exception as e:
            logger.error(f"Erro ao salvar permissões no banco: {e}")

    # 2. Fallback: Salvar apenas em session_state (temporário)
    st.session_state[f"permissions_{username}"] = pages_list
    logger.warning(f"⚠️ Permissões salvas apenas em session_state para {username} (temporário)")
    return False

def check_page_access(page_name):
    """
    Helper para verificar acesso e exibir erro se não autorizado
    Deve ser chamado no início de cada página
    """
    if not st.session_state.get("authenticated"):
        st.error("❌ Acesso negado. Faça login para continuar.")
        st.stop()

    if not has_page_permission(page_name):
        st.error("❌ Você não tem permissão para acessar esta página.")
        st.info("💡 Entre em contato com o administrador para solicitar acesso.")
        st.stop()
