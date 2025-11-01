"""
Teste das correções críticas implementadas.
Valida as queries problemáticas identificadas nos logs.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.business_intelligence.direct_query_engine import DirectQueryEngine
from core.connectivity.parquet_adapter import ParquetAdapter

def test_queries_problematicas():
    """
    Testa as queries que estavam falhando antes das correções.
    """
    print("=" * 80)
    print("INICIANDO TESTES DAS CORREÇÕES CRÍTICAS")
    print("=" * 80)

    # Inicializar o adapter e engine
    parquet_path = 'data/parquet/admmat.parquet'
    if not os.path.exists(parquet_path):
        print(f"\n❌ ERRO: Arquivo parquet não encontrado: {parquet_path}")
        return False

    adapter = ParquetAdapter(file_path=parquet_path)
    engine = DirectQueryEngine(parquet_adapter=adapter)

    # Lista de queries problemáticas identificadas nos logs
    queries_teste = [
        {
            "query": "quais categorias no segmento tecidos estão com produtos estoque 0?",
            "problema_anterior": "KeyError 'nome_categoria'",
            "esperado": "Deve retornar categorias com estoque zero no segmento TECIDOS"
        },
        {
            "query": "top 10 tecidos une cfr",
            "problema_anterior": "Retornava 'Top 10 UNEs' ao invés de produtos",
            "esperado": "Deve retornar top 10 produtos de TECIDOS na UNE CFR"
        },
        {
            "query": "quais sao os 10 tecidos mais vendidos na Une CFR?",
            "problema_anterior": "Classificação incorreta",
            "esperado": "Deve retornar top 10 produtos de TECIDOS na UNE CFR"
        },
        {
            "query": "Distribuição de vendas por categoria dentro do segmento PAPELARIA",
            "problema_anterior": "KeyError 'nome_categoria'",
            "esperado": "Deve retornar distribuição por categoria no segmento PAPELARIA"
        },
        {
            "query": "top 10 malhas une mad",
            "problema_anterior": "Método não implementado",
            "esperado": "Deve retornar top 10 produtos de MALHAS na UNE MAD"
        }
    ]

    resultados = []

    for i, teste in enumerate(queries_teste, 1):
        print(f"\n{'='*80}")
        print(f"TESTE {i}/{ len(queries_teste)}")
        print(f"{'='*80}")
        print(f"Query: {teste['query']}")
        print(f"Problema anterior: {teste['problema_anterior']}")
        print(f"Esperado: {teste['esperado']}")
        print(f"\n{'Executando...':<30}", end='', flush=True)

        try:
            result = engine.process_query(teste['query'])

            # Verificar se houve erro
            if result.get('type') == 'error':
                print(f"[X] ERRO")
                print(f"\nErro retornado: {result.get('error')}")
                resultados.append({
                    'query': teste['query'],
                    'status': 'ERRO',
                    'detalhes': result.get('error')
                })
            elif result.get('type') == 'fallback':
                print(f"[!] FALLBACK (precisou usar LLM)")
                print(f"\nRazao: {result.get('summary')}")
                resultados.append({
                    'query': teste['query'],
                    'status': 'FALLBACK',
                    'detalhes': result.get('summary')
                })
            else:
                print(f"[OK] SUCESSO (ZERO tokens LLM)")
                print(f"\nTitulo: {result.get('title')}")
                print(f"Summary: {result.get('summary')}")
                print(f"Tipo: {result.get('type')}")

                # Verificar detalhes
                if result.get('result'):
                    res = result['result']
                    if 'produtos' in res:
                        print(f"Produtos retornados: {len(res['produtos'])}")
                        if res['produtos']:
                            print(f"Primeiro produto: {res['produtos'][0].get('nome', 'N/A')}")
                    if 'categorias' in res:
                        print(f"Categorias retornadas: {len(res['categorias'])}")

                resultados.append({
                    'query': teste['query'],
                    'status': 'SUCESSO',
                    'detalhes': result.get('summary')
                })

        except Exception as e:
            print(f"[!] EXCEPTION")
            print(f"\nException: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            resultados.append({
                'query': teste['query'],
                'status': 'EXCEPTION',
                'detalhes': str(e)
            })

    # Resumo final
    print(f"\n{'='*80}")
    print("RESUMO DOS TESTES")
    print(f"{'='*80}")

    sucessos = sum(1 for r in resultados if r['status'] == 'SUCESSO')
    fallbacks = sum(1 for r in resultados if r['status'] == 'FALLBACK')
    erros = sum(1 for r in resultados if r['status'] == 'ERRO')
    exceptions = sum(1 for r in resultados if r['status'] == 'EXCEPTION')

    print(f"\n[OK] Sucessos (ZERO LLM): {sucessos}/{len(queries_teste)}")
    print(f"[!] Fallbacks (usou LLM): {fallbacks}/{len(queries_teste)}")
    print(f"[X] Erros: {erros}/{len(queries_teste)}")
    print(f"[!] Exceptions: {exceptions}/{len(queries_teste)}")

    taxa_sucesso = (sucessos / len(queries_teste)) * 100
    print(f"\nTaxa de sucesso: {taxa_sucesso:.1f}%")

    if taxa_sucesso >= 80:
        print("\n[OK] TESTES PASSARAM! Correcoes funcionando corretamente.")
        return True
    else:
        print("\n[!] TESTES FALHARAM. Revisar correcoes necessarias.")
        return False


if __name__ == "__main__":
    sucesso = test_queries_problematicas()
    sys.exit(0 if sucesso else 1)
