"""
Teste completo do sistema RAG (FASE 2)
Valida QueryRetriever, ExampleCollector e integração com CodeGenAgent
"""
import sys
from pathlib import Path

# Adicionar core ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.rag.query_retriever import QueryRetriever
from core.rag.example_collector import ExampleCollector


def test_query_retriever():
    """Testa QueryRetriever com queries reais"""
    print("\n" + "=" * 60)
    print("TESTE 1: QueryRetriever - Busca Semantica")
    print("=" * 60)

    retriever = QueryRetriever()

    # Queries de teste
    test_queries = [
        "Mostre o ranking dos produtos mais vendidos",
        "Quais são os top 10 produtos de papelaria?",
        "Me mostre o estoque por segmento",
        "Gráfico de vendas por mês",
        "Comparar vendas da UNE MAD com UNE SCR"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}] Query: '{query}'")

        # Buscar similares
        similar = retriever.find_similar_queries(query, top_k=3)

        if similar:
            print(f"    Encontradas {len(similar)} queries similares:")
            for j, example in enumerate(similar[:2], 1):  # Mostrar apenas top 2
                score = example.get('similarity_score', 0)
                query_similar = example.get('query_user', '')
                print(f"      [{j}] Similaridade: {score:.2%}")
                print(f"          Query: '{query_similar[:60]}...'")
        else:
            print("    [!] Nenhuma query similar encontrada")

    # Estatísticas
    stats = retriever.get_stats()
    print(f"\nEstatisticas do Retriever:")
    print(f"  Total de exemplos: {stats['total_examples']}")
    print(f"  Tamanho do indice: {stats['index_size']}")

    return True


def test_example_collector():
    """Testa ExampleCollector"""
    print("\n" + "=" * 60)
    print("TESTE 2: ExampleCollector - Coleta de Exemplos")
    print("=" * 60)

    collector = ExampleCollector()

    # Simular coleta de query bem-sucedida
    print("\nColetando query de teste...")
    example = collector.collect_successful_query(
        user_query="Ranking de produtos do segmento TECIDOS",
        code_generated="df = load_data(filters={'NOMESEGMENTO': 'TECIDOS'})\nresult = df.nlargest(10, 'VENDA_30DD')[['NOME', 'VENDA_30DD']]",
        result_rows=10,
        intent="ranking",
        tags=["ranking", "vendas", "tecidos"]
    )

    print(f"  OK - Exemplo coletado:")
    print(f"    Query normalizada: '{example['query_normalized']}'")
    print(f"    Tags: {example['tags']}")
    print(f"    Intent: {example['intent']}")

    # Estatísticas
    stats = collector.get_collection_stats()
    print(f"\nEstatisticas do Collector:")
    print(f"  Total de exemplos: {stats['total_examples']}")
    print(f"  Distribuicao de tags: {stats.get('tag_distribution', {})}")

    return True


def test_rag_integration():
    """Testa integração RAG end-to-end"""
    print("\n" + "=" * 60)
    print("TESTE 3: Integracao RAG End-to-End")
    print("=" * 60)

    # 1. Buscar query similar
    print("\nCenario: Usuario faz query sobre ranking")
    user_query = "Top 5 produtos mais vendidos de festas"

    retriever = QueryRetriever()
    similar = retriever.find_similar_queries(user_query, top_k=3)

    if similar:
        best_match = similar[0]
        print(f"\nMelhor match RAG:")
        print(f"  Similaridade: {best_match['similarity_score']:.2%}")
        print(f"  Query original: '{best_match['query_user']}'")
        print(f"  Codigo gerado:")
        code_lines = best_match['code_generated'].split('\n')[:3]
        for line in code_lines:
            print(f"    {line}")
    else:
        print("\n[!] Nenhum match encontrado")

    # 2. Simular execução bem-sucedida e coleta
    print("\nSimulando execucao bem-sucedida...")
    collector = ExampleCollector()

    new_example = collector.collect_successful_query(
        user_query=user_query,
        code_generated="df = load_data(filters={'NOMESEGMENTO': 'FESTAS'})\nresult = df.nlargest(5, 'VENDA_30DD')[['NOME', 'VENDA_30DD']]",
        result_rows=5,
        intent="ranking"
    )

    print(f"  OK - Nova query coletada e adicionada ao banco")
    print(f"    Tags auto-detectadas: {new_example['tags']}")

    return True


def test_rag_accuracy():
    """Testa acurácia do RAG com queries conhecidas"""
    print("\n" + "=" * 60)
    print("TESTE 4: Acuracia do RAG")
    print("=" * 60)

    retriever = QueryRetriever()

    # Pares query -> query esperada similar
    test_pairs = [
        ("Ranking de vendas", "ranking"),
        ("Mostre um gráfico", "grafico"),
        ("Estoque por loja", "estoque"),
        ("Top 10 produtos", "ranking")
    ]

    hits = 0
    total = len(test_pairs)

    for query, expected_tag in test_pairs:
        similar = retriever.find_similar_queries(query, top_k=1)

        if similar:
            best_match = similar[0]
            tags = best_match.get('tags', [])

            if expected_tag in str(tags).lower():
                hits += 1
                print(f"  OK - '{query}' -> encontrou tag '{expected_tag}'")
            else:
                print(f"  [X] '{query}' -> NAO encontrou '{expected_tag}' (tags: {tags})")
        else:
            print(f"  [X] '{query}' -> nenhum match")

    accuracy = (hits / total) * 100
    print(f"\nAcuracia: {accuracy:.1f}% ({hits}/{total})")

    return accuracy >= 50  # Mínimo 50% de acurácia


def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("TESTE COMPLETO DO SISTEMA RAG - FASE 2")
    print("=" * 60)

    tests = [
        ("QueryRetriever", test_query_retriever),
        ("ExampleCollector", test_example_collector),
        ("Integracao RAG", test_rag_integration),
        ("Acuracia RAG", test_rag_accuracy)
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[X] ERRO no teste {name}: {e}")
            results.append((name, False))

    # Resumo final
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)

    for name, result in results:
        status = "OK" if result else "FALHOU"
        print(f"  {name}: {status}")

    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} testes passaram")

    if passed == total:
        print("\nSUCESSO - Todos os testes passaram!")
    else:
        print("\nALGUNS TESTES FALHARAM - Revisar implementacao")

    print("=" * 60)


if __name__ == '__main__':
    main()
