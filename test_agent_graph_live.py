"""
Teste rapido do agent_graph - diagnostico ao vivo
"""
import logging
import sys
# Forcar UTF-8 no Windows
sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

print("=" * 60)
print("TESTE AGENT_GRAPH - DIAGNOSTICO COMPLETO")
print("=" * 60)

# 1. Carregar componentes
print("\n1. Carregando ComponentFactory...")
try:
    from core.factory.component_factory import ComponentFactory
    print("   [OK] ComponentFactory")
except Exception as e:
    print(f"   [ERRO] {e}")
    exit(1)

# 2. Inicializar LLM
print("\n2. Inicializando LLM...")
try:
    llm_adapter = ComponentFactory.get_llm_adapter("gemini")
    print("   [OK] LLM")
except Exception as e:
    print(f"   [ERRO] {e}")
    exit(1)

# 3. Inicializar HybridAdapter
print("\n3. Inicializando HybridAdapter...")
try:
    from core.connectivity.hybrid_adapter import HybridDataAdapter
    data_adapter = HybridDataAdapter()
    status = data_adapter.get_status()
    print(f"   [OK] HybridAdapter - Fonte: {status['current_source']}")
except Exception as e:
    print(f"   [ERRO] {e}")
    exit(1)

# 4. Inicializar CodeGenAgent
print("\n4. Inicializando CodeGenAgent...")
try:
    from core.agents.code_gen_agent import CodeGenAgent
    code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter)
    print("   [OK] CodeGenAgent")
    print(f"   Colunas carregadas: {len(code_gen_agent.column_descriptions)}")
except Exception as e:
    print(f"   [ERRO] {e}")
    exit(1)

# 5. Construir Grafo
print("\n5. Construindo agent_graph...")
try:
    from core.graph.graph_builder import GraphBuilder
    graph_builder = GraphBuilder(
        llm_adapter=llm_adapter,
        parquet_adapter=data_adapter,
        code_gen_agent=code_gen_agent
    )
    agent_graph = graph_builder.build()
    print("   [OK] agent_graph construido!")
except Exception as e:
    print(f"   [ERRO] {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# 6. Testar query
print("\n6. Testando query: 'qual e o ranking de vendas no segmento tecidos ?'")
print("   Aguarde...")

try:
    graph_input = {"messages": [{"role": "user", "content": "qual e o ranking de vendas no segmento tecidos ?"}]}
    final_state = agent_graph.invoke(graph_input)

    print("\n   [OK] agent_graph.invoke() executado!")
    print(f"\n   KEYS DO FINAL_STATE: {list(final_state.keys())}")

    final_response = final_state.get("final_response", {})
    print(f"\n   FINAL_RESPONSE TYPE: {type(final_response)}")
    print(f"   FINAL_RESPONSE KEYS: {list(final_response.keys()) if isinstance(final_response, dict) else 'N/A'}")

    if final_response:
        response_type = final_response.get("type", "unknown")
        print(f"\n   TIPO DE RESPOSTA: {response_type}")

        if response_type == "text":
            content = final_response.get("content", "")
            print(f"   CONTEUDO (primeiros 200 chars):\n   {content[:200]}")
        elif response_type == "data":
            data = final_response.get("content", [])
            print(f"   DADOS: {len(data)} registros")
            if data:
                print(f"   COLUNAS: {list(data[0].keys()) if isinstance(data[0], dict) else 'N/A'}")
        elif response_type == "chart":
            print(f"   GRAFICO gerado!")
        else:
            print(f"   Tipo desconhecido: {final_response}")
    else:
        print("\n   [ERRO] FINAL_RESPONSE VAZIO!")
        print(f"   FULL STATE:\n{final_state}")

    print("\n" + "=" * 60)
    print("TESTE CONCLUIDO!")
    print("=" * 60)

except Exception as e:
    print(f"\n   [ERRO] ao invocar agent_graph: {e}")
    import traceback
    traceback.print_exc()
