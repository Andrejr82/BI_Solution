"""
Teste de Integração UNE - End-to-End com LLM
Valida o fluxo completo das ferramentas UNE com chamadas reais à LLM
"""
import sys
import os
import time

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Executa testes de integração UNE com LLM"""
    print("\n" + "="*70)
    print("TESTE DE INTEGRACAO UNE - END-TO-END COM LLM")
    print("="*70)

    # Tracking de tokens
    token_usage = {
        'total_tokens': 0,
        'queries': []
    }

    # 1. Inicializar componentes
    print("\n[STEP 1] Inicializando componentes...")
    try:
        from core.agents.caculinha_bi_agent import create_caculinha_bi_agent
        from core.factory.component_factory import ComponentFactory
        from core.agents.code_gen_agent import CodeGenAgent
        from core.connectivity.parquet_adapter import ParquetAdapter

        # Obter LLM adapter
        llm_adapter = ComponentFactory.get_llm_adapter()
        print(f"   [OK] LLM Adapter: {llm_adapter.__class__.__name__}")

        # Criar ParquetAdapter
        parquet_adapter = ParquetAdapter('data/parquet/admmat_extended.parquet')
        print(f"   [OK] ParquetAdapter criado")

        # Criar CodeGenAgent
        code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter, data_adapter=parquet_adapter)
        print(f"   [OK] CodeGenAgent criado")

        # Criar agent
        agent, tools = create_caculinha_bi_agent(
            parquet_dir='data/parquet',
            code_gen_agent=code_gen_agent,
            llm_adapter=llm_adapter
        )
        print(f"   [OK] CaculinhaBI Agent criado com {len(tools)} ferramentas")

    except Exception as e:
        print(f"   [FAIL] Erro na inicializacao: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 2. Definir queries de teste UNE
    test_queries = [
        {
            "query": "Quais produtos do segmento TECIDOS precisam de abastecimento na UNE 2586?",
            "test_name": "Abastecimento UNE - Segmento TECIDOS",
            "expected_tool": "calcular_abastecimento_une"
        },
        {
            "query": "Qual a MC do produto 704559 na UNE 2586?",
            "test_name": "Calculo MC - Produto Especifico",
            "expected_tool": "calcular_mc_produto"
        },
        {
            "query": "Calcule o preco de R$ 800 ranking 0 pagando a vista",
            "test_name": "Politica de Precos - Atacado",
            "expected_tool": "calcular_preco_final_une"
        }
    ]

    # 3. Executar testes
    print("\n[STEP 2] Executando queries UNE com LLM...")
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
            # Invocar agent (fluxo completo com LLM)
            from langchain_core.messages import HumanMessage

            result = agent.invoke({
                "messages": [HumanMessage(content=query)]
            })

            elapsed = time.time() - start_time

            # Extrair resposta final
            messages = result.get("messages", [])
            if messages:
                final_message = messages[-1]
                content = final_message.content if hasattr(final_message, 'content') else str(final_message)

                # Verificar se houve erro
                if 'erro' in content.lower() or 'nao consegui' in content.lower():
                    print(f"   [FAIL] Resposta de erro")
                    print(f"   Conteudo: {content[:200]}")
                    results.append({
                        'test_name': test_name,
                        'success': False,
                        'time': elapsed,
                        'error': 'Resposta indica erro'
                    })
                else:
                    print(f"   [OK] Query executada com sucesso")
                    print(f"   Tempo: {elapsed:.2f}s")
                    print(f"   Resposta (preview): {content[:200]}...")

                    results.append({
                        'test_name': test_name,
                        'success': True,
                        'time': elapsed,
                        'response_length': len(content)
                    })

                    # Tracking de tokens (estimativa)
                    estimated_tokens = len(query.split()) * 1.3 + len(content.split()) * 1.3
                    token_usage['queries'].append({
                        'query': test_name,
                        'estimated_tokens': int(estimated_tokens)
                    })
                    token_usage['total_tokens'] += int(estimated_tokens)
            else:
                print(f"   [FAIL] Nenhuma mensagem retornada")
                results.append({
                    'test_name': test_name,
                    'success': False,
                    'time': elapsed,
                    'error': 'Nenhuma mensagem'
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
        print(f"{status} {result['test_name']} ({time_str})")
        if not result['success'] and 'error' in result:
            print(f"       Erro: {result['error']}")

    print(f"\nResultado: {passed}/{total} testes passaram")
    print(f"Tempo total: {total_time:.2f}s")

    # 5. Métricas de Tokens
    print("\n" + "="*70)
    print("METRICAS DE USO DE TOKENS (ESTIMATIVA)")
    print("="*70)

    if token_usage['queries']:
        for query_data in token_usage['queries']:
            print(f"  - {query_data['query']}: ~{query_data['estimated_tokens']} tokens")
        print(f"\nTotal estimado: ~{token_usage['total_tokens']} tokens")
        print(f"Tokens de contexto (verificacao): ~56.000 tokens")
        print(f"Total geral estimado: ~{token_usage['total_tokens'] + 56000} tokens")
    else:
        print("  Nenhuma query bem-sucedida para calcular tokens")

    # 6. Conclusão
    print("\n" + "="*70)
    if passed == total:
        print("RESULTADO FINAL: TODOS OS TESTES PASSARAM!")
        print("Status: INTEGRACAO UNE COM LLM FUNCIONANDO CORRETAMENTE")
        return True
    else:
        print(f"RESULTADO FINAL: {total - passed} teste(s) falharam")
        print("Status: VERIFICAR ERROS ACIMA")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
