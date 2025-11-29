import polars as pl
from pathlib import Path
import sys

# Caminho do arquivo
parquet_path = Path(__file__).parent / "data" / "parquet" / "users.parquet"

print(f"Verificando: {parquet_path}")
print(f"Existe: {parquet_path.exists()}")

if parquet_path.exists():
    try:
        df = pl.read_parquet(parquet_path)
        print(f"\nTotal de usuários: {len(df)}")
        print(f"\nColunas: {df.columns}")
        print(f"\nDados:")
        print(df)
        
        # Verificar se admin existe
        admin_users = df.filter(pl.col("username") == "admin")
        print(f"\nUsuários 'admin' encontrados: {len(admin_users)}")
        if len(admin_users) > 0:
            print(admin_users)
    except Exception as e:
        print(f"Erro ao ler Parquet: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\nArquivo users.parquet NÃO ENCONTRADO!")
