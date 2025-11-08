"""
Teste direto do filtro de produto usando Pandas
Reproduzir exatamente o que _load_data faz
"""
import pandas as pd
import sys
from pathlib import Path

# Configurar encoding UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def teste_filtro():
    """Testar filtro exatamente como _load_data faz"""

    print("=" * 80)
    print("TESTE DE FILTRO: Reproduzindo _load_data")
    print("=" * 80)

    parquet_path = "data/parquet/admmat.parquet"

    # Simular o que _load_data faz
    produto_id = 369947
    une_id = 2720

    # Colunas solicitadas pela funcao calcular_mc_produto
    columns_requested = ['codigo', 'nome_produto', 'une', 'mc', 'estoque_atual',
                        'linha_verde', 'nomesegmento', 'ESTOQUE_GONDOLA', 'estoque_gondola']

    # Mapear colunas (como _load_data faz)
    parquet_cols = []
    for col in columns_requested:
        if col == 'linha_verde':
            parquet_cols.append('estoque_lv')
        elif col == 'mc':
            parquet_cols.append('media_considerada_lv')
        else:
            parquet_cols.append(col)

    print("\nColunas solicitadas:", columns_requested)
    print("Colunas mapeadas para Parquet:", parquet_cols)

    # Tentar carregar
    try:
        print(f"\n1. Tentando carregar com colunas especificas...")
        df = pd.read_parquet(parquet_path, columns=parquet_cols)
        print(f"   [OK] Carregado: {len(df):,} linhas")

    except Exception as e:
        print(f"   [ERRO] Falha ao carregar: {e}")
        print("\n2. Tentando sem especificar colunas...")
        df = pd.read_parquet(parquet_path)
        print(f"   [OK] Carregado: {len(df):,} linhas")

        # Verificar quais colunas existem
        print("\nColunas que existem no Parquet:")
        missing = []
        present = []
        for col in parquet_cols:
            if col in df.columns:
                present.append(col)
            else:
                missing.append(col)

        if present:
            print(f"  Presentes: {present}")
        if missing:
            print(f"  FALTANDO: {missing}")

    # Aplicar filtros
    print(f"\n3. Aplicando filtros: codigo={produto_id}, une={une_id}")

    # TESTE 1: Filtro separado
    df_codigo = df[df['codigo'] == produto_id]
    print(f"   Produtos com codigo {produto_id}: {len(df_codigo)}")

    df_une = df[df['une'] == une_id]
    print(f"   Produtos na UNE {une_id}: {len(df_une)}")

    # TESTE 2: Filtro combinado (como _load_data faz)
    produto_df = df.copy()
    filters = {'codigo': produto_id, 'une': une_id}

    for col, val in filters.items():
        if col in produto_df.columns:
            print(f"   Aplicando filtro: {col} == {val}")
            antes = len(produto_df)
            produto_df = produto_df[produto_df[col] == val]
            depois = len(produto_df)
            print(f"      Registros antes: {antes:,}, depois: {depois:,}")
        else:
            print(f"   [ERRO] Coluna '{col}' nao existe!")

    print(f"\n4. Resultado final:")
    if produto_df.empty:
        print("   [ERRO] DataFrame VAZIO - Produto nao encontrado!")
    else:
        print(f"   [OK] Encontrado: {len(produto_df)} registro(s)")

        # Mostrar dados
        row = produto_df.iloc[0]
        print("\n   Valores encontrados:")
        for col in columns_requested:
            # Mapear de volta para coluna do parquet
            parquet_col = None
            if col == 'linha_verde':
                parquet_col = 'estoque_lv'
            elif col == 'mc':
                parquet_col = 'media_considerada_lv'
            else:
                parquet_col = col

            if parquet_col in row.index:
                valor = row[parquet_col]
                print(f"      {col:30s} ({parquet_col:30s}) = {valor}")
            else:
                print(f"      {col:30s} - COLUNA NAO ENCONTRADA")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    teste_filtro()
