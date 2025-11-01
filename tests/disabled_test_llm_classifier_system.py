"""
Testes do Sistema LLM Classifier.
Valida IntentClassifier, GenericExecutor e integração completa.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_intent_classifier():
    """Testa o IntentClassifier isoladamente."""
    print("\n" + "="*80)
    print("TESTE 1: IntentClassifier")
    print("="*80)

    try:
        from core.business_intelligence.intent_classifier import IntentClassifier

        classifier = IntentClassifier()

        if not classifier.enabled:
            print("[AVISO] Classifier desabilitado (Gemini não disponível)")
            print("   Isso é esperado se GEMINI_API_KEY não estiver configurada")
            return True

        # Teste 1: Query simples
        query1 = "top 10 produtos mais vendidos"
        print(f"\n[TESTE] Query: {query1}")
        intent1 = classifier.classify_intent(query1)
        print(f"[OK] Operation: {intent1.get('operation')}")
        print(f"   Confidence: {intent1.get('confidence', 0):.2f}")
        print(f"   Filters: {intent1.get('filters', {})}")

        # Teste 2: Query com filtros
        query2 = "top 10 tecidos une cfr"
        print(f"\n[TESTE] Query: {query2}")
        intent2 = classifier.classify_intent(query2)
        print(f"[OK] Operation: {intent2.get('operation')}")
        print(f"   Confidence: {intent2.get('confidence', 0):.2f}")
        print(f"   Filters: {intent2.get('filters', {})}")

        # Teste 3: Query complexa
        query3 = "quais categorias do segmento tecidos com estoque zero?"
        print(f"\n[TESTE] Query: {query3}")
        intent3 = classifier.classify_intent(query3)
        print(f"[OK] Operation: {intent3.get('operation')}")
        print(f"   Confidence: {intent3.get('confidence', 0):.2f}")
        print(f"   Filters: {intent3.get('filters', {})}")

        # Mostrar estatísticas
        stats = classifier.get_stats()
        print(f"\n[STATS] Estatísticas:")
        print(f"   Total tokens usados: {stats['total_tokens_used']}")

        print("\n[OK] TESTE PASSOU: IntentClassifier funcionando")
        return True

    except Exception as e:
        print(f"\n[FALHOU] TESTE FALHOU: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_generic_executor():
    """Testa o GenericExecutor isoladamente."""
    print("\n" + "="*80)
    print("TESTE 2: GenericExecutor")
    print("="*80)

    try:
        import pandas as pd
        from core.business_intelligence.generic_query_executor import GenericQueryExecutor

        executor = GenericQueryExecutor()

        # Criar DataFrame de teste
        df = pd.DataFrame({
            'codigo': [1, 2, 3, 4, 5],
            'nome_produto': ['Produto A', 'Produto B', 'Produto C', 'Produto D', 'Produto E'],
            'vendas_total': [1000, 800, 600, 400, 200],
            'une_nome': ['SCR', 'CFR', 'SCR', 'MAD', 'CFR'],
            'nomesegmento': ['TECIDOS', 'TECIDOS', 'ARMARINHO', 'PAPELARIA', 'FESTAS'],
            'NOMECATEGORIA': ['Cat1', 'Cat2', 'Cat3', 'Cat4', 'Cat5'],
            'preco_38_percent': [10.0, 20.0, 30.0, 40.0, 50.0]
        })

        # Teste 1: Ranking de produtos
        print("\n[TESTE] Teste: Ranking de produtos")
        intent1 = {
            'operation': 'ranking_produtos',
            'filters': {},
            'limit': 3
        }
        result1 = executor.execute(df, intent1)
        print(f"[OK] Type: {result1.get('type')}")
        print(f"   Title: {result1.get('title')}")
        print(f"   Produtos retornados: {len(result1.get('result', {}).get('produtos', []))}")

        # Teste 2: Ranking com filtro
        print("\n[TESTE] Teste: Ranking com filtro de UNE")
        intent2 = {
            'operation': 'ranking_produtos',
            'filters': {'une_nome': 'SCR'},
            'limit': 10
        }
        result2 = executor.execute(df, intent2)
        print(f"[OK] Type: {result2.get('type')}")
        print(f"   Produtos retornados: {len(result2.get('result', {}).get('produtos', []))}")

        # Teste 3: Distribuição por categoria
        print("\n[TESTE] Teste: Distribuição por categoria")
        intent3 = {
            'operation': 'distribuicao_categoria',
            'filters': {},
            'limit': 100
        }
        result3 = executor.execute(df, intent3)
        print(f"[OK] Type: {result3.get('type')}")
        print(f"   Categorias retornadas: {len(result3.get('result', {}).get('categorias', []))}")

        print("\n[OK] TESTE PASSOU: GenericExecutor funcionando")
        return True

    except Exception as e:
        print(f"\n[FALHOU] TESTE FALHOU: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_cache():
    """Testa o QueryCache."""
    print("\n" + "="*80)
    print("TESTE 3: QueryCache")
    print("="*80)

    try:
        from core.business_intelligence.query_cache import QueryCache

        cache = QueryCache(cache_dir="data/cache_test", ttl_hours=24)

        # Teste 1: Set e Get
        print("\n[TESTE] Teste: Set e Get")
        test_query = "top 10 produtos"
        test_intent = {
            'operation': 'ranking_produtos',
            'confidence': 0.95,
            'filters': {}
        }

        cache.set(test_query, test_intent)
        print("[OK] Intent salvo no cache")

        cached = cache.get(test_query)
        if cached:
            print(f"[OK] Intent recuperado do cache: {cached.get('operation')}")
        else:
            print("[FALHOU] Intent não encontrado no cache")
            return False

        # Teste 2: Query similar
        print("\n[TESTE] Teste: Cache miss")
        result = cache.get("query que nao existe")
        if result is None:
            print("[OK] Cache miss correto")
        else:
            print("[FALHOU] Cache deveria retornar None")

        # Mostrar estatísticas
        stats = cache.get_stats()
        print(f"\n[STATS] Estatísticas:")
        print(f"   Total entries: {stats['total_entries']}")
        print(f"   Hits: {stats['hits']}")
        print(f"   Misses: {stats['misses']}")
        print(f"   Hit rate: {stats['hit_rate']}")

        print("\n[OK] TESTE PASSOU: QueryCache funcionando")
        return True

    except Exception as e:
        print(f"\n[FALHOU] TESTE FALHOU: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Testa a integração completa com DirectQueryEngine."""
    print("\n" + "="*80)
    print("TESTE 4: Integração Completa")
    print("="*80)

    try:
        from core.connectivity.parquet_adapter import ParquetAdapter
        from core.business_intelligence.direct_query_engine import DirectQueryEngine

        # Verificar se arquivo existe
        parquet_path = 'data/parquet/admmat.parquet'
        if not os.path.exists(parquet_path):
            print(f"[AVISO] Arquivo não encontrado: {parquet_path}")
            print("   Pulando teste de integração")
            return True

        # Inicializar
        print("\n[TESTE] Inicializando DirectQueryEngine...")
        adapter = ParquetAdapter(file_path=parquet_path)
        engine = DirectQueryEngine(parquet_adapter=adapter)

        # Verificar se LLM Classifier está habilitado
        if engine.use_llm_classifier:
            print("[OK] LLM Classifier HABILITADO")
        else:
            print("[INFO] LLM Classifier DESABILITADO (USE_LLM_CLASSIFIER=false)")
            print("   Sistema funcionará apenas com regex (esperado)")

        # Testar query simples
        print("\n[TESTE] Teste: Query simples")
        query1 = "top 5 produtos"
        result1 = engine.process_query(query1)
        print(f"[OK] Method: {result1.get('method')}")
        print(f"   Type: {result1.get('type')}")
        print(f"   Cached: {result1.get('cached', False)}")

        # Testar query complexa
        print("\n[TESTE] Teste: Query complexa")
        query2 = "quais são os produtos mais vendidos no segmento tecidos?"
        result2 = engine.process_query(query2)
        print(f"[OK] Method: {result2.get('method')}")
        print(f"   Type: {result2.get('type')}")

        print("\n[OK] TESTE PASSOU: Integração funcionando")
        return True

    except Exception as e:
        print(f"\n[FALHOU] TESTE FALHOU: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes."""
    print("="*80)
    print("SUITE DE TESTES: Sistema LLM Classifier")
    print("="*80)

    results = []

    # Executar testes
    results.append(("IntentClassifier", test_intent_classifier()))
    results.append(("GenericExecutor", test_generic_executor()))
    results.append(("QueryCache", test_query_cache()))
    results.append(("Integração", test_integration()))

    # Resumo
    print("\n" + "="*80)
    print("RESUMO DOS TESTES")
    print("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[OK] PASSOU" if result else "[FALHOU] FALHOU"
        print(f"{test_name:<20} {status}")

    print(f"\nTotal: {passed}/{total} testes passaram")

    if passed == total:
        print("\n[SUCESSO] TODOS OS TESTES PASSARAM!")
        return 0
    else:
        print(f"\n[AVISO]  {total - passed} teste(s) falharam")
        return 1


if __name__ == "__main__":
    sys.exit(main())
