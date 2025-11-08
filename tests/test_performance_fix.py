"""
Teste de performance da otimizacao Parquet
"""

import time
import sys

print("=" * 80)
print("TESTE DE PERFORMANCE - QUERY MC PRODUTO")
print("=" * 80)

# Configurar logging
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(name)s - %(message)s')

print("\n1. Importando modulo une_tools...")
from core.tools.une_tools import calcular_mc_produto

print("2. Executando query: MC do produto 369947 na UNE 1685 (261)")

start = time.time()
# Usar .invoke() pois é um LangChain tool
result = calcular_mc_produto.invoke({"produto_id": 369947, "une_id": 1685})
elapsed = time.time() - start

print("\n" + "=" * 80)
print("RESULTADO DA QUERY:")
print("=" * 80)

if "error" in result:
    print(f"ERRO: {result['error']}")
    sys.exit(1)
else:
    print(f"Produto: {result.get('nome', 'N/A')}")
    print(f"MC Calculada: {result.get('mc_calculada', 0.0)}")
    print(f"Estoque Atual: {result.get('estoque_atual', 0.0)}")
    print(f"Linha Verde: {result.get('linha_verde', 0.0)}")
    print(f"Recomendacao: {result.get('recomendacao', 'N/A')}")

print("\n" + "=" * 80)
print(f"TEMPO DE EXECUCAO: {elapsed:.2f}s")
print("=" * 80)

# Avaliar performance
if elapsed < 1.0:
    print("RESULTADO: OTIMO! (< 1s)")
elif elapsed < 5.0:
    print("RESULTADO: BOM (< 5s)")
elif elapsed < 10.0:
    print("RESULTADO: ACEITAVEL (< 10s)")
else:
    print(f"RESULTADO: LENTO ({elapsed:.1f}s - PRECISA OTIMIZACAO)")
