from sqlalchemy import create_engine
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Global engine variable (lazy loaded)
engine = None

def get_engine():
    """Obtém o engine do banco usando lazy loading"""
    global engine
    if engine is None:
        try:
            from core.config.settings import get_settings
            settings = get_settings()
            DATABASE_URI = settings.SQL_SERVER_CONNECTION_STRING
            engine = create_engine(DATABASE_URI, pool_size=10, max_overflow=20)
            logger.info("✅ Engine de banco inicializado")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar engine: {e}")
            engine = None
    return engine

def get_db_connection():
    """
    Retorna uma conexão com o banco de dados SQL Server do pool de conexões do SQLAlchemy.
    """
    current_engine = get_engine()
    if current_engine is None:
        return None
    return current_engine.connect()
