"""
Script rapido para consultar categorias no segmento tecidos com estoque 0
"""
import pandas as pd
import sys

try:
    # Carregar apenas as colunas necessarias para economia de memoria
    # NOTA: NOMECATEGORIA esta em MAIUSCULA no arquivo Parquet
    df = pd.read_parquet(
        'data/parquet/admmat.parquet',
        columns=['nomesegmento', 'NOMECATEGORIA', 'estoque_atual']
    )

    print(f"OK Arquivo carregado: {len(df)} registros")
    print(f"Colunas: {list(df.columns)}")

    # Normalizar nome do segmento para busca case-insensitive
    df['nomesegmento_lower'] = df['nomesegmento'].str.lower().str.strip()

    # Filtrar segmento tecidos
    df_tecidos = df[df['nomesegmento_lower'].str.contains('tecido', na=False)]
    print(f"\nProdutos no segmento Tecidos: {len(df_tecidos)}")

    # Converter estoque_atual para numerico (pode estar como string)
    df_tecidos['estoque_atual'] = pd.to_numeric(df_tecidos['estoque_atual'], errors='coerce').fillna(0)

    # Filtrar estoque 0
    df_estoque_zero = df_tecidos[df_tecidos['estoque_atual'] == 0]
    print(f"Produtos com estoque 0: {len(df_estoque_zero)}")

    # Agrupar por categoria
    categorias_estoque_zero = df_estoque_zero['NOMECATEGORIA'].unique()
    categorias_estoque_zero = sorted([c for c in categorias_estoque_zero if pd.notna(c)])

    print(f"\nCategorias com produtos em estoque 0:")
    print(f"Total: {len(categorias_estoque_zero)} categorias\n")

    for i, cat in enumerate(categorias_estoque_zero, 1):
        qtd = len(df_estoque_zero[df_estoque_zero['NOMECATEGORIA'] == cat])
        print(f"{i}. {cat} ({qtd} produtos)")

except FileNotFoundError:
    print("❌ Arquivo admmat.parquet não encontrado em data/parquet/")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
