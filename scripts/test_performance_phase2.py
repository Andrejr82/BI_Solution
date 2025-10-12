"""
Teste de performance para validar otimizações da Fase 2 (Predicate Pushdown).
"""

import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.connectivity.parquet_adapter import ParquetAdapter
from core.business_intelligence.direct_query_engine import DirectQueryEngine

def test_performance():
    """Testa performance com Predicate Pushdown."""

    print("="*70)
    print("TESTE DE PERFORMANCE - FASE 2 (PREDICATE PUSHDOWN)")
    print("="*70)

    parquet_path = "data/parquet/admmat.parquet"
    if not os.path.exists(parquet_path):
        print(f"[ERRO] Arquivo nao encontrado: {parquet_path}")
        return

    adapter = ParquetAdapter(parquet_path)
    engine = DirectQueryEngine(adapter)

    # Testes que devem usar Predicate Pushdown
    tests = [
        {
            "name": "Top Produtos UNE Especifica (TIJ)",
            "query_type": "top_produtos_une_especifica",
            "params": {"limite": 10, "une_nome": "TIJ"},
            "expected_filter": True  # Deve filtrar por UNE
        },
        {
            "name": "Top Produtos por Segmento (TECIDOS)",
            "query_type": "top_produtos_por_segmento",
            "params": {"segmento": "TECIDOS", "limit": 10},
            "expected_filter": True  # Deve filtrar por segmento
        },
        {
            "name": "Vendas UNE Mes Especifico (TIJ - Janeiro)",
            "query_type": "vendas_une_mes_especifico",
            "params": {"une_nome": "TIJ", "mes_nome": "janeiro"},
            "expected_filter": True  # Deve filtrar por UNE
        },
        {
            "name": "Produto Mais Vendido (Geral - SEM filtro)",
            "query_type": "produto_mais_vendido",
            "params": {},
            "expected_filter": False  # NAO deve filtrar
        }
    ]

    print("\n[INFO] Executando testes...\n")

    results = []
    for test in tests:
        print(f"[TEST] {test['name']}")
        print(f"       Params: {test['params']}")

        start_time = time.time()

        try:
            result = engine.execute_direct_query(test['query_type'], test['params'])
            duration = time.time() - start_time

            if result and result.get('type') != 'error':
                print(f"  [OK] Executado em {duration:.2f}s")
                print(f"       Titulo: {result.get('title', 'N/A')}")
                print(f"       Tokens: {result.get('tokens_used', 0)}")

                results.append({
                    'test': test['name'],
                    'status': 'SUCCESS',
                    'duration': duration,
                    'expected_filter': test['expected_filter']
                })
            else:
                print(f"  [FALHOU] Erro: {result.get('error', 'Unknown')}")
                results.append({
                    'test': test['name'],
                    'status': 'FAILED',
                    'duration': duration,
                    'expected_filter': test['expected_filter']
                })

        except Exception as e:
            duration = time.time() - start_time
            print(f"  [ERRO] Excecao: {str(e)}")
            results.append({
                'test': test['name'],
                'status': 'ERROR',
                'duration': duration,
                'expected_filter': test['expected_filter']
            })

        print()

    # Resumo
    print("="*70)
    print("RESUMO DOS TESTES")
    print("="*70)

    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    total_count = len(results)

    print(f"\nTestes executados: {total_count}")
    print(f"Sucessos: {success_count}")
    print(f"Falhas: {total_count - success_count}")

    print("\nPerformance:")
    for r in results:
        status_icon = "OK" if r['status'] == 'SUCCESS' else "!!"
        filter_info = "(com filtro)" if r['expected_filter'] else "(sem filtro)"
        print(f"  [{status_icon}] {r['test']:50s} {filter_info:15s} - {r['duration']:.2f}s")

    print("\n[INFO] Teste concluido!")

    # Análise de performance
    filtered_tests = [r for r in results if r['expected_filter'] and r['status'] == 'SUCCESS']
    unfiltered_tests = [r for r in results if not r['expected_filter'] and r['status'] == 'SUCCESS']

    if filtered_tests and unfiltered_tests:
        avg_filtered = sum(r['duration'] for r in filtered_tests) / len(filtered_tests)
        avg_unfiltered = sum(r['duration'] for r in unfiltered_tests) / len(unfiltered_tests)

        print("\n" + "="*70)
        print("ANALISE DE PERFORMANCE")
        print("="*70)
        print(f"\nTempo medio com Predicate Pushdown: {avg_filtered:.2f}s")
        print(f"Tempo medio sem filtro (dataset completo): {avg_unfiltered:.2f}s")

        if avg_filtered < avg_unfiltered:
            improvement = ((avg_unfiltered - avg_filtered) / avg_unfiltered) * 100
            print(f"\n[OK] OTIMIZACAO EFETIVA! Reducao de {improvement:.1f}% no tempo de execucao")
        else:
            print(f"\n[AVISO] Queries com filtro deveriam ser mais rapidas")

if __name__ == "__main__":
    test_performance()
