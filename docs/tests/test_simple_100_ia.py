"""
Teste Simples - Validação 100% IA
"""
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_query(app, query_text, test_name):
    """Testa uma query e retorna resultado"""
    from core.agent_state import AgentState

    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"Query: {query_text}")
    print(f"{'='*60}")

    try:
        state = AgentState(messages=[{'role': 'user', 'content': query_text}])
        result = app.invoke(state)
        final = result.get('final_response', {})

        response_type = final.get('type')
        print(f"[OK] Response Type: {response_type}")

        if response_type == 'data':
            rows = len(final.get('content', []))
            print(f"[OK] Data Rows: {rows}")
            if rows > 0:
                print(f"[SUCCESS] Query retornou {rows} linhas")
                return True
            else:
                print(f"[FAIL] Query retornou 0 linhas")
                return False

        elif response_type == 'text':
            content = str(final.get('content', ''))[:200]
            print(f"[OK] Text Response: {content}")
            if 'erro' in content.lower() or 'nao consegui' in content.lower():
                print(f"[FAIL] Resposta de erro")
                return False
            return True

        else:
            print(f"[FAIL] Tipo de resposta inesperado: {response_type}")
            return False

    except Exception as e:
        print(f"[EXCEPTION] {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa bateria completa de testes"""
    print("\n" + "="*60)
    print("TESTE SIMPLES - 100% IA")
    print("="*60)

    # Initialize components
    print("\n1. Inicializando componentes...")
    try:
        from core.factory.component_factory import ComponentFactory
        from core.connectivity.parquet_adapter import ParquetAdapter
        from core.agents.code_gen_agent import CodeGenAgent
        from core.graph.graph_builder import GraphBuilder

        llm = ComponentFactory.get_llm_adapter('gemini')
        print("   [OK] LLM Adapter inicializado")

        adapter = ParquetAdapter('data/parquet/admmat.parquet')
        print(f"   [OK] ParquetAdapter inicializado: {adapter.file_path}")

        codegen = CodeGenAgent(llm_adapter=llm, data_adapter=adapter)
        print("   [OK] CodeGenAgent inicializado")

        builder = GraphBuilder(llm, adapter, codegen)
        app = builder.build()
        print("   [OK] Agent Graph compilado")

    except Exception as e:
        print(f"   [FAIL] FALHA NA INICIALIZACAO: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Run test queries
    print("\n2. Executando queries de teste...")

    tests = [
        ("qual e o preco do produto 369947", "Query simples - produto especifico"),
        ("ranking de vendas do tecido", "Ranking com analise Python - tecidos"),
        ("ranking de vendas da papelaria", "Ranking com analise Python - papelaria"),
    ]

    results = []
    for query, test_name in tests:
        success = test_query(app, query, test_name)
        results.append((test_name, success))

    # Summary
    print("\n" + "="*60)
    print("SUMARIO DOS TESTES")
    print("="*60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status}: {test_name}")

    print(f"\nResultado: {passed}/{total} testes passaram")

    if passed == total:
        print("\n[SUCCESS] TODOS OS TESTES PASSARAM!")
        return True
    else:
        print(f"\n[WARNING] {total - passed} teste(s) falharam")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
