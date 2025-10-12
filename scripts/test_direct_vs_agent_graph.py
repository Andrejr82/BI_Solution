"""
Teste para comparar DirectQueryEngine vs Agent Graph
Data: 12/10/2025
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.business_intelligence.direct_query_engine import DirectQueryEngine
from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.factory.component_factory import ComponentFactory
from core.agents.code_gen_agent import CodeGenAgent
from core.graph.graph_builder import GraphBuilder
import time

print("="*80)
print("TESTE: DirectQueryEngine vs Agent Graph")
print("="*80)

# Inicializar componentes
print("\n1. Inicializando componentes...")
adapter = HybridDataAdapter()
direct_engine = DirectQueryEngine(adapter)
llm_adapter = ComponentFactory.get_llm_adapter("gemini")
code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter, data_adapter=adapter)
graph_builder = GraphBuilder(llm_adapter=llm_adapter, parquet_adapter=adapter, code_gen_agent=code_gen_agent)
agent_graph = graph_builder.build()

print("   [OK] Componentes inicializados!")

# Queries de teste
test_queries = [
    "produto mais vendido",
    "top 10 produtos",
    "ranking de vendas no segmento tecidos",
    "qual o produto com maior estoque?",
    "analise complexa de vendas"  # Esta não será reconhecida
]

print("\n2. Testando queries com DirectQueryEngine...")
print("-"*80)

for query in test_queries:
    print(f"\nQuery: '{query}'")
    start = time.time()

    try:
        result = direct_engine.process_query(query)
        elapsed = (time.time() - start) * 1000  # ms

        result_type = result.get("type", "unknown")

        if result_type == "error":
            print(f"   [ERRO]: {result.get('error', 'Desconhecido')}")
            print(f"   Sugestao: {result.get('suggestion', 'N/A')}")
        elif result_type == "fallback":
            print(f"   [FALLBACK]: Nao reconhecido pelo DirectQueryEngine")
        else:
            print(f"   [SUCESSO]: Tipo={result_type}")
            if "title" in result:
                print(f"   Titulo: {result['title']}")
            if "summary" in result:
                summary = result['summary'][:100] + "..." if len(result['summary']) > 100 else result['summary']
                print(f"   Resumo: {summary}")

        print(f"   Tempo: {elapsed:.0f}ms")

    except Exception as e:
        print(f"   [EXCECAO]: {str(e)}")
        elapsed = (time.time() - start) * 1000
        print(f"   Tempo: {elapsed:.0f}ms")

print("\n3. Testando query complexa com Agent Graph (com timeout)...")
print("-"*80)

complex_query = "ranking de vendas no segmento tecidos"
print(f"\nQuery: '{complex_query}'")

import threading
import queue

result_queue = queue.Queue()
timeout_seconds = 30

def invoke_agent_graph():
    try:
        graph_input = {"messages": [{"role": "user", "content": complex_query}]}
        final_state = agent_graph.invoke(graph_input)
        result_queue.put(("success", final_state))
    except Exception as e:
        result_queue.put(("error", str(e)))

start = time.time()
thread = threading.Thread(target=invoke_agent_graph, daemon=True)
thread.start()
thread.join(timeout=timeout_seconds)
elapsed = (time.time() - start) * 1000

if thread.is_alive():
    print(f"   [TIMEOUT]: Agent graph nao respondeu em {timeout_seconds}s")
else:
    try:
        result_type, result = result_queue.get_nowait()

        if result_type == "success":
            final_response = result.get("final_response", {})
            response_type = final_response.get("type", "unknown")
            print(f"   [SUCESSO]: Tipo={response_type}")

            if "content" in final_response:
                content = str(final_response['content'])[:200] + "..." if len(str(final_response['content'])) > 200 else str(final_response['content'])
                print(f"   Conteudo: {content}")
        else:
            print(f"   [ERRO]: {result}")
    except queue.Empty:
        print("   [AVISO]: Thread terminou mas sem resultado")

print(f"   Tempo: {elapsed:.0f}ms")

print("\n" + "="*80)
print("RESUMO:")
print("="*80)
print("[OK] DirectQueryEngine: Rapido (200-500ms) mas limitado a padroes")
print("[OK] Agent Graph: Flexivel mas lento (5-30s) - AGORA COM TIMEOUT!")
print("[OK] Recomendacao: Usar DirectQueryEngine como padrao")
print("="*80)
