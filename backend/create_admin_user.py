import polars as pl
from pathlib import Path
import bcrypt
from datetime import datetime, timezone
import uuid

# Criar diretório se não existir
parquet_dir = Path(__file__).parent / "data" / "parquet"
parquet_dir.mkdir(parents=True, exist_ok=True)

# Criar hash da senha usando bcrypt diretamente
password = "Admin@2024"
password_bytes = password.encode('utf-8')
salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

print(f"Senha: {password}")
print(f"Hash: {hashed_password}")

# Verificar se o hash funciona
is_valid = bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
print(f"Verificação: {is_valid}")

# Criar DataFrame com usuário admin
users_data = {
    "id": [str(uuid.uuid4())],
    "username": ["admin"],
    "email": ["admin@agentbi.com"],
    "hashed_password": [hashed_password],
    "role": ["admin"],
    "is_active": [True],
    "created_at": [datetime.now(timezone.utc)],
    "updated_at": [datetime.now(timezone.utc)],
    "last_login": [None]
}

df = pl.DataFrame(users_data)

print("\nDataFrame criado:")
print(df)

# Salvar como Parquet
parquet_path = parquet_dir / "users.parquet"
df.write_parquet(parquet_path)

print(f"\n✅ Arquivo salvo em: {parquet_path}")
print(f"✅ Arquivo existe: {parquet_path.exists()}")

# Verificar leitura
df_read = pl.read_parquet(parquet_path)
print(f"\n✅ Verificação de leitura:")
print(df_read)
