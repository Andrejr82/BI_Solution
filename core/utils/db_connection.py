"""
Módulo de conexão com banco de dados SQL Server
VERSÃO FINAL SEM PYDANTIC - 100% COMPATÍVEL COM STREAMLIT CLOUD
"""

from sqlalchemy import create_engine
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Cache global do engine (lazy loading)
_cached_engine = None

def get_engine():
    """
    Obtém o engine do banco usando lazy loading
    ZERO dependências do Pydantic - usa safe_settings
    """
    global _cached_engine

    if _cached_engine is not None:
        return _cached_engine

    try:
        # Import local para evitar circular imports
        from core.config.safe_settings import get_safe_settings

        settings = get_safe_settings()
        database_uri = settings.SQL_SERVER_CONNECTION_STRING

        if database_uri:
            _cached_engine = create_engine(
                database_uri,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True
            )
            logger.info("✅ Engine de banco inicializado com sucesso")
        else:
            logger.warning("⚠️ Database URI não disponível - modo sem banco")
            _cached_engine = None

    except Exception as e:
        logger.error(f"❌ Erro ao inicializar engine: {e}")
        _cached_engine = None

    return _cached_engine

def get_db_connection():
    """
    Retorna uma conexão com o banco de dados SQL Server
    do pool de conexões do SQLAlchemy.

    Returns:
        Connection: Conexão ativa ou None se banco não disponível
    """
    engine = get_engine()

    if engine is None:
        logger.warning("⚠️ Engine não disponível - retornando None")
        return None

    try:
        connection = engine.connect()
        logger.debug("🔗 Conexão de banco obtida do pool")
        return connection
    except Exception as e:
        logger.error(f"❌ Erro ao obter conexão: {e}")
        return None

def is_database_configured():
    """Verifica se banco está configurado"""
    try:
        from core.config.safe_settings import get_safe_settings
        settings = get_safe_settings()
        return settings.is_database_available()
    except Exception:
        return False

def reset_engine():
    """
    Reseta o engine cached - útil para testes
    """
    global _cached_engine
    _cached_engine = None
    logger.info("🔄 Engine cache resetado")
