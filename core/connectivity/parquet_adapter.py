"""
Módulo para core/connectivity/parquet_adapter.py. Define a classe principal 'ParquetAdapter'. Fornece funções utilitárias, incluindo 'connect' e outras. Realiza operações de processamento de dados com Dask.
"""

# core/connectivity/parquet_adapter.py

import logging
import re
from typing import Any, Dict, List
import pandas as pd
import dask.dataframe as dd  # MODIFIED: Import Dask
import os

from .base import DatabaseAdapter

logger = logging.getLogger(__name__)

class ParquetAdapter(DatabaseAdapter):
    """
    Adapter for Parquet files using Dask for out-of-core processing.
    """

    def __init__(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Parquet file not found at: {file_path}")
        self.file_path = file_path
        logger.info(f"ParquetAdapter (Dask) initialized with file: {file_path}")

    def connect(self) -> None:
        """
        No-op. Dask handles connections lazily during query execution.
        This prevents eager loading of the entire file into memory at startup.
        """
        logger.info("ParquetAdapter.connect() is a no-op as Dask handles connections lazily.")
        pass

    def disconnect(self) -> None:
        """
        No-op. Dask handles resource management automatically.
        """
        logger.info("ParquetAdapter.disconnect() is a no-op.")
        pass

    def execute_query(self, query_filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Executes a query using Dask, applying predicate pushdown via filters.
        """
        logger.info(f"Starting Dask query with filters: {query_filters}")

        if not query_filters:
            logger.error("Query without filters is disallowed on Parquet adapter.")
            return [{"error": "A consulta é muito ampla. Adicione filtros (ex: por UNE, segmento) para continuar."}]

        try:
            schema = dd.read_parquet(self.file_path, engine='pyarrow').dtypes.to_dict()
        except Exception as e:
            logger.error(f"Failed to read Parquet schema: {e}")
            return [{"error": "Falha ao ler o esquema do arquivo Parquet.", "details": str(e)}]

        pyarrow_filters = []
        for column, condition in query_filters.items():
            try:
                if column not in schema:
                    logger.warning(f"Column '{column}' not found in Parquet schema. Skipping filter.")
                    continue

                col_type = schema[column]
                
                op = '='
                value = condition

                if isinstance(condition, str) and any(op in condition for op in ['>=', '<=', '!=', '>', '<', '=']):
                    match = re.match(r"(>=|<=|!=|>|<|=)\s*(.*)", str(condition))
                    if match:
                        op, value_str = match.groups()
                        op = op.strip()
                        value_str = value_str.strip()

                        if pd.api.types.is_string_dtype(col_type):
                            value = value_str.strip("'\"")
                        elif pd.api.types.is_numeric_dtype(col_type):
                            try:
                                if '.' in value_str:
                                    value = float(value_str)
                                else:
                                    value = int(value_str)
                            except ValueError:
                                value = value_str.strip("'\"") # Fallback to string if conversion fails
                        else:
                            value = value_str.strip("'\"")
                
                pyarrow_filters.append((column, op, value))

            except Exception as e:
                logger.error(f"Failed to parse filter: {column}={condition}. Error: {e}")
                return [{"error": f"Filtro inválido para a coluna '{column}'"}]

        try:
            logger.info(f"Applying filters to Dask read_parquet: {pyarrow_filters}")
            ddf = dd.read_parquet(
                self.file_path,
                engine='pyarrow',
                filters=pyarrow_filters
            )

            vendas_colunas = [f'mes_{i:02d}' for i in range(1, 13)]
            vendas_colunas_existentes = [col for col in vendas_colunas if col in ddf.columns]
            if vendas_colunas_existentes:
                for col in vendas_colunas_existentes:
                    ddf[col] = dd.to_numeric(ddf[col], errors='coerce')
                ddf['vendas_total'] = ddf[vendas_colunas_existentes].fillna(0).sum(axis=1)

            logger.info("Computing Dask query...")
            computed_df = ddf.compute()

            results = computed_df.to_dict(orient="records")
            logger.info(f"Dask query successful. {len(results)} rows returned.")
            return results
        except Exception as e:
            logger.error(f"Error executing Dask query: {e}", exc_info=True)
            return [{"error": "Falha ao executar a consulta Parquet com Dask.", "details": str(e)}]

    def get_schema(self) -> str:
        """
        Returns the schema by reading Parquet metadata with Dask.
        """
        try:
            # Create a lazy dataframe just to read metadata
            ddf = dd.read_parquet(self.file_path, engine='fastparquet')
            
            schema_str = "Parquet Schema (ADMMATAO.parquet) - via Dask:\n"
            for col_name, dtype in ddf.dtypes.items():
                schema_str += f"  - {col_name}: {dtype}\n"
            logger.info("Parquet schema generated from Dask metadata.")
            return schema_str
        except Exception as e:
            logger.error(f"Could not read Parquet schema: {e}")
            return f"Error reading schema: {e}"
