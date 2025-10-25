"""
Módulo para core/connectivity/parquet_adapter.py. Define a classe principal 'ParquetAdapter'. Fornece funções utilitárias, incluindo 'connect' e outras. Realiza operações de processamento de dados com Dask.

ATUALIZADO 2025-10-20: Agora usa PolarsDaskAdapter internamente (arquitetura híbrida).
"""

# core/connectivity/parquet_adapter.py

import logging
import re
from typing import Any, Dict, List
import pandas as pd
import dask.dataframe as dd  # Mantido para compatibilidade
import os

from .base import DatabaseAdapter
from .polars_dask_adapter import PolarsDaskAdapter  # NOVO: Adapter híbrido

logger = logging.getLogger(__name__)

class ParquetAdapter(DatabaseAdapter):
    """
    Adapter for Parquet files usando PolarsDaskAdapter (híbrido Polars+Dask).

    Mantém 100% compatibilidade com interface anterior, mas agora usa:
    - Polars para arquivos < 500MB (8.1x mais rápido)
    - Dask para arquivos >= 500MB (escalável)
    - Fallback automático Polars → Dask em caso de erro
    """

    def __init__(self, file_path: str):
        # Validação básica mantida (compatibilidade)
        if "*" not in file_path and not os.path.exists(file_path):
            raise FileNotFoundError(f"Parquet file not found at: {file_path}")
        elif "*" in file_path:
            import glob
            base_dir = os.path.dirname(file_path)
            if not os.path.exists(base_dir):
                raise FileNotFoundError(f"Parquet directory not found at: {base_dir}")
            matching_files = glob.glob(file_path)
            if not matching_files:
                raise FileNotFoundError(f"No Parquet files matching pattern: {file_path}")
            logger.info(f"ParquetAdapter found {len(matching_files)} file(s) matching pattern: {file_path}")

        self.file_path = file_path

        # NOVO: Delegar para PolarsDaskAdapter (arquitetura híbrida)
        self._hybrid = PolarsDaskAdapter(file_path)
        logger.info(f"ParquetAdapter initialized with PolarsDaskAdapter (engine: {self._hybrid.engine})")

    def connect(self) -> None:
        """No-op. Delegado para PolarsDaskAdapter."""
        self._hybrid.connect()

    def disconnect(self) -> None:
        """No-op. Delegado para PolarsDaskAdapter."""
        self._hybrid.disconnect()

    def execute_query(self, query_filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Executa query usando PolarsDaskAdapter (híbrido).

        Delegação transparente - mantém 100% compatibilidade.
        """
        logger.info(f"ParquetAdapter.execute_query() delegando para PolarsDaskAdapter...")
        # Delegação completa para PolarsDaskAdapter
        return self._hybrid.execute_query(query_filters)

    def get_schema(self) -> str:
        """Retorna schema. Delegado para PolarsDaskAdapter."""
        return self._hybrid.get_schema()
