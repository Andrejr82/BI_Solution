"""
Sistema de Estabilidade para Streamlit
=======================================

Previne fechamento inesperado do navegador causado por:
1. st.rerun() excessivos (loop infinito)
2. MemoryError não tratados
3. Session state corruption
4. Exceptions não capturadas

Baseado em:
- Context7 Streamlit Documentation
- Best practices de session state management
- Error handling patterns

Autor: Claude Code
Data: 2025-10-27
"""

import logging
import streamlit as st
import functools
import time
from typing import Any, Callable, Optional
import traceback

logger = logging.getLogger(__name__)


# ==================== CONFIGURAÇÕES ====================

# Limite de reruns consecutivos (proteção contra loop infinito)
MAX_RERUNS_PER_SECOND = 3
MAX_RERUNS_CONSECUTIVE = 10

# Timeout para operações pesadas
DEFAULT_TIMEOUT_SECONDS = 120


# ==================== MONITORAMENTO DE RERUNS ====================

def init_rerun_monitor():
    """
    Inicializa monitor de reruns no session_state.

    IMPORTANTE: Chamar no início do streamlit_app.py
    """
    if "rerun_monitor" not in st.session_state:
        st.session_state.rerun_monitor = {
            "count": 0,
            "last_rerun_time": 0,
            "consecutive_reruns": 0,
            "blocked": False
        }


def safe_rerun():
    """
    Versão segura de st.rerun() que previne loops infinitos.

    Substitua todas as chamadas `st.rerun()` por `safe_rerun()`.

    Raises:
        RuntimeError: Se detectado loop infinito de reruns
    """
    init_rerun_monitor()

    monitor = st.session_state.rerun_monitor
    current_time = time.time()

    # Verificar se está em loop
    time_since_last = current_time - monitor["last_rerun_time"]

    if time_since_last < 1.0:
        # Reruns muito rápidos
        monitor["consecutive_reruns"] += 1

        if monitor["consecutive_reruns"] >= MAX_RERUNS_CONSECUTIVE:
            logger.error(f"🚨 LOOP INFINITO DETECTADO: {monitor['consecutive_reruns']} reruns consecutivos")
            monitor["blocked"] = True

            # Mostrar erro na UI ao invés de crashar
            st.error(
                "⚠️ **Sistema Bloqueado Temporariamente**\n\n"
                "Detectado loop infinito de atualizações.\n\n"
                "**O que fazer:**\n"
                "1. Aguarde 5 segundos\n"
                "2. Recarregue a página (F5)\n"
                "3. Se persistir, limpe o cache do navegador"
            )

            # Resetar após 5 segundos
            time.sleep(5)
            monitor["consecutive_reruns"] = 0
            monitor["blocked"] = False

            return  # NÃO fazer rerun
    else:
        # Reset contador se passou tempo suficiente
        monitor["consecutive_reruns"] = 0

    # Atualizar monitor
    monitor["count"] += 1
    monitor["last_rerun_time"] = current_time

    logger.info(f"✅ Safe rerun #{monitor['count']} (consecutive: {monitor['consecutive_reruns']})")

    # Executar rerun normal
    st.rerun()


# ==================== ERROR HANDLING DECORATOR ====================

