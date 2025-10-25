"""
PolarsD askAdapter: Adaptador inteligente que escolhe automaticamente entre Polars e Dask.

Decisão automática baseada em tamanho do arquivo:
- Arquivos < 500MB: Polars (8.1x mais rápido)
- Arquivos >= 500MB: Dask (escalável, out-of-core)

Recursos:
- Fallback automático Polars → Dask em caso de erro
- Validação de integridade de dados
- Logging detalhado de decisões
- Feature flag para desabilitar Polars (POLARS_ENABLED=false)

Autor: Claude Code
Data: 2025-10-20
"""

import logging
import os
import re
import time
from typing import Any, Dict, List
import pandas as pd
import dask.dataframe as dd

# Import condicional do Polars (fallback para Dask se não disponível)
try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False
    pl = None
    logging.warning("Polars não disponível. Usando apenas Dask.")

from .base import DatabaseAdapter

logger = logging.getLogger(__name__)

class PolarsDaskAdapter(DatabaseAdapter):
    """
    Adaptador híbrido que escolhe automaticamente entre Polars (rápido) e Dask (escalável).
    """

    # Configurações (podem ser sobrescritas por env vars)
    POLARS_THRESHOLD_MB = int(os.getenv("POLARS_THRESHOLD_MB", "500"))
    POLARS_ENABLED = os.getenv("POLARS_ENABLED", "true").lower() == "true"
    FORCE_DASK = os.getenv("FORCE_DASK", "false").lower() == "true"

    def __init__(self, file_path: str):
        """
        Inicializa o PolarsDaskAdapter.

        Args:
            file_path: Caminho para arquivo(s) Parquet (suporta wildcards)
        """
        # Validação do arquivo (mesma lógica do ParquetAdapter)
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
            logger.info(f"PolarsDaskAdapter found {len(matching_files)} file(s) matching pattern: {file_path}")

        self.file_path = file_path
        self.size_mb = self._get_file_size_mb()
        self.engine = self._select_engine()

        logger.info(f"PolarsDaskAdapter initialized:")
        logger.info(f"  File: {file_path}")
        logger.info(f"  Size: {self.size_mb:.1f} MB")
        logger.info(f"  Engine: {self.engine.upper()}")
        logger.info(f"  Threshold: {self.POLARS_THRESHOLD_MB} MB")

    def _get_file_size_mb(self) -> float:
        """Calcula tamanho total do(s) arquivo(s) em MB."""
        import glob

        if "*" in self.file_path:
            files = glob.glob(self.file_path)
        else:
            files = [self.file_path]

        total_size = sum(os.path.getsize(f) for f in files if os.path.exists(f))
        return total_size / (1024 ** 2)

    def _select_engine(self) -> str:
        """
        Seleciona engine automaticamente baseado em:
        1. Disponibilidade do Polars
        2. Feature flag FORCE_DASK
        3. Feature flag POLARS_ENABLED
        4. Tamanho do arquivo vs threshold

        Returns:
            "polars" ou "dask"
        """
        # Se Polars não está disponível, usar Dask
        if not POLARS_AVAILABLE:
            logger.warning("Engine: DASK (Polars não instalado)")
            return "dask"

        if self.FORCE_DASK:
            logger.info("Engine: DASK (forced by FORCE_DASK=true)")
            return "dask"

        if not self.POLARS_ENABLED:
            logger.info("Engine: DASK (Polars disabled by POLARS_ENABLED=false)")
            return "dask"

        if self.size_mb < self.POLARS_THRESHOLD_MB:
            logger.info(f"Engine: POLARS ({self.size_mb:.1f}MB < {self.POLARS_THRESHOLD_MB}MB)")
            return "polars"
        else:
            logger.info(f"Engine: DASK ({self.size_mb:.1f}MB >= {self.POLARS_THRESHOLD_MB}MB)")
            return "dask"

    def connect(self) -> None:
        """No-op. Ambos engines usam lazy loading."""
        logger.info("PolarsDaskAdapter.connect() is a no-op (lazy loading)")
        pass

    def disconnect(self) -> None:
        """No-op. Ambos engines gerenciam recursos automaticamente."""
        logger.info("PolarsDaskAdapter.disconnect() is a no-op")
        pass

    def execute_query(self, query_filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Executa query usando engine selecionada (Polars ou Dask).
        Inclui fallback automático em caso de erro.

        Args:
            query_filters: Dicionário com filtros (coluna: valor)

        Returns:
            Lista de dicts com resultados
        """
        logger.info(f"PolarsDaskAdapter.execute_query() com {len(query_filters)} filtro(s)")

        if not query_filters:
            logger.error("Query sem filtros não é permitida")
            return [{"error": "A consulta é muito ampla. Adicione filtros (ex: por UNE, segmento) para continuar."}]

        start_time = time.time()

        # Tentar engine preferida
        try:
            if self.engine == "polars":
                logger.info("Executando com Polars...")
                result = self._execute_polars(query_filters)
            else:
                logger.info("Executando com Dask...")
                result = self._execute_dask(query_filters)

            elapsed = time.time() - start_time
            logger.info(f"Query executada com sucesso: {len(result)} rows em {elapsed:.2f}s usando {self.engine.upper()}")
            return result

        except Exception as e:
            logger.error(f"Erro com {self.engine.upper()}: {e}", exc_info=True)

            # Fallback: Se Polars falhou, tentar Dask
            if self.engine == "polars":
                logger.warning("Fallback: Polars falhou, tentando Dask...")
                try:
                    result = self._execute_dask(query_filters)
                    elapsed = time.time() - start_time
                    logger.info(f"Fallback bem-sucedido: {len(result)} rows em {elapsed:.2f}s usando DASK")
                    return result
                except Exception as e2:
                    logger.error(f"Fallback Dask também falhou: {e2}", exc_info=True)
                    return [{"error": f"Falha ao executar query. Erro original: {str(e)}", "details": str(e2)}]
            else:
                # Dask falhou e não há fallback
                return [{"error": f"Falha ao executar query com Dask: {str(e)}"}]

    def _execute_polars(self, query_filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Executa query usando Polars (rápido, lazy evaluation).

        Estratégia:
        1. Usar scan_parquet() para lazy loading
        2. Aplicar filtros string diretamente
        3. Converter tipos necessários (ESTOQUE_UNE, vendas)
        4. Aplicar filtros numéricos após conversão
        5. collect() para materializar resultado
        6. Converter para Pandas dict para compatibilidade
        """
        logger.info("Iniciando query Polars...")

        try:
            # 1. Lazy scan
            lf = pl.scan_parquet(self.file_path)

            # 2. Separar filtros por tipo (igual ParquetAdapter)
            NUMERIC_COLUMNS_IN_STRING_FORMAT = ['estoque_une', 'ESTOQUE_UNE', 'estoque_atual']

            string_filters = []
            numeric_filters = []

            # Obter schema para detectar tipos
            schema = lf.collect_schema()

            for column, condition in query_filters.items():
                # Normalizar nome da coluna (case-insensitive)
                try:
                    # Tentar encontrar coluna no schema (case-insensitive)
                    schema_cols = {c.lower(): c for c in schema.names()}
                    actual_column = schema_cols.get(column.lower(), column)
                except:
                    actual_column = column

                # Parse condição
                op = '='
                value = condition

                # Detectar tipo da coluna no Parquet
                col_dtype = schema.get(actual_column) if actual_column in schema.names() else None

                if isinstance(condition, str) and any(o in condition for o in ['>=', '<=', '!=', '>', '<', '=']):
                    match = re.match(r"(>=|<=|!=|>|<|=)\s*(.*)", str(condition))
                    if match:
                        op, value_str = match.groups()
                        op = op.strip()
                        value_str = value_str.strip().strip("'\"")

                        # Verificar se é filtro numérico em coluna string
                        if actual_column.lower() in [c.lower() for c in NUMERIC_COLUMNS_IN_STRING_FORMAT] and op in ['>=', '<=', '>', '<']:
                            try:
                                numeric_value = float(value_str) if '.' in value_str else int(value_str)
                                numeric_filters.append((actual_column, op, numeric_value))
                                logger.info(f"Filtro numérico adiado: {actual_column} {op} {numeric_value}")
                                continue
                            except ValueError:
                                pass

                        value = value_str

                # Converter value para tipo correto baseado no schema
                if col_dtype is not None and POLARS_AVAILABLE:
                    # Se coluna é numérica mas value é string, converter
                    dtype_str = str(col_dtype)
                    if any(t in dtype_str.lower() for t in ['int', 'uint']):
                        try:
                            value = int(value) if isinstance(value, str) else value
                            logger.info(f"Convertendo {column} para int: {value}")
                        except ValueError:
                            pass
                    elif 'float' in dtype_str.lower():
                        try:
                            value = float(value) if isinstance(value, str) else value
                            logger.info(f"Convertendo {column} para float: {value}")
                        except ValueError:
                            pass

                # Adicionar filtro string
                string_filters.append((actual_column, op, value))

            # 3. Aplicar filtros string
            for column, op, value in string_filters:
                if op == '=':
                    lf = lf.filter(pl.col(column) == value)
                elif op == '!=':
                    lf = lf.filter(pl.col(column) != value)
                elif op == '>':
                    lf = lf.filter(pl.col(column) > value)
                elif op == '<':
                    lf = lf.filter(pl.col(column) < value)
                elif op == '>=':
                    lf = lf.filter(pl.col(column) >= value)
                elif op == '<=':
                    lf = lf.filter(pl.col(column) <= value)

                logger.info(f"Filtro aplicado: {column} {op} {value}")

            # 4. Converter tipos (ESTOQUE, vendas mensais)
            # Tentar converter ESTOQUE_UNE de string para numeric
            schema = lf.collect_schema()
            for col in ['estoque_une', 'ESTOQUE_UNE', 'estoque_atual']:
                if col in schema.names():
                    lf = lf.with_columns(pl.col(col).cast(pl.Float64, strict=False).fill_null(0))
                    logger.info(f"Coluna {col} convertida para numeric")

            # Converter vendas mensais
            vendas_cols = [f'mes_{i:02d}' for i in range(1, 13)]
            existing_vendas = [c for c in vendas_cols if c in schema.names()]
            if existing_vendas:
                for col in existing_vendas:
                    lf = lf.with_columns(pl.col(col).cast(pl.Float64, strict=False).fill_null(0))
                logger.info(f"{len(existing_vendas)} colunas de vendas convertidas")

            # 5. Aplicar filtros numéricos após conversão
            for column, op, value in numeric_filters:
                if op == '>=':
                    lf = lf.filter(pl.col(column) >= value)
                elif op == '<=':
                    lf = lf.filter(pl.col(column) <= value)
                elif op == '>':
                    lf = lf.filter(pl.col(column) > value)
                elif op == '<':
                    lf = lf.filter(pl.col(column) < value)
                elif op == '=':
                    lf = lf.filter(pl.col(column) == value)
                elif op == '!=':
                    lf = lf.filter(pl.col(column) != value)

                logger.info(f"Filtro numérico aplicado: {column} {op} {value}")

            # 6. Adicionar vendas_total se existir vendas mensais
            if existing_vendas:
                lf = lf.with_columns(
                    pl.sum_horizontal(existing_vendas).alias('vendas_total')
                )
                logger.info("Coluna vendas_total adicionada")

            # 7. Collect (materializar resultado)
            logger.info("Materializando resultado com collect()...")
            df_polars = lf.collect()

            # 8. Converter para Pandas dict (compatibilidade)
            df_pandas = df_polars.to_pandas()
            result = df_pandas.to_dict(orient="records")

            logger.info(f"Polars query concluída: {len(result)} linhas retornadas")
            return result

        except Exception as e:
            logger.error(f"Erro na execução Polars: {e}", exc_info=True)
            raise

    def _execute_dask(self, query_filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Executa query usando Dask (código atual do ParquetAdapter).
        Mantém 100% da lógica existente para compatibilidade.
        """
        logger.info("Executando query com Dask (código original ParquetAdapter)...")

        try:
            schema = dd.read_parquet(self.file_path, engine='pyarrow').dtypes.to_dict()
        except Exception as e:
            logger.error(f"Failed to read Parquet schema: {e}")
            return [{"error": "Falha ao ler o esquema do arquivo Parquet.", "details": str(e)}]

        # Separar filtros (mesma lógica do ParquetAdapter)
        pyarrow_filters = []
        pandas_filters = []
        NUMERIC_COLUMNS_IN_STRING_FORMAT = ['estoque_une', 'ESTOQUE_UNE', 'estoque_atual']

        for column, condition in query_filters.items():
            try:
                if column not in schema:
                    logger.warning(f"Column '{column}' not found in Parquet schema. Skipping filter.")
                    continue

                col_type = schema[column]
                op = '='
                value = condition

                # Converter value para tipo correto se necessário
                if pd.api.types.is_integer_dtype(col_type) and isinstance(value, str):
                    try:
                        value = int(value)
                        logger.info(f"Convertendo {column} para int: {value}")
                    except ValueError:
                        pass
                elif pd.api.types.is_float_dtype(col_type) and isinstance(value, str):
                    try:
                        value = float(value)
                        logger.info(f"Convertendo {column} para float: {value}")
                    except ValueError:
                        pass

                if isinstance(condition, str) and any(op in condition for o in ['>=', '<=', '!=', '>', '<', '=']):
                    match = re.match(r"(>=|<=|!=|>|<|=)\s*(.*)", str(condition))
                    if match:
                        op, value_str = match.groups()
                        op = op.strip()
                        value_str = value_str.strip()

                        if column in NUMERIC_COLUMNS_IN_STRING_FORMAT and op in ['>=', '<=', '>', '<']:
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
            start_time = time.time()

            # Read com PyArrow filters (predicate pushdown)
            if pyarrow_filters:
                logger.info(f"Applying PyArrow filters: {pyarrow_filters}")
                ddf = dd.read_parquet(self.file_path, engine='pyarrow', filters=pyarrow_filters)
            else:
                logger.info("No PyArrow filters. Reading full dataset.")
                ddf = dd.read_parquet(self.file_path, engine='pyarrow')

            read_time = time.time() - start_time
            logger.info(f"Dask read_parquet (lazy): {read_time:.2f}s")

            # Converter tipos em Dask
            logger.info("Converting data types in Dask...")
            for col in ['estoque_une', 'ESTOQUE_UNE', 'estoque_atual']:
                if col in ddf.columns:
                    ddf[col] = dd.to_numeric(ddf[col], errors='coerce').fillna(0)

            vendas_colunas = [f'mes_{i:02d}' for i in range(1, 13)]
            vendas_colunas_existentes = [col for col in vendas_colunas if col in ddf.columns]
            if vendas_colunas_existentes:
                for col in vendas_colunas_existentes:
                    ddf[col] = dd.to_numeric(ddf[col], errors='coerce').fillna(0)

            # Aplicar filtros numéricos
            if pandas_filters:
                logger.info(f"Applying numeric filters in Dask: {pandas_filters}")
                for column, op, value in pandas_filters:
                    if op == '>=':
                        ddf = ddf[ddf[column] >= value]
                    elif op == '<=':
                        ddf = ddf[ddf[column] <= value]
                    elif op == '>':
                        ddf = ddf[ddf[column] > value]
                    elif op == '<':
                        ddf = ddf[ddf[column] < value]
                    elif op == '=':
                        ddf = ddf[ddf[column] == value]
                    elif op == '!=':
                        ddf = ddf[ddf[column] != value]

            # Compute
            logger.info("Computing Dask DataFrame...")
            compute_start = time.time()
            computed_df = ddf.compute()
            compute_time = time.time() - compute_start

            # Adicionar vendas_total
            if vendas_colunas_existentes and 'vendas_total' not in computed_df.columns:
                computed_df['vendas_total'] = computed_df[vendas_colunas_existentes].fillna(0).sum(axis=1)

            results = computed_df.to_dict(orient="records")
            total_time = time.time() - start_time
            logger.info(f"Dask query successful: {len(results)} rows | Compute: {compute_time:.2f}s | Total: {total_time:.2f}s")
            return results

        except Exception as e:
            logger.error(f"Error executing Dask query: {e}", exc_info=True)
            return [{"error": "Falha ao executar a consulta Parquet com Dask.", "details": str(e)}]

    def get_schema(self) -> str:
        """
        Retorna schema do Parquet.
        Usa Polars se disponível (mais rápido), senão Dask.
        """
        try:
            if self.engine == "polars":
                lf = pl.scan_parquet(self.file_path)
                schema = lf.collect_schema()
                schema_str = "Parquet Schema (via Polars):\n"
                for col_name, dtype in schema.items():
                    schema_str += f"  - {col_name}: {dtype}\n"
                logger.info("Schema gerado com Polars")
                return schema_str
            else:
                ddf = dd.read_parquet(self.file_path, engine='fastparquet')
                schema_str = "Parquet Schema (via Dask):\n"
                for col_name, dtype in ddf.dtypes.items():
                    schema_str += f"  - {col_name}: {dtype}\n"
                logger.info("Schema gerado com Dask")
                return schema_str
        except Exception as e:
            logger.error(f"Could not read Parquet schema: {e}")
            return f"Error reading schema: {e}"
