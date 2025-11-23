# Drop alembic_version table if it exists
import os
import pyodbc
from app.config.settings import get_settings

settings = get_settings()
conn_str = settings.PYODBC_CONNECTION_STRING

conn = pyodbc.connect(conn_str, autocommit=True)
cursor = conn.cursor()
# Check if table exists
cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'alembic_version'")
exists = cursor.fetchone()[0]
if exists:
    cursor.execute("DROP TABLE alembic_version")
    print("alembic_version table dropped")
else:
    print("alembic_version table not present")
conn.close()
