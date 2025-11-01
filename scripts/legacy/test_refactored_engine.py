"""
Script de teste para validar a refatoração do DirectQueryEngine.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.connectivity.parquet_adapter import ParquetAdapter
from core.business_intelligence.direct_query_engine import DirectQueryEngine

def test_basic_queries():
    """Testa consultas básicas após refatoração."""

    print("[TEST] Inicializando ParquetAdapter...")
    parquet_path = "data/parquet/admmat.parquet"

    if not os.path.exists(parquet_path):
        print(f"[ERRO] Arquivo não encontrado: {parquet_path}")
        return False

    adapter = ParquetAdapter(parquet_path)
    print("[OK] ParquetAdapter inicializado")

    print("\n[TEST] Inicializando DirectQueryEngine...")
    engine = DirectQueryEngine(adapter)
    print("[OK] DirectQueryEngine inicializado")

    # Testes de consultas
    tests = [
        {
            "name": "Produto Mais Vendido",
            "query_type": "produto_mais_vendido",
            "params": {}
        },
        {
            "name": "Ranking Vendas UNEs",
            "query_type": "ranking_vendas_unes",
            "params": {}
        },
        {
            "name": "Top Produtos por Segmento",
            "query_type": "top_produtos_por_segmento",
            "params": {"segmento": "TECIDOS", "limit": 5}
        }
    ]

    print("\n" + "="*60)
    print("EXECUTANDO TESTES")
    print("="*60)

    passed = 0
    failed = 0

    for test in tests:
        print(f"\n[TEST] {test['name']}...")
        try:
            result = engine.execute_direct_query(test['query_type'], test['params'])

            if result and result.get('type') != 'error':
                print(f"  [OK] {test['name']}")
                print(f"       Titulo: {result.get('title', 'N/A')}")
                print(f"       Tokens: {result.get('tokens_used', 0)}")
                passed += 1
            else:
                print(f"  [FALHOU] {test['name']}")
                print(f"       Erro: {result.get('error', 'Unknown')}")
                failed += 1
        except Exception as e:
            print(f"  [ERRO] {test['name']}")
            print(f"       Excecao: {str(e)}")
            failed += 1

    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    print(f"Passou: {passed}/{len(tests)}")
    print(f"Falhou: {failed}/{len(tests)}")
    print(f"Taxa de Sucesso: {(passed/len(tests)*100):.1f}%")

    return failed == 0

if __name__ == "__main__":
    success = test_basic_queries()
    sys.exit(0 if success else 1)
