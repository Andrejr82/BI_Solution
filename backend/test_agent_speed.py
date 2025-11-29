"""
Teste de performance do agente otimizado
Execute: python backend/test_agent_speed.py
"""
import time
import sys

queries = [
    "qual e o preco do produto 369947?",
    "qual o estoque do produto 59294?",
]

print("=" * 70)
print("TESTE DE PERFORMANCE - AGENTE OTIMIZADO")
print("=" * 70)

try:
    from app.core.query_processor import QueryProcessor

    print("\n[1/3] Inicializando QueryProcessor...")
    start = time.time()
    processor = QueryProcessor()
    init_time = time.time() - start
    print(f"OK - Inicializado em {init_time:.2f}s")

    total_time = 0
    successful = 0

    for i, query in enumerate(queries, 1):
        print(f"\n[{i+1}/{len(queries)+1}] Query: {query}")
        print("-" * 70)

        start = time.time()
        try:
            result = processor.process_query(query)
            elapsed = time.time() - start
            total_time += elapsed

            output = result.get("output", result.get("response", "Sem resposta"))

            print(f"Tempo: {elapsed:.2f}s")
            print(f"Resposta: {output[:150]}...")

            if elapsed < 3.0:
                print("Performance: EXCELENTE (< 3s)")
                successful += 1
            elif elapsed < 5.0:
                print("Performance: BOM (< 5s)")
                successful += 1
            elif elapsed < 7.0:
                print("Performance: OK (< 7s)")
            else:
                print("Performance: LENTO (> 7s)")

        except Exception as e:
            elapsed = time.time() - start
            print(f"ERRO apos {elapsed:.2f}s: {e}")

    print("\n" + "=" * 70)
    print(f"RESULTADO: {successful}/{len(queries)} queries rapidas")
    if successful == len(queries):
        print("STATUS: TODAS AS OTIMIZACOES FUNCIONANDO!")
    else:
        print("STATUS: PRECISA MAIS OTIMIZACAO")
    print("=" * 70)

except Exception as e:
    print(f"\nERRO FATAL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
