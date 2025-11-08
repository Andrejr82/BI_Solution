import pandas as pd
import os

def create_test_parquet():
    caminho_parquet = os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'data',
        'parquet',
        'admmat.parquet'
    )

    df = pd.read_parquet(caminho_parquet)

    # Create a deficit in UNE 2 for some products
    df.loc[df['une'] == 2, 'linha_verde'] = 100
    df.loc[df['une'] == 2, 'estoque'] = 10

    # Create an excess in UNE 1 for the same products
    df.loc[df['une'] == 1, 'linha_verde'] = 10
    df.loc[df['une'] == 1, 'estoque'] = 100

    caminho_teste_parquet = os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'data',
        'parquet',
        'admmat_test.parquet'
    )

    df.to_parquet(caminho_teste_parquet)

if __name__ == "__main__":
    create_test_parquet()
