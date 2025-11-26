"""
Parquet Cache System with LRU eviction policy
Maintains up to 5 Parquet DataFrames in memory (~500 MB max)
Thread-safe for concurrent access
"""

from collections import OrderedDict
from pathlib import Path
import polars as pl
import threading
import logging

logger = logging.getLogger(__name__)


class ParquetCache:
    """
    Thread-safe LRU cache for Parquet DataFrames
    Singleton pattern ensures single cache instance across the application
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._cache = OrderedDict()
                    cls._instance._max_size = 5  # Max 5 Parquets (~500 MB total)
        return cls._instance

    def get_dataframe(self, parquet_name: str) -> pl.DataFrame:
        """
        Get DataFrame from cache or load from disk

        Args:
            parquet_name: Name of the parquet file (e.g., "admmat.parquet")

        Returns:
            pl.DataFrame: Cached or freshly loaded DataFrame

        Raises:
            FileNotFoundError: If parquet file doesn't exist
        """
        with self._lock:
            # Cache hit - move to end (most recently used)
            if parquet_name in self._cache:
                logger.info(f"✅ Cache HIT: {parquet_name}")
                self._cache.move_to_end(parquet_name)
                return self._cache[parquet_name]

            # Cache miss - load from disk
            logger.info(f"⚠️  Cache MISS: {parquet_name} - Loading from disk...")
            df = self._load_parquet(parquet_name)

            # Add to cache
            self._cache[parquet_name] = df
            logger.info(f"✅ Loaded {parquet_name}: {len(df):,} rows × {len(df.columns)} columns")

            # Evict least recently used if exceeding limit
            if len(self._cache) > self._max_size:
                evicted_key, evicted_df = self._cache.popitem(last=False)
                logger.warning(f"🗑️  Cache EVICT: {evicted_key} (LRU policy - {len(evicted_df):,} rows freed)")

            return df

    def _load_parquet(self, parquet_name: str) -> pl.DataFrame:
        """
        Load Parquet file from disk (hybrid Docker/Dev path support)

        Args:
            parquet_name: Name of the parquet file

        Returns:
            pl.DataFrame: Loaded DataFrame

        Raises:
            FileNotFoundError: If file not found in any location
        """
        # Try Docker path first
        docker_path = Path(f"/app/data/parquet/{parquet_name}")

        # Fallback to development path (4 levels up from this file)
        dev_path = Path(__file__).parent.parent.parent.parent / "data" / "parquet" / parquet_name

        parquet_path = docker_path if docker_path.exists() else dev_path

        if not parquet_path.exists():
            raise FileNotFoundError(
                f"Parquet file not found: {parquet_name}\n"
                f"Tried paths:\n"
                f"  - Docker: {docker_path}\n"
                f"  - Dev: {dev_path}"
            )

        return pl.read_parquet(parquet_path)

    def clear(self):
        """Clear cache (useful for testing or manual refresh)"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"🧹 Cache cleared ({count} entries removed)")

    def get_cache_info(self) -> dict:
        """Get cache statistics"""
        with self._lock:
            return {
                "cached_files": list(self._cache.keys()),
                "cache_size": len(self._cache),
                "max_size": self._max_size,
                "cache_utilization": f"{len(self._cache)}/{self._max_size}"
            }


# Global singleton instance
cache = ParquetCache()
