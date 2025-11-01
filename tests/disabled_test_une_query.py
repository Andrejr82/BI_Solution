"""
Teste para reproduzir bug de query UNE 261 retornando dados de MAD
"""
import sys
import pandas as pd
from core.connectivity.parquet_adapter import ParquetAdapter
from core.business_intelligence.direct_query_engine import DirectQueryEngine

def test_une_261_query():
    """Testa query: 'quais são os 10 produtos mais vendidos na UNE 261?'"""

    print("=" * 80)
    print("TESTE: Query UNE 261")
    print("=" * 80)

    # 1. Verificar dados brutos
    print("\n1. VERIFICANDO DADOS BRUTOS")
    df = pd.read_parquet('data/parquet/admmat.parquet')
    print(f"   Total de registros: {len(df):,}")
    print(f"   UNEs disponíveis: {sorted(df['une_nome'].unique())}")

    une_261 = df[df['une_nome'] == '261']
    print(f"\n   Registros da UNE 261: {len(une_261):,}")

    if len(une_261) > 0:
        vendas_cols = [f'mes_{i:02d}' for i in range(1, 13)]
        une_261_copy = une_261.copy()
        for col in vendas_cols:
            une_261_copy[col] = pd.to_numeric(une_261_copy[col], errors='coerce')
        une_261_copy['vendas_total'] = une_261_copy[vendas_cols].fillna(0).sum(axis=1)
        top10_esperado = une_261_copy.nlargest(10, 'vendas_total')[['codigo', 'nome_produto', 'vendas_total', 'une_nome']]

        print("\n   TOP 10 ESPERADO (dados brutos):")
        for idx, row in top10_esperado.iterrows():
            print(f"   - {row['codigo']:6d} | {row['nome_produto'][:50]:50s} | {row['vendas_total']:8.0f} | UNE: {row['une_nome']}")

    # 2. Testar DirectQueryEngine
    print("\n" + "=" * 80)
    print("2. TESTANDO DIRECTQUERYENGINE")
    print("=" * 80)

    adapter = ParquetAdapter('data/parquet/admmat.parquet')
    engine = DirectQueryEngine(adapter)

    query = "quais sao os 10 produtos mais vendidos na une 261?"
    print(f"\n   Query: '{query}'")

    result = engine.process_query(query)

    print(f"\n   Tipo de resultado: {result.get('type')}")
    print(f"   Title: {result.get('title', 'N/A')}")

    if result.get('type') == 'error':
        print(f"\n   ❌ ERRO: {result.get('error')}")
        print(f"   Sugestão: {result.get('suggestion', 'N/A')}")
        return False

    # Analisar resultado
    if 'result' in result:
        result_data = result['result']

        if 'chart_data' in result_data:
            chart_data = result_data['chart_data']
            x_data = chart_data.get('x', [])
            y_data = chart_data.get('y', [])

            print(f"\n   Total de produtos retornados: {len(x_data)}")

            if len(x_data) > 0:
                print("\n   TOP 10 RETORNADO:")
                for i in range(min(10, len(x_data))):
                    print(f"   - {x_data[i][:50]:50s} | {y_data[i]:8.0f}")

        # Verificar produtos_info se disponível
        if 'produtos_info' in result_data:
            produtos = result_data['produtos_info']
            print(f"\n   Produtos info: {len(produtos)} produtos")

            # Verificar UNEs dos produtos retornados
            unes_retornadas = set()
            for produto in produtos[:10]:
                if 'une_nome' in produto:
                    unes_retornadas.add(produto['une_nome'])

            print(f"\n   UNEs nos produtos retornados: {unes_retornadas}")

            if '261' not in unes_retornadas:
                print("\n   ❌❌❌ BUG CONFIRMADO: Produtos retornados NÃO são da UNE 261!")
                print(f"   UNEs incorretas retornadas: {unes_retornadas}")
                return False
            elif len(unes_retornadas) > 1:
                print("\n   ⚠️ AVISO: Múltiplas UNEs retornadas (esperado apenas 261)")
                return False
            else:
                print("\n   ✅ OK: Produtos são da UNE 261")
                return True

    print("\n   ⚠️ Estrutura de resultado inesperada")
    print(f"   Result keys: {result.keys()}")
    return False

def test_adapter_filtering():
    """Testa se ParquetAdapter filtra corretamente por UNE"""

    print("\n" + "=" * 80)
    print("3. TESTANDO PARQUETADAPTER FILTERING")
    print("=" * 80)

    adapter = ParquetAdapter('data/parquet/admmat.parquet')
    adapter.connect()

    # Testar filtro simples
    filters = {'une_nome': '261'}
    print(f"\n   Filtro aplicado: {filters}")

    result = adapter.execute_query(query_filters=filters)

    print(f"   Registros retornados: {len(result):,}")

    if len(result) > 0:
        # Verificar se todos são da UNE 261
        unes_unicas = set(result['une_nome'].unique())
        print(f"   UNEs nos resultados: {unes_unicas}")

        if unes_unicas == {'261'}:
            print("   ✅ OK: Filtro funcionando corretamente")
            return True
        else:
            print(f"   ❌ BUG: Filtro retornou UNEs erradas: {unes_unicas}")
            return False
    else:
        print("   ❌ BUG: Filtro não retornou nenhum resultado")
        return False

if __name__ == "__main__":
    print("\nINICIANDO TESTES DE DIAGNOSTICO\n")

    # Executar testes
    test1_ok = test_une_261_query()
    test2_ok = test_adapter_filtering()

    print("\n" + "=" * 80)
    print("RESULTADO DOS TESTES")
    print("=" * 80)
    print(f"DirectQueryEngine: {'PASSOU' if test1_ok else 'FALHOU'}")
    print(f"ParquetAdapter:    {'PASSOU' if test2_ok else 'FALHOU'}")
    print("=" * 80)

    sys.exit(0 if (test1_ok and test2_ok) else 1)
