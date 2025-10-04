"""
Teste rápido dos 4 métodos implementados na Fase 4
Usando perguntas reais do teste de 80 perguntas
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.business_intelligence.direct_query_engine import DirectQueryEngine
from core.connectivity.parquet_adapter import ParquetAdapter

def test_fase4():
    """Testa os 4 métodos novos com perguntas reais"""

    adapter = ParquetAdapter('data/parquet/admmat.parquet')
    engine = DirectQueryEngine(adapter)

    # Perguntas REAIS que estavam em FALLBACK (IDs: 24, 54, 55, 57)
    test_queries = [
        "Comparativo de eficiência de vendas entre UNEs similares",  # ID 24
        "Novos fabricantes vs estabelecidos: performance comparativa",  # ID 54
        "Fabricantes exclusivos vs multimarca por UNE",  # ID 55
        "Performance por categoria dentro do segmento ARMARINHO E CONFECÇÃO"  # ID 57
    ]

    print("\n" + "="*80)
    print("TESTE FASE 4 - 4 NOVOS MÉTODOS (Dataset Completo)")
    print("="*80 + "\n")

    resultados = []

    for i, query in enumerate(test_queries, 1):
        print(f"[{i}/4] Testando: '{query}'")
        print("-" * 80)

        result = engine.process_query(query)

        query_type = result.get('query_type', 'N/A')
        result_type = result.get('type', 'N/A')
        title = result.get('title', 'N/A')
        tokens_used = result.get('tokens_used', -1)

        is_fallback = result_type == 'fallback'
        is_error = result_type == 'error'

        status = "[OK] SUCCESS" if not is_fallback and not is_error else "[FALLBACK]" if is_fallback else "[ERRO]"

        print(f"  Query Type: {query_type}")
        print(f"  Result Type: {result_type}")
        print(f"  Title: {title[:60]}")
        print(f"  Tokens LLM: {tokens_used}")
        print(f"  Status: {status}\n")

        resultados.append({
            "query": query,
            "query_type": query_type,
            "result_type": result_type,
            "status": status,
            "tokens_used": tokens_used
        })

    # Resumo
    print("="*80)
    print("RESUMO FASE 4")
    print("="*80 + "\n")

    sucesso = sum(1 for r in resultados if "[OK]" in r['status'])
    fallback = sum(1 for r in resultados if "FALLBACK" in r['status'])
    erro = sum(1 for r in resultados if "ERRO" in r['status'])

    print(f"Total de perguntas: {len(test_queries)}")
    print(f"[OK] Sucesso (Direto): {sucesso} ({sucesso/len(test_queries)*100:.1f}%)")
    print(f"[FALLBACK] Fallback: {fallback} ({fallback/len(test_queries)*100:.1f}%)")
    print(f"[ERRO] Erros: {erro} ({erro/len(test_queries)*100:.1f}%)")

    total_tokens = sum(r['tokens_used'] for r in resultados if r['tokens_used'] > 0)
    print(f"\nTotal de tokens LLM usados: {total_tokens}")
    print("\n" + "="*80 + "\n")

    return resultados

if __name__ == "__main__":
    test_fase4()
