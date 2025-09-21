from sqlalchemy import create_engine
from core.config.settings import settings # Import the settings object
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# A URI da base de dados é obtida do objeto de configurações
DATABASE_URI = settings.SQL_SERVER_CONNECTION_STRING

# Create the SQLAlchemy engine with connection pooling
engine = create_engine(DATABASE_URI, pool_size=10, max_overflow=20)

def get_db_connection():
    """
    Retorna uma conexão com o banco de dados SQL Server do pool de conexões do SQLAlchemy.
    """
    return engine.connect()
