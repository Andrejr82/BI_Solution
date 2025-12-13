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
        # Usar configuração centralizada do settings.py
        parquet_path = settings.PARQUET_FILE_PATH
        logger.info(f"📂 Usando arquivo Parquet: {parquet_path}")
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
        """Tenta conectar ao SQL Server (apenas para check), mas garante Parquet para queries."""
        if self.use_sql_server and self.sql_adapter:
            try:
                # Tentar conectar com timeout apenas para garantir que o serviço está de pé se necessário
                await asyncio.wait_for(self.sql_adapter.connect(), timeout=self.sql_timeout)
                self.sql_available = True
                # self.current_source = "sql_server" # REMOVIDO: Forçar Parquet como fonte de dados
                logger.info("✅ Conectado ao SQL Server (Disponível para Sync/Auth).")
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning(f"⚠️ Falha ao conectar SQL Server: {e}. Operando apenas com Parquet.")
                self.sql_available = False
        
        # Parquet "conecta" (lazy)
        # Garantir que a fonte atual seja SEMPRE parquet para queries
        self.current_source = "parquet"
        await self.parquet_adapter.connect()

    async def disconnect(self) -> None:
        if self.sql_adapter:
            await self.sql_adapter.disconnect()
        if self.parquet_adapter:
            await self.parquet_adapter.disconnect()

    async def execute_query(self, query_filters: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
        """
        Executa query EXCLUSIVAMENTE no Parquet.
        Aceita kwargs (ex: required_columns, query_text)
        """
        if self.parquet_adapter:
            return await self.parquet_adapter.execute_query(query_filters, **kwargs)
        
        return []

    async def get_schema(self) -> str:
        """Retorna schema do Parquet."""
        return await self.parquet_adapter.get_schema()
