"""
Teste direto da query: Quais são os 5 produtos mais vendidos na UNE SCR no último mês?
"""
import time
from datetime import datetime

print("=" * 60)
print("TESTE: Query Produtos Mais Vendidos")
print("=" * 60)

# Inicializar componentes
print("\n1. Inicializando componentes...")
start_init = time.time()

from core.factory.component_factory import ComponentFactory
from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.agents.code_gen_agent import CodeGenAgent
from core.graph.graph_builder import GraphBuilder
from langchain_core.messages import HumanMessage

# LLM
llm_adapter = ComponentFactory.get_llm_adapter("gemini")
print(f"   [OK] LLM: {llm_adapter.model_name}")

# Data
data_adapter = HybridDataAdapter()
print(f"   [OK] Data: {data_adapter.get_status()['current_source']}")

# CodeGen
code_gen = CodeGenAgent(llm_adapter=llm_adapter, data_adapter=data_adapter)
print(f"   [OK] CodeGen")

# Graph
graph_builder = GraphBuilder(
    llm_adapter=llm_adapter,
    parquet_adapter=data_adapter,
    code_gen_agent=code_gen
)
agent_graph = graph_builder.build()
print(f"   [OK] GraphBuilder")

elapsed_init = time.time() - start_init
print(f"\n   Tempo de inicializacao: {elapsed_init:.2f}s")

# Query do usuário
query = "Quais sao os 5 produtos mais vendidos na UNE SCR no ultimo mes?"
print(f"\n2. Executando query:")
print(f"   '{query}'")

# Executar
start_query = time.time()
graph_input = {"messages": [HumanMessage(content=query)], "query": query}

try:
    print("\n3. Processando com agent_graph...")
    print("   (aguarde - pode demorar 30-45s)")

    # Progress feedback
    import threading

    def print_progress():
        elapsed = 0
        while elapsed < 60 and thread.is_alive():
            time.sleep(5)
            elapsed += 5
            print(f"   ... {elapsed}s decorridos")

    result = None
    def run_graph():
        global result
        result = agent_graph.invoke(graph_input)

    thread = threading.Thread(target=run_graph)
    thread.start()

    progress_thread = threading.Thread(target=print_progress, daemon=True)
    progress_thread.start()

    thread.join(timeout=60)  # 60s de timeout

    elapsed_query = time.time() - start_query

    if thread.is_alive():
        print(f"\n   [TIMEOUT] Query excedeu 60s")
        print("=" * 60)
        exit(1)

    print(f"\n   [OK] Query completada em {elapsed_query:.2f}s")

    # Analisar resposta
    final_response = result.get("final_response", {})
    response_type = final_response.get("type", "unknown")

    print("\n4. Resultado:")
    print(f"   Tipo: {response_type}")

    if response_type == "data":
        data_content = final_response.get("data", [])
        print(f"   Linhas retornadas: {len(data_content)}")
        if len(data_content) > 0:
            print(f"\n   Primeiras 5 linhas:")
            for i, row in enumerate(data_content[:5], 1):
                print(f"      {i}. {row}")
    elif response_type == "text":
        print(f"   Conteudo: {final_response.get('content', '')[:200]}...")
    elif response_type == "error":
        print(f"   [ERRO] {final_response.get('content', 'Erro desconhecido')}")

    # Estatísticas
    print("\n5. Estatisticas:")
    print(f"   Tempo total: {elapsed_query:.2f}s")
    print(f"   Tempo inicializacao: {elapsed_init:.2f}s")
    print(f"   Tempo query: {elapsed_query - elapsed_init:.2f}s")

    if elapsed_query > 30:
        print(f"\n   [ALERTA] Query demorou mais de 30s!")
        print(f"   Timeout do Streamlit seria ativado neste caso.")
    else:
        print(f"\n   [OK] Query dentro do timeout de 30s")

    print("\n" + "=" * 60)
    print("STATUS: TESTE CONCLUIDO")
    print("=" * 60)

except Exception as e:
    print(f"\n   [ERRO] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 60)
    print("STATUS: TESTE FALHOU")
    print("=" * 60)
