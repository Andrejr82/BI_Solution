"""
Teste de UMA query específica com Dask.
"""

import sys
import os
import io
from pathlib import Path

# Fix encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.config.safe_settings import get_safe_settings
from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.llm_adapter import GeminiLLMAdapter
from core.agents.code_gen_agent import CodeGenAgent
from core.graph.graph_builder import GraphBuilder

def test_query(query_text):
    print("=" * 80)
    print(f"Query: {query_text}")
    print("=" * 80)

    # Inicializar
    settings = get_safe_settings()
    llm_adapter = GeminiLLMAdapter(
        api_key=settings.GEMINI_API_KEY,
        model_name=settings.GEMINI_MODEL_NAME
    )
    data_adapter = HybridDataAdapter()
    code_gen_agent = CodeGenAgent(
        llm_adapter=llm_adapter,
        data_adapter=data_adapter
    )
    graph_builder = GraphBuilder(
        llm_adapter=llm_adapter,
        parquet_adapter=data_adapter,
        code_gen_agent=code_gen_agent
    )
    grafo = graph_builder.build()

    # Executar
    import time
    start_time = time.time()

    result_state = grafo.invoke({
        "messages": [{"role": "user", "content": query_text}]
    })

    elapsed = time.time() - start_time

    # Analisar
    resultado = result_state.get("final_response", {})
    tipo = resultado.get("type", "unknown")
    sucesso = resultado.get("success", False)

    print(f"\nResultado:")
    print(f"  Sucesso: {sucesso}")
    print(f"  Tipo: {tipo}")
    print(f"  Tempo: {elapsed:.2f}s")

    if tipo == "data":
        data = resultado.get("data", [])
        print(f"  Registros: {len(data)}")
        if len(data) > 0:
            print(f"  Amostra: {data[0]}")

    return sucesso, tipo, elapsed

if __name__ == "__main__":
    # Query de GRÁFICO para testar geração Plotly
    query = "Gere um gráfico de barras mostrando o ranking dos 10 produtos mais vendidos no segmento TECIDOS"

    try:
        success, tipo, tempo = test_query(query)
        print(f"\n{'='*80}")
        print(f"TESTE {'PASSOU' if success else 'FALHOU'} em {tempo:.2f}s")
        print(f"Tipo esperado: chart")
        print(f"Tipo obtido: {tipo}")
        if tipo == "chart":
            print("SUCCESS! Grafico foi gerado!")
        print(f"{'='*80}")
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
