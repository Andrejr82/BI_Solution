"""
Teste rápido do agente otimizado
"""
import sys
import os
import time

# Adicionar backend ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

# Simular query simples
queries = [
    "qual é o preço do produto 369947?",
    "qual o estoque do produto 59294?",
    "me mostre informações completas do produto 369947",
]

print("TESTE DE PERFORMANCE DO AGENTE OTIMIZADO\n")
print("=" * 60)

try:
    from app.core.query_processor import QueryProcessor

    print("OK - QueryProcessor importado com sucesso\n")

    # Inicializar
    print("Inicializando QueryProcessor...")
    start = time.time()
    processor = QueryProcessor()
    init_time = time.time() - start
    print(f"OK - Inicializado em {init_time:.2f}s\n")

    # Testar cada query
    for i, query in enumerate(queries, 1):
        print(f"\nTESTE {i}/{len(queries)}: {query}")
        print("-" * 60)

        start = time.time()
        try:
            result = processor.process_query(query)
            elapsed = time.time() - start

            output = result.get("output", result.get("response", "Sem resposta"))

            print(f"Tempo: {elapsed:.2f}s")
            print(f"Resposta: {output[:200]}...")

            if elapsed < 3.0:
                print("EXCELENTE (< 3s)")
            elif elapsed < 5.0:
                print("BOM (< 5s)")
            elif elapsed < 10.0:
                print("LENTO (< 10s)")
            else:
                print("MUITO LENTO (> 10s)")

        except Exception as e:
            elapsed = time.time() - start
            print(f"ERRO apos {elapsed:.2f}s: {e}")

    print("\n" + "=" * 60)
    print("OK - TESTE CONCLUIDO")

except Exception as e:
    print(f"ERRO FATAL: {e}")
    import traceback
    traceback.print_exc()
