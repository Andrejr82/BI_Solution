"""Debug: Verificar UNE 2720 no Parquet"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

# Carregar parquet
parquet_path = Path(__file__).parent.parent / 'data' / 'parquet' / 'admmat.parquet'
df = pd.read_parquet(parquet_path)

print(f"Total registros: {len(df):,}")
print(f"\nColunas: {df.columns.tolist()}")

# Verificar se UNE 2720 existe
une_2720_code = df[df['une'] == 2720]
print(f"\n1. Filtro por código (une == 2720): {len(une_2720_code)} registros")

if len(une_2720_code) > 0:
    print(f"   Sigla: {une_2720_code['une_nome'].iloc[0]}")
else:
    # Tentar como string
    une_2720_str = df[df['une'].astype(str) == '2720']
    print(f"2. Filtro por string (une == '2720'): {len(une_2720_str)} registros")

    # Tentar por sigla
    if 'une_nome' in df.columns:
        une_2720_sigla = df[df['une_nome'].str.upper() == '2720']
        print(f"3. Filtro por sigla (une_nome == '2720'): {len(une_2720_sigla)} registros")

# Mostrar amostra de UNEs
print(f"\n5 UNEs exemplo:")
print(df[['une', 'une_nome']].drop_duplicates().head(10))
