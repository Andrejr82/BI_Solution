
import sys
from pathlib import Path
import pandas as pd

# Caminho para o arquivo Parquet
parquet_path = Path(__file__).parent.parent / 'data' / 'parquet' / 'admmat.parquet'

# Colunas necessárias para a verificação
columns_to_load = ['une', 'une_nome', 'codigo', 'nome_produto', 'estoque_atual']

# Carregar apenas as colunas necessárias do DataFrame
try:
    df = pd.read_parquet(parquet_path, columns=columns_to_load)
except Exception as e:
    print(f"Erro ao ler o arquivo Parquet: {e}")
    sys.exit()

# Encontre o une_id para SCR
une_scr = df[df['une_nome'] == 'SCR']
if une_scr.empty:
    print("UNE com nome 'SCR' não encontrada.")
    sys.exit()

une_id_scr = une_scr['une'].iloc[0]
print(f"UNE 'SCR' encontrada com une_id: {une_id_scr}")

# Verifique se o produto 369947 existe na UNE SCR
produto_scr = df[(df['une'] == une_id_scr) & (df['codigo'] == 369947)]

if not produto_scr.empty:
    print("\nProduto 369947 ENCONTRADO na UNE SCR:")
    print(produto_scr[['codigo', 'nome_produto', 'une', 'une_nome', 'estoque_atual']].to_dict('records')[0])
else:
    print("\nProduto 369947 NÃO ENCONTRADO na UNE SCR.")

# Verifique se o produto 369947 existe em qualquer outra UNE
produto_outras_unes = df[df['codigo'] == 369947]
if not produto_outras_unes.empty:
    print("\nO produto 369947 foi encontrado nas seguintes UNEs:")
    print(produto_outras_unes[['une', 'une_nome', 'estoque_atual']].drop_duplicates().to_string(index=False))
else:
    print("\nO produto 369947 não foi encontrado em nenhuma UNE.")
