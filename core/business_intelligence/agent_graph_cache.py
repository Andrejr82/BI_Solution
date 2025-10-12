"""
Cache inteligente para agent_graph - Reduz latência e custos
Armazena resultados de queries similares para evitar chamadas LLM repetidas.
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import pickle

logger = logging.getLogger(__name__)

class AgentGraphCache:
    """Cache inteligente para o agent_graph com expiração e similaridade"""

    def __init__(self, cache_dir: str = "data/cache_agent_graph", ttl_hours: int = 24):
        """
        Inicializa o cache.

        Args:
            cache_dir: Diretório para armazenar cache
            ttl_hours: Tempo de vida do cache em horas (padrão: 24h)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)

        # Cache em memória para acesso ultra-rápido
        self._memory_cache: Dict[str, Dict[str, Any]] = {}

        logger.info(f"✅ AgentGraphCache inicializado - TTL: {ttl_hours}h")

    def _normalize_query(self, query: str) -> str:
        """Normaliza query para melhor matching"""
        # Remove espaços extras, pontuação, e converte para minúsculas
        normalized = query.lower().strip()
        normalized = ' '.join(normalized.split())  # Remove múltiplos espaços
        return normalized

    def _generate_cache_key(self, query: str) -> str:
        """Gera chave única para a query"""
        normalized = self._normalize_query(query)
        return hashlib.md5(normalized.encode()).hexdigest()

    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Obtém resultado do cache se disponível e válido.

        Args:
            query: Query do usuário

        Returns:
            Resultado cacheado ou None
        """
        cache_key = self._generate_cache_key(query)

        # 1. Verificar cache em memória (mais rápido)
        if cache_key in self._memory_cache:
            cached = self._memory_cache[cache_key]

            # Verificar expiração
            cached_time = datetime.fromisoformat(cached['timestamp'])
            if datetime.now() - cached_time < self.ttl:
                logger.info(f"✅ CACHE HIT (memory) - Query: '{query[:50]}...'")
                cached['cache_hit'] = True
                cached['cache_source'] = 'memory'
                return cached['result']
            else:
                # Remover cache expirado
                del self._memory_cache[cache_key]
                logger.info(f"⏰ Cache expirado (memory) - Query: '{query[:50]}...'")

        # 2. Verificar cache em disco
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    cached = pickle.load(f)

                # Verificar expiração
                cached_time = datetime.fromisoformat(cached['timestamp'])
                if datetime.now() - cached_time < self.ttl:
                    # Recarregar para memória
                    self._memory_cache[cache_key] = cached

                    logger.info(f"✅ CACHE HIT (disk) - Query: '{query[:50]}...'")
                    cached['cache_hit'] = True
                    cached['cache_source'] = 'disk'
                    return cached['result']
                else:
                    # Remover cache expirado
                    cache_file.unlink()
                    logger.info(f"⏰ Cache expirado (disk) - Query: '{query[:50]}...'")
            except Exception as e:
                logger.error(f"❌ Erro ao ler cache: {e}")
                cache_file.unlink(missing_ok=True)

        logger.info(f"❌ CACHE MISS - Query: '{query[:50]}...'")
        return None

    def set(self, query: str, result: Dict[str, Any], metadata: Optional[Dict] = None):
        """
        Armazena resultado no cache.

        Args:
            query: Query do usuário
            result: Resultado do agent_graph
            metadata: Metadados adicionais (opcional)
        """
        cache_key = self._generate_cache_key(query)

        cached_data = {
            'query': query,
            'result': result,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        # 1. Armazenar em memória
        self._memory_cache[cache_key] = cached_data

        # 2. Armazenar em disco (persistência)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(cached_data, f)
            logger.info(f"💾 Cache salvo - Query: '{query[:50]}...'")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar cache: {e}")

    def clear_expired(self):
        """Remove entradas expiradas do cache"""
        now = datetime.now()
        expired_count = 0

        # Limpar memória
        expired_keys = [
            key for key, data in self._memory_cache.items()
            if now - datetime.fromisoformat(data['timestamp']) >= self.ttl
        ]
        for key in expired_keys:
            del self._memory_cache[key]
            expired_count += 1

        # Limpar disco
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                with open(cache_file, 'rb') as f:
                    cached = pickle.load(f)

                cached_time = datetime.fromisoformat(cached['timestamp'])
                if now - cached_time >= self.ttl:
                    cache_file.unlink()
                    expired_count += 1
            except Exception as e:
                logger.warning(f"Erro ao verificar {cache_file.name}: {e}")
                cache_file.unlink(missing_ok=True)

        if expired_count > 0:
            logger.info(f"🧹 Cache limpo - {expired_count} entradas expiradas removidas")

    def clear_all(self):
        """Remove todo o cache"""
        self._memory_cache.clear()

        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()

        logger.info("🧹 Todo o cache foi limpo")

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        return {
            'memory_entries': len(self._memory_cache),
            'disk_entries': len(list(self.cache_dir.glob("*.pkl"))),
            'cache_dir': str(self.cache_dir),
            'ttl_hours': self.ttl.total_seconds() / 3600
        }


# Instância global (singleton)
_cache_instance = None

def get_agent_graph_cache() -> AgentGraphCache:
    """Obtém instância singleton do cache"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = AgentGraphCache()
    return _cache_instance
