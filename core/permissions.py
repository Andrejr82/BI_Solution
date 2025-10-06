"""
Sistema de permissões de páginas por usuário
"""
import streamlit as st
import logging

logger = logging.getLogger(__name__)

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
    "user": [  # User tem acesso limitado
        "5_📚_Exemplos_Perguntas.py",
        "6_❓_Ajuda.py",
        "11_🔐_Alterar_Senha.py",
    ]
}

def get_user_permissions(username, role):
    """
    Retorna lista de páginas que o usuário tem permissão
    Por enquanto usa permissões padrão baseadas em role
    """
    # Admin sempre tem acesso total
    if role == "admin":
        return DEFAULT_PERMISSIONS["admin"]

    # Verificar se há permissões customizadas no session_state
    custom_perms = st.session_state.get(f"permissions_{username}")
    if custom_perms:
        return custom_perms

    # Usar permissões padrão
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
    (armazenado em session_state - em produção seria no banco)
    """
    st.session_state[f"permissions_{username}"] = pages_list
    logger.info(f"Permissões atualizadas para {username}: {len(pages_list)} páginas")

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
