import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.connectivity.parquet_adapter import ParquetAdapter
import pandas as pd

# Crie uma instância do ParquetAdapter
parquet_path = Path(__file__).parent.parent / 'data' / 'parquet' / 'admmat.parquet'
adapter = ParquetAdapter(file_path=str(parquet_path))

# Carregue o DataFrame
adapter.connect()
df = adapter._dataframe

# Inspecione o produto com código 369947
produto = df[df['codigo'] == 369947]

if not produto.empty:
    print("Produto encontrado:")
    print(produto.to_dict('records')[0])
else:
    print("Produto com código 369947 não encontrado.")

# Verifique o tipo de dados da coluna 'codigo'
print(f"\nTipo de dados da coluna 'codigo': {df['codigo'].dtype}")

# Verifique se há códigos como string
non_numeric_codes = df[~df['codigo'].apply(lambda x: isinstance(x, (int, float)))]
if not non_numeric_codes.empty:
    print("\nEncontrados códigos não numéricos:")
    print(non_numeric_codes[['codigo']].head())
else:
    print("\nTodos os códigos na coluna 'codigo' são numéricos.")
