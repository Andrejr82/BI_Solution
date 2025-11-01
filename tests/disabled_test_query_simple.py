"""
Teste simples e rápido do DirectQueryEngine
"""
import sys
import time
from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.business_intelligence.direct_query_engine import DirectQueryEngine

print("=" * 60)
print("TESTE SIMPLES - DirectQueryEngine")
print("=" * 60)

# 1. Inicializar adapter
print("\n[1/3] Inicializando HybridDataAdapter...")
start = time.time()
adapter = HybridDataAdapter()
print(f"[OK] Adapter inicializado em {time.time() - start:.2f}s")

# 2. Inicializar engine
print("\n[2/3] Inicializando DirectQueryEngine...")
start = time.time()
engine = DirectQueryEngine(adapter)
print(f"[OK] Engine inicializado em {time.time() - start:.2f}s")

# 3. Testar query simples
print("\n[3/3] Testando query: 'produto mais vendido'")
start = time.time()
try:
    result = engine.process_query("produto mais vendido")
    elapsed = time.time() - start

    print(f"[OK] Query processada em {elapsed:.2f}s")
    print(f"\nRESULTADO:")
    print(f"  - Tipo: {result.get('type')}")
    print(f"  - Titulo: {result.get('title', 'N/A')}")
    print(f"  - Method: {result.get('method', 'N/A')}")
    print(f"  - Query Type: {result.get('query_type', 'N/A')}")

    if result.get('type') == 'error':
        print(f"  - [ERRO]: {result.get('error')}")
    elif result.get('type') == 'fallback':
        print(f"  - [FALLBACK]: Query nao reconhecida")
    else:
        print(f"  - [SUCCESS]: Query executada com sucesso")

except Exception as e:
    print(f"[ERRO] ao processar query: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TESTE CONCLUÍDO")
print("=" * 60)
