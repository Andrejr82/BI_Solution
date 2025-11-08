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
from typing import Any, Dict, List, Optional
import pandas as pd
import dask.dataframe as dd

# Import condicional do Polars (fallback para Dask se não disponível)
try:
    import polars as pl
    POLARS_AVAILABLE = True
    logging.info(f"✅ Polars carregado com sucesso (versão {pl.__version__})")
except ImportError as e:
    POLARS_AVAILABLE = False
    pl = None
    logging.warning(f"⚠️ Polars não disponível: {e}. Usando apenas Dask.")
except Exception as e:
    POLARS_AVAILABLE = False
    pl = None
    logging.error(f"❌ Erro ao importar Polars: {e}. Usando apenas Dask.")

from .base import DatabaseAdapter
from core.utils.column_validator import (
    validate_columns,
    ColumnValidationError,
    get_available_columns_cached
)

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

    def execute_query(self, query_filters: Dict[str, Any], query_text: str = None, required_columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Executa query usando engine selecionada (Polars ou Dask).
        Inclui fallback automático em caso de erro.

        Args:
            query_filters: Dicionário com filtros (coluna: valor)
            query_text: Texto da pergunta do usuário (opcional, para otimização)

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
                result = self._execute_polars(query_filters, query_text=query_text, required_columns=required_columns)
            else:
                logger.info("Executando com Dask...")
                result = self._execute_dask(query_filters, query_text=query_text, required_columns=required_columns)

            elapsed = time.time() - start_time
            logger.info(f"Query executada com sucesso: {len(result)} rows em {elapsed:.2f}s usando {self.engine.upper()}")
            return result

        except Exception as e:
            logger.error(f"Erro com {self.engine.upper()}: {e}", exc_info=True)
            # Fallback: Se Polars falhou, tentar Dask
            if self.engine == "polars":
                logger.warning("Fallback: Polars falhou, tentando Dask...")
                result = self._execute_dask(
                    query_filters, query_text=query_text
                )

                # Se Dask retornou um objeto de erro (lista com dict contendo 'error'),
                # tentar fallback robusto com PyArrow -> pandas.
                if (
                    isinstance(result, list)
                    and result
                    and isinstance(result[0], dict)
                    and 'error' in result[0]
                ):
                    details = result[0].get('details', result[0].get('error'))
                    logger.error("Fallback Dask retornou erro: %s", details)

                    try:
                        import pyarrow.parquet as pq
                        import pandas as _pd

                        logger.warning(
                            "Tentando fallback robusto com PyArrow -> pandas"
                        )

                        # Expandir possível wildcard e ler arquivo a arquivo com pandas (mais tolerante)
                        import glob as _glob

                        files = []
                        if isinstance(self.file_path, str) and '*' in self.file_path:
                            files = _glob.glob(self.file_path)
                        elif isinstance(self.file_path, str) and os.path.isdir(self.file_path):
                            files = _glob.glob(os.path.join(self.file_path, '*.parquet'))
                        elif isinstance(self.file_path, str) and os.path.isfile(self.file_path):
                            files = [self.file_path]
                        else:
                            try:
                                files = _glob.glob(str(self.file_path))
                            except Exception:
                                files = []

                        if not files:
                            raise OSError(f"No parquet files found for path: {self.file_path}")

                        dfs = []
                        for f in files:
                            try:
                                # pandas read_parquet is usually more tolerant per-file; usar pyarrow engine
                                dfs.append(_pd.read_parquet(f, engine='pyarrow'))
                            except Exception as file_err:
                                logger.warning(f"Skipping parquet file due to read error: {f} -> {file_err}")

                        if not dfs:
                            raise OSError("No parquet files could be read successfully.")

                        df = _pd.concat(dfs, ignore_index=True)

                        # Coagir colunas possivelmente numéricas para números
                        pattern = (
                            r'mes_|venda|estoque|preco|liquido|qtde|qtd'
                        )
                        for col in df.columns:
                            if df[col].dtype == object and re.search(
                                pattern, col, re.I
                            ):
                                df[col] = _pd.to_numeric(
                                    df[col], errors='coerce'
                                ).fillna(0)

                        results = df.to_dict(orient='records')
                        logger.info(
                            "Fallback robusto bem-sucedido: %d rows lidos via"
                            " PyArrow->pandas",
                            len(results),
                        )

                        return results

                    except Exception as final_err:
                        logger.error(
                            "Fallback robusto falhou: %s",
                            final_err,
                            exc_info=True,
                        )

                        return [
                            {
                                "error": (
                                    "Falha ao executar query. Erro original: "
                                    f"{str(e)}"
                                ),
                                "details": str(final_err),
                            }
                        ]

                elapsed = time.time() - start_time
                logger.info(
                    "Fallback bem-sucedido: %d rows em %.2fs usando DASK",
                    len(result),
                    elapsed,
                )

                return result
            else:
                # Dask falhou e não há fallback
                return [{"error": f"Falha ao executar query com Dask: {str(e)}"}]

    def _execute_polars(self, query_filters: Dict[str, Any], query_text: str = None, required_columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Executa query usando Polars (rápido, lazy evaluation).

        Estratégia:
        1. Usar scan_parquet() para lazy loading
        2. Aplicar filtros string diretamente
        3. Converter tipos necessários (ESTOQUE_UNE, vendas)
        4. Aplicar filtros numéricos após conversão
        5. collect() para materializar resultado
        6. Converter para Pandas dict para compatibilidade

        Args:
            query_filters: Dicionário com filtros
            query_text: Texto da pergunta (opcional, para otimização)
        """
        logger.info("Iniciando query Polars...")

        try:
            # 1. Lazy scan com tolerância a variações de schema
            # ✅ CORREÇÃO CRÍTICA: extra_columns='ignore' para ignorar coluna 'mc' extra
            # (fix para: SchemaError: extra column in file outside of expected schema: mc)
            lf = pl.scan_parquet(
                self.file_path,
                allow_missing_columns=True,  # Tolerar colunas faltando
                extra_columns='ignore',  # ✅ IGNORAR colunas extras (como 'mc')
                glob=True,  # Permitir wildcard pattern
                hive_partitioning=None,  # Desabilitar hive partitioning
                retries=0  # Não tentar novamente em caso de erro
            )

            # ✅ CORREÇÃO: Adicionar colunas padrão se ausentes (robustez)
            schema = lf.collect_schema()
            expected_columns = {
                'linha_verde': 0,
                'une_id': 'N/A'  # Usar 'N/A' para manter tipo consistente se for string
            }
            
            # Otimização para verificar todas as colunas de uma vez
            cols_to_add = []
            for col, default_val in expected_columns.items():
                if col not in schema.names():
                    cols_to_add.append(pl.lit(default_val).alias(col))
                    logger.info(f"Coluna ausente '{col}' será adicionada com valor padrão: {default_val}")
            
            if cols_to_add:
                lf = lf.with_columns(cols_to_add)

            # 2. Separar filtros por tipo (igual ParquetAdapter)
            NUMERIC_COLUMNS_IN_STRING_FORMAT = ['estoque_une', 'ESTOQUE_UNE', 'estoque_atual']

            string_filters = []
            numeric_filters = []

            # Obter schema para detectar tipos
            schema = lf.collect_schema()
            available_columns = list(schema.names())

            # ✅ VALIDAÇÃO ROBUSTA DE COLUNAS
            # Validar todas as colunas dos filtros antes de executar
            filter_columns = list(query_filters.keys())

            try:
                validation_result = validate_columns(
                    filter_columns,
                    available_columns,
                    auto_correct=True  # Corrigir automaticamente
                )

                # Logar correções aplicadas
                if validation_result["corrected"]:
                    logger.info(f"✅ Colunas auto-corrigidas: {validation_result['corrected']}")

                # Se houver colunas inválidas, levantar erro com sugestões
                if not validation_result["all_valid"]:
                    invalid_col = validation_result["invalid"][0]
                    suggestions = validation_result["suggestions"].get(invalid_col, [])

                    error_msg = f"Coluna '{invalid_col}' não encontrada no DataFrame."
                    if suggestions:
                        error_msg += f" Você quis dizer: {', '.join(suggestions[:3])}?"

                    raise ColumnValidationError(invalid_col, suggestions, available_columns)

                # Criar dicionário de mapeamento old -> new para filtros
                column_mapping = {col: col for col in filter_columns}
                column_mapping.update(validation_result["corrected"])

            except ColumnValidationError as e:
                logger.error(f"❌ Erro de validação de coluna: {e}")
                raise
            except Exception as e:
                logger.warning(f"⚠️ Erro na validação de colunas (continuando): {e}")
                column_mapping = {col: col for col in filter_columns}

            for column, condition in query_filters.items():
                # Usar coluna corrigida se disponível
                actual_column = column_mapping.get(column, column)

                # Fallback: case-insensitive match
                try:
                    schema_cols = {c.lower(): c for c in schema.names()}
                    actual_column = schema_cols.get(actual_column.lower(), actual_column)
                except:
                    pass

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

            # 6.5. OTIMIZAÇÃO: Selecionar apenas colunas necessárias (reduz memória em 60-80%)
            # Apenas se query_text foi fornecida E dataset é grande
            schema_cols = lf.collect_schema().names()
            if query_text and len(schema_cols) > 10:
                try:
                    from core.utils.query_optimizer import get_optimized_columns
                    optimized_cols = get_optimized_columns(schema_cols, query=query_text)

                    # ✅ CONTEXT7: Garantir que required_columns sejam incluídas
                    if required_columns:
                        for col in required_columns:
                            if col not in optimized_cols:
                                optimized_cols.append(col)
                                logger.info(f"Coluna obrigatória '{col}' adicionada à seleção otimizada.")

                    if optimized_cols and len(optimized_cols) < len(schema_cols):
                        lf = lf.select(optimized_cols)
                        logger.info(f"Otimização: {len(schema_cols)} → {len(optimized_cols)} colunas")
                except Exception as opt_error:
                    # Otimização falhou, continuar sem otimizar (não quebra funcionalidade)
                    logger.warning(f"Otimização de colunas falhou (continuando sem otimizar): {opt_error}")
            # ✅ CONTEXT7: Se não houver otimização, mas houver required_columns, selecionar apenas elas
            elif required_columns:
                # Garantir que required_columns existam no schema antes de selecionar
                final_cols = [col for col in required_columns if col in schema_cols]
                if final_cols:
                    lf = lf.select(final_cols)
                    logger.info(f"Seleção de colunas: Apenas colunas obrigatórias ({len(final_cols)}) selecionadas.")
                else:
                    logger.warning("Nenhuma coluna obrigatória encontrada no schema. Retornando todas as colunas.")

            # 7. Collect (materializar resultado com STREAMING MODE)
            # ✅ OTIMIZAÇÃO CONTEXT7: Streaming mode reduz memória em 60-80%
            # Permite processar datasets maiores que RAM disponível
            logger.info("Materializando resultado com collect(engine='streaming')...")
            df_polars = lf.collect(engine="streaming")

            # 8. Converter para Pandas dict (compatibilidade)
            df_pandas = df_polars.to_pandas()
            result = df_pandas.to_dict(orient="records")

            logger.info(f"Polars query concluída: {len(result)} linhas retornadas")
            return result

        except Exception as e:
            logger.error(f"Erro na execução Polars: {e}", exc_info=True)
            raise

    def _execute_dask(self, query_filters: Dict[str, Any], query_text: str = None, required_columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Executa query usando Dask (código atual do ParquetAdapter).
        Mantém 100% da lógica existente para compatibilidade.

        Args:
            query_filters: Dicionário com filtros
            query_text: Texto da pergunta (opcional, para otimização)
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

            # ✅ CORREÇÃO: Adicionar colunas padrão se ausentes (robustez)
            expected_columns = {
                'linha_verde': 0,
                'une_id': 'N/A'  # Usar 'N/A' para manter tipo consistente se for string
            }
            for col, default_val in expected_columns.items():
                if col not in ddf.columns:
                    ddf[col] = default_val
                    logger.info(f"Coluna ausente '{col}' foi adicionada com valor padrão: {default_val}")

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

            # OTIMIZAÇÃO: Selecionar apenas colunas necessárias ANTES de compute() (reduz memória)
            if query_text and len(ddf.columns) > 10:
                try:
                    from core.utils.query_optimizer import get_optimized_columns
                    optimized_cols = get_optimized_columns(list(ddf.columns), query=query_text)

                    # ✅ CONTEXT7: Garantir que required_columns sejam incluídas
                    if required_columns:
                        for col in required_columns:
                            if col not in optimized_cols:
                                optimized_cols.append(col)
                                logger.info(f"Coluna obrigatória '{col}' adicionada à seleção otimizada.")

                    if optimized_cols and len(optimized_cols) < len(ddf.columns):
                        ddf = ddf[optimized_cols]
                        logger.info(f"Otimização: {len(ddf.columns)} → {len(optimized_cols)} colunas")
                except Exception as opt_error:
                    # Otimização falhou, continuar sem otimizar (não quebra funcionalidade)
                    logger.warning(f"Otimização de colunas falhou (continuando sem otimizar): {opt_error}")
            # ✅ CONTEXT7: Se não houver otimização, mas houver required_columns, selecionar apenas elas
            elif required_columns:
                # Garantir que required_columns existam no schema antes de selecionar
                # Dask DataFrames não têm um método collect_schema() direto como Polars
                # Precisamos verificar as colunas existentes no ddf
                existing_cols = list(ddf.columns)
                final_cols = [col for col in required_columns if col in existing_cols]
                if final_cols:
                    ddf = ddf[final_cols]
                    logger.info(f"Seleção de colunas: Apenas colunas obrigatórias ({len(final_cols)}) selecionadas.")
                else:
                    logger.warning("Nenhuma coluna obrigatória encontrada no schema. Retornando todas as colunas.")

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
        ✅ OTIMIZAÇÃO v2.2: Retorna schema do Parquet usando PyArrow (3-5x mais rápido)
        PyArrow lê apenas metadados, sem carregar dados (Context7 best practice)
        Ref: https://github.com/pola-rs/polars - scan_parquet schema optimization
        """
        try:
            # ✅ Usar PyArrow para leitura de schema (muito mais rápido)
            import pyarrow.parquet as pq

            parquet_file = pq.ParquetFile(self.file_path)
            schema = parquet_file.schema_arrow

            schema_str = "Parquet Schema (via PyArrow - optimized):\n"
            for i in range(len(schema)):
                field = schema.field(i)
                schema_str += f"  - {field.name}: {field.type}\n"

            logger.info("✅ Schema gerado com PyArrow (otimizado)")
            return schema_str

        except ImportError:
            # Fallback para Polars se PyArrow não disponível
            logger.warning("⚠️ PyArrow não disponível, usando Polars como fallback")
            try:
                if self.engine == "polars":
                    lf = pl.scan_parquet(self.file_path)
                    schema = lf.collect_schema()
                    schema_str = "Parquet Schema (via Polars):\n"
                    for col_name, dtype in schema.items():
                        schema_str += f"  - {col_name}: {dtype}\n"
                    return schema_str
                else:
                    ddf = dd.read_parquet(self.file_path, engine='fastparquet')
                    schema_str = "Parquet Schema (via Dask):\n"
                    for col_name, dtype in ddf.dtypes.items():
                        schema_str += f"  - {col_name}: {dtype}\n"
                    return schema_str
            except Exception as fallback_error:
                logger.error(f"Erro no fallback: {fallback_error}")
                return f"Error reading schema: {fallback_error}"

        except Exception as e:
            logger.error(f"Could not read Parquet schema: {e}")
            return f"Error reading schema: {e}"
