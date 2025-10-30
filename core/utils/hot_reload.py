"""
Hot Reload System - Recarga Automática Sem Logout
==================================================

Sistema moderno de detecção de mudanças e recarga automática
baseado nas melhores práticas do Streamlit (Context7).

Funcionalidades:
- Detecção de mudança de versão do código
- Recarga automática de cache sem logout
- Preservação do estado de autenticação
- Notificação visual ao usuário

Autor: Claude Code (baseado em Context7 - Streamlit docs)
Data: 2025-10-27
"""

import streamlit as st
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def init_version_monitor():
    """
    Inicializa o monitor de versão no session state.

    Baseado em: Context7 - Streamlit Session State patterns
    """
    if "code_version_monitor" not in st.session_state:
        st.session_state.code_version_monitor = {
            "current_version": None,
            "last_reload_time": None,
            "reload_count": 0
        }
        logger.info("🔄 Monitor de versão inicializado")


def get_current_code_version() -> Optional[str]:
    """
    Lê a versão atual do código do arquivo .code_version.

    Returns:
        String com a versão ou None se arquivo não existir
    """
    version_file = Path("data/cache/.code_version")

    if version_file.exists():
        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                version = f.read().strip()
            return version
        except Exception as e:
            logger.warning(f"Erro ao ler versão do código: {e}")
            return None
    else:
        logger.warning(f"Arquivo de versão não encontrado: {version_file}")
        return None


def check_code_version_changed() -> bool:
    """
    Verifica se a versão do código mudou desde o último check.

    Returns:
        True se mudou, False caso contrário

    Baseado em: Context7 - Streamlit Session State patterns
    """
    init_version_monitor()

    current_version = get_current_code_version()

    if current_version is None:
        return False

    monitor = st.session_state.code_version_monitor

    # Primeira execução
    if monitor["current_version"] is None:
        monitor["current_version"] = current_version
        logger.info(f"📌 Versão inicial: {current_version}")
        return False

    # Verificar se mudou
    if monitor["current_version"] != current_version:
        logger.warning(f"🔄 Versão mudou: {monitor['current_version']} → {current_version}")
        return True

    return False


def clear_caches_smart():
    """
    Limpa caches de forma inteligente preservando dados essenciais.

    Limpa:
    - st.cache_data (queries, resultados temporários)
    - st.cache_resource (NÃO limpa - preserva conexões DB, modelos LLM)

    Baseado em: Context7 - Streamlit Caching patterns
    """
    try:
        # Limpar cache de dados (queries, dataframes temporários)
        st.cache_data.clear()
        logger.info("✅ Cache de dados limpo (st.cache_data)")

        # NÃO limpar cache de recursos (conexões DB, modelos LLM)
        # st.cache_resource.clear()  ← Preservado intencionalmente

        logger.info("⚙️  Cache de recursos preservado (conexões DB, LLMs)")

        return True

    except Exception as e:
        logger.error(f"❌ Erro ao limpar caches: {e}")
        return False


def trigger_hot_reload():
    """
    Executa hot reload completo:
    1. Limpa caches de dados
    2. Atualiza versão no monitor
    3. Preserva autenticação
    4. Recarrega app (st.rerun)

    Baseado em: Context7 - Streamlit Caching + Session State
    """
    import time

    logger.warning("🔥 HOT RELOAD iniciado...")

    # 1. Limpar caches (dados, não recursos)
    cache_cleared = clear_caches_smart()

    # 2. Atualizar versão no monitor
    current_version = get_current_code_version()
    if current_version:
        st.session_state.code_version_monitor["current_version"] = current_version
        st.session_state.code_version_monitor["last_reload_time"] = time.time()
        st.session_state.code_version_monitor["reload_count"] += 1

        logger.info(f"📌 Versão atualizada: {current_version}")
        logger.info(f"🔢 Reload #{st.session_state.code_version_monitor['reload_count']}")

    # 3. Autenticação é PRESERVADA automaticamente
    # (session_state.username, session_state.role, etc. permanecem)
    if "username" in st.session_state:
        logger.info(f"👤 Autenticação preservada: {st.session_state.username}")

    # 4. Notificar usuário (antes do rerun)
    if cache_cleared:
        st.success("✅ Sistema atualizado! Recarregando...")
    else:
        st.warning("⚠️ Sistema parcialmente atualizado. Recarregando...")

    # Pequeno delay para usuário ver mensagem
    time.sleep(0.5)

    # 5. Recarregar app (Context7 pattern)
    st.rerun()


