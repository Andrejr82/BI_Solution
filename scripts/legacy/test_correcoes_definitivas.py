"""
Script de teste para validar todas as correções de performance e bugs.
Testa as 12 queries críticas identificadas nos logs.
"""
import sys
import os
from pathlib import Path
from datetime import datetime
import time

# Configurar encoding para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.business_intelligence.direct_query_engine import DirectQueryEngine
from core.connectivity.hybrid_adapter import HybridDataAdapter

def test_query(engine, query_type, params, query_name):
    """Testa uma query e retorna resultado + tempo."""
    print(f"\n{'='*60}")
    print(f"TESTE: {query_name}")
    print(f"Query Type: {query_type}")
    print(f"Params: {params}")
    print(f"{'='*60}")

    start = time.time()
    try:
        result = engine.execute_direct_query(query_type, params)
        duration = time.time() - start

        if result.get('error'):
            print(f"❌ ERRO: {result['error']}")
            return {'success': False, 'duration': duration, 'error': result['error']}
        else:
            print(f"✅ SUCESSO em {duration:.2f}s")
            print(f"   Título: {result.get('title', 'N/A')}")
            print(f"   Tipo: {result.get('type', 'N/A')}")
            if 'result' in result:
                print(f"   Resultado: {str(result['result'])[:200]}...")
            return {'success': True, 'duration': duration, 'result': result}

    except Exception as e:
        duration = time.time() - start
        print(f"❌ EXCEÇÃO: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'duration': duration, 'error': str(e)}

def main():
    """Testa todas as queries críticas dos logs."""
    print(f"\n{'#'*80}")
    print(f"TESTE DE CORREÇÕES DEFINITIVAS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*80}\n")

    # Inicializar engine
    print("Inicializando DirectQueryEngine...")
    adapter = HybridDataAdapter()
    engine = DirectQueryEngine(adapter)
    print("✅ Engine inicializado\n")

    # Lista de queries críticas do log
    test_cases = [
        # Query 1: Produto mais vendido (tinha MemoryError)
        {
            'name': 'Produto mais vendido',
            'type': 'produto_mais_vendido',
            'params': {
                'matched_keywords': 'produto mais vendido',
                'user_query': 'Produto mais vendido'
            }
        },

        # Query 2: Top 5 produtos UNE SCR (tinha MemoryError)
        {
            'name': 'Top 5 produtos UNE SCR',
            'type': 'top_produtos_une_especifica',
            'params': {
                'limite': '5',
                'une_nome': 'scr',
                'user_query': 'Quais são os 5 produtos mais vendidos na UNE SCR no último mês?'
            }
        },

        # Query 3: Top 10 produtos UNE 261
        {
            'name': 'Top 10 produtos UNE 261',
            'type': 'top_produtos_une_especifica',
            'params': {
                'limite': '10',
                'une_nome': '261',
                'user_query': 'top 10 produtos da une 261'
            }
        },

        # Query 4: Ranking vendas UNEs
        {
            'name': 'Ranking vendas todas UNEs',
            'type': 'ranking_vendas_unes',
            'params': {
                'user_query': 'Vendas totais de cada UNE'
            }
        },

        # Query 5: Segmento campeão (tinha NameError)
        {
            'name': 'Segmento campeão',
            'type': 'segmento_campao',
            'params': {
                'matched_keywords': 'segmento mais vendeu',
                'user_query': 'Qual segmento mais vendeu?'
            }
        },

        # Query 6: Top 5 produtos filial SCR
        {
            'name': 'Top 5 produtos filial SCR',
            'type': 'top_produtos_une_especifica',
            'params': {
                'limite': '5',
                'une_nome': 'scr',
                'user_query': 'top 5 produtos da filial SCR'
            }
        },

        # Query 7: Top 5 produtos loja MAD
        {
            'name': 'Top 5 produtos loja MAD',
            'type': 'top_produtos_une_especifica',
            'params': {
                'limite': '5',
                'une_nome': 'mad',
                'user_query': '5 produtos mais vendidos na loja MAD'
            }
        },

        # Query 8: Top 10 produtos UNE SCR (variação)
        {
            'name': 'Top 10 produtos UNE SCR',
            'type': 'top_produtos_une_especifica',
            'params': {
                'limite': '10',
                'une_nome': 'scr',
                'user_query': 'me mostre os 10 produtos mais vendidos na une SCR'
            }
        },

        # Query 9: Ranking geral (tinha AttributeError)
        {
            'name': 'Ranking geral segmentos',
            'type': 'ranking_geral',
            'params': {
                'user_query': 'gere o ranking de vendas do segmento tecidos'
            }
        },

        # Query 10: Filial que mais vendeu
        {
            'name': 'Filial que mais vendeu',
            'type': 'filial_mais_vendeu',
            'params': {
                'matched_keywords': 'filial mais vendeu',
                'user_query': 'Qual filial mais vendeu?'
            }
        }
    ]

    # Executar testes
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n[{i}/{len(test_cases)}] ", end='')
        result = test_query(
            engine,
            test_case['type'],
            test_case['params'],
            test_case['name']
        )
        results.append({
            'name': test_case['name'],
            'success': result['success'],
            'duration': result['duration']
        })

        # Pausa entre queries para evitar sobrecarga
        time.sleep(0.5)

    # Sumário final
    print(f"\n\n{'='*80}")
    print(f"SUMÁRIO FINAL")
    print(f"{'='*80}\n")

    total = len(results)
    success_count = sum(1 for r in results if r['success'])
    failed_count = total - success_count
    avg_duration = sum(r['duration'] for r in results) / total

    print(f"Total de testes: {total}")
    print(f"✅ Sucessos: {success_count} ({success_count/total*100:.1f}%)")
    print(f"❌ Falhas: {failed_count} ({failed_count/total*100:.1f}%)")
    print(f"⏱️  Tempo médio: {avg_duration:.2f}s")
    print(f"⏱️  Tempo total: {sum(r['duration'] for r in results):.2f}s\n")

    # Detalhamento
    print("Detalhamento por query:")
    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"{status} {r['name']}: {r['duration']:.2f}s")

    print(f"\n{'='*80}\n")

    if failed_count == 0:
        print("🎉 TODAS AS QUERIES PASSARAM! Sistema 100% operacional!")
        return 0
    else:
        print(f"⚠️  {failed_count} query(s) falharam. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
