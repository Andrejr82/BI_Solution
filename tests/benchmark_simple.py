"""
Benchmark Simples e Direto: Polars vs Dask vs Pandas
=====================================================
Testa operações reais do projeto com 1.1M linhas
"""

import time
import sys

parquet_path = 'data/parquet/admmat.parquet'

print("="*80)
print("BENCHMARK: Polars vs Dask (com dados reais do projeto)")
print("="*80)
print("Dataset: 1.1M linhas, 93MB (admmat.parquet)")
print("="*80)
print()

# ====================================================================
# TESTE 1: Filtro + Agregação (query típica do projeto)
# ====================================================================
print("TESTE 1: Filtro por segmento + Agregação de vendas")
print("-"*80)

# POLARS
print("\n1.1 POLARS (lazy execution):")
try:
    import polars as pl
    start = time.time()
    result = (
        pl.scan_parquet(parquet_path)
        .filter(pl.col('nomesegmento') == 'TECIDOS')
        .group_by('nomesegmento')
        .agg(pl.col('venda_30_d').sum())
        .collect()
    )
    time_polars = time.time() - start
    print(f"   Tempo: {time_polars:.3f}s")
    print(f"   Total vendas TECIDOS: R$ {result['venda_30_d'][0]:,.2f}")
except Exception as e:
    print(f"   ERRO: {e}")
    time_polars = float('inf')

# DASK
print("\n1.2 DASK (distributed computing):")
try:
    import dask.dataframe as dd
    start = time.time()
    ddf = dd.read_parquet(parquet_path, engine='pyarrow')
    result = ddf[ddf['nomesegmento'] == 'TECIDOS'].groupby('nomesegmento')['venda_30_d'].sum().compute()
    time_dask = time.time() - start
    print(f"   Tempo: {time_dask:.3f}s")
    print(f"   Total vendas TECIDOS: R$ {result.iloc[0]:,.2f}")
except Exception as e:
    print(f"   ERRO: {e}")
    time_dask = float('inf')

# PANDAS (com amostragem devido a limite de memória)
print("\n1.3 PANDAS (in-memory, limitado por memória):")
try:
    import pandas as pd
    import pyarrow.parquet as pq

    # Ler apenas primeiras 100k linhas para não estourar memória
    start = time.time()
    parquet_file = pq.ParquetFile(parquet_path)
    df = parquet_file.read_row_groups([0]).to_pandas()  # Primeiro row group
    result = df[df['nomesegmento'] == 'TECIDOS'].groupby('nomesegmento')['venda_30_d'].sum()
    time_pandas = time.time() - start
    print(f"   Tempo: {time_pandas:.3f}s")
    print(f"   Total vendas TECIDOS (amostra): R$ {result.iloc[0]:,.2f}")
    print(f"   NOTA: Pandas limitado a primeiro row group por limitação de memória")
except Exception as e:
    print(f"   ERRO: {e}")
    time_pandas = float('inf')

# ====================================================================
# TESTE 2: Ranking complexo (TOP 10)
# ====================================================================
print("\n\nTESTE 2: Ranking TOP 10 produtos mais vendidos")
print("-"*80)

# POLARS
print("\n2.1 POLARS:")
try:
    start = time.time()
    result = (
        pl.scan_parquet(parquet_path)
        .sort('venda_30_d', descending=True)
        .head(10)
        .select(['codigo', 'nome_produto', 'venda_30_d'])
        .collect()
    )
    time_polars_rank = time.time() - start
    print(f"   Tempo: {time_polars_rank:.3f}s")
    print(f"   TOP 1: {result['nome_produto'][0]} (R$ {result['venda_30_d'][0]:,.2f})")
except Exception as e:
    print(f"   ERRO: {e}")
    time_polars_rank = float('inf')

