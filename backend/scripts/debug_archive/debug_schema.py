"""
Debug script to check schema and test product 369947 query
"""
import sys
sys.path.insert(0, '.')

from app.infrastructure.data.duckdb_adapter import duckdb_adapter
import pandas as pd
import traceback

print("="*80)
print("SCHEMA VERIFICATION & PRODUCT 369947 TEST")
print("="*80)

try:
    # 1. Get parquet path
    parquet_path = duckdb_adapter._get_parquet_path()
    print(f'\n[OK] Parquet path: {parquet_path}')

    # 2. Get schema
    print(f'\n{"="*80}')
    print("SCHEMA ANALYSIS")
    print("="*80)

    df_schema = duckdb_adapter.query(f"""
        SELECT column_name, column_type
        FROM (DESCRIBE SELECT * FROM '{parquet_path}')
    """)

    print(f'\nTotal columns: {len(df_schema)}')

    # Find relevant columns
    keywords = ['QUANTIDADE', 'ESTOQUE', 'VENDA', 'SALDO', 'PRODUTO', 'UNE']
    print(f'\n{"="*80}')
    print(f"RELEVANT COLUMNS (containing: {', '.join(keywords)})")
    print("="*80)

    relevant = []
    for idx, row in df_schema.iterrows():
        col_name = row['column_name']
        if any(k in col_name.upper() for k in keywords):
            print(f'  • {col_name:30s} {row["column_type"]}')
            relevant.append(col_name)

    # 3. Test simple query on product 369947
    print(f'\n{"="*80}')
    print("TEST 1: Simple SELECT on product 369947")
    print("="*80)

    test_query1 = f"""
        SELECT PRODUTO, UNE, NOME, ESTOQUE_UNE, VENDA_30DD
        FROM '{parquet_path}'
        WHERE PRODUTO = 369947
        LIMIT 10
    """

    print(f"\nSQL: {test_query1}")
    result1 = duckdb_adapter.query(test_query1)
    print(f'\n[OK] Found {len(result1)} records')

    if len(result1) > 0:
        print(f'\nData types:')
        for col, dtype in result1.dtypes.items():
            print(f'  • {col}: {dtype}')

        print(f'\nFirst 5 rows:')
        print(result1.head().to_string())

        # Check for NULL values
        print(f'\nNULL values check:')
        for col in result1.columns:
            null_count = result1[col].isna().sum()
            if null_count > 0:
                print(f'  • {col}: {null_count} NULLs')

    # 4. Test aggregation with TRY_CAST
    print(f'\n{"="*80}')
    print("TEST 2: SUM aggregation with TRY_CAST")
    print("="*80)

    test_query2 = f"""
        SELECT
            UNE,
            SUM(COALESCE(TRY_CAST(ESTOQUE_UNE AS DOUBLE), 0)) as total_estoque,
            SUM(COALESCE(TRY_CAST(VENDA_30DD AS DOUBLE), 0)) as total_vendas
        FROM '{parquet_path}'
        WHERE PRODUTO = 369947
        GROUP BY UNE
        ORDER BY total_estoque DESC
        LIMIT 20
    """

    print(f"\nSQL: {test_query2}")
    result2 = duckdb_adapter.query(test_query2)
    print(f'\n[OK] Product found in {len(result2)} UNEs')

    if len(result2) > 0:
        print(f'\nTop UNEs by stock:')
        print(result2.head(10).to_string())

        total_stock = result2['total_estoque'].sum()
        total_sales = result2['total_vendas'].sum()
        print(f'\n[SUMMARY]:')
        print(f'  • Total stock across all UNEs: {total_stock:.2f}')
        print(f'  • Total sales (30 days): {total_sales:.2f}')

    # 5. Test using execute_aggregation method
    print(f'\n{"="*80}')
    print("TEST 3: Using execute_aggregation method")
    print("="*80)

    result3 = duckdb_adapter.execute_aggregation(
        agg_col='ESTOQUE_UNE',
        agg_func='sum',
        group_by=['UNE'],
        filters={'PRODUTO': 369947},
        limit=50
    )

    print(f'\n[OK] execute_aggregation returned {len(result3)} rows')
    if len(result3) > 0:
        print(f'\nFirst 10 rows:')
        print(result3.head(10).to_string())

    print(f'\n{"="*80}')
    print("[SUCCESS] ALL TESTS PASSED")
    print("="*80)

except Exception as e:
    print(f'\n{"="*80}')
    print(f"[ERROR] FAILED")
    print("="*80)
    print(f'\nError: {e}')
    print(f'\nFull traceback:')
    traceback.print_exc()
    sys.exit(1)
