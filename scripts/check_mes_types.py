import pandas as pd

df = pd.read_parquet(r'C:\Users\André\Documents\Agent_Solution_BI\data\parquet\admmat.parquet')

print("Tipos das colunas mes_XX:")
for i in range(1, 13):
    col = f'mes_{i:02d}'
    if col in df.columns:
        print(f'{col}: {df[col].dtype}')
        print(f'   Exemplo: {df[col].iloc[0]}')
