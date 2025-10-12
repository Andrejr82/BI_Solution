"""
Módulo para scripts/test_sql_quick.py. Define a classe principal 'Settings'.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Carregar .env
from pathlib import Path
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip().strip('"')

print("=== Teste Rapido SQL Server ===\n")

# Testar imports
try:
    from core.connectivity.sql_server_adapter import SQLServerAdapter
    print("[OK] SQLServerAdapter importado")
except Exception as e:
    print(f"[ERRO] Import SQLServerAdapter: {e}")
    sys.exit(1)

# Criar settings mock
class Settings:
    def __init__(self):
        driver = os.getenv("DB_DRIVER")
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        database = os.getenv("DB_NAME")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        trust_cert = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")

        server = f"{host},{port}" if port else host

        self.PYODBC_CONNECTION_STRING = (
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
            f"TrustServerCertificate={trust_cert};"
        )

        print(f"Connection String: {self.PYODBC_CONNECTION_STRING}\n")

settings = Settings()

# Testar conexão
try:
    adapter = SQLServerAdapter(settings)
    print("Conectando SQL Server...")
    adapter.connect()
    print("[OK] SQL Server CONECTADO!\n")

    # Testar query
    result = adapter.execute_query("SELECT COUNT(*) as total FROM ADMMATAO")
    print(f"[OK] Tabela ADMMATAO: {result[0]['total']:,} registros\n")

    adapter.disconnect()
    print("=== SUCESSO ===")

except Exception as e:
    print(f"[ERRO] {e}")
    import traceback
    traceback.print_exc()
