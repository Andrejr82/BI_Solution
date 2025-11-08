"""
✅ OTIMIZAÇÃO v2.2: Sistema de rastreamento de performance
Monitora tempo de queries, cache hits, startup time e outras métricas críticas
"""
import time
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import deque
import threading

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """
    Rastreador de métricas de performance em tempo real.
    Thread-safe para uso em ambiente multi-usuário.
    """

    def __init__(self, metrics_dir: str = "data/metrics"):
        """
        Inicializa o tracker de performance.

        Args:
            metrics_dir: Diretório para armazenar métricas históricas
        """
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        # Lock para thread safety
        self._lock = threading.Lock()

        # Métricas em memória (últimos 1000 eventos)
        self.query_times = deque(maxlen=1000)
        self.cache_hits = deque(maxlen=1000)
        self.cache_misses = deque(maxlen=1000)
        self.startup_times = deque(maxlen=100)
        self.errors = deque(maxlen=500)

        # Contadores totais
        self.total_queries = 0
        self.total_cache_hits = 0
        self.total_cache_misses = 0
        self.total_errors = 0

        # Timestamp de inicialização
        self.start_time = time.time()

        logger.info(f"✅ PerformanceTracker inicializado - Métricas: {self.metrics_dir}")

    def track_query(self, duration_ms: float, query_type: str = "general", success: bool = True):
        """
        Registra tempo de execução de uma query.

        Args:
            duration_ms: Tempo em milissegundos
            query_type: Tipo de query (general, sql, llm, etc)
            success: Se a query foi bem-sucedida
        """
        with self._lock:
            timestamp = datetime.now().isoformat()
            metric = {
                "timestamp": timestamp,
                "duration_ms": duration_ms,
                "type": query_type,
                "success": success
            }
            self.query_times.append(metric)
            self.total_queries += 1

            if not success:
                self.track_error(f"Query failed: {query_type}", duration_ms)

    def track_cache_hit(self, cache_type: str = "llm"):
        """Registra um cache hit."""
        with self._lock:
            timestamp = datetime.now().isoformat()
            self.cache_hits.append({"timestamp": timestamp, "type": cache_type})
            self.total_cache_hits += 1

    def track_cache_miss(self, cache_type: str = "llm"):
        """Registra um cache miss."""
        with self._lock:
            timestamp = datetime.now().isoformat()
            self.cache_misses.append({"timestamp": timestamp, "type": cache_type})
            self.total_cache_misses += 1

    def track_startup(self, duration_ms: float, component: str = "system"):
        """
        Registra tempo de inicialização de um componente.

        Args:
            duration_ms: Tempo em milissegundos
            component: Nome do componente (system, backend, llm, etc)
        """
        with self._lock:
            timestamp = datetime.now().isoformat()
            metric = {
                "timestamp": timestamp,
                "duration_ms": duration_ms,
                "component": component
            }
            self.startup_times.append(metric)

    def track_error(self, error_msg: str, context: Optional[float] = None):
        """
        Registra um erro.

        Args:
            error_msg: Mensagem de erro
            context: Contexto adicional (ex: tempo de query quando falhou)
        """
        with self._lock:
            timestamp = datetime.now().isoformat()
            self.errors.append({
                "timestamp": timestamp,
                "error": error_msg,
                "context": context
            })
            self.total_errors += 1

    def get_stats(self, window_minutes: int = 60) -> Dict:
        """
        Retorna estatísticas de performance da janela especificada.

        Args:
            window_minutes: Janela de tempo em minutos

        Returns:
            Dicionário com estatísticas de performance
        """
        with self._lock:
            now = datetime.now()
            cutoff = now - timedelta(minutes=window_minutes)

            # Filtrar queries recentes
            recent_queries = [
                q for q in self.query_times
                if datetime.fromisoformat(q["timestamp"]) > cutoff
            ]

            # Calcular estatísticas de queries
            if recent_queries:
                durations = [q["duration_ms"] for q in recent_queries]
                avg_query_time = sum(durations) / len(durations)
                min_query_time = min(durations)
                max_query_time = max(durations)
                p95_query_time = sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 10 else max_query_time
            else:
                avg_query_time = 0
                min_query_time = 0
                max_query_time = 0
                p95_query_time = 0

            # Filtrar cache hits/misses recentes
            recent_hits = [
                h for h in self.cache_hits
                if datetime.fromisoformat(h["timestamp"]) > cutoff
            ]
            recent_misses = [
                m for m in self.cache_misses
                if datetime.fromisoformat(m["timestamp"]) > cutoff
            ]

            total_cache_ops = len(recent_hits) + len(recent_misses)
            cache_hit_rate = (len(recent_hits) / total_cache_ops * 100) if total_cache_ops > 0 else 0

            # Filtrar erros recentes
            recent_errors = [
                e for e in self.errors
                if datetime.fromisoformat(e["timestamp"]) > cutoff
            ]

            # Uptime
            uptime_seconds = time.time() - self.start_time

            return {
                "window_minutes": window_minutes,
                "uptime_seconds": uptime_seconds,
                "uptime_formatted": self._format_uptime(uptime_seconds),

                # Query stats
                "total_queries": len(recent_queries),
                "avg_query_time_ms": round(avg_query_time, 2),
                "min_query_time_ms": round(min_query_time, 2),
                "max_query_time_ms": round(max_query_time, 2),
                "p95_query_time_ms": round(p95_query_time, 2),
                "queries_per_minute": round(len(recent_queries) / window_minutes, 2) if window_minutes > 0 else 0,

                # Cache stats
                "cache_hits": len(recent_hits),
                "cache_misses": len(recent_misses),
                "cache_hit_rate": round(cache_hit_rate, 2),

                # Error stats
                "errors": len(recent_errors),
                "error_rate": round((len(recent_errors) / len(recent_queries) * 100), 2) if recent_queries else 0,

                # Lifetime totals
                "lifetime_queries": self.total_queries,
                "lifetime_cache_hits": self.total_cache_hits,
                "lifetime_cache_misses": self.total_cache_misses,
                "lifetime_errors": self.total_errors,
                "lifetime_cache_hit_rate": round(
                    (self.total_cache_hits / (self.total_cache_hits + self.total_cache_misses) * 100)
                    if (self.total_cache_hits + self.total_cache_misses) > 0 else 0,
                    2
                )
            }

    def get_startup_stats(self) -> Dict:
        """Retorna estatísticas de startup time."""
        with self._lock:
            if not self.startup_times:
                return {
                    "count": 0,
                    "avg_startup_ms": 0,
                    "min_startup_ms": 0,
                    "max_startup_ms": 0,
                    "last_startup_ms": 0
                }

            durations = [s["duration_ms"] for s in self.startup_times]
            return {
                "count": len(durations),
                "avg_startup_ms": round(sum(durations) / len(durations), 2),
                "min_startup_ms": round(min(durations), 2),
                "max_startup_ms": round(max(durations), 2),
                "last_startup_ms": round(durations[-1], 2)
            }

    def get_recent_queries(self, limit: int = 10) -> List[Dict]:
        """Retorna as últimas N queries."""
        with self._lock:
            return list(self.query_times)[-limit:]

    def get_recent_errors(self, limit: int = 10) -> List[Dict]:
        """Retorna os últimos N erros."""
        with self._lock:
            return list(self.errors)[-limit:]

    def save_snapshot(self):
        """Salva snapshot das métricas em arquivo JSON."""
        try:
            stats = self.get_stats(window_minutes=60)
            startup_stats = self.get_startup_stats()

            snapshot = {
                "timestamp": datetime.now().isoformat(),
                "stats": stats,
                "startup": startup_stats
            }

            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.metrics_dir / filename

            with open(filepath, 'w') as f:
                json.dump(snapshot, f, indent=2)

            logger.info(f"✅ Snapshot de métricas salvo: {filepath}")

        except Exception as e:
            logger.error(f"❌ Erro ao salvar snapshot de métricas: {e}")

    def _format_uptime(self, seconds: float) -> str:
        """Formata uptime em formato legível."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

    def reset(self):
        """Reseta todas as métricas (use com cuidado)."""
        with self._lock:
            self.query_times.clear()
            self.cache_hits.clear()
            self.cache_misses.clear()
            self.startup_times.clear()
            self.errors.clear()

            self.total_queries = 0
            self.total_cache_hits = 0
            self.total_cache_misses = 0
            self.total_errors = 0

            self.start_time = time.time()

            logger.warning("⚠️ Métricas de performance resetadas")


# Singleton global
_performance_tracker = None


def get_performance_tracker() -> PerformanceTracker:
    """Retorna instância singleton do PerformanceTracker."""
    global _performance_tracker
    if _performance_tracker is None:
        _performance_tracker = PerformanceTracker()
    return _performance_tracker