def auto_hot_reload_on_version_change():
    """
    Detecta mudança de versão e executa hot reload automaticamente.

    Esta função deve ser chamada no início do streamlit_app.py,
    APÓS a autenticação mas ANTES de carregar componentes.

    Exemplo de uso:
    ```python
    # streamlit_app.py

    # 1. Autenticação
    if not st.session_state.get('authenticated'):
        show_login()
        st.stop()

    # 2. Hot Reload (APÓS autenticação)
    from core.utils.hot_reload import auto_hot_reload_on_version_change
    auto_hot_reload_on_version_change()

    # 3. Carregar resto da aplicação
    initialize_backend()
    # ...
    ```

    Baseado em: Context7 - Streamlit Session State + Caching patterns
    """
    # Apenas executar se usuário está autenticado
    if not st.session_state.get('authenticated', False):
        return

    # Verificar mudança de versão
    if check_code_version_changed():
        logger.warning("🚨 MUDANÇA DE CÓDIGO DETECTADA - Executando hot reload...")

        # Mostrar notificação ao usuário
        st.info("""
        🔄 **Atualização Detectada**

        O sistema detectou uma atualização e vai recarregar automaticamente.
        Você permanecerá logado!
        """)

        # Executar hot reload
        trigger_hot_reload()


def show_reload_notification():
    """
    Mostra notificação discreta de última recarga (opcional).

    Baseado em: Context7 - Streamlit UI patterns
    """
    if "code_version_monitor" in st.session_state:
        monitor = st.session_state.code_version_monitor

        if monitor["reload_count"] > 0 and monitor["last_reload_time"]:
            import time
            from datetime import datetime

            last_reload = datetime.fromtimestamp(monitor["last_reload_time"])
            time_ago = int(time.time() - monitor["last_reload_time"])

            if time_ago < 60:
                time_str = f"{time_ago}s atrás"
            elif time_ago < 3600:
                time_str = f"{time_ago // 60}min atrás"
            else:
                time_str = f"{time_ago // 3600}h atrás"

            with st.sidebar.expander(f"🔄 Última atualização: {time_str}", expanded=False):
                st.caption(f"**Versão:** {monitor['current_version']}")
                st.caption(f"**Recargas:** {monitor['reload_count']}")
                st.caption(f"**Horário:** {last_reload.strftime('%H:%M:%S')}")


# ==================== BOTÃO MANUAL DE RECARGA ====================

def show_manual_reload_button():
    """
    Mostra botão para recarga manual (para debug/admin).

    Baseado em: Context7 - Streamlit Button with Callback pattern
    """
    # Apenas para admins
    if st.session_state.get('role') != 'admin':
        return

    with st.sidebar.expander("⚙️ Admin: Recarga Manual", expanded=False):
        st.caption("Force a recarga do sistema sem logout")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 Reload", use_container_width=True, type="secondary"):
                st.session_state.manual_reload = True

        with col2:
            current_version = get_current_code_version()
            st.caption(f"Versão: `{current_version}`")

        # Executar reload se botão foi clicado
        if st.session_state.get('manual_reload', False):
            st.session_state.manual_reload = False
            trigger_hot_reload()


# ==================== EXEMPLO DE USO ====================

if __name__ == "__main__":
    print("""
    HOT RELOAD SYSTEM - Exemplo de Uso
    ===================================

    # streamlit_app.py

    from core.utils.hot_reload import auto_hot_reload_on_version_change, show_manual_reload_button

    # Após autenticação, antes de inicializar backend
    if st.session_state.get('authenticated'):
        # Hot reload automático
        auto_hot_reload_on_version_change()

        # Botão manual (admin)
        show_manual_reload_button()

    # Resto da aplicação...
    initialize_backend()
    # ...

    BENEFÍCIOS:
    ✅ Zero necessidade de logout/login
    ✅ Detecção automática de mudanças
    ✅ Preserva autenticação do usuário
    ✅ Cache inteligente (limpa dados, preserva recursos)
    ✅ Notificação visual amigável
    ✅ Padrões modernos do Streamlit (Context7)
    """)
