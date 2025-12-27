
import pyodbc
import polars as pl
from pathlib import Path

# Configurações
CONN_STR = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;DATABASE=agentbi;UID=AgenteVirtual;PWD=Cacula@2020;TrustServerCertificate=yes;"
PARQUET_PATH = Path("backend/data/parquet/users.parquet")
USERS_TO_CHECK = ["lucas.garcia", "hugo.mendes", "fausto.neto"]

def check_sql():
    print("--- Verificando SQL Server ---")
    try:
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        for user in USERS_TO_CHECK:
            cursor.execute("SELECT username, role, is_active FROM users WHERE username = ?", (user,))
            row = cursor.fetchone()
            if row:
                print(f"✅ Usuário '{user}' encontrado! (Role: {row[1]}, Ativo: {row[2]})")
            else:
                print(f"❌ Usuário '{user}' NÃO encontrado.")
        conn.close()
    except Exception as e:
        print(f"Erro no SQL Server: {e}")

def check_parquet():
    print("\n--- Verificando Parquet ---")
    if not PARQUET_PATH.exists():
        print(f"Arquivo {PARQUET_PATH} não encontrado.")
        return
    try:
        df = pl.read_parquet(PARQUET_PATH)
        for user in USERS_TO_CHECK:
            user_data = df.filter(pl.col("username") == user)
            if len(user_data) > 0:
                row = user_data.row(0, named=True)
                print(f"✅ Usuário '{user}' encontrado! (Role: {row['role']}, Ativo: {row['is_active']})")
            else:
                print(f"❌ Usuário '{user}' NÃO encontrado.")
    except Exception as e:
        print(f"Erro no Parquet: {e}")

if __name__ == "__main__":
    check_sql()
    check_parquet()
