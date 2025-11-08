"""
✅ OTIMIZAÇÃO v2.2: Integração automática do PerformanceTracker
Decorators e wrappers para tracking automático de performance
"""
import time
import functools
import logging
from typing import Callable, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)


def track_query_performance(query_type: str = "general"):
    """
    Decorator para rastrear performance de queries automaticamente.

    Usage:
        @track_query_performance("sql")
        def execute_sql_query(query):
            ...
            return results

        @track_query_performance("llm")
        def call_llm(prompt):
            ...
            return response
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            result = None

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000

                # Track performance (import lazy para evitar dependência circular)
                try:
                    from core.utils.performance_tracker import get_performance_tracker
                    tracker = get_performance_tracker()
                    tracker.track_query(duration_ms, query_type=query_type, success=success)
                except Exception as track_error:
                    logger.debug(f"Erro ao rastrear performance: {track_error}")

        return wrapper
    return decorator


@contextmanager
def track_startup(component: str = "system"):
    """
    Context manager para rastrear tempo de inicialização de componentes.

    Usage:
        with track_startup("backend"):
            initialize_backend()

        with track_startup("llm"):
            llm_adapter = LLMAdapter()
    """
    start_time = time.time()
    try:
        yield
    finally:
        duration_ms = (time.time() - start_time) * 1000

        try:
            from core.utils.performance_tracker import get_performance_tracker
            tracker = get_performance_tracker()
            tracker.track_startup(duration_ms, component=component)
            logger.info(f"✅ {component} inicializado em {duration_ms:.2f}ms")
        except Exception as e:
            logger.debug(f"Erro ao rastrear startup: {e}")


@contextmanager
def track_query_context(query_type: str = "general"):
    """
    Context manager para rastrear performance de queries.

    Usage:
        with track_query_context("sql"):
            results = execute_sql_query(query)

        with track_query_context("parquet"):
            df = read_parquet(file_path)
    """
    start_time = time.time()
    success = True

    try:
        yield
    except Exception as e:
        success = False
        raise
    finally:
        duration_ms = (time.time() - start_time) * 1000

        try:
            from core.utils.performance_tracker import get_performance_tracker
            tracker = get_performance_tracker()
            tracker.track_query(duration_ms, query_type=query_type, success=success)
        except Exception as track_error:
            logger.debug(f"Erro ao rastrear query: {track_error}")


def track_cache_operation(cache_type: str = "llm"):
    """
    Decorator para rastrear operações de cache.

    Usage:
        @track_cache_operation("llm")
        def get_cached_response(prompt):
            if prompt in cache:
                # Cache hit será rastreado automaticamente
                return cache[prompt]
            else:
                # Cache miss será rastreado automaticamente
                return None
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            try:
                from core.utils.performance_tracker import get_performance_tracker
                tracker = get_performance_tracker()

                # Se resultado não é None, considera cache hit
                if result is not None:
                    tracker.track_cache_hit(cache_type=cache_type)
                else:
                    tracker.track_cache_miss(cache_type=cache_type)

            except Exception as e:
                logger.debug(f"Erro ao rastrear cache: {e}")

            return result

        return wrapper
    return decorator


def manual_track_cache_hit(cache_type: str = "llm"):
    """
    Rastreia cache hit manualmente (para casos onde decorator não é viável).

    Usage:
        if prompt in cache:
            manual_track_cache_hit("llm")
            return cache[prompt]
    """
    try:
        from core.utils.performance_tracker import get_performance_tracker
        tracker = get_performance_tracker()
        tracker.track_cache_hit(cache_type=cache_type)
    except Exception as e:
        logger.debug(f"Erro ao rastrear cache hit: {e}")


def manual_track_cache_miss(cache_type: str = "llm"):
    """
    Rastreia cache miss manualmente (para casos onde decorator não é viável).

    Usage:
        if prompt not in cache:
            manual_track_cache_miss("llm")
            response = call_llm(prompt)
    """
    try:
        from core.utils.performance_tracker import get_performance_tracker
        tracker = get_performance_tracker()
        tracker.track_cache_miss(cache_type=cache_type)
    except Exception as e:
        logger.debug(f"Erro ao rastrear cache miss: {e}")


def track_error(error_msg: str, context: Any = None):
    """
    Rastreia um erro manualmente.

    Usage:
        try:
            execute_query(...)
        except Exception as e:
            track_error(str(e), context=query_time)
            raise
    """
    try:
        from core.utils.performance_tracker import get_performance_tracker
        tracker = get_performance_tracker()
        tracker.track_error(error_msg, context=context)
    except Exception as track_error:
        logger.debug(f"Erro ao rastrear erro: {track_error}")
