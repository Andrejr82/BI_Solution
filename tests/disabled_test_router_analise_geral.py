"""
Teste rápido do router _query_analise_geral
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.business_intelligence.direct_query_engine import DirectQueryEngine
from core.connectivity.parquet_adapter import ParquetAdapter

def test_router():
    """Testa o router inteligente com perguntas que caem em analise_geral"""

    # Inicializar engine
    adapter = ParquetAdapter('data/parquet/admmat.parquet')
    engine = DirectQueryEngine(adapter)

    # Perguntas de teste que devem ser roteadas pelo analise_geral
    # USANDO SEGMENTOS REAIS DO DATASET
    test_queries = [
        "Qual a análise ABC dos produtos?",
        "Mostre a sazonalidade de vendas",
        "Como está o crescimento do segmento TECIDOS?",
        "Qual a tendência de vendas?",
        "Quais produtos tiveram pico de vendas?",
        "Mostre a diversificação de produtos",
        "Qual a distribuição por categoria?",
        "Quais produtos têm estoque alto?",
        "Mostre produtos acima da média",
        "Qual o ranking de vendas?",
        "Compare os segmentos TECIDOS e PAPELARIA",
        "Mostre a evolução mês a mês",
        "Análise geral de vendas"  # Deve gerar análise geral padrão
    ]

    print("\n" + "="*80)
    print("TESTE DO ROUTER ANALISE_GERAL")
    print("="*80 + "\n")

    resultados = []

    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Testando: '{query}'")
        print("-" * 80)

        result = engine.process_query(query)

        query_type = result.get('query_type', 'N/A')
        result_type = result.get('type', 'N/A')
        title = result.get('title', 'N/A')
        tokens_used = result.get('tokens_used', -1)

        is_fallback = result_type == 'fallback'
        is_error = result_type == 'error'

        status = "[OK] SUCESSO" if not is_fallback and not is_error else "[FALLBACK] LLM" if is_fallback else "[ERRO]"

        print(f"  Query Type: {query_type}")
        print(f"  Result Type: {result_type}")
        print(f"  Title: {title}")
        print(f"  Tokens LLM: {tokens_used}")
        print(f"  Status: {status}")

        resultados.append({
            "query": query,
            "query_type": query_type,
            "result_type": result_type,
            "status": status,
            "tokens_used": tokens_used
        })

    # Resumo
    print("\n\n" + "="*80)
    print("RESUMO DOS TESTES")
    print("="*80 + "\n")

    sucesso = sum(1 for r in resultados if "[OK]" in r['status'])
    fallback = sum(1 for r in resultados if "FALLBACK" in r['status'])
    erro = sum(1 for r in resultados if "ERRO" in r['status'])

    print(f"Total de perguntas: {len(test_queries)}")
    print(f"[OK] Sucesso (Direto): {sucesso} ({sucesso/len(test_queries)*100:.1f}%)")
    print(f"[FALLBACK] Fallback (LLM): {fallback} ({fallback/len(test_queries)*100:.1f}%)")
    print(f"[ERRO] Erros: {erro} ({erro/len(test_queries)*100:.1f}%)")

    total_tokens = sum(r['tokens_used'] for r in resultados if r['tokens_used'] > 0)
    print(f"\nTotal de tokens LLM usados: {total_tokens}")

    print("\n" + "="*80 + "\n")

    return resultados

if __name__ == "__main__":
    test_router()
