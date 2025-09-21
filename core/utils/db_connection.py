from sqlalchemy import create_engine
from core.config.settings import settings # Import the new settings object
from typing import Optional

# A URI da base de dados é agora obtida diretamente do objeto de configurações centralizado.
DATABASE_URI = settings.SQL_SERVER_CONNECTION_STRING

# Create the SQLAlchemy engine only if DATABASE_URI is available
engine = None
if DATABASE_URI:
    engine = create_engine(DATABASE_URI, pool_size=10, max_overflow=20)

def get_db_connection():
    """
    Retorna uma conexão com o banco de dados SQL Server do pool de conexões do SQLAlchemy.
    Retorna None se não houver configuração de banco disponível.
    """
    if engine is None:
        return None
    return engine.connect()
