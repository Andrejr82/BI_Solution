"""
Teste rápido do HybridAdapter (Polars + Dask)
"""
import time
from core.connectivity.parquet_adapter import ParquetAdapter

print("=" * 60)
print("TESTE RAPIDO: HYBRID ADAPTER (POLARS + DASK)")
print("=" * 60)

# Inicializar adapter
adapter = ParquetAdapter("data/parquet/admmat.parquet")
print(f"\nEngine selecionada: {adapter._hybrid.engine.upper()}")
print(f"Tamanho arquivo: {adapter._hybrid.size_mb:.1f} MB")
print(f"Threshold: {adapter._hybrid.POLARS_THRESHOLD_MB} MB")

# Teste 1: Query simples
print("\n" + "-" * 60)
print("TESTE 1: Query com filtro (segmento = TECIDOS)")
print("-" * 60)

filters = {"nomesegmento": "TECIDOS"}
start = time.time()
result = adapter.execute_query(filters)
elapsed = time.time() - start

print(f"Resultados: {len(result)} linhas")
print(f"Tempo: {elapsed:.3f}s")
print(f"Engine usado: {adapter._hybrid.engine.upper()}")

if len(result) > 0:
    print(f"Primeira linha: {list(result[0].keys())[:5]}...")
    print(f"Exemplo produto: {result[0].get('NOME', 'N/A')[:50]}")

# Teste 2: Query com filtro numérico
print("\n" + "-" * 60)
print("TESTE 2: Query com filtro numérico (estoque > 100)")
print("-" * 60)

filters2 = {
    "nomesegmento": "TECIDOS",
    "estoque_une": "> 100"
}
start = time.time()
result2 = adapter.execute_query(filters2)
elapsed2 = time.time() - start

print(f"Resultados: {len(result2)} linhas")
print(f"Tempo: {elapsed2:.3f}s")

# Resumo
print("\n" + "=" * 60)
print("RESUMO")
print("=" * 60)
print(f"Engine: {adapter._hybrid.engine.upper()} (automatico)")
print(f"Teste 1: {elapsed:.3f}s ({len(result)} linhas)")
print(f"Teste 2: {elapsed2:.3f}s ({len(result2)} linhas)")
print(f"\nStatus: OK - Sistema hibrido funcionando!")
print("=" * 60)
