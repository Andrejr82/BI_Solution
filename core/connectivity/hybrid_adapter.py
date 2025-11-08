"""
HybridDataAdapter: SQL Server (primário) + Parquet (fallback automático)
Adapter inteligente que garante zero downtime.

Uso:
    adapter = HybridDataAdapter()
    result = adapter.execute_query({})  # tenta SQL Server, fallback para Parquet
"""
import glob
import logging
from typing import Dict, Any, List, Optional
import os
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

class HybridDataAdapter:
    """
    Adapter híbrido com fallback automático e inteligente.

    Prioridade:
    1. SQL Server (se USE_SQL_SERVER=true e conexão OK)
    2. Parquet (fallback sempre disponível)
    """

    def __init__(self):
        """Inicializa adapter com configurações do .env"""
        # Flags de controle
        self.use_sql_server = os.getenv("USE_SQL_SERVER", "false").lower() == "true"
        self.sql_timeout = int(os.getenv("SQL_SERVER_TIMEOUT", "10"))
        self.fallback_enabled = os.getenv("FALLBACK_TO_PARQUET", "true").lower() == "true"

        # Status de conexão
        self.sql_available = False
        self.current_source = "parquet"  # default seguro

        # Inicializar adapters
        self._init_adapters()

        logger.info(f"HybridDataAdapter inicializado - Fonte: {self.current_source}")

    def _init_adapters(self):
        """Inicializa adapters com tratamento robusto de erros."""

        # 1. SEMPRE inicializar Parquet (fallback obrigatório)
        try:
            from .parquet_adapter import ParquetAdapter

            # 🚀 USAR PADRÃO *.parquet PARA LER TODOS OS ARQUIVOS (múltiplas partições)
            parquet_dir = Path(os.getcwd()) / "data" / "parquet"
            parquet_pattern = str(parquet_dir / "*.parquet")

            if not parquet_dir.exists():
                # Tentar paths alternativos
                alt_dirs = [
                    Path(__file__).parent.parent.parent / "data" / "parquet",
                    Path("data/parquet"),
                ]

                for alt_dir in alt_dirs:
                    if alt_dir.exists():
                        parquet_dir = alt_dir
                        parquet_pattern = str(alt_dir / "*.parquet")
                        break

            self.parquet_adapter = ParquetAdapter(file_path=parquet_pattern)
            logger.info(f"[OK] Parquet adapter inicializado: {parquet_pattern}")

        except Exception as e:
            logger.critical(f"[ERRO CRITICO] Parquet adapter falhou: {e}")
            raise  # Sem Parquet = sistema não funciona

        # 2. Tentar inicializar SQL Server (opcional)
        self.sql_adapter = None

        if not self.use_sql_server:
            logger.info("SQL Server desabilitado (USE_SQL_SERVER=false)")
            return

        try:
            from .sql_server_adapter import SQLServerAdapter

            # Carregar settings SEMPRE do .env (mais confiável)
            settings = self._create_settings_from_env()
            logger.info(f"Usando connection string do .env")

            self.sql_adapter = SQLServerAdapter(settings)

            # Testar conexão COM TIMEOUT CURTO (não bloquear startup)
            logger.info("Tentando conectar SQL Server (timeout: 2s)...")
            import threading
            import queue

            result_queue = queue.Queue()

            def try_connect():
                try:
                    self.sql_adapter.connect()
                    result_queue.put(("success", None))
                except Exception as e:
                    result_queue.put(("error", str(e)))

            thread = threading.Thread(target=try_connect, daemon=True)
            thread.start()
            thread.join(timeout=2)  # Máximo 2s para conectar

            if thread.is_alive():
                # Timeout - usar Parquet
                logger.warning("SQL Server timeout (>2s) - usando Parquet")
                self.sql_available = False
                self.current_source = "parquet"
            else:
                try:
                    status, error = result_queue.get_nowait()
                    if status == "success":
                        # Conexão OK
                        self.sql_available = True
                        self.current_source = "sqlserver"
                        logger.info("[OK] SQL Server conectado - modo HIBRIDO ativo")
                    else:
                        # Erro na conexão
                        logger.warning(f"SQL Server falhou: {error} - usando Parquet")
                        self.sql_available = False
                        self.current_source = "parquet"
                except queue.Empty:
                    logger.warning("SQL Server sem resposta - usando Parquet")
                    self.sql_available = False
                    self.current_source = "parquet"

        except ImportError as e:
            logger.warning(f"SQL Server adapter nao disponivel: {e}")
            logger.info("-> Usando apenas Parquet")

        except Exception as e:
            logger.warning(f"SQL Server indisponivel: {e}")
            logger.info("-> Usando Parquet como fonte de dados")
            self.sql_available = False
            self.current_source = "parquet"

    def _create_settings_from_env(self):
        """Cria objeto settings a partir do .env se safe_settings falhar."""

        class Settings:
            def __init__(self):
                # Tentar formato DB_* primeiro (usado por check_db.py)
                driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
                host = os.getenv("DB_HOST")
                port = os.getenv("DB_PORT")
                database = os.getenv("DB_NAME")
                user = os.getenv("DB_USER")
                password = os.getenv("DB_PASSWORD")
                trust_cert = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")

                # Fallback para formato MSSQL_* se DB_* não existir
                if not host:
                    server = os.getenv("MSSQL_SERVER", "")
                    database = os.getenv("MSSQL_DATABASE", "")
                    user = os.getenv("MSSQL_USER", "")
                    password = os.getenv("MSSQL_PASSWORD", "")
                else:
                    # Formato DB_*: combinar host,port
                    server = f"{host},{port}" if port else host

                self.PYODBC_CONNECTION_STRING = (
                    f"DRIVER={driver};"
                    f"SERVER={server};"
                    f"DATABASE={database};"
                    f"UID={user};"
                    f"PWD={password};"
                    f"TrustServerCertificate={trust_cert};"
                )

        return Settings()

    def connect(self):
        """Conecta ao adapter ativo."""
        if self.current_source == "sqlserver" and self.sql_adapter:
            try:
                self.sql_adapter.connect()
            except Exception as e:
                logger.error(f"Erro ao conectar SQL Server: {e}")
                self._switch_to_fallback()
        else:
            self.parquet_adapter.connect()

    def disconnect(self):
        """Desconecta adapter ativo."""
        if self.current_source == "sqlserver" and self.sql_adapter:
            try:
                self.sql_adapter.disconnect()
            except:
                pass

        try:
            self.parquet_adapter.disconnect()
        except:
            pass

    def execute_query(self, query_filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Executa query com fallback automático.

        Args:
            query_filters: Filtros dict (ex: {"une": 261, "nomesegmento": "TECIDOS"})

        Returns:
            Lista de dicts com resultados
        """

        # Tentar SQL Server primeiro (se disponível)
        if self.current_source == "sqlserver" and self.sql_adapter:
            try:
                # Converter filtros dict para SQL WHERE
                sql_query = self._build_sql_query(query_filters)
                result = self.sql_adapter.execute_query(sql_query)

                logger.info(f"[OK] Query via SQL Server ({len(result)} rows)")
                # Normalizar chaves do resultado também para SQL Server
                try:
                    mapped_sql = self._normalize_result_rows(result)
                    return mapped_sql
                except Exception:
                    return result

            except Exception as e:
                logger.error(f"[ERRO] SQL Server: {e}")

                if self.fallback_enabled:
                    logger.warning("-> Ativando fallback para Parquet")
                    self._switch_to_fallback()
                else:
                    raise

        # Usar Parquet (fallback ou primário)
        result = self.parquet_adapter.execute_query(query_filters)
        logger.info(f"[OK] Query via Parquet ({len(result)} rows)")

        # Se o Parquet devolveu um erro (ex: problemas de parsing em colunas
        # numéricas como preco_38_percent), tentar uma segunda tentativa mais
        # tolerante pedindo apenas colunas essenciais (omitindo colunas
        # problemáticas). Isso evita propagar um dict de erro para callers
        # que esperam uma lista de registros.
        if isinstance(result, list) and len(result) == 1 and isinstance(result[0], dict) and result[0].get("error"):
            details = result[0].get("details", "") or ""
            logger.warning(f"Parquet returned error: {result[0].get('error')} - details: {details}")
            try:
                # Escolher um conjunto seguro de colunas essenciais (sem preco)
                # Safe set: evitar colunas numéricas problemáticas (preco, estoque)
                # Incluir 'une' para permitir filtro por UNE e reduzir volume lido
                safe_required = [
                    'codigo',
                    'nome_produto',
                    'nomesegmento',
                    'une',
                ]

                # Chamar o híbrido diretamente passando required_columns
                logger.info("Tentando leitura tolerante com apenas colunas essenciais (fallback)")
                retry = []
                try:
                    retry = self.parquet_adapter._hybrid.execute_query(
                        query_filters, required_columns=safe_required
                    )
                except Exception:
                    # se o _hybrid interno não funcionar, vamos tentar leitura segura via pyarrow+pandas
                    retry = []

                # Se obteve resultado válido, normalizar e retornar
                if isinstance(retry, list) and retry and not (len(retry) == 1 and isinstance(retry[0], dict) and retry[0].get('error')):
                    logger.info("Fallback tolerante bem-sucedido - retornando resultado reduzido")
                    return self._normalize_result_rows(retry)

                # Se retry falhou ou retornou erro, tentar leitura segura direta de arquivos parquet
                logger.info("Retry via _hybrid falhou ou retornou erro; tentando leitura segura direta de arquivos parquet")
                safe_rows = self._read_parquet_safe(required_columns=safe_required, query_filters=query_filters)
                if safe_rows:
                    # Garantir colunas numéricas esperadas para evitar KeyError em callers
                    for r in safe_rows:
                        if 'estoque_atual' not in r:
                            r['estoque_atual'] = 0
                        if 'venda_30_d' not in r:
                            r['venda_30_d'] = 0
                        if 'preco_38_percent' not in r:
                            r['preco_38_percent'] = 0
                    logger.info("Leitura segura de parquet obteve registros - retornando resultado reduzido")
                    return self._normalize_result_rows(safe_rows)
                else:
                    logger.warning("Leitura segura de parquet não retornou registros utilizáveis; retornando lista vazia")
                    return []
            except Exception as e:
                logger.warning(f"Fallback tolerante também falhou: {e}")

        # Normalizar resultado do Parquet
        try:
            return self._normalize_result_rows(result)
        except Exception:
            return result

    def _normalize_result_rows(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normaliza chaves de cada linha retornada (SQL ou Parquet) para nomes canônicos.

        Converte nomes MAIÚSCULOS/legados para nomes em minúsculas usados no código.
        """
        mapped = []
        col_map = {
            'PRODUTO': 'codigo',
            'NOME': 'nome_produto',
            'UNE_NOME': 'une_nome',
            'NOMESEGMENTO': 'nomesegmento',
            'VENDA_30DD': 'venda_30_d',
            'ESTOQUE_UNE': 'estoque_atual',
            'ESTOQUE_ATUAL': 'estoque_atual',
            'ESTOQUE_LV': 'estoque_lv',
        }

        for row in rows:
            if not isinstance(row, dict):
                mapped.append(row)
                continue

            new_row = {}
            for k, v in row.items():
                if isinstance(k, str) and k in col_map:
                    new_key = col_map[k]
                else:
                    new_key = k.lower() if isinstance(k, str) else k
                new_row[new_key] = v

            mapped.append(new_row)

        return mapped

    def _read_parquet_safe(self, required_columns: Optional[List[str]] = None, query_filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Tentativa robusta de leitura de arquivos Parquet usando pyarrow + pandas.

        - Expande globs para lista de arquivos (evita passar wildcard diretamente ao pyarrow)
        - Lê apenas as colunas necessárias (se informado)
        - Faz coercao de colunas de texto para numérico quando detectado
        - Retorna lista de dicts (ou [] em caso de falha)
        """
        try:
            fp = getattr(self.parquet_adapter, 'file_path', None)
            if not fp:
                logger.debug("_read_parquet_safe: parquet file_path indisponivel")
                return []

            # Expandir wildcard se houver
            files = []
            try:
                if isinstance(fp, str) and ('*' in fp):
                    files = glob.glob(fp)
                elif isinstance(fp, str) and os.path.isdir(fp):
                    files = glob.glob(os.path.join(fp, '*.parquet'))
                elif isinstance(fp, str) and os.path.isfile(fp):
                    files = [fp]
                else:
                    # tentar diretório pai
                    parent = os.path.dirname(fp)
                    files = glob.glob(os.path.join(parent, '*.parquet'))
            except Exception:
                files = glob.glob(str(fp)) if isinstance(fp, str) else []

            if not files:
                logger.warning("_read_parquet_safe: nenhum arquivo parquet encontrado para leitura segura")
                return []

            # Ler via pyarrow (mais tolerante ao passar lista de arquivos)
            try:
                import pyarrow.parquet as pq

                table = pq.read_table(files, columns=required_columns if required_columns else None)
                df = table.to_pandas()
            except Exception as e:
                logger.exception(f"_read_parquet_safe: falha ao ler arquivos com pyarrow: {e}")
                return []

            if df is None or df.empty:
                return []

            # Coercao heuristica: tentar converter colunas object -> numerico quando fizer sentido
            for col in list(df.columns):
                if df[col].dtype == object:
                    coerced = pd.to_numeric(df[col], errors='coerce')
                    # Se houver ao menos um valor convertido, aceitar coercao
                    if coerced.notna().sum() > 0:
                        df[col] = coerced

            # Substituir NaN por None para serializacao
            df = df.where(pd.notnull(df), None)

            return df.to_dict(orient='records')

        except Exception as e:
            logger.exception(f"_read_parquet_safe: erro inesperado: {e}")
            return []

    def _build_sql_query(self, filters: Dict[str, Any]) -> str:
        """
        Converte filtros dict para SQL query.

        Args:
            filters: {coluna: valor, ...}

        Returns:
            SQL query string
        """

        # Mapeamento de colunas Parquet → SQL Server (minúsculo → MAIÚSCULO)
        column_mapping = {
            'une': 'UNE',
            'codigo': 'PRODUTO',
            'nome_produto': 'NOME',
            'une_nome': 'UNE_NOME',
            'nomesegmento': 'NOMESEGMENTO',
            'nome_categoria': 'NomeCategoria',
            'nome_fabricante': 'NomeFabricante',
            'preco_38_percent': 'LIQUIDO_38',
            'mes_01': 'MES_01',
            'mes_02': 'MES_02',
            'mes_03': 'MES_03',
            'mes_04': 'MES_04',
            'mes_05': 'MES_05',
            'mes_06': 'MES_06',
            'mes_07': 'MES_07',
            'mes_08': 'MES_08',
            'mes_09': 'MES_09',
            'mes_10': 'MES_10',
            'mes_11': 'MES_11',
            'mes_12': 'MES_12',
            'estoque_atual': 'ESTOQUE_UNE',
            'venda_30_d': 'VENDA_30DD',
        }

        if not filters:
            # Sem filtros: retorna amostra segura
            return "SELECT TOP 500 * FROM ADMMATAO"

        where_clauses = []

        for col, val in filters.items():
            # Mapear nome da coluna
            sql_col = column_mapping.get(col, col.upper())

            # Construir WHERE clause
            if isinstance(val, str):
                # Escape de aspas simples
                val_escaped = val.replace("'", "''")
                where_clauses.append(f"{sql_col} = '{val_escaped}'")
            elif isinstance(val, (int, float)):
                where_clauses.append(f"{sql_col} = {val}")
            elif val is None:
                where_clauses.append(f"{sql_col} IS NULL")
            else:
                # Fallback: converter para string
                where_clauses.append(f"{sql_col} = '{str(val)}'")

        where_sql = " AND ".join(where_clauses)
        return f"SELECT * FROM ADMMATAO WHERE {where_sql}"

    def _switch_to_fallback(self):
        """Muda para Parquet em caso de falha SQL."""
        logger.warning("[FALLBACK] Mudando para modo Parquet")
        self.current_source = "parquet"
        self.sql_available = False
        self.parquet_adapter.connect()

    def get_schema(self) -> str:
        """Retorna schema da fonte de dados ativa."""
        if self.current_source == "sqlserver" and self.sql_adapter:
            try:
                return self.sql_adapter.get_schema()
            except:
                self._switch_to_fallback()

        return self.parquet_adapter.get_schema()

    def get_status(self) -> Dict[str, Any]:
        """Retorna status detalhado do adapter para debugging."""
        return {
            "current_source": self.current_source,
            "sql_available": self.sql_available,
            "sql_enabled": self.use_sql_server,
            "fallback_enabled": self.fallback_enabled,
            "adapter_type": "hybrid"
        }

    def _load_dataframe(self):
        """
        Carrega DataFrame completo.
        Delega para o parquet_adapter.
        """
        if hasattr(self.parquet_adapter, '_load_dataframe'):
            self.parquet_adapter._load_dataframe()

    @property
    def _dataframe(self):
        """
        Propriedade para acesso ao DataFrame.
        Retorna DataFrame do parquet_adapter.
        """
        if hasattr(self.parquet_adapter, '_dataframe'):
            return self.parquet_adapter._dataframe
        return None

    @property
    def file_path(self):
        """
        Propriedade para acesso ao caminho do arquivo.
        Retorna file_path do parquet_adapter interno.
        """
        if hasattr(self.parquet_adapter, 'file_path'):
            return self.parquet_adapter.file_path
        return None

    def __repr__(self):
        return f"HybridDataAdapter(source={self.current_source}, sql_available={self.sql_available})"
