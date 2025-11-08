"""
Teste de validação da correção de imports Optional
"""
import sys
import os

sys.path.insert(0, os.getcwd())

def test_imports():
    """Testa se todos os imports estão funcionando"""
    print("="*60)
    print("TESTE DE VALIDACAO - CORRECAO DE IMPORTS")
    print("="*60)

    try:
        # 1. Testar data_tools (onde estava o erro principal)
        print("\n1. Testando core.tools.data_tools...")
        from core.tools.data_tools import fetch_data_from_query
        print("   OK: fetch_data_from_query importado")

        # 2. Testar ParquetAdapter
        print("\n2. Testando ParquetAdapter...")
        from core.connectivity.parquet_adapter import ParquetAdapter
        print("   OK: ParquetAdapter importado")

        # 3. Testar GraphBuilder
        print("\n3. Testando GraphBuilder...")
        from core.graph.graph_builder import GraphBuilder
        print("   OK: GraphBuilder importado")

        # 4. Testar HybridAdapter
        print("\n4. Testando HybridAdapter...")
        from core.connectivity.hybrid_adapter import HybridDataAdapter
        print("   OK: HybridDataAdapter importado")

        # 5. Testar bi_agent_nodes
        print("\n5. Testando bi_agent_nodes...")
        from core.agents import bi_agent_nodes
        print("   OK: bi_agent_nodes importado")

        # 6. Instanciar ParquetAdapter com arquivo real
        print("\n6. Testando instanciacao do ParquetAdapter...")
        parquet_path = os.path.join(os.getcwd(), "data", "parquet", "*.parquet")
        adapter = ParquetAdapter(parquet_path)
        print(f"   OK: ParquetAdapter instanciado com {parquet_path}")

        # 7. Obter schema
        print("\n7. Testando get_schema()...")
        schema = adapter.get_schema()
        schema_lines = schema.split('\n')
        print(f"   OK: Schema obtido ({len(schema_lines)} linhas)")
        print(f"   Primeiras 3 linhas do schema:")
        for line in schema_lines[:3]:
            print(f"      {line}")

        print("\n" + "="*60)
        print("RESULTADO: TODOS OS TESTES PASSARAM!")
        print("="*60)
        print("\nO sistema esta pronto para processar queries de grafico.")
        return True

    except Exception as e:
        print(f"\nERRO: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*60)
        print("RESULTADO: TESTE FALHOU")
        print("="*60)
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
