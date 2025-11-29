import sqlite3
import sys
from pathlib import Path

# Conectar ao banco
db_path = Path(__file__).parent / "backend_auth.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Tables: {tables}")

# Verificar se tabela users existe
if ('users',) in tables or ('user',) in tables:
    try:
        cursor.execute("SELECT username, email, role FROM users")
        users = cursor.fetchall()
        print(f"\\nUsers found: {len(users)}")
        for user in users:
            print(f"  - {user}")
    except Exception as e:
        print(f"Error querying users: {e}")
else:
    print("\\nUsers table not found!")
    print("You may need to run migrations first.")

conn.close()
