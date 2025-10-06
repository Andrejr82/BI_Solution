"""
HybridDataAdapter: SQL Server (primário) + Parquet (fallback automático)
Adapter inteligente que garante zero downtime.

Uso:
    adapter = HybridDataAdapter()
    result = adapter.execute_query({})  # tenta SQL Server, fallback para Parquet
"""
import logging
from typing import Dict, Any, List, Optional
import os
from pathlib import Path

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

            parquet_path = Path(os.getcwd()) / "data" / "parquet" / "admmat.parquet"

            if not parquet_path.exists():
                # Tentar paths alternativos
                alt_paths = [
                    Path(__file__).parent.parent.parent / "data" / "parquet" / "admmat.parquet",
                    Path("data/parquet/admmat.parquet"),
                ]

                for alt_path in alt_paths:
                    if alt_path.exists():
                        parquet_path = alt_path
                        break

            self.parquet_adapter = ParquetAdapter(file_path=str(parquet_path))
            logger.info(f"[OK] Parquet adapter inicializado: {parquet_path}")

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

            # Testar conexão
            logger.info("Tentando conectar SQL Server...")
            self.sql_adapter.connect()

            # Se chegou aqui, conexão OK
            self.sql_available = True
            self.current_source = "sqlserver"
            logger.info("[OK] SQL Server conectado - modo HIBRIDO ativo")

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
        return result

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
        Compatibilidade com DirectQueryEngine.
        Delega para o parquet_adapter.
        """
        if hasattr(self.parquet_adapter, '_load_dataframe'):
            self.parquet_adapter._load_dataframe()

    @property
    def _dataframe(self):
        """
        Propriedade para compatibilidade com DirectQueryEngine.
        Retorna DataFrame do parquet_adapter.
        """
        if hasattr(self.parquet_adapter, '_dataframe'):
            return self.parquet_adapter._dataframe
        return None

    def __repr__(self):
        return f"HybridDataAdapter(source={self.current_source}, sql_available={self.sql_available})"
