import logging
from typing import Any, Dict, List
import pandas as pd
import os

from .base import DatabaseAdapter
from core.utils.memory_optimizer import MemoryOptimizer

logger = logging.getLogger(__name__)

class ParquetAdapter(DatabaseAdapter):
    """Concrete implementation of the adapter for Parquet files."""

    def __init__(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Parquet file not found at: {file_path}")
        self.file_path = file_path
        self._dataframe = None
        logger.info(f"ParquetAdapter initialized with file: {file_path}")

    def _load_dataframe(self):
        """
        Loads the parquet file into a pandas DataFrame if not already loaded.
        Optimized for Streamlit Cloud memory limits.
        """
        if self._dataframe is None:
            MemoryOptimizer.log_memory_usage("Before loading Parquet")
            logger.info(f"Loading Parquet file from {self.file_path}...")

            # OTIMIZAÇÃO STREAMLIT CLOUD: Carregar colunas essenciais + análises avançadas
            essential_cols = [
                # Básicas
                'codigo', 'nome_produto', 'preco_38_percent', 'nomesegmento',
                'nome_categoria', 'nome_fabricante', 'une', 'une_nome',
                # Vendas mensais
                'mes_01', 'mes_02', 'mes_03', 'mes_04', 'mes_05', 'mes_06',
                'mes_07', 'mes_08', 'mes_09', 'mes_10', 'mes_11', 'mes_12',
                # Frequência semanal (ciclo vendas)
                'freq_semana_anterior_5', 'freq_semana_anterior_4', 'freq_semana_anterior_3',
                'freq_semana_anterior_2', 'freq_semana_atual',
                # Estoque e logística
                'estoque_atual', 'estoque_cd', 'venda_30_d', 'leadtime_lv',
                'exposicao_minima_une'
            ]

            try:
                self._dataframe = pd.read_parquet(self.file_path, columns=essential_cols)
            except:
                # Fallback: carregar tudo se colunas específicas falharem
                self._dataframe = pd.read_parquet(self.file_path)

            logger.info(f"Parquet file loaded. Shape: {self._dataframe.shape}")

            # CRIAR COLUNA VENDAS_TOTAL: Somar vendas de todos os meses
            vendas_colunas = [f'mes_{i:02d}' for i in range(1, 13)]
            vendas_colunas_existentes = [col for col in vendas_colunas if col in self._dataframe.columns]

            if vendas_colunas_existentes:
                logger.info(f"Criando coluna vendas_total com colunas: {vendas_colunas_existentes}")
                # Converter para numérico antes de somar (corrige tipos mistos)
                for col in vendas_colunas_existentes:
                    self._dataframe[col] = pd.to_numeric(self._dataframe[col], errors='coerce')
                self._dataframe['vendas_total'] = self._dataframe[vendas_colunas_existentes].fillna(0).sum(axis=1)
                logger.info(f"Coluna vendas_total criada. Min: {self._dataframe['vendas_total'].min()}, Max: {self._dataframe['vendas_total'].max()}")
            else:
                logger.warning("Nenhuma coluna de vendas mensal encontrada!")

            # Otimizar uso de memória
            self._dataframe = MemoryOptimizer.optimize_dataframe_memory(self._dataframe)
            MemoryOptimizer.log_memory_usage("After loading and optimizing Parquet")

    def connect(self) -> None:
        """
        For Parquet, 'connect' means ensuring the DataFrame is loaded.
        """
        self._load_dataframe()

    def disconnect(self) -> None:
        """
        For Parquet, 'disconnect' means clearing the DataFrame from memory.
        """
        self._dataframe = None
        logger.info("Parquet DataFrame cleared from memory.")

    def execute_query(self, query_filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Executes a query (filters) on the Parquet DataFrame.
        query_filters example: {"column_name": "value", "another_column": ">10"}
        """
        logger.info(f"Starting execute_query with filters: {query_filters}")

        self._load_dataframe()
        if self._dataframe is None:
            logger.error("DataFrame not loaded, returning error")
            return [{"error": "DataFrame not loaded."}]

        logger.info(f"DataFrame shape: {self._dataframe.shape}, Memory usage: {self._dataframe.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

        # ✅ FIX CRÍTICO: Evitar cópia completa para economizar memória
        # filtered_df = self._dataframe.copy()  # REMOVIDO: Causa erro de memória
        filtered_df = self._dataframe  # Trabalhar diretamente no DataFrame
        logger.info(f"Applying filters: {query_filters}")

        # Se não há filtros, retorna uma amostra dos dados para análise
        if not query_filters:
            logger.info("Sem filtros específicos. Retornando amostra de dados.")
            # ✅ OTIMIZAÇÃO: Amostra aleatória maior para evitar dados repetidos
            sample_size = min(20000, len(filtered_df))  # Máximo 20000 linhas
            sample_df = filtered_df.sample(n=sample_size, random_state=42)  # Amostra aleatória
            results = sample_df.to_dict(orient="records")
            logger.info(f"Amostra aleatória retornada com sucesso. {len(results)} linhas de {len(filtered_df)} total.")
            return results

        try:
            logger.info(f"Available columns: {list(filtered_df.columns)}")

            for column, condition in query_filters.items():
                logger.info(f"Processing filter - Column: {column}, Condition: {condition}")

                # ✅ VALIDAÇÃO: Verificar se a coluna existe
                if column not in filtered_df.columns:
                    logger.error(f"Column '{column}' not found in DataFrame. Available columns: {list(filtered_df.columns)}")
                    return [{"error": f"Coluna '{column}' não encontrada. Colunas disponíveis: {list(filtered_df.columns)}"}]
                if isinstance(condition, str) and (condition.startswith(">") or condition.startswith("<") or condition.startswith(">=") or condition.startswith("<=") or condition.startswith("!=")):
                    # Handle comparison operators
                    op = condition[0]
                    if condition.startswith(">="): op = ">="
                    elif condition.startswith("<="): op = "<="
                    elif condition.startswith("!="): op = "!="
                    
                    value = condition[len(op):].strip()
                    
                    # Try to convert value to numeric if column is numeric
                    if pd.api.types.is_numeric_dtype(filtered_df[column]):
                        value = pd.to_numeric(value)

                    if op == ">":
                        filtered_df = filtered_df[filtered_df[column] > value]
                    elif op == "<":
                        filtered_df = filtered_df[filtered_df[column] < value]
                    elif op == ">=":
                        filtered_df = filtered_df[filtered_df[column] >= value]
                    elif op == "<=":
                        filtered_df = filtered_df[filtered_df[column] <= value]
                    elif op == "!=":
                        filtered_df = filtered_df[filtered_df[column] != value]
                    else:
                        # Default to equality if operator not recognized or simple string
                        filtered_df = filtered_df[filtered_df[column] == condition]
                else:
                    # Simple equality - with automatic type conversion
                    # Se a coluna é numérica e a condição é string numérica, converta
                    if pd.api.types.is_numeric_dtype(filtered_df[column]) and isinstance(condition, str) and condition.isdigit():
                        condition = pd.to_numeric(condition)
                    filtered_df = filtered_df[filtered_df[column] == condition]



            results = filtered_df.to_dict(orient="records")
            logger.info(f"Query executed successfully. {len(results)} rows returned from {len(self._dataframe)} total.")
            return results
        except KeyError as e:
            logger.error(f"Column not found in DataFrame: {e}. Available columns: {list(filtered_df.columns)}", exc_info=True)
            return [{"error": f"Coluna não encontrada: {e}. Colunas disponíveis: {list(filtered_df.columns)}."}]
        except MemoryError as e:
            logger.error(f"Memory error during query execution: {e}", exc_info=True)
            return [{"error": "Erro de memória. Tente usar filtros mais específicos para reduzir o volume de dados.", "details": str(e)}]
        except Exception as e:
            logger.error(f"Error executing Parquet query: {e}", exc_info=True)
            return [{"error": "Falha ao executar a consulta no arquivo Parquet.", "details": str(e)}]

    def get_schema(self) -> str:
        """
        Returns the schema of the Parquet file as a string (column names and types).
        """
        self._load_dataframe()
        if self._dataframe is None:
            return ""
        
        schema_str = "Parquet Schema (ADMMATAO.parquet):\n"
        for col_name, dtype in self._dataframe.dtypes.items():
            schema_str += f"  - {col_name}: {dtype}\n"
        logger.info("Parquet schema generated.")
        return schema_str
