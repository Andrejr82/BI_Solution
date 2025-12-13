"""
ParquetAdapter: Adaptador para arquivos Parquet.
Versão Async para FastAPI.
"""

import logging
from typing import Any, Dict, List, Optional

from app.infrastructure.data.base import DatabaseAdapter
from app.infrastructure.data.polars_dask_adapter import PolarsDaskAdapter

logger = logging.getLogger(__name__)

class ParquetAdapter(DatabaseAdapter):
    """
    Adapter for Parquet files usando PolarsDaskAdapter (híbrido Polars+Dask).
    Async wrapper.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._hybrid = PolarsDaskAdapter(file_path)
        logger.info(f"ParquetAdapter initialized with PolarsDaskAdapter")

    async def connect(self) -> None:
        await self._hybrid.connect()

    async def disconnect(self) -> None:
        await self._hybrid.disconnect()

    async def execute_query(self, query_filters: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
        """
        Executa query usando PolarsDaskAdapter (híbrido).
        """
        return await self._hybrid.execute_query(query_filters, **kwargs)

    async def get_schema(self) -> str:
        return await self._hybrid.get_schema()
