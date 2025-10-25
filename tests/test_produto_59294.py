"""
Teste rápido: Query específica de produto
"""
import time
from core.connectivity.parquet_adapter import ParquetAdapter

print("=" * 60)
print("TESTE: Query produto 59294")
print("=" * 60)

adapter = ParquetAdapter("data/parquet/admmat.parquet")
print(f"Engine: {adapter._hybrid.engine}")

# Query por código de produto
filters = {"codigo": "59294"}

print(f"\nExecutando query: {filters}")
start = time.time()
result = adapter.execute_query(filters)
elapsed = time.time() - start

print(f"\nResultados: {len(result)} linhas")
print(f"Tempo: {elapsed:.3f}s")

if len(result) > 0:
    produto = result[0]
    print(f"\nProduto encontrado:")
    print(f"  Código: {produto.get('codigo', 'N/A')}")
    print(f"  Nome: {produto.get('nome_produto', 'N/A')}")
    print(f"  Preço: R$ {produto.get('preco_38_percent', 'N/A')}")
    print(f"  Segmento: {produto.get('nomesegmento', 'N/A')}")
    print(f"  Estoque: {produto.get('estoque_atual', 'N/A')}")
else:
    print("\nProduto não encontrado!")

print("=" * 60)
