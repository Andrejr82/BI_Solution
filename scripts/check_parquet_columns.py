import pandas as pd
import sys

# Ler parquet
df = pd.read_parquet(r'C:\Users\André\Documents\Agent_Solution_BI\data\parquet\admmat.parquet')

print("=" * 80)
print("COLUNAS DO ADMMAT.PARQUET")
print("=" * 80)
print(f"\nTotal de colunas: {len(df.columns)}\n")

print("Todas as colunas:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i:3d}. {col}")

print("\n" + "=" * 80)
print("COLUNAS COM 'DATA' OU 'DATE'")
print("=" * 80)
date_cols = [c for c in df.columns if 'data' in c.lower() or 'date' in c.lower()]
if date_cols:
    for col in date_cols:
        print(f"  - {col}")
        print(f"    Tipo: {df[col].dtype}")
        print(f"    Exemplo: {df[col].iloc[0] if len(df) > 0 else 'N/A'}")
else:
    print("  NENHUMA COLUNA DE DATA ENCONTRADA!")

print("\n" + "=" * 80)
print("COLUNAS COM 'MES' OU 'MONTH'")
print("=" * 80)
mes_cols = [c for c in df.columns if 'mes' in c.lower() or 'month' in c.lower()]
if mes_cols:
    for col in mes_cols:
        print(f"  - {col}")
        print(f"    Tipo: {df[col].dtype}")
        print(f"    Exemplo: {df[col].iloc[0] if len(df) > 0 else 'N/A'}")
else:
    print("  NENHUMA COLUNA DE MÊS ENCONTRADA!")

print("\n" + "=" * 80)
print("INFO DO DATASET")
print("=" * 80)
print(f"Total de registros: {len(df)}")
print(f"Tamanho em memória: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
