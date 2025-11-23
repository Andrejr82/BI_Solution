"""
HybridDataAdapter: Adaptador híbrido com fallback automático e inteligente.
Versão Async para FastAPI.

Prioridade:
1. SQL Server (se USE_SQL_SERVER=true e conexão OK)
2. Parquet (fallback sempre disponível)
"""

import logging
import os
import asyncio
from typing import Any, Dict, List, Optional

from app.infrastructure.data.base import DatabaseAdapter
from app.infrastructure.data.sql_server_adapter import SQLServerAdapter
from app.infrastructure.data.parquet_adapter import ParquetAdapter
from app.config.settings import settings

logger = logging.getLogger(__name__)

class HybridDataAdapter(DatabaseAdapter):
    """
    Adapter híbrido com fallback automático.
    """

    def __init__(self):
        """Inicializa adapter com configurações do settings.py"""
        # Flags de controle
        self.use_sql_server = settings.USE_SQL_SERVER
        self.sql_timeout = settings.SQL_SERVER_TIMEOUT
        self.fallback_enabled = settings.FALLBACK_TO_PARQUET

        # Status de conexão
        self.sql_available = False
        self.current_source = "parquet"  # default seguro

        # Adapters
        self.sql_adapter: Optional[SQLServerAdapter] = None
        self.parquet_adapter: Optional[ParquetAdapter] = None

        # Inicializar adapters
        self._init_adapters()

        logger.info(f"HybridDataAdapter inicializado - Fonte Inicial: {self.current_source}")

    def _init_adapters(self):
        """Inicializa adapters."""
        # 1. Inicializar Parquet (sempre necessário como fallback)
        # Caminho do arquivo parquet deve vir de config ou ser descoberto
        parquet_path = os.getenv("PARQUET_FILE_PATH", "data/parquet/*.parquet")
        self.parquet_adapter = ParquetAdapter(parquet_path)

        # 2. Inicializar SQL Server se habilitado
        if self.use_sql_server:
            try:
                # Settings já deve ter a string de conexão configurada
                self.sql_adapter = SQLServerAdapter(settings)
                self.current_source = "sql_server" # Tentativa inicial
            except Exception as e:
                logger.error(f"Erro ao configurar SQL Server Adapter: {e}")
                self.sql_available = False
                self.current_source = "parquet"
        else:
            self.current_source = "parquet"

    async def connect(self) -> None:
        """Tenta conectar ao SQL Server, fallback para Parquet se falhar."""
        if self.use_sql_server and self.sql_adapter:
            try:
                # Tentar conectar com timeout
                await asyncio.wait_for(self.sql_adapter.connect(), timeout=self.sql_timeout)
                self.sql_available = True
                self.current_source = "sql_server"
                logger.info("✅ Conectado ao SQL Server com sucesso.")
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning(f"⚠️ Falha ao conectar SQL Server: {e}. Usando Fallback Parquet.")
                self.sql_available = False
                self.current_source = "parquet"
                
                if not self.fallback_enabled:
                    raise  # Se fallback desabilitado, re-raise erro
        
        # Parquet "conecta" (lazy)
        await self.parquet_adapter.connect()

    async def disconnect(self) -> None:
        if self.sql_adapter:
            await self.sql_adapter.disconnect()
        if self.parquet_adapter:
            await self.parquet_adapter.disconnect()

    async def execute_query(self, query_filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Executa query com fallback automático.
        Nota: SQL Server precisa de query SQL string, Parquet precisa de filtros dict.
        Este método assume que recebe filtros dict e converte para SQL se necessário.
        """
        
        # Tentar SQL Server Primeiro
        if self.use_sql_server and self.sql_available and self.sql_adapter:
            try:
                # Converter filtros para SQL
                sql_query = self._build_sql_query(query_filters)
                return await self.sql_adapter.execute_query(sql_query)
            except Exception as e:
                logger.error(f"Erro na query SQL Server: {e}")
                if self.fallback_enabled:
                    logger.info("🔄 Ativando Fallback para Parquet...")
                    self.current_source = "parquet"
                    # self.sql_available = False # Opcional: marcar como indisponível temporariamente
                else:
                    raise

        # Fallback para Parquet
        if self.fallback_enabled and self.parquet_adapter:
            return await self.parquet_adapter.execute_query(query_filters)
        
        return []

    def _build_sql_query(self, filters: Dict[str, Any]) -> str:
        """
        Constrói query SQL simples a partir de filtros dict.
        Implementação básica - deve ser expandida conforme necessidade.
        """
        # Mapeamento de tabelas/views deve ser configurado
        table_name = "Vendas" # Exemplo, deve ser configurável
        
        conditions = []
        for col, val in filters.items():
            if isinstance(val, str):
                conditions.append(f"{col} = '{val}'")
            else:
                conditions.append(f"{col} = {val}")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        return f"SELECT * FROM {table_name} WHERE {where_clause}"

    async def get_schema(self) -> str:
        if self.current_source == "sql_server" and self.sql_adapter:
            try:
                return await self.sql_adapter.get_schema()
            except:
                pass # Fallback
        
        return await self.parquet_adapter.get_schema()