def stable_component(error_message: str = "Erro ao carregar componente"):
    """
    Decorator para componentes Streamlit que previne crashes.

    Args:
        error_message: Mensagem customizada de erro

    Example:
        @stable_component("Erro ao carregar gráfico")
        def render_chart(data):
            st.plotly_chart(create_chart(data))
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)

            except MemoryError as e:
                logger.error(f"❌ MemoryError em {func.__name__}: {e}")

                st.error(
                    f"⚠️ **{error_message}**\n\n"
                    "Sistema com pouca memória disponível.\n\n"
                    "**Sugestões:**\n"
                    "- Tente uma consulta mais específica\n"
                    "- Feche outras abas do navegador\n"
                    "- Recarregue a página (F5)"
                )

                # NÃO fazer rerun - deixar usuário ver o erro
                return None

            except Exception as e:
                logger.error(f"❌ Erro em {func.__name__}: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")

                # Mostrar erro amigável
                st.error(
                    f"⚠️ **{error_message}**\n\n"
                    f"Detalhes técnicos: {str(e)[:200]}"
                )

                # Debug para admins
                if st.session_state.get('role') == 'admin':
                    with st.expander("🔍 Traceback Completo (Admin)", expanded=False):
                        st.code(traceback.format_exc())

                return None

        return wrapper
    return decorator


# ==================== SESSION STATE VALIDATION ====================

def validate_session_state(required_keys: list) -> bool:
    """
    Valida se session_state tem todas as chaves necessárias.

    Args:
        required_keys: Lista de chaves que devem existir

    Returns:
        True se válido, False caso contrário

    Example:
        if not validate_session_state(["authenticated", "backend_components"]):
            st.error("Session state corrompido. Recarregue a página.")
            st.stop()
    """
    missing_keys = [key for key in required_keys if key not in st.session_state]

    if missing_keys:
        logger.warning(f"⚠️ Session state incompleto. Faltando: {missing_keys}")
        return False

    return True


def safe_session_state_get(key: str, default: Any = None) -> Any:
    """
    Versão segura de st.session_state.get() com logging.

    Args:
        key: Chave do session state
        default: Valor padrão se não existir

    Returns:
        Valor ou default
    """
    try:
        if key in st.session_state:
            return st.session_state[key]
        else:
            logger.debug(f"Session state key '{key}' não encontrado. Usando default: {default}")
            return default

    except Exception as e:
        logger.error(f"Erro ao acessar session_state['{key}']: {e}")
        return default


def safe_session_state_set(key: str, value: Any):
    """
    Versão segura de st.session_state[key] = value com logging.

    Args:
        key: Chave do session state
        value: Valor a setar
    """
    try:
        st.session_state[key] = value
        logger.debug(f"✅ Session state['{key}'] = {str(value)[:100]}")

    except Exception as e:
        logger.error(f"❌ Erro ao setar session_state['{key}']: {e}")


# ==================== MEMORY MONITORING ====================

def check_memory_usage():
    """
    Verifica uso de memória e emite warnings se alto.

    Returns:
        Dict com info de memória
    """
    try:
        import psutil
        import os

        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()

        memory_mb = memory_info.rss / (1024 ** 2)
        memory_percent = process.memory_percent()

        logger.info(f"📊 Memória: {memory_mb:.1f}MB ({memory_percent:.1f}%)")

        # Warning se uso alto
        if memory_mb > 1000:  # > 1GB
            logger.warning(f"⚠️ Uso de memória alto: {memory_mb:.1f}MB")

        if memory_percent > 80:
            logger.warning(f"⚠️ Uso de memória crítico: {memory_percent:.1f}%")

        return {
            "memory_mb": memory_mb,
            "memory_percent": memory_percent,
            "high": memory_mb > 1000 or memory_percent > 80
        }

    except ImportError:
        logger.warning("psutil não instalado. Monitoramento de memória desabilitado.")
        return {"memory_mb": 0, "memory_percent": 0, "high": False}

    except Exception as e:
        logger.error(f"Erro ao checar memória: {e}")
        return {"memory_mb": 0, "memory_percent": 0, "high": False}


# ==================== CLEANUP UTILITIES ====================

def cleanup_old_session_data():
    """
    Limpa dados antigos do session_state para liberar memória.

    Chame periodicamente (ex: a cada 10 queries).
    """
    try:
        # Limpar mensagens antigas (manter só últimas 50)
        if "messages" in st.session_state:
            messages = st.session_state.messages

            if len(messages) > 50:
                logger.info(f"🧹 Limpando mensagens antigas: {len(messages)} → 50")
                st.session_state.messages = messages[-50:]

        # Limpar cache de gráficos antigos
        if "dashboard_charts" in st.session_state:
            charts = st.session_state.dashboard_charts

            if len(charts) > 20:
                logger.info(f"🧹 Limpando gráficos antigos: {len(charts)} → 20")
                st.session_state.dashboard_charts = charts[-20:]

        logger.info("✅ Cleanup de session data concluído")

    except Exception as e:
        logger.error(f"Erro no cleanup: {e}")


# ==================== HEALTH CHECK ====================

def run_health_check() -> dict:
    """
    Executa health check completo do app.

    Returns:
        Dict com status de saúde
    """
    health = {
        "status": "healthy",
        "issues": [],
        "warnings": []
    }

    # 1. Verificar session state
    required_keys = ["authenticated", "messages", "session_id"]
    if not validate_session_state(required_keys):
        health["issues"].append("Session state incompleto")
        health["status"] = "degraded"

    # 2. Verificar memória
    memory = check_memory_usage()
    if memory["high"]:
        health["warnings"].append(f"Uso de memória alto: {memory['memory_mb']:.1f}MB")

    # 3. Verificar reruns
    if "rerun_monitor" in st.session_state:
        monitor = st.session_state.rerun_monitor

        if monitor["blocked"]:
            health["issues"].append("Loop infinito detectado")
            health["status"] = "unhealthy"

        if monitor["consecutive_reruns"] > 5:
            health["warnings"].append(f"Reruns frequentes: {monitor['consecutive_reruns']}")

    # 4. Verificar backend
    # ✅ CORREÇÃO CONTEXT7: backend_components não está mais no session_state
    # O backend é gerenciado via @st.cache_resource e acessado diretamente
    # Esta verificação não é mais necessária (backend é singleton via cache_resource)

    # Determinar status final
    if health["issues"]:
        if len(health["issues"]) > 2:
            health["status"] = "unhealthy"
        elif health["status"] != "unhealthy":
            health["status"] = "degraded"

    logger.info(f"🏥 Health check: {health['status']}")

    return health


# ==================== EXEMPLO DE USO ====================

if __name__ == "__main__":
    print("="*60)
    print("STREAMLIT STABILITY UTILITIES")
    print("="*60)

    print("\n✅ Módulo carregado com sucesso!")
    print("\nFunções disponíveis:")
    print("  - init_rerun_monitor()")
    print("  - safe_rerun()")
    print("  - @stable_component()")
    print("  - validate_session_state()")
    print("  - check_memory_usage()")
    print("  - cleanup_old_session_data()")
    print("  - run_health_check()")

    print("\nPara usar no streamlit_app.py:")
    print("  from core.utils.streamlit_stability import safe_rerun, stable_component")
    print("  ...")
    print("  safe_rerun()  # ao invés de st.rerun()")