# DASK
print("\n2.2 DASK:")
try:
    start = time.time()
    ddf = dd.read_parquet(parquet_path, engine='pyarrow')
    result = ddf.nlargest(10, 'venda_30_d')[['codigo', 'nome_produto', 'venda_30_d']].compute()
    time_dask_rank = time.time() - start
    print(f"   Tempo: {time_dask_rank:.3f}s")
    print(f"   TOP 1: {result.iloc[0]['nome_produto']} (R$ {result.iloc[0]['venda_30_d']:,.2f})")
except Exception as e:
    print(f"   ERRO: {e}")
    time_dask_rank = float('inf')

# ====================================================================
# TESTE 3: Múltiplas agregações por segmento
# ====================================================================
print("\n\nTESTE 3: Agregações múltiplas por segmento (SUM, AVG, COUNT)")
print("-"*80)

# POLARS
print("\n3.1 POLARS:")
try:
    start = time.time()
    result = (
        pl.scan_parquet(parquet_path)
        .group_by('nomesegmento')
        .agg([
            pl.col('venda_30_d').sum().alias('total_vendas'),
            pl.col('venda_30_d').mean().alias('media_vendas'),
            pl.count().alias('qtd_produtos')
        ])
        .sort('total_vendas', descending=True)
        .collect()
    )
    time_polars_multi = time.time() - start
    print(f"   Tempo: {time_polars_multi:.3f}s")
    print(f"   Segmentos processados: {len(result)}")
except Exception as e:
    print(f"   ERRO: {e}")
    time_polars_multi = float('inf')

# DASK
print("\n3.2 DASK:")
try:
    start = time.time()
    ddf = dd.read_parquet(parquet_path, engine='pyarrow')
    result = ddf.groupby('nomesegmento').agg({
        'venda_30_d': ['sum', 'mean', 'count']
    }).compute()
    time_dask_multi = time.time() - start
    print(f"   Tempo: {time_dask_multi:.3f}s")
    print(f"   Segmentos processados: {len(result)}")
except Exception as e:
    print(f"   ERRO: {e}")
    time_dask_multi = float('inf')

# ====================================================================
# RESUMO FINAL
# ====================================================================
print("\n\n" + "="*80)
print("RESUMO DOS RESULTADOS")
print("="*80)
print()
print(f"{'Teste':<40} {'Polars':<12} {'Dask':<12} {'Vencedor':<12}")
print("-"*80)

tests = [
    ("Filtro + Agregação", time_polars, time_dask),
    ("Ranking TOP 10", time_polars_rank, time_dask_rank),
    ("Múltiplas Agregações", time_polars_multi, time_dask_multi)
]

polars_wins = 0
dask_wins = 0

for test_name, t_polars, t_dask in tests:
    winner = "Polars" if t_polars < t_dask else "Dask"
    if winner == "Polars":
        polars_wins += 1
    else:
        dask_wins += 1

    speedup = t_dask / t_polars if t_polars < t_dask else t_polars / t_dask
    winner_text = f"{winner} ({speedup:.1f}x)"

    print(f"{test_name:<40} {t_polars:>10.3f}s {t_dask:>10.3f}s {winner_text:<12}")

print("-"*80)
print(f"{'TOTAL DE VITÓRIAS':<40} {polars_wins:>10} {dask_wins:>10}")
print("="*80)
print()

# Recomendação
if polars_wins > dask_wins:
    speedup_avg = sum([t[2]/t[1] for t in tests if t[1] < t[2]]) / polars_wins
    print(f"RECOMENDAÇÃO: Usar POLARS")
    print(f"  - {polars_wins}/{len(tests)} vitórias")
    print(f"  - Em média {speedup_avg:.1f}x mais rápido que Dask")
    print(f"  - Sintaxe moderna e expressiva")
    print(f"  - Melhor uso de memória")
else:
    print(f"RECOMENDAÇÃO: Manter DASK")
    print(f"  - {dask_wins}/{len(tests)} vitórias")
    print(f"  - Melhor para datasets distribuídos")

print()
print("NOTA: Pandas não incluído na comparação final devido a limitação")
print("de memória com dataset de 1.1M linhas.")
print("="*80)
