"""
Semantic Cache - Cache inteligente baseado em similaridade semântica
Permite respostas instantâneas para perguntas similares
"""

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class SemanticCache:
    """
    Cache semântico para respostas do ChatBI.
    
    Características:
    - Hash baseado em normalização da query
    - TTL configurável
    - Persistência em disco
    - Estatísticas de hit/miss
    """
    
    def __init__(
        self, 
        cache_dir: str = "data/cache/semantic",
        ttl_minutes: int = 360,  # 6 horas
        max_entries: int = 1000
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_minutes * 60
        self.max_entries = max_entries
        
        # Estatísticas
        self.hits = 0
        self.misses = 0
        
        # Index em memória para busca rápida
        self._index: Dict[str, Dict[str, Any]] = {}
        self._load_index()
        
        logger.info(f"SemanticCache inicializado: {cache_dir}, TTL={ttl_minutes}min")
    
    def _normalize_query(self, query: str) -> str:
        """Normaliza query para melhor matching."""
        # Converter para minúsculas
        normalized = query.lower().strip()
        
        # Remover pontuação desnecessária
        for char in "?!.,;:":
            normalized = normalized.replace(char, "")
        
        # Normalizar espaços múltiplos
        normalized = " ".join(normalized.split())
        
        return normalized
    
    def _generate_key(self, query: str) -> str:
        """Gera chave hash para a query normalizada."""
        normalized = self._normalize_query(query)
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def _load_index(self):
        """Carrega índice do disco."""
        index_file = self.cache_dir / "index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    self._index = json.load(f)
                logger.info(f"Cache index carregado: {len(self._index)} entradas")
            except Exception as e:
                logger.error(f"Erro ao carregar cache index: {e}")
                self._index = {}
    
    def _save_index(self):
        """Salva índice no disco."""
        index_file = self.cache_dir / "index.json"
        try:
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(self._index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar cache index: {e}")
    
    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Busca resposta em cache.
        
        Args:
            query: Pergunta do usuário
            
        Returns:
            Resposta cacheada ou None se não encontrada/expirada
        """
        key = self._generate_key(query)
        
        if key not in self._index:
            self.misses += 1
            return None
        
        entry = self._index[key]
        
        # Verificar TTL
        if time.time() - entry.get("timestamp", 0) > self.ttl_seconds:
            # Expirado - remover
            self._remove_entry(key)
            self.misses += 1
            logger.debug(f"Cache expirado para: {query[:50]}...")
            return None
        
        # Cache hit!
        self.hits += 1
        logger.info(f"Cache HIT para: {query[:50]}... (hits={self.hits})")
        
        # Carregar resposta do arquivo
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao ler cache file: {e}")
                return None
        
        return None
    
    def set(self, query: str, response: Dict[str, Any]) -> bool:
        """
        Armazena resposta em cache.
        
        Args:
            query: Pergunta do usuário
            response: Resposta a cachear
            
        Returns:
            True se armazenado com sucesso
        """
        key = self._generate_key(query)
        
        # Verificar limite de entradas
        if len(self._index) >= self.max_entries:
            self._cleanup_oldest()
        
        # Atualizar índice
        self._index[key] = {
            "query": query,
            "normalized": self._normalize_query(query),
            "timestamp": time.time(),
        }
        
        # Salvar resposta em arquivo
        cache_file = self.cache_dir / f"{key}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(response, f, ensure_ascii=False, indent=2)
            
            self._save_index()
            logger.debug(f"Cache SET para: {query[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")
            return False
    
    def _remove_entry(self, key: str):
        """Remove entrada do cache."""
        if key in self._index:
            del self._index[key]
            
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            cache_file.unlink()
        
        self._save_index()
    
    def _cleanup_oldest(self, remove_count: int = 100):
        """Remove entradas mais antigas."""
        if not self._index:
            return
        
        # Ordenar por timestamp
        sorted_entries = sorted(
            self._index.items(),
            key=lambda x: x[1].get("timestamp", 0)
        )
        
        # Remover as mais antigas
        for key, _ in sorted_entries[:remove_count]:
            self._remove_entry(key)
        
        logger.info(f"Cache cleanup: removidas {remove_count} entradas antigas")
    
    def clear(self):
        """Limpa todo o cache."""
        for key in list(self._index.keys()):
            self._remove_entry(key)
        self._index = {}
        self._save_index()
        logger.info("Cache limpo completamente")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            "entries": len(self._index),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "cache_dir": str(self.cache_dir),
        }


# Instância global do cache
_semantic_cache: Optional[SemanticCache] = None


def get_semantic_cache() -> SemanticCache:
    """Retorna instância singleton do cache."""
    global _semantic_cache
    if _semantic_cache is None:
        _semantic_cache = SemanticCache()
    return _semantic_cache


# Funções de conveniência
def cache_get(query: str) -> Optional[Dict[str, Any]]:
    """Busca resposta em cache."""
    return get_semantic_cache().get(query)


def cache_set(query: str, response: Dict[str, Any]) -> bool:
    """Armazena resposta em cache."""
    return get_semantic_cache().set(query, response)


def cache_stats() -> Dict[str, Any]:
    """Retorna estatísticas do cache."""
    return get_semantic_cache().get_stats()
