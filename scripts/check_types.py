import pandas as pd

# Lê o arquivo
df = pd.read_parquet('data/parquet/users.parquet')

print("Tipos das colunas:")
print(df.dtypes)
print("\nPrimeira linha (admin):")
print(df.iloc[0])
