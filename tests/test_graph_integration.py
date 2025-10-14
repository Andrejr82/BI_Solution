"""
Teste de Integração do GraphBuilder - Valida fluxo completo UNE
Este teste valida especificamente o GraphBuilder usado pelo Streamlit
"""
import sys
import os
import time

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Executa testes de integração do GraphBuilder com ferramentas UNE"""
    print("\n" + "="*70)
    print("TESTE DE INTEGRACAO GRAPHBUILDER - FLUXO COMPLETO UNE")
    print("="*70)

    # 1. Inicializar componentes
    print("\n[STEP 1] Inicializando GraphBuilder (usado pelo Streamlit)...")
    try:
        from core.factory.component_factory import ComponentFactory
        from core.agents.code_gen_agent import CodeGenAgent
        from core.connectivity.parquet_adapter import ParquetAdapter
        from core.graph.graph_builder import GraphBuilder
        from langchain_core.messages import HumanMessage

        # Obter LLM adapter
        llm_adapter = ComponentFactory.get_llm_adapter()
        print(f"   [OK] LLM Adapter: {llm_adapter.__class__.__name__}")

        # Criar ParquetAdapter
        parquet_adapter = ParquetAdapter('data/parquet/admmat_extended.parquet')
        print(f"   [OK] ParquetAdapter criado")

        # Criar CodeGenAgent
        code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter, data_adapter=parquet_adapter)
        print(f"   [OK] CodeGenAgent criado")

        # Criar GraphBuilder e compilar grafo
        graph_builder = GraphBuilder(
            llm_adapter=llm_adapter,
            parquet_adapter=parquet_adapter,
            code_gen_agent=code_gen_agent
        )
        app = graph_builder.build()
        print(f"   [OK] GraphBuilder compilado com sucesso")

    except Exception as e:
        print(f"   [FAIL] Erro na inicialização: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 2. Definir queries de teste UNE
    test_queries = [
        {
            "query": "Quais produtos do segmento TECIDOS precisam de abastecimento na UNE 2586?",
            "test_name": "Abastecimento UNE - Segmento TECIDOS",
            "expected_intent": "une_operation"
        },
        {
            "query": "Qual a MC do produto 704559 na UNE 2586?",
            "test_name": "Calculo MC - Produto Especifico",
            "expected_intent": "une_operation"
        },
        {
            "query": "Calcule o preco de R$ 800 ranking 0 pagando a vista",
            "test_name": "Politica de Precos - Atacado",
            "expected_intent": "une_operation"
        }
    ]

    # 3. Executar testes
    print("\n[STEP 2] Executando queries UNE através do GraphBuilder...")
    print("="*70)

    results = []
    total_start = time.time()

    for idx, test_case in enumerate(test_queries, 1):
        query = test_case["query"]
        test_name = test_case["test_name"]

        print(f"\n[TEST {idx}/3] {test_name}")
        print(f"Query: {query}")
        print("-" * 70)

        start_time = time.time()

        try:
            # Invocar grafo (fluxo completo usado pelo Streamlit)
            result = app.invoke({
                "messages": [HumanMessage(content=query)],
                "query": query
            })

            elapsed = time.time() - start_time

            # Validar resultado
            intent = result.get("intent", "")
            final_response = result.get("final_response", "")

            print(f"   Intent detectado: {intent}")
            print(f"   Tempo: {elapsed:.2f}s")

            # Verificar se houve erro
            final_response_str = str(final_response) if final_response else ''
            if not final_response or 'erro' in final_response_str.lower():
                print(f"   [FAIL] Resposta vazia ou com erro")
                print(f"   Resposta: {str(final_response)[:200] if final_response else 'VAZIA'}")
                results.append({
                    'test_name': test_name,
                    'success': False,
                    'time': elapsed,
                    'error': 'Resposta vazia ou com erro',
                    'intent': intent
                })
            else:
                print(f"   [OK] Query executada com sucesso")
                response_preview = str(final_response)[:200] if final_response else ''
                print(f"   Resposta (preview): {response_preview}...")

                results.append({
                    'test_name': test_name,
                    'success': True,
                    'time': elapsed,
                    'response_length': len(str(final_response)),
                    'intent': intent
                })

        except Exception as e:
            elapsed = time.time() - start_time
            print(f"   [EXCEPTION] {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'test_name': test_name,
                'success': False,
                'time': elapsed,
                'error': str(e)
            })

    total_time = time.time() - total_start

    # 4. Sumário dos resultados
    print("\n" + "="*70)
    print("SUMARIO DOS TESTES")
    print("="*70)

    passed = sum(1 for r in results if r['success'])
    total = len(results)

    for result in results:
        status = "[PASS]" if result['success'] else "[FAIL]"
        time_str = f"{result['time']:.2f}s"
        intent_str = f"(intent: {result.get('intent', 'N/A')})"
        print(f"{status} {result['test_name']} {time_str} {intent_str}")
        if not result['success'] and 'error' in result:
            print(f"       Erro: {result['error']}")

    print(f"\nResultado: {passed}/{total} testes passaram")
    print(f"Tempo total: {total_time:.2f}s")

    # 5. Conclusão
    print("\n" + "="*70)
    if passed == total:
        print("RESULTADO FINAL: TODOS OS TESTES PASSARAM!")
        print("Status: GRAPHBUILDER COM UNE INTEGRADO CORRETAMENTE")
        return True
    else:
        print(f"RESULTADO FINAL: {total - passed} teste(s) falharam")
        print("Status: VERIFICAR ERROS ACIMA")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
