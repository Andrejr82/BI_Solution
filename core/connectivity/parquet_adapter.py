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
        # 🚀 Suportar padrões como "*.parquet" (Dask resolve automaticamente)
        if "*" not in file_path and not os.path.exists(file_path):
            raise FileNotFoundError(f"Parquet file not found at: {file_path}")
        elif "*" in file_path:
            # Verificar se o diretório existe
            import glob
            base_dir = os.path.dirname(file_path)
            if not os.path.exists(base_dir):
                raise FileNotFoundError(f"Parquet directory not found at: {base_dir}")
            # Verificar se há arquivos Parquet
            matching_files = glob.glob(file_path)
            if not matching_files:
                raise FileNotFoundError(f"No Parquet files matching pattern: {file_path}")
            logger.info(f"ParquetAdapter (Dask) found {len(matching_files)} file(s) matching pattern: {file_path}")
        self.file_path = file_path
        logger.info(f"ParquetAdapter (Dask) initialized with pattern: {file_path}")

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
        Executes a query using Dask.

        Strategy:
        1. Apply only STRING filters to Dask (safe for PyArrow)
        2. Load data and convert types (ESTOQUE_UNE, etc.)
        3. Apply NUMERIC filters in pandas after conversion
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

        # Separate filters: string filters (safe for PyArrow) vs numeric filters (apply in pandas)
        pyarrow_filters = []
        pandas_filters = []

        # Columns that need type conversion BEFORE filtering
        NUMERIC_COLUMNS_IN_STRING_FORMAT = ['estoque_une', 'ESTOQUE_UNE', 'estoque_atual']

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

                        # Check if this is a numeric comparison on a string-typed column
                        if column in NUMERIC_COLUMNS_IN_STRING_FORMAT and op in ['>=', '<=', '>', '<']:
                            # Defer to pandas (after type conversion)
                            try:
                                numeric_value = float(value_str) if '.' in value_str else int(value_str)
                                pandas_filters.append((column, op, numeric_value))
                                logger.info(f"Deferred numeric filter to pandas: {column} {op} {numeric_value}")
                                continue
                            except ValueError:
                                pass

                        if pd.api.types.is_string_dtype(col_type):
                            value = value_str.strip("'\"")
                        elif pd.api.types.is_numeric_dtype(col_type):
                            try:
                                if '.' in value_str:
                                    value = float(value_str)
                                else:
                                    value = int(value_str)
                            except ValueError:
                                value = value_str.strip("'\"")
                        else:
                            value = value_str.strip("'\"")

                pyarrow_filters.append((column, op, value))

            except Exception as e:
                logger.error(f"Failed to parse filter: {column}={condition}. Error: {e}")
                return [{"error": f"Filtro inválido para a coluna '{column}'"}]

        try:
            # Read Parquet with only string filters (safe for PyArrow)
            if pyarrow_filters:
                logger.info(f"Applying PyArrow filters: {pyarrow_filters}")
                ddf = dd.read_parquet(
                    self.file_path,
                    engine='pyarrow',
                    filters=pyarrow_filters
                )
            else:
                logger.info("No PyArrow filters. Reading full dataset.")
                ddf = dd.read_parquet(self.file_path, engine='pyarrow')

            logger.info("Computing Dask query...")
            computed_df = ddf.compute()

            # Convert types BEFORE applying numeric filters
            logger.info("Converting data types...")

            # Convert ESTOQUE columns from string to numeric
            for col in ['estoque_une', 'ESTOQUE_UNE', 'estoque_atual']:
                if col in computed_df.columns:
                    original_type = computed_df[col].dtype
                    computed_df[col] = pd.to_numeric(computed_df[col], errors='coerce')
                    invalid_count = computed_df[col].isna().sum()
                    computed_df[col] = computed_df[col].fillna(0)
                    logger.info(f"✅ {col} converted: {original_type} → float64 ({invalid_count} invalid values → 0)")

            # Convert vendas columns
            vendas_colunas = [f'mes_{i:02d}' for i in range(1, 13)]
            vendas_colunas_existentes = [col for col in vendas_colunas if col in computed_df.columns]
            if vendas_colunas_existentes:
                for col in vendas_colunas_existentes:
                    computed_df[col] = pd.to_numeric(computed_df[col], errors='coerce')
                computed_df['vendas_total'] = computed_df[vendas_colunas_existentes].fillna(0).sum(axis=1)

            # NOW apply numeric filters in pandas (after type conversion)
            if pandas_filters:
                logger.info(f"Applying pandas filters after type conversion: {pandas_filters}")
                for column, op, value in pandas_filters:
                    if op == '>=':
                        computed_df = computed_df[computed_df[column] >= value]
                    elif op == '<=':
                        computed_df = computed_df[computed_df[column] <= value]
                    elif op == '>':
                        computed_df = computed_df[computed_df[column] > value]
                    elif op == '<':
                        computed_df = computed_df[computed_df[column] < value]
                    elif op == '=':
                        computed_df = computed_df[computed_df[column] == value]
                    elif op == '!=':
                        computed_df = computed_df[computed_df[column] != value]

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
