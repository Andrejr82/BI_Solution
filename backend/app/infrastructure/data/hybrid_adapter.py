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
        logger.info(f"[PARQUET] Usando arquivo Parquet: {parquet_path}")
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
        """Tenta conectar ao SQL Server e define a fonte primária com base na disponibilidade."""
        if self.use_sql_server and self.sql_adapter:
            try:
                # Tentar conectar com timeout
                await asyncio.wait_for(self.sql_adapter.connect(), timeout=self.sql_timeout)
                self.sql_available = True
                self.current_source = "sql_server"
                logger.info("[SQL OK] Conectado ao SQL Server. Fonte de dados definida como SQL Server.")
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning(f"[FALLBACK] Falha ao conectar SQL Server: {e}. Fallback para Parquet ativado.")
                self.sql_available = False
                self.current_source = "parquet"
        else:
            self.current_source = "parquet"
        
        # Parquet "conecta" (lazy) para estar pronto para fallback
        await self.parquet_adapter.connect()

    async def disconnect(self) -> None:
        if self.sql_adapter:
            await self.sql_adapter.disconnect()
        if self.parquet_adapter:
            await self.parquet_adapter.disconnect()

    async def execute_query(self, query_filters: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
        """
        Executa query com fallback automático: SQL Server -> Parquet.
        """
        result = []
        used_source = self.current_source

        # Tentar SQL Server primeiro se for a fonte atual
        if self.current_source == "sql_server" and self.sql_adapter:
            try:
                # SQL Adapter deve suportar a mesma interface ou kwargs
                result = await self.sql_adapter.execute_query(query_filters, **kwargs)
                return result
            except Exception as e:
                logger.error(f"[ERROR] Erro na consulta SQL Server: {e}")
                if self.fallback_enabled:
                    logger.info("[FALLBACK] Tentando fallback para Parquet...")
                    used_source = "parquet"
                    # Não alteramos self.current_source permanentemente aqui, apenas para esta query
                    # ou poderíamos alterar se quiséssemos "downgrade" automático
                else:
                    raise e
        
        # Executar no Parquet (se for a fonte atual ou fallback)
        if used_source == "parquet" and self.parquet_adapter:
            return await self.parquet_adapter.execute_query(query_filters, **kwargs)
        
        return []

    async def get_schema(self) -> str:
        """Retorna schema do Parquet."""
        return await self.parquet_adapter.get_schema()
