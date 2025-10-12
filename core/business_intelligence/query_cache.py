"""
Query Cache Semântico - Armazena queries e respostas frequentes.
Reduz consumo de tokens do Gemini ao reutilizar classificações de queries similares.

ZERO RISCO: Este arquivo é NOVO e não afeta o sistema atual.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path

from core.utils.logger_config import get_logger

logger = get_logger('agent_bi.query_cache')


class QueryCache:
    """
    Cache semântico para queries e suas classificações.

    Funcionalidades:
    - Armazena pares (query, intent_classification)
    - Match semântico (não precisa ser exato)
    - Persistência em disco
    - Expiração configurável
    - Estatísticas de hit rate
    """

    def __init__(self, cache_dir: str = "data/cache", ttl_hours: int = 24):
        """
        Inicializa o cache.

        Args:
            cache_dir: Diretório para persistir cache
            ttl_hours: Time-to-live em horas (0 = sem expiração)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.cache_file = self.cache_dir / "query_cache.json"
        self.ttl_hours = ttl_hours

        # Estatísticas
        self.hits = 0
        self.misses = 0
        self.saves = 0

        # Carregar cache do disco
        self.cache = self._load_cache()

        logger.info(f"[OK] QueryCache inicializado: {len(self.cache)} entradas, TTL={ttl_hours}h")

    def _load_cache(self) -> Dict[str, Any]:
        """Carrega cache do disco."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    logger.info(f"[INFO] Cache carregado: {len(cache)} entradas")
                    return cache
            except Exception as e:
                logger.error(f"[ERRO] Erro ao carregar cache: {e}")
                return {}
        return {}

    def _save_cache(self):
        """Salva cache no disco."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            logger.debug(f"[INFO] Cache salvo: {len(self.cache)} entradas")
        except Exception as e:
            logger.error(f"[ERRO] Erro ao salvar cache: {e}")

    def _normalize_query(self, query: str) -> str:
        """
        Normaliza query para comparação.

        Args:
            query: Query original

        Returns:
            Query normalizada (lowercase, sem espaços extras, etc.)
        """
        # Lowercase
        normalized = query.lower().strip()

        # Remover espaços múltiplos
        normalized = ' '.join(normalized.split())

        # Remover pontuação no final
        normalized = normalized.rstrip('?!.')

        return normalized

    def _get_cache_key(self, query: str) -> str:
        """
        Gera chave de cache para uma query.

        Args:
            query: Query original

        Returns:
            Hash MD5 da query normalizada
        """
        normalized = self._normalize_query(query)
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()

    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Busca query no cache.

        Args:
            query: Query do usuário

        Returns:
            Intent classificado se encontrado, None se não encontrado
        """
        try:
            # Busca exata primeiro
            cache_key = self._get_cache_key(query)

            if cache_key in self.cache:
                entry = self.cache[cache_key]

                # Verificar expiração
                if self.ttl_hours > 0:
                    cached_time = datetime.fromisoformat(entry['timestamp'])
                    age = datetime.now() - cached_time

                    if age > timedelta(hours=self.ttl_hours):
                        logger.debug(f"[INFO] Cache expirado para: {query[:50]}...")
                        del self.cache[cache_key]
                        self._save_cache()
                        self.misses += 1
                        return None

                # Cache hit!
                self.hits += 1
                intent = entry['intent']
                logger.info(f"[OK] CACHE HIT: {query[:50]}... -> {intent.get('operation', 'unknown')}")
                return intent

            # Busca semântica (queries similares)
            # TODO: Implementar busca por similaridade se necessário

            # Cache miss
            self.misses += 1
            logger.debug(f"[INFO] CACHE MISS: {query[:50]}...")
            return None

        except Exception as e:
            logger.error(f"[ERRO] Erro ao buscar cache: {e}")
            return None

    def set(self, query: str, intent: Dict[str, Any]):
        """
        Armazena query e intent no cache.

        Args:
            query: Query do usuário
            intent: Intent classificado pelo IntentClassifier
        """
        try:
            cache_key = self._get_cache_key(query)

            entry = {
                'query': query,
                'normalized': self._normalize_query(query),
                'intent': intent,
                'timestamp': datetime.now().isoformat(),
                'hit_count': self.cache.get(cache_key, {}).get('hit_count', 0)
            }

            self.cache[cache_key] = entry
            self.saves += 1

            # Salvar no disco a cada 10 saves
            if self.saves % 10 == 0:
                self._save_cache()

            logger.debug(f"[INFO] Cached: {query[:50]}... -> {intent.get('operation', 'unknown')}")

        except Exception as e:
            logger.error(f"[ERRO] Erro ao salvar cache: {e}")

    def get_similar_queries(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Busca queries similares no cache.

        Args:
            query: Query do usuário
            limit: Número máximo de resultados

        Returns:
            Lista de queries similares com seus intents
        """
        normalized = self._normalize_query(query)
        query_words = set(normalized.split())

        similar = []

        for key, entry in self.cache.items():
            cached_normalized = entry.get('normalized', '')
            cached_words = set(cached_normalized.split())

            # Calcular similaridade (Jaccard)
            intersection = query_words & cached_words
            union = query_words | cached_words

            if union:
                similarity = len(intersection) / len(union)

                if similarity > 0.5:  # Threshold de 50%
                    similar.append({
                        'query': entry['query'],
                        'similarity': similarity,
                        'intent': entry['intent']
                    })

        # Ordenar por similaridade
        similar.sort(key=lambda x: x['similarity'], reverse=True)

        return similar[:limit]

    def clear_expired(self):
        """Remove entradas expiradas do cache."""
        if self.ttl_hours <= 0:
            return

        now = datetime.now()
        expired_keys = []

        for key, entry in self.cache.items():
            try:
                cached_time = datetime.fromisoformat(entry['timestamp'])
                age = now - cached_time

                if age > timedelta(hours=self.ttl_hours):
                    expired_keys.append(key)
            except Exception:
                continue

        for key in expired_keys:
            del self.cache[key]

        if expired_keys:
            logger.info(f"[INFO] Removidas {len(expired_keys)} entradas expiradas")
            self._save_cache()

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "total_entries": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "saves": self.saves,
            "ttl_hours": self.ttl_hours,
            "cache_file": str(self.cache_file)
        }

    def get_most_frequent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retorna queries mais frequentes.

        Args:
            limit: Número de queries a retornar

        Returns:
            Lista de queries ordenadas por frequência
        """
        entries = list(self.cache.values())
        entries.sort(key=lambda x: x.get('hit_count', 0), reverse=True)

        return [{
            'query': e['query'],
            'operation': e['intent'].get('operation', 'unknown'),
            'hit_count': e.get('hit_count', 0),
            'timestamp': e['timestamp']
        } for e in entries[:limit]]

    def export_to_patterns(self, output_file: str = "data/learned_patterns.json"):
        """
        Exporta queries frequentes como patterns para aprendizado.

        Args:
            output_file: Arquivo de saída
        """
        try:
            frequent_queries = self.get_most_frequent(limit=50)

            patterns = []
            for q in frequent_queries:
                if q['hit_count'] > 5:  # Só queries com 5+ hits
                    patterns.append({
                        "example_query": q['query'],
                        "operation": q['operation'],
                        "hit_count": q['hit_count'],
                        "learned_at": q['timestamp']
                    })

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "generated_at": datetime.now().isoformat(),
                        "total_patterns": len(patterns),
                        "description": "Patterns aprendidos automaticamente"
                    },
                    "patterns": patterns
                }, f, indent=2, ensure_ascii=False)

            logger.info(f"[INFO] Exportados {len(patterns)} patterns para {output_file}")

        except Exception as e:
            logger.error(f"[ERRO] Erro ao exportar patterns: {e}")

    def __del__(self):
        """Salva cache ao destruir objeto."""
        try:
            self._save_cache()
        except Exception:
            pass
