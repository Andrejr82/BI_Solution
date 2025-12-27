"""
SQLServerAdapter: Adaptador para Microsoft SQL Server usando aioodbc (Async).
"""

import logging
import aioodbc
from typing import Any, Dict, List, Optional

from app.infrastructure.data.base import DatabaseAdapter
from app.core.utils.serializers import TypeConverter

logger = logging.getLogger(__name__)

class SQLServerAdapter(DatabaseAdapter):
    """Concrete implementation of the adapter for Microsoft SQL Server (Async)."""

    def __init__(self, settings: Any):
        self._settings = settings
        self._pool = None
        # Connection string deve ser compatível com aioodbc (geralmente a mesma do pyodbc)
        self._dsn = settings.PYODBC_CONNECTION_STRING

    async def connect(self) -> None:
        """
        Establishes connection pool.
        aioodbc recommends using a pool.
        """
        if not self._pool:
            try:
                logger.info("Attempting to connect to SQL Server (aioodbc)...")
                # Criar pool de conexões
                self._pool = await aioodbc.create_pool(dsn=self._dsn, minsize=1, maxsize=10, autocommit=True)
                logger.info("SQL Server connection pool created successfully.")
            except Exception as ex:
                logger.error(f"SQL Server connection failed: {ex}", exc_info=True)
                raise

    async def disconnect(self) -> None:
        """Closes the connection pool."""
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()
            self._pool = None
            logger.info("SQL Server connection pool closed.")

    async def execute_query(self, query: str, params: Optional[list] = None) -> List[Dict[str, Any]]:
        """
        Executes a SQL query asynchronously with safe serialization.
        Supports parameterized queries to prevent SQL Injection.
        """
        if not self._pool:
            await self.connect()

        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                logger.debug(f"Executing query: {query}")
                if params:
                    await cursor.execute(query, params)
                else:
                    await cursor.execute(query)

                if cursor.description:
                    columns = [column[0] for column in cursor.description]
                    rows = await cursor.fetchall()

                    # Converter Row objects para dicts
                    results = []
                    for row in rows:
                        try:
                            # Tenta usar _mapping (SQLAlchemy Row)
                            if hasattr(row, '_mapping'):
                                results.append(TypeConverter.convert(dict(row._mapping)))
                            else:
                                # Fallback: zip com colunas e converter tipos
                                row_dict = dict(zip(columns, row))
                                results.append(TypeConverter.convert(row_dict))
                        except Exception as e:
                            logger.warning(f"Row conversion error: {e}, using basic fallback")
                            # Último recurso: conversão simples
                            results.append(dict(zip(columns, row)))

                    logger.debug(f"Query returned {len(results)} rows (serialization-safe).")
                    return results
                else:
                    return []

    async def get_schema(self) -> str:
        """
        Inspeciona o banco de dados e gera uma string DDL (CREATE TABLE).
        """
        if not self._pool:
            await self.connect()

        schema_ddl = ""
        
        # Query para pegar tabelas
        tables_query = """
        SELECT TABLE_SCHEMA, TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        """
        
        try:
            tables = await self.execute_query(tables_query)
            
            for table in tables:
                schema = table['TABLE_SCHEMA']
                name = table['TABLE_NAME']
                
                columns_query = f"""
                SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = '{name}' AND TABLE_SCHEMA = '{schema}'
                """
                
                columns = await self.execute_query(columns_query)
                
                ddl = f"CREATE TABLE {schema}.{name} (\n"
                col_defs = []
                for col in columns:
                    col_def = f"  {col['COLUMN_NAME']} {col['DATA_TYPE']}"
                    if col['CHARACTER_MAXIMUM_LENGTH']:
                        col_def += f"({col['CHARACTER_MAXIMUM_LENGTH']})"
                    if col['IS_NULLABLE'] == 'NO':
                        col_def += " NOT NULL"
                    col_defs.append(col_def)
                
                ddl += ",\n".join(col_defs)
                ddl += "\n);\n\n"
                schema_ddl += ddl
                
            return schema_ddl
            
        except Exception as e:
            logger.error(f"Error getting schema: {e}")
            return f"Error getting schema: {e}"
